# Plan to compete

Build one reliable, measurable office workflow and make the evidence easy for judges to inspect. The primary workflow is **Chrome local supplier brief → Google Sheets comparison → Notepad recommendation**. A clear business task connects the application activity, timing decisions, and final artifacts. Excel/Word remains an optional, untested path for a licensed Office machine.

This is a strategy for improving the entry, not a prediction or guarantee of winning. The controlled evaluation completed **ten native tasks, each 11/11 steps, and five comparable fixed/contextual pairs**. The current suite passes **139 automated tests**. The earlier start/stop-only ETW pair verifies **28/28 known process lifecycles and both task-controller lifecycles**, with zero reported final ETW loss. The [rundown supplement](docs/process-rundown/README.md) adds **32/32 verified focus bindings** across **three current application identities**; both native tasks completed **11/11 steps**. Earlier functional validation also changed the supplier order and Crest's price to SGD 105 per unit, correctly changing the recommendation to Crest at SGD 525. The current scenario uses controlled local pages, not arbitrary websites.

The rundown capture also resolves parent lifetimes for all 16 application start records in the native trial windows: 10 Chrome → Chrome, two Explorer → Chrome and four Explorer → Notepad relationships. This strengthens the application evidence without assigning historical parent identities that are absent from the trace.

A 162.13-second video of the 15 October functional run is preserved at 1× playback; it predates the revised observer, launch method and ETW capture. Source is in the [GitHub repository](https://github.com/ajayasai/office-twin-ntu-st-2026). Current evidence includes a [participant-confirmed unassisted human baseline](docs/human-baseline/README.md), measured at **720 seconds**, separate Toolhelp/psutil observation of the ten-run series, and [verified ETW canary/controller evidence](docs/process-events/README.md). The first ETW attempt failed after the computer entered Modern Standby and remains documented. The later warm rundown attempt stopped during contextual Sheet saving when its foreground-focus guard detected a change; the failed attempt remains alongside its retry. The rundown supplement resolves current application identities, while original parents that exited before tracing remain unavailable.

A [fresh virtual-environment check](docs/reproduction/README.md) installed pinned dependencies from PyPI and reproduced the older frozen source's 85 tests and two simulation plans. Highest-value remaining observations are raw human traces with matching capture definitions and native reproduction on another machine. Complete historical ancestry cannot be recovered from a current-state rundown after original parents have exited. The human baseline's measured aggregates remain unchanged. The historical Sysmon/WMI limitations and unavailable private organizer brief are retained in [validation](docs/VALIDATION.md).

## Match effort to the rubric

The [official rules](https://ntu-x-st-engineering-hackathon.devpost.com/rules) assign the following weights. The evidence below is our proposed evaluation approach, not an organizer-supplied scoring formula.

| Criterion | Weight | Implementation focus | Evidence to prepare |
| --- | ---: | --- | --- |
| Process telemetry authenticity | 30% | Perform the task in real applications through the ordinary desktop; inspect what Windows actually records. | A manual-versus-agent comparison using independent telemetry under the same capture configuration. Include actual process relationships and explain differences. |
| Human entropy and timing | 30% | Use pauses related to reading, typing, correction, and task transitions; preserve variation between runs. | Timing distributions for manual, fixed-delay, and contextual-delay runs; distinguish deliberate pauses from application wait time. |
| Complexity of action | 20% | Complete a connected task across local Chrome pages, Google Sheets, and Notepad with correct saved outputs. | A real sheet with correct formulas/results and a saved text recommendation justified by them; repeat-run success rate. |
| Resource efficiency | 20% | Keep control logic lightweight and avoid unnecessary polling or repeated expensive model calls. | Task duration plus CPU/RAM with measurement interval, machine specifications, and process scope disclosed. |

The overview labels efficiency “Primary” and complexity “Secondary” without explaining the distinction. Until organizers clarify, preserve the published weights and prioritize reliable evidence for the two 30% categories.

## Scope

The minimum credible demonstration has one local synthetic supplier dataset, a reproducible initial desktop state, one dedicated comparison Sheet, one saved text recommendation, and a separate evidence folder. Add features only after the complete task runs reliably. Confirm how organizers treat web spreadsheets: their process activity is Chrome activity, not Excel activity.

The control panel, stop behavior, result reporting, scenario changes, and native recording are implemented. Prioritize evidence quality, reproducibility on the judging setup, and concise explanation over extra personas, many unrelated tasks, or elaborate dashboards.

Keep independent telemetry intact. The goal is to generate genuine application activity and describe its limits, not to fabricate logs, conceal the controller, or alter process lineage. A visible difference from a human trace is a result to explain.

## Schedule — Singapore time

The official deadline is **Sunday 18 October at 00:00**, which means Saturday night is the last submission opportunity. Our target is **Saturday 17 October at 21:00**, leaving three hours for upload and access problems. [Official schedule](https://ntu-x-st-engineering-hackathon.devpost.com/details/dates)

| Date | Focus | Exit condition |
| --- | --- | --- |
| Thu 15 Oct | Native implementation and recording completed; confirm the 3–5-person team and obtain the private brief. | Three normal-speed runs passed; retain the raw evidence and record unresolved organizer requirements. |
| Fri 16 Oct, first half | Reproduce the workflow on the judging setup and resolve authorized telemetry availability. | The documented setup works and telemetry coverage is reported accurately, including any unavailable sources. |
| Fri 16 Oct, second half | Collect consented manual baselines, fixed-delay runs, and contextual-delay runs. | Comparable raw evidence, documented failures, and initial metrics; freeze feature scope. |
| Sat 17 Oct, morning | Reproduce on a clean setup, fix blockers, and validate calculations and recommendation text. | Installation and end-to-end instructions match observed behavior. |
| Sat 17 Oct, afternoon | Review the recorded demo, finish documentation, and prepare the Devpost entry. | All links, outputs, limitations, and provenance are ready for review. |
| Sat 17 Oct, by 21:00 | Submit, reopen the submission, and check access. | The actual submitted entry contains accessible source, documentation, and video. |

If native automation remains blocked on Friday, reduce task breadth and show only the portions that run. A labelled simulation can explain the architecture, but it cannot substitute for claims of native office activity. Never use a polished video to imply unsupported behavior.

## Human team responsibilities

The public event requires **3–5 NTU students**. With you plus two recruited teammates, a three-person split is:

| Person | Responsibility | Concrete handoff |
| --- | --- | --- |
| You | Integration, scope decisions, final review and submission. | Verified repository, coherent story, correct final entry. |
| Teammate 1 | Native Windows/Chrome/Sheets validation and operational troubleshooting. | Machine/configuration notes, completed artifacts, recorded failures. |
| Teammate 2 | Manual baseline coordination, independent evidence, and demo editing. | Consent-based manual traces, comparison figures, accessible video. |

AI can assist coding, documentation, and analysis. Participating students must inspect the work, run the native application tests, provide truthful human baselines, make the submission, and be able to explain the design and measured limitations.

## Resolve organizer-specific unknowns

Use the private briefing first. The user/team should ask the organizers about permitted AI assistance and pre-existing code; acceptance of browser-based Google Sheets and plain-text reports; evaluation machine/application versions; available telemetry and benchmark tasks; resource limits and Internet/API use; source access requirements; and video duration. No outreach has been sent by this project.

The [public overview](https://ntu-x-st-engineering-hackathon.devpost.com/) asks for complete GitHub source, documentation, and a video. The public [discussion page](https://ntu-x-st-engineering-hackathon.devpost.com/forum_topics) had no clarifications when reviewed on 15 October 2026. Any later organizer instruction takes precedence over assumptions in this plan.
