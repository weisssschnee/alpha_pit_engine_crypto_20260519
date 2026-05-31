from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.dataset as ds


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore9e_bounded_replay"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE9E_BOUNDED_REPLAY_EXECUTION_20260601.md"
A7FFCORE9 = REPO / "runtime" / "a7ffcore9_bounded_replay_contract" / "a7ffcore9_manifest.json"
PACKET = REPO / "runtime" / "a7ffcore9_bounded_replay_contract" / "a7ffcore9_replay_contract_packet.csv"
CLUES = REPO / "runtime" / "a7ffcore7er_repaired_numeric_response" / "a7ffcore7er_numeric_clues.csv"
BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet")

HORIZONS = [1, 4, 8, 24]
LABELS = ["L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"]
COST_BPS = [0, 2, 5, 10]
MAX_TIMESTAMPS_PER_SPLIT = 384
SPLIT_MAP = {
    "train_2024": "train",
    "validation_2025H1": "validation",
    "recent_2025H2_2026Apr": "recent",
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


def split_fields(series: pd.Series) -> set[str]:
    out: set[str] = set()
    for value in series.fillna("").astype(str):
        out.update(part for part in value.split(";") if part)
    return out


def load_panel(required_fields: set[str]) -> pd.DataFrame:
    base_needed = set(required_fields) | {"trade_close"}
    latent_needed = set(required_fields) | {"split", "liquidity_tier_static", "realized_vol_168h"}
    base_schema = set(ds.dataset(str(BASE_PANEL), format="parquet").schema.names)
    latent_schema = set(ds.dataset(str(LATENT_PANEL), format="parquet").schema.names)
    key_cols = ["symbol", "timestamp"]
    base_cols = key_cols + sorted((base_needed & base_schema) - set(key_cols))
    latent_cols = key_cols + sorted((latent_needed & latent_schema) - set(key_cols) - set(base_cols))
    base = ds.dataset(str(BASE_PANEL), format="parquet").to_table(columns=base_cols).to_pandas()
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True).dt.tz_localize(None)
    latent = pd.read_parquet(LATENT_PANEL, columns=latent_cols)
    latent["timestamp"] = pd.to_datetime(latent["timestamp"], utc=True).dt.tz_localize(None)
    panel = base.merge(latent, on=key_cols, how="left", validate="one_to_one")
    return panel.sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def label_col(label: str, horizon: int) -> str:
    if label.startswith("L1_"):
        return f"L1_h{horizon}"
    if label.startswith("L3_"):
        return f"L3_h{horizon}"
    if label.startswith("L5_"):
        return f"L5_h{horizon}"
    raise ValueError(label)


def add_labels(panel: pd.DataFrame) -> None:
    grouped_close = panel.groupby("symbol", sort=False)["trade_close"]
    vol = pd.to_numeric(panel["realized_vol_168h"], errors="coerce").abs().replace(0.0, np.nan).clip(lower=1e-8)
    for horizon in HORIZONS:
        raw = grouped_close.shift(-horizon) / panel["trade_close"] - 1.0
        panel[f"_raw_h{horizon}"] = raw
        panel[f"L1_h{horizon}"] = panel[f"_raw_h{horizon}"] - panel.groupby("timestamp", sort=False)[f"_raw_h{horizon}"].transform("mean")
        panel[f"L3_h{horizon}"] = panel[f"_raw_h{horizon}"] - panel.groupby(["timestamp", "liquidity_tier_static"], sort=False)[f"_raw_h{horizon}"].transform("mean")
        panel[f"L5_h{horizon}"] = panel[f"_raw_h{horizon}"] / vol


def sample_mask(panel: pd.DataFrame) -> np.ndarray:
    mask = np.zeros(len(panel), dtype=bool)
    split_group = panel["split"].map(SPLIT_MAP).fillna(panel["split"])
    for split_name in ["train", "validation", "recent"]:
        split_ts = np.array(sorted(panel.loc[split_group.eq(split_name), "timestamp"].dropna().unique()))
        if len(split_ts) == 0:
            continue
        if len(split_ts) > MAX_TIMESTAMPS_PER_SPLIT:
            idx = np.linspace(0, len(split_ts) - 1, MAX_TIMESTAMPS_PER_SPLIT).round().astype(int)
            split_ts = split_ts[idx]
        mask |= panel["timestamp"].isin(split_ts).to_numpy()
    return mask


