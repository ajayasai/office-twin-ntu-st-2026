"""Record a consenting participant's manual task boundaries and scoped resources.

No desktop automation, key hooks, screen capture, window titles, URLs, file
activity, or typed task content are collected. Console commands are voluntary
markers, not evidence of delivered desktop actions or task correctness.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
import uuid

try:
    import psutil
except ImportError:
    psutil = None


TASK_PROCESSES = {"chrome.exe", "msedge.exe", "firefox.exe", "notepad.exe", "excel.exe", "winword.exe"}
MARKERS = {"brief-reviewed", "quotes-reviewed", "spreadsheet-saved", "report-saved", "interruption"}
OUTCOMES = {"completed-unverified", "incomplete", "aborted"}


def _label(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", value):
        raise ValueError("Use a short anonymous label containing only letters, digits, underscore, or hyphen.")
    return value


class ManualRecorder:
    def __init__(self, directory: Path, participant: str, pids=(), *,
                 include_descendants: bool = False, interval: float = 0.5,
                 task: str = "office-twin-sheets-default", scenario_sha256: str | None = None):
        self.directory = Path(directory)
        self.participant, self.task = _label(participant), _label(task)
        self.pids = sorted(set(pids))
        if any(type(pid) is not int or pid <= 0 for pid in self.pids):
            raise ValueError("Selected process IDs must be positive integers.")
        if not 0.1 <= interval <= 10:
            raise ValueError("Sample interval must be between 0.1 and 10 seconds.")
        if psutil is None and self.pids:
            raise RuntimeError("Install requirements.txt to sample selected application processes.")
        self.include_descendants, self.interval = include_descendants, interval
        self.scenario_sha256 = scenario_sha256
        self._roots, self._observed = {}, {}
        self._started = self._cpu_start = None
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._summary = None
        self._peak_rss = None
        self._read_errors = 0
        self._markers = []

    def _event(self, event: str, **details) -> None:
        record = {"event": event, "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                  "elapsed_seconds": time.perf_counter() - self._started,
                  "source": "manual_reference_collector", **details}
        with self._lock:
            with (self.directory / "manual-events.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, allow_nan=False) + "\n")

    def start(self) -> None:
        if self._started is not None:
            raise RuntimeError("This recorder has already started; use a new recorder for each attempt.")
        # Bind PID + creation time before the clock starts. Never follow a reused
        # PID into an unrelated process, and never select processes by name alone.
        if psutil:
            for pid in self.pids:
                proc = psutil.Process(pid)
                name = proc.name()
                if name.lower() not in TASK_PROCESSES:
                    raise ValueError(f"PID {pid} is not a supported task application. Select the browser, Notepad, Excel, or Word PID.")
                self._roots[pid] = {"pid": pid, "name": name, "create_time": proc.create_time()}
        self.directory.mkdir(parents=True, exist_ok=False)
        self._cpu_start = time.process_time()
        self._started = time.perf_counter()
        self._event("start", participant_id=self.participant, task_id=self.task,
                    selected_processes=list(self._roots.values()),
                    descendants_included=self.include_descendants,
                    participant_declaration="Participant voluntarily started a manual attempt; no task input is injected by this collector.")
        self._sample()
        if psutil:
            self._thread = threading.Thread(target=self._monitor, daemon=True, name="manual-resource-sampler")
            self._thread.start()

    def _monitor(self) -> None:
        while not self._stop.wait(self.interval):
            self._sample()

    def _sample(self) -> None:
        if psutil is None:
            return
        candidates = {}
        for pid, root in self._roots.items():
            try:
                proc = psutil.Process(pid)
                if proc.create_time() != root["create_time"]:
                    continue
                candidates[(pid, root["create_time"])] = (proc, "explicitly selected PID")
                if self.include_descendants:
                    for child in proc.children(recursive=True):
                        candidates.setdefault((child.pid, child.create_time()), (child, "descendant of selected PID"))
            except psutil.Error:
                self._read_errors += 1
        snapshot = []
        for (pid, created), (proc, selection) in candidates.items():
            try:
                with proc.oneshot():
                    # Recheck the identity at the read boundary as well.
                    if proc.create_time() != created:
                        continue
                    cpu, memory, name = proc.cpu_times(), proc.memory_info(), proc.name()
                total_cpu, rss = float(cpu.user + cpu.system), int(memory.rss)
                elapsed = time.perf_counter() - self._started
                record = self._observed.setdefault((pid, created), {
                    "pid": pid, "name": name, "create_time": created, "selection": selection,
                    "first_observed_seconds": elapsed, "cpu_first_seconds": total_cpu,
                    "cpu_last_seconds": total_cpu, "peak_sampled_rss_bytes": rss, "samples": 0,
                })
                record["last_observed_seconds"] = elapsed
                record["cpu_last_seconds"] = max(record["cpu_last_seconds"], total_cpu)
                record["peak_sampled_rss_bytes"] = max(record["peak_sampled_rss_bytes"], rss)
                record["samples"] += 1
                snapshot.append({"pid": pid, "create_time": created, "name": name,
                                 "cpu_total_seconds": total_cpu, "rss_bytes": rss, "selection": selection})
            except psutil.Error:
                self._read_errors += 1
        collector_rss = None
        try:
            collector_rss = psutil.Process(os.getpid()).memory_info().rss
            self._peak_rss = max(self._peak_rss or 0, collector_rss)
        except psutil.Error:
            self._read_errors += 1
        self._event("resource_sample", processes=snapshot, collector_rss_bytes=collector_rss)

    def mark(self, marker: str) -> None:
        if self._started is None or self._summary is not None:
            raise RuntimeError("Markers require an active manual recording.")
        if marker not in MARKERS:
            raise ValueError("Use a predefined task marker; arbitrary typed content is not collected.")
        self._markers.append({"marker": marker, "elapsed_seconds": time.perf_counter() - self._started})
        self._event("participant_marker", marker=marker, interpretation="Participant-reported phase boundary; not independently verified.")

    def stop(self, outcome: str = "completed-unverified") -> dict:
        if outcome not in OUTCOMES:
            raise ValueError("Unknown manual outcome.")
        if self._summary is not None:
            return self._summary
        if self._started is None:
            raise RuntimeError("The manual recording has not started.")
        self._stop.set()
        if self._thread:
            self._thread.join()
        self._sample()
        elapsed = time.perf_counter() - self._started
        cpu = time.process_time() - self._cpu_start
        processes = []
        for record in self._observed.values():
            processes.append({**record, "observed_cpu_delta_seconds": max(0, record["cpu_last_seconds"] - record["cpu_first_seconds"])})
        self._summary = {
            "record_type": "participant_reported_manual_reference", "participant_id": self.participant,
            "task_id": self.task, "scenario_sha256": self.scenario_sha256,
            "outcome": outcome, "task_success_verified": False, "human_provenance_independently_verified": False,
            "elapsed_seconds": elapsed, "markers": self._markers,
            "resources": {"sample_interval_seconds": self.interval if psutil else None,
                          "collector_cpu_seconds": cpu, "collector_peak_sampled_rss_bytes": self._peak_rss,
                          "selected_processes": list(self._roots.values()),
                          "include_descendants": self.include_descendants,
                          "process_observations": processes, "process_read_errors": self._read_errors},
            "collection_scope": "Explicit start/stop and optional task markers; selected PID/creation-time resource snapshots only. No task keystrokes, mouse actions, windows, URLs, screenshots, files, or security logs are recorded.",
            "limitations": [
                "Manual participation and phase markers are participant declarations, not automated proof of human activity or task correctness.",
                "Task elapsed time includes switching to this console to enter start, markers, and stop; optional markers add overhead.",
                "Selected application processes can include other documents, tabs, or background work; their CPU is not exclusively attributable to this task.",
                "CPU is user plus kernel CPU-seconds between first and last observed samples, not a core-normalized utilization percentage.",
                "Samples miss short-lived activity and transient memory peaks; child processes are included only when explicitly requested.",
                "Collector CPU/RSS is separate from application resources and is not equivalent to agent-controller cost.",
                "This collection provides no keystroke/action interval distribution or independent Windows process-event trace.",
            ],
        }
        self._event("stop", participant_reported_outcome=outcome, elapsed_seconds=elapsed)
        (self.directory / "manual-summary.json").write_text(json.dumps(self._summary, indent=2), encoding="utf-8")
        return self._summary


def _process_options() -> None:
    if psutil is None:
        raise RuntimeError("Install requirements.txt to list task application PIDs.")
    print("PID       Application (no titles, commands, or paths collected)")
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if (proc.info["name"] or "").lower() in TASK_PROCESSES:
                print(f'{proc.info["pid"]:<9} {proc.info["name"]}')
        except psutil.Error:
            continue


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant", help="Anonymous participant label, e.g. P01")
    parser.add_argument("--task", default="office-twin-sheets-default", help="Short synthetic task identifier")
    parser.add_argument("--pid", type=int, action="append", default=[], help="Explicit task application PID; repeat for more than one")
    parser.add_argument("--include-descendants", action="store_true", help="Also sample descendants; browser descendants can include unrelated tabs")
    parser.add_argument("--interval", type=float, default=0.5, help="Resource sampling interval in seconds")
    parser.add_argument("--scenario", type=Path, help="Optional task JSON; record its SHA-256 digest only")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "runs" / "manual")
    parser.add_argument("--list-processes", action="store_true", help="Print task application names/PIDs and exit; does not start recording")
    args = parser.parse_args(argv)
    if args.list_processes:
        _process_options()
        return 0
    if not args.participant:
        parser.error("--participant is required for a manual recording")
    digest = None
    if args.scenario:
        with args.scenario.open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    recorder = ManualRecorder(args.output / run_id, args.participant, args.pid,
                              include_descendants=args.include_descendants, interval=args.interval,
                              task=args.task, scenario_sha256=digest)
    print("Only a consenting person should perform this reference task. This tool injects no desktop input.")
    print("Use a synthetic task and anonymous participant ID. Only explicitly selected PIDs are sampled.")
    print("No selected PIDs means elapsed time plus collector overhead only; application costs stay unavailable.")
    print("Prepare the blank task inputs and apps first. Type start when ready; any other response exits without recording.")
    try:
        if input("> ").strip().lower() != "start":
            return 0
        recorder.start()
        print("Recording. Perform the task manually. Commands: stop, incomplete, abort, or mark <phase>.")
        print("Optional phases: " + ", ".join(sorted(MARKERS)))
        while True:
            command = input("> ").strip().lower()
            if command in {"stop", "incomplete", "abort"}:
                outcome = {"stop": "completed-unverified", "incomplete": "incomplete", "abort": "aborted"}[command]
                break
            if command.startswith("mark ") and command[5:] in MARKERS:
                recorder.mark(command[5:])
            else:
                print("Use stop, incomplete, abort, or one of the predefined mark phases. Other text is not saved.")
    except (KeyboardInterrupt, EOFError):
        if recorder._started is None:
            return 0
        outcome = "aborted"
    summary = recorder.stop(outcome)
    print(f'Recorded {summary["elapsed_seconds"]:.2f} seconds; outcome: {outcome}. Output correctness is unverified.')
    print(recorder.directory / "manual-summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
