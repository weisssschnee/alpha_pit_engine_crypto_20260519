from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7pm3_experiment_board"
REPORT = REPO / "reports" / "CRYPTO_A7PM3_CURRENT_EXPERIMENT_BOARD_20260529.md"
A7PM0 = REPO / "runtime" / "a7pm0_source_of_truth_registry" / "a7pm0_manifest.json"
A7PM2 = REPO / "runtime" / "a7pm2_candidate_lifecycle" / "a7pm2_manifest.json"
A7FF52E = REPO / "runtime" / "a7ff52e_materialization_preflight" / "a7ff52e_manifest.json"
A7FF53 = REPO / "runtime" / "a7ff53_numeric_response_contract" / "a7ff53_manifest.json"
A7FF53E_S00 = REPO / "runtime" / "a7ff53e_numeric_response_execution_s00" / "a7ff53e_s00_manifest.json"
A7FF53E = REPO / "runtime" / "a7ff53e_numeric_response_summary" / "a7ff53e_manifest.json"
A7FF54 = REPO / "runtime" / "a7ff54_numeric_clue_consolidation" / "a7ff54_manifest.json"
A7FF55 = REPO / "runtime" / "a7ff55_selector_repair_contract" / "a7ff55_manifest.json"
A7FF55D = REPO / "runtime" / "a7ff55d_selector_repair_partial_dryrun" / "a7ff55d_manifest.json"
A7FF55F = REPO / "runtime" / "a7ff55f_full_primary_input_rebuild" / "a7ff55f_manifest.json"
A7FF55R = REPO / "runtime" / "a7ff55r_selector_field_family_repair_contract" / "a7ff55r_manifest.json"
A7FF55R1 = REPO / "runtime" / "a7ff55r1_supplemental_queue_feasibility" / "a7ff55r1_manifest.json"
A7FF55R2 = REPO / "runtime" / "a7ff55r2_atlas_field_family_generation_repair" / "a7ff55r2_manifest.json"
A7FF55R3 = REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation" / "a7ff55r3_manifest.json"
A7FF55R4 = REPO / "runtime" / "a7ff55r4_repaired_atlas_coverage_audit" / "a7ff55r4_manifest.json"
A7FF55R5 = REPO / "runtime" / "a7ff55r5_repaired_atlas_numeric_contract" / "a7ff55r5_manifest.json"
A7FF55R5E = REPO / "runtime" / "a7ff55r5e_sharded_numeric_summary" / "a7ff55r5e_manifest.json"
A7FFCORE0 = REPO / "runtime" / "a7ffcore0_typed_ast_governance" / "a7ffcore0_manifest.json"
A7FFCORE1 = REPO / "runtime" / "a7ffcore1_ast_schema_adapter" / "a7ffcore1_manifest.json"
A7FFCORE2 = REPO / "runtime" / "a7ffcore2_feature_subgraph_registry" / "a7ffcore2_manifest.json"
A7FFCORE3 = REPO / "runtime" / "a7ffcore3_formula_gen_subgraph_gate" / "a7ffcore3_manifest.json"
A7FFCORE4 = REPO / "runtime" / "a7ffcore4_gate_implementation_regression" / "a7ffcore4_manifest.json"
A7FFCORE5 = REPO / "runtime" / "a7ffcore5_gate_native_generation_dryrun" / "a7ffcore5_manifest.json"
A7FFCORE6 = REPO / "runtime" / "a7ffcore6_materialization_preflight_contract" / "a7ffcore6_manifest.json"
A7FFCORE6E = REPO / "runtime" / "a7ffcore6e_materialization_preflight" / "a7ffcore6e_manifest.json"
A7FFCORE7 = REPO / "runtime" / "a7ffcore7_numeric_response_contract" / "a7ffcore7_manifest.json"
A7FFCORE7E = REPO / "runtime" / "a7ffcore7e_numeric_response" / "a7ffcore7e_manifest.json"
A7FFCORE7R = REPO / "runtime" / "a7ffcore7r_control_policy_forensic" / "a7ffcore7r_manifest.json"
A7FFCORE7ER = REPO / "runtime" / "a7ffcore7er_repaired_numeric_response" / "a7ffcore7er_manifest.json"
A7FFCORE8 = REPO / "runtime" / "a7ffcore8_numeric_clue_consolidation" / "a7ffcore8_manifest.json"
A7FFCORE8E = REPO / "runtime" / "a7ffcore8e_replay_preflight_packet_audit" / "a7ffcore8e_manifest.json"
A7FFCORE9 = REPO / "runtime" / "a7ffcore9_bounded_replay_contract" / "a7ffcore9_manifest.json"
A7FFCORE9E = REPO / "runtime" / "a7ffcore9e_bounded_replay" / "a7ffcore9e_manifest.json"
A7FFCORE10E = REPO / "runtime" / "a7ffcore10e_search_readiness_audit" / "a7ffcore10e_manifest.json"
A7FFCORE11 = REPO / "runtime" / "a7ffcore11_small_expansion_contract" / "a7ffcore11_manifest.json"
A7FFCORE11E = REPO / "runtime" / "a7ffcore11e_small_dry_generation" / "a7ffcore11e_manifest.json"
A7FFCORE12 = REPO / "runtime" / "a7ffcore12_blueprint_registration_audit" / "a7ffcore12_manifest.json"
A7FFCORE12E = REPO / "runtime" / "a7ffcore12e_materialization_preflight" / "a7ffcore12e_manifest.json"
A7FFCORE13 = REPO / "runtime" / "a7ffcore13_numeric_response_contract" / "a7ffcore13_manifest.json"
A7FFCORE13E = REPO / "runtime" / "a7ffcore13e_numeric_response" / "a7ffcore13e_manifest.json"
A7FFCORE14 = REPO / "runtime" / "a7ffcore14_replay_preflight_contract" / "a7ffcore14_manifest.json"
A7FFCORE14E = REPO / "runtime" / "a7ffcore14e_bounded_replay" / "a7ffcore14e_manifest.json"
A7FFCORE14R = REPO / "runtime" / "a7ffcore14r_replay_failure_forensic" / "a7ffcore14r_manifest.json"
A7FFCORE14S = REPO / "runtime" / "a7ffcore14s_replay_packet_repair_contract" / "a7ffcore14s_manifest.json"
A7FFCORE14SE = REPO / "runtime" / "a7ffcore14se_repaired_packet_construction" / "a7ffcore14se_manifest.json"
A7FFCORE14SEE = REPO / "runtime" / "a7ffcore14see_sharded_bounded_replay" / "a7ffcore14see_manifest.json"
A7FFCORE14SER = REPO / "runtime" / "a7ffcore14ser_repaired_replay_forensic" / "a7ffcore14ser_manifest.json"
A7FFCORE15X = REPO / "runtime" / "a7ffcore15x_objective_surface_reset_contract" / "a7ffcore15x_manifest.json"
A7FFCORE15Y = REPO / "runtime" / "a7ffcore15y_replay_stability_surface" / "a7ffcore15y_manifest.json"
A7FFCORE15YR = REPO / "runtime" / "a7ffcore15yr_surface_failure_repair" / "a7ffcore15yr_manifest.json"


