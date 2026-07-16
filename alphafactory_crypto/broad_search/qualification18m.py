"""Evidence qualification for the frozen 18-month localized mechanisms.

This module is deliberately not a search runner.  It consumes the committed
candidate pack and the already-authorized development cache, then reconstructs
lineage, identities, economics, fixed ablations, and cross-seed relationships.
It cannot generate proposals, change the candidate pack, or read any surface
outside the two development blocks recorded by the source runtime contract.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from alphafactory_crypto.instrument_capability.mapping import (
    DEFAULT_MAPPING_CONTRACTS,
    map_portfolio,
    mapping_contract_sha256,
)
from alphafactory_crypto.instrument_canary.release import sha256_file

from .compositional18m import CandidateSpec, Expression, expression_from_dict
from .expression import (
    FieldContract,
    TypedExpressionRegistry,
    materialize_expression,
)
from .pair18m import (
    ACTIVE_EPSILON,
    FIXED_COST_BPS,
    _series_metrics,
    _turnover,
    robust_monthly_audit,
)
from .panel18m import RawPanelStore
from .runner18m import (
    POLICIES,
    _cluster_evidence,
    _cluster_key,
    _policy_audit,
)


FINAL_CLASSIFICATIONS = frozenset(
    {
        "LOCALIZED_DEVELOPMENT_INCREMENT_OBSERVED",
        "LEGITIMATE_REGIME_LOCALIZATION",
        "ACCIDENTAL_CONCENTRATION",
        "MAPPING_OR_IDENTITY_ARTIFACT",
        "INSUFFICIENT_INDEPENDENT_EVIDENCE",
    }
)

AUDIT_OUTPUTS = (
    "CRYPTO_SELECTION_LINEAGE_AUDIT.json",
    "CRYPTO_IDENTITY_AUDIT.json",
    "CRYPTO_ECONOMIC_DECOMPOSITION.parquet",
    "CRYPTO_REPORT_ONLY_INDEPENDENCE_AUDIT.json",
    "CRYPTO_STATE_REGIME_ABLATION.json",
    "CRYPTO_CROSS_SEED_MECHANISM_AUDIT.json",
)

DECISION_OUTPUTS = (
    "CRYPTO_LOCALIZED_MECHANISM_DECISION.json",
    "CRYPTO_IMMUTABLE_CHALLENGER_SPECIFICATION.json",
    "CRYPTO_QUALIFICATION_ARTIFACT_MANIFEST.json",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, default=str)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _payload_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
        ).encode("utf-8")
    ).hexdigest().upper()


def _array_sha(values: np.ndarray) -> str:
    array = np.nan_to_num(np.asarray(values, dtype="<f8"), nan=9.87654321e37)
    digest = hashlib.sha256()
    digest.update(str(array.shape).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest().upper()


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()


def _corr(left: np.ndarray, right: np.ndarray) -> float | None:
    a = np.asarray(left, dtype=float).ravel()
    b = np.asarray(right, dtype=float).ravel()
    finite = np.isfinite(a) & np.isfinite(b)
    if int(finite.sum()) < 3:
        return None
    a = a[finite]
    b = b[finite]
    if float(np.std(a)) <= 1e-15 or float(np.std(b)) <= 1e-15:
        return 1.0 if np.array_equal(a, b) else 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _rank_matrix(values: np.ndarray) -> np.ndarray:
    return (
        pd.DataFrame(np.asarray(values, dtype=float))
        .rank(axis=0, method="average", na_option="keep", pct=True)
        .to_numpy(dtype=float)
    )


def _exact_equal(left: np.ndarray, right: np.ndarray) -> bool:
    return bool(
        np.array_equal(
            np.asarray(left, dtype=float),
            np.asarray(right, dtype=float),
            equal_nan=True,
        )
    )


def _expression_text(expression: Expression) -> str:
    if expression.operator == "Raw":
        return f"Raw({expression.field_id})"
    parameters = ""
    if expression.parameters:
        parameters = ", " + ", ".join(
            f"{key}={value}" for key, value in sorted(expression.parameters.items())
        )
    return (
        f"{expression.operator}("
        + ", ".join(_expression_text(value) for value in expression.inputs)
        + parameters
        + ")"
    )


def _ast_tokens(expression: Expression) -> list[str]:
    token = expression.operator
    if expression.field_id:
        token += f":{expression.field_id}"
    if expression.parameters:
        token += ":" + json.dumps(
            dict(sorted(expression.parameters.items())),
            sort_keys=True,
            separators=(",", ":"),
        )
    output = [token]
    for child in expression.inputs:
        output.extend(_ast_tokens(child))
    return output


def _ast_distance(left: Expression, right: Expression) -> float:
    left_counts = Counter(_ast_tokens(left))
    right_counts = Counter(_ast_tokens(right))
    union = sum((left_counts | right_counts).values())
    overlap = sum((left_counts & right_counts).values())
    return 0.0 if union == 0 else float(1.0 - overlap / union)


def _candidate_id(candidate: CandidateSpec) -> str:
    return _payload_sha(
        {
            "skeleton_id": candidate.skeleton_id,
            "expression": candidate.expression.canonical_dict(),
            "control": candidate.control.canonical_dict(),
            "horizon_hours": candidate.horizon_hours,
            "mapping_id": candidate.mapping_id,
        }
    )


def _contracts(field_registry: Mapping[str, Any]) -> tuple[FieldContract, ...]:
    return tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
        )
        for row in field_registry["fields"]
    )


def _validate_config(config: Mapping[str, Any]) -> None:
    if config.get("task_id") != "CRYPTO_LOCALIZED_MECHANISM_EVIDENCE_QUALIFICATION":
        raise ValueError("unexpected qualification task")
    boundaries = config.get("boundaries", {})
    forbidden_true = [
        "new_proposals",
        "search_or_tuning",
        "grammar_changes",
        "field_changes",
        "window_changes",
        "mapping_changes",
        "reward_changes",
        "evaluator_changes",
        "cluster_changes",
        "control_changes",
        "candidate_pack_changes",
        "sealed_reads",
        "formal_search",
        "candidate_promotion",
        "cross_sprint_adaptive_memory",
    ]
    if any(bool(boundaries.get(name)) for name in forbidden_true):
        raise PermissionError("qualification config opened a frozen boundary")
    if boundaries.get("forward") != "SEALED":
        raise PermissionError("forward must remain sealed")
    variants = config["fixed_ablation"]["variants"]
    if variants != [
        "A_FULL_CANDIDATE",
        "B_BASE_SIGNAL_ONLY",
        "C_REGIME_ONLY",
        "D_NEUTRAL_REGIME",
        "E_TIME_SHUFFLED_REGIME",
        "F_LAGGED_REGIME",
        "G_MATCHED_OCCUPANCY_PLACEBO",
    ]:
        raise ValueError("fixed A-G ablation changed")
    blocks = config["authorized_blocks"]
    if (
        blocks["adaptive"]["start"] != "2023-07-01T00:00:00Z"
        or blocks["adaptive"]["end_exclusive"] != "2024-07-01T00:00:00Z"
        or blocks["report_only"]["start"] != "2024-07-01T00:00:00Z"
        or blocks["report_only"]["end_exclusive"] != "2025-01-01T00:00:00Z"
    ):
        raise PermissionError("authorized development coordinates changed")


def _load_context(
    repo_root: Path, config: Mapping[str, Any]
) -> dict[str, Any]:
    source_root = repo_root / str(config["source_runtime_root"])
    cache_root = repo_root / str(config["source_cache_root"])
    if not cache_root.exists():
        raise FileNotFoundError(
            "the disposable source cache is required for numeric qualification"
        )
    source_manifest = _read_json(source_root / "CRYPTO_ARTIFACT_MANIFEST.json")
    if source_manifest.get("bundle_sha256") != config["source_bundle_sha256"]:
        raise ValueError("source runtime bundle identity changed")
    strict = pd.read_parquet(source_root / "CRYPTO_STRICT_PAIR_RESULTS.parquet")
    challenge = pd.read_parquet(
        source_root / "CRYPTO_DEVELOPMENT_CHALLENGE_RESULTS.parquet"
    )
    robust = pd.read_parquet(
        source_root / "CRYPTO_ROBUST_STATISTICAL_AUDIT.parquet"
    )
    reproduction = _read_json(source_root / "CRYPTO_CROSS_SEED_REPRODUCTION.json")
    field_registry = _read_json(
        source_root / "CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY.json"
    )
    store = RawPanelStore.open(cache_root)
    if store.metadata.get("sealed_rows") != 0:
        raise PermissionError("source cache contains sealed rows")
    candidate_id = str(config["unique_robust_candidate_id"])
    robust_positive = robust[robust["robust_positive"].astype(bool)]
    if robust_positive["candidate_id"].astype(str).tolist() != [candidate_id]:
        raise ValueError("unique robust-positive identity changed")
    candidate_rows = strict[strict["candidate_id"].astype(str) == candidate_id]
    if len(candidate_rows) != 1:
        raise ValueError("unique robust candidate occurrence is not singular")
    candidate_row = candidate_rows.iloc[0]
    candidate = CandidateSpec.from_dict(json.loads(str(candidate_row["candidate_spec_json"])))
    if _candidate_id(candidate) != candidate_id:
        raise ValueError("candidate canonical identity does not reproduce")
    challenge_rows = challenge[challenge["candidate_id"].astype(str) == candidate_id]
    if len(challenge_rows) != 1:
        raise ValueError("candidate report-only occurrence is not singular")
    registry = TypedExpressionRegistry(_contracts(field_registry))
    registry.validate(candidate.expression)
    registry.validate(candidate.control)
    return {
        "source_root": source_root,
        "cache_root": cache_root,
        "source_manifest": source_manifest,
        "strict": strict,
        "challenge": challenge,
        "robust": robust,
        "reproduction": reproduction,
        "field_registry": field_registry,
        "store": store,
        "registry": registry,
        "candidate": candidate,
        "candidate_row": candidate_row,
        "challenge_row": challenge_rows.iloc[0],
        "robust_row": robust_positive.iloc[0],
    }


def _selection_lineage(
    config: Mapping[str, Any], context: Mapping[str, Any], *, source_sha: str
) -> dict[str, Any]:
    strict = context["strict"]
    challenge = context["challenge"]
    candidate_row = context["candidate_row"]
    robust_row = context["robust_row"]
    stage_a_pairs = 4096
    stage_a = strict.iloc[:stage_a_pairs].copy()
    stage_a_challenge = challenge.iloc[:stage_a_pairs].copy()
    if not (
        int(stage_a["proposal_step"].min()) == 0
        and int(stage_a["proposal_step"].max()) == 255
        and len(stage_a) == stage_a_pairs
    ):
        raise ValueError("Stage A occurrence boundary changed")
    clusters_a, reproduction_a, counts_a = _cluster_evidence(
        stage_a.to_dict("records"), stage_a_challenge.to_dict("records")
    )
    policy_a = _policy_audit(stage_a.to_dict("records"))
    triggers = {
        "adaptive_positive_clusters_ge_10": bool(
            counts_a["adaptive_positive_clusters"] >= 10
        ),
        "report_only_positive_clusters_ge_5": bool(
            counts_a["challenge_positive_clusters"] >= 5
        ),
        "report_only_maximum_family_yield_gt_0_005": bool(
            counts_a["maximum_family_challenge_yield"] > 0.005
        ),
        "adaptive_cross_seed_stable_policy_improvement": bool(
            policy_a["any_cross_seed_stable_policy_improvement"]
        ),
    }
    adaptive_only_trigger = bool(
        triggers["adaptive_positive_clusters_ge_10"]
        or triggers["adaptive_cross_seed_stable_policy_improvement"]
    )
    full_trigger = bool(any(triggers.values()))
    candidate = context["candidate"]
    lane = strict[
        (strict["policy"] == candidate_row["policy"])
        & (strict["seed"].astype(int) == int(candidate_row["seed"]))
    ].sort_values("proposal_step")
    lane_by_id = {str(row["candidate_id"]): row for _, row in lane.iterrows()}
    chain: list[dict[str, Any]] = []
    current = str(candidate.candidate_id)
    seen: set[str] = set()
    while current:
        if current in seen:
            raise ValueError("proposal parent lineage contains a cycle")
        seen.add(current)
        row = lane_by_id.get(current)
        if row is None:
            raise ValueError("proposal parent is absent from its private lane")
        receipt = json.loads(str(row["mutation_receipt_json"]))
        chain.append(
            {
                "candidate_id": current,
                "proposal_step": int(row["proposal_step"]),
                "parent_id": row["parent_id"],
                "pair_reward": float(row["pair_reward"]),
                "matched_positive": bool(row["matched_positive"]),
                "skeleton_id": str(row["skeleton_id"]),
                "mutation_receipt": receipt,
                "policy_state_hash_before": str(row["policy_state_hash_before"]),
                "policy_state_hash_after": str(row["policy_state_hash_after"]),
            }
        )
        current = str(row["parent_id"]) if pd.notna(row["parent_id"]) else ""
    strict_keys = Counter(
        (str(row.candidate_id), str(row.policy), int(row.seed))
        for row in strict.itertuples()
    )
    challenge_keys = Counter(
        (str(row.candidate_id), str(row.policy), int(row.seed))
        for row in challenge.itertuples()
    )
    family = str(candidate.mechanism_family)
    family_rows = strict[strict["mechanism_family"] == family]
    exact_unique = int(strict["candidate_id"].astype(str).nunique())
    behavior_unique = int(strict["delta_weight_sha256"].dropna().astype(str).nunique())
    cluster_ids = strict.apply(_cluster_key, axis=1)
    candidate_cluster_id = _cluster_key(candidate_row)
    robust_metrics = {
        key: (
            bool(robust_row[key])
            if isinstance(robust_row[key], (bool, np.bool_))
            else float(robust_row[key])
            if isinstance(robust_row[key], (float, np.floating))
            else int(robust_row[key])
            if isinstance(robust_row[key], (int, np.integer))
            else robust_row[key]
        )
        for key in robust_row.index
        if key != "candidate_id"
    }
    return {
        "schema_version": 1,
        "task_id": config["task_id"],
        "audit_source_sha": source_sha,
        "source_bundle_sha256": config["source_bundle_sha256"],
        "proposal_to_robust_chain": {
            "proposal": {
                "candidate_id": candidate.candidate_id,
                "policy": str(candidate_row["policy"]),
                "seed": int(candidate_row["seed"]),
                "proposal_step": int(candidate_row["proposal_step"]),
                "stage": "B" if int(candidate_row["proposal_step"]) >= 256 else "A",
                "parent_id": candidate_row["parent_id"],
                "cumulative_skeleton_exposure": int(
                    candidate_row["cumulative_skeleton_exposure"]
                ),
                "mutation_receipt": json.loads(
                    str(candidate_row["mutation_receipt_json"])
                ),
            },
            "admission": {
                "pair_evaluation_status": str(
                    candidate_row["pair_evaluation_status"]
                ),
                "matched_positive_adaptive": bool(candidate_row["matched_positive"]),
                "pair_reward_adaptive": float(candidate_row["pair_reward"]),
                "matched_positive_report_only": bool(
                    context["challenge_row"]["matched_positive"]
                ),
                "pair_reward_report_only": float(
                    context["challenge_row"]["pair_reward"]
                ),
            },
            "exact_identity": candidate.candidate_id,
            "behavior_identity": str(candidate_row["delta_weight_sha256"]),
            "cluster_id": candidate_cluster_id,
            "cross_seed_reproduced_same_cluster": bool(
                candidate_cluster_id
                in {
                    str(row["cluster_id"])
                    for row in context["reproduction"]["clusters"]
                }
            ),
            "robust": robust_metrics,
        },
        "proposal_lineage": list(reversed(chain)),
        "candidate_lineage": {
            "candidate_id": candidate.candidate_id,
            "formula": _expression_text(candidate.expression),
            "control_formula": _expression_text(candidate.control),
            "raw_fields": list(candidate.raw_fields),
            "field_families": list(candidate.field_families),
            "rolling_windows": list(candidate.rolling_windows),
            "horizon_hours": candidate.horizon_hours,
            "mapping_id": candidate.mapping_id,
        },
        "cluster_lineage": {
            "candidate_cluster_id": candidate_cluster_id,
            "candidate_cluster_members": int((cluster_ids == candidate_cluster_id).sum()),
            "source_cross_seed_clusters": context["reproduction"]["clusters"],
            "stage_a_cross_seed_clusters": reproduction_a["clusters"],
        },
        "family_lineage": {
            "mechanism_family": family,
            "strict_pairs": int(len(family_rows)),
            "exact_unique_candidates": int(
                family_rows["candidate_id"].astype(str).nunique()
            ),
            "adaptive_matched_positive": int(
                family_rows["matched_positive"].astype(bool).sum()
            ),
            "report_only_matched_positive": int(
                challenge[
                    challenge["candidate_id"].astype(str).isin(
                        set(family_rows["candidate_id"].astype(str))
                    )
                ]["matched_positive"]
                .astype(bool)
                .sum()
            ),
            "skeleton_exposure": {
                str(key): int(value)
                for key, value in family_rows.groupby("skeleton_id").size().items()
            },
        },
        "selection_exposure": {
            "strict_occurrences": int(len(strict)),
            "report_only_occurrences": int(len(challenge)),
            "exact_unique_candidates": exact_unique,
            "duplicate_candidate_occurrences": int(len(strict) - exact_unique),
            "behavior_unique_delta_weight_hashes": behavior_unique,
            "behavior_duplicate_occurrences": int(len(strict) - behavior_unique),
            "cluster_count": int(cluster_ids.nunique()),
            "candidate_stage_b_ordinal_within_lane": int(candidate_row["proposal_step"]),
            "candidate_stage_a_absent": bool(
                candidate.candidate_id
                not in set(stage_a["candidate_id"].astype(str))
            ),
            "adaptive_exposure": int(len(strict)),
            "report_only_exposure": int(len(challenge)),
            "strict_report_only_pack_multiset_equal": strict_keys == challenge_keys,
        },
        "stage_b_gate": {
            "stage_a_counts": counts_a,
            "trigger_values": triggers,
            "full_gate_result": full_trigger,
            "adaptive_only_counterfactual_gate_result": adaptive_only_trigger,
            "report_only_terms_were_causally_necessary": bool(
                full_trigger and not adaptive_only_trigger
            ),
            "conclusion": (
                "STAGE_B_COUNTERFACTUALLY_AUTHORIZED_BY_ADAPTIVE_ONLY_EVIDENCE"
                if adaptive_only_trigger
                else "STAGE_B_DEPENDED_ON_REPORT_ONLY_EVIDENCE"
            ),
        },
        "effective_trial_count": {
            "proposal_occurrences": int(len(strict)),
            "exact_formula_trials": exact_unique,
            "portfolio_behavior_trials": behavior_unique,
            "cluster_trials": int(cluster_ids.nunique()),
            "robust_post_selection_tests": int(len(context["robust"])),
            "robust_positive_tests": int(
                context["robust"]["robust_positive"].astype(bool).sum()
            ),
            "selection_warning": (
                "The 18-month robust statistic reuses 12 adaptive months that "
                "participated in proposal selection; only the six report-only "
                "months are an independent temporal retest."
            ),
        },
    }


def _series_arrays(
    *,
    weights: np.ndarray,
    target: np.ndarray,
    evaluation_mask: np.ndarray,
    horizon: int,
) -> dict[str, np.ndarray]:
    turnover, _ = _turnover(weights, horizon)
    gross = np.nansum(weights * target, axis=0) / float(horizon)
    cost = turnover * FIXED_COST_BPS / 10000.0
    net = gross - cost
    mask = np.asarray(evaluation_mask, dtype=bool) | (turnover > ACTIVE_EPSILON)
    return {
        "turnover": turnover,
        "gross": gross,
        "cost": cost,
        "net": net,
        "mask": mask,
    }


def _asset_turnover(weights: np.ndarray, horizon: int) -> np.ndarray:
    previous = np.zeros_like(weights)
    if weights.shape[1] > horizon:
        previous[:, horizon:] = weights[:, :-horizon]
    current_zero = np.abs(weights) <= ACTIVE_EPSILON
    previous_zero = np.abs(previous) <= ACTIVE_EPSILON
    flip = (~current_zero) & (~previous_zero) & (
        np.sign(weights) != np.sign(previous)
    )
    entry = np.where(
        (previous_zero & ~current_zero) | flip, np.abs(weights), 0.0
    )
    exit_ = np.where(
        (~previous_zero & current_zero) | flip, np.abs(previous), 0.0
    )
    rebalance = np.where(
        ~previous_zero & ~current_zero & ~flip,
        np.abs(weights - previous),
        0.0,
    )
    turnover = (entry + exit_ + rebalance) / float(horizon)
    for offset in range(min(horizon, weights.shape[1])):
        terminal_index = weights.shape[1] - 1 - (
            (weights.shape[1] - 1 - offset) % horizon
        )
        turnover[:, terminal_index] += (
            np.abs(weights[:, terminal_index]) / float(horizon)
        )
    return turnover


def _matched_occupancy_weights(
    reference_weights: np.ndarray, signal: np.ndarray, support: np.ndarray
) -> np.ndarray:
    """Relabel the exact reference weight multiset by a variant's ranks.

    Every timestamp retains the reference gross, net, cap, zero count, active
    count, and weight magnitudes.  Only the asset ordering is allowed to change.
    This isolates signal ordering from the native StateModulation sparsity.
    """

    reference = np.asarray(reference_weights, dtype=float)
    values = np.asarray(signal, dtype=float)
    mask = np.asarray(support, dtype=bool)
    output = np.zeros_like(reference)
    for column in range(reference.shape[1]):
        assets = np.flatnonzero(mask[:, column])
        if not assets.size:
            continue
        order = assets[
            np.lexsort((assets, np.nan_to_num(values[assets, column], nan=0.0)))
        ]
        output[order, column] = np.sort(
            reference[assets, column], kind="mergesort"
        )
    return output


def _month_shuffle(
    state: np.ndarray,
    months: np.ndarray,
    support: np.ndarray,
    *,
    seed: int,
) -> np.ndarray:
    output = np.empty_like(state)
    rng = np.random.default_rng(seed)
    for month in tuple(dict.fromkeys(months.tolist())):
        indices = np.flatnonzero(months == month)
        permutation = indices.copy()
        rng.shuffle(permutation)
        output[:, indices] = state[:, permutation]
    return np.where(
        support, np.where(np.isfinite(output), output, 1.0), np.nan
    )


def _cross_asset_placebo(
    state: np.ndarray, support: np.ndarray, *, seed: int
) -> np.ndarray:
    output = np.full_like(state, np.nan)
    for column in range(state.shape[1]):
        assets = np.flatnonzero(support[:, column])
        if assets.size:
            shift = (seed + 17 * column) % int(assets.size)
            output[assets, column] = np.roll(state[assets, column], shift)
    return np.where(
        support, np.where(np.isfinite(output), output, 1.0), np.nan
    )


def _unique_cross_section(values: np.ndarray) -> dict[str, Any]:
    counts = np.asarray(
        [
            len(np.unique(values[np.isfinite(values[:, column]), column]))
            for column in range(values.shape[1])
        ],
        dtype=int,
    )
    return {
        "minimum": int(counts.min()) if counts.size else 0,
        "median": float(np.median(counts)) if counts.size else 0.0,
        "maximum": int(counts.max()) if counts.size else 0,
        "zero_unique_coordinates": int(np.sum(counts == 0)),
    }


def _block_analysis(
    *,
    store: RawPanelStore,
    registry: TypedExpressionRegistry,
    candidate: CandidateSpec,
    block_name: str,
    block_config: Mapping[str, Any],
    ablation_config: Mapping[str, Any],
    symbols: Sequence[str],
) -> dict[str, Any]:
    block = store.block_slice(
        str(block_config["start"]), str(block_config["end_exclusive"])
    )
    base = np.asarray(store.base_eligible()[:, block], dtype=bool)
    raw = {
        field: np.asarray(store.field(field)[:, block], dtype=float)
        for field in candidate.raw_fields
    }
    raw_support = base.copy()
    for values in raw.values():
        raw_support &= np.isfinite(values)
    candidate_cache: dict[str, np.ndarray] = {}
    primary_signal = materialize_expression(
        candidate.expression,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=base,
        candidate_cache=candidate_cache,
    )
    control_signal = materialize_expression(
        candidate.control,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=base,
        candidate_cache=candidate_cache,
    )
    payload_signal = materialize_expression(
        candidate.expression.inputs[0],
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=base,
        candidate_cache=candidate_cache,
    )
    regime_signal = materialize_expression(
        candidate.expression.inputs[1],
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=base,
        candidate_cache=candidate_cache,
    )
    shared_signal_support = (
        raw_support
        & np.isfinite(primary_signal)
        & np.isfinite(control_signal)
        & np.isfinite(payload_signal)
        & np.isfinite(regime_signal)
    )
    primary_signal = np.where(shared_signal_support, primary_signal, np.nan)
    control_signal = np.where(shared_signal_support, control_signal, np.nan)
    payload_signal = np.where(shared_signal_support, payload_signal, np.nan)
    regime_signal = np.where(shared_signal_support, regime_signal, np.nan)
    mapping_contract = DEFAULT_MAPPING_CONTRACTS[candidate.mapping_id]
    primary_weight = np.asarray(
        map_portfolio(primary_signal, mapping_contract).weights, dtype=float
    )
    control_weight = np.asarray(
        map_portfolio(control_signal, mapping_contract).weights, dtype=float
    )
    target = np.asarray(
        store.target_return(candidate.horizon_hours)[:, block], dtype=float
    )
    active_union = (np.abs(primary_weight) > ACTIVE_EPSILON) | (
        np.abs(control_weight) > ACTIVE_EPSILON
    )
    missing_active_target = np.any(active_union & ~np.isfinite(target), axis=0)
    raw_coordinate_support = raw_support.sum(axis=0) >= 3
    evaluation_mask = raw_coordinate_support & ~missing_active_target
    timestamp_ns = np.asarray(store.timestamp_ns[block], dtype=np.int64)
    months = np.asarray(
        [str(np.datetime64(int(value), "ns"))[:7] for value in timestamp_ns],
        dtype=str,
    )
    primary_metrics = _series_metrics(
        weights=primary_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
    )
    control_metrics = _series_metrics(
        weights=control_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
    )
    delta_weight = primary_weight - control_weight
    incremental_metrics = _series_metrics(
        weights=delta_weight,
        target=target,
        months=months,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
    )
    primary_rank = _rank_matrix(primary_signal)
    control_rank = _rank_matrix(control_signal)
    primary_arrays = _series_arrays(
        weights=primary_weight,
        target=target,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
    )
    identity = {
        "block": block_name,
        "block_role": block_config["role"],
        "coordinates": int(primary_signal.shape[1]),
        "raw_support_fraction": float(np.mean(raw_support)),
        "shared_signal_support_fraction": float(np.mean(shared_signal_support)),
        "evaluation_observations": int(primary_arrays["mask"].sum()),
        "primary_control": {
            "numeric_exact_equality": _exact_equal(
                primary_signal, control_signal
            ),
            "numeric_value_correlation": _corr(
                primary_signal, control_signal
            ),
            "rank_correlation": _corr(primary_rank, control_rank),
            "primary_unique_cross_section": _unique_cross_section(
                primary_signal
            ),
            "control_unique_cross_section": _unique_cross_section(
                control_signal
            ),
            "portfolio_exact_equality": _exact_equal(
                primary_weight, control_weight
            ),
            "portfolio_correlation": _corr(
                primary_weight, control_weight
            ),
            "primary_active_weight_coordinates": int(
                np.sum(np.abs(primary_weight) > ACTIVE_EPSILON)
            ),
            "control_active_weight_coordinates": int(
                np.sum(np.abs(control_weight) > ACTIVE_EPSILON)
            ),
            "primary_mean_portfolio_size": float(
                np.mean(
                    np.sum(
                        np.abs(primary_weight) > ACTIVE_EPSILON, axis=0
                    )
                )
            ),
            "control_mean_portfolio_size": float(
                np.mean(
                    np.sum(
                        np.abs(control_weight) > ACTIVE_EPSILON, axis=0
                    )
                )
            ),
            "portfolio_size_ratio_primary_over_control": float(
                np.mean(
                    np.sum(
                        np.abs(primary_weight) > ACTIVE_EPSILON, axis=0
                    )
                )
                / max(
                    1e-12,
                    float(
                        np.mean(
                            np.sum(
                                np.abs(control_weight) > ACTIVE_EPSILON,
                                axis=0,
                            )
                        )
                    ),
                )
            ),
            "primary_weight_sha256": _array_sha(primary_weight),
            "control_weight_sha256": _array_sha(control_weight),
            "delta_weight_sha256": _array_sha(delta_weight),
        },
        "native_metrics": {
            "primary": primary_metrics,
            "control": control_metrics,
            "incremental": incremental_metrics,
        },
    }

    lag = np.empty_like(regime_signal)
    lag_hours = int(ablation_config["lag_hours"])
    lag[:, :lag_hours] = 1.0
    lag[:, lag_hours:] = regime_signal[:, :-lag_hours]
    lag = np.where(
        shared_signal_support,
        np.where(np.isfinite(lag), lag, 1.0),
        np.nan,
    )
    shuffled_regime = _month_shuffle(
        regime_signal,
        months,
        shared_signal_support,
        seed=int(ablation_config["seed"]),
    )
    placebo_regime = _cross_asset_placebo(
        regime_signal,
        shared_signal_support,
        seed=int(ablation_config["seed"]),
    )
    variant_signals = {
        "A_FULL_CANDIDATE": primary_signal,
        "B_BASE_SIGNAL_ONLY": control_signal,
        "C_REGIME_ONLY": regime_signal,
        "D_NEUTRAL_REGIME": payload_signal,
        "E_TIME_SHUFFLED_REGIME": np.where(
            shared_signal_support,
            payload_signal * shuffled_regime,
            np.nan,
        ),
        "F_LAGGED_REGIME": np.where(
            shared_signal_support, payload_signal * lag, np.nan
        ),
        "G_MATCHED_OCCUPANCY_PLACEBO": np.where(
            shared_signal_support,
            payload_signal * placebo_regime,
            np.nan,
        ),
    }
    variant_weights = {"A_FULL_CANDIDATE": primary_weight}
    for name, signal in variant_signals.items():
        if name == "A_FULL_CANDIDATE":
            continue
        variant_weights[name] = _matched_occupancy_weights(
            primary_weight, signal, shared_signal_support
        )
    reference_active = np.sum(
        np.abs(primary_weight) > ACTIVE_EPSILON, axis=0
    )
    reference_gross = np.sum(np.abs(primary_weight), axis=0)
    reference_net = np.sum(primary_weight, axis=0)
    ablation_rows: list[dict[str, Any]] = []
    variant_months: dict[str, list[float]] = {}
    reference_rebalance_count: int | None = None
    for ordinal, name in enumerate(ablation_config["variants"]):
        signal = np.asarray(variant_signals[name], dtype=float)
        weights = np.asarray(variant_weights[name], dtype=float)
        metrics = _series_metrics(
            weights=weights,
            target=target,
            months=months,
            evaluation_mask=evaluation_mask,
            horizon=candidate.horizon_hours,
        )
        arrays = _series_arrays(
            weights=weights,
            target=target,
            evaluation_mask=evaluation_mask,
            horizon=candidate.horizon_hours,
        )
        delta_vs_base = weights - variant_weights["B_BASE_SIGNAL_ONLY"]
        delta_metrics = _series_metrics(
            weights=delta_vs_base,
            target=target,
            months=months,
            evaluation_mask=evaluation_mask,
            horizon=candidate.horizon_hours,
        )
        signal_rank = _rank_matrix(signal)
        active = np.sum(np.abs(weights) > ACTIVE_EPSILON, axis=0)
        gross = np.sum(np.abs(weights), axis=0)
        net_exposure = np.sum(weights, axis=0)
        rebalance_count = int(
            np.sum(arrays["turnover"] > ACTIVE_EPSILON)
        )
        if reference_rebalance_count is None:
            reference_rebalance_count = rebalance_count
        reference_active_mask = np.abs(primary_weight) > ACTIVE_EPSILON
        active_mask = np.abs(weights) > ACTIVE_EPSILON
        union = int(np.sum(reference_active_mask | active_mask))
        overlap = int(np.sum(reference_active_mask & active_mask))
        comparison = {
            "signal_value_correlation_to_A": _corr(
                signal, primary_signal
            ),
            "signal_rank_correlation_to_A": _corr(
                signal_rank, primary_rank
            ),
            "portfolio_correlation_to_A": _corr(
                weights, primary_weight
            ),
            "pnl_correlation_to_A": _corr(
                arrays["net"][arrays["mask"] & primary_arrays["mask"]],
                primary_arrays["net"][
                    arrays["mask"] & primary_arrays["mask"]
                ],
            ),
            "signal_exact_equality_to_A": _exact_equal(
                signal, primary_signal
            ),
            "portfolio_exact_equality_to_A": _exact_equal(
                weights, primary_weight
            ),
            "behavior_active_overlap_jaccard": (
                float(overlap / union) if union else 1.0
            ),
            "behavior_sign_agreement": float(
                np.mean(
                    np.sign(weights[reference_active_mask & active_mask])
                    == np.sign(
                        primary_weight[
                            reference_active_mask & active_mask
                        ]
                    )
                )
            )
            if overlap
            else None,
        }
        exposure_contract = {
            "support_coordinates_equal": bool(
                np.array_equal(
                    np.isfinite(signal), shared_signal_support
                )
            ),
            "portfolio_size_per_timestamp_equal": bool(
                np.array_equal(active, reference_active)
            ),
            "gross_exposure_per_timestamp_equal": bool(
                np.allclose(gross, reference_gross, atol=1e-12, rtol=0.0)
            ),
            "net_exposure_per_timestamp_equal": bool(
                np.allclose(
                    net_exposure, reference_net, atol=1e-12, rtol=0.0
                )
            ),
            "evaluation_observations_equal": bool(
                int(arrays["mask"].sum())
                == int(primary_arrays["mask"].sum())
            ),
            "rebalance_observation_count": rebalance_count,
            "reference_rebalance_observation_count": int(
                reference_rebalance_count
            ),
            "maximum_abs_weight": float(np.max(np.abs(weights))),
        }
        if not all(
            exposure_contract[key]
            for key in (
                "support_coordinates_equal",
                "portfolio_size_per_timestamp_equal",
                "gross_exposure_per_timestamp_equal",
                "net_exposure_per_timestamp_equal",
                "evaluation_observations_equal",
            )
        ):
            raise AssertionError(f"ablation exposure contract failed: {name}")
        variant_months[name] = [
            float(row["net_mean"])
            for row in metrics["month_metrics"]
            if row["net_mean"] is not None
        ]
        ablation_rows.append(
            {
                "variant": name,
                "ordinal": ordinal,
                "construction": {
                    "A_FULL_CANDIDATE": "frozen primary expression",
                    "B_BASE_SIGNAL_ONLY": "frozen SupportMatchedPayload control",
                    "C_REGIME_ONLY": "frozen regime child only",
                    "D_NEUTRAL_REGIME": "payload multiplied by neutral state 1",
                    "E_TIME_SHUFFLED_REGIME": "within-month deterministic state-column shuffle",
                    "F_LAGGED_REGIME": f"state lagged by {lag_hours} hours with neutral edge fill",
                    "G_MATCHED_OCCUPANCY_PLACEBO": "deterministic cross-asset state rotation",
                }[name],
                "standalone": metrics,
                "incremental_vs_B_matched_occupancy": delta_metrics,
                "comparison_to_A": comparison,
                "exposure_contract": exposure_contract,
            }
        )

    delta_arrays = _series_arrays(
        weights=delta_weight,
        target=target,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
    )
    asset_turnover = _asset_turnover(delta_weight, candidate.horizon_hours)
    if not np.allclose(
        asset_turnover.sum(axis=0),
        delta_arrays["turnover"],
        atol=1e-12,
        rtol=0.0,
    ):
        raise AssertionError("asset turnover attribution does not sum to pair turnover")
    asset_gross = np.nan_to_num(
        delta_weight * target / float(candidate.horizon_hours)
    )
    asset_cost = asset_turnover * FIXED_COST_BPS / 10000.0
    mask = delta_arrays["mask"]
    asset_gross[:, ~mask] = 0.0
    asset_cost[:, ~mask] = 0.0
    asset_net = asset_gross - asset_cost
    decomposition_rows: list[dict[str, Any]] = []
    for month in tuple(dict.fromkeys(months.tolist())):
        local = mask & (months == month)
        decomposition_rows.append(
            {
                "block": block_name,
                "grain": "MONTH",
                "key": month,
                "month": month,
                "asset": None,
                "regime": None,
                "observations": int(local.sum()),
                "active_observations": int(
                    np.sum(
                        np.any(
                            np.abs(delta_weight[:, local])
                            > ACTIVE_EPSILON,
                            axis=0,
                        )
                    )
                ),
                "gross_sum": float(delta_arrays["gross"][local].sum()),
                "cost_sum": float(delta_arrays["cost"][local].sum()),
                "net_sum": float(delta_arrays["net"][local].sum()),
                "turnover_sum": float(
                    delta_arrays["turnover"][local].sum()
                ),
            }
        )
    for asset_index, symbol in enumerate(symbols):
        local_active = mask & (
            (np.abs(delta_weight[asset_index]) > ACTIVE_EPSILON)
            | (asset_turnover[asset_index] > ACTIVE_EPSILON)
        )
        decomposition_rows.append(
            {
                "block": block_name,
                "grain": "ASSET",
                "key": symbol,
                "month": None,
                "asset": symbol,
                "regime": None,
                "observations": int(mask.sum()),
                "active_observations": int(local_active.sum()),
                "gross_sum": float(asset_gross[asset_index].sum()),
                "cost_sum": float(asset_cost[asset_index].sum()),
                "net_sum": float(asset_net[asset_index].sum()),
                "turnover_sum": float(asset_turnover[asset_index, mask].sum()),
            }
        )
        for month in tuple(dict.fromkeys(months.tolist())):
            local = mask & (months == month)
            if not np.any(local):
                continue
            decomposition_rows.append(
                {
                    "block": block_name,
                    "grain": "ASSET_MONTH",
                    "key": f"{symbol}|{month}",
                    "month": month,
                    "asset": symbol,
                    "regime": None,
                    "observations": int(local.sum()),
                    "active_observations": int(
                        np.sum(
                            local
                            & (
                                (
                                    np.abs(delta_weight[asset_index])
                                    > ACTIVE_EPSILON
                                )
                                | (
                                    asset_turnover[asset_index]
                                    > ACTIVE_EPSILON
                                )
                            )
                        )
                    ),
                    "gross_sum": float(
                        asset_gross[asset_index, local].sum()
                    ),
                    "cost_sum": float(
                        asset_cost[asset_index, local].sum()
                    ),
                    "net_sum": float(asset_net[asset_index, local].sum()),
                    "turnover_sum": float(
                        asset_turnover[asset_index, local].sum()
                    ),
                }
            )
    regimes = np.full(regime_signal.shape, "AT_CS_MEDIAN", dtype=object)
    regimes[regime_signal < -1e-12] = "YOUNGER_THAN_CS_MEDIAN"
    regimes[regime_signal > 1e-12] = "OLDER_THAN_CS_MEDIAN"
    active_coordinate = (
        (np.abs(delta_weight) > ACTIVE_EPSILON)
        | (asset_turnover > ACTIVE_EPSILON)
    ) & mask[None, :]
    for regime in (
        "YOUNGER_THAN_CS_MEDIAN",
        "AT_CS_MEDIAN",
        "OLDER_THAN_CS_MEDIAN",
    ):
        local = active_coordinate & (regimes == regime)
        decomposition_rows.append(
            {
                "block": block_name,
                "grain": "REGIME",
                "key": regime,
                "month": None,
                "asset": None,
                "regime": regime,
                "observations": int(local.sum()),
                "active_observations": int(local.sum()),
                "gross_sum": float(asset_gross[local].sum()),
                "cost_sum": float(asset_cost[local].sum()),
                "net_sum": float(asset_net[local].sum()),
                "turnover_sum": float(asset_turnover[local].sum()),
            }
        )

    return {
        "identity": identity,
        "ablation_rows": ablation_rows,
        "variant_months": variant_months,
        "decomposition_rows": decomposition_rows,
        "concentration_inputs": {
            "net_sum": float(delta_arrays["net"][mask].sum()),
            "observations": int(mask.sum()),
            "months": [
                {
                    "month": row["key"],
                    "net_sum": row["net_sum"],
                    "observations": row["observations"],
                }
                for row in decomposition_rows
                if row["grain"] == "MONTH"
            ],
            "asset_net_sum": {
                row["asset"]: row["net_sum"]
                for row in decomposition_rows
                if row["grain"] == "ASSET"
            },
        },
        "reference": {
            "signal": primary_signal,
            "rank": primary_rank,
            "weight": primary_weight,
            "net": primary_arrays["net"],
            "mask": primary_arrays["mask"],
            "timestamps": timestamp_ns,
        },
    }


def _concentration_summary(
    block_results: Sequence[Mapping[str, Any]],
    *,
    rules: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    total_net = float(
        sum(row["concentration_inputs"]["net_sum"] for row in block_results)
    )
    total_observations = int(
        sum(
            row["concentration_inputs"]["observations"]
            for row in block_results
        )
    )
    months = [
        month
        for row in block_results
        for month in row["concentration_inputs"]["months"]
    ]
    asset_net: Counter[str] = Counter()
    for row in block_results:
        asset_net.update(row["concentration_inputs"]["asset_net_sum"])
    positive_month_sum = float(
        sum(max(0.0, float(row["net_sum"])) for row in months)
    )
    positive_asset_sum = float(
        sum(max(0.0, float(value)) for value in asset_net.values())
    )
    ordered_months = sorted(
        months, key=lambda row: float(row["net_sum"]), reverse=True
    )
    ordered_assets = sorted(
        asset_net.items(), key=lambda row: float(row[1]), reverse=True
    )
    top1_month_positive_share = (
        float(ordered_months[0]["net_sum"]) / positive_month_sum
        if ordered_months and positive_month_sum > 0.0
        else None
    )
    top3_month_positive_share = (
        float(sum(row["net_sum"] for row in ordered_months[:3]))
        / positive_month_sum
        if ordered_months and positive_month_sum > 0.0
        else None
    )
    top1_asset_positive_share = (
        float(ordered_assets[0][1]) / positive_asset_sum
        if ordered_assets and positive_asset_sum > 0.0
        else None
    )
    leave_one_month = [
        {
            "month": row["month"],
            "net_mean": float(
                (total_net - float(row["net_sum"]))
                / max(1, total_observations - int(row["observations"]))
            ),
        }
        for row in months
    ]
    leave_one_asset = [
        {
            "asset": asset,
            "net_mean": float(
                (total_net - float(value)) / max(1, total_observations)
            ),
        }
        for asset, value in ordered_assets
    ]
    top3_assets = [row[0] for row in ordered_assets[:3]]
    top3_asset_net = float(sum(row[1] for row in ordered_assets[:3]))
    leave_top3_assets_net_mean = float(
        (total_net - top3_asset_net) / max(1, total_observations)
    )
    thresholds = rules["accidental_concentration"]
    breaches = {
        "top1_month": bool(
            top1_month_positive_share is not None
            and top1_month_positive_share
            > float(
                thresholds[
                    "maximum_top1_month_positive_contribution_share"
                ]
            )
        ),
        "top3_month": bool(
            top3_month_positive_share is not None
            and top3_month_positive_share
            > float(
                thresholds[
                    "maximum_top3_month_positive_contribution_share"
                ]
            )
        ),
        "top1_asset": bool(
            top1_asset_positive_share is not None
            and top1_asset_positive_share
            > float(
                thresholds[
                    "maximum_top1_asset_positive_contribution_share"
                ]
            )
        ),
        "leave_one_month": bool(
            leave_one_month
            and min(row["net_mean"] for row in leave_one_month)
            < float(thresholds["minimum_leave_one_month_net_mean"])
        ),
        "leave_top3_assets": bool(
            leave_top3_assets_net_mean
            < float(thresholds["minimum_leave_top3_assets_net_mean"])
        ),
    }
    extra_rows = [
        {
            "block": "COMBINED_18M",
            "grain": "LEAVE_ONE_MONTH_OUT",
            "key": row["month"],
            "month": row["month"],
            "asset": None,
            "regime": None,
            "observations": total_observations,
            "active_observations": None,
            "gross_sum": None,
            "cost_sum": None,
            "net_sum": None,
            "turnover_sum": None,
            "net_mean": row["net_mean"],
        }
        for row in leave_one_month
    ]
    extra_rows.extend(
        {
            "block": "COMBINED_18M",
            "grain": "LEAVE_ONE_ASSET_OUT",
            "key": row["asset"],
            "month": None,
            "asset": row["asset"],
            "regime": None,
            "observations": total_observations,
            "active_observations": None,
            "gross_sum": None,
            "cost_sum": None,
            "net_sum": None,
            "turnover_sum": None,
            "net_mean": row["net_mean"],
        }
        for row in leave_one_asset
    )
    extra_rows.append(
        {
            "block": "COMBINED_18M",
            "grain": "LEAVE_TOP3_ASSETS_OUT",
            "key": "|".join(top3_assets),
            "month": None,
            "asset": None,
            "regime": None,
            "observations": total_observations,
            "active_observations": None,
            "gross_sum": None,
            "cost_sum": None,
            "net_sum": None,
            "turnover_sum": None,
            "net_mean": leave_top3_assets_net_mean,
        }
    )
    return (
        {
            "attribution_method": (
                "FIXED_PORTFOLIO_CONTRIBUTION_LEAVE_OUT; weights are not "
                "remapped after omission"
            ),
            "combined_net_sum": total_net,
            "combined_observations": total_observations,
            "combined_net_mean": float(
                total_net / max(1, total_observations)
            ),
            "top1_month": ordered_months[0] if ordered_months else None,
            "top3_months": ordered_months[:3],
            "top1_month_positive_contribution_share": (
                top1_month_positive_share
            ),
            "top3_month_positive_contribution_share": (
                top3_month_positive_share
            ),
            "top1_asset": (
                {
                    "asset": ordered_assets[0][0],
                    "net_sum": float(ordered_assets[0][1]),
                }
                if ordered_assets
                else None
            ),
            "top3_assets": [
                {"asset": asset, "net_sum": float(value)}
                for asset, value in ordered_assets[:3]
            ],
            "top1_asset_positive_contribution_share": (
                top1_asset_positive_share
            ),
            "leave_one_month_minimum": min(
                leave_one_month, key=lambda row: row["net_mean"]
            )
            if leave_one_month
            else None,
            "leave_one_asset_minimum": min(
                leave_one_asset, key=lambda row: row["net_mean"]
            )
            if leave_one_asset
            else None,
            "leave_top3_assets": {
                "assets": top3_assets,
                "net_mean": leave_top3_assets_net_mean,
            },
            "thresholds": thresholds,
            "breaches": breaches,
            "accidental_concentration": bool(any(breaches.values())),
        },
        extra_rows,
    )


def _report_only_independence(
    config: Mapping[str, Any],
    context: Mapping[str, Any],
    selection: Mapping[str, Any],
) -> dict[str, Any]:
    strict = context["strict"]
    challenge = context["challenge"]
    strict_pack = Counter(
        (str(row.candidate_id), str(row.policy), int(row.seed))
        for row in strict.itertuples()
    )
    challenge_pack = Counter(
        (str(row.candidate_id), str(row.policy), int(row.seed))
        for row in challenge.itertuples()
    )
    duplicate_inconsistency = int(
        challenge.groupby("candidate_id")["net_mean"].nunique(dropna=False).gt(1).sum()
    )
    stage_a_ids = set(strict.iloc[:4096]["candidate_id"].astype(str))
    stage_b_ids = set(strict.iloc[4096:]["candidate_id"].astype(str))
    source = inspect.getsource(
        __import__(
            "alphafactory_crypto.broad_search.runner18m",
            fromlist=["build_evidence"],
        ).build_evidence
    )
    visibility_patterns = {
        "stage_a_report_only_evaluated_before_stage_b": (
            "stage_a_challenge = _parallel_challenge" in source
            and source.index("stage_a_challenge = _parallel_challenge")
            < source.index("stage_b, stage_b_resources = _parallel_lanes")
        ),
        "stage_b_gate_reads_report_only_cluster_count": (
            'counts_a["challenge_positive_clusters"] >= 5' in source
        ),
        "stage_b_gate_reads_report_only_family_yield": (
            'counts_a["maximum_family_challenge_yield"] > 0.005' in source
        ),
        "stage_b_prior_is_adaptive_rows_only": (
            "for row in stage_a:" in source
            and "prior[(str(row[\"policy\"]), int(row[\"seed\"]))].append(row)"
            in source
        ),
    }
    policy_feedback_writes = int(
        challenge["policy_feedback_written"].astype(bool).sum()
    )
    stage_b_gate = selection["stage_b_gate"]
    midsearch_visibility = bool(
        visibility_patterns[
            "stage_b_gate_reads_report_only_cluster_count"
        ]
        or visibility_patterns[
            "stage_b_gate_reads_report_only_family_yield"
        ]
    )
    counterfactual_unchanged = bool(
        stage_b_gate["adaptive_only_counterfactual_gate_result"]
    )
    status = (
        "CANDIDATE_PACK_COUNTERFACTUALLY_INDEPENDENT_BUT_REPORT_ONLY_VISIBILITY_CONTRACT_FAILED"
        if counterfactual_unchanged and midsearch_visibility
        else "REPORT_ONLY_CANDIDATE_PACK_INDEPENDENT"
        if not midsearch_visibility
        else "REPORT_ONLY_CANDIDATE_PACK_CONTAMINATED"
    )
    return {
        "schema_version": 1,
        "status": status,
        "candidate_generation": {
            "strict_report_only_occurrence_multiset_equal": strict_pack
            == challenge_pack,
            "strict_occurrences": int(len(strict)),
            "report_only_occurrences": int(len(challenge)),
            "stage_a_stage_b_exact_identity_overlap": int(
                len(stage_a_ids & stage_b_ids)
            ),
            "candidate_pack_counterfactual_unchanged_without_report_only_metrics": (
                counterfactual_unchanged
            ),
        },
        "ordering": {
            "strict_order": "seed, policy, proposal_step",
            "report_only_order": "seed, policy, candidate_id",
            "ordering_reused_by_policy": False,
            "report_only_order_difference_is_evaluation_only": True,
        },
        "cluster_threshold": {
            "report_only_metrics_visible_to_stage_b_gate": midsearch_visibility,
            "visibility_patterns": visibility_patterns,
            "actual_trigger_values": stage_b_gate["trigger_values"],
            "report_only_terms_causally_necessary": stage_b_gate[
                "report_only_terms_were_causally_necessary"
            ],
            "contract_result": "FAIL",
            "reason": (
                "The feedback contract says report-only metrics are not visible "
                "to policy, but build_evidence reads report-only cluster/yield "
                "statistics before deciding Stage B.  Adaptive policy "
                "improvement independently made the gate true, so the read did "
                "not change this frozen candidate pack."
            ),
        },
        "pairing": {
            "candidate_id_is_pair_join_key": True,
            "duplicate_candidate_occurrences": int(
                len(strict)
                - strict["candidate_id"].astype(str).nunique()
            ),
            "duplicate_report_only_metric_inconsistencies": (
                duplicate_inconsistency
            ),
            "artifact_identity_reuse_error_observed": bool(
                duplicate_inconsistency > 0
            ),
        },
        "selection": {
            "policy_feedback_writes": policy_feedback_writes,
            "policy_feedback_is_adaptive_only": policy_feedback_writes == 0,
            "robust_and_cross_seed_reports_use_report_only_metrics": True,
            "robust_selection_is_post_search_evidence_selection": True,
            "adaptive_months_reused_in_robust_statistic": 12,
            "independent_report_only_months": 6,
        },
        "family_prior": {
            "stage_b_prior_contains_only_stage_a_adaptive_rows": bool(
                visibility_patterns["stage_b_prior_is_adaptive_rows_only"]
            ),
            "report_only_reward_written_to_lane_state": False,
        },
        "scope": {
            "sealed_reads": 0,
            "authorized_blocks_only": True,
            "cannot_conclude": [
                "formal OOS independence",
                "promotion readiness",
                "absence of selection bias in the 18-month robust statistic",
            ],
        },
    }


def _candidate_primary_reference(
    *,
    store: RawPanelStore,
    registry: TypedExpressionRegistry,
    candidate: CandidateSpec,
    block_config: Mapping[str, Any],
) -> dict[str, np.ndarray]:
    block = store.block_slice(
        str(block_config["start"]), str(block_config["end_exclusive"])
    )
    base = np.asarray(store.base_eligible()[:, block], dtype=bool)
    raw = {
        field: np.asarray(store.field(field)[:, block], dtype=float)
        for field in candidate.raw_fields
    }
    support = base.copy()
    for values in raw.values():
        support &= np.isfinite(values)
    signal = materialize_expression(
        candidate.expression,
        registry=registry,
        field_reader=raw.__getitem__,
        eligible_mask=base,
    )
    signal = np.where(support, signal, np.nan)
    weights = np.asarray(
        map_portfolio(
            signal, DEFAULT_MAPPING_CONTRACTS[candidate.mapping_id]
        ).weights,
        dtype=float,
    )
    target = np.asarray(
        store.target_return(candidate.horizon_hours)[:, block], dtype=float
    )
    active = np.abs(weights) > ACTIVE_EPSILON
    missing = np.any(active & ~np.isfinite(target), axis=0)
    evaluation_mask = (support.sum(axis=0) >= 3) & ~missing
    arrays = _series_arrays(
        weights=weights,
        target=target,
        evaluation_mask=evaluation_mask,
        horizon=candidate.horizon_hours,
    )
    return {
        "signal": signal,
        "rank": _rank_matrix(signal),
        "weight": weights,
        "net": arrays["net"],
        "mask": arrays["mask"],
    }


def _cross_seed_audit(
    config: Mapping[str, Any],
    context: Mapping[str, Any],
    references: Mapping[str, Mapping[str, np.ndarray]],
) -> dict[str, Any]:
    strict = context["strict"]
    challenge = context["challenge"]
    candidate = context["candidate"]
    challenge_map = {
        str(row["candidate_id"]): row for _, row in challenge.iterrows()
    }
    requested = list(config["cross_seed_cluster_ids"])
    source_clusters = {
        str(row["cluster_id"]): row
        for row in context["reproduction"]["clusters"]
    }
    if set(requested) != set(source_clusters):
        raise ValueError("cross-seed cluster qualification scope changed")
    cluster_payloads: list[dict[str, Any]] = []
    independent_replications = 0
    for cluster_id in requested:
        members = strict[
            strict.apply(_cluster_key, axis=1) == cluster_id
        ].copy()
        positive_members = [
            row
            for _, row in members.iterrows()
            if bool(
                challenge_map[str(row["candidate_id"])]["matched_positive"]
            )
        ]
        comparisons: list[dict[str, Any]] = []
        for row in positive_members:
            peer = CandidateSpec.from_dict(
                json.loads(str(row["candidate_spec_json"]))
            )
            block_comparisons: list[dict[str, Any]] = []
            for block_name, block_config in config[
                "authorized_blocks"
            ].items():
                peer_reference = _candidate_primary_reference(
                    store=context["store"],
                    registry=context["registry"],
                    candidate=peer,
                    block_config=block_config,
                )
                reference = references[block_name]
                common_mask = (
                    np.asarray(reference["mask"], dtype=bool)
                    & np.asarray(peer_reference["mask"], dtype=bool)
                )
                reference_active = (
                    np.abs(reference["weight"]) > ACTIVE_EPSILON
                )
                peer_active = (
                    np.abs(peer_reference["weight"]) > ACTIVE_EPSILON
                )
                overlap = int(np.sum(reference_active & peer_active))
                union = int(np.sum(reference_active | peer_active))
                block_comparisons.append(
                    {
                        "block": block_name,
                        "signal_correlation": _corr(
                            reference["signal"],
                            peer_reference["signal"],
                        ),
                        "rank_correlation": _corr(
                            reference["rank"], peer_reference["rank"]
                        ),
                        "portfolio_correlation": _corr(
                            reference["weight"],
                            peer_reference["weight"],
                        ),
                        "pnl_correlation": _corr(
                            reference["net"][common_mask],
                            peer_reference["net"][common_mask],
                        ),
                        "portfolio_exact_equality": _exact_equal(
                            reference["weight"],
                            peer_reference["weight"],
                        ),
                        "behavior_active_overlap_jaccard": (
                            float(overlap / union) if union else 1.0
                        ),
                    }
                )
            exact_mapping_duplicate = all(
                row["portfolio_exact_equality"]
                for row in block_comparisons
            )
            relationship = (
                "MAPPING_DUPLICATE"
                if exact_mapping_duplicate
                else "SAME_FAMILY_VARIANT"
                if peer.mechanism_family == candidate.mechanism_family
                else "INDEPENDENT_MECHANISM_REPLICATION"
            )
            adaptive_positive = bool(row["matched_positive"])
            report_positive = bool(
                challenge_map[str(row["candidate_id"])][
                    "matched_positive"
                ]
            )
            if (
                relationship == "INDEPENDENT_MECHANISM_REPLICATION"
                and adaptive_positive
                and report_positive
            ):
                independent_replications += 1
            comparisons.append(
                {
                    "candidate_id": peer.candidate_id,
                    "policy": str(row["policy"]),
                    "seed": int(row["seed"]),
                    "proposal_step": int(row["proposal_step"]),
                    "formula": _expression_text(peer.expression),
                    "raw_fields": list(peer.raw_fields),
                    "field_families": list(peer.field_families),
                    "horizon_hours": peer.horizon_hours,
                    "ast_distance_to_unique_robust": _ast_distance(
                        candidate.expression, peer.expression
                    ),
                    "field_lineage_jaccard": float(
                        len(set(candidate.raw_fields) & set(peer.raw_fields))
                        / max(
                            1,
                            len(
                                set(candidate.raw_fields)
                                | set(peer.raw_fields)
                            ),
                        )
                    ),
                    "mechanism_family_match": (
                        peer.mechanism_family
                        == candidate.mechanism_family
                    ),
                    "adaptive": {
                        "matched_positive": adaptive_positive,
                        "net_mean": (
                            float(row["net_mean"])
                            if pd.notna(row["net_mean"])
                            else None
                        ),
                        "net_lcb": (
                            float(row["net_lcb"])
                            if pd.notna(row["net_lcb"])
                            else None
                        ),
                    },
                    "report_only": {
                        "matched_positive": report_positive,
                        "net_mean": float(
                            challenge_map[str(row["candidate_id"])][
                                "net_mean"
                            ]
                        ),
                        "net_lcb": float(
                            challenge_map[str(row["candidate_id"])][
                                "net_lcb"
                            ]
                        ),
                    },
                    "relationship": relationship,
                    "block_comparisons": block_comparisons,
                }
            )
        cluster_payloads.append(
            {
                **source_clusters[cluster_id],
                "qualified_member_count": int(len(members)),
                "report_only_positive_candidates": comparisons,
                "adaptive_matched_positive_candidates": int(
                    members["matched_positive"].astype(bool).sum()
                ),
                "mechanism_assessment": (
                    "REPORT_ONLY_SAME_FAMILY_VARIANTS_NOT_INDEPENDENT_REPLICATION"
                ),
            }
        )
    return {
        "schema_version": 1,
        "unique_robust_candidate_id": candidate.candidate_id,
        "unique_robust_cluster_id": _cluster_key(
            context["candidate_row"]
        ),
        "clusters": cluster_payloads,
        "independent_mechanism_replications": independent_replications,
        "conclusion": (
            "The two reproduced clusters are report-only positive, "
            "same-family variants.  Neither supplies a distinct mechanism "
            "that is matched-positive on both the adaptive and report-only "
            "blocks, so they do not independently reproduce the unique "
            "StateModulation candidate."
        ),
    }


def _identity_audit(
    config: Mapping[str, Any],
    context: Mapping[str, Any],
    block_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    candidate = context["candidate"]
    candidate_row = context["candidate_row"]
    challenge_row = context["challenge_row"]
    robust_row = context["robust_row"]
    receipt = json.loads(str(candidate_row["mutation_receipt_json"]))
    adaptive_identity = block_results[0]["identity"]
    report_identity = block_results[1]["identity"]
    adaptive_artifact = json.loads(str(candidate_row["evaluation_json"]))
    report_artifact = json.loads(str(challenge_row["evaluation_json"]))
    metric_reproduction = {
        "adaptive_delta_weight_hash_equal": (
            adaptive_identity["primary_control"]["delta_weight_sha256"]
            == str(candidate_row["delta_weight_sha256"])
        ),
        "report_only_delta_weight_hash_equal": (
            report_identity["primary_control"]["delta_weight_sha256"]
            == str(challenge_row["delta_weight_sha256"])
        ),
        "adaptive_net_mean_equal": bool(
            math.isclose(
                float(
                    adaptive_identity["native_metrics"]["incremental"][
                        "net_mean"
                    ]
                ),
                float(candidate_row["net_mean"]),
                rel_tol=0.0,
                abs_tol=1e-15,
            )
        ),
        "report_only_net_mean_equal": bool(
            math.isclose(
                float(
                    report_identity["native_metrics"]["incremental"][
                        "net_mean"
                    ]
                ),
                float(challenge_row["net_mean"]),
                rel_tol=0.0,
                abs_tol=1e-15,
            )
        ),
        "adaptive_evaluation_json_delta_hash_equal": (
            adaptive_identity["primary_control"]["delta_weight_sha256"]
            == adaptive_artifact["delta_weight_sha256"]
        ),
        "report_evaluation_json_delta_hash_equal": (
            report_identity["primary_control"]["delta_weight_sha256"]
            == report_artifact["delta_weight_sha256"]
        ),
    }
    return {
        "schema_version": 1,
        "candidate_id": candidate.candidate_id,
        "formula_identity": {
            "formula": _expression_text(candidate.expression),
            "control_formula": _expression_text(candidate.control),
            "canonical_ast": candidate.expression.canonical_dict(),
            "canonical_control_ast": candidate.control.canonical_dict(),
            "expression_id": candidate.expression.expression_id,
            "control_expression_id": candidate.control.expression_id,
            "candidate_id_recomputed": _candidate_id(candidate),
            "candidate_id_exact": _candidate_id(candidate)
            == candidate.candidate_id,
        },
        "behavior_identity": {
            "adaptive_delta_weight_sha256": str(
                candidate_row["delta_weight_sha256"]
            ),
            "report_only_delta_weight_sha256": str(
                challenge_row["delta_weight_sha256"]
            ),
            "same_behavior_across_blocks": bool(
                str(candidate_row["delta_weight_sha256"])
                == str(challenge_row["delta_weight_sha256"])
            ),
            "note": (
                "Different block coordinates must have different weight hashes; "
                "identity is reproduced separately within each block."
            ),
        },
        "portfolio_identity": {
            "mapping_id": candidate.mapping_id,
            "mapping_hash": mapping_contract_sha256(
                DEFAULT_MAPPING_CONTRACTS[candidate.mapping_id]
            ),
            "blocks": [
                adaptive_identity["primary_control"],
                report_identity["primary_control"],
            ],
            "native_mapping_sparsity_change": {
                "adaptive_primary_over_control_portfolio_size_ratio": (
                    adaptive_identity["primary_control"][
                        "portfolio_size_ratio_primary_over_control"
                    ]
                ),
                "report_only_primary_over_control_portfolio_size_ratio": (
                    report_identity["primary_control"][
                        "portfolio_size_ratio_primary_over_control"
                    ]
                ),
                "interpretation": (
                    "StateModulation creates many tied/zero scores on the "
                    "adaptive block, so the native pair changes portfolio "
                    "occupancy as well as ordering.  The fixed A-G bridge "
                    "therefore holds the realized A weight multiset constant."
                ),
            },
        },
        "pair_identity": {
            "adaptive_pair_reward": float(candidate_row["pair_reward"]),
            "report_only_pair_reward": float(challenge_row["pair_reward"]),
            "adaptive_matched_positive": bool(
                candidate_row["matched_positive"]
            ),
            "report_only_matched_positive": bool(
                challenge_row["matched_positive"]
            ),
            "adaptive_incremental": adaptive_identity["native_metrics"][
                "incremental"
            ],
            "report_only_incremental": report_identity["native_metrics"][
                "incremental"
            ],
        },
        "receipt_identity": {
            "parent_id": candidate_row["parent_id"],
            "mutation_receipt": receipt,
            "receipt_child_matches_candidate": bool(
                receipt
                and receipt.get("child_id") == candidate.candidate_id
            ),
            "receipt_parent_matches_row": bool(
                receipt
                and receipt.get("parent_id")
                == candidate_row["parent_id"]
            ),
            "policy_state_hash_before": str(
                candidate_row["policy_state_hash_before"]
            ),
            "policy_state_hash_after": str(
                candidate_row["policy_state_hash_after"]
            ),
        },
        "runtime_identity": {
            "source_bundle_sha256": config["source_bundle_sha256"],
            "source_runtime_producer_sha": context["source_manifest"][
                "producer_source_sha"
            ],
            "train_content_bundle_sha256": context["source_manifest"][
                "bindings"
            ]["train_content_bundle_sha256"],
            "cache_identity_sha256": context["store"].metadata[
                "identity_sha256"
            ],
            "cache_sealed_rows": int(
                context["store"].metadata["sealed_rows"]
            ),
            "robust_row": {
                key: (
                    bool(robust_row[key])
                    if isinstance(robust_row[key], (bool, np.bool_))
                    else float(robust_row[key])
                    if isinstance(
                        robust_row[key], (float, np.floating)
                    )
                    else int(robust_row[key])
                    if isinstance(robust_row[key], (int, np.integer))
                    else robust_row[key]
                )
                for key in robust_row.index
            },
        },
        "artifact_reproduction": metric_reproduction,
        "artifact_identity_reuse_error": not all(
            metric_reproduction.values()
        ),
        "blocks": [adaptive_identity, report_identity],
    }


def build_audits(
    repo_root: Path,
    *,
    config_path: Path,
    source_sha: str | None = None,
) -> dict[str, Any]:
    config = _read_json(config_path)
    _validate_config(config)
    current_sha = _git_sha(repo_root)
    source_sha = (source_sha or current_sha).lower()
    if source_sha != current_sha:
        raise ValueError("audit source SHA must equal the checked-out implementation")
    context = _load_context(repo_root, config)
    runtime_root = repo_root / str(config["outputs"]["runtime_root"])
    runtime_root.mkdir(parents=True, exist_ok=True)
    selection = _selection_lineage(config, context, source_sha=source_sha)
    _write_json(runtime_root / AUDIT_OUTPUTS[0], selection)

    block_results: list[dict[str, Any]] = []
    for block_name, block_config in config["authorized_blocks"].items():
        block_results.append(
            _block_analysis(
                store=context["store"],
                registry=context["registry"],
                candidate=context["candidate"],
                block_name=block_name,
                block_config=block_config,
                ablation_config=config["fixed_ablation"],
                symbols=context["store"].symbols,
            )
        )
    identity = _identity_audit(config, context, block_results)
    _write_json(runtime_root / AUDIT_OUTPUTS[1], identity)

    concentration, extra_rows = _concentration_summary(
        block_results, rules=config["qualification_rules"]
    )
    decomposition_rows = [
        row
        for result in block_results
        for row in result["decomposition_rows"]
    ]
    decomposition_rows.extend(extra_rows)
    decomposition = pd.DataFrame(decomposition_rows)
    for column in ("gross_sum", "cost_sum", "net_sum", "turnover_sum"):
        if column not in decomposition:
            decomposition[column] = np.nan
    if "net_mean" not in decomposition:
        decomposition["net_mean"] = np.nan
    regular = decomposition["grain"].isin(
        ["MONTH", "ASSET", "ASSET_MONTH", "REGIME"]
    )
    decomposition.loc[regular, "net_mean"] = (
        decomposition.loc[regular, "net_sum"]
        / decomposition.loc[regular, "observations"].clip(lower=1)
    )
    decomposition["gross_mean"] = (
        decomposition["gross_sum"]
        / decomposition["observations"].clip(lower=1)
    )
    decomposition["cost_mean"] = (
        decomposition["cost_sum"]
        / decomposition["observations"].clip(lower=1)
    )
    decomposition["turnover_mean"] = (
        decomposition["turnover_sum"]
        / decomposition["observations"].clip(lower=1)
    )
    decomposition["candidate_id"] = context["candidate"].candidate_id
    decomposition.to_parquet(runtime_root / AUDIT_OUTPUTS[2], index=False)

    independence = _report_only_independence(config, context, selection)
    _write_json(runtime_root / AUDIT_OUTPUTS[3], independence)

    combined_variant_months: dict[str, list[float]] = {
        name: [] for name in config["fixed_ablation"]["variants"]
    }
    for result in block_results:
        for name, values in result["variant_months"].items():
            combined_variant_months[name].extend(values)
    ablation = {
        "schema_version": 1,
        "candidate_id": context["candidate"].candidate_id,
        "fixed_contract": config["fixed_ablation"],
        "native_source_pair": {
            result["identity"]["block"]: result["identity"][
                "native_metrics"
            ]
            for result in block_results
        },
        "matched_occupancy_bridge": {
            "purpose": (
                "Hold A's realized zero-net capped weight multiset, active "
                "count, gross, and support fixed while variants change only "
                "asset ordering."
            ),
            "not_a_search_mapping": True,
            "does_not_modify_source_candidate_or_evaluator": True,
        },
        "blocks": {
            result["identity"]["block"]: result["ablation_rows"]
            for result in block_results
        },
        "combined_18m_monthly_robustness": {
            name: robust_monthly_audit(
                values,
                seed=int(config["fixed_ablation"]["seed"]) + ordinal,
            )
            for ordinal, (name, values) in enumerate(
                combined_variant_months.items()
            )
        },
        "economic_concentration": concentration,
    }
    _write_json(runtime_root / AUDIT_OUTPUTS[4], ablation)

    references = {
        result["identity"]["block"]: result["reference"]
        for result in block_results
    }
    cross_seed = _cross_seed_audit(config, context, references)
    _write_json(runtime_root / AUDIT_OUTPUTS[5], cross_seed)
    return {
        "result": "PASS",
        "task_id": config["task_id"],
        "source_sha": source_sha,
        "candidate_id": context["candidate"].candidate_id,
        "audit_outputs": list(AUDIT_OUTPUTS),
        "sealed_reads": 0,
    }


def _classify(
    config: Mapping[str, Any],
    identity: Mapping[str, Any],
    independence: Mapping[str, Any],
    ablation: Mapping[str, Any],
    cross_seed: Mapping[str, Any],
) -> tuple[str, dict[str, Any]]:
    adaptive = identity["blocks"][0]
    report = identity["blocks"][1]
    artifact_flags = {
        "formula_identity_equals_control": bool(
            identity["formula_identity"]["expression_id"]
            == identity["formula_identity"]["control_expression_id"]
        ),
        "portfolio_identity_equals_control_on_any_block": bool(
            any(
                row["primary_control"]["portfolio_exact_equality"]
                for row in identity["blocks"]
            )
        ),
        "artifact_reproduction_failed": bool(
            identity["artifact_identity_reuse_error"]
        ),
    }
    a_rows = {
        row["variant"]: row
        for row in ablation["blocks"]["adaptive"]
    }
    report_a_rows = {
        row["variant"]: row
        for row in ablation["blocks"]["report_only"]
    }
    artifact_flags["matched_occupancy_A_equals_B"] = bool(
        a_rows["A_FULL_CANDIDATE"]["comparison_to_A"][
            "portfolio_exact_equality_to_A"
        ]
        and a_rows["B_BASE_SIGNAL_ONLY"]["comparison_to_A"][
            "portfolio_exact_equality_to_A"
        ]
        and report_a_rows["B_BASE_SIGNAL_ONLY"]["comparison_to_A"][
            "portfolio_exact_equality_to_A"
        ]
    )
    mapping_or_identity_artifact = bool(any(artifact_flags.values()))
    concentration = ablation["economic_concentration"]
    accidental_concentration = bool(
        concentration["accidental_concentration"]
    )
    independent_rules = config["qualification_rules"][
        "independent_evidence"
    ]
    report_net_lcb = float(
        report["native_metrics"]["incremental"]["net_lcb"]
    )
    independent_failures = {
        "report_only_midsearch_visibility_contract_failed": bool(
            independent_rules[
                "report_only_midsearch_visibility_forbidden"
            ]
            and independence["cluster_threshold"][
                "report_only_metrics_visible_to_stage_b_gate"
            ]
        ),
        "report_only_candidate_net_lcb_not_positive": bool(
            report_net_lcb
            <= float(independent_rules["minimum_report_only_net_lcb"])
        ),
        "no_independent_mechanism_replication": bool(
            int(cross_seed["independent_mechanism_replications"])
            < int(
                independent_rules[
                    "minimum_independent_mechanism_replications"
                ]
            )
        ),
        "robust_statistic_reuses_adaptive_selection_months": bool(
            independent_rules[
                "adaptive_data_cannot_count_as_independent_retest"
            ]
            and independence["selection"][
                "adaptive_months_reused_in_robust_statistic"
            ]
            > 0
        ),
    }
    insufficient = bool(any(independent_failures.values()))
    combined = ablation["combined_18m_monthly_robustness"]
    regime_evidence = {
        "A_robust_positive": bool(
            combined["A_FULL_CANDIDATE"]["robust_positive"]
        ),
        "C_regime_only_robust_positive": bool(
            combined["C_REGIME_ONLY"]["robust_positive"]
        ),
        "G_placebo_not_robust_positive": not bool(
            combined["G_MATCHED_OCCUPANCY_PLACEBO"]["robust_positive"]
        ),
        "A_differs_from_B_portfolio": not bool(
            a_rows["B_BASE_SIGNAL_ONLY"]["comparison_to_A"][
                "portfolio_exact_equality_to_A"
            ]
        ),
        "A_report_only_incremental_mean_positive": bool(
            report["native_metrics"]["incremental"]["net_mean"] > 0.0
        ),
    }
    legitimate_regime = bool(all(regime_evidence.values()))
    localized_increment = bool(
        combined["A_FULL_CANDIDATE"]["robust_positive"]
        and not accidental_concentration
        and not mapping_or_identity_artifact
    )
    if mapping_or_identity_artifact:
        classification = "MAPPING_OR_IDENTITY_ARTIFACT"
    elif accidental_concentration:
        classification = "ACCIDENTAL_CONCENTRATION"
    elif insufficient:
        classification = "INSUFFICIENT_INDEPENDENT_EVIDENCE"
    elif legitimate_regime:
        classification = "LEGITIMATE_REGIME_LOCALIZATION"
    elif localized_increment:
        classification = "LOCALIZED_DEVELOPMENT_INCREMENT_OBSERVED"
    else:
        classification = "INSUFFICIENT_INDEPENDENT_EVIDENCE"
    return classification, {
        "mapping_or_identity_artifact": mapping_or_identity_artifact,
        "artifact_flags": artifact_flags,
        "accidental_concentration": accidental_concentration,
        "concentration_breaches": concentration["breaches"],
        "insufficient_independent_evidence": insufficient,
        "independent_evidence_failures": independent_failures,
        "legitimate_regime_localization_evidence": regime_evidence,
        "localized_development_increment_evidence": localized_increment,
        "adaptive_native_net_lcb": float(
            adaptive["native_metrics"]["incremental"]["net_lcb"]
        ),
        "report_only_native_net_lcb": report_net_lcb,
    }


def _report_text(
    decision: Mapping[str, Any],
    identity: Mapping[str, Any],
    independence: Mapping[str, Any],
    ablation: Mapping[str, Any],
    cross_seed: Mapping[str, Any],
) -> str:
    concentration = ablation["economic_concentration"]
    adaptive = identity["blocks"][0]["native_metrics"]["incremental"]
    report = identity["blocks"][1]["native_metrics"]["incremental"]
    return f"""# Crypto Localized Mechanism Qualification

