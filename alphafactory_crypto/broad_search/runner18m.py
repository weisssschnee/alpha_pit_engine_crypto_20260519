"""Evidence-qualified runner for the bounded 18M compositional development search."""

from __future__ import annotations

import concurrent.futures
import ctypes
import gc
import hashlib
import json
import math
import os
import random
import subprocess
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
import psutil

from alphafactory_crypto.instrument_capability.mapping import (
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    mapping_contract_sha256,
)
from alphafactory_crypto.instrument_canary.release import sha256_file

from .compositional18m import (
    CandidateSpec,
    MECHANISM_FAMILIES,
    audit_numeric_expressivity,
    generate_candidate,
    generate_structural_pool,
    skeleton_payload,
    skeleton_registry,
)
from .expression import FieldContract, TypedExpressionRegistry
from .pair18m import (
    FIXED_COST_BPS,
    evaluate_pair,
    feedback_contract_payload,
    pair_contract_payload,
    robust_monthly_audit,
)
from .panel18m import (
    RawPanelStore,
    build_raw_panel_cache,
    field_equivalence_audit,
    qualify_fields,
)


EPOCH_ID = "CRYPTO_18M_COMPOSITIONAL_BROAD_ALPHA_SEARCH_EPOCH1"
POLICIES = (
    "canonical_typed_random",
    "cem_diversity_v2",
    "uct_ucb_like",
    "evolutionary",
)
SEEDS = (20260716, 20260717, 20260718, 20260719)
ADAPTIVE_START = "2023-07-01T00:00:00Z"
ADAPTIVE_END = "2024-07-01T00:00:00Z"
REPORT_ONLY_START = "2024-07-01T00:00:00Z"
REPORT_ONLY_END = "2025-01-01T00:00:00Z"

RUNTIME_OUTPUTS = (
    "CRYPTO_18M_SEARCH_CONTRACT.json",
    "CRYPTO_18M_FIELD_ADMISSION_AUDIT.csv",
    "CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY.json",
    "CRYPTO_FIELD_EQUIVALENCE_AUDIT.csv",
    "CRYPTO_DYNAMIC_ELIGIBILITY_LEDGER.parquet",
    "CRYPTO_COMPOSITIONAL_SKELETON_REGISTRY.json",
    "CRYPTO_GENERATOR_EXPRESSIVITY_AUDIT.json",
    "CRYPTO_MATCHED_ABLATION_PAIR_CONTRACT.json",
    "CRYPTO_PAIR_NATIVE_FEEDBACK_CONTRACT.json",
    "CRYPTO_PROPOSAL_EXPOSURE_LEDGER.parquet",
    "CRYPTO_ADMISSION_WATERFALL.csv",
    "CRYPTO_STRICT_PAIR_RESULTS.parquet",
    "CRYPTO_INCREMENTAL_SLEEVE_RESULTS.parquet",
    "CRYPTO_DEVELOPMENT_CHALLENGE_RESULTS.parquet",
    "CRYPTO_ROBUST_STATISTICAL_AUDIT.parquet",
    "CRYPTO_BEHAVIOR_CLUSTERS.json",
    "CRYPTO_CROSS_SEED_REPRODUCTION.json",
    "CRYPTO_POLICY_BEHAVIOR_AUDIT.json",
    "CRYPTO_RESOURCE_PREFLIGHT.json",
    "CRYPTO_SEARCH_DECISION.json",
    "CRYPTO_ARTIFACT_MANIFEST.json",
)


def _git_sha(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()


def _git_clean(repo_root: Path) -> bool:
    output = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=repo_root, text=True
    )
    return not output.strip()


def _source_tree_clean_for_run(
    repo_root: Path, *, allowed_paths: Sequence[Path]
) -> bool:
    output = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo_root,
        text=True,
    )
    allowed = [path.resolve() for path in allowed_paths]
    for line in output.splitlines():
        raw = line[3:].strip().strip('"').replace("/", os.sep)
        path = (repo_root / raw).resolve()
        if not any(path == root or root in path.parents for root in allowed):
            return False
    return True


def _payload_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
        ).encode("utf-8")
    ).hexdigest().upper()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _contracts_payload(contracts: Sequence[FieldContract]) -> list[dict[str, Any]]:
    return [
        {
            "field_id": item.field_id,
            "value_type": item.value_type,
            "unit": item.unit,
            "observable_lag_hours": item.observable_lag_hours,
            "pit_authority": item.pit_authority,
        }
        for item in contracts
    ]


def _contracts_from_payload(rows: Sequence[Mapping[str, Any]]) -> tuple[FieldContract, ...]:
    return tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
            str(row["pit_authority"]),
        )
        for row in rows
    )


def _trim_working_set() -> None:
    gc.collect()
    if os.name == "nt":
        try:
            ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
        except (AttributeError, OSError):
            pass


