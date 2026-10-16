import json
import os
from contextlib import nullcontext
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from office_twin.evidence import EvidenceRecorder
from office_twin.report import generate_report


class EvidenceTests(unittest.TestCase):
    def test_events_preserve_payload_and_protect_measurement_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = EvidenceRecorder(Path(directory))
            with patch("office_twin.evidence.psutil", None):
                recorder.start()
                recorder.emit({"event": "key", "kind": "key", "timestamp_utc": "fake", "sequence": 999})
                summary = recorder.stop()
                self.assertEqual(summary, recorder.stop())
            records = [json.loads(line) for line in recorder.events_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([r["sequence"] for r in records], [1, 2, 3])
            self.assertNotEqual(records[1]["timestamp_utc"], "fake")
            self.assertEqual(records[1]["evidence_source"], "controller_observation")
            self.assertGreaterEqual(summary["controller_cpu_seconds"], 0)
            self.assertGreaterEqual(summary["wall_seconds"], 0)
            self.assertIsNone(summary["controller_peak_rss_bytes"])

    def test_context_manager_stops_on_exception(self):
        with tempfile.TemporaryDirectory() as directory, patch("office_twin.evidence.psutil", None):
            recorder = EvidenceRecorder(Path(directory))
            with self.assertRaisesRegex(RuntimeError, "planned"):
                with recorder:
                    raise RuntimeError("planned")
            self.assertIsNotNone(recorder._summary)
            self.assertIn("run_exception", recorder.events_path.read_text(encoding="utf-8"))

    def test_controller_cpu_is_a_delta_not_lifetime_or_other_process_cpu(self):
        with tempfile.TemporaryDirectory() as directory, patch("office_twin.evidence.psutil", None), patch("office_twin.evidence.time.process_time", side_effect=[100.0, 101.25]):
            recorder = EvidenceRecorder(Path(directory)).start()
            recorder._observed[(8, 100)] = {"pid": 8, "name": "example", "cpu_first_seconds": 50.0, "cpu_last_seconds": 53.0}
            summary = recorder.stop()
            self.assertEqual(summary["controller_cpu_seconds"], 1.25)
            self.assertEqual(summary["process_observations"][0]["observed_cpu_delta_seconds"], 3.0)

    def test_report_escapes_fields_and_labels_simulation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            attack = '<script>alert("unsafe")</script>'
            (root / "summary.json").write_text(json.dumps({"backend": "simulation", "run_id": attack, "success": True, "timing": {"mode": "contextual"}}), encoding="utf-8")
            (root / "events.jsonl").write_text(json.dumps({"event": attack, "kind": attack, "delay_seconds": 0.4}) + "\nnot json\n", encoding="utf-8")
            report = generate_report(root).read_text(encoding="utf-8")
            self.assertNotIn(attack, report)
            self.assertIn("&lt;script&gt;", report)
            self.assertIn("SIMULATION", report)
            self.assertIn("Skipped 1 malformed", report)
            self.assertIn("Unavailable", report)
            self.assertIn("not independent Sysmon", report)

    def test_report_does_not_turn_missing_summary_into_success(self):
        with tempfile.TemporaryDirectory() as directory:
            report = generate_report(Path(directory)).read_text(encoding="utf-8")
            self.assertIn("EXECUTION MODE UNCONFIRMED", report)
            self.assertIn("Outcome not declared", report)
            self.assertNotIn("Declared success", report)

    def test_os_trace_status_is_truthful_escaped_and_links_only_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "summary.json").write_text(json.dumps({"backend": "desktop", "success": False, "process_trace": {"available": False, "provider": "Windows WMI Win32_ProcessStartTrace", "event_count": 0, "reason": "Access denied <unsafe>"}}), encoding="utf-8")
            report = generate_report(root).read_text(encoding="utf-8")
            self.assertIn("OS process-start trace", report)
            self.assertIn("Access denied &lt;unsafe&gt;", report)
            self.assertIn("Status <strong>Unavailable", report)
            self.assertNotIn('href="os-process-events.jsonl"', report)
            (root / "os-process-events.jsonl").touch()
            report = generate_report(root).read_text(encoding="utf-8")
            self.assertIn('href="os-process-events.jsonl"', report)
            self.assertIn("not Sysmon records", report)

    def test_parent_metadata_is_best_effort_without_dropping_process_measurements(self):
        controller = Mock()
        controller.memory_info.return_value = SimpleNamespace(rss=100)
        controller.children.return_value = []
        child = Mock()
        child.info = {"pid": 445, "name": "chrome.exe"}
        child.oneshot.side_effect = nullcontext
        child.create_time.return_value = 20.0
        child.name.return_value = "chrome.exe"
        child.cpu_times.return_value = SimpleNamespace(user=1.0, system=0.5)
        child.memory_info.return_value = SimpleNamespace(rss=2048)
        child.ppid.return_value = 444
        parent = Mock()
        parent.oneshot.side_effect = nullcontext
        parent.create_time.return_value = 10.0
        parent.name.return_value = "explorer.exe"
        fake_psutil = Mock()
        fake_psutil.Error = RuntimeError
        fake_psutil.Process.side_effect = lambda pid: controller if pid == os.getpid() else child if pid == 445 else parent
        inventory = [{"pid": 445, "name": "chrome.exe", "parent_pid": 444}]
        with tempfile.TemporaryDirectory() as directory, patch("office_twin.evidence.psutil", fake_psutil), patch("office_twin.evidence.process_inventory", return_value=inventory):
            recorder = EvidenceRecorder(Path(directory))
            recorder._snapshot()
            observed = recorder.stop()["process_observations"][0]
            self.assertEqual(observed["parent_pid"], 444)
            self.assertEqual(observed["parent_name"], "explorer.exe")
            self.assertEqual(observed["selection"], "application name match")
        parent.name.side_effect = RuntimeError("parent inaccessible")
        with tempfile.TemporaryDirectory() as directory, patch("office_twin.evidence.psutil", fake_psutil), patch("office_twin.evidence.process_inventory", return_value=inventory):
            recorder = EvidenceRecorder(Path(directory))
            recorder._snapshot()
            observed = recorder.stop()["process_observations"][0]
            self.assertEqual(observed["parent_pid"], 444)
            self.assertIsNone(observed["parent_name"])
            self.assertEqual(observed["cpu_first_seconds"], 1.5)

    @staticmethod
    def process(created=20.0, name="chrome.exe", cpu=1.5):
        proc = Mock()
        proc.pid = 445
        proc.oneshot.side_effect = nullcontext
        proc.create_time.return_value = created
        proc.name.return_value = name
        proc.cpu_times.return_value = SimpleNamespace(user=cpu, system=0.0)
        proc.memory_info.return_value = SimpleNamespace(rss=2048)
        return proc

    def snapshot_with_processes(self, recorder, processes, *, descendants=(), parent_pid=0, inventory_name="chrome.exe"):
        controller = Mock()
        controller.memory_info.return_value = SimpleNamespace(rss=100)
        controller.children.return_value = descendants
        sequence = iter(processes)
        def lookup(pid):
            if pid == os.getpid():
                return controller
            value = next(sequence)
            if isinstance(value, Exception):
                raise value
            return value
        fake = Mock()
        fake.Error = RuntimeError
        fake.Process.side_effect = lookup
        fake.process_iter.side_effect = AssertionError("Cached process objects must not supply measurements")
        inventory = [{"pid": 445, "name": inventory_name, "parent_pid": parent_pid}]
        with patch("office_twin.evidence.psutil", fake), patch("office_twin.evidence.process_inventory", return_value=inventory), patch("office_twin.evidence.time.time", return_value=100.0):
            recorder._snapshot()

    def test_pid_reused_during_counter_read_does_not_charge_new_process_to_old_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = EvidenceRecorder(Path(directory))
            self.snapshot_with_processes(recorder, [self.process(), self.process()])
            self.snapshot_with_processes(recorder, [self.process(cpu=100.0), self.process(created=30.0)])
            record = recorder._observed[(445, 20.0)]
            self.assertEqual(record["snapshot_count"], 1)
            self.assertEqual(record["cpu_last_seconds"], 1.5)
            self.snapshot_with_processes(recorder, [self.process(created=30.0, cpu=100.0), self.process(created=30.0)])
            self.assertEqual(set(recorder._observed), {(445, 20.0), (445, 30.0)})
            self.assertEqual(recorder._observed[(445, 30.0)]["cpu_first_seconds"], 100.0)

    def test_process_exit_or_access_race_discards_observation(self):
        for error in (RuntimeError("exited"), OSError("access changed")):
            for during_read in (False, True):
                with self.subTest(error=type(error).__name__, during_read=during_read), tempfile.TemporaryDirectory() as directory:
                    recorder = EvidenceRecorder(Path(directory))
                    processes = [self.process(), error] if during_read else [error]
                    self.snapshot_with_processes(recorder, processes)
                    self.assertEqual(recorder._observed, {})
                    self.assertEqual(recorder._peak_rss, 100)

    def test_pid_born_after_inventory_is_not_given_old_inventory_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = EvidenceRecorder(Path(directory))
            self.snapshot_with_processes(recorder, [self.process(created=101.0)])
            self.assertEqual(recorder._observed, {})

    def test_reused_descendant_pid_does_not_select_unrelated_non_application(self):
        old_child = self.process(created=10.0, name="worker.exe")
        with tempfile.TemporaryDirectory() as directory:
            recorder = EvidenceRecorder(Path(directory))
            self.snapshot_with_processes(recorder, [self.process(name="unrelated.exe")], descendants=[old_child], inventory_name="worker.exe")
            self.assertEqual(recorder._observed, {})
            self.snapshot_with_processes(recorder, [self.process(), self.process()], descendants=[old_child])
            self.assertEqual(recorder._observed[(445, 20.0)]["selection"], "application name match")

    def test_parent_reuse_does_not_change_valid_child_counters_or_invent_parent_name(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder = EvidenceRecorder(Path(directory))
            self.snapshot_with_processes(recorder, [self.process(), self.process(), self.process(created=10.0, name="explorer.exe"), self.process(created=30.0, name="unrelated.exe")], parent_pid=444)
            record = recorder._observed[(445, 20.0)]
            self.assertEqual(record["parent_pid"], 444)
            self.assertIsNone(record["parent_name"])
            self.assertEqual(record["cpu_first_seconds"], 1.5)


if __name__ == "__main__":
    unittest.main()
