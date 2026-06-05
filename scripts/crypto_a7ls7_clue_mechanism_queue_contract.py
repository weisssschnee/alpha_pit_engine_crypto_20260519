from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ls7_clue_mechanism_queue_contract"
REPORT = REPO / "reports" / "CRYPTO_A7LS7_CLUE_MECHANISM_QUEUE_CONTRACT_20260605.md"
A7LS6_MANIFEST = REPO / "runtime" / "a7ls6_company_result_aggregate" / "a7ls6_aggregate_manifest.json"
A7LS6_CLUES = REPO / "runtime" / "a7ls6_company_result_aggregate" / "a7ls6_non_l7_numeric_clues.csv"
A7LS6_SHORTLIST = REPO / "runtime" / "a7ls6_company_result_aggregate" / "a7ls6_non_l7_shortlist.csv"


FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {"Mean", "ZScore", "Delta", "CSRank", "TSRank", "Mul", "Sign", "Sub", "Add", "Neg", "Abs", "SafeDiv", "Clip", "Rank"}


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


def summarize(df: pd.DataFrame, cols: list[str], name: str = "rows") -> pd.DataFrame:
    if df.empty or any(col not in df.columns for col in cols):
        return pd.DataFrame(columns=cols + [name])
    return df.groupby(cols, dropna=False).size().reset_index(name=name).sort_values(name, ascending=False)


def skeleton_key(expr: str) -> str:
    return "skel_" + digest("".join("x" if ch.isalnum() else ch for ch in expr), 16)


def production_key(expr: str) -> str:
    return "prod_" + digest(expr, 16)


def fields_in_expr(expr: str) -> list[str]:
    tokens = FIELD_RE.findall(str(expr))
    return sorted({tok for tok in tokens if tok not in OPERATORS})


def mechanism_from_pair(pair: str, expr: str) -> str:
    text = f"{pair}|{expr}".lower()
    if "volume_volatility_ratio" in text:
        if "premium" in text or "basis" in text:
            return "volatility_liquidity_x_premium_basis"
        if "age_" in text or "listing" in text:
            return "volatility_liquidity_x_listing_lifecycle"
        return "volatility_liquidity_state"
    if "realized_vol" in text:
        if "premium" in text or "basis" in text:
            return "realized_vol_x_premium_basis"
        return "realized_vol_state"
    if "listing_age" in text or "age_x" in text or "age_percentile" in text:
        return "listing_lifecycle_state"
    if "open_interest" in text or "long_short" in text or "taker_buy_sell" in text:
        if "basis" in text or "premium" in text:
            return "positioning_x_basis_premium"
        return "positioning_flow_state"
    if "basis" in text or "premium" in text:
        return "basis_premium_state"
    return "other"


def quality_tier(row: dict[str, Any]) -> str:
    control = float(row.get("control_ratio_premay_max", 1.0) or 1.0)
    cost = float(row.get("cost10_recent_oriented", 0.0) or 0.0)
    robust = float(row.get("robust_min_tstat_floor", 0.0) or 0.0)
    lag = float(row.get("one_bar_lag_recent_oriented", 0.0) or 0.0)
    if control < 0.7 and cost > 0.01 and robust > 0.5 and lag > 0:
        return "Q0_high"
    if control < 0.85 and robust > 0:
        return "Q1_medium"
    if control < 1.0:
        return "Q2_weak_control_clean"
    return "Q3_borderline"


def load_clues() -> pd.DataFrame:
    frames = []
    for path, src in [(A7LS6_SHORTLIST, "shortlist"), (A7LS6_CLUES, "all_clues")]:
        df = read_csv(path)
        if not df.empty:
            df["source_registry"] = src
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    clues = pd.concat(frames, ignore_index=True)
    clues = clues[clues["label_family"].astype(str).ne("L7_ranked_future_return")].copy()
    for col in [
        "control_ratio_premay_max",
        "cost10_recent_oriented",
        "one_bar_lag_recent_oriented",
        "robust_min_tstat_floor",
        "deep_followup_score",
    ]:
        if col in clues.columns:
            clues[col] = pd.to_numeric(clues[col], errors="coerce")
    clues = clues.sort_values(["deep_followup_score", "blueprint_id"], ascending=[False, True]).drop_duplicates(
        ["blueprint_id", "label_family", "label_horizon_h"]
    )
    return clues


