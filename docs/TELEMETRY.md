# Separate process observation and paired timing evaluation

The added observer runs in a separate Python process from the desktop controller. It uses Windows Toolhelp for process inventory and psutil for process creation times and resource counters. It does not consume the controller's action records, inspect browser content, or intercept input. This supplies a second measurement path for process presence, compatible parent identities and resource use.

It is **sampled polling, not Sysmon, ETW or a complete process-start trace**. A separate process is not an independent auditor. First seen does not mean process started; a process missing from one sample is not proof that it exited.

## What is measured

- Process identity combines PID and creation time to avoid joining different processes after PID reuse.
- Each selected identity has first/last observed times, sample count, parent PID and a parent identity when its creation time is compatible with the child.
- CPU deltas begin at the first observed counter value. Pre-existing lifetime CPU is not charged to a trial. CPU consumed before first observation or after last observation is missing.
- Scope peak RSS is the maximum simultaneous sum of sampled RSS. It is not the sum of each process's separate peak, and shared pages can be counted more than once.
- The requested polling interval is 0.1 seconds. Actual median/maximum gaps and overruns are reported; no exact 10 Hz guarantee is implied.
- The exact controller, observed controller descendants, Chrome cohort, Notepad cohort and observer overhead are reported separately.

Chrome and Notepad are selected by executable name. They can include existing tabs, documents and unrelated background work. These cohorts provide useful context beyond controller-only figures, but **are not task-exclusive resource costs**. No total-workload efficiency claim follows from adding them together.

The observer records no command lines, usernames, URLs, window titles, keystrokes, clipboard data or screenshots. Raw observations stay in the private `runs/` directory. Public evidence uses an explicit numeric/enum allowlist and omits process IDs, personal paths and spreadsheet identifiers.

## Reproduce the collection

Create the dedicated Sheet described in [GOOGLE_SHEETS.md](GOOGLE_SHEETS.md), then save its URL in ignored `local-settings.json`:

```json
{"sheet_url": "PASTE_DEDICATED_SHEET_EDIT_URL"}
```

On an idle, unlocked Windows desktop:

```powershell
python tools/run_benchmark.py --output runs/paired-evaluation
python tools/analyze_benchmark.py --manifest runs/paired-evaluation/manifest.json --output runs/paired-evaluation/export
```

The harness plans fixed and contextual timing trials for seeds 211, 223, 227, 229 and 233, reversing their order in alternate pairs. Each uses the same default scenario and timing scale 1. It starts a separate observer before each worker and records the source commit, runtime hash and measurement-code hash. The worker supplies its actual PID and creation time, which may differ from a Windows launcher PID. The harness checks observer completion, bound identity and coverage, and stops on source changes, failed tasks, failed collection or unsafe cleanup. Every attempted run and capture failure remains visible. The observer is read-only and requires no security-configuration changes.

Keep the dedicated Sheet open before starting. Opening a new Sheet window in only one member of a pair changes the action sequence, so the analyzer excludes that comparison. After collection, the harness closes only validated run-owned supplier/Explorer windows and the saved report tab. It does not close the Sheet or unrelated browser tabs. The remaining signed-in Chrome profile is warm and shared; resource attribution remains limited even with this controlled cleanup.

The reported task interval starts at the first workflow step and ends when the last step completes. Controller wall time also includes setup, countdown, verification and runtime cleanup; the harness closes owned windows after the measurement ends. Requested delays and measured waits are reported by action kind; these are controller measurements, not hardware input timestamps.

## Evidence-driven launch correction

All three initial pilot trials completed their native tasks. Across those observations, the separate collector recorded six Notepad process identities with compatible Python parent identities. Opening the report directly through the controller's `os.startfile` call was therefore visible in the telemetry. These historical observations are retained; they are not rewritten to describe the revised implementation. The first initial fixed/contextual pair also had an extra Sheet-opening branch and is excluded from performance comparison.

