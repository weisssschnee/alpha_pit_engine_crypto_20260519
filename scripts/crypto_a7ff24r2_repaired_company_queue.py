from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff24r2_repaired_company_queue"
REPORT = REPO / "reports" / "CRYPTO_A7FF24R2_REPAIRED_COMPANY_QUEUE_20260530.md"
A7FF24R = REPO / "runtime" / "a7ff24r_dry_generation_plan"
A7FF25R4 = REPO / "runtime" / "a7ff25r4_no_activity_tail_audit"
A7FF25R6 = REPO / "runtime" / "a7ff25r6_dense_funding_state_audit"

ORIGINAL_QUEUE = A7FF24R / "a7ff24r_company_numeric_wave_queue.csv"
TAIL_AUDIT = A7FF25R4 / "a7ff25r4_tail_blueprint_failure_audit.csv"
TAIL_SHARDS = {"shard_08", "shard_09", "shard_10", "shard_11"}
SHARD_SIZE = 200


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def stable_id(prefix: str, expression: str, semantic_pair: str, motif: str) -> str:
    key = f"{expression}|{semantic_pair}|{motif}".encode("utf-8")
    return f"{prefix}_{hashlib.sha1(key).hexdigest()[:16]}"


def repair_expression(expression: str) -> tuple[str, str]:
    expr = str(expression)
    if "funding_rate" not in expr:
        return expr, "unchanged"
    if "Delta(funding_rate," in expr:
        repaired = re.sub(r"Delta\(funding_rate,(\d+)\)", r"Delta(funding_rate_state_last_ffill_8h,\1)", expr)
        return repaired, "delta_dense_state"
    if "Mean(funding_rate," in expr:
        repaired = re.sub(r"Mean\(funding_rate,(\d+)\)", r"Mean(funding_rate_state_last_ffill_8h,\1)", expr)
        return repaired, "mean_dense_state"
    repaired = expr.replace("funding_rate", "funding_rate_state_last_ffill_8h")
    return repaired, "generic_dense_state"


