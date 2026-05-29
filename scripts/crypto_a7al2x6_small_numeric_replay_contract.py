from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "a7al2x6_small_numeric_replay_contract"
REPORT = ROOT / "reports" / "CRYPTO_A7AL2X6_SMALL_NUMERIC_REPLAY_CONTRACT_20260529.md"

X5_MANIFEST = ROOT / "runtime" / "a7al2x5_evaluator_preflight_smoke" / "a7al2x5_manifest.json"
X3_LEDGER = ROOT / "runtime" / "a7al2x3_family_balanced_dry_generation" / "a7al2x3_generated_candidate_ledger.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    x5 = load_json(X5_MANIFEST)
    ledger = pd.read_csv(X3_LEDGER)
    selected = ledger[ledger["selected_for_family_balanced_preflight"].astype(str).str.lower().isin(["true", "1"])].copy()
    family_counts = selected.groupby("objective_family").size().rename("selected_available").reset_index()

    candidate_policy = pd.DataFrame(
        [
            ("input_pool", "A7AL-2X3 selected_for_family_balanced_preflight candidates only"),
            ("input_gate", "requires A7AL-2X4M PASS and A7AL-2X5 PASS"),
            ("candidate_cap", "56 candidates max"),
            ("family_quota", "up to 8 candidates per F0-F6 objective family"),
            ("selection_order", "family-balanced; skeleton diversity; production diversity; no May score"),
            ("symbol_sample", "strict_full_history symbols, max 96 for X7 preflight"),
            ("frequency", "1h"),
            ("label", "log trade_close[t+24h] - log trade_close[t]"),
            ("label_boundary", "label end must remain inside split"),
            ("cost_proxy", "report 0/2/5/10 bps proxy net spread; no production cost proof"),
            ("neutralization", "report original plus state-aware evaluator compatibility; full neutral replay remains later"),
        ],
        columns=["policy_key", "policy_value"],
    )

    replay_metric_contract = pd.DataFrame(
        [
            ("original", "primary signal spread", "required"),
            ("one_bar_lag", "execution alignment stress", "required"),
            ("wrong_lag_future_24h", "lookahead/control contamination check", "required"),
            ("wrong_lag_stale_168h", "stale-lag/control contamination check", "required"),
            ("time_shuffle", "time null", "required"),
            ("symbol_shuffle", "cross-section null", "required"),
            ("same_family_random", "same-family random placebo", "required"),
            ("overlap_disclosure", "24h labels overlap; report naive tstat as diagnostic only", "required"),
            ("non_overlap_offsets", "24 offset tstats if implemented in X7", "recommended"),
        ],
        columns=["metric_or_variant", "purpose", "requirement"],
    )

    control_policy = pd.DataFrame(
        [
            ("control_ratio >= 1.00 in any pre-May split", "hard_reject"),
            ("0.80 <= control_ratio < 1.00", "warning"),
            ("wrong_lag_future stronger than original", "hard_reject"),
            ("wrong_lag_stale stronger than original", "hard_reject"),
            ("May pass/fail in selector", "forbidden"),
            ("May stress", "post-selection veto/attribution only"),
        ],
        columns=["condition", "policy"],
    )

    bias_audit = pd.DataFrame(
        [
            ("lookahead", "feature fields must come from A7AL-2X5 materialized fields; no future rank statistics"),
            ("survivorship", "X7 preflight uses strict_full_history sample only; universe498 remains current/listing-aware outside proof"),
            ("date_alignment", "signal at t; label t to t+24h; one_bar_lag variant required"),
            ("label_horizon", "24h overlapping label disclosed; naive tstat not promotion evidence"),
            ("transaction_cost", "bps proxy only; no production cost proof"),
            ("turnover", "not a tradable book; report signal turnover proxy if implemented later"),
            ("replay_vs_discovery", "X7 is replay preflight from generated pool, not discovery proof"),
        ],
        columns=["audit_item", "contract"],
    )

    authorization = {
        "decision": "PASS_A7AL2X6_SMALL_NUMERIC_REPLAY_CONTRACT_READY_FOR_A7AL2X7",
        "requires_x5_decision": "PASS_A7AL2X5_EVALUATOR_PREFLIGHT_SMOKE_READY_FOR_SMALL_REPLAY_CONTRACT",
        "x5_decision": x5.get("decision"),
        "authorizes_a7al2x7_small_numeric_replay_preflight": x5.get("decision")
        == "PASS_A7AL2X5_EVALUATOR_PREFLIGHT_SMOKE_READY_FOR_SMALL_REPLAY_CONTRACT",
        "authorizes_full_numeric_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    if not authorization["authorizes_a7al2x7_small_numeric_replay_preflight"]:
        authorization["decision"] = "HOLD_A7AL2X6_X5_NOT_PASS"

    experiment = {
        "date": now_utc(),
        "experiment_id": "20260529_a7al2x6_small_numeric_replay_contract_001",
        "objective": "Define bounded numeric replay preflight after A7AL-2X5 evaluator smoke PASS.",
        "status": "completed",
        "mode": "light",
        "inputs": {
            "x5_manifest": str(X5_MANIFEST),
            "x3_ledger": str(X3_LEDGER),
            "selected_available": int(len(selected)),
            "family_counts": dict(zip(family_counts["objective_family"], family_counts["selected_available"])),
        },
        "parameters": {
            "candidate_cap": 56,
            "per_family_cap": 8,
            "symbol_cap": 96,
            "label_horizon_hours": 24,
            "frequency": "1h",
        },
        "decision": authorization["decision"],
        "next_action": "Run A7AL-2X7 small numeric replay preflight only if X6 authorization is true.",
    }

    candidate_policy.to_csv(RUNTIME / "a7al2x6_candidate_sample_policy.csv", index=False)
    replay_metric_contract.to_csv(RUNTIME / "a7al2x6_replay_metric_contract.csv", index=False)
    control_policy.to_csv(RUNTIME / "a7al2x6_control_policy.csv", index=False)
    bias_audit.to_csv(RUNTIME / "a7al2x6_bias_audit_contract.csv", index=False)
    family_counts.to_csv(RUNTIME / "a7al2x6_available_family_counts.csv", index=False)
    write_json(RUNTIME / "a7al2x6_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7al2x6_experiment_record.json", experiment)
    write_json(
        RUNTIME / "a7al2x6_manifest.json",
        {
            "stage": "A7AL-2X6",
            "generated_at": now_utc(),
            "decision": authorization["decision"],
            "executes_replay": False,
            "executes_search": False,
            "executes_training": False,
            "selected_available": int(len(selected)),
            "candidate_cap": 56,
            "per_family_cap": 8,
            "authorizes_a7al2x7_small_numeric_replay_preflight": authorization[
                "authorizes_a7al2x7_small_numeric_replay_preflight"
            ],
            "authorizes_alpha_proof": False,
            "authorizes_shadow_paper_live": False,
        },
    )

    report = f"""# CRYPTO A7AL-2X6 SMALL NUMERIC REPLAY CONTRACT

Generated: {now_utc()}

## Decision

`{authorization["decision"]}`

This is a contract stage. It does not run replay, search, training, or proof.

## Candidate Sample Policy

{md_table(candidate_policy)}

## Available Family Counts

{md_table(family_counts)}

## Replay Metric Contract

{md_table(replay_metric_contract)}

## Control Policy

{md_table(control_policy)}

## Bias Audit Contract

{md_table(bias_audit)}

## Authorization

```json
{json.dumps(authorization, indent=2, sort_keys=True)}
```

## Boundary

```text
Authorized next:
  A7AL-2X7 small numeric replay preflight, only within this contract.

Not authorized:
  full numeric replay
  formula generation/search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
