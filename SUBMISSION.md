# Submission status and evidence revision

## Rundown supplement prepared — 16 October 2026 (SGT)

The [new rundown evidence](docs/process-rundown/README.md) verifies 32/32 focus observations against three existing application identities, using actual before/after state records and exact independent OS snapshots. All 16 application starts inside the native windows have compatible parent identities: two Explorer → Chrome, ten Chrome → Chrome and four Explorer → Notepad. Thirteen have observed exits within the capture; three Chrome processes remain present in final rundown. The three warm main applications' original parents remain unavailable. Applications stayed open as requested.

The fresh seed-311 retry completed both 11-step native tasks and all 28 known process lifecycles, with zero reported final ETW loss. It used clean tooling source `95bb3efc830a2d811b69cc68c9483ae9b0353fec`; the 139-test suite passed before capture. The earlier warm rundown attempt stopped on a foreground-focus change during its second task and is retained as failed. Historical timing, human aggregates and the prior ETW result remain unchanged. The new source and evidence archive are prepared for replacing the current Devpost story and judges' attachment; verified upload details will be recorded after readback.

**The entry was submitted on 16 October 2026 (SGT).** Devpost displayed “Project submitted!” and “SUBMITTED TO NTU x ST Engineering Hackathon”. Team:

- **Ajay Asaithambi** — `@ajay007`, team leader and project owner.
- **Siddharth Paliwal** — `@siddhartha-paliwal21`.
- **Sourabh Sooraj** — `@sourabhsooraj97`.

