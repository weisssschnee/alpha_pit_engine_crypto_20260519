from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore26e_targeted_numeric_probe_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE26E_TARGETED_NUMERIC_PROBE_EXECUTION_20260602.md"
CORE26 = REPO / "runtime" / "a7ffcore26_targeted_numeric_probe_contract" / "a7ffcore26_manifest.json"
PACKET = REPO / "runtime" / "a7ffcore25e_targeted_lane_horizon_generation" / "a7ffcore25e_preflight_packet.csv"
BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet")

PREMAY_EVAL = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
TRAIN_SPLIT = "train_2024"
COSTS = [2, 5, 10]
MAX_TIMESTAMPS_PER_SPLIT = 384
PROBE_SYMBOL_LIMIT = 192
LABEL_PREFIX = {
    "L0_raw_forward_return": "L0",
    "L1_cross_sectional_relative_return": "L1",
    "L3_liquidity_tier_relative_return": "L3",
    "L5_vol_adjusted_return": "L5",
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


def stable_seed(text: str) -> int:
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16)


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
    missing = sorted((required_fields - base_schema - latent_schema))
    if missing:
        raise ValueError(f"required fields missing from base/latent panels: {missing}")
    base = ds.dataset(str(BASE_PANEL), format="parquet").to_table(columns=base_cols).to_pandas()
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True).dt.tz_localize(None)
    latent = pd.read_parquet(LATENT_PANEL, columns=latent_cols)
    latent["timestamp"] = pd.to_datetime(latent["timestamp"], utc=True).dt.tz_localize(None)
    panel = base.merge(latent, on=key_cols, how="left", validate="one_to_one")
    panel = panel.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    recent_mask = panel["split"].astype(str).eq("recent_2025H2_2026Apr")
    panel.loc[recent_mask & panel["timestamp"].lt(pd.Timestamp("2026-01-01")), "split"] = "test_2025H2"
    panel.loc[recent_mask & panel["timestamp"].ge(pd.Timestamp("2026-01-01")), "split"] = "recent_oos_2026JanApr"
    symbols = sorted(panel["symbol"].dropna().astype(str).unique())
    if len(symbols) > PROBE_SYMBOL_LIMIT:
        # Deterministic broad universe slice for bounded numeric probe. This is
        # not full proof; full replay remains gated by later contracts.
        idx = np.linspace(0, len(symbols) - 1, PROBE_SYMBOL_LIMIT).round().astype(int)
        keep = {symbols[i] for i in idx}
        panel = panel[panel["symbol"].astype(str).isin(keep)].reset_index(drop=True)
    return panel


def add_labels(panel: pd.DataFrame, horizons: set[int]) -> None:
    grouped_close = panel.groupby("symbol", sort=False)["trade_close"]
    vol = pd.to_numeric(panel["realized_vol_168h"], errors="coerce").abs().replace(0.0, np.nan).clip(lower=1e-8)
    for horizon in sorted(horizons):
        raw = grouped_close.shift(-int(horizon)) / panel["trade_close"] - 1.0
        panel[f"L0_h{horizon}"] = raw
        panel[f"L1_h{horizon}"] = raw - panel.groupby("timestamp", sort=False)[f"L0_h{horizon}"].transform("mean")
        panel[f"L3_h{horizon}"] = raw - panel.groupby(["timestamp", "liquidity_tier_static"], sort=False)[f"L0_h{horizon}"].transform("mean")
        panel[f"L5_h{horizon}"] = raw / vol


def label_col(label: str, horizon: int) -> str:
    return f"{LABEL_PREFIX[label]}_h{int(horizon)}"


def sample_by_split(panel: pd.DataFrame) -> np.ndarray:
    selected = np.zeros(len(panel), dtype=bool)
    for split in [TRAIN_SPLIT] + PREMAY_EVAL:
        timestamps = np.array(sorted(panel.loc[panel["split"].eq(split), "timestamp"].dropna().unique()))
        if len(timestamps) > MAX_TIMESTAMPS_PER_SPLIT:
            idx = np.linspace(0, len(timestamps) - 1, MAX_TIMESTAMPS_PER_SPLIT).round().astype(int)
            timestamps = timestamps[idx]
        selected |= panel["timestamp"].isin(timestamps).to_numpy() & panel["split"].eq(split).to_numpy()
    return selected


def spread_metric(x: np.ndarray, y: np.ndarray) -> tuple[float, float, int]:
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < 100:
        return math.nan, math.nan, n
    xs = x[mask].astype(float)
    ys = y[mask].astype(float)
    x_std = xs.std()
    y_std = ys.std()
    corr = math.nan if x_std <= 1e-12 or y_std <= 1e-12 else float(np.corrcoef(xs, ys)[0, 1])
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
        "sign_flip_diagnostic": -sampled,
    }


