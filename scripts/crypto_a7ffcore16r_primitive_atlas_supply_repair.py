from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16r_primitive_atlas_supply_repair"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16R_PRIMITIVE_ATLAS_SUPPLY_REPAIR_20260601.md"
CORE16 = REPO / "runtime" / "a7ffcore16_primitive_replay_stability_atlas" / "a7ffcore16_manifest.json"
CORE16_FAMILY = REPO / "runtime" / "a7ffcore16_primitive_replay_stability_atlas" / "a7ffcore16_field_type_by_label_horizon_stability.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
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
    core16 = read_json(CORE16)
    if core16.get("decision") != "HOLD_A7FFCORE16_PRIMITIVE_ATLAS_INSUFFICIENT":
        raise SystemExit(f"A7FF-CORE16 is not in repair state: {core16.get('decision')}")
    family = pd.read_csv(CORE16_FAMILY)
    repair_actions = pd.DataFrame(
        [
            {
                "action_id": "R0_expand_non_l7_primitive_probe",
                "requirement": "rerun/extend primitive response map with more transforms and less L7 absorption",
                "minimum": ">=64 non-L7 atlas candidates, >=6 field families, >=5 transforms",
            },
            {
                "action_id": "R1_operator_probing",
                "requirement": "score field_family x operator x label x horizon before factor generation",
                "minimum": "operator families must pass control_ratio < 1.0 and split consistency before generation",
            },
            {
                "action_id": "R2_field_family_quota",
                "requirement": "explicitly quota open_interest, positioning, taker_flow, liquidity, volatility, basis/funding",
                "minimum": "no single family >30 percent in atlas",
            },
            {
                "action_id": "R3_lag_fragility_repair",
                "requirement": "separate lag-fragile from control-clean; do not discard all lag-fragile fields without slow-horizon retest",
                "minimum": "slow-horizon retest contract for 4h/8h/24h primitive transforms",
            },
            {
                "action_id": "R4_no_search_until_supply_pass",
                "requirement": "formula search remains blocked until primitive atlas supply passes",
                "minimum": "CORE16R/CORE16E pass before any new generation/replay",
            },
        ]
    )
    next_contract = {
        "stage": "A7FF-CORE16E",
        "action": "expanded primitive/operator-probe atlas execution",
        "inputs": [
            "top498 feature panel",
            "A7AA label contract",
            "field role ledger",
            "CORE16 insufficient atlas",
        ],
        "transforms": [
            "level",
            "delta_1h",
            "delta_4h",
            "delta_24h",
            "zscore_72h",
            "zscore_168h",
            "tsrank_72h",
            "tsrank_168h",
            "shock_24h",
            "spread_short_long",
        ],
        "labels": [
            "L0_raw_forward_return",
            "L1_cross_sectional_relative_return",
            "L3_liquidity_tier_relative_return",
            "L5_vol_adjusted_return",
        ],
        "horizons": [1, 4, 8, 24],
        "pass_gate": {
            "atlas_candidate_count": 64,
            "field_family_count": 6,
            "transform_count": 5,
            "top_family_share_max": 0.30,
        },
        "forbidden": [
            "formula search",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }
    blocked = pd.DataFrame(
        [
            {"item": "CORE17 objective seed policy", "reason": "blocked: CORE16 atlas supply insufficient"},
            {"item": "formula generation", "reason": "blocked until expanded primitive atlas passes"},
            {"item": "bounded replay", "reason": "blocked until supply repair yields broader objective atlas"},
            {"item": "large search", "reason": "blocked"},
            {"item": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )
    repair_actions.to_csv(RUNTIME / "a7ffcore16r_repair_actions.csv", index=False)
    family.to_csv(RUNTIME / "a7ffcore16r_source_family_stability.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore16r_blocked_actions.csv", index=False)
    write_json(RUNTIME / "a7ffcore16r_next_contract.json", next_contract)
    decision = "PASS_A7FFCORE16R_PRIMITIVE_ATLAS_SUPPLY_REPAIR_READY_FOR_CORE16E"
    manifest = {
        "stage": "A7FF-CORE16R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16",
        "source_decision": core16.get("decision"),
        "decision": decision,
        "authorizes_core16e": True,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16E expanded primitive/operator-probe atlas execution",
    }
    write_json(RUNTIME / "a7ffcore16r_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16R PRIMITIVE ATLAS SUPPLY REPAIR",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE16R defines a supply repair for the primitive replay-stability atlas. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Repair Actions",
        "",
        md_table(repair_actions),
        "",
        "## Next Contract",
        "",
        "```json",
        json.dumps(next_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Blocked Actions",
        "",
        md_table(blocked),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
