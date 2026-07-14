from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from alphafactory_crypto.frontier_v2.qualification import (
    _prediction_comparison,
    _weight_comparison,
    base_bundle_attestation,
    build_artifact_index,
    evaluate_data_adequacy,
    plan_new_release_activation,
)


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config" / "crypto_frontier_evidence_qualification_v1.json"
BASE_ROOT = REPO / "runtime" / "crypto_frontier_research_v2_20260713"


class EvidenceQualificationTests(unittest.TestCase):
    def test_contract_preserves_all_frozen_boundaries(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        activation = config["new_release_activation"]
        self.assertTrue(activation["development_only"])
        self.assertTrue(activation["run_only_if_data_adequacy_passes"])
        for key in (
            "new_performance_search",
            "challenge_read",
            "forward_read",
            "recent_read",
            "may_stress_read",
            "candidate_promotion",
            "cross_sprint_adaptive_memory",
        ):
            self.assertFalse(activation[key])
        repair = config["qlib_one_shot_repair"]
        self.assertEqual(repair["fixed_fits"], 2)
        self.assertEqual(repair["parameter_trials"], 1)
        self.assertFalse(repair["search_performed"])
        self.assertEqual(set(repair["model_overrides"]), {"lambda_l1", "lambda_l2"})

    def test_prediction_and_weight_degeneracy_are_exact_not_rounded(self) -> None:
        rows = []
        for variant in ("FULL_ALPHA158", "FIRST_13_CONTROL"):
            for date in pd.date_range("2024-06-01", periods=2):
                for instrument in ("A", "B"):
                    rows.append(
                        {
                            "datetime": date,
                            "instrument": instrument,
                            "score": 1e-8,
                            "variant": variant,
                        }
                    )
        comparison = _prediction_comparison(pd.DataFrame(rows))
        self.assertTrue(comparison["exact_equality"])
        self.assertFalse(comparison["difference_is_only_report_rounding"])
        weights = pd.DataFrame(
            [[0.5, 0.5], [0.4, 0.6]],
            index=pd.date_range("2024-06-01", periods=2, tz="UTC"),
            columns=["A", "B"],
        )
        weight_comparison = _weight_comparison(weights, weights.copy())
        self.assertTrue(weight_comparison["exact_equality"])
        self.assertEqual(weight_comparison["max_daily_l1_difference"], 0.0)

    def test_data_adequacy_gate_fails_each_unmet_minimum(self) -> None:
        thresholds = {
            "P": {
                "min_development_dates": 60,
                "min_training_samples": 500,
                "min_cross_sectional_assets": 10,
                "min_feature_non_null_rate": 0.95,
                "min_positive_variance_feature_fraction": 1.0,
                "min_history_days": 365,
                "min_label_support": 0.95,
                "min_turnover_observations": 60,
                "min_independent_evaluation_blocks": 12,
            }
        }
        actual = {
            "P": {
                "development_dates": 23,
                "training_samples": 84,
                "cross_sectional_assets": 10,
                "feature_non_null_rate": 1.0,
                "positive_variance_feature_fraction": 1.0,
                "history_days": 182,
                "label_support": 1.0,
                "turnover_observations": 23,
                "independent_evaluation_blocks": 4,
            }
        }
        rows, summary = evaluate_data_adequacy(thresholds, actual)
        self.assertEqual(summary["P"]["status"], "DATA_ADEQUACY_UNDERPOWERED")
        self.assertEqual(
            set(summary["P"]["failed_conditions"]),
            {
                "development_dates",
                "training_samples",
                "history_days",
                "turnover_observations",
                "independent_evaluation_blocks",
            },
        )
        self.assertEqual(int(rows.passed.sum()), 4)

    def test_base_bundle_manifest_recomputes_122_identity(self) -> None:
        result = base_bundle_attestation(REPO, BASE_ROOT)
        self.assertEqual(result["artifact_count"], 122)
        self.assertEqual(
            result["bundle_sha256"],
            "99C0DACAF12F17DA6B7705DDBFCE9BAD996143082301F47BCA7E690071140EF2",
        )
        self.assertEqual(result["content_verification"]["missing"], [])
        self.assertEqual(result["content_verification"]["drift"], [])

    def test_qualification_index_excludes_runner_and_self_references(self) -> None:
        runtime_parent = REPO / "runtime"
        with tempfile.TemporaryDirectory(dir=runtime_parent) as directory:
            root = Path(directory)
            (root / "evidence.json").write_text("{}\n", encoding="utf-8")
            (root / "runner.run.log").write_text("volatile\n", encoding="utf-8")
            (root / "seal_result.json").write_text("{}\n", encoding="utf-8")
            result = build_artifact_index(REPO, root)
            index = pd.read_csv(root / "artifact_index.csv")
            self.assertEqual(result["artifact_count"], 1)
            self.assertEqual(index.artifact.str.endswith("evidence.json").sum(), 1)

    def test_direct_activation_selects_two_adequate_external_paradigms(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        profiles = {}
        for paradigm in ("QLIB_CROSS_SECTIONAL_DAILY", "DEEPDOW_DIRECT_5D"):
            threshold = config["data_adequacy_gate"][paradigm]
            profiles[paradigm] = {
                "development_dates": threshold["min_development_dates"],
                "training_samples": threshold["min_training_samples"],
                "cross_sectional_assets": threshold["min_cross_sectional_assets"],
                "feature_non_null_rate": threshold["min_feature_non_null_rate"],
                "positive_variance_feature_fraction": threshold[
                    "min_positive_variance_feature_fraction"
                ],
                "history_days": threshold["min_history_days"],
                "label_support": threshold["min_label_support"],
                "turnover_observations": threshold["min_turnover_observations"],
                "independent_evaluation_blocks": threshold[
                    "min_independent_evaluation_blocks"
                ],
                "information_match_score": 0.9 if paradigm.startswith("QLIB") else 0.8,
            }
        with tempfile.TemporaryDirectory(dir=REPO / "runtime") as directory:
            manifest = Path(directory) / "release.json"
            manifest.write_text(json.dumps({"adequacy_profiles": profiles}), encoding="utf-8")
            with patch(
                "alphafactory_crypto.frontier_v2.qualification.preflight_external_release",
                return_value={"ready": True, "failures": []},
            ):
                result = plan_new_release_activation(
                    manifest,
                    {"external_release_entry": {}},
                    config,
                )
        self.assertEqual(result["status"], "READY_FOR_NEW_DATA_ARENA")
        self.assertTrue(result["run_authorized"])
        self.assertEqual(len(result["selected_external_paradigms"]), 2)
        self.assertEqual(result["budget_action"], "FREEZE_FIXED_DEVELOPMENT_ONLY_BUDGET")
        self.assertFalse(result["boundaries"]["candidate_promotion"])


if __name__ == "__main__":
    unittest.main()
