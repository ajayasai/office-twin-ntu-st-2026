"""Append-only execution observations and explicitly scoped resource measures."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import threading
import time

try:
    import psutil
    from .observer import process_inventory
except ImportError:  # Wall time and controller CPU remain available.
    psutil = None


APPLICATION_NAMES = frozenset({
    "winword.exe", "excel.exe", "msedge.exe", "chrome.exe", "firefox.exe",
    "notepad.exe", "soffice.bin", "libreoffice", "chromium", "firefox",
})


class EvidenceRecorder:
    """Record controller observations, not independent Windows/Sysmon evidence.

    CPU time is the current process's user + system time via process_time().
    Other process CPU deltas are reported separately, never added to it.
    Their first observed value is a baseline, not CPU charged to this run.
    """

    def __init__(self, run_dir: Path):
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.run_dir / "events.jsonl"
        self._write_lock = threading.Lock()
        self._sample_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._started = None
        self._cpu_start = None
        self._summary = None
        self._peak_rss = None
        self._observed: dict[tuple[int, float], dict] = {}
        self._monitor_error_count = 0
        self._sequence = 0
        if self.events_path.exists():
            with self.events_path.open(encoding="utf-8") as handle:
                self._sequence = sum(1 for line in handle if line.strip())

    def emit(self, event: dict) -> None:
        if not isinstance(event, dict):
            raise TypeError("event must be a dictionary")
        with self._write_lock:
            now = time.perf_counter()
            record = dict(event)
            record.update({
                "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                "perf_counter": now,
                "elapsed_seconds": None if self._started is None else max(0.0, now - self._started),
                "sequence": self._sequence + 1,
                "evidence_source": "controller_observation",
            })
            line = json.dumps(record, ensure_ascii=False, allow_nan=False, default=str)
            with self.events_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(line + "\n")
            self._sequence += 1

    def start(self) -> "EvidenceRecorder":
        if self._summary is not None:
            raise RuntimeError("A stopped recorder cannot be restarted; use a new run directory")
        if self._started is not None:
            return self
        self._started = time.perf_counter()
        self._cpu_start = time.process_time()
        self._snapshot()
        self.emit({"event": "resource_monitor_started", "sample_interval_seconds": 0.25,
                   "monitor_backend": "psutil snapshots" if psutil else "stdlib controller CPU/wall only"})
        if psutil is not None:
            self._thread = threading.Thread(target=self._monitor, name="office-twin-resources", daemon=True)
            self._thread.start()
        return self

    def _monitor(self) -> None:
        while not self._stop_event.wait(0.25):
            self._snapshot()

    def _snapshot(self) -> None:
        if psutil is None:
            return
        try:
            controller = psutil.Process(os.getpid())
            controller_rss = controller.memory_info().rss
            child_identities = {(proc.pid, proc.create_time()) for proc in controller.children(recursive=True)}
            child_ids = {pid for pid, _ in child_identities}
            records = []
            parent_cache = {}
            # One OS inventory avoids cached process_iter names/creation times
            # and repeated Windows parent-map scans. It only finds candidates.
            inventory_started = time.time()
            for info in process_inventory():
                try:
                    if info["pid"] == os.getpid():
                        continue
                    name = (info.get("name") or "").lower()
                    if info["pid"] not in child_ids and name not in APPLICATION_NAMES:
                        continue
                    proc = psutil.Process(info["pid"])
                    with proc.oneshot():
                        created = proc.create_time()
                        # A process born after inventory began may have reused
                        # the listed PID, so its inventory metadata is unsafe.
                        if created > inventory_started:
                            continue
                        name = proc.name()
                        is_descendant = (info["pid"], created) in child_identities
                        if not is_descendant and name.lower() not in APPLICATION_NAMES:
                            continue
                        cpu, memory = proc.cpu_times(), proc.memory_info()
                    # A fresh object is essential: create_time is cached by
                    # psutil, including inside a later call on the same object.
                    if psutil.Process(info["pid"]).create_time() != created:
                        continue
                    parent_pid = info.get("parent_pid")
                    parent_name = None
                    if parent_pid is not None and parent_pid > 0:
                        if parent_pid not in parent_cache:
                            try:
                                parent = psutil.Process(parent_pid)
                                with parent.oneshot():
                                    parent_created, observed_parent_name = parent.create_time(), parent.name()
                                parent_cache[parent_pid] = ((parent_created, observed_parent_name)
                                    if psutil.Process(parent_pid).create_time() == parent_created else None)
                            except (psutil.Error, OSError):
                                parent_cache[parent_pid] = None
                        parent_info = parent_cache[parent_pid]
                        # Avoid labelling a reused PID as the original parent.
                        if parent_info is not None and parent_info[0] <= created:
                            parent_name = parent_info[1]
                    records.append((info["pid"], created, name,
                                    float(cpu.user + cpu.system), int(memory.rss),
                                    "controller descendant" if is_descendant else "application name match",
                                    parent_pid, parent_name))
                except (psutil.Error, OSError, KeyError, TypeError):
                    continue
            with self._sample_lock:
                self._peak_rss = max(self._peak_rss or 0, controller_rss)
                for pid, created, name, cpu, rss, selection, parent_pid, parent_name in records:
                    key = (pid, created)
                    current = self._observed.setdefault(key, {
                        "pid": pid, "name": name, "create_time": created, "selection": selection,
                        "cpu_first_seconds": cpu, "cpu_last_seconds": cpu,
                        "peak_observed_rss_bytes": rss, "snapshot_count": 0,
                        "parent_pid": parent_pid, "parent_name": parent_name,
                    })
                    if parent_pid is not None:
                        current["parent_pid"] = parent_pid
                    if parent_name is not None:
                        current["parent_name"] = parent_name
                    current["cpu_last_seconds"] = max(current["cpu_last_seconds"], cpu)
                    current["peak_observed_rss_bytes"] = max(current["peak_observed_rss_bytes"], rss)
                    current["snapshot_count"] += 1
        except (psutil.Error, OSError):
            self._monitor_error_count += 1

    def stop(self) -> dict:
        if self._summary is not None:
            return self._summary.copy()
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._started is not None:
            self._snapshot()
        wall = 0.0 if self._started is None else max(0.0, time.perf_counter() - self._started)
        cpu = 0.0 if self._cpu_start is None else max(0.0, time.process_time() - self._cpu_start)
        with self._sample_lock:
            observations = []
            for record in self._observed.values():
                item = record.copy()
                item["observed_cpu_delta_seconds"] = max(0.0, item["cpu_last_seconds"] - item["cpu_first_seconds"])
                observations.append(item)
        self._summary = {
            "wall_seconds": wall,
            "controller_cpu_seconds": cpu,
            "controller_peak_rss_bytes": self._peak_rss,
            "monitor_backend": "psutil snapshots" if psutil else "stdlib controller CPU/wall only",
            "sample_interval_seconds": 0.25 if psutil else None,
            "measurement_scope": "Controller CPU only; sampled controller RSS. Other process observations are separate, limited snapshots, not independent Sysmon evidence or attributable whole-system resource usage.",
            "process_observations": observations,
            "observed_processes": len(observations),
            "monitor_error_count": self._monitor_error_count,
            "limitations": [
                "Samples can miss short-lived processes and memory peaks.",
                "Named application processes may predate this run or include unrelated activity.",
                "Parent PID/name are best-effort snapshot metadata; ancestry does not establish workload attribution and inaccessible/exited parents may be unnamed.",
                "Other-process CPU deltas cover first to last observation only; they are not summed into controller CPU.",
                "Controller event logs describe requested/observed actions and do not independently prove native input delivery.",
            ],
        }
        self.emit({"event": "resource_monitor_stopped", "resources": self._summary})
        return self._summary.copy()

    def __enter__(self) -> "EvidenceRecorder":
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_type is not None:
            self.emit({"event": "run_exception", "error_type": exc_type.__name__, "message": str(exc_value)})
        self.stop()
        return False
