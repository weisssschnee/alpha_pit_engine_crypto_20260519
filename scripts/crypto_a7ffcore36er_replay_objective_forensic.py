from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore36er_replay_objective_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE36ER_REPLAY_OBJECTIVE_FORENSIC_20260602.md"
CORE36E = REPO / "runtime" / "a7ffcore36e_replay_objective_reset_execution" / "a7ffcore36e_manifest.json"
CORE36E_CANDIDATES = REPO / "runtime" / "a7ffcore36e_replay_objective_reset_execution" / "a7ffcore36e_candidate_rescore.csv"
CORE36E_SPLITS = REPO / "runtime" / "a7ffcore36e_replay_objective_reset_execution" / "a7ffcore36e_split_gate_audit.csv"


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


def bool_sum(series: pd.Series) -> int:
    return int(series.fillna(False).astype(bool).sum())


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE36E)
    if source.get("decision") != "HOLD_A7FFCORE36E_REPLAY_OBJECTIVE_RESET_NO_EXECUTABLE_SURVIVORS":
        raise SystemExit(f"CORE36E not in expected HOLD state: {source.get('decision')}")

    candidates = pd.read_csv(CORE36E_CANDIDATES)
    splits = pd.read_csv(CORE36E_SPLITS)

    failure_counts = (
        candidates.groupby(["family_id", "failure_reason"], as_index=False)
        .agg(candidate_count=("replay_candidate_id", "count"))
        .sort_values(["family_id", "failure_reason"])
    )
    global_failure_counts = (
        candidates.groupby("failure_reason", as_index=False)
        .agg(candidate_count=("replay_candidate_id", "count"))
        .sort_values("candidate_count", ascending=False)
    )
    train_pass = candidates[candidates["train_objective_pass"].fillna(False).astype(bool)].copy()
    train_pass_cols = [
        "replay_candidate_id",
        "family_id",
        "dataset",
        "motif",
        "operator",
        "primary_field",
        "partner_field",
        "train_median_net_spread",
        "train_median_control_ratio",
        "oos_split_pass_count",
        "oos_min_split_net_spread",
        "oos_worst_control_ratio",
        "failure_reason",
    ]
    train_pass_detail = train_pass[[c for c in train_pass_cols if c in train_pass.columns]].sort_values(
        ["oos_split_pass_count", "train_median_net_spread"], ascending=[False, False]
    )

    split_forensic = splits.merge(
        candidates[["replay_candidate_id", "family_id", "failure_reason", "train_objective_pass"]],
        on=["replay_candidate_id", "family_id"],
        how="left",
    )
    split_forensic_summary = (
        split_forensic.groupby(["family_id", "split"], as_index=False)
        .agg(
            candidate_count=("replay_candidate_id", "nunique"),
            split_pass_count=("split_objective_pass", bool_sum),
            median_net_spread=("median_net_spread", "median"),
            median_control_ratio=("median_control_ratio", "median"),
            median_positive_rows=("positive_rows", "median"),
            median_control_clean_rows=("control_clean_rows", "median"),
        )
        .sort_values(["family_id", "split"])
    )
    family_diagnosis = (
        candidates.groupby("family_id", as_index=False)
        .agg(
            candidate_count=("replay_candidate_id", "count"),
            train_objective_pass_count=("train_objective_pass", bool_sum),
            selected_count=("selected_for_core37_contract", bool_sum),
            strict_survivor_count=("strict_executable_survivor", bool_sum),
            median_train_net_spread=("train_median_net_spread", "median"),
            median_train_control_ratio=("train_median_control_ratio", "median"),
            median_oos_min_split_net_spread=("oos_min_split_net_spread", "median"),
            median_oos_worst_control_ratio=("oos_worst_control_ratio", "median"),
        )
        .sort_values("family_id")
    )
    family_diagnosis["diagnosis"] = "train_objective_control_fail"
    family_diagnosis.loc[
        family_diagnosis["train_objective_pass_count"].gt(0)
        & family_diagnosis["selected_count"].eq(0),
        "diagnosis",
    ] = "train_positive_but_oos_split_unstable"
    family_diagnosis.loc[
        family_diagnosis["strict_survivor_count"].gt(0),
        "diagnosis",
    ] = "has_strict_survivor"

    authorization = pd.DataFrame(
        [
            {
                "task": "A7FF-CORE37X replay-objective failure freeze / route arbitration contract",
                "status": "AUTHORIZED_CONTRACT_ONLY",
                "reason": "CORE36E found no executable survivors after objective reset; route decision is needed before any new work",
            },
            {
                "task": "same CORE33/34/36 queue rerun",
                "status": "NOT_AUTHORIZED",
                "reason": "CORE36E exhausted executable-spread-first rescoring without survivors",
            },
            {
                "task": "formula_search",
                "status": "NOT_AUTHORIZED",
                "reason": "no executable replay survivor and no family with stable train-to-OOS translation",
            },
            {
                "task": "large_search",
                "status": "NOT_AUTHORIZED",
                "reason": "numeric/preflight response still fails executable replay translation",
            },
            {
                "task": "alpha_proof / shadow / paper / live",
                "status": "NOT_AUTHORIZED",
                "reason": "no alpha proof object or replay survivor",
            },
        ]
    )
    decision = "PASS_A7FFCORE36ER_REPLAY_OBJECTIVE_FORENSIC_COMPLETE_READY_FOR_CORE37X"
    manifest = {
        "stage": "A7FF-CORE36ER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE36E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "candidate_count": int(candidates.shape[0]),
        "train_objective_pass_count": int(candidates["train_objective_pass"].fillna(False).astype(bool).sum()),
        "selected_count": int(candidates["selected_for_core37_contract"].fillna(False).astype(bool).sum()),
        "strict_survivor_count": int(candidates["strict_executable_survivor"].fillna(False).astype(bool).sum()),
        "dominant_failure": "train_to_oos_executable_spread_instability_after_control_gating",
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core37x_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE37X replay-objective failure freeze / route arbitration contract",
    }
    failure_counts.to_csv(RUNTIME / "a7ffcore36er_family_failure_counts.csv", index=False)
    global_failure_counts.to_csv(RUNTIME / "a7ffcore36er_global_failure_counts.csv", index=False)
    train_pass_detail.to_csv(RUNTIME / "a7ffcore36er_train_pass_oos_failure_detail.csv", index=False)
    split_forensic_summary.to_csv(RUNTIME / "a7ffcore36er_split_forensic_summary.csv", index=False)
    family_diagnosis.to_csv(RUNTIME / "a7ffcore36er_family_diagnosis.csv", index=False)
    authorization.to_csv(RUNTIME / "a7ffcore36er_authorization_matrix.csv", index=False)
    write_json(RUNTIME / "a7ffcore36er_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE36ER REPLAY OBJECTIVE RESET FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE36ER freezes the CORE36E failure. It does not run replay, formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Main Finding",
        "",
        "`train_to_oos_executable_spread_instability_after_control_gating`",
        "",
        "Only F1a produced train objective pass rows, and those rows failed OOS split balance. F1b/F2a are primarily train objective/control failures under the executable-spread-first reset.",
        "",
        "## Global Failure Counts",
        "",
        md_table(global_failure_counts),
        "",
        "## Family Diagnosis",
        "",
        md_table(family_diagnosis),
        "",
        "## Train-Pass OOS Failure Detail",
        "",
        md_table(train_pass_detail),
        "",
        "## Split Forensic Summary",
        "",
        md_table(split_forensic_summary),
        "",
        "## Authorization Matrix",
        "",
        md_table(authorization),
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
