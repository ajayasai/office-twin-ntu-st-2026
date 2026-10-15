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
        child.cpu_times.return_value = SimpleNamespace(user=1.0, system=0.5)
        child.memory_info.return_value = SimpleNamespace(rss=2048)
        child.ppid.return_value = 444
        parent = Mock()
        parent.oneshot.side_effect = nullcontext
        parent.create_time.return_value = 10.0
        parent.name.return_value = "explorer.exe"
        fake_psutil = Mock()
        fake_psutil.Error = RuntimeError
        fake_psutil.process_iter.return_value = [child]
        fake_psutil.Process.side_effect = lambda pid: controller if pid == os.getpid() else parent
        with tempfile.TemporaryDirectory() as directory, patch("office_twin.evidence.psutil", fake_psutil):
            recorder = EvidenceRecorder(Path(directory))
            recorder._snapshot()
            observed = recorder.stop()["process_observations"][0]
            self.assertEqual(observed["parent_pid"], 444)
            self.assertEqual(observed["parent_name"], "explorer.exe")
            self.assertEqual(observed["selection"], "application name match")
        parent.name.side_effect = RuntimeError("parent inaccessible")
        with tempfile.TemporaryDirectory() as directory, patch("office_twin.evidence.psutil", fake_psutil):
            recorder = EvidenceRecorder(Path(directory))
            recorder._snapshot()
            observed = recorder.stop()["process_observations"][0]
            self.assertEqual(observed["parent_pid"], 444)
            self.assertIsNone(observed["parent_name"])
            self.assertEqual(observed["cpu_first_seconds"], 1.5)


if __name__ == "__main__":
    unittest.main()
