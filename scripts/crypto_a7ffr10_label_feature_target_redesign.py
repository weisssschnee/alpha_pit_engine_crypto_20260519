from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffr10_label_feature_target_redesign"
REPORT = REPO / "reports" / "CRYPTO_A7FFR10_LABEL_FEATURE_TARGET_REDESIGN_20260531.md"

A7FF47_MANIFEST = REPO / "runtime" / "a7ff47_portfolio_microreplay" / "a7ff47_manifest.json"
A7FF47_LABEL_SUMMARY = REPO / "runtime" / "a7ff47_portfolio_microreplay" / "a7ff47_label_translation_summary.csv"
A7FF47_FAMILY_LABEL = REPO / "runtime" / "a7ff47_portfolio_microreplay" / "a7ff47_family_label_summary.csv"
A7FF47_TRANSLATION_MAP = REPO / "runtime" / "a7ff47_portfolio_microreplay" / "a7ff47_label_translation_map.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    f47 = read_json(A7FF47_MANIFEST)
    if f47.get("decision") != "HOLD_A7FF47_LABEL_TRANSLATION_FAIL_L5_ONLY":
        raise SystemExit(f"A7FF-47 state does not require R10 redesign: {f47.get('decision')}")

    label_summary = read_csv(A7FF47_LABEL_SUMMARY)
    family_label = read_csv(A7FF47_FAMILY_LABEL)
    translation_map = read_csv(A7FF47_TRANSLATION_MAP)

    failure_attribution = pd.DataFrame(
        [
            {
                "failure_layer": "label_target",
                "evidence": "strict translations exist only on L5_vol_adjusted_return",
                "impact": "current frozen pool is diagnostic-only and cannot become alpha/search input",
                "required_repair": "non-L5-first candidate mining from existing numeric maps",
            },
            {
                "failure_layer": "selector_reward",
                "evidence": "bounded replay rows are control-clean but L5-only",
                "impact": "selector can over-reward volatility-adjusted labels while raw/relative return translation is absent",
                "required_repair": "hard require L0/L1/L3 evidence before replay promotion",
            },
            {
                "failure_layer": "feature_role",
                "evidence": "basis/funding and regime/price clues behave as risk/vol-adjusted diagnostics",
                "impact": "do not treat L5-only clues as ordinary-alpha candidates",
                "required_repair": "demote L5-only features to diagnostic or risk-adjusted state features",
            },
        ]
    )
    failure_attribution.to_csv(RUNTIME / "a7ffr10_failure_attribution.csv", index=False)

    label_policy = pd.DataFrame(
        [
            {
                "label_family": "L0_raw_forward_return",
                "required_for_promotion": True,
                "role": "primary_non_l5_translation",
                "minimum_rows": 2,
            },
            {
                "label_family": "L1_cross_sectional_relative_return",
                "required_for_promotion": True,
                "role": "primary_non_l5_translation",
                "minimum_rows": 2,
            },
            {
                "label_family": "L3_liquidity_tier_relative_return",
                "required_for_promotion": True,
                "role": "primary_non_l5_translation",
                "minimum_rows": 2,
            },
            {
                "label_family": "L5_vol_adjusted_return",
                "required_for_promotion": False,
                "role": "supporting_risk_adjusted_diagnostic",
                "minimum_rows": 0,
            },
            {
                "label_family": "L7_ranked_future_return",
                "required_for_promotion": False,
                "role": "diagnostic_only_not_alpha_proof",
                "minimum_rows": 0,
            },
        ]
    )
    label_policy.to_csv(RUNTIME / "a7ffr10_label_target_policy.csv", index=False)

    source_maps = pd.DataFrame(
        [
            {
                "source_stage": "A7FF-42",
                "path": "runtime/a7ff42_family_balanced_numeric/a7ff42_control_strict_non_l7_clues.csv",
                "allowed": True,
                "use": "mine existing non-L5 strict clues without generation",
            },
            {
                "source_stage": "A7FF-45",
                "path": "runtime/a7ff45_bounded_deep_replay/a7ff45_label_response_metrics.csv",
                "allowed": True,
                "use": "negative reference for L5-only frozen pool",
            },
            {
                "source_stage": "A7FF-47",
                "path": "runtime/a7ff47_portfolio_microreplay/a7ff47_label_translation_map.csv",
                "allowed": True,
                "use": "label translation failure attribution",
            },
        ]
    )
    source_maps.to_csv(RUNTIME / "a7ffr10_allowed_source_maps.csv", index=False)

    next_contract = {
        "stage": "A7FF-49",
        "name": "existing-map non-L5 candidate mining",
        "allowed_inputs": source_maps[source_maps["allowed"]].to_dict("records"),
        "requirements": {
            "no_new_generation": True,
            "no_search": True,
            "require_non_l5_labels": ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"],
            "allow_l5_only_as_diagnostic": True,
            "control_ratio_max": 0.80,
            "min_candidate_rows": 6,
            "min_semantic_families": 2,
        },
        "not_authorized": ["formula_search", "large_search", "alpha_proof", "shadow", "paper", "live"],
    }
    write_json(RUNTIME / "a7ffr10_next_contract_a7ff49.json", next_contract)

    manifest = {
        "stage": "A7FF-R10",
        "generated_at": now_utc(),
        "decision": "PASS_A7FFR10_LABEL_FEATURE_TARGET_REDESIGN_READY_FOR_A7FF49_NO_SEARCH_AUTH",
        "source_a7ff47_decision": f47.get("decision"),
        "blockers": [],
        "warnings": ["current_frozen_pool_is_l5_only_diagnostic"],
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff49_existing_map_non_l5_mining": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffr10_manifest.json", manifest)
    write_json(RUNTIME / "a7ffr10_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-R10 LABEL / FEATURE TARGET REDESIGN

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-R10 converts the A7FF-47 L5-only hold into a stricter target policy. It does not generate formulas, run replay, or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Failure Attribution

{md_table(failure_attribution)}

## Label Target Policy

{md_table(label_policy)}

## Allowed Source Maps

{md_table(source_maps)}

## A7FF-47 Label Summary

{md_table(label_summary)}

## A7FF-47 Family Label Summary

{md_table(family_label)}

## Next Contract: A7FF-49

```json
{json.dumps(next_contract, indent=2, sort_keys=True)}
```

## Boundary

```text
generation executed: false
numeric probe executed: false
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
