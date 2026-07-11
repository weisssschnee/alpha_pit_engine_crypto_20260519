from __future__ import annotations

import math
from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from alphafactory_crypto.b1s_canary import FrozenPanel
from alphafactory_crypto.nextgen_epoch import portfolio_series


@dataclass(frozen=True)
class DevelopmentFeedback:
    coverage: float
    observations: int
    net_mean: float
    net_lcb: float
    worst_block: float
    positive_block_fraction: float
    stability_lcb: float
    turnover_mean: float
    cost_drag_mean: float
    concentration: float
    benchmark_increment_mean: float
    benchmark_increment_lcb: float
    early_gate_pass: bool
    gate_reasons: str
    survivor_near_miss_score: float
    limited_scalar: float


@dataclass(frozen=True)
class QuotaPlan:
    requested: int
    identity_capacity: int
    mechanism_family_count: int
    feasible_quota: int
    family_cap: int
    parent_cap: int
    behaviour_cap: int
    natural_underfill: int


@dataclass(frozen=True)
class AdmissionOutcome:
    admitted_ids: tuple[str, ...]
    rejected: tuple[tuple[str, str], ...]
    plan: QuotaPlan


def development_feedback(
    weights: np.ndarray,
    panel: FrozenPanel,
    benchmark_net: np.ndarray,
    *,
    cost_bps: float = 5.0,
    minimum_assets: int = 5,
) -> DevelopmentFeedback:
    target = np.asarray(panel.target_return, dtype=float)
    active = (np.abs(weights) > 1e-12).sum(axis=0)
    target_assets = np.isfinite(target).sum(axis=0)
    coordinate = (active >= minimum_assets) & (target_assets >= minimum_assets)
    gross, _ = portfolio_series(weights[:, coordinate], target[:, coordinate], 0.0)
    net, turnover = portfolio_series(weights[:, coordinate], target[:, coordinate], cost_bps)
    finite = np.isfinite(net)
    gross, net, turnover = gross[finite], net[finite], turnover[finite]
    observations = len(net)
    net_mean = float(np.mean(net)) if observations else float("nan")
    net_std = float(np.std(net)) if observations else float("nan")
    net_lcb = net_mean - 1.96 * net_std / math.sqrt(observations) if observations else float("nan")
    times = panel.timestamps[coordinate][finite]
    block_means = pd.Series(net).groupby(pd.PeriodIndex(times, freq="M")).mean().to_numpy(dtype=float)
    worst = float(np.min(block_means)) if len(block_means) else float("nan")
    positive = float(np.mean(block_means > 0)) if len(block_means) else 0.0
    block_std = float(np.std(block_means)) if len(block_means) else float("inf")
    stability_lcb = float(np.mean(block_means) - block_std) if len(block_means) else float("nan")
    benchmark = np.asarray(benchmark_net, dtype=float)[coordinate][finite]
    incremental = net - benchmark
    inc_mean = float(np.mean(incremental)) if len(incremental) else float("nan")
    inc_std = float(np.std(incremental)) if len(incremental) else float("nan")
    inc_lcb = inc_mean - 1.96 * inc_std / math.sqrt(len(incremental)) if len(incremental) else float("nan")
    selected_weights = weights[:, coordinate]
    concentration = float(np.mean(np.max(np.abs(selected_weights), axis=0))) if coordinate.any() else float("inf")
    turnover_mean = float(np.mean(turnover)) if observations else float("inf")
    reasons: list[str] = []
    coverage = float(coordinate.mean())
    if coverage < 0.80:
        reasons.append("COVERAGE")
    if observations < 100:
        reasons.append("OBSERVATIONS")
    if turnover_mean > 1.50:
        reasons.append("TURNOVER")
    if concentration > 0.25:
        reasons.append("CONCENTRATION")
    if positive < 0.25:
        reasons.append("STABILITY")
    if not np.isfinite(net_lcb) or not np.isfinite(inc_lcb):
        reasons.append("NON_FINITE")
    near = sum((
        net_lcb > -0.00010,
        worst > -0.0010,
        positive >= 0.40,
        inc_lcb > -0.00010,
        turnover_mean <= 1.20,
    )) / 5.0
    # Novelty is deliberately absent: it cannot compensate negative net or instability.
    scalar = (
        4000.0 * np.nan_to_num(net_lcb, nan=-0.01)
        + 1800.0 * np.nan_to_num(worst, nan=-0.01)
        + 2500.0 * np.nan_to_num(inc_lcb, nan=-0.01)
        + 1.5 * positive
        + 1200.0 * np.nan_to_num(stability_lcb, nan=-0.01)
        - 0.20 * min(turnover_mean, 10.0)
        - 0.50 * min(concentration, 1.0)
    )
    if reasons:
        scalar -= 2.0 + 0.5 * len(reasons)
    return DevelopmentFeedback(
        coverage, observations, net_mean, net_lcb, worst, positive, stability_lcb,
        turnover_mean, float(np.mean(gross - net)) if observations else float("nan"), concentration,
        inc_mean, inc_lcb, not reasons, "|".join(reasons), float(near), float(scalar),
    )


