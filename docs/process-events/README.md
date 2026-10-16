# Verified Windows process events — 16 October 2026

**The retry passed the complete defined validation protocol: 28/28 known process lifecycles, both native controller lifecycles, and two native tasks completing 11/11 steps with checked outputs.** All three final ETW loss counters were zero. This is bounded process-event evidence for this capture, not a claim that every possible system event or preexisting application ancestor was observed.

The process-only `Microsoft-Windows-Kernel-Process` capture ran for **393.982 seconds** on the same warm, shared Windows host. An elevated temporary collector recorded events while Office Twin and its validation worker ran unelevated. The fixed/contextual pair used seed 307 and normal timing scale 1, with the separate sampled observer also enabled. These trials are not pooled into the earlier ten-run timing or resource benchmark.

| Check | Verified result |
| --- | --- |
| Decoded provider records | 344: 172 starts, 172 stops, no rundown |
| Final EventsLost / LogBuffersLost / RealTimeBuffersLost | 0 / 0 / 0 |
| Known lifecycle checks | 28/28; start, stop, expected parent chain and exit status |
| Before/after task checks | 14 known processes before the native pair; 14 afterward |
| Short-lived processes | 24/28 lived under 100 ms; measured minimum 54.212 ms, median 59.998 ms, maximum 400.549 ms |
| Native output verification | Fixed 11/11; contextual 11/11; both passed saved text and reloaded Sheet value checks |
| Controller boundaries | Both native controllers and the validation worker resolved inside the trace |
| Collector scheduling | Maximum loop gap 0.235 s; no deadline overrun |
| Historical automated suite | 120 tests passed, including event parsing/export and guarded-worker tests |

Canaries are deliberately launched test processes, separate from the office workflow. Their short lifetimes are measured from ETW creation and exit payloads, not assumed from polling intervals. They test capture behavior; they are not evidence of human-like application behavior.

## Application events and ancestry boundaries

Within the two native trial windows, the nonexclusive application cohort contains **14 Chrome start records and four Notepad start records**, plus 14 Chrome and four Notepad stop records. These equal event counts are not 18 paired lifetimes: 16 starts pair with stops inside the same individual trial window; each trial also contains one start-only and one stop-only cohort identity. Three Chrome child starts resolve to parent Chrome lifetimes present in ETW. A separate comparison finds 15 parent-ID matches against controller-observed focused processes: three Chrome starts match the focused Explorer PID, four Notepad starts match Explorer, and eight Chrome starts match the already-running Chrome PID.

Those 15 comparisons match reported IDs only. They do not establish the preexisting parent's lifetime identity or prove that Office Twin caused every event in the shared application cohort. No raw process IDs, command lines, executable paths or window titles are published.

All **33 focus observations** refer to three main application processes already running before capture. None has a start, stop or rundown record in this window, so **0/33 focus bindings resolve to an ETW lifetime**. Their missing starts are not fabricated. The original ten-run [sampled parent observations](../benchmark/process-parent-evidence.md) remain a separate evidence source. Complete ancestry of those preexisting applications is still an evidence limit.

## Inspect the evidence

- [Validation summary](process-event-summary.json): all 28 checks, two native results, cohort counts, explicit limitations and source-artifact SHA-256 hashes.
- [Public event records](process-events-public.jsonl): 109 selected events across 56 capture-local process aliases; other process records are represented only by aggregate counts.
- [Native output verification](native-output-verification.json): saved-text and reloaded Sheet checks, source commit and hashes of the private run summaries. This runtime check does not independently inspect formula source.
- [Historical test output](tests.log) and [test provenance](test-provenance.json): 120 passing tests; temporary directory prefixes are replaced with `<TEMP>` in the public log.
- [Retained failed-attempt summary](failed-attempt-summary.json): the first attempt remains failed, with only the 14 before-task canaries and no successful native pair.
- [Capture, decode and reproduction protocol](../PROCESS_EVENTS.md): privilege boundary, validation gates, stop behavior and artifact handling.

The retry used clean source commit [`09e4b83824b8b0bec4348be0dbae2bcdef1f62dc`](https://github.com/ajayasai/office-twin-ntu-st-2026/commit/09e4b83824b8b0bec4348be0dbae2bcdef1f62dc). The application runtime used by this historical pair matched the frozen version used by the earlier benchmark. The later [resource-sampling fix](../resource-sampling-fix/README.md) changes only `office_twin/evidence.py` among runtime modules; its regression tests and noninteractive live sampling do not constitute a new native workflow trial. The later analyzer revision adds an explicitly scoped application-cohort view of the same unchanged capture; its source hash is recorded in the summary. It does not create a new native trial.

The original ETL SHA-256 is `45c0cf6a0305d8e5298722fab50cacdc7e6c212a6a494e6aee907553e6a04c22`. Raw ETL, original tracerpt XML, canonical Windows API XML, final counters, ground truth and native logs are retained privately. Hashes establish consistency with those artifacts, not third-party certification. The Windows API decode preserves native UTC timestamps; the original tracerpt output is unchanged.

The first attempt entered lid-triggered Modern Standby and exceeded its target duration while suspended. It captured 303 process events and verified 14 pre-task canaries, but did not complete the native protocol. Both attempts remain represented; the successful retry is not presented as an overall 100% attempt success rate.

The [fresh-environment check](../reproduction/README.md) separately verifies installation, the frozen 85-test suite and simulation plans on this machine. Retained human input-event logs, matched human/agent capture definitions and a second-machine native run remain unavailable. The participant-confirmed unassisted human measurements are preserved in the [human baseline](../human-baseline/README.md).
