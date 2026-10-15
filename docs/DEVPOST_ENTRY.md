# Office Twin

## Project name

Office Twin

## One-line description

A synthetic office worker that completes a supplier comparison through Chrome, Google Sheets and Notepad, with inspectable outputs, contextual timing and measured controller resources.

## Inspiration

Everyday office work connects several small decisions: inspect information, compare options, calculate a result and explain a recommendation. Those connections make a useful test of synthetic human activity. A convincing demonstration needs a concrete task, correct outputs and evidence of what the system actually did.

For the NTU × ST Engineering challenge, we chose a procurement exercise that makes the four evaluation areas visible: application activity, timing, action complexity and resource use. Office Twin performs that exercise in ordinary desktop applications and keeps a record that can be checked after the run.

## What it does

Office Twin completes an eleven-step workflow on Windows. It visits three local supplier pages in Chrome, enters quotations and six formulas into a dedicated Google Sheet, waits for the save indicator, reloads the sheet and checks the displayed results. It then types a recommendation in Notepad, makes a documented correction, saves the file and reopens it. The saved text is checked separately.

The task selects the lowest-cost supplier that meets the delivery deadline. In the default scenario, that is Atlas Supplies at SGD 600. Changing the supplier order and reducing Crest Industrial's price changes the recommendation to Crest at SGD 525. Both the spreadsheet and the written recommendation follow the supplied scenario.

The scenario is a validated JSON input. The local pages, planned actions and expected results are derived from it; the system does not claim to extract or understand arbitrary websites. A simulation mode exercises the plan without desktop input, while the native mode runs the documented Chrome → Google Sheets → Notepad workflow.

## How we built it

The implementation uses Python, pywinauto, Windows UI Automation and pywin32 for visible desktop interaction. It checks the target window, spreadsheet URL and worksheet before writing, and supports cancellation through Escape or the control panel. Each attempt gets its own output directory, including partial evidence when a run fails.

A seeded timing policy offers a fixed baseline and contextual delays for typing, reading, thinking, switching, reviewing and correction. The contextual model uses bounded variation and correlated pacing. These parameters are engineering defaults; they have not been calibrated against human recordings.

The evidence pipeline produces JSONL action records and self-contained HTML reports. It separates requested delays from measured waits and reports controller CPU time and sampled memory. A passive WMI collector reports process-start coverage when available. Execution makes no cloud-model calls. Google connectors were used outside the native runner to provision the test Sheet and independently inspect saved content.

OpenAI Codex assisted implementation, tests, documentation and execution of local validation. The repository records that provenance alongside the results and limitations; automated validation does not imply student review or organizer approval.

## Challenges we ran into

Real desktop runs exposed two faults that simulation could not: an unsupported accessibility lookup argument and a Sheets Tab action that did not commit a formula as intended. We corrected the lookup and changed formula entry to explicit Enter followed by explicit cell selection. The executor also binds to the intended worksheet and checks the saved grid after reloading.

We kept failed attempts in the evidence history. Across six documented Sheets development attempts, four completed and two failed. The latest three normal-scale runs completed all eleven steps, but the code and setup evolved during development; these observations are not a fixed-version reliability estimate.

Independent process-start collection was also limited by the host: WMI returned Access denied. The report records that result, and no security or logging settings were changed. No independent Sysmon export or human reference run has been collected.

## Accomplishments that we're proud of

The project completes a connected task in real applications and checks the resulting sheet values and saved recommendation. Its latest three native runs passed all eleven steps, and the automated suite passed 41 tests covering scenario decisions, timing, evidence handling, cancellation and reporting.

| Observed run | Result | Controller wall time | Controller CPU | Sampled controller peak RSS |
| --- | --- | ---: | ---: | ---: |
| Default scenario, fixed timing | 11/11; Atlas SGD 600 | 136.82 s | 14.86 CPU-s | 79.79 MiB |
| Default scenario, contextual timing; recording active | 11/11; Atlas SGD 600 | 158.84 s | 18.08 CPU-s | 80.30 MiB |
| Alternate scenario, contextual timing | 11/11; Crest SGD 525 | 141.81 s | 15.78 CPU-s | 81.03 MiB |

All three used timing scale 1. The alternate scenario's six formulas and computed results were independently checked through a read-only connector query. A continuous 162.13-second recording preserves the default contextual run at 1× playback.

The resource figures cover the Python controller, including monitoring, and exclude Chrome and Notepad. Memory was sampled at a requested 0.25-second interval. Wall time includes setup, countdown and cleanup. The runs differ in scenario, seed and recording overhead, so these figures do not establish that one timing policy is more efficient.

## What we learned

Task completion, saved-content correctness and process authenticity need different evidence. A successful keypress call does not prove that the intended cell changed; a correct spreadsheet does not prove a human-like process trace. Reloading and checking the saved output caught a real failure, while explicit capture status kept unavailable telemetry from becoming a misleading success claim.

Timing also needs a reference. Variation can be reproducible and context-dependent without being validated as human behavior. The next evaluation should compare equivalent manual, fixed-timing and contextual-timing runs under the same capture conditions.

## What's next for Office Twin

The priorities are consented manual reference runs, independent process telemetry on an authorized evaluation machine, and reproduction from the documented starting state. Those measurements would let us assess timing similarity and process differences instead of assuming them.

The demonstrated scope is three synthetic suppliers, English Chrome and Google Sheets, and a Notepad report on one Windows setup. The optional Excel/Word path remains untested. Window guards do not cover every possible in-page dialog or focused control, and the workflow requires an unlocked, idle desktop. We make no claim of general desktop autonomy, human indistinguishability or an official benchmark score.

## Built with

Python; Windows UI Automation; pywinauto; pywin32; psutil; Tkinter; Google Chrome; Google Sheets; Windows Notepad; HTML; CSS; SVG; FFmpeg.

Development assistance: OpenAI Codex. Google connectors supported fixture setup and separate read-only verification; they are not runtime shortcuts for entering task data.

## Project links and supporting evidence

- Source: [Office Twin on GitHub](https://github.com/ajayasai/office-twin-ntu-st-2026).
- [Observed validation and complete development history](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/VALIDATION.md).
- [Architecture and provenance](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/ARCHITECTURE.md).
- [Reproduction and Google Sheets setup](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/GOOGLE_SHEETS.md).
- [Proposed paired evaluation protocol](https://github.com/ajayasai/office-twin-ntu-st-2026/blob/main/docs/EVALUATION.md).

## Submission handoff — exclude from the project description

Use the final reviewed video URL in Devpost's video field and verify judge access to that URL and the source repository. Local recording paths are not substitutes for accessible submission links. The current recording has no narration; [PITCH.md](PITCH.md) provides a three-minute narration script. The field accepts YouTube, Vimeo or Youku. Team details and any CAPTCHA step belong in the submission flow, not this narrative.
