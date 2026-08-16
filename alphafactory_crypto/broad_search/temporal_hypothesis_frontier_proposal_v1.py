"""TEMPORAL_PROPOSAL_DISPATCHER_V1 supply for frozen P5/P6 programs."""

from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any, Mapping, Sequence

from . import search_engine_v1 as engine
from .compositional18m import CandidateSpec, MechanismSpec
from .temporal_hypothesis_frontier_v1 import (
    FrontierProgramSpec,
    rebuild_frontier_candidate,
    sample_frontier_candidate,
)
from .temporal_proposal_dispatch_v1 import (
    POOL_CAP,
    _score,
    _sha,
    _state,
    _weighted_index,
    dispatcher_state_hash,
)


ROUTE = "TEMPORAL_HYPOTHESIS_FRONTIER_CATALOG_SAMPLE"


def _features(
    policy: engine.MechanismEvolutionV2,
    *, candidate: CandidateSpec, program: FrontierProgramSpec,
    pool_size: int,
) -> dict[str, Any]:
    state = _state(policy)
    genes = candidate.generation_genes
    field_signature = "+".join(sorted(set(candidate.field_families)))
    raw_field_signature = "+".join(sorted(candidate.raw_fields))
    normalizers = sorted(str(value) for key, value in genes.items() if "normalizer" in key)
    scales = sorted(
        f"{key}={value}" for key, value in genes.items()
        if any(token in key for token in ("window", "threshold", "horizon", "beta"))
    )
    edit_type = "condition_structure" if program.condition_role else (
        "temporal_primitive" if program.temporal_primitive else "frontier_relation"
    )
    basin = "FRONTIER_DISCOVERY:" + program.family_id
    return {
        "program_family_id": program.family_id,
        "semantic_motif": program.motif_id,
        "parent_template_id": program.parent_template_id,
        "semantic_generation": program.semantic_generation,
        "parent_p1_program_id": program.program_id,
        "payload_identity": program.program_id,
        "condition_role": program.condition_role or "NONE",
        "condition_primitive": "NONE",
        "condition_operator": program.condition_operator or "NONE",
        "condition_mode": program.condition_mode or "NONE",
        "temporal_primitive": program.temporal_primitive or "NONE",
        "temporal_axis": program.temporal_axis or "NONE",
        "semantic_novelty": True,
        "economic_basin_id": basin,
        "parent_quality": 0.0,
        "parent_matched_positive": False,
        "parent_realization_cell": "FRONTIER",
        "parent_lineage_depth": 0,
        "parent_source": "FROZEN_FRONTIER_CATALOG",
        "basin_occupancy": 0,
        "basin_hq_depth": 0,
        "rare_realization_cell": True,
        "missing_dimensions": ["mapped_weight", "turnover", "raw_field", "asset_selection"],
        "requested_operation": "frontier_catalog_sample",
        "construction_route": ROUTE,
        "semantic_edit_type": edit_type,
        "changed_gene_groups": [],
        "normalization_changed": False,
        "binding_changed": True,
        "temporal_parameter_changed": bool(program.temporal_primitive),
        "role_changed": True,
        "component_changed": bool(program.temporal_primitive),
        "operator_changed": True,
        "repair_size": 0,
        "completion_failure_count": 0,
        "legal_child_pool_size": pool_size,
        "mutation_target": "frontier_supply",
        "program_id": program.program_id,
        "operator_path": candidate.operator_path,
        "field_signature": field_signature,
        "raw_field_signature": raw_field_signature,
        "normalizer_signature": "+".join(normalizers),
        "scale_signature": "+".join(scales),
        "candidate_complexity": len(json.dumps(candidate.expression.canonical_dict(), sort_keys=True)),
        "candidate_unseen": candidate.candidate_id not in policy.seen,
        "representation_distance_from_parent": 1,
        "selected_count_edit": int(dict(state["selection_counts"]).get("edit:" + edit_type, 0)),
        "selected_count_program": int(dict(state["selection_counts"]).get("program:" + program.program_id, 0)),
        "selected_count_operator": int(dict(state["selection_counts"]).get("operator:" + candidate.operator_path, 0)),
        "selected_count_field": int(dict(state["selection_counts"]).get("field:" + field_signature, 0)),
    }


def _receipt(
    candidate: CandidateSpec, program: FrontierProgramSpec, catalog_sha256: str
) -> dict[str, Any]:
    core = {
        "schema_version": "TEMPORAL_HYPOTHESIS_FRONTIER_PROPOSAL_V1",
        "operation": "FRONTIER_CATALOG_SAMPLE",
        "parent_ids": [],
        "child_id": candidate.candidate_id,
        "child_program_id": program.program_id,
        "child_mechanism_id": candidate.generation_genes["mechanism_id"],
        "child_expression_sha256": engine._payload_sha(candidate.expression.canonical_dict()),
        "child_control_sha256": engine._payload_sha(candidate.control.canonical_dict()),
        "child_genome_sha256": engine._payload_sha(candidate.generation_genes),
        "frontier_catalog_sha256": catalog_sha256,
    }
    return {**core, "receipt_sha256": engine._payload_sha(core)}


