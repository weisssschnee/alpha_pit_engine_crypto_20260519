"""Fail-closed authority resolution for real Search Engine experiments."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

from alphafactory_crypto.instrument_capability.mapping import (
    DEFAULT_MAPPING_CONTRACTS,
)
from alphafactory_crypto.instrument_canary.grammar import MECHANISM_MAPPING


REQUIRED_REAL_EXPERIMENT_ROLES = (
    "target",
    "optimizer_reward",
    "execution_price",
    "portfolio_mapping",
    "cost",
    "validation_role",
    "promotion_gate",
)
CONDITIONAL_RUN_NON_FORMAL_COMPONENTS = {
    "target": "real_policy_upgrade_canary",
    "optimizer_reward": "real_policy_upgrade_canary",
    "execution_price": "real_policy_upgrade_canary",
    "cost": "real_data_mapping_cost_evaluator",
    "validation_role": "real_policy_upgrade_canary",
}
V23_FROZEN_OOS_RECEIPT_PATH = (
    "config/crypto_search_v2_3_frozen_oos_receipt.json"
)
TEMPORAL_SUCCESSOR_AUTHORIZATION_PATH = (
    "config/crypto_temporal_program_30k_to_50k_successor_v1_authorization.json"
)
TEMPORAL_SUCCESSOR_SCOPE = (
    "ONE_30K_TO_50K_TRAIN_ONLY_TEMPORAL_PROGRAM_DEVELOPMENT_SUCCESSOR"
)
TEMPORAL_POLICY_VALIDATION_SCOPE = (
    "ONE_EQUAL_COUNT_TEMPORAL_POLICY_DEVELOPMENT_VALIDATION_NO_FEEDBACK"
)
TEMPORAL_POLICY_VALIDATION_AUTHORIZATION_PATH = (
    "config/crypto_temporal_policy_validation_v1_authorization.json"
)
DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH = (
    "config/crypto_search_economic_receipt_v1.json"
)
SEARCH_ECONOMIC_V2_RECEIPT_PATH = (
    "config/crypto_search_economic_receipt_v2.json"
)
SEARCH_ECONOMIC_V3_RECEIPT_PATH = (
    "config/crypto_search_economic_receipt_v3.json"
)
SEARCH_ECONOMIC_V4_RECEIPT_PATH = (
    "config/crypto_search_economic_receipt_v4.json"
)
SEARCH_ECONOMIC_V5_RECEIPT_PATH = (
    "config/crypto_search_economic_receipt_v5.json"
)
SEARCH_ECONOMIC_V6_RECEIPT_PATH = (
    "config/crypto_search_economic_receipt_v6.json"
)
SEARCH_MECHANISM_V2_RECEIPT_PATH = (
    "config/crypto_search_mechanism_v2_receipt.json"
)
SEARCH_MECHANISM_V21_RECEIPT_PATH = (
    "config/crypto_search_mechanism_v2_1_receipt.json"
)
SEARCH_MECHANISM_V22_RECEIPT_PATH = (
    "config/crypto_search_mechanism_v2_2_receipt.json"
)
SEARCH_MECHANISM_V23_RECEIPT_PATH = (
    "config/crypto_search_mechanism_v2_3_receipt.json"
)
SEARCH_EVIDENCE_V1_RECEIPT_PATH = (
    "config/crypto_search_run_evidence_v1_receipt.json"
)
SEARCH_EVIDENCE_V11_RECEIPT_PATH = (
    "config/crypto_search_run_evidence_v1_1_receipt.json"
)
BLOCK_ROBUST_GATE_RECEIPT_PATH = (
    "config/crypto_search_replication_aware_gate_v1_receipt.json"
)
BLOCK_ROBUST_GATE_REPLACEMENT_RECEIPT_PATH = (
    "config/crypto_search_replication_aware_gate_v1_replacement_receipt.json"
)
BLOCK_ROBUST_GATE_R2_RECEIPT_PATH = (
    "config/crypto_search_replication_aware_gate_v1_r2_receipt.json"
)
BLOCK_ROBUST_GATE_R3_RECEIPT_PATH = (
    "config/crypto_search_replication_aware_gate_v1_r3_receipt.json"
)
ECONOMIC_SEARCH_V6_EPOCH_ID = (
    "CRYPTO_SEARCH_ECONOMIC_V6_SEED_ROBUSTNESS_20260801"
)
ECONOMIC_SEARCH_V6_SEED_DERIVATION = (
    "SHA256_U32_BIG_ENDIAN(epoch_id|seed|ordinal_0_TO_3)"
)


def _derive_v6_seed_set(epoch_id: str) -> tuple[int, ...]:
    """Derive a pre-registered uint32 seed set without outcome inspection."""

    return tuple(
        int.from_bytes(
            hashlib.sha256(f"{epoch_id}|seed|{ordinal}".encode("utf-8")).digest()[
                :4
            ],
            "big",
        )
        for ordinal in range(4)
    )


ECONOMIC_SEARCH_V6_SEEDS = _derive_v6_seed_set(
    ECONOMIC_SEARCH_V6_EPOCH_ID
)
SEARCH_ECONOMIC_RECEIPT_SPECS: dict[str, dict[str, Any]] = {
    "CRYPTO_SEARCH_ECONOMIC_RECEIPT_V1": {
        "path": DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH,
        "decision_id": "USER_AUTHORIZED_CRYPTO_SEARCH_ECONOMIC_V1_20260731",
        "runner_campaign": "crypto_search_economic_v1",
        "runtime_date": "20260731",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_BUDGET_EXHAUSTED",
            "reason": "RAW_GENERATION_ATTEMPT_LIMIT",
            "runtime": "runtime/crypto_search_economic_v1_20260731",
            "producer_source_sha": (
                "17d5b5f19acd1366cf5b8f332249d78e918556f1"
            ),
            "generation_attempts": 95_776,
            "strict_evaluated_count": 1_190,
            "checkpoint": "checkpoint_budget_exhausted",
            "rescue_rerun_started": False,
        },
    },
    "CRYPTO_SEARCH_ECONOMIC_RECEIPT_V2": {
        "path": SEARCH_ECONOMIC_V2_RECEIPT_PATH,
        "decision_id": "USER_AUTHORIZED_CRYPTO_SEARCH_ECONOMIC_V2_20260731",
        "runner_campaign": "crypto_search_economic_v2",
        "runtime_date": "20260731",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_VALIDATION_BLOCKED",
            "reason": "CONTROL_BEHAVIOR_EQUALS_PRIMARY",
            "runtime": "runtime/crypto_search_economic_v2_20260731",
            "producer_source_sha": (
                "bcb77cecf2d75e650e73998b37af9ceed1b71072"
            ),
            "generation_attempts": 2_280,
            "strict_evaluated_count": 2_000,
            "checkpoint": "checkpoint_000",
            "rescue_rerun_started": False,
        },
    },
    "CRYPTO_SEARCH_ECONOMIC_RECEIPT_V3": {
        "path": SEARCH_ECONOMIC_V3_RECEIPT_PATH,
        "decision_id": "USER_AUTHORIZED_CRYPTO_SEARCH_ECONOMIC_V3_20260731",
        "runner_campaign": "crypto_search_economic_v3",
        "runtime_date": "20260731",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_VALIDATION_BLOCKED",
            "reason": "CONTROL_BEHAVIOR_EQUALS_PRIMARY",
            "runtime": "runtime/crypto_search_economic_v3_20260731",
            "producer_source_sha": (
                "ead338b4d34a95b707ae1a140b1aa318a71e4f6a"
            ),
            "generation_attempts": 2_280,
            "strict_evaluated_count": 2_000,
            "checkpoint": "checkpoint_validation_blocked",
            "rescue_rerun_started": False,
        },
    },
    "CRYPTO_SEARCH_ECONOMIC_RECEIPT_V4": {
        "path": SEARCH_ECONOMIC_V4_RECEIPT_PATH,
        "decision_id": "USER_AUTHORIZED_CRYPTO_SEARCH_ECONOMIC_V4_20260731",
        "runner_campaign": "crypto_search_economic_v4",
        "runtime_date": "20260731",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_VALIDATION_BLOCKED",
            "reason": "CONTROL_BEHAVIOR_EQUALS_PRIMARY",
            "runtime": "runtime/crypto_search_economic_v4_20260731",
            "producer_source_sha": (
                "94c79d0a8e559b7223fa1eaddb2d07ca76c1e628"
            ),
            "generation_attempts": 2_298,
            "strict_evaluated_count": 2_000,
            "checkpoint": "checkpoint_validation_blocked",
            "rescue_rerun_started": False,
        },
    },
    "CRYPTO_SEARCH_ECONOMIC_RECEIPT_V5": {
        "path": SEARCH_ECONOMIC_V5_RECEIPT_PATH,
        "decision_id": "USER_AUTHORIZED_CRYPTO_SEARCH_ECONOMIC_V5_20260731",
        "runner_campaign": "crypto_search_economic_v5",
        "runtime_date": "20260731",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_VALIDATION_BLOCKED",
            "reason": "VALIDATION_CONTROL_ARM_FAILED_KILL_LINE",
            "runtime": "runtime/crypto_search_economic_v5_20260731",
            "producer_source_sha": (
                "a6946df8b9b24db8572e48a5f8b79ef621feb0f9"
            ),
            "generation_attempts": 2_298,
            "strict_evaluated_count": 2_000,
            "checkpoint": "checkpoint_validation",
            "rescue_rerun_started": False,
        },
    },
    "CRYPTO_SEARCH_ECONOMIC_RECEIPT_V6": {
        "path": SEARCH_ECONOMIC_V6_RECEIPT_PATH,
        "decision_id": (
            "USER_AUTHORIZED_CRYPTO_SEARCH_ECONOMIC_V6_SEED_ROBUSTNESS_20260801"
        ),
        "runner_campaign": "crypto_search_economic_v6",
        "runtime_date": "20260801",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_VALIDATION_BLOCKED",
            "reason": "VALIDATION_CONTROL_ARM_FAILED_KILL_LINE",
            "runtime": "runtime/crypto_search_economic_v6_20260801",
            "producer_source_sha": (
                "07a699f11510b943991425c4a86eb7582aa59583"
            ),
            "generation_attempts": 2_263,
            "strict_evaluated_count": 2_000,
            "checkpoint": "checkpoint_validation",
            "rescue_rerun_started": False,
        },
        "run_authorization_extras": {
            "new_campaign_seed_set_authorized": True,
            "seed_set_pre_registered": True,
            "additional_seed_campaign_allowed": False,
        },
        "search_override_keys": {
            "runner_campaign",
            "runtime_date",
            "seed_set",
            "seed_derivation",
        },
        "seed_set": ECONOMIC_SEARCH_V6_SEEDS,
        "seed_derivation": ECONOMIC_SEARCH_V6_SEED_DERIVATION,
    },
    "CRYPTO_SEARCH_MECHANISM_V2_RECEIPT": {
        "path": SEARCH_MECHANISM_V2_RECEIPT_PATH,
        "decision_id": (
            "USER_AUTHORIZED_EXTENSIBLE_TYPED_MECHANISM_GRAMMAR_12K_20260801"
        ),
        "runner_campaign": "crypto_search_mechanism_v2",
        "runtime_date": "20260801",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_VALIDATION_BLOCKED",
            "reason": "VALIDATION_CONTROL_PATH_SCHEMA_INCONSISTENT",
            "runtime": "runtime/crypto_search_mechanism_v2_20260801",
            "producer_source_sha": (
                "ef688d89ca0e89654015bf5f76a6b9c26494d837"
            ),
            "generation_attempts": 20_386,
            "strict_evaluated_count": 12_000,
            "checkpoint": "checkpoint_005",
            "rescue_rerun_started": False,
        },
        "run_authorization_scope": (
            "ONE_FRESH_STATE_12000_STRICT_MECHANISM_CAMPAIGN"
        ),
        "run_authorization_extras": {
            "mechanism_catalog_persistence_authorized": True,
            "candidate_or_policy_state_persistence_authorized": False,
            "additional_seed_campaign_allowed": False,
        },
        "mechanism_registry_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "compile_mechanism_catalog"
        ),
        "mapping_adapter_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "mapping_id_for_mechanism_spec"
        ),
        "economic_hypothesis_field": "hypothesis",
        "mapping_classes": {
            "CROSS_SECTIONAL_RELATIVE",
            "DIRECTIONAL_STATEFUL",
            "SPARSE_EVENT_CARRY",
        },
        "strict_evaluated_target": 12_000,
        "checkpoint_size": 2_000,
        "checkpoint_count": 6,
        "validation_trigger": 5,
        "validation_continuation_action": (
            "NO_ADDITIONAL_BUDGET_FINAL_PER_ARM_QUALIFICATION"
        ),
        "random_control_survival_required": False,
        "seed_set": (
            3119619210,
            1353677240,
            2161345710,
            2150829259,
        ),
        "seed_derivation": (
            "SHA256_U32_BIG_ENDIAN(epoch_id|seed|ordinal_0_TO_3)"
        ),
        "required_component_sources": {
            "mechanism",
            "mechanism_mapping",
            "direction",
            "validation_kill_line",
            "portfolio_mapping_and_cost",
            "target_execution",
            "optimizer_reward_and_matched_attribution",
            "target_contract",
            "runtime_binding",
            "mechanism_catalog",
            "campaign_contract",
        },
    },
    "CRYPTO_SEARCH_MECHANISM_V2_1_RECEIPT": {
        "path": SEARCH_MECHANISM_V21_RECEIPT_PATH,
        "decision_id": (
            "USER_AUTHORIZED_EVOLUTION_GUIDED_MECHANISM_BASIS_10K_20260801"
        ),
        "runner_campaign": "crypto_search_mechanism_v2_1",
        "runtime_date": "20260801",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        },
        "expected_run_outcome": {
            "status": "PASS_SEARCH_ENGINE_V2_1_TRAIN_GATE_NEGATIVE",
            "reason": "TRAIN_GATE_NEGATIVE",
            "runtime": "runtime/crypto_search_mechanism_v2_1_20260801",
            "producer_source_sha": (
                "94b016fa7847d5c5b06db1e6144bda7062064151"
            ),
            "generation_attempts": 14_237,
            "strict_evaluated_count": 10_000,
            "checkpoint": "checkpoint_004",
            "rescue_rerun_started": False,
        },
        "run_authorization_scope": (
            "ONE_FRESH_STATE_10000_STRICT_MECHANISM_BASIS_CAMPAIGN"
        ),
        "run_authorization_extras": {
            "mechanism_catalog_persistence_authorized": True,
            "aggregate_mechanism_knowledge_authorized": True,
            "candidate_or_policy_state_persistence_authorized": False,
            "additional_seed_campaign_allowed": False,
        },
        "mechanism_registry_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "compile_mechanism_catalog"
        ),
        "mapping_adapter_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "mapping_id_for_mechanism_spec"
        ),
        "economic_hypothesis_field": "hypothesis",
        "mapping_classes": {
            "CROSS_SECTIONAL_RELATIVE",
            "DIRECTIONAL_STATEFUL",
            "SPARSE_EVENT_CARRY",
        },
        "strict_evaluated_target": 10_000,
        "checkpoint_size": 2_000,
        "checkpoint_count": 5,
        "validation_trigger": 4,
        "validation_continuation_action": (
            "NO_ADDITIONAL_BUDGET_FINAL_PER_ARM_QUALIFICATION"
        ),
        "random_control_survival_required": False,
        "seed_set": (
            1690649940,
            1761225687,
            4212849294,
            1880069717,
        ),
        "seed_derivation": (
            "SHA256_U32_BIG_ENDIAN(epoch_id|seed|ordinal_0_TO_3)"
        ),
        "required_component_sources": {
            "mechanism",
            "mechanism_mapping",
            "direction",
            "validation_kill_line",
            "portfolio_mapping_and_cost",
            "target_execution",
            "optimizer_reward_and_matched_attribution",
            "target_contract",
            "runtime_binding",
            "legacy_mechanism_catalog",
            "expanded_mechanism_catalog",
            "aggregate_mechanism_knowledge",
            "campaign_contract",
        },
    },
    "CRYPTO_SEARCH_MECHANISM_V2_2_RECEIPT": {
        "path": SEARCH_MECHANISM_V22_RECEIPT_PATH,
        "decision_id": (
            "USER_AUTHORIZED_FRESH_STATE_EVOLUTION_QUALIFICATION_20K_20260802"
        ),
        "runner_campaign": "crypto_search_mechanism_v2_2",
        "runtime_date": "20260802",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        },
        "expected_run_outcome": {
            "status": "PASS_SEARCH_ENGINE_V2_2_VALIDATION_GATE_NEGATIVE",
            "reason": "VALIDATION_GATE_NEGATIVE",
            "runtime": "runtime/crypto_search_mechanism_v2_2_20260802",
            "producer_source_sha": (
                "e84b35c76a4cfc139f1c351286489b83fce61250"
            ),
            "generation_attempts": 12_240,
            "strict_evaluated_count": 8_000,
            "checkpoint": "checkpoint_validation",
            "rescue_rerun_started": False,
        },
        "run_authorization_scope": (
            "ONE_FRESH_STATE_UP_TO_20000_STRICT_EVOLUTION_QUALIFICATION_CAMPAIGN"
        ),
        "run_authorization_extras": {
            "mechanism_catalog_persistence_authorized": True,
            "aggregate_mechanism_knowledge_authorized": True,
            "candidate_or_policy_state_persistence_authorized": False,
            "additional_seed_campaign_allowed": False,
        },
        "mechanism_registry_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "compile_mechanism_catalog"
        ),
        "mapping_adapter_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "mapping_id_for_mechanism_spec"
        ),
        "economic_hypothesis_field": "hypothesis",
        "mapping_classes": {
            "CROSS_SECTIONAL_RELATIVE",
            "DIRECTIONAL_STATEFUL",
            "SPARSE_EVENT_CARRY",
        },
        "strict_evaluated_target": 20_000,
        "checkpoint_size": 2_000,
        "checkpoint_count": 10,
        "validation_trigger": 3,
        "validation_continuation_action": (
            "CONTINUE_SAME_FRESH_STATE_TO_20000_IF_BOTH_ARMS_PASS"
        ),
        "random_control_survival_required": True,
        "control_arm_id": "expanded_mechanism_random_v2_2",
        "seed_set": (
            1805313393,
            1209455071,
            1221486859,
            2049360136,
        ),
        "seed_derivation": (
            "SHA256_U32_BIG_ENDIAN(epoch_id|seed|ordinal_0_TO_3)"
        ),
        "required_component_sources": {
            "mechanism",
            "mechanism_mapping",
            "direction",
            "validation_kill_line",
            "portfolio_mapping_and_cost",
            "target_execution",
            "optimizer_reward_and_matched_attribution",
            "target_contract",
            "runtime_binding",
            "expanded_mechanism_catalog",
            "aggregate_mechanism_knowledge",
            "campaign_contract",
        },
    },
    "CRYPTO_SEARCH_MECHANISM_V2_3_RECEIPT": {
        "path": SEARCH_MECHANISM_V23_RECEIPT_PATH,
        "decision_id": "USER_AUTHORIZED_EVOLUTION_POLICY_ATTRIBUTION_V2_3_20260802",
        "runner_campaign": "crypto_search_mechanism_v2_3",
        "runtime_date": "20260802",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        },
        "expected_run_outcome": {
            "status": "PASS_SEARCH_ENGINE_V2_3_POLICY_ATTRIBUTION_GATE_NEGATIVE",
            "reason": "FULL_POLICY_ATTRIBUTION_GATE_NEGATIVE",
            "runtime": "runtime/crypto_search_mechanism_v2_3_20260802",
            "producer_source_sha": (
                "06512e01876345d9921d56405d8254a82933a9b7"
            ),
            "generation_attempts": 23_869,
            "strict_evaluated_count": 16_000,
            "validation_candidate_cohort_evaluated_count": 1_024,
            "checkpoint": "checkpoint_validation",
            "proposal_distribution_qualified": False,
            "train_ranker_qualified": False,
            "full_evolution_policy_pass": False,
            "continuation_authorized": False,
            "artifact_bundle_sha256": (
                "A593CAB511326F30ABC426329E71F1451AD73250E5D4FEF4552CFD8F46AEDAF5"
            ),
            "rescue_rerun_started": False,
        },
        "run_authorization_scope": (
            "ONE_FRESH_STATE_16000_STRICT_POLICY_ATTRIBUTION_PLUS_CONDITIONAL_"
            "4000_EVOLUTION_CONTINUATION"
        ),
        "run_authorization_extras": {
            "mechanism_catalog_persistence_authorized": True,
            "aggregate_mechanism_knowledge_authorized": True,
            "candidate_or_policy_state_persistence_authorized": False,
            "additional_seed_campaign_allowed": False,
            "random_profitability_survival_required": False,
        },
        "mechanism_registry_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "compile_mechanism_catalog"
        ),
        "mapping_adapter_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "mapping_id_for_mechanism_spec"
        ),
        "economic_hypothesis_field": "hypothesis",
        "mapping_classes": {
            "CROSS_SECTIONAL_RELATIVE",
            "DIRECTIONAL_STATEFUL",
            "SPARSE_EVENT_CARRY",
        },
        "strict_evaluated_target": 20_000,
        "checkpoint_size": 2_000,
        "checkpoint_count": 10,
        "validation_trigger": 7,
        "validation_minimum_evaluated_per_active_arm": 512,
        "validation_evaluated_per_active_arm": 512,
        "validation_candidate_selection": (
            "FOUR_DISJOINT_TWO_SEED_TRAIN_TOP_AND_ORDINAL_STRATIFIED_COHORTS"
        ),
        "validation_arm_aggregation": (
            "SEED_HORIZON_COHORT_EQUAL_WEIGHT_WITH_PAIRED_DAILY_BLOCK_EFFECTS"
        ),
        "validation_failure_action": "STOP_AT_16000_WITH_COMPLETED_RESULTS",
        "validation_failed_arm_allocation": "NO_CONTINUATION_ALLOCATION",
        "validation_continuation_action": (
            "CONTINUE_SAME_FRESH_EVOLUTION_STATE_FOR_4000_STRICT"
        ),
        "validation_runtime_symbol": (
            "alphafactory_crypto.broad_search.search_engine_v1."
            "run_v23_policy_attribution_validation"
        ),
        "random_control_survival_required": False,
        "control_arm_id": "expanded_mechanism_random_v2_3",
        "seed_set": (359914106, 1141399971),
        "seed_derivation": (
            "SHA256_U32_BIG_ENDIAN(epoch_id|seed|ordinal_0_TO_1)"
        ),
        "required_component_sources": {
            "mechanism",
            "mechanism_mapping",
            "direction",
            "validation_kill_line",
            "portfolio_mapping_and_cost",
            "target_execution",
            "optimizer_reward_and_matched_attribution",
            "target_contract",
            "runtime_binding",
            "expanded_mechanism_catalog",
            "aggregate_mechanism_knowledge",
            "campaign_contract",
        },
    },
    "CRYPTO_SEARCH_RUN_EVIDENCE_V1_RECEIPT": {
        "path": SEARCH_EVIDENCE_V1_RECEIPT_PATH,
        "decision_id": "USER_AUTHORIZED_SEARCH_RUN_EVIDENCE_V1_20260804",
        "runner_campaign": "crypto_search_run_evidence_v1",
        "runtime_date": "20260804",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_VERIFICATION_FAILED",
            "reason": "LEDGER_EVIDENCE_COLUMNS_MISSING",
            "runtime": "runtime/crypto_search_run_evidence_v1_20260804",
            "producer_source_sha": (
                "fea74611c491d2d9a77d8013bc6cdaf427b4fd8c"
            ),
            "generation_attempts": 12_034,
            "strict_evaluated_count": 8_000,
            "checkpoint": "checkpoint_003",
            "artifact_bundle_sha256": (
                "04FB3B25295F44C741333431904A0FDED064CCA1D122A9EEEEE40D1C3C76B2CF"
            ),
            "checker_result": "FAIL",
            "sealed_reads": 0,
            "rescue_rerun_started": False,
        },
        "run_authorization_scope": (
            "ONE_FRESH_STATE_8000_STRICT_DEVELOPMENT_EVIDENCE_RUN"
        ),
        "run_authorization_extras": {
            "passive_evidence_only": True,
            "search_policy_change_allowed": False,
            "reward_change_allowed": False,
            "mapping_change_allowed": False,
            "validation_allowed": False,
            "oos_allowed": False,
        },
        "mechanism_registry_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "compile_mechanism_catalog"
        ),
        "mapping_adapter_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "mapping_id_for_mechanism_spec"
        ),
        "economic_hypothesis_field": "hypothesis",
        "mapping_classes": {
            "CROSS_SECTIONAL_RELATIVE",
            "DIRECTIONAL_STATEFUL",
            "SPARSE_EVENT_CARRY",
        },
        "strict_evaluated_target": 8_000,
        "checkpoint_size": 2_000,
        "checkpoint_count": 4,
        "validation_trigger": 999,
        "validation_minimum_evaluated_per_active_arm": 0,
        "validation_evaluated_per_active_arm": 0,
        "validation_candidate_selection": "NOT_AUTHORIZED",
        "validation_arm_aggregation": "NOT_AUTHORIZED",
        "validation_failure_action": "NOT_AUTHORIZED",
        "validation_failed_arm_allocation": "NOT_AUTHORIZED",
        "validation_continuation_action": "NOT_AUTHORIZED",
        "validation_runtime_symbol": (
            "alphafactory_crypto.broad_search.search_engine_v1.run_engine"
        ),
        "random_control_survival_required": False,
        "control_arm_id": "expanded_mechanism_random_v2_3",
        "seed_set": (2109280669, 1412948873),
        "seed_derivation": (
            "SHA256_U32_BIG_ENDIAN(epoch_id|seed|ordinal_0_TO_1)"
        ),
        "required_component_sources": {
            "mechanism",
            "mechanism_mapping",
            "direction",
            "validation_kill_line",
            "portfolio_mapping_and_cost",
            "target_execution",
            "optimizer_reward_and_matched_attribution",
            "target_contract",
            "runtime_binding",
            "behavior_provenance_consumer",
            "expanded_mechanism_catalog",
            "aggregate_mechanism_knowledge",
            "campaign_contract",
        },
    },
    "CRYPTO_SEARCH_RUN_EVIDENCE_V1_1_RECEIPT": {
        "path": SEARCH_EVIDENCE_V11_RECEIPT_PATH,
        "decision_id": "USER_AUTHORIZED_SEARCH_RUN_EVIDENCE_V1_1_20260805",
        "runner_campaign": "crypto_search_run_evidence_v1_1",
        "runtime_date": "20260805",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_COMPLETE",
            "reason": "FRESH_DEVELOPMENT_SEARCH_AND_PASSIVE_EVIDENCE_JOIN_COMPLETE",
            "runtime": "runtime/crypto_search_run_evidence_v1_1_20260805",
            "producer_source_sha": "67701ba73ac16c3da6cbdf6d98431d6d1df998e1",
            "generation_attempts": 3_201,
            "strict_evaluated_count": 2_000,
            "joined_strict_provenance_count": 2_000,
            "behavior_attributed_proposal_count": 2_320,
            "control_degenerate_count": 320,
            "checkpoint": "checkpoint_000",
            "checkpoint_restore_verified": True,
            "artifact_bundle_sha256": (
                "DE21BD375C420DCA93C7FAE8FFB4E461"
                "E519041611E34314E32C43AAC791241C"
            ),
            "authoritative_archive_sha256": (
                "B21B2B96C156EFF8CCAC4679642799F8"
                "EBEE62014B9A7F2F1761128793D604FB"
            ),
            "checker_result": "PASS",
            "engineering_integrity": "PASS",
            "earliest_supported_failure_layer": (
                "GROSS_TO_NET_COST_THEN_DUAL_AXIS_NET_LCB_STABILITY"
            ),
            "primary_gross_positive": 1_725,
            "primary_net_positive": 695,
            "left_increment_gross_positive": 1_286,
            "left_increment_net_positive": 452,
            "both_axis_gross_positive": 754,
            "both_axis_net_positive": 156,
            "both_axis_net_lcb_positive": 0,
            "positive_search_reward_count": 68,
            "matched_positive_count": 0,
            "process_exit_code": 1,
            "process_exit_attribution": (
                "CLI_SUCCESS_STATUS_MAPPING_OMITTED_EVIDENCE_V1_1_PASS"
            ),
            "sealed_reads": 0,
            "rescue_rerun_started": False,
        },
        "run_authorization_scope": (
            "ONE_FRESH_STATE_2000_STRICT_DEVELOPMENT_EVIDENCE_CHECKPOINT"
        ),
        "run_authorization_extras": {
            "passive_evidence_only": True,
            "search_policy_change_allowed": False,
            "reward_change_allowed": False,
            "mapping_change_allowed": False,
            "validation_allowed": False,
            "oos_allowed": False,
        },
        "mechanism_registry_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "compile_mechanism_catalog"
        ),
        "mapping_adapter_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "mapping_id_for_mechanism_spec"
        ),
        "economic_hypothesis_field": "hypothesis",
        "mapping_classes": {
            "CROSS_SECTIONAL_RELATIVE",
            "DIRECTIONAL_STATEFUL",
            "SPARSE_EVENT_CARRY",
        },
        "strict_evaluated_target": 2_000,
        "checkpoint_size": 2_000,
        "checkpoint_count": 1,
        "validation_trigger": 999,
        "validation_minimum_evaluated_per_active_arm": 0,
        "validation_evaluated_per_active_arm": 0,
        "validation_candidate_selection": "NOT_AUTHORIZED",
        "validation_arm_aggregation": "NOT_AUTHORIZED",
        "validation_failure_action": "NOT_AUTHORIZED",
        "validation_failed_arm_allocation": "NOT_AUTHORIZED",
        "validation_continuation_action": "NOT_AUTHORIZED",
        "validation_runtime_symbol": (
            "alphafactory_crypto.broad_search.search_engine_v1.run_engine"
        ),
        "random_control_survival_required": False,
        "control_arm_id": "expanded_mechanism_random_v2_3",
        "seed_set": (125908376, 3137011914),
        "seed_derivation": (
            "SHA256_U32_BIG_ENDIAN(epoch_id|seed|ordinal_0_TO_1)"
        ),
        "required_component_sources": {
            "mechanism",
            "mechanism_mapping",
            "direction",
            "validation_kill_line",
            "portfolio_mapping_and_cost",
            "target_execution",
            "optimizer_reward_and_matched_attribution",
            "target_contract",
            "runtime_binding",
            "behavior_provenance_consumer",
            "expanded_mechanism_catalog",
            "aggregate_mechanism_knowledge",
            "campaign_contract",
        },
    },
    "CRYPTO_REPLICATION_AWARE_SEARCH_GATE_V1_RECEIPT": {
        "path": BLOCK_ROBUST_GATE_RECEIPT_PATH,
        "decision_id": "USER_AUTHORIZED_REPLICATION_AWARE_SEARCH_GATE_V1_20260806",
        "runner_campaign": "crypto_search_replication_aware_gate_v1",
        "runtime_date": "20260806",
        "allowed_statuses": {
            "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
            "RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED",
        },
        "expected_run_outcome": {
            "status": "ENGINE_VERIFICATION_FAILED",
            "reason": "PRODUCER_PARENT_EXITED_BEFORE_FIRST_ATTEMPT",
            "runtime": (
                "runtime/crypto_search_replication_aware_gate_v1_20260806"
            ),
            "producer_source_sha": (
                "ee36ea46a617b8786661b402992ef3fb0fbaaf5a"
            ),
            "generation_attempts": 0,
            "strict_evaluated_count": 0,
            "checkpoint": None,
            "artifact_bundle_sha256": (
                "D0E544EB1396CA5C43E77ED82B4277FA"
                "EF05164650846CB7735CB3D4F65EBCFD"
            ),
            "checker_result": "FAIL",
            "checker_exit_code": 1,
            "checker_missing_artifact_count": 13,
            "effective_task_id": "job_20260806_044440_a5b83e",
            "sealed_reads": 0,
            "rescue_rerun_started": False,
        },
        "run_authorization_scope": (
            "ONE_FRESH_STATE_1536_STRICT_DEVELOPMENT_BLOCK_ROBUST_GATE"
        ),
        "run_authorization_extras": {
            "passive_evidence_only": False,
            "search_selection_authority_change_allowed": True,
            "reward_formula_change_allowed": False,
            "mapping_change_allowed": False,
            "validation_allowed": False,
            "oos_allowed": False,
        },
        "mechanism_registry_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "compile_mechanism_catalog"
        ),
        "mapping_adapter_symbol": (
            "alphafactory_crypto.broad_search.compositional18m."
            "mapping_id_for_mechanism_spec"
        ),
        "economic_hypothesis_field": "hypothesis",
        "mapping_classes": {
            "CROSS_SECTIONAL_RELATIVE",
            "DIRECTIONAL_STATEFUL",
            "SPARSE_EVENT_CARRY",
        },
        "strict_evaluated_target": 1_536,
        "checkpoint_size": 512,
        "checkpoint_count": 3,
        "validation_trigger": 999,
        "validation_minimum_evaluated_per_active_arm": 0,
        "validation_evaluated_per_active_arm": 0,
        "validation_candidate_selection": "NOT_AUTHORIZED",
        "validation_arm_aggregation": "NOT_AUTHORIZED",
        "validation_evaluation_order": "NOT_AUTHORIZED",
        "validation_required_horizons_hours": [4],
        "validation_evaluated_per_arm_per_horizon": 0,
        "validation_failure_action": "NOT_AUTHORIZED",
        "validation_failed_arm_allocation": "NOT_AUTHORIZED",
        "validation_continuation_action": "NOT_AUTHORIZED",
        "validation_checkpoint_action": "NOT_AUTHORIZED",
        "validation_runtime_symbol": (
            "alphafactory_crypto.broad_search.search_engine_v1.run_engine"
        ),
        "random_control_survival_required": False,
        "control_arm_id": "block_robust_typed_random_v1",
        "seed_set": (1544162162, 58589310),
        "seed_derivation": (
            "SHA256_U32_BIG_ENDIAN(epoch_id|seed|ordinal_0_TO_1)"
        ),
        "required_component_sources": {
            "mechanism",
            "mechanism_mapping",
            "direction",
            "validation_kill_line",
            "portfolio_mapping_and_cost",
            "target_execution",
            "optimizer_reward_and_matched_attribution",
            "target_contract",
            "runtime_binding",
            "behavior_provenance_consumer",
            "expanded_mechanism_catalog",
            "aggregate_mechanism_knowledge",
            "campaign_contract",
        },
    },
}

# The original receipt and invalid-run outcome remain independently resolvable.
# The replacement receipt changes only one-run authority and runtime identity;
# every economic/search contract field is inherited unchanged.
SEARCH_ECONOMIC_RECEIPT_SPECS[
    "CRYPTO_REPLICATION_AWARE_SEARCH_GATE_V1_REPLACEMENT_RECEIPT"
] = {
    **SEARCH_ECONOMIC_RECEIPT_SPECS[
        "CRYPTO_REPLICATION_AWARE_SEARCH_GATE_V1_RECEIPT"
    ],
    "path": BLOCK_ROBUST_GATE_REPLACEMENT_RECEIPT_PATH,
    "decision_id": (
        "USER_AUTHORIZED_REPLICATION_AWARE_SEARCH_GATE_V1_REPLACEMENT_20260806"
    ),
    "runtime_date": "20260806r1",
    "expected_run_outcome": {
        "status": "ENGINE_VERIFICATION_FAILED",
        "reason": "NATIVE_STDERR_TERMINATED_BEFORE_WORKER_SUBMIT",
        "runtime": (
            "runtime/crypto_search_replication_aware_gate_v1_20260806r1"
        ),
        "producer_source_sha": (
            "a0c60ec55c4e71da08f575dfcbf2ec76cecd7596"
        ),
        "generation_attempts": 8,
        "submitted_count": 0,
        "returned_count": 0,
        "strict_evaluated_count": 0,
        "market_evaluations": 0,
        "checkpoint": None,
        "artifact_bundle_sha256": (
            "C8B3ADD62EEBC1C01A9A7E0D20057148"
            "5BED83FF582B57AD798CE2E5568720EC"
        ),
        "checker_result": "FAIL",
        "checker_exit_code": 1,
        "checker_missing_artifact_count": 13,
        "effective_task_id": "job_20260806_125929_7681d5",
        "launcher_failure": (
            "WINDOWS_POWERSHELL_NATIVE_COMMAND_ERROR_FROM_NUMPY_RUNTIME_WARNING"
        ),
        "orphan_worker_terminated": True,
        "sealed_reads": 0,
        "rescue_rerun_started": False,
    },
}

# The two failed launches remain immutable historical evidence.  R2 is a new,
# single-use authority with the same economic/search contract and a new runtime
# identity; it does not convert either failed launch into a resumable run.
SEARCH_ECONOMIC_RECEIPT_SPECS[
    "CRYPTO_REPLICATION_AWARE_SEARCH_GATE_V1_R2_RECEIPT"
] = {
    **SEARCH_ECONOMIC_RECEIPT_SPECS[
        "CRYPTO_REPLICATION_AWARE_SEARCH_GATE_V1_RECEIPT"
    ],
    "path": BLOCK_ROBUST_GATE_R2_RECEIPT_PATH,
    "decision_id": (
        "USER_AUTHORIZED_REPLICATION_AWARE_SEARCH_GATE_V1_R2_20260806"
    ),
    "runtime_date": "20260806r2",
    "expected_run_outcome": {
        "status": "ENGINE_VERIFICATION_FAILED",
        "reason": "ARGPARSE_ARGUMENT_LIST_FLATTENED_BEFORE_ENGINE_ENTRY",
        "runtime": (
            "runtime/crypto_search_replication_aware_gate_v1_20260806r2"
        ),
        "producer_source_sha": (
            "c8ddfed84ed06101cd69b3ae5d6b63451e5be698"
        ),
        "generation_attempts": 0,
        "submitted_count": 0,
        "returned_count": 0,
        "strict_evaluated_count": 0,
        "market_evaluations": 0,
        "checkpoint": None,
        "artifact_bundle_sha256": (
            "78862541488DEC0A3D7F12FAE1FC5376"
            "108CD8CD9A883F346851277B714728D3"
        ),
        "checker_result": "FAIL",
        "checker_exit_code": 1,
        "checker_missing_artifact_count": 15,
        "effective_task_id": "job_20260806_140152_2eabe8",
        "launcher_failure": (
            "START_PROCESS_ARGUMENT_LIST_FLATTENED_MULTIWORD_VALUES"
        ),
        "native_exit_code": 2,
        "runtime_created": False,
        "sealed_reads": 0,
        "rescue_rerun_started": False,
    },
}

# R3 is a new single-use authority created only after the R2 launcher defect was
# closed.  It preserves every frozen economic/search field and changes only the
# receipt plus runtime identity; no failed campaign state is resumable.
SEARCH_ECONOMIC_RECEIPT_SPECS[
    "CRYPTO_REPLICATION_AWARE_SEARCH_GATE_V1_R3_RECEIPT"
] = {
    **SEARCH_ECONOMIC_RECEIPT_SPECS[
        "CRYPTO_REPLICATION_AWARE_SEARCH_GATE_V1_RECEIPT"
    ],
    "path": BLOCK_ROBUST_GATE_R3_RECEIPT_PATH,
    "decision_id": (
        "USER_AUTHORIZED_REPLICATION_AWARE_SEARCH_GATE_V1_R3_20260806"
    ),
    "runtime_date": "20260806r3",
    "expected_run_outcome": {
        "status": "ENGINE_COMPLETE",
        "reason": (
            "FRESH_DEVELOPMENT_BLOCK_ROBUST_POLICY_COMPARISON_COMPLETE"
        ),
        "runtime": (
            "runtime/crypto_search_replication_aware_gate_v1_20260806r3"
        ),
        "producer_source_sha": (
            "fd6220d56e0632b5084c2ed7574992c8bc2803fb"
        ),
        "generation_attempts": 2_077,
        "strict_evaluated_count": 1_536,
        "joined_strict_provenance_count": 1_536,
        "behavior_attributed_proposal_count": 1_605,
        "control_degenerate_count": 69,
        "checkpoint": "checkpoint_002",
        "checkpoint_restore_verified": True,
        "artifact_bundle_sha256": (
            "708C48BB96624AD4902704C4FA17277D3"
            "336FAD57B9AC2919E1ECCB5FFAA47A1"
        ),
        "checker_result": "PASS",
        "engineering_integrity": "PASS",
        "research_decision": "NOT_QUALIFIED_FOR_VALIDATION",
        "replication_candidate_count": 29,
        "current_candidate_count": 27,
        "replication_candidates_per_process_cpu_hour": 74.65057817998995,
        "current_candidates_per_process_cpu_hour": 66.90255207941236,
        "failed_gate": "leave_best_template_out_delta_positive",
        "matched_positive_count": 1,
        "process_exit_code": 1,
        "process_exit_attribution": (
            "POST_ARTIFACT_NOT_AUTHORIZED_VALIDATION_RESUMED_KEY_MISSING"
        ),
        "sealed_reads": 0,
        "rescue_rerun_started": False,
    },
}

_INVALID_INTENT = {
    "",
    "n/a",
    "na",
    "none",
    "tbd",
    "todo",
    "unknown",
    "\u5f85\u5b9a",
    "\u672a\u77e5",
}


def _node_id(node: dict[str, Any]) -> str:
    return str(node.get("id") or node.get("node_id") or node.get("key") or "")


def _meaningful(value: str | None) -> bool:
    return str(value or "").strip().casefold() not in _INVALID_INTENT


def _canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest().upper()


def _canonical_file_sha256(payload: bytes) -> str:
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        canonical = payload
    else:
        canonical = text.replace("\r\n", "\n").replace("\r", "\n").encode(
            "utf-8"
        )
    return hashlib.sha256(canonical).hexdigest().upper()


def _file_sha256(path: Path) -> str:
    return _canonical_file_sha256(path.read_bytes())


@lru_cache(maxsize=256)
def _git_file_payload(repo_root: Path, source_sha: str, path: str) -> bytes:
    """Read one committed source file without changing the checkout."""

    return subprocess.check_output(
        ["git", "show", f"{source_sha}:{Path(path).as_posix()}"],
        cwd=repo_root,
        stderr=subprocess.DEVNULL,
    )


def _symbol_is_declared_payload(payload: bytes, dotted_symbol: str) -> bool:
    symbol = str(dotted_symbol).rsplit(".", 1)[-1]
    tree = ast.parse(payload.decode("utf-8-sig"))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == symbol:
                return True
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == symbol for target in targets):
                return True
    return False


def _symbol_is_declared(source_path: Path, dotted_symbol: str) -> bool:
    return _symbol_is_declared_payload(source_path.read_bytes(), dotted_symbol)


def _parse_utc(value: Any, field: str, blockers: list[str]) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        blockers.append(field)
        return None
    if parsed.utcoffset() is None:
        blockers.append(field)
        return None
    return parsed


def evaluate_search_validation_kill_line(
    metrics: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the frozen development-validation stop rule without reading data.

    The caller owns metric production and checkpoint persistence.  This gate
    consumes one already-evaluated validation row, returns a deterministic
    decision, and has no optimizer, archive, proposal, or holdout side effect.
    """

    required = {
        "validation_net_mean_positive": bool(
            float(metrics.get("validation_net_mean", float("nan"))) > 0.0
        ),
        "validation_nonoverlap_floor_sortino_positive": bool(
            float(
                metrics.get(
                    "validation_nonoverlap_floor_sortino",
                    float("nan"),
                )
            )
            > 0.0
        ),
        "validation_matched_increment_positive": bool(
            float(
                metrics.get(
                    "validation_matched_increment",
                    float("nan"),
                )
            )
            > 0.0
        ),
        "validation_control_not_dominant": (
            metrics.get("validation_control_not_dominant") is True
        ),
    }
    passed = all(required.values())
    return {
        "result": (
            "PASS_CONTINUE_FROZEN_ARM"
            if passed
            else "FAIL_STOP_ARM_AND_WRITE_CHECKPOINT"
        ),
        "passed": passed,
        "conditions": required,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "candidate_generation_performed": False,
        "holdout_read": False,
    }


