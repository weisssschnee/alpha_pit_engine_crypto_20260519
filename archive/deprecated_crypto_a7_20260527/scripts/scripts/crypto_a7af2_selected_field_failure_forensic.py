from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
A7AF1_DIR = ROOT / "runtime" / "a7af1_core39_selected_field_smoke"
A7AF1_AUTH = A7AF1_DIR / "a7af1_authorization_matrix.json"

OUT_DIR = ROOT / "runtime" / "a7af2_selected_field_failure_forensic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AF2_SELECTED_FIELD_FAILURE_FORENSIC_20260522.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def bool_col(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce").fillna(-np.inf) > 0.0


def reason_counts(candidates: pd.DataFrame) -> pd.DataFrame:
    counter: Counter[str] = Counter()
    for text in candidates["reject_reasons"].fillna(""):
        for item in str(text).split(";"):
            item = item.strip()
            if item:
                counter[item] += 1
    return pd.DataFrame(
        [{"reject_reason": key, "count": value} for key, value in counter.most_common()]
    )


def add_gate_columns(candidates: pd.DataFrame) -> pd.DataFrame:
    out = candidates.copy()
    out["gate_raw_validation_positive"] = bool_col(out, "raw_validation_2025H1_ann_10bps_lag0")
    out["gate_raw_recent_positive"] = bool_col(out, "raw_recent_2025H2_2026Apr_ann_10bps_lag0")
    out["gate_cost20_recent_positive"] = bool_col(out, "raw_recent_2025H2_2026Apr_ann_20bps_lag0")
    out["gate_lag1_recent_positive"] = bool_col(out, "raw_recent_2025H2_2026Apr_ann_10bps_lag1")
    out["gate_residual_recent_positive"] = bool_col(out, "residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0")
    out["gate_may_raw_positive"] = bool_col(out, "raw_may_2026_stress_ann_10bps_lag0")
    out["gate_may_residual_positive"] = bool_col(out, "residual_funding_may_2026_stress_ann_10bps_lag0")
    out["gate_controls_clean"] = pd.to_numeric(out["control_research_like_count"], errors="coerce").fillna(0).eq(0)
    out["pre_may_core_gate"] = (
        out["gate_raw_validation_positive"]
        & out["gate_raw_recent_positive"]
        & out["gate_cost20_recent_positive"]
        & out["gate_lag1_recent_positive"]
        & out["gate_residual_recent_positive"]
        & out["gate_controls_clean"]
    )
    out["post_may_positive"] = out["gate_may_raw_positive"] & out["gate_may_residual_positive"]
    out["post_may_eligible_after_core"] = out["pre_may_core_gate"] & out["post_may_positive"]
    out["candidate_underperforms_best_control_recent"] = (
        pd.to_numeric(out["raw_recent_2025H2_2026Apr_ann_10bps_lag0"], errors="coerce")
        <= pd.to_numeric(out["max_control_recent_ann_10bps_lag0"], errors="coerce")
    )
    return out


def gate_summary(candidates: pd.DataFrame) -> pd.DataFrame:
    gates = [
        "gate_raw_validation_positive",
        "gate_raw_recent_positive",
        "gate_cost20_recent_positive",
        "gate_lag1_recent_positive",
        "gate_residual_recent_positive",
        "gate_controls_clean",
        "pre_may_core_gate",
        "post_may_positive",
        "post_may_eligible_after_core",
    ]
    rows = []
    total = len(candidates)
    for gate in gates:
        count = int(candidates[gate].sum())
        rows.append({"gate": gate, "pass_count": count, "total": total, "pass_rate": count / total if total else 0.0})
    return pd.DataFrame(rows)


