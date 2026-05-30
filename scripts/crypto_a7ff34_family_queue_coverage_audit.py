from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff34_family_queue_coverage_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FF34_FAMILY_QUEUE_COVERAGE_AUDIT_20260530.md"

A7FF33_MANIFEST = REPO / "runtime" / "a7ff33_family_diversified_dry_generation" / "a7ff33_manifest.json"
A7FF33_POOL = REPO / "runtime" / "a7ff33_family_diversified_dry_generation" / "a7ff33_blueprint_pool.csv"
A7FF33_MATERIALIZATION = REPO / "runtime" / "a7ff33_family_diversified_dry_generation" / "a7ff33_materialization_queue.csv"
A7FF33_COMPANY = REPO / "runtime" / "a7ff33_family_diversified_dry_generation" / "a7ff33_company_numeric_wave_queue.csv"

FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Mean",
    "Delta",
    "TSRank",
    "Decay",
    "Rank",
    "CSRank",
    "ZScore",
    "Mul",
    "Sub",
    "Add",
    "Neg",
    "Abs",
    "Sign",
    "SafeDiv",
    "Clip",
    "Winsor",
}


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


def expression_fields(expr: str) -> list[str]:
    return [token for token in FIELD_RE.findall(str(expr)) if token not in OPERATORS]


def field_usage(frame: pd.DataFrame, label: str) -> pd.DataFrame:
    counts: Counter[str] = Counter()
    for expr in frame["expression"].astype(str):
        counts.update(expression_fields(expr))
    return pd.DataFrame(
        [{"queue": label, "field": field, "formula_count": count} for field, count in counts.most_common()]
    )


def coverage(frame: pd.DataFrame, label: str) -> pd.DataFrame:
    rows = []
    total = max(1, len(frame))
    for key in ["family_id", "root_family", "motif", "level"]:
        summary = frame[key].value_counts().reset_index()
        summary.columns = [key, "count"]
        summary["share"] = summary["count"] / total
        summary["queue"] = label
        rows.append(summary)
    return pd.concat(rows, ignore_index=True)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    f33 = read_json(A7FF33_MANIFEST)
    if not f33.get("authorizes_a7ff34_queue_coverage_audit"):
        raise SystemExit(f"A7FF-33 does not authorize A7FF-34: {f33.get('decision')}")

    pool = pd.read_csv(A7FF33_POOL)
    materialization = pd.read_csv(A7FF33_MATERIALIZATION)
    company = pd.read_csv(A7FF33_COMPANY)

    coverage_df = pd.concat(
        [coverage(pool, "blueprint_pool"), coverage(materialization, "materialization_queue"), coverage(company, "company_wave")],
        ignore_index=True,
    )
    coverage_df.to_csv(RUNTIME / "a7ff34_queue_coverage_summary.csv", index=False)

    fields = pd.concat(
        [field_usage(pool, "blueprint_pool"), field_usage(materialization, "materialization_queue"), field_usage(company, "company_wave")],
        ignore_index=True,
    )
    fields.to_csv(RUNTIME / "a7ff34_base_field_usage.csv", index=False)

    shard = (
        company.groupby("company_shard", dropna=False)
        .agg(
            row_count=("blueprint_id", "count"),
            family_count=("family_id", "nunique"),
            root_family_count=("root_family", "nunique"),
            motif_count=("motif", "nunique"),
            skeleton_count=("skeleton_key", "nunique"),
        )
        .reset_index()
        .sort_values("company_shard")
    )
    shard.to_csv(RUNTIME / "a7ff34_company_shard_coverage.csv", index=False)

    family = (
        company.groupby(["family_id", "root_family"], dropna=False)
        .agg(
            company_wave_count=("blueprint_id", "count"),
            company_wave_share=("blueprint_id", lambda x: len(x) / max(1, len(company))),
            motif_count=("motif", "nunique"),
            skeleton_count=("skeleton_key", "nunique"),
            primary_field_count=("primary_field", "nunique"),
            secondary_field_count=("secondary_field", "nunique"),
        )
        .reset_index()
        .sort_values("company_wave_count", ascending=False)
    )
    family.to_csv(RUNTIME / "a7ff34_company_family_coverage.csv", index=False)

    root_shares = company["root_family"].value_counts(normalize=True)
    top_root_share = float(root_shares.max()) if not root_shares.empty else 0.0
    basis_root_share = float(root_shares.get("basis_premium_like|basis_premium_like", 0.0))
    non_basis_share = 1.0 - basis_root_share
    shard_imbalanced = bool(shard["row_count"].nunique() != 1)
    blockers: list[str] = []
    warnings: list[str] = []
    if company["family_id"].nunique() < 7:
        blockers.append("family_count_below_7")
    if company["motif"].nunique() < 10:
        blockers.append("motif_count_below_10")
    if non_basis_share < 0.65:
        blockers.append("non_basis_share_below_65pct")
    if top_root_share > 0.35:
        blockers.append("top_root_family_share_above_35pct")
    if basis_root_share > 0.20:
        blockers.append("basis_root_share_above_20pct")
    if shard_imbalanced:
        warnings.append("company_shard_row_count_imbalance")
    if fields[(fields["queue"].eq("company_wave")) & (fields["field"].eq("funding_rate"))]["formula_count"].sum() > 0:
        blockers.append("raw_funding_rate_in_company_wave")

    decision = "PASS_A7FF34_FAMILY_QUEUE_COVERAGE_ACCEPTABLE_READY_FOR_A7FF35_NUMERIC_PREFLIGHT_NO_SEARCH_AUTH" if not blockers else "HOLD_A7FF34_QUEUE_COVERAGE_FAIL"
    manifest = {
        "stage": "A7FF-34",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_a7ff33_decision": f33.get("decision"),
        "blueprint_count": int(len(pool)),
        "materialization_queue_count": int(len(materialization)),
        "company_wave_queue_count": int(len(company)),
        "company_shard_count": int(company["company_shard"].nunique()),
        "company_family_count": int(company["family_id"].nunique()),
        "company_motif_count": int(company["motif"].nunique()),
        "company_top_root_family_share": top_root_share,
        "company_basis_root_share": basis_root_share,
        "company_non_basis_share": non_basis_share,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_a7ff35_numeric_prefight": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff34_manifest.json", manifest)
    write_json(RUNTIME / "a7ff34_decision_record.json", manifest)

    report = f"""# CRYPTO A7FF-34 FAMILY QUEUE COVERAGE AUDIT

Generated: {manifest["generated_at"]}

## Decision

`{decision}`

A7FF-34 audits A7FF-33 queue coverage only. It does not run numeric probe, replay, search, alpha proof, shadow, paper, or live.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Company Family Coverage

{md_table(family)}

## Company Shard Coverage

{md_table(shard)}

## Company Field Usage

{md_table(fields[fields["queue"].eq("company_wave")], 100)}

## Boundary

```text
numeric probe executed: false
replay executed: false
search executed: false
May used: false
next if PASS: A7FF-35 numeric preflight on diversified queue
```
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
