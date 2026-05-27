from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
GATE_DIR = REPO / "runtime" / "a7al2g_matched_control_gate"
OUT_DIR = REPO / "runtime" / "a7al2h_selector_repair"
REPORT = REPO / "reports" / "CRYPTO_A7AL2H_SELECTOR_REPAIR_20260527.md"


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
    gate_manifest = json.loads((GATE_DIR / "a7al2g_manifest.json").read_text(encoding="utf-8"))
    gate = pd.read_csv(GATE_DIR / "a7al2g_candidate_gate_matrix.csv")
    eligible = gate[~gate["a7al2g_policy"].astype(str).str.startswith("not_")].copy()

    # Diversity-first repair: retain all eligible candidates, but enforce per-policy and per-skeleton accounting.
    eligible["repaired_selector_status"] = "selected_for_control_gated_pre_replay"
    eligible["repaired_selector_reason"] = eligible["a7al2g_policy"]
    eligible["rank_execution_allowed"] = False
    eligible["requires_matched_control_bundle"] = True

    rejected = gate[gate["a7al2g_policy"].astype(str).str.startswith("not_")].copy()
    rejected["repaired_selector_status"] = "rejected_before_replay"
    rejected["repaired_selector_reason"] = rejected["a7al2g_policy"]

    repaired = pd.concat([eligible, rejected], ignore_index=True)
    selected_count = int((repaired["repaired_selector_status"] == "selected_for_control_gated_pre_replay").sum())
    selected = repaired[repaired["repaired_selector_status"] == "selected_for_control_gated_pre_replay"].copy()
    skeleton_count = int(selected["skeleton_key"].nunique()) if not selected.empty else 0
    top_skeleton_share = (
        float(selected["skeleton_key"].value_counts(normalize=True).iloc[0]) if not selected.empty else 0.0
    )
    policy_counts = selected["a7al2g_policy"].value_counts().rename_axis("policy").reset_index(name="selected_count")
    family_counts = selected["field_families"].value_counts().rename_axis("field_families").reset_index(name="selected_count")

    blockers = []
    if gate_manifest.get("decision") != "PASS_A7AL2G_MATCHED_CONTROL_GATE_PREFLIGHT_EXECUTION_HOLD":
        blockers.append("a7al2g_not_passed")
    if selected_count < 12:
        blockers.append("selected_control_gated_pool_too_small")
    if skeleton_count < 10:
        blockers.append("selected_skeleton_diversity_too_low")
    if top_skeleton_share > 0.20:
        blockers.append("top_skeleton_share_above_20pct")

    decision = "PASS_A7AL2H_SELECTOR_REPAIRED_READY_FOR_REPLAY_PREFLIGHT" if not blockers else "HOLD_A7AL2H_SELECTOR_REPAIR_INSUFFICIENT"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_a7al2g_decision": gate_manifest.get("decision"),
        "input_candidates": int(len(gate)),
        "selected_control_gated_candidates": selected_count,
        "rejected_not_authorized_candidates": int(len(rejected)),
        "selected_skeleton_count": skeleton_count,
        "top_skeleton_share": top_skeleton_share,
        "blockers": blockers,
        "executes_formula_generation": False,
        "executes_formula_search": False,
        "executes_replay": False,
        "authorizes_a7al2_replay_preflight": not blockers,
        "authorizes_a7al2_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_required_step": "A7AL-2I replay preflight: evaluate selected control-gated candidates and matched controls on base v2 with one-bar-lag stress",
    }

    repaired.to_csv(OUT_DIR / "a7al2h_repaired_selection_trace.csv", index=False)
    selected.to_csv(OUT_DIR / "a7al2h_selected_control_gated_candidates.csv", index=False)
    rejected.to_csv(OUT_DIR / "a7al2h_rejected_not_authorized_candidates.csv", index=False)
    policy_counts.to_csv(OUT_DIR / "a7al2h_selected_policy_counts.csv", index=False)
    family_counts.to_csv(OUT_DIR / "a7al2h_selected_family_counts.csv", index=False)
    write_json(OUT_DIR / "a7al2h_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2H Selector Repair

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This stage repairs the pre-replay selector. It does not run replay or formula search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Selected Policy Counts

{md_table(policy_counts, 40)}

## Selected Family Counts

{md_table(family_counts, 40)}

## Selected Control-Gated Candidates

{md_table(selected[["candidate_id", "family", "field_families", "a7al2g_policy", "required_controls"]], 80)}

## Rejected Not-Authorized Candidates

{md_table(rejected[["candidate_id", "family", "field_families", "a7al2g_policy", "policy_reason"]], 80)}

## Boundary

```text
AUTHORIZED:
  A7AL-2I replay preflight only if decision PASS.

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
