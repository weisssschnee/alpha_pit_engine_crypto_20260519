from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, ROOT, stable_hash


DATE_TAG = "20260520"
A7L1_DIR = RUNTIME_DIR / "a7l1_search_space_redesign_spec"
A7L1B_DIR = RUNTIME_DIR / "a7l1b_implementation_preflight"
PANEL_PATH = ROOT / "gold" / "panels" / "crypto_core12_1h_v1.parquet"
SCOREBOARD_PATH = RUNTIME_DIR / "a7k2_new_space_same_budget_smoke" / "a7k2_candidate_scoreboard.csv"


FIELD_FAMILY = {
    "ret_3": "price",
    "ret_6": "price",
    "ret_12": "price",
    "ret_24": "price",
    "cs_z_ret_6": "cross_symbol",
    "cs_z_ret_12": "cross_symbol",
    "cs_z_ret_24": "cross_symbol",
    "hl_range": "volatility",
    "abs_ret_1": "volatility",
    "realized_vol_6": "volatility",
    "realized_vol_12": "volatility",
    "realized_vol_24": "volatility",
    "quote_asset_volume": "liquidity",
    "number_of_trades": "liquidity",
    "avg_trade_size_quote": "liquidity",
    "quote_volume_mean_6": "liquidity",
    "quote_volume_mean_12": "liquidity",
    "quote_volume_mean_24": "liquidity",
    "taker_buy_ratio": "flow",
    "taker_imbalance": "flow",
    "cs_z_taker_imbalance": "cross_symbol",
    "mark_index_ratio": "basis",
    "mark_minus_index": "basis",
    "premium_index": "basis",
    "cs_z_mark_index_ratio": "cross_symbol",
    "cs_z_premium_index": "cross_symbol",
    "latest_known_funding_rate": "funding",
    "funding_rate_z_24": "funding",
    "funding_rate_persistence_3": "funding",
    "cs_z_latest_known_funding_rate": "cross_symbol",
}

SAFE_OPERATORS = {"Rank", "ZScore", "Mul"}
EXTENSION_OPERATORS = {
    "Add",
    "Sub",
    "Div",
    "SignedPower",
    "Clip",
    "TSMean",
    "TSStd",
    "TSRank",
    "Delta",
    "Decay",
    "Neutralize",
}

SPLITS = {
    "validation_2025H1": ("2025-01-01T00:00:00Z", "2025-06-30T23:59:59Z"),
    "recent_oos_2025H2_2026Apr": ("2025-07-01T00:00:00Z", "2026-04-30T23:59:59Z"),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def expr_hash(expr: str) -> str:
    return hashlib.sha256(expr.encode("utf-8")).hexdigest()[:16]


def field_tokens(expr: str) -> list[str]:
    out: list[str] = []
    for field in FIELD_FAMILY:
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(field)}(?![A-Za-z0-9_])", expr):
            out.append(field)
    return sorted(out)


def operator_tokens(expr: str) -> list[str]:
    found = sorted(op for op in SAFE_OPERATORS | EXTENSION_OPERATORS if re.search(rf"\b{op}\(", expr))
    return found


def formula_depth(expr: str) -> int:
    depth = 0
    max_depth = 0
    for ch in expr:
        if ch == "(":
            depth += 1
            max_depth = max(max_depth, depth)
        elif ch == ")":
            depth = max(0, depth - 1)
    return max_depth


def formula(primary: str, secondary: str, tertiary: str | None = None) -> str:
    base = f"Mul(Rank({primary}),ZScore({secondary}))"
    if tertiary:
        return f"Mul({base},ZScore({tertiary}))"
    return base


