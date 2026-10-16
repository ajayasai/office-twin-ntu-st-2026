"""Cancellation-aware coordinator with a durable evidence trail on every outcome."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path
import threading
import time
import uuid

from .evidence import EvidenceRecorder
from .report import generate_report
from .timing import TimingPolicy


class RunCancelled(RuntimeError):
    pass


@dataclass
class RunConfig:
    mode: str = "simulate"
    timing: str = "contextual"
    seed: int = 42
    scale: float = 1.0
    workflow: str = "notepad"
    output: str = str(Path(__file__).resolve().parent.parent / "runs")
    sheet_url: str = ""
    scenario: str = ""

    def validate(self):
        if self.mode not in {"simulate", "desktop"}:
            raise ValueError("Mode must be simulate or desktop")
        if self.workflow not in {"office", "notepad", "sheets"}:
            raise ValueError("Unknown workflow")
        if self.mode == "desktop" and self.workflow == "sheets" and not self.sheet_url:
            raise ValueError("A dedicated Google Sheet URL is required for the Sheets workflow")
        if not 0 <= self.scale <= 10:
            raise ValueError("Timing scale must be between 0 and 10")
        TimingPolicy(mode=self.timing, seed=self.seed, scale=self.scale)
        if self.scenario and not Path(self.scenario).is_file():
            raise ValueError("Scenario JSON file does not exist")


def run(config: RunConfig, cancel=None, on_event=None):
    config.validate()
    cancel = cancel or threading.Event()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    run_dir = Path(config.output).expanduser().resolve() / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    recorder = EvidenceRecorder(run_dir)
    policy = TimingPolicy(mode=config.timing, seed=config.seed, scale=config.scale)
    backend = None
    trace = None
    summary = {"run_id": run_id, "backend": "simulation" if config.mode == "simulate" else "desktop",
               "config": asdict(config), "timing": policy.metadata(), "status": "starting",
               "success": False, "steps_completed": 0, "run_directory": str(run_dir),
               "limitations": ["Agent event logs are self-reported, not independent Sysmon evidence.",
                               policy.metadata()["calibration"],
                               "Requested delays do not verify delivered key intervals or key-hold durations.",
                               "No claim of human indistinguishability is made."]}

    def emit(event):
        recorder.emit(event)
        if on_event:
            try:
                on_event(dict(event))
            except Exception as exc:
                summary.setdefault("observer_errors", []).append(str(exc))

    def pause(kind, units=1):
        if cancel.is_set():
            raise RunCancelled("Run stopped by user")
        seconds = policy.sample(kind, units)
        started = time.perf_counter()
        interrupted = cancel.wait(seconds)
        emit({"event": "timing", "kind": kind, "units": units, "delay_seconds": seconds,
              "actual_wait_seconds": time.perf_counter() - started,
              "interrupted": interrupted})
        if interrupted:
            raise RunCancelled("Run stopped by user")

    try:
        recorder.start()
        if config.mode == "desktop":
            from .process_trace import ProcessTrace
            trace = ProcessTrace(run_dir).start()
        emit({"event": "run_started", "mode": config.mode, "workflow": config.workflow,
              "seed": config.seed, "timing": config.timing})
        if config.mode == "simulate":
            from .simulation import SimulationDesktop
            backend_type = SimulationDesktop
        elif config.workflow == "sheets":
            from .sheets import GoogleSheetsDesktop
            backend_type = GoogleSheetsDesktop
        else:
            from .desktop import WindowsDesktop
            backend_type = WindowsDesktop
        kwargs = {"workspace": run_dir / "workspace", "cancel": cancel,
                  "emit": emit, "pause": pause, "workflow": config.workflow}
        if config.workflow == "sheets" and config.mode == "desktop":
            kwargs["sheet_url"] = config.sheet_url
        if config.scenario:
            kwargs["scenario_path"] = Path(config.scenario)
        backend = backend_type(**kwargs)
        bundle = backend.prepare()
        steps = bundle["steps"]
        summary["steps_total"] = len(steps)
        summary["artifacts"] = {str(k): str(v) for k, v in bundle.get("paths", {}).items()}
        summary["task_model"] = bundle.get("task_model", "Recipe-driven synthetic task")
        if bundle.get("paths", {}).get("scenario"):
            summary["scenario_sha256"] = hashlib.sha256(Path(bundle["paths"]["scenario"]).read_bytes()).hexdigest()
        if config.mode == "desktop":
            emit({"event": "countdown", "label": "Desktop run starts in 5 seconds. Escape stops input."})
            if cancel.wait(5):
                raise RunCancelled("Cancelled before desktop input")
        for i, step in enumerate(steps):
            if cancel.is_set():
                raise RunCancelled("Run stopped by user")
            emit({"event": "step_started", "step_id": step["id"], "label": step["label"],
                  "index": i + 1, "total": len(steps), "kind": step.get("kind", "think")})
            result = backend.run_step(step)
            summary["steps_completed"] += 1
            emit({"event": "step_completed", "step_id": step["id"], "result": result,
                  "index": i + 1, "total": len(steps)})
        verification = backend.verify()
        summary["verification"] = verification
        verified = verification.get("success", verification.get("passed", verification.get("ok", False)))
        summary["success"] = bool(verified)
        summary["status"] = ("plan_completed" if config.mode == "simulate" else "completed") if verified else "verification_failed"
        if not verified:
            summary["error"] = "Output verification did not pass; inspect verification details."
        emit({"event": "verification", "result": verification})
    except Exception as exc:
        summary["status"] = "cancelled" if cancel.is_set() or isinstance(exc, RunCancelled) else "failed"
        summary["error"] = str(exc)
        emit({"event": "run_error", "error_type": type(exc).__name__, "message": str(exc)})
    finally:
        if backend:
            try:
                backend.close()
            except Exception as exc:
                summary["cleanup_error"] = str(exc)
        emit({"event": "run_finished", "status": summary["status"], "success": summary["success"]})
        if trace:
            summary["process_trace"] = trace.stop()
        summary["timing"] = policy.metadata()
        summary["resources"] = recorder.stop()
        (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        try:
            summary["report_path"] = str(generate_report(run_dir))
        except Exception as exc:
            summary["report_error"] = str(exc)
        (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary
