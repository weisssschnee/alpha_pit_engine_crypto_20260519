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


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore7e_numeric_response"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE7E_NUMERIC_RESPONSE_EXECUTION_20260601.md"
A7FFCORE7 = REPO / "runtime" / "a7ffcore7_numeric_response_contract" / "a7ffcore7_manifest.json"
QUEUE = REPO / "runtime" / "a7ffcore5_gate_native_generation_dryrun" / "a7ffcore5_gate_native_candidate_queue.csv"
SHARD_PLAN = REPO / "runtime" / "a7ffcore7_numeric_response_contract" / "a7ffcore7_shard_plan.csv"
MAT = REPO / "runtime" / "a7ffcore6e_materialization_preflight" / "a7ffcore6e_materialization_summary_rows.csv"
BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet")


HORIZONS = [1, 4, 8, 24]
LABELS = ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return", "L7_ranked_future_return"]
PRIMARY_LABELS = {"L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"}
MAX_SAMPLE_TIMESTAMPS = 512


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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def stable_seed(text: str) -> int:
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16)


def split_fields(series: pd.Series) -> set[str]:
    fields: set[str] = set()
    for value in series.fillna("").astype(str):
        fields.update(part for part in value.split(";") if part)
    return fields


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


def add_labels(panel: pd.DataFrame) -> list[str]:
    label_cols: list[str] = []
    grouped_close = panel.groupby("symbol", sort=False)["trade_close"]
    for horizon in HORIZONS:
        raw_col = f"L0_h{horizon}"
        future_close = grouped_close.shift(-horizon)
        panel[raw_col] = future_close / panel["trade_close"] - 1.0
        label_cols.append(raw_col)

        rel_col = f"L1_h{horizon}"
        panel[rel_col] = panel[raw_col] - panel.groupby("timestamp", sort=False)[raw_col].transform("mean")
        label_cols.append(rel_col)

        liq_col = f"L3_h{horizon}"
        panel[liq_col] = panel[raw_col] - panel.groupby(["timestamp", "liquidity_tier_static"], sort=False)[raw_col].transform("mean")
        label_cols.append(liq_col)

        vol_col = f"L5_h{horizon}"
        vol = pd.to_numeric(panel["realized_vol_168h"], errors="coerce").abs().replace(0.0, np.nan)
        panel[vol_col] = panel[raw_col] / vol.clip(lower=1e-8)
        label_cols.append(vol_col)

        rank_col = f"L7_h{horizon}"
        panel[rank_col] = panel.groupby("timestamp", sort=False)[raw_col].rank(pct=True, method="average") - 0.5
        label_cols.append(rank_col)
    return label_cols


def label_col(label_id: str, horizon: int) -> str:
    prefix = {
        "L0_raw_forward_return": "L0",
        "L1_cross_sectional_relative_return": "L1",
        "L3_liquidity_tier_relative_return": "L3",
        "L5_vol_adjusted_return": "L5",
        "L7_ranked_future_return": "L7",
    }[label_id]
    return f"{prefix}_h{horizon}"


def sample_mask(panel: pd.DataFrame) -> np.ndarray:
    timestamps = np.array(sorted(panel["timestamp"].dropna().unique()))
    if len(timestamps) <= MAX_SAMPLE_TIMESTAMPS:
        chosen = set(timestamps)
    else:
        idx = np.linspace(0, len(timestamps) - 1, MAX_SAMPLE_TIMESTAMPS, dtype=int)
        chosen = set(timestamps[idx])
    return panel["timestamp"].isin(chosen).to_numpy()


def metric_pair(x: np.ndarray, y: np.ndarray) -> tuple[float, float, int]:
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
    low = ys[xs <= q10]
    high = ys[xs >= q90]
    spread = math.nan if len(low) == 0 or len(high) == 0 else float(np.nanmean(high) - np.nanmean(low))
    return corr, spread, n


def control_variants(
    signal: pd.Series,
    sampled_index: np.ndarray,
    candidate_id: str,
    panel: pd.DataFrame,
) -> dict[str, np.ndarray]:
    full = signal.astype(float)
    symbol_groups = panel["symbol"]
    variants: dict[str, pd.Series] = {
        "wrong_lag_future": full.groupby(symbol_groups, sort=False).shift(-1),
        "wrong_lag_stale": full.groupby(symbol_groups, sort=False).shift(24),
        "sign_flip": -full,
    }
    sampled = full.to_numpy()[sampled_index]
    rng = np.random.default_rng(stable_seed(candidate_id))
    perm = rng.permutation(len(sampled))
    variants_np = {
        "time_shuffle": np.roll(sampled, 97),
        "symbol_shuffle": sampled[perm],
        "same_family_placebo": rng.normal(0.0, np.nanstd(sampled) if np.isfinite(np.nanstd(sampled)) else 1.0, len(sampled)),
    }
    for name, series in variants.items():
        variants_np[name] = series.to_numpy()[sampled_index]
    return variants_np


