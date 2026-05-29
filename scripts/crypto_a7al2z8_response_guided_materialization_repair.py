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
)
from scripts.crypto_a7al2z2_broader_non_oi_materialization_audit import (  # noqa: E402
    MIN_FINITE_SHARE,
    MIN_NONZERO_SHARE,
    expression_group_fields,
    split_pipe,
)
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402
from scripts.crypto_a7al2z4_broader_non_oi_numeric_replay_preflight import smoke_column_indices  # noqa: E402


RUNTIME = REPO / "runtime" / "a7al2z8_response_guided_materialization_repair"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z8_RESPONSE_GUIDED_MATERIALIZATION_REPAIR_20260529.md"
Z7_MANIFEST = REPO / "runtime" / "a7al2z7_response_guided_dry_generation" / "a7al2z7_manifest.json"
Z7_LEDGER = REPO / "runtime" / "a7al2z7_response_guided_dry_generation" / "a7al2z7_generated_candidate_ledger.csv"

TARGET_PER_FAMILY = 16
MAX_EVAL_PER_FAMILY = 96


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


def ledger_fields(ledger: pd.DataFrame) -> set[str]:
    fields = {"trade_close"}
    for text in ledger["fields"].dropna().astype(str):
        fields.update(split_pipe(text))
    return fields


def evaluate_expression(evaluator: StateAwareEvaluator, expression: str) -> dict[str, Any]:
    try:
        values = evaluator.eval(expression)
        finite = np.isfinite(values)
        finite_share = float(finite.mean()) if values.size else 0.0
        nonzero_share = float((np.abs(values[finite]) > 1e-12).mean()) if finite.any() else 0.0
        eval_success = True
        error = ""
    except Exception as exc:  # noqa: BLE001
        finite_share = 0.0
        nonzero_share = 0.0
        eval_success = False
        error = repr(exc)
    activity_ok = eval_success and finite_share >= MIN_FINITE_SHARE and nonzero_share >= MIN_NONZERO_SHARE
    return {
        "eval_success": eval_success,
        "finite_share": finite_share,
        "nonzero_share": nonzero_share,
        "activity_ok": activity_ok,
        "error": error,
    }


