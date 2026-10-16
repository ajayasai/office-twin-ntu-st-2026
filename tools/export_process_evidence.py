"""Export privacy-safe process-parent counts from external observer summaries.

Run aliases follow analyze_benchmark.py: first occurrence of each resolved run
path in manifest order is R001, R002, etc. Source identities and timestamps are
used only for validation, deduplication and relative age classification. They
are never included in exported JSON or Markdown.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import json
import math
from pathlib import Path


SCOPES = ("controller", "controller_descendants", "chrome", "notepad", "unrecognized-scope")
APPLICATION_ROLES = {"chrome": "chrome", "chrome.exe": "chrome",
                     "notepad": "notepad", "notepad.exe": "notepad",
                     "python": "python", "python.exe": "python",
                     "pythonw": "pythonw", "pythonw.exe": "pythonw",
                     "explorer": "explorer", "explorer.exe": "explorer"}
AGES = ("preexisting-at-observer-start", "os-creation-time-within-observer-window", "unresolved-or-outside-window")
PARENTS = ("resolved-compatible-age", "unresolved", "conflicting-observations")
LIMITATIONS = [
    "These are external OS inventory/resource snapshots from a separate process, not Sysmon/ETW process-start events or an independent third-party audit.",
    "Creation classification compares the OS-reported creation timestamp with the observer window; it is not an observed process-start event and does not establish who caused the launch.",
    "Parent PID and identity are best-effort sampled metadata. A resolved parent must match the recorded parent PID and have a creation time no later than its child; this check does not prove the original launch chain.",
    "Preexisting Chrome processes may have Explorer parentage from before the task. Such relationships do not prove that this run launched Chrome through Explorer.",
    "Chrome and Notepad cohorts include shared tabs, documents and unrelated activity. Process relationships do not establish exclusive workload attribution or delivered desktop input.",
    "Polling can miss short-lived processes and inaccessible or exited parents. Missing observations are not evidence that a process or relationship never existed.",
    "Each run counts unique PID-plus-creation-time identities privately. Cross-run totals sum per-run counts, so a reused warm process can be counted in multiple runs.",
    "P001-style aliases are local to each run and are not stable across runs. A parent alias is included only when that compatible parent identity was itself observed in the selected process cohort.",
    "Per-process CPU covers first-to-last sampled counters, not lifetime CPU. Peak RSS is a sampled process maximum; per-process memory peaks must not be added to infer simultaneous or unique physical memory.",
    "Only fixed application roles are published; all other process names are redacted. PIDs, raw creation timestamps, source paths, command lines, URLs and account information are not exported.",
    "Human reference runs: 0. Process parentage and automated timing evidence do not establish human similarity.",
]


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value) if value >= 0 else None


def _integer(value):
    value = _number(value)
    return int(value) if value is not None and value.is_integer() else None


def _identity(pid, created):
    pid = _integer(pid)
    created = _number(created)
    return (pid, created) if pid and created and created > 0 else None


def _role(name):
    return APPLICATION_ROLES.get(name.lower(), "other-redacted") if isinstance(name, str) else "other-redacted"


def _timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if moment.tzinfo is None:
            return None
        return moment.timestamp()
    except (ValueError, OverflowError, OSError):
        return None


def _window(data):
    started, ended = _timestamp(data.get("started_utc")), _timestamp(data.get("ended_utc"))
    return (started, ended) if started is not None and ended is not None and ended >= started else None


def _creation_class(created, window):
    if window is None:
        return AGES[2]
    if created < window[0]:
        return AGES[0]
    if created <= window[1]:
        return AGES[1]
    return AGES[2]


def _read_json(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        return value if isinstance(value, dict) else None
    except (OSError, ValueError):
        return None


def _observer_path(manifest, entry):
    if isinstance(entry.get("observer_summary"), str):
        return (manifest.parent / entry["observer_summary"]).resolve()
    if isinstance(entry.get("observer_path"), str):
        return (manifest.parent / entry["observer_path"] / "external-observer-summary.json").resolve()
    return (manifest.parent / entry["path"] / "external-observer-summary.json").resolve()


def _collect_identities(records):
    """Return private identity groups; none of these keys may be exported."""
    groups = defaultdict(list)
    invalid = 0
    for record in records:
        if not isinstance(record, dict):
            invalid += 1
            continue
        key = _identity(record.get("pid"), record.get("create_time"))
        samples = _integer(record.get("samples"))
        if key is None or not samples:
            invalid += 1
            continue
        groups[key].append(record)
    return groups, invalid


def _parent(group, child_created):
    candidates = set()
    invalid_claims = False
    for record in group:
        raw = record.get("parent_identity")
        if not isinstance(raw, dict):
            continue
        key = _identity(raw.get("pid"), raw.get("create_time"))
        if key is None or key[0] != _integer(record.get("parent_pid")) or key[1] > child_created:
            invalid_claims = True
            continue
        candidates.add((key, _role(raw.get("name"))))
    # A later resolved observation can fill an earlier missing parent. Two
    # different compatible parents must not silently collapse into one claim.
    if len(candidates) > 1 or (invalid_claims and candidates):
        return "conflicting-observations", "unresolved", None
    if candidates:
        key, role = next(iter(candidates))
        return "resolved-compatible-age", role, key
    return "unresolved", "unresolved", None


def _process_metrics(group):
    """Merge redundant summary rows without summing duplicate observations."""
    bounds = [(first, last) for row in group
              if (first := _number(row.get("first_observed_seconds"))) is not None
              and (last := _number(row.get("last_observed_seconds"))) is not None and last >= first]
    cpu_bounds = [(first, last) for row in group
                  if (first := _number(row.get("cpu_first_seconds"))) is not None
                  and (last := _number(row.get("cpu_last_seconds"))) is not None and last >= first]
    memory = [value for row in group if (value := _integer(row.get("peak_sampled_rss_bytes"))) is not None]
    return {"first_observed_seconds": min(first for first, _ in bounds) if bounds else None,
            "last_observed_seconds": max(last for _, last in bounds) if bounds else None,
            "samples": max(_integer(row.get("samples")) or 0 for row in group),
            "observed_cpu_delta_seconds": max(last for _, last in cpu_bounds) - min(first for first, _ in cpu_bounds) if cpu_bounds else None,
            "peak_sampled_rss_bytes": max(memory) if memory else None}


def summarize_observer(data, run_alias, policy="unknown", telemetry_validated=None):
    result = {"id": run_alias, "policy": policy if policy in {"fixed", "contextual"} else "unknown",
              "observer_present": data is not None, "recognized_schema": False,
              "observer_status": "unavailable", "harness_telemetry_validated": telemetry_validated if isinstance(telemetry_validated, bool) else None,
              "method": "sampled_polling", "process_start_event_trace": False, "human_reference": False,
              "unique_observed_identities": 0, "duplicate_identity_records_excluded": 0,
              "invalid_records_excluded": 0, "creation_window_valid": False,
              "parent_resolution_counts": {status: 0 for status in PARENTS},
              "creation_counts": {age: 0 for age in AGES}, "scopes": {}, "relationships": [], "processes": [], "warnings": []}
    if data is None:
        result["warnings"].append("Observer summary unavailable or malformed.")
        return result
    recognized = (data.get("evidence_source") == "external_process_snapshot_observer"
                  and data.get("method") == "sampled_polling"
                  and data.get("process_start_event_trace") is False)
    result["recognized_schema"] = recognized
    if not recognized:
        result["warnings"].append("Unrecognized observer schema; process relationships were not exported.")
        return result
    status = data.get("status")
    result["observer_status"] = status if status in {"completed", "failed", "interrupted"} else "unspecified"
    raw_records = data.get("process_observations")
    if not isinstance(raw_records, list):
        result["warnings"].append("Process observation list unavailable or malformed.")
        return result
    window = _window(data)
    result["creation_window_valid"] = window is not None
    if window is None:
        result["warnings"].append("Observer time window is unavailable or invalid; creation age remains unresolved.")
    groups, invalid = _collect_identities(raw_records)
    result["invalid_records_excluded"] = invalid
    result["unique_observed_identities"] = len(groups)
    result["duplicate_identity_records_excluded"] = sum(len(group) - 1 for group in groups.values())
    reported = _integer(data.get("process_count"))
    if reported is not None and reported != len(groups):
        result["warnings"].append("Reported process count differs from the validated unique identity count.")
    if invalid:
        result["warnings"].append("Invalid process records were excluded.")
    relationships = Counter()
    scopes = {}
    aliases = {key: f"P{index:03d}" for index, key in enumerate(groups, 1)}
    for key, group in groups.items():
        _, created = key
        declared_scopes = {record.get("scope") for record in group if isinstance(record.get("scope"), str)}
        scope = next(iter(declared_scopes)) if len(declared_scopes) == 1 else "unrecognized-scope"
        scope = scope if scope in SCOPES else "unrecognized-scope"
        roles = {_role(record.get("name")) for record in group}
        child_role = next(iter(roles)) if len(roles) == 1 else "other-redacted"
        parent_status, parent_role, parent_key = _parent(group, created)
        age = _creation_class(created, window)
        bucket = scopes.setdefault(scope, {"unique_observed_identities": 0,
                                           "parent_resolution_counts": {status: 0 for status in PARENTS},
                                           "creation_counts": {age: 0 for age in AGES}})
        bucket["unique_observed_identities"] += 1
        bucket["parent_resolution_counts"][parent_status] += 1
        bucket["creation_counts"][age] += 1
        result["parent_resolution_counts"][parent_status] += 1
        result["creation_counts"][age] += 1
        relationships[(scope, child_role, parent_role, parent_status, age)] += 1
        result["processes"].append({"id": aliases[key], "scope": scope, "application_role": child_role,
                                     "parent_role": parent_role, "parent_resolution": parent_status,
                                     "parent_observed_process_alias": aliases.get(parent_key), "creation_class": age,
                                     **_process_metrics(group)})
    result["scopes"] = {scope: scopes[scope] for scope in SCOPES if scope in scopes}
    result["relationships"] = [{"scope": key[0], "application_role": key[1], "parent_role": key[2],
                                 "parent_resolution": key[3], "creation_class": key[4], "identity_count": count}
                                for key, count in sorted(relationships.items())]
    if result["parent_resolution_counts"]["conflicting-observations"]:
        result["warnings"].append("Conflicting duplicate parent observations were retained as unresolved relationships.")
    return result


def analyze_manifest(manifest):
    manifest = Path(manifest).resolve()
    raw = _read_json(manifest)
    if raw is None or not isinstance(raw.get("runs"), list):
        raise ValueError("Manifest must contain a runs list")
    entries, duplicate_paths = {}, 0
    for entry in raw["runs"]:
        entry = {"path": entry} if isinstance(entry, str) else entry
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError("Each manifest run needs a path")
        path = (manifest.parent / entry["path"]).resolve()
        if path in entries:
            duplicate_paths += 1
        else:
            entries[path] = entry
    runs = []
    for index, entry in enumerate(entries.values(), 1):
        data = _read_json(_observer_path(manifest, entry))
        runs.append(summarize_observer(data, f"R{index:03d}", entry.get("timing"), entry.get("telemetry_validated")))
    total_relationships = Counter()
    for run in runs:
        for row in run["relationships"]:
            key = tuple(row[field] for field in ("scope", "application_role", "parent_role", "parent_resolution", "creation_class"))
            total_relationships[key] += row["identity_count"]
    return {"schema_version": 1, "evidence_type": "sanitized_external_process_parent_observations",
            "run_alias_definition": "First occurrence of each resolved run path in manifest order; matches benchmark analyzer aliases.",
            "raw_process_identifiers_exported": False, "absolute_timestamps_exported": False,
            "source_paths_exported": False, "human_reference_runs": 0,
            "summary": {"runs": len(runs), "runs_with_recognized_observer": sum(run["recognized_schema"] for run in runs),
                        "sum_of_per_run_unique_identities": sum(run["unique_observed_identities"] for run in runs),
                        "duplicate_manifest_paths_excluded": duplicate_paths,
                        "resolved_compatible_age_per_run_identity_sum": sum(run["parent_resolution_counts"]["resolved-compatible-age"] for run in runs)},
            "runs": runs,
            "relationship_totals": [{"scope": key[0], "application_role": key[1], "parent_role": key[2],
                                     "parent_resolution": key[3], "creation_class": key[4],
                                     "sum_of_per_run_identity_counts": count} for key, count in sorted(total_relationships.items())],
            "limitations": list(LIMITATIONS)}


def markdown(data):
    lines = ["# External process-parent evidence", "",
             "The separate observer sampled real OS process identities and parent metadata. The tables publish fixed application roles and aggregate counts only.", "",
             "**This is sampled process evidence, not a process-start trace.** Creation age uses OS-reported timestamps. Preexisting Chrome parentage does not establish how this run launched Chrome; application cohorts include unrelated activity. Human reference runs: **0**.", "",
             "| Run | Policy | Observed identities | Compatible parent | Unresolved/conflicting parent | Preexisting | OS creation within window | Age unresolved |",
             "|---|---|---:|---:|---:|---:|---:|---:|"]
    for run in data["runs"]:
        parents, ages = run["parent_resolution_counts"], run["creation_counts"]
        lines.append(f'| {run["id"]} | {run["policy"]} | {run["unique_observed_identities"]} | {parents[PARENTS[0]]} | {parents[PARENTS[1]] + parents[PARENTS[2]]} | {ages[AGES[0]]} | {ages[AGES[1]]} | {ages[AGES[2]]} |')
    lines += ["", "Counts below sum identities separately within each run. The same warm process can appear in several runs; these totals are not distinct processes across the experiment.", "",
              "| Scope | Application role | Parent role | Parent evidence | Creation class | Sum of per-run counts |",
              "|---|---|---|---|---|---:|"]
    for row in data["relationship_totals"]:
        lines.append(f'| {row["scope"]} | {row["application_role"]} | {row["parent_role"]} | {row["parent_resolution"]} | {row["creation_class"]} | {row["sum_of_per_run_identity_counts"]} |')
    warnings = [(run["id"], warning) for run in data["runs"] for warning in run["warnings"]]
    if warnings:
        lines += ["", "## Data quality", ""]
        lines += [f"- {alias}: {warning}" for alias, warning in warnings]
    lines += ["", "## Pseudonymized process observations", "",
              "Aliases restart at P001 in each run. A blank parent alias means the compatible parent was outside the selected cohort or unresolved. Times are seconds from observer start; CPU is the sampled counter delta. RSS is each process's sampled peak in MiB, not a simultaneous memory total."]
    def fmt(value, digits=3):
        return "unavailable" if value is None else f"{value:.{digits}f}"
    for run in data["runs"]:
        lines += ["", f'### {run["id"]} ({run["policy"]})', "",
                  "| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |",
                  "|---|---|---|---|---|---:|---:|---:|---:|"]
        for row in run["processes"]:
            rss = row["peak_sampled_rss_bytes"]
            lines.append(f'| {row["id"]} | {row["scope"]} / {row["application_role"]} | {row["parent_observed_process_alias"] or "—"} / {row["parent_role"]} | {row["parent_resolution"]} | {row["creation_class"]} | {fmt(row["first_observed_seconds"])} / {fmt(row["last_observed_seconds"])} | {row["samples"]} | {fmt(row["observed_cpu_delta_seconds"])} | {fmt(rss / 1048576 if rss is not None else None, 2)} |')
    lines += ["", "## Interpretation limits", ""]
    lines += [f"- {limitation}" for limitation in data["limitations"]]
    return "\n".join(lines) + "\n"


def export(manifest, output):
    result = analyze_manifest(manifest)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "process-parent-evidence.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (output / "process-parent-evidence.md").write_text(markdown(result), encoding="utf-8")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Directory for sanitized JSON and Markdown")
    args = parser.parse_args(argv)
    try:
        result = export(args.manifest, args.output)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
