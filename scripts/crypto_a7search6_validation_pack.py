from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.crypto_a7reward1_portfolio_reward_model import expression_fields  # noqa: E402


DATE = "20260702"
STAGE = "A7SEARCH6-VALIDATION-PACK"
DEFAULT_ACCEPTED_ROOT = REPO / "runtime" / "a7search6_selected_full_reward_r1_aggregate_20260702"
DEFAULT_RUNTIME = REPO / "runtime" / "a7search6_validation_pack_20260702"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SEARCH6_VALIDATION_PACK_20260702.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 40) -> str:
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


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size <= 2:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def accepted_rows(accepted_root: Path) -> pd.DataFrame:
    path = accepted_root / "a7v3s0_reward_accepted_enriched.csv"
    frame = read_csv_or_empty(path)
    if frame.empty:
        raise RuntimeError(f"missing or empty accepted queue: {path}")
    for col in ["min_oos_floor_sortino", "min_oos_sortino", "recent_sortino", "train_sortino"]:
        if col in frame.columns:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    return frame.sort_values(
        ["min_oos_floor_sortino", "min_oos_sortino", "recent_sortino"],
        ascending=False,
    )


def compressed_mechanisms(accepted: pd.DataFrame) -> pd.DataFrame:
    sort_cols = ["min_oos_floor_sortino", "min_oos_sortino", "recent_sortino"]
    ranked = accepted.sort_values(sort_cols, ascending=False).copy()
    compressed = ranked.drop_duplicates("blueprint_id", keep="first").copy()
    compressed["source_rank"] = range(1, len(compressed) + 1)
    compressed["formula_fields"] = compressed["formula"].fillna(compressed.get("expression", "")).astype(str).map(
        lambda expr: "|".join(expression_fields(expr))
    )
    return compressed


def field_risk(field: str) -> tuple[str, str]:
    if field in {"funding_rate_delta_state_24h", "funding_rate_state_last_ffill_8h", "funding_rate_update_age_hours"}:
        return "event_dense_funding", "requires funding publication timestamp / ffill-age proof"
    if "funding" in field:
        return "funding", "requires exchange funding event timestamp proof"
    if "open_interest" in field:
        return "open_interest", "requires OI snapshot timestamp and no same-bar fill proof"
    if "long_short" in field or "position" in field:
        return "positioning", "requires account/position ratio publication lag proof"
    if "taker" in field:
        return "taker_flow", "bar-close flow field; must execute after bar close"
    if "basis" in field or "premium" in field or "mark" in field or "index" in field:
        return "basis_premium", "mark/index/premium bar-close alignment proof required"
    if "liquidity" in field or "volume" in field:
        return "liquidity", "bar-close liquidity field; must execute after bar close"
    if "regime" in field or "state" in field:
        return "regime_state", "state thresholds must be train-only or rolling-past"
    return "generic_numeric", "needs source contract lookup"


