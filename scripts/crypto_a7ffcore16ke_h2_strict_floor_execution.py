from __future__ import annotations

import argparse
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
from scripts.crypto_a7ffcore16e_sharded_primitive_operator_atlas import LABELS, rolling_tsrank  # noqa: E402
from scripts.crypto_a7ffcore16ge_family_native_interaction_probe import combine_signal, load_fields  # noqa: E402
from scripts.crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import rolling_mean, shift_matrix  # noqa: E402
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import spread_series  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore16ke_h2_strict_floor_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16KE_H2_STRICT_FLOOR_EXECUTION_20260601.md"
CORE16K = REPO / "runtime" / "a7ffcore16k_h2_strict_floor_repair_contract" / "a7ffcore16k_manifest.json"
STRICT_QUEUE = REPO / "runtime" / "a7ffcore16j_nearmiss_resolution_audit" / "a7ffcore16j_strict_preseed_queue.csv"
H2_NEAR = REPO / "runtime" / "a7ffcore16k_h2_strict_floor_repair_contract" / "a7ffcore16k_source_h2_excluded_nearmiss_rows.csv"

LABEL_HORIZONS = [1, 4, 8, 24]
TRANSFORMS = [
    "delta_2h",
    "delta_4h",
    "delta_8h",
    "zscore_72h",
    "shock_24h",
]
OPERATORS = ["Mul", "SafeDiv", "Sub"]


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


