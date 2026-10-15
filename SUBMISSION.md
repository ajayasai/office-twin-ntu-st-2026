# Submission checklist

**Target:** 17 October 2026, 21:00 SGT. **Official cutoff:** 18 October 2026, 00:00 SGT. Do not interpret midnight as the end of Sunday. [Schedule](https://ntu-x-st-engineering-hackathon.devpost.com/details/dates)

Unchecked items below are required work or review points, not completed claims.

The primary entry targets Chrome, Google Sheets, and Notepad. Its eleven-step native smoke run completed with correct displayed values, independently verified formulas, and a saved-text check. Timing scale `0.15` accelerated that functional test; it does not establish human-like timing. The optional Excel/Word path remains untested. Preserve those distinctions in the submitted claims.

## Team and event requirements

- [ ] Confirm 3–5 eligible NTU students and ensure each required team member is included in the entry.
- [ ] Read the private challenge brief and reconcile it with the public requirements.
- [ ] Have a team member clarify organizer-specific AI/pre-existing-code policy and record the answer.
- [ ] Confirm organizer acceptance of Google Sheets and a plain-text recommendation for this workflow.
- [ ] Review any licensing and source-disclosure obligations for dependencies or borrowed code.

## Source and reproducibility

- [ ] Put the complete source in the GitHub repository used for submission.
- [ ] Install from the documented instructions on the evaluation setup.
- [ ] Record Windows, Python, Chrome and Notepad versions, machine specifications, display settings, and Google Sheets setup. Record Office versions only if that optional path is demonstrated.
- [ ] Run the exact documented native Sheets command and check the cloud sheet plus saved text report manually.
- [ ] Record all attempted runs, including partial completions and failures.
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

- [ ] Update README status to reflect only the tests and demonstrations actually completed.
- [ ] Explain the architecture, workflow, timing model, error handling, and evaluation procedure.
- [ ] Disclose AI assistance, third-party code, and human review accurately.
- [ ] Record and upload a demonstration video. No video is provided or implied by this repository's planning documents.
- [ ] Use the suggested [three-minute storyboard](docs/DEMO.md), adjusting to any organizer-specified limit.
- [ ] Label speed changes, edited sequences, simulated material, and recorded-versus-live demonstrations.
- [ ] Check video playback, readable text, sound, and link accessibility.

## Devpost entry draft

**Project name:** Office Twin

**One-line description:** A synthetic office worker that turns local supplier quotes into a Google Sheets comparison and a Notepad recommendation, with measurable desktop activity and timing.

**Problem:** Desktop-agent demonstrations can show task completion while leaving the resulting system activity, timing, and computing cost unexamined.

**Approach:** Perform one controlled office task through visible Chrome and Notepad input, record execution evidence, and compare observed behavior with documented baselines. The agent uses local synthetic supplier pages and an explicitly supplied test Sheet. Only describe capabilities that the submitted version has demonstrated; do not claim arbitrary-site understanding.

**What we measured:** Replace this paragraph with actual run counts, completion results, timing comparisons, resource measurements, and the scope of any independently collected telemetry. If a measurement was not collected, say so. Do not fill missing values with estimates presented as results.

**Limitations:** Record the supported machine/application setup, brittle steps, unresolved failures, telemetry coverage, baseline sample size, and any untested conditions.

## Final submission check

- [ ] Add the complete GitHub source link, documentation, and video required by the [official overview](https://ntu-x-st-engineering-hackathon.devpost.com/).
- [ ] Have another teammate follow every link and compare the entry's claims against the evidence.
- [ ] Submit by 21:00 SGT on 17 October.
- [ ] Reopen the submitted entry and verify the final state and team membership.
- [ ] Preserve the submitted commit and evidence set so the team can reproduce and explain it during judging.
