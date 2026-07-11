from __future__ import annotations

import unittest

from scripts.crypto_architecture_control_plane import (
    BOUNDARY_PATH,
    B0P_ATTESTATION_PATH,
    B0A_MANIFEST_PATH,
    NEXTGEN_MATERIALIZATION_PATH,
    NEXTGEN_BOOKTICKER_PATH,
    NEXTGEN_RUN_MANIFEST_PATH,
    CANARY_PLAN_PATH,
    B1S_FROZEN_MANIFEST_PATH,
    B1S_RUN_MANIFEST_PATH,
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
B0A_ACCEPTED_SUBJECT_SHA = "4e09f33159fabe21add8e5d405f76a5a97c61f83"


class ArchitectureControlPlaneTests(unittest.TestCase):
    def test_registry_and_generated_outputs_are_synchronized(self) -> None:
        registry = load_json(REGISTRY_PATH)
        validate_registry(registry)
        validate_outputs(registry)

        state = load_json(STATE_SOURCE_PATH)
        self.assertEqual(state["current_phase"], "B1S_CANARY_PARTIALLY_COMPLETED_STOPPED")
        self.assertEqual(
            state["production_observation_qualification_status"],
            "PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED",
        )
        self.assertEqual(state["phase_b1_status"], "PHASE_B1_PERFORMANCE_INTEGRATION_FROZEN")
        self.assertEqual(state["phase_b0p_acceptance"]["status"], "PHASE_B0P_PARTIALLY_ACCEPTED")
        self.assertEqual(state["active_stage"], "B1S_CANARY_CLOSED_WAITING_FROZEN_SEARCH_EPOCH_AUTHORIZATION")
        self.assertEqual(state["frozen_signal_behaviour_status"], "FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED")
        self.assertEqual(state["phase_b0a_acceptance"]["accepted_subject_sha"], B0A_ACCEPTED_SUBJECT_SHA)
        self.assertEqual(state["formal_search_status"], "FORMAL_SEARCH_FROZEN")
        self.assertEqual(state["nextgen_dark_status"], "NEXTGEN_DARK_SCOPED_READY")
        self.assertEqual(state["canary_status"], "B1S_CANARY_PARTIALLY_COMPLETED")
        self.assertEqual(state["adaptive_cross_epoch_memory_status"], "ADAPTIVE_CROSS_EPOCH_MEMORY_FROZEN")
        self.assertEqual(state["candidate_promotion_status"], "NO_CANDIDATE_PROMOTION")

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
        self.assertEqual(manifest["b1s_canary_status"], "B1S_CANARY_PARTIALLY_COMPLETED")

        nodes = {node["id"]: node for node in registry["nodes"]}
        self.assertIn("contract implemented", nodes["feature_builder"]["blocker"])
        self.assertIn("primitive contract implemented", nodes["basis_oi_event_detection"]["blocker"])
        self.assertFalse(any(node["feedback_permission"].endswith("_B0") for node in registry["nodes"]))

        authority = BOUNDARY_PATH.read_text(encoding="utf-8")
        self.assertLess(authority.index("machine-readable architecture authority"), authority.index("deterministic graph view"))
        self.assertLess(authority.index("deterministic graph view"), authority.index("human-readable generated view"))

        current_architecture = CURRENT_ARCH_PATH.read_text(encoding="utf-8")
        self.assertIn("B1S_CANARY_PARTIALLY_COMPLETED_STOPPED", current_architecture)
        self.assertIn("PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED", current_architecture)

        graph = load_json(GRAPH_PATH)
        graph_control = graph["graph"]["architecture_control_plane"]
        self.assertEqual(graph_control["phase_status"], "B1S_CANARY_PARTIALLY_COMPLETED_STOPPED")
        self.assertEqual(graph_control["accepted_subject_sha"], ACCEPTED_SUBJECT_SHA)
        self.assertEqual(graph_control["b0p_accepted_subject_sha"], B0P_ACCEPTED_SUBJECT_SHA)
        self.assertEqual(graph_control["b0p_acceptance_status"], "PHASE_B0P_PARTIALLY_ACCEPTED")
        self.assertEqual(graph_control["frozen_signal_behaviour_status"], "FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED")
        self.assertEqual(graph_control["b0a_accepted_subject_sha"], B0A_ACCEPTED_SUBJECT_SHA)
        self.assertEqual(graph_control["nextgen_dark_status"], "NEXTGEN_DARK_SCOPED_READY")
        self.assertEqual(graph_control["b1s_canary_decision"], "B1S_CANARY_PARTIALLY_COMPLETED")
        self.assertEqual(graph_control["candidate_promotion_status"], "NO_CANDIDATE_PROMOTION")
        self.assertEqual(graph["built_at_accepted_subject"], B0A_ACCEPTED_SUBJECT_SHA)
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

        nextgen = load_json(NEXTGEN_RUN_MANIFEST_PATH)
        self.assertEqual(nextgen["decision"], "NEXTGEN_DARK_SCOPED_READY")
        self.assertEqual(nextgen["accepted_b0a_subject_sha"], B0A_ACCEPTED_SUBJECT_SHA)
        self.assertTrue(nextgen["materialization_reproducible"])
        self.assertEqual(nextgen["rows"], 245088)
        self.assertEqual(nextgen["symbols"], 12)
        self.assertEqual(set(nextgen["unavailable_states"]), {"liquidation_cluster"})
        self.assertEqual(nextgen["partially_available_states"], ["depth_liquidity_state"])
        self.assertEqual(nextgen["pc1_top_of_book_rows"], 14208)
        self.assertEqual(nextgen["pc1_top_of_book_depth_semantics"], "TOP_OF_BOOK_BBO_ONLY_NOT_MULTI_LEVEL_DEPTH")
        self.assertFalse(nextgen["search_started"])
        self.assertFalse(nextgen["performance_evaluated"])
        self.assertFalse(nextgen["canary_started"])
        self.assertRegex(nextgen["test_evidence"]["result"], r"^72 passed in ")

        materialization = load_json(NEXTGEN_MATERIALIZATION_PATH)
        self.assertFalse(materialization["forbidden_performance_columns_read"])
        self.assertFalse(materialization["forward_read"])
        bookticker = load_json(NEXTGEN_BOOKTICKER_PATH)
        self.assertTrue(bookticker["reproducible"])
        self.assertFalse(bookticker["liquidation_source_found_on_pc1"])
        canary = load_json(CANARY_PLAN_PATH)
        self.assertFalse(canary["execution_authorized"])
        self.assertFalse(canary["started"])

        frozen = load_json(B1S_FROZEN_MANIFEST_PATH)
        self.assertEqual(frozen["repo_sha"], "39dbd40e6ce7bde3fbaba0067da6a5bfbae797f8")
        self.assertEqual(frozen["frozen_manifest_sha256"], "897A36543AC4CB4E9F658DFA7CF0B71F869ACB3755F318F451AE039E63FDE1D2")
        b1s = load_json(B1S_RUN_MANIFEST_PATH)
        self.assertEqual(b1s["decision"], "B1S_CANARY_PARTIALLY_COMPLETED")
        self.assertEqual(b1s["proposal_rows"], 5120)
        self.assertEqual(b1s["stratified_admissions"], 564)
        self.assertEqual(b1s["stratified_strict_evaluations"], 315)
        self.assertEqual(b1s["global_top_k_strict_evaluations"], 320)
        self.assertEqual(b1s["adaptive_feedback_queries"], 64)
        self.assertFalse(b1s["main_and_bbo_directly_ranked"])
        self.assertFalse(b1s["candidate_promotion"])


if __name__ == "__main__":
    unittest.main()