def choose_probe_packet(packet: pd.DataFrame) -> pd.DataFrame:
    quotas = {
        "S0_positioning_price_basis": 160,
        "S1_liquidity_basis_positioning": 160,
        "S2_taker_flow_liquidity_oi": 80,
        "S3_cross_family_bridge": 80,
    }
    parts = []
    for lane, quota in quotas.items():
        lane_rows = packet[packet["seed_lane"].eq(lane)].copy()
        # Favor longer horizons first while preserving label diversity.
        lane_rows["label_order"] = lane_rows["label_family"].map(
            {
                "L0_raw_forward_return": 0,
                "L1_cross_sectional_relative_return": 1,
                "L3_liquidity_tier_relative_return": 2,
                "L5_vol_adjusted_return": 3,
            }
        )
        lane_rows = lane_rows.sort_values(["label_horizon_h", "label_order", "blueprint_id"], ascending=[False, True, True])
        parts.append(lane_rows.head(quota))
    return pd.concat(parts, ignore_index=True).drop_duplicates("blueprint_id")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core26 = read_json(CORE26)
    if core26.get("decision") != "PASS_A7FFCORE26_TARGETED_NUMERIC_PROBE_CONTRACT_READY_FOR_CORE26E":
        raise SystemExit(f"CORE26 is not ready: {core26.get('decision')}")
    packet = choose_probe_packet(pd.read_csv(PACKET))
    required_fields = set(packet["left_field"].astype(str)) | set(packet["right_field"].astype(str))
    panel = load_panel(required_fields)
    horizons = set(pd.to_numeric(packet["label_horizon_h"], errors="coerce").dropna().astype(int))
    add_labels(panel, horizons)
    sample_mask = sample_by_split(panel)
    sample_idx = np.flatnonzero(sample_mask)
    sample = panel.iloc[sample_idx].copy()
    evaluator = CachedCryptoFeatureAlgebra(panel, allowed_fields=required_fields | {"trade_close", "realized_vol_168h", "liquidity_tier_static", "split"})

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for cand in packet.to_dict("records"):
        cid = str(cand["blueprint_id"])
        label = str(cand["label_family"])
        horizon = int(cand["label_horizon_h"])
        col = label_col(label, horizon)
        try:
            signal = evaluator.evaluate(str(cand["expression"])).values
            one_bar_signal = signal.groupby(panel["symbol"], sort=False).shift(1)
            x_same = signal.to_numpy()[sample_idx]
            x_one = one_bar_signal.to_numpy()[sample_idx]
            control_values = controls(one_bar_signal, sample_idx, panel, cid)
        except Exception as exc:
            errors.append({"candidate_id": cid, "error": str(exc)})
            continue
        y_all = sample[col].to_numpy(dtype=float)
        split_all = sample["split"].astype(str).to_numpy()
        train_mask = split_all == TRAIN_SPLIT
        _, train_spread, train_n = spread_metric(x_one[train_mask], y_all[train_mask])
        orientation = 1.0 if not np.isfinite(train_spread) or train_spread >= 0 else -1.0
        for split in [TRAIN_SPLIT] + PREMAY_EVAL:
            smask = split_all == split
            corr_one, spread_one, n_one = spread_metric(x_one[smask], y_all[smask])
            _, spread_same, _ = spread_metric(x_same[smask], y_all[smask])
            oriented_one = spread_one * orientation if np.isfinite(spread_one) else math.nan
            oriented_same = spread_same * orientation if np.isfinite(spread_same) else math.nan
            control_scores = []
            for cname, cx in control_values.items():
                _, cspread, _ = spread_metric(cx[smask], y_all[smask])
                if cname != "sign_flip_diagnostic":
                    control_scores.append(abs(cspread) if np.isfinite(cspread) else 0.0)
            max_control = max(control_scores) if control_scores else 0.0
            control_ratio = max_control / max(abs(oriented_one) if np.isfinite(oriented_one) else 0.0, 1e-12)
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
                        "sample_rows": n_one,
                        "corr_one_bar": corr_one,
                        "one_bar_spread": oriented_one,
                        "same_bar_spread": oriented_same,
                        "one_bar_costed_spread": oriented_one - (2.0 * cost / 10000.0) if np.isfinite(oriented_one) else math.nan,
                        "same_bar_costed_spread": oriented_same - (2.0 * cost / 10000.0) if np.isfinite(oriented_same) else math.nan,
                        "max_control_spread": max_control,
                        "control_ratio": control_ratio,
                    }
                )
    result = pd.DataFrame(rows)
    errors_df = pd.DataFrame(errors)
    clean_rows = result[result["split"].isin(PREMAY_EVAL) & result["cost_bps"].eq(2)].copy()
    ok = clean_rows[clean_rows["one_bar_costed_spread"].gt(0) & clean_rows["control_ratio"].lt(1.0)]
    split_counts = ok.groupby("candidate_id")["split"].nunique()
    clean_ids = set(split_counts[split_counts >= len(PREMAY_EVAL)].index.astype(str))
    clean_candidates = result[result["candidate_id"].astype(str).isin(clean_ids)].drop_duplicates("candidate_id").copy()
    candidate_summary = (
        result.groupby(["candidate_id", "seed_lane", "label_family", "label_horizon_h"], dropna=False)
        .agg(
            min_one_bar_costed_spread=("one_bar_costed_spread", "min"),
            mean_one_bar_costed_spread=("one_bar_costed_spread", "mean"),
            max_control_ratio=("control_ratio", "max"),
            min_sample_rows=("sample_rows", "min"),
        )
        .reset_index()
    )
    candidate_summary["one_bar_executable_clean_2bps"] = candidate_summary["candidate_id"].astype(str).isin(clean_ids)
    lane_summary = (
        clean_candidates.groupby("seed_lane", dropna=False)
        .agg(clean_candidate_count=("candidate_id", "nunique"), label_family_count=("label_family", "nunique"))
        .reset_index()
        if not clean_candidates.empty
        else pd.DataFrame(columns=["seed_lane", "clean_candidate_count", "label_family_count"])
    )
    label_summary = (
        clean_candidates.groupby("label_family", dropna=False)
        .agg(clean_candidate_count=("candidate_id", "nunique"), lane_count=("seed_lane", "nunique"))
        .reset_index()
        if not clean_candidates.empty
        else pd.DataFrame(columns=["label_family", "clean_candidate_count", "lane_count"])
    )
    result.to_csv(RUNTIME / "a7ffcore26e_numeric_rows.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore26e_candidate_summary.csv", index=False)
    clean_candidates.to_csv(RUNTIME / "a7ffcore26e_executable_clean_candidates.csv", index=False)
    lane_summary.to_csv(RUNTIME / "a7ffcore26e_lane_summary.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ffcore26e_label_summary.csv", index=False)
    errors_df.to_csv(RUNTIME / "a7ffcore26e_eval_errors.csv", index=False)
    packet.to_csv(RUNTIME / "a7ffcore26e_probe_packet.csv", index=False)

    clean_count = int(clean_candidates["candidate_id"].nunique()) if not clean_candidates.empty else 0
    clean_lane_count = int(clean_candidates["seed_lane"].nunique()) if not clean_candidates.empty else 0
    non_l5_count = int(clean_candidates["label_family"].astype(str).ne("L5_vol_adjusted_return").sum()) if not clean_candidates.empty else 0
    blockers: list[str] = []
    if len(errors) > 0:
        blockers.append("eval_errors_present")
    if clean_count < 6:
        blockers.append("one_bar_executable_clean_count_lt_6")
    if clean_lane_count < 3:
        blockers.append("one_bar_executable_lane_count_lt_3")
    if non_l5_count < 3:
        blockers.append("non_l5_clean_count_lt_3")
    decision = "PASS_A7FFCORE26E_TARGETED_NUMERIC_PROBE_READY_FOR_CORE27" if not blockers else "HOLD_A7FFCORE26E_TARGETED_NUMERIC_PROBE_INSUFFICIENT"
    manifest = {
        "stage": "A7FF-CORE26E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE26",
        "source_decision": core26.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "probe_candidate_count": int(packet["blueprint_id"].nunique()),
        "probe_symbol_limit": PROBE_SYMBOL_LIMIT,
        "probe_symbol_count": int(panel["symbol"].nunique()),
        "numeric_rows": int(result.shape[0]),
        "eval_error_count": int(len(errors)),
        "one_bar_executable_clean_candidate_count": clean_count,
        "one_bar_executable_clean_lane_count": clean_lane_count,
        "non_l5_clean_count": non_l5_count,
        "authorizes_core27_contract": decision.startswith("PASS_"),
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE27 targeted bounded replay contract" if decision.startswith("PASS_") else "A7FF-CORE26R targeted numeric probe forensic",
    }
    write_json(RUNTIME / "a7ffcore26e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE26E TARGETED NUMERIC PROBE EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE26E executes a bounded numeric probe over the CORE25E targeted packet. It does not authorize search, large search, alpha proof, shadow, paper, or live.",
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
        "## Label Summary",
        "",
        md_table(label_summary),
        "",
        "## Clean Candidates",
        "",
        md_table(clean_candidates[["candidate_id", "seed_lane", "label_family", "label_horizon_h", "left_field", "left_transform", "operator", "right_field", "right_transform"]].head(40) if not clean_candidates.empty else clean_candidates),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
