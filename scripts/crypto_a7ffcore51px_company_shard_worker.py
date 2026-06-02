from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra
from crypto_a7ffcore49e_full_universe_null_vector_preflight_execution import vector_controls
from crypto_a7ffcore51p_optimized_replay_runner_smoke import dense_index, dense_matrix


HORIZONS = [1, 4, 8, 24]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def decile_spread_fast(signal_matrix: np.ndarray, label_matrix: np.ndarray) -> tuple[float, float, int]:
    """Compute hourly top-bottom decile spread without row-wise nanpercentile allocations."""
    spreads: list[float] = []
    for signal_row, label_row in zip(signal_matrix, label_matrix):
        valid = np.isfinite(signal_row) & np.isfinite(label_row)
        n = int(valid.sum())
        if n < 20:
            continue
        s = signal_row[valid]
        l = label_row[valid]
        k = max(1, int(np.ceil(0.1 * n)))
        order = np.argpartition(s, (k - 1, n - k))
        bottom_mean = float(np.mean(l[order[:k]]))
        top_mean = float(np.mean(l[order[n - k :]]))
        spread = top_mean - bottom_mean
        if np.isfinite(spread):
            spreads.append(spread)
    if not spreads:
        return np.nan, np.nan, 0
    values = np.asarray(spreads, dtype=np.float64)
    mean = float(values.mean())
    std = float(values.std(ddof=1)) if values.size > 1 else np.nan
    tstat = mean / (std / np.sqrt(values.size)) if np.isfinite(std) and std > 0 else np.nan
    return mean, float(tstat) if np.isfinite(tstat) else np.nan, int(values.size)


def decile_spreads_for_labels(
    signal_matrix: np.ndarray, label_matrices: dict[str, np.ndarray]
) -> dict[str, tuple[float, float, int]]:
    """Compute decile spreads for all labels while reusing each hourly signal sort."""
    spread_lists: dict[str, list[float]] = {label_key: [] for label_key in label_matrices}
    label_items = list(label_matrices.items())
    for row_num, signal_row in enumerate(signal_matrix):
        finite_signal = np.isfinite(signal_row)
        n_signal = int(finite_signal.sum())
        if n_signal < 20:
            continue
        finite_cols = np.flatnonzero(finite_signal)
        ordered_cols = finite_cols[np.argsort(signal_row[finite_cols])]
        for label_key, label_matrix in label_items:
            label_row = label_matrix[row_num]
            usable_cols = ordered_cols[np.isfinite(label_row[ordered_cols])]
            n = int(usable_cols.size)
            if n < 20:
                continue
            k = max(1, int(np.ceil(0.1 * n)))
            spread = float(np.mean(label_row[usable_cols[-k:]]) - np.mean(label_row[usable_cols[:k]]))
            if np.isfinite(spread):
                spread_lists[label_key].append(spread)
    out: dict[str, tuple[float, float, int]] = {}
    for label_key, spreads in spread_lists.items():
        if not spreads:
            out[label_key] = (np.nan, np.nan, 0)
            continue
        values = np.asarray(spreads, dtype=np.float64)
        mean = float(values.mean())
        std = float(values.std(ddof=1)) if values.size > 1 else np.nan
        tstat = mean / (std / np.sqrt(values.size)) if np.isfinite(std) and std > 0 else np.nan
        out[label_key] = (mean, float(tstat) if np.isfinite(tstat) else np.nan, int(values.size))
    return out


