from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
A7AG1_DIR = ROOT / "runtime" / "a7ag1_core3_aggtrades_interaction_smoke"
A7AG1_AUTH = A7AG1_DIR / "a7ag1_authorization_matrix.json"

OUT_DIR = ROOT / "runtime" / "a7ag2_aggtrades_interaction_failure_forensic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AG2_AGGTRADES_INTERACTION_FAILURE_FORENSIC_20260522.md"


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


def gt0(df: pd.DataFrame, col: str) -> pd.Series:
    return pd.to_numeric(df[col], errors="coerce").fillna(-np.inf).gt(0.0)


def add_gates(score: pd.DataFrame) -> pd.DataFrame:
    out = score.copy()
    out["gate_raw_validation_positive"] = gt0(out, "raw_validation_2025H1_ann_10bps_lag0")
    out["gate_raw_recent_positive"] = gt0(out, "raw_recent_2025H2_2026Apr_ann_10bps_lag0")
    out["gate_cost20_recent_positive"] = gt0(out, "raw_recent_2025H2_2026Apr_ann_20bps_lag0")
    out["gate_lag1_recent_positive"] = gt0(out, "raw_recent_2025H2_2026Apr_ann_10bps_lag1")
    out["gate_lag2_recent_positive"] = gt0(out, "raw_recent_2025H2_2026Apr_ann_10bps_lag2")
    out["gate_residual_recent_positive"] = gt0(out, "residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0")
    out["gate_may_raw_positive"] = gt0(out, "raw_may_2026_stress_ann_10bps_lag0")
    out["gate_may_residual_positive"] = gt0(out, "residual_funding_may_2026_stress_ann_10bps_lag0")
    out["gate_controls_clean"] = pd.to_numeric(out["control_research_like_count"], errors="coerce").fillna(0).eq(0)
    out["pre_may_core_gate"] = (
        out["gate_raw_validation_positive"]
        & out["gate_raw_recent_positive"]
        & out["gate_cost20_recent_positive"]
        & out["gate_lag1_recent_positive"]
        & out["gate_lag2_recent_positive"]
        & out["gate_residual_recent_positive"]
        & out["gate_controls_clean"]
    )
    out["post_may_positive"] = out["gate_may_raw_positive"] & out["gate_may_residual_positive"]
    out["post_may_eligible_after_core"] = out["pre_may_core_gate"] & out["post_may_positive"]
    return out


def gate_summary(score: pd.DataFrame) -> pd.DataFrame:
    gates = [
        "gate_raw_validation_positive",
        "gate_raw_recent_positive",
        "gate_cost20_recent_positive",
        "gate_lag1_recent_positive",
        "gate_lag2_recent_positive",
        "gate_residual_recent_positive",
        "gate_controls_clean",
        "pre_may_core_gate",
        "post_may_positive",
        "post_may_eligible_after_core",
    ]
    total = len(score)
    return pd.DataFrame(
        [{"gate": gate, "pass_count": int(score[gate].sum()), "total": total, "pass_rate": float(score[gate].mean())} for gate in gates]
    )


def reject_counts(score: pd.DataFrame) -> pd.DataFrame:
    counter: Counter[str] = Counter()
    for text in score["reject_reasons"].fillna(""):
        for item in str(text).split(";"):
            item = item.strip()
            if item:
                counter[item] += 1
    return pd.DataFrame([{"reject_reason": key, "count": value} for key, value in counter.most_common()])


