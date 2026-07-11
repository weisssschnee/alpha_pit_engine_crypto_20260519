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
B0P_FUNDING_SUMMARY_PATH = REPO / "runtime" / "a7b0p_funding_qualification_20260711" / "funding_qualification_summary.json"
B0P_IDENTITY_SUMMARY_PATH = REPO / "runtime" / "a7b0p_identity_qualification_20260711" / "identity_qualification_manifest.json"
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


def build_documents(registry: dict[str, Any], state: dict[str, Any], decisions: list[dict[str, Any]], digest: str) -> None:
    current = f"""# Current Architecture

Generated from `{relative(REGISTRY_PATH)}`. Registry SHA256: `{digest}`.

Status: `{state['current_phase']}` / `{state['production_observation_qualification_status']}` / `{state['research_status']}` / `{state['phase_b1_status']}` / `{state['forward_data_status']}`.

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
- Binance UM core12 funding observation is production-qualified through 2026-04-30; cross-venue qualification is not claimed.
- Phase B1 is frozen.

## Decision Timeline

{timeline}
"""
    items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["b0_items"])
    b0p_items = "\n".join(f"- `{item['id']}` {item['name']}: `{item['status']}`" for item in state["b0p_items"])
    state_doc = f"""# Crypto AlphaFactory Planning State

Registry SHA256: `{digest}`.

## Formal Status

- `{state['phase_a_status']}`
- `{state['collapse_status']}`
- `{state['research_status']}`
- Current phase: `{state['current_phase']}`
- Production observation qualification: `{state['production_observation_qualification_status']}`
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

## Phase B0P Allowed

""" + "\n".join(f"- {x}" for x in state["allowed_b0p"]) + "\n\n## Prohibited\n\n" + "\n".join(f"- {x}" for x in state["prohibited_b0p"]) + f"\n\n## Next Acceptance Gate\n\n{state['next_acceptance_gate']}\n"
    CURRENT_ARCH_PATH.write_text(current, encoding="utf-8")
    BOUNDARY_PATH.write_text(boundary, encoding="utf-8")
    EVOLUTION_PATH.write_text(evolution, encoding="utf-8")
    STATE_PATH.write_text(state_doc, encoding="utf-8")


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
    b0p_manifest = {
        "manifest_id": "CRYPTO-B0P-QUALIFICATION-20260711",
        "decision": state["production_observation_qualification_status"],
        "funding_status": funding_summary["decision"],
        "identity_status": identity_summary["decision"],
        "activation_status": identity_summary["activation_status"],
        "funding_summary": relative(B0P_FUNDING_SUMMARY_PATH),
        "identity_summary": relative(B0P_IDENTITY_SUMMARY_PATH),
        "registry_sha256": digest,
        "search_started": False,
        "forward_performance_read": False,
        "state_event_reward_connected": False,
        "cem_ucb_mcts_updated": False,
        "a7mem_updated": False,
        "candidate_selection_performed": False,
        "b1_lane_integration": False,
        "large_search_authorized": False,
        "alpha_ready": False,
    }
    B0P_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    B0P_MANIFEST_PATH.write_text(json.dumps(b0p_manifest, indent=2) + "\n", encoding="utf-8")
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
        "artifact_index": relative(ARTIFACT_INDEX_PATH), "decision_log": relative(DECISION_LOG_PATH),
        "b0p_qualification_manifest": relative(B0P_MANIFEST_PATH),
    }
    RUN_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    paths = {
        REGISTRY_PATH, STATE_SOURCE_PATH, DECISION_LOG_PATH, CURRENT_ARCH_PATH, BOUNDARY_PATH, EVOLUTION_PATH,
        GRAPH_PATH, STATE_PATH, RUN_MANIFEST_PATH, ATTESTATION_PATH, ACCEPTANCE_TEST_OUTPUT_PATH, B0P_MANIFEST_PATH,
    }
    for node in registry["nodes"]:
        paths.update(REPO / raw for raw in [*node["implementation_path"], *node["artifact_test"]])
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
    for path in [CURRENT_ARCH_PATH, BOUNDARY_PATH, EVOLUTION_PATH, STATE_PATH]:
        if digest not in path.read_text(encoding="utf-8"):
            raise ValueError(f"stale generated control document: {relative(path)}")
    graph = load_json(GRAPH_PATH)
    meta = graph.get("graph", {}).get("architecture_control_plane", {})
    if meta.get("registry_sha256") != digest:
        raise ValueError("graph control overlay is stale")
    control_ids = {node["id"] for node in graph["nodes"] if str(node.get("id", "")).startswith("control_")}
    expected_ids = {f"control_{node['id']}" for node in registry["nodes"]}
    if control_ids != expected_ids:
        raise ValueError("graph control nodes do not match registry")
    forbidden = {(edge["source"], edge["target"]) for edge in graph["links"] if edge.get("forbidden")}
    expected_forbidden = {(f"control_{a}", f"control_{b}") for a, b in REQUIRED_FORBIDDEN_EDGES}
    if not expected_forbidden.issubset(forbidden):
        raise ValueError("graph missing required forbidden edges")
    manifest = load_json(RUN_MANIFEST_PATH)
    if manifest.get("registry_sha256") != digest or manifest.get("search_started") or manifest.get("forward_performance_read"):
        raise ValueError("run manifest mismatch or prohibited activity recorded")
    state = load_json(STATE_SOURCE_PATH)
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
    if meta.get("phase_status") != state["current_phase"] or meta.get("accepted_subject_sha") != accepted_subject_sha:
        raise ValueError("graph phase acceptance metadata mismatch")
    evidence = attestation.get("test_evidence", {})
    if evidence != acceptance_test_evidence(state) or manifest.get("test_evidence") != evidence:
        raise ValueError("acceptance test evidence mismatch")
    if not ARTIFACT_INDEX_PATH.exists():
        raise ValueError("artifact index missing")


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
