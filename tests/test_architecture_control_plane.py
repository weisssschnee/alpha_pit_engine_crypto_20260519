from __future__ import annotations

import unittest

from scripts.crypto_architecture_control_plane import (
    BOUNDARY_PATH,
    B0P_ATTESTATION_PATH,
    B0A_MANIFEST_PATH,
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
B0P_MANIFEST_PATH = REGISTRY_PATH.parents[1] / "runtime" / "a7b0p_control_plane_20260711" / "b0p_qualification_manifest.json"
ACCEPTED_SUBJECT_SHA = "9574d32053d1679d64179fe2d6607d1a05e13db9"
B0P_ACCEPTED_SUBJECT_SHA = "5219e7899cad1be83f9bcf2ec520ed1ff5037f9e"


class ArchitectureControlPlaneTests(unittest.TestCase):
    def test_registry_and_generated_outputs_are_synchronized(self) -> None:
        registry = load_json(REGISTRY_PATH)
        validate_registry(registry)
        validate_outputs(registry)

        state = load_json(STATE_SOURCE_PATH)
        self.assertEqual(state["current_phase"], "PHASE_B0_CONTRACTS_ACCEPTED")
        self.assertEqual(
            state["production_observation_qualification_status"],
            "PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED",
        )
        self.assertEqual(state["phase_b1_status"], "PHASE_B1_FROZEN")
        self.assertEqual(state["phase_b0p_acceptance"]["status"], "PHASE_B0P_PARTIALLY_ACCEPTED")
        self.assertEqual(state["active_stage"], "PHASE_B0A_COMPLETE_STOPPED")
        self.assertEqual(state["frozen_signal_behaviour_status"], "FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED")

        attestation = load_json(ATTESTATION_PATH)
        self.assertEqual(attestation["accepted_subject_sha"], ACCEPTED_SUBJECT_SHA)
        self.assertEqual(
            attestation["production_observation_qualification_status"],
            "PHASE_B0_PRODUCTION_OBSERVATION_QUALIFICATION_PENDING",
        )
        self.assertEqual(attestation["test_evidence"]["subject_sha"], ACCEPTED_SUBJECT_SHA)
        self.assertEqual(attestation["test_evidence"]["result"], "39 passed in 22.15s")
        self.assertNotIn("acceptance_attestation_commit", attestation)

        b0p_attestation = load_json(B0P_ATTESTATION_PATH)
        self.assertEqual(b0p_attestation["accepted_subject_sha"], B0P_ACCEPTED_SUBJECT_SHA)
        self.assertEqual(b0p_attestation["attestation_status"], "PHASE_B0P_PARTIALLY_ACCEPTED")
        self.assertEqual(
            b0p_attestation["funding_status"],
            "PRODUCTION_FUNDING_OBSERVATION_QUALIFIED_WITHIN_BINANCE_UM_CORE12",
        )
        self.assertEqual(b0p_attestation["activation_status"], "ACTIVATION_IDENTITY_NOT_QUALIFIED")
        self.assertEqual(b0p_attestation["test_evidence"]["result"], "47 passed in 31.10s")
        self.assertNotIn("acceptance_attestation_commit", b0p_attestation)

        manifest = load_json(RUN_MANIFEST_PATH)
        self.assertEqual(manifest["accepted_subject_sha"], ACCEPTED_SUBJECT_SHA)
        self.assertNotIn("last_verified_remote_sha", manifest)
        self.assertEqual(manifest["b0p_accepted_subject_sha"], B0P_ACCEPTED_SUBJECT_SHA)
        self.assertEqual(manifest["b0p_acceptance_status"], "PHASE_B0P_PARTIALLY_ACCEPTED")

        nodes = {node["id"]: node for node in registry["nodes"]}
        self.assertIn("contract implemented", nodes["feature_builder"]["blocker"])
        self.assertIn("primitive contract implemented", nodes["basis_oi_event_detection"]["blocker"])
        self.assertFalse(any(node["feedback_permission"].endswith("_B0") for node in registry["nodes"]))

        authority = BOUNDARY_PATH.read_text(encoding="utf-8")
        self.assertLess(authority.index("machine-readable architecture authority"), authority.index("deterministic graph view"))
        self.assertLess(authority.index("deterministic graph view"), authority.index("human-readable generated view"))

        current_architecture = CURRENT_ARCH_PATH.read_text(encoding="utf-8")
        self.assertIn("PHASE_B0_CONTRACTS_ACCEPTED", current_architecture)
        self.assertIn("PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED", current_architecture)

        graph = load_json(GRAPH_PATH)
        graph_control = graph["graph"]["architecture_control_plane"]
        self.assertEqual(graph_control["phase_status"], "PHASE_B0_CONTRACTS_ACCEPTED")
        self.assertEqual(graph_control["accepted_subject_sha"], ACCEPTED_SUBJECT_SHA)
        self.assertEqual(graph_control["b0p_accepted_subject_sha"], B0P_ACCEPTED_SUBJECT_SHA)
        self.assertEqual(graph_control["b0p_acceptance_status"], "PHASE_B0P_PARTIALLY_ACCEPTED")
        self.assertEqual(graph_control["frozen_signal_behaviour_status"], "FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED")
        self.assertEqual(graph["built_at_accepted_subject"], ACCEPTED_SUBJECT_SHA)
        self.assertNotIn("built_at_commit", graph)

        b0p_manifest = load_json(B0P_MANIFEST_PATH)
        self.assertEqual(b0p_manifest["decision"], "PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED")
        self.assertEqual(b0p_manifest["funding_status"], "PRODUCTION_FUNDING_OBSERVATION_QUALIFIED")
        self.assertEqual(b0p_manifest["identity_status"], "LAYERED_IDENTITY_PARTIALLY_QUALIFIED")
        self.assertFalse(b0p_manifest["search_started"])
        self.assertFalse(b0p_manifest["forward_performance_read"])

        b0a_manifest = load_json(B0A_MANIFEST_PATH)
        self.assertEqual(b0a_manifest["decision"], "FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED")
        self.assertEqual(b0a_manifest["full_survivor_rows"], 33)
        self.assertEqual(b0a_manifest["full_survivor_exact_identities"], 18)
        self.assertEqual(b0a_manifest["accepted_alias_rows_materialized"], 16)
        self.assertEqual(b0a_manifest["canonical_exact_signals_materialized"], 6)
        self.assertEqual(b0a_manifest["activation_identities"], 5)
        self.assertEqual(b0a_manifest["behaviour_clusters"], 4)
        self.assertEqual(b0a_manifest["economic_hypotheses"], 5)
        self.assertTrue(b0a_manifest["reproducible"])
        self.assertTrue(b0a_manifest["alias_reconstruction_pass"])
        self.assertFalse(b0a_manifest["return_label_read"])
        self.assertFalse(b0a_manifest["reward_read"])


if __name__ == "__main__":
    unittest.main()
