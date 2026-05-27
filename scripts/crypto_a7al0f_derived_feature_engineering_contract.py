from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al0f_derived_feature_engineering_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AL0F_DERIVED_FEATURE_ENGINEERING_CONTRACT_20260527.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows: list[dict[str, Any]], limit: int | None = None) -> str:
    if limit is not None:
        rows = rows[:limit]
    if not rows:
        return "`<empty>`"
    fields = list(rows[0].keys())
    out = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(f, "")) for f in fields) + " |")
    return "\n".join(out)


def contract_rows() -> list[dict[str, Any]]:
    specs = [
        ("L0_raw_source", "trade_ohlcv", "trade OHLCV, taker buy quote share", "market price/liquidity base", "same-bar leakage, beta dominance", "wrong_lag_future,row_shuffle"),
        ("L0_raw_source", "mark_index_premium", "mark/index/premium OHLC and basis bps", "basis/premium state", "future basis semantic misuse", "wrong_lag_future,symbol_shuffle"),
        ("L0_raw_source", "funding", "funding_rate, funding_interval_hours", "funding state/exposure", "next funding leakage, funding baseline packaging", "wrong_lag_future,sign_flip"),
        ("L0_raw_source", "metrics_positioning", "OI, OI value, long-short ratios, taker ratio", "positioning/crowding state", "vendor 5m jitter, +2h fragility", "wrong_lag_future,time_shuffle"),
        ("L1_single_source_derived", "price_return", "trade_return_1h/24h, ranges", "past price state", "momentum beta packaging", "sign_flip,row_shuffle"),
        ("L1_single_source_derived", "liquidity", "rolling volume, trade count, liquidity rank", "liquidity expansion/contraction", "liquidity/age bias", "symbol_shuffle,same_family_placebo"),
        ("L1_single_source_derived", "volatility", "realized_vol 24/72/168h", "risk state", "vol beta dominance", "sign_flip,time_shuffle"),
        ("L1_single_source_derived", "funding_abs", "funding abs/mean rolling states", "funding crowding", "funding baseline dominance", "wrong_lag_future,sign_flip"),
        ("L1_single_source_derived", "basis_premium_abs", "basis_abs_168h, premium_abs_168h", "basis dislocation", "premium timestamp mismatch", "wrong_lag_future,symbol_shuffle"),
        ("L1_single_source_derived", "open_interest_change", "open_interest_change_1/4/24h", "leverage flow", "positioning publication lag", "wrong_lag_future,time_shuffle"),
        ("L2_cross_source_interaction", "oi_x_price", "OI change x price move", "leverage-flow pressure", "market beta packaging", "sign_flip,wrong_lag_future"),
        ("L2_cross_source_interaction", "funding_x_basis", "funding abs x basis dislocation", "crowded carry state", "FundingCore packaging", "same_family_placebo,wrong_lag_future"),
        ("L2_cross_source_interaction", "volume_x_volatility", "liquidity x realized vol with cap", "activity stress state", "liquidity-vol cluster collapse", "cluster_cap,symbol_shuffle"),
        ("L2_cross_source_interaction", "positioning_x_trend", "long-short ratios x trend/reversal", "crowding trend state", "ratio direction semantic error", "sign_flip,wrong_lag_future"),
        ("L2_cross_source_interaction", "premium_x_market_state", "premium dislocation x market trend/vol", "basis stress interaction", "state overfit", "time_shuffle,same_family_placebo"),
        ("L3_cross_sectional_state", "rank_percentile", "timestamp rank/zscore/percentile", "relative value/state expression", "future universe/survivorship", "symbol_shuffle,row_shuffle"),
        ("L3_cross_sectional_state", "dispersion_breadth", "cross-sectional dispersion and breadth", "market regime state", "using label-period breadth", "wrong_lag_future,time_shuffle"),
        ("L3_cross_sectional_state", "tier_relative", "liquidity/age/meme tier relative values", "neutralized cross-section", "small-group noise", "small_group_fallback_audit"),
        ("L4_upper_regime_state", "market_beta", "market trend/vol/breadth", "top-level market regime", "market direction overfit", "train_only_threshold_audit"),
        ("L4_upper_regime_state", "leverage_crowding", "market OI/funding/positioning aggregate", "system leverage state", "funding baseline packaging", "train_only_threshold_audit"),
        ("L4_upper_regime_state", "meme_listing_cycle", "meme risk, listing pressure", "lifecycle/tail regime", "May-style stress overfit", "train_only_threshold_audit"),
    ]
    rows = []
    for level, family, fields, role, failure, controls in specs:
        rows.append(
            {
                "feature_level": level,
                "feature_family": family,
                "candidate_fields_or_transforms": fields,
                "economic_role": role,
                "pit_rule": "+1h primary; +2h conservative stress mandatory",
                "train_fit_rule": "train-only thresholds for ranks/regime; rolling past-only otherwise",
                "expected_failure_mode": failure,
                "negative_control": controls,
                "allowed_in_a7al1_baseline": True,
                "allowed_in_a7al2_formula_search": False,
            }
        )
    return rows


