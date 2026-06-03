from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE53I = REPO / "runtime" / "a7ffcore53i_factor_input_information_audit"
RUNTIME = REPO / "runtime" / "a7ffcore53ir_factor_input_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE53IR_FACTOR_INPUT_REPAIR_CONTRACT_20260603.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE53I / "a7ffcore53i_manifest.json")
    if not source.get("authorizes_factor_input_repair"):
        raise SystemExit(f"CORE53IR not authorized by CORE53I: {source.get('decision')}")
    type_usage = pd.read_csv(CORE53I / "a7ffcore53i_field_type_usage.csv")
    field_usage = pd.read_csv(CORE53I / "a7ffcore53i_base_field_usage.csv")
    type_redundancy = pd.read_csv(CORE53I / "a7ffcore53i_input_type_redundancy.csv")

    field_type_policy = pd.DataFrame(
        [
            {"field_type": "price_like", "max_candidate_share": 0.30, "min_candidate_share": 0.05, "role": "baseline_or_interaction_only"},
            {"field_type": "funding_like", "max_candidate_share": 0.25, "min_candidate_share": 0.05, "role": "signal_or_state"},
            {"field_type": "positioning_like", "max_candidate_share": 0.25, "min_candidate_share": 0.08, "role": "signal_or_state"},
            {"field_type": "basis_premium_like", "max_candidate_share": 0.25, "min_candidate_share": 0.05, "role": "signal_or_state"},
            {"field_type": "liquidity_like", "max_candidate_share": 0.25, "min_candidate_share": 0.05, "role": "interaction_or_neutralizer"},
            {"field_type": "volatility_like", "max_candidate_share": 0.20, "min_candidate_share": 0.04, "role": "risk_scale_or_interaction"},
            {"field_type": "state_or_taxonomy", "max_candidate_share": 0.20, "min_candidate_share": 0.03, "role": "condition_or_neutralizer"},
            {"field_type": "generic_numeric", "max_candidate_share": 0.10, "min_candidate_share": 0.00, "role": "restricted_until_retyped"},
        ]
    )
    pair_policy = pd.DataFrame(
        [
            {"pair_rule": "single_price_like", "status": "cap", "max_share": 0.12, "reason": "price-like standalone often wraps market beta"},
            {"pair_rule": "single_funding_like", "status": "cap", "max_share": 0.10, "reason": "funding standalone has high control sensitivity"},
            {"pair_rule": "positioning_like|funding_like", "status": "require_quota", "min_share": 0.06, "reason": "crowding plus leverage-state interaction"},
            {"pair_rule": "positioning_like|basis_premium_like", "status": "require_quota", "min_share": 0.05, "reason": "leverage expansion under dislocation"},
            {"pair_rule": "positioning_like|liquidity_like", "status": "require_quota", "min_share": 0.05, "reason": "crowding under tradability/liquidity state"},
            {"pair_rule": "funding_like|volatility_like", "status": "require_quota", "min_share": 0.04, "reason": "crowding under volatility state"},
            {"pair_rule": "basis_premium_like|liquidity_like", "status": "require_quota", "min_share": 0.04, "reason": "dislocation with tradability"},
            {"pair_rule": "state_or_taxonomy interactions", "status": "condition_only", "max_share": 0.15, "reason": "state fields should not dominate standalone alpha"},
        ]
    )
    queue_gate = {
        "candidate_queue_requirements": {
            "min_candidate_count": 384,
            "min_input_type_count": 7,
            "min_strict_candidate_input_type_count_after_repaired_targets": 3,
            "max_top_input_type_share": 0.35,
            "max_top_base_field_share": 0.25,
            "max_top_input_field_set_share": 0.08,
            "min_required_interaction_pair_count": 5,
            "no_single_price_or_funding_dominance": True,
        },
        "strict_promotion_requirements": {
            "min_independent_repaired_target_count": 3,
            "min_input_type_count": 3,
            "min_semantic_pair_count": 3,
            "median_control_ratio_max": 0.90,
            "requires_positive_portfolio_net_spread_proxy": True,
        },
        "forbidden": [
            "counting multiple formulas with identical input field set as independent breadth",
            "counting L0_raw and L1_xs as independent label evidence",
            "allowing one strict clue from one input type to authorize search",
            "expanding formula search before repaired target replay passes input breadth gate",
        ],
    }
    repair_actions = pd.DataFrame(
        [
            {"action_id": "R0", "action": "retype derived/regime fields from compact frame before formula selection", "required": True},
            {"action_id": "R1", "action": "apply field-type quota before materialization queue selection", "required": True},
            {"action_id": "R2", "action": "apply input-field-set cap before selector/replay", "required": True},
            {"action_id": "R3", "action": "force minimum OI/positioning interaction supply", "required": True},
            {"action_id": "R4", "action": "force minimum funding/basis/liquidity/volatility interaction supply", "required": True},
            {"action_id": "R5", "action": "separate condition/state variables from standalone alpha fields", "required": True},
            {"action_id": "R6", "action": "rerun CORE53I after repaired queue construction", "required": True},
        ]
    )
    current_snapshot = {
        "top_base_field_share": source.get("top_base_field_share"),
        "top_input_type_share": source.get("top_input_type_share"),
        "top_input_field_set_share": source.get("top_input_field_set_share"),
        "diagnostic_input_type_count": source.get("diagnostic_input_type_count"),
        "strict_input_type_count": source.get("strict_input_type_count"),
        "blockers": source.get("blockers"),
    }
    manifest = {
        "stage": "A7FF-CORE53IR",
        "generated_at": now_utc(),
        "source_stage": source.get("stage"),
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE53IR_FACTOR_INPUT_REPAIR_CONTRACT_READY_FOR_REPAIRED_QUEUE_BUILDER",
        "executes_replay": False,
        "executes_search": False,
        "field_type_policy_count": int(field_type_policy.shape[0]),
        "pair_policy_count": int(pair_policy.shape[0]),
        "repair_action_count": int(repair_actions.shape[0]),
        "authorizes_repaired_queue_builder_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    authorization = {
        "authorized": {
            "A7FF-CORE54 repaired factor-input queue builder contract": True,
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    field_type_policy.to_csv(RUNTIME / "a7ffcore53ir_field_type_quota_policy.csv", index=False)
    pair_policy.to_csv(RUNTIME / "a7ffcore53ir_pair_quota_policy.csv", index=False)
    repair_actions.to_csv(RUNTIME / "a7ffcore53ir_repair_actions.csv", index=False)
    type_usage.to_csv(RUNTIME / "a7ffcore53ir_source_field_type_usage.csv", index=False)
    field_usage.to_csv(RUNTIME / "a7ffcore53ir_source_base_field_usage.csv", index=False)
    type_redundancy.to_csv(RUNTIME / "a7ffcore53ir_source_input_type_redundancy.csv", index=False)
    write_json(RUNTIME / "a7ffcore53ir_queue_gate_policy.json", queue_gate)
    write_json(RUNTIME / "a7ffcore53ir_current_snapshot.json", current_snapshot)
    write_json(RUNTIME / "a7ffcore53ir_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore53ir_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE53IR FACTOR INPUT REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE53IR turns CORE53I factor-input redundancy findings into queue construction constraints. It does not execute generation, replay, search, proof, or promotion.",
        "",
        "## Current Snapshot",
        "",
        "```json",
        json.dumps(current_snapshot, indent=2, sort_keys=True),
        "```",
        "",
        "## Field Type Quota Policy",
        "",
        md_table(field_type_policy),
        "",
        "## Pair Quota Policy",
        "",
        md_table(pair_policy),
        "",
        "## Repair Actions",
        "",
        md_table(repair_actions),
        "",
        "## Queue Gate",
        "",
        "```json",
        json.dumps(queue_gate, indent=2, sort_keys=True),
        "```",
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
