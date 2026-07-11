from __future__ import annotations

from dataclasses import dataclass

import numpy as np


FUTURE_WRONG_LAG_HOURS = 24
FUTURE_WRONG_LAG_VARIANT = "future_wrong_lag_24h"


def future_wrong_lag(values: np.ndarray, periods: int = FUTURE_WRONG_LAG_HOURS) -> np.ndarray:
    if periods <= 0:
        raise ValueError("future wrong-lag periods must be positive")
    if values.ndim != 2:
        raise ValueError("future wrong-lag expects asset x time matrix")
    out = np.full_like(values, np.nan, dtype=np.float64)
    if periods < values.shape[1]:
        out[:, :-periods] = values[:, periods:]
    return out


@dataclass(frozen=True)
class FutureWrongLagAudit:
    original_metric: float
    future_metric: float
    tolerance: float
    future_dominates: bool
    status: str


def audit_future_wrong_lag(
    original_metric: float,
    future_metric: float,
    *,
    tolerance: float = 0.0,
) -> FutureWrongLagAudit:
    original = float(original_metric)
    future = float(future_metric)
    if not np.isfinite(original) or not np.isfinite(future):
        return FutureWrongLagAudit(original, future, tolerance, True, "FAIL_NON_FINITE_CONTROL_METRIC")
    dominates = future >= original - float(tolerance)
    return FutureWrongLagAudit(
        original,
        future,
        float(tolerance),
        dominates,
        "FAIL_FUTURE_WRONG_LAG_DOMINATES" if dominates else "PASS_FUTURE_WRONG_LAG_WEAKER",
    )
