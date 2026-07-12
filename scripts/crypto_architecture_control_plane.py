from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO / "config" / "crypto_architecture_control_registry_v1.json"
STATE_SOURCE_PATH = REPO / "config" / "crypto_phase_state_v1.json"
DECISION_LOG_PATH = REPO / "runtime" / "a7b0_control_plane_20260711" / "a7evalreset_decision_change_log.jsonl"
RUN_ROOT = REPO / "runtime" / "a7b0_control_plane_20260711"
RUN_MANIFEST_PATH = RUN_ROOT / "phase_a_b0_run_manifest.json"
ARTIFACT_INDEX_PATH = RUN_ROOT / "phase_a_b0_artifact_index.csv"
ATTESTATION_PATH = RUN_ROOT / "phase_b0_acceptance_attestation.json"
ACCEPTANCE_TEST_OUTPUT_PATH = RUN_ROOT / "phase_b0_acceptance_test_output.txt"
B0P_MANIFEST_PATH = REPO / "runtime" / "a7b0p_control_plane_20260711" / "b0p_qualification_manifest.json"
B0P_ATTESTATION_PATH = REPO / "runtime" / "a7b0p_control_plane_20260711" / "phase_b0p_partial_acceptance_attestation.json"
B0P_ACCEPTANCE_TEST_OUTPUT_PATH = REPO / "runtime" / "a7b0p_control_plane_20260711" / "phase_b0p_partial_acceptance_test_output.txt"
B0P_FUNDING_SUMMARY_PATH = REPO / "runtime" / "a7b0p_funding_qualification_20260711" / "funding_qualification_summary.json"
B0P_IDENTITY_SUMMARY_PATH = REPO / "runtime" / "a7b0p_identity_qualification_20260711" / "identity_qualification_manifest.json"
B0A_MANIFEST_PATH = REPO / "runtime" / "a7b0a_signal_behaviour_20260711" / "b0a_run_manifest.json"
B0A_ARTIFACT_PATH = REPO / "runtime" / "a7b0a_signal_behaviour_20260711" / "signal_behaviour_sketch.bin"
B0A_ARTIFACT_INDEX_PATH = REPO / "runtime" / "a7b0a_signal_behaviour_20260711" / "b0a_artifact_index.csv"
NEXTGEN_ROOT = REPO / "runtime" / "nextgen_dark_20260711"
NEXTGEN_MATERIALIZATION_PATH = NEXTGEN_ROOT / "feature_state_materialization_manifest.json"
NEXTGEN_COVERAGE_PATH = NEXTGEN_ROOT / "non_performance_coverage_capability.json"
NEXTGEN_BOOKTICKER_PATH = NEXTGEN_ROOT / "pc1_bookticker_top_of_book_manifest.json"
NEXTGEN_RUN_MANIFEST_PATH = NEXTGEN_ROOT / "nextgen_dark_run_manifest.json"
NEXTGEN_ARTIFACT_INDEX_PATH = NEXTGEN_ROOT / "nextgen_dark_artifact_index.csv"
NEXTGEN_TEST_OUTPUT_PATH = NEXTGEN_ROOT / "nextgen_dark_test_output.txt"
CANARY_PLAN_PATH = REPO / "config" / "crypto_nextgen_dark_canary_plan_v1.json"
NEXTGEN_ADR_PATH = REPO / "docs" / "adr" / "0002-nextgen-dark-isolated-observation-infrastructure.md"
B1S_ROOT = REPO / "runtime" / "b1s_canary_20260711"
B1S_FROZEN_MANIFEST_PATH = B1S_ROOT / "b1s_frozen_run_manifest.json"
B1S_RUN_MANIFEST_PATH = B1S_ROOT / "b1s_canary_manifest.json"
B1S_REPORT_PATH = B1S_ROOT / "B1S_CANARY_COMPACT_RESULT.md"
B1S_TEST_OUTPUT_PATH = B1S_ROOT / "b1s_test_output.txt"
B1S_ARTIFACT_INDEX_PATH = B1S_ROOT / "b1s_artifact_index.csv"
EPOCH0_ROOT = REPO / "runtime" / "nextgen_epoch0_20260711"
EPOCH0_SMOKE_PRE_PATH = EPOCH0_ROOT / "epoch0_throughput_smoke_pre_optimization.json"
EPOCH0_SMOKE_PATH = EPOCH0_ROOT / "epoch0_throughput_smoke.json"
EPOCH0_FROZEN_MANIFEST_PATH = EPOCH0_ROOT / "epoch0_frozen_design_manifest.json"
EPOCH0_CANARY_ATTRIBUTION_PATH = EPOCH0_ROOT / "b1s_canary_deep_attribution.json"
EPOCH0_CANARY_REPORT_PATH = EPOCH0_ROOT / "B1S_CANARY_COMPARATIVE_DECISION_REPORT.md"
EPOCH0_TEST_OUTPUT_PATH = EPOCH0_ROOT / "epoch0_design_test_output.txt"
EPOCH0_ARTIFACT_INDEX_PATH = EPOCH0_ROOT / "epoch0_artifact_index.csv"
EPOCH0_RUN_MANIFEST_PATH = EPOCH0_ROOT / "epoch0_run_manifest.json"
EPOCH0_CLOSURE_VALIDATION_PATH = EPOCH0_ROOT / "epoch0_closure_validation.json"
EPOCH0_COMPARATIVE_REPORT_PATH = EPOCH0_ROOT / "EPOCH0_COMPARATIVE_DECISION_REPORT.md"
EPOCH0_FAILURE_PATH = EPOCH0_ROOT / "epoch0_failure.json"
EPOCH1_ROOT = REPO / "runtime" / "nextgen_epoch1_20260712"
EPOCH1_SMOKE_PATH = EPOCH1_ROOT / "epoch1_throughput_smoke.json"
EPOCH1_FROZEN_MANIFEST_PATH = EPOCH1_ROOT / "epoch1_frozen_design_manifest.json"
EPOCH1_FAILURE_PATH = EPOCH1_ROOT / "epoch1_failure.json"
EPOCH1_CLOSURE_MANIFEST_PATH = EPOCH1_ROOT / "epoch1_closure_manifest.json"
EPOCH1_ARTIFACT_INDEX_PATH = EPOCH1_ROOT / "epoch1_artifact_index.csv"
EPOCH1R_ROOT = REPO / "runtime" / "nextgen_epoch1r_20260712"
EPOCH1R_PACK_PATH = EPOCH1R_ROOT / "proposal_pack.jsonl.gz"
EPOCH1R_PACK_MANIFEST_PATH = EPOCH1R_ROOT / "proposal_pack_manifest.json"
EPOCH1R_FULL_IDENTITIES_PATH = EPOCH1R_ROOT / "full_identity_records.jsonl.gz"
EPOCH1R_CAPACITY_PATH = EPOCH1R_ROOT / "admission_capacity_table.csv"
EPOCH1R_ASSIGNMENT_PATH = EPOCH1R_ROOT / "admission_assignments.csv"
EPOCH1R_PREFLIGHT_PATH = EPOCH1R_ROOT / "admission_preflight_manifest.json"
EPOCH1R_FROZEN_PATH = EPOCH1R_ROOT / "epoch1r_frozen_design_manifest.json"
EPOCH1R_RUN_PATH = EPOCH1R_ROOT / "epoch1r_run_manifest.json"
EPOCH1R_ARTIFACT_INDEX_PATH = EPOCH1R_ROOT / "epoch1r_artifact_index.csv"
MECHANISM_DATA_ROOT = REPO / "runtime" / "mechanism_data_expansion0_20260712"
MECHANISM_DATA_INVENTORY_MANIFEST_PATH = MECHANISM_DATA_ROOT / "inventory_completion_manifest.json"
MECHANISM_DATA_INVENTORY_INDEX_PATH = MECHANISM_DATA_ROOT / "inventory_artifact_index.csv"
NATIVE_AGGTRADES_RELEASE_ROOT = MECHANISM_DATA_ROOT / "native_aggtrades_release_v1"
NATIVE_AGGTRADES_RELEASE_MANIFEST_PATH = NATIVE_AGGTRADES_RELEASE_ROOT / "release_manifest.json"
NATIVE_AGGTRADES_RELEASE_INDEX_PATH = NATIVE_AGGTRADES_RELEASE_ROOT / "release_artifact_index.csv"
NATIVE_AGGTRADES_BENCHMARK_ROOT = MECHANISM_DATA_ROOT / "native_aggtrades_benchmark_v1"
NATIVE_AGGTRADES_BENCHMARK_SUMMARY_PATH = NATIVE_AGGTRADES_BENCHMARK_ROOT / "benchmark_summary.json"
BBO_ACQUISITION_SUMMARY_PATH = MECHANISM_DATA_ROOT / "bbo_full_year_acquisition" / "bbo_acquisition_capacity_summary.json"
MECHANISM_DATA_CLOSURE_MANIFEST_PATH = MECHANISM_DATA_ROOT / "stage_closure_manifest.json"
MECHANISM_DATA_CLOSURE_INDEX_PATH = MECHANISM_DATA_ROOT / "stage_artifact_index.csv"
CURRENT_ARCH_PATH = REPO / ".planning" / "graphs" / "CURRENT_ARCHITECTURE.md"
BOUNDARY_PATH = REPO / ".planning" / "graphs" / "ARCHITECTURE_BOUNDARY.md"
EVOLUTION_PATH = REPO / ".planning" / "graphs" / "EVOLUTION_MAP.md"
GRAPH_PATH = REPO / ".planning" / "graphs" / "graph.json"
STATE_PATH = REPO / ".planning" / "STATE.md"

REQUIRED_NODE_FIELDS = {
    "id",
    "label",
    "status",
    "implementation_path",
    "entrypoint",
    "input",
    "output",
    "data_role",
    "feedback_permission",
    "artifact_test",
    "last_verified_sha",
    "blocker",
}
REQUIRED_NODE_IDS = {
    "data_release", "time_block_roles", "field_ontology", "a7input0", "feature_builder",
    "label_builder", "regime_builder", "funding_event_detector", "basis_oi_event_detection",
    "semantic_compiler", "exact_signal_identity", "identity_registry", "generation_lanes", "proxy",
    "strict_reward", "admission", "a7mem", "scheduler", "benchmark_registry",
    "evaluation_access_ledger", "spent_evaluation", "sealed_forward", "future_wrong_lag", "bz",
    "temporal_event_contract", "feature_state_fabric", "production_observation_qualification",
    "frozen_signal_behaviour_qualification",
    "nextgen_observation_fabric", "typed_temporal_program", "isolated_hypothesis_lanes",
    "anti_collapse_admission", "challenger_harness", "coverage_observability", "canary_plan",
    "b1s_main_canary", "b1s_bbo_micro_canary", "b1s_canary_control",
    "nextgen_mechanism_registry", "nextgen_search_engine", "development_multiobjective_reward",
    "epoch0_frozen_design",
    "epoch0_execution",
    "epoch1_search_revision", "epoch1_frozen_design", "epoch1_execution",
    "epoch1r_admission_repair", "epoch1r_frozen_design", "epoch1r_execution",
    "epoch2_survivor_calibration", "epoch2_blocker_taxonomy", "epoch2_blocker_directed_search",
    "epoch2_frozen_design", "epoch2_execution",
    "mechanism_data_inventory",
    "native_aggtrades_release",
    "native_aggtrades_benchmark", "bbo_full_year_acquisition", "mechanism_data_expansion0_closure",
}
REQUIRED_FORBIDDEN_EDGES = {
    ("spent_evaluation", "admission"),
    ("spent_evaluation", "generation_lanes"),
    ("spent_evaluation", "a7mem"),
    ("sealed_forward", "scheduler"),
    ("benchmark_registry", "a7mem"),
    ("feature_state_fabric", "strict_reward"),
    ("a7input0", "generation_lanes"),
    ("bz", "admission"),
    ("identity_registry", "admission"),
    ("production_observation_qualification", "admission"),
    ("frozen_signal_behaviour_qualification", "admission"),
    ("frozen_signal_behaviour_qualification", "a7mem"),
    ("frozen_signal_behaviour_qualification", "scheduler"),
    ("frozen_signal_behaviour_qualification", "strict_reward"),
    ("nextgen_observation_fabric", "strict_reward"),
    ("nextgen_observation_fabric", "generation_lanes"),
    ("isolated_hypothesis_lanes", "a7mem"),
    ("challenger_harness", "a7mem"),
    ("sealed_forward", "canary_plan"),
    ("canary_plan", "scheduler"),
    ("b1s_main_canary", "b1s_bbo_micro_canary"),
    ("b1s_bbo_micro_canary", "b1s_main_canary"),
    ("spent_evaluation", "b1s_canary_control"),
    ("sealed_forward", "b1s_canary_control"),
    ("b1s_canary_control", "a7mem"),
    ("b1s_canary_control", "admission"),
    ("b1s_canary_control", "scheduler"),
    ("spent_evaluation", "epoch0_frozen_design"),
    ("sealed_forward", "epoch0_frozen_design"),
    ("epoch0_frozen_design", "a7mem"),
    ("epoch0_frozen_design", "admission"),
    ("epoch0_frozen_design", "scheduler"),
    ("epoch0_execution", "a7mem"),
    ("epoch0_execution", "admission"),
    ("epoch0_execution", "scheduler"),
    ("spent_evaluation", "epoch0_execution"),
    ("sealed_forward", "epoch0_execution"),
    ("spent_evaluation", "epoch1_search_revision"),
    ("sealed_forward", "epoch1_search_revision"),
    ("spent_evaluation", "epoch1_frozen_design"),
    ("sealed_forward", "epoch1_frozen_design"),
    ("epoch1_frozen_design", "a7mem"),
    ("epoch1_frozen_design", "admission"),
    ("epoch1_frozen_design", "scheduler"),
    ("epoch1_execution", "a7mem"),
    ("epoch1_execution", "admission"),
    ("epoch1_execution", "scheduler"),
    ("spent_evaluation", "epoch1_execution"),
    ("sealed_forward", "epoch1_execution"),
    ("spent_evaluation", "epoch1r_admission_repair"),
    ("sealed_forward", "epoch1r_admission_repair"),
    ("spent_evaluation", "epoch1r_execution"),
    ("sealed_forward", "epoch1r_execution"),
    ("epoch1r_execution", "a7mem"),
    ("epoch1r_execution", "admission"),
    ("epoch1r_execution", "scheduler"),
    ("sealed_forward", "epoch2_execution"), ("spent_evaluation", "epoch2_execution"),
    ("epoch2_execution", "a7mem"), ("epoch2_execution", "admission"), ("epoch2_execution", "scheduler"),
}
VALID_STATUSES = {"IMPLEMENTED", "PARTIAL", "PLANNED", "FROZEN", "DEPRECATED"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_normalized_text_file(path: Path) -> str:
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return sha256_bytes(normalized.encode("utf-8"))


def acceptance_test_evidence(state: dict[str, Any]) -> dict[str, str]:
    normalized = ACCEPTANCE_TEST_OUTPUT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    result = lines[-1] if lines else ""
    if not re.fullmatch(r"39 passed in [0-9]+(?:\.[0-9]+)?s", result):
        raise ValueError("acceptance test output does not record exactly 39 passing tests")
    return {
        "subject_sha": state["phase_b0_acceptance"]["accepted_subject_sha"],
        "command": "G:\\PythonProject\\.venv\\Scripts\\python.exe -m pytest -q",
        "result": result,
        "output_path": relative(ACCEPTANCE_TEST_OUTPUT_PATH),
        "output_sha256": sha256_normalized_text_file(ACCEPTANCE_TEST_OUTPUT_PATH),
    }


def b0p_acceptance_test_evidence(state: dict[str, Any]) -> dict[str, str]:
    normalized = B0P_ACCEPTANCE_TEST_OUTPUT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    result = lines[-1] if lines else ""
    if not re.fullmatch(r"47 passed in [0-9]+(?:\.[0-9]+)?s", result):
        raise ValueError("B0P partial-acceptance output does not record exactly 47 passing tests")
    return {
        "subject_sha": state["phase_b0p_acceptance"]["accepted_subject_sha"],
        "command": "G:\\PythonProject\\.venv\\Scripts\\python.exe -m pytest -q",
        "result": result,
        "output_path": relative(B0P_ACCEPTANCE_TEST_OUTPUT_PATH),
        "output_sha256": sha256_normalized_text_file(B0P_ACCEPTANCE_TEST_OUTPUT_PATH),
    }


def nextgen_test_evidence() -> dict[str, str]:
    normalized = NEXTGEN_TEST_OUTPUT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    result = lines[-1] if lines else ""
    if not re.fullmatch(r"72 passed in [0-9]+(?:\.[0-9]+)?s", result):
        raise ValueError("NEXTGEN-DARK test output does not record exactly 72 passing tests")
    return {
        "command": "G:\\PythonProject\\.venv\\Scripts\\python.exe -m pytest -q",
        "result": result,
        "output_path": relative(NEXTGEN_TEST_OUTPUT_PATH),
        "output_sha256": sha256_normalized_text_file(NEXTGEN_TEST_OUTPUT_PATH),
    }


def b1s_test_evidence() -> dict[str, str]:
    normalized = B1S_TEST_OUTPUT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in normalized.splitlines() if line.strip()]
    result = lines[-1] if lines else ""
    if not re.fullmatch(r"78 passed in [0-9]+(?:\.[0-9]+)?s", result):
        raise ValueError("B1S test output does not record exactly 78 passing tests")
    return {
        "command": "G:\\PythonProject\\.venv\\Scripts\\python.exe -m pytest -q",
        "result": result,
        "output_path": relative(B1S_TEST_OUTPUT_PATH),
        "output_sha256": sha256_normalized_text_file(B1S_TEST_OUTPUT_PATH),
    }


