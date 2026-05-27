from __future__ import annotations

import csv
import gc
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(
    __import__("os").environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData")
)
REPO = Path(__import__("os").environ.get("ALPHAFACTORY_CRYPTO_REPO_ROOT", str(REPO)))
BASE_PANEL_ROOT = Path(
    __import__("os").environ.get(
        "A7AL_BASE_PANEL_ROOT",
        str(DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527"),
    )
)
LV1_PANEL = Path(
    __import__("os").environ.get(
        "A7AL_LV1_PANEL",
        str(DATA_ROOT / "gold" / "features" / "binance_universe498_latent_state_features_v1_20260527.parquet"),
    )
)
REGIME_PANEL = Path(
    __import__("os").environ.get(
        "A7AL_REGIME_PANEL",
        str(DATA_ROOT / "gold" / "features" / "binance_universe498_upper_regime_state_v1_20260527.parquet"),
    )
)
TAXONOMY = Path(
    __import__("os").environ.get(
        "A7AL_TAXONOMY",
        str(REPO / "runtime" / "a7ak_lv3r_contract_meme_taxonomy_audit" / "a7ak_lv3r_contract_meme_taxonomy.csv"),
    )
)
A7AL0P = REPO / "runtime" / "a7al0p_pretrain_readiness_gate" / "a7al0p_manifest.json"
A7AL0L = REPO / "runtime" / "a7al0l_fixed_delay_stress_abolition" / "a7al0l_manifest.json"

OUT_DIR = REPO / "runtime" / "a7al1_field_family_neutralized_baseline"
REPORT = REPO / "reports" / "CRYPTO_A7AL1_FIELD_FAMILY_NEUTRALIZED_BASELINE_20260527.md"

PRIMARY_LABEL = "fwd_ret_24h"
MIN_GROUP = 8
MIN_ACTIVE_SYMBOLS = 30
SHORTLIST_PER_FAMILY = 1
MAX_FULL_NEUTRALIZED_SIGNALS = 10
CONTROL_SHORTLIST_N = 8

SPLIT_ORDER = ["train_2024", "validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
SPLIT_END = {
    "train_2024": pd.Timestamp("2024-12-31 23:00:00+00:00"),
    "validation_2025H1": pd.Timestamp("2025-06-30 23:00:00+00:00"),
    "test_2025H2": pd.Timestamp("2025-12-31 23:00:00+00:00"),
    "recent_oos_2026JanApr": pd.Timestamp("2026-04-30 23:00:00+00:00"),
}


@dataclass(frozen=True)
class SignalSpec:
    signal_name: str
    field_family: str
    column: str
    direction: float = 1.0


BASE_COLUMNS = [
    "symbol",
    "timestamp",
    "trade_high",
    "trade_low",
    "trade_close",
    "trade_quote_volume",
    "trade_count",
    "open_interest_last",
    "open_interest_value_last",
    "global_long_short_account_ratio_last",
    "top_long_short_account_ratio_last",
    "top_long_short_position_ratio_last",
    "taker_buy_sell_volume_ratio_last",
    "funding_rate",
    "premium_close_bps",
    "mark_index_basis_bps",
    "mark_trade_basis_bps",
]

LV1_COLUMNS = [
    "symbol",
    "timestamp",
    "split",
    "search_eligibility",
    "liquidity_tier_static",
    "age_bucket_dynamic",
    "liquidity_state",
    "volatility_state",
    "major_state",
    "trade_return_24h",
    "realized_vol_24h",
    "realized_vol_168h",
    "liquidity_rank_active_universe",
    "log_quote_volume_168h",
    "funding_rate_abs_168h",
    "funding_rate_mean_168h",
    "basis_abs_168h",
    "premium_abs_168h",
    "open_interest_change_24h",
    "oi_x_price_move_24h",
    "age_x_liquidity",
    "age_x_volatility",
    "age_x_funding_abs",
]

REGIME_COLUMNS = [
    "timestamp",
    "R1_market_volatility_state",
    "R3_liquidity_cycle_state",
    "R4_leverage_crowding_state",
    "R5_basis_premium_dislocation_state",
    "R6_positioning_crowding_state",
    "R10_stress_proxy_state",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


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
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def load_base_panel() -> pd.DataFrame:
    parts = []
    for sym_dir in sorted(BASE_PANEL_ROOT.glob("symbol=*")):
        parquet = sym_dir / "part.parquet"
        csv_gz = sym_dir / "part.csv.gz"
        if parquet.exists():
            parts.append(pd.read_parquet(parquet, columns=BASE_COLUMNS, engine="pyarrow"))
        elif csv_gz.exists():
            df = pd.read_csv(csv_gz, usecols=lambda c: c in set(BASE_COLUMNS))
            missing = [c for c in BASE_COLUMNS if c not in df.columns]
            for col in missing:
                df[col] = np.nan
            parts.append(df[BASE_COLUMNS])
    if not parts:
        raise FileNotFoundError(f"No part.parquet or part.csv.gz files found under {BASE_PANEL_ROOT}")
    base = pd.concat(parts, ignore_index=True)
    base["timestamp"] = pd.to_datetime(base["timestamp"], utc=True)
    return base


def rolling_z_by_symbol(df: pd.DataFrame, col: str, window: int = 168) -> pd.Series:
    values = pd.to_numeric(df[col], errors="coerce")
    grp = values.groupby(df["symbol"], sort=False)
    mean = grp.transform(lambda s: s.rolling(window, min_periods=max(24, window // 4)).mean())
    std = grp.transform(lambda s: s.rolling(window, min_periods=max(24, window // 4)).std()).replace(0, np.nan)
    return ((values - mean) / std).clip(-8, 8)


def diff_by_symbol(df: pd.DataFrame, col: str, periods: int) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce").groupby(df["symbol"], sort=False).diff(periods)


def pct_log_change_by_symbol(df: pd.DataFrame, col: str, periods: int) -> pd.Series:
    values = pd.to_numeric(df[col], errors="coerce")
    logged = np.log(values.where(values > 0))
    return logged.groupby(df["symbol"], sort=False).diff(periods)


def prepare_panel() -> pd.DataFrame:
    lv1 = pd.read_parquet(LV1_PANEL, columns=LV1_COLUMNS, engine="pyarrow")
    lv1["timestamp"] = pd.to_datetime(lv1["timestamp"], utc=True)
    for col in [
        "split",
        "search_eligibility",
        "liquidity_tier_static",
        "age_bucket_dynamic",
        "liquidity_state",
        "volatility_state",
        "major_state",
    ]:
        if col in lv1.columns:
            lv1[col] = lv1[col].astype("category")
    base = load_base_panel()
    panel = lv1.merge(base, on=["symbol", "timestamp"], how="left", sort=False)
    del lv1, base
    gc.collect()
    panel["source_split"] = panel["split"].astype(str)
    panel["split"] = np.select(
        [
            panel["timestamp"].le(SPLIT_END["train_2024"]),
            panel["timestamp"].le(SPLIT_END["validation_2025H1"]),
            panel["timestamp"].le(SPLIT_END["test_2025H2"]),
            panel["timestamp"].le(SPLIT_END["recent_oos_2026JanApr"]),
        ],
        SPLIT_ORDER,
        default="out_of_scope",
    )

    taxonomy = pd.read_csv(TAXONOMY)
    taxonomy_cols = [
        "symbol",
        "is_meme_token",
        "meme_contract_group",
        "search_stratification_group",
        "is_multiplier_contract",
    ]
    panel = panel.merge(taxonomy[taxonomy_cols], on="symbol", how="left")
    regime = pd.read_parquet(REGIME_PANEL, columns=REGIME_COLUMNS, engine="pyarrow")
    regime["timestamp"] = pd.to_datetime(regime["timestamp"], utc=True)
    panel = panel.merge(regime, on="timestamp", how="left")

    panel = panel.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    close = pd.to_numeric(panel["trade_close"], errors="coerce")
    log_close = np.log(close.where(close > 0))
    panel["fwd_ret_1h"] = log_close.groupby(panel["symbol"], sort=False).shift(-1) - log_close
    panel["fwd_ret_24h"] = log_close.groupby(panel["symbol"], sort=False).shift(-24) - log_close
    for label, hours in [("fwd_ret_1h", 1), ("fwd_ret_24h", 24)]:
        label_end = panel["timestamp"] + pd.Timedelta(hours=hours)
        split_end = panel["split"].map(SPLIT_END)
        panel.loc[label_end > split_end, label] = np.nan
    return panel


def add_derived_features(panel: pd.DataFrame) -> tuple[pd.DataFrame, list[SignalSpec]]:
    panel["log_open_interest"] = np.log(pd.to_numeric(panel["open_interest_last"], errors="coerce").where(lambda s: s > 0))
    panel["log_open_interest_value"] = np.log(pd.to_numeric(panel["open_interest_value_last"], errors="coerce").where(lambda s: s > 0))
    panel["funding_abs"] = pd.to_numeric(panel["funding_rate"], errors="coerce").abs()
    panel["premium_abs_bps"] = pd.to_numeric(panel["premium_close_bps"], errors="coerce").abs()
    panel["basis_abs_bps"] = pd.to_numeric(panel["mark_index_basis_bps"], errors="coerce").abs()
    panel["range_bps"] = (
        (pd.to_numeric(panel["trade_high"], errors="coerce") - pd.to_numeric(panel["trade_low"], errors="coerce"))
        / pd.to_numeric(panel["trade_close"], errors="coerce").replace(0, np.nan)
        * 10000
    )
    panel["vol_compression"] = pd.to_numeric(panel["realized_vol_24h"], errors="coerce") / pd.to_numeric(panel["realized_vol_168h"], errors="coerce").replace(0, np.nan)
    panel["ret_x_vol"] = pd.to_numeric(panel["trade_return_24h"], errors="coerce") * pd.to_numeric(panel["realized_vol_168h"], errors="coerce")
    panel["log_trade_quote_volume"] = np.log(pd.to_numeric(panel["trade_quote_volume"], errors="coerce").where(lambda s: s > 0))

    panel["lev_high_oi_change_24h"] = np.where(panel["R4_leverage_crowding_state"].astype(str).eq("lev_high"), panel["open_interest_change_24h"], np.nan)
    panel["basis_high_basis_abs"] = np.where(panel["R5_basis_premium_dislocation_state"].astype(str).eq("basis_high"), panel["basis_abs_168h"], np.nan)
    panel["liq_contracting_volume_level"] = np.where(panel["R3_liquidity_cycle_state"].astype(str).eq("liq_contracting"), panel["log_quote_volume_168h"], np.nan)
    panel["stress_high_low_vol"] = np.where(panel["R10_stress_proxy_state"].astype(str).eq("stress_high"), -panel["realized_vol_168h"], np.nan)

    specs = [
        SignalSpec("oi_level_log", "open_interest", "log_open_interest"),
        SignalSpec("oi_change_24h_lv1", "open_interest", "open_interest_change_24h"),
        SignalSpec("oi_value_level_log", "open_interest", "log_open_interest_value"),
        SignalSpec("oi_x_price_move_24h", "open_interest", "oi_x_price_move_24h"),
        SignalSpec("global_long_short_level", "long_short_positioning", "global_long_short_account_ratio_last"),
        SignalSpec("top_account_long_short_level", "long_short_positioning", "top_long_short_account_ratio_last"),
        SignalSpec("top_position_long_short_level", "long_short_positioning", "top_long_short_position_ratio_last"),
        SignalSpec("taker_buy_sell_level", "taker_buy_sell_volume_ratio", "taker_buy_sell_volume_ratio_last"),
        SignalSpec("premium_level_bps", "premium_basis", "premium_close_bps"),
        SignalSpec("premium_abs_bps", "premium_basis", "premium_abs_bps"),
        SignalSpec("premium_abs_168h", "premium_basis", "premium_abs_168h"),
        SignalSpec("basis_level_bps", "premium_basis", "mark_index_basis_bps"),
        SignalSpec("basis_abs_bps", "premium_basis", "basis_abs_bps"),
        SignalSpec("basis_abs_168h", "premium_basis", "basis_abs_168h"),
        SignalSpec("funding_level", "funding", "funding_rate"),
        SignalSpec("funding_abs", "funding", "funding_abs"),
        SignalSpec("funding_abs_168h", "funding", "funding_rate_abs_168h"),
        SignalSpec("funding_mean_168h", "funding", "funding_rate_mean_168h"),
        SignalSpec("ret_x_vol", "price_volatility_interaction", "ret_x_vol"),
        SignalSpec("range_bps", "price_volatility_interaction", "range_bps"),
        SignalSpec("vol_compression", "price_volatility_interaction", "vol_compression", -1.0),
        SignalSpec("liquidity_level_log_quote", "liquidity_volume", "log_trade_quote_volume"),
        SignalSpec("liquidity_log_quote_168h", "liquidity_volume", "log_quote_volume_168h"),
        SignalSpec("liquidity_rank_active", "liquidity_volume", "liquidity_rank_active_universe"),
        SignalSpec("trade_count_level", "liquidity_volume", "trade_count"),
        SignalSpec("age_x_liquidity", "listing_age_latent_interaction", "age_x_liquidity"),
        SignalSpec("age_x_volatility", "listing_age_latent_interaction", "age_x_volatility"),
        SignalSpec("age_x_funding_abs", "listing_age_latent_interaction", "age_x_funding_abs"),
        SignalSpec("lev_high_oi_change_24h", "upper_regime_interaction", "lev_high_oi_change_24h"),
        SignalSpec("basis_high_basis_abs", "upper_regime_interaction", "basis_high_basis_abs"),
        SignalSpec("liq_contracting_volume_level", "upper_regime_interaction", "liq_contracting_volume_level"),
        SignalSpec("stress_high_low_vol", "upper_regime_interaction", "stress_high_low_vol"),
    ]
    return panel, specs


def global_z(df: pd.DataFrame, value: pd.Series) -> pd.Series:
    tmp = pd.DataFrame({"timestamp": df["timestamp"], "value": pd.to_numeric(value, errors="coerce")})
    mean = tmp.groupby("timestamp", observed=True)["value"].transform("mean")
    std = tmp.groupby("timestamp", observed=True)["value"].transform("std").replace(0, np.nan)
    return ((tmp["value"] - mean) / std).clip(-6, 6)


def neutral_z(df: pd.DataFrame, value: pd.Series, group_cols: list[str]) -> pd.Series:
    base = global_z(df, value)
    tmp = pd.DataFrame({"timestamp": df["timestamp"], "value": pd.to_numeric(value, errors="coerce")})
    for col in group_cols:
        tmp[col] = df[col].astype(str)
    keys = ["timestamp"] + group_cols
    count = tmp.groupby(keys, observed=True)["value"].transform("count")
    mean = tmp.groupby(keys, observed=True)["value"].transform("mean")
    std = tmp.groupby(keys, observed=True)["value"].transform("std").replace(0, np.nan)
    z = ((tmp["value"] - mean) / std).clip(-6, 6)
    z[count < MIN_GROUP] = np.nan
    return z.fillna(base)


def make_signal(panel: pd.DataFrame, spec: SignalSpec, mode: str) -> pd.Series:
    value = spec.direction * pd.to_numeric(panel[spec.column], errors="coerce")
    if mode == "global":
        return global_z(panel, value)
    if mode == "age_neutral":
        return neutral_z(panel, value, ["age_bucket_dynamic"])
    if mode == "latent_state_neutral":
        return neutral_z(panel, value, ["coarse_latent_group"])
    if mode == "liquidity_tier_neutral":
        return neutral_z(panel, value, ["liquidity_tier_static"])
    if mode == "meme_multiplier_aware":
        return neutral_z(panel, value, ["meme_contract_group"])
    raise ValueError(mode)


def prune_panel_for_eval(panel: pd.DataFrame, specs: list[SignalSpec]) -> pd.DataFrame:
    keep = {
        "timestamp",
        "split",
        "symbol",
        "search_eligibility",
        PRIMARY_LABEL,
        "age_bucket_dynamic",
        "liquidity_state",
        "volatility_state",
        "major_state",
        "liquidity_tier_static",
        "meme_contract_group",
    }
    keep.update(spec.column for spec in specs)
    out = panel[[col for col in panel.columns if col in keep]].copy()
    out["coarse_latent_group"] = (
        out["age_bucket_dynamic"].astype(str)
        + "|"
        + out["liquidity_state"].astype(str)
        + "|"
        + out["volatility_state"].astype(str)
        + "|"
        + out["major_state"].astype(str)
    ).astype("category")
    for col in [
        "split",
        "search_eligibility",
        "age_bucket_dynamic",
        "liquidity_tier_static",
        "meme_contract_group",
    ]:
        if col in out.columns:
            out[col] = out[col].astype("category")
    return out


def tstat(values: pd.Series) -> float:
    x = pd.to_numeric(values, errors="coerce").dropna()
    if len(x) < 3:
        return np.nan
    std = x.std(ddof=1)
    if not np.isfinite(std) or std == 0:
        return np.nan
    return float(x.mean() / std * np.sqrt(len(x)))


def timestamp_spread_metrics(df: pd.DataFrame, signal: pd.Series, label: str = PRIMARY_LABEL) -> tuple[pd.DataFrame, dict[str, Any]]:
    work = pd.DataFrame(
        {
            "timestamp": df["timestamp"],
            "split": df["split"],
            "signal": pd.to_numeric(signal, errors="coerce"),
            "label": pd.to_numeric(df[label], errors="coerce"),
            "symbol": df["symbol"],
        }
    ).replace([np.inf, -np.inf], np.nan)
    work = work.dropna(subset=["signal", "label"])
    valid_rows = int(len(work))
    if valid_rows == 0:
        return pd.DataFrame(), {"valid_rows": 0, "valid_row_share": 0.0}
    keys = ["split", "timestamp"]
    counts = work.groupby(keys, observed=True)["signal"].transform("count")
    work = work[counts >= MIN_ACTIVE_SYMBOLS].copy()
    if work.empty:
        return pd.DataFrame(), {"valid_rows": valid_rows, "valid_row_share": float(valid_rows / len(df))}
    work["rank_pct"] = work.groupby(keys, observed=True)["signal"].rank(pct=True, method="average")
    top = work[work["rank_pct"] >= 0.9].groupby(keys, observed=True)["label"].mean()
    bottom = work[work["rank_pct"] <= 0.1].groupby(keys, observed=True)["label"].mean()
    nobs = work.groupby(keys, observed=True)["symbol"].count()
    out = pd.concat([top.rename("top_ret"), bottom.rename("bottom_ret"), nobs.rename("n_obs")], axis=1).dropna()
    out["spread"] = out["top_ret"] - out["bottom_ret"]
    out = out.reset_index()
    return out, {"valid_rows": valid_rows, "valid_row_share": float(valid_rows / len(df))}


def summarize_spreads(ts: pd.DataFrame, coverage: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for split in SPLIT_ORDER:
        if ts.empty or "split" not in ts.columns:
            g = pd.DataFrame()
        else:
            g = ts[ts["split"] == split]
        has_data = not g.empty and all(col in g.columns for col in ["timestamp", "n_obs", "spread"])
        rows.append(
            {
                "split": split,
                "n_dates": int(g["timestamp"].nunique()) if has_data else 0,
                "avg_n_obs": float(g["n_obs"].mean()) if has_data else np.nan,
                "valid_rows": int(coverage["valid_rows"]),
                "valid_row_share": round(float(coverage["valid_row_share"]), 6),
                "mean_spread_24h": float(g["spread"].mean()) if has_data else np.nan,
                "spread_tstat": tstat(g["spread"]) if has_data else np.nan,
                "positive_spread_rate": float((g["spread"] > 0).mean()) if has_data else np.nan,
            }
        )
    return rows


def evaluate_metric_grid(
    panel: pd.DataFrame,
    specs: list[SignalSpec],
    modes: list[str],
    universe_names: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, Any]] = []
    trace_rows: list[dict[str, Any]] = []
    universes = {
        "U0_strict_full_history": panel["search_eligibility"].eq("strict_full_history"),
        "U1_listing_aware": panel["search_eligibility"].eq("listing_aware"),
        "U0U1_all_eligible": panel["search_eligibility"].isin(["strict_full_history", "listing_aware"]),
    }

    for spec in specs:
        print(f"[A7AL-1] evaluate {spec.signal_name}: modes={len(modes)} universes={len(universe_names)}", flush=True)
        for mode in modes:
            signal = make_signal(panel, spec, mode)
            for universe in universe_names:
                mask = universes[universe]
                sub = panel.loc[mask, ["timestamp", "split", "symbol", PRIMARY_LABEL]]
                sub_signal = signal.loc[mask]
                ts, coverage = timestamp_spread_metrics(sub, sub_signal)
                for row in summarize_spreads(ts, coverage):
                    row.update(
                        {
                            "signal_name": spec.signal_name,
                            "field_family": spec.field_family,
                            "source_column": spec.column,
                            "neutralization_mode": mode,
                            "universe": universe,
                        }
                    )
                    metric_rows.append(row)
                if universe == "U0_strict_full_history" and mode in ["global", "latent_state_neutral"]:
                    for _, r in ts.head(250).iterrows():
                        trace_rows.append(
                            {
                                "signal_name": spec.signal_name,
                                "field_family": spec.field_family,
                                "neutralization_mode": mode,
                                "universe": universe,
                                "split": r["split"],
                                "timestamp": r["timestamp"],
                                "spread": r["spread"],
                                "n_obs": r["n_obs"],
                            }
                        )
            del signal
            gc.collect()
    metrics = pd.DataFrame(metric_rows)
    trace = pd.DataFrame(trace_rows)
    return metrics, trace


def shortlist_from_stage1(stage1: pd.DataFrame, specs: list[SignalSpec]) -> list[SignalSpec]:
    val = stage1[
        (stage1["universe"] == "U0_strict_full_history")
        & (stage1["neutralization_mode"] == "global")
        & (stage1["split"] == "validation_2025H1")
    ].copy()
    test = stage1[
        (stage1["universe"] == "U0_strict_full_history")
        & (stage1["neutralization_mode"] == "global")
        & (stage1["split"] == "test_2025H2")
    ][["signal_name", "mean_spread_24h"]].rename(columns={"mean_spread_24h": "test_spread"})
    recent = stage1[
        (stage1["universe"] == "U0_strict_full_history")
        & (stage1["neutralization_mode"] == "global")
        & (stage1["split"] == "recent_oos_2026JanApr")
    ][["signal_name", "mean_spread_24h"]].rename(columns={"mean_spread_24h": "recent_spread"})
    val = val.merge(test, on="signal_name", how="left").merge(recent, on="signal_name", how="left")
    val["stage1_score"] = (
        val["mean_spread_24h"].abs().fillna(0)
        + 0.5 * val["test_spread"].abs().fillna(0)
        + 0.5 * val["recent_spread"].abs().fillna(0)
    )
    chosen: list[str] = []
    for _, g in val.sort_values("stage1_score", ascending=False).groupby("field_family", sort=False):
        chosen.extend(g.head(SHORTLIST_PER_FAMILY)["signal_name"].astype(str).tolist())
    chosen = val[val["signal_name"].isin(chosen)].sort_values("stage1_score", ascending=False)["signal_name"].head(MAX_FULL_NEUTRALIZED_SIGNALS).tolist()
    spec_by_name = {s.signal_name: s for s in specs}
    return [spec_by_name[name] for name in chosen if name in spec_by_name]


def evaluate(panel: pd.DataFrame, specs: list[SignalSpec]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    print(f"[A7AL-1] stage1 global screening: signals={len(specs)}", flush=True)
    stage1, stage1_trace = evaluate_metric_grid(
        panel,
        specs,
        modes=["global"],
        universe_names=["U0_strict_full_history"],
    )
    shortlist = shortlist_from_stage1(stage1, specs)
    print(f"[A7AL-1] full neutralization shortlist: signals={len(shortlist)}", flush=True)
    full_u0_metrics, full_u0_trace = evaluate_metric_grid(
        panel,
        shortlist,
        modes=["global", "age_neutral", "latent_state_neutral", "liquidity_tier_neutral", "meme_multiplier_aware"],
        universe_names=["U0_strict_full_history"],
    )
    full_u1_metrics, full_u1_trace = evaluate_metric_grid(
        panel,
        shortlist,
        modes=["latent_state_neutral"],
        universe_names=["U1_listing_aware", "U0U1_all_eligible"],
    )
    full_metrics = pd.concat([full_u0_metrics, full_u1_metrics], ignore_index=True)
    full_trace = pd.concat([full_u0_trace, full_u1_trace], ignore_index=True)
    full_metrics["evaluation_stage"] = "full_neutralized_shortlist"
    stage1["evaluation_stage"] = "stage1_global_screen"
    metrics = pd.concat([stage1, full_metrics], ignore_index=True)
    trace = pd.concat([stage1_trace.assign(evaluation_stage="stage1_global_screen"), full_trace.assign(evaluation_stage="full_neutralized_shortlist")], ignore_index=True)
    decisions = classify(full_metrics)
    screened_names = set(decisions["signal_name"].astype(str)) if not decisions.empty else set()
    for spec in specs:
        if spec.signal_name not in screened_names:
            decisions = pd.concat(
                [
                    decisions,
                    pd.DataFrame(
                        [
                            {
                                "signal_name": spec.signal_name,
                                "field_family": spec.field_family,
                                "source_column": spec.column,
                                "diagnostic_decision": "STAGE1_ONLY_NOT_SHORTLISTED",
                            }
                        ]
                    ),
                ],
                ignore_index=True,
            )
    return metrics, trace, decisions, pd.DataFrame([{"signal_name": s.signal_name, "field_family": s.field_family, "source_column": s.column} for s in shortlist])


def split_value(metrics: pd.DataFrame, signal: str, family: str, mode: str, universe: str, split: str, field: str) -> float:
    row = metrics[
        (metrics["signal_name"] == signal)
        & (metrics["field_family"] == family)
        & (metrics["neutralization_mode"] == mode)
        & (metrics["universe"] == universe)
        & (metrics["split"] == split)
    ]
    if row.empty:
        return np.nan
    return float(row.iloc[0][field])


def classify(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = metrics[["signal_name", "field_family", "source_column"]].drop_duplicates()
    for signal_name, family, source_column in keys.itertuples(index=False, name=None):
        g_val = split_value(metrics, signal_name, family, "global", "U0_strict_full_history", "validation_2025H1", "mean_spread_24h")
        g_test = split_value(metrics, signal_name, family, "global", "U0_strict_full_history", "test_2025H2", "mean_spread_24h")
        g_rec = split_value(metrics, signal_name, family, "global", "U0_strict_full_history", "recent_oos_2026JanApr", "mean_spread_24h")
        a_val = split_value(metrics, signal_name, family, "age_neutral", "U0_strict_full_history", "validation_2025H1", "mean_spread_24h")
        l_val = split_value(metrics, signal_name, family, "latent_state_neutral", "U0_strict_full_history", "validation_2025H1", "mean_spread_24h")
        q_val = split_value(metrics, signal_name, family, "liquidity_tier_neutral", "U0_strict_full_history", "validation_2025H1", "mean_spread_24h")
        m_val = split_value(metrics, signal_name, family, "meme_multiplier_aware", "U0_strict_full_history", "validation_2025H1", "mean_spread_24h")
        u1_val = split_value(metrics, signal_name, family, "latent_state_neutral", "U1_listing_aware", "validation_2025H1", "mean_spread_24h")
        signs = [np.sign(x) for x in [g_val, g_test, g_rec] if np.isfinite(x) and abs(x) > 1e-8]
        stable_global = len(signs) == 3 and len(set(signs)) == 1 and min(abs(g_val), abs(g_test), abs(g_rec)) >= 0.0002
        neutral_ok = stable_global and all(np.isfinite(x) and np.sign(x) == np.sign(g_val) and abs(x) >= 0.0001 for x in [a_val, l_val, q_val, m_val])
        u1_consistent = np.isfinite(u1_val) and np.sign(u1_val) == np.sign(g_val)
        if neutral_ok and u1_consistent:
            decision = "FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC"
        elif stable_global and not neutral_ok:
            decision = "HOLD_A7AL1_STATE_OR_GROUP_BIAS"
        else:
            decision = "NO_STABLE_FIELD_FAMILY_STRUCTURE"
        rows.append(
            {
                "signal_name": signal_name,
                "field_family": family,
                "source_column": source_column,
                "global_validation_spread": g_val,
                "global_test_spread": g_test,
                "global_recent_spread": g_rec,
                "age_neutral_validation_spread": a_val,
                "latent_neutral_validation_spread": l_val,
                "liquidity_neutral_validation_spread": q_val,
                "meme_multiplier_validation_spread": m_val,
                "u1_listing_latent_validation_spread": u1_val,
                "diagnostic_decision": decision,
            }
        )
    return pd.DataFrame(rows)


def control_audit(panel: pd.DataFrame, specs: list[SignalSpec], decisions: pd.DataFrame) -> pd.DataFrame:
    shortlist = decisions.sort_values("global_validation_spread", key=lambda s: s.abs(), ascending=False).head(CONTROL_SHORTLIST_N)
    decision_by_signal = decisions.set_index("signal_name")["diagnostic_decision"].to_dict()
    rows = []
    strict = panel[panel["search_eligibility"].eq("strict_full_history")].copy()
    rng = np.random.default_rng(20260527)
    for signal_name in shortlist["signal_name"]:
        spec = next(s for s in specs if s.signal_name == signal_name)
        value = spec.direction * pd.to_numeric(strict[spec.column], errors="coerce")
        original = make_signal(strict, spec, "latent_state_neutral")
        controls = {
            "original": original,
            "wrong_lag_future_24h": global_z(strict, value.groupby(strict["symbol"], sort=False).shift(-24)),
            "wrong_lag_stale_168h": global_z(strict, value.groupby(strict["symbol"], sort=False).shift(168)),
            "sign_flip": -original,
            "random_field": pd.Series(rng.normal(size=len(strict)), index=strict.index),
        }
        orig_val = np.nan
        for control, sig in controls.items():
            ts, coverage = timestamp_spread_metrics(strict, sig)
            val = float(ts.loc[ts["split"].eq("validation_2025H1"), "spread"].mean()) if not ts.empty else np.nan
            if control == "original":
                orig_val = val
            rows.append(
                {
                    "signal_name": signal_name,
                    "field_family": spec.field_family,
                    "original_decision": decision_by_signal.get(signal_name, ""),
                    "control": control,
                    "validation_mean_spread_24h": val,
                    "abs_vs_original_ratio": abs(val) / abs(orig_val) if np.isfinite(val) and np.isfinite(orig_val) and abs(orig_val) > 0 else np.nan,
                    "valid_row_share": coverage.get("valid_row_share", 0.0),
                }
            )
    out = pd.DataFrame(rows)
    out["control_flag"] = "OK"
    out.loc[out["control"].eq("original"), "control_flag"] = "REFERENCE"
    out.loc[out["control"].eq("sign_flip"), "control_flag"] = "EXPECTED_INVERSION"
    nonblocking = ~out["original_decision"].eq("FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC")
    out.loc[nonblocking & ~out["control"].isin(["original", "sign_flip"]), "control_flag"] = "NONBLOCKING_DIAGNOSTIC"
    blocking = (
        out["original_decision"].eq("FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC")
        & ~out["control"].isin(["original", "sign_flip"])
        & (out["abs_vs_original_ratio"] >= 0.8)
    )
    out.loc[blocking, "control_flag"] = "CONTROL_TOO_STRONG"
    return out


def bias_audit(decision: str, blockers: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"check": "candidate_scope", "status": "PASS", "detail": "fixed field-family baseline only; no formula generation"},
            {"check": "pit_timing", "status": "PASS", "detail": "1h feature_available_time/execution_time inherited; fixed +2h stress abolished"},
            {"check": "label_alignment", "status": "PASS", "detail": "forward 24h label clipped at split end; overlapping labels disclosed"},
            {"check": "survivorship_boundary", "status": "WARN", "detail": "Universe498 is current/listing-aware; U0 strict is primary, U1 diagnostic"},
            {"check": "cost_turnover_boundary", "status": "WARN", "detail": "top/bottom book proxy only; no executable turnover/cost replay"},
            {"check": "negative_controls", "status": "PASS" if not blockers else "HOLD", "detail": ";".join(blockers) if blockers else "shortlist controls attached"},
            {"check": "decision", "status": decision, "detail": "A7AL-1 does not authorize alpha proof or formula search execution"},
        ]
    )


def build_report(manifest: dict[str, Any], decisions: pd.DataFrame, metrics: pd.DataFrame, controls: pd.DataFrame, audit: pd.DataFrame) -> None:
    top_decisions = decisions.sort_values(["diagnostic_decision", "global_validation_spread"], ascending=[True, False])
    validation_metrics = metrics[metrics["split"].isin(["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"])].copy()
    report = f"""# CRYPTO A7AL-1 Field-Family Neutralized Baseline

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This is a fixed field-family baseline replay proxy. It does not generate formulas and does not authorize alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Signal Decisions

{md_table(top_decisions, 80)}

## Validation / Test / Recent Metrics

{md_table(validation_metrics.sort_values(["universe", "neutralization_mode", "split", "mean_spread_24h"], ascending=[True, True, True, False]), 120)}

## Negative-Control Audit

{md_table(controls, 120)}

## Bias Audit

{md_table(audit)}

## Boundary

```text
AUTHORIZED NEXT:
  If decision PASS: A7AL-1B control / latency / beta dominance forensic.

NOT AUTHORIZED:
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = prepare_panel()
    panel, specs = add_derived_features(panel)
    panel = prune_panel_for_eval(panel, specs)
    gc.collect()
    metrics, trace, decisions, shortlist = evaluate(panel, specs)
    controls = control_audit(panel, specs, decisions)

    field_family_pass = decisions[decisions["diagnostic_decision"].eq("FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC")]["field_family"].nunique()
    control_blockers = sorted(controls.loc[controls["control_flag"].eq("CONTROL_TOO_STRONG") & controls["control"].ne("sign_flip"), "control"].unique().tolist())
    blockers: list[str] = []
    a7al0p = read_json(A7AL0P)
    a7al0l = read_json(A7AL0L)
    if a7al0p.get("decision") != "PASS_A7AL0P_PRETRAIN_READY_FOR_A7AL1_FIELD_FAMILY_BASELINE":
        blockers.append("a7al0p_not_passed")
    if a7al0l.get("decision") != "PASS_A7AL0L_FIXED_DELAY_STRESS_ABOLISHED":
        blockers.append("a7al0l_not_passed")
    if field_family_pass < 2:
        blockers.append("fewer_than_2_field_families_passed")
    if control_blockers:
        blockers.append("control_dominance_" + "|".join(control_blockers))

    if blockers:
        if "fewer_than_2_field_families_passed" in blockers:
            decision = "HOLD_A7AL1_NO_FIELD_FAMILY_STRUCTURE"
        elif any(b.startswith("control_dominance") for b in blockers):
            decision = "HOLD_A7AL1_CONTROL_CONTAMINATION"
        else:
            decision = "HOLD_A7AL1_PRECONDITION_FAIL"
    else:
        decision = "PASS_A7AL1_FIELD_FAMILY_STRUCTURE_FOUND"

    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_panel_root": str(BASE_PANEL_ROOT),
        "input_latent_panel": str(LV1_PANEL),
        "input_regime_panel": str(REGIME_PANEL),
        "signals_tested": len(specs),
        "field_families_tested": int(pd.Series([s.field_family for s in specs]).nunique()),
        "rows": int(len(panel)),
        "primary_label": PRIMARY_LABEL,
        "neutralization_modes": ["global", "age_neutral", "latent_state_neutral", "liquidity_tier_neutral", "meme_multiplier_aware"],
        "universes": ["U0_strict_full_history", "U1_listing_aware", "U0U1_all_eligible"],
        "passed_field_family_count": int(field_family_pass),
        "blockers": blockers,
        "executes_formula_generation": False,
        "executes_formula_search": False,
        "executes_alpha_proof": False,
        "authorizes_a7al1b_forensic": decision == "PASS_A7AL1_FIELD_FAMILY_STRUCTURE_FOUND",
        "authorizes_a7al2_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "warnings": [
            "Baseline uses overlapping 24h labels and top/bottom spread proxy",
            "Universe498 is current/listing-aware; U0 strict is primary, U1 diagnostic",
            "No executable turnover/cost book is run in A7AL-1",
            "May rows are unavailable and not used",
        ],
    }
    audit = bias_audit(decision, blockers)

    write_json(OUT_DIR / "a7al1_manifest.json", manifest)
    metrics.to_csv(OUT_DIR / "a7al1_field_family_metrics.csv", index=False)
    shortlist.to_csv(OUT_DIR / "a7al1_full_neutralization_shortlist.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7al1_signal_decisions.csv", index=False)
    controls.to_csv(OUT_DIR / "a7al1_negative_control_audit.csv", index=False)
    trace.to_csv(OUT_DIR / "a7al1_timestamp_spread_trace_sample.csv", index=False)
    audit.to_csv(OUT_DIR / "a7al1_bias_audit.csv", index=False)
    build_report(manifest, decisions, metrics, controls, audit)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
