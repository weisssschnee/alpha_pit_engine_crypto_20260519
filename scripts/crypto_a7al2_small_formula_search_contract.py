from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
IN_DIR = REPO / "runtime" / "a7al1b_control_latency_forensic"
OUT_DIR = REPO / "runtime" / "a7al2_small_formula_search_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AL2_SMALL_FORMULA_SEARCH_CONTRACT_20260527.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    a7al1b = json.loads((IN_DIR / "a7al1b_manifest.json").read_text(encoding="utf-8"))
    policy = pd.read_csv(IN_DIR / "a7al1b_signal_policy_recommendations.csv")
    family = pd.read_csv(IN_DIR / "a7al1b_family_policy_summary.csv")

    allowed_rows = []
    for _, row in policy.iterrows():
        signal = str(row["signal_name"])
        family_name = str(row["field_family"])
        p = str(row["a7al2_policy"])
        if p == "REGIME_OR_STATE_ONLY":
            allowed_rows.append(
                {
                    "signal_name": signal,
                    "field_family": family_name,
                    "a7al2_role": "regime_state_or_neutralizer",
                    "direct_rank_allowed": False,
                    "mutation_allowed": True,
                    "required_control": "matched wrong_lag_stale_168h dominance",
                }
            )
        elif p == "BLOCK_DIRECT_ALPHA_RANK":
            allowed_rows.append(
                {
                    "signal_name": signal,
                    "field_family": family_name,
                    "a7al2_role": "mutation_source_only",
                    "direct_rank_allowed": False,
                    "mutation_allowed": True,
                    "required_control": "matched wrong_lag_future_24h and wrong_lag_stale_168h dominance",
                }
            )
        elif p == "ALLOW_FORENSIC_ONLY":
            allowed_rows.append(
                {
                    "signal_name": signal,
                    "field_family": family_name,
                    "a7al2_role": "forensic_candidate_source",
                    "direct_rank_allowed": False,
                    "mutation_allowed": True,
                    "required_control": "full matched-control dominance",
                }
            )
    allowed = pd.DataFrame(allowed_rows)
    if allowed.empty:
        allowed = pd.DataFrame(
            columns=[
                "signal_name",
                "field_family",
                "a7al2_role",
                "direct_rank_allowed",
                "mutation_allowed",
                "required_control",
            ]
        )

    control_plan = pd.DataFrame(
        [
            {
                "control": "wrong_lag_future_24h",
                "applies_to": "every selected formula",
                "pass_rule": "candidate validation/recent robust score must exceed matched control by margin and same sign stability",
            },
            {
                "control": "wrong_lag_stale_168h",
                "applies_to": "every selected formula",
                "pass_rule": "candidate must not be return-correlated or score-equivalent to stale control",
            },
            {
                "control": "time_shuffle",
                "applies_to": "top replay shortlist",
                "pass_rule": "shuffle score materially weaker than original",
            },
            {
                "control": "symbol_shuffle",
                "applies_to": "top replay shortlist",
                "pass_rule": "shuffle score materially weaker than original",
            },
            {
                "control": "same_family_random",
                "applies_to": "per field family",
                "pass_rule": "family placebo must not produce comparable candidate",
            },
        ]
    )

    execution_plan = {
        "generated_cap": 5000,
        "selector_cap": 512,
        "strict_replay_cap": 128,
        "deep_audit_cap": 32,
        "universe_primary": "U0_strict_full_history",
        "universe_diagnostic": "U1_listing_aware",
        "latency_policy": "field_native_only; fixed +2h stress prohibited",
        "portfolio_proxy": "top/bottom cross-sectional spread only at contract stage",
    }

    blockers = []
    if a7al1b.get("decision") != "PASS_A7AL1B_CONTROL_LATENCY_CLEAN":
        blockers.append("a7al1b_control_latency_hold_requires_contract_repair")
    if allowed.empty:
        blockers.append("no_allowed_mutation_sources")

    decision = "PASS_A7AL2_CONTROL_DOMINANCE_CONTRACT_DRAFTED_EXECUTION_HOLD"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_a7al1b_decision": a7al1b.get("decision"),
        "allowed_mutation_source_count": int(len(allowed)),
        "blockers_to_execution": blockers,
        "execution_plan": execution_plan,
        "executes_formula_generation": False,
        "executes_formula_search": False,
        "authorizes_a7al2_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    allowed.to_csv(OUT_DIR / "a7al2_allowed_feature_roles.csv", index=False)
    control_plan.to_csv(OUT_DIR / "a7al2_matched_control_plan.csv", index=False)
    family.to_csv(OUT_DIR / "a7al2_input_family_policy_summary.csv", index=False)
    write_json(OUT_DIR / "a7al2_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2 Small Formula Search Contract

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This is a contract only. It does not execute formula generation or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Allowed Feature Roles

{md_table(allowed, 80)}

## Matched-Control Plan

{md_table(control_plan, 80)}

## Input Family Policy Summary

{md_table(family, 80)}

## Boundary

```text
AUTHORIZED:
  Contract review / selector wiring repair.

NOT AUTHORIZED:
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
