from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7aa1_primitive_response_map import (  # noqa: E402
    PRE_MAY_SPLITS,
    horizon_label,
    label_family_matrix,
    max_control_ratio,
    rolling_zscore,
    summarize_spread,
)
from scripts.crypto_a7ffcore16e_sharded_primitive_operator_atlas import rolling_tsrank  # noqa: E402
from scripts.crypto_a7ffcore16ge_family_native_interaction_probe import combine_signal, load_fields  # noqa: E402
from scripts.crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import rolling_mean, shift_matrix  # noqa: E402
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import spread_series  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE19E_BOUNDED_REPLAY_EXECUTION_20260601.md"
CORE19 = REPO / "runtime" / "a7ffcore19_bounded_replay_contract" / "a7ffcore19_manifest.json"
PACKET = REPO / "runtime" / "a7ffcore17e_objective_seed_packet_construction" / "a7ffcore17e_objective_seed_packet.csv"

COST_BPS = [2, 5, 10, 20]


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


def transform(values: np.ndarray, name: str) -> np.ndarray:
    if name == "level":
        return values.astype(np.float64, copy=True)
    if name.startswith("delta_") and name.endswith("h"):
        hours = int(name.removeprefix("delta_").removesuffix("h"))
        return values - shift_matrix(values, hours)
    if name == "zscore_72h":
        return rolling_zscore(values, 72)
    if name == "zscore_168h":
        return rolling_zscore(values, 168)
    if name == "tsrank_72h":
        return rolling_tsrank(values, 72)
    if name == "tsrank_168h":
        return rolling_tsrank(values, 168)
    if name == "shock_24h":
        delta = values - shift_matrix(values, 24)
        scale = rolling_mean(np.abs(delta), 168)
        out = delta / np.where(np.isfinite(scale) & (scale > 1e-12), scale, np.nan)
        out[~np.isfinite(out)] = np.nan
        return out
    if name == "spread_short_long":
        return rolling_mean(values, 24) - rolling_mean(values, 168)
    raise ValueError(name)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core19 = read_json(CORE19)
    if core19.get("decision") != "PASS_A7FFCORE19_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE19E":
        raise SystemExit(f"CORE19 is not ready for CORE19E: {core19.get('decision')}")
    packet = pd.read_csv(PACKET)
    field_names = set(packet["left_field"].astype(str)) | set(packet["right_field"].astype(str))
    loaded_symbols, timestamps, numeric, groups, missing, full_timestamp_count = load_fields(field_names)
    if missing:
        raise SystemExit(f"missing packet fields: {missing}")
    split = split_for_timestamps(timestamps)
    horizons = sorted(pd.to_numeric(packet["label_horizon_h"], errors="coerce").dropna().astype(int).unique().tolist())
    raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in horizons}
    vol = numeric.get("realized_vol_168h", np.full_like(numeric["trade_close"], np.nan))
    liquidity_tier = groups["liquidity_tier"]
    rng = np.random.default_rng(19019)
    cache: dict[tuple[str, str], np.ndarray] = {}

    def get(field: str, tr: str) -> np.ndarray:
        key = (field, tr)
        if key not in cache:
            cache[key] = transform(numeric[field], tr)
        return cache[key]

    rows: list[dict[str, Any]] = []
    eval_errors: list[dict[str, Any]] = []
    for cand in packet.to_dict("records"):
        candidate_id = str(cand["blueprint_id"]) + "|" + str(cand["label_family"]) + "|" + str(cand["label_horizon_h"])
        try:
            signal = combine_signal(get(str(cand["left_field"]), str(cand["left_transform"])), get(str(cand["right_field"]), str(cand["right_transform"])), str(cand["operator"]))
        except Exception as exc:  # noqa: BLE001
            eval_errors.append({"candidate_id": candidate_id, "error": repr(exc)})
            continue
        horizon = int(cand["label_horizon_h"])
        label_family = str(cand["label_family"])
        label = label_family_matrix(raw_labels[horizon], label_family, vol, liquidity_tier)
        orientation = float(cand.get("orientation_from_train", 1.0))
        signal = signal * orientation
        spread, valid_counts = spread_series(signal, label)
        summary = summarize_spread(spread, split, horizon)
        variants = {
            "wrong_lag_future_24h": shift_matrix(signal, -24),
            "wrong_lag_stale_168h": shift_matrix(signal, 168),
            "same_family_random": rng.normal(size=signal.shape),
            "one_bar_lag": shift_matrix(signal, 1),
        }
        control_spreads = {}
        for name, variant_signal in variants.items():
            if name == "one_bar_lag":
                continue
            ctrl_spread, _ = spread_series(variant_signal, label)
            control_spreads[name] = ctrl_spread
        oriented = {
            split_name: float(summary.get(f"{split_name}_mean_spread", np.nan))
            for split_name in ["train_2024", *PRE_MAY_SPLITS]
        }
        control_ratio = max_control_ratio(oriented, control_spreads, 1.0, split)
        lag_spread, _ = spread_series(variants["one_bar_lag"], label)
        lag_summary = summarize_spread(lag_spread, split, horizon)
        for split_name in ["train_2024", *PRE_MAY_SPLITS]:
            split_spread = float(summary.get(f"{split_name}_mean_spread", np.nan))
            split_tstat = float(summary.get(f"{split_name}_tstat", np.nan))
            lag_mean = float(lag_summary.get(f"{split_name}_mean_spread", np.nan))
            for cost in COST_BPS:
                cost_adjusted = split_spread - (2.0 * cost / 10000.0) if np.isfinite(split_spread) else np.nan
                rows.append(
                    {
                        "candidate_id": candidate_id,
                        "blueprint_id": cand["blueprint_id"],
                        "seed_lane": cand["seed_lane"],
                        "second_pass_family": cand["second_pass_family"],
                        "left_field": cand["left_field"],
                        "left_transform": cand["left_transform"],
                        "operator": cand["operator"],
                        "right_field": cand["right_field"],
                        "right_transform": cand["right_transform"],
                        "label_family": label_family,
                        "label_horizon_h": horizon,
                        "split": split_name,
                        "cost_bps": cost,
                        "spread": split_spread,
                        "cost_adjusted_spread": cost_adjusted,
                        "tstat": split_tstat,
                        "one_bar_lag_spread": lag_mean,
                        "control_ratio_premay_max": control_ratio,
                        "avg_n_obs_recent": float(np.nanmean(valid_counts[(split == "recent_oos_2026JanApr")])) if np.any(split == "recent_oos_2026JanApr") else np.nan,
                        "status": "ok",
                    }
                )
    result = pd.DataFrame(rows)
    errors = pd.DataFrame(eval_errors)
    clean_base = result[
        result["split"].isin(PRE_MAY_SPLITS)
        & result["cost_bps"].eq(5)
        & pd.to_numeric(result["cost_adjusted_spread"], errors="coerce").gt(0)
        & pd.to_numeric(result["control_ratio_premay_max"], errors="coerce").lt(1.0)
        & pd.to_numeric(result["one_bar_lag_spread"], errors="coerce").gt(0)
    ].copy()
    clean_counts = clean_base.groupby("candidate_id")["split"].nunique()
    clean_candidates = set(clean_counts[clean_counts >= len(PRE_MAY_SPLITS)].index.astype(str))
    candidate_summary = (
        result.groupby(["candidate_id", "seed_lane", "second_pass_family", "label_family", "label_horizon_h"], dropna=False)
        .agg(
            replay_rows=("candidate_id", "size"),
            median_cost_adjusted_spread=("cost_adjusted_spread", "median"),
            min_cost_adjusted_spread=("cost_adjusted_spread", "min"),
            max_tstat=("tstat", "max"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            min_one_bar_lag_spread=("one_bar_lag_spread", "min"),
        )
        .reset_index()
        if not result.empty
        else pd.DataFrame()
    )
    if not candidate_summary.empty:
        clean_split_df = clean_counts.rename("clean_premay_split_count").reset_index()
        candidate_summary = candidate_summary.merge(clean_split_df, on="candidate_id", how="left")
        candidate_summary["clean_premay_split_count"] = candidate_summary["clean_premay_split_count"].fillna(0).astype(int)
        candidate_summary["replay_clean"] = candidate_summary["candidate_id"].astype(str).isin(clean_candidates)
        candidate_summary = candidate_summary.sort_values(["replay_clean", "max_tstat"], ascending=[False, False])
    family_summary = (
        candidate_summary.groupby(["seed_lane", "second_pass_family"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "nunique"),
            replay_clean_candidate_count=("replay_clean", "sum"),
            label_family_count=("label_family", "nunique"),
            median_control_ratio=("median_control_ratio", "median"),
        )
        .reset_index()
        .sort_values(["replay_clean_candidate_count", "candidate_count"], ascending=[False, False])
        if not candidate_summary.empty
        else pd.DataFrame()
    )
    clean_frame = candidate_summary[candidate_summary["replay_clean"]].copy() if not candidate_summary.empty else pd.DataFrame()
    clean_count = int(clean_frame["candidate_id"].nunique()) if not clean_frame.empty else 0
    clean_lane_count = int(clean_frame["seed_lane"].nunique()) if not clean_frame.empty else 0
    clean_non_l5_share = float(clean_frame["label_family"].astype(str).ne("L5_vol_adjusted_return").mean()) if not clean_frame.empty else 0.0
    blockers: list[str] = []
    if eval_errors:
        blockers.append("eval_errors_nonzero")
    if clean_count < 12:
        blockers.append("replay_clean_candidate_count_lt_12")
    if clean_lane_count < 3:
        blockers.append("replay_clean_seed_lane_count_lt_3")
    if clean_count and clean_non_l5_share < 0.50:
        blockers.append("replay_clean_non_l5_share_lt_50pct")
    decision = "PASS_A7FFCORE19E_BOUNDED_REPLAY_CLEAN_PACKET_READY_FOR_CORE20" if not blockers else "HOLD_A7FFCORE19E_BOUNDED_REPLAY_INSUFFICIENT"
    result.to_csv(RUNTIME / "a7ffcore19e_replay_rows.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore19e_candidate_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore19e_family_summary.csv", index=False)
    clean_frame.to_csv(RUNTIME / "a7ffcore19e_replay_clean_candidates.csv", index=False)
    errors.to_csv(RUNTIME / "a7ffcore19e_eval_errors.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE19E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE19",
        "source_decision": core19.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "candidate_count": int(packet.shape[0]),
        "eval_error_count": int(len(eval_errors)),
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": full_timestamp_count,
        "replay_rows": int(result.shape[0]),
        "replay_clean_candidate_count": clean_count,
        "replay_clean_seed_lane_count": clean_lane_count,
        "replay_clean_non_l5_share": clean_non_l5_share,
        "clean_rule": "validation/test/recent all positive at 5bps, control_ratio < 1.0, one_bar_lag positive",
        "executes_replay": True,
        "executes_search": False,
        "authorizes_core20_contract": decision.startswith("PASS_"),
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE20 replay-clean consolidation / search-readiness contract" if decision.startswith("PASS_") else "A7FF-CORE19R bounded replay forensic",
    }
    write_json(RUNTIME / "a7ffcore19e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE19E BOUNDED REPLAY EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE19E executes bounded replay over the locked 96-row packet. It does not execute formula generation, search expansion, large search, alpha proof, shadow, paper, or live.",
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
        "## Replay Clean Candidates",
        "",
        md_table(clean_frame, max_rows=80),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
