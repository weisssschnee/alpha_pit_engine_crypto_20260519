from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff25r0_company_queue_coverage"
REPORT = REPO / "reports" / "CRYPTO_A7FF25R0_COMPANY_QUEUE_COVERAGE_AUDIT_20260530.md"

A7FF_VERSION_MANIFEST = REPO / "runtime" / "a7ff_version_20260530" / "a7ff_v20260530_manifest.json"
A7FF24R_MANIFEST = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_manifest.json"
FORMULA_INDEX = REPO / "runtime" / "a7ff_version_20260530" / "a7ff_v20260530_formula_index.csv"
DERIVED_CATALOG = REPO / "runtime" / "a7ff_version_20260530" / "a7ff_v20260530_derived_field_catalog.csv"
MATERIALIZATION_QUEUE = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_materialization_queue.csv"
COMPANY_QUEUE = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_company_numeric_wave_queue.csv"
SHARD_PLAN = REPO / "runtime" / "a7ff24r_dry_generation_plan" / "a7ff24r_company_shard_plan.csv"


IMPORTANT_FIELD_TYPES = {
    "basis_premium_like",
    "funding_like",
    "positioning_like",
    "volatility_like",
    "price_like",
    "liquidity_like",
}


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


def add_membership(formula: pd.DataFrame, materialization: pd.DataFrame, company: pd.DataFrame) -> pd.DataFrame:
    mat_ids = set(materialization["blueprint_id"].astype(str))
    company_cols = ["blueprint_id", "company_shard"] if "company_shard" in company.columns else ["blueprint_id"]
    out = formula.copy()
    out["in_materialization_queue"] = out["blueprint_id"].astype(str).isin(mat_ids)
    out = out.drop(columns=["company_shard"], errors="ignore")
    out = out.merge(company[company_cols], on="blueprint_id", how="left")
    out["in_company_wave"] = out["company_shard"].notna()
    return out


