from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra
from alphafactory_crypto.engines.formula_gen_v2_adapter import CryptoFormulaGenV2Adapter, load_field_enforcement_csv

RUNTIME = REPO / "runtime" / "a7aif2_field_enforcement_regression"
REPORT = REPO / "reports" / "CRYPTO_A7AIF2_END_TO_END_FIELD_ENFORCEMENT_REGRESSION_20260529.md"

A7AIF1 = REPO / "runtime" / "a7aif1_engine_enforcement_gap_audit" / "a7aif1_manifest.json"
LEDGER_PATH = REPO / "runtime" / "a7aif0_field_contract_enforcement_ledger" / "a7aif0_semantic_field_enforcement_ledger.csv"
MOTIF_PACK = REPO / "config" / "crypto_formula_gen_v2_motif_pack_v1.json"
SHARED_POOL = REPO / "runtime" / "a7ar7_shared_candidate_pool" / "a7ar7_shared_candidate_pool.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def field_set(text: Any) -> list[str]:
    if pd.isna(text):
        return []
    return [part for part in str(text).split("|") if part]


def role_for_fields(fields: list[str], ledger: dict[str, dict[str, Any]]) -> tuple[str, str]:
    statuses = []
    roles = []
    for field in fields:
        row = ledger.get(field, {})
        statuses.append(str(row.get("enforcement_status", "MISSING")))
        roles.append(str(row.get("semantic_role", "missing")))
    if any(status == "FORBID" or status.startswith("HOLD_CONTRACT") or status.startswith("HOLD_TIMING") for status in statuses):
        return "role_violation", "|".join(sorted(set(roles)))
    if any(role == "ordinary_signal_candidate" for role in roles):
        return "ordinary_alpha_possible", "|".join(sorted(set(roles)))
    if any(role == "diagnostic_rank_or_nonordinary_signal" or role == "regime_state_or_interaction_input" for role in roles):
        return "diagnostic_only", "|".join(sorted(set(roles)))
    if any(role == "risk_exposure_or_control_like" for role in roles):
        return "risk_defense_only", "|".join(sorted(set(roles)))
    return "weak_or_unclassified", "|".join(sorted(set(roles)))


def generator_smoke(ledger_path: Path) -> pd.DataFrame:
    rows = []
    for mode in ["ordinary_alpha", "diagnostic", "risk_defense"]:
        adapter = CryptoFormulaGenV2Adapter.from_path(
            MOTIF_PACK,
            seed=f"a7aif2_{mode}",
            field_enforcement_path=ledger_path,
            field_mode=mode,
        )
        registry = adapter.field_registry
        eligible = adapter._eligible_motif_families()
        generated = []
        errors = []
        for index in range(8):
            try:
                candidate = adapter.generate(index=index)
                generated.append(candidate)
            except Exception as exc:  # mode may intentionally have no complete motifs
                errors.append(str(exc))
                break
        blocked_fields = []
        for fields in registry.values():
            for field in fields:
                row = adapter.field_enforcement.get(field, {})
                if mode != "syntax" and not truthy(row.get({"ordinary_alpha": "ordinary_alpha_allowed", "diagnostic": "diagnostic_allowed", "risk_defense": "risk_defense_allowed"}[mode])):
                    blocked_fields.append(field)
        rows.append(
            {
                "mode": mode,
                "registry_field_count": sum(len(v) for v in registry.values()),
                "eligible_motif_family_count": len(eligible),
                "generated_count": len(generated),
                "error": errors[0] if errors else "",
                "blocked_field_leak_count": len(blocked_fields),
                "sample_expression": generated[0].expression if generated else "",
                "decision": "PASS_FAIL_CLOSED_NO_ELIGIBLE_MOTIF" if not generated and errors else ("PASS" if not blocked_fields else "HOLD_BLOCKED_FIELD_LEAK"),
            }
        )
    return pd.DataFrame(rows)


def evaluator_fail_closed(ledger: dict[str, dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "symbol": ["A", "A", "B", "B"],
            "timestamp": [1, 2, 1, 2],
            "mark_index_basis_bps": [1.0, 2.0, 3.0, 4.0],
            "forward_trade_return_1h": [0.1, 0.2, 0.3, 0.4],
        }
    )
    rows = []
    checks = [
        ("allowed_contract_field", "mark_index_basis_bps", {"mark_index_basis_bps"}, True),
        ("label_future_field", "forward_trade_return_1h", {"forward_trade_return_1h"}, False),
        ("missing_contract_field", "made_up_field", {"made_up_field"}, False),
    ]
    for check, expression, allowed, should_pass in checks:
        if expression == "made_up_field":
            frame[expression] = [1.0, 1.0, 1.0, 1.0]
        try:
            CryptoFeatureAlgebra(frame, allowed, field_contract=ledger).evaluate(expression)
            passed = True
            error = ""
        except Exception as exc:
            passed = False
            error = str(exc)
        rows.append(
            {
                "check": check,
                "expression": expression,
                "should_pass": should_pass,
                "actual_pass": passed,
                "error": error,
                "decision": "PASS" if passed == should_pass else "HOLD_EVALUATOR_FAIL_CLOSED_GAP",
            }
        )
    return pd.DataFrame(rows)


