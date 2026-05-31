from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff55r1_supplemental_queue_feasibility"
REPORT = REPO / "reports" / "CRYPTO_A7FF55R1_SUPPLEMENTAL_QUEUE_FEASIBILITY_20260531.md"
FORMULA_INDEX = REPO / "runtime" / "a7ff_version_20260530" / "a7ff_v20260530_formula_index.csv"
A7FF55R = REPO / "runtime" / "a7ff55r_selector_field_family_repair_contract" / "a7ff55r_manifest.json"
QUOTA = REPO / "runtime" / "a7ff55r_selector_field_family_repair_contract" / "a7ff55r_supplemental_family_quota.csv"


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


def family_mask(df: pd.DataFrame, family: str) -> pd.Series:
    cols = [c for c in ["semantic_pair", "primary_semantic", "secondary_semantic", "primary_field", "secondary_field"] if c in df.columns]
    mask = pd.Series(False, index=df.index)
    for col in cols:
        mask = mask | df[col].astype(str).str.contains(family, regex=False, na=False)
    return mask


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    m55r = read_json(A7FF55R)
    if m55r.get("decision") != "PASS_A7FF55R_SELECTOR_FIELD_FAMILY_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH":
        raise SystemExit(f"A7FF-55R is not ready: {m55r.get('decision')}")
    formulas = pd.read_csv(FORMULA_INDEX)
    quota = pd.read_csv(QUOTA)

    rows = []
    for _, q in quota.iterrows():
        family = str(q["field_family"])
        sub = formulas[family_mask(formulas, family)]
        mat = sub[sub["in_materialization_queue"].astype(str).str.lower().eq("true")] if not sub.empty else sub
        company = sub[sub["in_company_numeric_wave_queue"].astype(str).str.lower().eq("true")] if not sub.empty else sub
        rows.append(
            {
                "field_family": family,
                "required_min_primary_candidates": int(q["min_primary_candidates"]),
                "formula_count": int(len(sub)),
                "materialization_queue_count": int(len(mat)),
                "company_wave_queue_count": int(len(company)),
                "semantic_pair_count": int(sub["semantic_pair"].nunique()) if not sub.empty else 0,
                "motif_count": int(sub["motif"].nunique()) if not sub.empty else 0,
                "feasible_for_supplemental_numeric": bool(len(sub) >= int(q["min_primary_candidates"]) and int(q["min_primary_candidates"]) > 0),
                "feasible_for_existing_materialized_numeric": bool(len(mat) >= int(q["min_primary_candidates"]) and int(q["min_primary_candidates"]) > 0),
            }
        )
    feasibility = pd.DataFrame(rows)
    feasibility.to_csv(RUNTIME / "a7ff55r1_family_feasibility.csv", index=False)

    family_motif = (
        formulas.groupby(["semantic_pair", "motif"], dropna=False)
        .agg(
            formula_count=("blueprint_id", "count"),
            materialization_count=("in_materialization_queue", lambda x: int(x.astype(str).str.lower().eq("true").sum())),
            company_wave_count=("in_company_numeric_wave_queue", lambda x: int(x.astype(str).str.lower().eq("true").sum())),
        )
        .reset_index()
        .sort_values(["company_wave_count", "materialization_count", "formula_count"], ascending=False)
    )
    family_motif.to_csv(RUNTIME / "a7ff55r1_atlas_family_motif_availability.csv", index=False)

    blockers = []
    for _, row in feasibility.iterrows():
        if row["required_min_primary_candidates"] <= 0:
            continue
        if row["formula_count"] == 0:
            blockers.append(f"{row['field_family']}_absent_from_formula_index")
        elif row["materialization_queue_count"] == 0:
            blockers.append(f"{row['field_family']}_absent_from_materialization_queue")
        elif row["materialization_queue_count"] < row["required_min_primary_candidates"]:
            blockers.append(f"{row['field_family']}_materialization_count_below_quota")
    decision = "PASS_A7FF55R1_SUPPLEMENTAL_QUEUE_FEASIBLE_NO_EXECUTION_AUTH" if not blockers else "HOLD_A7FF55R1_SUPPLEMENTAL_QUEUE_ATLAS_COVERAGE_FAIL"
    next_allowed = "A7FF-55R2 supplemental numeric execution contract" if not blockers else "A7FF-55R2 atlas field-family generation repair"
    manifest = {
        "stage": "A7FF-55R1",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "formula_index_rows": int(len(formulas)),
        "quota_rows": int(len(quota)),
        "families_required_positive_quota": int((quota["min_primary_candidates"] > 0).sum()),
        "families_feasible_from_formula_index": int(feasibility["feasible_for_supplemental_numeric"].sum()),
        "families_feasible_from_materialized_queue": int(feasibility["feasible_for_existing_materialized_numeric"].sum()),
        "next_allowed": next_allowed,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff55r1_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-55R1 SUPPLEMENTAL QUEUE FEASIBILITY

Generated: {manifest["generated_at"]}

## Decision

`{manifest["decision"]}`

A7FF-55R1 checks whether the current A7FF v20260530 formula atlas can satisfy the A7FF-55R supplemental family quotas. It does not run numeric replay or search.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Family Feasibility

{md_table(feasibility, 40)}

## Top Atlas Family / Motif Availability

{md_table(family_motif, 80)}

## Boundary

```text
feasibility audit executed: true
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