def family_gate_summary(candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family, part in candidates.groupby("family", observed=True):
        rows.append(
            {
                "family": family,
                "count": int(len(part)),
                "raw_validation_positive": int(part["gate_raw_validation_positive"].sum()),
                "raw_recent_positive": int(part["gate_raw_recent_positive"].sum()),
                "cost20_recent_positive": int(part["gate_cost20_recent_positive"].sum()),
                "lag1_recent_positive": int(part["gate_lag1_recent_positive"].sum()),
                "residual_recent_positive": int(part["gate_residual_recent_positive"].sum()),
                "controls_clean": int(part["gate_controls_clean"].sum()),
                "pre_may_core_gate": int(part["pre_may_core_gate"].sum()),
                "post_may_positive": int(part["post_may_positive"].sum()),
                "post_may_eligible_after_core": int(part["post_may_eligible_after_core"].sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["pre_may_core_gate", "raw_recent_positive"], ascending=[False, False])


def rank_deciles(candidates: pd.DataFrame) -> pd.DataFrame:
    out = candidates.copy()
    score = pd.to_numeric(out["raw_recent_2025H2_2026Apr_ann_10bps_lag0"], errors="coerce")
    out["recent_rank_desc"] = score.rank(method="first", ascending=False)
    n = len(out)
    out["recent_decile"] = np.ceil(out["recent_rank_desc"] / max(n / 10.0, 1.0)).astype(int).clip(1, 10)
    rows = []
    for decile, part in out.groupby("recent_decile", observed=True):
        rows.append(
            {
                "recent_decile": int(decile),
                "count": int(len(part)),
                "raw_recent_mean": float(pd.to_numeric(part["raw_recent_2025H2_2026Apr_ann_10bps_lag0"], errors="coerce").mean()),
                "post_may_positive_count": int(part["post_may_positive"].sum()),
                "post_may_positive_rate": float(part["post_may_positive"].mean()),
                "pre_may_core_gate_count": int(part["pre_may_core_gate"].sum()),
                "control_contaminated_count": int((~part["gate_controls_clean"]).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("recent_decile")


def control_forensic(candidates: pd.DataFrame, controls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    controls = controls.copy()
    controls["control_research_like"] = controls["control_research_like"].astype(bool)
    penetrating = controls[controls["control_research_like"]].copy()
    join_cols = [
        "candidate_id",
        "expression",
        "source_fields",
        "horizon",
        "decision",
        "reject_reasons",
        "raw_validation_2025H1_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_20bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag1",
        "raw_may_2026_stress_ann_10bps_lag0",
        "residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0",
        "residual_funding_may_2026_stress_ann_10bps_lag0",
    ]
    penetrating = penetrating.merge(
        candidates[join_cols],
        left_on="base_candidate_id",
        right_on="candidate_id",
        how="left",
        suffixes=("", "_base"),
    )
    penetrating = penetrating.drop(columns=["candidate_id"], errors="ignore")
    summary = (
        controls.groupby(["family", "control_mode", "control_research_like"], observed=True)
        .size()
        .reset_index(name="count")
        .sort_values(["control_research_like", "count"], ascending=[False, False])
    )
    return penetrating, summary


def weak_prior_registry(candidates: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    family_summary = family_gate_summary(candidates)
    for _, row in family_summary.iterrows():
        status = "blocked_for_expansion"
        reason = "no_pre_may_core_gate" if int(row["pre_may_core_gate"]) == 0 else "post_may_or_control_failure"
        rows.append(
            {
                "registry_item": row["family"],
                "type": "family",
                "status": status,
                "reason": reason,
                "count": int(row["count"]),
                "pre_may_core_gate": int(row["pre_may_core_gate"]),
                "post_may_eligible_after_core": int(row["post_may_eligible_after_core"]),
            }
        )
    penetrating = controls[controls["control_research_like"].astype(bool)]
    for _, row in penetrating.iterrows():
        rows.append(
            {
                "registry_item": f"{row['family']}::{row['control_mode']}",
                "type": "control_contamination",
                "status": "blocked_for_expansion",
                "reason": "negative_control_research_like",
                "count": 1,
                "pre_may_core_gate": None,
                "post_may_eligible_after_core": None,
            }
        )
    rows.append(
        {
            "registry_item": "core39_metrics_market_structure_selected_fields_a7af1",
            "type": "route",
            "status": "do_not_expand_without_new_objective",
            "reason": "zero_control_clean_clues_and_negative_control_penetration",
            "count": int(len(candidates)),
            "pre_may_core_gate": int(candidates["pre_may_core_gate"].sum()),
            "post_may_eligible_after_core": int(candidates["post_may_eligible_after_core"].sum()),
        }
    )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    auth_prev = json.loads(A7AF1_AUTH.read_text(encoding="utf-8"))
    if not auth_prev.get("authorizes_a7af2_forensic"):
        raise RuntimeError("A7AF1 does not authorize A7AF2 forensic")

    candidates = pd.read_csv(A7AF1_DIR / "a7af1_candidate_scoreboard.csv")
    controls = pd.read_csv(A7AF1_DIR / "a7af1_control_scoreboard.csv")
    candidates = add_gate_columns(candidates)

    reject_summary = reason_counts(candidates)
    gates = gate_summary(candidates)
    family_summary = family_gate_summary(candidates)
    deciles = rank_deciles(candidates)
    penetrating_controls, control_summary = control_forensic(candidates, controls)
    registry = weak_prior_registry(candidates, controls)

    pre_may_count = int(candidates["pre_may_core_gate"].sum())
    post_may_count = int(candidates["post_may_eligible_after_core"].sum())
    neg_control_count = int(controls["control_research_like"].astype(bool).sum())
    blockers = []
    if pre_may_count == 0:
        blockers.append("no_pre_may_core_gate_candidate")
    if post_may_count == 0:
        blockers.append("no_post_may_eligible_after_core_gate")
    if neg_control_count > 0:
        blockers.append("negative_control_research_like_penetration")
    if int(candidates["candidate_underperforms_best_control_recent"].sum()) > 0:
        blockers.append("some_candidates_underperform_matched_best_control_recent")

    decision = "HOLD_A7AF2_SELECTED_FIELD_FAMILY_REJECTED"
    if neg_control_count > 0:
        decision = "HOLD_A7AF2_CONTROL_CONTAMINATION_AND_NO_SIGNAL"
    elif pre_may_count > 0 and post_may_count == 0:
        decision = "HOLD_A7AF2_PRE_MAY_ONLY_NO_MAY_STRESS_SURVIVAL"

    auth = {
        "decision": decision,
        "blockers": blockers,
        "authorizes_a7ag0_core3_aggtrades_contract": True,
        "authorizes_a7af_expanded_replay": False,
        "authorizes_core39_selected_field_expansion": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_policy": "May remains post-selection stress only; this forensic does not use May for generation, ranking, threshold tuning, or authorization uplift",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "candidates": int(len(candidates)),
        "controls": int(len(controls)),
        "pre_may_core_gate_candidates": pre_may_count,
        "post_may_eligible_after_core_candidates": post_may_count,
        "negative_control_research_like": neg_control_count,
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    candidates.to_csv(OUT_DIR / "a7af2_candidate_gate_audit.csv", index=False)
    gates.to_csv(OUT_DIR / "a7af2_gate_summary.csv", index=False)
    reject_summary.to_csv(OUT_DIR / "a7af2_reject_reason_counts.csv", index=False)
    family_summary.to_csv(OUT_DIR / "a7af2_family_gate_summary.csv", index=False)
    deciles.to_csv(OUT_DIR / "a7af2_rank_decile_may_alignment.csv", index=False)
    penetrating_controls.to_csv(OUT_DIR / "a7af2_negative_control_penetration.csv", index=False)
    control_summary.to_csv(OUT_DIR / "a7af2_control_mode_summary.csv", index=False)
    registry.to_csv(OUT_DIR / "a7af2_weak_prior_registry.csv", index=False)
    write_json(OUT_DIR / "a7af2_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7af2_manifest.json", manifest)

    report = f"""# CRYPTO A7AF-2 Selected-Field Failure Forensic

Generated: {now}

## Decision

```text
{decision}
```

This stage uses only A7AF-1 artifacts. It runs no new replay and no search.

## Summary

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Bias Audit

- Factor set: fixed A7AF-1 selected core39 metrics / market-structure candidates.
- Run/experiment_id: A7AF-1 smoke, A7AF-2 forensic.
- Data source and universe: Binance core39 all-features metrics v3 + market structure v1; 39 USD-M futures symbols.
- Frequency and horizon: 1h panel, candidate horizons 24/48, ret_1 forward proxy.
- IS/OOS windows: validation 2025H1, recent 2025H2-2026Apr, May 2026 stress-only.
- OOS sample grade: method smoke only; not promotion evidence.
- Cost model: 10bps primary, 20bps severe in A7AF-1.
- Turnover: implicit hourly position change cost in A7AF-1 proxy replay.
- Discovery status: fixed smoke/replay, not formula discovery.

### Findings

- Look-ahead: no May ranking or generation; May is post-selection stress only.
- Date alignment: A7AF-0 contract uses feature available at timestamp + 1h and execution >= next 1h bar; A7AF-1 remains proxy replay, not execution-grade proof.
- Costs/lag: cost20 and lag1 are explicit gates.
- Replay vs discovery: replay smoke only; no KEEP or promotion.

### Decision

HOLD_RESEARCH. The blocker is signal/control quality, not data availability.

## Gate Summary

{md_table(gates)}

## Family Gate Summary

{md_table(family_summary)}

## Reject Reasons

{md_table(reject_summary)}

## Negative Control Penetration

{md_table(penetrating_controls)}

## Control Mode Summary

{md_table(control_summary)}

## Recent-Rank Decile vs May Alignment

{md_table(deciles)}

## Weak-Prior Registry

{md_table(registry)}

## Required Next Action

- Do not expand A7AF core39 selected-field replay.
- Do not run formula search on this selected-field family.
- Keep funding/crowding/basis fields as control/context inputs until a new objective is defined.
- The only authorized next step from this line is A7AG-0 core3 aggTrades interaction contract, not alpha promotion.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
