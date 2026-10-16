# Observed validation — 16 October 2026 update

## Current rundown identity validation

The [rundown supplement](process-rundown/README.md) resolves **32/32 focus observations** across **three current application identities** and verifies **28/28 known process lifecycles**. Both native tasks completed **11/11 steps**. Its 354.908-second trace contains 1,300 provider records: 185 starts, 185 stops and 930 rundown records (including two Idle PID 0 state records excluded from process identities); final reported loss counters were **0 / 0 / 0**. The seed-311 pair uses clean source `95bb3efc830a2d811b69cc68c9483ae9b0353fec`, normal timing and warm shared applications kept open as requested.

Preexisting identities must match exact Toolhelp/GetProcessTimes snapshots bracketing native work and rundown records before and after their focus observations. Newly created application identities use their actual start and applicable later snapshot or observed stop. These checks verify current lifetime identity, not a fabricated historical start. The warm main applications’ original parents had exited before capture and remain unresolved. All 16 application start records inside the two native trial windows resolve to compatible parent lifetimes: 10 Chrome → Chrome, two Explorer → Chrome and four Explorer → Notepad. These are 12 Chrome and four Notepad starts; they are not a claim of 16 complete lifecycles inside each trial window or exclusive task causation.

**139 automated tests passed in 10.389 seconds** before this clean capture source was frozen. Test provenance and private artifact hashes are retained in the supplement. These checks are separate from the earlier 120-test event result, historical 85-test benchmark/installation suite and video claims.

The first warm rundown attempt is retained as failed: fixed completed 11/11; contextual stopped at 7/11 during `sheet_save` when the foreground-focus guard detected a change. It recorded 14/14 before-task canaries and no after-task canaries. The fresh retry does not overwrite that attempt or establish an all-attempt 100% success rate. Both remain separate from the ten-run timing/resource benchmark.

## Earlier start/stop-only event retry and installation checks

**The earlier start/stop-only ETW retry completed both native tasks at 11/11 steps and verified all 28 known canary lifecycles plus both task-controller lifecycles.** The fixed/contextual pair used seed 307, normal timing scale and clean source `09e4b83824b8b0bec4348be0dbae2bcdef1f62dc`. Its 393.982-second capture contains 344 Kernel-Process records: 172 starts and 172 stops, with no rundown. All three final ETW loss counters were zero. Twenty-four canaries lived less than 100 ms; observed canary lifetime minimum/median/maximum was 54.2124/59.99755/400.5494 ms. The [event record](process-events/README.md) supplies the public export, hashes, native results and limits.

Within the native task windows, the nonexclusive application-name cohort has **14 Chrome and four Notepad start records**, plus **three Chrome → Chrome relationships with resolved parent identities**. Eighteen stop records were also observed, but only 16 starts pair to stops inside their same individual trial window; equal event totals are not 18 complete per-trial lifecycles. Fifteen further comparisons match parent PIDs: three Chrome/Explorer, four Notepad/Explorer and eight Chrome/warm-Chrome. These are parent-PID-only comparisons, not resolved parent lifetimes. All 33 focus observations refer to three preexisting main-application identities that emitted no start/stop/rundown records; their lifecycle bindings and full ancestry remain unresolved.

The result verifies the stated known canary/controller coverage and completed saved-output checks. Zero reported ETW loss is not universal completeness. The first ETW attempt failed after the computer entered Modern Standby; its 14 before-native canaries and partial native attempt remain documented. The retry's capture conditions differ from the ten-run benchmark below, so no performance statistics or all-attempt reliability rate are pooled across them.

**119 automated tests passed before that retry; its final evidence suite passed 120 tests**, including the added application-cohort export check. Tests cover event parsing, evidence integrity and workload cancellation; they are software checks rather than native event observations. A separate [fresh-environment reproduction](reproduction/README.md) installed the five pinned dependencies directly from PyPI and passed the earlier frozen source `5d3e0100f652f424fed5653ac78b2ffdae0256e5`'s **85 tests** plus default/alternate 11-step simulation plans. Those plans performed no desktop input and have `native_verified=false`. This installation check used the same physical Windows machine and base Python installation.

## Earlier ten-run controlled benchmark

