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
PANEL_PATH = DATA_ROOT / "gold" / "features" / "binance_core39_all_features_metrics_v3_market_structure_v1.parquet"
A7AF0_AUTH = ROOT / "runtime" / "a7af0_core39_selected_field_replay_contract" / "a7af0_authorization_matrix.json"

OUT_DIR = ROOT / "runtime" / "a7af1_core39_selected_field_smoke"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AF1_CORE39_SELECTED_FIELD_SMOKE_20260522.md"

SPLITS = {
    "validation_2025H1": ("2025-01-01 00:00:00+00:00", "2025-06-30 23:00:00+00:00"),
    "recent_2025H2_2026Apr": ("2025-07-01 00:00:00+00:00", "2026-04-30 23:00:00+00:00"),
    "may_2026_stress": ("2026-05-01 00:00:00+00:00", "2026-05-21 23:00:00+00:00"),
}

ANNUALIZATION = 24 * 365
PRIMARY_COST_BPS = 10.0
SEVERE_COST_BPS = 20.0


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
            raise KeyError(expr)
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
        raise ValueError(f"unsupported op {op}")


def candidate_row(family: str, expr: str, horizon: int, fields: list[str]) -> dict[str, Any]:
    return {
        "candidate_id": f"a7af1_{family}_{horizon}_{stable_id(expr)}",
        "family": family,
        "expression": expr,
        "horizon": horizon,
        "source_fields": ";".join(sorted(set(fields))),
    }


