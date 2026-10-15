import tempfile
import unittest
import json
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from office_twin.fixtures import (
    HEADERS, QUOTES, REPORT_TEXT, NS_S, NS_W, DEFAULT_SCENARIO,
    prepare_workspace, read_docx, read_xlsx, verify_documents, validate_scenario,
)


class FixtureTests(unittest.TestCase):
    @staticmethod
    def _scenario_file(directory, scenario):
        path = Path(directory) / "input-scenario.json"
        path.write_text(json.dumps(scenario), encoding="utf-8")
        return path

    def test_blank_office_files_are_valid_packages_but_not_completed_tasks(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = prepare_workspace(Path(directory))
            for key in ("docx", "xlsx"):
                with ZipFile(bundle["paths"][key]) as package:
                    self.assertIsNone(package.testzip())
                    for name in package.namelist():
                        if name.endswith((".xml", ".rels")):
                            ET.fromstring(package.read(name))
            self.assertEqual(read_docx(bundle["paths"]["docx"]), "")
            self.assertEqual(read_xlsx(bundle["paths"]["xlsx"])["values"], {})
            self.assertFalse(verify_documents(bundle)["passed"])

    def test_supplier_economics_and_local_links_are_consistent(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = prepare_workspace(Path(directory))
            viable = [q for q in QUOTES if q["lead_days"] <= 7]
            winner = min(viable, key=lambda q: q["total"])
            self.assertEqual(winner["id"], "atlas")
            self.assertEqual(winner["total"], 600)
            index = (bundle["paths"]["site"] / "index.html").read_text(encoding="utf-8")
            for quote in QUOTES:
                self.assertEqual(quote["unit_price"] * quote["quantity"], quote["total"])
                self.assertIn(f'{quote["id"]}.html', index)
                self.assertTrue((bundle["paths"]["site"] / f'{quote["id"]}.html').is_file())

    def test_notepad_verification_requires_actual_correct_saved_text(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = prepare_workspace(Path(directory), "notepad")
            self.assertFalse(verify_documents(bundle)["passed"])
            bundle["paths"]["txt"].write_text(REPORT_TEXT, encoding="utf-8-sig")
            self.assertTrue(verify_documents(bundle)["passed"])
            bundle["paths"]["txt"].write_text(REPORT_TEXT.replace("600", "999"), encoding="utf-8")
            self.assertFalse(verify_documents(bundle)["passed"])
            self.assertFalse(any(step["id"].startswith("excel") for step in bundle["steps"]))

    def test_repeated_prepare_does_not_overwrite_existing_run_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            a = prepare_workspace(Path(directory), "notepad")
            a["paths"]["txt"].write_text("preserve", encoding="utf-8")
            b = prepare_workspace(Path(directory), "notepad")
            self.assertNotEqual(a["paths"]["txt"], b["paths"]["txt"])
            self.assertEqual(a["paths"]["txt"].read_text(encoding="utf-8"), "preserve")

    def test_invalid_workflow_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                prepare_workspace(Path(directory), "made-up")

    def test_corrupt_office_artifact_fails_with_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = prepare_workspace(Path(directory))
            bundle["paths"]["xlsx"].write_bytes(b"not a spreadsheet")
            result = verify_documents(bundle)
            self.assertFalse(result["passed"])
            self.assertFalse(result["checks"]["spreadsheet_readable"])
            self.assertTrue(result["errors"])

    def test_changed_price_changes_winner_report_and_expected_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            scenario = deepcopy(DEFAULT_SCENARIO)
            scenario["quotes"][2]["unit_price"] = 100
            path = self._scenario_file(directory, scenario)
            bundle = prepare_workspace(Path(directory) / "run", scenario_path=path)
            self.assertEqual(bundle["winner"]["id"], "crest")
            self.assertIn("Recommendation: choose Crest Industrial at SGD 500", bundle["expected"]["report_text"])
            self.assertEqual(bundle["expected"]["cells"]["B4"], "100")
            self.assertEqual(bundle["expected"]["results"]["E4"], "500")
            self.assertIn("SGD 100", (bundle["paths"]["site"] / "crest.html").read_text(encoding="utf-8"))
            self.assertEqual(json.loads(bundle["paths"]["scenario"].read_text()), scenario)

    def test_reordered_input_has_matching_rows_and_same_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            scenario = deepcopy(DEFAULT_SCENARIO)
            scenario["quotes"].reverse()
            path = self._scenario_file(directory, scenario)
            bundle = prepare_workspace(Path(directory) / "run", scenario_path=path)
            self.assertEqual(bundle["winner"]["id"], "atlas")
            self.assertEqual(bundle["steps"][1]["supplier"], "crest")
            self.assertEqual(bundle["expected"]["cells"]["A2"], "Crest Industrial")
            self.assertEqual(bundle["expected"]["results"]["E2"], "625")
            self.assertEqual(bundle["expected"]["results"]["E4"], "600")

    def test_no_eligible_supplier_produces_explicit_no_purchase_recommendation(self):
        with tempfile.TemporaryDirectory() as directory:
            scenario = deepcopy(DEFAULT_SCENARIO)
            scenario["deadline_days"] = 1
            scenario["quantity"] = 2
            path = self._scenario_file(directory, scenario)
            bundle = prepare_workspace(Path(directory) / "run", "notepad", path)
            self.assertIsNone(bundle["winner"])
            self.assertIn("no supplier meets the 1-day deadline", bundle["expected"]["report_text"])
            self.assertNotIn("Recommendation: choose", bundle["expected"]["report_text"])
            self.assertEqual(bundle["expected"]["results"]["E2"], "240")
            self.assertEqual(bundle["expected"]["formulas"]["F2"], 'IF(D2<=1,"YES","NO")')
            self.assertTrue(all(bundle["expected"]["results"][f"F{row}"] == "NO" for row in (2, 3, 4)))

    def test_invalid_or_unsafe_scenario_is_rejected_before_outputs_exist(self):
        invalid = []
        for key, value in (("quantity", True), ("deadline_days", 0), ("quotes", [])):
            scenario = deepcopy(DEFAULT_SCENARIO)
            scenario[key] = value
            invalid.append(scenario)
        for key, value in (("id", "../escape"), ("id", "index"), ("id", "open"),
                           ("supplier", "=IMPORTXML(unsafe)"), ("supplier", "Bad\nName"),
                           ("unit_price", -1), ("unit_price", 1.25), ("lead_days", False)):
            scenario = deepcopy(DEFAULT_SCENARIO)
            scenario["quotes"][0][key] = value
            invalid.append(scenario)
        duplicate = deepcopy(DEFAULT_SCENARIO)
        duplicate["quotes"][1]["id"] = duplicate["quotes"][0]["id"]
        invalid.append(duplicate)
        for index, scenario in enumerate(invalid):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                path = self._scenario_file(directory, scenario)
                workspace = Path(directory) / "must-not-exist"
                with self.assertRaises(ValueError):
                    prepare_workspace(workspace, scenario_path=path)
                self.assertFalse(workspace.exists())

    def test_equal_prices_choose_earlier_delivery_independent_of_input_order(self):
        scenario = deepcopy(DEFAULT_SCENARIO)
        scenario["quotes"][2]["unit_price"] = 120
        self.assertEqual(validate_scenario(scenario)["winner"]["id"], "crest")
        scenario["quotes"].reverse()
        self.assertEqual(validate_scenario(scenario)["winner"]["id"], "crest")


if __name__ == "__main__":
    unittest.main()
