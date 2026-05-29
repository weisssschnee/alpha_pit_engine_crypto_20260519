from __future__ import annotations

import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_ORDER, label_matrix, split_for_timestamps  # noqa: E402
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    StateAwareEvaluator,
    load_base,
    load_group_fields,
    load_latent_numeric,
    parquet_schema,
    shift_matrix,
)
from scripts.crypto_a7al2z2_broader_non_oi_materialization_audit import expression_group_fields, split_pipe  # noqa: E402
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402


RUNTIME = REPO / "runtime" / "a7al2z4_broader_non_oi_numeric_replay_preflight"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z4_BROADER_NON_OI_NUMERIC_REPLAY_PREFLIGHT_20260529.md"
Z3_MANIFEST = REPO / "runtime" / "a7al2z3_broader_non_oi_numeric_preflight_contract" / "a7al2z3_manifest.json"
Z2R_SELECTED = REPO / "runtime" / "a7al2z2r_broader_non_oi_materialization_repair" / "a7al2z2r_repaired_selected_candidates.csv"

MIN_ACTIVE_SYMBOLS = 30
HOURS_PER_SPLIT = 720
PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
CONTROL_VARIANTS = [
    "one_bar_lag",
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random",
]


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


def selected_fields(selected: pd.DataFrame) -> set[str]:
    fields = {"trade_close"}
    for text in selected["fields"].dropna().astype(str):
        fields.update(split_pipe(text))
    return fields


def shift_object_matrix(values: np.ndarray, periods: int) -> np.ndarray:
    out = np.empty_like(values, dtype=object)
    out[:, :] = None
    if periods == 0:
        return values.copy()
    if periods > 0:
        out[:, periods:] = values[:, :-periods]
    else:
        p = abs(periods)
        out[:, :-p] = values[:, p:]
    return out


def shifted_numeric(fields: dict[str, np.ndarray], periods: int) -> dict[str, np.ndarray]:
    return {key: shift_matrix(value, periods) for key, value in fields.items()}


def shifted_groups(groups: dict[str, np.ndarray], periods: int) -> dict[str, np.ndarray]:
    return {key: shift_object_matrix(value, periods) for key, value in groups.items()}


def smoke_column_indices(timestamps: pd.DatetimeIndex) -> np.ndarray:
    split = split_for_timestamps(timestamps)
    selected: list[int] = []
    for split_name in SPLIT_ORDER:
        idx = np.where(split == split_name)[0]
        if len(idx) == 0:
            continue
        selected.extend(idx[-HOURS_PER_SPLIT:].tolist())
    return np.array(sorted(set(selected)), dtype=int)


def subset_columns(
    timestamps: pd.DatetimeIndex,
    numeric: dict[str, np.ndarray],
    groups: dict[str, np.ndarray],
) -> tuple[pd.DatetimeIndex, dict[str, np.ndarray], dict[str, np.ndarray]]:
    idx = smoke_column_indices(timestamps)
    return (
        pd.DatetimeIndex(timestamps[idx]),
        {key: value[:, idx] for key, value in numeric.items()},
        {key: value[:, idx] for key, value in groups.items()},
    )


