# External process-parent evidence

The separate observer sampled real OS process identities and parent metadata. The tables publish fixed application roles, aggregate counts and pseudonymized process observations.

**This is sampled process evidence, not a process-start trace.** Creation age uses OS-reported timestamps. Preexisting Chrome parentage does not establish how this run launched Chrome; application cohorts include unrelated activity. Human reference runs within this historical automated series: **0**. The later [unassisted human baseline](../human-baseline/README.md), including participant-reported measured process ancestry, is reported separately.

| Run | Policy | Observed identities | Compatible parent | Unresolved/conflicting parent | Preexisting | OS creation within window | Age unresolved |
|---|---|---:|---:|---:|---:|---:|---:|
| R001 | fixed | 46 | 46 | 0 | 32 | 14 | 0 |
| R002 | contextual | 40 | 39 | 1 | 32 | 8 | 0 |
| R003 | contextual | 40 | 38 | 2 | 32 | 8 | 0 |

Counts below sum identities separately within each run. The same warm process can appear in several runs; these totals are not distinct processes across the experiment.

| Scope | Application role | Parent role | Parent evidence | Creation class | Sum of per-run counts |
|---|---|---|---|---|---:|
| chrome | chrome | chrome | resolved-compatible-age | os-creation-time-within-observer-window | 16 |
| chrome | chrome | chrome | resolved-compatible-age | preexisting-at-observer-start | 91 |
| chrome | chrome | explorer | resolved-compatible-age | os-creation-time-within-observer-window | 3 |
| chrome | chrome | explorer | resolved-compatible-age | preexisting-at-observer-start | 3 |
| chrome | chrome | unresolved | unresolved | os-creation-time-within-observer-window | 1 |
| controller | python | python | resolved-compatible-age | os-creation-time-within-observer-window | 3 |
| notepad | notepad | notepad | resolved-compatible-age | os-creation-time-within-observer-window | 1 |
| notepad | notepad | python | resolved-compatible-age | os-creation-time-within-observer-window | 6 |
| notepad | notepad | unresolved | unresolved | preexisting-at-observer-start | 2 |

## Pseudonymized process observations

Aliases restart at P001 in each run. A blank parent alias means the compatible parent was outside the selected cohort or unresolved. Times are seconds from observer start; CPU is the sampled counter delta. RSS is each process's sampled peak in MiB, not a simultaneous memory total.

### R001 (fixed)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 23.266 | 658.05 |
| P002 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 131.515 | 1308 | 3.953 | 206.25 |
| P003 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.965 / 166.692 | 1620 | 28.594 | 83.05 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.578 | 63.23 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 22.953 | 1107.59 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.000 | 43.84 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.031 | 161.83 |
| P008 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 21.953 | 499.30 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.188 | 53.38 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.016 | 100.19 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 131.515 / 167.797 | 362 | 0.047 | 32.30 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 15.621 / 51.904 | 362 | 0.000 | 32.34 |
| P013 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.016 | 55.71 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.000 | 9.24 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 6.453 | 313.04 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 51.904 / 115.531 | 634 | 0.094 | 61.54 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.047 | 51.19 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.891 | 107.29 |
| P019 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.000 | 40.46 |
| P020 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.016 | 22.66 |
| P021 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.172 | 139.63 |
| P022 | chrome / chrome | P037 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 50.698 / 50.698 | 1 | 0.000 | 10.06 |
| P023 | notepad / notepad | P039 / notepad | resolved-compatible-age | os-creation-time-within-observer-window | 111.915 / 167.797 | 557 | 8.156 | 204.57 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.294 | 1664 | 1.375 | 222.65 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 52.005 / 116.033 | 638 | 0.234 | 64.04 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 2.797 | 79.57 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.000 | 72.71 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.000 | 93.84 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 1.391 | 126.74 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.062 | 139.20 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.031 | 20.06 |
| P032 | chrome / chrome | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 15.420 / 15.420 | 1 | 0.000 | 8.35 |
| P033 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.000 | 58.14 |
| P034 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.266 | 308.23 |
| P035 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.234 | 477.37 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.000 | 276.14 |
| P037 | chrome / chrome | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 50.698 / 50.698 | 1 | 0.000 | 8.35 |
| P038 | chrome / chrome | P032 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 15.420 / 15.420 | 1 | 0.000 | 10.06 |
| P039 | notepad / notepad | P003 / python | resolved-compatible-age | os-creation-time-within-observer-window | 111.814 / 161.866 | 499 | 0.031 | 18.20 |
| P040 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 129.504 / 167.797 | 382 | 5.219 | 231.93 |
| P041 | notepad / notepad | P003 / python | resolved-compatible-age | os-creation-time-within-observer-window | 162.671 / 167.797 | 52 | 0.016 | 17.73 |
| P042 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.000 | 167.12 |
| P043 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.078 | 262.41 |
| P044 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 3.766 | 375.52 |
| P045 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 54.014 / 131.414 | 771 | 0.000 | 38.36 |
| P046 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 167.797 | 1669 | 0.766 | 221.73 |

