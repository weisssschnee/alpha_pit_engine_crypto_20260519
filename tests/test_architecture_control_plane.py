from __future__ import annotations

import unittest

from scripts.crypto_architecture_control_plane import (
    BOUNDARY_PATH,
    CURRENT_ARCH_PATH,
    GRAPH_PATH,
    REGISTRY_PATH,
    RUN_MANIFEST_PATH,
    STATE_SOURCE_PATH,
    load_json,
    validate_outputs,
    validate_registry,
)


ATTESTATION_PATH = REGISTRY_PATH.parents[1] / "runtime" / "a7b0_control_plane_20260711" / "phase_b0_acceptance_attestation.json"
ACCEPTED_SUBJECT_SHA = "9574d32053d1679d64179fe2d6607d1a05e13db9"


class ArchitectureControlPlaneTests(unittest.TestCase):
    def test_registry_and_generated_outputs_are_synchronized(self) -> None:
        registry = load_json(REGISTRY_PATH)
        validate_registry(registry)
        validate_outputs(registry)

        state = load_json(STATE_SOURCE_PATH)
        self.assertEqual(state["current_phase"], "PHASE_B0_CONTRACTS_ACCEPTED")
        self.assertEqual(
            state["production_observation_qualification_status"],
            "PHASE_B0_PRODUCTION_OBSERVATION_QUALIFICATION_PENDING",
        )
        self.assertEqual(state["phase_b1_status"], "PHASE_B1_FROZEN")

        attestation = load_json(ATTESTATION_PATH)
        self.assertEqual(attestation["accepted_subject_sha"], ACCEPTED_SUBJECT_SHA)
        self.assertEqual(attestation["test_evidence"]["subject_sha"], ACCEPTED_SUBJECT_SHA)
        self.assertEqual(attestation["test_evidence"]["result"], "39 passed in 22.15s")
        self.assertNotIn("acceptance_attestation_commit", attestation)

        manifest = load_json(RUN_MANIFEST_PATH)
        self.assertEqual(manifest["accepted_subject_sha"], ACCEPTED_SUBJECT_SHA)
        self.assertNotIn("last_verified_remote_sha", manifest)

        nodes = {node["id"]: node for node in registry["nodes"]}
        self.assertIn("contract implemented", nodes["feature_builder"]["blocker"])
        self.assertIn("primitive contract implemented", nodes["basis_oi_event_detection"]["blocker"])
        self.assertFalse(any(node["feedback_permission"].endswith("_B0") for node in registry["nodes"]))

        authority = BOUNDARY_PATH.read_text(encoding="utf-8")
        self.assertLess(authority.index("machine-readable architecture authority"), authority.index("deterministic graph view"))
        self.assertLess(authority.index("deterministic graph view"), authority.index("human-readable generated view"))

        current_architecture = CURRENT_ARCH_PATH.read_text(encoding="utf-8")
        self.assertIn("PHASE_B0_CONTRACTS_ACCEPTED", current_architecture)
        self.assertIn("PHASE_B0_PRODUCTION_OBSERVATION_QUALIFICATION_PENDING", current_architecture)

        graph = load_json(GRAPH_PATH)
        graph_control = graph["graph"]["architecture_control_plane"]
        self.assertEqual(graph_control["phase_status"], "PHASE_B0_CONTRACTS_ACCEPTED")
        self.assertEqual(graph_control["accepted_subject_sha"], ACCEPTED_SUBJECT_SHA)
        self.assertEqual(graph["built_at_accepted_subject"], ACCEPTED_SUBJECT_SHA)
        self.assertNotIn("built_at_commit", graph)


if __name__ == "__main__":
    unittest.main()
