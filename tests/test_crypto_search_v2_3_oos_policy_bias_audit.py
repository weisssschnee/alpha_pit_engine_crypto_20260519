from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.crypto_search_v2_3_oos_policy_bias_audit import (
    _correlation_summary,
    _moving_block_bootstrap,
)


def test_v23_oos_policy_bias_audit_helpers_are_deterministic() -> None:
    values = np.linspace(-0.001, 0.002, 181)
    first = _moving_block_bootstrap(values, label="determinism")
    second = _moving_block_bootstrap(values, label="determinism")

    assert first == second
    assert first["paired_day_count"] == 181
    assert first["block_length_days"] == 7
    assert first["replications"] == 4096


def test_v23_oos_policy_bias_audit_effective_rank_detects_duplicates() -> None:
    base = np.linspace(-1.0, 1.0, 181)
    frame = pd.DataFrame(
        {
            "duplicate_a": base,
            "duplicate_b": base,
            "opposite": -base,
        }
    )
    summary = _correlation_summary(frame)

    assert summary["candidate_count"] == 3
    assert summary["pair_share_above_0_90"] == 1.0 / 3.0
    assert summary["correlation_participation_ratio_effective_rank"] == 1.0
