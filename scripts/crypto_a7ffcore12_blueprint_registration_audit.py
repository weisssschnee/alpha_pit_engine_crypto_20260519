from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from crypto_a7ffcore1_ast_schema_adapter import ast_stats, parse_expression, render  # noqa: E402


RUNTIME = REPO / "runtime" / "a7ffcore12_blueprint_registration_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE12_BLUEPRINT_REGISTRATION_AUDIT_20260601.md"
A7FFCORE11E = REPO / "runtime" / "a7ffcore11e_small_dry_generation" / "a7ffcore11e_manifest.json"
BLUEPRINTS = REPO / "runtime" / "a7ffcore11e_small_dry_generation" / "a7ffcore11e_blueprint_pool.csv"

ALLOWED_OPS = {"Mean", "Delta", "ZScore", "Rank", "CSRank", "TSRank", "SafeDiv", "Mul", "Sub", "Add", "Neg", "Abs", "Sign", "Clip", "Decay"}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def stable_id(expr: str) -> str:
    return "sgx_" + hashlib.sha1(expr.replace(" ", "").encode("utf-8")).hexdigest()[:18]


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core11e = read_json(A7FFCORE11E)
    if core11e.get("decision") != "PASS_A7FFCORE11E_BLUEPRINTS_READY_FOR_CORE12_REGISTRATION":
        raise SystemExit(f"A7FF-CORE11E is not ready: {core11e.get('decision')}")
    blueprints = pd.read_csv(BLUEPRINTS)
    rows: list[dict[str, Any]] = []
    parse_errors = 0
    for row in blueprints.to_dict("records"):
        expr = str(row["expression"])
        try:
            ast = parse_expression(expr)
            rendered = render(ast)
            stats = ast_stats(ast)
            ops = [op for op in str(stats["operator_path"]).split(">") if op]
            bad_ops = sorted(set(ops) - ALLOWED_OPS)
            status = "approved_for_temp_registration"
            reject_reason = ""
            if bad_ops:
                status = "rejected"
                reject_reason = "unsupported_operator:" + ";".join(bad_ops)
            elif int(stats["max_depth"]) > 10 or int(stats["node_count"]) > 80:
                status = "rejected"
                reject_reason = "ast_complexity_limit"
            rows.append(
                {
                    **row,
                    "proposed_subgraph_id": stable_id(rendered),
                    "canonical_expression": rendered,
                    "parse_status": "ok",
                    "registration_status": status,
                    "reject_reason": reject_reason,
                    **stats,
                }
            )
        except Exception as exc:
            parse_errors += 1
            rows.append({**row, "proposed_subgraph_id": "", "canonical_expression": "", "parse_status": "error", "registration_status": "rejected", "reject_reason": str(exc)})
    registry = pd.DataFrame(rows)
    approved = registry[registry["registration_status"].eq("approved_for_temp_registration")].copy()
    operator_summary = (
        approved.assign(operator_path=approved["operator_path"].fillna(""))
        .groupby("generation_mode", dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), median_node_count=("node_count", "median"), median_depth=("max_depth", "median"))
        .reset_index()
        .sort_values("candidate_count", ascending=False)
    )
    family_summary = (
        approved.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), parent_count=("parent_candidate_id", "nunique"), generation_mode_count=("generation_mode", "nunique"))
        .reset_index()
        .sort_values("candidate_count", ascending=False)
    )
    registry.to_csv(RUNTIME / "a7ffcore12_proposed_subgraph_registry.csv", index=False)
    approved.to_csv(RUNTIME / "a7ffcore12_approved_temp_subgraphs.csv", index=False)
    operator_summary.to_csv(RUNTIME / "a7ffcore12_operator_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore12_family_summary.csv", index=False)
    rejected = registry[registry["registration_status"].ne("approved_for_temp_registration")]
    rejected.to_csv(RUNTIME / "a7ffcore12_rejected_blueprints.csv", index=False)
    risk_flags = []
    if parse_errors:
        risk_flags.append("parse_errors_present")
    if len(approved) < 3000:
        risk_flags.append("approved_temp_subgraphs_below_3000")
    if int(approved["parent_candidate_id"].nunique()) < 20:
        risk_flags.append("parent_seed_coverage_low")
    if int(approved["semantic_bucket"].nunique()) < 8:
        risk_flags.append("semantic_breadth_low")
    pd.DataFrame([{"risk_flag": r} for r in risk_flags]).to_csv(RUNTIME / "a7ffcore12_risk_flags.csv", index=False)
    decision = "PASS_A7FFCORE12_TEMP_SUBGRAPH_REGISTRY_READY_FOR_CORE12E" if not risk_flags else "HOLD_A7FFCORE12_REGISTRATION_AUDIT_FAIL"
    manifest = {
        "stage": "A7FF-CORE12",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE11E",
        "source_decision": core11e.get("decision"),
        "decision": decision,
        "blueprint_count": int(len(registry)),
        "parse_error_count": int(parse_errors),
        "approved_temp_subgraph_count": int(len(approved)),
        "rejected_count": int(len(rejected)),
        "parent_seed_count": int(approved["parent_candidate_id"].nunique()) if not approved.empty else 0,
        "semantic_bucket_count": int(approved["semantic_bucket"].nunique()) if not approved.empty else 0,
        "motif_bucket_count": int(approved["motif_bucket"].nunique()) if not approved.empty else 0,
        "risk_flags": risk_flags,
        "executes_materialization": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core12e": not risk_flags,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE12E temp-subgraph materialization preflight" if not risk_flags else "A7FF-CORE12R registration repair",
    }
    write_json(RUNTIME / "a7ffcore12_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE12 BLUEPRINT REGISTRATION AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE12 parses CORE11E blueprints into a temporary subgraph registry. It does not modify CORE2 registry, materialize formulas, run numeric response, replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Operator Summary",
        "",
        md_table(operator_summary),
        "",
        "## Boundary",
        "",
        "```text",
        "temporary registration audit: true",
        "CORE2 registry modified: false",
        "materialization / numeric / replay / search: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