def quota_plan(rows: Sequence[Mapping[str, Any]], requested: int) -> QuotaPlan:
    identities = {str(row["full_exact_identity"]) for row in rows if str(row.get("full_exact_identity", ""))}
    families = {str(row["mechanism_id"]) for row in rows if str(row.get("full_exact_identity", ""))}
    capacity = len(identities)
    family_count = max(1, len(families))
    feasible = min(requested, capacity)
    # With one legal family the cap equals the requested quota; with more families it prevents domination
    # while leaving at least 1.5x average capacity for naturally uneven mechanisms.
    family_cap = requested if family_count == 1 else max(2, math.ceil(requested / family_count * 1.5))
    return QuotaPlan(
        requested=requested, identity_capacity=capacity, mechanism_family_count=family_count,
        feasible_quota=feasible, family_cap=family_cap,
        parent_cap=max(4, math.ceil(requested / max(4, family_count * 2))),
        behaviour_cap=max(4, math.ceil(requested / max(8, family_count * 2))),
        natural_underfill=requested - feasible,
    )


def admit_full_identity(rows: Sequence[Mapping[str, Any]], requested: int) -> AdmissionOutcome:
    plan = quota_plan(rows, requested)
    representatives: dict[str, Mapping[str, Any]] = {}
    for row in sorted(rows, key=lambda item: (int(item["ordinal"]), str(item["proposal_id"]))):
        identity = str(row.get("full_exact_identity", ""))
        if identity:
            representatives.setdefault(identity, row)
    buckets = {
        family: deque(items.to_dict("records"))
        for family, items in pd.DataFrame(list(representatives.values())).groupby("mechanism_id", sort=True)
    }
    keys = sorted(buckets)
    admitted: list[str] = []
    rejected: list[tuple[str, str]] = []
    parents: Counter[str] = Counter()
    families: Counter[str] = Counter()
    behaviours: Counter[str] = Counter()
    while len(admitted) < plan.feasible_quota and any(len(bucket) for bucket in buckets.values()):
        progressed = False
        for family in keys:
            if len(admitted) >= plan.feasible_quota or not len(buckets[family]):
                continue
            row = dict(buckets[family].popleft())
            progressed = True
            proposal = str(row["proposal_id"])
            parent = str(row["parent_identity"])
            behaviour = str(row["behaviour_cluster"])
            if families[family] >= plan.family_cap:
                rejected.append((proposal, "FAMILY_CAP")); continue
            if parents[parent] >= plan.parent_cap:
                rejected.append((proposal, "PARENT_CAP")); continue
            if behaviours[behaviour] >= plan.behaviour_cap:
                rejected.append((proposal, "BEHAVIOUR_CAP")); continue
            admitted.append(proposal)
            families[family] += 1; parents[parent] += 1; behaviours[behaviour] += 1
        if not progressed:
            break
    return AdmissionOutcome(tuple(admitted), tuple(rejected), plan)