def epoch0_test_evidence() -> dict[str, str]:
    normalized = EPOCH0_TEST_OUTPUT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    match = re.search(r"(?m)^(94 passed in [0-9.]+s)$", normalized)
    if not match:
        raise ValueError("Epoch-0 closure test output does not record exactly 94 passing tests")
    return {
        "command": "G:/PythonProject/.venv/Scripts/python.exe -m pytest -q",
        "result": match.group(1),
        "output_path": relative(EPOCH0_TEST_OUTPUT_PATH),
        "output_sha256": sha256_normalized_text_file(EPOCH0_TEST_OUTPUT_PATH),
    }


def relative(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_decisions() -> list[dict[str, Any]]:
    rows = []
    for line in DECISION_LOG_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def node_bundle_sha(node: dict[str, Any]) -> str:
    records: list[str] = []
    for raw in [*node.get("implementation_path", []), *node.get("artifact_test", [])]:
        path = REPO / raw
        records.append(f"{raw}:{sha256_file(path) if path.is_file() else 'MISSING'}")
    if not records:
        records.append(f"{node['id']}:NO_ARTIFACT_YET")
    return sha256_bytes("\n".join(records).encode("utf-8"))


def materialize_registry() -> dict[str, Any]:
    registry = load_json(REGISTRY_PATH)
    for node in registry["nodes"]:
        node["last_verified_sha"] = node_bundle_sha(node)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return registry


def validate_registry(registry: dict[str, Any]) -> None:
    nodes = registry.get("nodes", [])
    ids = [node.get("id") for node in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate architecture node id")
    missing_ids = sorted(REQUIRED_NODE_IDS.difference(ids))
    if missing_ids:
        raise ValueError(f"missing required architecture nodes: {missing_ids}")
    for node in nodes:
        missing = sorted(REQUIRED_NODE_FIELDS.difference(node))
        if missing:
            raise ValueError(f"node {node.get('id')} missing fields: {missing}")
        if node["status"] not in VALID_STATUSES:
            raise ValueError(f"node {node['id']} invalid status: {node['status']}")
        if node["status"] == "IMPLEMENTED" and not node["implementation_path"]:
            raise ValueError(f"implemented node {node['id']} has no implementation path")
    forbidden = {(edge["source"], edge["target"]) for edge in registry.get("edges", []) if edge["kind"] == "FORBIDDEN"}
    missing_edges = sorted(REQUIRED_FORBIDDEN_EDGES.difference(forbidden))
    if missing_edges:
        raise ValueError(f"missing required forbidden edges: {missing_edges}")


def mermaid(registry: dict[str, Any]) -> str:
    lines = ["```mermaid", "flowchart TD"]
    for node in registry["nodes"]:
        label = f"{node['label']}\\n{node['status']}"
        lines.append(f"  control_{node['id']}[\"{label}\"]")
    for edge in registry["edges"]:
        arrow = "-. forbidden .->" if edge["kind"] == "FORBIDDEN" else "-->"
        lines.append(f"  control_{edge['source']} {arrow} control_{edge['target']}")
    lines.append("```")
    return "\n".join(lines)


def node_table(registry: dict[str, Any]) -> str:
    columns = ["Node", "Status", "Implementation", "Entrypoint", "Input -> Output", "Data role", "Feedback", "Artifact/test", "Last verified SHA", "Blocker"]
    rows = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for n in registry["nodes"]:
        values = [
            n["label"], n["status"], "; ".join(n["implementation_path"]) or "planned",
            n["entrypoint"], f"{n['input']} -> {n['output']}", n["data_role"], n["feedback_permission"],
            "; ".join(n["artifact_test"]) or "planned", n["last_verified_sha"], n["blocker"],
        ]
        rows.append("| " + " | ".join(str(v).replace("|", "\\|") for v in values) + " |")
    return "\n".join(rows)


def forbidden_table(registry: dict[str, Any]) -> str:
    edges = [edge for edge in registry["edges"] if edge["kind"] == "FORBIDDEN"]
    rows = ["| Source | Target | Prohibition |", "|---|---|---|"]
    rows.extend(f"| {e['source']} | {e['target']} | {e['label']} |" for e in edges)
    return "\n".join(rows)


def render_documents(
    registry: dict[str, Any], state: dict[str, Any], decisions: list[dict[str, Any]], digest: str
) -> dict[Path, str]:
    current = f"""# Current Architecture

Generated from `{relative(REGISTRY_PATH)}`. Registry SHA256: `{digest}`.

Status: `{state['current_phase']}` / `{state['nextgen_epoch2']['status']}` / `{state['nextgen_epoch1r']['status']}` / `{state['nextgen_epoch1']['status']}` / `{state['nextgen_epoch0']['status']}` / `{state['production_observation_qualification_status']}` / `{state['formal_search_status']}` / `{state['adaptive_cross_epoch_memory_status']}` / `{state['candidate_promotion_status']}` / `{state['forward_data_status']}`.

Authority: `{relative(REGISTRY_PATH)}` is the machine-readable architecture authority; `graph.json` is its deterministic graph view; this file is the human-readable generated view. Raw graphify is unavailable, so `graph.json` retains the prior navigation graph plus a deterministic `control_*` overlay.

## Architecture

{mermaid(registry)}

## Node Registry

{node_table(registry)}

## Time Block Roles

- 2024 train: discovery training, not OOS proof.
- 2025-06 validation, 2025-12 test, 2026-04 recent, and 2026-05 stress: `SPENT_HISTORICAL_EVALUATION`, report-only.
- Unknown/new epochs: `SEALED_FORWARD`, no read in B0.

## Forbidden Edges

{forbidden_table(registry)}
"""
    boundary = f"""# Architecture Boundary

Generated from registry SHA256: `{digest}`.

## Authority

1. Current user instruction and governance decisions.
2. `{relative(REGISTRY_PATH)}` is the machine-readable architecture authority.
3. `graph.json` is the deterministic graph view generated from the registry.
4. `{relative(CURRENT_ARCH_PATH)}` is the human-readable generated view.
5. `{relative(STATE_PATH)}`, the EVALRESET decision log, and the run manifest record phase state and history.

External graphify is currently unavailable. This does not permit manual architecture claims: `scripts/crypto_architecture_control_plane.py --check` must pass.

## Acceptance Rule

Any code, registry, route, artifact, curated document, STATE, decision log, run manifest, artifact index, or control graph mismatch blocks Phase acceptance.

## Forbidden Edges

{forbidden_table(registry)}
"""
    timeline = "\n".join(f"- `{d['decision_id']}` — `{d['status']}`: {d['detail']}" for d in decisions)
    evolution = f"""# Evolution Map

Generated from registry SHA256: `{digest}`.

## Current Evolution

- The frozen release compresses 33 alias-expanded blueprints to 18 numeric representatives, 16 accepted rows, 6 canonical expressions, and 6 exact signal identities.
- Exact-identity admission and strict reward are observed contraction points.
- Activation collapse remains unestablished because no frozen signal behavior matrix is present. One coarse spent split-sign diagnostic identity and five semantic economic hypotheses are registered, but neither establishes the first collapse of independent economic information.
- At Phase B0 entry, funding event detection, future wrong-lag, A7INPUT0 coverage, and authoritative BZ definition blocked research. B0.1-B0.4 close their contract-level gaps; production execution and promotion remain frozen under `HOLD_RESEARCH`.
- The proposed 400k reward-integrated search is revoked.
- Phase A governance is accepted while `HOLD_RESEARCH` remains.
- Phase B0 contracts are accepted for subject `{state['phase_b0_acceptance']['accepted_subject_sha']}`.
- B0P is stopped at `PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED` because funding qualified but activation identity did not.
- B0P subject `{state['phase_b0p_acceptance']['accepted_subject_sha']}` is independently attested as `{state['phase_b0p_acceptance']['status']}`; only frozen signal-behaviour qualification is unlocked.
- Binance UM core12 funding observation is production-qualified through 2026-04-30; cross-venue qualification is not claimed.
- B0A establishes `16 accepted aliases -> 6 exact signals -> 5 activation identities -> 4 behaviour clusters -> 5 semantic economic hypotheses`; the complete 33-row survivor map still contains 18 exact identities and must not be collapsed to six in reporting.
- Exact-to-activation and activation-to-behaviour contraction are now observed on the frozen pre-forward coordinate contract. This does not by itself establish collapse of independent economic information because the five economic hypotheses remain semantic registrations.
- B0A is stopped at `{state['frozen_signal_behaviour_status']}` with no reward, selection, scheduler, generator, or memory feedback.
- NEXTGEN-DARK materializes 245088 Binance UM core12 development/pre-forward coordinates reproducibly without performance columns. Funding, basis, OI, mark/index, taker, liquidity, volatility, session, and cross-asset states materialize. A PC1 supplement scoped-qualifies 14208 top-of-book liquidity rows over 2024-01/02 with 82.22% core12 coordinate coverage; it is BBO only, not multi-level depth. Liquidation remains unavailable because PC1 contains no liquidation/force-order source.
- Thirteen typed temporal/event primitives, seven isolated no-memory lanes, deterministic anti-collapse quotas, frozen benchmark/challenger interfaces, and non-performance coverage metrics are implemented without execution of formal search or performance comparison.
- The earlier NEXTGEN-DARK CANARY plan is superseded by the frozen B1S contract and retained as historical configuration.
- B1S execution is accepted as `B1S_CANARY_COMPLETED_WITH_NATURAL_QUOTA_UNDERFILL`: 5120 frozen proposals, 315/320 stratified strict evaluations, 320/320 equal-budget global-top-K controls, and 64 adaptive runtime-only queries. Funding-event naturally underfilled by five because only 27 legal exact identities existed under one-exact-one-vote; rerun is forbidden and the fixed budget contract was preserved.
- CANARY attribution shows funding identities saturated after the first 128 proposals, both seeds produced the same 27 identities, event-window/transition produced zero legal identities, and the former adaptive tail collapsed all 448 proposals to `blend`. Epoch-0 therefore replaces the single adaptive lane with isolated CEM, multi-step UCT/MCTS, evolutionary, surrogate, typed, LLM-repair and orthogonal lanes.
- Epoch-0 design is frozen at manifest `CD839D4F...`: 32768 proposals, seeds 2701/2709, 1024 stratified strict evaluations and 1024 equal-budget global-top-K controls. No Epoch-0 performance has been produced at the design-freeze node.
- Epoch-0 then completed its single fixed execution: 32768 proposals and 1801 full-identity strict evaluations after deterministic dedup, with no rerun or budget extension. The original frozen checker incorrectly demanded exactly 1024 global rows despite the natural-underfill contract; its visible failure record is retained and an independent closure validator passed.
- Funding capacity expanded to 120 exact identities in typed funding slices, so the earlier 27-identity CANARY ceiling was a grammar/generator limitation. However all lanes produced zero complete development survivors, BBO stratified admission was mechanically capped at 32/128, and UCT concentrated into one reward basin. The validated recommendation is `REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH`, not hypothesis-space expansion or rotating challenge authorization.
- Epoch-1 revision attributes the Epoch-0 failure across hard gates, net LCB, benchmark increment, stability, turnover, identity capacity and reward-basin concentration. The offline replay restores BBO admission from 32 to 128 using existing sketch identities without rewriting Epoch-0 or reading a new block.
- Epoch-1 implements full-identity-first feasible admission, positive-net-LCB-aligned hard gates and limited scalarization, equal-root matched controls, adaptive failure rules, UCT exploration/crowding controls, gated CEM elites, Pareto-aware surrogate targets and explicit evolutionary/repair lineage. `{state['nextgen_epoch1']['status']}`; design frozen `{state['nextgen_epoch1']['design_frozen']}`; performance started `{state['nextgen_epoch1']['performance_started']}`.
- The sole frozen Epoch-1 attempt failed before strict evaluation: an empty post-dedup identity set raised `KeyError: mechanism_id` instead of becoming a zero-capacity natural underfill. This is `EPOCH1_EXECUTION_FAILED_PRE_STRICT`, not evidence against the implemented search revision; `NO_EPOCH1_PERFORMANCE_CONCLUSION` remains explicit.
- Epoch-1R narrows the repair to admission empty-set semantics. Empty representatives now produce complete-schema zero-capacity natural underfill with `NO_LEGAL_EXACT_IDENTITIES`; CEM, MCTS, surrogate, reward/objective, survivor contract, grammar, seeds, budgets and hypothesis space remain unchanged. Current Epoch-1R state: `{state['nextgen_epoch1r']['status']}`.
- Epoch-2 calibration proves the frozen survivor contract reachable: planted controls pass `{state['nextgen_epoch2']['planted_pass_rate']}` and null controls pass `{state['nextgen_epoch2']['null_pass_rate']}`. OOS grade remains NONE and the bias-audit decision is HOLD_RESEARCH.
- All 84 Epoch-1R near-miss evaluation rows are frozen as explicit repair parents without reselection; blocker counts are `{state['nextgen_epoch2']['blocker_counts']}`.
- Epoch-2 strict evidence is accepted, the historical Hybrid comparison is invalid, and blocker-directed repair is rejected. Epoch-2B read 6157 existing strict rows with zero new performance queries: 72/84 parents have no reliable gross edge, all 24 adaptive operator-blocker cells lack causal gate control, and main NET_LCB near-miss distance worsened despite count growth.
- Epoch-2B selects `{state['epoch2b_audit']['main_recommendation']}` as the single main route. BBO full-2024 physically isolated acquisition remains a secondary engineering line with no winner selection.
- MECHANISM/DATA EXPANSION-0 inventory scans `{state['mechanism_data_expansion0']['local_files']}` local and `{state['mechanism_data_expansion0']['pc1_files']}` PC1 file observations without row data, performance, or forward access. Cross-venue history, multi-level depth, forced-flow and options remain unavailable; full-year BBO remains under-covered. Binance UM native aggTrades is the first release-qualification candidate based on longitudinal source availability, not accepted identities or performance.
- The first new release is `{state['mechanism_data_expansion0']['first_release_status']}`: `{state['mechanism_data_expansion0']['first_release_qualified_symbol_months']}/{state['mechanism_data_expansion0']['first_release_planned_symbol_months']}` core12 symbol-months over 2024-01..10, with physically isolated 2024-01..06 development and 2024-07..10 challenge directories. Development/challenge coverage is `{state['mechanism_data_expansion0']['first_release_development_coverage_ratio']}` / `{state['mechanism_data_expansion0']['first_release_challenge_coverage_ratio']}`; no interpolation or performance read occurred. The pre-performance horizons are frozen at 1h and 4h.
- The fixed native aggTrades simple benchmark CANARY completed `{state['mechanism_data_expansion0']['benchmark_fixed_evaluations']}` evaluations. Five of 32 base role/horizon rows have positive gross LCB, zero have positive net LCB and zero benchmark-horizons satisfy future-search admission; native aggTrades is `REJECT_NO_EDGE`.
- Binance Vision monthly bookTicker exposes only `{state['mechanism_data_expansion0']['bbo_full_year_available_coordinates']}/{state['mechanism_data_expansion0']['bbo_full_year_required_coordinates']}` core12 full-2024 symbol-months. May through December return HTTP 404, so downloading the available `{state['mechanism_data_expansion0']['bbo_full_year_available_compressed_gib']}` GiB cannot satisfy the 95% full-year BBO gate.
- MECHANISM/DATA EXPANSION-0 closes as `{state['mechanism_data_expansion0']['stage_status']}` with recommendation `{state['mechanism_data_expansion0']['stage_recommendation']}`. Formal search, forward access, candidate promotion and cross-epoch memory remain frozen.
- Main and BBO micro results remain separate comparison domains. BBO is core11 2024-01/02 top-of-book only and cannot rank main candidates or imply multi-level depth.
- `{state['formal_search_status']}`, `{state['adaptive_cross_epoch_memory_status']}`, `{state['candidate_promotion_status']}`, and `{state['forward_data_status']}` remain frozen.

## Decision Timeline

{timeline}
"""
    items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["b0_items"])
    b0p_items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["b0p_items"])
    b0a_items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["b0a_items"])
    nextgen_items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["nextgen_dark_items"])
    b1s_items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["b1s_canary_items"])
    state_doc = f"""# Crypto AlphaFactory Planning State

Registry SHA256: `{digest}`.

## Formal Status

- `{state['phase_a_status']}`
- `{state['collapse_status']}`
- `{state['research_status']}`
- Current phase: `{state['current_phase']}`
- Production observation qualification: `{state['production_observation_qualification_status']}`
- Phase B0P acceptance: `{state['phase_b0p_acceptance']['status']}`
- Frozen signal behaviour: `{state['frozen_signal_behaviour_status']}`
- NEXTGEN-DARK: `{state['nextgen_dark_status']}`
- Formal search: `{state['formal_search_status']}`
- CANARY: `{state['canary_status']}`
- Adaptive cross-epoch memory: `{state['adaptive_cross_epoch_memory_status']}`
- Candidate promotion: `{state['candidate_promotion_status']}`
- Active stage: `{state['active_stage']}`
- Phase B1: `{state['phase_b1_status']}`
- Forward data: `{state['forward_data_status']}`
- Mechanism/data inventory: `{state['mechanism_data_expansion0']['inventory_status']}`
- First release-qualification candidate: `{state['mechanism_data_expansion0']['first_release_candidate']}`
- First qualified release: `{state['mechanism_data_expansion0']['first_release_status']}`
- Release content SHA256: `{state['mechanism_data_expansion0']['first_release_content_sha256']}`
- Native aggTrades benchmark: `{state['mechanism_data_expansion0']['benchmark_status']}`; admitted horizons `{state['mechanism_data_expansion0']['benchmark_admitted_horizons']}`
- Full-year BBO source availability: `{state['mechanism_data_expansion0']['bbo_full_year_available_coordinates']}/{state['mechanism_data_expansion0']['bbo_full_year_required_coordinates']}`
- Stage recommendation: `{state['mechanism_data_expansion0']['stage_recommendation']}`
- Epoch-2B remote sync: `{state['epoch2b_remote_sync']['status']}`; tag peeled commit `{state['epoch2b_remote_sync']['tag_peeled_commit']}`
- Mechanism/data closure remote sync: `{state['mechanism_data_expansion0']['closure_remote_status']}` for `{state['mechanism_data_expansion0']['closure_subject_sha']}`

## Remote Baseline

- Branch: `{state['phase_a_remote_sync']['branch']}`
- Local Phase A SHA: `{state['phase_a_remote_sync']['local_sha']}`
- Remote Phase A SHA: `{state['phase_a_remote_sync']['remote_sha']}`
- Baseline tag commit: `{state['phase_a_remote_sync']['tag_commit']}`
- Sync status: `{state['phase_a_remote_sync']['status']}`

The earlier Phase A unsynchronized state is superseded by the verified remote refs above.

## Phase B0 Acceptance Attestation

- Accepted subject SHA: `{state['phase_b0_acceptance']['accepted_subject_sha']}`
- Accepted subject remote ref: `{state['phase_b0_acceptance']['accepted_subject_remote_ref']}`
- Attestation artifact: `{state['phase_b0_acceptance']['attestation_path']}`
- Attestation commit policy: `{state['phase_b0_acceptance']['attestation_commit_policy']}`
- Status: `{state['phase_b0_acceptance']['status']}`

## Phase B0 Items

{items}

## Phase B0P Items

{b0p_items}

## Phase B0P Partial Acceptance

- Accepted subject SHA: `{state['phase_b0p_acceptance']['accepted_subject_sha']}`
- Accepted subject remote ref: `{state['phase_b0p_acceptance']['accepted_subject_remote_ref']}`
- Attestation artifact: `{state['phase_b0p_acceptance']['attestation_path']}`
- Funding: `{state['phase_b0p_acceptance']['funding_status']}`
- Identity: `{state['phase_b0p_acceptance']['identity_status']}`
- Activation: `{state['phase_b0p_acceptance']['activation_status']}`

## Phase B0A Items

{b0a_items}

## Phase B0A Result

- Decision: `{state['frozen_signal_behaviour_status']}`
- Artifact: `{state['phase_b0a_result']['artifact_path']}`
- Artifact index: `{state['phase_b0a_result']['artifact_index_path']}`
- Artifact SHA256: `{state['phase_b0a_result']['artifact_sha256']}`
- Compression: `{state['phase_b0a_result']['compression']}`
- N_eff: `{state['phase_b0a_result']['n_eff']}`
- Top-cluster share: `{state['phase_b0a_result']['top_cluster_share']}`
- Cross-time stability median/min: `{state['phase_b0a_result']['cross_time_slice_stability_median']}` / `{state['phase_b0a_result']['cross_time_slice_stability_min']}`

## NEXTGEN-DARK Closure

{nextgen_items}

## B1S-CANARY Closure

{b1s_items}

- Decision: `{state['phase_b1s_result']['decision']}`
- Frozen repo SHA: `{state['phase_b1s_result']['frozen_repo_sha']}`
- Frozen manifest SHA256: `{state['phase_b1s_result']['frozen_manifest_sha256']}`
- Proposals / legal rate: `{state['phase_b1s_result']['proposal_rows']}` / `{state['phase_b1s_result']['legal_candidate_rate']}`
- Stratified admissions: `{state['phase_b1s_result']['actual_stratified_admissions']}` of planned `{state['phase_b1s_result']['planned_stratified_admissions']}`
- Stratified strict evaluations: `{state['phase_b1s_result']['actual_stratified_strict_evaluations']}` of planned `{state['phase_b1s_result']['planned_stratified_strict_evaluations']}`
- Global-top-K strict evaluations: `{state['phase_b1s_result']['global_top_k_strict_evaluations']}`
- Adaptive feedback queries: `{state['phase_b1s_result']['adaptive_feedback_queries']}`
- Execution acceptance: `{state['phase_b1s_result']['execution_acceptance']}` / `{state['phase_b1s_result']['fixed_budget_contract_status']}`
- Quota fill: `{state['phase_b1s_result']['quota_fill_rate']}`; natural underfill `{state['phase_b1s_result']['underfill_count']}` in `{state['phase_b1s_result']['underfill_lane']}`; rerun required `{state['phase_b1s_result']['rerun_required']}`
- Underfill explanation: {state['phase_b1s_result']['underfill_explanation']}

## CRYPTO NEXTGEN SEARCH EPOCH-0 Design Freeze

- Status: `{state['nextgen_epoch0']['status']}`
- Implementation subject: `{state['nextgen_epoch0']['implementation_subject_sha']}`
- Frozen manifest SHA256: `{state['nextgen_epoch0']['frozen_manifest_sha256']}`
- Proposals / lanes / seeds: `{state['nextgen_epoch0']['total_proposals']}` / `{state['nextgen_epoch0']['independent_lanes']}` / `{state['nextgen_epoch0']['fixed_seeds']}`
- Strict budgets: `{state['nextgen_epoch0']['planned_stratified_strict_evaluations']}` stratified + `{state['nextgen_epoch0']['planned_global_top_k_strict_evaluations']}` equal-budget global-top-K
- Performance started: `{state['nextgen_epoch0']['performance_started']}`
- Execution / strict fill: `{state['nextgen_epoch0']['execution_status']}` / `{state['nextgen_epoch0']['total_development_strict_evaluations']}` of `{state['nextgen_epoch0']['planned_logical_strict_evaluations']}` (`{state['nextgen_epoch0']['strict_fill_rate']}`)
- Development survivors / Pareto / frozen pack: `{state['nextgen_epoch0']['development_survivors']}` / `{state['nextgen_epoch0']['pareto_candidates']}` / `{state['nextgen_epoch0']['frozen_candidate_pack_rows']}`
- Natural full-identity underfill / rerun required: `{state['nextgen_epoch0']['natural_full_identity_underfill']}` / `{state['nextgen_epoch0']['rerun_required']}`
- Validated recommendation: `{state['nextgen_epoch0']['recommendation']}` — {state['nextgen_epoch0']['recommendation_basis']}
- Forward read / promotion / cross-epoch memory: `{state['nextgen_epoch0']['forward_read']}` / `{state['nextgen_epoch0']['candidate_promotion']}` / `{state['nextgen_epoch0']['cross_epoch_memory']}`

## CRYPTO NEXTGEN SEARCH EPOCH-1

- Status: `{state['nextgen_epoch1']['status']}`
- Accepted Epoch-0 subject: `{state['nextgen_epoch1']['accepted_epoch0_subject_sha']}`
- Revision subject: `{state['nextgen_epoch1']['revision_subject_sha']}`
- BBO offline replay: `{state['nextgen_epoch1']['bbo_replay_old_admissions']}` -> `{state['nextgen_epoch1']['bbo_replay_feasible_admissions']}`; history rewritten `{state['nextgen_epoch1']['history_rewritten']}`
- Design frozen / performance started / execution: `{state['nextgen_epoch1']['design_frozen']}` / `{state['nextgen_epoch1']['performance_started']}` / `{state['nextgen_epoch1']['execution_status']}`
- Attempts / persisted strict evaluations / rerun: `{state['nextgen_epoch1']['attempts']}` / `{state['nextgen_epoch1']['strict_evaluations_persisted']}` / `{state['nextgen_epoch1']['rerun_performed']}`
- Failure: `{state['nextgen_epoch1']['failure_type']}`
- Recommendation: `{state['nextgen_epoch1']['recommendation']}`
- Remote sync: `{state['epoch1_remote_sync']['status']}` for `{state['epoch1_remote_sync']['closure_subject_sha']}` after `{state['epoch1_remote_sync']['attempts']}` attempts
- Forward read / promotion / cross-epoch memory: `{state['nextgen_epoch1']['forward_read']}` / `{state['nextgen_epoch1']['candidate_promotion']}` / `{state['nextgen_epoch1']['cross_epoch_memory']}`

## CRYPTO NEXTGEN SEARCH EPOCH-1R

- Status: `{state['nextgen_epoch1r']['status']}`
- Repair scope: `{state['nextgen_epoch1r']['repair_scope']}`
- Failed evidence subject: `{state['nextgen_epoch1r']['failed_epoch1_subject_sha']}`
- Upstream changes — generator / grammar / objective / adaptive / seeds / budgets: `{state['nextgen_epoch1r']['proposal_generator_changed']}` / `{state['nextgen_epoch1r']['grammar_changed']}` / `{state['nextgen_epoch1r']['reward_objective_changed']}` / `{state['nextgen_epoch1r']['adaptive_algorithms_changed']}` / `{state['nextgen_epoch1r']['seeds_changed']}` / `{state['nextgen_epoch1r']['budgets_changed']}`
- Design frozen / strict started: `{state['nextgen_epoch1r']['design_frozen']}` / `{state['nextgen_epoch1r']['strict_evaluation_started']}`
- Frozen repo / manifest: `{state['nextgen_epoch1r'].get('frozen_repo_sha', 'not_frozen')}` / `{state['nextgen_epoch1r'].get('frozen_manifest_sha256', 'not_frozen')}`
- Execution / strict / natural underfill: `{state['nextgen_epoch1r'].get('execution_status', 'not_started')}` / `{state['nextgen_epoch1r'].get('executed_strict_evaluations', 0)}` / `{state['nextgen_epoch1r'].get('natural_underfill', False)}`
- Survivors / near misses / positive net LCB / adaptive successes: `{state['nextgen_epoch1r'].get('development_survivors', 0)}` / `{state['nextgen_epoch1r'].get('survivor_near_miss', 0)}` / `{state['nextgen_epoch1r'].get('positive_net_lcb', 0)}` / `{state['nextgen_epoch1r'].get('adaptive_successes', 0)}`
- Recommendation: `{state['nextgen_epoch1r'].get('recommendation', 'not_available')}`
- Remote sync: `{state['epoch1r_remote_sync']['status']}` for closure `{state['epoch1r_remote_sync']['closure_subject_sha']}` after `{state['epoch1r_remote_sync']['attempts']}` attempts

## CRYPTO EPOCH-2

- Status: `{state['nextgen_epoch2']['status']}`
- Hybrid comparison: `{state['nextgen_epoch2']['hybrid_comparison_status']}`
- Repair strategy: `{state['nextgen_epoch2']['repair_strategy_status']}`
- Calibration: `{state['nextgen_epoch2']['calibration_decision']}`; planted/null pass `{state['nextgen_epoch2']['planted_pass_rate']}` / `{state['nextgen_epoch2']['null_pass_rate']}`
- Frozen parents: `{state['nextgen_epoch2']['parent_rows']}` rows / `{state['nextgen_epoch2']['unique_parent_proposals']}` proposals / `{state['nextgen_epoch2']['unique_parent_exact_identities']}` exact identities
- Budget: `{state['nextgen_epoch2']['proposal_budget']}` proposals / `{state['nextgen_epoch2']['strict_budget']}` strict / seeds `{state['nextgen_epoch2']['fixed_seeds']}`
- Bias audit: `{state['nextgen_epoch2']['bias_audit']}`
- Design frozen / performance started: `{state['nextgen_epoch2']['design_frozen']}` / `{state['nextgen_epoch2']['performance_started']}`
- Forward read / promotion / cross-epoch memory: `{state['nextgen_epoch1r']['forward_read']}` / `{state['nextgen_epoch1r']['candidate_promotion']}` / `{state['nextgen_epoch1r']['cross_epoch_memory']}`

## CRYPTO EPOCH-2B Economic Bottleneck Audit

- Status: `{state['epoch2b_audit']['status']}`
- Main recommendation: `{state['epoch2b_audit']['main_recommendation']}`
- Existing logical strict rows read / new performance queries: `{state['epoch2b_audit']['logical_strict_rows_read']}` / `{state['epoch2b_audit']['new_performance_queries']}`
- Main median positive gross-LCB proxy fraction / rare-edge cost-kill share: `{state['epoch2b_audit']['main_positive_gross_lcb_proxy_fraction_median']}` / `{state['epoch2b_audit']['cost_killed_share_of_rare_positive_gross_lcb']}`
- Parent classes — no edge / portfolio transform / unstable: `{state['epoch2b_audit']['parents_no_economic_edge']}` / `{state['epoch2b_audit']['parents_portfolio_transform_required']}` / `{state['epoch2b_audit']['parents_unstable_neighbourhood']}`
- Adaptive operator cells without causal control / target crossing / collateral damage: `{state['epoch2b_audit']['adaptive_operator_cells_no_causal_control']}` / `{state['epoch2b_audit']['adaptive_target_gate_crossing_rate']}` / `{state['epoch2b_audit']['adaptive_collateral_damage_rate']}`
- Main NET_LCB near misses Epoch-1R -> Epoch-2 / distance change: `{state['epoch2b_audit']['epoch1r_main_net_near_misses']}` -> `{state['epoch2b_audit']['epoch2_main_net_near_misses']}` / `{state['epoch2b_audit']['near_miss_distance_relative_change']}`
- BBO secondary line: `{state['epoch2b_audit']['bbo_secondary_line']}`; positive exact / clusters / coverage `{state['epoch2b_audit']['bbo_positive_net_exact_identities']}` / `{state['epoch2b_audit']['bbo_behaviour_clusters']}` / `{state['epoch2b_audit']['bbo_coverage_ratio']}`

## NEXTGEN-DARK Allowed

""" + "\n".join(f"- {x}" for x in state["allowed_nextgen_dark"]) + "\n\n## NEXTGEN-DARK Prohibited\n\n" + "\n".join(f"- {x}" for x in state["prohibited_nextgen_dark"]) + """

## Phase B0A Allowed

""" + "\n".join(f"- {x}" for x in state["allowed_b0a"]) + "\n\n## Prohibited\n\n" + "\n".join(f"- {x}" for x in state["prohibited_b0a"]) + f"\n\n## Next Acceptance Gate\n\n{state['next_acceptance_gate']}\n"
    return {
        CURRENT_ARCH_PATH: current,
        BOUNDARY_PATH: boundary,
        EVOLUTION_PATH: evolution,
        STATE_PATH: state_doc,
    }


