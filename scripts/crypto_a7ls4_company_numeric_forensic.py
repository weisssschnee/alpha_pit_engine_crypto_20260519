from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
INPUT = REPO / "runtime" / "a7ls3hr_company_result_aggregate"
RUNTIME = REPO / "runtime" / "a7ls4_company_numeric_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7LS4_COMPANY_NUMERIC_FORENSIC_20260605.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def safe_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def summarize(df: pd.DataFrame, cols: list[str], value_name: str = "rows") -> pd.DataFrame:
    if df.empty or any(col not in df.columns for col in cols):
        return pd.DataFrame(columns=cols + [value_name])
    return df.groupby(cols, dropna=False).size().reset_index(name=value_name).sort_values(value_name, ascending=False)


def response_blocker_summary(responses: pd.DataFrame) -> pd.DataFrame:
    if responses.empty or "decision" not in responses.columns:
        return pd.DataFrame(columns=["blocker_family", "rows"])
    decision = responses["decision"].astype(str)
    families = []
    for value in decision:
        if "PRE_MAY_UNSTABLE" in value:
            families.append("pre_may_unstable")
        elif "CONTROL_DOMINATED" in value:
            families.append("control_dominated")
        elif "LAG_FRAGILE" in value:
            families.append("lag_fragile")
        elif "COST_FRAGILE" in value:
            families.append("cost_fragile")
        elif "NUMERIC_CLUE" in value:
            families.append("numeric_clue")
        elif "RANK_LABEL_DIAGNOSTIC_CLUE" in value:
            families.append("rank_label_diagnostic_clue")
        else:
            families.append("other")
    out = pd.Series(families).value_counts().rename_axis("blocker_family").reset_index(name="rows")
    out["share"] = out["rows"] / max(1, int(out["rows"].sum()))
    return out


def build_shortlist(clues: pd.DataFrame) -> pd.DataFrame:
    if clues.empty:
        return pd.DataFrame()
    frame = clues.copy()
    if "label_family" in frame.columns:
        frame["is_l7"] = frame["label_family"].astype(str).eq("L7_ranked_future_return")
    else:
        frame["is_l7"] = False
    for col in [
        "score_no_may",
        "control_ratio_premay_max",
        "robust_min_tstat_floor",
        "cost10_recent_oriented",
        "one_bar_lag_recent_oriented",
    ]:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    if "robust_ok" in frame.columns:
        frame["robust_ok_bool"] = safe_bool(frame["robust_ok"])
    else:
        frame["robust_ok_bool"] = False
    if "lag_ok" in frame.columns:
        frame["lag_ok_bool"] = safe_bool(frame["lag_ok"])
    else:
        frame["lag_ok_bool"] = False
    frame["shortlist_score"] = (
        frame.get("score_no_may", pd.Series(0, index=frame.index)).fillna(0)
        + frame.get("robust_min_tstat_floor", pd.Series(0, index=frame.index)).fillna(0) * 5
        - frame.get("control_ratio_premay_max", pd.Series(1, index=frame.index)).fillna(1) * 20
    )
    keep = frame[
        (~frame["is_l7"])
        & (frame.get("control_ratio_premay_max", pd.Series(99, index=frame.index)).fillna(99) < 1.0)
        & frame["robust_ok_bool"]
        & frame["lag_ok_bool"]
    ].copy()
    cols = [
        "blueprint_id",
        "expression",
        "semantic_pair",
        "motif",
        "label_family",
        "label_horizon_h",
        "decision",
        "shard",
        "score_no_may",
        "control_ratio_premay_max",
        "robust_min_tstat_floor",
        "cost10_recent_oriented",
        "one_bar_lag_recent_oriented",
        "skeleton_key",
        "finite_share",
        "nonzero_share",
        "shortlist_score",
    ]
    cols = [col for col in cols if col in keep.columns]
    return keep.sort_values("shortlist_score", ascending=False)[cols].head(64)


