from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype


class FundingEventContractError(ValueError):
    pass


CANONICAL_EVENT_COLUMNS = [
    "event_id",
    "venue",
    "instrument",
    "funding_time_utc",
    "observable_time_utc",
    "maturity_time_utc",
    "funding_rate",
    "mark_price",
    "payer_side",
    "receiver_side",
    "long_cashflow_rate",
    "short_cashflow_rate",
    "source_record_id",
]


def _utc(series: pd.Series) -> pd.Series:
    if is_datetime64_any_dtype(series.dtype):
        return pd.to_datetime(series, utc=True, errors="coerce")
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().mean() >= 0.8 and numeric.notna().any():
        median = float(numeric.dropna().abs().median())
        unit = "ms" if median > 10_000_000_000 else "s"
        return pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
    return pd.to_datetime(series, utc=True, errors="coerce")


def _stable_event_id(venue: str, instrument: str, event_time: pd.Timestamp) -> str:
    key = f"{venue}|{instrument}|{event_time.isoformat()}"
    return "funding-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]


def canonicalize_funding_events(
    frame: pd.DataFrame,
    *,
    instrument_col: str = "symbol",
    event_time_col: str = "funding_time",
    rate_col: str = "funding_rate",
    observable_time_col: str | None = None,
    mark_price_col: str | None = None,
    source_record_col: str | None = None,
    venue: str = "BINANCE_UM",
    default_observable_delay: str | pd.Timedelta = "1h",
) -> pd.DataFrame:
    required = {instrument_col, event_time_col, rate_col}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise FundingEventContractError(f"missing native funding event fields: {missing}")
    if frame.empty:
        return pd.DataFrame(columns=CANONICAL_EVENT_COLUMNS)

    out = pd.DataFrame(index=frame.index)
    out["venue"] = venue
    out["instrument"] = frame[instrument_col].astype(str).str.upper().str.strip()
    out["funding_time_utc"] = _utc(frame[event_time_col])
    out["funding_rate"] = pd.to_numeric(frame[rate_col], errors="coerce")
    out["mark_price"] = (
        pd.to_numeric(frame[mark_price_col], errors="coerce")
        if mark_price_col and mark_price_col in frame
        else np.nan
    )
    if observable_time_col and observable_time_col in frame:
        out["observable_time_utc"] = _utc(frame[observable_time_col])
    else:
        out["observable_time_utc"] = out["funding_time_utc"] + pd.Timedelta(default_observable_delay)
    out["maturity_time_utc"] = out[["funding_time_utc", "observable_time_utc"]].max(axis=1)
    out["source_record_id"] = (
        frame[source_record_col].astype(str)
        if source_record_col and source_record_col in frame
        else ""
    )
    out = out.dropna(subset=["funding_time_utc", "observable_time_utc", "funding_rate"])
    if (out["observable_time_utc"] < out["funding_time_utc"]).any():
        raise FundingEventContractError("observable_time precedes funding_time")
    if (~np.isfinite(out["funding_rate"].to_numpy(dtype=float))).any():
        raise FundingEventContractError("funding_rate must be finite")

    duplicate_key = ["venue", "instrument", "funding_time_utc"]
    conflicting = out.groupby(duplicate_key, dropna=False)["funding_rate"].nunique().gt(1)
    if conflicting.any():
        raise FundingEventContractError("conflicting funding rates for one native event identity")
    out = out.sort_values(duplicate_key + ["observable_time_utc"]).drop_duplicates(duplicate_key, keep="first")
    out["payer_side"] = np.where(out["funding_rate"] > 0, "LONG", np.where(out["funding_rate"] < 0, "SHORT", "NONE"))
    out["receiver_side"] = np.where(out["funding_rate"] > 0, "SHORT", np.where(out["funding_rate"] < 0, "LONG", "NONE"))
    out["long_cashflow_rate"] = -out["funding_rate"]
    out["short_cashflow_rate"] = out["funding_rate"]
    out["event_id"] = [
        _stable_event_id(str(row.venue), str(row.instrument), row.funding_time_utc)
        for row in out.itertuples()
    ]
    return out[CANONICAL_EVENT_COLUMNS].reset_index(drop=True)


def funding_event_flags_from_last_time(
    frame: pd.DataFrame,
    *,
    symbol_col: str = "symbol",
    row_time_col: str = "timestamp",
    last_funding_time_col: str = "last_funding_time",
) -> pd.Series:
    if last_funding_time_col not in frame.columns:
        return pd.Series(False, index=frame.index, dtype=bool)
    work = pd.DataFrame(index=frame.index)
    work["symbol"] = frame[symbol_col].astype(str)
    work["row_time"] = _utc(frame[row_time_col])
    work["native_event_time"] = _utc(frame[last_funding_time_col])
    ordered = work.sort_values(["symbol", "row_time"])
    previous = ordered.groupby("symbol", sort=False)["native_event_time"].shift(1)
    changed = ordered["native_event_time"].notna() & ordered["native_event_time"].ne(previous)
    observable = ordered["native_event_time"] <= ordered["row_time"]
    flags = (changed & observable).reindex(frame.index).fillna(False)
    return flags.astype(bool)


