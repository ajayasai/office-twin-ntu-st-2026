# Submission checklist

**Status: submitted on 16 October 2026 (SGT).** Devpost displayed **"Project submitted!"** and **"SUBMITTED TO NTU x ST Engineering Hackathon"**. The joined team is:

- **Ajay Asaithambi** — `@ajay007`, team leader.
- **Siddharth Paliwal** — `@siddhartha-paliwal21`.
- **Sourabh Sooraj** — `@sourabhsooraj97`.

**Team requirement:** 3–5 eligible NTU students. **Target submission:** 17 October 2026, 21:00 SGT. **Official cutoff:** 18 October 2026, 00:00 SGT, immediately after Saturday ends. [Official schedule](https://ntu-x-st-engineering-hackathon.devpost.com/details/dates)

## Ready

- [x] Public [GitHub source repository](https://github.com/ajayasai/office-twin-ntu-st-2026).
- [x] Three latest native Chrome → Google Sheets → Notepad runs completed all 11 steps at timing scale 1; 41 automated tests pass.
- [x] Saved text and displayed-sheet checks passed. Separate connector readback verified the alternate scenario's six formulas and Crest recommendation at SGD 525.
- [x] [Validation history](docs/VALIDATION.md), [architecture and provenance](docs/ARCHITECTURE.md), [setup instructions](docs/GOOGLE_SHEETS.md), and [Devpost narrative](docs/DEVPOST_ENTRY.md) are prepared.
- [x] Final narrated video is 180.13 seconds, preserving the continuous 162.13-second source run at 1× between an eight-second introduction and ten-second closing card.
- [x] [YouTube video](https://youtu.be/0OpIetkSomM) is published as **Unlisted**, verified in Studio; copyright and community checks passed. Viewer-facing playback was verified on the YouTube watch page.

The local final video is `dist/office-twin-submission.mp4`. Raw run evidence and videos are excluded from the source archive. The public video and repository links above are the submission links.

## Submission verification

- [x] Confirm all three team members have joined the Devpost entry, with Ajay as team leader.
- [x] Verify the saved Devpost title, narrative, technology tags, repository URL, image, and embedded video in the project preview. Ajay's contribution reads "Team leader and project owner."
- [x] Upload the review ZIP and save the judges' GitHub field.
- [x] Verify watch-page playback. The local edit has readable captions and AAC narration; measured audio has no clipping.
- [x] Push the reviewed documentation and source; preserve the package commit and artifact hashes in `dist/manifest.json`.
- [x] Complete the final rules/Terms confirmations with explicit user approval.
- [x] Submit after the required teammates joined, before the target time above.
- [x] Verify the success toast and submitted competition status in Devpost.

The uploaded source archive is based on commit [`5dd7181317838d9cfa52ba023cf02037539ac5ff`](https://github.com/ajayasai/office-twin-ntu-st-2026/commit/5dd7181317838d9cfa52ba023cf02037539ac5ff). Its artifact hashes remain in `dist/manifest.json`. Later documentation commits record submission status only; they do not create new test results, rebuild the package or replace the uploaded archive.

## Claims to preserve

The demonstrated task is a controlled, scenario-driven workflow, not arbitrary website understanding. Four of six documented Sheets development attempts completed; two earlier failures and their fixes remain in the evidence history. The three latest runs differ in seed, scenario and recording setup, so their durations are not a controlled efficiency comparison.

No human baseline or Sysmon trace was collected; WMI process-start collection returned Access denied. Resource figures cover the Python controller, not the full application workload. The manual collector is implemented, but its tests are not human reference runs. Excel/Word support remains untested. AI assistance and synthetic narration are disclosed.

No private organizer brief has been supplied. Apply any additional instructions if the team later provides one; no special approval requirement for Google Sheets or AI assistance is inferred from the public rules.