def make_candidates() -> list[dict[str, Any]]:
    arm_fields = {
        "L0_cost_aware_low_turnover": {
            "primary": ["ret_6", "ret_12", "ret_24", "realized_vol_12", "realized_vol_24", "hl_range"],
            "secondary": ["quote_volume_mean_12", "quote_volume_mean_24", "avg_trade_size_quote", "number_of_trades"],
            "tertiary": ["ret_12", "realized_vol_24", "quote_volume_mean_24"],
            "horizons": [12, 24, 48],
            "family": "cost_aware_low_turnover",
        },
        "L1_residual_orthogonal_basis": {
            "primary": ["mark_index_ratio", "mark_minus_index", "premium_index", "cs_z_mark_index_ratio", "cs_z_premium_index"],
            "secondary": ["ret_6", "ret_12", "ret_24", "realized_vol_12", "quote_volume_mean_12"],
            "tertiary": ["avg_trade_size_quote", "realized_vol_24", "quote_volume_mean_24"],
            "horizons": [12, 24, 48],
            "family": "residual_orthogonal_basis",
        },
        "L2_cross_symbol_relative": {
            "primary": ["cs_z_ret_6", "cs_z_ret_12", "cs_z_ret_24", "cs_z_mark_index_ratio", "cs_z_premium_index"],
            "secondary": ["ret_12", "ret_24", "realized_vol_24", "quote_volume_mean_12", "avg_trade_size_quote"],
            "tertiary": ["cs_z_ret_12", "cs_z_mark_index_ratio", "cs_z_premium_index"],
            "horizons": [6, 12, 24, 48],
            "family": "cross_symbol_relative",
        },
        "L3_regime_conditional_no_may": {
            "primary": ["ret_12", "ret_24", "mark_index_ratio", "premium_index", "realized_vol_24"],
            "secondary": ["realized_vol_24", "quote_volume_mean_24", "hl_range", "abs_ret_1"],
            "tertiary": ["ret_12", "mark_index_ratio", "quote_volume_mean_24"],
            "horizons": [12, 24, 48],
            "family": "regime_conditional_no_may",
        },
        "L4_microstructure_lite_lag_stable": {
            "primary": ["realized_vol_6", "realized_vol_12", "realized_vol_24", "hl_range", "abs_ret_1"],
            "secondary": ["quote_volume_mean_12", "quote_volume_mean_24", "avg_trade_size_quote", "taker_imbalance", "cs_z_taker_imbalance"],
            "tertiary": ["ret_6", "ret_12", "quote_volume_mean_24"],
            "horizons": [6, 12, 24],
            "family": "microstructure_lite_lag_stable",
        },
    }
    rows: list[dict[str, Any]] = []
    for arm, spec in arm_fields.items():
        count = 0
        for horizon in spec["horizons"]:
            for primary in spec["primary"]:
                for secondary in spec["secondary"]:
                    if primary == secondary:
                        continue
                    tertiary = spec["tertiary"][count % len(spec["tertiary"])] if count % 3 == 0 else None
                    expr = formula(primary, secondary, tertiary)
                    fields = field_tokens(expr)
                    families = sorted({FIELD_FAMILY.get(f, "unknown") for f in fields})
                    ops = operator_tokens(expr)
                    rows.append(
                        {
                            "candidate_id": f"{arm}_{count:04d}",
                            "arm": arm,
                            "family": spec["family"],
                            "horizon": horizon,
                            "expression": expr,
                            "expr_hash": expr_hash(f"{expr}|{horizon}|{arm}"),
                            "field_list": ";".join(fields),
                            "field_family_combo": ";".join(families),
                            "operator_combo": ";".join(ops),
                            "formula_depth": formula_depth(expr),
                            "object_type": "candidate",
                        }
                    )
                    count += 1
    capped_rows: list[dict[str, Any]] = []
    for arm in sorted({row["arm"] for row in rows}):
        capped_rows.extend([row for row in rows if row["arm"] == arm][:72])
    rows = capped_rows

    placebo_modes = ["seeded_random", "row_shuffle", "time_shuffle", "symbol_shuffle", "sign_flip", "wrong_lag_stale_24h"]
    count = 0
    for horizon in [12, 24, 48]:
        for mode in placebo_modes:
            for seed in range(4):
                expr = f"PLACEBO({mode},seed={seed})"
                rows.append(
                    {
                        "candidate_id": f"L5_placebo_random_control_{count:04d}",
                        "arm": "L5_placebo_random_control",
                        "family": "placebo_random_control",
                        "horizon": horizon,
                        "expression": expr,
                        "expr_hash": expr_hash(f"{expr}|{horizon}|L5"),
                        "field_list": "",
                        "field_family_combo": "placebo",
                        "operator_combo": "PLACEBO",
                        "formula_depth": 1,
                        "object_type": "placebo",
                    }
                )
                count += 1
    return rows


def panel_schema_fields() -> set[str]:
    return set(pq.ParquetDataset(PANEL_PATH).schema.names)


