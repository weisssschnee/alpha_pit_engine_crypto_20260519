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
    summarize_spread,
)
from scripts.crypto_a7ffcore16e_sharded_primitive_operator_atlas import LABELS, transform_signal  # noqa: E402
from scripts.crypto_a7ffcore16ge_family_native_interaction_probe import combine_signal, load_fields  # noqa: E402
from scripts.crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import shift_matrix  # noqa: E402
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import spread_series  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore16he_second_pass_interaction_breadth"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16HE_SECOND_PASS_INTERACTION_BREADTH_20260601.md"
CORE16H = REPO / "runtime" / "a7ffcore16h_second_pass_interaction_contract" / "a7ffcore16h_manifest.json"
A7AA0_FIELDS = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_candidate_primitive_fields.csv"

LABEL_HORIZONS = [1, 4, 8, 24]


SECOND_PASS_SPECS: dict[str, dict[str, Any]] = {
    "H0_I3_deconcentration": {
        "left_families": ["positioning"],
        "right_families": ["price_return", "basis_premium"],
        "left_transforms": ["spread_short_long", "zscore_168h"],
        "right_transforms": ["delta_24h", "shock_24h", "zscore_72h"],
        "operators": ["Sub", "Mul", "SafeDiv"],
    },
    "H1_I5_deconcentration": {
        "left_families": ["liquidity"],
        "right_families": ["basis_premium", "positioning"],
        "left_transforms": ["zscore_168h", "tsrank_168h", "shock_24h"],
        "right_transforms": ["delta_24h", "zscore_168h", "spread_short_long"],
        "operators": ["Mul", "SafeDiv", "Sub"],
    },
    "H2_I4_near_miss_repair": {
        "left_families": ["taker_flow"],
        "right_families": ["open_interest", "liquidity"],
        "left_transforms": ["delta_1h", "delta_4h", "shock_24h", "tsrank_72h"],
        "right_transforms": ["level", "delta_4h", "delta_24h", "zscore_168h", "tsrank_168h"],
        "operators": ["Mul", "SafeDiv"],
    },
    "H3_cross_family_bridge": {
        "left_families": ["positioning", "liquidity", "taker_flow"],
        "right_families": ["open_interest", "basis_premium", "price_return"],
        "left_transforms": ["zscore_168h", "spread_short_long"],
        "right_transforms": ["delta_24h", "zscore_168h"],
        "operators": ["Mul", "SafeDiv"],
    },
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


def build_blueprints(second_pass_family: str) -> pd.DataFrame:
    if second_pass_family not in SECOND_PASS_SPECS:
        raise SystemExit(f"unknown second-pass family: {second_pass_family}")
    spec = SECOND_PASS_SPECS[second_pass_family]
    fields = pd.read_csv(A7AA0_FIELDS)
    left_fields = fields[fields["field_family"].astype(str).isin(spec["left_families"])].copy()
    right_fields = fields[fields["field_family"].astype(str).isin(spec["right_families"])].copy()
    rows: list[dict[str, Any]] = []
    for left in left_fields.to_dict("records"):
        for right in right_fields.to_dict("records"):
            if left["field_name"] == right["field_name"]:
                continue
            for left_transform in spec["left_transforms"]:
                for right_transform in spec["right_transforms"]:
                    for operator in spec["operators"]:
                        rows.append(
                            {
                                "second_pass_family": second_pass_family,
                                "left_field": left["field_name"],
                                "left_family": left["field_family"],
                                "right_field": right["field_name"],
                                "right_family": right["field_family"],
                                "left_transform": left_transform,
                                "right_transform": right_transform,
                                "operator": operator,
                                "blueprint_id": (
                                    f"core16he_{second_pass_family}_{left['field_name']}_{left_transform}_"
                                    f"{operator}_{right['field_name']}_{right_transform}"
                                ),
                            }
                        )
    return pd.DataFrame(rows)


def evaluate_second_pass_family(second_pass_family: str, chunk_index: int | None = None, chunk_count: int | None = None) -> dict[str, Any]:
    core16h = read_json(CORE16H)
    if core16h.get("decision") != "PASS_A7FFCORE16H_SECOND_PASS_INTERACTION_CONTRACT_READY_FOR_CORE16HE":
        raise SystemExit(f"CORE16H is not ready: {core16h.get('decision')}")
    blueprints = build_blueprints(second_pass_family)
    if chunk_index is not None or chunk_count is not None:
        if chunk_index is None or chunk_count is None or chunk_count <= 0 or chunk_index < 0 or chunk_index >= chunk_count:
            raise SystemExit("--chunk-index must be in [0, --chunk-count)")
        blueprints = blueprints.iloc[[i for i in range(len(blueprints)) if i % chunk_count == chunk_index]].copy()
        shard_dir = RUNTIME / f"second_pass_family={second_pass_family}__chunk={chunk_index}-of-{chunk_count}"
    else:
        shard_dir = RUNTIME / f"second_pass_family={second_pass_family}"
    shard_dir.mkdir(parents=True, exist_ok=True)
    field_names = set(blueprints["left_field"].astype(str)) | set(blueprints["right_field"].astype(str))
    loaded_symbols, timestamps, numeric, groups, missing, full_timestamp_count = load_fields(field_names)
    if missing:
        blueprints = blueprints[
            ~blueprints["left_field"].astype(str).isin(missing)
            & ~blueprints["right_field"].astype(str).isin(missing)
        ].copy()
    split = split_for_timestamps(timestamps)
    raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in LABEL_HORIZONS}
    vol = numeric.get("realized_vol_168h", np.full_like(numeric["trade_close"], np.nan))
    liquidity_tier = groups["liquidity_tier"]
    rng = np.random.default_rng(abs(hash(second_pass_family)) % (2**32))
    cache: dict[tuple[str, str], np.ndarray] = {}

    def transformed(field: str, transform: str) -> np.ndarray:
        key = (field, transform)
        if key not in cache:
            cache[key] = transform_signal(numeric[field], transform)
        return cache[key]

    rows: list[dict[str, Any]] = []
    for bp in blueprints.to_dict("records"):
        try:
            left = transformed(str(bp["left_field"]), str(bp["left_transform"]))
            right = transformed(str(bp["right_field"]), str(bp["right_transform"]))
            signal = combine_signal(left, right, str(bp["operator"]))
        except Exception as exc:  # noqa: BLE001
            rows.append({**bp, "decision": "HOLD_A7FFCORE16HE_MATERIALIZATION_ERROR", "error": repr(exc)})
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
                    decision = "A7FFCORE16HE_SECOND_PASS_CANDIDATE_LAG_OK"
                elif candidate:
                    decision = "A7FFCORE16HE_SECOND_PASS_CANDIDATE_LAG_FRAGILE"
                elif near_miss:
                    decision = "A7FFCORE16HE_NEAR_MISS_CONTROL_MARGIN"
                elif pre_may_all:
                    decision = "HOLD_A7FFCORE16HE_CONTROL_LIKE"
                else:
                    decision = "HOLD_A7FFCORE16HE_PREMAY_UNSTABLE"
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
                        "second_pass_candidate": candidate,
                        "near_miss": near_miss,
                        "decision": decision,
                        **summary,
                        "avg_n_obs_recent": float(np.nanmean(valid_counts[(split == "recent_oos_2026JanApr")])) if np.any(split == "recent_oos_2026JanApr") else np.nan,
                        "error": "",
                    }
                )
    response = pd.DataFrame(rows)
    candidates = response[response.get("second_pass_candidate", pd.Series(dtype=bool)).astype(str).str.lower().eq("true")].copy()
    blueprints.to_csv(shard_dir / "a7ffcore16he_blueprint_queue.csv", index=False)
    response.to_csv(shard_dir / "a7ffcore16he_response_map.csv", index=False)
    candidates.to_csv(shard_dir / "a7ffcore16he_second_pass_candidates.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE16HE-FAMILY",
        "generated_at": now_utc(),
        "second_pass_family": second_pass_family,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": full_timestamp_count,
        "blueprint_count": int(len(blueprints)),
        "response_rows": int(len(response)),
        "second_pass_candidate_count": int(len(candidates)),
        "near_miss_count": int((response.get("near_miss", pd.Series(dtype=bool)).astype(str).str.lower() == "true").sum()) if not response.empty else 0,
        "missing_fields_excluded": missing,
        "decision": "PASS_A7FFCORE16HE_FAMILY_SHARD_COMPLETE",
    }
    write_json(shard_dir / "a7ffcore16he_family_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def summarize() -> dict[str, Any]:
    family_dirs = [p for p in RUNTIME.glob("second_pass_family=*") if p.is_dir()]
    responses = []
    blueprints = []
    candidates = []
    manifests = []
    for directory in family_dirs:
        manifest = read_json(directory / "a7ffcore16he_family_manifest.json")
        if manifest:
            manifests.append(manifest)
        resp = directory / "a7ffcore16he_response_map.csv"
        bp = directory / "a7ffcore16he_blueprint_queue.csv"
        cand = directory / "a7ffcore16he_second_pass_candidates.csv"
        if resp.exists():
            responses.append(pd.read_csv(resp))
        if bp.exists():
            blueprints.append(pd.read_csv(bp))
        if cand.exists():
            candidates.append(pd.read_csv(cand))
    response = pd.concat(responses, ignore_index=True) if responses else pd.DataFrame()
    blueprint_df = pd.concat(blueprints, ignore_index=True) if blueprints else pd.DataFrame()
    candidate_df = pd.concat(candidates, ignore_index=True) if candidates else pd.DataFrame()
    family_summary = (
        response.groupby("second_pass_family", dropna=False)
        .agg(
            response_rows=("blueprint_id", "size"),
            blueprint_count=("blueprint_id", "nunique"),
            candidate_count=("second_pass_candidate", "sum"),
            near_miss_count=("near_miss", "sum"),
            label_family_count=("label_family", "nunique"),
            operator_count=("operator", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values(["candidate_count", "near_miss_count"], ascending=[False, False])
        if not response.empty
        else pd.DataFrame()
    )
    decision_counts = response["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not response.empty else pd.DataFrame()
    candidate_count = int(len(candidate_df))
    family_count = int(candidate_df["second_pass_family"].nunique()) if not candidate_df.empty else 0
    top_share = float(candidate_df["second_pass_family"].value_counts(normalize=True).max()) if not candidate_df.empty else 0.0
    operator_count = int(candidate_df["operator"].nunique()) if not candidate_df.empty else 0
    non_l5_share = float((candidate_df["label_family"].astype(str) != "L5_vol_adjusted_return").mean()) if not candidate_df.empty else 0.0
    i4_like = int(candidate_df[candidate_df["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].shape[0]) if not candidate_df.empty else 0
    blockers: list[str] = []
    if candidate_count < 96:
        blockers.append("candidate_count_lt_96")
    if family_count < 3:
        blockers.append("interaction_family_count_lt_3")
    if candidate_count and top_share > 0.45:
        blockers.append("top_family_share_gt_45pct")
    if operator_count < 2:
        blockers.append("operator_count_lt_2")
    if candidate_count and non_l5_share < 0.40:
        blockers.append("non_l5_label_share_lt_40pct")
    if i4_like < 12:
        blockers.append("i4_floor_lt_12")
    if blockers:
        decision = "HOLD_A7FFCORE16HE_SECOND_PASS_BREADTH_INSUFFICIENT"
        next_allowed = "A7FF-CORE16HER second-pass interaction forensic"
        authorizes_core17 = False
    else:
        decision = "PASS_A7FFCORE16HE_SECOND_PASS_BREADTH_READY_FOR_CORE17_CONTRACT"
        next_allowed = "A7FF-CORE17 objective seed policy contract"
        authorizes_core17 = True
    response.to_csv(RUNTIME / "a7ffcore16he_response_map.csv", index=False)
    blueprint_df.to_csv(RUNTIME / "a7ffcore16he_blueprint_queue.csv", index=False)
    candidate_df.to_csv(RUNTIME / "a7ffcore16he_second_pass_candidates.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore16he_family_summary.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7ffcore16he_decision_counts.csv", index=False)
    pd.DataFrame(manifests).to_csv(RUNTIME / "a7ffcore16he_shard_manifest_summary.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE16HE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16H",
        "source_decision": read_json(CORE16H).get("decision"),
        "decision": decision,
        "blockers": blockers,
        "completed_second_pass_shards": len(manifests),
        "blueprint_count": int(len(blueprint_df)),
        "response_rows": int(len(response)),
        "second_pass_candidate_count": candidate_count,
        "second_pass_family_count": family_count,
        "top_second_pass_family_share": top_share,
        "operator_count": operator_count,
        "non_l5_label_share": non_l5_share,
        "i4_repair_candidate_count": i4_like,
        "authorizes_core17": authorizes_core17,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": next_allowed,
    }
    write_json(RUNTIME / "a7ffcore16he_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16HE SECOND-PASS INTERACTION BREADTH",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16HE executes the second-pass typed interaction breadth repair authorized by CORE16H. It does not execute open grammar formula generation, bounded replay, search, promotion, alpha proof, shadow, paper, or live.",
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
        "## Second-Pass Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Candidate Sample",
        "",
        md_table(candidate_df.head(80)),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--second-pass-family")
    parser.add_argument("--chunk-index", type=int)
    parser.add_argument("--chunk-count", type=int)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    if args.summary:
        summarize()
    elif args.second_pass_family:
        evaluate_second_pass_family(args.second_pass_family, args.chunk_index, args.chunk_count)
    else:
        raise SystemExit("pass --second-pass-family NAME or --summary")


if __name__ == "__main__":
    main()
