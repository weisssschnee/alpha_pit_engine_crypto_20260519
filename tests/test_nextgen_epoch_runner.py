from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("crypto_nextgen_epoch0", REPO / "scripts/crypto_nextgen_epoch0.py")
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


def candidate(proposal_id: str, lane: str, exact: str, mechanism: str, ordinal: int, proxy: float = 0.0) -> dict[str, object]:
    return {
        "proposal_id": proposal_id, "panel_id": "main", "lane_id": lane, "legal": True,
        "exact_identity": exact, "behaviour_cluster": f"b:{ordinal % 5}",
        "economic_hypothesis": f"h:{ordinal % 7}", "parent_identity": f"p:{ordinal % 11}",
        "mechanism_id": mechanism, "seed": 2701, "ordinal": ordinal, "proxy_score": proxy,
    }


def test_frozen_budget_shape_is_exactly_lower_authorized_bound() -> None:
    lane_proposals = {lane: 3840 for lane in runner.MAIN_LANES} | {runner.BBO_LANES[0]: 2048}
    strict = {lane: 112 for lane in runner.MAIN_LANES} | {runner.BBO_LANES[0]: 128}
    assert sum(lane_proposals.values()) == 32768
    assert sum(strict.values()) == 1024
    assert len(runner.MAIN_LANES) == 8
    assert runner.BBO_LANES == ("bbo_typed_temporal",)


def test_stratified_admission_enforces_global_exact_vote_and_natural_underfill() -> None:
    rows = []
    for lane in ("typed_ast", "cem"):
        for ordinal in range(20):
            exact = f"exact:{ordinal}" if lane == "typed_ast" else f"exact:{ordinal + 10}"
            rows.append(candidate(f"{lane}:{ordinal}", lane, exact, f"m:{ordinal % 3}", ordinal))
    admitted, _ = runner._admit_stratified(pd.DataFrame(rows), {"typed_ast": 16, "cem": 16})
    assert not admitted.duplicated(["panel_id", "exact_identity"]).any()
    assert len(admitted) < 32  # overlapping exact capacity is not filled by duplicate votes
    assert admitted["selected_for_strict"].all()


def test_global_top_k_is_exact_deduplicated_and_panel_scoped() -> None:
    rows = [candidate(f"p:{i}", "typed_ast", f"e:{i // 2}", "m", i, proxy=float(i)) for i in range(20)]
    frame = pd.DataFrame(rows)
    selected = runner._global_top_k(frame, "main", 5)
    selected_rows = frame.set_index("proposal_id").loc[selected]
    assert len(selected) == 5
    assert selected_rows["exact_identity"].nunique() == 5
    assert selected_rows["proxy_score"].is_monotonic_decreasing


def test_epoch_input_columns_are_observable_features_not_evaluation_blocks() -> None:
    forbidden = {"validation", "test", "recent", "stress", "oos", "forward", "return_label", "reward"}
    assert not any(any(token in column.lower() for token in forbidden) for column in runner.MAIN_COLUMNS)
    assert "feature_available_time" in runner.MAIN_COLUMNS


def test_algorithms_have_independent_runtime_lanes() -> None:
    assert runner.ALGORITHM_BY_LANE["cem"] == "cem"
    assert runner.ALGORITHM_BY_LANE["uct_mcts"] == "uct_mcts"
    assert runner.ALGORITHM_BY_LANE["evolutionary"] == "evolutionary_search"
    assert runner.ALGORITHM_BY_LANE["surrogate"] == "surrogate"
    assert runner.ALGORITHM_BY_LANE["llm_proposal_repair"] == "llm_proposal_repair"


def test_proposal_sketch_is_deterministic_and_keeps_panel_boundary() -> None:
    frozen = runner.FrozenPanel(
        "main", ("A", "B"), pd.date_range("2024-01-01", periods=12, freq="h", tz="UTC"),
        {"x": __import__("numpy").arange(24, dtype=float).reshape(2, 12)},
        __import__("numpy").zeros((2, 12)), "bucket_start_plus_1h", "bucket_close", "MAIN_ONLY",
    )
    first = runner.sketch_panel(frozen, 4)
    second = runner.sketch_panel(frozen, 4)
    assert first.timestamps.equals(second.timestamps)
    assert list(first.timestamps) == list(frozen.timestamps[::4])
    assert first.comparison_domain == "MAIN_ONLY"
