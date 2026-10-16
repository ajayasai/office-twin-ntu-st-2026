# Windows process lifecycle event evidence

**Latest status: rundown validation passed with 32/32 focus observations bound to three existing application identities and 16/16 observed application-start parents resolved.** All 28 known canary lifecycles and both 11-step native tasks passed; final ETW loss counters were zero. See the [current identity and parent evidence](process-rundown/README.md). The original parents of the three warm main applications remain unavailable. The [earlier start/stop-only result](process-events/README.md) and failed attempts remain separate historical records.

The existing [ten-run benchmark](benchmark/README.md) used a separate process that sampled Toolhelp/psutil counters. Those historical results remain unchanged. This protocol adds a new, separately identified fixed/contextual pair under Windows process lifecycle tracing; it does not retroactively turn the earlier samples into event records or merge the new pair into the old timing comparison.

## Instruments and privilege boundary

| Tool | Role | Privilege |
|---|---|---|
| `tools/capture_process_events.ps1` | Starts a temporary process-only ETW session, writes a readiness marker, stops and flushes collection, and converts the private ETL | Elevated Administrator token |
| `tools/decode_process_events.ps1` | Decodes the unchanged ETL with `Get-WinEvent.ToXml`, retaining native UTC timestamps and decode provenance | Normal user or the collector |
| `tools/run_event_validation.py` | Launches known child processes before and after one native fixed/contextual pair, retaining launch/wait ground truth | Normal, unelevated user; refuses elevated execution |
| `tools/analyze_process_events.py` | Checks final capture state, raw-artifact integrity, lifecycle identities, canaries and native task coverage; exports an allowlisted public view | Normal user |

Only the collector is elevated. The browser, task controller, benchmark harness and canary workload stay in the ordinary desktop session. The collector uses the in-box `logman`, `tracerpt` and `ControlTraceW` facilities. It does not install Sysmon, change security or audit policies, enable a persistent Event Log channel, or create a scheduled data collector. Windows restricts control of ordinary ETW sessions to administrative/service identities or the Performance Log Users group; this script requires an elevated administrator token explicitly. [Microsoft StartTrace documentation](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea).

The provider is `Microsoft-Windows-Kernel-Process`, GUID `{22FB2CD6-0E7B-422B-A0C7-2FAD1FD0E716}`, process keyword `0x10`, informational level 4. Installed provider metadata is saved with the capture. Process lifecycle records are collected system-wide in the raw file; public selection happens afterward. Other providers, thread/image tracing and stack sampling are not enabled.

## Reproduce a new capture

Use the repository root as the working directory in both shells. Configure the dedicated Sheet in ignored `local-settings.json` as described in [GOOGLE_SHEETS.md](GOOGLE_SHEETS.md), keep that Sheet open, and leave the desktop unlocked and awake with the lid open. Each attempt needs fresh capture and native-output directory names; retain failed attempts. Do not edit the collector, decoder, worker, runtime or analyzer during an attempt.

In an **Administrator PowerShell**, run:

```powershell
$captureDirectory = Join-Path (Get-Location).Path 'runs\process-event-validation-01'
& .\tools\capture_process_events.ps1 -OutputDirectory $captureDirectory -MaxSeconds 900 -RequestRundown
```

The capture directory must not already exist and must be covered by the repository's `runs/` ignore rule. `capture-ready.json` is written only after the uniquely named session and expected private output path are confirmed. The marker records the session, provider, collector PID plus creation time, start/ready times, source hash and initial counters. Wait for the collector's recording message.

Within two minutes of readiness, run the following in a **normal PowerShell**, also from the repository root:

```powershell
.\.venv\Scripts\python.exe tools\run_event_validation.py --capture-dir runs\process-event-validation-01 --native-output runs\process-event-native-01 --seed 307 --require-rundown
```

The worker checks the collector's process identity and marker freshness. It launches 14 known processes before the native pair and 14 afterward: in each phase, 12 direct `cmd.exe /d /c exit` children plus a base-Python intermediate parent and its Python child. Known exit statuses include 0 and 7. These are intended to exercise short-lived processes and nested ancestry; actual lifetimes must come from ETW, and the protocol does not assume sub-100-millisecond coverage. Ground truth records actual child identities, launch/wait boundaries and exit results in `canary-ground-truth.json`.

The native pair uses the existing desktop benchmark harness at normal timing scale. The worker monitors collector lifetime and stops its owned Python workers if collection ends or the capture deadline approaches. It does not terminate shared Chrome or Notepad cohorts. At completion or failure, it requests collector shutdown by creating `stop.request`. The collector checks a 900-second target while Windows schedules it. System suspend can delay that check, so actual elapsed time, deadline overrun and maximum collector loop gap are reported. A duration-limit stop or scheduling gap above five seconds makes the capture incomplete.

