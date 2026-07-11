from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import inspect
import io
import json
import shutil
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import scripts.crypto_nextgen_epoch0 as epoch0
import scripts.crypto_nextgen_epoch1 as epoch1
from alphafactory_crypto.b1s_canary import rank_weights
from alphafactory_crypto.nextgen_epoch import (
    ProgramSpec, complexity, effective_count, materialize_program, multiobjective_evaluate,
    pareto_front, signal_record,
)
from alphafactory_crypto.search_revision import (
    adaptive_verdict, admit_full_identity, concentration_metrics, development_feedback,
    partition_exact_identity_owners,
)


OUTPUT_ROOT = REPO / "runtime/nextgen_epoch1r_20260712"
PACK = OUTPUT_ROOT / "proposal_pack.jsonl.gz"
PACK_MANIFEST = OUTPUT_ROOT / "proposal_pack_manifest.json"
FULL_IDENTITIES = OUTPUT_ROOT / "full_identity_records.jsonl.gz"
CAPACITY_TABLE = OUTPUT_ROOT / "admission_capacity_table.csv"
ASSIGNMENTS = OUTPUT_ROOT / "admission_assignments.csv"
PREFLIGHT = OUTPUT_ROOT / "admission_preflight_manifest.json"
FROZEN = OUTPUT_ROOT / "epoch1r_frozen_design_manifest.json"
RUN = OUTPUT_ROOT / "epoch1r_run_manifest.json"
FAILURE = OUTPUT_ROOT / "epoch1r_failure.json"
TEST_EVIDENCE = OUTPUT_ROOT / "epoch1r_test_output.txt"
OLD_FROZEN = epoch1.FROZEN
FAILED_SUBJECT = "403b3519773e18c38033b2eaeaf404c98320595a"
FIXED_SEEDS = (3701, 3709)
MAIN_STRICT_MAX = 1440
BBO_STRICT_MAX = 96


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=REPO, text=True, capture_output=True, check=check)
    return result.stdout.strip()


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_payload(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(raw).hexdigest().upper()


def write_jsonl_gz(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as text:
                for row in rows:
                    text.write(json.dumps(row, sort_keys=True, separators=(",", ":"), default=str) + "\n")


def read_jsonl_gz(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def source_node_hash(path: Path, names: Iterable[str], ref: str | None = None) -> str:
    source = git("show", f"{ref}:{relative(path)}") if ref else path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    wanted = set(names)
    nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in wanted]
    return sha256_payload([ast.dump(node, include_attributes=False) for node in nodes])


def validate_unchanged_upstream() -> dict[str, Any]:
    old = load_json(OLD_FROZEN)
    if old["budget"]["total_proposals"] != 32768 or tuple(old["budget"]["fixed_seeds"]) != FIXED_SEEDS:
        raise ValueError("old Epoch-1 proposal budget or seeds drifted")
    if old["budget"]["strict_per_arm"] != 1536 or old["budget"]["proposals_by_lane"] != (
        {lane: 2560 for lane in epoch1.MAIN_LANES} | {epoch1.BBO_LANES[0]: 2048}
    ):
        raise ValueError("old Epoch-1 lane budget drifted")
    unchanged_paths = [
        epoch1.CONFIG, epoch1.MECHANISMS, REPO / "alphafactory_crypto/nextgen_epoch.py",
        REPO / "scripts/crypto_nextgen_epoch0.py", REPO / "scripts/crypto_nextgen_epoch1.py",
    ]
    for path in unchanged_paths:
        expected = old["contracts_sha256"][relative(path)]
        if sha256_file(path) != expected:
            raise ValueError(f"forbidden upstream contract drift: {relative(path)}")
    protected = (
        "development_feedback", "concentration_metrics", "adaptive_verdict", "epoch0_failure_matrix",
        "DevelopmentFeedback",
    )
    current_hash = source_node_hash(epoch1.MODULE, protected)
    failed_hash = source_node_hash(epoch1.MODULE, protected, FAILED_SUBJECT)
    if current_hash != failed_hash:
        raise ValueError("reward/objective/adaptive logic changed outside narrow admission repair")
    return {
        "old_frozen_manifest_sha256": old["frozen_manifest_sha256"],
        "unchanged_contracts": {relative(path): sha256_file(path) for path in unchanged_paths},
        "protected_search_logic_ast_sha256": current_hash,
        "reward_contract": old["reward_contract"],
        "survivor_contract": old["survivor_contract"],
        "lane_specs": old["lane_specs"],
        "budget": old["budget"],
        "matched_controls": old["matched_controls"],
        "capability_matrix": old["capability_matrix"],
        "benchmark_contract": old["benchmark_contract"],
    }


def generate_pack() -> dict[str, Any]:
    guard = validate_unchanged_upstream()
    started = time.perf_counter()
    registry = epoch1.load_json(epoch1.MECHANISMS)
    main = epoch0.load_main_panel()
    bbo = epoch0.load_bbo_panel(main)
    full_panels = {"main": main, "bbo_micro": bbo}
    sketch_panels = {"main": epoch0.sketch_panel(main, 4), "bbo_micro": epoch0.sketch_panel(bbo, 2)}
    _, best_full = epoch0._run_benchmarks(full_panels, 5.0, 5)
    best_sketch = {"main": best_full["main"][::4], "bbo_micro": best_full["bbo_micro"][::2]}
    old = load_json(OLD_FROZEN)
    cache: dict[Any, Any] = {}
    rows: list[dict[str, Any]] = []
    lane_runtime: dict[str, float] = {}
    feedback_queries = 0
    for panel_id, lanes in (("main", epoch1.MAIN_LANES), ("bbo_micro", epoch1.BBO_LANES)):
        for lane in lanes:
            lane_started = time.perf_counter()
            per_seed = int(old["budget"]["proposals_by_lane"][lane]) // 2
            lane_ordinal = 0
            for seed in FIXED_SEEDS:
                specs, evaluations, queries = epoch1._generate_lane(
                    registry, lane, panel_id, seed, per_seed, 256,
                    sketch_panels[panel_id], best_sketch[panel_id], cache,
                )
                feedback_queries += len(queries)
                for spec, (record, feedback) in zip(specs, evaluations):
                    proposal_id = epoch1.candidate_identity(spec)
                    candidate = {
                        "proposal_id": proposal_id, "panel_id": panel_id, "lane_id": lane,
                        "algorithm": spec.algorithm, "seed": spec.seed, "ordinal": spec.ordinal,
                        "lane_ordinal": lane_ordinal, "mechanism_id": spec.mechanism_id,
                        "economic_hypothesis": spec.economic_hypothesis, "primitive": spec.primitive,
                        "interaction": spec.interaction, "parent_identity": spec.parent_identity,
                        "canonical_expression": epoch1.canonical_program_json(spec),
                        "canonical_identity": epoch1.program_identity(spec),
                        "sketch_exact_identity": record.exact_identity,
                        "activation_identity": record.activation_identity,
                        "behaviour_cluster": record.behaviour_cluster,
                        "proxy_score_diagnostic_only": record.proxy_score,
                        "legal": record.legal, "failure_reason": record.failure_reason,
                        "early_gate_pass": feedback["early_gate_pass"],
                        "gate_reasons": feedback["gate_reasons"],
                        "survivor_near_miss_score": feedback["survivor_near_miss_score"],
                        "development_scalar": feedback["limited_scalar"],
                        "feedback_net_lcb": feedback["net_lcb"],
                        "feedback_worst_block": feedback["worst_block"],
                        "feedback_turnover": feedback["turnover_mean"],
                        "feedback_benchmark_increment_lcb": feedback["benchmark_increment_lcb"],
                        "feedback_permission": "EPOCH1R_RUNTIME_ONLY_NO_MEMORY_NO_PROMOTION",
                    }
                    rows.append({"proposal_id": proposal_id, "spec": asdict(spec), "candidate": candidate})
                    lane_ordinal += 1
            lane_runtime[f"{panel_id}/{lane}"] = time.perf_counter() - lane_started
    if len(rows) != 32768 or len({row["proposal_id"] for row in rows}) != 32768:
        raise ValueError("proposal pack count or candidate identity drift")
    write_jsonl_gz(PACK, rows)
    manifest = {
        "experiment_id": "20260712_crypto_nextgen_epoch1r_001",
        "status": "EPOCH1R_PROPOSAL_PACK_FROZEN_PRE_STRICT",
        "objective": "regenerate the unchanged Epoch-1 proposal stream and isolate the narrow admission repair",
        "repo_sha": git("rev-parse", "HEAD"), "failed_epoch1_subject": FAILED_SUBJECT,
        "proposal_rows": len(rows), "proposal_pack": relative(PACK), "proposal_pack_sha256": sha256_file(PACK),
        "proposal_pack_content_sha256": sha256_payload(rows), "fixed_seeds": list(FIXED_SEEDS),
        "lane_budgets": guard["budget"]["proposals_by_lane"], "adaptive_feedback_queries": feedback_queries,
        "lane_runtime_seconds": lane_runtime, "runtime_seconds": time.perf_counter() - started,
        "upstream_contract_guard": guard, "strict_evaluations": 0,
        "forward_read": False, "candidate_promotion": False, "cross_epoch_memory": False,
        "reproducibility": "DETERMINISTIC_GZIP_MTIME_ZERO_SORTED_JSON_KEYS_FIXED_SEEDS",
        "continuation": "run admission-only preflight; do not perform strict evaluation before preflight passes",
    }
    PACK_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "proposals": len(rows), "pack_sha256": manifest["proposal_pack_sha256"], "runtime_seconds": manifest["runtime_seconds"]}, indent=2))
    return manifest


