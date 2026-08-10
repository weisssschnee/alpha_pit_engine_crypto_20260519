from __future__ import annotations

import json
import tarfile
from pathlib import Path

import pandas as pd

from alphafactory_crypto.broad_search.p4_mechanism_pocket_validation_v1 import (
    build_summary,
    load_receipt,
    load_selection,
)
from scripts.acquire_binance_daily_aggtrades_compact_v1 import package_rank_group


ROOT = Path(__file__).resolve().parents[1]


def _result_row(
    candidate_id: str,
    behavior: str,
    group: str,
    family: str,
    *,
    train_reward: float,
    matched: bool,
    net: float,
    lcb: float,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "behavior_family_id": behavior,
        "selection_group": group,
        "program_family_id": family,
        "completion_ordinal": int(candidate_id.rsplit("-", 1)[-1]),
        "strict_evaluated": True,
        "train_search_reward": train_reward,
        "fresh_search_reward": train_reward / 2.0,
        "fresh_matched_positive": matched,
        "fresh_left_incremental_net_mean": net,
        "fresh_right_incremental_net_mean": net,
        "fresh_left_incremental_gross_mean": net + 0.01,
        "fresh_right_incremental_gross_mean": net + 0.01,
        "fresh_left_incremental_net_lcb": lcb,
        "fresh_right_incremental_net_lcb": lcb,
    }


def test_frozen_selection_contains_exact_candidates_and_directions() -> None:
    receipt, rows = load_selection(ROOT)
    assert receipt["receipt_sha256"] == (
        "F80DA0531A46660766423B90073F1F861DA89F56A00F3869939BF7CFFCDE6858"
    )
    assert len(rows) == 80
    assert len({row["candidate_id"] for row in rows}) == 80
    assert {row["train_orientation"] for row in rows} == {-1.0, 1.0}
    assert sum(row["selection_group"] == "discovery_matched_positive" for row in rows) == 40


def test_run_receipt_freezes_one_no_feedback_development_gate() -> None:
    receipt = load_receipt(ROOT, require_authorized=True)
    assert receipt["compute"]["candidate_count"] == 80
    assert receipt["economic_contract"]["cost_bps"] == 5.0
    assert receipt["development_fresh_interval"]["role"] == (
        "DEVELOPMENT_FRESH_NO_FEEDBACK_NOT_OOS"
    )
    assert not any(receipt["boundaries"].values())


def test_summary_reports_raw_and_behavior_deoverlapped_views() -> None:
    p4 = "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"
    p1 = "P1_POSITION_STATE_CHANGE_TO_RESPONSE"
    rows = [
        _result_row("candidate-1", "same", "discovery_matched_positive", p4, train_reward=2.0, matched=True, net=0.1, lcb=0.01),
        _result_row("candidate-2", "same", "discovery_matched_positive", p4, train_reward=1.0, matched=False, net=-0.1, lcb=-0.01),
        _result_row("candidate-3", "p1", "discovery_matched_positive", p1, train_reward=1.0, matched=False, net=0.1, lcb=-0.01),
        _result_row("candidate-4", "evo", "evolution_near_miss_control", p4, train_reward=0.0, matched=False, net=-0.1, lcb=-0.01),
        _result_row("candidate-5", "rnd", "random_near_miss_control", p4, train_reward=-1.0, matched=False, net=-0.1, lcb=-0.01),
    ]
    summary = build_summary(rows)
    assert summary["raw_candidate_count"] == 5
    assert summary["behavior_family_deoverlapped_count"] == 4
    p4_metrics = summary["discovery_program_family_behavior_family_deoverlapped"][p4]
    assert p4_metrics["source_count"] == 1
    assert p4_metrics["fresh_matched_positive_count"] == 1
    assert summary["research_result"] == "P4_POCKET_FRESH_MATCHED_REPLICATION_OBSERVED"


def test_daily_compact_packaging_preserves_existing_carrier_layout(tmp_path: Path) -> None:
    combined = tmp_path / "combined"
    ranking = [(1, "BTCUSDT"), (101, "ETHUSDT")]
    for rank, symbol in ranking:
        month = "2026-08"
        done = combined / "done" / symbol / f"{month}.json"
        manifest = combined / "object_manifest" / f"symbol={symbol}" / f"{month}.json"
        parquet = combined / "compact_1m" / f"symbol={symbol}" / f"month={month}" / "part.parquet"
        done.parent.mkdir(parents=True, exist_ok=True)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        parquet.parent.mkdir(parents=True, exist_ok=True)
        payload = {"status": "complete", "rank": rank}
        done.write_text(json.dumps(payload), encoding="utf-8")
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        pd.DataFrame({"timestamp": pd.to_datetime(["2026-08-01"], utc=True)}).to_parquet(parquet, index=False)
    result = package_rank_group(
        data_root=tmp_path,
        combined_root=combined,
        ranking=ranking,
        first_rank=1,
        last_rank=100,
        name="top100",
        month="2026-08",
    )
    assert result["member_count"] == 3
    assert Path(result["path"] + ".sha256").is_file()
    with tarfile.open(result["path"]) as archive:
        names = set(archive.getnames())
    assert "combined/done/BTCUSDT/2026-08.json" in names
    assert "combined/compact_1m/symbol=BTCUSDT/month=2026-08/part.parquet" in names