Wait for final `capture-status.json`, then analyze in the normal shell:

```powershell
.\.venv\Scripts\python.exe tools\analyze_process_events.py --capture-dir runs\process-event-validation-01 --manifest runs\process-event-native-01\manifest.json --output-dir runs\process-event-validation-01\public-export
```

The native manifest is required for this submission protocol, even though the analyzer also accepts canary-only input for development. Inspect the result and exit status. A failed capture, canary or native trial remains a failed attempt; changing its status text or omitting the failed record is not a repair. Resolve the cause, use fresh paths and collect another attempt.

If the normal worker cannot start, request shutdown explicitly from the normal shell:

```powershell
New-Item -ItemType File -Path runs\process-event-validation-01\stop.request
```

This preserves a final capture record but supplies no successful workload evidence.

## Lifecycle identity and validation gates

The analyzer matches provider event IDs and reads named payload fields rather than assuming one binary layout. Event 1 is ProcessStart, event 2 is ProcessStop and event 15 is ProcessRundown in the installed provider metadata. Rundown enumerates an already-running process; it is never counted as a newly observed start.

The optional `-RequestRundown` collector mode requests provider state before readiness and immediately before stopping. It uses `EnableTraceEx2` with `EVENT_CONTROL_CODE_CAPTURE_STATE`, a bounded callback timeout and a session handle obtained from the verified owned session. API success is recorded separately from observed events. The matching worker option `--require-rundown` collects two independent Toolhelp/GetProcessTimes snapshots around the native pair. These preserve exact 100-nanosecond creation identities and recheck process handles; they collect no command lines, window titles or executable paths. The verifier requires actual before/after rundown records and matching snapshots for every preexisting focused process. A process created during the trace instead requires its actual start plus a compatible later snapshot or observed exit.

This protocol can identify applications that predate collection and resolve parent identities that are present in the trace. It cannot recover an original parent that exited before collection without retained historical evidence. Parent identity closure is reported separately from focused-process identity coverage. Unavailable parent sequence numbers, conflicting identities and reused parent PIDs do not become verified ancestry. Microsoft's [provider state request documentation](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-enabletraceex2) describes the request mechanism; the actual decoded events establish what this host emitted.

Identity uses PID together with process creation time. Sequence numbers, where present, provide additional consistency checks. A repeated PID alone is insufficient to join records. Parent relationships must resolve to a compatible parent identity at the child's start; ambiguous, contradictory or absent parent evidence is not invented. The public export uses capture-local aliases and distinguishes rundown, start and stop records.

A submission result must satisfy all of these checks:

1. The collector confirms an orderly stop of its own session, the requested stop marker, successful conversion and final counters. `captured_pending_verification` is a collector status, not a verified task result.
2. **Final** `EventsLost`, `LogBuffersLost` and `RealTimeBuffersLost` are available and zero. The script saves the running pre-stop query separately from the return of `ControlTraceW` STOP; a successful running query cannot replace final statistics. A fallback stop with unavailable final counters remains incomplete. [ControlTraceW](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-controltracew) controls the named session, and [EVENT_TRACE_PROPERTIES](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-event_trace_properties) defines the loss counters.
3. Raw ETL/XML sizes and SHA-256 hashes match the finalized capture record. Readiness, session identity and ground truth agree. The validation worker's lifecycle is present in the trace.
4. All **28 known canary lifecycles** are verified, including both phases, expected parent relationships and exit codes. Their observed boundaries bracket the native work.
5. Both native fixed/contextual trials complete output verification, retain their manifests and logs, and lie inside the capture window. Each controller lifecycle must resolve consistently against the event evidence. The analyzer separately reports how many native focus identities have matching lifecycle records; already-running application processes can remain unresolved when no rundown is emitted. A successful controller/canary check is not a claim of complete application ancestry. Process starts alone cannot establish that spreadsheet formulas or saved output are correct.
6. The analyzer reports `validation_passed: true` with no validation errors. Review the public export before linking it from the submission.

The native trace conversion uses [`tracerpt`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tracerpt) to preserve its XML and local summary; it does not use a permissive best-effort decode mode. A second decode uses `Get-WinEvent -Path ... -Oldest` and each record's `ToXml()` output to preserve the Windows API's UTC timestamps. Microsoft documents `-Oldest` as required for ETL input. [Get-WinEvent documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.diagnostics/get-winevent?view=powershell-5.1).

