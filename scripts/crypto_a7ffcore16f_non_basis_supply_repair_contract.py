from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16f_non_basis_supply_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16F_NON_BASIS_SUPPLY_REPAIR_CONTRACT_20260601.md"
CORE16ER = REPO / "runtime" / "a7ffcore16er_expanded_atlas_forensic" / "a7ffcore16er_manifest.json"
FAMILY_SUPPLY = REPO / "runtime" / "a7ffcore16er_expanded_atlas_forensic" / "a7ffcore16er_family_supply_forensic.csv"
FAMILY_CONCENTRATION = REPO / "runtime" / "a7ffcore16er_expanded_atlas_forensic" / "a7ffcore16er_family_concentration.csv"


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

    core16er = read_json(CORE16ER)
    if core16er.get("decision") != "PASS_A7FFCORE16ER_EXPANDED_ATLAS_FORENSIC_COMPLETE_READY_FOR_CORE16F":
        raise SystemExit(f"CORE16ER is not ready for CORE16F: {core16er.get('decision')}")

    family_supply = load_csv(FAMILY_SUPPLY)
    concentration = load_csv(FAMILY_CONCENTRATION)

    target_families = pd.DataFrame(
        [
            {
                "field_family": "open_interest",
                "repair_priority": 1,
                "allowed_transforms": "delta_1h;delta_4h;delta_24h;zscore_72h;zscore_168h;tsrank_72h;spread_short_long",
                "family_native_labels": "L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return",
                "probe_policy": "single-field plus OI-price/OI-funding interaction probe, no open grammar",
                "minimum_non_basis_candidates": 8,
            },
            {
                "field_family": "positioning",
                "repair_priority": 2,
                "allowed_transforms": "level;delta_4h;delta_24h;zscore_168h;spread_short_long",
                "family_native_labels": "L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return",
                "probe_policy": "divergence and crowding probes only",
                "minimum_non_basis_candidates": 8,
            },
            {
                "field_family": "taker_flow",
                "repair_priority": 3,
                "allowed_transforms": "delta_1h;delta_4h;zscore_72h;shock_24h;tsrank_72h",
                "family_native_labels": "L0_raw_forward_return;L1_cross_sectional_relative_return;L5_vol_adjusted_return",
                "probe_policy": "flow imbalance and reversal probes; require controls weaker than original",
                "minimum_non_basis_candidates": 6,
            },
            {
                "field_family": "liquidity",
                "repair_priority": 4,
                "allowed_transforms": "delta_4h;delta_24h;zscore_168h;tsrank_168h;shock_24h",
                "family_native_labels": "L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return",
                "probe_policy": "state/neutralizer first; standalone signal only if non-L7 and control-clean",
                "minimum_non_basis_candidates": 4,
            },
            {
                "field_family": "volatility",
                "repair_priority": 5,
                "allowed_transforms": "delta_4h;delta_24h;zscore_72h;zscore_168h;spread_short_long",
                "family_native_labels": "L3_liquidity_tier_relative_return;L5_vol_adjusted_return",
                "probe_policy": "risk-state and reversal pressure probes; no pure volatility beta wrapper",
                "minimum_non_basis_candidates": 4,
            },
            {
                "field_family": "price_return",
                "repair_priority": 6,
                "allowed_transforms": "delta_1h;delta_4h;zscore_72h;tsrank_72h;shock_24h",
                "family_native_labels": "L1_cross_sectional_relative_return;L3_liquidity_tier_relative_return;L5_vol_adjusted_return",
                "probe_policy": "use only as interaction/control baseline; cap standalone exposure",
                "minimum_non_basis_candidates": 2,
            },
        ]
    )

    cap_policy = pd.DataFrame(
        [
            {
                "policy_id": "basis_premium_cap",
                "field_family": "basis_premium",
                "max_share_in_core16fe_queue": 0.35,
                "reason": "CORE16E basis_premium share was 96.6 percent",
            },
            {
                "policy_id": "non_basis_floor",
                "field_family": "non_basis_total",
                "min_candidate_count": 32,
                "min_field_family_count": 4,
                "reason": "CORE17 requires breadth before objective seed policy",
            },
            {
                "policy_id": "family_native_gate",
                "field_family": "all",
                "gate": "premay_all_positive and control_ratio < 1.0; lag_ok is diagnostic flag, not hard reject",
                "reason": "avoid over-conservative latency filtering while still rejecting control-like responses",
            },
            {
                "policy_id": "near_miss_lane",
                "field_family": "non_basis",
                "gate": "control_ratio between 1.0 and 1.5 may enter forensic-only lane",
                "reason": "surface repair evidence without promoting control-like rows",
            },
        ]
    )

    execution_contract = {
        "stage": "A7FF-CORE16FE",
        "name": "non-basis expanded primitive/operator atlas execution",
        "authorized": True,
        "executes_replay": False,
        "executes_search": False,
        "families": target_families["field_family"].tolist(),
        "labels": [
            "L0_raw_forward_return",
            "L1_cross_sectional_relative_return",
            "L3_liquidity_tier_relative_return",
            "L5_vol_adjusted_return",
        ],
        "horizons": [1, 4, 8, 24],
        "basis_premium_max_share": 0.35,
        "non_basis_min_candidate_count": 32,
        "non_basis_min_field_family_count": 4,
        "top_family_share_max": 0.50,
        "forbidden": [
            "formula generation",
            "bounded replay",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }

    blocked = pd.DataFrame(
        [
            {"item": "A7FF-CORE17 objective seed policy", "reason": "blocked until CORE16FE non-basis supply passes"},
            {"item": "formula generation", "reason": "blocked until primitive/operator supply has non-basis breadth"},
            {"item": "bounded replay", "reason": "blocked until objective atlas breadth exists"},
            {"item": "large search", "reason": "blocked"},
            {"item": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )

    decision = "PASS_A7FFCORE16F_NON_BASIS_SUPPLY_REPAIR_CONTRACT_READY_FOR_CORE16FE"
    manifest = {
        "stage": "A7FF-CORE16F",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16ER",
        "source_decision": core16er.get("decision"),
        "decision": decision,
        "authorizes_core16fe": True,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16FE non-basis expanded primitive/operator atlas execution",
    }

    family_supply.to_csv(RUNTIME / "a7ffcore16f_source_family_supply_forensic.csv", index=False)
    concentration.to_csv(RUNTIME / "a7ffcore16f_source_family_concentration.csv", index=False)
    target_families.to_csv(RUNTIME / "a7ffcore16f_target_family_policy.csv", index=False)
    cap_policy.to_csv(RUNTIME / "a7ffcore16f_cap_and_floor_policy.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore16f_blocked_actions.csv", index=False)
    write_json(RUNTIME / "a7ffcore16f_execution_contract.json", execution_contract)
    write_json(RUNTIME / "a7ffcore16f_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE16F NON-BASIS SUPPLY REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16F is a contract stage. It defines how to repair non-basis primitive/operator supply after CORE16E showed a 96.6% basis/premium concentration. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Target Family Policy",
        "",
        md_table(target_families),
        "",
        "## Cap / Floor Policy",
        "",
        md_table(cap_policy),
        "",
        "## Execution Contract",
        "",
        "```json",
        json.dumps(execution_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Family Concentration",
        "",
        md_table(concentration),
        "",
        "## Blocked Actions",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