def audit_cashflow_semantics(events: pd.DataFrame, *, atol: float = 1e-15) -> dict[str, Any]:
    if events.empty:
        return {"rows": 0, "zero_sum_failures": 0, "payer_sign_failures": 0, "pass": True}
    zero_sum = pd.to_numeric(events["long_cashflow_rate"], errors="coerce") + pd.to_numeric(
        events["short_cashflow_rate"], errors="coerce"
    )
    rate = pd.to_numeric(events["funding_rate"], errors="coerce")
    payer = events["payer_side"].astype(str)
    sign_ok = ((rate > 0) & payer.eq("LONG")) | ((rate < 0) & payer.eq("SHORT")) | ((rate == 0) & payer.eq("NONE"))
    zero_failures = int((zero_sum.abs() > atol).sum())
    sign_failures = int((~sign_ok).sum())
    return {
        "rows": int(len(events)),
        "zero_sum_failures": zero_failures,
        "payer_sign_failures": sign_failures,
        "pass": zero_failures == 0 and sign_failures == 0,
    }


@dataclass(frozen=True)
class FundingEventAudit:
    summary: dict[str, Any]
    matches: pd.DataFrame
    missed: pd.DataFrame
    false_positives: pd.DataFrame


def audit_funding_event_detection(
    expected: pd.DataFrame,
    detected: pd.DataFrame,
    *,
    tolerance: str | pd.Timedelta = "30m",
) -> FundingEventAudit:
    required = {"venue", "instrument", "funding_time_utc"}
    for name, frame in (("expected", expected), ("detected", detected)):
        missing = sorted(required.difference(frame.columns))
        if missing:
            raise FundingEventContractError(f"{name} events missing audit fields: {missing}")
    tol = pd.Timedelta(tolerance)
    exp = expected.copy().reset_index(drop=True)
    det = detected.copy().reset_index(drop=True)
    exp["funding_time_utc"] = _utc(exp["funding_time_utc"])
    det["funding_time_utc"] = _utc(det["funding_time_utc"])
    used: set[int] = set()
    match_rows: list[dict[str, Any]] = []
    missed_indices: list[int] = []
    for exp_idx, row in exp.iterrows():
        candidates = det[
            det["venue"].astype(str).eq(str(row["venue"]))
            & det["instrument"].astype(str).eq(str(row["instrument"]))
            & ~det.index.isin(used)
        ].copy()
        if candidates.empty:
            missed_indices.append(exp_idx)
            continue
        candidates["timing_error"] = candidates["funding_time_utc"] - row["funding_time_utc"]
        candidates["timing_error_abs"] = candidates["timing_error"].abs()
        best_idx = int(candidates["timing_error_abs"].idxmin())
        best = candidates.loc[best_idx]
        if best["timing_error_abs"] > tol:
            missed_indices.append(exp_idx)
            continue
        used.add(best_idx)
        match_rows.append(
            {
                "expected_index": exp_idx,
                "detected_index": best_idx,
                "venue": row["venue"],
                "instrument": row["instrument"],
                "expected_time_utc": row["funding_time_utc"],
                "detected_time_utc": best["funding_time_utc"],
                "timing_error_seconds": float(best["timing_error"].total_seconds()),
            }
        )
    matches = pd.DataFrame(match_rows)
    missed = exp.loc[missed_indices].copy()
    false_positives = det.loc[~det.index.isin(used)].copy()
    expected_count = len(exp)
    detected_count = len(det)
    matched_count = len(matches)
    timing_abs = matches["timing_error_seconds"].abs() if not matches.empty else pd.Series(dtype=float)
    cashflow = audit_cashflow_semantics(detected) if set(CANONICAL_EVENT_COLUMNS).issubset(detected.columns) else {"pass": False}
    summary = {
        "tolerance_seconds": float(tol.total_seconds()),
        "expected_events": expected_count,
        "detected_events": detected_count,
        "matched_events": matched_count,
        "missed_events": int(len(missed)),
        "false_positive_events": int(len(false_positives)),
        "recall": float(matched_count / expected_count) if expected_count else 1.0,
        "precision": float(matched_count / detected_count) if detected_count else (1.0 if expected_count == 0 else 0.0),
        "timing_error_abs_seconds_max": float(timing_abs.max()) if not timing_abs.empty else 0.0,
        "cashflow_semantics_pass": bool(cashflow.get("pass", False)),
    }
    return FundingEventAudit(summary, matches, missed, false_positives)