def load_pack() -> tuple[list[dict[str, Any]], pd.DataFrame, dict[str, ProgramSpec]]:
    manifest = load_json(PACK_MANIFEST)
    if sha256_file(PACK) != manifest["proposal_pack_sha256"]:
        raise ValueError("proposal pack hash drift")
    rows = read_jsonl_gz(PACK)
    if len(rows) != 32768 or sha256_payload(rows) != manifest["proposal_pack_content_sha256"]:
        raise ValueError("proposal pack content drift")
    candidates = pd.DataFrame([row["candidate"] for row in rows])
    specs = {row["proposal_id"]: ProgramSpec(**row["spec"]) for row in rows}
    return rows, candidates, specs


def preflight() -> dict[str, Any]:
    started = time.perf_counter()
    if PREFLIGHT.exists() and "preflight_revision" not in load_json(PREFLIGHT):
        archive = OUTPUT_ROOT / "diagnostic_sequential_preflight"
        archive.mkdir(parents=True, exist_ok=True)
        for path in (FULL_IDENTITIES, CAPACITY_TABLE, ASSIGNMENTS, PREFLIGHT):
            if path.exists():
                shutil.copy2(path, archive / path.name)
    _, candidates, specs = load_pack()
    old = load_json(OLD_FROZEN)
    main = epoch0.load_main_panel(include_target=False)
    bbo = epoch0.load_bbo_panel(main, include_target=False)
    panels = {"main": main, "bbo_micro": bbo}
    by_id = candidates.set_index("proposal_id", drop=False)
    strat_pool: list[tuple[str, str]] = []
    for (panel, lane), group in candidates[candidates.legal].groupby(["panel_id", "lane_id"], sort=True):
        quota = int(old["budget"]["strict_by_lane"][lane])
        strat_pool += [("STRATIFIED_ADMISSION", pid) for pid in epoch1._round_robin_pool(group, quota * 2)]
    global_pool: list[tuple[str, str]] = []
    for panel, quota in (("main", MAIN_STRICT_MAX), ("bbo_micro", BBO_STRICT_MAX)):
        group = candidates[(candidates.panel_id == panel) & candidates.legal].nlargest(quota * 2, "development_scalar")
        global_pool += [("GLOBAL_TOP_K_CONTROL", pid) for pid in group.proposal_id]
    full_records: dict[str, dict[str, Any]] = {}
    for _, proposal_id in strat_pool + global_pool:
        if proposal_id in full_records:
            continue
        base = by_id.loc[proposal_id]
        spec = specs[proposal_id]
        panel = panels[str(base.panel_id)]
        record, _ = signal_record(spec, materialize_program(spec, panel), panel, np.ones(len(panel.timestamps), dtype=bool))
        full_records[proposal_id] = asdict(record)
    write_jsonl_gz(FULL_IDENTITIES, ({"proposal_id": pid, **record} for pid, record in sorted(full_records.items())))
    capacity_rows: list[dict[str, Any]] = []
    assignments: list[dict[str, Any]] = []
    grouped = {(panel, lane): group for (panel, lane), group in candidates.groupby(["panel_id", "lane_id"], sort=True)}
    expected_groups = [("main", lane) for lane in epoch1.MAIN_LANES] + [("bbo_micro", lane) for lane in epoch1.BBO_LANES]
    raw_rows_by_group: dict[tuple[str, str], list[dict[str, Any]]] = {}
    exact_before_by_group: dict[tuple[str, str], set[str]] = {}
    for panel, lane in expected_groups:
        group = grouped[(panel, lane)]
        pool_ids = [pid for arm, pid in strat_pool if arm == "STRATIFIED_ADMISSION" and by_id.loc[pid].panel_id == panel and by_id.loc[pid].lane_id == lane]
        exact_before = {full_records[pid]["exact_identity"] for pid in pool_ids if full_records[pid]["exact_identity"]}
        rows = []
        for pid in pool_ids:
            record = full_records[pid]
            exact = record["exact_identity"]
            if not exact:
                continue
            base = by_id.loc[pid]
            rows.append({
                "proposal_id": pid, "full_exact_identity": exact, "mechanism_id": base.mechanism_id,
                "parent_identity": base.parent_identity, "behaviour_cluster": record["behaviour_cluster"],
                "ordinal": int(base.ordinal),
            })
        raw_rows_by_group[(panel, lane)] = rows
        exact_before_by_group[(panel, lane)] = exact_before
    owned_rows_by_group: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for panel, lanes in (("main", epoch1.MAIN_LANES), ("bbo_micro", epoch1.BBO_LANES)):
        lane_rows = {lane: raw_rows_by_group[(panel, lane)] for lane in lanes}
        quotas = {lane: int(old["budget"]["strict_by_lane"][lane]) for lane in lanes}
        owned = partition_exact_identity_owners(lane_rows, quotas, lanes)
        for lane in lanes:
            owned_rows_by_group[(panel, lane)] = owned[lane]
    for panel, lane in expected_groups:
        group = grouped[(panel, lane)]
        quota = int(old["budget"]["strict_by_lane"][lane])
        rows = owned_rows_by_group[(panel, lane)]
        outcome = admit_full_identity(rows, quota)
        for rank, pid in enumerate(outcome.admitted_ids):
            exact = full_records[pid]["exact_identity"]
            assignments.append({
                "panel_id": panel, "lane_id": lane, "arm": "STRATIFIED_ADMISSION",
                "proposal_id": pid, "rank": rank, "full_exact_identity": exact,
            })
        capacity_rows.append({
            "panel_id": panel, "lane_id": lane, "proposal_count": len(group),
            "legal_count": int(group.legal.sum()), "exact_identity_count": len(exact_before_by_group[(panel, lane)]),
            "representative_count": outcome.plan.identity_capacity,
            "mechanism_count": outcome.plan.mechanism_family_count, "requested_quota": quota,
            "feasible_quota": outcome.capacity.feasible_capacity,
            "assigned_quota": outcome.capacity.assigned_capacity,
            "natural_underfill": outcome.capacity.natural_underfill,
            "underfill_reason": outcome.capacity.reason,
        })
    for panel, quota in (("main", MAIN_STRICT_MAX), ("bbo_micro", BBO_STRICT_MAX)):
        seen: set[str] = set()
        rank = 0
        for arm, pid in global_pool:
            if arm != "GLOBAL_TOP_K_CONTROL" or by_id.loc[pid].panel_id != panel:
                continue
            exact = full_records[pid]["exact_identity"]
            if not exact or exact in seen or rank >= quota:
                continue
            seen.add(exact)
            assignments.append({
                "panel_id": panel, "lane_id": by_id.loc[pid].lane_id, "arm": arm,
                "proposal_id": pid, "rank": rank, "full_exact_identity": exact,
            })
            rank += 1
        capacity_rows.append({
            "panel_id": panel, "lane_id": "__GLOBAL_TOP_K_CONTROL__", "proposal_count": int((candidates.panel_id == panel).sum()),
            "legal_count": int(((candidates.panel_id == panel) & candidates.legal).sum()),
            "exact_identity_count": len(seen), "representative_count": len(seen),
            "mechanism_count": int(candidates.loc[(candidates.panel_id == panel) & candidates.proposal_id.isin([pid for arm, pid in global_pool if arm == "GLOBAL_TOP_K_CONTROL"]), "mechanism_id"].nunique()),
            "requested_quota": quota, "feasible_quota": min(quota, len(seen)), "assigned_quota": rank,
            "natural_underfill": rank < quota,
            "underfill_reason": "LEGAL_EXACT_IDENTITY_CAPACITY" if rank < quota else "",
        })
    capacity = pd.DataFrame(capacity_rows)
    assignment = pd.DataFrame(assignments, columns=["panel_id", "lane_id", "arm", "proposal_id", "rank", "full_exact_identity"])
    if len(capacity) != len(expected_groups) + 2:
        raise ValueError("not all panel/lane capacity records were produced")
    if (capacity.assigned_quota > capacity.feasible_quota).any():
        raise ValueError("assigned quota exceeds feasible quota")
    duplicate = assignment.groupby(["panel_id", "arm"])["full_exact_identity"].apply(lambda values: values.duplicated().any())
    if duplicate.any():
        raise ValueError("duplicate exact identity in strict assignment")
    enabled_controls = set(epoch1.MATCHED.values())
    control_counts = assignment[(assignment.panel_id == "main") & (assignment.arm == "STRATIFIED_ADMISSION")].groupby("lane_id").size().to_dict()
    if any(int(control_counts.get(lane, 0)) == 0 for lane in enabled_controls):
        raise ValueError("matched-control lane starved by exact-identity ownership")
    expected_total = int(capacity.assigned_quota.sum())
    if len(assignment) != expected_total:
        raise ValueError("assignment total/capacity table mismatch")
    capacity.to_csv(CAPACITY_TABLE, index=False)
    assignment.to_csv(ASSIGNMENTS, index=False)
    manifest = {
        "experiment_id": "20260712_crypto_nextgen_epoch1r_001",
        "status": "PASS_EPOCH1R_ADMISSION_ONLY_PREFLIGHT", "preflight_revision": "FAIR_EXACT_IDENTITY_OWNERSHIP_V1",
        "proposal_pack_sha256": sha256_file(PACK),
        "full_identity_records_sha256": sha256_file(FULL_IDENTITIES),
        "capacity_table_sha256": sha256_file(CAPACITY_TABLE), "assignment_sha256": sha256_file(ASSIGNMENTS),
        "panel_lane_rows": len(capacity), "strict_assignment_total": len(assignment),
        "stratified_assignment_total": int((assignment.arm == "STRATIFIED_ADMISSION").sum()),
        "global_assignment_total": int((assignment.arm == "GLOBAL_TOP_K_CONTROL").sum()),
        "natural_underfill_rows": int(capacity.natural_underfill.sum()),
        "empty_lane_rows": int((capacity.representative_count == 0).sum()),
        "hard_gates": {
            "all_panel_lanes_recorded": True, "empty_lanes_returned": True,
            "assigned_lte_feasible": True, "exact_identities_unique_per_panel_arm": True,
            "assignment_total_bound": True, "admission_exception_absent": True,
            "matched_controls_non_empty": True,
        },
        "strict_evaluations": 0, "return_label_read_for_preflight": False,
        "forward_read": False, "candidate_promotion": False, "cross_epoch_memory": False,
        "runtime_seconds": time.perf_counter() - started,
    }
    PREFLIGHT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return manifest


