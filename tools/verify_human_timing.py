"""Offline verification of synthetic key-delay aggregates, never native input.

Run: python tools/verify_human_timing.py --output-dir NEW_OUTPUT_DIRECTORY
The predeclared seeds, sample count and 3% criterion are fixed, not CLI-tunable.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
from statistics import NormalDist
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from office_twin.timing import TimingPolicy

REFERENCE_PATH = "docs/human-baseline/aggregate.json"
REFERENCE_SHA256 = "a18df6f37bb963db97acd371ccc7d2991ca746d9d300c69dbe7b3b3b2aba5976"
SEEDS = (211, 223, 227, 229, 233)
SAMPLES_PER_SEED = 100_000
MODES = ("contextual", "human-informed")
TARGETS = {"mean": 0.200, "median": 0.170, "p90": 0.350}
BOUNDS = {"contextual": (0.035, 0.300), "human-informed": (0.005, 2.0)}
RELATIVE_ERROR_LIMIT = 0.03
QUANTILE_DEFINITION = "Linear interpolation between sorted samples at zero-based position (n - 1) * p; median uses p=0.5 and p90 uses p=0.9."
LIMITATIONS = [
    "All generated values are synthetic requested pre-key controller delays, not measured human intervals or observed native key delivery.",
    "The reference is participant-confirmed unassisted human measurement aggregates. Raw input traces and detailed interval capture definitions were not supplied; independent verification is not claimed.",
    "Median and p90 are fit targets. Mean is held out of the two-parameter fit as an aggregate consistency check, not an independent participant or task.",
    "Matching three aggregate statistics does not recover the human distribution, serial correlation, pauses, key holds, errors, mouse activity, or task behavior.",
    "The 3% threshold is a predeclared engineering acceptance criterion, not a confidence interval, significance test, competition rule, or human-indistinguishability threshold.",
    "Scale is one and each sample requests one key unit. Application/API overhead and OS scheduling add time; these synthetic delays cannot be directly substituted for delivered inter-key intervals.",
    "The 720-second task and 180-second typing window are not fitted, reconstructed, or validated. No new human run or native desktop run occurred.",
    "Engineering clipping bounds are not measured human extrema. Public sample() exposes boundary values, not the underlying unclipped draws.",
    "No official score, winning probability, human-versus-agent speed ratio, KS test, or human-authenticity conclusion is produced.",
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_reference(path=None):
    path = Path(path) if path is not None else ROOT / REFERENCE_PATH
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != REFERENCE_SHA256:
        raise ValueError("Human aggregate reference SHA-256 differs from the predeclared reference")
    data = json.loads(raw.decode("utf-8-sig"))
    measured = data["measured_results_participant_reported"]
    fields = {"mean": "mean_inter_key_interval_milliseconds",
              "median": "median_inter_key_interval_milliseconds",
              "p90": "p90_inter_key_interval_milliseconds"}
    targets = {}
    for metric, field in fields.items():
        value = measured[field]
        if type(value) not in (int, float) or not math.isfinite(value) or value / 1000 != TARGETS[metric]:
            raise ValueError(f"Reference {metric} does not match the predeclared target")
        targets[metric] = value / 1000
    provenance = data["provenance"]
    for field in ("actual_measurements_confirmed_by_participant",
                  "completed_entirely_by_human_confirmed_by_participant",
                  "without_guidance_confirmed_by_participant"):
        if provenance.get(field) is not True:
            raise ValueError("Reference does not confirm unassisted participant measurements")
    if provenance.get("independently_verified") is not False or provenance.get("raw_input_event_logs_supplied") is not False:
        raise ValueError("Reference provenance differs from the declared aggregate-only scope")
    return {"path": REFERENCE_PATH, "sha256": digest,
            "classification": "participant-confirmed unassisted human measurement aggregates",
            "targets_seconds": targets, "independently_verified": False,
            "raw_input_event_logs_supplied": False,
            "fitted_metrics": ["median", "p90"], "held_out_aggregate_check": "mean"}


def quantile_sorted(values, probability):
    """Interpolate an already sorted, nonempty numeric sequence."""
    if not values or not 0 <= probability <= 1:
        raise ValueError("Quantile requires values and probability in [0, 1]")
    position = (len(values) - 1) * probability
    lower = math.floor(position)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def summarize_samples(values, bounds):
    if not values:
        raise ValueError("At least one synthetic sample is required")
    if any(type(value) not in (int, float) or not math.isfinite(value) or value <= 0 for value in values):
        raise ValueError("Synthetic samples must be positive finite numbers")
    ordered = sorted(values)
    low, high = bounds
    return {"count": len(ordered), "mean": math.fsum(ordered) / len(ordered),
            "median": quantile_sorted(ordered, .5), "p90": quantile_sorted(ordered, .9),
            "minimum": ordered[0], "maximum": ordered[-1],
            "engineering_bounds_seconds": {"minimum": low, "maximum": high},
            "all_samples_within_bounds": low <= ordered[0] <= ordered[-1] <= high,
            "bound_hit_counts": {"lower": sum(value == low for value in ordered),
                                "upper": sum(value == high for value in ordered)},
            "bound_hit_definition": "Returned values exactly equal to an engineering bound; raw unclipped draws are not exposed by sample()."}


def metadata_reference_matches(metadata, reference):
    fit = metadata.get("reference_fit", {})
    profile = metadata.get("profiles_seconds_per_unit", {}).get("key", {})
    targets = reference["targets_seconds"]
    return (
        metadata.get("mode") == "human-informed" and metadata.get("scale") == 1.0
        and fit.get("source") == reference["path"] and fit.get("source_sha256") == reference["sha256"]
        and fit.get("fitted_median_seconds") == targets["median"]
        and fit.get("fitted_p90_seconds") == targets["p90"]
        and fit.get("reference_mean_seconds") == targets["mean"]
        and fit.get("target_scale") == 1.0 and fit.get("scale_one_targets_active") is True
        and fit.get("independent_key_samples") is True
        and fit.get("native_input_intervals_verified") is False
        and fit.get("human_indistinguishability_verified") is False
        and profile.get("minimum") == BOUNDS["human-informed"][0]
        and profile.get("maximum") == BOUNDS["human-informed"][1]
    )


def sample_policy(mode, seed, count):
    if type(count) is not int or count < 1:
        raise ValueError("Sample count must be a positive integer")
    policy = TimingPolicy(mode=mode, seed=seed, scale=1.0)
    values = [policy.sample("key", 1) for _ in range(count)]
    return summarize_samples(values, BOUNDS[mode]), policy.metadata()


def compare_seed(seed, samples, targets):
    comparisons = {}
    for metric, target in targets.items():
        old_error = abs(samples["contextual"][metric] - target) / target
        new_error = abs(samples["human-informed"][metric] - target) / target
        comparisons[metric] = {
            "target_seconds": target,
            "contextual_absolute_relative_error": old_error,
            "human_informed_absolute_relative_error": new_error,
            "human_informed_within_3_percent": new_error <= RELATIVE_ERROR_LIMIT,
            "human_informed_closer_than_contextual": new_error < old_error,
        }
    return {"seed": seed, "samples": samples, "metric_checks": comparisons,
            "passed": all(item["human_informed_within_3_percent"]
                          and item["human_informed_closer_than_contextual"] for item in comparisons.values())
                      and all(item["all_samples_within_bounds"] for item in samples.values())}


def verify():
    reference = load_reference()
    sources_before = {name: sha256(ROOT / name) for name in
                      ("office_twin/timing.py", "tools/verify_human_timing.py")}
    rows, model_metadata = [], {}
    metadata_matches = True
    for seed in SEEDS:
        samples = {}
        for mode in MODES:
            samples[mode], metadata = sample_policy(mode, seed, SAMPLES_PER_SEED)
            if mode == "human-informed":
                metadata_matches = metadata_matches and metadata_reference_matches(metadata, reference)
            # Public model metadata contains only declared policy information.
            # Keep one representative per mode, not every duplicate profile.
            if mode not in model_metadata:
                model_metadata[mode] = metadata
        rows.append(compare_seed(seed, samples, reference["targets_seconds"]))
    sources_after = {name: sha256(ROOT / name) for name in sources_before}
    sigma = math.log(reference["targets_seconds"]["p90"] / reference["targets_seconds"]["median"]) / NormalDist().inv_cdf(.9)
    median = reference["targets_seconds"]["median"]
    low, high = BOUNDS["human-informed"]
    checks = {
        "reference_hash_and_aggregate_targets_verified": True,
        "model_metadata_matches_reference_and_scope": metadata_matches,
        "all_predeclared_seed_checks_passed": all(row["passed"] for row in rows),
        "source_bytes_unchanged_during_verification": sources_before == sources_after,
    }
    return {
        "schema_version": 1, "kind": "offline-synthetic-key-timing-verification",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "passed": all(checks.values()), "checks": checks,
        "source_files_sha256": sources_before, "reference": reference,
        "python_version": platform.python_version(),
        "protocol": {"seeds": list(SEEDS), "modes": list(MODES),
                     "samples_per_seed_per_mode": SAMPLES_PER_SEED,
                     "total_generated_key_delay_samples": len(SEEDS) * len(MODES) * SAMPLES_PER_SEED,
                     "scale": 1.0, "units_per_sample": 1, "draw_kind": "key",
                     "absolute_relative_error_limit": RELATIVE_ERROR_LIMIT,
                     "required_comparison": "Each human-informed mean, median and p90 must be within 3% of its target and strictly closer than contextual for the same seed.",
                     "quantile_definition": QUANTILE_DEFINITION,
                     "predeclared_engineering_criteria": True,
                     "actual_sleep_or_input_delivery_performed": False},
        "claims": {"synthetic_samples": True, "new_human_run": False,
                   "native_input_observed": False, "elapsed_task_duration_validated": False,
                   "human_distribution_tested": False, "official_score_claimed": False},
        "model_metadata": model_metadata,
        "analytical_unclipped_fit": {
            "log_sigma": sigma, "median_seconds": median,
            "mean_seconds": median * math.exp(sigma * sigma / 2),
            "probability_below_engineering_lower_bound": NormalDist().cdf(math.log(low / median) / sigma),
            "probability_above_engineering_upper_bound": 1 - NormalDist().cdf(math.log(high / median) / sigma),
            "interpretation": "Mathematical properties of the assumed lognormal model, not estimates of human population tails."},
        "per_seed_results": rows, "limitations": list(LIMITATIONS),
    }


def export(result, output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    path = output / "timing-verification.json"
    # Retain previous reports: callers must choose a fresh output directory.
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = verify()
        path = export(result, args.output_dir)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(path.resolve())
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

