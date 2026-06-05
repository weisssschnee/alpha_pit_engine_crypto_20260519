from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ls1_multi_arm_blueprint_generation"
REPORT = REPO / "reports" / "CRYPTO_A7LS1_MULTI_ARM_BLUEPRINT_GENERATION_20260605.md"
LS0 = REPO / "runtime" / "a7ls0_checkpoint_large_search_contract"
EXTERNAL = Path(
    os.environ.get(
        "A7LS1_EXTERNAL",
        "G:/AlphaFactory_CryptoData/research_runtime/a7ls1_multi_arm_blueprint_generation_20260605",
    )
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(prefix: str, text: str) -> str:
    return f"{prefix}_{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


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
        return "```csv\n" + view.to_csv(index=False) + "```"


def skeleton(expr: str) -> str:
    text = re.sub(r"[A-Za-z_][A-Za-z0-9_]*", "TOK", expr)
    text = re.sub(r"\d+", "N", text)
    return stable_id("skel", text)


def field_catalog() -> dict[str, list[str]]:
    # Only include fields already supported by the existing A7FF8 numeric evaluator.
    # funding_event_age_hours from A7LS-0 maps to funding_rate_update_age_hours here.
    return {
        "price_like": ["trade_close", "mark_close", "index_close", "trade_return_1h"],
        "basis_premium_like": ["mark_index_basis_bps", "mark_trade_basis_bps", "premium_close_bps"],
        "funding_state_like": [
            "funding_rate_state_last_ffill_8h",
            "funding_rate_update_age_hours",
            "funding_rate_abs_state_168h_z",
            "funding_rate_delta_state_24h",
            "funding_state_x_basis_delta",
        ],
        "open_interest_like": [
            "open_interest_last",
            "open_interest_mean",
            "open_interest_value_last",
            "open_interest_value_mean",
            "open_interest_change_24h",
        ],
        "positioning_like": [
            "global_long_short_account_ratio_last",
            "global_long_short_account_ratio_mean",
            "top_long_short_account_ratio_last",
            "top_long_short_account_ratio_mean",
            "top_long_short_position_ratio_last",
            "top_long_short_position_ratio_mean",
        ],
        "taker_flow_like": [
            "taker_buy_sell_volume_ratio_last",
            "taker_buy_sell_volume_ratio_mean",
            "kline_taker_buy_quote_share",
            "taker_buy_quote_volume",
        ],
        "liquidity_like": [
            "trade_quote_volume",
            "trade_volume",
            "trade_count",
            "log_quote_volume_168h",
            "median_quote_volume_168h",
            "liquidity_rank_active_universe",
            "volume_volatility_ratio_168h",
        ],
        "volatility_like": ["realized_vol_24h", "realized_vol_72h", "realized_vol_168h"],
        "listing_age_like": [
            "listing_age_days",
            "log1p_listing_age_days",
            "sqrt_listing_age_days",
            "age_percentile_active_universe",
            "age_x_liquidity",
            "age_x_volatility",
        ],
        "regime_state": [
            "funding_abs_state",
            "basis_abs_state",
            "liquidity_state",
            "volatility_state",
            "coverage_state",
            "rolling_coverage_168h",
        ],
        "placebo": ["trade_return_1h", "mark_index_basis_bps", "realized_vol_168h"],
        "low_prior_axes": ["premium_count", "funding_interval_hours", "source_market_funding"],
    }


def transform_set(field: str, axis: str, depth: str) -> list[tuple[str, str]]:
    if axis in {"regime_state", "listing_age_like"}:
        windows = [24, 72, 168]
    elif depth == "raw_or_simple_typed_l1_l2_only":
        windows = [1, 4, 8, 24, 72]
    else:
        windows = [1, 2, 4, 8, 12, 24, 48, 72, 168]
    out: list[tuple[str, str]] = [("level", field)]
    for w in windows:
        out.append((f"delta_{w}h", f"Delta({field},{w})"))
        out.append((f"mean_{w}h", f"Mean({field},{w})"))
        out.append((f"zmean_{w}h", f"ZScore(Mean({field},{w}))"))
    if depth != "raw_or_simple_typed_l1_l2_only":
        for w in [24, 72, 168]:
            out.append((f"abs_zmean_{w}h", f"Abs(ZScore(Mean({field},{w})))"))
            out.append((f"decay_{w}h", f"Decay({field},{w})"))
            out.append((f"tsrank_{w}h", f"TSRank({field},{w})"))
    if axis not in {"regime_state", "listing_age_like"}:
        out.append(("csrank", f"CSRank({field})"))
        out.append(("clip_z", f"Clip(ZScore({field}),-3,3)"))
    # Deduplicate by expression while preserving transform name order.
    seen: set[str] = set()
    dedup: list[tuple[str, str]] = []
    for name, expr in out:
        if expr in seen:
            continue
        seen.add(expr)
        dedup.append((name, expr))
    return dedup


def motif_expr(left: str, right: str, motif: str) -> str:
    if motif == "mul":
        return f"Mul({left},{right})"
    if motif == "sub":
        return f"Sub({left},{right})"
    if motif == "spread_rank":
        return f"Sub(CSRank({left}),CSRank({right}))"
    if motif == "gated_sign":
        return f"Mul({left},Sign({right}))"
    if motif == "safe_div_abs":
        return f"SafeDiv({left},Abs({right}))"
    if motif == "smooth_mul":
        return f"Mean(Mul({left},{right}),4)"
    if motif == "relative_shock":
        return f"Mul(Delta({left},4),ZScore({right}))"
    if motif == "signed_spread":
        return f"Mul(Sub(CSRank({left}),CSRank({right})),Sign({right}))"
    if motif == "mean_reversion_gate":
        return f"Mul(Neg(ZScore({left})),Sign({right}))"
    if motif == "delta_x_divergence":
        return f"Mul(Delta({left},24),Sub(CSRank({left}),CSRank({right})))"
    if motif == "state_gate":
        return f"Mul({left},Sign(Mean({right},24)))"
    if motif == "control_flip":
        return f"Neg(Mul({left},{right}))"
    return f"Mul({left},{right})"


def axis_pairs_for_arm(arm_id: str) -> list[tuple[str, str]]:
    if arm_id == "A7LS_A":
        return [
            ("basis_premium_like", "price_like"),
            ("basis_premium_like", "volatility_like"),
            ("basis_premium_like", "basis_premium_like"),
            ("price_like", "volatility_like"),
        ]
    if arm_id == "A7LS_B":
        axes = [
            "price_like",
            "basis_premium_like",
            "funding_state_like",
            "open_interest_like",
            "positioning_like",
            "taker_flow_like",
            "liquidity_like",
            "volatility_like",
            "listing_age_like",
            "regime_state",
        ]
        pairs: list[tuple[str, str]] = []
        for i, left in enumerate(axes):
            for right in axes[i:]:
                if left == right and left not in {"price_like", "basis_premium_like", "open_interest_like"}:
                    continue
                pairs.append((left, right))
        return pairs
    if arm_id == "A7LS_C":
        return [
            ("funding_state_like", "basis_premium_like"),
            ("funding_state_like", "positioning_like"),
            ("funding_state_like", "open_interest_like"),
            ("open_interest_like", "positioning_like"),
            ("open_interest_like", "taker_flow_like"),
            ("positioning_like", "taker_flow_like"),
            ("basis_premium_like", "regime_state"),
            ("open_interest_like", "regime_state"),
        ]
    return [
        ("placebo", "price_like"),
        ("placebo", "basis_premium_like"),
        ("low_prior_axes", "price_like"),
        ("low_prior_axes", "basis_premium_like"),
        ("volatility_like", "liquidity_like"),
    ]


def motifs_for_arm(arm_id: str, left_axis: str, right_axis: str) -> list[str]:
    if arm_id == "A7LS_D":
        return ["control_flip", "sub", "safe_div_abs", "spread_rank"]
    base = ["mul", "sub", "spread_rank", "gated_sign", "safe_div_abs", "smooth_mul"]
    if arm_id in {"A7LS_A", "A7LS_C"}:
        base.extend(["relative_shock", "signed_spread", "mean_reversion_gate", "delta_x_divergence", "state_gate"])
    if arm_id == "A7LS_B":
        base.extend(["relative_shock", "signed_spread", "state_gate"])
    if "regime_state" in {left_axis, right_axis} or "listing_age_like" in {left_axis, right_axis}:
        return ["mul", "gated_sign", "smooth_mul", "state_gate", "signed_spread"]
    return base


def add_row(rows: list[dict[str, Any]], seen_expr: set[str], row: dict[str, Any], target: int) -> bool:
    if len(rows) >= target:
        return False
    expr = str(row["expression"])
    if expr in seen_expr:
        return False
    row["skeleton_key"] = skeleton(expr)
    row["production_key"] = stable_id(
        "prod",
        f"{row['a7ls_arm']}|{row['primary_field']}|{row['secondary_field']}|{row['primary_transform']}|{row['secondary_transform']}|{row['motif']}",
    )
    row["blueprint_id"] = stable_id("a7ls1", f"{row['a7ls_arm']}|{row['level']}|{expr}")
    rows.append(row)
    seen_expr.add(expr)
    return True


def generate_arm(arm: pd.Series, catalog: dict[str, list[str]]) -> pd.DataFrame:
    arm_id = str(arm["arm_id"])
    target = int(arm["generated_budget"])
    depth = str(arm["allowed_transform_depth"])
    rows: list[dict[str, Any]] = []
    seen_expr: set[str] = set()
    pairs = axis_pairs_for_arm(arm_id)
    transform_cache = {
        (axis, field): transform_set(field, axis, depth)
        for axis, fields in catalog.items()
        for field in fields
    }

    # L1 raw/single-axis probes are especially important for the raw arm.
    l1_cap = 5000 if arm_id == "A7LS_B" else 2500
    for axis in sorted({axis for pair in pairs for axis in pair}):
        for field in catalog.get(axis, []):
            for tname, expr in transform_cache.get((axis, field), [])[:28]:
                add_row(
                    rows,
                    seen_expr,
                    {
                        "a7ls_arm": arm_id,
                        "arm_name": arm["arm_name"],
                        "search_role": arm["search_role"],
                        "level": "L1_single_axis_raw_transform",
                        "candidate_role": "control_only" if arm_id == "A7LS_D" else "ordinary_alpha_probe",
                        "generation_priority": "P0" if arm_id in {"A7LS_A", "A7LS_B"} else "P1",
                        "semantic_pair": axis,
                        "motif": "single",
                        "primary_field": field,
                        "secondary_field": "",
                        "primary_semantic": axis,
                        "secondary_semantic": "",
                        "primary_transform": tname,
                        "secondary_transform": "",
                        "modifier_guard_required": axis in {"regime_state", "listing_age_like"},
                        "expression": expr,
                    },
                    l1_cap,
                )
                if len(rows) >= l1_cap:
                    break
            if len(rows) >= l1_cap:
                break
        if len(rows) >= l1_cap:
            break

    remaining_target = max(0, target - len(rows))
    per_pair_cap = max(500, int(remaining_target / max(1, len(pairs))) + 1)
    pair_counts: dict[tuple[str, str], int] = {pair: 0 for pair in pairs}

    for left_axis, right_axis in pairs:
        if len(rows) >= target:
            break
        key = (left_axis, right_axis)
        left_fields = catalog.get(left_axis, [])
        right_fields = catalog.get(right_axis, [])
        if not left_fields or not right_fields:
            continue
        motifs = motifs_for_arm(arm_id, left_axis, right_axis)
        for li, left_field in enumerate(left_fields):
            if len(rows) >= target or pair_counts[key] >= per_pair_cap:
                break
            for ri, right_field in enumerate(right_fields):
                if len(rows) >= target or pair_counts[key] >= per_pair_cap:
                    break
                if left_field == right_field:
                    continue
                left_ts = transform_cache.get((left_axis, left_field), [])[:32]
                right_ts = transform_cache.get((right_axis, right_field), [])[:32]
                for left_name, left_expr in left_ts:
                    if len(rows) >= target or pair_counts[key] >= per_pair_cap:
                        break
                    for right_name, right_expr in right_ts:
                        if len(rows) >= target or pair_counts[key] >= per_pair_cap:
                            break
                        for motif in motifs:
                            expr = motif_expr(left_expr, right_expr, motif)
                            ok = add_row(
                                rows,
                                seen_expr,
                                {
                                    "a7ls_arm": arm_id,
                                    "arm_name": arm["arm_name"],
                                    "search_role": arm["search_role"],
                                    "level": "L2_raw_multi_axis_interaction" if arm_id == "A7LS_B" else "L2_typed_arm_interaction",
                                    "candidate_role": "control_only" if arm_id == "A7LS_D" else "role_mixed_allowed",
                                    "generation_priority": "P0" if arm_id in {"A7LS_A", "A7LS_B"} else "P1",
                                    "semantic_pair": f"{left_axis}|{right_axis}" if left_axis != right_axis else left_axis,
                                    "motif": motif,
                                    "primary_field": left_field,
                                    "secondary_field": right_field,
                                    "primary_semantic": left_axis,
                                    "secondary_semantic": right_axis,
                                    "primary_transform": left_name,
                                    "secondary_transform": right_name,
                                    "modifier_guard_required": "regime_state" in {left_axis, right_axis}
                                    or "listing_age_like" in {left_axis, right_axis},
                                    "expression": expr,
                                },
                                target,
                            )
                            if ok:
                                pair_counts[key] += 1
                            if len(rows) >= target or pair_counts[key] >= per_pair_cap:
                                break

    # If a narrow arm still has budget after pair caps, do one finite uncapped refill pass.
    if len(rows) < target:
        for left_axis, right_axis in pairs:
            if len(rows) >= target:
                break
            for left_field in catalog.get(left_axis, []):
                if len(rows) >= target:
                    break
                for right_field in catalog.get(right_axis, []):
                    if len(rows) >= target:
                        break
                    if left_field == right_field:
                        continue
                    for left_name, left_expr in transform_cache.get((left_axis, left_field), [])[:40]:
                        if len(rows) >= target:
                            break
                        for right_name, right_expr in transform_cache.get((right_axis, right_field), [])[:40]:
                            if len(rows) >= target:
                                break
                            for motif in motifs_for_arm(arm_id, left_axis, right_axis):
                                add_row(
                                    rows,
                                    seen_expr,
                                    {
                                        "a7ls_arm": arm_id,
                                        "arm_name": arm["arm_name"],
                                        "search_role": arm["search_role"],
                                        "level": "L2_raw_multi_axis_interaction" if arm_id == "A7LS_B" else "L2_typed_arm_interaction",
                                        "candidate_role": "control_only" if arm_id == "A7LS_D" else "role_mixed_allowed",
                                        "generation_priority": "P0" if arm_id in {"A7LS_A", "A7LS_B"} else "P1",
                                        "semantic_pair": f"{left_axis}|{right_axis}" if left_axis != right_axis else left_axis,
                                        "motif": motif,
                                        "primary_field": left_field,
                                        "secondary_field": right_field,
                                        "primary_semantic": left_axis,
                                        "secondary_semantic": right_axis,
                                        "primary_transform": left_name,
                                        "secondary_transform": right_name,
                                        "modifier_guard_required": "regime_state" in {left_axis, right_axis}
                                        or "listing_age_like" in {left_axis, right_axis},
                                        "expression": motif_expr(left_expr, right_expr, motif),
                                    },
                                    target,
                                )
                                if len(rows) >= target:
                                    break
    return pd.DataFrame(rows)


def balanced_select(pool: pd.DataFrame, per_arm: int, *, for_numeric: bool) -> pd.DataFrame:
    selected: list[pd.Series] = []
    for arm_id, arm_df in pool.groupby("a7ls_arm", sort=False):
        target = per_arm
        arm_df = arm_df.sort_values(
            ["generation_priority", "semantic_pair", "motif", "blueprint_id"],
            ascending=[True, True, True, True],
        )
        if arm_id == "A7LS_B":
            axis_max = max(1, int(target * 0.25))
            skel_cap = 30 if for_numeric else 120
            axis_groups = {
                axis: group.reset_index(drop=True)
                for axis, group in arm_df.groupby("primary_semantic", sort=True)
            }
            axis_positions = {axis: 0 for axis in axis_groups}
            axis_counts = {axis: 0 for axis in axis_groups}
            skel_counts: dict[str, int] = {}
            used: set[str] = set()
            arm_selected: list[pd.Series] = []
            while len(arm_selected) < target:
                progressed = False
                for axis in sorted(axis_groups):
                    if len(arm_selected) >= target:
                        break
                    if axis_counts.get(axis, 0) >= axis_max:
                        continue
                    group = axis_groups[axis]
                    pos = axis_positions[axis]
                    while pos < len(group):
                        row = group.iloc[pos]
                        pos += 1
                        bid = str(row["blueprint_id"])
                        skel = str(row["skeleton_key"])
                        if bid in used:
                            continue
                        if skel_counts.get(skel, 0) >= skel_cap:
                            continue
                        arm_selected.append(row)
                        used.add(bid)
                        axis_counts[axis] = axis_counts.get(axis, 0) + 1
                        skel_counts[skel] = skel_counts.get(skel, 0) + 1
                        progressed = True
                        break
                    axis_positions[axis] = pos
                if not progressed:
                    break
            selected.extend(arm_selected)
            continue
        sem_cap = max(50, int(target * 0.18))
        motif_cap = max(50, int(target * 0.20))
        skel_cap = 12 if for_numeric else 40
        axis_cap = max(50, int(target * 0.18))
        sem_counts: dict[str, int] = {}
        motif_counts: dict[str, int] = {}
        skel_counts: dict[str, int] = {}
        axis_counts: dict[str, int] = {}
        arm_selected: list[pd.Series] = []
        for _, row in arm_df.iterrows():
            sem = str(row["semantic_pair"])
            motif = str(row["motif"])
            skel = str(row["skeleton_key"])
            axis = str(row["primary_semantic"])
            if sem_counts.get(sem, 0) >= sem_cap:
                continue
            if motif_counts.get(motif, 0) >= motif_cap:
                continue
            if skel_counts.get(skel, 0) >= skel_cap:
                continue
            if row["a7ls_arm"] == "A7LS_B" and axis_counts.get(axis, 0) >= axis_cap:
                continue
            arm_selected.append(row)
            sem_counts[sem] = sem_counts.get(sem, 0) + 1
            motif_counts[motif] = motif_counts.get(motif, 0) + 1
            skel_counts[skel] = skel_counts.get(skel, 0) + 1
            axis_counts[axis] = axis_counts.get(axis, 0) + 1
            if len(arm_selected) >= target:
                break
        if len(arm_selected) < target:
            used = {str(r["blueprint_id"]) for r in arm_selected}
            for _, row in arm_df.iterrows():
                if str(row["blueprint_id"]) in used:
                    continue
                arm_selected.append(row)
                used.add(str(row["blueprint_id"]))
                if len(arm_selected) >= target:
                    break
        selected.extend(arm_selected)
    out = pd.DataFrame(selected)
    return out.reset_index(drop=True)


def assign_shards(df: pd.DataFrame, rows_per_shard: int, prefix: str) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    out[f"{prefix}_shard"] = [
        f"{row.a7ls_arm.lower()}_{prefix}_s{idx // rows_per_shard:03d}"
        for idx, row in enumerate(out.itertuples(index=False))
    ]
    out["checkpoint_key"] = out[f"{prefix}_shard"] + "::" + out["blueprint_id"].astype(str)
    return out


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    ls0 = read_json(LS0 / "a7ls0_manifest.json")
    if not ls0.get("authorizes_a7ls1_blueprint_generation"):
        raise SystemExit(f"A7LS-0 does not authorize A7LS-1: {ls0.get('decision')}")

    arms = pd.read_csv(LS0 / "a7ls0_arm_budget_map.csv")
    catalog = field_catalog()
    frames: list[pd.DataFrame] = []
    for _, arm in arms.iterrows():
        frame = generate_arm(arm, catalog)
        frames.append(frame)
        print(f"[A7LS-1] generated {len(frame)} rows for {arm['arm_id']}", flush=True)
    pool = pd.concat(frames, ignore_index=True)

    pool_path = EXTERNAL / "a7ls1_full_blueprint_pool.csv"
    pool.to_csv(pool_path, index=False)

    materialization = balanced_select(pool, per_arm=10000, for_numeric=False)
    materialization["in_materialization_queue"] = True
    materialization["in_company_numeric_wave_queue"] = False
    materialization = assign_shards(materialization, rows_per_shard=500, prefix="materialization")
    numeric = balanced_select(materialization, per_arm=2000, for_numeric=True)
    numeric["in_company_numeric_wave_queue"] = True
    numeric = assign_shards(numeric, rows_per_shard=500, prefix="numeric")

    materialization.to_csv(RUNTIME / "a7ls1_materialization_wave_queue.csv", index=False)
    numeric.to_csv(RUNTIME / "a7ls1_numeric_wave_queue.csv", index=False)

    arm_summary = pool.groupby("a7ls_arm", dropna=False).agg(
        generated_rows=("blueprint_id", "size"),
        unique_expressions=("expression", "nunique"),
        semantic_pair_count=("semantic_pair", "nunique"),
        motif_count=("motif", "nunique"),
        skeleton_count=("skeleton_key", "nunique"),
        primary_field_count=("primary_field", "nunique"),
        secondary_field_count=("secondary_field", "nunique"),
    ).reset_index()
    mat_summary = materialization.groupby("a7ls_arm", dropna=False).agg(
        materialization_rows=("blueprint_id", "size"),
        materialization_semantic_pairs=("semantic_pair", "nunique"),
        materialization_motifs=("motif", "nunique"),
        materialization_skeletons=("skeleton_key", "nunique"),
    ).reset_index()
    num_summary = numeric.groupby("a7ls_arm", dropna=False).agg(
        numeric_rows=("blueprint_id", "size"),
        numeric_semantic_pairs=("semantic_pair", "nunique"),
        numeric_motifs=("motif", "nunique"),
        numeric_skeletons=("skeleton_key", "nunique"),
    ).reset_index()
    summary = arm_summary.merge(mat_summary, on="a7ls_arm", how="left").merge(num_summary, on="a7ls_arm", how="left")
    summary.to_csv(RUNTIME / "a7ls1_arm_generation_summary.csv", index=False)

    raw_axis_summary = (
        pool[pool["a7ls_arm"].eq("A7LS_B")]
        .groupby(["primary_semantic"], dropna=False)
        .agg(rows=("blueprint_id", "size"), semantic_pairs=("semantic_pair", "nunique"), motifs=("motif", "nunique"))
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    raw_axis_summary.to_csv(RUNTIME / "a7ls1_raw_arm_axis_summary.csv", index=False)

    shard_plan = pd.concat(
        [
            materialization.groupby(["a7ls_arm", "materialization_shard"], dropna=False).size().reset_index(name="rows").rename(columns={"materialization_shard": "shard"}),
            numeric.groupby(["a7ls_arm", "numeric_shard"], dropna=False).size().reset_index(name="rows").rename(columns={"numeric_shard": "shard"}),
        ],
        ignore_index=True,
    )
    shard_plan["wave"] = shard_plan["shard"].map(lambda x: "numeric" if "_numeric_" in str(x) else "materialization")
    shard_plan.to_csv(RUNTIME / "a7ls1_shard_plan.csv", index=False)

    output_manifest = pd.DataFrame(
        [
            {"path": str(pool_path).replace("\\", "/"), "rows": int(len(pool)), "location": "external", "purpose": "full 240k generated blueprint atlas"},
            {"path": str(RUNTIME / "a7ls1_materialization_wave_queue.csv").replace("\\", "/"), "rows": int(len(materialization)), "location": "repo", "purpose": "40k materialization wave queue"},
            {"path": str(RUNTIME / "a7ls1_numeric_wave_queue.csv").replace("\\", "/"), "rows": int(len(numeric)), "location": "repo", "purpose": "8k numeric checkpoint wave queue"},
        ]
    )
    output_manifest.to_csv(RUNTIME / "a7ls1_output_artifact_manifest.csv", index=False)

    blockers: list[str] = []
    if len(pool) < int(ls0["total_generated_budget"]):
        blockers.append("generated_rows_lt_budget")
    if len(materialization) < int(ls0["total_materialization_budget"]):
        blockers.append("materialization_rows_lt_budget")
    if len(numeric) < int(ls0["total_numeric_budget"]):
        blockers.append("numeric_rows_lt_budget")
    raw_numeric = numeric[numeric["a7ls_arm"].eq("A7LS_B")]
    if raw_numeric["primary_semantic"].nunique() < 5:
        blockers.append("raw_arm_numeric_active_axes_lt_5")
    if raw_numeric["primary_semantic"].value_counts(normalize=True).max() > 0.25:
        blockers.append("raw_arm_numeric_top_axis_share_gt_25pct")
    decision = "PASS_A7LS1_MULTI_ARM_BLUEPRINT_GENERATION_READY_FOR_A7LS2" if not blockers else "HOLD_A7LS1_BLUEPRINT_GENERATION_DIVERSITY_WEAK"
    manifest = {
        "stage": "A7LS-1",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7LS-0",
        "source_decision": ls0.get("decision"),
        "full_blueprint_pool_rows": int(len(pool)),
        "full_blueprint_pool_external_path": str(pool_path).replace("\\", "/"),
        "materialization_wave_rows": int(len(materialization)),
        "numeric_wave_rows": int(len(numeric)),
        "arm_count": int(pool["a7ls_arm"].nunique()),
        "raw_arm_generated_rows": int(pool["a7ls_arm"].eq("A7LS_B").sum()),
        "raw_arm_numeric_rows": int(len(raw_numeric)),
        "raw_arm_numeric_active_axes": int(raw_numeric["primary_semantic"].nunique()),
        "executes_generation": True,
        "executes_materialization": False,
        "executes_numeric_probe": False,
        "executes_search": False,
        "authorizes_a7ls2_materialization_wave": decision.startswith("PASS_"),
        "authorizes_a7ls3_numeric_wave": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls1_manifest.json", manifest)

    REPORT.write_text("\n".join([
        "# CRYPTO A7LS-1 MULTI-ARM BLUEPRINT GENERATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7LS-1 generates the four-arm checkpoint large-search blueprint atlas. The full 240k atlas is stored externally; repo artifacts keep the executable materialization and numeric checkpoint queues.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Arm Summary",
        "",
        md_table(summary, 20),
        "",
        "## Raw Arm Axis Summary",
        "",
        md_table(raw_axis_summary, 40),
        "",
        "## Output Artifacts",
        "",
        md_table(output_manifest, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "generation executed: true",
        "materialization executed: false",
        "numeric probe executed: false",
        "search/proof/shadow/live: false",
        "```",
    ]), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
