import unittest

from office_twin.timing import PROFILES, TimingPolicy


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


if __name__ == "__main__":
    unittest.main()