The canonical `process-events-winapi.xml` contains only the exact process-provider GUID. `winapi-decode-status.json` binds its hash and event count to the unchanged ETL hash, records the decoder source hash, and is required before the analyzer uses that view. A failed or inconsistent decode does not become verified evidence. No timestamp is manually shifted to fit a canary window.

## Verified rundown retry

The [rundown supplement](process-rundown/README.md) records 1,300 provider events over 354.9077122 seconds. All 32 focus observations resolve through exact bracketing snapshots and actual rundown. The 16 application starts inside the native windows have compatible parent lifetimes: two Explorer → Chrome, ten Chrome → Chrome and four Explorer → Notepad. Thirteen of those identities have observed exits; three Chrome processes are confirmed alive in final rundown. All 28 canaries and both native tasks pass, with 26 canaries below 100 ms and zero reported final logger loss. The current software suite passed 139 tests.

The first rundown attempt was interrupted by a foreground-focus change during the contextual task and remains a failed full-protocol attempt. The successful retry uses the same frozen tooling source `95bb3ef`, fresh paths, seed 311 and unchanged runtime. These runs are not added to the historical performance comparison. The three preexisting main applications' original parents remain unresolved; current identity coverage does not reconstruct that history.

## Historical start/stop-only retry

The [published retry evidence](process-events/README.md) records a 393.9823415-second capture with 344 process-provider records: 172 starts, 172 stops and no rundown records. Final `EventsLost`, `LogBuffersLost` and `RealTimeBuffersLost` were all zero. The maximum collector loop gap was 0.2349567 seconds, the collector received the requested stop marker, and no deadline overrun was reported.

All 28 known canary lifecycles passed the identity, parent-chain, time-boundary and exit-code checks. Both native trial controllers had verified lifecycles within the trace, bracketed by verified canaries, and both tasks completed 11/11 steps and output verification. The analyzer reported `validation_passed: true` with no validation errors. The 33 focus records refer to already-running application processes without a matching lifecycle record in this trace (0/33 focus bindings). Application-cohort events are reported separately in the public evidence; they do not make those focus bindings complete. No rundown events were observed, so this capture does not establish the original ancestry of every process already running when tracing began.

The 120-test software suite passed separately. Unit tests support the collector/decoder/validator implementation; the actual ETW files, native outputs and protocol checks provide the new observational evidence. This retry remains separate from the earlier ten-run sampled timing benchmark.

## Retained first attempt

The first attempt on 16 October 2026 produced 303 process-provider records: 168 starts and 135 stops, with no rundown records. All three final ETW loss counters were zero. The 14 before-native canaries resolved to their expected lifecycle, parent and exit data after canonical decoding; the 14 after-native canaries and successful native pair were not obtained. This is a failed full-protocol attempt, not a 28/28 validation or a completed benchmark.

Windows System events record entry into Modern Standby because of the lid at 10:14:24 UTC and exit on keyboard input at 10:30:21 UTC. The trace lasted approximately 1,037 seconds despite its 900-second target, and the native workload failed. The original capture status, failed workload and raw files remain intact. The revised collector reports scheduling gaps and actual overrun explicitly; no software loop can run while the operating system has suspended it.

This attempt also exposed a local `tracerpt` timestamp serialization defect: XML header timestamps had an offset of `+07:59`, while the Windows Event Log API decoded the same ETL timestamps directly as UTC. The original XML remains untouched. The separately hashed Windows API decode fixes the evidence-reading path, not the failed task result. `tracerpt -gmt` is documented for WPP payload timestamps and is not assumed to fix this manifest-provider header issue.

## Evidence handling and scope of a successful result

Keep the original ETL, both decoded XML views, decode provenance, capture commands/logs, ready/final status, child ground truth and native run artifacts in ignored `runs/`. Raw ETW may contain full executable paths, process identifiers, absolute timestamps and security metadata about unrelated applications. Do not attach the raw capture to Devpost or add it to the source archive.

The analyzer's `process-event-summary.json` and `process-events-public.jsonl` select task/canary processes and evidenced ancestors, publish fixed application roles and capture-local aliases, and retain relative event times and integrity hashes. Public hashes identify the privately retained source artifacts; they do not constitute independent third-party attestation. Check the allowlisted export for paths, identifiers and unrelated content before copying a verified result into public documentation.

A successful attempt supports a bounded statement: the recorded native pair and the 28 known lifecycles passed the listed validation checks, with zero **reported** ETW session loss. It does not prove that every possible system event was captured, that provider internals never omitted an event, or that other computers will behave identically. Process telemetry also does not prove delivered keyboard/mouse events, human behavior or task-exclusive resource costs. The participant-confirmed human baseline remains a separate human observation, and its missing raw event logs are not reconstructed from this automated trace.
