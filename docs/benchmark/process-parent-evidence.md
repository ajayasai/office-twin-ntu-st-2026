# External process-parent evidence

The separate observer sampled real OS process identities and parent metadata. The tables publish fixed application roles, aggregate counts and pseudonymized process observations.

**This is sampled process evidence, not a process-start trace.** Creation age uses OS-reported timestamps. Preexisting Chrome parentage does not establish how this run launched Chrome; application cohorts include unrelated activity. Human reference runs: **0**.

| Run | Policy | Observed identities | Compatible parent | Unresolved/conflicting parent | Preexisting | OS creation within window | Age unresolved |
|---|---|---:|---:|---:|---:|---:|---:|
| R001 | fixed | 40 | 39 | 1 | 32 | 8 | 0 |
| R002 | contextual | 38 | 37 | 1 | 34 | 4 | 0 |
| R003 | contextual | 37 | 36 | 1 | 32 | 5 | 0 |
| R004 | fixed | 35 | 34 | 1 | 32 | 3 | 0 |
| R005 | fixed | 39 | 38 | 1 | 32 | 7 | 0 |
| R006 | contextual | 37 | 36 | 1 | 32 | 5 | 0 |
| R007 | contextual | 41 | 40 | 1 | 32 | 9 | 0 |
| R008 | fixed | 38 | 37 | 1 | 32 | 6 | 0 |
| R009 | fixed | 36 | 35 | 1 | 34 | 2 | 0 |
| R010 | contextual | 40 | 39 | 1 | 32 | 8 | 0 |

Counts below sum identities separately within each run. The same warm process can appear in several runs; these totals are not distinct processes across the experiment.

| Scope | Application role | Parent role | Parent evidence | Creation class | Sum of per-run counts |
|---|---|---|---|---|---:|
| chrome | chrome | chrome | resolved-compatible-age | os-creation-time-within-observer-window | 33 |
| chrome | chrome | chrome | resolved-compatible-age | preexisting-at-observer-start | 304 |
| chrome | chrome | explorer | resolved-compatible-age | os-creation-time-within-observer-window | 6 |
| chrome | chrome | explorer | resolved-compatible-age | preexisting-at-observer-start | 10 |
| controller | python | python | resolved-compatible-age | os-creation-time-within-observer-window | 10 |
| notepad | notepad | explorer | resolved-compatible-age | os-creation-time-within-observer-window | 8 |
| notepad | notepad | unresolved | unresolved | preexisting-at-observer-start | 10 |

## Pseudonymized process observations

Aliases restart at P001 in each run. A blank parent alias means the compatible parent was outside the selected cohort or unresolved. Times are seconds from observer start; CPU is the sampled counter delta. RSS is each process's sampled peak in MiB, not a simultaneous memory total.

### R001 (fixed)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 30.641 | 631.49 |
| P002 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 29.141 | 560.54 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.000 | 41.16 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.016 | 150.69 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 14.062 | 418.00 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 145.881 / 171.109 | 252 | 0.109 | 32.50 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.047 | 52.97 |
| P008 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.016 | 78.48 |
| P009 | chrome / chrome | P013 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 14.373 / 14.373 | 1 | 0.000 | 10.05 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 143.770 / 171.109 | 273 | 0.406 | 62.95 |
| P011 | notepad / notepad | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 165.284 / 165.284 | 1 | 0.000 | 8.32 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.062 | 54.84 |
| P013 | chrome / chrome | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 14.373 / 14.373 | 1 | 0.000 | 8.82 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.000 | 9.24 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 3.234 | 271.62 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.031 | 48.52 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.125 | 95.78 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.047 | 40.28 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.016 | 22.61 |
| P020 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.031 | 139.48 |
| P021 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 6.859 | 206.56 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 143.669 / 171.109 | 274 | 0.109 | 62.40 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 1.406 | 71.54 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.000 | 67.34 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.000 | 93.75 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.703 | 130.12 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.062 | 124.83 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.031 | 19.67 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.000 | 54.38 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 4.438 | 377.80 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.250 | 461.95 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.000 | 276.12 |
| P033 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 14.473 / 143.669 | 1287 | 0.000 | 32.27 |
| P034 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.718 / 170.004 | 1656 | 28.562 | 73.92 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.000 | 167.89 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.422 | 63.05 |
| P037 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.016 | 158.27 |
| P038 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 0.375 | 252.93 |
| P039 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 1.453 | 370.50 |
| P040 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 171.109 | 1704 | 1.281 | 206.99 |

