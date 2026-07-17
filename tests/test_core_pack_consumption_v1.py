from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from alphafactory_crypto.core_pack_consumption import (
    BROAD_CONTEXT,
    CORE3_CONTEXT,
    ResolvedToken,
    dense_consumption_probe,
    materialize_core3_context,
    qualify_consumption_rows,
    resolve_core_pack,
)


ROOT = Path(__file__).resolve().parents[1]


def test_real_core_pack_resolves_to_two_contexts_and_120_unique_tokens() -> None:
    pack = json.loads(
        (ROOT / "runtime/crypto_field_information_v0_20260717/core_pack_manifest.json").read_text()
    )
    base = pd.read_csv(
        ROOT
        / "runtime/crypto_feature_runtime_inventory_20260714/aggtrades_base_feature_registry_94.csv"
    )
    derived = pd.read_csv(
        ROOT
        / "runtime/crypto_feature_runtime_inventory_20260714/aggtrades_derived_feature_specs_5211.csv"
    )
    resolved = resolve_core_pack(pack, base, derived)
    assert len(resolved) == 120
    assert len({row.token_id for row in resolved}) == 120
    assert sum(row.context_id == BROAD_CONTEXT for row in resolved) == 39
    assert sum(row.context_id == CORE3_CONTEXT for row in resolved) == 81
    assert sum(row.token_kind == "DERIVED" for row in resolved) == 45
    zscore = next(row for row in resolved if "TRANSFORM:ZSCORE" in row.token_id)
    assert zscore.expression.startswith("ZScore(Mean(")
    assert zscore.alignment_shift_bars == zscore.feature_available_lag_bars - 1
    decay = next(row for row in resolved if "TRANSFORM:DECAY" in row.token_id)
    assert decay.execution_semantics == "TRAILING_LINEAR_DECAY"


def _contract(field: str, kind: str = "BASE", *, lag: int = 1) -> ResolvedToken:
    expression = field if kind == "BASE" else f"Delta({field},4)"
    token = f"FIELD:{field}" if kind == "BASE" else f"FIELD:{field}|DELTA"
    return ResolvedToken(
        ordinal=1 if kind == "BASE" else 2,
        token_id=token,
        field_id=field if kind == "BASE" else f"Delta_4h__{field}",
        token_kind=kind,
        context_id=CORE3_CONTEXT,
        family="flow",
        expression=expression,
        base_dependencies=(field,),
        feature_available_lag_bars=lag,
        alignment_shift_bars=max(0, lag - 1),
        execution_semantics="TEST",
        authority_ref="TEST",
    )


def _panel(path: Path, future_offset: float = 0.0) -> None:
    rows = []
    timestamps = pd.date_range("2024-01-01", periods=96, freq="h", tz="UTC")
    for symbol_index, symbol in enumerate(("BTCUSDT", "ETHUSDT", "SOLUSDT")):
        for index, timestamp in enumerate(timestamps):
            value = float(index + symbol_index)
            if index >= 70:
                value += future_offset
            rows.append(
                {
                    "symbol": symbol,
                    "timestamp": timestamp,
                    "close": 100.0 + index + symbol_index,
                    "agg_features_available": True,
                    "x": value,
                }
            )
    pd.DataFrame(rows).to_parquet(path, index=False)


def test_core3_materialization_is_causal_and_applies_registry_lag(tmp_path: Path) -> None:
    first = tmp_path / "first.parquet"
    second = tmp_path / "second.parquet"
    _panel(first)
    _panel(second, future_offset=10_000.0)
    context = {
        "symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT"],
        "start": "2024-01-01T00:00:00Z",
        "end_exclusive": "2024-01-05T00:00:00Z",
    }
    contracts = [_contract("x"), _contract("x", "DERIVED", lag=4)]
    left, _, _, summary = materialize_core3_context(first, contracts, context)
    right, _, _, _ = materialize_core3_context(second, contracts, context)
    assert summary["maximum_alignment_shift_bars"] == 3
    for symbol_index in range(3):
        start = symbol_index * 96
        np.testing.assert_allclose(
            left[start : start + 60], right[start : start + 60], equal_nan=True
        )
    assert np.isnan(left[:7, 1]).all()


def test_dense_probe_reaches_updates_and_ablates_every_channel() -> None:
    rng = np.random.default_rng(20260718)
    values = rng.normal(size=(1024, 6)).astype(np.float32)
    target = (values[:, 0] - 0.5 * values[:, 1] + rng.normal(scale=0.1, size=1024)).astype(
        np.float32
    )
    summary, rows = dense_consumption_probe(
        values,
        target,
        seed=20260718,
        maximum_samples=1024,
        epochs=4,
        hidden_width=8,
        learning_rate=0.01,
        ablation_samples=256,
    )
    assert summary["gradient_reachable_channels"] == 6
    assert summary["updated_value_channels"] == 6
    assert summary["ablation_sensitive_channels"] == 6
    assert isinstance(summary["training_loss_decreased"], bool)
    materialized = [
        {"finite_rows": 1024, "finite_ratio": 1.0, "variance": 1.0} for _ in rows
    ]
    qualified = qualify_consumption_rows(materialized, rows, minimum_finite_ratio=0.05)
    assert all(row["plumbing_pass"] for row in qualified)
    assert all(row["nontrivial_utilization_pass"] for row in qualified)
    assert all(row["consumption_pass"] for row in qualified)
