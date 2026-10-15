# Office Twin — three-minute pitch

The spoken script below accompanies the existing 162.13-second desktop recording. Use an eight-second opening card, preserve the full recording at 1×, and finish with a roughly ten-second result card. That produces a three-minute cut without accelerating or splicing the recorded task. Timing markers are approximate; align narration to the visible actions before exporting.

Source footage: `runs/demo/office-twin-desktop-20261015-171812.mp4`. This recording shows the **default scenario**, which selects **Atlas at SGD 600**. A closing card may show the separately validated **alternate scenario**, labelled as a separate run, which selects **Crest at SGD 525**. Do not imply that the alternate outcome appears in the default recording.

## 0:00–0:08 — Opening card

**On screen:** Office Twin. Chrome → Google Sheets → Notepad. Recorded desktop execution, 1× playback.

**Narration:**

Office Twin completes a supplier comparison through real desktop input, with outputs and execution evidence you can inspect.

## 0:08–0:32 — Begin the continuous recording

**On screen:** The original footage begins, including its countdown and visible application opening.

**Narration:**

The task is to buy five sensor kits from the lowest-cost supplier that can deliver within seven days. Office Twin visits three local supplier pages in Chrome, compares the quotes in Google Sheets, and saves a recommendation in Notepad. The data is synthetic, and the workflow is driven by a validated scenario.

## 0:32–0:58 — Supplier pages

**On screen:** Continue the same recording. Keep supplier names and quotations readable.

**Narration:**

Our focus is connected office activity: navigating, typing, calculating, reviewing and saving. Contextual timing varies pauses by action, with a seed for repeatable policy samples. It also includes a scripted typing correction. These are engineering choices, not parameters learned from human recordings.

## 0:58–1:26 — Enter the comparison

**On screen:** The recording reaches the dedicated Sheet and enters its headings and supplier data.

**Narration:**

The runner selects its dedicated Quotes worksheet and enters the data through Chrome's visible interface. It checks the target window and spreadsheet, and Escape stops input. Google connectors are used separately for setup and verification; they do not write the task data during this desktop run.

## 1:26–1:54 — Formulas and saved-grid readback

**On screen:** Show the formulas being entered, followed by save confirmation, reload and readback.

**Narration:**

The sheet calculates total cost and delivery eligibility. After saving, the runner reloads and checks the displayed values. Atlas costs six hundred Singapore dollars and meets the deadline. Beacon is cheaper but late; Crest costs more. The system then opens Notepad to record the recommendation and checks the saved text separately.

## 1:54–2:30 — Write and correct the recommendation

**On screen:** Continue the original Notepad typing sequence. A small caption may identify the correction as scripted.

**Narration:**

The latest three native runs completed all eleven steps, and forty-one automated tests passed. The full Sheets development history includes four completed attempts and two failures, which we retained. This recorded run took about one hundred and fifty-nine seconds, using eighteen controller CPU-seconds and about eighty mebibytes of sampled controller memory. Those figures exclude Chrome and Notepad, and recording overhead prevents a direct efficiency comparison with our unrecorded runs.

## 2:30–2:50 — Save, reopen and verify

**On screen:** Finish the original recording through the reopened report. Let the final source frame finish naturally at approximately 2:50.13.

**Narration:**

We have not collected a human baseline or independent Sysmon trace. WMI access was denied, and the report says so. These results demonstrate task execution and checked outputs. They do not establish human indistinguishability or general desktop autonomy.

## 2:50–3:00 — Closing result card

**On screen:** “Separate alternate run: Crest selected at SGD 525.” Show a readable excerpt of its verified result, the repository address, and “Source • validation • reproducible scenarios.”

**Narration:**

A separate changed-price scenario selected Crest at five hundred and twenty-five dollars. The source and validation records explain the decision, measurements and remaining limits.

## Export and submission notes

- Keep the source recording uncut and at 1× within this version. The existing capture includes no microphone audio; narration must be added separately.
- The raw video is 162.13 seconds, while the run's measured wall time is 158.84 seconds. Capture begins before and ends after execution; those are different measurements.
- The spoken script is 340 words. Use a measured speaking pace and adjust pauses after checking the actual edit. Do not rush the limitations or shrink the evidence captions to fit.
- Keep the unedited recording available alongside the narrated cut if the submission destination permits. Label the alternate result card as a separate run.
- Use the final accessible repository and video URLs. The current Devpost video field accepts YouTube, Vimeo or Youku. Three minutes is our proposed format; follow any duration instruction in the team's brief.
- Facts and resource scope are documented in [VALIDATION.md](VALIDATION.md). AI-assistance provenance is documented in [ARCHITECTURE.md](ARCHITECTURE.md).
