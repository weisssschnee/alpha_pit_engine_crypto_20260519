from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_END, SPLIT_ORDER, split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    cs_rank_pct,
    group_demean,
    load_base,
    load_group_fields,
    load_latent_numeric,
    parquet_schema,
    rolling_mean,
    shift_matrix,
)
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import smoke_column_indices, spread_series, tstat  # noqa: E402


RUNTIME = REPO / "runtime" / "a7aa1_primitive_response_map"
REPORT = REPO / "reports" / "CRYPTO_A7AA1_PRIMITIVE_RESPONSE_MAP_20260529.md"
A7AA0_MANIFEST = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_manifest.json"
A7AA0_FIELDS = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_candidate_primitive_fields.csv"
A7AA0_LABELS = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_label_family_contract.csv"
A7AA0_TRANSFORMS = REPO / "runtime" / "a7aa0_label_feature_response_contract" / "a7aa0_transform_contract.csv"

PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
LABEL_HORIZONS = [1, 4, 24]
MIN_ACTIVE_SYMBOLS = 30
FEATURE_CAP = 24
ENABLED_TRANSFORMS = ["level", "delta_24h", "cs_rank"]
ENABLED_LABELS = ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L7_ranked_future_return"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def horizon_label(close: np.ndarray, timestamps: pd.DatetimeIndex, split: np.ndarray, horizon: int) -> np.ndarray:
    x = np.where(close > 0, close, np.nan)
    log_close = np.log(x)
    label = shift_matrix(log_close, -horizon) - log_close
    label_end = timestamps + pd.Timedelta(hours=horizon)
    for split_name in SPLIT_ORDER:
        mask = (split == split_name) & (label_end > SPLIT_END[split_name])
        label[:, mask] = np.nan
    label[:, split == "out_of_scope"] = np.nan
    return label


def rolling_zscore(values: np.ndarray, window: int = 168) -> np.ndarray:
    mean = rolling_mean(values, window)
    second = rolling_mean(values * values, window)
    var = second - mean * mean
    std = np.sqrt(np.where(var > 0, var, np.nan))
    out = (values - mean) / std
    out[~np.isfinite(out)] = np.nan
    return out


def transform_signal(values: np.ndarray, transform: str) -> np.ndarray:
    if transform == "level":
        return values.astype(np.float64, copy=True)
    if transform == "delta_4h":
        return values - shift_matrix(values, 4)
    if transform == "delta_24h":
        return values - shift_matrix(values, 24)
    if transform == "cs_rank":
        return cs_rank_pct(values)
    if transform == "ts_zscore_168h":
        return rolling_zscore(values, 168)
    raise ValueError(f"unsupported transform: {transform}")


def label_family_matrix(
    raw: np.ndarray,
    label_family: str,
    vol: np.ndarray,
    liquidity_tier: np.ndarray,
) -> np.ndarray:
    if label_family == "L0_raw_forward_return":
        return raw
    if label_family == "L1_cross_sectional_relative_return":
        with np.errstate(invalid="ignore"):
            mean = np.nanmean(raw, axis=0, keepdims=True)
        return raw - mean
    if label_family == "L3_liquidity_tier_relative_return":
        return group_demean(raw, liquidity_tier)
    if label_family == "L5_vol_adjusted_return":
        denom = np.where(np.isfinite(vol) & (vol > 1e-8), vol, np.nan)
        return raw / denom
    if label_family == "L7_ranked_future_return":
        return cs_rank_pct(raw) - 0.5
    raise ValueError(f"unsupported label family: {label_family}")


def nonoverlap_tstat(values: np.ndarray, mask: np.ndarray, horizon: int) -> tuple[float, float]:
    stats = []
    idx = np.where(mask & np.isfinite(values))[0]
    if len(idx) == 0:
        return np.nan, np.nan
    step = max(1, int(horizon))
    for offset in range(step):
        sub_idx = idx[idx % step == offset]
        if len(sub_idx) >= 3:
            stats.append(tstat(values[sub_idx]))
    finite = [x for x in stats if np.isfinite(x)]
    if not finite:
        return np.nan, np.nan
    return float(np.nanmedian(finite)), float(np.nanmin(finite))


