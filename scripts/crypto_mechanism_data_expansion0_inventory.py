from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config" / "crypto_mechanism_data_expansion0_v1.json"
DEFAULT_ROOT = REPO / "runtime" / "mechanism_data_expansion0_20260712"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate_inventory_manifest(payload: dict[str, Any]) -> None:
    if payload.get("performance_queries") != 0:
        raise PermissionError("inventory used performance queries")
    if payload.get("row_data_read") is not False:
        raise PermissionError("inventory read row data")
    if payload.get("sealed_paths_footer_read") is not False:
        raise PermissionError("inventory read sealed metadata")
    if not payload.get("reproducible"):
        raise ValueError("inventory is not reproducible")


def path_role(path: str, tokens: list[str]) -> str:
    lowered = path.lower().replace("\\", "/")
    return "INELIGIBLE_EVALUATION_OR_SHORT_PROBE" if any(token.lower() in lowered for token in tokens) else "INVENTORY_ELIGIBLE"


def choose_first_release(registry: pd.DataFrame) -> str:
    eligible = registry[
        registry["inventory_status"].eq("DISCOVERED_REQUIRES_RELEASE_QUALIFICATION")
        & registry["physical_split_possible"].eq(True)
    ]
    if eligible.empty:
        return "NONE"
    ordered = eligible.sort_values(["release_priority", "source_id"], kind="mergesort")
    return str(ordered.iloc[0]["source_id"])


