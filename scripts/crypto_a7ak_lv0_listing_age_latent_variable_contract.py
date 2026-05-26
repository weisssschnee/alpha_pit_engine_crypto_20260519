from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

SYMBOL_CLASSIFICATION = DATA_ROOT / "gold" / "metadata" / "binance_universe498_replay_1h_v1_symbol_classification_20260526.csv"
FEATURE_CONTRACT = DATA_ROOT / "gold" / "metadata" / "binance_universe498_replay_1h_v1_feature_contract_20260526.csv"
SEARCH_CONFIG = DATA_ROOT / "gold" / "metadata" / "binance_universe498_replay_1h_v1_a7ak_min_search_config_20260526.json"

OUT_DIR = ROOT / "runtime" / "a7ak_lv0_listing_age_latent_variable_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AK_LV0_LISTING_AGE_LATENT_VARIABLE_CONTRACT_20260526.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def observable_state_features() -> pd.DataFrame:
    rows = [
        ("listing_age_hours", "age", "timestamp - first_observed_trade_timestamp", "row-local observable after listing", "past_only"),
        ("listing_age_days", "age", "listing_age_hours / 24", "row-local observable after listing", "past_only"),
        ("log1p_listing_age_days", "age_transform", "log1p(listing_age_days)", "nonlinear age transform", "past_only"),
        ("sqrt_listing_age_days", "age_transform", "sqrt(listing_age_days)", "nonlinear age transform", "past_only"),
        ("age_bucket_dynamic", "age_transform", "<30d, 30-90d, 90-180d, 180-365d, >=365d", "diagnostic bucket only; not final state", "past_only"),
        ("age_percentile_active_universe", "age_transform", "cross-sectional percentile among active symbols at timestamp", "observable active cross-section; proof caveat from current universe", "timestamp_cross_section"),
        ("history_length_hours", "coverage", "available rows since first observed timestamp", "past coverage proxy", "past_only"),
        ("rolling_coverage_168h", "coverage", "source flags complete over trailing 168h", "data quality state", "past_only"),
        ("gap_hours_recent_168h", "coverage", "missing hours over trailing 168h", "data quality state", "past_only"),
        ("median_quote_volume_168h", "liquidity", "rolling median trade_quote_volume", "liquidity state", "past_only"),
        ("log_quote_volume_168h", "liquidity", "log1p(median_quote_volume_168h)", "liquidity transform", "past_only"),
        ("liquidity_rank_active_universe", "liquidity", "cross-sectional rank of rolling quote volume", "active universe liquidity tier", "timestamp_cross_section"),
        ("trade_count_168h", "activity", "rolling mean/sum trade_count", "activity state", "past_only"),
        ("realized_vol_24h", "volatility", "std of trade_return_1h over trailing 24h", "volatility state", "past_only"),
        ("realized_vol_72h", "volatility", "std of trade_return_1h over trailing 72h", "volatility state", "past_only"),
        ("realized_vol_168h", "volatility", "std of trade_return_1h over trailing 168h", "volatility state", "past_only"),
        ("volume_volatility_ratio_168h", "interaction", "log_quote_volume_168h / realized_vol_168h", "liquidity-volatility state", "past_only"),
        ("funding_rate_abs_168h", "funding", "rolling mean abs(funding_rate)", "crowding/funding state", "past_only"),
        ("funding_rate_mean_168h", "funding", "rolling mean funding_rate", "funding direction state", "past_only"),
        ("basis_abs_168h", "basis", "rolling mean abs(mark_index_basis_bps)", "basis dislocation state", "past_only"),
        ("premium_abs_168h", "basis", "rolling mean abs(premium_close_bps)", "premium dislocation state", "past_only"),
        ("open_interest_change_24h", "positioning", "pct/log change of open_interest_last", "positioning state", "past_only"),
        ("oi_x_price_move_24h", "interaction", "open_interest_change_24h * trade_return_24h", "crowding/positioning interaction", "past_only"),
        ("age_x_liquidity", "interaction", "log1p_listing_age_days * liquidity_rank/state", "age-liquidity interaction", "past_only"),
        ("age_x_volatility", "interaction", "log1p_listing_age_days * realized_vol_168h", "age-volatility interaction", "past_only"),
        ("age_x_funding_abs", "interaction", "log1p_listing_age_days * funding_rate_abs_168h", "age-funding interaction", "past_only"),
        ("is_major", "symbol_static", "BTC/ETH/BNB/SOL/XRP style major flag", "static symbol tier", "known_at_symbol_selection"),
        ("is_core12", "symbol_static", "legacy audited core12 flag", "static evidence layer", "known_at_symbol_selection"),
        ("contract_format", "symbol_static", "plain vs multiplier contract", "contract normalization risk", "known_at_symbol_selection"),
    ]
    return pd.DataFrame(rows, columns=["feature_name", "feature_group", "definition", "purpose", "timing_rule"])


