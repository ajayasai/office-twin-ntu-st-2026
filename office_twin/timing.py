"""Seeded timing policies for transparent, context-dependent UI workloads.

Defaults are engineering choices, not measurements of human behaviour.
One ``read`` unit means a short reading chunk; other units are action counts.
"""

from __future__ import annotations

import math
import random


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
        if mode not in {"contextual", "fixed"}:
            raise ValueError("mode must be 'contextual' or 'fixed'")
        if isinstance(seed, bool) or not isinstance(seed, int):
            raise ValueError("seed must be an integer")
        if isinstance(scale, bool) or not isinstance(scale, (int, float)):
            raise ValueError("scale must be a finite non-negative number")
        if not math.isfinite(scale) or scale < 0:
            raise ValueError("scale must be a finite non-negative number")
        self.mode, self.seed, self.scale = mode, seed, float(scale)
        self._rng = random.Random(seed)
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
        return {
            "mode": self.mode,
            "seed": self.seed,
            "scale": self.scale,
            "sample_count": self._sample_count,
            "model_version": "contextual-v1",
            "calibration": "Uncalibrated engineering defaults; no human reference data supplied.",
            "units": "Seconds per action unit; read units are short reading chunks.",
            "delays_disabled": self.scale == 0,
            "profiles_seconds_per_unit": {
                kind: {"minimum": low, "nominal": median, "maximum": high}
                for kind, (low, median, high) in PROFILES.items()
            },
        }
