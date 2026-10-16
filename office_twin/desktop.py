"""Native visible Windows execution; never writes completed Office artifacts.

The desktop remains a single-user surface. Any unexpected foreground window,
Escape press, or cancellation stops input. Office activation is a prerequisite.
"""
from __future__ import annotations

import ctypes
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import threading
import time
from typing import Callable

from .fixtures import HEADERS, prepare_workspace, verify_documents


class DesktopPrerequisiteError(RuntimeError):
    pass


class DesktopCancelled(RuntimeError):
    pass


class DesktopFocusError(RuntimeError):
    pass


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        pass


class WindowsDesktop:
    def __init__(self, workspace: Path, cancel: threading.Event,
                 emit: Callable[[dict], None], pause: Callable[[str, int], None],
                 workflow: str = "office", scenario_path: Path | None = None):
        self.workspace = Path(workspace)
        self.cancel = cancel
        self.emit = emit
        self.pause = pause
        self.workflow = workflow
        self.scenario_path = Path(scenario_path) if scenario_path else None
        self.bundle: dict | None = None
        self.server: ThreadingHTTPServer | None = None
        self.server_thread: threading.Thread | None = None
        self._window = None
        self._app = None
        self._Desktop = None
        self._send_keys = None
        self._psutil = None
        self._browser_executable = None

    def prepare(self) -> dict:
        if self.bundle is not None:
            return self.bundle
        if os.name != "nt":
            raise DesktopPrerequisiteError("Native execution requires Windows and an unlocked interactive desktop.")
        try:
            from pywinauto import Desktop, keyboard
            import psutil
        except ImportError as exc:
            raise DesktopPrerequisiteError("Install requirements.txt in this Python environment before native execution.") from exc
        self._Desktop = Desktop
        self._send_keys = keyboard.send_keys
        self._psutil = psutil
        self.bundle = prepare_workspace(self.workspace, self.workflow, self.scenario_path)
        handler = partial(_QuietHandler, directory=str(self.bundle["paths"]["site"]))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.server.daemon_threads = True
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True, name="OfficeTwin-fixtures")
        self.server_thread.start()
        self.bundle["base_url"] = f"http://127.0.0.1:{self.server.server_port}"
        self.emit({"event": "fixture_server", "kind": "setup", "base_url": self.bundle["base_url"], "scope": "loopback-only", "workflow": self.workflow})
        return self.bundle

    def close(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        if self.server_thread:
            self.server_thread.join(timeout=2)
            self.server_thread = None

    def _abort_check(self) -> None:
        if self.cancel.is_set():
            raise DesktopCancelled("Run cancelled; native input stopped.")
        if os.name == "nt" and ctypes.windll.user32.GetAsyncKeyState(0x1B) & 0x8000:
            self.cancel.set()
            raise DesktopCancelled("Escape pressed; native input stopped.")

    def _sleep(self, seconds: float) -> None:
        until = time.monotonic() + seconds
        while time.monotonic() < until:
            self._abort_check()
            self.cancel.wait(min(0.05, max(0, until - time.monotonic())))

    def _delay(self, kind: str, units: int = 1) -> None:
        self._abort_check()
        self.pause(kind, units)
        self._abort_check()

    def _process_name(self, pid: int) -> str:
        try:
            return self._psutil.Process(pid).name().lower()
        except (self._psutil.NoSuchProcess, self._psutil.AccessDenied):
            return ""

    def _office_gate(self, app: str) -> None:
        if app not in {"word", "excel"}:
            return
        process_names = {"word": {"winword.exe"}, "excel": {"excel.exe"}}[app]
        phrases = ("sign in to set up office", "sign in to get started", "activate office",
                   "product activation", "unlicensed product", "enter your product key",
                   "your account doesn't allow editing", "your account doesn’t allow editing")
        for window in self._Desktop(backend="uia").windows(visible_only=True):
            self._abort_check()
            try:
                if self._process_name(window.process_id()) not in process_names:
                    continue
                title = window.window_text().lower()
                texts = [title]
                texts.extend(control.window_text().lower() for control in window.descendants(control_type="Text"))
                blocked = title.strip() in {"sign in", "sign in to your account", "activation"}
                if blocked or any(phrase in text for text in texts for phrase in phrases):
                    raise DesktopPrerequisiteError(
                        f"{app.title()} requires Office sign-in or activation. Complete it yourself in Office, "
                        "then start a fresh native run. No input was sent to the sign-in screen. "
                        "The notepad workflow is available as a reduced-scope fallback."
                    )
            except DesktopPrerequisiteError:
                raise
            except (RuntimeError, AttributeError, self._psutil.Error):
                continue

    def _marker(self, app: str) -> str:
        if app == "browser":
            return f'OfficeTwin {self.bundle["token"]}'
        if app == "explorer":
            return self.bundle["paths"]["launch"].name
        key = {"excel": "xlsx", "word": "docx", "notepad": "txt"}[app]
        return self.bundle["paths"][key].stem

    def _find_window(self, app: str, timeout: float = 35):
        marker = self._marker(app).lower()
        names = {"excel": {"excel.exe"}, "word": {"winword.exe"},
                 "notepad": {"notepad.exe"}, "browser": {"msedge.exe", "chrome.exe", "firefox.exe"},
                 "explorer": {"explorer.exe"}}[app]
        deadline = time.monotonic() + timeout
        gate_at = 0.0
        while time.monotonic() < deadline:
            self._abort_check()
            if time.monotonic() >= gate_at:
                self._office_gate(app)
                gate_at = time.monotonic() + 2
            matches = []
            for window in self._Desktop(backend="uia").windows(visible_only=True):
                try:
                    if marker in window.window_text().lower() and self._process_name(window.process_id()) in names:
                        matches.append(window)
                except (RuntimeError, AttributeError):
                    continue
            if len(matches) == 1:
                return matches[0]
            if len(matches) > 1:
                raise DesktopFocusError(f"Multiple {app} windows match this run's unique filename; close the duplicate before retrying.")
            self._sleep(0.15)
        raise DesktopPrerequisiteError(
            f"Could not find the {app} window for this run within {timeout:g} seconds. "
            "Check that the application is installed, usable, and has no first-run, sign-in, or recovery dialog."
        )

    def _focus(self, app: str) -> None:
        self._abort_check()
        self._office_gate(app)
        window = self._find_window(app)
        self._window = window
        self._app = app
        window.maximize()
        window.set_focus()
        self._sleep(0.2)
        self._assert_focus()
        self.emit({"event": "window_focus", "kind": "switch", "app": app, "pid": window.process_id(), "hwnd": window.handle, "title": window.window_text()})
        self._delay("switch")

    def _assert_focus(self) -> None:
        self._abort_check()
        if self._window is None:
            raise DesktopFocusError("No intended window has been selected.")
        actual = ctypes.windll.user32.GetForegroundWindow()
        expected = int(self._window.handle)
        # No arbitrary same-process dialog is accepted: input stays in the
        # exact top-level window that was located by the unique run filename.
        if actual != expected:
            raise DesktopFocusError("Foreground focus changed. Input stopped to avoid typing into another window. Start a fresh run when the desktop is ready.")
        if self._marker(self._app).lower() not in self._window.window_text().lower():
            raise DesktopFocusError("The active document or tab changed. Input stopped.")
        if not self._window.is_enabled():
            raise DesktopPrerequisiteError("The intended application is blocked by a dialog. No input was sent to that dialog.")

    def _press(self, keys: str, label: str | None = None) -> None:
        self._assert_focus()
        self._send_keys(keys, pause=0, with_spaces=True, vk_packet=True)
        self.emit({"event": "input", "kind": "key", "app": self._app, "action": label or keys, "native": True})
        self._abort_check()

    def _type(self, text: str) -> None:
        escape = {"+": "{+}", "^": "{^}", "%": "{%}", "~": "{~}", "(": "{(}", ")": "{)}", "{": "{{}", "}": "{}}"}
        for char in text:
            self._delay("key")
            if char == "\n":
                self._press("{ENTER}", "enter")
            elif char == "\t":
                self._press("{TAB}", "tab")
            else:
                self._press(escape.get(char, char), "character")

    def _launch_file(self, app: str, key: str) -> None:
        self._abort_check()
        self._office_gate(app)
        path = self.bundle["paths"][key]
        if app == "notepad":
            self._launch_report_via_explorer(Path(path))
        else:
            self.emit({"event": "launch", "kind": "switch", "app": app, "path": str(path), "mechanism": "os.startfile / Windows ShellExecute file association"})
            os.startfile(str(path))
        self._focus(app)

    def _launch_report_via_explorer(self, path: Path) -> None:
        """Open this run's text file by an ordinary visible Explorer action."""
        self._abort_check()
        path = path.resolve()
        expected = self.workspace.resolve() / f'OfficeTwin-{self.bundle["token"]}-recommendation.txt'
        if path != expected or not path.is_file():
            raise DesktopPrerequisiteError("Only this run's existing recommendation file may be opened through its report shortcut.")
        launch_dir = self.workspace.resolve() / f'OfficeTwin-launch-{self.bundle["token"]}'
        launch_dir.mkdir(exist_ok=True)
        self.bundle["paths"]["launch"] = launch_dir
        shortcut_name = f'Open OfficeTwin report {self.bundle["token"]}'
        shortcut_path = launch_dir / f"{shortcut_name}.lnk"
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(str(shortcut_path))
            shortcut.TargetPath = str(path)
            shortcut.Arguments = ""
            shortcut.WorkingDirectory = str(path.parent)
            shortcut.Description = "Open this run's saved text recommendation through its Windows file association"
            shortcut.Save()
        except Exception as exc:
            raise DesktopPrerequisiteError(f"Could not create the run-local report shortcut: {exc}") from exc
        # Reuse the unique launch folder left open by the supplier browser step.
        # Open it only if absent; ambiguity is an error, never another window.
        try:
            self._find_window("explorer", timeout=0.7)
        except DesktopPrerequisiteError:
            self.emit({"event": "launch_folder", "kind": "switch", "app": "explorer", "path": str(launch_dir),
                       "mechanism": "os.startfile / Windows ShellExecute folder association"})
            os.startfile(str(launch_dir))
        self._focus("explorer")
        matches = []
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            self._assert_focus()
            for control_type in ("ListItem", "DataItem"):
                matches = [item for item in self._window.descendants(control_type=control_type)
                           if item.window_text().lower() in {shortcut_name.lower(), shortcut_path.name.lower()}]
                if len(matches) == 1:
                    break
            if len(matches) == 1:
                break
            self._sleep(0.15)
        if len(matches) != 1:
            raise DesktopPrerequisiteError("The run-local report shortcut could not be located uniquely in Explorer. No direct-file or direct-process fallback was attempted.")
        self._assert_focus()
        matches[0].double_click_input()
        self.emit({"event": "input", "kind": "click", "app": "explorer", "action": "Double-click the run-local report shortcut", "native": True})
        self.emit({"event": "launch", "kind": "switch", "app": "notepad", "path": str(path), "shortcut": str(shortcut_path),
                   "mechanism": "Visible Explorer double-click on run-local .lnk targeting the exact text report",
                   "parent_note": "Ordinary shell interaction; Windows file association and application reuse determine actual ancestry. Verify it with independent telemetry."})

    def _launch_browser(self) -> None:
        self._abort_check()
        candidates = [
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", "C:/missing")) / "Google/Chrome/Application/chrome.exe",
        ]
        executable = next((path for path in candidates if path.is_file()), None)
        if executable is None:
            raise DesktopPrerequisiteError("Google Chrome was not found in its usual Windows installation locations.")
        self._browser_executable = executable
        url = self.bundle["base_url"] + "/index.html"
        self._launch_browser_via_explorer(executable, url)
        self._focus("browser")
        self._delay("read", 3)

    def _launch_browser_via_explorer(self, executable: Path, url: str) -> None:
        """Open Chrome through an ordinary visible Explorer shortcut action.

        A running Chrome instance may reuse its existing process. The action log
        states the launch mechanism; independent telemetry must establish ancestry.
        """
        self._abort_check()
        launch_dir = self.workspace.resolve() / f'OfficeTwin-launch-{self.bundle["token"]}'
        launch_dir.mkdir(exist_ok=True)
        self.bundle["paths"]["launch"] = launch_dir
        shortcut_name = f'Launch OfficeTwin {self.bundle["token"]}'
        shortcut_path = launch_dir / f"{shortcut_name}.lnk"
        try:
            import win32com.client
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(str(shortcut_path))
            shortcut.TargetPath = str(executable)
            shortcut.Arguments = f'--new-window "{url}"'
            shortcut.WorkingDirectory = str(executable.parent)
            shortcut.Description = "Open this run's local OfficeTwin supplier comparison in Google Chrome"
            shortcut.Save()
        except Exception as exc:
            raise DesktopPrerequisiteError(f"Could not create the run-local Chrome shortcut: {exc}") from exc
        self.emit({"event": "launch_folder", "kind": "switch", "app": "explorer", "path": str(launch_dir), "mechanism": "os.startfile / Windows ShellExecute folder association"})
        os.startfile(str(launch_dir))
        self._focus("explorer")
        matches = []
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            self._assert_focus()
            for control_type in ("ListItem", "DataItem"):
                matches = [item for item in self._window.descendants(control_type=control_type)
                           if item.window_text().lower() in {shortcut_name.lower(), shortcut_path.name.lower()}]
                if len(matches) == 1:
                    break
            if len(matches) == 1:
                break
            self._sleep(0.15)
        if len(matches) != 1:
            raise DesktopPrerequisiteError("The run-local Chrome shortcut could not be located uniquely in Explorer. No coordinate-only click or direct-process fallback was attempted.")
        self._assert_focus()
        matches[0].double_click_input()
        self.emit({"event": "input", "kind": "click", "app": "explorer", "action": "Double-click the run-local Chrome shortcut", "native": True})
        self.emit({"event": "launch", "kind": "switch", "app": "browser", "url": url,
                   "shortcut": str(shortcut_path), "target": str(executable),
                   "mechanism": "Visible Explorer double-click on run-local .lnk targeting Google Chrome --new-window",
                   "parent_note": "Ordinary shell interaction; running Chrome may reuse existing processes. Verify actual ancestry with independent telemetry."})

    def _browser_supplier(self, supplier_id: str) -> None:
        self._focus("browser")
        supplier = next(q for q in self.bundle["quotes"] if q["id"] == supplier_id)
        if supplier_id != self.bundle["quotes"][0]["id"]:
            # Back to the controlled comparison page using a normal browser key.
            self._press("%{LEFT}", "browser back")
            self._sleep(0.4)
        self._assert_focus()
        matches = []
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            self._assert_focus()
            matches = self._window.descendants(control_type="Hyperlink", title=supplier["supplier"])
            if len(matches) == 1:
                break
            self._sleep(0.15)
        if len(matches) != 1:
            raise DesktopPrerequisiteError(f"The local supplier link for {supplier['supplier']} is unavailable in Chrome accessibility. No coordinate-only click was attempted.")
        self._delay("think")
        self._assert_focus()
        matches[0].click_input()
        self.emit({"event": "input", "kind": "click", "app": "browser", "action": f'Open {supplier["supplier"]}', "native": True})
        self._sleep(0.3)
        self._assert_focus()
        self._delay("read", 3)
        self._press("{PGDN}", "scroll page down")
        self._delay("read", 2)
        self._press("{HOME}", "return toward page start")

    def _excel_data(self) -> None:
        self._focus("excel")
        self._press("^{HOME}", "first worksheet cell")
        self._type("\t".join(HEADERS))
        self._press("{ENTER}", "finish header row")
        self._press("^{HOME}", "return to A1")
        self._press("{DOWN}", "select A2")
        for index, quote in enumerate(self.bundle["quotes"]):
            values = (quote["supplier"], quote["unit_price"], quote["quantity"], quote["lead_days"])
            self._type("\t".join(str(value) for value in values))
            self._press("{ENTER}", "finish supplier row")
            # Explicit navigation avoids dependence on Excel's Tab/Enter origin.
            self._press("^{HOME}", "return to A1")
            for _ in range(index + 2):
                self._press("{DOWN}", "next supplier row")
            self._delay("think")

    def _excel_formulas(self) -> None:
        self._focus("excel")
        for row in range(2, 5):
            self._press("^{HOME}", "return to A1")
            for _ in range(row - 1):
                self._press("{DOWN}", "select supplier row")
            for _ in range(4):
                self._press("{RIGHT}", "select total column")
            self._type(f"=B{row}*C{row}")
            self._press("{TAB}", "commit total formula")
            self._type(f'=IF(D{row}<={self.bundle["deadline_days"]},"YES","NO")')
            self._press("{ENTER}", "commit deadline formula")
            self._delay("review")
        self._press("^{HOME}", "return to A1")
        self._press("+{RIGHT 5}", "select column headings")
        self._press("^b", "bold column headings")
        self._press("^{HOME}", "return to A1")

    def _write_report(self, app: str) -> None:
        self._focus(app)
        self._press("^{HOME}", "document start")
        # A visible, corrected transposition is part of this documented recipe.
        # It is deliberately generic so changing the selected supplier works.
        report_text = self.bundle["expected"]["report_text"]
        word = "recommendation"
        before, after = report_text.split(word, 1)
        self._type(before + "recommnedation")
        self._delay("correction")
        for _ in range(len("recommnedation")):
            self._press("{BACKSPACE}", "correct transposed word")
            self._delay("key")
        self.emit({"event": "correction", "kind": "correction", "app": app, "action": "Corrected a documented transposition", "native": True})
        self._type(word + after)
        self._delay("review")

    def _save_reopen(self, app: str, key: str) -> None:
        self._focus(app)
        self._press("^s", "save document")
        self._sleep(1.0)
        self._assert_focus()
        self._delay("review")
        self._press("^w", "close document tab")
        self._window = None
        self._app = None
        self._sleep(0.5)
        self._launch_file(app, key)
        self._delay("review")
        self.emit({"event": "reopened", "kind": "review", "app": app, "path": str(self.bundle["paths"][key])})

    def run_step(self, step: dict) -> dict:
        if self.bundle is None:
            raise RuntimeError("Call prepare() before run_step().")
        self._abort_check()
        step_id = step["id"]
        start = time.monotonic()
        actions = {
            "browser_open": self._launch_browser,
            "excel_open": lambda: self._launch_file("excel", "xlsx"),
            "excel_data": self._excel_data,
            "excel_formulas": self._excel_formulas,
            "excel_save": lambda: self._save_reopen("excel", "xlsx"),
            "word_open": lambda: self._launch_file("word", "docx"),
            "word_write": lambda: self._write_report("word"),
            "word_save": lambda: self._save_reopen("word", "docx"),
            "notepad_open": lambda: self._launch_file("notepad", "txt"),
            "notepad_write": lambda: self._write_report("notepad"),
            "notepad_save": lambda: self._save_reopen("notepad", "txt"),
        }
        if step_id.startswith("browser_") and step_id != "browser_open":
            self._browser_supplier(step["supplier"])
        elif step_id in actions:
            actions[step_id]()
        else:
            raise ValueError(f"Unknown desktop step: {step_id}")
        return {"id": step_id, "passed": True, "duration_s": round(time.monotonic() - start, 3), "workflow": self.workflow, "execution": "native UI input"}

    def verify(self) -> dict:
        if self.bundle is None:
            raise RuntimeError("Call prepare() before verify().")
        return verify_documents(self.bundle)
