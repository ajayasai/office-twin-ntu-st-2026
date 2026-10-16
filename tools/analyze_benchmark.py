"""Analyze fixed/contextual runs without exporting paths, URLs or raw events.

python tools/analyze_benchmark.py --manifest runs/benchmark/manifest.json --output dist/benchmark
python tools/analyze_benchmark.py RUN_DIR RUN_DIR --output dist/benchmark

Manifest paths are relative to the manifest. Optional top-level defaults are
source_commit, environment_id and capture_condition; each run may override them.
Use pair_id to explicitly associate attempts (including failed attempts).
Metadata in the manifest is an operator declaration, not verified provenance.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import statistics


KINDS = frozenset({"key", "read", "think", "switch", "review", "correction", "click", "move", "scroll", "action"})
LIMITATIONS = [
    "No human participant or human reference data was collected. Timing variation is not evidence of human similarity.",
    "No official score, winning probability, statistical significance or population reliability is inferred.",
    "Matching source version, environment and capture metadata is based on operator declarations, not independent verification.",
    "Task interval runs from the first step start through the final step completion; it excludes preparation, countdown, final verification and cleanup.",
    "Requested delays and measured controller waits are not measurements of native input delivery; application waits are not fully captured by timing events.",
    "Controller CPU and sampled peak RSS cover the full recorder window, not just the task interval, and exclude application resource use.",
    "Process observations are limited samples and may miss processes or peaks; named applications may include unrelated work.",
    "The declared environment may reuse warm, shared Chrome/Notepad processes; background activity is not assumed isolated.",
    "Repeated timing events within one run are correlated observations, not independent experimental replicates.",
    "A fixed/contextual comparison can measure the effect of the chosen timing policy; it cannot validate human authenticity.",
]


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) and value >= 0 else None
    except (TypeError, ValueError, OverflowError):
        return None


def _integer(value):
    number = _number(value)
    return int(number) if number is not None and number.is_integer() else None


def _dict(value):
    return value if isinstance(value, dict) else {}


def _hash(value, minimum=64):
    return value.lower() if isinstance(value, str) and re.fullmatch(rf"[0-9a-fA-F]{{{minimum},64}}", value) else None


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest() if value not in (None, "") else None


def distribution(values):
    """Descriptive sample summary; p90 uses linear interpolation."""
    values = sorted(value for item in values if (value := _number(item)) is not None)
    if not values:
        return {"count": 0, "total_seconds": 0.0, "minimum_seconds": None, "median_seconds": None,
                "p90_seconds": None, "maximum_seconds": None, "mean_seconds": None, "sample_sd_seconds": None}
    position = (len(values) - 1) * 0.90
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return {"count": len(values), "total_seconds": sum(values), "minimum_seconds": values[0],
            "median_seconds": statistics.median(values),
            "p90_seconds": values[lower] + (values[upper] - values[lower]) * (position - lower),
            "maximum_seconds": values[-1], "mean_seconds": statistics.mean(values),
            "sample_sd_seconds": statistics.stdev(values) if len(values) > 1 else None}


def _read_json(path, warnings, label):
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(value, dict):
            raise ValueError("not an object")
        return value
    except (OSError, ValueError):
        warnings.append(f"{label} unavailable or malformed.")
        return {}


def _read_events(path, warnings):
    events = []
    try:
        with path.open(encoding="utf-8-sig") as stream:
            for line in stream:
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise ValueError("not an object")
                    events.append(value)
                except ValueError:
                    warnings.append("A malformed event was excluded.")
    except OSError:
        warnings.append("Event file unavailable.")
    return events


def _task_interval(events, total):
    start = next((event for event in events if event.get("event") == "step_started" and event.get("index") == 1), None)
    end = next((event for event in reversed(events) if event.get("event") == "step_completed" and total and event.get("index") == total), None)
    partial = next((event for event in reversed(events) if event.get("event") == "step_completed"), None)

    def elapsed(last):
        if not start or not last:
            return None
        for field in ("perf_counter", "elapsed_seconds"):
            a, b = _number(start.get(field)), _number(last.get(field))
            if a is not None and b is not None and b >= a:
                return b - a
        return None

    completed = {event.get("index") for event in events if event.get("event") == "step_completed" and isinstance(event.get("index"), int)}
    complete = bool(total and completed == set(range(1, total + 1)) and elapsed(end) is not None)
    return {"complete_step_sequence": complete, "task_seconds": elapsed(end) if complete else None,
            "partial_through_last_completed_step_seconds": elapsed(partial) if not complete else None,
            "definition": "First step_started through final step_completed; excludes final verification."}


def _timings(events):
    groups = defaultdict(lambda: {"requested": [], "actual": [], "completed_actual": [], "overrun": [], "interrupted": 0, "missing_actual": 0})
    signature = []
    for event in events:
        if event.get("event") != "timing":
            continue
        raw_kind = event.get("kind")
        kind = raw_kind if raw_kind in KINDS else "other"
        units = _integer(event.get("units"))
        if not units:
            units = None
        group = groups[(kind, units)]
        requested, actual = _number(event.get("delay_seconds")), _number(event.get("actual_wait_seconds"))
        signature.append((kind, units))
        if requested is not None:
            group["requested"].append(requested)
        if actual is not None:
            group["actual"].append(actual)
        else:
            group["missing_actual"] += 1
        if event.get("interrupted") is True:
            group["interrupted"] += 1
        elif actual is not None:
            group["completed_actual"].append(actual)
            if requested is not None:
                group["overrun"].append(max(0, actual - requested))
    result = []
    for (kind, units), values in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1] or 0)):
        result.append({"kind": kind, "units": units, "requested_wait": distribution(values["requested"]),
                       "actual_wait": distribution(values["actual"]), "uninterrupted_actual_wait": distribution(values["completed_actual"]),
                       "uninterrupted_nonnegative_overrun": distribution(values["overrun"]),
                       "interrupted_count": values["interrupted"], "missing_actual_count": values["missing_actual"]})
    return result, _digest(signature)


def _observer(path, entry, warnings):
    """Only explicitly selected numeric fields are exported; raw data stays local."""
    supplied = entry.get("observer_summary")
    supplied_path = Path(supplied) if supplied else None
    if supplied_path is not None and not supplied_path.is_absolute():
        supplied_path = path / supplied_path
    candidates = [supplied_path] if supplied_path else [path / name for name in ("external-observer-summary.json", "observer-summary.json", "process-observer-summary.json")]
    candidate = next((item for item in candidates if item.is_file()), None)
    if candidate is None:
        return {"present": False}
    data = _read_json(candidate, warnings, "External observer summary")
    recognized = data.get("evidence_source") == "external_process_snapshot_observer"
    result = {"present": True, "recognized_schema": recognized,
              "available": bool(recognized and (_number(data.get("snapshot_count")) or 0) > 0),
              "source": "Separate OS inventory and resource snapshot observer" if recognized else "Unrecognized separate observer summary",
              "process_start_event_trace": False, "human_reference": False}
    status = data.get("status")
    result["status"] = status if status in {"completed", "stopped", "failed", "running", "unavailable", "partial", "cancelled", "interrupted"} else "unspecified"
    reason = data.get("stop_reason")
    result["stop_reason"] = reason if reason in {"stop_file", "duration_limit", "keyboard_interrupt"} else "unspecified"
    fields = ("interval_seconds", "duration_seconds", "snapshot_count", "process_count", "read_error_count")
    for field in fields:
        value = _number(data.get(field))
        if value is not None:
            result[field] = value
    result["cadence"] = {field: _number(_dict(data.get("cadence")).get(field))
                         for field in ("median_gap_seconds", "max_gap_seconds", "overrun_count")}
    result["scopes"] = {}
    if recognized:
        for name in ("controller", "chrome", "notepad", "controller_descendants"):
            scope = _dict(_dict(data.get("scopes")).get(name))
            result["scopes"][name] = {field: _number(scope.get(field))
                                      for field in ("process_count", "observed_cpu_delta_seconds", "peak_sampled_rss_bytes", "single_sample_process_count")}
    result["observer_resources"] = {field: _number(_dict(data.get("observer_resources")).get(field))
                                    for field in ("cpu_seconds", "peak_sampled_rss_bytes")}
    result["limitations"] = ["Separate process sampling is not a Sysmon or ETW event stream and does not establish human similarity.",
                             "CPU covers first-to-last sampled observation per process identity; it may omit lifetime boundaries.",
                             "Scope RSS is the maximum simultaneous sum of sampled process RSS; shared memory can be counted more than once.",
                             "Application cohorts are nonexclusive and can include unrelated work; scopes may overlap and must not be added together.",
                             "Observer overhead is separate; no whole-system total is inferred."]
    return result


def load_run(path, entry, index):
    warnings = []
    for name in ("trial-metadata.json", "benchmark-metadata.json"):
        if (path / name).is_file():
            metadata = _read_json(path / name, warnings, "Trial metadata")
            entry = {**metadata, **{key: value for key, value in entry.items() if value is not None}}
            break
    summary = _read_json(path / "summary.json", warnings, "Summary")
    events = _read_events(path / "events.jsonl", warnings)
    config, timing, resources = (_dict(summary.get(name)) for name in ("config", "timing", "resources"))
    total = _integer(summary.get("steps_total"))
    interval = _task_interval(events, total)
    waits, action_signature = _timings(events)
    backend = summary.get("backend", config.get("mode", entry.get("backend")))
    backend = "simulation" if backend in {"simulate", "simulation"} else "desktop" if backend == "desktop" else "unknown"
    workflow = config.get("workflow", entry.get("workflow"))
    workflow = workflow if workflow in {"office", "notepad", "sheets"} else "unknown"
    policy = timing.get("mode", config.get("timing", entry.get("timing")))
    policy = policy if policy in {"fixed", "contextual"} else "unknown"
    status = summary.get("status", entry.get("status"))
    status = status if status in {"starting", "completed", "plan_completed", "verification_failed", "cancelled", "failed"} else "unknown"
    success = summary.get("success") is True
    if success and not interval["complete_step_sequence"]:
        warnings.append("Declared success lacks a complete timestamped step sequence.")
    provenance = _dict(summary.get("provenance"))
    version = entry.get("source_commit", summary.get("source_commit", provenance.get("source_commit")))
    source_hash = _hash(version, minimum=7)
    if source_hash is None:
        warnings.append("Source version is not supplied in a valid commit/hash form.")
    env = entry.get("environment_id", entry.get("environment", summary.get("environment_id")))
    capture = entry.get("capture_condition", entry.get("capture", summary.get("capture_condition")))
    if env in (None, ""):
        warnings.append("Environment/start-state condition is undeclared.")
    if capture in (None, ""):
        warnings.append("Capture condition is undeclared; missing recording metadata does not mean unrecorded.")
    scenario = _hash(summary.get("scenario_sha256", entry.get("scenario_sha256")))
    if scenario is None:
        # Read only the conventional owned fixture, never a summary-supplied absolute path.
        fixture = path / "workspace" / "scenario.json"
        if fixture.is_file():
            scenario = hashlib.sha256(fixture.read_bytes()).hexdigest()
    trace = _dict(summary.get("process_trace"))
    observer = _observer(path, entry, warnings)
    attempt = entry.get("attempt_status")
    attempt = attempt if attempt in {"started", "completed", "failed", "interrupted"} else "unspecified"
    return {"id": f"R{index:03d}", "backend": backend, "workflow": workflow, "policy": policy,
            "seed": _integer(timing.get("seed", config.get("seed", entry.get("seed")))), "scale": _number(timing.get("scale", config.get("scale", entry.get("scale")))),
            "source_commit": source_hash, "scenario_sha256": scenario,
            "runtime_sha256": _hash(entry.get("runtime_sha256")), "measurement_sha256": _hash(entry.get("measurement_sha256")),
            "environment_condition_sha256": _digest(env), "capture_condition_sha256": _digest(capture),
            "timing_model_sha256": _digest(timing.get("model_version")), "timing_action_sequence_sha256": action_signature,
            "status": status, "declared_success": success, "steps_completed": _integer(summary.get("steps_completed")), "steps_total": total,
            "harness_attempt_status": attempt,
            "observer_coverage_validated_by_harness": entry.get("telemetry_validated") if isinstance(entry.get("telemetry_validated"), bool) else None,
            "complete_verified_desktop_task": success and backend == "desktop" and interval["complete_step_sequence"],
            "task_interval": interval, "waits_by_kind_and_units": waits,
            "resources": {key: _number(resources.get(key)) for key in ("wall_seconds", "controller_cpu_seconds", "controller_peak_rss_bytes", "sample_interval_seconds")},
            "process_trace": {"available": trace.get("available") if isinstance(trace.get("available"), bool) else None,
                              "event_count": _integer(trace.get("event_count")), "source": "Controller-started WMI collector, when declared available"},
            "external_observer": observer,
            "observer_condition_sha256": _digest({"present": observer["present"], "recognized": observer.get("recognized_schema"), "interval": observer.get("interval_seconds")}),
            "warnings": sorted(set(warnings)),
            "_pair": _digest(entry.get("pair_id")), "_path": str(path)}


MATCH_FIELDS = ("backend", "workflow", "seed", "scale", "source_commit", "scenario_sha256", "environment_condition_sha256", "capture_condition_sha256", "timing_model_sha256", "observer_condition_sha256", "steps_total")


def _pairs(runs):
    grouped = defaultdict(list)
    for run in runs:
        # Explicit pairs expose mismatches; automatic pairs match declared metadata.
        key = ("explicit", run["_pair"]) if run["_pair"] else ("automatic", *(run[field] for field in MATCH_FIELDS))
        grouped[key].append(run)
    result = []
    for members in grouped.values():
        fixed = [run for run in members if run["policy"] == "fixed"]
        contextual = [run for run in members if run["policy"] == "contextual"]
        reasons = []
        if len(fixed) != 1 or len(contextual) != 1 or len(members) != 2:
            reasons.append("A pair requires exactly one fixed and one contextual attempt; missing or ambiguous members are retained.")
        for field in MATCH_FIELDS:
            values = [run[field] for run in members]
            if any(value is None or value == "unknown" for value in values):
                reasons.append(f"Missing required matching metadata: {field}.")
            elif any(value != values[0] for value in values[1:]):
                reasons.append(f"Mismatched {field}.")
        for field in ("runtime_sha256", "measurement_sha256"):
            values = [run[field] for run in members]
            if any(value is not None for value in values) and (None in values or len(set(values)) > 1):
                reasons.append(f"Mismatched or incomplete optional {field}.")
        metadata_matched = not reasons
        if any(not run["complete_verified_desktop_task"] for run in members):
            reasons.append("Both attempts must finish a verified native task with a complete step sequence for performance comparison.")
        if len({run["timing_action_sequence_sha256"] for run in members}) > 1:
            reasons.append("Timing action-kind/unit sequences differ.")
        if any(sum(item["missing_actual_count"] for item in run["waits_by_kind_and_units"]) for run in members):
            reasons.append("Measured waits are incomplete.")
        if any(not run["waits_by_kind_and_units"] for run in members):
            reasons.append("Timing observations are absent.")
        if any(run["harness_attempt_status"] in {"started", "failed", "interrupted"} for run in members):
            reasons.append("Harness completion is incomplete or failed; native success alone does not establish complete measurement.")
        if any(run["observer_coverage_validated_by_harness"] is False for run in members):
            reasons.append("Harness validation of observer identity, coverage or completion failed.")
        for run in members:
            observer = run["external_observer"]
            if observer.get("present") and (not observer.get("available") or observer.get("status") != "completed"):
                reasons.append("A supplied external observer is unavailable, incomplete or failed.")
                break
        item = {"id": f"P{len(result)+1:03d}", "run_ids": [run["id"] for run in members],
                "matching_metadata_complete": metadata_matched, "performance_comparable": not reasons,
                "matching_evidence": "Operator-declared version/setup plus run metadata; not independently verified", "reasons": reasons}
        if not reasons:
            a, b = fixed[0], contextual[0]
            item["contextual_minus_fixed"] = {
                "task_seconds": b["task_interval"]["task_seconds"] - a["task_interval"]["task_seconds"],
                **{field: b["resources"][field] - a["resources"][field]
                   if a["resources"][field] is not None and b["resources"][field] is not None else None
                   for field in ("wall_seconds", "controller_cpu_seconds", "controller_peak_rss_bytes")}}
        result.append(item)
    return result


def analyze(run_dirs=(), manifest=None):
    """Build an allowlisted, portable result. No arbitrary source strings copied."""
    entries, defaults = [], {}
    if manifest:
        manifest = Path(manifest).resolve()
        raw = json.loads(manifest.read_text(encoding="utf-8-sig"))
        if not isinstance(raw, dict) or not isinstance(raw.get("runs"), list):
            raise ValueError("Manifest must be an object containing a runs list")
        defaults = {field: raw[field] for field in ("source_commit", "environment_id", "capture_condition", "environment", "capture", "runtime_sha256", "measurement_sha256", "backend", "workflow", "scale", "scenario_sha256") if field in raw}
        for item in raw["runs"]:
            item = {"path": item} if isinstance(item, str) else item
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                raise ValueError("Each manifest run needs a path")
            entry = {**defaults, **item}
            entry["path"] = (manifest.parent / item["path"]).resolve()
            if item.get("observer_summary"):
                entry["observer_summary"] = str((manifest.parent / item["observer_summary"]).resolve())
            entries.append(entry)
    entries.extend({**defaults, "path": Path(path).resolve()} for path in run_dirs)
    if not entries:
        raise ValueError("Supply run directories or a manifest containing runs")
    unique, duplicates = {}, 0
    for entry in entries:
        path = entry["path"]
        if path in unique:
            duplicates += 1
        else:
            unique[path] = entry
    runs = [load_run(path, entry, index) for index, (path, entry) in enumerate(unique.items(), 1)]
    pairs = _pairs(runs)
    output = {"schema_version": 1, "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "human_reference_runs": 0, "source_paths_exported": False,
              "summary": {"attempts": len(runs), "complete_verified_desktop_tasks": sum(run["complete_verified_desktop_task"] for run in runs),
                          "performance_comparable_pairs": sum(pair["performance_comparable"] for pair in pairs),
                          "duplicate_paths_excluded": duplicates}, "runs": runs, "pairs": pairs, "limitations": list(LIMITATIONS)}
    output["paired_delta_summary"] = {}
    for field in ("task_seconds", "wall_seconds", "controller_cpu_seconds", "controller_peak_rss_bytes"):
        values = [pair["contextual_minus_fixed"][field] for pair in pairs if pair["performance_comparable"] and pair["contextual_minus_fixed"][field] is not None]
        output["paired_delta_summary"][field] = {"pairs": len(values), "minimum": min(values) if values else None,
                                                "median": statistics.median(values) if values else None,
                                                "maximum": max(values) if values else None}
    for run in runs:
        run.pop("_path")
        run.pop("_pair")
    return output


def _fmt(value, digits=3):
    return "unavailable" if value is None else f"{value:.{digits}f}"


def markdown(result):
    lines = ["# Controlled timing benchmark — observed evidence", "",
             f"{result['summary']['attempts']} attempts; {result['summary']['complete_verified_desktop_tasks']} complete, verified native tasks; {result['summary']['performance_comparable_pairs']} comparable fixed/contextual pairs under declared matching conditions.",
             "", "**No human baseline was collected. This comparison does not establish human similarity or an official score.**", "",
             "Run aliases correspond to manifest order (then explicit run arguments); duplicate paths are excluded. No source paths, Sheet IDs, process command lines, raw error text or event payloads are exported.", "",
             "| Run | Policy / seed | Status | Steps | Task interval (s) | Full wall (s) | Controller CPU (s) | Sampled controller RSS (MiB) |",
             "| --- | --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for run in result["runs"]:
        r = run["resources"]
        rss = r["controller_peak_rss_bytes"]
        lines.append(f"| {run['id']} | {run['policy']} / {run['seed']} | {run['backend']}: {run['status']} | {run['steps_completed']}/{run['steps_total']} | {_fmt(run['task_interval']['task_seconds'])} | {_fmt(r['wall_seconds'])} | {_fmt(r['controller_cpu_seconds'])} | {_fmt(rss / 1048576 if rss is not None else None, 2)} |")
    lines += ["", "## Paired comparison", "", "Deltas below are contextual minus fixed. A shorter or lower-resource incomplete run is never treated as an improvement.", ""]
    for pair in result["pairs"]:
        lines.append(f"- **{pair['id']} ({', '.join(pair['run_ids'])})**: " + ("comparable under declared conditions." if pair["performance_comparable"] else "not performance-comparable. " + " ".join(pair["reasons"])))
        if pair.get("contextual_minus_fixed"):
            delta = pair["contextual_minus_fixed"]
            lines.append(f"  Task delta {_fmt(delta['task_seconds'])} s; full-window controller CPU delta {_fmt(delta['controller_cpu_seconds'])} CPU-s. This measures policy cost, not human realism.")
    aggregate = result["paired_delta_summary"]["task_seconds"]
    if aggregate["pairs"]:
        lines += ["", f"Across {aggregate['pairs']} comparable pairs, task-duration delta median is {_fmt(aggregate['median'])} s (range {_fmt(aggregate['minimum'])} to {_fmt(aggregate['maximum'])} s). These are descriptive paired observations, not a significance test."]
    lines += ["", "## Requested and observed waits", "", "Samples are grouped by action kind and unit count. These are controller waits; correlated events are not independent task trials. Interrupted waits remain in the data.", "",
              "| Run | Kind / units | Requested n | Requested median / p90 (s) | Actual n | Actual median / p90 (s) | Interrupted |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for run in result["runs"]:
        for wait in run["waits_by_kind_and_units"]:
            a, b = wait["requested_wait"], wait["actual_wait"]
            lines.append(f"| {run['id']} | {wait['kind']} / {wait['units']} | {a['count']} | {_fmt(a['median_seconds'])} / {_fmt(a['p90_seconds'])} | {b['count']} | {_fmt(b['median_seconds'])} / {_fmt(b['p90_seconds'])} | {wait['interrupted_count']} |")
    lines += ["", "## Observer coverage and input validity", ""]
    for run in result["runs"]:
        obs = run["external_observer"]
        lines.append(f"- {run['id']}: separate observer summary {'present' if obs['present'] else 'absent'} (status {obs.get('status', 'absent')}); harness status {run['harness_attempt_status']}; WMI collector available: {run['process_trace']['available']}." + (" " + " ".join(run["warnings"]) if run["warnings"] else ""))
    if any(run["external_observer"].get("scopes") for run in result["runs"]):
        lines += ["", "External sampling covers its own observation window. Chrome/Notepad are nonexclusive cohorts, CPU covers first-to-last samples, RSS can double-count shared memory, and scopes may overlap. Do not add these scopes to the controller total.", "",
                  "| Run | Observer scope | Processes | Observed CPU delta (s) | Peak simultaneous sampled RSS (MiB) |",
                  "| --- | --- | ---: | ---: | ---: |"]
        for run in result["runs"]:
            for name, scope in run["external_observer"].get("scopes", {}).items():
                rss = scope["peak_sampled_rss_bytes"]
                lines.append(f"| {run['id']} | {name} | {_fmt(scope['process_count'], 0)} | {_fmt(scope['observed_cpu_delta_seconds'])} | {_fmt(rss / 1048576 if rss is not None else None, 2)} |")
        lines += ["", "| Run | Observer snapshots | Duration (s) | Median / max sample gap (s) | Observer CPU (s) | Observer peak RSS (MiB) |",
                  "| --- | ---: | ---: | ---: | ---: | ---: |"]
        for run in result["runs"]:
            obs = run["external_observer"]
            if not obs.get("scopes"):
                continue
            cadence, overhead = obs["cadence"], obs["observer_resources"]
            rss = overhead["peak_sampled_rss_bytes"]
            lines.append(f"| {run['id']} | {_fmt(obs.get('snapshot_count'), 0)} | {_fmt(obs.get('duration_seconds'))} | {_fmt(cadence['median_gap_seconds'])} / {_fmt(cadence['max_gap_seconds'])} | {_fmt(overhead['cpu_seconds'])} | {_fmt(rss / 1048576 if rss is not None else None, 2)} |")
    lines += ["", "## Limits", ""] + [f"- {item}" for item in result["limitations"]]
    return "\n".join(lines) + "\n"


def export(result, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    json_path, md_path = output / "benchmark.json", output / "BENCHMARK.md"
    json_path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    md_path.write_text(markdown(result), encoding="utf-8")
    return json_path, md_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dirs", nargs="*", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--root", type=Path, help="Benchmark root containing manifest.json; does not recursively select unrelated runs")
    parser.add_argument("--output", type=Path, required=True, help="Directory for benchmark.json and BENCHMARK.md")
    args = parser.parse_args(argv)
    if args.root and args.manifest:
        parser.error("Choose --root or --manifest")
    try:
        result = analyze(args.run_dirs, args.manifest or (args.root / "manifest.json" if args.root else None))
        paths = export(result, args.output)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    for path in paths:
        print(path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
