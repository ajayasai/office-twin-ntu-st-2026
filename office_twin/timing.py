"""Seeded timing policies for transparent, context-dependent UI workloads.

Legacy defaults are engineering choices. The optional human-informed key
profile fits participant-supplied aggregates, not a reconstructed human trace.
One ``read`` unit means a short reading chunk; other units are action counts.
"""

from __future__ import annotations

import math
import random
from statistics import NormalDist


TIMING_MODES = ("contextual", "fixed", "human-informed")
HUMAN_BASELINE_PATH = "docs/human-baseline/aggregate.json"
HUMAN_BASELINE_SHA256 = "a18df6f37bb963db97acd371ccc7d2991ca746d9d300c69dbe7b3b3b2aba5976"
HUMAN_KEY_MEDIAN = 0.170
HUMAN_KEY_P90 = 0.350
HUMAN_KEY_MEAN_REFERENCE = 0.200
HUMAN_KEY_SIGMA = math.log(HUMAN_KEY_P90 / HUMAN_KEY_MEDIAN) / NormalDist().inv_cdf(0.9)
# Engineering safeguards, NOT inferred human minimum/maximum observations.
HUMAN_KEY_BOUNDS = (0.005, 2.0)


# Lower bound, fixed baseline / nominal median, upper bound (seconds/unit).
PROFILES: dict[str, tuple[float, float, float]] = {
    "key": (0.035, 0.095, 0.30),
    "read": (0.30, 0.80, 2.50),
    "think": (0.35, 1.10, 3.80),
    "switch": (0.15, 0.45, 1.60),
    "review": (0.40, 1.30, 4.50),
    "correction": (0.10, 0.35, 1.10),
    "click": (0.08, 0.18, 0.60),
    "move": (0.08, 0.20, 0.70),
    "scroll": (0.08, 0.22, 0.80),
    "action": (0.10, 0.30, 1.00),
}


class TimingPolicy:
    """Sample bounded delays without sleeping or changing the global RNG.

    The contextual policy carries a gently correlated pace state between
    actions and introduces occasional pauses within key sequences. It is a
    transparent synthetic model, not a validated human or evasion model.
    Scale zero explicitly disables delays for simulation and testing.
    """

    def __init__(self, mode: str = "contextual", seed: int = 42, scale: float = 1.0):
        if mode not in TIMING_MODES:
            raise ValueError(f"mode must be one of {TIMING_MODES}")
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("seed must be an integer")
        if isinstance(scale, bool) or not isinstance(scale, (int, float)):
            raise ValueError("scale must be a finite non-negative number")
        if not math.isfinite(scale) or scale < 0:
            raise ValueError("scale must be a finite non-negative number")
        self.mode, self.seed, self.scale = mode, seed, float(scale)
        self._rng = random.Random(seed)
        # A separate stream keeps key-target fits stable when other actions
        # are interleaved. Legacy streams and their seeded behavior are intact.
        self._key_rng = random.Random(f"human-informed-key:{seed}")
        self._pace = 0.0
        self._sample_count = 0

    def sample(self, kind: str, units: int = 1) -> float:
        if kind not in PROFILES:
            raise ValueError(f"Unknown timing kind: {kind!r}")
        if isinstance(units, bool) or not isinstance(units, int) or units < 1:
            raise ValueError("units must be a positive integer")
        low, median, high = PROFILES[kind]
        self._sample_count += 1
        if self.mode == "fixed":
            return median * units * self.scale
        if self.mode == "human-informed" and kind == "key":
            low, high = HUMAN_KEY_BOUNDS
            return sum(min(high, max(low, self._key_rng.lognormvariate(
                math.log(HUMAN_KEY_MEDIAN), HUMAN_KEY_SIGMA)))
                for _ in range(units)) * self.scale
        duration = 0.0
        for _ in range(units):
            self._pace = 0.82 * self._pace + self._rng.gauss(0.0, 0.075)
            spread = 0.30 if kind == "key" else 0.42
            seconds = self._rng.lognormvariate(math.log(median) + self._pace, spread)
            if kind == "key" and self._rng.random() < 0.06:
                seconds *= 1.8
            duration += min(high, max(low, seconds))
        return duration * self.scale

    def metadata(self) -> dict:
        result = {
            "mode": self.mode,
            "seed": self.seed,
            "scale": self.scale,
            "sample_count": self._sample_count,
            "model_version": "aggregate-key-v1" if self.mode == "human-informed" else "contextual-v1",
            "calibration": ("Participant-aggregate-informed requested key delays; other actions retain engineering defaults."
                            if self.mode == "human-informed" else
                            "Uncalibrated engineering defaults; this legacy mode does not use the supplied human aggregates."),
            "units": "Seconds per action unit; read units are short reading chunks.",
            "delays_disabled": self.scale == 0,
            "profiles_seconds_per_unit": {
                kind: {"minimum": low, "nominal": median, "maximum": high}
                for kind, (low, median, high) in PROFILES.items()
            },
        }
        if self.mode == "human-informed":
            result["profiles_seconds_per_unit"]["key"] = {
                "minimum": HUMAN_KEY_BOUNDS[0], "nominal": HUMAN_KEY_MEDIAN,
                "maximum": HUMAN_KEY_BOUNDS[1], "bounds_basis": "engineering safeguards, not measured extrema",
            }
            result["reference_fit"] = {
                "source": HUMAN_BASELINE_PATH, "source_sha256": HUMAN_BASELINE_SHA256,
                "provenance": "Participant-confirmed unassisted human measurement aggregates; raw traces not supplied",
                "method": "Lognormal fitted to reported median and p90; reported mean is a held-out aggregate consistency check",
                "fitted_median_seconds": HUMAN_KEY_MEDIAN, "fitted_p90_seconds": HUMAN_KEY_P90,
                "reference_mean_seconds": HUMAN_KEY_MEAN_REFERENCE,
                "unclipped_model_mean_seconds": HUMAN_KEY_MEDIAN * math.exp(HUMAN_KEY_SIGMA ** 2 / 2),
                "log_sigma": HUMAN_KEY_SIGMA, "target_scale": 1.0,
                "scale_one_targets_active": self.scale == 1.0,
                "independent_key_samples": True,
                "scope": "Requested pre-key controller delays only. UI/API overhead and OS scheduling add to delivered input intervals.",
                "not_fitted": ["key holds", "serial correlation", "reading/thinking phases", "pause episodes", "errors", "mouse activity", "total task duration"],
                "native_input_intervals_verified": False,
                "human_indistinguishability_verified": False,
            }
        return result
