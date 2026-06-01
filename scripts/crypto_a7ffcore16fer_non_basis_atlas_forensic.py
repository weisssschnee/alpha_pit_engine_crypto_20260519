from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16fer_non_basis_atlas_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16FER_NON_BASIS_ATLAS_FORENSIC_20260601.md"
CORE16FE = REPO / "runtime" / "a7ffcore16fe_non_basis_atlas_execution" / "a7ffcore16fe_manifest.json"
FAMILY_SUMMARY = REPO / "runtime" / "a7ffcore16fe_non_basis_atlas_execution" / "a7ffcore16fe_family_supply_summary.csv"
NEAR_MISS = REPO / "runtime" / "a7ffcore16fe_non_basis_atlas_execution" / "a7ffcore16fe_non_basis_near_miss_forensic_lane.csv"
STRICT = REPO / "runtime" / "a7ffcore16fe_non_basis_atlas_execution" / "a7ffcore16fe_strict_non_basis_atlas_candidates.csv"


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

    core16fe = read_json(CORE16FE)
    if core16fe.get("decision") != "HOLD_A7FFCORE16FE_NON_BASIS_ATLAS_SUPPLY_INSUFFICIENT":
        raise SystemExit(f"CORE16FE is not in forensic state: {core16fe.get('decision')}")

    family = load_csv(FAMILY_SUMMARY)
    near = load_csv(NEAR_MISS)
    strict = load_csv(STRICT)

    if near.empty:
        near_family = pd.DataFrame()
    else:
        near_family = (
            near.groupby(["field_family", "transform", "label_family"], dropna=False)
            .agg(
                near_miss_count=("field_name", "size"),
                median_control_ratio=("control_ratio_premay_max", "median"),
                median_positive_splits=("premay_positive_split_count", "median"),
            )
            .reset_index()
            .sort_values("near_miss_count", ascending=False)
        )

    family_actions = pd.DataFrame(
        [
            {
                "family": "open_interest",
                "status": "near_miss_repairable",
                "next_action": "convert OI level/delta near-miss rows into OI x price/funding/basis interaction probes",
                "hard_limit": "no standalone OI alpha promotion without control_ratio < 1.0",
            },
            {
                "family": "positioning",
                "status": "thin_strict_supply",
                "next_action": "use account-vs-position divergence and top-vs-global divergence as typed interaction probes",
                "hard_limit": "positioning cannot be a risk-defense wrapper selected as ordinary alpha",
            },
            {
                "family": "taker_flow",
                "status": "zero_strict_supply",
                "next_action": "only test taker x OI and taker x liquidity reversal probes; no standalone flow search",
                "hard_limit": "requires non-L7 response and control-clean evidence",
            },
            {
                "family": "liquidity",
                "status": "zero_strict_supply",
                "next_action": "treat as state/neutralizer unless interaction probe beats controls",
                "hard_limit": "no liquidity-volatility old-family revival",
            },
            {
                "family": "volatility",
                "status": "zero_strict_supply",
                "next_action": "use volatility as conditioning state for basis/OI/positioning only",
                "hard_limit": "no pure volatility beta signal",
            },
            {
                "family": "price_return",
                "status": "thin_but_control_risky",
                "next_action": "use only as interaction leg and baseline control",
                "hard_limit": "no direct price-return objective expansion",
            },
        ]
    )

    next_contract = {
        "stage": "A7FF-CORE16G",
        "name": "family-native interaction repair contract",
        "authorized": True,
        "executes_replay": False,
        "executes_search": False,
        "inputs": [
            "CORE16FE strict non-basis atlas candidates",
            "CORE16FE near-miss forensic lane",
            "CORE16F family policy",
            "field role ledger",
        ],
        "allowed_interaction_families": [
            "OI_delta_x_price_move",
            "OI_delta_x_funding_abs",
            "OI_delta_x_basis_premium_dislocation",
            "positioning_divergence_x_price_or_basis",
            "taker_flow_x_OI_or_liquidity",
            "liquidity_state_x_basis_or_positioning",
            "volatility_state_x_basis_or_OI",
        ],
        "pass_gate": {
            "interaction_probe_candidates": 64,
            "non_basis_family_count": 4,
            "top_family_share_max": 0.40,
            "control_ratio_required": "< 1.0 for promotion, 1.0-1.5 forensic only",
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
            {"item": "A7FF-CORE17 objective seed policy", "reason": "blocked until CORE16G/next interaction repair passes"},
            {"item": "formula generation", "reason": "blocked: non-basis single-field supply insufficient"},
            {"item": "bounded replay", "reason": "blocked: no broad objective atlas"},
            {"item": "large search", "reason": "blocked"},
            {"item": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )

    decision = "PASS_A7FFCORE16FER_NON_BASIS_FORENSIC_COMPLETE_READY_FOR_CORE16G"
    manifest = {
        "stage": "A7FF-CORE16FER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16FE",
        "source_decision": core16fe.get("decision"),
        "decision": decision,
        "dominant_failure": "non_basis_single_field_supply_insufficient",
        "strict_non_basis_candidate_count": int(core16fe.get("strict_non_basis_candidate_count", 0)),
        "near_miss_non_basis_count": int(core16fe.get("near_miss_non_basis_count", 0)),
        "strict_non_basis_field_family_count": int(core16fe.get("strict_non_basis_field_family_count", 0)),
        "authorizes_core16g_contract": True,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16G family-native interaction repair contract",
    }

    family.to_csv(RUNTIME / "a7ffcore16fer_source_family_supply_summary.csv", index=False)
    strict.to_csv(RUNTIME / "a7ffcore16fer_source_strict_candidates.csv", index=False)
    near.to_csv(RUNTIME / "a7ffcore16fer_source_near_miss_lane.csv", index=False)
    near_family.to_csv(RUNTIME / "a7ffcore16fer_near_miss_by_family_transform_label.csv", index=False)
    family_actions.to_csv(RUNTIME / "a7ffcore16fer_family_repair_actions.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore16fer_blocked_actions.csv", index=False)
    write_json(RUNTIME / "a7ffcore16fer_next_contract.json", next_contract)
    write_json(RUNTIME / "a7ffcore16fer_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE16FER NON-BASIS ATLAS FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16FER freezes the CORE16FE result. Non-basis strict supply is too thin for CORE17 or replay expansion, but the 46-row near-miss lane is enough to justify a family-native interaction repair contract. This is not formula generation or search authorization.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Supply",
        "",
        md_table(family),
        "",
        "## Near-Miss By Family / Transform / Label",
        "",
        md_table(near_family),
        "",
        "## Family Repair Actions",
        "",
        md_table(family_actions),
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
