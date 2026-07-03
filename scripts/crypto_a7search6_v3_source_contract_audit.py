from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7reward1_portfolio_reward_model import expression_fields  # noqa: E402


DATE = "20260703"
STAGE = "A7SEARCH6-V3-SOURCE-CONTRACT"
DEFAULT_INPUT = REPO / "runtime" / "a7search6_validation_pack_r2_20260702" / "a7search6_validation_accepted_summary.csv"
DEFAULT_VALIDATION_RUNTIME = REPO / "runtime" / "a7search6_validation_pack_r2_20260702"
DEFAULT_REWARD_AGG = REPO / "runtime" / "a7search6_validation_pack_reward_r2_aggregate_20260702"
DEFAULT_RUNTIME = REPO / "runtime" / "a7search6_v3_source_contract_audit_20260703"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SEARCH6_V3_SOURCE_CONTRACT_AUDIT_20260703.md"
DEFAULT_DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))


FIELD_RULES: list[tuple[re.Pattern[str], dict[str, str]]] = [
    (
        re.compile(r"funding_rate_delta_state_24h|funding_rate_state_last_ffill_8h|funding_rate_update_age_hours"),
        {
            "field_family": "event_dense_funding",
            "source_family": "binance_funding_rest_derived_state",
            "availability_policy": "event timestamp plus forward-fill age required; signal must use only already published funding events",
            "contract_status": "HOLD_SOURCE_PROOF",
            "blocking_issue": "derived funding state needs event-time/ffill-age proof in reward loader",
            "allowed_for_controlled_search": "true",
        },
    ),
    (
        re.compile(r".*funding.*"),
        {
            "field_family": "funding",
            "source_family": "binance_funding_rest",
            "availability_policy": "funding event timestamp required; no next funding leakage",
            "contract_status": "HOLD_SOURCE_PROOF",
            "blocking_issue": "REST funding source has no exchange checksum and publication-time proof is not wired into reward",
            "allowed_for_controlled_search": "true",
        },
    ),
    (
        re.compile(r".*open_interest.*"),
        {
            "field_family": "open_interest",
            "source_family": "binance_metrics_open_interest",
            "availability_policy": "metrics snapshot timestamp must be <= signal timestamp; no same-bar backfill",
            "contract_status": "HOLD_SOURCE_PROOF",
            "blocking_issue": "metrics snapshot/native interval timestamp proof is not attached to reward rows",
            "allowed_for_controlled_search": "true",
        },
    ),
    (
        re.compile(r".*(long_short|position).*"),
        {
            "field_family": "positioning",
            "source_family": "binance_metrics_positioning_ratio",
            "availability_policy": "account/top position ratio publication lag must be explicit",
            "contract_status": "HOLD_SOURCE_PROOF",
            "blocking_issue": "positioning ratio publication lag proof is missing",
            "allowed_for_controlled_search": "true",
        },
    ),
    (
        re.compile(r".*taker.*"),
        {
            "field_family": "taker_flow",
            "source_family": "bar_close_trade_flow",
            "availability_policy": "available after bar close; execute at timestamp + 1h or later",
            "contract_status": "PASS_CONTROLLED_CONTRACT",
            "blocking_issue": "",
            "allowed_for_controlled_search": "true",
        },
    ),
    (
        re.compile(r".*(basis|premium|mark|index).*"),
        {
            "field_family": "basis_premium",
            "source_family": "binance_vision_mark_index_premium",
            "availability_policy": "bar-close mark/index/premium available after bucket close; execute at timestamp + 1h or later",
            "contract_status": "PASS_CONTROLLED_CONTRACT",
            "blocking_issue": "final proof still requires official CHECKSUM audit for Vision fast path",
            "allowed_for_controlled_search": "true",
        },
    ),
    (
        re.compile(r".*(volume|liquidity|quote_volume).*"),
        {
            "field_family": "liquidity",
            "source_family": "binance_vision_trade_bar",
            "availability_policy": "bar-close volume available after bucket close; execute at timestamp + 1h or later",
            "contract_status": "PASS_CONTROLLED_CONTRACT",
            "blocking_issue": "final proof still requires official CHECKSUM audit for Vision fast path",
            "allowed_for_controlled_search": "true",
        },
    ),
    (
        re.compile(r".*(regime|state|stress_proxy).*"),
        {
            "field_family": "regime_state",
            "source_family": "computed_state",
            "availability_policy": "state thresholds must be rolling-past or train-only frozen",
            "contract_status": "HOLD_SOURCE_PROOF",
            "blocking_issue": "state threshold lineage is not attached to accepted reward rows",
            "allowed_for_controlled_search": "true",
        },
    ),
]


