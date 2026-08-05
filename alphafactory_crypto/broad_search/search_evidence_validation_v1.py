"""One-shot no-feedback validation for the final Evidence V1.1 champions.

This adapter deliberately reuses the existing typed compiler, Binance target,
portfolio mapping, pair evaluator, and V2.4 process worker/path projection.  It
does not generate candidates or write optimizer/archive state.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from alphafactory_crypto.broad_search.search_engine_v1 import (
    _evaluation_audit_fields,
    _search_ordering_reward,
)
from alphafactory_crypto.broad_search.search_engine_v2_4 import (
    _v24_checkpoint_files,
    _v24_worker_evaluate,
    _v24_worker_initialize,
    _v24_write_batch_projections,
    sweep_v24_static_constructibility,
)


RECEIPT_PATH = "config/crypto_search_evidence_v1_1_validation_receipt.json"
RUNTIME_PREFIX = "crypto_search_evidence_v1_1_validation"
DEFAULT_RUNTIME_DATE = "20260805"
EXPECTED_SELECTION_SHA256 = (
    "C3BD1C0D0940BEE2FAE41B51BD94D11B3684CD93B4E9AD84D125AEC0D5A746DE"
)
CONSENSUS_RECEIPT_PATH = (
    "config/crypto_search_family_consensus_dev_v1_receipt.json"
)
CONSENSUS_RUNTIME_PREFIX = "crypto_search_family_consensus_dev_v1"
CONSENSUS_DEFAULT_RUNTIME_DATE = "20260805"
CONSENSUS_MAIN_CANDIDATE_IDS_SHA256 = (
    "EAB230F56C938295BA8D74570A66FEF18E64A2FD88E9341C22B7B2E79268D1E7"
)
CONSENSUS_OTHER_CANDIDATE_IDS_SHA256 = (
    "06707EF9D18B347295B78CE1975F51C0E73F515A1752D880128D6EE0326A0D04"
)


def _canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest().upper()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def load_validation_receipt(
    repo_root: Path,
    *,
    require_authorized: bool | None = None,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    path = Path(repo_root) / str(receipt_path)
    receipt = json.loads(path.read_text(encoding="utf-8"))
    blockers: list[str] = []
    if int(receipt.get("schema_version", -1)) != 1:
        blockers.append("schema_version")
    if receipt.get("receipt_id") not in {
        "CRYPTO_SEARCH_EVIDENCE_V1_1_VALIDATION",
        "CRYPTO_SEARCH_EVIDENCE_V1_1_VALIDATION_REPLACEMENT",
    }:
        blockers.append("receipt_id")
    if require_authorized is not None and bool(receipt.get("run_authorized")) is not bool(
        require_authorized
    ):
        blockers.append("run_authorized")
    source = dict(receipt.get("source_evidence") or {})
    selection = dict(receipt.get("selection") or {})
    validation = dict(receipt.get("validation") or {})
    compute = dict(receipt.get("compute") or {})
    boundaries = dict(receipt.get("boundaries") or {})
    if source.get("candidate_ledger_sha256") != (
        "6554BECC35E8586F63505DA4646F41482BEFB80FEE4618B2710C22A35A8D6718"
    ):
        blockers.append("candidate_ledger_sha256")
    if source.get("behavior_archive_sha256") != (
        "182D2ABB810B73C02622BBA51E41F231EFA0AED8A4D1E15B93D48499866C391F"
    ):
        blockers.append("behavior_archive_sha256")
    if selection.get("candidate_count_exact") != 49:
        blockers.append("candidate_count_exact")
    if selection.get("selection_sha256") != EXPECTED_SELECTION_SHA256:
        blockers.append("selection_sha256")
    if validation != {
        "start": "2025-11-01T00:00:00Z",
        "end_exclusive": "2026-01-01T00:00:00Z",
        "role": "DEVELOPMENT_VALIDATION_NO_FEEDBACK",
        "execution_venue": "BINANCE_USD_M",
        "cost_bps": 5.0,
    }:
        blockers.append("validation")
    if compute.get("workers_default") != 10 or compute.get("workers_fallback") != 8:
        blockers.append("workers")
    required_false = (
        "candidate_generation",
        "optimizer_feedback",
        "policy_memory_write",
        "archive_write",
        "backfill",
        "restart",
        "reseed",
        "parameter_tuning",
        "rescue_rerun",
        "holdout_read",
        "oos",
        "promotion",
    )
    if any(boundaries.get(key) is not False for key in required_false):
        blockers.append("boundaries")
    if blockers:
        raise RuntimeError("EVIDENCE_VALIDATION_RECEIPT_INVALID:" + ",".join(blockers))
    return receipt


def _selection_projection(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": str(row["candidate_id"]),
            "candidate_spec_sha256": str(row["candidate_spec_sha256"]),
            "behavior_family_id": str(row["behavior_family_id"]),
            "arm": str(row["arm"]),
            "seed": int(row["seed"]),
            "horizon_hours": int(row["horizon_hours"]),
            "search_reward": float(row["search_reward"]),
            "train_orientation": float(row["train_orientation"]),
        }
        for row in rows
    ]


def select_final_positive_champions(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Rebuild the exact final champion cohort from immutable train artifacts."""

    root = Path(repo_root)
    receipt = dict(receipt or load_validation_receipt(root))
    source = dict(receipt["source_evidence"])
    ledger_path = root / str(source["candidate_ledger_path"])
    archive_path = root / str(source["behavior_archive_path"])
    if (
        _file_sha256(ledger_path) != str(source["candidate_ledger_sha256"])
        or _file_sha256(archive_path) != str(source["behavior_archive_sha256"])
    ):
        raise RuntimeError("EVIDENCE_VALIDATION_SOURCE_ARTIFACT_CHANGED")
    ledger = pd.read_parquet(ledger_path)
    archive = pd.read_parquet(archive_path)
    if len(ledger) != int(source["candidate_ledger_row_count"]):
        raise RuntimeError("EVIDENCE_VALIDATION_SOURCE_LEDGER_COUNT_CHANGED")
    champions = archive.loc[
        archive["is_family_champion"].eq(True) & archive["search_reward"].gt(0.0),
        ["exact_expression_id", "behavior_family_id", "arm", "seed"],
    ]
    selected = ledger.merge(
        champions,
        on=["exact_expression_id", "behavior_family_id", "arm", "seed"],
        how="inner",
        validate="one_to_one",
    ).sort_values("candidate_id", kind="stable")
    rows = selected.to_dict("records")
    if (
        len(rows) != 49
        or selected["candidate_id"].nunique() != 49
        or selected["behavior_family_id"].nunique() != 49
        or not selected["search_reward"].gt(0.0).all()
    ):
        raise RuntimeError("EVIDENCE_VALIDATION_COHORT_CHANGED")
    prepared: list[dict[str, Any]] = []
    for row in rows:
        local = dict(row)
        local["candidate"] = json.loads(str(local["candidate_spec_json"]))
        local["source_arm"] = str(local["arm"])
        prepared.append(local)
    projection = _selection_projection(prepared)
    if _canonical_sha256(projection) != str(
        receipt["selection"]["selection_sha256"]
    ):
        raise RuntimeError("EVIDENCE_VALIDATION_SELECTION_CHANGED")
    return prepared


