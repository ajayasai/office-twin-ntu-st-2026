## Evidence at a glance

| Official criterion | Weight | Evidence to inspect |
| --- | --- | --- |
| Process Telemetry Authenticity | 30% | New rundown capture verifies 32/32 application focus observations and 16/16 new application-start parent relationships: 2 Explorer → Chrome, 10 Chrome → Chrome, 4 Explorer → Notepad. Also 28/28 known canaries and zero reported final ETW loss. |
| Human Entropy & Timing | 30% | Five controlled fixed/contextual pairs, measured wait variation, and a participant-confirmed unassisted human baseline: 720 seconds, 42 WPM and 14 corrected error episodes. |
| Complexity of Action | 20% | Ten controlled native tasks completed all 11 steps; two separate successful ETW pairs also completed 11/11 each. Three quotes, six formulas, deadline eligibility and a saved/reopened recommendation form one connected decision. Failed attempts remain documented. |
| Resource Efficiency | 20% | Median controller CPU: 19.14 / 20.61 CPU-s (fixed/contextual); sampled peak controller RSS: 72.72–73.09 MiB. Runtime makes no cloud-model calls; observer and application costs are reported separately. |

Start with the [judging guide](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/JUDGING_GUIDE.md) for evidence links, exact measurement boundaries, expected outputs and reproduction commands. These are observed and participant-reported results, not a calculated judging score.

### Latest process evidence: existing identities and real parent relationships

The [new rundown validation](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/process-rundown/README.md) verifies **32/32 recorded focus observations** against three preexisting application identities: Chrome/Sheets, Notepad and Explorer. Exact creation timestamps from two independent OS snapshots agree with actual Windows rundown records before and after the native work. Existing applications remained open throughout.

All **16 new application starts** inside the task windows have resolved parent identities: **2 Explorer → Chrome, 10 Chrome → Chrome, and 4 Explorer → Notepad**. These are compatible lifetime/sequence relationships, stronger than parent-PID comparisons alone. Thirteen of these application identities have observed exits within the capture; three Chrome processes are confirmed present in the final rundown. Shared application cohorts can include unrelated activity, so the counts do not imply exclusive task causation.

Both new fixed/contextual tasks completed **11/11 steps**, with saved text and reloaded Sheet values verified. **28/28 known canary lifecycles** passed parent, time-boundary and exit-code checks; **26 lived under 100 ms**. The 354.908-second capture contains **1,300 process-provider records: 185 starts, 185 stops and 930 rundown records**. All three final logger-loss counters were zero. Rundown is observed existing state, not a newly observed start; equal start/stop totals are not assumed to be paired identities.

The remaining ancestry boundary is explicit: the **three existing main applications' original parents had already exited**, and their identities cannot be recovered from this trace. The new result closes current focus-identity coverage and resolves the parents of observed application starts; it does not claim complete historical ancestry or universal event completeness. Only the temporary collector runs elevated. Public evidence uses anonymous aliases, relative times and integrity hashes; raw process identifiers, paths and command lines remain private.

The successful rundown retry used clean source `95bb3ef`, with unchanged application runtime. Its first attempt completed the fixed task but stopped the contextual task at 7/11 when foreground focus changed; that failed attempt is retained. The [earlier start/stop-only ETW result](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/process-events/README.md), including its historical 0/33 focus bindings and separate 28/28 canaries, remains unchanged. Neither supplement is pooled into the earlier five-pair timing benchmark.

The current software suite passes **139 tests**. A separate [fresh-environment check](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/reproduction/README.md) installed pinned dependencies and passed the earlier frozen source's **85 tests** plus two 11-step simulation plans. It is a same-machine installation check, not a second-device native validation.

**Video scope:** the linked 3-minute edit shows the labelled 15 October functional recording and earlier 16 October results. The latest rundown evidence and 139-test result are documented above; the video predates them.

## Inspiration

An office worker moves between applications, pauses to read, compares alternatives, corrects mistakes and saves work. For the Synthetic Human Agent challenge, we wanted to make those actions visible and measure how our implementation behaved.

Office Twin started as a supplier comparison across Chrome, Google Sheets and Notepad. Its most useful improvement came from measuring the implementation: a separate observer revealed that our original Notepad opening method left Python parent relationships. We changed the actual desktop action, retained the original observations and evaluated the revised version separately.

## What it does

Office Twin completes an eleven-step procurement workflow on Windows. It visits three local supplier pages in Chrome, types quotations and six formulas into a dedicated Google Sheet, waits for saving, reloads and checks the displayed results. It then writes a recommendation in Notepad, makes a documented correction, saves the report and reopens it for verification.

