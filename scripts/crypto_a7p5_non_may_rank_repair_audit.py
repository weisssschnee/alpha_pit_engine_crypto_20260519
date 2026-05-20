from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "runtime"
REPORT_DIR = ROOT / "reports"
CHECKPOINT_ID = "A7P3_W2PILOT"
SOURCE_DIR = RUNTIME_DIR / f"a7o_l1_checkpoint_{CHECKPOINT_ID}"
SOURCE_PREFIX = f"a7o_l1_checkpoint_{CHECKPOINT_ID}"
OUT_DIR = RUNTIME_DIR / "a7p5_non_may_rank_repair_audit"
DATE_TAG = "20260521"

STRESS_FOLDS = [
    "F11_cross_symbol_crowding",
    "F4_basis_dislocation",
    "F1_high_realized_vol",
    "F3_high_liquidity_high_vol",
]
SERIES_SOURCES = {
    "raw_10bp": "fold_replay_metrics",
    "residual_vs_funding_10bp": "residual_fold_metrics",
    "residual_vs_core4_10bp": "residual_fold_metrics",
    "raw_20bp": "cost_lag_fold_metrics",
    "execution_lag_1bar_raw_10bp": "cost_lag_fold_metrics",
}


def utc_stamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    return df.head(max_rows).to_markdown(index=False)


def load_csv(stem: str) -> pd.DataFrame:
    return pd.read_csv(SOURCE_DIR / f"{SOURCE_PREFIX}_{stem}.csv")


def rank_decile_summary(df: pd.DataFrame, score_col: str) -> pd.DataFrame:
    ranked = df.copy()
    ranked["rank_order"] = ranked[score_col].rank(method="first", ascending=False)
    ranked["rank_decile"] = pd.qcut(ranked["rank_order"], 10, labels=False, duplicates="drop") + 1
    out = (
        ranked.groupby("rank_decile", dropna=False)
        .agg(
            rows=("candidate_id", "count"),
            post_may_eligible_count=("candidate_decision", lambda s: int((s == "A7O_PILOT_RESEARCH_CANDIDATE").sum())),
            may_vetoed_count=("candidate_decision", lambda s: int((s == "A7O_PILOT_MAY_VETOED_NEAR_MISS").sum())),
            median_score=(score_col, "median"),
            median_raw_may=("raw_10bp__fresh_forward_2026May", "median"),
            median_residual_funding_may=("residual_vs_funding_10bp__fresh_forward_2026May", "median"),
            median_raw_recent=("raw_10bp__recent_oos_2025H2_2026Apr", "median"),
        )
        .reset_index()
        .sort_values("rank_decile")
    )
    out["post_may_eligible_rate"] = out["post_may_eligible_count"] / out["rows"].clip(lower=1)
    out["score_name"] = score_col
    return out


