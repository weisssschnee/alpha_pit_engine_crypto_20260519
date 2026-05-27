from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")
BASE_PANEL_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v1_20260525"
LV1_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_latent_state_features_v1_20260527.parquet"
TAXONOMY = REPO / "runtime" / "a7ak_lv3r_contract_meme_taxonomy_audit" / "a7ak_lv3r_contract_meme_taxonomy.csv"

RUNTIME = REPO / "runtime" / "a7al0g_upper_regime_state_builder"
REPORT = REPO / "reports" / "CRYPTO_A7AL0G_UPPER_REGIME_STATE_BUILDER_20260527.md"
OUTPUT_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_upper_regime_state_v1_20260527.parquet"

TRAIN_SPLIT = "train_2024"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
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


def load_positioning_fields() -> pd.DataFrame:
    cols = [
        "symbol",
        "timestamp",
        "global_long_short_account_ratio_last",
        "top_long_short_account_ratio_last",
        "top_long_short_position_ratio_last",
        "taker_buy_sell_volume_ratio_last",
    ]
    parts = []
    for part in sorted(BASE_PANEL_ROOT.glob("symbol=*/part.parquet")):
        parts.append(pd.read_parquet(part, columns=cols, engine="pyarrow"))
    out = pd.concat(parts, ignore_index=True)
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    return out


def split_label(ts: pd.Series) -> pd.Series:
    out = pd.Series("outside", index=ts.index, dtype="object")
    out[(ts >= pd.Timestamp("2024-01-01", tz="UTC")) & (ts <= pd.Timestamp("2024-12-31 23:00", tz="UTC"))] = "train_2024"
    out[(ts >= pd.Timestamp("2025-01-01", tz="UTC")) & (ts <= pd.Timestamp("2025-06-30 23:00", tz="UTC"))] = "validation_2025H1"
    out[(ts >= pd.Timestamp("2025-07-01", tz="UTC")) & (ts <= pd.Timestamp("2025-12-31 23:00", tz="UTC"))] = "test_2025H2"
    out[(ts >= pd.Timestamp("2026-01-01", tz="UTC")) & (ts <= pd.Timestamp("2026-04-30 23:00", tz="UTC"))] = "recent_oos_2026JanApr"
    return out


