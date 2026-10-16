import tempfile
from pathlib import Path
import unittest

from tools.run_benchmark import code_digest, trial_order, measurement_digest, cleanup_targets, validate_observer


class BenchmarkRunnerTests(unittest.TestCase):
    def test_counterbalance_preserves_paired_seed_and_counts(self):
        order = trial_order([211, 223, 227, 229, 233])
        self.assertEqual(len(order), 10)
        self.assertEqual([mode for _, _, mode in order].count("fixed"), 5)
        self.assertEqual(order[:4], [(1, 211, "fixed"), (1, 211, "contextual"),
                                     (2, 223, "contextual"), (2, 223, "fixed")])

    def test_runtime_digest_detects_changes_and_ignores_docs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "office_twin").mkdir()
            source = root / "office_twin" / "timing.py"
            source.write_text("old", encoding="utf-8")
            original = code_digest(root)
            (root / "README.md").write_text("documentation", encoding="utf-8")
            self.assertEqual(code_digest(root), original)
            source.write_text("new", encoding="utf-8")
            self.assertNotEqual(code_digest(root), original)

    def test_measurement_digest_detects_harness_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "office_twin").mkdir()
            (root / "tools").mkdir()
            source = root / "tools" / "run_benchmark.py"
            source.write_text("old", encoding="utf-8")
            original = measurement_digest(root)
            source.write_text("new", encoding="utf-8")
            self.assertNotEqual(measurement_digest(root), original)

    def test_cleanup_never_selects_sheet_or_other_run(self):
        summary = {"artifacts": {"txt": "OfficeTwin-1234abcd-recommendation.txt"}}
        events = [{"event": "window_focus", "app": app, "title": title, "hwnd": hwnd, "pid": 1}
                  for app, title, hwnd in (("sheets", "Personal Google Sheets", 99),
                                          ("browser", "OfficeTwin 1234abcd - Supplier", 1),
                                          ("explorer", "OfficeTwin-launch-1234abcd", 2),
                                          ("notepad", "OfficeTwin-1234abcd-recommendation.txt", 3))]
        selected = cleanup_targets(summary, events)
        self.assertEqual(set(selected), {"browser", "explorer", "notepad"})
        self.assertNotIn(99, [item["hwnd"] for item in selected.values()])
        events[-1]["title"] = "OfficeTwin-deadbeef-recommendation.txt"
        with self.assertRaisesRegex(RuntimeError, "cleanup token"):
            cleanup_targets(summary, events)

    def test_cleanup_rejects_missing_or_ambiguous_ownership(self):
        with self.assertRaises(RuntimeError):
            cleanup_targets({"artifacts": {"txt": "other.txt"}}, [])
        with self.assertRaises(RuntimeError):
            cleanup_targets({"artifacts": {"txt": "OfficeTwin-1234abcd-recommendation.txt"}}, [])

    def test_observer_must_cover_worker_and_bind_exact_identity(self):
        bound = {"pid": 123, "create_time": 1234.5}
        data = {"status": "completed", "stop_reason": "stop_file", "controller_identity": bound,
                "duration_seconds": 20, "snapshot_count": 100,
                "scopes": {"controller": {"process_count": 1}}}
        validate_observer(data, 0, bound, 19)
        for changed in ({"stop_reason": "duration_limit"}, {"duration_seconds": 18},
                        {"controller_identity": {"pid": 123, "create_time": 1}},
                        {"scopes": {}}, {"status": "failed"}):
            with self.assertRaises(RuntimeError):
                validate_observer({**data, **changed}, 0, bound, 19)
        with self.assertRaises(RuntimeError):
            validate_observer(data, 1, bound, 19)
