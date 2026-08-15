"""Dispatcher-backed proposal supply for the frozen P1 generation-2 catalog."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Mapping, Sequence

from . import search_engine_v1 as engine
from .compositional18m import CandidateSpec, MechanismSpec
from .temporal_p1_semantic_expansion_v1 import (
    P1,
    P1Generation2ProgramSpec,
    p1_generation2_candidate_from_genes,
    sample_p1_generation2_candidate,
)
from .temporal_program_v1 import TemporalProgramSpec
from .temporal_proposal_dispatch_v1 import (
    POOL_CAP,
    _feature_vector,
    _score,
    _sha,
    _state,
    _weighted_index,
    dispatcher_state_hash,
    select_mutation_target_v1,
)
from .temporal_realization_v2 import targeted_members, targeted_parent_record


ROUTE = "P1_G2_FACTORIZED_COMPLETION"
RECEIPT_SCHEMA = "P1_SEMANTIC_SUPPLY_EXPANSION_RECEIPT_V1"


def _catalog_maps(
    catalog: Sequence[tuple[MechanismSpec, P1Generation2ProgramSpec]],
) -> tuple[
    dict[str, list[tuple[MechanismSpec, P1Generation2ProgramSpec]]], str
]:
    grouped: dict[str, list[tuple[MechanismSpec, P1Generation2ProgramSpec]]] = {}
    rows = []
    for mechanism, program in catalog:
        grouped.setdefault(program.parent_program_id, []).append((mechanism, program))
        rows.append({"mechanism_spec": mechanism.to_dict(), "program_spec": program.to_dict()})
    for values in grouped.values():
        values.sort(key=lambda row: row[1].program_id)
    return grouped, _sha(sorted(rows, key=lambda row: row["program_spec"]["program_id"]))


def _p1_parent(
    policy: engine.MechanismEvolutionV2,
    accepted_parent_ids: set[str],
) -> tuple[str, CandidateSpec]:
    state = _state(policy)
    basins = sorted(
        str(row["economic_similarity_cluster_id"])
        for row in policy.targeted_parent_pool_payload["target_basins"]
        if str(row["program_family_id"]) == P1
    )
    if not basins:
        raise RuntimeError("P1 G2 has no frozen P1 basin")
    cursor = int(state.get("p1_g2_basin_cursor", 0))
    for offset in range(len(basins)):
        basin_id = basins[(cursor + offset) % len(basins)]
        candidates = []
        for candidate_id in targeted_members(policy, basin_id):
            record = targeted_parent_record(policy, candidate_id)
            if not record:
                continue
            candidate = policy._candidate(record)
            if str(candidate.generation_genes.get("program_id")) in accepted_parent_ids:
                candidates.append(candidate)
        if candidates:
            candidates.sort(key=lambda candidate: candidate.candidate_id)
            parent_cursor_key = "p1_g2_parent_cursor:" + basin_id
            parent_cursor = int(state.get(parent_cursor_key, 0))
            state[parent_cursor_key] = parent_cursor + 1
            state["p1_g2_basin_cursor"] = cursor + offset + 1
            return basin_id, candidates[parent_cursor % len(candidates)]
    raise RuntimeError("P1 G2 selected parent programs are absent from frozen P1 basins")


def _receipt(
    *,
    policy: engine.MechanismEvolutionV2,
    parents: Sequence[CandidateSpec],
    child: CandidateSpec,
    catalog_sha256: str,
    details: Mapping[str, Any],
) -> dict[str, Any]:
    core = {
        "schema_version": RECEIPT_SCHEMA,
        "operation": engine.MECHANISM_EVOLUTION_OPERATIONS[
            2 if len(parents) == 2 else 1
        ],
        "parent_ids": [parent.candidate_id for parent in parents],
        "parent_program_ids": [
            str(parent.generation_genes["program_id"]) for parent in parents
        ],
        "child_id": child.candidate_id,
        "child_program_id": str(child.generation_genes["program_id"]),
        "child_mechanism_id": str(child.generation_genes["mechanism_id"]),
        "parent_expression_sha256": [
            engine._payload_sha(parent.expression.canonical_dict()) for parent in parents
        ],
        "child_expression_sha256": engine._payload_sha(
            child.expression.canonical_dict()
        ),
        "child_control_sha256": engine._payload_sha(child.control.canonical_dict()),
        "child_genome_sha256": engine._payload_sha(child.generation_genes),
        "p1_g2_catalog_sha256": catalog_sha256,
        **dict(details),
    }
    return {**core, "receipt_sha256": engine._payload_sha(core)}


def verify_p1_generation2_receipt(
    registry: Any,
    parents: Sequence[CandidateSpec],
    child: CandidateSpec,
    receipt: Mapping[str, Any],
    *,
    catalog_sha256: str,
    legal_program_ids: set[str],
) -> bool:
    try:
        core = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        rebuilt = p1_generation2_candidate_from_genes(
            registry, genes=child.generation_genes
        )
        return bool(
            receipt.get("schema_version") == RECEIPT_SCHEMA
            and receipt.get("receipt_sha256") == engine._payload_sha(core)
            and receipt.get("p1_g2_catalog_sha256") == catalog_sha256
            and list(receipt.get("parent_ids") or ())
            == [parent.candidate_id for parent in parents]
            and list(receipt.get("parent_program_ids") or ())
            == [str(parent.generation_genes["program_id"]) for parent in parents]
            and receipt.get("child_id") == child.candidate_id
            and str(child.generation_genes["program_id"]) in legal_program_ids
            and str(child.generation_genes["parent_program_id"])
            == str(parents[0].generation_genes["program_id"])
            and rebuilt.candidate_id == child.candidate_id
            and rebuilt.expression.expression_id == child.expression.expression_id
            and rebuilt.control.expression_id == child.control.expression_id
        )
    except (KeyError, TypeError, ValueError):
        return False


def _proposal_pool(
    policy: engine.MechanismEvolutionV2,
    *,
    parent: CandidateSpec,
    catalog: Sequence[tuple[MechanismSpec, P1Generation2ProgramSpec]],
    scale_contract: Mapping[str, Any],
    catalog_sha256: str,
    mutation_target: str,
) -> list[dict[str, Any]]:
    parent_program = TemporalProgramSpec.from_dict(
        dict(parent.generation_genes["program_spec"])
    )
    values = [row for row in catalog if row[1].parent_program_id == parent_program.program_id]
    state = _state(policy)
    offset = int(state["dispatch_counters"]["dispatches"])
    values.sort(
        key=lambda row: _sha(
            {"seed": policy.seed, "offset": offset, "program_id": row[1].program_id}
        )
    )
    output = []
    for mechanism, program in values[:12]:
        variants: list[tuple[CandidateSpec, str, list[str]]] = []
        try:
            variants.append(
                (
                    sample_p1_generation2_candidate(
                        registry=policy.registry,
                        mechanism=mechanism,
                        program=program,
                        parent=parent,
                        parent_program=parent_program,
                        scale_contract=scale_contract,
                        rng=policy.rng,
                        domains=policy.domains,
                    ),
                    "factorized_condition_completion",
                    ["condition_binding", "condition_normalization", "condition_temporal_parameter"],
                )
            )
        except ValueError:
            pass
        if len(output) < 8:
            try:
                mutated, legacy_receipt = policy._mutate_parameters(
                    parent, target_dimension=mutation_target
                )
                variants.append(
                    (
                        sample_p1_generation2_candidate(
                            registry=policy.registry,
                            mechanism=mechanism,
                            program=program,
                            parent=mutated,
                            parent_program=parent_program,
                            scale_contract=scale_contract,
                            rng=policy.rng,
                            domains=policy.domains,
                        ),
                        "dimension_aware_payload_plus_condition_completion",
                        [
                            *[
                                "+".join(group)
                                for group in legacy_receipt.get("changed_gene_groups", ())
                            ],
                            "condition_binding",
                            "condition_temporal_parameter",
                        ],
                    )
                )
            except (ValueError, RuntimeError):
                pass
        for child, completion_route, changed in variants:
            details = {
                "requested_operation": "p1_g2_semantic_completion",
                "realized_operation": "p1_g2_semantic_completion",
                "construction_route": completion_route,
                "semantic_edit_type": "p1_g2_condition",
                "mutation_target": mutation_target,
                "changed_gene_groups": [[value] for value in changed],
                "semantic_generation": 2,
                "parent_p1_program_id": parent_program.program_id,
                "condition_role": program.condition_role,
                "condition_primitive": program.condition_component,
                "condition_operator": program.condition_operator,
                "condition_mode": program.condition_mode,
                "repair_size": 0,
                "completion_failure_count": 0,
                "legal_child_count": 1,
            }
            output.append(
                {
                    "candidate": child,
                    "parents": (parent,),
                    "receipt": _receipt(
                        policy=policy,
                        parents=(parent,),
                        child=child,
                        catalog_sha256=catalog_sha256,
                        details=details,
                    ),
                    "route": ROUTE,
                    "details": details,
                }
            )
    return output


def propose_p1_generation2_with_dispatcher(
    policy: engine.MechanismEvolutionV2,
    *,
    catalog: Sequence[tuple[MechanismSpec, P1Generation2ProgramSpec]],
    scale_contract: Mapping[str, Any],
) -> tuple[CandidateSpec, dict[str, Any]]:
    grouped, catalog_sha256 = _catalog_maps(catalog)
    legal_program_ids = {program.program_id for _, program in catalog}
    state = _state(policy)
    state_hash_before = policy.state_hash()
    dispatch_state_hash_before = dispatcher_state_hash(policy)
    limit = int(policy.parameters.get("duplicate_resample_limit", 64))
    for duplicate_attempt in range(1, limit + 2):
        basin_id, parent = _p1_parent(policy, set(grouped))
        target = select_mutation_target_v1(policy, basin_id)
        pool = _proposal_pool(
            policy,
            parent=parent,
            catalog=catalog,
            scale_contract=scale_contract,
            catalog_sha256=catalog_sha256,
            mutation_target=target,
        )
        unique = {
            item["candidate"].candidate_id: item
            for item in pool
            if item["candidate"].candidate_id not in policy.seen
        }
        candidates = list(unique.values())[:POOL_CAP]
        if not candidates:
            continue
        scoring_model_state_hash = _sha(
            {
                "configuration_sha256": state["configuration_sha256"],
                "online_tables": state["online_tables"],
                "selection_counts": state["selection_counts"],
            }
        )
        scored = []
        for item in candidates:
            features = _feature_vector(
                policy,
                candidate=item["candidate"],
                parents=item["parents"],
                basin_id=basin_id,
                route=item["route"],
                details=item["details"],
                pool_size=len(candidates),
            )
            scored.append({**item, "features": features, "score": _score(state, features)})
        ranked = sorted(
            scored,
            key=lambda item: (-float(item["score"]["total"]), item["candidate"].candidate_id),
        )
        explore = policy.rng.random() < float(state["exploration_probability"])
        top_count = max(1, math.ceil(len(ranked) * float(state["top_region_fraction"])))
        if explore and len(ranked) > top_count:
            eligible = ranked[top_count:]
        else:
            explore = False
            eligible = ranked[:top_count]
        selected = eligible[_weighted_index(policy, [float(item["score"]["total"]) for item in eligible])]
        rank = ranked.index(selected) + 1
        child = selected["candidate"]
        receipt = policy._bind_targeted_receipt(
            selected["receipt"], basin_id=basin_id, parents=selected["parents"]
        )
        if not verify_p1_generation2_receipt(
            policy.registry,
            selected["parents"],
            child,
            receipt,
            catalog_sha256=catalog_sha256,
            legal_program_ids=legal_program_ids,
        ):
            raise RuntimeError("P1 G2 dispatch receipt failed verification")
        policy.seen.add(child.candidate_id)
        policy.step += 1
        counters = Counter(state["dispatch_counters"])
        counters.update(
            {
                "dispatches": 1,
                "legal_generated": len(unique),
                "legal_scored": len(ranked),
                "exploration_selected" if explore else "exploitation_selected": 1,
                "pool_under_eight": int(len(ranked) < 8),
            }
        )
        state["dispatch_counters"] = dict(sorted(counters.items()))
        for field, value in (
            ("pool_size_counts", str(len(ranked))),
            ("selected_rank_counts", str(rank)),
            ("source_selected", ROUTE),
            ("edit_selected", selected["features"]["semantic_edit_type"]),
            ("target_selected", selected["features"]["mutation_target"]),
        ):
            counter = Counter(state[field]); counter[str(value)] += 1; state[field] = dict(sorted(counter.items()))
        for item in ranked:
            for field, value in (
                ("source_generated", ROUTE),
                ("edit_generated", item["features"]["semantic_edit_type"]),
                ("target_generated", item["features"]["mutation_target"]),
            ):
                counter = Counter(state[field]); counter[str(value)] += 1; state[field] = dict(sorted(counter.items()))
        selection = Counter(state["selection_counts"])
        for key in (
            "edit:" + selected["features"]["semantic_edit_type"],
            "program:" + selected["features"]["program_id"],
            "operator:" + child.operator_path,
            "field:" + selected["features"]["field_signature"],
        ):
            selection[key] += 1
        state["selection_counts"] = dict(sorted(selection.items()))
        scores = [float(item["score"]["total"]) for item in ranked]
        dispatch_receipt = {
            "schema_version": 1,
            "dispatcher_id": state["dispatcher_id"],
            "historical_prior_sha256": state["historical_prior_sha256"],
            "p1_g2_source_gap_sha256": state["p1_g2_source_gap_sha256"],
            "p1_g2_catalog_sha256": catalog_sha256,
            "dispatcher_state_hash_before": dispatch_state_hash_before,
            "candidate_feature_hash": _sha(selected["features"]),
            "candidate_features": selected["features"],
            "score_components": selected["score"],
            "scoring_model_state_hash": scoring_model_state_hash,
            "legal_candidates_generated": len(unique),
            "legal_candidates_scored": len(ranked),
            "pool_score_minimum": min(scores),
            "pool_score_median": sorted(scores)[len(scores) // 2],
            "pool_score_maximum": max(scores),
            "selected_score": float(selected["score"]["total"]),
            "selected_rank": rank,
            "selected_score_decile": min(9, int((rank - 1) * 10 / len(ranked))),
            "exploration_selected": explore,
            "construction_route": ROUTE,
        }
        dispatch_receipt["dispatch_receipt_sha256"] = _sha(dispatch_receipt)
        return child, {
            "policy_state_hash_before": state_hash_before,
            "operation": str(receipt["operation"]),
            "parent_ids": [parent.candidate_id],
            "receipt": receipt,
            "receipt_verified": True,
            "raw_attempts": duplicate_attempt + len(unique),
            "compile_valid_attempts": len(unique),
            "targeted_economic_basin_id": basin_id,
            "targeted_parent_pool_sha256": str(policy.targeted_parent_pool_payload["target_parent_pool_sha256"]),
            "dispatch_receipt": dispatch_receipt,
        }
    raise engine._ProposalGenerationFailure("P1 G2 legal pool exhausted", raw_attempts=limit + 1)


__all__ = ["propose_p1_generation2_with_dispatcher", "verify_p1_generation2_receipt"]
