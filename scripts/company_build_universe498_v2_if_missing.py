from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))
OLD_DIR = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v1_20260525"
PATCH_PARQUET_DIR = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_may2026_patch_v1_20260527"
PATCH_STDLIB_DIR = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_may2026_patch_stdlib_v1_20260527"
OUT_DIR = DATA_ROOT / "gold" / "features" / "binance_universe498_replay_1h_v2_20260527"
MANIFEST = DATA_ROOT / "manifests" / "binance_universe498_replay_1h_v2_20260527_manifest.csv"
COVERAGE = DATA_ROOT / "manifests" / "binance_universe498_replay_1h_v2_20260527_coverage.csv"
REPORT = DATA_ROOT / "reports" / "binance_universe498_replay_1h_v2_20260527.json"
DATASET = "binance_universe498_replay_1h_v2_20260527"

NUMERIC_OI = [
    "open_interest_last",
    "open_interest_mean",
    "open_interest_value_last",
    "open_interest_value_mean",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_part(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path, compression="gzip")


def part_map(root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    if not root.exists():
        return out
    for part in root.glob("symbol=*/part.*"):
        if part.name not in {"part.parquet", "part.csv.gz"}:
            continue
        symbol = part.parent.name.split("=", 1)[1]
        out[symbol] = part
    return out


def inf_count(frame: pd.DataFrame) -> int:
    nums = frame.select_dtypes(include=["number"])
    if nums.empty:
        return 0
    return int(np.isinf(nums.to_numpy()).sum())


def safe_reset() -> None:
    parent = (DATA_ROOT / "gold" / "features").resolve()
    target = OUT_DIR.resolve()
    if OUT_DIR.exists():
        if parent not in target.parents or DATASET not in OUT_DIR.name:
            raise RuntimeError(f"refuse reset outside controlled dataset: {target}")
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    if OUT_DIR.exists() and any(OUT_DIR.glob("symbol=*/part.parquet")) and MANIFEST.exists():
        print(
            json.dumps(
                {
                    "decision": "V2_ALREADY_PRESENT",
                    "gold_dir": str(OUT_DIR),
                    "manifest": str(MANIFEST),
                },
                indent=2,
            )
        )
        return

    old = part_map(OLD_DIR)
    patch = part_map(PATCH_PARQUET_DIR)
    if not patch:
        patch = part_map(PATCH_STDLIB_DIR)
    if not old:
        raise SystemExit(f"missing old v1 parts: {OLD_DIR}")
    if not patch:
        raise SystemExit(f"missing May patch parts: {PATCH_PARQUET_DIR} or {PATCH_STDLIB_DIR}")

    safe_reset()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    coverage_rows = []
    total_rows = 0
    duplicate_total = 0
    inf_total = 0
    gap_total = 0
    for symbol in sorted(set(old) | set(patch)):
        frames = []
        if symbol in old:
            frames.append(read_part(old[symbol]))
        if symbol in patch:
            frames.append(read_part(patch[symbol]))
        if not frames:
            continue
        frame = pd.concat(frames, ignore_index=True, sort=False)
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True)
        for col in ["feature_available_time", "execution_time"]:
            if col in frame.columns:
                frame[col] = pd.to_datetime(frame[col], errors="coerce", utc=True)
        frame = frame.dropna(subset=["timestamp"]).sort_values("timestamp")
        if "symbol" not in frame.columns:
            frame["symbol"] = symbol
        frame = frame.drop_duplicates(["symbol", "timestamp"], keep="last").sort_values("timestamp")

        out_dir = OUT_DIR / f"symbol={symbol}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "part.parquet"
        frame.to_parquet(out_path, index=False)

        duplicate_count = int(frame.duplicated(["symbol", "timestamp"]).sum())
        n_inf = inf_count(frame)
        gap_count = int((frame["timestamp"].diff().dropna() > pd.Timedelta(hours=1)).sum())
        total_rows += len(frame)
        duplicate_total += duplicate_count
        inf_total += n_inf
        gap_total += gap_count
        oi_cov = {f"{col}_coverage": float(frame[col].notna().mean()) for col in NUMERIC_OI if col in frame.columns}
        manifest_rows.append(
            {
                "symbol": symbol,
                "status": "ok" if duplicate_count == 0 and n_inf == 0 else "warn",
                "rows": len(frame),
                "min_timestamp": frame["timestamp"].min(),
                "max_timestamp": frame["timestamp"].max(),
                "duplicate_timestamp_count": duplicate_count,
                "inf_cell_count": n_inf,
                "gap_hours_gt_1": gap_count,
                "missing_metrics_rows": int((~frame["source_metrics"]).sum()) if "source_metrics" in frame.columns else None,
                "missing_market_funding_rows": int((~frame["source_market_funding"]).sum())
                if "source_market_funding" in frame.columns
                else None,
                "output_path": str(out_path),
                **oi_cov,
            }
        )
        coverage_rows.append(
            {
                "symbol": symbol,
                "rows": len(frame),
                "trade_start": frame["timestamp"].min(),
                "trade_end": frame["timestamp"].max(),
                "metrics_coverage": float(frame["source_metrics"].mean()) if "source_metrics" in frame.columns else np.nan,
                "market_funding_coverage": float(frame["source_market_funding"].mean())
                if "source_market_funding" in frame.columns
                else np.nan,
                **oi_cov,
            }
        )

    manifest = pd.DataFrame(manifest_rows)
    coverage = pd.DataFrame(coverage_rows)
    manifest.to_csv(MANIFEST, index=False)
    coverage.to_csv(COVERAGE, index=False)
    report = {
        "dataset": DATASET,
        "generated_at_utc": utc_now(),
        "decision": "BINANCE_UNIVERSE498_REPLAY_BASE_EXTENDED_TO_MAY_PATCH",
        "symbols": int(manifest["symbol"].nunique()) if not manifest.empty else 0,
        "rows": int(total_rows),
        "min_timestamp": str(manifest["min_timestamp"].min()) if not manifest.empty else None,
        "max_timestamp": str(manifest["max_timestamp"].max()) if not manifest.empty else None,
        "duplicate_timestamp_count": int(duplicate_total),
        "inf_cell_count": int(inf_total),
        "gap_hours_gt_1": int(gap_total),
        "manifest": str(MANIFEST),
        "coverage": str(COVERAGE),
        "gold_dir": str(OUT_DIR),
        "source_old_dir": str(OLD_DIR),
        "source_patch_dir": str(PATCH_PARQUET_DIR if PATCH_PARQUET_DIR.exists() else PATCH_STDLIB_DIR),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
