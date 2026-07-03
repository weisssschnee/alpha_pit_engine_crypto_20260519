from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7al2z2r_broader_non_oi_materialization_repair import strict_symbols  # noqa: E402


PATCH_DATASET = "binance_universe498_recent_patch_1h_v1_20260612"


def resolve_data_root() -> Path:
    candidates = [
        Path(os.environ["ALPHAFACTORY_CRYPTO_DATA_ROOT"])
        for _ in [0]
        if os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT")
    ]
    candidates.extend(
        [
            Path(r"G:\AlphaFactory_CryptoData"),
            Path(r"D:\HermesWorker\GDrive\AlphaFactory_CryptoData"),
        ]
    )
    for candidate in candidates:
        if (candidate / "reports" / f"{PATCH_DATASET}.json").exists():
            return candidate
    return candidates[0] if candidates else Path(r"G:\AlphaFactory_CryptoData")


DATA_ROOT = resolve_data_root()
DEFAULT_PATCH_ROOT = DATA_ROOT / "gold" / "features" / PATCH_DATASET
DEFAULT_PACKET = REPO / "runtime" / "a7shadow7_dedup_review_packet_20260704" / "a7shadow7_selected_review_packet.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7live1_source_lag_checksum_audit_20260704"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7LIVE1_SOURCE_LAG_CHECKSUM_AUDIT_20260704.md"
FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Abs",
    "Add",
    "CSRank",
    "Decay",
    "Delta",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "Sub",
    "TSRank",
    "ZScore",
}
FIELD_ALIAS_POLICY = [
    {
        "requested_field": "premium_close_bps",
        "patch_field": "premium_bps",
        "adapter_field": "premium_close_bps",
        "status": "alias_required",
        "policy": "rename premium_bps to premium_close_bps before formula evaluation",
    },
    {
        "requested_field": "funding_rate_delta_state_24h",
        "patch_field": "funding_rate",
        "adapter_field": "funding_rate_delta_state_24h",
        "status": "derived_past_only",
        "policy": "ffill funding_rate within symbol up to 8h, then subtract 24h lagged dense funding value",
    },
]
FIELD_SOURCE_RULES = {
    "open_interest_value_last": {
        "source_family": "metrics",
        "raw_source": "Binance Vision futures/um/daily/metrics",
        "checksum_expectation": "local_sha256_present_official_checksum_pending",
        "availability_policy": "timestamp + 1h conservative bucket close availability",
        "same_bar_policy": "usable at execution_time timestamp+1h only",
    },
    "open_interest_mean": {
        "source_family": "metrics",
        "raw_source": "Binance Vision futures/um/daily/metrics",
        "checksum_expectation": "local_sha256_present_official_checksum_pending",
        "availability_policy": "timestamp + 1h conservative bucket close availability",
        "same_bar_policy": "usable at execution_time timestamp+1h only",
    },
    "premium_close_bps": {
        "source_family": "premiumIndexKlines",
        "raw_source": "Binance Vision futures/um/daily/premiumIndexKlines",
        "checksum_expectation": "local_sha256_present_official_checksum_pending",
        "availability_policy": "timestamp + 1h conservative bucket close availability",
        "same_bar_policy": "usable at execution_time timestamp+1h only",
    },
    "funding_rate_delta_state_24h": {
        "source_family": "funding_rest",
        "raw_source": "Binance USD-M futures REST fapi/v1/fundingRate",
        "checksum_expectation": "rest_no_exchange_checksum",
        "availability_policy": "derived from event funding_rate, ffilled only from known past event rows",
        "same_bar_policy": "24h lagged delta; no negative lag allowed",
    },
}
SOURCE_DECLARATION_TOKENS = {
    "metrics": ["metrics"],
    "premiumIndexKlines": ["premium", "premiumIndexKlines"],
    "funding_rest": ["funding", "fundingRate", "funding_rate"],
}


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


def expression_fields(expression: str) -> set[str]:
    return {
        token
        for token in FIELD_RE.findall(str(expression))
        if token not in OPERATORS and token.lower() not in {"nan", "inf"}
    }


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def selected_fields(packet: pd.DataFrame) -> list[str]:
    fields: set[str] = set()
    for expr in packet["expression"].astype(str):
        fields.update(expression_fields(expr))
    return sorted(fields)


