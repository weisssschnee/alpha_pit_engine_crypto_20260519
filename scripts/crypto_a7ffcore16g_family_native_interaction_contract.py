from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16g_family_native_interaction_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16G_FAMILY_NATIVE_INTERACTION_CONTRACT_20260601.md"
CORE16FER = REPO / "runtime" / "a7ffcore16fer_non_basis_atlas_forensic" / "a7ffcore16fer_manifest.json"
NEAR_MISS = REPO / "runtime" / "a7ffcore16fer_non_basis_atlas_forensic" / "a7ffcore16fer_source_near_miss_lane.csv"


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

    core16fer = read_json(CORE16FER)
    if core16fer.get("decision") != "PASS_A7FFCORE16FER_NON_BASIS_FORENSIC_COMPLETE_READY_FOR_CORE16G":
        raise SystemExit(f"CORE16FER is not ready for CORE16G: {core16fer.get('decision')}")

    near = pd.read_csv(NEAR_MISS) if NEAR_MISS.exists() else pd.DataFrame()
    near_summary = (
        near.groupby("field_family", dropna=False)
        .agg(
            near_miss_count=("field_name", "size"),
            transform_count=("transform", "nunique"),
            label_family_count=("label_family", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values("near_miss_count", ascending=False)
        if not near.empty
        else pd.DataFrame()
    )

    interaction_families = pd.DataFrame(
        [
            {
                "interaction_family": "I0_OI_delta_x_price_move",
                "left_family": "open_interest",
                "right_family": "price_return",
                "allowed_transforms": "delta_4h;delta_24h;zscore_168h;spread_short_long",
                "role": "ordinary_alpha_probe",
                "rationale": "OI single-field rows have near misses but need price-move context to avoid slow leverage-state ambiguity",
            },
            {
                "interaction_family": "I1_OI_delta_x_funding_abs",
                "left_family": "open_interest",
                "right_family": "funding",
                "allowed_transforms": "delta_4h;delta_24h;zscore_168h",
                "role": "ordinary_alpha_probe",
                "rationale": "leverage expansion should be interpreted under crowding/funding state",
            },
            {
                "interaction_family": "I2_OI_delta_x_basis_premium_dislocation",
                "left_family": "open_interest",
                "right_family": "basis_premium",
                "allowed_transforms": "delta_4h;zscore_72h;zscore_168h;shock_24h",
                "role": "ordinary_alpha_probe_with_basis_cap",
                "rationale": "use basis/premium as context leg, not dominant standalone source",
            },
            {
                "interaction_family": "I3_positioning_divergence_x_price_or_basis",
                "left_family": "positioning",
                "right_family": "price_return;basis_premium",
                "allowed_transforms": "spread_short_long;delta_24h;zscore_168h",
                "role": "ordinary_alpha_probe",
                "rationale": "positioning strict supply is thin but divergence may only matter under price/basis context",
            },
            {
                "interaction_family": "I4_taker_flow_x_OI_or_liquidity",
                "left_family": "taker_flow",
                "right_family": "open_interest;liquidity",
                "allowed_transforms": "delta_1h;delta_4h;shock_24h;tsrank_72h",
                "role": "diagnostic_to_alpha_probe",
                "rationale": "flow alone has zero strict supply; test only with leverage or liquidity state",
            },
            {
                "interaction_family": "I5_liquidity_state_x_basis_or_positioning",
                "left_family": "liquidity",
                "right_family": "basis_premium;positioning",
                "allowed_transforms": "zscore_168h;tsrank_168h;shock_24h",
                "role": "state_conditioned_probe",
                "rationale": "liquidity is likely a state/neutralizer unless interaction beats controls",
            },
            {
                "interaction_family": "I6_volatility_state_x_basis_or_OI",
                "left_family": "volatility",
                "right_family": "basis_premium;open_interest",
                "allowed_transforms": "zscore_72h;zscore_168h;spread_short_long",
                "role": "state_conditioned_probe",
                "rationale": "volatility should condition dislocation/leverage signals, not become pure volatility beta",
            },
        ]
    )

    operator_policy = pd.DataFrame(
        [
            {"operator": "Mul", "allowed": True, "constraint": "only typed left/right families in interaction_families"},
            {"operator": "SafeDiv", "allowed": True, "constraint": "denominator must be positive-stable; winsorize extreme denominators"},
            {"operator": "Sub", "allowed": True, "constraint": "only for divergence/spread semantics"},
            {"operator": "Add", "allowed": True, "constraint": "only after same semantic scale normalization"},
            {"operator": "ZScore", "allowed": True, "constraint": "lookback 72h/168h only"},
            {"operator": "TSRank", "allowed": True, "constraint": "lookback 72h/168h only"},
            {"operator": "Clip", "allowed": True, "constraint": "predefined quantile clip; no tuned thresholds"},
            {"operator": "IfElse", "allowed": False, "constraint": "blocked: no deep conditionals or threshold masks"},
            {"operator": "SignedPower", "allowed": False, "constraint": "blocked: unbounded nonlinear transform"},
        ]
    )

    execution_contract = {
        "stage": "A7FF-CORE16GE",
        "name": "family-native interaction probe execution",
        "authorized": True,
        "executes_replay": False,
        "executes_search": False,
        "max_blueprints": 2048,
        "target_interaction_families": interaction_families["interaction_family"].tolist(),
        "labels": [
            "L0_raw_forward_return",
            "L1_cross_sectional_relative_return",
            "L3_liquidity_tier_relative_return",
            "L5_vol_adjusted_return",
        ],
        "horizons": [1, 4, 8, 24],
        "promotion_gate": {
            "interaction_probe_candidates": 64,
            "non_basis_family_count": 4,
            "top_family_share_max": 0.40,
            "control_ratio_for_promotion": "< 1.0",
            "near_miss_lane": "1.0 <= control_ratio < 1.5 forensic-only",
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
            {"item": "A7FF-CORE17 objective seed policy", "reason": "blocked until CORE16GE interaction probe passes"},
            {"item": "formula generation", "reason": "blocked: CORE16G authorizes typed interaction probes only"},
            {"item": "bounded replay", "reason": "blocked: no broad objective atlas"},
            {"item": "large search", "reason": "blocked"},
            {"item": "alpha proof / shadow / paper / live", "reason": "not authorized"},
        ]
    )

    decision = "PASS_A7FFCORE16G_FAMILY_NATIVE_INTERACTION_CONTRACT_READY_FOR_CORE16GE"
    manifest = {
        "stage": "A7FF-CORE16G",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16FER",
        "source_decision": core16fer.get("decision"),
        "decision": decision,
        "near_miss_non_basis_count": int(core16fer.get("near_miss_non_basis_count", 0)),
        "interaction_family_count": int(interaction_families.shape[0]),
        "authorizes_core16ge": True,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16GE family-native interaction probe execution",
    }

    near_summary.to_csv(RUNTIME / "a7ffcore16g_source_near_miss_summary.csv", index=False)
    interaction_families.to_csv(RUNTIME / "a7ffcore16g_interaction_family_contract.csv", index=False)
    operator_policy.to_csv(RUNTIME / "a7ffcore16g_operator_policy.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore16g_blocked_actions.csv", index=False)
    write_json(RUNTIME / "a7ffcore16g_execution_contract.json", execution_contract)
    write_json(RUNTIME / "a7ffcore16g_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE16G FAMILY-NATIVE INTERACTION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16G defines a typed, family-native interaction probe contract after CORE16FE showed non-basis single-field supply is insufficient. It does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Near-Miss Summary",
        "",
        md_table(near_summary),
        "",
        "## Interaction Families",
        "",
        md_table(interaction_families),
        "",
        "## Operator Policy",
        "",
        md_table(operator_policy),
        "",
        "## Execution Contract",
        "",
        "```json",
        json.dumps(execution_contract, indent=2, sort_keys=True),
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
