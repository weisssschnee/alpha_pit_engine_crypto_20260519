from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

CRYPTO_ROOT = Path(__file__).resolve().parents[1]
if str(CRYPTO_ROOT) not in sys.path:
    sys.path.insert(0, str(CRYPTO_ROOT))

from alphafactory_crypto.engines.feature_algebra import CryptoFeatureAlgebra
from alphafactory_crypto.engines.formula_gen_v2_adapter import CryptoFormulaGenV2Adapter


DATE_TAG = "20260527"
REPORT_DIR = CRYPTO_ROOT / "reports"
RUNTIME_DIR = CRYPTO_ROOT / "runtime" / "a7ar2_feature_algebra_parity_smoke"
PANEL_ROOT = Path(r"G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v1_20260525")
A7AR1_CANDIDATES = CRYPTO_ROOT / "runtime" / "a7ar1_formula_engine_adapter_smoke" / "a7ar1_generated_candidates.csv"
SPLIT_COVERAGE = CRYPTO_ROOT / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_split_coverage_by_symbol.csv"
FIELD_TIMING = CRYPTO_ROOT / "runtime" / "a7al0_top498_alpha_search_contract" / "a7al_field_timing_contract.csv"
CONFIG_PATH = CRYPTO_ROOT / "config" / "crypto_formula_gen_v2_motif_pack_v1.json"


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv_dict(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def select_candidates(rows: list[dict[str, str]], per_family: int = 16) -> list[dict[str, str]]:
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_family[row["family"]].append(row)
    selected: list[dict[str, str]] = []
    for family in sorted(by_family):
        selected.extend(by_family[family][:per_family])
    return selected


def strict_symbols(limit: int = 32) -> list[str]:
    rows = read_csv_dict(SPLIT_COVERAGE)
    symbols: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if row.get("split") != "train":
            continue
        if row.get("search_eligibility") != "strict_full_history":
            continue
        symbol = row.get("symbol", "")
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        symbols.append(symbol)
        if len(symbols) >= limit:
            break
    return symbols


def fields_from_candidates(candidates: list[dict[str, str]]) -> set[str]:
    fields: set[str] = set()
    for row in candidates:
        fields.update(part for part in str(row.get("fields", "")).split("|") if part)
    return fields


def load_panel(symbols: list[str], columns: set[str]) -> pd.DataFrame:
    base_columns = {"symbol", "timestamp", "feature_available_time", "execution_time"}
    selected_columns = sorted(base_columns | columns)
    frames: list[pd.DataFrame] = []
    for symbol in symbols:
        path = PANEL_ROOT / f"symbol={symbol}" / "part.parquet"
        if not path.exists():
            continue
        frame = pd.read_parquet(path, columns=[col for col in selected_columns if col != "symbol"])
        frame["symbol"] = symbol
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=False)
        frame = frame[(frame["timestamp"] >= "2024-01-01") & (frame["timestamp"] <= "2025-06-30 23:00:00")]
        frames.append(frame[selected_columns])
    if not frames:
        raise RuntimeError("no panel frames loaded")
    output = pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"]).reset_index(drop=True)
    return output


def timing_audit(frame: pd.DataFrame) -> list[dict[str, Any]]:
    timestamps = pd.to_datetime(frame["timestamp"])
    feature_available = pd.to_datetime(frame["feature_available_time"])
    execution = pd.to_datetime(frame["execution_time"])
    expected_plus1 = timestamps + pd.Timedelta(hours=1)
    return [
        {
            "check": "feature_available_time_at_least_timestamp_plus_1h",
            "violations": int((feature_available < expected_plus1).sum()),
            "rows": int(len(frame)),
        },
        {
            "check": "execution_time_at_least_timestamp_plus_1h",
            "violations": int((execution < expected_plus1).sum()),
            "rows": int(len(frame)),
        },
        {
            "check": "execution_time_at_least_feature_available_time",
            "violations": int((execution < feature_available).sum()),
            "rows": int(len(frame)),
        },
    ]


def field_timing_subset(fields: set[str]) -> list[dict[str, Any]]:
    timing_rows = read_csv_dict(FIELD_TIMING)
    by_field = {row["field_name"]: row for row in timing_rows}
    rows: list[dict[str, Any]] = []
    for field in sorted(fields):
        row = by_field.get(field)
        rows.append(
            {
                "field_name": field,
                "in_contract": row is not None,
                "feature_available_time_primary": row.get("feature_available_time_primary", "") if row else "",
                "feature_available_time_conservative": row.get("feature_available_time_conservative", "") if row else "",
                "same_bar_execution_allowed": row.get("same_bar_execution_allowed", "") if row else "",
                "two_bar_lag_stress_required": row.get("two_bar_lag_stress_required", "") if row else "",
            }
        )
    return rows


def shifted_activity(values: pd.Series, frame: pd.DataFrame, shift_hours: int) -> dict[str, Any]:
    shifted = values.groupby(frame["symbol"], sort=False).shift(shift_hours)
    non_null = shifted.notna()
    active = non_null & (shifted.abs() > 1e-12)
    return {
        "non_null_ratio": round(float(non_null.mean()), 6),
        "active_ratio": round(float(active.mean()), 6),
        "inf_rows": int(np.isinf(shifted.to_numpy(dtype=float, na_value=np.nan)).sum()),
    }