def _validate_search_economic_receipt(
    repo_root: Path,
    receipt: Mapping[str, Any],
    *,
    receipt_path_label: str,
) -> dict[str, Any]:
    """Validate the one explicitly authorized conditional-development receipt."""

    receipt = dict(receipt)
    blockers: list[str] = []

    if receipt.get("schema_version") != 2:
        blockers.append("schema_version")
    receipt_id = str(receipt.get("receipt_id") or "")
    receipt_spec = SEARCH_ECONOMIC_RECEIPT_SPECS.get(receipt_id)
    if receipt_spec is None:
        blockers.append("receipt_id")
        receipt_spec = SEARCH_ECONOMIC_RECEIPT_SPECS[
            "CRYPTO_SEARCH_ECONOMIC_RECEIPT_V1"
        ]
    if receipt_path_label.replace("\\", "/") != receipt_spec["path"]:
        blockers.append("receipt_path")
    status = str(receipt.get("status") or "")
    run_authorized = receipt.get("run_authorized")
    consumed_statuses = {
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE",
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_BUDGET_EXHAUSTED",
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_VALIDATION_BLOCKED",
        "RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED",
    }
    if status not in receipt_spec["allowed_statuses"]:
        blockers.append("status")
    if (
        status == "RUN_AUTHORIZED_CONDITIONAL_DEVELOPMENT"
        and run_authorized is not True
    ) or (status in consumed_statuses and run_authorized is not False):
        blockers.append("run_authorized")
    run_authorization = dict(receipt.get("run_authorization") or {})
    expected_run_authorization = {
        "decision_id": receipt_spec["decision_id"],
        "authority": "CURRENT_USER_INSTRUCTION",
        "scope": receipt_spec.get(
            "run_authorization_scope",
            "ONE_FRESH_STATE_20000_STRICT_MAXIMUM_CAMPAIGN",
        ),
        "cost_interpretation": "RESULTS_CONDITIONAL_ON_FROZEN_5_BPS",
        "parameter_tuning_allowed": False,
        "seed_change_allowed": False,
        "rescue_rerun_allowed": False,
        **dict(receipt_spec.get("run_authorization_extras") or {}),
    }
    if run_authorization != expected_run_authorization:
        blockers.append("run_authorization")
    run_outcome = dict(receipt.get("run_outcome") or {})
    expected_run_outcome = receipt_spec["expected_run_outcome"]
    if status in consumed_statuses:
        if run_outcome != expected_run_outcome:
            blockers.append("run_outcome")
    elif run_outcome:
        blockers.append("run_outcome")
    market = dict(receipt.get("market") or {})
    if market != {"asset_class": "CRYPTO", "calendar": "CONTINUOUS_UTC"}:
        blockers.append("market")

    mechanism = dict(receipt.get("mechanism") or {})
    search_campaign = dict(receipt.get("search_campaign") or {})
    direction = dict(receipt.get("direction") or {})
    portfolio = dict(receipt.get("portfolio") or {})
    execution = dict(receipt.get("execution") or {})
    cost = dict(receipt.get("cost") or {})
    optimizer_reward = dict(receipt.get("optimizer_reward") or {})
    partitions = dict(receipt.get("evidence_partition") or {})
    validation = dict(partitions.get("validation") or {})
    holdout = dict(partitions.get("holdout") or {})
    kill_line = dict(receipt.get("validation_kill_line") or {})
    boundaries = dict(receipt.get("boundaries") or {})
    component_sources = dict(receipt.get("component_sources") or {})

    expected_mechanism = str(
        receipt_spec.get(
            "mechanism_registry_symbol",
            "alphafactory_crypto.broad_search.compositional18m.skeleton_registry",
        )
    )
    expected_mapping = (
        "alphafactory_crypto.instrument_canary.grammar.MECHANISM_MAPPING"
    )
    expected_mapping_adapter = str(
        receipt_spec.get(
            "mapping_adapter_symbol",
            "alphafactory_crypto.broad_search.compositional18m."
            "mapping_id_for_mechanism_family",
        )
    )
    expected_direction = (
        "scripts.crypto_a7reward1_portfolio_reward_model.select_train_orientation"
    )
    expected_validation = (
        "alphafactory_crypto.broad_search.experiment_authority."
        "evaluate_search_validation_kill_line"
    )
    expected_validation_runtime = str(
        receipt_spec.get(
            "validation_runtime_symbol",
            "alphafactory_crypto.broad_search.search_engine_v1."
            "apply_search_validation_kill_line",
        )
    )
    expected_target_store = (
        "alphafactory_crypto.broad_search.replay_v14_binance_target."
        "BinanceTargetStore"
    )
    expected_reward = (
        "alphafactory_crypto.broad_search.pair18m.SEARCH_REWARD_AUTHORITY"
    )
    if mechanism.get("registry_symbol") != expected_mechanism:
        blockers.append("mechanism.registry_symbol")
    if mechanism.get("economic_hypothesis_field") != receipt_spec.get(
        "economic_hypothesis_field", "financial_hypothesis"
    ):
        blockers.append("mechanism.economic_hypothesis_field")
    if mechanism.get("mapping_authority_symbol") != expected_mapping:
        blockers.append("mechanism.mapping_authority_symbol")
    if mechanism.get("mapping_adapter_symbol") != expected_mapping_adapter:
        blockers.append("mechanism.mapping_adapter_symbol")
    expected_mapping_classes = set(
        receipt_spec.get("mapping_classes", {"CROSS_SECTIONAL_RELATIVE"})
    )
    observed_mapping_classes = set(
        str(value) for value in mechanism.get("mapping_classes", ())
    ) or {str(mechanism.get("mapping_class") or "")}
    if observed_mapping_classes != expected_mapping_classes:
        blockers.append("mechanism.mapping_class")
    resolved_mapping_ids = {
        str(MECHANISM_MAPPING[value])
        for value in observed_mapping_classes
        if value in MECHANISM_MAPPING
    }
    observed_portfolio_mapping_ids = set(
        str(value) for value in portfolio.get("mapping_ids", ())
    ) or {str(portfolio.get("mapping_id") or "")}
    if resolved_mapping_ids != observed_portfolio_mapping_ids:
        blockers.append("mechanism.mapping_resolution")
    if direction.get("rule") != "TRAIN_FROZEN_SIGN_ORIENTATION":
        blockers.append("direction.rule")
    if direction.get("authority_symbol") != expected_direction:
        blockers.append("direction.authority_symbol")
    if direction.get("fit_role") != "FRESH_DEVELOPMENT_TRAIN_ONLY":
        blockers.append("direction.fit_role")
    if direction.get("allowed_values") != [-1, 1]:
        blockers.append("direction.allowed_values")
    if direction.get("persist_in_candidate_ledger") is not True:
        blockers.append("direction.persist_in_candidate_ledger")
    if portfolio.get("mapping_authority_component") != "explicit_portfolio_mapping":
        blockers.append("portfolio.mapping_authority_component")
    mapping_ids = tuple(sorted(observed_portfolio_mapping_ids))
    mapping_contracts = [
        DEFAULT_MAPPING_CONTRACTS[value]
        for value in mapping_ids
        if value in DEFAULT_MAPPING_CONTRACTS
    ]
    if len(mapping_contracts) != len(mapping_ids):
        blockers.append("portfolio.mapping_id")
    if portfolio.get("shared_support_execution_horizon_cost") is not True:
        blockers.append("portfolio.shared_support_execution_horizon_cost")

    target_config_path = repo_root / str(execution.get("authority_config") or "")
    target_config: dict[str, Any] = {}
    if not target_config_path.is_file():
        blockers.append("execution.authority_config")
    else:
        target_config = json.loads(
            target_config_path.read_text(encoding="utf-8-sig")
        )
    target = dict(target_config.get("target") or {})
    target_fields = (
        "venue",
        "source",
        "price_field",
        "formula",
        "execution_delay_hours",
        "horizons_hours",
        "positive_price_required",
        "missing_value_fill",
    )
    for field in target_fields:
        if execution.get(field) != target.get(field):
            blockers.append(f"execution.{field}")
    expected_tail_purge = int(execution.get("execution_delay_hours", -1)) + max(
        (
            int(value)
            for value in execution.get("horizons_hours", ())
        ),
        default=-1,
    )
    if (
        execution.get("partition_tail_purge_hours") != 6
        or expected_tail_purge != 6
    ):
        blockers.append("execution.partition_tail_purge_hours")
    if execution.get("target_store_symbol") != expected_target_store:
        blockers.append("execution.target_store_symbol")
    if (
        execution.get("target_cache_path")
        != ".cache/crypto_search_engine_v1_4/binance_open_target_v1"
    ):
        blockers.append("execution.target_cache_path")
    if len(str(execution.get("target_cache_identity_sha256") or "")) != 64:
        blockers.append("execution.target_cache_identity_sha256")
    if execution.get("venue") != "BINANCE_USD_M":
        blockers.append("execution.venue")
    if execution.get("instrument_type") != "LINEAR_PERPETUAL":
        blockers.append("execution.instrument_type")

    if mapping_contracts:
        mapping_cost_models = {
            _canonical_sha256(dict(contract.cost_model)): dict(contract.cost_model)
            for contract in mapping_contracts
        }
        if len(mapping_cost_models) != 1:
            blockers.append("cost.mapping_contract_divergence")
        mapping_cost = next(iter(mapping_cost_models.values()))
        expected_cost = {
            "model_id": mapping_cost.get("id"),
            "cost_bps": float(mapping_cost.get("cost_bps")),
            "initial_establishment_charged": mapping_cost.get(
                "initial_establishment_charged"
            ),
        }
        observed_cost = {
            "model_id": cost.get("model_id"),
            "cost_bps": float(cost.get("cost_bps", float("nan"))),
            "initial_establishment_charged": cost.get(
                "initial_establishment_charged"
            ),
        }
        if observed_cost != expected_cost:
            blockers.append("cost.mapping_contract")
    else:
        observed_cost = {}
    if cost.get("authority_component") != "real_data_mapping_cost_evaluator":
        blockers.append("cost.authority_component")
    cost_mapping_ids = set(str(value) for value in cost.get("mapping_ids", ())) or {
        str(cost.get("mapping_id") or "")
    }
    if cost_mapping_ids != set(mapping_ids):
        blockers.append("cost.mapping_id")
    if cost.get("venue") != execution.get("venue"):
        blockers.append("cost.venue")
    if cost.get("instrument_type") != execution.get("instrument_type"):
        blockers.append("cost.instrument_type")
    if (
        cost.get("qualification")
        != "FROZEN_CONDITIONAL_5BPS_ASSUMPTION"
    ):
        blockers.append("cost.qualification")

    from alphafactory_crypto.broad_search.pair18m import SEARCH_REWARD_AUTHORITY

    if optimizer_reward.get("authority_symbol") != expected_reward:
        blockers.append("optimizer_reward.authority_symbol")
    if optimizer_reward.get("authority_id") != SEARCH_REWARD_AUTHORITY:
        blockers.append("optimizer_reward.authority_id")
    if optimizer_reward.get("feedback_role") != "FRESH_DEVELOPMENT_TRAIN_ONLY":
        blockers.append("optimizer_reward.feedback_role")
    if (
        optimizer_reward.get("pair_reward_role")
        != "MATCHED_ATTRIBUTION_DIAGNOSTIC_ONLY"
    ):
        blockers.append("optimizer_reward.pair_reward_role")

    train = dict(partitions.get("train") or {})
    train_start = _parse_utc(
        train.get("start"), "evidence_partition.train.start", blockers
    )
    train_end = _parse_utc(
        train.get("end_exclusive"),
        "evidence_partition.train.end_exclusive",
        blockers,
    )
    validation_start = _parse_utc(
        validation.get("start"),
        "evidence_partition.validation.start",
        blockers,
    )
    validation_end = _parse_utc(
        validation.get("end_exclusive"),
        "evidence_partition.validation.end_exclusive",
        blockers,
    )
    holdout_start = _parse_utc(
        holdout.get("start"), "evidence_partition.holdout.start", blockers
    )
    holdout_end = _parse_utc(
        holdout.get("end_exclusive"),
        "evidence_partition.holdout.end_exclusive",
        blockers,
    )
    if all(
        value is not None
        for value in (
            train_start,
            train_end,
            validation_start,
            validation_end,
            holdout_start,
            holdout_end,
        )
    ) and not (
        train_start
        < train_end
        == validation_start
        < validation_end
        == holdout_start
        < holdout_end
    ):
        blockers.append("evidence_partition.order")
    if train.get("optimizer_feedback_allowed") is not True:
        blockers.append("evidence_partition.train.optimizer_feedback_allowed")
    for field in (
        "optimizer_feedback_allowed",
        "policy_memory_write_allowed",
        "candidate_generation_allowed",
    ):
        if validation.get(field) is not False:
            blockers.append(f"evidence_partition.validation.{field}")
    for field in (
        "read_allowed",
        "optimizer_feedback_allowed",
        "policy_memory_write_allowed",
    ):
        if holdout.get(field) is not False:
            blockers.append(f"evidence_partition.holdout.{field}")
    if kill_line.get("authority_symbol") != expected_validation:
        blockers.append("validation_kill_line.authority_symbol")
    if kill_line.get("runtime_symbol") != expected_validation_runtime:
        blockers.append("validation_kill_line.runtime_symbol")
    if kill_line.get("evaluation_order") != receipt_spec.get(
        "validation_evaluation_order",
        "AFTER_FROZEN_TRAIN_POLICY_BEFORE_ANY_ADDITIONAL_BUDGET",
    ):
        blockers.append("validation_kill_line.evaluation_order")
    if kill_line.get("equal_matched_evaluated_count") is not True:
        blockers.append("validation_kill_line.equal_matched_evaluated_count")
    if (
        search_campaign.get("runner_campaign")
        != receipt_spec["runner_campaign"]
    ):
        blockers.append("search_campaign.runner_campaign")
    if search_campaign.get("runtime_date") != receipt_spec["runtime_date"]:
        blockers.append("search_campaign.runtime_date")
    if (
        search_campaign.get("carrier_id")
        != "OI_MARK_RANKS51_200_X_AGGTRADES_TOP200_ALIGNED"
    ):
        blockers.append("search_campaign.carrier_id")
    if (
        search_campaign.get("carrier_manifest")
        != (
            "runtime/crypto_search_engine_v1_4_oi_flow_20260728/"
            "aligned_carrier_manifest.json"
        )
    ):
        blockers.append("search_campaign.carrier_manifest")
    if (
        search_campaign.get("carrier_cache_identity_sha256")
        != "E8BFD15AF1EA58807A75868D52AD3535126DFB77CEDEB404EEE8E690AA58F2BA"
    ):
        blockers.append("search_campaign.carrier_cache_identity_sha256")
    if search_campaign.get("field_count") != 115:
        blockers.append("search_campaign.field_count")
    if search_campaign.get("strict_evaluated_target") != int(
        receipt_spec.get("strict_evaluated_target", 20_000)
    ):
        blockers.append("search_campaign.strict_evaluated_target")
    if search_campaign.get("checkpoint_size") != int(
        receipt_spec.get("checkpoint_size", 2_000)
    ):
        blockers.append("search_campaign.checkpoint_size")
    if search_campaign.get("checkpoint_count") != int(
        receipt_spec.get("checkpoint_count", 10)
    ):
        blockers.append("search_campaign.checkpoint_count")
    if search_campaign.get("fresh_state") is not True:
        blockers.append("search_campaign.fresh_state")
    expected_seed_set = receipt_spec.get("seed_set")
    if expected_seed_set is not None:
        if tuple(int(value) for value in search_campaign.get("seed_set") or ()) != tuple(
            int(value) for value in expected_seed_set
        ):
            blockers.append("search_campaign.seed_set")
        if (
            search_campaign.get("seed_derivation")
            != receipt_spec.get("seed_derivation")
        ):
            blockers.append("search_campaign.seed_derivation")
    elif "seed_set" in search_campaign or "seed_derivation" in search_campaign:
        blockers.append("search_campaign.unexpected_seed_override")
    if (
        kill_line.get("orchestration_campaign")
        != receipt_spec["runner_campaign"]
    ):
        blockers.append("validation_kill_line.orchestration_campaign")
    if kill_line.get("trigger_after_train_checkpoint_index") != int(
        receipt_spec.get("validation_trigger", 0)
    ):
        blockers.append(
            "validation_kill_line.trigger_after_train_checkpoint_index"
        )
    if kill_line.get("minimum_evaluated_per_active_arm") != int(
        receipt_spec.get("validation_minimum_evaluated_per_active_arm", 128)
    ):
        blockers.append("validation_kill_line.minimum_evaluated_per_active_arm")
    if kill_line.get("evaluated_per_active_arm") != int(
        receipt_spec.get("validation_evaluated_per_active_arm", 128)
    ):
        blockers.append("validation_kill_line.evaluated_per_active_arm")
    if kill_line.get("required_horizons_hours") != receipt_spec.get(
        "validation_required_horizons_hours", [1, 4]
    ):
        blockers.append("validation_kill_line.required_horizons_hours")
    if kill_line.get("evaluated_per_arm_per_horizon") != int(
        receipt_spec.get("validation_evaluated_per_arm_per_horizon", 64)
    ):
        blockers.append(
            "validation_kill_line.evaluated_per_arm_per_horizon"
        )
    if (
        kill_line.get("candidate_selection")
        != receipt_spec.get(
            "validation_candidate_selection",
            "TOP_TRAIN_SEARCH_REWARD_PER_REQUIRED_HORIZON_"
            "THEN_COMPLETION_ORDINAL",
        )
    ):
        blockers.append("validation_kill_line.candidate_selection")
    if (
        kill_line.get("arm_aggregation")
        != receipt_spec.get(
            "validation_arm_aggregation",
            "WORST_HORIZON_EQUAL_WEIGHT_FROZEN_CANDIDATE_ENSEMBLE",
        )
    ):
        blockers.append("validation_kill_line.arm_aggregation")
    if kill_line.get("threshold_tuning_allowed") is not False:
        blockers.append("validation_kill_line.threshold_tuning_allowed")
    if kill_line.get("failure_action") != receipt_spec.get(
        "validation_failure_action",
        "STOP_ARM_AND_WRITE_CHECKPOINT",
    ):
        blockers.append("validation_kill_line.failure_action")
    if kill_line.get("failed_arm_allocation") != receipt_spec.get(
        "validation_failed_arm_allocation",
        "EXISTING_ARM_STATE_EXITED",
    ):
        blockers.append("validation_kill_line.failed_arm_allocation")
    if (
        kill_line.get("continuation_action")
        != receipt_spec.get(
            "validation_continuation_action",
            "NEXT_CHECKPOINT_USES_EXISTING_ARM_STATE",
        )
    ):
        blockers.append("validation_kill_line.continuation_action")
    if "random_control_survival_required" in receipt_spec and (
        kill_line.get("random_control_survival_required")
        is not receipt_spec["random_control_survival_required"]
    ):
        blockers.append(
            "validation_kill_line.random_control_survival_required"
        )
    if "control_arm_id" in receipt_spec and (
        kill_line.get("control_arm_id") != receipt_spec["control_arm_id"]
    ):
        blockers.append("validation_kill_line.control_arm_id")
    if kill_line.get("checkpoint_action") != receipt_spec.get(
        "validation_checkpoint_action",
        "EXISTING_CAMPAIGN_CHECKPOINT_WITH_VALIDATION_ARTIFACTS",
    ):
        blockers.append("validation_kill_line.checkpoint_action")

    for field in (
        "oos",
        "challenge",
        "recent",
        "may_stress",
        "forward",
        "promotion",
        "cross_sprint_adaptive_memory",
        "a_share_constraints_applied",
    ):
        if boundaries.get(field) is not False:
            blockers.append(f"boundaries.{field}")
    if boundaries.get("development_only") is not True:
        blockers.append("boundaries.development_only")
    if boundaries.get("sealed_reads") != 0:
        blockers.append("boundaries.sealed_reads")

    source_symbols = {
        "mechanism": mechanism.get("registry_symbol"),
        "mechanism_mapping": mechanism.get("mapping_authority_symbol"),
        "direction": direction.get("authority_symbol"),
        "validation_kill_line": kill_line.get("authority_symbol"),
        "target_execution": execution.get("target_store_symbol"),
        "optimizer_reward_and_matched_attribution": optimizer_reward.get(
            "authority_symbol"
        ),
        "runtime_binding": (
            "alphafactory_crypto.broad_search.search_engine_v1."
            "_require_bound_economic_run"
        ),
    }
    component_sha256: dict[str, str] = {}
    component_payloads: dict[str, bytes] = {}
    historical_component_sha256: dict[str, str] | None = None
    historical_source_sha = ""
    if status in consumed_statuses:
        historical_source_sha = str(run_outcome.get("producer_source_sha") or "")
        frozen_contract_path = (
            repo_root
            / str(run_outcome.get("runtime") or "")
            / "frozen_contract.json"
        )
        if not frozen_contract_path.is_file():
            blockers.append("run_outcome.frozen_contract")
        else:
            frozen_contract = json.loads(
                frozen_contract_path.read_text(encoding="utf-8-sig")
            )
            if str(frozen_contract.get("source_sha") or "") != historical_source_sha:
                blockers.append("run_outcome.producer_source_sha")
            frozen_receipt = dict(frozen_contract.get("economic_receipt") or {})
            historical_component_sha256 = {
                str(key): str(value).upper()
                for key, value in dict(
                    frozen_receipt.get("component_sha256") or {}
                ).items()
            }
    required_component_sources = receipt_spec.get("required_component_sources")
    if required_component_sources is not None and set(component_sources) != set(
        required_component_sources
    ):
        blockers.append("component_sources.required_set")
    for component, source_binding in component_sources.items():
        if not isinstance(source_binding, Mapping):
            blockers.append(f"component_sources.{component}")
            continue
        relative_source_path = str(source_binding.get("path") or "")
        source_path = repo_root / relative_source_path
        expected_sha256 = str(source_binding.get("sha256") or "").upper()
        if status in consumed_statuses:
            try:
                source_payload = _git_file_payload(
                    repo_root,
                    historical_source_sha,
                    relative_source_path,
                )
            except (OSError, subprocess.CalledProcessError):
                blockers.append(f"component_sources.{component}.producer_blob")
                continue
            expected_sha256 = str(
                (historical_component_sha256 or {}).get(str(component)) or ""
            ).upper()
            if not expected_sha256:
                blockers.append(f"component_sources.{component}.frozen_hash")
        else:
            if not source_path.is_file():
                blockers.append(f"component_sources.{component}")
                continue
            source_payload = source_path.read_bytes()
        observed_sha256 = _canonical_file_sha256(source_payload)
        component_sha256[str(component)] = observed_sha256
        component_payloads[str(component)] = source_payload
        if observed_sha256 != expected_sha256:
            blockers.append(f"component_hash.{component}")
        symbol = source_symbols.get(str(component))
        if symbol and not _symbol_is_declared_payload(source_payload, str(symbol)):
            blockers.append(f"component_symbol.{component}")
    mechanism_payload = component_payloads.get("mechanism")
    if mechanism_payload is not None:
        if not _symbol_is_declared_payload(
            mechanism_payload,
            expected_mapping_adapter,
        ):
            blockers.append("component_symbol.mechanism_mapping_adapter")
    runtime_payload = component_payloads.get("runtime_binding")
    if runtime_payload is not None:
        if not _symbol_is_declared_payload(
            runtime_payload,
            expected_validation_runtime,
        ):
            blockers.append("component_symbol.validation_kill_line_runtime")

    if blockers:
        raise RuntimeError(
            "SEARCH_ECONOMIC_RECEIPT_BLOCKED: "
            + "; ".join(sorted(set(blockers)))
        )
    return {
        "result": str(receipt["status"]),
        "receipt_path": receipt_path_label,
        "receipt_sha256": _canonical_sha256(receipt),
        "component_sha256": component_sha256,
        "market": market,
        "search_campaign": search_campaign,
        "mechanism": mechanism,
        "direction": direction,
        "portfolio": portfolio,
        "execution": execution,
        "cost": observed_cost,
        "optimizer_reward": optimizer_reward,
        "evidence_partition": {
            "train": train,
            "validation": validation,
            "holdout": holdout,
        },
        "train": train,
        "validation": validation,
        "holdout": holdout,
        "validation_kill_line": kill_line,
        "run_authorization": run_authorization,
        "run_authorized": bool(receipt["run_authorized"]),
        "run_outcome": run_outcome,
        "formal_claims_authorized": False,
    }


