## What Office Twin does

Office Twin completes a procurement decision across **Chrome → Google Sheets → Notepad**. It compares three suppliers, calculates six formulas, rejects a cheaper quote that misses the deadline, and saves and reopens a checked recommendation. The default task selects **Atlas at SGD 600**; a changed-price/order scenario correctly selects **Crest at SGD 525**.

The project combines a working desktop task with measured timing, actual Windows process evidence and explicitly scoped resource costs. The [judging guide](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/JUDGING_GUIDE.md) links each result to its source and reproduction instructions.

## Evidence against the four criteria

| Official criterion | Weight | Result and evidence | Measurement boundary |
| --- | ---: | --- | --- |
| Process Telemetry Authenticity | 30% | **32/32 focus observations** bound to current application identities; **16/16 new application-start parent relationships** resolved; **28/28 canary lifecycles** verified; final ETW loss counters **0 / 0 / 0**. [Rundown evidence](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/process-rundown/README.md) | The three warm main applications' original parents had already exited and remain unresolved. Zero reported loss is not universal completeness. |
| Human Entropy & Timing | 30% | New optional **human-informed** key delays fit the existing unassisted **170 ms median / 350 ms p90**, with implied mean **199.249 ms** against **200 ms** reported. Automatic verification uses **five seeds × 100,000 samples per policy**. Five historical native fixed/contextual pairs remain separately reported. [Model and verification](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/human-timing/README.md) | Generated controller delays are checked against aggregate design targets. Delivered input timing, key holds and human similarity remain unverified. |
| Complexity of Action | 20% | **Ten-run benchmark: 10/10 native tasks, 11/11 steps each**, with six formulas, delivery eligibility, a recommendation and saved-output checks. Two separate successful ETW pairs also completed 11/11 each. [Validation history](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/VALIDATION.md) | Controlled synthetic supplier pages and one connected workflow; Google Sheets in Chrome, with optional Excel/Word untested. Failed attempts remain documented. |
| Resource Efficiency | 20% | Historical controller CPU medians **19.14 / 20.61 CPU-s** (fixed/contextual); sampled peak RSS **72.72–73.09 MiB**. No runtime cloud-model calls. Sampler checkpoint: **144 tests and 19/19 integration checks**, retained separately from current timing tests. [Resource report](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/benchmark/BENCHMARK.md) | Application and observer costs are separate. Later fixes do not establish a new full-task performance result or efficiency improvement. |

These are observed or participant-reported results, not a calculated judging score. The implementation, logs, retained failures and source versions remain inspectable in the repository.

## Inspiration and implementation

An office worker reads, compares, pauses, corrects and saves. We wanted those actions to form a useful task whose outputs and system activity could both be checked.

Python, pywinauto, Windows UI Automation and pywin32 drive visible applications. The eleven-step workflow reads three local quotation pages, enters values and six formulas in a dedicated Google Sheet, reloads the Sheet to check displayed results, then writes, corrects, saves and reopens a Notepad recommendation. Validated scenario JSON supplies the pages, planned actions and expected outputs; this is not autonomous extraction from arbitrary websites.

The runner checks the target window, Sheet URL, worksheet and range before writing, supports cancellation and retains partial evidence on failure. A separate final read-only Sheet inspection verified **18 literal cells, six formula sources and six calculated results**. Each completed trial in the ten-run benchmark verified displayed values and the saved report.

All timing policies share the same workflow. Legacy contextual timing uses bounded variation and correlated pacing; fixed and contextual defaults and seeded behavior are preserved. The new optional `human-informed` policy fits requested pre-key delays to the existing unassisted median and p90 using a lognormal model. The reported mean is a held-out aggregate consistency check, not independent human validation. Other actions remain engineering defaults and the deliberate corrected typo remains scripted.

The new profile has separately seeded key draws and engineering bounds of 5–2,000 ms, not claimed human extrema. Its automatic verifier checks each seed's mean, median and p90 against a predefined 3% relative-error threshold and compares target error with the legacy model. Tests replace native input with test doubles; the 11-step plan check blocks native backend imports. The [complete fit and source-bound verification](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/human-timing/README.md) distinguish generated delays from delivered input. No new human run, app restart or native workload was required. The supplied 100 ms hold mean, pause schedule and total 720-second duration are not reconstructed or claimed as implemented.

OpenAI Codex assisted implementation, tests, documentation and validation. Google connectors provisioned the fixture and performed separate saved-content checks; runtime execution makes no cloud-model calls. The [architecture and dependency provenance](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/ARCHITECTURE.md) document these boundaries.

## What the measurements changed

The first separate-observer series found compatible Python parents for six Notepad identities. We changed the actual desktop action: the browser and report now open through visible Explorer shortcut double-clicks. We did not alter process metadata. The initial comparison also exposed different Sheet-opening actions, so the analyzer rejected it instead of treating it as a matched pair.

