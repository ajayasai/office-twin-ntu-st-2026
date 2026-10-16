"""Validate private Kernel-Process ETW evidence and export allowlisted evidence.

Raw ETL/XML and canary identities stay private. A successful result means that
the stopped logger reported zero loss and every known canary was observed; it
does NOT certify universal completeness or establish exclusive app attribution.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import statistics
import sys
import xml.etree.ElementTree as ET

PROVIDER = "22fb2cd6-0e7b-422b-a0c7-2fad1fd0e716"
KINDS = {1: "start", 2: "stop", 15: "rundown"}
ROLES = {name + suffix: name for name in ("chrome", "notepad", "explorer", "python", "cmd", "pwsh", "powershell") for suffix in ("", ".exe")}
FOCUS_ROLES = {"explorer": "explorer", "browser": "chrome", "sheets": "chrome", "notepad": "notepad"}
APPLICATION_ROLES = frozenset(("chrome", "notepad", "explorer"))
LOSS_KEYS = ("events_lost", "log_buffers_lost", "real_time_buffers_lost")
LIMITATIONS = [
    "Zero reported logger loss plus observed known canaries is a bounded validation, not proof that every system process event was captured.",
    "Rundown records identify processes already present; they are never counted as observed process-start events.",
    "A stop is paired only with a compatible process sequence number or PID plus creation time. Ambiguous identities and parents remain unresolved.",
    "Application windows and their descendant cohorts can share unrelated tabs and work; process relationships do not prove exclusive task attribution or delivery of desktop input.",
    "Preexisting application processes may have no event or rundown in this trace. Unresolved window-to-process bindings are counted separately and are not synthesized from snapshots; they do not invalidate observed known-canary and controller lifecycles.",
    "Native application cohorts include Chrome, Notepad and Explorer lifecycle events inside each trial window, regardless of who caused them. A reported parent-ID match compares an ETW start's ParentProcessID with a controller window-focus PID; it is not a resolved parent lifetime identity or proof of task causation.",
    "Capture-boundary and known-canary checks cover this trace and supplied native trials only; they do not create raw human-input evidence or establish portability to another machine.",
    "Public output contains capture-local aliases, relative times and allowlisted application roles; original ETL/XML, identifiers, absolute times and command lines remain private.",
]


def integer(value):
    if isinstance(value, bool):
        raise ValueError("boolean integer")
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        raise ValueError("invalid integer")
    value = value.strip()
    if not re.fullmatch(r"(?:0[xX][0-9a-fA-F]+|[+-]?\d+)", value):
        raise ValueError("invalid integer")
    return int(value, 16 if value.lower().startswith("0x") else 10)


def timestamp_ns(value, *, creation=False):
    """Keep 100 ns FILETIME precision, avoiding floating-point identity keys."""
    if creation and isinstance(value, (int, str)) and re.fullmatch(r"(?:0[xX][0-9a-fA-F]+|\d+)", str(value)):
        ticks = integer(value)
        if ticks <= 116444736000000000:
            raise ValueError("invalid FILETIME")
        return (ticks - 116444736000000000) * 100
    if not isinstance(value, str):
        raise ValueError("timestamp must be string")
    match = re.fullmatch(r"(\d{4}-\d\d-\d\d[T ]\d\d:\d\d:\d\d)(?:\.(\d{1,9}))?(Z|[+-]\d\d:\d\d)", value.strip())
    if not match:
        raise ValueError("timestamp missing timezone or malformed")
    base = datetime.fromisoformat(match[1] + match[3].replace("Z", "+00:00"))
    delta = base.astimezone(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (delta.days * 86400 + delta.seconds) * 1_000_000_000 + int((match[2] or "").ljust(9, "0"))


def epoch_ns(value):
    if isinstance(value, bool):
        raise ValueError("invalid epoch")
    try:
        number = Decimal(str(value))
        if not number.is_finite() or number <= 0:
            raise ValueError("invalid epoch")
        return int(number * 1_000_000_000)
    except InvalidOperation as exc:
        raise ValueError("invalid epoch") from exc


def role(value):
    return ROLES.get(PureWindowsPath(str(value)).name.lower(), "other")


def local(tag):
    return tag.rsplit("}", 1)[-1]


@dataclass(frozen=True)
class Event:
    kind: str
    time: int
    pid: int
    created: int
    sequence: int | None
    parent_pid: int | None
    parent_sequence: int | None
    exit_code: int | None
    role: str
    exit_time: int | None


def read_xml(path):
    events, counts = [], Counter()
    try:
        for _, element in ET.iterparse(path, events=("end",)):
            if local(element.tag) != "Event":
                continue
            system = next((child for child in element if local(child.tag) == "System"), None)
            if system is None:
                counts["malformed_system"] += 1
                element.clear()
                continue
            fields = {local(child.tag): child for child in system}
            provider = fields.get("Provider")
            guid = "" if provider is None else provider.get("Guid", provider.get("GUID", "")).strip("{}").lower()
            if guid != PROVIDER:
                counts["other_provider_events"] += 1
                element.clear()
                continue
            counts["provider_events"] += 1
            try:
                event_id = integer(fields["EventID"].text)
                if event_id not in KINDS:
                    counts["other_provider_event_ids"] += 1
                    element.clear()
                    continue
                # Use field names rather than version-specific positional order.
                data = {}
                for entry in element.iter():
                    if local(entry.tag) == "Data" and entry.get("Name"):
                        name = entry.get("Name").lower()
                        if name in data:
                            raise ValueError("duplicate event field")
                        data[name] = entry.text or ""
                time = timestamp_ns(fields["TimeCreated"].get("SystemTime"))
                pid = integer(data["processid"])
                created = timestamp_ns(data["createtime"], creation=True)
                seq = integer(data["processsequencenumber"]) if "processsequencenumber" in data else None
                pseq = integer(data["parentprocesssequencenumber"]) if "parentprocesssequencenumber" in data else None
                parent = integer(data["parentprocessid"]) if "parentprocessid" in data else None
                code = integer(data["exitcode"]) if "exitcode" in data else None
                exit_time = timestamp_ns(data["exittime"], creation=True) if "exittime" in data else None
                if pid <= 0 or seq is not None and seq < 0 or parent is not None and parent < 0 or created > time + 1_000_000:
                    raise ValueError("invalid process identity")
                if event_id in (1, 15) and parent is None or event_id == 2 and (code is None or exit_time is None):
                    raise ValueError("required field missing")
                if exit_time is not None and not created <= exit_time <= time + 1_000_000:
                    raise ValueError("invalid exit timestamp")
                events.append(Event(KINDS[event_id], time, pid, created, seq, parent, pseq, code,
                                    role(data.get("imagename", "")), exit_time))
                counts[KINDS[event_id]] += 1
            except (KeyError, ValueError, TypeError, OverflowError):
                counts["invalid_process_events"] += 1
            element.clear()
    except (ET.ParseError, OSError, UnicodeError):
        counts["xml_read_errors"] += 1
    return sorted(events, key=lambda event: (event.time, {"start": 0, "rundown": 1, "stop": 2}[event.kind])), counts


def build_processes(events):
    processes, sequence_ids, issues = {}, defaultdict(set), Counter()
    for event in events:
        identity = (event.pid, event.created)
        process = processes.setdefault(identity, {"events": [], "sequences": set(), "parents": set(), "roles": set()})
        process["events"].append(event)
        if event.sequence is not None:
            process["sequences"].add(event.sequence)
            sequence_ids[event.sequence].add(identity)
        if event.parent_pid is not None:
            process["parents"].add((event.parent_pid, event.parent_sequence))
        if event.role != "other":
            process["roles"].add(event.role)
    for identity, process in processes.items():
        process["starts"] = [event for event in process["events"] if event.kind == "start"]
        process["stops"] = [event for event in process["events"] if event.kind == "stop"]
        process["role"] = next(iter(process["roles"])) if len(process["roles"]) == 1 else "other"
        process["identity_valid"] = len(process["sequences"]) <= 1 and all(len(sequence_ids[seq]) == 1 for seq in process["sequences"])
        if not process["identity_valid"]:
            issues["conflicting_process_identities"] += 1
        if len(process["starts"]) > 1 or len(process["stops"]) > 1:
            issues["duplicate_lifecycle_events"] += 1
        if process["stops"] and min(event.time for event in process["stops"]) < identity[1]:
            issues["inverted_lifetime"] += 1
        process["parent"] = None
        parents = set()
        for ppid, pseq in process["parents"]:
            if ppid == 0:
                continue
            candidates = []
            for key, candidate in processes.items():
                if key == identity or key[0] != ppid or key[1] > identity[1]:
                    continue
                if pseq is not None and pseq not in candidate["sequences"]:
                    continue
                # Creation and exit evidence must place this exact parent alive.
                stops = [event.time for event in candidate["events"] if event.kind == "stop"]
                if stops and min(stops) < identity[1]:
                    continue
                candidates.append(key)
            if len(candidates) == 1:
                parents.add(candidates[0])
        if len(parents) == 1 and len({value[0] for value in process["parents"]}) == 1:
            process["parent"] = next(iter(parents))
    # A reused PID with no exit observed can make a parent relation ambiguous;
    # never pick the most recent record merely because it looks convenient.
    return processes, issues


def read_json(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("JSON object required")
    return data


def hash_file(path):
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(value, origin):
    return round((value - origin) / 1_000_000_000, 7)


def analyze_capture(capture_dir, manifest_path=None):
    capture_dir = Path(capture_dir)
    errors = set()
    try:
        status = read_json(capture_dir / "capture-status.json")
    except (OSError, ValueError):
        status = {}
        errors.add("capture_status_missing_or_invalid")
    try:
        origin = timestamp_ns(status["trace_started_utc"])
        ended = timestamp_ns(status["trace_stopped_utc"])
        if ended <= origin:
            raise ValueError("invalid trace window")
    except (KeyError, ValueError, TypeError, OverflowError):
        origin = ended = 0
        errors.add("capture_window_missing_or_invalid")
    if status.get("finalized") is not True:
        errors.add("capture_not_finalized")
    if (status.get("status") != "captured_pending_verification" or status.get("stop_reason") != "stop_request"
            or status.get("final_loss_counters_available") is not True or status.get("conversion_exit_code") != 0
            or status.get("errors") != [] or str(status.get("provider_guid", "")).strip("{}").lower() != PROVIDER):
        errors.add("capture_final_status_not_successful")
    counters = {}
    try:
        for key in LOSS_KEYS:
            counters[key] = integer(status["loss_counters"][key])
            if counters[key] < 0:
                raise ValueError("negative loss")
    except (KeyError, ValueError, TypeError):
        errors.add("final_loss_counters_missing_or_invalid")
    zero_loss = len(counters) == len(LOSS_KEYS) and all(value == 0 for value in counters.values())
    if not zero_loss:
        errors.add("zero_reported_loss_not_verified")
    xml_path = capture_dir / "process-events.xml"
    decoder = "tracerpt"
    decode_metadata = None
    canonical_path = capture_dir / "process-events-winapi.xml"
    decode_status_path = capture_dir / "winapi-decode-status.json"
    if canonical_path.exists() or decode_status_path.exists():
        try:
            decode_metadata = read_json(decode_status_path)
            if (decode_metadata.get("status") != "decoded" or decode_metadata.get("decoder") != "Get-WinEvent.ToXml"
                    or decode_metadata.get("errors") != []
                    or decode_metadata.get("source_etl_sha256") != hash_file(capture_dir / "process-events.etl")
                    or decode_metadata.get("xml_sha256") != hash_file(canonical_path)
                    or not canonical_path.is_file()):
                raise ValueError("canonical decoder evidence invalid")
            xml_path, decoder = canonical_path, "Get-WinEvent.ToXml"
        except (OSError, ValueError, KeyError, TypeError):
            errors.add("canonical_decode_integrity_not_verified")
    events, counts = read_xml(xml_path)
    if decoder == "Get-WinEvent.ToXml":
        try:
            if integer(decode_metadata["decoded_event_count"]) != counts["provider_events"]:
                raise ValueError("canonical decode count mismatch")
        except (KeyError, ValueError, TypeError):
            errors.add("canonical_decode_event_count_mismatch")
    if counts["xml_read_errors"] or counts["malformed_system"] or counts["invalid_process_events"]:
        errors.add("process_event_parse_failed")
    if not events:
        errors.add("no_process_events")
    processes, issues = build_processes(events)
    if issues:
        errors.add("process_identity_or_lifecycle_conflict")
    # Alias order is deterministic but all aliases are local to this capture.
    aliases = {key: f"P{number:04d}" for number, key in enumerate(sorted(processes, key=lambda key: (key[1], key[0])), 1)}
    selected = defaultdict(set)
    parent_focus_matches = defaultdict(set)
    try:
        ground = read_json(capture_dir / "canary-ground-truth.json")
        children = ground.get("canaries", ground.get("children"))
        if not isinstance(children, list) or not children:
            raise ValueError("empty canaries")
    except (OSError, ValueError, KeyError, TypeError):
        ground = {}
        children = []
        errors.add("canary_ground_truth_missing_or_invalid")
    worker_verified, worker_pid = False, None
    try:
        worker_start, worker_finish = timestamp_ns(ground["started_utc"]), timestamp_ns(ground["finished_utc"])
        worker_pid = integer(ground["controller_pid"])
        ready_path = capture_dir / "capture-ready.json"
        ready = read_json(ready_path)
        ready_bound = ground["capture_ready_sha256"] == hash_file(ready_path) and ground["capture_session"] == ready["session_name"] == status["session_name"]
        workers = [(key, process) for key, process in processes.items() if key[0] == worker_pid and origin <= key[1] <= worker_start and process["identity_valid"]]
        if len(workers) == 1:
            key, worker = workers[0]
            selected[key].add("validation_worker")
            worker_verified = (ground.get("status") == "completed" and ready_bound and origin <= worker_start <= worker_finish <= ended
                               and len(worker["starts"]) == len(worker["stops"]) == 1
                               and worker["starts"][0].time <= worker_start <= worker_finish <= worker["stops"][0].time <= ended
                               and worker["stops"][0].exit_code == 0)
    except (OSError, ValueError, KeyError, TypeError, OverflowError):
        pass
    if not worker_verified:
        errors.add("validation_worker_lifecycle_not_verified")
    canaries, verified_windows, seen_canaries = [], defaultdict(list), set()
    for number, child in enumerate(children, 1):
        row = {"id": f"C{number:03d}", "phase": "other", "kind": "other", "verified": False}
        try:
            pid, ppid = integer(child["pid"]), integer(child["parent_pid"])
            expected = integer(child["expected_exit_code"]) & 0xFFFFFFFF
            before = timestamp_ns(child["launch_before_utc"])
            after = timestamp_ns(child["wait_finished_utc"])
            row["phase"] = child.get("phase") if child.get("phase") in ("before-native", "after-native") else "other"
            row["kind"] = child.get("kind") if child.get("kind") in ("short-lived-child", "intermediate-parent", "nested-child") else "other"
            candidates = [(key, process) for key, process in processes.items() if key[0] == pid and before <= key[1] <= after and process["identity_valid"]]
            if before > after or len(candidates) != 1:
                raise ValueError("canary identity ambiguous")
            key, process = candidates[0]
            if key in seen_canaries:
                raise ValueError("canary identity repeated")
            seen_canaries.add(key)
            starts = [event for event in process["starts"] if before <= event.time <= after]
            stops = [event for event in process["stops"] if before <= event.time <= after]
            selected[key].add("known_canary")
            row.update({"process": aliases[key], "observed_starts": len(starts), "observed_stops": len(stops),
                        "expected_exit_code": expected, "within_capture_boundary": origin <= before <= after <= ended})
            start_ok = len(starts) == 1 and starts[0].parent_pid == ppid
            stop_ok = len(stops) == 1 and (stops[0].exit_code & 0xFFFFFFFF) == expected
            parent_ok = process["parent"] is not None and process["parent"][0] == ppid
            row.update({"parent_id_matches": start_ok, "parent_identity_resolved": parent_ok, "exit_code_matches": stop_ok})
            actual_ok = integer(child["actual_exit_code"]) & 0xFFFFFFFF == expected
            expected_parents = [worker_pid] if row["kind"] in ("short-lived-child", "intermediate-parent") else [
                integer(candidate["pid"]) for candidate in children if isinstance(candidate, dict)
                and candidate.get("phase") == row["phase"] and candidate.get("kind") == "intermediate-parent"]
            chain_ok = len(expected_parents) == 1 and ppid == expected_parents[0]
            row["expected_parent_chain_matches"] = chain_ok
            row["verified"] = start_ok and stop_ok and parent_ok and chain_ok and actual_ok and row["within_capture_boundary"] and starts[0].time <= stops[0].time
            if row["verified"]:
                verified_windows[row["phase"]].append((starts[0].time, stops[0].time))
                row["lifetime_ms"] = round((stops[0].exit_time - key[1]) / 1_000_000, 4)
                row["start_to_stop_event_span_ms"] = round((stops[0].time - starts[0].time) / 1_000_000, 4)
        except (KeyError, ValueError, TypeError, OverflowError):
            row["validation_error"] = "canary_record_or_identity_invalid"
        canaries.append(row)
    if not canaries or not all(row["verified"] for row in canaries):
        errors.add("known_canary_coverage_not_verified")
    expected_protocol = Counter({(phase, kind): count for phase in ("before-native", "after-native")
                                 for kind, count in (("short-lived-child", 12), ("intermediate-parent", 1), ("nested-child", 1))})
    observed_protocol = Counter((row["phase"], row["kind"]) for row in canaries)
    if observed_protocol != expected_protocol:
        errors.add("expected_28_canary_protocol_not_met")
    runs = []
    if manifest_path is not None:
        manifest_path = Path(manifest_path)
        try:
            manifest = read_json(manifest_path)
            entries = manifest["runs"]
            if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
                raise ValueError("manifest runs invalid")
            if manifest.get("status") != "completed" or not entries:
                errors.add("native_manifest_incomplete")
            if len(entries) != 2 or Counter(entry.get("timing") for entry in entries) != Counter(("fixed", "contextual")):
                errors.add("expected_native_timing_pair_not_met")
        except (OSError, ValueError, KeyError, TypeError):
            entries = []
            errors.add("native_manifest_missing_or_incomplete")
        for number, entry in enumerate(entries, 1):
            row = {"id": f"R{number:03d}", "verified": False}
            try:
                start, end = timestamp_ns(entry["started_utc"]), timestamp_ns(entry["finished_utc"])
                run_dir = (manifest_path.parent / entry["path"]).resolve()
                summary = read_json(run_dir / "summary.json")
                observer = read_json((manifest_path.parent / entry["observer_summary"]).resolve())
                identity = observer["controller_identity"]
                pid, created = integer(identity["pid"]), epoch_ns(identity["create_time"])
                # psutil exposes float seconds; allow <= 1 us solely for this binding,
                # and require an unambiguous exact ETW identity thereafter.
                bound = [key for key in processes if key[0] == pid and abs(key[1] - created) <= 1000]
                verification = summary.get("verification", {})
                if not isinstance(verification, dict) or not isinstance(verification.get("checks"), dict):
                    raise ValueError("invalid native verification")
                complete = (entry.get("backend") == "desktop" and entry.get("success") is True
                            and entry.get("controller_exit_code") == 0 and summary.get("backend") == "desktop"
                            and summary.get("status") == "completed" and summary.get("success") is True
                            and verification.get("passed") is True and verification.get("native_verified") is not False
                            and verification.get("errors") == [] and bool(verification.get("checks"))
                            and all(value is True for value in verification["checks"].values()))
                window_ok = origin <= start <= end <= ended
                before_windows = verified_windows["before-native"]
                after_windows = verified_windows["after-native"]
                bracketed = bool(before_windows and after_windows and max(stop for _, stop in before_windows) <= start and min(begin for begin, _ in after_windows) >= end)
                controller_ok = False
                if len(bound) == 1:
                    key = bound[0]
                    selected[key].add("native_controller")
                    process = processes[key]
                    starts, stops = process["starts"], process["stops"]
                    controller_ok = process["identity_valid"] and len(starts) == len(stops) == 1 and start <= starts[0].time <= stops[0].time <= end and stops[0].exit_code == 0
                    row["controller"] = aliases[key]
                focus_bound, focus_total = 0, 0
                focus_roles = defaultdict(set)
                for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines():
                    event = json.loads(line)
                    if event.get("event") != "window_focus":
                        continue
                    focus_total += 1
                    event_time = timestamp_ns(event["timestamp_utc"])
                    if not start <= event_time <= end:
                        raise ValueError("focus event outside native trial")
                    focus_pid = integer(event["pid"])
                    if event.get("app") in FOCUS_ROLES:
                        focus_roles[focus_pid].add(FOCUS_ROLES[event["app"]])
                    candidates = [key for key, process in processes.items() if key[0] == focus_pid and key[1] <= event_time and not any(stop.time < event_time for stop in process["stops"])]
                    if len(candidates) == 1:
                        selected[candidates[0]].add("native_window_process")
                        focus_bound += 1
                cohort_events = [event for event in events if start <= event.time <= end and processes[(event.pid, event.created)]["role"] in APPLICATION_ROLES]
                cohort_keys = {(event.pid, event.created) for event in cohort_events}
                for key in cohort_keys:
                    selected[key].add("native_application_cohort")
                cohort_counts = Counter((processes[(event.pid, event.created)]["role"], event.kind) for event in cohort_events)
                parent_matches, resolved_chains = Counter(), Counter()
                for event in cohort_events:
                    if event.kind != "start":
                        continue
                    key = (event.pid, event.created)
                    process = processes[key]
                    if event.parent_pid in focus_roles and len(focus_roles[event.parent_pid]) == 1:
                        focused_role = next(iter(focus_roles[event.parent_pid]))
                        parent_matches[(process["role"], focused_role)] += 1
                        parent_focus_matches[key].add(focused_role)
                    parent = process["parent"]
                    if parent is not None:
                        resolved_chains[(process["role"], processes[parent]["role"])] += 1
                row["application_cohort"] = {
                    "selection": "allowlisted application lifecycle events within native trial; shared cohort, task causation not established",
                    "identity_count": len(cohort_keys),
                    "event_counts": [{"application_role": app_role, "event": kind, "count": count} for (app_role, kind), count in sorted(cohort_counts.items())],
                    "reported_parent_id_focus_matches": [{"child_role": child_role, "focused_parent_role": parent_role, "start_events": count}
                                                         for (child_role, parent_role), count in sorted(parent_matches.items())],
                    "reported_parent_id_match_scope": "ETW ParentProcessID equals controller-reported focused PID; this comparison does not resolve the parent lifetime identity",
                    "resolved_etw_parent_chains": [{"child_role": child_role, "parent_role": parent_role, "start_events": count}
                                                  for (child_role, parent_role), count in sorted(resolved_chains.items())],
                }
                row.update({"native_task_verified": complete, "inside_trace_window": window_ok,
                            "bracketed_by_verified_canaries": bracketed, "controller_lifecycle_verified": controller_ok,
                            "focus_events": focus_total, "focus_events_with_resolved_identity": focus_bound,
                            "focus_bindings_complete": focus_total > 0 and focus_bound == focus_total,
                            "start_seconds": relative(start, origin), "end_seconds": relative(end, origin),
                            "steps_completed": integer(summary["steps_completed"]), "steps_total": integer(summary["steps_total"])})
                row["verified"] = complete and window_ok and bracketed and controller_ok and focus_total > 0 and row["steps_completed"] == row["steps_total"]
            except (OSError, KeyError, ValueError, TypeError, OverflowError):
                row["validation_error"] = "native_trial_evidence_invalid"
            runs.append(row)
        if not runs or not all(row["verified"] for row in runs):
            errors.add("native_trace_overlap_not_verified")
    # Export only selected task/canary processes and their evidenced ancestors.
    for key in list(selected):
        visited = {key}
        parent = processes[key]["parent"]
        while parent is not None and parent not in visited:
            visited.add(parent)
            selected[parent].add("selected_process_ancestor")
            parent = processes[parent]["parent"]
    public_events = []
    for event in events:
        key = (event.pid, event.created)
        if key not in selected:
            continue
        process = processes[key]
        record = {"process": aliases[key], "event": event.kind, "at_seconds": relative(event.time, origin),
                  "application_role": process["role"], "selection": sorted(selected[key]),
                  "parent_process": aliases.get(process["parent"]), "identity_valid": process["identity_valid"]}
        if event.kind == "stop":
            record["exit_code"] = event.exit_code & 0xFFFFFFFF
        if event.kind == "start" and key in parent_focus_matches:
            record["reported_parent_id_focus_role_matches"] = sorted(parent_focus_matches[key])
            record["reported_parent_id_match_scope"] = "ETW ParentProcessID versus controller window-focus PID; parent lifetime identity not established by this comparison"
        public_events.append(record)
    hashes = {name: hash_file(capture_dir / filename) for name, filename in (("raw_etl_sha256", "process-events.etl"), ("raw_xml_sha256", "process-events.xml"), ("capture_status_sha256", "capture-status.json"), ("canary_ground_truth_sha256", "canary-ground-truth.json"))}
    hashes["analyzer_source_sha256"] = hash_file(Path(__file__))
    hashes["collector_source_sha256"] = hash_file(Path(__file__).parent / "capture_process_events.ps1")
    hashes["validation_worker_source_sha256"] = hash_file(Path(__file__).parent / "run_event_validation.py")
    hashes["decoder_source_sha256"] = hash_file(Path(__file__).parent / "decode_process_events.ps1")
    hashes["capture_ready_sha256"] = hash_file(capture_dir / "capture-ready.json")
    recorded_hash = ground.get("worker_source_sha256")
    hashes["recorded_validation_worker_source_sha256"] = recorded_hash if isinstance(recorded_hash, str) and re.fullmatch(r"[0-9a-f]{64}", recorded_hash) else None
    try:
        recorded_hash = read_json(capture_dir / "capture-ready.json").get("script_sha256")
        hashes["recorded_collector_source_sha256"] = recorded_hash if isinstance(recorded_hash, str) and re.fullmatch(r"[0-9a-f]{64}", recorded_hash) else None
    except (OSError, ValueError):
        hashes["recorded_collector_source_sha256"] = None
    if canonical_path.exists() or decode_status_path.exists():
        hashes["canonical_xml_sha256"] = hash_file(canonical_path)
        hashes["canonical_decode_status_sha256"] = hash_file(decode_status_path)
        recorded_hash = decode_metadata.get("decoder_script_sha256") if isinstance(decode_metadata, dict) else None
        hashes["recorded_decoder_source_sha256"] = recorded_hash if isinstance(recorded_hash, str) and re.fullmatch(r"[0-9a-f]{64}", recorded_hash) else None
    if manifest_path is not None:
        hashes["native_manifest_sha256"] = hash_file(manifest_path)
    if not hashes["raw_etl_sha256"]:
        errors.add("raw_etl_missing")
    for name, filename in (("etl", "process-events.etl"), ("xml", "process-events.xml")):
        try:
            item = status[name]
            path = capture_dir / filename
            if item["sha256"] != hash_file(path) or integer(item["bytes"]) != path.stat().st_size:
                raise ValueError("hash or size mismatch")
        except (OSError, KeyError, ValueError, TypeError):
            errors.add("raw_artifact_integrity_not_verified")
    lifetimes = [row["lifetime_ms"] for row in canaries if row["verified"]]
    lifetime_stats = {"verified_count": len(lifetimes), "min_ms": min(lifetimes) if lifetimes else None,
                      "median_ms": statistics.median(lifetimes) if lifetimes else None, "max_ms": max(lifetimes) if lifetimes else None,
                      "count_under_100_ms": sum(value < 100 for value in lifetimes),
                      "method": "ProcessStop payload ExitTime minus process CreateTime; not an assumed canary duration"}
    summary = {"schema_version": 1, "evidence_source": "Microsoft-Windows-Kernel-Process", "provider_guid": PROVIDER,
               "validation_passed": not errors, "universal_completeness_claim": False,
               "analyzed_xml_decoder": decoder,
               "validation_worker_lifecycle_verified": worker_verified,
               "zero_reported_logger_loss": zero_loss, "final_loss_counters": counters,
               "capture_duration_seconds": relative(ended, origin) if ended else None,
               "parse_counts": dict(sorted(counts.items())), "identity_issue_counts": dict(sorted(issues.items())),
               "known_canary_count": len(canaries), "verified_canary_count": sum(row["verified"] for row in canaries),
               "expected_canary_count": 28, "expected_canary_protocol_matched": observed_protocol == expected_protocol,
               "known_canary_lifetime_statistics": lifetime_stats,
               "canaries": canaries, "native_runs": runs, "selected_process_count": len(selected),
               "selected_event_count": len(public_events), "unselected_process_count": len(processes) - len(selected),
               "unselected_event_counts": dict(sorted(Counter(event.kind for event in events if (event.pid, event.created) not in selected).items())),
               "hashes": hashes, "validation_errors": sorted(errors), "limitations": LIMITATIONS}
    return summary, public_events


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, help="Optional native benchmark manifest captured inside this trace")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    summary, events = analyze_capture(args.capture_dir, args.manifest)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "process-event-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "process-events-public.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
    print(json.dumps({"validation_passed": summary["validation_passed"], "verified_canaries": summary["verified_canary_count"], "known_canaries": summary["known_canary_count"], "native_runs": len(summary["native_runs"]), "errors": summary["validation_errors"]}))
    return 0 if summary["validation_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