def allowed_set() -> dict[str, Any]:
    return {
        "levels_allowed_for_A7AL1": ["L0_raw_source", "L1_single_source_derived", "L2_cross_source_interaction", "L3_cross_sectional_state", "L4_upper_regime_state"],
        "mandatory_constraints": [
            "feature lineage present",
            "+1h primary and +2h stress reported",
            "no label fields",
            "train-only thresholds for regime/rank bins",
            "negative controls must be weaker than original",
            "neutralization and beta residual must be reported",
        ],
        "derived_fields_are_first_class": True,
    }


def blocked_set() -> dict[str, Any]:
    return {
        "blocked_fields": ["forward_trade_return_1h", "fwd_ret_1h", "fwd_ret_4h", "fwd_ret_24h"],
        "blocked_patterns": [
            "future funding or next funding as signal",
            "same-bar execution from bar-close fields",
            "validation/test-fitted thresholds",
            "May-derived thresholds or weights",
            "global-rank-only promotion without neutralized survival",
            "wrong-lag controls comparable to original",
        ],
    }


def caps() -> dict[str, Any]:
    return {
        "field_family_caps": {
            "liquidity_volatility_interaction": 0.15,
            "funding_basis_interaction": 0.20,
            "meme_listing_cycle": 0.15,
            "single_raw_source_family": 0.35,
        },
        "search_quota_policy": {
            "age_lt30d_minimum_search_quota": 0.10,
            "strict_full_history_minimum_search_quota": 0.35,
            "listing_aware_max_primary_proof_weight": 0.0,
        },
        "small_group_policy": {
            "min_group_symbols": 10,
            "min_group_active_symbols_per_hour": 8,
            "fallback": "parent state -> liquidity tier -> global",
        },
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    rows = contract_rows()
    write_csv(RUNTIME / "a7al0f_feature_generation_contract.csv", rows)
    (RUNTIME / "a7al0f_allowed_derived_feature_set.json").write_text(json.dumps(allowed_set(), indent=2), encoding="utf-8")
    (RUNTIME / "a7al0f_blocked_feature_set.json").write_text(json.dumps(blocked_set(), indent=2), encoding="utf-8")
    (RUNTIME / "a7al0f_feature_family_caps.json").write_text(json.dumps(caps(), indent=2), encoding="utf-8")

    manifest = {
        "generated_at": generated_at,
        "decision": "PASS_A7AL0F_DERIVED_FEATURE_ENGINEERING_CONTRACT",
        "executes_search": False,
        "executes_replay": False,
        "feature_family_rows": len(rows),
        "derived_fields_first_class": True,
        "authorizes_a7al0g_upper_regime_builder": True,
        "authorizes_a7al1_baseline": False,
        "authorizes_formula_search": False,
        "blockers": [],
    }
    (RUNTIME / "a7al0f_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = f"""# CRYPTO A7AL-0F Derived Feature Engineering Contract

Generated: {generated_at}

## Decision

```text
{manifest["decision"]}
```

Derived fields are first-class state/search inputs when they have lineage, PIT lag, train-only fitting where needed, and explicit negative controls.

## Feature Generation Contract

{md_table(rows)}

## Boundary

```text
AUTHORIZED NEXT:
  A7AL-0G upper-regime state builder

NOT AUTHORIZED:
  A7AL-1 baseline replay
  A7AL-2 formula search
  alpha proof / shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
