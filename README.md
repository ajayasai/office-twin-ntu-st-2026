# Office Twin

Office Twin is an NTU × ST Engineering Hackathon project for a synthetic office worker: review local supplier quotes in **Chrome**, compare them in **Google Sheets**, and write a recommendation in **Notepad**. It performs a controlled, repeatable scenario through visible desktop input. It does not navigate or understand arbitrary websites.

**Status:** three normal-speed native Chrome → Google Sheets → Notepad runs completed all **11/11 steps**: fixed timing, recorded contextual timing, and an alternate scenario. All saved-report and displayed-sheet checks passed. Independent read-only connector checks also verified actual formula source and values for the initial smoke test and the alternate scenario. The automated test suite passes **41 tests**. Excel/Word support is optional and untested here because licensed Office is unavailable.

Source is in the public [GitHub repository](https://github.com/ajayasai/office-twin-ntu-st-2026). The completed narrated submission video is **180.13 seconds**: an eight-second introduction, the continuous 162.13-second desktop recording at 1×, and a ten-second closing card. The local file is `dist/office-twin-submission.mp4`. The [YouTube video](https://youtu.be/0OpIetkSomM) is published as **Unlisted**, verified in YouTube Studio; copyright and community checks passed. Viewer-facing playback was verified on the YouTube watch page. Raw runs and video files are excluded from the source repository.

**Submission status:** draft. Ajay is the team leader; final submission is held until two teammates have joined.

| Verified normal-speed run | Evidence folder | Result |
| --- | --- | --- |
| Fixed timing, default scenario | `runs/20261015T091539Z-3d7a2a48` | 11/11 steps; artifact checks passed |
| Contextual timing, recorded default scenario | `runs/demo/20261015T091815Z-588afee5` | 11/11 steps; artifact checks passed |
| Contextual timing, alternate scenario | `runs/20261015T092135Z-e43abfcb` | 11/11 steps; artifact checks passed; Crest selected at SGD 525 |

No human baseline was collected. No Sysmon capture was collected, and WMI process-start collection reported access denied. These runs establish task execution and output correctness, not human indistinguishability or validated process-telemetry authenticity. No private organizer brief was available for review. See [validation details](docs/VALIDATION.md).

## Run

Use Python 3.11 or newer. Open a terminal in this repository and create a virtual environment:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The dependencies include `pywinauto` and `psutil`. Launch the Tk interface:

```powershell
.\.venv\Scripts\python.exe -m office_twin
```

Run the safe simulation without opening native applications:

```powershell
.\.venv\Scripts\python.exe -m office_twin --mode simulate
```

Run the primary desktop scenario on Windows with Chrome already signed in to the dedicated Google Sheet:

```powershell
.\.venv\Scripts\python.exe -m office_twin --mode desktop --workflow sheets --timing contextual --seed 42 --sheet-url "PASTE_DEDICATED_SHEET_EDIT_URL" --output runs
```

For a timing comparison, repeat with a separate output directory:

```powershell
.\.venv\Scripts\python.exe -m office_twin --mode desktop --workflow sheets --timing fixed --seed 42 --sheet-url "PASTE_DEDICATED_SHEET_EDIT_URL" --output runs/fixed
```

Use `--workflow notepad` for the smaller Chrome-and-Notepad task, which needs no spreadsheet account. Use `--workflow office` only on a machine with installed, licensed Excel and Word; that path has not been validated here. See the [Google Sheets setup guide](docs/GOOGLE_SHEETS.md) before a Sheets run.

`runs` is the default output location. Keep contextual and fixed runs separately so evidence is not mixed. Close unrelated documents and first-run dialogs, and use a dedicated test desktop before native testing. Do not test against personal documents or production websites.

## What to demonstrate

1. Read synthetic supplier information on the run's local website in Chrome.
2. Enter the comparison and formulas through Google Sheets' UI, confirm cloud save, and read back the displayed results.
3. Write, save, and reopen a Notepad recommendation consistent with that comparison.
4. Show the actual output files alongside recorded action timing and resource measurements.

Use application state and saved content to determine task success. A log entry saying an action ran is not sufficient proof that it succeeded.

## Evidence and limitations

- **Simulation** exercises orchestration and reporting without performing native office work. Label all its outputs as simulated.
- **Agent logs** are self-reported execution records. They are not independent Windows telemetry.
- **Native evidence** includes the real Google Sheet, its UI readback, the saved text report, a screen recording, and independently collected Windows telemetry where available. Browser-based Sheets activity does not create Excel process evidence.
- **Resource measurements** must state their scope. Agent-process CPU/RAM alone excludes Chrome and Notepad, or Excel/Word when using the optional Office path.
- **Human comparisons** require consented manual runs of the same task. Synthetic or automated traces must never be labelled human.
- **Manual reference collector:** `tools/record_manual.py` records explicit task boundaries, optional participant markers and selected-process resources. It does not collect keystroke timings or independently verify human participation or task success. The tool is ready; no human reference runs have been collected. See the [collection guide](docs/MANUAL_BASELINE.md).
- **Timing** is a testable model of pauses and activity, not proof of indistinguishability or a guarantee against automation detection.

If Sysmon is already installed and authorized for the test environment, export the relevant records using the existing configuration. Do not disable security controls, alter logs, manipulate process ancestry, or change security logging settings to improve the result. State when an event type is unavailable under the current configuration.

## Project documents

- [Architecture and AI/dependency provenance](docs/ARCHITECTURE.md)
- [Winning strategy and schedule](STRATEGY.md)
- [Submission checklist](SUBMISSION.md)
- [Paired benchmark and human-baseline protocol](docs/EVALUATION.md)
- [Suggested demo storyboard](docs/DEMO.md)
- [Manual reference collector and guide](docs/MANUAL_BASELINE.md)
- [Manual baseline log template](docs/baseline-template.csv)
- [Devpost project narrative](docs/DEVPOST_ENTRY.md)
- [Narrated pitch script](docs/PITCH.md)
- [Validation details](docs/VALIDATION.md)

## Provenance

This project is being developed with AI assistance. Document the tools used, generated or adapted components, third-party dependencies, and the human review and validation performed. The public event pages do not resolve all policies on AI assistance or pre-existing code; the participating students should confirm these points with the organizers and follow any private briefing they received. Do not claim that unreviewed generated code is original human work or that unperformed tests passed.

The public event requires complete source through a GitHub link, implementation documentation, and a demonstration video. The deadline is **18 October 2026, 00:00 Singapore time**, immediately after Saturday 17 October ends. See the [official overview](https://ntu-x-st-engineering-hackathon.devpost.com/), [rules](https://ntu-x-st-engineering-hackathon.devpost.com/rules), and [schedule](https://ntu-x-st-engineering-hackathon.devpost.com/details/dates).
