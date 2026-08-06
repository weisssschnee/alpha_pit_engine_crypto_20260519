from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from alphafactory_crypto.broad_search import (
    funding_flow_residual_confirmation_v1 as confirmation,
)

from alphafactory_crypto.broad_search.funding_flow_residual_confirmation_v1 import (
    _counterfactual_decision,
    _verify_checkpoint,
    _write_checkpoint,
    build_frozen_grid,
    freeze_validation_b_selection,
    load_confirmation_receipt,
    preflight_confirmation,
    stage_a_family_gate,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _positive_stage_rows() -> tuple[list[dict], list[dict], dict]:
    receipt = load_confirmation_receipt(REPO_ROOT, require_authorized=False)
    grid, pairs, _ = build_frozen_grid(REPO_ROOT, receipt=receipt)
    rows = []
    for index, row in enumerate(grid):
        value = 0.001 + index * 1e-8
        if row["candidate_group"] == "placebo":
            value -= 0.0005
        rows.append(
            {
                **row,
                "strict_evaluated": True,
                "left_incremental_net_mean": value,
                "right_incremental_net_mean": value + 0.0001,
                "worst_axis_net": value,
                "primary_turnover_mean": 0.1,
            }
        )
    by_id = {row["candidate_id"]: row for row in rows}
    paired = [
        {
            **pair,
            "main_strict_evaluated": True,
            "placebo_strict_evaluated": True,
            "main_worst_axis_net": by_id[pair["main_candidate_id"]][
                "worst_axis_net"
            ],
            "placebo_worst_axis_net": by_id[pair["placebo_candidate_id"]][
                "worst_axis_net"
            ],
            "main_minus_placebo_worst_axis_net": (
                by_id[pair["main_candidate_id"]]["worst_axis_net"]
                - by_id[pair["placebo_candidate_id"]]["worst_axis_net"]
            ),
        }
        for pair in pairs
    ]
    return rows, paired, receipt


def test_preflight_freezes_exact_main_placebo_grid_without_market_read() -> None:
    receipt = load_confirmation_receipt(REPO_ROOT, require_authorized=False)
    rows, pairs, proof = build_frozen_grid(REPO_ROOT, receipt=receipt)
    assert len(rows) == 162
    assert len(pairs) == 81
    assert proof["market_read_performed"] is False
    assert proof["main_count"] == 81
    assert proof["placebo_count"] == 81
    assert proof["anchor_candidate_id"] == (
        "D2D46A0AB9675C7349A1C658D4B200987FBC216A89AD5627FF613EC26E7B71CE"
    )
    if receipt.get("run_authorized") is True:
        result = preflight_confirmation(REPO_ROOT)
        assert result["status"] == "PREFLIGHT_PASS_NO_MARKET_EVALUATION"
        assert result["market_read_performed"] is False
        assert result["economic_authority_verified"] is True


def test_preflight_resolves_economic_authority_before_launch(monkeypatch) -> None:
    receipt = load_confirmation_receipt(REPO_ROOT, require_authorized=False)
    calls: list[Path] = []

    monkeypatch.setattr(
        confirmation,
        "load_confirmation_receipt",
        lambda *args, **kwargs: receipt,
    )

    def record_economic_authority(root: Path, loaded_receipt: dict) -> object:
        assert loaded_receipt is receipt
        calls.append(root)
        return object()

    monkeypatch.setattr(
        confirmation,
        "_build_economic_context",
        record_economic_authority,
    )
    result = confirmation.preflight_confirmation(REPO_ROOT)
    assert calls == [REPO_ROOT]
    assert result["economic_authority_verified"] is True


def test_validation_splits_and_tail_purge_are_frozen() -> None:
    contract = json.loads(
        (REPO_ROOT / "config/crypto_funding_flow_residual_nested_confirmation_v1.json")
        .read_text(encoding="utf-8")
    )
    assert contract["validation_a"]["end_exclusive"] == contract["validation_b"][
        "start"
    ]
    assert contract["validation_a"]["partition_tail_purge_hours"] == 6
    assert contract["validation_b"]["partition_tail_purge_hours"] == 6
    assert contract["validation_a"]["execution_delay_hours"] == 2
    assert contract["validation_b"]["execution_delay_hours"] == 2


def test_family_cell_aggregation_and_placebo_gate() -> None:
    rows, pairs, receipt = _positive_stage_rows()
    result = stage_a_family_gate(rows, pairs, contract=receipt["_contract"])
    assert result["family_gate_pass"] is True
    assert result["main_vs_placebo_gate_pass"] is True
    assert len(result["cell_metrics"]) == 27
    assert all(row["candidate_count"] == 3 for row in result["cell_metrics"])
    assert result["metrics"]["anchor_direct_neighbor_count"] == 6
    assert result["metrics"]["anchor_direct_neighbor_positive_fraction"] == 1.0


def test_fixed_decision_tree_has_all_five_branches() -> None:
    a_pass = {"main_vs_placebo_gate_pass": True}
    a_placebo_fail = {"main_vs_placebo_gate_pass": False}
    assert _counterfactual_decision(
        stage_a_gate=a_placebo_fail, stage_b_gate=None
    ) == "LONG_FUNDING_SHORT_FLOW_DIRECTIONAL_HYPOTHESIS_NOT_SUPPORTED"
    assert _counterfactual_decision(
        stage_a_gate=a_pass,
        stage_b_gate={"anchor_pass": True, "family_pass": True},
    ) == "FUNDING_FLOW_RESIDUAL_CONFIRMED_FOR_SEPARATE_OOS_AUTHORIZATION"
    assert _counterfactual_decision(
        stage_a_gate=a_pass,
        stage_b_gate={"anchor_pass": False, "family_pass": True},
    ) == "MECHANISM_FAMILY_SUPPORTED_BUT_NO_PRECONFIRMED_OOS_CANDIDATE"
    assert _counterfactual_decision(
        stage_a_gate=a_pass,
        stage_b_gate={"anchor_pass": True, "family_pass": False},
    ) == "ISOLATED_CANDIDATE_CONFIRMATION_WITHOUT_BROAD_MECHANISM_SUPPORT"
    assert _counterfactual_decision(
        stage_a_gate=a_pass,
        stage_b_gate={"anchor_pass": False, "family_pass": False},
    ) == "FUNDING_FLOW_RESIDUAL_ROUTE_CLOSED"


def test_selection_is_deterministic_and_validation_b_is_still_unread(
    tmp_path: Path,
) -> None:
    rows, pairs, receipt = _positive_stage_rows()
    stage0 = []
    for row in rows:
        stage0.append(
            {
                **row,
                "development_worst_block_min_matched_net": row["worst_axis_net"],
                "train_orientation": -1.0,
            }
        )
    checkpoint = tmp_path / "checkpoints" / "checkpoint_validation_a"
    checkpoint.mkdir(parents=True)
    (checkpoint / "manifest.json").write_text("{}\n", encoding="utf-8")
    gate = stage_a_family_gate(rows, pairs, contract=receipt["_contract"])
    selected_1, frozen_1 = freeze_validation_b_selection(
        runtime_root=tmp_path,
        stage_a_rows=rows,
        stage_0_rows=stage0,
        pairs=[
            {
                key: pair[key]
                for key in (
                    "pair_id",
                    "cell_id",
                    "funding_source",
                    "funding_field",
                    "funding_window",
                    "flow_window",
                    "beta",
                    "main_candidate_id",
                    "placebo_candidate_id",
                )
            }
            for pair in pairs
        ],
        stage_a_gate=gate,
        producer_source_sha="a" * 40,
        frozen_contract_sha256="B" * 64,
    )
    selected_2, frozen_2 = freeze_validation_b_selection(
        runtime_root=tmp_path,
        stage_a_rows=rows,
        stage_0_rows=stage0,
        pairs=[
            {
                key: pair[key]
                for key in (
                    "pair_id",
                    "cell_id",
                    "funding_source",
                    "funding_field",
                    "funding_window",
                    "flow_window",
                    "beta",
                    "main_candidate_id",
                    "placebo_candidate_id",
                )
            }
            for pair in pairs
        ],
        stage_a_gate=gate,
        producer_source_sha="a" * 40,
        frozen_contract_sha256="B" * 64,
    )
    assert [row["candidate_id"] for row in selected_1] == [
        row["candidate_id"] for row in selected_2
    ]
    assert frozen_1 == frozen_2
    assert frozen_1["validation_b_read"] is False
    assert frozen_1["candidate_count"] <= 10


def test_atomic_checkpoint_can_be_restored(tmp_path: Path) -> None:
    row = {
        "candidate_id": "A",
        "candidate_group": "main",
        "strict_evaluated": True,
        "matched_positive": False,
        "left_incremental_net_mean": 0.0,
        "right_incremental_net_mean": 0.0,
        "process_cpu_seconds": 1.0,
        "worker_rss_bytes": 1,
        "worker_private_bytes": 1,
    }
    manifest = _write_checkpoint(
        tmp_path,
        name="checkpoint_stage_0",
        stage="stage_0",
        rows=[row],
        pairs=[{"pair_id": "P"}],
        resource={"strict_evaluated_count": 1},
        producer_source_sha="a" * 40,
        frozen_contract_sha256="B" * 64,
    )
    restored = _verify_checkpoint(
        tmp_path / "checkpoints" / "checkpoint_stage_0",
        expected_stage="stage_0",
        producer_source_sha="a" * 40,
        frozen_contract_sha256="B" * 64,
    )
    assert restored == manifest
    frame = pd.read_parquet(
        tmp_path
        / "checkpoints"
        / "checkpoint_stage_0"
        / "candidate_ledger.parquet"
    )
    assert frame["candidate_id"].tolist() == ["A"]
