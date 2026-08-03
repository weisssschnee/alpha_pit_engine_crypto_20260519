"""Behavior-family-first V2.4 selection and economic-path persistence.

This module is deliberately not a second search engine or evaluator.  It
contains the thin policy-selection and artifact projections needed by the next
fresh-data gate while delegating candidate economics to ``pair18m.evaluate_pair``.
No market run is authorized by the committed contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np


V24_CONTRACT_PATH = "config/crypto_search_engine_v2_4_behavior_family.json"
V24_SELECTION_AUTHORITY = "TRAIN_SEARCH_REWARD_ONLY"
V24_FAMILY_KEY = (
    "arm",
    "seed",
    "horizon_hours",
    "behavior_family_id",
)
V24_CHAMPION_ORDER = (
    "search_reward_desc",
    "arm_completion_ordinal_asc",
    "candidate_id_asc",
)


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest().upper()


def _family_key(row: Mapping[str, Any]) -> tuple[str, int, int, str]:
    family_id = str(row.get("behavior_family_id") or "")
    if not family_id:
        raise ValueError("V24_BEHAVIOR_FAMILY_ID_MISSING")
    return (
        str(row["arm"]),
        int(row["seed"]),
        int(row["horizon_hours"]),
        family_id,
    )


def _champion_order(row: Mapping[str, Any]) -> tuple[float, int, str]:
    reward = float(row["search_reward"])
    if not math.isfinite(reward):
        raise ValueError("V24_TRAIN_SEARCH_REWARD_NON_FINITE")
    return (
        -reward,
        int(row["arm_completion_ordinal"]),
        str(row["candidate_id"]),
    )


def select_behavior_family_champions(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Select one deterministic train-reward champion per arm/seed/horizon/family.

    No validation, OOS, economic outcome, novelty score, or expression count is
    allowed to influence the champion order.  Cells remain separate so one
    seed or horizon cannot donate a champion to another.
    """

    champions: dict[tuple[str, int, int, str], Mapping[str, Any]] = {}
    family_expression_counts: Counter[tuple[str, int, int, str]] = Counter()
    candidate_ids: set[str] = set()
    for row in rows:
        candidate_id = str(row.get("candidate_id") or "")
        if not candidate_id or candidate_id in candidate_ids:
            raise ValueError("V24_CANDIDATE_ID_MISSING_OR_DUPLICATED")
        candidate_ids.add(candidate_id)
        key = _family_key(row)
        family_expression_counts[key] += 1
        previous = champions.get(key)
        if previous is None or _champion_order(row) < _champion_order(previous):
            champions[key] = row

    selected = [
        dict(row)
        for _, row in sorted(
            champions.items(),
            key=lambda item: (
                item[0][0],
                item[0][1],
                item[0][2],
                _champion_order(item[1]),
                item[0][3],
            ),
        )
    ]
    proof_rows = [
        {
            "arm": key[0],
            "seed": key[1],
            "horizon_hours": key[2],
            "behavior_family_id": key[3],
            "expression_count": int(family_expression_counts[key]),
            "champion_candidate_id": str(champions[key]["candidate_id"]),
            "champion_search_reward": float(champions[key]["search_reward"]),
            "champion_arm_completion_ordinal": int(
                champions[key]["arm_completion_ordinal"]
            ),
        }
        for key in sorted(champions)
    ]
    selection_projection = [
        {
            "arm": str(row["arm"]),
            "seed": int(row["seed"]),
            "horizon_hours": int(row["horizon_hours"]),
            "behavior_family_id": str(row["behavior_family_id"]),
            "candidate_id": str(row["candidate_id"]),
            "search_reward": float(row["search_reward"]),
            "arm_completion_ordinal": int(row["arm_completion_ordinal"]),
        }
        for row in selected
    ]
    receipt = {
        "schema_version": 1,
        "selection_unit": "BEHAVIOR_FAMILY",
        "family_key": list(V24_FAMILY_KEY),
        "selection_authority": V24_SELECTION_AUTHORITY,
        "champion_order": list(V24_CHAMPION_ORDER),
        "input_expression_count": len(rows),
        "selected_behavior_family_count": len(selected),
        "duplicate_expression_count": len(rows) - len(selected),
        "family_proof": proof_rows,
        "selection_sha256": _canonical_sha256(selection_projection),
        "validation_or_oos_feedback_used": False,
    }
    return selected, receipt


