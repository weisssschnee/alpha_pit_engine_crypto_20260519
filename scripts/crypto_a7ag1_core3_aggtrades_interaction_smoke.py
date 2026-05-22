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
PANEL_PATH = DATA_ROOT / "gold" / "features" / "binance_core3_all_features_metrics_market_structure_aggtrades_v1.parquet"
A7AG0_AUTH = ROOT / "runtime" / "a7ag0_core3_aggtrades_interaction_contract" / "a7ag0_authorization_matrix.json"
A7AG0_FIELDS = ROOT / "runtime" / "a7ag0_core3_aggtrades_interaction_contract" / "a7ag0_interaction_field_contract.csv"

OUT_DIR = ROOT / "runtime" / "a7ag1_core3_aggtrades_interaction_smoke"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AG1_CORE3_AGGTRADES_INTERACTION_SMOKE_20260522.md"

SPLITS = {
    "validation_2025H1": ("2025-01-01 00:00:00+00:00", "2025-06-30 23:00:00+00:00"),
    "recent_2025H2_2026Apr": ("2025-07-01 00:00:00+00:00", "2026-04-30 23:00:00+00:00"),
    "may_2026_stress": ("2026-05-01 00:00:00+00:00", "2026-05-20 23:00:00+00:00"),
}

ANNUALIZATION = 24 * 365


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


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
        "candidate_id": f"a7ag1_{family}_{horizon}_{stable_id(expr)}",
        "family": family,
        "expression": expr,
        "horizon": horizon,
        "source_fields": ";".join(sorted(set(fields))),
    }