**The revised series completed 10 of 10 native tasks, each with 11/11 steps, yielding five comparable fixed/contextual pairs.** Fixed task duration had a median of **153.13 s** (range 152.24–158.99); contextual duration had a median of **167.08 s** (158.78–169.35). The within-pair contextual-minus-fixed difference had a median of **+11.26 s**, ranging from +5.55 to +17.10 s. These are descriptive results on one warm, shared Windows host, not a population reliability or significance claim.

Each run recorded 586 single-key controller waits. Across runs, their 90th percentiles were **109.50–110.08 ms for fixed** and **161.01–177.73 ms for contextual**. This establishes measured policy variation and its cost; the waits are not OS input-delivery timestamps and do not validate human behavior.

The separate observer collected **17,018 snapshots**. Per-run median gaps were 100.39–100.44 ms; the largest gap was **510.89 ms**, with one overrun. It observed eight per-run Notepad identities created within capture windows with compatible Explorer parents, and ten preexisting Notepad observations with unresolved parents. No Notepad-to-Python parent was observed in this revised series. Reused warm processes can appear in multiple runs; polling can miss short-lived processes, so these counts do not prove complete launch coverage.

Final read-only Sheet inspection confirmed all six formulas and their saved values, supporting Atlas at SGD 600. That separate formula-source inspection applies to the last saved Sheet; every native trial additionally passed its runtime displayed-value and saved-report checks.

Runtime commit `051ec6871425ddaba9faeffed297a2168620e58c` remained fixed across the ten revised attempts. Normal scale 1, seeds 211/223/227/229/233, alternating policy order, default scenario, no video recording. Every attempt is retained; no revised attempt was excluded. The [full benchmark](benchmark/README.md) records hashes, scoped resource measurements, actual sampling gaps and observer overhead. The [figure](media/benchmark.png) plots all five comparable pairs.

**85 automated tests passed** before the revised native series. They cover scenario decisions, bounded timing, cancellation/failure evidence, window targeting, real Explorer report opening, observer PID identity/races, scoped resources, benchmark validation and sanitized exports. Tests and automated task runs are not manual observations. The ten-run automated benchmark contains no human reference data; the unassisted baseline and earlier guided practice are reported separately below.

The [initial observer series](benchmark-initial/README.md) completed three native tasks on the previous runtime but yielded zero comparable pairs. Its attempted pair differed in Sheet-opening actions; the third trial was unpaired. Six sampled Notepad identities had compatible Python parents. That prompted an actual Explorer shortcut-opening change. The harness stopped before its next trial when source changed. Initial, revised and 15 October runs remain separate.

During the ten-run series, Sysmon was unavailable; Security-log access and WMI process-start collection were denied to the unelevated collector. The separate Toolhelp/psutil observer is our read-only sampling instrument, not an independent auditor or a process-start event stream. The later temporary ETW collector above supplies a separate event-based result without changing those historical observations. No logging/security settings or process-parent metadata were altered. Chrome/Notepad cohorts are shared and nonexclusive. Observer CPU and RSS are reported separately.

