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
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
CANARY_PYTHON = getattr(sys, "_base_executable", sys.executable)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


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
                ground["native_started_utc"] = now()
                write_json(ground_path, ground)
                print("NATIVE VALIDATION: one fixed/contextual pair, normal timing", flush=True)
                native_exit = run_native_guarded(capture, output, args.seed, ready_data, collector)
                ground["native_finished_utc"] = now()
                ground["native_exit_code"] = native_exit
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
