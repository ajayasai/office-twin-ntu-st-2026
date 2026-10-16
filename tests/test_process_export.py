from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from tools.export_process_evidence import analyze_manifest, export, markdown, summarize_observer


START = datetime(2026, 10, 16, 8, 0, tzinfo=timezone.utc).timestamp()


def process(pid=10001, created=START - 60, name="chrome.exe", scope="chrome", parent=9001, parent_created=START - 120, parent_name="explorer.exe", **extra):
    return {"pid": pid, "create_time": created, "name": name, "scope": scope, "samples": 5,
            "first_observed_seconds": 0.1, "last_observed_seconds": 0.5,
            "cpu_first_seconds": 100.0, "cpu_last_seconds": 101.25, "peak_sampled_rss_bytes": 1048576,
            "parent_pid": parent, "parent_identity": {"pid": parent, "create_time": parent_created, "name": parent_name}, **extra}


def observer(records):
    return {"evidence_source": "external_process_snapshot_observer", "method": "sampled_polling",
            "process_start_event_trace": False, "status": "completed", "process_count": len(records),
            "started_utc": "2026-10-16T08:00:00+00:00", "ended_utc": "2026-10-16T08:03:00+00:00",
            "process_observations": records}


class ProcessExportTests(unittest.TestCase):
    def test_parent_counts_distinguish_preexisting_from_os_creation_in_window(self):
        records = [process(), process(pid=10002, created=START + 1, parent_created=START - 60, parent_name="chrome.exe"),
                   process(pid=10003, created=START + 2, name="python.exe", scope="controller", parent_created=START + 1, parent_name="python.exe")]
        result = summarize_observer(observer(records), "R001", "fixed")
        self.assertEqual(result["unique_observed_identities"], 3)
        self.assertEqual(result["parent_resolution_counts"]["resolved-compatible-age"], 3)
        self.assertEqual(result["creation_counts"]["preexisting-at-observer-start"], 1)
        self.assertEqual(result["creation_counts"]["os-creation-time-within-observer-window"], 2)
        explorer = next(row for row in result["relationships"] if row["parent_role"] == "explorer")
        self.assertEqual(explorer["creation_class"], "preexisting-at-observer-start")
        self.assertFalse(result["process_start_event_trace"])

    def test_duplicate_identities_are_counted_once_and_reused_pids_remain_distinct(self):
        old = process()
        result = summarize_observer(observer([old, dict(old), process(created=START + 1)]), "R001")
        self.assertEqual(result["unique_observed_identities"], 2)
        self.assertEqual(result["duplicate_identity_records_excluded"], 1)
        self.assertEqual(sum(row["identity_count"] for row in result["relationships"]), 2)

    def test_invalid_and_conflicting_parent_claims_are_not_resolved(self):
        newer_parent = process(parent_created=START)
        wrong_parent = process(pid=10002, parent_identity={"pid": 88, "create_time": START - 100, "name": "explorer.exe"})
        conflict_a = process(pid=10003, parent=98)
        conflict_b = process(pid=10003, parent=99)
        result = summarize_observer(observer([newer_parent, wrong_parent, conflict_a, conflict_b]), "R001")
        self.assertEqual(result["parent_resolution_counts"]["resolved-compatible-age"], 0)
        self.assertEqual(result["parent_resolution_counts"]["unresolved"], 2)
        self.assertEqual(result["parent_resolution_counts"]["conflicting-observations"], 1)

    def test_missing_parent_can_be_filled_by_a_later_compatible_observation(self):
        result = summarize_observer(observer([process(parent_identity=None), process()]), "R001")
        self.assertEqual(result["unique_observed_identities"], 1)
        self.assertEqual(result["parent_resolution_counts"]["resolved-compatible-age"], 1)

    def test_pseudonyms_link_only_observed_compatible_parents_and_export_delta_metrics(self):
        parent = process(pid=9001, created=START - 120, parent=8001, parent_created=START - 200, parent_name="explorer.exe")
        child = process(parent_name="chrome.exe")
        other = process(pid=10002, parent=7001)
        result = summarize_observer(observer([parent, child, other]), "R001")
        rows = result["processes"]
        self.assertEqual([row["id"] for row in rows], ["P001", "P002", "P003"])
        self.assertEqual(rows[1]["parent_observed_process_alias"], "P001")
        self.assertIsNone(rows[0]["parent_observed_process_alias"])
        self.assertIsNone(rows[2]["parent_observed_process_alias"])
        self.assertEqual(rows[1]["observed_cpu_delta_seconds"], 1.25)
        self.assertEqual(rows[1]["first_observed_seconds"], 0.1)
        self.assertEqual(rows[1]["last_observed_seconds"], 0.5)
        self.assertEqual(rows[1]["samples"], 5)
        self.assertEqual(rows[1]["peak_sampled_rss_bytes"], 1048576)

    def test_redundant_process_rows_do_not_double_count_samples_cpu_or_memory(self):
        result = summarize_observer(observer([process(), process()]), "R001")
        row = result["processes"][0]
        self.assertEqual(len(result["processes"]), 1)
        self.assertEqual(row["samples"], 5)
        self.assertEqual(row["observed_cpu_delta_seconds"], 1.25)
        self.assertEqual(row["peak_sampled_rss_bytes"], 1048576)

    def test_privacy_allowlist_excludes_all_arbitrary_strings_and_raw_identifiers(self):
        secret = "PRIVATE_ACCOUNT_SECRET"
        data = observer([process(pid=874567, name=secret + ".exe", parent=963852,
                                 parent_name="C:/Users/" + secret + "/python.exe",
                                 cmdline="https://secret.example/" + secret, username=secret, path=secret)])
        data.update({"provider": secret, "selection": secret, "error": secret})
        result = summarize_observer(data, "R001", secret)
        encoded = json.dumps(result)
        for denied in (secret, "874567", "963852", str(START - 60), "2026-10-16", "secret.example", "C:/Users"):
            self.assertNotIn(denied, encoded)
        self.assertEqual(result["policy"], "unknown")
        self.assertEqual(result["relationships"][0]["application_role"], "other-redacted")
        self.assertEqual(result["relationships"][0]["parent_role"], "other-redacted")

    def test_unknown_or_inverted_windows_do_not_become_new_process_evidence(self):
        data = observer([process()])
        data["ended_utc"] = "2026-10-16T07:59:00+00:00"
        result = summarize_observer(data, "R001")
        self.assertFalse(result["creation_window_valid"])
        self.assertEqual(result["creation_counts"]["unresolved-or-outside-window"], 1)
        data["ended_utc"] = "2026-10-16T08:03:00"  # Missing time zone is ambiguous.
        self.assertFalse(summarize_observer(data, "R001")["creation_window_valid"])

    def test_invalid_identity_or_unobserved_record_is_excluded(self):
        result = summarize_observer(observer([process(pid=True), process(created=float("nan")), process(samples=0), "invalid"]), "R001")
        self.assertEqual(result["unique_observed_identities"], 0)
        self.assertEqual(result["invalid_records_excluded"], 4)

    def test_manifest_aliases_match_first_occurrence_order_and_export_stays_private(self):
        with tempfile.TemporaryDirectory(prefix="private-source-path-") as directory:
            root = Path(directory)
            (root / "observer-a").mkdir()
            (root / "observer-b").mkdir()
            for name in ("observer-a", "observer-b"):
                (root / name / "external-observer-summary.json").write_text(json.dumps(observer([process()])))
            manifest = root / "private-manifest.json"
            manifest.write_text(json.dumps({"source_commit": "PRIVATE_COMMIT", "runs": [
                {"path": "run-a", "observer_path": "observer-a", "timing": "fixed"},
                {"path": "run-a", "observer_path": "observer-a", "timing": "fixed"},
                {"path": "run-b", "observer_summary": "observer-b/external-observer-summary.json", "timing": "contextual"}]}))
            result = export(manifest, root / "public")
            self.assertEqual([run["id"] for run in result["runs"]], ["R001", "R002"])
            self.assertEqual(result["summary"]["duplicate_manifest_paths_excluded"], 1)
            self.assertEqual(result["summary"]["sum_of_per_run_unique_identities"], 2)
            self.assertEqual(result["relationship_totals"][0]["sum_of_per_run_identity_counts"], 2)
            self.assertEqual(result["human_reference_runs"], 0)
            for file in (root / "public").iterdir():
                text = file.read_text(encoding="utf-8")
                for denied in (str(root), "private-source-path-", "PRIVATE_COMMIT", "observer-a", "run-a", "2026-10-16", "10001"):
                    self.assertNotIn(denied, text)
            self.assertIn("same warm process", markdown(result))
            self.assertIn("not a process-start trace", markdown(result))

    def test_missing_observer_and_unrecognized_schema_are_retained_without_claims(self):
        missing = summarize_observer(None, "R001")
        self.assertFalse(missing["observer_present"])
        self.assertEqual(missing["relationships"], [])
        data = observer([process()])
        data["evidence_source"] = "controller-self-report"
        unknown = summarize_observer(data, "R002")
        self.assertFalse(unknown["recognized_schema"])
        self.assertEqual(unknown["unique_observed_identities"], 0)


if __name__ == "__main__":
    unittest.main()
