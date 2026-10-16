# Evaluation protocol

The purpose is to measure correct task completion, timing, genuine application activity, and resource cost. The protocol is proposed by this team; it is not an official organizer benchmark. See [observed validation](VALIDATION.md) for reported results. The paired benchmark compares two automated timing policies. One later [guided manual practice](manual-practice/README.md) has verified saved outputs and is reported separately; an unassisted manual comparison remains future work.

## A paired task

Use the same synthetic supplier quotes, business question, application versions, display setup, and initial files for all conditions. For the primary workflow, the participant or agent reads local pages in Chrome, calculates the comparison in Google Sheets, and saves a Notepad recommendation that agrees with the calculations. If evaluating the optional Excel/Word path, keep its results separate from the browser-based workflow.

Define the expected sheet values and recommendation criteria before collecting runs. Save an untouched copy of the fixture. A task succeeds only if the cloud sheet and saved text report open correctly, contain the expected data/calculations, and support the stated decision. Runtime clipboard readback checks displayed values; verify formula source separately through the formula bar or a read-only connector query.

Compare these conditions:

| Condition | What it establishes |
| --- | --- |
| Manual | A consenting human performs the task without automation. Provides a small exploratory reference, not the full range of human behavior. |
| Guided manual practice | A participant performs the task with instruction support. Report guidance, waiting time and output verification separately; do not treat it as an unassisted timing baseline. |
| Fixed timing | The desktop agent performs the task using the fixed timing mode. A comparison condition for the timing model. |
| Contextual timing | The desktop agent performs the task using the contextual timing mode. The proposed submission behavior. |

Simulation is a separate development check. Do not include it in native completion rates or human-versus-agent comparisons.

## Collect the manual reference honestly

1. Ask the teammates who will participate for consent to record task activity and elapsed time. Explain exactly which events, recordings, or process data will be retained.
2. Use a dedicated test environment containing synthetic data. Close personal accounts and unrelated applications that might expose private information.
3. Give each participant the same task instructions and a short practice attempt. Do not direct them to create a desired timing pattern or intentionally make mistakes.
4. Record an anonymous participant ID, run ID, environment, start/end times, task boundaries, success, and any interruption. The [CSV template](baseline-template.csv) is a manual recording aid, not a telemetry collector.
5. Retain only the task-relevant records. Remove personal paths, account names, window titles, and unrelated browsing details from the shared copy; preserve an access-controlled original only where needed and agreed.

A future exploratory study could target three consenting teammates completing two unassisted manual runs each and at least five runs per automated condition. These are planning targets, not observations or evidence that the sample is statistically adequate. Current manual evidence is **one participant, one guided completion, zero unassisted baseline runs**. Report each evidence class separately and restrict conclusions accordingly.

The guided completion took **734.526 seconds** from the participant's browser Start to Finish, including chat instructions, replies and waiting. Exact Sheet headers/formulas and a sample report were supplied; the participant had seen the task before. Separate reads verified the saved Sheet's six formulas/results and correct recommendation. Participation was declared rather than independently observed, and the saved report matches the supplied sample after whitespace normalization. No task input timings, application-resource samples or process events were collected. These boundaries and assistance differ from the automated benchmark, so no agent-versus-human speed ratio or timing-similarity claim is justified.

## Make conditions comparable

- Document the starting state, including whether applications are already running. Match it across compared runs; separate cold-start from warm-start results.
- Reset fixtures and outputs between runs. Do not overwrite a failed attempt with a successful retry.
- Alternate fixed and contextual runs where practical to reduce order effects. Use the same seed across a paired automated comparison, then repeat with other seeds.
- Keep telemetry collection, screen recording, and resource sampling settings the same. Recording overhead is part of the test setup and must be disclosed.
- Record app-load waits separately from deliberate pacing where the evidence allows it. A long delay caused by an error is not evidence of realistic human behavior.

The automated harness uses seeds 211, 223, 227, 229 and 233, pairing fixed and contextual policies and reversing their order in alternate pairs. It plans five runs per policy at scale 1 on the same default scenario. Source commit, runtime hash and measurement-code hash are recorded; changed code stops the series. Worker identity comes from the actual interpreter, not its possible Windows launcher. Every attempted run is retained even when launch, collection, task completion or cleanup fails.

