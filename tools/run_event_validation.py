"""Run known process lifecycles and a separate native pair inside a ready ETW capture.

The elevated collector is launched by the participant. This worker remains
unelevated. Canary processes only exit; their exact PIDs and time bounds are
private verification inputs, not public evidence. Native trials use the existing
Office Twin harness and dedicated Sheet. No historical run is changed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
CANARY_PYTHON = getattr(sys, "_base_executable", sys.executable)
RUNDOWN_APPLICATIONS = {"chrome.exe", "notepad.exe", "explorer.exe"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class WindowsSnapshotReader:
    """Read limited process metadata without commands, paths or desktop state."""
    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ctypes, self.wintypes = ctypes, wintypes
        self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        self.kernel.OpenProcess.restype = wintypes.HANDLE
        self.kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
        self.kernel.GetProcessTimes.restype = wintypes.BOOL
        self.kernel.GetSystemTimePreciseAsFileTime.argtypes = [ctypes.POINTER(wintypes.FILETIME)]
        self.kernel.GetSystemTimePreciseAsFileTime.restype = None
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel.CloseHandle.restype = wintypes.BOOL

    @staticmethod
    def filetime(value):
        # Keep all 100 ns bits. Epoch float conversion loses identity precision.
        return (int(value.dwHighDateTime) << 32) | int(value.dwLowDateTime)

    def system_filetime(self):
        value = self.wintypes.FILETIME()
        self.kernel.GetSystemTimePreciseAsFileTime(self.ctypes.byref(value))
        return self.filetime(value)

    def inventory(self):
        from office_twin.observer import process_inventory
        return process_inventory()  # TH32CS_SNAPPROCESS: PID, PPID, executable basename.

    def created(self, pid):
        handle = self.kernel.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            raise self.ctypes.WinError(self.ctypes.get_last_error())
        try:
            created, exited, kernel, user = (self.wintypes.FILETIME() for _ in range(4))
            if not self.kernel.GetProcessTimes(handle, *(self.ctypes.byref(value)
                                                        for value in (created, exited, kernel, user))):
                raise self.ctypes.WinError(self.ctypes.get_last_error())
            value = self.filetime(created)
            if value <= 0 or self.filetime(exited) != 0:
                raise OSError("Process is no longer alive or has no creation identity")
            return value
        finally:
            self.kernel.CloseHandle(handle)


def collect_rundown_snapshot(phase, reader=None):
    """Cross-check live application identities; never invent exited ancestors.

    Toolhelp's parent PID is retained as reported metadata. An ancestor row is
    included only if that live identity is no younger than its child. A fresh
    process handle rechecks every retained creation time after traversal.
    """
    if phase not in {"before-native", "after-native"}:
        raise ValueError("Unknown rundown snapshot phase")
    reader = reader if reader is not None else WindowsSnapshotReader()
    result = {"phase": phase, "source": "Toolhelp32Snapshot+GetProcessTimes",
              "started_utc": now(), "processes": [], "read_error_count": 0,
              "race_discard_count": 0, "rejected_parent_count": 0}
    inventory_started = reader.system_filetime()
    inventory = reader.inventory()
    by_pid = {row["pid"]: row for row in inventory
              if type(row.get("pid")) is int and row["pid"] > 0}
    metadata = {}

    def read(pid):
        if pid in metadata:
            return metadata[pid]
        base = by_pid.get(pid)
        if base is None:
            return None
        try:
            created = reader.created(pid)
            if type(created) is not int or created <= 0:
                raise ValueError("Exact integer FILETIME required")
            if created > inventory_started:
                result["race_discard_count"] += 1
                metadata[pid] = None
                return None
            parent_pid = base.get("parent_pid")
            if type(parent_pid) is not int or parent_pid < 0:
                raise ValueError("Invalid reported parent PID")
            name = base.get("name")
            name = name if isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9_. -]{1,100}", name) else "redacted-process-name"
            row = {"pid": pid, "create_time_filetime": str(created),
                   "parent_pid": parent_pid, "name": name}
        except (OSError, ValueError):
            result["read_error_count"] += 1
            row = None
        metadata[pid] = row
        return row

    selected = {}
    for pid, base in by_pid.items():
        if str(base.get("name", "")).lower() not in RUNDOWN_APPLICATIONS:
            continue
        current, visited = read(pid), set()
        while current is not None:
            selected[current["pid"]] = current
            visited.add(current["pid"])
            parent_pid = current["parent_pid"]
            if parent_pid == 0:
                break
            if parent_pid in visited:
                result["rejected_parent_count"] += 1
                break
            parent = read(parent_pid)
            if parent is None:
                break
            if int(parent["create_time_filetime"]) > int(current["create_time_filetime"]):
                result["rejected_parent_count"] += 1
                break
            current = parent
    for pid, row in sorted(selected.items()):
        try:
            rechecked = reader.created(pid)  # New handle, not a cached PID lookup.
            if type(rechecked) is not int or rechecked != int(row["create_time_filetime"]):
                result["race_discard_count"] += 1
                continue
        except OSError:
            result["read_error_count"] += 1
            continue
        result["processes"].append({**row, "identity_rechecked": True})
    result["finished_utc"] = now()
    return result


def simple_canary(phase, index):
    expected = 7 if index % 4 == 3 else 0
    before = now()
    # The in-box command interpreter executes only a literal exit. Its short
    # lifecycle challenges snapshot polling; actual duration comes from ETW.
    executable = str(Path(os.environ["SystemRoot"]) / "System32" / "cmd.exe")
    process = subprocess.Popen(
        [executable, "/d", "/c", "exit", str(expected)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW)
    actual = process.wait(timeout=15)
    return {"phase": phase, "kind": "short-lived-child", "pid": process.pid,
            "parent_pid": os.getpid(), "expected_exit_code": expected,
            "actual_exit_code": actual, "launch_before_utc": before,
            "wait_finished_utc": now()}


def nested_canary(phase):
    # The child reports its own child's identity and boundaries. The parent
    # records the intermediate process independently through Popen/wait.
    code = """import datetime,json,os,subprocess,sys
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds')
before=now()
p=subprocess.Popen([sys.executable,'-c','import sys; sys.exit(7)'],creationflags=subprocess.CREATE_NO_WINDOW)
actual=p.wait(timeout=15)
print(json.dumps({'pid':p.pid,'parent_pid':os.getpid(),'expected_exit_code':7,'actual_exit_code':actual,'launch_before_utc':before,'wait_finished_utc':now()}),flush=True)
"""
    before = now()
    process = subprocess.Popen([CANARY_PYTHON, "-c", code], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
    stdout, stderr = process.communicate(timeout=30)
    intermediate = {"phase": phase, "kind": "intermediate-parent", "pid": process.pid,
                    "parent_pid": os.getpid(), "expected_exit_code": 0,
                    "actual_exit_code": process.returncode, "launch_before_utc": before,
                    "wait_finished_utc": now()}
    if process.returncode != 0:
        raise RuntimeError("Nested canary failed: " + stderr[:500])
    child = json.loads(stdout)
    if child["parent_pid"] != process.pid:
        raise RuntimeError("Nested canary parent identity disagrees with launched process")
    return [intermediate, {**child, "phase": phase, "kind": "nested-child"}]


def stop_declared_python(identity_file, key=None):
    """Cancel only exact Python identities declared in this attempt's files."""
    import psutil
    try:
        declared = json.loads(identity_file.read_text(encoding="utf-8"))
        if key:
            declared = declared[key]
        process = psutil.Process(declared["pid"])
        if (process.pid == os.getpid() or process.create_time() != declared["create_time"]
                or process.name().lower() not in {"python.exe", "pythonw.exe"}):
            return
        process.terminate()
        try:
            process.wait(timeout=5)
        except psutil.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    except (OSError, ValueError, KeyError, psutil.Error):
        pass