def generate_candidates(columns: set[str]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    def add(family: str, expr: str, horizon: int, fields: list[str]) -> None:
        if all(field in columns for field in fields):
            rows.append(candidate_row(family, expr, horizon, fields))

    agg_flow = [
        "agg_signed_flow_z_24h",
        "agg_flow_imbalance_notional_24h",
        "agg_flow_accel_4h_vs_24h",
        "agg_cross_symbol_signed_flow_share",
    ]
    agg_large = ["agg_large_notional_share_24h", "agg_large_notional_share_4h", "agg_cross_symbol_large_notional_share"]
    contexts = ["mark_index_basis_change_24h", "premium_index_change_24h", "open_interest_change_24h", "ret_24"]
    crowding = ["top_long_short_position_ratio_zscore_168h"]

    for horizon in [24, 48, 72]:
        for agg in agg_flow:
            for ctx in contexts:
                add("H0_agg_flow_x_context", f"Mul(Rank({agg}),Rank({ctx}))", horizon, [agg, ctx])
                add("H0_agg_flow_x_context", f"Mul(Neg(Rank({agg})),Rank({ctx}))", horizon, [agg, ctx])
        for agg in agg_large:
            for ctx in contexts[:3]:
                add("H1_large_trade_x_context", f"Mul(Rank({agg}),Rank({ctx}))", horizon, [agg, ctx])
        for agg in agg_flow[:3]:
            for crowd in crowding:
                add("H2_flow_x_crowding", f"Mul(Rank({agg}),Neg(ZScore({crowd})))", horizon, [agg, crowd])
        add("H3_flow_pressure_benchmark", "Mul(Rank(flow_pressure_score_v1),Rank(mark_index_basis_change_24h))", horizon, ["flow_pressure_score_v1", "mark_index_basis_change_24h"])
        add("H3_flow_pressure_benchmark", "Mul(Rank(flow_pressure_score_v1),Rank(ret_24))", horizon, ["flow_pressure_score_v1", "ret_24"])
    return pd.DataFrame(rows).drop_duplicates("candidate_id").head(90).reset_index(drop=True)


def load_panel(required_fields: list[str]) -> tuple[pd.DataFrame, list[str], list[pd.Timestamp]]:
    schema = pq.read_schema(PANEL_PATH)
    cols = [col for col in ["symbol", "timestamp", "ret_1", "funding_rate_bps"] + required_fields if col in schema.names]
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
        mean = float(np.nanmean(vals))
        std = float(np.nanstd(vals))
        out[f"{split}_ann"] = mean * ANNUALIZATION
        out[f"{split}_sharpe"] = mean / std * math.sqrt(ANNUALIZATION) if std > 1e-12 else None
        out[f"{split}_sum"] = float(np.nansum(vals))
        out[f"{split}_active_hours"] = int(vals.size)
    return out


def prefixed(metrics: dict[str, Any], prefix: str, cost_bps: float, lag: int) -> dict[str, Any]:
    return {f"{prefix}_{key}_{int(cost_bps)}bps_lag{lag}": value for key, value in metrics.items()}


def evaluate_candidate(expr: str, horizon: int, ctx: ExprContext, ret_1: np.ndarray, funding: np.ndarray, masks: dict[str, np.ndarray]) -> dict[str, Any]:
    signal = ctx.eval(expr)
    residual = row_residualize(signal, row_zscore(funding))
    row: dict[str, Any] = {}
    for cost, lag in [(10.0, 0), (20.0, 0), (10.0, 1), (10.0, 2)]:
        row.update(prefixed(replay(signal, ret_1, masks, horizon, cost, lag), "raw", cost, lag))
        row.update(prefixed(replay(residual, ret_1, masks, horizon, cost, lag), "residual_funding", cost, lag))
    return row


def numeric_positive(row: pd.Series, col: str) -> bool:
    try:
        value = float(row[col])
    except Exception:
        return False
    return math.isfinite(value) and value > 0.0


def decision_for_row(row: pd.Series) -> tuple[str, str]:
    reasons: list[str] = []
    gates = [
        ("raw_validation_2025H1_ann_10bps_lag0", "raw_validation_nonpositive"),
        ("raw_recent_2025H2_2026Apr_ann_10bps_lag0", "raw_recent_nonpositive"),
        ("raw_recent_2025H2_2026Apr_ann_20bps_lag0", "cost20_recent_nonpositive"),
        ("raw_recent_2025H2_2026Apr_ann_10bps_lag1", "lag1_recent_nonpositive"),
        ("raw_recent_2025H2_2026Apr_ann_10bps_lag2", "lag2_recent_nonpositive"),
        ("residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0", "residual_funding_recent_nonpositive"),
    ]
    for col, reason in gates:
        if not numeric_positive(row, col):
            reasons.append(reason)
    if int(row.get("control_research_like_count", 0)) > 0:
        reasons.append("negative_control_not_dominated")
    pre_may_ok = not reasons
    may_ok = numeric_positive(row, "raw_may_2026_stress_ann_10bps_lag0") and numeric_positive(row, "residual_funding_may_2026_stress_ann_10bps_lag0")
    if pre_may_ok and may_ok:
        return "A7AG1_POST_MAY_RESEARCH_CLUE", ""
    if pre_may_ok:
        return "A7AG1_PRE_MAY_ONLY_CLUE", "may_stress_not_positive"
    return "A7AG1_REJECTED", ";".join(sorted(set(reasons)))


def control_variants(candidate: pd.Series, signal: np.ndarray, matrices: dict[str, np.ndarray]) -> list[tuple[str, np.ndarray]]:
    rng = np.random.default_rng(stable_seed(candidate["candidate_id"]))
    variants: list[tuple[str, np.ndarray]] = [("sign_flip", -signal)]
    flat = signal.reshape(-1).copy()
    rng.shuffle(flat)
    variants.append(("row_shuffle", flat.reshape(signal.shape)))
    shift = min(24, signal.shape[0] - 1)
    stale = np.vstack([np.full((shift, signal.shape[1]), np.nan), signal[:-shift, :]]) if shift > 0 else signal.copy()
    variants.append(("wrong_lag_stale_24h", stale))
    time_idx = np.arange(signal.shape[0])
    rng.shuffle(time_idx)
    variants.append(("time_shuffle", signal[time_idx, :]))
    return variants


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    auth_prev = json.loads(A7AG0_AUTH.read_text(encoding="utf-8"))
    if not auth_prev.get("authorizes_a7ag1_small_controlled_interaction_smoke"):
        raise RuntimeError("A7AG0 does not authorize A7AG1")

    contract = pd.read_csv(A7AG0_FIELDS)
    candidate_fields = contract["field_name"].dropna().tolist() + ["ret_24", "funding_rate_bps"]
    schema = pq.read_schema(PANEL_PATH)
    generated = generate_candidates(set(schema.names))
    required = sorted(set(";".join(generated["source_fields"]).split(";") + candidate_fields))
    df, symbols, timestamps = load_panel(required)
    matrices = {field: matrix(df, symbols, timestamps, field) for field in required if field in df.columns}
    ret_1 = matrix(df, symbols, timestamps, "ret_1")
    funding = matrix(df, symbols, timestamps, "funding_rate_bps") if "funding_rate_bps" in df.columns else np.zeros_like(ret_1)
    ctx = ExprContext(matrices)
    masks = split_masks(timestamps)

    rows: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    signal_cache: dict[str, np.ndarray] = {}
    for _, cand in generated.iterrows():
        signal = ctx.eval(cand["expression"])
        signal_cache[cand["candidate_id"]] = signal
        row = cand.to_dict()
        row.update(evaluate_candidate(cand["expression"], int(cand["horizon"]), ctx, ret_1, funding, masks))
        rows.append(row)
        for mode, variant in control_variants(cand, signal, matrices):
            cmetrics = replay(variant, ret_1, masks, int(cand["horizon"]), 10.0, 0)
            controls.append(
                {
                    "control_id": f"{cand['candidate_id']}__{mode}",
                    "base_candidate_id": cand["candidate_id"],
                    "family": cand["family"],
                    "control_mode": mode,
                    **{f"raw_{key}_10bps_lag0": value for key, value in cmetrics.items()},
                }
            )

    score = pd.DataFrame(rows)
    control_df = pd.DataFrame(controls)
    control_df["control_research_like"] = (
        pd.to_numeric(control_df["raw_validation_2025H1_ann_10bps_lag0"], errors="coerce").fillna(-np.inf).gt(0)
        & pd.to_numeric(control_df["raw_recent_2025H2_2026Apr_ann_10bps_lag0"], errors="coerce").fillna(-np.inf).gt(0)
        & pd.to_numeric(control_df["raw_may_2026_stress_ann_10bps_lag0"], errors="coerce").fillna(-np.inf).gt(0)
    )
    control_counts = control_df.groupby("base_candidate_id", observed=True)["control_research_like"].sum().rename("control_research_like_count")
    max_control_recent = control_df.groupby("base_candidate_id", observed=True)["raw_recent_2025H2_2026Apr_ann_10bps_lag0"].max().rename("max_control_recent_ann_10bps_lag0")
    score = score.merge(control_counts, left_on="candidate_id", right_index=True, how="left")
    score = score.merge(max_control_recent, left_on="candidate_id", right_index=True, how="left")
    score["control_research_like_count"] = score["control_research_like_count"].fillna(0).astype(int)
    decisions = score.apply(decision_for_row, axis=1, result_type="expand")
    score["decision"] = decisions[0]
    score["reject_reasons"] = decisions[1]

    shortlist = score[score["decision"].isin(["A7AG1_POST_MAY_RESEARCH_CLUE", "A7AG1_PRE_MAY_ONLY_CLUE"])].copy()
    post_may = score[score["decision"].eq("A7AG1_POST_MAY_RESEARCH_CLUE")].copy()
    control_summary = (
        control_df.groupby(["family", "control_mode", "control_research_like"], observed=True)
        .size()
        .reset_index(name="count")
        .sort_values(["control_research_like", "count"], ascending=[False, False])
    )
    family_summary = score.groupby(["family", "decision"], observed=True).size().reset_index(name="count")

    neg_controls = int(control_df["control_research_like"].sum())
    decision = "PASS_A7AG1_CORE3_AGGTRADES_INTERACTION_POST_MAY_CLUES" if len(post_may) > 0 and neg_controls == 0 else "HOLD_A7AG1_NO_POST_MAY_CONTROL_CLEAN_CLUE"
    if neg_controls > 0:
        decision = "HOLD_A7AG1_NEGATIVE_CONTROL_PENETRATION"
    elif len(shortlist) > 0 and len(post_may) == 0:
        decision = "HOLD_A7AG1_PRE_MAY_ONLY_CLUES"

    auth = {
        "decision": decision,
        "authorizes_a7ag2_forensic": True,
        "authorizes_expanded_replay": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "May was evaluated after fixed candidate generation; no May ranking, symbol tuning, threshold tuning, or generation",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "generated_candidates": int(len(generated)),
        "shortlist": int(len(shortlist)),
        "post_may_clues": int(len(post_may)),
        "control_rows": int(len(control_df)),
        "negative_control_research_like": neg_controls,
        "symbols": len(symbols),
        "timestamps": len(timestamps),
        "executes_replay": True,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    generated.to_csv(OUT_DIR / "a7ag1_generated_candidates.csv", index=False)
    score.to_csv(OUT_DIR / "a7ag1_candidate_scoreboard.csv", index=False)
    control_df.to_csv(OUT_DIR / "a7ag1_control_scoreboard.csv", index=False)
    shortlist.to_csv(OUT_DIR / "a7ag1_research_clue_shortlist.csv", index=False)
    post_may.to_csv(OUT_DIR / "a7ag1_post_may_clues.csv", index=False)
    family_summary.to_csv(OUT_DIR / "a7ag1_family_summary.csv", index=False)
    control_summary.to_csv(OUT_DIR / "a7ag1_control_summary.csv", index=False)
    write_json(OUT_DIR / "a7ag1_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ag1_manifest.json", manifest)

    top_cols = [
        "candidate_id",
        "family",
        "expression",
        "horizon",
        "raw_validation_2025H1_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_20bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag1",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag2",
        "raw_may_2026_stress_ann_10bps_lag0",
        "residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0",
        "residual_funding_may_2026_stress_ann_10bps_lag0",
        "control_research_like_count",
        "decision",
        "reject_reasons",
    ]
    report = f"""# CRYPTO A7AG-1 Core3 aggTrades Interaction Smoke

Generated: {now}

## Decision

```text
{decision}
```

This is a small controlled smoke for core3 aggTrades interaction/state candidates. It is not formula search and not execution-grade proof.

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

## Shortlist

{md_table(shortlist[top_cols] if not shortlist.empty else shortlist)}

## Top Candidates By Recent

{md_table(score.sort_values("raw_recent_2025H2_2026Apr_ann_10bps_lag0", ascending=False)[top_cols], max_rows=40)}

## Boundary

- May stress is post-selection only.
- aggTrades standalone activity/liquidity family remains blocked.
- Funding remains a residual/control baseline.
- `ret_1` proxy replay is method smoke only.
- Any clue requires A7AG-2 forensic before expansion.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
