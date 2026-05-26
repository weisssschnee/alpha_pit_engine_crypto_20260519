from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

BASE_PANEL_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v1_20260525"
LV1_PANEL = DATA_ROOT / "gold" / "features" / "binance_universe498_latent_state_features_v1_20260527.parquet"
LV2_MANIFEST = ROOT / "runtime" / "a7ak_lv2_response_merge_audit" / "a7ak_lv2_manifest.json"

OUT_DIR = ROOT / "runtime" / "a7ak_lv3_neutral_field_family_smoke"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AK_LV3_NEUTRAL_FIELD_FAMILY_SMOKE_20260527.md"

TRAIN_END = pd.Timestamp("2024-12-31 23:00:00+00:00")
VALIDATION_END = pd.Timestamp("2025-06-30 23:00:00+00:00")
RECENT_END = pd.Timestamp("2026-04-30 23:00:00+00:00")

LV1_COLUMNS = [
    "symbol",
    "timestamp",
    "split",
    "listing_age_days",
    "trade_return_24h",
    "liquidity_rank_active_universe",
    "realized_vol_168h",
    "funding_rate_abs_168h",
    "basis_abs_168h",
    "premium_abs_168h",
    "open_interest_change_24h",
    "oi_x_price_move_24h",
    "age_x_liquidity",
    "age_x_volatility",
    "age_bucket_dynamic",
    "liquidity_state",
    "volatility_state",
    "funding_abs_state",
    "basis_abs_state",
    "major_state",
    "raw_latent_state_id",
    "state_seen_in_train",
]

BASE_COLUMNS = ["symbol", "timestamp", "trade_close"]

SIGNAL_SPECS = [
    ("momentum_24h", "price", "trade_return_24h", 1.0),
    ("reversal_24h", "price", "trade_return_24h", -1.0),
    ("liquidity_rank", "liquidity", "liquidity_rank_active_universe", 1.0),
    ("low_liquidity", "liquidity", "liquidity_rank_active_universe", -1.0),
    ("realized_vol", "volatility", "realized_vol_168h", 1.0),
    ("low_realized_vol", "volatility", "realized_vol_168h", -1.0),
    ("funding_abs", "funding", "funding_rate_abs_168h", 1.0),
    ("basis_abs", "basis", "basis_abs_168h", 1.0),
    ("premium_abs", "basis", "premium_abs_168h", 1.0),
    ("oi_change_24h", "positioning", "open_interest_change_24h", 1.0),
    ("oi_x_price_move", "positioning", "oi_x_price_move_24h", 1.0),
    ("age_x_liquidity", "age_interaction", "age_x_liquidity", 1.0),
    ("age_x_volatility", "age_interaction", "age_x_volatility", 1.0),
]

SPLIT_TIMESTAMP_SAMPLE_CAP = {
    "train_2024": 384,
    "validation_2025H1": 256,
    "recent_2025H2_2026Apr": 384,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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


def symbol_dirs() -> list[Path]:
    return sorted(p for p in BASE_PANEL_ROOT.glob("symbol=*") if (p / "part.parquet").exists())


def split_end(split: str) -> pd.Timestamp:
    if split == "train_2024":
        return TRAIN_END
    if split == "validation_2025H1":
        return VALIDATION_END
    if split == "recent_2025H2_2026Apr":
        return RECENT_END
    return pd.Timestamp("1900-01-01 00:00:00+00:00")


def load_forward_label() -> pd.DataFrame:
    parts = []
    for sym_dir in symbol_dirs():
        df = pd.read_parquet(sym_dir / "part.parquet", columns=BASE_COLUMNS, engine="pyarrow")
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)
        close = pd.to_numeric(df["trade_close"], errors="coerce")
        log_close = np.log(close.where(close > 0))
        df["fwd_ret_24h"] = log_close.shift(-24) - log_close
        parts.append(df[["symbol", "timestamp", "fwd_ret_24h"]])
    return pd.concat(parts, ignore_index=True)