def construction_rules() -> pd.DataFrame:
    rows = [
        ("LV1", "state_construction_period", "train only", "Fit transforms/clusters only on train rows; validation/recent evaluate frozen mapping"),
        ("LV1", "initial_state_model", "interpretable clustering", "First pass uses age/liquidity/vol/funding/basis/coverage features; avoid opaque model"),
        ("LV1", "normalization", "train-only robust zscore or rank", "No validation/test/May distribution in scaler"),
        ("LV1", "age_role", "input feature only", "Age bucket is diagnostic, not final state label"),
        ("LV1", "short_history_policy", "include in modeling if quality pass", "Short-history symbols can inform lifecycle states but not primary proof"),
        ("LV1", "age_lt_30d_policy", "fixed quota", "Do not discard; reserve explicit search quota and report separately"),
        ("LV2", "response_merge_period", "train only", "State response vector computed only on train"),
        ("LV2", "merge_rule", "response similarity + risk similarity", "Merge raw states if response vectors and cost/lag/funding/beta profiles align"),
        ("LV2", "freeze_rule", "freeze raw-to-merged map", "Apply frozen map to validation/recent; do not refit on outcomes"),
        ("LV3", "ranking_views", "global/age-neutral/latent-neutral", "Every candidate reports all three views"),
        ("LV3", "promotion_boundary", "strict proof universe primary", "Listing-aware states can support diagnostics/generalization, not standalone proof"),
    ]
    return pd.DataFrame(rows, columns=["stage", "rule_name", "rule_value", "rationale"])


def response_vector_definition() -> pd.DataFrame:
    rows = [
        ("future_return_mean", "mean next-bar/trade label return within train", "response", "train_only"),
        ("future_return_vol", "volatility of next-bar/trade label return within train", "risk", "train_only"),
        ("drawdown_proxy", "state-level cumulative drawdown proxy", "risk", "train_only"),
        ("cost20_survival", "state response after 20bps cost stress", "execution", "train_only"),
        ("lag1_survival", "state response after one-bar lag stress", "execution", "train_only"),
        ("funding_beta", "state beta to FundingCore/funding baseline", "exposure", "train_only"),
        ("btc_beta", "state beta to BTC return", "exposure", "train_only"),
        ("liquidity_beta", "state beta to liquidity factor", "exposure", "train_only"),
        ("volatility_beta", "state beta to volatility factor", "exposure", "train_only"),
        ("momentum_probe_response", "response to simple momentum probe", "signal_family_response", "train_only"),
        ("reversal_probe_response", "response to simple reversal probe", "signal_family_response", "train_only"),
        ("liquidity_probe_response", "response to liquidity/activity probe", "signal_family_response", "train_only"),
        ("basis_probe_response", "response to basis/premium probe", "signal_family_response", "train_only"),
        ("funding_probe_response", "response to observable funding probe", "signal_family_response", "train_only"),
        ("oi_positioning_probe_response", "response to OI/positioning probe", "signal_family_response", "train_only"),
    ]
    return pd.DataFrame(rows, columns=["response_component", "definition", "component_group", "allowed_fit_period"])


def quota_policy() -> pd.DataFrame:
    rows = [
        ("age_lt_30d", "listing_age_days < 30", 0.10, "fixed minimum", "Minimum 10% of LV smoke generation/selection slots when available; never zeroed due to short history"),
        ("age_30_90d", "30 <= listing_age_days < 90", 0.10, "soft minimum", "Lifecycle continuation bucket"),
        ("age_90_180d", "90 <= listing_age_days < 180", 0.10, "soft minimum", "Post-listing stabilization bucket"),
        ("age_180_365d", "180 <= listing_age_days < 365", 0.15, "soft minimum", "Maturing alt bucket"),
        ("age_ge_365d", "listing_age_days >= 365", 0.40, "primary mass", "Primary mature-history mass"),
        ("state_diversity_reserve", "underrepresented latent states", 0.15, "reserve", "Allocated to latent states with sufficient quality but low representation"),
    ]
    return pd.DataFrame(rows, columns=["quota_bucket", "definition", "target_share", "quota_type", "notes"])


def forbidden_inputs() -> pd.DataFrame:
    rows = [
        ("validation_or_recent_returns", "state construction / scaler / cluster fit", "Would leak evaluation outcomes"),
        ("May stress labels", "state construction / merge / quota / ranking", "Known adversarial stress; stress-only"),
        ("future delisting or survival", "symbol class or latent state", "Survivorship leakage"),
        ("future liquidity percentile", "row-level feature", "Must use timestamp-active or trailing window only"),
        ("post-period volume median", "state construction", "Use train-only or trailing windows"),
        ("control outcome superiority", "candidate promotion", "Negative controls can block, not optimize"),
    ]
    return pd.DataFrame(rows, columns=["forbidden_input", "forbidden_use", "reason"])


