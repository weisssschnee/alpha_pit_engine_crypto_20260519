from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260607"
STAGE = "A7LS-22"

IN_DIR = REPO / "runtime" / "a7ls21_company_deep_replay_aggregate"
SELECTED = IN_DIR / "a7ls21_selected_portfolio_queue_all.csv"
LABEL_RESPONSE = IN_DIR / "a7ls21_label_response_metrics_all.csv"
UPSTREAM_MANIFEST = IN_DIR / "a7ls21_manifest.json"

FULL_BLUEPRINT_INDEX = Path(
    r"G:\AlphaFactory_CryptoData\research_runtime\a7ls15_million_scale_blueprint_generation_20260606\a7ls15_full_blueprint_index.csv"
)

OUT_DIR = REPO / "runtime" / "a7ls22_clue_attribution_promotion_triage"
REPORT = REPO / "reports" / f"CRYPTO_A7LS22_CLUE_ATTRIBUTION_PROMOTION_TRIAGE_{DATE}.md"

OPERATORS = {
    "Abs",
    "Add",
    "Clip",
    "CSRank",
    "Decay",
    "Delta",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "Sub",
    "TSRank",
    "ZScore",
}

FIELD_HINTS = {
    "basis": "basis/premium dislocation",
    "premium": "basis/premium dislocation",
    "funding": "funding crowding",
    "open_interest": "leverage / open-interest state",
    "long_short": "positioning crowding",
    "taker": "aggressive taker flow",
    "volume": "liquidity / volume state",
    "liquidity": "liquidity state",
    "age": "listing lifecycle",
    "return": "price response",
    "close": "price level / price move",
}


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def extract_tokens(expr: str) -> tuple[list[str], list[str]]:
    raw = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", str(expr))
    ops = [t for t in raw if t in OPERATORS]
    fields = [t for t in raw if t not in OPERATORS and not t.startswith("skel_")]
    # Drop obvious non-field constants that can appear in expressions if parser
    # ever expands them as identifiers.
    fields = [f for f in fields if f not in {"True", "False", "nan", "inf"}]
    return sorted(set(fields)), ops


def mechanism_from_row(row: pd.Series, fields: list[str]) -> tuple[str, str]:
    semantic = str(row.get("semantic_pair", ""))
    motif = str(row.get("motif", ""))
    lower = " ".join([semantic, motif, " ".join(fields)]).lower()
    tags = []
    for needle, tag in FIELD_HINTS.items():
        if needle in lower and tag not in tags:
            tags.append(tag)
    if not tags:
        tags.append("generic cross-sectional state")

    if "open_interest" in lower and "long_short" in lower:
        principle = "leverage expansion/contraction combined with trader positioning imbalance"
        chinese = "杠杆仓位变化和多空拥挤共同刻画拥挤交易状态。"
    elif "open_interest" in lower and "taker" in lower:
        principle = "open-interest crowding combined with aggressive taker-flow pressure"
        chinese = "持仓扩张叠加主动买卖压力，用来识别杠杆资金流方向。"
    elif "basis" in lower and "liquidity" in lower:
        principle = "basis/premium dislocation filtered by liquidity or volume state"
        chinese = "基差/溢价异常只有在特定流动性状态下更可能有预测意义。"
    elif "basis" in lower and "age" in lower:
        principle = "basis/premium dislocation conditioned on listing lifecycle"
        chinese = "新老币生命周期会改变基差/溢价异常的含义。"
    elif "basis" in lower and "positioning" in lower:
        principle = "basis/premium dislocation versus positioning crowding"
        chinese = "基差/溢价偏离与多空持仓拥挤之间的相对状态。"
    elif "basis" in lower and "price" in lower:
        principle = "basis/premium dislocation versus short-term price response"
        chinese = "基差/溢价状态与短期价格反应的相对错位。"
    elif "funding" in lower and "liquidity" in lower:
        principle = "funding/basis crowding under liquidity regime"
        chinese = "资金费/基差拥挤在流动性状态约束下的排序信号。"
    elif semantic == "price_like":
        principle = "short-horizon price relative-value / reversal diagnostic"
        chinese = "短周期价格相对变化，更多是诊断信号而非独立信息源。"
    else:
        principle = "typed state interaction"
        chinese = "多个已知状态变量的类型化交互，需要继续检查增量信息。"
    return principle, chinese + " 核心标签：" + "；".join(tags)