def prepare_panel() -> pd.DataFrame:
    panel = pd.read_parquet(LV1_PANEL, columns=LV1_COLUMNS, engine="pyarrow")
    panel["timestamp"] = pd.to_datetime(panel["timestamp"], utc=True)
    labels = load_forward_label()
    panel = panel.merge(labels, on=["symbol", "timestamp"], how="left")
    ends = panel["split"].map(lambda s: split_end(str(s)))
    label_end = panel["timestamp"] + pd.Timedelta(hours=24)
    panel.loc[label_end > ends, "fwd_ret_24h"] = np.nan
    panel["coarse_latent_group"] = (
        panel["age_bucket_dynamic"].astype(str)
        + "|"
        + panel["liquidity_state"].astype(str)
        + "|"
        + panel["volatility_state"].astype(str)
        + "|"
        + panel["major_state"].astype(str)
    )
    return panel


def deterministic_timestamp_sample(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    keep_ts = []
    rows = []
    for split, cap in SPLIT_TIMESTAMP_SAMPLE_CAP.items():
        timestamps = np.array(sorted(panel.loc[panel["split"] == split, "timestamp"].dropna().unique()))
        if len(timestamps) == 0:
            rows.append({"split": split, "available_timestamps": 0, "sampled_timestamps": 0, "sample_cap": cap})
            continue
        if len(timestamps) <= cap:
            chosen = timestamps
        else:
            idx = np.linspace(0, len(timestamps) - 1, cap).round().astype(int)
            chosen = timestamps[np.unique(idx)]
        keep_ts.extend(chosen.tolist())
        rows.append(
            {
                "split": split,
                "available_timestamps": int(len(timestamps)),
                "sampled_timestamps": int(len(chosen)),
                "sample_cap": int(cap),
            }
        )
    sampled = panel[panel["timestamp"].isin(pd.to_datetime(keep_ts, utc=True))].copy()
    return sampled, pd.DataFrame(rows)


def cross_section_z(df: pd.DataFrame, value: pd.Series) -> pd.Series:
    mean = value.groupby(df["timestamp"]).transform("mean")
    std = value.groupby(df["timestamp"]).transform("std").replace(0, np.nan)
    return ((value - mean) / std).clip(-5, 5)


def neutral_z(df: pd.DataFrame, value: pd.Series, group_cols: list[str], min_group_size: int) -> pd.Series:
    tmp = pd.DataFrame({"timestamp": df["timestamp"], "value": value})
    for col in group_cols:
        tmp[col] = df[col].astype(str)
    keys = ["timestamp"] + group_cols
    count = tmp.groupby(keys, observed=True)["value"].transform("count")
    mean = tmp.groupby(keys, observed=True)["value"].transform("mean")
    std = tmp.groupby(keys, observed=True)["value"].transform("std").replace(0, np.nan)
    z = ((tmp["value"] - mean) / std).clip(-5, 5)
    z[count < min_group_size] = np.nan
    return z


def timestamp_ic_and_spread(df: pd.DataFrame, signal: pd.Series) -> tuple[pd.DataFrame, dict[str, float]]:
    work = pd.DataFrame(
        {
            "timestamp": df["timestamp"],
            "split": df["split"],
            "signal": pd.to_numeric(signal, errors="coerce"),
            "label": pd.to_numeric(df["fwd_ret_24h"], errors="coerce"),
        }
    ).replace([np.inf, -np.inf], np.nan)
    work = work.dropna(subset=["signal", "label"])
    valid_share = float(len(work) / len(df)) if len(df) else 0.0
    rows = []
    for (split, ts), g in work.groupby(["split", "timestamp"], observed=True):
        if len(g) < 20 or g["signal"].nunique() < 5:
            continue
        ic = g["signal"].corr(g["label"], method="spearman")
        q_hi = g["signal"].quantile(0.9)
        q_lo = g["signal"].quantile(0.1)
        top = g[g["signal"] >= q_hi]["label"].mean()
        bottom = g[g["signal"] <= q_lo]["label"].mean()
        rows.append(
            {
                "split": split,
                "timestamp": ts,
                "n_obs": int(len(g)),
                "ic_spearman": float(ic) if pd.notna(ic) else np.nan,
                "decile_spread": float(top - bottom) if pd.notna(top) and pd.notna(bottom) else np.nan,
            }
        )
    return pd.DataFrame(rows), {"valid_row_share": valid_share, "valid_rows": float(len(work))}


def tstat(values: pd.Series) -> float:
    values = pd.to_numeric(values, errors="coerce").dropna()
    if len(values) < 3:
        return np.nan
    std = values.std(ddof=1)
    if not np.isfinite(std) or std == 0:
        return np.nan
    return float(values.mean() / std * np.sqrt(len(values)))


def summarize_ts(ts_df: pd.DataFrame, signal_name: str, family: str, mode: str, coverage: dict[str, float]) -> pd.DataFrame:
    rows = []
    for split, g in ts_df.groupby("split", observed=True):
        rows.append(
            {
                "signal_name": signal_name,
                "field_family": family,
                "neutralization_mode": mode,
                "split": split,
                "n_dates": int(g["timestamp"].nunique()),
                "avg_n_obs": float(g["n_obs"].mean()) if len(g) else np.nan,
                "valid_row_share": coverage["valid_row_share"],
                "valid_rows": int(coverage["valid_rows"]),
                "mean_ic": float(g["ic_spearman"].mean()) if len(g) else np.nan,
                "ic_tstat": tstat(g["ic_spearman"]),
                "positive_ic_rate": float((g["ic_spearman"] > 0).mean()) if len(g) else np.nan,
                "mean_decile_spread": float(g["decile_spread"].mean()) if len(g) else np.nan,
                "decile_spread_tstat": tstat(g["decile_spread"]),
                "positive_spread_rate": float((g["decile_spread"] > 0).mean()) if len(g) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def evaluate_signals(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_parts = []
    coverage_rows = []
    modes = [
        ("global", [], 1),
        ("age_neutral", ["age_bucket_dynamic"], 5),
        ("coarse_latent_neutral", ["coarse_latent_group"], 5),
        ("raw_latent_neutral", ["raw_latent_state_id"], 5),
    ]
    for signal_name, family, source_col, direction in SIGNAL_SPECS:
        value = direction * pd.to_numeric(panel[source_col], errors="coerce")
        for mode, group_cols, min_group_size in modes:
            if mode == "global":
                signal = cross_section_z(panel, value)
            else:
                signal = neutral_z(panel, value, group_cols, min_group_size)
            ts_df, coverage = timestamp_ic_and_spread(panel, signal)
            metric_parts.append(summarize_ts(ts_df, signal_name, family, mode, coverage))
            coverage_rows.append(
                {
                    "signal_name": signal_name,
                    "field_family": family,
                    "neutralization_mode": mode,
                    "valid_row_share": coverage["valid_row_share"],
                    "valid_rows": int(coverage["valid_rows"]),
                    "min_group_size": min_group_size,
                }
            )
    return pd.concat(metric_parts, ignore_index=True), pd.DataFrame(coverage_rows)


def classify_signals(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    pivot = metrics.pivot_table(
        index=["signal_name", "field_family", "neutralization_mode"],
        columns="split",
        values=["mean_ic", "ic_tstat", "valid_row_share", "n_dates"],
        aggfunc="first",
    )
    signal_keys = metrics[["signal_name", "field_family"]].drop_duplicates().sort_values(["field_family", "signal_name"])
    for signal_name, family in signal_keys.itertuples(index=False, name=None):
        def get(mode: str, field: str, split: str) -> float:
            try:
                return float(pivot.loc[(signal_name, family, mode), (field, split)])
            except Exception:
                return np.nan

        g_val = get("global", "mean_ic", "validation_2025H1")
        g_rec = get("global", "mean_ic", "recent_2025H2_2026Apr")
        a_val = get("age_neutral", "mean_ic", "validation_2025H1")
        a_rec = get("age_neutral", "mean_ic", "recent_2025H2_2026Apr")
        c_val = get("coarse_latent_neutral", "mean_ic", "validation_2025H1")
        c_rec = get("coarse_latent_neutral", "mean_ic", "recent_2025H2_2026Apr")
        raw_cov = get("raw_latent_neutral", "valid_row_share", "recent_2025H2_2026Apr")

        global_consistent = np.isfinite(g_val) and np.isfinite(g_rec) and np.sign(g_val) == np.sign(g_rec) and abs(g_val) >= 0.005 and abs(g_rec) >= 0.005
        age_survives = np.isfinite(a_val) and np.isfinite(a_rec) and np.sign(a_val) == np.sign(g_val) and np.sign(a_rec) == np.sign(g_rec) and abs(a_val) >= 0.003 and abs(a_rec) >= 0.003
        coarse_survives = np.isfinite(c_val) and np.isfinite(c_rec) and np.sign(c_val) == np.sign(g_val) and np.sign(c_rec) == np.sign(g_rec) and abs(c_val) >= 0.003 and abs(c_rec) >= 0.003
        if not global_consistent:
            decision = "NO_STABLE_GLOBAL_SIGNAL"
        elif age_survives and coarse_survives:
            decision = "SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC"
        elif age_survives and not coarse_survives:
            decision = "LIKELY_LATENT_STATE_BIAS"
        elif not age_survives:
            decision = "LIKELY_AGE_OR_LIFECYCLE_BIAS"
        else:
            decision = "HOLD_NEEDS_REVIEW"
        rows.append(
            {
                "signal_name": signal_name,
                "field_family": family,
                "global_validation_mean_ic": g_val,
                "global_recent_mean_ic": g_rec,
                "age_neutral_validation_mean_ic": a_val,
                "age_neutral_recent_mean_ic": a_rec,
                "coarse_latent_validation_mean_ic": c_val,
                "coarse_latent_recent_mean_ic": c_rec,
                "raw_latent_recent_valid_row_share": raw_cov,
                "diagnostic_decision": decision,
            }
        )
    return pd.DataFrame(rows)


def bias_audit() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "check": "candidate_set",
                "status": "PASS",
                "detail": "fixed field-family list only; no generated formulas",
            },
            {
                "check": "neutralization_modes",
                "status": "PASS",
                "detail": "global, age-neutral, coarse-latent-neutral, raw-latent-neutral are reported separately",
            },
            {
                "check": "may_usage",
                "status": "PASS",
                "detail": "May rows are unavailable and not used",
            },
            {
                "check": "promotion_boundary",
                "status": "PASS",
                "detail": "LV3 is diagnostic IC/spread smoke, not tradable replay or alpha proof",
            },
            {
                "check": "cost_boundary",
                "status": "WARN",
                "detail": "no executable turnover/cost book is run in LV3",
            },
        ]
    )


def build_report(
    summary: dict[str, Any],
    sample_df: pd.DataFrame,
    metrics: pd.DataFrame,
    coverage: pd.DataFrame,
    decisions: pd.DataFrame,
    audit: pd.DataFrame,
) -> None:
    validation_recent = metrics[metrics["split"].isin(["validation_2025H1", "recent_2025H2_2026Apr"])].copy()
    top_metrics = validation_recent.sort_values(["split", "mean_ic"], ascending=[True, False])
    report = f"""# CRYPTO A7AK-LV3 Neutral Field-Family Smoke

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

LV3 compares fixed field-family signals under global, age-neutral, coarse-latent-neutral, and raw-latent-neutral ranking. It does not generate formulas and does not authorize promotion.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Signal Decisions

{md_table(decisions, max_rows=80)}

## Timestamp Sample Audit

{md_table(sample_df)}

## Validation / Recent Metrics

{md_table(top_metrics, max_rows=120)}

## Neutralization Coverage

{md_table(coverage, max_rows=80)}

## Bias Boundary Audit

{md_table(audit)}

## Boundary

```text
AUTHORIZED NEXT:
  A7AK-LV4 small fixed-family neutral replay design, only for signals that survive age/coarse-latent diagnostics

NOT AUTHORIZED:
  broad formula search
  alpha proof
  shadow / paper / live

INTERPRETATION:
  Global-only signal = likely age/state exposure.
  Age-neutral survival but coarse-latent failure = likely latent state bias.
  Survival under age and coarse latent = diagnostic candidate only, not alpha proof.
```
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lv2_manifest = read_json(LV2_MANIFEST)
    panel = prepare_panel()
    panel, sample_df = deterministic_timestamp_sample(panel)
    metrics, coverage = evaluate_signals(panel)
    decisions = classify_signals(metrics)
    audit = bias_audit()

    survivor_count = int((decisions["diagnostic_decision"] == "SURVIVES_AGE_AND_COARSE_LATENT_NEUTRAL_DIAGNOSTIC").sum())
    bias_count = int(decisions["diagnostic_decision"].isin(["LIKELY_LATENT_STATE_BIAS", "LIKELY_AGE_OR_LIFECYCLE_BIAS"]).sum())
    blockers: list[str] = []
    if lv2_manifest.get("decision") != "PASS_A7AK_LV2_RESPONSE_MERGE_AUDIT_READY":
        blockers.append("lv2_not_passed")
    if metrics.empty:
        blockers.append("empty_lv3_metrics")

    summary = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AK_LV3_NEUTRAL_FIELD_FAMILY_DIAGNOSTIC_READY",
        "input_lv1_panel": str(LV1_PANEL),
        "input_base_panel_root": str(BASE_PANEL_ROOT),
        "signals_tested": int(len(SIGNAL_SPECS)),
        "sampled_rows": int(len(panel)),
        "timestamp_sample_caps": SPLIT_TIMESTAMP_SAMPLE_CAP,
        "neutralization_modes": ["global", "age_neutral", "coarse_latent_neutral", "raw_latent_neutral"],
        "diagnostic_survivors_age_and_coarse_latent": survivor_count,
        "likely_age_or_latent_bias_signals": bias_count,
        "executes_fixed_field_family_diagnostic": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_tradable_replay": False,
        "authorizes_lv4_small_fixed_family_replay_design": True,
        "authorizes_broad_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "warnings": [
            "LV3 uses IC/spread diagnostics, not executable book PnL",
            "Raw latent neutralization has lower coverage because groups are sparse",
            "May rows are unavailable and not used",
            "Signals that survive neutralization are diagnostic candidates only",
        ],
    }
    if blockers:
        summary["decision"] = "HOLD_A7AK_LV3_NEUTRAL_FIELD_FAMILY_DIAGNOSTIC_BLOCKED"
        summary["authorizes_lv4_small_fixed_family_replay_design"] = False

    write_json(OUT_DIR / "a7ak_lv3_manifest.json", summary)
    sample_df.to_csv(OUT_DIR / "a7ak_lv3_timestamp_sample_audit.csv", index=False)
    metrics.to_csv(OUT_DIR / "a7ak_lv3_signal_mode_metrics.csv", index=False)
    coverage.to_csv(OUT_DIR / "a7ak_lv3_neutralization_coverage.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7ak_lv3_signal_decisions.csv", index=False)
    audit.to_csv(OUT_DIR / "a7ak_lv3_bias_boundary_audit.csv", index=False)

    build_report(summary, sample_df, metrics, coverage, decisions, audit)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
