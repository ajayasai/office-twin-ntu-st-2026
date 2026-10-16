"""Read-only process polling in a process separate from the task controller.

These are sampled OS process observations, not process-start/exit events. The
observer deliberately has no access to controller action logs, browser content,
command lines, environment variables, usernames, file paths, or input hooks.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import statistics
import time

import psutil


APPLICATION_SCOPES = {"chrome.exe": "chrome", "chrome": "chrome",
                      "notepad.exe": "notepad", "notepad": "notepad"}
SCOPES = ("controller", "controller_descendants", "chrome", "notepad")
LIMITATIONS = [
    "Sampled polling can miss short-lived processes, CPU before first/after last observation, and transient memory peaks; first seen and not seen are not process-start or exit events.",
    "Chrome and Notepad are name-selected application cohorts. Existing tabs, documents, background activity, and unrelated instances are included; their resources are not exclusive task costs.",
    "Parent identity is a best-effort snapshot of the current parent PID, accepted only when its creation time is no later than the child. It does not prove process creation or workload causation.",
    "CPU is user plus system CPU-seconds between each identity's first and last successful resource observations. A single observation contributes zero; lifetime CPU is never charged to the run.",
    "Scope peak RSS is the largest simultaneous sum of sampled process RSS. Shared memory pages can be counted in multiple processes; this is not unique physical memory or the sum of individual process peaks.",
    "Observer CPU and RSS are measured separately. Sampling and the existing controller recorder add overhead; OS access failures and scheduling gaps reduce coverage.",
    "A separate observer process reads real OS process counters but is not an independent auditor, Sysmon/ETW trace, proof of input delivery, or proof of human activity.",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def safe_name(value: object) -> str:
    """Do not let an unexpected provider value become a path/content leak."""
    if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_. -]{1,100}", value):
        return value
    return "redacted-process-name"


def identity(pid: object, created: object) -> tuple[int, float]:
    if type(pid) is not int or pid <= 0:
        raise ValueError("Process PID must be a positive integer")
    if isinstance(created, bool) or not isinstance(created, (int, float)) or not math.isfinite(created) or created <= 0:
        raise ValueError("Process creation time must be a positive finite timestamp")
    return pid, float(created)


def identity_record(key: tuple[int, float]) -> dict:
    return {"pid": key[0], "create_time": key[1]}


def process_inventory() -> list[dict]:
    """Read process IDs, executable names and parent IDs in one OS snapshot.

    Windows psutil ppid() rebuilds the system map for each call. Toolhelp avoids
    hundreds of full inventories per sample and requires no admin permission.
    https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/ns-tlhelp32-processentry32w
    """
    if os.name != "nt":
        return [{"pid": proc.info["pid"], "name": proc.info["name"], "parent_pid": proc.info["ppid"]}
                for proc in psutil.process_iter(["pid", "name", "ppid"], ad_value=None)
                if proc.info["name"] is not None and proc.info["ppid"] is not None]
    import ctypes
    from ctypes import wintypes

    class ProcessEntry(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", wintypes.WCHAR * 260)]
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.Process32FirstW.restype = wintypes.BOOL
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(ProcessEntry)]
    kernel.Process32NextW.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    snapshot = kernel.CreateToolhelp32Snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS only
    if snapshot == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())
    rows = []
    try:
        entry = ProcessEntry()
        entry.dwSize = ctypes.sizeof(entry)
        more = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        if not more:
            raise ctypes.WinError(ctypes.get_last_error())
        while more:
            rows.append({"pid": int(entry.th32ProcessID), "name": entry.szExeFile,
                         "parent_pid": int(entry.th32ParentProcessID)})
            more = kernel.Process32NextW(snapshot, ctypes.byref(entry))
        if ctypes.get_last_error() != 18:  # ERROR_NO_MORE_FILES is expected.
            raise ctypes.WinError(ctypes.get_last_error())
    finally:
        kernel.CloseHandle(snapshot)
    return rows


def clean_process(record: dict) -> dict:
    """An explicit allowlist protects output even when a provider adds fields."""
    key = identity(record.get("pid"), record.get("create_time"))
    cpu = record.get("cpu_total_seconds")
    rss = record.get("rss_bytes")
    if isinstance(cpu, bool) or not isinstance(cpu, (int, float)) or not math.isfinite(cpu) or cpu < 0:
        raise ValueError("CPU total must be finite and nonnegative")
    if type(rss) is not int or rss < 0:
        raise ValueError("RSS must be a nonnegative integer")
    scope = record.get("scope")
    if scope not in SCOPES:
        raise ValueError("Unknown observation scope")
    ppid = record.get("parent_pid")
    if type(ppid) is not int or ppid < 0:
        ppid = None
    parent = None
    raw_parent = record.get("parent_identity")
    if isinstance(raw_parent, dict):
        try:
            parent_key = identity(raw_parent.get("pid"), raw_parent.get("create_time"))
            if parent_key[0] == ppid and parent_key[1] <= key[1]:
                parent = {**identity_record(parent_key), "name": safe_name(raw_parent.get("name"))}
        except ValueError:
            pass
    return {**identity_record(key), "name": safe_name(record.get("name")), "scope": scope,
            "parent_pid": ppid, "parent_identity": parent,
            "parent_identity_status": "observed-compatible-age" if parent else "unresolved-or-incompatible-age",
            "cpu_total_seconds": float(cpu), "rss_bytes": rss}


class ObservationLedger:
    """Aggregate identity-safe snapshots without inferring unobserved events."""
    def __init__(self):
        self.processes = {}
        self.scope_peak_rss = {scope: 0 for scope in SCOPES}
        self.gaps = []
        self.last_elapsed = None
        self.snapshot_count = 0
        self.previous_keys = set()
        self.not_seen_transitions = 0

    def add(self, records: list[dict], elapsed: float) -> dict:
        if not math.isfinite(elapsed) or elapsed < 0 or (self.last_elapsed is not None and elapsed < self.last_elapsed):
            raise ValueError("Snapshot time must be finite, nonnegative, and monotonic")
        if self.last_elapsed is not None:
            self.gaps.append(elapsed - self.last_elapsed)
        self.last_elapsed = elapsed
        self.snapshot_count += 1
        clean = [clean_process(record) for record in records]
        keys = set()
        newly_seen = []
        scope_rss = {scope: 0 for scope in SCOPES}
        for item in clean:
            key = identity(item["pid"], item["create_time"])
            if key in keys:
                raise ValueError("Duplicate identity in one snapshot")
            keys.add(key)
            scope_rss[item["scope"]] += item["rss_bytes"]
            if key not in self.processes:
                newly_seen.append(identity_record(key))
                self.processes[key] = {**item, "first_observed_seconds": elapsed,
                                       "last_observed_seconds": elapsed, "samples": 0,
                                       "cpu_first_seconds": item["cpu_total_seconds"],
                                       "cpu_last_seconds": item["cpu_total_seconds"],
                                       "peak_sampled_rss_bytes": item["rss_bytes"],
                                       "cpu_counter_decreases": 0}
            record = self.processes[key]
            if item["scope"] != record["scope"]:
                # The controller binding can arrive after its process was seen
                # as a descendant. Keep one scope and do not count it twice.
                record["scope"] = item["scope"]
            if item["cpu_total_seconds"] < record["cpu_last_seconds"]:
                record["cpu_counter_decreases"] += 1
            record["cpu_last_seconds"] = max(record["cpu_last_seconds"], item["cpu_total_seconds"])
            record["last_observed_seconds"] = elapsed
            record["peak_sampled_rss_bytes"] = max(record["peak_sampled_rss_bytes"], item["rss_bytes"])
            record["samples"] += 1
            if item["parent_identity"] is not None:
                record["parent_identity"] = item["parent_identity"]
                record["parent_identity_status"] = item["parent_identity_status"]
        no_longer_seen = self.previous_keys - keys
        self.not_seen_transitions += len(no_longer_seen)
        self.previous_keys = keys
        for scope in SCOPES:
            self.scope_peak_rss[scope] = max(self.scope_peak_rss[scope], scope_rss[scope])
        return {"processes": clean, "scope_rss_bytes": scope_rss,
                "newly_observed_identities": newly_seen,
                "not_seen_in_this_snapshot": [identity_record(key) for key in sorted(no_longer_seen)]}

    def summarize(self, interval: float) -> dict:
        processes = []
        for item in sorted(self.processes.values(), key=lambda row: (row["pid"], row["create_time"])):
            out = {key: value for key, value in item.items() if key not in {"cpu_total_seconds", "rss_bytes"}}
            out["observed_cpu_delta_seconds"] = max(0.0, item["cpu_last_seconds"] - item["cpu_first_seconds"])
            processes.append(out)
        scopes = {}
        for scope in SCOPES:
            members = [row for row in processes if row["scope"] == scope]
            scopes[scope] = {"process_count": len(members),
                             "observed_cpu_delta_seconds": sum(row["observed_cpu_delta_seconds"] for row in members),
                             "peak_sampled_rss_bytes": self.scope_peak_rss[scope],
                             "single_sample_process_count": sum(row["samples"] == 1 for row in members)}
        return {"snapshot_count": self.snapshot_count, "process_count": len(processes), "scopes": scopes,
                "process_observations": processes, "not_seen_transitions": self.not_seen_transitions,
                "cadence": {"median_gap_seconds": statistics.median(self.gaps) if self.gaps else None,
                            "max_gap_seconds": max(self.gaps) if self.gaps else None,
                            "overrun_count": sum(gap > interval * 1.5 for gap in self.gaps),
                            "overrun_threshold_seconds": interval * 1.5}}


class ProcessSnapshotProvider:
    """Select application cohorts and the exact bound controller identity."""
    def __init__(self, controller_identity: tuple[int, float] | None = None):
        self.controller_identity = controller_identity
        self.read_error_count = 0
        self.race_discard_count = 0

    def _metadata(self, base: dict, inventory_started: float) -> dict | None:
        try:
            # Fresh Process objects avoid retaining a cached creation time
            # across polling samples when Windows reuses a PID.
            proc = psutil.Process(base["pid"])
            result = {**base, "create_time": proc.create_time()}
            if result["create_time"] > inventory_started:
                # Do not attach snapshot parent metadata to a PID that may
                # have been recycled after the inventory began.
                self.race_discard_count += 1
                return None
            identity(result["pid"], result["create_time"])
            return result
        except (psutil.Error, OSError, ValueError):
            self.read_error_count += 1
            return None

    def _scope(self, meta: dict, metadata: dict) -> str | None:
        key = (meta["pid"], meta["create_time"])
        if key == self.controller_identity:
            return "controller"
        app_scope = APPLICATION_SCOPES.get(meta["name"].lower())
        if app_scope:
            return app_scope
        if self.controller_identity is None:
            return None
        current, visited = meta, set()
        for _ in range(32):
            ppid = current["parent_pid"]
            if ppid in visited or ppid <= 0:
                break
            visited.add(ppid)
            parent = metadata.get(ppid)
            if parent is None or parent["create_time"] > current["create_time"]:
                break
            if (parent["pid"], parent["create_time"]) == self.controller_identity:
                return "controller_descendants"
            current = parent
        return None

    def snapshot(self) -> list[dict]:
        metadata = {}
        # This inventory is internal only. Output contains selected processes
        # and their immediate parent metadata, never the all-process list.
        try:
            inventory_started = time.time()
            inventory = process_inventory()
        except (psutil.Error, OSError):
            self.read_error_count += 1
            return []
        by_pid = {base["pid"]: base for base in inventory if base["pid"] > 0}
        candidate_ids = {pid for pid, base in by_pid.items() if base["name"].lower() in APPLICATION_SCOPES}
        if self.controller_identity is not None:
            root_pid = self.controller_identity[0]
            candidate_ids.add(root_pid)
            # Cheap candidate discovery only. _scope later verifies creation
            # times along every link so PID reuse cannot establish ancestry.
            for pid, base in by_pid.items():
                current, visited = base, set()
                for _ in range(32):
                    ppid = current["parent_pid"]
                    if ppid == root_pid:
                        candidate_ids.add(pid)
                        break
                    if ppid in visited or ppid not in by_pid:
                        break
                    visited.add(ppid)
                    current = by_pid[ppid]
        metadata_ids = candidate_ids | {by_pid[pid]["parent_pid"] for pid in candidate_ids if pid in by_pid}
        for pid in metadata_ids:
            if pid not in by_pid:
                continue
            meta = self._metadata(by_pid[pid], inventory_started)
            if meta is not None:
                metadata[meta["pid"]] = meta
        result = []
        for pid, meta in metadata.items():
            if pid == os.getpid() or pid not in candidate_ids:
                continue
            scope = self._scope(meta, metadata)
            if scope is None:
                continue
            try:
                proc = psutil.Process(pid)
                with proc.oneshot():
                    if proc.create_time() != meta["create_time"]:
                        self.race_discard_count += 1
                        continue
                    cpu, memory = proc.cpu_times(), proc.memory_info()
                # A new object avoids the earlier oneshot/cache when checking
                # whether PID reuse occurred while reading the counters.
                if psutil.Process(pid).create_time() != meta["create_time"]:
                    self.race_discard_count += 1
                    continue
                parent = metadata.get(meta["parent_pid"])
                parent_identity = None
                if parent is not None and parent["create_time"] <= meta["create_time"]:
                    parent_identity = {"pid": parent["pid"], "create_time": parent["create_time"], "name": parent["name"]}
                result.append(clean_process({**meta, "scope": scope, "parent_identity": parent_identity,
                                             "cpu_total_seconds": float(cpu.user + cpu.system), "rss_bytes": int(memory.rss)}))
            except (psutil.Error, OSError, ValueError):
                self.read_error_count += 1
        return result


def write_json_atomic(path: Path, payload: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


def observe(output: Path, *, stop_file: Path | None = None, controller_file: Path | None = None,
            controller_identity: tuple[int, float] | None = None, interval: float = 0.1,
            duration: float = 1800.0) -> dict:
    """Run synchronously; launch this function in a separate OS process."""
    if not math.isfinite(interval) or not 0.05 <= interval <= 10:
        raise ValueError("Interval must be between 0.05 and 10 seconds")
    if not math.isfinite(duration) or not 0 < duration <= 86400:
        raise ValueError("Duration must be positive and at most 86400 seconds")
    if controller_identity is not None:
        controller_identity = identity(*controller_identity)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if (output / "external-observer-samples.jsonl").exists() or (output / "external-observer-summary.json").exists():
        raise ValueError("Use a fresh observer output directory; existing evidence is never overwritten")
    provider = ProcessSnapshotProvider(controller_identity)
    ledger = ObservationLedger()
    started_utc, started, cpu_started = utc_now(), time.perf_counter(), time.process_time()
    observer_pid = os.getpid()
    observer_created = psutil.Process(observer_pid).create_time()
    observer_peak_rss = 0
    binding_errors = 0
    status, reason = "completed", "duration_limit"
    binding_time = 0.0 if controller_identity else None
    samples_path = output / "external-observer-samples.jsonl"
    try:
        with samples_path.open("x", encoding="utf-8", newline="\n") as handle:
            while True:
                sample_started = time.perf_counter()
                elapsed = sample_started - started
                if provider.controller_identity is None and controller_file is not None and controller_file.exists():
                    try:
                        binding = json.loads(controller_file.read_text(encoding="utf-8"))
                        candidate = identity(binding["pid"], binding["create_time"])
                        if candidate[0] == observer_pid:
                            raise ValueError("Observer cannot be its own controller")
                        provider.controller_identity = candidate
                        binding_time = elapsed
                    except (OSError, ValueError, KeyError, TypeError):
                        binding_errors += 1
                records = provider.snapshot()
                sampled = ledger.add(records, elapsed)
                try:
                    observer_peak_rss = max(observer_peak_rss, psutil.Process(observer_pid).memory_info().rss)
                except psutil.Error:
                    provider.read_error_count += 1
                event = {"event": "process_snapshot", "evidence_source": "external_process_snapshot_observer",
                         "method": "sampled_polling", "sequence": ledger.snapshot_count,
                         "timestamp_utc": utc_now(), "elapsed_seconds": elapsed,
                         "snapshot_read_seconds": time.perf_counter() - sample_started, **sampled}
                handle.write(json.dumps(event, allow_nan=False) + "\n")
                handle.flush()
                if ledger.snapshot_count == 1:
                    write_json_atomic(output / "observer-ready.json", {
                        "status": "ready", "observer_identity": {"pid": observer_pid, "create_time": observer_created},
                        "timestamp_utc": utc_now(), "first_sample_complete": True, "method": "sampled_polling"})
                if stop_file is not None and stop_file.exists():
                    reason = "stop_file"
                    break
                if time.perf_counter() - started >= duration:
                    break
                time.sleep(max(0.0, interval - (time.perf_counter() - sample_started)))
    except KeyboardInterrupt:
        status, reason = "interrupted", "keyboard_interrupt"
    except Exception as error:
        status, reason = "failed", type(error).__name__
    summary = {"schema_version": 1, "evidence_source": "external_process_snapshot_observer",
               "provider": "Windows Toolhelp inventory + psutil identity/resource snapshots" if os.name == "nt" else "psutil process snapshots", "method": "sampled_polling",
               "process_start_event_trace": False, "status": status, "stop_reason": reason,
               "started_utc": started_utc, "ended_utc": utc_now(), "duration_seconds": time.perf_counter() - started,
               "interval_seconds": interval, "observer_identity": {"pid": observer_pid, "create_time": observer_created},
               "controller_identity": identity_record(provider.controller_identity) if provider.controller_identity else None,
               "controller_bound_at_seconds": binding_time, "controller_binding_error_count": binding_errors,
               "observer_resources": {"cpu_seconds": max(0.0, time.process_time() - cpu_started),
                                      "peak_sampled_rss_bytes": observer_peak_rss},
               "read_error_count": provider.read_error_count, "race_discard_count": provider.race_discard_count,
               "selection": "Exact controller PID plus creation time and observed descendants; all Chrome and Notepad processes by application name. Application cohorts include shared/unrelated activity.",
               "limitations": LIMITATIONS, **ledger.summarize(interval)}
    write_json_atomic(output / "external-observer-summary.json", summary)
    return summary