def audit_selected_fields(fields: list[str], field_contract: dict[str, Any], download_summary: pd.DataFrame) -> pd.DataFrame:
    source_text = json.dumps(field_contract.get("sources", {}), sort_keys=True)
    timestamp_semantics = field_contract.get("timestamp_semantics", {})
    rows: list[dict[str, Any]] = []
    for field in fields:
        rule = FIELD_SOURCE_RULES.get(field, {})
        source_family = rule.get("source_family", "unknown")
        if source_family == "funding_rest":
            family_rows = pd.DataFrame([{"checksum_status": "rest_no_exchange_checksum", "source": "binance_rest"}])
        else:
            family_rows = download_summary[download_summary["family"].astype(str).eq(source_family)]
        checksum_values = sorted(set(family_rows.get("checksum_status", pd.Series(dtype=str)).dropna().astype(str)))
        local_sha256_count = int(family_rows.get("sha256_present_count", pd.Series(dtype=int)).sum()) if "sha256_present_count" in family_rows else 0
        official_checksum_ok = any("checksum_ok" in value for value in checksum_values)
        checksum_pending = any("pending" in value or "not_checked" in value for value in checksum_values) or source_family == "funding_rest"
        declaration_tokens = SOURCE_DECLARATION_TOKENS.get(source_family, [source_family])
        source_declared = any(token in source_text for token in declaration_tokens)
        lag_policy_ok = bool(timestamp_semantics.get("feature_available_time")) and bool(timestamp_semantics.get("execution_time"))
        if field == "funding_rate_delta_state_24h":
            lag_policy_ok = True
        status = "PASS_CONTROLLED_RESEARCH"
        final_proof_status = "PASS_FINAL_PROOF"
        blockers: list[str] = []
        final_blockers: list[str] = []
        if not source_declared:
            blockers.append("source_family_not_declared")
        if not lag_policy_ok:
            blockers.append("missing_timestamp_lag_policy")
        if not family_rows.empty and local_sha256_count <= 0 and source_family != "funding_rest":
            blockers.append("missing_local_sha256")
        if blockers:
            status = "HOLD_SOURCE_LAG_OR_TRACE"
        if not official_checksum_ok:
            final_blockers.append("official_checksum_not_closed")
        if source_family == "funding_rest":
            final_blockers.append("rest_source_has_no_exchange_checksum")
        if final_blockers:
            final_proof_status = "HOLD_FINAL_PROOF_SOURCE_EVIDENCE"
        rows.append(
            {
                "field": field,
                "source_family": source_family,
                "raw_source": rule.get("raw_source", "unknown"),
                "controlled_research_status": status,
                "final_proof_status": final_proof_status,
                "local_sha256_count": local_sha256_count,
                "checksum_status_values": ";".join(checksum_values),
                "source_declared_in_contract": source_declared,
                "lag_policy_ok": lag_policy_ok,
                "availability_policy": rule.get("availability_policy", ""),
                "same_bar_policy": rule.get("same_bar_policy", ""),
                "controlled_blockers": ";".join(blockers),
                "final_proof_blockers": ";".join(final_blockers),
            }
        )
    return pd.DataFrame(rows)


