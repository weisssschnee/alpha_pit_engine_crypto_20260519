"""Freeze the P4 mechanism-pocket validation cohort before fresh market read.

The source adaptive-broad run is formally invalid after its 30k frozen stop.
Only immutable rows at or before that stop are eligible for this development
selection.  This script reads candidate evidence only; it never opens market
data, a validation partition, an optimizer, or an Archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd


EXPERIMENT_ID = "CRYPTO_P4_MECHANISM_POCKET_FRESH_DEVELOPMENT_GATE_V1_20260811"
SOURCE_PRODUCER_SHA = "6450be52f7ff85385ac7de86e1d62819a48c1e66"
SOURCE_STOP_STRICT = 30_000
P1 = "P1_POSITION_STATE_CHANGE_TO_RESPONSE"
P4 = "P4_MULTISCALE_STATE_X_TRANSITION_ROUTING"
EVOLUTION = "temporal_program_evolution"
RANDOM = "temporal_program_random"
PROGRAM_QUOTAS = {
    "TEMPORAL_PROGRAM_V1_268DD2312788C06F66E82068DFC8E7E8": 2,
    "TEMPORAL_PROGRAM_V1_6AF37F6F0B946EC9315E5DDDB616E3F9": 2,
    "TEMPORAL_PROGRAM_V1_9643240F7F0A2749EFAC96EA55070D23": 1,
    "TEMPORAL_PROGRAM_V1_A8DD36BD5232C3BCFCA3D8F7E775BD04": 2,
    "TEMPORAL_PROGRAM_V1_CA2AEFBFD0D0242173D7920F01E95B08": 1,
    "TEMPORAL_PROGRAM_V1_FCA9F4AE903698CE9F63499FAED84B5B": 12,
}
EXPECTED_POSITIVE_PROGRAM_COUNTS = {
    "TEMPORAL_PROGRAM_V1_268DD2312788C06F66E82068DFC8E7E8": 4,
    "TEMPORAL_PROGRAM_V1_6AF37F6F0B946EC9315E5DDDB616E3F9": 4,
    "TEMPORAL_PROGRAM_V1_9643240F7F0A2749EFAC96EA55070D23": 2,
    "TEMPORAL_PROGRAM_V1_A8DD36BD5232C3BCFCA3D8F7E775BD04": 4,
    "TEMPORAL_PROGRAM_V1_CA2AEFBFD0D0242173D7920F01E95B08": 1,
    "TEMPORAL_PROGRAM_V1_FCA9F4AE903698CE9F63499FAED84B5B": 25,
}
REQUIRED_COLUMNS = {
    "completion_ordinal",
    "candidate_id",
    "candidate_spec_sha256",
    "candidate_spec_json",
    "behavior_family_id",
    "arm",
    "seed",
    "program_family_id",
    "program_id",
    "horizon_hours",
    "compile_valid",
    "exact_unique",
    "matched_control_valid",
    "strict_cost_evaluated",
    "strict_evaluated",
    "search_reward",
    "matched_positive",
    "left_incremental_net_mean",
    "right_incremental_net_mean",
    "left_incremental_net_lcb",
    "right_incremental_net_lcb",
}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def git_head(repo_root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip()


def _bool_series(frame: pd.DataFrame, name: str) -> pd.Series:
    return frame[name].fillna(False).astype(bool)


def _eligible(frame: pd.DataFrame) -> pd.DataFrame:
    required = REQUIRED_COLUMNS.difference(frame.columns)
    if required:
        raise ValueError(f"candidate ledger missing columns: {sorted(required)}")
    valid = frame.loc[
        frame["completion_ordinal"].astype(int).le(SOURCE_STOP_STRICT)
        & frame["program_family_id"].astype(str).isin({P1, P4})
        & frame["horizon_hours"].astype(int).eq(4)
        & _bool_series(frame, "compile_valid")
        & _bool_series(frame, "exact_unique")
        & _bool_series(frame, "matched_control_valid")
        & _bool_series(frame, "strict_cost_evaluated")
        & _bool_series(frame, "strict_evaluated")
    ].copy()
    if valid.empty:
        raise ValueError("no eligible pre-stop strict candidates")
    return valid


def _best_per_behavior(frame: pd.DataFrame) -> pd.DataFrame:
    ordered = frame.sort_values(
        ["search_reward", "candidate_id"], ascending=[False, True], kind="mergesort"
    )
    return ordered.drop_duplicates("behavior_family_id", keep="first")


def select_frozen_cohort(frame: pd.DataFrame) -> list[dict[str, Any]]:
    eligible = _eligible(frame)
    positive = eligible.loc[
        eligible["arm"].astype(str).eq(EVOLUTION)
        & _bool_series(eligible, "matched_positive")
    ].copy()
    positive = positive.sort_values("candidate_id", kind="mergesort")
    if len(positive) != 40 or positive["candidate_id"].nunique() != 40:
        raise ValueError("expected exactly 40 unique Evolution matched positives")
    family_counts = positive["program_family_id"].value_counts().to_dict()
    if family_counts != {P4: 32, P1: 8}:
        raise ValueError(f"unexpected positive family counts: {family_counts}")
    program_counts = positive["program_id"].value_counts().to_dict()
    if program_counts != EXPECTED_POSITIVE_PROGRAM_COUNTS:
        raise ValueError(f"unexpected positive program counts: {program_counts}")

    rows: list[tuple[str, pd.Series]] = [
        ("discovery_matched_positive", row) for _, row in positive.iterrows()
    ]
    used_behaviors = set(positive["behavior_family_id"].astype(str))
    used_candidates = set(positive["candidate_id"].astype(str))
    for arm, group in (
        (EVOLUTION, "evolution_near_miss_control"),
        (RANDOM, "random_near_miss_control"),
    ):
        for program_id, quota in sorted(PROGRAM_QUOTAS.items()):
            pool = eligible.loc[
                eligible["arm"].astype(str).eq(arm)
                & eligible["program_id"].astype(str).eq(program_id)
                & ~_bool_series(eligible, "matched_positive")
                & ~eligible["candidate_id"].astype(str).isin(used_candidates)
                & ~eligible["behavior_family_id"].astype(str).isin(used_behaviors)
            ].copy()
            pool = _best_per_behavior(pool)
            if len(pool) < quota:
                raise ValueError(
                    f"insufficient controls arm={arm} program={program_id}: "
                    f"required={quota} available={len(pool)}"
                )
            chosen = pool.head(quota)
            for _, row in chosen.iterrows():
                rows.append((group, row))
                used_candidates.add(str(row["candidate_id"]))
                used_behaviors.add(str(row["behavior_family_id"]))

    if len(rows) != 80:
        raise AssertionError(f"selection size mismatch: {len(rows)}")
    projection: list[dict[str, Any]] = []
    for selection_ordinal, (group, row) in enumerate(rows, start=1):
        candidate_spec = json.loads(str(row["candidate_spec_json"]))
        if canonical_sha256(candidate_spec) != str(row["candidate_spec_sha256"]).upper():
            raise ValueError(f"candidate spec hash mismatch: {row['candidate_id']}")
        projection.append(
            {
                "selection_ordinal": selection_ordinal,
                "selection_group": group,
                "candidate_id": str(row["candidate_id"]),
                "candidate_spec_sha256": str(row["candidate_spec_sha256"]).upper(),
                "candidate_spec": candidate_spec,
                "source_completion_ordinal": int(row["completion_ordinal"]),
                "source_arm": str(row["arm"]),
                "source_seed": int(row["seed"]),
                "program_family_id": str(row["program_family_id"]),
                "program_id": str(row["program_id"]),
                "behavior_family_id": str(row["behavior_family_id"]),
                "train_search_reward": float(row["search_reward"]),
                "train_matched_positive": bool(row["matched_positive"]),
                "train_left_incremental_net_mean": float(
                    row["left_incremental_net_mean"]
                ),
                "train_right_incremental_net_mean": float(
                    row["right_incremental_net_mean"]
                ),
                "train_left_incremental_net_lcb": float(
                    row["left_incremental_net_lcb"]
                ),
                "train_right_incremental_net_lcb": float(
                    row["right_incremental_net_lcb"]
                ),
            }
        )
    return projection


def freeze_selection(
    *,
    repo_root: Path,
    ledger_path: Path,
    stop_decision_path: Path,
    frozen_contract_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    if output_path.exists():
        raise FileExistsError(f"selection already exists: {output_path}")
    source_contract = json.loads(frozen_contract_path.read_text(encoding="utf-8"))
    source_sha = str(
        source_contract.get("source_git_sha")
        or source_contract.get("producer_source_sha")
        or source_contract.get("source_sha")
        or ""
    ).lower()
    if source_sha and source_sha != SOURCE_PRODUCER_SHA:
        raise ValueError(f"source producer mismatch: {source_sha}")
    stop_decision = json.loads(stop_decision_path.read_text(encoding="utf-8"))
    if (
        int(stop_decision.get("strict_boundary", -1)) != SOURCE_STOP_STRICT
        or stop_decision.get("status") != "STOP_ALL_ADAPTIVE_ARMS_EXITED"
    ):
        raise ValueError("source 30k stop decision mismatch")
    frame = pd.read_parquet(ledger_path)
    selected = select_frozen_cohort(frame)
    selection_projection = [
        {
            "selection_ordinal": row["selection_ordinal"],
            "selection_group": row["selection_group"],
            "candidate_id": row["candidate_id"],
            "candidate_spec_sha256": row["candidate_spec_sha256"],
            "program_family_id": row["program_family_id"],
            "program_id": row["program_id"],
            "behavior_family_id": row["behavior_family_id"],
        }
        for row in selected
    ]
    receipt: dict[str, Any] = {
        "schema_version": 1,
        "status": "SELECTION_FROZEN_BEFORE_FRESH_DEVELOPMENT_READ",
        "experiment_id": EXPERIMENT_ID,
        "selection_tool_source_sha": git_head(repo_root),
        "market_payload_read": False,
        "validation_or_oos_read": False,
        "source": {
            "producer_source_sha": SOURCE_PRODUCER_SHA,
            "runtime_status": "ENGINE_RUN_INVALID",
            "allowed_evidence_boundary": "PRE_STOP_ROWS_ONLY",
            "maximum_completion_ordinal": SOURCE_STOP_STRICT,
            "candidate_ledger_path": str(ledger_path),
            "candidate_ledger_sha256": file_sha256(ledger_path),
            "candidate_ledger_rows": int(len(frame)),
            "stop_decision_path": str(stop_decision_path),
            "stop_decision_sha256": file_sha256(stop_decision_path),
            "frozen_contract_path": str(frozen_contract_path),
            "frozen_contract_sha256": file_sha256(frozen_contract_path),
        },
        "selection_contract": {
            "candidate_count_exact": 80,
            "discovery_matched_positive_count": 40,
            "evolution_near_miss_control_count": 20,
            "random_near_miss_control_count": 20,
            "positive_program_family_counts": {P1: 8, P4: 32},
            "control_program_quota_per_arm": PROGRAM_QUOTAS,
            "control_order": "highest_train_search_reward_then_candidate_id_after_behavior_dedupe",
            "all_candidates_4h": True,
            "no_candidate_generation": True,
            "no_optimizer_archive_feedback": True,
            "raw_and_behavior_family_deoverlapped_readout_required": True,
        },
        "fresh_development_contract": {
            "role": "development_fresh_not_oos",
            "feature_warmup_start": "2026-07-18T00:00:00Z",
            "evaluation_start": "2026-08-01T00:00:00Z",
            "evaluation_end_exclusive": "2026-08-10T00:00:00Z",
            "feature_warmup_hours_maximum": 336,
            "warmup_rows_cannot_enter_labels_or_metrics": True,
            "target": "BINANCE_USDM_DELAYED_OPEN_2H_V1",
            "horizon_hours": 4,
            "mapping": "existing_candidate_mapping_unchanged",
            "cost_bps": 5.0,
            "dual_axis_matched_controls_required": True,
            "oos_holdout_recent_challenge_forward_promotion": False,
        },
        "selection_sha256": canonical_sha256(selection_projection),
        "selected_candidates": selected,
    }
    receipt["receipt_sha256"] = canonical_sha256(receipt)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    if temporary.exists():
        raise FileExistsError(f"temporary selection exists: {temporary}")
    temporary.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output_path)
    return receipt


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--stop-decision", type=Path, required=True)
    parser.add_argument("--frozen-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    result = freeze_selection(
        repo_root=arguments.repo_root.resolve(),
        ledger_path=arguments.ledger.resolve(),
        stop_decision_path=arguments.stop_decision.resolve(),
        frozen_contract_path=arguments.frozen_contract.resolve(),
        output_path=arguments.output.resolve(),
    )
    print(
        json.dumps(
            {
                "candidate_count": len(result["selected_candidates"]),
                "receipt_sha256": result["receipt_sha256"],
                "selection_sha256": result["selection_sha256"],
                "status": result["status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
