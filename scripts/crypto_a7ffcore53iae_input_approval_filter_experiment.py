from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE53IA = REPO / "runtime" / "a7ffcore53ia_incremental_input_approval"
A7FF_VERSION = REPO / "runtime" / "a7ff_version_20260530"
CORE51PX = REPO / "runtime" / "a7ffcore51px_company_sharded_replay_runner_contract"
CORE52 = REPO / "runtime" / "a7ffcore52_company_replay_arbitration"
RUNTIME = REPO / "runtime" / "a7ffcore53iae_input_approval_filter_experiment"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE53IAE_INPUT_APPROVAL_FILTER_EXPERIMENT_20260603.md"

FIELD_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b")
FUNCTION_TOKENS = {
    "Abs",
    "Add",
    "Clip",
    "CSRank",
    "Decay",
    "Delta",
    "Identity",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "SignedRankDelta",
    "SpreadShortLong",
    "Sub",
    "TSRank",
    "WinsorZ",
    "ZScore",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def parse_fields(expression: str, known_fields: set[str]) -> list[str]:
    out = []
    for token in FIELD_RE.findall(str(expression)):
        if token in FUNCTION_TOKENS:
            continue
        if token in known_fields:
            out.append(token)
    return sorted(set(out))


def build_registry(ledger: pd.DataFrame) -> pd.DataFrame:
    registry = ledger[
        [
            "field",
            "semantic_type",
            "info_cluster_id",
            "cluster_size",
            "coverage",
            "unique_count",
            "median_xs_std",
            "active_xs_share",
            "input_approval",
            "approval_reason",
        ]
    ].copy()
    role = []
    for _, row in registry.iterrows():
        approval = str(row["input_approval"])
        if approval == "approved_incremental_signal_input":
            role.append("signal_primary")
        elif approval == "approved_redundant_cluster_member_requires_cap":
            role.append("signal_redundant_cap")
        elif approval == "approved_condition_or_neutralizer_only":
            role.append("condition_or_neutralizer")
        elif approval.startswith("blocked"):
            role.append("blocked")
        else:
            role.append("unknown")
    registry["system_input_role"] = role
    return registry


def classify_formula(fields: list[str], registry_by_field: dict[str, dict]) -> tuple[str, str, str, str]:
    if not fields:
        return "reject_no_known_input", "", "", "no_known_approved_field"
    missing = [f for f in fields if f not in registry_by_field]
    if missing:
        return "reject_unknown_input", "|".join(missing), "", "unknown_field_not_in_approval_ledger"
    roles = [registry_by_field[f]["system_input_role"] for f in fields]
    clusters = [registry_by_field[f]["info_cluster_id"] for f in fields]
    blocked = [f for f, role in zip(fields, roles) if role == "blocked"]
    if blocked:
        return "reject_blocked_input", "|".join(blocked), "|".join(sorted(set(clusters))), "contains_blocked_field"
    primary = [f for f, role in zip(fields, roles) if role == "signal_primary"]
    redundant = [f for f, role in zip(fields, roles) if role == "signal_redundant_cap"]
    condition = [f for f, role in zip(fields, roles) if role == "condition_or_neutralizer"]
    if primary:
        if len(set(clusters)) < len(clusters):
            return "accept_primary_with_cluster_overlap_warning", "", "|".join(sorted(set(clusters))), "has_primary_signal_but_cluster_overlap"
        return "accept_primary_incremental_input", "", "|".join(sorted(set(clusters))), "has_primary_incremental_signal"
    if redundant:
        if condition:
            return "accept_redundant_cap_with_condition_only", "", "|".join(sorted(set(clusters))), "redundant_signal_requires_cluster_cap"
        return "accept_redundant_cap_only", "", "|".join(sorted(set(clusters))), "redundant_signal_requires_cluster_cap"
    return "reject_condition_only", "|".join(condition), "|".join(sorted(set(clusters))), "condition_fields_not_alpha_inputs"


def apply_filter(pool: pd.DataFrame, pool_name: str, registry: pd.DataFrame) -> pd.DataFrame:
    registry_by_field = registry.set_index("field").to_dict("index")
    known_fields = set(registry_by_field)
    rows = []
    for _, row in pool.iterrows():
        expression = row.get("expression", "")
        seed_id = row.get("seed_id", row.get("formula_id", row.get("id", "")))
        fields = parse_fields(expression, known_fields)
        decision, rejected_fields, clusters, reason = classify_formula(fields, registry_by_field)
        rows.append(
            {
                "pool_name": pool_name,
                "seed_id": seed_id,
                "expression": expression,
                "semantic_pair": row.get("semantic_pair", ""),
                "operator": row.get("operator", row.get("motif", "")),
                "input_fields": "|".join(fields),
                "input_field_count": len(fields),
                "info_clusters": clusters,
                "input_cluster_count": len(set(clusters.split("|"))) if clusters else 0,
                "filter_decision": decision,
                "rejected_fields": rejected_fields,
                "filter_reason": reason,
            }
        )
    return pd.DataFrame(rows)


def summarize(filtered: pd.DataFrame) -> pd.DataFrame:
    return (
        filtered.groupby(["pool_name", "filter_decision"], as_index=False)
        .agg(
            formula_count=("seed_id", "count"),
            semantic_pair_count=("semantic_pair", "nunique"),
            operator_count=("operator", "nunique"),
            median_input_field_count=("input_field_count", "median"),
        )
        .sort_values(["pool_name", "formula_count"], ascending=[True, False])
    )


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE53IA / "a7ffcore53ia_manifest.json")
    if source.get("decision") != "PASS_A7FFCORE53IA_INCREMENTAL_INPUT_APPROVAL_BUILT":
        raise SystemExit(f"CORE53IA not ready for filter experiment: {source.get('decision')}")
    ledger = pd.read_csv(CORE53IA / "a7ffcore53ia_field_input_approval_ledger.csv")
    registry = build_registry(ledger)
    formula_index = pd.read_csv(A7FF_VERSION / "a7ff_v20260530_formula_index.csv")
    selected_queue = pd.read_csv(CORE51PX / "a7ffcore51px_selected_candidate_queue.csv")
    seed_arbitration = pd.read_csv(CORE52 / "a7ffcore52_seed_arbitration.csv")

    formula_filtered = apply_filter(formula_index, "a7ff_v20260530_formula_index", registry)
    queue_filtered = apply_filter(selected_queue, "core51px_selected_queue", registry)
    queue_with_arbitration = queue_filtered.merge(
        seed_arbitration[
            [
                "seed_id",
                "arbitration_status",
                "clean_label_count",
                "clean_horizons",
                "median_control_ratio",
                "max_original_spread",
            ]
        ],
        on="seed_id",
        how="left",
    )
    combined = pd.concat([formula_filtered, queue_filtered], ignore_index=True)
    summary = summarize(combined)
    registry_summary = (
        registry.groupby(["semantic_type", "system_input_role"], as_index=False)
        .agg(field_count=("field", "count"))
        .sort_values(["semantic_type", "field_count"], ascending=[True, False])
    )
    clue_filter_summary = (
        queue_with_arbitration.groupby(["arbitration_status", "filter_decision"], dropna=False, as_index=False)
        .agg(seed_count=("seed_id", "count"), median_control_ratio=("median_control_ratio", "median"))
        .sort_values(["arbitration_status", "seed_count"], ascending=[True, False])
    )
    cluster_counter = Counter()
    for value in formula_filtered.loc[formula_filtered["filter_decision"].str.startswith("accept"), "info_clusters"].dropna():
        for cluster in str(value).split("|"):
            if cluster:
                cluster_counter[cluster] += 1
    cluster_usage = pd.DataFrame(
        [{"info_cluster_id": cluster, "accepted_formula_count": count} for cluster, count in cluster_counter.items()]
    ).sort_values("accepted_formula_count", ascending=False)
    cluster_usage = cluster_usage.merge(
        registry[["info_cluster_id", "field", "semantic_type"]]
        .groupby("info_cluster_id", as_index=False)
        .agg(fields=("field", lambda s: "|".join(sorted(s))), semantic_types=("semantic_type", lambda s: "|".join(sorted(set(s))))),
        on="info_cluster_id",
        how="left",
    )
    accepted_formula_count = int(formula_filtered["filter_decision"].str.startswith("accept").sum())
    rejected_formula_count = int(formula_filtered.shape[0] - accepted_formula_count)
    queue_accepted_count = int(queue_filtered["filter_decision"].str.startswith("accept").sum())
    queue_rejected_count = int(queue_filtered.shape[0] - queue_accepted_count)
    strict_clues = queue_with_arbitration["arbitration_status"].eq("strict_replay_clue")
    strict_clue_accepted_count = int(queue_with_arbitration.loc[strict_clues, "filter_decision"].str.startswith("accept").sum())
    diagnostic_clues = queue_with_arbitration["arbitration_status"].isin(["diagnostic_clue", "strict_replay_clue"])
    diagnostic_clue_accepted_count = int(queue_with_arbitration.loc[diagnostic_clues, "filter_decision"].str.startswith("accept").sum())
    manifest = {
        "stage": "A7FF-CORE53IAE",
        "generated_at": now_utc(),
        "source_stage": source.get("stage"),
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE53IAE_INPUT_APPROVAL_FILTER_EXPERIMENT_BUILT",
        "formula_index_rows": int(formula_filtered.shape[0]),
        "formula_index_accepted_count": accepted_formula_count,
        "formula_index_rejected_count": rejected_formula_count,
        "formula_index_accept_rate": accepted_formula_count / max(1, int(formula_filtered.shape[0])),
        "selected_queue_rows": int(queue_filtered.shape[0]),
        "selected_queue_accepted_count": queue_accepted_count,
        "selected_queue_rejected_count": queue_rejected_count,
        "strict_clue_accepted_count": strict_clue_accepted_count,
        "diagnostic_clue_accepted_count": diagnostic_clue_accepted_count,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core54_queue_builder": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    authorization = {
        "authorized": {
            "A7FF-CORE54 input-approval-aware queue builder": True,
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    registry.to_csv(RUNTIME / "a7ffcore53iae_system_input_registry.csv", index=False)
    formula_filtered.to_csv(RUNTIME / "a7ffcore53iae_formula_index_filter_trace.csv", index=False)
    queue_with_arbitration.to_csv(RUNTIME / "a7ffcore53iae_selected_queue_filter_trace.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore53iae_filter_summary.csv", index=False)
    registry_summary.to_csv(RUNTIME / "a7ffcore53iae_registry_summary.csv", index=False)
    clue_filter_summary.to_csv(RUNTIME / "a7ffcore53iae_clue_filter_summary.csv", index=False)
    cluster_usage.to_csv(RUNTIME / "a7ffcore53iae_accepted_cluster_usage.csv", index=False)
    write_json(RUNTIME / "a7ffcore53iae_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore53iae_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE53IAE INPUT APPROVAL FILTER EXPERIMENT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE53IAE applies the input approval ledger to the formula index and current selected replay queue. It validates whether the approval layer can screen information sources before candidate construction. It does not execute replay/search/proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## System Input Registry Summary",
        "",
        md_table(registry_summary),
        "",
        "## Filter Summary",
        "",
        md_table(summary, 80),
        "",
        "## Clue Filter Summary",
        "",
        md_table(clue_filter_summary, 80),
        "",
        "## Accepted Cluster Usage",
        "",
        md_table(cluster_usage, 80),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
