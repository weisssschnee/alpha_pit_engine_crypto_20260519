from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff25r4_no_activity_tail_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FF25R4_NO_ACTIVITY_TAIL_AUDIT_20260530.md"
A7FF25R3 = REPO / "runtime" / "a7ff25r3_full_numeric_wave"
A7FF24R = REPO / "runtime" / "a7ff24r_dry_generation_plan"

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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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


def expression_fields(expression: str) -> list[str]:
    fields: list[str] = []
    for token in FIELD_RE.findall(str(expression)):
        if token in OPERATORS or token in {"nan", "inf"}:
            continue
        fields.append(token)
    return fields


def classify_failure(row: pd.Series) -> str:
    if not bool(row.get("eval_success", False)):
        return "eval_failure"
    finite = float(row.get("finite_share", 0.0) or 0.0)
    nonzero = float(row.get("nonzero_share", 0.0) or 0.0)
    if finite < 0.20:
        return "low_finite_share"
    if nonzero < 0.01:
        return "low_nonzero_share"
    if not bool(row.get("activity_ok", False)):
        return "activity_threshold_fail"
    return "activity_ok"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    prior = read_json(A7FF25R3 / "a7ff25r3_manifest.json")
    shard_summary = read_csv(A7FF25R3 / "a7ff25r3_shard_summary.csv")
    if shard_summary.empty:
        raise SystemExit("missing A7FF-25R3 shard summary")

    no_activity = shard_summary[shard_summary["materialized_activity_ok_count"].astype(float).eq(0)].copy()
    no_activity_shards = [f"{int(x):02d}" if str(x).isdigit() else str(x).zfill(2) for x in no_activity["shard"].tolist()]

    tail_rows: list[pd.DataFrame] = []
    field_counter: Counter[str] = Counter()
    for shard in no_activity_shards:
        q = read_csv(A7FF24R / f"a7ff24r_company_shard_{shard}_queue.csv")
        m = read_csv(A7FF25R3 / f"shard_{shard}" / f"a7ff25r3s{shard}_materialization_metrics.csv")
        if q.empty or m.empty:
            continue
        q_cols = ["blueprint_id", "semantic_pair", "motif", "candidate_role", "expression"]
        merged = m.merge(q[q_cols], on=["blueprint_id", "expression"], how="left", suffixes=("", "_queue"))
        merged["shard"] = shard
        merged["fields"] = merged["expression"].map(lambda x: ";".join(expression_fields(x)))
        merged["failure_reason"] = merged.apply(classify_failure, axis=1)
        for fields in merged["fields"]:
            for field in str(fields).split(";"):
                if field:
                    field_counter[field] += 1
        tail_rows.append(merged)

    tail = pd.concat(tail_rows, ignore_index=True) if tail_rows else pd.DataFrame()
    if not tail.empty:
        cols = [
            "shard",
            "blueprint_id",
            "semantic_pair",
            "motif",
            "expression",
            "eval_success",
            "finite_share",
            "nonzero_share",
            "activity_ok",
            "failure_reason",
            "fields",
        ]
        tail[cols].to_csv(RUNTIME / "a7ff25r4_tail_blueprint_failure_audit.csv", index=False)
    else:
        pd.DataFrame().to_csv(RUNTIME / "a7ff25r4_tail_blueprint_failure_audit.csv", index=False)

    family_motif = (
        tail.groupby(["shard", "semantic_pair", "motif", "failure_reason"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["shard", "count"], ascending=[True, False])
        if not tail.empty
        else pd.DataFrame(columns=["shard", "semantic_pair", "motif", "failure_reason", "count"])
    )
    family_motif.to_csv(RUNTIME / "a7ff25r4_tail_family_motif_failure_summary.csv", index=False)

    field_usage = pd.DataFrame([{"field": k, "tail_expression_count": v} for k, v in field_counter.items()]).sort_values(
        "tail_expression_count", ascending=False
    )
    field_usage.to_csv(RUNTIME / "a7ff25r4_tail_queue_field_usage.csv", index=False)

    shard_activity = shard_summary.copy()
    shard_activity["is_no_activity_tail"] = shard_activity["shard"].astype(str).str.zfill(2).isin(no_activity_shards)
    shard_activity.to_csv(RUNTIME / "a7ff25r4_shard_activity_summary.csv", index=False)

    if not tail.empty:
        failure_summary = (
            tail.groupby(["failure_reason"], dropna=False)
            .agg(
                rows=("blueprint_id", "count"),
                finite_share_median=("finite_share", "median"),
                finite_share_max=("finite_share", "max"),
                nonzero_share_median=("nonzero_share", "median"),
            )
            .reset_index()
        )
    else:
        failure_summary = pd.DataFrame(columns=["failure_reason", "rows", "finite_share_median", "finite_share_max", "nonzero_share_median"])
    failure_summary.to_csv(RUNTIME / "a7ff25r4_failure_reason_summary.csv", index=False)

    repair_policy = pd.DataFrame(
        [
            {
                "policy_id": "funding_raw_sparse_quarantine",
                "applies_to": "raw funding_rate expressions in company queue",
                "action": "do_not_count_as_healthy_company_queue_until dense funding-state transforms exist",
                "reason": "eval_success but low finite_share caused all activity_ok=0 in shards 08-11",
            },
            {
                "policy_id": "funding_state_rebuild",
                "applies_to": "funding_like semantic family",
                "action": "replace raw funding_rate wrappers with settlement-aware or forward-filled funding state features before numeric wave",
                "reason": "sparse event-style funding field is not suitable as a direct dense 1h alpha field",
            },
            {
                "policy_id": "queue_tail_backfill",
                "applies_to": "A7FF company queue",
                "action": "backfill shards 08-11 with activity-capable semantic pairs before full replay authorization",
                "reason": "2400-row queue contains 800 rows that materialize to no activity",
            },
        ]
    )
    repair_policy.to_csv(RUNTIME / "a7ff25r4_tail_repair_policy.csv", index=False)

    tail_count = int(len(tail))
    low_finite_rows = int((tail["failure_reason"].eq("low_finite_share")).sum()) if not tail.empty else 0
    funding_rows = int(field_counter.get("funding_rate", 0))
    warnings = []
    if no_activity_shards:
        warnings.append("no_activity_tail_shards")
    if tail_count and low_finite_rows == tail_count:
        warnings.append("all_tail_failures_low_finite_share")
    if funding_rows == tail_count:
        warnings.append("tail_all_uses_funding_rate")

    decision = (
        "PASS_A7FF25R4_NO_ACTIVITY_TAIL_CAUSE_IDENTIFIED_REPAIR_REQUIRED"
        if no_activity_shards and tail_count > 0
        else "PASS_A7FF25R4_NO_NO_ACTIVITY_TAIL_FOUND"
    )
    manifest = {
        "stage": "A7FF-25R4",
        "generated_at": now_utc(),
        "decision": decision,
        "warnings": warnings,
        "prior_stage": prior.get("stage", "A7FF-25R3"),
        "prior_decision": prior.get("decision", ""),
        "no_activity_shards": no_activity_shards,
        "tail_blueprint_count": tail_count,
        "tail_low_finite_share_count": low_finite_rows,
        "tail_funding_rate_expression_count": funding_rows,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_queue_repair": True,
    }
    write_json(RUNTIME / "a7ff25r4_manifest.json", manifest)
    write_json(RUNTIME / "a7ff25r4_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-25R4 NO-ACTIVITY TAIL AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-25R4 audits why A7FF-25R3 shards 08-11 had eval success but zero activity-ok blueprints. It does not generate, replay, search, or prove alpha.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Failure Summary",
        "",
        md_table(failure_summary, 40),
        "",
        "## Tail Field Usage",
        "",
        md_table(field_usage, 40),
        "",
        "## Tail Family/Motif Failures",
        "",
        md_table(family_motif, 80),
        "",
        "## Repair Policy",
        "",
        md_table(repair_policy, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "Funding-like raw sparse expressions are not deleted; they are quarantined from healthy company-wave evidence until rebuilt as dense funding-state features.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
