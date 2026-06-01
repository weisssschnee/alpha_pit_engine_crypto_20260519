from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from crypto_a7ffcore30e_bounded_numeric_probe import load_dataset
from crypto_a7ffcore39e_symbol_level_book_packet_audit import attach_symbol_labels
from crypto_a7ffcore44e_orthogonal_score_packet_construction import build_book_packet


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore45e_orthogonal_book_replay_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE45E_ORTHOGONAL_BOOK_REPLAY_EXECUTION_20260602.md"
CORE45 = REPO / "runtime" / "a7ffcore45_orthogonal_book_replay_contract" / "a7ffcore45_manifest.json"
CORE43E = REPO / "runtime" / "a7ffcore43e_control_vector_rebuild_audit" / "a7ffcore43e_manifest.json"
OBJECTIVES = REPO / "runtime" / "a7ffcore45_orthogonal_book_replay_contract" / "a7ffcore45_replay_objectives.csv"
HORIZONS = REPO / "runtime" / "a7ffcore45_orthogonal_book_replay_contract" / "a7ffcore45_horizon_policy.csv"


CONTROL_SCORE_COLUMNS = {
    "original": "candidate_score_original",
    "stale": "candidate_score_stale",
    "sign_flip": "candidate_score_sign_flip",
    "shuffle_time": "candidate_score_shuffle_time",
    "shuffle_symbol": "candidate_score_shuffle_symbol",
    "residual_null": "residual_score_null_orthogonal",
}


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


def build_variant_packet(vectors: pd.DataFrame, variant: str, score_col: str) -> pd.DataFrame:
    renamed = vectors.copy()
    renamed["residual_score_null_orthogonal"] = pd.to_numeric(renamed[score_col], errors="coerce").astype("float32")
    packet = build_book_packet(renamed)
    packet["score_variant"] = variant
    return packet


