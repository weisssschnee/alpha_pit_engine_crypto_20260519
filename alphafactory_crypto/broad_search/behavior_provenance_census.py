"""Source-only consumer for candidate-bound trading-behavior provenance.

The consumer never materializes expressions, reads market arrays, evaluates a
candidate, or writes optimizer feedback.  It validates and aggregates
provenance already persisted in a candidate ledger.  Ledgers without that
provenance are reported as unmeasurable rather than assigned zero stage counts.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd


CONTRACT_PATH = "config/crypto_behavior_provenance_census_v1.json"
CONTRACT_CANONICAL_SHA256 = (
    "D9C5DBCEF8F64340DFC8AD0EB8CE013B0854B5B476977FC67337035D93488864"
)
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
CONSUMER_COMPONENT_PATHS = (
    "alphafactory_crypto/broad_search/behavior_provenance_census.py",
    "alphafactory_crypto/broad_search/search_engine_v2_4.py",
    "config/crypto_behavior_provenance_census_v1.json",
    "scripts/crypto_behavior_provenance_census.py",
)
OUTPUT_SCHEMAS = {
    "candidate_behavior_provenance.parquet": (
        "candidate_id",
        "comparison_id",
        "stage_ordinal",
        "stage",
        "primary_fingerprint",
        "control_fingerprint",
        "equal",
        "mapping_family",
        "primary_label",
        "control_label",
        "arm",
        "seed",
        "skeleton_id",
        "mechanism_family",
        "horizon_hours",
        "direction_authority",
        "first_equal_stage",
    ),
    "degeneracy_stage_counts.parquet": (
        "slice_dimension",
        "slice_value",
        "first_equal_stage",
        "candidate_count",
        "slice_candidate_count",
        "candidate_rate",
    ),
    "search_policy_funnel.parquet": (
        "slice_dimension",
        "slice_value",
        "proposal_count",
        "typed_constructible_count",
        "behavior_unique_count",
        "control_non_degenerate_count",
        "strict_evaluated_count",
        "matched_positive_count",
        "qualified_candidate_count",
        "process_cpu_hours",
        "behavior_unique_per_proposal",
        "control_non_degenerate_per_proposal",
        "strict_evaluated_per_proposal",
        "matched_positive_per_proposal",
        "qualified_candidate_per_proposal",
        "behavior_unique_per_cpu_hour",
        "control_non_degenerate_per_cpu_hour",
        "strict_evaluated_per_cpu_hour",
        "matched_positive_per_cpu_hour",
    ),
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
    if hashlib.sha256(_json_bytes(contract)).hexdigest().upper() != CONTRACT_CANONICAL_SHA256:
        raise ValueError("BEHAVIOR_CENSUS_CONTRACT_CANONICAL_HASH_CHANGED")
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
    if {
        name: tuple(columns)
        for name, columns in dict(contract.get("output_schemas") or {}).items()
    } != OUTPUT_SCHEMAS:
        raise ValueError("BEHAVIOR_CENSUS_CONTRACT_CHANGED:output_schemas")
    return contract


def _git_commit_exists(repo_root: Path, source_sha: str) -> bool:
    if len(source_sha) != 40 or any(
        character not in "0123456789abcdef" for character in source_sha.lower()
    ):
        return False
    return (
        subprocess.run(
            ["git", "cat-file", "-e", f"{source_sha}^{{commit}}"],
            cwd=repo_root,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def _git_blob_sha256(repo_root: Path, source_sha: str, relative: str) -> str:
    payload = subprocess.check_output(
        ["git", "show", f"{source_sha}:{relative}"],
        cwd=repo_root,
    )
    return hashlib.sha256(payload).hexdigest().upper()


def _verify_consumer_components(repo_root: Path) -> tuple[str, dict[str, str]]:
    source_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
    ).strip().lower()
    blobs: dict[str, str] = {}
    for relative in CONSUMER_COMPONENT_PATHS:
        committed = _git_blob_sha256(repo_root, source_sha, relative)
        if subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=repo_root,
            check=False,
        ).returncode != 0:
            raise ValueError(f"CONSUMER_COMPONENT_NOT_COMMITTED:{relative}")
        blobs[relative] = committed
    return source_sha, blobs


def _validate_source_manifest(
    repo_root: Path,
    *,
    ledger_path: Path,
    source_manifest_path: Path,
    ledger_row_count: int,
) -> dict[str, Any]:
    manifest_path = Path(source_manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files")
    if not isinstance(files, list) or (
        hashlib.sha256(_json_bytes(files)).hexdigest().upper()
        != str(manifest.get("artifact_bundle_sha256") or "")
    ):
        raise ValueError("SOURCE_MANIFEST_ARTIFACT_BUNDLE_CHANGED")
    ledger_records = [
        item
        for item in files
        if isinstance(item, Mapping)
        and str(item.get("path") or "") == "candidate_ledger.parquet"
    ]
    if len(ledger_records) != 1:
        raise ValueError("SOURCE_MANIFEST_LEDGER_RECORD_CHANGED")
    record = dict(ledger_records[0])
    expected_ledger = (manifest_path.parent / str(record["path"])).resolve()
    observed_ledger = Path(ledger_path).resolve()
    if expected_ledger != observed_ledger:
        raise ValueError("SOURCE_MANIFEST_LEDGER_PATH_CHANGED")
    if (
        int(record.get("bytes", -1)) != observed_ledger.stat().st_size
        or str(record.get("sha256") or "") != _file_sha256(observed_ledger)
        or int(manifest.get("source_candidate_count", -1)) != ledger_row_count
    ):
        raise ValueError("SOURCE_MANIFEST_LEDGER_IDENTITY_CHANGED")
    for key in ("producer_source_sha", "finalizer_source_sha"):
        if not _git_commit_exists(repo_root, str(manifest.get(key) or "")):
            raise ValueError(f"SOURCE_MANIFEST_COMMIT_INVALID:{key}")
    try:
        portable_manifest_path = manifest_path.relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        portable_manifest_path = str(manifest_path)
    return {
        "source_manifest_path": portable_manifest_path,
        "source_manifest_sha256": _file_sha256(manifest_path),
        "producer_source_sha": str(manifest["producer_source_sha"]),
        "finalizer_source_sha": str(manifest["finalizer_source_sha"]),
        "candidate_ledger_sha256": str(record["sha256"]),
        "candidate_ledger_row_count": ledger_row_count,
        "verification_status": "VERIFIED_MANIFEST_BOUND_INPUT",
    }


def verify_authoritative_legacy_v24(repo_root: Path) -> dict[str, Any]:
    root = Path(repo_root)
    contract = load_behavior_provenance_census_contract(root)
    authority = dict(contract.get("legacy_authority") or {})
    ledger_path = root / str(authority.get("candidate_ledger_path") or "")
    manifest_path = root / str(authority.get("source_manifest_path") or "")
    if (
        not ledger_path.is_file()
        or _file_sha256(ledger_path)
        != str(authority.get("candidate_ledger_sha256") or "")
        or not manifest_path.is_file()
        or _file_sha256(manifest_path)
        != str(authority.get("source_manifest_sha256") or "")
    ):
        raise ValueError("LEGACY_V24_AUTHORITY_IDENTITY_CHANGED")
    ledger = pd.read_parquet(ledger_path)
    if len(ledger) != int(authority.get("candidate_ledger_row_count", -1)):
        raise ValueError("LEGACY_V24_AUTHORITY_ROW_COUNT_CHANGED")
    source = _validate_source_manifest(
        root,
        ledger_path=ledger_path,
        source_manifest_path=manifest_path,
        ledger_row_count=len(ledger),
    )
    if (
        source["producer_source_sha"] != authority.get("producer_source_sha")
        or source["finalizer_source_sha"] != authority.get("finalizer_source_sha")
    ):
        raise ValueError("LEGACY_V24_AUTHORITY_SOURCE_CHANGED")
    summary = build_behavior_provenance_census(ledger)["summary"]
    if summary != authority.get("expected_result"):
        raise ValueError("LEGACY_V24_AUTHORITY_RESULT_CHANGED")
    return summary


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
        or tuple(order[-3:])
        != ("CAPPED_WEIGHT", "MAPPED_WEIGHT", "EXECUTABLE_WEIGHT")
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
        hierarchical_legacy = binary | {"ab_vs_interaction_left_control"}
        hierarchical_complete = hierarchical_legacy | {
            "ab_vs_interaction_right_control"
        }
        if comparison_ids not in (
            binary,
            hierarchical_legacy,
            hierarchical_complete,
        ):
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


def _qualified_mask(local: pd.DataFrame) -> pd.Series | None:
    if "qualified_candidate" not in local.columns:
        return None
    values = local["qualified_candidate"].tolist()
    if all(_is_missing(value) for value in values):
        return None
    if not all(_is_bool(value) for value in values):
        raise ValueError("QUALIFIED_CANDIDATE_PARTIAL_OR_INVALID")
    return local["qualified_candidate"].astype(bool)


def _funnel_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dimension, value, local in _slice_frames(frame):
        cpu_seconds = float(local["process_cpu_seconds"].astype(float).sum())
        cpu_hours = cpu_seconds / 3600.0
        typed_mask = local["typed_constructible"].astype(bool)
        behavior_mask = typed_mask & local["behavior_unique"].astype(bool)
        nondegenerate_mask = behavior_mask & (
            local["first_equal_stage"] == "NON_DEGENERATE"
        )
        strict_mask = nondegenerate_mask & local["strict_evaluated"].astype(bool)
        positive_mask = strict_mask & local["matched_positive"].astype(bool)
        raw_qualified = _qualified_mask(local)
        qualified_mask = (
            positive_mask & raw_qualified
            if raw_qualified is not None
            else None
        )
        typed = int(typed_mask.sum())
        unique = int(behavior_mask.sum())
        nondegenerate = int(nondegenerate_mask.sum())
        strict = int(strict_mask.sum())
        positive = int(positive_mask.sum())
        qualified = (
            int(qualified_mask.sum()) if qualified_mask is not None else None
        )
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
            "candidate_provenance": pd.DataFrame(
                columns=OUTPUT_SCHEMAS[
                    "candidate_behavior_provenance.parquet"
                ]
            ),
            "stage_counts": pd.DataFrame(
                columns=OUTPUT_SCHEMAS["degeneracy_stage_counts.parquet"]
            ),
            "funnel": pd.DataFrame(
                columns=OUTPUT_SCHEMAS["search_policy_funnel.parquet"]
            ),
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
        "behavior_unique",
        "behavior_unique_scope",
        "strict_evaluated",
        "matched_positive",
        "process_cpu_seconds",
        "control_degeneracy_provenance_sha256",
        "validation_status",
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
        "behavior_unique_scope",
    )
    for column in identity_columns:
        if any(_is_missing(value) for value in frame[column].tolist()):
            raise ValueError(f"PROVENANCE_LEDGER_IDENTITY_MISSING:{column}")
    if set(frame["behavior_unique_scope"].astype(str)) != {
        "ARM_SEED_HORIZON_BEHAVIOR_FAMILY"
    }:
        raise ValueError("BEHAVIOR_UNIQUE_SCOPE_CHANGED")
    for column in (
        "typed_constructible",
        "behavior_unique",
        "strict_evaluated",
        "matched_positive",
    ):
        if not all(_is_bool(value) for value in frame[column].tolist()):
            raise ValueError(f"PROVENANCE_LEDGER_BOOLEAN_INVALID:{column}")
    cpu_seconds = frame["process_cpu_seconds"].astype(float)
    if not np.isfinite(cpu_seconds).all() or bool((cpu_seconds < 0).any()):
        raise ValueError("PROVENANCE_LEDGER_CPU_INVALID")
    unique_rows = frame.loc[frame["behavior_unique"].astype(bool)]
    if unique_rows.duplicated(
        ["arm", "seed", "horizon_hours", "behavior_family_id"]
    ).any():
        raise ValueError("BEHAVIOR_UNIQUE_SCOPE_DUPLICATED")

    candidate_rows: list[dict[str, Any]] = []
    stage_rows: list[dict[str, Any]] = []
    for record in frame.to_dict("records"):
        classification, comparisons = _parse_bound_provenance(record)
        if any(
            str(item["mapping_family"]) != str(record["mapping_family"])
            for item in comparisons
        ):
            raise ValueError("PROVENANCE_MAPPING_FAMILY_CHANGED")
        strict = bool(record["strict_evaluated"])
        positive = bool(record["matched_positive"])
        failure_reason = record.get("validation_failure_reason")
        status = str(record["validation_status"])
        if classification == "NON_DEGENERATE":
            consistent = (
                strict
                and _is_missing(failure_reason)
                and status == "EVALUATED"
            )
        else:
            consistent = (
                not strict
                and not positive
                and str(failure_reason or "") in BEHAVIOR_FAILURES
                and status == "CANDIDATE_LOCAL_FAILURE"
            )
        if not consistent or (positive and not strict):
            raise ValueError("PROVENANCE_LEDGER_STATE_INCONSISTENT")
        if (
            record.get("qualified_candidate") is True
            and not positive
        ):
            raise ValueError("QUALIFIED_CANDIDATE_NOT_POSITIVE")
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
        "candidate_provenance": pd.DataFrame(stage_rows).reindex(
            columns=OUTPUT_SCHEMAS["candidate_behavior_provenance.parquet"]
        ),
        "stage_counts": pd.DataFrame(stage_counts).reindex(
            columns=OUTPUT_SCHEMAS["degeneracy_stage_counts.parquet"]
        ),
        "funnel": pd.DataFrame(_funnel_rows(candidates)).reindex(
            columns=OUTPUT_SCHEMAS["search_policy_funnel.parquet"]
        ),
    }


def write_behavior_provenance_census(
    repo_root: Path,
    *,
    ledger_path: Path,
    output_root: Path,
    source_manifest_path: Path,
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
    ledger = pd.read_parquet(source)
    result = build_behavior_provenance_census(ledger)
    input_authority = _validate_source_manifest(
        root,
        ledger_path=source,
        source_manifest_path=Path(source_manifest_path),
        ledger_row_count=len(ledger),
    )
    source_sha, component_blobs = _verify_consumer_components(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.", dir=output.parent)
    )
    try:
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
            frame = result[key]
            expected_columns = list(contract["output_schemas"][name])
            if list(frame.columns) != expected_columns:
                raise ValueError(f"CENSUS_OUTPUT_SCHEMA_CHANGED:{name}")
            frame.to_parquet(temporary / name, index=False)
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
            "consumer_component_blobs": component_blobs,
            "input_authority": input_authority,
            "status": result["summary"]["status"],
            "artifacts": artifacts,
            "artifact_bundle_sha256": hashlib.sha256(
                _json_bytes(artifacts)
            ).hexdigest().upper(),
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
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


__all__ = [
    "build_behavior_provenance_census",
    "load_behavior_provenance_census_contract",
    "verify_authoritative_legacy_v24",
    "write_behavior_provenance_census",
]
