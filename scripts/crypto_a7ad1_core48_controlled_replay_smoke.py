from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
PANEL_PATH = DATA_ROOT / "gold" / "panels" / "crypto_core48_1h_with_metrics_candidate_v1.parquet"
A7AD0_AUTH = ROOT / "runtime" / "a7ad0_controlled_replay_prep" / "a7ad0_authorization_matrix.json"

OUT_DIR = ROOT / "runtime" / "a7ad1_core48_controlled_replay_smoke"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AD1_CORE48_CONTROLLED_REPLAY_SMOKE_20260522.md"

SPLITS = {
    "train_2024_common": ("2024-03-16 12:00:00+00:00", "2024-12-31 23:00:00+00:00"),
    "validation_2025H1": ("2025-01-01 00:00:00+00:00", "2025-06-30 23:00:00+00:00"),
    "recent_2025H2_2026Apr": ("2025-07-01 00:00:00+00:00", "2026-04-30 23:00:00+00:00"),
}

PRIMARY_COST_BPS = 10.0
SEVERE_COST_BPS = 20.0
ANNUALIZATION = 24 * 365


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def stable_id(text: str, n: int = 12) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def row_rank(x: np.ndarray) -> np.ndarray:
    return pd.DataFrame(x).rank(axis=1, pct=True).to_numpy(dtype=float)


def row_zscore(x: np.ndarray) -> np.ndarray:
    mean = np.nanmean(x, axis=1, keepdims=True)
    std = np.nanstd(x, axis=1, keepdims=True)
    std[std < 1e-12] = np.nan
    out = (x - mean) / std
    out[~np.isfinite(out)] = np.nan
    return out


def row_residualize(signal: np.ndarray, baseline: np.ndarray) -> np.ndarray:
    valid = np.isfinite(signal) & np.isfinite(baseline)
    x = np.where(valid, signal, np.nan)
    b = np.where(valid, baseline, np.nan)
    xm = np.nanmean(x, axis=1, keepdims=True)
    bm = np.nanmean(b, axis=1, keepdims=True)
    xc = x - xm
    bc = b - bm
    cov = np.nansum(xc * bc, axis=1, keepdims=True)
    var = np.nansum(bc * bc, axis=1, keepdims=True)
    beta = np.divide(cov, var, out=np.zeros_like(cov), where=var > 1e-12)
    out = signal - beta * baseline
    out[~np.isfinite(out)] = np.nan
    return out


def split_args(text: str) -> list[str]:
    args: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            args.append(text[start:i].strip())
            start = i + 1
    args.append(text[start:].strip())
    return args


class ExprContext:
    def __init__(self, matrices: dict[str, np.ndarray]):
        self.matrices = matrices
        self.cache: dict[str, np.ndarray] = {}

    def eval(self, expr: str) -> np.ndarray:
        expr = str(expr).strip()
        if expr in self.cache:
            return self.cache[expr]
        if expr in self.matrices:
            out = self.matrices[expr]
        else:
            out = self._eval_call(expr)
        self.cache[expr] = out
        return out

    def _eval_call(self, expr: str) -> np.ndarray:
        if not expr.endswith(")") or "(" not in expr:
            raise KeyError(f"unknown expression: {expr}")
        op, rest = expr.split("(", 1)
        args = split_args(rest[:-1])
        if op in {"Rank", "CrossSymbolRank"}:
            return row_rank(self.eval(args[0]))
        if op in {"ZScore", "CrossSymbolZScore"}:
            return row_zscore(self.eval(args[0]))
        if op == "Neg":
            return -self.eval(args[0])
        if op == "Abs":
            return np.abs(self.eval(args[0]))
        if op == "Mul":
            return self.eval(args[0]) * self.eval(args[1])
        if op == "Add":
            return self.eval(args[0]) + self.eval(args[1])
        if op == "Sub":
            return self.eval(args[0]) - self.eval(args[1])
        raise ValueError(f"unsupported expression operator: {op}")