The revised ten-run benchmark used frozen runtime `051ec68`, five seed pairs (211, 223, 227, 229, 233), normal timing scale 1 and alternating policy order. All ten tasks completed. Native task duration had medians of **153.13 s fixed** and **167.08 s contextual**. Across the five matched pairs, contextual timing added a median **11.26 task seconds** (range 5.55–17.10) and **1.219 controller CPU-seconds** (range 0.219–1.859). These quantify the cost of the timing policy on one warm, shared host; they are not a human-versus-agent speedup or a statistical significance claim.

The table shows the range of per-run **90th-percentile observed controller waits** across five runs per policy. Counts are per run.

| Action | Waits per run | Fixed p90 range | Contextual p90 range |
| --- | ---: | ---: | ---: |
| Single key | 586 | 109.50–110.08 ms | 161.01–177.73 ms |
| Review | 6 | 1.312–1.320 s | 1.809–2.814 s |
| Window focus | 16 | 0.463–0.469 s | 0.628–0.973 s |

Controller waits include scheduler effects and are not OS input-delivery timestamps. Within-run waits are not independent task trials. The [complete numeric benchmark](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/benchmark/benchmark.json) retains each run, comparison and measurement scope.

The later rundown capture independently checks process state against exact Windows creation timestamps before and after the work. It verifies **2 Explorer → Chrome, 10 Chrome → Chrome and 4 Explorer → Notepad** new-start parent relationships. Both native tasks completed 11/11 steps; 26 of the 28 known canaries lived under 100 ms. Its 354.908-second trace contains **1,300 provider records: 185 starts, 185 stops and 930 rundown records**. Rundown records existing state, not a new launch, and equal start/stop totals are not assumed to be paired lifecycles. Applications stayed open; shared cohorts do not establish exclusive task causation.

The successful rundown source was `95bb3ef`, whose application runtime matched the historical benchmark. An earlier attempt stopped at 7/11 during its second task when the foreground-focus guard detected a change. That attempt and the earlier start/stop-only ETW series remain in the [validation history](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/VALIDATION.md); they are not pooled into the five-pair performance benchmark.

The earlier [resource-sampling fix](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/resource-sampling-fix/README.md) rejects stale process identities around CPU/RSS reads and checks parents separately. Its **144-test checkpoint** and **19/19-check noninteractive probe** verified 37 existing Chrome/Notepad identities, excluded 0.65625 CPU-s of prior worker activity, and measured 0.78125 CPU-s matching fresh OS readings. The initial probe's launcher-selection mistake is retained. That revision changed only `office_twin/evidence.py`; the later timing revision changes additional modules. The sampler and observer source hashes still match their preserved integration evidence. Historical performance results retain their original versions; neither revision reran the native benchmark.

## Resource scope and reproducibility

The benchmark used Windows 11 build 26200, Core Ultra 7 155U (14 logical processors), 31.55 GiB RAM, Python 3.14.2, Chrome 155.0.8059.40, Notepad 11.2607.14.0 and a 1920 × 1200 display. Applications were warm and shared. The human mouse-distance figure below separately assumes 1920 × 1080 coordinates.

Controller CPU covers the full execution window; task duration covers first step through final completion. Controller RSS was sampled at a requested 250 ms interval. The separate observer requested 100 ms, recorded **17,018 snapshots**, median gaps of 100.39–100.44 ms and a maximum gap of 510.89 ms with one overrun. Its own overhead was **38.36–65.88 CPU-s and 26.45–29.28 MiB** peak sampled RSS per capture. Chrome/Notepad cohorts include unrelated activity; summed RSS can double-count shared pages. The observer is our instrumentation, not an independent auditor. Public exports omit personal paths, command lines and raw process identifiers.

