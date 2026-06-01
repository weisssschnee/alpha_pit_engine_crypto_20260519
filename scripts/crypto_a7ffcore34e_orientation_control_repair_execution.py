from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore34e_orientation_control_repair_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE34E_ORIENTATION_CONTROL_REPAIR_EXECUTION_20260602.md"
CORE34 = REPO / "runtime" / "a7ffcore34_orientation_control_repair_contract" / "a7ffcore34_manifest.json"
REPAIR_QUEUE = REPO / "runtime" / "a7ffcore34_orientation_control_repair_contract" / "a7ffcore34_repair_candidate_queue.csv"
CORE33E_RESULTS = REPO / "runtime" / "a7ffcore33e_bounded_replay_execution" / "a7ffcore33e_replay_results.csv"


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
    source = read_json(CORE34)
    if source.get("decision") != "PASS_A7FFCORE34_ORIENTATION_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE34E":
        raise SystemExit(f"CORE34 not ready for CORE34E: {source.get('decision')}")

    repair_queue = pd.read_csv(REPAIR_QUEUE)
    results = pd.read_csv(CORE33E_RESULTS)
    ids = sorted(repair_queue["replay_candidate_id"].astype(str).unique())
    work = results[results["replay_candidate_id"].astype(str).isin(ids)].copy()
    work["cost_proxy"] = work["spread"] - work["net_spread"]
    train = work[work["split"].eq("train_2024") & work["label_family"].isin(["L1", "L5"])].copy()
    sign_map = (
        train.groupby("replay_candidate_id", as_index=False)
        .agg(train_median_spread=("spread", "median"), train_median_control_ratio=("control_ratio", "median"))
    )
    sign_map["orientation_sign"] = np.where(sign_map["train_median_spread"].ge(0), 1, -1)
    sign_map["train_control_filter_pass"] = sign_map["train_median_control_ratio"].lt(1.0)
    work = work.merge(sign_map, on="replay_candidate_id", how="left")
    work["orientation_sign"] = work["orientation_sign"].fillna(1).astype(int)
    work["repaired_spread"] = work["orientation_sign"] * work["spread"]
    work["repaired_net_spread"] = work["repaired_spread"] - work["cost_proxy"].abs()
    work["repaired_positive_net"] = work["repaired_net_spread"].gt(0)
    work["repaired_control_clean"] = work["control_ratio"].lt(1.0)
    work["oos_split"] = work["split"].ne("train_2024")

    candidate_summary = (
        work.groupby(["replay_candidate_id", "family_id"], as_index=False)
        .agg(
            train_control_filter_pass=("train_control_filter_pass", "max"),
            orientation_sign=("orientation_sign", "max"),
            repaired_positive_count=("repaired_positive_net", "sum"),
            repaired_control_clean_count=("repaired_control_clean", "sum"),
            oos_positive_count=("repaired_positive_net", lambda s: int(s[work.loc[s.index, "oos_split"]].sum())),
            oos_control_clean_count=("repaired_control_clean", lambda s: int(s[work.loc[s.index, "oos_split"]].sum())),
            median_repaired_net_spread=("repaired_net_spread", "median"),
            train_median_control_ratio=("train_median_control_ratio", "max"),
        )
        .sort_values(["oos_positive_count", "oos_control_clean_count", "median_repaired_net_spread"], ascending=[False, False, False])
    )
    split_summary = (
        work.groupby(["replay_candidate_id", "family_id", "split"], as_index=False)
        .agg(
            positive_count=("repaired_positive_net", "sum"),
            control_clean_count=("repaired_control_clean", "sum"),
            median_repaired_net_spread=("repaired_net_spread", "median"),
            median_control_ratio=("control_ratio", "median"),
            row_count=("replay_candidate_id", "count"),
        )
        .sort_values(["replay_candidate_id", "split"])
    )
    split_pivot = split_summary.pivot_table(
        index=["replay_candidate_id", "family_id"],
        columns="split",
        values="positive_count",
        aggfunc="first",
        fill_value=0,
    ).reset_index()
    for col in ["validation_2025H1", "test_2025H2", "recent_2026JanApr"]:
        if col not in split_pivot.columns:
            split_pivot[col] = 0
    candidate_summary = candidate_summary.merge(split_pivot, on=["replay_candidate_id", "family_id"], how="left")
    candidate_summary["all_oos_splits_positive"] = (
        candidate_summary["validation_2025H1"].ge(3)
        & candidate_summary["test_2025H2"].ge(3)
        & candidate_summary["recent_2026JanApr"].ge(3)
    )
    survivors = candidate_summary[
        candidate_summary["train_control_filter_pass"].astype(bool)
        & candidate_summary["oos_positive_count"].ge(15)
        & candidate_summary["oos_control_clean_count"].ge(15)
        & candidate_summary["all_oos_splits_positive"].astype(bool)
    ].copy()
    family_summary = (
        candidate_summary.groupby("family_id", as_index=False)
        .agg(
            repair_candidate_count=("replay_candidate_id", "count"),
            survivor_count=("replay_candidate_id", lambda s: int(s.isin(survivors["replay_candidate_id"]).sum())),
            median_oos_positive_count=("oos_positive_count", "median"),
            median_oos_control_clean_count=("oos_control_clean_count", "median"),
            median_repaired_net_spread=("median_repaired_net_spread", "median"),
        )
        .sort_values("family_id")
    )
    survivor_family_count = int(survivors["family_id"].nunique()) if not survivors.empty else 0
    decision = (
        "PASS_A7FFCORE34E_REPAIRED_REPLAY_SURVIVORS_READY_FOR_CORE35_ARBITRATION"
        if survivors.shape[0] >= 4 and survivor_family_count >= 2
        else "HOLD_A7FFCORE34E_REPAIR_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE34E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE34",
        "source_decision": source.get("decision"),
        "decision": decision,
        "repair_candidate_count": int(candidate_summary.shape[0]),
        "survivor_count": int(survivors.shape[0]),
        "survivor_family_count": survivor_family_count,
        "executes_replay_repair": True,
        "executes_search": False,
        "authorizes_core35_arbitration": decision.startswith("PASS_"),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE35 search-readiness arbitration" if decision.startswith("PASS_") else "CORE34E repair forensic",
    }
    work.to_csv(RUNTIME / "a7ffcore34e_repaired_replay_results.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore34e_candidate_summary.csv", index=False)
    split_summary.to_csv(RUNTIME / "a7ffcore34e_split_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore34e_family_summary.csv", index=False)
    survivors.to_csv(RUNTIME / "a7ffcore34e_survivors.csv", index=False)
    write_json(RUNTIME / "a7ffcore34e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE34E ORIENTATION/CONTROL REPAIR EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE34E applies train-only orientation and train control filtering to bounded replay repair candidates. It does not execute search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- repair_candidate_count: `{manifest['repair_candidate_count']}`",
        f"- survivor_count: `{manifest['survivor_count']}`",
        f"- survivor_family_count: `{survivor_family_count}`",
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Survivors",
        "",
        md_table(survivors),
        "",
        "## Candidate Summary Preview",
        "",
        md_table(candidate_summary.head(40)),
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