def historical_reclassification(ledger: dict[str, dict[str, Any]]) -> pd.DataFrame:
    if not SHARED_POOL.exists():
        return pd.DataFrame()
    pool = pd.read_csv(SHARED_POOL)
    rows = []
    for _, row in pool.iterrows():
        fields = field_set(row.get("fields", ""))
        candidate_role, field_roles = role_for_fields(fields, ledger)
        role_violation = candidate_role == "role_violation"
        selected_alpha_like = truthy(row.get("eligible_for_alpha_proof")) or truthy(row.get("eligible_for_large_search"))
        rows.append(
            {
                "candidate_id": row.get("candidate_id", ""),
                "fields": "|".join(fields),
                "candidate_role": candidate_role,
                "field_roles": field_roles,
                "role_violation": role_violation,
                "selected_alpha_like": selected_alpha_like,
                "control_dominated_premay": truthy(row.get("is_control_dominated_premay")),
                "may_stress_failed": truthy(row.get("is_may_stress_failed")),
                "decision": "HOLD_ROLE_VIOLATION" if role_violation else ("DIAGNOSTIC_ONLY" if candidate_role != "ordinary_alpha_possible" else "ORDINARY_ALPHA_POSSIBLE"),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    a7aif1 = read_json(A7AIF1)
    if a7aif1.get("decision") != "PASS_A7AIF1_ENGINE_ENFORCEMENT_CONNECTED":
        raise SystemExit("A7AI-F1 is not connected")
    ledger = load_field_enforcement_csv(LEDGER_PATH)

    gen = generator_smoke(LEDGER_PATH)
    eval_audit = evaluator_fail_closed(ledger)
    hist = historical_reclassification(ledger)
    selector_trace = hist[["candidate_id", "candidate_role", "field_roles", "role_violation", "decision"]].copy() if not hist.empty else pd.DataFrame()
    violation_summary = (
        hist.groupby(["candidate_role", "decision"], dropna=False).size().reset_index(name="count")
        if not hist.empty
        else pd.DataFrame(columns=["candidate_role", "decision", "count"])
    )
    blockers = []
    if gen["decision"].astype(str).str.contains("HOLD").any():
        blockers.append("generator_mode_blocked_field_leak")
    if eval_audit["decision"].astype(str).str.contains("HOLD").any():
        blockers.append("evaluator_fail_closed_gap")
    if not hist.empty and bool(hist["role_violation"].any()):
        blockers.append("historical_pool_role_violation")
    decision = "PASS_A7AIF2_END_TO_END_ENFORCEMENT_CONNECTED" if not blockers else "HOLD_A7AIF2_ROLE_ENFORCEMENT_GAP"
    manifest = {
        "stage": "A7AI-F2",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "generator_mode_count": int(len(gen)),
        "historical_candidate_count": int(len(hist)),
        "role_violation_count": int(hist["role_violation"].sum()) if not hist.empty else 0,
        "authorizes_a7aif3": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    gen.to_csv(RUNTIME / "a7aif2_generator_mode_smoke.csv", index=False)
    eval_audit.to_csv(RUNTIME / "a7aif2_evaluator_fail_closed_audit.csv", index=False)
    selector_trace.to_csv(RUNTIME / "a7aif2_selector_role_trace_audit.csv", index=False)
    hist.to_csv(RUNTIME / "a7aif2_historical_candidate_role_reclassification.csv", index=False)
    violation_summary.to_csv(RUNTIME / "a7aif2_role_violation_summary.csv", index=False)
    write_json(RUNTIME / "a7aif2_manifest.json", manifest)
    write_json(RUNTIME / "a7aif2_authorization_matrix.json", {"A7AI-F2": {"status": decision}, "A7AI-F3": {"authorized": decision.startswith("PASS_")}, "search": {"authorized": False}})
    lines = [
        "# CRYPTO A7AI-F2 END TO END FIELD ENFORCEMENT REGRESSION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Generator Mode Smoke",
        "",
        md_table(gen, 20),
        "",
        "## Evaluator Fail-Closed Audit",
        "",
        md_table(eval_audit, 20),
        "",
        "## Historical Candidate Role Summary",
        "",
        md_table(violation_summary, 40),
        "",
        "## Boundary",
        "",
        "```text",
        "No formula search, replay execution, alpha proof, shadow, paper, or live execution is authorized.",
        "Diagnostic-only and risk-defense-only fields are not ordinary alpha replay seeds.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
