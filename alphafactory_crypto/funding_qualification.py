from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .funding_events import FundingEventAudit, audit_funding_event_detection


class FundingQualificationError(ValueError):
    pass


@dataclass(frozen=True)
class FundingProductionQualification:
    summary: dict[str, Any]
    matches: pd.DataFrame
    misses: pd.DataFrame
    false_positives: pd.DataFrame
    symbol_month_coverage: pd.DataFrame
    schedule_intervals: pd.DataFrame


def validate_observation_columns(requested: Iterable[str], allowed: set[str]) -> None:
    requested_set = {str(value) for value in requested}
    forbidden = sorted(requested_set.difference(allowed))
    if forbidden:
        raise FundingQualificationError(f"unapproved funding qualification columns: {forbidden}")


def _duplicate_count(frame: pd.DataFrame) -> int:
    return int(frame.duplicated(["venue", "instrument", "funding_time_utc"], keep=False).sum())


def _coverage(truth: pd.DataFrame, audit: FundingEventAudit) -> pd.DataFrame:
    expected = truth.copy()
    expected["month_utc"] = expected["funding_time_utc"].dt.strftime("%Y-%m")
    expected["matched"] = expected.index.isin(audit.matches.get("expected_index", pd.Series(dtype=int)))
    coverage = (
        expected.groupby(["venue", "instrument", "month_utc"], as_index=False)
        .agg(expected_events=("event_id", "size"), matched_events=("matched", "sum"))
        .sort_values(["venue", "instrument", "month_utc"])
    )
    coverage["missed_events"] = coverage["expected_events"] - coverage["matched_events"]
    coverage["coverage_ratio"] = coverage["matched_events"] / coverage["expected_events"]
    return coverage.reset_index(drop=True)


def _schedule_intervals(truth: pd.DataFrame) -> pd.DataFrame:
    ordered = truth.sort_values(["venue", "instrument", "funding_time_utc"]).copy()
    interval_seconds = ordered.groupby(["venue", "instrument"])["funding_time_utc"].diff().dt.total_seconds()
    ordered["interval_hours"] = (np.rint(interval_seconds / 60.0) * 60.0 / 3600.0).round(6)
    intervals = ordered.dropna(subset=["interval_hours"]).copy()
    intervals["interval_hours"] = intervals["interval_hours"].round(6)
    if intervals.empty:
        return pd.DataFrame(columns=["venue", "instrument", "interval_hours", "event_transitions"])
    return (
        intervals.groupby(["venue", "instrument", "interval_hours"], as_index=False)
        .size()
        .rename(columns={"size": "event_transitions"})
        .sort_values(["venue", "instrument", "interval_hours"])
        .reset_index(drop=True)
    )


def qualify_production_funding(
    truth: pd.DataFrame,
    detected: pd.DataFrame,
    *,
    source_integrity_verified: bool,
    tolerance: str | pd.Timedelta = "30m",
    rate_atol: float = 1e-15,
) -> FundingProductionQualification:
    audit = audit_funding_event_detection(truth, detected, tolerance=tolerance)
    matches = audit.matches.copy()
    if matches.empty:
        rate_mismatch_events = 0
        max_rate_error = 0.0
    else:
        expected_rates = truth.loc[matches["expected_index"], "funding_rate"].to_numpy(dtype=float)
        detected_rates = detected.loc[matches["detected_index"], "funding_rate"].to_numpy(dtype=float)
        rate_errors = np.abs(expected_rates - detected_rates)
        matches["expected_funding_rate"] = expected_rates
        matches["detected_funding_rate"] = detected_rates
        matches["funding_rate_abs_error"] = rate_errors
        rate_mismatch_events = int((rate_errors > rate_atol).sum())
        max_rate_error = float(rate_errors.max(initial=0.0))

    misses = audit.missed.copy()
    detected_symbols = set(detected["instrument"].astype(str))
    if not misses.empty:
        misses["miss_classification"] = np.where(
            misses["instrument"].astype(str).isin(detected_symbols),
            "NO_DETECTED_EVENT_WITHIN_TOLERANCE",
            "NO_SYMBOL_COVERAGE",
        )
    false_positives = audit.false_positives.copy()
    if not false_positives.empty:
        false_positives["false_positive_classification"] = "NO_TRUTH_EVENT_WITHIN_TOLERANCE"

    coverage = _coverage(truth, audit)
    schedule = _schedule_intervals(truth)
    complete_groups = int(coverage["coverage_ratio"].eq(1.0).sum()) if not coverage.empty else 0
    total_groups = int(len(coverage))
    truth_symbols = set(truth["instrument"].astype(str))
    fully_covered_symbols = set(
        coverage.groupby("instrument")["coverage_ratio"].min().loc[lambda values: values.eq(1.0)].index.astype(str)
    ) if not coverage.empty else set()
    symbol_coverage_ratio = float(len(fully_covered_symbols) / len(truth_symbols)) if truth_symbols else 1.0
    group_coverage_ratio = float(complete_groups / total_groups) if total_groups else 1.0

    strict_pass = all(
        [
            source_integrity_verified,
            audit.summary["recall"] == 1.0,
            audit.summary["precision"] == 1.0,
            _duplicate_count(truth) == 0,
            _duplicate_count(detected) == 0,
            rate_mismatch_events == 0,
            audit.summary["cashflow_semantics_pass"],
            symbol_coverage_ratio == 1.0,
            group_coverage_ratio == 1.0,
        ]
    )
    if strict_pass:
        decision = "PRODUCTION_FUNDING_OBSERVATION_QUALIFIED"
    elif source_integrity_verified and len(truth) and audit.summary["cashflow_semantics_pass"]:
        decision = "PRODUCTION_FUNDING_OBSERVATION_PARTIALLY_QUALIFIED"
    else:
        decision = "PRODUCTION_FUNDING_OBSERVATION_NOT_QUALIFIED"

    summary = {
        "decision": decision,
        **audit.summary,
        "source_integrity_verified": bool(source_integrity_verified),
        "truth_duplicate_rows": _duplicate_count(truth),
        "detected_duplicate_rows": _duplicate_count(detected),
        "rate_mismatch_events": rate_mismatch_events,
        "funding_rate_abs_error_max": max_rate_error,
        "truth_symbols": len(truth_symbols),
        "fully_covered_symbols": len(fully_covered_symbols),
        "symbol_coverage_ratio": symbol_coverage_ratio,
        "symbol_month_groups": total_groups,
        "fully_covered_symbol_month_groups": complete_groups,
        "symbol_month_coverage_ratio": group_coverage_ratio,
        "schedule_interval_variants": int(schedule["interval_hours"].nunique()) if not schedule.empty else 0,
        "non_8h_schedule_transitions": int(
            schedule.loc[~schedule["interval_hours"].eq(8.0), "event_transitions"].sum()
        ) if not schedule.empty else 0,
        "price_or_return_columns_read": False,
        "alpha_reward_computed": False,
        "candidate_feedback_authorized": False,
    }
    return FundingProductionQualification(summary, matches, misses, false_positives, coverage, schedule)