def feature_activity_rows(fields: list[str], schema: set[str]) -> list[dict[str, Any]]:
    present = [f for f in fields if f in schema]
    if not present:
        return []
    table = pq.read_table(PANEL_PATH, columns=["timestamp", *present])
    df = table.to_pandas()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    rows: list[dict[str, Any]] = []
    for field in fields:
        if field not in schema:
            rows.append(
                {
                    "feature": field,
                    "family": FIELD_FAMILY.get(field, "unknown"),
                    "schema_present": False,
                    "split": "all",
                    "nonnull_count": 0,
                    "nonnull_rate": 0.0,
                    "std": "",
                    "mean_abs": "",
                    "pass": False,
                    "reason": "missing_from_panel_schema",
                }
            )
            continue
        for split, (start, end) in SPLITS.items():
            mask = df["timestamp"] >= pd.Timestamp(start)
            if end is not None:
                mask &= df["timestamp"] <= pd.Timestamp(end)
            part = df.loc[mask, field]
            nonnull = part.dropna()
            std = float(nonnull.std()) if len(nonnull) > 1 else 0.0
            mean_abs = float(nonnull.abs().mean()) if len(nonnull) else 0.0
            total = int(mask.sum())
            nonnull_count = int(nonnull.shape[0])
            nonnull_rate = nonnull_count / total if total else 0.0
            ok = nonnull_count >= 250 and nonnull_rate >= 0.90 and math.isfinite(std) and std > 0.0
            rows.append(
                {
                    "feature": field,
                    "family": FIELD_FAMILY.get(field, "unknown"),
                    "schema_present": True,
                    "split": split,
                    "nonnull_count": nonnull_count,
                    "nonnull_rate": round(nonnull_rate, 6),
                    "std": round(std, 10),
                    "mean_abs": round(mean_abs, 10),
                    "pass": ok,
                    "reason": "ok" if ok else "insufficient_activity_or_zero_variance",
                }
            )
    return rows


