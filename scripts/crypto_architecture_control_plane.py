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

Status: `{state['current_phase']}` / `{state['phase_b0p_acceptance']['status']}` / `{state['production_observation_qualification_status']}` / `{state['frozen_signal_behaviour_status']}` / `{state['research_status']}` / `{state['phase_b1_status']}` / `{state['forward_data_status']}`.

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
- Phase B1 is frozen.

## Decision Timeline

{timeline}
"""
    items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["b0_items"])
    b0p_items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["b0p_items"])
    b0a_items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["b0a_items"])
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
- Active stage: `{state['active_stage']}`
- Phase B1: `{state['phase_b1_status']}`
- Forward data: `{state['forward_data_status']}`

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
    }
    for node in registry["nodes"]:
        paths.update(REPO / raw for raw in [*node["implementation_path"], *node["artifact_test"]])
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
        "research_status": state["research_status"], "phase_b1_status": state["phase_b1_status"],
        "forward_data_status": state["forward_data_status"],
    }
    graph.pop("built_at_commit", None)
    graph["built_at_accepted_subject"] = state["phase_b0_acceptance"]["accepted_subject_sha"]
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
    B0P_ATTESTATION_PATH.write_text(json.dumps(b0p_attestation, indent=2) + "\n", encoding="utf-8")
    b0a_manifest = load_json(B0A_MANIFEST_PATH)
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