def add(rows: list[dict[str, Any]], lane: str, family: str, pair: str, motif: str, expr: str, seed_id: str, priority: int) -> None:
    rows.append(
        {
            "a7ls_arm": lane,
            "next_wave_family": family,
            "semantic_pair": pair,
            "motif": motif,
            "blueprint_id": "a7ls8_" + digest(f"{lane}|{family}|{motif}|{expr}", 16),
            "source_seed_id": seed_id,
            "source_priority_rank": priority,
            "expression": expr,
            "skeleton_key": skeleton_key(expr),
            "production_key": production_key(expr),
            "selected_for_next_numeric": True,
            "uses_may": False,
            "notes": "A7LS7 mechanism-backed next numeric queue; no search authorization.",
        }
    )


def volatility_expansion(rows: list[dict[str, Any]], seed_id: str, priority: int) -> None:
    fields = ["volume_volatility_ratio_168h", "realized_vol_24h", "realized_vol_72h", "realized_vol_168h"]
    partners = ["premium_close_bps", "mark_index_basis_bps", "mark_trade_basis_bps", "age_percentile_active_universe", "liquidity_rank_active_universe"]
    windows = [4, 8, 12, 24, 48, 72, 168, 336, 720]
    for field in fields:
        for w in windows:
            add(rows, "A7LS8_A", "volatility_core_expansion", "volatility_like", "zmean", f"ZScore(Mean({field},{w}))", seed_id, priority)
            add(rows, "A7LS8_A", "volatility_core_expansion", "volatility_like", "delta", f"Delta({field},{w})", seed_id, priority)
            add(rows, "A7LS8_A", "volatility_core_expansion", "volatility_like", "rank", f"CSRank({field})", seed_id, priority)
        for short, long in [(4, 72), (8, 168), (24, 336), (72, 720)]:
            add(rows, "A7LS8_A", "volatility_core_expansion", "volatility_like", "spread_short_long", f"Sub(Mean({field},{short}),Mean({field},{long}))", seed_id, priority)
        for partner in partners:
            for w in [8, 24, 72, 168, 336]:
                pair = f"volatility_like|{partner}"
                add(rows, "A7LS8_B", "volatility_context_interaction", pair, "typed_gate", f"Mul(ZScore(Mean({field},{w})),Sign(ZScore(Mean({partner},{w}))))", seed_id, priority)
                add(rows, "A7LS8_B", "volatility_context_interaction", pair, "typed_interaction", f"Mul(Delta({field},{w}),ZScore(Mean({partner},{w})))", seed_id, priority)


def listing_expansion(rows: list[dict[str, Any]], seed_id: str, priority: int) -> None:
    fields = ["age_x_volatility", "age_x_liquidity", "age_x_funding_abs", "age_percentile_active_universe", "log1p_listing_age_days", "sqrt_listing_age_days"]
    partners = ["premium_abs_168h", "basis_abs_168h", "realized_vol_168h", "volume_volatility_ratio_168h", "liquidity_rank_active_universe"]
    for field in fields:
        for w in [24, 72, 168, 336, 720]:
            add(rows, "A7LS8_C", "listing_lifecycle_expansion", "listing_age_like", "zmean", f"ZScore(Mean({field},{w}))", seed_id, priority)
            add(rows, "A7LS8_C", "listing_lifecycle_expansion", "listing_age_like", "rank", f"CSRank({field})", seed_id, priority)
        for partner in partners:
            for w in [24, 72, 168, 336]:
                add(rows, "A7LS8_C", "listing_lifecycle_expansion", "listing_age_like|regime_state", "typed_gate", f"Mul(ZScore(Mean({field},{w})),Sign(ZScore(Mean({partner},{w}))))", seed_id, priority)
                add(rows, "A7LS8_C", "listing_lifecycle_expansion", "listing_age_like|regime_state", "typed_interaction", f"Mul(ZScore(Mean({field},{w})),ZScore(Mean({partner},{w})))", seed_id, priority)


