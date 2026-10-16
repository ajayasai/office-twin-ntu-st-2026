from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from xml.sax.saxutils import escape

from tools.analyze_process_events import PROVIDER, analyze_capture, build_processes, read_xml, timestamp_ns


BASE = datetime(2026, 10, 16, 8, tzinfo=timezone.utc)


def stamp(seconds):
    return (BASE + timedelta(seconds=seconds)).isoformat(timespec="microseconds")


def filetime(seconds):
    return str((timestamp_ns(stamp(seconds)) // 100) + 116444736000000000)


def event(kind, pid, created, at=None, parent=100, code=0, sequence=None, parent_sequence=None,
          name="C:\\Users\\PRIVATE_ACCOUNT\\python.exe", hex_numbers=False):
    values = {"ProcessID": hex(pid) if hex_numbers else str(pid), "CreateTime": filetime(created), "ImageName": name,
              "CommandLine": "PRIVATE_COMMAND_LINE", "Sid": "PRIVATE_SID"}
    if kind in (1, 15):
        values["ParentProcessID"] = hex(parent) if hex_numbers else str(parent)
    if kind == 2:
        values["ExitCode"] = hex(code) if hex_numbers else str(code)
        values["ExitTime"] = filetime(created if at is None else at)
    if sequence is not None:
        values["ProcessSequenceNumber"] = str(sequence)
    if parent_sequence is not None:
        values["ParentProcessSequenceNumber"] = str(parent_sequence)
    data = "".join(f'<Data Name="{key}">{escape(value)}</Data>' for key, value in values.items())
    return f'<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event"><System><Provider Guid="{{{PROVIDER}}}"/><EventID>{kind}</EventID><TimeCreated SystemTime="{stamp(created if at is None else at)}"/></System><EventData>{data}</EventData></Event>'


class TraceFixture:
    def __init__(self, directory):
        self.root = Path(directory)
        self.xml_events = [event(15, 9, -100, at=0.2, parent=0, name="C:\\Windows\\explorer.exe"),
                           event(1, 100, 1, parent=9), event(2, 100, 1, at=31),
                           event(1, 101, 3), event(2, 101, 3, at=4),
                           event(1, 102, 25), event(2, 102, 25, at=26, code=7)]
        self.ready = {"session_name": "PRIVATE_SESSION"}
        self.ground = {"status": "completed", "controller_pid": 100, "started_utc": stamp(2),
                       "finished_utc": stamp(30), "capture_session": "PRIVATE_SESSION", "canaries": [
                           {"pid": 101, "parent_pid": 100, "expected_exit_code": 0, "actual_exit_code": 0,
                            "launch_before_utc": stamp(2.9), "wait_finished_utc": stamp(4.1), "phase": "before-native", "kind": "short-lived-child"},
                           {"pid": 102, "parent_pid": 100, "expected_exit_code": 7, "actual_exit_code": 7,
                            "launch_before_utc": stamp(24.9), "wait_finished_utc": stamp(26.1), "phase": "after-native", "kind": "short-lived-child"}]}
        self.status = {"status": "captured_pending_verification", "finalized": True, "trace_started_utc": stamp(0),
                       "trace_stopped_utc": stamp(32), "final_loss_counters_available": True, "stop_reason": "stop_request",
                       "loss_counters": {"events_lost": 0, "log_buffers_lost": 0, "real_time_buffers_lost": 0},
                       "conversion_exit_code": 0, "errors": [], "provider_guid": "{" + PROVIDER + "}", "session_name": "PRIVATE_SESSION"}
        for phase_index, (phase, offset) in enumerate((("before-native", 3), ("after-native", 25))):
            def add_canary(pid, parent, start, stop, kind):
                self.xml_events.extend([event(1, pid, start, parent=parent), event(2, pid, start, at=stop)])
                self.ground["canaries"].append({"pid": pid, "parent_pid": parent, "expected_exit_code": 0, "actual_exit_code": 0,
                                               "launch_before_utc": stamp(start - 0.001), "wait_finished_utc": stamp(stop + 0.001),
                                               "phase": phase, "kind": kind})
            for index in range(11):
                start = offset + 0.1 + index * 0.02
                add_canary(1000 + 100 * phase_index + index, 100, start, start + 0.01, "short-lived-child")
            intermediate = 1500 + phase_index
            add_canary(intermediate, 100, offset + 1.5, offset + 2, "intermediate-parent")
            add_canary(1600 + phase_index, intermediate, offset + 1.6, offset + 1.7, "nested-child")

    def save(self):
        (self.root / "process-events.etl").write_bytes(b"private raw trace fixture")
        (self.root / "process-events.xml").write_text("<?xml version='1.0'?><Events>" + "".join(self.xml_events) + "</Events>", encoding="utf-8")
        (self.root / "capture-ready.json").write_text(json.dumps(self.ready), encoding="utf-8")
        self.ground["capture_ready_sha256"] = hashlib.sha256((self.root / "capture-ready.json").read_bytes()).hexdigest()
        (self.root / "canary-ground-truth.json").write_text(json.dumps(self.ground), encoding="utf-8")
        for name, filename in (("etl", "process-events.etl"), ("xml", "process-events.xml")):
            data = (self.root / filename).read_bytes()
            self.status[name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        (self.root / "capture-status.json").write_text(json.dumps(self.status), encoding="utf-8")

    def native_manifest(self):
        self.xml_events.extend([event(1, 200, 11), event(2, 200, 11, at=14),
                                event(1, 201, 17), event(2, 201, 17, at=19),
                                event(15, 300, -10, at=0.3, parent=9, name="chrome.exe")])
        entries = []
        for name, mode, pid, created, start, end, focus in (("trial", "fixed", 200, 11, 10, 15, 13), ("trial2", "contextual", 201, 17, 16, 20, 18)):
            trial = self.root / "native" / name
            trial.mkdir(parents=True)
            (trial / "summary.json").write_text(json.dumps({"backend": "desktop", "status": "completed", "success": True, "verification": {"passed": True, "checks": {"text_content": True, "spreadsheet_headers": True, "spreadsheet_inputs": True, "spreadsheet_calculated_results": True}, "errors": []}, "steps_completed": 11, "steps_total": 11}), encoding="utf-8")
            (trial / "observer.json").write_text(json.dumps({"controller_identity": {"pid": pid, "create_time": (BASE + timedelta(seconds=created)).timestamp()}}), encoding="utf-8")
            (trial / "events.jsonl").write_text(json.dumps({"event": "window_focus", "timestamp_utc": stamp(focus), "pid": 300, "title": "PRIVATE_WINDOW_TITLE"}) + "\n", encoding="utf-8")
            entries.append({"path": name, "observer_summary": name + "/observer.json", "backend": "desktop", "success": True,
                            "timing": mode, "controller_exit_code": 0, "started_utc": stamp(start), "finished_utc": stamp(end)})
        manifest = self.root / "native" / "manifest.json"
        manifest.write_text(json.dumps({"status": "completed", "runs": entries}), encoding="utf-8")
        return manifest


class EventTraceAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = TraceFixture(self.temp.name)

    def analyze(self):
        self.fixture.save()
        return analyze_capture(self.fixture.root)

    def rundown_manifest(self, parent=9):
        manifest = self.fixture.native_manifest()
        self.fixture.xml_events[0] = event(15, 9, -100, at=0.2, parent=0, sequence=9, name="explorer.exe")
        self.fixture.xml_events[-1] = event(15, 300, -10, at=0.3, parent=parent, sequence=3000, parent_sequence=9 if parent == 9 else 999, name="chrome.exe")
        self.fixture.xml_events.extend([event(15, 9, -100, at=31.1, parent=0, sequence=9, name="explorer.exe"),
                                        event(15, 300, -10, at=31.2, parent=parent, sequence=3000, parent_sequence=9 if parent == 9 else 999, name="chrome.exe")])
        self.fixture.ready["request_rundown"] = True
        self.fixture.ground["require_rundown"] = True
        identities = [{"pid": 300, "create_time_filetime": filetime(-10), "parent_pid": parent, "name": "C:\\PRIVATE_PROFILE\\chrome.exe", "identity_rechecked": True},
                      {"pid": 9, "create_time_filetime": filetime(-100), "parent_pid": 0, "name": "explorer.exe", "identity_rechecked": True}]
        self.fixture.ground["rundown_identity_snapshots"] = [
            {"phase": "before-native", "source": "Toolhelp32Snapshot+GetProcessTimes", "started_utc": stamp(8), "finished_utc": stamp(9), "processes": deepcopy(identities)},
            {"phase": "after-native", "source": "Toolhelp32Snapshot+GetProcessTimes", "started_utc": stamp(21), "finished_utc": stamp(22), "processes": deepcopy(identities)},
        ]
        for name in ("trial", "trial2"):
            path = manifest.parent / name / "events.jsonl"
            focus = json.loads(path.read_text(encoding="utf-8"))
            focus["app"] = "browser"
            path.write_text(json.dumps(focus) + "\n", encoding="utf-8")
        return manifest

    def test_rundown_focus_identity_and_parent_sequence_match_two_independent_snapshots(self):
        manifest = self.rundown_manifest()
        self.fixture.ground["require_application_parents"] = True
        self.fixture.save()
        summary, events = analyze_capture(self.fixture.root, manifest)
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        check = summary["rundown_focus_validation"]
        self.assertTrue(check["verified"])
        self.assertEqual(check["verified_focus_event_count"], 2)
        self.assertTrue(check["all_immediate_application_parents_verified"])
        record = check["focused_processes"][0]
        self.assertEqual(record["parent_resolution_method"], "process-sequence-number")
        self.assertTrue(record["stable_identity_in_both_os_snapshots"])
        self.assertTrue(record["parent_identity_stable_in_both_os_snapshots"])
        self.assertFalse(any(row["event"] == "start" and row["process"] == record["process"] for row in events))
        self.assertNotIn("PRIVATE_PROFILE", json.dumps([summary, events]))

    def test_rundown_request_success_cannot_replace_actual_after_rundown(self):
        manifest = self.rundown_manifest()
        self.fixture.xml_events.pop()
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertFalse(summary["rundown_focus_validation"]["verified"])
        self.assertFalse(summary["validation_passed"])

    def test_rundown_snapshot_pid_reuse_or_role_mismatch_fails_exact_binding(self):
        manifest = self.rundown_manifest()
        snapshot_row = self.fixture.ground["rundown_identity_snapshots"][1]["processes"][0]
        snapshot_row["create_time_filetime"] = filetime(-9)
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertFalse(summary["rundown_focus_validation"]["verified"])
        snapshot_row["create_time_filetime"] = filetime(-10)
        snapshot_row["name"] = "PRIVATE_DIFFERENT_APP.exe"
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertFalse(summary["rundown_focus_validation"]["verified"])
        self.assertNotIn("PRIVATE_DIFFERENT_APP", json.dumps(summary))

    def test_exited_original_parent_remains_separate_from_verified_warm_identity(self):
        manifest = self.rundown_manifest(parent=8877)
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        check = summary["rundown_focus_validation"]
        self.assertTrue(check["verified"])
        self.assertFalse(check["all_immediate_application_parents_verified"])
        self.assertTrue(check["focused_processes"][0]["terminal_parent_gap"])
        self.fixture.ground["require_application_parents"] = True
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertFalse(summary["validation_passed"])

    def test_newly_started_focus_process_does_not_require_prebirth_snapshot(self):
        manifest = self.rundown_manifest()
        self.fixture.xml_events = [value for value in self.fixture.xml_events if not ('<Data Name="ProcessID">300</Data>' in value)]
        self.fixture.xml_events.extend([event(1, 300, 12, parent=9, name="chrome.exe"), event(2, 300, 12, at=14, name="chrome.exe"),
                                        event(1, 301, 17, parent=9, name="chrome.exe"), event(2, 301, 17, at=19, name="chrome.exe")])
        path = manifest.parent / "trial2" / "events.jsonl"
        focus = json.loads(path.read_text(encoding="utf-8"))
        focus["pid"] = 301
        path.write_text(json.dumps(focus) + "\n", encoding="utf-8")
        for snapshot in self.fixture.ground["rundown_identity_snapshots"]:
            snapshot["processes"] = [row for row in snapshot["processes"] if row["pid"] != 300]
        self.fixture.ground["require_application_parents"] = True
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        records = summary["rundown_focus_validation"]["focused_processes"]
        self.assertEqual(len(records), 2)
        self.assertTrue(all(row["verified"] and row["observed_exit_after_last_focus"] for row in records))
        self.assertTrue(all(not row["preexisting_at_trace_start"] for row in records))

    def test_parent_exit_payload_prevents_false_ancestry_during_delayed_stop_event(self):
        self.fixture.xml_events.extend([
            event(1, 700, 7, parent=100),
            event(2, 700, 7, at=9).replace('<Data Name="ExitTime">' + filetime(9), '<Data Name="ExitTime">' + filetime(8)),
            event(1, 701, 8.5, parent=700),
        ])
        self.fixture.save()
        events, _ = read_xml(self.fixture.root / "process-events.xml")
        processes, _ = build_processes(events)
        child = processes[(701, timestamp_ns(stamp(8.5)))]
        self.assertIsNone(child["parent"])

    def test_conflicting_parent_sequence_observations_remain_unresolved(self):
        self.fixture.xml_events.extend([event(1, 700, 7, parent=100, sequence=700),
                                        event(1, 701, 8, parent=700, parent_sequence=700),
                                        event(15, 701, 8, at=9, parent=700, parent_sequence=999)])
        self.fixture.save()
        events, _ = read_xml(self.fixture.root / "process-events.xml")
        processes, _ = build_processes(events)
        self.assertIsNone(processes[(701, timestamp_ns(stamp(8)))]["parent"])

    def test_system_idle_rundown_is_counted_but_not_a_task_identity_or_parse_failure(self):
        self.fixture.xml_events.append(event(15, 0, -100, at=0.1, parent=0, sequence=0, parent_sequence=0xFFFFFFFFFFFFFFFF, name="Idle").replace(filetime(-100), "0"))
        summary, events = self.analyze()
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        self.assertEqual(summary["parse_counts"]["system_idle_rundown_excluded"], 1)
        self.assertEqual(summary["parse_counts"]["rundown"], 2)
        self.assertNotIn("invalid_process_events", summary["parse_counts"])
        self.assertFalse(any(row["application_role"] == "idle" for row in events))

    def test_unavailable_parent_sequence_sentinel_cannot_bind_a_reused_parent_pid(self):
        manifest = self.rundown_manifest()
        self.fixture.xml_events = [value.replace('<Data Name="ParentProcessSequenceNumber">9</Data>', '<Data Name="ParentProcessSequenceNumber">18446744073709551615</Data>') if '<Data Name="ProcessID">300</Data>' in value else value for value in self.fixture.xml_events]
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        record = summary["rundown_focus_validation"]["focused_processes"][0]
        self.assertTrue(record["unavailable_parent_sequence_reported"])
        self.assertTrue(record["terminal_parent_gap"])
        self.assertIsNone(record["parent_process"])

    def test_known_canaries_and_worker_verified_without_universal_claim(self):
        summary, events = self.analyze()
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        self.assertEqual(summary["verified_canary_count"], 28)
        self.assertTrue(summary["validation_worker_lifecycle_verified"])
        self.assertFalse(summary["universal_completeness_claim"])
        self.assertEqual(summary["parse_counts"]["start"], 29)
        self.assertEqual(summary["parse_counts"]["rundown"], 1)
        self.assertEqual(summary["known_canary_lifetime_statistics"]["count_under_100_ms"], 22)
        self.assertTrue(any(row["parent_process"] for row in events if "known_canary" in row["selection"]))

    def test_rundown_cannot_replace_missing_canary_start(self):
        self.fixture.xml_events[3] = event(15, 101, 3, at=3.1)
        summary, _ = self.analyze()
        self.assertFalse(summary["validation_passed"])
        self.assertEqual(summary["canaries"][0]["observed_starts"], 0)

    def test_missing_stop_fails_even_if_exit_ground_truth_exists(self):
        self.fixture.xml_events.pop(4)
        summary, _ = self.analyze()
        self.assertIn("known_canary_coverage_not_verified", summary["validation_errors"])

    def test_wrong_exit_or_parent_cannot_verify(self):
        for replacement in (event(2, 101, 3, at=4, code=7), event(1, 101, 3, parent=9)):
            fixture = self.fixture
            index = 4 if "<EventID>2" in replacement else 3
            original = fixture.xml_events[index]
            fixture.xml_events[index] = replacement
            summary, _ = self.analyze()
            self.assertFalse(summary["canaries"][0]["verified"])
            fixture.xml_events[index] = original

    def test_missing_or_nonzero_loss_counters_fail_closed(self):
        original = deepcopy(self.fixture.status)
        for value in (None, {"events_lost": 0}, {"events_lost": 1, "log_buffers_lost": 0, "real_time_buffers_lost": 0}):
            self.fixture.status = deepcopy(original)
            self.fixture.status["loss_counters"] = value
            summary, _ = self.analyze()
            self.assertFalse(summary["validation_passed"])
            self.assertFalse(summary["zero_reported_logger_loss"])

    def test_duration_stop_or_unfinalized_capture_fails(self):
        self.fixture.status["stop_reason"] = "duration_limit"
        summary, _ = self.analyze()
        self.assertIn("capture_final_status_not_successful", summary["validation_errors"])
        self.fixture.status["finalized"] = False
        summary, _ = self.analyze()
        self.assertIn("capture_not_finalized", summary["validation_errors"])

    def test_pid_reuse_does_not_pair_old_stop_with_new_start(self):
        self.fixture.xml_events[4] = event(2, 101, 2, at=4)
        summary, _ = self.analyze()
        self.assertFalse(summary["canaries"][0]["verified"])
        self.assertEqual(summary["canaries"][0]["observed_stops"], 0)

    def test_sequence_collision_fails_even_when_pid_times_look_valid(self):
        self.fixture.xml_events[3] = event(1, 101, 3, sequence=50)
        self.fixture.xml_events[5] = event(1, 102, 25, sequence=50)
        summary, _ = self.analyze()
        self.assertIn("process_identity_or_lifecycle_conflict", summary["validation_errors"])

    def test_hex_identifiers_and_filetime_precision(self):
        self.fixture.xml_events[3] = event(1, 101, 3, hex_numbers=True)
        self.fixture.xml_events[4] = event(2, 101, 3, at=4, hex_numbers=True)
        summary, _ = self.analyze()
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        self.assertEqual(timestamp_ns("2026-10-16T08:00:00.1234567Z") % 1_000_000_000, 123456700)
        self.assertEqual(timestamp_ns("0x" + format(int(filetime(3)), "x"), creation=True), timestamp_ns(stamp(3)))

    def test_bad_event_or_truncated_xml_fails(self):
        self.fixture.xml_events.append(event(1, 555, 9).replace('Name="CreateTime"', 'Name="MissingCreateTime"'))
        summary, _ = self.analyze()
        self.assertIn("process_event_parse_failed", summary["validation_errors"])
        self.fixture.save()
        path = self.fixture.root / "process-events.xml"
        path.write_text(path.read_text(encoding="utf-8")[:-8], encoding="utf-8")
        summary, _ = analyze_capture(self.fixture.root)
        self.assertIn("process_event_parse_failed", summary["validation_errors"])
        self.assertIn("raw_artifact_integrity_not_verified", summary["validation_errors"])

    def test_public_export_contains_no_arbitrary_private_strings_or_raw_ids(self):
        self.fixture.xml_events.extend([event(1, 987654, 5, name="PRIVATE_UNRELATED.exe"), event(2, 987654, 5, at=6, name="PRIVATE_UNRELATED.exe")])
        summary, events = self.analyze()
        serialized = json.dumps([summary, events])
        for secret in ("PRIVATE", "987654", "C:\\", "2026-10-16", "CommandLine", "Sid", '"pid"', '"parent_pid"'):
            self.assertNotIn(secret, serialized)
        self.assertEqual(summary["unselected_process_count"], 1)
        self.assertEqual(summary["unselected_event_counts"], {"start": 1, "stop": 1})

    def test_manifest_requires_task_success_complete_controller_and_boundaries(self):
        manifest = self.fixture.native_manifest()
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertTrue(summary["validation_passed"], summary)
        self.assertTrue(summary["native_runs"][0]["verified"])
        self.fixture.status["trace_stopped_utc"] = stamp(12)
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertFalse(summary["native_runs"][0]["verified"])
        self.assertFalse(summary["native_runs"][0]["inside_trace_window"])

    def test_native_interval_must_be_between_before_and_after_canaries(self):
        manifest = self.fixture.native_manifest()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["runs"][0]["started_utc"] = stamp(3)
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertFalse(summary["native_runs"][0]["bracketed_by_verified_canaries"])
        self.assertFalse(summary["validation_passed"])

    def test_missing_ground_truth_returns_failed_summary(self):
        self.fixture.save()
        (self.fixture.root / "canary-ground-truth.json").unlink()
        summary, _ = analyze_capture(self.fixture.root)
        self.assertFalse(summary["validation_passed"])
        self.assertEqual(summary["known_canary_count"], 0)

    def test_native_simulation_or_failed_output_cannot_verify(self):
        manifest = self.fixture.native_manifest()
        path = manifest.parent / "trial" / "summary.json"
        original = json.loads(path.read_text(encoding="utf-8"))
        for replacement in ({**original, "backend": "simulate"},
                            {**original, "verification": {**original["verification"], "native_verified": False}},
                            {**original, "verification": {**original["verification"], "checks": {"text_content": False}}}):
            path.write_text(json.dumps(replacement), encoding="utf-8")
            self.fixture.save()
            summary, _ = analyze_capture(self.fixture.root, manifest)
            self.assertFalse(summary["native_runs"][0]["native_task_verified"])
            self.assertFalse(summary["validation_passed"])

    def test_unmatched_ready_marker_or_incomplete_worker_fails(self):
        self.fixture.ground["capture_session"] = "different_private_session"
        summary, _ = self.analyze()
        self.assertFalse(summary["validation_worker_lifecycle_verified"])
        self.fixture.ground["capture_session"] = "PRIVATE_SESSION"
        self.fixture.xml_events.pop(2)  # The worker itself must have an observed stop.
        summary, _ = self.analyze()
        self.assertFalse(summary["validation_worker_lifecycle_verified"])

    def test_missing_worker_identity_and_duplicate_canary_cannot_verify(self):
        del self.fixture.ground["controller_pid"]
        summary, _ = self.analyze()
        self.assertFalse(summary["validation_passed"])
        self.assertFalse(summary["validation_worker_lifecycle_verified"])
        self.fixture.ground["controller_pid"] = 100
        self.fixture.ground["canaries"][1] = {**self.fixture.ground["canaries"][0], "phase": "after-native"}
        summary, _ = self.analyze()
        self.assertFalse(summary["validation_passed"])
        self.assertFalse(summary["canaries"][1]["verified"])

    def test_json_arrays_are_rejected_without_exporting_source_data(self):
        self.fixture.save()
        (self.fixture.root / "capture-status.json").write_text('["PRIVATE_BAD_STATUS"]', encoding="utf-8")
        summary, _ = analyze_capture(self.fixture.root)
        self.assertFalse(summary["validation_passed"])
        self.assertNotIn("PRIVATE_BAD_STATUS", json.dumps(summary))

    def test_missing_protocol_canary_or_native_mode_is_not_a_complete_capture(self):
        self.fixture.ground["canaries"].pop()
        summary, _ = self.analyze()
        self.assertIn("expected_28_canary_protocol_not_met", summary["validation_errors"])
        manifest = self.fixture.native_manifest()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["runs"][1]["timing"] = "fixed"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertIn("expected_native_timing_pair_not_met", summary["validation_errors"])

    def test_preexisting_window_without_rundown_is_reported_as_unresolved(self):
        manifest = self.fixture.native_manifest()
        self.fixture.xml_events.pop()  # Existing Chrome is absent from the provider's rundown.
        self.fixture.save()
        summary, events = analyze_capture(self.fixture.root, manifest)
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        self.assertFalse(summary["native_runs"][0]["focus_bindings_complete"])
        self.assertEqual(summary["native_runs"][0]["focus_events_with_resolved_identity"], 0)
        self.assertFalse(any(row["application_role"] == "chrome" for row in events))

    def test_application_cohort_distinguishes_pid_only_matches_from_resolved_parent_lifetimes(self):
        manifest = self.fixture.native_manifest()
        self.fixture.xml_events.pop()  # Focused Chrome PID 300 predates this trace; no invented rundown.
        self.fixture.xml_events.extend([
            event(1, 400, 12, parent=300, name="C:\\PRIVATE_BROWSER_PROFILE\\chrome.exe"),
            event(2, 400, 12, at=14, name="chrome.exe"),
            event(1, 401, 12.5, parent=400, name="chrome.exe"),
            event(2, 401, 12.5, at=13.5, name="chrome.exe"),
            event(1, 500, 14, parent=100, name="PRIVATE_UNRELATED.exe"),
            event(2, 500, 14, at=14.5, name="PRIVATE_UNRELATED.exe"),
        ])
        # The controller's app label provides only a focused PID comparison.
        path = manifest.parent / "trial" / "events.jsonl"
        focus = json.loads(path.read_text(encoding="utf-8"))
        focus["app"] = "browser"
        path.write_text(json.dumps(focus) + "\n", encoding="utf-8")
        self.fixture.save()
        summary, events = analyze_capture(self.fixture.root, manifest)
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        run = summary["native_runs"][0]
        self.assertEqual(run["focus_events_with_resolved_identity"], 0)
        cohort = run["application_cohort"]
        self.assertEqual(cohort["identity_count"], 2)
        self.assertEqual(cohort["reported_parent_id_focus_matches"], [{"child_role": "chrome", "focused_parent_role": "chrome", "start_events": 1}])
        self.assertEqual(cohort["resolved_etw_parent_chains"], [{"child_role": "chrome", "parent_role": "chrome", "start_events": 1}])
        starts = [row for row in events if row["event"] == "start" and "native_application_cohort" in row["selection"]]
        self.assertEqual(len(starts), 2)
        self.assertIsNone(starts[0]["parent_process"])
        self.assertEqual(starts[0]["reported_parent_id_focus_role_matches"], ["chrome"])
        self.assertIn("not established", starts[0]["reported_parent_id_match_scope"])
        self.assertEqual(starts[1]["parent_process"], starts[0]["process"])
        self.assertNotIn("reported_parent_id_focus_role_matches", starts[1])
        public = json.dumps([summary, events])
        for secret in ("PRIVATE", "C:\\", '"pid"', '"parent_pid"', '"title"'):
            self.assertNotIn(secret, public)

    def test_canonical_decoder_requires_raw_etl_hash_and_exact_event_count(self):
        self.fixture.save()
        canonical = self.fixture.root / "process-events-winapi.xml"
        canonical.write_bytes((self.fixture.root / "process-events.xml").read_bytes())
        status = {"status": "decoded", "decoder": "Get-WinEvent.ToXml", "errors": [], "decoded_event_count": 59,
                  "source_etl_sha256": hashlib.sha256((self.fixture.root / "process-events.etl").read_bytes()).hexdigest(),
                  "xml_sha256": hashlib.sha256(canonical.read_bytes()).hexdigest()}
        path = self.fixture.root / "winapi-decode-status.json"
        path.write_text(json.dumps(status), encoding="utf-8")
        summary, _ = analyze_capture(self.fixture.root)
        self.assertTrue(summary["validation_passed"], summary["validation_errors"])
        self.assertEqual(summary["analyzed_xml_decoder"], "Get-WinEvent.ToXml")
        status["decoded_event_count"] -= 1
        path.write_text(json.dumps(status), encoding="utf-8")
        summary, _ = analyze_capture(self.fixture.root)
        self.assertIn("canonical_decode_event_count_mismatch", summary["validation_errors"])
        status["source_etl_sha256"] = "0" * 64
        path.write_text(json.dumps(status), encoding="utf-8")
        summary, _ = analyze_capture(self.fixture.root)
        self.assertIn("canonical_decode_integrity_not_verified", summary["validation_errors"])

    def test_tracerpt_timezone_bug_is_not_silently_corrected(self):
        # Actual Windows tracerpt emitted a local wall time with +07:59 while
        # the ETL decoded independently through Get-WinEvent correctly uses UTC.
        self.fixture.xml_events = [value.replace('SystemTime="2026-10-16T08:', 'SystemTime="2026-10-16T16:').replace('+00:00"/>', '+07:59"/>') for value in self.fixture.xml_events]
        summary, _ = self.analyze()
        self.assertFalse(summary["validation_passed"])
        self.assertEqual(summary["verified_canary_count"], 0)

    def test_failed_manifest_keeps_attempted_runs_visible(self):
        manifest = self.fixture.native_manifest()
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["status"] = "stopped"
        data["runs"] = data["runs"][:1]
        data["runs"][0]["success"] = False
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.fixture.save()
        summary, _ = analyze_capture(self.fixture.root, manifest)
        self.assertEqual(len(summary["native_runs"]), 1)
        self.assertFalse(summary["native_runs"][0]["verified"])
        self.assertIn("native_manifest_incomplete", summary["validation_errors"])

    def test_reused_parent_pid_requires_unambiguous_lifetime_or_sequence(self):
        self.fixture.xml_events.append(event(15, 100, -50, at=0.1, parent=9))
        summary, _ = self.analyze()
        self.assertFalse(summary["canaries"][0]["parent_identity_resolved"])
        # The old identity has no observed exit: an exact sequence reference,
        # rather than newest-PID heuristics, can still disambiguate the parent.
        self.fixture.xml_events[1] = event(1, 100, 1, parent=9, sequence=20)
        self.fixture.xml_events[-1] = event(15, 100, -50, at=0.1, parent=9, sequence=10)
        self.fixture.xml_events[3] = event(1, 101, 3, parent_sequence=20)
        self.fixture.xml_events[5] = event(1, 102, 25, parent_sequence=20)
        summary, _ = self.analyze()
        self.assertTrue(summary["canaries"][0]["parent_identity_resolved"])


if __name__ == "__main__":
    unittest.main()
