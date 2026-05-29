from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ah1_ordinary_alpha_objective_rewrite_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AH1_ORDINARY_ALPHA_OBJECTIVE_REWRITE_CONTRACT_20260529.md"

A7AH0_MANIFEST = REPO / "runtime" / "a7ah0_post_a7ag_role_split_decision" / "a7ah0_manifest.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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

    a7ah0 = read_json(A7AH0_MANIFEST)
    if not a7ah0.get("authorizes_a7ah1_ordinary_alpha_objective_rewrite_contract"):
        raise SystemExit("A7AH-0 does not authorize A7AH-1")

    label_policy = {
        "primary_alpha_labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return"],
        "secondary_diagnostic_labels": ["L2_BTC_ETH_beta_residual_return", "L3_liquidity_tier_relative_return"],
        "diagnostic_only_labels": ["L5_vol_adjusted_return"],
        "risk_defense_only_labels": ["L6_downside_avoidance"],
        "forbidden_as_primary_alpha_labels": ["L5_vol_adjusted_return", "L6_downside_avoidance", "L7_ranked_future_return"],
        "ordinary_alpha_candidate_requires": [
            "positive_L0_or_L1_response",
            "control_ratio_lt_1_in_each_pre_may_split",
            "one_bar_lag_survival",
            "cost5_proxy_survival",
            "nonoverlap_median_tstat_floor_gt_0",
            "not_concentration_dominated",
        ],
    }
    selector_policy = {
        "score_components_allowed": [
            "L0_L1_oriented_spread",
            "matched_control_margin",
            "one_bar_lag_survival",
            "cost5_proxy_survival",
            "nonoverlap_robustness",
            "field_family_diversity",
            "skeleton_diversity",
        ],
        "score_components_forbidden": [
            "L5_as_primary_reward",
            "L6_as_primary_reward",
            "May",
            "ranked_label_only_reward",
        ],
        "hard_reject": [
            "no_L0_or_L1_positive_split",
            "control_ratio_ge_1",
            "wrong_lag_or_shuffle_control_stronger",
            "same_skeleton_over_cap",
            "same_field_family_over_cap",
        ],
        "dry_rerank_input": "existing A7AG2/A7AG3 queue and metrics only",
    }
    objective_rows = [
        {
            "objective_id": "O0_basis_premium_ordinary_alpha",
            "allowed_seed_families": "basis_premium",
            "primary_labels": "L0_raw_forward_return|L1_cross_sectional_relative_return",
            "diagnostic_labels": "L2_BTC_ETH_beta_residual_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return",
            "forbidden_primary_labels": "L5_vol_adjusted_return|L6_downside_avoidance|L7_ranked_future_return",
            "status": "allowed_for_dry_rerank_only",
        },
        {
            "objective_id": "O1_positioning_ordinary_alpha",
            "allowed_seed_families": "positioning|open_interest_interaction",
            "primary_labels": "L0_raw_forward_return|L1_cross_sectional_relative_return",
            "diagnostic_labels": "L2_BTC_ETH_beta_residual_return|L3_liquidity_tier_relative_return",
            "forbidden_primary_labels": "L6_downside_avoidance|L7_ranked_future_return",
            "status": "allowed_for_dry_rerank_only",
        },
        {
            "objective_id": "O2_vol_adjusted_to_ordinary_translation",
            "allowed_seed_families": "basis_premium|volatility",
            "primary_labels": "L0_raw_forward_return|L1_cross_sectional_relative_return",
            "diagnostic_labels": "L5_vol_adjusted_return",
            "forbidden_primary_labels": "L5_vol_adjusted_return",
            "status": "translation_diagnostic_only",
        },
    ]
    objective_df = pd.DataFrame(objective_rows)

    decision = "PASS_A7AH1_ORDINARY_ALPHA_OBJECTIVE_REWRITE_CONTRACT_READY_FOR_DRY_RERANK"
    manifest = {
        "stage": "A7AH-1",
        "generated_at": now_utc(),
        "decision": decision,
        "input_a7ah0_decision": a7ah0.get("decision"),
        "executes_contract_only": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7ah1d_dry_rerank": True,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
    }

    objective_df.to_csv(RUNTIME / "a7ah1_allowed_objective_families.csv", index=False)
    write_json(RUNTIME / "a7ah1_label_policy.json", label_policy)
    write_json(RUNTIME / "a7ah1_selector_policy.json", selector_policy)
    write_json(RUNTIME / "a7ah1_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ah1_authorization_matrix.json",
        {
            "A7AH-1": {"status": decision},
            "a7ah1d_dry_rerank": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AH-1 ORDINARY ALPHA OBJECTIVE REWRITE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AH-1 rewrites the ordinary-alpha selector target after A7AG5 found no L0/L1 translation. It is contract-only and does not execute search or replay.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Policy",
        "",
        "```json",
        json.dumps(label_policy, indent=2, sort_keys=True),
        "```",
        "",
        "## Selector Policy",
        "",
        "```json",
        json.dumps(selector_policy, indent=2, sort_keys=True),
        "```",
        "",
        "## Objective Families",
        "",
        md_table(objective_df),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AH-1 restores ordinary alpha discipline: L0/L1 must be primary.",
        "Vol-adjusted/downside/ranked labels can diagnose but cannot carry ordinary alpha promotion.",
        "No formula search, large search, alpha proof, shadow, paper, or live is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
