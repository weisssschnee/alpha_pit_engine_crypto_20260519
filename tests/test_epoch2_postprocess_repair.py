import pandas as pd
import pytest

from scripts.crypto_epoch2_postprocess_repair import audit_hybrid_contract, reconstruct_proposal_ids


def _frames(rows=2304):
    assignments = pd.DataFrame({
        "admission_policy": [f"p{i % 3}" for i in range(rows)],
        "panel_id": ["main" for _ in range(rows)],
        "exact_identity": [f"e{i}" for i in range(rows)],
        "proposal_id": [f"c{i}" for i in range(rows)],
    })
    strict = assignments.drop(columns="proposal_id").copy()
    strict["net_lcb"] = 0.0
    return strict, assignments


def test_reconstructs_omitted_proposal_id_without_changing_rows():
    strict, assignments = _frames()
    repaired = reconstruct_proposal_ids(strict, assignments)
    assert len(repaired) == 2304
    assert repaired.proposal_id.tolist() == assignments.proposal_id.tolist()
    assert repaired.net_lcb.eq(0.0).all()


def test_rejects_incomplete_strict_execution():
    strict, assignments = _frames(2303)
    with pytest.raises(ValueError, match="complete frozen"):
        reconstruct_proposal_ids(strict, assignments)


def test_rejects_ambiguous_identity_join():
    strict, assignments = _frames()
    assignments.loc[1, ["admission_policy", "panel_id", "exact_identity"]] = assignments.loc[0, ["admission_policy", "panel_id", "exact_identity"]]
    with pytest.raises(ValueError, match="one-to-one"):
        reconstruct_proposal_ids(strict, assignments)


def test_hybrid_audit_is_on_admitted_identity_rows_not_raw_budget_only():
    proposal_rows = []
    assignment_rows = []
    for panel, quota in {"main": 744, "bbo_micro": 24}.items():
        for ordinal in range(quota + 10):
            proposal_rows.append({"panel_id": panel, "proposal_id": f"{panel}-{ordinal}", "legal": True, "near_score": quota - ordinal, "quality": quota - ordinal})
        for ordinal in range(quota):
            assignment_rows.append({"panel_id": panel, "proposal_id": f"{panel}-{ordinal}", "admission_policy": "HYBRID_QUALITY_DIVERSITY"})
    audit = audit_hybrid_contract(pd.DataFrame(proposal_rows), pd.DataFrame(assignment_rows))
    assert audit.contract_pass.all()

    assignments = pd.DataFrame(assignment_rows)
    assignments.loc[0, "proposal_id"] = "main-750"
    audit = audit_hybrid_contract(pd.DataFrame(proposal_rows), assignments)
    assert not audit.loc[audit.panel_id == "main", "contract_pass"].iloc[0]
