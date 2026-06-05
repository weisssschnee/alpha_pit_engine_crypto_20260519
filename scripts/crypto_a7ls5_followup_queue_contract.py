from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ls5_followup_queue_contract"
REPORT = REPO / "reports" / "CRYPTO_A7LS5_FOLLOWUP_QUEUE_CONTRACT_20260605.md"
A7LS4 = REPO / "runtime" / "a7ls4_company_numeric_forensic" / "a7ls4_non_l7_control_clean_shortlist.csv"
A7LS4R = REPO / "runtime" / "a7ls4r_company_retry_forensic" / "a7ls4r_retry_non_l7_numeric_clues.csv"
A7LS2_AUTH = REPO / "runtime" / "a7ls2_sharded_materialization_wave" / "a7ls2_manifest.json"


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


def skel(expr: str) -> str:
    return "skel_" + digest("".join(ch if not ch.isalnum() else "x" for ch in expr), 16)


def prod(expr: str) -> str:
    return "prod_" + digest(expr, 16)


def seed_rows() -> pd.DataFrame:
    frames = []
    first = read_csv(A7LS4)
    if not first.empty:
        first["source_stage"] = "A7LS4"
        frames.append(first)
    retry = read_csv(A7LS4R)
    if not retry.empty:
        retry["source_stage"] = "A7LS4R"
        frames.append(retry)
    if not frames:
        return pd.DataFrame()
    seeds = pd.concat(frames, ignore_index=True)
    seeds = seeds[seeds["label_family"].astype(str).ne("L7_ranked_future_return")].copy()
    seeds["control_ratio_premay_max"] = pd.to_numeric(seeds.get("control_ratio_premay_max"), errors="coerce")
    seeds["cost10_recent_oriented"] = pd.to_numeric(seeds.get("cost10_recent_oriented"), errors="coerce")
    seeds["one_bar_lag_recent_oriented"] = pd.to_numeric(seeds.get("one_bar_lag_recent_oriented"), errors="coerce")
    seeds["robust_min_tstat_floor"] = pd.to_numeric(seeds.get("robust_min_tstat_floor"), errors="coerce")
    seeds = seeds.sort_values(
        ["label_family", "semantic_pair", "control_ratio_premay_max", "blueprint_id"],
        ascending=[True, True, True, True],
    ).drop_duplicates(["blueprint_id", "label_family", "label_horizon_h"])
    return seeds


def add_candidate(rows: list[dict[str, Any]], arm: str, family: str, semantic_pair: str, motif: str, expression: str, source_seed: str, priority: str) -> None:
    blueprint_id = "a7ls5_" + digest(f"{arm}|{family}|{motif}|{expression}", 16)
    rows.append(
        {
            "a7ls_arm": arm,
            "followup_family": family,
            "semantic_pair": semantic_pair,
            "motif": motif,
            "blueprint_id": blueprint_id,
            "source_seed_id": source_seed,
            "source_priority": priority,
            "expression": expression,
            "skeleton_key": skel(expression),
            "production_key": prod(expression),
            "selected_for_followup_numeric": True,
            "uses_may": False,
            "notes": "A7LS5 follow-up numeric probe queue; not search authorization.",
        }
    )


def basis_variants(rows: list[dict[str, Any]], source_seed: str, priority: str) -> None:
    bases = ["mark_index_basis_bps", "mark_trade_basis_bps", "premium_close_bps"]
    gate_fields = ["mark_trade_basis_bps", "premium_close_bps", "mark_index_basis_bps"]
    windows = [1, 2, 4, 8, 12, 24, 72, 168]
    for field in bases:
        for w in windows:
            add_candidate(rows, "A7LS5_A", "basis_followup", "basis_premium_like", "single", f"Delta({field},{w})", source_seed, priority)
            add_candidate(rows, "A7LS5_A", "basis_followup", "basis_premium_like", "single", f"ZScore(Mean({field},{w}))", source_seed, priority)
            add_candidate(rows, "A7LS5_A", "basis_followup", "basis_premium_like", "single", f"TSRank({field},{w})", source_seed, priority)
        for short, long in [(1, 12), (2, 24), (4, 72), (12, 168), (24, 168)]:
            add_candidate(rows, "A7LS5_A", "basis_followup", "basis_premium_like", "spread_short_long", f"Sub(Mean({field},{short}),Mean({field},{long}))", source_seed, priority)
        for gate in gate_fields:
            for w in [1, 2, 4, 8, 12, 24]:
                add_candidate(rows, "A7LS5_A", "basis_followup", "basis_premium_like", "gated_sign", f"Mul(Delta({field},{w}),Sign({gate}))", source_seed, priority)
                add_candidate(rows, "A7LS5_A", "basis_followup", "basis_premium_like", "gated_sign", f"Mul({field},Sign(Mean({gate},{w})))", source_seed, priority)
                add_candidate(rows, "A7LS5_A", "basis_followup", "basis_premium_like", "gated_sign", f"Mul(ZScore(Mean({field},{w})),Sign(ZScore(Mean({gate},{w}))))", source_seed, priority)


def lifecycle_variants(rows: list[dict[str, Any]], source_seed: str, priority: str) -> None:
    fields = [
        "listing_age_days",
        "log1p_listing_age_days",
        "sqrt_listing_age_days",
        "age_percentile_active_universe",
        "age_x_liquidity",
        "age_x_volatility",
        "age_x_funding_abs",
    ]
    state_fields = ["liquidity_rank_active_universe", "realized_vol_168h", "funding_rate_abs_168h", "basis_abs_168h"]
    for field in fields:
        add_candidate(rows, "A7LS5_B", "listing_lifecycle_followup", "listing_age_like", "single", field, source_seed, priority)
        for w in [24, 72, 168, 336]:
            add_candidate(rows, "A7LS5_B", "listing_lifecycle_followup", "listing_age_like", "single", f"Mean({field},{w})", source_seed, priority)
            add_candidate(rows, "A7LS5_B", "listing_lifecycle_followup", "listing_age_like", "single", f"ZScore(Mean({field},{w}))", source_seed, priority)
            add_candidate(rows, "A7LS5_B", "listing_lifecycle_followup", "listing_age_like", "single", f"CSRank({field})", source_seed, priority)
    for left in ["age_x_volatility", "age_x_liquidity", "sqrt_listing_age_days"]:
        for right in state_fields:
            for w in [24, 72, 168]:
                add_candidate(rows, "A7LS5_B", "listing_lifecycle_followup", "listing_age_like|regime_state", "gated_sign", f"Mul(ZScore(Mean({left},{w})),Sign(ZScore(Mean({right},{w}))))", source_seed, priority)


def volatility_variants(rows: list[dict[str, Any]], source_seed: str, priority: str) -> None:
    fields = ["realized_vol_24h", "realized_vol_72h", "realized_vol_168h", "volume_volatility_ratio_168h"]
    gates = ["liquidity_rank_active_universe", "age_percentile_active_universe", "basis_abs_168h"]
    for field in fields:
        for w in [1, 4, 24, 72, 168]:
            add_candidate(rows, "A7LS5_C", "volatility_relative_followup", "volatility_like", "single", f"Mean({field},{w})", source_seed, priority)
            add_candidate(rows, "A7LS5_C", "volatility_relative_followup", "volatility_like", "single", f"ZScore(Mean({field},{w}))", source_seed, priority)
            add_candidate(rows, "A7LS5_C", "volatility_relative_followup", "volatility_like", "single", f"CSRank({field})", source_seed, priority)
        for gate in gates:
            for w in [24, 72, 168]:
                add_candidate(rows, "A7LS5_C", "volatility_relative_followup", "volatility_like|regime_state", "gated_sign", f"Mul(ZScore(Mean({field},{w})),Sign(ZScore(Mean({gate},{w}))))", source_seed, priority)


def oi_positioning_probe_variants(rows: list[dict[str, Any]], source_seed: str, priority: str) -> None:
    fields = [
        "open_interest_last",
        "open_interest_value_last",
        "global_long_short_account_ratio_last",
        "top_long_short_account_ratio_last",
        "top_long_short_position_ratio_last",
        "taker_buy_sell_volume_ratio_last",
    ]
    for field in fields:
        for w in [1, 4, 24, 72, 168]:
            add_candidate(rows, "A7LS5_D", "oi_positioning_control_probe", "open_interest_like|positioning_like", "single", f"Delta({field},{w})", source_seed, priority)
            add_candidate(rows, "A7LS5_D", "oi_positioning_control_probe", "open_interest_like|positioning_like", "single", f"ZScore(Mean({field},{w}))", source_seed, priority)
        for basis in ["mark_index_basis_bps", "premium_close_bps"]:
            for w in [4, 24, 72]:
                add_candidate(rows, "A7LS5_D", "oi_positioning_control_probe", "open_interest_like|basis_premium_like", "gated_sign", f"Mul(Delta({field},{w}),Sign(ZScore(Mean({basis},{w}))))", source_seed, priority)