def family_summary(score: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family, part in score.groupby("family", observed=True):
        rows.append(
            {
                "family": family,
                "count": int(len(part)),
                "pre_may_core_gate": int(part["pre_may_core_gate"].sum()),
                "post_may_positive": int(part["post_may_positive"].sum()),
                "post_may_eligible_after_core": int(part["post_may_eligible_after_core"].sum()),
                "raw_recent_positive": int(part["gate_raw_recent_positive"].sum()),
                "cost20_recent_positive": int(part["gate_cost20_recent_positive"].sum()),
                "lag2_recent_positive": int(part["gate_lag2_recent_positive"].sum()),
                "residual_recent_positive": int(part["gate_residual_recent_positive"].sum()),
                "control_contaminated": int((~part["gate_controls_clean"]).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["pre_may_core_gate", "raw_recent_positive"], ascending=[False, False])


def control_penetration(score: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
    penetrating = controls[controls["control_research_like"].astype(bool)].copy()
    keep = [
        "candidate_id",
        "expression",
        "source_fields",
        "horizon",
        "decision",
        "reject_reasons",
        "raw_validation_2025H1_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag0",
        "raw_may_2026_stress_ann_10bps_lag0",
        "residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0",
        "residual_funding_may_2026_stress_ann_10bps_lag0",
    ]
    return penetrating.merge(score[keep], left_on="base_candidate_id", right_on="candidate_id", how="left", suffixes=("", "_base")).drop(columns=["candidate_id"], errors="ignore")


def rank_deciles(score: pd.DataFrame) -> pd.DataFrame:
    out = score.copy()
    recent = pd.to_numeric(out["raw_recent_2025H2_2026Apr_ann_10bps_lag0"], errors="coerce")
    out["recent_rank_desc"] = recent.rank(method="first", ascending=False)
    out["recent_decile"] = np.ceil(out["recent_rank_desc"] / max(len(out) / 10.0, 1.0)).astype(int).clip(1, 10)
    rows = []
    for decile, part in out.groupby("recent_decile", observed=True):
        rows.append(
            {
                "recent_decile": int(decile),
                "count": int(len(part)),
                "raw_recent_mean": float(pd.to_numeric(part["raw_recent_2025H2_2026Apr_ann_10bps_lag0"], errors="coerce").mean()),
                "post_may_positive_count": int(part["post_may_positive"].sum()),
                "pre_may_core_gate_count": int(part["pre_may_core_gate"].sum()),
                "control_contaminated_count": int((~part["gate_controls_clean"]).sum()),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    auth_prev = json.loads(A7AG1_AUTH.read_text(encoding="utf-8"))
    if not auth_prev.get("authorizes_a7ag2_forensic"):
        raise RuntimeError("A7AG1 does not authorize A7AG2")

    score = pd.read_csv(A7AG1_DIR / "a7ag1_candidate_scoreboard.csv")
    controls = pd.read_csv(A7AG1_DIR / "a7ag1_control_scoreboard.csv")
    score = add_gates(score)

    gates = gate_summary(score)
    families = family_summary(score)
    rejects = reject_counts(score)
    controls_pen = control_penetration(score, controls)
    deciles = rank_deciles(score)
    shortlist = score[score["decision"].isin(["A7AG1_POST_MAY_RESEARCH_CLUE", "A7AG1_PRE_MAY_ONLY_CLUE"])].copy()

    pre_may_count = int(score["pre_may_core_gate"].sum())
    post_may_count = int(score["post_may_eligible_after_core"].sum())
    neg_control_count = int(controls["control_research_like"].astype(bool).sum())
    blockers = []
    if post_may_count == 0:
        blockers.append("no_post_may_eligible_after_core_gate")
    if neg_control_count > 0:
        blockers.append("negative_control_research_like_penetration")
    if pre_may_count > 0 and post_may_count == 0:
        blockers.append("pre_may_clue_fails_may_stress")

    decision = "HOLD_A7AG2_PRE_MAY_ONLY_AND_CONTROL_CONTAMINATION"
    if neg_control_count == 0 and pre_may_count > 0 and post_may_count == 0:
        decision = "HOLD_A7AG2_PRE_MAY_ONLY_NO_MAY_STRESS_SURVIVAL"
    elif neg_control_count == 0 and pre_may_count == 0:
        decision = "HOLD_A7AG2_NO_SIGNAL"

    auth = {
        "decision": decision,
        "blockers": blockers,
        "authorizes_a7ag_expanded_replay": False,
        "authorizes_aggtrades_interaction_expansion": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "suggested_next": "wait_for_core12_rem9_aggtrades_or_define_new_non_1h_objective_contract",
        "may_policy": "May remains post-selection stress only; no May ranking or symbol tuning",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "candidates": int(len(score)),
        "controls": int(len(controls)),
        "pre_may_core_gate_candidates": pre_may_count,
        "post_may_eligible_after_core_candidates": post_may_count,
        "negative_control_research_like": neg_control_count,
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    score.to_csv(OUT_DIR / "a7ag2_candidate_gate_audit.csv", index=False)
    gates.to_csv(OUT_DIR / "a7ag2_gate_summary.csv", index=False)
    families.to_csv(OUT_DIR / "a7ag2_family_gate_summary.csv", index=False)
    rejects.to_csv(OUT_DIR / "a7ag2_reject_reason_counts.csv", index=False)
    controls_pen.to_csv(OUT_DIR / "a7ag2_negative_control_penetration.csv", index=False)
    deciles.to_csv(OUT_DIR / "a7ag2_rank_decile_may_alignment.csv", index=False)
    shortlist.to_csv(OUT_DIR / "a7ag2_shortlist_forensic.csv", index=False)
    write_json(OUT_DIR / "a7ag2_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ag2_manifest.json", manifest)

    cols = [
        "candidate_id",
        "family",
        "expression",
        "horizon",
        "raw_validation_2025H1_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_20bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag1",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag2",
        "raw_may_2026_stress_ann_10bps_lag0",
        "residual_funding_recent_2025H2_2026Apr_ann_10bps_lag0",
        "residual_funding_may_2026_stress_ann_10bps_lag0",
        "control_research_like_count",
        "decision",
        "reject_reasons",
    ]
    report = f"""# CRYPTO A7AG-2 aggTrades Interaction Failure Forensic

Generated: {now}

## Decision

```text
{decision}
```

This stage uses only A7AG-1 artifacts. It runs no new replay and no search.

## Summary

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Gate Summary

{md_table(gates)}

## Family Gate Summary

{md_table(families)}

## Reject Reasons

{md_table(rejects)}

## Shortlist Forensic

{md_table(shortlist[cols] if not shortlist.empty else shortlist)}

## Negative Control Penetration

{md_table(controls_pen)}

## Recent-Rank Decile vs May Alignment

{md_table(deciles)}

## Required Next Action

- Do not expand A7AG core3 aggTrades interaction replay.
- Do not promote the pre-May clue; it fails May stress.
- Do not use H2 flow x crowding until sign-flip control contamination is resolved.
- Next valid work is either core12 rem9 aggTrades source completion audit or a new non-1h objective/horizon contract.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