def run_native_guarded(capture, output, seed, ready_data, collector):
    identity_file = capture / "harness-identity.json"
    wrapper = """import json,os,psutil,runpy,sys
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({'pid':os.getpid(),'create_time':psutil.Process().create_time()}),encoding='utf-8')
sys.argv=sys.argv[2:]
runpy.run_path(sys.argv[0],run_name='__main__')
"""
    process = subprocess.Popen([sys.executable, "-u", "-c", wrapper, str(identity_file),
                                str(ROOT / "tools/run_benchmark.py"), "--output", str(output),
                                "--seeds", str(seed)], cwd=ROOT)
    deadline = datetime.fromisoformat(ready_data["trace_started_utc"].replace("Z", "+00:00")).timestamp() + ready_data["max_seconds"] - 60
    try:
        while process.poll() is None:
            if time.time() >= deadline:
                raise RuntimeError("Stopping workload before the collector duration limit")
            if (not collector.is_running() or (capture / "capture-status.json").exists()
                    or (capture / "stop.request").exists()):
                raise RuntimeError("ETW collector stopped before native validation finished")
            time.sleep(0.25)
        return process.returncode
    finally:
        if process.poll() is None:
            # Stop the harness first to prevent another trial, then any actual
            # interpreters declared by that harness. Never kill app cohorts.
            stop_declared_python(identity_file)
            for path in output.glob("*/controller-identity.json"):
                stop_declared_python(path)
            for path in output.glob("*/observer/observer-ready.json"):
                stop_declared_python(path, "observer_identity")
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--native-output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=307)
    parser.add_argument("--require-rundown", action="store_true",
                        help="Require collector rundown and bracket native trials with exact process identity snapshots")
    args = parser.parse_args(argv)
    capture = args.capture_dir.resolve()
    output = args.native_output.resolve()
    ready = capture / "capture-ready.json"
    if os.name != "nt":
        parser.error("Windows is required")
    import ctypes
    if ctypes.windll.shell32.IsUserAnAdmin():
        parser.error("Run this workload unelevated; only the separate ETW collector needs elevation")
    if not ready.is_file() or (capture / "capture-status.json").exists():
        parser.error("A currently ready ETW capture is required")
    if output.exists() or (capture / "canary-ground-truth.json").exists():
        parser.error("Use fresh output paths; existing evidence is never overwritten")
    ready_data = json.loads(ready.read_text(encoding="utf-8-sig"))
    if args.require_rundown and ready_data.get("request_rundown") is not True:
        parser.error("Rundown validation requires a collector started with rundown enabled")
    import psutil
    collector = psutil.Process(ready_data["collector_pid"])
    recorded_creation = datetime.fromisoformat(ready_data["collector_created_utc"].replace("Z", "+00:00")).timestamp()
    if abs(collector.create_time() - recorded_creation) > 0.01:
        parser.error("Capture marker refers to a different collector process identity")
    age = time.time() - datetime.fromisoformat(ready_data["ready_utc"].replace("Z", "+00:00")).timestamp()
    if ready_data.get("status") != "recording" or not -1 <= age <= 120:
        parser.error("Capture must be recording and have become ready within the last two minutes")
    if (capture / "stop.request").exists():
        parser.error("Capture is already stopping")
    records = []
    ground = {"schema_version": 1, "source": "known-subprocess-launch-and-wait",
              "started_utc": now(), "controller_pid": os.getpid(),
              "worker_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "capture_ready_sha256": hashlib.sha256(ready.read_bytes()).hexdigest(),
              "capture_session": ready_data.get("session_name"), "canaries": records,
              "status": "running", "native_manifest": str(output / "manifest.json")}
    if args.require_rundown:
        ground.update({"require_rundown": True, "rundown_identity_snapshots": []})
    ground_path = capture / "canary-ground-truth.json"
    write_json(ground_path, ground)
    returncode = 1
    try:
        for phase in ("before-native", "after-native"):
            print(f"CANARIES: {phase}", flush=True)
            for index in range(12):
                records.append(simple_canary(phase, index))
                write_json(ground_path, ground)
            records.extend(nested_canary(phase))
            write_json(ground_path, ground)
            if any(row["actual_exit_code"] != row["expected_exit_code"] for row in records):
                raise RuntimeError("Canary exit mismatch")
            if phase == "before-native":
                if args.require_rundown:
                    ground["rundown_identity_snapshots"].append(collect_rundown_snapshot("before-native"))
                    write_json(ground_path, ground)
                ground["native_started_utc"] = now()
                write_json(ground_path, ground)
                print("NATIVE VALIDATION: one fixed/contextual pair, normal timing", flush=True)
                native_exit = run_native_guarded(capture, output, args.seed, ready_data, collector)
                ground["native_finished_utc"] = now()
                ground["native_exit_code"] = native_exit
                write_json(ground_path, ground)
                if args.require_rundown:
                    ground["rundown_identity_snapshots"].append(collect_rundown_snapshot("after-native"))
                    write_json(ground_path, ground)
                if native_exit:
                    raise RuntimeError("Native validation failed; attempted evidence retained")
        ground["status"] = "completed"
        returncode = 0
    except BaseException as exc:
        ground["status"] = "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
        ground["error_type"] = type(exc).__name__
        ground["error"] = str(exc)
        print(str(exc), file=sys.stderr, flush=True)
    finally:
        ground["finished_utc"] = now()
        write_json(ground_path, ground)
        # Capture remains alive briefly after the last wait to include delivery
        # and cleanup; stopping flushes ETW buffers. This is not a loss guarantee.
        time.sleep(2)
        (capture / "stop.request").touch(exist_ok=True)
        print("Requested capture stop. Verify final loss counters and decoded events before claiming success.", flush=True)
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())
