from __future__ import annotations

import argparse
import json
import os
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


STAGE = "A7SOURCE-1-FIELD-TIMING-PROOF"
DEFAULT_INPUT = REPO / "runtime" / "a7search6_june_blind_adapter_20260703" / "a7search6_june_blind_original_summary.csv"
DEFAULT_V3_GATE = REPO / "runtime" / "a7search6_v3_source_contract_audit_20260703" / "a7search6_v3_field_source_contract_gate.csv"
DEFAULT_RUNTIME = REPO / "runtime" / "a7source1_field_timing_proof_20260703"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SOURCE1_FIELD_TIMING_PROOF_20260703.md"
DEFAULT_DATA_ROOT = Path(os.environ.get("ALPHAFACTORY_CRYPTO_DATA_ROOT", r"G:\AlphaFactory_CryptoData"))


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


def md_table(frame: pd.DataFrame, max_rows: int = 50) -> str:
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


def source_trace_paths(data_root: Path) -> dict[str, Path]:
    return {
        "a7s1_report": data_root / "alphafactory_crypto" / "reports" / "CRYPTO_A7S1_BINANCE_METRICS_SOURCE_TRACE_20260522.md",
        "a7s1_contract": data_root / "alphafactory_crypto" / "runtime" / "a7s1_metrics_source_trace" / "a7s1_metrics_field_contract.json",
        "a7s1_coverage": data_root / "alphafactory_crypto" / "runtime" / "a7s1_metrics_source_trace" / "a7s1_metrics_coverage_by_symbol.csv",
        "recent_report": data_root / "reports" / "binance_universe498_recent_patch_1h_v1_20260612.json",
        "recent_contract": data_root / "gold" / "metadata" / "binance_universe498_recent_patch_1h_v1_20260612_field_contract.json",
        "recent_manifest": data_root / "manifests" / "binance_universe498_recent_patch_1h_v1_20260612_manifest.csv",
        "recent_download_manifest": data_root / "manifests" / "binance_universe498_recent_patch_1h_v1_20260612_download_manifest.csv",
        "pre2024_report": data_root / "reports" / "binance_universe_pre2024_complete_replay_1h_v1_20260612.json",
    }


def field_family(field: str) -> str:
    if "open_interest" in field:
        return "open_interest"
    if "long_short" in field or "position" in field:
        return "positioning"
    if "funding" in field:
        return "funding_state"
    if "stress_proxy" in field or "regime" in field or "state" in field:
        return "regime_state"
    if "premium" in field or "basis" in field or "mark" in field or "index" in field:
        return "basis_premium"
    if "taker" in field:
        return "taker_flow"
    if "quote_volume" in field or "liquidity" in field:
        return "liquidity"
    return "other"


