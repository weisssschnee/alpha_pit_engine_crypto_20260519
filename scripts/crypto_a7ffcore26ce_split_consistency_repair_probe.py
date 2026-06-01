from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore26ce_split_consistency_repair_probe"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE26CE_SPLIT_CONSISTENCY_REPAIR_PROBE_20260602.md"
CORE26C = REPO / "runtime" / "a7ffcore26c_split_consistency_repair_contract" / "a7ffcore26c_manifest.json"
NEAR_MISS = REPO / "runtime" / "a7ffcore26c_split_consistency_repair_contract" / "a7ffcore26c_near_miss_seed_snapshot.csv"
BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet")

TRAIN_SPLIT = "train_2024"
PREMAY_EVAL = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
COSTS = [2, 5]
MAX_TIMESTAMPS_PER_SPLIT = 256
PROBE_SYMBOL_LIMIT = 160
LABEL_PREFIX = {
    "L0_raw_forward_return": "L0",
    "L1_cross_sectional_relative_return": "L1",
    "L3_liquidity_tier_relative_return": "L3",
}


class CachedCryptoFeatureAlgebra(CryptoFeatureAlgebra):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._cache: dict[str, pd.Series] = {}

    def _eval(self, expression: str) -> pd.Series:
        key = expression.strip()
        if key in self._cache:
            return self._cache[key]
        values = super()._eval(key)
        self._cache[key] = values
        return values


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def short_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:14]


def stable_seed(text: str) -> int:
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16)


def transform_expr(field: str, transform: str) -> str:
    if transform.startswith("delta_"):
        h = transform.split("_", 1)[1].replace("h", "")
        return f"Delta({field},{h})"
    if transform.startswith("mean_"):
        h = transform.split("_", 1)[1].replace("h", "")
        return f"Mean({field},{h})"
    if transform.startswith("decay_"):
        h = transform.split("_", 1)[1].replace("h", "")
        return f"Decay({field},{h})"
    if transform.startswith("tsrank_"):
        h = transform.split("_", 1)[1].replace("h", "")
        return f"TSRank({field},{h})"
    if transform.startswith("zscore"):
        return f"ZScore({field})"
    if transform.startswith("abs_zscore"):
        return f"Abs(ZScore({field}))"
    if transform == "spread_short_long":
        return f"Sub(Mean({field},24),Mean({field},168))"
    return field


def make_expr(op: str, left: str, right: str) -> str:
    if op == "SafeDiv":
        return f"SafeDiv({left},Abs({right}))"
    if op in {"Sub", "Mul", "Add"}:
        return f"{op}({left},{right})"
    raise ValueError(op)


def generate_repair_pool() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    specs = {
        "S0_positioning_price_basis": {
            "quota": 180,
            "left_fields": ["top_long_short_position_ratio_last", "top_long_short_account_ratio_last"],
            "right_fields": ["trade_return_24h", "premium_close_bps", "mark_trade_basis_bps", "mark_index_basis_bps"],
            "left_transforms": ["delta_4h", "delta_8h", "delta_24h", "mean_24h", "decay_24h", "spread_short_long"],
            "right_transforms": ["delta_4h", "delta_8h", "delta_24h", "decay_24h", "decay_72h", "zscore_168h", "abs_zscore_168h"],
            "operators": ["Sub", "SafeDiv", "Mul"],
            "labels": ["L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L0_raw_forward_return"],
            "horizons": [8, 24],
        },
        "S3_cross_family_bridge": {
            "quota": 180,
            "left_fields": ["top_long_short_position_ratio_last", "liquidity_rank_active_universe", "median_quote_volume_168h"],
            "right_fields": ["mark_trade_basis_bps", "mark_index_basis_bps", "basis_abs_168h", "open_interest_value_last"],
            "left_transforms": ["delta_8h", "delta_24h", "mean_24h", "decay_24h", "spread_short_long"],
            "right_transforms": ["delta_8h", "delta_24h", "decay_24h", "decay_72h", "zscore_168h", "abs_zscore_168h"],
            "operators": ["SafeDiv", "Mul", "Sub"],
            "labels": ["L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L0_raw_forward_return"],
            "horizons": [8, 24],
        },
    }
    for lane, spec in specs.items():
        count = 0
        for left, lt, op, right, rt, label, horizon in product(
            spec["left_fields"],
            spec["left_transforms"],
            spec["operators"],
            spec["right_fields"],
            spec["right_transforms"],
            spec["labels"],
            spec["horizons"],
        ):
            left_expr = transform_expr(left, lt)
            right_expr = transform_expr(right, rt)
            expr = make_expr(op, left_expr, right_expr)
            blueprint_id = f"core26ce_{lane}_{short_hash(expr + '|' + label + '|' + str(horizon))}"
            rows.append(
                {
                    "blueprint_id": blueprint_id,
                    "seed_lane": lane,
                    "label_family": label,
                    "label_horizon_h": int(horizon),
                    "left_field": left,
                    "left_transform": lt,
                    "operator": op,
                    "right_field": right,
                    "right_transform": rt,
                    "expression": expr,
                    "candidate_role": "split_consistency_repair_probe",
                }
            )
            count += 1
            if count >= int(spec["quota"]):
                break
    return pd.DataFrame(rows).drop_duplicates("blueprint_id").reset_index(drop=True)


