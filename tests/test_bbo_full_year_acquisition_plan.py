from pathlib import Path

import scripts.crypto_bbo_full_year_acquisition_plan as plan


def test_capacity_grid_is_core12_full_2024() -> None:
    assert len(plan.CORE12) == 12
    assert len(plan.MONTHS) == 12
    assert plan.MONTHS[0] == "2024-01" and plan.MONTHS[-1] == "2024-12"


def test_official_url_is_monthly_um_bookticker() -> None:
    assert plan.source_url("BTCUSDT", "2024-03") == "https://data.binance.vision/data/futures/um/monthly/bookTicker/BTCUSDT/BTCUSDT-bookTicker-2024-03.zip"


def test_planner_contains_no_performance_or_candidate_loader() -> None:
    source = Path(plan.__file__).read_text(encoding="utf-8")
    for forbidden in ("multiobjective_evaluate(", "development_feedback(", "load_main_panel(", "strict_evaluations.csv"):
        assert forbidden not in source
