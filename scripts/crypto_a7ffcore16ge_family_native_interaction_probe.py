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
from scripts.crypto_a7ffcore16e_sharded_primitive_operator_atlas import (  # noqa: E402
    LABELS,
    transform_signal,
)
from scripts.crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    load_base,
    load_group_fields,
    load_latent_numeric,
    parquet_schema,
    shift_matrix,
)
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import smoke_column_indices, spread_series  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore16ge_family_native_interaction_probe"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16GE_FAMILY_NATIVE_INTERACTION_PROBE_20260601.md"
CORE16G = REPO / "runtime" / "a7ffcore16g_family_native_interaction_contract" / "a7ffcore16g_manifest.json"
INTERACTION_CONTRACT = REPO / "runtime" / "a7ffcore16g_family_native_interaction_contract" / "a7ffcore16g_interaction_family_contract.csv"
A7AA0_FIELDS = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_candidate_primitive_fields.csv"

LABEL_HORIZONS = [1, 4, 8, 24]
OPERATORS = ["Mul", "Sub", "SafeDiv"]


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


def parse_list(value: Any) -> list[str]:
    return [part.strip() for part in str(value).split(";") if part.strip()]


def combine_signal(left: np.ndarray, right: np.ndarray, operator: str) -> np.ndarray:
    if operator == "Mul":
        out = left * right
    elif operator == "Sub":
        out = left - right
    elif operator == "SafeDiv":
        denom = np.where(np.isfinite(right) & (np.abs(right) > 1e-9), np.abs(right), np.nan)
        out = left / denom
    else:
        raise ValueError(f"unsupported interaction operator: {operator}")
    out = out.astype(np.float64, copy=False)
    out[~np.isfinite(out)] = np.nan
    return np.clip(out, -50.0, 50.0)


def load_fields(field_names: set[str]) -> tuple[list[str], pd.DatetimeIndex, dict[str, np.ndarray], dict[str, np.ndarray], list[str], int]:
    candidate_fields = set(field_names) | {"trade_close", "realized_vol_168h"}
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_fields = {field for field in candidate_fields if field in base_schema}
    latent_fields = {field for field in candidate_fields if field in latent_schema and field not in base_fields}
    missing = sorted(candidate_fields - base_fields - latent_fields)
    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    groups = load_group_fields(loaded_symbols, timestamps, {"liquidity_tier"})
    full_timestamp_count = int(len(timestamps))
    idx = smoke_column_indices(timestamps)
    timestamps = pd.DatetimeIndex(timestamps[idx])
    numeric = {key: value[:, idx] for key, value in numeric.items()}
    groups = {key: value[:, idx] for key, value in groups.items()}
    return loaded_symbols, timestamps, numeric, groups, missing, full_timestamp_count