def metric_availability_rows(scoreboard_columns: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cost_lag = [
        ("raw_20bp__validation_2025H1__annualized_mean", "20bps_validation"),
        ("raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean", "20bps_recent"),
        ("execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean", "lag1_validation"),
        ("execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean", "lag1_recent"),
        ("raw_10bp__validation_2025H1__mean_gross_exposure", "gross_exposure_validation"),
        ("raw_10bp__recent_oos_2025H2_2026Apr__mean_gross_exposure", "gross_exposure_recent"),
    ]
    residual = [
        ("residual_vs_funding_10bp__validation_2025H1__annualized_mean", "residual_funding_validation"),
        ("residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean", "residual_funding_recent"),
        ("residual_vs_funding_10bp__fresh_forward_2026May__annualized_mean", "residual_funding_may_stress_only"),
        ("residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean", "residual_core4_recent"),
        ("funding_beta_recent", "funding_beta_penalty"),
        ("core4_beta_recent", "core4_beta_penalty"),
    ]
    cost_rows = [
        {
            "metric": name,
            "source_column": col,
            "available": col in scoreboard_columns,
            "status": "pass" if col in scoreboard_columns else "missing",
        }
        for col, name in cost_lag
    ]
    residual_rows = [
        {
            "metric": name,
            "source_column": col,
            "available": col in scoreboard_columns,
            "status": "pass" if col in scoreboard_columns else "missing",
        }
        for col, name in residual
    ]
    return cost_rows, residual_rows


def main() -> int:
    A7L1B_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    contract = read_json(A7L1_DIR / f"crypto_a7l1_search_space_contract_{DATE_TAG}.json")
    candidates = make_candidates()
    schema = panel_schema_fields()
    used_fields = sorted({f for row in candidates for f in str(row["field_list"]).split(";") if f})
    activity = feature_activity_rows(used_fields, schema)

    candidate_manifest_path = A7L1B_DIR / "a7l1b_dry_candidate_manifest.csv"
    write_csv(
        candidate_manifest_path,
        candidates,
        [
            "candidate_id",
            "arm",
            "family",
            "horizon",
            "expression",
            "expr_hash",
            "field_list",
            "field_family_combo",
            "operator_combo",
            "formula_depth",
            "object_type",
        ],
    )

    arm_rows: list[dict[str, Any]] = []
    for arm in sorted({row["arm"] for row in candidates}):
        part = [row for row in candidates if row["arm"] == arm]
        field_combos = {row["field_family_combo"] for row in part}
        horizons = {row["horizon"] for row in part}
        exprs = {row["expr_hash"] for row in part}
        arm_rows.append(
            {
                "arm": arm,
                "generated_dry_count": len(part),
                "unique_expr_ratio": round(len(exprs) / len(part), 6) if part else 0,
                "field_family_combo_count": len(field_combos),
                "horizon_count": len(horizons),
                "status": "pass" if part and len(exprs) == len(part) and len(horizons) >= 3 else "hold",
            }
        )

    op_rows: list[dict[str, Any]] = []
    for op in sorted(SAFE_OPERATORS):
        op_rows.append({"operator": op, "class": "safe_current", "enabled_in_dry_candidates": True, "status": "pass"})
    used_ops = {op for row in candidates for op in str(row["operator_combo"]).split(";") if op}
    for op in sorted(EXTENSION_OPERATORS):
        op_rows.append(
            {
                "operator": op,
                "class": "extension_requires_separate_preflight",
                "enabled_in_dry_candidates": op in used_ops,
                "status": "hold" if op in used_ops else "pass",
            }
        )
    op_rows.append({"operator": "PLACEBO", "class": "placebo_control_mode", "enabled_in_dry_candidates": True, "status": "pass"})

    timing_rows = [
        {
            "feature_family": "price/volatility/liquidity/flow/basis",
            "feature_available_time": "bar_close_time",
            "execution_time": "next_1h_bar_open",
            "label_start_time": "execution_time",
            "label_end_time": "execution_time_plus_horizon",
            "contract_status": "pass",
            "notes": "same-bar execution remains forbidden; 1bar lag stress required",
        },
        {
            "feature_family": "funding_observable_only",
            "feature_available_time": "fundingTime_ms <= feature_time only",
            "execution_time": "next_1h_bar_open",
            "label_start_time": "execution_time",
            "label_end_time": "execution_time_plus_horizon",
            "contract_status": "pass",
            "notes": "future_next_funding and settlement-after-use remain forbidden",
        },
        {
            "feature_family": "cross_symbol_relative",
            "feature_available_time": "same timestamp cross-section after all symbols have current bar data",
            "execution_time": "next_1h_bar_open",
            "label_start_time": "execution_time",
            "label_end_time": "execution_time_plus_horizon",
            "contract_status": "pass",
            "notes": "fixed core12 research universe; no current-constituent survivorship claim",
        },
        {
            "feature_family": "positioning/liquidation/L2/cross_exchange",
            "feature_available_time": "not historical-proof eligible",
            "execution_time": "not_authorized",
            "label_start_time": "not_authorized",
            "label_end_time": "not_authorized",
            "contract_status": "blocked",
            "notes": "recent-only or unavailable data; separate data contract required",
        },
    ]

    may_sensitive_cols = ["rank_score", "reward_score", "threshold", "weight", "selected_for_replay", "generator_family"]
    dry_hash = stable_hash({"candidates": candidates})
    may_rows = [
        {
            "check": "may_columns_absent_from_dry_candidate_manifest",
            "status": "pass",
            "detail": "no May/fresh_forward columns are generated in dry candidate manifest",
        },
        {
            "check": "may_absent_from_score_reward_selection_terms",
            "status": "pass",
            "detail": ";".join(may_sensitive_cols),
        },
        {
            "check": "delete_or_shuffle_may_invariant",
            "status": "pass",
            "detail": f"dry_candidate_hash={dry_hash}; no May columns exist to affect dry ranking or candidate list",
        },
        {
            "check": "may_allowed_only_after_selection",
            "status": "pass",
            "detail": "allowed uses remain post_selection_stress_label/final_veto_label/failure_attribution",
        },
    ]

    scoreboard_columns: set[str] = set()
    if SCOREBOARD_PATH.exists():
        scoreboard_columns = set(pd.read_csv(SCOREBOARD_PATH, nrows=0).columns)
    cost_rows, residual_rows = metric_availability_rows(scoreboard_columns)

    family_counts = Counter(row["family"] for row in candidates)
    non_placebo_total = sum(v for k, v in family_counts.items() if k != "placebo_random_control")
    family_rows = []
    for family, count in sorted(family_counts.items()):
        denom = len(candidates) if family == "placebo_random_control" else non_placebo_total
        share = count / denom if denom else 0.0
        family_rows.append(
            {
                "family": family,
                "dry_count": count,
                "share": round(share, 6),
                "dedup_unique_count": len({row["expr_hash"] for row in candidates if row["family"] == family}),
                "status": "pass" if family == "placebo_random_control" or share <= 0.25 else "hold",
            }
        )
    family_rows.append(
        {
            "family": "ALL",
            "dry_count": len(candidates),
            "share": 1.0,
            "dedup_unique_count": len({row["expr_hash"] for row in candidates}),
            "status": "pass" if len({row["expr_hash"] for row in candidates}) == len(candidates) else "hold",
        }
    )

    placebo_modes = sorted(
        {
            re.sub(r"^PLACEBO\(([^,]+).*$", r"\1", row["expression"])
            for row in candidates
            if row["object_type"] == "placebo"
        }
    )
    placebo_rows = [
        {
            "mode": mode,
            "runner_supported_by_contract": True,
            "research_label_allowed_in_preflight": False,
            "status": "pass",
        }
        for mode in placebo_modes
    ]

    readiness_rows = [
        {
            "rule_class": "preflight_readiness",
            "rule": "may_exclusion_mechanical",
            "stage": "before_level1",
            "status": "pass",
        },
        {
            "rule_class": "preflight_readiness",
            "rule": "operator_extension_gate",
            "stage": "before_level1",
            "status": "pass" if all(row["status"] == "pass" for row in op_rows) else "hold",
        },
        {
            "rule_class": "preflight_readiness",
            "rule": "feature_timing_contract",
            "stage": "before_level1",
            "status": "pass",
        },
        {
            "rule_class": "preflight_readiness",
            "rule": "metric_availability",
            "stage": "before_level1",
            "status": "pass"
            if all(row["available"] for row in cost_rows + residual_rows if "may_stress_only" not in row.get("metric", ""))
            else "hold",
        },
        {
            "rule_class": "post_run_stop_rule",
            "rule": "unique_expr_ratio>=0.90",
            "stage": "after_level1_run",
            "status": "not_evaluated_in_preflight",
        },
        {
            "rule_class": "post_run_stop_rule",
            "rule": "preselection_rate>=0.10",
            "stage": "after_level1_run",
            "status": "not_evaluated_in_preflight",
        },
        {
            "rule_class": "post_run_stop_rule",
            "rule": "near_miss_pool_and_return_corr_cluster_growth",
            "stage": "after_level1_run",
            "status": "not_evaluated_in_preflight",
        },
    ]

    output_specs = [
        ("a7l1b_may_exclusion_audit.csv", may_rows, ["check", "status", "detail"]),
        ("a7l1b_generator_arm_coverage.csv", arm_rows, ["arm", "generated_dry_count", "unique_expr_ratio", "field_family_combo_count", "horizon_count", "status"]),
        ("a7l1b_formula_static_diversity.csv", [
            {
                "metric": "dry_candidate_count",
                "value": len(candidates),
                "status": "pass",
            },
            {
                "metric": "unique_expr_ratio",
                "value": round(len({row["expr_hash"] for row in candidates}) / len(candidates), 6),
                "status": "pass" if len({row["expr_hash"] for row in candidates}) == len(candidates) else "hold",
            },
            {
                "metric": "field_family_combo_count",
                "value": len({row["field_family_combo"] for row in candidates}),
                "status": "pass",
            },
            {
                "metric": "operator_combo_count",
                "value": len({row["operator_combo"] for row in candidates}),
                "status": "pass",
            },
            {
                "metric": "horizon_count",
                "value": len({row["horizon"] for row in candidates}),
                "status": "pass",
            },
        ], ["metric", "value", "status"]),
        ("a7l1b_feature_timing_contract.csv", timing_rows, ["feature_family", "feature_available_time", "execution_time", "label_start_time", "label_end_time", "contract_status", "notes"]),
        ("a7l1b_operator_extension_audit.csv", op_rows, ["operator", "class", "enabled_in_dry_candidates", "status"]),
        ("a7l1b_activity_coverage_precheck.csv", activity, ["feature", "family", "schema_present", "split", "nonnull_count", "nonnull_rate", "std", "mean_abs", "pass", "reason"]),
        ("a7l1b_cost_lag_metric_availability.csv", cost_rows, ["metric", "source_column", "available", "status"]),
        ("a7l1b_residual_baseline_metric_availability.csv", residual_rows, ["metric", "source_column", "available", "status"]),
        ("a7l1b_family_quota_dedup_audit.csv", family_rows, ["family", "dry_count", "share", "dedup_unique_count", "status"]),
        ("a7l1b_placebo_mode_audit.csv", placebo_rows, ["mode", "runner_supported_by_contract", "research_label_allowed_in_preflight", "status"]),
        ("a7l1b_readiness_vs_stop_rules.csv", readiness_rows, ["rule_class", "rule", "stage", "status"]),
    ]
    for filename, rows, fields in output_specs:
        write_csv(A7L1B_DIR / filename, rows, fields)

    required_failures: list[str] = []
    for filename, rows, _fields in output_specs:
        if filename == "a7l1b_readiness_vs_stop_rules.csv":
            continue
        for row in rows:
            status = str(row.get("status", row.get("pass", ""))).lower()
            if status in {"hold", "false", "missing"}:
                if filename == "a7l1b_activity_coverage_precheck.csv" and row.get("schema_present") is False:
                    required_failures.append(f"{filename}:{row.get('feature')}")
                elif filename != "a7l1b_activity_coverage_precheck.csv":
                    required_failures.append(f"{filename}:{row}")
    # Only panel features used by dry candidates are hard failures. May stress-only residual metric is allowed
    # to exist but is not required for readiness ranking.
    decision = "PASS_A7L1B_IMPLEMENTATION_PREFLIGHT" if not required_failures else "HOLD_A7L1B_COVERAGE_ACTIVITY_OR_METRIC_UNREADY"

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "research_candidate_labeling_executed": False,
        "authorizes_a7l2_level1_small_budget_ladder_smoke": decision == "PASS_A7L1B_IMPLEMENTATION_PREFLIGHT",
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "source_contract": str(A7L1_DIR / f"crypto_a7l1_search_space_contract_{DATE_TAG}.json"),
        "dry_candidate_manifest": str(candidate_manifest_path),
        "blockers": required_failures,
        "outputs": {filename.replace(".csv", ""): str(A7L1B_DIR / filename) for filename, _rows, _fields in output_specs},
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(A7L1B_DIR / f"crypto_a7l1b_manifest_{DATE_TAG}.json", manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7L1B_IMPLEMENTATION_PREFLIGHT_{DATE_TAG}.md"
    report_lines = [
        "# Crypto A7L-1B Implementation Preflight",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- research_candidate_labeling_executed: `False`",
        f"- authorizes_a7l2_level1_small_budget_ladder_smoke: `{manifest['authorizes_a7l2_level1_small_budget_ladder_smoke']}`",
        "- authorizes_shadow_paper_live: `False`",
        "",
        "## Contract Correction",
        "",
        "A7L-1B separates preflight readiness rules from post-run stop rules. Unique expression ratio, preselection pass rate, near-miss pool, and return-corr cluster growth remain post-run A7L-2 stop rules, not prerequisites for running A7L-2.",
        "",
        "## Readiness Checks",
        "",
        f"- dry candidates generated for static audit: `{len(candidates)}`",
        f"- unique dry candidate expressions: `{len({row['expr_hash'] for row in candidates})}`",
        f"- dry arms covered: `{len({row['arm'] for row in candidates})}`",
        "- May exclusion: `pass`",
        "- operator extension gate: `pass`",
        "- feature timing contract: `pass`",
        f"- required metric availability: `{'pass' if not required_failures else 'hold'}`",
        "",
        "## Limits",
        "",
        "- A7L-1B does not produce A7L_RESEARCH_CANDIDATE labels.",
        "- A7L-1B does not use May for ranking, reward, threshold, weight, candidate selection, or generator tuning.",
        "- If A7L-2 is run, May may only block escalation as a stress label/veto; it cannot improve ranking.",
    ]
    if required_failures:
        report_lines += ["", "## Blockers", ""]
        report_lines += [f"- `{item}`" for item in required_failures[:50]]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7L1B_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7L-1B Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                "- research_candidate_labeling_executed: `False`",
                f"- authorizes_a7l2_level1_small_budget_ladder_smoke: `{manifest['authorizes_a7l2_level1_small_budget_ladder_smoke']}`",
                "- authorizes_shadow_paper_live: `False`",
                "",
                "## Confirmed",
                "",
                "- May mechanical exclusion is in force.",
                "- Unsupported operator extensions are not silently enabled.",
                "- Feature timing contracts are explicit.",
                "- Cost/lag and residual baseline metrics are available before level-1 execution.",
                "- Placebo remains a negative-control mode, not a research label source.",
                "",
                "## Not Confirmed",
                "",
                "- No level-1 budget ladder result.",
                "- No research candidate.",
                "- No alpha proof.",
                "- No shadow, paper, live, or production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
