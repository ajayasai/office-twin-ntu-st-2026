import argparse
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import package_submission as package


class PackageValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for relative in ("office_twin/evidence.py", "office_twin/observer.py", "office_twin/timing.py",
                         "tools/verify_human_timing.py", "tests/test_example.py", "requirements.txt"):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# fixture source\n", encoding="utf-8")
        self.baseline = self.root / "docs/human-baseline/aggregate.json"
        self.write_json(self.baseline, {"participant_measurements": "unchanged"})
        self.validation_dir = self.root / "docs/human-timing"
        self.validation_dir.mkdir(parents=True)
        (self.validation_dir / "tests.log").write_text("fixture tests passed\n", encoding="utf-8")
        self.validation = {
            "passed": True, "tests": 10, "tested_source_commit": "a" * 40,
            "runtime_sha256": package.code_digest(self.root),
            "runtime_digest_algorithm": "fixture digest description",
            "published_log_sha256": package.sha256(self.validation_dir / "tests.log"),
            "source_file_sha256": {
                path.relative_to(self.root).as_posix(): package.sha256(path)
                for path in self.root.rglob("*") if path.is_file()
                and (path.suffix == ".py" or path.name == "requirements.txt")},
        }
        self.write_json(self.validation_dir / "test-provenance.json", self.validation)
        self.integration = {
            "passed": True, "checks": {f"check_{i}": True for i in range(19)},
            "source_commit": "b" * 40, "source_worktree_had_uncommitted_fix": True,
            "source_files_sha256": {name: package.sha256(self.root / name)
                                    for name in package.SAMPLER_SOURCES},
        }
        self.write_json(self.root / package.SAMPLER_PATH, self.integration)
        self.timing_path = self.validation_dir / "verification.json"
        self.timing = {
            "schema_version": 1, "kind": "offline-synthetic-key-timing-verification",
            "passed": True, "checks": {"fit": True},
            "source_files_sha256": {name: package.sha256(self.root / name)
                                    for name in ("office_twin/timing.py", "tools/verify_human_timing.py")},
            "reference": {"path": "docs/human-baseline/aggregate.json", "sha256": package.sha256(self.baseline)},
            "claims": {"synthetic_samples": True, "new_human_run": False,
                       "native_input_observed": False, "elapsed_task_duration_validated": False,
                       "human_distribution_tested": False, "official_score_claimed": False},
        }
        self.write_json(self.timing_path, self.timing)

    @staticmethod
    def write_json(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_selected_validation_is_separate_from_historical_sampler(self):
        current = package.current_validation(self.root, self.validation_dir)
        sampler = package.historical_sampler_validation(self.root)
        self.assertEqual(current["test_provenance_path"], "docs/human-timing/test-provenance.json")
        self.assertNotIn("integration_evidence_sha256", current)
        self.assertEqual(sampler["check_count"], 19)
        self.assertEqual(sampler["source_commit"], "b" * 40)
        self.assertFalse(sampler["probe_rerun"])

    def test_changed_runtime_or_test_log_is_rejected(self):
        (self.root / "office_twin/timing.py").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "runtime"):
            package.current_validation(self.root, self.validation_dir)
        (self.root / "office_twin/timing.py").write_text("# fixture source\n", encoding="utf-8")
        (self.validation_dir / "tests.log").write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "test log"):
            package.current_validation(self.root, self.validation_dir)

    def test_changed_tool_and_new_unrecorded_source_are_rejected(self):
        path = self.root / "tools/verify_human_timing.py"
        path.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Tested source mismatch"):
            package.current_validation(self.root, self.validation_dir)
        path.write_text("# fixture source\n", encoding="utf-8")
        (self.root / "tools/new_tool.py").write_text("new", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "omits required"):
            package.current_validation(self.root, self.validation_dir)

    def test_historical_sampler_rejects_changed_module_or_failed_check(self):
        path = self.root / "office_twin/evidence.py"
        path.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Historical sampler source mismatch"):
            package.historical_sampler_validation(self.root)
        path.write_text("# fixture source\n", encoding="utf-8")
        self.integration["checks"]["check_0"] = False
        self.write_json(self.root / package.SAMPLER_PATH, self.integration)
        with self.assertRaisesRegex(RuntimeError, "every recorded check"):
            package.historical_sampler_validation(self.root)

    def test_timing_verification_binds_baseline_and_sources(self):
        result = package.timing_validation(self.root, self.timing_path)
        self.assertEqual(result["baseline_sha256"], package.sha256(self.baseline))
        self.assertFalse(result["human_run"])
        self.assertFalse(result["input_delivery_validated"])
        self.baseline.write_text("changed aggregates", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "baseline hash"):
            package.timing_validation(self.root, self.timing_path)

    def test_timing_verification_rejects_failed_or_contradictory_claims(self):
        for mutation in (lambda: self.timing.update(passed=False),
                         lambda: self.timing["checks"].update(fit=False),
                         lambda: self.timing["claims"].update(native_input_observed=True)):
            mutation()
            self.write_json(self.timing_path, self.timing)
            with self.assertRaises(RuntimeError):
                package.timing_validation(self.root, self.timing_path)
            self.timing["passed"] = True
            self.timing["checks"]["fit"] = True
            self.timing["claims"]["native_input_observed"] = False

    def test_timing_verification_rejects_stale_or_missing_verifier_source(self):
        name = "tools/verify_human_timing.py"
        (self.root / name).write_text("new verifier", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Timing verification source mismatch"):
            package.timing_validation(self.root, self.timing_path)
        del self.timing["source_files_sha256"][name]
        self.write_json(self.timing_path, self.timing)
        with self.assertRaisesRegex(RuntimeError, "omits required"):
            package.timing_validation(self.root, self.timing_path)

    def test_private_or_external_evidence_is_rejected(self):
        private_path = self.root / "runs/verification.json"
        self.write_json(private_path, self.timing)
        with self.assertRaisesRegex(RuntimeError, "included in the source archive"):
            package.timing_validation(self.root, private_path)
        with self.assertRaisesRegex(RuntimeError, "repository file"):
            package.repository_path(self.root, self.root.parent / "outside.json")

    def test_manifest_separates_all_three_validation_scopes(self):
        args = argparse.Namespace(validation_dir=self.validation_dir, timing_verification=self.timing_path,
                                  video_scope="historical recording", video_url="https://example.test/video")
        def fake_git(command, **kwargs):
            if command[1] == "rev-parse":
                return "c" * 40
            if command[1] == "status":
                return ""
            return b"# old runtime\n"
        with patch.object(package.subprocess, "check_output", side_effect=fake_git):
            manifest = package.build_manifest(self.root, args)
        self.assertEqual(manifest["manifest_schema_version"], 3)
        self.assertEqual(manifest["current_software_validation"]["test_count"], 10)
        self.assertEqual(manifest["historical_sampler_verification"]["check_count"], 19)
        self.assertTrue(manifest["timing_model_verification"]["passed"])
        self.assertFalse(manifest["historical_native_benchmark"]["applies_to_packaged_runtime"])
        args.timing_verification = None
        with patch.object(package.subprocess, "check_output", side_effect=fake_git):
            self.assertNotIn("timing_model_verification", package.build_manifest(self.root, args))

    def test_failed_validation_does_not_overwrite_existing_archive(self):
        output = self.root / "output"
        output.mkdir()
        archive = output / "office-twin-source.zip"
        archive.write_bytes(b"preserve prior archive")
        with patch.object(package, "build_manifest", side_effect=RuntimeError("stale proof")):
            with self.assertRaisesRegex(RuntimeError, "stale proof"):
                package.main(["--output-dir", str(output)])
        self.assertEqual(archive.read_bytes(), b"preserve prior archive")


if __name__ == "__main__":
    unittest.main()
