from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff22_label_balanced_expansion_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF22_LABEL_BALANCED_EXPANSION_CONTRACT_20260530.md"

A7FF21_MANIFEST = REPO / "runtime" / "a7ff21_external_confirmation_selector" / "a7ff21_manifest.json"
A7FF21_QUEUE = REPO / "runtime" / "a7ff21_external_confirmation_selector" / "a7ff21_external_confirmation_selected_queue.csv"


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
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ff21 = read_json(A7FF21_MANIFEST)
    if not a7ff21.get("authorizes_a7ff22_expansion_contract"):
        raise SystemExit("A7FF-21 does not authorize A7FF-22 expansion contract")
    queue = pd.read_csv(A7FF21_QUEUE)
    if queue.empty:
        raise SystemExit("empty A7FF-21 selected queue")

    label_policy = (
        queue.groupby("label_family", dropna=False)
        .agg(
            seed_rows=("blueprint_id", "count"),
            unique_blueprints=("blueprint_id", "nunique"),
            strict_cost10_rows=("cost_tier", lambda s: int((s == "strict_cost10").sum())),
            cost5_or_better_rows=("cost_tier", lambda s: int(s.isin(["strict_cost10", "cost5_followup"]).sum())),
        )
        .reset_index()
        .sort_values("label_family")
    )
    semantic_policy = (
        queue.groupby("semantic_pair", dropna=False)
        .agg(seed_rows=("blueprint_id", "count"), unique_blueprints=("blueprint_id", "nunique"))
        .reset_index()
        .sort_values("seed_rows", ascending=False)
    )
    motif_policy = (
        queue.groupby("motif", dropna=False)
        .agg(seed_rows=("blueprint_id", "count"), unique_blueprints=("blueprint_id", "nunique"))
        .reset_index()
        .sort_values("seed_rows", ascending=False)
    )

    generation_budget = {
        "generated_blueprints_target": 9600,
        "materialization_target": 960,
        "company_numeric_wave_blueprints": 960,
        "company_numeric_shards": 8,
        "company_numeric_shard_size": 120,
        "max_parallel_company_shards": 2,
        "external_selector_target_rows": 240,
        "external_selector_label_quota": 60,
        "deep_diagnostic_target": 64,
    }
    allowed_families = [
        {
            "family": "G0_basis_premium_volatility",
            "semantic_pairs": ["basis_premium_like|volatility_like"],
            "motifs": ["sub", "safe_div_abs", "gated_sign", "spread_rank", "mul"],
            "label_targets": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"],
        },
        {
            "family": "G1_basis_premium_positioning",
            "semantic_pairs": ["basis_premium_like|positioning_like"],
            "motifs": ["safe_div_abs", "sub", "gated_sign", "spread_rank", "mul"],
            "label_targets": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"],
        },
        {
            "family": "G2_basis_premium_relative_value",
            "semantic_pairs": ["basis_premium_like|basis_premium_like"],
            "motifs": ["sub", "spread_rank", "safe_div_abs", "gated_sign"],
            "label_targets": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"],
        },
        {
            "family": "G3_basis_premium_price_state",
            "semantic_pairs": ["basis_premium_like|price_like"],
            "motifs": ["sub", "gated_sign", "mul", "safe_div_abs"],
            "label_targets": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"],
        },
    ]
    selector_policy = {
        "must_use_external_label_balanced_selector": True,
        "forbid_a7ff8_internal_selected_queue_as_source_of_truth": True,
        "label_families": [
            "L0_raw_forward_return",
            "L1_cross_sectional_relative_return",
            "L3_liquidity_tier_relative_return",
            "L5_vol_adjusted_return",
        ],
        "label_quota_share": 0.25,
        "max_top_label_share": 0.30,
        "max_top_semantic_share": 0.35,
        "max_top_motif_share": 0.35,
        "min_cost5_or_better_share": 0.75,
        "min_strict_cost10_rows_after_selection": 80,
        "min_unique_blueprints_after_selection": 120,
        "l3_policy": "cost5_or_better_allowed; strict_cost10_preferred_but_not_required",
    }
    forbidden = [
        "A7FF8_internal_selected_queue_as_final_selector",
        "L5_only_selector_target",
        "L7_ranked_future_return_as_alpha_proof_label",
        "May_in_generation_or_selector_or_mutation",
        "full_open_formula_search",
        "alpha_proof_shadow_paper_live",
    ]

    decision = "PASS_A7FF22_LABEL_BALANCED_EXPANSION_CONTRACT_READY_FOR_A7FF23"
    manifest = {
        "stage": "A7FF-22-LABEL-BALANCED-EXPANSION-CONTRACT",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff21_decision": a7ff21.get("decision", ""),
        "seed_rows": int(len(queue)),
        "seed_unique_blueprints": int(queue["blueprint_id"].nunique()),
        "generation_budget": generation_budget,
        "uses_may": False,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_a7ff23_label_balanced_generation_contract": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    label_policy.to_csv(RUNTIME / "a7ff22_label_policy.csv", index=False)
    semantic_policy.to_csv(RUNTIME / "a7ff22_semantic_policy.csv", index=False)
    motif_policy.to_csv(RUNTIME / "a7ff22_motif_policy.csv", index=False)
    write_json(RUNTIME / "a7ff22_allowed_families.json", allowed_families)
    write_json(RUNTIME / "a7ff22_selector_policy.json", selector_policy)
    write_json(RUNTIME / "a7ff22_forbidden_policy.json", forbidden)
    write_json(RUNTIME / "a7ff22_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-22 LABEL-BALANCED EXPANSION CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-22 defines a larger label-balanced expansion route based on the confirmed A7FF-21 external selector. It does not execute generation, replay, or search. It only authorizes the next contract stage for controlled A7FF-23 generation planning.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Generation Budget

```json
{json.dumps(generation_budget, indent=2, sort_keys=True)}
```

## Selector Policy

```json
{json.dumps(selector_policy, indent=2, sort_keys=True)}
```

## Label Policy

{md_table(label_policy)}

## Semantic Policy

{md_table(semantic_policy)}

## Motif Policy

{md_table(motif_policy)}

## Allowed Families

```json
{json.dumps(allowed_families, indent=2, sort_keys=True)}
```

## Forbidden

```json
{json.dumps(forbidden, indent=2, sort_keys=True)}
```

## Boundary

- Uses May: `false`
- Executes generation: `false`
- Executes replay: `false`
- Executes search: `false`
- Authorizes alpha proof / shadow / paper / live: `false`
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
