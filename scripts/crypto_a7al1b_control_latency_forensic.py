from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
IN_DIR = REPO / "runtime" / "a7al1_field_family_neutralized_baseline"
OUT_DIR = REPO / "runtime" / "a7al1b_control_latency_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7AL1B_CONTROL_LATENCY_FORENSIC_20260527.md"


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


def recommendation(row: pd.Series) -> tuple[str, str]:
    signal = str(row["signal_name"])
    family = str(row["field_family"])
    blockers = str(row.get("blocking_controls", ""))
    if "wrong_lag_future_24h" in blockers:
        return (
            "BLOCK_DIRECT_ALPHA_RANK",
            "future wrong-lag control dominates; keep only for diagnostics until a matched-control dominance gate is implemented",
        )
    if "wrong_lag_stale_168h" in blockers:
        return (
            "REGIME_OR_STATE_ONLY",
            "stale wrong-lag control is comparable; use as slow state/neutralization input, not as standalone alpha rank",
        )
    if str(row.get("diagnostic_decision", "")) == "FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC":
        return (
            "ALLOW_FORENSIC_ONLY",
            "diagnostic structure exists but must be reviewed with controls before formula search",
        )
    return (
        "DO_NOT_PROMOTE",
        "no stable neutralized field-family structure",
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((IN_DIR / "a7al1_manifest.json").read_text(encoding="utf-8"))
    decisions = pd.read_csv(IN_DIR / "a7al1_signal_decisions.csv")
    controls = pd.read_csv(IN_DIR / "a7al1_negative_control_audit.csv")
    metrics = pd.read_csv(IN_DIR / "a7al1_field_family_metrics.csv")

    blockers = controls[controls["control_flag"].eq("CONTROL_TOO_STRONG")].copy()
    blocker_summary = (
        blockers.groupby(["field_family", "signal_name"], dropna=False)
        .agg(
            blocking_controls=("control", lambda s: "|".join(sorted(set(map(str, s))))),
            max_abs_vs_original_ratio=("abs_vs_original_ratio", "max"),
            max_abs_control_spread=("validation_mean_spread_24h", lambda s: float(np.nanmax(np.abs(s)))),
            min_valid_row_share=("valid_row_share", "min"),
        )
        .reset_index()
    )
    gate = decisions.merge(blocker_summary, on=["field_family", "signal_name"], how="left")
    gate["blocking_controls"] = gate["blocking_controls"].fillna("")
    recs = gate.apply(recommendation, axis=1, result_type="expand")
    gate["a7al2_policy"] = recs[0]
    gate["policy_reason"] = recs[1]

    family_summary = (
        gate.groupby("field_family", dropna=False)
        .agg(
            signals=("signal_name", "count"),
            diagnostic_pass_signals=("diagnostic_decision", lambda s: int((s == "FIELD_FAMILY_STRUCTURE_FOUND_DIAGNOSTIC").sum())),
            control_blocked_signals=("blocking_controls", lambda s: int((s.astype(str) != "").sum())),
            recommended_direct_alpha=("a7al2_policy", lambda s: int((s == "ALLOW_FORENSIC_ONLY").sum())),
            regime_or_state_only=("a7al2_policy", lambda s: int((s == "REGIME_OR_STATE_ONLY").sum())),
            blocked_direct_rank=("a7al2_policy", lambda s: int((s == "BLOCK_DIRECT_ALPHA_RANK").sum())),
        )
        .reset_index()
    )

    top_metrics = metrics[
        metrics["split"].isin(["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"])
        & metrics["universe"].eq("U0_strict_full_history")
        & metrics["neutralization_mode"].isin(["global", "latent_state_neutral"])
    ].copy()

    negative_control_clean = blockers.empty
    decision = (
        "PASS_A7AL1B_CONTROL_LATENCY_CLEAN"
        if negative_control_clean
        else "HOLD_A7AL1B_WRONG_LAG_CONTAMINATION_CONFIRMED"
    )
    out_manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_a7al1_decision": manifest.get("decision"),
        "diagnostic_field_families": int(manifest.get("passed_field_family_count", 0)),
        "control_blocked_signal_count": int(len(blocker_summary)),
        "blocking_controls": sorted(blockers["control"].dropna().astype(str).unique().tolist()),
        "executes_formula_generation": False,
        "executes_formula_search": False,
        "authorizes_a7al2_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "recommended_next": "repair A7AL-2 contract to require matched-control dominance; keep slow level fields as regime/state inputs only",
    }

    blocker_summary.to_csv(OUT_DIR / "a7al1b_control_blocker_summary.csv", index=False)
    gate.to_csv(OUT_DIR / "a7al1b_signal_policy_recommendations.csv", index=False)
    family_summary.to_csv(OUT_DIR / "a7al1b_family_policy_summary.csv", index=False)
    top_metrics.to_csv(OUT_DIR / "a7al1b_relevant_metric_extract.csv", index=False)
    write_json(OUT_DIR / "a7al1b_manifest.json", out_manifest)

    report = f"""# CRYPTO A7AL-1B Control / Latency Forensic

Generated: {out_manifest["generated_at"]}

## Decision

```text
{decision}
```

This audit does not run formula generation or replay. It interprets A7AL-1 negative controls before any A7AL-2 search contract.

## Manifest

```json
{json.dumps(out_manifest, indent=2, sort_keys=True)}
```

## Control Blockers

{md_table(blocker_summary, 80)}

## Signal Policy Recommendations

{md_table(gate[["signal_name", "field_family", "diagnostic_decision", "blocking_controls", "a7al2_policy", "policy_reason"]], 120)}

## Family Policy Summary

{md_table(family_summary, 80)}

## Boundary

```text
AUTHORIZED:
  A7AL-2 contract repair only.

NOT AUTHORIZED:
  A7AL-2 formula search execution
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(out_manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
