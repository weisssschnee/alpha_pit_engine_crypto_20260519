from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

INPUT_GOLD_ROOT = DATA_ROOT / "gold" / "features" / "okx_binance_cross_exchange_1h_30d_v1_20260527"
TAXONOMY_PATH = DATA_ROOT / "gold" / "metadata" / "binance_universe498_contract_meme_taxonomy_v1_20260527.csv"
OUTPUT_GOLD_ROOT = DATA_ROOT / "gold" / "features" / "okx_binance_cross_exchange_1h_30d_v1_price_scale_repaired_20260527"

OUT_DIR = ROOT / "runtime" / "a7ap2_multiplier_price_scale_repair"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AP2_MULTIPLIER_PRICE_SCALE_REPAIR_20260527.md"

PRICE_SCALE_MISMATCH_BPS_THRESHOLD = 500.0

FIELD_SPECS = [
    ("mark_basis_okx_contract_unit_minus_binance", "basis", "mark_basis_bps_okx_contract_unit_minus_binance", 1.0),
    ("mark_basis_binance_minus_okx_contract_unit", "basis", "mark_basis_bps_okx_contract_unit_minus_binance", -1.0),
    ("index_spread_okx_contract_unit_minus_binance", "index_spread", "index_spread_bps_okx_contract_unit_minus_binance", 1.0),
    ("index_spread_binance_minus_okx_contract_unit", "index_spread", "index_spread_bps_okx_contract_unit_minus_binance", -1.0),
    ("funding_spread_okx_minus_binance", "funding", "funding_spread_okx_minus_binance", 1.0),
    ("funding_spread_binance_minus_okx", "funding", "funding_spread_okx_minus_binance", -1.0),
    ("okx_internal_basis", "basis", "okx_internal_mark_index_basis_bps", 1.0),
    ("binance_internal_basis", "basis", "binance_internal_mark_index_basis_bps", 1.0),
]


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


def parquet_files() -> list[Path]:
    return sorted(INPUT_GOLD_ROOT.glob("symbol=*/part.parquet"))


def load_taxonomy() -> pd.DataFrame:
    tax = pd.read_csv(TAXONOMY_PATH)
    keep = ["symbol", "underlying_asset", "contract_unit_multiplier", "is_multiplier_contract", "is_meme_token", "meme_confidence"]
    return tax[keep].copy()


def repair_symbol_file(path: Path, tax_row: pd.Series) -> pd.DataFrame:
    df = pd.read_parquet(path, engine="pyarrow")
    multiplier = int(tax_row.get("contract_unit_multiplier", 1))
    is_multiplier = bool(tax_row.get("is_multiplier_contract", False))
    df["contract_unit_multiplier"] = multiplier
    df["underlying_asset"] = str(tax_row.get("underlying_asset", ""))
    df["price_scale_repair_applied"] = bool(is_multiplier and multiplier != 1)
    for field in ["open", "high", "low", "close"]:
        mark_col = f"okx_mark_{field}"
        index_col = f"okx_index_{field}"
        if mark_col in df.columns:
            df[f"okx_mark_{field}_contract_unit"] = pd.to_numeric(df[mark_col], errors="coerce") * multiplier
        if index_col in df.columns:
            df[f"okx_index_{field}_contract_unit"] = pd.to_numeric(df[index_col], errors="coerce") * multiplier
    df["mark_basis_bps_okx_contract_unit_minus_binance"] = (
        df["okx_mark_close_contract_unit"] / pd.to_numeric(df["binance_mark_close"], errors="coerce") - 1.0
    ) * 10000.0
    df["index_spread_bps_okx_contract_unit_minus_binance"] = (
        df["okx_index_close_contract_unit"] / pd.to_numeric(df["binance_index_close"], errors="coerce") - 1.0
    ) * 10000.0
    out_path = OUTPUT_GOLD_ROOT / path.parent.name / "part.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, engine="pyarrow", index=False)
    return df