def field_risk_table(compressed: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for rec in compressed.to_dict("records"):
        fields = expression_fields(str(rec.get("formula") or rec.get("expression") or ""))
        for field in fields:
            family, note = field_risk(field)
            rows.append(
                {
                    "source_blueprint_id": rec["blueprint_id"],
                    "source_rank": rec["source_rank"],
                    "field": field,
                    "field_family": family,
                    "timing_risk_note": note,
                }
            )
    return pd.DataFrame(rows).drop_duplicates().sort_values(["source_rank", "field"]) if rows else pd.DataFrame()


def add_row(rows: list[dict[str, Any]], source: dict[str, Any], suffix: str, expr: str, group: str, note: str) -> None:
    source_id = str(source["blueprint_id"])
    rows.append(
        {
            "blueprint_id": f"a7search6_vp_{source_id}_{suffix}",
            "production_key": f"a7search6_vp_{source_id}_{suffix}",
            "source_blueprint_id": source_id,
            "source_horizon_h": source.get("horizon_h", ""),
            "source_rank": source.get("source_rank", ""),
            "source_min_oos_floor_sortino": source.get("min_oos_floor_sortino", ""),
            "source_min_oos_sortino": source.get("min_oos_sortino", ""),
            "source_recent_sortino": source.get("recent_sortino", ""),
            "semantic_pair": source.get("semantic_pair", ""),
            "motif": f"{source.get('motif', '')}_validation",
            "skeleton_key": suffix,
            "expression": expr,
            "validation_group": group,
            "validation_note": note,
            "candidate_role": "validation_ablation",
        }
    )


def validation_rows(compressed: pd.DataFrame, max_fields_per_formula: int = 3) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in compressed.to_dict("records"):
        expr = str(source.get("formula") or source.get("expression") or "")
        fields = sorted(expression_fields(expr))[:max_fields_per_formula]
        add_row(rows, source, "canonical", expr, "canonical", "accepted formula rerun")
        for field in fields:
            safe = field.replace("|", "_").replace(" ", "_")
            add_row(rows, source, f"single_csrank_{safe}", f"CSRank({field})", "single_leg", f"{field} cross-sectional rank only")
            add_row(rows, source, f"single_zscore_{safe}", f"ZScore({field})", "single_leg", f"{field} time-series z-score only")
            add_row(rows, source, f"single_tsrank_{safe}", f"TSRank({field},336)", "single_leg", f"{field} 336h TS rank only")
            add_row(rows, source, f"single_mean72_{safe}", f"Mean({field},72)", "single_leg", f"{field} 72h mean only")
        if len(fields) >= 2:
            left, right = fields[0], fields[1]
            add_row(rows, source, "pair_spread_rank", f"Sub(CSRank({left}),CSRank({right}))", "operator_neighbor", "rank spread of first two source fields")
            add_row(rows, source, "pair_mul_rank", f"Mul(CSRank({left}),CSRank({right}))", "operator_neighbor", "rank multiplication of first two source fields")
            add_row(rows, source, "pair_safe_div_rank", f"SafeDiv(CSRank({left}),Abs(CSRank({right})))", "operator_neighbor", "rank safe-div of first two source fields")
            add_row(rows, source, "pair_safe_div_rank_swapped", f"SafeDiv(CSRank({right}),Abs(CSRank({left})))", "operator_neighbor", "swapped rank safe-div of first two source fields")
        if expr.startswith("SafeDiv(") and "Abs(" in expr:
            add_row(rows, source, "operator_no_abs_text", expr.replace("Abs(", "(", 1), "operator_text_ablation", "remove first Abs wrapper textually")
        if expr.startswith("Mul("):
            add_row(rows, source, "operator_signed_sum_proxy", f"Add({fields[0]},{fields[1]})" if len(fields) >= 2 else expr, "operator_neighbor", "replace multiplication with additive proxy")
    return rows


def build_queue(accepted_root: Path, runtime: Path, max_fields_per_formula: int) -> Path:
    runtime.mkdir(parents=True, exist_ok=True)
    accepted = accepted_rows(accepted_root)
    compressed = compressed_mechanisms(accepted)
    risks = field_risk_table(compressed)
    queue = pd.DataFrame(validation_rows(compressed, max_fields_per_formula=max_fields_per_formula))
    queue = queue.drop_duplicates(["blueprint_id"], keep="first").reset_index(drop=True)

    compressed.to_csv(runtime / "a7search6_validation_compressed_mechanisms.csv", index=False)
    risks.to_csv(runtime / "a7search6_validation_field_timing_risk.csv", index=False)
    queue_path = runtime / "a7search6_validation_ablation_queue.csv"
    queue.to_csv(queue_path, index=False)
    group_summary = (
        queue.groupby("validation_group", dropna=False)
        .agg(candidates=("blueprint_id", "nunique"), source_blueprints=("source_blueprint_id", "nunique"))
        .reset_index()
        .sort_values(["validation_group"])
    )
    group_summary.to_csv(runtime / "a7search6_validation_queue_group_summary.csv", index=False)
    write_json(
        runtime / "a7search6_validation_build_manifest.json",
        {
            "stage": STAGE,
            "generated_at": now_utc(),
            "decision": "PASS_A7SEARCH6_VALIDATION_QUEUE_BUILT",
            "accepted_root": str(accepted_root),
            "runtime": str(runtime),
            "accepted_rows": int(accepted.shape[0]),
            "compressed_unique_blueprints": int(compressed["blueprint_id"].nunique()),
            "queue_rows": int(queue.shape[0]),
            "max_fields_per_formula": int(max_fields_per_formula),
            "authorizes_validation_reward": True,
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
        },
    )
    return queue_path


def summarize(runtime: Path, reward_aggregate_root: Path, report: Path) -> dict[str, Any]:
    queue = read_csv_or_empty(runtime / "a7search6_validation_ablation_queue.csv")
    compressed = read_csv_or_empty(runtime / "a7search6_validation_compressed_mechanisms.csv")
    risks = read_csv_or_empty(runtime / "a7search6_validation_field_timing_risk.csv")
    leaderboard = read_csv_or_empty(reward_aggregate_root / "a7v3s0_reward_candidate_leaderboard_all.csv")
    accepted = read_csv_or_empty(reward_aggregate_root / "a7v3s0_reward_accepted_enriched.csv")
    rejections = read_csv_or_empty(reward_aggregate_root / "a7v3s0_reward_rejections_enriched.csv")
    errors = read_csv_or_empty(reward_aggregate_root / "a7v3s0_reward_eval_errors_all.csv")
    manifest = json.loads((reward_aggregate_root / "a7v3s0_reward_sharded_aggregate_manifest.json").read_text(encoding="utf-8"))

    group_cols = ["blueprint_id", "source_blueprint_id", "validation_group", "validation_note", "source_rank", "source_min_oos_floor_sortino"]
    group_map = queue[group_cols].drop_duplicates("blueprint_id") if not queue.empty else pd.DataFrame(columns=group_cols)
    def attach(frame: pd.DataFrame) -> pd.DataFrame:
        if frame.empty or group_map.empty:
            return frame
        return frame.merge(group_map, on="blueprint_id", how="left")

    leaderboard = attach(leaderboard)
    accepted = attach(accepted)
    rejections = attach(rejections)

    accepted_summary = (
        accepted.groupby(["source_blueprint_id", "validation_group", "blueprint_id", "horizon_h"], dropna=False)
        .agg(
            rows=("blueprint_id", "count"),
            train_sortino=("train_sortino", "max"),
            validation_sortino=("validation_sortino", "max"),
            test_sortino=("test_sortino", "max"),
            recent_sortino=("recent_sortino", "max"),
            min_oos_floor_sortino=("min_oos_floor_sortino", "max"),
            stress_floor_sortino=("stress_floor_sortino", "max"),
            recent_shuffle_control_ratio=("recent_shuffle_control_ratio", "min"),
            formula=("formula", "first"),
        )
        .reset_index()
        .sort_values(["min_oos_floor_sortino", "recent_sortino"], ascending=False)
        if not accepted.empty
        else pd.DataFrame()
    )
    group_summary = (
        leaderboard.groupby("validation_group", dropna=False)
        .agg(
            candidates=("blueprint_id", "nunique"),
            accepted_rows=("gate_pass", lambda s: int(s.astype(bool).sum())),
            accepted_unique=("blueprint_id", lambda s: int(accepted.loc[accepted["blueprint_id"].isin(set(s)), "blueprint_id"].nunique()) if not accepted.empty else 0),
            max_recent_sortino=("recent_sortino", "max"),
            max_min_oos_floor_sortino=("min_oos_floor_sortino", "max"),
        )
        .reset_index()
        .sort_values(["accepted_rows", "max_min_oos_floor_sortino"], ascending=False)
        if not leaderboard.empty
        else pd.DataFrame()
    )

    source_rows = []
    for sid, src in queue.groupby("source_blueprint_id", dropna=False):
        acc = accepted[accepted["source_blueprint_id"].astype(str).eq(str(sid))] if not accepted.empty else pd.DataFrame()
        canonical = int(acc["validation_group"].eq("canonical").sum()) if not acc.empty else 0
        single = int(acc["validation_group"].eq("single_leg").sum()) if not acc.empty else 0
        neighbor = int(acc["validation_group"].isin(["operator_neighbor", "operator_text_ablation"]).sum()) if not acc.empty else 0
        if canonical > 0 and single == 0 and neighbor == 0:
            decision = "PASS_INCREMENTAL_INTERACTION_EVIDENCE"
        elif canonical > 0:
            decision = "HOLD_NON_UNIQUE_INFORMATION"
        else:
            decision = "HOLD_CANONICAL_DID_NOT_REPASS"
        source_rows.append(
            {
                "source_blueprint_id": sid,
                "source_rank": pd.to_numeric(src["source_rank"], errors="coerce").min(),
                "canonical_accepted_rows": canonical,
                "single_leg_accepted_rows": single,
                "operator_neighbor_accepted_rows": neighbor,
                "accepted_rows": int(acc.shape[0]),
                "decision": decision,
            }
        )
    source_decisions = pd.DataFrame(source_rows).sort_values(["decision", "source_rank"]) if source_rows else pd.DataFrame()

    incremental_count = int(source_decisions["decision"].eq("PASS_INCREMENTAL_INTERACTION_EVIDENCE").sum()) if not source_decisions.empty else 0
    non_unique_count = int(source_decisions["decision"].eq("HOLD_NON_UNIQUE_INFORMATION").sum()) if not source_decisions.empty else 0
    canonical_fail_count = int(source_decisions["decision"].eq("HOLD_CANONICAL_DID_NOT_REPASS").sum()) if not source_decisions.empty else 0
    if int(manifest.get("eval_error_rows", 0)) > 0 or not errors.empty:
        decision = "HOLD_A7SEARCH6_VALIDATION_EVAL_ERRORS"
    elif incremental_count > 0:
        decision = "PASS_A7SEARCH6_VALIDATION_HAS_INCREMENTAL_CANDIDATES"
    elif non_unique_count > 0:
        decision = "HOLD_A7SEARCH6_VALIDATION_NON_UNIQUE_INFORMATION"
    else:
        decision = "HOLD_A7SEARCH6_VALIDATION_CANONICAL_FAILED"

    accepted_summary.to_csv(runtime / "a7search6_validation_accepted_summary.csv", index=False)
    group_summary.to_csv(runtime / "a7search6_validation_group_summary.csv", index=False)
    source_decisions.to_csv(runtime / "a7search6_validation_source_decisions.csv", index=False)

    risk_summary = (
        risks.groupby(["field_family", "timing_risk_note"], dropna=False)
        .agg(fields=("field", "nunique"), source_blueprints=("source_blueprint_id", "nunique"))
        .reset_index()
        .sort_values(["source_blueprints", "fields"], ascending=False)
        if not risks.empty
        else pd.DataFrame()
    )
    risk_summary.to_csv(runtime / "a7search6_validation_field_timing_risk_summary.csv", index=False)

    out_manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "runtime": str(runtime),
        "report": str(report),
        "reward_aggregate_root": str(reward_aggregate_root),
        "queue_rows": int(queue.shape[0]),
        "compressed_unique_blueprints": int(compressed["blueprint_id"].nunique()) if not compressed.empty else 0,
        "reward_rows": int(manifest.get("reward_rows", 0)),
        "accepted_rows": int(manifest.get("accepted_rows", 0)),
        "accepted_unique_blueprints": int(manifest.get("accepted_unique_blueprints", 0)),
        "eval_error_rows": int(manifest.get("eval_error_rows", 0)),
        "incremental_source_count": incremental_count,
        "non_unique_source_count": non_unique_count,
        "canonical_failed_source_count": canonical_fail_count,
        "blind_june_status": "NOT_EXECUTED_REWARD_SPLIT_NOT_DEFINED_FOR_JUNE_2026",
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_next_search_seed_triage": decision.startswith("PASS_"),
        "outputs": {
            "compressed_mechanisms": str(runtime / "a7search6_validation_compressed_mechanisms.csv"),
            "validation_queue": str(runtime / "a7search6_validation_ablation_queue.csv"),
            "accepted_summary": str(runtime / "a7search6_validation_accepted_summary.csv"),
            "group_summary": str(runtime / "a7search6_validation_group_summary.csv"),
            "source_decisions": str(runtime / "a7search6_validation_source_decisions.csv"),
            "field_timing_risk": str(runtime / "a7search6_validation_field_timing_risk.csv"),
            "field_timing_risk_summary": str(runtime / "a7search6_validation_field_timing_risk_summary.csv"),
        },
    }
    write_json(runtime / "a7search6_validation_manifest.json", out_manifest)

    lines = [
        "# CRYPTO A7SEARCH6 Validation Pack 20260702",
        "",
        f"Generated: `{out_manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This validates whether A7SEARCH6 accepted candidates have incremental evidence over single-leg and nearby-operator baselines. It is not alpha proof and does not authorize shadow, paper, live, or production portfolio construction.",
        "",
        "## Counts",
        "",
        f"- compressed_unique_blueprints: `{out_manifest['compressed_unique_blueprints']}`",
        f"- validation_queue_rows: `{out_manifest['queue_rows']}`",
        f"- reward_rows: `{out_manifest['reward_rows']}`",
        f"- accepted_rows: `{out_manifest['accepted_rows']}`",
        f"- accepted_unique_blueprints: `{out_manifest['accepted_unique_blueprints']}`",
        f"- eval_error_rows: `{out_manifest['eval_error_rows']}`",
        f"- incremental_source_count: `{incremental_count}`",
        f"- non_unique_source_count: `{non_unique_count}`",
        f"- canonical_failed_source_count: `{canonical_fail_count}`",
        f"- blind_june_status: `{out_manifest['blind_june_status']}`",
        "",
        "## Validation Group Summary",
        "",
        md_table(group_summary, 30),
        "",
        "## Source Decisions",
        "",
        md_table(source_decisions, 40),
        "",
        "## Top Accepted Validation Rows",
        "",
        md_table(accepted_summary, 40),
        "",
        "## Field Timing Risk Summary",
        "",
        md_table(risk_summary, 30),
        "",
        "## Bias Audit Notes",
        "",
        "- Discovery status: replay/validation of A7SEARCH6 reward-selected candidates, not new blind discovery.",
        "- Cost model: inherited A7REWARD1 `cost_bps=5.0`.",
        "- Reward windows: train_2024, validation_2025H1, test_2025H2, recent_oos_2026JanApr, known_may2026_stress.",
        "- June 2026 blind check is not executed here because the current reward split function does not define a June holdout split.",
        "- Candidate acceptance remains a research gate only.",
        "",
        "## Outputs",
        "",
    ]
    for key, value in out_manifest["outputs"].items():
        lines.append(f"- `{key}`: `{value}`")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accepted-root", type=Path, default=DEFAULT_ACCEPTED_ROOT)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--reward-aggregate-root", type=Path, default=DEFAULT_RUNTIME / "reward_aggregate")
    parser.add_argument("--mode", choices=["build", "summarize"], default="build")
    parser.add_argument("--max-fields-per-formula", type=int, default=3)
    args = parser.parse_args()

    if args.mode == "build":
        queue_path = build_queue(args.accepted_root, args.runtime, args.max_fields_per_formula)
        print(json.dumps({"queue": str(queue_path), "runtime": str(args.runtime)}, indent=2, sort_keys=True))
    else:
        manifest = summarize(args.runtime, args.reward_aggregate_root, args.report)
        print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
