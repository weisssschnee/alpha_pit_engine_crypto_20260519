from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path("G:/AlphaFactory_CryptoData")
SOURCE_DIR = DATA_ROOT / "alphafactory_crypto" / "runtime" / "a7s1_metrics_source_trace"
SOURCE_REPORT = DATA_ROOT / "alphafactory_crypto" / "reports" / "CRYPTO_A7S1_BINANCE_METRICS_SOURCE_TRACE_20260522.md"
GOLD_PATH = DATA_ROOT / "gold" / "features" / "binance_metrics_1h_features_v1.parquet"

OUT_DIR = ROOT / "runtime" / "a7s1_metrics_acceptance_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7S1_METRICS_ACCEPTANCE_AUDIT_20260522.md"

INDEPENDENT_FIELDS = {
    "open_interest",
    "open_interest_value",
    "global_long_short_account_ratio",
    "top_long_short_account_ratio",
    "top_long_short_position_ratio",
    "taker_buy_sell_volume_ratio",
}


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def clean_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if np.isfinite(out) else None


def load_inputs() -> dict[str, Any]:
    manifest = pd.read_csv(SOURCE_DIR / "a7s1_metrics_symbol_date_manifest.csv")
    checksum = pd.read_csv(SOURCE_DIR / "a7s1_metrics_checksum_audit.csv")
    coverage = pd.read_csv(SOURCE_DIR / "a7s1_metrics_coverage_by_symbol.csv")
    availability = pd.read_csv(SOURCE_DIR / "a7s1_metrics_1h_feature_availability.csv")
    field_contract = json.loads((SOURCE_DIR / "a7s1_metrics_field_contract.json").read_text(encoding="utf-8"))
    gold = pd.read_parquet(GOLD_PATH)
    return {
        "manifest": manifest,
        "checksum": checksum,
        "coverage": coverage,
        "availability": availability,
        "field_contract": field_contract,
        "gold": gold,
    }


def source_trace_summary(inputs: dict[str, Any]) -> pd.DataFrame:
    manifest = inputs["manifest"]
    checksum = inputs["checksum"]
    coverage = inputs["coverage"]
    rows = [
        {"check": "expected_symbol_days", "value": int(len(manifest)), "status": "INFO"},
        {"check": "ready_symbol_days", "value": int(manifest["status"].eq("ready").sum()), "status": "PASS" if manifest["status"].eq("ready").all() else "BLOCKER"},
        {"check": "checksum_not_ok", "value": int(checksum["checksum_status"].ne("ok").sum()), "status": "PASS" if checksum["checksum_status"].eq("ok").all() else "BLOCKER"},
        {"check": "raw_duplicate_timestamp_count", "value": int(manifest["duplicate_timestamp_count"].sum()), "status": "PASS" if int(manifest["duplicate_timestamp_count"].sum()) == 0 else "BLOCKER"},
        {"check": "rounded_5m_bucket_duplicate_count", "value": int(manifest["duplicate_bucket_5m_count"].sum()), "status": "WARNING"},
        {"check": "rounded_5m_timestamp_gap_count", "value": int(manifest["timestamp_gap_count_5m"].sum()), "status": "WARNING"},
        {"check": "gap_symbol_days", "value": int(manifest["timestamp_gap_count_5m"].gt(0).sum()), "status": "WARNING"},
        {"check": "raw_nan_count", "value": int(manifest["nan_count_raw_values"].sum()), "status": "WARNING"},
        {"check": "negative_raw_values", "value": int(manifest["negative_count_raw_values"].sum()), "status": "PASS" if int(manifest["negative_count_raw_values"].sum()) == 0 else "BLOCKER"},
        {"check": "symbols", "value": int(coverage["symbol"].nunique()), "status": "PASS" if int(coverage["symbol"].nunique()) == 12 else "BLOCKER"},
    ]
    return pd.DataFrame(rows)


