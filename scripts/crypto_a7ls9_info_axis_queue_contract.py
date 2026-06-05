from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ls9_info_axis_queue_contract"
REPORT = REPO / "reports" / "CRYPTO_A7LS9_INFO_AXIS_QUEUE_CONTRACT_20260605.md"
A7LS8_MANIFEST = REPO / "runtime" / "a7ls8_company_result_aggregate" / "a7ls8_aggregate_manifest.json"
A7LS8_CLUES = REPO / "runtime" / "a7ls8_company_result_aggregate" / "a7ls8_non_l7_numeric_clues.csv"
A7LS8_RESPONSES = REPO / "runtime" / "a7ls8_company_result_aggregate" / "a7ls8_combined_responses.csv"


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
    return "skel_" + digest("".join("x" if ch.isalnum() else ch for ch in str(expr)), 16)


def production_key(expr: str) -> str:
    return "prod_" + digest(str(expr), 16)


def fields_in_expr(expr: str) -> list[str]:
    tokens = FIELD_RE.findall(str(expr))
    return sorted({tok for tok in tokens if tok not in OPERATORS})


def operator_path(expr: str) -> str:
    return " > ".join(tok for tok in FIELD_RE.findall(str(expr)) if tok in OPERATORS)


def infer_info_axis(expr: str, pair: str) -> str:
    text = f"{pair}|{expr}".lower()
    has_vol = "realized_vol" in text or "volume_volatility" in text
    has_liq = "liquidity_rank" in text or "volume_volatility" in text
    has_age = "age_" in text or "listing" in text or "log1p_listing" in text or "sqrt_listing" in text
    has_basis = "basis" in text or "premium" in text
    has_oi = "open_interest" in text or "long_short" in text or "taker_buy_sell" in text
    if has_age and has_vol and has_liq:
        return "listing_x_vol_liquidity"
    if has_age and has_basis:
        return "listing_x_basis_regime"
    if has_age:
        return "listing_lifecycle"
    if has_vol and has_liq and has_basis:
        return "vol_liquidity_x_basis"
    if has_vol and has_liq:
        return "vol_liquidity"
    if has_vol and has_basis:
        return "vol_x_basis"
    if has_oi and has_basis:
        return "positioning_x_basis"
    if has_oi and has_vol:
        return "positioning_x_vol"
    if has_oi:
        return "positioning_flow"
    if has_basis:
        return "basis_premium"
    if has_vol:
        return "volatility"
    return "other"


def stability_tier(row: dict[str, Any]) -> str:
    control = float(row.get("control_ratio_premay_max", 1.0) or 1.0)
    robust = float(row.get("robust_min_tstat_floor", 0.0) or 0.0)
    cost2 = float(row.get("cost2_recent_oriented", 0.0) or 0.0)
    cost10 = float(row.get("cost10_recent_oriented", 0.0) or 0.0)
    lag = float(row.get("one_bar_lag_recent_oriented", 0.0) or 0.0)
    labels = int(row.get("distinct_label_count", 1) or 1)
    horizons = int(row.get("distinct_horizon_count", 1) or 1)
    if control < 0.65 and robust > 0.5 and cost10 > 0 and lag > 0 and labels >= 2:
        return "S0_strong_tradeable_probe"
    if control < 0.8 and robust > 0 and cost2 > 0 and lag > 0 and labels >= 1:
        return "S1_good_numeric_probe"
    if control < 0.95 and robust > -0.25 and lag > 0:
        return "S2_control_clean_probe"
    if labels >= 2 or horizons >= 2:
        return "S3_multi_label_diagnostic"
    return "S4_single_view_weak"


def numeric_score(row: dict[str, Any]) -> float:
    control = float(row.get("control_ratio_premay_max", 1.0) or 1.0)
    robust = float(row.get("robust_min_tstat_floor", 0.0) or 0.0)
    lag = float(row.get("one_bar_lag_recent_oriented", 0.0) or 0.0)
    cost2 = float(row.get("cost2_recent_oriented", 0.0) or 0.0)
    cost10 = float(row.get("cost10_recent_oriented", 0.0) or 0.0)
    labels = float(row.get("distinct_label_count", 1) or 1)
    horizons = float(row.get("distinct_horizon_count", 1) or 1)
    return (
        max(0.0, 1.0 - min(control, 1.2)) * 100.0
        + max(0.0, robust) * 8.0
        + max(0.0, lag) * 1200.0
        + max(0.0, cost2) * 900.0
        + max(0.0, cost10) * 600.0
        + min(labels, 4.0) * 4.0
        + min(horizons, 4.0) * 2.0
    )


