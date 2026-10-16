# Office Twin — judging guide

Office Twin performs a connected procurement task through Chrome, Google Sheets and Notepad: compare three suppliers, calculate price and deadline eligibility, choose the cheapest eligible quote, and save and reopen a checked recommendation. This guide maps the evidence to the [official judging criteria](https://ntu-x-st-engineering-hackathon.devpost.com/rules).

## Evidence by criterion

| Criterion | Weight | Result to inspect | Evidence |
| --- | ---: | --- | --- |
| Process Telemetry Authenticity | 30% | Actual Explorer shortcut openings, Chrome multiprocess activity and Notepad use. The separate observer collected 17,018 snapshots. Within capture windows it observed compatible Explorer parents for 6 Chrome and 8 Notepad identities, and Chrome parents for 33 Chrome child identities. | [Parent observations](benchmark/process-parent-evidence.md), [measurement method](TELEMETRY.md) |
| Human Entropy & Timing | 30% | Five paired fixed/contextual runs. Per-run 90th-percentile single-key controller waits were 109.50–110.08 ms fixed and 161.01–177.73 ms contextual. A participant-confirmed unassisted human baseline reports 720 s, 42 WPM, 14 corrected errors and measured process ancestry. | [Paired timing results](benchmark/README.md), [human baseline and definitions](human-baseline/README.md) |
| Complexity of Action | 20% | Ten of ten native tasks completed all 11 steps: three supplier reviews, six formulas, cost/deadline decisions, a typing correction, cloud-save/reload verification, and text-file save/reopen verification. A separately validated changed-price scenario correctly changes the winner. | [Validation history](VALIDATION.md), [saved formula/value check](benchmark/saved-sheet-verification.json), [scenario source](../scenarios/alternate.json) |
| Resource Efficiency | 20% | Median full-window controller CPU: 19.14 CPU-s fixed / 20.61 contextual. Sampled controller peak RSS: 72.72–73.09 MiB across ten runs. Runtime makes no cloud-model calls. Observer overhead and application cohorts are reported separately. | [Full numeric resource report](benchmark/BENCHMARK.md), [machine-readable export](benchmark/benchmark.json), [architecture](ARCHITECTURE.md) |

The process counts sum identities separately within each run; they are not globally unique process counts. The observer polls OS state rather than collecting a complete process-start event stream. Human aggregates and controller waits use different measurement definitions; they are not a validated timing-similarity comparison. The evidence supports the listed results, not a computed official score.

## What a correct result looks like

The default task purchases five sensor kits with a seven-day delivery deadline. Atlas is selected at **SGD 600**; Beacon is cheaper but misses the deadline. A separate alternate-price/order fixture selects **Crest at SGD 525**. The final saved Sheet check contains 18 literal cells, six formula sources and six calculated results. Native trials also verify the displayed grid and saved recommendation.

Google Sheets runs inside Chrome. Native Excel/Word is optional and has not been validated; it is not needed to reproduce the demonstrated workflow. The supplier pages are generated from validated synthetic scenario data. This is a controlled workflow, not arbitrary-web extraction.

## Reproduce or review

1. Follow the [installation commands](../README.md#run), then run `python -m office_twin --doctor` and `python -m unittest discover -s tests -v` inside the configured environment. The reviewed suite passes **85 tests**.
2. Run `python -m office_twin --mode simulate --workflow sheets` to inspect the plan without driving the desktop. Simulation is explicitly labelled and does not count as a native result.
3. Prepare a dedicated Google Sheet using [GOOGLE_SHEETS.md](GOOGLE_SHEETS.md). Use the native contextual command in the README on an unlocked Windows desktop. Escape cancels input. Use synthetic task data and a dedicated output directory.
4. Inspect saved results and logs. For the controlled fixed/contextual series, follow [the telemetry reproduction commands](TELEMETRY.md#reproduce-the-collection); retain every attempted run and its capture result.

The recorded automated environment was Windows 11 Home Single Language build 26200, Intel Core Ultra 7 155U with 14 logical processors, 31.55 GiB RAM, Python 3.14.2, Chrome 155.0.8059.40, Notepad 11.2607.14.0 and a 1920 × 1200 display. Applications were warm and shared. This is distinct from the human mouse-distance summary's assumed 1920 × 1080 coordinates.

## Resource boundaries and cost

Controller CPU covers its full execution window, while task duration covers first step start through final step completion. The controller requests 250 ms RSS sampling. Its figures exclude Chrome, Notepad and the separate observer. The observer requests 100 ms polling, measured per-run median gaps of 100.39–100.44 ms, and a worst gap of 510.89 ms. Its own measured cost was 38.36–65.88 CPU-s and 26.45–29.28 MiB peak sampled RSS per capture. This diagnostic overhead is disclosed rather than included invisibly in controller cost.

Chrome and Notepad cohorts may include unrelated application activity. Summed RSS can double-count shared pages. Do not add overlapping scopes or treat these application cohorts as exclusive whole-task costs. CPU-seconds are processor time, not wall-clock seconds or a utilization percentage.

## Version and evidence map

- The ten-run automated benchmark used frozen runtime `051ec6871425ddaba9faeffed297a2168620e58c`. Later documentation and presentation updates do not constitute a new runtime trial.
- The continuous desktop footage is from **15 October 2026**, before the later launch and observer changes. Later results shown in presentation material are identified separately; they were not recorded in that footage.
- The [unassisted 720-second baseline](human-baseline/README.md) contains participant-confirmed measured aggregates, including process ancestry. Raw input, resource and process-event traces were not supplied with those aggregates.
- The [earlier 734.526-second guided practice](manual-practice/README.md) is preserved as a separate historical record with its guidance and waiting-inclusive boundaries.
- The [initial automated series](benchmark-initial/README.md) retains three completed tasks and an excluded comparison. Its observed Python-to-Notepad parentage motivated the actual Explorer opening change.
- The [submission record](../SUBMISSION.md) identifies published artifacts. [AI assistance and dependency provenance](ARCHITECTURE.md) remain disclosed.

Remaining evidence limits are a matched human/agent input-event study, complete event telemetry, and native reproduction on a second machine. Those require new observations; editing the narrative cannot establish them.
