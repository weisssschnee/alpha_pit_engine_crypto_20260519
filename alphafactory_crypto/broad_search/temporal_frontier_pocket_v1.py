"""Frozen-anchor, train-only local search policy for the two frontier pockets."""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from .compositional18m import CandidateSpec, temporal_mechanism_candidate_from_genes
from .temporal_hypothesis_frontier_v1 import P5, P6, rebuild_frontier_candidate
from .temporal_targeted_deepening_v1 import (
    _cluster_labels,
    _fingerprint_matrix,
    _realization_id,
)


ANCHORS = {
    P5: {
        "candidate_id": "92879E90E1587A4D951DEBE2F94B2AAD1C30F0D3DB52D4B4E12C31C688B0F2CF",
        "program_id": "TEMPORAL_FRONTIER_V1_34A11C69FE06AC49E4820772793355ED",
        "seed": 3823740441,
    },
    P6: {
        "candidate_id": "C6F2ED2519831A1AA58E3FAFA932DA2A79CDAB13DD56F72159C9A80B1C282252",
        "program_id": "TEMPORAL_FRONTIER_V1_AD96002D012C7C2B2021C20FC245F471",
        "seed": 2099206231,
    },
}
P5_PARTICIPATION_FIELDS = (
    "trade_count_gt_1m",
    "trade_count_100k_1m",
    "agg_trade_count",
    "underlying_trade_count",
)
P6_FUNDING_FIELDS = (
    "bybit__funding_rate_mean",
    "bybit__funding_rate_last",
    "bybit__funding_rate_min",
    "bybit__funding_rate_max",
    "bybit__funding_rate_std",
)
P6_FLOW_FIELDS = (
    "buy_sell_notional_ratio",
    "volume_imbalance",
    "signed_aggressor_notional",
    "signed_aggressor_quantity",
)
WINDOWS = (6, 12, 24, 48, 72, 168, 336, 720)
PERSISTENCE_WINDOWS = (2, 4, 8, 12, 24)
NORMALIZERS = ("RollingZScore", "VolatilityScale", "HistoricalPercentile")
BETAS = (-1.0, -0.5, 0.5, 1.0)


def _sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest().upper()


def load_anchor_rows(ledger_path: Path) -> dict[str, dict[str, Any]]:
    frame = pd.read_parquet(ledger_path)
    if len(frame) != 30_000:
        raise RuntimeError("FRONTIER_SOURCE_LEDGER_ROW_COUNT_CHANGED")
    rows: dict[str, dict[str, Any]] = {}
    for family, expected in ANCHORS.items():
        local = frame.loc[frame["candidate_id"].astype(str) == expected["candidate_id"]]
        if len(local) != 1:
            raise RuntimeError(f"FRONTIER_ANCHOR_RECOVERY_CHANGED:{family}:{len(local)}")
        row = local.iloc[0].to_dict()
        if (
            not bool(row.get("matched_positive"))
            or str(row.get("program_family_id")) != family
            or str(row.get("program_id")) != expected["program_id"]
            or int(row.get("seed")) != expected["seed"]
        ):
            raise RuntimeError(f"FRONTIER_ANCHOR_IDENTITY_CHANGED:{family}")
        rows[family] = row
    return rows


def rebuild_anchors(registry: Any, rows: Mapping[str, Mapping[str, Any]]) -> dict[str, CandidateSpec]:
    output: dict[str, CandidateSpec] = {}
    for family, row in rows.items():
        candidate = CandidateSpec.from_dict(json.loads(str(row["candidate_spec_json"])))
        rebuilt = rebuild_frontier_candidate(registry, candidate)
        if rebuilt.candidate_id != candidate.candidate_id or candidate.candidate_id != ANCHORS[family]["candidate_id"]:
            raise RuntimeError(f"FRONTIER_ANCHOR_REBUILD_CHANGED:{family}")
        output[family] = candidate
    return output


def anchor_receipt(rows: Mapping[str, Mapping[str, Any]], candidates: Mapping[str, CandidateSpec], *, ledger_sha256: str) -> dict[str, Any]:
    anchors = {}
    for family in (P5, P6):
        candidate = candidates[family]
        row = rows[family]
        anchors[family] = {
            **ANCHORS[family],
            "candidate_spec_sha256": _sha(candidate.to_dict()),
            "mechanism_id": str(candidate.generation_genes["mechanism_id"]),
            "mapping_id": candidate.mapping_id,
            "matched_positive": bool(row["matched_positive"]),
            "replicated_positive_block_count": int(row["replicated_positive_block_count"]),
            "worst_block_min_matched_net_mean": float(row["development_worst_block_min_matched_net"]),
        }
    core = {
        "schema_version": 1,
        "status": "FRONTIER_POCKET_ANCHORS_EXACTLY_RECOVERED",
        "source_ledger_rows": 30_000,
        "source_ledger_sha256": ledger_sha256,
        "anchors": anchors,
        "validation_reads": 0,
        "oos_reads": 0,
        "holdout_reads": 0,
        "forward_reads": 0,
        "promotion_reads": 0,
        "sealed_reads": 0,
    }
    return {**core, "anchor_receipt_sha256": _sha(core)}


