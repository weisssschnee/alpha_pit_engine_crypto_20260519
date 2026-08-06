from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from alphafactory_crypto.broad_search import temporal_activation_v1 as temporal_module
from alphafactory_crypto.broad_search import search_engine_v1 as engine
from alphafactory_crypto.broad_search.compositional18m import (
    CandidateSpec,
    compile_mechanism_catalog,
    mechanism_role_domains,
)
from alphafactory_crypto.broad_search.expression import (
    CANONICAL_PRIMITIVE_OPERATOR,
    CanonicalTemporalPrimitiveAdapterV1,
    Expression,
    FieldContract,
    TypedExpressionRegistry,
    materialize_expression,
)
from alphafactory_crypto.broad_search.temporal_activation_v1 import (
    ALLOWED_PRIMITIVES,
    _allocation_coordinate,
    _checkpoint,
    _operator_nodes,
    _pair_diagnostic_row,
    _paired_common_support,
    _receipt_content_sha,
    _validate_config,
    classify_results,
    continuation_decision,
    consume_binding_receipt,
    propose_pair,
    source_smoke,
)
from alphafactory_crypto.instrument_canary.grammar import (
    PRIMITIVE_PARAMETER_OPTIONS,
)
from alphafactory_crypto.instrument_capability.primitives import evaluate_primitive


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (REPO_ROOT / "config/crypto_search_temporal_activation_v1.json").read_text(
        encoding="utf-8"
    )
)


def _contracts() -> tuple[FieldContract, ...]:
    manifest = json.loads(
        (
            REPO_ROOT
            / "runtime/crypto_search_engine_v1_4_oi_flow_20260728/aligned_carrier_manifest.json"
        ).read_text(encoding="utf-8")
    )
    return tuple(
        FieldContract(
            str(row["field_id"]),
            str(row["value_type"]),
            str(row["unit"]),
            int(row["observable_lag_hours"]),
            str(row["pit_authority"]),
        )
        for row in manifest["contracts"]
    )


@pytest.mark.parametrize("primitive_id", ALLOWED_PRIMITIVES)
def test_canonical_adapter_delegates_exactly_to_authority(primitive_id: str) -> None:
    values = np.vstack(
        (
            np.linspace(-3.0, 5.0, 400),
            np.sin(np.linspace(0.0, 30.0, 400)),
        )
    )
    window, long_window, threshold = PRIMITIVE_PARAMETER_OPTIONS[primitive_id][0]
    expression = CanonicalTemporalPrimitiveAdapterV1.expression(
        Expression.raw("x"),
        primitive_id=primitive_id,
        window=window,
        long_window=long_window,
        threshold=threshold,
    )
    registry = TypedExpressionRegistry((FieldContract("x", "RATIO", "ratio", 2),))
    observed = materialize_expression(
        expression,
        registry=registry,
        field_reader=lambda _: values,
    )
    expected = evaluate_primitive(
        primitive_id,
        values,
        window=1 if window is None else window,
        long_window=1 if long_window is None else long_window,
        threshold=0.0 if threshold is None else threshold,
    )
    np.testing.assert_array_equal(observed, expected)
    assurance = registry.validate(expression)
    assert assurance.observable_lag_hours == 2
    assert expression.expression_id


def test_adapter_rejects_unbound_primitive_parameters_and_nesting() -> None:
    raw = Expression.raw("x")
    registry = TypedExpressionRegistry((FieldContract("x", "RATIO", "ratio"),))
    with pytest.raises(ValueError):
        CanonicalTemporalPrimitiveAdapterV1.expression(
            raw,
            primitive_id="Slope",
            window=24,
            long_window=None,
            threshold=None,
        )
    with pytest.raises(ValueError):
        CanonicalTemporalPrimitiveAdapterV1.expression(
            raw,
            primitive_id="Delta",
            window=999,
            long_window=None,
            threshold=None,
        )
    first = CanonicalTemporalPrimitiveAdapterV1.expression(
        raw,
        primitive_id="Delta",
        window=24,
        long_window=None,
        threshold=None,
    )
    second = CanonicalTemporalPrimitiveAdapterV1.expression(
        first,
        primitive_id="Delta",
        window=24,
        long_window=None,
        threshold=None,
    )
    with pytest.raises(ValueError, match="more than one"):
        registry.validate(second)


