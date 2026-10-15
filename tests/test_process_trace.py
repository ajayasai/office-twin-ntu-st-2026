import json
from pathlib import Path
import queue
import tempfile
import threading
import time
import unittest

from office_twin.process_trace import ProcessTrace, PROVIDER, _is_timeout


class FakeSource:
    def __init__(self, events=()):
        self.events = queue.Queue()
        for event in events:
            self.events.put(event)
        self.closed = False

    def next_event(self, timeout_ms):
        try:
            return self.events.get(timeout=min(timeout_ms / 1000, 0.01))
        except queue.Empty:
            return None

    def close(self):
        self.closed = True


def event(name, pid, parent):
    return {"ProcessName": name, "ProcessID": pid, "ParentProcessID": parent,
            "TIME_CREATED": "116444736000000000", "CommandLine": "must never be collected", "Sid": "private"}


class ProcessTraceTests(unittest.TestCase):
    def wait_for_count(self, trace, count):
        deadline = time.monotonic() + 1
        while trace._event_count < count and time.monotonic() < deadline:
            time.sleep(0.005)
        self.assertEqual(trace._event_count, count)

    def test_scope_and_serialization_exclude_private_unrelated_details(self):
        source = FakeSource([event("private-program.exe", 20, 1), event("chrome.exe", 21, 1), event("python.exe", 22, 100), event("helper.exe", 23, 22)])
        def resolver(pid):
            return {1: {"name": "explorer.exe", "ppid": 0}, 22: {"name": "python.exe", "ppid": 100}}.get(pid)
        with tempfile.TemporaryDirectory() as directory:
            trace = ProcessTrace(Path(directory), source_factory=lambda: source, process_resolver=resolver, controller_pid=100).start()
            self.wait_for_count(trace, 3)
            summary = trace.stop()
            records = [json.loads(line) for line in trace.path.read_text(encoding="utf-8").splitlines()]
            self.assertTrue(summary["available"])
            self.assertTrue(source.closed)
            self.assertEqual([record["pid"] for record in records], [21, 22, 23])
            self.assertTrue(all(record["event_source"] == PROVIDER for record in records))
            self.assertEqual(records[0]["parent_name"], "explorer.exe")
            self.assertEqual(records[0]["event_time_utc"], "1970-01-01T00:00:00.000000+00:00")
            self.assertIn("causation not established", records[0]["selection"])
            self.assertEqual(records[2]["selection"], "controller descendant")
            raw = trace.path.read_text(encoding="utf-8")
            for forbidden in ("CommandLine", "must never", "private-program", '"Sid"'):
                self.assertNotIn(forbidden, raw)
            self.assertEqual(summary, trace.stop())

    def test_unavailable_provider_is_truthful_and_nonfatal(self):
        def denied():
            raise PermissionError("provider access denied")
        with tempfile.TemporaryDirectory() as directory:
            trace = ProcessTrace(Path(directory), source_factory=denied).start()
            summary = trace.stop()
            self.assertFalse(summary["available"])
            self.assertIn("access denied", summary["reason"])
            self.assertEqual(summary["event_count"], 0)
            self.assertEqual(trace.path.read_text(encoding="utf-8"), "")

    def test_startup_and_stop_are_bounded_even_when_source_initialization_blocks(self):
        release = threading.Event()
        source = FakeSource()
        def blocked():
            release.wait(1)
            return source
        with tempfile.TemporaryDirectory() as directory:
            started = time.monotonic()
            trace = ProcessTrace(Path(directory), source_factory=blocked, startup_timeout=0.02, stop_timeout=0.02).start()
            summary = trace.stop()
            self.assertLess(time.monotonic() - started, 0.5)
            self.assertFalse(summary["available"])
            self.assertTrue(summary["worker_shutdown_pending"])
            release.set()
            trace._thread.join(1)
            self.assertTrue(source.closed)
            self.assertEqual(trace.path.read_text(encoding="utf-8"), "")

    def test_bad_record_does_not_end_stream(self):
        source = FakeSource([event("chrome.exe", "not-a-pid", 1), event("notepad.exe", 45, 1)])
        with tempfile.TemporaryDirectory() as directory:
            trace = ProcessTrace(Path(directory), source_factory=lambda: source, process_resolver=lambda pid: None).start()
            self.wait_for_count(trace, 1)
            summary = trace.stop()
            self.assertEqual(summary["invalid_events"], 1)
            self.assertTrue(summary["available"])

    def test_nested_com_timeout_code_is_recognized_without_masking_access_denied(self):
        self.assertTrue(_is_timeout(Exception(-2147352567, "wrapper", (0, "WMI", "timeout", None, 0, -2147209215))))
        self.assertFalse(_is_timeout(PermissionError(-2147217405, "access denied")))


if __name__ == "__main__":
    unittest.main()
