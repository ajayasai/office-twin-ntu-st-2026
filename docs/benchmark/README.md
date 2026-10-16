# Revised benchmark — 16 October 2026

**The revised series completed 10 of 10 native tasks, each with 11/11 steps, yielding five comparable fixed/contextual pairs.** Fixed task duration had a median of **153.13 s** (range 152.24–158.99); contextual duration had a median of **167.08 s** (158.78–169.35). The within-pair contextual-minus-fixed difference had a median of **+11.26 s**, ranging from +5.55 to +17.10 s. These are descriptive results on one warm, shared Windows host, not a population reliability or significance claim.

Each run recorded 586 single-key controller waits. Across runs, their 90th percentiles were **109.50–110.08 ms for fixed** and **161.01–177.73 ms for contextual**. This establishes measured policy variation and its cost; the waits are not OS input-delivery timestamps and do not validate human behavior.

The separate observer collected **17,018 snapshots**. Per-run median gaps were 100.39–100.44 ms; the largest gap was **510.89 ms**, with one overrun. It observed eight per-run Notepad identities created within capture windows with compatible Explorer parents, and ten preexisting Notepad observations with unresolved parents. No Notepad-to-Python parent was observed in this revised series. Reused warm processes can appear in multiple runs; polling can miss short-lived processes, so these counts do not prove complete launch coverage.

Final read-only Sheet inspection confirmed all six formulas and their saved values, supporting Atlas at SGD 600. That separate formula-source inspection applies to the last saved Sheet; every native trial additionally passed its runtime displayed-value and saved-report checks.

![Paired task durations and measured controller waits](../media/benchmark.png)

## Scope and version

Runtime commit: `051ec6871425ddaba9faeffed297a2168620e58c`. Five seed pairs (211, 223, 227, 229, 233), scale 1, default scenario, no screen recording. Fixed/contextual order reverses in alternate pairs. All pairs passed the analyzer's declared-version, scenario, action-sequence, capture and completion checks. The runtime and measurement source hashes are retained in the JSON export. Each run contains 622 timing events with the same kind/unit sequence.

No human participant was available: **human reference n=0**. This is an automated policy comparison. No official score or human-authenticity result is inferred.

## Resource scope

Full-window controller CPU medians were 19.14 CPU-s (fixed) and 20.61 CPU-s (contextual). Sampled controller peak RSS ranged from 72.72 to 73.09 MiB across all ten runs. These omit Chrome and Notepad. Separate application cohorts include unrelated activity and shared memory; their sampled CPU/RSS must not be presented as exclusive whole-task costs or added across overlapping scopes.

The observer itself used 38.36–65.88 CPU-s and 26.45–29.28 MiB peak sampled RSS per capture. Its overhead is measured separately and is part of the benchmark setup. The 100 ms target is not guaranteed: the worst observed gap is reported above.

## Inspect the evidence

- [Full numeric report](BENCHMARK.md) and [machine-readable export](benchmark.json).
- [Sampled parent relationships and process observations](process-parent-evidence.md), with [JSON](process-parent-evidence.json).
- [Separate final saved-Sheet formula and value check](saved-sheet-verification.json).
- [Protocol](../EVALUATION.md), [telemetry definitions and reproduction commands](../TELEMETRY.md), and [historical validation](../VALIDATION.md).
- [Retained initial series](../benchmark-initial/README.md): three successful tasks, zero comparable pairs; six Notepad-to-Python observations prompted the actual Explorer launch change. This earlier version is not pooled into the revised results.

Raw records remain local. Public exports contain synthetic task values, fixed application-role labels, pseudonyms and numeric measurements, excluding account paths, spreadsheet identifiers, command lines and raw process IDs. The video remains the 15 October functional demonstration; it is not a recording of this revised benchmark.
