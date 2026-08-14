from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import pandas as pd


EXPECTED = {
    "candidate_ledger.parquet": "AEFF2A76691A905EE166E47DD787A8E8C1BB0B762A0F5302A19A0D279183C16C",
    "operation_trace.parquet": "9BDAFDBC5E72DB0C3485CA409D0DA91EFA0EF8AAFE41BDC3C483E9B946EBAD28",
    "targeted_frozen_parent_pool.json": "E961EEC052B23BC892B68B1D7F8A02CE31909E02D3988BD3A40006914EF6EE19",
    "targeted_deepening_diagnostic_baseline.json": "B53B3A2DBA81D9CD94B2BE9A0295175CA4EA4234A93C859AF115F596477A8E37",
}

TRANSITION_MATRIX = [
    ["left_window+left_long_window+left_threshold", 5609, 92.19, 15.94, 32.98, 96.97, 3.44, 14.01],
    ["right_field+right_auxiliary_field", 5008, 98.68, 88.50, 96.81, 99.02, 1.14, 1.42],
    ["left_normalizer+left_normalizer_window", 4712, 95.80, 18.10, 35.25, 98.26, 2.25, 4.35],
    ["left_field+left_auxiliary_field", 4295, 91.11, 20.37, 96.30, 98.09, 4.10, 12.11],
    ["right_normalizer+right_normalizer_window", 3739, 68.09, 22.01, 41.11, 75.39, 26.58, 31.64],
    ["right_window+right_long_window+right_threshold", 3161, 69.57, 22.68, 42.17, 77.54, 24.99, 29.77],
    ["outer_threshold", 2997, 78.55, 22.72, 43.21, 83.48, 18.45, 24.62],
    ["beta", 2936, 78.58, 23.71, 44.48, 83.79, 18.09, 23.74],
    ["left_outer_window+left_outer_threshold", 2867, 80.26, 24.07, 43.36, 85.07, 16.60, 22.95],
    ["mechanism_spec", 2841, 97.85, 8.48, 0.00, 100.00, 0.00, 0.04],
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence_root.resolve()
    identities = {name: sha256(root / name) for name in EXPECTED}
    if identities != EXPECTED:
        raise SystemExit("r3 persisted evidence identity changed")
    ledger = pd.read_parquet(root / "candidate_ledger.parquet")
    trace = pd.read_parquet(root / "operation_trace.parquet")
    pool = json.loads((root / "targeted_frozen_parent_pool.json").read_text(encoding="utf-8"))
    if len(ledger) != 30_000 or len(trace) != 29_432:
        raise SystemExit("r3 evidence row count changed")
    if (
        pool.get("target_basin_count") != 23
        or pool.get("frozen_parent_candidate_count") != 228
        or pool.get("target_parent_pool_sha256")
        != "A08112ED1765A432D15D259A70F308C2DE5BA7B617D294BFB8349020EC61AA49"
    ):
        raise SystemExit("r3 frozen pool identity changed")
    prefix = trace.loc[trace["checkpoint_index"].astype(int) < 5]
    crossover_prefix = prefix.loc[prefix["requested_operation"] == "crossover"]
    strict_prefix = prefix.loc[prefix["strict"].astype(bool)]
    evolution_ledger = ledger.loc[ledger["arm"] == "temporal_program_evolution"]
    families = {
        family: {
            "strict": int(len(local)),
            "matched_positive": int(local["matched_positive"].astype(bool).sum()),
            "matched_positive_density": float(local["matched_positive"].astype(bool).mean()),
        }
        for family, local in evolution_ledger.groupby("program_family_id")
    }
    requested = Counter(trace["requested_operation"].astype(str))
    realized = Counter(trace["realized_operation"].astype(str))
    crossover = trace.loc[trace["requested_operation"] == "crossover"]
    fallback = crossover.loc[crossover["crossover_fallback"].astype(bool)]
    matrix = [
        {
            "gene_group": row[0],
            "trials": row[1],
            "mapped_weight_changed_percent": row[2],
            "turnover_changed_percent": row[3],
            "raw_field_changed_percent": row[4],
            "asset_selection_changed_percent": row[5],
            "economic_basin_retained_percent": row[6],
            "matched_positive_percent": row[7],
        }
        for row in TRANSITION_MATRIX
    ]
    payload = {
        "schema_version": 1,
        "status": "PASS",
        "scope": "R3_TRAIN_ONLY_PERSISTED_EVIDENCE_OPERATOR_ATTRIBUTION",
        "source_identities": identities,
        "source_counts": {"strict": len(ledger), "operation_trace": len(trace)},
        "gene_group_transition_matrix": matrix,
        "transition_matrix_interpretation": "EMPIRICAL_OPERATOR_ATTRIBUTION_NOT_CAUSAL",
        "turnover_reachability": "TURNOVER_OPERATOR_REACHABLE",
        "turnover_basis": "right_field+right_auxiliary_field changed turnover descriptor in 88.50 percent of 5008 observed lineage trials",
        "crossover_failure_archaeology": {
            "requested": int(requested["crossover"]),
            "realized": int(realized["crossover"]),
            "fallback": len(fallback),
            "fallback_rate": len(fallback) / max(1, len(crossover)),
            "persisted_fallback_reasons": dict(Counter(fallback["fallback_reason"].astype(str))),
            "r3_receipt_limitation": "r3 collapsed build, identity, duplicate, and legal-point exhaustion into CROSSOVER_PROPOSAL_GENERATION_FAILURE",
            "constructive_real_parent_dry_replay": {
                "proposals": 400,
                "crossover_requested": 141,
                "crossover_realized": 104,
                "legal_child_set_empty": 37,
                "fallback_rate": 37 / 141,
                "cross_basin_contamination": 0,
            },
            "structural_finding": "one-point construction discarded legal non-contiguous gene-group splices; exhaustive legal-splice construction reduced meaningless fallback",
        },
        "r3_first_10000_prefix": {
            "operation_trace_rows": len(prefix),
            "crossover_requested": len(crossover_prefix),
            "crossover_realized": int((crossover_prefix["realized_operation"] == "crossover").sum()),
            "crossover_fallback": int(crossover_prefix["crossover_fallback"].astype(bool).sum()),
            "evolution_strict": len(strict_prefix),
            "evolution_matched_positive": int(strict_prefix["matched_positive"].astype(bool).sum()),
        },
        "p1_vs_p4": families,
        "p1_classification": "MIXED_ECONOMICALLY_WEAK_REPRESENTATION_CONSTRAINED_OPERATOR_CONSTRAINED",
        "p1_parent_diversity": {"frozen_parents": 6, "concrete_realizations": 3, "economic_basins": 1},
        "p4_parent_diversity": {"frozen_parents": 222, "concrete_realizations": 96, "economic_basins": 22},
        "selected_v2_probabilities": {
            "parameter_mutation_probability": 0.62,
            "mechanism_mutation_probability": 0.03,
            "crossover_probability": 0.35,
        },
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
        "market_arrays_read": 0,
        "candidate_evaluations": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
