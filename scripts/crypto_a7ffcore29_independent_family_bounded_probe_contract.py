from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore29_independent_family_bounded_probe_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE29_INDEPENDENT_FAMILY_BOUNDED_PROBE_CONTRACT_20260602.md"
CORE28E = REPO / "runtime" / "a7ffcore28e_independent_data_family_atlas_audit" / "a7ffcore28e_manifest.json"
CORE28E_CANDIDATES = (
    REPO / "runtime" / "a7ffcore28e_independent_data_family_atlas_audit" / "a7ffcore28e_next_family_candidates.csv"
)


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
    source = read_json(CORE28E)
    if source.get("decision") != "PASS_A7FFCORE28E_INDEPENDENT_DATA_FAMILY_ATLAS_READY_FOR_CORE29_CONTRACT":
        raise SystemExit(f"CORE28E is not ready for CORE29: {source.get('decision')}")
    candidates = pd.read_csv(CORE28E_CANDIDATES)
    required_families = {"F1a_aggtrades_flow_microstructure", "F1b_taker_flow_market_panel", "F2a_basis_funding_independent"}
    missing = sorted(required_families - set(candidates["family_id"].astype(str)))
    if missing:
        raise SystemExit(f"CORE28E candidate family set incomplete: {missing}")

    family_contract = pd.DataFrame(
        [
            {
                "family_id": "F1a_aggtrades_flow_microstructure",
                "scope": "core12_bounded",
                "role": "independent_flow_state_interaction",
                "allowed_motifs": "signed_flow_reversal; large_trade_shock; flow_x_basis_or_funding_state; flow_x_low_turnover",
                "blocked_motifs": "A7V activity/liquidity self-reproduction; standalone volume/trade_count rank",
                "required_adapter": "aggtrades_enhanced_field_adapter",
                "max_blueprints": 800,
                "preflight_rows": 160,
                "numeric_probe_rows": 80,
            },
            {
                "family_id": "F1b_taker_flow_market_panel",
                "scope": "top498_listing_aware",
                "role": "top498_flow_interaction",
                "allowed_motifs": "taker_share_x_basis; taker_share_x_volatility_compression; taker_share_x_liquidity_tier; low_turnover_flow_state",
                "blocked_motifs": "standalone taker-share rank; standalone activity/liquidity rank",
                "required_adapter": "existing_top498_panel_fields",
                "max_blueprints": 800,
                "preflight_rows": 160,
                "numeric_probe_rows": 80,
            },
            {
                "family_id": "F2a_basis_funding_independent",
                "scope": "top498_listing_aware",
                "role": "basis_funding_dislocation_interaction",
                "allowed_motifs": "basis_delta_x_funding_abs; basis_dislocation_x_flow; funding_persistence_x_low_turnover; H8_H24_dislocation",
                "blocked_motifs": "basis-only wrapper; funding-only wrapper; direct S0 positioning-price-basis rerun",
                "required_adapter": "existing_top498_panel_fields",
                "max_blueprints": 800,
                "preflight_rows": 160,
                "numeric_probe_rows": 80,
            },
        ]
    )
    budget_plan = pd.DataFrame(
        [
            {"budget_item": "max_total_blueprints", "value": 2400, "notes": "contract cap; no generation executed here"},
            {"budget_item": "materialization_preflight_rows", "value": 480, "notes": "balanced 160 rows per family"},
            {"budget_item": "numeric_probe_rows", "value": 240, "notes": "only after adapter/preflight pass"},
            {"budget_item": "min_family_count", "value": 3, "notes": "all CORE28E candidate families represented"},
            {"budget_item": "max_single_family_share", "value": 0.34, "notes": "preflight and numeric queue cap"},
            {"budget_item": "max_single_motif_share", "value": 0.20, "notes": "prevent motif collapse"},
        ]
    )
    allowed_fields = pd.DataFrame(
        [
            {"field_token": "signed_aggressor_notional", "family_id": "F1a_aggtrades_flow_microstructure", "role": "flow"},
            {"field_token": "signed_aggressor_quantity", "family_id": "F1a_aggtrades_flow_microstructure", "role": "flow"},
            {"field_token": "volume_imbalance", "family_id": "F1a_aggtrades_flow_microstructure", "role": "flow_state"},
            {"field_token": "max_trade_notional", "family_id": "F1a_aggtrades_flow_microstructure", "role": "large_trade_state"},
            {"field_token": "kline_taker_buy_quote_share", "family_id": "F1b_taker_flow_market_panel", "role": "taker_flow"},
            {"field_token": "kline_quote_volume", "family_id": "F1b_taker_flow_market_panel", "role": "liquidity_state"},
            {"field_token": "realized_vol_168h", "family_id": "F1b_taker_flow_market_panel", "role": "volatility_state"},
            {"field_token": "mark_index_basis_bps", "family_id": "F2a_basis_funding_independent", "role": "basis"},
            {"field_token": "premium_close_bps", "family_id": "F2a_basis_funding_independent", "role": "premium"},
            {"field_token": "funding_rate", "family_id": "F2a_basis_funding_independent", "role": "funding"},
            {"field_token": "funding_rate_abs_168h", "family_id": "F2a_basis_funding_independent", "role": "funding_state"},
        ]
    )
    forbidden = pd.DataFrame(
        [
            {"pattern": "direct_OI_price_rerun", "reason": "S0 was single-lane only and superseded as diagnostic reference"},
            {"pattern": "basis_only_wrapper", "reason": "basis-only promotion collapsed to narrow surface"},
            {"pattern": "funding_only_wrapper", "reason": "funding-only wrapper is not independent family evidence"},
            {"pattern": "activity_liquidity_self_reproduction", "reason": "A7V activity/liquidity family remains blocked"},
            {"pattern": "raw_OKX_Binance_direct_price_comparison", "reason": "requires canonical contract-unit fields"},
            {"pattern": "forward_only_cross_exchange_as_historical_proof", "reason": "cross-exchange overlay is diagnostic/recent only"},
            {"pattern": "liquidation_orderbook_without_PIT_contract", "reason": "new data source contract required"},
        ]
    )
    adapter_requirements = pd.DataFrame(
        [
            {
                "adapter": "aggtrades_enhanced_field_adapter",
                "required_for": "F1a_aggtrades_flow_microstructure",
                "must_check": "field existence; timestamp after-hour availability; core12 coverage; NaN/inf; role trace",
                "blocking_if_missing": True,
            },
            {
                "adapter": "existing_top498_panel_fields",
                "required_for": "F1b/F2a",
                "must_check": "field contract; materialization parity; label alignment; no S0-only queue dominance",
                "blocking_if_missing": True,
            },
            {
                "adapter": "control_attachment",
                "required_for": "all",
                "must_check": "row shuffle; time shuffle; wrong lag; stale; same-family placebo",
                "blocking_if_missing": True,
            },
        ]
    )
    authorization = {
        "authorized": {
            "A7FF-CORE29E independent family dry-generation/materialization adapter preflight": True,
            "A7FF-CORE29E numeric probe": False,
        },
        "not_authorized": {
            "formula_generation_execution_beyond_contract": True,
            "search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    manifest = {
        "stage": "A7FF-CORE29",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE28E",
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE29_INDEPENDENT_FAMILY_BOUNDED_PROBE_CONTRACT_READY_FOR_CORE29E",
        "family_count": int(family_contract.shape[0]),
        "max_total_blueprints": 2400,
        "materialization_preflight_rows": 480,
        "numeric_probe_rows_after_preflight": 240,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core29e_preflight": True,
        "authorizes_numeric_probe": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE29E independent family dry-generation/materialization adapter preflight",
    }

    family_contract.to_csv(RUNTIME / "a7ffcore29_family_contract.csv", index=False)
    budget_plan.to_csv(RUNTIME / "a7ffcore29_budget_plan.csv", index=False)
    allowed_fields.to_csv(RUNTIME / "a7ffcore29_allowed_field_tokens.csv", index=False)
    forbidden.to_csv(RUNTIME / "a7ffcore29_forbidden_patterns.csv", index=False)
    adapter_requirements.to_csv(RUNTIME / "a7ffcore29_adapter_requirements.csv", index=False)
    write_json(RUNTIME / "a7ffcore29_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore29_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-CORE29 INDEPENDENT FAMILY BOUNDED PROBE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE29 is a contract. It defines a bounded independent-family generation/preflight envelope but does not execute generation, numeric replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Family Contract",
        "",
        md_table(family_contract),
        "",
        "## Budget Plan",
        "",
        md_table(budget_plan),
        "",
        "## Allowed Field Tokens",
        "",
        md_table(allowed_fields),
        "",
        "## Forbidden Patterns",
        "",
        md_table(forbidden),
        "",
        "## Adapter Requirements",
        "",
        md_table(adapter_requirements),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
