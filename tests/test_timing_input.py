"""Check policy routing with native guards/input replaced; no desktop calls."""
from pathlib import Path
import threading
import unittest
from unittest.mock import Mock

from office_twin.desktop import DesktopCancelled, WindowsDesktop
from office_twin.timing import TimingPolicy


class TimingInputRoutingTests(unittest.TestCase):
    def test_existing_text_executor_routes_each_character_through_new_policy(self):
        policy = TimingPolicy("human-informed", seed=42)
        events = []
        desktop = WindowsDesktop(Path("unused"), threading.Event(), lambda event: None,
                                 lambda kind, units: events.append(("wait", kind, policy.sample(kind, units))))
        desktop._abort_check = Mock()
        desktop._assert_focus = Mock()
        desktop._send_keys = Mock(side_effect=lambda *a, **kw: events.append(("send", a[0])))
        desktop._type("A+\n\t")
        self.assertEqual([e[0] for e in events], ["wait", "send"] * 4)
        self.assertEqual([e[1] for e in events if e[0] == "send"], ["A", "{+}", "{ENTER}", "{TAB}"])
        self.assertEqual(policy.metadata()["sample_count"], 4)
        self.assertTrue(all(e[1] == "key" and e[2] > 0 for e in events if e[0] == "wait"))
        self.assertEqual(desktop._assert_focus.call_count, 4)

    def test_cancelled_policy_wait_prevents_dispatch(self):
        desktop = WindowsDesktop(Path("unused"), threading.Event(), Mock(),
                                 Mock(side_effect=DesktopCancelled("cancelled wait")))
        desktop._abort_check = Mock()
        desktop._assert_focus = Mock()
        desktop._send_keys = Mock()
        with self.assertRaises(DesktopCancelled):
            desktop._type("A")
        desktop._send_keys.assert_not_called()
        desktop._assert_focus.assert_not_called()
