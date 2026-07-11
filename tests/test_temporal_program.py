from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from alphafactory_crypto.temporal_program import (
    PRIMITIVES, ObservationVector, TypedProgram, canonical_program, equivalent, evaluate, program_identity,
)


def observations(lag_hours: int = 0) -> ObservationVector:
    index = pd.date_range("2026-01-01", periods=24, freq="h", tz="UTC")
    values = pd.Series(np.arange(24, dtype=float), index=index)
    observable = pd.Series(index + pd.Timedelta(hours=lag_hours), index=index)
    maturity = pd.Series(index, index=index)
    return ObservationVector(values, observable, maturity)


class TemporalProgramTests(unittest.TestCase):
    def test_every_required_primitive_is_typed_canonical_and_deterministic(self) -> None:
        params = {
            "Delta": {"periods": 2}, "Slope": {"periods": 3}, "Acceleration": {"periods": 2},
            "Persistence": {"periods": 3}, "Duration": {}, "StateAge": {}, "TimeSince": {},
            "Transition": {}, "FirstHit": {}, "LastHit": {}, "PathShape": {"periods": 6},
            "EventWindow": {"periods": 3},
            "MultiScaleRelation": {"short_periods": 2, "long_periods": 6},
        }
        self.assertEqual(len(PRIMITIVES), 13)
        for primitive in PRIMITIVES:
            program = TypedProgram(primitive, "field:test", params[primitive])
            self.assertEqual(program_identity(program), program_identity(program))
            self.assertEqual(len(evaluate(program, observations())), 24)

    def test_pit_source_lag_prevents_same_bar_visibility(self) -> None:
        result = evaluate(TypedProgram("Delta", "field:test", {"periods": 1}), observations(lag_hours=1))
        self.assertTrue(pd.isna(result.iloc[0]))
        self.assertEqual(result.iloc[2], 1.0)

    def test_equivalence_normalizes_parameter_order_and_negative_zero(self) -> None:
        left = TypedProgram("Persistence", "x", {"periods": 3, "threshold": -0.0})
        right = TypedProgram("Persistence", "x", {"threshold": 0.0, "periods": 3})
        self.assertTrue(equivalent(left, right))

    def test_contract_change_changes_identity(self) -> None:
        left = TypedProgram("Delta", "x", {"periods": 1})
        right = TypedProgram("Delta", "x", {"periods": 1}, maturity_rule="window_close")
        self.assertFalse(equivalent(left, right))

    def test_invalid_multiscale_and_observable_time_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            canonical_program(TypedProgram("MultiScaleRelation", "x", {"short_periods": 6, "long_periods": 2}))
        obs = observations()
        bad = ObservationVector(obs.values, obs.observable_time - pd.Timedelta(hours=1), obs.maturity_time)
        with self.assertRaises(ValueError):
            evaluate(TypedProgram("Delta", "x", {"periods": 1}), bad)


if __name__ == "__main__":
    unittest.main()
