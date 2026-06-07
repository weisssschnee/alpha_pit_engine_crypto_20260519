from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260607"
STAGE = "A7LS-23"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="A7LS-23 strict candidate bias audit.")
    parser.add_argument(
        "--promotion",
        default=str(REPO / "runtime" / "a7ls22_clue_attribution_promotion_triage" / "a7ls22_promotion_triage.csv"),
    )
    parser.add_argument(
        "--candidate-review",
        default=str(REPO / "runtime" / "a7ls22_clue_attribution_promotion_triage" / "a7ls22_candidate_factor_review.csv"),
    )
    parser.add_argument(
        "--label-response",
        default=str(REPO / "runtime" / "a7ls21_company_deep_replay_aggregate" / "a7ls21_label_response_metrics_all.csv"),
    )
    parser.add_argument(
        "--out-dir",
        default=str(REPO / "runtime" / "a7ls23_strict_candidate_bias_audit"),
    )
    parser.add_argument(
        "--report",
        default=str(REPO / "reports" / f"CRYPTO_A7LS23_STRICT_CANDIDATE_BIAS_AUDIT_{DATE}.md"),
    )
    return parser.parse_args()


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def split_tokens(value: str) -> set[str]:
    if not isinstance(value, str) or not value:
        return set()
    return {x for x in value.split("|") if x}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def is_clue(decision: str) -> bool:
    decision = str(decision)
    return "NUMERIC_CLUE" in decision or "RANK_LABEL_DIAGNOSTIC_CLUE" in decision


def is_non_l7_numeric_clue(row: pd.Series) -> bool:
    return is_clue(row.get("decision", "")) and row.get("label_family") != "L7_ranked_future_return"