def evaluate_candidate(
    row: dict[str, Any],
    signal: pd.Series,
    panel: pd.DataFrame,
    panel_sample: pd.DataFrame,
    sample_idx: np.ndarray,
    y_by_col: dict[str, np.ndarray],
) -> list[dict[str, Any]]:
    x = signal.to_numpy()[sample_idx]
    controls = control_variants(signal, sample_idx, str(row["candidate_id"]), panel)
    out: list[dict[str, Any]] = []
    for label in LABELS:
        for horizon in HORIZONS:
            col = label_col(label, horizon)
            y = y_by_col[col]
            corr, spread, n = metric_pair(x, y)
            original_score = max(abs(corr) if np.isfinite(corr) else 0.0, abs(spread) if np.isfinite(spread) else 0.0)
            control_scores = []
            control_corrs: dict[str, float] = {}
            control_spreads: dict[str, float] = {}
            for cname, cx in controls.items():
                ccorr, cspread, _ = metric_pair(cx, y)
                control_corrs[cname] = ccorr
                control_spreads[cname] = cspread
                control_scores.append(max(abs(ccorr) if np.isfinite(ccorr) else 0.0, abs(cspread) if np.isfinite(cspread) else 0.0))
            max_control = max(control_scores) if control_scores else 0.0
            control_ratio = max_control / max(original_score, 1e-12)
            clue = bool(label in PRIMARY_LABELS and np.isfinite(corr) and abs(corr) >= 0.001 and control_ratio < 0.8)
            out.append(
                {
                    "candidate_id": row["candidate_id"],
                    "root_subgraph_id": row["root_subgraph_id"],
                    "semantic_bucket": row["semantic_bucket"],
                    "motif_bucket": row["motif_bucket"],
                    "label_id": label,
                    "horizon": horizon,
                    "sample_rows": n,
                    "corr": corr,
                    "spread": spread,
                    "original_score": original_score,
                    "max_control_score": max_control,
                    "control_ratio": control_ratio,
                    "primary_non_l7": label in PRIMARY_LABELS,
                    "numeric_clue": clue,
                    **{f"{k}_corr": v for k, v in control_corrs.items()},
                    **{f"{k}_spread": v for k, v in control_spreads.items()},
                }
            )
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core7 = read_json(A7FFCORE7)
    if core7.get("decision") != "PASS_A7FFCORE7_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE7E":
        raise SystemExit(f"A7FF-CORE7 is not ready: {core7.get('decision')}")
    queue = pd.read_csv(QUEUE)
    mat = pd.read_csv(MAT)
    ok_ids = set(mat.loc[mat["status"].eq("ok"), "candidate_id"].astype(str))
    queue = queue[queue["candidate_id"].astype(str).isin(ok_ids)].reset_index(drop=True)
    required_fields = set()
    for value in queue["raw_inputs"].fillna("").astype(str):
        required_fields.update(part for part in value.split(";") if part)
    panel = load_panel(required_fields)
    add_labels(panel)
    mask = sample_mask(panel)
    sample_positions = np.flatnonzero(mask)
    panel_sample = panel.iloc[sample_positions].copy()
    y_by_col = {label_col(label, horizon): panel_sample[label_col(label, horizon)].to_numpy(dtype=float) for label in LABELS for horizon in HORIZONS}

    shard_plan = pd.read_csv(REPO / "runtime" / "a7ffcore7_numeric_response_contract" / "a7ffcore7_shard_plan.csv")
    shard_manifests: list[dict[str, Any]] = []
    all_rows: list[pd.DataFrame] = []
    for shard in shard_plan.to_dict("records"):
        shard_id = str(shard["shard_id"])
        out_path = RUNTIME / f"a7ffcore7e_{shard_id}_response.csv"
        manifest_path = RUNTIME / f"a7ffcore7e_{shard_id}_manifest.json"
        if out_path.exists() and manifest_path.exists():
            shard_df = pd.read_csv(out_path)
            all_rows.append(shard_df)
            shard_manifests.append(read_json(manifest_path))
            continue
        start = int(shard["start_index"])
        end = int(shard["end_index_exclusive"])
        shard_queue = queue.iloc[start:end].copy()
        evaluator = CachedCryptoFeatureAlgebra(panel, allowed_fields=set(required_fields) | {"trade_close", "realized_vol_168h", "liquidity_tier_static"})
        rows: list[dict[str, Any]] = []
        eval_errors = 0
        for cand in shard_queue.to_dict("records"):
            try:
                signal = evaluator.evaluate(str(cand["expression"])).values
                rows.extend(evaluate_candidate(cand, signal, panel, panel_sample, sample_positions, y_by_col))
            except Exception as exc:
                eval_errors += 1
                rows.append(
                    {
                        "candidate_id": cand["candidate_id"],
                        "root_subgraph_id": cand["root_subgraph_id"],
                        "semantic_bucket": cand["semantic_bucket"],
                        "motif_bucket": cand["motif_bucket"],
                        "label_id": "EVAL_ERROR",
                        "horizon": 0,
                        "sample_rows": 0,
                        "corr": math.nan,
                        "spread": math.nan,
                        "original_score": 0.0,
                        "max_control_score": 0.0,
                        "control_ratio": math.inf,
                        "primary_non_l7": False,
                        "numeric_clue": False,
                        "error": str(exc),
                    }
                )
        shard_df = pd.DataFrame(rows)
        shard_df.to_csv(out_path, index=False)
        manifest = {
            "shard_id": shard_id,
            "candidate_count": int(len(shard_queue)),
            "response_rows": int(len(shard_df)),
            "eval_errors": eval_errors,
            "numeric_clues": int(shard_df.get("numeric_clue", pd.Series(dtype=bool)).sum()),
            "primary_non_l7_clues": int(shard_df[(shard_df.get("primary_non_l7", False) == True) & (shard_df.get("numeric_clue", False) == True)].shape[0]) if not shard_df.empty else 0,
            "output": str(out_path.relative_to(REPO)),
        }
        write_json(manifest_path, manifest)
        shard_manifests.append(manifest)
        all_rows.append(shard_df)

    combined = pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()
    combined.to_csv(RUNTIME / "a7ffcore7e_response_rows.csv", index=False)
    shard_summary = pd.DataFrame(shard_manifests)
    shard_summary.to_csv(RUNTIME / "a7ffcore7e_shard_summary.csv", index=False)
    label_summary = (
        combined.groupby(["label_id", "horizon"], dropna=False)
        .agg(
            rows=("candidate_id", "count"),
            numeric_clues=("numeric_clue", "sum"),
            median_abs_corr=("corr", lambda s: float(np.nanmedian(np.abs(s)))),
            median_control_ratio=("control_ratio", "median"),
        )
        .reset_index()
        .sort_values(["numeric_clues", "median_abs_corr"], ascending=False)
    )
    label_summary.to_csv(RUNTIME / "a7ffcore7e_label_summary.csv", index=False)
    clue_rows = combined[combined["numeric_clue"].astype(bool)].copy()
    clue_rows.to_csv(RUNTIME / "a7ffcore7e_numeric_clues.csv", index=False)
    family_summary = (
        combined.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            rows=("candidate_id", "count"),
            candidate_count=("candidate_id", "nunique"),
            numeric_clues=("numeric_clue", "sum"),
            median_control_ratio=("control_ratio", "median"),
        )
        .reset_index()
        .sort_values("numeric_clues", ascending=False)
    )
    family_summary.to_csv(RUNTIME / "a7ffcore7e_family_summary.csv", index=False)

    primary_non_l7_clues = int(clue_rows[clue_rows["primary_non_l7"].astype(bool)].shape[0]) if not clue_rows.empty else 0
    wrong_lag_dominated = int((combined["control_ratio"] >= 1.0).sum()) if not combined.empty else 0
    blockers: list[str] = []
    if primary_non_l7_clues < 1:
        blockers.append("no_primary_non_l7_numeric_clues")
    if int(shard_summary["eval_errors"].sum()) > 0:
        blockers.append("eval_errors_present")
    decision = "PASS_A7FFCORE7E_NUMERIC_RESPONSE_READY_FOR_CORE8" if not blockers else "HOLD_A7FFCORE7E_NUMERIC_RESPONSE_WEAK"
    manifest = {
        "stage": "A7FF-CORE7E",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE7",
        "source_decision": core7.get("decision"),
        "panel_rows": int(len(panel)),
        "sample_timestamp_count": int(panel_sample["timestamp"].nunique()),
        "sample_rows": int(len(panel_sample)),
        "candidate_count": int(queue["candidate_id"].nunique()),
        "response_rows": int(len(combined)),
        "numeric_clue_rows": int(len(clue_rows)),
        "primary_non_l7_clue_rows": primary_non_l7_clues,
        "wrong_lag_or_control_dominated_rows": wrong_lag_dominated,
        "shard_count": int(len(shard_summary)),
        "eval_error_count": int(shard_summary["eval_errors"].sum()) if not shard_summary.empty else 0,
        "executes_numeric": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core8": not bool(blockers),
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE8 numeric clue consolidation / replay-preflight contract" if not blockers else "A7FF-CORE7R response repair or label/control forensic",
    }
    write_json(RUNTIME / "a7ffcore7e_manifest.json", manifest)
    report = f"""# CRYPTO A7FF-CORE7E NUMERIC RESPONSE EXECUTION

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE7E computes bounded label/control numeric response for the CORE6E materialized gate-native queue. It does not run portfolio replay, search, promotion, alpha proof, shadow, paper, or live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Label Summary

{md_table(label_summary, 80)}

## Family Summary

{md_table(family_summary, 80)}

## Shard Summary

{md_table(shard_summary, 40)}

## Top Numeric Clues

{md_table(clue_rows.sort_values(["primary_non_l7", "original_score"], ascending=False).head(80), 80)}

## Boundary

```text
numeric response executed: true
portfolio replay: false
search: false
promotion: false
May used for orientation/scoring: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