The dedicated Sheet stays open between runs. After measurement, the harness closes only validated run-owned supplier and Explorer windows and the saved Notepad report tab, avoiding accumulated task windows. Chrome remains a warm, shared profile with potentially unrelated background work. The analyzer requires matched metadata, timing action-kind/unit sequences, complete verified native tasks and valid collection before publishing paired performance deltas.

The initial pilot illustrates why these checks matter: its first fixed/contextual pair differed because one run opened the Sheet window and the other reused it. That pair is excluded from performance comparison. Three successful initial pilot trials also exposed six Notepad identities with compatible Python parent snapshots. They motivated the real Explorer report-opening change; historical and revised runtime results remain separate.

## Independent telemetry

Agent action logs describe what the controller reports doing. They do not independently prove application execution, parent-child relationships, file operations, or user interaction.

If Sysmon is already installed and its use is authorized, collect the relevant time window from its existing event channel and record the configuration/version used. Windows Event Logs may provide additional evidence depending on the existing audit configuration. Do not change security settings, add exclusions, disable protections, alter process relationships, or modify logs for the demonstration.

Observe and report the actual application execution relationships. Compare them with manual runs from the same machine and starting state. Ordinary application reuse, browser multiprocess behavior, and different opening paths can produce legitimate differences. Missing events may reflect capture configuration; they must not be interpreted automatically as absent activity.

Preserve raw exports separately from redacted presentation copies. Explain how displayed figures were derived. Screen recordings and output files support task completion, but neither replaces process telemetry.

On this host, Sysmon was unavailable, the Security channel was inaccessible to the current account, and WMI process-start capture reported Access denied. The added separate observer therefore reads Windows Toolhelp process inventory and psutil counters, targeting 100 ms polling while recording actual gaps and access failures. It supplies a separate OS measurement path, not a complete event stream or an independent auditor. Parent identities are accepted only with compatible creation times; unresolved parents remain unresolved. See [the telemetry protocol](TELEMETRY.md).

Measure the exact controller, observed controller descendants, name-selected Chrome and Notepad cohorts, and observer overhead separately. Application cohorts include unrelated instances and background activity. Their simultaneous sampled RSS sums may count shared pages more than once, and CPU deltas omit work outside each identity's first-to-last observations. Do not describe these aggregates as exclusive whole-task costs.

## Metrics and reporting

| Metric | Reporting rule |
| --- | --- |
| Task completion | Successful complete runs / all attempted runs; list partial runs and failure reasons separately. |
| Output correctness | Check the saved sheet's input values, formula source and results, and whether the text report's recommendation follows them. |
| Timing | Report total duration and available action/phase intervals using median and spread; show distributions rather than only one average. |
| Timing similarity | Not measured: unassisted human baseline n=0 and no human task input-timing data. The one guided completion provides no matched timing distribution. A future consented study can compare like-for-like phases. |
| Process activity | Show actual application observations and compatible parent snapshots, collection coverage and unresolved identities. Distinguish sampled observations from event traces. |
| Resource cost | Give sampling interval, CPU definition and core normalization, RAM measure, and which processes are included. Report agent-only figures separately from whole-workload figures. |

Do not compute a purported official total score from these measurements: the public rubric gives category weights but no numerical scoring transformation. Do not call greater randomness “more human” without comparison evidence. A coherent task can have repeated actions and correlated pauses.

## Results reporting

Generate the numeric report from retained run manifests rather than filling planned counts into a results table. Report attempts, complete/correct tasks, comparable pairs, task-interval duration, full-window controller CPU/RSS, observer coverage/overhead and nonexclusive application cohorts. Keep failed attempts and excluded pairs visible, explain each exclusion, and identify the tested runtime version. The completed 16 October series is reported in the [revised benchmark](benchmark/README.md): ten complete native tasks and five comparable pairs.

Include environment details, anonymization steps, failure notes and evidence references with the results. [Validation](VALIDATION.md) records published outcomes; this document defines the protocol. The current 85 passing automated tests validate software behavior and evidence handling, not human timing or participant activity. Keep the [guided practice result](manual-practice/README.md) alongside the automated benchmark with its assistance, timing boundaries and separately verified saved outputs explicit.