def candidate_sort_key(row: dict[str, Any], selected_seed: bool) -> tuple[int, str, str]:
    return (0 if selected_seed else 1, str(row["skeleton_key"]), str(row["candidate_id"]))


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    z7 = read_json(Z7_MANIFEST)
    if not z7.get("authorizes_a7al2z8_materialization_repair"):
        raise SystemExit("A7AL-2Z7 does not authorize Z8 materialization")
    ledger = pd.read_csv(Z7_LEDGER)
    ledger = ledger[ledger["static_valid"].astype(str).str.lower().isin(["true", "1"])].copy()
    fields = ledger_fields(ledger)
    group_fields = {
        f
        for f in fields
        if (f.startswith("R") and f.endswith("_state"))
        or f in {"liquidity_tier", "meme_contract_group", "is_multiplier_contract", "is_major"}
    }
    group_fields.update(expression_group_fields(ledger))
    numeric_fields = fields - group_fields
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_numeric_fields = {field for field in numeric_fields if field in base_schema}
    latent_numeric_fields = {field for field in numeric_fields if field in latent_schema and field not in base_numeric_fields}
    missing_numeric_fields = sorted(numeric_fields - base_numeric_fields - latent_numeric_fields)
    if missing_numeric_fields:
        raise SystemExit(f"missing numeric fields for Z8: {missing_numeric_fields}")
    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_numeric_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_numeric_fields))
    groups = load_group_fields(loaded_symbols, timestamps, group_fields)
    full_timestamp_count = int(len(timestamps))
    idx = smoke_column_indices(timestamps)
    timestamps = pd.DatetimeIndex(timestamps[idx])
    numeric = {key: value[:, idx] for key, value in numeric.items()}
    groups = {key: value[:, idx] for key, value in groups.items()}
    evaluator = StateAwareEvaluator(numeric, groups)

    selected_rows: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []
    blocker_rows: list[dict[str, Any]] = []
    seen_selected_ids: set[str] = set()
    for family, family_df in ledger.groupby("objective_family", sort=True):
        family_eval_count = 0
        selected_seed_ids = set(
            family_df.loc[
                family_df["selected_for_z8_materialization"].astype(str).str.lower().isin(["true", "1"]),
                "candidate_id",
            ]
        )
        ordered = sorted(family_df.to_dict("records"), key=lambda row: candidate_sort_key(row, str(row["candidate_id"]) in selected_seed_ids))
        family_selected: list[dict[str, Any]] = []
        used_skeletons: set[str] = set()
        for pass_number in [0, 1]:
            for row in ordered:
                if family_eval_count >= MAX_EVAL_PER_FAMILY:
                    break
                if len(family_selected) >= TARGET_PER_FAMILY:
                    break
                cid = str(row["candidate_id"])
                skeleton = str(row["skeleton_key"])
                if cid in seen_selected_ids:
                    continue
                if pass_number == 0 and skeleton in used_skeletons:
                    continue
                result = evaluate_expression(evaluator, str(row["expression"]))
                family_eval_count += 1
                trace = {
                    "candidate_id": cid,
                    "objective_family": family,
                    "expression": row["expression"],
                    "skeleton_key": skeleton,
                    "was_z7_selected": cid in selected_seed_ids,
                    **result,
                }
                trace_rows.append(trace)
                if len(trace_rows) % 16 == 0:
                    print(f"[A7AL-2Z8] evaluated {len(trace_rows)} candidates", flush=True)
                if result["activity_ok"]:
                    out = dict(row)
                    out.update(result)
                    out["selected_by_z8"] = True
                    out["was_z7_selected"] = cid in selected_seed_ids
                    family_selected.append(out)
                    seen_selected_ids.add(cid)
                    used_skeletons.add(skeleton)
                elif not result["eval_success"]:
                    blocker_rows.append({"candidate_id": cid, "blocker": "eval_failure", "detail": result["error"]})
                else:
                    blocker_rows.append(
                        {
                            "candidate_id": cid,
                            "blocker": "activity_or_coverage_failure",
                            "detail": f"finite={result['finite_share']:.6f};nonzero={result['nonzero_share']:.6f}",
                        }
                    )
            if len(family_selected) >= TARGET_PER_FAMILY:
                break
        selected_rows.extend(family_selected)
        if len(family_selected) < TARGET_PER_FAMILY:
            blocker_rows.append({"candidate_id": "", "blocker": "family_repair_quota_unfilled", "detail": f"{family}: selected={len(family_selected)} target={TARGET_PER_FAMILY}"})
        print(f"[A7AL-2Z8] {family}: selected {len(family_selected)}/{TARGET_PER_FAMILY}", flush=True)

    selected = pd.DataFrame(selected_rows)
    trace = pd.DataFrame(trace_rows)
    blockers = pd.DataFrame(blocker_rows)
    family = (
        selected.groupby("objective_family", dropna=False)
        .agg(
            selected_count=("candidate_id", "count"),
            z7_seed_retained_count=("was_z7_selected", "sum"),
            unique_skeleton_count=("skeleton_key", "nunique"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
        )
        .reset_index()
        if not selected.empty
        else pd.DataFrame()
    )
    family_ok = selected.groupby("objective_family")["candidate_id"].count().ge(TARGET_PER_FAMILY).all() if not selected.empty else False
    eval_fail_selected = int((~selected["eval_success"]).sum()) if not selected.empty else 0
    activity_fail_selected = int((~selected["activity_ok"]).sum()) if not selected.empty else 0
    decision = (
        "PASS_A7AL2Z8_RESPONSE_GUIDED_MATERIALIZATION_READY_FOR_Z9"
        if family_ok and eval_fail_selected == 0 and activity_fail_selected == 0
        else "HOLD_A7AL2Z8_REPAIR_QUOTA_OR_ACTIVITY_FAILURE"
    )
    manifest = {
        "stage": "A7AL-2Z8",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_materialization_repair": True,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7al2z9_numeric_diagnostic": decision.startswith("PASS"),
        "authorizes_numeric_replay_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "ledger_candidates": int(len(ledger)),
        "evaluated_candidates": int(len(trace)),
        "selected_candidates": int(len(selected)),
        "target_per_family": TARGET_PER_FAMILY,
        "family_count": int(selected["objective_family"].nunique()) if not selected.empty else 0,
        "selected_eval_failure_count": eval_fail_selected,
        "selected_activity_failure_count": activity_fail_selected,
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "full_timestamps_before_materialization_subset": full_timestamp_count,
        "max_eval_per_family": MAX_EVAL_PER_FAMILY,
        "numeric_field_count": int(len(numeric)),
        "group_field_count": int(len(groups)),
        "uses_may": False,
    }
    selected.to_csv(RUNTIME / "a7al2z8_repaired_selected_candidates.csv", index=False)
    trace.to_csv(RUNTIME / "a7al2z8_candidate_eval_trace.csv", index=False)
    family.to_csv(RUNTIME / "a7al2z8_family_repair_summary.csv", index=False)
    blockers.to_csv(RUNTIME / "a7al2z8_repair_blocker_matrix.csv", index=False)
    write_json(RUNTIME / "a7al2z8_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z8_authorization_matrix.json",
        {
            "A7AL-2Z8": {"status": decision},
            "a7al2z9_numeric_diagnostic": {"authorized": decision.startswith("PASS")},
            "numeric_replay_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AL-2Z8 RESPONSE-GUIDED MATERIALIZATION REPAIR",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "Z8 materializes and repairs the Z7 response-guided queue. It does not compute returns, run replay, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Summary",
        "",
        md_table(family),
        "",
        "## Selected Queue",
        "",
        md_table(selected[["candidate_id", "objective_family", "expression", "skeleton_key", "finite_share", "nonzero_share"]], 80),
        "",
        "## Blockers",
        "",
        md_table(blockers) if not blockers.empty else "No blockers.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