def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    auth = read_json(A7LS2_AUTH)
    seeds = seed_rows()
    rows: list[dict[str, Any]] = []
    if seeds.empty:
        raise SystemExit("missing A7LS4/A7LS4R seed clues")

    for seed in seeds.to_dict("records"):
        source_seed = str(seed.get("blueprint_id", ""))
        pair = str(seed.get("semantic_pair", ""))
        label = str(seed.get("label_family", ""))
        control = float(seed.get("control_ratio_premay_max")) if pd.notna(seed.get("control_ratio_premay_max")) else 1.0
        priority = "high" if label in {"L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"} and control < 0.8 else "normal"
        if "basis_premium_like" in pair:
            basis_variants(rows, source_seed, priority)
        if "listing_age_like" in pair:
            lifecycle_variants(rows, source_seed, priority)
        if "volatility_like" in pair:
            volatility_variants(rows, source_seed, priority)
        if "open_interest_like" in pair:
            oi_positioning_probe_variants(rows, source_seed, priority)

    # Always reserve one raw-axis lane so follow-up does not collapse into basis only.
    oi_positioning_probe_variants(rows, "a7ls5_raw_axis_reserved", "reserve")
    lifecycle_variants(rows, "a7ls5_lifecycle_reserved", "reserve")
    volatility_variants(rows, "a7ls5_volatility_reserved", "reserve")

    queue = pd.DataFrame(rows).drop_duplicates("blueprint_id").copy()
    # Balanced cap by family. Keep the queue substantial but bounded for company numeric.
    family_caps = {
        "basis_followup": 256,
        "listing_lifecycle_followup": 192,
        "volatility_relative_followup": 160,
        "oi_positioning_control_probe": 128,
    }
    selected_parts = []
    for family, cap in family_caps.items():
        sub = queue[queue["followup_family"].eq(family)].copy()
        sub["priority_rank"] = sub["source_priority"].map({"high": 0, "normal": 1, "reserve": 2}).fillna(3)
        selected_parts.append(sub.sort_values(["priority_rank", "blueprint_id"]).head(cap))
    selected = pd.concat(selected_parts, ignore_index=True).drop_duplicates("blueprint_id").copy()
    selected = selected.sort_values(["followup_family", "source_priority", "blueprint_id"]).reset_index(drop=True)

    rows_per_shard = 64
    selected["company_numeric_shard"] = [f"a7ls5_s{i // rows_per_shard:03d}" for i in range(len(selected))]
    selected["checkpoint_key"] = selected["company_numeric_shard"] + "::" + selected["blueprint_id"]

    shard_plan = (
        selected.groupby("company_numeric_shard", dropna=False)
        .agg(
            rows=("blueprint_id", "size"),
            family_count=("followup_family", "nunique"),
            semantic_pair_count=("semantic_pair", "nunique"),
            motif_count=("motif", "nunique"),
        )
        .reset_index()
    )
    family_summary = (
        selected.groupby("followup_family", dropna=False)
        .agg(
            rows=("blueprint_id", "size"),
            semantic_pair_count=("semantic_pair", "nunique"),
            motif_count=("motif", "nunique"),
            skeleton_count=("skeleton_key", "nunique"),
            source_seed_count=("source_seed_id", "nunique"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    seed_summary = (
        seeds.groupby(["semantic_pair", "label_family"], dropna=False)
        .size()
        .reset_index(name="seed_rows")
        .sort_values("seed_rows", ascending=False)
    )

    seeds.to_csv(RUNTIME / "a7ls5_seed_clue_registry.csv", index=False)
    queue.to_csv(RUNTIME / "a7ls5_full_generated_followup_pool.csv", index=False)
    selected.to_csv(RUNTIME / "a7ls5_company_numeric_queue.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ls5_company_shard_plan.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ls5_family_summary.csv", index=False)
    seed_summary.to_csv(RUNTIME / "a7ls5_seed_summary.csv", index=False)

    blockers: list[str] = []
    if len(selected) < 256:
        blockers.append("followup_queue_too_small")
    if family_summary["followup_family"].nunique() < 3:
        blockers.append("followup_family_breadth_too_low")
    if auth.get("decision") != "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY":
        blockers.append("a7ls2_auth_not_ready")

    decision = (
        "PASS_A7LS5_FOLLOWUP_QUEUE_READY_FOR_COMPANY_NUMERIC_NO_SEARCH_AUTH"
        if not blockers
        else "HOLD_A7LS5_FOLLOWUP_QUEUE_NOT_READY"
    )
    manifest = {
        "stage": "A7LS-5",
        "generated_at": now_utc(),
        "decision": decision,
        "seed_rows": int(len(seeds)),
        "full_generated_pool_rows": int(len(queue)),
        "company_numeric_queue_rows": int(len(selected)),
        "rows_per_shard": rows_per_shard,
        "company_shard_count": int(shard_plan.shape[0]),
        "followup_family_count": int(family_summary["followup_family"].nunique()),
        "semantic_pair_count": int(selected["semantic_pair"].nunique()),
        "motif_count": int(selected["motif"].nunique()),
        "blockers": blockers,
        "source_seed_files": [str(A7LS4), str(A7LS4R)],
        "queue_path": str(RUNTIME / "a7ls5_company_numeric_queue.csv"),
        "shard_plan_path": str(RUNTIME / "a7ls5_company_shard_plan.csv"),
        "executes_generation": True,
        "executes_numeric_probe": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_company_numeric_probe": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls5_manifest.json", manifest)

    lines = [
        "# CRYPTO A7LS-5 FOLLOWUP QUEUE CONTRACT",
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
        f"- full_generated_pool_rows: {len(queue)}",
        f"- company_numeric_queue_rows: {len(selected)}",
        f"- company_shard_count: {shard_plan.shape[0]}",
        f"- followup_family_count: {family_summary['followup_family'].nunique()}",
        f"- semantic_pair_count: {selected['semantic_pair'].nunique()}",
        f"- motif_count: {selected['motif'].nunique()}",
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
        md_table(shard_plan, 40),
        "",
        "## Authorization",
        "",
        "- Authorizes company numeric probe only if decision is PASS.",
        "- Does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "- May is not used in generation or ranking.",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
