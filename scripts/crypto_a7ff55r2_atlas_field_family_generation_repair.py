from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55r2_atlas_field_family_generation_repair"
REPORT = REPO / "reports" / "CRYPTO_A7FF55R2_ATLAS_FIELD_FAMILY_GENERATION_REPAIR_20260531.md"
A7FF55R1 = REPO / "runtime" / "a7ff55r1_supplemental_queue_feasibility" / "a7ff55r1_manifest.json"
SEED_POLICY = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_seed_policy.csv"
PAIR_POLICY = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_pair_policy.csv"


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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def repaired_semantic(field_name: str, old_semantic: str) -> tuple[str, str]:
    name = field_name.lower()
    if "open_interest" in name:
        return "open_interest_like", "split_open_interest_from_positioning"
    if "taker_buy_sell" in name or name in {"taker_buy_volume", "taker_buy_quote_volume"}:
        return "taker_flow_like", "split_taker_flow_from_positioning_or_liquidity"
    if "long_short" in name:
        return "positioning_like", "keep_positioning_ratio"
    if any(token in name for token in ["liquidity", "quote_volume", "trade_volume", "trade_count", "volume_volatility"]):
        return "liquidity_like", "keep_liquidity_activity"
    return old_semantic, "unchanged"


def repaired_route(field_name: str, repaired_semantic_type: str, old_route: str) -> tuple[str, str]:
    if repaired_semantic_type in {"open_interest_like", "taker_flow_like"}:
        return "exploratory_signal_seed", "promote_from_modifier_to_exploratory_signal_seed"
    if repaired_semantic_type == "liquidity_like" and old_route == "modifier_only_seed":
        return "exploratory_signal_seed", "promote_liquidity_from_modifier_to_exploratory_signal_seed"
    return old_route, "route_unchanged"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    m55r1 = read_json(A7FF55R1)
    if m55r1.get("decision") != "HOLD_A7FF55R1_SUPPLEMENTAL_QUEUE_ATLAS_COVERAGE_FAIL":
        raise SystemExit(f"A7FF-55R1 is not in atlas repair state: {m55r1.get('decision')}")

    seeds = pd.read_csv(SEED_POLICY)
    pairs = pd.read_csv(PAIR_POLICY)
    repair_rows = []
    repaired = seeds.copy()
    repaired["old_semantic_type_v3"] = repaired["semantic_type_v3"]
    repaired["old_seed_route"] = repaired["a7ff23r_seed_route"]
    for idx, row in repaired.iterrows():
        new_sem, semantic_reason = repaired_semantic(str(row["field_name"]), str(row["semantic_type_v3"]))
        new_route, route_reason = repaired_route(str(row["field_name"]), new_sem, str(row["a7ff23r_seed_route"]))
        repaired.at[idx, "semantic_type_v3"] = new_sem
        repaired.at[idx, "a7ff23r_seed_route"] = new_route
        repaired.at[idx, "standalone_alpha_allowed"] = new_route == "primary_signal_seed"
        repaired.at[idx, "interaction_allowed"] = new_route in {"primary_signal_seed", "exploratory_signal_seed", "modifier_only_seed"}
        if new_sem != row["semantic_type_v3"] or new_route != row["a7ff23r_seed_route"]:
            repair_rows.append(
                {
                    "field_name": row["field_name"],
                    "old_semantic_type_v3": row["semantic_type_v3"],
                    "new_semantic_type_v3": new_sem,
                    "old_seed_route": row["a7ff23r_seed_route"],
                    "new_seed_route": new_route,
                    "semantic_repair_reason": semantic_reason,
                    "route_repair_reason": route_reason,
                }
            )
    repair_map = pd.DataFrame(repair_rows)

    manual_pairs = pd.DataFrame(
        [
            {
                "semantic_pair": "open_interest_like|positioning_like",
                "left_semantic_type_v3": "open_interest_like",
                "right_semantic_type_v3": "positioning_like",
                "a7ff55r2_pair_route": "generation_priority",
                "motif_priority": "delta_x_divergence|signed_spread|smooth_mul",
                "reason": "recover OI-positioning interaction absent from current atlas",
            },
            {
                "semantic_pair": "taker_flow_like|open_interest_like",
                "left_semantic_type_v3": "taker_flow_like",
                "right_semantic_type_v3": "open_interest_like",
                "a7ff55r2_pair_route": "generation_priority",
                "motif_priority": "flow_x_leverage|relative_shock|gated_sign",
                "reason": "recover taker-flow leverage state absent from current atlas",
            },
            {
                "semantic_pair": "liquidity_like|volatility_like",
                "left_semantic_type_v3": "liquidity_like",
                "right_semantic_type_v3": "volatility_like",
                "a7ff55r2_pair_route": "generation_priority",
                "motif_priority": "liquidity_shock|vol_compression|smooth_mul",
                "reason": "make existing liquidity formulas materialization-eligible",
            },
            {
                "semantic_pair": "open_interest_like|price_like",
                "left_semantic_type_v3": "open_interest_like",
                "right_semantic_type_v3": "price_like",
                "a7ff55r2_pair_route": "probe_priority",
                "motif_priority": "oi_delta_x_price_move|mean_reversion_gate",
                "reason": "diagnostic OI-price interaction without direct OI-price standalone rerun",
            },
            {
                "semantic_pair": "taker_flow_like|basis_premium_like",
                "left_semantic_type_v3": "taker_flow_like",
                "right_semantic_type_v3": "basis_premium_like",
                "a7ff55r2_pair_route": "probe_priority",
                "motif_priority": "flow_x_basis_dislocation|relative_shock",
                "reason": "test aggressive-flow response under basis/premium dislocation",
            },
        ]
    )
    seed_summary = (
        repaired.groupby(["semantic_type_v3", "a7ff23r_seed_route"], dropna=False)
        .size()
        .reset_index(name="field_count")
        .sort_values(["semantic_type_v3", "a7ff23r_seed_route"])
    )
    old_seed_summary = (
        seeds.groupby(["semantic_type_v3", "a7ff23r_seed_route"], dropna=False)
        .size()
        .reset_index(name="field_count")
        .sort_values(["semantic_type_v3", "a7ff23r_seed_route"])
    )
    pair_source_summary = (
        pairs.groupby(["semantic_pair", "a7ff23r_pair_route"], dropna=False)
        .size()
        .reset_index(name="pair_rows")
        .sort_values("pair_rows", ascending=False)
    )

    repair_map.to_csv(RUNTIME / "a7ff55r2_semantic_route_repair_map.csv", index=False)
    repaired.to_csv(RUNTIME / "a7ff55r2_repaired_seed_policy_preview.csv", index=False)
    manual_pairs.to_csv(RUNTIME / "a7ff55r2_required_pair_policy_patch.csv", index=False)
    seed_summary.to_csv(RUNTIME / "a7ff55r2_repaired_seed_summary.csv", index=False)
    old_seed_summary.to_csv(RUNTIME / "a7ff55r2_old_seed_summary.csv", index=False)
    pair_source_summary.to_csv(RUNTIME / "a7ff55r2_existing_pair_source_summary.csv", index=False)

    manifest = {
        "stage": "A7FF-55R2",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF55R2_ATLAS_FIELD_FAMILY_GENERATION_REPAIR_READY_NO_GENERATION_EXEC",
        "source_stage": "A7FF-55R1",
        "source_decision": m55r1.get("decision"),
        "field_repairs": int(len(repair_map)),
        "required_pair_patch_rows": int(len(manual_pairs)),
        "repaired_open_interest_seed_count": int((repaired["semantic_type_v3"] == "open_interest_like").sum()),
        "repaired_taker_flow_seed_count": int((repaired["semantic_type_v3"] == "taker_flow_like").sum()),
        "repaired_liquidity_seed_count": int((repaired["semantic_type_v3"] == "liquidity_like").sum()),
        "next_allowed": "A7FF-55R3 repaired atlas dry generation using repaired seed/pair preview",
        "executes_generation": False,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff55r2_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-55R2 ATLAS FIELD-FAMILY GENERATION REPAIR

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55R2 repairs the generation atlas contract after A7FF-55R1 showed missing open-interest and taker-flow families. It does not execute dry generation, numeric evaluation, replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Semantic / Route Repair Map

{md_table(repair_map, 80)}

## Old Seed Summary

{md_table(old_seed_summary, 80)}

## Repaired Seed Summary

{md_table(seed_summary, 80)}

## Required Pair Policy Patch

{md_table(manual_pairs, 40)}

## Existing Pair Source Summary

{md_table(pair_source_summary, 80)}

## Boundary

```text
generation executed: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
