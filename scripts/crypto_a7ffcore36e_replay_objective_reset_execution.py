from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore36e_replay_objective_reset_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE36E_REPLAY_OBJECTIVE_RESET_EXECUTION_20260602.md"
CORE36 = REPO / "runtime" / "a7ffcore36_replay_objective_reset_contract" / "a7ffcore36_manifest.json"
CORE33_QUEUE = REPO / "runtime" / "a7ffcore33_bounded_replay_contract" / "a7ffcore33_replay_candidate_queue.csv"
CORE33E_RESULTS = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution" / "a7ffcore33e_replay_results.csv"

PRIMARY_LABELS = {"L1", "L5"}
PRIMARY_HORIZONS = {8, 24}
TRAIN_SPLIT = "train_2024"
OOS_SPLITS = ["validation_2025H1", "test_2025H2", "recent_2026JanApr"]


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

    source = read_json(CORE36)
    if source.get("decision") != "PASS_A7FFCORE36_REPLAY_OBJECTIVE_RESET_CONTRACT_READY_FOR_CORE36E":
        raise SystemExit(f"CORE36 not ready for CORE36E: {source.get('decision')}")

    queue = pd.read_csv(CORE33_QUEUE)
    replay = pd.read_csv(CORE33E_RESULTS)
    replay["is_primary_label"] = replay["label_family"].astype(str).isin(PRIMARY_LABELS)
    replay["is_primary_horizon"] = replay["horizon_h"].astype(int).isin(PRIMARY_HORIZONS)
    replay["is_primary_objective_row"] = replay["is_primary_label"] & replay["is_primary_horizon"]
    primary = replay[replay["is_primary_objective_row"]].copy()

    train = primary[primary["split"].eq(TRAIN_SPLIT)].copy()
    train_summary = (
        train.groupby("replay_candidate_id", as_index=False)
        .agg(
            train_rows=("replay_candidate_id", "count"),
            train_median_net_spread=("net_spread", "median"),
            train_min_net_spread=("net_spread", "min"),
            train_positive_rows=("positive_net", bool_sum),
            train_median_control_ratio=("control_ratio", "median"),
            train_max_control_ratio=("control_ratio", "max"),
            train_control_clean_rows=("control_clean", bool_sum),
            train_median_turnover=("turnover", "median"),
            train_median_tstat=("tstat", "median"),
        )
    )
    train_summary["train_control_margin"] = 1.0 - train_summary["train_median_control_ratio"]
    train_summary["train_objective_pass"] = (
        train_summary["train_median_net_spread"].gt(0)
        & train_summary["train_median_control_ratio"].lt(1.0)
        & train_summary["train_positive_rows"].ge(2)
    )

    split_summary = (
        primary.groupby(["replay_candidate_id", "family_id", "split"], as_index=False)
        .agg(
            primary_rows=("replay_candidate_id", "count"),
            median_net_spread=("net_spread", "median"),
            min_net_spread=("net_spread", "min"),
            positive_rows=("positive_net", bool_sum),
            median_control_ratio=("control_ratio", "median"),
            max_control_ratio=("control_ratio", "max"),
            control_clean_rows=("control_clean", bool_sum),
            median_turnover=("turnover", "median"),
            median_tstat=("tstat", "median"),
        )
        .sort_values(["replay_candidate_id", "split"])
    )
    split_summary["split_objective_pass"] = (
        split_summary["median_net_spread"].gt(0)
        & split_summary["median_control_ratio"].lt(1.0)
        & split_summary["positive_rows"].ge(2)
    )
    oos = split_summary[split_summary["split"].isin(OOS_SPLITS)].copy()
    oos_summary = (
        oos.groupby("replay_candidate_id", as_index=False)
        .agg(
            oos_split_count=("split", "nunique"),
            oos_split_pass_count=("split_objective_pass", bool_sum),
            oos_min_split_net_spread=("median_net_spread", "min"),
            oos_median_split_net_spread=("median_net_spread", "median"),
            oos_worst_control_ratio=("median_control_ratio", "max"),
            oos_control_clean_rows=("control_clean_rows", "sum"),
            oos_positive_rows=("positive_rows", "sum"),
        )
    )
    family_meta_cols = [
        "replay_candidate_id",
        "preflight_candidate_id",
        "numeric_probe_id",
        "family_id",
        "dataset",
        "motif",
        "operator",
        "primary_field",
        "partner_field",
        "window_h",
        "expression",
        "cluster_key",
    ]
    meta = queue[[c for c in family_meta_cols if c in queue.columns]].drop_duplicates("replay_candidate_id")
    candidate = meta.merge(train_summary, on="replay_candidate_id", how="left").merge(
        oos_summary, on="replay_candidate_id", how="left"
    )
    fill_zero = [
        "train_rows",
        "train_positive_rows",
        "train_control_clean_rows",
        "oos_split_count",
        "oos_split_pass_count",
        "oos_control_clean_rows",
        "oos_positive_rows",
    ]
    for col in fill_zero:
        if col in candidate.columns:
            candidate[col] = candidate[col].fillna(0).astype(int)
    candidate["oos_all_splits_available"] = candidate["oos_split_count"].ge(len(OOS_SPLITS))
    candidate["oos_two_split_balance_pass"] = candidate["oos_split_pass_count"].ge(2)
    candidate["oos_all_split_balance_pass"] = candidate["oos_split_pass_count"].ge(3)
    candidate["executable_objective_score"] = (
        candidate["train_median_net_spread"].fillna(-1.0) * 10000.0
        + candidate["oos_split_pass_count"].fillna(0) * 1.0
        + candidate["train_control_margin"].fillna(-10.0).clip(lower=-10, upper=2)
        + candidate["oos_median_split_net_spread"].fillna(-1.0) * 5000.0
    )
    candidate["selected_for_core37_contract"] = (
        candidate["train_objective_pass"].fillna(False).astype(bool)
        & candidate["oos_two_split_balance_pass"].fillna(False).astype(bool)
        & candidate["oos_worst_control_ratio"].fillna(99).lt(1.0)
    )
    candidate["strict_executable_survivor"] = (
        candidate["train_objective_pass"].fillna(False).astype(bool)
        & candidate["oos_all_split_balance_pass"].fillna(False).astype(bool)
        & candidate["oos_min_split_net_spread"].fillna(-1.0).gt(0)
        & candidate["oos_worst_control_ratio"].fillna(99).lt(1.0)
    )
    candidate["failure_reason"] = "candidate"
    candidate.loc[~candidate["train_objective_pass"].fillna(False).astype(bool), "failure_reason"] = "train_objective_fail"
    candidate.loc[
        candidate["train_objective_pass"].fillna(False).astype(bool)
        & ~candidate["oos_two_split_balance_pass"].fillna(False).astype(bool),
        "failure_reason",
    ] = "oos_split_balance_fail"
    candidate.loc[
        candidate["train_objective_pass"].fillna(False).astype(bool)
        & candidate["oos_two_split_balance_pass"].fillna(False).astype(bool)
        & candidate["oos_worst_control_ratio"].fillna(99).ge(1.0),
        "failure_reason",
    ] = "oos_control_fail"
    candidate.loc[candidate["selected_for_core37_contract"], "failure_reason"] = "selected_for_core37_contract"
    candidate.loc[candidate["strict_executable_survivor"], "failure_reason"] = "strict_executable_survivor"
    candidate = candidate.sort_values(
        ["strict_executable_survivor", "selected_for_core37_contract", "executable_objective_score"],
        ascending=[False, False, False],
    )

    selected = candidate[candidate["selected_for_core37_contract"]].copy()
    strict_survivors = candidate[candidate["strict_executable_survivor"]].copy()
    selected_family_count = int(selected["family_id"].nunique()) if not selected.empty else 0
    strict_family_count = int(strict_survivors["family_id"].nunique()) if not strict_survivors.empty else 0

    family_summary = (
        candidate.groupby("family_id", as_index=False)
        .agg(
            candidate_count=("replay_candidate_id", "count"),
            train_pass_count=("train_objective_pass", bool_sum),
            two_split_selected_count=("selected_for_core37_contract", bool_sum),
            strict_survivor_count=("strict_executable_survivor", bool_sum),
            median_train_net_spread=("train_median_net_spread", "median"),
            median_oos_min_split_net_spread=("oos_min_split_net_spread", "median"),
            median_train_control_ratio=("train_median_control_ratio", "median"),
            median_oos_worst_control_ratio=("oos_worst_control_ratio", "median"),
            median_objective_score=("executable_objective_score", "median"),
        )
        .sort_values("family_id")
    )
    decision_matrix = pd.DataFrame(
        [
            {
                "gate": "selected_count_ge_4",
                "value": int(selected.shape[0]),
                "pass": bool(selected.shape[0] >= 4),
                "required_for_pass": True,
            },
            {
                "gate": "selected_family_count_ge_2",
                "value": selected_family_count,
                "pass": bool(selected_family_count >= 2),
                "required_for_pass": True,
            },
            {
                "gate": "strict_survivor_count",
                "value": int(strict_survivors.shape[0]),
                "pass": bool(strict_survivors.shape[0] > 0),
                "required_for_pass": False,
            },
            {
                "gate": "strict_survivor_family_count",
                "value": strict_family_count,
                "pass": bool(strict_family_count > 0),
                "required_for_pass": False,
            },
        ]
    )
    pass_ready = bool(selected.shape[0] >= 4 and selected_family_count >= 2)
    decision = (
        "PASS_A7FFCORE36E_REPLAY_OBJECTIVE_SURVIVORS_READY_FOR_CORE37_CONTRACT"
        if pass_ready
        else "HOLD_A7FFCORE36E_REPLAY_OBJECTIVE_RESET_NO_EXECUTABLE_SURVIVORS"
    )
    manifest = {
        "stage": "A7FF-CORE36E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE36",
        "source_decision": source.get("decision"),
        "decision": decision,
        "candidate_count": int(candidate.shape[0]),
        "primary_replay_rows": int(primary.shape[0]),
        "selected_count": int(selected.shape[0]),
        "selected_family_count": selected_family_count,
        "strict_survivor_count": int(strict_survivors.shape[0]),
        "strict_survivor_family_count": strict_family_count,
        "executes_replay": False,
        "executes_search": False,
        "uses_existing_core33e_replay_results": True,
        "authorizes_core37_contract": pass_ready,
        "authorizes_core36er_forensic": not pass_ready,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE37 bounded replay-objective repair contract"
        if pass_ready
        else "A7FF-CORE36ER replay-objective reset forensic",
    }

    candidate.to_csv(RUNTIME / "a7ffcore36e_candidate_rescore.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore36e_family_rescore_summary.csv", index=False)
    selected.to_csv(RUNTIME / "a7ffcore36e_selected_queue.csv", index=False)
    split_summary.to_csv(RUNTIME / "a7ffcore36e_split_gate_audit.csv", index=False)
    decision_matrix.to_csv(RUNTIME / "a7ffcore36e_decision_matrix.csv", index=False)
    write_json(RUNTIME / "a7ffcore36e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE36E REPLAY OBJECTIVE RESET EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE36E re-scores the existing CORE33E bounded replay results with an executable-spread-first objective. It does not generate formulas, run replay, run search, authorize alpha proof, or authorize shadow/paper/live.",
        "",
        "## Summary",
        "",
        f"- candidate_count: `{manifest['candidate_count']}`",
        f"- primary_replay_rows: `{manifest['primary_replay_rows']}`",
        f"- selected_count: `{manifest['selected_count']}`",
        f"- selected_family_count: `{manifest['selected_family_count']}`",
        f"- strict_survivor_count: `{manifest['strict_survivor_count']}`",
        "",
        "## Decision Matrix",
        "",
        md_table(decision_matrix),
        "",
        "## Family Rescore Summary",
        "",
        md_table(family_summary),
        "",
        "## Selected Queue",
        "",
        md_table(selected),
        "",
        "## Candidate Rescore Preview",
        "",
        md_table(candidate.head(40)),
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
