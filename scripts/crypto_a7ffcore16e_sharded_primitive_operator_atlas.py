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
from scripts.crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    load_base,
    load_group_fields,
    load_latent_numeric,
    parquet_schema,
    rolling_mean,
    shift_matrix,
)
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import smoke_column_indices, spread_series  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore16e_expanded_primitive_operator_atlas"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16E_EXPANDED_PRIMITIVE_OPERATOR_ATLAS_20260601.md"
CORE16R = REPO / "runtime" / "a7ffcore16r_primitive_atlas_supply_repair" / "a7ffcore16r_manifest.json"
A7AA0_FIELDS = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_candidate_primitive_fields.csv"

LABEL_HORIZONS = [1, 4, 8, 24]
LABELS = [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
]
TRANSFORMS = [
    "level",
    "delta_1h",
    "delta_4h",
    "delta_24h",
    "zscore_72h",
    "zscore_168h",
    "tsrank_72h",
    "tsrank_168h",
    "shock_24h",
    "spread_short_long",
]


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


def rolling_tsrank(values: np.ndarray, window: int) -> np.ndarray:
    out = np.full_like(values, np.nan, dtype=np.float64)
    for offset in range(window - 1, values.shape[1]):
        block = values[:, offset - window + 1 : offset + 1]
        current = values[:, offset]
        with np.errstate(invalid="ignore"):
            out[:, offset] = np.nanmean(block <= current[:, None], axis=1)
    out[~np.isfinite(out)] = np.nan
    return out


def transform_signal(values: np.ndarray, transform: str) -> np.ndarray:
    if transform == "level":
        return values.astype(np.float64, copy=True)
    if transform == "delta_1h":
        return values - shift_matrix(values, 1)
    if transform == "delta_4h":
        return values - shift_matrix(values, 4)
    if transform == "delta_24h":
        return values - shift_matrix(values, 24)
    if transform == "zscore_72h":
        return rolling_zscore(values, 72)
    if transform == "zscore_168h":
        return rolling_zscore(values, 168)
    if transform == "tsrank_72h":
        return rolling_tsrank(values, 72)
    if transform == "tsrank_168h":
        return rolling_tsrank(values, 168)
    if transform == "shock_24h":
        delta = values - shift_matrix(values, 24)
        scale = rolling_mean(np.abs(delta), 168)
        out = delta / np.where(np.isfinite(scale) & (scale > 1e-12), scale, np.nan)
        out[~np.isfinite(out)] = np.nan
        return out
    if transform == "spread_short_long":
        return rolling_mean(values, 24) - rolling_mean(values, 168)
    raise ValueError(f"unsupported transform: {transform}")


def load_fields(fields_df: pd.DataFrame) -> tuple[list[str], pd.DatetimeIndex, dict[str, np.ndarray], dict[str, np.ndarray], list[str], int]:
    candidate_fields = set(fields_df["field_name"].astype(str)) | {"trade_close", "realized_vol_168h"}
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


