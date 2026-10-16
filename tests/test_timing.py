import unittest
import hashlib
import json
from pathlib import Path

from office_twin.timing import (PROFILES, TimingPolicy, HUMAN_BASELINE_PATH,
                              HUMAN_BASELINE_SHA256, HUMAN_KEY_BOUNDS)


class TimingPolicyTests(unittest.TestCase):
    def test_seed_reproduces_the_sequence_without_collapsing_variation(self):
        sequence = ["key", "read", "key", "think", "switch", "review", "correction"] * 20
        first, second, different = TimingPolicy(seed=7), TimingPolicy(seed=7), TimingPolicy(seed=8)
        a = [first.sample(kind) for kind in sequence]
        self.assertEqual(a, [second.sample(kind) for kind in sequence])
        self.assertNotEqual(a, [different.sample(kind) for kind in sequence])
        self.assertGreater(len(set(a)), 100)

    def test_bounded_samples_and_unit_scaling(self):
        policy = TimingPolicy(seed=913, scale=0.4)
        for kind, (minimum, nominal, maximum) in PROFILES.items():
            for units in (1, 3, 20):
                for _ in range(30):
                    sample = policy.sample(kind, units)
                    self.assertGreaterEqual(sample + 1e-12, minimum * units * 0.4)
                    self.assertLessEqual(sample, maximum * units * 0.4 + 1e-12)
            self.assertEqual(TimingPolicy("fixed", scale=0.4).sample(kind, 3), nominal * 3 * 0.4)

    def test_scale_changes_only_duration(self):
        full, scaled = TimingPolicy(seed=23), TimingPolicy(seed=23, scale=0.1)
        for kind in PROFILES:
            self.assertAlmostEqual(full.sample(kind) * 0.1, scaled.sample(kind))
        self.assertEqual(TimingPolicy(scale=0).sample("key"), 0)
        self.assertTrue(TimingPolicy(scale=0).metadata()["delays_disabled"])

    def test_invalid_values_are_rejected(self):
        for arguments in ({"mode": "invented"}, {"scale": -1}, {"scale": float("nan")}, {"scale": float("inf")}, {"seed": True}):
            with self.assertRaises(ValueError):
                TimingPolicy(**arguments)
        for units in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                TimingPolicy().sample("key", units)
        with self.assertRaises(ValueError):
            TimingPolicy().sample("unknown")

    def test_metadata_does_not_invent_calibration(self):
        policy = TimingPolicy()
        policy.sample("review")
        self.assertEqual(policy.metadata()["sample_count"], 1)
        self.assertIn("Uncalibrated", policy.metadata()["calibration"])

    def test_legacy_seed_sequence_is_unchanged(self):
        # Frozen before adding the optional profile; benchmark seeds must not
        # acquire different legacy behavior as new policy modes are introduced.
        policy = TimingPolicy(seed=7)
        expected = [0.10133499371999974, 0.7384106002500818,
                    0.09137748004761831, 0.8012910464528201,
                    0.5113523500584736, 1.9990158157496654,
                    0.17862896961429325, 0.07042531504026603]
        kinds = ["key", "read", "key", "think", "switch", "review", "correction", "key"]
        self.assertEqual(expected, [policy.sample(kind) for kind in kinds])

    def test_human_targets_match_preserved_participant_data(self):
        path = Path(__file__).resolve().parents[1] / HUMAN_BASELINE_PATH
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), HUMAN_BASELINE_SHA256)
        measured = json.loads(path.read_text(encoding="utf-8"))["measured_results_participant_reported"]
        fit = TimingPolicy("human-informed").metadata()["reference_fit"]
        for field, key in (("fitted_median_seconds", "median"), ("fitted_p90_seconds", "p90"), ("reference_mean_seconds", "mean")):
            self.assertEqual(fit[field] * 1000, measured[f"{key}_inter_key_interval_milliseconds"])
        self.assertFalse(fit["native_input_intervals_verified"])
        self.assertFalse(fit["human_indistinguishability_verified"])
        self.assertIn("key holds", fit["not_fitted"])

    def test_human_key_stream_is_reproducible_and_not_changed_by_interleaving(self):
        plain, mixed = TimingPolicy("human-informed", seed=23), TimingPolicy("human-informed", seed=23)
        a, b = [], []
        for _ in range(200):
            a.append(plain.sample("key"))
            mixed.sample("read")
            mixed.sample("review")
            b.append(mixed.sample("key"))
        self.assertEqual(a, b)
        self.assertGreater(len(set(a)), 190)
        other = TimingPolicy("human-informed", seed=24)
        self.assertNotEqual(a, [other.sample("key") for _ in a])

    def test_human_bounds_units_scaling_and_nonkey_defaults(self):
        single, grouped = TimingPolicy("human-informed", seed=17), TimingPolicy("human-informed", seed=17)
        self.assertEqual(sum(single.sample("key") for _ in range(30)), grouped.sample("key", 30))
        full, scaled = TimingPolicy("human-informed", seed=18), TimingPolicy("human-informed", seed=18, scale=0.25)
        for _ in range(1000):
            seconds = full.sample("key")
            self.assertTrue(HUMAN_KEY_BOUNDS[0] <= seconds <= HUMAN_KEY_BOUNDS[1])
            self.assertEqual(seconds * 0.25, scaled.sample("key"))
        self.assertFalse(scaled.metadata()["reference_fit"]["scale_one_targets_active"])
        legacy, informed = TimingPolicy(seed=10), TimingPolicy("human-informed", seed=10)
        for kind in [k for k in PROFILES if k != "key"] * 10:
            self.assertEqual(legacy.sample(kind), informed.sample(kind))
        zero = TimingPolicy("human-informed", scale=0)
        self.assertEqual(zero.sample("key"), 0)
        self.assertTrue(zero.metadata()["delays_disabled"])


if __name__ == "__main__":
    unittest.main()
