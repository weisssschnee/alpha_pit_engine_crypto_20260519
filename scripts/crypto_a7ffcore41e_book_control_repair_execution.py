from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore41e_book_control_repair_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE41E_BOOK_CONTROL_REPAIR_EXECUTION_20260602.md"
CORE41 = REPO / "runtime" / "a7ffcore41_book_control_repair_contract" / "a7ffcore41_manifest.json"
ALL_VARIANTS = REPO / "runtime" / "a7ffcore40e_book_objective_replay_execution" / "a7ffcore40e_book_replay_all_variants.csv"


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
    source = read_json(CORE41)
    if source.get("decision") != "PASS_A7FFCORE41_BOOK_CONTROL_REPAIR_CONTRACT_READY_FOR_CORE41E":
        raise SystemExit(f"CORE41 not ready for CORE41E: {source.get('decision')}")

    variants = pd.read_csv(ALL_VARIANTS)
    key = ["candidate_id", "family_id", "objective_id", "horizon_h", "split"]
    wide = variants.pivot_table(index=key, columns="control_variant", values="net_book_return", aggfunc="first").reset_index()
    for col in ["original", "sign_flip", "stale"]:
        if col not in wide.columns:
            wide[col] = pd.NA
    train = wide[wide["split"].eq("train_2024")].copy()
    orient = train[["candidate_id", "objective_id", "horizon_h", "original", "sign_flip"]].copy()
    orient["chosen_variant"] = "original"
    orient.loc[orient["sign_flip"].fillna(-1e99).gt(orient["original"].fillna(-1e99)), "chosen_variant"] = "sign_flip"
    orient = orient[["candidate_id", "objective_id", "horizon_h", "chosen_variant"]].drop_duplicates()
    repaired = wide.merge(orient, on=["candidate_id", "objective_id", "horizon_h"], how="left")
    repaired["chosen_variant"] = repaired["chosen_variant"].fillna("original")
    repaired["repaired_net_book_return"] = repaired.apply(
        lambda r: r["sign_flip"] if r["chosen_variant"] == "sign_flip" else r["original"], axis=1
    )
    repaired["opposite_control"] = repaired.apply(
        lambda r: r["original"] if r["chosen_variant"] == "sign_flip" else r["sign_flip"], axis=1
    )
    repaired["max_abs_control_net"] = repaired[["opposite_control", "stale"]].abs().max(axis=1)
    repaired["repaired_control_ratio"] = repaired["max_abs_control_net"] / (repaired["repaired_net_book_return"].abs() + 1e-12)
    repaired["repaired_positive"] = repaired["repaired_net_book_return"].gt(0)
    repaired["repaired_control_clean"] = repaired["repaired_control_ratio"].lt(1.0)
    repaired["repaired_split_pass"] = repaired["repaired_positive"] & repaired["repaired_control_clean"]
    split_summary = (
        repaired.groupby(["candidate_id", "family_id", "split"], as_index=False)
        .agg(
            split_pass_count=("repaired_split_pass", bool_sum),
            median_repaired_net_book_return=("repaired_net_book_return", "median"),
            median_repaired_control_ratio=("repaired_control_ratio", "median"),
            chosen_sign_flip_count=("chosen_variant", lambda s: int((s == "sign_flip").sum())),
        )
    )
    train_summary = split_summary[split_summary["split"].eq("train_2024")][
        ["candidate_id", "split_pass_count", "median_repaired_net_book_return", "median_repaired_control_ratio"]
    ].rename(
        columns={
            "split_pass_count": "train_pass_count",
            "median_repaired_net_book_return": "train_median_repaired_net_book_return",
            "median_repaired_control_ratio": "train_median_repaired_control_ratio",
        }
    )
    oos = split_summary[~split_summary["split"].eq("train_2024")]
    oos_summary = (
        oos.groupby("candidate_id", as_index=False)
        .agg(
            oos_split_count=("split", "nunique"),
            oos_positive_split_count=("median_repaired_net_book_return", lambda s: int((s > 0).sum())),
            oos_control_clean_split_count=("median_repaired_control_ratio", lambda s: int((s < 1).sum())),
            oos_min_repaired_net_book_return=("median_repaired_net_book_return", "min"),
            oos_worst_repaired_control_ratio=("median_repaired_control_ratio", "max"),
        )
    )
    meta = repaired[["candidate_id", "family_id"]].drop_duplicates()
    candidate_summary = meta.merge(train_summary, on="candidate_id", how="left").merge(oos_summary, on="candidate_id", how="left")
    orientation_summary = (
        repaired.groupby(["candidate_id", "family_id", "chosen_variant"], as_index=False)
        .agg(row_count=("candidate_id", "count"))
        .sort_values(["candidate_id", "chosen_variant"])
    )
    candidate_summary["repair_survivor"] = (
        candidate_summary["train_median_repaired_net_book_return"].fillna(-1).gt(0)
        & candidate_summary["train_median_repaired_control_ratio"].fillna(99).lt(1.0)
        & candidate_summary["oos_positive_split_count"].fillna(0).ge(2)
        & candidate_summary["oos_control_clean_split_count"].fillna(0).ge(2)
    )
    survivors = candidate_summary[candidate_summary["repair_survivor"]].copy()
    family_summary = (
        candidate_summary.groupby("family_id", as_index=False)
        .agg(
            candidate_count=("candidate_id", "count"),
            survivor_count=("repair_survivor", bool_sum),
            median_train_net=("train_median_repaired_net_book_return", "median"),
            median_train_control_ratio=("train_median_repaired_control_ratio", "median"),
            median_oos_min_net=("oos_min_repaired_net_book_return", "median"),
            median_oos_worst_control_ratio=("oos_worst_repaired_control_ratio", "median"),
        )
    )
    survivor_family_count = int(survivors["family_id"].nunique()) if not survivors.empty else 0
    decision = (
        "PASS_A7FFCORE41E_BOOK_CONTROL_REPAIR_SURVIVORS_READY_FOR_CORE42_ARBITRATION"
        if survivors.shape[0] >= 4 and survivor_family_count >= 2
        else "HOLD_A7FFCORE41E_BOOK_CONTROL_REPAIR_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE41E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE41",
        "source_decision": source.get("decision"),
        "decision": decision,
        "candidate_count": int(candidate_summary.shape[0]),
        "survivor_count": int(survivors.shape[0]),
        "survivor_family_count": survivor_family_count,
        "executes_replay_repair": True,
        "executes_search": False,
        "authorizes_core42_arbitration": decision.startswith("PASS_"),
        "authorizes_core41er_forensic": not decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE42 book control repair arbitration" if decision.startswith("PASS_") else "A7FF-CORE41ER book control repair forensic",
    }
    repaired.to_csv(RUNTIME / "a7ffcore41e_repaired_book_rows.csv", index=False)
    split_summary.to_csv(RUNTIME / "a7ffcore41e_split_summary.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore41e_candidate_summary.csv", index=False)
    orientation_summary.to_csv(RUNTIME / "a7ffcore41e_orientation_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore41e_family_summary.csv", index=False)
    survivors.to_csv(RUNTIME / "a7ffcore41e_survivors.csv", index=False)
    write_json(RUNTIME / "a7ffcore41e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE41E BOOK CONTROL REPAIR EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE41E applies train-only orientation and control repair over existing CORE40E book replay variants. It does not run generation, formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- candidate_count: `{manifest['candidate_count']}`",
        f"- survivor_count: `{manifest['survivor_count']}`",
        f"- survivor_family_count: `{manifest['survivor_family_count']}`",
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Survivors",
        "",
        md_table(survivors),
        "",
        "## Candidate Summary",
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
