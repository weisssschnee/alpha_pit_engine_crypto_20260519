from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff25r5_funding_tail_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF25R5_FUNDING_TAIL_REPAIR_CONTRACT_20260530.md"
A7FF25R4 = REPO / "runtime" / "a7ff25r4_no_activity_tail_audit"


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
        if df[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    prior = read_json(A7FF25R4 / "a7ff25r4_manifest.json")
    failure = read_csv(A7FF25R4 / "a7ff25r4_failure_reason_summary.csv")
    tail_usage = read_csv(A7FF25R4 / "a7ff25r4_tail_queue_field_usage.csv")

    dense_fields = pd.DataFrame(
        [
            {
                "field_name": "funding_rate_state_last_ffill_8h",
                "source_field": "funding_rate",
                "feature_class": "dense_funding_state",
                "definition": "last observed funding_rate carried forward up to 8h; stale beyond 8h becomes NaN",
                "pit_rule": "feature available at timestamp after source observation, then usable from next 1h bar",
                "allowed_role": "signal_candidate_or_regime",
                "caveat": "must record age/staleness; no unlimited forward fill",
            },
            {
                "field_name": "funding_rate_update_age_hours",
                "source_field": "funding_rate",
                "feature_class": "funding_observation_age",
                "definition": "hours since latest observed funding_rate for symbol",
                "pit_rule": "computed only from past observations",
                "allowed_role": "neutralizer_or_regime",
                "caveat": "not standalone alpha",
            },
            {
                "field_name": "funding_rate_abs_state_168h_z",
                "source_field": "funding_rate_state_last_ffill_8h",
                "feature_class": "funding_crowding_state",
                "definition": "rolling 168h zscore of absolute dense funding state",
                "pit_rule": "past rolling window only; min_period >= 48",
                "allowed_role": "regime_or_interaction_seed",
                "caveat": "direct alpha use requires response evidence",
            },
            {
                "field_name": "funding_rate_delta_state_24h",
                "source_field": "funding_rate_state_last_ffill_8h",
                "feature_class": "funding_state_change",
                "definition": "24h change in dense funding state",
                "pit_rule": "past 24h diff only",
                "allowed_role": "signal_candidate_or_interaction_seed",
                "caveat": "must pass activity and control checks before company queue",
            },
            {
                "field_name": "funding_state_x_basis_delta",
                "source_field": "funding_rate_delta_state_24h + mark_index_basis_bps",
                "feature_class": "typed_interaction",
                "definition": "interaction between dense funding-state change and basis/premium dislocation transform",
                "pit_rule": "inherits max lag of both inputs",
                "allowed_role": "interaction_seed_only",
                "caveat": "no funding-only wrapper promotion",
            },
        ]
    )
    dense_fields.to_csv(RUNTIME / "a7ff25r5_dense_funding_state_field_contract.csv", index=False)

    blocked = pd.DataFrame(
        [
            {
                "pattern": "raw funding_rate direct wrapper",
                "examples": "Mean(funding_rate,*), Delta(funding_rate,*), ZScore(Mean(funding_rate,*))",
                "status": "blocked_from_healthy_company_queue",
                "reason": "A7FF-25R4 showed 800/800 tail blueprints fail low finite_share",
            },
            {
                "pattern": "funding_only_alpha_objective",
                "examples": "funding_rate as standalone signal family",
                "status": "blocked",
                "reason": "funding field is sparse/event-like and must be rebuilt as dense state or interaction",
            },
        ]
    )
    blocked.to_csv(RUNTIME / "a7ff25r5_blocked_funding_patterns.csv", index=False)

    queue_policy = pd.DataFrame(
        [
            {
                "gate": "dense_state_required",
                "rule": "funding-like formulas must use approved dense funding-state fields, not raw funding_rate",
                "failure_action": "reject from company wave queue",
            },
            {
                "gate": "activity_precheck",
                "rule": "finite_share >= 0.20 and nonzero_share >= 0.01 on smoke panel before queue admission",
                "failure_action": "quarantine and backfill with non-funding semantic pair",
            },
            {
                "gate": "family_backfill",
                "rule": "replace shards 08-11 with activity-capable basis/price/volatility or rebuilt funding-state interactions",
                "failure_action": "do not treat 2400-row queue as uniformly healthy",
            },
            {
                "gate": "response_evidence_required",
                "rule": "dense funding-state fields need non-L7/control-clean response before promotion beyond diagnostic",
                "failure_action": "diagnostic_only",
            },
        ]
    )
    queue_policy.to_csv(RUNTIME / "a7ff25r5_queue_repair_policy.csv", index=False)

    next_actions = {
        "A7FF-25R6": "implement dense funding-state materialization audit and activity precheck",
        "A7FF-24R2": "rebuild company queue tail after funding-state repair or backfill with healthy semantic pairs",
        "blocked": ["formula search", "large search", "alpha proof", "shadow/paper/live"],
    }
    write_json(RUNTIME / "a7ff25r5_next_actions.json", next_actions)

    manifest = {
        "stage": "A7FF-25R5",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF25R5_FUNDING_TAIL_REPAIR_CONTRACT_BUILT_NO_SEARCH_AUTH",
        "prior_stage": prior.get("stage", "A7FF-25R4"),
        "prior_decision": prior.get("decision", ""),
        "dense_funding_state_field_count": int(len(dense_fields)),
        "blocked_pattern_count": int(len(blocked)),
        "queue_policy_gate_count": int(len(queue_policy)),
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_funding_state_materialization_audit": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff25r5_manifest.json", manifest)
    write_json(RUNTIME / "a7ff25r5_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-25R5 FUNDING TAIL REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        "`PASS_A7FF25R5_FUNDING_TAIL_REPAIR_CONTRACT_BUILT_NO_SEARCH_AUTH`",
        "",
        "A7FF-25R5 converts the A7FF-25R4 no-activity funding tail failure into a repair contract. It does not generate formulas, run replay, execute search, or prove alpha.",
        "",
        "## Experiment Record",
        "",
        "```text",
        "experiment_id: 20260530_a7ff25r5_funding_tail_repair_contract",
        "objective: prevent raw sparse funding_rate wrappers from entering healthy company wave evidence",
        "input: runtime/a7ff25r4_no_activity_tail_audit/*",
        "parameters: no execution; contract-only",
        "decision: funding state repair required before funding-like tail queue can count as healthy",
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Prior Failure Summary",
        "",
        md_table(failure, 20),
        "",
        "## Tail Field Usage",
        "",
        md_table(tail_usage, 20),
        "",
        "## Dense Funding-State Field Contract",
        "",
        md_table(dense_fields, 40),
        "",
        "## Blocked Funding Patterns",
        "",
        md_table(blocked, 20),
        "",
        "## Queue Repair Policy",
        "",
        md_table(queue_policy, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "Raw funding_rate is not removed from the data layer.",
        "Raw funding_rate direct wrappers are blocked from healthy company-wave evidence until dense funding-state repair passes.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
