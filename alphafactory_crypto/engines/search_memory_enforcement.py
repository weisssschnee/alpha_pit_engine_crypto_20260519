from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alphafactory_crypto.engines.search_memory import expression_memory_key, skeleton_memory_key


REQUIRED_DECISION = "PASS_A7MEM0_SEARCH_MEMORY_REGISTRY_BUILT"


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _as_float(value: Any, default: float = 1.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _pair_motif(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("semantic_pair", "") or ""), str(row.get("motif", "") or "")


def _resolve_relocated_path(raw_path: str, *, prior_dir: Path) -> Path:
    path = Path(raw_path)
    if path.exists():
        return path
    relocated = prior_dir / path.name
    if relocated.exists():
        return relocated
    return path


@dataclass(slots=True)
class MemoryDecision:
    allowed: bool
    action: str
    reason: str
    expression_key: str
    skeleton_key: str
    pair_motif: str
    search_weight: float

    def as_row(self) -> dict[str, Any]:
        return {
            "memory_allowed": str(self.allowed),
            "memory_action": self.action,
            "memory_reason": self.reason,
            "memory_expression_key": self.expression_key,
            "memory_skeleton_key": self.skeleton_key,
            "memory_pair_motif": self.pair_motif,
            "memory_search_weight": self.search_weight,
        }


class SearchMemoryEnforcer:
    """Fail-closed A7MEM prior loader and queue-level search memory gate."""

    def __init__(self, *, prior_path: Path) -> None:
        self.prior_path = prior_path
        if not prior_path.exists():
            raise FileNotFoundError(f"search memory prior missing: {prior_path}")
        self.prior = json.loads(prior_path.read_text(encoding="utf-8"))
        if self.prior.get("decision") != REQUIRED_DECISION:
            raise ValueError(f"search memory prior not pass: {self.prior.get('decision')}")
        if self.prior.get("required_for_next_large_search") is not True:
            raise ValueError("search memory prior is not marked required_for_next_large_search")

        prior_dir = prior_path.parent
        self.candidate_memory_path = _resolve_relocated_path(str(self.prior["candidate_memory"]), prior_dir=prior_dir)
        self.rejection_memory_path = (
            _resolve_relocated_path(str(self.prior.get("rejection_memory", "")), prior_dir=prior_dir)
            if self.prior.get("rejection_memory")
            else None
        )
        self.cluster_memory_path = _resolve_relocated_path(str(self.prior["cluster_memory"]), prior_dir=prior_dir)
        self.pair_motif_prior_path = _resolve_relocated_path(str(self.prior["pair_motif_prior"]), prior_dir=prior_dir)

        for path in [self.candidate_memory_path, self.cluster_memory_path, self.pair_motif_prior_path]:
            if not path.exists():
                raise FileNotFoundError(f"search memory referenced file missing: {path}")

        self.cluster_caps = dict(self.prior.get("cluster_caps", {}))
        self.hard_ban_rejection_classes = set(self.prior.get("hard_ban_rejection_classes", []))
        self.candidate_memory = _read_csv(self.candidate_memory_path)
        self.pair_motif_prior = _read_csv(self.pair_motif_prior_path)

        self.seen_expression_keys = {
            row.get("expression_key", "")
            for row in self.candidate_memory
            if row.get("expression_key")
        }
        self.hard_banned_expression_keys = {
            row.get("expression_key", "")
            for row in self.candidate_memory
            if row.get("expression_key") and row.get("rejection_class") in self.hard_ban_rejection_classes
        }
        self.pair_motif_weights: dict[tuple[str, str], float] = {}
        self.pair_motif_actions: dict[tuple[str, str], str] = {}
        for row in self.pair_motif_prior:
            key = _pair_motif(row)
            self.pair_motif_weights[key] = _as_float(row.get("search_weight"), 1.0)
            self.pair_motif_actions[key] = str(row.get("prior_action", "neutral_explore") or "neutral_explore")

        self.max_same_expression_key = int(self.cluster_caps.get("max_same_expression_key", 1))
        self.max_same_skeleton_key_per_shard = int(self.cluster_caps.get("max_same_skeleton_key_per_shard", 2))
        self.max_same_semantic_pair_motif_per_shard = int(self.cluster_caps.get("max_same_semantic_pair_motif_per_shard", 16))

    def decide(self, row: dict[str, Any], counters: dict[str, Counter[str]]) -> MemoryDecision:
        expression = str(row.get("expression", "") or row.get("formula", "") or "")
        expr_key = expression_memory_key(expression)
        skel_key = skeleton_memory_key(expression)
        pair, motif = _pair_motif(row)
        pair_motif = f"{pair}|{motif}"
        weight = self.pair_motif_weights.get((pair, motif), 0.75)
        action = self.pair_motif_actions.get((pair, motif), "neutral_explore")

        if not expression:
            return MemoryDecision(False, "reject", "missing_expression", expr_key, skel_key, pair_motif, 0.0)
        if expr_key in self.hard_banned_expression_keys:
            return MemoryDecision(False, "reject", "hard_banned_expression_memory", expr_key, skel_key, pair_motif, 0.0)
        if counters["expression_key"][expr_key] >= self.max_same_expression_key:
            return MemoryDecision(False, "reject", "duplicate_expression_key_cap", expr_key, skel_key, pair_motif, 0.0)
        if expr_key in self.seen_expression_keys:
            return MemoryDecision(False, "reject", "previously_seen_expression_memory", expr_key, skel_key, pair_motif, 0.0)
        if counters["skeleton_key"][skel_key] >= self.max_same_skeleton_key_per_shard:
            return MemoryDecision(False, "reject", "skeleton_key_cap", expr_key, skel_key, pair_motif, 0.0)
        if counters["pair_motif"][pair_motif] >= self.max_same_semantic_pair_motif_per_shard:
            return MemoryDecision(False, "reject", "pair_motif_cap", expr_key, skel_key, pair_motif, 0.0)
        if action == "downweight_or_ban" and weight <= 0.25:
            return MemoryDecision(True, "downweight", "pair_motif_downweighted", expr_key, skel_key, pair_motif, weight)
        if action in {"promote_with_cluster_cap", "exploit_lightly_with_diversity_cap"}:
            return MemoryDecision(True, "promote", action, expr_key, skel_key, pair_motif, weight)
        return MemoryDecision(True, "neutral", action, expr_key, skel_key, pair_motif, weight)

    def filter_rows(self, rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
        counters: dict[str, Counter[str]] = {
            "expression_key": Counter(),
            "skeleton_key": Counter(),
            "pair_motif": Counter(),
        }
        accepted: list[dict[str, Any]] = []
        trace: list[dict[str, Any]] = []
        action_counts: Counter[str] = Counter()
        reason_counts: Counter[str] = Counter()
        for idx, row in enumerate(rows):
            decision = self.decide(row, counters)
            trace_row = {"row_index": idx, **{k: row.get(k, "") for k in ["blueprint_id", "semantic_pair", "motif", "horizon_h", "expression"]}, **decision.as_row()}
            trace.append(trace_row)
            action_counts[decision.action] += 1
            reason_counts[decision.reason] += 1
            if not decision.allowed:
                continue
            enriched = dict(row)
            enriched.update(decision.as_row())
            accepted.append(enriched)
            counters["expression_key"][decision.expression_key] += 1
            counters["skeleton_key"][decision.skeleton_key] += 1
            counters["pair_motif"][decision.pair_motif] += 1

        manifest = {
            "prior_path": str(self.prior_path),
            "prior_decision": self.prior.get("decision"),
            "input_rows": len(rows),
            "accepted_rows": len(accepted),
            "rejected_rows": len(rows) - len(accepted),
            "action_counts": dict(action_counts),
            "reason_counts": dict(reason_counts),
            "cluster_caps": self.cluster_caps,
            "candidate_memory_rows": len(self.candidate_memory),
            "pair_motif_prior_rows": len(self.pair_motif_prior),
        }
        return accepted, trace, manifest
