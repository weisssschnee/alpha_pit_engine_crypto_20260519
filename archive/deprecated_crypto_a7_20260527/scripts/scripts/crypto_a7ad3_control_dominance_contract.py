from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
A7AD2_DIR = ROOT / "runtime" / "a7ad2_core48_control_forensic"
OUT_DIR = ROOT / "runtime" / "a7ad3_control_dominance_contract"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AD3_CONTROL_DOMINANCE_CONTRACT_20260522.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    contamination = pd.read_csv(A7AD2_DIR / "a7ad2_control_contamination_by_family.csv")
    top_controls = pd.read_csv(A7AD2_DIR / "a7ad2_top_research_like_controls.csv")

    family_policy = pd.DataFrame(
        [
            {
                "family": "F0_low_turnover_price_basis",
                "status": "allow_limited",
                "reason": "no research-like controls, but broad raw/cost/residual weakness",
                "next_quota": 32,
            },
            {
                "family": "F1_funding_residual_controls",
                "status": "benchmark_only",
                "reason": "funding controls have sign/wrong-lag pass; do not promote standalone funding motifs",
                "next_quota": 16,
            },
            {
                "family": "F2_metrics_crowding_oi_interaction",
                "status": "redesign_required",
                "reason": "wrong_lag_stale_24h dominates top apparent positives; require delta/persistence/non-stale transformations",
                "next_quota": 48,
            },
            {
                "family": "F3_cross_symbol_relative_strength",
                "status": "redesign_required",
                "reason": "wrong_lag controls pass at high rate; require change-based or regime-conditional variants",
                "next_quota": 24,
            },
            {
                "family": "F4_volatility_liquidity_capped",
                "status": "quarantine",
                "reason": "sign-flip and wrong-lag controls pass; previous liquidity/volatility collapse risk remains",
                "next_quota": 8,
            },
        ]
    )

    dominance_rules = pd.DataFrame(
        [
            {
                "rule_id": "D0",
                "rule": "matched_controls_required_for_every_candidate",
                "threshold": "all candidates",
                "effect": "candidate cannot be shortlisted without matched sign_flip,row_shuffle,time_shuffle,wrong_lag_stale_24h controls",
            },
            {
                "rule_id": "D1",
                "rule": "wrong_lag_strict_block",
                "threshold": "any matched wrong_lag_stale_24h control passes validation and recent raw 10bps",
                "effect": "candidate and same motif are rejected for the smoke",
            },
            {
                "rule_id": "D2",
                "rule": "sign_flip_orientation_block",
                "threshold": "matched sign_flip passes validation and recent raw 10bps",
                "effect": "candidate family/motif is orientation-unstable; demote to diagnostic only",
            },
            {
                "rule_id": "D3",
                "rule": "control_margin",
                "threshold": "candidate recent robust score > max matched control score + 25pct relative margin",
                "effect": "candidate must materially dominate controls, not merely tie them",
            },
            {
                "rule_id": "D4",
                "rule": "stale_sensitive_feature_quarantine",
                "threshold": "open_interest_value_zscore_168h x realized_vol/ret motifs with wrong-lag control pass",
                "effect": "do not expand stale-sensitive OI x vol/trend motifs until redesigned",
            },
        ]
    )

    next_smoke_contract = pd.DataFrame(
        [
            {
                "item": "scope",
                "value": "A7AE-0 contract only, then A7AE-1 <= 96 candidate controlled smoke if contract passes",
            },
            {
                "item": "candidate_focus",
                "value": "change/persistence/regime interaction variants; avoid static OI level x realized_vol dominance",
            },
            {
                "item": "cost_lag",
                "value": "10bps/20bps and lag0/lag1 required; lag2 diagnostic",
            },
            {
                "item": "controls",
                "value": "matched controls mandatory; wrong-lag strict block; sign-flip orientation block",
            },
            {
                "item": "may_policy",
                "value": "May still unavailable for core48 common window; future May is stress-only",
            },
            {
                "item": "authorization",
                "value": "no formula search, no large search, no alpha proof, no shadow/paper/live",
            },
        ]
    )

    decision = "PASS_A7AD3_CONTROL_DOMINANCE_CONTRACT_READY"
    auth = {
        "decision": decision,
        "authorizes_a7ae0_candidate_redesign_contract": True,
        "authorizes_a7ad1_rerun_same_contract": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "research_like_controls_from_a7ad2": int(top_controls.shape[0]),
        "families_requiring_redesign_or_quarantine": int(family_policy[family_policy["status"].isin(["redesign_required", "quarantine"])].shape[0]),
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    family_policy.to_csv(OUT_DIR / "a7ad3_family_policy_revision.csv", index=False)
    dominance_rules.to_csv(OUT_DIR / "a7ad3_control_dominance_rules.csv", index=False)
    next_smoke_contract.to_csv(OUT_DIR / "a7ad3_next_smoke_contract.csv", index=False)
    write_json(OUT_DIR / "a7ad3_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ad3_manifest.json", manifest)

    report = f"""# CRYPTO A7AD-3 Control Dominance Contract

Generated: {now}

## Decision

```text
{decision}
```

This stage does not run replay and does not run search. It converts A7AD-2 failures into stricter replay rules.

## Summary

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Family Policy Revision

{md_table(family_policy)}

## Control Dominance Rules

{md_table(dominance_rules)}

## Next Smoke Contract

{md_table(next_smoke_contract)}

## Evidence Inputs

### A7AD-2 Control Contamination

{md_table(contamination)}

### Top Research-Like Controls

{md_table(top_controls, 20)}

## Boundary

- Do not rerun A7AD-1 unchanged.
- Do not expand F2/F3/F4 directly.
- Do not treat static OI-level x volatility/trend motifs as research clues unless they dominate wrong-lag controls.
- A7AE-0 should redesign candidate grammar first; A7AE-1 can be a smaller controlled smoke after that.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