def local_genes(anchor: CandidateSpec, family: str, rng: random.Random, *, exact_binding_weight: float = 0.60) -> dict[str, Any]:
    genes = json.loads(json.dumps(anchor.generation_genes))
    exact_binding = rng.random() < exact_binding_weight
    if family == P5:
        genes["left_field"] = "buy_sell_notional_ratio"
        genes["right_field"] = "trade_count_gt_1m" if exact_binding else rng.choice(P5_PARTICIPATION_FIELDS)
        genes["left_window"] = rng.choice(WINDOWS)
        genes["right_window"] = rng.choice(WINDOWS)
        genes["left_normalizer"] = rng.choice(NORMALIZERS)
        genes["right_normalizer"] = rng.choice(NORMALIZERS)
        genes["beta"] = 0.5
        transform = dict(genes["temporal_transform"])
        transform.update({"primitive_id": "Persistence", "axis": "left", "window": rng.choice(PERSISTENCE_WINDOWS), "long_window": None, "threshold": 0.0, "placement": "POST_NORMALIZER"})
        genes["temporal_transform"] = transform
    elif family == P6:
        genes["left_field"] = "bybit__funding_rate_mean" if exact_binding else rng.choice(P6_FUNDING_FIELDS)
        genes["right_field"] = "buy_sell_notional_ratio" if exact_binding else rng.choice(P6_FLOW_FIELDS)
        genes["left_window"] = rng.choice(WINDOWS)
        genes["right_window"] = rng.choice(WINDOWS)
        genes["left_normalizer"] = rng.choice(NORMALIZERS)
        genes["right_normalizer"] = rng.choice(NORMALIZERS)
        genes["beta"] = rng.choice(BETAS)
        transform = dict(genes["temporal_transform"])
        transform.update({"primitive_id": "Transition", "axis": "left", "window": None, "long_window": None, "threshold": 0.0, "placement": "POST_NORMALIZER"})
        genes["temporal_transform"] = transform
    else:
        raise ValueError("FRONTIER_POCKET_FAMILY_OUT_OF_SCOPE")
    return genes


def propose_local(
    registry: Any,
    anchor: CandidateSpec,
    family: str,
    rng: random.Random,
    *,
    exact_binding_weight: float = 0.60,
) -> CandidateSpec:
    candidate = temporal_mechanism_candidate_from_genes(
        registry,
        genes=local_genes(
            anchor,
            family,
            rng,
            exact_binding_weight=exact_binding_weight,
        ),
    )
    if (
        candidate.mapping_id != anchor.mapping_id
        or candidate.skeleton_id != anchor.skeleton_id
        or str(candidate.generation_genes["mechanism_spec"]["program_id"]) != ANCHORS[family]["program_id"]
        or str(candidate.generation_genes["mechanism_spec"]["template_id"]) != family
    ):
        raise RuntimeError("RESEARCH_INVALID:POCKET_CORE_SEMANTICS_DRIFT")
    return candidate


def classify_against_anchor(anchor_row: Mapping[str, Any], row: Mapping[str, Any]) -> tuple[str, float | None]:
    if not bool(row.get("matched_positive")):
        block = json.loads(str(row.get("block_robust_ordering_json") or "{}"))
        replicated = int(block.get("replicated_positive_block_count") or row.get("replicated_positive_block_count") or 0)
        return ("NEAR_MISS" if replicated >= 2 else "OTHER", None)
    matrix = _fingerprint_matrix([anchor_row, row])
    labels = _cluster_labels(matrix, 0.90)
    centered = matrix - matrix.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(centered, axis=1)
    similarity = float(np.dot(centered[0], centered[1]) / max(float(norms[0] * norms[1]), 1.0e-12))
    return ("ANCHOR_POCKET" if labels[0] == labels[1] else "LOCAL_NEW_BASIN", similarity)


def realization_id(row: Mapping[str, Any]) -> str:
    return _realization_id(row)


__all__ = [
    "ANCHORS", "P5_PARTICIPATION_FIELDS", "P6_FLOW_FIELDS", "P6_FUNDING_FIELDS",
    "anchor_receipt", "classify_against_anchor", "load_anchor_rows", "propose_local",
    "realization_id", "rebuild_anchors",
]