def evaluate_candidates(candidates: list[dict[str, str]], frame: pd.DataFrame, allowed_fields: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    evaluator = CryptoFeatureAlgebra(frame, allowed_fields)
    metric_rows: list[dict[str, Any]] = []
    control_rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(20260527)
    for row in candidates:
        candidate_id = row["candidate_id"]
        expression = row["expression"]
        try:
            result = evaluator.evaluate(expression)
            plus1 = shifted_activity(result.values, frame, 0)
            plus2 = shifted_activity(result.values, frame, 1)
            stale24 = shifted_activity(result.values, frame, 24)
            future1 = shifted_activity(result.values, frame, -1)
            random_values = pd.Series(rng.normal(size=len(frame)), index=frame.index)
            random_diag = evaluator.diagnostics(random_values)
            metric_rows.append(
                {
                    "candidate_id": candidate_id,
                    "family": row["family"],
                    "expression": expression,
                    "eval_status": "pass",
                    "rows": result.diagnostics["rows"],
                    "non_null_ratio_0bar": result.diagnostics["non_null_ratio"],
                    "active_ratio_0bar": result.diagnostics["active_ratio"],
                    "inf_rows_0bar": result.diagnostics["inf_rows"],
                    "std_0bar": result.diagnostics["std"],
                    "active_ratio_plus1h": plus1["active_ratio"],
                    "active_ratio_plus2h": plus2["active_ratio"],
                    "inf_rows_plus2h": plus2["inf_rows"],
                    "error": "",
                }
            )
            control_rows.extend(
                [
                    {
                        "candidate_id": candidate_id,
                        "control": "wrong_lag_future_1h",
                        "eval_status": "pass",
                        "active_ratio": future1["active_ratio"],
                        "inf_rows": future1["inf_rows"],
                    },
                    {
                        "candidate_id": candidate_id,
                        "control": "wrong_lag_stale_24h",
                        "eval_status": "pass",
                        "active_ratio": stale24["active_ratio"],
                        "inf_rows": stale24["inf_rows"],
                    },
                    {
                        "candidate_id": candidate_id,
                        "control": "random_field",
                        "eval_status": "pass",
                        "active_ratio": random_diag["active_ratio"],
                        "inf_rows": random_diag["inf_rows"],
                    },
                ]
            )
        except Exception as exc:
            metric_rows.append(
                {
                    "candidate_id": candidate_id,
                    "family": row["family"],
                    "expression": expression,
                    "eval_status": "fail",
                    "rows": len(frame),
                    "non_null_ratio_0bar": 0,
                    "active_ratio_0bar": 0,
                    "inf_rows_0bar": 0,
                    "std_0bar": "",
                    "active_ratio_plus1h": 0,
                    "active_ratio_plus2h": 0,
                    "inf_rows_plus2h": 0,
                    "error": str(exc)[:400],
                }
            )
    return metric_rows, control_rows


def aggregate_by_family(metric_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in metric_rows:
        by_family[row["family"]].append(row)
    output: list[dict[str, Any]] = []
    for family, rows in sorted(by_family.items()):
        active_plus2 = [float(row["active_ratio_plus2h"]) for row in rows if row["eval_status"] == "pass"]
        output.append(
            {
                "family": family,
                "candidates": len(rows),
                "eval_failures": sum(1 for row in rows if row["eval_status"] != "pass"),
                "median_active_ratio_plus2h": round(float(np.median(active_plus2)), 6) if active_plus2 else 0.0,
                "min_active_ratio_plus2h": round(float(np.min(active_plus2)), 6) if active_plus2 else 0.0,
            }
        )
    return output


def make_report(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Crypto A7AR-2 Feature Algebra Parity Smoke",
            "",
            "## Decision",
            "",
            summary["decision"],
            "",
            "## Scope",
            "",
            "- Evaluates A7AR-1 generated formulas on a strict_full_history top498 sample.",
            "- Tests crypto-safe operator execution for Mean, Delta, ZScore, Rank, Mul, Sub, Neg.",
            "- Audits +1h/+2h timing feasibility, NaN/inf, active signal coverage, and control-evaluation feasibility.",
            "- Does not run alpha replay, ranking, formula search, or candidate promotion.",
            "",
            "## Results",
            "",
            f"- symbols: {summary['symbols']}",
            f"- panel_rows: {summary['panel_rows']}",
            f"- evaluated_candidates: {summary['evaluated_candidates']}",
            f"- eval_failures: {summary['eval_failures']}",
            f"- plus2_active_candidates: {summary['plus2_active_candidates']}",
            f"- inf_candidate_count: {summary['inf_candidate_count']}",
            f"- timing_violations: {summary['timing_violations']}",
            f"- field_contract_missing: {summary['field_contract_missing']}",
            f"- control_eval_failures: {summary['control_eval_failures']}",
            "",
            "## Authorization",
            "",
            "- A7AR-3 fresh memory/dedup smoke is authorized if this decision is PASS.",
            "- A7AL-2 formula search remains not authorized.",
        ]
    )


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    candidates = select_candidates(read_csv_dict(A7AR1_CANDIDATES), per_family=16)
    fields = fields_from_candidates(candidates)
    adapter = CryptoFormulaGenV2Adapter.from_path(CONFIG_PATH, seed="a7ar2_allowed_fields")
    unknown_fields = sorted(fields - adapter.allowed_fields)
    symbols = strict_symbols(limit=32)
    frame = load_panel(symbols, fields)

    timing_rows = timing_audit(frame)
    field_contract_rows = field_timing_subset(fields)
    metric_rows, control_rows = evaluate_candidates(candidates, frame, adapter.allowed_fields)
    family_rows = aggregate_by_family(metric_rows)

    eval_failures = sum(1 for row in metric_rows if row["eval_status"] != "pass")
    inf_candidate_count = sum(1 for row in metric_rows if int(row["inf_rows_0bar"] or 0) > 0 or int(row["inf_rows_plus2h"] or 0) > 0)
    plus2_active_candidates = sum(1 for row in metric_rows if row["eval_status"] == "pass" and float(row["active_ratio_plus2h"]) >= 0.25)
    timing_violations = sum(int(row["violations"]) for row in timing_rows)
    field_contract_missing = sum(1 for row in field_contract_rows if not row["in_contract"])
    control_eval_failures = sum(1 for row in control_rows if row["eval_status"] != "pass")

    pass_gate = (
        not unknown_fields
        and eval_failures == 0
        and inf_candidate_count == 0
        and timing_violations == 0
        and field_contract_missing == 0
        and control_eval_failures == 0
        and plus2_active_candidates >= int(0.85 * len(metric_rows))
    )
    decision = "PASS_A7AR2_FEATURE_ALGEBRA_PARITY_SMOKE" if pass_gate else "HOLD_A7AR2_FEATURE_ALGEBRA_PARITY_SMOKE"
    summary = {
        "decision": decision,
        "symbols": len(symbols),
        "panel_rows": int(len(frame)),
        "evaluated_candidates": len(metric_rows),
        "eval_failures": eval_failures,
        "plus2_active_candidates": plus2_active_candidates,
        "inf_candidate_count": inf_candidate_count,
        "timing_violations": timing_violations,
        "field_contract_missing": field_contract_missing,
        "unknown_fields": unknown_fields,
        "control_eval_failures": control_eval_failures,
        "a7ar3_authorized": pass_gate,
        "a7al2_formula_search_authorized": False,
        "alpha_proof_authorized": False,
        "shadow_paper_live_authorized": False,
    }

    write_csv(
        RUNTIME_DIR / "a7ar2_candidate_eval_metrics.csv",
        metric_rows,
        [
            "candidate_id",
            "family",
            "expression",
            "eval_status",
            "rows",
            "non_null_ratio_0bar",
            "active_ratio_0bar",
            "inf_rows_0bar",
            "std_0bar",
            "active_ratio_plus1h",
            "active_ratio_plus2h",
            "inf_rows_plus2h",
            "error",
        ],
    )
    write_csv(
        RUNTIME_DIR / "a7ar2_control_eval_audit.csv",
        control_rows,
        ["candidate_id", "control", "eval_status", "active_ratio", "inf_rows"],
    )
    write_csv(
        RUNTIME_DIR / "a7ar2_timing_audit.csv",
        timing_rows,
        ["check", "violations", "rows"],
    )
    write_csv(
        RUNTIME_DIR / "a7ar2_field_contract_audit.csv",
        field_contract_rows,
        [
            "field_name",
            "in_contract",
            "feature_available_time_primary",
            "feature_available_time_conservative",
            "same_bar_execution_allowed",
            "two_bar_lag_stress_required",
        ],
    )
    write_csv(
        RUNTIME_DIR / "a7ar2_family_summary.csv",
        family_rows,
        ["family", "candidates", "eval_failures", "median_active_ratio_plus2h", "min_active_ratio_plus2h"],
    )
    write_json(RUNTIME_DIR / "a7ar2_decision_record.json", summary)
    write_json(
        RUNTIME_DIR / "a7ar2_manifest.json",
        {
            "object_id": "crypto_a7ar2_feature_algebra_parity_smoke",
            "decision": decision,
            "panel_root": str(PANEL_ROOT),
            "candidate_source": str(A7AR1_CANDIDATES),
            "outputs": {
                "candidate_eval_metrics": str(RUNTIME_DIR / "a7ar2_candidate_eval_metrics.csv"),
                "control_eval_audit": str(RUNTIME_DIR / "a7ar2_control_eval_audit.csv"),
                "timing_audit": str(RUNTIME_DIR / "a7ar2_timing_audit.csv"),
                "field_contract_audit": str(RUNTIME_DIR / "a7ar2_field_contract_audit.csv"),
            },
        },
    )
    (REPORT_DIR / f"CRYPTO_A7AR2_FEATURE_ALGEBRA_PARITY_SMOKE_{DATE_TAG}.md").write_text(make_report(summary), encoding="utf-8")
    print(decision)


if __name__ == "__main__":
    main()
