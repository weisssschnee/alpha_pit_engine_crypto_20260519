from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from alphafactory_crypto.instrument_canary.admission import authorize_candidate
from alphafactory_crypto.instrument_canary.contracts import CandidateGenome
from alphafactory_crypto.instrument_canary.grammar import (
    CROSS_SECTIONAL_RELATIVE,
    DIRECTIONAL_STATEFUL,
    SPARSE_EVENT_CARRY,
    FrozenGrammar,
)
from alphafactory_crypto.instrument_canary.materialize import materialize_authorized
from alphafactory_crypto.instrument_canary.release import canonical_sha256


SOURCE_SHA = "a" * 40


def _expected_release() -> dict[str, object]:
    return {
        "parent_release_id": "RELEASE_V1",
        "parent_release_content_sha256": "B" * 64,
        "development_view_id": "RELEASE_V1_DEV_ONLY",
        "expected_source_bundle_sha256": "C" * 64,
        "expected_output_bundle_sha256": "D" * 64,
        "symbols": ["A", "B"],
        "months": ["2024-01"],
        "searchable_fields": [
            "trade_count",
            "vwap",
            "close_to_open_bps",
            "volume_imbalance",
            "large_trade_count_ratio_100k_plus",
        ],
    }


def _view_sha256() -> str:
    expected = _expected_release()
    return canonical_sha256(
        {
            "release_id": expected["parent_release_id"],
            "assets": expected["symbols"],
            "months": expected["months"],
            "source_bundle_sha256": expected["expected_source_bundle_sha256"],
            "output_bundle_sha256": expected["expected_output_bundle_sha256"],
            "searchable_fields": expected["searchable_fields"],
            "target_only_fields": ["close_price"],
        }
    )


def _target_contract() -> dict[str, object]:
    return {
        "price_source": "source close_price; target-only and forbidden from grammar",
        "horizons_hours": [1, 4],
        "feature_bucket_coordinate": "t",
        "feature_observable_time": "t+1h",
        "execution_time": "t+2h",
        "execution_delay_after_observable_hours": 1,
        "formula": "log(close[t+2h+horizon] / close[t+2h])",
        "all_metrics_role": "DEVELOPMENT_TRAIN_ONLY",
    }


def _manifest() -> dict[str, object]:
    value: dict[str, object] = {
        "schema_version": 1,
        "release_id": "RELEASE_V1",
        "development_view_id": "RELEASE_V1_DEV_ONLY",
        "data_role": "DEVELOPMENT_TRAIN_ONLY",
        "parent_release_content_sha256": "B" * 64,
        "source_bundle_sha256": "C" * 64,
        "output_bundle_sha256": "D" * 64,
        "development_view_sha256": _view_sha256(),
        "assets": ["A", "B"],
        "months": ["2024-01"],
        "searchable_fields": _expected_release()["searchable_fields"],
        "target_only_fields": ["close_price"],
        "pit_contract": {
            "observable_time": "timestamp + 1h",
            "maturity": "timestamp + 1h",
            "source_lag_seconds": 0,
            "partial_current_hour": "PROHIBITED",
            "no_fill": True,
        },
        "target_horizon_contract": _target_contract(),
        "sealed_reads": 0,
        "challenge_path_enumerated": False,
    }
    value["manifest_sha256"] = canonical_sha256(value)
    return value


def _changed_manifest(**changes: object) -> dict[str, object]:
    value = {
        key: item for key, item in _manifest().items() if key != "manifest_sha256"
    }
    value.update(changes)
    value["manifest_sha256"] = canonical_sha256(value)
    return value


def _genome(**changes: object) -> CandidateGenome:
    payload: dict[str, object] = {
        "field_id": "trade_count",
        "representation_id": "identity",
        "primitive_id": "Delta",
        "window": 2,
        "long_window": None,
        "threshold": None,
        "mechanism_family": CROSS_SECTIONAL_RELATIVE,
        "target_horizon_hours": 1,
    }
    payload.update(changes)
    return CandidateGenome(**payload)  # type: ignore[arg-type]


