from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from itertools import cycle, product
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore25e_targeted_lane_horizon_generation"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE25E_TARGETED_LANE_HORIZON_GENERATION_20260601.md"
CORE25 = REPO / "runtime" / "a7ffcore25_targeted_lane_horizon_generation_contract" / "a7ffcore25_manifest.json"
FIELD_MATRIX = REPO / "runtime" / "a7aif3_materialization_evaluator_parity" / "a7aif3_field_materialization_matrix.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def short_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:14]


def expr_for(op: str, left_expr: str, right_expr: str) -> str:
    if op == "SafeDiv":
        return f"SafeDiv({left_expr},Abs({right_expr}))"
    if op in {"Sub", "Add", "Mul"}:
        return f"{op}({left_expr},{right_expr})"
    raise ValueError(op)


def transform_expr(field: str, transform: str) -> str:
    if transform.startswith("delta_"):
        h = transform.split("_", 1)[1].replace("h", "")
        return f"Delta({field},{h})"
    if transform.startswith("mean_"):
        h = transform.split("_", 1)[1].replace("h", "")
        return f"Mean({field},{h})"
    if transform.startswith("zscore_"):
        return f"ZScore({field})"
    if transform.startswith("tsrank_"):
        h = transform.split("_", 1)[1].replace("h", "")
        return f"TSRank({field},{h})"
    if transform.startswith("decay_"):
        h = transform.split("_", 1)[1].replace("h", "")
        return f"Decay({field},{h})"
    if transform == "spread_short_long":
        return f"Sub(Mean({field},24),Mean({field},168))"
    if transform.startswith("rank"):
        return f"Rank({field})"
    if transform.startswith("abs_zscore"):
        return f"Abs(ZScore({field}))"
    return field


def lane_specs() -> dict[str, dict[str, Any]]:
    return {
        "S0_positioning_price_basis": {
            "quota": 1800,
            "preflight_quota": 360,
            "left_fields": ["top_long_short_position_ratio_last", "top_long_short_account_ratio_last", "global_long_short_account_ratio_last"],
            "right_fields": ["mark_index_basis_bps", "mark_trade_basis_bps", "premium_close_bps", "trade_return_24h", "index_close", "mark_close"],
            "left_transforms": ["delta_4h", "delta_24h", "mean_24h", "zscore_168h", "tsrank_168h", "decay_24h"],
            "right_transforms": ["delta_4h", "delta_24h", "zscore_168h", "tsrank_168h", "decay_24h", "abs_zscore_168h"],
            "operators": ["Sub", "Mul", "SafeDiv", "Add"],
            "horizons": [4, 8, 24],
            "labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"],
        },
        "S1_liquidity_basis_positioning": {
            "quota": 1800,
            "preflight_quota": 360,
            "left_fields": ["median_quote_volume_168h", "trade_volume", "realized_vol_24h", "realized_vol_168h", "liquidity_rank_active_universe"],
            "right_fields": ["mark_trade_basis_bps", "mark_index_basis_bps", "premium_close_bps", "top_long_short_position_ratio_last", "top_long_short_account_ratio_last"],
            "left_transforms": ["delta_24h", "mean_24h", "zscore_168h", "tsrank_168h", "decay_24h", "abs_zscore_168h"],
            "right_transforms": ["delta_4h", "delta_24h", "zscore_168h", "tsrank_168h", "decay_24h", "abs_zscore_168h"],
            "operators": ["Mul", "Sub", "SafeDiv", "Add"],
            "horizons": [4, 8, 24],
            "labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"],
        },
        "S2_taker_flow_liquidity_oi": {
            "quota": 600,
            "preflight_quota": 120,
            "left_fields": ["taker_buy_sell_volume_ratio_last", "kline_taker_buy_quote_share", "taker_buy_quote_volume"],
            "right_fields": ["open_interest_last", "open_interest_value_last", "open_interest_change_24h", "median_quote_volume_168h"],
            "left_transforms": ["delta_4h", "delta_24h", "zscore_168h", "tsrank_168h", "decay_24h"],
            "right_transforms": ["delta_24h", "zscore_168h", "tsrank_168h", "decay_24h", "abs_zscore_168h"],
            "operators": ["SafeDiv", "Mul", "Sub"],
            "horizons": [24],
            "labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"],
        },
        "S3_cross_family_bridge": {
            "quota": 600,
            "preflight_quota": 120,
            "left_fields": ["top_long_short_position_ratio_last", "liquidity_rank_active_universe", "median_quote_volume_168h"],
            "right_fields": ["open_interest_value_last", "basis_abs_168h", "mark_trade_basis_bps", "mark_index_basis_bps"],
            "left_transforms": ["delta_24h", "spread_short_long", "zscore_168h", "tsrank_168h", "decay_24h"],
            "right_transforms": ["delta_24h", "zscore_168h", "tsrank_168h", "decay_24h", "abs_zscore_168h"],
            "operators": ["SafeDiv", "Mul", "Sub"],
            "horizons": [8, 24],
            "labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"],
        },
    }


