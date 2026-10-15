"""Google Sheets workload through the visible Chrome UI, with a Notepad report.

The Drive connector may provision a blank fixture separately. This executor
does not use Google APIs, browser debugging protocols, or hidden DOM writes.
"""
from __future__ import annotations

import csv
import ctypes
import io
import json
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .desktop import DesktopFocusError, DesktopPrerequisiteError, WindowsDesktop
from .fixtures import HEADERS, verify_documents


class GoogleSheetsDesktop(WindowsDesktop):
    """Run against one explicitly supplied, dedicated Google Sheets fixture.

    The fixture must have a selected Quotes tab and a reserved A:F work area.
    Repeated runs replace the active scenario's rows with synthetic task data.
    """

    def __init__(self, workspace: Path, cancel, emit, pause,
                 sheet_url: str, workflow: str | None = None,
                 scenario_path: Path | None = None):
        parsed = urlparse(sheet_url.strip())
        match = re.fullmatch(r"/spreadsheets/d/([A-Za-z0-9_-]+)(?:/edit)?/?", parsed.path)
        if parsed.scheme != "https" or parsed.netloc != "docs.google.com" or not match:
            raise ValueError("Provide the edit URL of a dedicated native Google Sheet.")
        options = {"workflow": "notepad"}
        if scenario_path is not None:
            options["scenario_path"] = scenario_path
        super().__init__(workspace, cancel, emit, pause, **options)
        self.sheet_url = sheet_url.strip()
        self.sheet_id = match.group(1)
        self._configured_gid = self._url_gid(self.sheet_url)
        self._active_gid = None
        self._sheet_marker = ""
        self._sheet_address = None
        self._sheet_readback = None

    def prepare(self) -> dict:
        if self.bundle is not None:
            return self.bundle
        bundle = super().prepare()
        self.workflow = "sheets"
        bundle["workflow"] = "sheets"
        bundle["sheet_url"] = self.sheet_url
        bundle["steps"] = bundle["steps"][:len(bundle["quotes"]) + 1] + [
            {"id": "sheets_open", "label": "Open the dedicated Google Sheet in Chrome", "kind": "switch"},
            {"id": "sheets_data", "label": "Type the supplier quotations into Sheets", "kind": "typing"},
            {"id": "sheets_formulas", "label": "Calculate totals and delivery eligibility in Sheets", "kind": "typing"},
            {"id": "sheets_save", "label": "Confirm cloud save, reload, and read back the grid", "kind": "review"},
            {"id": "notepad_open", "label": "Open the blank text recommendation", "kind": "switch"},
            {"id": "notepad_write", "label": "Write and correct the recommendation", "kind": "typing"},
            {"id": "notepad_save", "label": "Save and reopen the text report", "kind": "review"},
        ]
        self.emit({"event": "sheets_setup", "kind": "setup", "workflow": "sheets",
                   "write_range": f'Quotes!A1:F{len(bundle["quotes"]) + 1}', "runtime_input": "native Chrome keyboard/mouse",
                   "note": "Browser workload, not native Excel process telemetry"})
        return bundle

    def _marker(self, app: str) -> str:
        if app == "sheets":
            return self._sheet_marker
        return super()._marker(app)

    def _is_target_url(self, value: str) -> bool:
        value = value.strip()
        if value.startswith("docs.google.com/"):
            value = "https://" + value
        parsed = urlparse(value)
        correct_file = (parsed.scheme == "https" and parsed.netloc == "docs.google.com"
                        and re.match(rf"^/spreadsheets/d/{re.escape(self.sheet_id)}(?:/|$)", parsed.path) is not None)
        return correct_file and (self._active_gid is None or self._url_gid(value) == self._active_gid)

    @staticmethod
    def _url_gid(value: str) -> str | None:
        parsed = urlparse(value if "://" in value else "https://" + value)
        values = parse_qs(parsed.fragment).get("gid") or parse_qs(parsed.query).get("gid")
        return values[0] if values and re.fullmatch(r"\d+", values[0]) else None

    def _address_control(self, window):
        # Chrome's English UIA omnibox has this accessible name. Fail closed
        # if the browser language or accessibility surface differs.
        controls = window.descendants(control_type="Edit", title="Address and search bar")
        if len(controls) != 1:
            return None
        return controls[0]

    @staticmethod
    def _control_value(control) -> str:
        try:
            return str(control.iface_value.CurrentValue)
        except (AttributeError, RuntimeError):
            return str(control.window_text())

    def _find_window(self, app: str, timeout: float = 35):
        if app != "sheets":
            return super()._find_window(app, timeout)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self._abort_check()
            matches = []
            for window in self._Desktop(backend="uia").windows(visible_only=True):
                try:
                    if self._process_name(window.process_id()) != "chrome.exe":
                        continue
                    title = window.window_text()
                    if "Google Sheets" not in title:
                        continue
                    address = self._address_control(window)
                    if address is not None and self._is_target_url(self._control_value(address)):
                        matches.append((window, address, title))
                except (RuntimeError, AttributeError):
                    continue
            if len(matches) == 1:
                window, address, title = matches[0]
                self._sheet_marker = title
                self._sheet_address = address
                return window
            if len(matches) > 1:
                raise DesktopFocusError("Multiple Chrome windows show the target Sheet. Keep one target window open before retrying.")
            self._sleep(0.15)
        raise DesktopPrerequisiteError(
            "The dedicated Google Sheet is not open and editable in Chrome. Sign in yourself, "
            "open its Quotes tab, and close first-run or account dialogs. The English Chrome "
            "address bar must be available through Windows accessibility."
        )

    def _assert_focus(self) -> None:
        super()._assert_focus()
        if self._app == "sheets":
            try:
                correct = self._sheet_address is not None and self._is_target_url(self._control_value(self._sheet_address))
            except (RuntimeError, AttributeError):
                correct = False
            if not correct:
                raise DesktopFocusError("The active browser URL changed. Sheets input stopped.")

    def _open_sheets(self) -> None:
        try:
            self._find_window("sheets", timeout=0.7)
        except DesktopPrerequisiteError:
            if self._browser_executable is None:
                raise DesktopPrerequisiteError("Open the supplier brief in Chrome before the Sheets step.")
            self._launch_browser_via_explorer(self._browser_executable, self.sheet_url)
        self._focus("sheets")
        self._name_box(timeout=15)
        self._select_quotes_sheet()

    def _select_quotes_sheet(self) -> None:
        """Choose the owned worksheet, then bind subsequent input to its gid."""
        self._assert_focus()
        matches = []
        for control_type in ("Button", "TabItem", "MenuItem"):
            matches.extend(self._window.descendants(control_type=control_type, title="Quotes"))
        if len(matches) != 1:
            raise DesktopPrerequisiteError("Could not locate the Quotes worksheet tab uniquely. No cells were edited.")
        matches[0].click_input()
        self.emit({"event": "input", "kind": "click", "app": "sheets", "action": "Select Quotes worksheet", "native": True})
        self._sleep(0.25)
        current = self._control_value(self._sheet_address)
        gid = self._url_gid(current)
        if gid is None or (self._configured_gid is not None and gid != self._configured_gid):
            raise DesktopPrerequisiteError("The selected Quotes worksheet does not match the supplied sheet URL's gid, or its gid is unavailable. No cells were edited.")
        self._active_gid = gid
        self._assert_focus()
        self.emit({"event": "worksheet_bound", "kind": "setup", "app": "sheets", "sheet": "Quotes", "gid": gid})

    def _name_box(self, timeout: float = 8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self._assert_focus()
            controls = [control for control in self._window.descendants(control_type="Edit")
                        if control.element_info.automation_id == "t-name-box"]
            if len(controls) == 1:
                return controls[0]
            self._sleep(0.15)
        raise DesktopPrerequisiteError(
            "Google Sheets' editable Name box is unavailable. Confirm edit access, the Quotes tab, "
            "and that no dialog is open. No coordinate-only input was attempted."
        )

    def _select_range(self, address: str) -> None:
        self._assert_focus()
        control = self._name_box()
        control.click_input()
        self.emit({"event": "input", "kind": "click", "app": "sheets", "action": "Name box", "native": True})
        self._press("^a", "select Name box contents")
        self._type(address)
        self._press("{ENTER}", f"select {address}")
        self._sleep(0.12)
        selected = self._control_value(self._name_box()).replace("$", "").upper()
        if selected != address.upper():
            raise DesktopFocusError(f"Sheets did not select {address}; current selection is {selected!r}.")

    def _sheets_data(self) -> None:
        self._focus("sheets")
        self._select_range(f'A1:F{len(self.bundle["quotes"]) + 1}')
        self._press("{DELETE}", "clear owned task range before new input")
        self._sleep(0.2)
        self._select_range("A1")
        self._type("\t".join(HEADERS))
        self._press("{ENTER}", "commit headings")
        for row, quote in enumerate(self.bundle["quotes"], 2):
            self._select_range(f"A{row}")
            values = (quote["supplier"], quote["unit_price"], quote["quantity"], quote["lead_days"])
            self._type("\t".join(map(str, values)))
            self._press("{ENTER}", "commit supplier data")
            self._delay("think")

    def _sheets_formulas(self) -> None:
        self._focus("sheets")
        deadline_days = self.bundle.get("deadline_days", 7)
        for row in range(2, len(self.bundle["quotes"]) + 2):
            self._select_range(f"E{row}")
            self._type(f"=B{row}*C{row}")
            # In Sheets, Tab may accept a formula completion without leaving
            # edit mode. Enter commits; select the next cell explicitly.
            self._press("{ENTER}", "commit total formula")
            self._sleep(0.25)
            self._select_range(f"F{row}")
            self._type(f'=IF(D{row}<={deadline_days},"YES","NO")')
            self._press("{ENTER}", "commit eligibility formula")
            self._sleep(0.25)
            self._delay("review")
        self._select_range("A1")

    def _wait_saved(self, timeout: float = 20) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self._assert_focus()
            buttons = self._window.descendants(control_type="Button")
            if any("Saved to Drive" in button.window_text() for button in buttons):
                return
            self._sleep(0.25)
        raise DesktopPrerequisiteError("Google Sheets did not report Saved to Drive. Check the connection and save status before retrying.")

    def _copy_grid(self) -> str:
        import win32clipboard
        import win32con

        self._select_range(f'A1:F{len(self.bundle["quotes"]) + 1}')
        previous = ctypes.windll.user32.GetClipboardSequenceNumber()
        self._press("^c", "copy selected grid for verification")
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            self._assert_focus()
            if ctypes.windll.user32.GetClipboardSequenceNumber() != previous:
                try:
                    win32clipboard.OpenClipboard()
                    try:
                        return win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                    finally:
                        win32clipboard.CloseClipboard()
                except Exception:
                    # The browser may temporarily own the clipboard while it
                    # writes HTML and text representations of the selection.
                    pass
            self._sleep(0.1)
        raise DesktopPrerequisiteError("The selected Sheets grid could not be copied for readback. No cached clipboard data was accepted.")

    def _save_sheets(self) -> None:
        self._focus("sheets")
        self._wait_saved()
        self._press("^r", "reload saved Google Sheet")
        self._sleep(1.0)
        self._focus("sheets")
        self._name_box(timeout=20)
        self._wait_saved()
        text = self._copy_grid()
        rows = list(csv.reader(io.StringIO(text), delimiter="\t"))
        quotes = self.bundle["quotes"]
        deadline_days = self.bundle.get("deadline_days", 7)
        expected = [list(HEADERS)] + [
            [q["supplier"], str(q["unit_price"]), str(q["quantity"]), str(q["lead_days"]),
             str(q["total"]), "YES" if q["lead_days"] <= deadline_days else "NO"] for q in quotes
        ]
        checks = {
            "spreadsheet_headers": bool(rows) and rows[0] == expected[0],
            "spreadsheet_inputs": len(rows) == len(expected) and all(rows[r][:4] == expected[r][:4] for r in range(1, len(expected))),
            "spreadsheet_calculated_results": len(rows) == len(expected) and all(rows[r][4:6] == expected[r][4:6] for r in range(1, len(expected))),
        }
        self._sheet_readback = {"checks": checks, "actual_grid": rows, "saved_to_drive_indicator": True,
                                "method": f"Chrome UI clipboard readback of A1:F{len(expected)} after reload",
                                "formula_source_verified": False,
                                "note": "Checks displayed results, not independent process telemetry or formula source."}
        path = self.workspace / "sheets-readback.json"
        path.write_text(json.dumps(self._sheet_readback, indent=2), encoding="utf-8")
        self.emit({"event": "sheets_readback", "kind": "review", "checks": checks, "path": str(path)})
        self._select_range("A1")
        if not all(checks.values()):
            raise DesktopPrerequisiteError("Saved Sheets values differ from the expected task outputs. Inspect sheets-readback.json; the run is not a success.")

    def run_step(self, step: dict) -> dict:
        actions = {"sheets_open": self._open_sheets, "sheets_data": self._sheets_data,
                   "sheets_formulas": self._sheets_formulas, "sheets_save": self._save_sheets}
        if step["id"] not in actions:
            return super().run_step(step)
        if self.bundle is None:
            raise RuntimeError("Call prepare() before run_step().")
        self._abort_check()
        started = time.monotonic()
        actions[step["id"]]()
        return {"id": step["id"], "passed": True, "duration_s": round(time.monotonic() - started, 3),
                "workflow": "sheets", "execution": "native Chrome UI input"}

    def verify(self) -> dict:
        if self.bundle is None:
            raise RuntimeError("Call prepare() before verify().")
        report = verify_documents({**self.bundle, "workflow": "notepad"})
        checks = dict(report["checks"])
        checks.update((self._sheet_readback or {}).get("checks", {"spreadsheet_readback": False}))
        return {"passed": bool(checks) and all(checks.values()), "checks": checks,
                "errors": report["errors"], "workflow": "sheets",
                "method": "Saved text-file read plus Google Sheets visible-value clipboard readback after reload",
                "limitations": ["Formula source is not independently verified by this runtime check.",
                                "Browser-based Sheets activity is not native Excel process activity."]}