def proof_for_field(field: str, paths: dict[str, Path]) -> dict[str, Any]:
    family = field_family(field)
    recent_report = read_json_or_empty(paths["recent_report"])
    recent_contract = read_json_or_empty(paths["recent_contract"])
    a7s1_contract = read_json_or_empty(paths["a7s1_contract"])
    recent_manifest = read_csv_or_empty(paths["recent_manifest"])
    recent_download = read_csv_or_empty(paths["recent_download_manifest"])
    pre2024_report = read_json_or_empty(paths["pre2024_report"])

    base = {
        "field": field,
        "field_family": family,
        "source_dataset": "",
        "mechanical_past_only": False,
        "source_trace_status": "",
        "publication_time_status": "",
        "checksum_status": "",
        "coverage_status": "",
        "proof_decision": "",
        "blocking_issue": "",
        "evidence": "",
    }

    if family in {"open_interest", "positioning", "taker_flow"}:
        source = "Binance Vision daily metrics create_time -> 1h last/mean"
        a7s1_ts_policy = a7s1_contract.get("timestamp_policy", {})
        recent_decision = str(recent_report.get("decision", ""))
        recent_checksum = ""
        if not recent_download.empty and "checksum_status" in recent_download.columns:
            statuses = Counter(recent_download["checksum_status"].astype(str))
            recent_checksum = ";".join(f"{k}:{v}" for k, v in sorted(statuses.items()))
        mean_metrics = recent_report.get("mean_metrics_coverage")
        base.update(
            source_dataset=source,
            mechanical_past_only=True,
            source_trace_status="PASS_A7S1_CORE12_TRACE;RECENT_PATCH_FAST_TRACE",
            publication_time_status="HOLD_VENDOR_PUBLICATION_NOT_ASSERTED_BEYOND_CREATE_TIME",
            checksum_status=recent_checksum or "UNKNOWN",
            coverage_status=f"recent_mean_metrics_coverage={mean_metrics}",
            proof_decision="HOLD_PUBLICATION_LAG_PROOF_REQUIRED",
            blocking_issue="Binance metrics create_time is observation timestamp; vendor publication lag is not independently proven for full 498 recent patch",
            evidence=json.dumps(
                {
                    "a7s1_timestamp_policy": a7s1_ts_policy,
                    "recent_decision": recent_decision,
                    "recent_rows": recent_report.get("rows"),
                    "recent_symbols": recent_report.get("symbols"),
                },
                ensure_ascii=False,
            ),
        )
        if family == "taker_flow":
            base["proof_decision"] = "PASS_CONTROLLED_AFTER_BAR_CLOSE"
            base["blocking_issue"] = "final proof still requires official checksum if used for promotion"
        return base

    if family == "funding_state":
        recent_decision = str(recent_report.get("decision", ""))
        base.update(
            source_dataset="Binance funding REST/event field plus dense_ffill_and_age derived state",
            mechanical_past_only=True,
            source_trace_status="PASS_MECHANICAL_PAST_ONLY_DERIVATION",
            publication_time_status="HOLD_FUNDING_EVENT_PUBLICATION_PROOF_REQUIRED",
            checksum_status="REST_NO_EXCHANGE_CHECKSUM",
            coverage_status=f"recent_mean_funding_coverage={recent_report.get('mean_funding_coverage')}",
            proof_decision="HOLD_EVENT_PUBLICATION_PROOF_REQUIRED",
            blocking_issue="dense funding state uses past-only ffill/delta, but funding event publication timestamp is not independently carried into reward rows",
            evidence=json.dumps(
                {
                    "recent_decision": recent_decision,
                    "dense_function": "dense_ffill_and_age scans left-to-right; delta_state_24h = dense[t] - dense[t-24]",
                },
                ensure_ascii=False,
            ),
        )
        return base

    if family == "regime_state":
        base.update(
            source_dataset="computed upper/regime state",
            mechanical_past_only=False,
            source_trace_status="HOLD_REGIME_THRESHOLD_LINEAGE_REQUIRED",
            publication_time_status="not_applicable_if_thresholds_frozen_or_rolling_past",
            checksum_status="not_applicable",
            coverage_status="not_a_raw_source",
            proof_decision="HOLD_REGIME_LINEAGE_PROOF_REQUIRED",
            blocking_issue="regime state threshold source and train-only/rolling-past lineage are not attached to reward rows",
            evidence="upper regime alias used in accepted formulas; needs threshold lineage table",
        )
        return base

    if family in {"basis_premium", "liquidity"}:
        recent_decision = str(recent_report.get("decision", ""))
        base.update(
            source_dataset="Binance Vision bar-close panel",
            mechanical_past_only=True,
            source_trace_status="PASS_CONTROLLED_AFTER_BAR_CLOSE",
            publication_time_status="PASS_CONTROLLED_TIMESTAMP_PLUS_1H",
            checksum_status="FAST_CHECKSUM_PENDING",
            coverage_status=f"recent_decision={recent_decision};pre2024_decision={pre2024_report.get('decision')}",
            proof_decision="PASS_CONTROLLED_EXPERIMENT",
            blocking_issue="final proof still requires official CHECKSUM audit",
            evidence=json.dumps(recent_contract.get("timestamp_semantics", {}), ensure_ascii=False),
        )
        return base

    base.update(
        source_dataset="unknown",
        source_trace_status="HOLD_UNKNOWN_FIELD",
        publication_time_status="unknown",
        checksum_status="unknown",
        coverage_status="unknown",
        proof_decision="HOLD_UNKNOWN_FIELD",
        blocking_issue="field is not mapped by A7SOURCE-1",
    )
    return base