def generate_candidates(columns: set[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    def add(family: str, expr: str, horizon: int, fields: list[str]) -> None:
        if all(f in columns for f in fields):
            rows.append(candidate_row(family, expr, horizon, fields))

    horizons = [24, 48]
    basis_dyn = ["mark_index_basis_change_24h", "mark_index_basis_zscore_168h", "premium_index_change_24h", "premium_index_bps"]
    crowd = [
        "global_long_short_account_ratio_zscore_168h",
        "top_long_short_account_ratio_zscore_168h",
        "top_long_short_position_ratio_zscore_168h",
        "taker_buy_sell_volume_ratio_zscore_168h",
    ]
    oi_dyn = ["open_interest_change_24h", "open_interest_zscore_168h", "open_interest_value_zscore_168h"]
    contexts = ["ret_24", "mark_index_basis_change_24h", "premium_index_change_24h"]
    for h in horizons:
        for b in basis_dyn:
            add("G0_basis_premium_dynamic", f"Rank({b})", h, [b])
            add("G0_basis_premium_dynamic", f"Neg(Rank({b}))", h, [b])
        for c in crowd:
            for b in basis_dyn[:3]:
                add("G1_crowding_x_basis_dynamic", f"Mul(Neg(ZScore({c})),Rank({b}))", h, [c, b])
        for oi in oi_dyn:
            for b in basis_dyn[:3]:
                add("G2_oi_dynamic_x_basis_dynamic", f"Mul(ZScore({oi}),Rank({b}))", h, [oi, b])
        for c in crowd:
            for ctx in contexts:
                add("G3_crowding_x_context", f"Mul(Neg(ZScore({c})),Rank({ctx}))", h, [c, ctx])
        for oi in ["open_interest_change_24h"]:
            for ctx in contexts:
                add("G4_oi_change_x_context", f"Mul(ZScore({oi}),Rank({ctx}))", h, [oi, ctx])
        add("G5_funding_basis_benchmark", "Mul(ZScore(funding_rate_change_3obs),Rank(mark_index_basis_change_24h))", h, ["funding_rate_change_3obs", "mark_index_basis_change_24h"])
        add("G5_funding_basis_benchmark", "Mul(ZScore(funding_rate_bps),Rank(premium_index_change_24h))", h, ["funding_rate_bps", "premium_index_change_24h"])

    return pd.DataFrame(rows).drop_duplicates("candidate_id").head(120).reset_index(drop=True)


def load_panel(required_fields: list[str]) -> tuple[pd.DataFrame, list[str], list[pd.Timestamp]]:
    schema = pq.read_schema(PANEL_PATH)
    cols = [c for c in ["symbol", "timestamp", "ret_1"] + required_fields if c in schema.names]
    df = pd.read_parquet(PANEL_PATH, columns=sorted(set(cols)), engine="pyarrow")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    symbols = sorted(df["symbol"].dropna().unique().tolist())
    timestamps = sorted(df["timestamp"].dropna().unique().tolist())
    return df, symbols, timestamps


def matrix(df: pd.DataFrame, symbols: list[str], timestamps: list[pd.Timestamp], field: str) -> np.ndarray:
    return df.pivot(index="timestamp", columns="symbol", values=field).reindex(index=timestamps, columns=symbols).to_numpy(dtype=float)


def forward_return_from_ret1(ret_1: np.ndarray, horizon: int, lag: int) -> np.ndarray:
    logret = np.log1p(np.clip(ret_1, -0.99, 10.0))
    logret[~np.isfinite(logret)] = np.nan
    out = np.full_like(logret, np.nan, dtype=float)
    for k in range(horizon):
        shift = 1 + lag + k
        if shift >= logret.shape[0]:
            break
        vals = logret[shift:, :]
        target = out[: logret.shape[0] - shift, :]
        if k == 0:
            target[:] = vals
        else:
            target[:] = target + vals
    out = np.expm1(out)
    out[~np.isfinite(out)] = np.nan
    return out


def positions(signal: np.ndarray) -> np.ndarray:
    z = row_zscore(signal)
    denom = np.nansum(np.abs(z), axis=1, keepdims=True)
    out = np.divide(z, denom, out=np.zeros_like(z), where=denom > 1e-12)
    out[~np.isfinite(out)] = 0.0
    return out


def split_masks(timestamps: list[pd.Timestamp]) -> dict[str, np.ndarray]:
    ts = pd.DatetimeIndex(timestamps)
    return {name: (ts >= pd.Timestamp(start)) & (ts <= pd.Timestamp(end)) for name, (start, end) in SPLITS.items()}


def replay(signal: np.ndarray, ret_1: np.ndarray, masks: dict[str, np.ndarray], horizon: int, cost_bps: float, lag: int) -> dict[str, Any]:
    pos = positions(signal)
    fwd = forward_return_from_ret1(ret_1, horizon, lag)
    gross = np.nansum(pos * fwd, axis=1)
    exposure = np.nansum(np.abs(pos), axis=1)
    prev = np.vstack([np.zeros((1, pos.shape[1])), pos[:-1, :]])
    turnover = np.nansum(np.abs(pos - prev), axis=1)
    net = gross - turnover * (cost_bps / 10000.0)
    out: dict[str, Any] = {}
    for split, mask in masks.items():
        valid = mask & np.isfinite(net) & (exposure > 1e-9)
        vals = net[valid]
        if vals.size == 0:
            out[f"{split}_ann"] = None
            out[f"{split}_sharpe"] = None
            out[f"{split}_sum"] = None
            out[f"{split}_active_hours"] = 0
            continue
        std = float(np.nanstd(vals))
        out[f"{split}_ann"] = clean_float(float(np.nanmean(vals) * ANNUALIZATION))
        out[f"{split}_sharpe"] = clean_float(float(np.nanmean(vals) / std * math.sqrt(ANNUALIZATION)) if std > 1e-12 else None)
        out[f"{split}_sum"] = clean_float(float(np.nansum(vals)))
        out[f"{split}_active_hours"] = int(vals.size)
    return out


def control_signal(signal: np.ndarray, mode: str, seed_text: str) -> np.ndarray:
    rng = np.random.default_rng(stable_seed(seed_text + mode))
    if mode == "sign_flip":
        return -signal
    if mode == "wrong_lag_stale_24h":
        out = np.full_like(signal, np.nan)
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
    checks = {
        "raw_validation_nonpositive": row.get("raw_validation_2025H1_ann_10bps_lag0"),
        "raw_recent_nonpositive": row.get("raw_recent_2025H2_2026Apr_ann_10bps_lag0"),
        "cost20_recent_nonpositive": row.get("raw_recent_2025H2_2026Apr_ann_20bps_lag0"),
        "lag1_recent_nonpositive": row.get("raw_recent_2025H2_2026Apr_ann_10bps_lag1"),
        "residual_funding_recent_nonpositive": row.get("residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0"),
    }
    for reason, value in checks.items():
        if value is None or float(value) <= 0:
            reasons.append(reason)
    if reasons:
        return "A7AF1_REJECTED", reasons
    may = row.get("raw_may_2026_stress_ann_10bps_lag0")
    if may is not None and float(may) > 0:
        return "A7AF1_POST_MAY_ELIGIBLE_RESEARCH_CLUE", []
    return "A7AF1_PRE_MAY_ONLY_CLUE", ["may_stress_nonpositive_or_missing"]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    auth0 = json.loads(A7AF0_AUTH.read_text(encoding="utf-8"))
    if not auth0.get("authorizes_a7af1_small_controlled_smoke"):
        raise RuntimeError("A7AF0 does not authorize A7AF1")

    schema_names = set(pq.read_schema(PANEL_PATH).names)
    candidates = generate_candidates(schema_names)
    required = sorted(set(";".join(candidates["source_fields"].tolist()).split(";") + ["funding_rate_bps", "ret_24"]))
    df, symbols, timestamps = load_panel(required)
    mats = {field: matrix(df, symbols, timestamps, field) for field in sorted(set(required + ["ret_1", "funding_rate_bps", "ret_24"])) if field in df.columns}
    ctx = ExprContext(mats)
    masks = split_masks(timestamps)
    ret_1 = mats["ret_1"]
    funding_proxy = row_zscore(mats["funding_rate_bps"]) if "funding_rate_bps" in mats else row_zscore(np.zeros_like(ret_1))

    rows: list[dict[str, Any]] = []
    control_rows: list[dict[str, Any]] = []
    for _, cand in candidates.iterrows():
        signal = ctx.eval(cand["expression"])
        rec: dict[str, Any] = cand.to_dict()
        for prefix, sig in [("raw", signal), ("residual_funding", row_residualize(signal, funding_proxy))]:
            for cost, lag in [(10.0, 0), (20.0, 0), (10.0, 1)]:
                metrics = replay(sig, ret_1, masks, int(cand["horizon"]), cost, lag)
                for key, value in metrics.items():
                    rec[f"{prefix}_{key}_{int(cost)}bps_lag{lag}"] = value
        control_like = 0
        max_control_recent = -999.0
        for mode in ["sign_flip", "row_shuffle", "time_shuffle", "wrong_lag_stale_24h"]:
            ctrl = control_signal(signal, mode, cand["candidate_id"])
            cmetrics = replay(ctrl, ret_1, masks, int(cand["horizon"]), 10.0, 0)
            crecord: dict[str, Any] = {
                "control_id": f"{cand['candidate_id']}__{mode}",
                "base_candidate_id": cand["candidate_id"],
                "family": cand["family"],
                "control_mode": mode,
            }
            for key, value in cmetrics.items():
                crecord[f"raw_{key}_10bps_lag0"] = value
            comparable = (
                (crecord.get("raw_validation_2025H1_ann_10bps_lag0") or -999.0) > 0
                and (crecord.get("raw_recent_2025H2_2026Apr_ann_10bps_lag0") or -999.0) > 0
            )
            crecord["control_research_like"] = bool(comparable)
            control_like += int(comparable)
            max_control_recent = max(max_control_recent, float(crecord.get("raw_recent_2025H2_2026Apr_ann_10bps_lag0") or -999.0))
            control_rows.append(crecord)
        label, reasons = classify(rec)
        if control_like:
            label = "A7AF1_REJECTED"
            reasons.append("negative_control_not_dominated")
        rec["decision"] = label
        rec["reject_reasons"] = ";".join(sorted(set(reasons)))
        rec["control_research_like_count"] = control_like
        rec["max_control_recent_ann_10bps_lag0"] = clean_float(max_control_recent)
        rows.append(rec)

    scoreboard = pd.DataFrame(rows)
    controls = pd.DataFrame(control_rows)
    clues = scoreboard[scoreboard["decision"].isin(["A7AF1_POST_MAY_ELIGIBLE_RESEARCH_CLUE", "A7AF1_PRE_MAY_ONLY_CLUE"])].copy()
    post_may = scoreboard[scoreboard["decision"].eq("A7AF1_POST_MAY_ELIGIBLE_RESEARCH_CLUE")].copy()
    family_summary = scoreboard.groupby(["family", "decision"], observed=True).size().reset_index(name="count")
    control_summary = controls.groupby(["family", "control_mode", "control_research_like"], observed=True).size().reset_index(name="count")
    negative_control_like = int(controls["control_research_like"].sum()) if not controls.empty else 0

    if len(post_may) > 0 and negative_control_like == 0:
        decision = "PASS_A7AF1_SELECTED_FIELD_SMOKE_HAS_POST_MAY_CLUES"
    elif len(clues) > 0:
        decision = "HOLD_A7AF1_PRE_MAY_ONLY_OR_CONTROL_LIMITED_CLUES"
    else:
        decision = "HOLD_A7AF1_NO_CONTROL_CLEAN_CLUE"
    auth = {
        "decision": decision,
        "authorizes_a7af2_forensic": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "May was evaluated only after fixed candidate generation; no May ranking or selection",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "generated_candidates": int(len(candidates)),
        "control_rows": int(len(controls)),
        "negative_control_research_like": negative_control_like,
        "clues": int(len(clues)),
        "post_may_clues": int(len(post_may)),
        "symbols": int(len(symbols)),
        "timestamps": int(len(timestamps)),
        "executes_replay": True,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    candidates.to_csv(OUT_DIR / "a7af1_generated_candidates.csv", index=False)
    scoreboard.to_csv(OUT_DIR / "a7af1_candidate_scoreboard.csv", index=False)
    controls.to_csv(OUT_DIR / "a7af1_control_scoreboard.csv", index=False)
    clues.to_csv(OUT_DIR / "a7af1_research_clue_shortlist.csv", index=False)
    family_summary.to_csv(OUT_DIR / "a7af1_family_summary.csv", index=False)
    control_summary.to_csv(OUT_DIR / "a7af1_control_summary.csv", index=False)
    write_json(OUT_DIR / "a7af1_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7af1_manifest.json", manifest)

    top_cols = [
        "candidate_id",
        "family",
        "expression",
        "horizon",
        "raw_validation_2025H1_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_20bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag1",
        "raw_may_2026_stress_ann_10bps_lag0",
        "residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0",
        "control_research_like_count",
        "decision",
        "reject_reasons",
    ]
    report = f"""# CRYPTO A7AF-1 Core39 Selected-Field Smoke

Generated: {now}

## Decision

```text
{decision}
```

This is a selected-field controlled replay smoke using a `ret_1` forward-return proxy. It is not execution-grade proof and not formula search.

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

## Top Candidates By Recent

{md_table(scoreboard.sort_values('raw_recent_2025H2_2026Apr_ann_10bps_lag0', ascending=False)[top_cols], 40)}

## Clue Shortlist

{md_table(clues[top_cols] if not clues.empty else clues, 60)}

## Boundary

- May stress is post-selection only.
- `ret_1` proxy replay is method smoke only; no execution-grade proof.
- Funding remains residual/control baseline.
- Any clue still requires A7AF-2 forensic before further replay.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
