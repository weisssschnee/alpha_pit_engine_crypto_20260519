from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7aa0_label_feature_response_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AA0_LABEL_FEATURE_RESPONSE_CONTRACT_20260529.md"
Z9_MANIFEST = REPO / "runtime" / "a7al2z9_response_guided_partial_numeric_diagnostic" / "a7al2z9_manifest.json"
LINEAGE = REPO / "runtime" / "a7al0r_code_feature_regime_readiness_audit" / "a7al0r_feature_lineage_ledger.csv"


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

    z9 = read_json(Z9_MANIFEST)
    if not z9:
        raise SystemExit("A7AL-2Z9 manifest is required before A7AA-0")
    labels = pd.DataFrame(
        [
            {
                "label_family": "L0_raw_forward_return",
                "definition": "log(close_t+h)-log(close_t)",
                "role": "baseline raw forward return",
                "allowed_in_a7aa1": True,
            },
            {
                "label_family": "L1_cross_sectional_relative_return",
                "definition": "raw forward return minus timestamp cross-sectional mean",
                "role": "market-mode reduced relative return",
                "allowed_in_a7aa1": True,
            },
            {
                "label_family": "L3_liquidity_tier_relative_return",
                "definition": "raw forward return demeaned within liquidity_tier",
                "role": "liquidity-tier relative label",
                "allowed_in_a7aa1": True,
            },
            {
                "label_family": "L5_vol_adjusted_return",
                "definition": "raw forward return divided by realized_vol_168h",
                "role": "vol-normalized response",
                "allowed_in_a7aa1": True,
            },
            {
                "label_family": "L7_ranked_future_return",
                "definition": "timestamp cross-sectional rank percentile of raw forward return minus 0.5",
                "role": "ranked future return",
                "allowed_in_a7aa1": True,
            },
            {
                "label_family": "L2_BTC_ETH_beta_residual_return",
                "definition": "future return residualized versus BTC/ETH beta proxy",
                "role": "contract only; not used until beta matrix is frozen",
                "allowed_in_a7aa1": False,
            },
            {
                "label_family": "L6_downside_avoidance",
                "definition": "asymmetric downside/crash avoidance label",
                "role": "contract only; requires separate downside objective",
                "allowed_in_a7aa1": False,
            },
        ]
    )
    transforms = pd.DataFrame(
        [
            {"transform": "level", "uses_future": False, "description": "raw feature value"},
            {"transform": "delta_4h", "uses_future": False, "description": "feature_t - feature_t-4"},
            {"transform": "delta_24h", "uses_future": False, "description": "feature_t - feature_t-24"},
            {"transform": "cs_rank", "uses_future": False, "description": "timestamp cross-sectional rank percentile"},
            {"transform": "ts_zscore_168h", "uses_future": False, "description": "past rolling 168h zscore"},
        ]
    )
    controls = pd.DataFrame(
        [
            {"control": "one_bar_lag", "purpose": "entry latency survival"},
            {"control": "wrong_lag_future_24h", "purpose": "lookahead contamination check"},
            {"control": "wrong_lag_stale_168h", "purpose": "stale signal placebo"},
            {"control": "same_family_random", "purpose": "random signal placebo"},
        ]
    )
    candidate_fields = pd.DataFrame(
        [
            ("trade_return_1h", "price_return"),
            ("trade_return_24h", "price_return"),
            ("realized_vol_24h", "volatility"),
            ("realized_vol_168h", "volatility"),
            ("trade_quote_volume", "liquidity"),
            ("trade_count", "liquidity"),
            ("liquidity_rank_active_universe", "liquidity"),
            ("kline_taker_buy_quote_share", "taker_flow"),
            ("taker_buy_sell_volume_ratio_last", "taker_flow"),
            ("funding_rate", "funding"),
            ("funding_rate_abs_168h", "funding"),
            ("funding_rate_mean_168h", "funding"),
            ("premium_close_bps", "basis_premium"),
            ("mark_index_basis_bps", "basis_premium"),
            ("mark_trade_basis_bps", "basis_premium"),
            ("basis_abs_168h", "basis_premium"),
            ("premium_abs_168h", "basis_premium"),
            ("open_interest_last", "open_interest"),
            ("open_interest_value_last", "open_interest"),
            ("open_interest_change_24h", "open_interest"),
            ("oi_x_price_move_24h", "open_interest_interaction"),
            ("global_long_short_account_ratio_last", "positioning"),
            ("top_long_short_account_ratio_last", "positioning"),
            ("top_long_short_position_ratio_last", "positioning"),
            ("age_percentile_active_universe", "listing_age"),
            ("log1p_listing_age_days", "listing_age"),
            ("age_x_liquidity", "listing_age_interaction"),
            ("age_x_volatility", "listing_age_interaction"),
            ("volume_volatility_ratio_168h", "liquidity_volatility"),
            ("rolling_coverage_168h", "coverage"),
            ("gap_hours_recent_168h", "coverage"),
            ("median_quote_volume_168h", "liquidity"),
        ],
        columns=["field_name", "field_family"],
    )
    lineage = pd.read_csv(LINEAGE) if LINEAGE.exists() else pd.DataFrame()
    if not lineage.empty:
        candidate_fields = candidate_fields.merge(
            lineage[["field_name", "source_family", "feature_class", "allowed_for_search", "allowed_for_label"]].drop_duplicates("field_name"),
            on="field_name",
            how="left",
        )
    decision = "PASS_A7AA0_LABEL_FEATURE_RESPONSE_CONTRACT_READY_FOR_A7AA1"
    manifest = {
        "stage": "A7AA-0",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_response_map": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7aa1_primitive_response_map": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "source_z9_decision": z9.get("decision"),
        "source_z9_stress_clean_count": z9.get("stress_clean_clue_count"),
        "feature_count": int(len(candidate_fields)),
        "label_families_allowed_in_a7aa1": int(labels["allowed_in_a7aa1"].sum()),
        "uses_may_for_contract": False,
    }
    labels.to_csv(RUNTIME / "a7aa0_label_family_contract.csv", index=False)
    transforms.to_csv(RUNTIME / "a7aa0_transform_contract.csv", index=False)
    controls.to_csv(RUNTIME / "a7aa0_negative_control_contract.csv", index=False)
    candidate_fields.to_csv(RUNTIME / "a7aa0_candidate_primitive_fields.csv", index=False)
    write_json(RUNTIME / "a7aa0_manifest.json", manifest)
    write_json(
        RUNTIME / "a7aa0_authorization_matrix.json",
        {
            "A7AA-0": {"status": decision},
            "a7aa1_primitive_response_map": {"authorized": True},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AA-0 LABEL / FEATURE RESPONSE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AA-0 freezes the primitive response-map contract after Z-series formula-first diagnostics failed. It does not search, replay, train, or prove alpha.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Families",
        "",
        md_table(labels),
        "",
        "## Transforms",
        "",
        md_table(transforms),
        "",
        "## Candidate Primitive Fields",
        "",
        md_table(candidate_fields, 80),
        "",
        "## Controls",
        "",
        md_table(controls),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
