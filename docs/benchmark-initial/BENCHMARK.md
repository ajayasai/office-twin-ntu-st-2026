# Controlled timing benchmark — observed evidence

3 attempts; 3 complete, verified native tasks; 0 comparable fixed/contextual pairs under declared matching conditions.

**No human baseline was collected. This comparison does not establish human similarity or an official score.**

Run aliases correspond to manifest order (then explicit run arguments); duplicate paths are excluded. No source paths, Sheet IDs, process command lines, raw error text or event payloads are exported.

| Run | Policy / seed | Status | Steps | Task interval (s) | Full wall (s) | Controller CPU (s) | Sampled controller RSS (MiB) |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| R001 | fixed / 211 | desktop: completed | 11/11 | 154.623 | 162.498 | 28.438 | 81.36 |
| R002 | contextual / 211 | desktop: completed | 11/11 | 162.362 | 169.205 | 29.719 | 81.32 |
| R003 | contextual / 223 | desktop: completed | 11/11 | 162.056 | 169.121 | 29.328 | 81.22 |

## Paired comparison

Deltas below are contextual minus fixed. A shorter or lower-resource incomplete run is never treated as an improvement.

- **P001 (R001, R002)**: not performance-comparable. Timing action-kind/unit sequences differ.
- **P002 (R003)**: not performance-comparable. A pair requires exactly one fixed and one contextual attempt; missing or ambiguous members are retained.

## Requested and observed waits

Samples are grouped by action kind and unit count. These are controller waits; correlated events are not independent task trials. Interrupted waits remain in the data.

| Run | Kind / units | Requested n | Requested median / p90 (s) | Actual n | Actual median / p90 (s) | Interrupted |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| R001 | correction / 1 | 1 | 0.350 / 0.350 | 1 | 0.364 / 0.364 | 0 |
| R001 | key / 1 | 586 | 0.095 / 0.095 | 586 | 0.100 / 0.112 | 0 |
| R001 | read / 2 | 3 | 1.600 / 1.600 | 3 | 1.612 / 1.613 | 0 |
| R001 | read / 3 | 4 | 2.400 / 2.400 | 4 | 2.411 / 2.415 | 0 |
| R001 | review / 1 | 6 | 1.300 / 1.300 | 6 | 1.305 / 1.311 | 0 |
| R001 | switch / 1 | 15 | 0.450 / 0.450 | 15 | 0.455 / 0.462 | 0 |
| R001 | think / 1 | 6 | 1.100 / 1.100 | 6 | 1.105 / 1.118 | 0 |
| R002 | correction / 1 | 1 | 0.252 / 0.252 | 1 | 0.257 / 0.257 | 0 |
| R002 | key / 1 | 586 | 0.097 / 0.159 | 586 | 0.106 / 0.166 | 0 |
| R002 | read / 2 | 3 | 1.566 / 1.740 | 3 | 1.573 / 1.752 | 0 |
| R002 | read / 3 | 4 | 2.581 / 3.362 | 4 | 2.585 / 3.362 | 0 |
| R002 | review / 1 | 6 | 1.238 / 1.619 | 6 | 1.243 / 1.625 | 0 |
| R002 | switch / 1 | 14 | 0.514 / 0.695 | 14 | 0.540 / 0.699 | 0 |
| R002 | think / 1 | 6 | 1.530 / 2.518 | 6 | 1.538 / 2.529 | 0 |
| R003 | correction / 1 | 1 | 0.192 / 0.192 | 1 | 0.191 / 0.191 | 0 |
| R003 | key / 1 | 586 | 0.100 / 0.155 | 586 | 0.108 / 0.167 | 0 |
| R003 | read / 2 | 3 | 1.754 / 2.473 | 3 | 1.758 / 2.497 | 0 |
| R003 | read / 3 | 4 | 3.290 / 4.485 | 4 | 3.297 / 4.492 | 0 |
| R003 | review / 1 | 6 | 1.362 / 1.840 | 6 | 1.365 / 1.851 | 0 |
| R003 | switch / 1 | 14 | 0.533 / 0.692 | 14 | 0.543 / 0.696 | 0 |
| R003 | think / 1 | 6 | 0.715 / 1.130 | 6 | 0.726 / 1.136 | 0 |

## Observer coverage and input validity

- R001: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R002: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R003: separate observer summary present (status completed); harness status completed; WMI collector available: False.

External sampling covers its own observation window. Chrome/Notepad are nonexclusive cohorts, CPU covers first-to-last samples, RSS can double-count shared memory, and scopes may overlap. Do not add these scopes to the controller total.

| Run | Observer scope | Processes | Observed CPU delta (s) | Peak simultaneous sampled RSS (MiB) |
| --- | --- | ---: | ---: | ---: |
| R001 | controller | 1 | 28.594 | 83.05 |
| R001 | chrome | 42 | 96.891 | 5954.95 |
| R001 | notepad | 3 | 8.203 | 222.76 |
| R001 | controller_descendants | 0 | 0.000 | 0.00 |
| R002 | controller | 1 | 29.844 | 82.34 |
| R002 | chrome | 36 | 94.984 | 5734.09 |
| R002 | notepad | 3 | 6.484 | 225.49 |
| R002 | controller_descendants | 0 | 0.000 | 0.00 |
| R003 | controller | 1 | 29.422 | 82.68 |
| R003 | chrome | 36 | 94.953 | 5523.46 |
| R003 | notepad | 3 | 7.047 | 226.23 |
| R003 | controller_descendants | 0 | 0.000 | 0.00 |

| Run | Observer snapshots | Duration (s) | Median / max sample gap (s) | Observer CPU (s) | Observer peak RSS (MiB) |
| --- | ---: | ---: | ---: | ---: | ---: |
| R001 | 1669 | 167.837 | 0.100 / 0.229 | 59.734 | 26.04 |
| R002 | 1734 | 174.205 | 0.100 / 0.106 | 68.062 | 27.54 |
| R003 | 1733 | 174.062 | 0.100 / 0.103 | 64.953 | 29.18 |

## Limits

- No human participant or human reference data was collected. Timing variation is not evidence of human similarity.
- No official score, winning probability, statistical significance or population reliability is inferred.
- Matching source version, environment and capture metadata is based on operator declarations, not independent verification.
- Task interval runs from the first step start through the final step completion; it excludes preparation, countdown, final verification and cleanup.
- Requested delays and measured controller waits are not measurements of native input delivery; application waits are not fully captured by timing events.
- Controller CPU and sampled peak RSS cover the full recorder window, not just the task interval, and exclude application resource use.
- Process observations are limited samples and may miss processes or peaks; named applications may include unrelated work.
- The declared environment may reuse warm, shared Chrome/Notepad processes; background activity is not assumed isolated.
- Repeated timing events within one run are correlated observations, not independent experimental replicates.
- A fixed/contextual comparison can measure the effect of the chosen timing policy; it cannot validate human authenticity.