def audit_decision(row: pd.Series) -> tuple[str, str]:
    control = float(row["control_ratio_premay_max"])
    score = float(row["score_no_may"])
    cost10 = float(row["cost10_recent_oriented"])
    l5_selected = row["selected_label_family"] == "L5_vol_adjusted_return"
    non_l7_clues = int(row["non_l7_clue_rows_all_labels"])
    clue_label_families = int(row["non_l7_clue_label_family_count"])
    max_overlap = float(row["max_field_overlap_with_other_keep"])

    # This gate is intentionally practical. A candidate can move to a deeper
    # replay packet without becoming proof; weak spots become audit flags.
    if control < 0.75 and score >= 100 and cost10 > 0.05 and max_overlap < 0.80:
        return "PRIORITY_DEEP_BIAS_REPLAY", "Strong score, clean control margin, positive cost10, and not a near-duplicate."
    if control < 0.90 and score >= 25 and cost10 > 0 and non_l7_clues >= 1:
        if l5_selected and clue_label_families <= 1:
            return "SECONDARY_LABEL_TRANSFER_REPLAY", "Usable but label-transfer risk remains high."
        return "SECONDARY_DEEP_BIAS_REPLAY", "Usable secondary candidate for deeper replay."
    return "HOLD_BIAS_OR_MARGIN_WEAK", "Insufficient score/control/cost/label evidence for next replay packet."


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    report = Path(args.report)
    out_dir.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    promotion = pd.read_csv(args.promotion)
    review = pd.read_csv(args.candidate_review)
    labels = pd.read_csv(args.label_response)

    keep_ids = set(promotion["blueprint_id"].astype(str))
    labels_keep = labels[labels["blueprint_id"].astype(str).isin(keep_ids)].copy()
    labels_keep["is_clue"] = labels_keep["decision"].map(is_clue)
    labels_keep["is_non_l7_numeric_clue"] = labels_keep.apply(is_non_l7_numeric_clue, axis=1)
    if "score_no_may" not in labels_keep.columns:
        labels_keep["score_no_may"] = float("nan")
    if "cost10_recent_oriented" not in labels_keep.columns:
        labels_keep["cost10_recent_oriented"] = float("nan")

    label_summary = (
        labels_keep.groupby("blueprint_id")
        .agg(
            label_rows=("label_family", "size"),
            clue_rows_all_labels=("is_clue", "sum"),
            non_l7_clue_rows_all_labels=("is_non_l7_numeric_clue", "sum"),
            non_l7_clue_label_family_count=(
                "label_family",
                lambda s: labels_keep.loc[s.index][labels_keep.loc[s.index, "is_non_l7_numeric_clue"]][
                    "label_family"
                ].nunique(),
            ),
            clue_horizon_count=(
                "label_horizon_h",
                lambda s: labels_keep.loc[s.index][labels_keep.loc[s.index, "is_clue"]]["label_horizon_h"].nunique(),
            ),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_control_ratio=("control_ratio_premay_max", "max"),
            max_score_no_may=("score_no_may", "max"),
            max_cost10=("cost10_recent_oriented", "max"),
        )
        .reset_index()
    )
    label_summary.to_csv(out_dir / "a7ls23_label_transfer_audit.csv", index=False)

    base = promotion.copy()
    base = base.rename(columns={"label_family": "selected_label_family"})
    base = base.merge(label_summary, on="blueprint_id", how="left")
    for col in [
        "label_rows",
        "clue_rows_all_labels",
        "non_l7_clue_rows_all_labels",
        "non_l7_clue_label_family_count",
        "clue_horizon_count",
    ]:
        base[col] = base[col].fillna(0).astype(int)

    field_sets = {row["blueprint_id"]: split_tokens(row.get("field_tokens", "")) for _, row in base.iterrows()}
    overlap_rows = []
    for _, row in base.iterrows():
        bid = row["blueprint_id"]
        overlaps = []
        nearest = ""
        for other, fields in field_sets.items():
            if other == bid:
                continue
            sim = jaccard(field_sets[bid], fields)
            overlaps.append(sim)
            if sim == max(overlaps):
                nearest = other
        overlap_rows.append(
            {
                "blueprint_id": bid,
                "max_field_overlap_with_other_keep": max(overlaps) if overlaps else 0.0,
                "nearest_keep_by_field_overlap": nearest,
            }
        )
    overlap = pd.DataFrame(overlap_rows)
    overlap.to_csv(out_dir / "a7ls23_overlap_audit.csv", index=False)
    base = base.merge(overlap, on="blueprint_id", how="left")

    flags = []
    decisions = []
    reasons = []
    for _, row in base.iterrows():
        row_flags = []
        if row["selected_label_family"] == "L5_vol_adjusted_return":
            row_flags.append("selected_l5_vol_adjusted")
        if int(row["non_l7_clue_label_family_count"]) <= 1:
            row_flags.append("limited_label_transfer")
        if float(row["control_ratio_premay_max"]) >= 0.85:
            row_flags.append("thin_control_margin")
        if float(row["max_field_overlap_with_other_keep"]) >= 0.80:
            row_flags.append("near_duplicate_field_set")
        if "basis_premium" in str(row["semantic_pair"]):
            row_flags.append("basis_premium_dependent")
        decision, reason = audit_decision(row)
        flags.append("|".join(row_flags))
        decisions.append(decision)
        reasons.append(reason)
    base["bias_flags"] = flags
    base["a7ls23_decision"] = decisions
    base["a7ls23_reason"] = reasons
    base["authorizes_a7ls24_deep_replay"] = base["a7ls23_decision"].isin(
        ["PRIORITY_DEEP_BIAS_REPLAY", "SECONDARY_DEEP_BIAS_REPLAY", "SECONDARY_LABEL_TRANSFER_REPLAY"]
    )
    base["authorizes_alpha_proof"] = False
    base["authorizes_search"] = False

    decision_cols = [
        "blueprint_id",
        "a7ls23_decision",
        "a7ls23_reason",
        "authorizes_a7ls24_deep_replay",
        "bias_flags",
        "semantic_pair",
        "motif",
        "selected_label_family",
        "label_horizon_h",
        "score_no_may",
        "control_ratio_premay_max",
        "cost10_recent_oriented",
        "non_l7_clue_rows_all_labels",
        "non_l7_clue_label_family_count",
        "clue_horizon_count",
        "max_field_overlap_with_other_keep",
        "nearest_keep_by_field_overlap",
        "financial_principle",
        "chinese_explanation",
        "field_tokens",
        "operator_tokens",
        "expression",
    ]
    base[decision_cols].sort_values(
        ["authorizes_a7ls24_deep_replay", "score_no_may"], ascending=[False, False]
    ).to_csv(out_dir / "a7ls23_strict_candidate_bias_audit.csv", index=False)

    queue = base[base["authorizes_a7ls24_deep_replay"]].copy()
    queue[decision_cols].to_csv(out_dir / "a7ls23_a7ls24_deep_replay_queue.csv", index=False)

    summary = (
        base.groupby(["a7ls23_decision", "selected_label_family", "semantic_pair"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    summary.to_csv(out_dir / "a7ls23_decision_summary.csv", index=False)

    keep_count = int(len(base))
    replay_count = int(len(queue))
    priority_count = int((base["a7ls23_decision"] == "PRIORITY_DEEP_BIAS_REPLAY").sum())
    secondary_count = int(base["a7ls23_decision"].str.startswith("SECONDARY_").sum())
    l5_share = float((base["selected_label_family"] == "L5_vol_adjusted_return").mean()) if keep_count else 0.0
    unique_semantic = int(base["semantic_pair"].nunique())

    blockers = []
    if replay_count < 4:
        blockers.append("a7ls24_queue_lt_4")
    if unique_semantic < 4:
        blockers.append("semantic_pair_count_lt_4")

    decision = (
        "PASS_A7LS23_STRICT_BIAS_AUDIT_READY_FOR_A7LS24"
        if not blockers
        else "HOLD_A7LS23_STRICT_BIAS_AUDIT_QUEUE_INSUFFICIENT"
    )

    manifest = {
        "stage": STAGE,
        "decision": decision,
        "blockers": blockers,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "input_keep_review_count": keep_count,
        "a7ls24_deep_replay_queue_count": replay_count,
        "priority_deep_replay_count": priority_count,
        "secondary_deep_replay_count": secondary_count,
        "selected_l5_share": l5_share,
        "semantic_pair_count": unique_semantic,
        "uses_may": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_authorized": ["A7LS24 deep bias replay packet"] if not blockers else ["A7LS23R queue repair"],
    }
    write_json(out_dir / "a7ls23_manifest.json", manifest)
    write_json(
        out_dir / "a7ls23_authorization_matrix.json",
        {
            "authorized": manifest["next_authorized"],
            "not_authorized": ["formula search", "large search", "alpha proof", "shadow", "paper", "live"],
        },
    )

    report_lines = [
        f"# CRYPTO A7LS-23 Strict Candidate Bias Audit ({DATE})",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- input keep-review candidates: {keep_count}",
        f"- A7LS24 deep replay queue: {replay_count}",
        f"- priority deep replay: {priority_count}",
        f"- secondary deep replay: {secondary_count}",
        f"- selected L5 share: {l5_share:.2%}",
        f"- semantic pairs: {unique_semantic}",
        "",
        "## Interpretation",
        "",
        "The queue is usable for the next deep-bias replay packet. It is not proof. The strongest risk remains label concentration around L5 vol-adjusted return, so A7LS24 must test label transfer and portfolio contribution explicitly.",
        "",
        "## A7LS24 Queue",
        "",
    ]
    for _, row in queue.sort_values("score_no_may", ascending=False).iterrows():
        report_lines.extend(
            [
                f"### {row['blueprint_id']}",
                "",
                f"- decision: `{row['a7ls23_decision']}`",
                f"- semantic_pair: `{row['semantic_pair']}`",
                f"- selected label: `{row['selected_label_family']} / {row['label_horizon_h']}h`",
                f"- score_no_may: `{row['score_no_may']:.4f}`",
                f"- control_ratio_premay_max: `{row['control_ratio_premay_max']:.4f}`",
                f"- non_l7_clue_rows_all_labels: `{int(row['non_l7_clue_rows_all_labels'])}`",
                f"- flags: `{row['bias_flags']}`",
                f"- principle: {row['financial_principle']}",
                f"- expression: `{row['expression']}`",
                "",
            ]
        )
    report_lines.extend(
        [
            "## Boundaries",
            "",
            "- May is not used.",
            "- No search is executed or authorized.",
            "- A7LS24 is authorized only as a deeper replay/bias packet for this queue.",
            "- Alpha proof, shadow, paper, and live remain blocked.",
            "",
            "## Decision Counts",
            "",
            base["a7ls23_decision"].value_counts().rename_axis("decision").reset_index(name="count").to_markdown(index=False),
            "",
        ]
    )
    report.write_text("\n".join(report_lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
