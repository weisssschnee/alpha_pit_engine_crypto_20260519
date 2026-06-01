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


RUNTIME = REPO / "runtime" / "a7ffcore13e_numeric_response"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE13E_NUMERIC_RESPONSE_EXECUTION_20260601.md"
A7FFCORE13 = REPO / "runtime" / "a7ffcore13_numeric_response_contract" / "a7ffcore13_manifest.json"
QUEUE = REPO / "runtime" / "a7ffcore13_numeric_response_contract" / "a7ffcore13_numeric_response_queue.csv"
BASE_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_latent_state_features_v1_20260527.parquet")

HORIZONS = [1, 4, 8, 24]
LABELS = ["L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"]
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
    return view.to_markdown(index=False)


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
        panel[f"L1_h{horizon}"] = raw - panel.groupby("timestamp", sort=False)[f"_raw_h{horizon}"].transform("mean")
        panel[f"L3_h{horizon}"] = raw - panel.groupby(["timestamp", "liquidity_tier_static"], sort=False)[f"_raw_h{horizon}"].transform("mean")
        panel[f"L5_h{horizon}"] = raw / vol


def sample_mask(panel: pd.DataFrame) -> np.ndarray:
    timestamps = np.array(sorted(panel["timestamp"].dropna().unique()))
    if len(timestamps) > MAX_SAMPLE_TIMESTAMPS:
        idx = np.linspace(0, len(timestamps) - 1, MAX_SAMPLE_TIMESTAMPS).round().astype(int)
        timestamps = timestamps[idx]
    return panel["timestamp"].isin(timestamps).to_numpy()


def metric_pair(x: np.ndarray, y: np.ndarray) -> tuple[float, float, int]:
    mask = np.isfinite(x) & np.isfinite(y)
    if mask.sum() < 100:
        return math.nan, math.nan, int(mask.sum())
    xs = x[mask]
    ys = y[mask]
    corr = math.nan if xs.std() <= 1e-12 or ys.std() <= 1e-12 else float(np.corrcoef(xs, ys)[0, 1])
    q10, q90 = np.nanquantile(xs, [0.1, 0.9])
    spread = float(np.nanmean(ys[xs >= q90]) - np.nanmean(ys[xs <= q10]))
    return corr, spread, int(mask.sum())