def dataset_specs(data_root: Path) -> list[dict[str, Any]]:
    return [
        {
            "name": "binance_universe498_recent_patch_1h_v1_20260612",
            "report": data_root / "reports" / "binance_universe498_recent_patch_1h_v1_20260612.json",
            "field_contract": data_root
            / "gold"
            / "metadata"
            / "binance_universe498_recent_patch_1h_v1_20260612_field_contract.json",
            "manifest": data_root / "manifests" / "binance_universe498_recent_patch_1h_v1_20260612_manifest.csv",
            "coverage": data_root / "manifests" / "binance_universe498_recent_patch_1h_v1_20260612_coverage.csv",
            "role": "June/late-May blind holdout data source",
        },
        {
            "name": "binance_universe_pre2024_complete_replay_1h_v1_20260612",
            "report": data_root / "reports" / "binance_universe_pre2024_complete_replay_1h_v1_20260612.json",
            "field_contract": data_root
            / "gold"
            / "metadata"
            / "binance_universe_pre2024_complete_replay_1h_v1_20260612_field_contract.json",
            "manifest": data_root / "manifests" / "binance_universe_pre2024_complete_replay_1h_v1_20260612_manifest.csv",
            "coverage": data_root / "manifests" / "binance_universe_pre2024_complete_replay_1h_v1_20260612_coverage.csv",
            "role": "pre-2024 regime enrichment source",
        },
    ]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size <= 2:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 40) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def field_contract(field: str) -> dict[str, str]:
    for pattern, payload in FIELD_RULES:
        if pattern.fullmatch(field) or pattern.match(field):
            out = dict(payload)
            out["field"] = field
            return out
    return {
        "field": field,
        "field_family": "generic_numeric",
        "source_family": "unknown_or_generic",
        "availability_policy": "requires explicit source contract lookup",
        "contract_status": "HOLD_UNKNOWN_FIELD_CONTRACT",
        "blocking_issue": "field is not mapped in A7SEARCH6-V3 source contract table",
        "allowed_for_controlled_search": "false",
    }


def load_accepted(path: Path) -> pd.DataFrame:
    accepted = read_csv_or_empty(path)
    if accepted.empty:
        raise RuntimeError(f"missing accepted validation summary: {path}")
    for col in [
        "train_sortino",
        "validation_sortino",
        "test_sortino",
        "recent_sortino",
        "min_oos_floor_sortino",
        "stress_floor_sortino",
        "recent_shuffle_control_ratio",
    ]:
        if col in accepted.columns:
            accepted[col] = pd.to_numeric(accepted[col], errors="coerce")
    return accepted


