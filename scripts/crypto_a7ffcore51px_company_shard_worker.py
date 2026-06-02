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
from crypto_a7ffcore51p_optimized_replay_runner_smoke import dense_index, dense_matrix, dense_spread


HORIZONS = [1, 4, 8, 24]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
            dense_signals = {name: dense_matrix(series, row_idx, col_idx, n_ts, n_symbols) for name, series in signal_map.items()}
        except Exception as exc:
            failures.append({"seed_id": seed.get("seed_id", ""), "expression": seed.get("expression", ""), "error": str(exc)})
            continue
        for label_key, label_matrix in label_matrices.items():
            original_mean, original_tstat, obs = dense_spread(dense_signals["original"], label_matrix)
            control_means = []
            control_spreads = {}
            for control_name in ["stale", "time_shuffle", "symbol_shuffle", "sign_flip"]:
                mean, _, _ = dense_spread(dense_signals[control_name], label_matrix)
                control_spreads[f"{control_name}_spread_mean"] = mean
                control_means.append(abs(mean) if np.isfinite(mean) else np.nan)
            control_max = np.nanmax(control_means)
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