def run_family(field_family: str) -> dict[str, Any]:
    core16r = read_json(CORE16R)
    if core16r.get("decision") != "PASS_A7FFCORE16R_PRIMITIVE_ATLAS_SUPPLY_REPAIR_READY_FOR_CORE16E":
        raise SystemExit(f"A7FF-CORE16R is not ready: {core16r.get('decision')}")
    fields_all = pd.read_csv(A7AA0_FIELDS)
    fields_df = fields_all[fields_all["field_family"].astype(str).eq(field_family)].copy()
    if fields_df.empty:
        raise SystemExit(f"no fields for family {field_family}")
    shard_dir = RUNTIME / f"family={field_family}"
    shard_dir.mkdir(parents=True, exist_ok=True)
    loaded_symbols, timestamps, numeric, groups, missing, full_timestamp_count = load_fields(fields_df)
    fields_df = fields_df[~fields_df["field_name"].isin(missing)].copy()
    split = split_for_timestamps(timestamps)
    raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in LABEL_HORIZONS}
    vol = numeric.get("realized_vol_168h", np.full_like(numeric["trade_close"], np.nan))
    liquidity_tier = groups["liquidity_tier"]
    rng = np.random.default_rng(abs(hash(field_family)) % (2**32))
    rows: list[dict[str, Any]] = []
    for field_row in fields_df.to_dict("records"):
        field = str(field_row["field_name"])
        values = numeric.get(field)
        if values is None:
            continue
        for transform in TRANSFORMS:
            try:
                signal = transform_signal(values, transform)
            except Exception as exc:  # noqa: BLE001
                rows.append({"field_name": field, "field_family": field_family, "transform": transform, "decision": "HOLD_A7FFCORE16E_TRANSFORM_ERROR", "error": repr(exc)})
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
                    atlas_candidate = pre_may_all and np.isfinite(control_ratio) and control_ratio < 1.0
                    if atlas_candidate and lag_ok:
                        decision = "A7FFCORE16E_ATLAS_CANDIDATE_LAG_OK"
                    elif atlas_candidate:
                        decision = "A7FFCORE16E_ATLAS_CANDIDATE_LAG_FRAGILE"
                    elif pre_may_all and np.isfinite(control_ratio) and control_ratio < 1.25:
                        decision = "A7FFCORE16E_NEAR_MISS_CONTROL_MARGIN"
                    elif pre_may_all:
                        decision = "HOLD_A7FFCORE16E_CONTROL_LIKE"
                    else:
                        decision = "HOLD_A7FFCORE16E_PREMAY_UNSTABLE"
                    rows.append(
                        {
                            "field_name": field,
                            "field_family": field_family,
                            "source_family": field_row.get("source_family", ""),
                            "feature_class": field_row.get("feature_class", ""),
                            "transform": transform,
                            "label_family": label_family,
                            "label_horizon_h": horizon,
                            "orientation_from_train": orientation,
                            "premay_positive_split_count": pre_may_count,
                            "premay_all_positive": pre_may_all,
                            "control_ratio_premay_max": control_ratio,
                            "one_bar_lag_recent_oriented": lag_recent,
                            "lag_ok": lag_ok,
                            "atlas_candidate": atlas_candidate,
                            "decision": decision,
                            **summary,
                            "avg_n_obs_recent": float(np.nanmean(valid_counts[(split == "recent_oos_2026JanApr")])) if np.any(split == "recent_oos_2026JanApr") else np.nan,
                            "error": "",
                        }
                    )
    response = pd.DataFrame(rows)
    atlas = response[response.get("atlas_candidate", pd.Series(dtype=bool)).astype(str).str.lower().eq("true")].copy()
    if not atlas.empty:
        atlas["objective_id"] = "core16e_" + atlas["field_family"].astype(str) + "_" + atlas["field_name"].astype(str) + "_" + atlas["transform"].astype(str) + "_" + atlas["label_family"].astype(str) + "_h" + atlas["label_horizon_h"].astype(str)
    response.to_csv(shard_dir / "a7ffcore16e_family_response_map.csv", index=False)
    atlas.to_csv(shard_dir / "a7ffcore16e_family_atlas_candidates.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE16E-FAMILY",
        "generated_at": now_utc(),
        "field_family": field_family,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": full_timestamp_count,
        "field_count": int(len(fields_df)),
        "response_rows": int(len(response)),
        "atlas_candidate_count": int(len(atlas)),
        "transform_count": int(atlas["transform"].nunique()) if not atlas.empty else 0,
        "missing_fields_excluded": missing,
        "decision": "PASS_A7FFCORE16E_FAMILY_SHARD_COMPLETE",
    }
    write_json(shard_dir / "a7ffcore16e_family_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def summarize() -> dict[str, Any]:
    family_dirs = [p for p in RUNTIME.glob("family=*") if p.is_dir()]
    responses = []
    atlas_parts = []
    manifests = []
    for directory in family_dirs:
        manifest = read_json(directory / "a7ffcore16e_family_manifest.json")
        if manifest:
            manifests.append(manifest)
        resp = directory / "a7ffcore16e_family_response_map.csv"
        cand = directory / "a7ffcore16e_family_atlas_candidates.csv"
        if resp.exists():
            responses.append(pd.read_csv(resp))
        if cand.exists():
            atlas_parts.append(pd.read_csv(cand))
    response = pd.concat(responses, ignore_index=True) if responses else pd.DataFrame()
    atlas = pd.concat(atlas_parts, ignore_index=True) if atlas_parts else pd.DataFrame()
    family = (
        response.groupby(["field_family", "transform", "label_family"], dropna=False)
        .agg(
            rows=("field_name", "size"),
            atlas_candidate_count=("atlas_candidate", "sum"),
            lag_ok_candidate_count=("decision", lambda s: int((s == "A7FFCORE16E_ATLAS_CANDIDATE_LAG_OK").sum())),
            near_miss_count=("decision", lambda s: int((s == "A7FFCORE16E_NEAR_MISS_CONTROL_MARGIN").sum())),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values(["atlas_candidate_count", "near_miss_count"], ascending=[False, False])
        if not response.empty
        else pd.DataFrame()
    )
    decision_counts = response["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not response.empty else pd.DataFrame()
    candidate_count = int(atlas["objective_id"].nunique()) if "objective_id" in atlas.columns else int(len(atlas))
    field_family_count = int(atlas["field_family"].nunique()) if not atlas.empty else 0
    transform_count = int(atlas["transform"].nunique()) if not atlas.empty else 0
    top_family_share = float(atlas["field_family"].value_counts(normalize=True).max()) if not atlas.empty else 1.0
    blockers = []
    if candidate_count < 64:
        blockers.append("atlas_candidate_count_lt_64")
    if field_family_count < 6:
        blockers.append("field_family_count_lt_6")
    if transform_count < 5:
        blockers.append("transform_count_lt_5")
    if top_family_share > 0.30:
        blockers.append("top_family_share_gt_30pct")
    decision = "PASS_A7FFCORE16E_EXPANDED_PRIMITIVE_ATLAS_READY_FOR_CORE17" if not blockers else "HOLD_A7FFCORE16E_EXPANDED_PRIMITIVE_ATLAS_INSUFFICIENT"
    response.to_csv(RUNTIME / "a7ffcore16e_expanded_response_map.csv", index=False)
    atlas.to_csv(RUNTIME / "a7ffcore16e_candidate_objective_atlas.csv", index=False)
    family.to_csv(RUNTIME / "a7ffcore16e_operator_family_scoreboard.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7ffcore16e_decision_counts.csv", index=False)
    pd.DataFrame(manifests).to_csv(RUNTIME / "a7ffcore16e_family_manifest_summary.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE16E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16R",
        "source_decision": read_json(CORE16R).get("decision"),
        "decision": decision,
        "blockers": blockers,
        "completed_family_shards": len(manifests),
        "response_rows": int(len(response)),
        "atlas_candidate_count": candidate_count,
        "field_family_count": field_family_count,
        "atlas_transform_count": transform_count,
        "top_family_share": top_family_share,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core17": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE17 objective atlas seed policy" if decision.startswith("PASS_") else "A7FF-CORE16ER expanded atlas failure forensic",
    }
    write_json(RUNTIME / "a7ffcore16e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16E EXPANDED PRIMITIVE / OPERATOR ATLAS",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE16E executes an expanded primitive/operator response atlas as field-family shards. It does not execute formula generation, replay, search, promotion, alpha proof, shadow, paper, or live.",
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
        "## Operator / Family Scoreboard",
        "",
        md_table(family, max_rows=120),
        "",
        "## Candidate Objective Atlas",
        "",
        md_table(atlas, max_rows=100),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    RUNTIME.mkdir(parents=True, exist_ok=True)
    if args.summary:
        summarize()
    elif args.family:
        run_family(args.family)
    else:
        raise SystemExit("pass --family FIELD_FAMILY or --summary")


if __name__ == "__main__":
    main()
