import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from office_twin.runner import RunConfig, run
from office_twin.simulation import SimulationDesktop
from office_twin.compare import generate_comparison_report


class RunnerTests(unittest.TestCase):
    def read_run(self, summary):
        root = Path(summary["run_directory"])
        saved = json.loads((root / "summary.json").read_text(encoding="utf-8"))
        events = [json.loads(line) for line in (root / "events.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(summary["status"], saved["status"])
        self.assertIn("resources", saved)
        self.assertTrue((root / "report.html").is_file())
        self.assertEqual(events[-1]["event"], "resource_monitor_stopped")
        return saved, events

    def test_simulation_never_imports_native_backends_or_claims_native_verification(self):
        with tempfile.TemporaryDirectory() as output, patch.dict("sys.modules", {"office_twin.desktop": None, "office_twin.sheets": None}):
            summary = run(RunConfig(mode="simulate", workflow="office", scale=0, output=output))
            saved, events = self.read_run(summary)
            self.assertTrue(saved["success"], saved.get("error"))
            self.assertEqual(saved["status"], "plan_completed")
            self.assertTrue(saved["verification"]["plan_only"])
            self.assertFalse(saved["verification"]["native_verified"])
            self.assertEqual(saved["steps_completed"], saved["steps_total"])
            actions = [e for e in events if e["event"] == "simulated_action"]
            self.assertEqual(len(actions), saved["steps_total"])
            self.assertTrue(all(e["native_action"] is False for e in actions))
            self.assertGreater(saved["timing"]["sample_count"], 0)

    def test_cancellation_before_first_step_has_durable_evidence(self):
        cancel = threading.Event()
        cancel.set()
        with tempfile.TemporaryDirectory() as output:
            summary = run(RunConfig(scale=0, output=output), cancel=cancel)
            saved, events = self.read_run(summary)
            self.assertEqual(saved["status"], "cancelled")
            self.assertFalse(saved["success"])
            self.assertEqual(saved["steps_completed"], 0)
            self.assertFalse(any(e["event"] == "simulated_action" for e in events))

    def test_cancellation_at_input_boundary_stops_remaining_steps(self):
        cancel = threading.Event()
        def cancel_at_start(event):
            if event["event"] == "step_started":
                cancel.set()
        with tempfile.TemporaryDirectory() as output:
            summary = run(RunConfig(scale=0, output=output), cancel=cancel, on_event=cancel_at_start)
            saved, events = self.read_run(summary)
            self.assertEqual(saved["status"], "cancelled")
            self.assertEqual(saved["steps_completed"], 0)
            self.assertFalse(any(e["event"] == "simulated_action" for e in events))

    def test_execution_exception_still_writes_summary_and_report(self):
        with tempfile.TemporaryDirectory() as output, patch.object(SimulationDesktop, "run_step", side_effect=RuntimeError("controlled test failure")):
            summary = run(RunConfig(scale=0, output=output))
            saved, events = self.read_run(summary)
            self.assertFalse(saved["success"])
            self.assertEqual(saved["status"], "failed")
            self.assertIn("controlled test failure", saved["error"])
            self.assertTrue(any(e["event"] == "run_error" for e in events))

    def test_progress_callback_failure_does_not_destroy_durable_evidence(self):
        def broken_callback(event):
            raise RuntimeError("progress display unavailable")
        with tempfile.TemporaryDirectory() as output:
            summary = run(RunConfig(scale=0, output=output), on_event=broken_callback)
            saved, events = self.read_run(summary)
            self.assertIn(saved["status"], {"failed", "plan_completed"})
            self.assertGreater(len(events), 1)


class ComparisonTests(unittest.TestCase):
    def test_mixed_modes_and_interrupted_waits_remain_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = root / "simulation", root / "desktop"
            first.mkdir()
            second.mkdir()
            for path, backend, success, status in ((first, "simulation", True, "plan_completed"), (second, "desktop", False, "cancelled")):
                (path / "summary.json").write_text(json.dumps({"backend": backend, "success": success, "status": status, "config": {"workflow": "office", "timing": "fixed", "scale": 1}, "resources": {"controller_cpu_seconds": 0.2, "wall_seconds": 1.3}}), encoding="utf-8")
                (path / "events.jsonl").write_text(json.dumps({"event": "timing", "kind": "read", "delay_seconds": 1.0, "actual_wait_seconds": 0.01, "interrupted": not success}) + "\n", encoding="utf-8")
            document = generate_comparison_report([first, second], root / "comparison.html").read_text(encoding="utf-8")
            for phrase in ("Mixed execution backends", "cancelled", "plan_completed", "1.000 s", "0.010 s", "Interrupted", "plan replay only", "not total application or system CPU"):
                self.assertIn(phrase, document)

    def test_missing_data_not_success_and_markup_is_escaped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            attack = '<script>alert("unsafe")</script>'
            (root / "summary.json").write_text(json.dumps({"run_id": attack, "backend": attack}), encoding="utf-8")
            document = generate_comparison_report([root], root / "comparison.html").read_text(encoding="utf-8")
            self.assertNotIn(attack, document)
            self.assertIn("&lt;script&gt;", document)
            self.assertIn("Not declared", document)
            self.assertIn("Unavailable", document)

    def test_duplicate_directories_do_not_inflate_sample_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document = generate_comparison_report([root, root], root / "comparison.html").read_text(encoding="utf-8")
            self.assertIn("1 supplied run(s)", document)
            self.assertIn("Excluded 1 repeated", document)
            with self.assertRaises(ValueError):
                generate_comparison_report([root], root / "summary.json")


if __name__ == "__main__":
    unittest.main()