### R002 (contextual)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 31.266 | 629.43 |
| P002 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 29.922 | 513.75 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.000 | 41.04 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.031 | 147.52 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 16.094 | 423.85 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.438 | 65.52 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.109 | 53.31 |
| P008 | chrome / chrome | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 14.085 / 14.085 | 1 | 0.000 | 8.18 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.016 | 77.68 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 32.977 | 329 | 0.078 | 64.69 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.000 | 54.82 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.000 | 9.29 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 3.203 | 267.50 |
| P014 | notepad / notepad | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 119.905 / 119.905 | 1 | 0.000 | 5.04 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.000 | 48.24 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.141 | 95.73 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.016 | 40.58 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.016 | 22.46 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.047 | 139.70 |
| P020 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 6.125 | 206.75 |
| P021 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 32.575 | 325 | 0.094 | 64.32 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 1.469 | 71.78 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.000 | 67.29 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.000 | 93.65 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.688 | 134.28 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.109 | 125.28 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.031 | 19.97 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.031 | 54.41 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.094 | 309.62 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 2.484 | 462.04 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.000 | 276.38 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.000 | 166.87 |
| P033 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.016 | 109.29 |
| P034 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.625 / 179.266 | 1749 | 28.859 | 73.61 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.125 | 238.37 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 2.281 | 360.91 |
| P037 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.007 / 180.372 | 1796 | 0.906 | 195.03 |
| P038 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 14.286 / 180.372 | 1654 | 0.000 | 32.39 |

### R003 (contextual)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 21.875 | 637.14 |
| P002 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 21.156 | 514.95 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 41.04 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.016 | 147.54 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 10.031 | 422.11 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 53.32 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 77.71 |
| P008 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 54.87 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 9.29 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 88.909 / 153.189 | 641 | 0.078 | 62.06 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 2.453 | 264.70 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 48.25 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.062 | 91.44 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 40.59 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 22.46 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.047 | 139.50 |
| P017 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 4.797 | 207.08 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 1.250 | 71.80 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 67.30 |
| P020 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.757 / 88.909 | 759 | 0.000 | 32.42 |
| P021 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 86.80 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.844 | 137.98 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.031 | 125.27 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 20.31 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.016 | 54.41 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.031 | 308.29 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.547 | 436.79 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.016 | 276.39 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 166.87 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 89.009 / 153.691 | 645 | 1.891 | 138.02 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 91.017 / 174.796 | 835 | 0.047 | 34.89 |
| P032 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.316 / 173.691 | 1697 | 18.625 | 73.49 |
| P033 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.000 | 101.86 |
| P034 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.047 | 210.27 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 1.203 | 363.15 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.469 | 194.01 |
| P037 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 174.796 | 1741 | 0.375 | 65.48 |

### R004 (fixed)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 20.453 | 630.79 |
| P002 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 20.422 | 500.92 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.000 | 41.04 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.031 | 147.54 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 9.062 | 439.84 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.031 | 53.34 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.000 | 77.71 |
| P008 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.000 | 54.88 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.000 | 9.29 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 2.078 | 262.55 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.016 | 48.25 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.141 | 91.70 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.000 | 40.59 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.016 | 22.45 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.047 | 139.58 |
| P016 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 4.969 | 207.30 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 1.141 | 72.14 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.000 | 67.30 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.000 | 86.79 |
| P020 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.859 | 137.42 |
| P021 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.016 | 124.88 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.000 | 19.96 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.016 | 54.39 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.078 | 309.14 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.359 | 436.81 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.016 | 276.39 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.359 / 163.784 | 1509 | 0.000 | 32.34 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.031 | 166.66 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.391 | 65.54 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.000 | 101.87 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.078 | 210.28 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 1.172 | 371.21 |
| P033 | notepad / notepad | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 107.652 / 107.652 | 1 | 0.000 | 17.77 |
| P034 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.784 | 1632 | 0.672 | 195.78 |
| P035 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.412 / 162.680 | 1587 | 18.297 | 73.91 |

### R005 (fixed)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 22.219 | 634.87 |
| P002 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 19.797 | 498.06 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.016 | 41.04 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.016 | 147.54 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 9.234 | 450.76 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.062 | 53.34 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.016 | 77.80 |
| P008 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.000 | 55.05 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.000 | 9.29 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 2.188 | 264.60 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.000 | 48.23 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.141 | 89.26 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.000 | 40.62 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.016 | 22.55 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.078 | 139.75 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.153 / 48.617 | 364 | 0.031 | 35.04 |
| P017 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 4.141 | 205.62 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 1.391 | 71.89 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.000 | 67.31 |
| P020 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.000 | 84.94 |
| P021 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.859 | 135.64 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.031 | 125.32 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.031 | 20.23 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.016 | 54.39 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.172 | 313.65 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 3.672 | 450.63 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.000 | 276.39 |
| P028 | chrome / chrome | P029 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.053 / 12.053 | 1 | 0.000 | 10.06 |
| P029 | chrome / chrome | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 12.053 / 12.053 | 1 | 0.000 | 12.04 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 48.717 / 111.376 | 625 | 0.266 | 64.98 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.391 | 63.08 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.031 | 166.66 |
| P033 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.313 / 162.984 | 1591 | 19.484 | 73.50 |
| P034 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.016 | 101.80 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.250 | 211.29 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 1.516 | 369.90 |
| P037 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 50.728 / 164.087 | 1130 | 0.031 | 34.91 |
| P038 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 48.617 / 110.874 | 621 | 0.094 | 64.86 |
| P039 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 164.087 | 1635 | 0.625 | 197.31 |