def _materialize_search_economic_receipt(
    repo_root: Path,
    receipt: Mapping[str, Any],
) -> dict[str, Any]:
    """Materialize a narrowly authorized receipt over one hash-bound base contract."""

    raw = dict(receipt)
    base_path_label = str(raw.get("base_receipt_path") or "").replace("\\", "/")
    if not base_path_label:
        return raw
    required_keys = {
        "schema_version",
        "receipt_id",
        "status",
        "run_authorized",
        "run_authorization",
        "base_receipt_path",
        "base_receipt_sha256",
        "search_campaign",
        "validation_kill_line",
    }
    optional_keys = {"run_outcome"}
    if not required_keys.issubset(raw) or not set(raw).issubset(
        required_keys | optional_keys
    ):
        raise RuntimeError(
            "SEARCH_ECONOMIC_RECEIPT_BLOCKED: inherited_receipt:SCHEMA"
        )
    if base_path_label != DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH:
        raise RuntimeError(
            "SEARCH_ECONOMIC_RECEIPT_BLOCKED: inherited_receipt:BASE_PATH"
        )
    base_path = repo_root / base_path_label
    if not base_path.is_file():
        raise RuntimeError(
            "SEARCH_ECONOMIC_RECEIPT_BLOCKED: inherited_receipt:BASE_MISSING"
        )
    base = json.loads(base_path.read_text(encoding="utf-8-sig"))
    base_sha256 = _canonical_sha256(base)
    if str(raw.get("base_receipt_sha256") or "").upper() != base_sha256:
        raise RuntimeError(
            "SEARCH_ECONOMIC_RECEIPT_BLOCKED: inherited_receipt:BASE_HASH"
        )
    _validate_search_economic_receipt(
        repo_root,
        base,
        receipt_path_label=base_path_label,
    )
    search_override = dict(raw.get("search_campaign") or {})
    validation_override = dict(raw.get("validation_kill_line") or {})
    receipt_spec = SEARCH_ECONOMIC_RECEIPT_SPECS.get(
        str(raw.get("receipt_id") or "")
    )
    allowed_search_override = set(
        dict(receipt_spec or {}).get(
            "search_override_keys", {"runner_campaign"}
        )
    )
    if set(search_override) != allowed_search_override:
        raise RuntimeError(
            "SEARCH_ECONOMIC_RECEIPT_BLOCKED: inherited_receipt:SEARCH_OVERRIDE"
        )
    if set(validation_override) != {"orchestration_campaign"}:
        raise RuntimeError(
            "SEARCH_ECONOMIC_RECEIPT_BLOCKED: "
            "inherited_receipt:VALIDATION_OVERRIDE"
        )
    effective = dict(base)
    for key in (
        "schema_version",
        "receipt_id",
        "status",
        "run_authorized",
        "run_authorization",
    ):
        effective[key] = raw[key]
    effective.pop("run_outcome", None)
    if raw.get("run_outcome"):
        effective["run_outcome"] = dict(raw["run_outcome"])
    effective["search_campaign"] = {
        **dict(base["search_campaign"]),
        **search_override,
    }
    effective["validation_kill_line"] = {
        **dict(base["validation_kill_line"]),
        **validation_override,
    }
    effective["contract_inheritance"] = {
        "base_receipt_path": base_path_label,
        "base_receipt_sha256": base_sha256,
        "authorization_receipt_sha256": _canonical_sha256(raw),
    }
    return effective