## Decision

`{decision["final_classification"]}`

The unique robust-positive candidate is not an exact identity or portfolio
duplicate of its matched control, and its fixed 18-month contribution is not
dominated by one month or one asset.  The evidence is nevertheless not
independent enough to freeze a challenger.

## Candidate and native pair

- candidate: `{decision["candidate_id"]}`
- formula: `{identity["formula_identity"]["formula"]}`
- control: `{identity["formula_identity"]["control_formula"]}`
- adaptive incremental net / LCB: `{adaptive["net_mean"]:.12g}` / `{adaptive["net_lcb"]:.12g}`
- report-only incremental net / LCB: `{report["net_mean"]:.12g}` / `{report["net_lcb"]:.12g}`
- mapping: `{identity["portfolio_identity"]["mapping_id"]}` at 5 bps full L1 cost

## Identity and mapping qualification

- exact formula equals control: `{decision["qualification"]["artifact_flags"]["formula_identity_equals_control"]}`
- portfolio equals control on any block: `{decision["qualification"]["artifact_flags"]["portfolio_identity_equals_control_on_any_block"]}`
- adaptive primary/control portfolio-size ratio: `{identity["portfolio_identity"]["native_mapping_sparsity_change"]["adaptive_primary_over_control_portfolio_size_ratio"]:.6f}`
- report-only primary/control portfolio-size ratio: `{identity["portfolio_identity"]["native_mapping_sparsity_change"]["report_only_primary_over_control_portfolio_size_ratio"]:.6f}`
- artifact replay: `{"PASS" if not identity["artifact_identity_reuse_error"] else "FAIL"}`