def controls(signal: pd.Series, sample_idx: np.ndarray, panel: pd.DataFrame, cid: str) -> dict[str, np.ndarray]:
    full = signal.astype(float)
    sampled = full.to_numpy()[sample_idx]
    rng = np.random.default_rng(stable_seed(cid))
    out = {
        "wrong_lag_future": full.groupby(panel["symbol"], sort=False).shift(-1).to_numpy()[sample_idx],
        "wrong_lag_stale": full.groupby(panel["symbol"], sort=False).shift(24).to_numpy()[sample_idx],
        "time_shuffle": np.roll(sampled, 97),
        "symbol_shuffle": sampled[rng.permutation(len(sampled))],
        "same_family_placebo": rng.normal(0.0, np.nanstd(sampled) if np.isfinite(np.nanstd(sampled)) else 1.0, len(sampled)),
        "sign_flip_diagnostic": -sampled,
    }
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core13 = read_json(A7FFCORE13)
    if core13.get("decision") != "PASS_A7FFCORE13_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE13E":
        raise SystemExit(f"A7FF-CORE13 is not ready: {core13.get('decision')}")
    queue = pd.read_csv(QUEUE)
    required_fields = split_fields(queue["raw_inputs"])
    panel = load_panel(required_fields)
    add_labels(panel)
    mask = sample_mask(panel)
    sample_idx = np.flatnonzero(mask)
    sample = panel.iloc[sample_idx].copy()
    y_by_col = {label_col(label, horizon): sample[label_col(label, horizon)].to_numpy(dtype=float) for label in LABELS for horizon in HORIZONS}
    evaluator = CachedCryptoFeatureAlgebra(panel, allowed_fields=required_fields | {"trade_close", "realized_vol_168h", "liquidity_tier_static"})
    rows: list[dict[str, Any]] = []
    eval_errors = 0
    for cand in queue.to_dict("records"):
        try:
            signal = evaluator.evaluate(str(cand["expression"])).values
            x = signal.to_numpy()[sample_idx]
            control_values = controls(signal, sample_idx, panel, str(cand["candidate_id"]))
        except Exception as exc:
            eval_errors += 1
            rows.append({"candidate_id": cand["candidate_id"], "semantic_bucket": cand["semantic_bucket"], "motif_bucket": cand["motif_bucket"], "label_id": "EVAL_ERROR", "horizon": 0, "error": str(exc)})
            continue
        for label in LABELS:
            for horizon in HORIZONS:
                y = y_by_col[label_col(label, horizon)]
                corr, spread, n = metric_pair(x, y)
                original_score = max(abs(corr) if np.isfinite(corr) else 0.0, abs(spread) if np.isfinite(spread) else 0.0)
                c_scores = []
                c_payload: dict[str, float] = {}
                for cname, cx in control_values.items():
                    ccorr, cspread, _ = metric_pair(cx, y)
                    c_payload[f"{cname}_corr"] = ccorr
                    c_payload[f"{cname}_spread"] = cspread
                    if cname != "sign_flip_diagnostic":
                        c_scores.append(max(abs(ccorr) if np.isfinite(ccorr) else 0.0, abs(cspread) if np.isfinite(cspread) else 0.0))
                max_control = max(c_scores) if c_scores else 0.0
                ratio = max_control / max(original_score, 1e-12)
                rows.append(
                    {
                        "candidate_id": cand["candidate_id"],
                        "semantic_bucket": cand["semantic_bucket"],
                        "motif_bucket": cand["motif_bucket"],
                        "generation_mode": cand["generation_mode"],
                        "label_id": label,
                        "horizon": horizon,
                        "sample_rows": n,
                        "corr": corr,
                        "spread": spread,
                        "original_score": original_score,
                        "max_control_score": max_control,
                        "control_ratio": ratio,
                        "numeric_clue": bool(np.isfinite(corr) and abs(corr) >= 0.001 and ratio < 0.8),
                        **c_payload,
                    }
                )
    result = pd.DataFrame(rows)
    clues = result[result.get("numeric_clue", False).astype(bool)].copy() if "numeric_clue" in result else pd.DataFrame()
    label_summary = (
        result[result["label_id"].ne("EVAL_ERROR")]
        .groupby(["label_id", "horizon"], dropna=False)
        .agg(rows=("candidate_id", "size"), numeric_clues=("numeric_clue", "sum"), candidate_count=("candidate_id", "nunique"), median_control_ratio=("control_ratio", "median"))
        .reset_index()
        .sort_values(["numeric_clues", "candidate_count"], ascending=[False, False])
    )
    family_summary = (
        result[result["label_id"].ne("EVAL_ERROR")]
        .groupby(["semantic_bucket", "motif_bucket", "generation_mode"], dropna=False)
        .agg(rows=("candidate_id", "size"), numeric_clues=("numeric_clue", "sum"), candidate_count=("candidate_id", "nunique"), median_control_ratio=("control_ratio", "median"))
        .reset_index()
        .sort_values(["numeric_clues", "candidate_count"], ascending=[False, False])
    )
    result.to_csv(RUNTIME / "a7ffcore13e_response_rows.csv", index=False)
    clues.to_csv(RUNTIME / "a7ffcore13e_numeric_clues.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ffcore13e_label_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore13e_family_summary.csv", index=False)
    clue_candidates = int(clues["candidate_id"].nunique()) if not clues.empty else 0
    semantic_count = int(clues["semantic_bucket"].nunique()) if not clues.empty else 0
    motif_count = int(clues["motif_bucket"].nunique()) if not clues.empty else 0
    decision = (
        "PASS_A7FFCORE13E_NUMERIC_RESPONSE_READY_FOR_CORE14"
        if eval_errors == 0 and clue_candidates >= 64 and semantic_count >= 6 and motif_count >= 5
        else "HOLD_A7FFCORE13E_NUMERIC_RESPONSE_INSUFFICIENT"
    )
    blockers = []
    if eval_errors:
        blockers.append("eval_errors_present")
    if clue_candidates < 64:
        blockers.append("numeric_clue_candidates_below_64")
    if semantic_count < 6:
        blockers.append("semantic_breadth_low")
    if motif_count < 5:
        blockers.append("motif_breadth_low")
    manifest = {
        "stage": "A7FF-CORE13E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE13",
        "source_decision": core13.get("decision"),
        "decision": decision,
        "candidate_count": int(queue.shape[0]),
        "eval_error_count": int(eval_errors),
        "response_rows": int(result.shape[0]),
        "numeric_clue_rows": int(clues.shape[0]) if not clues.empty else 0,
        "numeric_clue_candidate_count": clue_candidates,
        "semantic_bucket_count_with_clues": semantic_count,
        "motif_bucket_count_with_clues": motif_count,
        "sample_rows": int(sample.shape[0]),
        "sample_timestamp_count": int(sample["timestamp"].nunique()),
        "blockers": blockers,
        "executes_numeric": True,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core14": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE14 replay-preflight contract" if decision.startswith("PASS_") else "A7FF-CORE13R numeric response repair",
    }
    write_json(RUNTIME / "a7ffcore13e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE13E NUMERIC RESPONSE EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE13E executes numeric response over CORE12E temp subgraphs. It does not run replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Summary",
        "",
        md_table(label_summary),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
