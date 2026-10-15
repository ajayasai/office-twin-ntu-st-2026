# Submission checklist

**Status: draft; project details saved, judges' file upload being prepared.** Ajay is the team leader. Two additional teammates must join before final submission; Siddharth has been invited but has not joined.

**Team requirement:** 3–5 eligible NTU students. **Target submission:** 17 October 2026, 21:00 SGT. **Official cutoff:** 18 October 2026, 00:00 SGT, immediately after Saturday ends. [Official schedule](https://ntu-x-st-engineering-hackathon.devpost.com/details/dates)

## Ready

- [x] Public [GitHub source repository](https://github.com/ajayasai/office-twin-ntu-st-2026).
- [x] Three latest native Chrome → Google Sheets → Notepad runs completed all 11 steps at timing scale 1; 41 automated tests pass.
- [x] Saved text and displayed-sheet checks passed. Separate connector readback verified the alternate scenario's six formulas and Crest recommendation at SGD 525.
- [x] [Validation history](docs/VALIDATION.md), [architecture and provenance](docs/ARCHITECTURE.md), [setup instructions](docs/GOOGLE_SHEETS.md), and [Devpost narrative](docs/DEVPOST_ENTRY.md) are prepared.
- [x] Final narrated video is 180.13 seconds, preserving the continuous 162.13-second source run at 1× between an eight-second introduction and ten-second closing card.
- [x] [YouTube video](https://youtu.be/0OpIetkSomM) is published as **Unlisted**, verified in Studio; copyright and community checks passed. Viewer-facing playback was verified on the YouTube watch page.

The local final video is `dist/office-twin-submission.mp4`. Raw run evidence and videos are excluded from the source archive. The public video and repository links above are the submission links.

## Before final submission

- [ ] Confirm two teammates have joined and the entry lists 3–5 eligible NTU students, with Ajay as team leader. An invitation alone is not a completed join.
- [x] Verify the saved Devpost title, narrative, technology tags, repository URL, image, and embedded video in the project preview. Ajay's contribution reads "Team leader and project owner."
- [ ] Upload the review ZIP and save the judges' GitHub field, then verify the completed draft.
- [x] Verify watch-page playback. The local edit has readable captions and AAC narration; measured audio has no clipping.
- [ ] Push the final reviewed documentation and source, then verify the submission links and evidence descriptions.
- [ ] Submit after the required teammates have joined, by the target time above.
- [ ] Reopen the entry and confirm its submitted status, team membership and links; preserve the submitted commit and evidence set.

## Claims to preserve

The demonstrated task is a controlled, scenario-driven workflow, not arbitrary website understanding. Four of six documented Sheets development attempts completed; two earlier failures and their fixes remain in the evidence history. The three latest runs differ in seed, scenario and recording setup, so their durations are not a controlled efficiency comparison.

No human baseline or Sysmon trace was collected; WMI process-start collection returned Access denied. Resource figures cover the Python controller, not the full application workload. The manual collector is implemented, but its tests are not human reference runs. Excel/Word support remains untested. AI assistance and synthetic narration are disclosed.

No private organizer brief has been supplied. Apply any additional instructions if the team later provides one; no special approval requirement for Google Sheets or AI assistance is inferred from the public rules.
