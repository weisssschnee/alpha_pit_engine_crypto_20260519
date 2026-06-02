from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra
from crypto_a7ffcore49e_full_universe_null_vector_preflight_execution import (
    extract_fields,
    read_base_panel,
    overlay_latent_fields,
    vector_controls,
)
from crypto_a7ffcore51e_filtered_replay_execution import add_labels, select_balanced, HORIZONS


RUNTIME = REPO / "runtime" / "a7ffcore51p_optimized_replay_runner_smoke"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE51P_OPTIMIZED_REPLAY_RUNNER_SMOKE_20260602.md"
CORE51ER = REPO / "runtime" / "a7ffcore51er_replay_runner_performance_forensic" / "a7ffcore51er_manifest.json"
FILTERED = REPO / "runtime" / "a7ffcore50_null_vector_preflight_arbitration" / "a7ffcore50_filtered_seed_preview.csv"
SMOKE_COUNT = 16


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


def dense_index(frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, int, int]:
    timestamps = pd.Categorical(frame["timestamp"], categories=sorted(frame["timestamp"].dropna().unique()), ordered=True)
    symbols = pd.Categorical(frame["symbol"], categories=sorted(frame["symbol"].dropna().unique()), ordered=True)
    return timestamps.codes.astype(np.int32), symbols.codes.astype(np.int32), len(timestamps.categories), len(symbols.categories)


def dense_matrix(values: pd.Series, row_idx: np.ndarray, col_idx: np.ndarray, n_rows: int, n_cols: int) -> np.ndarray:
    matrix = np.full((n_rows, n_cols), np.nan, dtype=np.float32)
    array = pd.to_numeric(values, errors="coerce").to_numpy(dtype=np.float32, na_value=np.nan)
    valid = (row_idx >= 0) & (col_idx >= 0)
    matrix[row_idx[valid], col_idx[valid]] = array[valid]
    return matrix