def source_registry(local: pd.DataFrame, pc1: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    def match(frame: pd.DataFrame, family: str, contains: str = "") -> pd.DataFrame:
        selected = frame[frame["data_family"].eq(family)]
        if contains:
            selected = selected[selected["dataset_root"].str.contains(contains, case=False, regex=False, na=False)]
        return selected

    pc1_bbo = match(pc1, "BOOKTICKER_BBO", "bookticker_multires_top50")
    local_agg = match(local, "AGG_TRADES", "aggtrades_package_a_raw")
    cross = local[local["venue"].isin(["OKX", "BYBIT"])]
    forced = match(local, "LIQUIDATION_FORCE_ORDER")
    depth = match(local, "ORDER_BOOK_DEPTH")
    options = pd.concat([match(local, "OPTIONS"), match(pc1, "OPTIONS")], ignore_index=True)

    def total(frame: pd.DataFrame, column: str) -> int:
        return int(pd.to_numeric(frame[column], errors="coerce").fillna(0).sum()) if not frame.empty else 0

    def months(frame: pd.DataFrame) -> list[str]:
        values: set[str] = set()
        for value in frame.get("months", pd.Series(dtype=str)).dropna().astype(str):
            values.update(item for item in value.split("|") if item)
        return sorted(values)

    records = [
        {
            "source_id": "CROSS_VENUE_HISTORICAL_PRICE_FLOW", "mechanism_family": "CROSS_VENUE_PRICE_DISCOVERY",
            "source": "OKX/BYBIT local REST probes and short clean panels", "venue": "OKX|BYBIT", "market_type": "PERPETUAL",
            "symbol_scope": "short-probe only", "start": min(months(cross), default=""), "end": max(months(cross), default=""),
            "frequency": "mixed 1h/snapshot", "row_count": "METADATA_SAMPLE_ONLY", "fields": "funding|mark|OI|taker|snapshot",
            "event_time": "present but source-specific", "source_observed_time": "query_time where present", "publication_delay": "UNQUALIFIED",
            "coverage": f"{total(cross, 'files')} files; only 30d/90d/May probes", "file_format": "parquet/json/csv",
            "provenance": "G:/AlphaFactory_CryptoData/raw/source_probes and silver/cross_exchange",
            "licensing_access": "internal copy; license review required", "contains_future_revisions": "UNKNOWN",
            "physical_split_possible": False, "data_role": "SPENT_OR_RECENT_DIAGNOSTIC_ONLY",
            "inventory_status": "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE", "release_priority": 90,
            "decision": "UNAVAILABLE_NO_SOURCE", "blocker": "all observed non-Binance venue data are short recent/May probes; sealed blocks cannot be used",
        },
        {
            "source_id": "BINANCE_UM_NATIVE_AGGTRADES_CORE12_HISTORY", "mechanism_family": "NATIVE_TRADE_FLOW_MICROSTRUCTURE",
            "source": "Binance Vision monthly aggTrades archives", "venue": "BINANCE", "market_type": "UM_PERPETUAL",
            "symbol_scope": f"observed up to {int(local_agg['symbol_count'].max()) if not local_agg.empty else 0} symbols",
            "start": min(months(local_agg), default=""), "end": max(months(local_agg), default=""), "frequency": "native event",
            "row_count": "NOT_READ_IN_INVENTORY", "fields": "aggregate trade id|price|quantity|first/last trade id|event time|buyer maker",
            "event_time": "native aggregate-trade event time", "source_observed_time": "event receipt/public archive availability requires qualification",
            "publication_delay": "REQUIRES_SOURCE_CONTRACT", "coverage": f"{total(local_agg, 'files')} raw archives; {len(months(local_agg))} observed months",
            "file_format": "zip/csv", "provenance": "Binance Vision historical archive internal copy",
            "licensing_access": "public archive internal copy; terms review required", "contains_future_revisions": "checksum replacement risk to audit",
            "physical_split_possible": True, "data_role": "INVENTORY_ONLY_NO_PERFORMANCE",
            "inventory_status": "DISCOVERED_REQUIRES_RELEASE_QUALIFICATION", "release_priority": 1,
            "decision": "HOLD_FOR_MORE_DATA", "blocker": "must verify core12 symbol-month coverage, checksums, observable time and physical development/challenge split",
        },
        {
            "source_id": "BINANCE_UM_BBO_FULL_2024", "mechanism_family": "NATIVE_BBO_MICROSTRUCTURE",
            "source": "Binance Vision bookTicker", "venue": "BINANCE", "market_type": "UM_PERPETUAL",
            "symbol_scope": f"Jan max {int(pc1_bbo['symbol_count'].max()) if not pc1_bbo.empty else 0}; accepted scope core11",
            "start": min(months(pc1_bbo), default=""), "end": max(months(pc1_bbo), default=""), "frequency": "15m/30m/1h aggregates",
            "row_count": "14208 previously qualified scoped rows", "fields": "bid|ask|bid quantity|ask quantity|spread|mid|quote imbalance",
            "event_time": "native update aggregated to bucket", "source_observed_time": "bucket close", "publication_delay": "bucket close",
            "coverage": "82.22% core12 coordinates in 2024-01/02; one-symbol March fragment; no full-year pack",
            "file_format": "csv.gz/parquet", "provenance": "PC1 AlphaFactory_CryptoData Binance Vision pullback",
            "licensing_access": "public archive internal copy; terms review required", "contains_future_revisions": "NO_IN_SCOPED_RELEASE",
            "physical_split_possible": False, "data_role": "SCOPED_BBO_ONLY_NO_EXTRAPOLATION",
            "inventory_status": "HOLD_FOR_FULL_YEAR_ACQUISITION", "release_priority": 20,
            "decision": "HOLD_FOR_MORE_DATA", "blocker": "full-2024 core12 symbol-month coverage >=95% is absent; BBO is not multi-level depth",
        },
        {
            "source_id": "HISTORICAL_MULTI_LEVEL_ORDER_BOOK", "mechanism_family": "NATIVE_ORDER_BOOK_DEPTH",
            "source": "none verified", "venue": "NONE", "market_type": "NONE", "symbol_scope": "NONE", "start": "", "end": "",
            "frequency": "NONE", "row_count": "0", "fields": "NONE", "event_time": "NONE", "source_observed_time": "NONE",
            "publication_delay": "NONE", "coverage": f"{total(depth, 'files')} local files are May snapshots/probes only",
            "file_format": "NONE_ELIGIBLE", "provenance": "inventory", "licensing_access": "NONE", "contains_future_revisions": "N/A",
            "physical_split_possible": False, "data_role": "DISABLED_NO_APPROVED_SOURCE",
            "inventory_status": "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE", "release_priority": 91,
            "decision": "UNAVAILABLE_NO_SOURCE", "blocker": "no historical snapshots/deltas; top-of-book must not be relabelled as depth",
        },
        {
            "source_id": "HISTORICAL_LIQUIDATION_FORCE_ORDER", "mechanism_family": "FORCED_FLOW_LIQUIDATION",
            "source": "none verified", "venue": "NONE", "market_type": "NONE", "symbol_scope": "NONE", "start": "", "end": "",
            "frequency": "NONE", "row_count": "0", "fields": "NONE", "event_time": "NONE", "source_observed_time": "NONE",
            "publication_delay": "NONE", "coverage": f"{total(forced, 'files')} local paths are May OKX probe responses only",
            "file_format": "NONE_ELIGIBLE", "provenance": "inventory", "licensing_access": "NONE", "contains_future_revisions": "N/A",
            "physical_split_possible": False, "data_role": "DISABLED_NO_APPROVED_SOURCE",
            "inventory_status": "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE", "release_priority": 92,
            "decision": "UNAVAILABLE_NO_SOURCE", "blocker": "current API fields or short probes do not prove an historical source; proxy substitution forbidden",
        },
        {
            "source_id": "HISTORICAL_OPTIONS_EXPECTATION_STATE", "mechanism_family": "DERIVATIVES_EXPECTATION_STATE",
            "source": "none found", "venue": "NONE", "market_type": "OPTIONS", "symbol_scope": "NONE", "start": "", "end": "",
            "frequency": "NONE", "row_count": "0", "fields": "NONE", "event_time": "NONE", "source_observed_time": "NONE",
            "publication_delay": "NONE", "coverage": f"{total(options, 'files')} files", "file_format": "NONE",
            "provenance": "local and PC1 inventory", "licensing_access": "NONE", "contains_future_revisions": "N/A",
            "physical_split_possible": False, "data_role": "DISABLED_NO_APPROVED_SOURCE",
            "inventory_status": "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE", "release_priority": 93,
            "decision": "UNAVAILABLE_NO_SOURCE", "blocker": "no Deribit or other options historical source found",
        },
    ]
    return pd.DataFrame(records)


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)