def oi_expansion(rows: list[dict[str, Any]], seed_id: str, priority: int) -> None:
    fields = [
        "open_interest_last",
        "open_interest_value_last",
        "global_long_short_account_ratio_last",
        "top_long_short_account_ratio_last",
        "top_long_short_position_ratio_last",
        "taker_buy_sell_volume_ratio_last",
    ]
    partners = ["mark_index_basis_bps", "premium_close_bps", "trade_return_24h", "realized_vol_168h", "volume_volatility_ratio_168h"]
    for field in fields:
        for w in [4, 12, 24, 72, 168, 336]:
            add(rows, "A7LS8_D", "oi_positioning_expansion", "open_interest_like|positioning_like", "zmean", f"ZScore(Mean({field},{w}))", seed_id, priority)
            add(rows, "A7LS8_D", "oi_positioning_expansion", "open_interest_like|positioning_like", "delta", f"Delta({field},{w})", seed_id, priority)
        for partner in partners:
            for w in [12, 24, 72, 168]:
                pair = f"open_interest_like|{partner}"
                add(rows, "A7LS8_D", "oi_positioning_expansion", pair, "typed_gate", f"Mul(ZScore(Mean({field},{w})),Sign(ZScore(Mean({partner},{w}))))", seed_id, priority)
                add(rows, "A7LS8_D", "oi_positioning_expansion", pair, "typed_interaction", f"Mul(Delta({field},{w}),ZScore(Mean({partner},{w})))", seed_id, priority)


def basis_vol_expansion(rows: list[dict[str, Any]], seed_id: str, priority: int) -> None:
    basis_fields = ["mark_index_basis_bps", "mark_trade_basis_bps", "premium_close_bps"]
    vol_fields = ["volume_volatility_ratio_168h", "realized_vol_24h", "realized_vol_168h"]
    for basis in basis_fields:
        for vol in vol_fields:
            for w in [4, 12, 24, 72, 168, 336]:
                add(rows, "A7LS8_E", "basis_vol_hybrid_expansion", f"basis_premium_like|{vol}", "typed_gate", f"Mul(ZScore(Mean({basis},{w})),Sign(ZScore(Mean({vol},{w}))))", seed_id, priority)
                add(rows, "A7LS8_E", "basis_vol_hybrid_expansion", f"basis_premium_like|{vol}", "typed_interaction", f"Mul(Delta({basis},{w}),ZScore(Mean({vol},{w})))", seed_id, priority)
                add(rows, "A7LS8_E", "basis_vol_hybrid_expansion", f"basis_premium_like|{vol}", "spread_interaction", f"Mul(Sub(Mean({basis},{max(1, w // 6)}),Mean({basis},{w})),ZScore(Mean({vol},{w})))", seed_id, priority)