def build_documents(registry: dict[str, Any], state: dict[str, Any], decisions: list[dict[str, Any]], digest: str) -> None:
    for path, content in render_documents(registry, state, decisions, digest).items():
        path.write_text(content, encoding="utf-8")


def artifact_paths(registry: dict[str, Any]) -> set[Path]:
    paths = {
        REGISTRY_PATH,
        STATE_SOURCE_PATH,
        DECISION_LOG_PATH,
        CURRENT_ARCH_PATH,
        BOUNDARY_PATH,
        EVOLUTION_PATH,
        GRAPH_PATH,
        STATE_PATH,
        RUN_MANIFEST_PATH,
        ATTESTATION_PATH,
        ACCEPTANCE_TEST_OUTPUT_PATH,
        B0P_MANIFEST_PATH,
        B0P_ATTESTATION_PATH,
        B0P_ACCEPTANCE_TEST_OUTPUT_PATH,
        B0A_MANIFEST_PATH,
        B0A_ARTIFACT_PATH,
        B0A_ARTIFACT_INDEX_PATH,
        NEXTGEN_MATERIALIZATION_PATH,
        NEXTGEN_COVERAGE_PATH,
        NEXTGEN_RUN_MANIFEST_PATH,
        NEXTGEN_ADR_PATH,
        CANARY_PLAN_PATH,
        B1S_FROZEN_MANIFEST_PATH,
        B1S_RUN_MANIFEST_PATH,
        B1S_REPORT_PATH,
        B1S_TEST_OUTPUT_PATH,
        B1S_ARTIFACT_INDEX_PATH,
        EPOCH0_SMOKE_PRE_PATH,
        EPOCH0_SMOKE_PATH,
        EPOCH0_FROZEN_MANIFEST_PATH,
        EPOCH0_CANARY_ATTRIBUTION_PATH,
        EPOCH0_CANARY_REPORT_PATH,
        EPOCH0_TEST_OUTPUT_PATH,
        EPOCH0_ARTIFACT_INDEX_PATH,
        EPOCH0_RUN_MANIFEST_PATH,
        EPOCH0_CLOSURE_VALIDATION_PATH,
        EPOCH0_COMPARATIVE_REPORT_PATH,
        EPOCH0_FAILURE_PATH,
        EPOCH1_ARTIFACT_INDEX_PATH,
        EPOCH1R_ARTIFACT_INDEX_PATH,
    }
    for node in registry["nodes"]:
        paths.update(REPO / raw for raw in [*node["implementation_path"], *node["artifact_test"]])
    return paths


