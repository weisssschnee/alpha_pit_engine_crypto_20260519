from __future__ import annotations

import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7aa1_primitive_response_map import horizon_label, label_family_matrix, max_control_ratio, summarize_spread  # noqa: E402
from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator  # noqa: E402
from scripts.crypto_a7al2l_fast_derived_replay_preflight import SPLIT_ORDER, split_for_timestamps  # noqa: E402
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
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import smoke_column_indices, spread_series, tstat  # noqa: E402


STAGE = os.environ.get("A7FF8_STAGE", "A7FF-8")
DECISION_PREFIX = STAGE.replace("-", "")
FILE_PREFIX = os.environ.get("A7FF8_FILE_PREFIX", DECISION_PREFIX.lower())
RUNTIME = Path(os.environ.get("A7FF8_RUNTIME", str(REPO / "runtime" / "a7ff8_expanded_numeric_probe")))
REPORT = Path(os.environ.get("A7FF8_REPORT", str(REPO / "reports" / "CRYPTO_A7FF8_EXPANDED_NUMERIC_PROBE_20260530.md")))

A7FF7E_MANIFEST = REPO / "runtime" / "a7ff7e_expanded_derivation_probe_contract" / "a7ff7e_manifest.json"
A7FF7E_QUEUE = REPO / "runtime" / "a7ff7e_expanded_derivation_probe_contract" / "a7ff7e_selected_numeric_probe_queue.csv"
A7FF7E_PLAN = REPO / "runtime" / "a7ff7e_expanded_derivation_probe_contract" / "a7ff7e_numeric_probe_plan.json"
QUEUE_PATH = Path(os.environ.get("A7FF8_QUEUE_PATH", str(A7FF7E_QUEUE)))

LABELS = [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
    "L7_ranked_future_return",
]
NON_L7_LABELS = {x for x in LABELS if x != "L7_ranked_future_return"}
HORIZONS = [1, 4, 8, 24]
PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
MATERIALIZE_CAP = int(os.environ.get("A7FF8_MATERIALIZE_CAP", "384"))
FAST_NUMERIC_CAP = int(os.environ.get("A7FF8_FAST_NUMERIC_CAP", "256"))
PORTFOLIO_CAP = int(os.environ.get("A7FF8_PORTFOLIO_CAP", "128"))
QUEUE_OFFSET = int(os.environ.get("A7FF8_QUEUE_OFFSET", "0"))
QUEUE_LIMIT = int(os.environ.get("A7FF8_QUEUE_LIMIT", "0"))
MIN_FINITE_SHARE = float(os.environ.get("A7FF8_MIN_FINITE_SHARE", "0.20"))
MIN_NONZERO_SHARE = float(os.environ.get("A7FF8_MIN_NONZERO_SHARE", "0.01"))

FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Mean",
    "Delta",
    "TSRank",
    "Decay",
    "Rank",
    "CSRank",
    "ZScore",
    "Mul",
    "Sub",
    "Add",
    "Neg",
    "Abs",
    "Sign",
    "SafeDiv",
    "Clip",
    "Winsor",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def artifact(name: str) -> Path:
    return RUNTIME / f"{FILE_PREFIX}_{name}"


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def expression_fields(expression: str) -> set[str]:
    fields: set[str] = set()
    for token in FIELD_RE.findall(str(expression)):
        if token in OPERATORS:
            continue
        if token in {"nan", "inf"}:
            continue
        fields.add(token)
    return fields


def shifted_for_control(signal: np.ndarray, name: str, rng: np.random.Generator) -> np.ndarray:
    if name == "one_bar_lag":
        return shift_matrix(signal, 1)
    if name == "wrong_lag_future_24h":
        return shift_matrix(signal, -24)
    if name == "wrong_lag_stale_168h":
        return shift_matrix(signal, 168)
    if name == "time_shuffle":
        idx = rng.permutation(signal.shape[1])
        return signal[:, idx]
    if name == "symbol_shuffle":
        idx = rng.permutation(signal.shape[0])
        return signal[idx, :]
    if name == "sign_flip":
        return -signal
    if name == "same_family_placebo":
        return rng.normal(size=signal.shape)
    raise ValueError(name)


