from contextlib import nullcontext
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from office_twin.observer import (LIMITATIONS, ObservationLedger, ProcessSnapshotProvider,
                                  clean_process, identity, observe)


def row(pid=12, created=100.0, cpu=50.0, rss=100, scope="chrome", **extra):
    return {"pid": pid, "create_time": created, "name": "chrome.exe", "scope": scope,
            "parent_pid": 8, "parent_identity": {"pid": 8, "create_time": 90.0, "name": "explorer.exe"},
            "cpu_total_seconds": cpu, "rss_bytes": rss, **extra}


def fake_process(created=100.0, cpu=50.0, rss=100):
    proc = Mock()
    proc.oneshot.side_effect = nullcontext
    proc.create_time.return_value = created
    proc.cpu_times.return_value = SimpleNamespace(user=cpu, system=0.0)
    proc.memory_info.return_value = SimpleNamespace(rss=rss)
    return proc


class ObserverTests(unittest.TestCase):
    def test_cpu_uses_first_observation_baseline_and_pid_reuse_is_separate(self):
        ledger = ObservationLedger()
        ledger.add([row(cpu=500.0)], 0.0)
        ledger.add([row(cpu=501.5)], 0.1)
        ledger.add([], 0.2)
        # The same PID refers to a different identity; its initial lifetime
        # CPU must not be compared with the previous process's counters.
        ledger.add([row(created=110.0, cpu=0.2)], 0.3)
        ledger.add([row(created=110.0, cpu=0.5)], 0.4)
        result = ledger.summarize(0.1)
        self.assertEqual(result["process_count"], 2)
        self.assertAlmostEqual(result["scopes"]["chrome"]["observed_cpu_delta_seconds"], 1.8)
        self.assertEqual(result["not_seen_transitions"], 1)

    def test_scope_rss_peak_is_simultaneous_sum_not_sum_of_individual_peaks(self):
        ledger = ObservationLedger()
        ledger.add([row(pid=12, rss=100), row(pid=13, rss=20)], 0.0)
        ledger.add([row(pid=12, rss=20), row(pid=13, rss=100)], 0.1)
        summary = ledger.summarize(0.1)
        self.assertEqual(summary["scopes"]["chrome"]["peak_sampled_rss_bytes"], 120)
        self.assertEqual(sum(record["peak_sampled_rss_bytes"] for record in summary["process_observations"]), 200)

    def test_allowlist_excludes_content_paths_and_untrusted_name_values(self):
        clean = clean_process(row(name="C:\\Users\\private\\chrome.exe", cmdline="https://secret.example",
                                  username="secret-account", window_title="private document",
                                  parent_identity={"pid": 8, "create_time": 90, "name": "http://private"}))
        encoded = json.dumps(clean)
        for secret in ("Users", "secret", "window_title", "cmdline", "http:"):
            self.assertNotIn(secret, encoded)
        self.assertEqual(clean["name"], "redacted-process-name")
        self.assertEqual(clean["parent_identity"]["name"], "redacted-process-name")

    def test_newer_or_mismatched_current_parent_is_not_assigned_as_original(self):
        self.assertIsNone(clean_process(row(parent_identity={"pid": 8, "create_time": 101, "name": "other.exe"}))["parent_identity"])
        self.assertIsNone(clean_process(row(parent_identity={"pid": 9, "create_time": 90, "name": "other.exe"}))["parent_identity"])

    def test_first_seen_is_not_start_event_and_actual_sampling_gaps_are_reported(self):
        ledger = ObservationLedger()
        ledger.add([row(cpu=200)], 0)
        event = ledger.add([], 0.5)
        result = ledger.summarize(0.1)
        self.assertEqual(result["scopes"]["chrome"]["observed_cpu_delta_seconds"], 0)
        self.assertEqual(result["scopes"]["chrome"]["single_sample_process_count"], 1)
        self.assertEqual(result["cadence"]["max_gap_seconds"], 0.5)
        self.assertEqual(result["cadence"]["overrun_count"], 1)
        self.assertEqual(event["not_seen_in_this_snapshot"], [{"pid": 12, "create_time": 100.0}])
        self.assertIn("miss short-lived processes", " ".join(LIMITATIONS))
        self.assertIn("not process-start or exit events", " ".join(LIMITATIONS))

    def test_reused_controller_pid_does_not_select_new_process_descendants(self):
        provider = ProcessSnapshotProvider((4, 50.0))
        metadata = {4: {"pid": 4, "create_time": 200.0, "name": "python.exe", "parent_pid": 2},
                    5: {"pid": 5, "create_time": 210.0, "name": "python.exe", "parent_pid": 4}}
        self.assertIsNone(provider._scope(metadata[4], metadata))
        self.assertIsNone(provider._scope(metadata[5], metadata))
        metadata[4]["create_time"] = 50.0
        self.assertEqual(provider._scope(metadata[4], metadata), "controller")
        self.assertEqual(provider._scope(metadata[5], metadata), "controller_descendants")
        metadata[5]["create_time"] = 40.0
        self.assertIsNone(provider._scope(metadata[5], metadata))

    def test_provider_discards_counter_read_when_pid_reused_mid_sample(self):
        provider = ProcessSnapshotProvider()
        inventory = [{"pid": 12, "name": "chrome.exe", "parent_pid": 0}]
        processes = [fake_process(100), fake_process(100), fake_process(200)]
        with patch("office_twin.observer.process_inventory", return_value=inventory), \
                patch("office_twin.observer.psutil.Process", side_effect=processes):
            result = provider.snapshot()
        self.assertEqual(result, [])
        self.assertEqual(provider.race_discard_count, 1)

    def test_provider_does_not_query_command_lines_or_unselected_process_resources(self):
        provider = ProcessSnapshotProvider()
        inventory = [{"pid": 12, "name": "chrome.exe", "parent_pid": 8},
                     {"pid": 8, "name": "explorer.exe", "parent_pid": 0},
                     {"pid": 60, "name": "private-app.exe", "parent_pid": 0}]
        child, parent = fake_process(100), fake_process(90)
        def process(pid):
            if pid == 12:
                return child
            if pid == 8:
                return parent
            raise AssertionError("An unrelated process was queried")
        with patch("office_twin.observer.process_inventory", return_value=inventory), \
                patch("office_twin.observer.psutil.Process", side_effect=process):
            result = provider.snapshot()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["parent_identity"]["name"], "explorer.exe")
        parent.cpu_times.assert_not_called()
        parent.memory_info.assert_not_called()
        child.cmdline.assert_not_called()
        child.username.assert_not_called()
        child.exe.assert_not_called()

    def test_stop_marker_writes_ready_and_summary_and_binds_only_allowed_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stop_file, binding = root / "stop", root / "controller.json"
            stop_file.touch()
            binding.write_text(json.dumps({"pid": 123, "create_time": 100.0, "cmdline": "private-url"}))
            with patch("office_twin.observer.ProcessSnapshotProvider.snapshot", return_value=[row()]):
                result = observe(root / "evidence", stop_file=stop_file, controller_file=binding)
            self.assertEqual(result["controller_identity"], {"pid": 123, "create_time": 100.0})
            self.assertFalse(result["process_start_event_trace"])
            self.assertEqual(result["stop_reason"], "stop_file")
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["snapshot_count"], 1)
            self.assertTrue((root / "evidence" / "observer-ready.json").exists())
            self.assertTrue((root / "evidence" / "external-observer-summary.json").exists())
            self.assertNotIn("private-url", (root / "evidence" / "external-observer-summary.json").read_text())
            with self.assertRaisesRegex(ValueError, "never overwritten"):
                observe(root / "evidence", duration=0.01)

    def test_invalid_identities_and_measurements_are_rejected(self):
        for pid, created in ((True, 100), (0, 100), (12, float("nan")), (12, True), (12, 0)):
            with self.assertRaises(ValueError):
                identity(pid, created)
        for values in ({"cpu": float("inf")}, {"cpu": -1}, {"rss": -1}, {"rss": 1.5}, {"scope": "unknown"}):
            with self.assertRaises(ValueError):
                clean_process(row(**values))


if __name__ == "__main__":
    unittest.main()
