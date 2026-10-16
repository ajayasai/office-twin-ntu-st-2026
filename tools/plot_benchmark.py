"""Render an evidence figure from the sanitized benchmark export.

Requires matplotlib only for this optional reporting tool, not agent execution.
Usage: python tools/plot_benchmark.py benchmark.json --output figures/benchmark.png
Both PNG and SVG are written beside the requested output stem.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


NAVY, TEAL, SLATE, MUTED, GRID = "#13283e", "#008979", "#5b7187", "#536779", "#e4ebf0"


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
        return value if math.isfinite(value) and value >= 0 else None
    except (ValueError, TypeError, OverflowError):
        return None


def _selected_pairs(data):
    runs = {run.get("id"): run for run in data.get("runs", []) if isinstance(run, dict)}
    pairs, used = [], set()
    for pair in data.get("pairs", []):
        if not isinstance(pair, dict) or pair.get("performance_comparable") is not True:
            continue
        ids = pair.get("run_ids", [])
        if len(ids) != 2 or len(set(ids)) != 2 or any(identifier not in runs or identifier in used for identifier in ids):
            continue
        members = [runs[identifier] for identifier in ids]
        if {run.get("policy") for run in members} != {"fixed", "contextual"}:
            continue
        if any(run.get("complete_verified_desktop_task") is not True or
               _number(run.get("task_interval", {}).get("task_seconds")) is None for run in members):
            continue
        by_policy = {run["policy"]: run for run in members}
        if by_policy["fixed"].get("seed") != by_policy["contextual"].get("seed"):
            continue
        pairs.append((by_policy["fixed"], by_policy["contextual"]))
        used.update(ids)
    return pairs, used


def plot_benchmark(source: Path, output: Path, dpi: int = 220):
    """Return PNG and SVG paths; incomplete pairs are never plotted as complete."""
    data = json.loads(Path(source).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or not isinstance(data.get("runs"), list) or not isinstance(data.get("pairs"), list):
        raise ValueError("Expected the sanitized benchmark.json produced by analyze_benchmark.py")
    if data.get("human_reference_runs") != 0:
        raise ValueError("This figure is scoped to the automated benchmark with human_reference_runs=0")
    if not 72 <= dpi <= 600:
        raise ValueError("DPI must be between 72 and 600")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        from matplotlib.ticker import MaxNLocator
    except ImportError as exc:
        raise RuntimeError("This optional figure tool requires matplotlib; use the bundled document Python runtime or install it in a reporting environment.") from exc

    output = Path(output)
    if output.suffix.lower() not in {"", ".png", ".svg"}:
        raise ValueError("Output must be a .png, .svg, or extension-free stem")
    stem = output.with_suffix("") if output.suffix else output
    png, svg = stem.with_suffix(".png"), stem.with_suffix(".svg")
    png.parent.mkdir(parents=True, exist_ok=True)
    pairs, used = _selected_pairs(data)
    excluded = len(data["runs"]) - len(used)
    style = {"font.family": "DejaVu Sans", "font.size": 10, "text.color": NAVY,
             "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
             "axes.edgecolor": GRID, "axes.linewidth": 0.8, "svg.fonttype": "none"}
    with plt.rc_context(style):
        fig, axes = plt.subplots(1, 2, figsize=(13.6, 8.2), facecolor="white")
        # Reserve separate bands for the automated-series notice, panel titles,
        # two-line seed labels and the measurement notes.
        fig.subplots_adjust(left=0.073, right=0.975, top=0.69, bottom=0.30, wspace=0.23)
        fig.text(0.073, 0.94, "OFFICE TWIN  /  OBSERVED AUTOMATED BENCHMARK", fontsize=10,
                 weight="bold", color=TEAL)
        fig.text(0.073, 0.884, "Paired timing, with the limits visible.", fontsize=24, weight="bold")
        fig.text(0.073, 0.838, f"{len(data['runs'])} supplied attempts  ·  {len(pairs)} matched complete pairs  ·  {excluded} attempts excluded from these plots",
                 fontsize=11, color=MUTED)
        fig.text(0.073, 0.792, "AUTOMATED POLICY COMPARISON · Human measurements are reported separately.",
                 fontsize=11, color=NAVY, weight="bold", bbox={"facecolor": "#edf6f4", "edgecolor": "none", "pad": 7})

        for ax in axes:
            ax.set_facecolor("white")
            ax.spines[["top", "right"]].set_visible(False)
            ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
            ax.set_axisbelow(True)
            ax.tick_params(axis="both", length=0, pad=8)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=6))

        first, second = axes
        first.set_title("A  Task duration", loc="left", fontsize=14, weight="bold", pad=17)
        first.set_ylabel("First step start → final step completion (seconds)", labelpad=12)
        first.set_xlabel("Lines connect fixed and contextual runs with the same seed", fontsize=9, labelpad=14)
        max_duration, labels = 1.0, []
        for index, (fixed, contextual) in enumerate(pairs):
            a, b = fixed["task_interval"]["task_seconds"], contextual["task_interval"]["task_seconds"]
            max_duration = max(max_duration, a, b)
            left, right = index - 0.16, index + 0.16
            first.plot([left, right], [a, b], color="#b6c4d0", linewidth=1.8, zorder=2)
            first.scatter([left], [a], color=SLATE, s=60, marker="o", zorder=3)
            first.scatter([right], [b], color=TEAL, s=65, marker="D", zorder=3)
            first.annotate(f"{a:.1f}", (left, a), xytext=(-4, 9), textcoords="offset points", ha="right", fontsize=8.5, color=SLATE)
            first.annotate(f"{b:.1f}", (right, b), xytext=(4, 9), textcoords="offset points", ha="left", fontsize=8.5, color=TEAL)
            seed = fixed.get("seed")
            labels.append(f"Seed {seed}" if isinstance(seed, int) else f"Pair {index + 1}")
        first.set_xticks(range(len(pairs)), labels, fontsize=9)
        first.set_xlim(-0.7, max(0.7, len(pairs) - 0.3))
        first.set_ylim(0, max_duration * 1.20)
        first.legend(handles=[Line2D([], [], color=SLATE, marker="o", linestyle="none", label="Fixed"),
                              Line2D([], [], color=TEAL, marker="D", linestyle="none", label="Contextual")],
                     loc="upper left", frameon=False, ncol=2, fontsize=9)
        if not pairs:
            first.text(0.5, 0.5, "No complete matched pairs\nSee benchmark.json for exclusions", transform=first.transAxes,
                       ha="center", va="center", color=MUTED)

        second.set_title("B  Actual single-key controller waits", loc="left", fontsize=14, weight="bold", pad=17)
        second.set_ylabel("Measured wait duration (milliseconds)", labelpad=10)
        second.set_xlabel("Each run: median ● and 90th percentile ◇", fontsize=9, labelpad=14)
        wait_labels, counts, max_wait, missing = [], [], 1.0, 0
        for fixed, contextual in pairs:
            for run in (fixed, contextual):
                item = next((wait for wait in run.get("waits_by_kind_and_units", [])
                             if wait.get("kind") == "key" and wait.get("units") == 1), None)
                values = item.get("uninterrupted_actual_wait", {}) if item else {}
                median, p90, count = (_number(values.get(field)) for field in ("median_seconds", "p90_seconds", "count"))
                if median is None or p90 is None or not count:
                    missing += 1
                    continue
                x = len(wait_labels)
                color = SLATE if run["policy"] == "fixed" else TEAL
                second.vlines(x, median * 1000, p90 * 1000, color=color, linewidth=2.2, alpha=0.6)
                second.scatter([x], [median * 1000], color=color, marker="o", s=45, zorder=3)
                second.scatter([x], [p90 * 1000], edgecolors=color, facecolors="white", marker="D", s=45, linewidths=1.6, zorder=3)
                seed = run.get("seed")
                wait_labels.append(f"{'F' if run['policy'] == 'fixed' else 'C'}\n{seed if isinstance(seed, int) else x+1}")
                counts.append(int(count))
                max_wait = max(max_wait, p90 * 1000, median * 1000)
        second.set_xticks(range(len(wait_labels)), wait_labels, fontsize=8.5)
        second.set_xlim(-0.6, max(0.6, len(wait_labels) - 0.4))
        second.set_ylim(0, max_wait * 1.23)
        if counts:
            count_label = str(counts[0]) if min(counts) == max(counts) else f"{min(counts)}–{max(counts)}"
            second.text(0.02, 0.97, f"{count_label} uninterrupted key waits per run\nF = fixed; C = contextual; numbers = seeds",
                        transform=second.transAxes, va="top", fontsize=8.5, color=MUTED)
        else:
            second.text(0.5, 0.5, "No eligible single-key wait samples", transform=second.transAxes,
                        ha="center", va="center", color=MUTED)

        fig.text(0.073, 0.159, "WHAT THIS MEASURES", fontsize=9, weight="bold", color=TEAL)
        fig.text(0.073, 0.127, "Pairs match declared source, scenario, seed, scale, environment and capture settings. Task time excludes preparation, final verification and cleanup.",
                 fontsize=9, color=MUTED)
        fig.text(0.073, 0.098, "Waits are controller sleep intervals, not OS input timestamps. Events within a run are correlated. Variation alone does not establish human behavior.",
                 fontsize=9, color=MUTED)
        fig.text(0.073, 0.069, f"Failed, incomplete and unmatched attempts are excluded from these plots and retained in the evidence report. Missing eligible key-wait summaries: {missing}.",
                 fontsize=9, color=MUTED)
        fig.text(0.073, 0.038, "Descriptive observations only  ·  No statistical significance, whole-system efficiency, human authenticity or official score is inferred.",
                 fontsize=9, color=NAVY)
        fig.savefig(png, dpi=dpi, facecolor="white", metadata={"Description": "Observed paired automated benchmark. Human measurements are reported separately; no human similarity validation is inferred."})
        fig.savefig(svg, facecolor="white", metadata={"Description": "Observed paired automated benchmark. Human measurements are reported separately; no human similarity validation is inferred."})
        plt.close(fig)
    return png.resolve(), svg.resolve()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("benchmark", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dpi", type=int, default=220)
    args = parser.parse_args(argv)
    try:
        paths = plot_benchmark(args.benchmark, args.output, args.dpi)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
