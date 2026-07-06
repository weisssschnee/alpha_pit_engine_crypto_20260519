from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE6_RUNTIME = REPO / "runtime" / "a7source6_incremental_validation_pack_20260706"
DEFAULT_SOURCE6_REWARD = REPO / "runtime" / "a7source6_incremental_validation_reward_aggregate_20260706"
DEFAULT_RUNTIME = REPO / "runtime" / "a7source7_seed_triage_20260706"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SOURCE7_SEED_TRIAGE_AND_NEXT_SEARCH_CONTRACT_20260706.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def repo_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


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


def build_seed_queue(
    accepted: pd.DataFrame, decisions: pd.DataFrame, reward_accepted: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if accepted.empty:
        return pd.DataFrame(), decisions.copy()
    if not reward_accepted.empty and "blueprint_id" in reward_accepted.columns:
        meta_cols = [col for col in ["blueprint_id", "semantic_pair", "motif", "skeleton_key", "expression"] if col in reward_accepted.columns]
        meta = reward_accepted[meta_cols].drop_duplicates("blueprint_id") if meta_cols else pd.DataFrame()
        if not meta.empty:
            accepted = accepted.merge(meta, on="blueprint_id", how="left", suffixes=("", "_reward"))
            for col in ["semantic_pair", "motif", "skeleton_key", "expression"]:
                reward_col = f"{col}_reward"
                if col not in accepted.columns and reward_col in accepted.columns:
                    accepted[col] = accepted[reward_col]
                elif reward_col in accepted.columns:
                    accepted[col] = accepted[col].fillna(accepted[reward_col])
    decision_cols = ["source_blueprint_id", "decision"]
    decision_map = decisions[decision_cols].drop_duplicates("source_blueprint_id") if set(decision_cols).issubset(decisions.columns) else pd.DataFrame(columns=decision_cols)
    seeds = accepted.merge(decision_map, on="source_blueprint_id", how="left")
    seeds = seeds[seeds["decision"].astype(str).eq("PASS_INCREMENTAL_INTERACTION_EVIDENCE")].copy()
    seeds = seeds.sort_values(["min_oos_floor_sortino", "recent_sortino"], ascending=False).reset_index(drop=True)
    if seeds.empty:
        return seeds, decisions.copy()
    seeds["seed_rank"] = range(1, len(seeds) + 1)
    seeds["seed_role"] = "source_lag_proven_incremental_seed"
    seeds["allowed_next_use"] = "small_mechanism_expansion_and_control_strict_search"
    seeds["blocked_next_use"] = "alpha_proof|shadow|paper|live|single_leg_promotion"
    seeds["required_next_checks"] = (
        "formula_identity_lock|source_lag_inheritance|single_leg_recheck|operator_neighbor_recheck|"
        "walk_forward_2026_holdout|capacity_turnover_realism|family_cap"
    )
    failed = decisions[~decisions["source_blueprint_id"].astype(str).isin(set(seeds["source_blueprint_id"].astype(str)))].copy() if not decisions.empty else pd.DataFrame()
    return seeds, failed


def group_summary(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    if frame.empty or key not in frame.columns:
        return pd.DataFrame(columns=[key, "count", "share"])
    out = frame.groupby(key, dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    total = max(1, int(out["count"].sum()))
    out["share"] = out["count"] / total
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source6-runtime", type=Path, default=DEFAULT_SOURCE6_RUNTIME)
    parser.add_argument("--source6-reward", type=Path, default=DEFAULT_SOURCE6_REWARD)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    args.runtime.mkdir(parents=True, exist_ok=True)
    source6_manifest = read_json(args.source6_runtime / "a7source6_validation_manifest.json")
    accepted = read_csv(args.source6_runtime / "a7source6_validation_accepted_summary.csv")
    decisions = read_csv(args.source6_runtime / "a7source6_validation_source_decisions.csv")
    reward_manifest = read_json(args.source6_reward / "a7v3s0_reward_sharded_aggregate_manifest.json")
    reward_accepted = read_csv(args.source6_reward / "a7v3s0_reward_accepted_enriched.csv")

    seeds, failed = build_seed_queue(accepted, decisions, reward_accepted)
    pair_summary = group_summary(seeds, "semantic_pair")
    motif_summary = group_summary(seeds, "motif")
    horizon_summary = group_summary(seeds, "horizon_h")

    outputs = {
        "promoted_seed_queue": args.runtime / "a7source7_promoted_seed_queue.csv",
        "failed_or_blocked": args.runtime / "a7source7_failed_or_blocked_sources.csv",
        "semantic_pair_summary": args.runtime / "a7source7_semantic_pair_summary.csv",
        "motif_summary": args.runtime / "a7source7_motif_summary.csv",
        "horizon_summary": args.runtime / "a7source7_horizon_summary.csv",
        "search_constraints": args.runtime / "a7source7_search_constraints.json",
    }
    seeds.to_csv(outputs["promoted_seed_queue"], index=False)
    failed.to_csv(outputs["failed_or_blocked"], index=False)
    pair_summary.to_csv(outputs["semantic_pair_summary"], index=False)
    motif_summary.to_csv(outputs["motif_summary"], index=False)
    horizon_summary.to_csv(outputs["horizon_summary"], index=False)

    constraints = {
        "stage": "A7SOURCE7-SEED-TRIAGE",
        "allowed": [
            "mechanism-local expansion around promoted seeds",
            "formula identity locked rerun",
            "source-lag inherited validation only when formula+horizon matches",
            "strict reward gate with controls",
        ],
        "blocked": [
            "alpha proof",
            "shadow/paper/live",
            "single-leg promotion",
            "large raw search without family caps",
            "source-lag proof inheritance for mutated formulas",
        ],
        "family_caps": {
            "max_open_interest_family_share": 0.60,
            "max_semantic_pair_share": 0.40,
            "require_non_open_interest_new_seed_attempts": True,
        },
        "next_required": [
            "A7SOURCE8 formula identity and source-lag inheritance lock",
            "A7SEARCH8 controlled seed expansion with caps",
            "A7VAL walk-forward 2026 holdout and execution realism",
        ],
    }
    write_json(outputs["search_constraints"], constraints)

    decision = "PASS_A7SOURCE7_SEED_TRIAGE_READY" if not seeds.empty else "HOLD_A7SOURCE7_NO_PROMOTED_SEEDS"
    manifest = {
        "stage": "A7SOURCE7-SEED-TRIAGE",
        "generated_at": now_utc(),
        "decision": decision,
        "source6_decision": source6_manifest.get("decision", ""),
        "source6_reward_decision": reward_manifest.get("decision", ""),
        "runtime": str(args.runtime),
        "runtime_relative": repo_relative(args.runtime),
        "report": str(args.report),
        "report_relative": repo_relative(args.report),
        "promoted_seed_count": int(seeds.shape[0]),
        "failed_or_blocked_count": int(failed.shape[0]),
        "authorizes_seed_expansion": not seeds.empty,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "outputs": {key: str(value) for key, value in outputs.items()},
        "outputs_relative": {key: repo_relative(value) for key, value in outputs.items()},
    }
    write_json(args.runtime / "a7source7_seed_triage_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SOURCE7 Seed Triage And Next Search Contract",
        "",
        f"Generated: `{manifest['generated_at']}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7SOURCE7 promotes only A7SOURCE6 survivors whose canonical formulas re-pass strict reward while single-leg and operator-neighbor controls do not pass.",
        "",
        "## Counts",
        "",
        f"- promoted_seed_count: `{manifest['promoted_seed_count']}`",
        f"- failed_or_blocked_count: `{manifest['failed_or_blocked_count']}`",
        f"- source6_decision: `{manifest['source6_decision']}`",
        f"- source6_reward_decision: `{manifest['source6_reward_decision']}`",
        "",
        "## Promoted Seeds",
        "",
        md_table(seeds, 20),
        "",
        "## Failed Or Blocked",
        "",
        md_table(failed, 20),
        "",
        "## Semantic Pair Summary",
        "",
        md_table(pair_summary, 20),
        "",
        "## Search Constraints",
        "",
        "```json",
        json.dumps(constraints, indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "- Authorizes controlled seed expansion only.",
        "- Does not authorize alpha proof, shadow, paper, live, or deployment.",
    ]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
