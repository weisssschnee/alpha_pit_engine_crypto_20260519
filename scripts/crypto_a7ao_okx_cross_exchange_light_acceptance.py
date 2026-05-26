from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

OKX_ROOT = DATA_ROOT / "silver" / "cross_exchange" / "okx_cross_exchange_light_top50_30d_v1_20260526"
OKX_MANIFEST = DATA_ROOT / "manifests" / "okx_cross_exchange_light_top50_30d_v1_20260526.csv"
OKX_REPORT = DATA_ROOT / "reports" / "okx_cross_exchange_light_top50_30d_v1_20260526.json"
BINANCE_PANEL_ROOT = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v1_20260525"

OUTPUT_ROOT = DATA_ROOT / "gold" / "features" / "okx_binance_cross_exchange_light_top50_30d_v1_20260526"

OUT_DIR = ROOT / "runtime" / "a7ao_okx_cross_exchange_light_acceptance"
REPORT_ACCEPTANCE = ROOT / "reports" / "CRYPTO_A7AO0_OKX_CROSS_EXCHANGE_LIGHT_ACCEPTANCE_20260526.md"
REPORT_ALIGNMENT = ROOT / "reports" / "CRYPTO_A7AO1_OKX_BINANCE_SPREAD_ALIGNMENT_SAMPLE_20260526.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def normalize_ms_to_hour(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, unit="ms", utc=True).dt.floor("h")


def safe_div(num: pd.Series, den: pd.Series) -> pd.Series:
    return (num.astype(float) / den.astype(float).replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)


def load_okx() -> dict[str, pd.DataFrame]:
    funding = pd.read_csv(OKX_ROOT / "okx_funding_history.csv")
    funding["timestamp"] = normalize_ms_to_hour(funding["fundingTime"])
    funding = funding.sort_values(["symbol", "timestamp"]).drop_duplicates(["symbol", "timestamp"], keep="last")

    mark = pd.read_csv(OKX_ROOT / "okx_mark_price_candles_1h.csv")
    mark["timestamp"] = normalize_ms_to_hour(mark["ts"])
    mark = mark.rename(
        columns={
            "open": "okx_mark_open",
            "high": "okx_mark_high",
            "low": "okx_mark_low",
            "close": "okx_mark_close",
            "confirm": "okx_mark_confirm",
        }
    )
    mark = mark.sort_values(["symbol", "timestamp"]).drop_duplicates(["symbol", "timestamp"], keep="last")

    index = pd.read_csv(OKX_ROOT / "okx_index_candles_1h.csv")
    index["timestamp"] = normalize_ms_to_hour(index["ts"])
    index = index.rename(
        columns={
            "open": "okx_index_open",
            "high": "okx_index_high",
            "low": "okx_index_low",
            "close": "okx_index_close",
            "confirm": "okx_index_confirm",
        }
    )
    index = index.sort_values(["symbol", "timestamp"]).drop_duplicates(["symbol", "timestamp"], keep="last")

    oi = pd.read_csv(OKX_ROOT / "okx_open_interest_snapshot.csv")
    if not oi.empty:
        oi["snapshot_time"] = pd.to_datetime(oi["ts"], unit="ms", utc=True)
    return {"funding": funding, "mark": mark, "index": index, "oi": oi}


def dataset_quality(name: str, df: pd.DataFrame, ts_col: str = "timestamp") -> dict[str, Any]:
    numeric = df.select_dtypes(include=[np.number])
    out: dict[str, Any] = {
        "dataset": name,
        "rows": int(len(df)),
        "symbols": int(df["symbol"].nunique()) if "symbol" in df else 0,
        "duplicate_symbol_timestamp": int(df.duplicated(["symbol", ts_col]).sum()) if {"symbol", ts_col}.issubset(df.columns) else None,
        "inf_cell_count": int(np.isinf(numeric.to_numpy(dtype=float, copy=False)).sum()) if not numeric.empty else 0,
        "nan_cell_count": int(numeric.isna().sum().sum()) if not numeric.empty else 0,
    }
    if ts_col in df:
        out["timestamp_min"] = str(df[ts_col].min())
        out["timestamp_max"] = str(df[ts_col].max())
    return out