The existing [video](https://youtu.be/0OpIetkSomM) documents the historical functional run below. It does not show the revised launch mechanism or provide video evidence for the ten new trials. See [submission status](../SUBMISSION.md) for the source archive and Devpost update.

## Unassisted human baseline — documentation update, 16 October 2026

The participant confirms an actual **720-second (12-minute)** task performed entirely by a human, without guidance. Supplied aggregate measurements include **42 WPM**, **740 key-down events**, mean/median/p90 inter-key intervals of **200/170/350 ms**, **14 corrected input-error episodes**, **112 mouse clicks**, and Chrome/Notepad CPU and RSS. Measured process ancestry is **Explorer → Chrome; Chrome → Chrome child processes; Explorer → Notepad**. The [complete baseline page](human-baseline/README.md) and [aggregate JSON](human-baseline/aggregate.json) preserve all metrics and arithmetic checks.

This record is separate from the 734.526-second guided practice below. The participant supplied the measurements and confirmed their provenance; raw input, resource and process-event traces were not supplied, so independent verification is not claimed. The measurement date, run ID, actual hardware and capture definitions are unspecified. The documentation date is not assigned as the measurement date. The phase total, key-category total, WPM and deletion share reconcile, but those checks do not establish a matched human-versus-agent comparison or output correctness.

## Earlier guided manual practice — 16 October 2026

One participant, **P01**, recorded **one guided manual completion in 734.526 seconds** (12 minutes 14.5 seconds). A separate post-run Google Sheets connector read verified six headers, twelve supplier inputs, all six formula sources and their calculated results. A separate read of the saved text report confirmed the task requirements, supplier facts and recommendation of Atlas at SGD 600 as the lowest eligible supplier. The [sanitized practice evidence](manual-practice/README.md) preserves the result and saved report.

The participant had prior exposure to the task and received step-by-step chat guidance, exact Sheet headers/formulas and a sample report during the attempt. The saved report matches the supplied sample after whitespace normalization; report authorship and typing versus pasting were not observed. The participant reported operating the applications manually, and the assistant did not inject task input during the attempt. Post-run checks verify saved-output correctness, not human participation or the exact action sequence.

Elapsed time runs from the participant's browser **Start** to **Finish**, including chat instructions, replies, waiting, application switching and save/reopen steps. The collector recorded duration and its own overhead, with no task keystrokes, mouse events, pause distributions, application-resource samples or process events. At that checkpoint, no unassisted baseline had been supplied; the separate aggregate baseline above is the later evidence update. This guided completion is not comparable to the automated task interval, supports no agent-versus-human speed ratio, and does not validate human-like timing.

---

# Historical functional validation — 15 October 2026

The three final 15 October native runs each completed all **11 steps**, including a saved Google Sheets comparison and a reopened, correct Notepad recommendation. The third run changed supplier order and price; the recommendation changed from Atlas at $600 to Crest at $525. These are small functional checks on one machine, not a reliability estimate or a human-similarity benchmark.

The workflow used **Chrome → Google Sheets → Notepad** on Windows with Python 3.14. Runtime actions used desktop input and UI Automation. Google connectors were used for fixture setup and independent readback, not to write the sheet during a native run. The task uses validated synthetic scenario data; it does not autonomously extract arbitrary websites.

Observed setup: Windows 11 Home Single Language, build 26200; Python 3.14.2; Chrome 155.0.8059.40; Notepad 11.2607.14.0; Intel Core Ultra 7 155U (14 logical processors); 31.55 GiB OS-reported RAM; primary display 1920×1200. Applications were already installed and Chrome was signed in to the dedicated test Sheet. This was not a clean-machine installation test.

## Historical normal-speed runs

| Run ID | Condition | Result | Wall time | Controller CPU | Sampled controller peak RSS |
| --- | --- | --- | ---: | ---: | ---: |
| `20261015T091539Z-3d7a2a48` | Default scenario, fixed timing, seed 42, scale 1 | 11/11; Atlas $600 | 136.82 s | 14.86 CPU-s | 79.79 MiB |
| `20261015T091815Z-588afee5` | Default scenario, contextual timing, seed 73, scale 1; screen recording active | 11/11; Atlas $600 | 158.84 s | 18.08 CPU-s | 80.30 MiB |
| `20261015T092135Z-e43abfcb` | Alternate scenario, contextual timing, seed 101, scale 1 | 11/11; Crest $525 | 141.81 s | 15.78 CPU-s | 81.03 MiB |

CPU is measured for the Python controller only, including monitoring overhead. RSS is sampled at a requested 0.25-second interval and may miss transient peaks. Chrome, Sheets and Notepad resource use is not included in those controller figures. Wall time includes setup, countdown, cleanup and monitoring. These runs differ in recording, scenario and seed; their durations do not establish that one timing policy is faster or more efficient.

## Earlier attempts and fixes

| Run ID | Scope | Outcome |
| --- | --- | --- |
| `20261015T085621Z-e5a89455` | Earlier Chrome/Notepad workflow, 7 steps | 7/7 passed; different scope from the Sheets workflow. |
| `20261015T090304Z-558389e7` | Sheets workflow, scale 1 | Failed after 4/11 steps: unsupported UI Automation lookup argument. Corrected the lookup. |
| `20261015T090739Z-a30f8a8b` | Sheets workflow, scale 0.15 | Failed after 7/11 steps: a tab key did not commit the formula as intended. Changed to explicit Enter and cell selection. |
| `20261015T091003Z-1a9e2fd5` | Sheets workflow, scale 0.15 | 11/11 passed; independent readback confirmed all six formulas and calculated results. Accelerated functional test only. |

Across the six documented Sheets development attempts, four passed and two failed. The latest three normal-speed attempts passed. Code and instrumentation evolved between attempts; pooling them as a fixed-version reliability benchmark would be misleading. Failures and their local evidence have been retained.

## Evidence available locally

- `runs/<run-id>/summary.json`, `events.jsonl`, resource observations and `report.html` describe each attempt. The recorded run is under `runs/demo/<run-id>/`.
- `runs/comparison.html` compares all seven native attempts with failures, task scopes, speed scales and capture differences preserved.
- `runs/20261015T091003Z-1a9e2fd5/sheets-independent-verification.json` records the independent default-scenario formula check. `runs/20261015T092135Z-e43abfcb/sheets-independent-verification.json` confirms all six alternate-scenario formulas, results of 525/600/575 and eligibility of YES/YES/NO. Separate connector reads verify saved content, not every UI action.
- `runs/demo/office-twin-desktop-20261015-171812.mp4` is a continuous **162.13-second**, 1920×1200, 15 fps, real-time (1×) recording. It has identifying banners and no microphone audio. Capture starts before and ends after the workflow, so video length differs from run duration.
- `dist/office-twin-submission.mp4` is the completed **180.133333-second** narrated edit, with an eight-second introduction, the full continuous 162.133-second source recording at 1×, and a ten-second closing card. It is 1920×1200 with H.264 video and AAC audio. Microsoft Zira Desktop supplies synthetic narration; captions identify evidence limits and the separately validated alternate scenario. The edit does not add another native test run.
- `docs/validation-results.json` contains selected measurements copied from the run summaries without local account paths or spreadsheet identifiers.

Raw local evidence, videos, credentials, personal settings and the virtual environment are excluded from the source archive. The [source repository is public](https://github.com/ajayasai/office-twin-ntu-st-2026). The narrated [YouTube video](https://youtu.be/0OpIetkSomM) is published as **Unlisted**, verified in YouTube Studio; copyright and community checks passed. Viewer-facing playback was verified on the YouTube watch page.

Submission was confirmed in Devpost on **16 October 2026 (SGT)** by the "Project submitted!" message and the submitted competition status. The joined team is Ajay Asaithambi (`@ajay007`, leader), Siddharth Paliwal (`@siddhartha-paliwal21`), and Sourabh Sooraj (`@sourabhsooraj97`). The uploaded source archive corresponds to commit [`5dd7181317838d9cfa52ba023cf02037539ac5ff`](https://github.com/ajayasai/office-twin-ntu-st-2026/commit/5dd7181317838d9cfa52ba023cf02037539ac5ff). That original package is retained locally; the 16 October evidence revision is documented above and replacement-upload status is tracked in SUBMISSION.md.

## Automated verification and limits

**41 unit tests passed** in the 15 October suite, including five checks for the manual reference collector. The earlier suite contained 36 tests. They cover scenario validation and changed decisions, timing bounds and reproducibility, CPU delta reporting, failure/cancellation reporting, HTML escaping, comparison scope, and unavailable process tracing. They do not replace native end-to-end runs.

At the 15 October checkpoint, the [manual reference collector](MANUAL_BASELINE.md) was implemented and tested. It records explicit participant start/stop, optional phase markers, and resource snapshots for selected PIDs; it records no task keystrokes, pointer activity or screen content. Collector outcomes are participant-reported until separately checked. No manual run had been collected at that checkpoint; the later guided practice, separate output verification and participant-supplied unassisted aggregates are documented above.

The passive WMI process-start collector returned **Access denied** on this host. No independent Sysmon export was collected. Controller action logs and process snapshots must not be presented as independent Sysmon evidence. Security and logging settings were not changed.

At the 15 October checkpoint, no unassisted human baseline had been supplied. Current evidence now includes the unassisted aggregate record above, while retained human input-event traces remain unavailable and the timing parameters remain engineering defaults. No human-indistinguishability, general desktop autonomy, arbitrary website extraction or official benchmark score is claimed. The optional native Excel/Word workflow remains untested because Office activation was unavailable. Desktop tests require an idle, unlocked session and the documented app state; window guards do not prove every focused child control is correct.

The next evaluation step is additional unassisted manual references with retained traces and matched boundaries under [EVALUATION.md](EVALUATION.md), followed by reproduction on the intended demonstration machine and confirmation of the private organizer brief.