def propose_frontier_with_dispatcher_v1(
    policy: engine.MechanismEvolutionV2,
    *, catalog: Sequence[tuple[MechanismSpec, FrontierProgramSpec]],
    family_id: str, catalog_sha256: str,
) -> tuple[CandidateSpec, dict[str, Any]]:
    legal = [(mechanism, program) for mechanism, program in catalog if program.family_id == family_id]
    if not legal:
        raise ValueError("frontier dispatcher family lane is empty")
    state = _state(policy)
    state_hash_before = policy.state_hash()
    dispatch_state_hash_before = dispatcher_state_hash(policy)
    limit = int(policy.parameters.get("duplicate_resample_limit", 64))
    attempts = 0
    for _ in range(limit + 1):
        offset = int(state["dispatch_counters"]["dispatches"])
        ordered = sorted(legal, key=lambda row: _sha({
            "seed": policy.seed, "offset": offset, "program_id": row[1].program_id,
        }))
        pool: dict[str, tuple[CandidateSpec, FrontierProgramSpec]] = {}
        for mechanism, program in ordered[:16]:
            attempts += 1
            try:
                candidate = sample_frontier_candidate(
                    registry=policy.registry, mechanism=mechanism, program=program,
                    rng=policy.rng, domains=policy.domains,
                )
            except ValueError:
                continue
            if candidate.candidate_id not in policy.seen:
                pool[candidate.candidate_id] = (candidate, program)
        if not pool:
            continue
        scored = []
        for candidate, program in list(pool.values())[:POOL_CAP]:
            features = _features(policy, candidate=candidate, program=program, pool_size=len(pool))
            scored.append({"candidate": candidate, "program": program, "features": features, "score": _score(state, features)})
        ranked = sorted(scored, key=lambda row: (-float(row["score"]["total"]), row["candidate"].candidate_id))
        explore = policy.rng.random() < float(state["exploration_probability"])
        top_count = max(1, math.ceil(len(ranked) * float(state["top_region_fraction"])))
        if explore and len(ranked) > top_count:
            eligible = ranked[top_count:]
        else:
            explore = False
            eligible = ranked[:top_count]
        selected = eligible[_weighted_index(policy, [float(row["score"]["total"]) for row in eligible])]
        candidate, program = selected["candidate"], selected["program"]
        rebuilt = rebuild_frontier_candidate(policy.registry, candidate, policy.domains)
        if rebuilt.candidate_id != candidate.candidate_id:
            raise RuntimeError("frontier proposal replay failed")
        receipt = _receipt(candidate, program, catalog_sha256)
        policy.seen.add(candidate.candidate_id)
        policy.step += 1
        counters = Counter(state["dispatch_counters"])
        counters.update({
            "dispatches": 1, "legal_generated": len(pool), "legal_scored": len(ranked),
            "exploration_selected" if explore else "exploitation_selected": 1,
            "pool_under_eight": int(len(ranked) < 8),
        })
        state["dispatch_counters"] = dict(sorted(counters.items()))
        for field, value in (
            ("pool_size_counts", str(len(ranked))),
            ("selected_rank_counts", str(ranked.index(selected) + 1)),
            ("source_selected", ROUTE),
            ("edit_selected", selected["features"]["semantic_edit_type"]),
            ("target_selected", "frontier_supply"),
        ):
            counter = Counter(state[field]); counter[str(value)] += 1; state[field] = dict(sorted(counter.items()))
        for row in ranked:
            for field, value in (
                ("source_generated", ROUTE),
                ("edit_generated", row["features"]["semantic_edit_type"]),
                ("target_generated", "frontier_supply"),
            ):
                counter = Counter(state[field]); counter[str(value)] += 1; state[field] = dict(sorted(counter.items()))
        selection = Counter(state["selection_counts"])
        for key in (
            "edit:" + selected["features"]["semantic_edit_type"],
            "program:" + program.program_id,
            "operator:" + candidate.operator_path,
            "field:" + selected["features"]["field_signature"],
        ):
            selection[key] += 1
        state["selection_counts"] = dict(sorted(selection.items()))
        scores = sorted(float(row["score"]["total"]) for row in ranked)
        dispatch = {
            "schema_version": 1,
            "dispatcher_id": state["dispatcher_id"],
            "historical_prior_sha256": state["historical_prior_sha256"],
            "frontier_source_gap_sha256": state["frontier_source_gap_sha256"],
            "frontier_catalog_sha256": catalog_sha256,
            "dispatcher_state_hash_before": dispatch_state_hash_before,
            "candidate_feature_hash": _sha(selected["features"]),
            "candidate_features": selected["features"],
            "score_components": selected["score"],
            "legal_candidates_generated": len(pool),
            "legal_candidates_scored": len(ranked),
            "pool_score_minimum": scores[0], "pool_score_median": scores[len(scores)//2],
            "pool_score_maximum": scores[-1], "selected_score": float(selected["score"]["total"]),
            "selected_rank": ranked.index(selected) + 1,
            "selected_score_decile": min(9, int(ranked.index(selected) * 10 / len(ranked))),
            "exploration_selected": explore,
            "construction_route": ROUTE,
        }
        dispatch["dispatch_receipt_sha256"] = _sha(dispatch)
        return candidate, {
            "policy_state_hash_before": state_hash_before,
            "operation": "FRONTIER_CATALOG_SAMPLE", "parent_ids": [],
            "receipt": receipt, "receipt_verified": True,
            "raw_attempts": attempts, "compile_valid_attempts": len(pool),
            "targeted_economic_basin_id": "FRONTIER_DISCOVERY:" + family_id,
            "dispatch_receipt": dispatch,
        }
    raise engine._ProposalGenerationFailure("frontier legal pool exhausted", raw_attempts=attempts)


__all__ = ["propose_frontier_with_dispatcher_v1"]
