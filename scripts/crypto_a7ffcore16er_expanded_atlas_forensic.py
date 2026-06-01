from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16er_expanded_atlas_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16ER_EXPANDED_ATLAS_FORENSIC_20260601.md"
CORE16E_DIR = REPO / "runtime" / "a7ffcore16e_expanded_primitive_operator_atlas"
CORE16E_MANIFEST = CORE16E_DIR / "a7ffcore16e_manifest.json"
CORE16E_ATLAS = CORE16E_DIR / "a7ffcore16e_candidate_objective_atlas.csv"
CORE16E_SCOREBOARD = CORE16E_DIR / "a7ffcore16e_operator_family_scoreboard.csv"
CORE16E_DECISIONS = CORE16E_DIR / "a7ffcore16e_decision_counts.csv"


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


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest16e = read_json(CORE16E_MANIFEST)
    if manifest16e.get("decision") != "HOLD_A7FFCORE16E_EXPANDED_PRIMITIVE_ATLAS_INSUFFICIENT":
        raise SystemExit(f"CORE16E is not in forensic state: {manifest16e.get('decision')}")

    atlas = load_csv(CORE16E_ATLAS)
    scoreboard = load_csv(CORE16E_SCOREBOARD)
    decisions = load_csv(CORE16E_DECISIONS)

    if atlas.empty:
        family_concentration = pd.DataFrame(
            columns=[
                "field_family",
                "atlas_candidate_count",
                "share",
                "transform_count",
                "label_family_count",
                "lag_ok_candidate_count",
                "median_control_ratio",
                "status",
            ]
        )
    else:
        family_concentration = (
            atlas.groupby("field_family", dropna=False)
            .agg(
                atlas_candidate_count=("atlas_candidate", "size"),
                transform_count=("transform", "nunique"),
                label_family_count=("label_family", "nunique"),
                lag_ok_candidate_count=("lag_ok", "sum"),
                median_control_ratio=("control_ratio_premay_max", "median"),
            )
            .reset_index()
        )
        total = float(family_concentration["atlas_candidate_count"].sum())
        family_concentration["share"] = family_concentration["atlas_candidate_count"] / total if total else 0.0
        family_concentration["status"] = family_concentration.apply(
            lambda row: "dominant_saturated_family"
            if row["share"] > 0.50
            else ("thin_positive_supply" if row["atlas_candidate_count"] > 0 else "zero_supply"),
            axis=1,
        )
        family_concentration = family_concentration[
            [
                "field_family",
                "atlas_candidate_count",
                "share",
                "transform_count",
                "label_family_count",
                "lag_ok_candidate_count",
                "median_control_ratio",
                "status",
            ]
        ].sort_values(["atlas_candidate_count", "field_family"], ascending=[False, True])

    if scoreboard.empty:
        family_supply = pd.DataFrame()
    else:
        family_supply = (
            scoreboard.groupby("field_family", dropna=False)
            .agg(
                scored_rows=("rows", "sum"),
                atlas_candidate_count=("atlas_candidate_count", "sum"),
                lag_ok_candidate_count=("lag_ok_candidate_count", "sum"),
                near_miss_count=("near_miss_count", "sum"),
                median_control_ratio=("median_control_ratio", "median"),
                transform_count=("transform", "nunique"),
                label_family_count=("label_family", "nunique"),
            )
            .reset_index()
        )
        family_supply["supply_class"] = family_supply.apply(
            lambda row: "positive_concentrated"
            if row["atlas_candidate_count"] >= 16
            else ("near_miss_repairable" if row["near_miss_count"] > 0 else "zero_or_control_like"),
            axis=1,
        )
        family_supply = family_supply.sort_values(["atlas_candidate_count", "near_miss_count"], ascending=[False, False])

    repair_actions = pd.DataFrame(
        [
            {
                "action_id": "R0_cap_basis_premium_atlas",
                "target": "basis_premium",
                "action": "treat as saturated diagnostic supply; cap in any future atlas/queue until non-basis families show supply",
                "reason": "CORE16E top_family_share is above 96 percent even after lag gate relaxation",
            },
            {
                "action_id": "R1_non_basis_near_miss_repair",
                "target": "open_interest, price_return, positioning, listing_age",
                "action": "mine near-miss rows with control_ratio between 1.0 and 1.5 and require split-specific failure attribution before generation",
                "reason": "non-basis families have sparse or zero atlas supply but some near-miss evidence exists",
            },
            {
                "action_id": "R2_family_native_label_policy",
                "target": "all non-basis families",
                "action": "allow family-native label/transform pair contracts rather than one global pass gate",
                "reason": "global primitive atlas pass gate rewards basis/premium and suppresses sparse event-like families",
            },
            {
                "action_id": "R3_interaction_probe_before_formula",
                "target": "OI, positioning, taker_flow, liquidity, volatility",
                "action": "run typed interaction probes only after single-family near-miss repair; no open grammar",
                "reason": "single-field response is insufficient, but direct formula generation would amplify control-like structures",
            },
            {
                "action_id": "R4_stop_core17_until_breadth",
                "target": "CORE17/search",
                "action": "block objective seed policy, replay expansion, and formula search until non-basis breadth gate passes",
                "reason": "149 candidates are not useful if 144 come from one family",
            },
        ]
    )

    blocked = pd.DataFrame(
        [
            {"item": "A7FF-CORE17 objective seed policy", "reason": "blocked: CORE16E atlas breadth failed"},
            {"item": "A7FF formula generation", "reason": "blocked: primitive/operator supply is basis-dominated"},
            {"item": "A7FF bounded replay expansion", "reason": "blocked: no broad objective atlas to replay"},
            {"item": "A7FF large search", "reason": "blocked"},
            {"item": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )

    next_contract = {
        "stage": "A7FF-CORE16F",
        "name": "non-basis field-family supply repair contract",
        "authorized": True,
        "executes_replay": False,
        "executes_search": False,
        "scope": [
            "basis/premium cap policy",
            "non-basis near-miss mining",
            "family-native label/transform pass gates",
            "typed interaction probe contract",
        ],
        "minimum_success_criteria": {
            "non_basis_candidate_count": 32,
            "non_basis_field_family_count": 4,
            "top_family_share_max": 0.50,
            "basis_premium_share_max": 0.50,
        },
        "forbidden": [
            "CORE17 objective seed policy",
            "formula generation",
            "replay expansion",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }

    decision = "PASS_A7FFCORE16ER_EXPANDED_ATLAS_FORENSIC_COMPLETE_READY_FOR_CORE16F"
    manifest = {
        "stage": "A7FF-CORE16ER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16E",
        "source_decision": manifest16e.get("decision"),
        "decision": decision,
        "dominant_failure": "basis_premium_supply_concentration",
        "atlas_candidate_count": int(manifest16e.get("atlas_candidate_count", 0)),
        "field_family_count": int(manifest16e.get("field_family_count", 0)),
        "top_family_share": float(manifest16e.get("top_family_share", 0.0)),
        "authorizes_core16f_contract": True,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16F non-basis field-family supply repair contract",
    }

    family_concentration.to_csv(RUNTIME / "a7ffcore16er_family_concentration.csv", index=False)
    family_supply.to_csv(RUNTIME / "a7ffcore16er_family_supply_forensic.csv", index=False)
    repair_actions.to_csv(RUNTIME / "a7ffcore16er_repair_actions.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore16er_blocked_actions.csv", index=False)
    decisions.to_csv(RUNTIME / "a7ffcore16er_source_decision_counts.csv", index=False)
    write_json(RUNTIME / "a7ffcore16er_next_contract.json", next_contract)
    write_json(RUNTIME / "a7ffcore16er_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE16ER EXPANDED ATLAS FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16ER freezes the CORE16E result. CORE16E deliberately relaxed the lag gate and still produced a basis/premium-dominated atlas, so the blocker is field-family supply concentration, not an over-conservative latency rule.",
        "",
        "This stage does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Concentration",
        "",
        md_table(family_concentration),
        "",
        "## Family Supply Forensic",
        "",
        md_table(family_supply),
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
