from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import cycle
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from crypto_a7ls1_multi_arm_blueprint_generation import (  # noqa: E402
    field_catalog as base_field_catalog,
    motif_expr,
    skeleton,
)


RUNTIME = REPO / "runtime" / "a7ls15_million_scale_blueprint_generation"
REPORT = REPO / "reports" / "CRYPTO_A7LS15_MILLION_SCALE_BLUEPRINT_GENERATION_20260606.md"
A7LS14 = REPO / "runtime" / "a7ls14_scaled_multi_axis_search_contract"
A7LS14X = REPO / "runtime" / "a7ls14x_authorization_arbitration" / "a7ls14x_manifest.json"
EXTERNAL = Path(
    os.environ.get(
        "A7LS15_EXTERNAL",
        "G:/AlphaFactory_CryptoData/research_runtime/a7ls15_million_scale_blueprint_generation_20260606",
    )
)


ARM_ALIAS = {
    "A7LS14_A": "A7LS_A",
    "A7LS14_B": "A7LS_B",
    "A7LS14_C": "A7LS_C",
    "A7LS14_D": "A7LS_D",
}

FIELDNAMES = [
    "blueprint_id",
    "expression",
    "a7ls_lane",
    "lane_name",
    "search_role",
    "level",
    "candidate_role",
    "generation_priority",
    "semantic_pair",
    "motif",
    "primary_field",
    "secondary_field",
    "primary_semantic",
    "secondary_semantic",
    "primary_transform",
    "secondary_transform",
    "skeleton_key",
    "production_key",
    "source_stage",
    "source_seed_id",
    "checkpoint_group",
]


def now_iso() -> str:
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
    return view.to_markdown(index=False)


def field_catalog() -> dict[str, list[str]]:
    catalog = base_field_catalog()
    additions = {
        "basis_premium_like": ["basis_abs_168h", "premium_abs_168h", "basis_abs_state", "premium_abs_state"],
        "funding_state_like": ["funding_rate_abs_168h", "funding_rate_persistence_24h"],
        "open_interest_like": ["oi_x_price_move_24h", "open_interest_value_change_24h"],
        "positioning_like": ["account_position_divergence", "top_global_account_divergence"],
        "taker_flow_like": ["taker_buy_sell_volume_ratio_last", "taker_buy_sell_volume_ratio_mean"],
        "liquidity_like": ["trade_quote_volume", "quote_volume_z_168h", "liquidity_rank_active_universe"],
        "volatility_like": ["realized_vol_24h", "realized_vol_72h", "realized_vol_168h"],
        "listing_age_like": ["age_x_liquidity", "age_x_volatility", "listing_age_days"],
        "regime_state": [
            "market_breadth_state",
            "leverage_crowding_state",
            "basis_dislocation_state",
            "liquidity_cycle_state",
            "stress_proxy_state",
        ],
    }
    for axis, fields in additions.items():
        current = catalog.setdefault(axis, [])
        for field in fields:
            if field not in current:
                current.append(field)
    return catalog


def transforms(field: str, axis: str, raw_lane: bool) -> list[tuple[str, str]]:
    windows = [1, 2, 3, 4, 6, 8, 12, 16, 24, 36, 48, 72, 96, 120, 168, 240, 336, 504, 720]
    if axis in {"regime_state", "listing_age_like"}:
        windows = [4, 8, 24, 72, 168, 336]
    if raw_lane:
        windows = windows[:16]
    out: list[tuple[str, str]] = [("level", field), ("csrank", f"CSRank({field})"), ("clip_z", f"Clip(ZScore({field}),-3,3)")]
    for w in windows:
        out.extend(
            [
                (f"delta_{w}h", f"Delta({field},{w})"),
                (f"mean_{w}h", f"Mean({field},{w})"),
                (f"zmean_{w}h", f"ZScore(Mean({field},{w}))"),
                (f"abs_zmean_{w}h", f"Abs(ZScore(Mean({field},{w})))"),
                (f"decay_{w}h", f"Decay({field},{w})"),
                (f"tsrank_{w}h", f"TSRank({field},{w})"),
            ]
        )
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for name, expr in out:
        if expr in seen:
            continue
        seen.add(expr)
        result.append((name, expr))
    return result