def build_repaired_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    tax = load_taxonomy().set_index("symbol")
    parts = []
    audit_rows = []
    for path in parquet_files():
        symbol = path.parent.name.split("=", 1)[1]
        tax_row = tax.loc[symbol] if symbol in tax.index else pd.Series({"contract_unit_multiplier": 1, "is_multiplier_contract": False})
        df = repair_symbol_file(path, tax_row)
        pre_mark = pd.to_numeric(df["mark_basis_bps_okx_minus_binance"], errors="coerce").abs() > PRICE_SCALE_MISMATCH_BPS_THRESHOLD
        post_mark = pd.to_numeric(df["mark_basis_bps_okx_contract_unit_minus_binance"], errors="coerce").abs() > PRICE_SCALE_MISMATCH_BPS_THRESHOLD
        pre_index = pd.to_numeric(df["index_spread_bps_okx_minus_binance"], errors="coerce").abs() > PRICE_SCALE_MISMATCH_BPS_THRESHOLD
        post_index = pd.to_numeric(df["index_spread_bps_okx_contract_unit_minus_binance"], errors="coerce").abs() > PRICE_SCALE_MISMATCH_BPS_THRESHOLD
        audit_rows.append(
            {
                "symbol": symbol,
                "rows": int(len(df)),
                "contract_unit_multiplier": int(df["contract_unit_multiplier"].iloc[0]),
                "price_scale_repair_applied": bool(df["price_scale_repair_applied"].iloc[0]),
                "pre_mark_extreme_rows": int(pre_mark.sum()),
                "post_mark_extreme_rows": int(post_mark.sum()),
                "pre_index_extreme_rows": int(pre_index.sum()),
                "post_index_extreme_rows": int(post_index.sum()),
                "pre_mark_min": float(df["mark_basis_bps_okx_minus_binance"].min()),
                "pre_mark_max": float(df["mark_basis_bps_okx_minus_binance"].max()),
                "post_mark_min": float(df["mark_basis_bps_okx_contract_unit_minus_binance"].min()),
                "post_mark_max": float(df["mark_basis_bps_okx_contract_unit_minus_binance"].max()),
                "pre_index_min": float(df["index_spread_bps_okx_minus_binance"].min()),
                "pre_index_max": float(df["index_spread_bps_okx_minus_binance"].max()),
                "post_index_min": float(df["index_spread_bps_okx_contract_unit_minus_binance"].min()),
                "post_index_max": float(df["index_spread_bps_okx_contract_unit_minus_binance"].max()),
            }
        )
        parts.append(df)
    panel = pd.concat(parts, ignore_index=True)
    panel["timestamp"] = pd.to_datetime(panel["timestamp"], utc=True)
    panel = panel.sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    audit = pd.DataFrame(audit_rows).sort_values(["price_scale_repair_applied", "symbol"], ascending=[False, True])
    return panel, audit


def cs_zscore(panel: pd.DataFrame, value: pd.Series) -> pd.Series:
    mean = value.groupby(panel["timestamp"]).transform("mean")
    std = value.groupby(panel["timestamp"]).transform("std").replace(0, np.nan)
    return ((value - mean) / std).clip(-5, 5)


def add_forward_returns(panel: pd.DataFrame) -> pd.DataFrame:
    out = panel.copy()
    close = pd.to_numeric(out["binance_trade_close"], errors="coerce")
    out["_log_close"] = np.log(close.where(close > 0))
    for h in [1, 4, 12]:
        out[f"fwd_ret_{h}h"] = out.groupby("symbol", observed=True)["_log_close"].shift(-h) - out["_log_close"]
    return out.drop(columns=["_log_close"])