def _authorize(genome: CandidateGenome, **changes: object):
    arguments: dict[str, object] = {
        "grammar": FrozenGrammar.default(),
        "release_manifest": _manifest(),
        "expected_release": _expected_release(),
        "target_contract": _target_contract(),
        "cost_contract": {
            "model_id": "FULL_L1_FIXED_5BPS_WITH_INITIAL_AND_TERMINAL",
            "cost_bps": 5.0,
            "initial_establishment_charged": True,
            "terminal_liquidation_charged": True,
        },
        "source_code_sha": SOURCE_SHA,
    }
    arguments.update(changes)
    return authorize_candidate(genome, **arguments)  # type: ignore[arg-type]


def test_receipt_binds_complete_authority_and_has_stable_cache_key() -> None:
    reads: list[str] = []
    receipt = _authorize(_genome(), reader_callback=lambda: reads.append("authorized"))
    repeat = _authorize(_genome())

    assert reads == ["authorized"]
    assert receipt.candidate_id == _genome().candidate_id
    assert receipt.mapping_id == "CROSS_SECTIONAL_ZERO_NET"
    assert len(receipt.mapping_contract_sha256) == 64
    assert receipt.release_view_sha256 == _view_sha256()
    assert receipt.target_horizon_hours == 1
    assert receipt.source_code_sha == SOURCE_SHA
    assert receipt.target_execution_offset_hours == 2
    assert receipt.cache_key == repeat.cache_key
    assert receipt.receipt_sha256 == repeat.receipt_sha256
    payload = receipt.to_dict()
    assert payload["genome"] == _genome().canonical_dict()
    assert payload["pit_lag_contract"]["feature_observable_offset_hours"] == 1
    assert payload["pit_lag_contract"]["execution_offset_hours"] == 2
    assert payload["contracts"]["grammar_sha256"] == receipt.grammar_contract_sha256
    assert payload["contracts"]["cost_sha256"] == receipt.cost_contract_sha256


@pytest.mark.parametrize(
    ("genome", "argument_changes"),
    [
        (_genome(field_id="not_a_release_field"), {}),
        (_genome(primitive_id="b1s:delta"), {}),
        (_genome(), {"expected_mapping_id": "TIME_SERIES_DIRECTIONAL_STATEFUL"}),
        (
            _genome(),
            {
                "target_contract": {
                    **_target_contract(),
                    "execution_time": "t+1h",
                    "execution_delay_after_observable_hours": 0,
                }
            },
        ),
        (
            _genome(),
            {
                "release_manifest": _changed_manifest(
                    development_view_sha256="0" * 64
                )
            },
        ),
    ],
)
def test_invalid_candidate_or_contract_fails_before_reader_callback(
    genome: CandidateGenome, argument_changes: dict[str, object]
) -> None:
    reads: list[str] = []
    with pytest.raises((TypeError, ValueError, PermissionError)):
        _authorize(
            genome,
            **argument_changes,
            reader_callback=lambda: reads.append("must-not-run"),
        )
    assert reads == []


