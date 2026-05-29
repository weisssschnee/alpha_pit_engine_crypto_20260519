from __future__ import annotations

import json
import re
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


RUNTIME = REPO / "runtime" / "a7al2z2_broader_non_oi_materialization_audit"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z2_BROADER_NON_OI_MATERIALIZATION_AUDIT_20260529.md"
Z1_MANIFEST = REPO / "runtime" / "a7al2z1_broader_non_oi_dry_generation" / "a7al2z1_manifest.json"
Z1_SELECTED = REPO / "runtime" / "a7al2z1_broader_non_oi_dry_generation" / "a7al2z1_selected_for_z2_materialization.csv"

SYMBOL_CAP = 96
MIN_FINITE_SHARE = 0.20
MIN_NONZERO_SHARE = 0.01
REGIME_STATE_RE = re.compile(r"\bR\d+_[A-Za-z0-9_]+_state\b")
STATIC_GROUP_FIELDS = {"liquidity_tier", "meme_contract_group", "is_multiplier_contract", "is_major"}


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
    return [x for x in str(value).split("|") if x]


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


def selected_fields(selected: pd.DataFrame) -> set[str]:
    fields = {"trade_close"}
    for text in selected["fields"].dropna().astype(str):
        fields.update(split_pipe(text))
    return fields


def expression_group_fields(selected: pd.DataFrame) -> set[str]:
    """Recover group tokens from expressions.

    Z1's static field ledger was intentionally source-field oriented and did
    not always include upper-regime group tokens in the pipe-delimited `fields`
    column. The evaluator still needs those group arrays loaded before it can
    materialize GroupNeutralize/LatentNeutralRank expressions.
    """
    groups: set[str] = set()
    for expression in selected["expression"].dropna().astype(str):
        groups.update(REGIME_STATE_RE.findall(expression))
        for field in STATIC_GROUP_FIELDS:
            if re.search(rf"\b{re.escape(field)}\b", expression):
                groups.add(field)
    return groups


