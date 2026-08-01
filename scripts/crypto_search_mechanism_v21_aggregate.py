"""Freeze V2 mechanism outcomes as aggregate-only V2.1 catalog knowledge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


MINIMUM_SUPPORT = 32
SHRINKAGE_PRIOR_STRENGTH = 32.0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _top_decile_mean(values: Iterable[float]) -> float | None:
    array = np.asarray(tuple(float(value) for value in values), dtype=float)
    if not array.size:
        return None
    count = max(1, int(np.ceil(array.size * 0.10)))
    return float(np.mean(np.sort(array)[-count:]))


def _aggregate(
    frame: pd.DataFrame,
    dimensions: tuple[str, ...],
    *,
    global_mean: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, local in frame.groupby(list(dimensions), dropna=False, sort=True):
        keys = key if isinstance(key, tuple) else (key,)
        count = int(len(local))
        mean = float(local["search_reward"].mean())
        positive_count = int((local["search_reward"] > 0.0).sum())
        rows.append(
            {
                "dimensions": {
                    name: (None if pd.isna(value) else value)
                    for name, value in zip(dimensions, keys, strict=True)
                },
                "strict_evaluated_count": count,
                "behavior_family_count": int(
                    local["behavior_family_id"].nunique()
                ),
                "positive_search_reward_count": positive_count,
                "positive_search_reward_rate": positive_count / count,
                "mean_search_reward": mean,
                "top_decile_search_reward": _top_decile_mean(
                    local["search_reward"]
                ),
                "shrunk_mean_search_reward": (
                    count * mean + SHRINKAGE_PRIOR_STRENGTH * global_mean
                )
                / (count + SHRINKAGE_PRIOR_STRENGTH),
                "beta_smoothed_positive_rate": (positive_count + 1.0)
                / (count + 2.0),
                "minimum_support_met": count >= MINIMUM_SUPPORT,
            }
        )
    return rows


def build(input_path: Path) -> dict[str, Any]:
    ledger = pd.read_parquet(input_path)
    mechanism_rows: list[dict[str, Any]] = []
    for raw in ledger["candidate_spec_json"]:
        candidate = json.loads(str(raw))
        genes = dict(candidate.get("generation_genes") or {})
        spec = dict(genes.get("mechanism_spec") or {})
        mechanism_rows.append(
            {
                "mechanism_id": spec.get("mechanism_id"),
                "template_id": spec.get("template_id"),
                "generation": spec.get("generation"),
                "left_role": spec.get("left_role"),
                "right_role": spec.get("right_role"),
                "payload_operator": spec.get("payload_operator"),
                "payload_mode": spec.get("payload_mode"),
                "condition_role": spec.get("condition_role"),
                "condition_operator": spec.get("condition_operator"),
                "condition_mode": spec.get("condition_mode"),
                "left_window": genes.get("left_window"),
                "right_window": genes.get("right_window"),
                "condition_window": genes.get("condition_window"),
                "left_normalizer": genes.get("left_normalizer"),
                "right_normalizer": genes.get("right_normalizer"),
                "condition_normalizer": genes.get("condition_normalizer"),
            }
        )
    expanded = pd.concat(
        [ledger.reset_index(drop=True), pd.DataFrame(mechanism_rows)], axis=1
    )
    expanded = expanded.loc[
        expanded["arm"].astype(str) != "canonical_typed_random"
    ].copy()
    global_mean = float(expanded["search_reward"].mean())
    groupings = (
        ("mechanism_id",),
        ("template_id",),
        ("left_role", "right_role", "condition_role"),
        ("payload_operator", "payload_mode"),
        ("condition_operator", "condition_mode"),
        ("horizon_hours",),
        ("left_normalizer",),
        ("right_normalizer",),
        ("condition_normalizer",),
        ("left_window",),
        ("right_window",),
        ("condition_window",),
    )
    return {
        "schema_version": 1,
        "knowledge_id": "CRYPTO_SEARCH_MECHANISM_V2_AGGREGATE_KNOWLEDGE",
        "source_campaign": "crypto_search_mechanism_v2",
        "source_runtime": "runtime/crypto_search_mechanism_v2_20260801",
        "source_candidate_ledger": (
            "runtime/crypto_search_mechanism_v2_20260801/"
            "candidate_ledger.parquet"
        ),
        "source_candidate_ledger_sha256": _sha256(input_path),
        "source_strict_evaluated_count": int(len(ledger)),
        "included_expanded_grammar_count": int(len(expanded)),
        "excluded_legacy_fixed_skeleton_count": int(len(ledger) - len(expanded)),
        "minimum_support": MINIMUM_SUPPORT,
        "shrinkage_prior_strength": SHRINKAGE_PRIOR_STRENGTH,
        "global_mean_search_reward": global_mean,
        "grouped_outcomes": {
            "|".join(dimensions): _aggregate(
                expanded, dimensions, global_mean=global_mean
            )
            for dimensions in groupings
        },
        "usage_contract": {
            "catalog_design_and_lifecycle_only": True,
            "sampling_probability_prior": False,
            "candidate_or_reward_import": False,
            "population_or_distribution_import": False,
            "rng_or_policy_state_import": False,
            "individual_candidate_identity_persisted": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        default="config/crypto_search_mechanism_v2_aggregate_knowledge.json",
    )
    args = parser.parse_args()
    input_path = (
        args.repo_root
        / "runtime/crypto_search_mechanism_v2_20260801/candidate_ledger.parquet"
    )
    output_path = args.repo_root / str(args.output)
    payload = build(input_path)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "result": "PASS",
                "output": str(output_path),
                "source_sha256": payload["source_candidate_ledger_sha256"],
                "grouping_count": len(payload["grouped_outcomes"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
