from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from alphafactory_crypto.broad_search.compositional18m import CandidateSpec
from alphafactory_crypto.broad_search.expression import Expression
from alphafactory_crypto.unified_field_management import compile_management_tables


ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads(
    (ROOT / "config/crypto_unified_field_management_v1.json").read_text(
        encoding="utf-8"
    )
)


@pytest.fixture(scope="module")
def tables() -> dict[str, pd.DataFrame]:
    return compile_management_tables(ROOT, CONFIG)


def test_every_discovered_field_has_one_canonical_management_record(
    tables: dict[str, pd.DataFrame],
) -> None:
    catalog = tables["unified_field_catalog"]
    assert len(catalog) == 5509
    assert catalog["canonical_field_id"].nunique() == len(catalog)
    assert set(tables["field_alias_map"]["canonical_field_id"]) <= set(
        catalog["canonical_field_id"]
    )


def test_canonical_identity_is_deterministic(
    tables: dict[str, pd.DataFrame],
) -> None:
    second = compile_management_tables(ROOT, CONFIG)
    pd.testing.assert_frame_equal(
        tables["unified_field_catalog"], second["unified_field_catalog"]
    )


def test_aliases_resolve_to_one_canonical_field(
    tables: dict[str, pd.DataFrame],
) -> None:
    aliases = tables["field_alias_map"]
    duplicate = aliases.loc[aliases["source_field_id"] == "agg_trade_count"]
    assert set(duplicate["canonical_field_id"]) == {"FIELD:agg_trade_count"}
    assert {
        "AGGTRADES_TOP200_DELIVERED",
        "CORE3_MICROSTRUCTURE_PILOT",
    } <= set(duplicate["authority_scope"])


def test_different_venue_or_unit_does_not_collapse(
    tables: dict[str, pd.DataFrame],
) -> None:
    catalog = tables["unified_field_catalog"].set_index("field_id")
    oi_fields = [
        field_id
        for field_id in catalog.index
        if str(field_id).endswith("__open_interest_last")
    ]
    assert len(oi_fields) >= 2
    assert (
        catalog.loc[oi_fields[0], "canonical_field_id"]
        != catalog.loc[oi_fields[1], "canonical_field_id"]
    )
    carrier = tables["carrier_field_matrix"]
    signatures = carrier.groupby("canonical_field_id")[
        ["value_type", "unit", "observable_lag_hours"]
    ].nunique()
    assert not (signatures > 1).any().any()


def test_derived_view_identity_is_deterministic(
    tables: dict[str, pd.DataFrame],
) -> None:
    derived = tables["derived_view_catalog"]
    row = derived.loc[
        derived["field_id"] == "ZScore_24h__agg_signed_aggressor_notional"
    ].iloc[0]
    assert "TRANSFORM:ZSCORE" in row["canonical_field_id"]
    assert len(row["recipe_identity_sha256"]) == 64


def test_prematerialized_derived_field_binds_to_existing_recipe(
    tables: dict[str, pd.DataFrame],
) -> None:
    derived = tables["derived_view_catalog"]
    assert len(derived) == 5211
    assert set(derived["materialization"]) == {"LAZY_EXISTING_RECIPE"}
    assert derived["authority_ref"].str.len().gt(0).all()


def test_provenance_only_field_cannot_receive_search_role(
    tables: dict[str, pd.DataFrame],
) -> None:
    blocked = set(CONFIG["provenance_only_fields"])
    roles = tables["search_role_binding"]
    assert blocked.isdisjoint(set(roles["field_id"]))
    catalog = tables["unified_field_catalog"]
    rows = catalog.loc[catalog["field_id"].isin(blocked)]
    assert len(rows) == len(blocked)
    assert rows["provenance_only"].all()
    assert not rows["search_allowed"].any()


def test_carrier_boundaries_are_not_merged(
    tables: dict[str, pd.DataFrame],
) -> None:
    carrier = tables["carrier_field_matrix"]
    assert set(carrier["carrier_id"]) == {
        "AGGTRADES_TOP200_DELIVERED",
        "BROAD_PANEL_BASELINE",
        "CORE3_MICROSTRUCTURE_PILOT",
        "OI_MARK_RANKS51_200_DELIVERED",
    }
    assert set(carrier["boundary"]) == {"INDEPENDENT_DATA_PLANE"}
    assert carrier.groupby("carrier_id").size().to_dict() == {
        "AGGTRADES_TOP200_DELIVERED": 44,
        "BROAD_PANEL_BASELINE": 39,
        "CORE3_MICROSTRUCTURE_PILOT": 81,
        "OI_MARK_RANKS51_200_DELIVERED": 71,
    }


def test_conflicting_authorities_fail_closed(tmp_path: Path) -> None:
    contracts = json.loads((ROOT / CONFIG["inputs"]["carrier_contracts"]).read_text())
    contracts["AGGTRADES_TOP200_DELIVERED"][0]["unit"] = "incompatible"
    path = tmp_path / "carrier_contracts.json"
    path.write_text(json.dumps(contracts), encoding="utf-8")
    config = json.loads(json.dumps(CONFIG))
    config["inputs"]["carrier_contracts"] = str(path)
    with pytest.raises(ValueError, match="conflicting field authorities"):
        compile_management_tables(ROOT, config)


def test_existing_search_fields_preserve_contract_identity(
    tables: dict[str, pd.DataFrame],
) -> None:
    carrier = tables["carrier_field_matrix"]
    assert (
        carrier.loc[
            carrier["field_id"] == "open_interest_value_last",
            "canonical_field_id",
        ].iloc[0]
        == "FIELD:open_interest_value_last"
    )
    assert len(carrier) == 235
    assert not carrier.duplicated(["carrier_id", "field_id"]).any()


def test_existing_candidate_spec_replay_is_unchanged() -> None:
    payload = {
        "candidate_id": "TEST-CANDIDATE",
        "skeleton_id": "OI_PRICE_DIVERGENCE_V1",
        "mechanism_family": "OI_PRICE_DIVERGENCE",
        "expression": Expression.raw("open_interest_value_last").canonical_dict(),
        "control": Expression.raw("trade_close").canonical_dict(),
        "horizon_hours": 4,
        "mapping_id": "TOP_BOTTOM_EQUAL",
        "raw_fields": ["open_interest_value_last", "trade_close"],
        "field_families": ["open_interest_value", "price_return"],
        "rolling_windows": [],
        "expression_depth": 1,
        "operator_path": "Raw",
        "generation_genes": {},
    }
    before = CandidateSpec.from_dict(payload)
    compile_management_tables(ROOT, CONFIG)
    after = CandidateSpec.from_dict(payload)
    assert before.to_dict() == after.to_dict()


def test_new_registry_can_be_added_without_duplicate_manual_entry(
    tables: dict[str, pd.DataFrame],
) -> None:
    aliases = tables["field_alias_map"]
    oi = aliases.loc[aliases["authority_scope"] == "OI_MARK_RANKS51_200_DELIVERED"]
    assert len(oi) == 71
    assert oi["source_field_id"].nunique() == 71


def test_no_second_ontology_or_approval_authority_is_created() -> None:
    source = (
        ROOT / "alphafactory_crypto/unified_field_management.py"
    ).read_text(encoding="utf-8")
    assert "to_csv" not in source
    assert "ontology.csv" not in source
    assert "approval_registry" not in source
