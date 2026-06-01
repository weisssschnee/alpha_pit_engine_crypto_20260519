from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7ffcore30e_bounded_numeric_probe import build_signal, load_dataset


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore43e_control_vector_rebuild_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE43E_CONTROL_VECTOR_REBUILD_AUDIT_20260602.md"
CORE43 = REPO / "runtime" / "a7ffcore43_control_orthogonalization_contract" / "a7ffcore43_manifest.json"
CORE33_QUEUE = REPO / "runtime" / "a7ffcore33_bounded_replay_contract" / "a7ffcore33_replay_candidate_queue.csv"
ARTIFACT_ROOT = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore43e_control_vectors_20260602")

MAX_TIMESTAMPS_PER_DATASET = 48
STALE_LAG_H = 24
SHUFFLE_TIME_LAG = 7
MIN_RESIDUAL_FIT_ROWS = 30


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


def choose_timestamps(df: pd.DataFrame, max_timestamps: int) -> pd.Index:
    stamps = pd.Index(sorted(df["timestamp"].dropna().unique()))
    if len(stamps) <= max_timestamps:
        return stamps
    idx = np.linspace(0, len(stamps) - 1, max_timestamps).round().astype(int)
    return stamps[idx]


def choose_signal_timestamps(
    df: pd.DataFrame,
    original: pd.Series,
    stale: pd.Series,
    shuffle_time: pd.Series,
    max_timestamps: int,
) -> pd.Index:
    symbol_count = max(int(df["symbol"].nunique()), 1)
    min_symbols_per_timestamp = max(10, int(symbol_count * 0.10))
    eligible = original.notna() & stale.notna() & shuffle_time.notna()
    counts = df.loc[eligible, "timestamp"].value_counts()
    stamps = pd.Index(sorted(counts[counts.ge(min_symbols_per_timestamp)].index))
    if len(stamps) == 0:
        stamps = pd.Index(sorted(df.loc[original.notna(), "timestamp"].dropna().unique()))
    if len(stamps) > max_timestamps:
        idx = np.linspace(0, len(stamps) - 1, max_timestamps).round().astype(int)
        stamps = stamps[idx]
    return stamps


def split_name(timestamp: pd.Series) -> pd.Series:
    ts = pd.to_datetime(timestamp, utc=True)
    out = pd.Series("recent_2026JanApr", index=timestamp.index, dtype=object)
    out.loc[ts.lt(pd.Timestamp("2025-01-01", tz="UTC"))] = "train_2024"
    out.loc[ts.ge(pd.Timestamp("2025-01-01", tz="UTC")) & ts.lt(pd.Timestamp("2025-07-01", tz="UTC"))] = "validation_2025H1"
    out.loc[ts.ge(pd.Timestamp("2025-07-01", tz="UTC")) & ts.lt(pd.Timestamp("2026-01-01", tz="UTC"))] = "test_2025H2"
    return out


def rotate_symbol_control(work: pd.DataFrame) -> pd.Series:
    parts: list[pd.Series] = []
    for _, group in work.groupby("timestamp", sort=False):
        ordered = group.sort_values("symbol")
        rotated = ordered["candidate_score_original"].shift(1)
        if len(rotated) > 1:
            rotated.iloc[0] = ordered["candidate_score_original"].iloc[-1]
        parts.append(pd.Series(rotated.to_numpy(), index=ordered.index))
    return pd.concat(parts).sort_index().astype("float32") if parts else pd.Series(dtype="float32")