def normalized_entropy(values: Iterable[str]) -> float:
    counts = np.asarray(list(Counter(values).values()), dtype=float)
    if len(counts) <= 1:
        return 0.0
    probability = counts / counts.sum()
    return float(-np.sum(probability * np.log(probability)) / np.log(len(counts)))


def concentration_metrics(rows: pd.DataFrame, score_column: str = "development_scalar") -> dict[str, float]:
    legal = rows[rows["legal"]].nlargest(max(1, int(rows["legal"].sum()) // 10), score_column)
    return {
        "mechanism_entropy": normalized_entropy(rows.loc[rows["legal"], "mechanism_id"]),
        "primitive_entropy": normalized_entropy(rows.loc[rows["legal"], "primitive"]),
        "behaviour_cluster_entropy": normalized_entropy(rows.loc[rows["legal"], "behaviour_cluster"]),
        "top_decile_mechanism_share": float(legal["mechanism_id"].value_counts(normalize=True).iloc[0]) if len(legal) else 0.0,
        "top_decile_primitive_share": float(legal["primitive"].value_counts(normalize=True).iloc[0]) if len(legal) else 0.0,
        "top_decile_behaviour_share": float(legal["behaviour_cluster"].value_counts(normalize=True).iloc[0]) if len(legal) else 0.0,
    }


def adaptive_verdict(adaptive: Mapping[str, float], control: Mapping[str, float]) -> str:
    conditions = (
        adaptive["near_miss_per_strict"] > control["near_miss_per_strict"] or adaptive["survivor_per_strict"] > control["survivor_per_strict"],
        adaptive["cluster_yield"] >= 0.90 * control["cluster_yield"],
        adaptive["top_concentration"] <= control["top_concentration"] + 0.05,
        adaptive["runtime_per_proposal"] <= 2.0 * control["runtime_per_proposal"],
        adaptive["benchmark_increment_median"] >= control["benchmark_increment_median"],
    )
    return "ADAPTIVE_SUCCESS" if all(conditions) else "ADAPTIVE_FAILURE_NO_SURVIVOR_GAIN"


def epoch0_failure_matrix(strict: pd.DataFrame) -> pd.DataFrame:
    criteria = pd.DataFrame({
        "hard_gate": strict["hard_gate_pass"], "net_lcb": strict["net_lcb"] > 0,
        "benchmark_increment": strict["benchmark_incremental_lcb"] > 0,
        "ic_lcb": strict["ic_lcb"] > 0, "worst_block": strict["worst_horizon_net_mean"] > -0.001,
    })
    return pd.DataFrame([
        {"failure_axis": "proposal_quality", "affected_rows": int((~criteria["ic_lcb"]).sum()), "evidence": "non-positive IC LCB"},
        {"failure_axis": "admission_quota_waste", "affected_rows": 1936, "evidence": "BBO Epoch-0 FAMILY_BUDGET_CAP rejections"},
        {"failure_axis": "identity_dedup_timing", "affected_rows": 103, "evidence": "main stratified sketch-to-full identity slot loss"},
        {"failure_axis": "scalar_survivor_misalignment", "affected_rows": int((~criteria["net_lcb"]).sum()), "evidence": "scalar discovery without positive net LCB"},
        {"failure_axis": "cost_turnover", "affected_rows": int(((strict["gross_mean"] > 0) & (strict["net_mean"] <= 0)).sum()), "evidence": "positive gross flipped non-positive after cost"},
        {"failure_axis": "stability_worst_block", "affected_rows": int((strict["time_block_positive_fraction"] < 0.5).sum()), "evidence": "less than half positive development blocks"},
        {"failure_axis": "benchmark_increment", "affected_rows": int((~criteria["benchmark_increment"]).sum()), "evidence": "non-positive benchmark incremental LCB"},
        {"failure_axis": "adaptive_proxy_basin", "affected_rows": 1, "evidence": "UCT top mechanism/primitive concentration 66.58%/63.93%"},
    ])