def nextgen_artifact_paths(registry: dict[str, Any]) -> set[Path]:
    node_ids = {
        "nextgen_observation_fabric", "typed_temporal_program", "isolated_hypothesis_lanes",
        "anti_collapse_admission", "challenger_harness", "coverage_observability", "canary_plan",
    }
    paths = {
        REGISTRY_PATH, STATE_SOURCE_PATH, DECISION_LOG_PATH, CURRENT_ARCH_PATH, BOUNDARY_PATH,
        EVOLUTION_PATH, GRAPH_PATH, STATE_PATH, NEXTGEN_RUN_MANIFEST_PATH, NEXTGEN_ADR_PATH,
        CANARY_PLAN_PATH, NEXTGEN_MATERIALIZATION_PATH, NEXTGEN_COVERAGE_PATH,
        NEXTGEN_BOOKTICKER_PATH,
        NEXTGEN_TEST_OUTPUT_PATH,
        REPO / "scripts" / "crypto_architecture_control_plane.py",
        REPO / "tests" / "test_architecture_control_plane.py",
    }
    for node in registry["nodes"]:
        if node["id"] in node_ids:
            paths.update(REPO / raw for raw in [*node["implementation_path"], *node["artifact_test"]])
    paths.discard(NEXTGEN_ARTIFACT_INDEX_PATH)
    return paths


def b1s_artifact_paths(registry: dict[str, Any]) -> set[Path]:
    node_ids = {"b1s_main_canary", "b1s_bbo_micro_canary", "b1s_canary_control"}
    paths = {
        REGISTRY_PATH, STATE_SOURCE_PATH, DECISION_LOG_PATH, CURRENT_ARCH_PATH, BOUNDARY_PATH,
        EVOLUTION_PATH, GRAPH_PATH, STATE_PATH, B1S_FROZEN_MANIFEST_PATH, B1S_RUN_MANIFEST_PATH,
        B1S_REPORT_PATH, B1S_TEST_OUTPUT_PATH, RUN_MANIFEST_PATH,
        REPO / "scripts" / "crypto_architecture_control_plane.py",
        REPO / "tests" / "test_architecture_control_plane.py",
    }
    for node in registry["nodes"]:
        if node["id"] in node_ids:
            paths.update(REPO / raw for raw in [*node["implementation_path"], *node["artifact_test"]])
    paths.discard(B1S_ARTIFACT_INDEX_PATH)
    return paths


def epoch0_artifact_paths(registry: dict[str, Any]) -> set[Path]:
    node_ids = {
        "nextgen_mechanism_registry", "nextgen_search_engine", "development_multiobjective_reward",
        "epoch0_frozen_design", "epoch0_execution",
    }
    paths = {
        REGISTRY_PATH, STATE_SOURCE_PATH, DECISION_LOG_PATH, CURRENT_ARCH_PATH, BOUNDARY_PATH,
        EVOLUTION_PATH, GRAPH_PATH, STATE_PATH, EPOCH0_SMOKE_PRE_PATH, EPOCH0_SMOKE_PATH,
        EPOCH0_FROZEN_MANIFEST_PATH, EPOCH0_CANARY_ATTRIBUTION_PATH, EPOCH0_CANARY_REPORT_PATH,
        EPOCH0_TEST_OUTPUT_PATH, RUN_MANIFEST_PATH,
        EPOCH0_RUN_MANIFEST_PATH, EPOCH0_CLOSURE_VALIDATION_PATH,
        EPOCH0_COMPARATIVE_REPORT_PATH, EPOCH0_FAILURE_PATH,
        REPO / "scripts" / "crypto_architecture_control_plane.py",
        REPO / "tests" / "test_architecture_control_plane.py",
    }
    for node in registry["nodes"]:
        if node["id"] in node_ids:
            paths.update(REPO / raw for raw in [*node["implementation_path"], *node["artifact_test"]])
    if EPOCH0_RUN_MANIFEST_PATH.exists():
        run = load_json(EPOCH0_RUN_MANIFEST_PATH)
        paths.update(REPO / item["path"] for item in run.get("outputs", []))
    paths.discard(EPOCH0_ARTIFACT_INDEX_PATH)
    return paths


def epoch1_artifact_paths(registry: dict[str, Any]) -> set[Path]:
    node_ids = {"epoch1_search_revision", "epoch1_frozen_design", "epoch1_execution"}
    paths = {
        REGISTRY_PATH, STATE_SOURCE_PATH, DECISION_LOG_PATH, CURRENT_ARCH_PATH, BOUNDARY_PATH,
        EVOLUTION_PATH, GRAPH_PATH, STATE_PATH, RUN_MANIFEST_PATH, EPOCH1_SMOKE_PATH,
        EPOCH1_FROZEN_MANIFEST_PATH, EPOCH1_FAILURE_PATH, EPOCH1_CLOSURE_MANIFEST_PATH,
        REPO / "scripts" / "crypto_architecture_control_plane.py",
        REPO / "tests" / "test_architecture_control_plane.py",
    }
    for node in registry["nodes"]:
        if node["id"] in node_ids:
            paths.update(REPO / raw for raw in [*node["implementation_path"], *node["artifact_test"]])
    paths.discard(EPOCH1_ARTIFACT_INDEX_PATH)
    return paths


