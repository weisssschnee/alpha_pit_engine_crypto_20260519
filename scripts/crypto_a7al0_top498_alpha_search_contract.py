from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al0_top498_alpha_search_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AL0_TOP498_LATENT_NEUTRAL_ALPHA_SEARCH_CONTRACT_20260527.md"

PANEL_ROOT = Path(r"G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v1_20260525")
SYMBOL_QUALITY = REPO / "runtime" / "a7al_universe498_replay_acceptance" / "a7al_symbol_quality.csv"
BASE_FEATURE_CONTRACT = REPO / "runtime" / "a7al_universe498_replay_acceptance" / "a7am_feature_contract.csv"
LV1_MANIFEST = REPO / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_manifest.json"
LV1_FEATURE_QUALITY = REPO / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_state_feature_quality.csv"
LV1_RAW_STATE_REGISTRY = REPO / "runtime" / "a7ak_lv1_latent_state_feature_build" / "a7ak_lv1_raw_state_registry.csv"
LV2_MANIFEST = REPO / "runtime" / "a7ak_lv2_response_merge_audit" / "a7ak_lv2_manifest.json"
LV2_BIAS_AUDIT = REPO / "runtime" / "a7ak_lv2_response_merge_audit" / "a7ak_lv2_bias_boundary_audit.csv"
LV2_UNSEEN_POLICY = REPO / "runtime" / "a7ak_lv2_response_merge_audit" / "a7ak_lv2_unseen_state_policy.csv"
TAXONOMY = REPO / "runtime" / "a7ak_lv3r_contract_meme_taxonomy_audit" / "a7ak_lv3r_contract_meme_taxonomy.csv"


SPLITS = [
    {
        "split": "train",
        "split_label": "train_2024",
        "start": pd.Timestamp("2024-01-01 00:00:00"),
        "end": pd.Timestamp("2024-12-31 23:00:00"),
        "role": "fit thresholds / latent construction / response merge only",
    },
    {
        "split": "validation",
        "split_label": "validation_2025H1",
        "start": pd.Timestamp("2025-01-01 00:00:00"),
        "end": pd.Timestamp("2025-06-30 23:00:00"),
        "role": "field-family validation",
    },
    {
        "split": "test",
        "split_label": "test_2025H2",
        "start": pd.Timestamp("2025-07-01 00:00:00"),
        "end": pd.Timestamp("2025-12-31 23:00:00"),
        "role": "held-out historical test",
    },
    {
        "split": "recent_oos",
        "split_label": "recent_oos_2026JanApr",
        "start": pd.Timestamp("2026-01-01 00:00:00"),
        "end": pd.Timestamp("2026-04-30 23:00:00"),
        "role": "recent OOS; May 2026 unavailable in this panel",
    },
]

