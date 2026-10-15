# Record a genuine manual reference

`tools/record_manual.py` measures a consenting participant's attempt at the same synthetic office task. It never controls the desktop or records typing, pointer activity, screen content, window titles, URLs, command lines, or security logs. It records explicit start/stop, optional predefined task markers, and resource counters for application PIDs you select.

The tool cannot establish that a person did the task, that the outputs are correct, or that the timing resembles a population of people. It labels the outcome **participant-reported** and **unverified**. Do not use an agent-run session as human evidence.

## Prepare a comparable task

Follow [the evaluation protocol](EVALUATION.md). Use the same scenario, blank target sheet/report, application versions, starting state, and recording setup for manual and agent conditions. Explain the collection scope and obtain consent. Use a pseudonym such as `P01`, never the participant's name.

Choose and document the timing boundary before capture. Give the participant access to the brief and supplier pages, without displaying the generated answer. They should inspect the quotations, enter the sheet inputs/formulas, decide on a supplier, and save a text recommendation. If applications are already running, use a warm-start agent run too. Match whether opening the task page, target sheet, and report file is inside the measured interval. The manual tool does not create/reset fixtures or start applications.

The agent's total recorder wall time includes preparation, its five-second countdown, and cleanup. Do **not** directly compare that total with a manual interval beginning at the first task action. Either include equivalent boundaries on both sides or derive the corresponding agent task interval from its event timestamps and label that derivation. Console-switch overhead remains part of the manual duration.

Use Task Manager to identify the intended application PIDs. This optional command lists only supported application names and PIDs:

```powershell
.\.venv\Scripts\python.exe tools\record_manual.py --list-processes
```

A Chrome process can own several tabs and background tasks. Use an otherwise idle demonstration browser. Resource observations still describe selected processes, not exclusively the task. `--include-descendants` also samples children of the selected PID, useful for Chrome's multiple processes; it can include unrelated browser tabs. Do not select processes solely because their name appears in this list.

## Start and stop explicitly

Replace the example PIDs with the actual task application PIDs:

```powershell
.\.venv\Scripts\python.exe tools\record_manual.py --participant P01 --pid 1234 --pid 5678 --include-descendants --task office-twin-sheets-default
```

To collect duration without application resource measurements, omit `--pid`. The output reports only collector overhead in that case. An optional `--scenario scenarios\alternate.json` records a SHA-256 digest of that input file; it does not copy file contents or paths into the summary.

1. Type `start` once the participant is ready, then perform the task manually.
2. Optional phase markers are `mark brief-reviewed`, `mark quotes-reviewed`, `mark spreadsheet-saved`, and `mark report-saved`. `mark interruption` marks an interruption. These are voluntary reports, not detected actions. Omit them when minimizing console-switch overhead matters more than phase detail.
3. Return to the console and type `stop` when finished, `incomplete` for an unfinished attempt, or `abort` to abandon it. Ctrl+C or end-of-input after starting saves an aborted attempt. Typing `stop` does **not** declare output correctness.

Every attempt gets a new directory under `runs/manual/`. Preserve failed and interrupted attempts. The tool never modifies the participant's application settings or files.

## Read the evidence accurately

- `manual-summary.json`: participant/task labels, duration, markers, participant-reported outcome, scenario digest if supplied, and scoped resource summaries.
- `manual-events.jsonl`: timestamped boundaries, optional markers, and periodic resource snapshots. It contains no task keystrokes or unrelated input logging.
- CPU values are user plus kernel **CPU-seconds** between first and last observed samples. They are not percentages. PID and process creation time bind identity so a reused PID is not silently followed.
- RSS is sampled resident memory; the default interval is 0.5 seconds. Peaks and short-lived processes can be missed.
- Collector CPU/RSS is separate from application observations. Do not compare manual collector overhead with agent-controller overhead as if they were equivalent workloads.
- Duration includes switching to the console to start, mark, and stop. Document that overhead. This tool does not collect native input-event timing or independent process-event traces.

Verify saved sheet values, **formula source**, and the report's decision separately. Record those check results next to the manual run; leave `task_success_verified` false in the raw collector output, whose scope is intentionally narrower. Do not feed these manual files into the automated run-report pipeline as if they were agent runs. Enter the real measurements into the evaluation table with sample sizes and interruption notes.

Before sharing evidence, review it with participants. A practice attempt and a few manual runs support an exploratory comparison, not a claim that the agent is indistinguishable from people.