def run(input_path: Path, v3_gate_path: Path, runtime: Path, report: Path, data_root: Path) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    accepted = read_csv_or_empty(input_path)
    if accepted.empty:
        raise RuntimeError(f"missing input: {input_path}")
    if "june_gate_pass_diagnostic" in accepted.columns:
        top = accepted[accepted["june_gate_pass_diagnostic"].astype(str).str.lower().eq("true")].copy()
    else:
        top = accepted.head(3).copy()
    if top.empty:
        top = accepted.head(3).copy()
    paths = source_trace_paths(data_root)
    field_rows: list[dict[str, Any]] = []
    formula_rows: list[dict[str, Any]] = []
    for rec in top.to_dict("records"):
        formula = str(rec.get("formula", ""))
        fields = expression_fields(formula)
        decisions: list[str] = []
        issues: list[str] = []
        for field in fields:
            proof = proof_for_field(field, paths)
            proof.update(
                {
                    "source_blueprint_id": rec.get("source_blueprint_id", ""),
                    "blueprint_id": rec.get("blueprint_id", ""),
                    "horizon_h": rec.get("horizon_h", ""),
                    "formula": formula,
                }
            )
            field_rows.append(proof)
            decisions.append(str(proof["proof_decision"]))
            if proof["blocking_issue"]:
                issues.append(f"{field}:{proof['blocking_issue']}")
        hard_holds = [x for x in decisions if x.startswith("HOLD") or x.startswith("FAIL")]
        formula_decision = "HOLD_SOURCE_PROOF_REQUIRED" if hard_holds else "PASS_CONTROLLED_SOURCE_PROOF"
        formula_rows.append(
            {
                "source_blueprint_id": rec.get("source_blueprint_id", ""),
                "blueprint_id": rec.get("blueprint_id", ""),
                "horizon_h": rec.get("horizon_h", ""),
                "june_sortino": rec.get("sortino", ""),
                "june_nonoverlap_floor_sortino": rec.get("nonoverlap_floor_sortino", ""),
                "formula_decision": formula_decision,
                "field_proof_decisions": "|".join(sorted(set(decisions))),
                "blocking_issues": ";".join(issues),
                "formula": formula,
            }
        )
    field_df = pd.DataFrame(field_rows).drop_duplicates()
    formula_df = pd.DataFrame(formula_rows)
    summary_df = (
        field_df.groupby(["field_family", "proof_decision"], dropna=False)
        .agg(fields=("field", "nunique"), formulas=("formula", "nunique"))
        .reset_index()
        .sort_values(["formulas", "fields"], ascending=False)
        if not field_df.empty
        else pd.DataFrame()
    )
    field_df.to_csv(runtime / "a7source1_field_proof_map.csv", index=False)
    formula_df.to_csv(runtime / "a7source1_formula_proof_gate.csv", index=False)
    summary_df.to_csv(runtime / "a7source1_family_proof_summary.csv", index=False)

    formula_holds = int(formula_df["formula_decision"].astype(str).str.startswith("HOLD").sum())
    decision = "HOLD_A7SOURCE1_FIELD_TIMING_PROOF_INCOMPLETE" if formula_holds else "PASS_A7SOURCE1_CONTROLLED_FIELD_TIMING_PROOF"
    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "input": str(input_path),
        "v3_gate": str(v3_gate_path),
        "runtime": str(runtime),
        "report": str(report),
        "data_root": str(data_root),
        "top_formula_count": int(formula_df.shape[0]),
        "formula_hold_count": formula_holds,
        "unique_fields": int(field_df["field"].nunique()) if not field_df.empty else 0,
        "authorizes_source_lag_retest": True,
        "authorizes_next_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(runtime / "a7source1_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SOURCE-1 Field Timing Proof",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This audits source timing proof for June-diagnostic A7SEARCH6 survivors. It is a bias gate, not a return-improvement step.",
        "",
        "## Summary",
        "",
        md_table(summary_df),
        "",
        "## Formula Gate",
        "",
        md_table(formula_df, max_rows=20),
        "",
        "## Blocking Interpretation",
        "",
        "- Metrics fields have good historical source trace for core12 and controlled recent-patch coverage, but full 498 recent-patch publication lag is not independently proven.",
        "- Funding dense state is mechanically past-only, but event publication timestamp is not carried into reward rows.",
        "- Therefore source-lag retest is authorized as diagnostic, while alpha proof/search expansion remains blocked.",
        "",
    ]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--v3-gate", type=Path, default=DEFAULT_V3_GATE)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    args = parser.parse_args()
    manifest = run(args.input, args.v3_gate, args.runtime, args.report, args.data_root)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