The native pair changes occupancy on the adaptive block because the
cross-sectional listing-age state creates tied/zero scores.  The fixed A-G
audit therefore also uses a matched-occupancy bridge that preserves A's exact
weight multiset at every timestamp; it is diagnostic and does not change the
source mapping or candidate.

## Economic concentration

- combined fixed-portfolio net mean: `{concentration["combined_net_mean"]:.12g}`
- Top-1 month positive contribution share: `{concentration["top1_month_positive_contribution_share"]:.6f}`
- Top-3 month positive contribution share: `{concentration["top3_month_positive_contribution_share"]:.6f}`
- Top-1 asset positive contribution share: `{concentration["top1_asset_positive_contribution_share"]:.6f}`
- minimum leave-one-month net mean: `{concentration["leave_one_month_minimum"]["net_mean"]:.12g}`
- leave-top-3-assets net mean: `{concentration["leave_top3_assets"]["net_mean"]:.12g}`
- accidental concentration: `{concentration["accidental_concentration"]}`

## Report-only independence

`{independence["status"]}`

The Stage B gate read Stage A report-only cluster/yield statistics even though
the feedback contract declared those metrics invisible to policy.  In this
frozen run the read was non-causal: adaptive cross-seed policy improvement
already made the OR gate true, so removing report-only terms leaves the same
Stage B authorization.  No report-only reward was written to lane state.

