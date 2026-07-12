from __future__ import annotations

import json
from pathlib import Path

import scripts.crypto_mechanism_data_inventory as inventory


def test_path_inference_covers_priority_mechanism_families() -> None:
    bbo = r"D:\data\binance\um\bookTicker\BTCUSDT\2024-01.csv"
    forced = r"D:\data\bybit\perp\liquidation\ETHUSDT\2024_02.parquet"
    options = r"D:\data\deribit\options\BTCUSD\2024-03.parquet"

    assert inventory.infer_venue(bbo) == "BINANCE"
    assert inventory.infer_market(bbo) == "PERPETUAL_OR_FUTURES"
    assert inventory.infer_family(bbo) == "BOOKTICKER_BBO"
    assert inventory.infer_symbol(bbo) == "BTCUSDT"
    assert inventory.infer_month(bbo) == "2024-01"
    assert inventory.infer_family(forced) == "LIQUIDATION_FORCE_ORDER"
    assert inventory.infer_family(options) == "OPTIONS"


def test_sealed_path_blocks_header_and_footer_reads(tmp_path: Path, monkeypatch) -> None:
    sealed = tmp_path / "forward" / "binance_bookTicker_BTCUSDT_2024-01.csv"
    sealed.parent.mkdir()
    sealed.write_text("return_label,secret\n1,2\n", encoding="utf-8")

    def forbidden(_: Path) -> str:
        raise AssertionError("sealed header must not be read")

    monkeypatch.setattr(inventory, "header_fields", forbidden)
    row = inventory.inventory_file(sealed, tmp_path, "TEST_PC")

    assert row["sealed_path"] is True
    assert row["data_role"] == "SEALED_METADATA_ONLY"
    assert row["fields"] == ""
    assert row["footer_status"] == "BLOCKED_SEALED_PATH"
    assert row["row_data_read"] is False


def test_inventory_run_is_metadata_only_and_hashes_outputs(tmp_path: Path, monkeypatch) -> None:
    # Pytest's temporary parent contains the governance token ``test``; this
    # case exercises an explicitly unsealed historical source.
    monkeypatch.setattr(inventory, "is_sealed", lambda _: False)
    root = tmp_path / "raw"
    root.mkdir()
    (root / "binance_um_bookTicker_BTCUSDT_2024-01.csv").write_text(
        "event_time,bid_price,ask_price,bid_qty,ask_qty\n", encoding="utf-8"
    )
    output = tmp_path / "out"

    inventory.run([root], output)
    manifest = json.loads((output / "inventory_manifest.json").read_text(encoding="utf-8"))
    availability = json.loads((output / "mechanism_source_availability.json").read_text(encoding="utf-8"))

    assert manifest["files"] == 1
    assert manifest["row_data_read"] is False
    assert manifest["sealed_paths_footer_read"] is False
    assert manifest["performance_queries"] == 0
    assert len(manifest["outputs"]) == 4
    assert all(len(item["sha256"]) == 64 for item in manifest["outputs"])
    assert availability["native_bbo"] == "DISCOVERED_REQUIRES_QUALIFICATION"
    assert availability["forced_flow_liquidation"] == "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE"
    assert availability["proxy_substitution_allowed"] is False


def test_family_aggregation_and_cross_venue_discovery() -> None:
    base = {
        "market_type": "PERPETUAL_OR_FUTURES",
        "files": 1,
        "sealed_files": 0,
    }
    families = [
        {**base, "venue": "BINANCE", "data_family": "KLINES"},
        {**base, "venue": "OKX", "data_family": "KLINES"},
        {**base, "venue": "BINANCE", "data_family": "AGG_TRADES"},
    ]

    result = inventory.availability(families)

    assert result["cross_venue_price_discovery"] == "DISCOVERED_REQUIRES_QUALIFICATION"
    assert result["trade_flow"] == "DISCOVERED_REQUIRES_QUALIFICATION"
    assert result["options_expectation_state"] == "UNAVAILABLE_NO_VERIFIED_HISTORICAL_SOURCE"
    assert result["observed_venues"] == ["BINANCE", "OKX"]


def test_large_dataset_inventory_is_complete_but_metadata_is_capped(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(inventory, "is_sealed", lambda _: False)
    root = tmp_path / "raw"
    root.mkdir()
    for ordinal in range(5):
        (root / f"binance_bookTicker_BTCUSDT_2024-01-{ordinal}.csv").write_text(
            "event_time,bid_price,ask_price\n", encoding="utf-8"
        )
    output = tmp_path / "out"

    inventory.run([root], output, metadata_samples_per_dataset=2)
    manifest = json.loads((output / "inventory_manifest.json").read_text(encoding="utf-8"))
    file_rows = (output / "file_inventory.csv").read_text(encoding="utf-8").splitlines()

    assert manifest["files"] == 5
    assert manifest["metadata_files_inspected"] == 2
    assert manifest["metadata_samples_per_dataset"] == 2
    assert len(file_rows) == 6


def test_static_contract_contains_no_evaluator_or_label_read() -> None:
    source = Path(inventory.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "multiobjective_evaluate(",
        "development_feedback(",
        "load_main_panel(",
        "return_label",
        "fwd_ret",
    ):
        assert forbidden not in source