def beta_residual(y: pd.Series, xcols: list[pd.Series]) -> tuple[pd.Series, dict[str, float]]:
    matrix = pd.concat([y.rename("y"), *[x.rename(f"x{i}") for i, x in enumerate(xcols)]], axis=1)
    clean = matrix.replace([np.inf, -np.inf], np.nan).dropna()
    if clean.shape[0] < MIN_RESIDUAL_FIT_ROWS or clean["y"].std() == 0:
        return pd.Series(np.nan, index=y.index, dtype="float32"), {
            "fit_rows": int(clean.shape[0]),
            "r2": np.nan,
            "residual_std": np.nan,
            "original_std": float(y.std(skipna=True)) if y.notna().any() else np.nan,
        }
    x = clean.drop(columns=["y"]).to_numpy(dtype="float64")
    x = np.column_stack([np.ones(x.shape[0]), x])
    target = clean["y"].to_numpy(dtype="float64")
    coef, *_ = np.linalg.lstsq(x, target, rcond=None)
    pred = x @ coef
    resid_fit = target - pred
    ss_tot = float(np.sum((target - target.mean()) ** 2))
    ss_res = float(np.sum(resid_fit**2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    all_x = pd.concat(xcols, axis=1).replace([np.inf, -np.inf], np.nan)
    valid = all_x.notna().all(axis=1) & y.notna()
    resid = pd.Series(np.nan, index=y.index, dtype="float32")
    if valid.any():
        all_design = np.column_stack([np.ones(int(valid.sum())), all_x.loc[valid].to_numpy(dtype="float64")])
        resid.loc[valid] = (y.loc[valid].to_numpy(dtype="float64") - all_design @ coef).astype("float32")
    return resid, {
        "fit_rows": int(clean.shape[0]),
        "r2": float(r2),
        "residual_std": float(resid.std(skipna=True)) if resid.notna().any() else np.nan,
        "original_std": float(y.std(skipna=True)) if y.notna().any() else np.nan,
    }


def vector_packet_for_candidate(
    df: pd.DataFrame,
    row: pd.Series,
    signal: pd.Series,
    sample_timestamps: pd.Index,
    *,
    quote_col: str,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    original_all = signal.astype("float32")
    stale_all = signal.groupby(df["symbol"], sort=False).shift(STALE_LAG_H).astype("float32")
    shuffle_time_all = signal.groupby(df["symbol"], sort=False).shift(SHUFFLE_TIME_LAG).astype("float32")
    candidate_timestamps = choose_signal_timestamps(
        df,
        original_all,
        stale_all,
        shuffle_time_all,
        MAX_TIMESTAMPS_PER_DATASET,
    )
    if len(candidate_timestamps) == 0:
        candidate_timestamps = sample_timestamps
    base_cols = ["symbol", "timestamp", quote_col]
    work = df.loc[df["timestamp"].isin(candidate_timestamps), base_cols].copy()
    work["candidate_id"] = row["replay_candidate_id"]
    work["family_id"] = row["family_id"]
    work["dataset"] = row["dataset"]
    work["cluster_key"] = row["cluster_key"]
    work["split"] = split_name(work["timestamp"]).to_numpy()
    work["candidate_score_original"] = original_all.loc[work.index].astype("float32")
    work["candidate_score_stale"] = stale_all.loc[work.index].astype("float32")
    work["candidate_score_sign_flip"] = (-work["candidate_score_original"]).astype("float32")
    work["candidate_score_shuffle_time"] = shuffle_time_all.loc[work.index].astype("float32")
    work["candidate_score_shuffle_symbol"] = rotate_symbol_control(work)
    work["quote_volume"] = pd.to_numeric(work[quote_col], errors="coerce").astype("float32")

    stale_resid, stale_stats = beta_residual(
        work["candidate_score_original"], [work["candidate_score_stale"]]
    )
    null_resid, null_stats = beta_residual(
        work["candidate_score_original"],
        [
            work["candidate_score_stale"],
            work["candidate_score_shuffle_time"],
            work["candidate_score_shuffle_symbol"],
        ],
    )
    work["residual_score_stale_orthogonal"] = stale_resid
    work["residual_score_null_orthogonal"] = null_resid
    for col in [
        "candidate_score_original",
        "candidate_score_stale",
        "candidate_score_sign_flip",
        "candidate_score_shuffle_time",
        "candidate_score_shuffle_symbol",
        "residual_score_stale_orthogonal",
        "residual_score_null_orthogonal",
    ]:
        work[f"{col}_rank"] = work[col].groupby(work["timestamp"]).rank(pct=True, method="average").astype("float32")

    quality = {
        "candidate_id": row["replay_candidate_id"],
        "family_id": row["family_id"],
        "dataset": row["dataset"],
        "sample_rows": int(work.shape[0]),
        "sample_symbols": int(work["symbol"].nunique()),
        "sample_timestamps": int(work["timestamp"].nunique()),
        "candidate_timestamp_selection": "signal_valid_control_ready",
        "original_non_null_ratio": float(work["candidate_score_original"].notna().mean()) if len(work) else 0.0,
        "stale_non_null_ratio": float(work["candidate_score_stale"].notna().mean()) if len(work) else 0.0,
        "shuffle_time_non_null_ratio": float(work["candidate_score_shuffle_time"].notna().mean()) if len(work) else 0.0,
        "shuffle_symbol_non_null_ratio": float(work["candidate_score_shuffle_symbol"].notna().mean()) if len(work) else 0.0,
        "original_std": float(work["candidate_score_original"].std(skipna=True)) if work["candidate_score_original"].notna().any() else np.nan,
        "residual_stale_std": float(work["residual_score_stale_orthogonal"].std(skipna=True)) if work["residual_score_stale_orthogonal"].notna().any() else np.nan,
        "residual_null_std": float(work["residual_score_null_orthogonal"].std(skipna=True)) if work["residual_score_null_orthogonal"].notna().any() else np.nan,
    }
    residual_quality = {
        "candidate_id": row["replay_candidate_id"],
        "family_id": row["family_id"],
        "dataset": row["dataset"],
        "stale_fit_rows": stale_stats["fit_rows"],
        "stale_r2": stale_stats["r2"],
        "stale_original_std": stale_stats["original_std"],
        "stale_residual_std": stale_stats["residual_std"],
        "null_fit_rows": null_stats["fit_rows"],
        "null_r2": null_stats["r2"],
        "null_original_std": null_stats["original_std"],
        "null_residual_std": null_stats["residual_std"],
        "residual_nonzero": bool(
            np.isfinite(quality["residual_null_std"]) and quality["residual_null_std"] > 1e-8
        ),
    }
    keep = [
        "candidate_id",
        "dataset",
        "family_id",
        "cluster_key",
        "timestamp",
        "symbol",
        "split",
        "quote_volume",
        "candidate_score_original",
        "candidate_score_stale",
        "candidate_score_sign_flip",
        "candidate_score_shuffle_time",
        "candidate_score_shuffle_symbol",
        "residual_score_stale_orthogonal",
        "residual_score_null_orthogonal",
        "candidate_score_original_rank",
        "residual_score_stale_orthogonal_rank",
        "residual_score_null_orthogonal_rank",
    ]
    return work[keep], quality, residual_quality


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE43)
    if source.get("decision") != "PASS_A7FFCORE43_CONTROL_ORTHOGONALIZATION_CONTRACT_READY_FOR_CORE43E":
        raise SystemExit(f"CORE43 not ready for CORE43E: {source.get('decision')}")

    queue = pd.read_csv(CORE33_QUEUE)
    vector_packets: list[pd.DataFrame] = []
    dataset_rows: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    for dataset_name, q in queue.groupby("dataset", sort=True):
        fields = set(q["primary_field"].astype(str)).union(set(q["partner_field"].astype(str)))
        quote_col = "trade_quote_volume" if dataset_name == "top498_replay_v2" else "agg_notional"
        fields.add(quote_col)
        df = load_dataset(dataset_name, fields)
        sample_timestamps = choose_timestamps(df, MAX_TIMESTAMPS_PER_DATASET)
        dataset_rows.append(
            {
                "dataset": dataset_name,
                "source_rows": int(df.shape[0]),
                "source_symbols": int(df["symbol"].nunique()),
                "source_timestamps": int(df["timestamp"].nunique()),
                "sample_timestamps": int(len(sample_timestamps)),
                "candidate_count": int(q.shape[0]),
                "quote_col": quote_col,
            }
        )
        cache: dict[tuple[str, str, int], pd.Series] = {}
        for _, row in q.reset_index(drop=True).iterrows():
            signal = build_signal(df, row, cache)
            packet, quality, residual_quality = vector_packet_for_candidate(
                df, row, signal, sample_timestamps, quote_col=quote_col
            )
            vector_packets.append(packet)
            quality_rows.append(quality)
            residual_rows.append(residual_quality)

    vector_sample = pd.concat(vector_packets, ignore_index=True) if vector_packets else pd.DataFrame()
    sample_path = ARTIFACT_ROOT / "a7ffcore43e_full_universe_control_vector_sample.parquet"
    if not vector_sample.empty:
        vector_sample.to_parquet(sample_path, index=False)

    dataset_summary = pd.DataFrame(dataset_rows)
    candidate_quality = pd.DataFrame(quality_rows)
    residual_quality = pd.DataFrame(residual_rows)
    required_cols = [
        "candidate_score_original",
        "candidate_score_stale",
        "candidate_score_sign_flip",
        "candidate_score_shuffle_time",
        "candidate_score_shuffle_symbol",
        "residual_score_stale_orthogonal",
        "residual_score_null_orthogonal",
    ]
    sample_quality = pd.DataFrame(
        [
            {
                "metric": "vector_sample_rows",
                "value": int(vector_sample.shape[0]),
                "pass": bool(vector_sample.shape[0] > 0),
            },
            {
                "metric": "candidate_count",
                "value": int(candidate_quality["candidate_id"].nunique()) if not candidate_quality.empty else 0,
                "pass": bool(not candidate_quality.empty and candidate_quality["candidate_id"].nunique() == queue["replay_candidate_id"].nunique()),
            },
            {
                "metric": "required_vector_columns_present",
                "value": int(sum(col in vector_sample.columns for col in required_cols)),
                "pass": bool(all(col in vector_sample.columns for col in required_cols)),
            },
            {
                "metric": "min_original_non_null_ratio",
                "value": float(candidate_quality["original_non_null_ratio"].min()) if not candidate_quality.empty else 0.0,
                "pass": bool(not candidate_quality.empty and candidate_quality["original_non_null_ratio"].min() >= 0.20),
            },
            {
                "metric": "min_residual_null_std",
                "value": float(residual_quality["null_residual_std"].min(skipna=True)) if not residual_quality.empty else 0.0,
                "pass": bool(not residual_quality.empty and residual_quality["residual_nonzero"].all()),
            },
            {
                "metric": "min_null_fit_rows",
                "value": int(residual_quality["null_fit_rows"].min()) if not residual_quality.empty else 0,
                "pass": bool(not residual_quality.empty and residual_quality["null_fit_rows"].min() >= MIN_RESIDUAL_FIT_ROWS),
            },
        ]
    )
    decision = (
        "PASS_A7FFCORE43E_CONTROL_VECTOR_REBUILD_READY_FOR_CORE44"
        if bool(sample_quality["pass"].all())
        else "HOLD_A7FFCORE43E_CONTROL_VECTOR_REBUILD_INCOMPLETE"
    )
    artifact_manifest = pd.DataFrame(
        [
            {
                "artifact": "full_universe_control_vector_sample",
                "path": str(sample_path).replace("\\", "/"),
                "committed_to_git": False,
                "rows": int(vector_sample.shape[0]),
                "columns": int(vector_sample.shape[1]) if not vector_sample.empty else 0,
                "bytes": int(sample_path.stat().st_size) if sample_path.exists() else 0,
            }
        ]
    )
    authorization = {
        "authorized": {
            "A7FF-CORE44 full-universe orthogonal score packet construction contract": decision.startswith("PASS")
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "new_generation": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
            "book_replay_execution_from_selected_packet": True,
        },
    }
    manifest = {
        "stage": "A7FF-CORE43E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE43",
        "source_decision": source.get("decision"),
        "decision": decision,
        "candidate_count": int(queue["replay_candidate_id"].nunique()),
        "dataset_count": int(queue["dataset"].nunique()),
        "vector_sample_rows": int(vector_sample.shape[0]),
        "vector_sample_columns": int(vector_sample.shape[1]) if not vector_sample.empty else 0,
        "min_residual_fit_rows_required": MIN_RESIDUAL_FIT_ROWS,
        "external_sample_path": str(sample_path).replace("\\", "/"),
        "executes_search": False,
        "executes_new_generation": False,
        "authorizes_core44_contract": decision.startswith("PASS"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE44 full-universe orthogonal score packet construction contract"
        if decision.startswith("PASS")
        else "A7FF-CORE43E repair / rerun only",
    }
    dataset_summary.to_csv(RUNTIME / "a7ffcore43e_dataset_summary.csv", index=False)
    candidate_quality.to_csv(RUNTIME / "a7ffcore43e_candidate_vector_quality.csv", index=False)
    residual_quality.to_csv(RUNTIME / "a7ffcore43e_residualization_quality.csv", index=False)
    sample_quality.to_csv(RUNTIME / "a7ffcore43e_sample_quality_gate.csv", index=False)
    artifact_manifest.to_csv(RUNTIME / "a7ffcore43e_control_vector_artifact_manifest.csv", index=False)
    write_json(RUNTIME / "a7ffcore43e_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore43e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE43E CONTROL VECTOR REBUILD AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE43E rebuilds bounded full-universe candidate/control score vectors from existing CORE33 candidates and panels. It is audit-only: no new formula generation, search, alpha proof, shadow, paper, or live authorization.",
        "",
        "## Dataset Summary",
        "",
        md_table(dataset_summary),
        "",
        "## Sample Quality Gate",
        "",
        md_table(sample_quality),
        "",
        "## Candidate Vector Quality",
        "",
        md_table(candidate_quality),
        "",
        "## Residualization Quality",
        "",
        md_table(residual_quality),
        "",
        "## External Artifact",
        "",
        md_table(artifact_manifest),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