def manifest_summary(manifest: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dataset, g in manifest.groupby("dataset"):
        rows.append(
            {
                "dataset": dataset,
                "symbols": int(g["symbol"].nunique()),
                "ok_symbols": int((g["status"] == "ok").sum()),
                "error_symbols": int((g["status"] != "ok").sum()),
                "rows": int(g["rows"].sum()),
                "zero_row_ok": int(((g["status"] == "ok") & (g["rows"] == 0)).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("dataset")


def symbol_coverage(manifest: pd.DataFrame, okx: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for symbol, g in manifest.groupby("symbol"):
        row = {"symbol": symbol, "instId": g["instId"].dropna().iloc[0] if len(g["instId"].dropna()) else ""}
        for dataset in ["funding", "mark_1h", "index_1h", "open_interest_snapshot"]:
            part = g[g["dataset"] == dataset]
            row[f"{dataset}_status"] = part["status"].iloc[0] if len(part) else "missing_manifest"
            row[f"{dataset}_rows_manifest"] = int(part["rows"].iloc[0]) if len(part) else 0
        for dataset, key in [("funding", "funding"), ("mark_1h", "mark"), ("index_1h", "index")]:
            d = okx[key]
            p = d[d["symbol"] == symbol]
            row[f"{dataset}_rows_actual"] = int(len(p))
            row[f"{dataset}_timestamp_min"] = str(p["timestamp"].min()) if len(p) else ""
            row[f"{dataset}_timestamp_max"] = str(p["timestamp"].max()) if len(p) else ""
        rows.append(row)
    return pd.DataFrame(rows)


def load_binance(symbol: str, timestamps: pd.Series) -> pd.DataFrame:
    path = BINANCE_PANEL_ROOT / f"symbol={symbol}" / "part.parquet"
    if not path.exists():
        return pd.DataFrame()
    start = timestamps.min()
    end = timestamps.max()
    cols = [
        "symbol",
        "timestamp",
        "mark_close",
        "index_close",
        "premium_close",
        "premium_close_bps",
        "funding_rate",
        "trade_close",
        "feature_available_time",
        "execution_time",
    ]
    df = pd.read_parquet(path, columns=cols, engine="pyarrow")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df[(df["timestamp"] >= start) & (df["timestamp"] <= end)].copy()


def build_alignment(okx: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    mark = okx["mark"][
        [
            "symbol",
            "timestamp",
            "instId",
            "okx_mark_open",
            "okx_mark_high",
            "okx_mark_low",
            "okx_mark_close",
            "okx_mark_confirm",
            "query_time",
        ]
    ].copy()
    index = okx["index"][
        [
            "symbol",
            "timestamp",
            "okx_index_open",
            "okx_index_high",
            "okx_index_low",
            "okx_index_close",
            "okx_index_confirm",
        ]
    ].copy()
    aligned = mark.merge(index, on=["symbol", "timestamp"], how="inner", validate="one_to_one")
    aligned["okx_mark_index_basis_bps"] = (safe_div(aligned["okx_mark_close"], aligned["okx_index_close"]) - 1.0) * 10000.0
    aligned["okx_feature_available_time"] = aligned["timestamp"] + pd.Timedelta(hours=1)
    aligned["okx_sample_only_flag"] = True

    pieces = []
    for symbol, g in aligned.groupby("symbol"):
        b = load_binance(symbol, g["timestamp"])
        if b.empty:
            continue
        part = g.merge(b, on=["symbol", "timestamp"], how="inner", validate="one_to_one")
        pieces.append(part)
    if pieces:
        sample = pd.concat(pieces, ignore_index=True)
    else:
        sample = pd.DataFrame()

    if not sample.empty:
        funding = okx["funding"][["symbol", "timestamp", "fundingRate", "realizedRate", "method", "formulaType"]].rename(
            columns={"fundingRate": "okx_funding_rate", "realizedRate": "okx_realized_funding_rate"}
        )
        sample = sample.merge(funding, on=["symbol", "timestamp"], how="left")
        sample["binance_mark_index_basis_bps"] = (safe_div(sample["mark_close"], sample["index_close"]) - 1.0) * 10000.0
        sample["mark_basis_spread_bps_okx_minus_binance"] = sample["okx_mark_index_basis_bps"] - sample["binance_mark_index_basis_bps"]
        sample["mark_close_spread_bps_okx_minus_binance"] = (safe_div(sample["okx_mark_close"], sample["mark_close"]) - 1.0) * 10000.0
        sample["index_close_spread_bps_okx_minus_binance"] = (safe_div(sample["okx_index_close"], sample["index_close"]) - 1.0) * 10000.0
        sample["funding_spread_okx_minus_binance"] = sample["okx_funding_rate"] - sample["funding_rate"]
        sample["funding_spread_bps_okx_minus_binance"] = sample["funding_spread_okx_minus_binance"] * 10000.0
        sample["feature_available_time"] = sample["timestamp"] + pd.Timedelta(hours=1)
        sample["execution_time_min"] = sample["timestamp"] + pd.Timedelta(hours=2)
        sample["cross_exchange_sample_only"] = True

    summary_rows = []
    for symbol, g in sample.groupby("symbol") if not sample.empty else []:
        summary_rows.append(
            {
                "symbol": symbol,
                "aligned_rows": int(len(g)),
                "timestamp_min": str(g["timestamp"].min()),
                "timestamp_max": str(g["timestamp"].max()),
                "okx_funding_matched_rows": int(g["okx_funding_rate"].notna().sum()) if "okx_funding_rate" in g else 0,
                "basis_spread_bps_mean": float(g["mark_basis_spread_bps_okx_minus_binance"].mean()),
                "basis_spread_bps_abs_p95": float(g["mark_basis_spread_bps_okx_minus_binance"].abs().quantile(0.95)),
                "mark_close_spread_bps_abs_p95": float(g["mark_close_spread_bps_okx_minus_binance"].abs().quantile(0.95)),
                "funding_spread_bps_mean": float(g["funding_spread_bps_okx_minus_binance"].mean()) if "funding_spread_bps_okx_minus_binance" in g else np.nan,
            }
        )
    return sample, pd.DataFrame(summary_rows)


def feature_contract() -> pd.DataFrame:
    rows = [
        ("okx_funding_rate", "okx_funding", "OKX public funding-rate-history recent window", "historical recent sample", "timestamp + 1h conservative", "sample/telemetry only"),
        ("okx_realized_funding_rate", "okx_funding", "OKX public funding-rate-history recent window", "historical recent sample", "timestamp + 1h conservative", "sample/telemetry only"),
        ("okx_mark_close", "okx_mark", "OKX mark-price 1h candles", "historical recent sample", "timestamp + 1h conservative", "sample/telemetry only"),
        ("okx_index_close", "okx_index", "OKX index 1h candles", "historical recent sample", "timestamp + 1h conservative", "sample/telemetry only"),
        ("okx_mark_index_basis_bps", "derived_cross_exchange", "okx_mark_close / okx_index_close - 1", "derived from OKX recent sample", "timestamp + 1h conservative", "sample/telemetry only"),
        ("mark_basis_spread_bps_okx_minus_binance", "derived_cross_exchange", "OKX basis minus Binance basis", "derived aligned sample", "timestamp + 1h conservative", "sample/telemetry only"),
        ("funding_spread_bps_okx_minus_binance", "derived_cross_exchange", "OKX funding minus Binance funding", "derived aligned sample", "timestamp + 1h conservative", "sample/telemetry only"),
        ("okx_open_interest_snapshot", "okx_forward_snapshot", "OKX current open interest snapshot", "forward-only snapshot", "collector_time observable", "forward telemetry only; not historical proof"),
    ]
    return pd.DataFrame(rows, columns=["field_name", "source_class", "raw_source", "history_status", "feature_available_rule", "authorization"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    okx_report = read_json(OKX_REPORT)
    manifest = pd.read_csv(OKX_MANIFEST)
    okx = load_okx()

    manifest_sum = manifest_summary(manifest)
    quality = pd.DataFrame(
        [
            dataset_quality("funding", okx["funding"]),
            dataset_quality("mark_1h", okx["mark"]),
            dataset_quality("index_1h", okx["index"]),
            dataset_quality("open_interest_snapshot", okx["oi"], ts_col="snapshot_time" if "snapshot_time" in okx["oi"].columns else "ts"),
        ]
    )
    coverage = symbol_coverage(manifest, okx)
    aligned, aligned_summary = build_alignment(okx)
    contract = feature_contract()

    if OUTPUT_ROOT.exists():
        for p in OUTPUT_ROOT.glob("*"):
            if p.is_file():
                p.unlink()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    aligned_path = OUTPUT_ROOT / "okx_binance_mark_index_funding_spread_sample.parquet"
    if not aligned.empty:
        aligned.to_parquet(aligned_path, engine="pyarrow", index=False)

    quality.to_csv(OUT_DIR / "a7ao0_okx_dataset_quality.csv", index=False)
    manifest_sum.to_csv(OUT_DIR / "a7ao0_manifest_summary.csv", index=False)
    coverage.to_csv(OUT_DIR / "a7ao0_symbol_coverage.csv", index=False)
    contract.to_csv(OUT_DIR / "a7ao0_field_contract.csv", index=False)
    aligned_summary.to_csv(OUT_DIR / "a7ao1_alignment_summary.csv", index=False)
    if not aligned.empty:
        aligned_summary.to_csv(OUTPUT_ROOT / "okx_binance_alignment_summary.csv", index=False)
        contract.to_csv(OUTPUT_ROOT / "okx_cross_exchange_light_field_contract.csv", index=False)

    hard_blockers = []
    if int(quality["duplicate_symbol_timestamp"].fillna(0).sum()):
        hard_blockers.append("duplicate_symbol_timestamp")
    if int(quality["inf_cell_count"].fillna(0).sum()):
        hard_blockers.append("inf_cells")
    if aligned.empty:
        hard_blockers.append("no_binance_okx_alignment_rows")

    summary = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AO_OKX_LIGHT_SAMPLE_ACCEPTED_FOR_TELEMETRY_AND_SPREAD_AUDIT",
        "okx_report": str(OKX_REPORT),
        "okx_manifest": str(OKX_MANIFEST),
        "okx_root": str(OKX_ROOT),
        "output_root": str(OUTPUT_ROOT),
        "aligned_sample_path": str(aligned_path),
        "manifest_symbols": int(manifest["symbol"].nunique()),
        "funding_rows": int(len(okx["funding"])),
        "mark_rows": int(len(okx["mark"])),
        "index_rows": int(len(okx["index"])),
        "oi_snapshot_rows": int(len(okx["oi"])),
        "aligned_rows": int(len(aligned)),
        "aligned_symbols": int(aligned["symbol"].nunique()) if not aligned.empty else 0,
        "blockers": hard_blockers,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_historical_alpha_proof": False,
        "authorizes_forward_telemetry_design": True,
        "authorizes_cross_exchange_spread_diagnostic": True,
        "warnings": [
            "OKX light sample is recent/partial and not a full historical proof source",
            "open_interest_snapshot is forward-only current snapshot",
            "manifest contains timeout/error rows; use coverage table before any diagnostic",
            "Bybit remains unavailable due timeout and is not part of this sample",
        ],
        "source_report_counts": okx_report.get("counts", {}),
    }
    if hard_blockers:
        summary["decision"] = "HOLD_A7AO_OKX_LIGHT_ACCEPTANCE_BLOCKED"
        summary["authorizes_forward_telemetry_design"] = False
        summary["authorizes_cross_exchange_spread_diagnostic"] = False

    write_json(OUT_DIR / "a7ao_manifest.json", summary)
    write_json(OUTPUT_ROOT / "okx_binance_cross_exchange_light_manifest.json", summary)

    acceptance = f"""# CRYPTO A7AO-0 OKX Cross-Exchange Light Acceptance

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This audit accepts the OKX light top50 30d sample for telemetry/spread diagnostics only. It does not authorize historical alpha proof.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Manifest Summary

{md_table(manifest_sum)}

## Dataset Quality

{md_table(quality)}

## Symbol Coverage Sample

{md_table(coverage, 60)}

## Field Contract

{md_table(contract)}

## Boundary

```text
OKX funding/mark/index = recent partial sample
OKX open interest = forward-only snapshot
Bybit = unavailable
No historical alpha proof, no replay promotion, no search authorization
```
"""
    REPORT_ACCEPTANCE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_ACCEPTANCE.write_text(acceptance, encoding="utf-8")

    align_report = f"""# CRYPTO A7AO-1 OKX-Binance Spread Alignment Sample

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This stage aligns OKX recent mark/index/funding observations with the accepted Binance universe498 replay base where symbols and timestamps overlap.

## Output

```text
{aligned_path}
```

## Alignment Summary

{md_table(aligned_summary, 80)}

## Authorization

```text
AUTHORIZED:
  cross-exchange spread diagnostic
  forward telemetry design

NOT AUTHORIZED:
  historical alpha proof
  large search
  shadow / paper / live
```
"""
    REPORT_ALIGNMENT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_ALIGNMENT.write_text(align_report, encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