BASE_BLOCKED = {
    "A7FF-24R4E execution": "pending explicit heavy-execution authorization; A7FF-24R4 contract is ready but numeric wave execution is not started",
    "A7FF-51 execution": "not authorized by A7FF-R11; only contract drafting is allowed",
    "A7FF-50": "not authorized by A7FF-49; no non-reference non-L5 candidates exist in current maps",
    "A7FF-48": "not authorized by A7FF-47; frozen clues fail non-L5 label translation",
    "A7FF-45 continuation": "bounded replay passed but is superseded by A7FF-47 L5-only translation hold",
    "A7FF-43 deep forensic": "not authorized by A7FF-42; selected control-strict non-L7 evidence remains single-family",
    "A7FF-41 control-strict expansion": "not authorized by A7FF-40; selected control-strict non-L7 evidence remains single-family",
    "A7FF search execution": "numeric wave has clues but still no replay/search authorization",
    "A7AL-2Y generation": "not authorized",
    "A7AL-3 large search": "not authorized",
    "direct OI-price rerun": "superseded weak prior / not authorized",
    "A7AL-2Q": "not authorized by A7AL-2X0",
    "alpha proof": "not authorized",
    "shadow/paper/live": "not authorized",
}


def board_state() -> tuple[dict[str, str], dict[str, str], pd.DataFrame]:
    a7ff52e = read_json(A7FF52E)
    a7ff53 = read_json(A7FF53)
    a7ff53e_s00 = read_json(A7FF53E_S00)
    a7ff53e = read_json(A7FF53E)
    a7ff54 = read_json(A7FF54)
    a7ff55 = read_json(A7FF55)
    a7ff55d = read_json(A7FF55D)
    a7ff55f = read_json(A7FF55F)
    a7ff55r = read_json(A7FF55R)
    a7ff55r1 = read_json(A7FF55R1)
    a7ff55r2 = read_json(A7FF55R2)
    a7ff55r3 = read_json(A7FF55R3)
    a7ff55r4 = read_json(A7FF55R4)
    a7ff55r5 = read_json(A7FF55R5)
    a7ff55r5e = read_json(A7FF55R5E)
    a7ffcore0 = read_json(A7FFCORE0)
    a7ffcore1 = read_json(A7FFCORE1)
    a7ffcore2 = read_json(A7FFCORE2)
    a7ffcore3 = read_json(A7FFCORE3)
    a7ffcore4 = read_json(A7FFCORE4)
    a7ffcore5 = read_json(A7FFCORE5)
    a7ffcore6 = read_json(A7FFCORE6)
    a7ffcore6e = read_json(A7FFCORE6E)
    a7ffcore7 = read_json(A7FFCORE7)
    a7ffcore7e = read_json(A7FFCORE7E)
    a7ffcore7r = read_json(A7FFCORE7R)
    a7ffcore7er = read_json(A7FFCORE7ER)
    a7ffcore8 = read_json(A7FFCORE8)
    a7ffcore8e = read_json(A7FFCORE8E)
    a7ffcore9 = read_json(A7FFCORE9)
    a7ffcore9e = read_json(A7FFCORE9E)
    a7ffcore10e = read_json(A7FFCORE10E)
    a7ffcore11 = read_json(A7FFCORE11)
    a7ffcore11e = read_json(A7FFCORE11E)
    a7ffcore12 = read_json(A7FFCORE12)
    a7ffcore12e = read_json(A7FFCORE12E)
    a7ffcore13 = read_json(A7FFCORE13)
    a7ffcore13e = read_json(A7FFCORE13E)
    a7ffcore14 = read_json(A7FFCORE14)
    a7ffcore14e = read_json(A7FFCORE14E)
    a7ffcore14r = read_json(A7FFCORE14R)
    a7ffcore14s = read_json(A7FFCORE14S)
    a7ffcore14se = read_json(A7FFCORE14SE)
    a7ffcore14see = read_json(A7FFCORE14SEE)
    a7ffcore14ser = read_json(A7FFCORE14SER)
    a7ffcore15x = read_json(A7FFCORE15X)
    a7ffcore15y = read_json(A7FFCORE15Y)
    a7ffcore15yr = read_json(A7FFCORE15YR)
    allowed = {
        "A7FF-24R4E repaired numeric wave execution option": "requires explicit user authorization; no search and no promotion",
        "A7PM-0/3 maintenance": "governance registry maintenance",
    }
    blocked = dict(BASE_BLOCKED)
    if a7ffcore15yr.get("decision") == "PASS_A7FFCORE15YR_SURFACE_FAILURE_REPAIR_READY_FOR_CORE16_ATLAS":
        allowed["A7FF-CORE16 primitive-response replay-stability atlas rebuild"] = (
            "build new objective atlas from primitive response and replay-stability evidence; no replay execution/search/promotion"
        )
        blocked["A7FF-CORE15Z"] = "blocked: CORE15Y surface candidate breadth failed"
        blocked["A7FF bounded replay rerun"] = "blocked: CORE15YR requires atlas rebuild before any replay"
        blocked["A7FF large search"] = "blocked until CORE16 atlas passes breadth/control gates"
        current_stage = "A7FF-CORE15YR"
        status = "surface_failure_repair_ready_for_core16_atlas"
        next_task = "A7FF-CORE16 primitive-response replay-stability atlas rebuild"
    elif a7ffcore15y.get("decision") == "HOLD_A7FFCORE15Y_REPLAY_STABILITY_SURFACE_INSUFFICIENT":
        allowed["A7FF-CORE15YR objective-surface failure repair"] = (
            "contract only; diagnose insufficient objective-surface breadth and define atlas rebuild; no replay/search/promotion"
        )
        blocked["A7FF-CORE15Z"] = "blocked: CORE15Y surface candidates insufficient"
        blocked["A7FF large search"] = "blocked: CORE15Y did not establish replay-stable surface"
        current_stage = "A7FF-CORE15Y"
        status = "replay_stability_surface_hold"
        next_task = "A7FF-CORE15YR objective-surface failure repair"
    elif a7ffcore15x.get("decision") == "PASS_A7FFCORE15X_OBJECTIVE_SURFACE_RESET_CONTRACT_READY_FOR_CORE15Y":
        allowed["A7FF-CORE15Y replay-stability objective-surface builder"] = (
            "build replay-stability feature matrix from existing numeric/replay/forensic rows; no replay execution/search/promotion"
        )
        blocked["A7FF-CORE15"] = "blocked: CORE15X requires objective-surface builder before any search-readiness audit"
        blocked["A7FF bounded replay rerun"] = "blocked: CORE15X forbids rerun before objective-surface repair"
        blocked["A7FF large search"] = "blocked: replay-stable objective surface is not yet established"
        current_stage = "A7FF-CORE15X"
        status = "objective_surface_reset_contract_ready_for_core15y"
        next_task = "A7FF-CORE15Y replay-stability objective-surface builder"
    elif a7ffcore14ser.get("decision") == "PASS_A7FFCORE14SER_REPAIRED_REPLAY_FORENSIC_COMPLETE_STOP_REPLAY_EXPANSION":
        allowed["A7FF-CORE15X objective-surface reset / replay-stability repair contract"] = (
            "contract only; reset objective surface after repaired replay failure; no replay execution/search/promotion"
        )
        blocked["A7FF-CORE15"] = "blocked: CORE14SER stops replay expansion; clean pool is one candidate in one family"
        blocked["A7FF-CORE14SEE rerun"] = "blocked until CORE15X defines a new objective-surface or stability policy"
        blocked["A7FF large search"] = "blocked: repaired packet failed replay-stability gates"
        current_stage = "A7FF-CORE14SER"
        status = "repaired_replay_forensic_stop_replay_expansion"
        next_task = "A7FF-CORE15X objective-surface reset / replay-stability repair contract"
    elif a7ffcore14see.get("decision") == "HOLD_A7FFCORE14SEE_REPAIRED_BOUNDED_REPLAY_INSUFFICIENT_OR_INCOMPLETE":
        allowed["A7FF-CORE14SER repaired replay forensic"] = (
            "diagnose repaired packet replay failure after all shards complete; no rerun/search/promotion"
        )
        blocked["A7FF-CORE15"] = "blocked: CORE14SEE repaired replay is insufficient"
        blocked["A7FF large search"] = "blocked: CORE14SEE did not produce enough clean breadth"
        current_stage = "A7FF-CORE14SEE"
        status = "repaired_bounded_replay_hold"
        next_task = "A7FF-CORE14SER repaired replay forensic"
    elif a7ffcore14se.get("decision") == "PASS_A7FFCORE14SE_REPAIRED_PACKET_READY_FOR_BOUNDED_REPLAY":
        allowed["A7FF-CORE14SEE repaired packet bounded replay execution"] = (
            "execute bounded replay over repaired CORE14SE packet only; no formula search, large search, promotion, or alpha proof"
        )
        blocked["A7FF-CORE15"] = "blocked until CORE14SEE produces enough clean breadth"
        blocked["A7FF large search"] = "blocked: CORE14SE authorizes bounded replay only"
        blocked["same CORE14 packet rerun"] = "blocked: CORE14SE built a repaired packet; unchanged packet remains superseded"
        current_stage = "A7FF-CORE14SE"
        status = "repaired_packet_ready_for_core14see"
        next_task = "A7FF-CORE14SEE repaired packet bounded replay execution"
    elif a7ffcore14s.get("decision") == "PASS_A7FFCORE14S_REPLAY_PACKET_REPAIR_CONTRACT_READY_FOR_CORE14SE":
        allowed["A7FF-CORE14SE repaired packet construction / bounded replay execution"] = (
            "construct repaired packet under CORE14S rules and run bounded replay only; no formula search, large search, promotion, or alpha proof"
        )
        blocked["A7FF-CORE15"] = "blocked until CORE14SE produces enough clean breadth"
        blocked["A7FF large search"] = "blocked: CORE14S authorizes repaired bounded replay only"
        blocked["same CORE14 packet rerun"] = "blocked: CORE14S requires repaired packet, not unchanged rerun"
        current_stage = "A7FF-CORE14S"
        status = "replay_packet_repair_contract_ready_for_core14se"
        next_task = "A7FF-CORE14SE repaired packet construction / bounded replay execution"
    elif a7ffcore14r.get("decision") == "PASS_A7FFCORE14R_FAILURE_ATTRIBUTION_COMPLETE_READY_FOR_CORE14S":
        allowed["A7FF-CORE14S replay-packet/objective repair contract"] = (
            "contract only; repair replay packet/objective based on CORE14R control/cost/split attribution; no replay execution/search/promotion"
        )
        blocked["A7FF-CORE15"] = "blocked: CORE14E replay-clean pool insufficient and CORE14R requires repair contract first"
        blocked["A7FF-CORE14E rerun"] = "blocked until CORE14S defines a concrete repair policy"
        blocked["A7FF large search"] = "blocked: CORE14R shows current replay packet is not search-ready"
        current_stage = "A7FF-CORE14R"
        status = "replay_failure_forensic_ready_for_core14s"
        next_task = "A7FF-CORE14S replay-packet/objective repair contract"
    elif a7ffcore14e.get("decision") == "HOLD_A7FFCORE14E_BOUNDED_REPLAY_INSUFFICIENT":
        allowed["A7FF-CORE14R replay failure forensic"] = (
            "diagnose CORE14E replay collapse by split/control/family; no rerun/search/promotion"
        )
        blocked["A7FF-CORE15"] = "blocked: CORE14E replay-clean pool insufficient"
        blocked["A7FF-CORE14E rerun"] = "blocked until CORE14R identifies a concrete replay policy or pool repair"
        blocked["A7FF large search"] = "blocked: CORE14E hold; replay-clean candidates are too narrow"
        current_stage = "A7FF-CORE14E"
        status = "bounded_replay_hold_insufficient_clean_pool"
        next_task = "A7FF-CORE14R replay failure forensic"
    elif a7ffcore14e.get("decision") == "PASS_A7FFCORE14E_BOUNDED_REPLAY_CLEAN_CANDIDATES_READY_FOR_CORE15":
        allowed["A7FF-CORE15 replay-clean consolidation / search-readiness audit"] = (
            "contract/audit only; consolidate CORE14E clean pool and decide whether any small-search gate is met"
        )
        blocked["A7FF-CORE14E rerun"] = "bounded replay passed; rerun only if packet or replay policy changes"
        blocked["A7FF large search"] = "blocked until CORE15 explicitly passes large-search readiness gates"
        current_stage = "A7FF-CORE14E"
        status = "bounded_replay_clean_candidates_ready_for_core15"
        next_task = "A7FF-CORE15 replay-clean consolidation / search-readiness audit"
    elif a7ffcore14.get("decision") == "PASS_A7FFCORE14_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE14E":
        allowed["A7FF-CORE14E bounded replay execution"] = (
            "execute bounded replay over CORE14 128-candidate packet only; no formula search, large search, promotion, or alpha proof"
        )
        blocked["A7FF-CORE14 rerun"] = "replay-preflight contract passed; rerun only if CORE13E numeric clues or replay packet policy changes"
        blocked["A7FF-CORE13E direct replay"] = "superseded by CORE14 replay-preflight packet"
        blocked["A7FF large search"] = "blocked: CORE14 authorizes bounded replay only, not search"
        current_stage = "A7FF-CORE14"
        status = "replay_preflight_contract_ready_for_core14e"
        next_task = "A7FF-CORE14E bounded replay execution"
    elif a7ffcore13e.get("decision") == "PASS_A7FFCORE13E_NUMERIC_RESPONSE_READY_FOR_CORE14":
        allowed["A7FF-CORE14 replay-preflight contract"] = (
            "contract only; define bounded replay packet from CORE13E numeric clues; no replay execution/search/promotion"
        )
        blocked["A7FF-CORE13E rerun"] = "numeric response passed; rerun only if temp subgraph queue or response policy changes"
        blocked["A7FF-CORE13 direct replay"] = "blocked: CORE13E authorizes replay-preflight contract only"
        blocked["A7FF large search"] = "blocked: CORE13E is numeric response, not search authorization"
        current_stage = "A7FF-CORE13E"
        status = "numeric_response_ready_for_core14"
        next_task = "A7FF-CORE14 replay-preflight contract"
    elif a7ffcore13.get("decision") == "PASS_A7FFCORE13_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE13E":
        allowed["A7FF-CORE13E numeric response execution"] = (
            "execute bounded primary-label numeric response over 416 CORE12E candidates; no replay/search/promotion"
        )
        blocked["A7FF-CORE13 direct replay"] = "blocked until CORE13E numeric response passes"
        blocked["A7FF-CORE12E rerun"] = "materialization preflight consumed by CORE13 contract"
        blocked["A7FF large search"] = "blocked: CORE13 authorizes numeric response only"
        current_stage = "A7FF-CORE13"
        status = "numeric_response_contract_ready_for_core13e"
        next_task = "A7FF-CORE13E numeric response execution"
    elif a7ffcore12e.get("decision") == "PASS_A7FFCORE12E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE13":
        allowed["A7FF-CORE13 numeric response contract"] = (
            "contract only; define primary-label numeric response over CORE12E materialized temp subgraphs; no numeric execution/search/promotion"
        )
        blocked["A7FF-CORE12E rerun"] = "materialization preflight passed; rerun only if blueprint registry or evaluator changes"
        blocked["A7FF-CORE12 direct numeric"] = "blocked: CORE12E authorizes CORE13 contract only"
        blocked["A7FF large search"] = "blocked: CORE12E only authorizes numeric response contract"
        current_stage = "A7FF-CORE12E"
        status = "materialization_preflight_ready_for_core13"
        next_task = "A7FF-CORE13 numeric response contract"
    elif a7ffcore12.get("decision") == "PASS_A7FFCORE12_TEMP_SUBGRAPH_REGISTRY_READY_FOR_CORE12E":
        allowed["A7FF-CORE12E temp-subgraph materialization preflight"] = (
            "materialization/activity preflight for CORE12 temporary subgraphs; no numeric/replay/search/promotion"
        )
        blocked["A7FF-CORE12 direct numeric"] = "blocked until CORE12E materialization preflight passes"
        blocked["A7FF-CORE11E materialization"] = "superseded by CORE12 temp-subgraph registry"
        blocked["A7FF large search"] = "blocked: CORE12 only authorizes materialization preflight"
        current_stage = "A7FF-CORE12"
        status = "temp_subgraph_registry_ready_for_core12e"
        next_task = "A7FF-CORE12E temp-subgraph materialization preflight"
    elif a7ffcore11e.get("decision") == "PASS_A7FFCORE11E_BLUEPRINTS_READY_FOR_CORE12_REGISTRATION":
        allowed["A7FF-CORE12 blueprint subgraph registration / gate audit"] = (
            "register/audit CORE11E blueprints under typed subgraph governance; no materialization/numeric/replay/search promotion"
        )
        blocked["A7FF-CORE11E materialization"] = "blocked: CORE11E outputs blueprints requiring CORE12 registration first"
        blocked["A7FF large search"] = "blocked: CORE11E is small blueprint generation only"
        blocked["A7FF-CORE11 rerun"] = "blueprint generation passed; rerun only if seed pool or grammar changes"
        current_stage = "A7FF-CORE11E"
        status = "blueprints_ready_for_core12_registration"
        next_task = "A7FF-CORE12 blueprint subgraph registration / gate audit"
    elif a7ffcore11.get("decision") == "PASS_A7FFCORE11_SMALL_EXPANSION_CONTRACT_READY_FOR_CORE11E":
        allowed["A7FF-CORE11E small gate-native dry generation"] = (
            "generate 4000 small-expansion formulas from replay-clean seeds under typed AST/subgraph gate; no materialization/numeric/replay/search promotion"
        )
        blocked["A7FF large search"] = "blocked: CORE11 only authorizes small dry generation, not large search"
        blocked["A7FF-CORE11 materialization execution"] = "blocked until CORE11E dry generation produces a valid queue"
        blocked["A7FF-CORE10E rerun"] = "search-readiness audit consumed by CORE11 contract"
        current_stage = "A7FF-CORE11"
        status = "small_expansion_contract_ready_for_core11e"
        next_task = "A7FF-CORE11E small gate-native dry generation"
    elif a7ffcore10e.get("decision") == "PASS_A7FFCORE10E_READY_FOR_CORE11_SMALL_SEARCH_CONTRACT":
        allowed["A7FF-CORE11 small gate-native formula expansion contract"] = (
            "contract only; define small expansion from 23 replay-clean seeds; no execution until contract is written"
        )
        blocked["A7FF large search"] = "blocked: CORE10E large-search gates failed; seed_count < 64 and breadth < large-search minimum"
        blocked["A7FF-CORE10E rerun"] = "search readiness audit passed for small contract; rerun only if clean pool changes"
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE10E gate-native search-readiness path"
        current_stage = "A7FF-CORE10E"
        status = "ready_for_core11_small_search_contract_not_large_search"
        next_task = "A7FF-CORE11 small gate-native formula expansion contract"
    elif a7ffcore9e.get("decision") == "PASS_A7FFCORE9E_BOUNDED_REPLAY_CLEAN_CANDIDATES_READY_FOR_CORE10":
        allowed["A7FF-CORE10 replay-clean consolidation / search-readiness contract"] = (
            "contract only; consolidate CORE9E replay-clean candidates and define search-readiness gates; no formula search or promotion"
        )
        blocked["A7FF-CORE9E rerun"] = "bounded replay passed; rerun only if packet, replay policy, or data changes"
        blocked["A7FF-CORE9 large replay"] = "blocked: CORE9E is bounded replay only and authorizes CORE10 contract"
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE9E gate-native replay path"
        current_stage = "A7FF-CORE9E"
        status = "bounded_replay_clean_candidates_ready_for_core10"
        next_task = "A7FF-CORE10 replay-clean consolidation / search-readiness contract"
    elif a7ffcore9.get("decision") == "PASS_A7FFCORE9_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE9E":
        allowed["A7FF-CORE9E bounded replay execution"] = (
            "bounded replay execution over CORE9 contract packet only; no formula search, large search, promotion, or alpha proof"
        )
        blocked["A7FF-CORE9 large replay"] = "blocked: CORE9 authorizes bounded execution only"
        blocked["A7FF-CORE8 direct replay execution"] = "superseded by CORE9 contract"
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE9 gate-native replay path"
        current_stage = "A7FF-CORE9"
        status = "bounded_replay_contract_ready_for_core9e"
        next_task = "A7FF-CORE9E bounded replay execution"
    elif a7ffcore8e.get("decision") == "PASS_A7FFCORE8E_REPLAY_PREFLIGHT_PACKET_READY_FOR_CORE9_CONTRACT":
        allowed["A7FF-CORE9 bounded replay contract"] = (
            "contract only; define bounded replay protocol for CORE8E packet; no replay execution/search/promotion"
        )
        blocked["A7FF-CORE8 direct replay execution"] = "blocked: CORE8E authorizes CORE9 contract only"
        blocked["A7FF-CORE8E rerun"] = "packet audit passed; rerun only if CORE8 packet or audit policy changes"
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE7/CORE8 gate-native path"
        current_stage = "A7FF-CORE8E"
        status = "replay_preflight_packet_ready_for_core9_contract"
        next_task = "A7FF-CORE9 bounded replay contract"
    elif a7ffcore8.get("decision") == "PASS_A7FFCORE8_NUMERIC_CLUE_CONSOLIDATION_READY_FOR_CORE8E":
        allowed["A7FF-CORE8E replay-preflight packet audit"] = (
            "audit CORE8 candidate packet for expression materialization, label/control coverage, diversity, and replay readiness; no portfolio replay/search/promotion"
        )
        blocked["A7FF-CORE8 direct replay execution"] = "blocked: CORE8 authorizes replay-preflight packet audit only"
        blocked["A7FF-CORE7E rerun"] = "superseded by CORE7ER and CORE8"
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE7/CORE8 gate-native path"
        current_stage = "A7FF-CORE8"
        status = "numeric_clue_consolidation_ready_for_core8e"
        next_task = "A7FF-CORE8E replay-preflight packet audit"
    elif a7ffcore7er.get("decision") == "PASS_A7FFCORE7ER_REPAIRED_NUMERIC_RESPONSE_READY_FOR_CORE8":
        allowed["A7FF-CORE8 numeric clue consolidation / replay-preflight contract"] = (
            "contract only; consolidate CORE7ER repaired numeric clues and define replay-preflight gate; no replay/search/promotion"
        )
        blocked["A7FF-CORE7E rerun"] = "superseded by CORE7ER repaired numeric response"
        blocked["A7FF-CORE7R continuation"] = "control-policy forensic completed; CORE7ER is canonical repaired numeric response"
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE7 gate-native path"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "legacy atlas repair superseded; use CORE7ER repaired gate-native response"
        )
        current_stage = "A7FF-CORE7ER"
        status = "repaired_numeric_response_ready_for_core8"
        next_task = "A7FF-CORE8 numeric clue consolidation / replay-preflight contract"
    elif a7ffcore7r.get("decision") == "PASS_A7FFCORE7R_CONTROL_POLICY_REPAIR_REQUIRED_READY_FOR_CORE7ER":
        allowed["A7FF-CORE7ER repaired numeric-response reclassification"] = (
            "reclassify CORE7E response rows with sign_flip diagnostic-only policy; no replay/search/promotion"
        )
        blocked["A7FF-CORE8 numeric clue consolidation"] = "blocked until CORE7ER writes canonical repaired numeric response"
        blocked["A7FF-CORE7E rerun"] = "blocked: CORE7R identified policy repair path; use CORE7ER reclassification first"
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE7 gate-native path"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "legacy atlas repair superseded; use CORE7R/CORE7ER on gate-native queue instead"
        )
        current_stage = "A7FF-CORE7R"
        status = "control_policy_repair_ready_for_core7er"
        next_task = "A7FF-CORE7ER repaired numeric-response reclassification"
    elif a7ffcore7e.get("decision") == "PASS_A7FFCORE7E_NUMERIC_RESPONSE_READY_FOR_CORE8":
        allowed["A7FF-CORE8 numeric clue consolidation / replay-preflight contract"] = (
            "contract only; consolidate CORE7E numeric clues and define replay-preflight gate; no replay/search/promotion"
        )
        blocked["A7FF-CORE7E rerun"] = "numeric response execution complete; rerun only if queue, labels, controls, or runner changes"
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE7E gate-native numeric path"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = "superseded by CORE7E gate-native numeric path"
        current_stage = "A7FF-CORE7E"
        status = "numeric_response_ready_for_core8"
        next_task = "A7FF-CORE8 numeric clue consolidation / replay-preflight contract"
    elif a7ffcore7e.get("decision") == "HOLD_A7FFCORE7E_NUMERIC_RESPONSE_WEAK":
        allowed["A7FF-CORE7R response repair / label-control forensic"] = (
            "forensic/repair only; inspect no-primary-non-L7 clue result and control dominance before changing generation or selector"
        )
        blocked["A7FF-CORE8 numeric clue consolidation"] = "blocked: CORE7E produced no primary non-L7 numeric clues"
        blocked["A7FF-CORE7E rerun"] = "blocked unless queue, labels, controls, or runner changes"
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE7E gate-native numeric path"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "legacy atlas repair superseded; use CORE7R on gate-native queue instead"
        )
        current_stage = "A7FF-CORE7E"
        status = "numeric_response_hold_weak"
        next_task = "A7FF-CORE7R response repair / label-control forensic"
    elif a7ffcore7.get("decision") == "PASS_A7FFCORE7_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE7E":
        allowed["A7FF-CORE7E gate-native numeric-response execution"] = (
            "bounded numeric-response execution only over CORE6E materialized queue; no replay/search/promotion"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE7E gate-native numeric path"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "superseded by CORE7E path; legacy atlas numeric response remains blocked"
        )
        current_stage = "A7FF-CORE7"
        status = "numeric_response_contract_ready_for_core7e"
        next_task = "A7FF-CORE7E gate-native numeric-response execution"
    elif a7ffcore6e.get("decision") == "PASS_A7FFCORE6E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE7":
        allowed["A7FF-CORE7 gate-native numeric-response contract"] = (
            "contract only; define label/control response run over materialized CORE6E queue; no execution/replay/search/promotion"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "superseded by CORE7 path; legacy numeric execution remains blocked"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "superseded by CORE7 path; gate-native materialization passed, next is numeric-response contract"
        )
        current_stage = "A7FF-CORE6E"
        status = "materialization_preflight_ready_for_core7"
        next_task = "A7FF-CORE7 gate-native numeric-response contract"
    elif a7ffcore6.get("decision") == "PASS_A7FFCORE6_MATERIALIZATION_PREFLIGHT_CONTRACT_READY_FOR_CORE6E":
        allowed["A7FF-CORE6E gate-native materialization preflight execution"] = (
            "materialization/activity preflight only over CORE5 queue shards; no labels, returns, replay, search, or promotion"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "blocked until CORE6E materialization preflight passes and CORE7 numeric-response contract is written"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "superseded by CORE6E path; materialize gate-native queue before any numeric response or atlas repair"
        )
        current_stage = "A7FF-CORE6"
        status = "materialization_preflight_contract_ready_for_core6e"
        next_task = "A7FF-CORE6E gate-native materialization preflight execution"
    elif a7ffcore5.get("decision") == "PASS_A7FFCORE5_GATE_NATIVE_DRYRUN_READY_FOR_CORE6":
        allowed["A7FF-CORE6 gate-native materialization preflight contract"] = (
            "contract/preflight design only; define materialization checks for CORE5 gate-native queue; no numeric/replay/search/promotion"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "blocked until CORE6 materialization preflight and CORE7 numeric contract pass on gate-native queue"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "deprioritized; CORE5 now provides gate-native queue, next work is materialization preflight not legacy atlas repair"
        )
        current_stage = "A7FF-CORE5"
        status = "gate_native_dryrun_ready_for_core6"
        next_task = "A7FF-CORE6 gate-native materialization preflight contract"
    elif a7ffcore4.get("decision") == "PASS_A7FFCORE4_GATE_IMPLEMENTATION_REGRESSION_READY_FOR_CORE5":
        allowed["A7FF-CORE5 gate-native generation compatibility dryrun"] = (
            "dryrun/compatibility only; build a new generator entrypoint that emits CORE4-gated subgraph references; no numeric/replay/search/promotion"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "blocked until CORE5 produces a gate-native generated queue and CORE6 materialization preflight passes"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "deprioritized until CORE5 gate-native generation queue exists; weak numeric response should not drive quarantined legacy generators"
        )
        current_stage = "A7FF-CORE4"
        status = "gate_implementation_regression_ready_for_core5"
        next_task = "A7FF-CORE5 gate-native generation compatibility dryrun"
    elif a7ffcore3.get("decision") == "PASS_A7FFCORE3_FORMULAGEN_SUBGRAPH_GATE_READY_FOR_CORE4":
        allowed["A7FF-CORE4 FormulaGen gate implementation regression"] = (
            "implementation/regression only; wire active generation entrypoints to CORE3 subgraph gate or quarantine bypass scripts; no generation/numeric/replay/search"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "blocked until CORE4 proves generation entrypoints cannot bypass typed subgraph gate"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "deprioritized until CORE4 closes legacy generation bypass risk; weak numeric response should not drive untyped atlas patches"
        )
        current_stage = "A7FF-CORE3"
        status = "formulagen_subgraph_gate_ready_for_core4"
        next_task = "A7FF-CORE4 FormulaGen gate implementation regression"
    elif a7ffcore2.get("decision") == "PASS_A7FFCORE2_FEATURE_SUBGRAPH_REGISTRY_READY_FOR_CORE3":
        allowed["A7FF-CORE3 FormulaGen subgraph gate"] = (
            "governance/gate only; require FormulaGen to consume approved typed subgraphs and reject bypassed raw expressions; no generation/numeric/replay/search"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "blocked until FormulaGen subgraph gate is wired and audited"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "deprioritized until FormulaGen consumes typed subgraph registry; weak numeric response should not drive untyped atlas patches"
        )
        current_stage = "A7FF-CORE2"
        status = "feature_subgraph_registry_ready_for_core3"
        next_task = "A7FF-CORE3 FormulaGen subgraph gate"
    elif a7ffcore1.get("decision") == "PASS_A7FFCORE1_AST_SCHEMA_ADAPTER_READY_FOR_CORE2":
        allowed["A7FF-CORE2 FeatureFactory subgraph registry"] = (
            "registry only; promote parsed AST nodes into reusable feature subgraphs with lineage/PIT/role metadata; no generation/numeric/replay/search"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "blocked until typed subgraph registry and FormulaGen gate are wired"
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "deprioritized until typed subgraph registry is available; weak numeric response should not drive untyped atlas patches"
        )
        current_stage = "A7FF-CORE1"
        status = "ast_schema_adapter_ready_for_core2"
        next_task = "A7FF-CORE2 FeatureFactory subgraph registry"
    elif a7ffcore0.get("decision") == "PASS_A7FFCORE0_TYPED_AST_GOVERNANCE_READY_FOR_CORE1":
        allowed["A7FF-CORE1 AST schema adapter"] = (
            "governance/adapter only; round-trip expression string to typed AST JSON and back; no generation/numeric/replay/search"
        )
        blocked["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "deprioritized until typed AST governance is wired; current issue is generator/feature boundary, not only response forensic"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "blocked: A7FF-CORE0 requires typed AST adapter before expanding repaired atlas"
        current_stage = "A7FF-CORE0"
        status = "typed_ast_governance_ready_for_core1"
        next_task = "A7FF-CORE1 AST schema adapter"
    elif a7ff55r5e.get("decision") == "HOLD_A7FF55R5E_SHARDED_NUMERIC_WEAK_RESPONSE":
        allowed["A7FF-55R6 numeric response forensic / atlas repair"] = (
            "forensic/repair only; inspect weak primary-label response and revise repaired atlas before further numeric expansion"
        )
        blocked["A7FF-55R5F expanded sharded numeric execution"] = "blocked: sampled repaired atlas numeric response is too weak"
        blocked["A7FF-56 replay-preflight contract"] = "blocked: A7FF-55R5E selected queue too small and insufficiently diverse"
        current_stage = "A7FF-55R5E"
        status = "sharded_numeric_weak_response_hold"
        next_task = "A7FF-55R6 numeric response forensic / atlas repair"
    elif a7ff55r5.get("decision") == "PASS_A7FF55R5_REPAIRED_ATLAS_NUMERIC_CONTRACT_READY_FOR_EXECUTION":
        allowed["A7FF-55R5E repaired atlas numeric execution"] = (
            "bounded numeric execution over repaired 2400-row queue; primary labels only; no replay/search/promotion"
        )
        blocked["A7FF-56 replay-preflight contract"] = "blocked until A7FF-55R5E numeric response summary passes"
        current_stage = "A7FF-55R5"
        status = "repaired_atlas_numeric_contract_ready_for_execution"
        next_task = "A7FF-55R5E repaired atlas numeric execution"
    elif a7ff55r4.get("decision") == "PASS_A7FF55R4_REPAIRED_ATLAS_COVERAGE_READY_FOR_NUMERIC_CONTRACT":
        allowed["A7FF-55R5 repaired atlas numeric contract"] = (
            "contract drafting only; define bounded primary-label numeric run over repaired 2400-row queue; no numeric/replay/search execution"
        )
        blocked["A7FF-55R4 direct numeric execution"] = "blocked: coverage audit authorizes numeric contract only, not execution"
        blocked["A7FF-56 replay-preflight contract"] = "blocked until repaired atlas numeric response selector queue passes"
        current_stage = "A7FF-55R4"
        status = "repaired_atlas_coverage_ready_for_numeric_contract"
        next_task = "A7FF-55R5 repaired atlas numeric contract"
    elif a7ff55r3.get("decision") == "PASS_A7FF55R3_REPAIRED_ATLAS_DRY_GENERATION_READY_FOR_COVERAGE_AUDIT":
        allowed["A7FF-55R4 repaired atlas coverage audit"] = (
            "coverage audit only; verify repaired 2400-row queue family/motif/base-field balance before numeric execution"
        )
        blocked["A7FF-55R3 direct numeric execution"] = "blocked: dry generation only authorizes coverage audit, not numeric execution"
        blocked["A7FF-56 replay-preflight contract"] = "blocked until repaired atlas numeric response selector queue passes"
        current_stage = "A7FF-55R3"
        status = "repaired_atlas_dry_generation_ready_for_coverage_audit"
        next_task = "A7FF-55R4 repaired atlas coverage audit"
    elif a7ff55r2.get("decision") == "PASS_A7FF55R2_ATLAS_FIELD_FAMILY_GENERATION_REPAIR_READY_NO_GENERATION_EXEC":
        allowed["A7FF-55R3 repaired atlas dry generation"] = (
            "dry generation only; use repaired open_interest/taker-flow/liquidity seed and pair previews; no numeric/replay/search/promotion"
        )
        blocked["A7FF-55R1 supplemental numeric execution"] = "blocked until repaired atlas dry generation and coverage audit pass"
        blocked["A7FF-56 replay-preflight contract"] = "blocked until repaired atlas numeric response selector queue passes"
        current_stage = "A7FF-55R2"
        status = "atlas_field_family_generation_repair_ready_no_generation_exec"
        next_task = "A7FF-55R3 repaired atlas dry generation"
    elif a7ff55r1.get("decision") == "HOLD_A7FF55R1_SUPPLEMENTAL_QUEUE_ATLAS_COVERAGE_FAIL":
        allowed["A7FF-55R2 atlas field-family generation repair"] = (
            "contract/implementation repair only; add missing open_interest/taker-flow families and materializable liquidity queue before numeric execution"
        )
        blocked["A7FF-55R1 supplemental numeric execution"] = "blocked: current atlas lacks open_interest/taker-flow formulas and liquidity materialization coverage"
        blocked["A7FF-56 replay-preflight contract"] = "blocked: A7FF-55R1 atlas coverage fail"
        current_stage = "A7FF-55R1"
        status = "supplemental_queue_atlas_coverage_fail"
        next_task = "A7FF-55R2 atlas field-family generation repair"
    elif a7ff55r.get("decision") == "PASS_A7FF55R_SELECTOR_FIELD_FAMILY_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH":
        allowed["A7FF-55R1 family-diverse supplemental primary-label input generation"] = (
            "requires explicit heavy execution; over-sample open_interest/positioning/liquidity/volatility/taker-flow primary-label inputs; no replay/search/promotion"
        )
        blocked["A7FF-56 replay-preflight contract"] = "blocked: A7FF-55F selected queue still family/motif/label concentrated"
        blocked["A7FF-55F selected queue replay"] = "blocked: selector dryrun did not pass concentration caps"
        current_stage = "A7FF-55R"
        status = "selector_field_family_repair_contract_ready_no_execution"
        next_task = "A7FF-55R1 family-diverse supplemental primary-label input generation if explicitly authorized"
    elif a7ff55f.get("decision") == "HOLD_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_REPAIR_REQUIRED":
        allowed["A7FF-55R selector / field-family repair contract"] = (
            "contract drafting only; repair family/motif/top-label concentration before any replay preflight"
        )
        blocked["A7FF-56 replay-preflight contract"] = "blocked: A7FF-55F selected queue still family/motif/label concentrated"
        current_stage = "A7FF-55F"
        status = "full_primary_selector_input_hold_repair_required"
        next_task = "A7FF-55R selector / field-family repair contract"
    elif a7ff55f.get("decision") == "PASS_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_READY_NO_REPLAY_AUTH":
        allowed["A7FF-56 replay-preflight contract"] = (
            "contract drafting only; A7FF-55F selected queue passed primary-label and diversity caps; no replay/search/promotion"
        )
        blocked["A7FF-55F direct replay"] = "blocked: A7FF-55F authorizes contract only, not replay execution"
        current_stage = "A7FF-55F"
        status = "full_primary_selector_input_ready_no_replay"
        next_task = "A7FF-56 replay-preflight contract"
    elif a7ff55d.get("decision") == "HOLD_A7FF55D_PARTIAL_SELECTOR_DRYRUN_REQUIRES_FULL_INPUT_REBUILD":
        allowed["A7FF-55F full primary-label input rebuild"] = (
            "requires heavy execution; rebuild S02-S06 primary-label compact inputs with shard outputs; no replay/search/promotion"
        )
        blocked["A7FF-55D replay preflight"] = "blocked: partial dryrun still family/motif concentrated and is not full-scope"
        current_stage = "A7FF-55D"
        status = "partial_selector_dryrun_hold_full_input_rebuild_required"
        next_task = "A7FF-55F full primary-label input rebuild"
    elif a7ff55.get("decision") == "PASS_A7FF55_SELECTOR_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH":
        allowed["A7FF-55D selector input rebuild / dryrun option"] = (
            "requires explicit execution; rebuild primary-label response compact and dryrun selector repair; no replay/search/promotion"
        )
        blocked["A7FF-54 selected queue replay"] = "blocked by A7FF-55: no L0/L1/L3 selected rows and L5/L7 absorption"
        current_stage = "A7FF-55"
        status = "selector_repair_contract_ready_no_execution"
        next_task = "A7FF-55D selector input rebuild / dryrun if explicitly authorized"
    elif a7ff54.get("decision") == "HOLD_A7FF54_SELECTED_QUEUE_LABEL_REPAIR_REQUIRED_NO_REPLAY_AUTH":
        allowed["A7FF-55 selector repair contract"] = (
            "contract drafting only; require L0/L1/L3 representation and motif caps before any replay preflight"
        )
        blocked["A7FF-54 replay preflight"] = "blocked: selected queue has no L0/L1/L3 rows and non-L7 rows are L5-only"
        current_stage = "A7FF-54"
        status = "hold_selector_label_repair_required"
        next_task = "A7FF-55 selector repair contract"
    elif a7ff53e.get("decision") == "PASS_A7FF53E_NUMERIC_RESPONSE_SHARD_SUMMARY_READY_NO_SEARCH_AUTH":
        allowed["A7FF-54 numeric clue consolidation contract"] = (
            "contract drafting only; consolidate 186 non-L7 clues and 148 selected queue rows; no replay/search/promotion"
        )
        blocked["A7FF-53E rerun"] = "numeric response summary complete; rerun only if queue or runner changes"
        current_stage = "A7FF-53E"
        status = "numeric_response_summary_pass_no_search"
        next_task = "A7FF-54 clue consolidation contract"
    elif a7ff53e_s00.get("decision") == "PASS_A7FF53ES00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH":
        allowed["A7FF-53E remaining shard execution option"] = (
            "requires explicit heavy-task authorization; continue bounded numeric response shards or optimize runner; no replay/search/promotion"
        )
        blocked["A7FF-53E full one-shot execution"] = "current runner timed out on 1200-row one-shot; use shard execution or optimize before full run"
        current_stage = "A7FF-53E-S00"
        status = "first_numeric_shard_pass_no_search"
        next_task = "A7FF-53E remaining shards or runner optimization"
    elif a7ff53.get("decision") == "PASS_A7FF53_NUMERIC_RESPONSE_CONTRACT_READY_NO_EXECUTION_AUTH":
        allowed["A7FF-53E numeric response execution option"] = (
            "requires explicit authorization; bounded numeric response only; no replay/search/promotion"
        )
        blocked["A7FF-53 execution"] = "contract ready but numeric response execution is not started"
        blocked["A7FF-52E rerun"] = "already executed; rerun only if A7FF-51E pool or evaluator changes"
        current_stage = "A7FF-53"
        status = "numeric_response_contract_ready_no_execution"
        next_task = "A7FF-53E if explicitly authorized"
    elif a7ff52e.get("decision") == "PASS_A7FF52E_MATERIALIZATION_PREFLIGHT_READY_FOR_NUMERIC_CONTRACT":
        allowed["A7FF-53 numeric response contract"] = (
            "contract drafting only; use A7FF-52E materialization metrics; no numeric execution/search"
        )
        blocked["A7FF-52E rerun"] = "already executed; rerun only if A7FF-51E pool or evaluator changes"
        current_stage = "A7FF-52E"
        status = "materialization_preflight_pass_no_numeric"
        next_task = "A7FF-53 numeric response contract"
    else:
        allowed["A7FF-52E materialization preflight execution option"] = (
            "requires explicit authorization; 1200 family-balanced rows; no numeric replay/search"
        )
        blocked["A7FF-52E execution"] = (
            "pending explicit materialization-preflight authorization; A7FF-52 contract is ready but materialization is not started"
        )
        current_stage = "A7FF-52"
        status = "contract_ready_no_materialization"
        next_task = "A7FF-52E if explicitly authorized"
    active = pd.DataFrame(
        [
            {"workstream": "governance", "current_stage": "A7PM-0/1/2/3", "status": "pass", "next": "keep registry as source-of-truth"},
            {"workstream": "a7ff_family_diversification", "current_stage": current_stage, "status": status, "next": next_task},
            {"workstream": "a7ff_funding_tail", "current_stage": "A7FF-24R4", "status": "contract_ready_no_execution", "next": "A7FF-24R4E if explicitly authorized"},
            {"workstream": "search_execution", "current_stage": "blocked", "status": "not_authorized", "next": "none"},
        ]
    )
    return allowed, blocked, active


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    pm0 = read_json(A7PM0)
    pm2 = read_json(A7PM2)
    if not pm0.get("authorizes_a7pm3") and not pm2.get("authorizes_a7pm3"):
        raise SystemExit("A7PM source stages do not authorize A7PM-3")

    allowed, blocked, active = board_state()
    manifest = {
        "stage": "A7PM-3",
        "generated_at": now_utc(),
        "decision": "PASS_A7PM3_CURRENT_EXPERIMENT_BOARD_BUILT",
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "allowed_next_task_count": len(allowed),
        "blocked_task_count": len(blocked),
    }
    write_json(RUNTIME / "a7pm3_allowed_next_tasks.json", allowed)
    write_json(RUNTIME / "a7pm3_blocked_tasks.json", blocked)
    active.to_csv(RUNTIME / "a7pm3_active_workstreams.csv", index=False)
    write_json(
        RUNTIME / "a7pm3_latest_source_of_truth.json",
        {"a7pm0": pm0, "a7pm2": pm2, "head_equals_origin_main": pm0.get("head_equals_origin_main")},
    )
    write_json(RUNTIME / "a7pm3_manifest.json", manifest)
    allowed_df = pd.DataFrame([{"task": k, "reason": v} for k, v in allowed.items()])
    blocked_df = pd.DataFrame([{"task": k, "reason": v} for k, v in blocked.items()])
    lines = [
        "# CRYPTO A7PM-3 CURRENT EXPERIMENT BOARD",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## Active Workstreams",
        "",
        md_table(active),
        "",
        "## Allowed Next Tasks",
        "",
        md_table(allowed_df),
        "",
        "## Blocked Tasks",
        "",
        md_table(blocked_df),
        "",
        "## Boundary",
        "",
        "```text",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "A7FF-52E materialization is complete if present in the source-of-truth registry. Next A7FF step is contract-only unless explicitly authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
