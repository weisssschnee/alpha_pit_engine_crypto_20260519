from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore28e_independent_data_family_atlas_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE28E_INDEPENDENT_DATA_FAMILY_ATLAS_AUDIT_20260602.md"

CORE28 = REPO / "runtime" / "a7ffcore28_objective_data_family_reset_contract" / "a7ffcore28_manifest.json"
A7U0R = REPO / "runtime" / "a7u0r_source_trace_audit" / "a7u0r_manifest.json"
A7S1_ACCEPT = REPO / "runtime" / "a7s1_metrics_acceptance_audit" / "a7s1_acceptance_manifest.json"
A7AP1 = REPO / "runtime" / "a7ap1_cross_exchange_field_smoke" / "a7ap1_manifest.json"
A7AIF3_FIELDS = REPO / "runtime" / "a7aif3_materialization_evaluator_parity" / "a7aif3_field_materialization_matrix.csv"
A7AIF4_PROMOTED = REPO / "runtime" / "a7aif4_response_backed_field_promotion" / "a7aif4_promoted_ordinary_alpha_fields.csv"
CORE26DER = REPO / "runtime" / "a7ffcore26der_non_s0_repair_forensic" / "a7ffcore26der_manifest.json"
CORE27X = REPO / "runtime" / "a7ffcore27x_search_readiness_arbitration" / "a7ffcore27x_manifest.json"

