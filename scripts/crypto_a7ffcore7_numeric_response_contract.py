from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore7_numeric_response_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE7_NUMERIC_RESPONSE_CONTRACT_20260601.md"
A7FFCORE6E = REPO / "runtime" / "a7ffcore6e_materialization_preflight" / "a7ffcore6e_manifest.json"
QUEUE = REPO / "runtime" / "a7ffcore5_gate_native_generation_dryrun" / "a7ffcore5_gate_native_candidate_queue.csv"
MATERIALIZATION = REPO / "runtime" / "a7ffcore6e_materialization_preflight" / "a7ffcore6e_materialization_summary_rows.csv"


LABELS = [
    {"label_id": "L0_raw_forward_return", "field": "forward_trade_return_1h", "horizons": "1h;4h;8h;24h", "primary": False},
    {"label_id": "L1_cross_sectional_relative_return", "field": "derived_in_runner", "horizons": "1h;4h;8h;24h", "primary": True},
    {"label_id": "L3_liquidity_tier_relative_return", "field": "derived_in_runner", "horizons": "1h;4h;8h;24h", "primary": True},
    {"label_id": "L5_vol_adjusted_return", "field": "derived_in_runner", "horizons": "1h;4h;8h;24h", "primary": True},
    {"label_id": "L7_ranked_future_return", "field": "derived_in_runner", "horizons": "1h;4h;8h;24h", "primary": False},
]
CONTROLS = [
    "wrong_lag_future",
    "wrong_lag_stale",
    "time_shuffle",
    "symbol_shuffle",
    "sign_flip",
    "same_family_placebo",
]


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core6e = read_json(A7FFCORE6E)
    if core6e.get("decision") != "PASS_A7FFCORE6E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE7":
        raise SystemExit(f"A7FF-CORE6E is not ready: {core6e.get('decision')}")
    queue = pd.read_csv(QUEUE)
    mat = pd.read_csv(MATERIALIZATION)
    usable = mat[mat["status"].eq("ok")].copy()

    label_contract = pd.DataFrame(LABELS)
    label_contract.to_csv(RUNTIME / "a7ffcore7_label_contract.csv", index=False)
    control_contract = pd.DataFrame(
        [{"control_id": control, "required": True, "hard_gate": control in {"wrong_lag_future", "wrong_lag_stale"}} for control in CONTROLS]
    )
    control_contract.to_csv(RUNTIME / "a7ffcore7_control_contract.csv", index=False)

    shard_rows: list[dict[str, Any]] = []
    shard_size = 256
    for shard_id, start in enumerate(range(0, len(usable), shard_size)):
        shard = usable.iloc[start : start + shard_size]
        shard_rows.append(
            {
                "shard_id": f"S{shard_id:02d}",
                "start_index": int(start),
                "end_index_exclusive": int(start + len(shard)),
                "candidate_count": int(len(shard)),
                "label_count": len(LABELS),
                "control_count": len(CONTROLS),
                "expected_rows": int(len(shard) * len(LABELS) * 4),
                "expected_output": f"runtime/a7ffcore7e_numeric_response/a7ffcore7e_S{shard_id:02d}_response.csv",
            }
        )
    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(RUNTIME / "a7ffcore7_shard_plan.csv", index=False)

    response_gates = pd.DataFrame(
        [
            {"gate_id": "G00_materialized_only", "rule": "only CORE6E status=ok candidates enter numeric response", "hard_gate": True},
            {"gate_id": "G01_primary_non_l7_presence", "rule": "L1/L3/L5 primary labels must be reported separately from L7", "hard_gate": True},
            {"gate_id": "G02_control_dominance", "rule": "wrong-lag/stale controls must be weaker than original signal", "hard_gate": True},
            {"gate_id": "G03_split_consistency", "rule": "train/validation/recent split metrics emitted separately", "hard_gate": True},
            {"gate_id": "G04_nonoverlap_stats", "rule": "24h non-overlap offsets or robust stats required for any future promotion", "hard_gate": True},
            {"gate_id": "G05_no_may_selector", "rule": "May stress may not enter orientation, selector score, mutation, or ranking", "hard_gate": True},
            {"gate_id": "G06_no_replay_or_promotion", "rule": "CORE7E numeric response is not replay/search/promotion", "hard_gate": True},
        ]
    )
    response_gates.to_csv(RUNTIME / "a7ffcore7_response_gates.csv", index=False)

    execution_contract = {
        "stage": "A7FF-CORE7E",
        "input_materialization": str(MATERIALIZATION.relative_to(REPO)),
        "candidate_count": int(len(usable)),
        "labels": LABELS,
        "controls": CONTROLS,
        "shard_count": int(len(shard_plan)),
        "forbidden_actions": [
            "replay portfolio construction",
            "search",
            "candidate promotion",
            "alpha proof",
            "shadow/paper/live",
            "May-informed orientation or scoring",
        ],
        "pass_conditions_for_next_contract": {
            "primary_non_l7_clue_count_min": 1,
            "wrong_lag_control_dominated_count": 0,
            "missing_label_metric_rate_max": 0.01,
            "single_family_selected_share_max": 0.35,
        },
    }
    write_json(RUNTIME / "a7ffcore7e_execution_contract.json", execution_contract)

    blockers: list[str] = []
    if len(usable) != len(queue):
        blockers.append("not_all_queue_candidates_materialized")
    if len(usable) < 1024:
        blockers.append("usable_candidate_count_too_low")
    if len(label_contract[label_contract["primary"].astype(bool)]) < 3:
        blockers.append("primary_label_contract_too_narrow")
    if len(control_contract) < 4:
        blockers.append("control_contract_too_narrow")

    decision = "PASS_A7FFCORE7_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE7E" if not blockers else "HOLD_A7FFCORE7_NUMERIC_RESPONSE_CONTRACT_FAIL"
    manifest = {
        "stage": "A7FF-CORE7",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE6E",
        "source_decision": core6e.get("decision"),
        "materialized_candidate_count": int(len(usable)),
        "queue_candidate_count": int(len(queue)),
        "label_family_count": int(len(label_contract)),
        "primary_label_count": int(label_contract["primary"].astype(bool).sum()),
        "control_count": int(len(control_contract)),
        "shard_count": int(len(shard_plan)),
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core7e": not bool(blockers),
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE7E gate-native numeric-response execution" if not blockers else "A7FF-CORE7 contract repair",
    }
    write_json(RUNTIME / "a7ffcore7_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-CORE7 NUMERIC RESPONSE CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-CORE7 defines the numeric-response contract for the CORE6E materialized gate-native queue. It does not execute numeric response, replay, search, or promotion.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Label Contract

{md_table(label_contract, 40)}

## Control Contract

{md_table(control_contract, 40)}

## Shard Plan

{md_table(shard_plan, 40)}

## Response Gates

{md_table(response_gates, 40)}

## Execution Contract

```json
{json.dumps(execution_contract, indent=2, sort_keys=True)}
```

## Boundary

```text
numeric response executed: false
replay executed: false
search executed: false
May used for orientation/scoring: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
