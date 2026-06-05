from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ls6_deep_followup_queue_contract"
REPORT = REPO / "reports" / "CRYPTO_A7LS6_DEEP_FOLLOWUP_QUEUE_CONTRACT_20260605.md"
A7LS5_AGG = REPO / "runtime" / "a7ls5_company_result_aggregate" / "a7ls5_aggregate_manifest.json"
A7LS5_SHORTLIST = REPO / "runtime" / "a7ls5_company_result_aggregate" / "a7ls5_non_l7_shortlist.csv"
A7LS5_CLUES = REPO / "runtime" / "a7ls5_company_result_aggregate" / "a7ls5_non_l7_numeric_clues.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def digest(text: str, n: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def skeleton_key(expr: str) -> str:
    return "skel_" + digest("".join("x" if ch.isalnum() else ch for ch in expr), 16)


def production_key(expr: str) -> str:
    return "prod_" + digest(expr, 16)


def add(rows: list[dict[str, Any]], lane: str, family: str, pair: str, motif: str, expr: str, seed_id: str, priority: int) -> None:
    rows.append(
        {
            "a7ls_arm": lane,
            "followup_family": family,
            "semantic_pair": pair,
            "motif": motif,
            "blueprint_id": "a7ls6_" + digest(f"{lane}|{family}|{motif}|{expr}", 16),
            "source_seed_id": seed_id,
            "source_priority_rank": priority,
            "expression": expr,
            "skeleton_key": skeleton_key(expr),
            "production_key": production_key(expr),
            "selected_for_deep_numeric": True,
            "uses_may": False,
            "notes": "A7LS6 deeper numeric follow-up queue; no search authorization.",
        }
    )


def seed_table() -> pd.DataFrame:
    frames = []
    for path, label in [(A7LS5_SHORTLIST, "A7LS5_shortlist"), (A7LS5_CLUES, "A7LS5_all_clues")]:
        df = read_csv(path)
        if not df.empty:
            df["source_stage"] = label
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    seeds = pd.concat(frames, ignore_index=True)
    seeds = seeds[seeds["label_family"].astype(str).ne("L7_ranked_future_return")].copy()
    for col in ["control_ratio_premay_max", "cost10_recent_oriented", "one_bar_lag_recent_oriented", "robust_min_tstat_floor", "followup_score"]:
        if col in seeds.columns:
            seeds[col] = pd.to_numeric(seeds[col], errors="coerce")
    score_cols = [col for col in ["followup_score", "cost10_recent_oriented", "one_bar_lag_recent_oriented", "robust_min_tstat_floor"] if col in seeds.columns]
    seeds["priority_score"] = 0.0
    for col in score_cols:
        seeds["priority_score"] += seeds[col].fillna(0.0)
    if "control_ratio_premay_max" in seeds.columns:
        seeds["priority_score"] -= seeds["control_ratio_premay_max"].fillna(1.0) * 50.0
    return seeds.sort_values(["semantic_pair", "priority_score", "blueprint_id"], ascending=[True, False, True]).drop_duplicates(["blueprint_id", "label_family", "label_horizon_h"])


