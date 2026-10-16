import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from office_twin.timing import TimingPolicy
from tools import verify_human_timing as verifier


class HumanTimingVerificationTests(unittest.TestCase):
    def sample_summary(self, mean=.2, median=.17, p90=.35):
        return {"count": 11, "mean": mean, "median": median, "p90": p90,
                "minimum": .1, "maximum": .44, "all_samples_within_bounds": True}

    def test_quantile_estimator_is_explicit_linear_interpolation(self):
        result = verifier.summarize_samples([.4, .1, .3, .2], (.005, 2.0))
        self.assertAlmostEqual(result["mean"], .25)
        self.assertAlmostEqual(result["median"], .25)
        self.assertAlmostEqual(result["p90"], .37)
        self.assertEqual(verifier.quantile_sorted([.17], .9), .17)
        self.assertEqual(verifier.quantile_sorted([.1, .3], 0), .1)
        self.assertEqual(verifier.quantile_sorted([.1, .3], 1), .3)
        with self.assertRaises(ValueError):
            verifier.quantile_sorted([], .9)

    def test_nonfinite_or_nonpositive_samples_are_rejected_not_silently_dropped(self):
        for values in ([], [True], [0], [-.1], [float("nan")], [float("inf")], ["0.2"]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                verifier.summarize_samples(values, (.005, 2))
        result = verifier.summarize_samples([.005, .17, 2], (.005, 2))
        self.assertEqual(result["bound_hit_counts"], {"lower": 1, "upper": 1})
        self.assertTrue(result["all_samples_within_bounds"])
        self.assertFalse(verifier.summarize_samples([2.1], (.005, 2))["all_samples_within_bounds"])
        self.assertIn("raw unclipped draws", result["bound_hit_definition"])

    def test_reference_load_checks_exact_retained_bytes_and_target_units(self):
        reference = verifier.load_reference()
        self.assertEqual(reference["sha256"], verifier.REFERENCE_SHA256)
        self.assertEqual(reference["targets_seconds"], {"mean": .2, "median": .17, "p90": .35})
        self.assertFalse(reference["independently_verified"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aggregate.json"
            path.write_bytes((verifier.ROOT / verifier.REFERENCE_PATH).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                verifier.load_reference(path)

    def test_changed_targets_or_human_provenance_fail_even_if_hash_is_updated(self):
        original = json.loads((verifier.ROOT / verifier.REFERENCE_PATH).read_text())
        changed_target, changed_provenance = deepcopy(original), deepcopy(original)
        changed_target["measured_results_participant_reported"]["median_inter_key_interval_milliseconds"] = 190
        changed_provenance["provenance"]["without_guidance_confirmed_by_participant"] = False
        for changed in (changed_target, changed_provenance):
            with self.subTest(changed=changed is changed_target), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "aggregate.json"
                raw = json.dumps(changed).encode()
                path.write_bytes(raw)
                with patch.object(verifier, "REFERENCE_SHA256", hashlib.sha256(raw).hexdigest()), self.assertRaises(ValueError):
                    verifier.load_reference(path)

    def test_every_metric_must_pass_threshold_and_strict_improvement(self):
        legacy = self.sample_summary(.11, .10, .17)
        current = self.sample_summary()
        result = verifier.compare_seed(211, {"contextual": legacy, "human-informed": current}, verifier.TARGETS)
        self.assertTrue(result["passed"])
        current["p90"] = .37
        result = verifier.compare_seed(211, {"contextual": legacy, "human-informed": current}, verifier.TARGETS)
        self.assertFalse(result["passed"])
        self.assertFalse(result["metric_checks"]["p90"]["human_informed_within_3_percent"])
        # A target-matching legacy metric cannot be called an improvement.
        current = self.sample_summary(mean=.201)
        legacy["mean"] = .2
        result = verifier.compare_seed(211, {"contextual": legacy, "human-informed": current}, verifier.TARGETS)
        self.assertFalse(result["passed"])
        self.assertFalse(result["metric_checks"]["mean"]["human_informed_closer_than_contextual"])

    def test_sampling_uses_only_public_sample_api_at_unit_scale(self):
        values = [.1, .1, .1, .1, .1, .17, .2, .24, .3, .35, .44]
        policy = Mock()
        policy.sample.side_effect = values
        policy.metadata.return_value = {"mode": "human-informed"}
        with patch.object(verifier, "TimingPolicy", return_value=policy) as constructor:
            summary, metadata = verifier.sample_policy("human-informed", 223, len(values))
        constructor.assert_called_once_with(mode="human-informed", seed=223, scale=1.0)
        self.assertTrue(all(call.args == ("key", 1) for call in policy.sample.call_args_list))
        self.assertEqual(policy.sample.call_count, 11)
        self.assertAlmostEqual(summary["mean"], .2)
        self.assertEqual(summary["median"], .17)
        self.assertEqual(summary["p90"], .35)
        self.assertEqual(metadata["mode"], "human-informed")

    def test_model_metadata_cannot_claim_native_or_human_validation(self):
        reference = verifier.load_reference()
        metadata = TimingPolicy(mode="human-informed", seed=211).metadata()
        self.assertTrue(verifier.metadata_reference_matches(metadata, reference))
        for field, wrong in (("source_sha256", "f" * 64),
                             ("native_input_intervals_verified", True),
                             ("human_indistinguishability_verified", True),
                             ("scale_one_targets_active", False)):
            changed = deepcopy(metadata)
            changed["reference_fit"][field] = wrong
            self.assertFalse(verifier.metadata_reference_matches(changed, reference))

    def test_report_scope_and_predeclared_protocol_remain_explicit(self):
        def fake_sample(mode, seed, count):
            summary = self.sample_summary() if mode == "human-informed" else self.sample_summary(.11, .10, .17)
            summary["count"] = count
            return summary, TimingPolicy(mode=mode, seed=seed).metadata()
        with patch.object(verifier, "sample_policy", side_effect=fake_sample):
            result = verifier.verify()
        self.assertTrue(result["passed"])
        self.assertEqual(result["protocol"]["seeds"], [211, 223, 227, 229, 233])
        self.assertEqual(result["protocol"]["samples_per_seed_per_mode"], 100000)
        self.assertEqual(result["protocol"]["total_generated_key_delay_samples"], 1000000)
        self.assertEqual(len(result["per_seed_results"]), 5)
        self.assertTrue(result["claims"]["synthetic_samples"])
        self.assertTrue(all(value is False for key, value in result["claims"].items() if key != "synthetic_samples"))
        self.assertFalse(result["protocol"]["actual_sleep_or_input_delivery_performed"])
        self.assertEqual(set(result["source_files_sha256"]), {"office_twin/timing.py", "tools/verify_human_timing.py"})
        self.assertIn("720-second task and 180-second typing window", " ".join(result["limitations"]))
        self.assertIn("not a confidence interval", " ".join(result["limitations"]))

    def test_report_fails_closed_when_model_scope_is_misreported(self):
        def fake_sample(mode, seed, count):
            metadata = TimingPolicy(mode=mode, seed=seed).metadata()
            if mode == "human-informed":
                metadata["reference_fit"]["native_input_intervals_verified"] = True
            summary = self.sample_summary() if mode == "human-informed" else self.sample_summary(.11, .10, .17)
            return summary, metadata
        with patch.object(verifier, "sample_policy", side_effect=fake_sample):
            result = verifier.verify()
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["model_metadata_matches_reference_and_scope"])

    def test_export_preserves_existing_reports_and_failure_exit_is_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with patch.object(verifier, "verify", return_value={"passed": False}), patch("builtins.print"):
                self.assertEqual(verifier.main(["--output-dir", str(output)]), 1)
            saved = output / "timing-verification.json"
            original = saved.read_bytes()
            with self.assertRaises(FileExistsError):
                verifier.export({"passed": True}, output)
            self.assertEqual(saved.read_bytes(), original)

    def test_tool_has_no_native_input_network_recorder_or_sleep_dependency(self):
        tree = ast.parse(Path(verifier.__file__).read_text())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, {"sleep", "send_keys", "Popen", "click", "terminate", "start", "wait"})
        self.assertEqual(imports, {"__future__", "argparse", "datetime", "hashlib", "json", "math",
                                  "pathlib", "platform", "statistics", "sys", "office_twin.timing"})


if __name__ == "__main__":
    unittest.main()

