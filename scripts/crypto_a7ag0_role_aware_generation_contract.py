from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ag0_role_aware_generation_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AG0_ROLE_AWARE_GENERATION_CONTRACT_20260529.md"

A7AF1_MANIFEST = REPO / "runtime" / "a7af1_role_aware_selector_dryrun" / "a7af1_manifest.json"
A7AF1_QUEUE = REPO / "runtime" / "a7af1_role_aware_selector_dryrun" / "a7af1_selected_queue.csv"


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

    a7af1 = read_json(A7AF1_MANIFEST)
    if not a7af1.get("authorizes_a7ag0_role_aware_generation_contract"):
        raise SystemExit("A7AF-1 does not authorize A7AG-0")
    queue = pd.read_csv(A7AF1_QUEUE)

    generation_tracks = pd.DataFrame(
        [
            {
                "track_id": "G0_ordinary_alpha_basis_premium",
                "source_selector_tier": "T0_raw_relative_alpha",
                "status": "contract_only",
                "primary_fields": "mark_index_basis_bps",
                "allowed_labels": "L0_raw_forward_return|L1_cross_sectional_relative_return|L5_vol_adjusted_return",
                "allowed_transforms": "level|delta_24h|cs_rank|clip|winsor",
                "allowed_interactions": "basis_delta_x_vol_state|basis_delta_x_liquidity_tier|basis_delta_x_market_breadth",
                "forbidden": "funding_only_wrapper|liquidity_volatility_old_family|direct_raw_okx_binance_price_comparison|May_mask",
                "max_static_blueprints": 128,
                "authorizes_execution": False,
            },
            {
                "track_id": "G1_neutralized_alpha_diagnostic",
                "source_selector_tier": "T1_beta_neutral_alpha_diagnostic",
                "status": "contract_only",
                "primary_fields": "trade_return_1h|liquidity_rank_active_universe|premium_close_bps",
                "allowed_labels": "L2_BTC_ETH_beta_residual_return|L3_liquidity_tier_relative_return|L5_vol_adjusted_return",
                "allowed_transforms": "level|delta_24h|cs_rank|ts_zscore_168h",
                "allowed_interactions": "price_reversal_x_liquidity_rank|premium_delta_x_vol_adjusted|liquidity_rank_x_major_beta_residual",
                "forbidden": "ordinary_alpha_promotion_without_L0_L1_translation|May_mask|full_open_grammar",
                "max_static_blueprints": 192,
                "authorizes_execution": False,
            },
            {
                "track_id": "G2_downside_risk_defense",
                "source_selector_tier": "T2_downside_risk_defense",
                "status": "contract_only",
                "primary_fields": "trade_count|realized_vol_24h|open_interest_last|oi_x_price_move_24h|positioning_ratios",
                "allowed_labels": "L6_downside_avoidance",
                "allowed_transforms": "level|delta_24h|cs_rank|ts_zscore_168h",
                "allowed_interactions": "risk_state_x_positioning_delta|vol_state_x_trade_count|oi_price_move_x_downside_state",
                "forbidden": "ordinary_alpha_promotion|rank_label_only_promotion|May_mask|large_search",
                "max_static_blueprints": 256,
                "authorizes_execution": False,
            },
        ]
    )
    track_rules = pd.DataFrame(
        [
            {"rule": "source_queue_only", "detail": "A7AG inputs must come from A7AF1 selected queue"},
            {"rule": "role_label_alignment", "detail": "track labels must match selector tier role"},
            {"rule": "no_cross_track_promotion", "detail": "downside/risk-defense results cannot count as ordinary alpha"},
            {"rule": "control_first", "detail": "matched wrong-lag/stale/random controls must be attached before any numeric replay contract"},
            {"rule": "latency_native", "detail": "same-bar field-native timing policy remains; no artificial +2h stress"},
            {"rule": "no_may", "detail": "May not used in generation, selector score, threshold, mutation, or authorization"},
            {"rule": "no_full_grammar", "detail": "FormulaGenV2 open grammar remains disabled; only typed role-aware blueprints allowed"},
        ]
    )
    blueprint_budget = {
        "a7ag1_static_blueprint_dryrun_authorized": True,
        "a7ag1_executes_numeric_replay": False,
        "a7ag1_executes_formula_search": False,
        "g0_max_static_blueprints": 128,
        "g1_max_static_blueprints": 192,
        "g2_max_static_blueprints": 256,
        "combined_max_static_blueprints": 576,
        "numeric_replay_after_a7ag1": "requires_separate_A7AG2_contract",
    }
    track_summary = (
        queue.groupby("selector_tier", dropna=False)
        .agg(
            selected=("candidate_id", "count"),
            unique_fields=("field_name", "nunique"),
            unique_families=("field_family", "nunique"),
            max_control_ratio=("control_ratio_premay_max", "max"),
            min_robust_tstat_floor=("robust_tstat_floor", "min"),
        )
        .reset_index()
    )
    decision = "PASS_A7AG0_ROLE_AWARE_GENERATION_CONTRACT_READY_FOR_A7AG1_BLUEPRINT_DRYRUN"
    manifest = {
        "stage": "A7AG-0",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7af1_decision": a7af1.get("decision"),
        "executes_contract_only": True,
        "executes_static_blueprint_generation": False,
        "executes_numeric_replay": False,
        "executes_formula_search": False,
        "executes_training": False,
        "authorizes_a7ag1_static_blueprint_dryrun": True,
        "authorizes_numeric_replay": False,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "selected_queue_rows": int(len(queue)),
        "track_count": int(len(generation_tracks)),
        "uses_may": False,
    }
    queue.to_csv(RUNTIME / "a7ag0_source_selected_queue.csv", index=False)
    generation_tracks.to_csv(RUNTIME / "a7ag0_generation_tracks.csv", index=False)
    track_rules.to_csv(RUNTIME / "a7ag0_generation_rules.csv", index=False)
    track_summary.to_csv(RUNTIME / "a7ag0_source_queue_track_summary.csv", index=False)
    write_json(RUNTIME / "a7ag0_blueprint_budget.json", blueprint_budget)
    write_json(RUNTIME / "a7ag0_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ag0_authorization_matrix.json",
        {
            "A7AG-0": {"status": decision},
            "a7ag1_static_blueprint_dryrun": {"authorized": True},
            "numeric_replay": {"authorized": False},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AG-0 ROLE-AWARE GENERATION CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AG-0 defines a role-aware generation contract from the A7AF selector queue. It does not generate formulas, run numeric replay, search, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Generation Tracks",
        "",
        md_table(generation_tracks),
        "",
        "## Source Queue Summary",
        "",
        md_table(track_summary),
        "",
        "## Track Rules",
        "",
        md_table(track_rules),
        "",
        "## Blueprint Budget",
        "",
        "```json",
        json.dumps(blueprint_budget, indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "A7AG-0 only authorizes A7AG-1 static blueprint dryrun.",
        "Numeric replay and formula search execution remain not authorized.",
        "Downside/risk-defense remains separate from ordinary alpha.",
        "May is not used.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