def select_behavior_family_cohort(
    rows: Sequence[Mapping[str, Any]],
    *,
    per_cell_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return an equal-count top-family cohort for every arm/seed/horizon cell."""

    if int(per_cell_count) < 1:
        raise ValueError("V24_BEHAVIOR_FAMILY_COHORT_COUNT_INVALID")
    champions, champion_receipt = select_behavior_family_champions(rows)
    cells: dict[tuple[str, int, int], list[dict[str, Any]]] = {}
    for row in champions:
        key = (str(row["arm"]), int(row["seed"]), int(row["horizon_hours"]))
        cells.setdefault(key, []).append(row)
    selected: list[dict[str, Any]] = []
    cell_proof: list[dict[str, Any]] = []
    for key in sorted(cells):
        ordered = sorted(cells[key], key=_champion_order)
        if len(ordered) < int(per_cell_count):
            raise RuntimeError(
                "V24_BEHAVIOR_FAMILY_COHORT_UNDERFILLED:"
                + "|".join((key[0], str(key[1]), str(key[2])))
            )
        local = ordered[: int(per_cell_count)]
        selected.extend(local)
        cell_proof.append(
            {
                "arm": key[0],
                "seed": key[1],
                "horizon_hours": key[2],
                "available_family_count": len(ordered),
                "selected_family_count": len(local),
                "selected_candidate_ids": [
                    str(row["candidate_id"]) for row in local
                ],
            }
        )
    projection = [
        {
            "arm": str(row["arm"]),
            "seed": int(row["seed"]),
            "horizon_hours": int(row["horizon_hours"]),
            "behavior_family_id": str(row["behavior_family_id"]),
            "candidate_id": str(row["candidate_id"]),
        }
        for row in selected
    ]
    return selected, {
        "schema_version": 1,
        "selection_unit": "BEHAVIOR_FAMILY",
        "per_arm_seed_horizon_count": int(per_cell_count),
        "cell_count": len(cells),
        "selected_count": len(selected),
        "duplicate_family_backfill_used": False,
        "champion_selection_sha256": champion_receipt["selection_sha256"],
        "cell_proof": cell_proof,
        "cohort_sha256": _canonical_sha256(projection),
    }


def _finite_mean(values: np.ndarray) -> float:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    return float(np.mean(finite)) if finite.size else float("nan")


def build_economic_path_artifacts(
    evaluation: Mapping[str, Any],
    *,
    cohort: str,
    arm: str,
    seed: int,
    horizon_hours: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Project pair18m economic paths to daily sleeves and sparse positions."""

    payload = evaluation.get("_economic_paths")
    if not isinstance(payload, Mapping) or int(payload.get("schema_version", -1)) != 1:
        raise ValueError("V24_ECONOMIC_PATHS_MISSING")
    timestamps = np.asarray(payload["timestamp_ns"], dtype=np.int64)
    if timestamps.ndim != 1 or timestamps.size == 0:
        raise ValueError("V24_ECONOMIC_TIMESTAMPS_INVALID")
    asset_ids = tuple(str(value) for value in payload["asset_ids"])
    execution_venue = str(payload.get("execution_venue") or "")
    if not execution_venue or len(asset_ids) != len(set(asset_ids)):
        raise ValueError("V24_ECONOMIC_IDENTITY_INVALID")
    utc_hours = timestamps.astype("datetime64[ns]")
    utc_days = utc_hours.astype("datetime64[D]")
    unique_days = tuple(dict.fromkeys(utc_days.tolist()))
    candidate_id = str(evaluation["candidate_id"])
    common = {
        "candidate_id": candidate_id,
        "cohort": str(cohort),
        "arm": str(arm),
        "seed": int(seed),
        "horizon_hours": int(horizon_hours),
        "execution_venue": execution_venue,
        "raw_fields_json": json.dumps(
            list(payload.get("raw_fields") or ()),
            sort_keys=True,
            separators=(",", ":"),
        ),
    }
    daily_rows: list[dict[str, Any]] = []
    position_rows: list[dict[str, Any]] = []
    sleeves = dict(payload.get("sleeves") or {})
    if not sleeves:
        raise ValueError("V24_ECONOMIC_SLEEVES_MISSING")
    for sleeve_name, raw_sleeve in sorted(sleeves.items()):
        sleeve = dict(raw_sleeve)
        vectors = {
            name: np.asarray(sleeve[name], dtype=float)
            for name in ("gross", "cost", "turnover", "net")
        }
        mask = np.asarray(sleeve["mask"], dtype=bool)
        weights = np.asarray(sleeve["weights"], dtype=float)
        asset_gross = np.asarray(
            sleeve["asset_gross_contribution"], dtype=float
        )
        if (
            any(values.shape != timestamps.shape for values in vectors.values())
            or mask.shape != timestamps.shape
            or weights.shape != (len(asset_ids), timestamps.size)
            or asset_gross.shape != weights.shape
        ):
            raise ValueError("V24_ECONOMIC_PATH_SHAPE_CHANGED")
        finite = mask & np.isfinite(vectors["net"])
        if not np.allclose(
            vectors["gross"][finite] - vectors["cost"][finite],
            vectors["net"][finite],
            rtol=0.0,
            atol=1.0e-15,
        ):
            raise ValueError("V24_ECONOMIC_WATERFALL_NOT_ADDITIVE")
        for day_ordinal, day in enumerate(unique_days):
            local = (utc_days == day) & mask
            daily_rows.append(
                {
                    **common,
                    "sleeve": str(sleeve_name),
                    "day_ordinal": int(day_ordinal),
                    "utc_day": str(day),
                    "gross": _finite_mean(vectors["gross"][local]),
                    "cost": _finite_mean(vectors["cost"][local]),
                    "turnover": _finite_mean(vectors["turnover"][local]),
                    "net": _finite_mean(vectors["net"][local]),
                    "active_hour_count": int(local.sum()),
                }
            )
        active_coordinates = np.argwhere(
            mask[np.newaxis, :]
            & (
                (np.abs(weights) > 1.0e-12)
                | (np.abs(asset_gross) > 1.0e-18)
            )
        )
        for asset_index, time_index in active_coordinates:
            position_rows.append(
                {
                    **common,
                    "sleeve": str(sleeve_name),
                    "timestamp_ns": int(timestamps[time_index]),
                    "utc_hour": str(utc_hours[time_index]),
                    "asset_id": asset_ids[int(asset_index)],
                    "weight": float(weights[asset_index, time_index]),
                    "asset_gross_contribution": float(
                        asset_gross[asset_index, time_index]
                    ),
                }
            )
    return daily_rows, position_rows


def load_v24_contract(repo_root: Path) -> dict[str, Any]:
    path = Path(repo_root) / V24_CONTRACT_PATH
    contract = json.loads(path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    if contract.get("schema_version") != 1:
        blockers.append("schema_version")
    if contract.get("status") != "SOURCE_IMPLEMENTED_RUN_NOT_AUTHORIZED":
        blockers.append("status")
    if contract.get("run_authorized") is not False:
        blockers.append("run_authorized")
    selection = dict(contract.get("selection") or {})
    if selection.get("unit") != "BEHAVIOR_FAMILY":
        blockers.append("selection.unit")
    if selection.get("family_key") != list(V24_FAMILY_KEY):
        blockers.append("selection.family_key")
    if selection.get("champion_order") != list(V24_CHAMPION_ORDER):
        blockers.append("selection.champion_order")
    fresh = dict(contract.get("fresh_data_gate") or {})
    if (
        fresh.get("prior_holdout_end_exclusive")
        != "2026-07-01T00:00:00Z"
        or fresh.get("candidate_generation_during_gate") is not False
        or fresh.get("adaptive_feedback_during_gate") is not False
    ):
        blockers.append("fresh_data_gate")
    required_paths = dict(contract.get("economic_path_artifacts") or {})
    if required_paths.get("required") is not True:
        blockers.append("economic_path_artifacts.required")
    boundaries = dict(contract.get("boundaries") or {})
    if any(value is not False for value in boundaries.values()):
        blockers.append("boundaries")
    if blockers:
        raise RuntimeError("V24_SOURCE_CONTRACT_BLOCKED:" + ",".join(blockers))
    return contract


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check-source",))
    parser.add_argument("--repo-root", type=Path, required=True)
    arguments = parser.parse_args(argv)
    contract = load_v24_contract(arguments.repo_root)
    print(
        json.dumps(
            {
                "status": "PASS_V24_SOURCE_ONLY",
                "run_authorized": contract["run_authorized"],
                "contract_sha256": _canonical_sha256(contract),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
