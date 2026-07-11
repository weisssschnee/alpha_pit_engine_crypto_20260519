from __future__ import annotations

import unittest

from alphafactory_crypto.anti_collapse import AdmissionPolicy, CandidateEnvelope, admit


def candidate(i, exact=None, behaviour=None, hypothesis=None, parent=None, family=None, fresh=False):
    return CandidateEnvelope(f"c{i}", exact or f"e{i}", behaviour or f"b{i%3}", hypothesis or f"h{i%4}",
                             parent or f"p{i%5}", family or f"f{i%4}", "orthogonal_exile", i, fresh, "lineage:exile")


POLICY = AdmissionPolicy(6, 2, 2, 2, 2, 2)


class AdmissionTests(unittest.TestCase):
    def test_deterministic_and_one_exact_one_vote(self):
        rows = [candidate(i, fresh=i in {6, 7}) for i in range(8)] + [candidate(9, exact="e1")]
        left = admit(rows, POLICY)
        right = admit(reversed(rows), POLICY)
        self.assertEqual(left.decision_hash, right.decision_hash)
        self.assertEqual(len({x.exact_identity for x in left.admitted}), len(left.admitted))
        self.assertGreaterEqual(sum(x.is_fresh for x in left.admitted), 2)

    def test_cluster_exile_and_caps(self):
        policy = AdmissionPolicy(4, 1, 2, 1, 2, 0, top_cluster_exile="top")
        result = admit([candidate(0, behaviour="top"), candidate(1, parent="same"), candidate(2, parent="same")], policy)
        reasons = dict(result.rejected)
        self.assertEqual(reasons["c0"], "TOP_CLUSTER_EXILE")
        self.assertEqual(reasons["c2"], "PARENT_DESCENDANT_CAP")

    def test_memory_and_global_top_k_frozen(self):
        row = candidate(0)
        row = CandidateEnvelope(**({**row.__dict__, "memory_source": "A7MEM"}))
        with self.assertRaises(PermissionError):
            admit([row], POLICY)
        with self.assertRaises(PermissionError):
            admit([candidate(0)], AdmissionPolicy(1,1,1,1,1,0,global_top_k_baseline_enabled=True))


if __name__ == "__main__": unittest.main()
