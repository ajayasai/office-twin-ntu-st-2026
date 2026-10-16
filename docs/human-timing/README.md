# Human-informed requested key timing

Office Twin now offers an optional `human-informed` timing policy using the participant's existing **unassisted human measurements**. It changes requested pre-key delays while preserving the legacy `contextual` and `fixed` modes, their defaults and seeded sequences. No new human task, native workflow, application restart or input capture was performed for this update.

## What is fitted

The supplied [baseline](../human-baseline/README.md) reports inter-key mean **200 ms**, median **170 ms** and p90 **350 ms**. Its [original JSON](../human-baseline/aggregate.json) remains byte-for-byte unchanged, with SHA-256 `a18df6f37bb963db97acd371ccc7d2991ca746d9d300c69dbe7b3b3b2aba5976`.

The new key-delay distribution is lognormal: `mu = ln(0.170)` and `sigma = ln(0.350 / 0.170) / NormalDist().inv_cdf(0.9) = 0.563484714`. Median and p90 determine these two parameters. The mean is an unused aggregate consistency check: the unclipped model predicts **199.249 ms**, **0.751 ms (0.376%) below** the reported 200 ms. It is not an independent human validation set.

Each draw is clipped to **5–2,000 ms** as an engineering safeguard. These bounds are not claimed as observed human extrema. Key draws use a separate seeded random stream, so intervening reading/review actions do not change their sequence. The model assumes independent key-delay samples; human serial dependence cannot be inferred from the summaries. Remaining action types retain engineering defaults. Scale 1 is required for the stated targets; scale 0 explicitly disables waits for plan checks.

## Automatic verification

The [verification program](../../tools/verify_human_timing.py) generates 100,000 requested key delays for each of five predefined seeds (211, 223, 227, 229, 233), for both legacy contextual and human-informed modes: **1,000,000 synthetic samples total**. It checks each human-informed seed's mean, median and p90 against a predefined 3% relative-error threshold, and checks that each target error is lower than the corresponding legacy error. Quantiles use linear interpolation at `(n - 1) * p`. No samples are labelled as recorded human keystrokes or delivered native input.

**Result: all five seeds pass; all 15 mean/median/p90 checks are within 0.61% of the supplied targets and closer than the corresponding legacy-policy statistics. All 172 software tests pass** (9.841 seconds reported by unittest), from clean source `db808d703af3ae146c8a089e8a4dc9497b0d89ae`.

| Statistic | Supplied human aggregate | Legacy contextual generated range | Human-informed generated range |
| --- | ---: | ---: | ---: |
| Mean | 200 ms | 104.525–105.006 ms | 198.797–199.704 ms |
| Median | 170 ms | 96.947–97.452 ms | 169.442–169.920 ms |
| p90 | 350 ms | 154.371–155.554 ms | 349.104–351.707 ms |

Ranges span the five predefined seeds, not confidence intervals. Both model columns are generated requested delays, not the historical native benchmark's measured controller waits.

See [all per-seed results and provenance](verification.json), [automated test log](tests.log) and [test-source hashes](test-provenance.json). The suite also checks preserved baseline hashes, unchanged legacy sequences, separate key streams, unit/scaling behavior, cancellation before dispatch, and routing through the existing text executor with native input replaced by test doubles. An 11-step Sheets plan test blocks native backend imports. A separate [CLI plan check](plan-check.json) completed 11/11 plan steps at scale 0, explicitly reporting `native_verified: false`; neither performs desktop input.

## Reproduce without touching applications

From the repository root after the [documented installation](../../README.md#run):

```powershell
.\.venv\Scripts\python.exe tools/verify_human_timing.py --output-dir runs/human-timing-check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m office_twin --mode simulate --workflow sheets --timing human-informed --scale 0 --output runs/human-timing-plan
```

For a future authorised desktop task, select `human-informed` in the control panel or add `--timing human-informed --scale 1` to the documented desktop command. The optional policy was not used in the retained native benchmark. Historical performance and ETW results retain their original source versions; their measurements have not been recomputed or relabelled.

## What this does and does not verify

This verifies implementation and aggregate-target consistency of requested controller delays. The human record lacks raw timestamps, eligible-key definitions and pause-exclusion rules. The executor waits before sending a key; focus checks, application/API work and OS scheduling add to delivered intervals. The baseline is used as a numerical design target, not as proof that these differently defined quantities measure the same thing.

The supplied **100 ms key-hold mean is not implemented or verified**: the existing input API sends key down/up together. The 18 pauses, 150-second combined pause time, 14 corrected errors, mouse metrics and phase durations remain reported measurements, not inferred event schedules. Their overlap and event definitions are insufficient to reconstruct a timeline. We do not add pauses to the 720-second total, force the workload to last 12 minutes, compute a human/agent speedup, or claim human indistinguishability or an official score.

The original human reference page's historical “not a timing calibration” description remains preserved with that record. This later, separately versioned profile is its first use as a timing-design target. Matching supplied aggregate targets is an improvement in model grounding; native delivered timing and generalisation beyond this participant remain unverified.