def test_pair_generation_is_replayable_and_preserves_temporal_control() -> None:
    _validate_config(CONFIG)
    contracts = _contracts()
    registry = TypedExpressionRegistry(contracts)
    domains = {**mechanism_role_domains(contracts), "__HORIZONS__": (4,)}
    specs = tuple(
        row
        for row in compile_mechanism_catalog(
            json.loads(
                (
                    REPO_ROOT / "config/crypto_typed_mechanism_catalog_v2_1.json"
                ).read_text(encoding="utf-8")
            )
        )
        if row.generation == 1 and row.matched_control_schema == "DUAL_AXIS_A_B_AB"
    )
    identities: set[str] = set()
    for family in CONFIG["temporal_families"]:
        first = propose_pair(
            config=CONFIG,
            family=family,
            registry=registry,
            specs=specs,
            domains=domains,
            slot=0,
            attempt=0,
        )
        replay = propose_pair(
            config=CONFIG,
            family=family,
            registry=registry,
            specs=specs,
            domains=domains,
            slot=0,
            attempt=0,
        )
        assert first["paired_proposal_id"] == replay["paired_proposal_id"]
        assert first["static"].candidate_id == replay["static"].candidate_id
        assert first["temporal"].candidate_id == replay["temporal"].candidate_id
        assert first["static"].raw_fields == first["temporal"].raw_fields
        assert first["static"].mapping_id == first["temporal"].mapping_id
        assert first["static"].horizon_hours == 4
        expression_nodes = _operator_nodes(
            first["temporal"].expression, CANONICAL_PRIMITIVE_OPERATOR
        )
        control_nodes = _operator_nodes(
            first["temporal"].control, CANONICAL_PRIMITIVE_OPERATOR
        )
        assert len(expression_nodes) == len(control_nodes) == 1
        assert expression_nodes[0].parameters == control_nodes[0].parameters
        restored = CandidateSpec.from_dict(first["temporal"].to_dict())
        assert restored.to_dict() == first["temporal"].to_dict()
        assert restored.generation_genes["paired_lineage"][
            "paired_static_candidate_id"
        ] == first["static"].candidate_id
        identities.add(first["paired_proposal_id"])
    assert len(identities) == 4


def test_t1_t4_allocation_balances_primitive_template_and_reachable_roles() -> None:
    specs = tuple(
        row
        for row in compile_mechanism_catalog(
            json.loads(
                (
                    REPO_ROOT / "config/crypto_typed_mechanism_catalog_v2_1.json"
                ).read_text(encoding="utf-8")
            )
        )
        if row.generation == 1 and row.matched_control_schema == "DUAL_AXIS_A_B_AB"
    )
    for family in CONFIG["temporal_families"]:
        for tranche_index in range(4):
            rows = [
                _allocation_coordinate(family=family, specs=specs, slot=slot)
                for slot in range(tranche_index * 256, (tranche_index + 1) * 256)
            ]
            primitive_counts = Counter(row[0] for row in rows)
            template_counts = Counter(row[1] for row in rows)
            role_counts = Counter(
                row[2].left_role if row[3] == "left" else row[2].right_role
                for row in rows
            )
            assert max(primitive_counts.values()) - min(primitive_counts.values()) <= 1
            assert max(template_counts.values()) - min(template_counts.values()) <= 1
            assert set(role_counts) == set(family["eligible_temporal_roles"])


