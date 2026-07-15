from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from alphafactory_crypto.instrument_canary.release import ReleasePanel


class ReleasePanelTests(unittest.TestCase):
    def _panel(self) -> ReleasePanel:
        timestamps = pd.date_range("2024-01-01", periods=8, freq="h", tz="UTC")
        return ReleasePanel(
            release_id="release",
            development_view_id="view",
            assets=("A",),
            timestamps=timestamps,
            fields={"trade_count": np.arange(8.0).reshape(1, 8)},
            close_price=np.exp(np.arange(8.0) / 100.0).reshape(1, 8),
            month_labels=np.array(["2024-01"] * 8),
            observable_times=timestamps + pd.Timedelta(hours=1),
            release_manifest={"development_view_sha256": "view-hash"},
        )

    def test_arrays_and_field_mapping_are_read_only(self) -> None:
        panel = self._panel()
        with self.assertRaises(ValueError):
            panel.fields["trade_count"][0, 0] = 9.0
        with self.assertRaises(ValueError):
            panel.close_price[0, 0] = 9.0
        with self.assertRaises(TypeError):
            panel.fields["new"] = np.zeros((1, 8))
        with self.assertRaises(TypeError):
            panel.release_manifest["new"] = "value"

    def test_target_waits_one_complete_hour_after_observability(self) -> None:
        panel = self._panel()
        one_hour = panel.target_return(1)
        four_hour = panel.target_return(4)
        self.assertAlmostEqual(one_hour[0, 0], 0.01)
        self.assertAlmostEqual(four_hour[0, 0], 0.04)
        self.assertTrue(np.isnan(one_hour[0, -3:]).all())
        self.assertTrue(np.isnan(four_hour[0, -6:]).all())


if __name__ == "__main__":
    unittest.main()
