"""Source-only consumer for candidate-bound trading-behavior provenance.

The consumer never materializes expressions, reads market arrays, evaluates a
candidate, or writes optimizer feedback.  It validates and aggregates
provenance already persisted in a candidate ledger.  Ledgers without that
provenance are reported as unmeasurable rather than assigned zero stage counts.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd


CONTRACT_PATH = "config/crypto_behavior_provenance_census_v1.json"
BOUND_SCHEMA = "CRYPTO_V24_BOUND_CONTROL_PROVENANCE_V1"
PAIR_SCHEMA = "CRYPTO_PAIR_CONTROL_PROVENANCE_V1"
COMPARISON_SCHEMA = "CRYPTO_CONTROL_DEGENERACY_PROVENANCE_V1"
BEHAVIOR_FAILURES = {
    "CONTROL_BEHAVIOR_EQUALS_PRIMARY",
    "RIGHT_AXIS_CONTROL_BEHAVIOR_EQUALS_PRIMARY",
    "INTERACTION_LEFT_CONTROL_BEHAVIOR_EQUALS_AB",
}
STAGE_ORDER = (
    "SIGNAL",
    "ORIENTED_SIGNAL",
    "RANK",
    "NORMALIZED_SCORE",
    "SELECTION",
    "RAW_WEIGHT",
    "CAPPED_WEIGHT",
    "MAPPED_WEIGHT",
    "EXECUTABLE_WEIGHT",
)
SLICE_COLUMNS = {
    "arm": "arm",
    "seed": "seed",
    "skeleton": "skeleton_id",
    "mechanism_family": "mechanism_family",
    "mapping_family": "mapping_family",
    "horizon": "horizon_hours",
    "direction_authority": "direction_authority",
}


def _json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    payload = {key: item for key, item in value.items() if key != "provenance_sha256"}
    return hashlib.sha256(_json_bytes(payload)).hexdigest().upper()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _is_bool(value: Any) -> bool:
    return type(value) is bool or type(value) is np.bool_


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def load_behavior_provenance_census_contract(
    repo_root: Path,
) -> dict[str, Any]:
    path = Path(repo_root) / CONTRACT_PATH
    contract = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version": 1,
        "consumer_id": "CRYPTO_BEHAVIOR_PROVENANCE_CENSUS_V1",
        "status": "SOURCE_ONLY_OBSERVABILITY_INFRASTRUCTURE",
        "historical_inference_allowed": False,
        "market_read_allowed": False,
        "candidate_replay_allowed": False,
        "reward_or_policy_feedback_allowed": False,
        "exclusive_counting_key": "first_equal_stage",
    }
    for key, expected in required.items():
        if contract.get(key) != expected:
            raise ValueError(f"BEHAVIOR_CENSUS_CONTRACT_CHANGED:{key}")
    if tuple(contract.get("allowed_stages") or ()) != STAGE_ORDER:
        raise ValueError("BEHAVIOR_CENSUS_CONTRACT_CHANGED:allowed_stages")
    if dict(contract.get("slice_columns") or {}) != SLICE_COLUMNS:
        raise ValueError("BEHAVIOR_CENSUS_CONTRACT_CHANGED:slice_columns")
    return contract


def _verify_comparison(
    payload: Mapping[str, Any],
    *,
    candidate_id: str,
    comparison_id: str,
) -> tuple[str | None, list[dict[str, Any]]]:
    raw = dict(payload)
    if raw.get("schema_version") != COMPARISON_SCHEMA:
        raise ValueError("CONTROL_COMPARISON_SCHEMA_CHANGED")
    if _canonical_sha256(raw) != str(raw.get("provenance_sha256") or ""):
        raise ValueError("CONTROL_COMPARISON_HASH_CHANGED")
    order = list(raw.get("stage_order") or [])
    positions = [STAGE_ORDER.index(stage) for stage in order if stage in STAGE_ORDER]
    if (
        not order
        or len(order) != len(set(order))
        or set(order) - set(STAGE_ORDER)
        or positions != sorted(positions)
    ):
        raise ValueError("CONTROL_COMPARISON_STAGE_ORDER_INVALID")
    stages = dict(raw.get("stages") or {})
    if set(stages) != set(order):
        raise ValueError("CONTROL_COMPARISON_STAGE_SET_CHANGED")
    rows: list[dict[str, Any]] = []
    equal_flags: list[bool] = []
    for ordinal, stage in enumerate(order):
        item = dict(stages[stage])
        if not _is_bool(item.get("equal")):
            raise ValueError("CONTROL_COMPARISON_EQUALITY_INVALID")
        primary = str(item.get("primary_identity_sha256") or "")
        control = str(item.get("control_identity_sha256") or "")
        if (
            len(primary) != 64
            or len(control) != 64
            or any(character not in "0123456789ABCDEF" for character in primary)
            or any(character not in "0123456789ABCDEF" for character in control)
        ):
            raise ValueError("CONTROL_COMPARISON_FINGERPRINT_INVALID")
        equal = bool(item["equal"])
        if equal != (primary == control):
            raise ValueError("CONTROL_COMPARISON_FINGERPRINT_EQUALITY_CHANGED")
        equal_flags.append(equal)
        rows.append(
            {
                "candidate_id": candidate_id,
                "comparison_id": comparison_id,
                "stage_ordinal": ordinal,
                "stage": stage,
                "primary_fingerprint": primary,
                "control_fingerprint": control,
                "equal": equal,
                "mapping_family": str(raw.get("mapping_id") or ""),
                "primary_label": str(raw.get("primary_label") or ""),
                "control_label": str(raw.get("control_label") or ""),
            }
        )
    stable_first = next(
        (
            order[index]
            for index in range(len(order))
            if all(equal_flags[index:])
        ),
        None,
    )
    declared_first = raw.get("first_equal_stage")
    if declared_first != stable_first:
        raise ValueError("CONTROL_COMPARISON_FIRST_EQUAL_STAGE_CHANGED")
    if type(raw.get("final_weight_equal")) is not bool:
        raise ValueError("CONTROL_COMPARISON_FINAL_EQUALITY_INVALID")
    if bool(raw["final_weight_equal"]) != bool(equal_flags[-1]):
        raise ValueError("CONTROL_COMPARISON_FINAL_EQUALITY_CHANGED")
    return stable_first, rows


def _parse_bound_provenance(
    row: Mapping[str, Any],
) -> tuple[str, list[dict[str, Any]]]:
    try:
        envelope = json.loads(str(row["control_degeneracy_provenance_json"]))
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("BOUND_PROVENANCE_JSON_INVALID") from exc
    if not isinstance(envelope, dict) or envelope.get("schema_version") != BOUND_SCHEMA:
        raise ValueError("BOUND_PROVENANCE_SCHEMA_CHANGED")
    candidate_id = str(row["candidate_id"])
    if (
        str(envelope.get("candidate_id") or "") != candidate_id
        or str(envelope.get("candidate_spec_sha256") or "")
        != str(row["candidate_spec_sha256"])
    ):
        raise ValueError("BOUND_PROVENANCE_CANDIDATE_BINDING_CHANGED")
    observed_hash = str(envelope.get("provenance_sha256") or "")
    if (
        _canonical_sha256(envelope) != observed_hash
        or observed_hash
        != str(row.get("control_degeneracy_provenance_sha256") or "")
    ):
        raise ValueError("BOUND_PROVENANCE_HASH_CHANGED")
    inner = envelope.get("provenance")
    if not isinstance(inner, Mapping):
        raise ValueError("BOUND_PROVENANCE_PAYLOAD_MISSING")
    failure_reason = envelope.get("failure_reason")
    comparison_rows: list[dict[str, Any]] = []
    if inner.get("schema_version") == PAIR_SCHEMA:
        if failure_reason is not None:
            raise ValueError("PAIR_PROVENANCE_FAILURE_BINDING_CHANGED")
        if _canonical_sha256(inner) != str(inner.get("provenance_sha256") or ""):
            raise ValueError("PAIR_PROVENANCE_HASH_CHANGED")
        comparisons = inner.get("comparisons")
        if not isinstance(comparisons, Mapping) or not comparisons:
            raise ValueError("PAIR_PROVENANCE_COMPARISONS_MISSING")
        comparison_ids = set(comparisons)
        binary = {"primary_vs_left_control", "primary_vs_right_control"}
        hierarchical = binary | {"ab_vs_interaction_left_control"}
        if comparison_ids not in (binary, hierarchical):
            raise ValueError("PAIR_PROVENANCE_COMPARISON_SET_CHANGED")
        for comparison_id, comparison in sorted(comparisons.items()):
            if not isinstance(comparison, Mapping):
                raise ValueError("PAIR_PROVENANCE_COMPARISON_INVALID")
            first, rows = _verify_comparison(
                comparison,
                candidate_id=candidate_id,
                comparison_id=str(comparison_id),
            )
            if first is not None:
                raise ValueError("EVALUATED_PAIR_CONTAINS_DEGENERATE_CONTROL")
            comparison_rows.extend(rows)
        classification = "NON_DEGENERATE"
    else:
        if str(failure_reason or "") not in BEHAVIOR_FAILURES:
            raise ValueError("FAILURE_PROVENANCE_REASON_CHANGED")
        if str(row.get("validation_failure_reason") or "") != str(failure_reason):
            raise ValueError("FAILURE_PROVENANCE_LEDGER_REASON_CHANGED")
        first, comparison_rows = _verify_comparison(
            inner,
            candidate_id=candidate_id,
            comparison_id="failing_control",
        )
        if first is None:
            raise ValueError("FAILURE_PROVENANCE_FIRST_EQUAL_STAGE_MISSING")
        classification = first
    return classification, comparison_rows


def _slice_frames(frame: pd.DataFrame) -> list[tuple[str, str, pd.DataFrame]]:
    slices: list[tuple[str, str, pd.DataFrame]] = [("overall", "ALL", frame)]
    for dimension, column in SLICE_COLUMNS.items():
        for value, local in frame.groupby(column, dropna=False, sort=True):
            rendered = "NOT_RECORDED" if _is_missing(value) else str(value)
            slices.append((dimension, rendered, local))
    return slices


def _qualified_count(local: pd.DataFrame) -> int | None:
    if "qualified_candidate" not in local.columns:
        return None
    values = local["qualified_candidate"].tolist()
    if all(_is_missing(value) for value in values):
        return None
    if not all(_is_bool(value) for value in values):
        raise ValueError("QUALIFIED_CANDIDATE_PARTIAL_OR_INVALID")
    return int(sum(bool(value) for value in values))


def _funnel_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dimension, value, local in _slice_frames(frame):
        cpu_seconds = float(local["process_cpu_seconds"].astype(float).sum())
        cpu_hours = cpu_seconds / 3600.0
        typed = int(local["typed_constructible"].astype(bool).sum())
        unique = int(local.loc[local["typed_constructible"].astype(bool), "behavior_family_id"].nunique())
        nondegenerate = int((local["first_equal_stage"] == "NON_DEGENERATE").sum())
        strict = int(local["strict_evaluated"].astype(bool).sum())
        positive = int(local["matched_positive"].astype(bool).sum())
        qualified = _qualified_count(local)
        rows.append(
            {
                "slice_dimension": dimension,
                "slice_value": value,
                "proposal_count": int(len(local)),
                "typed_constructible_count": typed,
                "behavior_unique_count": unique,
                "control_non_degenerate_count": nondegenerate,
                "strict_evaluated_count": strict,
                "matched_positive_count": positive,
                "qualified_candidate_count": qualified,
                "process_cpu_hours": cpu_hours,
                "behavior_unique_per_proposal": unique / len(local),
                "control_non_degenerate_per_proposal": nondegenerate / len(local),
                "strict_evaluated_per_proposal": strict / len(local),
                "matched_positive_per_proposal": positive / len(local),
                "qualified_candidate_per_proposal": (
                    qualified / len(local) if qualified is not None else None
                ),
                "behavior_unique_per_cpu_hour": (
                    unique / cpu_hours if cpu_hours > 0 else None
                ),
                "control_non_degenerate_per_cpu_hour": (
                    nondegenerate / cpu_hours if cpu_hours > 0 else None
                ),
                "strict_evaluated_per_cpu_hour": (
                    strict / cpu_hours if cpu_hours > 0 else None
                ),
                "matched_positive_per_cpu_hour": (
                    positive / cpu_hours if cpu_hours > 0 else None
                ),
            }
        )
    return rows


def build_behavior_provenance_census(
    ledger: pd.DataFrame,
) -> dict[str, Any]:
    """Validate and aggregate already-persisted behavior provenance."""

    frame = ledger.copy()
    if "candidate_id" not in frame or frame["candidate_id"].astype(str).duplicated().any():
        raise ValueError("CANDIDATE_ID_MISSING_OR_DUPLICATED")
    provenance_column = (
        frame["control_degeneracy_provenance_json"]
        if "control_degeneracy_provenance_json" in frame
        else pd.Series([None] * len(frame), index=frame.index, dtype=object)
    )
    present = ~provenance_column.map(_is_missing)
    if not bool(present.any()):
        failures = (
            frame["validation_failure_reason"].astype(str)
            if "validation_failure_reason" in frame
            else pd.Series([], dtype=str)
        )
        return {
            "summary": {
                "status": "NO_PROVENANCE_ROWS",
                "legacy_final_equal_count": int(failures.isin(BEHAVIOR_FAILURES).sum()),
                "first_equal_stage": None,
            },
            "candidate_provenance": pd.DataFrame(),
            "stage_counts": pd.DataFrame(),
            "funnel": pd.DataFrame(),
        }
    if not bool(present.all()):
        raise ValueError("PARTIAL_PROVENANCE_ROWS")
    required = {
        "candidate_spec_sha256",
        "behavior_family_id",
        "arm",
        "seed",
        "skeleton_id",
        "mechanism_family",
        "mapping_family",
        "horizon_hours",
        "direction_authority",
        "typed_constructible",
        "strict_evaluated",
        "matched_positive",
        "process_cpu_seconds",
        "control_degeneracy_provenance_sha256",
        "validation_failure_reason",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"PROVENANCE_LEDGER_SCHEMA_MISSING:{','.join(missing)}")
    identity_columns = (
        "candidate_spec_sha256",
        "behavior_family_id",
        "arm",
        "skeleton_id",
        "mechanism_family",
        "mapping_family",
        "direction_authority",
    )
    for column in identity_columns:
        if any(_is_missing(value) for value in frame[column].tolist()):
            raise ValueError(f"PROVENANCE_LEDGER_IDENTITY_MISSING:{column}")
    for column in ("typed_constructible", "strict_evaluated", "matched_positive"):
        if not all(_is_bool(value) for value in frame[column].tolist()):
            raise ValueError(f"PROVENANCE_LEDGER_BOOLEAN_INVALID:{column}")
    cpu_seconds = frame["process_cpu_seconds"].astype(float)
    if not np.isfinite(cpu_seconds).all() or bool((cpu_seconds < 0).any()):
        raise ValueError("PROVENANCE_LEDGER_CPU_INVALID")

    candidate_rows: list[dict[str, Any]] = []
    stage_rows: list[dict[str, Any]] = []
    for record in frame.to_dict("records"):
        classification, comparisons = _parse_bound_provenance(record)
        if any(
            str(item["mapping_family"]) != str(record["mapping_family"])
            for item in comparisons
        ):
            raise ValueError("PROVENANCE_MAPPING_FAMILY_CHANGED")
        candidate_rows.append(
            {
                **record,
                "first_equal_stage": classification,
            }
        )
        dimensions = {
            "arm": str(record["arm"]),
            "seed": int(record["seed"]),
            "skeleton_id": str(record["skeleton_id"]),
            "mechanism_family": str(record["mechanism_family"]),
            "mapping_family": str(record["mapping_family"]),
            "horizon_hours": int(record["horizon_hours"]),
            "direction_authority": str(record["direction_authority"]),
            "first_equal_stage": classification,
        }
        stage_rows.extend({**item, **dimensions} for item in comparisons)
    candidates = pd.DataFrame(candidate_rows)

    stage_counts: list[dict[str, Any]] = []
    for dimension, value, local in _slice_frames(candidates):
        for stage, count in local["first_equal_stage"].value_counts().sort_index().items():
            stage_counts.append(
                {
                    "slice_dimension": dimension,
                    "slice_value": value,
                    "first_equal_stage": str(stage),
                    "candidate_count": int(count),
                    "slice_candidate_count": int(len(local)),
                    "candidate_rate": float(count / len(local)),
                }
            )
    counts = candidates["first_equal_stage"].value_counts().sort_index()
    return {
        "summary": {
            "status": "PASS_BEHAVIOR_PROVENANCE_CENSUS",
            "candidate_count": int(len(candidates)),
            "provenance_candidate_count": int(len(candidates)),
            "first_equal_stage_counts": {
                str(key): int(value) for key, value in counts.items()
            },
            "historical_inference_performed": False,
            "market_read_performed": False,
            "candidate_replay_performed": False,
            "reward_or_policy_feedback_written": False,
        },
        "candidate_provenance": pd.DataFrame(stage_rows),
        "stage_counts": pd.DataFrame(stage_counts),
        "funnel": pd.DataFrame(_funnel_rows(candidates)),
    }


def write_behavior_provenance_census(
    repo_root: Path,
    *,
    ledger_path: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Consume one ledger and atomically write an observability-only bundle."""

    root = Path(repo_root)
    contract = load_behavior_provenance_census_contract(root)
    source = Path(ledger_path)
    if not source.is_file():
        raise FileNotFoundError(source)
    output = Path(output_root)
    if output.exists():
        raise FileExistsError(output)
    result = build_behavior_provenance_census(pd.read_parquet(source))
    temporary = output.with_name(f".{output.name}.tmp")
    if temporary.exists():
        raise FileExistsError(temporary)
    temporary.mkdir(parents=True)
    (temporary / "frozen_contract.json").write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (temporary / "census_summary.json").write_text(
        json.dumps(result["summary"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    for name, key in (
        ("candidate_behavior_provenance.parquet", "candidate_provenance"),
        ("degeneracy_stage_counts.parquet", "stage_counts"),
        ("search_policy_funnel.parquet", "funnel"),
    ):
        result[key].to_parquet(temporary / name, index=False)
    source_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()
    artifacts = []
    for path in sorted(temporary.iterdir()):
        artifacts.append(
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
        )
    manifest = {
        "schema_version": 1,
        "consumer_id": contract["consumer_id"],
        "source_sha": source_sha,
        "source_ledger_path": str(source),
        "source_ledger_sha256": _file_sha256(source),
        "status": result["summary"]["status"],
        "artifacts": artifacts,
        "artifact_bundle_sha256": hashlib.sha256(_json_bytes(artifacts)).hexdigest().upper(),
        "market_read_performed": False,
        "candidate_replay_performed": False,
        "reward_or_policy_feedback_written": False,
    }
    (temporary / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(output)
    return {"summary": result["summary"], "manifest": manifest}


__all__ = [
    "build_behavior_provenance_census",
    "load_behavior_provenance_census_contract",
    "write_behavior_provenance_census",
]
