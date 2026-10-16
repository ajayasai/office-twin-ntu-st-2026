# Office Twin — judging guide

Office Twin performs a connected procurement task through Chrome, Google Sheets and Notepad: compare three suppliers, calculate price and deadline eligibility, choose the cheapest eligible quote, and save and reopen a checked recommendation. This guide maps the evidence to the [official judging criteria](https://ntu-x-st-engineering-hackathon.devpost.com/rules).

## Review in one minute

1. **See the task:** three supplier quotes become six Sheet formulas, a deadline-aware choice and a saved/reopened report. Atlas wins at SGD 600; the alternate fixture changes the winner to Crest at SGD 525.
2. **Inspect actual process evidence:** the [rundown record](process-rundown/README.md) verifies 32/32 focus observations and 16 newly observed application-start parent relationships. Exited original parents remain unresolved.
3. **Compare timing and cost:** five paired trials show contextual wait variation at a median added cost of 11.26 task seconds and 1.219 controller CPU-seconds. These are historical policy comparisons, not human-similarity results.
4. **Check the supplied human reference and current software:** the [720-second unassisted baseline](human-baseline/README.md) remains unchanged; the [current sampler evidence](resource-sampling-fix/README.md) records 144 tests and 19/19 noninteractive checks. Native benchmarks retain their original code versions.

## Evidence by criterion

| Criterion | Weight | Result to inspect | Evidence |
| --- | ---: | --- | --- |
| Process Telemetry Authenticity | 30% | Rundown and exact OS snapshots verify 32/32 focus bindings across three current application identities. 28/28 known lifecycles and the stated controller checks pass; final loss counters: 0 / 0 / 0. All 16 application starts have resolved parent lifetimes: 10 Chrome → Chrome, two Explorer → Chrome and four Explorer → Notepad. Warm main processes’ exited original parents remain unresolved. | [Current rundown evidence](process-rundown/README.md), [earlier event evidence](process-events/README.md), [event protocol](PROCESS_EVENTS.md) |
| Human Entropy & Timing | 30% | Five paired fixed/contextual runs measure key, review and window-focus wait variation; see the table below. Single-key p90 ranges are 109.50–110.08 ms fixed and 161.01–177.73 ms contextual. A participant-confirmed unassisted human baseline reports 720 s, 42 WPM, 14 corrected errors and measured process ancestry. | [Paired timing results](benchmark/README.md), [human baseline and definitions](human-baseline/README.md) |
| Complexity of Action | 20% | The ten-run controlled series completed all 11 steps in every run. The earlier ETW retry pair completed 11/11 each; the rundown supplement adds 11/11 steps in both runs. Interrupted attempts remain documented. Tasks include supplier review, six formulas, a cost/deadline decision, correction and save/reopen checks. A historical changed-price scenario changes the winner. | [Validation history](VALIDATION.md), [rundown evidence](process-rundown/README.md), [saved formula/value check](benchmark/saved-sheet-verification.json), [scenario source](../scenarios/alternate.json) |
| Resource Efficiency | 20% | Historical ten-run median full-window controller CPU: 19.14 CPU-s fixed / 20.61 contextual. Sampled controller peak RSS: 72.72–73.09 MiB across ten runs. Runtime makes no cloud-model calls. Observer overhead and application cohorts are reported separately. Current sampler correctness is supported by 144 tests and 19/19 noninteractive checks; this is not a new task-performance measurement. | [Full numeric resource report](benchmark/BENCHMARK.md), [machine-readable export](benchmark/benchmark.json), [sampler validation](resource-sampling-fix/README.md), [architecture](ARCHITECTURE.md) |

The historical observer polls OS state; its per-run parent counts are not globally unique process counts. The rundown supplement adds verified current focus identities to known canary/controller coverage. It does not recover exited historical parents or establish every possible system event. Current identity coverage and historical ancestry closure are reported as separate checks. Human aggregates and controller waits use different measurement definitions; they are not a validated timing-similarity comparison. The evidence supports the listed results, not a computed official score.

## Measured controller waits

These are ranges of per-run 90th-percentile observed waits across five runs per policy, derived from each run's `actual_wait` measurements in the [retained benchmark](benchmark/benchmark.json). Counts are per run.

| Action | Observed waits per run | Fixed p90 range | Contextual p90 range |
| --- | ---: | ---: | ---: |
| Single key | 586 | 109.50–110.08 ms | 161.01–177.73 ms |
| Review | 6 | 1.312–1.320 s | 1.809–2.814 s |
| Window focus (`switch`) | 16 | 0.463–0.469 s | 0.628–0.973 s |

Controller waits include scheduler effects and are not OS input-delivery timestamps. Waits within a run are not independent task trials. These measurements show variation between the implemented policies; they do not establish calibrated human similarity or a matched comparison with the participant's timing aggregates.

Across those same five retained pairs, contextual-minus-fixed task duration had a median of **+11.26 seconds** (range +5.55–17.10), while full-window controller CPU had a median paired increase of **+1.219 CPU-seconds** (range +0.219–1.859). These paired deltas are computed separately from the two policy medians. They quantify the historical timing policy's observed cost on this host, not the new sampler's efficiency or a human-versus-agent difference.

## What a correct result looks like

The default task purchases five sensor kits with a seven-day delivery deadline. Atlas is selected at **SGD 600**; Beacon is cheaper but misses the deadline. A separate alternate-price/order fixture selects **Crest at SGD 525**. The final saved Sheet check contains 18 literal cells, six formula sources and six calculated results. Native trials also verify the displayed grid and saved recommendation.

Google Sheets runs inside Chrome. Native Excel/Word is optional and has not been validated; it is not needed to reproduce the demonstrated workflow. The supplier pages are generated from validated synthetic scenario data. This is a controlled workflow, not arbitrary-web extraction.

## Reproduce or review

1. Follow the [installation commands](../README.md#run), then run `.\.venv\Scripts\python.exe -m office_twin --doctor` and `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` inside the configured environment. The current reviewed suite passes **144 tests**. A [fresh-environment check](reproduction/README.md) separately reproduced the earlier frozen source's 85 tests and two simulation plans on this same machine.
2. Run `.\.venv\Scripts\python.exe -m office_twin --mode simulate --workflow sheets --scale 0` to inspect the plan without driving the desktop. Simulation is explicitly labelled and does not count as a native result.
3. Prepare a dedicated Google Sheet using [GOOGLE_SHEETS.md](GOOGLE_SHEETS.md). Use the native contextual command in the README on an unlocked Windows desktop. Escape cancels input. Use synthetic task data and a dedicated output directory.
4. Inspect saved results and logs. For the controlled fixed/contextual series, follow [the telemetry reproduction commands](TELEMETRY.md#reproduce-the-collection). The separate [ETW protocol](PROCESS_EVENTS.md) keeps its collector elevated and workload unelevated; retain every attempted run and its capture result.

The recorded automated environment was Windows 11 Home Single Language build 26200, Intel Core Ultra 7 155U with 14 logical processors, 31.55 GiB RAM, Python 3.14.2, Chrome 155.0.8059.40, Notepad 11.2607.14.0 and a 1920 × 1200 display. Applications were warm and shared. This is distinct from the human mouse-distance summary's assumed 1920 × 1080 coordinates.

## Resource boundaries and cost

Controller CPU covers its full execution window, while task duration covers first step start through final step completion. The controller requests 250 ms RSS sampling. Its figures exclude Chrome, Notepad and the separate observer. The observer requests 100 ms polling, measured per-run median gaps of 100.39–100.44 ms, and a worst gap of 510.89 ms. Its own measured cost was 38.36–65.88 CPU-s and 26.45–29.28 MiB peak sampled RSS per capture. This diagnostic overhead is disclosed rather than included invisibly in controller cost.

Chrome and Notepad cohorts may include unrelated application activity. Summed RSS can double-count shared pages. Do not add overlapping scopes or treat these application cohorts as exclusive whole-task costs. CPU-seconds are processor time, not wall-clock seconds or a utilization percentage.

## Version and evidence map

- The ten-run automated benchmark used frozen runtime `051ec6871425ddaba9faeffed297a2168620e58c`. Those measurements retain that source version and do not measure the later resource-sampling fix.
- The current [resource-sampling fix](resource-sampling-fix/README.md) changes only `office_twin/evidence.py` among runtime modules relative to the published native evidence. Regression tests and noninteractive live sampling validate the change; the suite now passes 144 tests. The native workflow was not rerun.
- The earlier start/stop-only ETW retry used source `09e4b83824b8b0bec4348be0dbae2bcdef1f62dc` and retains its 120-test provenance and 0/33 focus-binding result.
- The rundown supplement uses clean source `95bb3efc830a2d811b69cc68c9483ae9b0353fec`, seed 311 and the 139-test suite. Its warm application identities are cross-checked without restarting applications. All event-validation pairs remain separate from the ten-run performance series, and interrupted attempts remain available.
- The [fresh-install result](reproduction/README.md) uses frozen source `5d3e0100f652f424fed5653ac78b2ffdae0256e5` and its historical 85-test suite. It demonstrates installation in a new virtual environment on the same Windows host, not portability to a second device.
- The continuous desktop footage is from **15 October 2026**, before the later launch and observer changes. Later results shown in presentation material are identified separately; they were not recorded in that footage.
- The [unassisted 720-second baseline](human-baseline/README.md) contains participant-confirmed measured aggregates, including process ancestry. Raw input, resource and process-event traces were not supplied with those aggregates.
- The [earlier 734.526-second guided practice](manual-practice/README.md) is preserved as a separate historical record with its guidance and waiting-inclusive boundaries.
- The [initial automated series](benchmark-initial/README.md) retains three completed tasks and an excluded comparison. Its observed Python-to-Notepad parentage motivated the actual Explorer opening change.
- The [submission record](../SUBMISSION.md) identifies published artifacts. [AI assistance and dependency provenance](ARCHITECTURE.md) remain disclosed.

Remaining evidence limits are matched human/agent input-event observations, ancestors that exited before tracing, and native reproduction on a second machine. Verified current identities do not close those separate gaps or support a computed official score.