def coverage_table(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    grouped = (
        df.groupby(group_cols, dropna=False)
        .agg(
            formula_count=("blueprint_id", "count"),
            materialization_count=("in_materialization_queue", "sum"),
            company_wave_count=("in_company_wave", "sum"),
            skeleton_count=("skeleton_key", "nunique"),
            production_key_count=("production_key", "nunique"),
        )
        .reset_index()
    )
    total_formula = max(1, int(df["blueprint_id"].count()))
    total_materialization = max(1, int(df["in_materialization_queue"].sum()))
    total_company = max(1, int(df["in_company_wave"].sum()))
    grouped["formula_share"] = grouped["formula_count"] / total_formula
    grouped["materialization_share"] = grouped["materialization_count"] / total_materialization
    grouped["company_wave_share"] = grouped["company_wave_count"] / total_company
    grouped["materialization_rate_from_formula"] = grouped["materialization_count"] / grouped["formula_count"].replace(0, pd.NA)
    grouped["company_rate_from_formula"] = grouped["company_wave_count"] / grouped["formula_count"].replace(0, pd.NA)
    return grouped.sort_values(["company_wave_count", "formula_count"], ascending=False)


def explode_base_fields(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for side in ["primary", "secondary"]:
        field_col = f"{side}_field"
        semantic_col = f"{side}_semantic"
        route_col = f"{side}_route"
        transform_col = f"{side}_transform"
        if field_col not in df.columns:
            continue
        subset = df[df[field_col].fillna("").astype(str).ne("")]
        for row in subset.itertuples(index=False):
            payload = {
                "base_field": getattr(row, field_col),
                "semantic_type": getattr(row, semantic_col, ""),
                "seed_route": getattr(row, route_col, ""),
                "transform": getattr(row, transform_col, ""),
                "side": side,
                "blueprint_id": row.blueprint_id,
                "level": row.level,
                "semantic_pair": row.semantic_pair,
                "motif": row.motif,
                "skeleton_key": row.skeleton_key,
                "production_key": row.production_key,
                "in_materialization_queue": row.in_materialization_queue,
                "in_company_wave": row.in_company_wave,
            }
            rows.append(payload)
    return pd.DataFrame(rows)


def dropoff_table(df: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    cov = coverage_table(df, group_cols)
    cov["materialization_dropoff"] = cov["formula_count"] - cov["materialization_count"]
    cov["company_dropoff"] = cov["formula_count"] - cov["company_wave_count"]
    cov["materialization_absent"] = cov["formula_count"].gt(0) & cov["materialization_count"].eq(0)
    cov["company_absent"] = cov["formula_count"].gt(0) & cov["company_wave_count"].eq(0)
    return cov.sort_values(["company_absent", "company_dropoff", "formula_count"], ascending=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    version = read_json(A7FF_VERSION_MANIFEST)
    a7ff24r = read_json(A7FF24R_MANIFEST)
    if not a7ff24r.get("authorizes_company_numeric_execution"):
        raise SystemExit(f"A7FF-24R does not authorize company numeric preflight: {a7ff24r.get('decision')}")

    formula_raw = pd.read_csv(FORMULA_INDEX)
    materialization = pd.read_csv(MATERIALIZATION_QUEUE)
    company = pd.read_csv(COMPANY_QUEUE)
    derived = pd.read_csv(DERIVED_CATALOG)
    shard_plan = pd.read_csv(SHARD_PLAN)
    formula = add_membership(formula_raw, materialization, company)

    by_level = coverage_table(formula, ["level"])
    by_semantic = coverage_table(formula, ["semantic_pair"])
    by_motif = coverage_table(formula, ["motif"])
    base_rows = explode_base_fields(formula)
    by_base = coverage_table(base_rows, ["base_field", "semantic_type", "seed_route"])
    materialization_dropoff = dropoff_table(formula, ["level", "semantic_pair", "motif"])

    semantic_company = by_semantic[by_semantic["company_wave_count"] > 0].copy()
    motif_company = by_motif[by_motif["company_wave_count"] > 0].copy()
    base_company = by_base[by_base["company_wave_count"] > 0].copy()
    company_rows = int(formula["in_company_wave"].sum())
    materialization_rows = int(formula["in_materialization_queue"].sum())
    top_semantic_share = float(semantic_company["company_wave_share"].max()) if not semantic_company.empty else 1.0
    top_base_share = float(base_company["company_wave_share"].max()) if not base_company.empty else 1.0
    top_motif_share = float(motif_company["company_wave_share"].max()) if not motif_company.empty else 1.0
    company_semantic_count = int(semantic_company["semantic_pair"].nunique())
    company_motif_count = int(motif_company["motif"].nunique())
    company_base_semantic_types = set(base_company["semantic_type"].dropna().astype(str))
    missing_important_field_types = sorted(IMPORTANT_FIELD_TYPES - company_base_semantic_types)

    issues: list[str] = []
    warnings: list[str] = []
    if company_semantic_count < 8:
        issues.append("company_semantic_pair_count_lt_8")
    if company_motif_count < 6:
        issues.append("company_motif_count_lt_6")
    if top_semantic_share > 0.35:
        issues.append("top_semantic_pair_share_gt_35pct")
    if top_base_share > 0.35:
        issues.append("top_base_field_share_gt_35pct")
    if top_motif_share > 0.35:
        warnings.append("top_motif_share_gt_35pct")
    if missing_important_field_types:
        warnings.append("important_field_type_absent_from_company_wave:" + ",".join(missing_important_field_types))

    # Missing company coverage for large formula families is a warning, not a hard
    # blocker, because A7FF-24R intentionally selects a bounded wave from a wider atlas.
    unrepresented_large = materialization_dropoff[
        (materialization_dropoff["formula_count"] >= 250)
        & (materialization_dropoff["company_wave_count"] == 0)
    ].copy()
    if not unrepresented_large.empty:
        warnings.append(f"large_formula_families_absent_from_company_wave:{len(unrepresented_large)}")

    if issues:
        decision = "HOLD_A7FF25R0_COMPANY_QUEUE_COVERAGE_BIASED"
        authorizes_next = False
    else:
        decision = "PASS_A7FF25R0_COMPANY_QUEUE_COVERAGE_ACCEPTABLE_WITH_WARNINGS" if warnings else "PASS_A7FF25R0_COMPANY_QUEUE_COVERAGE_ACCEPTABLE"
        authorizes_next = True

    by_level.to_csv(RUNTIME / "a7ff25r0_company_queue_coverage_by_level.csv", index=False)
    by_semantic.to_csv(RUNTIME / "a7ff25r0_company_queue_coverage_by_semantic_pair.csv", index=False)
    by_motif.to_csv(RUNTIME / "a7ff25r0_company_queue_coverage_by_motif.csv", index=False)
    by_base.to_csv(RUNTIME / "a7ff25r0_company_queue_coverage_by_base_field.csv", index=False)
    materialization_dropoff.to_csv(RUNTIME / "a7ff25r0_materialization_dropoff_audit.csv", index=False)
    unrepresented_large.to_csv(RUNTIME / "a7ff25r0_unrepresented_large_families.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ff25r0_company_shard_plan_copy.csv", index=False)

    experiment_record = {
        "date": "2026-05-30",
        "experiment_id": "20260530_a7ff25r0_company_queue_coverage",
        "objective": "audit whether A7FF-24R company numeric queue represents the versioned formula atlas well enough for adapter smoke",
        "status": "completed",
        "mode": "light",
        "inputs": [
            str(FORMULA_INDEX),
            str(DERIVED_CATALOG),
            str(MATERIALIZATION_QUEUE),
            str(COMPANY_QUEUE),
            str(SHARD_PLAN),
        ],
        "commands": [
            "G:\\PythonProject\\.venv\\Scripts\\python.exe scripts\\crypto_a7ff25r0_company_queue_coverage_audit.py"
        ],
        "outputs": [
            str(REPORT),
            str(RUNTIME),
        ],
        "decision": decision,
        "next_action": "A7FF-25R1 numeric adapter parity smoke if PASS/HOLD warnings accepted",
    }
    write_json(RUNTIME / "a7ff25r0_experiment_record.json", experiment_record)

    manifest = {
        "stage": "A7FF-25R0-COMPANY-QUEUE-COVERAGE-AUDIT",
        "generated_at": now_utc(),
        "decision": decision,
        "issues": issues,
        "warnings": warnings,
        "version_id": version.get("version_id"),
        "version_head": git_text("rev-parse", "HEAD"),
        "formula_rows": int(len(formula)),
        "materialization_queue_count": materialization_rows,
        "company_wave_queue_count": company_rows,
        "company_semantic_pair_count": company_semantic_count,
        "company_motif_count": company_motif_count,
        "company_base_field_count": int(base_company["base_field"].nunique()) if not base_company.empty else 0,
        "company_base_semantic_type_count": int(len(company_base_semantic_types)),
        "top_semantic_pair_share": top_semantic_share,
        "top_motif_share": top_motif_share,
        "top_base_field_share": top_base_share,
        "missing_important_field_types": missing_important_field_types,
        "large_unrepresented_family_count": int(len(unrepresented_large)),
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff25r1_adapter_parity_smoke": authorizes_next,
        "authorizes_full_12_shard_numeric": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff25r0_manifest.json", manifest)

    report = f"""# CRYPTO A7FF-25R0 COMPANY QUEUE COVERAGE AUDIT

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-25R0 audits the A7FF-24R company numeric queue before any numeric probe. It checks whether the 2,400-row company wave reasonably represents the 20,599-row versioned formula atlas.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Coverage Criteria

```text
semantic_pair_count_in_company >= 8
motif_count_in_company >= 6
top_semantic_pair_share <= 35%
top_base_field_share <= 35%
important field families should not be silently absent
```

## Coverage By Level

{md_table(by_level)}

## Coverage By Semantic Pair

{md_table(by_semantic, 80)}

## Coverage By Motif

{md_table(by_motif, 80)}

## Coverage By Base Field

{md_table(by_base, 80)}

## Materialization / Company Dropoff

{md_table(materialization_dropoff, 80)}

## Large Formula Families Absent From Company Wave

{md_table(unrepresented_large, 80)}

## Company Shard Plan

{md_table(shard_plan)}

## Experiment Record

```json
{json.dumps(experiment_record, indent=2, sort_keys=True)}
```

## Boundary

```text
numeric probe executed: false
replay executed: false
search executed: false
May used: false
full 12-shard numeric execution authorized: false
next allowed if PASS: A7FF-25R1 numeric adapter parity smoke
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
