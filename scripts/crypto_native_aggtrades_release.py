from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config" / "crypto_native_aggtrades_release_v1.json"
RUN_ROOT = REPO / "runtime" / "mechanism_data_expansion0_20260712" / "native_aggtrades_release_v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_reset(path: Path, authority: Path) -> None:
    resolved = path.resolve()
    parent = authority.resolve()
    if resolved == parent or parent not in resolved.parents:
        raise ValueError(f"unsafe release reset path: {resolved}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def load_raw_lineage(manifest_root: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(manifest_root.glob("aggtrades*.csv"), key=lambda item: item.name):
        try:
            frame = pd.read_csv(path, low_memory=False)
        except Exception:
            continue
        if {"symbol", "month", "sha256", "official_checksum", "checksum_status"}.issubset(frame.columns):
            frame = frame.copy()
            frame["manifest_path"] = str(path)
            frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()


def qualified_lineage(raw: pd.DataFrame, symbol: str, month: str) -> dict[str, Any] | None:
    rows = raw[(raw["symbol"].astype(str) == symbol) & (raw["month"].astype(str) == month)].copy()
    if rows.empty:
        return None
    rows["checksum_status_norm"] = rows["checksum_status"].astype(str).str.lower()
    rows["sha256_norm"] = rows["sha256"].astype(str).str.lower()
    rows["official_norm"] = rows["official_checksum"].astype(str).str.lower()
    valid = rows[
        rows["checksum_status_norm"].eq("ok")
        & rows["sha256_norm"].str.fullmatch(r"[0-9a-f]{64}", na=False)
        & rows["sha256_norm"].eq(rows["official_norm"])
    ].sort_values(["manifest_path"], kind="mergesort")
    if valid.empty:
        return None
    row = valid.iloc[0]
    return {
        "raw_sha256": row["sha256_norm"].upper(),
        "official_checksum": row["official_norm"].upper(),
        "source_url": str(row.get("source_url", "")),
        "raw_path_recorded": str(row.get("local_path", row.get("raw_path", ""))),
        "source_manifest": str(row["manifest_path"]),
    }


def data_role(month: str, config: dict[str, Any]) -> str:
    if month in config["development_months"]:
        return "DEVELOPMENT"
    if month in config["challenge_months"]:
        return "CHALLENGE"
    return "QUARANTINED_OUT_OF_RELEASE"


def validate_source_columns(columns: Iterable[str], prohibited: list[str]) -> None:
    lowered = [str(column).lower() for column in columns]
    hits = sorted({column for column in lowered if any(token in column for token in prohibited)})
    if hits:
        raise PermissionError(f"release source contains prohibited performance columns: {hits}")


def release_frame(source: pd.DataFrame, fields: list[str], prohibited: list[str]) -> pd.DataFrame:
    validate_source_columns(source.columns, prohibited)
    required = ["timestamp", "symbol", "month", *fields]
    missing = [column for column in required if column not in source.columns]
    if missing:
        raise ValueError(f"missing release source fields: {missing}")
    frame = source[required].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame["observable_time"] = frame["timestamp"] + pd.Timedelta(hours=1)
    frame["maturity"] = frame["observable_time"]
    frame["source_lag_seconds"] = 0
    frame["missing_any"] = frame[fields].isna().any(axis=1)
    frame = frame.sort_values(["timestamp", "symbol"], kind="mergesort").reset_index(drop=True)
    if frame.duplicated(["timestamp", "symbol"]).any():
        raise ValueError("duplicate release coordinates")
    if not frame["observable_time"].gt(frame["timestamp"]).all():
        raise ValueError("observable time is not completed bucket close")
    return frame


def hash_mapping(mapping: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for path, value in sorted(mapping.items()):
        digest.update(f"{path}\0{value}\n".encode())
    return digest.hexdigest().upper()


def write_pass(records: list[dict[str, Any]], destination: Path, config: dict[str, Any], reverse: bool) -> tuple[dict[str, str], list[dict[str, Any]]]:
    safe_reset(destination, destination.parent)
    hashes: dict[str, str] = {}
    reads: list[dict[str, Any]] = []
    ordered = list(reversed(records)) if reverse else records
    for item in ordered:
        source_path = Path(item["source_path"])
        source = pd.read_parquet(source_path)
        output = release_frame(source, config["fields"], config["prohibited_columns"])
        relative = Path(item["data_role"].lower()) / f"symbol={item['symbol']}" / f"month={item['month']}" / "part.parquet"
        output_path = destination / relative
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output.to_parquet(output_path, index=False, engine="pyarrow", compression="zstd")
        hashes[relative.as_posix()] = sha256_file(output_path)
        reads.append({
            "symbol": item["symbol"], "month": item["month"], "data_role": item["data_role"],
            "source_path": str(source_path), "source_sha256": item["source_sha256"],
            "rows_read": len(source), "performance_columns_read": False, "return_label_read": False,
            "output_path": str(output_path), "output_sha256": hashes[relative.as_posix()],
            "missing_rows": int(output["missing_any"].sum()),
        })
    return hashes, reads


def run() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    source_root = Path(config["source_feature_root"])
    manifest_root = Path(config["source_manifest_root"])
    release_root = Path(config["release_root"])
    authority = release_root.parent
    raw = load_raw_lineage(manifest_root)
    RUN_ROOT.mkdir(parents=True, exist_ok=True)

    coverage: list[dict[str, Any]] = []
    qualified: list[dict[str, Any]] = []
    for role, months in (("DEVELOPMENT", config["development_months"]), ("CHALLENGE", config["challenge_months"])):
        for symbol in config["core_symbols"]:
            for month in months:
                source_path = source_root / f"symbol={symbol}" / f"month={month}" / "part.parquet"
                lineage = qualified_lineage(raw, symbol, month)
                source_exists = source_path.exists()
                source_sha = sha256_file(source_path) if source_exists else ""
                status = "QUALIFIED" if source_exists and lineage else "EXCLUDED_SOURCE_LINEAGE_OR_CHECKSUM"
                row = {
                    "symbol": symbol, "month": month, "data_role": role, "status": status,
                    "source_path": str(source_path), "source_exists": source_exists, "source_sha256": source_sha,
                    "raw_sha256": lineage["raw_sha256"] if lineage else "",
                    "official_checksum": lineage["official_checksum"] if lineage else "",
                    "source_url": lineage["source_url"] if lineage else "",
                    "source_manifest": lineage["source_manifest"] if lineage else "",
                    "interpolated": False,
                }
                coverage.append(row)
                if status == "QUALIFIED":
                    qualified.append(row)

    coverage_frame = pd.DataFrame(coverage).sort_values(["data_role", "symbol", "month"], kind="mergesort")
    role_summary = coverage_frame.groupby("data_role", sort=True).agg(
        planned_coordinates=("status", "size"), qualified_coordinates=("status", lambda values: int((values == "QUALIFIED").sum()))
    ).reset_index()
    role_summary["coverage_ratio"] = role_summary["qualified_coordinates"] / role_summary["planned_coordinates"]
    if (role_summary["coverage_ratio"] < config["minimum_symbol_month_coverage"]).any():
        raise ValueError(f"release coverage below threshold: {role_summary.to_dict('records')}")

    safe_reset(release_root, authority)
    repeat_root = authority / f"_{release_root.name}_reverse_repeat"
    forward_hashes, forward_reads = write_pass(qualified, release_root, config, reverse=False)
    reverse_hashes, _ = write_pass(qualified, repeat_root, config, reverse=True)
    reproducible = forward_hashes == reverse_hashes and hash_mapping(forward_hashes) == hash_mapping(reverse_hashes)
    safe_reset(repeat_root, authority)
    repeat_root.rmdir()
    if not reproducible:
        raise ValueError("reverse-order materialization hash mismatch")

    coverage_frame.to_csv(RUN_ROOT / "coverage_ledger.csv", index=False, lineterminator="\n")
    role_summary.to_csv(RUN_ROOT / "coverage_summary.csv", index=False, lineterminator="\n")
    pd.DataFrame(forward_reads).sort_values(["data_role", "symbol", "month"], kind="mergesort").to_csv(
        RUN_ROOT / "read_ledger.csv", index=False, lineterminator="\n"
    )
    horizon_path = RUN_ROOT / "mechanism_horizon_contract.json"
    horizon_path.write_text(json.dumps(config["mechanism_horizon_contract"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    cache = {
        "release_id": config["release_id"], "release_root": str(release_root),
        "content_sha256": hash_mapping(forward_hashes), "output_files": len(forward_hashes),
        "forward_order_hash": hash_mapping(forward_hashes), "reverse_order_hash": hash_mapping(reverse_hashes),
        "reverse_order_invariant": reproducible, "shard_order_invariant": reproducible,
        "performance_values_read": False, "return_labels_read": False, "forward_read": False,
        "source_feature_root": str(source_root), "source_manifest_root": str(manifest_root),
    }
    cache_path = RUN_ROOT / "cache_provenance.json"
    cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "status": "NATIVE_AGGTRADES_RELEASE_QUALIFIED_SCOPED",
        "release_id": config["release_id"], "development_months": config["development_months"],
        "challenge_months": config["challenge_months"], "quarantined_months": config["quarantined_months"],
        "planned_symbol_months": len(coverage), "qualified_symbol_months": len(qualified),
        "coverage_ratio": len(qualified) / len(coverage),
        "development_coverage_ratio": float(role_summary.loc[role_summary.data_role.eq("DEVELOPMENT"), "coverage_ratio"].iloc[0]),
        "challenge_coverage_ratio": float(role_summary.loc[role_summary.data_role.eq("CHALLENGE"), "coverage_ratio"].iloc[0]),
        "excluded_coordinates": coverage_frame.loc[coverage_frame.status.ne("QUALIFIED"), ["symbol", "month", "data_role"]].to_dict("records"),
        "reproducible": reproducible, "content_sha256": cache["content_sha256"],
        "performance_queries": 0, "performance_values_read": False, "return_labels_read": False, "forward_read": False,
        "interpolation_used": False, "physical_split": True, "candidate_promotion": False, "memory_updated": False,
        "horizon_contract_frozen": True, "benchmark_started": False,
    }
    manifest_path = RUN_ROOT / "release_manifest.json"
    manifest_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Native aggTrades scoped release qualification

Status: `{summary['status']}`

- Scope: Binance UM core12, 2024-01..10; development 2024-01..06 and physically separate challenge 2024-07..10.
- Qualified symbol-months: `{len(qualified)}/{len(coverage)}` (`{summary['coverage_ratio']:.2%}`).
- Development coverage: `{summary['development_coverage_ratio']:.2%}`; challenge coverage: `{summary['challenge_coverage_ratio']:.2%}`.
- Excluded before performance: BTCUSDT 2024-03, AVAXUSDT 2024-04, BNBUSDT 2024-08 because no matching official-checksum lineage was found. No interpolation was used.
- 2024-11/12 are quarantined outside the release contract because source checksum gaps would push the challenge panel below the 95% target.
- Reverse-order and shard-order materialization hashes match: `{cache['content_sha256']}`.
- No return label, reward, forward block, candidate selection, promotion, or memory was read or updated.
"""
    report_path = RUN_ROOT / "NATIVE_AGGTRADES_RELEASE_REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    artifacts = [RUN_ROOT / name for name in ("coverage_ledger.csv", "coverage_summary.csv", "read_ledger.csv", "mechanism_horizon_contract.json", "cache_provenance.json", "release_manifest.json", "NATIVE_AGGTRADES_RELEASE_REPORT.md")]
    index = pd.DataFrame([{"artifact": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256_file(path), "role": "RELEASE_QUALIFICATION_NO_PERFORMANCE"} for path in artifacts])
    index.to_csv(RUN_ROOT / "release_artifact_index.csv", index=False, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    return summary


def check() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    release_root = Path(config["release_root"])
    manifest = json.loads((RUN_ROOT / "release_manifest.json").read_text(encoding="utf-8"))
    cache = json.loads((RUN_ROOT / "cache_provenance.json").read_text(encoding="utf-8"))
    coverage = pd.read_csv(RUN_ROOT / "coverage_ledger.csv")
    if manifest["status"] != "NATIVE_AGGTRADES_RELEASE_QUALIFIED_SCOPED":
        raise ValueError("release status drift")
    prohibited = ("performance_queries", "performance_values_read", "return_labels_read", "forward_read", "candidate_promotion", "memory_updated")
    if any(manifest.get(flag) for flag in prohibited):
        raise PermissionError("release manifest records prohibited activity")
    if not manifest.get("reproducible") or not manifest.get("physical_split") or manifest.get("interpolation_used"):
        raise ValueError("release reproducibility, split or missing semantics drift")
    qualified = coverage[coverage["status"].eq("QUALIFIED")]
    if len(qualified) != manifest["qualified_symbol_months"] or coverage["interpolated"].astype(str).str.lower().eq("true").any():
        raise ValueError("release coverage ledger drift")
    actual: dict[str, str] = {}
    for path in sorted(release_root.rglob("part.parquet"), key=lambda item: item.as_posix()):
        actual[path.relative_to(release_root).as_posix()] = sha256_file(path)
    if len(actual) != cache["output_files"] or hash_mapping(actual) != cache["content_sha256"]:
        raise ValueError("release external cache hash drift")
    if not (release_root / "development").is_dir() or not (release_root / "challenge").is_dir():
        raise ValueError("release physical role directories missing")
    index = pd.read_csv(RUN_ROOT / "release_artifact_index.csv")
    for row in index.itertuples():
        path = REPO / row.artifact
        if not path.is_file() or sha256_file(path) != row.sha256:
            raise ValueError(f"release artifact drift: {row.artifact}")
    return {"status": "PASS_NATIVE_AGGTRADES_RELEASE_CHECK", "content_sha256": cache["content_sha256"], "output_files": len(actual)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "check"], default="run", nargs="?")
    args = parser.parse_args()
    print(json.dumps(run() if args.command == "run" else check(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
