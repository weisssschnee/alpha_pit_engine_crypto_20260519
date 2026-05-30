from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff_version_20260530"
REPORT = REPO / "reports" / "CRYPTO_A7FF_VERSION_20260530_A7FFR_TO_A7FF24R.md"

A7FFR1 = REPO / "runtime" / "a7ffr1_field_ontology_v3" / "a7ffr1_manifest.json"
A7FFR5 = REPO / "runtime" / "a7ffr5_response_backed_promotion_redesign" / "a7ffr5_manifest.json"
A7FF23R = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_manifest.json"
A7FF24R = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_manifest.json"
BLUEPRINT_POOL = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_blueprint_pool.csv"
MATERIALIZATION_QUEUE = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_materialization_queue.csv"
COMPANY_QUEUE = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_company_numeric_wave_queue.csv"
SHARD_PLAN = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_company_shard_plan.csv"
SEED_POLICY = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_seed_policy.csv"
PAIR_POLICY = REPO / "runtime" / "a7ff23r_derived_factor_expansion_contract" / "a7ff23r_pair_policy.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def git_text(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {exc}"


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def file_record(path: Path, purpose: str, finality: str) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "size_bytes": None,
            "modified_time": None,
            "purpose": purpose,
            "finality": finality,
        }
    stat = path.stat()
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_time": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        "purpose": purpose,
        "finality": finality,
    }


def build_formula_index(pool: pd.DataFrame, mat: pd.DataFrame, company: pd.DataFrame) -> pd.DataFrame:
    mat_ids = set(mat["blueprint_id"].astype(str)) if not mat.empty else set()
    company_cols = ["blueprint_id", "company_shard"] if "company_shard" in company.columns else ["blueprint_id"]
    company_membership = company[company_cols].copy() if not company.empty else pd.DataFrame(columns=company_cols)
    formula = pool.copy()
    formula["in_materialization_queue"] = formula["blueprint_id"].astype(str).isin(mat_ids)
    formula = formula.merge(company_membership, on="blueprint_id", how="left")
    formula["in_company_numeric_wave_queue"] = formula["company_shard"].notna()
    ordered = [
        "blueprint_id",
        "level",
        "candidate_role",
        "generation_priority",
        "semantic_pair",
        "motif",
        "primary_field",
        "secondary_field",
        "primary_semantic",
        "secondary_semantic",
        "primary_route",
        "secondary_route",
        "primary_transform",
        "secondary_transform",
        "modifier_guard_required",
        "skeleton_key",
        "production_key",
        "in_materialization_queue",
        "in_company_numeric_wave_queue",
        "company_shard",
        "expression",
    ]
    return formula[[col for col in ordered if col in formula.columns]]


