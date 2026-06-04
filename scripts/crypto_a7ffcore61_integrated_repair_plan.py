from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
EXTERNAL = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604")
RUNTIME = REPO / "runtime" / "a7ffcore61_integrated_repair_plan"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE61_INTEGRATED_REPAIR_PLAN_20260605.md"

CORE60B = REPO / "runtime" / "a7ffcore60b_target_adequacy_repair_audit"
CORE60C = REPO / "runtime" / "a7ffcore60c_materialization_repair_audit"
CORE60D = REPO / "runtime" / "a7ffcore60d_selector_portfolio_proxy_attribution"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 50) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```csv\n" + view.to_csv(index=False) + "```"


def collect(name: str, shard_count: int = 6) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for shard in range(shard_count):
        path = EXTERNAL / f"shard_{shard:02d}" / f"a7ffcore59_s{shard:02d}_{name}.csv"
        frame = read_csv(path)
        if not frame.empty:
            frame["core59_shard"] = f"s{shard:02d}"
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def decision_class(value: Any) -> str:
    text = str(value)
    if "NUMERIC_CLUE" in text and "RANK_LABEL" not in text:
        return "non_l7_numeric_clue"
    if "RANK_LABEL_DIAGNOSTIC_CLUE" in text:
        return "rank_label_diagnostic_clue"
    if "PRE_MAY_UNSTABLE" in text:
        return "pre_may_unstable"
    if "CONTROL_DOMINATED" in text:
        return "control_dominated"
    if "ONE_BAR_LAG_FRAGILE" in text:
        return "one_bar_lag_fragile"
    return "other"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    core60b = read_json(CORE60B / "core60b_decision_record.json")
    core60c = read_json(CORE60C / "core60c_decision_record.json")
    core60d = read_json(CORE60D / "core60d_decision_record.json")
    material_semantic = read_csv(CORE60C / "core60c_materialization_by_semantic_pair.csv")

    label = collect("label_response_metrics")
    queue = collect("queue")
    material = collect("materialization_metrics")
    selected = collect("selected_portfolio_queue")
    if label.empty or queue.empty or material.empty:
        raise SystemExit("CORE61 requires CORE59 detailed label/queue/materialization artifacts")

    inactive_semantics = set(
        material_semantic.loc[
            pd.to_numeric(material_semantic.get("activity_ok_rows"), errors="coerce").fillna(0).eq(0),
            "semantic_pair",
        ].astype(str)
    )
    weak_materialization_semantics = set(
        material_semantic.loc[
            pd.to_numeric(material_semantic.get("activity_ok_rate"), errors="coerce").fillna(0).lt(0.6),
            "semantic_pair",
        ].astype(str)
    )

    df = label.copy()
    df["decision_class"] = df["decision"].map(decision_class)
    df["is_l7"] = df["label_family"].eq("L7_ranked_future_return")
    df["is_non_l7_label"] = ~df["is_l7"]
    df["is_non_l7_clue"] = df["decision_class"].eq("non_l7_numeric_clue") & df["is_non_l7_label"]
    df["control_ratio"] = pd.to_numeric(df["control_ratio_premay_max"], errors="coerce")
    df["cost10"] = pd.to_numeric(df["cost10_recent_oriented"], errors="coerce")
    df["near_miss_non_l7"] = (
        df["is_non_l7_label"]
        & df["decision_class"].isin(["pre_may_unstable", "control_dominated", "one_bar_lag_fragile"])
        & (pd.to_numeric(df["premay_positive_split_count"], errors="coerce").fillna(0) >= 2)
        & (df["control_ratio"].fillna(999) < 1.25)
        & (df["cost10"].fillna(-999) > -0.0025)
    )
    df["blocked_by_zero_activity_semantic"] = df["semantic_pair"].astype(str).isin(inactive_semantics)
    df["weak_materialization_semantic"] = df["semantic_pair"].astype(str).isin(weak_materialization_semantics)

    candidate_rows = df[(df["is_non_l7_clue"] | df["near_miss_non_l7"])].copy()
    candidate_rows["core61_reason"] = candidate_rows.apply(
        lambda r: "exact_non_l7_clue" if bool(r["is_non_l7_clue"]) else f"near_miss_{r['decision_class']}",
        axis=1,
    )
    candidate_rows["core61_blocked"] = candidate_rows["blocked_by_zero_activity_semantic"]
    candidate_rows["core61_route"] = candidate_rows.apply(
        lambda r: "CORE62C_materialization_repair_required"
        if bool(r["blocked_by_zero_activity_semantic"])
        else ("CORE62A_non_l7_selector_target_dryrun" if bool(r["is_non_l7_clue"]) else "CORE62B_target_near_miss_repair_dryrun"),
        axis=1,
    )

    sort_cols = ["core61_blocked", "is_non_l7_clue", "control_ratio", "cost10", "premay_positive_split_count"]
    candidate_rows = candidate_rows.sort_values(sort_cols, ascending=[True, False, True, False, False])
    keep_cols = [
        "blueprint_id", "core59_shard", "core61_route", "core61_reason", "core61_blocked",
        "semantic_pair", "motif", "label_family", "label_horizon_h", "decision",
        "premay_positive_split_count", "control_ratio", "cost10", "robust_ok", "lag_ok",
        "expression",
    ]
    candidate_preview = candidate_rows[[c for c in keep_cols if c in candidate_rows.columns]].drop_duplicates()
    candidate_preview.to_csv(RUNTIME / "core61_repair_candidate_queue_preview.csv", index=False)

    route_summary = candidate_preview.groupby(["core61_route", "core61_reason"], dropna=False).agg(
        rows=("blueprint_id", "size"),
        unique_blueprints=("blueprint_id", "nunique"),
        semantic_pair_count=("semantic_pair", "nunique"),
        median_control_ratio=("control_ratio", "median"),
        min_cost10=("cost10", "min"),
        max_cost10=("cost10", "max"),
    ).reset_index().sort_values(["core61_route", "rows"], ascending=[True, False])
    route_summary.to_csv(RUNTIME / "core61_route_summary.csv", index=False)

    materialization_repair_policy = pd.DataFrame(
        [
            {
                "repair_item": "funding_positioning_zero_activity",
                "affected_semantic_pairs": ";".join(sorted(inactive_semantics)),
                "evidence": "CORE60C activity_ok_rows=0 for funding related pairs",
                "action": "do not send these pairs to selector until panel availability / transform activity repair passes",
                "next_stage": "CORE62C_materialization_repair_dryrun",
            },
            {
                "repair_item": "basis_funding_sparse_finite_share",
                "affected_semantic_pairs": "basis_premium_like|funding_like",
                "evidence": "median_finite_share near zero despite nonzero_share high",
                "action": "audit funding_rate timestamp/coverage and transform windows before any numeric expansion",
                "next_stage": "CORE62C_materialization_repair_dryrun",
            },
        ]
    )
    materialization_repair_policy.to_csv(RUNTIME / "core61_materialization_repair_policy.csv", index=False)

    target_repair_policy = pd.DataFrame(
        [
            {
                "policy_id": "T0_non_l7_first",
                "rule": "CORE62 selector dryrun must score non-L7 labels first and treat L7 as diagnostic-only evidence",
                "threshold": "selected_l7_share <= 0.40",
            },
            {
                "policy_id": "T1_premay_stability_split",
                "rule": "separate pre_may_unstable into split-sign instability vs weak magnitude; do not loosen pass gate globally",
                "threshold": "non_l7_target_count >= 4 before numeric expansion",
            },
            {
                "policy_id": "T2_control_margin_floor",
                "rule": "non-L7 exact clue or near-miss must retain control_ratio < 1.0 for selector queue",
                "threshold": "hard reject control_ratio >= 1.0",
            },
            {
                "policy_id": "T3_cost_floor",
                "rule": "cost10 negative candidates can only enter target forensic, not selector queue",
                "threshold": "selector cost10_recent_oriented > 0",
            },
        ]
    )
    target_repair_policy.to_csv(RUNTIME / "core61_target_repair_policy.csv", index=False)

    selector_policy = {
        "stage": "A7FF-CORE61",
        "selector_mode": "non_l7_first_repair_dryrun",
        "hard_caps": {
            "selected_l7_share_max": 0.40,
            "selected_non_l7_min": 12,
            "selected_semantic_pair_min": 4,
            "top_semantic_pair_share_max": 0.35,
        },
        "hard_reject": [
            "control_ratio >= 1.0",
            "cost10_recent_oriented <= 0 for selector route",
            "zero_activity_semantic_pair",
            "missing materialization contract",
        ],
        "allowed_next": [
            "CORE62A non-L7 selector target dryrun on exact clean subset",
            "CORE62B target near-miss repair dryrun",
            "CORE62C materialization repair dryrun",
        ],
        "forbidden": [
            "formula search",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }
    write_json(RUNTIME / "core61_selector_policy.json", selector_policy)

    exact_non_l7 = candidate_preview[candidate_preview["core61_reason"].eq("exact_non_l7_clue")]
    exact_clean = exact_non_l7[
        (~exact_non_l7["core61_blocked"])
        & (pd.to_numeric(exact_non_l7["control_ratio"], errors="coerce") < 1.0)
        & (pd.to_numeric(exact_non_l7["cost10"], errors="coerce") > 0)
    ]
    near_miss = candidate_preview[candidate_preview["core61_reason"].astype(str).str.startswith("near_miss")]

    blockers: list[str] = []
    if len(exact_clean) < 4:
        blockers.append("exact_clean_non_l7_lt_4")
    if exact_clean["semantic_pair"].nunique() < 2:
        blockers.append("exact_clean_semantic_pair_lt_2")
    if len(near_miss) < 24:
        blockers.append("near_miss_pool_lt_24")
    if len(inactive_semantics) > 0:
        blockers.append("materialization_zero_activity_pairs_present")

    decision = "PASS_CORE61_REPAIR_PLAN_READY_FOR_CORE62_DRYRUN" if len(candidate_preview) > 0 else "HOLD_CORE61_NO_REPAIR_QUEUE"
    if "materialization_zero_activity_pairs_present" in blockers or "exact_clean_non_l7_lt_4" in blockers:
        decision = "HOLD_CORE61_REPAIR_PLAN_REQUIRES_MATERIALIZATION_AND_TARGET_FIX"

    record = {
        "stage": "A7FF-CORE61",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_core60b_decision": core60b.get("decision"),
        "source_core60c_decision": core60c.get("decision"),
        "source_core60d_decision": core60d.get("decision"),
        "repair_candidate_rows": int(len(candidate_preview)),
        "exact_non_l7_rows": int(len(exact_non_l7)),
        "exact_clean_non_l7_rows": int(len(exact_clean)),
        "near_miss_rows": int(len(near_miss)),
        "repair_semantic_pair_count": int(candidate_preview["semantic_pair"].nunique()) if not candidate_preview.empty else 0,
        "inactive_semantic_pair_count": int(len(inactive_semantics)),
        "authorizes_core62a_non_l7_selector_dryrun": int(len(exact_clean)) >= 4,
        "authorizes_core62b_target_near_miss_dryrun": int(len(near_miss)) >= 24,
        "authorizes_core62c_materialization_repair_dryrun": int(len(inactive_semantics)) > 0,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "executes_search": False,
        "executes_replay": False,
    }
    write_json(RUNTIME / "core61_decision_record.json", record)

    REPORT.write_text("\n".join([
        "# CRYPTO A7FF-CORE61 INTEGRATED REPAIR PLAN",
        "",
        f"Generated: {record['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE61 converts CORE60B/C/D bottleneck audits into a concrete repair queue preview and selector/materialization/target policies. It does not search, replay, or promote candidates.",
        "",
        "## Decision Record",
        "",
        "```json",
        json.dumps(record, indent=2, sort_keys=True),
        "```",
        "",
        "## Route Summary",
        "",
        md_table(route_summary, 40),
        "",
        "## Repair Candidate Queue Preview",
        "",
        md_table(candidate_preview, 40),
        "",
        "## Target Repair Policy",
        "",
        md_table(target_repair_policy),
        "",
        "## Materialization Repair Policy",
        "",
        md_table(materialization_repair_policy),
        "",
        "## Selector Policy",
        "",
        "```json",
        json.dumps(selector_policy, indent=2, sort_keys=True),
        "```",
        "",
    ]), encoding="utf-8")

    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
