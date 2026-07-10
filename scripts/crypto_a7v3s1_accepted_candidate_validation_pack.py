from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("runtime/a7v3s0_reward_sharded_720h_r2_aggregate_20260613")
DEFAULT_RUNTIME = Path("runtime/a7v3s1_accepted_candidate_validation_20260613")
DEFAULT_REPORT = Path("reports/CRYPTO_A7V3S1_ACCEPTED_CANDIDATE_VALIDATION_20260613.md")

STRUCTURAL_FIELDS = {
    "listing_age_days",
    "sqrt_listing_age_days",
    "log1p_listing_age_days",
    "age_percentile_active_universe",
    "active_universe_size",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def finite_float(value: object, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def split_reasons(value: object) -> list[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    return [part for part in text.split(";") if part]


def md_table(frame: pd.DataFrame, max_rows: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(max_rows).copy()
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def field_set(row: pd.Series) -> set[str]:
    fields = set()
    for col in ("primary_field", "secondary_field"):
        value = row.get(col)
        if isinstance(value, str) and value:
            fields.add(value)
    expression = str(row.get("expression", row.get("formula", "")))
    for name in STRUCTURAL_FIELDS:
        if re.search(rf"\b{re.escape(name)}\b", expression):
            fields.add(name)
    return fields


def review_row(row: pd.Series, duplicate_cluster_sizes: dict[str, int]) -> dict[str, object]:
    flags: list[str] = []
    required: list[str] = []
    fields = field_set(row)

    hard_reject = bool(row.get("hard_reject", False))
    gate_pass = bool(row.get("gate_pass", False))
    min_oos_floor = finite_float(row.get("min_oos_floor_sortino"))
    min_oos = finite_float(row.get("min_oos_sortino"))
    shuffle_ratio = finite_float(row.get("recent_shuffle_control_ratio"))
    matched_ratio = finite_float(row.get("recent_control_ratio"))
    recent_sortino = finite_float(row.get("recent_sortino"))
    stress_sortino = finite_float(row.get("stress_sortino"))
    stress_floor = finite_float(row.get("stress_floor_sortino"))

    if hard_reject:
        flags.append("hard_reject")
        flags.extend(split_reasons(row.get("hard_reject_reasons")))
    if not gate_pass:
        flags.append("gate_fail")
    if not math.isfinite(min_oos_floor) or min_oos_floor <= 0:
        flags.append("oos_nonoverlap_floor_not_positive")
    if not math.isfinite(min_oos) or min_oos <= 0:
        flags.append("oos_sortino_not_positive")
    if math.isfinite(shuffle_ratio) and shuffle_ratio >= 1:
        flags.append("shuffle_control_dominated_recent")
    if math.isfinite(matched_ratio) and matched_ratio >= 1:
        flags.append("matched_control_ratio_ge_1")
        required.append("matched-control and neutralization rerun")
    if STRUCTURAL_FIELDS & fields:
        flags.append("structural_listing_or_universe_state_dependency")
        required.append("PIT listing/universe membership audit")
    if str(row.get("candidate_role", "")) == "numeric_probe_only":
        flags.append("numeric_probe_only_not_factor")
        required.append("deep replay before factor promotion")
    skeleton_key = str(row.get("skeleton_key", ""))
    if duplicate_cluster_sizes.get(skeleton_key, 0) > 1:
        flags.append("same_skeleton_duplicate_cluster")
        required.append("formula family dedupe")
    if math.isfinite(stress_sortino) and stress_sortino <= 0:
        flags.append("stress_sortino_non_positive")
    if math.isfinite(stress_floor) and stress_floor <= 0:
        flags.append("stress_floor_non_positive")

    blocking = {
        "hard_reject",
        "gate_fail",
        "oos_nonoverlap_floor_not_positive",
        "oos_sortino_not_positive",
        "shuffle_control_dominated_recent",
    }
    if blocking & set(flags):
        decision = "REJECT_FROM_NEXT_VALIDATION"
    elif STRUCTURAL_FIELDS & fields:
        decision = "ADVANCE_PIT_AND_REGIME_VALIDATION"
    elif math.isfinite(matched_ratio) and matched_ratio >= 1:
        decision = "ADVANCE_CONTROL_NEUTRALIZATION_VALIDATION"
    else:
        decision = "ADVANCE_DEEP_REPLAY_VALIDATION"

    return {
        "blueprint_id": row.get("blueprint_id"),
        "production_key": row.get("production_key"),
        "semantic_pair": row.get("semantic_pair"),
        "motif": row.get("motif"),
        "skeleton_key": skeleton_key,
        "expression": row.get("expression", row.get("formula")),
        "horizon_h": row.get("horizon_h"),
        "primary_field": row.get("primary_field"),
        "secondary_field": row.get("secondary_field"),
        "recent_sortino": recent_sortino,
        "min_oos_sortino": min_oos,
        "min_oos_floor_sortino": min_oos_floor,
        "stress_sortino": stress_sortino,
        "stress_floor_sortino": stress_floor,
        "recent_sharpe": finite_float(row.get("recent_sharpe")),
        "recent_ic": finite_float(row.get("recent_ic")),
        "recent_rankic": finite_float(row.get("recent_rankic")),
        "recent_net_mean": finite_float(row.get("recent_net_mean")),
        "recent_avg_turnover": finite_float(row.get("recent_avg_turnover")),
        "recent_capacity_proxy": finite_float(row.get("recent_capacity_proxy")),
        "recent_control_ratio": matched_ratio,
        "recent_shuffle_control_ratio": shuffle_ratio,
        "objective_pass_count": row.get("objective_pass_count"),
        "pareto_rank": row.get("pareto_rank"),
        "candidate_role": row.get("candidate_role"),
        "review_flags": ";".join(dict.fromkeys(flags)),
        "required_validation": ";".join(dict.fromkeys(required)),
        "validation_decision": decision,
    }


def build_split_matrix(split_metrics_path: Path, accepted_ids: set[str]) -> pd.DataFrame:
    rows = []
    for chunk in pd.read_csv(split_metrics_path, chunksize=200_000):
        part = chunk[chunk["blueprint_id"].isin(accepted_ids)].copy()
        if not part.empty:
            rows.append(part)
    if not rows:
        return pd.DataFrame()
    keep = pd.concat(rows, ignore_index=True)
    cols = [
        "blueprint_id",
        "semantic_pair",
        "motif",
        "horizon_h",
        "variant",
        "split",
        "n_obs",
        "net_mean",
        "sharpe",
        "sortino",
        "nonoverlap_floor_sortino",
        "max_drawdown",
        "avg_turnover",
        "ic_mean",
        "rankic_mean",
    ]
    return keep[[col for col in cols if col in keep.columns]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    args.runtime.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    accepted = read_csv(args.input / "a7v3s0_reward_accepted_enriched.csv")
    unique = read_csv(args.input / "a7v3s0_reward_unique_blueprint_best.csv")

    duplicate_clusters = (
        accepted.groupby(["skeleton_key", "semantic_pair", "motif"], dropna=False)
        .agg(
            accepted_rows=("blueprint_id", "count"),
            unique_blueprints=("blueprint_id", "nunique"),
            expression_examples=("expression", lambda s: " || ".join(s.astype(str).head(3))),
        )
        .reset_index()
        .sort_values(["accepted_rows", "unique_blueprints"], ascending=False)
    )
    cluster_sizes = dict(zip(duplicate_clusters["skeleton_key"], duplicate_clusters["unique_blueprints"]))

    reviews = pd.DataFrame([review_row(row, cluster_sizes) for _, row in unique.iterrows()])
    family = (
        reviews.groupby(["semantic_pair", "motif", "validation_decision"], dropna=False)
        .agg(
            candidates=("blueprint_id", "count"),
            median_recent_sortino=("recent_sortino", "median"),
            median_min_oos_floor_sortino=("min_oos_floor_sortino", "median"),
            max_recent_sortino=("recent_sortino", "max"),
        )
        .reset_index()
        .sort_values(["candidates", "median_recent_sortino"], ascending=False)
    )
    flags = (
        reviews.assign(review_flags=reviews["review_flags"].fillna("").str.split(";"))
        .explode("review_flags")
        .query("review_flags != ''")
        .groupby("review_flags", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    queue = reviews[reviews["validation_decision"] != "REJECT_FROM_NEXT_VALIDATION"].copy()
    queue["priority_score"] = (
        queue["min_oos_floor_sortino"].fillna(-999)
        + 0.25 * queue["recent_sortino"].fillna(0)
        - 0.5 * queue["recent_shuffle_control_ratio"].fillna(1)
        - 0.25 * queue["recent_control_ratio"].fillna(1)
    )
    queue = queue.sort_values(["validation_decision", "priority_score"], ascending=[True, False])

    split_matrix = build_split_matrix(
        args.input / "a7v3s0_reward_split_metrics_all.csv",
        set(unique["blueprint_id"].astype(str)),
    )
    if not split_matrix.empty:
        split_summary = (
            split_matrix.groupby(["split", "variant"], dropna=False)
            .agg(
                rows=("blueprint_id", "count"),
                unique_blueprints=("blueprint_id", "nunique"),
                median_sortino=("sortino", "median"),
                min_floor_sortino=("nonoverlap_floor_sortino", "min"),
                median_ic=("ic_mean", "median"),
            )
            .reset_index()
        )
    else:
        split_summary = pd.DataFrame()

    outputs = {
        "candidate_review": args.runtime / "a7v3s1_candidate_review.csv",
        "duplicate_clusters": args.runtime / "a7v3s1_duplicate_cluster_audit.csv",
        "family_concentration": args.runtime / "a7v3s1_family_concentration.csv",
        "review_flag_summary": args.runtime / "a7v3s1_review_flag_summary.csv",
        "split_matrix": args.runtime / "a7v3s1_split_window_matrix.csv",
        "split_summary": args.runtime / "a7v3s1_split_window_summary.csv",
        "next_queue": args.runtime / "a7v3s1_next_deep_validation_queue.csv",
        "manifest": args.runtime / "a7v3s1_manifest.json",
    }
    reviews.to_csv(outputs["candidate_review"], index=False)
    duplicate_clusters.to_csv(outputs["duplicate_clusters"], index=False)
    family.to_csv(outputs["family_concentration"], index=False)
    flags.to_csv(outputs["review_flag_summary"], index=False)
    split_matrix.to_csv(outputs["split_matrix"], index=False)
    split_summary.to_csv(outputs["split_summary"], index=False)
    queue.to_csv(outputs["next_queue"], index=False)

    decision_counts = reviews["validation_decision"].value_counts().rename_axis("decision").reset_index(name="count")
    manifest = {
        "stage": "A7V3S1-ACCEPTED-CANDIDATE-VALIDATION",
        "generated_at": now_utc(),
        "input": str(args.input),
        "runtime": str(args.runtime),
        "report": str(args.report),
        "accepted_rows": int(len(accepted)),
        "unique_blueprints": int(len(unique)),
        "next_deep_validation_count": int(len(queue)),
        "rejected_from_next_validation_count": int((reviews["validation_decision"] == "REJECT_FROM_NEXT_VALIDATION").sum()),
        "decision_counts": dict(zip(decision_counts["decision"], decision_counts["count"].astype(int))),
        "review_flag_counts": dict(zip(flags["review_flags"], flags["count"].astype(int))) if not flags.empty else {},
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_deep_validation": True,
        "outputs": {key: str(value) for key, value in outputs.items()},
    }
    outputs["manifest"].write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    report = [
        "# CRYPTO A7V3S1 Accepted Candidate Validation Pack",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        "`PASS_A7V3S1_VALIDATION_PACK_BUILT`",
        "",
        "This is a validation handoff for reward-accepted numeric probes. It is not alpha proof and does not authorize shadow, paper, or live trading.",
        "",
        "## Counts",
        "",
        f"- accepted reward rows: `{len(accepted)}`",
        f"- unique accepted blueprints: `{len(unique)}`",
        f"- next deep validation queue: `{len(queue)}`",
        f"- rejected from next validation: `{manifest['rejected_from_next_validation_count']}`",
        "",
        "## Validation Decisions",
        "",
        md_table(decision_counts),
        "",
        "## Review Flags",
        "",
        md_table(flags),
        "",
        "## Family Concentration",
        "",
        md_table(family),
        "",
        "## Top Deep Validation Queue",
        "",
        md_table(
            queue[
                [
                    "validation_decision",
                    "semantic_pair",
                    "motif",
                    "horizon_h",
                    "recent_sortino",
                    "min_oos_floor_sortino",
                    "stress_sortino",
                    "recent_control_ratio",
                    "recent_shuffle_control_ratio",
                    "required_validation",
                    "expression",
                ]
            ],
            max_rows=20,
        ),
        "",
        "## Bias-Audit Notes",
        "",
        "- `numeric_probe_only_not_factor` means reward passed a numeric probe but the candidate is not a promoted factor.",
        "- `structural_listing_or_universe_state_dependency` means the candidate depends on listing age or active-universe state and needs PIT membership/listing audit before any promotion discussion.",
        "- `matched_control_ratio_ge_1` means matched control is as strong or stronger on the recent slice and requires neutralized/control replay.",
        "- Same-skeleton clusters are not independent discoveries; they require family dedupe before queue expansion.",
        "",
        "## Outputs",
        "",
    ]
    for key, value in outputs.items():
        report.append(f"- `{key}`: `{value}`")
    args.report.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