def test_t3_basis_state_route_is_not_silently_downgraded() -> None:
    contracts = _contracts()
    registry = TypedExpressionRegistry(contracts)
    domains = {**mechanism_role_domains(contracts), "__HORIZONS__": (4,)}
    specs = tuple(
        row
        for row in compile_mechanism_catalog(
            json.loads(
                (
                    REPO_ROOT / "config/crypto_typed_mechanism_catalog_v2_1.json"
                ).read_text(encoding="utf-8")
            )
        )
        if row.generation == 1 and row.matched_control_schema == "DUAL_AXIS_A_B_AB"
    )
    family = next(
        row
        for row in CONFIG["temporal_families"]
        if row["family_id"] == "T3_CROWDING_TRANSITION"
    )
    slot = next(
        value
        for value in range(256)
        if (
            lambda allocation: (
                allocation[2].left_role
                if allocation[3] == "left"
                else allocation[2].right_role
            )
        )(_allocation_coordinate(family=family, specs=specs, slot=value))
        == "BASIS_BUNDLE"
    )
    pair = propose_pair(
        config=CONFIG,
        family=family,
        registry=registry,
        specs=specs,
        domains=domains,
        slot=slot,
        attempt=0,
    )
    assert pair["temporal_role"] == "BASIS_BUNDLE"
    assert pair["temporal_placement"] == "POST_TYPED_BUNDLE_PRE_OUTER"


def _gate_row(
    index: int,
    *,
    temporal_net: bool = True,
    temporal_gross: bool = True,
) -> dict[str, object]:
    templates = ("A", "B", "C", "D")
    primitives = ALLOWED_PRIMITIVES
    return {
        "paired_proposal_id": f"pair-{index}",
        "outer_template": templates[index % len(templates)],
        "temporal_field_family": f"R{index % 4}",
        "primitive_id": primitives[index % len(primitives)],
        "native_paired_worst_axis_net_delta": 1.0,
        "common_paired_worst_axis_net_delta": 0.5,
        "static_dual_axis_gross_positive": True,
        "temporal_dual_axis_gross_positive": temporal_gross,
        "static_dual_axis_net_positive": False,
        "temporal_dual_axis_net_positive": temporal_net,
        "static_replicated_positive_block_count": 1,
        "temporal_replicated_positive_block_count": 2,
        "static_all_three_blocks_positive": False,
        "temporal_all_three_blocks_positive": False,
        "static_worst_axis_net_lcb": -2.0,
        "temporal_worst_axis_net_lcb": -1.0,
        "static_joint_net_lcb_margin": -3.0,
        "temporal_joint_net_lcb_margin": -1.5,
        "static_worst_block_matched_net": -2.0,
        "temporal_worst_block_matched_net": -1.0,
        "static_matched_positive": False,
        "temporal_matched_positive": False,
        "support_selection_effect": False,
    }


def test_tranche_zero_broad_shift_pass_and_fail_are_exact() -> None:
    rows = [_gate_row(index) for index in range(1_024)]
    passed = classify_results(rows, [{} for _ in range(2_048)], expected_pairs=1_024)
    assert passed["status"] == "CANONICAL_TEMPORAL_PRIMITIVE_ACTIVATION_SUPPORTED"
    assert continuation_decision(
        rows, [{} for _ in range(2_048)], completed_tranche=0
    )["decision"] == "CONTINUE"
    failed_rows = [
        {**row, "native_paired_worst_axis_net_delta": -1.0} for row in rows
    ]
    stopped = continuation_decision(
        failed_rows, [{} for _ in range(2_048)], completed_tranche=0
    )
    assert stopped["decision"] == "STOP_TEMPORAL_NOT_SUPPORTED"