def load_schema(path: Path) -> set[str]:
    if path.is_dir():
        return set(ds.dataset(str(path), format="parquet").schema.names)
    return set(pq.ParquetFile(str(path)).schema_arrow.names)


def load_panel(required_fields: set[str]) -> pd.DataFrame:
    base_schema = load_schema(BASE_PANEL)
    latent_schema = load_schema(LATENT_PANEL)
    key_cols = ["symbol", "timestamp"]
    base_needed = set(required_fields) | {"trade_close"}
    latent_needed = set(required_fields) | {"split", "liquidity_tier_static", "realized_vol_168h"}
    base_cols = key_cols + sorted((base_needed & base_schema) - set(key_cols))
    latent_cols = key_cols + sorted((latent_needed & latent_schema) - set(key_cols) - set(base_cols))
    missing = sorted(required_fields - base_schema - latent_schema)
    if missing:
        raise ValueError(f"required fields missing from panels: {missing}")
    base = ds.dataset(str(BASE_PANEL), format="parquet").to_table(columns=base_cols).to_pandas()
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True).dt.tz_localize(None)
    latent = pd.read_parquet(LATENT_PANEL, columns=latent_cols)
    latent["timestamp"] = pd.to_datetime(latent["timestamp"], utc=True).dt.tz_localize(None)
    panel = base.merge(latent, on=key_cols, how="left", validate="one_to_one").sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    recent_mask = panel["split"].astype(str).eq("recent_2025H2_2026Apr")
    panel.loc[recent_mask & panel["timestamp"].lt(pd.Timestamp("2026-01-01")), "split"] = "test_2025H2"
    panel.loc[recent_mask & panel["timestamp"].ge(pd.Timestamp("2026-01-01")), "split"] = "recent_oos_2026JanApr"
    symbols = sorted(panel["symbol"].dropna().astype(str).unique())
    if len(symbols) > PROBE_SYMBOL_LIMIT:
        idx = np.linspace(0, len(symbols) - 1, PROBE_SYMBOL_LIMIT).round().astype(int)
        keep = {symbols[i] for i in idx}
        panel = panel[panel["symbol"].astype(str).isin(keep)].reset_index(drop=True)
    return panel


def add_labels(panel: pd.DataFrame, horizons: set[int]) -> None:
    close = panel.groupby("symbol", sort=False)["trade_close"]
    vol = pd.to_numeric(panel["realized_vol_168h"], errors="coerce").abs().replace(0.0, np.nan).clip(lower=1e-8)
    for h in sorted(horizons):
        raw = close.shift(-int(h)) / panel["trade_close"] - 1.0
        panel[f"L0_h{h}"] = raw
        panel[f"L1_h{h}"] = raw - panel.groupby("timestamp", sort=False)[f"L0_h{h}"].transform("mean")
        panel[f"L3_h{h}"] = raw - panel.groupby(["timestamp", "liquidity_tier_static"], sort=False)[f"L0_h{h}"].transform("mean")
        panel[f"L5_h{h}"] = raw / vol


def label_col(label: str, horizon: int) -> str:
    return f"{LABEL_PREFIX[label]}_h{int(horizon)}"


def sample_by_split(panel: pd.DataFrame) -> np.ndarray:
    selected = np.zeros(len(panel), dtype=bool)
    for split in [TRAIN_SPLIT] + PREMAY_EVAL:
        ts = np.array(sorted(panel.loc[panel["split"].eq(split), "timestamp"].dropna().unique()))
        if len(ts) > MAX_TIMESTAMPS_PER_SPLIT:
            idx = np.linspace(0, len(ts) - 1, MAX_TIMESTAMPS_PER_SPLIT).round().astype(int)
            ts = ts[idx]
        selected |= panel["timestamp"].isin(ts).to_numpy() & panel["split"].eq(split).to_numpy()
    return selected


