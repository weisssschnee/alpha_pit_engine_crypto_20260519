from __future__ import annotations

import json
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

from scripts.crypto_a7al2x5_evaluator_preflight_smoke import (  # noqa: E402
    BASE_DIR,
    LATENT_PANEL,
    SPLIT_COVERAGE,
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


RUNTIME = REPO / "runtime" / "a7al2z2r_broader_non_oi_materialization_repair"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z2R_BROADER_NON_OI_MATERIALIZATION_REPAIR_20260529.md"
Z1_MANIFEST = REPO / "runtime" / "a7al2z1_broader_non_oi_dry_generation" / "a7al2z1_manifest.json"
Z1_LEDGER = REPO / "runtime" / "a7al2z1_broader_non_oi_dry_generation" / "a7al2z1_generated_candidate_ledger.csv"
Z2_MANIFEST = REPO / "runtime" / "a7al2z2_broader_non_oi_materialization_audit" / "a7al2z2_manifest.json"

SYMBOL_CAP = 96
TARGET_PER_FAMILY = 16


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


def strict_symbols() -> list[str]:
    cov = pd.read_csv(SPLIT_COVERAGE)
    symbols = (
        cov.loc[cov["search_eligibility"].eq("strict_full_history"), "symbol"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )
    return symbols[:SYMBOL_CAP]


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
        min_value = float(np.nanmin(values)) if finite.any() else np.nan
        max_value = float(np.nanmax(values)) if finite.any() else np.nan
        eval_success = True
        error = ""
    except Exception as exc:  # noqa: BLE001
        finite_share = 0.0
        nonzero_share = 0.0
        min_value = np.nan
        max_value = np.nan
        eval_success = False
        error = repr(exc)
    activity_ok = eval_success and finite_share >= MIN_FINITE_SHARE and nonzero_share >= MIN_NONZERO_SHARE
    return {
        "eval_success": eval_success,
        "finite_share": finite_share,
        "nonzero_share": nonzero_share,
        "activity_ok": activity_ok,
        "min_value": min_value,
        "max_value": max_value,
        "error": error,
    }


def candidate_sort_key(row: dict[str, Any], selected_seed: bool) -> tuple[int, str, str]:
    # Prefer the original Z1 selected queue, but allow replacements when those
    # expressions are sparse or constant under real materialization.
    return (0 if selected_seed else 1, str(row["skeleton_key"]), str(row["candidate_id"]))


def write_report(
    manifest: dict[str, Any],
    selected: pd.DataFrame,
    family: pd.DataFrame,
    trace: pd.DataFrame,
    blockers: pd.DataFrame,
) -> None:
    lines = [
        "# CRYPTO A7AL-2Z2R BROADER NON-OI MATERIALIZATION REPAIR",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "Z2R repairs the Z1 materialization queue by replacing sparse or constant expressions from the same static dry pool. It does not compute returns, replay, train, or authorize proof.",
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
        "## Repaired Selected Queue",
        "",
        md_table(selected[["candidate_id", "objective_family", "expression", "skeleton_key", "finite_share", "nonzero_share"]], 80),
        "",
        "## Evaluation Trace Preview",
        "",
        md_table(trace, 80),
        "",
        "## Blockers",
        "",
        md_table(blockers) if not blockers.empty else "No blockers.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    z1 = read_json(Z1_MANIFEST)
    z2 = read_json(Z2_MANIFEST)
    if not z1.get("authorizes_a7al2z2_materialization_audit"):
        raise SystemExit("A7AL-2Z1 does not authorize Z2 materialization audit")
    if not z2 or z2.get("eval_failure_count", 1) != 0:
        raise SystemExit("A7AL-2Z2 must have zero evaluator failures before Z2R repair")

    ledger = pd.read_csv(Z1_LEDGER)
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
        raise SystemExit(f"missing numeric fields for Z2R: {missing_numeric_fields}")

    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_numeric_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_numeric_fields))
    groups = load_group_fields(loaded_symbols, timestamps, group_fields)
    evaluator = StateAwareEvaluator(numeric, groups)

    selected_rows: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []
    blocker_rows: list[dict[str, Any]] = []
    seen_selected_ids: set[str] = set()

    for family, family_df in ledger.groupby("objective_family", sort=True):
        selected_seed_ids = set(
            family_df.loc[
                family_df["selected_for_z2_materialization"].astype(str).str.lower().isin(["true", "1"]),
                "candidate_id",
            ]
        )
        ordered = sorted(
            family_df.to_dict("records"),
            key=lambda row: candidate_sort_key(row, str(row["candidate_id"]) in selected_seed_ids),
        )
        family_selected: list[dict[str, Any]] = []
        used_skeletons: set[str] = set()
        pass_number = 0
        while len(family_selected) < TARGET_PER_FAMILY and pass_number < 2:
            for row in ordered:
                if len(family_selected) >= TARGET_PER_FAMILY:
                    break
                cid = str(row["candidate_id"])
                if cid in seen_selected_ids:
                    continue
                skeleton = str(row["skeleton_key"])
                if pass_number == 0 and skeleton in used_skeletons:
                    continue
                result = evaluate_expression(evaluator, str(row["expression"]))
                trace = {
                    "candidate_id": cid,
                    "objective_family": family,
                    "expression": row["expression"],
                    "skeleton_key": skeleton,
                    "was_z1_selected": cid in selected_seed_ids,
                    **result,
                }
                trace_rows.append(trace)
                if result["activity_ok"]:
                    out = dict(row)
                    out.update(result)
                    out["selected_by_z2r"] = True
                    out["was_z1_selected"] = cid in selected_seed_ids
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
            pass_number += 1
        selected_rows.extend(family_selected)
        if len(family_selected) < TARGET_PER_FAMILY:
            blocker_rows.append(
                {
                    "candidate_id": "",
                    "blocker": "family_repair_quota_unfilled",
                    "detail": f"{family}: selected={len(family_selected)} target={TARGET_PER_FAMILY}",
                }
            )
        print(f"[A7AL-2Z2R] {family}: selected {len(family_selected)}/{TARGET_PER_FAMILY}", flush=True)

    selected = pd.DataFrame(selected_rows)
    trace = pd.DataFrame(trace_rows)
    blockers = pd.DataFrame(blocker_rows)
    if selected.empty:
        family = pd.DataFrame()
    else:
        family = (
            selected.groupby("objective_family", dropna=False)
            .agg(
                selected_count=("candidate_id", "count"),
                z1_seed_retained_count=("was_z1_selected", "sum"),
                unique_skeleton_count=("skeleton_key", "nunique"),
                median_finite_share=("finite_share", "median"),
                median_nonzero_share=("nonzero_share", "median"),
            )
            .reset_index()
        )
    family_ok = selected.groupby("objective_family")["candidate_id"].count().ge(TARGET_PER_FAMILY).all() if not selected.empty else False
    eval_fail_selected = int((~selected["eval_success"]).sum()) if not selected.empty else 0
    activity_fail_selected = int((~selected["activity_ok"]).sum()) if not selected.empty else 0
    decision = (
        "PASS_A7AL2Z2R_BROADER_NON_OI_MATERIALIZATION_REPAIR_READY_FOR_Z3_CONTRACT"
        if family_ok and eval_fail_selected == 0 and activity_fail_selected == 0
        else "HOLD_A7AL2Z2R_REPAIR_QUOTA_OR_ACTIVITY_FAILURE"
    )
    manifest = {
        "stage": "A7AL-2Z2R",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_materialization_repair": True,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7al2z3_numeric_preflight_contract": decision.startswith("PASS"),
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
        "numeric_field_count": int(len(numeric)),
        "group_field_count": int(len(groups)),
        "uses_may": False,
    }

    selected.to_csv(RUNTIME / "a7al2z2r_repaired_selected_candidates.csv", index=False)
    trace.to_csv(RUNTIME / "a7al2z2r_candidate_eval_trace.csv", index=False)
    family.to_csv(RUNTIME / "a7al2z2r_family_repair_summary.csv", index=False)
    blockers.to_csv(RUNTIME / "a7al2z2r_repair_blocker_matrix.csv", index=False)
    write_json(RUNTIME / "a7al2z2r_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z2r_authorization_matrix.json",
        {
            "A7AL-2Z2R": {"status": decision},
            "a7al2z3_numeric_preflight_contract": {"authorized": decision.startswith("PASS")},
            "numeric_replay_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    write_report(manifest, selected, family, trace, blockers)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
