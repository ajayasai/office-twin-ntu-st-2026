# Controlled timing benchmark — observed evidence

10 attempts; 10 complete, verified native tasks; 5 comparable fixed/contextual pairs under declared matching conditions.

**This automated series contains no human-reference runs.** The subsequent [720-second unassisted human baseline](../human-baseline/README.md) is reported separately from participant-supplied measurements. This automated comparison does not establish human similarity or an official score; its retained JSON preserves the original series scope.

Run aliases correspond to manifest order (then explicit run arguments); duplicate paths are excluded. No source paths, Sheet IDs, process command lines, raw error text or event payloads are exported.

| Run | Policy / seed | Status | Steps | Task interval (s) | Full wall (s) | Controller CPU (s) | Sampled controller RSS (MiB) |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| R001 | fixed / 211 | desktop: completed | 11/11 | 158.986 | 166.172 | 28.516 | 72.91 |
| R002 | contextual / 211 | desktop: completed | 11/11 | 168.434 | 175.527 | 28.781 | 72.86 |
| R003 | contextual / 223 | desktop: completed | 11/11 | 164.204 | 170.258 | 18.578 | 72.77 |
| R004 | fixed / 223 | desktop: completed | 11/11 | 152.946 | 159.270 | 18.359 | 72.87 |
| R005 | fixed / 227 | desktop: completed | 11/11 | 153.130 | 159.591 | 19.438 | 72.78 |
| R006 | contextual / 227 | desktop: completed | 11/11 | 167.080 | 173.372 | 21.297 | 73.09 |
| R007 | contextual / 229 | desktop: completed | 11/11 | 158.781 | 165.213 | 19.344 | 73.08 |
| R008 | fixed / 229 | desktop: completed | 11/11 | 153.230 | 159.789 | 18.125 | 72.93 |
| R009 | fixed / 233 | desktop: completed | 11/11 | 152.245 | 158.496 | 19.141 | 72.72 |
| R010 | contextual / 233 | desktop: completed | 11/11 | 169.347 | 175.306 | 20.609 | 72.88 |

## Paired comparison

Deltas below are contextual minus fixed. A shorter or lower-resource incomplete run is never treated as an improvement.

- **P001 (R001, R002)**: comparable under declared conditions.
  Task delta 9.448 s; full-window controller CPU delta 0.266 CPU-s. This measures policy cost, not human realism.
- **P002 (R003, R004)**: comparable under declared conditions.
  Task delta 11.258 s; full-window controller CPU delta 0.219 CPU-s. This measures policy cost, not human realism.
- **P003 (R005, R006)**: comparable under declared conditions.
  Task delta 13.950 s; full-window controller CPU delta 1.859 CPU-s. This measures policy cost, not human realism.
- **P004 (R007, R008)**: comparable under declared conditions.
  Task delta 5.550 s; full-window controller CPU delta 1.219 CPU-s. This measures policy cost, not human realism.
- **P005 (R009, R010)**: comparable under declared conditions.
  Task delta 17.102 s; full-window controller CPU delta 1.469 CPU-s. This measures policy cost, not human realism.

Across 5 comparable pairs, task-duration delta median is 11.258 s (range 5.550 to 17.102 s). These are descriptive paired observations, not a significance test.

## Requested and observed waits

Samples are grouped by action kind and unit count. These are controller waits; correlated events are not independent task trials. Interrupted waits remain in the data.