def labels_for_dataset(dataset_name: str, timestamps: pd.Series, horizons: list[int]) -> pd.DataFrame:
    quote_col = "trade_quote_volume" if dataset_name == "top498_replay_v2" else "agg_notional"
    df = load_dataset(dataset_name, {quote_col})
    needed_ts = pd.Index(pd.to_datetime(timestamps, utc=True).dropna().unique())
    rows: list[pd.DataFrame] = []
    for horizon in horizons:
        labels = attach_symbol_labels(df, horizon, quote_col)
        frame = df.loc[df["timestamp"].isin(needed_ts), ["symbol", "timestamp"]].copy()
        frame["horizon_h"] = horizon
        for col in [
            "forward_return",
            "cs_relative_return",
            "market_beta_residual_return",
            "liquidity_tier_relative_return",
            "vol_adjusted_return",
        ]:
            frame[col] = labels.loc[frame.index, col].to_numpy(dtype="float32")
        rows.append(frame)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE45)
    if source.get("decision") != "PASS_A7FFCORE45_ORTHOGONAL_BOOK_REPLAY_CONTRACT_READY_FOR_CORE45E":
        raise SystemExit(f"CORE45 not ready for CORE45E: {source.get('decision')}")
    vector_source = read_json(CORE43E)
    vector_path = Path(str(vector_source.get("external_sample_path", "")))
    if not vector_path.exists():
        raise SystemExit(f"CORE43E vector sample missing: {vector_path}")

    vectors = pd.read_parquet(vector_path)
    objectives = pd.read_csv(OBJECTIVES)
    horizons = sorted(pd.read_csv(HORIZONS)["horizon_h"].astype(int).unique().tolist())
    packet_variants = [build_variant_packet(vectors, variant, col) for variant, col in CONTROL_SCORE_COLUMNS.items()]
    packet = pd.concat(packet_variants, ignore_index=True) if packet_variants else pd.DataFrame()

    labels = []
    for dataset_name, sub in packet.groupby("dataset", sort=True):
        labels.append(labels_for_dataset(dataset_name, sub["timestamp"], horizons))
    label_frame = pd.concat(labels, ignore_index=True) if labels else pd.DataFrame()
    replay_input = packet.merge(label_frame, on=["symbol", "timestamp"], how="left")
    objective_rows: list[pd.DataFrame] = []
    for _, objective in objectives.iterrows():
        label_col = str(objective["label_column"])
        work = replay_input.copy()
        work["objective_id"] = objective["objective_id"]
        work["label_column"] = label_col
        work["weighted_return"] = work["book_weight"] * pd.to_numeric(work[label_col], errors="coerce")
        work["cost"] = work["book_weight"].abs() * 5.0 / 10000.0
        objective_rows.append(work)
    obj = pd.concat(objective_rows, ignore_index=True) if objective_rows else pd.DataFrame()
    group_cols = ["candidate_id", "family_id", "objective_id", "horizon_h", "split", "score_variant"]
    aggregate = (
        obj.groupby(group_cols, as_index=False)
        .agg(
            book_return=("weighted_return", "sum"),
            book_cost=("cost", "sum"),
            row_count=("symbol", "count"),
            timestamp_count=("timestamp", "nunique"),
            gross_weight=("book_weight", lambda s: float(np.nansum(np.abs(s)))),
        )
    )
    aggregate["net_book_return"] = aggregate["book_return"] - aggregate["book_cost"]
    primary = aggregate[aggregate["score_variant"].eq("residual_null")].copy()
    controls = (
        aggregate[~aggregate["score_variant"].eq("residual_null")]
        .groupby(["candidate_id", "objective_id", "horizon_h", "split"], as_index=False)
        .agg(max_abs_control_net=("net_book_return", lambda s: float(np.nanmax(np.abs(s))) if len(s) else np.nan))
    )
    replay = primary.merge(controls, on=["candidate_id", "objective_id", "horizon_h", "split"], how="left")
    replay["control_ratio"] = replay["max_abs_control_net"].abs() / (replay["net_book_return"].abs() + 1e-12)
    replay["positive_net"] = replay["net_book_return"].gt(0)
    replay["control_clean"] = replay["control_ratio"].lt(1.0)
    replay["split_pass"] = replay["positive_net"] & replay["control_clean"]

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
    candidate_summary = (
        replay.groupby(["candidate_id", "family_id"], as_index=False)
        .agg(
            replay_rows=("candidate_id", "count"),
            positive_rows=("positive_net", bool_sum),
            control_clean_rows=("control_clean", bool_sum),
            split_pass_rows=("split_pass", bool_sum),
            median_net_book_return=("net_book_return", "median"),
            median_control_ratio=("control_ratio", "median"),
        )
        .merge(train, on="candidate_id", how="left")
        .merge(oos_summary, on="candidate_id", how="left")
    )
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
        "PASS_A7FFCORE45E_ORTHOGONAL_BOOK_SURVIVORS_READY_FOR_CORE46_ARBITRATION"
        if survivors.shape[0] >= 4 and survivor_family_count >= 2
        else "HOLD_A7FFCORE45E_ORTHOGONAL_BOOK_REPLAY_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE45E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE45",
        "source_decision": source.get("decision"),
        "decision": decision,
        "vector_rows": int(vectors.shape[0]),
        "packet_variant_rows": int(packet.shape[0]),
        "book_replay_rows": int(replay.shape[0]),
        "survivor_count": int(survivors.shape[0]),
        "survivor_family_count": survivor_family_count,
        "executes_replay": True,
        "executes_search": False,
        "authorizes_core46_arbitration": decision.startswith("PASS_"),
        "authorizes_core45r_forensic": not decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE46 orthogonal book survivor arbitration"
        if decision.startswith("PASS_")
        else "A7FF-CORE45R orthogonal book replay forensic",
    }
    aggregate.to_csv(RUNTIME / "a7ffcore45e_book_replay_all_variants.csv", index=False)
    replay.to_csv(RUNTIME / "a7ffcore45e_residual_vs_controls.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore45e_candidate_summary.csv", index=False)
    split_balance.to_csv(RUNTIME / "a7ffcore45e_split_balance.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore45e_family_summary.csv", index=False)
    objective_summary.to_csv(RUNTIME / "a7ffcore45e_objective_summary.csv", index=False)
    survivors.to_csv(RUNTIME / "a7ffcore45e_survivors.csv", index=False)
    write_json(RUNTIME / "a7ffcore45e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE45E ORTHOGONAL BOOK REPLAY EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE45E executes bounded book replay over CORE43E/CORE44E orthogonal score inputs. It does not run formula generation, formula search, large search, alpha proof, shadow, paper, live, or promotion.",
        "",
        "## Summary",
        "",
        f"- vector_rows: `{manifest['vector_rows']}`",
        f"- packet_variant_rows: `{manifest['packet_variant_rows']}`",
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