The recommendation selects the lowest-cost supplier that meets the delivery deadline. Our original functional checks selected Atlas Supplies at SGD 600. Changing the supplier order and Crest Industrial's price changed the correct recommendation to Crest at SGD 525.

The task is driven by validated synthetic JSON data. That input supplies the pages, planned actions and expected outputs; browsing is not autonomous extraction from arbitrary websites. Google Sheets is a browser application, not native Excel. The optional Excel/Word route remains untested. Simulation is available for development and is always distinguished from native desktop execution.

## How we built it

Python, pywinauto, Windows UI Automation and pywin32 control visible applications. The runner checks the target window, spreadsheet URL, worksheet and range before writing, supports cancellation and retains partial evidence on failure. It verifies saved sheet values and the saved text report.

The revised implementation opens both the supplier browser and the Notepad report through visible Explorer shortcut double-clicks. The report shortcut targets the exact run-owned text file. Ambiguous controls stop the run; no direct-file fallback silently changes the opening method.

Fixed and contextual timing policies share the same workflow. Contextual timing introduces bounded variation, correlated pacing and pauses for reading, typing, switching, review and correction. These remain engineering defaults. A participant-confirmed, unassisted human baseline is reported below; it has not yet been used to calibrate the timing policies. The earlier documented practice record is retained separately.

A separate Python observer uses Windows Toolhelp inventory and psutil identity/resource snapshots. It requests 100-millisecond polling and reports actual median and maximum sampling gaps, overruns and its own CPU/memory overhead. Controller resources, controller descendants, Chrome and Notepad are separate scopes. Application cohorts can include unrelated activity; they are not exclusive task costs and must not be added into a purported whole-system total.

The observer does not read the controller's action log, but it is still our instrumentation, not an independent auditor. That historical polling method is distinct from the new Kernel-Process ETW collector, canonical Windows API decoder and lifecycle verifier. The event verifier checks identities, before/after canaries, native-task coverage and final logger counters. Public exports omit personal paths, Sheet IDs, command lines and raw process identifiers.

Runtime execution makes no cloud-model calls. Google connectors provisioned the fixture and provided separate saved-content checks. OpenAI Codex assisted implementation, tests, documentation and local validation; that provenance is disclosed.

## Challenges we ran into

Native execution exposed faults simulation missed: an unsupported accessibility lookup and a Tab action that failed to commit a Sheets formula. We corrected the lookup and used explicit Enter plus cell selection. The six historical Sheets development attempts remain documented: four completed and two failed. Those evolving attempts are not a fixed-version reliability estimate.

The first separate-observer series completed three native trials. It recorded six Notepad process identities with compatible Python parent identities. That evidence prompted the Explorer launch change; we did not rewrite process metadata or erase the earlier observations.

The same series exposed a comparison problem. Its first fixed run opened the Sheet through an extra Explorer branch, while the contextual run reused it. The analyzer rejected that attempted pair. The third trial remained unpaired: **three completed tasks, zero comparable pairs**. When the source changed, the harness stopped before another trial.

The revised series is therefore separate. It uses frozen source `051ec68`, five seed pairs—211, 223, 227, 229 and 233—at normal timing scale 1. Fixed/contextual order reverses in alternate pairs. Source hashes, scenario, seed, capture settings, action sequence and observer coverage must match. Signed-in applications stay warm and shared; background activity is not assumed isolated.

## Accomplishments that we're proud of

The project delivers a connected native workflow with checked outputs, an inspectable implementation and **139 passing automated tests**. Measured process relationships led to a real implementation change, and the comparison checks caught a setup difference that would otherwise have distorted the timing result. The separate ETW supplements add verified canary/controller lifecycles, current application identities and observed parent relationships while retaining failed attempts.

**The revised series completed 10 of 10 native tasks, each with 11/11 steps, yielding five comparable fixed/contextual pairs.** Fixed task duration had a median of **153.13 s** (range 152.24–158.99); contextual duration had a median of **167.08 s** (158.78–169.35). The within-pair contextual-minus-fixed difference had a median of **+11.26 s**, ranging from +5.55 to +17.10 s. These are descriptive results on one warm, shared Windows host, not a population reliability or significance claim.

Each run recorded 586 single-key controller waits. Across runs, their 90th percentiles were **109.50–110.08 ms for fixed** and **161.01–177.73 ms for contextual**. This establishes measured policy variation and its cost; the waits are not OS input-delivery timestamps and do not validate human behavior.