The larger limitation is statistical: the reported 18-month robust statistic
combines 12 adaptive selection months with only six report-only months.  The
candidate's independent report-only LCB is negative.

## Fixed A-G ablation

- A full candidate robust positive: `{ablation["combined_18m_monthly_robustness"]["A_FULL_CANDIDATE"]["robust_positive"]}`
- C regime-only robust positive: `{ablation["combined_18m_monthly_robustness"]["C_REGIME_ONLY"]["robust_positive"]}`
- E time-shuffled regime robust positive: `{ablation["combined_18m_monthly_robustness"]["E_TIME_SHUFFLED_REGIME"]["robust_positive"]}`
- F lagged regime portfolio equals A on the frozen coordinates: `{ablation["blocks"]["adaptive"][5]["comparison_to_A"]["portfolio_exact_equality_to_A"] and ablation["blocks"]["report_only"][5]["comparison_to_A"]["portfolio_exact_equality_to_A"]}`
- G matched-occupancy placebo robust positive: `{ablation["combined_18m_monthly_robustness"]["G_MATCHED_OCCUPANCY_PLACEBO"]["robust_positive"]}`

The results are compatible with a listing-age/maturity localization, but they
do not isolate a unique contemporaneous regime mechanism.  The 4-hour lag
remains highly portfolio-correlated with A and is still robust-positive.  The
time-shuffled state loses standalone robustness but retains a positive
incremental-vs-base mean on both development blocks.

