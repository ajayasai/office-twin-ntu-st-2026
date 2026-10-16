from pathlib import Path
import tempfile
import threading
import types
import unittest
from unittest.mock import Mock, patch

from office_twin.desktop import WindowsDesktop, DesktopFocusError, DesktopPrerequisiteError


class ReportLaunchTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.workspace = Path(self.directory.name).resolve()
        self.report = self.workspace / "OfficeTwin-1234abcd-recommendation.txt"
        self.report.write_text("saved recommendation", encoding="utf-8")
        self.events = []
        self.desktop = WindowsDesktop(self.workspace, threading.Event(), self.events.append, lambda *args: None)
        self.desktop.bundle = {"token": "1234abcd", "paths": {"txt": self.report}}
        for name in ("_abort_check", "_office_gate", "_focus", "_assert_focus", "_sleep"):
            setattr(self.desktop, name, Mock())
        self.desktop._find_window = Mock(return_value=object())
        self.shortcut_item = Mock()
        self.shortcut_item.window_text.return_value = "Open OfficeTwin report 1234abcd"
        self.desktop._window = Mock()
        self.desktop._window.descendants.return_value = [self.shortcut_item]
        self.shortcut = Mock()
        client = types.ModuleType("win32com.client")
        client.Dispatch = Mock(return_value=Mock(CreateShortcut=Mock(return_value=self.shortcut)))
        com = types.ModuleType("win32com")
        com.client = client
        self.addCleanup(patch.stopall)
        patch.dict("sys.modules", {"win32com": com, "win32com.client": client}).start()
        self.startfile = patch("office_twin.desktop.os.startfile", create=True).start()

    def test_visible_report_launch_reuses_folder_and_never_directly_opens_file(self):
        self.desktop._launch_file("notepad", "txt")
        self.startfile.assert_not_called()
        self.assertEqual(self.shortcut.TargetPath, str(self.report))
        self.assertEqual(self.shortcut.Arguments, "")
        self.shortcut.Save.assert_called_once()
        self.shortcut_item.double_click_input.assert_called_once()
        self.assertEqual([call.args[0] for call in self.desktop._focus.call_args_list], ["explorer", "notepad"])
        self.assertIn("Visible Explorer double-click", self.events[-1]["mechanism"])
        self.assertEqual(self.report.read_text(encoding="utf-8"), "saved recommendation")

    def test_missing_explorer_opens_only_owned_folder(self):
        self.desktop._find_window.side_effect = DesktopPrerequisiteError("absent")
        self.desktop._launch_file("notepad", "txt")
        self.startfile.assert_called_once_with(str(self.workspace / "OfficeTwin-launch-1234abcd"))
        self.shortcut_item.double_click_input.assert_called_once()

    def test_ambiguous_explorer_fails_without_additional_window_or_input(self):
        self.desktop._find_window.side_effect = DesktopFocusError("multiple windows")
        with self.assertRaises(DesktopFocusError):
            self.desktop._launch_file("notepad", "txt")
        self.startfile.assert_not_called()
        self.shortcut_item.double_click_input.assert_not_called()

    def test_out_of_scope_target_is_rejected_before_shell_or_input(self):
        other = self.workspace / "unrelated.txt"
        other.write_text("private content", encoding="utf-8")
        with self.assertRaises(DesktopPrerequisiteError):
            self.desktop._launch_report_via_explorer(other)
        self.shortcut.Save.assert_not_called()
        self.startfile.assert_not_called()
        self.shortcut_item.double_click_input.assert_not_called()

    def test_shortcut_not_found_has_bounded_failure_without_fallback(self):
        self.desktop._window.descendants.return_value = []
        with patch("office_twin.desktop.time.monotonic", side_effect=[0, 0, 9]):
            with self.assertRaisesRegex(DesktopPrerequisiteError, "uniquely"):
                self.desktop._launch_report_via_explorer(self.report)
        self.startfile.assert_not_called()
        self.shortcut_item.double_click_input.assert_not_called()


if __name__ == "__main__":
    unittest.main()
