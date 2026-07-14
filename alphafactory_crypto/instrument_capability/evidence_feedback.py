"""Pure renderers for capability feedback and strict-feasibility evidence.

The functions in this module do not write files and do not make economic-
increment claims.  They compare a legacy diagnostic proxy with the frozen
aligned ordering over deterministic synthetic qualification payloads only.
"""

from __future__ import annotations

import math
from itertools import combinations
from typing import Any, Mapping, Sequence


DEFAULT_TOP_K = 3
POSITIVE_VARIANT = "positive"
EVIDENCE_SCOPE = "SYNTHETIC_CAPABILITY_ONLY_NO_ECONOMIC_INCREMENT_CLAIM"


def _finite(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _clean(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(item) for item in value]
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def _family_id(run: Mapping[str, Any]) -> str:
    return str(run.get("family_contract", {}).get("family_id", ""))


def _aligned_key(candidate: Mapping[str, Any]) -> tuple[float, ...]:
    raw = candidate.get("feedback", {}).get("sort_key", ())
    values = tuple(_finite(value) for value in raw) if isinstance(raw, Sequence) else ()
    if not values or any(value is None for value in values):
        return (float("-inf"),)
    return tuple(float(value) for value in values if value is not None)


def _aligned_outcome(candidate: Mapping[str, Any]) -> str:
    feedback = candidate.get("feedback", {})
    if bool(feedback.get("blocked")):
        return "BLOCKED_BEFORE_STRICT_ORDERING"
    if bool(feedback.get("feasible")):
        return "STRICT_FEASIBLE"
    return "STRICT_INFEASIBLE"


def _legacy_proxy(candidate: Mapping[str, Any]) -> float | None:
    return _finite(candidate.get("metrics", {}).get("gross_proxy"))


def _strict_distance(candidate: Mapping[str, Any]) -> float | None:
    return _finite(candidate.get("feedback", {}).get("distance"))


def _average_ranks(values: Mapping[str, Any]) -> dict[str, float]:
    ordered = sorted(values, key=lambda key: values[key])
    ranks: dict[str, float] = {}
    cursor = 0
    while cursor < len(ordered):
        end = cursor + 1
        while end < len(ordered) and values[ordered[end]] == values[ordered[cursor]]:
            end += 1
        average = ((cursor + 1) + end) / 2.0
        for key in ordered[cursor:end]:
            ranks[key] = average
        cursor = end
    return ranks


def _spearman(left: Mapping[str, Any], right: Mapping[str, Any]) -> float | None:
    keys = [key for key in left if key in right]
    if len(keys) < 2:
        return None
    left_rank = _average_ranks({key: left[key] for key in keys})
    right_rank = _average_ranks({key: right[key] for key in keys})
    x = [left_rank[key] for key in keys]
    y = [right_rank[key] for key in keys]
    x_mean, y_mean = sum(x) / len(x), sum(y) / len(y)
    numerator = sum((a - x_mean) * (b - y_mean) for a, b in zip(x, y))
    denominator = math.sqrt(
        sum((a - x_mean) ** 2 for a in x) * sum((b - y_mean) ** 2 for b in y)
    )
    return numerator / denominator if denominator > 0.0 else None


def _pairwise(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    keys = [key for key in left if key in right]
    agreement = inversions = tie_disagreements = total = 0
    for first, second in combinations(keys, 2):
        left_sign = (left[first] > left[second]) - (left[first] < left[second])
        right_sign = (right[first] > right[second]) - (right[first] < right[second])
        total += 1
        if left_sign == right_sign:
            agreement += 1
        elif left_sign * right_sign < 0:
            inversions += 1
        else:
            tie_disagreements += 1
    return {
        "comparable_pairs": total,
        "ordering_agreement": agreement / total if total else None,
        "pairwise_inversion_count": inversions,
        "tie_disagreement_count": tie_disagreements,
    }


def _run_alignment(run: Mapping[str, Any]) -> dict[str, Any]:
    candidates = run.get("candidates", {})
    positive = candidates.get(POSITIVE_VARIANT, {})
    old = {
        variant: proxy
        for variant, candidate in candidates.items()
        if (proxy := _legacy_proxy(candidate)) is not None
    }
    aligned = {variant: _aligned_key(candidate) for variant, candidate in candidates.items()}
    common = {variant: old[variant] for variant in old if variant in aligned}
    common_aligned = {variant: aligned[variant] for variant in common}
    old_ranks = _average_ranks(common) if common else {}
    aligned_ranks = _average_ranks(common_aligned) if common_aligned else {}
    top_k = min(DEFAULT_TOP_K, len(common))
    old_top = sorted(common, key=lambda key: (common[key], key), reverse=True)[:top_k]
    new_top = sorted(common_aligned, key=lambda key: (common_aligned[key], key), reverse=True)[:top_k]

    def feasible_rate(variants: Sequence[str]) -> float | None:
        if not variants:
            return None
        return sum(bool(candidates[item].get("feedback", {}).get("feasible")) for item in variants) / len(variants)

    decoys = [variant for variant in candidates if variant != POSITIVE_VARIANT]
    positive_old = _legacy_proxy(positive)
    comparable_old_decoys = [variant for variant in decoys if _legacy_proxy(candidates[variant]) is not None and positive_old is not None]
    old_rejected = [variant for variant in comparable_old_decoys if positive_old > float(_legacy_proxy(candidates[variant]))]
    new_rejected = [variant for variant in decoys if _aligned_key(positive) > _aligned_key(candidates[variant])]
    old_fooling = [variant for variant in comparable_old_decoys if float(_legacy_proxy(candidates[variant])) >= float(positive_old)]
    new_fooling = [variant for variant in decoys if _aligned_key(candidates[variant]) >= _aligned_key(positive)]
    pairwise = _pairwise(common, common_aligned)

    comparison_rows = []
    for variant, candidate in candidates.items():
        comparison_rows.append(
            {
                "variant": variant,
                "candidate_id": candidate.get("candidate_id"),
                "is_decoy": variant != POSITIVE_VARIANT,
                "legacy_gross_proxy": _legacy_proxy(candidate),
                "legacy_rank": old_ranks.get(variant),
                "aligned_rank": aligned_ranks.get(variant),
                "aligned_outcome": _aligned_outcome(candidate),
                "strict_feasibility_distance": _strict_distance(candidate),
                "strict_feasible": bool(candidate.get("feedback", {}).get("feasible")),
                "blocked_before_strict_ordering": bool(candidate.get("feedback", {}).get("blocked")),
            }
        )
    return {
        "family_id": _family_id(run),
        "seed": run.get("seed"),
        "comparison_candidate_count": len(common),
        "legacy_proxy_unavailable_variants": sorted(set(candidates) - set(old)),
        "top_k": top_k,
        **pairwise,
        "spearman_rank_correlation": _spearman(common, common_aligned),
        "top_k_strict_feasibility_rate_legacy": feasible_rate(old_top),
        "top_k_strict_feasibility_rate_aligned": feasible_rate(new_top),
        "decoy_rejection_rate_legacy": len(old_rejected) / len(comparable_old_decoys) if comparable_old_decoys else None,
        "decoy_rejection_rate_aligned": len(new_rejected) / len(decoys) if decoys else None,
        "legacy_decoy_denominator": len(comparable_old_decoys),
        "aligned_decoy_denominator": len(decoys),
        "decoys_still_fooling_legacy_feedback": sorted(old_fooling),
        "decoys_still_fooling_aligned_feedback": sorted(new_fooling),
        "legacy_proxy_not_comparable_decoys": sorted(set(decoys) - set(comparable_old_decoys)),
        "legacy_top_k_variants": old_top,
        "aligned_top_k_variants": new_top,
        "candidate_comparison": comparison_rows,
    }


def proxy_strict_alignment_payload(q: Mapping[str, Any]) -> dict[str, Any]:
    """Compare legacy proxy ordering with aligned strict-feasibility ordering."""

    runs = [_run_alignment(run) for run in q.get("runs", [])]
    mean_fields = (
        "ordering_agreement",
        "spearman_rank_correlation",
        "top_k_strict_feasibility_rate_legacy",
        "top_k_strict_feasibility_rate_aligned",
        "decoy_rejection_rate_legacy",
        "decoy_rejection_rate_aligned",
    )
    aggregate: dict[str, Any] = {}
    for field in mean_fields:
        values = [_finite(run.get(field)) for run in runs]
        finite = [value for value in values if value is not None]
        aggregate[f"mean_{field}"] = sum(finite) / len(finite) if finite else None
    aggregate["pairwise_inversion_count"] = sum(int(run["pairwise_inversion_count"]) for run in runs)
    aggregate["decoys_still_fooling_legacy_feedback"] = sorted({item for run in runs for item in run["decoys_still_fooling_legacy_feedback"]})
    aggregate["decoys_still_fooling_aligned_feedback"] = sorted({item for run in runs for item in run["decoys_still_fooling_aligned_feedback"]})
    return _clean(
        {
            "schema_version": 1,
            "scope": EVIDENCE_SCOPE,
            "economic_increment_claimed": False,
            "ordering_agreement_definition": "matching pairwise order signs on candidates with finite legacy proxy",
            "strict_feasibility_definition": "aligned outcome and signed minimum normalized strict margin",
            "run_count": len(runs),
            "runs": runs,
            "aggregate": aggregate,
        }
    )


def capability_matrix_rows(q: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return one flat capability row per family, seed, and algorithm."""

    rows: list[dict[str, Any]] = []
    cross_seed = q.get("cross_seed_reproduction", {})
    for run in q.get("runs", []):
        family = _family_id(run)
        candidates = run.get("candidates", {})
        positive = candidates.get(POSITIVE_VARIANT, {})
        by_id = {candidate.get("candidate_id"): candidate for candidate in candidates.values()}
        for algorithm, search in run.get("searches", {}).items():
            survivor = by_id.get(search.get("survivor_id"), {})
            proposals = list(search.get("proposal_order", []))
            rows.append(
                {
                    "family_id": family,
                    "seed": run.get("seed"),
                    "algorithm": algorithm,
                    "proposal_count": len(proposals),
                    "unique_candidate_count": len(set(proposals)),
                    "positive_reachable": positive.get("candidate_id") in proposals,
                    "survivor_id": search.get("survivor_id"),
                    "survivor_variant": search.get("survivor_variant"),
                    "survivor_aligned_outcome": _aligned_outcome(survivor),
                    "survivor_strict_feasibility_distance": _strict_distance(survivor),
                    "survivor_strict_feasible": bool(survivor.get("feedback", {}).get("feasible")),
                    "positive_survived": search.get("survivor_variant") == POSITIVE_VARIANT,
                    "independent_behavior": bool(search.get("independent_behavior")),
                    "behavior_hash": search.get("behavior_hash"),
                    "run_qualified": bool(run.get("qualified")),
                    "canonical_mechanism_reproduction": cross_seed.get(family, {}).get("canonical_mechanism_reproduction"),
                    "behavior_reproduction": cross_seed.get(family, {}).get("behavior_reproduction"),
                    "evidence_scope": EVIDENCE_SCOPE,
                    "economic_increment_claimed": False,
                }
            )
    return _clean(rows)


def planted_result_rows(q: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return one flat planted-result row per family, seed, and variant."""

    rows: list[dict[str, Any]] = []
    for run in q.get("runs", []):
        family = _family_id(run)
        candidates = run.get("candidates", {})
        positive = candidates.get(POSITIVE_VARIANT, {})
        positive_old = _legacy_proxy(positive)
        positive_aligned = _aligned_key(positive)
        old_values = {variant: proxy for variant, candidate in candidates.items() if (proxy := _legacy_proxy(candidate)) is not None}
        aligned_values = {variant: _aligned_key(candidate) for variant, candidate in candidates.items()}
        old_ranks = _average_ranks(old_values) if old_values else {}
        aligned_ranks = _average_ranks(aligned_values) if aligned_values else {}
        searches = run.get("searches", {})
        for variant, candidate in candidates.items():
            metrics = candidate.get("metrics", {})
            survived = sorted(algorithm for algorithm, search in searches.items() if search.get("survivor_variant") == variant)
            reached = sorted(algorithm for algorithm, search in searches.items() if candidate.get("candidate_id") in search.get("proposal_order", []))
            old_proxy = _legacy_proxy(candidate)
            rows.append(
                {
                    "family_id": family,
                    "seed": run.get("seed"),
                    "variant": variant,
                    "candidate_id": candidate.get("candidate_id"),
                    "primitive_id": candidate.get("primitive_id"),
                    "portfolio_mapping_id": candidate.get("portfolio_mapping_id"),
                    "is_planted_positive": variant == POSITIVE_VARIANT,
                    "is_decoy": variant != POSITIVE_VARIANT,
                    "legal": bool(candidate.get("legal")),
                    "entered_strict": bool(candidate.get("entered_strict")),
                    "aligned_outcome": _aligned_outcome(candidate),
                    "aligned_blocked": bool(candidate.get("feedback", {}).get("blocked")),
                    "aligned_feasible": bool(candidate.get("feedback", {}).get("feasible")),
                    "aligned_reason": candidate.get("feedback", {}).get("reason"),
                    "strict_feasibility_distance": _strict_distance(candidate),
                    "legacy_gross_proxy": old_proxy,
                    "legacy_rank": old_ranks.get(variant),
                    "aligned_rank": aligned_ranks.get(variant),
                    "fools_legacy_feedback": None if old_proxy is None or positive_old is None or variant == POSITIVE_VARIANT else old_proxy >= positive_old,
                    "fools_aligned_feedback": False if variant == POSITIVE_VARIANT else _aligned_key(candidate) >= positive_aligned,
                    "mapped_net_metric": _finite(metrics.get("mapped_net_metric")),
                    "benchmark_increment": _finite(metrics.get("benchmark_increment")),
                    "worst_block_margin": _finite(metrics.get("worst_block_margin")),
                    "positive_block_fraction": _finite(metrics.get("positive_block_fraction")),
                    "turnover": _finite(metrics.get("turnover")),
                    "cost": _finite(metrics.get("cost")),
                    "concentration": _finite(metrics.get("concentration")),
                    "support": _finite(metrics.get("support")),
                    "behavior_identity": candidate.get("behavior_identity"),
                    "reached_algorithms": reached,
                    "survived_algorithms": survived,
                    "survivor_count": len(survived),
                    "evidence_scope": EVIDENCE_SCOPE,
                    "economic_increment_claimed": False,
                }
            )
    return _clean(rows)


__all__ = [
    "capability_matrix_rows",
    "planted_result_rows",
    "proxy_strict_alignment_payload",
]
