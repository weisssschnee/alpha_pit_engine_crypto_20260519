from __future__ import annotations

import json
import math
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

from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator  # noqa: E402
from scripts.crypto_a7ae1_label_adequacy_response_map import (  # noqa: E402
    PRE_MAY_SPLITS,
    horizon_label,
    label_family_matrix,
    max_control_ratio,
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
    shift_matrix,
    strict_symbols,
)
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import smoke_column_indices, spread_series  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ag3_numeric_replay_pilot"
REPORT = REPO / "reports" / "CRYPTO_A7AG3_NUMERIC_REPLAY_PILOT_20260529.md"

A7AG2_MANIFEST = REPO / "runtime" / "a7ag2_numeric_replay_contract" / "a7ag2_manifest.json"
A7AG2_QUEUE = REPO / "runtime" / "a7ag2_numeric_replay_contract" / "a7ag2_numeric_replay_queue.csv"

MIN_FINITE_SHARE = 0.20
MIN_NONZERO_SHARE = 0.01
CONTROL_VARIANTS = ["wrong_lag_future_24h", "wrong_lag_stale_168h", "same_family_random"]
PILOT_COST_BPS = 5
TRACK_PASS_MIN_CLUES = {
    "G0_ordinary_alpha_basis_premium": 2,
    "G1_neutralized_alpha_diagnostic": 3,
    "G2_downside_risk_defense": 4,
}
NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")


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


