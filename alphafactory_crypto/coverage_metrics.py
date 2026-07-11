from __future__ import annotations

import math
from collections import Counter
from typing import Iterable, Mapping


def entropy(values: Iterable[str]) -> float:
    counts = Counter(values)
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def coverage(observed: Iterable[str], registry: Iterable[str]) -> dict[str, float | int]:
    expected = set(registry)
    actual = set(observed) & expected
    return {"covered": len(actual), "registered": len(expected), "ratio": len(actual) / len(expected) if expected else 1.0}


def nextgen_coverage_report(
    proposals: Iterable[Mapping[str, str]], *, field_families: Iterable[str], primitives: Iterable[str],
    event_states: Iterable[str], hypotheses: Iterable[str], behaviours: Iterable[str], lanes: Iterable[str],
) -> dict[str, object]:
    rows = tuple(proposals)
    values = lambda key: [str(row[key]) for row in rows if row.get(key)]
    hypothesis_counts = Counter(values("economic_hypothesis"))
    total = sum(hypothesis_counts.values())
    imbalance = max(hypothesis_counts.values(), default=0) / total if total else 0.0
    return {
        "metric_class": "NON_PERFORMANCE_COVERAGE_ONLY",
        "field_family_coverage": coverage(values("field_family"), field_families),
        "temporal_primitive_coverage": coverage(values("primitive"), primitives),
        "event_state_coverage": coverage(values("event_state"), event_states),
        "economic_hypothesis_coverage": coverage(values("economic_hypothesis"), hypotheses),
        "behaviour_cluster_potential": len(set(values("behaviour_cluster"))),
        "grammar_cell_entropy": entropy(values("grammar_cell")),
        "lineage_entropy": entropy(values("lineage_namespace")),
        "semantic_volume_imbalance": imbalance,
        "per_lane_proposal_distribution": dict(sorted(Counter(values("lane_id")).items())),
        "lane_coverage": coverage(values("lane_id"), lanes),
        "performance_fields_read": False,
    }