def candidate_row(family: str, expr: str, horizon: int, fields: list[str]) -> dict[str, Any]:
    cid = f"a7ad1_{family}_{horizon}_{stable_id(expr)}"
    return {
        "candidate_id": cid,
        "family": family,
        "expression": expr,
        "horizon": horizon,
        "source_fields": ";".join(sorted(set(fields))),
        "feature_available_lag_bars": 1,
        "replay_scope": "core48_common_window_only",
    }


def generate_candidates(columns: set[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    horizons = [12, 24, 48]

    def add(family: str, expr: str, horizon: int, fields: list[str]) -> None:
        if all(f in columns for f in fields):
            rows.append(candidate_row(family, expr, horizon, fields))

    for h in horizons:
        for field in ["ret_12", "ret_24", "mark_index_ratio", "premium_index", "realized_vol_24"]:
            add("F0_low_turnover_price_basis", f"Rank({field})", h, [field])
            add("F0_low_turnover_price_basis", f"Neg(Rank({field}))", h, [field])
        for price in ["ret_24", "realized_vol_24"]:
            for basis in ["mark_index_ratio", "premium_index"]:
                add("F0_low_turnover_price_basis", f"Mul(Rank({price}),ZScore({basis}))", h, [price, basis])

    for h in horizons:
        for field in ["latest_known_funding_rate", "funding_rate_persistence_3"]:
            add("F1_funding_residual_controls", f"Rank({field})", h, [field])
            add("F1_funding_residual_controls", f"Neg(Rank({field}))", h, [field])

    crowding = [
        "global_long_short_account_ratio_zscore_168h",
        "top_long_short_account_ratio_zscore_168h",
        "top_long_short_position_ratio_zscore_168h",
        "taker_buy_sell_volume_ratio_zscore_168h",
    ]
    oi_fields = ["open_interest_zscore_168h", "open_interest_change_24h", "open_interest_value_zscore_168h"]
    contexts = ["ret_24", "mark_index_ratio", "premium_index", "realized_vol_24"]
    for h in [24, 48]:
        for crowd in crowding:
            for ctx in contexts:
                add("F2_metrics_crowding_oi_interaction", f"Mul(Neg(ZScore({crowd})),Rank({ctx}))", h, [crowd, ctx])
        for oi in oi_fields:
            for ctx in contexts:
                add("F2_metrics_crowding_oi_interaction", f"Mul(ZScore({oi}),Rank({ctx}))", h, [oi, ctx])
        for crowd in crowding[:3]:
            for oi in oi_fields:
                add("F2_metrics_crowding_oi_interaction", f"Mul(Neg(ZScore({crowd})),Rank({oi}))", h, [crowd, oi])

    for h in [24, 48]:
        for field in ["ret_24", "open_interest_value_zscore_168h", "quote_volume_mean_24", "realized_vol_24"]:
            add("F3_cross_symbol_relative_strength", f"CrossSymbolRank({field})", h, [field])
        add("F3_cross_symbol_relative_strength", "Mul(CrossSymbolRank(ret_24),CrossSymbolRank(open_interest_value_zscore_168h))", h, ["ret_24", "open_interest_value_zscore_168h"])
        add("F3_cross_symbol_relative_strength", "Mul(Neg(CrossSymbolRank(realized_vol_24)),CrossSymbolRank(ret_24))", h, ["realized_vol_24", "ret_24"])

    for h in [24, 48]:
        for liq in ["quote_asset_volume", "quote_volume_mean_24", "number_of_trades", "open_interest_value_zscore_168h"]:
            add("F4_volatility_liquidity_capped", f"Mul(Rank({liq}),Rank(realized_vol_24))", h, [liq, "realized_vol_24"])
            add("F4_volatility_liquidity_capped", f"Mul(Neg(Rank({liq})),Rank(realized_vol_24))", h, [liq, "realized_vol_24"])

    out = pd.DataFrame(rows).drop_duplicates("candidate_id").reset_index(drop=True)
    return out


def load_panel() -> tuple[pd.DataFrame, list[str], list[pd.Timestamp]]:
    needed = {
        "symbol",
        "timestamp",
        "core48_common_window_eligible",
        "open",
        "close",
        "ret_12",
        "ret_24",
        "mark_index_ratio",
        "premium_index",
        "realized_vol_24",
        "latest_known_funding_rate",
        "funding_rate_persistence_3",
        "global_long_short_account_ratio_zscore_168h",
        "top_long_short_account_ratio_zscore_168h",
        "top_long_short_position_ratio_zscore_168h",
        "taker_buy_sell_volume_ratio_zscore_168h",
        "open_interest_zscore_168h",
        "open_interest_change_24h",
        "open_interest_value_zscore_168h",
        "quote_asset_volume",
        "quote_volume_mean_24",
        "number_of_trades",
    }
    all_cols = pq.read_schema(PANEL_PATH).names
    cols = [c for c in all_cols if c in needed]
    df = pd.read_parquet(PANEL_PATH, columns=cols, engine="pyarrow")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df[df["core48_common_window_eligible"].eq(True)].copy()
    df = df.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    symbols = sorted(df["symbol"].unique().tolist())
    timestamps = sorted(df["timestamp"].unique().tolist())
    return df, symbols, timestamps


def matrix_from_panel(df: pd.DataFrame, symbols: list[str], timestamps: list[pd.Timestamp], field: str) -> np.ndarray:
    wide = df.pivot(index="timestamp", columns="symbol", values=field).reindex(index=timestamps, columns=symbols)
    return wide.to_numpy(dtype=float)


def future_open_return(open_px: np.ndarray, horizon: int, lag: int) -> np.ndarray:
    out = np.full_like(open_px, np.nan, dtype=float)
    start = 1 + lag
    end = start + horizon
    if end < open_px.shape[0]:
        entry = open_px[start:-horizon, :]
        exit_ = open_px[end:, :]
        with np.errstate(divide="ignore", invalid="ignore"):
            out[: open_px.shape[0] - end, :] = exit_ / entry - 1.0
    return out


def position_from_signal(signal: np.ndarray) -> np.ndarray:
    z = row_zscore(signal)
    denom = np.nansum(np.abs(z), axis=1, keepdims=True)
    out = np.divide(z, denom, out=np.zeros_like(z), where=denom > 1e-12)
    out[~np.isfinite(out)] = 0.0
    return out


def replay_signal(
    signal: np.ndarray,
    open_px: np.ndarray,
    split_masks: dict[str, np.ndarray],
    horizon: int,
    cost_bps: float,
    lag: int,
) -> dict[str, Any]:
    pos = position_from_signal(signal)
    fwd = future_open_return(open_px, horizon, lag)
    gross_ret = np.nansum(pos * fwd, axis=1)
    gross_exposure = np.nansum(np.abs(pos), axis=1)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover = np.nansum(np.abs(pos - prev), axis=1)
    net = gross_ret - turnover * (cost_bps / 10000.0)
    out: dict[str, Any] = {}
    for split, mask in split_masks.items():
        valid = mask & np.isfinite(net) & (gross_exposure > 1e-9)
        vals = net[valid]
        gross_vals = gross_ret[valid]
        turn_vals = turnover[valid]
        if vals.size == 0:
            out[f"{split}_ann"] = None
            out[f"{split}_sharpe"] = None
            out[f"{split}_sum"] = None
            out[f"{split}_max_dd"] = None
            out[f"{split}_active_hours"] = 0
            out[f"{split}_mean_turnover"] = None
            out[f"{split}_gross_ann"] = None
            continue
        cum = np.cumsum(vals)
        dd = cum - np.maximum.accumulate(cum)
        std = float(np.nanstd(vals))
        out[f"{split}_ann"] = clean_float(float(np.nanmean(vals) * ANNUALIZATION))
        out[f"{split}_gross_ann"] = clean_float(float(np.nanmean(gross_vals) * ANNUALIZATION))
        out[f"{split}_sharpe"] = clean_float(float(np.nanmean(vals) / std * math.sqrt(ANNUALIZATION)) if std > 1e-12 else None)
        out[f"{split}_sum"] = clean_float(float(np.nansum(vals)))
        out[f"{split}_max_dd"] = clean_float(float(np.nanmin(dd)))
        out[f"{split}_active_hours"] = int(vals.size)
        out[f"{split}_mean_turnover"] = clean_float(float(np.nanmean(turn_vals)))
    out["mean_gross_exposure"] = clean_float(float(np.nanmean(gross_exposure[np.isfinite(gross_exposure)])))
    return out


def split_masks(timestamps: list[pd.Timestamp]) -> dict[str, np.ndarray]:
    ts = pd.DatetimeIndex(timestamps)
    masks: dict[str, np.ndarray] = {}
    for name, (start, end) in SPLITS.items():
        masks[name] = (ts >= pd.Timestamp(start)) & (ts <= pd.Timestamp(end))
    return masks


def control_signal(signal: np.ndarray, mode: str, seed_text: str) -> np.ndarray:
    rng = np.random.default_rng(stable_seed(seed_text + mode))
    if mode == "sign_flip":
        return -signal
    if mode == "wrong_lag_stale_24h":
        out = np.full_like(signal, np.nan, dtype=float)
        out[24:, :] = signal[:-24, :]
        return out
    if mode == "time_shuffle":
        idx = np.arange(signal.shape[0])
        rng.shuffle(idx)
        return signal[idx, :]
    if mode == "row_shuffle":
        order = np.argsort(rng.random(signal.shape), axis=1)
        return np.take_along_axis(signal, order, axis=1)
    raise ValueError(mode)


def classify(row: dict[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if (row.get("raw_validation_2025H1_ann_10bps_lag0") or -999.0) <= 0:
        reasons.append("raw_validation_nonpositive")
    if (row.get("raw_recent_2025H2_2026Apr_ann_10bps_lag0") or -999.0) <= 0:
        reasons.append("raw_recent_nonpositive")
    if (row.get("raw_recent_2025H2_2026Apr_ann_20bps_lag0") or -999.0) <= 0:
        reasons.append("cost20_recent_nonpositive")
    if (row.get("raw_recent_2025H2_2026Apr_ann_10bps_lag1") or -999.0) <= 0:
        reasons.append("lag1_recent_nonpositive")
    if (row.get("residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0") or -999.0) <= 0:
        reasons.append("residual_funding_recent_nonpositive")
    if (row.get("residual_core4_recent_2025H2_2026Apr_ann_10bps_lag0") or -999.0) <= 0:
        reasons.append("residual_core4_recent_nonpositive")
    if reasons:
        return "A7AD1_REJECTED", reasons
    return "A7AD1_RESEARCH_CLUE_PRE_MAY_ONLY", []


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    if not A7AD0_AUTH.exists():
        raise FileNotFoundError(f"missing A7AD0 authorization: {A7AD0_AUTH}")
    auth0 = json.loads(A7AD0_AUTH.read_text(encoding="utf-8"))
    if not auth0.get("authorizes_a7ad1_small_controlled_replay_smoke"):
        raise RuntimeError("A7AD0 does not authorize A7AD1")

    df, symbols, timestamps = load_panel()
    available_cols = set(df.columns)
    candidates = generate_candidates(available_cols)
    candidates.to_csv(OUT_DIR / "a7ad1_generated_candidates.csv", index=False)

    matrices = {field: matrix_from_panel(df, symbols, timestamps, field) for field in sorted(set(";".join(candidates["source_fields"]).split(";")) | {"open", "latest_known_funding_rate", "ret_12", "mark_index_ratio"}) if field in available_cols}
    ctx = ExprContext(matrices)
    open_px = matrices["open"]
    masks = split_masks(timestamps)
    funding_proxy = row_zscore(matrices["latest_known_funding_rate"])
    core4_proxy = row_zscore(ctx.eval("Mul(Rank(ret_12),ZScore(latest_known_funding_rate))")) + row_zscore(ctx.eval("Mul(Rank(mark_index_ratio),ZScore(latest_known_funding_rate))"))

    rows: list[dict[str, Any]] = []
    control_rows: list[dict[str, Any]] = []
    dominance_rows: list[dict[str, Any]] = []

    for _, cand in candidates.iterrows():
        signal = ctx.eval(str(cand["expression"]))
        base: dict[str, Any] = cand.to_dict()
        for prefix, sig in [
            ("raw", signal),
            ("residual_funding", row_residualize(signal, funding_proxy)),
            ("residual_core4", row_residualize(signal, core4_proxy)),
        ]:
            for cost, lag in [(10.0, 0), (20.0, 0), (10.0, 1)]:
                metrics = replay_signal(sig, open_px, masks, int(cand["horizon"]), cost, lag)
                for key, value in metrics.items():
                    base[f"{prefix}_{key}_{int(cost)}bps_lag{lag}"] = value
        label, reasons = classify(base)
        base["decision"] = label
        base["reject_reasons"] = ";".join(reasons)
        rows.append(base)

        control_metrics = []
        for mode in ["sign_flip", "row_shuffle", "time_shuffle", "wrong_lag_stale_24h"]:
            ctrl = control_signal(signal, mode, str(cand["candidate_id"]))
            rec: dict[str, Any] = {
                "control_id": f"{cand['candidate_id']}__{mode}",
                "base_candidate_id": cand["candidate_id"],
                "control_mode": mode,
                "family": cand["family"],
                "horizon": cand["horizon"],
            }
            metrics = replay_signal(ctrl, open_px, masks, int(cand["horizon"]), 10.0, 0)
            for key, value in metrics.items():
                rec[f"raw_{key}_10bps_lag0"] = value
            comparable = (
                (rec.get("raw_validation_2025H1_ann_10bps_lag0") or -999.0) > 0
                and (rec.get("raw_recent_2025H2_2026Apr_ann_10bps_lag0") or -999.0) > 0
            )
            rec["control_research_like"] = bool(comparable)
            control_rows.append(rec)
            control_metrics.append(rec)
        max_control_recent = max((r.get("raw_recent_2025H2_2026Apr_ann_10bps_lag0") or -999.0) for r in control_metrics)
        dominance_rows.append(
            {
                "candidate_id": cand["candidate_id"],
                "family": cand["family"],
                "candidate_recent_ann_10bps_lag0": base.get("raw_recent_2025H2_2026Apr_ann_10bps_lag0"),
                "max_control_recent_ann_10bps_lag0": clean_float(max_control_recent),
                "control_research_like_count": int(sum(bool(r["control_research_like"]) for r in control_metrics)),
                "dominance_clean": bool(max_control_recent < (base.get("raw_recent_2025H2_2026Apr_ann_10bps_lag0") or -999.0) and sum(bool(r["control_research_like"]) for r in control_metrics) == 0),
            }
        )

    scoreboard = pd.DataFrame(rows)
    controls = pd.DataFrame(control_rows)
    dominance = pd.DataFrame(dominance_rows)
    scoreboard = scoreboard.merge(dominance[["candidate_id", "control_research_like_count", "dominance_clean"]], on="candidate_id", how="left")
    scoreboard.loc[~scoreboard["dominance_clean"].fillna(False), "decision"] = "A7AD1_REJECTED"
    scoreboard.loc[~scoreboard["dominance_clean"].fillna(False), "reject_reasons"] = scoreboard["reject_reasons"].fillna("").astype(str).str.strip(";") + ";negative_control_not_dominated"

    clues = scoreboard[scoreboard["decision"].eq("A7AD1_RESEARCH_CLUE_PRE_MAY_ONLY")].copy()
    family_summary = scoreboard.groupby(["family", "decision"], observed=True).size().reset_index(name="count")
    control_summary = controls.groupby(["family", "control_mode", "control_research_like"], observed=True).size().reset_index(name="count")

    negative_control_research_like = int(controls["control_research_like"].sum()) if not controls.empty else 0
    blockers: list[str] = []
    warnings = [
        "no_may_stress_available_for_core48_common_window",
        "this_is_controlled_smoke_not_formula_search",
    ]
    if negative_control_research_like > 0:
        warnings.append("matched_negative_controls_research_like_present_candidates_demoted")
    if clues.empty:
        warnings.append("no_pre_may_research_clues_after_controls")

    if clues.empty:
        decision = "HOLD_A7AD1_NO_CONTROL_CLEAN_PRE_MAY_CLUE"
    elif negative_control_research_like > 0:
        decision = "HOLD_A7AD1_NEGATIVE_CONTROL_RESEARCH_LIKE_PRESENT"
    else:
        decision = "PASS_A7AD1_CONTROLLED_REPLAY_SMOKE_HAS_CONTROL_CLEAN_PRE_MAY_CLUES"
    auth = {
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_a7ad2_forensic_or_contract_revision": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "May unavailable in core48 common window; future May/backfilled stress remains post-selection only",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "panel": str(PANEL_PATH),
        "symbols": len(symbols),
        "timestamps": len(timestamps),
        "generated_candidates": int(len(candidates)),
        "scoreboard_rows": int(len(scoreboard)),
        "control_rows": int(len(controls)),
        "negative_control_research_like": negative_control_research_like,
        "research_clues_pre_may_only": int(len(clues)),
        "executes_replay": True,
        "executes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    scoreboard.to_csv(OUT_DIR / "a7ad1_candidate_scoreboard.csv", index=False)
    controls.to_csv(OUT_DIR / "a7ad1_control_scoreboard.csv", index=False)
    dominance.to_csv(OUT_DIR / "a7ad1_negative_control_dominance.csv", index=False)
    clues.to_csv(OUT_DIR / "a7ad1_research_clue_shortlist_pre_may_only.csv", index=False)
    family_summary.to_csv(OUT_DIR / "a7ad1_family_summary.csv", index=False)
    control_summary.to_csv(OUT_DIR / "a7ad1_control_summary.csv", index=False)
    write_json(OUT_DIR / "a7ad1_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ad1_manifest.json", manifest)

    top_cols = [
        "candidate_id",
        "family",
        "expression",
        "horizon",
        "raw_validation_2025H1_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_20bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag1",
        "residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0",
        "residual_core4_recent_2025H2_2026Apr_ann_10bps_lag0",
        "control_research_like_count",
        "decision",
        "reject_reasons",
    ]
    display = scoreboard.sort_values("raw_recent_2025H2_2026Apr_ann_10bps_lag0", ascending=False)
    report = f"""# CRYPTO A7AD-1 Core48 Controlled Replay Smoke

Generated: {now}

## Decision

```text
{decision}
```

This stage is a small controlled replay smoke on the core48 common window. It is not formula search, not large search, and not alpha proof.

## Summary

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Family Summary

{md_table(family_summary)}

## Control Summary

{md_table(control_summary)}

## Top Raw Recent Candidates

{md_table(display[top_cols], 30)}

## Pre-May Research Clue Shortlist

{md_table(clues[top_cols] if not clues.empty else clues, 40)}

## Boundary

- May is unavailable for the core48 common window and is not used.
- Matched controls are evaluated and any control-like pass demotes the candidate.
- FundingCore/Core4 are residual benchmarks only.
- Any shortlist item is `pre-May-only research clue`, not alpha proof and not shadow/paper/live eligible.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