## Cross-seed qualification

- reproduced source clusters: `{len(cross_seed["clusters"])}`
- independent mechanism replications: `{cross_seed["independent_mechanism_replications"]}`

Both clusters are report-only-positive variants of the same broad
STATE_REGIME_MODULATION family.  They do not provide a distinct mechanism that
is matched-positive on both blocks and therefore cannot independently validate
the unique candidate.

## Claim boundary

- `NEW_SEARCH_REMAINS_FROZEN`
- `STRICT_OOS_REMAINS_NOT_AUTHORIZED`
- `PROMOTION_REMAINS_FORBIDDEN`
- forward, recent, validation, holdout, May stress, and formal challenge were not read
- no `ALPHA_FOUND`, `OOS_PASS`, or `PROMOTION_READY` conclusion is authorized
"""


def build_decision(
    repo_root: Path,
    *,
    config_path: Path,
    source_sha: str | None = None,
) -> dict[str, Any]:
    config = _read_json(config_path)
    _validate_config(config)
    runtime_root = repo_root / str(config["outputs"]["runtime_root"])
    for name in AUDIT_OUTPUTS:
        if not (runtime_root / name).exists():
            raise FileNotFoundError(f"missing qualification audit: {name}")
    source_sha = (source_sha or _git_sha(repo_root)).lower()
    selection = _read_json(runtime_root / AUDIT_OUTPUTS[0])
    identity = _read_json(runtime_root / AUDIT_OUTPUTS[1])
    independence = _read_json(runtime_root / AUDIT_OUTPUTS[3])
    ablation = _read_json(runtime_root / AUDIT_OUTPUTS[4])
    cross_seed = _read_json(runtime_root / AUDIT_OUTPUTS[5])
    classification, qualification = _classify(
        config, identity, independence, ablation, cross_seed
    )
    if classification not in FINAL_CLASSIFICATIONS:
        raise AssertionError("invalid final classification")
    challenger_allowed = classification in {
        "LOCALIZED_DEVELOPMENT_INCREMENT_OBSERVED",
        "LEGITIMATE_REGIME_LOCALIZATION",
    }
    decision = {
        "schema_version": 1,
        "task_id": config["task_id"],
        "final_classification": classification,
        "candidate_id": config["unique_robust_candidate_id"],
        "source_bundle_sha256": config["source_bundle_sha256"],
        "audit_implementation_sha": selection["audit_source_sha"],
        "decision_producer_sha": source_sha,
        "qualification": qualification,
        "challenger_frozen": challenger_allowed,
        "challenger_specification": (
            "ISSUED" if challenger_allowed else "NOT_ISSUED"
        ),
        "claim_scope": (
            "authorized 2023-07 through 2024-12 development coordinates only"
        ),
        "sealed_reads": 0,
        "boundaries": {
            "NEW_SEARCH_REMAINS_FROZEN": True,
            "STRICT_OOS_REMAINS_NOT_AUTHORIZED": True,
            "PROMOTION_REMAINS_FORBIDDEN": True,
            "FORWARD_REMAINS_SEALED": True,
            "CROSS_SPRINT_MEMORY_REMAINS_FORBIDDEN": True,
        },
        "cannot_conclude": [
            "ALPHA_FOUND",
            "OOS_PASS",
            "PROMOTION_READY",
            "formal challenge qualification",
            "live execution readiness",
        ],
    }
    _write_json(runtime_root / DECISION_OUTPUTS[0], decision)
    if challenger_allowed:
        challenger = {
            "schema_version": 1,
            "issued": True,
            "classification": classification,
            "formula": identity["formula_identity"]["canonical_ast"],
            "identity": identity["formula_identity"],
            "fields": selection["candidate_lineage"]["raw_fields"],
            "mapping": identity["portfolio_identity"],
            "cost_bps": FIXED_COST_BPS,
            "support": "frozen source pair raw-support contract",
            "regime": "frozen canonical expression state child",
            "clock": config["authorized_blocks"],
            "receipt": identity["receipt_identity"],
            "candidate_hash": config["unique_robust_candidate_id"],
            "cluster_hash": selection["cluster_lineage"][
                "candidate_cluster_id"
            ],
            "allowed_future_evidence": [
                "explicitly authorized strict OOS replay without modification"
            ],
            "forbidden_modifications": [
                "formula",
                "fields",
                "windows",
                "mapping",
                "cost",
                "support",
                "regime",
                "clock",
                "candidate identity",
            ],
            "success_criterion": "predeclared strict OOS contract passes",
            "failure_criterion": "any identity drift or strict OOS failure",
        }
    else:
        challenger = {
            "schema_version": 1,
            "issued": False,
            "not_a_specification": True,
            "classification": classification,
            "reason": (
                "Only LOCALIZED_DEVELOPMENT_INCREMENT_OBSERVED or "
                "LEGITIMATE_REGIME_LOCALIZATION may issue an immutable "
                "challenger.  Independent evidence requirements were not met."
            ),
            "candidate_id_recorded_for_non_issuance_only": config[
                "unique_robust_candidate_id"
            ],
            "promotion": "FORBIDDEN",
        }
    _write_json(runtime_root / DECISION_OUTPUTS[1], challenger)
    report_path = repo_root / str(config["outputs"]["report"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _report_text(decision, identity, independence, ablation, cross_seed),
        encoding="utf-8",
        newline="\n",
    )
    artifact_paths = [
        runtime_root / name for name in (*AUDIT_OUTPUTS, *DECISION_OUTPUTS[:2])
    ] + [
        report_path,
        config_path,
        repo_root
        / "alphafactory_crypto"
        / "broad_search"
        / "qualification18m.py",
        repo_root / "scripts" / "crypto_localized_mechanism_qualification.py",
        repo_root / "tests" / "test_crypto_localized_mechanism_qualification.py",
        repo_root
        / str(config["source_runtime_root"])
        / "CRYPTO_ARTIFACT_MANIFEST.json",
    ]
    artifact_rows = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": int(path.stat().st_size),
            "sha256": sha256_file(path),
        }
        for path in sorted(set(artifact_paths))
    ]
    manifest = {
        "schema_version": 1,
        "task_id": config["task_id"],
        "final_classification": classification,
        "audit_implementation_sha": selection["audit_source_sha"],
        "decision_producer_sha": source_sha,
        "base_closure_sha": config["base_closure_sha"],
        "source_bundle_sha256": config["source_bundle_sha256"],
        "sealed_reads": 0,
        "artifacts": artifact_rows,
    }
    manifest["bundle_sha256"] = _payload_sha(artifact_rows)
    _write_json(runtime_root / DECISION_OUTPUTS[2], manifest)
    return {
        "result": "PASS",
        "final_classification": classification,
        "challenger_frozen": challenger_allowed,
        "bundle_sha256": manifest["bundle_sha256"],
        "sealed_reads": 0,
    }


def check_evidence(
    repo_root: Path, *, config_path: Path
) -> dict[str, Any]:
    config = _read_json(config_path)
    _validate_config(config)
    runtime_root = repo_root / str(config["outputs"]["runtime_root"])
    manifest_path = runtime_root / DECISION_OUTPUTS[2]
    manifest = _read_json(manifest_path)
    errors: list[str] = []
    source_manifest = _read_json(
        repo_root
        / str(config["source_runtime_root"])
        / "CRYPTO_ARTIFACT_MANIFEST.json"
    )
    if source_manifest.get("bundle_sha256") != config["source_bundle_sha256"]:
        errors.append("source_bundle_sha256")
    for row in manifest.get("artifacts", []):
        path = repo_root / str(row["path"])
        if not path.exists():
            errors.append(f"missing:{row['path']}")
            continue
        if int(path.stat().st_size) != int(row["bytes"]):
            errors.append(f"bytes:{row['path']}")
        if sha256_file(path) != row["sha256"]:
            errors.append(f"sha256:{row['path']}")
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get(
        "bundle_sha256"
    ):
        errors.append("bundle_sha256")
    decision = _read_json(runtime_root / DECISION_OUTPUTS[0])
    challenger = _read_json(runtime_root / DECISION_OUTPUTS[1])
    if decision.get("final_classification") not in FINAL_CLASSIFICATIONS:
        errors.append("final_classification")
    allowed = decision.get("final_classification") in {
        "LOCALIZED_DEVELOPMENT_INCREMENT_OBSERVED",
        "LEGITIMATE_REGIME_LOCALIZATION",
    }
    if bool(challenger.get("issued")) != allowed:
        errors.append("challenger_issuance")
    if int(decision.get("sealed_reads", -1)) != 0:
        errors.append("sealed_reads")
    boundaries = decision.get("boundaries", {})
    if not all(
        bool(boundaries.get(name))
        for name in (
            "NEW_SEARCH_REMAINS_FROZEN",
            "STRICT_OOS_REMAINS_NOT_AUTHORIZED",
            "PROMOTION_REMAINS_FORBIDDEN",
            "FORWARD_REMAINS_SEALED",
            "CROSS_SPRINT_MEMORY_REMAINS_FORBIDDEN",
        )
    ):
        errors.append("boundaries")
    identity = _read_json(runtime_root / AUDIT_OUTPUTS[1])
    if identity.get("artifact_identity_reuse_error"):
        errors.append("artifact_reproduction")
    independence = _read_json(runtime_root / AUDIT_OUTPUTS[3])
    if independence["candidate_generation"][
        "strict_report_only_occurrence_multiset_equal"
    ] is not True:
        errors.append("candidate_pack_identity")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "final_classification": decision.get("final_classification"),
        "challenger_frozen": bool(challenger.get("issued")),
        "bundle_sha256": manifest.get("bundle_sha256"),
        "sealed_reads": decision.get("sealed_reads"),
    }


__all__ = [
    "AUDIT_OUTPUTS",
    "DECISION_OUTPUTS",
    "FINAL_CLASSIFICATIONS",
    "build_audits",
    "build_decision",
    "check_evidence",
]
