# Office Twin — three-minute pitch, 16 October evidence update

The spoken script below accompanies the existing 162.13-second desktop recording. An eight-second opening card, the full recording at 1×, and a ten-second result card produce a 180.13-second cut. The top banner identifies the footage as the **15 October functional version**, before the subsequent Notepad launch and observer changes. Later benchmark and human-reference results are reported separately in narration and captions; the footage does not depict those measurements.

Source footage: `runs/demo/office-twin-desktop-20261015-171812.mp4`. This recording shows the **default scenario**, which selects **Atlas at SGD 600**. Historical narrated versions are retained separately. The current closing card summarizes the later evidence rather than implying that it appears in the original run.

## 0:00–0:08 — Opening card

**On screen:** Office Twin. Chrome → Google Sheets → Notepad. 15 October functional recording, continuous 1× playback; later results reported separately.

**Narration:**

Office Twin performs real desktop work. This continuous October fifteenth recording accompanies our updated evidence.

## 0:08–0:32 — Begin the continuous recording

**On screen:** The original footage begins, including its countdown and visible application opening.

**Narration:**

The task is to buy five sensor kits from the lowest-cost supplier that can deliver within seven days. Office Twin visits three local supplier pages in Chrome, compares the quotes in Google Sheets, and saves a recommendation in Notepad. A validated scenario drives this synthetic task; arbitrary website understanding is outside its scope.

## 0:32–0:58 — Supplier pages

**On screen:** Continue the same recording. Keep supplier names and quotations readable.

**Narration:**

The workflow connects navigation, typing, calculation, review and saving. Contextual timing varies pauses by action, with a seed for repeatable policy samples. A scripted typing correction adds another observable action. These engineering defaults have not been calibrated to the human measurements. The real applications generate their own process and resource activity.

## 0:58–1:26 — Enter the comparison

**On screen:** The recording reaches the dedicated Sheet and enters its headings and supplier data.

**Narration:**

The runner selects its dedicated Quotes worksheet and enters data through Chrome's visible interface. It checks the target window and spreadsheet, and Escape stops input. Google connectors support separate setup and saved-cell verification. All task data during the desktop run is entered through keyboard and mouse actions.

## 1:26–1:54 — Formulas and saved-grid readback

**On screen:** Show the formulas being entered, followed by save confirmation, reload and readback.

**Narration:**

The sheet calculates total cost and delivery eligibility. After saving, the runner reloads and checks displayed values. Atlas costs six hundred Singapore dollars and meets the deadline. Beacon is cheaper but late; Crest costs more. The recommendation is saved and reopened in Notepad, and its text is checked separately.

## 1:54–2:30 — Write and correct the recommendation

**On screen:** Continue the original Notepad typing sequence. The caption explicitly labels the later benchmark statistics; the historical-recording banner remains visible.

**Narration:**

Separate October sixteenth evaluation completed ten native tasks with all eleven steps, five matched timing pairs, and eighty-five passing tests. Contextual timing added a median eleven point two six seconds within pairs. A separate observer sampled actual process parents, CPU and memory, with capture gaps and unresolved identities reported. Those later runs are distinct from this footage. The public repository retains earlier failures, measurement scope and saved-output checks.

## 2:30–2:50 — Save, reopen and verify

**On screen:** Finish the original recording through the reopened report. Show the participant-confirmed 720-second unassisted reference as a separate evidence caption. Let the final source frame finish naturally at approximately 2:50.13.

**Narration:**

A participant confirms an unassisted human baseline of seven hundred twenty seconds, including typing, interaction, resource and ancestry measurements. The supplied aggregates lack raw traces. We report them separately without claiming human indistinguishability or a matched speed advantage.

## 2:50–3:00 — Closing result card

**On screen:** “Later evidence / 16 October update: 10/10 native tasks • 5 matched pairs • 85 tests passed.” State that the 720-second human baseline is participant-confirmed aggregate data, and show the repository address.

**Narration:**

Inspect the complete source, reproduction steps, validation records and human baseline. The documentation distinguishes every evidence source and its limits.

## Export and submission notes

- Keep the source recording uncut and at 1× within this version. The existing capture includes no microphone audio; narration must be added separately.
- The raw video is 162.13 seconds, while the run's measured wall time is 158.84 seconds. Capture begins before and ends after execution; those are different measurements.
- The build checks every narration slot and rejects speech requiring more than 1.35× audio acceleration. Video playback always remains continuous 1×; the generated `build.json` records actual audio timings.
- Keep the unedited recording and previous narrated version separately. The updated narration does not change the runtime shown in the historical recording.
- Use the final accessible repository and video URLs. The current Devpost video field accepts YouTube, Vimeo or Youku. Three minutes is our proposed format; follow any duration instruction in the team's brief.
- Facts and resource scope are documented in [VALIDATION.md](VALIDATION.md). AI-assistance provenance is documented in [ARCHITECTURE.md](ARCHITECTURE.md).
- Optional media tooling requires Pillow, FFmpeg/ffprobe on PATH, and Windows System.Speech with Microsoft Zira Desktop. These are not runtime dependencies. Rebuild with `python tools/build_pitch.py --source PATH_TO_ORIGINAL_RECORDING --work-dir runs/pitch-update --output runs/pitch-update/office-twin-submission-updated.mp4 --cover-output runs/pitch-update/office-twin-cover.png`. This preserves the prior submitted media. The original 162.13-second recording is also distributed as `office-twin-demo.mp4` in the judges' evidence archive; supply that file as `--source` when rebuilding from the archive.