def mechanism_registry(clues: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in clues.to_dict("records"):
        expr = str(row.get("expression", ""))
        pair = str(row.get("semantic_pair", ""))
        fields = fields_in_expr(expr)
        rows.append(
            {
                "blueprint_id": row.get("blueprint_id", ""),
                "expression": expr,
                "semantic_pair": pair,
                "motif": row.get("motif", ""),
                "label_family": row.get("label_family", ""),
                "label_horizon_h": row.get("label_horizon_h", ""),
                "mechanism": mechanism_from_pair(pair, expr),
                "field_tokens": ";".join(fields),
                "field_count": len(fields),
                "operator_path": " > ".join(tok for tok in FIELD_RE.findall(expr) if tok in OPERATORS),
                "quality_tier": quality_tier(row),
                "control_ratio_premay_max": row.get("control_ratio_premay_max", ""),
                "cost10_recent_oriented": row.get("cost10_recent_oriented", ""),
                "one_bar_lag_recent_oriented": row.get("one_bar_lag_recent_oriented", ""),
                "robust_min_tstat_floor": row.get("robust_min_tstat_floor", ""),
                "deep_followup_score": row.get("deep_followup_score", ""),
                "source_file": row.get("source_file", ""),
            }
        )
    return pd.DataFrame(rows)


def build_next_queue(registry: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    seeds = registry.sort_values(["quality_tier", "deep_followup_score"], ascending=[True, False]).to_dict("records")
    if not seeds:
        return pd.DataFrame()
    for i, seed in enumerate(seeds):
        seed_id = str(seed.get("blueprint_id", f"seed_{i}"))
        mechanism = str(seed.get("mechanism", ""))
        priority = i
        if mechanism in {"volatility_liquidity_state", "volatility_liquidity_x_premium_basis", "volatility_liquidity_x_listing_lifecycle", "realized_vol_state", "realized_vol_x_premium_basis"}:
            volatility_expansion(rows, seed_id, priority)
            basis_vol_expansion(rows, seed_id, priority + 500)
        if mechanism == "listing_lifecycle_state":
            listing_expansion(rows, seed_id, priority)
        if mechanism in {"positioning_flow_state", "positioning_x_basis_premium"}:
            oi_expansion(rows, seed_id, priority)
        if mechanism == "basis_premium_state":
            basis_vol_expansion(rows, seed_id, priority)

    # Explicit reserved axes prevent the next wave from collapsing into whichever mechanism had the most A7LS6 rows.
    volatility_expansion(rows, "a7ls7_reserved_volatility_axis", 100000)
    listing_expansion(rows, "a7ls7_reserved_listing_axis", 100001)
    oi_expansion(rows, "a7ls7_reserved_oi_axis", 100002)
    basis_vol_expansion(rows, "a7ls7_reserved_basis_vol_axis", 100003)

    pool = pd.DataFrame(rows).drop_duplicates("blueprint_id").copy()
    caps = {
        "volatility_core_expansion": 384,
        "volatility_context_interaction": 384,
        "listing_lifecycle_expansion": 256,
        "oi_positioning_expansion": 256,
        "basis_vol_hybrid_expansion": 256,
    }
    parts = []
    for family, cap in caps.items():
        sub = pool[pool["next_wave_family"].eq(family)].copy()
        parts.append(sub.sort_values(["source_priority_rank", "semantic_pair", "motif", "blueprint_id"]).head(cap))
    queue = pd.concat(parts, ignore_index=True).drop_duplicates("blueprint_id").copy()
    queue = queue.sort_values(["next_wave_family", "source_priority_rank", "semantic_pair", "blueprint_id"]).reset_index(drop=True)
    rows_per_shard = 64
    queue["company_numeric_shard"] = [f"a7ls8_s{i // rows_per_shard:03d}" for i in range(len(queue))]
    queue["checkpoint_key"] = queue["company_numeric_shard"] + "::" + queue["blueprint_id"]
    return queue


def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    auth = read_json(A7LS6_MANIFEST)
    clues = load_clues()
    if clues.empty:
        raise SystemExit("missing A7LS6 non-L7 clues")
    registry = mechanism_registry(clues)
    unique_expr = registry.sort_values(["quality_tier", "deep_followup_score"], ascending=[True, False]).drop_duplicates("expression")
    queue = build_next_queue(registry)

    shard_plan = queue.groupby("company_numeric_shard", dropna=False).agg(
        rows=("blueprint_id", "size"),
        family_count=("next_wave_family", "nunique"),
        semantic_pair_count=("semantic_pair", "nunique"),
        motif_count=("motif", "nunique"),
    ).reset_index() if not queue.empty else pd.DataFrame()
    mechanism_summary = summarize(registry, ["mechanism", "quality_tier"])
    family_summary = queue.groupby("next_wave_family", dropna=False).agg(
        rows=("blueprint_id", "size"),
        semantic_pair_count=("semantic_pair", "nunique"),
        motif_count=("motif", "nunique"),
        skeleton_count=("skeleton_key", "nunique"),
        source_seed_count=("source_seed_id", "nunique"),
    ).reset_index().sort_values("rows", ascending=False) if not queue.empty else pd.DataFrame()

    registry.to_csv(RUNTIME / "a7ls7_clue_mechanism_registry.csv", index=False)
    unique_expr.to_csv(RUNTIME / "a7ls7_unique_expression_registry.csv", index=False)
    mechanism_summary.to_csv(RUNTIME / "a7ls7_mechanism_summary.csv", index=False)
    summarize(registry, ["label_family", "label_horizon_h"]).to_csv(RUNTIME / "a7ls7_label_horizon_summary.csv", index=False)
    summarize(registry, ["semantic_pair", "mechanism"]).to_csv(RUNTIME / "a7ls7_pair_mechanism_summary.csv", index=False)
    queue.to_csv(RUNTIME / "a7ls7_next_company_numeric_queue.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ls7_next_company_shard_plan.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ls7_next_family_summary.csv", index=False)

    blockers: list[str] = []
    if auth.get("decision") != "PASS_A7LS6_DEEP_NUMERIC_AGGREGATED_CLUES_FOUND_NO_SEARCH_AUTH":
        blockers.append("a7ls6_aggregate_not_ready")
    if len(registry) < 20:
        blockers.append("too_few_clues_for_mechanism_queue")
    if registry["mechanism"].nunique() < 4:
        blockers.append("mechanism_breadth_too_low")
    if len(queue) < 768:
        blockers.append("next_queue_too_small")
    if not family_summary.empty and family_summary["rows"].max() / len(queue) > 0.4:
        blockers.append("next_queue_family_concentration_high")

    decision = "PASS_A7LS7_MECHANISM_QUEUE_READY_FOR_A7LS8_COMPANY_NUMERIC_NO_SEARCH_AUTH" if not blockers else "HOLD_A7LS7_MECHANISM_QUEUE_NOT_READY"
    manifest = {
        "stage": "A7LS-7",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ls6_manifest": str(A7LS6_MANIFEST),
        "clue_rows": int(len(registry)),
        "unique_expression_count": int(len(unique_expr)),
        "mechanism_count": int(registry["mechanism"].nunique()),
        "quality_tier_count": int(registry["quality_tier"].nunique()),
        "next_queue_rows": int(len(queue)),
        "next_shard_count": int(shard_plan.shape[0]) if not shard_plan.empty else 0,
        "next_family_count": int(family_summary.shape[0]) if not family_summary.empty else 0,
        "rows_per_shard": 64,
        "hours_per_split_target": 2160,
        "blockers": blockers,
        "executes_generation": True,
        "executes_numeric_probe": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ls8_company_numeric": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls7_manifest.json", manifest)

    lines = [
        "# CRYPTO A7LS-7 CLUE MECHANISM QUEUE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- clue_rows: {manifest['clue_rows']}",
        f"- unique_expression_count: {manifest['unique_expression_count']}",
        f"- mechanism_count: {manifest['mechanism_count']}",
        f"- next_queue_rows: {manifest['next_queue_rows']}",
        f"- next_shard_count: {manifest['next_shard_count']}",
        f"- next_family_count: {manifest['next_family_count']}",
        f"- hours_per_split_target: {manifest['hours_per_split_target']}",
        f"- blockers: {', '.join(blockers) if blockers else '<none>'}",
        "",
        "## Mechanism Summary",
        "",
        md_table(mechanism_summary, 80),
        "",
        "## Next Family Summary",
        "",
        md_table(family_summary, 40),
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan, 80),
        "",
        "## Top Clue Mechanisms",
        "",
        md_table(registry.sort_values(["quality_tier", "deep_followup_score"], ascending=[True, False]).head(30), 30),
        "",
        "## Authorization",
        "",
        "- Authorizes A7LS8 company numeric execution only if decision is PASS.",
        "- Does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "- May is not used in clue classification, queue ranking, or next-wave construction.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