The separate observer collected **17,018 snapshots**. Per-run median gaps were 100.39–100.44 ms; the largest gap was **510.89 ms**, with one overrun. For identities created within capture windows, the per-run counts sum to **6 Chrome identities with compatible Explorer parents, 33 Chrome children with compatible Chrome parents, and 8 Notepad identities with compatible Explorer parents**. Ten preexisting Notepad observations had unresolved parents. These are per-run identity counts, not distinct processes across the whole experiment. No Notepad-to-Python parent was observed in this revised series. Reused warm processes can appear in multiple runs; polling can miss short-lived processes, so these counts do not prove complete launch coverage.

Final read-only Sheet inspection confirmed all six formulas and their saved values, supporting Atlas at SGD 600. That separate formula-source inspection applies to the last saved Sheet; every native trial additionally passed its runtime displayed-value and saved-report checks.

### Measured resource efficiency and test environment

Full-window controller CPU had medians of **19.14 CPU-seconds (fixed)** and **20.61 CPU-seconds (contextual)**. Across the ten runs, sampled controller peak RSS was **72.72–73.09 MiB**, with a requested 250 ms sampling interval. These controller figures exclude the applications and observer. The separate observer itself used **38.36–65.88 CPU-seconds** and **26.45–29.28 MiB** peak sampled RSS per capture. Its diagnostic cost is disclosed separately; Chrome and Notepad cohorts may include unrelated activity and shared pages. The [numeric benchmark](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/benchmark/BENCHMARK.md) retains all scopes and per-run results.

The automated benchmark ran on Windows 11 build 26200, an Intel Core Ultra 7 155U with 14 logical processors and 31.55 GiB RAM, Python 3.14.2, Chrome 155.0.8059.40 and Notepad 11.2607.14.0, at 1920 × 1200. Applications were warm and shared. The human mouse-distance summary below separately assumes 1920 × 1080 coordinates; the two display descriptions are not pooled.

**Earlier practice record, retained separately from the human baseline below.** One participant completed a documented practice with verified saved outputs. The participant reported operating the applications personally and used Start/Finish buttons. Post-run checks confirmed 18 literal Sheet cells, six formula sources, six calculated results and a correct saved recommendation for Atlas at SGD 600. The recorded **734.526 seconds** includes chat guidance and waiting. Exact formulas and a report example were supplied during the attempt; independent report authorship and entry method were not established. This is one guided completion, with no input-timing or application-resource recording, so it is not used for an agent-versus-human speed ratio. [Practice evidence](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/manual-practice/README.md) and the [verification record](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/manual-practice/result.json) preserve that distinction.

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

The [revised narrated video](https://youtu.be/oTTT0ECN25U) preserves the same continuous 162.13-second **15 October functional recording at 1×** within a 180.13-second edit. Updated narration and cards report the **16 October evidence—ten native completions, five matched pairs, 85 passing tests and the participant-confirmed 720-second unassisted human baseline—separately from the footage**. The historical recording is labelled throughout; it does not show the revised launch mechanism or constitute a new benchmark trial. That edit predates the ETW verification and current 139-test suite, which are documented in the linked evidence. The four judging criteria remain explicit in the evidence table and guide.

## What we learned

A correct artifact, a successful desktop action and a convincing process trace require different evidence. Separate observation made an implementation difference visible.

Timing variation is similarly insufficient by itself. Our automated comparison measures policy behavior and its observed cost. The earlier practice demonstrates correct saved work, and the participant-confirmed unassisted baseline adds reported human measurements. Neither establishes human indistinguishability or an official judging score. Missing parents remain unresolved, and sampled CPU or memory must keep its measurement scope attached.

## What's next

Next are additional consented, unassisted manual reference runs with retained input-event and resource traces, explicit timestamp and process-cohort definitions, and calibration against those observations. The new rundown capture resolves current application identities; future tracing begun before application launch could supply their otherwise unavailable original-parent history. Native reproduction on another Windows setup would test robustness beyond the current host; the new fresh-environment check uses this same machine.

Evidence: [latest application identity and parent verification](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/process-rundown/README.md), [source](https://github.com/ajayasai/office-twin-ntu-st-2026), [verified process events](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/process-events/README.md), [fresh-install check](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/reproduction/README.md), [revised benchmark](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/benchmark/BENCHMARK.md), [sampled parent evidence](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/benchmark/process-parent-evidence.md), [telemetry methods](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/TELEMETRY.md), and [retained initial series](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/benchmark-initial/README.md).