def load_registry() -> pd.DataFrame:
    clues = read_csv(A7LS8_CLUES)
    if clues.empty:
        raise SystemExit("missing A7LS8 non-L7 clues")
    for col in [
        "control_ratio_premay_max",
        "cost2_recent_oriented",
        "cost5_recent_oriented",
        "cost10_recent_oriented",
        "one_bar_lag_recent_oriented",
        "robust_min_tstat_floor",
        "label_horizon_h",
    ]:
        if col in clues.columns:
            clues[col] = pd.to_numeric(clues[col], errors="coerce")
    group_cols = ["blueprint_id", "expression", "semantic_pair", "motif", "next_wave_family", "a7ls_arm", "source_seed_id", "skeleton_key", "production_key"]
    rows = []
    for _, grp in clues.groupby(group_cols, dropna=False):
        best = grp.sort_values(["control_ratio_premay_max", "robust_min_tstat_floor"], ascending=[True, False]).iloc[0].to_dict()
        labels = sorted(map(str, grp["label_family"].dropna().unique()))
        horizons = sorted(map(str, grp["label_horizon_h"].dropna().astype(int).unique())) if "label_horizon_h" in grp.columns else []
        expr = str(best.get("expression", ""))
        pair = str(best.get("semantic_pair", ""))
        rec = {
            **best,
            "distinct_label_count": len(labels),
            "distinct_horizon_count": len(horizons),
            "label_families_seen": ";".join(labels),
            "horizons_seen": ";".join(horizons),
            "field_tokens": ";".join(fields_in_expr(expr)),
            "field_count": len(fields_in_expr(expr)),
            "operator_path": operator_path(expr),
            "info_axis": infer_info_axis(expr, pair),
            "candidate_review_provenance": "A7LS8 company numeric non-L7 clue; no discovery credit; no search authorization.",
        }
        rec["stability_tier"] = stability_tier(rec)
        rec["info_axis_score"] = numeric_score(rec)
        rows.append(rec)
    registry = pd.DataFrame(rows).sort_values(["stability_tier", "info_axis_score", "blueprint_id"], ascending=[True, False, True])
    return registry


def add(rows: list[dict[str, Any]], arm: str, family: str, pair: str, motif: str, expr: str, source: dict[str, Any], priority: int) -> None:
    rows.append(
        {
            "a7ls_arm": arm,
            "next_wave_family": family,
            "semantic_pair": pair,
            "motif": motif,
            "blueprint_id": "a7ls9_" + digest(f"{arm}|{family}|{motif}|{expr}", 16),
            "source_seed_id": source.get("blueprint_id", ""),
            "source_info_axis": source.get("info_axis", ""),
            "source_stability_tier": source.get("stability_tier", ""),
            "source_info_axis_score": source.get("info_axis_score", ""),
            "source_label_families_seen": source.get("label_families_seen", ""),
            "source_horizons_seen": source.get("horizons_seen", ""),
            "source_priority_rank": priority,
            "expression": expr,
            "field_tokens": ";".join(fields_in_expr(expr)),
            "operator_path": operator_path(expr),
            "skeleton_key": skeleton_key(expr),
            "production_key": production_key(expr),
            "selected_for_next_numeric": True,
            "uses_may": False,
            "notes": "A7LS9 information-axis queue; mechanism deduped; no search authorization.",
        }
    )