The revised workflow opens both the supplier browser and the Notepad report through real, visible Explorer shortcut double-clicks. The report shortcut targets only the exact existing run-owned text file, and its unique launch-folder window is reused for the saved-file reopen. Missing or ambiguous controls stop input; there is no direct-file launch fallback. This changes the actual opening action, not process metadata. Windows file association, application reuse and sampling coverage still determine which parent relationships can be observed. Unresolved parents remain explicitly unresolved.

The revised paired series is a separate source version. Its ten native attempts all completed, yielding five comparable pairs; see the [revised benchmark](benchmark/README.md) and [validation](VALIDATION.md) for measurements and limits. The current software suite has 139 passing tests, including launch targeting and evidence-handling checks; tests are not native telemetry observations.

## Human-reference status

**The automated observer series contains zero human-reference runs.** A subsequent [participant-confirmed, unassisted human baseline](human-baseline/README.md) reports a 720-second task, input behavior, application resources and measured process ancestry. Its aggregates were supplied by the participant; raw input-event and resource logs were not supplied. It is separate from both this automated capture and the earlier guided practice.

The timing policy remains an uncalibrated engineering model. Fixed-versus-contextual measurements can show whether variation exists and what time/resource cost it has; they cannot establish resemblance to humans, human entropy, indistinguishability or an official judging score. The retained automated exports keep their original `human_reference_runs: 0` scope.

The existing [manual collector and protocol](MANUAL_BASELINE.md) remain available for a future consented study. Automated runs, collector tests and synthetic traces are never substituted for manual observations.

## Existing event-trace availability

The collection process runs with an unelevated, medium-integrity token; the account's Administrators membership is present only as deny-only in that token. No Sysmon service/channel was available, the Security log was inaccessible, and the WMI process-start collector reported Access denied. These historical collection limitations are preserved. No logging policy, endpoint protection or audit records were modified, and no process-parent metadata was spoofed or rewritten.

The separate [process lifecycle event protocol](PROCESS_EVENTS.md) provides an elevated, temporary ETW collector and a separate unelevated validation worker. The [earlier start/stop-only retry](process-events/README.md) passed 28/28 known canary lifecycles and 2/2 native tasks with 11/11 steps each. Its 393.9823415-second trace contained 344 process-provider records (172 starts and 172 stops), with zero in all three final ETW loss counters. This is bounded validation of the specified lifecycles and tasks; no rundown events were observed, and complete application-window ancestry is not claimed.

The first event-trace attempt remains a recorded failure after the computer entered Modern Standby. These historical attempts remain separate from the ten-run sampled benchmark above. The elevated ETW results do not change the historical WMI access-denied result or turn those earlier sampled observations into process events.

## Rundown identity supplement

The [new rundown capture](process-rundown/README.md) verifies **32/32 focus observations** across **three current application identities**, with **28/28 known lifecycles**, **11/11 steps in both runs** and final loss counters **0 / 0 / 0**. Requested state records and two exact OS snapshots cross-check applications already running before capture. Snapshots retain PID, reported parent PID, executable basename and exact creation FILETIME; a fresh process handle rechecks each identity. They collect no commands, window titles, usernames or paths.

The applications stayed open as requested. Their original parents had already exited, so current child identity verification does not close those historical parent chains. All 16 application starts inside the native trial windows resolve to compatible parent lifetimes: 10 Chrome → Chrome, two Explorer → Chrome and four Explorer → Notepad. Shared application activity remains nonexclusive, and zero reported loss is not universal completeness.

The first warm rundown attempt remains failed: fixed 11/11, contextual stopped at 7/11 when the foreground guard detected a focus change during Sheet saving, 14 before-task canaries and no after-task canaries. The fresh retry is reported separately; neither is pooled into the ten-run resource benchmark. The earlier start/stop-only capture retains its historical 0/33 focus-binding result and 120-test provenance.

Implementation references: [Microsoft Toolhelp process inventory](https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/ns-tlhelp32-processentry32w) and [psutil process counters](https://psutil.readthedocs.io/en/latest/). Parent snapshots establish observed compatibility, not causation.
