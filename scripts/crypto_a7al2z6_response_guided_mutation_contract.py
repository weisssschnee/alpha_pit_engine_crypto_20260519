from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al2z6_response_guided_mutation_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z6_RESPONSE_GUIDED_MUTATION_CONTRACT_20260529.md"
Z5_MANIFEST = REPO / "runtime" / "a7al2z5_broader_non_oi_multi_horizon_diagnostic" / "a7al2z5_manifest.json"
Z5_FAMILY = REPO / "runtime" / "a7al2z5_broader_non_oi_multi_horizon_diagnostic" / "a7al2z5_family_horizon_summary.csv"
Z5_COUNTS = REPO / "runtime" / "a7al2z5_broader_non_oi_multi_horizon_diagnostic" / "a7al2z5_decision_counts_by_horizon.csv"


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

    z5 = read_json(Z5_MANIFEST)
    if not z5 or z5.get("eval_error_count", 1) != 0:
        raise SystemExit("A7AL-2Z5 must complete with zero eval errors before Z6")
    family = pd.read_csv(Z5_FAMILY)
    counts = pd.read_csv(Z5_COUNTS)

    mutation_rows = []
    for row in family.to_dict("records"):
        candidates = max(1, int(row["candidate_count"]))
        pre_may_rate = float(row["pre_may_positive_count"]) / candidates
        lag_ok_rate = float(row["lag_ok_count"]) / candidates
        control_ratio = float(row["median_control_ratio"]) if pd.notna(row["median_control_ratio"]) else 999.0
        directives: list[str] = []
        if pre_may_rate < 0.20:
            directives.append("drop_or_downweight_mean_rank_templates")
            directives.append("require_two_source_interaction")
        if control_ratio >= 1.0:
            directives.append("require_matched_control_resistant_double_difference")
            directives.append("forbid_single_source_wrapper")
        if lag_ok_rate < 0.50:
            directives.append("add_smoothing_and_slow_delta")
            directives.append("prefer_group_neutralized_low_turnover_form")
        if not directives:
            directives.append("keep_family_with_diversity_cap")
        mutation_rows.append(
            {
                "source_objective_family": row["objective_family"],
                "label_horizon_h": row["label_horizon_h"],
                "pre_may_positive_rate": pre_may_rate,
                "lag_ok_rate": lag_ok_rate,
                "median_control_ratio": control_ratio,
                "mutation_directives": "|".join(sorted(set(directives))),
                "eligible_for_z7_seed": bool(pre_may_rate >= 0.125 or lag_ok_rate >= 0.40),
            }
        )
    directives = pd.DataFrame(mutation_rows)
    allowed = pd.DataFrame(
        [
            {
                "family_id": "M0_basis_funding_double_difference",
                "description": "Basis/premium and funding dislocation with group-neutral double differences.",
                "minimum_generated": 160,
                "minimum_selected": 16,
            },
            {
                "family_id": "M1_price_range_smoothed_reversal",
                "description": "Smoothed range/price reversal with volatility and trend-state neutralization.",
                "minimum_generated": 160,
                "minimum_selected": 16,
            },
            {
                "family_id": "M2_taker_liquidity_control_resistant",
                "description": "Taker/liquidity pressure after liquidity-tier and stale-control resistant transforms.",
                "minimum_generated": 160,
                "minimum_selected": 16,
            },
            {
                "family_id": "M3_latent_meme_major_neutral",
                "description": "Latent, meme, major and multiplier neutral structures using non-OI fields.",
                "minimum_generated": 160,
                "minimum_selected": 16,
            },
            {
                "family_id": "M4_regime_relative_value",
                "description": "Regime-neutral relative value between basis/funding/price/taker fields.",
                "minimum_generated": 160,
                "minimum_selected": 16,
            },
            {
                "family_id": "M5_trend_breadth_interaction",
                "description": "Market trend/breadth state interactions with price and premium reversals.",
                "minimum_generated": 160,
                "minimum_selected": 16,
            },
            {
                "family_id": "M6_low_turnover_funding_premium",
                "description": "Lower-turnover funding/premium persistence and compression forms.",
                "minimum_generated": 160,
                "minimum_selected": 16,
            },
            {
                "family_id": "M7_multi_neutral_cross_family",
                "description": "Cross-family expressions requiring both state neutralization and source diversity.",
                "minimum_generated": 160,
                "minimum_selected": 16,
            },
        ]
    )
    forbidden = pd.DataFrame(
        [
            {"forbidden": "single_source_rank_or_delta_wrapper"},
            {"forbidden": "OI_or_positioning_core_fields"},
            {"forbidden": "A7V_activity_liquidity_self_reproduction"},
            {"forbidden": "liquidity_x_volatility_rc000_style"},
            {"forbidden": "May_in_selector_generation_mutation"},
            {"forbidden": "full_open_grammar"},
        ]
    )
    decision = "PASS_A7AL2Z6_RESPONSE_GUIDED_MUTATION_CONTRACT_READY_FOR_Z7"
    manifest = {
        "stage": "A7AL-2Z6",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_generation": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7al2z7_response_guided_generation": True,
        "authorizes_full_replay": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "source_z5_decision": z5.get("decision"),
        "source_z5_stress_clean_count": z5.get("stress_clean_clue_count"),
        "source_z5_blockers": z5.get("blockers"),
        "uses_may_for_mutation": False,
    }

    directives.to_csv(RUNTIME / "a7al2z6_failure_guided_mutation_directives.csv", index=False)
    allowed.to_csv(RUNTIME / "a7al2z6_allowed_mutation_families.csv", index=False)
    forbidden.to_csv(RUNTIME / "a7al2z6_forbidden_patterns.csv", index=False)
    counts.to_csv(RUNTIME / "a7al2z6_source_decision_counts_by_horizon.csv", index=False)
    write_json(RUNTIME / "a7al2z6_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z6_authorization_matrix.json",
        {
            "A7AL-2Z6": {"status": decision},
            "a7al2z7_response_guided_generation": {"authorized": True},
            "full_replay": {"authorized": False},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AL-2Z6 RESPONSE-GUIDED MUTATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "Z6 converts the Z5 non-May failure map into mutation directives. It does not run generation, replay, training, or proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Mutation Directives",
        "",
        md_table(directives, 120),
        "",
        "## Allowed Families",
        "",
        md_table(allowed),
        "",
        "## Forbidden Patterns",
        "",
        md_table(forbidden),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