def basis_lane(rows: list[dict[str, Any]], seed_id: str, priority: int) -> None:
    fields = ["mark_index_basis_bps", "mark_trade_basis_bps", "premium_close_bps", "basis_abs_168h", "premium_abs_168h"]
    windows = [1, 2, 4, 8, 12, 24, 48, 72, 168, 336]
    for field in fields:
        for w in windows:
            add(rows, "A7LS6_A", "basis_deep", "basis_premium_like", "delta", f"Delta({field},{w})", seed_id, priority)
            add(rows, "A7LS6_A", "basis_deep", "basis_premium_like", "zmean", f"ZScore(Mean({field},{w}))", seed_id, priority)
            add(rows, "A7LS6_A", "basis_deep", "basis_premium_like", "rank", f"CSRank({field})", seed_id, priority)
        for short, long in [(1, 24), (2, 48), (4, 72), (8, 168), (24, 336)]:
            add(rows, "A7LS6_A", "basis_deep", "basis_premium_like", "spread_short_long", f"Sub(Mean({field},{short}),Mean({field},{long}))", seed_id, priority)
    for left in ["mark_index_basis_bps", "mark_trade_basis_bps", "premium_close_bps"]:
        for right in ["funding_rate", "realized_vol_168h", "liquidity_rank_active_universe", "volume_volatility_ratio_168h"]:
            for w in [4, 12, 24, 72, 168]:
                add(rows, "A7LS6_A", "basis_deep", f"basis_premium_like|{right}", "typed_gate", f"Mul(ZScore(Mean({left},{w})),Sign(ZScore(Mean({right},{w}))))", seed_id, priority)
                add(rows, "A7LS6_A", "basis_deep", f"basis_premium_like|{right}", "typed_interaction", f"Mul(Delta({left},{w}),ZScore(Mean({right},{w})))", seed_id, priority)


def listing_lane(rows: list[dict[str, Any]], seed_id: str, priority: int) -> None:
    fields = ["listing_age_days", "log1p_listing_age_days", "sqrt_listing_age_days", "age_percentile_active_universe", "age_x_liquidity", "age_x_volatility", "age_x_funding_abs"]
    partners = ["liquidity_rank_active_universe", "realized_vol_168h", "basis_abs_168h", "premium_abs_168h", "funding_rate_abs_168h"]
    for field in fields:
        for w in [24, 72, 168, 336, 720]:
            add(rows, "A7LS6_B", "listing_lifecycle_deep", "listing_age_like", "level", field, seed_id, priority)
            add(rows, "A7LS6_B", "listing_lifecycle_deep", "listing_age_like", "zmean", f"ZScore(Mean({field},{w}))", seed_id, priority)
            add(rows, "A7LS6_B", "listing_lifecycle_deep", "listing_age_like", "rank", f"CSRank({field})", seed_id, priority)
    for left in ["age_x_volatility", "age_x_liquidity", "age_percentile_active_universe"]:
        for right in partners:
            for w in [24, 72, 168, 336]:
                add(rows, "A7LS6_B", "listing_lifecycle_deep", "listing_age_like|regime_state", "typed_gate", f"Mul(ZScore(Mean({left},{w})),Sign(ZScore(Mean({right},{w}))))", seed_id, priority)


def volatility_lane(rows: list[dict[str, Any]], seed_id: str, priority: int) -> None:
    fields = ["realized_vol_24h", "realized_vol_72h", "realized_vol_168h", "volume_volatility_ratio_168h"]
    partners = ["mark_index_basis_bps", "premium_close_bps", "liquidity_rank_active_universe", "age_percentile_active_universe"]
    for field in fields:
        for w in [1, 4, 12, 24, 72, 168, 336]:
            add(rows, "A7LS6_C", "volatility_relative_deep", "volatility_like", "zmean", f"ZScore(Mean({field},{w}))", seed_id, priority)
            add(rows, "A7LS6_C", "volatility_relative_deep", "volatility_like", "delta", f"Delta({field},{w})", seed_id, priority)
            add(rows, "A7LS6_C", "volatility_relative_deep", "volatility_like", "rank", f"CSRank({field})", seed_id, priority)
    for left in fields:
        for right in partners:
            for w in [24, 72, 168]:
                add(rows, "A7LS6_C", "volatility_relative_deep", f"volatility_like|{right}", "typed_gate", f"Mul(ZScore(Mean({left},{w})),Sign(ZScore(Mean({right},{w}))))", seed_id, priority)


