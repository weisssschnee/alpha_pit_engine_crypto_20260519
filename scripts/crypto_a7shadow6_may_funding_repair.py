from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
import zipfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7al2x5_evaluator_preflight_smoke import BASE_DIR  # noqa: E402
from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402
from scripts.crypto_a7ff25r6_dense_funding_state_audit import dense_ffill_and_age, shift_matrix  # noqa: E402
from scripts.crypto_a7al2l_fast_derived_replay_preflight import split_for_timestamps  # noqa: E402


DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))
DATASET = "binance_universe498_replay_1h_v2_may_funding_repair_v1_20260704"
DEFAULT_OUT_DIR = DATA_ROOT / "gold" / "features" / DATASET
DEFAULT_RAW_CACHE = DATA_ROOT / "raw" / "binance_api" / "funding_rate_may2026_repair_v1_20260704"
DEFAULT_VISION_CACHE = DATA_ROOT / "raw" / "binance_vision" / "fundingRate_may2026_repair_v1_20260704"
DEFAULT_RUNTIME = REPO / "runtime" / "a7shadow6_may_funding_repair_20260704"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SHADOW6_MAY_FUNDING_REPAIR_20260704.md"
DEFAULT_START = "2026-04-30T00:00:00Z"
DEFAULT_END = "2026-05-26T00:00:00Z"
BINANCE_FUNDING_URL = "https://fapi.binance.com/fapi/v1/fundingRate"
BINANCE_VISION_FUNDING_URL = "https://data.binance.vision/data/futures/um/monthly/fundingRate"
EXISTING_VISION_ROOTS = [
    DATA_ROOT / "raw" / "binance_vision" / "fundingRate_monthly_universe300",
    DATA_ROOT / "raw" / "binance_vision" / "fundingRate_monthly_universe500_remaining",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def millis(ts: pd.Timestamp) -> int:
    return int(ts.timestamp() * 1000)


def safe_reset(out_dir: Path) -> None:
    parent = (DATA_ROOT / "gold" / "features").resolve()
    target = out_dir.resolve()
    if out_dir.exists():
        if parent not in target.parents or DATASET not in out_dir.name:
            raise RuntimeError(f"refuse reset outside controlled dataset: {target}")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)


def vision_zip_candidates(symbol: str, month: str, vision_cache: Path) -> list[Path]:
    year = month.split("-", 1)[0]
    filename = f"{symbol}-fundingRate-{month}.zip"
    paths = [root / f"symbol={symbol}" / f"year={year}" / filename for root in EXISTING_VISION_ROOTS]
    paths.append(vision_cache / f"symbol={symbol}" / f"year={year}" / filename)
    return paths


def download_vision_zip(symbol: str, month: str, vision_cache: Path) -> tuple[Path | None, str]:
    year = month.split("-", 1)[0]
    filename = f"{symbol}-fundingRate-{month}.zip"
    out = vision_cache / f"symbol={symbol}" / f"year={year}" / filename
    if out.exists() and out.stat().st_size > 0:
        return out, ""
    out.parent.mkdir(parents=True, exist_ok=True)
    url = f"{BINANCE_VISION_FUNDING_URL}/{symbol}/{filename}"
    tmp = out.with_suffix(out.suffix + ".tmp")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AlphaFactory-A7SHADOW6/0.1"})
        with urllib.request.urlopen(req, timeout=45) as response:
            tmp.write_bytes(response.read())
        if not zipfile.is_zipfile(tmp):
            tmp.unlink(missing_ok=True)
            return None, "downloaded_file_not_zip"
        tmp.replace(out)
        return out, ""
    except Exception as exc:  # noqa: BLE001
        tmp.unlink(missing_ok=True)
        return None, repr(exc)


