import json
from pathlib import Path
import tempfile
import unittest

from tools.analyze_benchmark import analyze, distribution, export, main, markdown


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_fixture(self, name, policy="fixed", success=True, end=20, backend="desktop", units=1):
        path = self.root / name
        path.mkdir()
        summary = {"run_id": name, "backend": backend, "status": "completed" if success else "failed",
                   "success": success, "steps_total": 2, "steps_completed": 2 if success else 1,
                   "config": {"workflow": "sheets", "sheet_url": "https://docs.google.com/spreadsheets/d/PRIVATE_SHEET_ID"},
                   "timing": {"mode": policy, "seed": 211, "scale": 1, "model_version": "contextual-v1"},
                   "scenario_sha256": "a" * 64,
                   "resources": {"wall_seconds": 100 + end, "controller_cpu_seconds": end / 10,
                                 "controller_peak_rss_bytes": 80000000, "sample_interval_seconds": 0.25}}
        events = [{"event": "run_started", "perf_counter": 100},
                  {"event": "step_started", "index": 1, "perf_counter": 110},
                  {"event": "timing", "kind": "key", "units": units, "delay_seconds": 0.1, "actual_wait_seconds": 0.11, "interrupted": False},
                  {"event": "step_completed", "index": 1, "perf_counter": 115}]
        if success:
            events += [{"event": "step_started", "index": 2, "perf_counter": 116},
                       {"event": "step_completed", "index": 2, "perf_counter": 100 + end}]
        events += [{"event": "run_finished", "perf_counter": 1000}]
        (path / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        (path / "events.jsonl").write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
        return path

    def manifest(self, paths, **changes):
        manifest = {"source_commit": "b" * 40, "environment_id": "same warm session", "capture_condition": "no-screen-recording",
                    "runs": [{"path": str(path.relative_to(self.root)), "pair_id": "pair211"} for path in paths]}
        manifest.update(changes)
        path = self.root / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_paired_task_interval_excludes_startup_and_cleanup(self):
        a = self.run_fixture("fixed")
        b = self.run_fixture("contextual", "contextual", end=23)
        result = analyze(manifest=self.manifest([a, b]))
        self.assertEqual(result["summary"]["performance_comparable_pairs"], 1)
        self.assertEqual(result["runs"][0]["task_interval"]["task_seconds"], 10)
        self.assertEqual(result["runs"][0]["resources"]["wall_seconds"], 120)
        self.assertEqual(result["pairs"][0]["contextual_minus_fixed"]["task_seconds"], 3)
        self.assertEqual(result["human_reference_runs"], 0)

    def test_failure_kept_with_partial_interval_and_no_efficiency_delta(self):
        a = self.run_fixture("fixed")
        b = self.run_fixture("contextual", "contextual", success=False)
        result = analyze(manifest=self.manifest([a, b]))
        self.assertEqual(result["summary"]["attempts"], 2)
        self.assertEqual(result["summary"]["complete_verified_desktop_tasks"], 1)
        self.assertIsNone(result["runs"][1]["task_interval"]["task_seconds"])
        self.assertEqual(result["runs"][1]["task_interval"]["partial_through_last_completed_step_seconds"], 5)
        self.assertNotIn("contextual_minus_fixed", result["pairs"][0])

    def test_explicit_mismatches_are_rejected_not_silently_paired(self):
        a = self.run_fixture("fixed")
        b = self.run_fixture("contextual", "contextual")
        path = b / "summary.json"
        summary = json.loads(path.read_text())
        summary["scenario_sha256"] = "c" * 64
        path.write_text(json.dumps(summary))
        result = analyze(manifest=self.manifest([a, b]))
        self.assertFalse(result["pairs"][0]["performance_comparable"])
        self.assertIn("Mismatched scenario_sha256.", result["pairs"][0]["reasons"])

    def test_missing_version_capture_and_pair_are_not_controlled(self):
        a = self.run_fixture("fixed")
        result = analyze([a, a])
        self.assertEqual(result["summary"]["attempts"], 1)
        self.assertEqual(result["summary"]["duplicate_paths_excluded"], 1)
        self.assertFalse(result["pairs"][0]["performance_comparable"])
        self.assertIn("Missing required matching metadata: source_commit.", result["pairs"][0]["reasons"])
        self.assertIn("Missing required matching metadata: capture_condition_sha256.", result["pairs"][0]["reasons"])

    def test_export_omits_paths_sheet_ids_raw_errors_and_arbitrary_text(self):
        a = self.run_fixture("private-name")
        path = a / "summary.json"
        summary = json.loads(path.read_text())
        secret = "SECRET_USERNAME_AND_CONTENT"
        summary.update({"run_id": secret, "error": secret, "run_directory": "C:/Users/" + secret,
                        "artifacts": {"scenario": secret}, "process_trace": {"reason": secret, "path": secret, "available": False}})
        summary["resources"]["process_observations"] = [{"name": secret, "pid": 999}]
        path.write_text(json.dumps(summary))
        manifest = self.manifest([a], environment_id=secret, capture_condition=secret)
        result = analyze(manifest=manifest)
        outputs = export(result, self.root / "export")
        for output in outputs:
            text = output.read_text()
            for excluded in (secret, "PRIVATE_SHEET_ID", "private-name", str(self.root), "C:/Users"):
                self.assertNotIn(excluded, text)
        self.assertIn("No human baseline", markdown(result))

    def test_observer_aggregates_export_without_raw_process_details(self):
        a = self.run_fixture("fixed")
        observer = {"evidence_source": "external_process_snapshot_observer", "status": "completed", "snapshot_count": 50,
                    "duration_seconds": 12.5, "interval_seconds": 0.25, "process_count": 9,
                    "cadence": {"median_gap_seconds": 0.251, "max_gap_seconds": 0.3, "overrun_count": 2},
                    "scopes": {"chrome": {"process_count": 7, "observed_cpu_delta_seconds": 4.5, "peak_sampled_rss_bytes": 1234567}},
                    "observer_resources": {"cpu_seconds": 0.2, "peak_sampled_rss_bytes": 9876},
                    "processes": [{"pid": 4444, "cmdline": "SECRET_COMMAND"}], "stop_reason": "SECRET_COMMAND"}
        (a / "external-observer-summary.json").write_text(json.dumps(observer))
        result = analyze([a])
        exported = result["runs"][0]["external_observer"]
        self.assertTrue(exported["available"])
        self.assertEqual(exported["scopes"]["chrome"]["observed_cpu_delta_seconds"], 4.5)
        self.assertEqual(exported["observer_resources"]["cpu_seconds"], 0.2)
        self.assertFalse(exported["process_start_event_trace"])
        self.assertNotIn("SECRET_COMMAND", json.dumps(result))
        self.assertIn("nonexclusive", markdown(result))

    def test_waits_keep_units_and_interruption_separate(self):
        a = self.run_fixture("fixed")
        with (a / "events.jsonl").open("a") as output:
            output.write("\n" + json.dumps({"event": "timing", "kind": "key", "units": 2, "delay_seconds": 0.2,
                                           "actual_wait_seconds": 0.05, "interrupted": True}))
        waits = analyze([a])["runs"][0]["waits_by_kind_and_units"]
        self.assertEqual([wait["units"] for wait in waits], [1, 2])
        self.assertEqual(waits[1]["actual_wait"]["count"], 1)
        self.assertEqual(waits[1]["uninterrupted_actual_wait"]["count"], 0)
        self.assertEqual(waits[1]["interrupted_count"], 1)
        self.assertEqual(distribution([1, 2, 3])["p90_seconds"], 2.8)

    def test_simulation_success_never_counts_as_native_and_malformed_event_warns(self):
        a = self.run_fixture("simulation", backend="simulation")
        with (a / "events.jsonl").open("a") as output:
            output.write("\nnot-json")
        result = analyze([a])
        self.assertEqual(result["summary"]["complete_verified_desktop_tasks"], 0)
        self.assertIn("A malformed event was excluded.", result["runs"][0]["warnings"])

    def test_per_trial_metadata_and_root_cli(self):
        a = self.run_fixture("fixed")
        metadata = {"source_commit": "e" * 40, "environment_id": "warm", "capture_condition": "no-screen-recording"}
        (a / "trial-metadata.json").write_text(json.dumps(metadata))
        self.assertEqual(analyze([a])["runs"][0]["source_commit"], "e" * 40)
        self.manifest([a])
        self.assertEqual(main(["--root", str(self.root), "--output", str(self.root / "export")]), 0)
        self.assertTrue((self.root / "export" / "benchmark.json").is_file())
        self.assertTrue((self.root / "export" / "BENCHMARK.md").is_file())

    def test_harness_launch_failure_without_summary_is_preserved(self):
        a = self.run_fixture("fixed")
        missing = self.root / "unstarted" / "runs"
        path = self.manifest([a])
        manifest = json.loads(path.read_text())
        manifest["runs"].append({"path": str(missing.relative_to(self.root)), "pair_id": "pair211", "seed": 211,
                                 "timing": "contextual", "backend": "desktop", "workflow": "sheets", "scale": 1,
                                 "status": "failed", "error_type": "DO_NOT_EXPORT_PRIVATE_ERROR"})
        path.write_text(json.dumps(manifest))
        result = analyze(manifest=path)
        self.assertEqual(result["summary"]["attempts"], 2)
        self.assertEqual(result["runs"][1]["policy"], "contextual")
        self.assertEqual(result["runs"][1]["seed"], 211)
        self.assertEqual(result["runs"][1]["status"], "failed")
        self.assertFalse(result["pairs"][0]["performance_comparable"])
        self.assertNotIn("DO_NOT_EXPORT_PRIVATE_ERROR", json.dumps(result))

    def test_changed_capture_or_instrumentation_invalidates_pair(self):
        a = self.run_fixture("fixed")
        b = self.run_fixture("contextual", "contextual")
        path = self.manifest([a, b])
        manifest = json.loads(path.read_text())
        manifest["runs"][0]["measurement_sha256"] = "c" * 64
        manifest["runs"][1].update({"capture_condition": "screen-recording", "measurement_sha256": "d" * 64})
        path.write_text(json.dumps(manifest))
        result = analyze(manifest=path)
        self.assertFalse(result["pairs"][0]["performance_comparable"])
        self.assertIn("Mismatched capture_condition_sha256.", result["pairs"][0]["reasons"])
        self.assertIn("Mismatched or incomplete optional measurement_sha256.", result["pairs"][0]["reasons"])

    def test_failed_measurement_does_not_erase_native_success_or_allow_comparison(self):
        a = self.run_fixture("fixed")
        b = self.run_fixture("contextual", "contextual")
        path = self.manifest([a, b])
        manifest = json.loads(path.read_text())
        manifest["runs"][1]["attempt_status"] = "failed"
        path.write_text(json.dumps(manifest))
        for run in (a, b):
            (run / "external-observer-summary.json").write_text(json.dumps({
                "evidence_source": "external_process_snapshot_observer", "interval_seconds": 0.1,
                "snapshot_count": 100, "status": "completed" if run == a else "failed"}))
        result = analyze(manifest=path)
        self.assertEqual(result["summary"]["complete_verified_desktop_tasks"], 2)
        self.assertFalse(result["pairs"][0]["performance_comparable"])
        self.assertTrue(any("Harness completion" in reason for reason in result["pairs"][0]["reasons"]))
        self.assertTrue(any("external observer" in reason for reason in result["pairs"][0]["reasons"]))


if __name__ == "__main__":
    unittest.main()
