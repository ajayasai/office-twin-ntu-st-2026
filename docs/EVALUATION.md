# Evaluation protocol

The purpose is to measure correct task completion, timing, genuine application activity, and resource cost. The protocol is proposed by this team; it is not an official organizer benchmark. See [observed validation](VALIDATION.md) for the completed functional checks; the paired human comparison below is still outstanding.

## A paired task

Use the same synthetic supplier quotes, business question, application versions, display setup, and initial files for all conditions. For the primary workflow, the participant or agent reads local pages in Chrome, calculates the comparison in Google Sheets, and saves a Notepad recommendation that agrees with the calculations. If evaluating the optional Excel/Word path, keep its results separate from the browser-based workflow.

Define the expected sheet values and recommendation criteria before collecting runs. Save an untouched copy of the fixture. A task succeeds only if the cloud sheet and saved text report open correctly, contain the expected data/calculations, and support the stated decision. Runtime clipboard readback checks displayed values; verify formula source separately through the formula bar or a read-only connector query.

Compare these conditions:

| Condition | What it establishes |
| --- | --- |
| Manual | A consenting human performs the task without automation. Provides a small exploratory reference, not the full range of human behavior. |
| Fixed timing | The desktop agent performs the task using the fixed timing mode. A comparison condition for the timing model. |
| Contextual timing | The desktop agent performs the task using the contextual timing mode. The proposed submission behavior. |

Simulation is a separate development check. Do not include it in native completion rates or human-versus-agent comparisons.

## Collect the manual reference honestly

1. Ask the teammates who will participate for consent to record task activity and elapsed time. Explain exactly which events, recordings, or process data will be retained.
2. Use a dedicated test environment containing synthetic data. Close personal accounts and unrelated applications that might expose private information.
3. Give each participant the same task instructions and a short practice attempt. Do not direct them to create a desired timing pattern or intentionally make mistakes.
4. Record an anonymous participant ID, run ID, environment, start/end times, task boundaries, success, and any interruption. The [CSV template](baseline-template.csv) is a manual recording aid, not a telemetry collector.
5. Retain only the task-relevant records. Remove personal paths, account names, window titles, and unrelated browsing details from the shared copy; preserve an access-controlled original only where needed and agreed.

A practical minimum target is three consenting teammates completing two manual runs each and at least five runs per automated condition. This is a small pilot, not a statistically strong population study. If fewer runs are feasible, report the actual sample size and restrict conclusions accordingly.

## Make conditions comparable

- Document the starting state, including whether applications are already running. Match it across compared runs; separate cold-start from warm-start results.
- Reset fixtures and outputs between runs. Do not overwrite a failed attempt with a successful retry.
- Alternate fixed and contextual runs where practical to reduce order effects. Use the same seed across a paired automated comparison, then repeat with other seeds.
- Keep telemetry collection, screen recording, and resource sampling settings the same. Recording overhead is part of the test setup and must be disclosed.
- Record app-load waits separately from deliberate pacing where the evidence allows it. A long delay caused by an error is not evidence of realistic human behavior.

## Independent telemetry

Agent action logs describe what the controller reports doing. They do not independently prove application execution, parent-child relationships, file operations, or user interaction.

If Sysmon is already installed and its use is authorized, collect the relevant time window from its existing event channel and record the configuration/version used. Windows Event Logs may provide additional evidence depending on the existing audit configuration. Do not change security settings, add exclusions, disable protections, alter process relationships, or modify logs for the demonstration.

Observe and report the actual application execution relationships. Compare them with manual runs from the same machine and starting state. Ordinary application reuse, browser multiprocess behavior, and different opening paths can produce legitimate differences. Missing events may reflect capture configuration; they must not be interpreted automatically as absent activity.

Preserve raw exports separately from redacted presentation copies. Explain how displayed figures were derived. Screen recordings and output files support task completion, but neither replaces process telemetry.

## Metrics and reporting

| Metric | Reporting rule |
| --- | --- |
| Task completion | Successful complete runs / all attempted runs; list partial runs and failure reasons separately. |
| Output correctness | Check the saved sheet's input values, formula source and results, and whether the text report's recommendation follows them. |
| Timing | Report total duration and available action/phase intervals using median and spread; show distributions rather than only one average. |
| Timing similarity | Compare like-for-like phases against the small manual reference; describe observed overlap and differences without claiming a detector cannot distinguish them. |
| Process activity | Show actual independently recorded application events/relationships, collection coverage, and unexplained differences. |
| Resource cost | Give sampling interval, CPU definition and core normalization, RAM measure, and which processes are included. Report agent-only figures separately from whole-workload figures. |

Do not compute a purported official total score from these measurements: the public rubric gives category weights but no numerical scoring transformation. Do not call greater randomness “more human” without comparison evidence. A coherent task can have repeated actions and correlated pauses.

## Results template

Fill this table only after actual runs. Use “not collected” where necessary.

| Condition | Attempts | Complete/correct | Duration summary | CPU/RAM scope and summary | Independent telemetry |
| --- | ---: | --- | --- | --- | --- |
| Manual | Not collected | Not collected | Not collected | Not collected | Not collected |
| Fixed timing | Not collected | Not collected | Not collected | Not collected | Not collected |
| Contextual timing | Not collected | Not collected | Not collected | Not collected | Not collected |

Include environment details, anonymization steps, failure notes, and evidence paths beside the completed table.
