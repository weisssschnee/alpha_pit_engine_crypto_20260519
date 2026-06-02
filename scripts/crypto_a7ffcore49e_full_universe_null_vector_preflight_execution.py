from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra


RUNTIME = REPO / "runtime" / "a7ffcore49e_full_universe_null_vector_preflight_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE49E_FULL_UNIVERSE_NULL_VECTOR_PREFLIGHT_EXECUTION_20260602.md"
CORE49 = REPO / "runtime" / "a7ffcore49_full_universe_null_vector_preflight_contract" / "a7ffcore49_manifest.json"
QUEUE_PATH = REPO / "runtime" / "a7ffcore48se_repaired_null_first_dry_generation" / "a7ffcore48se_eligible_seed_queue.csv"
BASE_PANEL = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_latent_state_features_v1_20260527.parquet")
EXTERNAL = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore49e_full_universe_null_vector_preflight_20260602")

OPS = {
    "Mean",
    "Delta",
    "TSRank",
    "Decay",
    "Rank",
    "CSRank",
    "ZScore",
    "Mul",
    "Sub",
    "SafeDiv",
    "Add",
    "Neg",
    "Abs",
    "Sign",
    "Clip",
}


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


def extract_fields(expressions: pd.Series) -> list[str]:
    tokens: set[str] = set()
    for expression in expressions.astype(str):
        tokens.update(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", expression))
    return sorted(token for token in tokens if token not in OPS)


def normalize_timestamp(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values, utc=True, errors="coerce").dt.tz_convert(None)


def read_base_panel(required_fields: list[str]) -> pd.DataFrame:
    part_files = sorted(BASE_PANEL.glob("symbol=*/part.parquet"))
    if not part_files:
        raise FileNotFoundError(f"no panel partitions found: {BASE_PANEL}")
    sample_cols = set(pd.read_parquet(part_files[0]).columns)
    cols = ["symbol", "timestamp", *[field for field in required_fields if field in sample_cols and field not in {"symbol", "timestamp"}]]
    frames = []
    for path in part_files:
        frames.append(pd.read_parquet(path, columns=cols))
    frame = pd.concat(frames, ignore_index=True)
    frame["timestamp"] = normalize_timestamp(frame["timestamp"])
    return frame


def overlay_latent_fields(frame: pd.DataFrame, required_fields: list[str]) -> pd.DataFrame:
    if not LATENT_PANEL.exists():
        return frame
    latent_schema_cols = pq.ParquetFile(LATENT_PANEL).schema_arrow.names
    missing = [field for field in required_fields if field not in frame.columns and field in latent_schema_cols]
    if not missing:
        return frame
    latent = pd.read_parquet(LATENT_PANEL, columns=["symbol", "timestamp", *missing])
    latent["timestamp"] = normalize_timestamp(latent["timestamp"])
    return frame.merge(latent, on=["symbol", "timestamp"], how="left", sort=False)


def corr(a: pd.Series, b: pd.Series) -> float:
    valid = a.notna() & b.notna()
    if int(valid.sum()) < 100:
        return float("nan")
    value = a[valid].corr(b[valid])
    return float(value) if pd.notna(value) else float("nan")


def vector_controls(values: pd.Series, frame: pd.DataFrame) -> dict[str, pd.Series]:
    stale = values.groupby(frame["symbol"], sort=False).shift(1)
    time_shuffle = values.groupby(frame["symbol"], sort=False).shift(24)
    tmp = pd.DataFrame({"timestamp": frame["timestamp"], "symbol": frame["symbol"], "value": values})
    symbol_shuffle = tmp.sort_values(["timestamp", "symbol"]).groupby("timestamp", sort=False)["value"].shift(1).reindex(values.index)
    return {
        "stale_signal": stale,
        "sign_flip_signal": -values,
        "time_shuffle_signal": time_shuffle,
        "symbol_shuffle_signal": symbol_shuffle,
    }


def vector_stats(seed: pd.Series, values: pd.Series, frame: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame]:
    diagnostics = CryptoFeatureAlgebra(frame[["symbol", "timestamp"]].copy(), {"placeholder"}).diagnostics(values)
    controls = vector_controls(values, frame)
    control_finite = {name: int(series.notna().sum()) for name, series in controls.items()}
    control_corr = {f"{name}_corr": corr(values, series) for name, series in controls.items()}
    finite_mask = values.notna() & np.isfinite(values.to_numpy(dtype=float, na_value=np.nan))
    sample_idx = np.flatnonzero(finite_mask.to_numpy())[:80]
    sample = pd.DataFrame(
        {
            "seed_id": seed["seed_id"],
            "timestamp": frame.iloc[sample_idx]["timestamp"].to_numpy(),
            "symbol": frame.iloc[sample_idx]["symbol"].to_numpy(),
            "original_signal": values.iloc[sample_idx].to_numpy(),
            "stale_signal": controls["stale_signal"].iloc[sample_idx].to_numpy(),
            "sign_flip_signal": controls["sign_flip_signal"].iloc[sample_idx].to_numpy(),
            "time_shuffle_signal": controls["time_shuffle_signal"].iloc[sample_idx].to_numpy(),
            "symbol_shuffle_signal": controls["symbol_shuffle_signal"].iloc[sample_idx].to_numpy(),
        }
    )
    row = {
        "seed_id": seed["seed_id"],
        "semantic_pair": seed.get("semantic_pair", ""),
        "operator": seed.get("operator", ""),
        "operator_origin": seed.get("operator_origin", ""),
        "expression": seed.get("expression", ""),
        "materialization_status": "pass" if diagnostics["finite_rows"] > 0 and diagnostics["active_rows"] > 0 else "fail_inactive_or_empty",
        **diagnostics,
        **control_finite,
        **control_corr,
    }
    return row, sample


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE49)
    if source.get("decision") != "PASS_A7FFCORE49_FULL_UNIVERSE_NULL_VECTOR_PREFLIGHT_CONTRACT_READY_FOR_CORE49E":
        raise SystemExit(f"CORE49 not ready for CORE49E: {source.get('decision')}")

    queue = pd.read_csv(QUEUE_PATH)
    source_seed_count = int(len(queue))
    max_seeds = int(os.environ.get("A7FFCORE49E_MAX_SEEDS", str(source_seed_count)))
    queue = queue.head(max_seeds).copy()
    required_fields = extract_fields(queue["expression"])
    frame = read_base_panel(required_fields)
    frame = overlay_latent_fields(frame, required_fields)
    missing_fields = sorted(field for field in required_fields if field not in frame.columns)
    allowed_fields = set(frame.columns) - {"symbol", "timestamp"}
    evaluator = CryptoFeatureAlgebra(frame[["symbol", "timestamp", *sorted(allowed_fields)]].copy(), set(allowed_fields))

    rows: list[dict[str, Any]] = []
    samples: list[pd.DataFrame] = []
    failures: list[dict[str, Any]] = []
    for _, seed in queue.iterrows():
        expression = str(seed["expression"])
        try:
            result = evaluator.evaluate(expression)
            row, sample = vector_stats(seed, result.values, evaluator.frame)
            rows.append(row)
            if len(samples) < 200:
                samples.append(sample)
        except Exception as exc:
            failures.append(
                {
                    "seed_id": seed.get("seed_id", ""),
                    "semantic_pair": seed.get("semantic_pair", ""),
                    "operator": seed.get("operator", ""),
                    "expression": expression,
                    "error": str(exc),
                }
            )
            rows.append(
                {
                    "seed_id": seed.get("seed_id", ""),
                    "semantic_pair": seed.get("semantic_pair", ""),
                    "operator": seed.get("operator", ""),
                    "operator_origin": seed.get("operator_origin", ""),
                    "expression": expression,
                    "materialization_status": "fail_eval_error",
                    "rows": int(len(evaluator.frame)),
                    "non_null_rows": 0,
                    "finite_rows": 0,
                    "nan_rows": int(len(evaluator.frame)),
                    "inf_rows": 0,
                    "active_rows": 0,
                    "non_null_ratio": 0.0,
                    "active_ratio": 0.0,
                    "std": float("nan"),
                }
            )

    metrics = pd.DataFrame(rows)
    failures_df = pd.DataFrame(failures)
    sample_df = pd.concat(samples, ignore_index=True) if samples else pd.DataFrame()
    sample_path = EXTERNAL / "a7ffcore49e_vector_sample.parquet"
    if not sample_df.empty:
        sample_df.to_parquet(sample_path, index=False)

    metrics.to_csv(RUNTIME / "a7ffcore49e_seed_vector_metrics.csv", index=False)
    failures_df.to_csv(RUNTIME / "a7ffcore49e_eval_failures.csv", index=False)
    pd.DataFrame({"missing_field": missing_fields}).to_csv(RUNTIME / "a7ffcore49e_missing_fields.csv", index=False)
    family_summary = (
        metrics.groupby(["semantic_pair", "operator"], as_index=False)
        .agg(
            seed_count=("seed_id", "count"),
            pass_count=("materialization_status", lambda s: int((s == "pass").sum())),
            median_active_ratio=("active_ratio", "median"),
            median_stale_corr=("stale_signal_corr", "median"),
            median_time_shuffle_corr=("time_shuffle_signal_corr", "median"),
        )
        .sort_values(["pass_count", "seed_count"], ascending=False)
    )
    family_summary.to_csv(RUNTIME / "a7ffcore49e_family_operator_summary.csv", index=False)

    pass_count = int((metrics["materialization_status"] == "pass").sum())
    eval_failure_count = int(len(failures_df))
    missing_field_count = int(len(missing_fields))
    is_partial_smoke = int(len(queue)) < source_seed_count
    min_pass_required = int(0.6 * len(queue)) if is_partial_smoke else max(120, int(0.6 * len(queue)))
    gate_pass = pass_count >= min_pass_required and eval_failure_count == 0 and missing_field_count == 0
    if is_partial_smoke and gate_pass:
        decision = "PASS_A7FFCORE49E_PARTIAL_NULL_VECTOR_SMOKE_READY_FOR_FULL_RUN"
    elif gate_pass:
        decision = "PASS_A7FFCORE49E_NULL_VECTOR_PREFLIGHT_READY_FOR_CORE50_CONTRACT"
    else:
        decision = "HOLD_A7FFCORE49E_NULL_VECTOR_PREFLIGHT_BLOCKERS"
    manifest = {
        "stage": "A7FF-CORE49E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE49",
        "source_decision": source.get("decision"),
        "decision": decision,
        "is_partial_smoke": is_partial_smoke,
        "source_seed_count": source_seed_count,
        "seed_count": int(len(queue)),
        "frame_rows": int(len(evaluator.frame)),
        "frame_symbols": int(evaluator.frame["symbol"].nunique()),
        "required_field_count": int(len(required_fields)),
        "missing_field_count": missing_field_count,
        "eval_failure_count": eval_failure_count,
        "materialization_pass_count": pass_count,
        "external_vector_sample": str(sample_path).replace("\\", "/") if not sample_df.empty else "",
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core50_contract": decision == "PASS_A7FFCORE49E_NULL_VECTOR_PREFLIGHT_READY_FOR_CORE50_CONTRACT",
        "authorizes_core49e_full_run": decision == "PASS_A7FFCORE49E_PARTIAL_NULL_VECTOR_SMOKE_READY_FOR_FULL_RUN",
        "authorizes_numeric_replay": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE49E full run" if is_partial_smoke and gate_pass else "A7FF-CORE50 null-vector preflight forensic or replay contract arbitration",
    }
    authorization = {
        "authorized": {
            "A7FF-CORE49E full run": decision == "PASS_A7FFCORE49E_PARTIAL_NULL_VECTOR_SMOKE_READY_FOR_FULL_RUN",
            "A7FF-CORE50 contract/arbitration": decision == "PASS_A7FFCORE49E_NULL_VECTOR_PREFLIGHT_READY_FOR_CORE50_CONTRACT",
            "A7FF-CORE49ER preflight forensic": not decision.startswith("PASS_"),
        },
        "not_authorized": {
            "numeric_replay": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    write_json(RUNTIME / "a7ffcore49e_manifest.json", manifest)
    write_json(RUNTIME / "a7ffcore49e_authorization_matrix.json", authorization)

    report = [
        "# CRYPTO A7FF-CORE49E FULL-UNIVERSE NULL-VECTOR PREFLIGHT EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE49E materializes original/null vector diagnostics over the full available universe frame. It does not execute replay, search, proof, promotion, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family / Operator Summary",
        "",
        md_table(family_summary, 80),
        "",
        "## Missing Fields",
        "",
        md_table(pd.DataFrame({"missing_field": missing_fields}), 80),
        "",
        "## Eval Failures",
        "",
        md_table(failures_df, 80),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