def run(root: Path) -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    local_root = root / "inventory" / "local"
    pc1_root = root / "inventory" / "pc1"
    local_manifest = json.loads((local_root / "inventory_manifest.json").read_text(encoding="utf-8"))
    pc1_manifest = json.loads((pc1_root / "inventory_manifest.json").read_text(encoding="utf-8-sig"))
    validate_inventory_manifest(local_manifest)
    validate_inventory_manifest(pc1_manifest)
    local = pd.read_csv(local_root / "data_family_inventory.csv")
    pc1 = pd.read_csv(pc1_root / "data_family_inventory.csv")
    local.insert(0, "inventory_site", "LOCAL")
    pc1.insert(0, "inventory_site", "PC1")
    combined = pd.concat([local, pc1], ignore_index=True).sort_values(
        ["inventory_site", "venue", "data_family", "dataset_root"], kind="mergesort"
    )
    registry = source_registry(local, pc1, config)
    selected = choose_first_release(registry)
    if selected != config["first_release_qualification_candidate"]:
        raise ValueError(f"release route mismatch: {selected}")

    write_csv(root / "combined_data_family_inventory.csv", combined)
    write_csv(root / "mechanism_source_registry.csv", registry)
    decision = {
        "status": "DATA_MECHANISM_INVENTORY_COMPLETED",
        "local_files": local_manifest["files"], "pc1_files": pc1_manifest["files"],
        "total_file_observations": local_manifest["files"] + pc1_manifest["files"],
        "new_performance_queries": 0, "forward_read": False, "row_data_read": False,
        "selected_release_qualification_candidate": selected,
        "selection_used_accepted_identities": False, "selection_used_performance": False,
        "cross_venue": "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE",
        "full_year_bbo": "HOLD_FOR_MORE_DATA", "multi_level_depth": "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE",
        "forced_flow": "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE", "options": "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE",
        "native_aggtrades": "DISCOVERED_REQUIRES_RELEASE_QUALIFICATION",
        "resource_reallocation": "unavailable cross-venue/forced-flow/options effort moves to the next real available family: native aggTrades",
    }
    decision_path = root / "inventory_decision.json"
    decision_path.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# CRYPTO MECHANISM/DATA EXPANSION-0 Inventory

Status: `DATA_MECHANISM_INVENTORY_COMPLETED`

- Local files inventoried: `{decision['local_files']}`.
- PC1 files inventoried: `{decision['pc1_files']}`.
- Row data read: `false`; performance queries: `0`; forward read: `false`.
- Cross-venue historical price/flow: `UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE` (only recent/May short probes found).
- Full-year Binance UM core12 BBO: `HOLD_FOR_MORE_DATA` (qualified scope remains core11, 2024-01/02, 82.22%; BBO is not depth).
- Multi-level depth: `UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE`.
- Liquidation/force-order: `UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE`.
- Options expectation state: `UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE`.
- Native Binance UM aggTrades: `DISCOVERED_REQUIRES_RELEASE_QUALIFICATION` with a longitudinal raw archive footprint.

The first release-qualification route is `{selected}`. It was chosen from physical source availability and split feasibility only; no accepted identity, historical winner, candidate score, or OOS result was used.
"""
    report_path = root / "MECHANISM_DATA_INVENTORY_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    inputs = [CONFIG, local_root / "inventory_manifest.json", local_root / "data_family_inventory.csv", local_root / "symbol_month_ledger.csv",
              pc1_root / "inventory_manifest.json", pc1_root / "data_family_inventory.csv", pc1_root / "symbol_month_ledger.csv"]
    outputs = [root / "combined_data_family_inventory.csv", root / "mechanism_source_registry.csv", decision_path, report_path]
    manifest = {
        "experiment_id": "20260712_crypto_mechanism_data_expansion0_inventory_001",
        "status": decision["status"], "repo_sha_at_run": "32FD2833E06DED22EB13E8CB4E4EF0BA77C8B55C",
        "performance_queries": 0, "row_data_read": False, "forward_read": False,
        "inputs": [{"path": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256_file(path)} for path in inputs],
        "outputs": [{"path": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256_file(path)} for path in outputs],
        "remote_task": {"task_id": "mechanism_inventory_20260712_1747", "machine": "DESKTOP-7877972", "exit_code": 0,
                        "data_root": "D:/HermesWorker/GDrive/AlphaFactory_CryptoData", "output_root": "H:/CodexRuntime/mechanism_data_expansion0_inventory_20260712/pc1"},
    }
    manifest_path = root / "inventory_completion_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifacts = outputs + [manifest_path]
    index = pd.DataFrame([{"artifact": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": sha256_file(path), "role": "INVENTORY_NO_PERFORMANCE"} for path in artifacts])
    write_csv(root / "inventory_artifact_index.csv", index)
    return decision


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    args = parser.parse_args()
    print(json.dumps(run(Path(args.root)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
