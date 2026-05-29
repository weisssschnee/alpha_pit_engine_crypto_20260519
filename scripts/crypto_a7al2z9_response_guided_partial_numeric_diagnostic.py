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
from scripts.crypto_a7al2z2_broader_non_oi_materialization_audit import expression_group_fields  # noqa: E402
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402
from scripts.crypto_a7al2z5_broader_non_oi_multi_horizon_diagnostic import (  # noqa: E402
    LABEL_HORIZONS,
    classify,
    horizon_label,
    md_table,
    selected_fields,
    shifted_groups,
    shifted_numeric,
    smoke_column_indices,
    spread_series,
    summarize_variant,
)
from scripts.crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402


RUNTIME = REPO / "runtime" / "a7al2z9_response_guided_partial_numeric_diagnostic"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z9_RESPONSE_GUIDED_PARTIAL_NUMERIC_DIAGNOSTIC_20260529.md"
Z8P_MANIFEST = REPO / "runtime" / "a7al2z8p_partial_viable_queue_authorization" / "a7al2z8p_manifest.json"
Z8P_SELECTED = REPO / "runtime" / "a7al2z8p_partial_viable_queue_authorization" / "a7al2z8p_partial_viable_candidates.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def split_pipe(value: Any) -> list[str]:
    if pd.isna(value):
        return []
    return [x for x in str(value).split("|") if x]


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    z8p = read_json(Z8P_MANIFEST)
    if not z8p.get("authorizes_a7al2z9_partial_numeric_diagnostic"):
        raise SystemExit("A7AL-2Z8P does not authorize Z9")
    sample = pd.read_csv(Z8P_SELECTED).sort_values(["objective_family", "skeleton_key", "candidate_id"]).reset_index(drop=True)
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
        raise SystemExit(f"missing numeric fields for Z9: {missing_numeric_fields}")

    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_numeric_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_numeric_fields))
    groups = load_group_fields(loaded_symbols, timestamps, group_fields)
    full_timestamp_count = int(len(timestamps))
    idx = smoke_column_indices(timestamps)
    timestamps = pd.DatetimeIndex(timestamps[idx])
    numeric = {key: value[:, idx] for key, value in numeric.items()}
    groups = {key: value[:, idx] for key, value in groups.items()}
    split = split_for_timestamps(timestamps)
    labels = {horizon: horizon_label(numeric["trade_close"], timestamps, split, horizon) for horizon in LABEL_HORIZONS}

    original_eval = StateAwareEvaluator(numeric, groups)
    future_eval = StateAwareEvaluator(shifted_numeric(numeric, -24), shifted_groups(groups, -24))
    stale_eval = StateAwareEvaluator(shifted_numeric(numeric, 168), shifted_groups(groups, 168))
    rng = np.random.default_rng(20260529)

    metric_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    for i, row in enumerate(sample.to_dict("records"), start=1):
        cid = row["candidate_id"]
        expr = row["expression"]
        print(f"[A7AL-2Z9] {i}/{len(sample)} {cid}", flush=True)
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
            for horizon, label in labels.items():
                for variant, variant_signal in variants.items():
                    spread, valid_counts = spread_series(variant_signal, label)
                    metric_rows.extend(summarize_variant(cid, row["objective_family"], horizon, variant, spread, valid_counts, split))
        except Exception as exc:  # noqa: BLE001
            error_rows.append({"candidate_id": cid, "error": repr(exc)})

    metrics = pd.DataFrame(metric_rows)
    decisions = classify(metrics, sample) if not metrics.empty else pd.DataFrame()
    if not decisions.empty:
        decisions["decision"] = decisions["decision"].astype(str).str.replace("A7AL2Z5", "A7AL2Z9", regex=False)
    counts = (
        decisions.groupby(["label_horizon_h", "decision"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["label_horizon_h", "count"], ascending=[True, False])
        if not decisions.empty
        else pd.DataFrame(columns=["label_horizon_h", "decision", "count"])
    )
    family = (
        decisions.groupby(["label_horizon_h", "objective_family"], dropna=False)
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
    stress_clean_count = int(decisions["decision"].eq("A7AL2Z9_MULTI_HORIZON_PREFLIGHT_CLUE_STRESS_CLEAN").sum()) if not decisions.empty else 0
    veto_count = int(decisions["decision"].eq("A7AL2Z9_PRE_MAY_CLUE_MAY_STRESS_VETOED").sum()) if not decisions.empty else 0
    unobserved_count = int(decisions["decision"].eq("A7AL2Z9_PRE_MAY_CLUE_MAY_STRESS_UNOBSERVED").sum()) if not decisions.empty else 0
    blockers = []
    if error_rows:
        blockers.append("eval_errors")
    if stress_clean_count == 0 and veto_count == 0 and unobserved_count == 0:
        blockers.append("no_response_guided_partial_numeric_clues")
    decision = (
        "PASS_A7AL2Z9_RESPONSE_GUIDED_PARTIAL_NUMERIC_CLUES_FOUND_EXECUTION_HOLD"
        if not error_rows and (stress_clean_count > 0 or veto_count > 0 or unobserved_count > 0)
        else "HOLD_A7AL2Z9_NO_RESPONSE_GUIDED_PARTIAL_NUMERIC_CLUES"
    )
    manifest = {
        "stage": "A7AL-2Z9",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_partial_numeric_diagnostic": True,
        "executes_generation": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_full_replay": False,
        "authorizes_formula_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "candidate_count": int(len(sample)),
        "label_horizons_h": LABEL_HORIZONS,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_smoke_subset": full_timestamp_count,
        "metric_rows": int(len(metrics)),
        "eval_error_count": int(len(error_rows)),
        "stress_clean_clue_count": stress_clean_count,
        "pre_may_clue_may_veto_count": veto_count,
        "pre_may_clue_may_unobserved_count": unobserved_count,
        "blockers": blockers,
        "source_z8p_selected_candidates": int(z8p.get("selected_candidates", 0)),
        "uses_may_in_selector": False,
        "uses_may_in_generation": False,
    }
    metrics.to_csv(RUNTIME / "a7al2z9_candidate_variant_metrics_by_horizon.csv", index=False)
    decisions.to_csv(RUNTIME / "a7al2z9_candidate_horizon_decisions.csv", index=False)
    counts.to_csv(RUNTIME / "a7al2z9_decision_counts_by_horizon.csv", index=False)
    family.to_csv(RUNTIME / "a7al2z9_family_horizon_summary.csv", index=False)
    pd.DataFrame(error_rows).to_csv(RUNTIME / "a7al2z9_eval_errors.csv", index=False)
    write_json(RUNTIME / "a7al2z9_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z9_authorization_matrix.json",
        {
            "A7AL-2Z9": {"status": decision},
            "full_replay": {"authorized": False},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AL-2Z9 RESPONSE-GUIDED PARTIAL NUMERIC DIAGNOSTIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "Z9 runs a bounded multi-horizon diagnostic only on the Z8P partial viable queue. It does not authorize full replay, formula search, or proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Decision Counts By Horizon",
        "",
        md_table(counts, 80),
        "",
        "## Family Horizon Summary",
        "",
        md_table(family, 120),
        "",
        "## Candidate Horizon Decisions",
        "",
        md_table(decisions, 120),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
