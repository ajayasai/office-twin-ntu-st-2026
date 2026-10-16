"""Exact snapshot identity and workload opt-in checks, without desktop activity."""
from contextlib import ExitStack, redirect_stderr
from datetime import datetime, timezone
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

from tools import run_event_validation as runner


class FakeReader:
    def __init__(self, inventory, identities, inventory_time=140000000000000000):
        self.rows = inventory
        self.identities = {pid: list(values) for pid, values in identities.items()}
        self.inventory_time = inventory_time
        self.lookups = []

    def system_filetime(self):
        return self.inventory_time

    def inventory(self):
        return self.rows

    def created(self, pid):
        self.lookups.append(pid)
        values = self.identities[pid]
        result = values.pop(0) if len(values) > 1 else values[0]
        if isinstance(result, Exception):
            raise result
        return result


def process(pid, name, parent_pid=0, **extra):
    return {"pid": pid, "name": name, "parent_pid": parent_pid, **extra}


class RundownSnapshotTests(unittest.TestCase):
    def test_preserves_exact_filetime_and_retains_only_apps_and_live_ancestors(self):
        stamp = 134075000000000003  # Not exactly representable as a binary float.
        reader = FakeReader([
            process(30, "chrome.exe", 20, command_line="private", username="private"),
            process(20, "launcher.exe", 10), process(10, "root.exe"),
            process(40, "Notepad.exe"), process(50, "explorer.exe"),
            process(99, "unrelated.exe", command_line="never read")],
            {30: [stamp], 20: [stamp - 1], 10: [stamp - 2], 40: [stamp + 1], 50: [stamp + 2]})
        result = runner.collect_rundown_snapshot("before-native", reader)
        self.assertEqual([row["pid"] for row in result["processes"]], [10, 20, 30, 40, 50])
        self.assertEqual(result["processes"][2]["create_time_filetime"], str(stamp))
        self.assertNotIn(99, reader.lookups)
        self.assertEqual(result["read_error_count"], 0)
        self.assertEqual(result["race_discard_count"], 0)
        for row in result["processes"]:
            self.assertTrue(row["identity_rechecked"])
            self.assertEqual(set(row), {"pid", "create_time_filetime", "parent_pid", "name", "identity_rechecked"})
            self.assertEqual(reader.lookups.count(row["pid"]), 2)
        self.assertEqual(result["source"], "Toolhelp32Snapshot+GetProcessTimes")

    def test_exited_reused_and_younger_parent_ids_do_not_create_ancestor_rows(self):
        reader = FakeReader([
            process(10, "chrome.exe", 11), process(11, "reused.exe", 12), process(12, "unrelated.exe"),
            process(20, "notepad.exe", 21), process(21, "gone.exe"),
            process(30, "explorer.exe", 31)],
            {10: [100], 11: [101], 20: [200], 21: [OSError("gone")], 30: [300]})
        result = runner.collect_rundown_snapshot("after-native", reader)
        self.assertEqual([row["pid"] for row in result["processes"]], [10, 20, 30])
        self.assertEqual([row["parent_pid"] for row in result["processes"]], [11, 21, 31])
        self.assertEqual(result["rejected_parent_count"], 1)
        self.assertEqual(result["read_error_count"], 1)
        self.assertNotIn(12, reader.lookups)

    def test_races_during_inventory_or_recheck_are_omitted_and_counted(self):
        reader = FakeReader([process(10, "chrome.exe"), process(20, "notepad.exe"),
                             process(30, "explorer.exe"), process(40, "chrome.exe")],
                            {10: [1001], 20: [100, 101], 30: [100, OSError("exited")], 40: [100]},
                            inventory_time=1000)
        result = runner.collect_rundown_snapshot("before-native", reader)
        self.assertEqual([row["pid"] for row in result["processes"]], [40])
        self.assertEqual(result["race_discard_count"], 2)
        self.assertEqual(result["read_error_count"], 1)

    def test_cycles_terminate_and_unexpected_names_are_redacted(self):
        reader = FakeReader([process(10, "chrome.exe", 20),
                             process(20, "C:\\private\\launcher.exe", 10)],
                            {10: [100], 20: [100]})
        result = runner.collect_rundown_snapshot("before-native", reader)
        self.assertEqual(len(result["processes"]), 2)
        self.assertEqual(result["processes"][1]["name"], "redacted-process-name")
        self.assertEqual(result["rejected_parent_count"], 1)

    def test_inventory_failure_propagates_without_fabricated_snapshot(self):
        reader = Mock()
        reader.inventory.side_effect = OSError("inventory failed")
        with self.assertRaises(OSError):
            runner.collect_rundown_snapshot("before-native", reader)
        reader.created.assert_not_called()

    def test_filetime_conversion_retains_low_bits(self):
        value = SimpleNamespace(dwHighDateTime=0x01DC0000, dwLowDateTime=0xDEADBEEF)
        self.assertEqual(runner.WindowsSnapshotReader.filetime(value), 0x01DC0000DEADBEEF)

    def test_query_error_closes_handle_and_uses_only_limited_query_access(self):
        import ctypes
        from ctypes import wintypes
        reader = object.__new__(runner.WindowsSnapshotReader)
        reader.ctypes = SimpleNamespace(byref=ctypes.byref, get_last_error=lambda: 5,
                                       WinError=lambda code: OSError(code, "query failed"))
        reader.wintypes = wintypes
        reader.kernel = Mock()
        reader.kernel.OpenProcess.return_value = 123
        reader.kernel.GetProcessTimes.return_value = False
        with self.assertRaises(OSError):
            reader.created(10)
        reader.kernel.OpenProcess.assert_called_once_with(0x1000, False, 10)
        reader.kernel.CloseHandle.assert_called_once_with(123)


class RundownWorkerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.capture = self.root / "capture"
        self.capture.mkdir()
        self.output = self.root / "native"
        self.stamp = datetime(2026, 10, 16, tzinfo=timezone.utc).timestamp()

    def run_worker(self, require=False, ready_flag=None, native_code=0):
        ready = {"status": "recording", "collector_pid": 999,
                 "collector_created_utc": "2026-10-15T23:59:00+00:00",
                 "ready_utc": "2026-10-16T00:00:01+00:00", "session_name": "test",
                 "trace_started_utc": "2026-10-16T00:00:00+00:00", "max_seconds": 900}
        if ready_flag is not None:
            ready["request_rundown"] = ready_flag
        (self.capture / "capture-ready.json").write_text(json.dumps(ready), encoding="utf-8")
        collector = Mock()
        collector.create_time.return_value = self.stamp - 60
        windll = Mock()
        windll.shell32.IsUserAnAdmin.return_value = False
        order = []

        def snapshot(phase):
            order.append(phase)
            return {"phase": phase, "source": "Toolhelp32Snapshot+GetProcessTimes",
                    "started_utc": runner.now(), "finished_utc": runner.now(), "processes": []}

        def native(*args):
            order.append("native")
            return native_code

        with ExitStack() as stack:
            stack.enter_context(patch.object(runner, "os", SimpleNamespace(name="nt", getpid=lambda: 222)))
            stack.enter_context(patch("ctypes.windll", windll, create=True))
            stack.enter_context(patch("psutil.Process", return_value=collector))
            stack.enter_context(patch.object(runner.time, "time", return_value=self.stamp + 10))
            stack.enter_context(patch.object(runner.time, "sleep"))
            stack.enter_context(patch.object(runner.subprocess, "check_output", return_value="testcommit\n"))
            canary = stack.enter_context(patch.object(runner, "simple_canary", return_value={"actual_exit_code": 0, "expected_exit_code": 0}))
            nested = stack.enter_context(patch.object(runner, "nested_canary", return_value=[]))
            snapshots = stack.enter_context(patch.object(runner, "collect_rundown_snapshot", side_effect=snapshot))
            workload = stack.enter_context(patch.object(runner, "run_native_guarded", side_effect=native))
            stack.enter_context(redirect_stderr(io.StringIO()))
            args = ["--capture-dir", str(self.capture), "--native-output", str(self.output)]
            if require:
                args.append("--require-rundown")
            try:
                result = runner.main(args)
            except SystemExit as exc:
                result = exc
        return result, order, canary, nested, snapshots, workload

    def test_required_rundown_rejects_absent_or_nonboolean_ready_flag_before_work(self):
        for value in (None, False, "true", 1):
            with self.subTest(value=value):
                result, order, canary, nested, snapshots, workload = self.run_worker(True, value)
                self.assertIsInstance(result, SystemExit)
                self.assertEqual(result.code, 2)
                self.assertEqual(order, [])
                for mock in (canary, nested, snapshots, workload):
                    mock.assert_not_called()
                self.assertFalse((self.capture / "canary-ground-truth.json").exists())

    def test_default_behavior_does_not_collect_or_require_snapshots(self):
        result, order, _, _, snapshots, _ = self.run_worker()
        self.assertEqual(result, 0)
        self.assertEqual(order, ["native"])
        snapshots.assert_not_called()
        ground = json.loads((self.capture / "canary-ground-truth.json").read_text())
        self.assertNotIn("require_rundown", ground)
        self.assertNotIn("rundown_identity_snapshots", ground)

    def test_requested_snapshots_bracket_native_even_when_native_reports_failure(self):
        for native_code in (0, 9):
            with self.subTest(native_code=native_code):
                for name in ("canary-ground-truth.json", "stop.request"):
                    (self.capture / name).unlink(missing_ok=True)
                result, order, canary, _, _, _ = self.run_worker(True, True, native_code)
                self.assertEqual(result, 0 if native_code == 0 else 1)
                self.assertEqual(order, ["before-native", "native", "after-native"])
                ground = json.loads((self.capture / "canary-ground-truth.json").read_text())
                self.assertIs(ground["require_rundown"], True)
                before, after = ground["rundown_identity_snapshots"]
                self.assertLessEqual(before["finished_utc"], ground["native_started_utc"])
                self.assertGreaterEqual(after["started_utc"], ground["native_finished_utc"])
                self.assertEqual(ground["native_exit_code"], native_code)
                self.assertEqual(ground["status"], "completed" if native_code == 0 else "failed")
                self.assertEqual(canary.call_count, 24 if native_code == 0 else 12)
                self.assertTrue((self.capture / "stop.request").exists())


if __name__ == "__main__":
    unittest.main()
