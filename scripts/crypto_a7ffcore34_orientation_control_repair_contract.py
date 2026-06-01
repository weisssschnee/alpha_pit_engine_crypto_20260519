from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore34_orientation_control_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE34_ORIENTATION_CONTROL_REPAIR_CONTRACT_20260602.md"
CORE33ER = REPO / "runtime" / "a7ffcore33er_bounded_replay_forensic" / "a7ffcore33er_manifest.json"
DIAG = REPO / "runtime" / "a7ffcore33er_bounded_replay_forensic" / "a7ffcore33er_candidate_failure_diagnostic.csv"
CORE33_QUEUE = REPO / "runtime" / "a7ffcore33_bounded_replay_contract" / "a7ffcore33_replay_candidate_queue.csv"


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
    source = read_json(CORE33ER)
    if source.get("decision") != "PASS_A7FFCORE33ER_FORENSIC_READY_FOR_CORE34_ORIENTATION_REPAIR_CONTRACT":
        raise SystemExit(f"CORE33ER not ready for CORE34: {source.get('decision')}")
    diag = pd.read_csv(DIAG)
    queue = pd.read_csv(CORE33_QUEUE)
    repair_candidates = diag[
        diag["orientation_repair_candidate"].astype(bool) | diag["control_repair_candidate"].astype(bool)
    ].merge(
        queue,
        on=["replay_candidate_id", "family_id"],
        how="left",
        suffixes=("", "_queue"),
    )
    repair_candidates["repair_mode"] = "control_filter"
    repair_candidates.loc[repair_candidates["orientation_repair_candidate"].astype(bool), "repair_mode"] = "train_only_orientation"
    repair_candidates["executes_in_core34"] = False
    repair_protocol = pd.DataFrame(
        [
            {
                "step": "train_orientation_fit",
                "rule": "fit sign only on train_2024 using L1/L5 net spread; freeze sign for later splits",
                "blocking": True,
            },
            {
                "step": "control_filter",
                "rule": "reject candidate if train_2024 stale-control ratio >= 1.0 after orientation",
                "blocking": True,
            },
            {
                "step": "multi_cost_report",
                "rule": "report 2/5/10bps net spread by split and label",
                "blocking": True,
            },
            {
                "step": "no_test_orientation",
                "rule": "validation/test/recent may evaluate only; cannot set sign or thresholds",
                "blocking": True,
            },
            {
                "step": "no_search",
                "rule": "repair execution is bounded replay repair only, not formula generation/search",
                "blocking": True,
            },
        ]
    )
    family_summary = (
        repair_candidates.groupby(["family_id", "repair_mode"], as_index=False)
        .agg(candidate_count=("replay_candidate_id", "count"))
        .sort_values(["family_id", "repair_mode"])
    )
    gates = pd.DataFrame(
        [
            {
                "gate": "repair_candidate_count",
                "threshold": ">= 6",
                "observed": int(repair_candidates.shape[0]),
                "pass": bool(repair_candidates.shape[0] >= 6),
            },
            {
                "gate": "repair_family_count",
                "threshold": ">= 2",
                "observed": int(repair_candidates["family_id"].nunique()),
                "pass": bool(repair_candidates["family_id"].nunique() >= 2),
            },
            {
                "gate": "orientation_candidates",
                "threshold": ">= 1",
                "observed": int(repair_candidates["orientation_repair_candidate"].astype(bool).sum()),
                "pass": bool(repair_candidates["orientation_repair_candidate"].astype(bool).sum() >= 1),
            },
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE34E train-only orientation/control repair execution": True},
        "not_authorized": {
            "new_formula_generation": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    decision = (
        "PASS_A7FFCORE34_ORIENTATION_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE34E"
        if bool(gates["pass"].all())
        else "HOLD_A7FFCORE34_REPAIR_CONTRACT_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE34",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE33ER",
        "source_decision": source.get("decision"),
        "decision": decision,
        "repair_candidate_count": int(repair_candidates.shape[0]),
        "repair_family_count": int(repair_candidates["family_id"].nunique()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core34e_execution": decision.startswith("PASS_"),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE34E train-only orientation/control repair execution"
        if decision.startswith("PASS_")
        else "CORE34 contract repair",
    }
    repair_candidates.to_csv(RUNTIME / "a7ffcore34_repair_candidate_queue.csv", index=False)
    repair_protocol.to_csv(RUNTIME / "a7ffcore34_repair_protocol.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore34_family_summary.csv", index=False)
    gates.to_csv(RUNTIME / "a7ffcore34_gate_audit.csv", index=False)
    write_json(RUNTIME / "a7ffcore34_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore34_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE34 ORIENTATION/CONTROL REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE34 defines a train-only orientation and control repair path after CORE33E bounded replay failed. It does not execute new generation, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Gate Audit",
        "",
        md_table(gates),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Repair Protocol",
        "",
        md_table(repair_protocol),
        "",
        "## Repair Candidate Queue",
        "",
        md_table(repair_candidates[["replay_candidate_id", "family_id", "repair_mode", "positive_net_count", "control_clean_count", "median_control_ratio", "median_net_spread"]]),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
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
