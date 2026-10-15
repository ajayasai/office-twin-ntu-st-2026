# Submission checklist

**Target:** 17 October 2026, 21:00 SGT. **Official cutoff:** 18 October 2026, 00:00 SGT. Do not interpret midnight as the end of Sunday. [Schedule](https://ntu-x-st-engineering-hackathon.devpost.com/details/dates)

Unchecked items below are required work or review points, not completed claims.

The primary entry targets Chrome, Google Sheets, and Notepad. Three normal-speed native runs—fixed, recorded contextual, and alternate contextual—completed all 11/11 steps with correct saved outputs; 36 automated tests pass. The local 1× demonstration video is 162.13 seconds long. Independent connector reads verified the alternate scenario's actual formulas and values, including Crest at SGD 525. The optional Excel/Word path remains untested.

No human baseline was collected. No Sysmon capture was collected, and WMI collection reported access denied. No private organizer brief was available for review. Preserve these limits in the submitted claims. Evidence locations are recorded in [validation details](docs/VALIDATION.md).

## Team and event requirements

- [ ] Confirm 3–5 eligible NTU students and ensure each required team member is included in the entry.
- [ ] Read the private challenge brief and reconcile it with the public requirements.
- [ ] Have a team member clarify organizer-specific AI/pre-existing-code policy and record the answer.
- [ ] Confirm organizer acceptance of Google Sheets and a plain-text recommendation for this workflow.
- [ ] Review any licensing and source-disclosure obligations for dependencies or borrowed code.

## Source and reproducibility

- [x] Create the private [source repository](https://github.com/ajayasai/office-twin-ntu-st-2026).
- [ ] Push the final reviewed source and documentation to the submission commit.
- [ ] Install from the documented instructions on the evaluation setup.
- [x] Record the tested machine, OS, application versions and primary display in [validation](docs/VALIDATION.md); document the [Sheet setup](docs/GOOGLE_SHEETS.md).
- [ ] Run the exact documented native Sheets command and check the cloud sheet plus saved text report manually.
- [x] Preserve all seven recorded native development attempts, including two failed Sheets attempts, in the local evidence history.
- [ ] Remove secrets and personal data; use only synthetic business fixtures in shared artifacts.
- [ ] Check that judges can access the repository and required files without requesting additional permissions.

## Evidence

- [ ] Keep simulation outputs explicitly separate from real desktop evidence.
- [ ] Include the real Google Sheet and saved text recommendation whose values agree; verify formulas separately from displayed values.
- [ ] Describe observed Chrome/Notepad telemetry accurately, without presenting browser activity as Excel/Word activity.
- [ ] Include anonymized agent logs; label them self-reported.
- [ ] Include independent Windows telemetry only if actually collected, with capture scope and configuration documented.
- [ ] Include consented manual baselines only if performed; otherwise state that no human comparison was collected.
- [ ] Report timing and resource metrics with units, sampling interval, process scope, run count, and failure count.
- [ ] Explain observed differences and limitations without claiming indistinguishability.

## Documentation and video

- [x] Update README status with completed runs, tests, recording, and current limitations.
- [x] Explain the [architecture, workflow, timing and error handling](docs/ARCHITECTURE.md), plus the [evaluation procedure](docs/EVALUATION.md).
- [x] Disclose AI assistance and dependency provenance; state that student review has not been recorded.
- [x] Record the native contextual demonstration: [local 1× video](runs/demo/office-twin-desktop-20261015-171812.mp4), 162.13 seconds.
- [ ] Upload the reviewed video to an organizer-accepted destination and verify judge access.
- [ ] Use the suggested [three-minute storyboard](docs/DEMO.md), adjusting to any organizer-specified limit.
- [ ] Label speed changes, edited sequences, simulated material, and recorded-versus-live demonstrations.
- [ ] Check video playback, readable text, sound, and link accessibility.

## Devpost entry draft

**Project name:** Office Twin

**One-line description:** A synthetic office worker that turns local supplier quotes into a Google Sheets comparison and a Notepad recommendation, with measurable desktop activity and timing.

**Problem:** Desktop-agent demonstrations can show task completion while leaving the resulting system activity, timing, and computing cost unexamined.

**Approach:** Perform one controlled office task through visible Chrome and Notepad input, record execution evidence, and compare observed behavior with documented baselines. The agent uses local synthetic supplier pages and an explicitly supplied test Sheet. Only describe capabilities that the submitted version has demonstrated; do not claim arbitrary-site understanding.

**What we measured:** Three normal-speed native runs completed 11/11 steps each: fixed timing (`20261015T091539Z-3d7a2a48`), recorded contextual timing (`20261015T091815Z-588afee5`), and alternate contextual timing (`20261015T092135Z-e43abfcb`). Saved text and displayed-sheet checks passed. A read-only connector query independently confirmed the alternate scenario's formula source and values. Thirty-six automated tests pass. Report resource values from the matching run reports with their actual process scope; do not infer missing telemetry or human similarity from successful completion.

**Limitations:** The workflow uses controlled local pages, three synthetic suppliers, Google Sheets in Chrome, and Notepad. It does not establish arbitrary-site autonomy. No human baseline or Sysmon capture was collected; WMI process-start collection was unavailable because access was denied. Excel/Word remains untested, and private organizer requirements were unavailable for review. Keep earlier failed attempts in the evidence history.

## Final submission check

- [ ] Add the complete GitHub source link, documentation, and video required by the [official overview](https://ntu-x-st-engineering-hackathon.devpost.com/).
- [ ] Have another teammate follow every link and compare the entry's claims against the evidence.
- [ ] Submit by 21:00 SGT on 17 October.
- [ ] Reopen the submitted entry and verify the final state and team membership.
- [ ] Preserve the submitted commit and evidence set so the team can reproduce and explain it during judging.
