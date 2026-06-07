from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260607"
STAGE = "A7LS-24"

QUEUE = REPO / "runtime" / "a7ls23_strict_candidate_bias_audit" / "a7ls23_a7ls24_deep_replay_queue.csv"
LABELS = REPO / "runtime" / "a7ls21_company_deep_replay_aggregate" / "a7ls21_label_response_metrics_all.csv"
OUT_DIR = REPO / "runtime" / "a7ls24_label_transfer_deep_bias_replay"
REPORT = REPO / "reports" / f"CRYPTO_A7LS24_LABEL_TRANSFER_DEEP_BIAS_REPLAY_{DATE}.md"

L5 = "L5_vol_adjusted_return"
L7 = "L7_ranked_future_return"


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def clue_mask(df: pd.DataFrame) -> pd.Series:
    return df["decision"].astype(str).str.contains("NUMERIC_CLUE|RANK_LABEL_DIAGNOSTIC_CLUE", regex=True, na=False)


def transfer_decision(row: pd.Series) -> tuple[str, str, bool]:
    non_l5_non_l7 = int(row["non_l5_non_l7_clue_rows"])
    l5 = int(row["l5_clue_rows"])
    l7 = int(row["l7_clue_rows"])
    semantic = str(row["semantic_pair"])
    control = float(row["control_ratio_premay_max"])

    if non_l5_non_l7 >= 3 and l5 >= 1 and control < 0.85:
        return (
            "PASS_A7LS24_STRONG_LABEL_TRANSFER",
            "Has L5 and at least three non-L5/non-L7 clue rows with acceptable control margin.",
            True,
        )
    if non_l5_non_l7 >= 1 and l5 >= 1 and ("open_interest" in semantic or "positioning" in semantic):
        return (
            "PASS_A7LS24_MECHANISM_LABEL_TRANSFER",
            "Has non-L5 transfer plus leverage/positioning mechanism; keep as mechanism-diverse seed.",
            True,
        )
    if non_l5_non_l7 >= 1 and l5 >= 1:
        return (
            "HOLD_A7LS24_WEAK_LABEL_TRANSFER",
            "Has one non-L5 transfer but mechanism/control evidence is not enough for priority.",
            False,
        )
    if l7 > 0 and l5 > 0:
        return (
            "DIAGNOSTIC_A7LS24_L5_PLUS_RANK_ONLY",
            "Transfers only to ranked-return diagnostic label, not to raw/relative labels.",
            False,
        )
    return (
        "HOLD_A7LS24_L5_ONLY",
        "Evidence remains concentrated in L5 vol-adjusted return.",
        False,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    queue = pd.read_csv(QUEUE)
    labels = pd.read_csv(LABELS)
    labels = labels[labels["blueprint_id"].isin(set(queue["blueprint_id"]))].copy()
    labels["is_clue"] = clue_mask(labels)
    labels["is_l5_clue"] = labels["is_clue"] & labels["label_family"].eq(L5)
    labels["is_l7_clue"] = labels["is_clue"] & labels["label_family"].eq(L7)
    labels["is_non_l5_non_l7_clue"] = labels["is_clue"] & ~labels["label_family"].isin([L5, L7])

    label_audit = (
        labels.groupby("blueprint_id")
        .agg(
            label_rows=("label_family", "size"),
            clue_rows=("is_clue", "sum"),
            l5_clue_rows=("is_l5_clue", "sum"),
            l7_clue_rows=("is_l7_clue", "sum"),
            non_l5_non_l7_clue_rows=("is_non_l5_non_l7_clue", "sum"),
            non_l5_non_l7_label_families=(
                "label_family",
                lambda s: labels.loc[s.index][labels.loc[s.index, "is_non_l5_non_l7_clue"]][
                    "label_family"
                ].nunique(),
            ),
            non_l5_non_l7_horizons=(
                "label_horizon_h",
                lambda s: labels.loc[s.index][labels.loc[s.index, "is_non_l5_non_l7_clue"]][
                    "label_horizon_h"
                ].nunique(),
            ),
            worst_control_ratio=("control_ratio_premay_max", "max"),
            best_control_ratio=("control_ratio_premay_max", "min"),
            best_cost10=("cost10_recent_oriented", "max"),
        )
        .reset_index()
    )
    label_audit.to_csv(OUT_DIR / "a7ls24_label_transfer_audit.csv", index=False)

    detail = queue.merge(label_audit, on="blueprint_id", how="left")
    for col in [
        "label_rows",
        "clue_rows",
        "l5_clue_rows",
        "l7_clue_rows",
        "non_l5_non_l7_clue_rows",
        "non_l5_non_l7_label_families",
        "non_l5_non_l7_horizons",
    ]:
        detail[col] = detail[col].fillna(0).astype(int)

    decisions = []
    reasons = []
    selected = []
    for _, row in detail.iterrows():
        decision, reason, keep = transfer_decision(row)
        decisions.append(decision)
        reasons.append(reason)
        selected.append(keep)

    detail["a7ls24_decision"] = decisions
    detail["a7ls24_reason"] = reasons
    detail["authorizes_a7ls25_label_transfer_packet"] = selected
    detail["role_in_a7ls25"] = detail["authorizes_a7ls25_label_transfer_packet"].map(
        {True: "label_transfer_seed", False: "l5_only_or_rank_control"}
    )
    detail["authorizes_search"] = False
    detail["authorizes_alpha_proof"] = False

    ordered = detail.sort_values(
        ["authorizes_a7ls25_label_transfer_packet", "score_no_may"], ascending=[False, False]
    )
    ordered.to_csv(OUT_DIR / "a7ls24_candidate_label_transfer_decisions.csv", index=False)

    packet = ordered.copy()
    packet.to_csv(OUT_DIR / "a7ls24_a7ls25_label_transfer_packet_queue.csv", index=False)

    family = (
        detail.groupby(["a7ls24_decision", "semantic_pair", "selected_label_family"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    family.to_csv(OUT_DIR / "a7ls24_decision_family_summary.csv", index=False)

    transfer_count = int(detail["authorizes_a7ls25_label_transfer_packet"].sum())
    strong_count = int(detail["a7ls24_decision"].eq("PASS_A7LS24_STRONG_LABEL_TRANSFER").sum())
    mechanism_count = int(detail["a7ls24_decision"].eq("PASS_A7LS24_MECHANISM_LABEL_TRANSFER").sum())
    l5_only_count = int(detail["a7ls24_decision"].eq("HOLD_A7LS24_L5_ONLY").sum())
    semantic_count = int(detail[detail["authorizes_a7ls25_label_transfer_packet"]]["semantic_pair"].nunique())
    input_count = int(len(detail))

    blockers: list[str] = []
    if transfer_count < 3:
        blockers.append("label_transfer_seed_count_lt_3")
    if semantic_count < 2:
        blockers.append("label_transfer_semantic_pair_count_lt_2")

    if blockers:
        stage_decision = "HOLD_A7LS24_LABEL_TRANSFER_INSUFFICIENT"
        next_authorized = ["A7LS24R label-transfer repair / broader queue replay"]
    else:
        stage_decision = "PASS_A7LS24_LABEL_TRANSFER_PACKET_READY_FOR_A7LS25"
        next_authorized = ["A7LS25 label-transfer portfolio contribution replay packet"]

    manifest = {
        "stage": STAGE,
        "decision": stage_decision,
        "blockers": blockers,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "input_candidate_count": input_count,
        "label_transfer_seed_count": transfer_count,
        "strong_label_transfer_count": strong_count,
        "mechanism_label_transfer_count": mechanism_count,
        "l5_only_hold_count": l5_only_count,
        "label_transfer_semantic_pair_count": semantic_count,
        "uses_may": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_authorized": next_authorized,
    }
    write_json(OUT_DIR / "a7ls24_manifest.json", manifest)
    write_json(
        OUT_DIR / "a7ls24_authorization_matrix.json",
        {
            "authorized": next_authorized,
            "not_authorized": ["formula search", "large search", "alpha proof", "shadow", "paper", "live"],
        },
    )

    report_lines = [
        f"# CRYPTO A7LS-24 Label-Transfer Deep Bias Replay ({DATE})",
        "",
        "## Decision",
        "",
        f"`{stage_decision}`",
        "",
        "## Summary",
        "",
        f"- input candidates: {input_count}",
        f"- label-transfer seeds: {transfer_count}",
        f"- strong label-transfer: {strong_count}",
        f"- mechanism label-transfer: {mechanism_count}",
        f"- L5-only holds: {l5_only_count}",
        f"- label-transfer semantic pairs: {semantic_count}",
        "",
        "## Main Finding",
        "",
        "A7LS23 correctly flagged the main risk: the selected queue is L5-heavy. A7LS24 narrows it to candidates that transfer beyond L5 into raw/relative/liquidity-tier labels. The rest are retained only as L5 controls.",
        "",
        "## Label-Transfer Seeds",
        "",
    ]
    seeds = ordered[ordered["authorizes_a7ls25_label_transfer_packet"]]
    for _, row in seeds.iterrows():
        report_lines.extend(
            [
                f"### {row['blueprint_id']}",
                "",
                f"- decision: `{row['a7ls24_decision']}`",
                f"- semantic_pair: `{row['semantic_pair']}`",
                f"- selected label: `{row['selected_label_family']} / {row['label_horizon_h']}h`",
                f"- non-L5/non-L7 clue rows: `{int(row['non_l5_non_l7_clue_rows'])}`",
                f"- non-L5/non-L7 label families: `{int(row['non_l5_non_l7_label_families'])}`",
                f"- score_no_may: `{row['score_no_may']:.4f}`",
                f"- control_ratio_premay_max: `{row['control_ratio_premay_max']:.4f}`",
                f"- principle: {row['financial_principle']}",
                f"- expression: `{row['expression']}`",
                "",
            ]
        )

    report_lines.extend(
        [
            "## Boundaries",
            "",
            "- This stage uses existing A7LS21 label-response metrics; it does not generate or replay new formulas.",
            "- May is not used.",
            "- A7LS25 is authorized only as a label-transfer portfolio contribution replay packet.",
            "- Search, alpha proof, shadow, paper, and live remain blocked.",
            "",
            "## Decision Counts",
            "",
            detail["a7ls24_decision"].value_counts().rename_axis("decision").reset_index(name="count").to_markdown(index=False),
            "",
        ]
    )
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
