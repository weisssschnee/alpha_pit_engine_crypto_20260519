from __future__ import annotations

import unittest

from alphafactory_crypto.challenger_harness import ALGORITHM_CHALLENGERS, STRATEGY_BENCHMARKS, HarnessSpec, validate_harness
from alphafactory_crypto.coverage_metrics import nextgen_coverage_report


def harnesses():
    return [HarnessSpec(name, kind, 8, 0, f"archive:{name}", True, "dark:v1", "DEVELOPMENT_ONLY_NO_FORWARD")
            for kind, names in (("strategy_benchmark", STRATEGY_BENCHMARKS), ("algorithm_challenger", ALGORITHM_CHALLENGERS))
            for name in names]


class ChallengerCoverageTests(unittest.TestCase):
    def test_complete_harness_cannot_execute(self):
        self.assertEqual(len(validate_harness(harnesses())), 17)
        bad = harnesses()
        bad[0] = HarnessSpec(**({**bad[0].__dict__, "execution_authorized": True}))
        with self.assertRaises(PermissionError): validate_harness(bad)

    def test_non_performance_coverage(self):
        rows = [
            {"field_family":"funding","primitive":"Delta","event_state":"funding","economic_hypothesis":"carry",
             "behaviour_cluster":"potential:a","grammar_cell":"funding:Delta","lineage_namespace":"l1","lane_id":"temporal"},
            {"field_family":"basis","primitive":"Slope","event_state":"basis","economic_hypothesis":"dislocation",
             "behaviour_cluster":"potential:b","grammar_cell":"basis:Slope","lineage_namespace":"l2","lane_id":"event"},
        ]
        report = nextgen_coverage_report(rows, field_families=["funding","basis"], primitives=["Delta","Slope"],
                                         event_states=["funding","basis"], hypotheses=["carry","dislocation"],
                                         behaviours=["potential:a","potential:b"], lanes=["temporal","event"])
        self.assertEqual(report["field_family_coverage"]["ratio"], 1.0)
        self.assertFalse(report["performance_fields_read"])
        self.assertGreater(report["lineage_entropy"], 0.0)


if __name__ == "__main__": unittest.main()