@dataclass(slots=True)
class LanePolicy:
    policy: str
    seed: int
    registry: TypedExpressionRegistry
    rng: random.Random = field(init=False)
    seen: set[str] = field(default_factory=set)
    rewards: dict[str, float] = field(default_factory=dict)
    candidates: dict[str, CandidateSpec] = field(default_factory=dict)
    skeleton_visits: Counter[str] = field(default_factory=Counter)
    skeleton_rewards: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    step: int = 0

    def __post_init__(self) -> None:
        if self.policy not in POLICIES:
            raise ValueError(self.policy)
        self.rng = random.Random(self.seed)

    def state_hash(self) -> str:
        return _payload_sha(
            {
                "policy": self.policy,
                "seed": self.seed,
                "step": self.step,
                "seen": sorted(self.seen),
                "rewards": sorted(self.rewards.items()),
                "rng": repr(self.rng.getstate()),
            }
        )

    def _mean_reward(self, skeleton_id: str) -> float:
        values = self.skeleton_rewards.get(skeleton_id, [])
        return float(np.mean(values)) if values else -11.0

    def _choose_skeleton(self) -> tuple[Any, str | None]:
        skeletons = skeleton_registry()
        parent_id: str | None = None
        if self.policy == "canonical_typed_random":
            return skeletons[(self.step + self.seed) % len(skeletons)], None
        if self.policy == "cem_diversity_v2":
            explore = self.step < 8 or self.rng.random() < 0.20
            if explore:
                return skeletons[(self.step + self.seed) % len(skeletons)], None
            scores = np.asarray([max(-10.0, self._mean_reward(item.skeleton_id)) for item in skeletons])
            weights = np.exp(scores - np.max(scores)) + 1e-6
            selected = self.rng.choices(skeletons, weights=weights.tolist(), k=1)[0]
            return selected, None
        if self.policy == "uct_ucb_like":
            unvisited = [item for item in skeletons if self.skeleton_visits[item.skeleton_id] == 0]
            if unvisited:
                return unvisited[0], None
            total = max(1, sum(self.skeleton_visits.values()))
            selected = max(
                skeletons,
                key=lambda item: self._mean_reward(item.skeleton_id)
                + math.sqrt(2.0 * math.log(total) / self.skeleton_visits[item.skeleton_id]),
            )
            return selected, None
        if self.step < 8 or not self.rewards:
            return skeletons[(self.step + self.seed) % len(skeletons)], None
        elites = sorted(self.rewards, key=lambda key: (self.rewards[key], key), reverse=True)[:8]
        parent_id = self.rng.choice(elites)
        parent = self.candidates[parent_id]
        selected = next(item for item in skeletons if item.skeleton_id == parent.skeleton_id)
        return selected, parent_id

    def propose(self) -> tuple[CandidateSpec, dict[str, Any]]:
        before = self.state_hash()
        skeleton, parent_id = self._choose_skeleton()
        candidate: CandidateSpec | None = None
        duplicate_resamples = 0
        for duplicate_resamples in range(17):
            candidate = generate_candidate(self.registry, skeleton=skeleton, rng=self.rng)
            if candidate.candidate_id not in self.seen:
                break
        assert candidate is not None
        if candidate.candidate_id in self.seen:
            raise RuntimeError("duplicate resample limit exhausted")
        changed: list[str] = []
        if parent_id is not None:
            parent = self.candidates[parent_id]
            for name in ("raw_fields", "rolling_windows", "horizon_hours", "operator_path"):
                if getattr(parent, name) != getattr(candidate, name):
                    changed.append(name)
        self.seen.add(candidate.candidate_id)
        self.candidates[candidate.candidate_id] = candidate
        self.skeleton_visits[candidate.skeleton_id] += 1
        metadata = {
            "proposal_step": self.step,
            "policy_state_hash_before": before,
            "parent_id": parent_id,
            "mutation_receipt": {
                "parent_id": parent_id,
                "child_id": candidate.candidate_id,
                "changed_genes": changed,
            }
            if parent_id is not None
            else None,
            "duplicate_resamples": duplicate_resamples,
            "first_visit": True,
            "cache_hit": False,
            "cumulative_skeleton_exposure": self.skeleton_visits[candidate.skeleton_id],
        }
        self.step += 1
        return candidate, metadata

    def update(self, candidate: CandidateSpec, reward: float) -> None:
        if candidate.candidate_id not in self.seen:
            raise PermissionError("unvisited candidate cannot receive feedback")
        if candidate.candidate_id in self.rewards:
            raise PermissionError("candidate feedback is immutable")
        value = float(reward)
        if not math.isfinite(value):
            value = -11.0
        self.rewards[candidate.candidate_id] = value
        self.skeleton_rewards[candidate.skeleton_id].append(value)


def _flat_pair_row(
    *,
    candidate: CandidateSpec,
    evaluation: Mapping[str, Any] | None,
    policy: str,
    seed: int,
    metadata: Mapping[str, Any],
    error: str | None,
) -> dict[str, Any]:
    if evaluation is None:
        reward = -11.0
        matched = False
        incremental: Mapping[str, Any] = {}
        timings: Mapping[str, Any] = {}
    else:
        reward = float(evaluation["pair_reward"])
        matched = bool(evaluation["matched_positive"])
        incremental = evaluation["incremental"]
        timings = evaluation["timings"]
    return {
        "candidate_id": candidate.candidate_id,
        "skeleton_id": candidate.skeleton_id,
        "mechanism_family": candidate.mechanism_family,
        "policy": policy,
        "seed": int(seed),
        "proposal_step": int(metadata["proposal_step"]),
        "parent_id": metadata.get("parent_id"),
        "mutation_receipt_json": json.dumps(metadata.get("mutation_receipt"), sort_keys=True),
        "policy_state_hash_before": metadata["policy_state_hash_before"],
        "first_visit": bool(metadata["first_visit"]),
        "cache_hit": bool(metadata["cache_hit"]),
        "duplicate_resamples": int(metadata["duplicate_resamples"]),
        "cumulative_skeleton_exposure": int(metadata["cumulative_skeleton_exposure"]),
        "pair_evaluation_status": "PASS" if evaluation is not None else "FAIL",
        "failure_reason": error,
        "pair_reward": reward,
        "matched_positive": matched,
        "net_mean": incremental.get("net_mean"),
        "net_lcb": incremental.get("net_lcb"),
        "gross_mean": incremental.get("gross_mean"),
        "turnover_mean": incremental.get("turnover_mean"),
        "cost_mean": incremental.get("cost_mean"),
        "support": incremental.get("support"),
        "positive_month_fraction": incremental.get("positive_month_fraction"),
        "median_month": incremental.get("median_month"),
        "worst_month": incremental.get("worst_month"),
        "delta_weight_sha256": incremental.get("weight_sha256"),
        "candidate_spec_json": json.dumps(candidate.to_dict(), sort_keys=True),
        "evaluation_json": json.dumps(evaluation, sort_keys=True, default=str) if evaluation is not None else None,
        "field_read_seconds": timings.get("field_read_seconds"),
        "dag_materialization_seconds": timings.get("dag_materialization_seconds"),
        "mapping_seconds": timings.get("mapping_seconds"),
        "standalone_evaluator_seconds": timings.get("standalone_evaluator_seconds"),
        "incremental_sleeve_seconds": timings.get("incremental_sleeve_seconds"),
        "pair_peak_rss_bytes": timings.get("peak_rss_bytes"),
        "pair_peak_private_bytes": timings.get("peak_private_bytes"),
    }


