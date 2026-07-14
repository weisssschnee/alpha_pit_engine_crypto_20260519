from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from alphafactory_crypto.frontier_v2.arena import evaluate_common_bridge, paired_increment
from alphafactory_crypto.frontier_v2.release import (
    canonical_sha256,
    preflight_external_release,
    sha256_file,
)


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config/crypto_frontier_research_v2.json"


def test_v2_contract_keeps_all_frozen_boundaries() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    boundaries = config["boundaries"]
    assert boundaries["allowed_role"] == "DEVELOPMENT"
    assert all(value for key, value in boundaries.items() if key != "allowed_role")
    assert config["qlib"]["git_commit"] == "da920b7f954f48ab1bb64117c976710de198373e"
    assert config["deepdow"]["git_commit"] == "384e18acc17c982ac5a4362187b348bdbdb07b98"
    assert config["budget"]["qlib_fits"] == 2
    assert config["budget"]["deepdow_fits"] == 4


def test_common_bridge_uses_delayed_label_and_paired_block_lcb() -> None:
    dates = pd.date_range("2024-06-01", periods=12, freq="D", tz="UTC")
    rows = []
    for symbol, sign in (("A", 1.0), ("B", -1.0)):
        for ordinal, date in enumerate(dates):
            rows.append(
                {
                    "date": date,
                    "symbol": symbol,
                    "label_1d_delayed": sign * (ordinal + 1) / 1000,
                }
            )
    daily = pd.DataFrame(rows)
    challenger = pd.DataFrame({"A": 1.0, "B": 0.0}, index=dates)
    control = pd.DataFrame({"A": 0.5, "B": 0.5}, index=dates)
    cm, cp = evaluate_common_bridge(
        daily,
        challenger,
        system_id="C",
        cost_bps_per_unit_turnover=5,
        annualization=365,
        block_days=3,
        bootstrap_samples=200,
    )
    _, bp = evaluate_common_bridge(
        daily,
        control,
        system_id="B",
        cost_bps_per_unit_turnover=5,
        annualization=365,
        block_days=3,
        bootstrap_samples=200,
    )
    comparison = paired_increment(
        cp,
        bp,
        challenger_id="C",
        control_id="B",
        block_days=3,
        bootstrap_samples=200,
    )
    assert cm.observations == 12
    assert comparison["paired_net_increment_mean"] > 0
    assert comparison["paired_net_increment_lcb_95"] > 0


def test_external_release_entry_checks_hash_schema_role_and_pit(tmp_path: Path) -> None:
    data = pd.DataFrame(
        {
            "venue": ["X", "X"],
            "symbol": ["A", "A"],
            "event_time": ["2024-01-01T00:00:00Z", "2024-01-01T00:01:00Z"],
            "observed_time": ["2024-01-01T00:00:01Z", "2024-01-01T00:01:01Z"],
            "maturity": ["2024-01-01T00:00:01Z", "2024-01-01T00:01:01Z"],
            "price": [1.0, 1.1],
            "quantity": [2.0, 3.0],
        }
    )
    data_path = tmp_path / "development.csv"
    data.to_csv(data_path, index=False, lineterminator="\n")
    coverage_path = tmp_path / "coverage.csv"
    pd.DataFrame({"symbol": ["A"], "coverage": [1.0]}).to_csv(
        coverage_path, index=False, lineterminator="\n"
    )
    file_record = {"path": data_path.name, "sha256": sha256_file(data_path), "rows": len(data)}
    content_sha = canonical_sha256(
        [{"path": data_path.resolve().as_posix(), "sha256": file_record["sha256"], "rows": len(data)}]
    )
    manifest = {
        "release_id": "TEST_DEV_RELEASE",
        "family": "cross_venue_trades_quotes",
        "data_role": "DEVELOPMENT",
        "source_url": "https://example.invalid/source",
        "license": "test",
        "content_sha256": content_sha,
        "schema": list(data.columns),
        "event_time_semantics": "exchange event timestamp",
        "observable_time_semantics": "arrival timestamp",
        "maturity_semantics": "arrival timestamp",
        "coverage_ledger": {"path": coverage_path.name, "sha256": sha256_file(coverage_path)},
        "missing_policy": "no fill",
        "allowed_research_roles": ["DEVELOPMENT_ONLY_REPRODUCTION"],
        "files": [file_record],
        "primary_key": ["venue", "symbol", "event_time"],
        "time_fields": {"event": "event_time", "observable": "observed_time", "maturity": "maturity"},
        "coverage_ratio": 1.0,
        "minimum_coverage_ratio": 0.95,
        "consumer_ids": ["QLIB_V097_NATIVE_FULL"],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    contract = json.loads(CONFIG.read_text(encoding="utf-8"))["external_release_entry"]
    result = preflight_external_release(manifest_path, contract)
    assert result["ready"] is True
    assert result["point_in_time_checked"] is True


def test_supersession_does_not_rewrite_historical_runner() -> None:
    old_runner = (REPO / "scripts/crypto_external_frontier_assimilation.py").read_text(encoding="utf-8")
    new_runner = (REPO / "scripts/crypto_frontier_research_v2.py").read_text(encoding="utf-8")
    assert '"real_end_to_end_reproductions": 2' in old_runner
    assert "supersession_decision.json" in new_runner
    assert "candidate_promotion\": False" in new_runner
