from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260609"
STAGE = "A7LS-29"

A7LS28B_ACCEPT = Path(r"G:\AlphaFactory_CryptoData\research_runtime\a7ls28b_targeted_numeric_acceptance_20260609")
A7LS28B_QUEUE = Path(
    r"G:\AlphaFactory_CryptoData\research_runtime\a7ls28b_broader_targeted_space_queue_20260609\a7ls28b_targeted_blueprint_queue.csv"
)
FIELD_GATE1 = REPO / "runtime" / "a7ls_field_gate1_contract_backfill_20260609"
FIELD_GATE1_REGISTRY = FIELD_GATE1 / "a7ls_field_gate1_runner_extension_registry.json"
RUNTIME = REPO / "runtime" / "a7ls29_productive_family_queue_20260609"
REPORT = REPO / "reports" / f"CRYPTO_A7LS29_PRODUCTIVE_FAMILY_QUEUE_{DATE}.md"

TARGET_ROWS = 6144
ROWS_PER_SHARD = 512
FAMILY_TARGETS = {
    "basis_premium_like|positioning_like": 2304,
    "open_interest_like|positioning_like|regime_state": 1536,
    "open_interest_like|positioning_like|listing_age_like": 1024,
    "basis_premium_like|age_x_volatility|positioning_like": 768,
    "open_interest_like|positioning_like": 512,
}

BASIS_FIELDS = ["mark_index_basis_bps", "mark_trade_basis_bps", "premium_close_bps", "basis_abs_168h", "premium_abs_168h"]
POSITIONING_FIELDS = [
    "top_long_short_position_ratio_last",
    "top_long_short_position_ratio_mean",
    "top_long_short_account_ratio_last",
    "top_long_short_account_ratio_mean",
    "global_long_short_account_ratio_last",
    "global_long_short_account_ratio_mean",
    "account_position_divergence",
    "top_global_account_divergence",
]
OI_FIELDS = [
    "open_interest_last",
    "open_interest_mean",
    "open_interest_value_last",
    "open_interest_change_24h",
    "open_interest_value_change_24h",
]
REGIME_FIELDS = [
    "market_breadth_state",
    "liquidity_cycle_state",
    "leverage_crowding_state",
    "basis_dislocation_state",
    "stress_proxy_state",
]
AGE_FIELDS = ["listing_age_days", "log1p_listing_age_days", "sqrt_listing_age_days", "age_percentile_active_universe"]
AGE_VOL_FIELDS = ["age_x_volatility", "rolling_coverage_168h"]
WINDOWS = [3, 4, 6, 8, 12, 16, 24, 36, 48, 72, 96, 168, 240, 336, 504]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
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


def short_hash(text: str, n: int = 16) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:n]


def normalize_skeleton(expression: str) -> str:
    text = re.sub(r"\b\d+\b", "W", str(expression))
    text = re.sub(r"[A-Za-z_][A-Za-z0-9_]*", lambda m: "F" if m.group(0) not in {"Mean", "Delta", "TSRank", "Decay", "Rank", "CSRank", "ZScore", "Mul", "Sub", "Add", "Neg", "Abs", "Sign", "SafeDiv", "Clip", "Winsor"} else m.group(0), text)
    return text


def skeleton_key(semantic_pair: str, motif: str, expression: str) -> str:
    return f"{semantic_pair}|{motif}|{short_hash(normalize_skeleton(expression), 12)}"


