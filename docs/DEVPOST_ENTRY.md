# Office Twin

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

Fixed and contextual timing policies share the same workflow. Contextual timing introduces bounded variation, correlated pacing and pauses for reading, typing, switching, review and correction. These remain engineering defaults: **unassisted human reference n = 0**. The guided manual completion described below adds functional evidence, not human-timing calibration.

A separate Python observer uses Windows Toolhelp inventory and psutil identity/resource snapshots. It requests 100-millisecond polling and reports actual median and maximum sampling gaps, overruns and its own CPU/memory overhead. Controller resources, controller descendants, Chrome and Notepad are separate scopes. Application cohorts can include unrelated activity; they are not exclusive task costs and must not be added into a purported whole-system total.

The observer does not read the controller's action log, but it is still our instrumentation, not an independent auditor. Polling is not Sysmon, ETW or a complete process-start trace. Public exports omit personal paths, Sheet IDs, command lines and raw process identifiers.

Runtime execution makes no cloud-model calls. Google connectors provisioned the fixture and provided separate saved-content checks. OpenAI Codex assisted implementation, tests, documentation and local validation; that provenance is disclosed.

## Challenges we ran into

Native execution exposed faults simulation missed: an unsupported accessibility lookup and a Tab action that failed to commit a Sheets formula. We corrected the lookup and used explicit Enter plus cell selection. The six historical Sheets development attempts remain documented: four completed and two failed. Those evolving attempts are not a fixed-version reliability estimate.

The first separate-observer series completed three native trials. It recorded six Notepad process identities with compatible Python parent identities. That evidence prompted the Explorer launch change; we did not rewrite process metadata or erase the earlier observations.

The same series exposed a comparison problem. Its first fixed run opened the Sheet through an extra Explorer branch, while the contextual run reused it. The analyzer rejected that attempted pair. The third trial remained unpaired: **three completed tasks, zero comparable pairs**. When the source changed, the harness stopped before another trial.

The revised series is therefore separate. It uses frozen source `051ec68`, five seed pairs—211, 223, 227, 229 and 233—at normal timing scale 1. Fixed/contextual order reverses in alternate pairs. Source hashes, scenario, seed, capture settings, action sequence and observer coverage must match. Signed-in applications stay warm and shared; background activity is not assumed isolated.

## Accomplishments that we're proud of

The project delivers a connected native workflow with checked outputs, an inspectable implementation and **85 passing automated tests**. Measured process relationships led to a real implementation change, and the comparison checks caught a setup difference that would otherwise have distorted the timing result.

**The revised series completed 10 of 10 native tasks, each with 11/11 steps, yielding five comparable fixed/contextual pairs.** Fixed task duration had a median of **153.13 s** (range 152.24–158.99); contextual duration had a median of **167.08 s** (158.78–169.35). The within-pair contextual-minus-fixed difference had a median of **+11.26 s**, ranging from +5.55 to +17.10 s. These are descriptive results on one warm, shared Windows host, not a population reliability or significance claim.

Each run recorded 586 single-key controller waits. Across runs, their 90th percentiles were **109.50–110.08 ms for fixed** and **161.01–177.73 ms for contextual**. This establishes measured policy variation and its cost; the waits are not OS input-delivery timestamps and do not validate human behavior.

The separate observer collected **17,018 snapshots**. Per-run median gaps were 100.39–100.44 ms; the largest gap was **510.89 ms**, with one overrun. It observed eight per-run Notepad identities created within capture windows with compatible Explorer parents, and ten preexisting Notepad observations with unresolved parents. No Notepad-to-Python parent was observed in this revised series. Reused warm processes can appear in multiple runs; polling can miss short-lived processes, so these counts do not prove complete launch coverage.

Final read-only Sheet inspection confirmed all six formulas and their saved values, supporting Atlas at SGD 600. That separate formula-source inspection applies to the last saved Sheet; every native trial additionally passed its runtime displayed-value and saved-report checks.

**One participant also completed a guided manual practice with verified saved outputs.** The participant reported operating the applications personally and used Start/Finish buttons. Post-run checks confirmed 18 literal Sheet cells, six formula sources, six calculated results and a correct saved recommendation for Atlas at SGD 600. The recorded **734.526 seconds** includes chat guidance and waiting. Exact formulas and a report example were supplied during the attempt; independent report authorship and entry method were not established. This is one guided completion, with no input-timing or application-resource recording, so it is not used for an agent-versus-human speed ratio. [Practice evidence](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/manual-practice/README.md) and the [verification record](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/manual-practice/result.json) preserve that distinction.

Automated task duration covers first step start through final step completion; full controller wall time also includes preparation, countdown, verification and cleanup. Controller waits are not OS input timestamps.

The published video shows the initial functional run recorded on 15 October, preserved continuously at 1× within the narrated edit. It does not show the revised launch mechanism or constitute a new benchmark trial.

## What we learned

A correct artifact, a successful desktop action and a convincing process trace require different evidence. Separate observation made an implementation difference visible.

Timing variation is similarly insufficient by itself. Our automated comparison measures policy behavior and its observed cost. The guided manual practice demonstrates correct saved work, but does not establish human entropy, indistinguishability or an official judging score. Missing parents remain unresolved, and sampled CPU or memory must keep its measurement scope attached.

## What's next

Next are consented, unassisted manual reference runs with suitable input-timing capture, calibration against those observations and independent event telemetry on an appropriately configured evaluation machine. Reproduction on another Windows setup would test robustness beyond the current host.

Evidence: [source](https://github.com/ajayasai/office-twin-ntu-st-2026), [revised benchmark](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/benchmark/BENCHMARK.md), [sampled parent evidence](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/benchmark/process-parent-evidence.md), [telemetry methods](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/TELEMETRY.md), and [retained initial series](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/benchmark-initial/README.md).