def expand_vol_liquidity(rows: list[dict[str, Any]], source: dict[str, Any], priority: int) -> None:
    vol_fields = ["volume_volatility_ratio_168h", "realized_vol_24h", "realized_vol_72h", "realized_vol_168h", "trade_return_24h"]
    liq_fields = ["liquidity_rank_active_universe", "volume_volatility_ratio_168h", "quote_volume", "trade_volume"]
    windows = [4, 8, 12, 24, 48, 72, 96, 168, 336, 504, 720]
    for vol in vol_fields:
        for w in windows:
            add(rows, "A7LS9_A", "vol_liquidity_deep", "volatility_like", "zmean", f"ZScore(Mean({vol},{w}))", source, priority)
            add(rows, "A7LS9_A", "vol_liquidity_deep", "volatility_like", "delta", f"Delta({vol},{w})", source, priority)
            add(rows, "A7LS9_A", "vol_liquidity_deep", "volatility_like", "rank", f"CSRank({vol})", source, priority)
        for short, long in [(4, 48), (8, 72), (12, 168), (24, 336), (72, 720)]:
            add(rows, "A7LS9_A", "vol_liquidity_deep", "volatility_like", "spread_short_long", f"Sub(Mean({vol},{short}),Mean({vol},{long}))", source, priority)
            add(rows, "A7LS9_A", "vol_liquidity_deep", "volatility_like", "spread_abs", f"Abs(Sub(Mean({vol},{short}),Mean({vol},{long})))", source, priority)
        for liq in liq_fields:
            for w in [8, 12, 24, 48, 72, 168, 336, 504]:
                add(rows, "A7LS9_B", "vol_liquidity_interaction", f"volatility_like|{liq}", "typed_interaction", f"Mul(Delta({vol},{w}),ZScore(Mean({liq},{w})))", source, priority)
                add(rows, "A7LS9_B", "vol_liquidity_interaction", f"volatility_like|{liq}", "typed_gate", f"Mul(ZScore(Mean({vol},{w})),Sign(ZScore(Mean({liq},{w}))))", source, priority)
                add(rows, "A7LS9_B", "vol_liquidity_interaction", f"volatility_like|{liq}", "abs_state_interaction", f"Mul(Abs(ZScore(Mean({vol},{w}))),ZScore(Mean({liq},{w})))", source, priority)


def expand_listing(rows: list[dict[str, Any]], source: dict[str, Any], priority: int) -> None:
    age_fields = ["age_x_liquidity", "age_x_volatility", "age_x_funding_abs", "age_percentile_active_universe", "log1p_listing_age_days", "sqrt_listing_age_days"]
    partners = ["volume_volatility_ratio_168h", "realized_vol_24h", "realized_vol_72h", "realized_vol_168h", "liquidity_rank_active_universe", "premium_abs_168h", "basis_abs_168h", "premium_close_bps", "mark_index_basis_bps"]
    for age in age_fields:
        for w in [4, 8, 24, 48, 72, 168, 336, 504, 720]:
            add(rows, "A7LS9_C", "listing_lifecycle_deep", "listing_age_like", "zmean", f"ZScore(Mean({age},{w}))", source, priority)
            add(rows, "A7LS9_C", "listing_lifecycle_deep", "listing_age_like", "rank", f"CSRank({age})", source, priority)
            add(rows, "A7LS9_C", "listing_lifecycle_deep", "listing_age_like", "delta", f"Delta({age},{w})", source, priority)
        for partner in partners:
            for w in [12, 24, 72, 168, 336, 504]:
                add(rows, "A7LS9_D", "listing_state_interaction", "listing_age_like|regime_state", "typed_interaction", f"Mul(ZScore(Mean({age},{w})),ZScore(Mean({partner},{w})))", source, priority)
                add(rows, "A7LS9_D", "listing_state_interaction", "listing_age_like|regime_state", "typed_gate", f"Mul(ZScore(Mean({age},{w})),Sign(ZScore(Mean({partner},{w}))))", source, priority)
                add(rows, "A7LS9_D", "listing_state_interaction", "listing_age_like|regime_state", "age_abs_state", f"Mul(ZScore(Mean({age},{w})),Abs(ZScore(Mean({partner},{w}))))", source, priority)