def freeze() -> dict[str, Any]:
    guard = validate_unchanged_upstream()
    pack = load_json(PACK_MANIFEST)
    pre = load_json(PREFLIGHT)
    if pre["status"] != "PASS_EPOCH1R_ADMISSION_ONLY_PREFLIGHT" or not all(pre["hard_gates"].values()):
        raise RuntimeError("admission-only preflight has not passed")
    if subprocess.run(["git", "diff", "--quiet"], cwd=REPO).returncode:
        raise RuntimeError("Epoch-1R freeze requires committed tracked implementation and preflight artifacts")
    if not TEST_EVIDENCE.exists():
        raise RuntimeError("Epoch-1R test evidence missing")
    payload = {
        "experiment_id": "20260712_crypto_nextgen_epoch1r_001", "status": "EPOCH1R_DESIGN_FROZEN_NOT_STARTED",
        "objective": "strictly isolate empty-admission semantics repair while preserving all Epoch-1 search contracts",
        "repo_sha": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
        "failed_epoch1_subject": FAILED_SUBJECT, "failed_epoch1_manifest_preserved": relative(epoch1.FROZEN),
        "failed_epoch1_failure_preserved": relative(epoch1.FAILURE),
        "proposal_pack": relative(PACK), "proposal_pack_sha256": sha256_file(PACK),
        "proposal_pack_content_sha256": pack["proposal_pack_content_sha256"],
        "admission_code_sha256": sha256_file(epoch1.MODULE), "test_evidence": relative(TEST_EVIDENCE),
        "test_evidence_sha256": sha256_file(TEST_EVIDENCE), "capacity_table": relative(CAPACITY_TABLE),
        "capacity_table_sha256": sha256_file(CAPACITY_TABLE), "assignment": relative(ASSIGNMENTS),
        "assignment_sha256": sha256_file(ASSIGNMENTS), "full_identity_records_sha256": sha256_file(FULL_IDENTITIES),
        "strict_assignment_total": pre["strict_assignment_total"],
        "stratified_assignment_total": pre["stratified_assignment_total"],
        "global_assignment_total": pre["global_assignment_total"],
        "natural_underfill_rows": pre["natural_underfill_rows"], "repair_contract": {
            "scope": "EMPTY_REPRESENTATIVE_SET_ONLY", "no_legal_reason": "NO_LEGAL_EXACT_IDENTITIES",
            "empty_feasible_capacity": 0, "empty_assigned_capacity": 0,
            "budget_reallocation": False, "quota_relaxation": False,
        },
        "reward_contract": guard["reward_contract"], "survivor_contract": guard["survivor_contract"],
        "lane_specs": guard["lane_specs"], "budget": guard["budget"], "fixed_seeds": list(FIXED_SEEDS),
        "matched_controls": guard["matched_controls"], "capability_matrix": guard["capability_matrix"],
        "benchmark_contract": guard["benchmark_contract"], "upstream_contract_guard": guard,
        "commands": {"run": "python scripts/crypto_nextgen_epoch1r.py run", "check": "python scripts/crypto_nextgen_epoch1r.py check"},
        "estimated_cost_time": "strict-only continuation estimated under 30 minutes",
        "reproducibility": "HASHED_PACK_CAPACITY_ASSIGNMENT_CODE_TESTS_CONTRACTS_FIXED_SEEDS",
        "search_started": False, "strict_evaluation_started": False, "forward_read": False,
        "candidate_promotion": False, "cross_epoch_memory": False, "online_contract_changed": False,
    }
    payload["frozen_manifest_sha256"] = sha256_payload(payload)
    FROZEN.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "repo_sha": payload["repo_sha"], "strict_assignment_total": payload["strict_assignment_total"], "frozen_manifest_sha256": payload["frozen_manifest_sha256"]}, indent=2))
    return payload