def train_thresholds(df: pd.DataFrame, fields: list[str]) -> tuple[pd.DataFrame, dict[str, dict[str, float]]]:
    rows = []
    lookup: dict[str, dict[str, float]] = {}
    train = df[df["split"] == TRAIN_SPLIT]
    for field in fields:
        values = pd.to_numeric(train[field], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        lookup[field] = {}
        for q in [0.2, 0.33, 0.5, 0.66, 0.8]:
            threshold = float(values.quantile(q)) if len(values) else np.nan
            lookup[field][str(q)] = threshold
            rows.append({"field_name": field, "quantile": q, "threshold": threshold, "fit_split": TRAIN_SPLIT, "fit_rows": int(len(values))})
    return pd.DataFrame(rows), lookup


def tri_state(series: pd.Series, lo: float, hi: float, labels: tuple[str, str, str]) -> pd.Series:
    return pd.cut(series, bins=[-np.inf, lo, hi, np.inf], labels=list(labels)).astype("object")


def build_regime_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    lv = pd.read_parquet(
        LV1_PANEL,
        columns=[
            "symbol",
            "timestamp",
            "trade_return_24h",
            "realized_vol_168h",
            "log_quote_volume_168h",
            "open_interest_change_24h",
            "funding_rate_abs_168h",
            "basis_abs_168h",
            "premium_abs_168h",
            "age_bucket_dynamic",
            "is_major",
        ],
        engine="pyarrow",
    )
    lv["timestamp"] = pd.to_datetime(lv["timestamp"], utc=True)
    tax = pd.read_csv(TAXONOMY)[["symbol", "is_meme_token"]]
    lv = lv.merge(tax, on="symbol", how="left")
    lv["is_meme_token"] = lv["is_meme_token"].fillna(False).astype(bool)
    lv["ret_positive"] = pd.to_numeric(lv["trade_return_24h"], errors="coerce") > 0
    lv["age_lt30"] = lv["age_bucket_dynamic"] == "age_lt30d"
    lv["age_lt90"] = lv["age_bucket_dynamic"].isin(["age_lt30d", "age_30_90d"])

    grp = lv.groupby("timestamp", observed=True)
    base = grp.agg(
        active_symbols=("symbol", "nunique"),
        market_ret_24h_median=("trade_return_24h", "median"),
        market_ret_24h_mean=("trade_return_24h", "mean"),
        market_vol_168h_median=("realized_vol_168h", "median"),
        market_breadth_positive=("ret_positive", "mean"),
        market_liquidity_log_median=("log_quote_volume_168h", "median"),
        leverage_oi_change_median=("open_interest_change_24h", "median"),
        funding_abs_median=("funding_rate_abs_168h", "median"),
        basis_abs_median=("basis_abs_168h", "median"),
        premium_abs_median=("premium_abs_168h", "median"),
        listing_age_lt30_share=("age_lt30", "mean"),
        listing_age_lt90_share=("age_lt90", "mean"),
    ).reset_index()

    major = lv[lv["is_major"].astype(bool)].groupby("timestamp", observed=True)["trade_return_24h"].median().rename("major_ret_24h_median")
    alt = lv[~lv["is_major"].astype(bool)].groupby("timestamp", observed=True)["trade_return_24h"].median().rename("alt_ret_24h_median")
    meme = lv[lv["is_meme_token"]].groupby("timestamp", observed=True)["trade_return_24h"].median().rename("meme_ret_24h_median")
    nonmeme = lv[~lv["is_meme_token"]].groupby("timestamp", observed=True)["trade_return_24h"].median().rename("nonmeme_ret_24h_median")
    base = base.merge(major, on="timestamp", how="left").merge(alt, on="timestamp", how="left").merge(meme, on="timestamp", how="left").merge(nonmeme, on="timestamp", how="left")
    base["alt_vs_major_ret_24h"] = base["alt_ret_24h_median"] - base["major_ret_24h_median"]
    base["meme_vs_nonmeme_ret_24h"] = base["meme_ret_24h_median"] - base["nonmeme_ret_24h_median"]

    pos = load_positioning_fields()
    pos_agg = pos.groupby("timestamp", observed=True).agg(
        global_long_short_median=("global_long_short_account_ratio_last", "median"),
        top_long_short_account_median=("top_long_short_account_ratio_last", "median"),
        top_long_short_position_median=("top_long_short_position_ratio_last", "median"),
        taker_buy_sell_ratio_median=("taker_buy_sell_volume_ratio_last", "median"),
    ).reset_index()
    panel = base.merge(pos_agg, on="timestamp", how="left")
    panel["split"] = split_label(panel["timestamp"])

    fields = [
        "market_ret_24h_median",
        "market_vol_168h_median",
        "market_breadth_positive",
        "market_liquidity_log_median",
        "leverage_oi_change_median",
        "funding_abs_median",
        "basis_abs_median",
        "premium_abs_median",
        "global_long_short_median",
        "top_long_short_position_median",
        "meme_vs_nonmeme_ret_24h",
        "listing_age_lt30_share",
        "alt_vs_major_ret_24h",
    ]
    thresholds, lookup = train_thresholds(panel, fields)

    panel["R0_market_trend_state"] = tri_state(panel["market_ret_24h_median"], lookup["market_ret_24h_median"]["0.33"], lookup["market_ret_24h_median"]["0.66"], ("trend_down", "trend_mid", "trend_up"))
    panel["R1_market_volatility_state"] = tri_state(panel["market_vol_168h_median"], lookup["market_vol_168h_median"]["0.33"], lookup["market_vol_168h_median"]["0.66"], ("vol_low", "vol_mid", "vol_high"))
    panel["R2_market_breadth_state"] = tri_state(panel["market_breadth_positive"], lookup["market_breadth_positive"]["0.33"], lookup["market_breadth_positive"]["0.66"], ("breadth_weak", "breadth_mid", "breadth_strong"))
    panel["R3_liquidity_cycle_state"] = tri_state(panel["market_liquidity_log_median"], lookup["market_liquidity_log_median"]["0.33"], lookup["market_liquidity_log_median"]["0.66"], ("liq_contracting", "liq_mid", "liq_expanding"))
    panel["R4_leverage_crowding_state"] = tri_state(panel["leverage_oi_change_median"] + panel["funding_abs_median"].fillna(0), (lookup["leverage_oi_change_median"]["0.33"] + lookup["funding_abs_median"]["0.33"]), (lookup["leverage_oi_change_median"]["0.66"] + lookup["funding_abs_median"]["0.66"]), ("lev_low", "lev_mid", "lev_high"))
    panel["R5_basis_premium_dislocation_state"] = tri_state(panel["basis_abs_median"].fillna(0) + panel["premium_abs_median"].fillna(0), (lookup["basis_abs_median"]["0.33"] + lookup["premium_abs_median"]["0.33"]), (lookup["basis_abs_median"]["0.66"] + lookup["premium_abs_median"]["0.66"]), ("basis_low", "basis_mid", "basis_high"))
    panel["R6_positioning_crowding_state"] = tri_state(panel["top_long_short_position_median"], lookup["top_long_short_position_median"]["0.33"], lookup["top_long_short_position_median"]["0.66"], ("pos_low", "pos_mid", "pos_high"))
    panel["R7_meme_risk_on_state"] = tri_state(panel["meme_vs_nonmeme_ret_24h"], lookup["meme_vs_nonmeme_ret_24h"]["0.33"], lookup["meme_vs_nonmeme_ret_24h"]["0.66"], ("meme_off", "meme_mid", "meme_on"))
    panel["R8_listing_cycle_pressure_state"] = tri_state(panel["listing_age_lt30_share"], lookup["listing_age_lt30_share"]["0.33"], lookup["listing_age_lt30_share"]["0.66"], ("listing_low", "listing_mid", "listing_high"))
    panel["R9_alt_vs_major_dispersion_state"] = tri_state(panel["alt_vs_major_ret_24h"], lookup["alt_vs_major_ret_24h"]["0.33"], lookup["alt_vs_major_ret_24h"]["0.66"], ("alt_lag", "alt_mid", "alt_lead"))
    panel["R10_stress_proxy_state"] = np.select(
        [
            (panel["R1_market_volatility_state"] == "vol_high") & (panel["R2_market_breadth_state"] == "breadth_weak"),
            (panel["R1_market_volatility_state"] == "vol_low") & (panel["R2_market_breadth_state"] == "breadth_strong"),
        ],
        ["stress_high", "stress_low"],
        default="stress_mid",
    )
    return panel, thresholds


def contract_rows() -> list[dict[str, Any]]:
    regimes = [
        ("R0_market_trend", "market_ret_24h_median", "market trend / reversal pressure"),
        ("R1_market_volatility", "market_vol_168h_median", "aggregate volatility state"),
        ("R2_market_breadth", "market_breadth_positive", "cross-sectional breadth"),
        ("R3_liquidity_cycle", "market_liquidity_log_median", "market liquidity cycle"),
        ("R4_leverage_crowding", "leverage_oi_change_median + funding_abs_median", "aggregate leverage/funding crowding"),
        ("R5_basis_premium_dislocation", "basis_abs_median + premium_abs_median", "basis/premium dislocation"),
        ("R6_positioning_crowding", "top_long_short_position_median", "positioning crowding"),
        ("R7_meme_risk_on", "meme_vs_nonmeme_ret_24h", "meme risk-on state"),
        ("R8_listing_cycle_pressure", "listing_age_lt30_share", "listing lifecycle pressure"),
        ("R9_alt_vs_major_dispersion", "alt_vs_major_ret_24h", "alt vs major relative state"),
        ("R10_stress_proxy", "volatility high + breadth weak", "market stress proxy"),
    ]
    return [
        {
            "regime_id": regime_id,
            "input_fields": fields,
            "economic_role": role,
            "fit_rule": "thresholds fit on train_2024 only",
            "apply_rule": "validation/test/recent apply frozen thresholds",
            "may_used": False,
            "allowed_for_rank": False,
            "allowed_for_regime": True,
            "allowed_for_search_interaction": True,
        }
        for regime_id, fields, role in regimes
    ]


def coverage_rows(panel: pd.DataFrame) -> list[dict[str, Any]]:
    states = [c for c in panel.columns if c.startswith("R") and c.endswith("_state")]
    rows = []
    for split, g in panel.groupby("split", observed=True):
        if split == "outside":
            continue
        row: dict[str, Any] = {"split": split, "timestamps": int(len(g)), "active_symbols_median": float(g["active_symbols"].median())}
        for state in states:
            row[f"{state}_states"] = int(g[state].nunique(dropna=True))
            row[f"{state}_missing"] = int(g[state].isna().sum())
        rows.append(row)
    return rows


def transition_rows(panel: pd.DataFrame) -> list[dict[str, Any]]:
    states = [c for c in panel.columns if c.startswith("R") and c.endswith("_state")]
    rows = []
    ordered = panel.sort_values("timestamp")
    for state in states:
        prev = ordered[state].shift(1)
        changed = (ordered[state] != prev) & prev.notna() & ordered[state].notna()
        rows.append(
            {
                "regime_state": state,
                "transitions": int(changed.sum()),
                "transition_rate": float(changed.mean()),
                "distinct_states": int(ordered[state].nunique(dropna=True)),
            }
        )
    return rows


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    generated_at = utc_now()
    panel, thresholds = build_regime_panel()
    panel.to_parquet(OUTPUT_PANEL, engine="pyarrow", index=False)

    contract = contract_rows()
    coverage = coverage_rows(panel)
    transitions = transition_rows(panel)
    thresholds.to_csv(RUNTIME / "a7al0g_train_only_thresholds.csv", index=False)
    write_csv(RUNTIME / "a7al0g_regime_state_contract.csv", contract)
    write_csv(RUNTIME / "a7al0g_regime_coverage_by_split.csv", coverage)
    write_csv(RUNTIME / "a7al0g_regime_transition_matrix.csv", transitions)

    blockers = []
    if int((thresholds["fit_rows"] == 0).sum()):
        blockers.append("empty_train_threshold_fit")
    if panel.empty:
        blockers.append("empty_regime_panel")
    manifest = {
        "generated_at": generated_at,
        "decision": "PASS_A7AL0G_UPPER_REGIME_STATE_BUILDER" if not blockers else "HOLD_A7AL0G_UPPER_REGIME_BLOCKED",
        "output_panel": str(OUTPUT_PANEL),
        "rows": int(len(panel)),
        "columns": int(len(panel.columns)),
        "regime_states": len([c for c in panel.columns if c.startswith("R") and c.endswith("_state")]),
        "executes_search": False,
        "executes_replay": False,
        "train_only_thresholds": True,
        "may_used": False,
        "authorizes_a7al0p_pretrain_gate": not blockers,
        "authorizes_a7al1_baseline": False,
        "blockers": blockers,
    }
    (RUNTIME / "a7al0g_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = f"""# CRYPTO A7AL-0G Upper Regime State Builder

Generated: {generated_at}

## Decision

```text
{manifest["decision"]}
```

Upper regime states are derived from observable top498 panel features. Thresholds are train-only and then frozen.

## Summary

```json
{json.dumps(manifest, indent=2)}
```

## Regime Contract

{md_table(contract)}

## Coverage By Split

{md_table(coverage)}

## Transition Audit

{md_table(transitions)}

## Boundary

```text
AUTHORIZED NEXT:
  A7AL-0P pre-train readiness gate

NOT AUTHORIZED:
  A7AL-1 baseline replay
  formula search
  alpha proof / shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
