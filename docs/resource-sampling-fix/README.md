# Resource-sampling fix — 16 October 2026

The current controller resource recorder passes **144 automated tests** and a separate **19/19-check noninteractive Windows integration probe**. Existing Chrome, Notepad and Explorer applications were left open. No office-task input, new human run, input hooks or ETW capture occurred. The participant-confirmed [unassisted human baseline](../human-baseline/README.md) is unchanged.

## What changed

`EvidenceRecorder` previously enumerated cached `psutil.process_iter` objects. A process ID reused between enumeration and measurement could mix a stale name/creation time with a new process's CPU or memory counters. A failed parent lookup did not reliably reject that mixed observation.

The recorder now uses one Windows Toolhelp inventory to find candidates, fresh process objects for measurements, and a second fresh creation-time check after reading counters. A process born after inventory began is skipped. Descendant membership uses PID plus creation time; a reused descendant PID alone does not select an unrelated process. Parent identity has its own fresh recheck. An inaccessible or incompatible parent stays unresolved while valid child counters remain usable.

Five added regression cases cover PID reuse during reads, exit/access races, stale inventory metadata, descendant reuse and parent reuse. They supplement existing tests of resource scope, baseline subtraction and recorder lifecycle. This is an attribution-correctness change, not a measured CPU, memory or task-speed improvement.

## Recorded live check

The [allowlisted integration summary](integration-summary.json) records all 19 checks, measured endpoints, source hashes and limitations. A temporary Python worker touched 32 MiB of memory and performed bounded CPU work before and during sampling:

| Check | Observed result |
| --- | --- |
| Pre-sampling CPU excluded from measured delta | 0.65625 CPU-seconds |
| First-to-last sampled CPU increase | 0.78125 CPU-seconds |
| Increase from separate fresh OS readings | 0.78125 CPU-seconds |
| Worker observations | 9 |
| Worker peak sampled RSS | 56,590,336 bytes |
| Existing identities readable before/after and matched to sampler | 37: 36 Chrome, 1 Notepad |
| Recorder window | 3.2366833 seconds |
| Monitor errors | 0 |
| Worker exit and recorder thread shutdown | Passed |

Direct and recorder readings use the same Windows counter interface through psutil; these are cross-checks, not an independent audit. No PID reuse was forced in this live probe: regression tests cover those races. Sampling can miss brief processes and memory peaks. Application cohorts are warm, shared and nonexclusive, and the stability check covers identities readable at both boundaries.

The first attempt failed its workload assertions because the probe selected the Windows virtual-environment launcher PID instead of the actual worker descendant. The recorder captured both identities correctly. The corrected probe checks the worker's exact PID and creation time against the owned launcher's descendant tree. The failed attempt is retained privately with its hashes and explanation in the public summary.

## Source and evidence provenance

- [Test log](tests.log) and [test provenance](test-provenance.json) record the exact tested source commit, duration and source hashes. Runtime digests use the raw-byte `run_benchmark.code_digest` convention; file hashes also bind all test/tool sources.
- The live probe ran on `ebbf792` plus the uncommitted fix, later committed as `da9323415987a481679a1c1bc027948e2bb653c3`. The summary retains that original state and patch hash. Its `evidence.py` and `observer.py` hashes exactly match the published implementation.
- [Exact probe source](integration-probe.py.txt) is included for inspection and reproduction, with SHA-256 `0b6515f140e268fbce45c05ce8f4d349e57d21c0e9c5ff6ee3daa90096b2af19`. Raw process IDs and private logs are excluded from the public export.
- [Preserved evidence hashes](preserved-evidence-sha256.json) bind the unchanged human baseline, historical benchmark and rundown evidence. The human section in the Devpost story is also preserved, including the participant-reported measured ancestry.
- Of 14 application runtime modules, only `office_twin/evidence.py` differs from historical native benchmark `051ec6871425ddaba9faeffed297a2168620e58c` after CRLF-to-LF normalization. The native benchmark's performance results and the later ETW captures retain their original code versions. No native office workflow was rerun for this fix.

## Reproduce without restarting applications

Use a full Git checkout on Windows with Git for Windows, Python and the pinned dependencies installed as in the [main setup](../../README.md). Keep an existing Chrome and Notepad process open. First run the automated suite:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The exact historical probe expects its script at `runs/<group>/<fresh-directory>/probe.py` so its repository-root calculation remains valid. From the repository root, copy it into a new directory and run it:

```powershell
$probeDirectory = Join-Path (Get-Location) ('runs\resource-probes\' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $probeDirectory | Out-Null
Copy-Item -LiteralPath 'docs\resource-sampling-fix\integration-probe.py.txt' -Destination (Join-Path $probeDirectory 'probe.py')
& '.venv\Scripts\python.exe' (Join-Path $probeDirectory 'probe.py')
```

It samples existing processes and starts only an owned, bounded Python workload. It performs no desktop input or app restart. Inspect the generated private report's `checks` and final pass status; new numeric values need not equal this recorded run. The exact historical probe's failure cleanup terminates its owned launcher; a worker descendant may finish only when its bounded 15-second marker wait expires. Use a fresh directory every time and keep generated raw process records private.