Official cutoff: **18 October 2026, 00:00 SGT**. [Official schedule](https://ntu-x-st-engineering-hackathon.devpost.com/details/dates).

## Revised evidence prepared on 16 October

- [x] Ten normal-speed native tasks, all 11/11 steps; five comparable policy pairs, no revised attempts excluded.
- [x] 85 passing automated tests; separate observer coverage, overhead and pseudonymized process-parent evidence.
- [x] Real Explorer report-opening change; original Python-parent observations and excluded comparison retained.
- [x] Six final saved formulas and all eighteen data/result values checked through a separate read-only connector.
- [x] Updated [benchmark](docs/benchmark/README.md), [validation](docs/VALIDATION.md), [architecture](docs/ARCHITECTURE.md), [telemetry methods](docs/TELEMETRY.md), [Devpost narrative](docs/DEVPOST_ENTRY.md) and chart.
- [x] Published the revised source and replaced the Devpost judges' evidence ZIP; verified the saved public story, benchmark chart, three teammates and submitted status on **16 October 2026, 15:58 SGT**.

The earlier judges' attachment was **`office-twin-evidence-20261016-193080e.zip`**, 10,105,470 bytes, SHA-256 `30cc679ed4af24b8e1ea414fcb2c6f6c64c0567fd475010adce83b197f29c28b`. It contained source from clean commit [`193080e19a62eab8b3d10197ada50ac0150bf0a6`](https://github.com/ajayasai/office-twin-ntu-st-2026/commit/193080e19a62eab8b3d10197ada50ac0150bf0a6), the existing videos and an artifact manifest. That revision was verified at 15:58 SGT and is preserved locally. The subsequent packages below replace it.

Documentation-only completion records follow each upload. The attached source archive contains its preparation-time status; this page records the verified completion without rebuilding the attachment or changing the tested runtime.

The release packager records its exact source commit, clean/dirty state and artifact hashes in `dist/manifest.json`. The revised runtime tested was `051ec6871425ddaba9faeffed297a2168620e58c`; later reporting/documentation commits do not imply a different tested runtime. The original submitted archive based on `5dd7181317838d9cfa52ba023cf02037539ac5ff` is preserved locally under `runs/submitted-20261016`.

## Guided manual evidence update — 16 October, 16:49 SGT

At this checkpoint, the public story added one participant-reported guided completion, **734.526 seconds**, and links to its [sanitized evidence](docs/manual-practice/README.md). Saved Sheet inputs, six formula sources/results and the recommendation were checked separately. The story disclosed the supplied instructions, formulas, report example and waiting-inclusive duration. No unassisted reference had yet been supplied; the later update below adds it.

That checkpoint's judges' attachment was **`office-twin-evidence-20261016-manual-7eecc49.zip`**, **10,111,965 bytes**, SHA-256 `ba6845d21054cdd5b4c289bcb8b93a53710eab890c400a01a14cc8bdc05015b6`. It contains source from clean commit [`7eecc49e168e37068f00c26e379aee98a5e44a57`](https://github.com/ajayasai/office-twin-ntu-st-2026/commit/7eecc49e168e37068f00c26e379aee98a5e44a57), the same existing videos and a manifest. Package contents and hashes were checked before upload; Devpost readback confirmed the exact saved filename, updated public story and **SUBMITTED** status. The three teammates and leader designation remained visible. No second submission or new terms declaration was created.

## Unassisted human evidence update — 16 October 2026 (SGT)

The saved public story adds a **720-second unassisted human baseline**, including typing, correction, pointer, switching, CPU/RSS and measured process-ancestry results. The participant confirms these are actual measurements of a task performed entirely by a human without guidance. The [baseline documentation](docs/human-baseline/README.md) and [aggregate JSON](docs/human-baseline/aggregate.json) preserve the data and scope. This record is separate from the earlier guided practice; the participant's correction changes the waiting label to “Waiting / idle” without changing its 90 seconds.

At this checkpoint, the confirmed uploaded attachment was **`office-twin-evidence-20261016-human-baseline.zip`**, **10,123,690 bytes**, SHA-256 `edf22cf8b7c1706dcff7eb1ef474aa240ef6c6e32a5df213e24e6d7ad0ec65c1`. It preserves every original entry in the preceding `manual-7eecc49` package and adds the participant-supplied aggregates, update notes and saved story. The runtime and frozen automated benchmark are unchanged. Devpost readback confirmed the human-baseline table and measured ancestry, the replacement attachment, and **SUBMITTED — 5/5 steps done** on 16 October 2026 (SGT). No measurement date is inferred from this upload date.

The tracked documentation was then reconciled with that submitted baseline so the repository's current-state pages no longer say zero unassisted references. Historical benchmark exports retain their original collection scope. A later attachment, if prepared, must be recorded here only after its upload is verified.

## Final presentation review — 16 October 2026 (SGT)

The [judging guide](docs/JUDGING_GUIDE.md) and revised [Devpost narrative](docs/DEVPOST_ENTRY.md) now map evidence to **all four judging criteria**. The review added scoped resource results—median controller CPU **19.14 / 20.61 CPU-s** for fixed/contextual timing and sampled controller peak RSS **72.72–73.09 MiB**—plus explicit measured process-parent counts. Within capture windows, per-run counts sum to **6 Chrome identities with compatible Explorer parents, 33 Chrome children with compatible Chrome parents, and 8 Notepad identities with compatible Explorer parents**. Counts are not globally unique processes; observer overhead and nonexclusive application costs remain separate.

The [revised video](https://youtu.be/oTTT0ECN25U) updates narration and cards to cover the later ten native completions, five matched pairs, **85 passing tests** and participant-confirmed **720-second unassisted human baseline**. It preserves the same continuous 162.13-second **15 October functional recording at 1×** within the 180.13-second edit. The footage is labelled throughout and does not depict the later launch mechanism, benchmark trials or human measurements. Synthetic Microsoft Zira narration remains disclosed. This presentation revision does not add a native runtime trial.

The source documentation and chart now consistently distinguish the unassisted baseline from the earlier guided practice and the automated series. The first final-audit package, **`office-twin-final-evidence-20261016-06a9f31.zip`** (10,281,230 bytes; SHA-256 `1c4f7b0926eecf6923ec5fcfefabc39430e0dce2eace50baaf217b6681f3f81a`), was verified as the saved Devpost attachment. It includes the revised video file and source from clean commit `06a9f31ad89925b988448313be86a22e91c6b4e3`. After the revised video was published as Unlisted, its new URL was reconciled here and in the story; the subsequent final package is recorded below only after its upload is verified.

## Final upload verified — 16 October 2026, 17:54 SGT

The final judges' attachment is **`office-twin-final-evidence-20261016-f89ca68.zip`**, **10,282,378 bytes**, SHA-256 `5a735f6521b6ec36285be8b238c00dd93da40d5c0453c850a5810bc92c05854d`. It contains source from clean commit [`f89ca68628a7330be6aab8250c0cd1e37621516c`](https://github.com/ajayasai/office-twin-ntu-st-2026/commit/f89ca68628a7330be6aab8250c0cd1e37621516c), the original continuous recording, the revised narrated video and a manifest with matching file hashes and the new published video URL. ZIP integrity passed; all 14 runtime Python files match the frozen tested version after line-ending normalization. Private settings and raw local runs are excluded.

Devpost readback confirmed the exact saved filename and **SUBMITTED — 5/5 steps done**. The public page displays the revised criterion table, human measurements, CPU/RSS results, process-parent counts and three teammates, and embeds the new video `oTTT0ECN25U`. YouTube confirmed **Video published** after Unlisted was selected; the public watch link opened and playback began. Copyright and Community Guidelines checks reported no issues. This completion record follows the verified upload and is not part of the archived source preparation snapshot.

## Process-event and reproduction supplement prepared — 16 October 2026 (SGT)

The [new ETW evidence](docs/process-events/README.md) verifies **28/28 known process lifecycles**, the validation worker, both native controllers, and a separate fixed/contextual pair completing **11/11 steps each**. The 393.982-second capture contains 344 process-provider records; all three final loss counters are zero. Twenty-four known processes lived under 100 ms. The native pair ran from clean source `09e4b83824b8b0bec4348be0dbae2bcdef1f62dc`; the application runtime is unchanged from the earlier benchmark.

The explicitly nonexclusive application cohort includes 14 Chrome and four Notepad start records inside the native windows, plus 18 stop records; equal counts do not imply paired lifetime identities. Three Chrome parent chains resolve to ETW lifetimes; 15 further parent-ID comparisons are labeled separately. The main applications predate capture, so all 33 focus-to-ETW-lifetime bindings remain unresolved. The failed first attempt remains documented. These results do not establish universal process-event completeness and are not pooled into the original performance comparison.

The current suite passes **120 tests**. A [fresh-environment check](docs/reproduction/README.md) independently recreated dependencies from PyPI and passed the earlier frozen source's 85 tests plus two simulation plans on this same machine. It does not establish native portability to another device. The published video predates this supplement and remains unchanged.

At this preparation checkpoint, the new source and evidence are ready for packaging; the previously verified Devpost attachment is still the `f89ca68` package above. A completion record will identify the replacement only after the saved filename and submitted status are read back.

The prepared replacement is **`office-twin-etw-evidence-20261016-9b9e37b.zip`**, **10,348,722 bytes**, SHA-256 `0979755b59a737bd0a8540e88a4560df8c95a2452d57332d2ef3e213a5e019a8`. It contains clean source commit [`9b9e37bb50115ff08e6a94712ec97c1ed731d972`](https://github.com/ajayasai/office-twin-ntu-st-2026/commit/9b9e37bb50115ff08e6a94712ec97c1ed731d972), the existing video files and their manifest. ZIP integrity, every artifact hash, all 14 unchanged runtime files, required evidence and exclusion of private runs were checked. Source was pushed to GitHub. **Devpost replacement upload is pending:** its editor presented a human-verification challenge, for which user approval was requested. This is not a verified upload record.

## ETW supplement upload verified — 16 October 2026, 19:22 SGT

Devpost now saves **`office-twin-etw-evidence-20261016-9b9e37b.zip`**, **10,348,722 bytes**, SHA-256 `0979755b59a737bd0a8540e88a4560df8c95a2452d57332d2ef3e213a5e019a8`, as the judges' attachment. The exact filename was read back from Additional info after saving, and the finalization page displayed **Project submitted! — SUBMITTED — 5/5 steps done**. This replaces the earlier `f89ca68` package; its preparation-time source is clean commit `9b9e37bb50115ff08e6a94712ec97c1ed731d972`.

The public story was saved from the packaged `docs/DEVPOST_ENTRY.md` and read back on the live project page. It displays the four-criterion table, verified ETW result, 120-test suite, fresh-environment result, preserved failed attempt and explicit application-ancestry limits. The participant-confirmed unassisted measurements remain unchanged. The historical benchmark image caption now distinguishes its 85-test checkpoint from the later ETW evidence and current suite. The page retains all three teammates and embeds the existing revised video `oTTT0ECN25U`. No new terms declaration or second submission was created.

The user completed the browser's human-verification step. Public-page, saved-attachment and submitted-status screenshots are retained locally. This completion record follows the verified upload and is not part of the archived preparation snapshot.

## Media and links

- [Devpost entry](https://devpost.com/software/office-twin).
- [Public GitHub source](https://github.com/ajayasai/office-twin-ntu-st-2026).
- [Revised narrated YouTube demo](https://youtu.be/oTTT0ECN25U), 180.13 seconds; updated evidence narration/cards around the continuous historical recording at 1×.
- [Earlier narrated version](https://youtu.be/0OpIetkSomM), retained as the historical published edit.

The three joined teammates and rules/Terms declaration were confirmed before the original submission. Updating the existing entry does not create a new team or a second submission.

Current repository evidence comprises the ten-run automated comparison, the separate bounded ETW validation, the fresh-environment installation check, the participant-confirmed unassisted aggregate baseline and the earlier guided practice with separately verified outputs. Human raw input/resource/process traces and matching capture definitions were not supplied, so no human timing calibration or agent-versus-human speed ratio is inferred. No human similarity, universal process-event coverage, whole-system efficiency or official score is claimed. Optional native Excel/Word support remains untested. AI assistance is disclosed; no private organizer brief has been supplied.

## Rundown evidence upload verified — 16 October 2026, 20:00 SGT

The current judges' attachment is **`office-twin-rundown-evidence-20261016-4b8d11a.zip`**, **10,382,895 bytes**, SHA-256 `f6b708a0e663132b91bce94d7ee9c540806c98545f7bcb7c7e86ae002ceb0caf`. It contains source from clean commit [`4b8d11a019e733ceaa9f3110943ac392181223b7`](https://github.com/ajayasai/office-twin-ntu-st-2026/commit/4b8d11a019e733ceaa9f3110943ac392181223b7), both existing videos and matching manifest hashes. ZIP integrity, public-evidence privacy and the unchanged 14 runtime files were verified before upload.

Devpost readback confirmed the exact saved filename and **SUBMITTED — 5/5 steps done**, with all three teammates present. The saved story exactly matches packaged `docs/DEVPOST_ENTRY.md` after newline normalization (22,198 characters; SHA-256 `fde81f811611cdbee63e9982735bac13065fc09048dc80322847e8570cd6678d`). The public story displays 32/32 focus observations, 16 resolved application-start parents, 28/28 canaries, both 11-step tasks, 139 passing tests and the original-parent limitation. Its image caption distinguishes the historical 85-test benchmark from the latest results; the video URL remains `https://youtu.be/oTTT0ECN25U` and its historical scope is explicit.

The new evidence is also publicly available in the repository. This documentation-only completion record follows the verified upload; the attached preparation snapshot is not rebuilt or relabelled. Raw traces remain private, and failed attempts and participant-reported human aggregates remain intact.
