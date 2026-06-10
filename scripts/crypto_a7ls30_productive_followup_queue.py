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
DATE = "20260610"
STAGE = "A7LS-30"

A7LS29_ACCEPT = REPO / "runtime" / "a7ls29_productive_numeric_acceptance_20260610"
A7LS29_PULLBACK = Path(
    r"G:\AlphaFactory_CryptoData\company_pullback\a7ls29_productive_numeric_wave_20260610\unzipped"
)
RUNTIME = REPO / "runtime" / "a7ls30_productive_followup_queue_20260610"
REPORT = REPO / "reports" / f"CRYPTO_A7LS30_PRODUCTIVE_FOLLOWUP_QUEUE_{DATE}.md"
DATA_RUNTIME = Path(r"G:\AlphaFactory_CryptoData\research_runtime\a7ls30_productive_followup_queue_20260610")

TARGET_ROWS = 8192
ROWS_PER_SHARD = 512
FAMILY_TARGETS = {
    "basis_premium_like|positioning_like": 2048,
    "open_interest_like|positioning_like|regime_state": 2048,
    "open_interest_like|positioning_like|listing_age_like": 1536,
    "basis_premium_like|age_x_volatility|positioning_like": 1024,
    "open_interest_like|positioning_like": 1536,
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
WINDOWS = [3, 4, 6, 8, 12, 16, 24, 36, 48, 72, 96, 120, 168, 240, 336, 504, 720]

OPS = {
    "Mean",
    "Delta",
    "TSRank",
    "Decay",
    "Rank",
    "CSRank",
    "ZScore",
    "Mul",
    "Sub",
    "Add",
    "Neg",
    "Abs",
    "Sign",
    "SafeDiv",
    "Clip",
    "Winsor",
}


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

    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        return token if token in OPS else "F"

    return re.sub(r"[A-Za-z_][A-Za-z0-9_]*", repl, text)


def skeleton_key(semantic_pair: str, motif: str, expression: str) -> str:
    return f"{semantic_pair}|{motif}|{short_hash(normalize_skeleton(expression), 12)}"


def replace_one(expr: str, fields: list[str], replacement: str) -> str | None:
    present = [f for f in fields if re.search(rf"\b{re.escape(f)}\b", expr)]
    if not present:
        return None
    src = present[0]
    if src == replacement:
        return None
    return re.sub(rf"\b{re.escape(src)}\b", replacement, expr, count=1)


def window_variants(expr: str) -> list[tuple[str, str]]:
    found = [int(x) for x in re.findall(r",(\d+)\)", expr)]
    variants: list[tuple[str, str]] = []
    for old in sorted(set(found)):
        for new in WINDOWS:
            if new != old:
                variants.append((re.sub(rf",{old}\)", f",{new})", expr, count=1), f"window_{old}_to_{new}"))
    return variants


def field_swap_variants(expr: str, semantic_pair: str) -> list[tuple[str, str]]:
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

    variants: list[tuple[str, str]] = []
    for group_name, fields in groups:
        for replacement in fields:
            candidate = replace_one(expr, fields, replacement)
            if candidate and candidate != expr:
                variants.append((candidate, f"field_swap_{group_name}_to_{replacement}"))
    return variants


def wrapper_variants(expr: str) -> list[tuple[str, str]]:
    return [
        (f"CSRank({expr})", "wrap_csrank"),
        (f"ZScore({expr})", "wrap_zscore"),
        (f"Neg({expr})", "wrap_neg"),
        (f"Clip({expr},-3,3)", "wrap_clip"),
        (f"Sign({expr})", "wrap_sign"),
        (f"Abs({expr})", "wrap_abs"),
    ]


def interaction_variants(expr: str, semantic_pair: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if "positioning_like" in semantic_pair:
        out.extend(
            [
                (f"Mul({expr},Sign(Decay(account_position_divergence,24)))", "gate_account_divergence_24"),
                (f"Mul({expr},Sign(Decay(top_global_account_divergence,24)))", "gate_top_global_divergence_24"),
            ]
        )
    if "regime_state" not in semantic_pair:
        out.extend(
            [
                (f"Mul({expr},Sign(Decay(leverage_crowding_state,24)))", "gate_leverage_crowding"),
                (f"Mul({expr},Sign(Decay(liquidity_cycle_state,24)))", "gate_liquidity_cycle"),
            ]
        )
    if "open_interest_like" in semantic_pair:
        out.extend(
            [
                (f"Sub(CSRank({expr}),CSRank(Delta(open_interest_last,24)))", "oi_residual_24"),
                (f"SafeDiv({expr},Abs(ZScore(Mean(open_interest_last,168))))", "oi_scale_168"),
            ]
        )
    return out


def variants_for_parent(expr: str, semantic_pair: str, motif: str) -> list[tuple[str, str, str]]:
    variants: list[tuple[str, str, str]] = [(expr, "parent_identity", "keep")]
    variants += [(v, "window_grid", d) for v, d in window_variants(expr)]
    variants += [(v, "same_type_field_swap", d) for v, d in field_swap_variants(expr, semantic_pair)]
    variants += [(v, "wrapper_probe", d) for v, d in wrapper_variants(expr)]
    variants += [(v, "interaction_probe", d) for v, d in interaction_variants(expr, semantic_pair)]
    if motif in {"spread_rank", "signed_spread", "seed_sub", "sub"}:
        variants.append((f"Abs({expr})", "magnitude_probe", "abs"))
        variants.append((f"Sign({expr})", "direction_probe", "sign"))
    return variants


def load_parents() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for name in ["a7ls29_selected_top160.csv", "a7ls29_non_l7_top240.csv"]:
        path = A7LS29_ACCEPT / name
        if path.exists():
            frames.append(pd.read_csv(path))
    if A7LS29_PULLBACK.exists():
        for path in sorted(A7LS29_PULLBACK.rglob("*portfolio_marginal_proxy.csv")):
            df = pd.read_csv(path)
            frames.append(df[df["label_family"].ne("L7_ranked_future_return")].copy())
    if not frames:
        raise FileNotFoundError("No A7LS29 parent evidence found")
    parents = pd.concat(frames, ignore_index=True)
    parents = parents[parents["expression"].notna()].copy()
    for col in ["score_no_may", "control_ratio_premay_max", "robust_median_tstat_floor", "cost10_recent_oriented"]:
        parents[col] = pd.to_numeric(parents.get(col, 0.0), errors="coerce").fillna(0.0)
    parents = parents[
        parents["semantic_pair"].isin(FAMILY_TARGETS)
        & parents["label_family"].ne("L7_ranked_future_return")
        & (parents["control_ratio_premay_max"] < 0.98)
    ].copy()
    parents["parent_score"] = (
        parents["score_no_may"]
        + (1.0 - parents["control_ratio_premay_max"].clip(upper=1.0)) * 100.0
        + parents["robust_median_tstat_floor"].clip(lower=0.0) * 25.0
        + parents["cost10_recent_oriented"].clip(lower=0.0) * 50.0
    )
    return parents.sort_values(["parent_score", "score_no_may"], ascending=[False, False])


def balanced_take(df: pd.DataFrame, target: int) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.sort_values(["parent_score", "approval_score", "blueprint_id"], ascending=[False, False, True])
    rows: list[dict[str, Any]] = []
    seen_expr: set[str] = set()
    parent_count: dict[str, int] = {}
    motif_cap = max(160, math.ceil(target / max(1, df["motif"].nunique())) + 80)
    parent_cap = 96
    motif_count: dict[str, int] = {}
    for row in df.to_dict("records"):
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
        for row in df.to_dict("records"):
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
    DATA_RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    parents = load_parents()
    candidates: list[dict[str, Any]] = []
    for parent in parents.to_dict("records"):
        parent_id = str(parent.get("blueprint_id", "parent"))
        semantic_pair = str(parent["semantic_pair"])
        motif = str(parent["motif"])
        parent_score = float(parent.get("parent_score", parent.get("score_no_may", 0.0)))
        for expr, kind, detail in variants_for_parent(str(parent["expression"]), semantic_pair, motif):
            approval_score = parent_score
            if kind == "interaction_probe":
                approval_score += 25.0
            if "open_interest_like" in semantic_pair:
                approval_score += 35.0
            if "regime_state" in semantic_pair or "listing_age_like" in semantic_pair:
                approval_score += 20.0
            if "basis_premium_like|positioning_like" == semantic_pair:
                approval_score -= 12.0
            candidates.append(
                {
                    "blueprint_id": "a7ls30_" + short_hash(f"{parent_id}|{expr}|{kind}|{detail}", 16),
                    "parent_blueprint_id": parent_id,
                    "expression": expr,
                    "semantic_pair": semantic_pair,
                    "motif": motif,
                    "parent_label_family": parent.get("label_family", ""),
                    "parent_label_horizon_h": parent.get("label_horizon_h", ""),
                    "approval_tier": "A7LS30_PRODUCTIVE_FOLLOWUP_EXPANSION",
                    "approval_score": approval_score,
                    "parent_score": parent_score,
                    "mutation_kind": kind,
                    "mutation_detail": detail,
                    "authorizes_search": False,
                    "skeleton_key": skeleton_key(semantic_pair, motif, expr),
                    "source_stage": "A7LS29_ACCEPTANCE_NO_SEARCH_AUTH",
                }
            )

    cand = pd.DataFrame(candidates).drop_duplicates("expression").copy()
    selected_parts: list[pd.DataFrame] = []
    for family, target in FAMILY_TARGETS.items():
        part = cand[cand["semantic_pair"].eq(family)].copy()
        selected_parts.append(balanced_take(part, target))
    queue = pd.concat(selected_parts, ignore_index=True).drop_duplicates("expression")
    if len(queue) < TARGET_ROWS:
        filler = cand[~cand["expression"].isin(set(queue["expression"]))].copy()
        queue = pd.concat([queue, balanced_take(filler, TARGET_ROWS - len(queue))], ignore_index=True)
    queue = queue.head(TARGET_ROWS).copy()
    queue["target_shard"] = [f"a7ls30_prod_s{idx // ROWS_PER_SHARD:03d}" for idx in range(len(queue))]

    queue_path = RUNTIME / "a7ls30_productive_followup_queue.csv"
    queue.to_csv(queue_path, index=False)
    queue.to_csv(DATA_RUNTIME / queue_path.name, index=False)

    family_summary = queue.groupby(["semantic_pair", "motif"], dropna=False).size().reset_index(name="queue_rows").sort_values("queue_rows", ascending=False)
    mutation_summary = queue.groupby(["mutation_kind", "mutation_detail"], dropna=False).size().reset_index(name="queue_rows").sort_values("queue_rows", ascending=False)
    shard_summary = queue.groupby("target_shard", dropna=False).size().reset_index(name="queue_rows")
    base_parent_summary = queue.groupby("parent_blueprint_id", dropna=False).size().reset_index(name="child_rows").sort_values("child_rows", ascending=False)
    for name, df in {
        "a7ls30_family_summary.csv": family_summary,
        "a7ls30_mutation_summary.csv": mutation_summary,
        "a7ls30_shard_plan.csv": shard_summary,
        "a7ls30_parent_usage_summary.csv": base_parent_summary,
    }.items():
        df.to_csv(RUNTIME / name, index=False)
        df.to_csv(DATA_RUNTIME / name, index=False)

    manifest = {
        "stage": STAGE,
        "generated_at": now_iso(),
        "decision": "PASS_A7LS30_PRODUCTIVE_FOLLOWUP_QUEUE_BUILT_NO_SEARCH_AUTH",
        "queue_rows": int(len(queue)),
        "rows_per_shard": ROWS_PER_SHARD,
        "shard_count": int(math.ceil(len(queue) / ROWS_PER_SHARD)),
        "parent_rows_loaded": int(len(parents)),
        "candidate_rows_before_balance": int(len(cand)),
        "family_targets": FAMILY_TARGETS,
        "queue_path": str(queue_path),
        "data_queue_path": str(DATA_RUNTIME / queue_path.name),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "next_required": ["A7LS30 field gate", "A7LS30 company numeric probe"],
    }
    write_json(RUNTIME / "a7ls30_productive_followup_manifest.json", manifest)
    write_json(DATA_RUNTIME / "a7ls30_productive_followup_manifest.json", manifest)

    report = f"""# CRYPTO A7LS30 Productive Follow-Up Queue {DATE}

## Decision

`{manifest['decision']}`

A7LS30 compiles an 8192-row numeric-probe queue from A7LS29 accepted evidence. It is deliberately larger than A7LS29, but it keeps family quotas so the next run expands productive information axes instead of only repeating basis/premium variants.

## Counts

- queue_rows: {manifest['queue_rows']}
- shard_count: {manifest['shard_count']}
- rows_per_shard: {manifest['rows_per_shard']}
- parent_rows_loaded: {manifest['parent_rows_loaded']}
- candidate_rows_before_balance: {manifest['candidate_rows_before_balance']}

## Family Summary

{md_table(family_summary, 60)}

## Mutation Summary

{md_table(mutation_summary, 60)}

## Shard Plan

{md_table(shard_summary, 40)}

## Boundary

```text
This queue authorizes numeric probes only after field gate PASS.
It does not authorize formula search, alpha proof, shadow, paper, or live.
```

## Outputs

- `{queue_path}`
- `{DATA_RUNTIME / queue_path.name}`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