@pytest.mark.parametrize(
    ("field_id", "representation_id", "source", "expected", "clip_count"),
    [
        ("trade_count", "identity", [0.0, 1.0, 3.0], [0.0, 1.0, 3.0], 0),
        (
            "trade_count",
            "log1p_nonnegative",
            [0.0, 1.0, 3.0],
            [0.0, np.log(2.0), np.log(4.0)],
            0,
        ),
        (
            "vwap",
            "log_positive",
            [1e-12, 1.0, np.e],
            [np.log(1e-12), 0.0, 1.0],
            0,
        ),
        (
            "close_to_open_bps",
            "signed_log1p_abs",
            [-3.0, 0.0, 3.0],
            [-np.log(4.0), 0.0, np.log(4.0)],
            0,
        ),
        (
            "volume_imbalance",
            "atanh_clip_0_999",
            [-1.0, 0.0, 1.0],
            [np.arctanh(-0.999), 0.0, np.arctanh(0.999)],
            20,
        ),
        (
            "volume_imbalance",
            "atanh_clip_0_999",
            [-0.9995, 0.0, 0.9995],
            [np.arctanh(-0.9995), 0.0, np.arctanh(0.9995)],
            0,
        ),
        (
            "large_trade_count_ratio_100k_plus",
            "logit_clip_1e6",
            [0.0, 0.5, 1.0],
            [np.log(1e-6 / (1.0 - 1e-6)), 0.0, np.log((1.0 - 1e-6) / 1e-6)],
            20,
        ),
    ],
)
def test_frozen_representations_then_canonical_primitive_and_mapping(
    field_id: str,
    representation_id: str,
    source: list[float],
    expected: list[float],
    clip_count: int,
) -> None:
    receipt = _authorize(_genome(field_id=field_id, representation_id=representation_id))
    matrix = np.tile(np.asarray(source, dtype=float), (5, 2))
    materialized = materialize_authorized(receipt, field_reader=lambda name: matrix)

    np.testing.assert_allclose(materialized.represented_values[0, :3], expected)
    assert materialized.signal.shape == matrix.shape
    assert materialized.mapped.weights.shape == matrix.shape
    assert materialized.mapped.portfolio_mapping_id == receipt.mapping_id
    assert materialized.endpoint_clip_count == clip_count
    assert materialized.field_array_sha256
    assert materialized.represented_array_sha256
    assert materialized.signal_array_sha256
    assert materialized.weight_array_sha256
    assert materialized.to_dict()["candidate_id"] == receipt.candidate_id
    assert materialized.to_dict()["endpoint_clip_count"] == clip_count


@pytest.mark.parametrize(
    ("field_id", "representation_id", "source"),
    [
        ("trade_count", "log1p_nonnegative", [-0.001, 1.0]),
        ("vwap", "log_positive", [0.0, 1.0]),
        ("volume_imbalance", "atanh_clip_0_999", [-1.0001, 0.0]),
        ("large_trade_count_ratio_100k_plus", "logit_clip_1e6", [0.0, 1.0001]),
        ("close_to_open_bps", "signed_log1p_abs", [0.0, np.inf]),
    ],
)
def test_release_value_domain_drift_fails_closed_before_transform(
    field_id: str, representation_id: str, source: list[float]
) -> None:
    receipt = _authorize(_genome(field_id=field_id, representation_id=representation_id))
    with pytest.raises(ValueError, match="field|domain"):
        materialize_authorized(
            receipt,
            field_reader=lambda _: np.tile(np.asarray(source, dtype=float), (5, 3)),
        )


@pytest.mark.parametrize(
    ("mechanism_family", "primitive_id", "window", "threshold", "mapping_id"),
    [
        (CROSS_SECTIONAL_RELATIVE, "Delta", 2, None, "CROSS_SECTIONAL_ZERO_NET"),
        (
            DIRECTIONAL_STATEFUL,
            "Delta",
            2,
            None,
            "TIME_SERIES_DIRECTIONAL_STATEFUL",
        ),
        (SPARSE_EVENT_CARRY, "Transition", None, 0.0, "SPARSE_EVENT_OR_CARRY"),
    ],
)
def test_each_explicit_mapping_is_executable(
    mechanism_family: str,
    primitive_id: str,
    window: int | None,
    threshold: float | None,
    mapping_id: str,
) -> None:
    receipt = _authorize(
        _genome(
            primitive_id=primitive_id,
            window=window,
            threshold=threshold,
            mechanism_family=mechanism_family,
        )
    )
    source = np.vstack([np.arange(12, dtype=float) + shift for shift in range(5)])
    materialized = materialize_authorized(receipt, field_reader=lambda _: source)
    assert materialized.mapped.portfolio_mapping_id == mapping_id
    assert materialized.mapped.contract_sha256 == receipt.mapping_contract_sha256


def test_tampered_receipt_fails_before_field_reader() -> None:
    receipt = _authorize(_genome())
    tampered = replace(receipt, release_view_sha256="0" * 64)
    reads: list[str] = []
    with pytest.raises(ValueError, match="receipt"):
        materialize_authorized(
            tampered,
            field_reader=lambda name: reads.append(name) or np.ones((5, 8)),
        )
    assert reads == []
