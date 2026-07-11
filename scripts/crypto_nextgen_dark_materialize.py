from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from alphafactory_crypto.nextgen_fabric import materialize_states


SAFE_COLUMNS = (
    "symbol", "timestamp", "feature_available_time", "funding_rate", "mark_trade_basis_bps",
    "mark_index_basis_bps", "open_interest_value_last", "kline_taker_buy_quote_share",
    "trade_quote_volume", "trade_close",
)
FORBIDDEN_TOKENS = ("forward", "fwd_", "reward", "pnl", "sharpe", "sortino")
CORE12_PANEL = Path("G:/AlphaFactory_CryptoData/gold/panels/crypto_core12_1h_v1_pre_forward_refresh_20260519.parquet")
FEATURE_ROOT = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v3_patch_age_20260613")
CUTOFF = pd.Timestamp("2026-04-30T23:00:00Z")
START = pd.Timestamp("2024-01-01T00:00:00Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_roles(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["field_name"]: row["input_role"] for row in csv.DictReader(handle)}


def load_core12_observations(feature_root: Path, core12_panel: Path) -> tuple[pd.DataFrame, list[Path]]:
    if any(any(token in column.lower() for token in FORBIDDEN_TOKENS) for column in SAFE_COLUMNS):
        raise PermissionError("forbidden performance column requested")
    symbols = sorted(pq.read_table(core12_panel, columns=["symbol"]).column("symbol").unique().to_pylist())
    if len(symbols) != 12:
        raise ValueError(f"funding production scope requires core12, got {len(symbols)} symbols")
    files = [feature_root / f"symbol={symbol}" / "part.parquet" for symbol in symbols]
    if any(not path.exists() for path in files):
        raise FileNotFoundError("core12 feature partition missing")
    pieces = []
    for path in files:
        piece = pq.read_table(path, columns=list(SAFE_COLUMNS)).to_pandas()
        piece["timestamp"] = pd.to_datetime(piece["timestamp"], utc=True)
        piece = piece[(piece["timestamp"] >= START) & (piece["timestamp"] <= CUTOFF)]
        pieces.append(piece)
    frame = pd.concat(pieces, ignore_index=True)
    frame = frame.rename(columns={"feature_available_time": "observable_time"})
    frame["observable_time"] = pd.to_datetime(frame["observable_time"], utc=True)
    frame["maturity_time"] = frame["observable_time"]
    return frame, files


def run(output_root: Path, manifest_path: Path, field_registry: Path) -> dict[str, object]:
    frame, files = load_core12_observations(FEATURE_ROOT, CORE12_PANEL)
    release_parts = [sha256_file(path) for path in files]
    release_hash = hashlib.sha256("".join(sorted(release_parts)).encode()).hexdigest().upper()
    registry_hash = sha256_file(field_registry)
    result = materialize_states(
        frame, read_roles(field_registry), source_release_hash=release_hash,
        field_registry_hash=registry_hash,
        production_scope="BINANCE_UM_CORE12_2024-01-01_THROUGH_2026-04-30",
    )
    output_root.mkdir(parents=True, exist_ok=True)
    data_path = output_root / f"{result.artifact_hash}.parquet"
    result.frame.to_parquet(data_path, index=False)
    manifest: dict[str, object] = {
        "artifact_id": "NEXTGEN-DARK-FEATURE-STATE-MATERIALIZATION-V1",
        "artifact_hash": result.artifact_hash,
        "content_sha256": sha256_file(data_path),
        "data_path": str(data_path.resolve()).replace("\\", "/"),
        "rows": len(result.frame),
        "symbols": int(result.frame["symbol"].nunique()),
        "start_utc": result.frame["timestamp"].min().isoformat(),
        "end_utc": result.frame["timestamp"].max().isoformat(),
        "source_release_hash": release_hash,
        "field_registry_hash": registry_hash,
        "columns_read": list(SAFE_COLUMNS),
        "forbidden_performance_columns_read": False,
        "availability": [item.__dict__ for item in result.availability],
        "lineage": dict(result.lineage),
        "search_started": False,
        "performance_evaluated": False,
        "forward_read": False,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize isolated NEXTGEN-DARK observable state artifacts")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--field-registry", type=Path,
        default=Path("runtime/a7input0_v2_field_roles_20260711/a7input0_v2_field_role_registry.csv"),
    )
    args = parser.parse_args()
    print(json.dumps(run(args.output_root, args.manifest, args.field_registry), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