def oi_lane(rows: list[dict[str, Any]], seed_id: str, priority: int) -> None:
    fields = ["open_interest_last", "open_interest_value_last", "global_long_short_account_ratio_last", "top_long_short_account_ratio_last", "top_long_short_position_ratio_last", "taker_buy_sell_volume_ratio_last"]
    partners = ["trade_return_24h", "mark_index_basis_bps", "premium_close_bps", "funding_rate", "realized_vol_168h"]
    for field in fields:
        for w in [1, 4, 12, 24, 72, 168, 336]:
            add(rows, "A7LS6_D", "oi_positioning_reserved_deep", "open_interest_like|positioning_like", "delta", f"Delta({field},{w})", seed_id, priority)
            add(rows, "A7LS6_D", "oi_positioning_reserved_deep", "open_interest_like|positioning_like", "zmean", f"ZScore(Mean({field},{w}))", seed_id, priority)
            add(rows, "A7LS6_D", "oi_positioning_reserved_deep", "open_interest_like|positioning_like", "rank", f"CSRank({field})", seed_id, priority)
        for right in partners:
            for w in [4, 24, 72, 168]:
                add(rows, "A7LS6_D", "oi_positioning_reserved_deep", f"open_interest_like|{right}", "typed_interaction", f"Mul(Delta({field},{w}),ZScore(Mean({right},{w})))", seed_id, priority)
                add(rows, "A7LS6_D", "oi_positioning_reserved_deep", f"open_interest_like|{right}", "typed_gate", f"Mul(ZScore(Mean({field},{w})),Sign(ZScore(Mean({right},{w}))))", seed_id, priority)


