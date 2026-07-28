from __future__ import annotations

import random
from pathlib import Path

import numpy as np

from alphafactory_crypto.broad_search.compositional18m import (
    CONDITIONAL_SEMANTIC_TUPLES,
    conditional_candidate_from_genes,
)
from alphafactory_crypto.broad_search.expression import (
    FieldContract,
    TypedExpressionRegistry,
)
from alphafactory_crypto.broad_search.pair18m import evaluate_pair
from alphafactory_crypto.broad_search.search_engine_v1 import (
    V14_CONFIG,
    _load_v14_config,
    _v14_domains,
    _v14_replay_verified,
    _v14_sample_conditional,
)


def _contracts() -> tuple[FieldContract, ...]:
    return (
        FieldContract(
            "bybit__open_interest_last", "VOLUME", "base_asset", 1, "TEST"
        ),
        FieldContract(
            "okx_futures__open_interest_last",
            "VOLUME",
            "base_asset",
            1,
            "TEST",
        ),
        FieldContract(
            "bybit__open_interest_value_last",
            "NOTIONAL",
            "quote_asset",
            1,
            "TEST",
        ),
        FieldContract(
            "bybit__mark_price_last",
            "PRICE",
            "quote_per_base",
            1,
            "TEST",
        ),
        FieldContract(
            "bybit__index_price_last",
            "PRICE",
            "quote_per_base",
            1,
            "TEST",
        ),
        FieldContract(
            "bybit__funding_rate_last",
            "RATIO",
            "dimensionless",
            1,
            "TEST",
        ),
        FieldContract(
            "signed_aggressor_notional",
            "SIGNED_FLOW",
            "quote_asset",
            1,
            "TEST",
        ),
        FieldContract(
            "volume_imbalance", "RATIO", "dimensionless", 1, "TEST"
        ),
        FieldContract(
            "price_range_bps", "BPS", "bps", 1, "TEST"
        ),
        FieldContract(
            "close_to_open_bps", "BPS", "bps", 1, "TEST"
        ),
        FieldContract(
            "large_notional_100k_plus",
            "NOTIONAL",
            "quote_asset",
            1,
            "TEST",
        ),
        FieldContract(
            "agg_trade_count", "COUNT", "observations", 1, "TEST"
        ),
    )


class _Store:
    def __init__(self, fields: dict[str, np.ndarray]) -> None:
        self._fields = fields
        self._base = np.ones_like(next(iter(fields.values())), dtype=bool)
        self.timestamp_ns = (
            np.datetime64("2025-07-01T00:00:00", "ns").astype("int64")
            + np.arange(self._base.shape[1], dtype=np.int64) * 3_600_000_000_000
        )
        rng = np.random.default_rng(99)
        self._target = rng.normal(
            0.0, 0.001, size=self._base.shape
        ).astype(float)

    def block_slice(self, start: str, end: str) -> slice:
        return slice(None)

    def base_eligible(self) -> np.ndarray:
        return self._base

    def field(self, field_id: str) -> np.ndarray:
        return self._fields[field_id]

    def candidate_support(
        self, field_ids: tuple[str, ...], block: slice
    ) -> np.ndarray:
        output = self._base.copy()
        for field_id in field_ids:
            output &= np.isfinite(self._fields[field_id])
        return output

    def target_return(self, horizon: int) -> np.ndarray:
        return self._target


def test_v14_config_freezes_staged_fresh_state_contract() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    config, path = _load_v14_config(repo_root)
    assert path == repo_root / V14_CONFIG
    assert tuple(config["semantic_tuples"]) == CONDITIONAL_SEMANTIC_TUPLES
    assert config["stage_b"]["typed_random_strict_count"] == 1200
    assert config["stage_c"]["enabled_only_if_stage_b_gate_passes"] is True
    assert not any(config["fresh_state"].values())
    assert config["boundaries"]["broad"] == "EXCLUDED"
    assert config["boundaries"]["core3"] == "EXCLUDED"


def test_all_v14_semantic_tuples_compile_at_depth_four_and_replay() -> None:
    registry = TypedExpressionRegistry(_contracts())
    domains = _v14_domains(_contracts())
    for index, semantic_tuple in enumerate(CONDITIONAL_SEMANTIC_TUPLES):
        candidate = _v14_sample_conditional(
            registry=registry,
            domains=domains,
            semantic_tuple=semantic_tuple,
            rng=random.Random(100 + index),
        )
        assert candidate.expression_depth == 4
        assert candidate.expression.operator == "StateModulation"
        assert candidate.expression.inputs[0].operator == "RatioInteraction"
        assert candidate.control.operator == "SupportMatchedPayload"
        assert _v14_replay_verified(registry, candidate)


def test_hierarchical_pair_records_ab_and_conditional_gates() -> None:
    registry = TypedExpressionRegistry(_contracts())
    domains = _v14_domains(_contracts())
    candidate = _v14_sample_conditional(
        registry=registry,
        domains=domains,
        semantic_tuple="OI_LEVEL_X_AGGRESSOR_FLOW_GIVEN_BASIS",
        rng=random.Random(17),
    )
    rng = np.random.default_rng(13)
    fields = {
        contract.field_id: rng.lognormal(
            mean=0.0, sigma=0.5, size=(8, 400)
        )
        for contract in _contracts()
    }
    fields["signed_aggressor_notional"] = rng.normal(
        0.0, 1.0, size=(8, 400)
    )
    fields["volume_imbalance"] = rng.normal(
        0.0, 0.3, size=(8, 400)
    )
    evaluation = evaluate_pair(
        store=_Store(fields),
        registry=registry,
        candidate=candidate,
        block_start="2025-07-01",
        block_end="2025-08-01",
        block_role="TEST",
    )
    assert evaluation["hierarchical_three_axis"] is True
    assert evaluation["interaction_left_incremental"] is not None
    assert evaluation["interaction_right_incremental"] is not None
    assert evaluation["conditional_incremental"] is not None
    assert evaluation["feedback"]["hierarchical_three_axis"] is True
    assert evaluation["pair_reward"] == min(
        evaluation["feedback"]["interaction_left_axis"]["distance"],
        evaluation["feedback"]["interaction_right_axis"]["distance"],
        evaluation["feedback"]["conditional_axis"]["distance"],
    )


def test_conditional_builder_rejects_role_unsafe_tuple() -> None:
    registry = TypedExpressionRegistry(_contracts())
    domains = _v14_domains(_contracts())
    candidate = _v14_sample_conditional(
        registry=registry,
        domains=domains,
        semantic_tuple=CONDITIONAL_SEMANTIC_TUPLES[0],
        rng=random.Random(7),
    )
    genes = dict(candidate.generation_genes)
    genes["right_field"] = "agg_trade_count"
    try:
        conditional_candidate_from_genes(registry, genes=genes)
    except ValueError as failure:
        assert "typed roles" in str(failure)
    else:  # pragma: no cover
        raise AssertionError("role-unsafe conditional tuple was accepted")