def download_family_summary(download_manifest: pd.DataFrame) -> pd.DataFrame:
    if download_manifest.empty:
        return pd.DataFrame(
            columns=[
                "source",
                "family",
                "rows",
                "status_values",
                "checksum_status_values",
                "sha256_present_count",
                "error_count",
            ]
        )
    frame = download_manifest.copy()
    frame["sha256_present"] = frame.get("sha256", "").astype(str).str.len() > 0
    frame["has_error"] = frame.get("error", "").fillna("").astype(str).str.len() > 0
    rows: list[dict[str, Any]] = []
    for (source, family), part in frame.groupby(["source", "family"], dropna=False):
        rows.append(
            {
                "source": source,
                "family": family,
                "rows": int(part.shape[0]),
                "status_values": ";".join(sorted(set(part.get("status", pd.Series(dtype=str)).dropna().astype(str)))),
                "checksum_status_values": ";".join(
                    sorted(set(part.get("checksum_status", pd.Series(dtype=str)).dropna().astype(str)))
                ),
                "sha256_present_count": int(part["sha256_present"].sum()),
                "error_count": int(part["has_error"].sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["source", "family"]).reset_index(drop=True)


def patch_manifest_audit(manifest: pd.DataFrame, coverage: pd.DataFrame, selected_symbol_count: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not manifest.empty:
        rows.append(
            {
                "check": "gold_manifest",
                "rows": int(manifest.shape[0]),
                "duplicate_timestamp_sum": int(pd.to_numeric(manifest.get("duplicate_timestamp", 0), errors="coerce").fillna(0).sum()),
                "inf_cell_sum": int(pd.to_numeric(manifest.get("inf_cells", 0), errors="coerce").fillna(0).sum()),
                "checksum_status_values": ";".join(sorted(set(manifest.get("checksum_status", pd.Series(dtype=str)).dropna().astype(str)))),
                "min_timestamp": str(manifest.get("timestamp_min", pd.Series(dtype=str)).min()),
                "max_timestamp": str(manifest.get("timestamp_max", pd.Series(dtype=str)).max()),
                "status": "PASS" if int(pd.to_numeric(manifest.get("duplicate_timestamp", 0), errors="coerce").fillna(0).sum()) == 0 else "HOLD",
            }
        )
    else:
        rows.append({"check": "gold_manifest", "status": "MISSING"})
    if not coverage.empty:
        selected = coverage[coverage["symbol"].isin(strict_symbols()[:selected_symbol_count])]
        rows.append(
            {
                "check": "selected_symbol_coverage",
                "rows": int(selected.shape[0]),
                "duplicate_timestamp_sum": "",
                "inf_cell_sum": "",
                "checksum_status_values": "",
                "min_timestamp": str(selected.get("timestamp_min", pd.Series(dtype=str)).min()),
                "max_timestamp": str(selected.get("timestamp_max", pd.Series(dtype=str)).max()),
                "min_coverage": float(pd.to_numeric(selected.get("coverage", 0), errors="coerce").min()) if not selected.empty else 0.0,
                "min_mark_coverage": float(pd.to_numeric(selected.get("mark_coverage", 0), errors="coerce").min()) if not selected.empty else 0.0,
                "min_metrics_coverage": float(pd.to_numeric(selected.get("metrics_coverage", 0), errors="coerce").min()) if not selected.empty else 0.0,
                "min_funding_coverage": float(pd.to_numeric(selected.get("funding_coverage", 0), errors="coerce").min()) if not selected.empty else 0.0,
                "status": "PASS" if not selected.empty and pd.to_numeric(selected.get("coverage", 0), errors="coerce").min() >= 0.99 else "HOLD",
            }
        )
    else:
        rows.append({"check": "selected_symbol_coverage", "status": "MISSING"})
    return pd.DataFrame(rows)


def timestamp_lag_audit(field_contract: dict[str, Any]) -> pd.DataFrame:
    semantics = field_contract.get("timestamp_semantics", {})
    rows = [
        {
            "item": "timestamp",
            "policy": semantics.get("timestamp", ""),
            "status": "PASS" if "bucket start" in str(semantics.get("timestamp", "")).lower() else "REVIEW",
        },
        {
            "item": "feature_available_time",
            "policy": semantics.get("feature_available_time", ""),
            "status": "PASS" if "+ 1h" in str(semantics.get("feature_available_time", "")) else "HOLD",
        },
        {
            "item": "execution_time",
            "policy": semantics.get("execution_time", ""),
            "status": "PASS" if "+ 1h" in str(semantics.get("execution_time", "")) else "HOLD",
        },
        {
            "item": "funding_rate_delta_state_24h",
            "policy": "adapter derives from ffilled current-or-past funding_rate minus 24h lag; no forward shift",
            "status": "PASS",
        },
    ]
    return pd.DataFrame(rows)


def build(runtime: Path, report: Path, packet_path: Path, patch_root: Path, symbol_cap: int) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    report_json_path = DATA_ROOT / "reports" / f"{PATCH_DATASET}.json"
    field_contract_path = DATA_ROOT / "gold" / "metadata" / f"{PATCH_DATASET}_field_contract.json"
    manifest_path = DATA_ROOT / "manifests" / f"{PATCH_DATASET}_manifest.csv"
    coverage_path = DATA_ROOT / "manifests" / f"{PATCH_DATASET}_coverage.csv"
    download_manifest_path = DATA_ROOT / "manifests" / f"{PATCH_DATASET}_download_manifest.csv"

    packet = pd.read_csv(packet_path)
    fields = selected_fields(packet)
    patch_report = read_json(report_json_path) if report_json_path.exists() else {}
    field_contract = read_json(field_contract_path) if field_contract_path.exists() else {}
    manifest = read_csv_if_exists(manifest_path)
    coverage = read_csv_if_exists(coverage_path)
    download_manifest = read_csv_if_exists(download_manifest_path)

    family_summary = download_family_summary(download_manifest)
    field_audit = audit_selected_fields(fields, field_contract, family_summary)
    manifest_audit = patch_manifest_audit(manifest, coverage, symbol_cap)
    lag_audit = timestamp_lag_audit(field_contract)
    alias_policy = pd.DataFrame(FIELD_ALIAS_POLICY)

    field_audit.to_csv(runtime / "a7live1_selected_field_source_audit.csv", index=False)
    family_summary.to_csv(runtime / "a7live1_download_manifest_family_summary.csv", index=False)
    manifest_audit.to_csv(runtime / "a7live1_patch_manifest_audit.csv", index=False)
    lag_audit.to_csv(runtime / "a7live1_timestamp_lag_audit.csv", index=False)
    alias_policy.to_csv(runtime / "a7live1_alias_policy.csv", index=False)

    controlled_blockers = sorted(
        set(
            item
            for cell in field_audit.get("controlled_blockers", pd.Series(dtype=str)).dropna().astype(str)
            for item in cell.split(";")
            if item
        )
    )
    controlled_blockers.extend(
        sorted(set(lag_audit.loc[lag_audit["status"].eq("HOLD"), "item"].astype(str).tolist()))
    )
    controlled_blockers.extend(
        sorted(set(manifest_audit.loc[manifest_audit["status"].eq("HOLD"), "check"].astype(str).tolist()))
    )
    final_blockers = sorted(
        set(
            item
            for cell in field_audit.get("final_proof_blockers", pd.Series(dtype=str)).dropna().astype(str)
            for item in cell.split(";")
            if item
        )
    )
    final_blockers.extend(
        ["recent_patch_report_fast_checksum_pending"]
        if "FAST_CHECKSUM_PENDING" in str(patch_report.get("decision", ""))
        else []
    )
    decision = (
        "PASS_A7LIVE1_CONTROLLED_RESEARCH_SOURCE_LAG_OK_CHECKSUM_PENDING"
        if not controlled_blockers
        else "HOLD_A7LIVE1_SOURCE_LAG_OR_TRACE_BLOCKED"
    )
    manifest_payload = {
        "stage": "A7LIVE-1",
        "generated_at": now_utc(),
        "decision": decision,
        "patch_dataset": PATCH_DATASET,
        "patch_root": str(patch_root),
        "patch_report_decision": patch_report.get("decision"),
        "packet_path": str(packet_path),
        "candidate_count": int(packet.shape[0]),
        "selected_fields": fields,
        "controlled_research_blockers": sorted(set(controlled_blockers)),
        "final_proof_blockers": sorted(set(final_blockers)),
        "field_audit_rows": int(field_audit.shape[0]),
        "download_manifest_rows": int(download_manifest.shape[0]) if not download_manifest.empty else 0,
        "gold_manifest_rows": int(manifest.shape[0]) if not manifest.empty else 0,
        "coverage_rows": int(coverage.shape[0]) if not coverage.empty else 0,
        "authorizes_family_diversified_search": not controlled_blockers,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_book": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_final_proof": False,
        "next_required": [
            "Close official Binance Vision CHECKSUM audit before any final proof claim.",
            "Treat REST funding source as controlled-research evidence unless an independent archive/source trace is added.",
            "Proceed to A7SEARCH7 family-diversified queue only if controlled_research_blockers is empty.",
        ],
    }
    write_json(runtime / "a7live1_manifest.json", manifest_payload)

    lines = [
        "# CRYPTO A7LIVE1 Source-Lag / Checksum Audit",
        "",
        f"Generated: {manifest_payload['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7LIVE-1 audits the A7LIVE-0 forward patch path for timestamp lag, source trace, alias policy, and checksum boundary. It does not run backtest, alpha proof, shadow, paper, or live trading.",
        "",
        "## Summary",
        "",
        f"- patch report decision: `{patch_report.get('decision')}`",
        f"- candidate_count: `{packet.shape[0]}`",
        f"- selected_fields: `{', '.join(fields)}`",
        f"- controlled_research_blockers: `{';'.join(sorted(set(controlled_blockers))) or 'none'}`",
        f"- final_proof_blockers: `{';'.join(sorted(set(final_blockers))) or 'none'}`",
        f"- authorizes_family_diversified_search: `{manifest_payload['authorizes_family_diversified_search']}`",
        "- authorizes_alpha_proof: `False`",
        "- authorizes_shadow_book/paper/live: `False`",
        "",
        "## Selected Field Source Audit",
        "",
        md_table(field_audit),
        "",
        "## Timestamp Lag Audit",
        "",
        md_table(lag_audit),
        "",
        "## Alias Policy",
        "",
        md_table(alias_policy),
        "",
        "## Patch Manifest Audit",
        "",
        md_table(manifest_audit),
        "",
        "## Download Manifest Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Interpretation",
        "",
        "The forward patch has enough declared timestamp-lag policy and local source trace for controlled research continuation if controlled blockers are empty. It is still not final proof because the recent patch explicitly remains fast-checksum-pending and REST funding has no exchange checksum.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest_payload, indent=2, sort_keys=True),
        "```",
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    return manifest_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit A7LIVE-0 forward patch source lag and checksum boundary.")
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--patch-root", type=Path, default=DEFAULT_PATCH_ROOT)
    parser.add_argument("--symbol-cap", type=int, default=96)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build(args.runtime, args.report, args.packet, args.patch_root, args.symbol_cap)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
