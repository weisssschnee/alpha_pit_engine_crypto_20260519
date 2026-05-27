from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import METHOD_FILE, REPORT_DIR, RUNTIME_DIR


A7I0_DIR = RUNTIME_DIR / "a7i0_runner_contract_audit"
DESIGN_PATH = REPORT_DIR / "CRYPTO_A7I_RESIDUAL_AWARE_SMALL_GENERATOR_DESIGN_20260519.md"
A7H_FINAL_PATH = REPORT_DIR / "CRYPTO_A7H_FINAL_DECISION_RECORD_20260519.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def check_contains(text: str, checks: dict[str, list[str]]) -> pd.DataFrame:
    rows = []
    lowered = text.lower()
    for group, terms in checks.items():
        for term in terms:
            rows.append(
                {
                    "group": group,
                    "required_term": term,
                    "present": term.lower() in lowered,
                }
            )
    return pd.DataFrame(rows)


def main() -> int:
    A7I0_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    design = DESIGN_PATH.read_text(encoding="utf-8")
    a7h_final = A7H_FINAL_PATH.read_text(encoding="utf-8")
    method = json.loads(METHOD_FILE.read_text(encoding="utf-8"))

    checks = {
        "may_boundary": [
            "known_adversarial_stress_set",
            "May cannot be used for ranking",
            "May is a stress gate only",
            "append-only locked-forward window",
        ],
        "execution_lag": [
            "execution_lag_1bar_stress",
            "1bar execution delay destroys all edge",
        ],
        "residual_baselines": [
            "residual vs FundingCore",
            "residual vs Core4",
            "FundingCore remains the primary residualization baseline",
        ],
        "placebo": [
            "sign flip",
            "row shuffle",
            "time shuffle",
            "wrong-lag future-funding diagnostic",
        ],
        "budget": [
            "generated candidates per arm: 250",
            "tradable replay candidates per arm: 64",
            "frequency: 1h only",
            "cost primary: 10bps",
            "cost stress: 20bps",
        ],
        "blocked_promotions": [
            "ALPHA_PROOF",
            "SHADOW_READY",
            "PAPER_READY",
            "PRODUCTION_READY",
        ],
    }
    check_df = check_contains(design, checks)
    check_path = A7I0_DIR / "crypto_a7i0_contract_checks_20260519.csv"
    check_df.to_csv(check_path, index=False)

    candidate_families = pd.DataFrame(
        [
            {
                "arm": "I0_basis_premium",
                "budget_generated": 250,
                "budget_replay": 64,
                "frequency": "1h",
                "may_usage": "stress_gate_only",
            },
            {
                "arm": "I1_flow_liquidity",
                "budget_generated": 250,
                "budget_replay": 64,
                "frequency": "1h",
                "may_usage": "stress_gate_only",
            },
            {
                "arm": "I2_microstructure_lite",
                "budget_generated": 250,
                "budget_replay": 64,
                "frequency": "1h",
                "may_usage": "stress_gate_only",
            },
            {
                "arm": "I3_placebo_random",
                "budget_generated": 250,
                "budget_replay": 64,
                "frequency": "1h",
                "may_usage": "stress_gate_only",
            },
        ]
    )
    family_path = A7I0_DIR / "crypto_a7i0_candidate_family_budget_20260519.csv"
    candidate_families.to_csv(family_path, index=False)

    unit_tests = pd.DataFrame(
        [
            {
                "test_name": "FundingCore_classified_as_mandatory_baseline",
                "expected_label": "MANDATORY_BASELINE_NOT_CANDIDATE",
                "source": "A7H final",
                "pass": "FundingCore" in a7h_final and "mandatory_baseline_only" in a7h_final,
            },
            {
                "test_name": "Core4_classified_as_research_benchmark",
                "expected_label": "RESEARCH_BENCHMARK_NOT_CANDIDATE",
                "source": "A7H final",
                "pass": "Core4" in a7h_final and "research_benchmark_only" in a7h_final,
            },
            {
                "test_name": "Taker_imbalance_classified_as_overlay_clue",
                "expected_label": "HOLD_RESIDUAL_ONLY_HEDGE_CLUE",
                "source": "A7H final",
                "pass": "taker_imbalance" in a7h_final and "hedge_overlay_clue_only" in a7h_final,
            },
            {
                "test_name": "Placebo_arm_required",
                "expected_label": "NEGATIVE_CONTROL",
                "source": "A7I design",
                "pass": "I3_placebo_random" in design,
            },
            {
                "test_name": "May_not_used_for_ranking",
                "expected_label": "CONTRACT_PASS",
                "source": "A7I design",
                "pass": "May cannot be used for ranking" in design and "May is a stress gate only" in design,
            },
        ]
    )
    unit_path = A7I0_DIR / "crypto_a7i0_unit_contract_tests_20260519.csv"
    unit_tests.to_csv(unit_path, index=False)

    missing = check_df[~check_df["present"]]
    failed_tests = unit_tests[~unit_tests["pass"]]
    blockers = []
    if not missing.empty:
        blockers.append("design_missing_required_contract_terms")
    if not failed_tests.empty:
        blockers.append("unit_contract_tests_failed")
    if method["temporal_splits"]["recent_oos"]["end"] != "2026-04-30T23:59:59Z":
        blockers.append("recent_oos_split_not_frozen_before_may")
    decision = "PASS_A7I0_RUNNER_CONTRACT_AUDIT" if not blockers else "HOLD_A7I0_RUNNER_CONTRACT_INCOMPLETE"

    manifest = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "stage": "A7I-0 runner contract implementation audit",
        "executes_search": False,
        "authorizes_a7i1": decision == "PASS_A7I0_RUNNER_CONTRACT_AUDIT",
        "authorizes_alpha_proof": False,
        "design_sha256": sha256_text(design),
        "a7h_final_sha256": sha256_text(a7h_final),
        "method_file": str(METHOD_FILE),
        "method_recent_oos_end": method["temporal_splits"]["recent_oos"]["end"],
        "outputs": {
            "contract_checks": str(check_path),
            "candidate_family_budget": str(family_path),
            "unit_contract_tests": str(unit_path),
        },
    }
    manifest_path = A7I0_DIR / "crypto_a7i0_manifest_20260519.json"
    write_json(manifest_path, manifest)

    report_path = REPORT_DIR / "CRYPTO_A7I0_RUNNER_CONTRACT_AUDIT_20260519.md"
    lines = [
        "# Crypto A7I-0 Runner Contract Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        f"- executes_search: `False`",
        f"- authorizes_a7i1: `{manifest['authorizes_a7i1']}`",
        f"- authorizes_alpha_proof: `False`",
        f"- blockers: `{blockers}`",
        "",
        "## Scope",
        "",
        "A7I-0 verifies that the residual-aware small generator contract is explicit before any A7I-1 search/smoke is run.",
        "",
        "## Required Contract Checks",
        "",
        "| group | checks | pass count | total |",
        "|---|---:|---:|---:|",
    ]
    grouped = check_df.groupby("group")["present"].agg(["sum", "count"]).reset_index()
    for _, row in grouped.iterrows():
        lines.append(f"| `{row['group']}` |  | {int(row['sum'])} | {int(row['count'])} |")
    lines += [
        "",
        "## Unit Contract Tests",
        "",
        "| test | expected | pass |",
        "|---|---|---:|",
    ]
    for _, row in unit_tests.iterrows():
        lines.append(f"| `{row['test_name']}` | `{row['expected_label']}` | `{bool(row['pass'])}` |")
    lines += [
        "",
        "## Decision Boundary",
        "",
        "- PASS allows implementing A7I-1 small matched-budget residual-aware generator smoke.",
        "- PASS does not authorize alpha proof, A7.3 old bakeoff, shadow, paper, or live.",
        "- May 2026 is locked as known adversarial stress and cannot be used for ranking.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("A7I0_REPORT=" + str(report_path))
    print("A7I0_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
