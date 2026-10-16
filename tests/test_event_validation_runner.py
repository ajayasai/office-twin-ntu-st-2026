"""Workload safety checks use fakes only: no ETW, process launch or desktop input."""
from contextlib import redirect_stderr
from datetime import datetime, timezone
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, call, patch

import psutil

from tools import run_event_validation as runner


class EventValidationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.capture = self.root / "capture"
        self.capture.mkdir()
        self.output = self.root / "native"
        self.ready = {"trace_started_utc": "2026-10-16T00:00:00+00:00", "max_seconds": 900}
        self.start = datetime(2026, 10, 16, tzinfo=timezone.utc).timestamp()

    def owned_files(self):
        paths = [self.capture / "harness-identity.json",
                 self.output / "01-fixed-307" / "controller-identity.json",
                 self.output / "01-fixed-307" / "observer" / "observer-ready.json"]
        for path in paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}", encoding="utf-8")
        # Nearby unrelated evidence and application identities are not workers.
        foreign = self.root / "foreign" / "controller-identity.json"
        foreign.parent.mkdir()
        foreign.write_text("{}", encoding="utf-8")
        app = self.output / "01-fixed-307" / "application-identity.json"
        app.write_text("{}", encoding="utf-8")
        return paths

    def test_each_capture_stop_condition_cancels_only_declared_workers(self):
        paths = self.owned_files()
        for trigger in ("collector_dead", "status", "stop_request", "deadline"):
            with self.subTest(trigger=trigger):
                for name in ("capture-status.json", "stop.request"):
                    (self.capture / name).unlink(missing_ok=True)
                if trigger == "status":
                    (self.capture / "capture-status.json").write_text("{}")
                if trigger == "stop_request":
                    (self.capture / "stop.request").touch()
                collector = Mock()
                collector.is_running.return_value = trigger != "collector_dead"
                process = Mock()
                process.poll.return_value = None
                stamp = self.start + (840 if trigger == "deadline" else 20)
                with patch.object(runner.subprocess, "Popen", return_value=process), \
                     patch.object(runner.time, "time", return_value=stamp), \
                     patch.object(runner.time, "sleep") as sleep, \
                     patch.object(runner, "stop_declared_python") as stop:
                    with self.assertRaises(RuntimeError):
                        runner.run_native_guarded(self.capture, self.output, 307, self.ready, collector)
                self.assertEqual(stop.call_args_list, [call(paths[0]), call(paths[1]),
                                                      call(paths[2], "observer_identity")])
                process.terminate.assert_called_once_with()
                process.wait.assert_called_once_with(timeout=5)
                process.kill.assert_not_called()
                sleep.assert_not_called()
                collector.terminate.assert_not_called()

    def test_cancelled_launcher_kill_fallback_is_bounded(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.side_effect = [runner.subprocess.TimeoutExpired("owned launcher", 5), 1]
        collector = Mock()
        collector.is_running.return_value = False
        with patch.object(runner.subprocess, "Popen", return_value=process), \
             patch.object(runner.time, "time", return_value=self.start + 20), \
             patch.object(runner, "stop_declared_python"):
            with self.assertRaises(RuntimeError):
                runner.run_native_guarded(self.capture, self.output, 307, self.ready, collector)
        process.terminate.assert_called_once_with()
        process.kill.assert_called_once_with()
        self.assertEqual(process.wait.call_args_list, [call(timeout=5), call(timeout=5)])

    def test_keyboard_interrupt_stops_owned_workers_and_propagates(self):
        paths = self.owned_files()
        process = Mock()
        process.poll.return_value = None
        collector = Mock()
        collector.is_running.return_value = True
        with patch.object(runner.subprocess, "Popen", return_value=process), \
             patch.object(runner.time, "time", return_value=self.start + 20), \
             patch.object(runner.time, "sleep", side_effect=KeyboardInterrupt), \
             patch.object(runner, "stop_declared_python") as stop:
            with self.assertRaises(KeyboardInterrupt):
                runner.run_native_guarded(self.capture, self.output, 307, self.ready, collector)
        self.assertEqual(stop.call_args_list, [call(paths[0]), call(paths[1]),
                                              call(paths[2], "observer_identity")])
        process.terminate.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=5)

    def test_completed_workload_does_not_terminate_any_process(self):
        self.owned_files()
        process = Mock(returncode=0)
        process.poll.side_effect = [None, 0, 0]
        collector = Mock()
        collector.is_running.return_value = True
        with patch.object(runner.subprocess, "Popen", return_value=process) as launch, \
             patch.object(runner.time, "time", return_value=self.start + 20), \
             patch.object(runner.time, "sleep"), \
             patch.object(runner, "stop_declared_python") as stop:
            result = runner.run_native_guarded(self.capture, self.output, 307, self.ready, collector)
        self.assertEqual(result, 0)
        stop.assert_not_called()
        process.terminate.assert_not_called()
        process.kill.assert_not_called()
        arguments = launch.call_args.args[0]
        self.assertEqual(arguments[0], runner.sys.executable)
        self.assertIn(str(runner.ROOT / "tools/run_benchmark.py"), arguments)
        self.assertEqual(arguments[-4:], ["--output", str(self.output), "--seeds", "307"])
        self.assertNotIn("--mode", arguments)  # Existing harness default is desktop.
        self.assertNotIn("--scale", arguments)  # Existing harness default is normal scale 1.
        self.assertNotIn("shell", launch.call_args.kwargs)

    def test_workload_failure_code_is_preserved_without_foreign_cleanup(self):
        process = Mock(returncode=9)
        process.poll.return_value = 9
        with patch.object(runner.subprocess, "Popen", return_value=process), \
             patch.object(runner, "stop_declared_python") as stop:
            result = runner.run_native_guarded(self.capture, self.output, 307, self.ready, Mock())
        self.assertEqual(result, 9)
        stop.assert_not_called()
        process.terminate.assert_not_called()

    def identity_file(self, pid=111, created=123.5, key=None):
        identity = {"pid": pid, "create_time": created}
        path = self.capture / "identity.json"
        path.write_text(json.dumps({key: identity} if key else identity), encoding="utf-8")
        return path

    def test_stop_refuses_reused_pid_non_python_and_self(self):
        cases = [(111, 124.5, "python.exe"), (111, 123.5, "chrome.exe"),
                 (runner.os.getpid(), 123.5, "python.exe")]
        for pid, created, name in cases:
            with self.subTest(pid=pid, created=created, name=name):
                path = self.identity_file(pid=pid)
                process = Mock(pid=pid)
                process.create_time.return_value = created
                process.name.return_value = name
                with patch("psutil.Process", return_value=process):
                    runner.stop_declared_python(path)
                process.terminate.assert_not_called()
                process.kill.assert_not_called()

    def test_stop_accepts_exact_nested_observer_identity(self):
        path = self.identity_file(key="observer_identity")
        process = Mock(pid=111)
        process.create_time.return_value = 123.5
        process.name.return_value = "python.exe"
        with patch("psutil.Process", return_value=process) as lookup:
            runner.stop_declared_python(path, "observer_identity")
        lookup.assert_called_once_with(111)
        process.terminate.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=5)
        process.kill.assert_not_called()

    def test_exact_identity_timeout_kills_only_that_python(self):
        path = self.identity_file()
        process = Mock(pid=111)
        process.create_time.return_value = 123.5
        process.name.return_value = "pythonw.exe"
        process.wait.side_effect = [psutil.TimeoutExpired(5, pid=111), 0]
        with patch("psutil.Process", return_value=process):
            runner.stop_declared_python(path)
        process.terminate.assert_called_once_with()
        process.kill.assert_called_once_with()
        self.assertEqual(process.wait.call_args_list, [call(timeout=5), call(timeout=5)])

    def test_missing_malformed_or_exited_identity_is_harmless(self):
        path = self.capture / "identity.json"
        with patch("psutil.Process") as lookup:
            runner.stop_declared_python(path)
            path.write_text("not json", encoding="utf-8")
            runner.stop_declared_python(path)
            path.write_text("{}", encoding="utf-8")
            runner.stop_declared_python(path)
        lookup.assert_not_called()
        path = self.identity_file()
        with patch("psutil.Process", side_effect=psutil.NoSuchProcess(111)):
            runner.stop_declared_python(path)

    def readiness(self):
        return {**self.ready, "status": "recording", "collector_pid": 999,
                "collector_created_utc": "2026-10-15T23:59:00+00:00",
                "ready_utc": "2026-10-16T00:00:01+00:00", "session_name": "test-session"}

    def test_invalid_readiness_and_elevation_stop_before_canaries_or_native_input(self):
        for fault in ("elevated", "missing_ready", "finalized", "stopping", "stale",
                      "future", "wrong_identity", "wrong_status"):
            with self.subTest(fault=fault):
                for name in ("capture-ready.json", "capture-status.json", "stop.request"):
                    (self.capture / name).unlink(missing_ok=True)
                ready = self.readiness()
                if fault == "wrong_status":
                    ready["status"] = "complete"
                if fault != "missing_ready":
                    (self.capture / "capture-ready.json").write_text(json.dumps(ready), encoding="utf-8")
                if fault == "finalized":
                    (self.capture / "capture-status.json").write_text("{}")
                if fault == "stopping":
                    (self.capture / "stop.request").touch()
                collector = Mock()
                collector.create_time.return_value = self.start - (59 if fault == "wrong_identity" else 60)
                age = {"stale": 122, "future": -2}.get(fault, 10)
                windll = Mock()
                windll.shell32.IsUserAnAdmin.return_value = fault == "elevated"
                with patch.object(runner, "os", SimpleNamespace(name="nt", getpid=lambda: 222)), \
                     patch("ctypes.windll", windll, create=True), \
                     patch("psutil.Process", return_value=collector), \
                     patch.object(runner.time, "time", return_value=self.start + 1 + age), \
                     patch.object(runner, "simple_canary") as canary, \
                     patch.object(runner, "nested_canary") as nested, \
                     patch.object(runner, "run_native_guarded") as native, \
                     redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as failure:
                        runner.main(["--capture-dir", str(self.capture), "--native-output", str(self.output)])
                self.assertEqual(failure.exception.code, 2)
                canary.assert_not_called()
                nested.assert_not_called()
                native.assert_not_called()
                self.assertFalse((self.capture / "canary-ground-truth.json").exists())


if __name__ == "__main__":
    unittest.main()