The [setup and reproduction guide](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/README.md#run) provides pinned dependencies, doctor checks, simulation and native commands. A separate [fresh-environment check](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/reproduction/README.md) passed the historical source's 85 tests and two 11-step simulation plans on this same machine. Simulation is explicitly labelled; a second-device native result is not claimed.

**Earlier guided practice, separate from the unassisted baseline below:** the retained 734.526-second attempt includes chat guidance, exact formulas, a report example and waiting. Saved outputs were checked afterward, but input timing and application resources were not recorded. It is not used for a human-versus-agent speed ratio. [Practice record](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/manual-practice/README.md).


## Human baseline: unassisted, human-performed task

The participant confirms that the following task was completed entirely by a human, without guidance. This is the participant-supplied measurement summary for a **720-second (12-minute) human baseline**. It is reported separately from the earlier 734.526-second practice record above. The aggregate measurements were supplied by the participant; raw input-event and resource logs were not included with this update. The participant's clarification is reflected in the waiting/idle phase label below. The [baseline documentation and machine-readable aggregates](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/human-baseline/README.md) preserve every measurement and its scope.

### Task duration and phases

| Measure | Human baseline |
| --- | --- |
| **Total task duration** | **720 seconds — 12 minutes** |
| Reading brief and reviewing quotes | 90 seconds |
| Entering spreadsheet headers | 45 seconds |
| Entering supplier data | 135 seconds |
| Calculations and deadline checks | 90 seconds |
| Writing recommendation | 180 seconds |
| Saving, reopening and checking outputs | 90 seconds |
| Waiting / idle | 90 seconds |
| Typing measurement window, across task phases | 180 seconds |

### Typing, corrections and interaction

| Measure | Human baseline |
| --- | --- |
| Final retained text | 630 characters |
| Net typing speed [1] | 42 WPM |
| Total key-down events | 740 |
| Printable-character keypresses | 672 |
| Backspace/Delete keypresses | 42 |
| Navigation/modifier keypresses | 26 |
| Backspace/Delete share | 5.68% |
| Mean inter-key interval [2] | 200 milliseconds |
| Median inter-key interval [2] | 170 milliseconds |
| 90th-percentile inter-key interval [2] | 350 milliseconds |
| Mean key-hold duration | 100 milliseconds |
| Input-error episodes | 14 |
| Error episodes corrected | 14 |
| Errors remaining in final output | 0 |
| Pauses of at least 2 seconds [3] | 18 |
| Combined pause duration [3] | 150 seconds |
| Mouse click cycles | 112 |
| Double-click gestures | 4, comprising 8 of those 112 clicks |
| Mouse-wheel events | 28 |
| Mouse travel at an assumed 1920 × 1080 resolution | 20,000 screen-coordinate pixels |
| Foreground application switches | 8 |
| Chrome tab switches | 24 |

### Application resources and process ancestry

| Measure | Human baseline |
| --- | --- |
| Chrome process-group CPU time [4] | 36 CPU-seconds |
| Chrome process-group mean / peak summed RSS [5] | 600 / 720 MiB |
| Notepad CPU time [4] | 1.8 CPU-seconds |
| Notepad mean / peak RSS [5] | 55 / 70 MiB |
| Measured process ancestry (participant-reported) | Explorer → Chrome; Chrome → Chrome child processes; Explorer → Notepad |

The participant confirms that the process ancestry is also an actual measurement. The reported relationships are included as human-baseline results; underlying process-event records were not supplied with this update. They are reported separately from the agent's retained sampled parent evidence.

**Definitions and scope.** [1] Net WPM = 630 retained characters ÷ 5 characters per word ÷ 3 minutes = 42. The phase durations sum to 720 seconds; the typing window spans those phases and is not additional time. Key categories sum to 740, and 42 ÷ 740 × 100 = 5.68%. [2] Inter-key and hold statistics are participant-reported aggregates. The eligible key set, timestamp source and pause-exclusion rule were not supplied, so they are not treated as directly comparable to the agent's controller waits. [3] Pause duration overlaps task activity and is not added to the 720-second total; its overlap with the 180-second typing window was not specified. [4] CPU-seconds represent processor time, not elapsed time. Capture boundaries and Chrome process inclusion rules were not supplied. [5] MiB means 2²⁰ bytes. Summed RSS can count shared pages more than once; sampling cadence and the group-peak aggregation method were not supplied.

**What this adds to the evaluation.** The human baseline provides a concrete reference for task phases, typing variation, correction behavior, application switching, process ancestry and application resources. The reported output has 14 corrected error episodes and zero remaining errors. It complements the verified agent workflow and five paired automated comparisons, while keeping participant-reported human measurements distinct from retained automated logs. A single aggregate baseline does not establish human indistinguishability, a population distribution or an official score. We do not infer an agent-versus-human speedup because capture boundaries, assistance history of the older practice and input-event definitions differ.

Automated task duration covers first step start through final step completion; full controller wall time also includes preparation, countdown, verification and cleanup. Controller waits are not OS input timestamps.

The [revised narrated video](https://youtu.be/oTTT0ECN25U) preserves the continuous **162.13-second 15 October functional recording at 1×** within a **180.13-second edit**. Narration and cards separately report earlier 16 October results: ten native completions, five matched pairs, the historical 85-test suite and the supplied unassisted baseline. The labelled footage predates the launch changes, ETW captures, sampler revision and new human-informed timing model. Microsoft Zira Desktop provides synthetic narration; the video is not evidence of those later results.

## What we learned and what remains

Correct saved work, natural-looking timing and authentic process relationships require different checks. Measurement led to an actual Explorer-opening change and caught a comparison that should not be counted. Retaining unsuccessful attempts makes the demonstrated success easier to assess.

The strongest remaining evidence needs are matched human/agent input-event definitions, ancestry captured before original parents exit, and native reproduction on a second machine. The existing participant-confirmed unassisted measurements remain unchanged. Current identity verification and the sampler fix improve specific checks; they do not close those separate gaps or establish human indistinguishability.

Start with the [judging guide](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/JUDGING_GUIDE.md), [complete source](https://github.com/ajayasai/office-twin-ntu-st-2026) and [submission artifact record](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/SUBMISSION.md). Detailed evidence and failed-attempt histories remain linked there.
