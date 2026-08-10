from __future__ import annotations

import json

import pandas as pd

from scripts.freeze_crypto_p4_mechanism_pocket_selection_v1 import (
    EVOLUTION,
    EXPECTED_POSITIVE_PROGRAM_COUNTS,
    P1,
    P4,
    PROGRAM_QUOTAS,
    RANDOM,
    canonical_sha256,
    select_frozen_cohort,
)


def _row(
    ordinal: int,
    *,
    arm: str,
    family: str,
    program: str,
    matched_positive: bool,
    reward: float,
    behavior: str,
) -> dict[str, object]:
    candidate_id = f"candidate-{ordinal:05d}"
    spec = {"candidate_id": candidate_id, "generation_genes": {"program_id": program}}
    return {
        "completion_ordinal": ordinal,
        "candidate_id": candidate_id,
        "candidate_spec_sha256": canonical_sha256(spec),
        "candidate_spec_json": json.dumps(spec, sort_keys=True),
        "behavior_family_id": behavior,
        "arm": arm,
        "seed": 7,
        "program_family_id": family,
        "program_id": program,
        "horizon_hours": 4,
        "compile_valid": True,
        "exact_unique": True,
        "matched_control_valid": True,
        "strict_cost_evaluated": True,
        "strict_evaluated": True,
        "train_orientation": -1.0 if ordinal % 2 else 1.0,
        "train_orientation_fitted": True,
        "search_reward": reward,
        "matched_positive": matched_positive,
        "left_incremental_net_mean": 0.1,
        "right_incremental_net_mean": 0.1,
        "left_incremental_net_lcb": 0.01,
        "right_incremental_net_lcb": 0.01,
    }


def _frame() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    ordinal = 0
    family_by_program = {
        program: (P1 if program.startswith("TEMPORAL_PROGRAM_V1_2") or program.startswith("TEMPORAL_PROGRAM_V1_6") else P4)
        for program in EXPECTED_POSITIVE_PROGRAM_COUNTS
    }
    for program, count in EXPECTED_POSITIVE_PROGRAM_COUNTS.items():
        for index in range(count):
            ordinal += 1
            rows.append(
                _row(
                    ordinal,
                    arm=EVOLUTION,
                    family=family_by_program[program],
                    program=program,
                    matched_positive=True,
                    reward=1.0 + index / 100.0,
                    behavior=f"positive-{ordinal}",
                )
            )
    for arm in (EVOLUTION, RANDOM):
        for program, quota in PROGRAM_QUOTAS.items():
            for index in range(quota + 2):
                ordinal += 1
                rows.append(
                    _row(
                        ordinal,
                        arm=arm,
                        family=family_by_program[program],
                        program=program,
                        matched_positive=False,
                        reward=0.9 - index / 100.0,
                        behavior=f"control-{arm}-{program}-{index}",
                    )
                )
    return pd.DataFrame(rows)


def test_frozen_selection_is_exact_balanced_and_deterministic() -> None:
    frame = _frame()
    first = select_frozen_cohort(frame)
    second = select_frozen_cohort(frame.sample(frac=1.0, random_state=19))
    assert first == second
    assert len(first) == 80
    assert {row["train_orientation"] for row in first} == {-1.0, 1.0}
    groups = pd.Series([row["selection_group"] for row in first]).value_counts()
    assert groups.to_dict() == {
        "discovery_matched_positive": 40,
        "evolution_near_miss_control": 20,
        "random_near_miss_control": 20,
    }
    controls = pd.DataFrame(first).loc[
        lambda value: value["selection_group"] != "discovery_matched_positive"
    ]
    for group in ("evolution_near_miss_control", "random_near_miss_control"):
        counts = controls.loc[controls["selection_group"].eq(group), "program_id"].value_counts()
        assert counts.to_dict() == PROGRAM_QUOTAS


def test_post_stop_rows_are_ineligible() -> None:
    frame = _frame()
    extra = frame.iloc[[0]].copy()
    extra["completion_ordinal"] = 30_001
    extra["candidate_id"] = "post-stop"
    extra["behavior_family_id"] = "post-stop"
    extra_spec = {"candidate_id": "post-stop", "generation_genes": {"program_id": extra.iloc[0]["program_id"]}}
    extra["candidate_spec_json"] = json.dumps(extra_spec, sort_keys=True)
    extra["candidate_spec_sha256"] = canonical_sha256(extra_spec)
    selected = select_frozen_cohort(pd.concat([frame, extra], ignore_index=True))
    assert "post-stop" not in {row["candidate_id"] for row in selected}