def epoch1r_artifact_paths(registry: dict[str, Any]) -> set[Path]:
    node_ids = {"epoch1r_admission_repair", "epoch1r_frozen_design", "epoch1r_execution"}
    paths = {
        REGISTRY_PATH, STATE_SOURCE_PATH, DECISION_LOG_PATH, CURRENT_ARCH_PATH, BOUNDARY_PATH,
        EVOLUTION_PATH, GRAPH_PATH, STATE_PATH, RUN_MANIFEST_PATH, EPOCH1R_PACK_PATH,
        EPOCH1R_PACK_MANIFEST_PATH, EPOCH1R_FULL_IDENTITIES_PATH, EPOCH1R_CAPACITY_PATH,
        EPOCH1R_ASSIGNMENT_PATH, EPOCH1R_PREFLIGHT_PATH,
        EPOCH1R_FROZEN_PATH,
        EPOCH1R_RUN_PATH,
        REPO / "scripts" / "crypto_architecture_control_plane.py",
        REPO / "tests" / "test_architecture_control_plane.py",
    }
    for node in registry["nodes"]:
        if node["id"] in node_ids:
            paths.update(REPO / raw for raw in [*node["implementation_path"], *node["artifact_test"]])
    paths.discard(EPOCH1R_ARTIFACT_INDEX_PATH)
    return paths


def b0a_artifact_paths(registry: dict[str, Any]) -> set[Path]:
    node = next(item for item in registry["nodes"] if item["id"] == "frozen_signal_behaviour_qualification")
    paths = {REPO / raw for raw in [*node["implementation_path"], *node["artifact_test"]]}
    paths.add(B0A_MANIFEST_PATH)
    paths.add(B0A_ARTIFACT_PATH)
    paths.update(
        {
            REGISTRY_PATH,
            STATE_SOURCE_PATH,
            DECISION_LOG_PATH,
            CURRENT_ARCH_PATH,
            BOUNDARY_PATH,
            EVOLUTION_PATH,
            GRAPH_PATH,
            STATE_PATH,
            RUN_MANIFEST_PATH,
            REPO / "scripts" / "crypto_architecture_control_plane.py",
            REPO / "tests" / "test_architecture_control_plane.py",
        }
    )
    paths.discard(B0A_ARTIFACT_INDEX_PATH)
    return paths