def resolve_search_economic_receipt(
    repo_root: Path,
    receipt_path: str | None = None,
) -> dict[str, Any]:
    """Verify the thin crypto campaign binding without reimplementing its authorities."""

    relative_receipt = str(
        receipt_path or DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH
    ).replace("\\", "/")
    registered_paths = {
        str(spec["path"]) for spec in SEARCH_ECONOMIC_RECEIPT_SPECS.values()
    }
    if relative_receipt not in registered_paths:
        raise RuntimeError(
            "SEARCH_ECONOMIC_RECEIPT_BLOCKED: "
            f"receipt:UNREGISTERED:{relative_receipt}"
        )
    path = repo_root / relative_receipt
    if not path.is_file():
        raise RuntimeError(
            f"SEARCH_ECONOMIC_RECEIPT_BLOCKED: receipt:MISSING:{path}"
        )
    receipt = _materialize_search_economic_receipt(
        repo_root,
        json.loads(path.read_text(encoding="utf-8-sig")),
    )
    return _validate_search_economic_receipt(
        repo_root,
        receipt,
        receipt_path_label=relative_receipt,
    )


def resolve_real_experiment_authorities(repo_root: Path) -> dict[str, Any]:
    current_path = repo_root / ".planning" / "graphs" / "current.json"
    if not current_path.is_file():
        raise RuntimeError(f"REAL_EXPERIMENT_AUTHORITY_BLOCKED: CURRENT missing: {current_path}")
    current = json.loads(current_path.read_text(encoding="utf-8-sig"))
    nodes = {
        _node_id(node): node
        for node in (current.get("nodes") or current.get("components") or [])
        if isinstance(node, dict) and _node_id(node)
    }
    bindings_by_role: dict[str, list[dict[str, Any]]] = {}
    for binding in current.get("semantic_authorities") or []:
        if isinstance(binding, dict):
            role = str(binding.get("semantic_role") or "")
            bindings_by_role.setdefault(role, []).append(binding)

    authority_refs: dict[str, dict[str, Any]] = {}
    blockers: list[str] = []
    non_formal: list[str] = []
    for role in REQUIRED_REAL_EXPERIMENT_ROLES:
        bindings = bindings_by_role.get(role, [])
        if not bindings:
            authority_refs[role] = {"status": "VACANT"}
            blockers.append(f"{role}:VACANT")
            continue
        if len(bindings) != 1:
            authority_refs[role] = {
                "status": "MULTIPLE_CONFLICTING_AUTHORITIES",
                "components": ",".join(
                    sorted(
                        str(item.get("authoritative_component") or "")
                        for item in bindings
                    )
                ),
            }
            blockers.append(f"{role}:MULTIPLE_CONFLICTING_AUTHORITIES")
            continue

        binding = bindings[0]
        component = str(binding.get("authoritative_component") or "")
        authority_class = str(binding.get("authority_class") or "UNCLASSIFIED").upper()
        node = nodes.get(component)
        lifecycle = str((node or {}).get("lifecycle") or (node or {}).get("status") or "")
        active_authority = (node or {}).get("active_authority")
        validation = (node or {}).get("validation")
        validation_result = (
            str(validation.get("result") or "").upper()
            if isinstance(validation, dict)
            else ""
        )
        if not node:
            status = "STALE"
        elif lifecycle.upper() in {"DEPRECATED", "REMOVED", "SUPERSEDED"}:
            status = "STALE"
        elif validation_result in {"FAIL", "FAILED", "ERROR", "STALE"}:
            status = "STALE"
        elif active_authority is not True:
            status = "INACTIVE_AUTHORITY"
        elif authority_class == "FORMAL":
            status = "RESOLVED"
        elif authority_class == "NON_FORMAL":
            status = "FOUND_BUT_UNQUALIFIED"
            non_formal.append(role)
        else:
            status = "FOUND_BUT_UNQUALIFIED"

        authority_refs[role] = {
            "status": status,
            "component": component,
            "authority_class": authority_class,
            "lifecycle": lifecycle,
            "active_authority": active_authority,
        }
        if (
            status in {"STALE", "INACTIVE_AUTHORITY"}
            or authority_class not in {"FORMAL", "NON_FORMAL"}
        ):
            blockers.append(f"{role}:{status}")

    return {
        "authority_refs": authority_refs,
        "blockers": blockers,
        "non_formal_roles": non_formal,
    }