def finalize_from_response(core16k: dict[str, Any], strict_queue: pd.DataFrame, response: pd.DataFrame, blueprint_df: pd.DataFrame, manifests: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = response[response.get("h2_repair_candidate", pd.Series(dtype=bool)).astype(str).str.lower().eq("true")].copy() if not response.empty else pd.DataFrame()
    if not candidates.empty:
        candidates["control_ratio_premay_max"] = pd.to_numeric(candidates["control_ratio_premay_max"], errors="coerce")
        candidates["lag_bonus"] = candidates["lag_ok"].astype(str).str.lower().eq("true").astype(int)
        candidates["non_l5_bonus"] = candidates["label_family"].astype(str).ne("L5_vol_adjusted_return").astype(int)
        candidates["selection_score"] = candidates["lag_bonus"] * 10 + candidates["non_l5_bonus"] * 5 - candidates["control_ratio_premay_max"].fillna(9)
        add = candidates.sort_values(["selection_score", "control_ratio_premay_max"], ascending=[False, True]).head(max(0, int(core16k.get("additional_h2_needed", 3)))).copy()
    else:
        add = pd.DataFrame()
    if not add.empty:
        add["queue_role"] = "strict_candidate"
    repaired_queue = pd.concat([strict_queue, add], ignore_index=True)
    repaired_queue = repaired_queue.drop_duplicates(subset=["blueprint_id", "label_family", "label_horizon_h"], keep="first")
    h2_count = int(repaired_queue[repaired_queue["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].shape[0])
    queue_size = int(repaired_queue.shape[0])
    added_count = int(add.shape[0])
    queue_pass = queue_size >= 96 and h2_count >= 12 and added_count >= int(core16k.get("additional_h2_needed", 3))
    decision = "PASS_A7FFCORE16KE_H2_STRICT_FLOOR_REPAIRED_READY_FOR_CORE16L" if queue_pass else "HOLD_A7FFCORE16KE_H2_STRICT_FLOOR_REPAIR_INSUFFICIENT"
    decision_counts = response["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not response.empty else pd.DataFrame()
    response.to_csv(RUNTIME / "a7ffcore16ke_h2_repair_response_map.csv", index=False)
    candidates.to_csv(RUNTIME / "a7ffcore16ke_h2_repair_candidates.csv", index=False)
    add.to_csv(RUNTIME / "a7ffcore16ke_h2_added_strict_rows.csv", index=False)
    repaired_queue.to_csv(RUNTIME / "a7ffcore16ke_repaired_strict_preseed_queue.csv", index=False)
    blueprint_df.to_csv(RUNTIME / "a7ffcore16ke_blueprint_queue.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7ffcore16ke_decision_counts.csv", index=False)
    pd.DataFrame(manifests).to_csv(RUNTIME / "a7ffcore16ke_chunk_manifest_summary.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE16KE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16K",
        "source_decision": core16k.get("decision"),
        "decision": decision,
        "chunk_count_completed": len(manifests),
        "blueprint_count": int(len(blueprint_df)),
        "response_rows": int(len(response)),
        "h2_repair_candidate_count": int(len(candidates)),
        "added_strict_h2_count": added_count,
        "repaired_queue_size": queue_size,
        "repaired_queue_h2_count": h2_count,
        "authorizes_core16l": queue_pass,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16L strict pre-seed queue lock audit" if queue_pass else "A7FF-CORE16KR H2 repair forensic",
    }
    write_json(RUNTIME / "a7ffcore16ke_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16KE H2 STRICT-FLOOR EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16KE executes a narrow H2/I4 strict-floor repair around the excluded near-miss field pair only. It does not execute open grammar formula generation, replay, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Decision Counts",
        "",
        md_table(decision_counts),
        "",
        "## Added Strict H2 Rows",
        "",
        md_table(add),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def summarize_from_chunks() -> dict[str, Any]:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core16k = read_json(CORE16K)
    strict_queue = pd.read_csv(STRICT_QUEUE)
    chunk_dirs = [p for p in RUNTIME.glob("chunk=*-of-*") if p.is_dir()]
    responses = []
    blueprints = []
    manifests = []
    for directory in chunk_dirs:
        manifest = read_json(directory / "a7ffcore16ke_chunk_manifest.json")
        if manifest:
            manifests.append(manifest)
        resp = directory / "a7ffcore16ke_h2_repair_response_map.csv"
        bp = directory / "a7ffcore16ke_blueprint_queue.csv"
        if resp.exists():
            responses.append(pd.read_csv(resp))
        if bp.exists():
            blueprints.append(pd.read_csv(bp))
    response = pd.concat(responses, ignore_index=True) if responses else pd.DataFrame()
    blueprint_df = pd.concat(blueprints, ignore_index=True) if blueprints else pd.DataFrame()
    return finalize_from_response(core16k, strict_queue, response, blueprint_df, manifests)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-index", type=int)
    parser.add_argument("--chunk-count", type=int)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if args.summary:
        summarize_from_chunks()
        return
    core16k = read_json(CORE16K)
    if core16k.get("decision") != "PASS_A7FFCORE16K_H2_STRICT_FLOOR_REPAIR_CONTRACT_READY_FOR_CORE16KE":
        raise SystemExit(f"CORE16K is not ready for CORE16KE: {core16k.get('decision')}")
    strict_queue = pd.read_csv(STRICT_QUEUE)
    near = pd.read_csv(H2_NEAR)
    left_fields = near["left_field"].astype(str).unique().tolist()
    right_fields = near["right_field"].astype(str).unique().tolist()
    field_names = set(left_fields + right_fields)
    loaded_symbols, timestamps, numeric, groups, missing, full_timestamp_count = load_fields(field_names)
    if missing:
        raise SystemExit(f"missing repair fields: {missing}")
    split = split_for_timestamps(timestamps)
    raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in LABEL_HORIZONS}
    vol = numeric.get("realized_vol_168h", np.full_like(numeric["trade_close"], np.nan))
    liquidity_tier = groups["liquidity_tier"]
    rng = np.random.default_rng(16016)
    cache: dict[tuple[str, str], np.ndarray] = {}

    def get(field: str, tr: str) -> np.ndarray:
        key = (field, tr)
        if key not in cache:
            cache[key] = transform(numeric[field], tr)
        return cache[key]

    blueprints = []
    for left in left_fields:
        for right in right_fields:
            for left_transform in TRANSFORMS:
                for right_transform in TRANSFORMS:
                    for operator in OPERATORS:
                        blueprints.append(
                            {
                                "second_pass_family": "H2_I4_near_miss_repair",
                                "left_field": left,
                                "left_transform": left_transform,
                                "operator": operator,
                                "right_field": right,
                                "right_transform": right_transform,
                                "blueprint_id": f"core16ke_H2_{left}_{left_transform}_{operator}_{right}_{right_transform}",
                            }
                        )
    if args.chunk_index is not None or args.chunk_count is not None:
        if args.chunk_index is None or args.chunk_count is None or args.chunk_count <= 0 or args.chunk_index < 0 or args.chunk_index >= args.chunk_count:
            raise SystemExit("--chunk-index must be in [0, --chunk-count)")
        blueprints = [bp for idx, bp in enumerate(blueprints) if idx % args.chunk_count == args.chunk_index]
        shard_dir = RUNTIME / f"chunk={args.chunk_index}-of-{args.chunk_count}"
    else:
        shard_dir = None
    rows: list[dict[str, Any]] = []
    for bp in blueprints:
        try:
            signal = combine_signal(get(bp["left_field"], bp["left_transform"]), get(bp["right_field"], bp["right_transform"]), bp["operator"])
        except Exception as exc:  # noqa: BLE001
            rows.append({**bp, "decision": "HOLD_A7FFCORE16KE_MATERIALIZATION_ERROR", "error": repr(exc)})
            continue
        variants = {
            "wrong_lag_future_24h": shift_matrix(signal, -24),
            "wrong_lag_stale_168h": shift_matrix(signal, 168),
            "same_family_random": rng.normal(size=signal.shape),
            "one_bar_lag": shift_matrix(signal, 1),
        }
        for horizon, raw in raw_labels.items():
            for label_family in LABELS:
                label = label_family_matrix(raw, label_family, vol, liquidity_tier)
                spread, valid_counts = spread_series(signal, label)
                summary = summarize_spread(spread, split, horizon)
                train_mean = summary.get("train_2024_mean_spread", np.nan)
                orientation = 1.0 if not np.isfinite(train_mean) or train_mean >= 0 else -1.0
                oriented = {
                    split_name: orientation * float(summary.get(f"{split_name}_mean_spread", np.nan))
                    for split_name in ["train_2024", *PRE_MAY_SPLITS]
                }
                pre_may_count = int(sum(np.isfinite(oriented[s]) and oriented[s] > 0 for s in PRE_MAY_SPLITS))
                pre_may_all = pre_may_count == len(PRE_MAY_SPLITS)
                control_spreads = {}
                for name, variant_signal in variants.items():
                    if name == "one_bar_lag":
                        continue
                    ctrl_spread, _ = spread_series(variant_signal, label)
                    control_spreads[name] = ctrl_spread
                control_ratio = max_control_ratio(oriented, control_spreads, orientation, split)
                lag_spread, _ = spread_series(variants["one_bar_lag"], label)
                recent_lag_mask = (split == "recent_oos_2026JanApr") & np.isfinite(lag_spread)
                lag_recent = orientation * float(np.nanmean(lag_spread[recent_lag_mask])) if recent_lag_mask.any() else np.nan
                recent = oriented["recent_oos_2026JanApr"]
                lag_ok = np.isfinite(recent) and np.isfinite(lag_recent) and lag_recent > 0 and abs(lag_recent) >= 0.25 * abs(recent)
                candidate = pre_may_all and np.isfinite(control_ratio) and control_ratio < 1.0
                near_miss = (not candidate) and pre_may_all and np.isfinite(control_ratio) and control_ratio < 1.5
                if candidate and lag_ok:
                    decision = "A7FFCORE16KE_H2_REPAIR_CANDIDATE_LAG_OK"
                elif candidate:
                    decision = "A7FFCORE16KE_H2_REPAIR_CANDIDATE_LAG_FRAGILE"
                elif near_miss:
                    decision = "A7FFCORE16KE_NEAR_MISS_CONTROL_MARGIN"
                elif pre_may_all:
                    decision = "HOLD_A7FFCORE16KE_CONTROL_LIKE"
                else:
                    decision = "HOLD_A7FFCORE16KE_PREMAY_UNSTABLE"
                rows.append(
                    {
                        **bp,
                        "label_family": label_family,
                        "label_horizon_h": horizon,
                        "orientation_from_train": orientation,
                        "premay_positive_split_count": pre_may_count,
                        "premay_all_positive": pre_may_all,
                        "control_ratio_premay_max": control_ratio,
                        "one_bar_lag_recent_oriented": lag_recent,
                        "lag_ok": lag_ok,
                        "h2_repair_candidate": candidate,
                        "near_miss": near_miss,
                        "decision": decision,
                        **summary,
                        "avg_n_obs_recent": float(np.nanmean(valid_counts[(split == "recent_oos_2026JanApr")])) if np.any(split == "recent_oos_2026JanApr") else np.nan,
                        "error": "",
                    }
                )
    response = pd.DataFrame(rows)
    candidates = response[response.get("h2_repair_candidate", pd.Series(dtype=bool)).astype(str).str.lower().eq("true")].copy()
    if shard_dir is not None:
        shard_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(blueprints).to_csv(shard_dir / "a7ffcore16ke_blueprint_queue.csv", index=False)
        response.to_csv(shard_dir / "a7ffcore16ke_h2_repair_response_map.csv", index=False)
        candidates.to_csv(shard_dir / "a7ffcore16ke_h2_repair_candidates.csv", index=False)
        chunk_manifest = {
            "stage": "A7FF-CORE16KE-CHUNK",
            "generated_at": now_utc(),
            "chunk_index": args.chunk_index,
            "chunk_count": args.chunk_count,
            "blueprint_count": len(blueprints),
            "response_rows": int(len(response)),
            "h2_repair_candidate_count": int(len(candidates)),
            "decision": "PASS_A7FFCORE16KE_CHUNK_COMPLETE",
        }
        write_json(shard_dir / "a7ffcore16ke_chunk_manifest.json", chunk_manifest)
        print(json.dumps(chunk_manifest, indent=2, sort_keys=True))
        return
    candidates["control_ratio_premay_max"] = pd.to_numeric(candidates["control_ratio_premay_max"], errors="coerce")
    candidates["lag_bonus"] = candidates["lag_ok"].astype(str).str.lower().eq("true").astype(int)
    candidates["non_l5_bonus"] = candidates["label_family"].astype(str).ne("L5_vol_adjusted_return").astype(int)
    candidates["selection_score"] = candidates["lag_bonus"] * 10 + candidates["non_l5_bonus"] * 5 - candidates["control_ratio_premay_max"].fillna(9)
    add = candidates.sort_values(["selection_score", "control_ratio_premay_max"], ascending=[False, True]).head(max(0, int(core16k.get("additional_h2_needed", 3)))).copy()
    add["queue_role"] = "strict_candidate"
    repaired_queue = pd.concat([strict_queue, add], ignore_index=True)
    repaired_queue = repaired_queue.drop_duplicates(subset=["blueprint_id", "label_family", "label_horizon_h"], keep="first")
    h2_count = int(repaired_queue[repaired_queue["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].shape[0])
    queue_size = int(repaired_queue.shape[0])
    queue_pass = queue_size >= 96 and h2_count >= 12 and int(add.shape[0]) >= int(core16k.get("additional_h2_needed", 3))
    decision = "PASS_A7FFCORE16KE_H2_STRICT_FLOOR_REPAIRED_READY_FOR_CORE16L" if queue_pass else "HOLD_A7FFCORE16KE_H2_STRICT_FLOOR_REPAIR_INSUFFICIENT"
    response.to_csv(RUNTIME / "a7ffcore16ke_h2_repair_response_map.csv", index=False)
    candidates.to_csv(RUNTIME / "a7ffcore16ke_h2_repair_candidates.csv", index=False)
    add.to_csv(RUNTIME / "a7ffcore16ke_h2_added_strict_rows.csv", index=False)
    repaired_queue.to_csv(RUNTIME / "a7ffcore16ke_repaired_strict_preseed_queue.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE16KE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16K",
        "source_decision": core16k.get("decision"),
        "decision": decision,
        "blueprint_count": len(blueprints),
        "response_rows": int(len(response)),
        "h2_repair_candidate_count": int(len(candidates)),
        "added_strict_h2_count": int(add.shape[0]),
        "repaired_queue_size": queue_size,
        "repaired_queue_h2_count": h2_count,
        "authorizes_core16l": queue_pass,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16L strict pre-seed queue lock audit" if queue_pass else "A7FF-CORE16KR H2 repair forensic",
    }
    write_json(RUNTIME / "a7ffcore16ke_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16KE H2 STRICT-FLOOR EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16KE executes a narrow H2/I4 strict-floor repair around the excluded near-miss field pair only. It does not execute open grammar formula generation, replay, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Added Strict H2 Rows",
        "",
        md_table(add),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
