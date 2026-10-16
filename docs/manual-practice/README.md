# Guided manual completion — 16 October 2026

One participant reported personally completing the supplier-comparison task in Chrome, Google Sheets and Notepad. The browser timer recorded **734.526 seconds (12 min 14.5 s)** from Start to Finish. Separate post-run reads confirmed a correct saved Sheet and report.

| Observation | Result |
| --- | --- |
| Participants / guided attempts | 1 / 1 |
| Unassisted reference attempts | 0 |
| Literal Sheet cells | All 18 correct: six headings and twelve supplier inputs |
| Formula sources / calculated results | All six formulas and all six results correct |
| Saved recommendation | Atlas Supplies, SGD 600, delivery within seven days |
| Task input timing / application-resource capture | Neither collected |

## What was measured

The participant used explicit Start and Finish buttons around the task. Elapsed time includes chat instructions, replies, waiting, application switching, and save/reopen steps. These components cannot be separated from the recorded boundaries. A private browser-button wrapper used the repository's manual collector; it did not inject task input. Its generic raw console-overhead description is clarified here: this attempt used browser buttons.

The task began with prepared synthetic supplier pages, a blank `Quotes` Sheet and a blank text report. The participant had already seen task explanations and project results. During this attempt, chat supplied step-by-step instructions, exact headings and formulas, and an example recommendation. The participant later stated an intention to write their own report; the saved text matches the supplied example after whitespace normalization. Input was not recorded, so typing versus pasting and independent authorship are not established.

This is evidence of successful **guided manual completion**. Participation is participant-reported, while saved-output correctness was checked separately. The duration is not pooled with the automated timing-policy benchmark and no human-versus-agent speed ratio is calculated. There is still no unassisted reference or human input-timing distribution for calibration.

## Inspect the evidence

- [Result and provenance](result.json): measured duration, relative start/stop boundaries, verification checks, assistance and limitations.
- [Saved Sheet readback](sheet-check.json): all 24 cells, including formula sources and effective values; private Sheet identity omitted.
- [Saved report](saved-report.txt): the text read after the participant finished.

The raw collector records remain unchanged with `completed-unverified` and false verification flags, which describe the collector's limited scope. Post-run output verification is recorded separately. The result includes SHA-256 hashes of retained raw records and public artifacts. Exact clock times, personal paths, Sheet IDs, timer URLs and process identifiers are excluded from this public evidence.
