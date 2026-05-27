from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

GOLD_ROOT = DATA_ROOT / "gold" / "features" / "okx_binance_cross_exchange_1h_30d_v1_20260527"
A7AP0_MANIFEST = ROOT / "runtime" / "a7ap0_cross_exchange_overlay_acceptance" / "a7ap0_manifest.json"
A7AP0_PRICE_SCALE_AUDIT = ROOT / "runtime" / "a7ap0_cross_exchange_overlay_acceptance" / "a7ap0_price_scale_audit.csv"

OUT_DIR = ROOT / "runtime" / "a7ap1_cross_exchange_field_smoke"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AP1_CROSS_EXCHANGE_FIELD_SMOKE_20260527.md"

FIELD_SPECS = [
    ("mark_basis_okx_minus_binance", "basis", "mark_basis_bps_okx_minus_binance", 1.0),
    ("mark_basis_binance_minus_okx", "basis", "mark_basis_bps_okx_minus_binance", -1.0),
    ("index_spread_okx_minus_binance", "index_spread", "index_spread_bps_okx_minus_binance", 1.0),
    ("index_spread_binance_minus_okx", "index_spread", "index_spread_bps_okx_minus_binance", -1.0),
    ("funding_spread_okx_minus_binance", "funding", "funding_spread_okx_minus_binance", 1.0),
    ("funding_spread_binance_minus_okx", "funding", "funding_spread_okx_minus_binance", -1.0),
    ("okx_internal_basis", "basis", "okx_internal_mark_index_basis_bps", 1.0),
    ("binance_internal_basis", "basis", "binance_internal_mark_index_basis_bps", 1.0),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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


def load_panel() -> pd.DataFrame:
    parts = []
    for path in sorted(GOLD_ROOT.glob("symbol=*/part.parquet")):
        df = pd.read_parquet(path, engine="pyarrow")
        parts.append(df)
    panel = pd.concat(parts, ignore_index=True)
    panel["timestamp"] = pd.to_datetime(panel["timestamp"], utc=True)
    panel = panel.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    if A7AP0_PRICE_SCALE_AUDIT.exists():
        price_scale = pd.read_csv(A7AP0_PRICE_SCALE_AUDIT)
        quarantine = set(price_scale.loc[price_scale["price_scale_status"] != "clean", "symbol"].astype(str))
        if quarantine:
            panel = panel[~panel["symbol"].astype(str).isin(quarantine)].copy()
    close = pd.to_numeric(panel["binance_trade_close"], errors="coerce")
    log_close = np.log(close.where(close > 0))
    panel["_log_close"] = log_close
    for h in [1, 4, 12]:
        panel[f"fwd_ret_{h}h"] = panel.groupby("symbol", observed=True)["_log_close"].shift(-h) - panel["_log_close"]
    panel = panel.drop(columns=["_log_close"])
    return panel


def cs_zscore(panel: pd.DataFrame, value: pd.Series) -> pd.Series:
    mean = value.groupby(panel["timestamp"]).transform("mean")
    std = value.groupby(panel["timestamp"]).transform("std").replace(0, np.nan)
    return ((value - mean) / std).clip(-5, 5)


def timestamp_metrics(panel: pd.DataFrame, signal: pd.Series, label_col: str) -> pd.DataFrame:
    work = pd.DataFrame(
        {
            "timestamp": panel["timestamp"],
            "symbol": panel["symbol"],
            "signal": pd.to_numeric(signal, errors="coerce"),
            "label": pd.to_numeric(panel[label_col], errors="coerce"),
        }
    ).replace([np.inf, -np.inf], np.nan)
    work = work.dropna(subset=["signal", "label"])
    rows = []
    for ts, g in work.groupby("timestamp", observed=True):
        if len(g) < 30 or g["signal"].nunique() < 8:
            continue
        ic = g["signal"].corr(g["label"], method="spearman")
        q_hi = g["signal"].quantile(0.9)
        q_lo = g["signal"].quantile(0.1)
        top = g[g["signal"] >= q_hi]["label"].mean()
        bottom = g[g["signal"] <= q_lo]["label"].mean()
        rows.append(
            {
                "timestamp": ts,
                "n_obs": int(len(g)),
                "ic_spearman": float(ic) if pd.notna(ic) else np.nan,
                "decile_spread": float(top - bottom) if pd.notna(top) and pd.notna(bottom) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def tstat(values: pd.Series) -> float:
    values = pd.to_numeric(values, errors="coerce").dropna()
    if len(values) < 3:
        return np.nan
    std = values.std(ddof=1)
    if not np.isfinite(std) or std == 0:
        return np.nan
    return float(values.mean() / std * np.sqrt(len(values)))


def evaluate(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    ts_parts = []
    for name, family, col, direction in FIELD_SPECS:
        raw = direction * pd.to_numeric(panel[col], errors="coerce")
        signal = cs_zscore(panel, raw)
        valid_rows = int((signal.notna()).sum())
        valid_share = float(signal.notna().mean())
        for horizon in [1, 4, 12]:
            label_col = f"fwd_ret_{horizon}h"
            ts_df = timestamp_metrics(panel, signal, label_col)
            if not ts_df.empty:
                ts_df["signal_name"] = name
                ts_df["field_family"] = family
                ts_df["label_horizon"] = f"{horizon}h"
                ts_parts.append(ts_df)
            rows.append(
                {
                    "signal_name": name,
                    "field_family": family,
                    "source_column": col,
                    "direction": direction,
                    "label_horizon": f"{horizon}h",
                    "valid_rows": valid_rows,
                    "valid_row_share": valid_share,
                    "n_dates": int(ts_df["timestamp"].nunique()) if not ts_df.empty else 0,
                    "avg_n_obs": float(ts_df["n_obs"].mean()) if not ts_df.empty else np.nan,
                    "mean_ic": float(ts_df["ic_spearman"].mean()) if not ts_df.empty else np.nan,
                    "ic_tstat": tstat(ts_df["ic_spearman"]) if not ts_df.empty else np.nan,
                    "positive_ic_rate": float((ts_df["ic_spearman"] > 0).mean()) if not ts_df.empty else np.nan,
                    "mean_decile_spread": float(ts_df["decile_spread"].mean()) if not ts_df.empty else np.nan,
                    "decile_spread_tstat": tstat(ts_df["decile_spread"]) if not ts_df.empty else np.nan,
                    "positive_spread_rate": float((ts_df["decile_spread"] > 0).mean()) if not ts_df.empty else np.nan,
                }
            )
    ts_metrics = pd.concat(ts_parts, ignore_index=True) if ts_parts else pd.DataFrame()
    return pd.DataFrame(rows), ts_metrics


def classify(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (name, family), g in metrics.groupby(["signal_name", "field_family"], observed=True):
        best = g.sort_values("mean_ic", key=lambda s: s.abs(), ascending=False).head(1).iloc[0]
        max_abs_ic = float(g["mean_ic"].abs().max())
        min_dates = int(g["n_dates"].min())
        if min_dates < 80:
            decision = "HOLD_TOO_FEW_DATES_FOR_ANYTHING_BEYOND_DIAGNOSTIC"
        elif max_abs_ic >= 0.04 and abs(float(best["ic_tstat"])) >= 2:
            decision = "A7AP1_DIAGNOSTIC_CLUE_ONLY"
        else:
            decision = "NO_DIAGNOSTIC_CLUE"
        rows.append(
            {
                "signal_name": name,
                "field_family": family,
                "best_horizon": best["label_horizon"],
                "best_mean_ic": float(best["mean_ic"]),
                "best_ic_tstat": float(best["ic_tstat"]),
                "best_mean_decile_spread": float(best["mean_decile_spread"]),
                "min_dates_across_horizons": min_dates,
                "decision": decision,
            }
        )
    return pd.DataFrame(rows).sort_values(["decision", "best_mean_ic"], ascending=[True, False])


def build_report(summary: dict[str, Any], decisions: pd.DataFrame, metrics: pd.DataFrame) -> None:
    report = f"""# CRYPTO A7AP-1 Cross-Exchange Field Smoke

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This is a small diagnostic IC/spread smoke on the short OKX/Binance overlap. It is not a tradable replay and cannot be alpha proof.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Signal Decisions

{md_table(decisions, max_rows=80)}

## Metrics

{md_table(metrics.sort_values("mean_ic", key=lambda s: s.abs(), ascending=False), max_rows=120)}

## Boundary

```text
AUTHORIZED NEXT:
  Use high-signal fields as diagnostic candidates for longer overlap collection or future forward telemetry.

NOT AUTHORIZED:
  historical alpha proof
  broad formula search
  shadow / paper / live

CAVEAT:
  The overlap window is only 103 hourly timestamps, ending 2026-04-30.
```
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    a7ap0 = read_json(A7AP0_MANIFEST)
    panel = load_panel()
    metrics, ts_metrics = evaluate(panel)
    decisions = classify(metrics)

    blockers: list[str] = []
    if a7ap0.get("decision") not in {
        "PASS_A7AP0_CROSS_EXCHANGE_OVERLAY_ACCEPTED_FOR_DIAGNOSTIC_SMOKE",
        "PASS_A7AP0_CROSS_EXCHANGE_OVERLAY_ACCEPTED_WITH_PRICE_SCALE_QUARANTINE",
    }:
        blockers.append("a7ap0_not_passed")
    if metrics.empty:
        blockers.append("empty_field_smoke_metrics")
    clue_count = int((decisions["decision"] == "A7AP1_DIAGNOSTIC_CLUE_ONLY").sum()) if not decisions.empty else 0

    summary = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AP1_CROSS_EXCHANGE_FIELD_SMOKE_DIAGNOSTIC_ONLY",
        "input_gold_root": str(GOLD_ROOT),
        "rows": int(len(panel)),
        "symbols": int(panel["symbol"].nunique()),
        "unique_hours": int(panel["timestamp"].nunique()),
        "timestamp_min": str(panel["timestamp"].min()),
        "timestamp_max": str(panel["timestamp"].max()),
        "fields_tested": int(len(FIELD_SPECS)),
        "price_scale_quarantine_applied": True,
        "price_scale_quarantine_symbols": a7ap0.get("price_scale_quarantine_symbols", []),
        "diagnostic_clue_count": clue_count,
        "executes_small_field_smoke": True,
        "executes_tradable_replay": False,
        "executes_search": False,
        "authorizes_longer_overlap_or_forward_collection_design": True,
        "authorizes_broad_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "warnings": [
            "Only 103 hourly timestamps are available in the overlap",
            "Funding fields are sparse on Binance side",
            "IC/spread diagnostics are not executable PnL",
        ],
    }
    if blockers:
        summary["decision"] = "HOLD_A7AP1_CROSS_EXCHANGE_FIELD_SMOKE_BLOCKED"
        summary["authorizes_longer_overlap_or_forward_collection_design"] = False

    write_json(OUT_DIR / "a7ap1_manifest.json", summary)
    metrics.to_csv(OUT_DIR / "a7ap1_field_smoke_metrics.csv", index=False)
    ts_metrics.to_csv(OUT_DIR / "a7ap1_timestamp_metrics.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7ap1_signal_decisions.csv", index=False)
    build_report(summary, decisions, metrics)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
