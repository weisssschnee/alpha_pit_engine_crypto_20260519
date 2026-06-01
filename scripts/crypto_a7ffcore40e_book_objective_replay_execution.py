from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore40e_book_objective_replay_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE40E_BOOK_OBJECTIVE_REPLAY_EXECUTION_20260602.md"
CORE40 = REPO / "runtime" / "a7ffcore40_book_objective_replay_contract" / "a7ffcore40_manifest.json"
BOOK_OBJECTIVES = REPO / "runtime" / "a7ffcore40_book_objective_replay_contract" / "a7ffcore40_book_objectives.csv"


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
    source = read_json(CORE40)
    if source.get("decision") != "PASS_A7FFCORE40_BOOK_OBJECTIVE_REPLAY_CONTRACT_READY_FOR_CORE40E":
        raise SystemExit(f"CORE40 not ready for CORE40E: {source.get('decision')}")
    packet_path = Path(str(source.get("packet_sample_path")))
    if not packet_path.exists():
        raise SystemExit(f"missing packet sample: {packet_path}")

    packet = pd.read_parquet(packet_path)
    objectives = pd.read_csv(BOOK_OBJECTIVES)
    label_map = dict(zip(objectives["book_objective"], objectives["label_column"]))
    reverse_label = {
        "cs_relative_return": "L1_cross_sectional_relative_return",
        "market_beta_residual_return": "L2_market_beta_residual_return",
        "vol_adjusted_return": "L5_vol_adjusted_return",
    }
    objective_rows = []
    for objective_id, label_col in label_map.items():
        label_id = reverse_label.get(label_col, "L1_cross_sectional_relative_return")
        work = packet[packet["label_id"].eq(label_id)].copy()
        if work.empty:
            continue
        work["objective_id"] = objective_id
        if objective_id == "B4_liquidity_cost_capped_book":
            work["weight"] = work["capped_weight"]
        else:
            work["weight"] = work["raw_weight"]
        work["weighted_return"] = work["weight"] * pd.to_numeric(work[label_col], errors="coerce")
        work["cost"] = work["weight"].abs() * pd.to_numeric(work["cost_bps"], errors="coerce") / 10000.0
        objective_rows.append(work)
    obj = pd.concat(objective_rows, ignore_index=True) if objective_rows else pd.DataFrame()
    group_cols = ["candidate_id", "family_id", "objective_id", "horizon_h", "split", "control_variant"]
    aggregate = (
        obj.groupby(group_cols, as_index=False)
        .agg(
            book_return=("weighted_return", "sum"),
            book_cost=("cost", "sum"),
            row_count=("symbol", "count"),
            timestamp_count=("timestamp", "nunique"),
            gross_weight=("weight", lambda s: float(np.nansum(np.abs(s)))),
        )
    )
    aggregate["net_book_return"] = aggregate["book_return"] - aggregate["book_cost"]
    original = aggregate[aggregate["control_variant"].eq("original")].copy()
    controls = (
        aggregate[~aggregate["control_variant"].eq("original")]
        .groupby(["candidate_id", "objective_id", "horizon_h", "split"], as_index=False)
        .agg(max_abs_control_net=("net_book_return", lambda s: float(np.nanmax(np.abs(s))) if len(s) else np.nan))
    )
    replay = original.merge(controls, on=["candidate_id", "objective_id", "horizon_h", "split"], how="left")
    replay["control_ratio"] = replay["max_abs_control_net"].abs() / (replay["net_book_return"].abs() + 1e-12)
    replay["positive_net"] = replay["net_book_return"].gt(0)
    replay["control_clean"] = replay["control_ratio"].lt(1.0)
    replay["split_pass"] = replay["positive_net"] & replay["control_clean"]

    candidate_summary = (
        replay.groupby(["candidate_id", "family_id"], as_index=False)
        .agg(
            replay_rows=("candidate_id", "count"),
            positive_rows=("positive_net", bool_sum),
            control_clean_rows=("control_clean", bool_sum),
            split_pass_rows=("split_pass", bool_sum),
            median_net_book_return=("net_book_return", "median"),
            median_control_ratio=("control_ratio", "median"),
            max_abs_net_book_return=("net_book_return", lambda s: float(np.nanmax(np.abs(s))) if len(s) else np.nan),
        )
    )
    split_balance = (
        replay.groupby(["candidate_id", "family_id", "split"], as_index=False)
        .agg(
            split_pass_count=("split_pass", bool_sum),
            median_net_book_return=("net_book_return", "median"),
            median_control_ratio=("control_ratio", "median"),
        )
    )
    train = split_balance[split_balance["split"].eq("train_2024")][
        ["candidate_id", "split_pass_count", "median_net_book_return", "median_control_ratio"]
    ].rename(
        columns={
            "split_pass_count": "train_split_pass_count",
            "median_net_book_return": "train_median_net_book_return",
            "median_control_ratio": "train_median_control_ratio",
        }
    )
    oos = split_balance[~split_balance["split"].eq("train_2024")].copy()
    oos_summary = (
        oos.groupby("candidate_id", as_index=False)
        .agg(
            oos_split_count=("split", "nunique"),
            oos_positive_split_count=("median_net_book_return", lambda s: int((s > 0).sum())),
            oos_control_clean_split_count=("median_control_ratio", lambda s: int((s < 1.0).sum())),
            oos_min_net_book_return=("median_net_book_return", "min"),
            oos_worst_control_ratio=("median_control_ratio", "max"),
        )
    )
    candidate_summary = candidate_summary.merge(train, on="candidate_id", how="left").merge(oos_summary, on="candidate_id", how="left")
    candidate_summary["book_survivor"] = (
        candidate_summary["train_median_net_book_return"].fillna(-1).gt(0)
        & candidate_summary["train_median_control_ratio"].fillna(99).lt(1.0)
        & candidate_summary["oos_positive_split_count"].fillna(0).ge(2)
        & candidate_summary["oos_control_clean_split_count"].fillna(0).ge(2)
    )
    survivors = candidate_summary[candidate_summary["book_survivor"]].copy()
    family_summary = (
        candidate_summary.groupby("family_id", as_index=False)
        .agg(
            candidate_count=("candidate_id", "count"),
            survivor_count=("book_survivor", bool_sum),
            median_net_book_return=("median_net_book_return", "median"),
            median_control_ratio=("median_control_ratio", "median"),
            median_oos_min_net_book_return=("oos_min_net_book_return", "median"),
            median_oos_worst_control_ratio=("oos_worst_control_ratio", "median"),
        )
    )
    objective_summary = (
        replay.groupby("objective_id", as_index=False)
        .agg(
            replay_rows=("candidate_id", "count"),
            positive_rows=("positive_net", bool_sum),
            control_clean_rows=("control_clean", bool_sum),
            median_net_book_return=("net_book_return", "median"),
            median_control_ratio=("control_ratio", "median"),
        )
    )
    survivor_family_count = int(survivors["family_id"].nunique()) if not survivors.empty else 0
    decision = (
        "PASS_A7FFCORE40E_BOOK_OBJECTIVE_SURVIVORS_READY_FOR_CORE41_ARBITRATION"
        if survivors.shape[0] >= 4 and survivor_family_count >= 2
        else "HOLD_A7FFCORE40E_BOOK_OBJECTIVE_REPLAY_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE40E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE40",
        "source_decision": source.get("decision"),
        "decision": decision,
        "packet_rows": int(packet.shape[0]),
        "book_replay_rows": int(replay.shape[0]),
        "survivor_count": int(survivors.shape[0]),
        "survivor_family_count": survivor_family_count,
        "executes_replay": True,
        "executes_search": False,
        "authorizes_core41_arbitration": decision.startswith("PASS_"),
        "authorizes_core40er_forensic": not decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE41 book-objective arbitration" if decision.startswith("PASS_") else "A7FF-CORE40ER book-objective replay forensic",
    }
    aggregate.to_csv(RUNTIME / "a7ffcore40e_book_replay_all_variants.csv", index=False)
    replay.to_csv(RUNTIME / "a7ffcore40e_book_replay_original_vs_controls.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore40e_candidate_summary.csv", index=False)
    split_balance.to_csv(RUNTIME / "a7ffcore40e_split_balance.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore40e_family_summary.csv", index=False)
    objective_summary.to_csv(RUNTIME / "a7ffcore40e_objective_summary.csv", index=False)
    survivors.to_csv(RUNTIME / "a7ffcore40e_survivors.csv", index=False)
    write_json(RUNTIME / "a7ffcore40e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE40E BOOK OBJECTIVE REPLAY EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE40E executes bounded book-objective replay over the CORE39E symbol-level sample packet. It does not run formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- packet_rows: `{manifest['packet_rows']}`",
        f"- book_replay_rows: `{manifest['book_replay_rows']}`",
        f"- survivor_count: `{manifest['survivor_count']}`",
        f"- survivor_family_count: `{manifest['survivor_family_count']}`",
        "",
        "## Objective Summary",
        "",
        md_table(objective_summary),
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
        md_table(candidate_summary),
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
