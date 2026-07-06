from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7ff8_expanded_numeric_probe import expression_fields  # noqa: E402
from scripts.crypto_a7v3s0_next_large_search_contract import FIELD_SPECS  # noqa: E402


DEFAULT_REWARD_AGG = REPO / "runtime" / "a7search7_strict_validation_reward_source5_py_aggregate_20260706"
DEFAULT_SOURCE_AGG = REPO / "runtime" / "a7source5_a7search7_source_lag_retest_py_aggregate_20260706"
DEFAULT_RUNTIME = REPO / "runtime" / "a7source5_accepted_forensic_pack_20260706"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SOURCE5_ACCEPTED_FORENSIC_PACK_20260706.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except EmptyDataError:
        return pd.DataFrame()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def md_table(frame: pd.DataFrame, max_rows: int = 30) -> str:
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


def short_hash(text: str, n: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def compact_expr(expr: Any) -> str:
    return re.sub(r"\s+", "", str(expr or ""))


def canonical_ast(expr: Any) -> str:
    text = compact_expr(expr)
    for field in sorted(FIELD_SPECS, key=len, reverse=True):
        text = text.replace(field, "FIELD")
    return re.sub(r"\b\d+\b", "W", text)


def field_semantic(field: str) -> str:
    return str(FIELD_SPECS.get(field, {}).get("semantic", "unknown"))


def summarize(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if frame.empty or not all(key in frame.columns for key in keys):
        return pd.DataFrame(columns=[*keys, "count", "share"])
    out = frame.groupby(keys, dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    total = max(1, int(out["count"].sum()))
    out["share"] = out["count"] / total
    return out


def accepted_field_usage(accepted: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in accepted.iterrows():
        expr = row.get("formula", row.get("expression", ""))
        for field in expression_fields(str(expr)):
            rows.append(
                {
                    "blueprint_id": row.get("blueprint_id", ""),
                    "horizon_h": row.get("horizon_h", ""),
                    "field": field,
                    "semantic": field_semantic(field),
                    "expression": expr,
                }
            )
    if not rows:
        return pd.DataFrame(columns=["field", "semantic", "formula_count", "blueprint_count"])
    frame = pd.DataFrame(rows)
    return (
        frame.groupby(["field", "semantic"], dropna=False)
        .agg(formula_count=("expression", "count"), blueprint_count=("blueprint_id", "nunique"))
        .reset_index()
        .sort_values(["blueprint_count", "formula_count"], ascending=False)
    )


def accepted_skeletons(accepted: pd.DataFrame) -> pd.DataFrame:
    if accepted.empty:
        return pd.DataFrame()
    out = accepted.copy()
    out["formula_compact"] = out["formula"].map(compact_expr)
    out["formula_hash"] = out["formula_compact"].map(short_hash)
    out["canonical_skeleton"] = out["formula"].map(canonical_ast)
    out["skeleton_hash"] = out["canonical_skeleton"].map(short_hash)
    return out[
        [
            col
            for col in [
                "blueprint_id",
                "horizon_h",
                "semantic_pair",
                "motif",
                "formula_hash",
                "skeleton_hash",
                "canonical_skeleton",
                "formula",
                "train_sortino",
                "validation_sortino",
                "test_sortino",
                "recent_sortino",
                "min_oos_floor_sortino",
                "stress_sortino",
                "stress_floor_sortino",
                "recent_shuffle_control_ratio",
            ]
            if col in out.columns
        ]
    ]


def source_lag_join(accepted: pd.DataFrame, source_summary: pd.DataFrame) -> pd.DataFrame:
    if accepted.empty or source_summary.empty:
        return pd.DataFrame()
    left = accepted.copy()
    left["formula_key"] = left["formula"].map(compact_expr)
    left["horizon_key"] = left["horizon_h"].astype(str)
    right = source_summary.copy()
    if "formula" not in right.columns:
        return pd.DataFrame()
    right["formula_key"] = right["formula"].map(compact_expr)
    right["horizon_key"] = right["horizon_h"].astype(str)
    keep = [
        col
        for col in [
            "formula_key",
            "horizon_key",
            "source_lag_gate",
            "sortino_original",
            "sortino_source_lag_1h",
            "sortino_source_lag_2h",
            "sortino_source_lag_4h",
            "nonoverlap_floor_sortino_original",
            "nonoverlap_floor_sortino_source_lag_1h",
            "nonoverlap_floor_sortino_source_lag_2h",
            "nonoverlap_floor_sortino_source_lag_4h",
            "floor_retention_source_lag_1h",
            "floor_retention_source_lag_2h",
            "floor_retention_source_lag_4h",
        ]
        if col in right.columns
    ]
    merged = left.merge(right[keep].drop_duplicates(["formula_key", "horizon_key"]), on=["formula_key", "horizon_key"], how="left")
    return merged


def split_details(accepted: pd.DataFrame, split_metrics: pd.DataFrame) -> pd.DataFrame:
    if accepted.empty or split_metrics.empty or "blueprint_id" not in split_metrics.columns:
        return pd.DataFrame()
    ids = set(accepted["blueprint_id"].astype(str))
    out = split_metrics[split_metrics["blueprint_id"].astype(str).isin(ids)].copy()
    order = [
        "blueprint_id",
        "horizon_h",
        "variant",
        "split",
        "sortino",
        "sharpe",
        "rankic_mean",
        "net_mean",
        "nonoverlap_floor_sortino",
        "n_obs",
        "avg_turnover",
        "max_drawdown",
    ]
    return out[[col for col in order if col in out.columns] + [col for col in out.columns if col not in order]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reward-aggregate", type=Path, default=DEFAULT_REWARD_AGG)
    parser.add_argument("--source-aggregate", type=Path, default=DEFAULT_SOURCE_AGG)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    runtime = args.runtime
    runtime.mkdir(parents=True, exist_ok=True)

    accepted = read_csv(args.reward_aggregate / "a7v3s0_reward_unique_blueprint_best.csv")
    accepted_all = read_csv(args.reward_aggregate / "a7v3s0_reward_accepted_enriched.csv")
    rejections = read_csv(args.reward_aggregate / "a7v3s0_reward_rejection_reason_summary.csv")
    rewards = read_csv(args.reward_aggregate / "a7v3s0_reward_candidate_leaderboard_all.csv")
    split_metrics = read_csv(args.reward_aggregate / "a7v3s0_reward_split_metrics_all.csv")
    reward_manifest = read_json(args.reward_aggregate / "a7v3s0_reward_sharded_aggregate_manifest.json")
    source_summary = read_csv(args.source_aggregate / "a7source5_source_lag_summary.csv")
    source_manifest = read_json(args.source_aggregate / "a7source5_manifest.json")

    if "formula" not in accepted.columns and "expression" in accepted.columns:
        accepted["formula"] = accepted["expression"]
    if "formula" not in accepted_all.columns and "expression" in accepted_all.columns:
        accepted_all["formula"] = accepted_all["expression"]

    fields = accepted_field_usage(accepted)
    skeletons = accepted_skeletons(accepted)
    source_join = source_lag_join(accepted, source_summary)
    splits = split_details(accepted, split_metrics)
    pair_summary = summarize(accepted, ["semantic_pair"])
    motif_summary = summarize(accepted, ["motif"])
    horizon_summary = summarize(accepted, ["horizon_h"])
    skeleton_summary = summarize(skeletons, ["skeleton_hash", "canonical_skeleton"])
    semantic_field_summary = summarize(fields, ["semantic"])

    outputs = {
        "accepted": runtime / "a7source5_accepted_candidates.csv",
        "accepted_all": runtime / "a7source5_accepted_all_rows.csv",
        "field_usage": runtime / "a7source5_accepted_field_usage.csv",
        "skeletons": runtime / "a7source5_accepted_skeletons.csv",
        "source_lag_join": runtime / "a7source5_accepted_source_lag_join.csv",
        "split_metrics": runtime / "a7source5_accepted_split_metrics.csv",
        "pair_summary": runtime / "a7source5_accepted_pair_summary.csv",
        "motif_summary": runtime / "a7source5_accepted_motif_summary.csv",
        "horizon_summary": runtime / "a7source5_accepted_horizon_summary.csv",
        "skeleton_summary": runtime / "a7source5_accepted_skeleton_summary.csv",
        "semantic_field_summary": runtime / "a7source5_accepted_semantic_field_summary.csv",
        "rejection_reasons": runtime / "a7source5_context_rejection_reason_summary.csv",
    }
    accepted.to_csv(outputs["accepted"], index=False)
    accepted_all.to_csv(outputs["accepted_all"], index=False)
    fields.to_csv(outputs["field_usage"], index=False)
    skeletons.to_csv(outputs["skeletons"], index=False)
    source_join.to_csv(outputs["source_lag_join"], index=False)
    splits.to_csv(outputs["split_metrics"], index=False)
    pair_summary.to_csv(outputs["pair_summary"], index=False)
    motif_summary.to_csv(outputs["motif_summary"], index=False)
    horizon_summary.to_csv(outputs["horizon_summary"], index=False)
    skeleton_summary.to_csv(outputs["skeleton_summary"], index=False)
    semantic_field_summary.to_csv(outputs["semantic_field_summary"], index=False)
    rejections.to_csv(outputs["rejection_reasons"], index=False)

    accepted_rows = int(accepted.shape[0])
    unique_blueprints = int(accepted["blueprint_id"].nunique()) if "blueprint_id" in accepted else accepted_rows
    top_pair_share = float(pair_summary["share"].iloc[0]) if not pair_summary.empty else 0.0
    top_field_semantic_share = float(semantic_field_summary["share"].iloc[0]) if not semantic_field_summary.empty else 0.0
    top_skeleton_share = float(skeleton_summary["share"].iloc[0]) if not skeleton_summary.empty else 0.0
    source_pass_rows = int(source_manifest.get("source_lag_pass_count", 0) or 0)
    reward_rows = int(reward_manifest.get("reward_rows", rewards.shape[0]) or 0)
    accepted_rate = accepted_rows / reward_rows if reward_rows else 0.0
    narrow_flags = []
    if top_pair_share > 0.50:
        narrow_flags.append("top_semantic_pair_share_above_50pct")
    if top_field_semantic_share > 0.50:
        narrow_flags.append("top_field_semantic_share_above_50pct")
    if top_skeleton_share > 0.50:
        narrow_flags.append("top_skeleton_share_above_50pct")
    decision = (
        "PASS_A7SOURCE5_ACCEPTED_FORENSIC_PACK_BUILT_NARROW_SURVIVOR_SET"
        if accepted_rows > 0
        else "HOLD_A7SOURCE5_ACCEPTED_FORENSIC_NO_ACCEPTED_ROWS"
    )

    manifest = {
        "stage": "A7SOURCE5-ACCEPTED-FORENSIC-PACK",
        "generated_at": now_utc(),
        "decision": decision,
        "runtime": str(runtime),
        "runtime_relative": repo_relative(runtime),
        "report": str(args.report),
        "report_relative": repo_relative(args.report),
        "reward_aggregate": str(args.reward_aggregate),
        "reward_aggregate_relative": repo_relative(args.reward_aggregate),
        "source_aggregate": str(args.source_aggregate),
        "source_aggregate_relative": repo_relative(args.source_aggregate),
        "accepted_rows": accepted_rows,
        "accepted_unique_blueprints": unique_blueprints,
        "reward_rows": reward_rows,
        "accepted_rate": accepted_rate,
        "source_lag_pass_rows": source_pass_rows,
        "top_pair_share": top_pair_share,
        "top_field_semantic_share": top_field_semantic_share,
        "top_skeleton_share": top_skeleton_share,
        "narrow_flags": narrow_flags,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_next_validation_pack": accepted_rows > 0,
        "outputs": {key: str(path) for key, path in outputs.items()},
        "outputs_relative": {key: repo_relative(path) for key, path in outputs.items()},
    }
    write_json(runtime / "a7source5_accepted_forensic_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SOURCE5 Accepted Forensic Pack",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Counts",
        "",
        f"- accepted_rows: `{accepted_rows}`",
        f"- accepted_unique_blueprints: `{unique_blueprints}`",
        f"- reward_rows: `{reward_rows}`",
        f"- accepted_rate: `{accepted_rate:.6f}`",
        f"- source_lag_pass_rows: `{source_pass_rows}`",
        f"- top_pair_share: `{top_pair_share:.3f}`",
        f"- top_field_semantic_share: `{top_field_semantic_share:.3f}`",
        f"- top_skeleton_share: `{top_skeleton_share:.3f}`",
        f"- narrow_flags: `{';'.join(narrow_flags) or 'none'}`",
        "",
        "## Accepted Candidates",
        "",
        md_table(
            accepted[
                [
                    col
                    for col in [
                        "blueprint_id",
                        "semantic_pair",
                        "motif",
                        "horizon_h",
                        "formula",
                        "train_sortino",
                        "validation_sortino",
                        "test_sortino",
                        "recent_sortino",
                        "min_oos_floor_sortino",
                        "stress_sortino",
                        "stress_floor_sortino",
                        "recent_shuffle_control_ratio",
                        "source_lag_gate",
                    ]
                    if col in accepted.columns
                ]
            ],
            20,
        ),
        "",
        "## Field Usage",
        "",
        md_table(fields, 30),
        "",
        "## Semantic Pair Summary",
        "",
        md_table(pair_summary, 20),
        "",
        "## Motif Summary",
        "",
        md_table(motif_summary, 20),
        "",
        "## Source Lag Join",
        "",
        md_table(
            source_join[
                [
                    col
                    for col in [
                        "blueprint_id",
                        "horizon_h",
                        "source_lag_gate",
                        "sortino_original",
                        "sortino_source_lag_1h",
                        "sortino_source_lag_2h",
                        "sortino_source_lag_4h",
                        "nonoverlap_floor_sortino_original",
                        "nonoverlap_floor_sortino_source_lag_1h",
                        "nonoverlap_floor_sortino_source_lag_2h",
                    ]
                    if col in source_join.columns
                ]
            ],
            20,
        ),
        "",
        "## Rejection Context",
        "",
        md_table(rejections, 20),
        "",
        "## Boundary",
        "",
        "This pack is forensic validation evidence only. It does not authorize alpha proof, shadow, paper, or live.",
        "",
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