def build_blueprints(interaction_family: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    contract = pd.read_csv(INTERACTION_CONTRACT)
    fields = pd.read_csv(A7AA0_FIELDS)
    row = contract[contract["interaction_family"].astype(str).eq(interaction_family)]
    if row.empty:
        raise SystemExit(f"unknown interaction family: {interaction_family}")
    spec = row.iloc[0].to_dict()
    left_family = str(spec["left_family"])
    right_families = parse_list(spec["right_family"])
    transforms = parse_list(spec["allowed_transforms"])
    left_fields = fields[fields["field_family"].astype(str).eq(left_family)].copy()
    right_fields = fields[fields["field_family"].astype(str).isin(right_families)].copy()
    blueprints: list[dict[str, Any]] = []
    for left in left_fields.to_dict("records"):
        for right in right_fields.to_dict("records"):
            if left["field_name"] == right["field_name"]:
                continue
            for transform in transforms:
                for operator in OPERATORS:
                    if operator == "Sub" and "divergence" not in interaction_family.lower() and left_family not in {"positioning"}:
                        continue
                    blueprints.append(
                        {
                            "interaction_family": interaction_family,
                            "left_field": left["field_name"],
                            "left_family": left_family,
                            "right_field": right["field_name"],
                            "right_family": right["field_family"],
                            "transform": transform,
                            "operator": operator,
                            "blueprint_id": f"core16ge_{interaction_family}_{left['field_name']}_{operator}_{right['field_name']}_{transform}",
                        }
                    )
    return pd.DataFrame(blueprints), fields


def evaluate_interaction_family(interaction_family: str) -> dict[str, Any]:
    core16g = read_json(CORE16G)
    if core16g.get("decision") != "PASS_A7FFCORE16G_FAMILY_NATIVE_INTERACTION_CONTRACT_READY_FOR_CORE16GE":
        raise SystemExit(f"CORE16G is not ready: {core16g.get('decision')}")

    shard_dir = RUNTIME / f"interaction_family={interaction_family}"
    shard_dir.mkdir(parents=True, exist_ok=True)
    blueprints, _fields = build_blueprints(interaction_family)
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
    rng = np.random.default_rng(abs(hash(interaction_family)) % (2**32))
    transform_cache: dict[tuple[str, str], np.ndarray] = {}

    def get_transformed(field: str, transform: str) -> np.ndarray:
        key = (field, transform)
        if key not in transform_cache:
            transform_cache[key] = transform_signal(numeric[field], transform)
        return transform_cache[key]

    rows: list[dict[str, Any]] = []
    for bp in blueprints.to_dict("records"):
        try:
            left = get_transformed(str(bp["left_field"]), str(bp["transform"]))
            right = get_transformed(str(bp["right_field"]), str(bp["transform"]))
            signal = combine_signal(left, right, str(bp["operator"]))
        except Exception as exc:  # noqa: BLE001
            rows.append({**bp, "decision": "HOLD_A7FFCORE16GE_MATERIALIZATION_ERROR", "error": repr(exc)})
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
                probe_candidate = pre_may_all and np.isfinite(control_ratio) and control_ratio < 1.0
                near_miss = (not probe_candidate) and pre_may_all and np.isfinite(control_ratio) and control_ratio < 1.5
                if probe_candidate and lag_ok:
                    decision = "A7FFCORE16GE_INTERACTION_PROBE_LAG_OK"
                elif probe_candidate:
                    decision = "A7FFCORE16GE_INTERACTION_PROBE_LAG_FRAGILE"
                elif near_miss:
                    decision = "A7FFCORE16GE_NEAR_MISS_CONTROL_MARGIN"
                elif pre_may_all:
                    decision = "HOLD_A7FFCORE16GE_CONTROL_LIKE"
                else:
                    decision = "HOLD_A7FFCORE16GE_PREMAY_UNSTABLE"
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
                        "probe_candidate": probe_candidate,
                        "near_miss": near_miss,
                        "decision": decision,
                        **summary,
                        "avg_n_obs_recent": float(np.nanmean(valid_counts[(split == "recent_oos_2026JanApr")])) if np.any(split == "recent_oos_2026JanApr") else np.nan,
                        "error": "",
                    }
                )
    response = pd.DataFrame(rows)
    candidates = response[response.get("probe_candidate", pd.Series(dtype=bool)).astype(str).str.lower().eq("true")].copy()
    response.to_csv(shard_dir / "a7ffcore16ge_interaction_response_map.csv", index=False)
    blueprints.to_csv(shard_dir / "a7ffcore16ge_blueprint_queue.csv", index=False)
    candidates.to_csv(shard_dir / "a7ffcore16ge_interaction_probe_candidates.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE16GE-INTERACTION",
        "generated_at": now_utc(),
        "interaction_family": interaction_family,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": full_timestamp_count,
        "blueprint_count": int(len(blueprints)),
        "response_rows": int(len(response)),
        "probe_candidate_count": int(len(candidates)),
        "near_miss_count": int((response.get("near_miss", pd.Series(dtype=bool)).astype(str).str.lower() == "true").sum()) if not response.empty else 0,
        "missing_fields_excluded": missing,
        "decision": "PASS_A7FFCORE16GE_INTERACTION_SHARD_COMPLETE",
    }
    write_json(shard_dir / "a7ffcore16ge_interaction_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def summarize() -> dict[str, Any]:
    family_dirs = [p for p in RUNTIME.glob("interaction_family=*") if p.is_dir()]
    responses = []
    blueprints = []
    candidates = []
    manifests = []
    for directory in family_dirs:
        manifest = read_json(directory / "a7ffcore16ge_interaction_manifest.json")
        if manifest:
            manifests.append(manifest)
        resp = directory / "a7ffcore16ge_interaction_response_map.csv"
        bp = directory / "a7ffcore16ge_blueprint_queue.csv"
        cand = directory / "a7ffcore16ge_interaction_probe_candidates.csv"
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
        response.groupby("interaction_family", dropna=False)
        .agg(
            response_rows=("blueprint_id", "size"),
            blueprint_count=("blueprint_id", "nunique"),
            probe_candidate_count=("probe_candidate", "sum"),
            near_miss_count=("near_miss", "sum"),
            label_family_count=("label_family", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values(["probe_candidate_count", "near_miss_count"], ascending=[False, False])
        if not response.empty
        else pd.DataFrame()
    )
    decision_counts = response["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not response.empty else pd.DataFrame()
    candidate_count = int(len(candidate_df))
    family_count = int(candidate_df["interaction_family"].nunique()) if not candidate_df.empty else 0
    top_share = float(candidate_df["interaction_family"].value_counts(normalize=True).max()) if not candidate_df.empty else 0.0
    blockers: list[str] = []
    if candidate_count < 64:
        blockers.append("interaction_probe_candidates_lt_64")
    if family_count < 4:
        blockers.append("interaction_family_count_lt_4")
    if candidate_count and top_share > 0.40:
        blockers.append("top_interaction_family_share_gt_40pct")
    if blockers:
        decision = "HOLD_A7FFCORE16GE_INTERACTION_PROBE_SUPPLY_INSUFFICIENT"
        next_allowed = "A7FF-CORE16GER interaction probe forensic"
        authorizes_core17 = False
    else:
        decision = "PASS_A7FFCORE16GE_INTERACTION_PROBE_READY_FOR_CORE17_CONTRACT"
        next_allowed = "A7FF-CORE17 objective seed policy contract"
        authorizes_core17 = True
    response.to_csv(RUNTIME / "a7ffcore16ge_interaction_response_map.csv", index=False)
    blueprint_df.to_csv(RUNTIME / "a7ffcore16ge_blueprint_queue.csv", index=False)
    candidate_df.to_csv(RUNTIME / "a7ffcore16ge_interaction_probe_candidates.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore16ge_interaction_family_summary.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7ffcore16ge_decision_counts.csv", index=False)
    pd.DataFrame(manifests).to_csv(RUNTIME / "a7ffcore16ge_shard_manifest_summary.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE16GE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16G",
        "source_decision": read_json(CORE16G).get("decision"),
        "decision": decision,
        "blockers": blockers,
        "completed_interaction_shards": len(manifests),
        "blueprint_count": int(len(blueprint_df)),
        "response_rows": int(len(response)),
        "interaction_probe_candidate_count": candidate_count,
        "interaction_family_count": family_count,
        "top_interaction_family_share": top_share,
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
    write_json(RUNTIME / "a7ffcore16ge_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16GE FAMILY-NATIVE INTERACTION PROBE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16GE executes typed interaction probes authorized by CORE16G. It does not execute open grammar formula generation, bounded replay, search, promotion, alpha proof, shadow, paper, or live.",
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
        "## Interaction Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Probe Candidate Sample",
        "",
        md_table(candidate_df.head(80)),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interaction-family")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    if args.summary:
        summarize()
    elif args.interaction_family:
        evaluate_interaction_family(args.interaction_family)
    else:
        raise SystemExit("pass --interaction-family NAME or --summary")


if __name__ == "__main__":
    main()