def spread_series(signal: np.ndarray, label: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    valid = np.isfinite(signal) & np.isfinite(label)
    valid_counts = valid.sum(axis=0)
    enough = valid_counts >= MIN_ACTIVE_SYMBOLS
    sig = np.where(valid, signal, np.nan)
    ranks = pd.DataFrame(sig).rank(axis=0, pct=True, method="average").to_numpy(dtype=np.float64)
    top_mask = valid & enough.reshape(1, -1) & (ranks >= 0.90)
    bottom_mask = valid & enough.reshape(1, -1) & (ranks <= 0.10)
    top_count = top_mask.sum(axis=0)
    bottom_count = bottom_mask.sum(axis=0)
    top_sum = np.where(top_mask, label, 0.0).sum(axis=0)
    bottom_sum = np.where(bottom_mask, label, 0.0).sum(axis=0)
    spread = np.full(signal.shape[1], np.nan)
    ok = (top_count > 0) & (bottom_count > 0)
    spread[ok] = (top_sum[ok] / top_count[ok]) - (bottom_sum[ok] / bottom_count[ok])
    return spread, valid_counts


def tstat(values: np.ndarray) -> float:
    x = values[np.isfinite(values)]
    if len(x) < 3:
        return np.nan
    std = np.nanstd(x, ddof=1)
    return float(np.nanmean(x) / std * math.sqrt(len(x))) if np.isfinite(std) and std > 0 else np.nan


def nonoverlap_tstat(values: np.ndarray, mask: np.ndarray) -> tuple[float, float]:
    stats = []
    idx = np.where(mask & np.isfinite(values))[0]
    if len(idx) == 0:
        return np.nan, np.nan
    for offset in range(24):
        sub_idx = idx[idx % 24 == offset]
        if len(sub_idx) >= 3:
            stats.append(tstat(values[sub_idx]))
    finite = [x for x in stats if np.isfinite(x)]
    if not finite:
        return np.nan, np.nan
    return float(np.nanmedian(finite)), float(np.nanmin(finite))


def summarize_variant(
    candidate_id: str,
    objective_family: str,
    variant: str,
    spread: np.ndarray,
    valid_counts: np.ndarray,
    split: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split_name in SPLIT_ORDER:
        mask = (split == split_name) & np.isfinite(spread)
        x = spread[mask]
        med_t, min_t = nonoverlap_tstat(spread, split == split_name)
        rows.append(
            {
                "candidate_id": candidate_id,
                "objective_family": objective_family,
                "variant": variant,
                "split": split_name,
                "n_dates": int(mask.sum()),
                "avg_n_obs": float(np.nanmean(valid_counts[mask])) if mask.any() else np.nan,
                "mean_spread_24h": float(np.nanmean(x)) if len(x) else np.nan,
                "naive_tstat": tstat(x),
                "nonoverlap_median_tstat": med_t,
                "nonoverlap_min_tstat": min_t,
                "positive_spread_rate": float(np.nanmean(x > 0)) if len(x) else np.nan,
            }
        )
    return rows


def split_value(metrics: pd.DataFrame, candidate_id: str, variant: str, split: str) -> float:
    sub = metrics[
        metrics["candidate_id"].eq(candidate_id)
        & metrics["variant"].eq(variant)
        & metrics["split"].eq(split)
    ]
    return float(sub["mean_spread_24h"].iloc[0]) if len(sub) else np.nan


def split_n(metrics: pd.DataFrame, candidate_id: str, variant: str, split: str) -> int:
    sub = metrics[
        metrics["candidate_id"].eq(candidate_id)
        & metrics["variant"].eq(variant)
        & metrics["split"].eq(split)
    ]
    return int(sub["n_dates"].iloc[0]) if len(sub) else 0


def classify(metrics: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in sample.to_dict("records"):
        cid = row["candidate_id"]
        train = split_value(metrics, cid, "original", "train_2024")
        orientation = 1.0 if not np.isfinite(train) or train >= 0 else -1.0
        oriented = {split: orientation * split_value(metrics, cid, "original", split) for split in SPLIT_ORDER}
        pre_may_positive = all(np.isfinite(oriented[s]) and oriented[s] > 0 for s in PRE_MAY_SPLITS)
        recent = oriented["recent_oos_2026JanApr"]
        lag_recent = orientation * split_value(metrics, cid, "one_bar_lag", "recent_oos_2026JanApr")
        lag_ok = np.isfinite(recent) and np.isfinite(lag_recent) and lag_recent > 0 and abs(lag_recent) >= 0.25 * abs(recent)
        control_ratios = []
        control_dominated = False
        for split_name in PRE_MAY_SPLITS:
            orig_abs = abs(oriented[split_name])
            if not np.isfinite(orig_abs) or orig_abs <= 1e-12:
                continue
            for variant in CONTROL_VARIANTS:
                if variant == "one_bar_lag":
                    continue
                ctrl = abs(orientation * split_value(metrics, cid, variant, split_name))
                if np.isfinite(ctrl):
                    ratio = ctrl / orig_abs
                    control_ratios.append(ratio)
                    if ratio >= 1.0:
                        control_dominated = True
        control_ratio = max(control_ratios) if control_ratios else np.nan
        cost10_recent = recent - 2 * 10 / 10000
        may_stress = oriented["known_may2026_stress"]
        may_n = split_n(metrics, cid, "original", "known_may2026_stress")
        may_stress_clean = np.isfinite(may_stress) and may_stress > 0
        if not pre_may_positive:
            decision = "HOLD_A7AL2Z4_PRE_MAY_UNSTABLE"
        elif not lag_ok:
            decision = "HOLD_A7AL2Z4_ONE_BAR_LAG_FRAGILE"
        elif control_dominated:
            decision = "HOLD_A7AL2Z4_CONTROL_DOMINATED"
        elif not np.isfinite(cost10_recent) or cost10_recent <= 0:
            decision = "HOLD_A7AL2Z4_COST10_FRAGILE"
        elif may_n <= 0:
            decision = "A7AL2Z4_PRE_MAY_CLUE_MAY_STRESS_UNOBSERVED"
        elif not may_stress_clean:
            decision = "A7AL2Z4_PRE_MAY_CLUE_MAY_STRESS_VETOED"
        else:
            decision = "A7AL2Z4_NUMERIC_PREFLIGHT_CLUE_STRESS_CLEAN"
        rows.append(
            {
                "candidate_id": cid,
                "objective_family": row["objective_family"],
                "orientation_from_train": orientation,
                "oriented_validation_spread": oriented["validation_2025H1"],
                "oriented_test_spread": oriented["test_2025H2"],
                "oriented_recent_spread": recent,
                "oriented_may_stress_spread": may_stress,
                "may_stress_n_dates": may_n,
                "one_bar_lag_recent_oriented": lag_recent,
                "cost10_recent_proxy": cost10_recent,
                "control_dominance_ratio_premay_max": control_ratio,
                "pre_may_positive": pre_may_positive,
                "lag_ok": lag_ok,
                "may_stress_clean": may_stress_clean,
                "decision": decision,
            }
        )
    return pd.DataFrame(rows)


def write_report(manifest: dict[str, Any], decisions: pd.DataFrame, counts: pd.DataFrame, family: pd.DataFrame, metrics_preview: pd.DataFrame) -> None:
    lines = [
        "# CRYPTO A7AL-2Z4 BROADER NON-OI NUMERIC REPLAY PREFLIGHT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "This is a bounded numeric preflight over Z2R materialized candidates. It is not full replay, formula search, alpha proof, or production-readiness evidence.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Decision Counts",
        "",
        md_table(counts),
        "",
        "## Family Decision Summary",
        "",
        md_table(family),
        "",
        "## Candidate Decisions",
        "",
        md_table(decisions, 128),
        "",
        "## Metrics Preview",
        "",
        md_table(metrics_preview, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "Allowed interpretation:",
        "  Z4 can produce numeric-preflight clues or holds only.",
        "",
        "Not authorized:",
        "  full numeric replay",
        "  formula generation/search",
        "  alpha proof",
        "  shadow / paper / live",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    z3 = read_json(Z3_MANIFEST)
    if not z3.get("authorizes_a7al2z4_broader_non_oi_numeric_preflight"):
        raise SystemExit("A7AL-2Z3 does not authorize Z4 numeric preflight")

    sample = pd.read_csv(Z2R_SELECTED).sort_values(["objective_family", "skeleton_key", "candidate_id"]).reset_index(drop=True)
    fields = selected_fields(sample)
    group_fields = {
        f
        for f in fields
        if (f.startswith("R") and f.endswith("_state"))
        or f in {"liquidity_tier", "meme_contract_group", "is_multiplier_contract", "is_major"}
    }
    group_fields.update(expression_group_fields(sample))
    numeric_fields = fields - group_fields
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_numeric_fields = {field for field in numeric_fields if field in base_schema}
    latent_numeric_fields = {field for field in numeric_fields if field in latent_schema and field not in base_numeric_fields}
    missing_numeric_fields = sorted(numeric_fields - base_numeric_fields - latent_numeric_fields)
    if missing_numeric_fields:
        raise SystemExit(f"missing numeric fields for Z4: {missing_numeric_fields}")

    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_numeric_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_numeric_fields))
    groups = load_group_fields(loaded_symbols, timestamps, group_fields)
    full_timestamp_count = int(len(timestamps))
    timestamps, numeric, groups = subset_columns(timestamps, numeric, groups)
    split = split_for_timestamps(timestamps)
    label = label_matrix(numeric["trade_close"], timestamps, split)

    original_eval = StateAwareEvaluator(numeric, groups)
    future_eval = StateAwareEvaluator(shifted_numeric(numeric, -24), shifted_groups(groups, -24))
    stale_eval = StateAwareEvaluator(shifted_numeric(numeric, 168), shifted_groups(groups, 168))
    rng = np.random.default_rng(20260529)

    metric_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    for i, row in enumerate(sample.to_dict("records"), start=1):
        cid = row["candidate_id"]
        expr = row["expression"]
        print(f"[A7AL-2Z4] {i}/{len(sample)} {cid}", flush=True)
        try:
            signal = original_eval.eval(expr)
            variants: dict[str, np.ndarray] = {
                "original": signal,
                "one_bar_lag": shift_matrix(signal, 1),
                "time_shuffle": signal[:, rng.permutation(signal.shape[1])],
                "symbol_shuffle": signal[rng.permutation(signal.shape[0]), :],
                "same_family_random": rng.normal(size=signal.shape),
                "wrong_lag_future_24h": future_eval.eval(expr),
                "wrong_lag_stale_168h": stale_eval.eval(expr),
            }
            for variant, variant_signal in variants.items():
                spread, valid_counts = spread_series(variant_signal, label)
                metric_rows.extend(summarize_variant(cid, row["objective_family"], variant, spread, valid_counts, split))
        except Exception as exc:  # noqa: BLE001
            error_rows.append({"candidate_id": cid, "error": repr(exc)})

    metrics = pd.DataFrame(metric_rows)
    decisions = classify(metrics, sample) if not metrics.empty else pd.DataFrame()
    counts = decisions["decision"].value_counts().rename_axis("decision").reset_index(name="count") if not decisions.empty else pd.DataFrame(columns=["decision", "count"])
    family = (
        decisions.groupby("objective_family", dropna=False)
        .agg(
            candidate_count=("candidate_id", "count"),
            pre_may_positive_count=("pre_may_positive", "sum"),
            lag_ok_count=("lag_ok", "sum"),
            may_stress_clean_count=("may_stress_clean", "sum"),
            median_control_ratio=("control_dominance_ratio_premay_max", "median"),
        )
        .reset_index()
        if not decisions.empty
        else pd.DataFrame()
    )
    stress_clean_count = int(decisions["decision"].eq("A7AL2Z4_NUMERIC_PREFLIGHT_CLUE_STRESS_CLEAN").sum()) if not decisions.empty else 0
    pre_may_veto_count = int(decisions["decision"].eq("A7AL2Z4_PRE_MAY_CLUE_MAY_STRESS_VETOED").sum()) if not decisions.empty else 0
    pre_may_unobserved_count = int(decisions["decision"].eq("A7AL2Z4_PRE_MAY_CLUE_MAY_STRESS_UNOBSERVED").sum()) if not decisions.empty else 0
    blockers = []
    if error_rows:
        blockers.append("eval_errors")
    if stress_clean_count == 0 and pre_may_veto_count == 0 and pre_may_unobserved_count == 0:
        blockers.append("no_numeric_preflight_clues")
    decision = (
        "PASS_A7AL2Z4_BROADER_NON_OI_NUMERIC_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD"
        if not error_rows and (stress_clean_count > 0 or pre_may_veto_count > 0 or pre_may_unobserved_count > 0)
        else "HOLD_A7AL2Z4_NO_NUMERIC_PREFLIGHT_CLUES"
    )
    manifest = {
        "stage": "A7AL-2Z4",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_numeric_replay_preflight": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_full_numeric_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "candidate_count": int(len(sample)),
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_smoke_subset": full_timestamp_count,
        "hours_per_split": HOURS_PER_SPLIT,
        "metric_rows": int(len(metrics)),
        "eval_error_count": int(len(error_rows)),
        "stress_clean_clue_count": stress_clean_count,
        "pre_may_clue_may_veto_count": pre_may_veto_count,
        "pre_may_clue_may_unobserved_count": pre_may_unobserved_count,
        "blockers": blockers,
        "controls": CONTROL_VARIANTS,
        "label": "log_trade_close_t_plus_24h_minus_log_trade_close_t",
        "orientation": "train_2024_original_spread_sign_only",
        "spread_bucket_method": "cross_sectional_rank_pct_top_bottom_decile",
        "uses_may_in_selector": False,
        "uses_may_in_generation": False,
    }
    sample.to_csv(RUNTIME / "a7al2z4_replayed_candidate_sample.csv", index=False)
    metrics.to_csv(RUNTIME / "a7al2z4_candidate_variant_metrics.csv", index=False)
    decisions.to_csv(RUNTIME / "a7al2z4_candidate_decisions.csv", index=False)
    pd.DataFrame(error_rows).to_csv(RUNTIME / "a7al2z4_eval_errors.csv", index=False)
    counts.to_csv(RUNTIME / "a7al2z4_decision_counts.csv", index=False)
    family.to_csv(RUNTIME / "a7al2z4_family_decision_summary.csv", index=False)
    write_json(RUNTIME / "a7al2z4_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z4_authorization_matrix.json",
        {
            "A7AL-2Z4": {"status": decision},
            "full_numeric_replay": {"authorized": False},
            "formula_generation": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    write_report(manifest, decisions, counts, family, metrics.head(120))
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