def test_later_tranche_two_step_marginal_futility_is_fail_closed() -> None:
    first = [
        _gate_row(
            index,
            temporal_net=index < 205,
            temporal_gross=index < 512,
        )
        for index in range(1_024)
    ]
    second = []
    third = []
    for index in range(1_024):
        second.append(_gate_row(1_024 + index, temporal_net=index < 410))
        third.append(_gate_row(2_048 + index, temporal_net=index < 409))
    decision0 = continuation_decision(
        first, [{} for _ in range(2_048)], completed_tranche=0
    )
    decision1 = continuation_decision(
        first + second,
        [{} for _ in range(4_096)],
        completed_tranche=1,
        prior_decisions=[decision0],
    )
    assert decision1["decision"] == "CONTINUE"
    assert decision1["no_boundary_progress"] is True
    decision2 = continuation_decision(
        first + second + third,
        [{} for _ in range(6_144)],
        completed_tranche=2,
        prior_decisions=[decision0, decision1],
    )
    assert decision2["decision"] == "EARLY_STOP_TEMPORAL_FUTILITY"


def test_checkpoint_snapshots_restore_without_following_ledger_mutation(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    engine._write_json(runtime / "work_state.json", {"rows": 1})
    for name in (
        "paired_proposal_ledger.parquet",
        "paired_economic_diagnostics.parquet",
        "candidate_ledger.parquet",
        "rejected_pair_ledger.parquet",
    ):
        engine._write_parquet(runtime / name, [{"value": 1}])
    manifest = _checkpoint(
        runtime,
        checkpoint_index=0,
        source_sha="a" * 40,
        frozen_hash="B" * 64,
        attempts={"T1": 1},
        accepted={"T1": 1},
        pair_rows=[{"pair": 1}],
        diagnostic_rows=[{"pair": 1}],
        candidate_rows=[{"candidate": 1}, {"candidate": 2}],
        rejected_rows=[],
    )
    engine._write_parquet(runtime / "candidate_ledger.parquet", [{"value": 2}])
    checkpoint = runtime / "checkpoints/checkpoint_000"
    assert all(
        (checkpoint / row["path"]).is_file() for row in manifest["files"]
    )
    assert pd.read_parquet(checkpoint / "candidate_ledger.parquet")["value"].tolist() == [1]


def test_native_and_common_support_views_remain_separate() -> None:
    def sleeve(mask: list[bool], gross: list[float]) -> dict[str, object]:
        return {
            "mask": np.asarray(mask, dtype=bool),
            "gross": np.asarray(gross, dtype=float),
            "weights": np.asarray([[0.0, 0.5, 0.0], [0.0, -0.5, 0.0]]),
        }

    static_paths = {
        "sleeves": {
            "primary_minus_left_control": sleeve([True, True, False], [0.1, 0.2, 0.0]),
            "primary_minus_right_control": sleeve([True, True, False], [0.1, 0.2, 0.0]),
        }
    }
    temporal_paths = {
        "sleeves": {
            "primary_minus_left_control": sleeve([True, False, True], [0.3, 0.0, 0.4]),
            "primary_minus_right_control": sleeve([True, False, True], [0.3, 0.0, 0.4]),
        }
    }
    diagnostic = _paired_common_support(
        static_paths, temporal_paths, cost_bps=5.0, horizon=1
    )
    assert diagnostic["axis"]["left"]["static"]["support_coordinates"] == 1
    assert diagnostic["axis"]["left"]["temporal"]["support_coordinates"] == 1
    assert diagnostic["paired_worst_axis_net_delta"] > 0.0


def test_pair_diagnostic_excludes_runtime_candidate_objects_and_writes_parquet(
    tmp_path: Path,
) -> None:
    def evaluation(value: float) -> dict[str, object]:
        return {
            "left_incremental": {
                "gross_mean": value,
                "net_mean": value,
                "net_lcb": value,
            },
            "right_incremental": {
                "gross_mean": value,
                "net_mean": value,
                "net_lcb": value,
            },
            "block_robust_ordering": {
                "replicated_positive_block_count": 3,
                "all_three_blocks_positive": True,
                "worst_block_min_matched_net_mean": value,
            },
            "matched_positive": True,
        }

    row = _pair_diagnostic_row(
        pair={
            "paired_proposal_id": "pair-1",
            "outer_template": "BASIS_OI_CROWDING",
            "primitive_id": "Delta",
            "temporal_field_family": "open_interest_level_change",
            "static": object(),
            "temporal": object(),
            "static_candidate_spec_json": "{}",
            "temporal_candidate_spec_json": "{}",
        },
        static=evaluation(0.1),
        temporal=evaluation(0.2),
        common={
            "static_worst_axis_net_mean": 0.1,
            "temporal_worst_axis_net_mean": 0.2,
            "paired_worst_axis_net_delta": 0.1,
        },
    )
    assert "static" not in row
    assert "temporal" not in row
    assert not any(key.endswith("_candidate_spec_json") for key in row)
    output = tmp_path / "paired_economic_diagnostics.parquet"
    engine._write_parquet(output, [row])
    restored = pd.read_parquet(output)
    assert restored.loc[0, "paired_proposal_id"] == "pair-1"


def test_source_smoke_compiles_families_and_closes_worker_evidence(tmp_path: Path) -> None:
    evidence = tmp_path / "process_evidence"
    result = source_smoke(REPO_ROOT, evidence_root=evidence)
    assert result["status"] == "PASS"
    assert result["market_arrays_read"] == 0
    assert result["receipt_consumed"] is False
    assert result["compiled_family_count"] == 4
    assert result["unique_pair_count"] == 4
    task_rows = [json.loads(path.read_text()) for path in evidence.glob("*_task.json")]
    assert task_rows and all(row["stage"] == "TASK_COMPLETED" for row in task_rows)


def test_receipt_consumption_is_one_time(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    relative_receipt = "config/receipt.json"
    monkeypatch.setattr(temporal_module, "BINDING_RECEIPT_PATH", relative_receipt)
    receipt_path = tmp_path / relative_receipt
    engine._write_json(
        receipt_path,
        {
            "status": "RUN_AUTHORIZED_DEVELOPMENT_ONLY",
            "run_authorized": True,
        },
    )
    runtime = tmp_path / "runtime/crypto_search_temporal_activation_v1_20260806"
    engine._write_json(
        runtime / "final_decision.json",
        {
            "producer_source_sha": "a" * 40,
            "status": "CANONICAL_TEMPORAL_PRIMITIVE_ACTIVATION_NOT_SUPPORTED",
            "strict_evaluated_count": 2_048,
            "completed_tranches": 1,
        },
    )
    engine._write_json(runtime / "run_manifest.json", {"bundle_sha256": "B" * 64})
    result = consume_binding_receipt(tmp_path, runtime_date="20260806")
    assert result["status"] == "CONSUMED"
    with pytest.raises(RuntimeError, match="not consumable"):
        consume_binding_receipt(tmp_path, runtime_date="20260806")


def test_receipt_content_hash_excludes_only_self_hash() -> None:
    payload = {"budget": {"strict": 2_048}, "boundaries": {"oos": False}}
    content_sha = temporal_module._json_sha(payload)
    receipt = {**payload, "receipt_sha256": content_sha}
    assert _receipt_content_sha(receipt) == content_sha
    assert temporal_module._json_sha(receipt) != content_sha


def test_pc2_launcher_keeps_frozen_worker_policy() -> None:
    source = (
        REPO_ROOT / "scripts/run_crypto_search_temporal_activation_v1_pc2.ps1"
    ).read_text(encoding="utf-8")
    assert "source-smoke" in source
    assert "--source-sha $SourceSha" in source
    assert "12" not in source


def test_config_rejects_any_prohibited_research_boundary() -> None:
    config = engine._read_json(REPO_ROOT / temporal_module.CONFIG_PATH)
    for boundary in (
        "validation",
        "oos",
        "holdout",
        "evaluator_formula_change",
        "new_behavior_archive_identity",
        "cross_sprint_adaptive_memory",
    ):
        changed = json.loads(json.dumps(config))
        changed["boundaries"][boundary] = True
        with pytest.raises(ValueError, match="research boundary"):
            _validate_config(changed)
