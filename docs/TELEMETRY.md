# Separate process observation and paired timing evaluation

The added observer runs in a separate Python process from the desktop controller. It reads the Windows process inventory and resource counters directly. It does not consume the controller's action records, inspect browser content, or intercept input. This supplies a second measurement path for process presence, compatible parent identities and resource use.

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

The harness pairs fixed and contextual timing for seeds 211, 223, 227, 229 and 233, reversing their order in alternate pairs. Each uses the same default scenario and timing scale 1. It starts a separate observer before each worker, records the source version, and stops the series on a failed trial. Every attempt and capture failure must remain visible. The observer is read-only and requires no security-configuration changes.

The reported task interval starts at the first workflow step and ends when the last step completes. Controller wall time also includes setup, countdown, verification and cleanup. Requested delays and measured waits are reported by action kind; these are controller measurements, not hardware input timestamps.

## Human-reference status

**Human participants: 0.** No participant was available for this evaluation. The timing policy remains an uncalibrated engineering model. Fixed-versus-contextual measurements can show whether variation exists and what time/resource cost it has; they cannot establish resemblance to humans, human entropy, indistinguishability or an official judging score.

The existing [manual collector and protocol](MANUAL_BASELINE.md) remain available for a future consented study. Automated runs, collector tests and synthetic traces are never substituted for manual observations.

## Existing event-trace availability

The current account is not an administrator. No Sysmon service/channel was available, the Security log was inaccessible, and the WMI process-start collector reported Access denied. These limitations are preserved. No logging policy, endpoint protection, process ancestry or audit records were modified.

Implementation references: [Microsoft Toolhelp process inventory](https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/ns-tlhelp32-processentry32w) and [psutil process counters](https://psutil.readthedocs.io/en/latest/). Parent snapshots establish observed compatibility, not causation.
