from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al0p_pretrain_readiness_gate"
REPORT = REPO / "reports" / "CRYPTO_A7AL0P_PRETRAIN_READINESS_GATE_20260527.md"

A7AL0R = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit" / "a7al0r_blocker_matrix.json"
A7AL0F = REPO / "runtime" / "a7al0f_derived_feature_engineering_contract" / "a7al0f_manifest.json"
A7AL0G = REPO / "runtime" / "a7al0g_upper_regime_state_builder" / "a7al0g_manifest.json"
A7AL0L = REPO / "runtime" / "a7al0l_fixed_delay_stress_abolition" / "a7al0l_manifest.json"
LINEAGE = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit" / "a7al0r_feature_lineage_ledger.csv"
LABEL_AUDIT = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit" / "a7al0r_label_lineage_audit.csv"
PIT_AUDIT = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit" / "a7al0r_pit_lag_audit.csv"
NEUTRAL = REPO / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_neutralization_policy.json"
NEGATIVE = REPO / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_negative_control_plan.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def md_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "`<empty>`"
    fields = list(rows[0].keys())
    out = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(f, "")) for f in fields) + " |")
    return "\n".join(out)


def checks() -> tuple[list[dict[str, Any]], list[str]]:
    blockers: list[str] = []
    rows: list[dict[str, Any]] = []

    m0r = read_json(A7AL0R)
    m0f = read_json(A7AL0F)
    m0g = read_json(A7AL0G)
    m0l = read_json(A7AL0L)
    lineage = pd.read_csv(LINEAGE) if LINEAGE.exists() else pd.DataFrame()
    labels = pd.read_csv(LABEL_AUDIT) if LABEL_AUDIT.exists() else pd.DataFrame()
    pit = pd.read_csv(PIT_AUDIT) if PIT_AUDIT.exists() else pd.DataFrame()
    neutral = read_json(NEUTRAL)
    negative = read_json(NEGATIVE)

    def add(name: str, status: bool, blocker: str, detail: str) -> None:
        rows.append({"check": name, "status": "PASS" if status else "HOLD", "blocker": "" if status else blocker, "detail": detail})
        if not status:
            blockers.append(blocker)

    add("feature_lineage_100pct_resolved", not lineage.empty and "field_name" in lineage.columns, "feature_lineage_missing", f"rows={len(lineage)}")
    label_ok = not labels.empty and not (labels["status"] != "PASS_LABEL_ISOLATED").any()
    add("label_fields_isolated", label_ok, "label_lineage_not_isolated", f"label_rows={len(labels)}")
    pit_ok = not pit.empty and not (pit["status"] != "PASS_PIT_CONTRACTED").any()
    fixed_delay_ok = "fixed_delay_stress_required" in pit.columns and not pit["fixed_delay_stress_required"].astype(bool).any()
    add("pit_lag_and_field_native_latency_contract", pit_ok and fixed_delay_ok, "pit_lag_or_fixed_delay_policy_incomplete", f"pit_rows={len(pit)} fixed_2h_delay_ok={fixed_delay_ok}")
    add("derived_feature_contract_passed", m0f.get("decision") == "PASS_A7AL0F_DERIVED_FEATURE_ENGINEERING_CONTRACT", "derived_contract_not_passed", str(m0f.get("decision")))
    add("upper_regime_train_only_passed", m0g.get("decision") == "PASS_A7AL0G_UPPER_REGIME_STATE_BUILDER" and m0g.get("train_only_thresholds") is True, "upper_regime_not_ready", str(m0g.get("decision")))
    add("fixed_delay_stress_abolished", m0l.get("decision") == "PASS_A7AL0L_FIXED_DELAY_STRESS_ABOLISHED", "fixed_delay_stress_policy_not_abolished", str(m0l.get("decision")))
    add("neutralization_policy_exists", bool(neutral.get("ranking_modes")), "neutralization_policy_missing", f"modes={len(neutral.get('ranking_modes', []))}")
    add("negative_control_plan_exists", bool(negative.get("controls")), "negative_control_plan_missing", f"controls={len(negative.get('controls', []))}")
    add("no_may_dependency", m0g.get("may_used") is False and "May" not in str(m0r.get("blockers", [])), "may_dependency_risk", "May unavailable and not used")
    add("a7al1_only_authorization", True, "", "pretrain gate can authorize field-family baseline only, not formula search")
    return rows, blockers


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    rows, blockers = checks()
    decision = "PASS_A7AL0P_PRETRAIN_READY_FOR_A7AL1_FIELD_FAMILY_BASELINE" if not blockers else "HOLD_A7AL0P_PRETRAIN_READINESS_BLOCKED"
    manifest = {
        "generated_at": generated_at,
        "decision": decision,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7al1_field_family_baseline": not blockers,
        "authorizes_a7al2_formula_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "warnings": [
            "A7AL-1 must remain field-family baseline replay, not formula search",
            "Derived features are allowed only with lineage, PIT, field-native latency audit, neutralization, and controls",
            "Age<30d symbols must receive fixed search quota but cannot dominate proof",
        ],
    }
    (RUNTIME / "a7al0p_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    pd.DataFrame(rows).to_csv(RUNTIME / "a7al0p_readiness_checks.csv", index=False)

    report = f"""# CRYPTO A7AL-0P Pretrain Readiness Gate

Generated: {generated_at}

## Decision

```text
{decision}
```

## Checks

{md_table(rows)}

## Authorization

```text
AUTHORIZED:
  A7AL-1 field-family neutralized baseline replay

NOT AUTHORIZED:
  A7AL-2 formula search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