def build_field_maps(accepted: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    formula_rows: list[dict[str, Any]] = []
    field_rows: list[dict[str, Any]] = []
    contract_rows: list[dict[str, Any]] = []

    for rec in accepted.to_dict("records"):
        formula = str(rec.get("formula", ""))
        fields = expression_fields(formula)
        formula_key = f"{rec.get('source_blueprint_id')}|{rec.get('blueprint_id')}|{rec.get('horizon_h')}"
        field_statuses: list[str] = []
        field_issues: list[str] = []
        for field in fields:
            contract = field_contract(field)
            field_statuses.append(contract["contract_status"])
            if contract["blocking_issue"]:
                field_issues.append(f"{field}:{contract['blocking_issue']}")
            field_rows.append(
                {
                    "formula_key": formula_key,
                    "source_blueprint_id": rec.get("source_blueprint_id"),
                    "blueprint_id": rec.get("blueprint_id"),
                    "horizon_h": rec.get("horizon_h"),
                    "field": field,
                    **contract,
                }
            )
            contract_rows.append(contract)
        unique_status = sorted(set(field_statuses))
        hard_blocks = [s for s in unique_status if s.startswith("HOLD") or s.startswith("FAIL")]
        if hard_blocks:
            formula_gate = "HOLD_SOURCE_CONTRACT_PROOF_REQUIRED"
        else:
            formula_gate = "PASS_CONTROLLED_SEARCH_SOURCE_GATE"
        formula_rows.append(
            {
                "formula_key": formula_key,
                "source_blueprint_id": rec.get("source_blueprint_id"),
                "blueprint_id": rec.get("blueprint_id"),
                "horizon_h": rec.get("horizon_h"),
                "formula": formula,
                "fields": "|".join(fields),
                "field_contract_statuses": "|".join(unique_status),
                "formula_source_gate": formula_gate,
                "blocking_issues": ";".join(field_issues),
                "train_sortino": rec.get("train_sortino"),
                "validation_sortino": rec.get("validation_sortino"),
                "test_sortino": rec.get("test_sortino"),
                "recent_sortino": rec.get("recent_sortino"),
                "min_oos_floor_sortino": rec.get("min_oos_floor_sortino"),
                "stress_floor_sortino": rec.get("stress_floor_sortino"),
                "recent_shuffle_control_ratio": rec.get("recent_shuffle_control_ratio"),
            }
        )

    field_map = pd.DataFrame(field_rows).drop_duplicates()
    formula_gate = pd.DataFrame(formula_rows).sort_values(
        ["formula_source_gate", "min_oos_floor_sortino", "recent_sortino"],
        ascending=[True, False, False],
    )
    contract_gate = pd.DataFrame(contract_rows).drop_duplicates("field").sort_values(["contract_status", "field"])
    return field_map, contract_gate, formula_gate


def dataset_inventory(data_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    june_rows: list[dict[str, Any]] = []
    for spec in dataset_specs(data_root):
        report = read_json_or_empty(spec["report"])
        contract = read_json_or_empty(spec["field_contract"])
        coverage = read_csv_or_empty(spec["coverage"])
        manifest = read_csv_or_empty(spec["manifest"])
        row = {
            "dataset": spec["name"],
            "role": spec["role"],
            "report_exists": spec["report"].exists(),
            "field_contract_exists": spec["field_contract"].exists(),
            "manifest_exists": spec["manifest"].exists(),
            "coverage_exists": spec["coverage"].exists(),
            "decision": report.get("decision", ""),
            "timestamp_min": report.get("timestamp_min") or report.get("build", {}).get("min_timestamp"),
            "timestamp_max": report.get("timestamp_max") or report.get("build", {}).get("max_timestamp"),
            "rows": report.get("rows") or report.get("build", {}).get("rows"),
            "symbols": report.get("symbols") or report.get("build", {}).get("symbols"),
            "mean_coverage": report.get("mean_coverage"),
            "mean_metrics_coverage": report.get("mean_metrics_coverage") or report.get("build", {}).get("mean_metrics_coverage"),
            "mean_funding_coverage": report.get("mean_funding_coverage") or report.get("build", {}).get("mean_funding_coverage"),
            "timestamp_semantics": json.dumps(contract.get("timestamp_semantics", contract.get("timestamp", "")), ensure_ascii=False),
            "feature_available_time": contract.get("timestamp_semantics", {}).get("feature_available_time")
            or contract.get("feature_available_time", ""),
            "proof_boundary": contract.get("proof_boundary", ""),
        }
        rows.append(row)
        if spec["name"] == "binance_universe498_recent_patch_1h_v1_20260612":
            june_mask = pd.Series(dtype=bool)
            if not manifest.empty and "timestamp_min" in manifest.columns and "timestamp_max" in manifest.columns:
                mn = pd.to_datetime(manifest["timestamp_min"], errors="coerce")
                mx = pd.to_datetime(manifest["timestamp_max"], errors="coerce")
                june_mask = mx.ge(pd.Timestamp("2026-06-01 00:00:00")) & mn.le(pd.Timestamp("2026-06-11 23:00:00"))
            june_coverage = coverage.copy()
            if not june_coverage.empty:
                for col in ["coverage", "mark_coverage", "metrics_coverage", "funding_coverage"]:
                    if col in june_coverage.columns:
                        june_coverage[col] = pd.to_numeric(june_coverage[col], errors="coerce")
            june_rows.append(
                {
                    "split_name": "blind_june2026_20260601_20260611",
                    "available": bool(report and report.get("timestamp_max", "") >= "2026-06-11"),
                    "dataset": spec["name"],
                    "start": "2026-06-01 00:00:00",
                    "end": "2026-06-11 23:00:00",
                    "available_symbols": int(june_mask.sum()) if not june_mask.empty else int(report.get("symbols", 0) or 0),
                    "dataset_symbols": int(report.get("symbols", 0) or 0),
                    "mean_coverage": float(june_coverage["coverage"].mean()) if "coverage" in june_coverage else None,
                    "mean_metrics_coverage": float(june_coverage["metrics_coverage"].mean()) if "metrics_coverage" in june_coverage else None,
                    "mean_funding_coverage": float(june_coverage["funding_coverage"].mean()) if "funding_coverage" in june_coverage else None,
                    "reward_split_wired": False,
                    "blocking_issue": "reward split function does not define June blind split and numeric loader does not merge recent patch panel",
                    "recommended_action": "add explicit blind_june2026 split after May stress; run accepted formulas only after source-contract gate",
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(june_rows)


def summarize(runtime: Path, report: Path, accepted_path: Path, data_root: Path) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    accepted = load_accepted(accepted_path)
    field_map, contract_gate, formula_gate = build_field_maps(accepted)
    dataset_df, june_df = dataset_inventory(data_root)

    field_map.to_csv(runtime / "a7search6_v3_formula_field_map.csv", index=False)
    contract_gate.to_csv(runtime / "a7search6_v3_field_source_contract_gate.csv", index=False)
    formula_gate.to_csv(runtime / "a7search6_v3_formula_source_gate.csv", index=False)
    dataset_df.to_csv(runtime / "a7search6_v3_dataset_contract_inventory.csv", index=False)
    june_df.to_csv(runtime / "a7search6_v3_june_holdout_wiring_gap.csv", index=False)

    family_counts = (
        field_map.groupby(["field_family", "contract_status"], dropna=False)
        .agg(fields=("field", "nunique"), formulas=("formula_key", "nunique"))
        .reset_index()
        .sort_values(["formulas", "fields"], ascending=False)
    )
    family_counts.to_csv(runtime / "a7search6_v3_field_family_gate_summary.csv", index=False)
    formula_gate_counts = Counter(formula_gate["formula_source_gate"].astype(str))
    field_status_counts = Counter(contract_gate["contract_status"].astype(str))
    hard_hold_formula_count = int(formula_gate["formula_source_gate"].astype(str).str.startswith("HOLD").sum())
    pass_controlled_formula_count = int(formula_gate["formula_source_gate"].eq("PASS_CONTROLLED_SEARCH_SOURCE_GATE").sum())
    june_wired = bool(june_df["reward_split_wired"].all()) if not june_df.empty else False

    if hard_hold_formula_count:
        decision = "HOLD_A7SEARCH6V3_SOURCE_CONTRACT_PROOF_REQUIRED"
    elif not june_wired:
        decision = "HOLD_A7SEARCH6V3_JUNE_HOLDOUT_NOT_WIRED"
    else:
        decision = "PASS_A7SEARCH6V3_SOURCE_AND_JUNE_GATE_READY"

    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "accepted_input": str(accepted_path),
        "runtime": str(runtime),
        "report": str(report),
        "accepted_rows": int(accepted.shape[0]),
        "accepted_unique_blueprints": int(accepted["source_blueprint_id"].nunique()) if "source_blueprint_id" in accepted else 0,
        "formula_rows": int(formula_gate.shape[0]),
        "field_rows": int(field_map.shape[0]),
        "unique_fields": int(field_map["field"].nunique()) if not field_map.empty else 0,
        "formula_source_gate_counts": dict(formula_gate_counts),
        "field_contract_status_counts": dict(field_status_counts),
        "pass_controlled_formula_count": pass_controlled_formula_count,
        "hard_hold_formula_count": hard_hold_formula_count,
        "june_holdout_available": bool(june_df["available"].all()) if not june_df.empty else False,
        "june_holdout_reward_split_wired": june_wired,
        "authorizes_next_search": False,
        "authorizes_source_contract_repair": True,
        "authorizes_june_holdout_adapter": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "outputs": {
            "formula_field_map": str(runtime / "a7search6_v3_formula_field_map.csv"),
            "field_source_contract_gate": str(runtime / "a7search6_v3_field_source_contract_gate.csv"),
            "formula_source_gate": str(runtime / "a7search6_v3_formula_source_gate.csv"),
            "dataset_contract_inventory": str(runtime / "a7search6_v3_dataset_contract_inventory.csv"),
            "june_holdout_wiring_gap": str(runtime / "a7search6_v3_june_holdout_wiring_gap.csv"),
            "field_family_gate_summary": str(runtime / "a7search6_v3_field_family_gate_summary.csv"),
            "manifest": str(runtime / "a7search6_v3_manifest.json"),
        },
    }
    write_json(runtime / "a7search6_v3_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SEARCH6 V3 Source Contract Audit",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This is a source-timing and blind-holdout gate for A7SEARCH6 accepted candidates. It does not validate alpha, and it does not authorize shadow, paper, live, or production portfolio construction.",
        "",
        "## Counts",
        "",
        f"- accepted_rows: `{manifest['accepted_rows']}`",
        f"- accepted_unique_blueprints: `{manifest['accepted_unique_blueprints']}`",
        f"- formula_rows: `{manifest['formula_rows']}`",
        f"- unique_fields: `{manifest['unique_fields']}`",
        f"- pass_controlled_formula_count: `{pass_controlled_formula_count}`",
        f"- hard_hold_formula_count: `{hard_hold_formula_count}`",
        f"- june_holdout_available: `{manifest['june_holdout_available']}`",
        f"- june_holdout_reward_split_wired: `{manifest['june_holdout_reward_split_wired']}`",
        "",
        "## Field Family Gate Summary",
        "",
        md_table(family_counts, max_rows=40),
        "",
        "## Dataset Contract Inventory",
        "",
        md_table(dataset_df, max_rows=20),
        "",
        "## June Holdout Wiring Gap",
        "",
        md_table(june_df, max_rows=20),
        "",
        "## Formula Source Gate",
        "",
        md_table(
            formula_gate[
                [
                    "source_blueprint_id",
                    "horizon_h",
                    "formula_source_gate",
                    "field_contract_statuses",
                    "min_oos_floor_sortino",
                    "recent_sortino",
                    "formula",
                ]
            ],
            max_rows=40,
        ),
        "",
        "## Required Next Actions",
        "",
        "1. Attach field-native source timestamps for Binance metrics OI, global/top long-short ratios, and funding-derived state before treating current A7SEARCH6 winners as proof candidates.",
        "2. Wire `blind_june2026_20260601_20260611` into the reward split/loader as an evaluation-only split; do not use it for orientation or search selection.",
        "3. Re-run accepted A7SEARCH6 formulas only after the above gate; broad search remains blocked by this audit.",
        "",
        "## Outputs",
        "",
    ]
    for key, value in manifest["outputs"].items():
        lines.append(f"- `{key}`: `{value}`")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    args = parser.parse_args()
    manifest = summarize(args.runtime, args.report, args.input, args.data_root)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