def _run_lane_worker(
    cache_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    policy_name: str,
    seed: int,
    count: int,
    prior_rows: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    store = RawPanelStore.open(Path(cache_root))
    registry = TypedExpressionRegistry(_contracts_from_payload(contract_rows))
    policy = LanePolicy(policy_name, int(seed), registry)
    replay_pass = True
    for prior in prior_rows or ():
        candidate, _ = policy.propose()
        if candidate.candidate_id != prior["candidate_id"]:
            replay_pass = False
            raise AssertionError("deterministic policy replay changed candidate identity")
        policy.update(candidate, float(prior["pair_reward"]))
    rows: list[dict[str, Any]] = []
    process = psutil.Process(os.getpid())
    peak_rss = process.memory_info().rss
    peak_private = getattr(process.memory_info(), "private", peak_rss)
    started = time.perf_counter()
    for _ in range(int(count)):
        candidate, metadata = policy.propose()
        evaluation = None
        error = None
        try:
            evaluation = evaluate_pair(
                store=store,
                registry=registry,
                candidate=candidate,
                block_start=ADAPTIVE_START,
                block_end=ADAPTIVE_END,
                block_role="DEVELOPMENT_ADAPTIVE_FEEDBACK",
            )
        except (ValueError, FloatingPointError, MemoryError) as failure:
            error = type(failure).__name__ + ":" + str(failure)
        row = _flat_pair_row(
            candidate=candidate,
            evaluation=evaluation,
            policy=policy_name,
            seed=seed,
            metadata=metadata,
            error=error,
        )
        policy.update(candidate, float(row["pair_reward"]))
        row["policy_state_hash_after"] = policy.state_hash()
        rows.append(row)
        peak_rss = max(
            peak_rss,
            int(row.get("pair_peak_rss_bytes") or 0),
        )
        peak_private = max(
            peak_private,
            int(row.get("pair_peak_private_bytes") or 0),
        )
        del evaluation
        _trim_working_set()
    return {
        "policy": policy_name,
        "seed": seed,
        "rows": rows,
        "elapsed_seconds": time.perf_counter() - started,
        "peak_rss_bytes": peak_rss,
        "peak_private_bytes": peak_private,
        "deterministic_replay_pass": replay_pass,
    }


def _challenge_worker(
    cache_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    store = RawPanelStore.open(Path(cache_root))
    registry = TypedExpressionRegistry(_contracts_from_payload(contract_rows))
    output: list[dict[str, Any]] = []
    for row in rows:
        candidate = CandidateSpec.from_dict(json.loads(str(row["candidate_spec_json"])))
        evaluation = None
        error = None
        try:
            evaluation = evaluate_pair(
                store=store,
                registry=registry,
                candidate=candidate,
                block_start=REPORT_ONLY_START,
                block_end=REPORT_ONLY_END,
                block_role="DEVELOPMENT_REPORT_ONLY_NO_FEEDBACK",
            )
        except (ValueError, FloatingPointError, MemoryError) as failure:
            error = type(failure).__name__ + ":" + str(failure)
        output.append(
            {
                "candidate_id": candidate.candidate_id,
                "skeleton_id": candidate.skeleton_id,
                "mechanism_family": candidate.mechanism_family,
                "policy": row["policy"],
                "seed": int(row["seed"]),
                "pair_evaluation_status": "PASS" if evaluation is not None else "FAIL",
                "failure_reason": error,
                "pair_reward": float(evaluation["pair_reward"]) if evaluation else -11.0,
                "matched_positive": bool(evaluation["matched_positive"]) if evaluation else False,
                "net_mean": evaluation["incremental"]["net_mean"] if evaluation else None,
                "net_lcb": evaluation["incremental"]["net_lcb"] if evaluation else None,
                "positive_month_fraction": evaluation["incremental"]["positive_month_fraction"] if evaluation else None,
                "median_month": evaluation["incremental"]["median_month"] if evaluation else None,
                "worst_month": evaluation["incremental"]["worst_month"] if evaluation else None,
                "delta_weight_sha256": evaluation["incremental"]["weight_sha256"] if evaluation else None,
                "evaluation_json": json.dumps(evaluation, sort_keys=True, default=str) if evaluation else None,
                "policy_feedback_written": False,
            }
        )
        del evaluation
        _trim_working_set()
    return output


def _parallel_lanes(
    *,
    cache_root: Path,
    contracts: Sequence[FieldContract],
    lanes: Sequence[tuple[str, int]],
    count_per_lane: int,
    max_workers: int,
    prior: Mapping[tuple[str, int], Sequence[Mapping[str, Any]]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contract_rows = _contracts_payload(contracts)
    rows: list[dict[str, Any]] = []
    resources: list[dict[str, Any]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _run_lane_worker,
                str(cache_root),
                contract_rows,
                policy,
                seed,
                count_per_lane,
                list((prior or {}).get((policy, seed), ())),
            ): (policy, seed)
            for policy, seed in lanes
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            rows.extend(result["rows"])
            resources.append({key: value for key, value in result.items() if key != "rows"})
            print(
                json.dumps(
                    {
                        "event": "strict_lane_complete",
                        "policy": result["policy"],
                        "seed": result["seed"],
                        "pairs": len(result["rows"]),
                        "seconds": result["elapsed_seconds"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    rows.sort(key=lambda row: (int(row["seed"]), POLICIES.index(str(row["policy"])), int(row["proposal_step"])))
    return rows, resources


def _parallel_challenge(
    *,
    cache_root: Path,
    contracts: Sequence[FieldContract],
    rows: Sequence[Mapping[str, Any]],
    max_workers: int,
    chunk_size: int = 32,
) -> list[dict[str, Any]]:
    contracts_payload = _contracts_payload(contracts)
    chunks = [rows[index : index + chunk_size] for index in range(0, len(rows), chunk_size)]
    output: list[dict[str, Any]] = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_challenge_worker, str(cache_root), contracts_payload, chunk)
            for chunk in chunks
        ]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            output.extend(future.result())
            if index % 8 == 0 or index == len(futures):
                print(
                    json.dumps(
                        {
                            "event": "report_only_challenge_progress",
                            "chunks_complete": index,
                            "chunks_total": len(futures),
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )
    output.sort(key=lambda row: (int(row["seed"]), POLICIES.index(str(row["policy"])), str(row["candidate_id"])))
    return output


def _cluster_key(row: Mapping[str, Any]) -> str:
    candidate = CandidateSpec.from_dict(json.loads(str(row["candidate_spec_json"])))
    return _payload_sha(
        {
            "mechanism_family": candidate.mechanism_family,
            "skeleton_id": candidate.skeleton_id,
            "field_families": sorted(candidate.field_families),
            "operator_path": candidate.operator_path,
        }
    )


def _cluster_evidence(
    adaptive: Sequence[Mapping[str, Any]], challenge: Sequence[Mapping[str, Any]]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    challenge_map = {str(row["candidate_id"]): row for row in challenge}
    groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in adaptive:
        enriched = dict(row)
        enriched["cluster_id"] = _cluster_key(row)
        groups[enriched["cluster_id"]].append(enriched)
    cluster_rows: list[dict[str, Any]] = []
    reproduced: list[dict[str, Any]] = []
    for cluster_id, rows in groups.items():
        adaptive_positive = [row for row in rows if bool(row["matched_positive"])]
        challenge_positive = [
            row
            for row in rows
            if bool(challenge_map.get(str(row["candidate_id"]), {}).get("matched_positive", False))
        ]
        seeds = sorted({int(row["seed"]) for row in challenge_positive})
        item = {
            "cluster_id": cluster_id,
            "mechanism_family": rows[0]["mechanism_family"],
            "skeleton_id": rows[0]["skeleton_id"],
            "candidates": len(rows),
            "adaptive_matched_positive": len(adaptive_positive),
            "challenge_matched_positive": len(challenge_positive),
            "challenge_positive_seeds": seeds,
            "cross_seed_reproduced": len(seeds) >= 2,
        }
        cluster_rows.append(item)
        if item["cross_seed_reproduced"]:
            reproduced.append(item)
    family_rows = []
    for family in MECHANISM_FAMILIES:
        local = [row for row in adaptive if row["mechanism_family"] == family]
        challenge_local = [challenge_map.get(str(row["candidate_id"]), {}) for row in local]
        family_rows.append(
            {
                "mechanism_family": family,
                "strict_pairs": len(local),
                "adaptive_matched_positive": sum(bool(row["matched_positive"]) for row in local),
                "challenge_matched_positive": sum(bool(row.get("matched_positive")) for row in challenge_local),
                "challenge_positive_yield": sum(bool(row.get("matched_positive")) for row in challenge_local) / max(1, len(local)),
            }
        )
    clusters = {"schema_version": 1, "clusters": sorted(cluster_rows, key=lambda row: row["cluster_id"]), "family_yield": family_rows}
    reproduction = {"schema_version": 1, "cross_seed_reproduced_clusters": len(reproduced), "clusters": reproduced}
    counts = {
        "adaptive_positive_clusters": sum(row["adaptive_matched_positive"] > 0 for row in cluster_rows),
        "challenge_positive_clusters": sum(row["challenge_matched_positive"] > 0 for row in cluster_rows),
        "cross_seed_reproduced_clusters": len(reproduced),
        "reproduced_families": len({row["mechanism_family"] for row in reproduced}),
        "maximum_family_challenge_yield": max((row["challenge_positive_yield"] for row in family_rows), default=0.0),
    }
    return clusters, reproduction, counts


def _policy_audit(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summaries = []
    by_lane: dict[tuple[str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_lane[(str(row["policy"]), int(row["seed"]))].append(row)
    for (policy, seed), local in sorted(by_lane.items()):
        summaries.append(
            {
                "policy": policy,
                "seed": seed,
                "pairs": len(local),
                "unique_candidates": len({row["candidate_id"] for row in local}),
                "mean_pair_reward": float(np.mean([float(row["pair_reward"]) for row in local])),
                "matched_positive": sum(bool(row["matched_positive"]) for row in local),
                "mutation_receipts": sum(str(row["mutation_receipt_json"]) != "null" for row in local),
                "cache_hits": sum(bool(row["cache_hit"]) for row in local),
            }
        )
    random_by_seed = {
        row["seed"]: row["mean_pair_reward"]
        for row in summaries
        if row["policy"] == "canonical_typed_random"
    }
    stable_improvement: dict[str, bool] = {}
    for policy in POLICIES[1:]:
        margins = [
            row["mean_pair_reward"] - random_by_seed.get(row["seed"], float("nan"))
            for row in summaries
            if row["policy"] == policy
        ]
        stable_improvement[policy] = len(margins) >= 2 and sum(value > 0 for value in margins) >= 2
    return {
        "schema_version": 1,
        "lanes": summaries,
        "adaptive_policy_quality_improvement_vs_typed_random": stable_improvement,
        "any_cross_seed_stable_policy_improvement": any(stable_improvement.values()),
        "unvisited_candidate_feedback": 0,
        "cross_policy_private_state_reads": 0,
        "deterministic_replay_required": True,
    }


def _robust_rows(
    adaptive: Sequence[Mapping[str, Any]], challenge: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    challenge_map = {str(row["candidate_id"]): row for row in challenge}
    rows: list[dict[str, Any]] = []
    for ordinal, adaptive_row in enumerate(adaptive):
        evaluation = json.loads(str(adaptive_row["evaluation_json"])) if adaptive_row.get("evaluation_json") else None
        challenge_row = challenge_map.get(str(adaptive_row["candidate_id"]))
        challenge_evaluation = (
            json.loads(str(challenge_row["evaluation_json"]))
            if challenge_row and challenge_row.get("evaluation_json")
            else None
        )
        adaptive_months = (
            [row["net_mean"] for row in evaluation["incremental"]["month_metrics"]]
            if evaluation
            else []
        )
        challenge_months = (
            [row["net_mean"] for row in challenge_evaluation["incremental"]["month_metrics"]]
            if challenge_evaluation
            else []
        )
        audit = robust_monthly_audit(
            [*adaptive_months, *challenge_months], seed=20260716 + ordinal
        )
        rows.append(
            {
                "candidate_id": adaptive_row["candidate_id"],
                "mechanism_family": adaptive_row["mechanism_family"],
                "policy": adaptive_row["policy"],
                "seed": int(adaptive_row["seed"]),
                "adaptive_net_mean": adaptive_row.get("net_mean"),
                "challenge_net_mean": challenge_row.get("net_mean") if challenge_row else None,
                "adaptive_challenge_sign_agreement": bool(
                    challenge_row
                    and adaptive_row.get("net_mean") is not None
                    and challenge_row.get("net_mean") is not None
                    and np.sign(float(adaptive_row["net_mean"])) == np.sign(float(challenge_row["net_mean"]))
                ),
                **audit,
            }
        )
    return rows


def _waterfall(
    structural: Mapping[str, Any],
    expressivity: Mapping[str, Any],
    adaptive: Sequence[Mapping[str, Any]],
    challenge: Sequence[Mapping[str, Any]],
    robust: Sequence[Mapping[str, Any]],
    reproduction: Mapping[str, Any],
) -> pd.DataFrame:
    pass_rows = [row for row in adaptive if row["pair_evaluation_status"] == "PASS"]
    challenge_pass = [row for row in challenge if row["pair_evaluation_status"] == "PASS"]
    stages = [
        ("proposal_attempts", structural["proposal_attempts"]),
        ("grammar_legal", structural["grammar_legal"]),
        ("PIT_unit_pass", structural["grammar_legal"]),
        ("exact_unique", structural["exact_unique"]),
        ("numeric_unique", expressivity["numeric_unique"]),
        ("behavior_unique", expressivity["behavior_unique"]),
        ("control_valid", expressivity["matched_control_valid"]),
        ("materialization_pass", len(pass_rows)),
        ("dynamic_support_pass", sum(float(row.get("support") or 0.0) >= 0.80 for row in pass_rows)),
        ("standalone_evaluation_pass", len(pass_rows) * 2),
        ("incremental_sleeve_pass", len(pass_rows)),
        ("adaptive_matched_positive", sum(bool(row["matched_positive"]) for row in pass_rows)),
        ("challenge_evaluation_pass", len(challenge_pass)),
        ("challenge_matched_positive", sum(bool(row["matched_positive"]) for row in challenge_pass)),
        ("robust_positive", sum(bool(row["robust_positive"]) for row in robust)),
        ("cross_seed_reproduced", int(reproduction["cross_seed_reproduced_clusters"])),
    ]
    return pd.DataFrame([{"stage": stage, "count": int(count)} for stage, count in stages])


def _failure_attribution(
    *,
    field_count: int,
    expressivity: Mapping[str, Any],
    adaptive: Sequence[Mapping[str, Any]],
    challenge: Sequence[Mapping[str, Any]],
    resource: Mapping[str, Any],
) -> tuple[str, list[str], dict[str, int]]:
    failures = Counter(
        str(row["failure_reason"]).split(":", 1)[-1]
        for row in adaptive
        if row["pair_evaluation_status"] != "PASS"
    )
    if field_count < 16:
        return "FIELD_AUTHORIZATION_NARROW", [], dict(failures)
    if expressivity["status"] != "PASS":
        mapping = {
            "COMPOSITIONAL_GENERATOR_TEMPLATE_COLLAPSE": "GENERATOR_TEMPLATE_COLLAPSE",
            "SEMANTIC_ALIAS_COLLAPSE": "SEMANTIC_ALIAS_COLLAPSE",
            "MATCHED_CONTROL_CONSTRUCTION_BOTTLENECK": "MATCHED_CONTROL_FAILURE",
            "FIELD_COMBINATION_UNDERCOVERAGE": "GENERATOR_TEMPLATE_COLLAPSE",
        }
        return mapping.get(str(expressivity["status"]), "GENERATOR_TEMPLATE_COLLAPSE"), [], dict(failures)
    if not bool(resource.get("stage_a_authorized")):
        return "COMPUTE_OR_IO_BOTTLENECK", [], dict(failures)
    if failures:
        primary = failures.most_common(1)[0][0]
        mapping = {
            "DYNAMIC_UNIVERSE_SUPPORT_COLLAPSE": "DYNAMIC_UNIVERSE_SUPPORT_COLLAPSE",
            "CONTROL_BEHAVIOR_EQUALS_PRIMARY": "MATCHED_CONTROL_FAILURE",
            "CONTROL_EXACT_IDENTITY_EQUALS_PRIMARY": "MATCHED_CONTROL_FAILURE",
        }
        token = mapping.get(primary, "DAG_MATERIALIZATION_FAILURE")
    else:
        passed = [row for row in adaptive if row["pair_evaluation_status"] == "PASS"]
        gross_positive = sum(float(row.get("gross_mean") or 0.0) > 0.0 for row in passed)
        matched = sum(bool(row["matched_positive"]) for row in passed)
        challenge_matched = sum(bool(row["matched_positive"]) for row in challenge)
        if matched and not challenge_matched:
            token = "ADAPTIVE_ONLY_OVERFIT"
        elif not gross_positive:
            token = "NO_GROSS_EDGE"
        elif not matched:
            turnover_dominated = sum(
                float(row.get("gross_mean") or 0.0) > 0.0
                and float(row.get("net_mean") or 0.0) <= 0.0
                for row in passed
            )
            token = "TURNOVER_COST_DOMINATED" if turnover_dominated > len(passed) / 2 else "CONTROL_NOT_BEATEN"
        else:
            token = "CHALLENGE_INSTABILITY"
    secondary = [key for key, _ in failures.most_common(3) if key != token]
    return token, secondary, dict(failures)


def _main_status(
    *,
    field_count: int,
    expressivity: Mapping[str, Any],
    resource: Mapping[str, Any],
    counts: Mapping[str, int],
    robust_positive_clusters: int,
    primary_bottleneck: str,
) -> str:
    if field_count < 16:
        return "CRYPTO_18M_FIELD_AUTHORIZATION_BOTTLENECK"
    if expressivity["status"] != "PASS":
        return "CRYPTO_18M_COMPOSITIONAL_GENERATOR_BOTTLENECK"
    if not resource.get("stage_a_authorized"):
        return "CRYPTO_18M_COMPUTE_OR_IO_BOTTLENECK"
    if counts["cross_seed_reproduced_clusters"] >= 3 and counts["reproduced_families"] >= 2 and robust_positive_clusters >= 3:
        return "CRYPTO_18M_COMPOSITIONAL_SEARCH_REPRODUCIBLE_MECHANISMS_FOUND"
    if counts["challenge_positive_clusters"] > 0:
        return "CRYPTO_18M_COMPOSITIONAL_SEARCH_LOCALIZED_MECHANISMS_ONLY"
    if primary_bottleneck == "ADAPTIVE_ONLY_OVERFIT":
        return "CRYPTO_18M_COMPOSITIONAL_SEARCH_ADAPTIVE_OVERFIT"
    if primary_bottleneck in {
        "MATCHED_CONTROL_FAILURE",
        "DAG_MATERIALIZATION_FAILURE",
    }:
        return "CRYPTO_18M_MATCHED_CONTROL_BOTTLENECK"
    if primary_bottleneck in {
        "DYNAMIC_UNIVERSE_SUPPORT_COLLAPSE",
        "MAPPING_DEGENERACY",
        "TURNOVER_COST_DOMINATED",
    }:
        return "CRYPTO_18M_SUPPORT_OR_COST_BOTTLENECK"
    return "CRYPTO_18M_COMPOSITIONAL_SEARCH_NO_EDGE_UNDER_CURRENT_AUTHORIZED_FIELDS"


def _report_text(decision: Mapping[str, Any]) -> str:
    return f"""# Crypto 18M Compositional Broad Search

## Decision

`{decision['main_status']}`

This is development-only evidence on the observed official archive/current-seed
surface.  The six-month report-only block is not formal validation, challenge,
forward, recent, or OOS evidence and never fed the search policy.

## Frozen execution

- source SHA: `{decision['source_sha']}`
- base closure: `{decision['base_closure_sha']}`
- admitted fields: {decision['admitted_field_count']} across {decision['field_family_count']} families
- proposal attempts: {decision['proposal_attempts']:,}
- strict adaptive pairs: {decision['strict_pairs']:,}
- report-only pair evaluations: {decision['report_only_pairs']:,}
- standalone evaluator calls: {decision['standalone_evaluator_calls']:,}
- incremental sleeve calls: {decision['incremental_sleeve_calls']:,}
- sealed reads: {decision['sealed_reads']}

## Evidence

- adaptive matched-positive clusters: {decision['adaptive_matched_positive_clusters']}
- report-only matched-positive clusters: {decision['challenge_matched_positive_clusters']}
- robust-positive candidates: {decision['robust_positive_candidates']}
- cross-seed reproduced clusters: {decision['cross_seed_reproduced_clusters']}
- primary bottleneck: `{decision['primary_bottleneck']}`

## Claim boundary

No formal OOS, full delisted-contract coverage, promotion, execution
recommendation, native aggTrades microstructure, or live-trading conclusion is
authorized.  Candidate promotion and all 2025+ reads remain forbidden.
"""


def _failure_report_text(decision: Mapping[str, Any]) -> str:
    rows = "\n".join(
        f"| {key} | {value} |" for key, value in sorted(decision["failure_counts"].items())
    ) or "| NONE | 0 |"
    return f"""# Crypto 18M Search Failure Attribution

Primary bottleneck: `{decision['primary_bottleneck']}`.

Secondary bottlenecks: {', '.join(decision['secondary_bottlenecks']) or 'none'}.

| Failure | Count |
|---|---:|
{rows}

The classification is layer-specific.  It must not be generalized to
`DATA_UNDERPOWERED` or `NO_ALPHA` outside the authorized field registry,
typed DAG, mapping, cost, and observed-archive scope.
"""


def _validate_config(config: Mapping[str, Any]) -> None:
    if config["base_closure_sha"].lower() != "a115913ae333696482059b497472864871cebc9f":
        raise ValueError("base data authority changed")
    boundaries = config["boundaries"]
    for key in (
        "sealed_reads_allowed",
        "formal_performance_search",
        "candidate_promotion",
        "cross_sprint_adaptive_memory",
    ):
        if bool(boundaries[key]):
            raise PermissionError(f"forbidden boundary enabled: {key}")
    budget = config["budget"]
    if int(budget["proposal_attempts"]) < 500000:
        raise ValueError("structural budget is below 500,000")
    if int(budget["stage_a_pairs"]) != 4096 or int(budget["hard_cap_pairs"]) != 8192:
        raise ValueError("strict pair budget changed")
    if tuple(int(value) for value in budget["seeds"]) != SEEDS:
        raise ValueError("seed contract changed")
    if tuple(budget["policies"]) != POLICIES:
        raise ValueError("policy contract changed")


def build_evidence(
    repo_root: Path, *, config_path: Path, source_sha: str | None = None
) -> dict[str, Any]:
    config = _read_json(config_path)
    _validate_config(config)
    source_sha = (source_sha or _git_sha(repo_root)).lower()
    if source_sha != _git_sha(repo_root):
        raise ValueError("runtime must bind the checked-out source implementation SHA")
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    cache_root = repo_root / config["cache_root"]
    report_path = repo_root / config["outputs"]["report"]
    failure_path = repo_root / config["outputs"]["failure_report"]
    if not _source_tree_clean_for_run(
        repo_root, allowed_paths=(runtime_root, report_path, failure_path)
    ):
        raise RuntimeError("source execution requires a clean implementation tree; only its own generated evidence may exist")
    runtime_root.mkdir(parents=True, exist_ok=True)
    train_config_path = repo_root / config["train_surface_config"]
    train_config = _read_json(train_config_path)
    train_decision = _read_json(
        repo_root
        / train_config["outputs"]["runtime_root"]
        / "CRYPTO_TRAIN_DATA_ADEQUACY.json"
    )
    if train_decision["decision"] != "PASS_CRYPTO_TRAIN_SURFACE_18M_DEVELOPMENT_READY_WITH_SCOPE_LIMITS":
        raise PermissionError("18M train authority is not qualified")

    search_contract = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "authorization": "EXPERIMENTAL_BOUNDED_18M_DEVELOPMENT_SEARCH",
        "base_closure_sha": config["base_closure_sha"],
        "source_sha": source_sha,
        "train_surface_id": train_config["surface_id"],
        "train_content_bundle_sha256": train_decision["source_content_bundle_sha256"],
        "adaptive_block": {"start": ADAPTIVE_START, "end_exclusive": ADAPTIVE_END, "feedback": True},
        "development_report_only_block": {"start": REPORT_ONLY_START, "end_exclusive": REPORT_ONLY_END, "feedback": False},
        "target": "log(close[t+2+h] / close[t+2])",
        "horizons_hours": [1, 4],
        "dynamic_eligibility": "observed at t, required inputs available at t, at least 168 completed consecutive hours; no future survival selection",
        "boundaries": config["boundaries"],
        "budget": config["budget"],
    }
    _write_json(runtime_root / RUNTIME_OUTPUTS[0], search_contract)

    store, quality, registry_rows, cache_metadata = build_raw_panel_cache(
        repo_root,
        train_config=train_config,
        cache_root=cache_root,
        eligibility_path=runtime_root / RUNTIME_OUTPUTS[4],
        source_sha=source_sha,
        warmup_hours=int(config["dynamic_eligibility"]["minimum_history_hours"]),
    )
    equivalence = field_equivalence_audit(store, quality["field_id"].tolist())
    field_audit, field_registry, contracts = qualify_fields(
        quality=quality,
        registry_rows=registry_rows,
        equivalence=equivalence,
        current_runtime_fields=train_config["runtime_fields"],
    )
    field_audit.to_csv(runtime_root / RUNTIME_OUTPUTS[1], index=False, lineterminator="\n")
    _write_json(runtime_root / RUNTIME_OUTPUTS[2], field_registry)
    equivalence.to_csv(runtime_root / RUNTIME_OUTPUTS[3], index=False, lineterminator="\n")
    skeletons = skeleton_payload()
    _write_json(runtime_root / RUNTIME_OUTPUTS[5], skeletons)
    _write_json(runtime_root / RUNTIME_OUTPUTS[7], pair_contract_payload())
    _write_json(runtime_root / RUNTIME_OUTPUTS[8], feedback_contract_payload())

    registry = TypedExpressionRegistry(contracts)
    structural_candidates, structural = generate_structural_pool(
        registry,
        attempts=int(config["budget"]["proposal_attempts"]),
        seed=int(config["budget"]["seeds"][0]),
        retain=int(config["expressivity"]["numeric_audit_candidates"]),
    )
    expressivity = audit_numeric_expressivity(
        store=store,
        registry=registry,
        candidates=structural_candidates,
        structural=structural,
        maximum_candidates=int(config["expressivity"]["numeric_audit_candidates"]),
    )
    _write_json(runtime_root / RUNTIME_OUTPUTS[6], expressivity)

    max_workers = int(config["resources"]["max_workers"])
    preflight_lanes = [
        ("canonical_typed_random", SEEDS[0]),
        ("canonical_typed_random", SEEDS[1]),
        ("cem_diversity_v2", SEEDS[0]),
        ("cem_diversity_v2", SEEDS[1]),
    ]
    preflight_started = time.perf_counter()
    preflight_rows, preflight_resources = _parallel_lanes(
        cache_root=cache_root,
        contracts=contracts,
        lanes=preflight_lanes,
        count_per_lane=16,
        max_workers=max_workers,
    )
    preflight_seconds = time.perf_counter() - preflight_started
    preflight_pass = sum(row["pair_evaluation_status"] == "PASS" for row in preflight_rows)
    estimated_stage_a_seconds = preflight_seconds * int(config["budget"]["stage_a_pairs"]) / 64.0
    peak_rss = max((int(row["peak_rss_bytes"]) for row in preflight_resources), default=0)
    stage_a_authorized = (
        len(contracts) >= 16
        and len(field_registry["field_families"]) >= 5
        and expressivity["status"] == "PASS"
        and preflight_pass == 64
        and estimated_stage_a_seconds <= float(config["resources"]["maximum_estimated_stage_a_seconds"])
        and peak_rss <= int(config["resources"]["maximum_worker_peak_rss_bytes"])
    )
    resource = {
        "schema_version": 1,
        "cache_build": cache_metadata,
        "preflight_pairs": 64,
        "preflight_pass": preflight_pass,
        "preflight_seconds": preflight_seconds,
        "pair_seconds": [sum(float(row.get(name) or 0.0) for name in ("field_read_seconds", "dag_materialization_seconds", "mapping_seconds", "standalone_evaluator_seconds", "incremental_sleeve_seconds")) for row in preflight_rows],
        "worker_resources": preflight_resources,
        "peak_worker_rss_bytes": peak_rss,
        "estimated_stage_a_seconds": estimated_stage_a_seconds,
        "estimated_stage_a_plus_report_only_seconds": estimated_stage_a_seconds * 2.0,
        "max_workers": max_workers,
        "stage_a_authorized": stage_a_authorized,
        "stage_a_authorization_requirements": {
            "fields_at_least_16": len(contracts) >= 16,
            "field_families_at_least_5": len(field_registry["field_families"]) >= 5,
            "generator_expressivity_pass": expressivity["status"] == "PASS",
            "preflight_64_of_64": preflight_pass == 64,
            "time_budget": estimated_stage_a_seconds <= float(config["resources"]["maximum_estimated_stage_a_seconds"]),
            "rss_budget": peak_rss <= int(config["resources"]["maximum_worker_peak_rss_bytes"]),
        },
    }
    _write_json(runtime_root / RUNTIME_OUTPUTS[18], resource)

    adaptive_rows: list[dict[str, Any]] = []
    challenge_rows: list[dict[str, Any]] = []
    lane_resources: list[dict[str, Any]] = []
    if stage_a_authorized:
        lanes = [(policy, seed) for seed in SEEDS for policy in POLICIES]
        per_lane = int(config["budget"]["stage_a_pairs"]) // len(lanes)
        stage_a, stage_a_resources = _parallel_lanes(
            cache_root=cache_root,
            contracts=contracts,
            lanes=lanes,
            count_per_lane=per_lane,
            max_workers=max_workers,
        )
        adaptive_rows.extend(stage_a)
        lane_resources.extend(stage_a_resources)
        stage_a_challenge = _parallel_challenge(
            cache_root=cache_root,
            contracts=contracts,
            rows=stage_a,
            max_workers=max_workers,
        )
        challenge_rows.extend(stage_a_challenge)
        clusters_a, reproduction_a, counts_a = _cluster_evidence(stage_a, stage_a_challenge)
        policy_a = _policy_audit(stage_a)
        continue_stage_b = (
            counts_a["adaptive_positive_clusters"] >= 10
            or counts_a["challenge_positive_clusters"] >= 5
            or counts_a["maximum_family_challenge_yield"] > 0.005
            or bool(policy_a["any_cross_seed_stable_policy_improvement"])
        )
        if continue_stage_b:
            prior: dict[tuple[str, int], list[Mapping[str, Any]]] = defaultdict(list)
            for row in stage_a:
                prior[(str(row["policy"]), int(row["seed"]))].append(row)
            stage_b, stage_b_resources = _parallel_lanes(
                cache_root=cache_root,
                contracts=contracts,
                lanes=lanes,
                count_per_lane=int(config["budget"]["maximum_stage_b_pairs"]) // len(lanes),
                max_workers=max_workers,
                prior=prior,
            )
            adaptive_rows.extend(stage_b)
            lane_resources.extend(stage_b_resources)
            challenge_rows.extend(
                _parallel_challenge(
                    cache_root=cache_root,
                    contracts=contracts,
                    rows=stage_b,
                    max_workers=max_workers,
                )
            )
    if len(adaptive_rows) > int(config["budget"]["hard_cap_pairs"]):
        raise AssertionError("strict hard cap exceeded")

    policy_audit = _policy_audit(adaptive_rows)
    policy_audit["lane_resources"] = lane_resources
    policy_audit["development_report_only_feedback_writes"] = sum(
        bool(row["policy_feedback_written"]) for row in challenge_rows
    )
    _write_json(runtime_root / RUNTIME_OUTPUTS[17], policy_audit)
    clusters, reproduction, counts = _cluster_evidence(adaptive_rows, challenge_rows)
    _write_json(runtime_root / RUNTIME_OUTPUTS[15], clusters)
    _write_json(runtime_root / RUNTIME_OUTPUTS[16], reproduction)
    robust = _robust_rows(adaptive_rows, challenge_rows)
    robust_positive_candidates = sum(bool(row["robust_positive"]) for row in robust)
    robust_positive_clusters = len(
        {
            _cluster_key(row)
            for row, audit in zip(adaptive_rows, robust)
            if bool(audit["robust_positive"])
        }
    )

    exposure = pd.DataFrame(
        [
            {
                key: row[key]
                for key in (
                    "candidate_id",
                    "skeleton_id",
                    "mechanism_family",
                    "policy",
                    "seed",
                    "proposal_step",
                    "parent_id",
                    "mutation_receipt_json",
                    "policy_state_hash_before",
                    "policy_state_hash_after",
                    "first_visit",
                    "cache_hit",
                    "cumulative_skeleton_exposure",
                    "pair_reward",
                )
            }
            for row in adaptive_rows
        ]
    )
    exposure.to_parquet(runtime_root / RUNTIME_OUTPUTS[9], index=False)
    strict = pd.DataFrame(adaptive_rows)
    strict.to_parquet(runtime_root / RUNTIME_OUTPUTS[11], index=False)
    incremental_columns = [
        "candidate_id",
        "skeleton_id",
        "mechanism_family",
        "policy",
        "seed",
        "pair_reward",
        "matched_positive",
        "net_mean",
        "net_lcb",
        "gross_mean",
        "turnover_mean",
        "cost_mean",
        "support",
        "positive_month_fraction",
        "median_month",
        "worst_month",
        "delta_weight_sha256",
    ]
    pd.DataFrame(adaptive_rows, columns=incremental_columns).to_parquet(
        runtime_root / RUNTIME_OUTPUTS[12], index=False
    )
    pd.DataFrame(challenge_rows).to_parquet(runtime_root / RUNTIME_OUTPUTS[13], index=False)
    pd.DataFrame(robust).to_parquet(runtime_root / RUNTIME_OUTPUTS[14], index=False)
    waterfall = _waterfall(structural, expressivity, adaptive_rows, challenge_rows, robust, reproduction)
    waterfall.to_csv(runtime_root / RUNTIME_OUTPUTS[10], index=False, lineterminator="\n")

    primary, secondary, failure_counts = _failure_attribution(
        field_count=len(contracts),
        expressivity=expressivity,
        adaptive=adaptive_rows,
        challenge=challenge_rows,
        resource=resource,
    )
    status = _main_status(
        field_count=len(contracts),
        expressivity=expressivity,
        resource=resource,
        counts=counts,
        robust_positive_clusters=robust_positive_clusters,
        primary_bottleneck=primary,
    )
    decision = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "main_status": status,
        "source_sha": source_sha,
        "base_closure_sha": config["base_closure_sha"],
        "train_surface_id": train_config["surface_id"],
        "train_content_bundle_sha256": train_decision["source_content_bundle_sha256"],
        "admitted_field_count": len(contracts),
        "field_family_count": len(field_registry["field_families"]),
        "proposal_attempts": int(structural["proposal_attempts"]),
        "legal_exact_unique": int(structural["exact_unique"]),
        "numeric_unique": int(expressivity["numeric_unique"]),
        "behavior_unique": int(expressivity["behavior_unique"]),
        "strict_pairs": len(adaptive_rows),
        "stage_a_pairs": min(len(adaptive_rows), int(config["budget"]["stage_a_pairs"])),
        "stage_b_pairs": max(0, len(adaptive_rows) - int(config["budget"]["stage_a_pairs"])),
        "report_only_pairs": len(challenge_rows),
        "standalone_evaluator_calls": 2 * (len(adaptive_rows) + len(challenge_rows)),
        "incremental_sleeve_calls": len(adaptive_rows) + len(challenge_rows),
        "adaptive_matched_positive_clusters": counts["adaptive_positive_clusters"],
        "challenge_matched_positive_clusters": counts["challenge_positive_clusters"],
        "robust_positive_candidates": robust_positive_candidates,
        "robust_positive_clusters": robust_positive_clusters,
        "cross_seed_reproduced_clusters": counts["cross_seed_reproduced_clusters"],
        "reproduced_families": counts["reproduced_families"],
        "primary_bottleneck": primary,
        "secondary_bottlenecks": secondary,
        "failure_counts": failure_counts,
        "sealed_reads": 0,
        "formal_performance_search": "FORBIDDEN",
        "candidate_promotion": "FORBIDDEN",
        "forward": "SEALED",
        "accepted_tag_movement": "FORBIDDEN",
        "claim_scope": "observed-official-archive current-seeded 18M development surface only",
        "cannot_conclude": [
            "formal OOS validity",
            "full historical delisted-contract coverage",
            "live execution or promotion readiness",
            "native aggTrades microstructure validity",
            "all-Crypto-market generality",
        ],
    }
    _write_json(runtime_root / RUNTIME_OUTPUTS[19], decision)
    report_path = repo_root / config["outputs"]["report"]
    failure_path = repo_root / config["outputs"]["failure_report"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_report_text(decision), encoding="utf-8", newline="\n")
    failure_path.write_text(_failure_report_text(decision), encoding="utf-8", newline="\n")

    artifact_paths = [
        runtime_root / name
        for name in RUNTIME_OUTPUTS
        if name != "CRYPTO_ARTIFACT_MANIFEST.json"
    ] + [
        report_path,
        failure_path,
        config_path,
        train_config_path,
        repo_root / "alphafactory_crypto" / "broad_search" / "expression.py",
        repo_root / "alphafactory_crypto" / "broad_search" / "panel18m.py",
        repo_root / "alphafactory_crypto" / "broad_search" / "compositional18m.py",
        repo_root / "alphafactory_crypto" / "broad_search" / "pair18m.py",
        repo_root / "alphafactory_crypto" / "broad_search" / "runner18m.py",
        repo_root / "scripts" / "crypto_18m_compositional_broad_search.py",
        repo_root / "tests" / "test_broad_search_expression.py",
        repo_root / "tests" / "test_crypto_18m_compositional_search.py",
    ]
    artifact_rows = [
        {
            "path": path.relative_to(repo_root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in sorted(set(artifact_paths))
    ]
    manifest = {
        "schema_version": 1,
        "epoch_id": EPOCH_ID,
        "producer_source_sha": source_sha,
        "base_closure_sha": config["base_closure_sha"],
        "bindings": {
            "train_surface_id": train_config["surface_id"],
            "train_content_bundle_sha256": train_decision["source_content_bundle_sha256"],
            "field_registry_hash": field_registry["registry_sha256"],
            "DAG_grammar_hash": _payload_sha(registry.contract_payload()),
            "skeleton_registry_hash": skeletons["skeleton_registry_sha256"],
            "mapping_hash": mapping_contract_sha256(DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]),
            "cost_hash": _payload_sha({"cost_bps": FIXED_COST_BPS, "turnover": "FULL_L1"}),
            "pair_feedback_hash": _payload_sha(feedback_contract_payload()),
            "adaptive_report_only_split_hash": _payload_sha(
                {"adaptive": [ADAPTIVE_START, ADAPTIVE_END], "report_only": [REPORT_ONLY_START, REPORT_ONLY_END]}
            ),
            "seeds": list(SEEDS),
            "budget": config["budget"],
        },
        "sealed_reads": 0,
        "artifacts": artifact_rows,
    }
    manifest["bundle_sha256"] = _payload_sha(artifact_rows)
    _write_json(runtime_root / RUNTIME_OUTPUTS[20], manifest)
    return {
        "result": "PASS",
        "main_status": status,
        "source_sha": source_sha,
        "strict_pairs": len(adaptive_rows),
        "report_only_pairs": len(challenge_rows),
        "sealed_reads": 0,
        "bundle_sha256": manifest["bundle_sha256"],
    }


def check_evidence(repo_root: Path, *, config_path: Path) -> dict[str, Any]:
    config = _read_json(config_path)
    _validate_config(config)
    runtime_root = repo_root / config["outputs"]["runtime_root"]
    manifest_path = runtime_root / "CRYPTO_ARTIFACT_MANIFEST.json"
    errors: list[str] = []
    if not manifest_path.is_file():
        return {"result": "FAIL", "errors": ["missing artifact manifest"]}
    manifest = _read_json(manifest_path)
    for record in manifest.get("artifacts", []):
        path = (repo_root / record["path"]).resolve()
        try:
            path.relative_to(repo_root.resolve())
        except ValueError:
            errors.append(f"path_escape:{record['path']}")
            continue
        if not path.is_file():
            errors.append(f"missing:{record['path']}")
        elif path.stat().st_size != int(record["bytes"]) or sha256_file(path) != record["sha256"]:
            errors.append(f"identity:{record['path']}")
    if _payload_sha(manifest.get("artifacts", [])) != manifest.get("bundle_sha256"):
        errors.append("bundle_sha256")
    decision = _read_json(runtime_root / "CRYPTO_SEARCH_DECISION.json")
    resource = _read_json(runtime_root / "CRYPTO_RESOURCE_PREFLIGHT.json")
    field_registry = _read_json(runtime_root / "CRYPTO_18M_COMPOSITIONAL_FIELD_REGISTRY.json")
    expressivity = _read_json(runtime_root / "CRYPTO_GENERATOR_EXPRESSIVITY_AUDIT.json")
    policy = _read_json(runtime_root / "CRYPTO_POLICY_BEHAVIOR_AUDIT.json")
    if decision.get("sealed_reads") != 0 or manifest.get("sealed_reads") != 0:
        errors.append("sealed_reads")
    if decision.get("formal_performance_search") != "FORBIDDEN" or decision.get("candidate_promotion") != "FORBIDDEN":
        errors.append("boundary_status")
    if field_registry.get("field_count", 0) >= 16 and expressivity.get("status") == "PASS" and resource.get("stage_a_authorized"):
        if int(decision.get("stage_a_pairs", 0)) != 4096:
            errors.append("stage_a_pair_count")
    if int(decision.get("strict_pairs", 0)) > 8192:
        errors.append("hard_cap")
    if policy.get("development_report_only_feedback_writes") != 0:
        errors.append("report_only_feedback")
    try:
        subprocess.check_call(
            ["git", "cat-file", "-e", f"{manifest['producer_source_sha']}^{{commit}}"],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        errors.append("producer_source_sha")
    return {
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "main_status": decision.get("main_status"),
        "producer_source_sha": manifest.get("producer_source_sha"),
        "bundle_sha256": manifest.get("bundle_sha256"),
        "strict_pairs": decision.get("strict_pairs"),
        "sealed_reads": decision.get("sealed_reads"),
    }


__all__ = [
    "ADAPTIVE_END",
    "ADAPTIVE_START",
    "EPOCH_ID",
    "POLICIES",
    "REPORT_ONLY_END",
    "REPORT_ONLY_START",
    "RUNTIME_OUTPUTS",
    "SEEDS",
    "LanePolicy",
    "build_evidence",
    "check_evidence",
]