DATA_ROOT = Path("G:/AlphaFactory_CryptoData")
DATA_PATHS = {
    "top498_replay_v2": DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527",
    "core12_aggtrades_all_features": DATA_ROOT
    / "gold"
    / "features"
    / "binance_core12_all_features_metrics_market_structure_aggtrades_v1_20260524.parquet",
    "cross_exchange_30d_v2": DATA_ROOT
    / "gold"
    / "features"
    / "okx_binance_cross_exchange_unified_1h_30d_v2_20260527",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def field_status(fields: pd.DataFrame, names: list[str]) -> tuple[str, str]:
    if fields.empty:
        return "unknown", "A7AI-F3 field matrix missing"
    present = fields[fields["field_name"].isin(names)]
    if present.empty:
        return "not_in_a7aif3_matrix", "no requested fields in materialization matrix"
    unresolved = present[present["resolution"].astype(str) != "resolved"]
    ordinary = int(present.get("ordinary_alpha_allowed", pd.Series(dtype=bool)).astype(str).eq("True").sum())
    diagnostic = int(present.get("diagnostic_allowed", pd.Series(dtype=bool)).astype(str).eq("True").sum())
    risk = int(present.get("risk_defense_allowed", pd.Series(dtype=bool)).astype(str).eq("True").sum())
    if not unresolved.empty:
        return "partial_or_unresolved", f"{len(unresolved)} unresolved field rows"
    return "resolved", f"resolved={len(present)} ordinary={ordinary} diagnostic={diagnostic} risk_defense={risk}"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    core28 = read_json(CORE28)
    if core28.get("decision") != "PASS_A7FFCORE28_OBJECTIVE_DATA_FAMILY_RESET_CONTRACT_READY_FOR_CORE28E":
        raise SystemExit(f"CORE28 is not ready for CORE28E: {core28.get('decision')}")

    a7u0r = read_json(A7U0R)
    a7s1 = read_json(A7S1_ACCEPT)
    a7ap1 = read_json(A7AP1)
    core26der = read_json(CORE26DER)
    core27x = read_json(CORE27X)
    fields = read_csv(A7AIF3_FIELDS)
    promoted = read_csv(A7AIF4_PROMOTED)

    source_inventory = pd.DataFrame(
        [
            {
                "artifact_id": key,
                "path": str(path),
                "exists": path.exists(),
                "artifact_type": "directory" if path.exists() and path.is_dir() else ("file" if path.exists() else "missing"),
            }
            for key, path in DATA_PATHS.items()
        ]
        + [
            {"artifact_id": "A7U0R_source_trace", "path": str(A7U0R), "exists": A7U0R.exists(), "artifact_type": "manifest"},
            {
                "artifact_id": "A7S1_metrics_acceptance",
                "path": str(A7S1_ACCEPT),
                "exists": A7S1_ACCEPT.exists(),
                "artifact_type": "manifest",
            },
            {"artifact_id": "A7AP1_cross_exchange", "path": str(A7AP1), "exists": A7AP1.exists(), "artifact_type": "manifest"},
            {"artifact_id": "A7AI-F3_fields", "path": str(A7AIF3_FIELDS), "exists": A7AIF3_FIELDS.exists(), "artifact_type": "csv"},
            {
                "artifact_id": "A7AI-F4_promoted_fields",
                "path": str(A7AIF4_PROMOTED),
                "exists": A7AIF4_PROMOTED.exists(),
                "artifact_type": "csv",
            },
        ]
    )

    family_specs = [
        {
            "family_id": "F0_positioning_price_basis_s0",
            "data_family": "positioning_price_basis_s0",
            "source_decision": core27x.get("decision", ""),
            "source_trace_status": "covered_by_CORE26_CORE27_failure_chain",
            "historical_availability": "available_but_failed_as_single_lane",
            "universe_scope": "top498 probe subset / S0 clean only",
            "pit_status": "usable_existing_panel",
            "field_names": ["open_interest_value_last", "index_close", "mark_index_basis_bps"],
            "independence_from_s0": "reference",
            "blocked_pattern_risk": "high",
            "recommended_role": "diagnostic_reference_only",
            "ready_for_core29": False,
            "notes": "4 S0 clean candidates are calibration/anti-overfit reference only; standalone rerun blocked.",
        },
        {
            "family_id": "F1a_aggtrades_flow_microstructure",
            "data_family": "aggTrades_flow_microstructure",
            "source_decision": a7u0r.get("decision", ""),
            "source_trace_status": "PASS" if a7u0r.get("decision") == "PASS_A7U0R_SOURCE_TRACE_COMPLETE" else "unknown",
            "historical_availability": "core12_2024_2026Apr",
            "universe_scope": "core12/core3 richer microstructure, not full top498",
            "pit_status": "hourly_bucket_available_after_hour_end",
            "field_names": [
                "signed_aggressor_notional",
                "signed_aggressor_quantity",
                "volume_imbalance",
                "max_trade_notional",
            ],
            "independence_from_s0": "high",
            "blocked_pattern_risk": "medium_A7V_self_reproduction_caution",
            "recommended_role": "bounded_core12_candidate_and_state_interaction",
            "ready_for_core29": True,
            "notes": "Use flow/large-trade/imbalance as independent state; block A7V activity/liquidity self-reproduction.",
        },
        {
            "family_id": "F1b_taker_flow_market_panel",
            "data_family": "taker_flow_market_panel",
            "source_decision": "available_in_top498_replay_v2",
            "source_trace_status": "panel_artifact_exists" if DATA_PATHS["top498_replay_v2"].exists() else "missing_panel_artifact",
            "historical_availability": "top498_2024_2026Apr",
            "universe_scope": "top498 listing-aware",
            "pit_status": "1h panel feature; use after bar close",
            "field_names": ["kline_taker_buy_quote_share", "kline_quote_volume", "kline_volume", "trade_count"],
            "independence_from_s0": "high",
            "blocked_pattern_risk": "medium_liquidity_activity_false_positive",
            "recommended_role": "ordinary_alpha_candidate_if_interaction_and_control_clean",
            "ready_for_core29": True,
            "notes": "Top498 coverage makes this the main independent flow candidate, but not standalone activity/liquidity.",
        },
        {
            "family_id": "F2a_basis_funding_independent",
            "data_family": "basis_funding_dislocation",
            "source_decision": a7s1.get("decision", ""),
            "source_trace_status": "PASS_WITH_WARNINGS",
            "historical_availability": "top498_2024_2026Apr",
            "universe_scope": "top498 listing-aware",
            "pit_status": "usable_existing_panel; funding/metrics use conservative availability policy",
            "field_names": ["mark_index_basis_bps", "premium_close_bps", "funding_rate", "funding_rate_abs_168h"],
            "independence_from_s0": "medium",
            "blocked_pattern_risk": "medium_basis_only_or_funding_only_wrapper",
            "recommended_role": "bounded_independent_interaction_candidate",
            "ready_for_core29": True,
            "notes": "Must be non-S0-neutralized and interaction/state-conditioned; prior promoted seed is basis_delta only.",
        },
        {
            "family_id": "F2b_positioning_ratios_diagnostic",
            "data_family": "positioning_ratios",
            "source_decision": a7s1.get("decision", ""),
            "source_trace_status": "PASS_WITH_VENDOR_5M_WARNINGS",
            "historical_availability": "top498 metrics history plus warnings",
            "universe_scope": "top498 listing-aware",
            "pit_status": "feature_available_after_hour_end; vendor 5m warnings",
            "field_names": [
                "global_long_short_account_ratio_last",
                "top_long_short_account_ratio_last",
                "top_long_short_position_ratio_last",
                "taker_buy_sell_volume_ratio_last",
            ],
            "independence_from_s0": "medium",
            "blocked_pattern_risk": "high_as_standalone_signal",
            "recommended_role": "risk_exposure_or_interaction_input",
            "ready_for_core29": False,
            "notes": "A7AI-F3/F4 treat most positioning as risk/control-like; require interaction-only contract before search.",
        },
        {
            "family_id": "F3_liquidity_volume_state",
            "data_family": "liquidity_volume_state",
            "source_decision": "available_in_top498_replay_v2",
            "source_trace_status": "panel_artifact_exists" if DATA_PATHS["top498_replay_v2"].exists() else "missing_panel_artifact",
            "historical_availability": "top498_2024_2026Apr",
            "universe_scope": "top498 listing-aware",
            "pit_status": "1h panel feature; use after bar close",
            "field_names": ["kline_quote_volume", "kline_volume", "liquidity_rank_active_universe", "realized_vol_168h"],
            "independence_from_s0": "high",
            "blocked_pattern_risk": "high_A7V_activity_liquidity_caution",
            "recommended_role": "regime_state_or_interaction_input",
            "ready_for_core29": False,
            "notes": "Useful as state/neutralizer; standalone activity/liquidity alpha family remains blocked.",
        },
        {
            "family_id": "F4_cross_exchange_forward_context",
            "data_family": "cross_exchange_basis_funding_depth",
            "source_decision": a7ap1.get("decision", ""),
            "source_trace_status": "diagnostic_recent_forward_context",
            "historical_availability": "30d/recent overlap only",
            "universe_scope": f"{a7ap1.get('symbols', 'unknown')} symbols / {a7ap1.get('unique_hours', 'unknown')} hours",
            "pit_status": "diagnostic_or_forward_only",
            "field_names": ["funding_spread", "basis_spread", "spread_bps", "depth_imbalance_20"],
            "independence_from_s0": "high",
            "blocked_pattern_risk": "high_if_backfilled_as_history",
            "recommended_role": "forward_context_diagnostic_only",
            "ready_for_core29": False,
            "notes": "Can design telemetry; cannot enter historical alpha proof or backfilled replay.",
        },
        {
            "family_id": "F5_new_liquidation_orderbook_contract",
            "data_family": "liquidation_orderbook_depth",
            "source_decision": "contract_required",
            "source_trace_status": "not_historical_source_trace_complete",
            "historical_availability": "not_ready",
            "universe_scope": "unknown_or_forward_only",
            "pit_status": "contract_required",
            "field_names": ["liquidation_imbalance", "large_liquidation_notional", "depth_imbalance_20", "spread_bps"],
            "independence_from_s0": "high",
            "blocked_pattern_risk": "high_without_PIT_contract",
            "recommended_role": "new_data_contract_only",
            "ready_for_core29": False,
            "notes": "High-value candidate family, but must not be used as historical proof without source/PIT contract.",
        },
    ]

    atlas = pd.DataFrame(family_specs)
    materialization_rows: list[dict[str, Any]] = []
    for row in family_specs:
        status, detail = field_status(fields, row["field_names"])
        materialization_rows.append(
            {
                "family_id": row["family_id"],
                "field_materialization_status": status,
                "field_materialization_detail": detail,
            }
        )
    materialization = pd.DataFrame(materialization_rows)
    atlas = atlas.merge(materialization, on="family_id", how="left")

    # Scoring is intentionally coarse: this is a contract/audit, not a selector.
    score_rows = []
    for row in atlas.to_dict("records"):
        score = 0
        if row["source_trace_status"].startswith("PASS") or "exists" in row["source_trace_status"]:
            score += 2
        if "top498" in row["universe_scope"]:
            score += 2
        elif "core12" in row["universe_scope"]:
            score += 1
        if row["pit_status"] not in {"contract_required", "diagnostic_or_forward_only"}:
            score += 1
        if row["independence_from_s0"] == "high":
            score += 2
        elif row["independence_from_s0"] == "medium":
            score += 1
        if row["field_materialization_status"] == "resolved":
            score += 1
        if row["blocked_pattern_risk"].startswith("high"):
            score -= 1
        elif row["blocked_pattern_risk"].startswith("medium"):
            score -= 0.5
        score_rows.append(
            {
                "family_id": row["family_id"],
                "independence_score": score,
                "ready_for_core29": bool(row["ready_for_core29"]),
                "core29_recommendation": (
                    "candidate_for_bounded_contract" if row["ready_for_core29"] else "blocked_or_diagnostic_only"
                ),
            }
        )
    scorecard = pd.DataFrame(score_rows).sort_values(["ready_for_core29", "independence_score"], ascending=[False, False])
    next_candidates = atlas[atlas["ready_for_core29"]].copy()
    blocked = atlas[~atlas["ready_for_core29"]].copy()

    ready_count = int(next_candidates.shape[0])
    independent_ready_count = int(
        next_candidates[next_candidates["independence_from_s0"].isin(["high", "medium"])].shape[0]
    )
    promoted_family_count = int(promoted["field_family"].nunique()) if not promoted.empty and "field_family" in promoted else 0
    decision = (
        "PASS_A7FFCORE28E_INDEPENDENT_DATA_FAMILY_ATLAS_READY_FOR_CORE29_CONTRACT"
        if independent_ready_count >= 2
        else "HOLD_A7FFCORE28E_INDEPENDENT_FAMILY_SUPPLY_INSUFFICIENT"
    )

    manifest = {
        "stage": "A7FF-CORE28E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE28",
        "source_decision": core28.get("decision"),
        "decision": decision,
        "family_count": int(atlas.shape[0]),
        "ready_for_core29_family_count": ready_count,
        "independent_ready_family_count": independent_ready_count,
        "a7aif4_promoted_family_count": promoted_family_count,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core29_contract": decision.startswith("PASS_"),
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": (
            "A7FF-CORE29 independent family bounded generation/probe contract"
            if decision.startswith("PASS_")
            else "CORE28E blocker repair"
        ),
        "candidate_family_ids": next_candidates["family_id"].tolist(),
        "blocked_family_ids": blocked["family_id"].tolist(),
    }

    source_inventory.to_csv(RUNTIME / "a7ffcore28e_source_artifact_inventory.csv", index=False)
    atlas.to_csv(RUNTIME / "a7ffcore28e_data_family_atlas.csv", index=False)
    scorecard.to_csv(RUNTIME / "a7ffcore28e_independence_scorecard.csv", index=False)
    next_candidates.to_csv(RUNTIME / "a7ffcore28e_next_family_candidates.csv", index=False)
    blocked.to_csv(RUNTIME / "a7ffcore28e_blocked_families.csv", index=False)
    write_json(RUNTIME / "a7ffcore28e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE28E INDEPENDENT DATA-FAMILY ATLAS AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE28E is an atlas/contract audit. It does not run formula generation, numeric replay, alpha search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- family_count: `{manifest['family_count']}`",
        f"- ready_for_core29_family_count: `{ready_count}`",
        f"- independent_ready_family_count: `{independent_ready_count}`",
        f"- A7AI-F4 promoted ordinary-alpha family count: `{promoted_family_count}`",
        "",
        "## Ready Families",
        "",
        md_table(next_candidates[
            [
                "family_id",
                "data_family",
                "universe_scope",
                "pit_status",
                "independence_from_s0",
                "recommended_role",
                "notes",
            ]
        ]),
        "",
        "## Blocked Or Diagnostic Families",
        "",
        md_table(blocked[
            [
                "family_id",
                "data_family",
                "recommended_role",
                "blocked_pattern_risk",
                "notes",
            ]
        ]),
        "",
        "## Independence Scorecard",
        "",
        md_table(scorecard),
        "",
        "## Source Artifact Inventory",
        "",
        md_table(source_inventory),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(
            {
                "authorized": {
                    "A7FF-CORE29 independent family bounded generation/probe contract": manifest[
                        "authorizes_core29_contract"
                    ]
                },
                "not_authorized": {
                    "formula_generation_execution": True,
                    "search": True,
                    "large_search": True,
                    "alpha_proof": True,
                    "shadow_paper_live": True,
                },
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
