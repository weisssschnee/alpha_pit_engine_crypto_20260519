from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
AS0 = REPO / "runtime" / "a7as0_v2_data_acceptance" / "a7as0_manifest.json"
AL2 = REPO / "runtime" / "a7al2_small_formula_search_contract" / "a7al2_manifest.json"
ROLE_PATH = REPO / "runtime" / "a7al2_small_formula_search_contract" / "a7al2_allowed_feature_roles.csv"
AR4_TRACE = REPO / "runtime" / "a7ar4_selector_adapter_smoke" / "a7ar4_selection_trace.csv"
OUT_DIR = REPO / "runtime" / "a7al2g_matched_control_gate"
REPORT = REPO / "reports" / "CRYPTO_A7AL2G_MATCHED_CONTROL_GATE_20260527.md"


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


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def classify_candidate(field_families: str) -> tuple[str, str]:
    parts = set(str(field_families).split("|"))
    if "positioning" in parts or "taker_ratio" in parts:
        return "not_authorized_by_a7al1b_baseline", "positioning/taker families did not pass A7AL-1 controls"
    if "basis" in parts or "funding" in parts:
        return "not_authorized_by_a7al1b_baseline", "basis/funding families did not pass A7AL-1 controls"
    if "open_interest" in parts:
        return "regime_state_or_neutralizer_only", "OI level is stale-control sensitive; no direct alpha rank"
    if "liquidity" in parts and "volatility" in parts:
        return "mutation_source_only_control_required", "liquidity/volatility structure needs future and stale wrong-lag dominance"
    if "price" in parts and "volatility" in parts:
        return "mutation_source_only_control_required", "price/volatility structure needs future and stale wrong-lag dominance"
    return "not_covered_by_a7al1b", "field-family combination is outside A7AL-1B allowed roles"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    as0 = read_json(AS0)
    al2 = read_json(AL2)
    roles = pd.read_csv(ROLE_PATH)
    trace = pd.read_csv(AR4_TRACE)
    selected = trace[trace["selected_for_pre_replay"].astype(bool)].copy()

    rows = []
    controls = [
        "one_bar_lag_stress",
        "wrong_lag_future_24h",
        "wrong_lag_stale_168h",
        "time_shuffle",
        "symbol_shuffle",
        "same_family_random",
    ]
    for _, row in selected.iterrows():
        policy, reason = classify_candidate(row.get("field_families", ""))
        direct_rank_allowed = False
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "family": row.get("family"),
                "field_families": row.get("field_families"),
                "fields": row.get("fields"),
                "operators": row.get("operators"),
                "windows": row.get("windows"),
                "skeleton_key": row.get("skeleton_key"),
                "production_key": row.get("production_key"),
                "a7al2g_policy": policy,
                "direct_rank_allowed": direct_rank_allowed,
                "policy_reason": reason,
                "required_controls": "|".join(controls),
                "one_bar_lag_required": True,
                "matched_control_dominance_required": True,
                "pass_rule": "candidate robust score must exceed max matched wrong-lag/stale/shuffle controls; one-bar-lag must not collapse",
            }
        )
    gate = pd.DataFrame(rows)
    control_specs = []
    for control in controls:
        control_specs.append(
            {
                "control": control,
                "construction": {
                    "one_bar_lag_stress": "evaluate same expression with field-native one bar delayed features",
                    "wrong_lag_future_24h": "shift every source feature family by -24h before expression evaluation",
                    "wrong_lag_stale_168h": "shift every source feature family by +168h before expression evaluation",
                    "time_shuffle": "permute timestamp blocks within split; preserve symbol membership",
                    "symbol_shuffle": "permute symbols within timestamp and split",
                    "same_family_random": "random expression from same field family / operator motif / horizon bucket",
                }[control],
                "promotion_rule": "must be materially weaker than original and cannot be return-corr equivalent",
            }
        )
    control_specs_df = pd.DataFrame(control_specs)

    policy_counts = gate["a7al2g_policy"].value_counts().rename_axis("policy").reset_index(name="count")
    not_authorized = int(gate["a7al2g_policy"].astype(str).str.startswith("not_").sum())
    blockers_to_execution = []
    if as0.get("decision") != "PASS_A7AS0_V2_DATA_ACCEPTANCE_READY_FOR_A7AL2G":
        blockers_to_execution.append("a7as0_data_acceptance_not_passed")
    if not_authorized:
        blockers_to_execution.append("selected_pool_contains_not_authorized_field_families")
    if al2.get("authorizes_a7al2_execution") is not False:
        blockers_to_execution.append("a7al2_contract_authorization_state_unexpected")
    blockers_to_execution.append("matched_control_gate_not_yet_connected_to_replay_runner")

    decision = "PASS_A7AL2G_MATCHED_CONTROL_GATE_PREFLIGHT_EXECUTION_HOLD"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_a7as0_decision": as0.get("decision"),
        "input_a7al2_decision": al2.get("decision"),
        "selected_candidates_audited": int(len(gate)),
        "required_controls": controls,
        "policy_counts": {str(r["policy"]): int(r["count"]) for _, r in policy_counts.iterrows()},
        "blockers_to_execution": blockers_to_execution,
        "executes_formula_generation": False,
        "executes_formula_search": False,
        "executes_replay": False,
        "authorizes_a7al2_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_required_step": "A7AL-2H selector repair: filter/reweight candidate pool to allowed mutation/regime roles before replay",
    }

    gate.to_csv(OUT_DIR / "a7al2g_candidate_gate_matrix.csv", index=False)
    control_specs_df.to_csv(OUT_DIR / "a7al2g_control_specs.csv", index=False)
    policy_counts.to_csv(OUT_DIR / "a7al2g_policy_counts.csv", index=False)
    roles.to_csv(OUT_DIR / "a7al2g_input_allowed_roles.csv", index=False)
    write_json(OUT_DIR / "a7al2g_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2G Matched-Control Gate

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This is a pre-replay gate preflight. It does not execute formula search, formula replay, alpha proof, shadow, paper, or live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Policy Counts

{md_table(policy_counts, 40)}

## Candidate Gate Matrix

{md_table(gate[["candidate_id", "family", "field_families", "a7al2g_policy", "direct_rank_allowed", "policy_reason"]], 120)}

## Control Specs

{md_table(control_specs_df, 40)}

## Boundary

```text
AUTHORIZED:
  A7AL-2H selector repair / candidate pool reweighting only.

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