def build_derived_field_catalog(formula: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for side in ["primary", "secondary"]:
        field_col = f"{side}_field"
        semantic_col = f"{side}_semantic"
        route_col = f"{side}_route"
        transform_col = f"{side}_transform"
        if field_col not in formula.columns:
            continue
        subset = formula[formula[field_col].fillna("").astype(str).ne("")].copy()
        if subset.empty:
            continue
        grouped = (
            subset.groupby([field_col, semantic_col, route_col, transform_col], dropna=False)
            .agg(
                formula_count=("blueprint_id", "count"),
                materialization_count=("in_materialization_queue", "sum"),
                company_wave_count=("in_company_numeric_wave_queue", "sum"),
                levels=("level", lambda s: ";".join(sorted(set(map(str, s))))),
                motifs=("motif", lambda s: ";".join(sorted(set(map(str, s))))),
                semantic_pairs=("semantic_pair", lambda s: ";".join(sorted(set(map(str, s))))),
            )
            .reset_index()
        )
        grouped = grouped.rename(
            columns={
                field_col: "base_field",
                semantic_col: "semantic_type",
                route_col: "seed_route",
                transform_col: "transform_name",
            }
        )
        grouped["side"] = side
        rows.append(grouped)
    if not rows:
        return pd.DataFrame()
    catalog = pd.concat(rows, ignore_index=True)
    return catalog.sort_values(["formula_count", "base_field", "transform_name"], ascending=[False, True, True])


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    r1 = read_json(A7FFR1)
    r5 = read_json(A7FFR5)
    r23 = read_json(A7FF23R)
    r24 = read_json(A7FF24R)
    pool = pd.read_csv(BLUEPRINT_POOL)
    mat = pd.read_csv(MATERIALIZATION_QUEUE)
    company = pd.read_csv(COMPANY_QUEUE)
    shard_plan = pd.read_csv(SHARD_PLAN)
    seeds = pd.read_csv(SEED_POLICY)
    pairs = pd.read_csv(PAIR_POLICY)

    formula = build_formula_index(pool, mat, company)
    derived = build_derived_field_catalog(formula)
    formula_summary = (
        formula.groupby(["level", "semantic_pair", "motif"], dropna=False)
        .agg(
            formula_count=("blueprint_id", "count"),
            materialization_count=("in_materialization_queue", "sum"),
            company_wave_count=("in_company_numeric_wave_queue", "sum"),
            skeleton_count=("skeleton_key", "nunique"),
            production_key_count=("production_key", "nunique"),
        )
        .reset_index()
        .sort_values("formula_count", ascending=False)
    )
    base_usage = (
        derived.groupby(["base_field", "semantic_type", "seed_route"], dropna=False)
        .agg(
            transform_count=("transform_name", "nunique"),
            formula_count=("formula_count", "sum"),
            materialization_count=("materialization_count", "sum"),
            company_wave_count=("company_wave_count", "sum"),
        )
        .reset_index()
        .sort_values("formula_count", ascending=False)
    )
    queue_summary = pd.DataFrame(
        [
            {"queue": "blueprint_pool", "rows": len(pool), "file": str(BLUEPRINT_POOL)},
            {"queue": "materialization_queue", "rows": len(mat), "file": str(MATERIALIZATION_QUEUE)},
            {"queue": "company_numeric_wave_queue", "rows": len(company), "file": str(COMPANY_QUEUE)},
        ]
    )
    output_manifest = pd.DataFrame(
        [
            file_record(REPORT, "canonical human-readable version file", "final"),
            file_record(RUNTIME / "a7ff_v20260530_formula_index.csv", "complete formula blueprint index", "final_index"),
            file_record(RUNTIME / "a7ff_v20260530_derived_field_catalog.csv", "base field and transform catalog", "final_index"),
            file_record(RUNTIME / "a7ff_v20260530_formula_family_summary.csv", "formula level/semantic/motif summary", "summary"),
            file_record(RUNTIME / "a7ff_v20260530_base_field_usage.csv", "base field usage summary", "summary"),
            file_record(RUNTIME / "a7ff_v20260530_queue_summary.csv", "queue counts and paths", "summary"),
            file_record(RUNTIME / "a7ff_v20260530_manifest.json", "version manifest", "final"),
        ]
    )

    formula.to_csv(RUNTIME / "a7ff_v20260530_formula_index.csv", index=False)
    derived.to_csv(RUNTIME / "a7ff_v20260530_derived_field_catalog.csv", index=False)
    formula_summary.to_csv(RUNTIME / "a7ff_v20260530_formula_family_summary.csv", index=False)
    base_usage.to_csv(RUNTIME / "a7ff_v20260530_base_field_usage.csv", index=False)
    queue_summary.to_csv(RUNTIME / "a7ff_v20260530_queue_summary.csv", index=False)
    output_manifest.to_csv(RUNTIME / "a7ff_v20260530_output_manifest.csv", index=False)

    head = git_text("rev-parse", "HEAD")
    origin = git_text("rev-parse", "origin/main")
    status = git_text("status", "--short")
    source_artifacts_uploaded = head == origin
    worktree_clean = status == ""
    manifest = {
        "stage": "A7FF-VERSION-20260530",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF_VERSION_FILE_BUILT",
        "version_id": "CRYPTO_A7FF_V20260530_R_TO_24R",
        "source_commit_head_at_generation": head,
        "origin_main_at_generation": origin,
        "source_artifacts_uploaded_at_generation": source_artifacts_uploaded,
        "version_file_pending_commit_at_generation": not worktree_clean,
        "worktree_status_at_generation": status,
        "blueprint_count": int(len(pool)),
        "formula_index_rows": int(len(formula)),
        "derived_field_catalog_rows": int(len(derived)),
        "materialization_queue_count": int(len(mat)),
        "company_wave_queue_count": int(len(company)),
        "company_shard_count": int(shard_plan["company_shard"].nunique()),
        "semantic_pair_count": int(formula["semantic_pair"].nunique()),
        "motif_count": int(formula["motif"].nunique()),
        "r1_decision": r1.get("decision"),
        "r5_decision": r5.get("decision"),
        "a7ff23r_decision": r23.get("decision"),
        "a7ff24r_decision": r24.get("decision"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff_v20260530_manifest.json", manifest)

    sample_cols = [
        "blueprint_id",
        "level",
        "semantic_pair",
        "motif",
        "primary_field",
        "secondary_field",
        "primary_transform",
        "secondary_transform",
        "in_materialization_queue",
        "in_company_numeric_wave_queue",
        "expression",
    ]
    sample = formula[sample_cols].head(30)
    report = f"""# CRYPTO A7FF VERSION 20260530: A7FF-R TO A7FF-24R

Generated: {manifest["generated_at"]}

## Version Decision

`{manifest["decision"]}`

This is the canonical version file for the A7FF-R -> A7FF-23R -> A7FF-24R line. Future A7FF work should use this format: one human version file under `reports/`, plus machine-readable indexes under a matching `runtime/a7ff_version_*` directory.

## Upload / Git Status At Generation

```json
{json.dumps({k: manifest[k] for k in ["source_commit_head_at_generation", "origin_main_at_generation", "source_artifacts_uploaded_at_generation", "version_file_pending_commit_at_generation", "worktree_status_at_generation"]}, indent=2, sort_keys=True)}
```

Note: this version file itself is committed after generation. `source_artifacts_uploaded_at_generation` refers to the source artifacts summarized here, not to this newly generated version file.

## Scope

Included stages:

```text
A7FF-R0/R1/R2/R3/R4/R5
A7FF-23R
A7FF-24R
```

Excluded from this version:

```text
numeric probe execution
replay execution
formula search
large search
alpha proof
shadow / paper / live
```

## Key Stage Decisions

| stage | decision |
|---|---|
| A7FF-R1 | `{r1.get("decision")}` |
| A7FF-R5 | `{r5.get("decision")}` |
| A7FF-23R | `{r23.get("decision")}` |
| A7FF-24R | `{r24.get("decision")}` |

## Main Counts

```json
{json.dumps({k: manifest[k] for k in ["blueprint_count", "formula_index_rows", "derived_field_catalog_rows", "materialization_queue_count", "company_wave_queue_count", "company_shard_count", "semantic_pair_count", "motif_count"]}, indent=2, sort_keys=True)}
```

## Complete Formula Index

The complete formula list is not embedded inline because it has `{len(formula)}` rows. It is stored here:

```text
{RUNTIME / "a7ff_v20260530_formula_index.csv"}
```

Columns include:

```text
blueprint_id
level
candidate_role
generation_priority
semantic_pair
motif
primary_field / secondary_field
primary_transform / secondary_transform
skeleton_key
production_key
queue membership
expression
```

## Formula Samples

{md_table(sample, 30)}

## Formula Family Summary

{md_table(formula_summary, 80)}

## Derived Field Catalog

The full derived field and transform catalog is stored here:

```text
{RUNTIME / "a7ff_v20260530_derived_field_catalog.csv"}
```

Top base fields:

{md_table(base_usage, 60)}

## Queue Summary

{md_table(queue_summary)}

## Company Shard Plan

{md_table(shard_plan)}

## Version Classification Standard For Future Work

Each future version must include:

```text
1. version_id
2. source commits and upload status
3. included stages and excluded stages
4. decisions and authorization boundaries
5. complete formula index path
6. derived field catalog path
7. queue membership and shard plan
8. selector / label / control policy
9. what is authorized next
10. what remains blocked
```

Required runtime files:

```text
a7ff_vYYYYMMDD_formula_index.csv
a7ff_vYYYYMMDD_derived_field_catalog.csv
a7ff_vYYYYMMDD_formula_family_summary.csv
a7ff_vYYYYMMDD_base_field_usage.csv
a7ff_vYYYYMMDD_queue_summary.csv
a7ff_vYYYYMMDD_output_manifest.csv
a7ff_vYYYYMMDD_manifest.json
```

## Authorization Boundary

```text
authorizes_search = false
authorizes_alpha_proof = false
authorizes_shadow_paper_live = false
next_allowed = company numeric execution adapter / A7FF-25R
```
"""
    REPORT.write_text(report, encoding="utf-8")

    # Recompute output manifest after report creation so size/mtime are present.
    output_manifest = pd.DataFrame(
        [
            file_record(REPORT, "canonical human-readable version file", "final"),
            file_record(RUNTIME / "a7ff_v20260530_formula_index.csv", "complete formula blueprint index", "final_index"),
            file_record(RUNTIME / "a7ff_v20260530_derived_field_catalog.csv", "base field and transform catalog", "final_index"),
            file_record(RUNTIME / "a7ff_v20260530_formula_family_summary.csv", "formula level/semantic/motif summary", "summary"),
            file_record(RUNTIME / "a7ff_v20260530_base_field_usage.csv", "base field usage summary", "summary"),
            file_record(RUNTIME / "a7ff_v20260530_queue_summary.csv", "queue counts and paths", "summary"),
            file_record(RUNTIME / "a7ff_v20260530_manifest.json", "version manifest", "final"),
        ]
    )
    output_manifest.to_csv(RUNTIME / "a7ff_v20260530_output_manifest.csv", index=False)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
