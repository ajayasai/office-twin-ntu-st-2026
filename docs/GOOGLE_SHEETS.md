# Google Sheets workflow

Use **Chrome → Google Sheets → Notepad** when Microsoft Excel or Word is unavailable. The desktop executor types supplier data and formulas through Chrome's visible UI, then writes, saves, and reopens a plain-text recommendation in Notepad.

This remains a reduced native-application demonstration: Sheets generates browser activity, not an Excel process. The public brief allows office activities and applications but does not explicitly settle whether web spreadsheets satisfy the organizers' intended telemetry comparison. Confirm that point through the team's briefing or organizers before claiming equivalent scoring.

## Prerequisites

- Windows with an unlocked desktop, Python 3.11+, installed requirements, Google Chrome, and Notepad.
- A Google account already signed in to the **Chrome profile** used for the demonstration, with edit access to the target Sheet. The app does not log in, enter passwords, or handle authentication prompts.
- Chrome and Google Sheets in English, with standard keyboard shortcuts and accessible Name box controls.
- A dedicated test spreadsheet with a **Quotes** tab. Reserve **A1:F4** for the three-supplier scenario. Each run selects the Quotes tab, binds to its worksheet ID, clears that owned range, and replaces its data. Do not select a personal or production sheet.
- Only one Chrome window displaying the target spreadsheet. Close first-run, sign-in, recovery, and other blocking dialogs yourself before starting.
- Reliable Internet access so Sheets can report **Saved to Drive**.

The setup workflow creates an empty `.xlsx` fixture and imports it as a native Google Sheet. Connectors are used only for setup and independent verification. Runtime task data is entered through native mouse/keyboard input; the executor makes no Google Sheets API calls.

## Run

Select the Google Sheets workflow in the control panel and supply the dedicated Sheet's edit URL. The equivalent command is:

```powershell
python -m office_twin --mode desktop --workflow sheets --timing contextual --seed 42 --sheet-url "PASTE_DEDICATED_SHEET_EDIT_URL" --output runs
```

Replace the placeholder with the dedicated fixture's verified URL. Use `--timing fixed` for the comparison condition. Keep the spreadsheet URL in local settings rather than committing a private account-linked fixture URL to the public repository.

Once started, leave the desktop alone. Press Escape to stop native input. The executor also stops if its intended window, document title, spreadsheet, or selected worksheet ID changes. These guards check the window and URL boundaries, not every possible in-page focus change. Close popups before running; same-window dialogs are not comprehensively guarded.

## Workload and expected values

The browser first displays local fictional supplier quotes. The agent then enters these inputs and formulas in Google Sheets:

| Supplier | Unit price (SGD) | Qty | Lead days | Total (SGD) | Meets deadline |
| --- | ---: | ---: | ---: | ---: | --- |
| Atlas Supplies | 120 | 5 | 7 | 600 | YES |
| Beacon Supply | 115 | 5 | 10 | 575 | NO |
| Crest Industrial | 125 | 5 | 3 | 625 | YES |

For this default fixture, column E uses `=B2*C2` and corresponding row references. Column F uses `=IF(D2<=7,"YES","NO")` and corresponding row references. Atlas is the lowest-cost supplier meeting the seven-day deadline. A custom scenario supplies its own quotes and deadline; the formulas, expected values, and recommendation must follow those inputs. The scenario still uses local synthetic supplier pages, not arbitrary external websites.

## What verification means

The executor waits for the visible Saved to Drive status, reloads the sheet, and copies the active task range through the UI (**A1:F4** by default). It compares the displayed headers, inputs, and computed values against the exercise. The copied range replaces the clipboard contents. Actual readback is saved as `sheets-readback.json` in the run workspace, including the values and checks.

The final report is independently read from the saved text file. A run fails if either the grid values or the saved report are wrong. The runtime clipboard check verifies displayed results, **not formula source**: inspect the formula cells separately or use a read-only connector check to establish that the formulas exist. A cloud-save indicator and a reload are useful UI evidence, not independent Windows process telemetry.

For a competition recording, show the real Chrome grid, formula bar, cloud-save state, and reopened Notepad report. Label this as the Sheets workflow. Keep independent process/event capture separate from controller logs and describe the browser and Notepad processes actually observed. Do not label it an Excel/Word demonstration.

## Validation status

After the initial accelerated smoke test, the worksheet-binding and range-clearing version completed three normal-speed native runs on 15 October 2026: fixed timing (`20261015T091539Z-3d7a2a48`), recorded contextual timing (`20261015T091815Z-588afee5`), and alternate contextual timing (`20261015T092135Z-e43abfcb`). All eleven steps and artifact checks passed in each run.

The alternate scenario changes the first row to Crest at SGD 105 per unit, correctly calculates SGD 525, and changes the recommendation to Crest. A separate read-only connector query confirmed all six actual formulas and the computed values; its result is saved as `sheets-independent-verification.json` in that run folder. The recorded contextual video is 162.13 seconds at 1× playback. Thirty-six automated tests pass.

No human baseline was collected. No Sysmon capture was collected and WMI process-start collection reported access denied, so functional success does not establish human-like timing or independent process-telemetry authenticity. See [validation details](VALIDATION.md).
