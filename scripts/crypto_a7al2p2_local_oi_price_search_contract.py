from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2p2_local_oi_price_search_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AL2P2_LOCAL_OI_PRICE_SEARCH_CONTRACT_20260528.md"

P1S_DECISION = REPO / "runtime" / "a7al2p1s_selected_pool_provenance" / "a7al2p1s_decision_record.json"
P1S_PROVENANCE = REPO / "runtime" / "a7al2p1s_selected_pool_provenance" / "a7al2p1s_candidate_provenance.csv"
P1R_DECISION = REPO / "runtime" / "a7al2p1r_selector_reweighted_retry" / "a7al2p1r_decision_record.csv"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_object_dtype(view[col]) or pd.api.types.is_string_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```\n" + view.to_string(index=False) + "\n```"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    p1s = read_json(P1S_DECISION)
    if p1s.get("decision") != "PASS_A7AL2P1S_SELECTED_POOL_PROVENANCE_CLEAN":
        raise SystemExit("A7AL-2P1S is not clean; cannot draft A7AL-2P2")

    provenance = pd.read_csv(P1S_PROVENANCE)
    p1r = pd.read_csv(P1R_DECISION)
    seeds = provenance.merge(
        p1r[["candidate_id", "decision", "warnings", "control_ratio_premay_max_by_split", "latent_positive_premay_splits", "recent_turnover"]],
        on="candidate_id",
        how="left",
        suffixes=("", "_p1r"),
    )
    seeds = seeds[
        [
            "candidate_id",
            "expression",
            "fields",
            "field_families",
            "skeleton_key",
            "production_key",
            "p1r_decision",
            "decision",
            "warnings",
            "control_ratio_premay_max_by_split",
            "latent_positive_premay_splits",
            "recent_turnover",
        ]
    ].rename(columns={"decision": "p1r_decision_from_record"})

    allowed_fields = pd.DataFrame(
        [
            {"field": "open_interest_last", "family": "open_interest", "role": "primary"},
            {"field": "open_interest_mean", "family": "open_interest", "role": "primary"},
            {"field": "open_interest_value_last", "family": "open_interest", "role": "primary"},
            {"field": "open_interest_value_mean", "family": "open_interest", "role": "primary"},
            {"field": "trade_close", "family": "price", "role": "primary_price"},
            {"field": "mark_close", "family": "price", "role": "primary_price"},
            {"field": "index_close", "family": "price", "role": "primary_price"},
            {"field": "premium_close", "family": "basis", "role": "diagnostic_interaction_only"},
            {"field": "premium_close_bps", "family": "basis", "role": "diagnostic_interaction_only"},
            {"field": "mark_index_basis_bps", "family": "basis", "role": "diagnostic_interaction_only"},
            {"field": "R3_liquidity_cycle", "family": "upper_regime", "role": "allowed_if_lineage_clean"},
            {"field": "R4_leverage_crowding", "family": "upper_regime", "role": "allowed_if_lineage_clean"},
            {"field": "R5_basis_dislocation", "family": "upper_regime", "role": "allowed_if_lineage_clean"},
            {"field": "R10_stress_proxy", "family": "upper_regime", "role": "allowed_if_lineage_clean"},
        ]
    )
    allowed_transforms = pd.DataFrame(
        [
            {"transform": name, "status": "allowed", "constraint": constraint}
            for name, constraint in [
                ("Mean", "past-only rolling window"),
                ("Delta", "past-only difference"),
                ("ZScore", "cross-sectional or past-only rolling; lineage required"),
                ("Rank", "cross-sectional at timestamp"),
                ("CSRank", "cross-sectional at timestamp"),
                ("Sub", "bounded arithmetic"),
                ("Mul", "two-term interaction only unless explicitly justified"),
                ("SafeDiv", "finite-denominator guard required"),
                ("Clip", "fixed non-May bounds"),
                ("Winsor", "fixed non-May bounds"),
                ("TSRank", "past-only rolling window"),
                ("Decay", "past-only smoothing"),
            ]
        ]
    )
    forbidden = pd.DataFrame(
        [
            {"item": "funding-only wrapper", "reason": "would reopen old funding residual route"},
            {"item": "basis/liquidity old families as standalone", "reason": "A7V/A7P failure family"},
            {"item": "activity/liquidity A7V family", "reason": "source-trace-clean but signal HOLD"},
            {"item": "J5 stale overlay aliases", "reason": "canonical contract only"},
            {"item": "mark_basis_bps_okx_minus_binance", "reason": "blocked direct/raw overlay alias"},
            {"item": "index_spread_bps_okx_minus_binance", "reason": "blocked direct/raw overlay alias"},
            {"item": "cross-exchange direct raw price comparison", "reason": "contract-unit unsafe"},
            {"item": "May-informed regime mask", "reason": "May remains stress-only"},
            {"item": "deep nested conditionals", "reason": "local seed search only"},
            {"item": "SignedPower", "reason": "unbounded nonlinear transform"},
            {"item": "full FormulaGenV2 open grammar", "reason": "not authorized for local contract"},
        ]
    )
    pass_gates = pd.DataFrame(
        [
            {"gate": "no_stale_artifact", "requirement": "P1S stays PASS"},
            {"gate": "control_dominance", "requirement": "no control ratio >= 1.0 in any pre-May split"},
            {"gate": "timevarying_latent", "requirement": "positive in all pre-May splits"},
            {"gate": "label_alignment", "requirement": "label_t1 and label_t2 positive in all pre-May splits"},
            {"gate": "overlap_robust_stats", "requirement": "overlap/non-overlap stats do not collapse"},
            {"gate": "cost_proxy", "requirement": "2/5/10bps proxy survives"},
            {"gate": "concentration", "requirement": "no single symbol/month/latent state dominates"},
            {"gate": "skeleton_diversity", "requirement": "no single skeleton > 20%"},
            {"gate": "negative_controls", "requirement": "attached and weaker than original"},
            {"gate": "may_exclusion", "requirement": "no May in selector/ranking/mutation"},
        ]
    )
    budget = {
        "generated_total": 4000,
        "selected_for_fast_replay": 128,
        "deep_audit": 16,
        "seed_count": int(len(seeds)),
        "scope": "local OI-price seed search only",
        "authorizes_a7al2q_local_execution": True,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
    }

    manifest = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AL2P2_LOCAL_OI_PRICE_SEARCH_CONTRACT_READY_FOR_A7AL2Q",
        "input_p1s_decision": p1s.get("decision"),
        "seed_candidates": seeds["candidate_id"].astype(str).tolist(),
        "budget": budget,
        "executes_training": False,
        "executes_search": False,
        "executes_alpha_proof": False,
        "uses_may_for_selection": False,
        "authorizes_a7al2q_local_execution": True,
        "authorizes_a7al2p2_execution": False,
        "authorizes_large_search": False,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "required_next": "Run A7AL-2Q local small formula-search execution only if operator/field implementation matches this contract.",
    }

    seeds.to_csv(OUT_DIR / "a7al2p2_seed_candidates.csv", index=False)
    allowed_fields.to_csv(OUT_DIR / "a7al2p2_allowed_fields.csv", index=False)
    allowed_transforms.to_csv(OUT_DIR / "a7al2p2_allowed_transforms.csv", index=False)
    forbidden.to_csv(OUT_DIR / "a7al2p2_forbidden_items.csv", index=False)
    pass_gates.to_csv(OUT_DIR / "a7al2p2_pass_fail_gates.csv", index=False)
    write_json(OUT_DIR / "a7al2p2_budget.json", budget)
    write_json(OUT_DIR / "a7al2p2_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2P2 Local OI-Price Search Contract

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This is a contract only. It does not execute formula search, replay, training, alpha proof, shadow, paper, or live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Seed Candidates

{md_table(seeds, 20)}

## Allowed Fields

{md_table(allowed_fields, 40)}

## Allowed Transforms

{md_table(allowed_transforms, 40)}

## Forbidden Items

{md_table(forbidden, 40)}

## Pass / Hold Gates

{md_table(pass_gates, 40)}

## Boundary

```text
Authorized:
  A7AL-2Q local small formula-search execution drafting/execution

Not authorized:
  full FormulaGenV2 open grammar
  large search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