def build_stress_score(deep: pd.DataFrame) -> pd.DataFrame:
    metrics = {
        "fold_replay_metrics": load_csv("fold_replay_metrics"),
        "residual_fold_metrics": load_csv("residual_fold_metrics"),
        "cost_lag_fold_metrics": load_csv("cost_lag_fold_metrics"),
    }
    score = deep[["candidate_id", "pilot_rank_score", "candidate_decision"]].copy()
    component_cols = []
    for series, source in SERIES_SOURCES.items():
        df = metrics[source]
        part = df[df["series"].eq(series) & df["fold_id"].isin(STRESS_FOLDS)].copy()
        by_candidate = (
            part.groupby("candidate_id", dropna=False)
            .agg(
                min_ann=("annualized_mean", "min"),
                median_ann=("annualized_mean", "median"),
                positive_rate=("annualized_mean", lambda s: float((s > 0).mean())),
                min_gross=("mean_gross_exposure", "min"),
                min_active_hours=("active_hour_count", "min"),
            )
            .reset_index()
        )
        rename = {c: f"{series}__stress_{c}" for c in by_candidate.columns if c != "candidate_id"}
        by_candidate = by_candidate.rename(columns=rename)
        score = score.merge(by_candidate, on="candidate_id", how="left")
        component_cols.append(f"{series}__stress_min_ann")
        component_cols.append(f"{series}__stress_positive_rate")

    min_cols = [c for c in score.columns if c.endswith("__stress_min_ann")]
    positive_cols = [c for c in score.columns if c.endswith("__stress_positive_rate")]
    score["stress_analog_min_ann"] = score[min_cols].min(axis=1)
    score["stress_analog_positive_rate"] = score[positive_cols].mean(axis=1)
    score["stress_analog_score"] = score["stress_analog_min_ann"] + 0.25 * score["stress_analog_positive_rate"]
    return score


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_stamp()
    deep = load_csv("deep_audit_scoreboard")
    manifest = json.loads((SOURCE_DIR / f"{SOURCE_PREFIX}_manifest.json").read_text(encoding="utf-8"))

    stress_score = build_stress_score(deep)
    scored = deep.merge(stress_score.drop(columns=["pilot_rank_score", "candidate_decision"]), on="candidate_id", how="left")
    scored.to_csv(OUT_DIR / "a7p5_candidate_stress_analog_scores.csv", index=False)

    original_deciles = rank_decile_summary(scored, "pilot_rank_score")
    repaired_deciles = rank_decile_summary(scored, "stress_analog_score")
    original_deciles.to_csv(OUT_DIR / "a7p5_original_rank_decile_alignment.csv", index=False)
    repaired_deciles.to_csv(OUT_DIR / "a7p5_stress_analog_rank_decile_alignment.csv", index=False)

    top_original = float(original_deciles.loc[original_deciles["rank_decile"].eq(1), "post_may_eligible_rate"].iloc[0])
    top_repaired = float(repaired_deciles.loc[repaired_deciles["rank_decile"].eq(1), "post_may_eligible_rate"].iloc[0])
    overall_rate = float((scored["candidate_decision"] == "A7O_PILOT_RESEARCH_CANDIDATE").mean())
    blockers = []
    if top_repaired <= top_original:
        blockers.append("stress_analog_top_decile_not_better_than_original")
    if top_repaired < overall_rate:
        blockers.append("stress_analog_top_decile_below_overall_rate")

    decision = "PASS_A7P5_NON_MAY_STRESS_ANALOG_HAS_SIGNAL" if not blockers else "HOLD_A7P5_NON_MAY_STRESS_ANALOG_WEAK"
    payload = {
        "generated_at": now,
        "decision": decision,
        "source_checkpoint": CHECKPOINT_ID,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_new_search": False,
        "authorizes_full_l1": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "stress_folds": STRESS_FOLDS,
        "score_uses_may": False,
        "may_policy": manifest.get("may_policy", {}),
        "blockers": blockers,
        "metrics": {
            "overall_post_may_eligible_rate": overall_rate,
            "original_top_decile_post_may_eligible_rate": top_original,
            "stress_analog_top_decile_post_may_eligible_rate": top_repaired,
        },
        "outputs": {
            "candidate_scores": str(OUT_DIR / "a7p5_candidate_stress_analog_scores.csv"),
            "original_rank_deciles": str(OUT_DIR / "a7p5_original_rank_decile_alignment.csv"),
            "stress_analog_rank_deciles": str(OUT_DIR / "a7p5_stress_analog_rank_decile_alignment.csv"),
        },
    }
    write_json(OUT_DIR / "a7p5_decision_record.json", payload)

    report = [
        "# Crypto A7P-5 Non-May Rank Repair Audit",
        "",
        f"- generated_at: `{now}`",
        f"- source_checkpoint: `{CHECKPOINT_ID}`",
        f"- decision: `{decision}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        f"- blockers: `{blockers}`",
        "",
        "## Purpose",
        "",
        "A7P-5 tests a non-May stress-analog rank computed only from difficult validation/recent fold metrics. May is used only after ranking for attribution.",
        "",
        "## Metrics",
        "",
        table(pd.DataFrame([payload["metrics"]])),
        "",
        "## Original Rank Deciles",
        "",
        table(original_deciles),
        "",
        "## Stress-Analog Rank Deciles",
        "",
        table(repaired_deciles),
        "",
        "## Interpretation",
        "",
        "This audit does not authorize new search. A PASS only means a non-May stress-analog score has directional information worth converting into a future objective contract. A HOLD means rank repair needs a different non-May proxy or the W2 registry remains too weak.",
    ]
    (REPORT_DIR / f"CRYPTO_A7P5_NON_MAY_RANK_REPAIR_AUDIT_{DATE_TAG}.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