| Run | Kind / units | Requested n | Requested median / p90 (s) | Actual n | Actual median / p90 (s) | Interrupted |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| R001 | correction / 1 | 1 | 0.350 / 0.350 | 1 | 0.362 / 0.362 | 0 |
| R001 | key / 1 | 586 | 0.095 / 0.095 | 586 | 0.100 / 0.110 | 0 |
| R001 | read / 2 | 3 | 1.600 / 1.600 | 3 | 1.601 / 1.607 | 0 |
| R001 | read / 3 | 4 | 2.400 / 2.400 | 4 | 2.410 / 2.413 | 0 |
| R001 | review / 1 | 6 | 1.300 / 1.300 | 6 | 1.304 / 1.312 | 0 |
| R001 | switch / 1 | 16 | 0.450 / 0.450 | 16 | 0.459 / 0.469 | 0 |
| R001 | think / 1 | 6 | 1.100 / 1.100 | 6 | 1.108 / 1.113 | 0 |
| R002 | correction / 1 | 1 | 0.259 / 0.259 | 1 | 0.273 / 0.273 | 0 |
| R002 | key / 1 | 586 | 0.096 / 0.154 | 586 | 0.105 / 0.164 | 0 |
| R002 | read / 2 | 3 | 1.566 / 1.740 | 3 | 1.573 / 1.747 | 0 |
| R002 | read / 3 | 4 | 2.581 / 3.362 | 4 | 2.587 / 3.368 | 0 |
| R002 | review / 1 | 6 | 1.470 / 2.284 | 6 | 1.476 / 2.289 | 0 |
| R002 | switch / 1 | 16 | 0.514 / 0.866 | 16 | 0.524 / 0.878 | 0 |
| R002 | think / 1 | 6 | 1.530 / 2.518 | 6 | 1.539 / 2.546 | 0 |
| R003 | correction / 1 | 1 | 0.231 / 0.231 | 1 | 0.245 / 0.245 | 0 |
| R003 | key / 1 | 586 | 0.098 / 0.154 | 586 | 0.108 / 0.164 | 0 |
| R003 | read / 2 | 3 | 1.754 / 2.473 | 3 | 1.770 / 2.482 | 0 |
| R003 | read / 3 | 4 | 3.290 / 4.485 | 4 | 3.297 / 4.490 | 0 |
| R003 | review / 1 | 6 | 1.359 / 1.799 | 6 | 1.368 / 1.809 | 0 |
| R003 | switch / 1 | 16 | 0.468 / 0.691 | 16 | 0.472 / 0.702 | 0 |
| R003 | think / 1 | 6 | 0.715 / 1.130 | 6 | 0.730 / 1.138 | 0 |
| R004 | correction / 1 | 1 | 0.350 / 0.350 | 1 | 0.353 / 0.353 | 0 |
| R004 | key / 1 | 586 | 0.095 / 0.095 | 586 | 0.102 / 0.110 | 0 |
| R004 | read / 2 | 3 | 1.600 / 1.600 | 3 | 1.614 / 1.632 | 0 |
| R004 | read / 3 | 4 | 2.400 / 2.400 | 4 | 2.407 / 2.412 | 0 |
| R004 | review / 1 | 6 | 1.300 / 1.300 | 6 | 1.311 / 1.320 | 0 |
| R004 | switch / 1 | 16 | 0.450 / 0.450 | 16 | 0.461 / 0.465 | 0 |
| R004 | think / 1 | 6 | 1.100 / 1.100 | 6 | 1.109 / 1.118 | 0 |
| R005 | correction / 1 | 1 | 0.350 / 0.350 | 1 | 0.360 / 0.360 | 0 |
| R005 | key / 1 | 586 | 0.095 / 0.095 | 586 | 0.101 / 0.110 | 0 |
| R005 | read / 2 | 3 | 1.600 / 1.600 | 3 | 1.610 / 1.611 | 0 |
| R005 | read / 3 | 4 | 2.400 / 2.400 | 4 | 2.410 / 2.415 | 0 |
| R005 | review / 1 | 6 | 1.300 / 1.300 | 6 | 1.309 / 1.313 | 0 |
| R005 | switch / 1 | 16 | 0.450 / 0.450 | 16 | 0.461 / 0.464 | 0 |
| R005 | think / 1 | 6 | 1.100 / 1.100 | 6 | 1.108 / 1.111 | 0 |
| R006 | correction / 1 | 1 | 0.194 / 0.194 | 1 | 0.195 / 0.195 | 0 |
| R006 | key / 1 | 586 | 0.099 / 0.165 | 586 | 0.108 / 0.178 | 0 |
| R006 | read / 2 | 3 | 1.369 / 2.426 | 3 | 1.386 / 2.434 | 0 |
| R006 | read / 3 | 4 | 2.470 / 3.763 | 4 | 2.475 / 3.766 | 0 |
| R006 | review / 1 | 6 | 1.871 / 2.358 | 6 | 1.877 / 2.370 | 0 |
| R006 | switch / 1 | 16 | 0.469 / 0.954 | 16 | 0.478 / 0.973 | 0 |
| R006 | think / 1 | 6 | 1.398 / 1.927 | 6 | 1.408 / 1.940 | 0 |
| R007 | correction / 1 | 1 | 0.172 / 0.172 | 1 | 0.178 / 0.178 | 0 |
| R007 | key / 1 | 586 | 0.097 / 0.154 | 586 | 0.108 / 0.161 | 0 |
| R007 | read / 2 | 3 | 1.571 / 2.082 | 3 | 1.579 / 2.092 | 0 |
| R007 | read / 3 | 4 | 2.614 / 4.276 | 4 | 2.620 / 4.284 | 0 |
| R007 | review / 1 | 6 | 0.989 / 2.125 | 6 | 1.002 / 2.137 | 0 |
| R007 | switch / 1 | 16 | 0.481 / 0.861 | 16 | 0.492 / 0.874 | 0 |
| R007 | think / 1 | 6 | 1.023 / 1.668 | 6 | 1.037 / 1.678 | 0 |
| R008 | correction / 1 | 1 | 0.350 / 0.350 | 1 | 0.359 / 0.359 | 0 |
| R008 | key / 1 | 586 | 0.095 / 0.095 | 586 | 0.100 / 0.110 | 0 |
| R008 | read / 2 | 3 | 1.600 / 1.600 | 3 | 1.611 / 1.615 | 0 |
| R008 | read / 3 | 4 | 2.400 / 2.400 | 4 | 2.406 / 2.412 | 0 |
| R008 | review / 1 | 6 | 1.300 / 1.300 | 6 | 1.303 / 1.313 | 0 |
| R008 | switch / 1 | 16 | 0.450 / 0.450 | 16 | 0.460 / 0.464 | 0 |
| R008 | think / 1 | 6 | 1.100 / 1.100 | 6 | 1.110 / 1.119 | 0 |
| R009 | correction / 1 | 1 | 0.350 / 0.350 | 1 | 0.362 / 0.362 | 0 |
| R009 | key / 1 | 586 | 0.095 / 0.095 | 586 | 0.102 / 0.110 | 0 |
| R009 | read / 2 | 3 | 1.600 / 1.600 | 3 | 1.607 / 1.615 | 0 |
| R009 | read / 3 | 4 | 2.400 / 2.400 | 4 | 2.406 / 2.409 | 0 |
| R009 | review / 1 | 6 | 1.300 / 1.300 | 6 | 1.311 / 1.314 | 0 |
| R009 | switch / 1 | 16 | 0.450 / 0.450 | 16 | 0.458 / 0.463 | 0 |
| R009 | think / 1 | 6 | 1.100 / 1.100 | 6 | 1.109 / 1.112 | 0 |
| R010 | correction / 1 | 1 | 0.453 / 0.453 | 1 | 0.464 / 0.464 | 0 |
| R010 | key / 1 | 586 | 0.100 / 0.163 | 586 | 0.110 / 0.172 | 0 |
| R010 | read / 2 | 3 | 1.430 / 1.953 | 3 | 1.439 / 1.956 | 0 |
| R010 | read / 3 | 4 | 2.776 / 3.198 | 4 | 2.782 / 3.205 | 0 |
| R010 | review / 1 | 6 | 1.690 / 2.808 | 6 | 1.697 / 2.814 | 0 |
| R010 | switch / 1 | 16 | 0.389 / 0.623 | 16 | 0.393 / 0.628 | 0 |
| R010 | think / 1 | 6 | 1.131 / 2.417 | 6 | 1.142 / 2.425 | 0 |

