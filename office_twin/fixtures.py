"""Local task fixtures and independent artifact checks (no desktop automation).

Office documents start empty. The executor must fill them through native input.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
import re
import uuid
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED, BadZipFile


DEFAULT_SCENARIO = {
    "deadline_days": 7,
    "quantity": 5,
    "quotes": [
        {"id": "atlas", "supplier": "Atlas Supplies", "unit_price": 120, "lead_days": 7},
        {"id": "beacon", "supplier": "Beacon Supply", "unit_price": 115, "lead_days": 10},
        {"id": "crest", "supplier": "Crest Industrial", "unit_price": 125, "lead_days": 3},
    ],
}


def validate_scenario(value: dict) -> dict:
    """Validate a deliberately small fixture schema before creating any files.

    This version supports whole SGD prices, positive quantities, and exactly
    three fictional suppliers. It is a recipe input, not web extraction.
    """
    if not isinstance(value, dict) or set(value) != {"deadline_days", "quantity", "quotes"}:
        raise ValueError("Scenario must contain exactly deadline_days, quantity, and quotes.")

    def integer(name: str, number, minimum: int, maximum: int) -> int:
        if type(number) is not int or not minimum <= number <= maximum:
            raise ValueError(f"{name} must be an integer from {minimum} to {maximum}.")
        return number

    deadline = integer("deadline_days", value["deadline_days"], 1, 365)
    quantity = integer("quantity", value["quantity"], 1, 10000)
    if not isinstance(value["quotes"], list) or len(value["quotes"]) != 3:
        raise ValueError("Scenario quotes must be a list of exactly three fictional suppliers.")
    quotes, ids, names = [], set(), set()
    for raw in value["quotes"]:
        if not isinstance(raw, dict) or set(raw) != {"id", "supplier", "unit_price", "lead_days"}:
            raise ValueError("Each quote must contain exactly id, supplier, unit_price, and lead_days.")
        identifier, supplier = raw["id"], raw["supplier"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", identifier):
            raise ValueError("Supplier id must be 1-32 lowercase letters, digits, or hyphens, starting with a letter.")
        if identifier in {"index", "open"} or identifier in ids:
            raise ValueError("Supplier ids must be unique and cannot be 'index' or 'open'.")
        if (not isinstance(supplier, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9 &().'-]{0,59}", supplier)
                or supplier != supplier.strip() or supplier.casefold() in names):
            raise ValueError("Supplier names must be unique, 1-60 safe ASCII characters, and start with a letter.")
        price = integer("unit_price (whole SGD)", raw["unit_price"], 1, 1000000)
        lead_days = integer("lead_days", raw["lead_days"], 0, 3650)
        quotes.append({"id": identifier, "supplier": supplier, "unit_price": price,
                       "quantity": quantity, "lead_days": lead_days, "total": price * quantity})
        ids.add(identifier)
        names.add(supplier.casefold())
    eligible = [q for q in quotes if q["lead_days"] <= deadline]
    # A documented stable tie-breaker makes reordering input inconsequential.
    winner = min(eligible, key=lambda q: (q["total"], q["lead_days"], q["supplier"].casefold())) if eligible else None
    return {"deadline_days": deadline, "quantity": quantity, "quotes": quotes,
            "winner": winner, "decision_rule": "Lowest eligible total; ties use earliest delivery, then supplier name."}


def load_scenario(scenario_path: Path | None = None) -> dict:
    if scenario_path is None:
        return validate_scenario(DEFAULT_SCENARIO)
    path = Path(scenario_path)
    if path.stat().st_size > 100000:
        raise ValueError("Scenario JSON must be smaller than 100 KB.")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Scenario must be valid UTF-8 JSON: {exc}") from exc
    return validate_scenario(value)


def build_report(scenario: dict) -> str:
    deadline, quantity, winner = scenario["deadline_days"], scenario["quantity"], scenario["winner"]
    lines = ["Procurement recommendation", "", f"Buy {quantity} sensor kits; delivery deadline: {deadline} days.", ""]
    for quote in scenario["quotes"]:
        status = "eligible" if quote["lead_days"] <= deadline else "late"
        lines.append(f'{quote["supplier"]}: SGD {quote["total"]} total; {quote["lead_days"]} days; {status}.')
    lines.append("")
    if winner:
        lines.append(f'Recommendation: choose {winner["supplier"]} at SGD {winner["total"]}, the lowest total meeting the deadline.')
    else:
        lines.append(f"Recommendation: no supplier meets the {deadline}-day deadline. Request revised delivery terms before approving a purchase.")
    return "\n".join(lines)


# Backward-compatible default fixture constants. Runtime execution uses its
# prepared bundle so alternate scenarios never silently fall back to these.
_DEFAULT_DERIVED = validate_scenario(DEFAULT_SCENARIO)
QUOTES = tuple(_DEFAULT_DERIVED["quotes"])
REPORT_TEXT = build_report(_DEFAULT_DERIVED)

HEADERS = ("Supplier", "Unit price (SGD)", "Qty", "Lead days", "Total (SGD)", "Meets deadline")
NS_S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _zip(path: Path, members: dict[str, str]) -> None:
    with ZipFile(path, "w", ZIP_DEFLATED) as package:
        for name, content in members.items():
            package.writestr(name, content)


def create_blank_docx(path: Path) -> None:
    """Create a minimal valid blank Word document, never task content."""
    _zip(path, {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        "word/document.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{NS_W}"><w:body><w:p/><w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>',
    })


def create_blank_xlsx(path: Path) -> None:
    """Create a blank workbook. Column widths are presentation only."""
    _zip(path, {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>',
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="{NS_S}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><bookViews><workbookView/></bookViews><sheets><sheet name="Quotes" sheetId="1" r:id="rId1"/></sheets><calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>',
        "xl/_rels/workbook.xml.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>',
        "xl/styles.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><styleSheet xmlns="{NS_S}"><fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>',
        "xl/worksheets/sheet1.xml": f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="{NS_S}"><dimension ref="A1"/><sheetViews><sheetView workbookViewId="0"><selection activeCell="A1" sqref="A1"/></sheetView></sheetViews><sheetFormatPr defaultRowHeight="15"/><cols><col min="1" max="1" width="24" customWidth="1"/><col min="2" max="2" width="20" customWidth="1"/><col min="3" max="4" width="13" customWidth="1"/><col min="5" max="6" width="20" customWidth="1"/></cols><sheetData/></worksheet>',
    })


def _page(title: str, body: str, token: str) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OfficeTwin {token} - {html.escape(title)}</title>
<style>body{{margin:0;background:#eef3f7;color:#182c3b;font:18px/1.6 system-ui,sans-serif}}main{{max-width:900px;margin:45px auto;padding:38px;background:white;border-radius:18px}}h1{{line-height:1.15}}.tag{{font-size:13px;text-transform:uppercase;letter-spacing:.14em;color:#28665e}}table{{border-collapse:collapse;width:100%}}td,th{{text-align:left;padding:14px;border-bottom:1px solid #dce4ea}}a{{color:#07665e}}.note{{background:#eef8f5;padding:18px;border-radius:10px}}footer{{margin-top:70px;color:#5f7281;font-size:14px}}</style></head>
<body><main><div class="tag">OfficeTwin / local synthetic task data</div><h1>{html.escape(title)}</h1>{body}<footer>Fictional supplier information for this local demonstration. No orders are placed.</footer></main></body></html>'''


def prepare_workspace(workspace: Path, workflow: str = "office", scenario_path: Path | None = None) -> dict:
    if workflow not in {"office", "notepad"}:
        raise ValueError("workflow must be 'office' or 'notepad'")
    scenario = load_scenario(scenario_path)
    quotes, quantity, deadline = scenario["quotes"], scenario["quantity"], scenario["deadline_days"]
    report_text = build_report(scenario)
    workspace = Path(workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex[:8]
    site = workspace / f"site-{token}"
    site.mkdir()
    paths = {
        "docx": workspace / f"OfficeTwin-{token}-recommendation.docx",
        "xlsx": workspace / f"OfficeTwin-{token}-quotes.xlsx",
        "txt": workspace / f"OfficeTwin-{token}-recommendation.txt",
        "site": site,
        "scenario": workspace / f"OfficeTwin-{token}-scenario.json",
    }
    create_blank_docx(paths["docx"])
    create_blank_xlsx(paths["xlsx"])
    paths["txt"].write_text("", encoding="utf-8")
    source_snapshot = {"deadline_days": deadline, "quantity": quantity, "quotes": [{key: q[key] for key in ("id", "supplier", "unit_price", "lead_days")} for q in quotes]}
    paths["scenario"].write_text(json.dumps(source_snapshot, indent=2), encoding="utf-8")
    rows = "".join(f'<tr><td><a href="{q["id"]}.html">{html.escape(q["supplier"])}</a></td><td>SGD {q["unit_price"]}</td><td>{q["lead_days"]} days</td></tr>' for q in quotes)
    (site / "index.html").write_text(_page("Supplier comparison", f'<p class="note">Buy {quantity} sensor kits. Choose the lowest total cost from suppliers that can deliver within {deadline} days.</p><p>Review each supplier, record the quotations, and write a short recommendation.</p><table><thead><tr><th>Supplier</th><th>Unit price</th><th>Delivery</th></tr></thead><tbody>{rows}</tbody></table>', token), encoding="utf-8")
    for q in quotes:
        body = f'<p><a href="index.html">Back to comparison</a></p><h2>Sensor kit quotation</h2><p>Unit price: <strong>SGD {q["unit_price"]}</strong></p><p>Quantity requested: <strong>{quantity}</strong></p><p>Delivery lead time: <strong>{q["lead_days"]} days</strong></p><p class="note">Quoted total: SGD {q["total"]}. Prices are fixed for this synthetic exercise.</p><h2>Review notes</h2><p>Compare total price and delivery time. The procurement deadline is {deadline} days.</p>'
        (site / f'{q["id"]}.html').write_text(_page(q["supplier"], body, token), encoding="utf-8")
    steps = [{"id": "browser_open", "label": "Open the local procurement brief", "kind": "browser"}]
    steps += [{"id": f'browser_{q["id"]}', "label": f'Review {q["supplier"]}', "kind": "browser", "supplier": q["id"]} for q in quotes]
    if workflow == "office":
        steps += [
            {"id": "excel_open", "label": "Open the blank quotation workbook", "kind": "switch"},
            {"id": "excel_data", "label": "Enter three supplier quotations", "kind": "typing"},
            {"id": "excel_formulas", "label": "Calculate totals and delivery eligibility", "kind": "typing"},
            {"id": "excel_save", "label": "Save and reopen the workbook", "kind": "review"},
            {"id": "word_open", "label": "Open the blank recommendation document", "kind": "switch"},
            {"id": "word_write", "label": "Write and correct the recommendation", "kind": "typing"},
            {"id": "word_save", "label": "Save and reopen the document", "kind": "review"},
        ]
    else:
        steps += [
            {"id": "notepad_open", "label": "Open the blank text recommendation", "kind": "switch"},
            {"id": "notepad_write", "label": "Write and correct the recommendation", "kind": "typing"},
            {"id": "notepad_save", "label": "Save and reopen the text report", "kind": "review"},
        ]
    expected_cells = {f"{chr(65 + col)}1": header for col, header in enumerate(HEADERS)}
    expected_formulas = {}
    expected_results = {}
    for row, q in enumerate(quotes, start=2):
        for column, value in zip("ABCD", (q["supplier"], q["unit_price"], q["quantity"], q["lead_days"])):
            expected_cells[f"{column}{row}"] = str(value)
        expected_formulas[f"E{row}"] = f"B{row}*C{row}"
        expected_formulas[f"F{row}"] = f'IF(D{row}<={deadline},"YES","NO")'
        expected_results[f"E{row}"] = str(q["total"])
        expected_results[f"F{row}"] = "YES" if q["lead_days"] <= deadline else "NO"
    return {"workspace": workspace, "workflow": workflow, "token": token, "paths": paths, "steps": steps,
            **scenario, "scenario_source": str(Path(scenario_path).resolve()) if scenario_path else "built-in synthetic scenario",
            "task_model": "Recipe-driven synthetic scenario; values come from validated input, not autonomous web extraction.",
            "expected": {"report_text": report_text, "cells": expected_cells, "formulas": expected_formulas, "results": expected_results}}


def read_xlsx(path: Path) -> dict:
    """Read actual saved workbook values, formulas, and Excel cached results."""
    with ZipFile(path) as package:
        strings = []
        if "xl/sharedStrings.xml" in package.namelist():
            root = ET.fromstring(package.read("xl/sharedStrings.xml"))
            strings = ["".join(t.text or "" for t in item.iter(f"{{{NS_S}}}t")) for item in root]
        root = ET.fromstring(package.read("xl/worksheets/sheet1.xml"))
        values, formulas = {}, {}
        for cell in root.iter(f"{{{NS_S}}}c"):
            address = cell.attrib["r"]
            value = cell.find(f"{{{NS_S}}}v")
            text = value.text if value is not None and value.text is not None else ""
            if cell.attrib.get("t") == "s" and text:
                text = strings[int(text)]
            elif cell.attrib.get("t") == "inlineStr":
                text = "".join(t.text or "" for t in cell.iter(f"{{{NS_S}}}t"))
            values[address] = text
            formula = cell.find(f"{{{NS_S}}}f")
            if formula is not None:
                formulas[address] = formula.text or ""
        return {"values": values, "formulas": formulas}


def read_docx(path: Path) -> str:
    with ZipFile(path) as package:
        root = ET.fromstring(package.read("word/document.xml"))
    paragraphs = []
    for paragraph in root.iter(f"{{{NS_W}}}p"):
        text = ""
        for node in paragraph.iter():
            if node.tag == f"{{{NS_W}}}t":
                text += node.text or ""
            elif node.tag == f"{{{NS_W}}}tab":
                text += "\t"
            elif node.tag in {f"{{{NS_W}}}br", f"{{{NS_W}}}cr"}:
                text += "\n"
        paragraphs.append(text)
    return "\n".join(paragraphs).strip()


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def verify_documents(bundle: dict) -> dict:
    """Checks on saved artifacts, separate from the controller action log."""
    checks, errors = {}, []
    paths, expected = bundle["paths"], bundle["expected"]
    if bundle["workflow"] == "notepad":
        try:
            actual = Path(paths["txt"]).read_text(encoding="utf-8-sig")
            checks["text_content"] = _normalize(actual) == _normalize(expected["report_text"])
        except (OSError, UnicodeError) as exc:
            checks["text_content"] = False
            errors.append(str(exc))
    else:
        try:
            actual = read_xlsx(Path(paths["xlsx"]))
            checks["spreadsheet_inputs"] = all(actual["values"].get(cell) == str(value) for cell, value in expected["cells"].items())
            checks["spreadsheet_formulas"] = all(actual["formulas"].get(cell, "").replace(" ", "").upper() == formula.replace(" ", "").upper() for cell, formula in expected["formulas"].items())
            checks["spreadsheet_calculated_results"] = all(actual["values"].get(cell) == value for cell, value in expected["results"].items())
        except (OSError, ValueError, ET.ParseError, KeyError, BadZipFile) as exc:
            checks["spreadsheet_readable"] = False
            errors.append(str(exc))
        try:
            actual_text = read_docx(Path(paths["docx"]))
            checks["document_content"] = _normalize(actual_text) == _normalize(expected["report_text"])
        except (OSError, ValueError, ET.ParseError, KeyError, BadZipFile) as exc:
            checks["document_content"] = False
            errors.append(str(exc))
    return {"passed": bool(checks) and all(checks.values()), "checks": checks, "errors": errors, "workflow": bundle["workflow"], "method": "Independent saved-file read; no reliance on controller action claims"}
