# Unassisted human baseline

The participant confirms these are **actual measurements of a task completed entirely by a human, without guidance**, including the measured process ancestry. This is one supplied aggregate baseline for a **720-second (12-minute)** task. It is separate from the earlier [734.526-second guided practice](../manual-practice/README.md).

[Machine-readable aggregate record](aggregate.json). Documentation was added on **16 October 2026 (SGT)**; the measurement date, run ID and actual hardware were not supplied. The participant's clarification corrects “Guidance / waiting” to “Waiting / idle”, retaining the reported 90 seconds. No other numeric measurements were changed.

## Task phases

| Measure | Human baseline |
| --- | ---: |
| **Total task duration** | **720 seconds** |
| Reading brief and reviewing quotes | 90 seconds |
| Entering spreadsheet headers | 45 seconds |
| Entering supplier data | 135 seconds |
| Calculations and deadline checks | 90 seconds |
| Writing recommendation | 180 seconds |
| Saving, reopening and checking outputs | 90 seconds |
| Waiting / idle | 90 seconds |
| Typing measurement window, across task phases | 180 seconds |

The seven phases sum to 720 seconds. The typing window spans those phases and is not additional elapsed time. The pause duration below also overlaps the task; its overlap with the typing window was not specified.

## Typing and interaction

| Measure | Human baseline |
| --- | ---: |
| Final retained text | 630 characters |
| Net typing speed | 42 WPM |
| Total key-down events | 740 |
| Printable-character keypresses | 672 |
| Backspace/Delete keypresses | 42 |
| Navigation/modifier keypresses | 26 |
| Backspace/Delete share | 5.68% |
| Mean inter-key interval | 200 milliseconds |
| Median inter-key interval | 170 milliseconds |
| 90th-percentile inter-key interval | 350 milliseconds |
| Mean key-hold duration | 100 milliseconds |
| Input-error episodes | 14 |
| Error episodes corrected | 14 |
| Errors remaining in final output | 0 |
| Pauses of at least 2 seconds | 18 |
| Combined pause duration | 150 seconds |
| Mouse click cycles | 112 |
| Double-click gestures | 4, comprising 8 of the 112 clicks |
| Mouse-wheel events | 28 |
| Mouse travel at an assumed 1920 × 1080 resolution | 20,000 screen-coordinate pixels |
| Foreground application switches | 8 |
| Chrome tab switches | 24 |

Net WPM uses the conventional five-character word: `(630 / 5) / (180 / 60) = 42`. Key categories reconcile: `672 + 42 + 26 = 740`; the deletion share is `42 / 740 × 100 = 5.68%` after rounding. Four double-click gestures contain eight clicks already included in 112. The equality `672 − 42 = 630` assumes each printable key adds one character and each deletion removes one; it does not reconstruct an input timeline.

## Application resources and ancestry

| Measure | Human baseline |
| --- | --- |
| Chrome process-group CPU time | 36 CPU-seconds |
| Chrome process-group mean / peak summed RSS | 600 / 720 MiB |
| Notepad CPU time | 1.8 CPU-seconds |
| Notepad mean / peak RSS | 55 / 70 MiB |
| Measured process ancestry, participant-reported | Explorer → Chrome; Chrome → Chrome child processes; Explorer → Notepad |

CPU-seconds mean processor time, not elapsed time or a utilization percentage. MiB means 1,048,576 bytes. Summed RSS may count shared pages more than once. Mouse travel is screen-coordinate distance at the stated assumed resolution, not physical distance or a confirmed display setup.

## Methods, provenance and interpretation

The source is the participant's measurement table and subsequent confirmations that the task was unassisted and the ancestry was measured. Raw input-event, resource and process-event logs were not supplied. The capture software, eligible key set, timestamp source, pause-exclusion rule, resource capture boundaries, process-selection rules, sampling cadence, mean weighting and group-peak method were not specified. The measurements are attributed to the participant; independent trace verification and saved-output validation are not claimed for this record.

These aggregates provide a human reference for phases, input variation, corrections, switching, resources and ancestry. They have not been used to calibrate the agent's timing defaults. The [automated benchmark](../benchmark/README.md) measures controller waits and scoped sampled process resources under its own documented boundaries; those are not assumed equivalent to the human measurements. No shared machine, participant identity with the guided practice, timing distribution, speedup or human-indistinguishability result is inferred.

See the [evaluation protocol](../EVALUATION.md) for future matched collection, [validation](../VALIDATION.md) for evidence scopes, and [submission record](../../SUBMISSION.md) for the confirmed uploaded package. Historical benchmark exports saying no human reference describe their pre-update automated series and remain unchanged.