def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    auth = read_json(A7LS5_AGG)
    seeds = seed_table()
    if seeds.empty:
        raise SystemExit("missing A7LS5 non-L7 seeds")

    rows: list[dict[str, Any]] = []
    for i, seed in enumerate(seeds.to_dict("records")):
        pair = str(seed.get("semantic_pair", ""))
        seed_id = str(seed.get("blueprint_id", f"seed_{i}"))
        priority = i
        if "basis_premium_like" in pair:
            basis_lane(rows, seed_id, priority)
        if "listing_age_like" in pair:
            listing_lane(rows, seed_id, priority)
        if "volatility_like" in pair:
            volatility_lane(rows, seed_id, priority)
        if "open_interest_like" in pair or "positioning_like" in pair:
            oi_lane(rows, seed_id, priority)

    # Keep explicit non-basis exploratory axes even if A7LS5 mostly found basis clues.
    listing_lane(rows, "a7ls6_reserved_listing_axis", 100000)
    volatility_lane(rows, "a7ls6_reserved_volatility_axis", 100001)
    oi_lane(rows, "a7ls6_reserved_oi_positioning_axis", 100002)

    full = pd.DataFrame(rows).drop_duplicates("blueprint_id").copy()
    caps = {
        "basis_deep": 384,
        "listing_lifecycle_deep": 192,
        "volatility_relative_deep": 192,
        "oi_positioning_reserved_deep": 192,
    }
    parts = []
    for family, cap in caps.items():
        sub = full[full["followup_family"].eq(family)].copy()
        parts.append(sub.sort_values(["source_priority_rank", "semantic_pair", "motif", "blueprint_id"]).head(cap))
    queue = pd.concat(parts, ignore_index=True).drop_duplicates("blueprint_id").copy()
    queue = queue.sort_values(["followup_family", "source_priority_rank", "semantic_pair", "blueprint_id"]).reset_index(drop=True)
    rows_per_shard = 64
    queue["company_numeric_shard"] = [f"a7ls6_s{i // rows_per_shard:03d}" for i in range(len(queue))]
    queue["checkpoint_key"] = queue["company_numeric_shard"] + "::" + queue["blueprint_id"]

    shard_plan = queue.groupby("company_numeric_shard", dropna=False).agg(rows=("blueprint_id", "size"), family_count=("followup_family", "nunique"), semantic_pair_count=("semantic_pair", "nunique"), motif_count=("motif", "nunique")).reset_index()
    family_summary = queue.groupby("followup_family", dropna=False).agg(rows=("blueprint_id", "size"), semantic_pair_count=("semantic_pair", "nunique"), motif_count=("motif", "nunique"), skeleton_count=("skeleton_key", "nunique"), source_seed_count=("source_seed_id", "nunique")).reset_index().sort_values("rows", ascending=False)
    seed_summary = seeds.groupby(["semantic_pair", "label_family"], dropna=False).size().reset_index(name="seed_rows").sort_values("seed_rows", ascending=False)

    seeds.to_csv(RUNTIME / "a7ls6_seed_clue_registry.csv", index=False)
    full.to_csv(RUNTIME / "a7ls6_full_generated_deep_followup_pool.csv", index=False)
    queue.to_csv(RUNTIME / "a7ls6_company_numeric_queue.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ls6_company_shard_plan.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ls6_family_summary.csv", index=False)
    seed_summary.to_csv(RUNTIME / "a7ls6_seed_summary.csv", index=False)

    blockers: list[str] = []
    if auth.get("decision") != "PASS_A7LS5_COMPANY_NUMERIC_AGGREGATED_READY_FOR_A7LS6_DEEP_FOLLOWUP":
        blockers.append("a7ls5_aggregate_auth_not_ready")
    if len(queue) < 512:
        blockers.append("deep_queue_too_small")
    if int(family_summary.shape[0]) < 4:
        blockers.append("deep_queue_family_breadth_too_low")
    if int(shard_plan.shape[0]) < 8:
        blockers.append("deep_queue_shard_count_too_low")

    decision = "PASS_A7LS6_DEEP_FOLLOWUP_QUEUE_READY_FOR_COMPANY_NUMERIC_NO_SEARCH_AUTH" if not blockers else "HOLD_A7LS6_DEEP_FOLLOWUP_QUEUE_NOT_READY"
    manifest = {
        "stage": "A7LS-6",
        "generated_at": now_utc(),
        "decision": decision,
        "seed_rows": int(len(seeds)),
        "full_generated_pool_rows": int(len(full)),
        "company_numeric_queue_rows": int(len(queue)),
        "rows_per_shard": rows_per_shard,
        "company_shard_count": int(shard_plan.shape[0]),
        "followup_family_count": int(family_summary.shape[0]),
        "semantic_pair_count": int(queue["semantic_pair"].nunique()),
        "motif_count": int(queue["motif"].nunique()),
        "hours_per_split_target": 2160,
        "blockers": blockers,
        "source_seed_files": [str(A7LS5_SHORTLIST), str(A7LS5_CLUES)],
        "queue_path": str(RUNTIME / "a7ls6_company_numeric_queue.csv"),
        "shard_plan_path": str(RUNTIME / "a7ls6_company_shard_plan.csv"),
        "executes_generation": True,
        "executes_numeric_probe": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_company_numeric_probe": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls6_manifest.json", manifest)

    lines = [
        "# CRYPTO A7LS-6 DEEP FOLLOWUP QUEUE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- seed_rows: {len(seeds)}",
        f"- full_generated_pool_rows: {len(full)}",
        f"- company_numeric_queue_rows: {len(queue)}",
        f"- company_shard_count: {shard_plan.shape[0]}",
        f"- rows_per_shard: {rows_per_shard}",
        f"- target hours_per_split: {manifest['hours_per_split_target']}",
        f"- followup_family_count: {family_summary.shape[0]}",
        f"- semantic_pair_count: {queue['semantic_pair'].nunique()}",
        f"- motif_count: {queue['motif'].nunique()}",
        "",
        "## Seed Summary",
        "",
        md_table(seed_summary),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan, 60),
        "",
        "## Authorization",
        "",
        "- Authorizes company numeric deep follow-up only if decision is PASS.",
        "- Does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "- May is not used in generation, ranking, mutation, or selector scoring.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
