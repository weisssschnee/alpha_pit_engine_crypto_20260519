from __future__ import annotations

import hashlib
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260610"
STAGE = "A7RAW-0"

FIELD_ROUTE_MAP = REPO / "runtime" / "a7ls30_field_gate_20260610" / "a7ls_field_gate_field_route_map.csv"
RUNTIME = REPO / "runtime" / "a7raw0_light_governed_large_space_queue_20260610"
REPORT = REPO / "reports" / f"CRYPTO_A7RAW0_LIGHT_GOVERNED_LARGE_SPACE_QUEUE_{DATE}.md"
DATA_RUNTIME = Path(r"G:\AlphaFactory_CryptoData\research_runtime\a7raw0_light_governed_large_space_queue_20260610")

TARGET_ROWS = 16384
ROWS_PER_SHARD = 512
RNG_SEED = 20260610

WINDOWS_FAST = [3, 4, 6, 8, 12, 16, 24, 36, 48, 72]
WINDOWS_SLOW = [96, 120, 168, 240, 336, 504, 720]
WINDOWS_ALL = WINDOWS_FAST + WINDOWS_SLOW

FIELD_SEMANTIC = {
    "mark_index_basis_bps": "basis",
    "mark_trade_basis_bps": "basis",
    "premium_close_bps": "basis",
    "basis_abs_168h": "basis",
    "premium_abs_168h": "basis",
    "open_interest_last": "open_interest",
    "open_interest_mean": "open_interest",
    "open_interest_change_24h": "open_interest",
    "open_interest_value_last": "open_interest",
    "open_interest_value_change_24h": "open_interest",
    "top_long_short_position_ratio_last": "positioning",
    "top_long_short_position_ratio_mean": "positioning",
    "top_long_short_account_ratio_last": "positioning",
    "top_long_short_account_ratio_mean": "positioning",
    "global_long_short_account_ratio_last": "positioning",
    "global_long_short_account_ratio_mean": "positioning",
    "account_position_divergence": "positioning",
    "top_global_account_divergence": "positioning",
    "taker_buy_sell_volume_ratio_last": "taker_flow",
    "taker_buy_sell_volume_ratio_mean": "taker_flow",
    "market_breadth_state": "regime",
    "liquidity_cycle_state": "regime",
    "leverage_crowding_state": "regime",
    "basis_dislocation_state": "regime",
    "stress_proxy_state": "regime",
    "listing_age_days": "age",
    "log1p_listing_age_days": "age",
    "sqrt_listing_age_days": "age",
    "age_percentile_active_universe": "age",
    "age_x_volatility": "age_vol",
    "rolling_coverage_168h": "coverage",
}