def update_graph(registry: dict[str, Any], state: dict[str, Any], digest: str) -> None:
    graph = load_json(GRAPH_PATH)
    graph["nodes"] = [node for node in graph.get("nodes", []) if not str(node.get("id", "")).startswith("control_")]
    graph["links"] = [edge for edge in graph.get("links", []) if not str(edge.get("edge_id", "")).startswith("control_")]
    for node in registry["nodes"]:
        graph["nodes"].append({
            "id": f"control_{node['id']}", "label": node["label"], "file_type": "architecture_control",
            "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": relative(REGISTRY_PATH),
            "status": node["status"], "implementation_path": node["implementation_path"], "entrypoint": node["entrypoint"],
            "input": node["input"], "output": node["output"], "data_role": node["data_role"],
            "feedback_permission": node["feedback_permission"], "artifact_test": node["artifact_test"],
            "last_verified_sha": node["last_verified_sha"], "blocker": node["blocker"], "weight": 1.0,
        })
    for idx, edge in enumerate(registry["edges"]):
        graph["links"].append({
            "edge_id": f"control_edge_{idx:03d}", "source": f"control_{edge['source']}",
            "target": f"control_{edge['target']}", "relationship": edge["kind"], "label": edge["label"],
            "forbidden": edge["kind"] == "FORBIDDEN", "confidence": "EXTRACTED", "confidence_score": 1.0,
            "source_file": relative(REGISTRY_PATH), "weight": 1.0,
        })
    graph.setdefault("graph", {})["architecture_control_plane"] = {
        "registry": relative(REGISTRY_PATH), "registry_sha256": digest, "generator": relative(Path(__file__)),
        "graphify_status": "UNAVAILABLE_REGISTRY_OVERLAY_ACTIVE", "control_node_count": len(registry["nodes"]),
        "control_edge_count": len(registry["edges"]), "phase_status": state["current_phase"],
        "production_observation_qualification_status": state["production_observation_qualification_status"],
        "active_stage": state["active_stage"],
        "accepted_subject_sha": state["phase_b0_acceptance"]["accepted_subject_sha"],
        "b0p_acceptance_status": state["phase_b0p_acceptance"]["status"],
        "b0p_accepted_subject_sha": state["phase_b0p_acceptance"]["accepted_subject_sha"],
        "frozen_signal_behaviour_status": state["frozen_signal_behaviour_status"],
        "b0a_accepted_subject_sha": state["phase_b0a_acceptance"]["accepted_subject_sha"],
        "nextgen_dark_status": state["nextgen_dark_status"],
        "formal_search_status": state["formal_search_status"],
        "canary_status": state["canary_status"],
        "adaptive_cross_epoch_memory_status": state["adaptive_cross_epoch_memory_status"],
        "candidate_promotion_status": state["candidate_promotion_status"],
        "b1s_canary_decision": state["phase_b1s_result"]["decision"],
        "b1s_frozen_repo_sha": state["phase_b1s_result"]["frozen_repo_sha"],
        "epoch0_status": state["nextgen_epoch0"]["status"],
        "epoch0_frozen_manifest_sha256": state["nextgen_epoch0"]["frozen_manifest_sha256"],
        "epoch0_performance_started": state["nextgen_epoch0"]["performance_started"],
        "epoch0_execution_status": state["nextgen_epoch0"].get("execution_status"),
        "epoch0_total_development_strict_evaluations": state["nextgen_epoch0"].get("total_development_strict_evaluations"),
        "epoch0_recommendation": state["nextgen_epoch0"].get("recommendation"),
        "epoch1_status": state["nextgen_epoch1"]["status"],
        "epoch1_design_frozen": state["nextgen_epoch1"]["design_frozen"],
        "epoch1_performance_started": state["nextgen_epoch1"]["performance_started"],
        "epoch1_execution_status": state["nextgen_epoch1"]["execution_status"],
        "epoch1_recommendation": state["nextgen_epoch1"].get("recommendation"),
        "epoch1_remote_sync_status": state["epoch1_remote_sync"]["status"],
        "epoch1r_status": state["nextgen_epoch1r"]["status"],
        "epoch1r_design_frozen": state["nextgen_epoch1r"]["design_frozen"],
        "epoch1r_strict_evaluation_started": state["nextgen_epoch1r"]["strict_evaluation_started"],
        "epoch1r_preflight_status": state["nextgen_epoch1r"].get("preflight_status"),
        "epoch1r_strict_assignment_total": state["nextgen_epoch1r"].get("strict_assignment_total"),
        "epoch1r_frozen_manifest_sha256": state["nextgen_epoch1r"].get("frozen_manifest_sha256"),
        "epoch1r_execution_status": state["nextgen_epoch1r"].get("execution_status"),
        "epoch1r_executed_strict_evaluations": state["nextgen_epoch1r"].get("executed_strict_evaluations"),
        "epoch1r_recommendation": state["nextgen_epoch1r"].get("recommendation"),
        "epoch1r_remote_sync_status": state["epoch1r_remote_sync"]["status"],
        "epoch2_status": state["nextgen_epoch2"]["status"],
        "epoch2_design_frozen": state["nextgen_epoch2"]["design_frozen"],
        "epoch2_performance_started": state["nextgen_epoch2"]["performance_started"],
        "epoch2b_status": state["epoch2b_audit"]["status"],
        "epoch2b_main_recommendation": state["epoch2b_audit"]["main_recommendation"],
        "epoch2b_new_performance_queries": state["epoch2b_audit"]["new_performance_queries"],
        "mechanism_data_inventory_status": state["mechanism_data_expansion0"]["inventory_status"],
        "mechanism_data_first_release_candidate": state["mechanism_data_expansion0"]["first_release_candidate"],
        "mechanism_data_first_release_status": state["mechanism_data_expansion0"]["first_release_status"],
        "mechanism_data_first_release_content_sha256": state["mechanism_data_expansion0"]["first_release_content_sha256"],
        "mechanism_data_benchmark_status": state["mechanism_data_expansion0"]["benchmark_status"],
        "mechanism_data_stage_status": state["mechanism_data_expansion0"]["stage_status"],
        "mechanism_data_stage_recommendation": state["mechanism_data_expansion0"]["stage_recommendation"],
        "epoch2b_remote_sync_status": state["epoch2b_remote_sync"]["status"],
        "mechanism_data_closure_remote_status": state["mechanism_data_expansion0"]["closure_remote_status"],
        "research_status": state["research_status"], "phase_b1_status": state["phase_b1_status"],
        "forward_data_status": state["forward_data_status"],
    }
    graph.pop("built_at_commit", None)
    graph["built_at_accepted_subject"] = state["phase_b0a_acceptance"]["accepted_subject_sha"]
    GRAPH_PATH.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_control_artifacts(registry: dict[str, Any], state: dict[str, Any], digest: str) -> None:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    acceptance = state["phase_b0_acceptance"]
    test_evidence = acceptance_test_evidence(state)
    attestation = {
        "attestation_id": "PHASE-B0-ACCEPTANCE-20260711",
        "attestation_status": state["current_phase"],
        "accepted_subject_sha": acceptance["accepted_subject_sha"],
        "accepted_subject_remote_ref": acceptance["accepted_subject_remote_ref"],
        "attestation_commit_policy": acceptance["attestation_commit_policy"],
        "production_observation_qualification_status": acceptance["production_observation_qualification_status_at_acceptance"],
        "research_status": state["research_status"],
        "phase_b1_status": state["phase_b1_status"],
        "forward_data_status": state["forward_data_status"],
        "test_evidence": test_evidence,
        "scope": "control-plane acceptance closure only; no B0 implementation logic changed",
    }
    if not ATTESTATION_PATH.exists():
        ATTESTATION_PATH.write_text(json.dumps(attestation, indent=2) + "\n", encoding="utf-8")
    funding_summary = load_json(B0P_FUNDING_SUMMARY_PATH)
    identity_summary = load_json(B0P_IDENTITY_SUMMARY_PATH)
    def observed(flag: str) -> bool:
        return bool(funding_summary.get(flag, False) or identity_summary.get(flag, False))

    b0p_manifest = {
        "manifest_id": "CRYPTO-B0P-QUALIFICATION-20260711",
        "decision": state["production_observation_qualification_status"],
        "funding_status": funding_summary["decision"],
        "identity_status": identity_summary["decision"],
        "activation_status": identity_summary["activation_status"],
        "funding_summary": relative(B0P_FUNDING_SUMMARY_PATH),
        "identity_summary": relative(B0P_IDENTITY_SUMMARY_PATH),
        "registry_sha256": digest,
        "search_started": observed("search_started"),
        "forward_performance_read": observed("forward_performance_read"),
        "state_event_reward_connected": observed("state_event_reward_connected"),
        "cem_ucb_mcts_updated": observed("cem_ucb_mcts_updated"),
        "a7mem_updated": observed("a7mem_updated"),
        "candidate_selection_performed": observed("candidate_selection_performed"),
        "b1_lane_integration": observed("b1_lane_integration"),
        "large_search_authorized": observed("large_search_authorized"),
        "alpha_ready": observed("alpha_ready"),
    }
    B0P_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not B0P_MANIFEST_PATH.exists():
        B0P_MANIFEST_PATH.write_text(json.dumps(b0p_manifest, indent=2) + "\n", encoding="utf-8")
    b0p_acceptance = state["phase_b0p_acceptance"]
    b0p_test_evidence = b0p_acceptance_test_evidence(state)
    b0p_attestation = {
        "attestation_id": "PHASE-B0P-PARTIAL-ACCEPTANCE-20260711",
        "attestation_status": b0p_acceptance["status"],
        "accepted_subject_sha": b0p_acceptance["accepted_subject_sha"],
        "accepted_subject_remote_ref": b0p_acceptance["accepted_subject_remote_ref"],
        "attestation_commit_policy": b0p_acceptance["attestation_commit_policy"],
        "funding_status": b0p_acceptance["funding_status"],
        "identity_status": b0p_acceptance["identity_status"],
        "activation_status": b0p_acceptance["activation_status"],
        "research_status": state["research_status"],
        "phase_b1_status": state["phase_b1_status"],
        "forward_data_status": state["forward_data_status"],
        "authorized_next_stage": "PHASE_B0A_FROZEN_SIGNAL_BEHAVIOUR_QUALIFICATION",
        "test_evidence": b0p_test_evidence,
        "scope": "independent partial acceptance of the fixed B0P subject; no B0P implementation logic changed",
    }
    if not B0P_ATTESTATION_PATH.exists():
        B0P_ATTESTATION_PATH.write_text(json.dumps(b0p_attestation, indent=2) + "\n", encoding="utf-8")
    b0a_manifest = load_json(B0A_MANIFEST_PATH)
    nextgen_materialization = load_json(NEXTGEN_MATERIALIZATION_PATH)
    nextgen_bookticker = load_json(NEXTGEN_BOOKTICKER_PATH)
    canary = load_json(CANARY_PLAN_PATH)
    nextgen_manifest = {
        "manifest_id": "CRYPTO-NEXTGEN-DARK-CLOSURE-20260711",
        "decision": state["nextgen_dark_status"],
        "accepted_b0a_subject_sha": state["phase_b0a_acceptance"]["accepted_subject_sha"],
        "materialization_manifest": relative(NEXTGEN_MATERIALIZATION_PATH),
        "materialization_artifact_hash": nextgen_materialization["artifact_hash"],
        "materialization_content_sha256": nextgen_materialization["content_sha256"],
        "materialization_reproducible": True,
        "rows": nextgen_materialization["rows"],
        "symbols": nextgen_materialization["symbols"],
        "unavailable_states": [
            item["state_id"] for item in nextgen_materialization["availability"]
            if item["status"] != "MATERIALIZED" and item["state_id"] != "depth_liquidity_state"
        ],
        "partially_available_states": ["depth_liquidity_state"],
        "pc1_top_of_book_manifest": relative(NEXTGEN_BOOKTICKER_PATH),
        "pc1_top_of_book_qualification": nextgen_bookticker["qualification"],
        "pc1_top_of_book_artifact_hash": nextgen_bookticker["artifact_hash"],
        "pc1_top_of_book_rows": nextgen_bookticker["rows"],
        "pc1_top_of_book_coordinate_coverage_ratio": nextgen_bookticker["coordinate_coverage_ratio"],
        "pc1_top_of_book_depth_semantics": nextgen_bookticker["depth_semantics"],
        "temporal_primitives_registered": 13,
        "isolated_lanes_registered": 7,
        "canary_plan": relative(CANARY_PLAN_PATH),
        "canary_status": canary["status"],
        "artifact_index": relative(NEXTGEN_ARTIFACT_INDEX_PATH),
        "registry_sha256": digest,
        "test_evidence": nextgen_test_evidence(),
        "search_started": False,
        "performance_evaluated": False,
        "forward_read": False,
        "state_event_reward_connected": False,
        "memory_updated": False,
        "scheduler_started": False,
        "canary_started": False,
        "formal_search_unlocked": False,
        "phase_b1_unlocked": False,
    }
    NEXTGEN_RUN_MANIFEST_PATH.write_text(json.dumps(nextgen_manifest, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "manifest_id": "PHASE-A-B0-B0P-RUN-MANIFEST-20260711", "phase_a_status": state["phase_a_status"],
        "collapse_status": state["collapse_status"], "research_status": state["research_status"],
        "current_phase": state["current_phase"], "phase_b1_status": state["phase_b1_status"],
        "forward_data_status": state["forward_data_status"], "registry_sha256": digest,
        "production_observation_qualification_status": state["production_observation_qualification_status"],
        "active_stage": state["active_stage"],
        "accepted_subject_sha": acceptance["accepted_subject_sha"],
        "acceptance_attestation": relative(ATTESTATION_PATH), "test_evidence": test_evidence,
        "graph_control_nodes": len(registry["nodes"]), "graph_control_edges": len(registry["edges"]),
        "b0_items": state["b0_items"], "search_started": False, "forward_performance_read": False,
        "b0p_items": state["b0p_items"],
        "b0p_acceptance_status": b0p_acceptance["status"],
        "b0p_accepted_subject_sha": b0p_acceptance["accepted_subject_sha"],
        "b0p_acceptance_attestation": relative(B0P_ATTESTATION_PATH),
        "b0p_acceptance_test_evidence": b0p_test_evidence,
        "frozen_signal_behaviour_status": state["frozen_signal_behaviour_status"],
        "b0a_run_manifest": relative(B0A_MANIFEST_PATH),
        "b0a_artifact": relative(B0A_ARTIFACT_PATH),
        "b0a_artifact_sha256": b0a_manifest["artifact_sha256"],
        "b0a_artifact_index": relative(B0A_ARTIFACT_INDEX_PATH),
        "b0a_items": state["b0a_items"],
        "artifact_index": relative(ARTIFACT_INDEX_PATH), "decision_log": relative(DECISION_LOG_PATH),
        "b0p_qualification_manifest": relative(B0P_MANIFEST_PATH),
        "nextgen_dark_status": state["nextgen_dark_status"],
        "formal_search_status": state["formal_search_status"],
        "nextgen_dark_run_manifest": relative(NEXTGEN_RUN_MANIFEST_PATH),
        "nextgen_dark_artifact_index": relative(NEXTGEN_ARTIFACT_INDEX_PATH),
        "b1s_canary_status": state["phase_b1s_result"]["decision"],
        "b1s_frozen_run_manifest": relative(B1S_FROZEN_MANIFEST_PATH),
        "b1s_canary_manifest": relative(B1S_RUN_MANIFEST_PATH),
        "b1s_artifact_index": relative(B1S_ARTIFACT_INDEX_PATH),
        "b1s_test_evidence": b1s_test_evidence(),
        "epoch0_status": state["nextgen_epoch0"]["status"],
        "epoch0_frozen_design_manifest": relative(EPOCH0_FROZEN_MANIFEST_PATH),
        "epoch0_frozen_manifest_sha256": state["nextgen_epoch0"]["frozen_manifest_sha256"],
        "epoch0_artifact_index": relative(EPOCH0_ARTIFACT_INDEX_PATH),
        "epoch0_test_evidence": epoch0_test_evidence(),
        "epoch0_run_manifest": relative(EPOCH0_RUN_MANIFEST_PATH),
        "epoch0_closure_validation": relative(EPOCH0_CLOSURE_VALIDATION_PATH),
        "epoch0_total_development_strict_evaluations": state["nextgen_epoch0"].get("total_development_strict_evaluations"),
        "epoch0_recommendation": state["nextgen_epoch0"].get("recommendation"),
        "epoch1_status": state["nextgen_epoch1"]["status"],
        "epoch1_design_frozen": state["nextgen_epoch1"]["design_frozen"],
        "epoch1_performance_started": state["nextgen_epoch1"]["performance_started"],
        "epoch1_execution_status": state["nextgen_epoch1"]["execution_status"],
        "epoch1_closure_manifest": relative(EPOCH1_CLOSURE_MANIFEST_PATH),
        "epoch1_artifact_index": relative(EPOCH1_ARTIFACT_INDEX_PATH),
        "epoch1_recommendation": state["nextgen_epoch1"].get("recommendation"),
        "epoch1_remote_sync": state["epoch1_remote_sync"],
        "epoch1r_status": state["nextgen_epoch1r"]["status"],
        "epoch1r_design_frozen": state["nextgen_epoch1r"]["design_frozen"],
        "epoch1r_strict_evaluation_started": state["nextgen_epoch1r"]["strict_evaluation_started"],
        "epoch1r_preflight": relative(EPOCH1R_PREFLIGHT_PATH),
        "epoch1r_artifact_index": relative(EPOCH1R_ARTIFACT_INDEX_PATH),
        "epoch1r_strict_assignment_total": state["nextgen_epoch1r"].get("strict_assignment_total"),
        "epoch1r_frozen_manifest": relative(EPOCH1R_FROZEN_PATH),
        "epoch1r_frozen_manifest_sha256": state["nextgen_epoch1r"].get("frozen_manifest_sha256"),
        "epoch1r_run_manifest": relative(EPOCH1R_RUN_PATH),
        "epoch1r_execution_status": state["nextgen_epoch1r"].get("execution_status"),
        "epoch1r_executed_strict_evaluations": state["nextgen_epoch1r"].get("executed_strict_evaluations"),
        "epoch1r_recommendation": state["nextgen_epoch1r"].get("recommendation"),
        "epoch1r_remote_sync": state["epoch1r_remote_sync"],
        "epoch2_status": state["nextgen_epoch2"]["status"],
        "epoch2_calibration_decision": state["nextgen_epoch2"]["calibration_decision"],
        "epoch2_parent_rows": state["nextgen_epoch2"]["parent_rows"],
        "epoch2_design_frozen": state["nextgen_epoch2"]["design_frozen"],
        "epoch2_performance_started": state["nextgen_epoch2"]["performance_started"],
        "epoch2b_status": state["epoch2b_audit"]["status"],
        "epoch2b_main_recommendation": state["epoch2b_audit"]["main_recommendation"],
        "epoch2b_new_performance_queries": state["epoch2b_audit"]["new_performance_queries"],
        "mechanism_data_inventory_status": state["mechanism_data_expansion0"]["inventory_status"],
        "mechanism_data_inventory_manifest": relative(MECHANISM_DATA_INVENTORY_MANIFEST_PATH),
        "mechanism_data_inventory_artifact_index": relative(MECHANISM_DATA_INVENTORY_INDEX_PATH),
        "mechanism_data_first_release_candidate": state["mechanism_data_expansion0"]["first_release_candidate"],
        "mechanism_data_first_release_status": state["mechanism_data_expansion0"]["first_release_status"],
        "native_aggtrades_release_manifest": relative(NATIVE_AGGTRADES_RELEASE_MANIFEST_PATH),
        "native_aggtrades_release_artifact_index": relative(NATIVE_AGGTRADES_RELEASE_INDEX_PATH),
        "native_aggtrades_release_content_sha256": state["mechanism_data_expansion0"]["first_release_content_sha256"],
        "native_aggtrades_benchmark_summary": relative(NATIVE_AGGTRADES_BENCHMARK_SUMMARY_PATH),
        "native_aggtrades_benchmark_status": state["mechanism_data_expansion0"]["benchmark_status"],
        "bbo_full_year_acquisition_summary": relative(BBO_ACQUISITION_SUMMARY_PATH),
        "mechanism_data_stage_status": state["mechanism_data_expansion0"]["stage_status"],
        "mechanism_data_stage_recommendation": state["mechanism_data_expansion0"]["stage_recommendation"],
        "mechanism_data_stage_closure_manifest": relative(MECHANISM_DATA_CLOSURE_MANIFEST_PATH),
        "mechanism_data_stage_artifact_index": relative(MECHANISM_DATA_CLOSURE_INDEX_PATH),
        "epoch2b_remote_sync": state["epoch2b_remote_sync"],
        "mechanism_data_closure_subject_sha": state["mechanism_data_expansion0"]["closure_subject_sha"],
        "mechanism_data_closure_remote_status": state["mechanism_data_expansion0"]["closure_remote_status"],
    }
    RUN_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    b0a_rows = []
    for path in sorted(b0a_artifact_paths(registry), key=lambda item: str(item)):
        b0a_rows.append(
            {
                "path": relative(path),
                "exists": str(path.exists()),
                "sha256": sha256_file(path) if path.is_file() else "",
                "role": "b0a_control_or_evidence",
            }
        )
    with B0A_ARTIFACT_INDEX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "exists", "sha256", "role"])
        writer.writeheader()
        writer.writerows(b0a_rows)
    b1s_rows = []
    for path in sorted(b1s_artifact_paths(registry), key=lambda item: str(item)):
        b1s_rows.append({
            "path": relative(path), "exists": str(path.exists()),
            "sha256": sha256_file(path) if path.is_file() else "", "role": "b1s_canary_closure",
        })
    with B1S_ARTIFACT_INDEX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "exists", "sha256", "role"])
        writer.writeheader()
        writer.writerows(b1s_rows)
    epoch0_rows = []
    for path in sorted(epoch0_artifact_paths(registry), key=lambda item: str(item)):
        epoch0_rows.append({
            "path": relative(path), "exists": str(path.exists()),
            "sha256": sha256_file(path) if path.is_file() else "", "role": "epoch0_design_freeze",
        })
    with EPOCH0_ARTIFACT_INDEX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "exists", "sha256", "role"])
        writer.writeheader()
        writer.writerows(epoch0_rows)
    epoch1_rows = []
    for path in sorted(epoch1_artifact_paths(registry), key=lambda item: str(item)):
        epoch1_rows.append({
            "path": relative(path), "exists": str(path.exists()),
            "sha256": sha256_file(path) if path.is_file() else "", "role": "epoch1_failed_closure",
        })
    with EPOCH1_ARTIFACT_INDEX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "exists", "sha256", "role"])
        writer.writeheader()
        writer.writerows(epoch1_rows)
    epoch1r_rows = []
    for path in sorted(epoch1r_artifact_paths(registry), key=lambda item: str(item)):
        epoch1r_rows.append({
            "path": relative(path), "exists": str(path.exists()),
            "sha256": sha256_file(path) if path.is_file() else "", "role": "epoch1r_repair_preflight",
        })
    with EPOCH1R_ARTIFACT_INDEX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "exists", "sha256", "role"])
        writer.writeheader()
        writer.writerows(epoch1r_rows)
    paths = artifact_paths(registry)
    rows = []
    for path in sorted(paths, key=lambda p: str(p)):
        rows.append({
            "path": relative(path), "exists": str(path.exists()), "sha256": sha256_file(path) if path.is_file() else "",
            "role": "control_plane" if path in {REGISTRY_PATH, STATE_SOURCE_PATH, DECISION_LOG_PATH, CURRENT_ARCH_PATH, BOUNDARY_PATH, EVOLUTION_PATH, GRAPH_PATH, STATE_PATH, RUN_MANIFEST_PATH} else "architecture_artifact",
        })
    with ARTIFACT_INDEX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "exists", "sha256", "role"])
        writer.writeheader()
        writer.writerows(rows)
    nextgen_rows = []
    for path in sorted(nextgen_artifact_paths(registry), key=lambda item: str(item)):
        nextgen_rows.append({
            "path": relative(path), "exists": str(path.exists()),
            "sha256": sha256_file(path) if path.is_file() else "", "role": "nextgen_dark_closure",
        })
    with NEXTGEN_ARTIFACT_INDEX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "exists", "sha256", "role"])
        writer.writeheader()
        writer.writerows(nextgen_rows)


