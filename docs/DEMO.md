# Suggested demonstration storyboard

This is a suggested **three-minute** pitch format, not a published competition time limit. Confirm any private organizer instructions.

A real native run was recorded on **15 October**: `runs/demo/office-twin-desktop-20261015-171812.mp4` (162.13 seconds, 1920×1200, continuous 1× playback, no microphone; capture requested 15 fps). Its matching run is `runs/demo/20261015T091815Z-588afee5`, which completed 11/11 steps. A stable copy, `office-twin-demo.mp4`, is included in the judges' evidence archive. It shows the functional version before the subsequent Notepad launch and observer changes. It does not depict the later ten-run benchmark or participant's human measurements.

The [updated narrated pitch](PITCH.md) preserves this complete recording at 1×, labels its date throughout, and reports the later ten native completions, five matched pairs, 85 passing tests and participant-confirmed 720-second human baseline separately. The human aggregate record lacks raw traces and is not used for a matched speed or human-similarity claim. See [observed validation](VALIDATION.md) for evidence and limits. The storyboard below describes the presentation flow; the pitch script defines the actual narration and media build.

| Time | Show | Say or establish |
| --- | --- | --- |
| 0:00–0:20 | The task: local supplier quotes, a Google Sheets comparison, and a Notepad recommendation. | Office Twin performs a controlled office workflow, and we evaluate the activity it actually produces. |
| 0:20–1:20 | A real native run moving from local Chrome pages to Google Sheets and then Notepad. | Identify the fixture, explain relevant pauses/corrections that were actually implemented, and show that output values remain correct. |
| 1:20–1:50 | The saved Sheet and reopened text report. | Demonstrate actual formula cells, computed values, cloud-save state, and the recommendation's agreement with the comparison. |
| 1:50–2:30 | Evidence for the four rubric categories. | Show only collected timing comparisons, independent telemetry, success counts, and resource measurements. State the sample size and measurement scope. |
| 2:30–3:00 | Reproduction command, supported setup, limitations, and repository link. | Explain what runs reliably, what remains limited, and how judges can inspect or repeat the result. |

## Recording rules

- Capture a successful run from the documented starting state and preserve its matching output files and logs.
- If accelerating a long run, visibly label playback speed. Do not splice separate attempts into an apparently uninterrupted successful run.
- Label recordings as recordings. Clearly distinguish simulation clips from native execution.
- Keep application text and chart labels readable. A slow, legible evidence view is more useful than several unreadable charts.
- Do not show invented metrics or claim that logs were independently collected when they came from the controller.
- Mention actual failures or setup constraints briefly and accurately. Keep a separate unedited run available if the organizer's submission format permits.
- Include accurate AI-assistance and third-party-code provenance in the accompanying documentation.
- Describe the actual Chrome and Notepad processes. Browser-based Sheets does not produce Excel process evidence; label any separately demonstrated Office path accurately.

## Rehearsal questions

Each team member should be able to answer:

1. How do you know the office task completed correctly?
2. Which evidence comes from the controller, and which was recorded independently?
3. What changed between fixed and contextual timing, and what did the comparison show?
4. What does the CPU/RAM figure include and exclude?
5. Which parts were built or adapted with AI assistance, and how did the team validate them?
6. What fails outside the demonstrated setup, and what would you improve next?