BASE_ALLOWED = {
    "basis",
    "open_interest",
    "positioning",
    "taker_flow",
    "regime",
    "age",
    "age_vol",
    "coverage",
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


def load_field_pool() -> pd.DataFrame:
    df = pd.read_csv(FIELD_ROUTE_MAP)
    df = df[df["is_system_required"].astype(str).str.lower().ne("true")].copy()
    df = df[df["contract_status"].astype(str).str.startswith("OK_")].copy()
    df["semantic"] = df["field"].map(FIELD_SEMANTIC)
    df = df[df["semantic"].isin(BASE_ALLOWED)].copy()
    return df.sort_values(["semantic", "field"])


def transform_expr(field: str, semantic: str, rng: random.Random) -> list[tuple[str, str]]:
    windows = rng.sample(WINDOWS_ALL, k=min(5, len(WINDOWS_ALL)))
    out: list[tuple[str, str]] = []
    for w in windows:
        if semantic in {"regime", "age", "age_vol", "coverage"}:
            out.extend(
                [
                    (f"CSRank({field})", "level_csrank"),
                    (f"Sign(TSRank({field},{w}))", "state_tsrank_sign"),
                    (f"Decay({field},{w})", "state_decay"),
                ]
            )
        elif semantic in {"basis", "open_interest", "positioning", "taker_flow"}:
            out.extend(
                [
                    (f"ZScore(Mean({field},{w}))", "zmean"),
                    (f"CSRank(Delta({field},{w}))", "cs_delta"),
                    (f"TSRank({field},{w})", "tsrank"),
                    (f"Decay({field},{w})", "decay"),
                    (f"Abs(ZScore(Mean({field},{w})))", "abs_zmean"),
                ]
            )
    return out


def pair_templates(
    left: tuple[str, str, str],
    right: tuple[str, str, str],
    rng: random.Random,
) -> list[tuple[str, str]]:
    lf, ls, le = left
    rf, rs, re = right
    out: list[tuple[str, str]] = []
    out.extend(
        [
            (f"Sub(CSRank({le}),CSRank({re}))", "raw_spread_rank"),
            (f"Mul(CSRank({le}),Sign({re}))", "raw_signed_mul"),
            (f"SafeDiv({le},Abs({re}))", "raw_safe_div_abs"),
            (f"Mul({le},{re})", "raw_mul"),
        ]
    )
    if rs in {"regime", "age", "age_vol", "coverage"}:
        out.extend(
            [
                (f"Mul({le},Sign({re}))", "raw_state_gate"),
                (f"Sub(CSRank({le}),CSRank({re}))", "raw_state_relative"),
            ]
        )
    if ls == rs:
        out.append((f"Sub(CSRank({le}),CSRank({re}))", "raw_same_semantic_spread"))
    if {"open_interest", "taker_flow"} <= {ls, rs}:
        out.append((f"Mul(CSRank({le}),CSRank({re}))", "raw_oi_flow_interaction"))
    if {"basis", "open_interest"} <= {ls, rs}:
        out.append((f"SafeDiv(Sub(CSRank({le}),CSRank({re})),Abs({re}))", "raw_basis_oi_scaled_spread"))
    if {"basis", "taker_flow"} <= {ls, rs}:
        out.append((f"Mul(Sub(CSRank({le}),CSRank({re})),Sign({re}))", "raw_basis_flow_signed_spread"))
    rng.shuffle(out)
    return out


def skeleton_key(semantic_pair: str, motif: str, expression: str) -> str:
    simplified = expression
    for token in sorted(FIELD_SEMANTIC, key=len, reverse=True):
        simplified = simplified.replace(token, "F")
    for w in WINDOWS_ALL:
        simplified = simplified.replace(str(w), "W")
    return f"{semantic_pair}|{motif}|{short_hash(simplified, 12)}"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    DATA_RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)
    fields = load_field_pool()
    if fields.empty:
        raise RuntimeError("empty field pool")

    transforms: list[tuple[str, str, str, str]] = []
    for row in fields.to_dict("records"):
        for expr, motif in transform_expr(str(row["field"]), str(row["semantic"]), rng):
            transforms.append((str(row["field"]), str(row["semantic"]), expr, motif))

    rows: list[dict[str, Any]] = []
    semantic_cap = math.ceil(TARGET_ROWS * 0.18)
    skeleton_cap = 48
    field_cap = math.ceil(TARGET_ROWS * 0.20)
    sem_count: dict[str, int] = {}
    skel_count: dict[str, int] = {}
    field_count: dict[str, int] = {}
    seen_expr: set[str] = set()
    target_candidates = TARGET_ROWS * 24
    attempts = 0
    max_attempts = target_candidates * 20
    transform_count = len(transforms)
    candidate_rows_before_governance = 0
    while len(rows) < TARGET_ROWS and attempts < max_attempts:
        attempts += 1
        left = transforms[rng.randrange(transform_count)]
        right = transforms[rng.randrange(transform_count)]
        lf, ls, le, lm = left
        rf, rs, re, rm = right
        if lf == rf and lm == rm:
            continue
        semantic_pair = "|".join(sorted([ls, rs]))
        templates = pair_templates((lf, ls, le), (rf, rs, re), rng)
        expr, motif = templates[0]
        skel = skeleton_key(semantic_pair, motif, expr)
        priority_score = 0.0
        if "open_interest" in semantic_pair:
            priority_score += 20
        if "taker_flow" in semantic_pair:
            priority_score += 20
        if "regime" in semantic_pair:
            priority_score += 15
        if "basis" in semantic_pair:
            priority_score += 5
        if "age" in semantic_pair:
            priority_score += 10
        priority_score += {
            "raw_safe_div_abs": 12,
            "raw_state_gate": 10,
            "raw_oi_flow_interaction": 14,
            "raw_basis_oi_scaled_spread": 12,
            "raw_basis_flow_signed_spread": 12,
            "raw_spread_rank": 8,
            "raw_mul": 4,
        }.get(motif, 0)
        candidate_rows_before_governance += 1
        if expr in seen_expr:
            continue
        if sem_count.get(semantic_pair, 0) >= semantic_cap:
            continue
        if skel_count.get(skel, 0) >= skeleton_cap:
            continue
        if field_count.get(lf, 0) >= field_cap or field_count.get(rf, 0) >= field_cap:
            continue
        rows.append(
            {
                "expression": expr,
                "semantic_pair": semantic_pair,
                "motif": motif,
                "left_field": lf,
                "right_field": rf,
                "left_semantic": ls,
                "right_semantic": rs,
                "left_transform": lm,
                "right_transform": rm,
                "skeleton_key": skel,
                "priority_score": priority_score,
            }
        )
        seen_expr.add(expr)
        sem_count[semantic_pair] = sem_count.get(semantic_pair, 0) + 1
        skel_count[skel] = skel_count.get(skel, 0) + 1
        field_count[lf] = field_count.get(lf, 0) + 1
        field_count[rf] = field_count.get(rf, 0) + 1

    queue = pd.DataFrame(rows).head(TARGET_ROWS).copy()
    if len(queue) < TARGET_ROWS:
        raise RuntimeError(f"queue too small: {len(queue)}")
    queue["blueprint_id"] = ["a7raw0_" + short_hash(f"{idx}|{expr}", 16) for idx, expr in enumerate(queue["expression"].astype(str))]
    queue["parent_blueprint_id"] = ""
    queue["approval_tier"] = "A7RAW0_LIGHT_GOVERNED_RAW_SPACE"
    queue["approval_score"] = queue["priority_score"]
    queue["parent_score"] = 0.0
    queue["mutation_kind"] = "raw_large_space"
    queue["mutation_detail"] = queue["left_transform"] + "_x_" + queue["right_transform"]
    queue["authorizes_search"] = False
    queue["source_stage"] = "A7RAW0_APPROVED_FIELD_UNIVERSE"
    queue["target_shard"] = [f"a7raw0_s{idx // ROWS_PER_SHARD:03d}" for idx in range(len(queue))]
    ordered = [
        "blueprint_id",
        "parent_blueprint_id",
        "expression",
        "semantic_pair",
        "motif",
        "approval_tier",
        "approval_score",
        "parent_score",
        "mutation_kind",
        "mutation_detail",
        "authorizes_search",
        "skeleton_key",
        "source_stage",
        "target_shard",
        "left_field",
        "right_field",
        "left_semantic",
        "right_semantic",
        "left_transform",
        "right_transform",
    ]
    queue = queue[ordered]
    queue_path = RUNTIME / "a7raw0_light_governed_queue.csv"
    queue.to_csv(queue_path, index=False)
    queue.to_csv(DATA_RUNTIME / queue_path.name, index=False)

    summaries = {
        "a7raw0_semantic_pair_summary.csv": queue.groupby("semantic_pair", dropna=False).size().reset_index(name="queue_rows").sort_values("queue_rows", ascending=False),
        "a7raw0_motif_summary.csv": queue.groupby("motif", dropna=False).size().reset_index(name="queue_rows").sort_values("queue_rows", ascending=False),
        "a7raw0_field_usage_summary.csv": pd.concat(
            [
                queue[["left_field"]].rename(columns={"left_field": "field"}),
                queue[["right_field"]].rename(columns={"right_field": "field"}),
            ],
            ignore_index=True,
        )
        .groupby("field")
        .size()
        .reset_index(name="usage_rows")
        .sort_values("usage_rows", ascending=False),
        "a7raw0_shard_plan.csv": queue.groupby("target_shard", dropna=False).size().reset_index(name="queue_rows"),
    }
    for name, df in summaries.items():
        df.to_csv(RUNTIME / name, index=False)
        df.to_csv(DATA_RUNTIME / name, index=False)

    manifest = {
        "stage": STAGE,
        "generated_at": now_iso(),
        "decision": "PASS_A7RAW0_LIGHT_GOVERNED_QUEUE_BUILT_NO_SEARCH_AUTH",
        "queue_rows": int(len(queue)),
        "candidate_rows_before_governance": int(candidate_rows_before_governance),
        "sampling_attempts": int(attempts),
        "field_count": int(fields["field"].nunique()),
        "semantic_count": int(fields["semantic"].nunique()),
        "rows_per_shard": ROWS_PER_SHARD,
        "shard_count": int(math.ceil(len(queue) / ROWS_PER_SHARD)),
        "queue_path": str(queue_path),
        "data_queue_path": str(DATA_RUNTIME / queue_path.name),
        "governance": {
            "semantic_cap": semantic_cap,
            "skeleton_cap": skeleton_cap,
            "field_cap": field_cap,
            "field_gate_required": True,
            "authorizes_search": False,
        },
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    write_json(RUNTIME / "a7raw0_light_governed_manifest.json", manifest)
    write_json(DATA_RUNTIME / "a7raw0_light_governed_manifest.json", manifest)

    report = f"""# CRYPTO A7RAW0 Light Governed Large-Space Queue {DATE}

## Decision

`{manifest['decision']}`

A7RAW0 is a lightly governed large-space raw-search queue. It does not hand-code narrow axes; it samples broad pairwise formula grammar from the approved field universe and applies only hard governance caps before field gate.

## Counts

- queue_rows: {manifest['queue_rows']}
- candidate_rows_before_governance: {manifest['candidate_rows_before_governance']}
- field_count: {manifest['field_count']}
- semantic_count: {manifest['semantic_count']}
- shard_count: {manifest['shard_count']}
- rows_per_shard: {manifest['rows_per_shard']}

## Semantic Pair Summary

{md_table(summaries['a7raw0_semantic_pair_summary.csv'], 80)}

## Motif Summary

{md_table(summaries['a7raw0_motif_summary.csv'], 80)}

## Field Usage Summary

{md_table(summaries['a7raw0_field_usage_summary.csv'], 80)}

## Boundary

```text
This queue is numeric-probe only after field gate PASS.
It does not authorize formula search, alpha proof, shadow, paper, or live.
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