## Observer coverage and input validity

- R001: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R002: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R003: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R004: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R005: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R006: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R007: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R008: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R009: separate observer summary present (status completed); harness status completed; WMI collector available: False.
- R010: separate observer summary present (status completed); harness status completed; WMI collector available: False.

External sampling covers its own observation window. Chrome/Notepad are nonexclusive cohorts, CPU covers first-to-last samples, RSS can double-count shared memory, and scopes may overlap. Do not add these scopes to the controller total.

| Run | Observer scope | Processes | Observed CPU delta (s) | Peak simultaneous sampled RSS (MiB) |
| --- | --- | ---: | ---: | ---: |
| R001 | controller | 1 | 28.562 | 73.92 |
| R001 | chrome | 37 | 88.531 | 5327.53 |
| R001 | notepad | 2 | 6.859 | 208.50 |
| R001 | controller_descendants | 0 | 0.000 | 0.00 |
| R002 | controller | 1 | 28.859 | 73.61 |
| R002 | chrome | 35 | 89.703 | 5325.13 |
| R002 | notepad | 2 | 6.125 | 206.75 |
| R002 | controller_descendants | 0 | 0.000 | 0.00 |
| R003 | controller | 1 | 18.625 | 73.49 |
| R003 | chrome | 35 | 62.484 | 5416.14 |
| R003 | notepad | 1 | 4.797 | 207.08 |
| R003 | controller_descendants | 0 | 0.000 | 0.00 |
| R004 | controller | 1 | 18.297 | 73.91 |
| R004 | chrome | 32 | 57.125 | 5242.55 |
| R004 | notepad | 2 | 4.969 | 216.50 |
| R004 | controller_descendants | 0 | 0.000 | 0.00 |
| R005 | controller | 1 | 19.484 | 73.50 |
| R005 | chrome | 37 | 63.203 | 5363.91 |
| R005 | notepad | 1 | 4.141 | 205.62 |
| R005 | controller_descendants | 0 | 0.000 | 0.00 |
| R006 | controller | 1 | 21.438 | 74.19 |
| R006 | chrome | 34 | 64.031 | 5203.20 |
| R006 | notepad | 2 | 4.438 | 206.84 |
| R006 | controller_descendants | 0 | 0.000 | 0.00 |
| R007 | controller | 1 | 19.312 | 74.20 |
| R007 | chrome | 37 | 63.562 | 5305.83 |
| R007 | notepad | 3 | 4.406 | 216.06 |
| R007 | controller_descendants | 0 | 0.000 | 0.00 |
| R008 | controller | 1 | 18.188 | 74.00 |
| R008 | chrome | 35 | 66.359 | 5108.39 |
| R008 | notepad | 2 | 4.344 | 198.96 |
| R008 | controller_descendants | 0 | 0.000 | 0.00 |
| R009 | controller | 1 | 19.094 | 73.75 |
| R009 | chrome | 34 | 63.031 | 5026.26 |
| R009 | notepad | 1 | 4.922 | 163.15 |
| R009 | controller_descendants | 0 | 0.000 | 0.00 |
| R010 | controller | 1 | 20.641 | 74.16 |
| R010 | chrome | 37 | 65.859 | 4658.38 |
| R010 | notepad | 2 | 4.531 | 129.27 |
| R010 | controller_descendants | 0 | 0.000 | 0.00 |

