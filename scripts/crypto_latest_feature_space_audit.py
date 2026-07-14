from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "runtime" / "crypto_feature_runtime_inventory_20260714"
DEFAULT_OUTPUT_DIR = ROOT / "runtime" / "crypto_latest_evidence_independent_audit_20260714"

BASE_INPUT = INPUT_DIR / "aggtrades_base_feature_registry_94.csv"
DERIVED_INPUT = INPUT_DIR / "aggtrades_derived_feature_specs_5211.csv"
LINEAGE_INPUT = INPUT_DIR / "feature_lineage_ledger.csv"
MAP_INPUT = INPUT_DIR / "field_representation_lane_generator_map.csv"
CURRENT_EPOCH_INPUT = INPUT_DIR / "current_epoch_runtime_fields.csv"
ASSET_MANIFEST_INPUT = INPUT_DIR / "asset_manifest.csv"

BASE_OUTPUT = "CRYPTO_FEATURE_INFORMATION_AXIS_AUDIT.csv"
DERIVED_OUTPUT = "CRYPTO_DERIVED_SPEC_EQUIVALENCE_AUDIT.csv"
SUMMARY_OUTPUT = "CRYPTO_FEATURE_SPACE_COMPRESSION_SUMMARY.json"

HISTORICAL_COMMIT = "1ed5acd"
AUDIT_COMMIT_SHA = "09ac397c61b0b462497e9a8c0ea84981cc6a93f9"
AUDIT_ROW_PROVENANCE = {
    "repo_ref": f"main@{AUDIT_COMMIT_SHA}",
    "commit_sha": AUDIT_COMMIT_SHA,
    "run_id": "NOT_APPLICABLE_STATIC_AUDIT",
    "data_release": "STATIC_HASHED_INVENTORY_NO_NUMERIC_DATA",
    "evidence_role": "STATIC_FEATURE_SPACE_QUALIFICATION",
    "superseded": "false",
    "authoritative_now": "true",
}
HISTORICAL_FORMATTER_PATH = (
    "archive/deprecated_crypto_a7_20260527/scripts/scripts/"
    "crypto_a7v3_agg_aware_candidate_dry_run.py"
)
HISTORICAL_EVALUATOR_PATH = (
    "archive/deprecated_crypto_a7_20260527/scripts/scripts/"
    "crypto_a7v5_small_replay_smoke.py"
)
CURRENT_BASE_FORMULA_PATH = ROOT / "scripts" / "crypto_a7ai0r_core12_aggtrades_unified_feature_build.py"

ALLOWED_BASE_CLASSIFICATIONS = {
    "RAW_OBSERVATION",
    "NORMALIZED_REPRESENTATION",
    "ROLLING_DERIVED",
    "CROSS_SYMBOL_DERIVED",
    "INTEGRITY_METADATA",
    "FORMULA_PROVENANCE_UNRESOLVED",
}

METADATA_FIELDS = {
    "agg_first_agg_trade_id",
    "agg_last_agg_trade_id",
    "agg_first_transact_time_ms",
    "agg_last_transact_time_ms",
}

# These fields exist in the recovered registry, but no matching implementation is
# present in Git history used by this audit.  Names are not treated as formulas.
UNRESOLVED_FORMULA_FIELDS = {
    "agg_buy_agg_trade_count",
    "agg_sell_agg_trade_count",
    "agg_buy_underlying_trade_count",
    "agg_sell_underlying_trade_count",
    "agg_buy_quantity",
    "agg_sell_quantity",
    "agg_trade_count_le_100",
    "agg_trade_count_100_1k",
    "agg_trade_count_1k_10k",
    "agg_trade_count_10k_100k",
    "agg_trade_count_100k_1m",
    "agg_trade_count_gt_1m",
    "agg_notional_le_100",
    "agg_notional_100_1k",
    "agg_notional_1k_10k",
    "agg_notional_10k_100k",
    "agg_notional_100k_1m",
    "agg_notional_gt_1m",
    "agg_flow_imbalance_qty",
    "agg_large_notional_share_100k_plus",
    "agg_large_count_share_100k_plus",
    "agg_signed_quantity_sum_4h",
    "agg_signed_quantity_sum_24h",
    "agg_universe_signed_notional",
}

NORMALIZED_FIELDS = {
    "agg_avg_agg_trade_notional",
    "agg_avg_underlying_trade_notional",
    "agg_volume_imbalance",
    "agg_buy_sell_notional_ratio",
    "agg_price_range_bps",
    "agg_close_to_open_bps",
    "agg_large_trade_count_ratio_100k_plus",
    "agg_large_notional_ratio_100k_plus",
    "agg_vwap_close_bps",
    "agg_buy_sell_vwap_spread_bps",
    "agg_avg_underlying_trades_per_agg",
    "agg_flow_imbalance_notional",
    "agg_buy_notional_share",
    "agg_sell_notional_share",
}

CURRENT_FORMULA_FIELDS = {
    "agg_vwap_close_bps",
    "agg_buy_sell_vwap_spread_bps",
    "agg_avg_underlying_trades_per_agg",
    "agg_flow_imbalance_notional",
    "agg_buy_notional_share",
    "agg_sell_notional_share",
}

RAW_SOURCE_DECLARATION_FIELDS = {
    "agg_trade_count",
    "agg_underlying_trade_count",
    "agg_quantity",
    "agg_notional",
    "agg_buy_notional",
    "agg_sell_notional",
    "agg_signed_aggressor_quantity",
    "agg_signed_aggressor_notional",
    "agg_high_price",
    "agg_low_price",
    "agg_price_std",
    "agg_max_trade_notional",
    "agg_open_price",
    "agg_close_price",
    "agg_vwap",
    "agg_buy_vwap",
    "agg_sell_vwap",
    "agg_avg_agg_trade_notional",
    "agg_avg_underlying_trade_notional",
    "agg_volume_imbalance",
    "agg_buy_sell_notional_ratio",
    "agg_price_range_bps",
    "agg_close_to_open_bps",
    "agg_large_trade_count_100k_plus",
    "agg_large_notional_100k_plus",
    "agg_large_trade_count_ratio_100k_plus",
    "agg_large_notional_ratio_100k_plus",
}

MARKET_AXIS = {
    "ret_6": "MARKET_RETURN",
    "ret_12": "MARKET_RETURN",
    "realized_vol_12": "REALIZED_VOLATILITY",
    "realized_vol_24": "REALIZED_VOLATILITY",
    "mark_index_ratio": "MARK_INDEX_BASIS",
    "premium_index": "PREMIUM_INDEX_BASIS",
    "latest_known_funding_rate": "FUNDING_RATE",
}

MIRROR_PARTNERS = {
    "agg_buy_agg_trade_count": "agg_sell_agg_trade_count",
    "agg_sell_agg_trade_count": "agg_buy_agg_trade_count",
    "agg_buy_underlying_trade_count": "agg_sell_underlying_trade_count",
    "agg_sell_underlying_trade_count": "agg_buy_underlying_trade_count",
    "agg_buy_quantity": "agg_sell_quantity",
    "agg_sell_quantity": "agg_buy_quantity",
    "agg_buy_notional": "agg_sell_notional",
    "agg_sell_notional": "agg_buy_notional",
    "agg_buy_vwap": "agg_sell_vwap",
    "agg_sell_vwap": "agg_buy_vwap",
    "agg_buy_notional_share": "agg_sell_notional_share",
    "agg_sell_notional_share": "agg_buy_notional_share",
}

