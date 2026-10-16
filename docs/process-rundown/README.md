# Verified existing application identities and new parent relationships

**The 16 October rundown retry passed: 32/32 native focus observations resolve to three existing application identities, and all 16 application starts inside the two task windows have resolved parent identities.** The two native tasks each completed 11/11 steps. All 28 known canary lifecycles, their expected parent chains and exit codes verified; all three final ETW loss counters were zero.

Existing Chrome, Notepad and Explorer processes remained open. This closes the earlier gap in identifying the focused processes within the new capture. Their own original parents had exited before tracing and remain unresolved. Current identity coverage and historical ancestry are separate results.

## Application evidence

| Focused application | Recorded focus observations | Exact identity in both OS snapshots | Actual rundown before and after focus | Original parent identity |
| --- | ---: | --- | --- | --- |
| Chrome, including Google Sheets | 18/18 verified | Matches | Present | Unavailable |
| Notepad | 8/8 verified | Matches | Present | Unavailable |
| Explorer | 6/6 verified | Matches | Present | Unavailable |

The snapshots use Toolhelp inventory and `GetProcessTimes` creation values retained as exact 100-nanosecond FILETIME integers. Fresh process handles recheck every retained identity. The verifier requires matching application roles and reported parent IDs, compatible lifetimes, and actual Event 15 records on both sides of the focus interval. Rundown is an observation of an existing process; it is never counted as an observed start. The provider explicitly returned unavailable sequence values for the three original parents; no current PID was substituted for a missing historical identity.

New application starts within the native trial windows have these resolved relationships:

| Observed parent → child | Fixed trial | Contextual trial | Total |
| --- | ---: | ---: | ---: |
| Explorer → Chrome | 1 | 1 | 2 |
| Chrome → Chrome | 5 | 5 | 10 |
| Explorer → Notepad | 2 | 2 | 4 |
| **Resolved application-start parents** | **8/8** | **8/8** | **16/16** |

These links use compatible process identities and available sequence numbers, not a parent-PID match alone. The actual workflow opens its supplier-browser and report shortcuts through Explorer. The application-name cohort can also contain unrelated activity; parent resolution does not prove exclusive task causation. Its 12 Chrome and four Notepad starts are not 16 newly created main application windows: existing application instances can receive work from short-lived launch processes. The 14 stop records inside the trial windows likewise must not be described as 16 complete lifecycles within those windows.

Of those 16 newly started application identities, 13 have an observed stop within the full capture; the other three Chrome processes are present in final rundown. Across the full system-wide capture, the equal totals of 185 starts and 185 stops comprise 175 paired identities plus ten start-only and ten stop-only identities. Counts alone are never used to infer lifecycle pairs.

## Capture and task checks

| Check | Observed result |
| --- | --- |
| Trace duration | 354.9077122 seconds |
| Provider records | 1,300: 185 starts, 185 stops, 930 rundown records |
| Idle placeholders | Two PID-zero rundown records counted above, explicitly excluded from process identities |
| Final EventsLost / LogBuffersLost / RealTimeBuffersLost | 0 / 0 / 0 |
| Maximum collector loop gap; deadline overrun | 0.2341363 seconds; zero |
| Known canary lifecycles | 28/28; 14 before and 14 after the native pair |
| Canary lifetimes from actual creation/exit values | 26 under 100 ms; min 21.3464 ms, median 30.0757 ms, max 213.0899 ms |
| Validation worker and task controllers | All required lifecycle checks passed |
| Native fixed/contextual tasks | 2/2 completed, each 11/11 steps; saved text and reloaded Sheet values passed |
| Exact focus bindings | 32/32, verified against three preexisting identities |
| Public selection | 59 process identities, 118 events; unrelated records excluded |
| Historical capture-source suite | 139 tests passed in 10.389 seconds |

The collector stopped its verified owned session on the requested stop marker, flushed it, and retained final counters. The unchanged ETL was decoded through `Get-WinEvent.ToXml`; hashes bind the decoded view, capture status, canary ground truth and native manifest. The final analyzer reports `validation_passed: true` and no validation errors. Zero reported session loss does not establish universal provider completeness.

## Reproduction and evidence files

Use the [process-event protocol](../PROCESS_EVENTS.md), including collector `-RequestRundown` and worker `--require-rundown`. Only the collector needs elevation. The task controller, worker and sampled observer run unelevated.

This pair used clean source `95bb3efc830a2d811b69cc68c9483ae9b0353fec`, seed 311, fixed then contextual timing, scale 1, on the same warm shared Windows host with no screen recording. The application runtime used by this historical pair matched the frozen ten-run benchmark implementation; that revision added evidence collection and verification. The later [resource-sampling fix](../resource-sampling-fix/README.md) changes only `office_twin/evidence.py` among runtime modules and was checked through regression tests and noninteractive live sampling, without rerunning the native workflow. These trials are not pooled into the historical timing/resource comparison.

- [Machine-readable verification](process-event-summary.json): capture counts, every canary check, focus identities, parent-resolution results and source/artifact hashes.
- [Allowlisted event records](process-events-public.jsonl): relative timestamps, capture-local aliases and application roles.
- [Native saved-output checks](native-output-verification.json): source provenance and private summary hashes. These runtime checks verify displayed values and saved text, not an independent formula-source inspection.
- [Test log](tests.log) and [test provenance](test-provenance.json): exact outcomes, source hashes and disclosed local-path redaction.
- [Interrupted rundown attempt](failed-rundown-attempt-summary.json): retained failed result, described below.

Raw ETL, XML, exact process identifiers, snapshots, task logs and original reports remain private under ignored local run directories. Hashes support artifact consistency, not third-party attestation. Public exports omit personal paths, command lines, Sheet identifiers and raw PIDs.

## Retained attempts and remaining limits

The first full rundown attempt completed its fixed task but stopped the contextual task after 7/11 steps when foreground focus changed. The input guard halted the task. Only the 14 before-native canaries ran, so the complete protocol failed. Its exported 16/16 focus bindings apply only to the completed fixed task; they are not presented as a successful pair. The retry above used fresh output paths and the same code, seed and task configuration.

The [earlier start/stop-only capture](../process-events/README.md) remains a separate result with 28/28 canaries, two completed tasks, its historical 0/33 focus bindings and 120-test provenance. The still earlier Modern Standby failure is retained there. No earlier trace or measurement has been relabelled as rundown evidence.

The three preexisting main applications' original parents remain unavailable. The participant requested keeping the applications open, so no cold-launch ancestry claim is made. Human baseline aggregates remain participant-confirmed actual measurements; raw matched human input logs and native reproduction on a second machine are still unavailable. This new process evidence does not close those separate limits or establish an official judging score.