def verify_frozen() -> dict[str, Any]:
    frozen = load_json(FROZEN)
    recorded = frozen.pop("frozen_manifest_sha256")
    if sha256_payload(frozen) != recorded:
        raise ValueError("Epoch-1R frozen manifest hash drift")
    frozen["frozen_manifest_sha256"] = recorded
    if subprocess.run(["git", "merge-base", "--is-ancestor", frozen["repo_sha"], "HEAD"], cwd=REPO).returncode:
        raise ValueError("Epoch-1R frozen repo subject is not an ancestor")
    checks = {
        PACK: frozen["proposal_pack_sha256"], epoch1.MODULE: frozen["admission_code_sha256"],
        TEST_EVIDENCE: frozen["test_evidence_sha256"], CAPACITY_TABLE: frozen["capacity_table_sha256"],
        ASSIGNMENTS: frozen["assignment_sha256"], FULL_IDENTITIES: frozen["full_identity_records_sha256"],
    }
    for path, expected in checks.items():
        if sha256_file(path) != expected:
            raise ValueError(f"Epoch-1R frozen artifact drift: {relative(path)}")
    validate_unchanged_upstream()
    return frozen


def run() -> dict[str, Any]:
    frozen = verify_frozen()
    started = time.perf_counter()
    _, candidates, specs = load_pack()
    by_id = candidates.set_index("proposal_id", drop=False)
    identities = {row["proposal_id"]: row for row in read_jsonl_gz(FULL_IDENTITIES)}
    assignment = pd.read_csv(ASSIGNMENTS)
    if len(assignment) != frozen["strict_assignment_total"]:
        raise ValueError("frozen strict assignment count drift")
    main = epoch0.load_main_panel()
    bbo = epoch0.load_bbo_panel(main)
    panels = {"main": main, "bbo_micro": bbo}
    benchmarks, best_full = epoch0._run_benchmarks(panels, 5.0, 5)
    preliminary: list[dict[str, Any]] = []
    for row in assignment.itertuples():
        base = by_id.loc[row.proposal_id]
        record = identities[row.proposal_id]
        preliminary.append({
            "arm": row.arm, "proposal_id": row.proposal_id, "panel_id": row.panel_id,
            "lane_id": row.lane_id, "exact_identity": record["exact_identity"],
            "activation_identity": record["activation_identity"], "behaviour_cluster": record["behaviour_cluster"],
            "economic_hypothesis": base.economic_hypothesis, "mechanism_id": base.mechanism_id,
            "algorithm": base.algorithm,
        })
    prelim = pd.DataFrame(preliminary)
    counts = prelim.groupby(["panel_id", "arm"])["behaviour_cluster"].transform("count")
    same = prelim.groupby(["panel_id", "arm", "behaviour_cluster"])["behaviour_cluster"].transform("count")
    novelty = np.log1p(counts / same)
    strict_rows: list[dict[str, Any]] = []
    for record, nov in zip(preliminary, novelty):
        spec = specs[record["proposal_id"]]
        panel = panels[record["panel_id"]]
        weights = rank_weights(materialize_program(spec, panel))
        vector = asdict(multiobjective_evaluate(
            weights, panel, complexity=complexity(spec), behaviour_novelty=float(nov),
            benchmark_net=best_full[record["panel_id"]], cost_bps=5.0, minimum_assets=5,
        ))
        feedback = asdict(development_feedback(weights, panel, best_full[record["panel_id"]]))
        criteria = [
            vector["hard_gate_pass"], vector["ic_lcb"] > 0, vector["net_lcb"] > 0,
            vector["benchmark_incremental_lcb"] > 0, vector["worst_horizon_net_mean"] > -0.001,
        ]
        strict_rows.append({
            **record, **vector, "development_scalar": feedback["limited_scalar"],
            "feedback_stability_lcb": feedback["stability_lcb"],
            "feedback_positive_block_fraction": feedback["positive_block_fraction"],
            "survivor_near_miss": sum(not value for value in criteria) == 1,
            "development_survivor": all(criteria), "candidate_promotion": False,
            "feedback_persisted": False,
        })
    strict = pd.DataFrame(strict_rows)
    pareto_rows: list[dict[str, Any]] = []
    for (panel, arm), group in strict.groupby(["panel_id", "arm"]):
        for proposal_id in pareto_front(group.to_dict("records")):
            pareto_rows.append({"panel_id": panel, "arm": arm, "proposal_id": proposal_id, "candidate_promotion": False})
    pareto = pd.DataFrame(pareto_rows)
    pareto_ids = set(pareto.proposal_id) if len(pareto) else set()
    pack = strict[(strict.arm == "STRATIFIED_ADMISSION") & strict.proposal_id.isin(pareto_ids)].copy()
    pack["pack_status"] = "FROZEN_DEVELOPMENT_NO_PROMOTION"
    comparisons: list[dict[str, Any]] = []
    for adaptive, control in epoch1.MATCHED.items():
        ag = strict[(strict.arm == "STRATIFIED_ADMISSION") & (strict.lane_id == adaptive)]
        cg = strict[(strict.arm == "STRATIFIED_ADMISSION") & (strict.lane_id == control)]
        ac = concentration_metrics(candidates[candidates.lane_id == adaptive])
        cc = concentration_metrics(candidates[candidates.lane_id == control])
        am = {"near_miss_per_strict": ag.survivor_near_miss.mean() if len(ag) else 0, "survivor_per_strict": ag.development_survivor.mean() if len(ag) else 0, "cluster_yield": ag.behaviour_cluster.nunique() / max(1, len(ag)), "top_concentration": max(ac["top_decile_mechanism_share"], ac["top_decile_primitive_share"]), "runtime_per_proposal": 1.0, "benchmark_increment_median": ag.benchmark_incremental_lcb.median() if len(ag) else -999}
        cm = {"near_miss_per_strict": cg.survivor_near_miss.mean() if len(cg) else 0, "survivor_per_strict": cg.development_survivor.mean() if len(cg) else 0, "cluster_yield": cg.behaviour_cluster.nunique() / max(1, len(cg)), "top_concentration": max(cc["top_decile_mechanism_share"], cc["top_decile_primitive_share"]), "runtime_per_proposal": 1.0, "benchmark_increment_median": cg.benchmark_incremental_lcb.median() if len(cg) else -999}
        comparisons.append({"adaptive_lane": adaptive, "control_lane": control, "verdict": adaptive_verdict(am, cm), **{f"adaptive_{key}": value for key, value in am.items()}, **{f"control_{key}": value for key, value in cm.items()}, **{f"adaptive_{key}": value for key, value in ac.items()}, **{f"control_{key}": value for key, value in cc.items()}})
    adaptive_compare = pd.DataFrame(comparisons)
    lane_rows: list[dict[str, Any]] = []
    for (panel, lane), group in candidates.groupby(["panel_id", "lane_id"]):
        sg = strict[(strict.panel_id == panel) & (strict.lane_id == lane) & (strict.arm == "STRATIFIED_ADMISSION")]
        vc = sg.behaviour_cluster.value_counts()
        lane_rows.append({"panel_id": panel, "lane_id": lane, "proposals": len(group), "legal_rate": group.legal.mean(), "exact_identities": group.loc[group.legal, "sketch_exact_identity"].nunique(), "strict": len(sg), "behaviour_clusters": sg.behaviour_cluster.nunique(), "n_eff": effective_count(sg.behaviour_cluster), "top_cluster_share": vc.iloc[0] / len(sg) if len(sg) else 0, "near_miss": int(sg.survivor_near_miss.sum()), "survivors": int(sg.development_survivor.sum()), "positive_net_lcb": int((sg.net_lcb > 0).sum()), "failure_rate": 1 - group.legal.mean()})
    lane_summary = pd.DataFrame(lane_rows)
    arm_rows: list[dict[str, Any]] = []
    for (panel, arm), group in strict.groupby(["panel_id", "arm"]):
        vc = group.behaviour_cluster.value_counts()
        arm_rows.append({"panel_id": panel, "arm": arm, "strict": len(group), "exact": group.exact_identity.nunique(), "clusters": group.behaviour_cluster.nunique(), "n_eff": effective_count(group.behaviour_cluster), "top1": vc.iloc[0] / len(group), "top3": vc.iloc[:3].sum() / len(group), "near_miss": int(group.survivor_near_miss.sum()), "survivors": int(group.development_survivor.sum()), "positive_net_lcb": int((group.net_lcb > 0).sum()), "hypotheses": group.economic_hypothesis.nunique(), "cross_panel_ranked": False})
    arm_summary = pd.DataFrame(arm_rows)
    survivors = int(strict.development_survivor.sum())
    near = int(strict.survivor_near_miss.sum())
    positive_net = int((strict.net_lcb > 0).sum())
    adaptive_success = int((adaptive_compare.verdict == "ADAPTIVE_SUCCESS").sum())
    uct_row = adaptive_compare[adaptive_compare.adaptive_lane == "uct_mcts"].iloc[0]
    uct_concentration = max(uct_row.adaptive_top_decile_mechanism_share, uct_row.adaptive_top_decile_primitive_share)
    natural_underfill = frozen["strict_assignment_total"] < 3072
    if survivors > 0 and positive_net > 3 and adaptive_success > 0 and uct_concentration < 0.60:
        recommendation = "PREPARE_ROTATING_CHALLENGE_EPOCH"
    elif survivors == 0 and positive_net > 3 and near > 17:
        recommendation = "REVISE_SURVIVOR_CONTRACT_WITHOUT_OOS_ACCESS"
    else:
        recommendation = "REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH"
    decision = "FROZEN_DEVELOPMENT_EPOCH1R_COMPLETED_WITH_NATURAL_UNDERFILL" if natural_underfill else "FROZEN_DEVELOPMENT_EPOCH1R_COMPLETED"
    tables = {
        "strict_evaluations.csv": strict, "pareto_archive.csv": pareto,
        "frozen_candidate_pack.csv": pack, "adaptive_vs_matched_controls.csv": adaptive_compare,
        "lane_summary.csv": lane_summary, "arm_summary.csv": arm_summary, "benchmark_results.csv": benchmarks,
    }
    for name, frame in tables.items():
        frame.to_csv(OUTPUT_ROOT / name, index=False)
    outputs = [{"path": relative(OUTPUT_ROOT / name), "sha256": sha256_file(OUTPUT_ROOT / name)} for name in tables]
    manifest = {
        "experiment_id": frozen["experiment_id"], "decision": decision, "recommendation": recommendation,
        "frozen_manifest_sha256": frozen["frozen_manifest_sha256"], "proposal_pack_sha256": frozen["proposal_pack_sha256"],
        "strict_assignment_total": len(strict), "stratified_strict": int((strict.arm == "STRATIFIED_ADMISSION").sum()),
        "global_strict": int((strict.arm == "GLOBAL_TOP_K_CONTROL").sum()), "natural_underfill": natural_underfill,
        "development_survivors": survivors, "survivor_near_miss": near, "positive_net_lcb": positive_net,
        "adaptive_successes": adaptive_success, "uct_top_concentration": float(uct_concentration),
        "runtime_seconds": time.perf_counter() - started, "outputs": outputs,
        "forward_status": "FORWARD_SEALED", "candidate_promotion": False, "a7mem_updated": False,
        "cross_epoch_memory": False, "online_contract_changed": False, "additional_budget": False,
        "seed_changed": False, "reward_changed": False, "admission_changed_after_freeze": False,
        "cross_panel_ranked": False, "oos_claim": False,
    }
    RUN.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = ["# Epoch-1R Compact Result", "", f"Decision: `{decision}`", f"Recommendation: `{recommendation}`", "", arm_summary.to_markdown(index=False), "", adaptive_compare.to_markdown(index=False), "", "- `FORWARD_SEALED`", "- `NO_CANDIDATE_PROMOTION`", "- `NO_CROSS_EPOCH_ADAPTIVE_MEMORY`"]
    result_path = OUTPUT_ROOT / "EPOCH1R_COMPACT_RESULT.md"
    result_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    manifest["outputs"].append({"path": relative(result_path), "sha256": sha256_file(result_path)})
    RUN.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "recommendation": recommendation, "strict": len(strict), "survivors": survivors, "near_miss": near, "positive_net_lcb": positive_net, "adaptive_successes": adaptive_success, "runtime_seconds": manifest["runtime_seconds"]}, indent=2))
    return manifest


