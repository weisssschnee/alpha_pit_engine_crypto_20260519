from __future__ import annotations

import json
import sys
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
from crypto_a7ffcore49e_full_universe_null_vector_preflight_execution import (  # noqa: E402
    extract_fields,
    overlay_latent_fields,
    read_base_panel,
    vector_controls,
)
from crypto_a7ffcore51p_optimized_replay_runner_smoke import dense_index, dense_matrix  # noqa: E402
from crypto_a7ffcore51px_company_shard_worker import decile_spreads_vectorized  # noqa: E402
from crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore56_bounded_replay_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE56_BOUNDED_REPLAY_PREFLIGHT_20260604.md"
CORE55_MANIFEST = REPO / "runtime" / "a7ffcore55_numeric_clue_forensic" / "a7ffcore55_manifest.json"
CORE55_PACKET = REPO / "runtime" / "a7ffcore55_numeric_clue_forensic" / "a7ffcore55_replay_ready_packet.csv"

HORIZONS = [1, 4, 8, 24]
LABEL_FAMILIES = ["L0_raw", "L1_xs", "L3_liquidity_relative", "L5_vol_adjusted"]
PREMAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]


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


def add_labels(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.sort_values(["symbol", "timestamp"]).reset_index(drop=True).copy()
    close = pd.to_numeric(frame["trade_close"], errors="coerce").astype("float64")
    vol = pd.to_numeric(frame.get("realized_vol_168h", pd.Series(np.nan, index=frame.index)), errors="coerce").replace(0.0, np.nan)
    for horizon in HORIZONS:
        raw = close.groupby(frame["symbol"], sort=False).shift(-horizon) / close - 1.0
        raw = raw.replace([np.inf, -np.inf], np.nan)
        frame[f"label_L0_raw_{horizon}h"] = raw
        frame[f"label_L1_xs_{horizon}h"] = raw - raw.groupby(frame["timestamp"], sort=False).transform("mean")
        if "liquidity_tier" in frame.columns:
            frame[f"label_L3_liquidity_relative_{horizon}h"] = raw - raw.groupby(
                [frame["timestamp"], frame["liquidity_tier"]], sort=False
            ).transform("mean")
        else:
            frame[f"label_L3_liquidity_relative_{horizon}h"] = np.nan
        frame[f"label_L5_vol_adjusted_{horizon}h"] = raw / vol
    return frame


def label_matrices(
    replay_frame: pd.DataFrame,
    row_idx: np.ndarray,
    col_idx: np.ndarray,
    n_ts: int,
    n_symbols: int,
) -> dict[tuple[str, int], np.ndarray]:
    mats: dict[tuple[str, int], np.ndarray] = {}
    for family in LABEL_FAMILIES:
        for horizon in HORIZONS:
            col = f"label_{family}_{horizon}h"
            if col in replay_frame.columns:
                mats[(family, horizon)] = dense_matrix(replay_frame[col], row_idx, col_idx, n_ts, n_symbols)
    return mats


def split_masks(replay_frame: pd.DataFrame) -> dict[str, np.ndarray]:
    timestamps = pd.DatetimeIndex(sorted(replay_frame["timestamp"].dropna().unique()))
    split_timestamps = timestamps.tz_localize("UTC") if timestamps.tz is None else timestamps
    split_values = split_for_timestamps(split_timestamps)
    return {
        split_name: np.asarray(split_values == split_name, dtype=bool)
        for split_name in ["train_2024", *PREMAY_SPLITS]
    }


def spread_for_split(signal: np.ndarray, label: np.ndarray, mask: np.ndarray) -> tuple[float, float, int]:
    if mask.size != signal.shape[0]:
        return np.nan, np.nan, 0
    if not bool(mask.any()):
        return np.nan, np.nan, 0
    return decile_spreads_vectorized(signal[mask], {"label": label[mask]})["label"]


def evaluate_candidate(
    packet_row: pd.Series,
    evaluator: CryptoFeatureAlgebra,
    replay_frame: pd.DataFrame,
    row_idx: np.ndarray,
    col_idx: np.ndarray,
    n_ts: int,
    n_symbols: int,
    labels: dict[tuple[str, int], np.ndarray],
    masks: dict[str, np.ndarray],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    expression = str(packet_row["expression"])
    try:
        values = evaluator.evaluate(expression).values
        controls = vector_controls(values, evaluator.frame)
    except Exception as exc:  # noqa: BLE001
        return [], {
            "blueprint_id": packet_row.get("blueprint_id", ""),
            "expression": expression,
            "error": repr(exc),
        }
    signal_map = {
        "original": dense_matrix(values, row_idx, col_idx, n_ts, n_symbols),
        "stale": dense_matrix(controls["stale_signal"], row_idx, col_idx, n_ts, n_symbols),
        "time_shuffle": dense_matrix(controls["time_shuffle_signal"], row_idx, col_idx, n_ts, n_symbols),
        "symbol_shuffle": dense_matrix(controls["symbol_shuffle_signal"], row_idx, col_idx, n_ts, n_symbols),
        "sign_flip": dense_matrix(controls["sign_flip_signal"], row_idx, col_idx, n_ts, n_symbols),
    }
    rows: list[dict[str, Any]] = []
    for (family, horizon), label in labels.items():
        train_mean, _, _ = spread_for_split(signal_map["original"], label, masks["train_2024"])
        orientation = 1.0 if not np.isfinite(train_mean) or train_mean >= 0 else -1.0
        original_split_stats: dict[str, tuple[float, float, int]] = {}
        control_split_stats: dict[str, dict[str, tuple[float, float, int]]] = {}
        for split_name, mask in masks.items():
            mean, tstat, obs = spread_for_split(signal_map["original"], label, mask)
            original_split_stats[split_name] = (orientation * mean if np.isfinite(mean) else np.nan, orientation * tstat if np.isfinite(tstat) else np.nan, obs)
            control_split_stats[split_name] = {}
            for control_name in ["stale", "time_shuffle", "symbol_shuffle", "sign_flip"]:
                cmean, ctstat, cobs = spread_for_split(signal_map[control_name], label, mask)
                control_split_stats[split_name][control_name] = (
                    orientation * cmean if np.isfinite(cmean) else np.nan,
                    orientation * ctstat if np.isfinite(ctstat) else np.nan,
                    cobs,
                )
        premay_positive = sum(
            np.isfinite(original_split_stats[s][0]) and original_split_stats[s][0] > 0 for s in PREMAY_SPLITS
        )
        recent_spread = original_split_stats["recent_oos_2026JanApr"][0]
        stale_recent = control_split_stats["recent_oos_2026JanApr"]["stale"][0]
        control_ratios = []
        for split_name in PREMAY_SPLITS:
            orig = abs(original_split_stats[split_name][0]) if np.isfinite(original_split_stats[split_name][0]) else np.nan
            if not np.isfinite(orig) or orig <= 1e-12:
                continue
            vals = [abs(control_split_stats[split_name][name][0]) for name in ["time_shuffle", "symbol_shuffle", "sign_flip"]]
            vals = [v for v in vals if np.isfinite(v)]
            if vals:
                control_ratios.append(max(vals) / orig)
        control_ratio = max(control_ratios) if control_ratios else np.nan
        stale_ratio_recent = abs(stale_recent) / abs(recent_spread) if np.isfinite(stale_recent) and np.isfinite(recent_spread) and abs(recent_spread) > 1e-12 else np.nan
        cost5_recent = recent_spread - 0.001 if np.isfinite(recent_spread) else np.nan
        if premay_positive < 3:
            decision = "HOLD_CORE56_PREMAY_UNSTABLE"
        elif np.isfinite(control_ratio) and control_ratio >= 1.0:
            decision = "HOLD_CORE56_CONTROL_DOMINATED"
        elif not np.isfinite(stale_recent) or stale_recent <= 0 or (np.isfinite(stale_ratio_recent) and stale_ratio_recent < 0.25):
            decision = "HOLD_CORE56_STALE_LAG_FRAGILE"
        elif not np.isfinite(cost5_recent) or cost5_recent <= 0:
            decision = "HOLD_CORE56_COST5_FRAGILE"
        else:
            decision = "CORE56_REPLAY_CLEAN_CLUE"
        row = {
            "blueprint_id": packet_row["blueprint_id"],
            "expression": expression,
            "a7input_queue": packet_row.get("a7input_queue", ""),
            "semantic_pair": packet_row.get("semantic_pair", ""),
            "motif": packet_row.get("motif", ""),
            "skeleton_key": packet_row.get("skeleton_key", ""),
            "production_key": packet_row.get("production_key", ""),
            "label_family": family,
            "label_horizon_h": horizon,
            "orientation_from_train": orientation,
            "premay_positive_split_count": premay_positive,
            "control_ratio_premay_max": control_ratio,
            "stale_ratio_recent": stale_ratio_recent,
            "cost5_recent_oriented": cost5_recent,
            "decision": decision,
        }
        for split_name, (mean, tstat, obs) in original_split_stats.items():
            row[f"{split_name}_spread"] = mean
            row[f"{split_name}_tstat"] = tstat
            row[f"{split_name}_obs"] = obs
            for control_name, (cmean, _, _) in control_split_stats[split_name].items():
                row[f"{split_name}_{control_name}_spread"] = cmean
        rows.append(row)
    return rows, None


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE55_MANIFEST)
    if not source.get("authorizes_core56_bounded_replay_preflight"):
        raise SystemExit(f"CORE55 does not authorize CORE56: {source.get('decision')}")
    packet = pd.read_csv(CORE55_PACKET)
    required_fields = list(dict.fromkeys(extract_fields(packet["expression"]) + ["trade_close", "split", "realized_vol_168h", "liquidity_tier"]))
    frame = read_base_panel(required_fields)
    frame = overlay_latent_fields(frame, required_fields)
    frame = add_labels(frame)
    allowed_fields = set(frame.columns) - {"symbol", "timestamp"}
    evaluator = CryptoFeatureAlgebra(frame[["symbol", "timestamp", *sorted(allowed_fields)]].copy(), set(allowed_fields))
    replay_frame = evaluator.frame.copy()
    for col in [c for c in frame.columns if c.startswith("label_") or c == "split" or c == "liquidity_tier"]:
        replay_frame[col] = frame[col].to_numpy()
    row_idx, col_idx, n_ts, n_symbols = dense_index(replay_frame)
    labels = label_matrices(replay_frame, row_idx, col_idx, n_ts, n_symbols)
    masks = split_masks(replay_frame)

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for index, packet_row in enumerate(packet.to_dict("records"), start=1):
        result_rows, failure = evaluate_candidate(
            pd.Series(packet_row),
            evaluator,
            replay_frame,
            row_idx,
            col_idx,
            n_ts,
            n_symbols,
            labels,
            masks,
        )
        rows.extend(result_rows)
        if failure:
            failures.append(failure)
        if index % 16 == 0:
            print(f"[CORE56] replayed {index}/{len(packet)}", flush=True)

    replay = pd.DataFrame(rows)
    failures_df = pd.DataFrame(failures)
    replay.to_csv(RUNTIME / "a7ffcore56_replay_metrics.csv", index=False)
    failures_df.to_csv(RUNTIME / "a7ffcore56_eval_failures.csv", index=False)
    clean = replay[replay["decision"].eq("CORE56_REPLAY_CLEAN_CLUE")].copy() if not replay.empty else pd.DataFrame()
    clean.to_csv(RUNTIME / "a7ffcore56_replay_clean_candidates.csv", index=False)
    candidate_summary = (
        replay.groupby(["blueprint_id", "semantic_pair", "motif"], as_index=False)
        .agg(
            replay_rows=("blueprint_id", "count"),
            clean_rows=("decision", lambda s: int((s == "CORE56_REPLAY_CLEAN_CLUE").sum())),
            label_family_count=("label_family", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_recent_spread=("recent_oos_2026JanApr_spread", "max"),
        )
        .sort_values(["clean_rows", "max_recent_spread"], ascending=[False, False])
        if not replay.empty
        else pd.DataFrame()
    )
    candidate_summary.to_csv(RUNTIME / "a7ffcore56_candidate_summary.csv", index=False)
    label_summary = (
        replay.groupby(["label_family", "label_horizon_h", "decision"], as_index=False)
        .size()
        .rename(columns={"size": "row_count"})
        .sort_values("row_count", ascending=False)
        if not replay.empty
        else pd.DataFrame()
    )
    semantic_summary = (
        clean.groupby(["semantic_pair", "label_family"], as_index=False)
        .size()
        .rename(columns={"size": "clean_row_count"})
        .sort_values("clean_row_count", ascending=False)
        if not clean.empty
        else pd.DataFrame()
    )
    split_obs_cols = [f"{split}_obs" for split in ["train_2024", *PREMAY_SPLITS]]
    split_obs_summary = (
        replay[split_obs_cols]
        .agg(["min", "median", "max", lambda s: int((s > 0).sum())])
        .rename(index={"<lambda>": "positive_row_count"})
        .reset_index(names="metric")
        if not replay.empty
        else pd.DataFrame()
    )
    label_summary.to_csv(RUNTIME / "a7ffcore56_label_decision_summary.csv", index=False)
    semantic_summary.to_csv(RUNTIME / "a7ffcore56_clean_semantic_summary.csv", index=False)
    split_obs_summary.to_csv(RUNTIME / "a7ffcore56_split_obs_summary.csv", index=False)

    clean_candidate_count = int(clean["blueprint_id"].nunique()) if not clean.empty else 0
    clean_semantic_count = int(clean["semantic_pair"].nunique()) if not clean.empty else 0
    clean_label_count = int(clean["label_family"].nunique()) if not clean.empty else 0
    top_semantic_share = float(clean["semantic_pair"].value_counts(normalize=True).iloc[0]) if not clean.empty else 0.0
    blockers = []
    if len(failures_df):
        blockers.append("eval_failures")
    if clean_candidate_count < 12:
        blockers.append("clean_candidate_count_lt_12")
    if clean_semantic_count < 4:
        blockers.append("clean_semantic_pair_count_lt_4")
    if clean_label_count < 2:
        blockers.append("clean_label_family_count_lt_2")
    if top_semantic_share > 0.40:
        blockers.append("top_semantic_pair_share_gt_40pct")
    decision = "PASS_A7FFCORE56_BOUNDED_REPLAY_PREFLIGHT_CLEAN_PACKET_READY" if not blockers else "HOLD_A7FFCORE56_BOUNDED_REPLAY_PREFLIGHT"
    manifest = {
        "stage": "A7FF-CORE56",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE55",
        "source_decision": source.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "packet_count": int(len(packet)),
        "frame_rows": int(len(replay_frame)),
        "frame_symbols": int(replay_frame["symbol"].nunique()),
        "timestamp_count": int(n_ts),
        "label_matrix_count": int(len(labels)),
        "eval_failure_count": int(len(failures_df)),
        "replay_metric_rows": int(len(replay)),
        "clean_replay_rows": int(len(clean)),
        "clean_candidate_count": clean_candidate_count,
        "clean_semantic_pair_count": clean_semantic_count,
        "clean_label_family_count": clean_label_count,
        "clean_top_semantic_pair_share": top_semantic_share,
        "executes_replay": True,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core57_replay_arbitration": decision.startswith("PASS_"),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore56_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ffcore56_authorization_matrix.json",
        {
            "authorized": {"A7FF-CORE57 replay arbitration": decision.startswith("PASS_")},
            "not_authorized": {"large_search": True, "alpha_proof": True, "shadow_paper_live": True},
        },
    )
    report = [
        "# CRYPTO A7FF-CORE56 BOUNDED REPLAY PREFLIGHT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE56 runs bounded replay over the CORE55 replay-ready packet. It uses full panel labels, decile spread, stale/time/symbol/sign controls, and split checks. It is not search or alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Decision Summary",
        "",
        md_table(label_summary, 80),
        "",
        "## Split Observation Summary",
        "",
        md_table(split_obs_summary, 80),
        "",
        "## Clean Semantic Summary",
        "",
        md_table(semantic_summary, 80),
        "",
        "## Candidate Summary",
        "",
        md_table(candidate_summary.head(80), 80),
        "",
        "## Boundary",
        "",
        "```text",
        "replay executed: true",
        "search executed: false",
        "May used: false",
        "large search / alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