UNRESOLVED_SIDE_MIRROR_FIELDS = {
    "agg_buy_agg_trade_count",
    "agg_sell_agg_trade_count",
    "agg_buy_underlying_trade_count",
    "agg_sell_underlying_trade_count",
    "agg_buy_quantity",
    "agg_sell_quantity",
}

POSITIVE_SCALE_EQUIVALENT_BASE = {
    ("TSMean", 4, "agg_notional"): "agg_notional_sum_4h",
    ("TSMean", 24, "agg_notional"): "agg_notional_sum_24h",
    ("TSMean", 4, "agg_quantity"): "agg_quantity_sum_4h",
    ("TSMean", 24, "agg_quantity"): "agg_quantity_sum_24h",
    ("TSMean", 4, "agg_signed_aggressor_notional"): "agg_signed_notional_sum_4h",
    ("TSMean", 24, "agg_signed_aggressor_notional"): "agg_signed_notional_sum_24h",
    ("TSMean", 4, "agg_large_notional_100k_plus"): "agg_large_notional_sum_4h",
    ("TSMean", 24, "agg_large_notional_100k_plus"): "agg_large_notional_sum_24h",
    ("TSMean", 4, "agg_trade_count"): "agg_trade_count_sum_4h",
    ("TSMean", 24, "agg_trade_count"): "agg_trade_count_sum_24h",
    ("TSMean", 4, "agg_close_to_open_bps"): "agg_close_to_open_bps_sum_4h",
    ("TSMean", 24, "agg_close_to_open_bps"): "agg_close_to_open_bps_sum_24h",
    ("RollingMax", 4, "agg_price_range_bps"): "agg_price_range_bps_max_4h",
    ("RollingMax", 24, "agg_price_range_bps"): "agg_price_range_bps_max_24h",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def git_show(commit: str, path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True, encoding="utf-8"
    )


def validate_audit_provenance() -> dict[str, str]:
    object_type = subprocess.check_output(
        ["git", "cat-file", "-t", AUDIT_COMMIT_SHA],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    ).strip()
    if object_type != "commit" or not re.fullmatch(r"[0-9a-f]{40}", AUDIT_COMMIT_SHA):
        raise AssertionError(
            f"audit commit provenance is not a valid single commit SHA: {AUDIT_COMMIT_SHA} ({object_type})"
        )
    return dict(AUDIT_ROW_PROVENANCE)


def require_source_evidence() -> dict[str, str]:
    formatter = git_show(HISTORICAL_COMMIT, HISTORICAL_FORMATTER_PATH)
    evaluator = git_show(HISTORICAL_COMMIT, HISTORICAL_EVALUATOR_PATH)
    current = CURRENT_BASE_FORMULA_PATH.read_text(encoding="utf-8")

    required_formatter = [
        'return f"ZScore(TSMean({field},{window}))"',
        'return f"HorizonSpread({agg_field},4,24)"',
        'return f"SmoothInteraction({agg_field},TSMean({market_field},12))"',
        'return f"SafeDiv({a},Clip(Abs(ZScore({market_field})),0.05,4.0))"',
    ]
    required_evaluator = [
        'if op in {"Rank", "CrossSymbolRank"}:',
        'if op in {"ZScore", "CrossSymbolZScore"}:',
        'if op == "ShareOfUniverse":',
        'if op == "HorizonSpread":',
        'if op == "SmoothInteraction":',
    ]
    required_current = [
        'out["agg_flow_imbalance_notional"] =',
        'out[f"agg_notional_sum_{window}h"] =',
        'out["agg_cross_symbol_notional_share"] =',
        'out[f"agg_flow_minus_{prefix}_4h"] =',
    ]
    for label, text, needles in [
        ("historical formatter", formatter, required_formatter),
        ("historical evaluator", evaluator, required_evaluator),
        ("current base formula source", current, required_current),
    ]:
        missing = [needle for needle in needles if needle not in text]
        if missing:
            raise AssertionError(f"{label} evidence changed or missing: {missing}")
    return {
        "historical_formatter_sha256": sha256_bytes(formatter.encode("utf-8")),
        "historical_evaluator_sha256": sha256_bytes(evaluator.encode("utf-8")),
        "current_base_formula_source_sha256": sha256_bytes(current.encode("utf-8")),
    }


def validate_input_hashes() -> dict[str, str]:
    manifest = {row["file"]: row["sha256"].upper() for row in read_csv(ASSET_MANIFEST_INPUT)}
    paths = [BASE_INPUT, DERIVED_INPUT, LINEAGE_INPUT, MAP_INPUT, CURRENT_EPOCH_INPUT]
    hashes: dict[str, str] = {}
    for path in paths:
        actual = sha256_path(path)
        expected = manifest.get(path.name)
        if expected != actual:
            raise AssertionError(f"input hash mismatch for {path.name}: {actual} != {expected}")
        hashes[path.name] = actual
    return hashes


def canonical_axis(field: str) -> str:
    if field in MARKET_AXIS:
        return MARKET_AXIS[field]
    if field in METADATA_FIELDS:
        return "INTEGRITY_TRADE_BOUNDARY_METADATA"
    if field in UNRESOLVED_FORMULA_FIELDS:
        return f"UNRESOLVED::{field}"
    if "underlying_trade_count" in field or "underlying_trades_per_agg" in field:
        return "TRADE_AGGREGATION_MULTIPLICITY"
    if "trade_count" in field and "large" not in field:
        return "TRADE_ACTIVITY_COUNT"
    if "quantity" in field:
        return "AGGRESSOR_QUANTITY_FLOW" if any(x in field for x in ["signed", "buy", "sell", "imbalance", "flow"]) else "EXECUTED_QUANTITY"
    if any(
        x in field
        for x in [
            "flow_imbalance",
            "flow_accel",
            "flow_minus",
            "signed_flow",
            "signed_notional",
            "buy_notional",
            "sell_notional",
            "buy_sell_notional",
        ]
    ):
        return "AGGRESSOR_NOTIONAL_FLOW"
    if "large" in field:
        return "LARGE_TRADE_INTENSITY" if any(x in field for x in ["share", "ratio", "count"]) else "LARGE_TRADE_NOTIONAL"
    if "notional" in field:
        return "TRADE_SIZE_MEAN" if "avg" in field else "EXECUTED_NOTIONAL"
    if "buy_sell_vwap" in field or "buy_vwap" in field or "sell_vwap" in field:
        return "AGGRESSOR_SIDE_PRICE"
    if any(x in field for x in ["price", "vwap", "open", "close"]):
        return "TRADE_PRICE_PATH"
    if "volume_imbalance" in field:
        return "AGGRESSOR_QUANTITY_FLOW"
    return f"UNRESOLVED::{field}"


def unit_signature(field: str) -> str:
    if field in MARKET_AXIS:
        if field.startswith("ret_"):
            return "DIMENSIONLESS_RETURN"
        if field.startswith("realized_vol_"):
            return "DIMENSIONLESS_VOLATILITY"
        return "DIMENSIONLESS_RATE_OR_RATIO"
    if field.endswith("_id"):
        return "IDENTIFIER"
    if "transact_time_ms" in field:
        return "TIMESTAMP_MS"
    if any(x in field for x in ["share", "ratio", "imbalance", "accel", "shock", "_z_"]):
        return "DIMENSIONLESS"
    if "bps" in field:
        return "BASIS_POINTS"
    if "count" in field or "trades_per_agg" in field:
        return "COUNT"
    if "quantity" in field:
        return "BASE_ASSET_QUANTITY"
    if "notional" in field:
        return "QUOTE_NOTIONAL"
    if any(x in field for x in ["price", "vwap"]):
        return "QUOTE_PER_BASE_PRICE"
    return "UNKNOWN"


def classify_base(field: str, family: str) -> str:
    if field in METADATA_FIELDS:
        return "INTEGRITY_METADATA"
    if field in UNRESOLVED_FORMULA_FIELDS:
        return "FORMULA_PROVENANCE_UNRESOLVED"
    if family == "rolling":
        return "ROLLING_DERIVED"
    if family == "cross_symbol":
        return "CROSS_SYMBOL_DERIVED"
    if field in NORMALIZED_FIELDS:
        return "NORMALIZED_REPRESENTATION"
    if field in RAW_SOURCE_DECLARATION_FIELDS:
        return "RAW_OBSERVATION"
    return "FORMULA_PROVENANCE_UNRESOLVED"


def base_formula_status(field: str, classification: str) -> tuple[str, str]:
    if field in METADATA_FIELDS:
        return (
            "REGISTRY_ONLY_METADATA_FORMULA_EXTERNAL",
            "feature_lineage_ledger.csv:REGISTRY_RECOVERED_FORMULA_DETAIL_EXTERNAL",
        )
    if field in UNRESOLVED_FORMULA_FIELDS:
        mismatch = field == "agg_universe_signed_notional"
        status = "NAME_MISMATCH_WITH_CURRENT_BUILDER_UNRESOLVED" if mismatch else "REGISTRY_ONLY_FORMULA_EXTERNAL"
        return status, "feature_lineage_ledger.csv:REGISTRY_RECOVERED_FORMULA_DETAIL_EXTERNAL"
    if classification == "ROLLING_DERIVED":
        if "signed_quantity_sum" in field:
            return (
                "REGISTRY_ONLY_FORMULA_EXTERNAL",
                "feature_lineage_ledger.csv:REGISTRY_RECOVERED_FORMULA_DETAIL_EXTERNAL",
            )
        return "CURRENT_BUILDER_FORMULA_RECOVERED", "scripts/crypto_a7ai0r_core12_aggtrades_unified_feature_build.py:161-184"
    if classification == "CROSS_SYMBOL_DERIVED":
        return "CURRENT_BUILDER_FORMULA_RECOVERED", "scripts/crypto_a7ai0r_core12_aggtrades_unified_feature_build.py:186-201"
    if field in CURRENT_FORMULA_FIELDS:
        return "CURRENT_BUILDER_FORMULA_RECOVERED", "scripts/crypto_a7ai0r_core12_aggtrades_unified_feature_build.py:154-159"
    if field in RAW_SOURCE_DECLARATION_FIELDS:
        return "CURRENT_BUILDER_SOURCE_COLUMN_DECLARATION", "scripts/crypto_a7ai0r_core12_aggtrades_unified_feature_build.py:50-79"
    return "REGISTRY_ONLY_FORMULA_EXTERNAL", "feature_lineage_ledger.csv:REGISTRY_RECOVERED_FORMULA_DETAIL_EXTERNAL"


def base_dependencies(field: str, formula_status: str) -> list[str]:
    if "UNRESOLVED" in formula_status or formula_status.startswith("REGISTRY_ONLY"):
        return [f"UNRESOLVED::{field}"]
    direct: dict[str, list[str]] = {
        "agg_vwap_close_bps": ["agg_vwap", "agg_close_price"],
        "agg_buy_sell_vwap_spread_bps": ["agg_buy_vwap", "agg_sell_vwap"],
        "agg_avg_underlying_trades_per_agg": ["agg_underlying_trade_count", "agg_trade_count"],
        "agg_flow_imbalance_notional": ["agg_signed_aggressor_notional", "agg_notional"],
        "agg_buy_notional_share": ["agg_buy_notional", "agg_notional"],
        "agg_sell_notional_share": ["agg_sell_notional", "agg_notional"],
        "agg_notional_shock_24h_mad": ["agg_notional"],
        "agg_signed_flow_z_24h": ["agg_signed_aggressor_notional"],
        "agg_notional_accel_4h_vs_24h": ["agg_notional"],
        "agg_flow_accel_4h_vs_24h": ["agg_signed_aggressor_notional", "agg_notional"],
        "agg_universe_notional": ["agg_notional"],
        "agg_universe_large_notional": ["agg_large_notional_100k_plus"],
        "agg_cross_symbol_notional_share": ["agg_notional"],
        "agg_cross_symbol_signed_flow_share": ["agg_signed_aggressor_notional"],
        "agg_cross_symbol_large_notional_share": ["agg_large_notional_100k_plus"],
        "agg_btcusdt_flow_imbalance_4h": ["agg_signed_aggressor_notional", "agg_notional"],
        "agg_flow_minus_btcusdt_4h": ["agg_signed_aggressor_notional", "agg_notional"],
        "agg_ethusdt_flow_imbalance_4h": ["agg_signed_aggressor_notional", "agg_notional"],
        "agg_flow_minus_ethusdt_4h": ["agg_signed_aggressor_notional", "agg_notional"],
    }
    if field in direct:
        return direct[field]
    rolling_patterns = [
        (r"agg_notional_sum_(?:4|24)h", "agg_notional"),
        (r"agg_quantity_sum_(?:4|24)h", "agg_quantity"),
        (r"agg_signed_notional_sum_(?:4|24)h", "agg_signed_aggressor_notional"),
        (r"agg_flow_imbalance_notional_(?:4|24)h", "agg_signed_aggressor_notional;agg_notional"),
        (r"agg_large_notional_sum_(?:4|24)h", "agg_large_notional_100k_plus"),
        (r"agg_large_notional_share_(?:4|24)h", "agg_large_notional_100k_plus;agg_notional"),
        (r"agg_trade_count_sum_(?:4|24)h", "agg_trade_count"),
        (r"agg_avg_trade_notional_(?:4|24)h", "agg_notional;agg_trade_count"),
        (r"agg_price_range_bps_max_(?:4|24)h", "agg_price_range_bps"),
        (r"agg_close_to_open_bps_sum_(?:4|24)h", "agg_close_to_open_bps"),
    ]
    for pattern, dependencies in rolling_patterns:
        if re.fullmatch(pattern, field):
            return dependencies.split(";")
    return [field]


def base_window_family(field: str, classification: str) -> str:
    if classification == "CROSS_SYMBOL_DERIVED":
        return "CORE12_INSTANTANEOUS_CROSS_SECTION_IN_CURRENT_BUILDER"
    if "4h_vs_24h" in field:
        return "4H_VS_24H"
    match = re.search(r"_(4|24)h(?:_|$)", field)
    if match:
        return f"{match.group(1)}H_ROLLING"
    return "1H_AGGREGATE"


def base_depth(field: str, classification: str, formula_status: str) -> int:
    if "UNRESOLVED" in formula_status or formula_status.startswith("REGISTRY_ONLY"):
        return -1
    if classification in {"RAW_OBSERVATION", "INTEGRITY_METADATA"}:
        return 0
    if classification == "NORMALIZED_REPRESENTATION":
        return 1
    if classification == "ROLLING_DERIVED":
        return 2 if any(x in field for x in ["accel", "share_", "avg_trade", "flow_imbalance"]) else 1
    if classification == "CROSS_SYMBOL_DERIVED":
        return 2 if any(x in field for x in ["share", "minus", "flow_imbalance_4h"]) else 1
    return -1


def base_equivalence(field: str) -> tuple[str, str]:
    if field in METADATA_FIELDS:
        return "NON_ALPHA_METADATA", "HIGH_METADATA_MISUSE_RISK"
    if field in MIRROR_PARTNERS:
        partner = MIRROR_PARTNERS[field]
        if field in UNRESOLVED_SIDE_MIRROR_FIELDS:
            return (
                f"CONDITIONAL_SIDE_MIRROR_CANDIDATE_FORMULA_UNRESOLVED_WITH::{partner}",
                "FORMULA_UNRESOLVED_NO_NUMERIC_OR_RANK_EQUIVALENCE_CLAIM",
            )
        if "share" in field:
            return (
                f"CONDITIONAL_AFFINE_COMPLEMENT_WITH::{partner}",
                "CONDITIONAL_RANK_REVERSAL_IF_BUY_SELL_PARTITION_EQUALS_TOTAL",
            )
        return (
            f"SIDE_MIRROR_PAIR_WITH::{partner}",
            "MIRROR_DEPENDENCE_RISK_FORMULA_PROVENANCE_REQUIRED",
        )
    if any(x in field for x in ["share", "imbalance", "ratio"]):
        return "NORMALIZED_REPRESENTATION_OF_PARENT_FLOW", "MONOTONIC_DUPLICATION_RISK_NOT_PROVEN"
    return "NONE_PROVEN", "NONE_PROVEN"


def make_base_audit(
    base_rows: list[dict[str, str]],
    lineage_by_id: dict[str, dict[str, str]],
    map_by_id: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    output: list[dict[str, Any]] = []
    by_field: dict[str, dict[str, Any]] = {}
    for ordinal, row in enumerate(base_rows, start=1):
        field = row["field_name"]
        family = row["field_family"]
        classification = classify_base(field, family)
        if classification not in ALLOWED_BASE_CLASSIFICATIONS:
            raise AssertionError(f"invalid base classification: {classification}")
        formula_status, formula_evidence = base_formula_status(field, classification)
        dependencies = sorted(set(base_dependencies(field, formula_status)))
        axis = canonical_axis(field)
        if (
            axis.startswith("UNRESOLVED::")
            or "UNRESOLVED" in formula_status
            or (formula_status.startswith("REGISTRY_ONLY") and classification != "INTEGRITY_METADATA")
        ):
            axis_status = "UNRESOLVED_FORMULA_OR_SEMANTICS"
        elif classification == "INTEGRITY_METADATA":
            axis_status = "RESOLVED_NON_ALPHA_METADATA"
        elif formula_status == "CURRENT_BUILDER_FORMULA_RECOVERED":
            axis_status = "RESOLVED_FORMULA_EVIDENCE"
        else:
            axis_status = "RESOLVED_SOURCE_SEMANTICS_FORMULA_EXTERNAL"
        algebraic, rank_risk = base_equivalence(field)
        mapping = map_by_id[field]
        lineage = lineage_by_id[field]
        scope = [
            "STATIC_ONLY_NOT_CURRENT_RUNTIME_LOADED",
            row["availability_scope"],
            f"symbol_scope={row['cross_symbol_scope']}",
            f"available_lag_bars={row['feature_available_lag_bars']}",
        ]
        if field in METADATA_FIELDS:
            scope.append("MUST_NOT_BE_TREATED_AS_ALPHA_WITHOUT_EXPLICIT_SEMANTIC_JUSTIFICATION")
        if classification == "CROSS_SYMBOL_DERIVED":
            scope.extend(
                [
                    "FORMULA_EVIDENCE_CURRENT_CORE12_WHILE_A7V1_REGISTRY_SCOPE_CORE3",
                    "NUMERIC_IDENTITY_ACROSS_UNIVERSE_SCOPE_NOT_CLAIMED",
                ]
            )
        audited = {
            "source_row_ordinal": ordinal,
            **AUDIT_ROW_PROVENANCE,
            "field_name": field,
            "field_family": family,
            "base_classification": classification,
            "formula_provenance_status": formula_status,
            "formula_evidence": formula_evidence,
            "base_dependency_set": ";".join(dependencies),
            "canonical_information_axis": axis,
            "axis_resolution_status": axis_status,
            "static_independence_status": "NOT_IDENTIFIABLE_STATICALLY",
            "unit_signature": unit_signature(field),
            "window_family": base_window_family(field, classification),
            "nested_derivation_depth": base_depth(field, classification, formula_status),
            "algebraic_equivalence": algebraic,
            "monotonic_rank_equivalence_risk": rank_risk,
            "scope_restrictions": ";".join(scope),
            "generator_enabled": row["generator_enabled"].lower(),
            "runtime_loaded": mapping["runtime_loaded"].lower(),
            "mapping_status": mapping["mapping_status"],
            "lineage_status": lineage["lineage_status"],
            "audit_notes": "classification is structural only; no numeric values, returns, selectors, or performance artifacts were read",
        }
        output.append(audited)
        by_field[field] = audited
    return output, by_field


def split_fields(text: str) -> list[str]:
    return [part.strip() for part in text.split(";") if part.strip()]


def reconstruct_expression(family: str, transform: str, fields: list[str], window: int) -> str:
    if family == "rolling_self_reproduction":
        field = fields[0]
        if transform == "ZScore":
            return f"ZScore(TSMean({field},{window}))"
        return f"{transform}({field},{window})"
    if family == "cross_symbol_self_reproduction_core3":
        return f"{transform}({fields[0]})"
    agg = fields[0]
    market = fields[1]
    a = f"ZScore({agg})"
    b = f"Rank({market})"
    if transform in {"Mul", "Add", "Sub"}:
        return f"{transform}({a},{b})"
    if transform == "SafeDiv":
        return f"SafeDiv({a},Clip(Abs(ZScore({market})),0.05,4.0))"
    if transform == "HorizonSpread":
        return f"HorizonSpread({agg},4,24)"
    if transform == "SmoothInteraction":
        return f"SmoothInteraction({agg},TSMean({market},12))"
    raise AssertionError(f"unknown interaction transform: {transform}")


def effective_spec_dependencies(family: str, transform: str, fields: list[str]) -> list[str]:
    if family == "interaction_self_reproduction" and transform == "HorizonSpread":
        return [fields[0]]
    return fields


def expand_raw_dependencies(fields: Iterable[str], base_by_field: dict[str, dict[str, Any]]) -> list[str]:
    expanded: set[str] = set()
    for field in fields:
        if field in MARKET_AXIS:
            expanded.add(field)
            continue
        base = base_by_field.get(field)
        if base is None:
            expanded.add(f"UNRESOLVED::{field}")
            continue
        expanded.update(split_fields(str(base["base_dependency_set"])))
    return sorted(expanded)


def effective_axis(fields: Iterable[str], base_by_field: dict[str, dict[str, Any]]) -> tuple[str, str]:
    axes: set[str] = set()
    unresolved = False
    for field in fields:
        if field in MARKET_AXIS:
            axis = MARKET_AXIS[field]
        else:
            base = base_by_field[field]
            axis = str(base["canonical_information_axis"])
            if base["axis_resolution_status"] == "UNRESOLVED_FORMULA_OR_SEMANTICS" and not axis.startswith("UNRESOLVED::"):
                axis = f"UNRESOLVED_INFERRED::{field}::{axis}"
        axes.add(axis)
        unresolved = unresolved or axis.startswith("UNRESOLVED::")
    if len(axes) == 1:
        label = next(iter(axes))
    else:
        label = "JOINT[" + "+".join(sorted(axes)) + "]"
    return label, "UNRESOLVED_DEPENDENCY_BUCKET" if unresolved else "RESOLVED_CANONICAL_DEPENDENCY_BUCKET"


def transformed_unit(family: str, transform: str, fields: list[str], base_by_field: dict[str, dict[str, Any]]) -> str:
    base_unit = unit_signature(fields[0]) if fields[0] in MARKET_AXIS else str(base_by_field[fields[0]]["unit_signature"])
    if family == "rolling_self_reproduction":
        return "DIMENSIONLESS" if transform == "ZScore" else base_unit
    if family == "cross_symbol_self_reproduction_core3":
        return base_unit if transform in {"RelativeToBTC", "RelativeToETH"} else "DIMENSIONLESS"
    if transform == "HorizonSpread":
        return base_unit
    return "DIMENSIONLESS"


def transform_family(family: str, transform: str) -> str:
    if family == "rolling_self_reproduction":
        if transform == "ZScore":
            return "ROLLING_MEAN_THEN_CROSS_SECTIONAL_ZSCORE"
        return {
            "TSMean": "ROLLING_LOCATION",
            "TSStd": "ROLLING_DISPERSION",
            "Delta": "TEMPORAL_DIFFERENCE",
            "Decay": "EXPONENTIAL_SMOOTHING",
            "RollingMin": "ROLLING_EXTREME",
            "RollingMax": "ROLLING_EXTREME",
        }[transform]
    if family == "cross_symbol_self_reproduction_core3":
        return "CROSS_SECTIONAL_ORDER_PRESERVING_REPRESENTATION"
    return {
        "Mul": "NORMALIZED_BINARY_INTERACTION",
        "Add": "NORMALIZED_COORDINATE_ADD",
        "Sub": "NORMALIZED_COORDINATE_SUB",
        "SafeDiv": "CLIPPED_DENOMINATOR_NORMALIZED_RATIO_WITH_AMPLIFICATION_RISK",
        "HorizonSpread": "FIXED_TEMPORAL_SCALE_SPREAD",
        "SmoothInteraction": "CROSS_SECTIONAL_SMOOTH_INTERACTION",
    }[transform]


def derived_depth(
    family: str,
    transform: str,
    effective_fields: list[str],
    base_by_field: dict[str, dict[str, Any]],
) -> int:
    depths = [
        0 if field in MARKET_AXIS else int(base_by_field[field]["nested_derivation_depth"])
        for field in effective_fields
    ]
    if any(depth < 0 for depth in depths):
        return -1
    increment = 1
    if family == "rolling_self_reproduction" and transform == "ZScore":
        increment = 2
    elif family == "interaction_self_reproduction" and transform in {"Mul", "Add", "Sub", "SmoothInteraction"}:
        increment = 2
    elif family == "interaction_self_reproduction" and transform == "SafeDiv":
        increment = 3
    return max(depths) + increment


def derived_equivalence(
    family: str,
    transform: str,
    fields: list[str],
    window: int,
) -> tuple[str, str, int, str]:
    if family == "interaction_self_reproduction" and transform == "HorizonSpread":
        group = f"EXACT_HORIZON_SPREAD_4H_24H::{fields[0]}"
        return "EXACT_DUPLICATE_MARKET_FIELD_UNUSED", group, 7, "HIGH_EXACT_EXPRESSION_DUPLICATION"
    equivalent_base = POSITIVE_SCALE_EQUIVALENT_BASE.get((transform, window, fields[0]))
    if equivalent_base:
        kind = "CONDITIONAL_IDENTITY_TO_BASE" if transform == "RollingMax" else "CONDITIONAL_POSITIVE_SCALE_EQUIVALENT_TO_BASE"
        return (
            kind + f"::{equivalent_base}::AFTER_FULL_VALID_WINDOW",
            f"BASE_EQUIVALENCE::{equivalent_base}",
            2,
            "HIGH_RANK_EQUIVALENT_WHEN_FULL_WINDOW_AND_MISSINGNESS_MATCH",
        )
    if family == "cross_symbol_self_reproduction_core3":
        return (
            "NONE_PROVEN_NUMERICALLY",
            f"RANK_ORDER_EQUIVALENCE::{fields[0]}",
            6,
            "PROVEN_ORDER_PRESERVING_OR_EXPLICIT_RANK_ENCODING",
        )
    if family == "interaction_self_reproduction" and transform == "SafeDiv":
        return (
            "NONE_PROVEN",
            "",
            0,
            "STRUCTURAL_UP_TO_20X_AMPLIFICATION_AND_CLIP_FLOOR_RERANK_RISK_NOT_EMPIRICALLY_TESTED",
        )
    if fields[0] in UNRESOLVED_SIDE_MIRROR_FIELDS:
        return (
            f"CONDITIONAL_SIDE_MIRROR_CANDIDATE_FORMULA_UNRESOLVED_WITH::{MIRROR_PARTNERS[fields[0]]}",
            "",
            0,
            "FORMULA_UNRESOLVED_NO_NUMERIC_OR_RANK_EQUIVALENCE_CLAIM",
        )
    if fields[0] in MIRROR_PARTNERS:
        return (
            f"CONDITIONAL_SIDE_MIRROR_WITH::{MIRROR_PARTNERS[fields[0]]}",
            "",
            0,
            "CONDITIONAL_MIRROR_RANK_EQUIVALENCE_NOT_PROVEN",
        )
    return "NONE_PROVEN", "", 0, "NONE_PROVEN"


def derived_scope(
    family: str,
    transform: str,
    fields: list[str],
    base_by_field: dict[str, dict[str, Any]],
) -> tuple[str, str]:
    restrictions = ["STATIC_SPEC_NOT_PROOF_OF_FULL_MATERIALIZATION", "STATIC_ONLY_NOT_CURRENT_RUNTIME_LOADED", "AGG_MASK_REQUIRED"]
    notes: list[str] = []
    if family == "cross_symbol_self_reproduction_core3":
        restrictions.extend(["CORE3_ONLY", "CROSS_SECTIONAL_DOF_AT_MOST_2", "MAXIMUM_THREE_UNIQUE_RANKS"])
    elif family == "rolling_self_reproduction":
        if base_by_field[fields[0]]["field_family"] == "rolling":
            restrictions.append("ROLLING_ON_ROLLING")
        if base_by_field[fields[0]]["base_classification"] == "INTEGRITY_METADATA":
            restrictions.append("ID_OR_TIMESTAMP_METADATA_USED_AS_GENERATOR_INPUT")
        if transform == "ZScore":
            restrictions.extend(["DECLARED_SAME_SYMBOL_BUT_EXECUTED_CROSS_SECTIONALLY", "EFFECTIVE_CORE3_CROSS_SECTIONAL_DOF_AT_MOST_2"])
            notes.append("historical formatter emits ZScore(TSMean(field,window)); evaluator implements ZScore as row-wise cross-sectional z-score")
    else:
        if transform == "HorizonSpread":
            restrictions.append("DECLARED_MARKET_FIELD_UNUSED")
            notes.append("all seven market-field labels per agg seed collapse to the same fixed 4h-minus-24h expression")
        else:
            restrictions.extend(["EFFECTIVE_CORE3_CROSS_SECTION_VIA_ZSCORE_OR_RANK", "CROSS_SECTIONAL_DOF_AT_MOST_2"])
        if transform in {"Add", "Sub"}:
            restrictions.append("DIMENSIONLESS_BUT_MIXED_ZSCORE_AND_PERCENTILE_COORDINATES")
            notes.append("no cross-unit arithmetic: formatter normalizes agg to z-score and market field to percentile rank")
        if transform == "SafeDiv":
            restrictions.extend(
                [
                    "DENOMINATOR_ABS_ZSCORE_CLIPPED_TO_0.05_4.0",
                    "STRUCTURAL_MAX_ABSOLUTE_RECIPROCAL_MULTIPLIER_20X",
                    "POTENTIAL_DISCONTINUOUS_RERANK_AT_CLIP_FLOOR",
                ]
            )
            notes.append(
                "clip floor prevents division by zero but permits up to 20x reciprocal amplification; empirical instability is not claimed without numeric evaluation"
            )
    return ";".join(restrictions), ";".join(notes)


def make_derived_audit(
    derived_rows: list[dict[str, str]],
    base_by_field: dict[str, dict[str, Any]],
    map_by_id: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for ordinal, row in enumerate(derived_rows, start=1):
        feature_id = row["derived_feature_id"]
        family = row["production_family"]
        transform = row["transform"]
        window = int(row["window_hours"])
        declared_fields = split_fields(row["base_fields"])
        effective_fields = effective_spec_dependencies(family, transform, declared_fields)
        expression = reconstruct_expression(family, transform, declared_fields, window)
        raw_dependencies = expand_raw_dependencies(effective_fields, base_by_field)
        axis, axis_status = effective_axis(effective_fields, base_by_field)
        algebraic, group_id, group_size, rank_risk = derived_equivalence(family, transform, declared_fields, window)
        scope, notes = derived_scope(family, transform, declared_fields, base_by_field)
        mapping = map_by_id[feature_id]
        if mapping["runtime_loaded"].lower() != "false" or mapping["mapping_status"] != "STATIC_ONLY":
            raise AssertionError(f"unexpected runtime mapping for {feature_id}")
        if family == "rolling_self_reproduction":
            window_family = f"{window}H_ROLLING"
        elif family == "cross_symbol_self_reproduction_core3":
            window_family = "1H_CORE3_CROSS_SECTION"
        elif transform == "HorizonSpread":
            window_family = "FIXED_4H_VS_24H"
        elif transform == "SmoothInteraction":
            window_family = "1H_AGG_WITH_12H_MARKET_SMOOTHING"
        else:
            window_family = "1H_POINTWISE_WITH_CROSS_SECTIONAL_NORMALIZATION"
        output.append(
            {
                "source_row_ordinal": ordinal,
                **AUDIT_ROW_PROVENANCE,
                "derived_feature_id": feature_id,
                "production_family": family,
                "transform": transform,
                "declared_base_fields": ";".join(declared_fields),
                "effective_spec_dependencies": ";".join(effective_fields),
                "base_dependency_set": ";".join(raw_dependencies),
                "canonical_information_axis": axis,
                "axis_resolution_status": axis_status,
                "static_independence_status": "NOT_IDENTIFIABLE_STATICALLY",
                "unit_signature": transformed_unit(family, transform, declared_fields, base_by_field),
                "window_family": window_family,
                "transform_family": transform_family(family, transform),
                "nested_derivation_depth": derived_depth(family, transform, effective_fields, base_by_field),
                "algebraic_equivalence": algebraic,
                "equivalence_group_id": group_id,
                "equivalence_group_size_including_referenced_base_when_applicable": group_size,
                "monotonic_rank_equivalence_risk": rank_risk,
                "scope_restrictions": scope,
                "formula_provenance_status": "HISTORICAL_DRY_RUN_FORMATTER_AND_REPLAY_EVALUATOR_RECOVERED",
                "formula_evidence": (
                    f"git:{HISTORICAL_COMMIT}:{HISTORICAL_FORMATTER_PATH};"
                    f"git:{HISTORICAL_COMMIT}:{HISTORICAL_EVALUATOR_PATH}"
                ),
                "reconstructed_expression": expression,
                "expression_sha256": sha256_bytes(expression.encode("utf-8")),
                "runtime_loaded": mapping["runtime_loaded"].lower(),
                "mapping_status": mapping["mapping_status"],
                "audit_notes": notes,
            }
        )
    return output


def csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        raise AssertionError("cannot serialize empty audit")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def count_where(rows: list[dict[str, Any]], predicate: Any) -> int:
    return sum(1 for row in rows if predicate(row))


def make_summary(
    base_rows: list[dict[str, Any]],
    derived_rows: list[dict[str, Any]],
    source_hashes: dict[str, str],
    evidence_hashes: dict[str, str],
    row_provenance: dict[str, str],
    map_validation: dict[str, Any],
    base_payload: bytes,
    derived_payload: bytes,
) -> dict[str, Any]:
    resolved_dependency_buckets = {
        row["canonical_information_axis"]
        for row in derived_rows
        if row["axis_resolution_status"] == "RESOLVED_CANONICAL_DEPENDENCY_BUCKET"
    }
    unresolved_dependency_sets = {
        row["canonical_information_axis"]
        for row in derived_rows
        if row["axis_resolution_status"] != "RESOLVED_CANONICAL_DEPENDENCY_BUCKET"
    }
    resolved_base_axes = {
        row["canonical_information_axis"]
        for row in base_rows
        if not str(row["canonical_information_axis"]).startswith("UNRESOLVED::")
        and row["base_classification"] != "INTEGRITY_METADATA"
    }
    resolved_nonmetadata_dependency_buckets = {
        bucket for bucket in resolved_dependency_buckets if "INTEGRITY_" not in bucket
    }
    expression_counts = Counter(row["reconstructed_expression"] for row in derived_rows)
    exact_duplicate_rows = sum(count - 1 for count in expression_counts.values() if count > 1)

    risk_counts = {
        "rolling_on_rolling_specs": count_where(derived_rows, lambda r: "ROLLING_ON_ROLLING" in r["scope_restrictions"]),
        "metadata_input_specs": count_where(derived_rows, lambda r: "ID_OR_TIMESTAMP_METADATA" in r["scope_restrictions"]),
        "core3_low_dof_specs": count_where(derived_rows, lambda r: "DOF_AT_MOST_2" in r["scope_restrictions"]),
        "rolling_zscore_scope_drift_specs": count_where(derived_rows, lambda r: "DECLARED_SAME_SYMBOL" in r["scope_restrictions"]),
        "horizon_spread_declared_dependency_dropped_specs": count_where(derived_rows, lambda r: "DECLARED_MARKET_FIELD_UNUSED" in r["scope_restrictions"]),
        "horizon_spread_exact_redundant_rows": 30,
        "conditional_scale_or_identity_equivalent_to_existing_base_specs": count_where(
            derived_rows,
            lambda r: r["algebraic_equivalence"].startswith("CONDITIONAL_POSITIVE_SCALE")
            or r["algebraic_equivalence"].startswith("CONDITIONAL_IDENTITY"),
        ),
        "cross_symbol_order_preserving_specs": count_where(
            derived_rows, lambda r: r["monotonic_rank_equivalence_risk"] == "PROVEN_ORDER_PRESERVING_OR_EXPLICIT_RANK_ENCODING"
        ),
        "conditional_buy_sell_mirror_specs": count_where(
            derived_rows, lambda r: r["algebraic_equivalence"].startswith("CONDITIONAL_SIDE_MIRROR")
        ),
        "mixed_physical_unit_add_sub_specs": 0,
        "mixed_normalized_coordinate_add_sub_specs": count_where(
            derived_rows, lambda r: "MIXED_ZSCORE_AND_PERCENTILE" in r["scope_restrictions"]
        ),
        "safediv_specs_with_bounded_denominator_guard": count_where(
            derived_rows, lambda r: "DENOMINATOR_ABS_ZSCORE_CLIPPED" in r["scope_restrictions"]
        ),
        "safediv_specs_with_structural_up_to_20x_amplification_and_clip_floor_rerank_risk": count_where(
            derived_rows, lambda r: "STRUCTURAL_MAX_ABSOLUTE_RECIPROCAL_MULTIPLIER_20X" in r["scope_restrictions"]
        ),
        "safediv_empirical_instability_claimed": False,
        "formula_or_dependency_bucket_unresolved_specs": count_where(
            derived_rows,
            lambda r: r["axis_resolution_status"] != "RESOLVED_CANONICAL_DEPENDENCY_BUCKET",
        ),
    }

    content_identity = {
        "base_output_sha256": sha256_bytes(base_payload),
        "derived_output_sha256": sha256_bytes(derived_payload),
        "source_hashes": source_hashes,
        "evidence_hashes": evidence_hashes,
    }
    return {
        "stage": "CRYPTO_LATEST_FEATURE_SPACE_INDEPENDENT_AUDIT",
        "audit_date": "2026-07-14",
        "evidence_boundary": {
            "read_numeric_feature_values": False,
            "read_returns_or_performance": False,
            "read_selector_outputs": False,
            "ran_search": False,
            "integrated_new_data": False,
            "registry_specs_are_not_assumed_materialized": True,
            "materialization_claim": "A7V1_REGISTERED_STATIC_SPECS; only historical smoke subsets have recovered evaluator evidence",
        },
        "source_identity": content_identity,
        "row_provenance_contract": row_provenance,
        "counts": {
            "base_registry_rows": len(base_rows),
            "base_classification_counts": dict(sorted(Counter(row["base_classification"] for row in base_rows).items())),
            "resolved_nonmetadata_base_canonical_bucket_count": len(resolved_base_axes),
            "unresolved_base_field_count": count_where(
                base_rows, lambda r: str(r["canonical_information_axis"]).startswith("UNRESOLVED::")
            ),
            "derived_spec_rows": len(derived_rows),
            "production_family_counts": dict(sorted(Counter(row["production_family"] for row in derived_rows).items())),
            "transform_counts": dict(sorted(Counter(row["transform"] for row in derived_rows).items())),
            "reconstructed_expression_identity_count": len(expression_counts),
            "exact_duplicate_expression_rows_beyond_first": exact_duplicate_rows,
            "resolved_canonical_dependency_bucket_count_including_nonalpha_metadata": len(
                resolved_dependency_buckets
            ),
            "resolved_nonmetadata_canonical_dependency_bucket_count": len(
                resolved_nonmetadata_dependency_buckets
            ),
            "unresolved_canonical_dependency_set_count": len(unresolved_dependency_sets),
        },
        "canonical_dependency_bucket_inventory": {
            "resolved_nonmetadata_base_canonical_buckets": sorted(resolved_base_axes),
            "resolved_derived_dependency_buckets_including_nonalpha_metadata": sorted(
                resolved_dependency_buckets
            ),
            "resolved_nonmetadata_derived_dependency_buckets": sorted(
                resolved_nonmetadata_dependency_buckets
            ),
            "unresolved_derived_dependency_sets": sorted(unresolved_dependency_sets),
        },
        "static_identifiability_contract": {
            "independent_axis_count": "NOT_IDENTIFIABLE_STATICALLY",
            "resolved_nonmetadata_canonical_dependency_bucket_count_for_5211_specs": len(
                resolved_nonmetadata_dependency_buckets
            ),
            "unresolved_canonical_dependency_set_count": len(unresolved_dependency_sets),
            "bucket_definition": "unique effective canonical dependency labels with formula-resolved dependencies; a bucket is not an independent axis",
            "does_not_claim": "statistical independence, empirical numeric or rank equivalence outside proven formula identities, materialization of all specs, or economic usefulness",
            "risk_flags_are_not_subtracted_as_exact_equivalence": True,
        },
        "runtime_map_validation": map_validation,
        "structural_risk_counts": risk_counts,
        "proven_equivalence_scope": {
            "exact_expression_duplicates": "HorizonSpread interaction labels that drop the market dependency",
            "conditional_scale_or_identity": "only recovered formula pairs, and only after a full valid matched window; missing-data differences are not claimed equivalent",
            "rank_order_equivalence": "core3 cross-symbol rank, zscore, common-denominator share, and common-reference subtraction when finite and nondegenerate",
            "conditional_only": "buy/sell mirror and share/imbalance/ratio relations when the missing upstream partition formula is required",
            "unknown": "numeric correlation, equality under missing-data differences, and portfolio-weight equivalence",
        },
        "limitations": [
            "All 94 recovered lineage rows say exact upstream data-builder formula is external to the A7V1 registry.",
            "Current Git source recovers formulas for a subset and exposes a name mismatch for agg_universe_signed_notional versus agg_universe_signed_abs_notional.",
            "Recovered current cross-symbol formulas use the later core12 builder while A7V1 registry scope is core3; formula shape is evidence, but cross-universe numeric identity is not claimed.",
            "The 5,211 rows are registry specs. Historical formatter/evaluator code proves intended semantics, not that every spec was materialized or evaluated.",
            "The 26 resolved nonmetadata labels are canonical dependency buckets, not independent axes; an independent-axis count is not identifiable statically.",
            "No numeric feature matrix was read, so empirical variance, correlation, rank equality, and portfolio equivalence remain untested.",
        ],
        "deterministic_audit_content_sha256": sha256_bytes(
            json.dumps(content_identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ),
    }


def validate_source_contracts(
    base_rows: list[dict[str, str]],
    derived_rows: list[dict[str, str]],
    lineage_rows: list[dict[str, str]],
    map_rows: list[dict[str, str]],
    current_epoch_rows: list[dict[str, str]],
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, Any]]:
    if len(base_rows) != 94 or len(derived_rows) != 5211:
        raise AssertionError(f"source row counts changed: base={len(base_rows)} derived={len(derived_rows)}")
    base_ids = [row["field_name"] for row in base_rows]
    derived_ids = [row["derived_feature_id"] for row in derived_rows]
    all_ids = base_ids + derived_ids
    if len(set(base_ids)) != 94 or len(set(derived_ids)) != 5211 or len(set(all_ids)) != 5305:
        raise AssertionError("duplicate or colliding feature ids")
    family_counts = Counter(row["production_family"] for row in derived_rows)
    expected_families = {
        "rolling_self_reproduction": 4606,
        "cross_symbol_self_reproduction_core3": 395,
        "interaction_self_reproduction": 210,
    }
    if family_counts != Counter(expected_families):
        raise AssertionError(f"production-family counts changed: {dict(family_counts)}")
    full_map_ids = [row["field_id"] for row in map_rows]
    if len(map_rows) != 5388 or len(set(full_map_ids)) != 5388:
        raise AssertionError(
            f"full map contract changed: rows={len(map_rows)} unique_fields={len(set(full_map_ids))}"
        )
    runtime_loaded_rows = [row for row in map_rows if row["runtime_loaded"].lower() == "true"]
    runtime_loaded_fields = sorted(row["field_id"] for row in runtime_loaded_rows)
    current_epoch_fields = sorted(row["field_name"] for row in current_epoch_rows)
    if len(current_epoch_rows) != 10 or len(runtime_loaded_rows) != 10:
        raise AssertionError(
            f"A7EFF2 runtime-loaded count changed: current_epoch={len(current_epoch_rows)} map={len(runtime_loaded_rows)}"
        )
    if runtime_loaded_fields != current_epoch_fields:
        raise AssertionError(
            f"A7EFF2 runtime-loaded identity mismatch: map={runtime_loaded_fields} current_epoch={current_epoch_fields}"
        )
    if any(
        row["mapping_status"] != "CURRENT_EPOCH"
        or row["consumer_lane"] != "A7EFF2_SOURCE_LAG_REWARD"
        for row in runtime_loaded_rows
    ):
        raise AssertionError("A7EFF2 runtime-loaded rows have unexpected mapping status or consumer lane")
    lineage_by_id = {row["field_id"]: row for row in lineage_rows if row["field_id"] in set(all_ids)}
    map_by_id = {row["field_id"]: row for row in map_rows if row["field_id"] in set(all_ids)}
    if set(lineage_by_id) != set(all_ids):
        raise AssertionError(f"lineage coverage mismatch: missing={sorted(set(all_ids) - set(lineage_by_id))[:10]}")
    if set(map_by_id) != set(all_ids):
        raise AssertionError(f"map coverage mismatch: missing={sorted(set(all_ids) - set(map_by_id))[:10]}")
    map_validation = {
        "full_map_row_count": len(map_rows),
        "full_map_unique_field_count": len(set(full_map_ids)),
        "runtime_loaded_field_count": len(runtime_loaded_rows),
        "runtime_loaded_fields": runtime_loaded_fields,
        "runtime_loaded_consumer_lane": "A7EFF2_SOURCE_LAG_REWARD",
        "runtime_loaded_mapping_status": "CURRENT_EPOCH",
        "static_only_field_count": sum(
            1
            for row in map_rows
            if row["runtime_loaded"].lower() == "false" and row["mapping_status"] == "STATIC_ONLY"
        ),
    }
    if map_validation["static_only_field_count"] != 5378:
        raise AssertionError(f"full map static-only count changed: {map_validation['static_only_field_count']}")
    return lineage_by_id, map_by_id, map_validation


def render_outputs() -> dict[str, bytes]:
    row_provenance = validate_audit_provenance()
    source_hashes = validate_input_hashes()
    evidence_hashes = require_source_evidence()
    base_source = read_csv(BASE_INPUT)
    derived_source = read_csv(DERIVED_INPUT)
    lineage_source = read_csv(LINEAGE_INPUT)
    map_source = read_csv(MAP_INPUT)
    current_epoch_source = read_csv(CURRENT_EPOCH_INPUT)
    lineage_by_id, map_by_id, map_validation = validate_source_contracts(
        base_source,
        derived_source,
        lineage_source,
        map_source,
        current_epoch_source,
    )
    base_audit, base_by_field = make_base_audit(base_source, lineage_by_id, map_by_id)
    derived_audit = make_derived_audit(derived_source, base_by_field, map_by_id)
    if len(base_audit) != 94 or len(derived_audit) != 5211:
        raise AssertionError("audit lost source rows")
    for output_name, rows in [(BASE_OUTPUT, base_audit), (DERIVED_OUTPUT, derived_audit)]:
        for row in rows:
            mismatches = {
                key: (row.get(key), expected)
                for key, expected in AUDIT_ROW_PROVENANCE.items()
                if row.get(key) != expected
            }
            if mismatches:
                raise AssertionError(f"row provenance mismatch in {output_name}: {mismatches}")
    base_payload = csv_bytes(base_audit)
    derived_payload = csv_bytes(derived_audit)
    summary = make_summary(
        base_audit,
        derived_audit,
        source_hashes,
        evidence_hashes,
        row_provenance,
        map_validation,
        base_payload,
        derived_payload,
    )
    summary_payload = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return {
        BASE_OUTPUT: base_payload,
        DERIVED_OUTPUT: derived_payload,
        SUMMARY_OUTPUT: summary_payload,
    }


def build(output_dir: Path) -> dict[str, str]:
    payloads = render_outputs()
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        (output_dir / name).write_bytes(payload)
    return {name: sha256_bytes(payload) for name, payload in payloads.items()}


def check(output_dir: Path) -> dict[str, str]:
    payloads = render_outputs()
    for name, expected in payloads.items():
        path = output_dir / name
        if not path.exists():
            raise AssertionError(f"missing output: {path}")
        actual = path.read_bytes()
        if actual != expected:
            raise AssertionError(
                f"non-deterministic or stale output: {name}; actual={sha256_bytes(actual)} expected={sha256_bytes(expected)}"
            )
    return {name: sha256_bytes(payload) for name, payload in payloads.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Static, evidence-independent audit of the recovered Crypto feature space")
    parser.add_argument("command", choices=["build", "check"], nargs="?", default="build")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    hashes = build(args.output_dir) if args.command == "build" else check(args.output_dir)
    print(
        json.dumps(
            {
                "command": args.command,
                "status": "PASS",
                "base_rows": 94,
                "derived_rows": 5211,
                "output_dir": str(args.output_dir),
                "output_sha256": hashes,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
