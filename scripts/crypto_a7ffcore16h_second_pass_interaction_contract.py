from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16h_second_pass_interaction_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16H_SECOND_PASS_INTERACTION_CONTRACT_20260601.md"
CORE16GER = REPO / "runtime" / "a7ffcore16ger_interaction_probe_forensic" / "a7ffcore16ger_manifest.json"
CANDIDATE_BREAKDOWN = REPO / "runtime" / "a7ffcore16ger_interaction_probe_forensic" / "a7ffcore16ger_candidate_breakdown.csv"
NEAR_MISS_BREAKDOWN = REPO / "runtime" / "a7ffcore16ger_interaction_probe_forensic" / "a7ffcore16ger_near_miss_breakdown.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


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

    core16ger = read_json(CORE16GER)
    if core16ger.get("decision") != "PASS_A7FFCORE16GER_INTERACTION_FORENSIC_COMPLETE_READY_FOR_CORE16H":
        raise SystemExit(f"CORE16GER is not ready for CORE16H: {core16ger.get('decision')}")

    candidate_breakdown = load_csv(CANDIDATE_BREAKDOWN)
    near_breakdown = load_csv(NEAR_MISS_BREAKDOWN)

    second_pass_families = pd.DataFrame(
        [
            {
                "family": "H0_I3_deconcentration",
                "source_interaction": "I3_positioning_divergence_x_price_or_basis",
                "action": "cap Sub/L5 concentration; add asymmetric transforms positioning:spread_short_long|zscore_168h with price/basis:delta_24h|shock_24h",
                "target": "keep I3 useful while preventing single operator/label dominance",
            },
            {
                "family": "H1_I5_deconcentration",
                "source_interaction": "I5_liquidity_state_x_basis_or_positioning",
                "action": "cap Mul/L5; add SafeDiv and Sub only where semantic scale permits; require non-L5 share",
                "target": "convert liquidity-state interaction into diversified candidate supply",
            },
            {
                "family": "H2_I4_near_miss_repair",
                "source_interaction": "I4_taker_flow_x_OI_or_liquidity",
                "action": "expand asymmetric transforms around near-miss rows; evaluate flow reversal under OI/liquidity context",
                "target": "turn best non-I3/I5 near-miss lane into strict candidates",
            },
            {
                "family": "H3_cross_family_bridge",
                "source_interaction": "I3/I5/I4",
                "action": "build low-count bridge probes that combine positioning/liquidity/taker context without basis dominance",
                "target": "raise interaction family count to at least 3 without open grammar",
            },
        ]
    )

    cap_policy = pd.DataFrame(
        [
            {"policy_id": "i3_i5_top_share_cap", "value": "each <= 45%", "reason": "CORE16GE top family share was 59.5%"},
            {"policy_id": "non_l5_label_floor", "value": ">= 40%", "reason": "avoid ranked/vol-only label concentration"},
            {"policy_id": "operator_floor", "value": ">= 2 operators", "reason": "avoid single Sub/Mul morphology"},
            {"policy_id": "i4_floor", "value": ">= 12 strict or near-strict rows", "reason": "force non-I3/I5 expansion lane to be tested"},
            {"policy_id": "control_gate", "value": "strict < 1.0; forensic 1.0-1.5", "reason": "do not promote control-like interactions"},
        ]
    )

    execution_contract = {
        "stage": "A7FF-CORE16HE",
        "name": "second-pass interaction breadth execution",
        "authorized": True,
        "executes_replay": False,
        "executes_search": False,
        "max_blueprints": 4096,
        "families": second_pass_families["family"].tolist(),
        "pass_gate": {
            "candidate_count": 96,
            "interaction_family_count": 3,
            "top_family_share_max": 0.45,
            "operator_count_min": 2,
            "non_l5_label_share_min": 0.40,
            "i4_floor": 12,
        },
        "forbidden": [
            "open grammar FormulaGen",
            "bounded replay",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }

    blocked = pd.DataFrame(
        [
            {"item": "A7FF-CORE17 objective seed policy", "reason": "blocked until CORE16HE breadth execution passes"},
            {"item": "formula generation", "reason": "blocked: only second-pass typed interaction execution is authorized"},
            {"item": "bounded replay", "reason": "blocked: no broad objective atlas"},
            {"item": "large search", "reason": "blocked"},
            {"item": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )

    decision = "PASS_A7FFCORE16H_SECOND_PASS_INTERACTION_CONTRACT_READY_FOR_CORE16HE"
    manifest = {
        "stage": "A7FF-CORE16H",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16GER",
        "source_decision": core16ger.get("decision"),
        "decision": decision,
        "authorizes_core16he": True,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16HE second-pass interaction breadth execution",
    }

    candidate_breakdown.to_csv(RUNTIME / "a7ffcore16h_source_candidate_breakdown.csv", index=False)
    near_breakdown.to_csv(RUNTIME / "a7ffcore16h_source_near_miss_breakdown.csv", index=False)
    second_pass_families.to_csv(RUNTIME / "a7ffcore16h_second_pass_family_policy.csv", index=False)
    cap_policy.to_csv(RUNTIME / "a7ffcore16h_cap_policy.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore16h_blocked_actions.csv", index=False)
    write_json(RUNTIME / "a7ffcore16h_execution_contract.json", execution_contract)
    write_json(RUNTIME / "a7ffcore16h_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE16H SECOND-PASS INTERACTION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16H defines the second-pass interaction breadth repair. It is still not formula generation, replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Second-Pass Families",
        "",
        md_table(second_pass_families),
        "",
        "## Cap Policy",
        "",
        md_table(cap_policy),
        "",
        "## Execution Contract",
        "",
        "```json",
        json.dumps(execution_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Candidate Breakdown",
        "",
        md_table(candidate_breakdown),
        "",
        "## Blocked Actions",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