def expand_basis_crowding(rows: list[dict[str, Any]], source: dict[str, Any], priority: int) -> None:
    basis_fields = ["mark_index_basis_bps", "mark_trade_basis_bps", "premium_close_bps", "basis_abs_168h", "premium_abs_168h"]
    partners = ["realized_vol_24h", "realized_vol_72h", "realized_vol_168h", "volume_volatility_ratio_168h", "liquidity_rank_active_universe", "age_x_volatility", "age_x_liquidity", "open_interest_value_last", "taker_buy_sell_volume_ratio_last"]
    for basis in basis_fields:
        for w in [4, 8, 12, 24, 48, 72, 168, 336, 504]:
            add(rows, "A7LS9_E", "basis_crowding_deep", "basis_premium_like", "zmean", f"ZScore(Mean({basis},{w}))", source, priority)
            add(rows, "A7LS9_E", "basis_crowding_deep", "basis_premium_like", "delta", f"Delta({basis},{w})", source, priority)
            add(rows, "A7LS9_E", "basis_crowding_deep", "basis_premium_like", "abs_zmean", f"Abs(ZScore(Mean({basis},{w})))", source, priority)
        for partner in partners:
            for w in [8, 12, 24, 72, 168, 336, 504]:
                add(rows, "A7LS9_F", "basis_context_interaction", f"basis_premium_like|{partner}", "typed_interaction", f"Mul(Delta({basis},{w}),ZScore(Mean({partner},{w})))", source, priority)
                add(rows, "A7LS9_F", "basis_context_interaction", f"basis_premium_like|{partner}", "spread_interaction", f"Mul(Sub(Mean({basis},{max(1, w // 6)}),Mean({basis},{w})),ZScore(Mean({partner},{w})))", source, priority)
                add(rows, "A7LS9_F", "basis_context_interaction", f"basis_premium_like|{partner}", "basis_abs_gate", f"Mul(Abs(ZScore(Mean({basis},{w}))),Sign(ZScore(Mean({partner},{w}))))", source, priority)


def expand_positioning(rows: list[dict[str, Any]], source: dict[str, Any], priority: int) -> None:
    pos_fields = [
        "open_interest_last",
        "open_interest_value_last",
        "global_long_short_account_ratio_last",
        "top_long_short_account_ratio_last",
        "top_long_short_position_ratio_last",
        "taker_buy_sell_volume_ratio_last",
    ]
    partners = ["mark_index_basis_bps", "premium_close_bps", "basis_abs_168h", "premium_abs_168h", "realized_vol_24h", "realized_vol_168h", "volume_volatility_ratio_168h", "age_x_liquidity", "liquidity_rank_active_universe"]
    for field in pos_fields:
        for w in [4, 8, 12, 24, 48, 72, 168, 336, 504]:
            add(rows, "A7LS9_G", "positioning_flow_recovery", "open_interest_like|positioning_like", "zmean", f"ZScore(Mean({field},{w}))", source, priority)
            add(rows, "A7LS9_G", "positioning_flow_recovery", "open_interest_like|positioning_like", "delta", f"Delta({field},{w})", source, priority)
            add(rows, "A7LS9_G", "positioning_flow_recovery", "open_interest_like|positioning_like", "rank", f"CSRank({field})", source, priority)
        for partner in partners:
            for w in [8, 12, 24, 72, 168, 336, 504]:
                add(rows, "A7LS9_H", "positioning_context_interaction", f"open_interest_like|{partner}", "typed_interaction", f"Mul(Delta({field},{w}),ZScore(Mean({partner},{w})))", source, priority)
                add(rows, "A7LS9_H", "positioning_context_interaction", f"open_interest_like|{partner}", "typed_gate", f"Mul(ZScore(Mean({field},{w})),Sign(ZScore(Mean({partner},{w}))))", source, priority)
                add(rows, "A7LS9_H", "positioning_context_interaction", f"open_interest_like|{partner}", "positioning_abs_state", f"Mul(Abs(ZScore(Mean({field},{w}))),ZScore(Mean({partner},{w})))", source, priority)


def expand_raw_axis(rows: list[dict[str, Any]], source: dict[str, Any], priority: int) -> None:
    # Deliberately broad but typed: this lane tests raw system usability without turning into unbounded grammar search.
    raw_fields = [
        "volume_volatility_ratio_168h",
        "realized_vol_24h",
        "realized_vol_72h",
        "realized_vol_168h",
        "liquidity_rank_active_universe",
        "age_x_liquidity",
        "age_x_volatility",
        "age_percentile_active_universe",
        "premium_close_bps",
        "mark_index_basis_bps",
        "basis_abs_168h",
        "premium_abs_168h",
        "open_interest_value_last",
        "taker_buy_sell_volume_ratio_last",
        "top_long_short_account_ratio_last",
    ]
    for i, left in enumerate(raw_fields):
        for right in raw_fields[i + 1 :]:
            for w in [12, 24, 72, 168, 336]:
                pair = f"{infer_info_axis(left, left)}|{infer_info_axis(right, right)}"
                add(rows, "A7LS9_R", "raw_multi_axis_probe", pair, "raw_typed_mul", f"Mul(ZScore(Mean({left},{w})),ZScore(Mean({right},{w})))", source, priority)
                add(rows, "A7LS9_R", "raw_multi_axis_probe", pair, "raw_gate", f"Mul(ZScore(Mean({left},{w})),Sign(ZScore(Mean({right},{w}))))", source, priority)
                add(rows, "A7LS9_R", "raw_multi_axis_probe", pair, "raw_delta_state", f"Mul(Delta({left},{w}),ZScore(Mean({right},{w})))", source, priority)
                add(rows, "A7LS9_R", "raw_multi_axis_probe", pair, "raw_abs_state", f"Mul(Abs(ZScore(Mean({left},{w}))),ZScore(Mean({right},{w})))", source, priority)