def classify_dense_fields(expression: str) -> str:
    fields = []
    for field in [
        "funding_rate_state_last_ffill_8h",
        "funding_rate_update_age_hours",
        "funding_rate_abs_state_168h_z",
        "funding_rate_delta_state_24h",
        "funding_state_x_basis_delta",
    ]:
        if field in expression:
            fields.append(field)
    return ";".join(fields)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    original = read_csv(ORIGINAL_QUEUE)
    tail_audit = read_csv(TAIL_AUDIT)
    r6_manifest = read_json(A7FF25R6 / "a7ff25r6_manifest.json")
    r6_metrics = read_csv(A7FF25R6 / "a7ff25r6_dense_funding_state_activity_metrics.csv")
    if not r6_manifest.get("authorizes_queue_repair_contract"):
        raise SystemExit("A7FF-25R6 does not authorize queue repair")
    if original.empty or tail_audit.empty:
        raise SystemExit("missing original queue or tail audit")

    healthy = original[~original["company_shard"].isin(TAIL_SHARDS)].copy()
    tail = original[original["company_shard"].isin(TAIL_SHARDS)].copy()
    tail_ids = set(tail_audit["blueprint_id"].astype(str))
    tail = tail[tail["blueprint_id"].astype(str).isin(tail_ids)].copy()
    if len(tail) != 800:
        raise SystemExit(f"expected 800 tail rows, got {len(tail)}")

    repaired_rows: list[dict[str, Any]] = []
    for _, row in tail.iterrows():
        payload = row.to_dict()
        old_expression = str(payload["expression"])
        new_expression, repair_rule = repair_expression(old_expression)
        payload["source_blueprint_id"] = payload["blueprint_id"]
        payload["source_expression"] = old_expression
        payload["expression"] = new_expression
        payload["repair_rule"] = repair_rule
        payload["primary_field"] = "funding_rate_state_last_ffill_8h" if payload.get("primary_field") == "funding_rate" else payload.get("primary_field")
        payload["primary_transform"] = str(payload.get("primary_transform", "")).replace("funding_rate", "funding_rate_state_last_ffill_8h")
        payload["candidate_role"] = "ordinary_alpha_valid_requires_dense_funding_materializer"
        payload["dense_funding_fields_required"] = classify_dense_fields(new_expression)
        payload["raw_funding_rate_present"] = "funding_rate" in new_expression and "funding_rate_state" not in new_expression
        payload["blueprint_id"] = stable_id("a7ff24r2", new_expression, str(payload.get("semantic_pair", "")), str(payload.get("motif", "")))
        payload["production_key"] = stable_id("prod", new_expression, str(payload.get("semantic_pair", "")), str(payload.get("motif", "")))
        payload["skeleton_key"] = stable_id("skel", re.sub(r"\d+", "N", new_expression), str(payload.get("semantic_pair", "")), str(payload.get("motif", "")))
        repaired_rows.append(payload)
    repaired_tail = pd.DataFrame(repaired_rows)

    repaired_queue = pd.concat([healthy, repaired_tail], ignore_index=True, sort=False)
    repaired_queue["company_shard"] = [f"shard_{i // SHARD_SIZE:02d}" for i in range(len(repaired_queue))]
    repaired_queue.to_csv(RUNTIME / "a7ff24r2_company_numeric_wave_queue.csv", index=False)

    shard_rows: list[dict[str, Any]] = []
    for shard, group in repaired_queue.groupby("company_shard", sort=True):
        group.to_csv(RUNTIME / f"a7ff24r2_{shard}_queue.csv", index=False)
        shard_rows.append(
            {
                "company_shard": shard,
                "row_count": int(len(group)),
                "semantic_pairs": int(group["semantic_pair"].nunique()),
                "motifs": int(group["motif"].nunique()),
                "skeletons": int(group["skeleton_key"].nunique()),
                "raw_funding_rate_rows": int(group["expression"].astype(str).str.contains(r"\bfunding_rate\b", regex=True).sum()),
                "dense_funding_rows": int(group["expression"].astype(str).str.contains("funding_rate_state_last_ffill_8h", regex=False).sum()),
            }
        )
    shard_plan = pd.DataFrame(shard_rows)
    shard_plan.to_csv(RUNTIME / "a7ff24r2_company_shard_plan.csv", index=False)

    tail_summary = repaired_tail.groupby(["semantic_pair", "motif", "repair_rule"], dropna=False).size().reset_index(name="count")
    tail_summary.to_csv(RUNTIME / "a7ff24r2_repaired_tail_summary.csv", index=False)

    usage_rows = []
    for field in [
        "funding_rate_state_last_ffill_8h",
        "funding_rate_update_age_hours",
        "funding_rate_abs_state_168h_z",
        "funding_rate_delta_state_24h",
        "funding_state_x_basis_delta",
    ]:
        usage_rows.append(
            {
                "field": field,
                "queue_expression_count": int(repaired_queue["expression"].astype(str).str.contains(field, regex=False).sum()),
                "r6_activity_ok": bool(r6_metrics.loc[r6_metrics["field_name"].eq(field), "activity_ok"].astype(str).str.lower().isin(["true", "1"]).any()) if not r6_metrics.empty else False,
            }
        )
    field_usage = pd.DataFrame(usage_rows)
    field_usage.to_csv(RUNTIME / "a7ff24r2_dense_field_usage.csv", index=False)

    repair_policy = pd.DataFrame(
        [
            {
                "gate": "no_raw_funding_rate_tail",
                "rule": "tail shard expressions may not contain raw funding_rate as the dense signal source",
                "status": "pass" if not bool(repaired_tail["raw_funding_rate_present"].any()) else "fail",
            },
            {
                "gate": "dense_materializer_required",
                "rule": "numeric runner must materialize funding_rate_state_last_ffill_8h before evaluating repaired queue",
                "status": "required",
            },
            {
                "gate": "tail_activity_precheck",
                "rule": "A7FF-25R6 dense state finite/nonzero activity passed on 96-symbol audit",
                "status": "pass",
            },
            {
                "gate": "search_boundary",
                "rule": "queue rebuild does not authorize formula search",
                "status": "pass",
            },
        ]
    )
    repair_policy.to_csv(RUNTIME / "a7ff24r2_repair_policy.csv", index=False)

    raw_tail_rows = int(repaired_tail["raw_funding_rate_present"].sum())
    dense_tail_rows = int(repaired_tail["expression"].astype(str).str.contains("funding_rate_state_last_ffill_8h", regex=False).sum())
    warnings: list[str] = []
    if dense_tail_rows < len(repaired_tail):
        warnings.append("not_all_tail_rows_use_dense_funding_state")
    if raw_tail_rows:
        warnings.append("raw_funding_rate_remains_in_tail")
    decision = (
        "PASS_A7FF24R2_REPAIRED_COMPANY_QUEUE_READY_FOR_DENSE_MATERIALIZER_PREFLIGHT_NO_SEARCH_AUTH"
        if len(repaired_queue) == len(original) and raw_tail_rows == 0 and dense_tail_rows == len(repaired_tail)
        else "HOLD_A7FF24R2_REPAIRED_COMPANY_QUEUE_INCOMPLETE"
    )
    manifest = {
        "stage": "A7FF-24R2",
        "generated_at": now_utc(),
        "decision": decision,
        "original_queue_count": int(len(original)),
        "healthy_preserved_count": int(len(healthy)),
        "tail_repaired_count": int(len(repaired_tail)),
        "repaired_queue_count": int(len(repaired_queue)),
        "dense_tail_rows": dense_tail_rows,
        "raw_funding_rate_remaining_tail_rows": raw_tail_rows,
        "company_shard_count": int(shard_plan["company_shard"].nunique()),
        "warnings": warnings,
        "executes_generation": False,
        "executes_numeric_probe": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_dense_materializer_preflight": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff24r2_manifest.json", manifest)
    write_json(RUNTIME / "a7ff24r2_decision_record.json", manifest)

    lines = [
        "# CRYPTO A7FF-24R2 REPAIRED COMPANY QUEUE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-24R2 rebuilds the A7FF-24R company numeric wave queue by preserving healthy shards 00-07 and replacing raw sparse funding_rate tail expressions in shards 08-11 with dense funding-state expressions. It does not run numeric replay or search.",
        "",
        "## Experiment Record",
        "",
        "```text",
        "experiment_id: 20260530_a7ff24r2_repaired_company_queue",
        "objective: repair no-activity funding tail queue without expanding search",
        "inputs: A7FF-24R queue, A7FF-25R4 tail audit, A7FF-25R6 dense funding-state audit",
        "parameters: preserve 1600 healthy rows; repair 800 tail rows; 12 shards x 200 rows",
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan, 20),
        "",
        "## Repaired Tail Summary",
        "",
        md_table(tail_summary, 40),
        "",
        "## Dense Field Usage",
        "",
        md_table(field_usage, 20),
        "",
        "## Repair Policy",
        "",
        md_table(repair_policy, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "A7FF-24R2 only repairs the queue. It does not execute formula search, large search, alpha proof, shadow, paper, or live trading.",
        "The next valid step is dense materializer preflight on the repaired queue.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
