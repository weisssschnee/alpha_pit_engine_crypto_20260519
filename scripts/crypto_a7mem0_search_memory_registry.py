from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.engines.search_memory import (  # noqa: E402
    expression_memory_key,
    skeleton_memory_key,
)
from alphafactory_crypto.evaluation_access import (  # noqa: E402
    EvaluationAccessViolation,
    assert_candidate_feedback_records_allowed,
)


DATE_TAG = "20260628"
STAGE = "A7MEM-0"
RUNTIME = REPO / "runtime" / "a7mem0_search_memory_registry_20260628"
REMOTE_INPUTS = RUNTIME / "remote_inputs"
REPORT = REPO / "reports" / "CRYPTO_A7MEM0_SEARCH_MEMORY_REGISTRY_20260628.md"

SOURCE_FILES = [
    {
        "run_id": "A7REWARD1",
        "source_type": "accepted_prior",
        "path": REPO / "runtime" / "a7reward1_portfolio_reward_model_20260610" / "a7reward1_accepted_for_next_search.csv",
        "notes": "strict reward gate accepted queue before A7SEARCH line",
    },
    {
        "run_id": "A7V3S0",
        "source_type": "accepted_prior",
        "path": REPO / "runtime" / "a7v3s0_reward_sharded_720h_r2_aggregate_20260613" / "a7v3s0_reward_accepted_enriched.csv",
        "notes": "reward aggregate accepted prior",
    },
    {
        "run_id": "A7V3S9",
        "source_type": "accepted_prior",
        "path": REPO / "runtime" / "a7v3s9_selected_full_reward_aggregate_20260614" / "a7v3s0_reward_accepted_enriched.csv",
        "notes": "selected full reward aggregate accepted prior",
    },
    {
        "run_id": "A7SEARCH4",
        "source_type": "strict_pass",
        "path": REMOTE_INPUTS / "a7search4_strict_pass_rows.csv",
        "notes": "company H aggregate strict pass rows copied into A7MEM input",
    },
    {
        "run_id": "A7SEARCH4",
        "source_type": "selected_or_nearmiss",
        "path": REMOTE_INPUTS / "a7search4_selected_rows.csv",
        "notes": "company H aggregate selected rows copied into A7MEM input",
    },
]

