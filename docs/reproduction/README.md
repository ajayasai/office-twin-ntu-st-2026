# Fresh-environment reproduction — 16 October 2026

**Installation, dependency checks, 85 tests, and both 11-step simulation plans passed in a newly created virtual environment.** This verification used the same physical Windows machine and base Python installation as the native benchmark. It establishes a fresh dependency installation from committed source; it is not a second-device or clean-Windows result.

The source was frozen from clean commit [`5d3e0100f652f424fed5653ac78b2ffdae0256e5`](https://github.com/ajayasai/office-twin-ntu-st-2026/commit/5d3e0100f652f424fed5653ac78b2ffdae0256e5) before later process-event tooling was added. The new environment did not reuse the project's existing virtual environment or installed packages. Installation used the repository's `requirements.txt`, constrained to the existing environment's five exact package versions, with `--isolated`, `--no-cache-dir`, and the explicit `https://pypi.org/simple` index.

| Check | Observed result |
| --- | --- |
| Python and OS | Python 3.14.2; Windows 11 build 26200 |
| Fresh install | All five constrained dependencies installed successfully from PyPI |
| Dependency consistency | `pip check` passed |
| Environment check | Doctor found `tkinter`, `pywinauto` and `psutil` |
| Automated suite | 85 tests passed; zero failed |
| Default Sheets simulation | 11/11 planned steps; `plan_completed`; `native_verified=false` |
| Alternate Sheets simulation | 11/11 planned steps; `plan_completed`; `native_verified=false` |
| Collection interval | 16 October 2026, 17:59:47–18:00:56 SGT |

The simulations used timing scale zero to check orchestration without native desktop input. Their generated result explicitly says output correctness was not tested. They do not add two native completions to the benchmark or establish that the spreadsheet, browser login or UI would work on another machine. The 85-test result applies to the frozen source above; it does not validate later-added process-event collection tools.

## Inspect the retained evidence

- [Machine-readable reproduction record](reproduction.json): commit, timestamps, environment, dependency versions, command results, simulation run IDs and hashes.
- [Pinned dependency constraints](constraints.txt): `comtypes==1.4.17`, `psutil==7.2.2`, `pywin32==312`, `pywinauto==0.6.9`, and `six==1.17.0`.
- [Doctor output](doctor.json) and [complete test output](tests.log).

The source ZIP SHA-256 is `dc179f9ee61c339e23f14a64407af5e4689f0d0f6dafeb489ba6723951544269`. The original private manifest SHA-256 is `5e9f2b6bb3239e14e4c140f0d6fa9340960651565bc5dbd13dcfd7c33389cca3`. Source ZIP integrity, all recorded command-log hashes, both raw simulation-summary hashes and the equality of installed versus constrained package versions were checked after completion.

Public files use an explicit field selection. The two temporary-directory prefixes emitted by the benchmark export test are replaced with `<TEMP>` in `tests.log`; the original log is retained separately and hashed. Public command hashes refer to the original private logs, while `published_files` hashes identify the public files. No local account paths, Sheet identifiers, raw process IDs or browser content are included. Hashes establish artifact consistency, not independent certification of the measurements.

## Repeat the check

These commands reproduce the checked source and command parameters with fresh local output paths. Run them from the repository root of a **full Git clone**, with Git for Windows on `PATH` and **Python 3.14.2** installed; see [the clone instructions](../../README.md#run). The judges' source ZIP lacks Git history, and a shallow clone may lack the frozen commit used by `git archive` below. The `py -3.14` selector must resolve to that patch version for an exact Python-version match. This current documentation directory supplies the constraints file; it was added after the frozen source commit.

```powershell
$reproRoot = Join-Path (Get-Location).Path 'runs\reproduction-check-20261016'
if (Test-Path -LiteralPath $reproRoot) { throw 'Choose a new reproduction output directory.' }
New-Item -ItemType Directory -Path $reproRoot | Out-Null
$reproSource = Join-Path $reproRoot 'source'
$reproVenv = Join-Path $reproRoot 'venv'
$reproZip = Join-Path $reproRoot 'source-snapshot.zip'
$reproPins = Join-Path $reproRoot 'constraints.txt'
Copy-Item -LiteralPath 'docs\reproduction\constraints.txt' -Destination $reproPins
git archive --format=zip --output $reproZip 5d3e0100f652f424fed5653ac78b2ffdae0256e5
Expand-Archive -LiteralPath $reproZip -DestinationPath $reproSource
py -3.14 -m venv $reproVenv
$reproPython = Join-Path $reproVenv 'Scripts\python.exe'
Set-Location -LiteralPath $reproSource
& $reproPython --version
& $reproPython -m pip --isolated install --no-cache-dir --index-url https://pypi.org/simple -r requirements.txt -c $reproPins
& $reproPython -m pip check
& $reproPython -m pip freeze
& $reproPython -m office_twin --doctor
& $reproPython -m unittest discover -s tests -v
& $reproPython -m office_twin --mode simulate --workflow sheets --timing contextual --seed 42 --scale 0 --output (Join-Path $reproRoot 'simulation-default')
& $reproPython -m office_twin --mode simulate --workflow sheets --timing contextual --seed 101 --scale 0 --scenario scenarios/alternate.json --output (Join-Path $reproRoot 'simulation-alternate')
```

Check each command's exit code and preserve failed attempts rather than replacing them. The local verification driver recorded each exit code and stopped on the first failure; all commands in this retained attempt exited zero. A second-machine native run and raw, matched human input measurements remain separate evidence needs.