def generate_for_lane(lane: str, spec: dict[str, Any], allowed_fields: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    combos = product(
        spec["left_fields"],
        spec["left_transforms"],
        spec["operators"],
        spec["right_fields"],
        spec["right_transforms"],
        spec["horizons"],
        spec["labels"],
    )
    for left, lt, op, right, rt, horizon, label in combos:
        if left not in allowed_fields or right not in allowed_fields:
            continue
        left_expr = transform_expr(left, lt)
        right_expr = transform_expr(right, rt)
        expr = expr_for(op, left_expr, right_expr)
        blueprint_id = f"core25e_{lane}_{short_hash(expr + '|' + label + '|' + str(horizon))}"
        rows.append(
            {
                "blueprint_id": blueprint_id,
                "seed_lane": lane,
                "left_field": left,
                "left_transform": lt,
                "operator": op,
                "right_field": right,
                "right_transform": rt,
                "label_family": label,
                "label_horizon_h": int(horizon),
                "expression": expr,
                "candidate_role": "targeted_lane_horizon_repair_blueprint",
                "source_stage": "A7FF-CORE25E",
            }
        )
        if len(rows) >= int(spec["quota"]):
            break
    return rows


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core25 = read_json(CORE25)
    if core25.get("decision") != "PASS_A7FFCORE25_TARGETED_LANE_HORIZON_GENERATION_CONTRACT_READY_FOR_CORE25E":
        raise SystemExit(f"CORE25 is not ready: {core25.get('decision')}")
    fields = pd.read_csv(FIELD_MATRIX)
    allowed_fields = set(fields.loc[fields["resolution"].eq("resolved"), "field_name"].astype(str))
    # CORE16/CORE24 packets already reference these derived fields; keep them explicit if absent from older F3 ledger.
    allowed_fields.update({"median_quote_volume_168h", "liquidity_rank_active_universe", "basis_abs_168h"})

    generated_parts: list[pd.DataFrame] = []
    specs = lane_specs()
    for lane, spec in specs.items():
        generated_parts.append(pd.DataFrame(generate_for_lane(lane, spec, allowed_fields)))
    generated = pd.concat(generated_parts, ignore_index=True).drop_duplicates("blueprint_id")

    preflight_parts = []
    for lane, spec in specs.items():
        lane_rows = generated[generated["seed_lane"].eq(lane)].copy()
        preflight_parts.append(lane_rows.head(int(spec["preflight_quota"])))
    preflight = pd.concat(preflight_parts, ignore_index=True).drop_duplicates("blueprint_id")

    lane_distribution = (
        generated.groupby("seed_lane", dropna=False)
        .agg(generated_count=("blueprint_id", "nunique"), label_family_count=("label_family", "nunique"), horizon_count=("label_horizon_h", "nunique"))
        .reset_index()
    )
    preflight_distribution = (
        preflight.groupby("seed_lane", dropna=False)
        .agg(preflight_count=("blueprint_id", "nunique"), label_family_count=("label_family", "nunique"), horizon_count=("label_horizon_h", "nunique"))
        .reset_index()
    )
    field_usage = (
        pd.concat(
            [
                generated[["left_field"]].rename(columns={"left_field": "field"}),
                generated[["right_field"]].rename(columns={"right_field": "field"}),
            ],
            ignore_index=True,
        )
        .groupby("field", dropna=False)
        .size()
        .reset_index(name="usage_count")
        .sort_values("usage_count", ascending=False)
    )

    blockers: list[str] = []
    if int(generated["blueprint_id"].nunique()) < 4800:
        blockers.append("generated_blueprints_lt_4800")
    if int(preflight["blueprint_id"].nunique()) < 960:
        blockers.append("preflight_packet_lt_960")
    for lane in ["S0_positioning_price_basis", "S1_liquidity_basis_positioning"]:
        if int(preflight[preflight["seed_lane"].eq(lane)]["blueprint_id"].nunique()) < 160:
            blockers.append(f"{lane}_preflight_lt_160")
    if preflight["seed_lane"].nunique() < 4:
        blockers.append("preflight_lane_count_lt_4")
    if preflight["label_horizon_h"].nunique() < 3:
        blockers.append("preflight_horizon_count_lt_3")

    decision = "PASS_A7FFCORE25E_TARGETED_GENERATION_PREFLIGHT_PACKET_READY_FOR_CORE26_CONTRACT" if not blockers else "HOLD_A7FFCORE25E_TARGETED_GENERATION_PREFLIGHT_INSUFFICIENT"

    generated.to_csv(RUNTIME / "a7ffcore25e_generated_blueprints.csv", index=False)
    preflight.to_csv(RUNTIME / "a7ffcore25e_preflight_packet.csv", index=False)
    lane_distribution.to_csv(RUNTIME / "a7ffcore25e_lane_distribution.csv", index=False)
    preflight_distribution.to_csv(RUNTIME / "a7ffcore25e_preflight_distribution.csv", index=False)
    field_usage.to_csv(RUNTIME / "a7ffcore25e_field_usage.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE25E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE25",
        "source_decision": core25.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "generated_blueprint_count": int(generated["blueprint_id"].nunique()),
        "preflight_packet_count": int(preflight["blueprint_id"].nunique()),
        "preflight_lane_count": int(preflight["seed_lane"].nunique()),
        "preflight_horizon_count": int(preflight["label_horizon_h"].nunique()),
        "preflight_label_family_count": int(preflight["label_family"].nunique()),
        "authorizes_core26_contract": decision.startswith("PASS_"),
        "authorizes_formula_generation": False,
        "authorizes_open_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE26 targeted numeric probe contract" if decision.startswith("PASS_") else "A7FF-CORE25R targeted generation forensic",
    }
    write_json(RUNTIME / "a7ffcore25e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE25E TARGETED LANE/HORIZON GENERATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE25E generates a bounded targeted blueprint/preflight packet for missing executable lanes. It does not execute numeric replay, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Lane Distribution",
        "",
        md_table(lane_distribution),
        "",
        "## Preflight Distribution",
        "",
        md_table(preflight_distribution),
        "",
        "## Top Field Usage",
        "",
        md_table(field_usage.head(30)),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
