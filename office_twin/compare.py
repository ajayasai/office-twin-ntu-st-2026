"""Compare observed runs without inventing human data or authenticity scores.

Usage: python -m office_twin.compare RUN_DIR RUN_DIR --output comparison.html
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import html
import json
import hashlib
import math
from pathlib import Path
import statistics


def _escape(value) -> str:
    return html.escape(str(value), quote=True)


def _numeric(value):
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) and number >= 0 else None
    except (TypeError, ValueError):
        return None


def _format(value, suffix="", precision=3):
    value = _numeric(value)
    return "Unavailable" if value is None else f"{value:,.{precision}f}{suffix}"


def _load_run(path: Path) -> dict:
    warnings = []
    try:
        summary = json.loads((path / "summary.json").read_text(encoding="utf-8-sig"))
        if not isinstance(summary, dict):
            raise ValueError("summary is not an object")
    except (OSError, ValueError) as exc:
        summary = {}
        warnings.append(f"Summary unavailable: {exc}")
    events = []
    try:
        with (path / "events.jsonl").open(encoding="utf-8-sig") as handle:
            for line in handle:
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    if isinstance(event, dict):
                        events.append(event)
                    else:
                        warnings.append("Skipped an event that was not an object.")
                except ValueError:
                    warnings.append("Skipped a malformed event record.")
    except OSError as exc:
        warnings.append(f"Events unavailable: {exc}")
    config = summary.get("config", {})
    config = config if isinstance(config, dict) else {}
    timing = summary.get("timing", summary.get("timing_policy", {}))
    timing = timing if isinstance(timing, dict) else {}
    resources = summary.get("resources", {})
    resources = resources if isinstance(resources, dict) else {}
    if not resources:
        resources = next((e["resources"] for e in reversed(events) if isinstance(e.get("resources"), dict)), {})
    backend = str(summary.get("backend", config.get("mode", "unknown")))
    backend = "simulation" if backend.lower() in {"simulate", "simulation", "sim", "dry-run"} else backend
    timings = defaultdict(lambda: {"requested": [], "actual": [], "interrupted": 0})
    for event in events:
        if event.get("event") not in {"timing", "delay", "pause"}:
            continue
        kind = str(event.get("timing_kind", event.get("kind", "unspecified")))
        requested = _numeric(event.get("delay_seconds", event.get("requested_delay_seconds", event.get("seconds"))))
        actual = _numeric(event.get("actual_wait_seconds"))
        if requested is not None:
            timings[kind]["requested"].append(requested)
        if actual is not None:
            timings[kind]["actual"].append(actual)
        if event.get("interrupted") is True:
            timings[kind]["interrupted"] += 1
    scenario_hash = summary.get("scenario_sha256", "unknown")
    if scenario_hash == "unknown":
        scenario_path = summary.get("artifacts", {}).get("scenario")
        if scenario_path and Path(scenario_path).is_file():
            scenario_hash = hashlib.sha256(Path(scenario_path).read_bytes()).hexdigest()
    return {
        "path": str(path.resolve()), "label": str(summary.get("run_id", path.name)),
        "summary": summary, "backend": backend, "workflow": str(config.get("workflow", summary.get("workflow", "unknown"))),
        "policy": str(timing.get("mode", config.get("timing", "unknown"))),
        "seed": timing.get("seed", config.get("seed", "unknown")),
        "scale": timing.get("scale", config.get("scale", "unknown")),
        "status": str(summary.get("status", "unknown")), "success": summary.get("success"),
        "scenario_hash": str(scenario_hash), "capture": "recorded" if summary.get("screen_recording") else "not recorded",
        "resources": resources, "events": len(events), "timings": dict(timings), "warnings": warnings,
    }


def generate_comparison_report(run_dirs, output: Path) -> Path:
    """Write a portable HTML report preserving run and backend boundaries."""
    supplied_paths = [Path(path).resolve() for path in run_dirs]
    paths = list(dict.fromkeys(supplied_paths))
    if not paths:
        raise ValueError("Provide at least one run directory")
    output = Path(output)
    if output.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("Comparison output must have an .html or .htm extension")
    runs = [_load_run(path) for path in paths]
    run_rows, timing_rows, scope_rows, warnings = [], [], [], []
    if len(paths) < len(supplied_paths):
        warnings.append(f"Excluded {len(supplied_paths) - len(paths)} repeated directory argument(s); each source directory is counted once.")
    groups = defaultdict(list)
    for index, run in enumerate(runs, 1):
        summary, resources = run["summary"], run["resources"]
        groups[(run["backend"], run["workflow"], run["policy"], str(run["scale"]), run["scenario_hash"], run["capture"])].append(run)
        short = f"R{index}"
        success = "Yes (declared)" if run["success"] is True else "No" if run["success"] is False else "Not declared"
        completed = f'{summary.get("steps_completed", "?")}/{summary.get("steps_total", "?")}'
        peak_rss = _numeric(resources.get("controller_peak_rss_bytes"))
        run_rows.append(f'<tr><td><strong>{short}</strong><small>{_escape(run["label"])}</small></td><td>{_escape(run["backend"])}<small>{_escape(run["workflow"])}</small></td><td>{_escape(run["policy"])}<small>seed {_escape(run["seed"])} · scale {_escape(run["scale"])}</small></td><td>{_escape(run["status"])}<small>Success: {success}</small></td><td>{_escape(completed)}<small>{run["events"]} events</small></td><td>{_format(resources.get("controller_cpu_seconds"), " s")}</td><td>{_format(resources.get("wall_seconds"), " s")}</td><td>{_format(None if peak_rss is None else peak_rss / 1048576, " MiB", 1)}</td></tr>')
        for kind, series in sorted(run["timings"].items()):
            requested, actual = series["requested"], series["actual"]
            requested_mean = statistics.mean(requested) if requested else None
            actual_mean = statistics.mean(actual) if actual else None
            requested_range = "Unavailable" if not requested else f'{min(requested):.3f}–{max(requested):.3f} s'
            actual_range = "Unavailable" if not actual else f'{min(actual):.3f}–{max(actual):.3f} s'
            timing_rows.append(f'<tr><td>{short}</td><td>{_escape(kind)}</td><td>{len(requested)}</td><td>{_format(requested_mean, " s")}<small>{requested_range}</small></td><td>{len(actual)}</td><td>{_format(actual_mean, " s")}<small>{actual_range}</small></td><td>{series["interrupted"]}</td></tr>')
        scope = resources.get("measurement_scope", "Measurement scope not supplied; do not assume whole-system CPU or memory.")
        scope += f" Scenario SHA256: {run['scenario_hash']}. Screen capture: {run['capture']}."
        scope_rows.append(f'<div class="scope"><h3>{short} · {_escape(run["label"])}</h3><p>{_escape(scope)}</p><small>Monitor: {_escape(resources.get("monitor_backend", "unknown"))}</small><small>Source: {_escape(run["path"])}</small></div>')
        warnings.extend(f'{short}: {warning}' for warning in run["warnings"])
    group_rows = []
    for (backend, workflow, policy, scale, scenario_hash, capture), members in sorted(groups.items()):
        success_count = sum(run["success"] is True for run in members)
        undeclared = sum(run["success"] is not True and run["success"] is not False for run in members)
        group_rows.append(f'<tr><td>{_escape(backend)}<small>{_escape(capture)}</small></td><td>{_escape(workflow)}<small>scenario {_escape(scenario_hash[:12])}</small></td><td>{_escape(policy)}</td><td>{_escape(scale)}</td><td>{len(members)}</td><td>{success_count}/{len(members)}<small>{undeclared} undeclared</small></td></tr>')
    warnings_html = "".join(f"<li>{_escape(warning)}</li>" for warning in warnings)
    if warnings_html:
        warnings_html = f'<section class="panel"><h2>Input warnings</h2><ul>{warnings_html}</ul></section>'
    backends = {run["backend"] for run in runs}
    combined = "Mixed execution backends are present. Simulation and desktop runs are displayed separately and must not be pooled as task-success or native-performance evidence." if len(backends) > 1 else "All supplied runs declare the same backend. This alone does not establish equivalent tasks, environment or verification."
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'"><title>Office Twin · Run comparison</title>
<style>:root{{color-scheme:dark;--bg:#0b1220;--card:#141f31;--line:#2b3b52;--text:#eef5ff;--muted:#b0bfd2;--accent:#55dbc2}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}}main{{max-width:1280px;margin:auto;padding:50px 25px 80px}}.eyebrow{{letter-spacing:.17em;color:var(--accent);font-size:12px;font-weight:800}}h1{{font-size:clamp(32px,5vw,52px);letter-spacing:-.035em;line-height:1.1;margin:14px 0 20px}}h2{{font-size:23px;margin:0 0 12px}}h3{{font-size:16px;margin:0 0 8px}}p{{margin:8px 0}}.lede{{color:var(--muted);font-size:17px;max-width:900px}}.banner{{border-left:3px solid #ffd18b;background:#251f1b;padding:16px 22px;margin:25px 0;border-radius:0 12px 12px 0;color:#f4dbb6}}.panel{{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:25px;margin:22px 0}}.muted,small{{color:var(--muted)}}small{{display:block;font-size:11px;overflow-wrap:anywhere}}.table-wrap{{overflow:auto}}table{{border-collapse:collapse;width:100%;font-size:13px}}th{{text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}}th,td{{padding:12px 10px;border-bottom:1px solid var(--line);vertical-align:top}}th:first-child,td:first-child{{padding-left:0}}tr:last-child td{{border-bottom:0}}.scope{{margin:20px 0;padding-bottom:15px;border-bottom:1px solid var(--line)}}.scope:last-child{{border:0;padding-bottom:0}}.scope p{{color:var(--muted);font-size:13px}}ul{{padding-left:22px;color:var(--muted)}}li{{margin:9px 0}}footer{{color:var(--muted);font-size:12px;margin-top:25px}}@media(max-width:700px){{main{{padding:28px 14px}}.panel{{padding:17px}}}}@media print{{:root{{color-scheme:light;--bg:white;--card:#f4f6f8;--line:#c3cbd3;--text:#172436;--muted:#43546a;--accent:#146859}}main{{padding:10px}}}}</style></head><body><main>
<div class="eyebrow">OFFICE TWIN / OBSERVED RUN COMPARISON</div><h1>Compare the evidence.</h1><p class="lede">{len(runs)} supplied run(s). Every result retains its execution mode, task, timing scale and completion state. No human data, authenticity scores or efficiency rankings are synthesized.</p><div class="banner">{combined}</div>
<section class="panel"><h2>Every run, including failures</h2><p class="muted">Success is the run's declared result. Simulation success means plan replay only. Fewer CPU-seconds on an incomplete task do not demonstrate greater efficiency.</p><div class="table-wrap"><table><thead><tr><th>Run</th><th>Execution/task</th><th>Timing</th><th>Outcome</th><th>Steps/events</th><th>Controller CPU</th><th>Wall time</th><th>Sampled peak RSS</th></tr></thead><tbody>{''.join(run_rows)}</tbody></table></div></section>
<section class="panel"><h2>Counts within declared configurations</h2><p class="muted">Groups separate backend, workflow, policy and speed scale. Small samples and reused scenarios do not establish general reliability. Environmental equivalence is not verified.</p><div class="table-wrap"><table><thead><tr><th>Backend</th><th>Workflow</th><th>Policy</th><th>Scale</th><th>Runs</th><th>Declared success</th></tr></thead><tbody>{''.join(group_rows)}</tbody></table></div></section>
<section class="panel"><h2>Timing, conditioned on action kind</h2><p class="muted">Means and ranges are descriptive. Requested policy delays and measured controller waits are separate. Actual waits include scheduling overhead and may be shortened by cancellation; neither is a measurement of native input delivery or a human reference distribution.</p><div class="table-wrap"><table><thead><tr><th>Run</th><th>Kind</th><th>Requested n</th><th>Requested mean/range</th><th>Actual n</th><th>Actual wait mean/range</th><th>Interrupted</th></tr></thead><tbody>{''.join(timing_rows) or '<tr><td colspan="7">No timing observations available.</td></tr>'}</tbody></table></div></section>
<section class="panel"><h2>How to interpret this comparison</h2><ul><li>Compare like-for-like completed tasks with the same backend, speed scale, input workload, starting application state and instrumentation. This report does not enforce those conditions.</li><li>Controller CPU time is CPU-seconds consumed by the Python controller, including its monitoring overhead. It is not total application or system CPU. Sleep lowers average CPU utilization; CPU-seconds and wall time are shown separately.</li><li>Peak RSS is sampled controller resident memory and can miss transient peaks. Background applications and cold starts can affect results.</li><li>Timing samples are conditioned on kind but are not normalized for unit count. Compare samples representing the same action units; a whole text chunk and a single key are different workloads.</li><li>Failed and cancelled runs can contain partial timing samples. No population-level reliability, statistical significance or human indistinguishability is inferred.</li><li>No human reference dataset was generated or added. A real human comparison requires separately recorded, consented and clearly identified reference observations.</li></ul></section>
<section class="panel"><h2>Measurement scope and source directories</h2>{''.join(scope_rows)}</section>{warnings_html}<footer>Generated {_escape(datetime.now(timezone.utc).isoformat(timespec='seconds'))} · Portable HTML · No external assets or network requests</footer></main></body></html>'''
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    return output.resolve()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compare Office Twin run evidence without inventing baselines")
    parser.add_argument("run_dirs", nargs="+", type=Path, help="Directories containing summary.json and events.jsonl")
    parser.add_argument("--output", type=Path, default=Path("comparison.html"), help="Destination HTML file")
    arguments = parser.parse_args(argv)
    try:
        output = generate_comparison_report(arguments.run_dirs, arguments.output)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