def _validate_temporal_successor_authority_exception(
    repo_root: Path,
    authorization: Mapping[str, Any],
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    """Validate the registered schema-2, one-workspace successor exception."""

    blockers: list[str] = []
    path = repo_root / TEMPORAL_SUCCESSOR_AUTHORIZATION_PATH
    if not path.is_file():
        return ["receipt_bound_non_formal_authorization:MISSING"], {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return ["receipt_bound_non_formal_authorization:READ"], {}
    run_authorization = dict(payload.get("run_authorization") or {})
    expected_call = {
        "decision_id": str(run_authorization.get("decision_id") or ""),
        "authority": "CURRENT_USER_INSTRUCTION",
        "scope": TEMPORAL_SUCCESSOR_SCOPE,
        "receipt_path": TEMPORAL_SUCCESSOR_AUTHORIZATION_PATH,
        "receipt_sha256": _canonical_sha256(payload),
        "run_authorized": True,
    }
    if dict(authorization) != expected_call:
        blockers.append("receipt_bound_non_formal_authorization:INVALID")
    content_sha = _canonical_sha256(
        {
            key: value
            for key, value in payload.items()
            if key != "authorization_sha256"
        }
    )
    if (
        payload.get("schema_version") != 2
        or payload.get("execution_mode") != "30K_TO_50K_SUCCESSOR"
        or payload.get("status")
        != "RUN_AUTHORIZED_ONE_TIME_30K_TO_50K_DEVELOPMENT_SUCCESSOR"
        or payload.get("run_authorized") is not True
        or payload.get("consumed") is not False
        or payload.get("authorization_sha256") != content_sha
        or run_authorization
        != {
            "authority": "CURRENT_USER_INSTRUCTION",
            "decision_id": expected_call["decision_id"],
            "scope": TEMPORAL_SUCCESSOR_SCOPE,
        }
        or not expected_call["decision_id"]
    ):
        blockers.append("receipt_bound_non_formal_authorization:HASH_OR_SCOPE")
    boundaries = dict(payload.get("boundaries") or {})
    if (
        boundaries.get("train_only") is not True
        or boundaries.get("validation") is not False
        or boundaries.get("oos") is not False
        or boundaries.get("holdout") is not False
        or boundaries.get("forward") is not False
        or boundaries.get("promotion") is not False
        or boundaries.get("automatic_expansion") is not False
        or int(boundaries.get("sealed_reads", -1)) != 0
    ):
        blockers.append("receipt_bound_non_formal_authorization:SEALED_BOUNDARY")
    authority_identity = dict(payload.get("authority_identity") or {})
    expected_role_bindings = {
        "target": {
            "component": "real_policy_upgrade_canary",
            "component_sha256": authority_identity.get("target_contract_sha256"),
        },
        "optimizer_reward": {
            "component": "real_policy_upgrade_canary",
            "component_sha256": authority_identity.get(
                "optimizer_reward_and_matched_attribution_sha256"
            ),
        },
        "execution_price": {
            "component": "real_policy_upgrade_canary",
            "component_sha256": authority_identity.get("target_execution_sha256"),
        },
        "cost": {
            "component": "real_data_mapping_cost_evaluator",
            "component_sha256": authority_identity.get(
                "portfolio_mapping_and_cost_sha256"
            ),
        },
    }
    role_bindings = dict(payload.get("receipt_bound_role_bindings") or {})
    if role_bindings != expected_role_bindings or any(
        not str(value.get("component_sha256") or "")
        for value in expected_role_bindings.values()
    ):
        blockers.append("receipt_bound_non_formal_authorization:ROLE_BINDING")
    return blockers, {
        role: dict(value) for role, value in expected_role_bindings.items()
    }


def _validate_temporal_policy_validation_authority_exception(
    repo_root: Path,
    authorization: Mapping[str, Any],
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    """Validate the one-run, balanced development-validation exception."""

    blockers: list[str] = []
    path = repo_root / TEMPORAL_POLICY_VALIDATION_AUTHORIZATION_PATH
    if not path.is_file():
        return ["receipt_bound_non_formal_authorization:MISSING"], {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return ["receipt_bound_non_formal_authorization:READ"], {}
    run_authorization = dict(payload.get("run_authorization") or {})
    expected_call = {
        "decision_id": str(run_authorization.get("decision_id") or ""),
        "authority": "CURRENT_USER_INSTRUCTION",
        "scope": TEMPORAL_POLICY_VALIDATION_SCOPE,
        "receipt_path": TEMPORAL_POLICY_VALIDATION_AUTHORIZATION_PATH,
        "receipt_sha256": _canonical_sha256(payload),
        "run_authorized": True,
    }
    if dict(authorization) != expected_call:
        blockers.append("receipt_bound_non_formal_authorization:INVALID")
    content_sha = _canonical_sha256(
        {key: value for key, value in payload.items() if key != "authorization_sha256"}
    )
    status = payload.get("status")
    continuation = dict(payload.get("continuation") or {})
    continuation_authorized = (
        status == "RUN_AUTHORIZED_SOURCE_REPAIR_CONTINUATION"
        and run_authorization.get("decision_id")
        == "USER_AUTHORIZED_TEMPORAL_POLICY_VALIDATION_SOURCE_REPAIR_CONTINUATION_20260812"
        and continuation
        == {
            "mode": "REUSE_VERIFIED_FULL_PASS_EVALUATE_MISSING_BLOCKS",
            "replacement_of_authorization_sha256": "CA0F769518435271811BA4B813F130B42287D3126D92542B811DE03FC7972E75",
            "source_runtime": "runtime/crypto_temporal_policy_validation_v1_20260812r1",
            "source_task_id": "job_20260812_105149_89f2cf",
            "source_producer_sha": "cf0db857ea285880ae3528586f747967b5ea8996",
            "full_pass_candidate_ledger_path": "runtime/crypto_temporal_policy_validation_v1_20260812r1/passes/full/candidate_ledger.parquet",
            "full_pass_candidate_ledger_sha256": "CB40F35114DCA0666420460AD301FCB87F8A7782B85F5E975AD2598FBA36A188",
            "reused_pair_evaluation_count": 360,
            "new_pair_evaluation_count": 1080,
            "missing_pass_labels": ["block_1", "block_2", "block_3"],
            "failure_before_missing_block_evaluation": "ECONOMIC_RECEIPT_EVALUATION_BLOCK_CHANGED",
            "full_pass_market_evaluation_must_not_repeat": True,
            "completed_pass_ledgers_sha256": {
                "full": "CB40F35114DCA0666420460AD301FCB87F8A7782B85F5E975AD2598FBA36A188",
                "block_1": "F6E7C066CD845096B86DD31374C4D9AEA969191F30267825FF31CCCEBA36B65E",
                "block_2": "CAEB7CC73C8A29E2834D2CFBC89C21033BF8F947BF6E1DB597F7C45758C955F5",
                "block_3": "080A17F4D17BFE4E6DD6F3D2A24F1A1CE18352E1475AEDB99FB98D3806E03EF7",
            },
            "completed_block_evaluation_task_id": "job_20260812_164556_d9edec",
            "completed_block_evaluation_source_sha": "728e13a348398e9c866322d11271e59e9ae2e6cd",
            "source_repair_finalization_only": True,
        }
    )
    if (
        payload.get("schema_version") != 2
        or payload.get("receipt_id") != "CRYPTO_TEMPORAL_POLICY_VALIDATION_V1"
        or status
        not in {
            "RUN_AUTHORIZED_ONE_TIME_DEVELOPMENT_VALIDATION",
            "RUN_AUTHORIZED_SOURCE_REPAIR_CONTINUATION",
        }
        or (
            status == "RUN_AUTHORIZED_SOURCE_REPAIR_CONTINUATION"
            and not continuation_authorized
        )
        or payload.get("run_authorized") is not True
        or payload.get("consumed") is not False
        or payload.get("authorization_sha256") != content_sha
        or run_authorization
        != {
            "authority": "CURRENT_USER_INSTRUCTION",
            "decision_id": expected_call["decision_id"],
            "scope": TEMPORAL_POLICY_VALIDATION_SCOPE,
        }
        or not expected_call["decision_id"]
    ):
        blockers.append("receipt_bound_non_formal_authorization:HASH_OR_SCOPE")
    split = dict(payload.get("split_contract") or {})
    train = dict(split.get("train") or {})
    validation = dict(split.get("validation") or {})
    blocks = [dict(row) for row in split.get("validation_blocks") or ()]
    if (
        train.get("end_exclusive") != validation.get("start")
        or train.get("start") != "2025-08-29T07:00:00Z"
        or validation.get("end_exclusive") != "2026-01-01T00:00:00Z"
        or len(blocks) != 3
        or int(split.get("partition_tail_purge_hours", -1)) != 6
        or int(split.get("maximum_feature_warmup_hours", -1)) != 720
        or split.get("warmup_rows_cannot_enter_labels_or_metrics") is not True
    ):
        blockers.append("receipt_bound_non_formal_authorization:SPLIT")
    boundaries = dict(payload.get("boundaries") or {})
    if (
        boundaries.get("candidate_generation") is not False
        or boundaries.get("optimizer_feedback") is not False
        or boundaries.get("policy_memory_write") is not False
        or boundaries.get("archive_write") is not False
        or boundaries.get("holdout_read") is not False
        or boundaries.get("oos") is not False
        or boundaries.get("promotion") is not False
        or boundaries.get("automatic_search_after_qualification") is not False
    ):
        blockers.append("receipt_bound_non_formal_authorization:SEALED_BOUNDARY")
    authority_identity = dict(payload.get("authority_identity") or {})
    expected_role_bindings = {
        "target": {
            "component": "real_policy_upgrade_canary",
            "component_sha256": authority_identity.get("target_contract_sha256"),
        },
        "optimizer_reward": {
            "component": "real_policy_upgrade_canary",
            "component_sha256": authority_identity.get(
                "optimizer_reward_and_matched_attribution_sha256"
            ),
        },
        "execution_price": {
            "component": "real_policy_upgrade_canary",
            "component_sha256": authority_identity.get("target_execution_sha256"),
        },
        "cost": {
            "component": "real_data_mapping_cost_evaluator",
            "component_sha256": authority_identity.get(
                "portfolio_mapping_and_cost_sha256"
            ),
        },
    }
    role_bindings = dict(payload.get("receipt_bound_role_bindings") or {})
    if role_bindings != expected_role_bindings or any(
        not str(value.get("component_sha256") or "")
        for value in expected_role_bindings.values()
    ):
        blockers.append("receipt_bound_non_formal_authorization:ROLE_BINDING")
    return blockers, {
        role: dict(value) for role, value in expected_role_bindings.items()
    }


def require_real_experiment_authority(
    repo_root: Path,
    *,
    evidence_to_add: str | None,
    decision_to_change: str | None,
    economic_receipt_required: bool = True,
    economic_receipt_path: str | None = None,
    receipt_bound_non_formal_authorization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    resolution = resolve_real_experiment_authorities(repo_root)
    blockers = list(resolution["blockers"])
    economic_receipt = None
    non_formal_binding_authorized = False
    receipt_bound_role_bindings: dict[str, dict[str, Any]] = {}
    if receipt_bound_non_formal_authorization is not None:
        authorization = dict(receipt_bound_non_formal_authorization)
        if authorization.get("scope") == TEMPORAL_SUCCESSOR_SCOPE:
            successor_blockers, receipt_bound_role_bindings = (
                _validate_temporal_successor_authority_exception(
                    repo_root, authorization
                )
            )
            blockers.extend(successor_blockers)
            non_formal_binding_authorized = not successor_blockers
        elif authorization.get("scope") == TEMPORAL_POLICY_VALIDATION_SCOPE:
            validation_blockers, receipt_bound_role_bindings = (
                _validate_temporal_policy_validation_authority_exception(
                    repo_root, authorization
                )
            )
            blockers.extend(validation_blockers)
            non_formal_binding_authorized = not validation_blockers
        else:
            expected_authorization = {
                "decision_id": "USER_AUTHORIZED_V23_FROZEN_OOS_REPLAY_20260803",
                "authority": "CURRENT_USER_INSTRUCTION",
                "scope": "ONE_READ_ONLY_FROZEN_V23_1024_COHORT_OOS_REPLAY",
                "receipt_path": V23_FROZEN_OOS_RECEIPT_PATH,
                "receipt_sha256": str(authorization.get("receipt_sha256") or ""),
                "run_authorized": True,
            }
            receipt_path = repo_root / V23_FROZEN_OOS_RECEIPT_PATH
            if authorization != expected_authorization:
                blockers.append("receipt_bound_non_formal_authorization:INVALID")
            elif not receipt_path.is_file():
                blockers.append("receipt_bound_non_formal_authorization:MISSING")
            else:
                receipt_payload = json.loads(
                    receipt_path.read_text(encoding="utf-8-sig")
                )
                if (
                    _canonical_sha256(receipt_payload)
                    != authorization["receipt_sha256"]
                    or receipt_payload.get("run_authorized") is not True
                    or dict(receipt_payload.get("run_authorization") or {}).get(
                        "decision_id"
                    )
                    != authorization["decision_id"]
                    or dict(receipt_payload.get("run_authorization") or {}).get(
                        "scope"
                    )
                    != authorization["scope"]
                ):
                    blockers.append(
                        "receipt_bound_non_formal_authorization:HASH_OR_SCOPE"
                    )
                else:
                    non_formal_binding_authorized = True
    if economic_receipt_required:
        economic_receipt = resolve_search_economic_receipt(
            repo_root,
            receipt_path=economic_receipt_path,
        )
        if economic_receipt["run_authorized"] is not True:
            blockers.append("economic_receipt:RUN_NOT_AUTHORIZED")
        else:
            non_formal_binding_authorized = True
    if non_formal_binding_authorized:
        authority_refs = {
            role: dict(value)
            for role, value in resolution["authority_refs"].items()
        }
        non_formal_roles = set(resolution["non_formal_roles"])
        for role, expected_component in (
            CONDITIONAL_RUN_NON_FORMAL_COMPONENTS.items()
        ):
            ref = authority_refs.get(role, {})
            receipt_binding = receipt_bound_role_bindings.get(role)
            if receipt_binding is not None and ref.get("status") in {
                "VACANT",
                "INACTIVE_AUTHORITY",
            }:
                blockers = [
                    value
                    for value in blockers
                    if value
                    not in {f"{role}:VACANT", f"{role}:INACTIVE_AUTHORITY"}
                ]
                authority_refs[role] = {
                    "status": "BOUND_NON_FORMAL_EXPERIMENT",
                    "component": receipt_binding["component"],
                    "component_sha256": receipt_binding["component_sha256"],
                    "authority_class": "NON_FORMAL",
                    "lifecycle": "RECEIPT_SCOPED",
                    "active_authority": False,
                }
                non_formal_roles.add(role)
                continue
            if (
                ref.get("status") == "INACTIVE_AUTHORITY"
                and ref.get("component") == expected_component
                and ref.get("authority_class") == "NON_FORMAL"
                and ref.get("lifecycle") == "EXPERIMENTAL"
                and ref.get("active_authority") is False
            ):
                blocker = f"{role}:INACTIVE_AUTHORITY"
                blockers = [value for value in blockers if value != blocker]
                ref["status"] = "BOUND_NON_FORMAL_EXPERIMENT"
                authority_refs[role] = ref
                non_formal_roles.add(role)
        resolution = {
            **resolution,
            "authority_refs": authority_refs,
            "non_formal_roles": sorted(non_formal_roles),
        }
    if not _meaningful(evidence_to_add):
        blockers.append("evidence_to_add:MISSING")
    if not _meaningful(decision_to_change):
        blockers.append("decision_to_change:MISSING")
    if blockers:
        raise RuntimeError(
            "REAL_EXPERIMENT_AUTHORITY_BLOCKED: " + "; ".join(blockers)
        )
    return {
        "result": (
            "READY_WITH_NON_FORMAL_BOUNDARIES"
            if resolution["non_formal_roles"]
            else "READY"
        ),
        "authority_refs": resolution["authority_refs"],
        "evidence_to_add": str(evidence_to_add).strip(),
        "decision_to_change": str(decision_to_change).strip(),
        "formal_claims_authorized": not bool(resolution["non_formal_roles"]),
        "economic_receipt": economic_receipt,
        "receipt_bound_non_formal_authorization": (
            dict(receipt_bound_non_formal_authorization)
            if receipt_bound_non_formal_authorization is not None
            else None
        ),
    }


__all__ = [
    "DEFAULT_SEARCH_ECONOMIC_RECEIPT_PATH",
    "SEARCH_ECONOMIC_V2_RECEIPT_PATH",
    "SEARCH_ECONOMIC_V3_RECEIPT_PATH",
    "SEARCH_ECONOMIC_V4_RECEIPT_PATH",
    "SEARCH_ECONOMIC_V5_RECEIPT_PATH",
    "SEARCH_ECONOMIC_V6_RECEIPT_PATH",
    "SEARCH_MECHANISM_V23_RECEIPT_PATH",
    "ECONOMIC_SEARCH_V6_EPOCH_ID",
    "ECONOMIC_SEARCH_V6_SEED_DERIVATION",
    "ECONOMIC_SEARCH_V6_SEEDS",
    "REQUIRED_REAL_EXPERIMENT_ROLES",
    "TEMPORAL_SUCCESSOR_AUTHORIZATION_PATH",
    "TEMPORAL_SUCCESSOR_SCOPE",
    "TEMPORAL_POLICY_VALIDATION_SCOPE",
    "evaluate_search_validation_kill_line",
    "require_real_experiment_authority",
    "resolve_real_experiment_authorities",
    "resolve_search_economic_receipt",
]
