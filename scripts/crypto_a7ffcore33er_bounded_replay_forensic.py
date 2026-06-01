from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore33er_bounded_replay_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE33ER_BOUNDED_REPLAY_FORENSIC_20260602.md"
CORE33E = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution" / "a7ffcore33e_manifest.json"
SUMMARY = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution" / "a7ffcore33e_candidate_summary.csv"
FAMILY = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution" / "a7ffcore33e_family_summary.csv"
RESULTS = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution" / "a7ffcore33e_replay_results.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE33E)
    if source.get("decision") != "HOLD_A7FFCORE33E_BOUNDED_REPLAY_INSUFFICIENT":
        raise SystemExit(f"CORE33E is not in expected HOLD state: {source.get('decision')}")
    summary = pd.read_csv(SUMMARY)
    family = pd.read_csv(FAMILY)
    results = pd.read_csv(RESULTS)
    family_diag = family.copy()
    family_diag["dominant_failure"] = "mixed"
    family_diag.loc[
        family_diag["median_control_ratio"].lt(1.0) & family_diag["median_net_spread"].lt(0),
        "dominant_failure",
    ] = "direction_or_orientation_mismatch_with_control_clean_response"
    family_diag.loc[family_diag["median_control_ratio"].ge(1.0), "dominant_failure"] = "control_dominated_bounded_replay"
    candidate_diag = summary.copy()
    candidate_diag["orientation_repair_candidate"] = (
        candidate_diag["median_control_ratio"].lt(1.0)
        & candidate_diag["median_net_spread"].lt(0)
        & candidate_diag["control_clean_count"].ge(18)
    )
    candidate_diag["control_repair_candidate"] = (
        candidate_diag["positive_net_count"].ge(14)
        & candidate_diag["control_clean_count"].ge(12)
        & candidate_diag["median_control_ratio"].ge(1.0)
    )
    split_label = (
        results.groupby(["family_id", "label_family", "horizon_h", "split"], as_index=False)
        .agg(
            positive_rate=("positive_net", "mean"),
            median_control_ratio=("control_ratio", "median"),
            median_net_spread=("net_spread", "median"),
            row_count=("replay_candidate_id", "count"),
        )
        .sort_values(["family_id", "label_family", "horizon_h", "split"])
    )
    repair_plan = pd.DataFrame(
        [
            {
                "repair": "train_only_orientation",
                "target": "F1a control-clean but negative net spread",
                "rule": "fit sign on train_2024 only, freeze sign, then evaluate validation/test/recent",
                "authorized_next": True,
            },
            {
                "repair": "control_dominance_filter",
                "target": "F1b/F2a control-dominated candidates",
                "rule": "drop or down-rank candidates with train control_ratio >= 1 before replay queue",
                "authorized_next": True,
            },
            {
                "repair": "cost_turnover_sensitivity",
                "target": "all bounded replay candidates",
                "rule": "report 2/5/10bps net spread and turnover by split before replay promotion",
                "authorized_next": True,
            },
            {
                "repair": "large_search",
                "target": "none",
                "rule": "not authorized until repaired bounded replay survivors exist",
                "authorized_next": False,
            },
        ]
    )
    orientation_count = int(candidate_diag["orientation_repair_candidate"].sum())
    control_repair_count = int(candidate_diag["control_repair_candidate"].sum())
    decision = (
        "PASS_A7FFCORE33ER_FORENSIC_READY_FOR_CORE34_ORIENTATION_REPAIR_CONTRACT"
        if orientation_count + control_repair_count > 0
        else "HOLD_A7FFCORE33ER_NO_REPAIRABLE_REPLAY_PATTERN"
    )
    manifest = {
        "stage": "A7FF-CORE33ER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE33E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "orientation_repair_candidate_count": orientation_count,
        "control_repair_candidate_count": control_repair_count,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core34_contract": decision.startswith("PASS_"),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE34 train-only orientation/control repair contract"
        if decision.startswith("PASS_")
        else "CORE33ER blocker review",
    }
    family_diag.to_csv(RUNTIME / "a7ffcore33er_family_failure_diagnostic.csv", index=False)
    candidate_diag.to_csv(RUNTIME / "a7ffcore33er_candidate_failure_diagnostic.csv", index=False)
    split_label.to_csv(RUNTIME / "a7ffcore33er_split_label_failure_map.csv", index=False)
    repair_plan.to_csv(RUNTIME / "a7ffcore33er_repair_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore33er_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE33ER BOUNDED REPLAY FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE33ER freezes the bounded replay failure. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- orientation_repair_candidate_count: `{orientation_count}`",
        f"- control_repair_candidate_count: `{control_repair_count}`",
        "",
        "## Family Diagnostic",
        "",
        md_table(family_diag),
        "",
        "## Candidate Diagnostic Preview",
        "",
        md_table(candidate_diag.head(40)),
        "",
        "## Repair Plan",
        "",
        md_table(repair_plan),
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
