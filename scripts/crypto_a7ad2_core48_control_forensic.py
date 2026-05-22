from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
A7AD1_DIR = ROOT / "runtime" / "a7ad1_core48_controlled_replay_smoke"
OUT_DIR = ROOT / "runtime" / "a7ad2_core48_control_forensic"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AD2_CORE48_CONTROL_FORENSIC_20260522.md"


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


def reason_summary(scoreboard: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in scoreboard.iterrows():
        reasons = [r for r in str(row.get("reject_reasons", "")).split(";") if r]
        if not reasons:
            reasons = ["none"]
        for reason in reasons:
            rows.append({"family": row["family"], "reason": reason, "candidate_id": row["candidate_id"]})
    out = pd.DataFrame(rows)
    return out.groupby(["family", "reason"], observed=True)["candidate_id"].nunique().reset_index(name="candidate_count")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    scoreboard = pd.read_csv(A7AD1_DIR / "a7ad1_candidate_scoreboard.csv")
    controls = pd.read_csv(A7AD1_DIR / "a7ad1_control_scoreboard.csv")
    dominance = pd.read_csv(A7AD1_DIR / "a7ad1_negative_control_dominance.csv")

    controls["control_research_like"] = controls["control_research_like"].astype(str).str.lower().eq("true")
    research_like_controls = controls[controls["control_research_like"]].copy()
    contamination = (
        controls.groupby(["family", "control_mode"], observed=True)
        .agg(control_count=("control_id", "count"), research_like_count=("control_research_like", "sum"))
        .reset_index()
    )
    contamination["research_like_rate"] = contamination["research_like_count"] / contamination["control_count"].clip(lower=1)

    reason_counts = reason_summary(scoreboard)
    pair_cols = [
        "control_id",
        "base_candidate_id",
        "family",
        "control_mode",
        "raw_validation_2025H1_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_ann_10bps_lag0",
        "raw_recent_2025H2_2026Apr_sharpe_10bps_lag0",
    ]
    top_controls = research_like_controls.sort_values("raw_recent_2025H2_2026Apr_ann_10bps_lag0", ascending=False)[pair_cols]

    merged = dominance.merge(
        scoreboard[
            [
                "candidate_id",
                "expression",
                "horizon",
                "raw_validation_2025H1_ann_10bps_lag0",
                "raw_recent_2025H2_2026Apr_ann_10bps_lag0",
                "raw_recent_2025H2_2026Apr_ann_20bps_lag0",
                "raw_recent_2025H2_2026Apr_ann_10bps_lag1",
                "reject_reasons",
            ]
        ],
        on="candidate_id",
        how="left",
    )
    pair_audit = merged.sort_values(["control_research_like_count", "candidate_recent_ann_10bps_lag0"], ascending=False)

    total_candidates = int(len(scoreboard))
    clue_count = int(scoreboard["decision"].eq("A7AD1_RESEARCH_CLUE_PRE_MAY_ONLY").sum())
    control_like_count = int(research_like_controls.shape[0])
    families_with_control_like = sorted(research_like_controls["family"].unique().tolist())
    wrong_lag_like = int(research_like_controls["control_mode"].eq("wrong_lag_stale_24h").sum())
    sign_flip_like = int(research_like_controls["control_mode"].eq("sign_flip").sum())

    decision = "HOLD_A7AD2_CONTROL_CONTAMINATION_AND_NO_CLUE_CONFIRMED"
    auth = {
        "decision": decision,
        "authorizes_a7ad3_contract_revision": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "recommended_next": "A7AD3 tighten control dominance and redesign candidate families before any new replay",
    }
    manifest = {
        "generated_at": now,
        "decision": decision,
        "total_candidates": total_candidates,
        "control_clean_research_clues": clue_count,
        "research_like_controls": control_like_count,
        "wrong_lag_research_like_controls": wrong_lag_like,
        "sign_flip_research_like_controls": sign_flip_like,
        "families_with_control_like": families_with_control_like,
        "executes_replay": False,
        "executes_search": False,
        "report": str(REPORT_PATH),
        "output_dir": str(OUT_DIR),
    }

    contamination.to_csv(OUT_DIR / "a7ad2_control_contamination_by_family.csv", index=False)
    top_controls.to_csv(OUT_DIR / "a7ad2_top_research_like_controls.csv", index=False)
    reason_counts.to_csv(OUT_DIR / "a7ad2_reject_reason_summary.csv", index=False)
    pair_audit.to_csv(OUT_DIR / "a7ad2_candidate_vs_control_pair_audit.csv", index=False)
    write_json(OUT_DIR / "a7ad2_authorization_matrix.json", auth)
    write_json(OUT_DIR / "a7ad2_manifest.json", manifest)

    report = f"""# CRYPTO A7AD-2 Core48 Control Forensic

Generated: {now}

## Decision

```text
{decision}
```

This stage does not run replay and does not run search. It reviews A7AD-1 outputs.

## Summary

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Authorization

```json
{json.dumps(auth, indent=2, sort_keys=True)}
```

## Control Contamination By Family

{md_table(contamination)}

## Reject Reason Summary

{md_table(reason_counts)}

## Top Research-Like Controls

{md_table(top_controls, 30)}

## Candidate vs Control Pair Audit

{md_table(pair_audit, 30)}

## Interpretation

- A7AD-1 produced no control-clean pre-May research clue.
- `wrong_lag_stale_24h` controls account for most research-like controls.
- `sign_flip` controls also pass in funding/liquidity-volatility families, which means orientation is unstable for those motifs.
- Current core48 candidate families should not be expanded directly.
- Next valid work is A7AD-3 contract revision: stricter negative-control dominance, lower reliance on stale-sensitive motifs, and smaller family-specific smoke before any broader replay.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
