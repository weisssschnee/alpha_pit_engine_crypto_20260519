from __future__ import annotations

import unittest

from alphafactory_crypto.nextgen_lanes import CandidateContract, LANE_IDS, LaneSpec, lane_registry_hash, validate_lanes


def lanes():
    return [LaneSpec(lane, f"root:{lane}", 8, 2, f"archive:{lane}", f"lineage:{lane}", 100 + i,
                     CandidateContract("dark:v1"), new_economic_hypothesis_first_class=lane == "orthogonal_exile")
            for i, lane in enumerate(LANE_IDS)]


class LaneTests(unittest.TestCase):
    def test_complete_registry_is_isolated_and_deterministic(self):
        self.assertEqual(lane_registry_hash(lanes()), lane_registry_hash(reversed(lanes())))
        self.assertEqual(len(validate_lanes(lanes())), 7)

    def test_shared_namespace_and_memory_fail_closed(self):
        values = lanes()
        values[1] = LaneSpec(values[1].lane_id, "root", 8, 2, values[0].archive_namespace, "other", 999,
                             CandidateContract("dark:v1"))
        with self.assertRaises(ValueError):
            validate_lanes(values)
        values = lanes()
        values[0] = LaneSpec(values[0].lane_id, "root", 8, 2, "a", "l", 999,
                             CandidateContract("dark:v1"), memory_policy="A7MEM")
        with self.assertRaises(PermissionError):
            validate_lanes(values)


if __name__ == "__main__": unittest.main()