def _line_sha256(values: Sequence[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(str(item) for item in values))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def load_consensus_receipt(
    repo_root: Path,
    *,
    require_authorized: bool | None = None,
    receipt_path: str = CONSENSUS_RECEIPT_PATH,
) -> dict[str, Any]:
    receipt_file = Path(repo_root) / str(receipt_path)
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    blockers: list[str] = []
    if int(receipt.get("schema_version", -1)) != 1:
        blockers.append("schema_version")
    if receipt.get("receipt_id") != "CRYPTO_SEARCH_FAMILY_CONSENSUS_DEV_V1":
        blockers.append("receipt_id")
    if require_authorized is not None and bool(receipt.get("run_authorized")) is not bool(
        require_authorized
    ):
        blockers.append("run_authorized")
    cohort = dict(receipt.get("cohort") or {})
    main_ids = [str(value) for value in cohort.get("main_candidate_ids") or ()]
    other_ids = [str(value) for value in cohort.get("other_candidate_ids") or ()]
    if (
        len(main_ids) != 23
        or len(set(main_ids)) != 23
        or _line_sha256(main_ids) != CONSENSUS_MAIN_CANDIDATE_IDS_SHA256
    ):
        blockers.append("main_cohort")
    if (
        len(other_ids) != 12
        or len(set(other_ids)) != 12
        or _line_sha256(other_ids) != CONSENSUS_OTHER_CANDIDATE_IDS_SHA256
        or set(main_ids) & set(other_ids)
    ):
        blockers.append("other_cohort")
    interval = dict(receipt.get("development_fresh_interval") or {})
    if interval != {
        "start": "2026-07-18T00:00:00Z",
        "end_exclusive": "2026-08-01T00:00:00Z",
        "hours": 336,
        "role": "SECOND_STAGE_DEVELOPMENT_FRESH_NO_FEEDBACK",
    }:
        blockers.append("development_fresh_interval")
    aggregation = dict(receipt.get("aggregation") or {})
    if (
        aggregation.get("coefficient_rule") != "EQUAL_FIXED_1_OVER_N"
        or aggregation.get("support_rule")
        != "COMMON_INTERSECTION_SHARED_BY_PRIMARY_LEFT_RIGHT"
        or aggregation.get("missing_weight_rule") != "FLAT_ZERO_OUTSIDE_COMMON_SUPPORT"
        or aggregation.get("economics_rule")
        != "RECOMPUTE_FROM_AGGREGATE_EXECUTABLE_WEIGHTS"
        or aggregation.get("comparison_role")
        != "MAIN_23_PRIMARY_OTHER_12_DESCRIPTIVE_ONLY"
    ):
        blockers.append("aggregation")
    compute = dict(receipt.get("compute") or {})
    if (
        int(compute.get("workers_default", -1)) != 10
        or int(compute.get("workers_fallback", -1)) != 8
        or compute.get("workers_12_forbidden") is not True
    ):
        blockers.append("compute")
    boundaries = dict(receipt.get("boundaries") or {})
    required_false = (
        "candidate_generation",
        "optimizer_feedback",
        "policy_memory_write",
        "archive_write",
        "parameter_tuning",
        "rescue_rerun",
        "second_run",
        "oos",
        "promotion",
        "challenge",
        "forward",
    )
    if any(boundaries.get(key) is not False for key in required_false):
        blockers.append("boundaries")
    if blockers:
        raise RuntimeError("FAMILY_CONSENSUS_RECEIPT_INVALID:" + ",".join(blockers))
    return receipt


def select_consensus_cohort(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    root = Path(repo_root)
    receipt = dict(receipt or load_consensus_receipt(root))
    source = dict(receipt["source_evidence"])
    train_path = root / str(source["candidate_ledger_path"])
    validation_path = root / str(source["validation_ledger_path"])
    if (
        _file_sha256(train_path) != str(source["candidate_ledger_sha256"])
        or _file_sha256(validation_path) != str(source["validation_ledger_sha256"])
    ):
        raise RuntimeError("FAMILY_CONSENSUS_SOURCE_LEDGER_CHANGED")
    train = pd.read_parquet(train_path)
    validation = pd.read_parquet(validation_path)
    cohort = dict(receipt["cohort"])
    grouped: dict[str, list[dict[str, Any]]] = {}
    all_ids: set[str] = set()
    for group, key in (("main", "main_candidate_ids"), ("other", "other_candidate_ids")):
        ids = [str(value) for value in cohort[key]]
        selected_validation = validation.loc[
            validation["candidate_id"].astype(str).isin(ids)
        ].copy()
        selected_train = train.loc[train["candidate_id"].astype(str).isin(ids)].copy()
        if (
            len(selected_validation) != len(ids)
            or len(selected_train) != len(ids)
            or selected_validation["candidate_id"].nunique() != len(ids)
            or selected_train["candidate_id"].nunique() != len(ids)
        ):
            raise RuntimeError("FAMILY_CONSENSUS_COHORT_JOIN_CHANGED")
        joined = selected_train.merge(
            selected_validation[
                [
                    "candidate_id",
                    "train_declared_axis_count",
                    "validation_search_reward",
                    "validation_left_incremental_net_mean",
                    "validation_right_incremental_net_mean",
                ]
            ],
            on="candidate_id",
            how="inner",
            validate="one_to_one",
        ).sort_values("candidate_id", kind="stable")
        if (
            not joined["horizon_hours"].eq(4).all()
            or not joined["declared_axis_count"].eq(2).all()
            or not joined["train_declared_axis_count"].eq(2).all()
        ):
            raise RuntimeError("FAMILY_CONSENSUS_PRIMARY_SLICE_CHANGED")
        if group == "main" and (
            not joined["mechanism_family"].eq(
                "MECHANISM_V2_FLOW_INTENSITY_CONVICTION"
            ).all()
            or not joined["mapping_family"].eq(
                "TIME_SERIES_DIRECTIONAL_STATEFUL"
            ).all()
        ):
            raise RuntimeError("FAMILY_CONSENSUS_MAIN_POCKET_CHANGED")
        rows: list[dict[str, Any]] = []
        for row in joined.to_dict("records"):
            local = dict(row)
            local["candidate"] = json.loads(str(local["candidate_spec_json"]))
            local["source_arm"] = str(local.get("source_arm") or local["arm"])
            local["consensus_group"] = group
            rows.append(local)
        if [str(row["candidate_id"]) for row in rows] != sorted(ids):
            raise RuntimeError("FAMILY_CONSENSUS_CANDIDATE_ORDER_CHANGED")
        grouped[group] = rows
        all_ids.update(ids)
    if len(all_ids) != 35:
        raise RuntimeError("FAMILY_CONSENSUS_TOTAL_COHORT_CHANGED")
    return grouped


def freeze_selection_before_validation_read(
    repo_root: Path,
    runtime_root: Path,
    *,
    producer_source_sha: str,
    receipt: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    output = Path(runtime_root) / "behavior_family_selection_receipt.json"
    if output.exists():
        raise RuntimeError("EVIDENCE_VALIDATION_RUNTIME_ALREADY_EXISTS")
    payload = {
        "schema_version": 1,
        "status": "SELECTION_FROZEN_BEFORE_VALIDATION_READ",
        "producer_source_sha": str(producer_source_sha).lower(),
        "run_receipt_sha256": _file_sha256(Path(repo_root) / str(receipt_path)),
        "source_candidate_ledger_sha256": receipt["source_evidence"][
            "candidate_ledger_sha256"
        ],
        "source_behavior_archive_sha256": receipt["source_evidence"][
            "behavior_archive_sha256"
        ],
        "candidate_count": len(rows),
        "selection_sha256": _canonical_sha256(_selection_projection(rows)),
        "candidate_ids": [str(row["candidate_id"]) for row in rows],
        "market_read_performed": False,
        "candidate_generation_performed": False,
        "optimizer_feedback_used": False,
    }
    payload["receipt_sha256"] = _canonical_sha256(payload)
    _write_json(output, payload)
    return payload


def freeze_consensus_selection_before_fresh_read(
    repo_root: Path,
    runtime_root: Path,
    *,
    producer_source_sha: str,
    receipt: Mapping[str, Any],
    grouped_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    receipt_path: str = CONSENSUS_RECEIPT_PATH,
) -> dict[str, Any]:
    output = Path(runtime_root) / "behavior_family_selection_receipt.json"
    if output.exists():
        raise RuntimeError("FAMILY_CONSENSUS_SELECTION_ALREADY_FROZEN")
    groups = {
        name: [
            {
                "candidate_id": str(row["candidate_id"]),
                "candidate_spec_sha256": str(row["candidate_spec_sha256"]),
                "behavior_family_id": str(row["behavior_family_id"]),
                "train_orientation": float(row["train_orientation"]),
                "coefficient": 1.0 / float(len(rows)),
            }
            for row in rows
        ]
        for name, rows in grouped_rows.items()
    }
    payload = {
        "schema_version": 1,
        "status": "CONSENSUS_SELECTION_FROZEN_BEFORE_FRESH_MARKET_PAYLOAD_READ",
        "producer_source_sha": str(producer_source_sha).lower(),
        "run_receipt_sha256": _file_sha256(Path(repo_root) / str(receipt_path)),
        "development_fresh_interval": dict(receipt["development_fresh_interval"]),
        "groups": groups,
        "main_candidate_ids_sha256": _line_sha256(
            [row["candidate_id"] for row in groups["main"]]
        ),
        "other_candidate_ids_sha256": _line_sha256(
            [row["candidate_id"] for row in groups["other"]]
        ),
        "market_payload_read": False,
        "source_metadata_probe_only_before_freeze": True,
        "candidate_generation_performed": False,
        "optimizer_feedback_used": False,
        "coefficient_rule": "EQUAL_FIXED_1_OVER_N",
    }
    payload["receipt_sha256"] = _canonical_sha256(payload)
    _write_json(output, payload)
    return payload


def freeze_consensus_run(
    repo_root: Path,
    *,
    runtime_date: str = CONSENSUS_DEFAULT_RUNTIME_DATE,
    producer_source_sha: str | None = None,
    receipt_path: str = CONSENSUS_RECEIPT_PATH,
) -> dict[str, Any]:
    """Freeze cohort and contracts before the development-fresh payload is read."""

    root = Path(repo_root)
    receipt = load_consensus_receipt(
        root, require_authorized=True, receipt_path=receipt_path
    )
    observed_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()
    source_sha = str(producer_source_sha or observed_sha).lower()
    if (
        source_sha != observed_sha
        or source_sha != str(receipt["source_implementation_sha"]).lower()
    ):
        raise RuntimeError("FAMILY_CONSENSUS_PRODUCER_SHA_CHANGED")
    runtime_root = root / "runtime" / f"{CONSENSUS_RUNTIME_PREFIX}_{runtime_date}"
    if runtime_root.exists():
        raise RuntimeError("FAMILY_CONSENSUS_RUNTIME_ALREADY_EXISTS")
    runtime_root.mkdir(parents=True)
    grouped = select_consensus_cohort(root, receipt=receipt)
    selection = freeze_consensus_selection_before_fresh_read(
        root,
        runtime_root,
        producer_source_sha=source_sha,
        receipt=receipt,
        grouped_rows=grouped,
        receipt_path=receipt_path,
    )
    from alphafactory_crypto.broad_search.search_engine_v1 import (
        _contracts_payload,
        _load_v14_config,
        _v14_carrier_contracts,
    )

    v14_config, _ = _load_v14_config(root)
    oi_contracts, agg_contracts, _, _ = _v14_carrier_contracts(root, v14_config)
    contract_rows = _contracts_payload(tuple((*oi_contracts, *agg_contracts)))
    if len(contract_rows) != 115:
        raise RuntimeError("FAMILY_CONSENSUS_CONTRACT_COUNT_CHANGED")
    all_rows = [*grouped["main"], *grouped["other"]]
    static = sweep_v24_static_constructibility(
        selected_rows=all_rows, contract_rows=contract_rows
    )
    if int(static["candidate_count"]) != 35:
        raise RuntimeError("FAMILY_CONSENSUS_STATIC_COUNT_CHANGED")
    _write_json(runtime_root / "static_constructibility.json", static)
    source_probe = dict(receipt["source_metadata_probe"])
    frozen = {
        "schema_version": 1,
        "status": "FROZEN_BEFORE_DEVELOPMENT_FRESH_MARKET_PAYLOAD_READ",
        "producer_source_sha": source_sha,
        "run_receipt_sha256": _file_sha256(root / str(receipt_path)),
        "selection_receipt_sha256": selection["receipt_sha256"],
        "main_candidate_ids_sha256": CONSENSUS_MAIN_CANDIDATE_IDS_SHA256,
        "other_candidate_ids_sha256": CONSENSUS_OTHER_CANDIDATE_IDS_SHA256,
        "main_member_count": 23,
        "other_member_count": 12,
        "development_fresh_interval": dict(receipt["development_fresh_interval"]),
        "aggregation": dict(receipt["aggregation"]),
        "carrier": dict(receipt["carrier"]),
        "source_metadata_probe": source_probe,
        "contracts_sha256": _canonical_sha256(contract_rows),
        "contract_count": len(contract_rows),
        "compute": dict(receipt["compute"]),
        "boundaries": dict(receipt["boundaries"]),
        "market_payload_read": False,
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "archive_written": False,
    }
    frozen["frozen_contract_sha256"] = _canonical_sha256(frozen)
    _write_json(runtime_root / "frozen_contract.json", frozen)
    _write_json(
        runtime_root / "producer_status.json",
        {
            "schema_version": 1,
            "status": "FROZEN_AWAITING_SINGLE_PC2_ACQUISITION_AND_GATE",
            "producer_source_sha": source_sha,
            "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "completed_candidate_count": 0,
            "market_payload_read": False,
            "candidate_generation_performed": False,
            "optimizer_feedback_written": False,
            "archive_written": False,
        },
    )
    return {
        "status": "FROZEN_AWAITING_SINGLE_PC2_ACQUISITION_AND_GATE",
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "producer_source_sha": source_sha,
        "selection_receipt_sha256": selection["receipt_sha256"],
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "candidate_count": 35,
        "market_payload_read": False,
    }


def _merge_raw_panel_stores(
    *,
    segment_roots: Sequence[Path],
    output_root: Path,
    source_binding_sha256: str,
) -> dict[str, Any]:
    """Join existing RawPanelStore segments without creating another store API."""

    from alphafactory_crypto.broad_search.runner18m import RawPanelStore
    from alphafactory_crypto.data_admission_v1 import _write_raw_panel_store

    stores = [RawPanelStore.open(Path(path)) for path in segment_roots]
    if len(stores) < 2:
        raise ValueError("FAMILY_CONSENSUS_MERGE_REQUIRES_MULTIPLE_SEGMENTS")
    field_ids = tuple(str(value) for value in stores[0].metadata["field_ids"])
    if any(set(store.metadata["field_ids"]) != set(field_ids) for store in stores[1:]):
        raise RuntimeError("FAMILY_CONSENSUS_SEGMENT_FIELD_SET_CHANGED")
    common_symbols = tuple(sorted(set.intersection(*(set(store.symbols) for store in stores))))
    if len(common_symbols) < 3:
        raise RuntimeError("FAMILY_CONSENSUS_SEGMENT_COMMON_ASSETS_BELOW_THREE")
    timestamps_by_segment = [np.asarray(store.timestamp_ns, dtype=np.int64) for store in stores]
    one_hour_ns = int(pd.Timedelta(hours=1).value)
    for index, timestamps in enumerate(timestamps_by_segment):
        if timestamps.size == 0 or (
            timestamps.size > 1 and not np.all(np.diff(timestamps) == one_hour_ns)
        ):
            raise RuntimeError("FAMILY_CONSENSUS_SEGMENT_TIMESTAMP_GAP")
        if index and int(timestamps_by_segment[index - 1][-1]) + one_hour_ns != int(
            timestamps[0]
        ):
            raise RuntimeError("FAMILY_CONSENSUS_SEGMENT_BOUNDARY_CHANGED")
    row_indices = [
        np.asarray([store.symbols.index(symbol) for symbol in common_symbols], dtype=int)
        for store in stores
    ]

    def concatenate(loader: Any, dtype: Any) -> np.ndarray:
        return np.concatenate(
            [
                np.asarray(loader(store), dtype=dtype)[indices]
                for store, indices in zip(stores, row_indices)
            ],
            axis=1,
        )

    observed = concatenate(lambda store: store.observed(), bool)
    base_eligible = concatenate(lambda store: store.base_eligible(), bool)
    source_segments = concatenate(
        lambda store: np.load(store.cache_root / "source_segment.npy", mmap_mode="r"),
        np.int8,
    )
    fields = {
        field_id: concatenate(lambda store, name=field_id: store.field(name), np.float32)
        for field_id in field_ids
    }
    timestamp_ns = np.concatenate(timestamps_by_segment)
    shape = (len(common_symbols), int(timestamp_ns.size))
    identity_payload = {
        "schema_version": 1,
        "role": "EXISTING_RAW_PANEL_STORE_SEGMENT_JOIN_FOR_ONE_CONSENSUS_GATE",
        "source_binding_sha256": str(source_binding_sha256),
        "segment_identities": [str(store.metadata["identity_sha256"]) for store in stores],
        "symbol_ids": list(common_symbols),
        "field_ids": list(field_ids),
        "start_utc": pd.Timestamp(int(timestamp_ns[0]), tz="UTC").isoformat(),
        "end_exclusive_utc": pd.Timestamp(
            int(timestamp_ns[-1]) + one_hour_ns, tz="UTC"
        ).isoformat(),
    }
    metadata = {
        "schema_version": 2,
        "surface_id": "OI_MARK_X_AGGTRADES_115_FAMILY_CONSENSUS_EXTENDED",
        "cache_role": "SEARCH_SURFACE_INTEGRATION_V1_RAW_PANEL_STORE",
        "identity_sha256": _canonical_sha256(identity_payload),
        "producer_binding_sha256": str(source_binding_sha256),
        "assets": shape[0],
        "timestamps": shape[1],
        "symbol_ids": list(common_symbols),
        "field_ids": list(field_ids),
        "target_horizons_hours": [1, 4],
        "target_formula": "TARGET_OVERRIDE_ONLY_BINANCE_DELAYED_OPEN",
        "start_utc": identity_payload["start_utc"],
        "end_exclusive_utc": identity_payload["end_exclusive_utc"],
        "observed_coordinates": int(observed.sum()),
        "eligible_coordinates": int(base_eligible.sum()),
        "minimum_assets_per_timestamp": 3,
        "contexts_merged": False,
        "research_admission": "HOLD_SECOND_STAGE_DEVELOPMENT_ONLY",
        "sealed_rows": 0,
        "segment_identities": identity_payload["segment_identities"],
    }
    targets = {
        horizon: np.full(shape, np.nan, dtype=np.float32) for horizon in (1, 4)
    }
    return _write_raw_panel_store(
        output_root=Path(output_root),
        metadata=metadata,
        timestamp_ns=timestamp_ns,
        observed=observed,
        base_eligible=base_eligible,
        source_segment=source_segments,
        fields=fields,
        targets=targets,
        source_manifest=identity_payload,
    )


def prepare_consensus_carrier(
    repo_root: Path,
    *,
    new_oi_source_root: Path,
    old_aligned_cache: Path,
    v24_aligned_cache: Path,
    top100_tar: Path,
    ranks101_200_tar: Path,
    runtime_date: str = CONSENSUS_DEFAULT_RUNTIME_DATE,
    producer_source_sha: str | None = None,
    receipt_path: str = CONSENSUS_RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_consensus_receipt(
        root, require_authorized=True, receipt_path=receipt_path
    )
    observed_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()
    source_sha = str(producer_source_sha or observed_sha).lower()
    if source_sha != observed_sha or source_sha != str(
        receipt["source_implementation_sha"]
    ).lower():
        raise RuntimeError("FAMILY_CONSENSUS_PRODUCER_SHA_CHANGED")
    runtime_root = root / "runtime" / f"{CONSENSUS_RUNTIME_PREFIX}_{runtime_date}"
    selection_path = runtime_root / "behavior_family_selection_receipt.json"
    if not selection_path.is_file():
        raise RuntimeError("FAMILY_CONSENSUS_SELECTION_NOT_FROZEN")
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    saved_selection = str(selection.pop("receipt_sha256", ""))
    if (
        _canonical_sha256(selection) != saved_selection
        or selection.get("market_payload_read") is not False
    ):
        raise RuntimeError("FAMILY_CONSENSUS_SELECTION_RECEIPT_CHANGED")
    from alphafactory_crypto.broad_search.replay_v14_binance_target import (
        build_binance_target_cache,
    )
    from alphafactory_crypto.broad_search.runner18m import RawPanelStore
    from alphafactory_crypto.broad_search.search_engine_v1 import (
        _contracts_payload,
        _directory_bundle,
        _load_v14_config,
        _v14_carrier_contracts,
        sha256_file,
    )
    from alphafactory_crypto.data_admission_v1 import (
        build_aggtrades_search_surface_cache,
        build_oi_mark_search_carrier,
    )

    carrier = dict(receipt["carrier"])
    old_store = RawPanelStore.open(Path(old_aligned_cache))
    v24_store = RawPanelStore.open(Path(v24_aligned_cache))
    if (
        str(old_store.metadata["identity_sha256"])
        != str(carrier["old_aligned_cache_identity_sha256"])
        or str(v24_store.metadata["identity_sha256"])
        != str(carrier["v24_aligned_cache_identity_sha256"])
    ):
        raise RuntimeError("FAMILY_CONSENSUS_WARMUP_CARRIER_IDENTITY_CHANGED")
    v14_config, _ = _load_v14_config(root)
    oi_contracts, agg_contracts, _, _ = _v14_carrier_contracts(root, v14_config)
    contracts = tuple((*oi_contracts, *agg_contracts))
    if len(contracts) != 115:
        raise RuntimeError("FAMILY_CONSENSUS_CONTRACT_COUNT_CHANGED")
    new_oi_cache = root / str(carrier["new_oi_cache"])
    source_binding = _canonical_sha256(
        {
            "receipt_sha256": _file_sha256(root / str(receipt_path)),
            "source_probe_sha256": receipt["source_metadata_probe"]["sha256"],
            "new_oi_source_root": str(Path(new_oi_source_root)),
        }
    )
    oi_metadata, active_oi_contracts, _, oi_evidence = build_oi_mark_search_carrier(
        source_root=Path(new_oi_source_root),
        output_root=new_oi_cache,
        source_binding_sha256=source_binding,
    )
    if {item.field_id for item in active_oi_contracts} != {
        item.field_id for item in oi_contracts
    }:
        raise RuntimeError("FAMILY_CONSENSUS_NEW_OI_FIELD_SET_CHANGED")
    new_aligned_cache = root / str(carrier["new_aligned_cache"])
    new_aligned_metadata = build_aggtrades_search_surface_cache(
        source_cache_root=new_oi_cache,
        top100_tar=Path(top100_tar),
        ranks101_200_tar=Path(ranks101_200_tar),
        output_cache_root=new_aligned_cache,
        broad_field_ids=[item.field_id for item in oi_contracts],
        start=str(receipt["development_fresh_interval"]["start"]),
        end_exclusive=str(receipt["development_fresh_interval"]["end_exclusive"]),
        producer_source_sha=source_sha,
        verify_tar_sha256=True,
    )
    extended_cache = root / str(carrier["extended_aligned_cache"])
    extended_metadata = _merge_raw_panel_stores(
        segment_roots=(Path(old_aligned_cache), Path(v24_aligned_cache), new_aligned_cache),
        output_root=extended_cache,
        source_binding_sha256=source_binding,
    )
    target_config = json.loads(
        (root / "config/crypto_search_engine_v1_4_binance_target_replay.json").read_text(
            encoding="utf-8"
        )
    )
    target_root = root / str(carrier["target_cache"])
    target_metadata = build_binance_target_cache(
        root,
        source_store=RawPanelStore.open(extended_cache),
        config=target_config,
        target_cache_root=target_root,
    )
    contract_rows = _contracts_payload(contracts)
    manifest = {
        "schema_version": 1,
        "status": "FAMILY_CONSENSUS_CARRIER_READY",
        "producer_source_sha": source_sha,
        "selection_receipt_sha256": saved_selection,
        "development_fresh_interval": dict(receipt["development_fresh_interval"]),
        "contracts": contract_rows,
        "contracts_sha256": _canonical_sha256(contract_rows),
        "field_count": len(contract_rows),
        "new_oi_cache": {
            "path": str(new_oi_cache),
            "identity_sha256": oi_metadata["identity_sha256"],
            "evidence": oi_evidence,
        },
        "new_aligned_cache": {
            "path": str(new_aligned_cache),
            "identity_sha256": new_aligned_metadata["identity_sha256"],
        },
        "extended_aligned_cache": {
            "path": str(extended_cache),
            "identity_sha256": extended_metadata["identity_sha256"],
            "directory_bundle": _directory_bundle(extended_cache),
        },
        "target_cache": {
            "path": str(target_root),
            "identity_sha256": target_metadata["identity_sha256"],
        },
        "top100_tar_sha256": sha256_file(Path(top100_tar)),
        "ranks101_200_tar_sha256": sha256_file(Path(ranks101_200_tar)),
        "market_payload_read_after_selection_freeze": True,
        "missing_value_fill": None,
        "candidate_generation_performed": False,
    }
    manifest["manifest_sha256"] = _canonical_sha256(manifest)
    _write_json(runtime_root / "aligned_carrier_manifest.json", manifest)
    return manifest


def _build_economic_context(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any],
    target_identity_sha256: str,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    from alphafactory_crypto.broad_search.experiment_authority import (
        resolve_search_economic_receipt,
    )

    source = dict(receipt["source_evidence"])
    base = resolve_search_economic_receipt(
        Path(repo_root), str(source["economic_receipt_path"])
    )
    validation = {
        "role": str(receipt["validation"]["role"]),
        "start": str(receipt["validation"]["start"]),
        "end_exclusive": str(receipt["validation"]["end_exclusive"]),
        "optimizer_feedback_allowed": False,
        "policy_memory_write_allowed": False,
        "candidate_generation_allowed": False,
    }
    partitions = {
        **{key: dict(value) for key, value in dict(base["evidence_partition"]).items()},
        "validation": validation,
    }
    execution = {
        **dict(base["execution"]),
        "target_cache_path": str(receipt["carrier"]["target_cache"]),
        "target_cache_identity_sha256": str(target_identity_sha256),
    }
    return {
        **base,
        "run_authorized": True,
        "run_authorization": {
            "decision_id": str(receipt["decision_id"]),
            "authority": "CURRENT_USER_INSTRUCTION",
            "scope": "ONE_EXACT_49_CHAMPION_DEVELOPMENT_VALIDATION_NO_FEEDBACK",
            "parameter_tuning_allowed": False,
            "seed_change_allowed": False,
            "rescue_rerun_allowed": False,
        },
        "evidence_partition": partitions,
        "validation": validation,
        "execution": execution,
        "receipt_sha256": _file_sha256(Path(repo_root) / str(receipt_path)),
    }


def _build_consensus_economic_context(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any],
    target_identity_sha256: str,
    receipt_path: str = CONSENSUS_RECEIPT_PATH,
) -> dict[str, Any]:
    from alphafactory_crypto.broad_search.experiment_authority import (
        resolve_search_economic_receipt,
    )

    base = resolve_search_economic_receipt(
        Path(repo_root), str(receipt["source_evidence"]["economic_receipt_path"])
    )
    interval = dict(receipt["development_fresh_interval"])
    validation = {
        "role": str(interval["role"]),
        "start": str(interval["start"]),
        "end_exclusive": str(interval["end_exclusive"]),
        "optimizer_feedback_allowed": False,
        "policy_memory_write_allowed": False,
        "candidate_generation_allowed": False,
    }
    partitions = {
        **{key: dict(value) for key, value in dict(base["evidence_partition"]).items()},
        "validation": validation,
    }
    execution = {
        **dict(base["execution"]),
        "target_cache_path": str(receipt["carrier"]["target_cache"]),
        "target_cache_identity_sha256": str(target_identity_sha256),
    }
    return {
        **base,
        "run_authorized": True,
        "run_authorization": {
            "decision_id": str(receipt["decision_id"]),
            "authority": "CURRENT_USER_INSTRUCTION",
            "scope": "ONE_4H_TWO_AXIS_FAMILY_CONSENSUS_SECOND_STAGE_DEVELOPMENT_GATE",
            "parameter_tuning_allowed": False,
            "seed_change_allowed": False,
            "rescue_rerun_allowed": False,
        },
        "evidence_partition": partitions,
        "validation": validation,
        "execution": execution,
        "receipt_sha256": _file_sha256(Path(repo_root) / str(receipt_path)),
    }


def _metrics_projection(
    group: str, sleeve: str, metrics: Mapping[str, Any]
) -> dict[str, Any]:
    output = {
        "consensus_group": str(group),
        "sleeve": str(sleeve),
    }
    for key, value in metrics.items():
        if key == "month_metrics":
            output["month_metrics_json"] = json.dumps(
                value, sort_keys=True, separators=(",", ":"), default=str
            )
        elif isinstance(value, (str, bool, int, float)) or value is None:
            output[key] = value
    return output


def _aggregate_consensus_group(
    *,
    group: str,
    rows: Sequence[Mapping[str, Any]],
    workers: Sequence[Mapping[str, Any]],
    target: np.ndarray,
) -> dict[str, Any]:
    from alphafactory_crypto.broad_search.pair18m import (
        _series_metrics,
        strict_pair_feedback,
        turnover_path,
    )

    lookup = {str(row["candidate_id"]): row for row in workers}
    if set(lookup) != {str(row["candidate_id"]) for row in rows}:
        raise RuntimeError("FAMILY_CONSENSUS_WORKER_ID_SET_CHANGED")
    if any(lookup[str(row["candidate_id"])].get("error") for row in rows):
        raise RuntimeError("FAMILY_CONSENSUS_FIXED_MEMBER_EVALUATION_FAILED")
    evaluations = [
        dict(lookup[str(row["candidate_id"])]["evaluation"])["_economic_paths"]
        for row in rows
    ]
    first = dict(evaluations[0])
    asset_ids = tuple(str(value) for value in first["asset_ids"])
    timestamp_ns = np.asarray(first["timestamp_ns"], dtype=np.int64)
    for paths in evaluations[1:]:
        if (
            tuple(str(value) for value in paths["asset_ids"]) != asset_ids
            or not np.array_equal(
                np.asarray(paths["timestamp_ns"], dtype=np.int64), timestamp_ns
            )
            or float(paths["cost_bps"]) != 5.0
            or int(paths["horizon_hours"]) != 4
        ):
            raise RuntimeError("FAMILY_CONSENSUS_ECONOMIC_PATH_IDENTITY_CHANGED")
    required = ("primary", "control_left", "control_right")
    common_mask = np.ones(timestamp_ns.shape, dtype=bool)
    for paths in evaluations:
        sleeves = dict(paths["sleeves"])
        for name in required:
            common_mask &= np.asarray(sleeves[name]["mask"], dtype=bool)
    if int(common_mask.sum()) < 24:
        raise RuntimeError("FAMILY_CONSENSUS_COMMON_SUPPORT_TOO_SMALL")
    stacks: dict[str, np.ndarray] = {}
    for name in required:
        local = []
        for paths in evaluations:
            weights = np.asarray(paths["sleeves"][name]["weights"], dtype=float)
            if weights.shape != (len(asset_ids), timestamp_ns.size):
                raise RuntimeError("FAMILY_CONSENSUS_WEIGHT_SHAPE_CHANGED")
            if not np.isfinite(weights[:, common_mask]).all():
                raise RuntimeError("FAMILY_CONSENSUS_COMMON_WEIGHT_NOT_FINITE")
            local.append(np.where(common_mask[np.newaxis, :], weights, 0.0))
        stacks[name] = np.stack(local, axis=0)
    stacks["primary_minus_left_control"] = (
        stacks["primary"] - stacks["control_left"]
    )
    stacks["primary_minus_right_control"] = (
        stacks["primary"] - stacks["control_right"]
    )
    consensus = {name: values.mean(axis=0) for name, values in stacks.items()}
    if np.asarray(target).shape != consensus["primary"].shape:
        raise RuntimeError("FAMILY_CONSENSUS_TARGET_SHAPE_CHANGED")
    months = np.asarray(
        pd.to_datetime(timestamp_ns, utc=True).strftime("%Y-%m"), dtype=object
    )
    metric_rows: list[dict[str, Any]] = []
    metrics_by_sleeve: dict[str, dict[str, Any]] = {}
    hourly_rows: list[dict[str, Any]] = []
    asset_rows: list[dict[str, Any]] = []
    for sleeve, weights in consensus.items():
        metrics = _series_metrics(
            weights=weights,
            target=np.asarray(target, dtype=float),
            months=months,
            evaluation_mask=common_mask,
            horizon=4,
            cost_bps=5.0,
            timestamp_ns=timestamp_ns,
        )
        metrics_by_sleeve[sleeve] = metrics
        metric_rows.append(_metrics_projection(group, sleeve, metrics))
        turnover, _ = turnover_path(weights, 4)
        gross = np.nansum(weights * np.asarray(target, dtype=float), axis=0) / 4.0
        cost = turnover * 5.0 / 10_000.0
        net = gross - cost
        active = common_mask | (turnover > 1.0e-12)
        for index in np.flatnonzero(active):
            hourly_rows.append(
                {
                    "consensus_group": group,
                    "sleeve": sleeve,
                    "timestamp_ns": int(timestamp_ns[index]),
                    "common_support": bool(common_mask[index]),
                    "gross": float(gross[index]),
                    "turnover": float(turnover[index]),
                    "cost": float(cost[index]),
                    "net": float(net[index]),
                }
            )
            for asset_index, asset_id in enumerate(asset_ids):
                value = float(weights[asset_index, index])
                if abs(value) > 1.0e-12:
                    asset_rows.append(
                        {
                            "consensus_group": group,
                            "sleeve": sleeve,
                            "timestamp_ns": int(timestamp_ns[index]),
                            "asset_id": asset_id,
                            "weight": value,
                        }
                    )
    influence_rows: list[dict[str, Any]] = []
    concentration_rows: list[dict[str, Any]] = []
    for sleeve, values in stacks.items():
        full = consensus[sleeve]
        member_l1 = np.sum(np.abs(values[:, :, common_mask]), axis=(1, 2))
        total_member_l1 = float(member_l1.sum())
        shares = (
            member_l1 / total_member_l1
            if total_member_l1 > 0.0
            else np.full(len(rows), np.nan)
        )
        individual_mean_l1 = float(
            np.mean(np.sum(np.abs(values[:, :, common_mask]), axis=1))
        )
        consensus_mean_l1 = float(
            np.mean(np.sum(np.abs(full[:, common_mask]), axis=0))
        )
        concentration_rows.append(
            {
                "consensus_group": group,
                "sleeve": sleeve,
                "member_count": len(rows),
                "common_support_hours": int(common_mask.sum()),
                "candidate_l1_share_hhi": float(np.nansum(shares * shares)),
                "candidate_l1_share_max": float(np.nanmax(shares)),
                "weight_cancellation_ratio": (
                    consensus_mean_l1 / individual_mean_l1
                    if individual_mean_l1 > 0.0
                    else float("nan")
                ),
            }
        )
        for index, row in enumerate(rows):
            leave_one_out = (
                (values.sum(axis=0) - values[index]) / float(len(rows) - 1)
                if len(rows) > 1
                else full.copy()
            )
            delta = full[:, common_mask] - leave_one_out[:, common_mask]
            influence_rows.append(
                {
                    "consensus_group": group,
                    "sleeve": sleeve,
                    "candidate_id": str(row["candidate_id"]),
                    "candidate_l1_share": float(shares[index]),
                    "leave_one_out_mean_l1_distance": float(
                        np.mean(np.sum(np.abs(delta), axis=0))
                    ),
                    "target_used": False,
                }
            )
    left_feedback = strict_pair_feedback(
        metrics_by_sleeve["primary_minus_left_control"]
    )
    right_feedback = strict_pair_feedback(
        metrics_by_sleeve["primary_minus_right_control"]
    )
    summary = {
        "consensus_group": group,
        "member_count": len(rows),
        "common_support_hours": int(common_mask.sum()),
        "coefficient": 1.0 / float(len(rows)),
        "left_incremental_net_mean": float(
            metrics_by_sleeve["primary_minus_left_control"]["net_mean"]
        ),
        "right_incremental_net_mean": float(
            metrics_by_sleeve["primary_minus_right_control"]["net_mean"]
        ),
        "left_incremental_net_lcb": float(
            metrics_by_sleeve["primary_minus_left_control"]["net_lcb"]
        ),
        "right_incremental_net_lcb": float(
            metrics_by_sleeve["primary_minus_right_control"]["net_lcb"]
        ),
        "left_matched_positive": bool(left_feedback["matched_positive"]),
        "right_matched_positive": bool(right_feedback["matched_positive"]),
        "dual_axis_matched_positive": bool(
            left_feedback["matched_positive"] and right_feedback["matched_positive"]
        ),
        "both_axis_net_mean_positive": bool(
            metrics_by_sleeve["primary_minus_left_control"]["net_mean"] > 0.0
            and metrics_by_sleeve["primary_minus_right_control"]["net_mean"] > 0.0
        ),
        "both_axis_net_lcb_positive": bool(
            metrics_by_sleeve["primary_minus_left_control"]["net_lcb"] > 0.0
            and metrics_by_sleeve["primary_minus_right_control"]["net_lcb"] > 0.0
        ),
        "left_feedback": left_feedback,
        "right_feedback": right_feedback,
    }
    return {
        "summary": summary,
        "metric_rows": metric_rows,
        "hourly_rows": hourly_rows,
        "asset_rows": asset_rows,
        "influence_rows": influence_rows,
        "concentration_rows": concentration_rows,
    }


def _augment_projection(
    projection: Mapping[str, Any],
    *,
    selected: Mapping[str, Any],
    worker: Mapping[str, Any],
) -> dict[str, Any]:
    output = dict(projection)
    output["train_declared_axis_count"] = int(selected["declared_axis_count"])
    output["primary_analysis_slice"] = bool(
        int(selected["horizon_hours"]) == 4
        and int(selected["declared_axis_count"]) == 2
    )
    if worker.get("error"):
        output.update(
            {
                "validation_search_reward": float("nan"),
                "validation_search_reward_feedback_json": None,
                "validation_behavior_family_id": None,
                "validation_declared_axis_count": None,
                "validation_active_axis_count": None,
                "validation_mechanism_realization_status": None,
            }
        )
        return output
    evaluation = dict(worker["evaluation"])
    feedback = dict(evaluation.get("search_reward_feedback") or {})
    behavior = dict(evaluation.get("behavior") or {})
    realization = dict(evaluation.get("mechanism_realization_provenance") or {})
    output.update(
        {
            "validation_search_reward": float(_search_ordering_reward(evaluation)),
            "validation_search_reward_feedback_json": json.dumps(
                feedback, sort_keys=True, separators=(",", ":"), default=str
            ),
            "validation_primary_search_reward": feedback.get("primary_search_reward"),
            "validation_matched_min_search_reward": feedback.get(
                "matched_min_search_reward"
            ),
            "validation_search_reward_limiting_component": feedback.get(
                "limiting_component"
            ),
            "validation_matched_positive": bool(evaluation["matched_positive"]),
            "validation_behavior_family_id": behavior.get("behavior_family_id"),
            "validation_declared_axis_count": realization.get("declared_axis_count"),
            "validation_active_axis_count": realization.get("active_axis_count"),
            "validation_mechanism_realization_status": realization.get("status"),
        }
    )
    output.update(
        {
            f"validation_{key}": value
            for key, value in _evaluation_audit_fields(evaluation).items()
        }
    )
    return output


def _slice_metrics(frame: pd.DataFrame) -> dict[str, Any]:
    evaluated = frame.loc[frame["strict_evaluated"].eq(True)].copy()
    if evaluated.empty:
        return {
            "source_count": int(len(frame)),
            "strict_evaluated_count": 0,
            "candidate_local_failure_count": int(len(frame)),
            "validation_search_reward_positive_count": 0,
            "matched_positive_count": 0,
            "primary_net_positive_count": 0,
            "both_axis_net_positive_count": 0,
            "both_axis_net_lcb_positive_count": 0,
            "train_validation_search_reward_spearman": None,
        }
    left_net = evaluated["validation_left_incremental_net_mean"]
    right_net = evaluated["validation_right_incremental_net_mean"]
    left_lcb = evaluated["validation_left_incremental_net_lcb"]
    right_lcb = evaluated["validation_right_incremental_net_lcb"]
    train_rank = evaluated["train_search_reward"].rank()
    validation_rank = evaluated["validation_search_reward"].rank()
    rank_corr = (
        train_rank.corr(validation_rank)
        if len(evaluated) > 1
        and train_rank.nunique() > 1
        and validation_rank.nunique() > 1
        else float("nan")
    )
    return {
        "source_count": int(len(frame)),
        "strict_evaluated_count": int(len(evaluated)),
        "candidate_local_failure_count": int(len(frame) - len(evaluated)),
        "validation_search_reward_positive_count": int(
            evaluated["validation_search_reward"].gt(0.0).sum()
        ),
        "matched_positive_count": int(
            evaluated["validation_matched_positive"].sum()
        ),
        "primary_net_positive_count": int(
            evaluated["validation_primary_net_mean"].gt(0.0).sum()
        ),
        "both_axis_net_positive_count": int(
            (left_net.gt(0.0) & right_net.gt(0.0)).sum()
        ),
        "both_axis_net_lcb_positive_count": int(
            (left_lcb.gt(0.0) & right_lcb.gt(0.0)).sum()
        ),
        "train_validation_search_reward_spearman": (
            float(rank_corr) if math.isfinite(float(rank_corr)) else None
        ),
    }


def _build_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    all_metrics = _slice_metrics(frame)
    primary = frame.loc[frame["primary_analysis_slice"].eq(True)]
    return {
        "schema_version": 1,
        "status": "VALIDATION_COMPLETE",
        "all_49": all_metrics,
        "primary_4h_two_axis": _slice_metrics(primary),
        "arm": {
            str(arm): _slice_metrics(local)
            for arm, local in frame.groupby("arm", sort=True)
        },
        "horizon": {
            str(int(horizon)): _slice_metrics(local)
            for horizon, local in frame.groupby("horizon_hours", sort=True)
        },
        "interpretation_boundary": (
            "DEVELOPMENT_VALIDATION_ONLY_NOT_GLOBALLY_UNTOUCHED_OOS_OR_PROMOTION"
        ),
    }


def _report(summary: Mapping[str, Any], source_sha: str) -> str:
    all_metrics = dict(summary["all_49"])
    primary = dict(summary["primary_4h_two_axis"])
    return f"""# Crypto Search Evidence V1.1 Champion Validation

- Status: `{summary['status']}`
- Producer source: `{source_sha}`
- Contract: exactly 49 final positive development behavior-family champions; no generation, feedback, backfill, tuning, reseed, OOS, or promotion.
- Partition: `2025-11-01` to `2026-01-01`, Binance USD-M delayed-open target, frozen direction/mapping/evaluator and 5 bps cost.
- Scope: development validation only; this block is not globally untouched confirmation.

## All 49 champions

- Strict evaluated: `{all_metrics['strict_evaluated_count']}/49`
- Candidate-local failures: `{all_metrics['candidate_local_failure_count']}`
- Positive validation search reward: `{all_metrics['validation_search_reward_positive_count']}`
- Matched positive: `{all_metrics['matched_positive_count']}`
- Both matched axes net positive: `{all_metrics['both_axis_net_positive_count']}`
- Both matched axes net-LCB positive: `{all_metrics['both_axis_net_lcb_positive_count']}`
- Train/validation reward rank correlation: `{all_metrics['train_validation_search_reward_spearman']}`

## Predeclared primary slice: 4h x two-axis

- Source: `{primary['source_count']}`
- Strict evaluated: `{primary['strict_evaluated_count']}`
- Positive validation search reward: `{primary['validation_search_reward_positive_count']}`
- Matched positive: `{primary['matched_positive_count']}`
- Both matched axes net positive: `{primary['both_axis_net_positive_count']}`
- Both matched axes net-LCB positive: `{primary['both_axis_net_lcb_positive_count']}`

No candidate is qualified or promoted by this report.
"""


def run_validation(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    producer_source_sha: str | None = None,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_validation_receipt(
        root, require_authorized=True, receipt_path=receipt_path
    )
    observed_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()
    source_sha = str(producer_source_sha or observed_sha).lower()
    if source_sha != observed_sha:
        raise RuntimeError("EVIDENCE_VALIDATION_SOURCE_SHA_CHANGED")
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    if runtime_root.exists():
        raise RuntimeError("EVIDENCE_VALIDATION_RUNTIME_ALREADY_EXISTS")
    runtime_root.mkdir(parents=True)
    selected = select_final_positive_champions(root, receipt=receipt)
    selection_receipt = freeze_selection_before_validation_read(
        root,
        runtime_root,
        producer_source_sha=source_sha,
        receipt=receipt,
        rows=selected,
        receipt_path=receipt_path,
    )
    carrier_manifest = json.loads(
        (root / str(receipt["carrier"]["manifest_path"])).read_text(encoding="utf-8")
    )
    contract_rows = list(carrier_manifest["contracts"])
    static = sweep_v24_static_constructibility(
        selected_rows=selected, contract_rows=contract_rows
    )
    _write_json(runtime_root / "static_constructibility.json", static)
    target_metadata = json.loads(
        (root / str(receipt["carrier"]["target_cache"]) / "metadata.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        str(carrier_manifest["cache_identity_sha256"])
        != str(receipt["carrier"]["cache_identity_sha256"])
        or str(target_metadata["identity_sha256"])
        != str(receipt["carrier"]["target_identity_sha256"])
        or len(contract_rows) != 115
    ):
        raise RuntimeError("EVIDENCE_VALIDATION_CARRIER_OR_TARGET_CHANGED")
    economic = _build_economic_context(
        root,
        receipt=receipt,
        target_identity_sha256=str(target_metadata["identity_sha256"]),
        receipt_path=receipt_path,
    )
    frozen = {
        "schema_version": 1,
        "producer_source_sha": source_sha,
        "run_receipt_sha256": _file_sha256(root / str(receipt_path)),
        "selection_receipt_sha256": selection_receipt["receipt_sha256"],
        "selection_sha256": receipt["selection"]["selection_sha256"],
        "candidate_count": 49,
        "validation": dict(receipt["validation"]),
        "carrier_cache_identity_sha256": carrier_manifest["cache_identity_sha256"],
        "target_cache_identity_sha256": target_metadata["identity_sha256"],
        "contracts_sha256": _canonical_sha256(contract_rows),
        "workers_default": 10,
        "workers_fallback": 8,
        "candidate_generation": False,
        "optimizer_feedback": False,
        "archive_write": False,
        "holdout_read": False,
    }
    frozen["frozen_contract_sha256"] = _canonical_sha256(frozen)
    _write_json(runtime_root / "frozen_contract.json", frozen)
    started = time.perf_counter()
    active_workers = int(receipt["compute"]["workers_default"])
    memory_fallback_used = False

    def write_status(status: str, **extra: Any) -> None:
        _write_json(
            runtime_root / "producer_status.json",
            {
                "schema_version": 1,
                "status": status,
                "producer_pid": os.getpid(),
                "producer_source_sha": source_sha,
                "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "source_candidate_count": 49,
                "workers": active_workers,
                "memory_fallback_used": memory_fallback_used,
                "active_wall_seconds": time.perf_counter() - started,
                "candidate_generation_performed": False,
                "optimizer_feedback_written": False,
                "archive_written": False,
                "holdout_read_count": 0,
                **extra,
            },
        )

    cache_root = root / str(receipt["carrier"]["aligned_cache"])
    target_root = root / str(receipt["carrier"]["target_cache"])

    def make_executor(workers: int) -> concurrent.futures.ProcessPoolExecutor:
        return concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            initializer=_v24_worker_initialize,
            initargs=(
                str(cache_root),
                str(target_root),
                contract_rows,
                economic,
                str(receipt["validation"]["start"]),
                str(receipt["validation"]["end_exclusive"]),
                str(receipt["validation"]["role"]),
            ),
        )

    write_status("VALIDATION_RUNNING", completed_candidate_count=0)
    payloads = [
        {
            "candidate": row["candidate"],
            "frozen_train_orientation": float(row["train_orientation"]),
        }
        for row in selected
    ]
    with make_executor(active_workers) as executor:
        workers = list(executor.map(_v24_worker_evaluate, payloads, chunksize=1))
    memory_indexes = [
        index for index, row in enumerate(workers) if bool(row.get("memory_error"))
    ]
    if memory_indexes:
        memory_fallback_used = True
        active_workers = int(receipt["compute"]["workers_fallback"])
        with make_executor(active_workers) as executor:
            retried = list(
                executor.map(
                    _v24_worker_evaluate,
                    [payloads[index] for index in memory_indexes],
                    chunksize=1,
                )
            )
        for index, row in zip(memory_indexes, retried):
            workers[index] = row
    if any(bool(row.get("memory_error")) for row in workers):
        write_status("ENGINE_BUDGET_EXHAUSTED_MEMORY")
        raise RuntimeError("EVIDENCE_VALIDATION_MEMORY_FALLBACK_EXHAUSTED")
    checkpoint_root = runtime_root / "checkpoints"
    temporary = checkpoint_root / f"checkpoint_000.tmp-{os.getpid()}"
    final_checkpoint = checkpoint_root / "checkpoint_000"
    temporary.mkdir(parents=True)
    projections = _v24_write_batch_projections(
        temporary,
        base_ordinal=0,
        selected_rows=selected,
        worker_rows=workers,
        economic_receipt_sha256=str(economic["receipt_sha256"]),
        persist_candidate_local_failures=True,
    )
    rows = [
        _augment_projection(item, selected=selected[index], worker=workers[index])
        for index, item in enumerate(projections)
    ]
    pd.DataFrame(rows).to_parquet(temporary / "candidate_ledger.parquet", index=False)
    checkpoint_manifest = {
        "schema_version": 1,
        "checkpoint": "checkpoint_000",
        "producer_source_sha": source_sha,
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "selection_receipt_sha256": selection_receipt["receipt_sha256"],
        "completed_candidate_count": 49,
        "strict_evaluated_count": sum(bool(row["strict_evaluated"]) for row in rows),
        "candidate_local_failure_count": sum(
            not bool(row["strict_evaluated"]) for row in rows
        ),
        "workers": active_workers,
        "memory_fallback_used": memory_fallback_used,
        "files": _v24_checkpoint_files(temporary),
    }
    checkpoint_manifest["manifest_sha256"] = _canonical_sha256(checkpoint_manifest)
    _write_json(temporary / "manifest.json", checkpoint_manifest)
    os.replace(temporary, final_checkpoint)
    ledger_path = runtime_root / "candidate_ledger.parquet"
    shutil.copy2(final_checkpoint / "candidate_ledger.parquet", ledger_path)
    summary = _build_summary(rows)
    _write_json(runtime_root / "validation_summary.json", summary)
    decision = {
        **summary,
        "producer_source_sha": source_sha,
        "selection_receipt_sha256": selection_receipt["receipt_sha256"],
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "arm_qualified": [],
        "promotion_authorized": False,
        "oos": False,
        "automatic_expansion": False,
    }
    _write_json(runtime_root / "final_decision.json", decision)
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    report_path = reports / f"CRYPTO_SEARCH_EVIDENCE_V1_1_VALIDATION_{runtime_date}.md"
    report_path.write_text(_report(summary, source_sha), encoding="utf-8")
    elapsed = time.perf_counter() - started
    manifest = {
        "schema_version": 1,
        "status": "VALIDATION_COMPLETE",
        "producer_source_sha": source_sha,
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "report": str(report_path.relative_to(root).as_posix()),
        "run_receipt_sha256": _file_sha256(root / str(receipt_path)),
        "selection_receipt_sha256": selection_receipt["receipt_sha256"],
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "candidate_count": 49,
        "strict_evaluated_count": summary["all_49"]["strict_evaluated_count"],
        "candidate_local_failure_count": summary["all_49"][
            "candidate_local_failure_count"
        ],
        "active_wall_seconds": elapsed,
        "pair_evaluated_per_hour": (
            summary["all_49"]["strict_evaluated_count"] * 3600.0 / elapsed
            if elapsed > 0
            else 0.0
        ),
        "workers": active_workers,
        "memory_fallback_used": memory_fallback_used,
        "checkpoint_count": 1,
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "holdout_read_count": 0,
        "oos": False,
        "promotion_authorized": False,
        "files": [
            {
                "path": str(path.relative_to(root).as_posix()),
                "bytes": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
            for path in (
                ledger_path,
                runtime_root / "validation_summary.json",
                runtime_root / "final_decision.json",
                final_checkpoint / "manifest.json",
                report_path,
            )
        ],
    }
    manifest["bundle_sha256"] = _canonical_sha256(manifest)
    _write_json(runtime_root / "run_manifest.json", manifest)
    write_status(
        "VALIDATION_COMPLETE",
        completed_candidate_count=49,
        strict_evaluated_count=summary["all_49"]["strict_evaluated_count"],
        checkpoint="checkpoint_000",
        pair_evaluated_per_hour=manifest["pair_evaluated_per_hour"],
    )
    return decision


def _consensus_report(decision: Mapping[str, Any]) -> str:
    main = dict(decision.get("main_consensus") or {})
    other = dict(decision.get("other_consensus_descriptive") or {})
    return f"""# Crypto 4h Two-Axis Family-Consensus Development Gate

- Status: `{decision['status']}`
- Producer source: `{decision['producer_source_sha']}`
- Interval: `2026-07-18T00:00:00Z` to `2026-08-01T00:00:00Z`
- Contract: fixed 23-member main family and fixed 12-member descriptive group; equal coefficients; identical common support for primary/A/B; aggregate executable weights are evaluated with the existing Binance target, 4h horizon, and 5 bps cost.
- Boundary: second-stage development-fresh evidence only. This is not OOS, promotion, or proof of a common causal mechanism.

## Main 23-member consensus

- Common support hours: `{main.get('common_support_hours')}`
- Left/right incremental net mean: `{main.get('left_incremental_net_mean')}` / `{main.get('right_incremental_net_mean')}`
- Left/right incremental net-LCB: `{main.get('left_incremental_net_lcb')}` / `{main.get('right_incremental_net_lcb')}`
- Both matched axes net-positive: `{main.get('both_axis_net_mean_positive')}`
- Both matched axes net-LCB-positive: `{main.get('both_axis_net_lcb_positive')}`
- Dual-axis strict matched-positive: `{main.get('dual_axis_matched_positive')}`
- Interpretation: `{decision.get('main_interpretation')}`

## Other 12-member descriptive consensus

- Common support hours: `{other.get('common_support_hours')}`
- Both matched axes net-positive: `{other.get('both_axis_net_mean_positive')}`
- Both matched axes net-LCB-positive: `{other.get('both_axis_net_lcb_positive')}`

The 12-member group is descriptive only because membership and statistical power are not matched to the main group. No candidate, family, arm, or ensemble is qualified or promoted by this report.
"""


def run_consensus_gate(
    repo_root: Path,
    *,
    runtime_date: str = CONSENSUS_DEFAULT_RUNTIME_DATE,
    producer_source_sha: str | None = None,
    receipt_path: str = CONSENSUS_RECEIPT_PATH,
) -> dict[str, Any]:
    """Evaluate the exact frozen members once and recompute ensemble economics."""

    root = Path(repo_root)
    receipt = load_consensus_receipt(
        root, require_authorized=True, receipt_path=receipt_path
    )
    observed_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()
    source_sha = str(producer_source_sha or observed_sha).lower()
    if (
        source_sha != observed_sha
        or source_sha != str(receipt["source_implementation_sha"]).lower()
    ):
        raise RuntimeError("FAMILY_CONSENSUS_PRODUCER_SHA_CHANGED")
    runtime_root = root / "runtime" / f"{CONSENSUS_RUNTIME_PREFIX}_{runtime_date}"
    if (runtime_root / "run_manifest.json").exists():
        raise RuntimeError("FAMILY_CONSENSUS_GATE_ALREADY_TERMINAL")
    grouped = select_consensus_cohort(root, receipt=receipt)
    selected = [*grouped["main"], *grouped["other"]]
    selection = json.loads(
        (runtime_root / "behavior_family_selection_receipt.json").read_text(
            encoding="utf-8"
        )
    )
    saved_selection = str(selection.pop("receipt_sha256", ""))
    if (
        _canonical_sha256(selection) != saved_selection
        or selection.get("market_payload_read") is not False
        or str(selection.get("producer_source_sha")) != source_sha
    ):
        raise RuntimeError("FAMILY_CONSENSUS_SELECTION_RECEIPT_CHANGED")
    frozen = json.loads((runtime_root / "frozen_contract.json").read_text(encoding="utf-8"))
    saved_frozen = str(frozen.pop("frozen_contract_sha256", ""))
    if (
        _canonical_sha256(frozen) != saved_frozen
        or frozen.get("market_payload_read") is not False
        or str(frozen.get("producer_source_sha")) != source_sha
    ):
        raise RuntimeError("FAMILY_CONSENSUS_FROZEN_CONTRACT_CHANGED")
    carrier_manifest = json.loads(
        (runtime_root / "aligned_carrier_manifest.json").read_text(encoding="utf-8")
    )
    saved_carrier = str(carrier_manifest.pop("manifest_sha256", ""))
    if (
        _canonical_sha256(carrier_manifest) != saved_carrier
        or str(carrier_manifest.get("selection_receipt_sha256")) != saved_selection
        or int(carrier_manifest.get("field_count", -1)) != 115
    ):
        raise RuntimeError("FAMILY_CONSENSUS_CARRIER_MANIFEST_CHANGED")
    contract_rows = list(carrier_manifest["contracts"])
    static = sweep_v24_static_constructibility(
        selected_rows=selected, contract_rows=contract_rows
    )
    if int(static["candidate_count"]) != 35:
        raise RuntimeError("FAMILY_CONSENSUS_STATIC_COUNT_CHANGED")
    carrier = dict(receipt["carrier"])
    cache_root = root / str(carrier["extended_aligned_cache"])
    target_root = root / str(carrier["target_cache"])
    target_metadata = json.loads((target_root / "metadata.json").read_text(encoding="utf-8"))
    if (
        str(carrier_manifest["extended_aligned_cache"]["identity_sha256"])
        != str(json.loads((cache_root / "metadata.json").read_text(encoding="utf-8"))["identity_sha256"])
        or str(carrier_manifest["target_cache"]["identity_sha256"])
        != str(target_metadata["identity_sha256"])
    ):
        raise RuntimeError("FAMILY_CONSENSUS_CARRIER_OR_TARGET_CHANGED")
    economic = _build_consensus_economic_context(
        root,
        receipt=receipt,
        target_identity_sha256=str(target_metadata["identity_sha256"]),
        receipt_path=receipt_path,
    )
    interval = dict(receipt["development_fresh_interval"])
    started = time.perf_counter()
    active_workers = int(receipt["compute"]["workers_default"])
    memory_fallback_used = False

    def write_status(status: str, **extra: Any) -> None:
        _write_json(
            runtime_root / "producer_status.json",
            {
                "schema_version": 1,
                "status": status,
                "producer_pid": os.getpid(),
                "producer_source_sha": source_sha,
                "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "source_candidate_count": 35,
                "workers": active_workers,
                "memory_fallback_used": memory_fallback_used,
                "active_wall_seconds": time.perf_counter() - started,
                "market_payload_read_after_selection_freeze": True,
                "candidate_generation_performed": False,
                "optimizer_feedback_written": False,
                "archive_written": False,
                "holdout_read_count": 0,
                **extra,
            },
        )

    def make_executor(workers: int) -> concurrent.futures.ProcessPoolExecutor:
        return concurrent.futures.ProcessPoolExecutor(
            max_workers=workers,
            initializer=_v24_worker_initialize,
            initargs=(
                str(cache_root),
                str(target_root),
                contract_rows,
                economic,
                str(interval["start"]),
                str(interval["end_exclusive"]),
                str(interval["role"]),
            ),
        )

    write_status("FAMILY_CONSENSUS_GATE_RUNNING", completed_candidate_count=0)
    payloads = [
        {
            "candidate": row["candidate"],
            "frozen_train_orientation": float(row["train_orientation"]),
        }
        for row in selected
    ]
    with make_executor(active_workers) as executor:
        workers = list(executor.map(_v24_worker_evaluate, payloads, chunksize=1))
    memory_indexes = [
        index for index, row in enumerate(workers) if bool(row.get("memory_error"))
    ]
    if memory_indexes:
        memory_fallback_used = True
        active_workers = int(receipt["compute"]["workers_fallback"])
        with make_executor(active_workers) as executor:
            retried = list(
                executor.map(
                    _v24_worker_evaluate,
                    [payloads[index] for index in memory_indexes],
                    chunksize=1,
                )
            )
        for index, row in zip(memory_indexes, retried):
            workers[index] = row
    if any(bool(row.get("memory_error")) for row in workers):
        write_status("ENGINE_BUDGET_EXHAUSTED_MEMORY", completed_candidate_count=0)
        raise RuntimeError("FAMILY_CONSENSUS_MEMORY_FALLBACK_EXHAUSTED")
    checkpoint_root = runtime_root / "checkpoints"
    temporary = checkpoint_root / f"checkpoint_000.tmp-{os.getpid()}"
    final_checkpoint = checkpoint_root / "checkpoint_000"
    temporary.mkdir(parents=True)
    projections = _v24_write_batch_projections(
        temporary,
        base_ordinal=0,
        selected_rows=selected,
        worker_rows=workers,
        economic_receipt_sha256=str(economic["receipt_sha256"]),
        persist_candidate_local_failures=True,
    )
    ledger_rows = []
    for index, projection in enumerate(projections):
        local = _augment_projection(
            projection, selected=selected[index], worker=workers[index]
        )
        local["consensus_group"] = str(selected[index]["consensus_group"])
        local["fixed_coefficient"] = (
            1.0 / 23.0
            if local["consensus_group"] == "main"
            else 1.0 / 12.0
        )
        ledger_rows.append(local)
    pd.DataFrame(ledger_rows).to_parquet(
        temporary / "candidate_ledger.parquet", index=False
    )
    local_failures = [
        {
            "candidate_id": str(worker["candidate_id"]),
            "error": str(worker.get("error")),
            "consensus_group": str(selected[index]["consensus_group"]),
        }
        for index, worker in enumerate(workers)
        if worker.get("error")
    ]
    checkpoint_manifest = {
        "schema_version": 1,
        "checkpoint": "checkpoint_000",
        "producer_source_sha": source_sha,
        "frozen_contract_sha256": saved_frozen,
        "selection_receipt_sha256": saved_selection,
        "completed_candidate_count": 35,
        "strict_evaluated_count": 35 - len(local_failures),
        "candidate_local_failure_count": len(local_failures),
        "workers": active_workers,
        "memory_fallback_used": memory_fallback_used,
        "files": _v24_checkpoint_files(temporary),
    }
    checkpoint_manifest["manifest_sha256"] = _canonical_sha256(checkpoint_manifest)
    _write_json(temporary / "manifest.json", checkpoint_manifest)
    os.replace(temporary, final_checkpoint)
    ledger_path = runtime_root / "candidate_ledger.parquet"
    shutil.copy2(final_checkpoint / "candidate_ledger.parquet", ledger_path)
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    report_path = reports / f"CRYPTO_SEARCH_FAMILY_CONSENSUS_DEV_V1_{runtime_date}.md"
    result_files: list[Path] = [ledger_path, final_checkpoint / "manifest.json"]
    if local_failures:
        decision: dict[str, Any] = {
            "schema_version": 1,
            "status": "FAMILY_CONSENSUS_FIXED_MEMBER_FAILURE",
            "producer_source_sha": source_sha,
            "fixed_member_failure_count": len(local_failures),
            "fixed_member_failures": local_failures,
            "main_consensus": {},
            "other_consensus_descriptive": {},
            "main_interpretation": "NOT_COMPUTED_FIXED_COHORT_INCOMPLETE",
            "oos": False,
            "promotion_authorized": False,
            "automatic_expansion": False,
        }
    else:
        from alphafactory_crypto.broad_search.replay_v14_binance_target import (
            BinanceTargetStore,
        )
        from alphafactory_crypto.broad_search.runner18m import RawPanelStore

        target_store = BinanceTargetStore(RawPanelStore.open(cache_root), target_root)
        time_slice = target_store.block_slice(
            str(interval["start"]), str(interval["end_exclusive"])
        )
        target = np.asarray(target_store.target_return(4)[:, time_slice], dtype=float)
        worker_lookup = {str(row["candidate_id"]): row for row in workers}
        aggregated = {
            group: _aggregate_consensus_group(
                group=group,
                rows=grouped[group],
                workers=[worker_lookup[str(row["candidate_id"])] for row in grouped[group]],
                target=target,
            )
            for group in ("main", "other")
        }
        tables = {
            "consensus_metrics.parquet": [
                row for group in aggregated.values() for row in group["metric_rows"]
            ],
            "consensus_hourly_paths.parquet": [
                row for group in aggregated.values() for row in group["hourly_rows"]
            ],
            "consensus_asset_weights.parquet": [
                row for group in aggregated.values() for row in group["asset_rows"]
            ],
            "candidate_influence.parquet": [
                row for group in aggregated.values() for row in group["influence_rows"]
            ],
            "consensus_concentration.parquet": [
                row
                for group in aggregated.values()
                for row in group["concentration_rows"]
            ],
        }
        for name, table_rows in tables.items():
            path = runtime_root / name
            pd.DataFrame(table_rows).to_parquet(path, index=False)
            result_files.append(path)
        main_summary = dict(aggregated["main"]["summary"])
        other_summary = dict(aggregated["other"]["summary"])
        if main_summary["both_axis_net_lcb_positive"]:
            interpretation = "FAMILY_ENSEMBLE_TRANSFER_OBSERVED_DEVELOPMENT_ONLY"
        elif main_summary["both_axis_net_mean_positive"]:
            interpretation = "THIN_FAMILY_EFFECT_NOT_STATISTICALLY_QUALIFIED"
        else:
            interpretation = "FAMILY_CONSENSUS_DID_NOT_TRANSFER"
        decision = {
            "schema_version": 1,
            "status": "FAMILY_CONSENSUS_GATE_COMPLETE",
            "producer_source_sha": source_sha,
            "main_consensus": main_summary,
            "other_consensus_descriptive": other_summary,
            "main_interpretation": interpretation,
            "comparison_role": "OTHER_12_DESCRIPTIVE_ONLY_NOT_FAIR_PRIMARY_COMPARATOR",
            "common_mechanism_claim_authorized": False,
            "oos": False,
            "promotion_authorized": False,
            "automatic_expansion": False,
        }
    decision_path = runtime_root / "final_decision.json"
    _write_json(decision_path, decision)
    report_path.write_text(_consensus_report(decision), encoding="utf-8")
    result_files.extend((decision_path, report_path))
    elapsed = time.perf_counter() - started
    manifest = {
        "schema_version": 1,
        "status": str(decision["status"]),
        "producer_source_sha": source_sha,
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "report": str(report_path.relative_to(root).as_posix()),
        "run_receipt_sha256": _file_sha256(root / str(receipt_path)),
        "selection_receipt_sha256": saved_selection,
        "frozen_contract_sha256": saved_frozen,
        "carrier_manifest_sha256": saved_carrier,
        "candidate_count": 35,
        "strict_evaluated_count": 35 - len(local_failures),
        "candidate_local_failure_count": len(local_failures),
        "active_wall_seconds": elapsed,
        "pair_evaluated_per_hour": (
            (35 - len(local_failures)) * 3600.0 / elapsed if elapsed > 0 else 0.0
        ),
        "workers": active_workers,
        "memory_fallback_used": memory_fallback_used,
        "checkpoint_count": 1,
        "market_payload_read_after_selection_freeze": True,
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "holdout_read_count": 0,
        "oos": False,
        "promotion_authorized": False,
        "files": [
            {
                "path": str(path.relative_to(root).as_posix()),
                "bytes": path.stat().st_size,
                "sha256": _file_sha256(path),
            }
            for path in result_files
        ],
    }
    manifest["bundle_sha256"] = _canonical_sha256(manifest)
    _write_json(runtime_root / "run_manifest.json", manifest)
    write_status(
        str(decision["status"]),
        completed_candidate_count=35,
        strict_evaluated_count=35 - len(local_failures),
        checkpoint="checkpoint_000",
        pair_evaluated_per_hour=manifest["pair_evaluated_per_hour"],
    )
    return decision


def check_consensus_gate(
    repo_root: Path,
    *,
    runtime_date: str = CONSENSUS_DEFAULT_RUNTIME_DATE,
    receipt_path: str = CONSENSUS_RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_consensus_receipt(root, receipt_path=receipt_path)
    runtime_root = root / "runtime" / f"{CONSENSUS_RUNTIME_PREFIX}_{runtime_date}"
    errors: list[str] = []
    try:
        grouped = select_consensus_cohort(root, receipt=receipt)
        expected_ids = {
            str(row["candidate_id"])
            for group in grouped.values()
            for row in group
        }
        selection = json.loads(
            (runtime_root / "behavior_family_selection_receipt.json").read_text(
                encoding="utf-8"
            )
        )
        saved_selection = str(selection.pop("receipt_sha256", ""))
        if (
            _canonical_sha256(selection) != saved_selection
            or selection.get("market_payload_read") is not False
        ):
            errors.append("selection_receipt")
        ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
        if (
            len(ledger) != 35
            or ledger["candidate_id"].nunique() != 35
            or set(ledger["candidate_id"].astype(str)) != expected_ids
        ):
            errors.append("candidate_ledger_identity")
        if ledger["candidate_generation_performed"].any():
            errors.append("candidate_generation")
        if ledger["optimizer_feedback_written"].any() or ledger["archive_written"].any():
            errors.append("feedback_or_archive")
        checkpoint = runtime_root / "checkpoints" / "checkpoint_000"
        checkpoint_manifest = json.loads(
            (checkpoint / "manifest.json").read_text(encoding="utf-8")
        )
        saved_checkpoint = str(checkpoint_manifest.pop("manifest_sha256", ""))
        if (
            _canonical_sha256(checkpoint_manifest) != saved_checkpoint
            or checkpoint_manifest["files"] != _v24_checkpoint_files(checkpoint)
        ):
            errors.append("checkpoint_restore")
        decision = json.loads(
            (runtime_root / "final_decision.json").read_text(encoding="utf-8")
        )
        if decision["status"] == "FAMILY_CONSENSUS_GATE_COMPLETE":
            metrics = pd.read_parquet(runtime_root / "consensus_metrics.parquet")
            influence = pd.read_parquet(runtime_root / "candidate_influence.parquet")
            concentration = pd.read_parquet(
                runtime_root / "consensus_concentration.parquet"
            )
            if (
                set(metrics["consensus_group"].astype(str)) != {"main", "other"}
                or set(metrics["sleeve"].astype(str))
                != {
                    "primary",
                    "control_left",
                    "control_right",
                    "primary_minus_left_control",
                    "primary_minus_right_control",
                }
                or influence["target_used"].any()
                or len(concentration) != 10
                or int(decision["main_consensus"]["member_count"]) != 23
                or int(decision["other_consensus_descriptive"]["member_count"]) != 12
            ):
                errors.append("consensus_artifacts")
        elif decision["status"] != "FAMILY_CONSENSUS_FIXED_MEMBER_FAILURE":
            errors.append("terminal_status")
        run_manifest = json.loads(
            (runtime_root / "run_manifest.json").read_text(encoding="utf-8")
        )
        saved_bundle = str(run_manifest.pop("bundle_sha256", ""))
        if _canonical_sha256(run_manifest) != saved_bundle:
            errors.append("run_manifest_hash")
        for item in run_manifest["files"]:
            path = root / str(item["path"])
            if (
                not path.is_file()
                or path.stat().st_size != int(item["bytes"])
                or _file_sha256(path) != str(item["sha256"])
            ):
                errors.append("run_manifest_file:" + str(item["path"]))
        if (
            run_manifest["candidate_generation_performed"]
            or run_manifest["optimizer_feedback_written"]
            or run_manifest["archive_written"]
            or int(run_manifest["holdout_read_count"]) != 0
            or run_manifest["oos"]
            or run_manifest["promotion_authorized"]
        ):
            errors.append("boundary")
    except Exception as exc:
        errors.append(f"{type(exc).__name__}:{exc}")
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "checked_utc": pd.Timestamp.now(tz="UTC").isoformat(),
    }
    _write_json(runtime_root / "independent_checker.json", result)
    return result


def check_validation(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_validation_receipt(root, receipt_path=receipt_path)
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    errors: list[str] = []
    try:
        selected = select_final_positive_champions(root, receipt=receipt)
        selection = json.loads(
            (runtime_root / "behavior_family_selection_receipt.json").read_text(
                encoding="utf-8"
            )
        )
        saved = str(selection.pop("receipt_sha256", ""))
        if _canonical_sha256(selection) != saved:
            errors.append("selection_receipt_hash")
        ledger = pd.read_parquet(runtime_root / "candidate_ledger.parquet")
        if len(ledger) != 49 or ledger["candidate_id"].nunique() != 49:
            errors.append("ledger_count")
        if set(ledger["candidate_id"].astype(str)) != {
            str(row["candidate_id"]) for row in selected
        }:
            errors.append("candidate_identity")
        if not ledger["completion_ordinal"].tolist() == list(range(1, 50)):
            errors.append("completion_ordinal")
        if ledger["candidate_generation_performed"].any():
            errors.append("candidate_generation")
        if ledger["optimizer_feedback_written"].any():
            errors.append("optimizer_feedback")
        if ledger["archive_written"].any():
            errors.append("archive_write")
        strict = ledger.loc[ledger["strict_evaluated"].eq(True)]
        if strict["validation_search_reward"].isna().any():
            errors.append("validation_reward_missing")
        checkpoint = runtime_root / "checkpoints" / "checkpoint_000"
        manifest = json.loads((checkpoint / "manifest.json").read_text(encoding="utf-8"))
        saved_manifest = str(manifest.pop("manifest_sha256", ""))
        if (
            _canonical_sha256(manifest) != saved_manifest
            or manifest["files"] != _v24_checkpoint_files(checkpoint)
        ):
            errors.append("checkpoint_restore")
        run_manifest = json.loads(
            (runtime_root / "run_manifest.json").read_text(encoding="utf-8")
        )
        saved_bundle = str(run_manifest.pop("bundle_sha256", ""))
        if _canonical_sha256(run_manifest) != saved_bundle:
            errors.append("run_manifest_hash")
        for item in run_manifest["files"]:
            path = root / str(item["path"])
            if (
                not path.is_file()
                or path.stat().st_size != int(item["bytes"])
                or _file_sha256(path) != str(item["sha256"])
            ):
                errors.append("run_manifest_file:" + str(item["path"]))
        if (
            run_manifest["candidate_generation_performed"]
            or run_manifest["optimizer_feedback_written"]
            or run_manifest["archive_written"]
            or int(run_manifest["holdout_read_count"]) != 0
            or run_manifest["oos"]
            or run_manifest["promotion_authorized"]
        ):
            errors.append("boundary")
    except Exception as exc:  # independent checker must report, not conceal
        errors.append(f"{type(exc).__name__}:{exc}")
    result = {
        "schema_version": 1,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "runtime": str(runtime_root.relative_to(root).as_posix()),
        "checked_utc": pd.Timestamp.now(tz="UTC").isoformat(),
    }
    _write_json(runtime_root / "independent_checker.json", result)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=(
            "run",
            "check",
            "select",
            "select-consensus",
            "freeze-consensus",
            "prepare-consensus-carrier",
            "run-consensus",
            "check-consensus",
        ),
    )
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--runtime-date", default=DEFAULT_RUNTIME_DATE)
    parser.add_argument("--producer-source-sha")
    parser.add_argument("--receipt-path")
    parser.add_argument("--new-oi-source-root", type=Path)
    parser.add_argument("--old-aligned-cache", type=Path)
    parser.add_argument("--v24-aligned-cache", type=Path)
    parser.add_argument("--top100-tar", type=Path)
    parser.add_argument("--ranks101-200-tar", type=Path)
    args = parser.parse_args(argv)
    is_consensus = args.command.endswith("consensus") or args.command == (
        "prepare-consensus-carrier"
    )
    receipt_path = str(
        args.receipt_path
        or (CONSENSUS_RECEIPT_PATH if is_consensus else RECEIPT_PATH)
    )
    if args.command == "select-consensus":
        receipt = load_consensus_receipt(
            args.repo_root, receipt_path=receipt_path
        )
        grouped = select_consensus_cohort(args.repo_root, receipt=receipt)
        print(
            json.dumps(
                {
                    "main_candidate_count": len(grouped["main"]),
                    "other_candidate_count": len(grouped["other"]),
                    "main_candidate_ids_sha256": _line_sha256(
                        [row["candidate_id"] for row in grouped["main"]]
                    ),
                    "other_candidate_ids_sha256": _line_sha256(
                        [row["candidate_id"] for row in grouped["other"]]
                    ),
                },
                sort_keys=True,
            )
        )
        return 0
    if args.command == "freeze-consensus":
        result = freeze_consensus_run(
            args.repo_root,
            runtime_date=args.runtime_date,
            producer_source_sha=args.producer_source_sha,
            receipt_path=receipt_path,
        )
        print(json.dumps(result, sort_keys=True, default=str))
        return 0
    if args.command == "prepare-consensus-carrier":
        required_paths = {
            "new_oi_source_root": args.new_oi_source_root,
            "old_aligned_cache": args.old_aligned_cache,
            "v24_aligned_cache": args.v24_aligned_cache,
            "top100_tar": args.top100_tar,
            "ranks101_200_tar": args.ranks101_200_tar,
        }
        missing = [name for name, value in required_paths.items() if value is None]
        if missing:
            parser.error("missing required carrier paths: " + ",".join(missing))
        result = prepare_consensus_carrier(
            args.repo_root,
            new_oi_source_root=Path(args.new_oi_source_root),
            old_aligned_cache=Path(args.old_aligned_cache),
            v24_aligned_cache=Path(args.v24_aligned_cache),
            top100_tar=Path(args.top100_tar),
            ranks101_200_tar=Path(args.ranks101_200_tar),
            runtime_date=args.runtime_date,
            producer_source_sha=args.producer_source_sha,
            receipt_path=receipt_path,
        )
        print(json.dumps(result, sort_keys=True, default=str))
        return 0
    if args.command == "run-consensus":
        result = run_consensus_gate(
            args.repo_root,
            runtime_date=args.runtime_date,
            producer_source_sha=args.producer_source_sha,
            receipt_path=receipt_path,
        )
        print(json.dumps(result, sort_keys=True, default=str))
        return 0
    if args.command == "check-consensus":
        result = check_consensus_gate(
            args.repo_root,
            runtime_date=args.runtime_date,
            receipt_path=receipt_path,
        )
        print(json.dumps(result, sort_keys=True, default=str))
        return 0 if result.get("status") == "PASS" else 1
    if args.command == "select":
        receipt = load_validation_receipt(
            args.repo_root, receipt_path=receipt_path
        )
        rows = select_final_positive_champions(args.repo_root, receipt=receipt)
        print(json.dumps({"candidate_count": len(rows), "selection_sha256": _canonical_sha256(_selection_projection(rows))}, sort_keys=True))
        return 0
    if args.command == "run":
        result = run_validation(
            args.repo_root,
            runtime_date=args.runtime_date,
            producer_source_sha=args.producer_source_sha,
            receipt_path=receipt_path,
        )
    else:
        result = check_validation(
            args.repo_root,
            runtime_date=args.runtime_date,
            receipt_path=receipt_path,
        )
    print(json.dumps(result, sort_keys=True, default=str))
    return 0 if result.get("status") != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