def validate_outputs(registry: dict[str, Any]) -> None:
    validate_registry(registry)
    digest = sha256_file(REGISTRY_PATH)
    state = load_json(STATE_SOURCE_PATH)
    expected_documents = render_documents(registry, state, load_decisions(), digest)
    for path, expected_content in expected_documents.items():
        if path.read_text(encoding="utf-8") != expected_content:
            raise ValueError(f"generated control document drift: {relative(path)}")
    graph = load_json(GRAPH_PATH)
    meta = graph.get("graph", {}).get("architecture_control_plane", {})
    if meta.get("registry_sha256") != digest:
        raise ValueError("graph control overlay is stale")
    actual_control_nodes = {
        node["id"]: node for node in graph["nodes"] if str(node.get("id", "")).startswith("control_")
    }
    expected_control_nodes = {
        f"control_{node['id']}": {
            "id": f"control_{node['id']}", "label": node["label"], "file_type": "architecture_control",
            "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": relative(REGISTRY_PATH),
            "status": node["status"], "implementation_path": node["implementation_path"],
            "entrypoint": node["entrypoint"], "input": node["input"], "output": node["output"],
            "data_role": node["data_role"], "feedback_permission": node["feedback_permission"],
            "artifact_test": node["artifact_test"], "last_verified_sha": node["last_verified_sha"],
            "blocker": node["blocker"], "weight": 1.0,
        }
        for node in registry["nodes"]
    }
    if actual_control_nodes != expected_control_nodes:
        raise ValueError("graph control node fields do not exactly match registry")
    actual_control_edges = [
        edge for edge in graph["links"] if str(edge.get("edge_id", "")).startswith("control_edge_")
    ]
    expected_control_edges = [
        {
            "edge_id": f"control_edge_{index:03d}", "source": f"control_{edge['source']}",
            "target": f"control_{edge['target']}", "relationship": edge["kind"], "label": edge["label"],
            "forbidden": edge["kind"] == "FORBIDDEN", "confidence": "EXTRACTED", "confidence_score": 1.0,
            "source_file": relative(REGISTRY_PATH), "weight": 1.0,
        }
        for index, edge in enumerate(registry["edges"])
    ]
    if actual_control_edges != expected_control_edges:
        raise ValueError("graph control edges do not exactly match registry")
    if meta.get("control_node_count") != len(registry["nodes"]) or meta.get("control_edge_count") != len(registry["edges"]):
        raise ValueError("graph control counts do not match registry")
    forbidden = {(edge["source"], edge["target"]) for edge in graph["links"] if edge.get("forbidden")}
    expected_forbidden = {(f"control_{a}", f"control_{b}") for a, b in REQUIRED_FORBIDDEN_EDGES}
    if not expected_forbidden.issubset(forbidden):
        raise ValueError("graph missing required forbidden edges")
    manifest = load_json(RUN_MANIFEST_PATH)
    if manifest.get("registry_sha256") != digest or manifest.get("search_started") or manifest.get("forward_performance_read"):
        raise ValueError("run manifest mismatch or prohibited activity recorded")
    acceptance = state["phase_b0_acceptance"]
    accepted_subject_sha = acceptance["accepted_subject_sha"]
    if len(accepted_subject_sha) != 40 or any(char not in "0123456789abcdef" for char in accepted_subject_sha):
        raise ValueError("invalid accepted subject SHA")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", accepted_subject_sha, "HEAD"], cwd=REPO, check=False
    ).returncode:
        raise ValueError("accepted subject is not an ancestor of the acceptance closure")
    attestation = load_json(ATTESTATION_PATH)
    if attestation.get("accepted_subject_sha") != accepted_subject_sha:
        raise ValueError("acceptance attestation subject mismatch")
    if "acceptance_attestation_commit" in attestation:
        raise ValueError("acceptance attestation must not self-record its commit SHA")
    if manifest.get("accepted_subject_sha") != accepted_subject_sha:
        raise ValueError("run manifest accepted subject mismatch")
    if manifest.get("acceptance_attestation") != relative(ATTESTATION_PATH):
        raise ValueError("run manifest acceptance attestation mismatch")
    b0p_manifest = load_json(B0P_MANIFEST_PATH)
    if b0p_manifest.get("decision") != state["production_observation_qualification_status"]:
        raise ValueError("B0P qualification status mismatch")
    prohibited_b0p_flags = [
        "search_started", "forward_performance_read", "state_event_reward_connected", "cem_ucb_mcts_updated",
        "a7mem_updated", "candidate_selection_performed", "b1_lane_integration", "large_search_authorized", "alpha_ready",
    ]
    if any(b0p_manifest.get(flag) for flag in prohibited_b0p_flags):
        raise ValueError("B0P manifest records prohibited activity or authorization")
    funding_summary = load_json(B0P_FUNDING_SUMMARY_PATH)
    identity_summary = load_json(B0P_IDENTITY_SUMMARY_PATH)
    for flag in prohibited_b0p_flags:
        observed_flag = bool(funding_summary.get(flag, False) or identity_summary.get(flag, False))
        if b0p_manifest.get(flag) != observed_flag:
            raise ValueError(f"B0P aggregate evidence mismatch for {flag}")
    if meta.get("phase_status") != state["current_phase"] or meta.get("accepted_subject_sha") != accepted_subject_sha:
        raise ValueError("graph phase acceptance metadata mismatch")
    evidence = attestation.get("test_evidence", {})
    if evidence != acceptance_test_evidence(state) or manifest.get("test_evidence") != evidence:
        raise ValueError("acceptance test evidence mismatch")
    b0p_acceptance = state["phase_b0p_acceptance"]
    b0p_subject_sha = b0p_acceptance["accepted_subject_sha"]
    if len(b0p_subject_sha) != 40 or any(char not in "0123456789abcdef" for char in b0p_subject_sha):
        raise ValueError("invalid B0P accepted subject SHA")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", b0p_subject_sha, "HEAD"], cwd=REPO, check=False
    ).returncode:
        raise ValueError("B0P accepted subject is not an ancestor of the acceptance closure")
    b0p_attestation = load_json(B0P_ATTESTATION_PATH)
    if b0p_attestation.get("accepted_subject_sha") != b0p_subject_sha:
        raise ValueError("B0P partial-acceptance attestation subject mismatch")
    if "acceptance_attestation_commit" in b0p_attestation:
        raise ValueError("B0P partial-acceptance attestation must not self-record its commit SHA")
    b0p_evidence = b0p_attestation.get("test_evidence", {})
    if b0p_evidence != b0p_acceptance_test_evidence(state):
        raise ValueError("B0P partial-acceptance test evidence mismatch")
    if manifest.get("b0p_acceptance_status") != b0p_acceptance["status"]:
        raise ValueError("run manifest B0P partial-acceptance status mismatch")
    if manifest.get("b0p_accepted_subject_sha") != b0p_subject_sha:
        raise ValueError("run manifest B0P accepted subject mismatch")
    if manifest.get("b0p_acceptance_attestation") != relative(B0P_ATTESTATION_PATH):
        raise ValueError("run manifest B0P acceptance attestation mismatch")
    if manifest.get("b0p_acceptance_test_evidence") != b0p_evidence:
        raise ValueError("run manifest B0P acceptance evidence mismatch")
    b0a_manifest = load_json(B0A_MANIFEST_PATH)
    if b0a_manifest.get("decision") != state["frozen_signal_behaviour_status"]:
        raise ValueError("B0A signal behaviour status mismatch")
    prohibited_b0a_flags = [
        "search_started", "candidate_modified", "generator_field_added", "state_event_reward_connected",
        "cem_ucb_mcts_updated", "a7mem_updated", "candidate_selection_performed", "forward_performance_read",
        "return_label_read", "reward_read", "spent_oos_reoptimized", "b1_lane_integration",
    ]
    if any(b0a_manifest.get(flag) for flag in prohibited_b0a_flags):
        raise ValueError("B0A manifest records prohibited activity")
    if not b0a_manifest.get("reproducible") or not b0a_manifest.get("alias_reconstruction_pass"):
        raise ValueError("B0A reproducibility or alias reconstruction failed")
    if sha256_file(B0A_ARTIFACT_PATH) != b0a_manifest.get("artifact_sha256"):
        raise ValueError("B0A signal behaviour artifact hash drift")
    if manifest.get("b0a_run_manifest") != relative(B0A_MANIFEST_PATH):
        raise ValueError("run manifest B0A manifest path mismatch")
    if manifest.get("b0a_artifact_sha256") != b0a_manifest.get("artifact_sha256"):
        raise ValueError("run manifest B0A artifact hash mismatch")
    if manifest.get("b0a_artifact_index") != relative(B0A_ARTIFACT_INDEX_PATH):
        raise ValueError("run manifest B0A artifact index mismatch")
    with B0A_ARTIFACT_INDEX_PATH.open("r", encoding="utf-8", newline="") as handle:
        b0a_index_rows = list(csv.DictReader(handle))
    if {row["path"] for row in b0a_index_rows} != {relative(path) for path in b0a_artifact_paths(registry)}:
        raise ValueError("B0A artifact index paths do not match B0A control node")
    for row in b0a_index_rows:
        path = REPO / row["path"]
        if row["exists"] != str(path.exists()) or row["sha256"] != (sha256_file(path) if path.is_file() else ""):
            raise ValueError(f"B0A artifact index hash drift: {row['path']}")
    if meta.get("frozen_signal_behaviour_status") != state["frozen_signal_behaviour_status"]:
        raise ValueError("graph B0A signal behaviour status mismatch")
    if meta.get("nextgen_dark_status") != state["nextgen_dark_status"]:
        raise ValueError("graph NEXTGEN-DARK status mismatch")
    b0a_subject = state["phase_b0a_acceptance"]["accepted_subject_sha"]
    if subprocess.run(["git", "merge-base", "--is-ancestor", b0a_subject, "HEAD"], cwd=REPO, check=False).returncode:
        raise ValueError("B0A accepted subject is not an ancestor of NEXTGEN-DARK closure")
    nextgen_manifest = load_json(NEXTGEN_RUN_MANIFEST_PATH)
    prohibited_nextgen = [
        "search_started", "performance_evaluated", "forward_read", "state_event_reward_connected",
        "memory_updated", "scheduler_started", "canary_started", "formal_search_unlocked", "phase_b1_unlocked",
    ]
    if nextgen_manifest.get("decision") != state["nextgen_dark_status"] or any(
        nextgen_manifest.get(flag) for flag in prohibited_nextgen
    ):
        raise ValueError("NEXTGEN-DARK manifest mismatch or prohibited activity recorded")
    if nextgen_manifest.get("test_evidence") != nextgen_test_evidence():
        raise ValueError("NEXTGEN-DARK test evidence mismatch")
    materialization = load_json(NEXTGEN_MATERIALIZATION_PATH)
    if materialization.get("artifact_hash") != nextgen_manifest.get("materialization_artifact_hash"):
        raise ValueError("NEXTGEN-DARK materialization hash mismatch")
    if materialization.get("forbidden_performance_columns_read") or materialization.get("forward_read"):
        raise ValueError("NEXTGEN-DARK materialization read prohibited data")
    bookticker = load_json(NEXTGEN_BOOKTICKER_PATH)
    if not bookticker.get("reproducible") or bookticker.get("performance_values_read") or bookticker.get("forward_performance_read"):
        raise ValueError("PC1 bookTicker qualification is non-reproducible or read prohibited data")
    if bookticker.get("depth_semantics") != "TOP_OF_BOOK_BBO_ONLY_NOT_MULTI_LEVEL_DEPTH":
        raise ValueError("PC1 bookTicker source must not claim multi-level depth")
    if bookticker.get("liquidation_source_found_on_pc1"):
        raise ValueError("PC1 audit evidence unexpectedly claims a liquidation source")
    canary = load_json(CANARY_PLAN_PATH)
    if canary.get("execution_authorized") or canary.get("started") or canary.get("data_access", {}).get("forward_read_allowed"):
        raise ValueError("CANARY must remain unauthorized and not started")
    b1s_frozen = load_json(B1S_FROZEN_MANIFEST_PATH)
    frozen_recorded = b1s_frozen.pop("frozen_manifest_sha256")
    frozen_actual = sha256_bytes(json.dumps(b1s_frozen, sort_keys=True, separators=(",", ":"), default=str).encode())
    if frozen_actual != frozen_recorded or frozen_recorded != state["phase_b1s_result"]["frozen_manifest_sha256"]:
        raise ValueError("B1S frozen manifest identity mismatch")
    b1s = load_json(B1S_RUN_MANIFEST_PATH)
    if b1s.get("decision") != state["phase_b1s_result"]["decision"]:
        raise ValueError("B1S decision mismatch")
    prohibited_b1s = [
        "candidate_promotion", "a7mem_updated", "adaptive_cross_epoch_memory_updated",
        "validation_test_recent_stress_forward_read", "policy_or_elite_persisted",
        "online_budget_or_threshold_changed", "additional_budget_added", "alpha_ready_claimed",
        "deployable_claimed", "oos_proven_claimed", "main_and_bbo_directly_ranked",
    ]
    if any(b1s.get(flag) for flag in prohibited_b1s):
        raise ValueError("B1S manifest records prohibited activity")
    expected_b1s_counts = {
        "proposal_rows": 5120, "stratified_admissions": 564, "stratified_strict_evaluations": 315,
        "global_top_k_strict_evaluations": 320, "logical_strict_evaluations": 635,
        "adaptive_feedback_queries": 64,
    }
    if any(b1s.get(key) != value for key, value in expected_b1s_counts.items()):
        raise ValueError("B1S fixed-budget actual counts drifted")
    if b1s.get("execution_status") != "COMPLETED" or not b1s.get("execution_acceptance") == "B1S_CANARY_EXECUTION_ACCEPTED":
        raise ValueError("B1S execution acceptance status mismatch")
    if b1s.get("quota_fill_rate") != 0.984375 or b1s.get("rerun_required"):
        raise ValueError("B1S natural quota underfill record mismatch")
    if b1s.get("repo_sha") != state["phase_b1s_result"]["frozen_repo_sha"]:
        raise ValueError("B1S frozen repo SHA mismatch")
    for output in b1s.get("outputs", []):
        path = REPO / output["path"]
        if sha256_file(path) != output["sha256"]:
            raise ValueError(f"B1S output hash drift: {output['path']}")
    comparison = list(csv.DictReader((B1S_ROOT / "stratified_vs_global_topk.csv").open("r", encoding="utf-8", newline="")))
    if any(row["direct_cross_panel_ranking_performed"].lower() == "true" for row in comparison):
        raise PermissionError("B1S main and BBO panels were directly ranked")
    if manifest.get("b1s_test_evidence") != b1s_test_evidence():
        raise ValueError("Phase A/B0 manifest B1S test evidence mismatch")
    epoch0_frozen = load_json(EPOCH0_FROZEN_MANIFEST_PATH)
    epoch0_recorded = epoch0_frozen.pop("frozen_manifest_sha256")
    epoch0_actual = sha256_bytes(json.dumps(epoch0_frozen, sort_keys=True, separators=(",", ":"), default=str).encode())
    if epoch0_actual != epoch0_recorded or epoch0_recorded != state["nextgen_epoch0"]["frozen_manifest_sha256"]:
        raise ValueError("Epoch-0 frozen design identity mismatch")
    if epoch0_frozen["status"] != "EPOCH0_DESIGN_FROZEN_NOT_STARTED" or epoch0_frozen["search_started"]:
        raise ValueError("Epoch-0 design freeze status mismatch")
    if epoch0_frozen["budget"]["total_proposals"] != 32768 or epoch0_frozen["budget"]["logical_strict_evaluations"] != 2048:
        raise ValueError("Epoch-0 frozen budget mismatch")
    smoke_pre = load_json(EPOCH0_SMOKE_PRE_PATH)
    smoke = load_json(EPOCH0_SMOKE_PATH)
    smoke_forbidden = ("performance_read", "target_return_read", "reward_read", "validation_test_recent_may_stress_forward_read")
    if any(smoke_pre.get(key) or smoke.get(key) for key in smoke_forbidden):
        raise PermissionError("Epoch-0 throughput smoke read performance")
    if smoke_pre.get("selected_budget_if_frozen_now") is not None or smoke.get("selected_budget_if_frozen_now") != 32768:
        raise ValueError("Epoch-0 pre/post optimization throughput decision mismatch")
    if meta.get("epoch0_status") != state["nextgen_epoch0"]["status"] or meta.get("epoch0_performance_started") != state["nextgen_epoch0"]["performance_started"]:
        raise ValueError("graph Epoch-0 status mismatch")
    epoch0_run = load_json(EPOCH0_RUN_MANIFEST_PATH)
    epoch0_closure = load_json(EPOCH0_CLOSURE_VALIDATION_PATH)
    prohibited_epoch0 = [
        "validation_test_recent_may_stress_forward_read", "candidate_promotion", "a7mem_updated",
        "cross_lane_memory_persisted", "cross_epoch_memory_persisted", "online_contract_changed",
        "additional_budget_added", "intermediate_human_reweighting", "alpha_ready_claimed",
        "oos_proven_claimed", "main_and_bbo_directly_ranked",
    ]
    if epoch0_run.get("decision") != "FROZEN_DEVELOPMENT_EPOCH_COMPLETED" or any(epoch0_run.get(flag) for flag in prohibited_epoch0):
        raise ValueError("Epoch-0 run decision mismatch or prohibited activity")
    if epoch0_run.get("proposal_rows") != 32768 or epoch0_run.get("total_development_strict_evaluations") != 1801:
        raise ValueError("Epoch-0 execution counts drifted")
    if epoch0_closure.get("validation_status") != "PASS_EPOCH0_CLOSURE_WITH_NATURAL_FULL_IDENTITY_UNDERFILL":
        raise ValueError("Epoch-0 closure validation status mismatch")
    if epoch0_closure.get("recommendation") != state["nextgen_epoch0"]["recommendation"]:
        raise ValueError("Epoch-0 closure recommendation mismatch")
    if epoch0_closure.get("rerun_required") or not epoch0_closure.get("natural_underfill"):
        raise ValueError("Epoch-0 natural underfill or rerun record mismatch")
    for output in epoch0_run.get("outputs", []):
        path = REPO / output["path"]
        if sha256_file(path) != output["sha256"]:
            raise ValueError(f"Epoch-0 output hash drift: {output['path']}")
    if manifest.get("epoch0_frozen_manifest_sha256") != epoch0_recorded or manifest.get("epoch0_test_evidence") != epoch0_test_evidence():
        raise ValueError("Phase A/B0 manifest Epoch-0 evidence mismatch")
    if manifest.get("epoch0_total_development_strict_evaluations") != 1801 or manifest.get("epoch0_recommendation") != epoch0_closure["recommendation"]:
        raise ValueError("Phase A/B0 manifest Epoch-0 execution summary mismatch")
    with ARTIFACT_INDEX_PATH.open("r", encoding="utf-8", newline="") as handle:
        index_rows = list(csv.DictReader(handle))
    indexed_paths = {row["path"] for row in index_rows}
    expected_paths = {relative(path) for path in artifact_paths(registry)}
    if indexed_paths != expected_paths:
        raise ValueError("artifact index paths do not match control registry")
    for row in index_rows:
        path = REPO / row["path"]
        expected_exists = str(path.exists())
        expected_sha = sha256_file(path) if path.is_file() else ""
        if row["exists"] != expected_exists or row["sha256"] != expected_sha:
            raise ValueError(f"artifact index hash drift: {row['path']}")
    with NEXTGEN_ARTIFACT_INDEX_PATH.open("r", encoding="utf-8", newline="") as handle:
        nextgen_index_rows = list(csv.DictReader(handle))
    if {row["path"] for row in nextgen_index_rows} != {
        relative(path) for path in nextgen_artifact_paths(registry)
    }:
        raise ValueError("NEXTGEN-DARK artifact index paths do not match closure scope")
    for row in nextgen_index_rows:
        path = REPO / row["path"]
        if row["exists"] != str(path.exists()) or row["sha256"] != (sha256_file(path) if path.is_file() else ""):
            raise ValueError(f"NEXTGEN-DARK artifact index hash drift: {row['path']}")
    with B1S_ARTIFACT_INDEX_PATH.open("r", encoding="utf-8", newline="") as handle:
        b1s_index_rows = list(csv.DictReader(handle))
    if {row["path"] for row in b1s_index_rows} != {relative(path) for path in b1s_artifact_paths(registry)}:
        raise ValueError("B1S artifact index paths do not match closure scope")
    for row in b1s_index_rows:
        path = REPO / row["path"]
        if row["exists"] != str(path.exists()) or row["sha256"] != (sha256_file(path) if path.is_file() else ""):
            raise ValueError(f"B1S artifact index hash drift: {row['path']}")
    with EPOCH0_ARTIFACT_INDEX_PATH.open("r", encoding="utf-8", newline="") as handle:
        epoch0_index_rows = list(csv.DictReader(handle))
    if {row["path"] for row in epoch0_index_rows} != {relative(path) for path in epoch0_artifact_paths(registry)}:
        raise ValueError("Epoch-0 artifact index paths do not match design-freeze scope")
    for row in epoch0_index_rows:
        path = REPO / row["path"]
        if row["exists"] != str(path.exists()) or row["sha256"] != (sha256_file(path) if path.is_file() else ""):
            raise ValueError(f"Epoch-0 artifact index hash drift: {row['path']}")
    epoch1_closure = load_json(EPOCH1_CLOSURE_MANIFEST_PATH)
    epoch1_failure = load_json(EPOCH1_FAILURE_PATH)
    prohibited_epoch1 = [
        "candidate_promotion", "a7mem_updated", "cross_epoch_memory", "online_contract_changed",
        "additional_budget", "seed_changed", "reward_changed", "admission_changed_after_freeze", "oos_claim",
    ]
    if epoch1_closure.get("decision") != "FROZEN_DEVELOPMENT_EPOCH1_FAILED" or any(epoch1_closure.get(flag) for flag in prohibited_epoch1):
        raise ValueError("Epoch-1 failed closure decision mismatch or prohibited activity")
    if epoch1_closure.get("attempts") != 1 or epoch1_closure.get("rerun_performed") or epoch1_closure.get("strict_evaluations_persisted") != 0:
        raise ValueError("Epoch-1 failed execution counts or rerun record mismatch")
    if epoch1_failure.get("status") != "FAILED_VISIBLE_NOT_DELETED" or epoch1_failure.get("error_type") != "KeyError":
        raise ValueError("Epoch-1 visible failure evidence mismatch")
    if manifest.get("epoch1_closure_manifest") != relative(EPOCH1_CLOSURE_MANIFEST_PATH) or manifest.get("epoch1_recommendation") != epoch1_closure["recommendation"]:
        raise ValueError("Phase A/B0 manifest Epoch-1 closure mismatch")
    with EPOCH1_ARTIFACT_INDEX_PATH.open("r", encoding="utf-8", newline="") as handle:
        epoch1_index_rows = list(csv.DictReader(handle))
    if {row["path"] for row in epoch1_index_rows} != {relative(path) for path in epoch1_artifact_paths(registry)}:
        raise ValueError("Epoch-1 artifact index paths do not match failed-closure scope")
    for row in epoch1_index_rows:
        path = REPO / row["path"]
        if row["exists"] != str(path.exists()) or row["sha256"] != (sha256_file(path) if path.is_file() else ""):
            raise ValueError(f"Epoch-1 artifact index hash drift: {row['path']}")
    epoch1r_pack = load_json(EPOCH1R_PACK_MANIFEST_PATH)
    epoch1r_preflight = load_json(EPOCH1R_PREFLIGHT_PATH)
    if epoch1r_pack.get("proposal_rows") != 32768 or epoch1r_pack.get("strict_evaluations") != 0:
        raise ValueError("Epoch-1R proposal pack count or strict boundary mismatch")
    if sha256_file(EPOCH1R_PACK_PATH) != epoch1r_pack.get("proposal_pack_sha256"):
        raise ValueError("Epoch-1R proposal pack hash drift")
    if epoch1r_preflight.get("status") != "PASS_EPOCH1R_ADMISSION_ONLY_PREFLIGHT" or epoch1r_preflight.get("strict_evaluations") != 0:
        raise ValueError("Epoch-1R admission-only preflight status mismatch")
    if not all(epoch1r_preflight.get("hard_gates", {}).values()) or epoch1r_preflight.get("return_label_read_for_preflight") or epoch1r_preflight.get("forward_read"):
        raise ValueError("Epoch-1R preflight hard gate or data-access violation")
    if epoch1r_preflight.get("strict_assignment_total") != state["nextgen_epoch1r"].get("strict_assignment_total"):
        raise ValueError("Epoch-1R preflight/state assignment count mismatch")
    if manifest.get("epoch1r_preflight") != relative(EPOCH1R_PREFLIGHT_PATH) or manifest.get("epoch1r_strict_assignment_total") != epoch1r_preflight["strict_assignment_total"]:
        raise ValueError("Phase A/B0 manifest Epoch-1R preflight mismatch")
    epoch1r_frozen = load_json(EPOCH1R_FROZEN_PATH)
    epoch1r_recorded = epoch1r_frozen.pop("frozen_manifest_sha256")
    epoch1r_actual = sha256_bytes(json.dumps(epoch1r_frozen, sort_keys=True, separators=(",", ":"), default=str).encode())
    if epoch1r_actual != epoch1r_recorded or epoch1r_recorded != state["nextgen_epoch1r"].get("frozen_manifest_sha256"):
        raise ValueError("Epoch-1R frozen manifest identity mismatch")
    if epoch1r_frozen.get("status") != "EPOCH1R_DESIGN_FROZEN_NOT_STARTED" or epoch1r_frozen.get("strict_evaluation_started"):
        raise ValueError("Epoch-1R design freeze status mismatch")
    if epoch1r_frozen.get("strict_assignment_total") != epoch1r_preflight["strict_assignment_total"]:
        raise ValueError("Epoch-1R frozen/preflight strict assignment mismatch")
    if manifest.get("epoch1r_frozen_manifest_sha256") != epoch1r_recorded:
        raise ValueError("Phase A/B0 manifest Epoch-1R frozen identity mismatch")
    epoch1r_run = load_json(EPOCH1R_RUN_PATH)
    prohibited_epoch1r = [
        "candidate_promotion", "a7mem_updated", "cross_epoch_memory", "online_contract_changed",
        "additional_budget", "seed_changed", "reward_changed", "admission_changed_after_freeze",
        "cross_panel_ranked", "oos_claim",
    ]
    if epoch1r_run.get("decision") != "FROZEN_DEVELOPMENT_EPOCH1R_COMPLETED_WITH_NATURAL_UNDERFILL" or any(epoch1r_run.get(flag) for flag in prohibited_epoch1r):
        raise ValueError("Epoch-1R run decision mismatch or prohibited activity")
    if epoch1r_run.get("frozen_manifest_sha256") != epoch1r_recorded or epoch1r_run.get("strict_assignment_total") != epoch1r_preflight["strict_assignment_total"]:
        raise ValueError("Epoch-1R run frozen identity or strict count mismatch")
    if epoch1r_run.get("development_survivors") != 0 or epoch1r_run.get("survivor_near_miss") != 84 or epoch1r_run.get("positive_net_lcb") != 2 or epoch1r_run.get("adaptive_successes") != 0:
        raise ValueError("Epoch-1R result metrics drifted")
    if epoch1r_run.get("recommendation") != state["nextgen_epoch1r"].get("recommendation"):
        raise ValueError("Epoch-1R recommendation/state mismatch")
    for output in epoch1r_run.get("outputs", []):
        path = REPO / output["path"]
        if sha256_file(path) != output["sha256"]:
            raise ValueError(f"Epoch-1R output hash drift: {output['path']}")
    if manifest.get("epoch1r_run_manifest") != relative(EPOCH1R_RUN_PATH) or manifest.get("epoch1r_recommendation") != epoch1r_run["recommendation"]:
        raise ValueError("Phase A/B0 manifest Epoch-1R execution mismatch")
    with EPOCH1R_ARTIFACT_INDEX_PATH.open("r", encoding="utf-8", newline="") as handle:
        epoch1r_index_rows = list(csv.DictReader(handle))
    if {row["path"] for row in epoch1r_index_rows} != {relative(path) for path in epoch1r_artifact_paths(registry)}:
        raise ValueError("Epoch-1R artifact index paths do not match repair/preflight scope")
    for row in epoch1r_index_rows:
        path = REPO / row["path"]
        if row["exists"] != str(path.exists()) or row["sha256"] != (sha256_file(path) if path.is_file() else ""):
            raise ValueError(f"Epoch-1R artifact index hash drift: {row['path']}")


def build() -> None:
    registry = materialize_registry()
    validate_registry(registry)
    digest = sha256_file(REGISTRY_PATH)
    state = load_json(STATE_SOURCE_PATH)
    decisions = load_decisions()
    build_documents(registry, state, decisions, digest)
    update_graph(registry, state, digest)
    write_control_artifacts(registry, state, digest)
    validate_outputs(registry)
    print(json.dumps({"status": "PASS_ARCHITECTURE_CONTROL_PLANE_SYNCED", "registry_sha256": digest, "nodes": len(registry["nodes"]), "edges": len(registry["edges"])}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["build", "check"])
    args = parser.parse_args()
    if args.mode == "build":
        build()
    else:
        registry = load_json(REGISTRY_PATH)
        validate_outputs(registry)
        print("PASS_ARCHITECTURE_CONTROL_PLANE_VALID")


if __name__ == "__main__":
    main()