def summarize_spread(spread: np.ndarray, split: np.ndarray, horizon: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for split_name in ["train_2024", *PRE_MAY_SPLITS]:
        mask = (split == split_name) & np.isfinite(spread)
        x = spread[mask]
        med_t, min_t = nonoverlap_tstat(spread, split == split_name, horizon)
        out[f"{split_name}_n"] = int(mask.sum())
        out[f"{split_name}_mean_spread"] = float(np.nanmean(x)) if len(x) else np.nan
        out[f"{split_name}_tstat"] = tstat(x)
        out[f"{split_name}_nonoverlap_median_tstat"] = med_t
        out[f"{split_name}_nonoverlap_min_tstat"] = min_t
        out[f"{split_name}_positive_rate"] = float(np.nanmean(x > 0)) if len(x) else np.nan
    return out


def max_control_ratio(
    original_oriented: dict[str, float],
    control_spreads: dict[str, np.ndarray],
    orientation: float,
    split: np.ndarray,
) -> float:
    ratios: list[float] = []
    for split_name in PRE_MAY_SPLITS:
        orig = abs(original_oriented.get(split_name, np.nan))
        if not np.isfinite(orig) or orig <= 1e-12:
            continue
        for values in control_spreads.values():
            mask = (split == split_name) & np.isfinite(values)
            ctrl = abs(orientation * float(np.nanmean(values[mask]))) if mask.any() else np.nan
            if np.isfinite(ctrl):
                ratios.append(ctrl / orig)
    return float(max(ratios)) if ratios else np.nan


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7aa0 = read_json(A7AA0_MANIFEST)
    if not a7aa0.get("authorizes_a7aa1_primitive_response_map"):
        raise SystemExit("A7AA-0 does not authorize A7AA-1")
    fields_df = pd.read_csv(A7AA0_FIELDS).head(FEATURE_CAP)
    labels_df = pd.read_csv(A7AA0_LABELS)
    labels = [
        x
        for x in labels_df.loc[labels_df["allowed_in_a7aa1"].astype(str).str.lower().isin(["true", "1"]), "label_family"].tolist()
        if x in ENABLED_LABELS
    ]
    transforms = [x for x in pd.read_csv(A7AA0_TRANSFORMS)["transform"].tolist() if x in ENABLED_TRANSFORMS]

    candidate_fields = set(fields_df["field_name"].astype(str)) | {"trade_close", "realized_vol_168h"}
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_fields = {field for field in candidate_fields if field in base_schema}
    latent_fields = {field for field in candidate_fields if field in latent_schema and field not in base_fields}
    missing = sorted(candidate_fields - base_fields - latent_fields)
    if missing:
        fields_df = fields_df[~fields_df["field_name"].isin(missing)].copy()
    symbols = strict_symbols()
    print(f"[A7AA-1] loading {len(symbols)} symbols, base_fields={len(base_fields)}, latent_fields={len(latent_fields)}", flush=True)
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    groups = load_group_fields(loaded_symbols, timestamps, {"liquidity_tier"})
    full_timestamp_count = int(len(timestamps))
    idx = smoke_column_indices(timestamps)
    timestamps = pd.DatetimeIndex(timestamps[idx])
    numeric = {key: value[:, idx] for key, value in numeric.items()}
    groups = {key: value[:, idx] for key, value in groups.items()}
    split = split_for_timestamps(timestamps)
    raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in LABEL_HORIZONS}
    print(f"[A7AA-1] loaded symbols={len(loaded_symbols)}, timestamps={len(timestamps)}, response_grid={len(fields_df) * len(transforms) * len(labels) * len(LABEL_HORIZONS)}", flush=True)
    vol = numeric.get("realized_vol_168h")
    if vol is None:
        vol = np.full_like(numeric["trade_close"], np.nan)
    liquidity_tier = groups["liquidity_tier"]
    rng = np.random.default_rng(20260529)

    rows: list[dict[str, Any]] = []
    for i, field_row in enumerate(fields_df.to_dict("records"), start=1):
        field = str(field_row["field_name"])
        if field not in numeric:
            continue
        values = numeric[field]
        print(f"[A7AA-1] field {i}/{len(fields_df)} {field}", flush=True)
        for transform in transforms:
            try:
                signal = transform_signal(values, transform)
            except Exception as exc:  # noqa: BLE001
                rows.append(
                    {
                        "field_name": field,
                        "field_family": field_row.get("field_family", ""),
                        "transform": transform,
                        "label_family": "",
                        "label_horizon_h": 0,
                        "decision": "HOLD_A7AA1_TRANSFORM_ERROR",
                        "error": repr(exc),
                    }
                )
                continue
            variants = {
                "wrong_lag_future_24h": shift_matrix(signal, -24),
                "wrong_lag_stale_168h": shift_matrix(signal, 168),
                "same_family_random": rng.normal(size=signal.shape),
                "one_bar_lag": shift_matrix(signal, 1),
            }
            for horizon, raw in raw_labels.items():
                for label_family in labels:
                    label = label_family_matrix(raw, label_family, vol, liquidity_tier)
                    spread, valid_counts = spread_series(signal, label)
                    summary = summarize_spread(spread, split, horizon)
                    train_mean = summary.get("train_2024_mean_spread", np.nan)
                    orientation = 1.0 if not np.isfinite(train_mean) or train_mean >= 0 else -1.0
                    oriented = {
                        split_name: orientation * float(summary.get(f"{split_name}_mean_spread", np.nan))
                        for split_name in ["train_2024", *PRE_MAY_SPLITS]
                    }
                    pre_may_positive_count = int(sum(np.isfinite(oriented[s]) and oriented[s] > 0 for s in PRE_MAY_SPLITS))
                    pre_may_positive_all = pre_may_positive_count == len(PRE_MAY_SPLITS)
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
                    if not pre_may_positive_all:
                        decision = "HOLD_A7AA1_PRE_MAY_UNSTABLE"
                    elif np.isfinite(control_ratio) and control_ratio >= 1.0:
                        decision = "HOLD_A7AA1_CONTROL_LIKE"
                    elif not lag_ok:
                        decision = "HOLD_A7AA1_LAG_FRAGILE"
                    else:
                        decision = "A7AA1_PRIMITIVE_RESPONSE_CANDIDATE"
                    rows.append(
                        {
                            "field_name": field,
                            "field_family": field_row.get("field_family", ""),
                            "source_family": field_row.get("source_family", ""),
                            "feature_class": field_row.get("feature_class", ""),
                            "transform": transform,
                            "label_family": label_family,
                            "label_horizon_h": horizon,
                            "orientation_from_train": orientation,
                            "premay_positive_split_count": pre_may_positive_count,
                            "premay_all_positive": pre_may_positive_all,
                            "control_ratio_premay_max": control_ratio,
                            "one_bar_lag_recent_oriented": lag_recent,
                            "lag_ok": lag_ok,
                            "decision": decision,
                            **summary,
                            "avg_n_obs_recent": float(np.nanmean(valid_counts[(split == "recent_oos_2026JanApr")])) if np.any(split == "recent_oos_2026JanApr") else np.nan,
                            "error": "",
                        }
                    )

    response = pd.DataFrame(rows)
    candidates = response[response["decision"].eq("A7AA1_PRIMITIVE_RESPONSE_CANDIDATE")].copy()
    family = (
        response.groupby(["field_family", "label_family", "label_horizon_h"], dropna=False)
        .agg(
            combos=("field_name", "count"),
            candidate_count=("decision", lambda s: int((s == "A7AA1_PRIMITIVE_RESPONSE_CANDIDATE").sum())),
            pre_may_stable_count=("premay_all_positive", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        if not response.empty
        else pd.DataFrame()
    )
    decision_counts = response["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not response.empty else pd.DataFrame(columns=["decision", "count"])
    candidate_count = int(len(candidates))
    decision = (
        "PASS_A7AA1_PRIMITIVE_RESPONSE_CANDIDATES_FOUND_FORMULA_SEARCH_STILL_HOLD"
        if candidate_count > 0
        else "HOLD_A7AA1_NO_PRIMITIVE_RESPONSE_CANDIDATES"
    )
    manifest = {
        "stage": "A7AA-1",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_primitive_response_map": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7aa2_feature_role_classification": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": full_timestamp_count,
        "feature_count": int(len(fields_df)),
        "transform_count": int(len(transforms)),
        "label_family_count": int(len(labels)),
        "label_horizon_count": int(len(LABEL_HORIZONS)),
        "response_rows": int(len(response)),
        "primitive_response_candidate_count": candidate_count,
        "missing_fields_excluded": missing,
        "uses_may": False,
    }
    response.to_csv(RUNTIME / "a7aa1_primitive_response_map.csv", index=False)
    candidates.to_csv(RUNTIME / "a7aa1_primitive_response_candidates.csv", index=False)
    family.to_csv(RUNTIME / "a7aa1_field_family_label_summary.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7aa1_decision_counts.csv", index=False)
    write_json(RUNTIME / "a7aa1_manifest.json", manifest)
    write_json(
        RUNTIME / "a7aa1_authorization_matrix.json",
        {
            "A7AA-1": {"status": decision},
            "a7aa2_feature_role_classification": {"authorized": True},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AA-1 PRIMITIVE FEATURE RESPONSE MAP",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AA-1 maps primitive field/transform response across label families and horizons. It does not generate formulas, search, train, or authorize proof.",
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
        "## Primitive Response Candidates",
        "",
        md_table(candidates.sort_values(["field_family", "field_name", "label_horizon_h"]).head(80), 80),
        "",
        "## Family / Label Summary",
        "",
        md_table(family.sort_values("candidate_count", ascending=False).head(120), 120),
        "",
        "## Boundary",
        "",
        "```text",
        "Formula search remains not authorized.",
        "This stage only identifies primitive response candidates and feature roles.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
