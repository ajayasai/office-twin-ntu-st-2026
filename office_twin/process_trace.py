"""Passive, filtered Windows process-start telemetry from the WMI provider.

This is not Sysmon and does not change logging policy, install a driver, or
collect command lines. Events prove process starts, not keyboard delivery.

Provider docs:
https://learn.microsoft.com/en-us/previous-versions/windows/desktop/krnlprov/win32-processstarttrace
https://learn.microsoft.com/en-us/windows/win32/wmisdk/swbemeventsource-nextevent
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path, PureWindowsPath
import sys
import threading


PROVIDER = "Windows WMI Win32_ProcessStartTrace"
APPLICATION_NAMES = frozenset({
    "winword.exe", "excel.exe", "msedge.exe", "chrome.exe", "firefox.exe",
    "notepad.exe", "soffice.bin",
})
WBEM_TIMEOUT = 0x80043001


def _is_timeout(error: Exception) -> bool:
    """COM may wrap the WMI HRESULT in EXCEPINFO rather than hresult."""
    pending = [getattr(error, "hresult", None), getattr(error, "excepinfo", None), error.args]
    while pending:
        value = pending.pop()
        if isinstance(value, int) and not isinstance(value, bool):
            if value & 0xFFFFFFFF == WBEM_TIMEOUT:
                return True
        elif isinstance(value, (tuple, list)):
            pending.extend(value)
    return False


class _WmiSource:
    """Create, consume and release all COM objects on the worker thread."""

    def __init__(self):
        if sys.platform != "win32":
            raise RuntimeError("Windows WMI process tracing is only available on Windows")
        try:
            import pythoncom
            from win32com.client import Dispatch
        except ImportError as exc:
            raise RuntimeError("pywin32 is unavailable; install it to enable passive WMI telemetry") from exc
        self._pythoncom = pythoncom
        self._initialized = False
        self._events = self._services = self._locator = None
        pythoncom.CoInitialize()
        self._initialized = True
        failure = None
        try:
            self._locator = Dispatch("WbemScripting.SWbemLocator")
            self._services = self._locator.ConnectServer(".", r"root\cimv2")
            self._events = self._services.ExecNotificationQuery("SELECT * FROM Win32_ProcessStartTrace")
        except Exception as exc:
            # Let the COM exception and its traceback release their proxy
            # references before uninitializing this thread's apartment.
            failure = f"{type(exc).__name__}: {exc}"
        if failure is not None:
            self.close()
            raise RuntimeError(failure)

    def next_event(self, timeout_ms: int):
        try:
            return self._events.NextEvent(timeout_ms)
        except Exception as exc:
            if _is_timeout(exc):
                return None
            raise

    def close(self):
        self._events = self._services = self._locator = None
        if self._initialized:
            self._pythoncom.CoUninitialize()
            self._initialized = False


def _resolve_process(pid: int):
    try:
        import psutil
        process = psutil.Process(pid)
        with process.oneshot():
            return {"name": process.name(), "ppid": process.ppid(), "created": process.create_time()}
    except Exception:
        # An exited/inaccessible parent is an expected observation gap.
        return None


def _field(event, name):
    return event.get(name) if isinstance(event, dict) else getattr(event, name)


def _event_time(filetime: int):
    try:
        return (datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=filetime // 10)).isoformat(timespec="microseconds")
    except (ValueError, OverflowError):
        return None


class ProcessTrace:
    """Bounded-startup collector with an injectable source for passive tests.

    ``source_factory`` returns an object exposing next_event(timeout_ms) and
    close(). Only the worker calls it; no COM object crosses thread boundaries.
    """

    def __init__(self, run_dir: Path, *, source_factory=None, process_resolver=None,
                 controller_pid=None, startup_timeout=2.0, stop_timeout=1.5):
        self.run_dir = Path(run_dir)
        self.path = self.run_dir / "os-process-events.jsonl"
        self._source_factory = source_factory or _WmiSource
        self._resolver = process_resolver or _resolve_process
        self._controller_pid = os.getpid() if controller_pid is None else int(controller_pid)
        self._startup_timeout = max(0.01, float(startup_timeout))
        self._stop_timeout = max(0.01, float(stop_timeout))
        self._stop = threading.Event()
        self._ready = threading.Event()
        self._lock = threading.Lock()
        self._thread = None
        self._available = False
        self._reason = "Not started"
        self._event_count = 0
        self._invalid_events = 0
        self._summary = None

    def start(self) -> "ProcessTrace":
        if self._summary is not None:
            raise RuntimeError("A stopped trace cannot be restarted")
        if self._thread is not None:
            return self
        try:
            self.run_dir.mkdir(parents=True, exist_ok=True)
            self.path.touch(exist_ok=True)
        except OSError as exc:
            self._reason = f"Cannot create telemetry file: {exc}"
            self._ready.set()
            return self
        self._thread = threading.Thread(target=self._worker, name="office-twin-wmi", daemon=True)
        self._thread.start()
        if not self._ready.wait(self._startup_timeout):
            self._stop.set()
            with self._lock:
                self._available = False
                self._reason = f"WMI subscription startup exceeded {self._startup_timeout:g} seconds; collection disabled"
        return self

    def _descendant(self, parent_pid: int) -> bool:
        # Resolve live ancestry rather than retaining PID-only ancestry across
        # PID reuse. Very short-lived inaccessible ancestors may be missed.
        seen = set()
        current = parent_pid
        for _ in range(32):
            if current == self._controller_pid:
                return True
            if current <= 0 or current in seen:
                return False
            seen.add(current)
            try:
                info = self._resolver(current)
                if not info:
                    return False
                current = int(info.get("ppid", 0))
            except (ValueError, TypeError, OSError):
                return False
        return False

    def _normalize(self, event):
        name = PureWindowsPath(str(_field(event, "ProcessName") or "")).name
        pid = int(_field(event, "ProcessID"))
        parent_pid = int(_field(event, "ParentProcessID"))
        filetime = int(_field(event, "TIME_CREATED"))
        if not name or pid <= 0 or parent_pid < 0 or filetime < 0:
            raise ValueError("Invalid process-start identity")
        descendant = self._descendant(parent_pid)
        app_match = name.lower() in APPLICATION_NAMES
        if not descendant and not app_match:
            return None
        try:
            parent = self._resolver(parent_pid)
            parent_name = PureWindowsPath(str(parent.get("name") or "")).name if parent else None
        except Exception:
            parent_name = None
        return {
            "event": "process_start",
            "event_source": PROVIDER,
            "process_name": name,
            "pid": pid,
            "parent_pid": parent_pid,
            "parent_name": parent_name,
            "TIME_CREATED": str(filetime),
            "event_time_utc": _event_time(filetime),
            "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "selection": "controller descendant" if descendant else "application name match; causation not established",
        }

    def _worker(self):
        source = None
        event = None
        try:
            source = self._source_factory()
            with self._lock:
                if self._stop.is_set():
                    return
                self._available = True
                self._reason = "Subscribed successfully; zero events means no matching process starts were observed"
            self._ready.set()
            while not self._stop.is_set():
                event = source.next_event(500)
                if event is None:
                    continue
                try:
                    record = self._normalize(event)
                except (ValueError, TypeError, AttributeError, OverflowError):
                    with self._lock:
                        self._invalid_events += 1
                    continue
                finally:
                    event = None
                if record is None:
                    continue
                with self._lock:
                    if self._stop.is_set():
                        break
                    with self.path.open("a", encoding="utf-8", newline="\n") as handle:
                        handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                    self._event_count += 1
        except Exception as exc:
            with self._lock:
                if not self._stop.is_set():
                    self._available = False
                    self._reason = f"WMI telemetry unavailable or interrupted ({type(exc).__name__}): {str(exc)[:700]}"
        finally:
            event = None
            if source is not None:
                try:
                    source.close()
                except Exception:
                    pass
            self._ready.set()

    def stop(self) -> dict:
        if self._summary is not None:
            return self._summary.copy()
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self._stop_timeout)
        with self._lock:
            worker_pending = self._thread is not None and self._thread.is_alive()
            self._summary = {
                "available": self._available,
                "reason": self._reason,
                "event_count": self._event_count,
                "path": str(self.path.resolve()),
                "provider": PROVIDER,
                "scope": "Selected application names and resolvable controller descendants only; no command lines, usernames, SID, executable paths or unrelated process records collected",
                "invalid_events": self._invalid_events,
                "worker_shutdown_pending": worker_pending,
                "limitations": [
                    "WMI process-start events are OS-provider observations, not Sysmon events or independent end-to-end audit evidence.",
                    "Process starts do not prove keystrokes, mouse input, app focus, document edits or task correctness.",
                    "Application name matches may be unrelated to this run; no causation is inferred.",
                    "Already-running application processes do not produce new start events merely because a document or tab opens.",
                    "Provider permissions, event delivery latency, missed events, and inaccessible or short-lived parent ancestry can limit coverage.",
                    "TIME_CREATED is the provider event-generation timestamp; observed_at_utc is the controller receipt timestamp.",
                ],
            }
            if worker_pending:
                self._summary["limitations"].append("A daemon worker has not finished its provider call; stop is bounded and further event writes are disabled.")
            return self._summary.copy()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        return False