### R002 (contextual)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | P002 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 43.518 / 106.727 | 630 | 0.812 | 83.35 |
| P002 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 33.109 | 645.14 |
| P003 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 31.438 | 596.27 |
| P004 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.000 | 43.84 |
| P005 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.016 | 161.89 |
| P006 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 15.516 | 422.20 |
| P007 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.016 | 52.88 |
| P008 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.000 | 100.19 |
| P009 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.359 | 65.12 |
| P010 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.000 | 55.74 |
| P011 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.016 | 9.24 |
| P012 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 5.094 | 295.00 |
| P013 | notepad / notepad | P036 / python | resolved-compatible-age | os-creation-time-within-observer-window | 115.767 / 168.314 | 524 | 0.031 | 17.75 |
| P014 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.000 | 51.19 |
| P015 | chrome / chrome | — / explorer | resolved-compatible-age | os-creation-time-within-observer-window | 14.473 / 14.473 | 1 | 0.000 | 8.36 |
| P016 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.172 | 96.61 |
| P017 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.016 | 40.47 |
| P018 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.000 | 22.70 |
| P019 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.125 | 139.76 |
| P020 | chrome / chrome | P002 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 43.417 / 106.225 | 626 | 0.125 | 61.64 |
| P021 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 6.453 | 207.76 |
| P022 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 1.594 | 72.42 |
| P023 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.000 | 72.71 |
| P024 | chrome / chrome | P002 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 14.674 / 43.417 | 287 | 0.000 | 32.31 |
| P025 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.000 | 93.77 |
| P026 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.844 | 132.13 |
| P027 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.047 | 139.90 |
| P028 | notepad / notepad | P036 / python | resolved-compatible-age | os-creation-time-within-observer-window | 169.220 / 174.165 | 50 | 0.000 | 17.75 |
| P029 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.031 | 20.04 |
| P030 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.016 | 58.14 |
| P031 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.078 | 308.22 |
| P032 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.641 | 487.26 |
| P033 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.000 | 276.18 |
| P034 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.453 | 176.03 |
| P035 | chrome / chrome | P002 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 45.627 / 174.165 | 1280 | 0.062 | 34.87 |
| P036 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.619 / 173.060 | 1687 | 29.844 | 82.34 |
| P037 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.016 | 167.12 |
| P038 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.062 | 262.58 |
| P039 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 3.438 | 374.68 |
| P040 | chrome / chrome | P002 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.165 | 1734 | 0.891 | 222.36 |

### R003 (contextual)

| Process | Scope / role | Parent alias / role | Parent evidence | Creation class | First / last (s) | Samples | CPU (s) | Peak RSS (MiB) |
|---|---|---|---|---|---:|---:|---:|---:|
| P001 | chrome / chrome | — / explorer | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 31.828 | 642.33 |
| P002 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 31.984 | 553.92 |
| P003 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.000 | 43.86 |
| P004 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.031 | 162.09 |
| P005 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 14.594 | 436.97 |
| P006 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.109 | 53.17 |
| P007 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.000 | 100.19 |
| P008 | notepad / notepad | P035 / python | resolved-compatible-age | os-creation-time-within-observer-window | 167.993 / 174.020 | 61 | 0.000 | 17.76 |
| P009 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.016 | 55.76 |
| P010 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.000 | 9.24 |
| P011 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 3.219 | 265.08 |
| P012 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 167.592 / 174.020 | 65 | 0.203 | 59.72 |
| P013 | notepad / notepad | P035 / python | resolved-compatible-age | os-creation-time-within-observer-window | 115.153 / 167.090 | 518 | 0.016 | 17.77 |
| P014 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.016 | 51.20 |
| P015 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.156 | 96.09 |
| P016 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.000 | 40.51 |
| P017 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.000 | 22.80 |
| P018 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.016 | 139.07 |
| P019 | notepad / notepad | — / unresolved | unresolved | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 7.031 | 208.49 |
| P020 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 1.719 | 72.20 |
| P021 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.000 | 72.73 |
| P022 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.047 | 93.77 |
| P023 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.875 | 135.82 |
| P024 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.047 | 139.33 |
| P025 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.016 | 19.87 |
| P026 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.000 | 58.26 |
| P027 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 1.516 | 317.39 |
| P028 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 2.297 | 487.31 |
| P029 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.047 | 276.19 |
| P030 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 14.073 / 167.692 | 1530 | 0.000 | 32.34 |
| P031 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.031 | 170.65 |
| P032 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 167.792 / 174.020 | 63 | 2.031 | 132.45 |
| P033 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.531 | 65.96 |
| P034 | chrome / chrome | P001 / chrome | resolved-compatible-age | os-creation-time-within-observer-window | 169.801 / 174.020 | 43 | 0.094 | 32.18 |
| P035 | controller / python | — / python | resolved-compatible-age | os-creation-time-within-observer-window | 3.618 / 172.915 | 1686 | 29.422 | 82.68 |
| P036 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.016 | 167.12 |
| P037 | chrome / chrome | — / unresolved | unresolved | os-creation-time-within-observer-window | 13.972 / 13.972 | 1 | 0.000 | 10.12 |
| P038 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.031 | 262.58 |
| P039 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 2.609 | 360.52 |
| P040 | chrome / chrome | P001 / chrome | resolved-compatible-age | preexisting-at-observer-start | 0.001 / 174.020 | 1733 | 0.875 | 222.42 |

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
- Human reference runs within this historical automated series: 0; the later [participant-reported baseline](../human-baseline/README.md) is separate. Process parentage and automated timing evidence do not establish human similarity.
