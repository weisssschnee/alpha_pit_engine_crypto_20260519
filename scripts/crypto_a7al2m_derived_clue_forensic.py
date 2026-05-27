from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE_TAG = "20260527"
IN_DIR = REPO / "runtime" / "a7al2l_fast_derived_replay_preflight"
OUT_DIR = REPO / "runtime" / "a7al2m_derived_clue_forensic"
REPORT = REPO / "reports" / f"CRYPTO_A7AL2M_DERIVED_CLUE_FORENSIC_{DATE_TAG}.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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


def sign_value(value: float) -> int:
    if not np.isfinite(value) or abs(value) < 1e-12:
        return 0
    return int(np.sign(value))


def classify(row: pd.Series) -> str:
    premay_values = [
        float(row["original_validation_spread"]),
        float(row["original_test_spread"]),
        float(row["original_recent_spread"]),
    ]
    premay_signs = {sign_value(x) for x in premay_values if sign_value(x) != 0}
    premay_sign = list(premay_signs)[0] if len(premay_signs) == 1 else 0
    may_sign = sign_value(float(row["original_may_stress_spread"]))
    recent = abs(float(row["original_recent_spread"]))
    lag = abs(float(row["one_bar_lag_recent_spread"]))
    lag_retention = lag / recent if recent > 0 else np.nan
    control = float(row["control_dominance_ratio_premay_max"])

    if premay_sign and may_sign and premay_sign != may_sign:
        return "A7AL2M_STRESS_DIVERGENT_CLUE"
    if np.isfinite(control) and control >= 1.10:
        return "A7AL2M_CONTROL_MARGIN_THIN_CLUE"
    if np.isfinite(lag_retention) and lag_retention < 0.50:
        return "A7AL2M_LAG_MARGIN_THIN_CLUE"
    return "A7AL2M_DEEP_AUDIT_CANDIDATE"


def add_quality_columns(clues: pd.DataFrame) -> pd.DataFrame:
    out = clues.copy()
    out["premay_mean_spread"] = out[
        ["original_validation_spread", "original_test_spread", "original_recent_spread"]
    ].astype(float).mean(axis=1)
    out["premay_min_abs_spread"] = out[
        ["original_validation_spread", "original_test_spread", "original_recent_spread"]
    ].astype(float).abs().min(axis=1)
    out["lag_recent_retention"] = out["one_bar_lag_recent_spread"].astype(float).abs() / out["original_recent_spread"].astype(float).abs()
    out["may_same_sign_as_premay"] = np.sign(out["original_may_stress_spread"].astype(float)) == np.sign(out["premay_mean_spread"].astype(float))
    out["quality_label"] = out.apply(classify, axis=1)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    al2l_manifest = read_json(IN_DIR / "a7al2l_fast_manifest.json")
    decisions = pd.read_csv(IN_DIR / "a7al2l_fast_candidate_decisions.csv")
    metrics = pd.read_csv(IN_DIR / "a7al2l_fast_candidate_variant_metrics.csv")
    clues = decisions[decisions["decision"].eq("A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE")].copy()
    clues = add_quality_columns(clues)

    quality_summary = clues["quality_label"].value_counts().rename_axis("quality_label").reset_index(name="count")
    cell_summary = clues.groupby(["cell", "family", "field_families"], dropna=False).size().reset_index(name="count")
    split_quality = (
        metrics[metrics["candidate_id"].isin(clues["candidate_id"])]
        .pivot_table(index=["candidate_id", "variant"], columns="split", values="mean_spread_24h", aggfunc="first")
        .reset_index()
    )

    deep_candidates = int(clues["quality_label"].eq("A7AL2M_DEEP_AUDIT_CANDIDATE").sum())
    stress_divergent = int(clues["quality_label"].eq("A7AL2M_STRESS_DIVERGENT_CLUE").sum())
    field_family_count = int(clues["field_families"].nunique())
    cell_count = int(clues["cell"].nunique())
    blockers: list[str] = []
    warnings: list[str] = []
    if len(clues) == 0:
        blockers.append("no_a7al2l_clues")
    if deep_candidates == 0:
        warnings.append("no_high_quality_deep_audit_candidate")
    if stress_divergent:
        warnings.append("stress_divergent_clues_present")
    if field_family_count < 4:
        warnings.append("field_family_diversity_below_4")

    decision = "PASS_A7AL2M_DERIVED_CLUE_POOL_READY_FOR_DEEP_AUDIT" if len(clues) > 0 and not blockers else "HOLD_A7AL2M_NO_DERIVED_CLUE_POOL"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_a7al2l_decision": al2l_manifest.get("decision"),
        "clue_count": int(len(clues)),
        "deep_audit_candidate_count": deep_candidates,
        "stress_divergent_clue_count": stress_divergent,
        "cell_count": cell_count,
        "field_family_count": field_family_count,
        "quality_counts": {str(r["quality_label"]): int(r["count"]) for _, r in quality_summary.iterrows()},
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_a7al2n_deep_audit": len(clues) > 0 and not blockers,
        "authorizes_formula_search_execution": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    clues.to_csv(OUT_DIR / "a7al2m_clue_shortlist.csv", index=False)
    quality_summary.to_csv(OUT_DIR / "a7al2m_quality_summary.csv", index=False)
    cell_summary.to_csv(OUT_DIR / "a7al2m_cell_family_summary.csv", index=False)
    split_quality.to_csv(OUT_DIR / "a7al2m_variant_split_metrics.csv", index=False)
    write_json(OUT_DIR / "a7al2m_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2M Derived Clue Forensic

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This stage classifies A7AL-2L replay-preflight clues. It does not run new replay and does not authorize formula search execution or alpha proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Quality Summary

{md_table(quality_summary, 40)}

## Cell / Family Summary

{md_table(cell_summary, 80)}

## Clue Shortlist

{md_table(clues[["candidate_id", "cell", "family", "field_families", "quality_label", "premay_mean_spread", "original_may_stress_spread", "lag_recent_retention", "control_dominance_ratio_premay_max"]], 80)}

## Boundary

```text
Deep audit candidate:
  clean enough for A7AL-2N forensic only.

Stress divergent clue:
  may still be useful as a regime clue, but not a promotion candidate.

Not authorized:
  alpha proof
  shadow / paper / live
  large formula search
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