def axis_pairs(lane_id: str) -> list[tuple[str, str]]:
    if lane_id == "A7LS14_A":
        return [
            ("basis_premium_like", "volatility_like"),
            ("basis_premium_like", "liquidity_like"),
            ("basis_premium_like", "price_like"),
            ("basis_premium_like", "listing_age_like"),
            ("basis_premium_like", "positioning_like"),
            ("basis_premium_like", "basis_premium_like"),
        ]
    if lane_id == "A7LS14_B":
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
        return [(left, right) for i, left in enumerate(axes) for right in axes[i:]]
    if lane_id == "A7LS14_C":
        return [
            ("open_interest_like", "positioning_like"),
            ("open_interest_like", "taker_flow_like"),
            ("open_interest_like", "funding_state_like"),
            ("open_interest_like", "regime_state"),
            ("positioning_like", "taker_flow_like"),
            ("positioning_like", "basis_premium_like"),
            ("listing_age_like", "basis_premium_like"),
            ("listing_age_like", "liquidity_like"),
            ("funding_state_like", "basis_premium_like"),
        ]
    return [
        ("placebo", "price_like"),
        ("placebo", "basis_premium_like"),
        ("low_prior_axes", "price_like"),
        ("low_prior_axes", "basis_premium_like"),
        ("volatility_like", "liquidity_like"),
        ("regime_state", "price_like"),
    ]


def motifs(lane_id: str, left_axis: str, right_axis: str) -> list[str]:
    if lane_id == "A7LS14_D":
        return ["control_flip", "sub", "safe_div_abs", "spread_rank", "mul"]
    base = ["mul", "sub", "spread_rank", "gated_sign", "safe_div_abs", "smooth_mul", "relative_shock", "signed_spread"]
    if lane_id in {"A7LS14_A", "A7LS14_C"}:
        base.extend(["mean_reversion_gate", "delta_x_divergence", "state_gate"])
    if "regime_state" in {left_axis, right_axis} or "listing_age_like" in {left_axis, right_axis}:
        return ["mul", "gated_sign", "smooth_mul", "state_gate", "signed_spread", "relative_shock"]
    return base


def row_for(
    *,
    lane: pd.Series,
    level: str,
    semantic_pair: str,
    motif: str,
    primary_field: str,
    secondary_field: str,
    primary_semantic: str,
    secondary_semantic: str,
    primary_transform: str,
    secondary_transform: str,
    expression: str,
    source_seed_id: str = "",
) -> dict[str, str]:
    lane_id = str(lane["lane_id"])
    skel = skeleton(expression)
    prod = stable_id(
        "prod",
        f"{lane_id}|{semantic_pair}|{motif}|{primary_field}|{secondary_field}|{primary_transform}|{secondary_transform}",
    )
    bid = stable_id("a7ls15", f"{lane_id}|{level}|{expression}|{source_seed_id}")
    return {
        "blueprint_id": bid,
        "expression": expression,
        "a7ls_lane": lane_id,
        "lane_name": str(lane["lane_name"]),
        "search_role": str(lane["search_role"]),
        "level": level,
        "candidate_role": "control_only" if lane_id == "A7LS14_D" else "role_mixed_allowed",
        "generation_priority": "P0" if lane_id in {"A7LS14_A", "A7LS14_B"} else "P1",
        "semantic_pair": semantic_pair,
        "motif": motif,
        "primary_field": primary_field,
        "secondary_field": secondary_field,
        "primary_semantic": primary_semantic,
        "secondary_semantic": secondary_semantic,
        "primary_transform": primary_transform,
        "secondary_transform": secondary_transform,
        "skeleton_key": skel,
        "production_key": prod,
        "source_stage": "A7LS-13" if source_seed_id else "A7LS-14",
        "source_seed_id": source_seed_id,
        "checkpoint_group": stable_id("chk", f"{lane_id}|{semantic_pair}|{motif}|{skel}")[:24],
    }


def single_axis_rows(lane: pd.Series, catalog: dict[str, list[str]]) -> Iterable[dict[str, str]]:
    lane_id = str(lane["lane_id"])
    raw_lane = lane_id == "A7LS14_B"
    for axis in sorted({axis for pair in axis_pairs(lane_id) for axis in pair}):
        for field in catalog.get(axis, []):
            for t_name, expr in transforms(field, axis, raw_lane)[:72]:
                yield row_for(
                    lane=lane,
                    level="L1_single_axis_transform",
                    semantic_pair=axis,
                    motif="single",
                    primary_field=field,
                    secondary_field="",
                    primary_semantic=axis,
                    secondary_semantic="",
                    primary_transform=t_name,
                    secondary_transform="",
                    expression=expr,
                )