### R006 (contextual)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 22.547 | 631.70 |
| P002 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 23.078 | 501.09 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 41.04 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 147.54 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 10.109 | 449.13 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.031 | 53.34 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 77.80 |
| P008 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.313 / 176.828 | 1729 | 21.438 | 74.19 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.016 | 55.06 |
| P010 | chrome / chrome | P021 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.153 / 12.153 | 1 | 0.000 | 10.07 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 9.29 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 2.641 | 262.45 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 48.23 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.031 | 89.34 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 40.57 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 22.44 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.047 | 139.83 |
| P018 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 4.438 | 206.84 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 1.172 | 71.65 |
| P020 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 67.31 |
| P021 | chrome / chrome | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 12.153 / 12.153 | 1 | 0.000 | 8.36 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 84.94 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.594 | 139.38 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.047 | 125.42 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 19.89 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 54.39 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.047 | 313.65 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 1.734 | 441.41 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 276.39 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.253 / 177.932 | 1651 | 0.016 | 35.05 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 166.66 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.000 | 101.81 |
| P033 | notepad / notepad | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 172.611 / 172.611 | 1 | 0.000 | 6.29 |
| P034 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.016 | 206.46 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 1.125 | 367.67 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.281 | 68.03 |
| P037 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 177.932 | 1773 | 0.500 | 195.94 |

### R007 (contextual)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 22.078 | 636.86 |
| P002 | chrome / chrome | P036 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.147 / 12.147 | 1 | 0.000 | 10.06 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 21.078 | 530.45 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 40.73 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 147.46 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 10.594 | 434.26 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.016 | 53.29 |
| P008 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 77.49 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 54.86 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 9.29 |
| P011 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.313 / 168.541 | 1646 | 19.312 | 74.20 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 2.281 | 264.08 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.016 | 47.82 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.062 | 89.32 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 40.55 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 22.44 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.031 | 124.92 |
| P018 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 4.406 | 204.99 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 1.312 | 72.05 |
| P020 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 66.86 |
| P021 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.016 | 65.46 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.703 | 135.52 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.016 | 124.59 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 20.25 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 54.31 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.062 | 308.83 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.828 | 438.92 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 275.26 |
| P029 | notepad / notepad | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 110.670 / 110.670 | 1 | 0.000 | 17.74 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 5.019 | 51 | 0.000 | 34.25 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 5.120 / 69.589 | 643 | 1.859 | 133.90 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 5.019 / 69.086 | 639 | 0.125 | 61.98 |
| P033 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.248 / 169.645 | 1568 | 0.000 | 32.31 |
| P034 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.000 | 166.25 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 7.128 / 169.645 | 1619 | 0.375 | 63.30 |
| P036 | chrome / chrome | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 12.147 / 12.147 | 1 | 0.000 | 8.36 |
| P037 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.016 | 100.18 |
| P038 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.062 | 193.93 |
| P039 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 1.531 | 365.18 |
| P040 | notepad / notepad | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 165.627 / 165.627 | 1 | 0.000 | 16.50 |
| P041 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 169.645 | 1690 | 0.500 | 196.93 |

### R008 (fixed)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 22.125 | 625.70 |
| P002 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.314 / 163.264 | 1592 | 18.188 | 74.00 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 134.625 / 164.369 | 297 | 0.328 | 80.57 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 19.641 | 448.18 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.000 | 40.74 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.047 | 147.46 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 9.625 | 446.14 |
| P008 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.125 | 53.29 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.000 | 77.49 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.031 | 54.86 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.016 | 9.29 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 2.125 | 261.93 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.000 | 47.82 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.016 | 89.34 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.031 | 40.59 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 136.733 / 164.369 | 276 | 0.000 | 34.86 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.000 | 22.46 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.047 | 124.92 |
| P019 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 4.344 | 198.96 |
| P020 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 1.047 | 75.82 |
| P021 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.000 | 66.86 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.000 | 65.46 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.625 | 139.71 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.047 | 123.86 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.031 | 19.94 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 134.625 / 164.369 | 297 | 0.016 | 62.54 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.016 | 54.31 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 2.016 | 312.73 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 6.562 | 503.05 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.000 | 275.26 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.354 / 134.525 | 1216 | 0.000 | 32.34 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.297 | 63.15 |
| P033 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.000 | 166.25 |
| P034 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.000 | 100.18 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.016 | 193.93 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 1.094 | 356.64 |
| P037 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 164.369 | 1636 | 0.438 | 197.01 |
| P038 | notepad / notepad | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 108.793 / 108.793 | 1 | 0.000 | 18.24 |

