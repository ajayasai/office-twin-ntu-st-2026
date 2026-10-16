"""Counterbalanced native timing trials with an independent observer process.

Local settings and raw evidence remain private. This tool does not collect a
human baseline and does not make the shared desktop an isolated laboratory.
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
sys.path.insert(0, str(ROOT))


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def code_digest(root=ROOT):
    """Hash runtime sources; docs and new measurements cannot change this ID."""
    digest = hashlib.sha256()
    for path in sorted((root / "office_twin").glob("*.py")):
        digest.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def measurement_digest(root=ROOT):
    """Include the measurement harness and external collector implementation."""
    digest = hashlib.sha256()
    paths = list((root / "office_twin").glob("*.py"))
    paths.extend(root / "tools" / name for name in ("run_benchmark.py", "observe_run.py"))
    for path in sorted(paths):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()


def validate_observer(data, returncode, controller_identity, minimum_duration):
    """A completed worker alone is not a successful telemetry capture."""
    if returncode != 0 or data.get("status") != "completed" or data.get("stop_reason") != "stop_file":
        raise RuntimeError("External observer did not complete through the requested stop marker")
    if data.get("controller_identity") != controller_identity:
        raise RuntimeError("External observer did not bind the launched controller identity")
    if data.get("duration_seconds", 0) < minimum_duration or data.get("snapshot_count", 0) < 2:
        raise RuntimeError("External observer coverage is shorter than the controller interval")
    if data.get("scopes", {}).get("controller", {}).get("process_count", 0) != 1:
        raise RuntimeError("External observer did not sample the bound controller")


def cleanup_targets(summary, events):
    """Derive only owned application windows; never select the Sheet window."""
    report_name = Path(summary.get("artifacts", {}).get("txt", "")).name
    match = re.fullmatch(r"OfficeTwin-([0-9a-f]{8})-recommendation\.txt", report_name)
    if not match:
        raise RuntimeError("Cannot identify this run's owned cleanup token")
    token = match.group(1)
    markers = {"browser": f"OfficeTwin {token}", "explorer": f"OfficeTwin-launch-{token}",
               "notepad": report_name.removesuffix(".txt")}
    targets = {}
    for event in events:
        app = event.get("app")
        if event.get("event") == "window_focus" and app in markers:
            if markers[app].lower() not in str(event.get("title", "")).lower():
                raise RuntimeError("Run focus evidence does not match its cleanup token")
            targets[app] = {**event, "marker": markers[app]}
    if set(targets) != set(markers):
        raise RuntimeError("Missing focus evidence for owned cleanup windows")
    if len({target["hwnd"] for target in targets.values()}) != len(targets):
        raise RuntimeError("Owned cleanup window handles are ambiguous")
    return targets


def cleanup_owned_windows(summary_path):
    """Close exact owned windows/report tab after measurement; stop on ambiguity."""
    import psutil
    import win32con
    import win32gui
    import win32process
    from pywinauto import Desktop, keyboard
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    events = [json.loads(line) for line in (summary_path.parent / "events.jsonl").read_text(encoding="utf-8").splitlines() if line]
    targets = cleanup_targets(summary, events)
    expected_names = {"browser": "chrome.exe", "explorer": "explorer.exe", "notepad": "notepad.exe"}
    records = []
    # Close the active saved report tab first; unrelated Notepad tabs remain.
    for app in ("notepad", "browser", "explorer"):
        target = targets[app]
        hwnd, pid = int(target["hwnd"]), int(target["pid"])
        if not win32gui.IsWindow(hwnd):
            records.append({"app": app, "status": "already_closed"})
            continue
        def validate():
            if win32process.GetWindowThreadProcessId(hwnd)[1] != pid:
                raise RuntimeError("Cleanup window PID changed; refusing to close it")
            process = psutil.Process(pid)
            event_time = datetime.fromisoformat(target["timestamp_utc"]).timestamp()
            if process.name().lower() != expected_names[app] or process.create_time() > event_time:
                raise RuntimeError("Cleanup process identity changed; refusing to close it")
            title = win32gui.GetWindowText(hwnd)
            if target["marker"].lower() not in title.lower() or title.startswith("*"):
                raise RuntimeError("Cleanup window title changed or has unsaved edits; refusing to close it")
        validate()
        window = Desktop(backend="uia").window(handle=hwnd).wrapper_object()
        if app == "notepad":
            window.set_focus()
            validate()
            if win32gui.GetForegroundWindow() != hwnd:
                raise RuntimeError("Cannot focus the saved report tab for cleanup")
            keyboard.send_keys("^w", pause=0)
        else:
            # A new user tab must never be closed as part of a benchmark.
            tabs = window.descendants(control_type="TabItem")
            if (app == "browser" and len(tabs) != 1) or (app == "explorer" and len(tabs) > 1):
                raise RuntimeError("Owned window has ambiguous/additional tabs; refusing window cleanup")
            validate()
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        deadline = time.monotonic() + 5
        while win32gui.IsWindow(hwnd) and target["marker"].lower() in win32gui.GetWindowText(hwnd).lower():
            if time.monotonic() >= deadline:
                raise RuntimeError("Owned window/tab did not close; benchmark stopped")
            time.sleep(0.05)
        records.append({"app": app, "status": "closed_owned_tab" if app == "notepad" else "closed_owned_window"})
    return records


def trial_order(seeds):
    return [(index + 1, seed, mode)
            for index, seed in enumerate(seeds)
            for mode in (("fixed", "contextual") if index % 2 == 0 else ("contextual", "fixed"))]


def wait_ready(path, process, timeout=20):
    deadline = time.monotonic() + timeout
    while not Path(path).exists():
        if process.poll() is not None:
            raise RuntimeError("Process exited before its ready handshake; inspect trial logs")
        if time.monotonic() >= deadline:
            raise TimeoutError("Process did not complete its ready handshake")
        time.sleep(0.05)


def worker(config_path):
    from office_twin.runner import RunConfig, run
    import psutil
    # On Windows a venv launcher PID can differ from the real interpreter.
    # This process declares its own identity before any native input begins.
    write_json(Path(config_path).parent / "controller-identity.json",
               {"pid": os.getpid(), "create_time": psutil.Process().create_time()})
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    result = run(RunConfig(**config), on_event=lambda event: (
        print(json.dumps({key: event[key] for key in ("event", "step_id", "index", "total") if key in event}), flush=True)
        if event["event"] in {"step_started", "step_completed", "run_error"} else None))
    print(json.dumps({"status": result["status"], "run_directory": result["run_directory"]}), flush=True)
    return 0 if result["success"] else 1


def terminate_worker(launcher, identity_file, identity_key=None):
    """Stop the worker interpreter as well as its optional Windows launcher."""
    import psutil
    try:
        declared = json.loads(identity_file.read_text(encoding="utf-8"))
        if identity_key:
            declared = declared[identity_key]
        actual = psutil.Process(declared["pid"])
        if actual.pid != os.getpid() and actual.create_time() == declared["create_time"]:
            actual.terminate()
            try:
                actual.wait(timeout=5)
            except psutil.TimeoutExpired:
                actual.kill()
                actual.wait(timeout=5)
    except (OSError, ValueError, KeyError, psutil.Error):
        pass
    if launcher.poll() is None:
        launcher.terminate()
        try:
            launcher.wait(timeout=5)
        except subprocess.TimeoutExpired:
            launcher.kill()
            launcher.wait(timeout=5)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--settings", type=Path, default=ROOT / "local-settings.json")
    parser.add_argument("--seeds", type=int, nargs="+", default=[211, 223, 227, 229, 233])
    parser.add_argument("--mode", choices=["desktop", "simulate"], default="desktop")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--baseline-seconds", type=float, default=3.0)
    args = parser.parse_args(argv)
    if args.worker:
        return worker(args.worker)
    if not args.output:
        parser.error("--output is required")
    if len(set(args.seeds)) != len(args.seeds):
        parser.error("Seeds must be unique")
    if not 0 <= args.baseline_seconds <= 60:
        parser.error("Baseline must be between 0 and 60 seconds")
    settings = json.loads(args.settings.read_text(encoding="utf-8"))
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    runtime_digest = code_digest()
    collector_digest = measurement_digest()
    manifest = {
        "source_commit": commit, "runtime_sha256": runtime_digest, "measurement_sha256": collector_digest,
        "source_worktree_dirty_at_start": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "environment_id": "same-windows-session-warm-shared-apps",
        "capture_condition": "separate-0.1s-process-observer; no screen recording",
        "condition_notes": [
            "Same default scenario, scale, signed-in Chrome profile and machine for all trials.",
            "Counterbalanced order across seed pairs; application state is warm and shared.",
            "Background tabs and unrelated application activity are not isolated.",
            "Each run resets the owned Sheet range and creates a fresh report file.",
            "After measurement, only validated run-owned supplier/Explorer windows and the saved report tab are closed; the Sheet window remains warm.",
            "Human reference n=0; comparison measures automated policies only.",
            "Stops at the first failed run; failures remain in this manifest."
        ],
        "planned": [{"pair_id": f"seed{seed}", "seed": seed, "timing": mode} for _, seed, mode in trial_order(args.seeds)],
        "runs": [], "status": "running",
    }
    manifest_path = output / "manifest.json"
    write_json(manifest_path, manifest)
    hidden = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    try:
        for number, (pair_index, seed, mode) in enumerate(trial_order(args.seeds), 1):
            if code_digest() != runtime_digest or measurement_digest() != collector_digest:
                raise RuntimeError("Runtime or measurement sources changed; refusing to mix versions")
            trial = output / f"{number:02d}-{mode}-{seed}"
            trial.mkdir()
            observer_dir = trial / "observer"
            identity_file = trial / "controller-identity.json"
            stop_file = trial / "observer.stop"
            config_path = trial / "config-private.json"
            write_json(config_path, {"mode": args.mode, "workflow": "sheets", "timing": mode,
                                    "seed": seed, "scale": args.scale, "output": str(trial / "runs"),
                                    "sheet_url": settings["sheet_url"]})
            entry = {"path": str((trial / "runs").relative_to(output)),
                     "observer_path": str(observer_dir.relative_to(output)),
                     "observer_summary": str((observer_dir / "external-observer-summary.json").relative_to(output)),
                     "pair_id": f"seed{seed}", "order": number, "seed": seed, "timing": mode,
                     "backend": args.mode, "workflow": "sheets", "scale": args.scale,
                     "source_commit": commit, "runtime_sha256": runtime_digest,
                     "measurement_sha256": collector_digest, "status": "started", "success": False,
                     "attempt_status": "started", "started_utc": datetime.now(timezone.utc).isoformat()}
            manifest["runs"].append(entry)
            write_json(manifest_path, manifest)
            print(f"TRIAL {number}/{len(args.seeds)*2}: {mode}, seed {seed}", flush=True)
            try:
                with (trial / "observer.log").open("w", encoding="utf-8") as observer_log:
                    observer = subprocess.Popen([sys.executable, str(ROOT / "tools" / "observe_run.py"),
                        "--output", str(observer_dir), "--controller-file", str(identity_file),
                        "--stop-file", str(stop_file), "--interval", "0.1",
                        "--duration", str(570 + args.baseline_seconds + 45)],
                        cwd=ROOT, stdout=observer_log, stderr=subprocess.STDOUT, creationflags=hidden)
                    try:
                        wait_ready(observer_dir / "observer-ready.json", observer)
                        time.sleep(args.baseline_seconds)
                        with (trial / "controller.log").open("w", encoding="utf-8") as controller_log:
                            controller_started = time.monotonic()
                            controller = subprocess.Popen([sys.executable, "-u", str(Path(__file__).resolve()),
                                "--worker", str(config_path)], cwd=ROOT, stdout=controller_log,
                                stderr=subprocess.STDOUT, creationflags=hidden)
                            try:
                                wait_ready(identity_file, controller)
                                controller_identity = json.loads(identity_file.read_text(encoding="utf-8"))
                                returncode = controller.wait(timeout=570)
                            finally:
                                # Stop only our exact worker; never kill application cohorts.
                                if controller.poll() is None:
                                    terminate_worker(controller, identity_file)
                            controller_duration = time.monotonic() - controller_started
                            entry["controller_exit_code"] = returncode
                        time.sleep(1.0)
                    finally:
                        stop_file.touch()
                        try:
                            observer.wait(timeout=15)
                        except subprocess.TimeoutExpired:
                            terminate_worker(observer, observer_dir / "observer-ready.json", "observer_identity")
                        entry["observer_exit_code"] = observer.returncode
                summaries = list((trial / "runs").glob("*/summary.json"))
                if len(summaries) != 1:
                    raise RuntimeError("Missing or ambiguous run summary; attempted failure retained")
                summary_path = summaries[0]
                summary = json.loads(summary_path.read_text(encoding="utf-8"))
                entry.update({"path": str(summary_path.parent.relative_to(output)),
                              "status": summary["status"], "success": summary["success"]})
                external = observer_dir / "external-observer-summary.json"
                if not external.is_file():
                    raise RuntimeError("External observer summary missing; telemetry capture failed")
                external_data = json.loads(external.read_text(encoding="utf-8"))
                (summary_path.parent / external.name).write_bytes(external.read_bytes())
                validate_observer(external_data, observer.returncode, controller_identity, controller_duration)
                entry["telemetry_validated"] = True
                print(json.dumps({"trial": number, "status": summary["status"],
                                  "steps": summary["steps_completed"],
                                  "wall_seconds": summary["resources"]["wall_seconds"]}), flush=True)
                if returncode or not summary["success"]:
                    raise RuntimeError("Native trial failed; stopped remaining trials")
                entry["cleanup"] = cleanup_owned_windows(summary_path) if args.mode == "desktop" else []
                entry["attempt_status"] = "completed"
            except BaseException as exc:
                entry["attempt_status"] = "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
                if entry["status"] == "started":
                    entry["status"] = "failed"
                entry["error_type"] = type(exc).__name__
                entry["error"] = str(exc)
                raise
            finally:
                entry["finished_utc"] = datetime.now(timezone.utc).isoformat()
                write_json(manifest_path, manifest)
        manifest["status"] = "completed"
        return 0
    except Exception as exc:
        manifest["status"] = "stopped"
        manifest["error"] = str(exc)
        print(str(exc), file=sys.stderr, flush=True)
        return 1
    except KeyboardInterrupt:
        manifest["status"] = "interrupted"
        return 130
    finally:
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(manifest_path, manifest)


if __name__ == "__main__":
    raise SystemExit(main())