def gold_panel_summary(inputs: dict[str, Any]) -> pd.DataFrame:
    gold = inputs["gold"]
    num = gold.select_dtypes("number")
    inf_count = int(np.isinf(num.to_numpy(dtype=float, copy=False)).sum())
    duplicate_keys = int(gold.duplicated(["symbol", "timestamp"]).sum())
    rows = [
        {"check": "gold_path_exists", "value": str(GOLD_PATH.exists()), "status": "PASS" if GOLD_PATH.exists() else "BLOCKER"},
        {"check": "gold_rows", "value": int(len(gold)), "status": "PASS" if len(gold) == 251028 else "WARNING"},
        {"check": "gold_columns", "value": int(gold.shape[1]), "status": "PASS" if gold.shape[1] == 40 else "WARNING"},
        {"check": "gold_symbols", "value": int(gold["symbol"].nunique()), "status": "PASS" if gold["symbol"].nunique() == 12 else "BLOCKER"},
        {"check": "gold_timestamp_min", "value": str(gold["timestamp"].min()), "status": "INFO"},
        {"check": "gold_timestamp_max", "value": str(gold["timestamp"].max()), "status": "INFO"},
        {"check": "gold_duplicate_symbol_timestamp", "value": duplicate_keys, "status": "PASS" if duplicate_keys == 0 else "BLOCKER"},
        {"check": "gold_inf_cells", "value": inf_count, "status": "PASS" if inf_count == 0 else "BLOCKER"},
        {"check": "gold_nan_numeric_cells", "value": int(num.isna().sum().sum()), "status": "WARNING"},
    ]
    return pd.DataFrame(rows)