def dense_spread(signal_matrix: np.ndarray, label_matrix: np.ndarray) -> tuple[float, float, int]:
    finite_signal = np.isfinite(signal_matrix)
    finite_label = np.isfinite(label_matrix)
    valid = finite_signal & finite_label
    row_counts = valid.sum(axis=1)
    enough = row_counts >= 20
    if not bool(enough.any()):
        return np.nan, np.nan, 0
    masked_signal = np.where(valid, signal_matrix, np.nan)
    q90 = np.nanpercentile(masked_signal[enough], 90, axis=1)
    q10 = np.nanpercentile(masked_signal[enough], 10, axis=1)
    sub_signal = masked_signal[enough]
    sub_label = np.where(valid[enough], label_matrix[enough], np.nan)
    top = np.where(sub_signal >= q90[:, None], sub_label, np.nan)
    bottom = np.where(sub_signal <= q10[:, None], sub_label, np.nan)
    top_mean = np.nanmean(top, axis=1)
    bottom_mean = np.nanmean(bottom, axis=1)
    spreads = top_mean - bottom_mean
    spreads = spreads[np.isfinite(spreads)]
    if len(spreads) == 0:
        return np.nan, np.nan, 0
    mean = float(np.mean(spreads))
    std = float(np.std(spreads, ddof=1)) if len(spreads) > 1 else np.nan
    tstat = mean / (std / np.sqrt(len(spreads))) if std and np.isfinite(std) and std > 0 else np.nan
    return mean, float(tstat) if np.isfinite(tstat) else np.nan, int(len(spreads))


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE51ER)
    if source.get("decision") != "HOLD_A7FFCORE51ER_REPLAY_RUNNER_PERFORMANCE_BLOCKER":
        raise SystemExit(f"CORE51ER not ready for CORE51P: {source.get('decision')}")

    started = time.perf_counter()
    filtered = pd.read_csv(FILTERED)
    selected = select_balanced(filtered, SMOKE_COUNT)
    required_fields = extract_fields(selected["expression"]) + ["trade_close", "split"]
    frame = read_base_panel(required_fields)
    frame = overlay_latent_fields(frame, required_fields)
    frame = add_labels(frame)
    allowed_fields = set(frame.columns) - {"symbol", "timestamp"}
    evaluator = CryptoFeatureAlgebra(frame[["symbol", "timestamp", *sorted(allowed_fields)]].copy(), set(allowed_fields))
    replay_frame = evaluator.frame.copy()
    for col in [c for c in frame.columns if c.startswith("label_") or c == "split"]:
        replay_frame[col] = frame[col].to_numpy()

    row_idx, col_idx, n_ts, n_symbols = dense_index(replay_frame)
    label_matrices = {
        f"{family}_{horizon}h": dense_matrix(replay_frame[col], row_idx, col_idx, n_ts, n_symbols)
        for horizon in HORIZONS
        for family, col in [("L0_raw", f"label_raw_{horizon}h"), ("L1_xs", f"label_xs_{horizon}h")]
    }

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for _, seed in selected.iterrows():
        try:
            values = evaluator.evaluate(str(seed["expression"])).values
            controls = vector_controls(values, evaluator.frame)
            signal_map = {"original": values, "stale": controls["stale_signal"], "time_shuffle": controls["time_shuffle_signal"], "symbol_shuffle": controls["symbol_shuffle_signal"], "sign_flip": controls["sign_flip_signal"]}
            dense_signals = {name: dense_matrix(series, row_idx, col_idx, n_ts, n_symbols) for name, series in signal_map.items()}
        except Exception as exc:
            failures.append({"seed_id": seed["seed_id"], "error": str(exc)})
            continue
        for label_key, label_matrix in label_matrices.items():
            original_mean, original_tstat, obs = dense_spread(dense_signals["original"], label_matrix)
            control_means = []
            for control_name in ["stale", "time_shuffle", "symbol_shuffle", "sign_flip"]:
                mean, _, _ = dense_spread(dense_signals[control_name], label_matrix)
                control_means.append(abs(mean) if np.isfinite(mean) else np.nan)
            control_max = np.nanmax(control_means)
            original_abs = abs(original_mean) if np.isfinite(original_mean) else np.nan
            control_ratio = control_max / original_abs if np.isfinite(original_abs) and original_abs > 1e-12 else np.nan
            rows.append(
                {
                    "seed_id": seed["seed_id"],
                    "semantic_pair": seed["semantic_pair"],
                    "operator": seed["operator"],
                    "label_key": label_key,
                    "original_spread_mean": original_mean,
                    "original_tstat": original_tstat,
                    "spread_obs": obs,
                    "control_ratio": control_ratio,
                    "decision": "control_clean_positive" if np.isfinite(control_ratio) and control_ratio < 1.0 and original_mean > 0 else "not_control_clean_positive",
                }
            )

    elapsed = time.perf_counter() - started
    replay = pd.DataFrame(rows)
    failures_df = pd.DataFrame(failures)
    summary = (
        replay.groupby("label_key", as_index=False)
        .agg(row_count=("seed_id", "count"), control_clean_positive_count=("decision", lambda s: int((s == "control_clean_positive").sum())), median_control_ratio=("control_ratio", "median"))
        .sort_values("label_key")
    )
    replay.to_csv(RUNTIME / "a7ffcore51p_smoke_replay_metrics.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore51p_smoke_label_summary.csv", index=False)
    failures_df.to_csv(RUNTIME / "a7ffcore51p_smoke_failures.csv", index=False)

    decision = (
        "PASS_A7FFCORE51P_OPTIMIZED_REPLAY_RUNNER_READY_FOR_CORE51E_RERUN"
        if elapsed <= 300 and failures_df.empty and not replay.empty
        else "HOLD_A7FFCORE51P_OPTIMIZED_REPLAY_RUNNER_STILL_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE51P",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE51ER",
        "source_decision": source.get("decision"),
        "decision": decision,
        "elapsed_seconds": round(float(elapsed), 3),
        "selected_count": int(selected.shape[0]),
        "frame_rows": int(len(replay_frame)),
        "frame_symbols": int(replay_frame["symbol"].nunique()),
        "timestamp_count": int(n_ts),
        "replay_metric_rows": int(replay.shape[0]),
        "eval_failure_count": int(len(failures_df)),
        "executes_replay": True,
        "executes_search": False,
        "executes_generation": False,
        "authorizes_core51e_optimized_rerun": decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE51E optimized filtered replay rerun" if decision.startswith("PASS_") else "A7FF-CORE51P runner repair",
    }
    authorization = {
        "authorized": {
            "A7FF-CORE51E optimized filtered replay rerun": decision.startswith("PASS_"),
            "A7FF-CORE51P runner repair": not decision.startswith("PASS_"),
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    write_json(RUNTIME / "a7ffcore51p_manifest.json", manifest)
    write_json(RUNTIME / "a7ffcore51p_authorization_matrix.json", authorization)

    report = [
        "# CRYPTO A7FF-CORE51P OPTIMIZED REPLAY RUNNER SMOKE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE51P validates a dense-matrix replay runner over 16 filtered candidates. It is an optimization smoke, not search/proof/promotion.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Summary",
        "",
        md_table(summary, 80),
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