def decile_spreads_vectorized(
    signal_matrix: np.ndarray, label_matrices: dict[str, np.ndarray]
) -> dict[str, tuple[float, float, int]]:
    finite_signal = np.isfinite(signal_matrix)
    row_counts = finite_signal.sum(axis=1).astype(np.int32)
    enough = row_counts >= 20
    if not bool(enough.any()):
        return {label_key: (np.nan, np.nan, 0) for label_key in label_matrices}
    k = np.ceil(row_counts * 0.1).astype(np.int32)
    k = np.maximum(k, 1)
    max_k = int(k[enough].max())
    sort_input = np.where(finite_signal, signal_matrix, np.inf)
    order = np.argsort(sort_input, axis=1)
    ar = np.arange(max_k, dtype=np.int32)
    bottom_idx = order[:, :max_k]
    bottom_mask = enough[:, None] & (ar[None, :] < k[:, None])
    top_positions = row_counts[:, None] - max_k + ar[None, :]
    top_positions = np.clip(top_positions, 0, signal_matrix.shape[1] - 1)
    top_idx = np.take_along_axis(order, top_positions, axis=1)
    top_mask = enough[:, None] & (ar[None, :] >= (max_k - k)[:, None])
    out: dict[str, tuple[float, float, int]] = {}
    for label_key, label_matrix in label_matrices.items():
        bottom_values = np.take_along_axis(label_matrix, bottom_idx, axis=1)
        top_values = np.take_along_axis(label_matrix, top_idx, axis=1)
        bottom_valid = bottom_mask & np.isfinite(bottom_values)
        top_valid = top_mask & np.isfinite(top_values)
        bottom_count = bottom_valid.sum(axis=1)
        top_count = top_valid.sum(axis=1)
        bottom_sum = np.where(bottom_valid, bottom_values, 0.0).sum(axis=1, dtype=np.float64)
        top_sum = np.where(top_valid, top_values, 0.0).sum(axis=1, dtype=np.float64)
        valid_rows = (bottom_count > 0) & (top_count > 0)
        if not bool(valid_rows.any()):
            out[label_key] = (np.nan, np.nan, 0)
            continue
        spreads = (top_sum[valid_rows] / top_count[valid_rows]) - (bottom_sum[valid_rows] / bottom_count[valid_rows])
        spreads = spreads[np.isfinite(spreads)]
        if spreads.size == 0:
            out[label_key] = (np.nan, np.nan, 0)
            continue
        mean = float(spreads.mean())
        std = float(spreads.std(ddof=1)) if spreads.size > 1 else np.nan
        tstat = mean / (std / np.sqrt(spreads.size)) if np.isfinite(std) and std > 0 else np.nan
        out[label_key] = (mean, float(tstat) if np.isfinite(tstat) else np.nan, int(spreads.size))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", required=True, help="Candidate shard CSV")
    parser.add_argument("--compact-frame", required=True, help="Compact frame parquet built by CORE51PX builder")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    shard_path = Path(args.shard)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    shard_id = shard_path.stem
    metrics_path = out_dir / f"{shard_id}_metrics.csv"
    manifest_path = out_dir / f"{shard_id}_manifest.json"
    if manifest_path.exists() and metrics_path.exists() and not args.force:
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("decision", "").startswith("PASS_"):
            print(json.dumps(existing, indent=2, sort_keys=True))
            return

    candidates = pd.read_csv(shard_path)
    frame = pd.read_parquet(args.compact_frame)
    frame = frame.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    allowed_fields = set(frame.columns) - {"symbol", "timestamp"}
    evaluator = CryptoFeatureAlgebra(frame[["symbol", "timestamp", *sorted(allowed_fields)]].copy(), set(allowed_fields))
    replay_frame = evaluator.frame.copy()
    for col in [c for c in frame.columns if c.startswith("label_")]:
        replay_frame[col] = frame[col].to_numpy()
    row_idx, col_idx, n_ts, n_symbols = dense_index(replay_frame)
    label_matrices = {
        f"{family}_{horizon}h": dense_matrix(replay_frame[col], row_idx, col_idx, n_ts, n_symbols)
        for horizon in HORIZONS
        for family, col in [("L0_raw", f"label_raw_{horizon}h"), ("L1_xs", f"label_xs_{horizon}h")]
        if col in replay_frame.columns
    }

    rows: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    for _, seed in candidates.iterrows():
        try:
            values = evaluator.evaluate(str(seed["expression"])).values
            controls = vector_controls(values, evaluator.frame)
            signal_map = {
                "original": values,
                "stale": controls["stale_signal"],
                "time_shuffle": controls["time_shuffle_signal"],
                "symbol_shuffle": controls["symbol_shuffle_signal"],
                "sign_flip": controls["sign_flip_signal"],
            }
            spread_maps = {
                name: decile_spreads_vectorized(dense_matrix(series, row_idx, col_idx, n_ts, n_symbols), label_matrices)
                for name, series in signal_map.items()
            }
        except Exception as exc:
            failures.append({"seed_id": seed.get("seed_id", ""), "expression": seed.get("expression", ""), "error": str(exc)})
            continue
        for label_key, label_matrix in label_matrices.items():
            original_mean, original_tstat, obs = spread_maps["original"][label_key]
            control_means = []
            control_spreads = {}
            for control_name in ["stale", "time_shuffle", "symbol_shuffle", "sign_flip"]:
                mean, _, _ = spread_maps[control_name][label_key]
                control_spreads[f"{control_name}_spread_mean"] = mean
                control_means.append(abs(mean) if np.isfinite(mean) else np.nan)
            control_max = np.nanmax(control_means) if any(np.isfinite(x) for x in control_means) else np.nan
            original_abs = abs(original_mean) if np.isfinite(original_mean) else np.nan
            control_ratio = control_max / original_abs if np.isfinite(original_abs) and original_abs > 1e-12 else np.nan
            rows.append(
                {
                    "shard_id": shard_id,
                    "seed_id": seed["seed_id"],
                    "semantic_pair": seed["semantic_pair"],
                    "operator": seed["operator"],
                    "stale_risk_tier": seed.get("stale_risk_tier", ""),
                    "label_key": label_key,
                    "original_spread_mean": original_mean,
                    "original_tstat": original_tstat,
                    "spread_obs": obs,
                    "control_ratio": control_ratio,
                    **control_spreads,
                    "decision": "control_clean_positive" if np.isfinite(control_ratio) and control_ratio < 1.0 and original_mean > 0 else "not_control_clean_positive",
                }
            )

    metrics = pd.DataFrame(rows)
    failures_df = pd.DataFrame(failures)
    metrics.to_csv(metrics_path, index=False)
    failures_df.to_csv(out_dir / f"{shard_id}_failures.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE51PXE-SHARD",
        "generated_at": now_utc(),
        "shard_id": shard_id,
        "candidate_count": int(candidates.shape[0]),
        "metric_rows": int(metrics.shape[0]),
        "eval_failure_count": int(failures_df.shape[0]),
        "control_clean_positive_rows": int(metrics["decision"].eq("control_clean_positive").sum()) if not metrics.empty else 0,
        "decision": "PASS_A7FFCORE51PXE_SHARD_REPLAY_COMPLETE" if failures_df.empty and not metrics.empty else "HOLD_A7FFCORE51PXE_SHARD_REPLAY_FAILURES",
        "executes_replay": True,
        "executes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