def normalize_funding_frame(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = {str(col).strip(): col for col in frame.columns}
    time_col = next((normalized[name] for name in ["fundingTime", "funding_time", "calc_time", "time"] if name in normalized), None)
    rate_col = next((normalized[name] for name in ["fundingRate", "funding_rate", "last_funding_rate"] if name in normalized), None)
    mark_col = next((normalized[name] for name in ["markPrice", "mark_price", "funding_mark_price"] if name in normalized), None)
    if time_col is None or rate_col is None:
        raise ValueError(f"cannot infer funding columns: {list(frame.columns)}")
    out = pd.DataFrame()
    raw_time = frame[time_col]
    numeric_time = pd.to_numeric(raw_time, errors="coerce")
    if numeric_time.notna().mean() > 0.8:
        unit = "ms" if float(numeric_time.dropna().median()) > 10_000_000_000 else "s"
        out["funding_time"] = pd.to_datetime(numeric_time, unit=unit, utc=True, errors="coerce")
    else:
        out["funding_time"] = pd.to_datetime(raw_time, utc=True, errors="coerce")
    out["funding_time"] = out["funding_time"].dt.floor("h")
    out["funding_rate_repair"] = pd.to_numeric(frame[rate_col], errors="coerce")
    out["funding_mark_price_repair"] = pd.to_numeric(frame[mark_col], errors="coerce") if mark_col is not None else np.nan
    return out.dropna(subset=["funding_time", "funding_rate_repair"])


def read_vision_zip(path: Path) -> pd.DataFrame:
    with zipfile.ZipFile(path) as zf:
        members = [name for name in zf.namelist() if not name.endswith("/")]
        if not members:
            return pd.DataFrame()
        member = members[0]
        with zf.open(member) as f:
            frame = pd.read_csv(f)
        try:
            return normalize_funding_frame(frame)
        except ValueError:
            with zf.open(member) as f:
                raw = pd.read_csv(f, header=None)
            if raw.shape[1] >= 3:
                raw = raw.iloc[:, :3].copy()
                raw.columns = ["calc_time", "funding_interval_hours", "last_funding_rate"]
            elif raw.shape[1] == 2:
                raw.columns = ["fundingTime", "fundingRate"]
            else:
                raise
            return normalize_funding_frame(raw)


def load_vision_funding(symbol: str, start: pd.Timestamp, end: pd.Timestamp, vision_cache: Path) -> tuple[pd.DataFrame, str, str]:
    frames: list[pd.DataFrame] = []
    errors: list[str] = []
    for month in ["2026-04", "2026-05"]:
        zip_path = next((path for path in vision_zip_candidates(symbol, month, vision_cache) if path.exists()), None)
        if zip_path is None:
            zip_path, error = download_vision_zip(symbol, month, vision_cache)
            if error:
                errors.append(f"{month}:{error}")
        if zip_path is None:
            continue
        try:
            frames.append(read_vision_zip(zip_path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{month}:{zip_path}:{exc!r}")
    if not frames:
        return pd.DataFrame(), "binance_vision_monthly_fundingRate", ";".join(errors)
    frame = pd.concat(frames, ignore_index=True)
    frame = frame[(frame["funding_time"] >= start) & (frame["funding_time"] <= end)]
    frame = frame.drop_duplicates("funding_time", keep="last").sort_values("funding_time")
    return frame[["funding_time", "funding_rate_repair", "funding_mark_price_repair"]], "binance_vision_monthly_fundingRate", ";".join(errors)


def fetch_rest_funding(symbol: str, start: pd.Timestamp, end: pd.Timestamp, raw_cache: Path, sleep_s: float) -> tuple[pd.DataFrame, str, str]:
    symbol_dir = raw_cache / f"symbol={symbol}"
    symbol_dir.mkdir(parents=True, exist_ok=True)
    cache_path = symbol_dir / "funding_rate_20260430_20260526.json"
    if cache_path.exists():
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        source = "cache"
        error = ""
    else:
        params = urllib.parse.urlencode(
            {
                "symbol": symbol,
                "startTime": millis(start),
                "endTime": millis(end),
                "limit": 1000,
            }
        )
        url = f"{BINANCE_FUNDING_URL}?{params}"
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
            cache_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            source = "binance_fapi_fundingRate"
            error = ""
            if sleep_s > 0:
                time.sleep(sleep_s)
        except Exception as exc:  # noqa: BLE001
            payload = []
            source = "binance_fapi_fundingRate"
            error = repr(exc)
            cache_path.write_text(json.dumps({"error": error}, indent=2, sort_keys=True), encoding="utf-8")
    if isinstance(payload, dict) and "error" in payload:
        return pd.DataFrame(), source, str(payload["error"])
    frame = pd.DataFrame(payload)
    if frame.empty:
        return frame, source, error
    frame["funding_time"] = pd.to_datetime(pd.to_numeric(frame["fundingTime"], errors="coerce"), unit="ms", utc=True)
    frame["funding_rate_repair"] = pd.to_numeric(frame["fundingRate"], errors="coerce")
    if "markPrice" in frame.columns:
        frame["funding_mark_price_repair"] = pd.to_numeric(frame["markPrice"], errors="coerce")
    else:
        frame["funding_mark_price_repair"] = np.nan
    frame = frame.dropna(subset=["funding_time", "funding_rate_repair"])
    frame = frame[(frame["funding_time"] >= start) & (frame["funding_time"] <= end)]
    frame = frame.drop_duplicates("funding_time", keep="last").sort_values("funding_time")
    return frame[["funding_time", "funding_rate_repair", "funding_mark_price_repair"]], source, error


def fetch_funding(symbol: str, start: pd.Timestamp, end: pd.Timestamp, raw_cache: Path, vision_cache: Path, sleep_s: float) -> tuple[pd.DataFrame, str, str]:
    vision, vision_source, vision_error = load_vision_funding(symbol, start, end, vision_cache)
    if not vision.empty:
        return vision, vision_source, vision_error
    rest, rest_source, rest_error = fetch_rest_funding(symbol, start, end, raw_cache, sleep_s)
    source = f"{vision_source}|{rest_source}"
    error = ";".join(part for part in [vision_error, rest_error] if part)
    return rest, source, error


def repair_symbol(
    symbol: str,
    base_dir: Path,
    out_dir: Path,
    raw_cache: Path,
    vision_cache: Path,
    start: pd.Timestamp,
    end: pd.Timestamp,
    sleep_s: float,
) -> dict[str, Any]:
    base_path = base_dir / f"symbol={symbol}" / "part.parquet"
    if not base_path.exists():
        return {"symbol": symbol, "status": "missing_base_part", "base_path": str(base_path)}
    frame = pd.read_parquet(base_path, engine="pyarrow")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame = frame.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
    if "funding_rate" not in frame.columns:
        frame["funding_rate"] = np.nan
    if "funding_mark_price" not in frame.columns:
        frame["funding_mark_price"] = np.nan

    funding, source, fetch_error = fetch_funding(symbol, start, end, raw_cache, vision_cache, sleep_s)
    before_missing = int(frame.loc[(frame["timestamp"] >= start) & (frame["timestamp"] <= end), "funding_rate"].isna().sum())
    filled_rows = 0
    event_rows = int(funding.shape[0])
    if not funding.empty:
        patch = funding.rename(columns={"funding_time": "timestamp"})
        frame = frame.merge(patch, on="timestamp", how="left")
        fill_mask = frame["funding_rate"].isna() & frame["funding_rate_repair"].notna()
        filled_rows = int(fill_mask.sum())
        frame.loc[fill_mask, "funding_rate"] = frame.loc[fill_mask, "funding_rate_repair"]
        mark_fill = frame["funding_mark_price"].isna() & frame["funding_mark_price_repair"].notna()
        frame.loc[mark_fill, "funding_mark_price"] = frame.loc[mark_fill, "funding_mark_price_repair"]
        frame["source_may_funding_repair"] = fill_mask
        frame = frame.drop(columns=["funding_rate_repair", "funding_mark_price_repair"])
    else:
        frame["source_may_funding_repair"] = False
    after_missing = int(frame.loc[(frame["timestamp"] >= start) & (frame["timestamp"] <= end), "funding_rate"].isna().sum())

    symbol_out = out_dir / f"symbol={symbol}"
    symbol_out.mkdir(parents=True, exist_ok=True)
    out_path = symbol_out / "part.parquet"
    frame.to_parquet(out_path, index=False)
    stress_mask = (frame["timestamp"] >= pd.Timestamp("2026-05-01T00:00:00Z")) & (frame["timestamp"] <= pd.Timestamp("2026-05-26T00:00:00Z"))
    return {
        "symbol": symbol,
        "status": "ok" if not fetch_error else "fetch_error",
        "fetch_source": source,
        "fetch_error": fetch_error,
        "event_rows": event_rows,
        "filled_rows": filled_rows,
        "repair_window_missing_before": before_missing,
        "repair_window_missing_after": after_missing,
        "stress_raw_funding_finite_share": float(frame.loc[stress_mask, "funding_rate"].notna().mean()) if stress_mask.any() else np.nan,
        "output_path": str(out_path),
    }


def dense_stress_audit(out_dir: Path, symbols: list[str]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    timestamps: pd.DatetimeIndex | None = None
    for symbol in symbols:
        path = out_dir / f"symbol={symbol}" / "part.parquet"
        if not path.exists():
            continue
        frame = pd.read_parquet(path, columns=["timestamp", "funding_rate", "premium_close_bps", "open_interest_mean"], engine="pyarrow")
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        frame = frame.sort_values("timestamp").drop_duplicates("timestamp")
        if timestamps is None:
            timestamps = pd.DatetimeIndex(frame["timestamp"])
        frame = frame.set_index("timestamp").reindex(timestamps)
        frames.append(frame)
    if timestamps is None or not frames:
        return pd.DataFrame()
    raw = np.vstack([pd.to_numeric(frame["funding_rate"], errors="coerce").to_numpy(dtype=np.float64) for frame in frames])
    premium = np.vstack([pd.to_numeric(frame["premium_close_bps"], errors="coerce").to_numpy(dtype=np.float64) for frame in frames])
    oi = np.vstack([pd.to_numeric(frame["open_interest_mean"], errors="coerce").to_numpy(dtype=np.float64) for frame in frames])
    dense8, _ = dense_ffill_and_age(raw, 8)
    delta8 = dense8 - shift_matrix(dense8, 24)
    split = split_for_timestamps(timestamps)
    rows = []
    for name, values in [
        ("raw_funding_rate", raw),
        ("funding_rate_state_last_ffill_8h", dense8),
        ("funding_rate_delta_state_24h_ffill_8h", delta8),
        ("premium_close_bps", premium),
        ("open_interest_mean", oi),
    ]:
        stress = split == "known_may2026_stress"
        mat = values[:, stress]
        rows.append(
            {
                "field": name,
                "split": "known_may2026_stress",
                "hour_count": int(stress.sum()),
                "finite_share": float(np.isfinite(mat).mean()) if mat.size else np.nan,
                "nonzero_share": float((np.isfinite(mat) & (np.abs(mat) > 1e-12)).mean()) if mat.size else np.nan,
                "symbol_with_any_finite": int(np.isfinite(mat).any(axis=1).sum()) if mat.size else 0,
            }
        )
    return pd.DataFrame(rows)


def build(
    base_dir: Path,
    out_dir: Path,
    raw_cache: Path,
    vision_cache: Path,
    runtime: Path,
    report: Path,
    symbol_cap: int,
    sleep_s: float,
    reset: bool,
) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    start = pd.Timestamp(DEFAULT_START)
    end = pd.Timestamp(DEFAULT_END)
    symbols = strict_symbols()[:symbol_cap]
    if reset:
        safe_reset(out_dir)
    else:
        out_dir.mkdir(parents=True, exist_ok=True)

    rows = [repair_symbol(symbol, base_dir, out_dir, raw_cache, vision_cache, start, end, sleep_s) for symbol in symbols]
    manifest_df = pd.DataFrame(rows)
    manifest_df.to_csv(runtime / "a7shadow6_symbol_repair_manifest.csv", index=False)

    dense = dense_stress_audit(out_dir, symbols)
    dense.to_csv(runtime / "a7shadow6_dense_stress_audit.csv", index=False)
    data_manifest = DATA_ROOT / "manifests" / f"{DATASET}_manifest.csv"
    data_report = DATA_ROOT / "reports" / f"{DATASET}.json"
    data_manifest.parent.mkdir(parents=True, exist_ok=True)
    data_report.parent.mkdir(parents=True, exist_ok=True)
    manifest_df.to_csv(data_manifest, index=False)

    fetch_errors = int(manifest_df["fetch_error"].astype(str).ne("").sum()) if "fetch_error" in manifest_df else len(symbols)
    ok_symbols = int(manifest_df["status"].eq("ok").sum()) if "status" in manifest_df else 0
    delta_row = dense[dense["field"].eq("funding_rate_delta_state_24h_ffill_8h")]
    delta_stress_share = float(delta_row["finite_share"].iloc[0]) if not delta_row.empty else np.nan
    decision = (
        "PASS_A7SHADOW6_MAY_FUNDING_REPAIR_PANEL_BUILT"
        if ok_symbols == len(symbols) and fetch_errors == 0 and delta_stress_share >= 0.95
        else "HOLD_A7SHADOW6_MAY_FUNDING_REPAIR_INCOMPLETE"
    )
    manifest = {
        "stage": "A7SHADOW-6",
        "generated_at": now_utc(),
        "decision": decision,
        "base_panel_root": str(base_dir),
        "output_panel_root": str(out_dir),
        "raw_cache_root": str(raw_cache),
        "vision_cache_root": str(vision_cache),
        "symbol_count": len(symbols),
        "ok_symbol_count": ok_symbols,
        "fetch_error_count": fetch_errors,
        "repair_start": DEFAULT_START,
        "repair_end": DEFAULT_END,
        "dense_delta_stress_finite_share": delta_stress_share,
        "data_manifest": str(data_manifest),
        "runtime": str(runtime),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_shadow_book": False,
        "authorizes_a7shadow5_rerun": decision.startswith("PASS"),
        "authorizes_a7shadow4_rerun": decision.startswith("PASS"),
    }
    write_json(runtime / "a7shadow6_manifest.json", manifest)
    write_json(data_report, manifest)

    lines = [
        "# CRYPTO A7SHADOW6 May Funding Repair",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This stage builds a separate evaluator base panel with repaired Binance funding-rate events for the May 2026 stress window. It does not run search or authorize any trading stage.",
        "",
        "## Counts",
        "",
        f"- symbol_count: `{manifest['symbol_count']}`",
        f"- ok_symbol_count: `{manifest['ok_symbol_count']}`",
        f"- fetch_error_count: `{manifest['fetch_error_count']}`",
        f"- dense_delta_stress_finite_share: `{manifest['dense_delta_stress_finite_share']}`",
        f"- output_panel_root: `{manifest['output_panel_root']}`",
        "",
        "## Dense Stress Audit",
        "",
        md_table(dense, 40),
        "",
        "## Symbol Repair Manifest",
        "",
        md_table(manifest_df, 40),
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", default=str(BASE_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--raw-cache", default=str(DEFAULT_RAW_CACHE))
    parser.add_argument("--vision-cache", default=str(DEFAULT_VISION_CACHE))
    parser.add_argument("--runtime", default=str(DEFAULT_RUNTIME))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--symbol-cap", type=int, default=96)
    parser.add_argument("--sleep-s", type=float, default=0.05)
    parser.add_argument("--no-reset", action="store_true")
    args = parser.parse_args()
    build(
        Path(args.base_dir),
        Path(args.out_dir),
        Path(args.raw_cache),
        Path(args.vision_cache),
        Path(args.runtime),
        Path(args.report),
        args.symbol_cap,
        args.sleep_s,
        not args.no_reset,
    )


if __name__ == "__main__":
    main()
