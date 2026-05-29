from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7af0_role_aware_selector_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AF0_ROLE_AWARE_SELECTOR_CONTRACT_20260529.md"

A7AE2_MANIFEST = REPO / "runtime" / "a7ae2_label_adequacy_role_review" / "a7ae2_manifest.json"
A7AE2_SEEDS = REPO / "runtime" / "a7ae2_label_adequacy_role_review" / "a7ae2_selector_seed_policy.csv"


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
    view = df.head(max_rows).copy().astype(str)
    for col in view.columns:
        view[col] = view[col].str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False, disable_numparse=True)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ae2 = read_json(A7AE2_MANIFEST)
    if not a7ae2.get("authorizes_selector_rewrite_review"):
        raise SystemExit("A7AE-2 does not authorize A7AF-0")

    seeds = pd.read_csv(A7AE2_SEEDS)
    tiers = pd.DataFrame(
        [
            {
                "selector_tier": "T0_raw_relative_alpha",
                "feature_role": "raw_relative_signal_candidate",
                "allowed_labels": "L0_raw_forward_return|L1_cross_sectional_relative_return|L2_BTC_ETH_beta_residual_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return",
                "allowed_next_use": "ordinary_alpha_candidate_contract_only",
                "queue_cap": 6,
                "requires": "raw_or_relative_candidate_count_gt_0|control_ratio_lt_1|lag_ok|premay_all_positive",
            },
            {
                "selector_tier": "T1_beta_neutral_alpha_diagnostic",
                "feature_role": "beta_or_neutralized_signal_candidate",
                "allowed_labels": "L2_BTC_ETH_beta_residual_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return",
                "allowed_next_use": "neutralized_alpha_diagnostic_contract_only",
                "queue_cap": 8,
                "requires": "beta_neutral_candidate_count_gt_0|control_ratio_lt_1|lag_ok|premay_all_positive",
            },
            {
                "selector_tier": "T2_downside_risk_defense",
                "feature_role": "downside_avoidance_signal_candidate",
                "allowed_labels": "L6_downside_avoidance",
                "allowed_next_use": "risk_defense_downside_contract_only",
                "queue_cap": 10,
                "requires": "downside_candidate_count_gt_0|control_ratio_lt_1|lag_ok|premay_all_positive",
            },
        ]
    )
    score_features = pd.DataFrame(
        [
            {"score_feature": "candidate_role_priority", "definition": "T0 > T1 > T2 for ordinary alpha; T2 separated from alpha queue"},
            {"score_feature": "premay_split_consistency", "definition": "validation/test/recent all oriented positive"},
            {"score_feature": "control_margin", "definition": "1 - max wrong-lag/stale/random control ratio"},
            {"score_feature": "one_bar_lag_survival", "definition": "recent one-bar-lag oriented spread survives"},
            {"score_feature": "nonoverlap_robust_tstat", "definition": "minimum oriented pre-May non-overlap tstat"},
            {"score_feature": "field_family_diversity", "definition": "cap per field family inside each tier"},
        ]
    )
    hard_gates = pd.DataFrame(
        [
            {"gate": "seed_field_must_be_in_a7ae2_policy", "rule": "field_name in a7ae2_selector_seed_policy.csv"},
            {"gate": "role_label_match", "rule": "label family must match feature role tier"},
            {"gate": "control_ratio_lt_1", "rule": "control_ratio_premay_max < 1.0"},
            {"gate": "premay_all_positive", "rule": "validation/test/recent all oriented positive"},
            {"gate": "lag_ok", "rule": "one_bar_lag_recent_oriented positive and >= 25pct of recent"},
            {"gate": "no_may", "rule": "May not used in selector score, threshold, mutation, generation, or authorization"},
            {"gate": "downside_not_ordinary_alpha", "rule": "L6 downside queue cannot authorize ordinary alpha search"},
        ]
    )
    role_caps = {
        "max_selected_total": 18,
        "max_per_field": 3,
        "max_per_field_family_per_tier": 4,
        "max_downside_share_in_combined_review": 0.50,
        "min_raw_relative_for_ordinary_alpha_contract": 2,
        "min_beta_neutral_for_neutralized_contract": 3,
        "min_downside_for_risk_defense_contract": 4,
    }

    decision = "PASS_A7AF0_ROLE_AWARE_SELECTOR_CONTRACT_READY_FOR_A7AF1"
    manifest = {
        "stage": "A7AF-0",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ae2_decision": a7ae2.get("decision"),
        "executes_contract_only": True,
        "executes_selector_dryrun": False,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7af1_role_aware_selector_dryrun": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "seed_field_count": int(len(seeds)),
        "selector_tier_count": int(len(tiers)),
        "uses_may": False,
    }
    seeds.to_csv(RUNTIME / "a7af0_allowed_seed_fields.csv", index=False)
    tiers.to_csv(RUNTIME / "a7af0_selector_tiers.csv", index=False)
    score_features.to_csv(RUNTIME / "a7af0_selector_score_features.csv", index=False)
    hard_gates.to_csv(RUNTIME / "a7af0_selector_hard_gates.csv", index=False)
    write_json(RUNTIME / "a7af0_role_caps.json", role_caps)
    write_json(RUNTIME / "a7af0_manifest.json", manifest)
    write_json(
        RUNTIME / "a7af0_authorization_matrix.json",
        {
            "A7AF-0": {"status": decision},
            "a7af1_role_aware_selector_dryrun": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AF-0 ROLE-AWARE SELECTOR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AF-0 rewrites selector policy after A7AE label adequacy review. It separates ordinary alpha, neutralized alpha diagnostics, and downside/risk-defense queues. It does not generate formulas, search, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Selector Tiers",
        "",
        md_table(tiers),
        "",
        "## Score Features",
        "",
        md_table(score_features),
        "",
        "## Hard Gates",
        "",
        md_table(hard_gates),
        "",
        "## Role Caps",
        "",
        "```json",
        json.dumps(role_caps, indent=2, sort_keys=True),
        "```",
        "",
        "## Allowed Seed Fields",
        "",
        md_table(seeds, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AF-0 only authorizes A7AF-1 role-aware selector dryrun.",
        "Formula search remains not authorized.",
        "Downside/risk-defense response must not be treated as ordinary alpha.",
        "May is not used.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
