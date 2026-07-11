from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from alphafactory_crypto.b1s_canary import (
    FrozenPanel, assert_no_cross_panel_comparison, generate_proposals, global_top_k,
    materialize, rank_weights, strict_evaluate, stratified_strict_selection, validate_contract,
)
from scripts.crypto_b1s_canary import MAIN_COLUMNS


REPO = Path(__file__).resolve().parents[1]


def panel() -> FrozenPanel:
    timestamps = pd.date_range("2024-01-01", periods=240, freq="h", tz="UTC")
    shape = (6, len(timestamps))
    base = np.arange(np.prod(shape), dtype=float).reshape(shape)
    fields = {name: np.sin(base / (7 + i)) for i, name in enumerate((
        "funding", "basis", "oi", "liquidity", "taker", "volatility", "positioning",
        "funding_abs", "funding_change", "basis_abs", "oi_change", "session_sin", "session_cos",
        "asset_return", "market_return", "relative_market_return", "cross_confirmation",
    ))}
    target = np.cos(base / 13) * 0.001
    return FrozenPanel("main", tuple(f"S{i}" for i in range(6)), timestamps, fields, target,
                       "bucket_start_plus_1h", "bucket_close", "MAIN_ONLY")


class B1SCanaryTests(unittest.TestCase):
    def test_frozen_contract_budgets(self) -> None:
        config = json.loads((REPO / "config" / "crypto_b1s_canary_v1.json").read_text(encoding="utf-8"))
        validate_contract(config)

    def test_proposals_are_deterministic_and_exclude_disabled_capabilities(self) -> None:
        left = generate_proposals("main", "temporal_program", 1701)
        right = generate_proposals("main", "temporal_program", 1701)
        self.assertEqual(left, right)
        self.assertEqual(len(left), 256)
        self.assertFalse(any("liquidation" in item.canonical_program or "depth" in item.canonical_program for item in left))

    def test_materialization_and_strict_evaluator_are_deterministic(self) -> None:
        frozen = panel()
        spec = generate_proposals("main", "temporal_program", 1701, count=1)[0]
        signal = materialize(spec, frozen)
        weights = rank_weights(signal)
        self.assertEqual(strict_evaluate(weights, frozen), strict_evaluate(weights.copy(), frozen))

    def test_stratified_and_global_controls_obey_fixed_quota(self) -> None:
        rows = [{
            "proposal_id": f"p{i}", "panel_id": "main", "exact_identity": f"e{i}",
            "behaviour_potential": f"b{i%4}", "economic_hypothesis": f"h{i%3}",
            "ordinal": i, "proxy_score": float(i), "legal": True,
        } for i in range(80)]
        self.assertEqual(len(stratified_strict_selection(rows, 32)), 32)
        self.assertEqual(global_top_k(rows, 32, panel_id="main")[0], "p79")
        self.assertEqual(len(global_top_k(rows, 32, panel_id="main")), 32)

    def test_cross_panel_ranking_fails_closed(self) -> None:
        with self.assertRaises(PermissionError):
            assert_no_cross_panel_comparison("main", "bbo_micro")

    def test_main_read_projection_has_no_return_or_oos_column(self) -> None:
        forbidden = ("return", "label", "validation", "test", "recent", "stress", "oos", "forward")
        self.assertFalse(any(token in column.lower() for column in MAIN_COLUMNS for token in forbidden))


if __name__ == "__main__":
    unittest.main()
