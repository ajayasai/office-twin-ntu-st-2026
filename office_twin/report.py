"""Generate a portable evidence report; no network, JavaScript or plotting deps."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import html
import json
import math
from pathlib import Path
import statistics


def _escape(value) -> str:
    return html.escape(str(value), quote=True)


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) and result >= 0 else None
    except (ValueError, TypeError):
        return None


def _format(value, suffix="", precision=2) -> str:
    result = _number(value)
    return "Unavailable" if result is None else f"{result:,.{precision}f}{suffix}"


def _read_events(path: Path) -> tuple[list[dict], int]:
    events, rejected = [], 0
    if not path.exists():
        return events, rejected
    with path.open(encoding="utf-8-sig") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError("not an object")
                events.append(record)
            except (ValueError, TypeError):
                rejected += 1
    return events, rejected


def generate_report(run_dir: Path) -> Path:
    """Read a run's summary/events and save a self-contained ``report.html``.

    Missing values are labelled unavailable; absence never becomes a pass.
    Event strings and summary fields are escaped before entering the document.
    """
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    summary_path = run_dir / "summary.json"
    warnings = []
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8-sig"))
        if not isinstance(summary, dict):
            raise ValueError("summary must be an object")
    except (OSError, ValueError) as exc:
        summary = {}
        warnings.append(f"Summary unavailable: {exc}")
    events, rejected = _read_events(run_dir / "events.jsonl")
    if rejected:
        warnings.append(f"Skipped {rejected} malformed event record(s).")
    resources = summary.get("resources", {})
    if not isinstance(resources, dict):
        resources = {}
    if not resources:
        resources = next((e["resources"] for e in reversed(events)
                          if isinstance(e.get("resources"), dict)), {})
    timing = summary.get("timing", summary.get("timing_policy", {}))
    if not isinstance(timing, dict):
        timing = {"mode": str(timing)}
    backend = str(summary.get("backend", summary.get("execution_mode", "unknown"))).lower()
    if backend == "unknown":
        backend = next((str(e.get("backend")).lower() for e in events if e.get("backend")), "unknown")
    simulation = backend in {"simulation", "simulate", "sim", "dry-run", "dry_run"}
    desktop = backend in {"desktop", "windows", "native", "live"}
    if simulation:
        mode_label = "SIMULATION"
        mode_explanation = "Simulation exercises the planner and evidence pipeline. It does not demonstrate native application interaction or Windows input delivery."
    elif desktop:
        mode_label = "DESKTOP RUN"
        mode_explanation = "Desktop execution was selected. Controller logs alone do not prove that every requested action reached the intended application; inspect screenshots, saved outputs and independent telemetry."
    else:
        mode_label = "EXECUTION MODE UNCONFIRMED"
        mode_explanation = "The run did not declare a recognized execution backend. No native application execution claim can be established from this report."
    declared_success = summary.get("success")
    result = "Declared success" if declared_success is True else "Declared failure" if declared_success is False else str(summary.get("status", "Outcome not declared"))
    delays = defaultdict(list)
    for event in events:
        kind = event.get("timing_kind", event.get("kind"))
        value = event.get("delay_seconds", event.get("requested_delay_seconds"))
        if value is None and event.get("event") in {"timing", "delay", "pause"}:
            value = event.get("seconds", event.get("duration_seconds"))
        numeric = _number(value)
        if kind and numeric is not None:
            delays[str(kind)].append(numeric)
    max_mean = max((statistics.mean(values) for values in delays.values()), default=1.0) or 1.0
    timing_rows, bars = [], []
    for index, (kind, values) in enumerate(sorted(delays.items())):
        mean = statistics.mean(values)
        timing_rows.append(f"<tr><td>{_escape(kind)}</td><td>{len(values)}</td><td>{mean:.3f} s</td><td>{min(values):.3f}–{max(values):.3f} s</td><td>{sum(values):.3f} s</td></tr>")
        y = index * 44 + 18
        bars.append(f'<text x="0" y="{y + 17}" class="svg-label">{_escape(kind)}</text><rect x="110" y="{y}" width="{max(1, mean / max_mean * 400):.2f}" height="24" rx="6" fill="#55dbc2"/><text x="525" y="{y + 17}" class="svg-label">{mean:.3f} s</text>')
    chart = (f'<svg viewBox="0 0 650 {max(90, len(bars) * 44 + 30)}" role="img" aria-label="Mean requested delay per timing kind">{"".join(bars)}</svg>'
             if bars else '<p class="muted">No requested delay events were recorded.</p>')
    rows = "".join(timing_rows) or '<tr><td colspan="5">No timing samples available.</td></tr>'
    event_rows = []
    meaningful_events = [event for event in events if event.get("event") not in {"timing", "resource_monitor_stopped"}]
    for event in meaningful_events[:100]:
        detail = {k: v for k, v in event.items() if k not in {"timestamp_utc", "perf_counter", "elapsed_seconds", "sequence", "evidence_source", "event", "resources"}}
        detail_text = json.dumps(detail, ensure_ascii=False, default=str)
        if len(detail_text) > 600:
            detail_text = detail_text[:600] + "…"
        event_rows.append(f'<tr><td class="nowrap">{_format(event.get("elapsed_seconds"), " s")}</td><td>{_escape(event.get("event", "observation"))}</td><td class="detail">{_escape(detail_text)}</td></tr>')
    if len(meaningful_events) > 100:
        event_rows.append(f'<tr><td colspan="3">Showing the first 100 of {len(meaningful_events)} non-timing events; raw events contain the full record.</td></tr>')
    observation_rows = []
    observations = resources.get("process_observations", [])
    if isinstance(observations, list):
        for item in observations:
            if not isinstance(item, dict):
                continue
            rss = _number(item.get("peak_observed_rss_bytes"))
            parent = "Unavailable" if item.get("parent_pid") is None else str(item["parent_pid"])
            if item.get("parent_name"):
                parent += " · " + str(item["parent_name"])
            observation_rows.append(f'<tr><td>{_escape(item.get("name", "Unknown"))}</td><td>{_escape(item.get("pid", "—"))}</td><td>{_escape(parent)}</td><td>{_escape(item.get("selection", "Unspecified"))}</td><td>{_format(item.get("observed_cpu_delta_seconds"), " s")}</td><td>{_format(None if rss is None else rss / 1048576, " MiB")}</td></tr>')
    process_trace = summary.get("process_trace")
    trace_panel = ""
    if isinstance(process_trace, dict) or desktop:
        process_trace = process_trace if isinstance(process_trace, dict) else {}
        trace_available = process_trace.get("available")
        trace_status = "Available" if trace_available is True else "Unavailable" if trace_available is False else "Not reported"
        trace_link = '<p><a href="os-process-events.jsonl">Raw OS process-start events</a></p>' if (run_dir / "os-process-events.jsonl").is_file() else ""
        trace_panel = f'''<section class="panel"><h2>OS process-start trace</h2><div class="facts"><span>Status <strong>{trace_status}</strong></span><span>Provider <strong>{_escape(process_trace.get("provider", "Not declared"))}</strong></span><span>Events <strong>{_format(process_trace.get("event_count"), precision=0)}</strong></span></div><p class="detail">{_escape(process_trace.get("reason", "No process-trace status was supplied for this run."))}</p><p class="muted">WMI process-start notifications are not Sysmon records. They do not prove UI input or document edits; existing applications may produce no new start event. App-name matches do not establish workload attribution.</p>{trace_link}</section>'''
    peak_rss = _number(resources.get("controller_peak_rss_bytes"))
    limitation_items = [
        "Timing defaults are an uncalibrated synthetic model. No human reference study or human indistinguishability result is claimed.",
        "Requested delays are policy outputs, not measurements of delivered input intervals or proof of successful task completion.",
        "Event records are controller observations. They are not independent Sysmon logs, hardware-originated input, or an external audit.",
        "Resource totals cover controller CPU and sampled controller memory. Application snapshots may include existing or unrelated processes and miss brief peaks.",
        "A successful simulation does not validate a desktop workflow. Native-app success needs output verification and recorded desktop evidence.",
    ]
    limitations = "".join(f"<li>{_escape(item)}</li>" for item in limitation_items)
    warning_html = "".join(f'<p class="warning">{_escape(warning)}</p>' for warning in warnings)
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'">
<title>Office Twin · Run evidence</title><style>
:root{{color-scheme:dark;--bg:#0b1220;--card:#141f31;--line:#2b3b52;--text:#eef5ff;--muted:#b0bfd2;--accent:#55dbc2;--amber:#ffd18b}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}}main{{max-width:1160px;margin:auto;padding:54px 28px 80px}}.eyebrow{{letter-spacing:.18em;color:var(--accent);font-size:12px;font-weight:800}}h1{{font-size:clamp(32px,5vw,52px);line-height:1.1;margin:13px 0 18px;letter-spacing:-.035em}}h2{{font-size:23px;line-height:1.25;margin:0 0 15px}}h3{{font-size:16px;margin:0 0 12px}}p{{margin:9px 0}}.lede{{color:var(--muted);max-width:800px;font-size:17px}}.badge{{display:inline-block;border:1px solid #557878;border-radius:99px;padding:5px 12px;font-size:11px;letter-spacing:.10em;color:var(--accent);font-weight:800;margin:20px 0 5px}}.banner{{border-left:3px solid var(--amber);background:#251f1b;padding:16px 22px;margin:24px 0 28px;border-radius:0 12px 12px 0}}.banner p{{margin:0;color:#f4dbb6}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0}}.metric,.panel{{background:var(--card);border:1px solid var(--line);border-radius:16px}}.metric{{padding:22px 18px}}.metric .value{{font-size:29px;line-height:1.25;font-weight:700;letter-spacing:-.025em}}.metric .label{{font-size:12px;color:var(--muted);margin-top:10px}}.panel{{padding:26px;margin:20px 0}}.split{{display:grid;grid-template-columns:1.2fr 1fr;gap:24px}}.muted,small{{color:var(--muted)}}.facts{{display:flex;flex-wrap:wrap;gap:12px 26px;color:var(--muted);font-size:13px}}.facts strong{{color:var(--text)}}table{{border-collapse:collapse;width:100%;font-size:13px}}th{{text-align:left;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}}th,td{{padding:12px 10px;border-bottom:1px solid var(--line);vertical-align:top}}td:first-child,th:first-child{{padding-left:0}}tr:last-child td{{border-bottom:0}}.table-wrap{{overflow-x:auto}}.detail{{overflow-wrap:anywhere;font-family:ui-monospace,Consolas,monospace;font-size:11px}}.nowrap{{white-space:nowrap}}svg{{width:100%;height:auto}}.svg-label{{fill:#dbe7f4;font:14px system-ui,sans-serif}}ul{{padding-left:22px;color:var(--muted)}}li{{margin:9px 0}}pre{{background:#0b1220;border-radius:10px;padding:18px;overflow:auto;max-height:440px;font:12px/1.6 ui-monospace,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere}}summary{{cursor:pointer;color:var(--accent);font-weight:600}}a{{color:var(--accent)}}.warning{{color:var(--amber)}}footer{{color:var(--muted);font-size:12px;margin-top:28px}}@media(max-width:760px){{main{{padding:30px 16px}}.metrics{{grid-template-columns:1fr 1fr}}.split{{grid-template-columns:1fr}}.panel{{padding:18px}}}}@media print{{:root{{color-scheme:light;--bg:white;--card:#f4f6f8;--line:#c3cbd3;--text:#172436;--muted:#43546a;--accent:#146859}}body{{background:white}}main{{padding:15px}}.panel{{break-inside:avoid}}.svg-label{{fill:#172436}}}}
</style></head><body><main>
<div class="eyebrow">OFFICE TWIN / EXECUTION EVIDENCE</div><h1>A workflow, with receipts.</h1>
<p class="lede">A transparent record of task execution, configured timing and measured controller resources. Evidence boundaries stay visible.</p>
<div class="badge">{mode_label}</div>
<div class="facts"><span>Run <strong>{_escape(summary.get("run_id", run_dir.name))}</strong></span><span>Outcome <strong>{_escape(result)}</strong></span><span>Timing <strong>{_escape(timing.get("mode", "Not declared"))}</strong></span><span>Seed <strong>{_escape(timing.get("seed", summary.get("seed", "Not declared")))}</strong></span><span>Scale <strong>{_escape(timing.get("scale", "Not declared"))}</strong></span></div>
<div class="banner"><p>{mode_explanation}</p></div>{warning_html}
<div class="metrics"><div class="metric"><div class="value">{_format(resources.get("wall_seconds"), " s")}</div><div class="label">MEASURED WALL TIME</div></div><div class="metric"><div class="value">{_format(resources.get("controller_cpu_seconds"), " s", 3)}</div><div class="label">CONTROLLER CPU TIME</div></div><div class="metric"><div class="value">{_format(None if peak_rss is None else peak_rss / 1048576, " MiB", 1)}</div><div class="label">SAMPLED CONTROLLER PEAK RSS</div></div><div class="metric"><div class="value">{len(events):,}</div><div class="label">CONTROLLER EVENT RECORDS</div></div></div>
<section class="panel"><h2>Timing has context</h2><p class="muted">Requested delays grouped by action kind. These are synthetic policy samples, not independently measured human input intervals. Units and speed scaling affect comparisons.</p><div class="split"><div>{chart}</div><div class="table-wrap"><table><thead><tr><th>Kind</th><th>Samples</th><th>Mean</th><th>Range</th><th>Total</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
<section class="panel"><h2>Execution trace</h2><p class="muted">A readable excerpt of the controller record. Validate task outcomes using saved artifacts and desktop recordings.</p><div class="table-wrap"><table><thead><tr><th>Elapsed</th><th>Event</th><th>Details</th></tr></thead><tbody>{''.join(event_rows) or '<tr><td colspan="3">No execution events available.</td></tr>'}</tbody></table></div></section>
{trace_panel}
<section class="panel"><h2>Process observations</h2><p class="muted">Limited process snapshots; not independent Sysmon telemetry. CPU deltas start at first observation and are not added to controller CPU time. Parent names are best-effort metadata; existing processes and ancestry do not establish workload attribution.</p><div class="table-wrap"><table><thead><tr><th>Process</th><th>PID</th><th>Parent PID/name</th><th>Selection</th><th>Observed CPU delta</th><th>Sampled peak RSS</th></tr></thead><tbody>{''.join(observation_rows) or '<tr><td colspan="6">No application process observations available.</td></tr>'}</tbody></table></div><p><small>Monitor: {_escape(resources.get('monitor_backend', 'Unavailable'))}</small></p></section>
<section class="panel"><h2>What this evidence supports</h2><p>This report exposes the declared execution mode, recorded actions, requested timing samples, and available resource measurements. It does not assign an authenticity score or infer a competition result.</p><ul>{limitations}</ul></section>
<section class="panel"><details><summary>Inspect the complete run summary</summary><pre>{_escape(json.dumps(summary, indent=2, ensure_ascii=False, default=str))}</pre></details><p><a href="events.jsonl">Raw controller events</a> · <a href="summary.json">Run summary</a></p></section>
<footer>Generated {_escape(generated)} · Self-contained report · No analytics or external assets</footer>
</main></body></html>'''
    output = run_dir / "report.html"
    output.write_text(document, encoding="utf-8")
    return output
