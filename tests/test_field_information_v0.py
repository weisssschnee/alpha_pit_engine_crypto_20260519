from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from alphafactory_crypto.field_information import (
    FieldBatchProvider,
    apply_bins,
    build_core_pack,
    compile_token_catalog,
    cross_fitted_ridge_residual,
    discrete_mi,
    quantile_edges,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config/crypto_field_information_v0.json").read_text())


def test_token_catalog_traces_existing_inventory_without_new_authority() -> None:
    catalog = compile_token_catalog(ROOT, CONFIG)
    assert len(catalog) == 5388
    assert catalog["field_id"].nunique() == 5388
    assert catalog["token_id"].nunique() == 5388
    assert (catalog["token_kind"] == "DERIVED").sum() == 5211
    base = catalog.loc[catalog["field_id"] == "agg_signed_aggressor_notional"].iloc[0]
    assert base["token_id"] == "FIELD:agg_signed_aggressor_notional"
    derived = catalog.loc[
        catalog["field_id"] == "ZScore_24h__agg_signed_aggressor_notional"
    ].iloc[0]
    assert "TRANSFORM:ZSCORE" in derived["token_id"]
    assert "WINDOW:24H" in derived["token_id"]
    assert derived["authority_ref"]


def test_field_batch_provider_loads_only_requested_subsets() -> None:
    cube = np.arange(3 * 4 * 10, dtype=float).reshape(3, 4, 10)
    provider = FieldBatchProvider.from_cube(["a", "b", "c", "d"], cube)
    batch = provider.load(["FIELD:b", "FIELD:d"], [0, 2], slice(3, 7))
    assert batch.values.shape == (2, 2, 4)
    np.testing.assert_array_equal(batch.values[:, 0], cube[[0, 2], 1, 3:7])
    assert batch.masks.all()


def test_train_quantile_bins_and_block_residual_are_deterministic() -> None:
    values = np.arange(160, dtype=float)
    edges = quantile_edges(values[:80], bins=16)
    assert len(edges) == 15
    assert apply_bins(values, edges).max() == 15
    x = np.concatenate(
        [values.reshape(2, 1, 80), (values * 0.5).reshape(2, 1, 80)], axis=1
    )
    target = (0.2 * x[:, 0, :] - 0.1 * x[:, 1, :])
    eligible = np.ones_like(target, dtype=bool)
    months = np.array(["2024-01"] * 40 + ["2024-02"] * 40)
    first = cross_fitted_ridge_residual(x, target, eligible, months)
    second = cross_fitted_ridge_residual(x, target, eligible, months)
    np.testing.assert_allclose(first, second)
    assert np.nanstd(first) < np.nanstd(target)


def test_block_permutation_breaks_direct_information() -> None:
    feature = np.random.default_rng(20260717).integers(0, 16, size=320)
    target = feature.copy()
    shifted = np.roll(target, 16 * 3 + 5)
    assert discrete_mi(feature, target) > discrete_mi(feature, shifted)


def test_core_pack_balances_base_and_lazy_derived_tokens() -> None:
    catalog = compile_token_catalog(ROOT, CONFIG)
    broad_registry = json.loads(
        (ROOT / CONFIG["inputs"]["broad_registry"]).read_text(encoding="utf-8")
    )
    base = pd.read_csv(ROOT / CONFIG["inputs"]["aggtrades_base"])
    rows = []
    for context, fields in [
        (
            "BROAD_PANEL_BASELINE",
            [(row["field_id"], row["field_family"]) for row in broad_registry["fields"]],
        ),
        (
            "CORE3_MICROSTRUCTURE_PILOT",
            list(base[["field_name", "field_family"]].itertuples(index=False, name=None)),
        ),
    ]:
        for index, (field, family) in enumerate(fields):
            rows.append(
                {
                    "context_id": context,
                    "field_id": field,
                    "family": family,
                    "coverage_ratio": 0.99,
                    "normalized_value_entropy": 0.8,
                    "missingness_flag": "",
                    "current_runtime_member": context == "BROAD_PANEL_BASELINE" and index < 10,
                    "residual_mi_excess": 0.02 / (index + 1),
                    "mutual_information_excess": 0.01 / (index + 1),
                    "block_q25": 0.005 / (index + 1),
                    "max_redundancy_spearman": 0.2,
                    "redundancy_cluster_id": f"{context}:{field}",
                }
            )
    pack = build_core_pack(pd.DataFrame(rows), catalog)
    assert 80 <= len(pack) <= 160
    assert any(row["token_kind"] == "DERIVED" for row in pack)
    assert len({row["token_id"] for row in pack}) == len(pack)
    assert all(
        row["materialization"] != "CURRENT_CONTEXT_AVAILABLE"
        for row in pack
        if row["token_kind"] == "DERIVED"
    )


def test_context_boundaries_exclude_sealed_dates_and_dense_derived_materialization() -> None:
    assert CONFIG["boundaries"]["latest_timestamp_exclusive"] == "2024-07-01T00:00:00Z"
    assert CONFIG["boundaries"]["sealed_reads_allowed"] is False
    assert CONFIG["boundaries"]["derived_dense_materialization"] is False
    assert CONFIG["contexts"]["CORE3_MICROSTRUCTURE_PILOT"]["symbols"] == [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
    ]