def score_parent(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in [
        "control_ratio_premay_max",
        "robust_median_tstat_floor",
        "robust_min_tstat_floor",
        "avg_n_obs_recent",
        "label_horizon_h",
        "one_bar_lag_recent_oriented",
        "cost5_recent_oriented",
    ]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    out["parent_score"] = (
        (1.0 - out["control_ratio_premay_max"].clip(upper=1.0)).fillna(0.0) * 1000.0
        + out["robust_median_tstat_floor"].fillna(0.0).clip(lower=0.0) * 100.0
        + out["avg_n_obs_recent"].fillna(0.0)
        + out["one_bar_lag_recent_oriented"].fillna(0.0).clip(lower=0.0) * 100.0
    )
    label_bonus = {
        "L0_raw_forward_return": 80.0,
        "L1_cross_sectional_relative_return": 80.0,
        "L3_liquidity_tier_relative_return": 60.0,
        "L5_vol_adjusted_return": 40.0,
    }
    out["parent_score"] += out["label_family"].map(label_bonus).fillna(0.0)
    return out


def replace_one(expr: str, fields: list[str], replacement: str) -> str | None:
    present = [f for f in fields if f in expr]
    if not present:
        return None
    src = present[0]
    if src == replacement:
        return None
    return expr.replace(src, replacement)


def window_variants(expr: str) -> list[tuple[str, str]]:
    found = [int(x) for x in re.findall(r",(\d+)\)", expr)]
    variants: list[tuple[str, str]] = []
    for old in sorted(set(found)):
        for new in WINDOWS:
            if new == old:
                continue
            variants.append((re.sub(rf",{old}\)", f",{new})", expr, count=1), f"window_{old}_to_{new}"))
    return variants


def wrapper_variants(expr: str) -> list[tuple[str, str]]:
    return [
        (f"CSRank({expr})", "wrap_csrank"),
        (f"ZScore({expr})", "wrap_zscore"),
        (f"Neg({expr})", "wrap_neg"),
        (f"Clip({expr},-3,3)", "wrap_clip"),
    ]


def field_swap_variants(expr: str, semantic_pair: str) -> list[tuple[str, str]]:
    variants: list[tuple[str, str]] = []
    groups: list[tuple[str, list[str]]] = []
    if "basis_premium_like" in semantic_pair:
        groups.append(("basis", BASIS_FIELDS))
    if "positioning_like" in semantic_pair:
        groups.append(("positioning", POSITIONING_FIELDS))
    if "open_interest_like" in semantic_pair:
        groups.append(("open_interest", OI_FIELDS))
    if "regime_state" in semantic_pair:
        groups.append(("regime", REGIME_FIELDS))
    if "listing_age_like" in semantic_pair:
        groups.append(("listing_age", AGE_FIELDS))
    if "age_x_volatility" in semantic_pair:
        groups.append(("age_x_vol", AGE_VOL_FIELDS))
    for group_name, fields in groups:
        for replacement in fields:
            candidate = replace_one(expr, fields, replacement)
            if candidate and candidate != expr:
                variants.append((candidate, f"field_swap_{group_name}_to_{replacement}"))
    return variants


def structural_variants(expr: str, semantic_pair: str, motif: str) -> list[tuple[str, str, str]]:
    variants: list[tuple[str, str, str]] = [(expr, "parent_identity", "keep")]
    variants += [(v, "window_grid", detail) for v, detail in window_variants(expr)]
    variants += [(v, "same_type_field_swap", detail) for v, detail in field_swap_variants(expr, semantic_pair)]
    variants += [(v, "wrapper_probe", detail) for v, detail in wrapper_variants(expr)]
    if motif in {"spread_rank", "signed_spread", "seed_sub"}:
        variants.append((f"Abs({expr})", "magnitude_probe", "abs"))
        variants.append((f"Sign({expr})", "direction_probe", "sign"))
    return variants


def balanced_take(candidates: pd.DataFrame, target: int) -> pd.DataFrame:
    if candidates.empty:
        return candidates
    candidates = candidates.sort_values(["parent_score", "blueprint_id"], ascending=[False, True]).copy()
    rows = []
    motif_cap = max(96, math.ceil(target / max(1, candidates["motif"].nunique())))
    parent_cap = 48
    seen_expr: set[str] = set()
    motif_count: dict[str, int] = {}
    parent_count: dict[str, int] = {}
    for row in candidates.to_dict("records"):
        expr = str(row["expression"])
        if expr in seen_expr:
            continue
        motif = str(row["motif"])
        parent = str(row["parent_blueprint_id"])
        if motif_count.get(motif, 0) >= motif_cap:
            continue
        if parent_count.get(parent, 0) >= parent_cap:
            continue
        rows.append(row)
        seen_expr.add(expr)
        motif_count[motif] = motif_count.get(motif, 0) + 1
        parent_count[parent] = parent_count.get(parent, 0) + 1
        if len(rows) >= target:
            break
    if len(rows) < target:
        for row in candidates.to_dict("records"):
            expr = str(row["expression"])
            if expr in seen_expr:
                continue
            rows.append(row)
            seen_expr.add(expr)
            if len(rows) >= target:
                break
    return pd.DataFrame(rows).head(target)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    registry = json.loads(FIELD_GATE1_REGISTRY.read_text(encoding="utf-8"))
    if not registry.get("field_roles"):
        raise RuntimeError("FIELD-GATE-1 registry is empty")

    non_l7 = pd.read_csv(A7LS28B_ACCEPT / "a7ls28b_non_l7_response_rows.csv")
    source_queue = pd.read_csv(A7LS28B_QUEUE)
    non_l7 = score_parent(non_l7)
    strong = non_l7[
        (non_l7["control_ratio_premay_max"] < 0.90)
        & (non_l7["premay_all_positive"].astype(str).str.lower().eq("true"))
        & (non_l7["lag_ok"].astype(str).str.lower().eq("true"))
        & (non_l7["robust_ok"].astype(str).str.lower().eq("true"))
    ].copy()
    parents = (
        strong.sort_values(["parent_score", "control_ratio_premay_max"], ascending=[False, True])
        .drop_duplicates(["blueprint_id", "label_family", "label_horizon_h"])
        .merge(
            source_queue[["blueprint_id", "parent_blueprint_id", "approval_tier", "approval_score"]],
            on="blueprint_id",
            how="left",
        )
    )
    parents["parent_blueprint_id"] = parents["parent_blueprint_id"].fillna(parents["blueprint_id"])
    parents["approval_tier"] = parents["approval_tier"].fillna("A7LS28B_PRODUCTIVE_NON_L7_PARENT")
    parents["approval_score"] = pd.to_numeric(parents["approval_score"], errors="coerce").fillna(parents["parent_score"])

    candidate_rows: list[dict[str, Any]] = []
    for parent in parents.to_dict("records"):
        semantic_pair = str(parent["semantic_pair"])
        if semantic_pair not in FAMILY_TARGETS:
            continue
        expr = str(parent["expression"])
        for variant_expr, mutation_kind, mutation_detail in structural_variants(expr, semantic_pair, str(parent["motif"])):
            key_material = "|".join(
                [
                    variant_expr,
                    semantic_pair,
                    str(parent["motif"]),
                    str(parent["label_family"]),
                    str(parent["label_horizon_h"]),
                    mutation_kind,
                    mutation_detail,
                ]
            )
            candidate_rows.append(
                {
                    "blueprint_id": "a7ls29_" + short_hash(key_material, 16),
                    "parent_blueprint_id": parent["blueprint_id"],
                    "expression": variant_expr,
                    "semantic_pair": semantic_pair,
                    "motif": parent["motif"],
                    "parent_label_family": parent["label_family"],
                    "parent_label_horizon_h": int(parent["label_horizon_h"]),
                    "approval_tier": "A7LS29_PRODUCTIVE_FAMILY_EXPANSION",
                    "approval_score": float(parent["parent_score"]),
                    "parent_score": float(parent["parent_score"]),
                    "mutation_kind": mutation_kind,
                    "mutation_detail": mutation_detail,
                    "authorizes_search": False,
                    "skeleton_key": skeleton_key(semantic_pair, str(parent["motif"]), variant_expr),
                    "source_stage": "A7LS28B_ACCEPTANCE_PLUS_FIELD_GATE1",
                }
            )

    candidates = pd.DataFrame(candidate_rows).drop_duplicates("blueprint_id")
    selected_parts = []
    coverage_rows = []
    for semantic_pair, target in FAMILY_TARGETS.items():
        sub = candidates[candidates["semantic_pair"].eq(semantic_pair)].copy()
        chosen = balanced_take(sub, target)
        selected_parts.append(chosen)
        coverage_rows.append(
            {
                "semantic_pair": semantic_pair,
                "target_rows": target,
                "candidate_rows": int(len(sub)),
                "selected_rows": int(len(chosen)),
                "motif_count": int(chosen["motif"].nunique()) if not chosen.empty else 0,
                "skeleton_count": int(chosen["skeleton_key"].nunique()) if not chosen.empty else 0,
            }
        )
    queue = pd.concat(selected_parts, ignore_index=True).drop_duplicates("blueprint_id").head(TARGET_ROWS)
    queue["target_shard"] = [
        f"a7ls29_prod_s{idx // ROWS_PER_SHARD:03d}" for idx in range(len(queue))
    ]
    shard_rows = []
    for shard, group in queue.groupby("target_shard", sort=True):
        shard_rows.append(
            {
                "shard_id": shard,
                "rows": int(len(group)),
                "start_row": int(group.index.min()),
                "end_row_exclusive": int(group.index.max()) + 1,
                "semantic_pair_count": int(group["semantic_pair"].nunique()),
                "motif_count": int(group["motif"].nunique()),
                "skeleton_count": int(group["skeleton_key"].nunique()),
            }
        )
    coverage = pd.DataFrame(coverage_rows)
    family_summary = (
        queue.groupby(["semantic_pair", "motif", "parent_label_family"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values("rows", ascending=False)
    )
    mutation_summary = queue.groupby("mutation_kind").size().reset_index(name="rows").sort_values("rows", ascending=False)
    shard_plan = pd.DataFrame(shard_rows)

    queue.to_csv(RUNTIME / "a7ls29_productive_family_queue.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ls29_shard_plan.csv", index=False)
    coverage.to_csv(RUNTIME / "a7ls29_family_coverage.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ls29_family_summary.csv", index=False)
    mutation_summary.to_csv(RUNTIME / "a7ls29_mutation_summary.csv", index=False)

    manifest = {
        "stage": STAGE,
        "decision": "PASS_A7LS29_PRODUCTIVE_FAMILY_QUEUE_BUILT_NO_NUMERIC_EXECUTION",
        "generated_at": now_iso(),
        "input_non_l7_rows": int(len(non_l7)),
        "strong_parent_rows": int(len(strong)),
        "candidate_rows": int(len(candidates)),
        "queue_rows": int(len(queue)),
        "target_rows": TARGET_ROWS,
        "rows_per_shard": ROWS_PER_SHARD,
        "shard_count": int(shard_plan.shape[0]),
        "field_gate1_registry": str(FIELD_GATE1_REGISTRY),
        "field_gate1_field_count": len(registry.get("field_roles", {})),
        "skeleton_key_present": "skeleton_key" in queue.columns,
        "skeleton_count": int(queue["skeleton_key"].nunique()),
        "authorizes_numeric_compute": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(RUNTIME / "a7ls29_manifest.json", manifest)

    report = f"""# CRYPTO A7LS29 Productive Family Queue {DATE}

## Decision

`{manifest["decision"]}`

A7LS29 compiles a larger queue from A7LS28B productive non-L7 families. It consumes A7LS-FIELD-GATE-1 registry and adds explicit `skeleton_key` values so the portfolio proxy does not collapse the selected queue to one item per shard.

## Counts

- input_non_l7_rows: {manifest["input_non_l7_rows"]}
- strong_parent_rows: {manifest["strong_parent_rows"]}
- candidate_rows: {manifest["candidate_rows"]}
- queue_rows: {manifest["queue_rows"]}
- rows_per_shard: {manifest["rows_per_shard"]}
- shard_count: {manifest["shard_count"]}
- skeleton_count: {manifest["skeleton_count"]}
- field_gate1_field_count: {manifest["field_gate1_field_count"]}

## Family Coverage

{md_table(coverage, 20)}

## Mutation Summary

{md_table(mutation_summary, 20)}

## Family Summary

{md_table(family_summary, 60)}

## Outputs

- `{RUNTIME / "a7ls29_productive_family_queue.csv"}`
- `{RUNTIME / "a7ls29_shard_plan.csv"}`
- `{RUNTIME / "a7ls29_family_coverage.csv"}`
- `{RUNTIME / "a7ls29_family_summary.csv"}`
- `{RUNTIME / "a7ls29_mutation_summary.csv"}`
- `{RUNTIME / "a7ls29_manifest.json"}`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
