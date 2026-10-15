import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from tools.record_manual import ManualRecorder


class ManualRecorderTests(unittest.TestCase):
    def test_explicit_boundaries_and_markers_never_claim_verified_human_success(self):
        with tempfile.TemporaryDirectory() as directory, patch("tools.record_manual.psutil", None):
            recorder = ManualRecorder(Path(directory) / "attempt", "P01")
            with self.assertRaises(RuntimeError):
                recorder.mark("quotes-reviewed")
            recorder.start()
            recorder.mark("quotes-reviewed")
            result = recorder.stop()
            self.assertEqual(result["outcome"], "completed-unverified")
            self.assertFalse(result["task_success_verified"])
            self.assertFalse(result["human_provenance_independently_verified"])
            self.assertEqual(result["resources"]["process_observations"], [])
            self.assertGreaterEqual(result["elapsed_seconds"], 0)
            records = [json.loads(line) for line in (recorder.directory / "manual-events.jsonl").read_text().splitlines()]
            self.assertEqual([record["event"] for record in records], ["start", "participant_marker", "stop"])
            self.assertEqual(recorder.stop(), result)

    def test_arbitrary_input_markers_are_rejected_and_not_logged(self):
        with tempfile.TemporaryDirectory() as directory, patch("tools.record_manual.psutil", None):
            recorder = ManualRecorder(Path(directory) / "attempt", "P02")
            recorder.start()
            with self.assertRaises(ValueError):
                recorder.mark("private unrelated text")
            recorder.stop("aborted")
            self.assertNotIn("private unrelated text", (recorder.directory / "manual-events.jsonl").read_text())

    def test_process_measurements_are_explicit_deltas_and_pid_reuse_is_ignored(self):
        proc = Mock()
        proc.pid = 123
        proc.name.return_value = "chrome.exe"
        proc.create_time.return_value = 100
        proc.cpu_times.return_value = SimpleNamespace(user=10, system=2)
        proc.memory_info.return_value = SimpleNamespace(rss=1000)
        proc.oneshot.return_value.__enter__ = Mock()
        proc.oneshot.return_value.__exit__ = Mock(return_value=False)
        controller = Mock()
        controller.memory_info.return_value = SimpleNamespace(rss=200)
        fake = Mock()
        fake.Error = RuntimeError
        fake.Process.side_effect = lambda pid: proc if pid == 123 else controller
        with tempfile.TemporaryDirectory() as directory, patch("tools.record_manual.psutil", fake), patch("tools.record_manual.threading.Thread"):
            recorder = ManualRecorder(Path(directory) / "attempt", "P03", [123])
            recorder.start()
            proc.cpu_times.return_value = SimpleNamespace(user=11, system=2.5)
            recorder._sample()
            proc.create_time.return_value = 999  # Same PID, different process identity.
            proc.cpu_times.return_value = SimpleNamespace(user=999, system=999)
            recorder._sample()
            result = recorder.stop("incomplete")
            observed = result["resources"]["process_observations"]
            self.assertEqual(len(observed), 1)
            self.assertEqual(observed[0]["observed_cpu_delta_seconds"], 1.5)
            self.assertEqual(observed[0]["samples"], 2)
            self.assertEqual(observed[0]["selection"], "explicitly selected PID")
            fake.process_iter.assert_not_called()
            proc.children.assert_not_called()

    def test_unsupported_process_is_rejected_before_recording(self):
        fake = Mock()
        fake.Process.return_value.name.return_value = "unrelated.exe"
        with tempfile.TemporaryDirectory() as directory, patch("tools.record_manual.psutil", fake):
            output = Path(directory) / "attempt"
            recorder = ManualRecorder(output, "P04", [123])
            with self.assertRaises(ValueError):
                recorder.start()
            self.assertFalse(output.exists())

    def test_existing_output_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory, patch("tools.record_manual.psutil", None):
            with self.assertRaises(FileExistsError):
                ManualRecorder(Path(directory), "P05").start()


if __name__ == "__main__":
    unittest.main()