def timestamp_metrics(panel: pd.DataFrame, signal: pd.Series, label_col: str) -> pd.DataFrame:
    work = pd.DataFrame(
        {
            "timestamp": panel["timestamp"],
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


def field_smoke(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    ts_parts = []
    for name, family, col, direction in FIELD_SPECS:
        raw = direction * pd.to_numeric(panel[col], errors="coerce")
        signal = cs_zscore(panel, raw)
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
                    "valid_rows": int(signal.notna().sum()),
                    "valid_row_share": float(signal.notna().mean()),
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
    return pd.DataFrame(rows), pd.concat(ts_parts, ignore_index=True) if ts_parts else pd.DataFrame()


def classify(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (name, family), g in metrics.groupby(["signal_name", "field_family"], observed=True):
        best = g.sort_values("mean_ic", key=lambda s: s.abs(), ascending=False).head(1).iloc[0]
        max_abs_ic = float(g["mean_ic"].abs().max())
        min_dates = int(g["n_dates"].min())
        if min_dates < 80:
            decision = "HOLD_TOO_FEW_DATES_FOR_ANYTHING_BEYOND_DIAGNOSTIC"
        elif max_abs_ic >= 0.04 and abs(float(best["ic_tstat"])) >= 2:
            decision = "A7AP2_DIAGNOSTIC_CLUE_ONLY"
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
    return pd.DataFrame(rows)


def build_report(summary: dict[str, Any], repair_audit: pd.DataFrame, decisions: pd.DataFrame, metrics: pd.DataFrame) -> None:
    report = f"""# CRYPTO A7AP-2 Multiplier Price-Scale Repair

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This stage repairs OKX/Binance price-scale comparison fields for multiplier contracts by converting OKX mark/index prices to the Binance contract unit before computing cross-exchange basis. It does not alter raw source fields.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Repair Audit

{md_table(repair_audit[repair_audit["price_scale_repair_applied"]], max_rows=80)}

## Signal Decisions After Repair

{md_table(decisions, max_rows=80)}

## Field Smoke Metrics After Repair

{md_table(metrics.sort_values("mean_ic", key=lambda s: s.abs(), ascending=False), max_rows=120)}

## Boundary

```text
AUTHORIZED NEXT:
  use repaired contract-unit fields for short-window diagnostic only
  continue longer overlap / forward telemetry design

NOT AUTHORIZED:
  historical alpha proof
  broad formula search
  shadow / paper / live

CAVEAT:
  overlap remains only 103 hourly timestamps.
```
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel, repair_audit = build_repaired_panel()
    panel = add_forward_returns(panel)
    metrics, ts_metrics = field_smoke(panel)
    decisions = classify(metrics)

    blockers: list[str] = []
    post_extreme_symbols = repair_audit[
        (repair_audit["post_mark_extreme_rows"] > 0) | (repair_audit["post_index_extreme_rows"] > 0)
    ]["symbol"].tolist()
    if post_extreme_symbols:
        blockers.append("post_repair_price_scale_extreme_symbols_remaining")
    if int(np.isinf(panel.select_dtypes(include=[np.number]).to_numpy(dtype=float, copy=False)).sum()):
        blockers.append("inf_numeric_cells_after_repair")

    clue_count = int((decisions["decision"] == "A7AP2_DIAGNOSTIC_CLUE_ONLY").sum()) if not decisions.empty else 0
    repair_symbols = repair_audit.loc[repair_audit["price_scale_repair_applied"], "symbol"].tolist()
    summary = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AP2_MULTIPLIER_PRICE_SCALE_REPAIR_DIAGNOSTIC_READY",
        "input_gold_root": str(INPUT_GOLD_ROOT),
        "output_gold_root": str(OUTPUT_GOLD_ROOT),
        "taxonomy": str(TAXONOMY_PATH),
        "rows": int(len(panel)),
        "symbols": int(panel["symbol"].nunique()),
        "unique_hours": int(panel["timestamp"].nunique()),
        "timestamp_min": str(panel["timestamp"].min()),
        "timestamp_max": str(panel["timestamp"].max()),
        "price_scale_repair_symbols": repair_symbols,
        "price_scale_repair_symbol_count": int(len(repair_symbols)),
        "post_repair_extreme_symbol_count": int(len(post_extreme_symbols)),
        "post_repair_extreme_symbols": post_extreme_symbols,
        "diagnostic_clue_count": clue_count,
        "executes_price_scale_repair": True,
        "executes_small_field_smoke": True,
        "executes_tradable_replay": False,
        "executes_search": False,
        "authorizes_diagnostic_use_repaired_fields": True,
        "authorizes_broad_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "warnings": [
            "Raw OKX/Binance fields are preserved; repaired fields use contract-unit OKX prices",
            "Overlap remains only 103 hours",
            "Field smoke is diagnostic only, not executable PnL",
        ],
    }
    if blockers:
        summary["decision"] = "HOLD_A7AP2_MULTIPLIER_PRICE_SCALE_REPAIR_BLOCKED"
        summary["authorizes_diagnostic_use_repaired_fields"] = False

    write_json(OUT_DIR / "a7ap2_manifest.json", summary)
    repair_audit.to_csv(OUT_DIR / "a7ap2_price_scale_repair_audit.csv", index=False)
    metrics.to_csv(OUT_DIR / "a7ap2_field_smoke_metrics.csv", index=False)
    ts_metrics.to_csv(OUT_DIR / "a7ap2_timestamp_metrics.csv", index=False)
    decisions.to_csv(OUT_DIR / "a7ap2_signal_decisions.csv", index=False)
    build_report(summary, repair_audit, decisions, metrics)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