def nonoverlap_floor(summary: dict[str, Any], orientation: float, suffix: str) -> float:
    vals: list[float] = []
    for split_name in PRE_MAY_SPLITS:
        value = summary.get(f"{split_name}_{suffix}", np.nan)
        if np.isfinite(value):
            vals.append(float(orientation) * float(value))
    return float(np.nanmin(vals)) if vals else np.nan


def split_oriented(summary: dict[str, Any], split_name: str, orientation: float) -> float:
    value = summary.get(f"{split_name}_mean_spread", np.nan)
    return orientation * float(value) if np.isfinite(value) else np.nan


def classify_label_response(
    candidate: dict[str, Any],
    signal: np.ndarray,
    label: np.ndarray,
    split: np.ndarray,
    horizon: int,
    label_family: str,
    rng: np.random.Generator,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    spread, valid_counts = spread_series(signal, label)
    summary = summarize_spread(spread, split, horizon)
    train_mean = summary.get("train_2024_mean_spread", np.nan)
    orientation = 1.0 if not np.isfinite(train_mean) or train_mean >= 0 else -1.0
    oriented = {name: split_oriented(summary, name, orientation) for name in ["train_2024", *PRE_MAY_SPLITS]}
    premay_positive_count = int(sum(np.isfinite(oriented[s]) and oriented[s] > 0 for s in PRE_MAY_SPLITS))
    premay_all_positive = premay_positive_count == len(PRE_MAY_SPLITS)

    control_rows: list[dict[str, Any]] = []
    control_spreads_for_ratio: dict[str, np.ndarray] = {}
    for control in [
        "one_bar_lag",
        "wrong_lag_future_24h",
        "wrong_lag_stale_168h",
        "time_shuffle",
        "symbol_shuffle",
        "sign_flip",
        "same_family_placebo",
    ]:
        ctrl_signal = shifted_for_control(signal, control, rng)
        ctrl_spread, _ = spread_series(ctrl_signal, label)
        if control not in {"one_bar_lag", "sign_flip"}:
            control_spreads_for_ratio[control] = ctrl_spread
        for split_name in PRE_MAY_SPLITS:
            mask = (split == split_name) & np.isfinite(ctrl_spread)
            ctrl_mean = float(np.nanmean(ctrl_spread[mask])) if mask.any() else np.nan
            orig_abs = abs(oriented.get(split_name, np.nan))
            ctrl_oriented = orientation * ctrl_mean if np.isfinite(ctrl_mean) else np.nan
            ratio = abs(ctrl_oriented) / orig_abs if np.isfinite(ctrl_oriented) and np.isfinite(orig_abs) and orig_abs > 1e-12 else np.nan
            control_rows.append(
                {
                    "blueprint_id": candidate["blueprint_id"],
                    "label_family": label_family,
                    "label_horizon_h": horizon,
                    "control": control,
                    "split": split_name,
                    "control_oriented_mean_spread": ctrl_oriented,
                    "control_ratio_to_original": ratio,
                }
            )
    control_ratio = max_control_ratio(oriented, control_spreads_for_ratio, orientation, split)

    lag_recent = next(
        (
            row["control_oriented_mean_spread"]
            for row in control_rows
            if row["control"] == "one_bar_lag" and row["split"] == "recent_oos_2026JanApr"
        ),
        np.nan,
    )
    recent = oriented["recent_oos_2026JanApr"]
    lag_ok = np.isfinite(recent) and np.isfinite(lag_recent) and lag_recent > 0 and abs(lag_recent) >= 0.25 * abs(recent)
    robust_median_floor = nonoverlap_floor(summary, orientation, "nonoverlap_median_tstat")
    robust_min_floor = nonoverlap_floor(summary, orientation, "nonoverlap_min_tstat")
    robust_ok = np.isfinite(robust_median_floor) and robust_median_floor > 0
    cost2_recent = recent - (2 * 2 / 10000) if np.isfinite(recent) else np.nan
    cost5_recent = recent - (2 * 5 / 10000) if np.isfinite(recent) else np.nan
    cost10_recent = recent - (2 * 10 / 10000) if np.isfinite(recent) else np.nan

    if not premay_all_positive:
        decision = f"HOLD_{DECISION_PREFIX}_PRE_MAY_UNSTABLE"
    elif np.isfinite(control_ratio) and control_ratio >= 1.0:
        decision = f"HOLD_{DECISION_PREFIX}_CONTROL_DOMINATED"
    elif not lag_ok:
        decision = f"HOLD_{DECISION_PREFIX}_ONE_BAR_LAG_FRAGILE"
    elif not robust_ok:
        decision = f"HOLD_{DECISION_PREFIX}_NONOVERLAP_WEAK"
    elif not np.isfinite(cost2_recent) or cost2_recent <= 0:
        decision = f"HOLD_{DECISION_PREFIX}_COST2_PROXY_FRAGILE"
    elif label_family == "L7_ranked_future_return":
        decision = f"{DECISION_PREFIX}_RANK_LABEL_DIAGNOSTIC_CLUE"
    else:
        decision = f"{DECISION_PREFIX}_NUMERIC_CLUE"

    response = {
        "blueprint_id": candidate["blueprint_id"],
        "expression": candidate["expression"],
        "semantic_pair": candidate["semantic_pair"],
        "motif": candidate["motif"],
        "label_family": label_family,
        "label_horizon_h": horizon,
        "orientation_from_train": orientation,
        "premay_positive_split_count": premay_positive_count,
        "premay_all_positive": premay_all_positive,
        "control_ratio_premay_max": control_ratio,
        "one_bar_lag_recent_oriented": lag_recent,
        "lag_ok": lag_ok,
        "robust_median_tstat_floor": robust_median_floor,
        "robust_min_tstat_floor": robust_min_floor,
        "robust_ok": robust_ok,
        "cost2_recent_oriented": cost2_recent,
        "cost5_recent_oriented": cost5_recent,
        "cost10_recent_oriented": cost10_recent,
        "avg_n_obs_recent": float(np.nanmean(valid_counts[(split == "recent_oos_2026JanApr")])) if np.any(split == "recent_oos_2026JanApr") else np.nan,
        "decision": decision,
    }
    for key, value in summary.items():
        response[key] = value

    nonoverlap = {
        "blueprint_id": candidate["blueprint_id"],
        "label_family": label_family,
        "label_horizon_h": horizon,
        "orientation_from_train": orientation,
        "robust_median_tstat_floor": robust_median_floor,
        "robust_min_tstat_floor": robust_min_floor,
        "robust_ok": robust_ok,
    }
    return response, control_rows, nonoverlap


def portfolio_proxy(responses: pd.DataFrame, materialized: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    usable = responses[
        responses["decision"].isin([f"{DECISION_PREFIX}_NUMERIC_CLUE", f"{DECISION_PREFIX}_RANK_LABEL_DIAGNOSTIC_CLUE"])
    ].copy()
    if usable.empty:
        empty = pd.DataFrame()
        return empty, empty
    usable["non_l7_bonus"] = usable["label_family"].ne("L7_ranked_future_return").astype(float)
    usable["score_no_may"] = (
        usable["non_l7_bonus"]
        + usable["premay_positive_split_count"].astype(float)
        + usable["lag_ok"].astype(float)
        + usable["robust_ok"].astype(float)
        + (1.0 - pd.to_numeric(usable["control_ratio_premay_max"], errors="coerce").clip(upper=1.0)).fillna(0.0)
        + pd.to_numeric(usable["cost5_recent_oriented"], errors="coerce").fillna(0.0).clip(lower=0.0) * 1000.0
    )
    best = usable.sort_values(["score_no_may", "blueprint_id"], ascending=[False, True]).drop_duplicates("blueprint_id")
    best = best.merge(
        materialized[["blueprint_id", "skeleton_key", "finite_share", "nonzero_share"]],
        on="blueprint_id",
        how="left",
    )
    selected_rows = []
    used_semantic: dict[str, int] = {}
    used_motif: dict[str, int] = {}
    used_skeleton: set[str] = set()
    for row in best.itertuples(index=False):
        if row.skeleton_key in used_skeleton:
            continue
        if used_semantic.get(row.semantic_pair, 0) >= 24:
            continue
        if used_motif.get(row.motif, 0) >= 32:
            continue
        selected_rows.append(row._asdict())
        used_skeleton.add(row.skeleton_key)
        used_semantic[row.semantic_pair] = used_semantic.get(row.semantic_pair, 0) + 1
        used_motif[row.motif] = used_motif.get(row.motif, 0) + 1
        if len(selected_rows) >= PORTFOLIO_CAP:
            break
    selected = pd.DataFrame(selected_rows)
    return best, selected


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    a7ff7e = read_json(A7FF7E_MANIFEST)
    if not a7ff7e.get("authorizes_a7ff8_numeric_probe_contract"):
        raise SystemExit(f"A7FF-7E does not authorize {STAGE} numeric probe")
    plan = read_json(A7FF7E_PLAN)
    queue_all = pd.read_csv(QUEUE_PATH)
    queue = queue_all.copy()
    if QUEUE_OFFSET:
        queue = queue.iloc[QUEUE_OFFSET:].copy()
    if QUEUE_LIMIT:
        queue = queue.head(QUEUE_LIMIT).copy()
    elif MATERIALIZE_CAP:
        queue = queue.head(MATERIALIZE_CAP).copy()
    if FAST_NUMERIC_CAP and len(queue) > FAST_NUMERIC_CAP:
        # Keep diversity: first pass by semantic pair/motif before truncation.
        rows = []
        for _, group in queue.groupby(["semantic_pair", "motif"], sort=False):
            rows.append(group.head(max(1, FAST_NUMERIC_CAP // max(1, queue[["semantic_pair", "motif"]].drop_duplicates().shape[0]))))
        sampled = pd.concat(rows, ignore_index=True).drop_duplicates("blueprint_id")
        if len(sampled) < FAST_NUMERIC_CAP:
            extra = queue[~queue["blueprint_id"].isin(set(sampled["blueprint_id"]))].head(FAST_NUMERIC_CAP - len(sampled))
            sampled = pd.concat([sampled, extra], ignore_index=True)
        queue = sampled.head(FAST_NUMERIC_CAP).copy()

    fields = {"trade_close", "realized_vol_168h"}
    for expr in queue["expression"].astype(str):
        fields.update(expression_fields(expr))
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_fields = {field for field in fields if field in base_schema}
    latent_fields = {field for field in fields if field in latent_schema and field not in base_fields}
    missing = sorted(fields - base_fields - latent_fields)

    blockers: list[str] = []
    material_rows: list[dict[str, Any]] = []
    response_rows: list[dict[str, Any]] = []
    control_rows: list[dict[str, Any]] = []
    nonoverlap_rows: list[dict[str, Any]] = []
    if missing:
        blockers.append("missing_numeric_fields")
    else:
        symbols = strict_symbols()
        print(f"[{STAGE}] loading symbols={len(symbols)}, base_fields={len(base_fields)}, latent_fields={len(latent_fields)}", flush=True)
        loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
        numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
        groups = load_group_fields(loaded_symbols, timestamps, {"liquidity_tier"})
        full_timestamp_count = int(len(timestamps))
        idx = smoke_column_indices(timestamps)
        timestamps = pd.DatetimeIndex(timestamps[idx])
        numeric = {key: value[:, idx] for key, value in numeric.items()}
        groups = {key: value[:, idx] for key, value in groups.items()}
        split = split_for_timestamps(timestamps)
        vol = numeric.get("realized_vol_168h", np.full_like(numeric["trade_close"], np.nan))
        liquidity_tier = groups["liquidity_tier"]
        raw_labels = {h: horizon_label(numeric["trade_close"], timestamps, split, h) for h in HORIZONS}
        label_mats = {
            (label_family, horizon): label_family_matrix(raw, label_family, vol, liquidity_tier)
            for horizon, raw in raw_labels.items()
            for label_family in LABELS
        }
        evaluator = A7AB4Evaluator(numeric, groups)
        rng = np.random.default_rng(20260530)
        print(f"[{STAGE}] evaluating blueprints={len(queue)}, timestamps={len(timestamps)}, full_timestamps={full_timestamp_count}", flush=True)
        for idx_row, row in enumerate(queue.to_dict("records"), start=1):
            expr = str(row["expression"])
            try:
                signal = evaluator.eval(expr)
                finite = np.isfinite(signal)
                finite_share = float(finite.mean()) if signal.size else 0.0
                nonzero_share = float((np.abs(signal[finite]) > 1e-12).mean()) if finite.any() else 0.0
                eval_success = True
                error = ""
                min_value = float(np.nanmin(signal)) if finite.any() else np.nan
                max_value = float(np.nanmax(signal)) if finite.any() else np.nan
                std_value = float(np.nanstd(signal)) if finite.any() else np.nan
            except Exception as exc:  # noqa: BLE001
                signal = np.empty((0, 0))
                finite_share = 0.0
                nonzero_share = 0.0
                eval_success = False
                error = repr(exc)
                min_value = max_value = std_value = np.nan
            activity_ok = eval_success and finite_share >= MIN_FINITE_SHARE and nonzero_share >= MIN_NONZERO_SHARE
            material_rows.append(
                {
                    "blueprint_id": row["blueprint_id"],
                    "expression": expr,
                    "semantic_pair": row.get("semantic_pair", ""),
                    "motif": row.get("motif", ""),
                    "skeleton_key": row.get("skeleton_key", ""),
                    "eval_success": eval_success,
                    "finite_share": finite_share,
                    "nonzero_share": nonzero_share,
                    "activity_ok": activity_ok,
                    "min_value": min_value,
                    "max_value": max_value,
                    "std_value": std_value,
                    "error": error,
                }
            )
            if activity_ok:
                for (label_family, horizon), label in label_mats.items():
                    response, controls, nonoverlap = classify_label_response(row, signal, label, split, horizon, label_family, rng)
                    response_rows.append(response)
                    control_rows.extend(controls)
                    nonoverlap_rows.append(nonoverlap)
            if idx_row % 32 == 0:
                print(f"[{STAGE}] evaluated {idx_row}/{len(queue)}", flush=True)

    materialized = pd.DataFrame(material_rows)
    responses = pd.DataFrame(response_rows)
    controls = pd.DataFrame(control_rows)
    nonoverlap = pd.DataFrame(nonoverlap_rows)
    portfolio_all, portfolio_selected = portfolio_proxy(responses, materialized) if not responses.empty else (pd.DataFrame(), pd.DataFrame())

    decision_counts = (
        responses.groupby(["decision", "label_family"], dropna=False).size().reset_index(name="count")
        if not responses.empty
        else pd.DataFrame(columns=["decision", "label_family", "count"])
    )
    family_summary = (
        responses.groupby(["semantic_pair", "decision"], dropna=False).size().reset_index(name="count")
        if not responses.empty
        else pd.DataFrame(columns=["semantic_pair", "decision", "count"])
    )
    control_summary = (
        controls.groupby(["control"], dropna=False)
        .agg(median_ratio=("control_ratio_to_original", "median"), max_ratio=("control_ratio_to_original", "max"), rows=("blueprint_id", "count"))
        .reset_index()
        if not controls.empty
        else pd.DataFrame(columns=["control", "median_ratio", "max_ratio", "rows"])
    )

    clue_count = int((responses["decision"] == f"{DECISION_PREFIX}_NUMERIC_CLUE").sum()) if not responses.empty else 0
    rank_clue_count = int((responses["decision"] == f"{DECISION_PREFIX}_RANK_LABEL_DIAGNOSTIC_CLUE").sum()) if not responses.empty else 0
    materialized_count = int(materialized["activity_ok"].sum()) if not materialized.empty else 0
    if missing:
        decision = f"HOLD_{DECISION_PREFIX}_MISSING_FIELDS"
    elif materialized_count == 0:
        decision = f"HOLD_{DECISION_PREFIX}_NO_ACTIVITY_OK_BLUEPRINTS"
        blockers.append("no_activity_ok_blueprints")
    elif clue_count == 0:
        decision = f"HOLD_{DECISION_PREFIX}_NO_NON_L7_NUMERIC_CLUES"
        blockers.append("no_non_l7_numeric_clues")
    elif len(portfolio_selected) < 4:
        decision = f"HOLD_{DECISION_PREFIX}_PORTFOLIO_QUEUE_TOO_SMALL"
        blockers.append("portfolio_selected_lt_4")
    else:
        decision = f"PASS_{DECISION_PREFIX}_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH"

    materialized.to_csv(artifact("materialization_metrics.csv"), index=False)
    responses.to_csv(artifact("label_response_metrics.csv"), index=False)
    controls.to_csv(artifact("control_dominance_metrics.csv"), index=False)
    nonoverlap.to_csv(artifact("nonoverlap_stats.csv"), index=False)
    portfolio_all.to_csv(artifact("portfolio_marginal_proxy.csv"), index=False)
    portfolio_selected.to_csv(artifact("selected_portfolio_queue.csv"), index=False)
    decision_counts.to_csv(artifact("decision_counts.csv"), index=False)
    family_summary.to_csv(artifact("family_decision_summary.csv"), index=False)
    control_summary.to_csv(artifact("control_summary.csv"), index=False)

    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": sorted(set(blockers)),
        "executes_generation": False,
        "executes_numeric_probe": True,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "input_blueprint_count": int(len(queue)),
        "queue_path": str(QUEUE_PATH),
        "queue_total_rows": int(len(queue_all)),
        "queue_offset": QUEUE_OFFSET,
        "queue_limit": QUEUE_LIMIT,
        "materialized_activity_ok_count": materialized_count,
        "label_response_rows": int(len(responses)),
        "non_l7_numeric_clue_rows": clue_count,
        "rank_label_diagnostic_clue_rows": rank_clue_count,
        "portfolio_queue_count": int(len(portfolio_all)),
        "selected_portfolio_queue_count": int(len(portfolio_selected)),
        "plan": plan,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(artifact("decision_record.json"), manifest)
    write_json(artifact("manifest.json"), manifest)

    lines = [
        f"# CRYPTO {STAGE} EXPANDED NUMERIC PROBE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        f"{STAGE} materializes the A7FF-7E selected blueprint queue and evaluates label response, controls, non-overlap statistics, and a dry portfolio marginal proxy. It is not formula search or alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Decision Counts",
        "",
        md_table(decision_counts, 80),
        "",
        "## Family Summary",
        "",
        md_table(family_summary, 80),
        "",
        "## Control Summary",
        "",
        md_table(control_summary, 80),
        "",
        "## Selected Portfolio Queue",
        "",
        md_table(portfolio_selected[["factor_blueprint_id", "blueprint_id", "label_family", "label_horizon_h", "semantic_pair", "motif", "score_no_may"]] if not portfolio_selected.empty and "factor_blueprint_id" in portfolio_selected.columns else portfolio_selected, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "No May/post-selection stress is used in scoring or authorization.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "L7 ranked-return rows remain diagnostic-only and cannot promote without non-L7 support.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
