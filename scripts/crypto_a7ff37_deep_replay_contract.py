from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff37_deep_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF37_DEEP_REPLAY_CONTRACT_20260530.md"

A7FF36_MANIFEST = REPO / "runtime" / "a7ff36_diversified_clue_forensic" / "a7ff36_manifest.json"
A7FF36_SELECTED = REPO / "runtime" / "a7ff36_diversified_clue_forensic" / "a7ff36_selected_clue_forensic.csv"
A7FF35_SAMPLE = REPO / "runtime" / "a7ff35_diversified_numeric_preflight" / "a7ff35_diversified_sample_queue.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


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

    f36 = read_json(A7FF36_MANIFEST)
    if not f36.get("authorizes_a7ff37_deep_replay_contract"):
        raise SystemExit(f"A7FF-36 does not authorize A7FF-37: {f36.get('decision')}")

    selected = pd.read_csv(A7FF36_SELECTED)
    sample = pd.read_csv(A7FF35_SAMPLE)
    selected["control_ratio_premay_max"] = pd.to_numeric(selected["control_ratio_premay_max"], errors="coerce")
    eligible = selected[
        selected["is_non_l7"].astype(str).str.lower().eq("true")
        & ~selected["control_block"].astype(str).str.lower().eq("true")
    ].copy()
    eligible_ids = set(eligible["blueprint_id"].astype(str))
    queue = sample[sample["blueprint_id"].astype(str).isin(eligible_ids)].copy()
    queue = queue.merge(
        eligible[
            [
                "blueprint_id",
                "label_family",
                "label_horizon_h",
                "forensic_decision",
                "control_ratio_premay_max",
                "score_no_may",
            ]
        ],
        on="blueprint_id",
        how="left",
        suffixes=("", "_a7ff36"),
    )
    queue["deep_replay_role"] = "non_l7_diversified_clue"
    queue["control_margin_policy"] = queue["control_ratio_premay_max"].apply(
        lambda x: "warning_margin_0p80_to_1p00" if pd.notna(x) and 0.80 <= float(x) < 1.0 else "clean_margin_lt_0p80"
    )
    queue.to_csv(RUNTIME / "a7ff37_deep_replay_queue.csv", index=False)

    excluded = selected[~selected["blueprint_id"].astype(str).isin(eligible_ids)].copy()
    excluded["exclusion_reason"] = "rank_label_only_or_control_block"
    excluded.to_csv(RUNTIME / "a7ff37_excluded_selected_rows.csv", index=False)

    queue_summary = (
        queue.groupby(["semantic_pair", "motif", "label_family"], dropna=False)
        .agg(
            replay_count=("blueprint_id", "count"),
            max_control_ratio=("control_ratio_premay_max", "max"),
            mean_score_no_may=("score_no_may", "mean"),
        )
        .reset_index()
        .sort_values("replay_count", ascending=False)
    )
    queue_summary.to_csv(RUNTIME / "a7ff37_queue_summary.csv", index=False)

    replay_plan = {
        "stage": "A7FF-37A",
        "type": "bounded_deep_replay_execution",
        "input_queue": "runtime/a7ff37_deep_replay_contract/a7ff37_deep_replay_queue.csv",
        "candidate_count": int(len(queue)),
        "symbol_universe": "strict_full_history_181",
        "labels": [
            "L0_raw_forward_return",
            "L1_cross_sectional_relative_return",
            "L3_liquidity_tier_relative_return",
            "L5_vol_adjusted_return",
            "L7_ranked_future_return_diagnostic_only",
        ],
        "horizons_hours": [1, 4, 8, 24],
        "required_controls": [
            "wrong_lag_future",
            "wrong_lag_stale",
            "time_shuffle",
            "symbol_shuffle",
            "sign_flip",
            "same_family_placebo",
        ],
        "hard_gates": {
            "eval_failure_count": 0,
            "control_ratio_block": "reject if >= 1.00 in any pre-May split",
            "control_ratio_warning": "flag if 0.80 <= ratio < 1.00",
            "non_l7_required": True,
            "rank_label_only_promotion": False,
            "may_in_scoring": False,
            "search_execution": False,
        },
        "promotion_boundary": "deep replay can only produce research-clue forensic evidence, not alpha proof",
    }
    write_json(RUNTIME / "a7ff37_deep_replay_plan.json", replay_plan)

    blockers: list[str] = []
    warnings: list[str] = []
    if len(queue) < 4:
        blockers.append("deep_replay_queue_below_4")
    if queue["semantic_pair"].nunique() < 3:
        blockers.append("deep_replay_family_count_below_3")
    if (queue["control_ratio_premay_max"] >= 1.0).any():
        blockers.append("control_block_in_deep_replay_queue")
    if (queue["control_ratio_premay_max"] >= 0.80).any():
        warnings.append("control_warning_candidate_included")
    if not excluded.empty:
        warnings.append("rank_label_selected_rows_excluded")

    decision = "PASS_A7FF37_DEEP_REPLAY_CONTRACT_READY_FOR_A7FF37A_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF37_DEEP_REPLAY_CONTRACT_BLOCKED"
    manifest = {
        "stage": "A7FF-37",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff36_decision": f36.get("decision"),
        "deep_replay_candidate_count": int(len(queue)),
        "excluded_selected_count": int(len(excluded)),
        "deep_replay_family_count": int(queue["semantic_pair"].nunique()),
        "deep_replay_motif_count": int(queue["motif"].nunique()),
        "control_warning_count": int((queue["control_ratio_premay_max"] >= 0.80).sum()),
        "control_block_count": int((queue["control_ratio_premay_max"] >= 1.0).sum()),
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff37a_bounded_deep_replay": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff37_manifest.json", manifest)
    write_json(RUNTIME / "a7ff37_decision_record.json", manifest)
    write_json(
        RUNTIME / "a7ff37_authorization_matrix.json",
        {
            "A7FF-37A_bounded_deep_replay": {"authorized": not blockers, "execution_type": "bounded_deep_replay_only"},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    report = f"""# CRYPTO A7FF-37 DEEP REPLAY CONTRACT

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-37 converts A7FF-36 non-L7 diversified clues into a bounded deep replay queue. Ranked-label-only selected rows are excluded. This is a contract stage only: no replay, no search, no alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Deep Replay Queue

{md_table(queue)}

## Queue Summary

{md_table(queue_summary)}

## Excluded Selected Rows

{md_table(excluded)}

## Replay Plan

```json
{json.dumps(replay_plan, indent=2, sort_keys=True)}
```

## Boundary

```text
bounded deep replay authorized: {str(not blockers).lower()}
replay executed: false
search executed: false
May used in scoring: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
