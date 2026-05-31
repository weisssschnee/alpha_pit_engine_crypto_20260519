from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore9_bounded_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE9_BOUNDED_REPLAY_CONTRACT_20260601.md"
A7FFCORE8E = REPO / "runtime" / "a7ffcore8e_replay_preflight_packet_audit" / "a7ffcore8e_manifest.json"
PACKET = REPO / "runtime" / "a7ffcore8e_replay_preflight_packet_audit" / "a7ffcore8e_replay_preflight_packet.csv"
SHARDS = REPO / "runtime" / "a7ffcore8e_replay_preflight_packet_audit" / "a7ffcore8e_replay_preflight_shard_plan.csv"


LABELS = ["L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"]
HORIZONS = [1, 4, 8, 24]
COST_BPS = [0, 2, 5, 10]
CONTROL_SET = ["wrong_lag_future", "wrong_lag_stale", "time_shuffle", "symbol_shuffle", "same_family_placebo"]


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core8e = read_json(A7FFCORE8E)
    if core8e.get("decision") != "PASS_A7FFCORE8E_REPLAY_PREFLIGHT_PACKET_READY_FOR_CORE9_CONTRACT":
        raise SystemExit(f"A7FF-CORE8E is not ready: {core8e.get('decision')}")
    packet = pd.read_csv(PACKET)
    shard_plan = pd.read_csv(SHARDS)

    replay_protocol = {
        "input_packet": str(PACKET.relative_to(REPO)),
        "candidate_count": int(packet.shape[0]),
        "labels": LABELS,
        "horizons": HORIZONS,
        "cost_bps": COST_BPS,
        "splits": ["train", "validation", "recent"],
        "portfolio_proxy": {
            "ranking": "cross_sectional_per_timestamp",
            "long_leg": "top_decile_or_top10_if_active_count_lt_100",
            "short_leg": "bottom_decile_or_bottom10_if_active_count_lt_100",
            "weighting": "equal_weight_with_per_symbol_cap",
            "dollar_neutral": True,
            "max_symbol_weight": 0.02,
            "max_semantic_bucket_weight": 0.30,
            "max_motif_bucket_weight": 0.35,
        },
        "orientation": {
            "source": "CORE7ER numeric clue sign by label/horizon",
            "may_used": False,
            "sign_flip_policy": "diagnostic_only_not_allowed_as_abs_control_dominance",
        },
        "controls": CONTROL_SET,
        "statistics": [
            "split_spread",
            "non_overlap_offset_spread",
            "hourly_overlap_tstat",
            "block_bootstrap_tstat",
            "control_dominance_margin",
            "turnover_proxy",
            "cost_adjusted_spread",
            "symbol_month_contribution",
            "semantic_motif_concentration",
        ],
        "hard_reject": [
            "eval_error_count > 0",
            "label_or_may_token",
            "missing_field_count > 0",
            "control_ratio >= 1.0 in any primary split",
            "wrong_lag_future stronger than original",
            "single_symbol_share > 0.20",
            "single_month_share > 0.35",
            "single_semantic_bucket_share > 0.35",
            "single_motif_bucket_share > 0.35",
        ],
        "pass_gate": [
            "at least 16 replay-clean candidates",
            "at least 4 semantic buckets",
            "at least 4 motif buckets",
            "non-L7 primary label evidence remains positive",
            "controls weaker than original on primary labels",
            "cost 5bps survives for replay-clean queue",
        ],
    }
    label_contract = pd.DataFrame([{"label_id": label, "horizon": horizon, "is_primary": True} for label in LABELS for horizon in HORIZONS])
    cost_contract = pd.DataFrame([{"cost_bps": cost, "purpose": "replay_cost_stress"} for cost in COST_BPS])
    control_contract = pd.DataFrame(
        [{"control": c, "dominance_role": "hard_control"} for c in CONTROL_SET]
        + [{"control": "sign_flip", "dominance_role": "diagnostic_only_orientation_check"}]
    )
    pass_gate = pd.DataFrame([{"gate": gate} for gate in replay_protocol["pass_gate"]])
    hard_reject = pd.DataFrame([{"reject_rule": rule} for rule in replay_protocol["hard_reject"]])

    packet.to_csv(RUNTIME / "a7ffcore9_replay_contract_packet.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ffcore9_replay_shard_plan.csv", index=False)
    label_contract.to_csv(RUNTIME / "a7ffcore9_label_contract.csv", index=False)
    cost_contract.to_csv(RUNTIME / "a7ffcore9_cost_contract.csv", index=False)
    control_contract.to_csv(RUNTIME / "a7ffcore9_control_contract.csv", index=False)
    pass_gate.to_csv(RUNTIME / "a7ffcore9_pass_gate.csv", index=False)
    hard_reject.to_csv(RUNTIME / "a7ffcore9_hard_reject_rules.csv", index=False)
    write_json(RUNTIME / "a7ffcore9_replay_protocol.json", replay_protocol)
    authorization = {
        "A7FF-CORE9E bounded replay execution": True,
        "large_replay": False,
        "formula_search": False,
        "large_search": False,
        "alpha_proof": False,
        "shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore9_authorization_matrix.json", authorization)

    decision = "PASS_A7FFCORE9_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE9E"
    manifest = {
        "stage": "A7FF-CORE9",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE8E",
        "source_decision": core8e.get("decision"),
        "decision": decision,
        "candidate_count": int(packet.shape[0]),
        "semantic_bucket_count": int(packet["semantic_bucket"].nunique()),
        "motif_bucket_count": int(packet["motif_bucket"].nunique()),
        "label_count": len(LABELS),
        "horizon_count": len(HORIZONS),
        "cost_tier_count": len(COST_BPS),
        "control_count": len(CONTROL_SET),
        "shard_count": int(shard_plan.shape[0]),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core9e": True,
        "authorizes_large_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE9E bounded replay execution",
    }
    write_json(RUNTIME / "a7ffcore9_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE9 BOUNDED REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE9 defines the bounded replay protocol for the CORE8E packet. It does not execute replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Replay Protocol",
        "",
        "```json",
        json.dumps(replay_protocol, indent=2, sort_keys=True),
        "```",
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan),
        "",
        "## Label Contract",
        "",
        md_table(label_contract),
        "",
        "## Control Contract",
        "",
        md_table(control_contract),
        "",
        "## Boundary",
        "",
        "```text",
        "bounded replay execution authorized as next stage: true",
        "large replay: false",
        "formula search / large search: false",
        "alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