| Run | Observer snapshots | Duration (s) | Median / max sample gap (s) | Observer CPU (s) | Observer peak RSS (MiB) |
| --- | ---: | ---: | ---: | ---: | ---: |
| R001 | 1704 | 171.148 | 0.100 / 0.105 | 61.234 | 28.91 |
| R002 | 1796 | 180.401 | 0.100 / 0.108 | 65.875 | 29.28 |
| R003 | 1741 | 174.816 | 0.100 / 0.117 | 43.703 | 28.22 |
| R004 | 1632 | 163.813 | 0.100 / 0.103 | 40.953 | 27.53 |
| R005 | 1635 | 164.120 | 0.100 / 0.111 | 42.172 | 26.45 |
| R006 | 1773 | 177.964 | 0.100 / 0.106 | 42.312 | 29.17 |
| R007 | 1690 | 169.678 | 0.100 / 0.103 | 39.703 | 28.20 |
| R008 | 1636 | 164.398 | 0.100 / 0.112 | 38.359 | 27.64 |
| R009 | 1620 | 163.040 | 0.100 / 0.511 | 39.484 | 27.58 |
| R010 | 1791 | 179.841 | 0.100 / 0.111 | 43.578 | 29.16 |

## Limits

- No human-reference data was collected within this automated series. The later [participant-reported human baseline](../human-baseline/README.md) is separate; timing variation is not evidence of human similarity.
- No official score, winning probability, statistical significance or population reliability is inferred.
- Matching source version, environment and capture metadata is based on operator declarations, not independent verification.
- Task interval runs from the first step start through the final step completion; it excludes preparation, countdown, final verification and cleanup.
- Requested delays and measured controller waits are not measurements of native input delivery; application waits are not fully captured by timing events.
- Controller CPU and sampled peak RSS cover the full recorder window, not just the task interval, and exclude application resource use.
- Process observations are limited samples and may miss processes or peaks; named applications may include unrelated work.
- The declared environment may reuse warm, shared Chrome/Notepad processes; background activity is not assumed isolated.
- Repeated timing events within one run are correlated observations, not independent experimental replicates.
- A fixed/contextual comparison can measure the effect of the chosen timing policy; it cannot validate human authenticity.