def authorization_matrix() -> dict[str, Any]:
    return {
        "decision": "PASS_A7AK_LV0_CONTRACT_READY_FOR_USER_APPROVAL",
        "executes_state_construction": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_lv1_after_user_approval": True,
        "authorizes_a7ak_min_without_lv": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "requires_user_approval_before_execution": True,
        "age_lt_30d_fixed_quota": "10% minimum of LV smoke generation/selection slots when available; not proof promotion quota",
        "proof_boundary": {
            "modeling": "U_all_quality_eligible can participate in train-only latent-state research",
            "primary_proof": "strict_full_history remains primary proof-style universe",
            "listing_aware": "generalization/lifecycle diagnostic only until frozen state map validates",
            "hold": "quality audit only",
        },
    }


def approval_checklist() -> pd.DataFrame:
    rows = [
        ("approve_lv1_state_feature_build", False, "Build row-level observable state features with train-only scalers"),
        ("approve_lv1_initial_clustering", False, "Fit initial interpretable latent states on train rows only"),
        ("approve_lv2_response_merge", False, "Compute train-only response vectors and frozen merge map"),
        ("approve_lv3_neutral_smoke", False, "Run global vs age-neutral vs latent-neutral field-family smoke"),
        ("approve_age_lt30_quota", False, "Reserve fixed age<30d quota in smoke; no direct proof promotion"),
    ]
    return pd.DataFrame(rows, columns=["approval_item", "approved_default", "description"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    symbols = pd.read_csv(SYMBOL_CLASSIFICATION)
    features = pd.read_csv(FEATURE_CONTRACT)
    search_config = read_json(SEARCH_CONFIG)

    obs = observable_state_features()
    rules = construction_rules()
    response = response_vector_definition()
    quotas = quota_policy()
    forbidden = forbidden_inputs()
    auth = authorization_matrix()
    checklist = approval_checklist()

    universe_counts = symbols.groupby(["search_eligibility", "liquidity_tier"], dropna=False).size().reset_index(name="symbols")
    feature_counts = features.groupby("source_class", dropna=False).size().reset_index(name="fields")
    manifest = {
        "generated_at": utc_now(),
        "decision": auth["decision"],
        "input_symbol_classification": str(SYMBOL_CLASSIFICATION),
        "input_feature_contract": str(FEATURE_CONTRACT),
        "input_search_config": str(SEARCH_CONFIG),
        "symbols": int(len(symbols)),
        "strict_full_history_symbols": int((symbols["search_eligibility"] == "strict_full_history").sum()),
        "listing_aware_symbols": int((symbols["search_eligibility"] == "listing_aware").sum()),
        "hold_symbols": int((symbols["search_eligibility"] == "hold_quality_or_short_history").sum()),
        "observable_state_features": int(len(obs)),
        "age_lt_30d_fixed_quota_share": 0.10,
        "executes_state_construction": False,
        "executes_replay": False,
        "executes_search": False,
        "requires_user_approval_before_execution": True,
    }

    write_json(OUT_DIR / "a7ak_lv0_manifest.json", manifest)
    write_json(OUT_DIR / "a7ak_lv0_authorization_matrix.json", auth)
    obs.to_csv(OUT_DIR / "a7ak_lv0_observable_state_features.csv", index=False)
    rules.to_csv(OUT_DIR / "a7ak_lv0_state_construction_rules.csv", index=False)
    response.to_csv(OUT_DIR / "a7ak_lv0_response_vector_definition.csv", index=False)
    quotas.to_csv(OUT_DIR / "a7ak_lv0_search_quota_policy.csv", index=False)
    forbidden.to_csv(OUT_DIR / "a7ak_lv0_forbidden_inputs.csv", index=False)
    checklist.to_csv(OUT_DIR / "a7ak_lv0_user_approval_checklist.csv", index=False)
    universe_counts.to_csv(OUT_DIR / "a7ak_lv0_universe_counts.csv", index=False)
    feature_counts.to_csv(OUT_DIR / "a7ak_lv0_input_feature_family_counts.csv", index=False)

    report = f"""# CRYPTO A7AK-LV0 Listing-Age Latent Variable Contract

Generated: {manifest["generated_at"]}

## Decision

```text
{auth["decision"]}
```

This stage defines the listing-age latent-variable framework and search quota policy. It does not construct states, does not run replay, and does not run search.

## Core Change

```text
Do not hard-bucket or discard short-history symbols by age.
Use age as one observable input into latent market state.
Merge states by train-only response similarity, not by age proximity.
Reserve a fixed age<30d search quota so new listings are studied instead of silently dropped.
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Input Universe Counts

{md_table(universe_counts)}

## Input Feature Families

{md_table(feature_counts)}

## Observable State Features

{md_table(obs, 80)}

## State Construction Rules

{md_table(rules)}

## Response Vector For Merge

{md_table(response)}

## Search Quota Policy

{md_table(quotas)}

## Forbidden Inputs

{md_table(forbidden)}

## User Approval Checklist

{md_table(checklist)}

## Execution Boundary

```text
NEXT ONLY AFTER USER APPROVAL:
  A7AK-LV1 train-only latent state feature build and initial clustering

NOT AUTHORIZED:
  replay
  search
  large search
  alpha proof
  shadow / paper / live
```
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