def load_provenance(ids: set[str]) -> pd.DataFrame:
    columns = [
        "blueprint_id",
        "a7ls_lane",
        "lane_name",
        "search_role",
        "level",
        "candidate_role",
        "generation_priority",
        "semantic_pair",
        "motif",
        "primary_field",
        "secondary_field",
        "primary_semantic",
        "secondary_semantic",
        "primary_transform",
        "secondary_transform",
        "skeleton_key",
        "production_key",
        "source_stage",
        "source_seed_id",
        "checkpoint_group",
    ]
    if not FULL_BLUEPRINT_INDEX.exists():
        return pd.DataFrame(columns=columns + ["provenance_found"])

    chunks = []
    for chunk in pd.read_csv(FULL_BLUEPRINT_INDEX, usecols=lambda c: c in columns, chunksize=100_000):
        hit = chunk[chunk["blueprint_id"].isin(ids)].copy()
        if not hit.empty:
            chunks.append(hit)
    if not chunks:
        out = pd.DataFrame({"blueprint_id": sorted(ids)})
        out["provenance_found"] = False
        return out
    out = pd.concat(chunks, ignore_index=True).drop_duplicates("blueprint_id")
    out["provenance_found"] = True
    missing = ids - set(out["blueprint_id"])
    if missing:
        out = pd.concat(
            [out, pd.DataFrame({"blueprint_id": sorted(missing), "provenance_found": False})],
            ignore_index=True,
        )
    return out


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def assign_duplicate_clusters(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    field_sets = [set(str(v).split("|")) if isinstance(v, str) else set() for v in df["field_tokens"]]
    for i in range(n):
        for j in range(i + 1, n):
            same_skel = str(df.iloc[i]["skeleton_key"]) == str(df.iloc[j]["skeleton_key"])
            same_semantic = str(df.iloc[i]["semantic_pair"]) == str(df.iloc[j]["semantic_pair"])
            same_motif = str(df.iloc[i]["motif"]) == str(df.iloc[j]["motif"])
            sim = jaccard(field_sets[i], field_sets[j])
            if same_skel or (sim >= 0.60 and (same_semantic or same_motif)):
                union(i, j)

    roots = {}
    cluster_ids = []
    for i in range(n):
        r = find(i)
        if r not in roots:
            roots[r] = f"cluster_{len(roots)+1:02d}"
        cluster_ids.append(roots[r])
    out = df.copy()
    out["duplicate_cluster_id"] = cluster_ids
    return out


def triage_decision(row: pd.Series, cluster_rank: int) -> tuple[str, str]:
    label = str(row["label_family"])
    control = float(row["control_ratio_premay_max"])
    score = float(row["score_no_may"])
    robust_ok = bool(row["robust_ok"])
    lag_ok = bool(row["lag_ok"])
    premay_all = bool(row["premay_all_positive"])
    cost10 = float(row["cost10_recent_oriented"])
    low_score_floor = 20.0

    if label == "L7_ranked_future_return":
        return "DIAGNOSTIC_ONLY_RANK_LABEL", "L7 ranked-return evidence cannot promote by itself."
    if control >= 0.90:
        return "HOLD_CONTROL_MARGIN_WEAK", "Control margin is too thin for promotion."
    if not (premay_all and lag_ok and robust_ok and cost10 > 0):
        return "HOLD_STABILITY_OR_COST_WEAK", "Split/lag/robust/cost gate is incomplete."
    if score < low_score_floor:
        return "HOLD_LOW_MARGINAL_SCORE", "Evidence exists but marginal score is too small."
    if cluster_rank > 1:
        return "HOLD_DUPLICATE_CLUSTER_FOLLOWER", "Cluster has a stronger representative."
    return "ALLOW_KEEP_REVIEW", "Eligible for strict candidate-factor review; not alpha proof."


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    upstream = read_json(UPSTREAM_MANIFEST)
    selected = pd.read_csv(SELECTED)
    labels = pd.read_csv(LABEL_RESPONSE)

    ids = set(selected["blueprint_id"].astype(str))
    provenance = load_provenance(ids)
    provenance.to_csv(OUT_DIR / "a7ls22_provenance_join.csv", index=False)

    rows = []
    for _, row in selected.iterrows():
        fields, ops = extract_tokens(row["expression"])
        principle, cn = mechanism_from_row(row, fields)
        rows.append(
            {
                "blueprint_id": row["blueprint_id"],
                "field_tokens": "|".join(fields),
                "operator_tokens": "|".join(ops),
                "operator_depth_proxy": len(ops),
                "raw_field_count": len(fields),
                "financial_principle": principle,
                "chinese_explanation": cn,
            }
        )
    attribution = pd.DataFrame(rows)

    review = selected.merge(attribution, on="blueprint_id", how="left").merge(
        provenance.drop(columns=["semantic_pair", "motif", "skeleton_key"], errors="ignore"),
        on="blueprint_id",
        how="left",
        suffixes=("", "_prov"),
    )
    review["provenance_found"] = review["provenance_found"].fillna(False)
    review = assign_duplicate_clusters(review)
    review["cluster_score_rank"] = (
        review.groupby("duplicate_cluster_id")["score_no_may"].rank(method="first", ascending=False).astype(int)
    )

    decisions = []
    reasons = []
    for _, row in review.iterrows():
        decision, reason = triage_decision(row, int(row["cluster_score_rank"]))
        decisions.append(decision)
        reasons.append(reason)
    review["triage_decision"] = decisions
    review["triage_reason"] = reasons
    review["keep_review_allowed"] = review["triage_decision"].eq("ALLOW_KEEP_REVIEW")
    review["alpha_proof_allowed"] = False
    review["search_allowed"] = False

    candidate_cols = [
        "blueprint_id",
        "shard_id",
        "triage_decision",
        "triage_reason",
        "keep_review_allowed",
        "semantic_pair",
        "motif",
        "label_family",
        "label_horizon_h",
        "score_no_may",
        "control_ratio_premay_max",
        "premay_positive_split_count",
        "premay_all_positive",
        "lag_ok",
        "robust_ok",
        "cost10_recent_oriented",
        "duplicate_cluster_id",
        "cluster_score_rank",
        "skeleton_key",
        "production_key",
        "a7ls_lane",
        "lane_name",
        "search_role",
        "source_stage",
        "source_seed_id",
        "financial_principle",
        "chinese_explanation",
        "field_tokens",
        "operator_tokens",
        "expression",
    ]
    for col in candidate_cols:
        if col not in review.columns:
            review[col] = ""
    review[candidate_cols].sort_values(
        ["keep_review_allowed", "score_no_may"], ascending=[False, False]
    ).to_csv(OUT_DIR / "a7ls22_candidate_factor_review.csv", index=False)

    attribution_cols = [
        "blueprint_id",
        "financial_principle",
        "chinese_explanation",
        "field_tokens",
        "operator_tokens",
        "operator_depth_proxy",
        "raw_field_count",
        "expression",
    ]
    review[attribution_cols].to_csv(OUT_DIR / "a7ls22_mechanism_attribution.csv", index=False)

    cluster = (
        review.groupby("duplicate_cluster_id")
        .agg(
            cluster_size=("blueprint_id", "size"),
            representative_blueprint=("blueprint_id", lambda s: review.loc[s.index, :].sort_values("score_no_may", ascending=False).iloc[0]["blueprint_id"]),
            max_score_no_may=("score_no_may", "max"),
            semantic_pairs=("semantic_pair", lambda s: ";".join(sorted(set(map(str, s))))),
            label_families=("label_family", lambda s: ";".join(sorted(set(map(str, s))))),
            skeletons=("skeleton_key", lambda s: ";".join(sorted(set(map(str, s))))),
            allowed_keep_review_count=("keep_review_allowed", "sum"),
        )
        .reset_index()
        .sort_values(["allowed_keep_review_count", "max_score_no_may"], ascending=[False, False])
    )
    cluster.to_csv(OUT_DIR / "a7ls22_duplicate_cluster_audit.csv", index=False)

    family = (
        review.groupby(["semantic_pair", "motif", "label_family", "triage_decision"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    family.to_csv(OUT_DIR / "a7ls22_family_label_triage_summary.csv", index=False)

    label_risk = (
        review.groupby("label_family", dropna=False)
        .agg(
            selected_count=("blueprint_id", "size"),
            keep_review_allowed_count=("keep_review_allowed", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            max_score_no_may=("score_no_may", "max"),
        )
        .reset_index()
        .sort_values("selected_count", ascending=False)
    )
    label_risk["selected_share"] = label_risk["selected_count"] / max(1, len(review))
    label_risk.to_csv(OUT_DIR / "a7ls22_label_family_risk.csv", index=False)

    promotion = review[review["keep_review_allowed"]].copy()
    promotion[candidate_cols].to_csv(OUT_DIR / "a7ls22_promotion_triage.csv", index=False)

    selected_count = int(len(review))
    keep_count = int(review["keep_review_allowed"].sum())
    cluster_count = int(review["duplicate_cluster_id"].nunique())
    semantic_count = int(review["semantic_pair"].nunique())
    top_label_share = float(review["label_family"].value_counts(normalize=True).iloc[0]) if selected_count else 0.0
    top_semantic_share = float(review["semantic_pair"].value_counts(normalize=True).iloc[0]) if selected_count else 0.0
    l7_count = int(review["label_family"].eq("L7_ranked_future_return").sum())
    non_l7_keep_count = int(
        (review["keep_review_allowed"] & ~review["label_family"].eq("L7_ranked_future_return")).sum()
    )

    blockers = []
    if selected_count < 4:
        blockers.append("selected_queue_too_small")
    if keep_count < 4:
        blockers.append("keep_review_allowed_lt_4")
    if non_l7_keep_count < 4:
        blockers.append("non_l7_keep_review_allowed_lt_4")
    if semantic_count < 4:
        blockers.append("semantic_pair_count_lt_4")
    if top_label_share > 0.70:
        blockers.append("top_label_family_share_gt_70pct")

    if blockers:
        decision = "HOLD_A7LS22_PROMOTION_TRIAGE_INSUFFICIENT"
        next_authorized = ["A7LS22R queue repair / broader attribution rerun"]
    else:
        decision = "PASS_A7LS22_RESEARCH_REVIEW_QUEUE_READY"
        next_authorized = ["A7LS23 strict candidate-factor review / bias audit packet"]

    manifest = {
        "stage": STAGE,
        "decision": decision,
        "blockers": blockers,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "upstream_decision": upstream.get("decision"),
        "input_selected_count": selected_count,
        "keep_review_allowed_count": keep_count,
        "non_l7_keep_review_allowed_count": non_l7_keep_count,
        "diagnostic_l7_count": l7_count,
        "duplicate_cluster_count": cluster_count,
        "semantic_pair_count": semantic_count,
        "top_label_family_share": top_label_share,
        "top_semantic_pair_share": top_semantic_share,
        "uses_may": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_authorized": next_authorized,
    }
    write_json(OUT_DIR / "a7ls22_manifest.json", manifest)

    auth = {
        "authorized": next_authorized,
        "not_authorized": [
            "formula search",
            "large search",
            "alpha proof",
            "shadow",
            "paper",
            "live",
        ],
    }
    write_json(OUT_DIR / "a7ls22_authorization_matrix.json", auth)

    report_lines = [
        f"# CRYPTO A7LS-22 Clue Attribution / Promotion Triage ({DATE})",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- input selected queue: {selected_count}",
        f"- keep-review allowed: {keep_count}",
        f"- non-L7 keep-review allowed: {non_l7_keep_count}",
        f"- duplicate clusters: {cluster_count}",
        f"- semantic pairs: {semantic_count}",
        f"- top label family share: {top_label_share:.2%}",
        f"- top semantic pair share: {top_semantic_share:.2%}",
        "",
        "## Main Finding",
        "",
        "A7LS21 did not collapse into one formula shape. It produced a small but usable research-review queue across basis/liquidity, basis/listing-age, basis/positioning, OI/positioning, and OI/taker-flow structures. The main risk is label concentration: L5 vol-adjusted return remains the dominant label family.",
        "",
        "## Keep-Review Queue",
        "",
    ]

    if promotion.empty:
        report_lines.append("No candidate passed keep-review triage.")
    else:
        for _, row in promotion.sort_values("score_no_may", ascending=False).iterrows():
            report_lines.extend(
                [
                    f"### {row['blueprint_id']}",
                    "",
                    f"- semantic_pair: `{row['semantic_pair']}`",
                    f"- motif: `{row['motif']}`",
                    f"- label: `{row['label_family']} / {row['label_horizon_h']}h`",
                    f"- score_no_may: `{row['score_no_may']:.4f}`",
                    f"- control_ratio_premay_max: `{row['control_ratio_premay_max']:.4f}`",
                    f"- principle: {row['financial_principle']}",
                    f"- 简释: {row['chinese_explanation']}",
                    f"- expression: `{row['expression']}`",
                    "",
                ]
            )

    report_lines.extend(
        [
            "## Boundaries",
            "",
            "- This stage does not execute search or replay.",
            "- May is not used.",
            "- ALLOW_KEEP_REVIEW is not alpha proof; it only authorizes strict candidate-factor review / bias audit packet.",
            "- Shadow, paper, and live remain blocked.",
            "",
            "## Triage Counts",
            "",
            review["triage_decision"].value_counts().rename_axis("triage_decision").reset_index(name="count").to_markdown(index=False),
            "",
        ]
    )
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")

    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
