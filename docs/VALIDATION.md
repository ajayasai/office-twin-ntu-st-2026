# Observed validation — 15 October 2026

The latest three native runs each completed all **11 steps**, including a saved Google Sheets comparison and a reopened, correct Notepad recommendation. The third run changed supplier order and price; the recommendation changed from Atlas at $600 to Crest at $525. These are small functional checks on one machine, not a reliability estimate or a human-similarity benchmark.

The workflow used **Chrome → Google Sheets → Notepad** on Windows with Python 3.14. Runtime actions used desktop input and UI Automation. Google connectors were used for fixture setup and independent readback, not to write the sheet during a native run. The task uses validated synthetic scenario data; it does not autonomously extract arbitrary websites.

Observed setup: Windows 11 Home Single Language, build 26200; Python 3.14.2; Chrome 155.0.8059.40; Notepad 11.2607.14.0; Intel Core Ultra 7 155U (14 logical processors); 31.55 GiB OS-reported RAM; primary display 1920×1200. Applications were already installed and Chrome was signed in to the dedicated test Sheet. This was not a clean-machine installation test.

## Latest normal-speed runs

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

Raw local evidence, videos, credentials, personal settings and the virtual environment are excluded from the source archive. The [source repository is public](https://github.com/ajayasai/office-twin-ntu-st-2026). The narrated [YouTube video](https://youtu.be/0OpIetkSomM) is published as **Unlisted**, verified in YouTube Studio; copyright and community checks passed. Viewer-facing playback was verified on the YouTube watch page. The Devpost entry remains a draft: Ajay is the team leader, and final submission is held until two teammates have joined.

## Automated verification and limits

**41 unit tests passed** in the final suite, including five checks for the manual reference collector. The earlier suite contained 36 tests. They cover scenario validation and changed decisions, timing bounds and reproducibility, CPU delta reporting, failure/cancellation reporting, HTML escaping, comparison scope, and unavailable process tracing. They do not replace native end-to-end runs.

The [manual reference collector](MANUAL_BASELINE.md) is implemented and tested. It records explicit participant start/stop, optional phase markers, and resource snapshots for selected PIDs; it records no task keystrokes, pointer activity or screen content. Outcomes remain participant-reported and unverified. Collector tests are not human reference observations, and no manual run has been collected.

The passive WMI process-start collector returned **Access denied** on this host. No independent Sysmon export was collected. Controller action logs and process snapshots must not be presented as independent Sysmon evidence. Security and logging settings were not changed.

No human reference runs have been collected, and the timing parameters remain engineering defaults. No human-indistinguishability, general desktop autonomy, arbitrary website extraction or official benchmark score is claimed. The optional native Excel/Word workflow remains untested because Office activation was unavailable. Desktop tests require an idle, unlocked session and the documented app state; window guards do not prove every focused child control is correct.

The most valuable next work is the manual-versus-agent evidence in [EVALUATION.md](EVALUATION.md), confirmation of the private organizer brief, and reproduction on the intended demonstration machine.
