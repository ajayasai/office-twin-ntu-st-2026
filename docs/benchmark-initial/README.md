# Initial telemetry observations — 16 October 2026

These three native trials used commit `0d04ae77d33301b0c614289486355753ce8c8dff`. All completed eleven steps and saved-output checks. Only the first two form a complete fixed/contextual pair; the third is retained as an unpaired attempt.

The new observer exposed six Notepad process identities with Python parentage and OS creation timestamps within the observation windows (two per trial). Chrome also had sampled Explorer-parent relationships. These are real sampled observations, not reconstructed process-start events.

This finding prompted a change from direct file association invocation in Python to a visible Explorer double-click for opening and reopening the report. The running trial finished on its already-loaded version. The harness then stopped before another trial when its source-digest guard detected the revision. No trial result was removed or relabelled as a failure.

These measurements are historical evidence for the launch-mechanism change. The revised-version benchmark is reported separately. Human reference runs remain zero. Shared application cohorts include unrelated activity.

- [Timing and resource observations](BENCHMARK.md)
- [Sampled parent relationships and pseudonymized observations](process-parent-evidence.md)
