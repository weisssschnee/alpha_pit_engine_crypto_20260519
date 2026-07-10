from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

from alphafactory_crypto.evaluation_access import (
    EvaluationAccessViolation,
    assert_candidate_feedback_columns_allowed,
    assert_epoch_candidate_feedback_allowed,
    blocked_candidate_feedback_columns,
    epoch_access,
    load_evaluation_access_policy,
)


class EvaluationAccessPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = load_evaluation_access_policy()

    def test_spent_historical_epochs_are_not_candidate_feedback(self) -> None:
        for epoch_id in (
            "validation_2025H1_selected_2025_06",
            "test_2025H2_selected_2025_12",
            "recent_oos_2026_04",
            "known_may2026_stress",
        ):
            access = epoch_access(epoch_id, self.policy)
            self.assertEqual(access.classification, "SPENT_HISTORICAL_EVALUATION")
            self.assertFalse(access.candidate_feedback_allowed)

    def test_unknown_epoch_is_sealed(self) -> None:
        access = epoch_access("unseen_forward_2026_07", self.policy)
        self.assertEqual(access.classification, "SEALED_FORWARD")
        self.assertFalse(access.candidate_feedback_allowed)

    def test_train_epoch_is_allowed_for_discovery_feedback(self) -> None:
        assert_epoch_candidate_feedback_allowed(["train_2024"], context="unit_test", policy=self.policy)

    def test_oos_and_report_only_metrics_are_blocked(self) -> None:
        blocked = blocked_candidate_feedback_columns(
            [
                "blueprint_id",
                "train_sortino",
                "validation_sortino",
                "recent_rankic",
                "min_oos_floor_sortino",
                "report_only_score",
                "gate_pass",
            ],
            self.policy,
        )
        self.assertEqual(
            blocked,
            [
                "gate_pass",
                "min_oos_floor_sortino",
                "recent_rankic",
                "report_only_score",
                "validation_sortino",
            ],
        )

    def test_candidate_feedback_guard_fails_closed(self) -> None:
        with self.assertRaises(EvaluationAccessViolation) as raised:
            assert_candidate_feedback_columns_allowed(
                ["blueprint_id", "expression", "overall_reward"],
                context="memory_ingest",
                policy=self.policy,
            )
        self.assertEqual(raised.exception.context, "memory_ingest")
        self.assertEqual(raised.exception.blocked_columns, ("overall_reward",))

    def test_current_a7eff2_accepted_pack_is_report_only(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        accepted_path = (
            repo
            / "runtime"
            / "a7eff2_git_release_20260711"
            / "a7eff2_accepted_train_validation_oos_log.csv"
        )
        with accepted_path.open("r", encoding="utf-8", newline="") as handle:
            columns = next(csv.reader(handle))
        with self.assertRaises(EvaluationAccessViolation):
            assert_candidate_feedback_columns_allowed(
                columns,
                context="current_a7eff2_candidate_feedback",
                policy=self.policy,
            )

    def test_current_a7eff2_releases_no_memory_credit(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        manifest_path = (
            repo
            / "runtime"
            / "a7eff2_git_release_20260711"
            / "a7eff2_release_manifest.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["reward_evidence"]["memory_credit_released_rows"], 0)
        self.assertFalse(manifest["boundaries"]["authorizes_alpha_proof"])


if __name__ == "__main__":
    unittest.main()