def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    clues = read_csv(INPUT / "a7ls3hr_combined_clues.csv")
    responses = read_csv(INPUT / "a7ls3hr_combined_responses.csv")
    portfolios = read_csv(INPUT / "a7ls3hr_combined_portfolio_candidates.csv")
    shards = read_csv(INPUT / "a7ls3hr_shard_manifest_summary.csv")

    clue_by_label = summarize(clues, ["label_family"])
    clue_by_pair = summarize(clues, ["semantic_pair"])
    clue_by_pair_label = summarize(clues, ["semantic_pair", "label_family"])
    clue_by_shard = summarize(clues, ["shard"])
    clue_by_motif = summarize(clues, ["motif"])
    portfolio_by_pair = summarize(portfolios, ["semantic_pair"])
    response_by_decision = summarize(responses, ["decision"])
    response_by_pair_decision = summarize(responses, ["semantic_pair", "decision"])
    blocker_summary = response_blocker_summary(responses)

    missing = shards[shards.get("blockers", pd.Series(dtype=str)).astype(str).str.contains("missing_numeric_fields", na=False)].copy()
    if not missing.empty:
        missing["root_cause"] = "panel_missing_listing_age_fields"
        missing["missing_field_family"] = "listing_age_like"

    shortlist = build_shortlist(clues)

    for name, frame in [
        ("a7ls4_clue_by_label.csv", clue_by_label),
        ("a7ls4_clue_by_semantic_pair.csv", clue_by_pair),
        ("a7ls4_clue_by_pair_label.csv", clue_by_pair_label),
        ("a7ls4_clue_by_shard.csv", clue_by_shard),
        ("a7ls4_clue_by_motif.csv", clue_by_motif),
        ("a7ls4_portfolio_by_semantic_pair.csv", portfolio_by_pair),
        ("a7ls4_response_by_decision.csv", response_by_decision),
        ("a7ls4_response_by_pair_decision.csv", response_by_pair_decision),
        ("a7ls4_response_blocker_summary.csv", blocker_summary),
        ("a7ls4_missing_field_shards.csv", missing),
        ("a7ls4_non_l7_control_clean_shortlist.csv", shortlist),
    ]:
        frame.to_csv(RUNTIME / name, index=False)

    clue_rows = int(len(clues))
    non_l7_rows = int((clues.get("label_family", pd.Series(dtype=str)).astype(str) != "L7_ranked_future_return").sum()) if not clues.empty else 0
    l7_rows = clue_rows - non_l7_rows
    response_rows = int(len(responses))
    portfolio_rows = int(len(portfolios))
    missing_shard_count = int(len(missing))
    pass_shards = int(shards.get("decision", pd.Series(dtype=str)).astype(str).str.contains("PASS_").sum()) if not shards.empty else 0

    top_pair_share = 0.0
    if not clue_by_pair.empty:
        top_pair_share = float(clue_by_pair["rows"].max() / max(1, clue_rows))

    blockers: list[str] = []
    if missing_shard_count:
        blockers.append("listing_age_fields_missing_for_raw_axis_shards")
    if top_pair_share > 0.35:
        blockers.append("clue_family_concentration")
    if non_l7_rows < 8:
        blockers.append("non_l7_clue_breadth_weak")
    if shortlist.empty:
        blockers.append("no_non_l7_control_clean_shortlist")

    decision = (
        "PASS_A7LS4_COMPANY_NUMERIC_FORENSIC_READY_FOR_A7LS5_REPAIR_AND_FOLLOWUP"
        if clue_rows > 0 and non_l7_rows > 0 and not shortlist.empty
        else "HOLD_A7LS4_COMPANY_NUMERIC_FORENSIC_NO_ACTIONABLE_SHORTLIST"
    )

    manifest = {
        "stage": "A7LS-4",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "input_clue_rows": clue_rows,
        "non_l7_clue_rows": non_l7_rows,
        "l7_rank_label_clue_rows": l7_rows,
        "input_response_rows": response_rows,
        "input_portfolio_rows": portfolio_rows,
        "pass_shards": pass_shards,
        "missing_field_shards": missing_shard_count,
        "top_clue_semantic_pair_share": top_pair_share,
        "shortlist_rows": int(len(shortlist)),
        "executes_search": False,
        "executes_numeric_probe": False,
        "authorizes_a7ls5_repair_and_followup_contract": decision.startswith("PASS_"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls4_manifest.json", manifest)

    report = [
        "# CRYPTO A7LS-4 COMPANY NUMERIC FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- clue_rows: {clue_rows}",
        f"- non_l7_clue_rows: {non_l7_rows}",
        f"- l7_rank_label_clue_rows: {l7_rows}",
        f"- response_rows: {response_rows}",
        f"- portfolio_rows: {portfolio_rows}",
        f"- pass_shards: {pass_shards}",
        f"- missing_field_shards: {missing_shard_count}",
        f"- top_clue_semantic_pair_share: {top_pair_share:.3f}",
        f"- shortlist_rows: {len(shortlist)}",
        "",
        "## Clue By Label",
        "",
        clue_by_label.to_markdown(index=False) if not clue_by_label.empty else "_none_",
        "",
        "## Clue By Semantic Pair",
        "",
        clue_by_pair.to_markdown(index=False) if not clue_by_pair.empty else "_none_",
        "",
        "## Response Blockers",
        "",
        blocker_summary.to_markdown(index=False) if not blocker_summary.empty else "_none_",
        "",
        "## Missing Field Shards",
        "",
        missing[["shard", "decision", "blockers", "root_cause", "missing_field_family"]].to_markdown(index=False)
        if not missing.empty
        else "_none_",
        "",
        "## Shortlist",
        "",
        shortlist.head(20).to_markdown(index=False) if not shortlist.empty else "_none_",
        "",
        "## Authorization",
        "",
        "- Forensic only.",
        "- Does not authorize search, alpha proof, shadow, paper, or live.",
        "- If passed, only authorizes drafting A7LS-5 repair/follow-up contract.",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
