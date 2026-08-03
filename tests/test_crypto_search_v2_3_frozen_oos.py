from __future__ import annotations

from pathlib import Path

from alphafactory_crypto.broad_search.search_engine_v1 import (
    MECHANISM_SEARCH_V23_SEEDS,
    V23_OOS_COHORT_COUNT,
    _load_v23_oos_candidates,
    _load_v23_oos_receipt,
    _payload_sha,
    _restore_v23_oos_checkpoint,
    _v23_oos_aggregate,
    _write_v23_oos_checkpoint,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_receipt_binds_exact_committed_v23_cohort_without_holdout_read() -> None:
    receipt = _load_v23_oos_receipt(REPO_ROOT, require_authorized=True)
    rows = _load_v23_oos_candidates(REPO_ROOT, receipt)
    projection = [
        {key: value for key, value in row.items() if key != "candidate"}
        for row in rows
    ]
    assert len(rows) == V23_OOS_COHORT_COUNT
    assert len({row["candidate_id"] for row in rows}) == V23_OOS_COHORT_COUNT
    assert _payload_sha(projection) == receipt["source_v23"][
        "evaluated_cohort_projection_sha256"
    ]
    assert receipt["holdout"]["read_allowed"] is True
    assert receipt["run_authorization"]["candidate_generation_allowed"] is False


def test_pooled_oos_effect_reports_heterogeneity_without_all_cell_gate() -> None:
    receipt = _load_v23_oos_receipt(REPO_ROOT, require_authorized=True)
    cohorts = {
        "random_stratified": "expanded_mechanism_random_v2_3",
        "random_train_top": "expanded_mechanism_random_v2_3",
        "evolution_stratified": "mechanism_evolution_v2_3",
        "evolution_train_top": "mechanism_evolution_v2_3",
    }
    candidate_rows = []
    path_rows = []
    for cohort, arm in cohorts.items():
        for seed in MECHANISM_SEARCH_V23_SEEDS:
            for horizon in (1, 4):
                candidate_id = f"{cohort}-{seed}-{horizon}"
                candidate_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "cohort": cohort,
                        "arm": arm,
                        "seed": seed,
                        "horizon_hours": horizon,
                        "oos_status": "EVALUATED",
                        "reason": None,
                    }
                )
                negative_cell = seed == MECHANISM_SEARCH_V23_SEEDS[1] and horizon == 4
                if cohort.startswith("random"):
                    primary = 0.0
                    matched = 0.0
                elif cohort == "evolution_stratified":
                    primary = 0.0005
                    matched = 0.00025
                else:
                    primary = -0.001 if negative_cell else 0.002
                    matched = -0.0005 if negative_cell else 0.001
                for day in range(21):
                    path_rows.append(
                        {
                            "candidate_id": candidate_id,
                            "cohort": cohort,
                            "arm": arm,
                            "seed": seed,
                            "horizon_hours": horizon,
                            "day_ordinal": day,
                            "utc_day": f"2026-01-{day + 1:02d}",
                            "primary_net": primary,
                            "matched_increment": matched,
                            "control_net": -0.0001,
                        }
                    )
    _, _, effects = _v23_oos_aggregate(
        candidate_rows=candidate_rows,
        candidate_path_rows=path_rows,
        receipt=receipt,
    )
    assert effects["binary_qualification_gate_applied"] is False
    assert effects["cell_results_role"] == "HETEROGENEITY_ONLY"
    assert effects["classification"] == (
        "OOS_TOTAL_POLICY_POSITIVE_DIRECTION_Q10_SUPPORTED"
    )
    total_cells = [
        row for row in effects["cell_effects"] if row["comparison"] == "total_policy"
    ]
    assert any(
        row["effects"]["primary_net"]["observed_mean_delta"] < 0.0
        for row in total_cells
    )
    assert effects["pooled_effects"]["total_policy"]["primary_net"][
        "observed_mean_delta"
    ] > 0.0


def test_oos_checkpoint_roundtrip_is_exact(tmp_path: Path) -> None:
    candidate_rows = [
        {
            "candidate_id": "candidate-1",
            "cohort": "random_train_top",
            "arm": "expanded_mechanism_random_v2_3",
            "seed": MECHANISM_SEARCH_V23_SEEDS[0],
            "horizon_hours": 1,
            "oos_status": "EVALUATED",
        }
    ]
    path_rows = [
        {
            "candidate_id": "candidate-1",
            "cohort": "random_train_top",
            "arm": "expanded_mechanism_random_v2_3",
            "seed": MECHANISM_SEARCH_V23_SEEDS[0],
            "horizon_hours": 1,
            "day_ordinal": 0,
            "utc_day": "2026-01-01",
            "primary_net": 0.001,
            "matched_increment": 0.0005,
            "control_net": 0.0,
        }
    ]
    _write_v23_oos_checkpoint(
        runtime_root=tmp_path,
        label="checkpoint_000",
        source_sha="a" * 40,
        frozen_hash="B" * 64,
        selection_hash="C" * 64,
        candidate_rows=candidate_rows,
        candidate_path_rows=path_rows,
    )
    restored = _restore_v23_oos_checkpoint(
        runtime_root=tmp_path,
        source_sha="a" * 40,
        frozen_hash="B" * 64,
        selection_hash="C" * 64,
    )
    assert restored is not None
    restored_candidates, restored_paths = restored
    assert [row["candidate_id"] for row in restored_candidates] == ["candidate-1"]
    assert len(restored_paths) == 1
    assert (
        tmp_path / "checkpoints" / "checkpoint_000" / "manifest.json"
    ).is_file()
