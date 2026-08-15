"""Train-only proposal scoring between legal construction and strict evaluation.

The dispatcher owns proposal choice only.  It reuses the frozen targeted basin/QD
state, existing candidate builders and the strict evaluator without changing any
economic authority.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import Counter
from typing import Any, Mapping, Sequence

from . import search_engine_v1 as engine
from .compositional18m import CandidateSpec
from .temporal_realization_v2 import (
    constructive_crossover_children,
    next_targeted_basin,
    next_targeted_parent,
    targeted_members,
    targeted_parent_record,
)
from .temporal_representation_successor_v1 import (
    ACTIVE_FAMILIES,
    SEMANTIC_BLOCKS,
    TemporalRepresentationInventory,
    _successor_second_parent,
    representation_successor_children,
    representation_successor_receipt,
    semantic_block_mutation,
    semantic_mechanism_donor_mutation,
    verify_successor_receipt,
)


DISPATCHER_ID = "TEMPORAL_PROPOSAL_DISPATCHER_V1"
STATE_KEY = "proposal_dispatcher_v1"
POOL_CAP = 24
SOURCE_CAP = 6
EXPLORATION_PROBABILITY = 0.15
TOP_REGION_FRACTION = 0.25
SMOOTHING_STRENGTH = 20.0
TARGETS = ("mapped_weight", "turnover", "raw_field", "asset_selection", "generic")
OUTCOMES = (
    "matched_positive",
    "basin_retained",
    "new_realization",
    "new_hq_realization",
    "positive_reward",
)
OUTCOME_WEIGHTS = {
    "matched_positive": 0.35,
    "basin_retained": 0.20,
    "new_realization": 0.15,
    "new_hq_realization": 0.25,
    "positive_reward": 0.05,
}
HISTORICAL_SAFE_FIELDS = frozenset(
    {
        "candidate_id",
        "program_family_id",
        "targeted_economic_basin_id",
        "requested_operation",
        "realized_operation",
        "operation",
        "semantic_edit_type",
        "mutation_target",
        "operator_path",
        "field_families_json",
        "raw_fields_json",
        "mapped_weight_descriptor_id",
        "turnover_path_descriptor_id",
        "selected_asset_overlap_id",
        "matched_positive",
        "search_reward",
        "representation_tournament_arm",
        "operation_receipt_json",
        "receipt_json",
    }
)
FEATURE_GROUP_WEIGHTS = {
    "family": 0.15,
    "basin": 0.15,
    "edit_type": 0.25,
    "mutation_target": 0.15,
    "operator_path": 0.10,
    "field_signature": 0.10,
    "construction_route": 0.10,
}
POSITIVE_EDIT_PRIOR = {
    "normalization": 0.16,
    "binding": 0.14,
    "temporal_parameter": 0.10,
    "binding+temporal_parameter": 0.14,
    "legacy_parameter": 0.08,
}
LOW_EDIT_PRIOR = {"role": -0.08, "component": -0.10, "operator": -0.09}


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest().upper()


def _state(policy: engine.MechanismEvolutionV2) -> dict[str, Any]:
    realization = policy.realization_v2_state
    if not isinstance(realization, dict):
        raise RuntimeError("proposal dispatcher requires Realization V2 state")
    state = realization.get(STATE_KEY)
    if not isinstance(state, dict):
        raise RuntimeError("proposal dispatcher is not configured")
    return state


def _empty_stats() -> dict[str, Any]:
    return {"attempts": 0, **{name: 0 for name in OUTCOMES}, "reward_sum": 0.0}


def _merge_stats(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "attempts": int(left.get("attempts", 0)) + int(right.get("attempts", 0)),
        **{
            name: int(left.get(name, 0)) + int(right.get(name, 0))
            for name in OUTCOMES
        },
        "reward_sum": float(left.get("reward_sum", 0.0))
        + float(right.get("reward_sum", 0.0)),
    }


def _validate_prior(prior: Mapping[str, Any]) -> dict[str, Any]:
    value = json.loads(json.dumps(dict(prior)))
    observed = str(value.get("prior_sha256") or "")
    core = {key: item for key, item in value.items() if key != "prior_sha256"}
    if (
        value.get("status") != "TRAIN_ONLY_PROPOSAL_PRIOR_READY"
        or observed != _sha(core)
        or value.get("forbidden_fields_verified") is not True
        or int(value.get("validation_reads", -1)) != 0
        or int(value.get("oos_reads", -1)) != 0
        or int(value.get("holdout_reads", -1)) != 0
        or int(value.get("forward_reads", -1)) != 0
        or int(value.get("promotion_reads", -1)) != 0
        or int(value.get("sealed_reads", -1)) != 0
    ):
        raise ValueError("proposal prior identity or train-only boundary changed")
    return value


def seal_historical_prior(payload: Mapping[str, Any]) -> dict[str, Any]:
    core = {key: value for key, value in dict(payload).items() if key != "prior_sha256"}
    return {**core, "prior_sha256": _sha(core)}


def _json_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str) and value and value.lower() != "nan":
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return dict(parsed) if isinstance(parsed, Mapping) else {}
    return {}


def _historical_feature_keys(row: Mapping[str, Any]) -> dict[str, str]:
    receipt = _json_mapping(row.get("operation_receipt_json")) or _json_mapping(
        row.get("receipt_json")
    )
    edit = str(row.get("semantic_edit_type") or receipt.get("semantic_edit_type") or "")
    edit = edit.replace("_change", "").replace("_crossover", "")
    operation = str(row.get("realized_operation") or row.get("operation") or "")
    if not edit:
        if "PARAMETER" in operation.upper():
            edit = "legacy_parameter"
        elif "CROSSOVER" in operation.upper():
            edit = "legacy_parameter"
        elif "MECHANISM" in operation.upper():
            edit = "operator"
        else:
            edit = "generic"
    field_value = row.get("field_families_json") or row.get("raw_fields_json") or "[]"
    try:
        fields = json.loads(str(field_value)) if isinstance(field_value, str) else field_value
    except json.JSONDecodeError:
        fields = []
    field_signature = "+".join(sorted(str(value) for value in (fields or ())))
    arm = str(row.get("representation_tournament_arm") or "")
    route = str(receipt.get("construction_route") or "")
    if not route:
        route = (
            "REPRESENTATION_SUCCESSOR_RECOMBINATION"
            if arm == "TEMPORAL_REPRESENTATION_SUCCESSOR"
            else "LEGACY_PARAMETER_RECOMBINATION"
            if "CROSSOVER" in operation.upper()
            else "DIMENSION_AWARE_PARAMETER_MUTATION"
        )
    return {
        "family": str(row.get("program_family_id") or "UNKNOWN"),
        "basin": str(
            row.get("targeted_economic_basin_id")
            or receipt.get("targeted_economic_basin_id")
            or "UNKNOWN"
        ),
        "edit_type": edit,
        "mutation_target": str(
            row.get("mutation_target") or receipt.get("mutation_target") or "generic"
        ),
        "operator_path": str(row.get("operator_path") or "UNKNOWN"),
        "field_signature": field_signature or "UNKNOWN",
        "construction_route": route,
    }


def _historical_realization_id(row: Mapping[str, Any]) -> str:
    return _sha(
        {
            "mapped_weight": row.get("mapped_weight_descriptor_id"),
            "turnover": row.get("turnover_path_descriptor_id"),
            "raw_fields": row.get("raw_fields_json"),
            "asset_selection": row.get("selected_asset_overlap_id"),
        }
    )


def build_train_only_historical_prior(
    campaigns: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    global_stats = _empty_stats()
    tables: dict[str, dict[str, dict[str, Any]]] = {}
    campaign_payloads = []
    edit_campaign_stats: dict[str, dict[str, Any]] = {}
    basin_counts: Counter[str] = Counter()
    for campaign in campaigns:
        campaign_id = str(campaign["campaign_id"])
        rows = list(campaign["rows"])
        retained = {str(value) for value in campaign.get("retained_candidate_ids", ())}
        seen_realizations: set[tuple[str, str]] = set()
        local_edits: dict[str, dict[str, Any]] = {}
        for original in rows:
            row = {key: original.get(key) for key in HISTORICAL_SAFE_FIELDS}
            keys = _historical_feature_keys(row)
            candidate_id = str(row.get("candidate_id") or "")
            realization = _historical_realization_id(row)
            basin_key = (keys["basin"], realization)
            new_realization = basin_key not in seen_realizations
            seen_realizations.add(basin_key)
            matched = bool(row.get("matched_positive"))
            basin_retained = candidate_id in retained if retained else matched
            outcomes = {
                "matched_positive": matched,
                "basin_retained": basin_retained,
                "new_realization": new_realization,
                "new_hq_realization": matched and basin_retained and new_realization,
                "positive_reward": float(row.get("search_reward") or 0.0) > 0.0,
                "search_reward": float(row.get("search_reward") or 0.0),
            }
            increment = {
                "attempts": 1,
                **{name: int(bool(outcomes[name])) for name in OUTCOMES},
                "reward_sum": outcomes["search_reward"],
            }
            global_stats = _merge_stats(global_stats, increment)
            basin_counts[keys["basin"]] += 1
            for group, key in keys.items():
                group_table = tables.setdefault(group, {})
                group_table[key] = _merge_stats(
                    group_table.get(key, _empty_stats()), increment
                )
            edit = keys["edit_type"]
            local_edits[edit] = _merge_stats(
                local_edits.get(edit, _empty_stats()), increment
            )
        edit_campaign_stats[campaign_id] = local_edits
        campaign_payloads.append(
            {
                "campaign_id": campaign_id,
                "row_count": len(rows),
                "retained_candidate_count": len(retained),
                "outcomes": _merge_stats(
                    _empty_stats(),
                    {
                        "attempts": len(rows),
                        **{
                            outcome: sum(
                                int(stats.get(outcome, 0))
                                for stats in local_edits.values()
                            )
                            for outcome in OUTCOMES
                        },
                        "reward_sum": sum(
                            float(stats.get("reward_sum", 0.0))
                            for stats in local_edits.values()
                        ),
                    },
                ),
                "source": dict(campaign.get("source") or {}),
            }
        )
    strong = {"normalization", "binding", "temporal_parameter", "binding+temporal_parameter"}
    weak = {"role", "component", "operator"}

    def matched_rate(edits: set[str]) -> float:
        stats = _empty_stats()
        for edit in edits:
            stats = _merge_stats(stats, tables.get("edit_type", {}).get(edit, {}))
        return float(stats["matched_positive"]) / max(1, int(stats["attempts"]))

    total = sum(basin_counts.values())
    payload = {
        "schema_version": 1,
        "status": "TRAIN_ONLY_PROPOSAL_PRIOR_READY",
        "campaigns": campaign_payloads,
        "campaign_separated": len(campaign_payloads) >= 2,
        "global": global_stats,
        "tables": {
            group: {key: value for key, value in sorted(values.items())}
            for group, values in sorted(tables.items())
        },
        "campaign_edit_statistics": edit_campaign_stats,
        "calibration": {
            "strong_edit_matched_rate": matched_rate(strong),
            "weak_edit_matched_rate": matched_rate(weak),
            "strong_edit_ranked_above_weak": matched_rate(strong) > matched_rate(weak),
            "maximum_basin_share": max(basin_counts.values(), default=0) / max(1, total),
            "severe_basin_concentration": (
                max(basin_counts.values(), default=0) / max(1, total) > 0.35
            ),
        },
        "safe_fields": sorted(HISTORICAL_SAFE_FIELDS),
        "forbidden_fields_verified": True,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }
    return seal_historical_prior(payload)


def configure_policy_dispatcher_v1(
    policy: engine.MechanismEvolutionV2,
    *,
    historical_prior: Mapping[str, Any],
) -> None:
    prior = _validate_prior(historical_prior)
    realization = policy.realization_v2_state
    if not isinstance(realization, dict):
        raise RuntimeError("dispatcher configuration requires Realization V2")
    state = {
        "schema_version": 1,
        "dispatcher_id": DISPATCHER_ID,
        "historical_prior": prior,
        "historical_prior_sha256": prior["prior_sha256"],
        "pool_cap": POOL_CAP,
        "source_cap": SOURCE_CAP,
        "exploration_probability": EXPLORATION_PROBABILITY,
        "top_region_fraction": TOP_REGION_FRACTION,
        "smoothing_strength": SMOOTHING_STRENGTH,
        "online_tables": {},
        "selection_counts": {},
        "mutation_target_counts": {},
        "dispatch_counters": {
            "dispatches": 0,
            "legal_generated": 0,
            "legal_scored": 0,
            "exploration_selected": 0,
            "exploitation_selected": 0,
            "pool_under_eight": 0,
        },
        "pool_size_counts": {},
        "selected_rank_counts": {},
        "score_decile_outcomes": {},
        "source_generated": {},
        "source_selected": {},
        "edit_generated": {},
        "edit_selected": {},
        "target_generated": {},
        "target_selected": {},
    }
    state["configuration_sha256"] = _sha(
        {key: value for key, value in state.items() if key != "configuration_sha256"}
    )
    realization[STATE_KEY] = state


def dispatcher_state_hash(policy: engine.MechanismEvolutionV2) -> str:
    return _sha(_state(policy))


def _record(policy: engine.MechanismEvolutionV2, candidate_id: str) -> dict[str, Any]:
    value = targeted_parent_record(policy, candidate_id)
    if value is None:
        raise KeyError(candidate_id)
    return dict(value)


def _dimension_counts(policy: engine.MechanismEvolutionV2, basin_id: str) -> dict[str, int]:
    fields = {
        "mapped_weight": "mapped_weight_descriptor_id",
        "turnover": "turnover_path_descriptor_id",
        "raw_field": "raw_fields_json",
        "asset_selection": "selected_asset_overlap_id",
    }
    records = [_record(policy, candidate_id) for candidate_id in targeted_members(policy, basin_id)]
    return {
        dimension: len({str(row.get(field) or "NOT_AVAILABLE") for row in records})
        for dimension, field in fields.items()
    }


def _table_stats(state: Mapping[str, Any], group: str, key: str) -> dict[str, Any]:
    historical = dict(state["historical_prior"].get("tables") or {})
    history = dict(dict(historical.get(group) or {}).get(key) or {})
    online = dict(dict(state.get("online_tables") or {}).get(group) or {})
    return _merge_stats(history, dict(online.get(key) or {}))


def _global_stats(state: Mapping[str, Any]) -> dict[str, Any]:
    history = dict(state["historical_prior"].get("global") or {})
    online = dict(dict(state.get("online_tables") or {}).get("global") or {}).get("ALL")
    return _merge_stats(history, dict(online or {}))


def _smoothed_rate(stats: Mapping[str, Any], outcome: str, prior: float) -> float:
    total = float(stats.get("attempts", 0))
    return (
        float(stats.get(outcome, 0)) + SMOOTHING_STRENGTH * prior
    ) / (total + SMOOTHING_STRENGTH)


def _target_conversion(state: Mapping[str, Any], target: str) -> float:
    global_stats = _global_stats(state)
    global_prior = {
        outcome: float(global_stats.get(outcome, 0))
        / max(1.0, float(global_stats.get("attempts", 0)))
        for outcome in OUTCOMES
    }
    stats = _table_stats(state, "mutation_target", target)
    score = sum(
        OUTCOME_WEIGHTS[outcome]
        * _smoothed_rate(stats, outcome, global_prior[outcome])
        for outcome in OUTCOMES
    )
    if target == "turnover":
        score *= 0.25
    return score


def select_mutation_target_v1(
    policy: engine.MechanismEvolutionV2, basin_id: str
) -> str:
    state = _state(policy)
    counts = _dimension_counts(policy, basin_id)
    shallow = [
        name
        for name, minimum in (
            ("mapped_weight", 3),
            ("raw_field", 2),
            ("asset_selection", 2),
            ("turnover", 2),
        )
        if counts[name] < minimum
    ]
    candidates = shallow or list(TARGETS[:-1])
    candidates.append("generic")
    weights = []
    for target in candidates:
        conversion = _target_conversion(state, target)
        exploration = 1.0 / math.sqrt(
            1.0 + int(dict(state["mutation_target_counts"]).get(target, 0))
        )
        weights.append(max(0.02, conversion + 0.08 * exploration))
    draw = policy.rng.random() * sum(weights)
    cumulative = 0.0
    selected = candidates[-1]
    for target, weight in zip(candidates, weights, strict=True):
        cumulative += weight
        if draw <= cumulative:
            selected = target
            break
    counter = Counter(state["mutation_target_counts"])
    counter[selected] += 1
    state["mutation_target_counts"] = dict(sorted(counter.items()))
    return selected


def _edit_type(details: Mapping[str, Any], route: str) -> str:
    explicit = str(details.get("semantic_edit_type") or "")
    if explicit:
        value = explicit.replace("_change", "").replace("_crossover", "")
        return value or route.lower()
    groups = [name for group in details.get("changed_gene_groups", ()) for name in group]
    edits = []
    if any("field" in name for name in groups):
        edits.append("binding")
    if any("normalizer" in name for name in groups):
        edits.append("normalization")
    if any(
        token in name
        for name in groups
        for token in ("window", "threshold", "horizon", "beta")
    ):
        edits.append("temporal_parameter")
    if not edits and route.startswith("LEGACY"):
        return "legacy_parameter"
    return "+".join(dict.fromkeys(edits)) or "generic"


def _canonical_complexity(value: Any) -> int:
    if isinstance(value, Mapping):
        return 1 + sum(_canonical_complexity(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return 1 + sum(_canonical_complexity(item) for item in value)
    return 1


def _feature_vector(
    policy: engine.MechanismEvolutionV2,
    *,
    candidate: CandidateSpec,
    parents: Sequence[CandidateSpec],
    basin_id: str,
    route: str,
    details: Mapping[str, Any],
    pool_size: int,
) -> dict[str, Any]:
    state = _state(policy)
    parent_rows = [_record(policy, parent.candidate_id) for parent in parents]
    origin = parent_rows[0]
    genes = candidate.generation_genes
    dimension_counts = _dimension_counts(policy, basin_id)
    field_signature = "+".join(sorted(set(candidate.field_families)))
    raw_field_signature = "+".join(sorted(candidate.raw_fields))
    normalizers = sorted(
        str(value) for key, value in genes.items() if "normalizer" in key
    )
    scales = sorted(
        f"{key}={value}"
        for key, value in genes.items()
        if any(token in key for token in ("window", "threshold", "horizon", "beta"))
    )
    edit_type = _edit_type(details, route)
    parent_genes = parents[0].generation_genes
    changed_count = sum(
        genes.get(key) != parent_genes.get(key) for key in set(genes) | set(parent_genes)
    )
    cells = Counter(
        str(_record(policy, candidate_id).get("realization_cell_id") or "")
        for candidate_id in targeted_members(policy, basin_id)
    )
    parent_cell = str(origin.get("realization_cell_id") or "")
    return {
        "program_family_id": str(genes["program_spec"]["family_id"]),
        "economic_basin_id": basin_id,
        "parent_quality": float(origin.get("search_reward") or 0.0),
        "parent_matched_positive": bool(
            origin.get("matched_positive", origin.get("parent_source") == "FROZEN_TRAIN_ONLY_BASELINE")
        ),
        "parent_realization_cell": parent_cell,
        "parent_lineage_depth": int(origin.get("lineage_depth") or 0),
        "parent_source": str(origin.get("parent_source") or ""),
        "basin_occupancy": len(targeted_members(policy, basin_id)),
        "basin_hq_depth": sum(
            bool(_record(policy, candidate_id).get("matched_positive", True))
            for candidate_id in targeted_members(policy, basin_id)
        ),
        "rare_realization_cell": cells[parent_cell] <= 1,
        "missing_dimensions": sorted(
            name
            for name, minimum in (
                ("mapped_weight", 3),
                ("turnover", 2),
                ("raw_field", 2),
                ("asset_selection", 2),
            )
            if dimension_counts[name] < minimum
        ),
        "requested_operation": str(details.get("requested_operation") or route),
        "construction_route": route,
        "semantic_edit_type": edit_type,
        "changed_gene_groups": details.get("changed_gene_groups", []),
        "normalization_changed": "normalization" in edit_type,
        "binding_changed": "binding" in edit_type,
        "temporal_parameter_changed": "temporal_parameter" in edit_type,
        "role_changed": "role" in edit_type,
        "component_changed": "component" in edit_type,
        "operator_changed": "operator" in edit_type,
        "repair_size": int(details.get("repair_size") or 0),
        "completion_failure_count": int(details.get("completion_failure_count") or 0),
        "legal_child_pool_size": int(details.get("legal_child_count") or pool_size),
        "mutation_target": str(details.get("mutation_target") or "generic"),
        "program_id": str(genes["program_id"]),
        "operator_path": candidate.operator_path,
        "field_signature": field_signature,
        "raw_field_signature": raw_field_signature,
        "normalizer_signature": "+".join(normalizers),
        "scale_signature": "+".join(scales),
        "candidate_complexity": _canonical_complexity(candidate.expression.canonical_dict()),
        "candidate_unseen": candidate.candidate_id not in policy.seen,
        "representation_distance_from_parent": changed_count,
        "selected_count_edit": int(dict(state["selection_counts"]).get("edit:" + edit_type, 0)),
        "selected_count_program": int(dict(state["selection_counts"]).get("program:" + str(genes["program_id"]), 0)),
        "selected_count_operator": int(dict(state["selection_counts"]).get("operator:" + candidate.operator_path, 0)),
        "selected_count_field": int(dict(state["selection_counts"]).get("field:" + field_signature, 0)),
    }


def _economic_score(state: Mapping[str, Any], features: Mapping[str, Any]) -> float:
    global_stats = _global_stats(state)
    global_prior = {
        outcome: float(global_stats.get(outcome, 0))
        / max(1.0, float(global_stats.get("attempts", 0)))
        for outcome in OUTCOMES
    }
    keys = {
        "family": str(features["program_family_id"]),
        "basin": str(features["economic_basin_id"]),
        "edit_type": str(features["semantic_edit_type"]),
        "mutation_target": str(features["mutation_target"]),
        "operator_path": str(features["operator_path"]),
        "field_signature": str(features["field_signature"]),
        "construction_route": str(features["construction_route"]),
    }
    score = 0.0
    for group, key in keys.items():
        stats = _table_stats(state, group, key)
        component = sum(
            OUTCOME_WEIGHTS[outcome]
            * _smoothed_rate(stats, outcome, global_prior[outcome])
            for outcome in OUTCOMES
        )
        score += FEATURE_GROUP_WEIGHTS[group] * component
    edit = str(features["semantic_edit_type"])
    score += POSITIVE_EDIT_PRIOR.get(edit, LOW_EDIT_PRIOR.get(edit, 0.0))
    return score


def _score(state: Mapping[str, Any], features: Mapping[str, Any]) -> dict[str, float]:
    economic = _economic_score(state, features)
    missing = set(features["missing_dimensions"])
    target = str(features["mutation_target"])
    novelty = (
        0.06 * bool(features["rare_realization_cell"])
        + 0.05 * bool(target in missing)
        + 0.02 * min(4, int(features["representation_distance_from_parent"]))
    )
    exploration = 0.035 * sum(
        1.0 / math.sqrt(1.0 + int(features[name]))
        for name in (
            "selected_count_edit",
            "selected_count_program",
            "selected_count_operator",
            "selected_count_field",
        )
    )
    failure_penalty = (
        0.015 * int(features["repair_size"])
        + 0.002 * int(features["completion_failure_count"])
    )
    total = economic + novelty + exploration - failure_penalty
    return {
        "economic_prior": economic,
        "novelty_value": novelty,
        "exploration_bonus": exploration,
        "known_failure_penalty": failure_penalty,
        "total": total,
    }


def _proposal(
    candidate: CandidateSpec,
    parents: Sequence[CandidateSpec],
    receipt: Mapping[str, Any],
    route: str,
    verifier: str,
) -> dict[str, Any]:
    return {
        "candidate": candidate,
        "parents": tuple(parents),
        "receipt": dict(receipt),
        "route": route,
        "verifier": verifier,
    }


def _parameter_pool(
    policy: engine.MechanismEvolutionV2,
    parent: CandidateSpec,
    target: str,
) -> list[dict[str, Any]]:
    output = []
    for index in range(SOURCE_CAP):
        selected_target = target if index < SOURCE_CAP - 2 else "generic"
        try:
            child, receipt = policy._mutate_parameters(
                parent, target_dimension=selected_target
            )
        except (ValueError, RuntimeError):
            continue
        details = {
            "requested_operation": "parameter_mutation",
            "realized_operation": "parameter_mutation",
            "mutation_target": selected_target,
        }
        receipt_core = {
            key: value for key, value in receipt.items() if key != "receipt_sha256"
        }
        receipt_core.update(details)
        receipt = {**receipt_core, "receipt_sha256": engine._payload_sha(receipt_core)}
        output.append(
            _proposal(
                child,
                (parent,),
                receipt,
                "DIMENSION_AWARE_PARAMETER_MUTATION",
                "LEGACY",
            )
        )
        output[-1]["details"] = details
    return output


def _legacy_crossover_pool(
    policy: engine.MechanismEvolutionV2,
    first: CandidateSpec,
    second: CandidateSpec | None,
) -> list[dict[str, Any]]:
    if second is None:
        return []
    legal, details = constructive_crossover_children(policy, first, second)
    output = []
    for candidate_id in sorted(legal)[:SOURCE_CAP]:
        selected, child = legal[candidate_id]
        child_details = {
            **details,
            "selected_splice": selected,
            "requested_operation": "crossover",
            "realized_operation": "crossover",
            "semantic_edit_type": "legacy_parameter",
        }
        receipt = policy._receipt(
            operation=engine.MECHANISM_EVOLUTION_OPERATIONS[2],
            parents=(first, second),
            child=child,
            details=child_details,
        )
        output.append(
            {
                **_proposal(
                    child,
                    (first, second),
                    receipt,
                    "LEGACY_PARAMETER_RECOMBINATION",
                    "LEGACY",
                ),
                "details": child_details,
            }
        )
    return output


def _successor_crossover_pool(
    policy: engine.MechanismEvolutionV2,
    first: CandidateSpec,
    second: CandidateSpec | None,
    *,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
) -> list[dict[str, Any]]:
    if second is None:
        return []
    legal, details = representation_successor_children(
        first,
        second,
        registry=policy.registry,
        scale_contract=scale_contract,
        inventory=inventory,
        seen=policy.seen,
    )
    output = []
    for candidate_id in sorted(legal)[:SOURCE_CAP]:
        child, completion = legal[candidate_id]
        changed = list(completion.get("selected_blocks_from_parent_b") or ())
        child_details = {
            **details,
            **completion,
            "requested_operation": "crossover",
            "realized_operation": "crossover",
            "semantic_edit_type": "+".join(changed) or "generic",
        }
        receipt = representation_successor_receipt(
            operation=engine.MECHANISM_EVOLUTION_OPERATIONS[2],
            parents=(first, second),
            child=child,
            details=child_details,
        )
        output.append(
            {
                **_proposal(
                    child,
                    (first, second),
                    receipt,
                    "REPRESENTATION_SUCCESSOR_RECOMBINATION",
                    "SUCCESSOR",
                ),
                "details": child_details,
            }
        )
    return output


def _semantic_donor_pool(
    policy: engine.MechanismEvolutionV2,
    parent: CandidateSpec,
    *,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
) -> list[dict[str, Any]]:
    family = str(parent.generation_genes["program_spec"]["family_id"])
    donors: list[tuple[str, Any, str]] = [
        ("TEMPORAL_PROGRAM_V1", donor, block)
        for block in SEMANTIC_BLOCKS
        for donor in inventory.programs_by_family[family]
    ] + [
        ("MECHANISM_V2_1", donor, block)
        for block in ("role", "operator")
        for donor in inventory.compatible_mechanism_donors
    ]
    state = _state(policy)
    offset = int(state["dispatch_counters"]["dispatches"])
    donors.sort(
        key=lambda row: (
            -POSITIVE_EDIT_PRIOR.get(row[2], LOW_EDIT_PRIOR.get(row[2], 0.0)),
            _sha(
                {
                    "seed": policy.seed,
                    "offset": offset,
                    "catalog": row[0],
                    "donor": getattr(row[1], "program_id", getattr(row[1], "mechanism_id", "")),
                    "block": row[2],
                }
            ),
        )
    )
    output = []
    for catalog, donor, block in donors[: SOURCE_CAP * 4]:
        try:
            if catalog == "TEMPORAL_PROGRAM_V1":
                child, completion = semantic_block_mutation(
                    parent,
                    donor_program=donor,
                    block=block,
                    registry=policy.registry,
                    scale_contract=scale_contract,
                    inventory=inventory,
                )
            else:
                child, completion = semantic_mechanism_donor_mutation(
                    parent,
                    donor=donor,
                    block=block,
                    registry=policy.registry,
                    scale_contract=scale_contract,
                    inventory=inventory,
                )
        except ValueError:
            continue
        if child.candidate_id in policy.seen:
            continue
        details = {
            **completion,
            "requested_operation": "mechanism_mutation",
            "realized_operation": "mechanism_mutation",
            "semantic_edit_type": block,
        }
        receipt = representation_successor_receipt(
            operation=engine.MECHANISM_EVOLUTION_OPERATIONS[1],
            parents=(parent,),
            child=child,
            details=details,
        )
        output.append(
            {
                **_proposal(
                    child,
                    (parent,),
                    receipt,
                    "SEMANTIC_DONOR_MUTATION",
                    "SUCCESSOR",
                ),
                "details": details,
            }
        )
        if len(output) >= SOURCE_CAP:
            break
    return output


def _weighted_index(policy: engine.MechanismEvolutionV2, scores: Sequence[float]) -> int:
    minimum = min(scores)
    weights = [max(1.0e-9, value - minimum + 0.01) for value in scores]
    draw = policy.rng.random() * sum(weights)
    cumulative = 0.0
    for index, weight in enumerate(weights):
        cumulative += weight
        if draw <= cumulative:
            return index
    return len(weights) - 1


def propose_with_dispatcher_v1(
    policy: engine.MechanismEvolutionV2,
    *,
    scale_contract: Mapping[str, Any],
    inventory: TemporalRepresentationInventory,
) -> tuple[CandidateSpec, dict[str, Any]]:
    state = _state(policy)
    state_hash_before = policy.state_hash()
    dispatch_state_hash_before = dispatcher_state_hash(policy)
    limit = int(policy.parameters.get("duplicate_resample_limit", 64))
    for duplicate_attempt in range(1, limit + 2):
        basin_id = next_targeted_basin(policy)
        first = next_targeted_parent(policy, basin_id)
        target = select_mutation_target_v1(policy, basin_id)
        legacy_second = policy._targeted_crossover_parent(basin_id, first)
        successor_second = _successor_second_parent(policy, basin_id, first)
        pool = (
            _parameter_pool(policy, first, target)
            + _legacy_crossover_pool(policy, first, legacy_second)
            + _successor_crossover_pool(
                policy,
                first,
                successor_second,
                scale_contract=scale_contract,
                inventory=inventory,
            )
            + _semantic_donor_pool(
                policy,
                first,
                scale_contract=scale_contract,
                inventory=inventory,
            )
        )
        unique: dict[str, dict[str, Any]] = {}
        for item in pool:
            candidate_id = item["candidate"].candidate_id
            if candidate_id not in policy.seen and candidate_id not in unique:
                unique[candidate_id] = item
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
            score = _score(state, features)
            scored.append({**item, "features": features, "score": score})
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
        selected = eligible[
            _weighted_index(policy, [float(item["score"]["total"]) for item in eligible])
        ]
        rank = ranked.index(selected) + 1
        parents = selected["parents"]
        child = selected["candidate"]
        receipt = policy._bind_targeted_receipt(
            selected["receipt"], basin_id=basin_id, parents=parents
        )
        if selected["verifier"] == "LEGACY":
            verified = policy.verify_receipt(parents, child, receipt)
        else:
            verified = verify_successor_receipt(policy.registry, parents, child, receipt)
        if not verified:
            raise RuntimeError("proposal dispatcher selected receipt failed verification")
        policy.seen.add(child.candidate_id)
        policy.step += 1
        counters = Counter(state["dispatch_counters"])
        counters["dispatches"] += 1
        counters["legal_generated"] += len(unique)
        counters["legal_scored"] += len(ranked)
        counters["exploration_selected" if explore else "exploitation_selected"] += 1
        counters["pool_under_eight"] += len(ranked) < 8
        state["dispatch_counters"] = dict(sorted(counters.items()))
        for field, value in (
            ("pool_size_counts", str(len(ranked))),
            ("selected_rank_counts", str(rank)),
            ("source_selected", selected["route"]),
            ("edit_selected", selected["features"]["semantic_edit_type"]),
            ("target_selected", selected["features"]["mutation_target"]),
        ):
            counter = Counter(state[field])
            counter[str(value)] += 1
            state[field] = dict(sorted(counter.items()))
        for item in ranked:
            for field, value in (
                ("source_generated", item["route"]),
                ("edit_generated", item["features"]["semantic_edit_type"]),
                ("target_generated", item["features"]["mutation_target"]),
            ):
                counter = Counter(state[field])
                counter[str(value)] += 1
                state[field] = dict(sorted(counter.items()))
        selection_counts = Counter(state["selection_counts"])
        for key in (
            "edit:" + str(selected["features"]["semantic_edit_type"]),
            "program:" + str(selected["features"]["program_id"]),
            "operator:" + str(selected["features"]["operator_path"]),
            "field:" + str(selected["features"]["field_signature"]),
        ):
            selection_counts[key] += 1
        state["selection_counts"] = dict(sorted(selection_counts.items()))
        score_values = [float(item["score"]["total"]) for item in ranked]
        selected_decile = min(9, int((rank - 1) * 10 / len(ranked)))
        dispatch_receipt = {
            "schema_version": 1,
            "dispatcher_id": DISPATCHER_ID,
            "historical_prior_sha256": state["historical_prior_sha256"],
            "dispatcher_state_hash_before": dispatch_state_hash_before,
            "candidate_feature_hash": _sha(selected["features"]),
            "candidate_features": selected["features"],
            "score_components": selected["score"],
            "scoring_model_state_hash": scoring_model_state_hash,
            "legal_candidates_generated": len(unique),
            "legal_candidates_scored": len(ranked),
            "pool_score_minimum": min(score_values),
            "pool_score_median": sorted(score_values)[len(score_values) // 2],
            "pool_score_maximum": max(score_values),
            "selected_score": float(selected["score"]["total"]),
            "selected_rank": rank,
            "selected_score_decile": selected_decile,
            "exploration_selected": explore,
            "construction_route": selected["route"],
        }
        dispatch_receipt["dispatch_receipt_sha256"] = _sha(dispatch_receipt)
        return child, {
            "policy_state_hash_before": state_hash_before,
            "operation": str(receipt["operation"]),
            "parent_ids": [parent.candidate_id for parent in parents],
            "receipt": receipt,
            "receipt_verified": True,
            "raw_attempts": duplicate_attempt + len(unique),
            "compile_valid_attempts": len(unique),
            "targeted_economic_basin_id": basin_id,
            "targeted_parent_pool_sha256": str(
                policy.targeted_parent_pool_payload["target_parent_pool_sha256"]
            ),
            "dispatch_receipt": dispatch_receipt,
        }
    raise engine._ProposalGenerationFailure(
        "proposal dispatcher legal pool exhausted", raw_attempts=limit + 1
    )


def _increment_table(
    state: dict[str, Any], group: str, key: str, outcomes: Mapping[str, Any]
) -> None:
    tables = state["online_tables"]
    group_table = dict(tables.get(group) or {})
    stats = dict(group_table.get(key) or _empty_stats())
    stats["attempts"] = int(stats.get("attempts", 0)) + 1
    for outcome in OUTCOMES:
        stats[outcome] = int(stats.get(outcome, 0)) + int(bool(outcomes[outcome]))
    stats["reward_sum"] = float(stats.get("reward_sum", 0.0)) + float(
        outcomes["search_reward"]
    )
    group_table[key] = stats
    tables[group] = group_table


def observe_dispatcher_v1(
    policy: engine.MechanismEvolutionV2,
    *,
    ledger_row: Mapping[str, Any],
    dispatch_receipt: Mapping[str, Any],
    basin_retained: bool,
    new_realization: bool,
    new_hq_realization: bool,
) -> dict[str, Any]:
    state = _state(policy)
    core = {
        key: value for key, value in dispatch_receipt.items() if key != "dispatch_receipt_sha256"
    }
    if dispatch_receipt.get("dispatch_receipt_sha256") != _sha(core):
        raise RuntimeError("proposal dispatch receipt changed before observation")
    features = dict(dispatch_receipt["candidate_features"])
    outcomes = {
        "matched_positive": bool(ledger_row["matched_positive"]),
        "basin_retained": bool(basin_retained),
        "new_realization": bool(new_realization),
        "new_hq_realization": bool(new_hq_realization),
        "positive_reward": float(ledger_row["search_reward"]) > 0.0,
        "search_reward": float(ledger_row["search_reward"]),
    }
    keys = {
        "global": "ALL",
        "family": str(features["program_family_id"]),
        "basin": str(features["economic_basin_id"]),
        "edit_type": str(features["semantic_edit_type"]),
        "mutation_target": str(features["mutation_target"]),
        "operator_path": str(features["operator_path"]),
        "field_signature": str(features["field_signature"]),
        "construction_route": str(features["construction_route"]),
    }
    for group, key in keys.items():
        _increment_table(state, group, key, outcomes)
    decile = str(int(dispatch_receipt["selected_score_decile"]))
    deciles = dict(state["score_decile_outcomes"])
    stats = dict(deciles.get(decile) or _empty_stats())
    stats = _merge_stats(
        stats,
        {
            "attempts": 1,
            **{name: int(bool(outcomes[name])) for name in OUTCOMES},
            "reward_sum": float(outcomes["search_reward"]),
        },
    )
    deciles[decile] = stats
    state["score_decile_outcomes"] = dict(sorted(deciles.items()))
    return outcomes


def dispatcher_diagnostics(policies: Mapping[str, Any]) -> dict[str, Any]:
    aggregates: dict[str, Counter[str]] = {
        key: Counter()
        for key in (
            "dispatch_counters",
            "pool_size_counts",
            "selected_rank_counts",
            "source_generated",
            "source_selected",
            "edit_generated",
            "edit_selected",
            "target_generated",
            "target_selected",
        )
    }
    deciles: dict[str, dict[str, Any]] = {}
    prior_hashes = set()
    state_hashes = {}
    for key, policy in sorted(policies.items()):
        if not isinstance(policy, engine.MechanismEvolutionV2):
            continue
        state = _state(policy)
        prior_hashes.add(str(state["historical_prior_sha256"]))
        state_hashes[key] = dispatcher_state_hash(policy)
        for name in aggregates:
            aggregates[name].update(state[name])
        for decile, stats in state["score_decile_outcomes"].items():
            deciles[decile] = _merge_stats(deciles.get(decile, _empty_stats()), stats)
    pool_values = [
        int(size)
        for size, count in aggregates["pool_size_counts"].items()
        for _ in range(int(count))
    ]
    result = {
        "schema_version": 1,
        "dispatcher_id": DISPATCHER_ID,
        "historical_prior_sha256": next(iter(prior_hashes)) if len(prior_hashes) == 1 else None,
        "policy_state_hashes": state_hashes,
        **{name: dict(sorted(counter.items())) for name, counter in aggregates.items()},
        "average_pool_size": sum(pool_values) / max(1, len(pool_values)),
        "median_pool_size": (
            sorted(pool_values)[len(pool_values) // 2] if pool_values else 0
        ),
        "score_decile_outcomes": dict(sorted(deciles.items())),
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }
    result["diagnostics_sha256"] = _sha(result)
    return result


__all__ = [
    "DISPATCHER_ID",
    "EXPLORATION_PROBABILITY",
    "POOL_CAP",
    "configure_policy_dispatcher_v1",
    "build_train_only_historical_prior",
    "dispatcher_diagnostics",
    "dispatcher_state_hash",
    "observe_dispatcher_v1",
    "propose_with_dispatcher_v1",
    "seal_historical_prior",
    "select_mutation_target_v1",
]