def interaction_rows(lane: pd.Series, catalog: dict[str, list[str]]) -> Iterable[dict[str, str]]:
    lane_id = str(lane["lane_id"])
    raw_lane = lane_id == "A7LS14_B"
    transform_cache = {
        (axis, field): transforms(field, axis, raw_lane)
        for axis, fields in catalog.items()
        for field in fields
    }
    pairs = axis_pairs(lane_id)
    pair_cycle = cycle(pairs)
    pair_positions: dict[tuple[str, str], int] = defaultdict(int)
    while True:
        left_axis, right_axis = next(pair_cycle)
        left_fields = catalog.get(left_axis, [])
        right_fields = catalog.get(right_axis, [])
        if not left_fields or not right_fields:
            continue
        pos = pair_positions[(left_axis, right_axis)]
        pair_positions[(left_axis, right_axis)] += 1
        left_field = left_fields[pos % len(left_fields)]
        right_field = right_fields[(pos // max(1, len(left_fields))) % len(right_fields)]
        if left_field == right_field and len(right_fields) > 1:
            right_field = right_fields[(right_fields.index(right_field) + 1) % len(right_fields)]
        left_ts = transform_cache[(left_axis, left_field)]
        right_ts = transform_cache[(right_axis, right_field)]
        left_name, left_expr = left_ts[(pos // 3) % len(left_ts)]
        right_name, right_expr = right_ts[(pos // 7) % len(right_ts)]
        motif_list = motifs(lane_id, left_axis, right_axis)
        motif = motif_list[pos % len(motif_list)]
        expr = motif_expr(left_expr, right_expr, motif)
        semantic_pair = f"{left_axis}|{right_axis}" if left_axis != right_axis else left_axis
        yield row_for(
            lane=lane,
            level="L2_raw_multi_axis_interaction" if lane_id == "A7LS14_B" else "L2_typed_interaction",
            semantic_pair=semantic_pair,
            motif=motif,
            primary_field=left_field,
            secondary_field=right_field,
            primary_semantic=left_axis,
            secondary_semantic=right_axis,
            primary_transform=left_name,
            secondary_transform=right_name,
            expression=expr,
        )


def seed_mutation_rows(lane: pd.Series, seed_packet: pd.DataFrame, catalog: dict[str, list[str]]) -> Iterable[dict[str, str]]:
    if seed_packet.empty:
        return
    context_axes = ["basis_premium_like", "volatility_like", "liquidity_like", "positioning_like", "listing_age_like", "regime_state"]
    rows = seed_packet.to_dict("records")
    idx = 0
    while True:
        seed = rows[idx % len(rows)]
        axis = context_axes[(idx // len(rows)) % len(context_axes)]
        fields = catalog.get(axis, [])
        if not fields:
            idx += 1
            continue
        field = fields[(idx // (len(rows) * len(context_axes))) % len(fields)]
        t_name, t_expr = transforms(field, axis, False)[idx % min(48, len(transforms(field, axis, False)))]
        motif = ["mul", "sub", "gated_sign", "smooth_mul", "relative_shock", "signed_spread"][idx % 6]
        expr = motif_expr(str(seed["expression"]), t_expr, motif)
        yield row_for(
            lane=lane,
            level="L3_seed_context_mutation",
            semantic_pair=f"{seed.get('semantic_pair','seed')}|{axis}",
            motif=f"seed_{motif}",
            primary_field=str(seed.get("blueprint_id", "")),
            secondary_field=field,
            primary_semantic="a7ls13_seed",
            secondary_semantic=axis,
            primary_transform="seed_expression",
            secondary_transform=t_name,
            expression=expr,
            source_seed_id=str(seed.get("blueprint_id", "")),
        )
        idx += 1


def write_lane(
    lane: pd.Series,
    catalog: dict[str, list[str]],
    seed_packet: pd.DataFrame,
    writer: csv.DictWriter,
    sample_writer: csv.DictWriter,
    materialization_writer: csv.DictWriter,
    global_seen: set[str],
    summary: list[dict[str, Any]],
    materialization_target: int,
    sample_limit: int,
    sample_count: list[int],
) -> int:
    lane_id = str(lane["lane_id"])
    target = int(lane["generated_budget"])
    generated = 0
    materialized = 0
    counters: dict[str, Counter[str]] = {
        "semantic_pair": Counter(),
        "motif": Counter(),
        "primary_semantic": Counter(),
        "skeleton_key": Counter(),
    }
    streams: list[Iterable[dict[str, str]]] = [single_axis_rows(lane, catalog), interaction_rows(lane, catalog)]
    if lane_id == "A7LS14_A":
        streams.insert(0, seed_mutation_rows(lane, seed_packet, catalog))
    active_streams = [iter(stream) for stream in streams if stream is not None]
    stream_idx = 0
    while generated < target:
        if not active_streams:
            raise RuntimeError(f"{lane_id} exhausted all generation streams at {generated}/{target}")
        idx = stream_idx % len(active_streams)
        stream_idx += 1
        try:
            row = next(active_streams[idx])
        except StopIteration:
            active_streams.pop(idx)
            continue
        expr = row["expression"]
        if expr in global_seen:
            continue
        global_seen.add(expr)
        generated += 1
        writer.writerow(row)
        if sample_count[0] < sample_limit:
            sample_writer.writerow(row)
            sample_count[0] += 1
        if materialized < materialization_target:
            materialization_writer.writerow(row)
            materialized += 1
        for key, counter in counters.items():
            counter[row[key]] += 1
        if generated % 50000 == 0:
            print(f"[A7LS15] {lane_id} generated={generated:,}/{target:,}", flush=True)
    summary.append(
        {
            "lane_id": lane_id,
            "lane_name": lane["lane_name"],
            "generated_rows": generated,
            "materialization_rows": materialized,
            "semantic_pair_count": len(counters["semantic_pair"]),
            "motif_count": len(counters["motif"]),
            "primary_axis_count": len(counters["primary_semantic"]),
            "skeleton_count": len(counters["skeleton_key"]),
            "top_semantic_pair": counters["semantic_pair"].most_common(1)[0][0],
            "top_semantic_pair_share": counters["semantic_pair"].most_common(1)[0][1] / generated,
            "top_motif": counters["motif"].most_common(1)[0][0],
            "top_motif_share": counters["motif"].most_common(1)[0][1] / generated,
        }
    )
    return generated


def build() -> dict[str, Any]:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    EXTERNAL.mkdir(parents=True, exist_ok=True)

    auth = read_json(A7LS14X)
    if auth.get("decision") != "PASS_A7LS14X_CHECKPOINT_LARGE_SEARCH_AUTHORIZATION_ARBITRATED":
        raise SystemExit(f"A7LS14X does not authorize A7LS15: {auth.get('decision')}")

    lanes = pd.read_csv(A7LS14 / "a7ls14_lane_budget_map.csv")
    seed_packet = pd.read_csv(REPO / "runtime" / "a7ls13_consolidation_replay_packet" / "a7ls13_replay_packet.csv")
    catalog = field_catalog()

    full_path = EXTERNAL / "a7ls15_full_blueprint_index.csv"
    materialization_path = EXTERNAL / "a7ls15_materialization_queue_100k.csv"
    sample_path = RUNTIME / "a7ls15_blueprint_index_sample.csv"
    summary_rows: list[dict[str, Any]] = []
    sample_count = [0]
    global_seen: set[str] = set()
    total_generated = 0

    with full_path.open("w", newline="", encoding="utf-8") as f_full, sample_path.open("w", newline="", encoding="utf-8") as f_sample, materialization_path.open("w", newline="", encoding="utf-8") as f_mat:
        writer = csv.DictWriter(f_full, fieldnames=FIELDNAMES)
        sample_writer = csv.DictWriter(f_sample, fieldnames=FIELDNAMES)
        mat_writer = csv.DictWriter(f_mat, fieldnames=FIELDNAMES)
        writer.writeheader()
        sample_writer.writeheader()
        mat_writer.writeheader()
        for _, lane in lanes.iterrows():
            total_generated += write_lane(
                lane,
                catalog,
                seed_packet,
                writer,
                sample_writer,
                mat_writer,
                global_seen,
                summary_rows,
                materialization_target=int(lane["materialization_budget"]),
                sample_limit=5000,
                sample_count=sample_count,
            )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(RUNTIME / "a7ls15_lane_generation_summary.csv", index=False)

    materialization_rows = int(lanes["materialization_budget"].sum())
    shard_rows = []
    rows_per_shard = 1000
    shard_count = (materialization_rows + rows_per_shard - 1) // rows_per_shard
    for shard_idx in range(shard_count):
        start = shard_idx * rows_per_shard
        end = min(materialization_rows, (shard_idx + 1) * rows_per_shard)
        shard_rows.append(
            {
                "shard_id": f"a7ls15_mat_s{shard_idx:03d}",
                "start_row": start,
                "end_row_exclusive": end,
                "rows": end - start,
                "source_path": str(materialization_path).replace("\\", "/"),
                "checkpoint_path": str((EXTERNAL / "checkpoints" / f"a7ls15_mat_s{shard_idx:03d}.json")).replace("\\", "/"),
            }
        )
    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(RUNTIME / "a7ls15_materialization_shard_plan.csv", index=False)

    artifact_manifest = pd.DataFrame(
        [
            {"artifact": "full_blueprint_index", "path": str(full_path).replace("\\", "/"), "rows": total_generated, "location": "external"},
            {"artifact": "materialization_queue", "path": str(materialization_path).replace("\\", "/"), "rows": materialization_rows, "location": "external"},
            {"artifact": "blueprint_sample", "path": str(sample_path).replace("\\", "/"), "rows": sample_count[0], "location": "repo"},
        ]
    )
    artifact_manifest.to_csv(RUNTIME / "a7ls15_artifact_manifest.csv", index=False)

    blockers: list[str] = []
    expected_generated = int(lanes["generated_budget"].sum())
    if total_generated != expected_generated:
        blockers.append("generated_total_mismatch")
    if materialization_rows != int(lanes["materialization_budget"].sum()):
        blockers.append("materialization_total_mismatch")
    if int(summary["primary_axis_count"].min()) < 2:
        blockers.append("lane_axis_breadth_too_low")
    if float(summary["top_semantic_pair_share"].max()) > 0.45:
        blockers.append("lane_top_semantic_pair_share_gt_45pct")
    decision = "PASS_A7LS15_MILLION_SCALE_BLUEPRINT_GENERATION_READY_FOR_A7LS16" if not blockers else "HOLD_A7LS15_BLUEPRINT_DIVERSITY_OR_COUNT_FAIL"

    manifest = {
        "stage": "A7LS-15",
        "generated_at": now_iso(),
        "decision": decision,
        "blockers": blockers,
        "input_stage": "A7LS-14X",
        "generated_total": total_generated,
        "materialization_queue_rows": materialization_rows,
        "materialization_shard_count": shard_count,
        "full_blueprint_index_path": str(full_path).replace("\\", "/"),
        "materialization_queue_path": str(materialization_path).replace("\\", "/"),
        "repo_sample_rows": sample_count[0],
        "lane_count": int(len(summary)),
        "authorizes_a7ls16_preflight": decision.startswith("PASS_"),
        "authorizes_a7ls17_company_materialization": False,
        "authorizes_a7ls18_company_numeric": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
    }
    write_json(RUNTIME / "a7ls15_manifest.json", manifest)

    REPORT.write_text(
        "\n".join(
            [
                "# CRYPTO A7LS-15 MILLION-SCALE BLUEPRINT GENERATION",
                "",
                f"Generated: {manifest['generated_at']}",
                "",
                "## Decision",
                "",
                f"`{decision}`",
                "",
                "## Counts",
                "",
                f"- generated_total: {total_generated:,}",
                f"- materialization_queue_rows: {materialization_rows:,}",
                f"- materialization_shard_count: {shard_count:,}",
                f"- full_blueprint_index_path: `{manifest['full_blueprint_index_path']}`",
                f"- materialization_queue_path: `{manifest['materialization_queue_path']}`",
                "",
                "## Lane Summary",
                "",
                md_table(summary),
                "",
                "## Authorization",
                "",
                "- A7LS16 local preflight: authorized if PASS.",
                "- A7LS17 company materialization: not directly authorized by this stage; requires A7LS16 preflight.",
                "- A7LS18 company numeric wave: not directly authorized by this stage; requires A7LS17 materialization.",
                "- Alpha proof / shadow / paper / live: not authorized.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