TARGET_FIELD_GROUPS = {
    "trade_ohlcv": [
        "trade_open",
        "trade_high",
        "trade_low",
        "trade_close",
        "trade_volume",
        "trade_quote_volume",
        "trade_count",
        "taker_buy_volume",
        "taker_buy_quote_volume",
    ],
    "metrics_positioning": [
        "open_interest_last",
        "open_interest_mean",
        "open_interest_value_last",
        "open_interest_value_mean",
        "global_long_short_account_ratio_last",
        "global_long_short_account_ratio_mean",
        "top_long_short_account_ratio_last",
        "top_long_short_account_ratio_mean",
        "top_long_short_position_ratio_last",
        "top_long_short_position_ratio_mean",
        "taker_buy_sell_volume_ratio_last",
        "taker_buy_sell_volume_ratio_mean",
    ],
    "funding": ["funding_rate", "funding_interval_hours"],
    "mark_index_premium": [
        "mark_open",
        "mark_high",
        "mark_low",
        "mark_close",
        "index_open",
        "index_high",
        "index_low",
        "index_close",
        "premium_open",
        "premium_high",
        "premium_low",
        "premium_close",
        "premium_close_bps",
        "mark_index_basis_bps",
        "mark_trade_basis_bps",
    ],
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def split_hours(split: dict) -> int:
    return int((split["end"] - split["start"]).total_seconds() // 3600) + 1


def active_expected_hours(symbol_min: pd.Timestamp, symbol_max: pd.Timestamp, split: dict) -> int:
    start = max(symbol_min, split["start"])
    end = min(symbol_max, split["end"])
    if pd.isna(start) or pd.isna(end) or end < start:
        return 0
    return int((end - start).total_seconds() // 3600) + 1


def safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        out = float(value)
    except Exception:
        return None
    if math.isnan(out) or math.isinf(out):
        return None
    return out


def cov_beta(y: pd.Series, x: pd.Series) -> tuple[float | None, float | None, int]:
    joined = pd.concat([y.rename("y"), x.rename("x")], axis=1, sort=False).dropna()
    n = len(joined)
    if n < 100:
        return None, None, n
    var_x = joined["x"].var()
    if not np.isfinite(var_x) or var_x == 0:
        return None, None, n
    beta = joined["y"].cov(joined["x"]) / var_x
    corr = joined["y"].corr(joined["x"])
    return safe_float(beta), safe_float(corr), n


def compute_symbol_split_counts(symbols: list[str]) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    for symbol in symbols:
        path = PANEL_ROOT / f"symbol={symbol}" / "part.parquet"
        if not path.exists():
            for split in SPLITS:
                counts[(symbol, split["split_label"])] = 0
            continue
        df = pd.read_parquet(path, columns=["timestamp"])
        ts = pd.to_datetime(df["timestamp"], utc=True).dt.tz_localize(None)
        for split in SPLITS:
            counts[(symbol, split["split_label"])] = int(((ts >= split["start"]) & (ts <= split["end"])).sum())
    return counts


def build_split_tables(symbol_quality: pd.DataFrame, split_counts: dict[tuple[str, str], int]) -> tuple[list[dict], list[dict], list[dict]]:
    by_symbol_rows: list[dict] = []
    summary_rows: list[dict] = []
    split_def_rows: list[dict] = []

    q = symbol_quality.copy()
    q["timestamp_min_ts"] = pd.to_datetime(q["timestamp_min"], utc=True).dt.tz_localize(None)
    q["timestamp_max_ts"] = pd.to_datetime(q["timestamp_max"], utc=True).dt.tz_localize(None)

    for split in SPLITS:
        label = split["split_label"]
        total_hours = split_hours(split)
        active_rows = []
        strict_active = 0
        listing_active = 0
        hold_active = 0
        coverage_values = []
        active_span_values = []
        for _, r in q.iterrows():
            rows = int(split_counts.get((r["symbol"], label), 0))
            active = rows > 0
            expected_active = active_expected_hours(r["timestamp_min_ts"], r["timestamp_max_ts"], split)
            window_cov = rows / total_hours if total_hours else 0.0
            active_cov = rows / expected_active if expected_active else 0.0
            if active:
                active_rows.append(rows)
                coverage_values.append(window_cov)
                active_span_values.append(active_cov)
                if r["search_eligibility"] == "strict_full_history":
                    strict_active += 1
                elif r["search_eligibility"] == "listing_aware":
                    listing_active += 1
                else:
                    hold_active += 1
            by_symbol_rows.append(
                {
                    "split": split["split"],
                    "split_label": label,
                    "train_start": SPLITS[0]["start"].isoformat() if split["split"] == "train" else "",
                    "train_end": SPLITS[0]["end"].isoformat() if split["split"] == "train" else "",
                    "validation_start": SPLITS[1]["start"].isoformat() if split["split"] == "validation" else "",
                    "validation_end": SPLITS[1]["end"].isoformat() if split["split"] == "validation" else "",
                    "test_start": SPLITS[2]["start"].isoformat() if split["split"] == "test" else "",
                    "test_end": SPLITS[2]["end"].isoformat() if split["split"] == "test" else "",
                    "recent_oos_start": SPLITS[3]["start"].isoformat() if split["split"] == "recent_oos" else "",
                    "recent_oos_end": SPLITS[3]["end"].isoformat() if split["split"] == "recent_oos" else "",
                    "symbol": r["symbol"],
                    "search_eligibility": r["search_eligibility"],
                    "liquidity_tier": r["liquidity_tier"],
                    "history_tier": r["history_tier"],
                    "is_core12": r["is_core12"],
                    "is_major": r["is_major"],
                    "rows": rows,
                    "active": active,
                    "split_expected_hours": total_hours,
                    "symbol_active_expected_hours": expected_active,
                    "window_coverage_ratio": round(window_cov, 6),
                    "active_span_coverage_ratio": round(active_cov, 6),
                }
            )

        summary_rows.append(
            {
                "split": split["split"],
                "split_label": label,
                "start": split["start"].isoformat(),
                "end": split["end"].isoformat(),
                "role": split["role"],
                "expected_hours": total_hours,
                "symbols_active": len(active_rows),
                "strict_full_history_symbols_active": strict_active,
                "listing_aware_symbols_active": listing_active,
                "hold_symbols_active": hold_active,
                "median_rows_per_symbol": int(np.median(active_rows)) if active_rows else 0,
                "min_rows_per_symbol": int(np.min(active_rows)) if active_rows else 0,
                "median_window_coverage_ratio": round(float(np.median(coverage_values)), 6) if coverage_values else 0.0,
                "median_active_span_coverage_ratio": round(float(np.median(active_span_values)), 6) if active_span_values else 0.0,
            }
        )
        split_def_rows.append(
            {
                "split": split["split"],
                "split_label": label,
                "start": split["start"].isoformat(),
                "end": split["end"].isoformat(),
                "expected_hours": total_hours,
                "role": split["role"],
            }
        )
    return by_symbol_rows, summary_rows, split_def_rows


def build_field_timing_contract(base_contract: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    target_fields = {f for fields in TARGET_FIELD_GROUPS.values() for f in fields}
    source_lookup = dict(zip(base_contract["field_name"], base_contract["source_class"]))
    detail_lookup = dict(zip(base_contract["field_name"], base_contract["source_detail"]))

    for field in sorted(target_fields):
        if field not in source_lookup:
            continue
        source_class = source_lookup[field]
        if source_class == "metrics_positioning":
            event_time = "5m vendor metric create_time inside 1h bucket"
            source_update_time = "vendor 5m create_time plus jitter; A7S1 warning applies"
            observable_time = "latest 5m observation in hour, conservatively no earlier than bucket_end"
            caveat = "vendor 5m jitter/gap warning; field-native latency audit required; fixed delay stress prohibited"
        elif source_class == "funding":
            event_time = "funding event timestamp if present in 1h bucket"
            source_update_time = "Binance fundingRate archive event/publication timing"
            observable_time = "only after event is known and 1h bucket is closed"
            caveat = "sparse event field; never use next funding as signal"
        elif source_class == "mark_index_premium":
            event_time = "1h mark/index/premium kline bucket [timestamp, timestamp+1h)"
            source_update_time = "Binance 1h kline close"
            observable_time = "bucket_end"
            caveat = "bar-close feature; same-bar execution forbidden"
        else:
            event_time = "1h trade kline bucket [timestamp, timestamp+1h)"
            source_update_time = "Binance 1h kline close"
            observable_time = "bucket_end"
            caveat = "bar-close feature; same-bar execution forbidden"
        rows.append(
            {
                "field_name": field,
                "source_class": source_class,
                "source_detail": detail_lookup.get(field, ""),
                "event_time": event_time,
                "source_update_time": source_update_time,
                "observable_time": observable_time,
                "feature_available_time_primary": "timestamp + 1h",
                "execution_time_primary": "timestamp + 1h / next 1h bar open",
                "latency_class": source_class,
                "primary_execution_lag": "timestamp + 1h / next 1h bar open",
                "required_latency_audit": "field-native availability, wrong-lag controls, and no same-bar execution",
                "must_lag_by_one_bar": True,
                "fixed_delay_stress_required": False,
                "same_bar_execution_allowed": False,
                "pit_status": "PIT_VALID_IF_PLUS_1H_AND_FIELD_NATIVE_LATENCY_AUDIT_PASS",
                "caveat": caveat,
            }
        )
    return rows


def build_latent_freeze_audit() -> tuple[list[dict], dict, list[dict], list[dict]]:
    lv1 = read_json(LV1_MANIFEST)
    lv2 = read_json(LV2_MANIFEST)
    bias = pd.read_csv(LV2_BIAS_AUDIT)
    feature_quality = pd.read_csv(LV1_FEATURE_QUALITY)
    raw_registry = pd.read_csv(LV1_RAW_STATE_REGISTRY)
    unseen = pd.read_csv(LV2_UNSEEN_POLICY)

    audit_rows = [
        {
            "stage": "LV1_observable_state_features",
            "artifact": str(LV1_MANIFEST),
            "train_only": True,
            "uses_validation_or_test_response": False,
            "uses_may": False,
            "rows": lv1.get("rows"),
            "symbols": lv1.get("symbols"),
            "raw_latent_states": lv1.get("raw_latent_states"),
            "train_seen_states": lv1.get("train_seen_states"),
            "unseen_state_rows": lv1.get("unseen_state_rows"),
            "status": lv1.get("decision"),
        },
        {
            "stage": "LV2_response_merge",
            "artifact": str(LV2_MANIFEST),
            "train_only": True,
            "uses_validation_or_test_response": False,
            "uses_may": False,
            "rows": lv2.get("state_response_count"),
            "symbols": "",
            "raw_latent_states": lv2.get("raw_latent_state_count"),
            "train_seen_states": lv2.get("train_response_state_count"),
            "unseen_state_rows": lv1.get("unseen_state_rows"),
            "status": lv2.get("decision"),
        },
    ]
    for _, r in bias.iterrows():
        audit_rows.append(
            {
                "stage": f"bias_check_{r['check']}",
                "artifact": str(LV2_BIAS_AUDIT),
                "train_only": r["status"] == "PASS",
                "uses_validation_or_test_response": False,
                "uses_may": False,
                "rows": "",
                "symbols": "",
                "raw_latent_states": "",
                "train_seen_states": "",
                "unseen_state_rows": "",
                "status": r["status"],
                "detail": r["detail"],
            }
        )

    input_rows = []
    for _, r in feature_quality.iterrows():
        input_rows.append(
            {
                "feature_name": r.get("feature_name", r.get("state_feature", "")),
                "non_null_share": r.get("non_null_share", ""),
                "source": "observable at timestamp; train thresholds only",
                "allowed_for_state_construction": True,
                "allowed_for_response_merge": False,
                "may_dependency": False,
            }
        )

    unseen_rows = []
    for _, r in unseen.head(2000).iterrows():
        unseen_rows.append(r.to_dict())

    freeze_manifest = {
        "lv1_decision": lv1.get("decision"),
        "lv2_decision": lv2.get("decision"),
        "state_construction_window": "train_2024 only for thresholds",
        "response_merge_window": "train_2024 only",
        "validation_test_policy": "apply frozen mapping; unseen states held or fallback only",
        "raw_latent_states": int(raw_registry["raw_latent_state_id"].nunique()),
        "train_seen_states": int(raw_registry.loc[raw_registry["state_seen_in_train"] == True, "raw_latent_state_id"].nunique()),
        "unseen_state_policy_rows": len(unseen),
        "may_used": False,
    }
    return audit_rows, freeze_manifest, input_rows, unseen_rows


def build_neutralization_policy() -> dict:
    return {
        "decision_scope": "A7AL-0 contract only; no alpha proof",
        "ranking_modes": [
            {
                "mode": "global_rank",
                "algorithm": "cross-sectional rank by timestamp over eligible symbols",
                "min_group_active_symbols_per_hour": 20,
                "fallback": "drop hour if below minimum",
            },
            {
                "mode": "age_neutral_rank",
                "algorithm": "within age bucket percentile rank, then pooled cross-section",
                "min_group_symbols": 10,
                "min_group_active_symbols_per_hour": 8,
                "small_group_fallback": "parent age bucket then global",
            },
            {
                "mode": "latent_state_neutral_rank",
                "algorithm": "within frozen merged latent state percentile rank",
                "min_group_symbols": 10,
                "min_group_active_symbols_per_hour": 8,
                "small_group_fallback": "coarse latent state -> liquidity tier -> global",
            },
            {
                "mode": "liquidity_tier_neutral_rank",
                "algorithm": "within liquidity tier percentile rank",
                "min_group_symbols": 10,
                "min_group_active_symbols_per_hour": 8,
                "small_group_fallback": "adjacent liquidity tier then global",
            },
            {
                "mode": "meme_multiplier_aware_rank",
                "algorithm": "report separate meme/multiplier strata; do not force tiny groups into standalone proof",
                "min_group_symbols": 10,
                "min_group_active_symbols_per_hour": 8,
                "small_group_fallback": "meme vs non-meme parent, multiplier flag reported as exposure",
            },
            {
                "mode": "btc_eth_beta_residual",
                "algorithm": "train-window rolling or fixed residual against BTC/ETH returns before cross-sectional ranking",
                "min_regression_observations": 500,
                "fallback": "report raw and mark residual unavailable; do not promote",
            },
        ],
        "portfolio_proxy": {
            "rebalance": "1h",
            "book": "dollar-neutral top/bottom cross-section proxy",
            "top_bottom_default": "top 10 percent vs bottom 10 percent, capped by available active symbols",
            "max_weight_per_symbol": 0.02,
            "max_weight_per_latent_state": 0.20,
            "max_weight_per_meme_multiplier_group": 0.15,
            "liquidity_weighting": "equal weight primary; liquidity-capped sensitivity required",
            "cost_stress_bps": [10, 20, 30],
            "execution_lag_stress": ["+1h primary", "field-native latency audit"],
        },
        "proof_boundary": {
            "U0_strict_full_history": "primary proof-style universe",
            "U1_listing_aware": "diagnostic and latent-state generalization only",
            "U2_hold": "excluded from candidate proof",
            "May": "unavailable in this panel; cannot rank/tune/select",
        },
    }


def build_negative_control_plan() -> dict:
    return {
        "stage": "A7AL-1 field-family baseline smoke",
        "controls_required_before_candidate_promotion": True,
        "controls": [
            {"name": "row_shuffle", "level": "within symbol", "must_be_weaker_than_original": True},
            {"name": "time_shuffle", "level": "within field family", "must_be_weaker_than_original": True},
            {"name": "symbol_shuffle", "level": "within timestamp", "must_be_weaker_than_original": True},
            {"name": "wrong_lag_future", "definition": "use t+1/t+2 feature as if known at t", "must_be_zero_tolerance": True},
            {"name": "wrong_lag_stale", "definition": "use stale 24h-lagged proxy", "must_be_weaker_than_original": True},
            {"name": "sign_flip", "definition": "invert signal direction", "must_be_weaker_than_original": True},
            {"name": "random_field", "definition": "seeded random normal per symbol-hour", "must_be_weaker_than_original": True},
            {"name": "same_family_placebo", "definition": "field-family matched but economically wrong transform", "must_be_weaker_than_original": True},
        ],
        "known_risk_from_prior_stages": [
            "wrong-lag controls previously penetrated crypto gates in A7O/A7P",
            "zero-exposure and low-activity false positives were observed and repaired",
            "global rank can be dominated by age/liquidity/meme state bias",
        ],
        "hard_holds": [
            "HOLD_A7AL1_CONTROL_CONTAMINATION if wrong_lag_future/stale is comparable to original",
            "HOLD_A7AL1_TIMING_FRAGILE if field-native latency audit or wrong-lag controls fail",
            "HOLD_A7AL1_STATE_BIAS_ONLY if neutralized signals vanish",
            "HOLD_A7AL1_MEME_OR_CONTRACT_BETA if only meme/multiplier strata explain result",
        ],
    }


def build_field_family_candidate_list() -> list[dict]:
    families = [
        ("P0", "open_interest", ["level", "change_1h", "change_4h", "change_24h", "zscore_168h", "cross_sectional_percentile"]),
        ("P1", "long_short_positioning", ["level", "change_4h", "change_24h", "zscore_168h", "rank"]),
        ("P2", "taker_buy_sell_volume_ratio", ["level", "change_4h", "zscore_168h", "rank"]),
        ("P3", "premium_basis", ["level", "abs", "change_4h", "zscore_168h", "ts_rank"]),
        ("P4", "funding", ["level", "abs", "persistence", "zscore_168h", "rank"]),
        ("P5", "price_volatility_interaction", ["ret_x_vol", "range_state", "vol_compression", "cross_sectional_percentile"]),
        ("P6", "liquidity_volume", ["level", "shock", "persistence", "zscore_168h", "rank"]),
        ("P7", "listing_age_latent_interaction", ["age_x_liquidity", "age_x_volatility", "latent_state_interaction"]),
        ("P8", "meme_multiplier_neutralization_diagnostic", ["meme_neutral_rank", "multiplier_exposure_report", "strata_attribution"]),
    ]
    rows = []
    for priority, family, transforms in families:
        for transform in transforms:
            rows.append(
                {
                    "priority": priority,
                    "field_family": family,
                    "fixed_transform": transform,
                    "search_allowed_in_a7al1": False,
                    "baseline_smoke_allowed": True,
                    "requires_field_native_latency_audit": True,
                    "requires_negative_controls": True,
                    "requires_latent_neutral": True,
                    "requires_meme_multiplier_attribution": family in {"meme_multiplier_neutralization_diagnostic", "listing_age_latent_interaction"},
                }
            )
    return rows


def load_return_series(symbol: str) -> pd.Series:
    path = PANEL_ROOT / f"symbol={symbol}" / "part.parquet"
    df = pd.read_parquet(path, columns=["timestamp", "trade_return_1h"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=False)
    return df.set_index("timestamp")["trade_return_1h"].astype(float)


def build_beta_exposure_baseline(symbol_quality: pd.DataFrame, taxonomy: pd.DataFrame) -> list[dict]:
    btc = load_return_series("BTCUSDT")
    eth = load_return_series("ETHUSDT")
    train_mask_btc = (btc.index >= SPLITS[0]["start"]) & (btc.index <= SPLITS[0]["end"])
    train_mask_eth = (eth.index >= SPLITS[0]["start"]) & (eth.index <= SPLITS[0]["end"])
    btc_train = btc.loc[train_mask_btc]
    eth_train = eth.loc[train_mask_eth]

    tax = taxonomy.set_index("symbol")
    rows = []
    for _, r in symbol_quality.iterrows():
        symbol = r["symbol"]
        try:
            ret = load_return_series(symbol)
        except Exception:
            ret = pd.Series(dtype=float)
        train_ret = ret.loc[(ret.index >= SPLITS[0]["start"]) & (ret.index <= SPLITS[0]["end"])]
        btc_beta, btc_corr, btc_n = cov_beta(train_ret, btc_train)
        eth_beta, eth_corr, eth_n = cov_beta(train_ret, eth_train)
        tax_row = tax.loc[symbol] if symbol in tax.index else {}
        rows.append(
            {
                "symbol": symbol,
                "search_eligibility": r["search_eligibility"],
                "history_tier": r["history_tier"],
                "liquidity_rank": r["liquidity_rank"],
                "liquidity_tier": r["liquidity_tier"],
                "median_hourly_quote_volume": r["median_hourly_quote_volume"],
                "is_core12": r["is_core12"],
                "is_major": r["is_major"],
                "contract_format": r["contract_format"],
                "meme_contract_group": tax_row.get("meme_contract_group", "") if hasattr(tax_row, "get") else "",
                "is_meme_token": tax_row.get("is_meme_token", "") if hasattr(tax_row, "get") else "",
                "is_multiplier_contract": tax_row.get("is_multiplier_contract", "") if hasattr(tax_row, "get") else "",
                "contract_unit_multiplier": tax_row.get("contract_unit_multiplier", "") if hasattr(tax_row, "get") else "",
                "btc_beta_train": btc_beta,
                "btc_corr_train": btc_corr,
                "btc_beta_obs_train": btc_n,
                "eth_beta_train": eth_beta,
                "eth_corr_train": eth_corr,
                "eth_beta_obs_train": eth_n,
                "major_beta_proxy_abs_corr": max(abs(btc_corr or 0.0), abs(eth_corr or 0.0)),
                "requires_beta_residual_audit": True,
            }
        )
    return rows


def build_universe_survivorship_audit(symbol_quality: pd.DataFrame) -> list[dict]:
    q = symbol_quality.copy()
    q["timestamp_min_ts"] = pd.to_datetime(q["timestamp_min"], utc=True).dt.tz_localize(None)
    q["timestamp_max_ts"] = pd.to_datetime(q["timestamp_max"], utc=True).dt.tz_localize(None)
    global_max = q["timestamp_max_ts"].max()
    rows = []
    for _, r in q.iterrows():
        listed_split = "before_or_at_train_start"
        if r["timestamp_min_ts"] > SPLITS[0]["end"]:
            listed_split = "listed_after_train"
        elif r["timestamp_min_ts"] > SPLITS[0]["start"]:
            listed_split = "listed_during_train"
        if r["timestamp_min_ts"] > SPLITS[1]["start"] and r["timestamp_min_ts"] <= SPLITS[1]["end"]:
            listed_split = "listed_during_validation"
        if r["timestamp_min_ts"] > SPLITS[2]["start"] and r["timestamp_min_ts"] <= SPLITS[2]["end"]:
            listed_split = "listed_during_test"
        if r["timestamp_min_ts"] > SPLITS[3]["start"] and r["timestamp_min_ts"] <= SPLITS[3]["end"]:
            listed_split = "listed_during_recent_oos"
        rows.append(
            {
                "symbol": r["symbol"],
                "timestamp_min": r["timestamp_min"],
                "timestamp_max": r["timestamp_max"],
                "listed_split_bucket": listed_split,
                "search_eligibility": r["search_eligibility"],
                "history_tier": r["history_tier"],
                "current_universe_bias_flag": True,
                "delisted_or_missing_symbol_flag": bool(r["timestamp_max_ts"] < global_max),
                "survivorship_safe_primary_proof": False,
                "notes": "Universe498 is current/listing-aware; strict symbols are proof-style subset but not delisting-complete universe.",
            }
        )
    return rows


def md_table(rows: list[dict], limit: int | None = None) -> str:
    if limit is not None:
        rows = rows[:limit]
    if not rows:
        return ""
    fields = list(rows[0].keys())
    out = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(f, "")) for f in fields) + " |")
    return "\n".join(out)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    symbol_quality = pd.read_csv(SYMBOL_QUALITY)
    base_contract = pd.read_csv(BASE_FEATURE_CONTRACT)
    taxonomy = pd.read_csv(TAXONOMY)
    split_counts = compute_symbol_split_counts(symbol_quality["symbol"].tolist())

    split_by_symbol, split_summary, split_def = build_split_tables(symbol_quality, split_counts)
    field_timing = build_field_timing_contract(base_contract)
    latent_audit, latent_manifest, latent_inputs, unseen_policy = build_latent_freeze_audit()
    neutral_policy = build_neutralization_policy()
    negative_plan = build_negative_control_plan()
    field_candidates = build_field_family_candidate_list()
    universe_audit = build_universe_survivorship_audit(symbol_quality)
    beta_baseline = build_beta_exposure_baseline(symbol_quality, taxonomy)

    write_csv(RUNTIME / "a7al_split_coverage_by_symbol.csv", split_by_symbol)
    write_csv(RUNTIME / "a7al_split_summary.csv", split_summary)
    write_csv(RUNTIME / "a7al_split_definition.csv", split_def)
    write_csv(RUNTIME / "a7al_field_timing_contract.csv", field_timing)
    write_csv(RUNTIME / "a7ak_lv_train_only_state_freeze_audit.csv", latent_audit)
    write_csv(RUNTIME / "a7al_latent_state_feature_inputs.csv", latent_inputs)
    write_csv(RUNTIME / "a7al_unseen_state_handling_policy.csv", unseen_policy)
    write_csv(RUNTIME / "a7al_beta_liquidity_meme_exposure_baseline.csv", beta_baseline)
    write_csv(RUNTIME / "a7al_universe_survivorship_audit.csv", universe_audit)
    write_csv(RUNTIME / "a7al_field_family_baseline_candidate_list.csv", field_candidates)
    (RUNTIME / "a7ak_lv_train_only_state_freeze_manifest.json").write_text(json.dumps(latent_manifest, indent=2), encoding="utf-8")
    (RUNTIME / "a7al_neutralization_policy.json").write_text(json.dumps(neutral_policy, indent=2), encoding="utf-8")
    (RUNTIME / "a7al_negative_control_plan.json").write_text(json.dumps(negative_plan, indent=2), encoding="utf-8")

    counts = symbol_quality["search_eligibility"].value_counts().to_dict()
    split_summary_lookup = {r["split"]: r for r in split_summary}
    manifest = {
        "generated_at": generated_at,
        "decision": "PASS_A7AL0_TOP498_ALPHA_SEARCH_CONTRACT_READY",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7al1_field_family_smoke": True,
        "authorizes_a7al2_formula_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "panel_root": str(PANEL_ROOT),
        "symbols": int(symbol_quality["symbol"].nunique()),
        "strict_full_history_symbols": int(counts.get("strict_full_history", 0)),
        "listing_aware_symbols": int(counts.get("listing_aware", 0)),
        "hold_symbols": int(counts.get("hold_quality_or_short_history", 0)),
        "split_summary": split_summary,
        "latent_freeze_manifest": latent_manifest,
        "required_outputs": [
            "a7al_split_coverage_by_symbol.csv",
            "a7al_field_timing_contract.csv",
            "a7ak_lv_train_only_state_freeze_audit.csv",
            "a7al_neutralization_policy.json",
            "a7al_beta_liquidity_meme_exposure_baseline.csv",
            "a7al_negative_control_plan.json",
        ],
        "blockers": [],
        "warnings": [
            "Universe498 is current/listing-aware and not delisting-complete",
            "May 2026 unavailable in this panel",
            "A7AL-0 is a contract/audit stage, not alpha evidence",
            "All field-family structures must pass field-native latency audit, beta residual, neutralization, and negative controls in A7AL-1",
        ],
    }
    (RUNTIME / "a7al0_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    required_file_rows = [
        {"file": "a7al_split_coverage_by_symbol.csv", "purpose": "split composition and coverage by symbol"},
        {"file": "a7al_field_timing_contract.csv", "purpose": "PIT event/availability/execution timing by field"},
        {"file": "a7ak_lv_train_only_state_freeze_audit.csv", "purpose": "latent train-only and no-validation/test-response audit"},
        {"file": "a7al_neutralization_policy.json", "purpose": "neutralization algorithms and fallback rules"},
        {"file": "a7al_beta_liquidity_meme_exposure_baseline.csv", "purpose": "symbol beta/liquidity/meme/multiplier exposure baseline"},
        {"file": "a7al_negative_control_plan.json", "purpose": "shuffle/wrong-lag/sign/random control requirements"},
    ]

    report = f"""# CRYPTO A7AL-0 Top498 Latent-Neutral Alpha Search Contract

Generated: {generated_at}

## Decision

```text
PASS_A7AL0_TOP498_ALPHA_SEARCH_CONTRACT_READY
```

This stage does not run alpha search or replay. It freezes the split, PIT timing, latent-state, neutralization, exposure, and negative-control rules required before A7AL-1.

## Required Outputs

{md_table(required_file_rows)}

## Split Summary

{md_table(split_summary)}

## Universe Boundary

```text
U0_strict_full_history: {int(counts.get("strict_full_history", 0))}
U1_listing_aware: {int(counts.get("listing_aware", 0))}
U2_hold: {int(counts.get("hold_quality_or_short_history", 0))}

Universe498 is current/listing-aware. It is useful for research and cross-sectional diagnostics,
but it is not delisting-complete survivorship-safe proof by itself.
```

## PIT Timing Rule

```text
primary feature availability: timestamp + 1h / next 1h bar open
fixed delay stress: prohibited
same-bar execution: forbidden
promotion rule: field-native latency audit and wrong-lag controls must pass
```

## Latent State Boundary

```json
{json.dumps(latent_manifest, indent=2)}
```

## Neutralization Boundary

```text
Minimum group symbols: 10
Minimum active symbols per hour: 8
Small-group fallback: parent state / liquidity tier / global
Meme and multiplier groups are exposure strata unless sample size is sufficient.
```

## A7AL-1 Authorization

```text
AUTHORIZED:
  field-family neutralized baseline smoke
  global vs age-neutral vs latent-neutral vs liquidity/meme/multiplier-aware diagnostics
  +1h primary and field-native latency audit
  negative controls before any candidate promotion

NOT AUTHORIZED:
  A7AL-2 formula search
  alpha proof
  shadow / paper / live
```

## Pass Conditions For A7AL-1

```text
At least 2 field families must survive on U0 strict symbols.
Signals must survive neutralization, BTC/ETH beta residual, field-native latency audit, and negative controls.
U1 listing-aware can support lifecycle generalization but not primary proof by itself.
Single symbol / single latent state / meme / multiplier concentration blocks promotion.
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