def split_pipe(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


class A7AG3Evaluator(A7AB4Evaluator):
    """A bounded pilot evaluator.

    A7AG blueprints may contain scalar constants such as 0.01. The shared array
    evaluator is intentionally field-only, so this pilot adds scalar literals
    locally without changing global evaluator semantics.
    """

    def __init__(self, numeric_fields: dict[str, np.ndarray], group_fields: dict[str, np.ndarray]) -> None:
        super().__init__(numeric_fields, group_fields)
        if not numeric_fields:
            raise ValueError("numeric_fields cannot be empty")
        first = next(iter(numeric_fields.values()))
        self.shape = first.shape

    def _eval(self, expression: str) -> np.ndarray:
        text = expression.strip()
        if NUMBER_RE.match(text):
            return np.full(self.shape, float(text), dtype=np.float64)
        return super()._eval(text)


def selected_fields(queue: pd.DataFrame) -> set[str]:
    fields = {"trade_close", "realized_vol_168h"}
    for text in queue["source_fields"].dropna().astype(str):
        fields.update(split_pipe(text))
    return fields


def subset_columns(
    timestamps: pd.DatetimeIndex,
    numeric: dict[str, np.ndarray],
    groups: dict[str, np.ndarray],
) -> tuple[pd.DatetimeIndex, dict[str, np.ndarray], dict[str, np.ndarray], int]:
    full_timestamp_count = int(len(timestamps))
    idx = smoke_column_indices(timestamps)
    return (
        pd.DatetimeIndex(timestamps[idx]),
        {key: value[:, idx] for key, value in numeric.items()},
        {key: value[:, idx] for key, value in groups.items()},
        full_timestamp_count,
    )


def nonoverlap_floor(summary: dict[str, Any], orientation: float, suffix: str) -> float:
    values: list[float] = []
    for split_name in PRE_MAY_SPLITS:
        value = summary.get(f"{split_name}_{suffix}", np.nan)
        if np.isfinite(value):
            values.append(float(orientation) * float(value))
    return float(np.nanmin(values)) if values else np.nan


def classify_candidate(
    row: dict[str, Any],
    signal: np.ndarray,
    label: np.ndarray,
    split: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, Any]:
    spread, valid_counts = spread_series(signal, label)
    summary = summarize_spread(spread, split, int(row["label_horizon_h"]))
    train_mean = summary.get("train_2024_mean_spread", np.nan)
    orientation = 1.0 if not np.isfinite(train_mean) or train_mean >= 0 else -1.0
    oriented = {
        split_name: orientation * float(summary.get(f"{split_name}_mean_spread", np.nan))
        for split_name in ["train_2024", *PRE_MAY_SPLITS]
    }
    pre_may_positive_count = int(sum(np.isfinite(oriented[s]) and oriented[s] > 0 for s in PRE_MAY_SPLITS))
    pre_may_positive_all = pre_may_positive_count == len(PRE_MAY_SPLITS)

    lag_spread, _ = spread_series(shift_matrix(signal, 1), label)
    lag_recent_mask = (split == "recent_oos_2026JanApr") & np.isfinite(lag_spread)
    lag_recent = orientation * float(np.nanmean(lag_spread[lag_recent_mask])) if lag_recent_mask.any() else np.nan
    recent = oriented["recent_oos_2026JanApr"]
    lag_ok = np.isfinite(recent) and np.isfinite(lag_recent) and lag_recent > 0 and abs(lag_recent) >= 0.25 * abs(recent)

    control_spreads: dict[str, np.ndarray] = {}
    control_spreads["wrong_lag_future_24h"], _ = spread_series(shift_matrix(signal, -24), label)
    control_spreads["wrong_lag_stale_168h"], _ = spread_series(shift_matrix(signal, 168), label)
    control_spreads["same_family_random"], _ = spread_series(rng.normal(size=signal.shape), label)
    control_ratio = max_control_ratio(oriented, control_spreads, orientation, split)
    control_clean = not (np.isfinite(control_ratio) and control_ratio >= 1.0)

    robust_median_floor = nonoverlap_floor(summary, orientation, "nonoverlap_median_tstat")
    robust_min_floor = nonoverlap_floor(summary, orientation, "nonoverlap_min_tstat")
    robust_ok = np.isfinite(robust_median_floor) and robust_median_floor > 0

    cost5_recent = recent - (2 * PILOT_COST_BPS / 10000)
    cost10_recent = recent - (2 * 10 / 10000)
    cost20_recent = recent - (2 * 20 / 10000)
    cost_proxy_ok = np.isfinite(cost5_recent) and cost5_recent > 0

    if not pre_may_positive_all:
        decision = "HOLD_A7AG3_PRE_MAY_UNSTABLE"
    elif not control_clean:
        decision = "HOLD_A7AG3_CONTROL_DOMINATED"
    elif not lag_ok:
        decision = "HOLD_A7AG3_ONE_BAR_LAG_FRAGILE"
    elif not robust_ok:
        decision = "HOLD_A7AG3_NONOVERLAP_WEAK"
    elif not cost_proxy_ok:
        decision = "HOLD_A7AG3_COST5_PROXY_FRAGILE"
    else:
        decision = "A7AG3_NUMERIC_REPLAY_CLUE"

    result = {
        "orientation_from_train": orientation,
        "premay_positive_split_count": pre_may_positive_count,
        "premay_all_positive": pre_may_positive_all,
        "control_ratio_premay_max": control_ratio,
        "control_clean": control_clean,
        "one_bar_lag_recent_oriented": lag_recent,
        "lag_ok": lag_ok,
        "robust_median_tstat_floor": robust_median_floor,
        "robust_min_tstat_floor": robust_min_floor,
        "robust_ok": robust_ok,
        "cost5_recent_oriented": cost5_recent,
        "cost10_recent_oriented": cost10_recent,
        "cost20_recent_oriented": cost20_recent,
        "cost_proxy_ok": cost_proxy_ok,
        "decision": decision,
        "avg_n_obs_recent": float(np.nanmean(valid_counts[(split == "recent_oos_2026JanApr")])) if np.any(split == "recent_oos_2026JanApr") else np.nan,
    }
    for key, value in summary.items():
        result[key] = value
    return result


def write_report(manifest: dict[str, Any], track_summary: pd.DataFrame, decision_counts: pd.DataFrame, clues: pd.DataFrame, control_summary: pd.DataFrame) -> None:
    lines = [
        "# CRYPTO A7AG-3 NUMERIC REPLAY PILOT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "A7AG-3 executes a bounded numeric pilot for the role-aware A7AG replay queue. It is not formula search, not training, and not alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Track Summary",
        "",
        md_table(track_summary),
        "",
        "## Decision Counts",
        "",
        md_table(decision_counts),
        "",
        "## Replay Clues",
        "",
        md_table(clues, 80),
        "",
        "## Control Summary",
        "",
        md_table(control_summary),
        "",
        "## Boundary",
        "",
        "```text",
        "May is not used in labels, ranking, selector score, mutation, or authorization.",
        "A7AG-3 uses a 5bps pilot cost proxy only; 10/20bps fields are reported but not a pilot hard gate.",
        "Formula search, large search, alpha proof, shadow, paper, and live remain not authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ag2 = read_json(A7AG2_MANIFEST)
    if not a7ag2.get("authorizes_a7ag3_numeric_replay_pilot"):
        raise SystemExit("A7AG-2 does not authorize A7AG-3")

    queue = pd.read_csv(A7AG2_QUEUE)
    fields = selected_fields(queue)
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_fields = {field for field in fields if field in base_schema}
    latent_fields = {field for field in fields if field in latent_schema and field not in base_fields}
    missing = sorted(fields - base_fields - latent_fields)

    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_fields))
    groups = load_group_fields(loaded_symbols, timestamps, {"liquidity_tier"})
    timestamps, numeric, groups, full_timestamp_count = subset_columns(timestamps, numeric, groups)
    split = split_for_timestamps(timestamps)

    if missing:
        rows = [
            {
                "candidate_id": row["candidate_id"],
                "track_id": row["track_id"],
                "decision": "HOLD_A7AG3_MISSING_FIELD",
                "error": "|".join(missing),
            }
            for row in queue.to_dict("records")
        ]
        metrics = pd.DataFrame(rows)
    else:
        evaluator = A7AG3Evaluator(numeric, {})
        raw_labels = {
            int(horizon): horizon_label(numeric["trade_close"], timestamps, split, int(horizon))
            for horizon in sorted(queue["label_horizon_h"].dropna().astype(int).unique())
        }
        vol = numeric.get("realized_vol_168h", np.full_like(numeric["trade_close"], np.nan))
        liquidity_tier = groups["liquidity_tier"]
        label_cache: dict[tuple[str, int], np.ndarray] = {}
        label_meta: dict[tuple[str, int], dict[str, Any]] = {}
        for row in queue.to_dict("records"):
            key = (str(row["label_family"]), int(row["label_horizon_h"]))
            if key not in label_cache:
                label_cache[key], label_meta[key] = label_family_matrix(
                    raw_labels[key[1]],
                    key[0],
                    loaded_symbols,
                    split,
                    vol,
                    liquidity_tier,
                )

        rng = np.random.default_rng(20260529)
        rows: list[dict[str, Any]] = []
        for index, row in enumerate(queue.to_dict("records"), start=1):
            expression = str(row["expression"])
            base: dict[str, Any] = {
                "candidate_id": row["candidate_id"],
                "replay_rank": row["replay_rank"],
                "track_id": row["track_id"],
                "selector_tier": row["selector_tier"],
                "blueprint_family": row["blueprint_family"],
                "variant_name": row["variant_name"],
                "seed_field": row["seed_field"],
                "interaction_field": row["interaction_field"],
                "field_family": row["field_family"],
                "feature_role": row["feature_role"],
                "label_family": row["label_family"],
                "label_horizon_h": int(row["label_horizon_h"]),
                "skeleton_key": row["skeleton_key"],
                "production_key": row["production_key"],
                "source_fields": row["source_fields"],
                "expression": expression,
                "eval_success": False,
                "finite_share": 0.0,
                "nonzero_share": 0.0,
                "activity_ok": False,
                "error": "",
            }
            try:
                signal = evaluator.eval(expression)
                finite = np.isfinite(signal)
                finite_share = float(finite.mean()) if signal.size else 0.0
                nonzero_share = float((np.abs(signal[finite]) > 1e-12).mean()) if finite.any() else 0.0
                activity_ok = finite_share >= MIN_FINITE_SHARE and nonzero_share >= MIN_NONZERO_SHARE
                base.update(
                    {
                        "eval_success": True,
                        "finite_share": finite_share,
                        "nonzero_share": nonzero_share,
                        "activity_ok": activity_ok,
                    }
                )
                if not activity_ok:
                    base.update({"decision": "HOLD_A7AG3_ACTIVITY_OR_COVERAGE_FAILURE"})
                else:
                    label = label_cache[(str(row["label_family"]), int(row["label_horizon_h"]))]
                    base.update(classify_candidate(row, signal, label, split, rng))
            except Exception as exc:  # noqa: BLE001 - pilot must record all evaluator failures.
                base.update({"decision": "HOLD_A7AG3_EVAL_FAILURE", "error": repr(exc)})
            rows.append(base)
            if index % 24 == 0:
                print(f"[A7AG-3] evaluated {index}/{len(queue)}", flush=True)
        metrics = pd.DataFrame(rows)

    clues = metrics[metrics["decision"].eq("A7AG3_NUMERIC_REPLAY_CLUE")].copy()
    decision_counts = metrics["decision"].value_counts().rename_axis("decision").reset_index(name="count")
    track_summary = (
        metrics.groupby("track_id", dropna=False)
        .agg(
            evaluated=("candidate_id", "count"),
            eval_success=("eval_success", "sum"),
            activity_ok=("activity_ok", "sum"),
            clue_count=("decision", lambda s: int((s == "A7AG3_NUMERIC_REPLAY_CLUE").sum())),
            pre_may_all_positive=("premay_all_positive", "sum"),
            control_clean=("control_clean", "sum"),
            lag_ok=("lag_ok", "sum"),
            robust_ok=("robust_ok", "sum"),
            cost_proxy_ok=("cost_proxy_ok", "sum"),
            unique_seed_fields=("seed_field", "nunique"),
            unique_skeletons=("skeleton_key", "nunique"),
        )
        .reset_index()
        if not metrics.empty
        else pd.DataFrame()
    )
    if not track_summary.empty:
        track_summary["track_pass_min_clues"] = track_summary["track_id"].map(TRACK_PASS_MIN_CLUES).fillna(math.inf).astype(float)
        track_summary["track_pilot_pass"] = track_summary["clue_count"] >= track_summary["track_pass_min_clues"]

    control_summary = (
        metrics.groupby("track_id", dropna=False)
        .agg(
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_control_ratio=("control_ratio_premay_max", "max"),
            control_dominated=("control_clean", lambda s: int((~s.fillna(False).astype(bool)).sum())),
        )
        .reset_index()
        if "control_ratio_premay_max" in metrics.columns
        else pd.DataFrame()
    )

    passed_tracks = track_summary.loc[track_summary.get("track_pilot_pass", pd.Series(dtype=bool)).astype(bool), "track_id"].tolist() if not track_summary.empty else []
    total_clues = int(len(clues))
    if passed_tracks:
        decision = "PASS_A7AG3_NUMERIC_REPLAY_PILOT_CLUES_FOUND_EXECUTION_STILL_HOLD"
    elif total_clues > 0:
        decision = "HOLD_A7AG3_CLUES_BELOW_TRACK_PASS_MINIMUM"
    else:
        decision = "HOLD_A7AG3_NO_NUMERIC_REPLAY_CLUES"

    manifest = {
        "stage": "A7AG-3",
        "generated_at": now_utc(),
        "decision": decision,
        "input_a7ag2_decision": a7ag2.get("decision"),
        "executes_numeric_replay_pilot": True,
        "executes_formula_search": False,
        "executes_training": False,
        "authorizes_a7ag4_forensic_contract": total_clues > 0,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "pilot_cost_bps_gate": PILOT_COST_BPS,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_subset": full_timestamp_count,
        "queue_count": int(len(queue)),
        "evaluated_count": int(len(metrics)),
        "clue_count": total_clues,
        "passed_tracks": passed_tracks,
        "missing_fields": missing,
        "base_field_count": int(len(base_fields)),
        "latent_field_count": int(len(latent_fields)),
    }

    metrics.to_csv(RUNTIME / "a7ag3_candidate_replay_metrics.csv", index=False)
    clues.to_csv(RUNTIME / "a7ag3_replay_clues.csv", index=False)
    track_summary.to_csv(RUNTIME / "a7ag3_track_summary.csv", index=False)
    decision_counts.to_csv(RUNTIME / "a7ag3_decision_counts.csv", index=False)
    control_summary.to_csv(RUNTIME / "a7ag3_control_summary.csv", index=False)
    write_json(RUNTIME / "a7ag3_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ag3_authorization_matrix.json",
        {
            "A7AG-3": {"status": decision},
            "a7ag4_forensic_contract": {"authorized": bool(manifest["authorizes_a7ag4_forensic_contract"])},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    write_report(manifest, track_summary, decision_counts, clues, control_summary)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