def check() -> None:
    frozen = verify_frozen()
    run_manifest = load_json(RUN)
    if run_manifest["frozen_manifest_sha256"] != frozen["frozen_manifest_sha256"]:
        raise ValueError("Epoch-1R run/freeze mismatch")
    prohibited = ("candidate_promotion", "a7mem_updated", "cross_epoch_memory", "online_contract_changed", "additional_budget", "seed_changed", "reward_changed", "admission_changed_after_freeze", "cross_panel_ranked", "oos_claim")
    if any(run_manifest[key] for key in prohibited):
        raise PermissionError("Epoch-1R prohibited activity")
    assignment = pd.read_csv(ASSIGNMENTS)
    strict = pd.read_csv(OUTPUT_ROOT / "strict_evaluations.csv")
    if len(strict) != len(assignment) or len(strict) != frozen["strict_assignment_total"]:
        raise ValueError("Epoch-1R strict assignment/execution mismatch")
    if strict.groupby(["panel_id", "arm"])["exact_identity"].apply(lambda values: values.duplicated().any()).any():
        raise ValueError("Epoch-1R duplicate exact identity vote")
    for item in run_manifest["outputs"]:
        if sha256_file(REPO / item["path"]) != item["sha256"]:
            raise ValueError(f"Epoch-1R output drift: {item['path']}")
    if run_manifest["decision"] not in {"FROZEN_DEVELOPMENT_EPOCH1R_COMPLETED", "FROZEN_DEVELOPMENT_EPOCH1R_COMPLETED_WITH_NATURAL_UNDERFILL"}:
        raise ValueError("Epoch-1R completion status invalid")
    print("PASS_FROZEN_DEVELOPMENT_EPOCH1R_VALID")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("pack", "preflight", "freeze", "run", "check"))
    args = parser.parse_args()
    try:
        if args.action == "pack":
            generate_pack()
        elif args.action == "preflight":
            preflight()
        elif args.action == "freeze":
            freeze()
        elif args.action == "run":
            run()
        else:
            check()
    except Exception as exc:
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        FAILURE.write_text(json.dumps({
            "action": args.action, "status": "FAILED_VISIBLE_NOT_DELETED",
            "error_type": type(exc).__name__, "error": str(exc), "repo_sha": git("rev-parse", "HEAD", check=False),
            "forward_read": False, "candidate_promotion": False, "cross_epoch_memory": False,
        }, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
