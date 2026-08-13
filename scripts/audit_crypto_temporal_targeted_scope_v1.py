from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import pandas as pd


ACTIVE_FAMILIES = {
    "P1_POSITION_STATE_CHANGE_TO_RESPONSE",
    "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--producer-source-sha", required=True)
    args = parser.parse_args()

    ledger = pd.read_parquet(args.ledger)
    ordinals = ledger["completion_ordinal"].astype(int).tolist()
    family_counts = Counter(ledger["program_family_id"].astype(str))
    out_of_scope_mask = ~ledger["program_family_id"].astype(str).isin(
        ACTIVE_FAMILIES
    )
    out_of_scope_rows = ledger.loc[out_of_scope_mask]
    out_of_scope = {
        family: count
        for family, count in sorted(family_counts.items())
        if family not in ACTIVE_FAMILIES
    }
    result = {
        "schema_version": 1,
        "status": "FAIL" if out_of_scope else "PASS",
        "finding": (
            "TARGETED_PROGRAM_FAMILY_SCOPE_VIOLATION"
            if out_of_scope
            else "TARGETED_PROGRAM_FAMILY_SCOPE_CONFIRMED"
        ),
        "next_decision": "SYSTEM_INVALID" if out_of_scope else None,
        "runtime_id": args.runtime_id,
        "task_id": args.task_id,
        "producer_source_sha": args.producer_source_sha,
        "ledger_path": args.ledger.as_posix(),
        "ledger_sha256": _sha256(args.ledger),
        "strict_rows_audited": len(ledger),
        "completion_ordinals_contiguous": ordinals
        == list(range(1, len(ledger) + 1)),
        "active_families": sorted(ACTIVE_FAMILIES),
        "program_family_counts": dict(sorted(family_counts.items())),
        "out_of_scope_family_counts": out_of_scope,
        "out_of_scope_strict_rows": sum(out_of_scope.values()),
        "out_of_scope_arm_counts": dict(
            sorted(Counter(out_of_scope_rows["arm"].astype(str)).items())
        ),
        "out_of_scope_policy_key_counts": (
            dict(
                sorted(
                    Counter(out_of_scope_rows["policy_key"].astype(str)).items()
                )
            )
            if "policy_key" in out_of_scope_rows.columns
            else "NOT_AVAILABLE"
        ),
        "out_of_scope_operation_counts": dict(
            sorted(Counter(out_of_scope_rows["operation"].astype(str)).items())
        ),
        "market_arrays_read_by_audit": 0,
        "candidate_evaluations_by_audit": 0,
        "validation_reads": 0,
        "oos_reads": 0,
        "sealed_reads": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
    return int(bool(out_of_scope))


if __name__ == "__main__":
    raise SystemExit(main())