def build_queue(registry: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    seeds = registry.sort_values(["stability_tier", "info_axis_score"], ascending=[True, False]).to_dict("records")
    for i, seed in enumerate(seeds):
        axis = str(seed.get("info_axis", ""))
        if axis in {"vol_liquidity", "vol_x_basis", "vol_liquidity_x_basis", "volatility"}:
            expand_vol_liquidity(rows, seed, i)
            expand_basis_crowding(rows, seed, i + 1000)
        if axis in {"listing_lifecycle", "listing_x_vol_liquidity", "listing_x_basis_regime"}:
            expand_listing(rows, seed, i)
        if axis in {"positioning_flow", "positioning_x_basis", "positioning_x_vol"}:
            expand_positioning(rows, seed, i)
        if axis in {"basis_premium"}:
            expand_basis_crowding(rows, seed, i)

    reserves = [
        {"blueprint_id": "a7ls9_reserved_vol_liq", "info_axis": "vol_liquidity", "stability_tier": "RESERVE", "info_axis_score": 0},
        {"blueprint_id": "a7ls9_reserved_listing", "info_axis": "listing_lifecycle", "stability_tier": "RESERVE", "info_axis_score": 0},
        {"blueprint_id": "a7ls9_reserved_positioning", "info_axis": "positioning_flow", "stability_tier": "RESERVE", "info_axis_score": 0},
        {"blueprint_id": "a7ls9_reserved_basis", "info_axis": "basis_premium", "stability_tier": "RESERVE", "info_axis_score": 0},
        {"blueprint_id": "a7ls9_reserved_raw", "info_axis": "raw_multi_axis", "stability_tier": "RESERVE", "info_axis_score": 0},
    ]
    expand_vol_liquidity(rows, reserves[0], 100000)
    expand_listing(rows, reserves[1], 100001)
    expand_positioning(rows, reserves[2], 100002)
    expand_basis_crowding(rows, reserves[3], 100003)
    expand_raw_axis(rows, reserves[4], 100004)

    pool = pd.DataFrame(rows).drop_duplicates("blueprint_id").copy()
    caps = {
        "vol_liquidity_deep": 384,
        "vol_liquidity_interaction": 384,
        "listing_lifecycle_deep": 320,
        "listing_state_interaction": 384,
        "basis_crowding_deep": 256,
        "basis_context_interaction": 320,
        "positioning_flow_recovery": 320,
        "positioning_context_interaction": 384,
        "raw_multi_axis_probe": 512,
    }
    parts = []
    for family, cap in caps.items():
        sub = pool[pool["next_wave_family"].eq(family)].copy()
        parts.append(sub.sort_values(["source_priority_rank", "semantic_pair", "motif", "blueprint_id"]).head(cap))
    queue = pd.concat(parts, ignore_index=True).drop_duplicates("blueprint_id").copy()
    queue = queue.sort_values(["next_wave_family", "source_priority_rank", "semantic_pair", "blueprint_id"]).reset_index(drop=True)
    rows_per_shard = 64
    queue["company_numeric_shard"] = [f"a7ls10_s{i // rows_per_shard:03d}" for i in range(len(queue))]
    queue["checkpoint_key"] = queue["company_numeric_shard"] + "::" + queue["blueprint_id"]
    return queue


def main() -> int:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    auth = read_json(A7LS8_MANIFEST)
    registry = load_registry()
    queue = build_queue(registry)

    axis_summary = summarize(registry, ["info_axis", "stability_tier"])
    label_summary = summarize(registry, ["label_families_seen", "horizons_seen"])
    family_summary = (
        queue.groupby("next_wave_family", dropna=False)
        .agg(
            rows=("blueprint_id", "size"),
            semantic_pair_count=("semantic_pair", "nunique"),
            motif_count=("motif", "nunique"),
            skeleton_count=("skeleton_key", "nunique"),
            source_seed_count=("source_seed_id", "nunique"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
        if not queue.empty
        else pd.DataFrame()
    )
    shard_plan = (
        queue.groupby("company_numeric_shard", dropna=False)
        .agg(
            rows=("blueprint_id", "size"),
            family_count=("next_wave_family", "nunique"),
            semantic_pair_count=("semantic_pair", "nunique"),
            motif_count=("motif", "nunique"),
        )
        .reset_index()
        if not queue.empty
        else pd.DataFrame()
    )
    overlap = summarize(registry, ["skeleton_key", "semantic_pair"])

    registry.to_csv(RUNTIME / "a7ls9_info_axis_registry.csv", index=False)
    axis_summary.to_csv(RUNTIME / "a7ls9_info_axis_summary.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ls9_label_horizon_evidence_summary.csv", index=False)
    overlap.to_csv(RUNTIME / "a7ls9_overlap_registry.csv", index=False)
    queue.to_csv(RUNTIME / "a7ls9_next_company_numeric_queue.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ls9_next_family_summary.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ls9_next_shard_plan.csv", index=False)

    blockers: list[str] = []
    if auth.get("decision") != "PASS_A7LS8_COMPANY_NUMERIC_AGGREGATED_CLUES_FOUND_NO_SEARCH_AUTH":
        blockers.append("a7ls8_aggregate_not_ready")
    if len(registry) < 20:
        blockers.append("too_few_unique_clue_expressions")
    if registry["info_axis"].nunique() < 5:
        blockers.append("info_axis_breadth_too_low")
    if len(queue) < 2048:
        blockers.append("next_queue_below_scale_floor")
    if not family_summary.empty and family_summary["rows"].max() / len(queue) > 0.25:
        blockers.append("next_queue_family_concentration_high")

    decision = "PASS_A7LS9_INFO_AXIS_QUEUE_READY_FOR_A7LS10_COMPANY_NUMERIC_NO_SEARCH_AUTH" if not blockers else "HOLD_A7LS9_INFO_AXIS_QUEUE_NOT_READY"
    manifest = {
        "stage": "A7LS-9",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ls8_manifest": str(A7LS8_MANIFEST),
        "unique_clue_expression_count": int(len(registry)),
        "source_non_l7_clue_rows": int(read_json(A7LS8_MANIFEST).get("non_l7_numeric_clue_rows", 0)),
        "info_axis_count": int(registry["info_axis"].nunique()),
        "stability_tier_count": int(registry["stability_tier"].nunique()),
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
        "authorizes_a7ls10_company_numeric": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls9_manifest.json", manifest)

    lines = [
        "# CRYPTO A7LS-9 INFORMATION AXIS QUEUE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- source_non_l7_clue_rows: {manifest['source_non_l7_clue_rows']}",
        f"- unique_clue_expression_count: {manifest['unique_clue_expression_count']}",
        f"- info_axis_count: {manifest['info_axis_count']}",
        f"- stability_tier_count: {manifest['stability_tier_count']}",
        f"- next_queue_rows: {manifest['next_queue_rows']}",
        f"- next_shard_count: {manifest['next_shard_count']}",
        f"- next_family_count: {manifest['next_family_count']}",
        f"- hours_per_split_target: {manifest['hours_per_split_target']}",
        f"- blockers: {', '.join(blockers) if blockers else '<none>'}",
        "",
        "## Information Axis Summary",
        "",
        md_table(axis_summary, 80),
        "",
        "## Next Family Summary",
        "",
        md_table(family_summary, 80),
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan, 80),
        "",
        "## Top Reviewed Clues",
        "",
        md_table(registry.head(60), 60),
        "",
        "## Authorization",
        "",
        "- Authorizes A7LS10 company numeric execution only if decision is PASS.",
        "- Does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "- May is not used in information-axis scoring, queue ranking, or next-wave construction.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