def write_report(manifest: dict[str, Any], summary: pd.DataFrame, family: pd.DataFrame, operators: pd.DataFrame, groups: pd.DataFrame, blockers: pd.DataFrame) -> None:
    lines = [
        "# CRYPTO A7AL-2Z2 BROADER NON-OI MATERIALIZATION AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "Z2 evaluates Z1-selected static expressions on a bounded strict-universe sample. It does not compute returns, run replay, train, or authorize proof.",
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
        "## Candidate Evaluation Summary",
        "",
        md_table(summary, 80),
        "",
        "## Operator Coverage",
        "",
        md_table(operators),
        "",
        "## Group Field Coverage",
        "",
        md_table(groups),
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
    if not z1.get("authorizes_a7al2z2_materialization_audit"):
        raise SystemExit("A7AL-2Z1 does not authorize Z2 materialization audit")
    selected = pd.read_csv(Z1_SELECTED)
    fields = selected_fields(selected)
    group_fields = {
        f
        for f in fields
        if (f.startswith("R") and f.endswith("_state"))
        or f in STATIC_GROUP_FIELDS
    }
    group_fields.update(expression_group_fields(selected))
    numeric_fields = fields - group_fields
    base_schema = parquet_schema(BASE_DIR)
    latent_schema = parquet_schema(LATENT_PANEL)
    base_numeric_fields = {field for field in numeric_fields if field in base_schema}
    latent_numeric_fields = {field for field in numeric_fields if field in latent_schema and field not in base_numeric_fields}
    missing_numeric_fields = sorted(numeric_fields - base_numeric_fields - latent_numeric_fields)
    if missing_numeric_fields:
        raise SystemExit(f"missing numeric fields for Z2: {missing_numeric_fields}")

    symbols = strict_symbols()
    loaded_symbols, timestamps, numeric = load_base(symbols, base_numeric_fields)
    numeric.update(load_latent_numeric(loaded_symbols, timestamps, latent_numeric_fields))
    groups = load_group_fields(loaded_symbols, timestamps, group_fields)
    evaluator = StateAwareEvaluator(numeric, groups)

    rows: list[dict[str, Any]] = []
    blocker_rows: list[dict[str, Any]] = []
    op_counter: Counter[str] = Counter()
    for i, row in enumerate(selected.to_dict("records"), start=1):
        expression = str(row["expression"])
        for op in split_pipe(row["operator_signature"]):
            op_counter[op] += 1
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
        if not eval_success:
            blocker_rows.append({"candidate_id": row["candidate_id"], "blocker": "eval_failure", "detail": error})
        elif not activity_ok:
            blocker_rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "blocker": "activity_or_coverage_failure",
                    "detail": f"finite={finite_share:.6f};nonzero={nonzero_share:.6f}",
                }
            )
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "objective_family": row["objective_family"],
                "expression": expression,
                "operator_signature": row["operator_signature"],
                "eval_success": eval_success,
                "finite_share": finite_share,
                "nonzero_share": nonzero_share,
                "activity_ok": activity_ok,
                "min_value": min_value,
                "max_value": max_value,
                "error": error,
            }
        )
        if i % 32 == 0:
            print(f"[A7AL-2Z2] evaluated {i}/{len(selected)}", flush=True)

    summary = pd.DataFrame(rows)
    blockers = pd.DataFrame(blocker_rows)
    family = (
        summary.groupby("objective_family", dropna=False)
        .agg(
            evaluated_count=("candidate_id", "count"),
            eval_success_count=("eval_success", "sum"),
            activity_ok_count=("activity_ok", "sum"),
            median_finite_share=("finite_share", "median"),
            median_nonzero_share=("nonzero_share", "median"),
        )
        .reset_index()
    )
    operators = pd.DataFrame([{"operator": key, "selected_candidate_count": val} for key, val in sorted(op_counter.items())])
    group_rows = []
    for field, matrix in groups.items():
        values = sorted(pd.Series(matrix.reshape(-1)).dropna().astype(str).unique().tolist())
        group_rows.append({"group_field": field, "unique_values": len(values), "values": "|".join(values[:80])})
    group_df = pd.DataFrame(group_rows)

    eval_fail = int((~summary["eval_success"]).sum())
    activity_fail = int((~summary["activity_ok"]).sum())
    decision = (
        "PASS_A7AL2Z2_BROADER_NON_OI_MATERIALIZATION_READY_FOR_NUMERIC_PREFLIGHT_CONTRACT"
        if eval_fail == 0 and activity_fail == 0
        else "HOLD_A7AL2Z2_EVAL_OR_ACTIVITY_FAILURE"
    )
    manifest = {
        "stage": "A7AL-2Z2",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_materialization_audit": True,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7al2z3_numeric_preflight_contract": decision.startswith("PASS"),
        "authorizes_numeric_replay_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "evaluated_candidates": int(len(summary)),
        "symbols_loaded": int(len(loaded_symbols)),
        "timestamps": int(len(timestamps)),
        "eval_failure_count": eval_fail,
        "activity_failure_count": activity_fail,
        "numeric_field_count": int(len(numeric)),
        "group_field_count": int(len(groups)),
        "base_numeric_field_count": int(len(base_numeric_fields)),
        "latent_numeric_field_count": int(len(latent_numeric_fields)),
        "uses_may": False,
    }

    summary.to_csv(RUNTIME / "a7al2z2_candidate_eval_summary.csv", index=False)
    family.to_csv(RUNTIME / "a7al2z2_family_eval_summary.csv", index=False)
    operators.to_csv(RUNTIME / "a7al2z2_operator_coverage.csv", index=False)
    group_df.to_csv(RUNTIME / "a7al2z2_group_field_coverage.csv", index=False)
    blockers.to_csv(RUNTIME / "a7al2z2_blocker_matrix.csv", index=False)
    write_json(RUNTIME / "a7al2z2_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z2_authorization_matrix.json",
        {
            "A7AL-2Z2": {"status": decision},
            "a7al2z3_numeric_preflight_contract": {"authorized": decision.startswith("PASS")},
            "numeric_replay_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    write_report(manifest, summary, family, operators, group_df, blockers)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