ARCHIVE_POINTERS = [
    {
        "run_id": "A7SEARCH4",
        "artifact_role": "final_aggregate",
        "local_pointer": str(REPO / "reports" / "CRYPTO_A7SEARCH4_FINAL_AGGREGATE_STATUS_20260628.md"),
        "remote_pointer": r"H:\AlphaFactory_CryptoData_archive\a7search4_final_aggregate_20260628",
        "status": "available_on_company_H",
    },
    {
        "run_id": "A7SEARCH4",
        "artifact_role": "source_runtime",
        "local_pointer": "",
        "remote_pointer": r"G:\AlphaFactory_CryptoData\research_runtime\a7search4_mixed_constrained_train_aligned_proxy_65k_20260626",
        "status": "source_runtime_may_be_archived",
    },
    {
        "run_id": "A7SEARCH1",
        "artifact_role": "archived_runtime",
        "local_pointer": "",
        "remote_pointer": r"H:\AlphaFactory_CryptoData_archive\research_runtime_archived_20260628\a7search1_cem_uct_ast_policy_bakeoff_20260618",
        "status": "archive_expected",
    },
    {
        "run_id": "A7SEARCH2",
        "artifact_role": "archived_runtime",
        "local_pointer": "",
        "remote_pointer": r"H:\AlphaFactory_CryptoData_archive\research_runtime_archived_20260628\a7search2_diversified_oi_positioning_capped_65k_20260623",
        "status": "archive_expected",
    },
    {
        "run_id": "A7SEARCH3",
        "artifact_role": "archived_runtime",
        "local_pointer": "",
        "remote_pointer": r"H:\AlphaFactory_CryptoData_archive\research_runtime_archived_20260628\a7search3_non_oi_positioning_forced_proxy_65k_20260624",
        "status": "archive_expected",
    },
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def as_float(value: Any, default: float = math.nan) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def as_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def stable_id(*parts: str) -> str:
    text = "|".join(str(part) for part in parts)
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def normalize_row(row: dict[str, str], *, run_id: str, source_type: str, source_path: Path) -> dict[str, Any]:
    expression = row.get("expression") or row.get("formula") or ""
    semantic_pair = row.get("semantic_pair") or row.get("field_families") or ""
    motif = row.get("motif") or row.get("family") or ""
    skeleton_key = row.get("skeleton_key") or skeleton_memory_key(expression)
    expr_key = expression_memory_key(expression)
    hard_reject = as_bool(row.get("hard_reject", "False"))
    gate_pass = as_bool(row.get("gate_pass", "False"))
    proxy_strict_pass = as_bool(row.get("proxy_strict_pass", "False")) or source_type == "strict_pass"
    proxy_near_miss = as_bool(row.get("proxy_near_miss", "False"))
    proxy_selectable = as_bool(row.get("proxy_selectable", "False"))
    hard_reject_reasons = row.get("hard_reject_reasons", "")

    if proxy_strict_pass:
        memory_status = "strict_pass"
    elif source_type == "accepted_prior" and gate_pass and not hard_reject:
        memory_status = "accepted_prior"
    elif hard_reject or (hard_reject_reasons and hard_reject_reasons.lower() != "nan"):
        memory_status = "rejected"
    elif proxy_near_miss or source_type == "selected_or_nearmiss":
        memory_status = "selected_nearmiss"
    elif proxy_selectable:
        memory_status = "selectable_unverified"
    else:
        memory_status = "observed"

    rejection_class = ""
    reasons_lower = hard_reject_reasons.lower()
    if memory_status == "rejected":
        if "control" in reasons_lower:
            rejection_class = "control_dominated"
        elif "lag" in reasons_lower or "stale" in reasons_lower:
            rejection_class = "lag_or_stale_dominated"
        elif "shuffle" in reasons_lower:
            rejection_class = "shuffle_dominated"
        elif "train" in reasons_lower or "overfit" in reasons_lower:
            rejection_class = "train_oos_inconsistent"
        else:
            rejection_class = "other_hard_reject"

    return {
        "memory_id": "mem-" + stable_id(run_id, source_type, expression, row.get("horizon_h", "")),
        "run_id": run_id,
        "source_type": source_type,
        "source_path": str(source_path),
        "blueprint_id": row.get("blueprint_id") or row.get("candidate_id") or "",
        "expression": expression,
        "expression_key": expr_key,
        "skeleton_key": skeleton_key,
        "semantic_pair": semantic_pair,
        "motif": motif,
        "horizon_h": row.get("horizon_h", ""),
        "memory_status": memory_status,
        "rejection_class": rejection_class,
        "hard_reject": str(hard_reject),
        "hard_reject_reasons": hard_reject_reasons,
        "gate_pass": str(gate_pass),
        "proxy_strict_pass": str(proxy_strict_pass),
        "proxy_near_miss": str(proxy_near_miss),
        "proxy_selectable": str(proxy_selectable),
        "overall_reward": as_float(row.get("overall_reward")),
        "proxy_score": as_float(row.get("proxy_score")),
        "train_sortino": as_float(row.get("train_sortino")),
        "validation_sortino": as_float(row.get("validation_sortino")),
        "test_sortino": as_float(row.get("test_sortino")),
        "recent_sortino": as_float(row.get("recent_sortino")),
        "min_oos_floor_sortino": as_float(row.get("min_oos_floor_sortino")),
        "stress_floor_sortino": as_float(row.get("stress_floor_sortino")),
        "recent_control_ratio": as_float(row.get("recent_control_ratio")),
        "recent_shuffle_control_ratio": as_float(row.get("recent_shuffle_control_ratio")),
        "oos_control_dominated_count": as_float(row.get("oos_control_dominated_count"), 0.0),
        "oos_lag_stale_dominated_count": as_float(row.get("oos_lag_stale_dominated_count"), 0.0),
        "oos_shuffle_dominated_count": as_float(row.get("oos_shuffle_dominated_count"), 0.0),
    }


def finite_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    vals = []
    for row in rows:
        value = row.get(key)
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            vals.append(float(value))
    return vals


def max_or_blank(rows: list[dict[str, Any]], key: str) -> Any:
    vals = finite_values(rows, key)
    return max(vals) if vals else ""


def avg_or_blank(rows: list[dict[str, Any]], key: str) -> Any:
    vals = finite_values(rows, key)
    return sum(vals) / len(vals) if vals else ""


def build_cluster_memory(candidate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in candidate_rows:
        groups[(str(row["semantic_pair"]), str(row["motif"]), str(row["skeleton_key"]))].append(row)
    out = []
    for (pair, motif, skeleton), rows in groups.items():
        statuses = Counter(str(row["memory_status"]) for row in rows)
        expressions = sorted({str(row["expression"]) for row in rows if row.get("expression")})
        duplicate_pressure = max(0, len(rows) - 1)
        if statuses.get("strict_pass", 0) > 0:
            next_action = "keep_but_cluster_cap"
        elif statuses.get("rejected", 0) >= max(1, len(rows) // 2):
            next_action = "ban_or_downweight"
        else:
            next_action = "observe_with_cap"
        out.append(
            {
                "cluster_id": "cluster-" + stable_id(pair, motif, skeleton),
                "semantic_pair": pair,
                "motif": motif,
                "skeleton_key": skeleton,
                "record_count": len(rows),
                "unique_expression_count": len(expressions),
                "strict_count": statuses.get("strict_pass", 0),
                "accepted_prior_count": statuses.get("accepted_prior", 0),
                "selected_nearmiss_count": statuses.get("selected_nearmiss", 0),
                "rejected_count": statuses.get("rejected", 0),
                "duplicate_pressure": duplicate_pressure,
                "max_train_sortino": max_or_blank(rows, "train_sortino"),
                "max_min_oos_floor_sortino": max_or_blank(rows, "min_oos_floor_sortino"),
                "max_stress_floor_sortino": max_or_blank(rows, "stress_floor_sortino"),
                "min_recent_control_ratio": min(finite_values(rows, "recent_control_ratio") or [math.nan]),
                "example_expression": expressions[0] if expressions else "",
                "next_action": next_action,
            }
        )
    return sorted(out, key=lambda r: (-int(r["strict_count"]), -int(r["record_count"]), str(r["semantic_pair"])))


def canonicalize_candidates(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    status_rank = {
        "strict_pass": 5,
        "accepted_prior": 4,
        "rejected": 3,
        "selected_nearmiss": 2,
        "selectable_unverified": 1,
        "observed": 0,
    }
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in source_rows:
        groups[(str(row["expression_key"]), str(row.get("horizon_h", "")))].append(row)

    canonical = []
    for rows in groups.values():
        rows_sorted = sorted(
            rows,
            key=lambda r: (
                status_rank.get(str(r.get("memory_status", "")), 0),
                float(r.get("proxy_score")) if isinstance(r.get("proxy_score"), (int, float)) and math.isfinite(float(r.get("proxy_score"))) else -1e9,
                float(r.get("overall_reward")) if isinstance(r.get("overall_reward"), (int, float)) and math.isfinite(float(r.get("overall_reward"))) else -1e9,
            ),
            reverse=True,
        )
        best = dict(rows_sorted[0])
        statuses = Counter(str(row.get("memory_status", "")) for row in rows)
        best["source_record_count"] = len(rows)
        best["source_types"] = ";".join(sorted({str(row.get("source_type", "")) for row in rows}))
        best["run_ids"] = ";".join(sorted({str(row.get("run_id", "")) for row in rows}))
        best["all_memory_statuses"] = ";".join(f"{key}:{value}" for key, value in sorted(statuses.items()))
        best["hard_reject_reasons_all"] = ";".join(
            sorted({str(row.get("hard_reject_reasons", "")) for row in rows if str(row.get("hard_reject_reasons", "")).strip()})
        )
        canonical.append(best)
    return sorted(canonical, key=lambda r: (str(r.get("semantic_pair", "")), str(r.get("motif", "")), str(r.get("expression_key", ""))))


def build_pair_motif_prior(candidate_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in candidate_rows:
        groups[(str(row["semantic_pair"]), str(row["motif"]))].append(row)
    out = []
    for (pair, motif), rows in groups.items():
        statuses = Counter(str(row["memory_status"]) for row in rows)
        strict_count = statuses.get("strict_pass", 0)
        rejected_count = statuses.get("rejected", 0)
        nearmiss_count = statuses.get("selected_nearmiss", 0)
        accepted_count = statuses.get("accepted_prior", 0)
        total = len(rows)
        strict_rate = strict_count / total if total else 0.0
        max_floor = max_or_blank(rows, "min_oos_floor_sortino")
        max_stress = max_or_blank(rows, "stress_floor_sortino")
        min_control_vals = finite_values(rows, "recent_control_ratio")
        min_control = min(min_control_vals) if min_control_vals else ""

        if strict_count >= 2 and (max_floor == "" or float(max_floor) > 0):
            prior_action = "promote_with_cluster_cap"
            search_weight = 2.5
        elif strict_count == 1:
            prior_action = "exploit_lightly_with_diversity_cap"
            search_weight = 1.5
        elif nearmiss_count > 0 and rejected_count < total:
            prior_action = "explore_repaired_variants"
            search_weight = 1.0
        elif rejected_count >= max(1, total // 2):
            prior_action = "downweight_or_ban"
            search_weight = 0.25
        elif accepted_count > 0:
            prior_action = "carry_forward_prior"
            search_weight = 1.25
        else:
            prior_action = "neutral_explore"
            search_weight = 0.75

        out.append(
            {
                "semantic_pair": pair,
                "motif": motif,
                "record_count": total,
                "strict_count": strict_count,
                "accepted_prior_count": accepted_count,
                "selected_nearmiss_count": nearmiss_count,
                "rejected_count": rejected_count,
                "strict_rate": strict_rate,
                "avg_train_sortino": avg_or_blank(rows, "train_sortino"),
                "max_train_sortino": max_or_blank(rows, "train_sortino"),
                "max_min_oos_floor_sortino": max_floor,
                "max_stress_floor_sortino": max_stress,
                "min_recent_control_ratio": min_control,
                "prior_action": prior_action,
                "search_weight": search_weight,
            }
        )
    return sorted(out, key=lambda r: (-float(r["search_weight"]), -int(r["strict_count"]), str(r["semantic_pair"]), str(r["motif"])))


def make_report(summary: dict[str, Any], top_priors: list[dict[str, Any]], top_clusters: list[dict[str, Any]]) -> str:
    def lines_for(rows: list[dict[str, Any]], cols: list[str], limit: int = 20) -> list[str]:
        if not rows:
            return ["`<empty>`"]
        header = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        body = []
        for row in rows[:limit]:
            body.append("| " + " | ".join(str(row.get(col, "")).replace("|", "\\|") for col in cols) + " |")
        return [header, sep, *body]

    out = [
        "# CRYPTO A7MEM-0 Search Memory Registry 20260628",
        "",
        "## Decision",
        "",
        f"`{summary['decision']}`",
        "",
        "Boundary: search memory and next-search prior only. This does not authorize alpha proof, shadow, paper, or live.",
        "",
        "## Why This Exists",
        "",
        "Crypto search memory existed as a low-level expression/skeleton smoke, but large-search stages used ad-hoc priors and local skeleton caps instead of a single mandatory memory registry.",
        "A7MEM-0 makes the search memory explicit and machine-readable before the next large search.",
        "",
        "## Counts",
        "",
        f"- source_files_seen: `{summary['source_files_seen']}`",
        f"- source_files_missing: `{summary['source_files_missing']}`",
        f"- source_record_rows: `{summary['source_record_rows']}`",
        f"- candidate_memory_rows: `{summary['candidate_memory_rows']}`",
        f"- strict_rows: `{summary['strict_rows']}`",
        f"- accepted_prior_rows: `{summary['accepted_prior_rows']}`",
        f"- rejected_rows: `{summary['rejected_rows']}`",
        f"- formula_clusters: `{summary['formula_clusters']}`",
        f"- pair_motif_priors: `{summary['pair_motif_priors']}`",
        "",
        "## Mandatory Next-Search Gate",
        "",
        "EVALRESET blocks this memory registry from authorizing the next search while candidate inputs contain spent/OOS-derived feedback.",
        "A future prior requires an unspent inner-validation contract and a passing candidate-feedback guard.",
        "",
        "## Top Pair/Motif Priors",
        "",
        *lines_for(top_priors, ["semantic_pair", "motif", "strict_count", "rejected_count", "prior_action", "search_weight"], 20),
        "",
        "## Top Formula Clusters",
        "",
        *lines_for(top_clusters, ["semantic_pair", "motif", "record_count", "strict_count", "duplicate_pressure", "next_action"], 20),
        "",
        "## Outputs",
        "",
        "- `a7mem0_search_run_registry.csv`",
        "- `a7mem0_candidate_memory.csv`",
        "- `a7mem0_formula_cluster_memory.csv`",
        "- `a7mem0_rejection_memory.csv`",
        "- `a7mem0_pair_motif_prior.csv`",
        "- `a7mem0_archive_pointer_map.csv`",
        "- `a7mem0_next_search_prior.json`",
        "- `a7mem0_manifest.json`",
    ]
    return "\n".join(out) + "\n"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    run_registry = []
    candidate_rows = []
    blocked_sources: list[dict[str, Any]] = []
    for source in SOURCE_FILES:
        path = Path(source["path"])
        exists = path.exists()
        rows = read_csv(path)
        source_row_count = len(rows)
        feedback_status = "PASS"
        try:
            assert_candidate_feedback_records_allowed(
                rows,
                context=f"a7mem0.ingest.{source['run_id']}.{source['source_type']}",
            )
        except EvaluationAccessViolation as exc:
            blocked_sources.append(exc.as_dict() | {"path": str(path)})
            feedback_status = "BLOCKED_EVALRESET_CANDIDATE_FEEDBACK"
            rows = []
        run_registry.append(
            {
                "run_id": source["run_id"],
                "source_type": source["source_type"],
                "path": str(path),
                "exists": str(exists),
                "source_row_count": source_row_count,
                "ingested_row_count": len(rows),
                "candidate_feedback_status": feedback_status,
                "sha256": sha256_file(path) if exists else "",
                "size_bytes": path.stat().st_size if exists else "",
                "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat() if exists else "",
                "notes": source["notes"],
            }
        )
        for row in rows:
            if row.get("expression") or row.get("formula"):
                candidate_rows.append(normalize_row(row, run_id=source["run_id"], source_type=source["source_type"], source_path=path))

    # One expression can appear in strict and selected files. Preserve source records, but make decisions on canonical rows.
    seen_expr = Counter(row["expression_key"] for row in candidate_rows)
    for row in candidate_rows:
        row["expression_duplicate_count"] = seen_expr[row["expression_key"]]

    source_record_rows = candidate_rows
    candidate_rows = canonicalize_candidates(source_record_rows)
    cluster_rows = build_cluster_memory(candidate_rows)
    rejection_rows = [row for row in candidate_rows if row["memory_status"] == "rejected" or row["rejection_class"]]
    prior_rows = build_pair_motif_prior(candidate_rows)
    archive_rows = ARCHIVE_POINTERS

    memory_decision = (
        "HOLD_EVALRESET_SPENT_EVALUATION_FEEDBACK_BLOCKED"
        if blocked_sources
        else "PASS_A7MEM0_SEARCH_MEMORY_REGISTRY_BUILT"
    )
    next_prior = {
        "object_id": "a7mem0_next_search_prior",
        "created_at": now_utc(),
        "stage": STAGE,
        "decision": memory_decision,
        "required_for_next_large_search": True,
        "search_authorized": False,
        "candidate_feedback_guard": blocked_sources or [{"status": "PASS"}],
        "memory_runtime": str(RUNTIME),
        "candidate_memory": str(RUNTIME / "a7mem0_candidate_memory.csv"),
        "source_record_memory": str(RUNTIME / "a7mem0_source_record_memory.csv"),
        "cluster_memory": str(RUNTIME / "a7mem0_formula_cluster_memory.csv"),
        "pair_motif_prior": str(RUNTIME / "a7mem0_pair_motif_prior.csv"),
        "promote_pair_motifs": [
            {
                "semantic_pair": row["semantic_pair"],
                "motif": row["motif"],
                "search_weight": row["search_weight"],
                "reason": row["prior_action"],
            }
            for row in prior_rows
            if row["prior_action"] in {"promote_with_cluster_cap", "exploit_lightly_with_diversity_cap"}
        ],
        "downweight_pair_motifs": [
            {
                "semantic_pair": row["semantic_pair"],
                "motif": row["motif"],
                "search_weight": row["search_weight"],
                "reason": row["prior_action"],
            }
            for row in prior_rows
            if row["prior_action"] == "downweight_or_ban"
        ],
        "cluster_caps": {
            "max_same_expression_key": 1,
            "max_same_skeleton_key_per_shard": 2,
            "max_same_semantic_pair_motif_per_shard": 16,
            "require_cluster_memory_loaded": True,
        },
        "hard_ban_rejection_classes": [
            "control_dominated",
            "lag_or_stale_dominated",
            "shuffle_dominated",
            "train_oos_inconsistent",
        ],
    }

    summary = {
        "object_id": "crypto_a7mem0_search_memory_registry",
        "created_at": now_utc(),
        "decision": memory_decision,
        "source_files_seen": sum(1 for row in run_registry if row["exists"] == "True"),
        "source_files_missing": sum(1 for row in run_registry if row["exists"] != "True"),
        "candidate_memory_rows": len(candidate_rows),
        "source_record_rows": len(source_record_rows),
        "strict_rows": sum(1 for row in candidate_rows if row["memory_status"] == "strict_pass"),
        "accepted_prior_rows": sum(1 for row in candidate_rows if row["memory_status"] == "accepted_prior"),
        "rejected_rows": len(rejection_rows),
        "formula_clusters": len(cluster_rows),
        "pair_motif_priors": len(prior_rows),
        "next_search_requires_a7mem_prior": True,
        "candidate_feedback_guard": blocked_sources or [{"status": "PASS"}],
        "outputs": {
            "search_run_registry": str(RUNTIME / "a7mem0_search_run_registry.csv"),
            "candidate_memory": str(RUNTIME / "a7mem0_candidate_memory.csv"),
            "source_record_memory": str(RUNTIME / "a7mem0_source_record_memory.csv"),
            "formula_cluster_memory": str(RUNTIME / "a7mem0_formula_cluster_memory.csv"),
            "rejection_memory": str(RUNTIME / "a7mem0_rejection_memory.csv"),
            "pair_motif_prior": str(RUNTIME / "a7mem0_pair_motif_prior.csv"),
            "archive_pointer_map": str(RUNTIME / "a7mem0_archive_pointer_map.csv"),
            "next_search_prior": str(RUNTIME / "a7mem0_next_search_prior.json"),
            "report": str(REPORT),
        },
    }

    write_csv(
        RUNTIME / "a7mem0_search_run_registry.csv",
        run_registry,
        [
            "run_id",
            "source_type",
            "path",
            "exists",
            "source_row_count",
            "ingested_row_count",
            "candidate_feedback_status",
            "sha256",
            "size_bytes",
            "mtime_utc",
            "notes",
        ],
    )
    candidate_cols = [
        "memory_id",
        "run_id",
        "source_type",
        "blueprint_id",
        "semantic_pair",
        "motif",
        "horizon_h",
        "memory_status",
        "rejection_class",
        "expression_key",
        "skeleton_key",
        "expression_duplicate_count",
        "source_record_count",
        "source_types",
        "run_ids",
        "all_memory_statuses",
        "hard_reject_reasons_all",
        "train_sortino",
        "validation_sortino",
        "test_sortino",
        "recent_sortino",
        "min_oos_floor_sortino",
        "stress_floor_sortino",
        "recent_control_ratio",
        "recent_shuffle_control_ratio",
        "hard_reject",
        "hard_reject_reasons",
        "gate_pass",
        "proxy_strict_pass",
        "proxy_near_miss",
        "proxy_selectable",
        "expression",
        "source_path",
    ]
    write_csv(RUNTIME / "a7mem0_source_record_memory.csv", source_record_rows, candidate_cols)
    write_csv(RUNTIME / "a7mem0_candidate_memory.csv", candidate_rows, candidate_cols)
    write_csv(
        RUNTIME / "a7mem0_formula_cluster_memory.csv",
        cluster_rows,
        [
            "cluster_id",
            "semantic_pair",
            "motif",
            "skeleton_key",
            "record_count",
            "unique_expression_count",
            "strict_count",
            "accepted_prior_count",
            "selected_nearmiss_count",
            "rejected_count",
            "duplicate_pressure",
            "max_train_sortino",
            "max_min_oos_floor_sortino",
            "max_stress_floor_sortino",
            "min_recent_control_ratio",
            "example_expression",
            "next_action",
        ],
    )
    write_csv(RUNTIME / "a7mem0_rejection_memory.csv", rejection_rows, candidate_cols)
    write_csv(
        RUNTIME / "a7mem0_pair_motif_prior.csv",
        prior_rows,
        [
            "semantic_pair",
            "motif",
            "record_count",
            "strict_count",
            "accepted_prior_count",
            "selected_nearmiss_count",
            "rejected_count",
            "strict_rate",
            "avg_train_sortino",
            "max_train_sortino",
            "max_min_oos_floor_sortino",
            "max_stress_floor_sortino",
            "min_recent_control_ratio",
            "prior_action",
            "search_weight",
        ],
    )
    write_csv(
        RUNTIME / "a7mem0_archive_pointer_map.csv",
        archive_rows,
        ["run_id", "artifact_role", "local_pointer", "remote_pointer", "status"],
    )
    write_json(RUNTIME / "a7mem0_next_search_prior.json", next_prior)
    write_json(RUNTIME / "a7mem0_manifest.json", summary)
    REPORT.write_text(make_report(summary, prior_rows, cluster_rows), encoding="utf-8")
    print(summary["decision"])


if __name__ == "__main__":
    main()