def field_contract_summary(inputs: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    fields = pd.DataFrame(inputs["field_contract"]["fields"])
    independent = fields[fields["independent_source"].eq(True)].copy()
    derived = fields[fields["independent_source"].eq(False)].copy()
    independent["expected_independent_source"] = independent["field_name"].isin(INDEPENDENT_FIELDS)
    derived["derived_policy_ok"] = derived["derived_from"].notna()
    summary = pd.DataFrame(
        [
            {
                "check": "independent_source_field_count",
                "value": int(len(independent)),
                "status": "PASS" if set(independent["field_name"]) == INDEPENDENT_FIELDS else "BLOCKER",
            },
            {
                "check": "derived_field_count",
                "value": int(len(derived)),
                "status": "PASS" if len(derived) > 0 and derived["derived_policy_ok"].all() else "BLOCKER",
            },
            {
                "check": "forward_only_independent_fields",
                "value": int(independent["is_forward_only"].astype(bool).sum()),
                "status": "PASS" if int(independent["is_forward_only"].astype(bool).sum()) == 0 else "BLOCKER",
            },
            {
                "check": "historical_backfill_independent_fields",
                "value": int(independent["is_historical_backfill"].astype(bool).sum()),
                "status": "PASS" if int(independent["is_historical_backfill"].astype(bool).sum()) == len(independent) else "BLOCKER",
            },
        ]
    )
    return summary, fields


def availability_summary(inputs: dict[str, Any]) -> pd.DataFrame:
    availability = inputs["availability"]
    rows = [
        {
            "check": "availability_symbols",
            "value": int(availability["symbol"].nunique()),
            "status": "PASS" if availability["symbol"].nunique() == 12 else "BLOCKER",
        },
        {
            "check": "available_before_execution_all",
            "value": str(bool(availability["available_before_execution_all"].all())),
            "status": "PASS" if bool(availability["available_before_execution_all"].all()) else "BLOCKER",
        },
        {
            "check": "availability_duplicate_timestamp_count",
            "value": int(availability["duplicate_timestamp_count"].sum()),
            "status": "PASS" if int(availability["duplicate_timestamp_count"].sum()) == 0 else "BLOCKER",
        },
        {
            "check": "availability_inf_cells",
            "value": int(availability["inf_cells"].sum()),
            "status": "PASS" if int(availability["inf_cells"].sum()) == 0 else "BLOCKER",
        },
        {
            "check": "availability_nan_cells",
            "value": int(availability["nan_cells"].sum()),
            "status": "WARNING",
        },
    ]
    return pd.DataFrame(rows)


def coverage_by_symbol(inputs: dict[str, Any]) -> pd.DataFrame:
    cov = inputs["coverage"].copy()
    cols = [
        "symbol",
        "expected_days",
        "ready_days",
        "missing_or_hold_days",
        "checksum_ok_days",
        "coverage_by_date",
        "row_coverage",
        "timestamp_gap_count_5m",
        "nan_count_raw_values",
        "negative_count_raw_values",
    ]
    return cov[cols].sort_values("symbol")


def write_report(
    now: str,
    source_summary: pd.DataFrame,
    gold_summary: pd.DataFrame,
    field_summary: pd.DataFrame,
    fields: pd.DataFrame,
    availability: pd.DataFrame,
    coverage: pd.DataFrame,
    authorization: dict[str, Any],
) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    independent_fields = sorted(fields[fields["independent_source"].eq(True)]["field_name"].tolist())
    derived_fields = sorted(fields[fields["independent_source"].eq(False)]["field_name"].tolist())
    lines = [
        "# Crypto A7S-1 Metrics Acceptance Audit",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{authorization['decision']}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Scope",
        "",
        "This is the experiment-side acceptance audit for Binance Vision daily/metrics. It verifies source trace closure, field contract boundaries, feature availability, and gold parquet sanity. It does not run alpha search.",
        "",
        "Vendor 5m jitter/gap warnings are retained as caveats. They do not block controlled experiments, but must be carried into reports.",
        "",
        "## Source Trace Summary",
        "",
        table(source_summary, max_rows=40),
        "",
        "## Gold Panel Summary",
        "",
        table(gold_summary, max_rows=40),
        "",
        "## Field Contract Summary",
        "",
        table(field_summary, max_rows=20),
        "",
        "## Independent Source Fields",
        "",
        "```text",
        "\n".join(independent_fields),
        "```",
        "",
        "## Derived Feature Fields",
        "",
        "```text",
        "\n".join(derived_fields),
        "```",
        "",
        "## Availability Summary",
        "",
        table(availability, max_rows=20),
        "",
        "## Coverage By Symbol",
        "",
        table(coverage, max_rows=20),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Required Next",
        "",
        "- Merge metrics into the experiment feature registry as `independent metrics source + derived feature layer`.",
        "- Run only controlled A7S-2/A7R-style diagnostics first; no alpha proof or full search.",
        "- Preserve vendor 5m warning caveat in all downstream reports.",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    inputs = load_inputs()
    source_summary = source_trace_summary(inputs)
    gold_summary = gold_panel_summary(inputs)
    field_summary, fields = field_contract_summary(inputs)
    availability = availability_summary(inputs)
    coverage = coverage_by_symbol(inputs)
    all_checks = pd.concat(
        [
            source_summary.assign(section="source_trace"),
            gold_summary.assign(section="gold_panel"),
            field_summary.assign(section="field_contract"),
            availability.assign(section="availability"),
        ],
        ignore_index=True,
    )
    blockers = all_checks[all_checks["status"].eq("BLOCKER")]["check"].tolist()
    warnings = all_checks[all_checks["status"].eq("WARNING")]["check"].tolist()
    decision = "PASS_A7S1_ACCEPTED_WITH_VENDOR_5M_WARNINGS" if not blockers else "HOLD_A7S1_ACCEPTANCE_BLOCKERS"
    authorization = {
        "generated_at": now,
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_report": str(SOURCE_REPORT),
        "gold_panel": str(GOLD_PATH),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_metrics_feature_registry_integration": not blockers,
        "authorizes_controlled_metrics_diagnostics": not blockers,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "vendor_5m_warning_caveat_required": True,
        "independent_source_fields": sorted(INDEPENDENT_FIELDS),
        "required_next": [
            "A7S-2 metrics feature registry integration and controlled diagnostics",
            "Do not classify change/zscore/interaction fields as independent sources",
            "Carry vendor 5m bucket duplicate/gap/NaN caveats downstream",
        ],
    }
    source_summary.to_csv(OUT_DIR / "a7s1_acceptance_source_trace_summary.csv", index=False)
    gold_summary.to_csv(OUT_DIR / "a7s1_acceptance_gold_panel_summary.csv", index=False)
    field_summary.to_csv(OUT_DIR / "a7s1_acceptance_field_contract_summary.csv", index=False)
    fields.to_csv(OUT_DIR / "a7s1_acceptance_field_contract_flat.csv", index=False)
    availability.to_csv(OUT_DIR / "a7s1_acceptance_availability_summary.csv", index=False)
    coverage.to_csv(OUT_DIR / "a7s1_acceptance_coverage_by_symbol.csv", index=False)
    all_checks.to_csv(OUT_DIR / "a7s1_acceptance_check_matrix.csv", index=False)
    write_json(OUT_DIR / "a7s1_acceptance_authorization_matrix.json", authorization)
    write_json(OUT_DIR / "a7s1_acceptance_manifest.json", {"generated_at": now, "decision": decision, "output_dir": str(OUT_DIR), "report": str(REPORT_PATH)})
    write_report(now, source_summary, gold_summary, field_summary, fields, availability, coverage, authorization)
    print(json.dumps({"decision": decision, "blockers": blockers, "warnings": warnings}, indent=2))


if __name__ == "__main__":
    main()
