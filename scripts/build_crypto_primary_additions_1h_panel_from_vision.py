from __future__ import annotations

import argparse
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_ROOT = Path(r"G:\AlphaFactory_CryptoData")
DEFAULT_MONTHLY_TAG = "a7ac_company_p0b01_b04_monthly_v3_20260522_194402"
DEFAULT_FUNDING_TAGS = [
    "a7ac_company_p0b05_funding_20260522_193740",
    "a7ac_company_p0b05_funding_retry_20260522_194314",
]

KLINE_COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_asset_volume",
    "number_of_trades",
    "taker_buy_base_asset_volume",
    "taker_buy_quote_asset_volume",
    "ignore",
]
TRADE_DATA_TYPE = "klines"
PREFIX_BY_DATA_TYPE = {
    "markPriceKlines": "mark",
    "indexPriceKlines": "index",
    "premiumIndexKlines": "premium",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_epoch_ms(series: pd.Series) -> pd.Series:
    raw = pd.to_numeric(series, errors="coerce")
    med = raw.dropna().abs().median()
    if pd.isna(med):
        return raw.astype("Int64")
    if med >= 10**15:
        return (raw // 1000).astype("Int64")
    if med >= 10**12:
        return raw.astype("Int64")
    if med >= 10**9:
        return (raw * 1000).astype("Int64")
    return raw.astype("Int64")


def read_zip_csv(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as zf:
        names = [name for name in zf.namelist() if not name.endswith("/")]
        if not names:
            raise ValueError("zip_has_no_csv_member")
        with zf.open(names[0]) as f:
            df = pd.read_csv(f, header=None, dtype=str)
    if df.empty:
        return df
    first = str(df.iloc[0, 0]).lower()
    if "open" in first or first in {"timestamp", "time"}:
        df = df.iloc[1:].reset_index(drop=True)
    for i in range(len(df.columns), len(KLINE_COLUMNS)):
        df[i] = pd.NA
    df = df.iloc[:, : len(KLINE_COLUMNS)].copy()
    df.columns = KLINE_COLUMNS
    return df


def aggregate_zip_to_1h(path: Path, symbol: str, data_type: str) -> pd.DataFrame:
    raw = read_zip_csv(path)
    if raw.empty:
        return raw
    df = raw.copy()
    df["symbol"] = symbol
    df["data_type"] = data_type
    df["open_time_ms"] = normalize_epoch_ms(df["open_time"])
    df["close_time_ms"] = normalize_epoch_ms(df["close_time"])
    df = df.dropna(subset=["open_time_ms"]).copy()
    df["hour_ms"] = ((df["open_time_ms"].astype("int64") // 3_600_000) * 3_600_000).astype("int64")
    for col in [
        "open",
        "high",
        "low",
        "close",
        "volume",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    agg: dict[str, str] = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "close_time_ms": "max",
    }
    if data_type == TRADE_DATA_TYPE:
        agg.update(
            {
                "volume": "sum",
                "quote_asset_volume": "sum",
                "number_of_trades": "sum",
                "taker_buy_base_asset_volume": "sum",
                "taker_buy_quote_asset_volume": "sum",
            }
        )
    out = df.sort_values("open_time_ms").groupby(["symbol", "hour_ms"], as_index=False).agg(agg)
    out = out.rename(columns={"hour_ms": "open_time_ms"})
    out["timestamp"] = pd.to_datetime(out["open_time_ms"], unit="ms", utc=True)
    out["bar_close_timestamp"] = pd.to_datetime(out["close_time_ms"], unit="ms", utc=True, errors="coerce")
    return out.sort_values(["symbol", "open_time_ms"])


def load_monthly_manifest(root: Path, tag: str) -> pd.DataFrame:
    path = root / "manifests" / f"binance_vision_monthly_pool_manifest_{tag}.csv"
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    return df[df["status"].isin(["downloaded_checksum_ok", "exists_checksum_ok"])].copy()


def build_family_hourly(monthly: pd.DataFrame, symbol: str, data_type: str) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    rows = monthly[(monthly["symbol"].eq(symbol)) & (monthly["data_type"].eq(data_type))].sort_values("month")
    frames = []
    errors: list[dict[str, Any]] = []
    for _, row in rows.iterrows():
        path = Path(str(row["path"]))
        try:
            frames.append(aggregate_zip_to_1h(path, symbol, data_type))
        except Exception as exc:  # noqa: BLE001 - record and continue
            errors.append({"symbol": symbol, "data_type": data_type, "month": row.get("month", ""), "path": str(path), "error": repr(exc)})
    if not frames:
        return pd.DataFrame(), errors
    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates(["symbol", "open_time_ms"]).sort_values(["symbol", "open_time_ms"])
    return out, errors


def load_funding(root: Path, funding_tags: list[str], symbols: list[str]) -> pd.DataFrame:
    frames = []
    for tag in funding_tags:
        manifest = root / "manifests" / f"binance_funding_rate_pool_manifest_{tag}.csv"
        if not manifest.exists():
            continue
        rows = pd.read_csv(manifest)
        for _, row in rows[rows["status"].eq("ok")].iterrows():
            silver = Path(str(row.get("silver_path", "")))
            if not silver.exists():
                continue
            df = pd.read_parquet(silver)
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    funding = pd.concat(frames, ignore_index=True)
    funding = funding[funding["symbol"].isin(symbols)].copy()
    if "fundingTime" in funding.columns:
        funding["fundingTime_ms"] = pd.to_numeric(funding["fundingTime"], errors="coerce")
    elif "fundingTime_ms" in funding.columns:
        funding["fundingTime_ms"] = pd.to_numeric(funding["fundingTime_ms"], errors="coerce")
    else:
        return pd.DataFrame()
    funding["latest_known_funding_rate"] = pd.to_numeric(funding["fundingRate"], errors="coerce")
    if "markPrice" in funding.columns:
        funding["funding_mark_price"] = pd.to_numeric(funding["markPrice"], errors="coerce")
    funding["funding_datetime_utc"] = pd.to_datetime(funding["fundingTime_ms"], unit="ms", utc=True, errors="coerce")
    funding = funding.dropna(subset=["fundingTime_ms", "latest_known_funding_rate"])
    funding["fundingTime_ms"] = funding["fundingTime_ms"].astype("int64")
    funding = funding.drop_duplicates(["symbol", "fundingTime_ms"]).sort_values(["symbol", "fundingTime_ms"])
    return funding


def merge_funding(base: pd.DataFrame, funding: pd.DataFrame) -> pd.DataFrame:
    if funding.empty:
        return base
    merged = []
    for symbol, part in base.groupby("symbol", sort=False):
        f = funding[funding["symbol"].eq(symbol)].sort_values("fundingTime_ms")
        if f.empty:
            merged.append(part)
            continue
        keep = ["fundingTime_ms", "funding_datetime_utc", "latest_known_funding_rate"]
        if "funding_mark_price" in f.columns:
            keep.append("funding_mark_price")
        out = pd.merge_asof(
            part.sort_values("open_time_ms"),
            f[keep],
            left_on="open_time_ms",
            right_on="fundingTime_ms",
            direction="backward",
            allow_exact_matches=True,
        )
        merged.append(out)
    return pd.concat(merged, ignore_index=True)


def add_features(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["symbol", "open_time_ms"]).copy()
    g = panel.groupby("symbol", group_keys=False)
    for w in [1, 3, 6, 12, 24]:
        panel[f"ret_{w}"] = g["close"].pct_change(w, fill_method=None)
        panel[f"fwd_ret_{w}"] = g["close"].pct_change(w, fill_method=None).shift(-w)
    panel["log_ret_1"] = g["close"].transform(lambda s: np.log(s).diff())
    panel["hl_range"] = (panel["high"] - panel["low"]) / panel["close"].replace(0, np.nan)
    panel["abs_ret_1"] = panel["ret_1"].abs()
    for w in [6, 12, 24]:
        min_periods = max(3, w // 2)
        panel[f"realized_vol_{w}"] = g["log_ret_1"].transform(lambda s: s.rolling(w, min_periods=min_periods).std())
        panel[f"quote_volume_mean_{w}"] = g["quote_asset_volume"].transform(lambda s: s.rolling(w, min_periods=min_periods).mean())
    panel["avg_trade_size_quote"] = panel["quote_asset_volume"] / panel["number_of_trades"].replace(0, np.nan)
    panel["taker_buy_ratio"] = panel["taker_buy_quote_asset_volume"] / panel["quote_asset_volume"].replace(0, np.nan)
    panel["taker_imbalance"] = (2.0 * panel["taker_buy_ratio"]) - 1.0
    if "mark_close" in panel.columns and "index_close" in panel.columns:
        panel["mark_minus_index"] = panel["mark_close"] - panel["index_close"]
        panel["mark_index_ratio"] = panel["mark_close"] / panel["index_close"].replace(0, np.nan) - 1.0
    if "premium_close" in panel.columns:
        panel["premium_index"] = panel["premium_close"]
    if "latest_known_funding_rate" in panel.columns:
        panel["funding_rate_sign"] = np.sign(panel["latest_known_funding_rate"])
        fg = panel.groupby("symbol")["latest_known_funding_rate"]
        mean = fg.transform(lambda s: s.rolling(24, min_periods=8).mean())
        std = fg.transform(lambda s: s.rolling(24, min_periods=8).std()).replace(0, np.nan)
        panel["funding_rate_z_24"] = (panel["latest_known_funding_rate"] - mean) / std
        panel["funding_rate_persistence_3"] = panel.groupby("symbol")["funding_rate_sign"].transform(lambda s: s.rolling(3, min_periods=2).mean())
    for col in [
        "ret_1",
        "ret_3",
        "ret_6",
        "ret_12",
        "ret_24",
        "quote_asset_volume",
        "taker_imbalance",
        "realized_vol_12",
        "mark_index_ratio",
        "premium_index",
        "latest_known_funding_rate",
    ]:
        if col not in panel.columns:
            continue
        grp = panel.groupby("open_time_ms")[col]
        panel[f"cs_rank_{col}"] = grp.rank(pct=True)
        panel[f"cs_z_{col}"] = (panel[col] - grp.transform("mean")) / grp.transform("std").replace(0, np.nan)
    panel["bar_interval"] = "1h"
    panel["source_panel"] = "binance_vision_monthly_plus_funding_rate"
    panel["historical_backfill_allowed"] = True
    panel["positioning_historical_allowed"] = False
    return panel.replace([np.inf, -np.inf], np.nan)


def build_symbol_panel(monthly: pd.DataFrame, symbol: str, funding: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    base, errs = build_family_hourly(monthly, symbol, TRADE_DATA_TYPE)
    errors.extend(errs)
    if base.empty:
        return base, errors
    base = base.rename(columns={"volume": "volume"})
    for data_type, prefix in PREFIX_BY_DATA_TYPE.items():
        fam, errs = build_family_hourly(monthly, symbol, data_type)
        errors.extend(errs)
        if fam.empty:
            continue
        keep = ["symbol", "open_time_ms", "open", "high", "low", "close"]
        fam = fam[[c for c in keep if c in fam.columns]].rename(
            columns={c: f"{prefix}_{c}" for c in ["open", "high", "low", "close"] if c in fam.columns}
        )
        base = base.merge(fam, on=["symbol", "open_time_ms"], how="left")
    base = merge_funding(base, funding)
    return base, errors


def sanity(panel: pd.DataFrame, errors: list[dict[str, Any]]) -> dict[str, Any]:
    symbol_summary = {}
    for symbol, part in panel.groupby("symbol"):
        part = part.sort_values("open_time_ms")
        diffs = part["open_time_ms"].diff().dropna()
        symbol_summary[symbol] = {
            "rows": int(len(part)),
            "timestamp_min": str(part["timestamp"].min()),
            "timestamp_max": str(part["timestamp"].max()),
            "gap_count": int((diffs != 3_600_000).sum()),
            "duplicate_timestamp_count": int(part.duplicated(["timestamp"]).sum()),
        }
    numeric = panel.select_dtypes(include=[np.number])
    return {
        "rows": int(len(panel)),
        "symbols": int(panel["symbol"].nunique()) if "symbol" in panel else 0,
        "columns": int(len(panel.columns)),
        "timestamp_min": str(panel["timestamp"].min()) if len(panel) else "",
        "timestamp_max": str(panel["timestamp"].max()) if len(panel) else "",
        "duplicate_key_count": int(panel.duplicated(["timestamp", "symbol"]).sum()) if len(panel) else 0,
        "symbol_summary": symbol_summary,
        "missing_rate_top20": {str(k): float(v) for k, v in numeric.isna().mean().sort_values(ascending=False).head(20).items()},
        "file_error_count": len(errors),
        "file_errors": errors[:50],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build 1h panel for A7AC primary additions from Binance Vision monthly sources.")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--monthly-tag", default=DEFAULT_MONTHLY_TAG)
    ap.add_argument("--funding-tags", nargs="+", default=DEFAULT_FUNDING_TAGS)
    ap.add_argument("--symbols", nargs="*", default=[])
    ap.add_argument("--output", default="")
    ap.add_argument("--report-tag", default="a7ac_primary_additions_1h_panel_v1")
    args = ap.parse_args()

    root = Path(args.root)
    monthly = load_monthly_manifest(root, args.monthly_tag)
    symbols = sorted({s.upper() for s in args.symbols}) if args.symbols else sorted(monthly["symbol"].astype(str).unique())
    funding = load_funding(root, args.funding_tags, symbols)
    frames = []
    errors: list[dict[str, Any]] = []
    started = utc_now()
    for i, symbol in enumerate(symbols, 1):
        frame, errs = build_symbol_panel(monthly, symbol, funding)
        errors.extend(errs)
        if not frame.empty:
            frames.append(frame)
        print(f"symbol_progress {i}/{len(symbols)} {symbol} rows={len(frame)} errors={len(errs)}", flush=True)
    if not frames:
        raise RuntimeError("no symbol frames built")
    panel = pd.concat(frames, ignore_index=True)
    panel = add_features(panel).sort_values(["timestamp", "symbol"]).reset_index(drop=True)
    output = Path(args.output) if args.output else root / "gold" / "panels" / "crypto_primary_core48_additions_1h_v1.parquet"
    output.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output, index=False, compression="zstd")
    info = sanity(panel, errors)
    info.update(
        {
            "generated_at": utc_now(),
            "started_at": started,
            "decision": "PASS_A7AC2D_PRIMARY_ADDITIONS_1H_PANEL_BUILT" if not errors else "HOLD_A7AC2D_PRIMARY_ADDITIONS_1H_PANEL_BUILT_WITH_FILE_ERRORS",
            "output": str(output),
            "output_sha256": sha256_file(output),
            "monthly_tag": args.monthly_tag,
            "funding_tags": args.funding_tags,
            "authorizes_formula_search": False,
            "authorizes_alpha_proof": False,
        }
    )
    report_dir = root / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_json = report_dir / f"{args.report_tag}.json"
    report_md = report_dir / f"{args.report_tag}.md"
    write_json(report_json, info)
    lines = [
        "# Crypto Primary Core48 Additions 1h Panel Build",
        "",
        f"- generated_at: `{info['generated_at']}`",
        f"- decision: `{info['decision']}`",
        f"- output: `{output}`",
        f"- rows: `{info['rows']}`",
        f"- symbols: `{info['symbols']}`",
        f"- timestamp_min: `{info['timestamp_min']}`",
        f"- timestamp_max: `{info['timestamp_max']}`",
        f"- duplicate_key_count: `{info['duplicate_key_count']}`",
        f"- file_error_count: `{info['file_error_count']}`",
        "",
        "This build does not authorize replay/search/alpha proof. A7AC-3 listing/survivorship and panel integrity audits remain required before experiments.",
    ]
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("output=" + str(output), flush=True)
    print("report=" + str(report_json), flush=True)
    print("decision=" + info["decision"], flush=True)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