def choose_best_clue(clues: pd.DataFrame) -> pd.DataFrame:
    clues = clues[clues["label_id"].isin(LABELS)].copy()
    clues["abs_corr"] = pd.to_numeric(clues["corr"], errors="coerce").abs()
    return (
        clues.sort_values(["candidate_id", "control_ratio", "abs_corr"], ascending=[True, True, False])
        .groupby("candidate_id", as_index=False)
        .head(1)[["candidate_id", "label_id", "horizon", "corr", "control_ratio"]]
        .rename(columns={"corr": "orientation_corr", "control_ratio": "numeric_control_ratio"})
    )


def replay_stats(frame: pd.DataFrame, signal_col: str, label_col_name: str) -> dict[str, float]:
    rows = []
    for _, g in frame[["timestamp", signal_col, label_col_name]].dropna().groupby("timestamp", sort=False):
        n = len(g)
        if n < 20:
            continue
        ranks = g[signal_col].rank(pct=True, method="average")
        long = g.loc[ranks >= 0.9, label_col_name]
        short = g.loc[ranks <= 0.1, label_col_name]
        if len(long) == 0 or len(short) == 0:
            continue
        rows.append(float(long.mean() - short.mean()))
    if not rows:
        return {"spread": math.nan, "tstat": math.nan, "hours": 0.0}
    arr = np.asarray(rows, dtype=float)
    std = float(np.nanstd(arr, ddof=1)) if len(arr) > 1 else math.nan
    tstat = math.nan if not np.isfinite(std) or std <= 1e-12 else float(np.nanmean(arr) / std * math.sqrt(len(arr)))
    return {"spread": float(np.nanmean(arr)), "tstat": tstat, "hours": float(len(arr))}


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core9 = read_json(A7FFCORE9)
    if core9.get("decision") != "PASS_A7FFCORE9_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE9E":
        raise SystemExit(f"A7FF-CORE9 is not ready: {core9.get('decision')}")

    packet = pd.read_csv(PACKET)
    clues = pd.read_csv(CLUES)
    best = choose_best_clue(clues)
    packet = packet.merge(best, on="candidate_id", how="inner", validate="one_to_one")
    required_fields = split_fields(packet["raw_inputs"])
    panel = load_panel(required_fields)
    add_labels(panel)
    panel["split_group"] = panel["split"].map(SPLIT_MAP).fillna(panel["split"])
    mask = sample_mask(panel)
    sampled = panel.loc[mask, ["symbol", "timestamp", "split", "split_group"] + [label_col(label, h) for label in LABELS for h in HORIZONS]].copy()
    sample_positions = np.flatnonzero(mask)
    evaluator = CachedCryptoFeatureAlgebra(panel, allowed_fields=required_fields | {"trade_close", "realized_vol_168h", "liquidity_tier_static"})
    rows = []
    eval_errors = 0
    for cand in packet.to_dict("records"):
        try:
            signal = evaluator.evaluate(str(cand["expression"])).values.to_numpy(dtype=float)
        except Exception as exc:
            eval_errors += 1
            rows.append({"candidate_id": cand["candidate_id"], "status": "eval_error", "error": str(exc)})
            continue
        orient = 1.0 if float(cand["orientation_corr"]) >= 0 else -1.0
        x = signal[sample_positions] * orient
        replay_frame = sampled.copy()
        replay_frame["signal"] = x
        ycol = label_col(str(cand["label_id"]), int(cand["horizon"]))
        control_full = pd.Series(signal).groupby(panel["symbol"], sort=False).shift(-1).to_numpy(dtype=float)
        replay_frame["wrong_lag_future"] = control_full[sample_positions] * orient
        for split_name in ["train", "validation", "recent"]:
            split_frame = replay_frame[replay_frame["split_group"].eq(split_name)]
            original = replay_stats(split_frame, "signal", ycol)
            wrong_lag = replay_stats(split_frame, "wrong_lag_future", ycol)
            max_control = abs(wrong_lag["spread"]) if np.isfinite(wrong_lag["spread"]) else 0.0
            orig_score = abs(original["spread"]) if np.isfinite(original["spread"]) else 0.0
            ratio = max_control / max(orig_score, 1e-12)
            for cost in COST_BPS:
                # Long + short rebalance proxy. This is a bounded pre-search replay, not execution-cost proof.
                cost_adjusted = original["spread"] - (2.0 * cost / 10000.0) if np.isfinite(original["spread"]) else math.nan
                rows.append(
                    {
                        "candidate_id": cand["candidate_id"],
                        "semantic_bucket": cand["semantic_bucket"],
                        "motif_bucket": cand["motif_bucket"],
                        "label_id": cand["label_id"],
                        "horizon": int(cand["horizon"]),
                        "split": split_name,
                        "cost_bps": cost,
                        "spread": original["spread"],
                        "cost_adjusted_spread": cost_adjusted,
                        "tstat": original["tstat"],
                        "hours": original["hours"],
                        "wrong_lag_future_spread": wrong_lag["spread"],
                        "wrong_lag_control_ratio": ratio,
                        "status": "ok",
                    }
                )
    result = pd.DataFrame(rows)
    ok = result[result["status"].eq("ok")].copy()
    pass_mask = (
        ok["split"].isin(["validation", "recent"])
        & ok["cost_bps"].eq(5)
        & pd.to_numeric(ok["cost_adjusted_spread"], errors="coerce").gt(0)
        & pd.to_numeric(ok["wrong_lag_control_ratio"], errors="coerce").lt(1.0)
    )
    clean_candidates = set(ok.loc[pass_mask, "candidate_id"].astype(str))
    candidate_summary = (
        ok.groupby(["candidate_id", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            replay_rows=("candidate_id", "size"),
            positive_validation_recent_cost5=("candidate_id", lambda s: int(s.astype(str).isin(clean_candidates).any())),
            median_spread=("spread", "median"),
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
            max_tstat=("tstat", "max"),
            min_control_ratio=("wrong_lag_control_ratio", "min"),
        )
        .reset_index()
        .sort_values(["positive_validation_recent_cost5", "max_tstat"], ascending=[False, False])
    )
    family_summary = (
        ok.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "nunique"),
            clean_candidate_count=("candidate_id", lambda s: int(len(set(s.astype(str)) & clean_candidates))),
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
            median_control_ratio=("wrong_lag_control_ratio", "median"),
        )
        .reset_index()
        .sort_values(["clean_candidate_count", "candidate_count"], ascending=[False, False])
    )
    result.to_csv(RUNTIME / "a7ffcore9e_replay_rows.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore9e_candidate_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore9e_family_summary.csv", index=False)
    pd.DataFrame([{"candidate_id": c} for c in sorted(clean_candidates)]).to_csv(RUNTIME / "a7ffcore9e_replay_clean_candidates.csv", index=False)

    clean_semantic = int(candidate_summary.loc[candidate_summary["candidate_id"].astype(str).isin(clean_candidates), "semantic_bucket"].nunique())
    clean_motif = int(candidate_summary.loc[candidate_summary["candidate_id"].astype(str).isin(clean_candidates), "motif_bucket"].nunique())
    decision = (
        "PASS_A7FFCORE9E_BOUNDED_REPLAY_CLEAN_CANDIDATES_READY_FOR_CORE10"
        if len(clean_candidates) >= 16 and clean_semantic >= 4 and clean_motif >= 4 and eval_errors == 0
        else "HOLD_A7FFCORE9E_BOUNDED_REPLAY_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE9E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE9",
        "source_decision": core9.get("decision"),
        "decision": decision,
        "candidate_count": int(packet.shape[0]),
        "eval_error_count": int(eval_errors),
        "sample_rows": int(sampled.shape[0]),
        "sample_timestamp_count": int(sampled["timestamp"].nunique()),
        "replay_rows": int(result.shape[0]),
        "replay_clean_candidate_count": int(len(clean_candidates)),
        "replay_clean_semantic_bucket_count": clean_semantic,
        "replay_clean_motif_bucket_count": clean_motif,
        "executes_replay": True,
        "executes_search": False,
        "authorizes_core10_contract": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE10 replay-clean consolidation / search-readiness contract" if decision.startswith("PASS_") else "A7FF-CORE9R replay failure forensic",
    }
    write_json(RUNTIME / "a7ffcore9e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE9E BOUNDED REPLAY EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE9E executes a bounded replay proxy for the CORE9 packet. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Candidate Summary",
        "",
        md_table(candidate_summary, max_rows=80),
        "",
        "## Boundary",
        "",
        "```text",
        "bounded replay proxy: true",
        "formula search / large search: false",
        "promotion: false",
        "alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