### R009 (fixed)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 21.141 | 613.51 |
| P002 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.413 / 161.910 | 1575 | 19.094 | 73.75 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 32.340 | 323 | 0.234 | 79.07 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 20.562 | 448.36 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.016 | 40.72 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 142.05 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 9.047 | 458.34 |
| P008 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.016 | 51.75 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 76.01 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 54.63 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.016 | 9.29 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.254 / 163.014 | 1498 | 0.000 | 32.37 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 2.641 | 261.11 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.031 | 47.80 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.172 | 86.52 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 40.58 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.359 | 65.15 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 22.44 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 105.30 |
| P020 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 4.922 | 163.15 |
| P021 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 1.062 | 73.03 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 66.84 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 65.19 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.891 | 139.11 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.031 | 124.16 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.016 | 20.22 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 31.837 | 318 | 0.016 | 64.30 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 54.13 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.062 | 296.48 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 4.438 | 464.61 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 203.33 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 158.24 |
| P033 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.000 | 97.12 |
| P034 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.094 | 183.88 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 1.328 | 344.77 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 163.014 | 1620 | 0.859 | 198.84 |

### R010 (contextual)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 23.219 | 465.22 |
| P002 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 22.391 | 397.06 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 40.45 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 105.28 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 10.016 | 416.39 |
| P006 | chrome / chrome | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 12.553 / 12.553 | 1 | 0.000 | 8.36 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.016 | 50.24 |
| P008 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 75.96 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.031 | 54.43 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.016 | 9.29 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.328 | 62.96 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.653 / 105.670 | 927 | 0.062 | 32.39 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 2.953 | 247.01 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 47.80 |
| P015 | notepad / notepad | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 174.478 / 174.478 | 1 | 0.000 | 9.88 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.109 | 73.71 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.031 | 40.55 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 22.44 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.016 | 95.37 |
| P020 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.315 / 178.695 | 1747 | 20.641 | 74.16 |
| P021 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 4.531 | 125.78 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 1.266 | 70.98 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 105.670 / 169.656 | 638 | 0.047 | 62.00 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 66.48 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.016 | 65.17 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.828 | 140.66 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.016 | 113.94 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 107.779 / 179.806 | 718 | 0.062 | 32.26 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.016 | 20.14 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 51.76 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.141 | 292.82 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.375 | 435.12 |
| P033 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 105.52 |
| P034 | chrome / chrome | P006 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 12.553 / 12.553 | 1 | 0.000 | 10.07 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 134.54 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 105.770 / 170.157 | 642 | 1.625 | 138.41 |
| P037 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.000 | 96.89 |
| P038 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.188 | 185.75 |
| P039 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 1.359 | 327.70 |
| P040 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.000 / 179.806 | 1791 | 0.734 | 198.21 |

## Interpretation limits

- These are external OS inventory/resource snapshots from a separate process, not Sysmon/ETW process-start events or an independent third-party audit.
- Creation classification compares the OS-reported creation timestamp with the observer window; it is not an observed process-start event and does not establish who caused the launch.
- Parent PID and identity are best-effort sampled metadata. A resolved parent must match the recorded parent PID and have a creation time no later than its child; this check does not prove the original launch chain.
- Preexisting Chrome processes may have Explorer parentage from before the task. Such relationships do not prove that this run launched Chrome through Explorer.
- Chrome and Notepad cohorts include shared tabs, documents and unrelated activity. Process relationships do not establish exclusive workload attribution or delivered desktop input.
- Polling can miss short-lived processes and inaccessible or exited parents. Missing observations are not evidence that a process or relationship never existed.
- Each run counts unique PID-plus-creation-time identities privately. Cross-run totals sum per-run counts, so a reused warm process can be counted in multiple runs.
- P001-style aliases are local to each run and are not stable across runs. A parent alias is included only when that compatible parent identity was itself observed in the selected process cohort.
- Per-process CPU covers first-to-last sampled counters, not lifetime CPU. Peak RSS is a sampled process maximum; per-process memory peaks must not be added to infer simultaneous or unique physical memory.
- Only fixed application roles are published; all other process names are redacted. PIDs, raw creation timestamps, source paths, command lines, URLs and account information are not exported.
- Human reference runs: 0. Process parentage and automated timing evidence do not establish human similarity.