def spread_metric(x: np.ndarray, y: np.ndarray) -> tuple[float, float, int]:
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < 100:
        return math.nan, math.nan, n
    xs = x[mask].astype(float)
    ys = y[mask].astype(float)
    corr = math.nan if xs.std() <= 1e-12 or ys.std() <= 1e-12 else float(np.corrcoef(xs, ys)[0, 1])
    q10, q90 = np.nanquantile(xs, [0.1, 0.9])
    spread = float(np.nanmean(ys[xs >= q90]) - np.nanmean(ys[xs <= q10]))
    return corr, spread, n


def controls(signal: pd.Series, sample_idx: np.ndarray, panel: pd.DataFrame, cid: str) -> dict[str, np.ndarray]:
    full = signal.astype(float)
    sampled = full.to_numpy()[sample_idx]
    rng = np.random.default_rng(stable_seed(cid))
    return {
        "wrong_lag_future": full.groupby(panel["symbol"], sort=False).shift(-1).to_numpy()[sample_idx],
        "wrong_lag_stale": full.groupby(panel["symbol"], sort=False).shift(24).to_numpy()[sample_idx],
        "time_shuffle": np.roll(sampled, 97),
        "symbol_shuffle": sampled[rng.permutation(len(sampled))],
        "same_family_placebo": rng.normal(0.0, np.nanstd(sampled) if np.isfinite(np.nanstd(sampled)) else 1.0, len(sampled)),
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core26c = read_json(CORE26C)
    if core26c.get("decision") != "PASS_A7FFCORE26C_SPLIT_CONSISTENCY_REPAIR_CONTRACT_READY_FOR_CORE26CE":
        raise SystemExit(f"CORE26C is not ready: {core26c.get('decision')}")
    repair_pool = generate_repair_pool()
    required_fields = set(repair_pool["left_field"].astype(str)) | set(repair_pool["right_field"].astype(str))
    panel = load_panel(required_fields)
    horizons = set(pd.to_numeric(repair_pool["label_horizon_h"], errors="coerce").dropna().astype(int))
    add_labels(panel, horizons)
    mask = sample_by_split(panel)
    sample_idx = np.flatnonzero(mask)
    sample = panel.iloc[sample_idx].copy()
    evaluator = CachedCryptoFeatureAlgebra(panel, allowed_fields=required_fields | {"trade_close", "realized_vol_168h", "liquidity_tier_static", "split"})

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for cand in repair_pool.to_dict("records"):
        cid = str(cand["blueprint_id"])
        label = str(cand["label_family"])
        horizon = int(cand["label_horizon_h"])
        try:
            signal = evaluator.evaluate(str(cand["expression"])).values
            one_bar = signal.groupby(panel["symbol"], sort=False).shift(1)
            x = one_bar.to_numpy()[sample_idx]
            ctrl = controls(one_bar, sample_idx, panel, cid)
        except Exception as exc:
            errors.append({"candidate_id": cid, "error": str(exc)})
            continue
        y = sample[label_col(label, horizon)].to_numpy(dtype=float)
        split_values = sample["split"].astype(str).to_numpy()
        train_mask = split_values == TRAIN_SPLIT
        _, train_spread, _ = spread_metric(x[train_mask], y[train_mask])
        orientation = 1.0 if not np.isfinite(train_spread) or train_spread >= 0 else -1.0
        for split in [TRAIN_SPLIT] + PREMAY_EVAL:
            smask = split_values == split
            corr, spread, n = spread_metric(x[smask], y[smask])
            oriented = spread * orientation if np.isfinite(spread) else math.nan
            control_scores = []
            for cx in ctrl.values():
                _, cspread, _ = spread_metric(cx[smask], y[smask])
                control_scores.append(abs(cspread) if np.isfinite(cspread) else 0.0)
            max_control = max(control_scores) if control_scores else 0.0
            ratio = max_control / max(abs(oriented) if np.isfinite(oriented) else 0.0, 1e-12)
            for cost in COSTS:
                rows.append(
                    {
                        "candidate_id": cid,
                        "seed_lane": cand["seed_lane"],
                        "label_family": label,
                        "label_horizon_h": horizon,
                        "left_field": cand["left_field"],
                        "left_transform": cand["left_transform"],
                        "operator": cand["operator"],
                        "right_field": cand["right_field"],
                        "right_transform": cand["right_transform"],
                        "split": split,
                        "cost_bps": cost,
                        "orientation": orientation,
                        "sample_rows": n,
                        "corr_one_bar": corr,
                        "one_bar_spread": oriented,
                        "one_bar_costed_spread": oriented - (2.0 * cost / 10000.0) if np.isfinite(oriented) else math.nan,
                        "max_control_spread": max_control,
                        "control_ratio": ratio,
                    }
                )
    result = pd.DataFrame(rows)
    errors_df = pd.DataFrame(errors)
    eval_rows = result[result["split"].isin(PREMAY_EVAL) & result["cost_bps"].eq(2)].copy()
    eval_rows["pass_both"] = eval_rows["one_bar_costed_spread"].gt(0) & eval_rows["control_ratio"].lt(1.0)
    split_counts = eval_rows[eval_rows["pass_both"]].groupby("candidate_id")["split"].nunique()
    clean_ids = set(split_counts[split_counts >= len(PREMAY_EVAL)].index.astype(str))
    near_ids = set(split_counts[split_counts >= 2].index.astype(str))
    clean = repair_pool[repair_pool["blueprint_id"].astype(str).isin(clean_ids)].copy()
    near = repair_pool[repair_pool["blueprint_id"].astype(str).isin(near_ids - clean_ids)].copy()
    candidate_summary = (
        eval_rows.groupby(["candidate_id", "seed_lane", "label_family", "label_horizon_h"], dropna=False)
        .agg(
            pass_splits=("pass_both", "sum"),
            min_spread=("one_bar_costed_spread", "min"),
            mean_spread=("one_bar_costed_spread", "mean"),
            max_control_ratio=("control_ratio", "max"),
            min_sample_rows=("sample_rows", "min"),
        )
        .reset_index()
    )
    lane_summary = (
        candidate_summary.groupby("seed_lane", dropna=False)
        .agg(
            candidates=("candidate_id", "nunique"),
            clean_3_split=("pass_splits", lambda s: int((s >= 3).sum())),
            near_2_split=("pass_splits", lambda s: int((s >= 2).sum())),
            median_control=("max_control_ratio", "median"),
            median_spread=("mean_spread", "median"),
        )
        .reset_index()
    )
    clean_count = int(clean["blueprint_id"].nunique())
    clean_lane_count = int(clean["seed_lane"].nunique()) if not clean.empty else 0
    near_count = int(near["blueprint_id"].nunique())
    blockers: list[str] = []
    if len(errors) > 0:
        blockers.append("eval_errors_present")
    if clean_count < 6:
        blockers.append("three_split_clean_count_lt_6")
    if clean_lane_count < 3:
        blockers.append("three_split_clean_lane_count_lt_3")
    if near_count < 12:
        blockers.append("two_split_near_miss_count_lt_12")
    decision = "PASS_A7FFCORE26CE_SPLIT_REPAIR_READY_FOR_CORE27_CONTRACT" if not blockers else "HOLD_A7FFCORE26CE_SPLIT_REPAIR_INSUFFICIENT"

    repair_pool.to_csv(RUNTIME / "a7ffcore26ce_repair_pool.csv", index=False)
    result.to_csv(RUNTIME / "a7ffcore26ce_numeric_rows.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore26ce_candidate_summary.csv", index=False)
    clean.to_csv(RUNTIME / "a7ffcore26ce_clean_candidates.csv", index=False)
    near.to_csv(RUNTIME / "a7ffcore26ce_near_miss_candidates.csv", index=False)
    lane_summary.to_csv(RUNTIME / "a7ffcore26ce_lane_summary.csv", index=False)
    errors_df.to_csv(RUNTIME / "a7ffcore26ce_eval_errors.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE26CE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE26C",
        "source_decision": core26c.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "repair_pool_count": int(repair_pool["blueprint_id"].nunique()),
        "numeric_rows": int(result.shape[0]),
        "eval_error_count": int(len(errors)),
        "three_split_clean_count": clean_count,
        "three_split_clean_lane_count": clean_lane_count,
        "two_split_near_miss_count": near_count,
        "authorizes_core27_contract": decision.startswith("PASS_"),
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE27 bounded replay contract" if decision.startswith("PASS_") else "A7FF-CORE26CER split repair forensic",
    }
    write_json(RUNTIME / "a7ffcore26ce_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE26CE SPLIT-CONSISTENCY REPAIR PROBE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE26CE executes a bounded S0/S3 split-consistency repair numeric probe. It does not authorize search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Lane Summary",
        "",
        md_table(lane_summary),
        "",
        "## Clean Candidates",
        "",
        md_table(clean.head(40)),
        "",
        "## Near Miss Candidates",
        "",
        md_table(near.head(40)),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
