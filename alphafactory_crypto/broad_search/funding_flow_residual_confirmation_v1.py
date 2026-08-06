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
import psutil

from alphafactory_crypto.broad_search.compositional18m import (
    CandidateSpec,
    TypedExpressionRegistry,
    _payload_sha,
    compile_mechanism_catalog,
    mapping_id_for_mechanism_spec,
    operator_path,
)
from alphafactory_crypto.broad_search.expression import Expression, ablate_expression
from alphafactory_crypto.broad_search.experiment_authority import (
    resolve_search_economic_receipt,
)
from alphafactory_crypto.broad_search.pair18m import (
    ControlBehaviorDegeneracyError,
    evaluate_pair,
)
from alphafactory_crypto.broad_search.replay_v14_binance_target import (
    BinanceTargetStore,
)
from alphafactory_crypto.broad_search.runner18m import (
    RawPanelStore,
    _contracts_from_payload,
)
from alphafactory_crypto.broad_search.panel18m import infer_family


RECEIPT_PATH = "config/crypto_funding_flow_residual_nested_confirmation_v1_receipt.json"
CONTRACT_PATH = "config/crypto_funding_flow_residual_nested_confirmation_v1.json"
DEFAULT_RUNTIME_DATE = "20260806"
RUNTIME_PREFIX = "crypto_funding_flow_residual_nested_confirmation_v1"
REPORT_PREFIX = "CRYPTO_FUNDING_FLOW_RESIDUAL_NESTED_CONFIRMATION_V1"

_WORKER_STORE: Any | None = None
_WORKER_REGISTRY: TypedExpressionRegistry | None = None
_WORKER_ECONOMIC: Mapping[str, Any] | None = None
_WORKER_START = ""
_WORKER_END = ""
_WORKER_ROLE = ""
_WORKER_BLOCK_CONTRACT: Mapping[str, Any] | None = None


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest().upper()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def load_confirmation_receipt(
    repo_root: Path,
    *,
    receipt_path: str = RECEIPT_PATH,
    require_authorized: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = _load_json(root / receipt_path)
    contract = _load_json(root / str(receipt["contract"]["path"]))
    errors: list[str] = []
    if receipt.get("receipt_id") != "CRYPTO_FUNDING_FLOW_RESIDUAL_NESTED_CONFIRMATION_V1_RECEIPT":
        errors.append("receipt_id")
    if require_authorized and receipt.get("run_authorized") is not True:
        errors.append("run_authorized")
    authorization = dict(receipt.get("run_authorization") or {})
    if (
        authorization.get("authority") != "CURRENT_USER_INSTRUCTION"
        or authorization.get("contaminated_interval_reuse_authorized") is not True
        or authorization.get("unread_migration_claim_allowed") is not False
        or authorization.get("oos_allowed") is not False
        or authorization.get("second_run_allowed") is not False
    ):
        errors.append("authorization_boundary")
    if contract.get("evidence_status") != (
        "REUSED_DEVELOPMENT_VALIDATION_ADAPTIVE_DIAGNOSTIC_ONLY"
    ):
        errors.append("evidence_status")
    if contract.get("source_deviation", {}).get("action") != (
        "USE_ONLY_EXISTING_BYBIT_HYPERLIQUID_OKX_FIELDS_NO_NEW_FIELD"
    ):
        errors.append("source_deviation")
    ledger = root / str(receipt["source_evidence"]["r3_candidate_ledger_path"])
    if not ledger.is_file() or _file_sha256(ledger) != str(
        receipt["source_evidence"]["r3_candidate_ledger_sha256"]
    ):
        errors.append("r3_candidate_ledger_path")
    for key, hash_key in (
        ("carrier_manifest_path", "carrier_manifest_canonical_sha256"),
        ("economic_receipt_path", "economic_receipt_canonical_sha256"),
        ("mechanism_catalog_path", "mechanism_catalog_canonical_sha256"),
        ("target_contract_path", "target_contract_canonical_sha256"),
        (
            "prior_validation_contract_path",
            "prior_validation_contract_canonical_sha256",
        ),
    ):
        relative = str(receipt["source_evidence"][key])
        path = root / relative
        if not path.is_file() or _canonical_sha256(_load_json(path)) != str(
            receipt["source_evidence"][hash_key]
        ):
            errors.append(key)
    if errors:
        raise RuntimeError("FUNDING_FLOW_CONFIRMATION_RECEIPT_BLOCKED:" + ",".join(errors))
    return {**receipt, "_contract": contract, "_receipt_path": receipt_path}


def _load_anchor(root: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    source = dict(receipt["source_evidence"])
    anchor_id = str(source["anchor_candidate_id"])
    frame = pd.read_parquet(
        root / str(source["r3_candidate_ledger_path"]),
        filters=[("candidate_id", "==", anchor_id)],
    )
    direct = frame.loc[frame["candidate_id"].astype(str).eq(anchor_id)]
    if len(direct) != 1:
        raise RuntimeError("FUNDING_FLOW_ANCHOR_ROW_NOT_UNIQUE")
    row = direct.iloc[0].to_dict()
    candidate = CandidateSpec.from_dict(json.loads(str(row["candidate_spec_json"])))
    if (
        candidate.candidate_id != anchor_id
        or str(row["candidate_spec_sha256"]) != str(source["anchor_candidate_spec_sha256"])
        or _canonical_sha256(candidate.to_dict()) != str(source["anchor_candidate_spec_sha256"])
        or str(row["behavior_family_id"]) != str(source["anchor_behavior_family_id"])
        or float(row["train_orientation"]) != float(source["anchor_train_orientation"])
        or bool(row["matched_positive"]) is not True
    ):
        raise RuntimeError("FUNDING_FLOW_ANCHOR_IDENTITY_CHANGED")
    return {**row, "candidate": candidate}


def _load_grid_inputs(
    root: Path,
    receipt: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[Mapping[str, Any], ...], TypedExpressionRegistry, Any]:
    source = dict(receipt["source_evidence"])
    manifest = _load_json(root / str(source["carrier_manifest_path"]))
    contracts = tuple(dict(row) for row in manifest["contracts"])
    if (
        len(contracts) != int(receipt["carrier"]["field_count"])
        or str(manifest["cache_identity_sha256"])
        != str(receipt["source_evidence"]["carrier_cache_identity_sha256"])
    ):
        raise RuntimeError("FUNDING_FLOW_CARRIER_IDENTITY_CHANGED")
    registry = TypedExpressionRegistry(_contracts_from_payload(contracts))
    catalog = _load_json(root / str(source["mechanism_catalog_path"]))
    specs = [
        spec
        for spec in compile_mechanism_catalog(catalog)
        if spec.template_id == "FUNDING_FLOW_CROWDING"
        and spec.payload_operator == "Residual"
        and spec.condition_role is None
    ]
    if len(specs) != 1:
        raise RuntimeError("FUNDING_FLOW_RESIDUAL_MECHANISM_NOT_UNIQUE")
    return manifest, contracts, registry, specs[0]


def _genes(spec: Any, *, funding_field: str, funding_window: int, flow_window: int, beta: float) -> dict[str, Any]:
    return {
        "mechanism_id": spec.mechanism_id,
        "mechanism_spec": spec.to_dict(),
        "left_field": str(funding_field),
        "left_auxiliary_field": "",
        "right_field": "signed_aggressor_notional",
        "right_auxiliary_field": "",
        "condition_field": "",
        "condition_auxiliary_field": "",
        "left_window": int(funding_window),
        "right_window": int(flow_window),
        "condition_window": 720,
        "left_normalizer": "VolatilityScale",
        "right_normalizer": "VolatilityScale",
        "condition_normalizer": "RollingZScore",
        "beta": float(beta),
        "horizon_hours": 4,
        "matched_control_schema": spec.matched_control_schema,
    }


def _deterministic_diagnostic_candidate(
    registry: TypedExpressionRegistry,
    *,
    spec: Any,
    funding_field: str,
    funding_window: int,
    flow_window: int,
    beta: float,
) -> CandidateSpec:
    """Build a frozen diagnostic point without expanding the search grammar.

    The requested 3/96/240-hour windows and beta=0.25 are intentionally not
    members of the generative proposal grammar.  This experiment is a fixed
    curve, not a search, so it constructs the same existing typed AST directly
    and sends it through the canonical registry validation/compiler path.
    """

    genes = _genes(
        spec,
        funding_field=funding_field,
        funding_window=funding_window,
        flow_window=flow_window,
        beta=beta,
    )
    left = Expression(
        "VolatilityScale",
        (Expression("Raw", field_id=str(funding_field)),),
        parameters={"window": int(funding_window)},
    )
    right = Expression(
        "VolatilityScale",
        (Expression("Raw", field_id="signed_aggressor_notional"),),
        parameters={"window": int(flow_window)},
    )
    expression = Expression(
        "Residual",
        (left, right),
        parameters={"beta": float(beta)},
    )
    assurance = registry.validate(expression)
    control = ablate_expression(expression)
    control_assurance = registry.validate(control)
    if set(assurance.raw_fields) != set(control_assurance.raw_fields):
        raise AssertionError("diagnostic matched control changed raw inputs")
    mapping_id = mapping_id_for_mechanism_spec(spec)
    candidate_payload = {
        "mechanism_id": spec.mechanism_id,
        "expression": expression.canonical_dict(),
        "control": control.canonical_dict(),
        "horizon_hours": 4,
        "mapping_id": mapping_id,
    }
    return CandidateSpec(
        _payload_sha(candidate_payload),
        spec.mechanism_id,
        f"MECHANISM_V2_{spec.template_id}",
        expression,
        control,
        4,
        mapping_id,
        assurance.raw_fields,
        tuple(infer_family(field_id) for field_id in assurance.raw_fields),
        assurance.rolling_windows,
        assurance.depth,
        operator_path(expression),
        genes,
    )


def build_frozen_grid(
    repo_root: Path,
    *,
    receipt: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    root = Path(repo_root)
    bound = dict(receipt or load_confirmation_receipt(root))
    contract = dict(bound["_contract"])
    manifest, contracts, registry, spec = _load_grid_inputs(root, bound)
    anchor = _load_anchor(root, bound)
    mechanism = dict(contract["mechanism"])
    rows: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    for funding_field in mechanism["funding_fields"]:
        source_id = str(funding_field).split("__", 1)[0]
        for funding_window in mechanism["funding_windows"]:
            for flow_window in mechanism["flow_windows"]:
                for beta in mechanism["betas"]:
                    main = _deterministic_diagnostic_candidate(
                        registry,
                        spec=spec,
                        funding_field=str(funding_field),
                        funding_window=int(funding_window),
                        flow_window=int(flow_window),
                        beta=float(beta),
                    )
                    placebo = _deterministic_diagnostic_candidate(
                        registry,
                        spec=spec,
                        funding_field=str(funding_field),
                        funding_window=int(flow_window),
                        flow_window=int(funding_window),
                        beta=float(beta),
                    )
                    pair_id = _canonical_sha256(
                        {"main": main.candidate_id, "placebo": placebo.candidate_id}
                    )
                    cell_id = f"{source_id}|{int(funding_window)}|{int(flow_window)}"
                    common = {
                        "pair_id": pair_id,
                        "cell_id": cell_id,
                        "funding_source": source_id,
                        "funding_field": str(funding_field),
                        "funding_window": int(funding_window),
                        "flow_window": int(flow_window),
                        "beta": float(beta),
                    }
                    for candidate_group, candidate in (("main", main), ("placebo", placebo)):
                        rows.append(
                            {
                                **common,
                                "candidate_group": candidate_group,
                                "candidate_id": candidate.candidate_id,
                                "candidate_spec_sha256": _canonical_sha256(candidate.to_dict()),
                                "exact_expression_id": candidate.candidate_id,
                                "canonical_expression_id": candidate.expression.expression_id,
                                "candidate_spec_json": _canonical_json(candidate.to_dict()),
                                "mechanism_family": candidate.mechanism_family,
                                "operator_path": candidate.operator_path,
                                "mapping_id": candidate.mapping_id,
                                "horizon_hours": int(candidate.horizon_hours),
                                "is_anchor": bool(candidate.candidate_id == anchor["candidate_id"]),
                            }
                        )
                    pairs.append(
                        {
                            **common,
                            "main_candidate_id": main.candidate_id,
                            "placebo_candidate_id": placebo.candidate_id,
                        }
                    )
    if (
        len(rows) != 162
        or len(pairs) != 81
        or len({row["candidate_id"] for row in rows}) != 162
        or len({row["pair_id"] for row in pairs}) != 81
    ):
        raise RuntimeError("FUNDING_FLOW_GRID_CARDINALITY_CHANGED")
    anchor_rows = [row for row in rows if row["is_anchor"]]
    if (
        len(anchor_rows) != 1
        or anchor_rows[0]["candidate_group"] != "main"
        or anchor_rows[0]["candidate_spec_sha256"]
        != bound["source_evidence"]["anchor_candidate_spec_sha256"]
    ):
        raise RuntimeError("FUNDING_FLOW_GRID_ANCHOR_CHANGED")
    proof = {
        "schema_version": 1,
        "market_read_performed": False,
        "candidate_count": len(rows),
        "main_count": sum(row["candidate_group"] == "main" for row in rows),
        "placebo_count": sum(row["candidate_group"] == "placebo" for row in rows),
        "pair_count": len(pairs),
        "grid_sha256": _canonical_sha256(rows),
        "pairs_sha256": _canonical_sha256(pairs),
        "contracts_sha256": _canonical_sha256(contracts),
        "carrier_identity_sha256": manifest["cache_identity_sha256"],
        "anchor_candidate_id": anchor_rows[0]["candidate_id"],
    }
    return rows, pairs, proof


def _build_economic_context(
    root: Path,
    receipt: Mapping[str, Any],
    *,
    validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    base = resolve_search_economic_receipt(
        root, str(receipt["source_evidence"]["economic_receipt_path"])
    )
    partitions = {
        key: dict(value)
        for key, value in dict(base["evidence_partition"]).items()
    }
    if validation is not None:
        local = {
            "role": str(validation["role"]),
            "start": str(validation["start"]),
            "end_exclusive": str(validation["end_exclusive"]),
            "optimizer_feedback_allowed": False,
            "policy_memory_write_allowed": False,
            "candidate_generation_allowed": False,
        }
        partitions["validation"] = local
    else:
        local = dict(base["validation"])
    execution = dict(base["execution"])
    execution["target_cache_path"] = str(receipt["carrier"]["target_cache"])
    execution["target_cache_identity_sha256"] = str(
        receipt["carrier"]["target_identity_sha256"]
    )
    return {
        **base,
        "run_authorized": True,
        "run_authorization": dict(receipt["run_authorization"]),
        "evidence_partition": partitions,
        "train": dict(partitions["train"]),
        "validation": local,
        "holdout": dict(partitions["holdout"]),
        "execution": execution,
        "receipt_sha256": _file_sha256(root / str(receipt["_receipt_path"])),
    }


def _worker_initialize(
    cache_root: str,
    target_root: str,
    contract_rows: Sequence[Mapping[str, Any]],
    economic_context: Mapping[str, Any],
    start: str,
    end_exclusive: str,
    role: str,
    block_contract: Mapping[str, Any] | None,
) -> None:
    global _WORKER_STORE, _WORKER_REGISTRY, _WORKER_ECONOMIC
    global _WORKER_START, _WORKER_END, _WORKER_ROLE, _WORKER_BLOCK_CONTRACT
    _WORKER_STORE = BinanceTargetStore(
        RawPanelStore.open(Path(cache_root)), Path(target_root)
    )
    _WORKER_REGISTRY = TypedExpressionRegistry(
        _contracts_from_payload(contract_rows)
    )
    _WORKER_ECONOMIC = dict(economic_context)
    _WORKER_START = str(start)
    _WORKER_END = str(end_exclusive)
    _WORKER_ROLE = str(role)
    _WORKER_BLOCK_CONTRACT = (
        dict(block_contract) if block_contract is not None else None
    )


def _array_sha256(value: np.ndarray) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(str(array.shape).encode("ascii"))
    digest.update(array.tobytes())
    return digest.hexdigest().upper()


def _economic_path_identity(paths: Mapping[str, Any]) -> dict[str, Any]:
    sleeves = {}
    for name, payload in sorted(dict(paths["sleeves"]).items()):
        sleeves[str(name)] = {
            key: _array_sha256(np.asarray(value))
            for key, value in sorted(dict(payload).items())
        }
    body = {
        "candidate_id": paths["candidate_id"],
        "economic_receipt_sha256": paths["economic_receipt_sha256"],
        "asset_ids": list(paths["asset_ids"]),
        "timestamp_ns_sha256": _array_sha256(np.asarray(paths["timestamp_ns"])),
        "sleeves": sleeves,
    }
    return {**body, "identity_sha256": _canonical_sha256(body)}


def _bucket_metrics(gross: np.ndarray, net: np.ndarray, mask: np.ndarray) -> dict[str, Any]:
    valid = np.asarray(mask, dtype=bool) & np.isfinite(gross) & np.isfinite(net)
    return {
        "count": int(valid.sum()),
        "gross_mean": float(np.nanmean(gross[valid])) if np.any(valid) else None,
        "net_mean": float(np.nanmean(net[valid])) if np.any(valid) else None,
    }


def _diagnostic_summary(candidate: CandidateSpec, paths: Mapping[str, Any]) -> dict[str, Any]:
    assert _WORKER_STORE is not None
    timestamp_ns = np.asarray(paths["timestamp_ns"], dtype=np.int64)
    store_timestamps = np.asarray(_WORKER_STORE.timestamp_ns, dtype=np.int64)
    indexes = np.searchsorted(store_timestamps, timestamp_ns)
    if (
        np.any(indexes >= store_timestamps.size)
        or not np.array_equal(store_timestamps[indexes], timestamp_ns)
    ):
        raise RuntimeError("FUNDING_FLOW_DIAGNOSTIC_TIMESTAMP_CHANGED")
    funding = np.asarray(_WORKER_STORE.field(candidate.raw_fields[0])[:, indexes], dtype=float)
    flow = np.asarray(_WORKER_STORE.field(candidate.raw_fields[1])[:, indexes], dtype=float)
    funding_state = np.nanmedian(funding, axis=0)
    flow_state = np.nanmedian(flow, axis=0)
    funding_lag = np.roll(funding_state, 8)
    funding_lag[:8] = np.nan
    primary = dict(paths["sleeves"]["primary"])
    gross = np.asarray(primary["gross"], dtype=float)
    net = np.asarray(primary["net"], dtype=float)
    objective = np.asarray(primary["mask"], dtype=bool)
    same_sign = np.sign(funding_state) == np.sign(flow_state)
    timestamps = pd.to_datetime(timestamp_ns, utc=True)
    buckets = {
        "funding_positive": funding_state > 0.0,
        "funding_negative": funding_state < 0.0,
        "funding_rising_8h": funding_state > funding_lag,
        "funding_falling_8h": funding_state < funding_lag,
        "flow_funding_same_sign": same_sign,
        "flow_funding_divergent_sign": ~same_sign,
        "funding_update_hour_utc_mod_8_zero": np.asarray(timestamps.hour % 8 == 0),
        "non_funding_update_hour": np.asarray(timestamps.hour % 8 != 0),
    }
    asset_contribution = np.asarray(primary["asset_gross_contribution"], dtype=float)
    asset_totals = np.nansum(asset_contribution, axis=1)
    day_frame = pd.DataFrame({"day": timestamps.floor("D"), "gross": gross, "net": net})
    day_totals = day_frame.groupby("day", sort=True)[["gross", "net"]].sum()

    def shares(values: np.ndarray) -> dict[str, float]:
        absolute = np.sort(np.abs(np.asarray(values, dtype=float)))[::-1]
        denominator = float(absolute.sum())
        return {
            f"top_{count}_absolute_share": (
                float(absolute[:count].sum() / denominator) if denominator > 0 else 0.0
            )
            for count in (1, 5, 10)
        }

    weeks = pd.DataFrame(
        {
            "week": timestamps.to_period("W-SUN").astype(str),
            "gross": gross,
            "net": net,
        }
    ).groupby("week", sort=True)[["gross", "net"]].mean()
    return {
        "schema_version": 1,
        "candidate_id": candidate.candidate_id,
        "economic_path_identity": _economic_path_identity(paths),
        "day_concentration": shares(day_totals["gross"].to_numpy()),
        "asset_concentration": shares(asset_totals),
        "regimes": {
            name: _bucket_metrics(gross, net, np.asarray(mask) & objective)
            for name, mask in buckets.items()
        },
        "weekly_subblocks": [
            {
                "week": str(index),
                "gross_mean": float(row["gross"]),
                "net_mean": float(row["net"]),
            }
            for index, row in weeks.iterrows()
        ],
    }


def _worker_evaluate(payload: Mapping[str, Any]) -> dict[str, Any]:
    if _WORKER_STORE is None or _WORKER_REGISTRY is None or _WORKER_ECONOMIC is None:
        raise RuntimeError("FUNDING_FLOW_WORKER_NOT_INITIALIZED")
    candidate = CandidateSpec.from_dict(dict(payload["candidate"]))
    orientation = payload.get("frozen_train_orientation")
    include_paths = bool(payload.get("include_economic_paths"))
    process = psutil.Process(os.getpid())
    started_cpu = time.process_time()
    started_wall = time.perf_counter()
    try:
        evaluation = evaluate_pair(
            store=_WORKER_STORE,
            registry=_WORKER_REGISTRY,
            candidate=candidate,
            block_start=_WORKER_START,
            block_end=_WORKER_END,
            block_role=_WORKER_ROLE,
            behavior_contract=None,
            economic_receipt=_WORKER_ECONOMIC,
            frozen_train_orientation=(
                None if orientation is None else float(orientation)
            ),
            include_economic_paths=include_paths,
            include_control_provenance=True,
            optimizer_block_contract=_WORKER_BLOCK_CONTRACT,
        )
        diagnostics = None
        if include_paths and bool(payload.get("diagnostics")):
            diagnostics = _diagnostic_summary(
                candidate, dict(evaluation["_economic_paths"])
            )
        paths_identity = (
            _economic_path_identity(dict(evaluation["_economic_paths"]))
            if include_paths
            else None
        )
        evaluation.pop("_economic_paths", None)
        error = None
        memory_error = False
    except MemoryError as exc:
        evaluation = None
        diagnostics = None
        paths_identity = None
        error = f"{type(exc).__name__}:{exc}"
        memory_error = True
    except ControlBehaviorDegeneracyError as exc:
        evaluation = None
        diagnostics = None
        paths_identity = None
        error = f"{type(exc).__name__}:{exc}"
        memory_error = False
    except Exception as exc:
        evaluation = None
        diagnostics = None
        paths_identity = None
        error = f"{type(exc).__name__}:{exc}"
        memory_error = False
    memory = process.memory_info()
    return {
        "candidate_id": candidate.candidate_id,
        "evaluation": evaluation,
        "diagnostics": diagnostics,
        "economic_path_identity": paths_identity,
        "error": error,
        "memory_error": memory_error,
        "process_cpu_seconds": time.process_time() - started_cpu,
        "wall_seconds": time.perf_counter() - started_wall,
        "worker_rss_bytes": int(memory.rss),
        "worker_private_bytes": int(getattr(memory, "private", memory.rss)),
    }


def _json_value(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _stage_projection(
    *,
    stage: str,
    ordinal: int,
    selected: Mapping[str, Any],
    worker: Mapping[str, Any],
) -> dict[str, Any]:
    base = {
        key: selected.get(key)
        for key in (
            "pair_id",
            "cell_id",
            "funding_source",
            "funding_field",
            "funding_window",
            "flow_window",
            "beta",
            "candidate_group",
            "candidate_id",
            "candidate_spec_sha256",
            "exact_expression_id",
            "canonical_expression_id",
            "mechanism_family",
            "operator_path",
            "mapping_id",
            "horizon_hours",
            "is_anchor",
            "selection_roles_json",
        )
        if key in selected
    }
    row: dict[str, Any] = {
        **base,
        "stage": str(stage),
        "completion_ordinal": int(ordinal + 1),
        "candidate_spec_json": str(selected["candidate_spec_json"]),
        "strict_evaluated": worker.get("evaluation") is not None,
        "failure_reason": worker.get("error"),
        "process_cpu_seconds": float(worker["process_cpu_seconds"]),
        "wall_seconds": float(worker["wall_seconds"]),
        "worker_rss_bytes": int(worker["worker_rss_bytes"]),
        "worker_private_bytes": int(worker["worker_private_bytes"]),
        "diagnostics_json": (
            _json_value(worker["diagnostics"])
            if worker.get("diagnostics") is not None
            else None
        ),
        "economic_path_identity_json": (
            _json_value(worker["economic_path_identity"])
            if worker.get("economic_path_identity") is not None
            else None
        ),
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "archive_written": False,
        "holdout_read_count": 0,
        "oos_read_count": 0,
    }
    evaluation = worker.get("evaluation")
    if not isinstance(evaluation, Mapping):
        row.update(
            {
                "train_orientation": None,
                "train_orientation_fitted": None,
                "evaluation_partition": None,
                "pair_reward": None,
                "search_reward": None,
                "matched_positive": False,
                "behavior_family_id": None,
                "left_incremental_net_mean": None,
                "right_incremental_net_mean": None,
                "left_incremental_net_lcb": None,
                "right_incremental_net_lcb": None,
                "primary_net_mean": None,
                "primary_net_lcb": None,
                "support_min": None,
                "worst_axis_net": None,
                "block_robust_ordering_json": None,
                "block_robust_ordering_sha256": None,
                "replicated_positive_block_count": None,
                "development_worst_block_min_matched_net": None,
                "development_median_block_matched_net": None,
            }
        )
        return row
    evaluation = dict(evaluation)
    if str(evaluation.get("candidate_id")) != str(selected["candidate_id"]):
        raise RuntimeError("FUNDING_FLOW_EVALUATION_IDENTITY_CHANGED")
    behavior = dict(evaluation.get("behavior") or {})
    realization = dict(evaluation.get("mechanism_realization_provenance") or {})
    block = evaluation.get("block_robust_ordering")
    block_payload = dict(block) if isinstance(block, Mapping) else None
    left = dict(evaluation.get("left_incremental") or {})
    right = dict(evaluation.get("right_incremental") or {})
    primary = dict(evaluation.get("primary") or {})
    audit_sections = {
        "primary": primary,
        "left_control": dict(evaluation.get("left_control") or {}),
        "right_control": dict(evaluation.get("right_control") or {}),
        "left_incremental": left,
        "right_incremental": right,
    }
    for section, metrics in audit_sections.items():
        for metric in (
            "gross_mean",
            "net_mean",
            "net_lcb",
            "net_standard_error",
            "turnover_mean",
            "cost_mean",
            "support",
            "positive_month_fraction",
            "median_month",
            "worst_month",
            "concentration_mean",
        ):
            row[f"{section}_{metric}"] = _finite_float(metrics.get(metric))
        row[f"{section}_month_metrics_json"] = _json_value(
            metrics.get("month_metrics") or []
        )
        row[f"{section}_weight_sha256"] = metrics.get("weight_sha256")
    left_net = _finite_float(left.get("net_mean"))
    right_net = _finite_float(right.get("net_mean"))
    supports = [
        value
        for value in (
            _finite_float(primary.get("support")),
            _finite_float(left.get("support")),
            _finite_float(right.get("support")),
        )
        if value is not None
    ]
    row.update(
        {
            "train_orientation": float(evaluation["train_orientation"]),
            "train_orientation_fitted": bool(evaluation["train_orientation_fitted"]),
            "evaluation_partition": str(evaluation["evaluation_partition"]),
            "pair_reward": float(evaluation["pair_reward"]),
            "search_reward": float(evaluation["search_reward"]),
            "matched_positive": bool(evaluation["matched_positive"]),
            "behavior_family_id": behavior.get("behavior_family_id"),
            "incremental_behavior_id": behavior.get("incremental_behavior_id"),
            "left_incremental_behavior_id": behavior.get(
                "left_incremental_behavior_id"
            ),
            "right_incremental_behavior_id": behavior.get(
                "right_incremental_behavior_id"
            ),
            "mechanism_declared_axis_count": realization.get("declared_axis_count"),
            "mechanism_active_axis_count": realization.get("active_axis_count"),
            "mechanism_realization_status": realization.get("status"),
            "mechanism_realization_json": _json_value(realization),
            "feedback_json": _json_value(evaluation.get("feedback") or {}),
            "search_reward_feedback_json": _json_value(
                evaluation.get("search_reward_feedback") or {}
            ),
            "support_min": min(supports) if supports else None,
            "worst_axis_net": (
                min(left_net, right_net)
                if left_net is not None and right_net is not None
                else None
            ),
            "block_robust_ordering_json": (
                _json_value(block_payload) if block_payload is not None else None
            ),
            "block_robust_ordering_sha256": (
                block_payload.get("ordering_sha256")
                if block_payload is not None
                else None
            ),
            "replicated_positive_block_count": (
                block_payload.get("replicated_positive_block_count")
                if block_payload is not None
                else None
            ),
            "development_worst_block_min_matched_net": (
                _finite_float(block_payload.get("worst_block_min_matched_net_mean"))
                if block_payload is not None
                else None
            ),
            "development_median_block_matched_net": (
                _finite_float(block_payload.get("median_block_min_matched_net_mean"))
                if block_payload is not None
                else None
            ),
        }
    )
    return row


def _make_executor(
    *,
    workers: int,
    cache_root: Path,
    target_root: Path,
    contracts: Sequence[Mapping[str, Any]],
    economic: Mapping[str, Any],
    start: str,
    end_exclusive: str,
    role: str,
    block_contract: Mapping[str, Any] | None,
) -> concurrent.futures.ProcessPoolExecutor:
    return concurrent.futures.ProcessPoolExecutor(
        max_workers=int(workers),
        initializer=_worker_initialize,
        initargs=(
            str(cache_root),
            str(target_root),
            list(contracts),
            dict(economic),
            str(start),
            str(end_exclusive),
            str(role),
            dict(block_contract) if block_contract is not None else None,
        ),
    )


def _evaluate_stage(
    *,
    stage: str,
    selected_rows: Sequence[Mapping[str, Any]],
    cache_root: Path,
    target_root: Path,
    contracts: Sequence[Mapping[str, Any]],
    economic: Mapping[str, Any],
    start: str,
    end_exclusive: str,
    role: str,
    block_contract: Mapping[str, Any] | None,
    workers_default: int,
    workers_fallback: int,
    wall_time_seconds_maximum: float,
    diagnostic_candidate_ids: set[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    started = time.perf_counter()
    payloads = []
    diagnostics = diagnostic_candidate_ids or set()
    for row in selected_rows:
        orientation = row.get("train_orientation")
        payloads.append(
            {
                "candidate": json.loads(str(row["candidate_spec_json"])),
                "frozen_train_orientation": (
                    None if orientation is None or pd.isna(orientation) else float(orientation)
                ),
                "include_economic_paths": str(row["candidate_id"]) in diagnostics,
                "diagnostics": str(row["candidate_id"]) in diagnostics,
            }
        )

    def execute(indexes: Sequence[int], workers: int) -> list[tuple[int, dict[str, Any]]]:
        remaining = max(
            1.0,
            float(wall_time_seconds_maximum) - (time.perf_counter() - started),
        )
        with _make_executor(
            workers=workers,
            cache_root=cache_root,
            target_root=target_root,
            contracts=contracts,
            economic=economic,
            start=start,
            end_exclusive=end_exclusive,
            role=role,
            block_contract=block_contract,
        ) as executor:
            futures = {
                executor.submit(_worker_evaluate, payloads[index]): index
                for index in indexes
            }
            completed: list[tuple[int, dict[str, Any]]] = []
            try:
                for future in concurrent.futures.as_completed(
                    futures, timeout=remaining
                ):
                    completed.append((futures[future], future.result()))
            except TimeoutError as exc:
                for future in futures:
                    future.cancel()
                raise RuntimeError("ENGINE_BUDGET_EXHAUSTED_WALL") from exc
        return completed

    indexed = execute(range(len(payloads)), int(workers_default))
    results: list[dict[str, Any] | None] = [None] * len(payloads)
    for index, value in indexed:
        results[index] = value
    if any(value is None for value in results):
        raise RuntimeError("FUNDING_FLOW_WORKER_RESULT_MISSING")
    memory_indexes = [
        index for index, value in enumerate(results) if bool(value.get("memory_error"))
    ]
    memory_fallback_used = bool(memory_indexes)
    if memory_indexes:
        for index, value in execute(memory_indexes, int(workers_fallback)):
            results[index] = value
    if any(bool(value.get("memory_error")) for value in results):
        raise RuntimeError("ENGINE_BUDGET_EXHAUSTED_MEMORY")
    projected = [
        _stage_projection(
            stage=stage,
            ordinal=index,
            selected=selected_rows[index],
            worker=dict(value),
        )
        for index, value in enumerate(results)
    ]
    elapsed = time.perf_counter() - started
    evaluated = sum(bool(row["strict_evaluated"]) for row in projected)
    resource = {
        "stage": stage,
        "candidate_count": len(projected),
        "strict_evaluated_count": evaluated,
        "candidate_local_failure_count": len(projected) - evaluated,
        "process_cpu_seconds": float(
            sum(float(row["process_cpu_seconds"]) for row in projected)
        ),
        "wall_seconds": float(elapsed),
        "pair_evaluated_per_hour": (
            float(evaluated * 3600.0 / elapsed) if elapsed > 0 else 0.0
        ),
        "workers": int(workers_fallback if memory_fallback_used else workers_default),
        "memory_fallback_used": memory_fallback_used,
        "max_worker_rss_bytes": max(int(row["worker_rss_bytes"]) for row in projected),
        "max_worker_private_bytes": max(
            int(row["worker_private_bytes"]) for row in projected
        ),
    }
    return projected, resource


def _paired_stage_rows(
    rows: Sequence[Mapping[str, Any]],
    pairs: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_id = {str(row["candidate_id"]): dict(row) for row in rows}
    output: list[dict[str, Any]] = []
    for pair in pairs:
        main = by_id.get(str(pair["main_candidate_id"]))
        placebo = by_id.get(str(pair["placebo_candidate_id"]))
        main_worst = _finite_float((main or {}).get("worst_axis_net"))
        placebo_worst = _finite_float((placebo or {}).get("worst_axis_net"))
        output.append(
            {
                **dict(pair),
                "main_strict_evaluated": bool((main or {}).get("strict_evaluated")),
                "placebo_strict_evaluated": bool(
                    (placebo or {}).get("strict_evaluated")
                ),
                "main_worst_axis_net": main_worst,
                "placebo_worst_axis_net": placebo_worst,
                "main_minus_placebo_worst_axis_net": (
                    main_worst - placebo_worst
                    if main_worst is not None and placebo_worst is not None
                    else None
                ),
            }
        )
    return output


def _checkpoint_files(root: Path) -> list[dict[str, Any]]:
    return [
        {
            "name": path.name,
            "bytes": int(path.stat().st_size),
            "sha256": _file_sha256(path),
        }
        for path in sorted(Path(root).iterdir(), key=lambda value: value.name)
        if path.is_file() and path.name != "manifest.json"
    ]


def _checkpoint_summary(
    stage: str,
    rows: Sequence[Mapping[str, Any]],
    resource: Mapping[str, Any],
) -> dict[str, Any]:
    evaluated = [row for row in rows if bool(row.get("strict_evaluated"))]
    return {
        "schema_version": 1,
        "stage": stage,
        "candidate_count": len(rows),
        "strict_evaluated_count": len(evaluated),
        "candidate_local_failure_count": len(rows) - len(evaluated),
        "main_count": sum(row.get("candidate_group") == "main" for row in rows),
        "placebo_count": sum(
            row.get("candidate_group") == "placebo" for row in rows
        ),
        "matched_positive_count": sum(
            bool(row.get("matched_positive")) for row in evaluated
        ),
        "both_axis_net_positive_count": sum(
            _finite_float(row.get("left_incremental_net_mean")) is not None
            and _finite_float(row.get("right_incremental_net_mean")) is not None
            and float(row["left_incremental_net_mean"]) > 0.0
            and float(row["right_incremental_net_mean"]) > 0.0
            for row in evaluated
        ),
        "resource": dict(resource),
    }


def _write_checkpoint(
    runtime_root: Path,
    *,
    name: str,
    stage: str,
    rows: Sequence[Mapping[str, Any]],
    pairs: Sequence[Mapping[str, Any]],
    resource: Mapping[str, Any],
    producer_source_sha: str,
    frozen_contract_sha256: str,
) -> dict[str, Any]:
    checkpoint_root = runtime_root / "checkpoints"
    checkpoint_root.mkdir(parents=True, exist_ok=True)
    final = checkpoint_root / name
    if final.exists():
        return _verify_checkpoint(
            final,
            expected_stage=stage,
            producer_source_sha=producer_source_sha,
            frozen_contract_sha256=frozen_contract_sha256,
        )
    temporary = checkpoint_root / f"{name}.tmp-{os.getpid()}"
    temporary.mkdir(parents=True)
    pd.DataFrame(rows).to_parquet(temporary / "candidate_ledger.parquet", index=False)
    pd.DataFrame(pairs).to_parquet(temporary / "paired_ledger.parquet", index=False)
    summary = _checkpoint_summary(stage, rows, resource)
    _write_json(temporary / "summary.json", summary)
    manifest = {
        "schema_version": 1,
        "checkpoint": name,
        "stage": stage,
        "producer_source_sha": producer_source_sha,
        "frozen_contract_sha256": frozen_contract_sha256,
        "candidate_count": len(rows),
        "candidate_ids_sha256": _canonical_sha256(
            [str(row["candidate_id"]) for row in rows]
        ),
        "strict_evaluated_count": int(summary["strict_evaluated_count"]),
        "files": _checkpoint_files(temporary),
    }
    manifest["manifest_sha256"] = _canonical_sha256(manifest)
    _write_json(temporary / "manifest.json", manifest)
    os.replace(temporary, final)
    return manifest


def _verify_checkpoint(
    path: Path,
    *,
    expected_stage: str,
    producer_source_sha: str,
    frozen_contract_sha256: str,
) -> dict[str, Any]:
    manifest = _load_json(path / "manifest.json")
    expected_hash = str(manifest.pop("manifest_sha256"))
    if (
        _canonical_sha256(manifest) != expected_hash
        or manifest.get("stage") != expected_stage
        or str(manifest.get("producer_source_sha")) != producer_source_sha
        or str(manifest.get("frozen_contract_sha256"))
        != frozen_contract_sha256
        or manifest.get("files") != _checkpoint_files(path)
    ):
        raise RuntimeError("FUNDING_FLOW_CHECKPOINT_RESTORE_FAILED")
    return {**manifest, "manifest_sha256": expected_hash}


def _direct_neighbor_ids(
    anchor: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
) -> list[str]:
    domains = {
        "funding_window": [96, 168, 240],
        "flow_window": [3, 6, 12],
        "beta": [0.25, 0.5, 1.0],
    }
    output: list[str] = []
    for row in rows:
        if (
            row.get("candidate_group") != "main"
            or str(row.get("funding_source")) != str(anchor["funding_source"])
            or str(row.get("candidate_id")) == str(anchor["candidate_id"])
        ):
            continue
        changed = []
        adjacent = True
        for key, domain in domains.items():
            left = float(anchor[key])
            right = float(row[key])
            if left == right:
                continue
            changed.append(key)
            left_index = domain.index(int(left) if key != "beta" else left)
            right_index = domain.index(int(right) if key != "beta" else right)
            adjacent = adjacent and abs(left_index - right_index) == 1
        if len(changed) == 1 and adjacent:
            output.append(str(row["candidate_id"]))
    return sorted(output)


def stage_a_family_gate(
    rows: Sequence[Mapping[str, Any]],
    pairs: Sequence[Mapping[str, Any]],
    *,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    frame = pd.DataFrame(rows)
    paired = pd.DataFrame(pairs)
    expected_main = int(contract["mechanism"]["main_candidate_count"])
    expected_placebo = int(contract["mechanism"]["placebo_candidate_count"])
    main = frame.loc[frame["candidate_group"].eq("main")].copy()
    placebo = frame.loc[frame["candidate_group"].eq("placebo")].copy()
    all_complete = bool(
        len(main) == expected_main
        and len(placebo) == expected_placebo
        and main["strict_evaluated"].eq(True).all()
        and placebo["strict_evaluated"].eq(True).all()
        and len(paired) == expected_main
        and paired["main_strict_evaluated"].eq(True).all()
        and paired["placebo_strict_evaluated"].eq(True).all()
    )
    group_keys = ["funding_source", "funding_window", "flow_window"]
    cell = (
        main.groupby(group_keys, sort=True, dropna=False)
        .agg(
            candidate_count=("candidate_id", "count"),
            cell_left_net=("left_incremental_net_mean", "median"),
            cell_right_net=("right_incremental_net_mean", "median"),
            cell_worst_axis_net=("worst_axis_net", "median"),
        )
        .reset_index()
    )
    pair_cell = (
        paired.groupby(group_keys, sort=True, dropna=False)
        .agg(
            candidate_pair_count=("pair_id", "count"),
            cell_main_worst_axis_net=("main_worst_axis_net", "median"),
            cell_placebo_worst_axis_net=("placebo_worst_axis_net", "median"),
            cell_main_minus_placebo=(
                "main_minus_placebo_worst_axis_net",
                "median",
            ),
        )
        .reset_index()
    )
    source = (
        cell.groupby("funding_source", sort=True)
        .agg(source_cell_median_worst_axis_net=("cell_worst_axis_net", "median"))
        .reset_index()
    )
    anchor_rows = main.loc[main["is_anchor"].eq(True)]
    neighbor_ids: list[str] = []
    neighbor_positive_count = 0
    neighbor_fraction = 0.0
    if len(anchor_rows) == 1:
        anchor = anchor_rows.iloc[0].to_dict()
        neighbor_ids = _direct_neighbor_ids(anchor, main.to_dict("records"))
        neighbors = main.loc[main["candidate_id"].astype(str).isin(neighbor_ids)]
        neighbor_positive_count = int(neighbors["worst_axis_net"].gt(0.0).sum())
        neighbor_fraction = (
            float(neighbor_positive_count / len(neighbor_ids))
            if neighbor_ids
            else 0.0
        )
    gates = dict(contract["stage_a_gate"])
    global_main_median = (
        float(cell["cell_worst_axis_net"].median()) if not cell.empty else float("nan")
    )
    cells_both_fraction = (
        float(
            (
                cell["cell_left_net"].gt(0.0)
                & cell["cell_right_net"].gt(0.0)
            ).mean()
        )
        if not cell.empty
        else 0.0
    )
    positive_sources = int(source["source_cell_median_worst_axis_net"].gt(0.0).sum())
    global_placebo_delta = (
        float(pair_cell["cell_main_minus_placebo"].median())
        if not pair_cell.empty
        else float("nan")
    )
    main_above_placebo_fraction = (
        float(pair_cell["cell_main_minus_placebo"].gt(0.0).mean())
        if not pair_cell.empty
        else 0.0
    )
    conditions = {
        "complete_evaluation": all_complete,
        "global_main_cell_median_worst_axis_net_positive": bool(
            math.isfinite(global_main_median) and global_main_median > 0.0
        ),
        "main_cells_both_axes_fraction": bool(
            cells_both_fraction
            >= float(gates["minimum_main_cells_both_axes_net_positive_fraction"])
        ),
        "positive_funding_source_count": bool(positive_sources >= 2),
        "global_main_minus_placebo_cell_delta_positive": bool(
            math.isfinite(global_placebo_delta) and global_placebo_delta > 0.0
        ),
        "paired_cells_main_above_placebo_fraction": bool(
            main_above_placebo_fraction
            >= float(gates["minimum_paired_cells_main_above_placebo_fraction"])
        ),
        "anchor_direct_neighbor_positive_fraction": bool(
            neighbor_fraction
            >= float(gates["minimum_anchor_direct_neighbor_positive_fraction"])
        ),
    }
    placebo_pass = bool(
        conditions["global_main_minus_placebo_cell_delta_positive"]
        and conditions["paired_cells_main_above_placebo_fraction"]
    )
    passed = bool(all(conditions.values()))
    return {
        "schema_version": 1,
        "stage": "validation_a",
        "status": "PASS" if passed else "FAIL",
        "family_gate_pass": passed,
        "main_vs_placebo_gate_pass": placebo_pass,
        "conditions": conditions,
        "metrics": {
            "global_main_cell_median_worst_axis_net": global_main_median,
            "main_cells_both_axes_positive_fraction": cells_both_fraction,
            "positive_funding_source_count": positive_sources,
            "global_median_main_minus_placebo_cell_delta": global_placebo_delta,
            "paired_cells_main_above_placebo_fraction": main_above_placebo_fraction,
            "anchor_direct_neighbor_count": len(neighbor_ids),
            "anchor_direct_neighbor_positive_count": neighbor_positive_count,
            "anchor_direct_neighbor_positive_fraction": neighbor_fraction,
        },
        "anchor_direct_neighbor_ids": neighbor_ids,
        "cell_metrics": cell.to_dict("records"),
        "paired_cell_metrics": pair_cell.to_dict("records"),
        "source_metrics": source.to_dict("records"),
    }


def _local_basin_scores(
    main_rows: Sequence[Mapping[str, Any]],
) -> dict[str, float]:
    by_id = {str(row["candidate_id"]): dict(row) for row in main_rows}
    scores: dict[str, float] = {}
    for candidate_id, row in by_id.items():
        ids = [candidate_id, *_direct_neighbor_ids(row, main_rows)]
        values = [
            _finite_float(by_id[value].get("worst_axis_net"))
            for value in ids
            if value in by_id
        ]
        finite = [value for value in values if value is not None]
        scores[candidate_id] = float(np.median(finite)) if finite else float("-inf")
    return scores


def freeze_validation_b_selection(
    *,
    runtime_root: Path,
    stage_a_rows: Sequence[Mapping[str, Any]],
    stage_0_rows: Sequence[Mapping[str, Any]],
    pairs: Sequence[Mapping[str, Any]],
    stage_a_gate: Mapping[str, Any],
    producer_source_sha: str,
    frozen_contract_sha256: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = runtime_root / "validation_b_selection_receipt.json"
    stage_a_by_id = {str(row["candidate_id"]): dict(row) for row in stage_a_rows}
    stage_0_by_id = {str(row["candidate_id"]): dict(row) for row in stage_0_rows}
    pair_by_main = {str(row["main_candidate_id"]): dict(row) for row in pairs}
    main_rows = [
        dict(row)
        for row in stage_a_rows
        if row.get("candidate_group") == "main" and bool(row.get("strict_evaluated"))
    ]
    scores = _local_basin_scores(main_rows)

    def ordering(row: Mapping[str, Any]) -> tuple[Any, ...]:
        candidate_id = str(row["candidate_id"])
        stage0 = stage_0_by_id[candidate_id]
        development_worst = _finite_float(
            stage0.get("development_worst_block_min_matched_net")
        )
        turnover = _finite_float(row.get("primary_turnover_mean"))
        return (
            -float(scores[candidate_id]),
            -float(row["worst_axis_net"]),
            -(development_worst if development_worst is not None else float("-inf")),
            turnover if turnover is not None else float("inf"),
            candidate_id,
        )

    anchor = [row for row in main_rows if bool(row.get("is_anchor"))]
    if len(anchor) != 1:
        raise RuntimeError("FUNDING_FLOW_SELECTION_ANCHOR_CHANGED")
    medoid = sorted(main_rows, key=ordering)[0]
    source_representatives = {
        str(source): sorted(
            [row for row in main_rows if str(row["funding_source"]) == str(source)],
            key=ordering,
        )[0]
        for source in sorted({str(row["funding_source"]) for row in main_rows})
    }
    roles: dict[str, list[str]] = {}

    def add_role(candidate_id: str, role: str) -> None:
        roles.setdefault(candidate_id, []).append(role)

    add_role(str(anchor[0]["candidate_id"]), "ANCHOR")
    add_role(str(medoid["candidate_id"]), "FAMILY_MEDOID")
    for source, row in source_representatives.items():
        add_role(str(row["candidate_id"]), f"SOURCE_REPRESENTATIVE:{source}")
    main_ids = list(roles)
    for main_id in list(main_ids):
        placebo_id = str(pair_by_main[main_id]["placebo_candidate_id"])
        for role in roles[main_id]:
            add_role(placebo_id, f"PAIRED_PLACEBO_FOR:{role}")
    candidate_ids = list(roles)
    selected: list[dict[str, Any]] = []
    grid_by_id = {str(row["candidate_id"]): dict(row) for row in stage_a_rows}
    for order, candidate_id in enumerate(candidate_ids, start=1):
        row = dict(grid_by_id[candidate_id])
        row["selection_roles_json"] = _json_value(roles[candidate_id])
        row["selection_order"] = order
        selected.append(row)
    if len(selected) > 2 * (1 + 1 + len(source_representatives)):
        raise RuntimeError("FUNDING_FLOW_SELECTION_COHORT_EXPANDED")
    selection = {
        "schema_version": 1,
        "experiment_id": "CRYPTO_FUNDING_FLOW_RESIDUAL_NESTED_CONFIRMATION_V1",
        "evidence_status": "REUSED_DEVELOPMENT_VALIDATION_ADAPTIVE_DIAGNOSTIC_ONLY",
        "producer_source_sha": producer_source_sha,
        "frozen_contract_sha256": frozen_contract_sha256,
        "validation_b_read": False,
        "candidate_count": len(selected),
        "candidate_ids": candidate_ids,
        "candidate_ids_sha256": _canonical_sha256(candidate_ids),
        "candidate_spec_sha256": {
            str(row["candidate_id"]): str(row["candidate_spec_sha256"])
            for row in selected
        },
        "selection_roles": roles,
        "anchor_candidate_id": str(anchor[0]["candidate_id"]),
        "family_medoid_candidate_id": str(medoid["candidate_id"]),
        "source_representatives": {
            source: str(row["candidate_id"])
            for source, row in source_representatives.items()
        },
        "paired_placebos": {
            main_id: str(pair_by_main[main_id]["placebo_candidate_id"])
            for main_id in main_ids
        },
        "local_basin_scores": {key: float(value) for key, value in scores.items()},
        "stage_a_gate_sha256": _canonical_sha256(stage_a_gate),
        "stage_a_checkpoint_manifest_sha256": _file_sha256(
            runtime_root / "checkpoints" / "checkpoint_validation_a" / "manifest.json"
        ),
        "selection_rule": [
            "LOCAL_BASIN_SCORE_DESC",
            "SELF_WORST_AXIS_NET_DESC",
            "DEVELOPMENT_WORST_BLOCK_MIN_MATCHED_NET_DESC",
            "TURNOVER_ASC",
            "CANDIDATE_ID_ASC",
        ],
        "optimizer_feedback_written": False,
        "archive_written": False,
        "oos_read": False,
        "holdout_read": False,
    }
    selection["selection_receipt_sha256"] = _canonical_sha256(selection)
    if path.exists():
        existing = _load_json(path)
        if existing != selection:
            raise RuntimeError("FUNDING_FLOW_SELECTION_RECEIPT_CHANGED")
    else:
        _write_json(path, selection)
    return selected, selection


def stage_b_confirmation_gate(
    rows: Sequence[Mapping[str, Any]],
    *,
    selection: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    by_id = {str(row["candidate_id"]): dict(row) for row in rows}
    if set(by_id) != set(selection["candidate_ids"]):
        raise RuntimeError("FUNDING_FLOW_VALIDATION_B_COHORT_CHANGED")
    anchor = by_id[str(selection["anchor_candidate_id"])]
    medoid = by_id[str(selection["family_medoid_candidate_id"])]
    reps = {
        str(source): by_id[str(candidate_id)]
        for source, candidate_id in dict(selection["source_representatives"]).items()
    }
    paired = dict(selection["paired_placebos"])

    def number(row: Mapping[str, Any], key: str) -> float:
        value = _finite_float(row.get(key))
        return value if value is not None else float("-inf")

    anchor_pass = bool(
        anchor.get("strict_evaluated")
        and anchor.get("matched_positive")
        and number(anchor, "primary_net_mean") > 0.0
        and number(anchor, "primary_net_lcb") > 0.0
        and number(anchor, "left_incremental_net_lcb") > 0.0
        and number(anchor, "right_incremental_net_lcb") > 0.0
        and number(anchor, "support_min") >= 0.8
    )
    rep_worst = [number(row, "worst_axis_net") for row in reps.values()]
    rep_both_positive = {
        source: bool(
            number(row, "left_incremental_net_mean") > 0.0
            and number(row, "right_incremental_net_mean") > 0.0
        )
        for source, row in reps.items()
    }
    rep_deltas = []
    for row in reps.values():
        main_id = str(row["candidate_id"])
        placebo = by_id[str(paired[main_id])]
        rep_deltas.append(
            number(row, "worst_axis_net") - number(placebo, "worst_axis_net")
        )
    family_conditions = {
        "all_selected_evaluated": all(
            bool(row.get("strict_evaluated")) for row in by_id.values()
        ),
        "family_medoid_strict_matched_positive": bool(
            medoid.get("strict_evaluated") and medoid.get("matched_positive")
        ),
        "source_representative_median_worst_axis_net_positive": bool(
            rep_worst and float(np.median(rep_worst)) > 0.0
        ),
        "minimum_two_source_representatives_both_axes_positive": bool(
            sum(rep_both_positive.values()) >= 2
        ),
        "representative_median_main_minus_placebo_positive": bool(
            rep_deltas and float(np.median(rep_deltas)) > 0.0
        ),
        "positive_representatives_span_sources": bool(
            len([source for source, value in rep_both_positive.items() if value]) > 1
        ),
        "anchor_or_medoid_strict_matched_positive": bool(
            anchor.get("matched_positive") or medoid.get("matched_positive")
        ),
    }
    family_pass = bool(all(family_conditions.values()))
    return {
        "schema_version": 1,
        "stage": "validation_b",
        "anchor_pass": anchor_pass,
        "family_pass": family_pass,
        "anchor_metrics": {
            key: anchor.get(key)
            for key in (
                "matched_positive",
                "primary_net_mean",
                "primary_net_lcb",
                "left_incremental_net_lcb",
                "right_incremental_net_lcb",
                "support_min",
            )
        },
        "family_conditions": family_conditions,
        "source_representative_both_axes_positive": rep_both_positive,
        "source_representative_worst_axis_net": {
            source: number(row, "worst_axis_net") for source, row in reps.items()
        },
        "source_representative_main_minus_placebo": rep_deltas,
        "source_representative_median_worst_axis_net": (
            float(np.median(rep_worst)) if rep_worst else None
        ),
        "representative_median_main_minus_placebo": (
            float(np.median(rep_deltas)) if rep_deltas else None
        ),
    }


def _counterfactual_decision(
    *,
    stage_a_gate: Mapping[str, Any],
    stage_b_gate: Mapping[str, Any] | None,
) -> str:
    if not bool(stage_a_gate.get("main_vs_placebo_gate_pass")):
        return "LONG_FUNDING_SHORT_FLOW_DIRECTIONAL_HYPOTHESIS_NOT_SUPPORTED"
    if stage_b_gate is None:
        return "FUNDING_FLOW_RESIDUAL_ROUTE_CLOSED"
    anchor = bool(stage_b_gate["anchor_pass"])
    family = bool(stage_b_gate["family_pass"])
    if anchor and family:
        return "FUNDING_FLOW_RESIDUAL_CONFIRMED_FOR_SEPARATE_OOS_AUTHORIZATION"
    if not anchor and family:
        return "MECHANISM_FAMILY_SUPPORTED_BUT_NO_PRECONFIRMED_OOS_CANDIDATE"
    if anchor and not family:
        return "ISOLATED_CANDIDATE_CONFIRMATION_WITHOUT_BROAD_MECHANISM_SUPPORT"
    return "FUNDING_FLOW_RESIDUAL_ROUTE_CLOSED"


def _report_markdown(decision: Mapping[str, Any]) -> str:
    stage_a = dict(decision.get("stage_a_gate") or {})
    stage_b = dict(decision.get("stage_b_gate") or {})
    a_metrics = dict(stage_a.get("metrics") or {})
    return f"""# Crypto Funding-Flow Residual Nested Confirmation V1

- Evidence status: `REUSED_DEVELOPMENT_VALIDATION / ADAPTIVE_DIAGNOSTIC_ONLY`
- Producer source: `{decision['producer_source_sha']}`
- Terminal status: `{decision['status']}`
- Actual research decision: `{decision['research_decision']}`
- Counterfactual preregistered branch: `{decision['counterfactual_preregistered_branch']}`
- Validation-B read: `{decision['validation_b_read']}`
- OOS / holdout reads: `0 / 0`

This run reused a previously read development-validation interval under the
user's explicit one-time override. It can diagnose basin continuity and the
main-versus-swapped-timescale placebo contrast, but it cannot establish unread
migration, OOS qualification, or promotion authority.

## Validation-A family screen

- Gate: `{stage_a.get('status')}`
- Main cell median worst-axis net: `{a_metrics.get('global_main_cell_median_worst_axis_net')}`
- Main cells with both axes positive: `{a_metrics.get('main_cells_both_axes_positive_fraction')}`
- Positive funding sources: `{a_metrics.get('positive_funding_source_count')}`
- Median main-minus-placebo cell delta: `{a_metrics.get('global_median_main_minus_placebo_cell_delta')}`
- Main above placebo cell fraction: `{a_metrics.get('paired_cells_main_above_placebo_fraction')}`
- Anchor direct-neighbor positive fraction: `{a_metrics.get('anchor_direct_neighbor_positive_fraction')}`

## Validation-B frozen confirmation

- Executed: `{bool(stage_b)}`
- Anchor pass: `{stage_b.get('anchor_pass')}`
- Family pass: `{stage_b.get('family_pass')}`
- Source representative median worst-axis net: `{stage_b.get('source_representative_median_worst_axis_net')}`
- Representative median main-minus-placebo: `{stage_b.get('representative_median_main_minus_placebo')}`

No candidate, family, arm, or mechanism is authorized for OOS, promotion,
challenge, forward, or automatic expansion by this diagnostic.
"""


def _runtime_artifacts(
    root: Path,
    runtime_root: Path,
    report_path: Path,
) -> list[dict[str, Any]]:
    names = [
        "frozen_contract.json",
        "candidate_grid.parquet",
        "paired_grid.parquet",
        "stage_0_candidate_ledger.parquet",
        "stage_0_paired_ledger.parquet",
        "validation_a_candidate_ledger.parquet",
        "validation_a_paired_ledger.parquet",
        "validation_a_gate.json",
        "validation_b_selection_receipt.json",
        "validation_b_candidate_ledger.parquet",
        "validation_b_paired_ledger.parquet",
        "validation_b_gate.json",
        "final_decision.json",
    ]
    paths = [runtime_root / name for name in names if (runtime_root / name).is_file()]
    if report_path.is_file():
        paths.append(report_path)
    for checkpoint in sorted((runtime_root / "checkpoints").glob("checkpoint_*")):
        if checkpoint.is_dir():
            paths.extend(sorted(path for path in checkpoint.iterdir() if path.is_file()))
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": int(path.stat().st_size),
            "sha256": _file_sha256(path),
        }
        for path in paths
    ]


def _write_terminal(
    *,
    root: Path,
    runtime_root: Path,
    runtime_date: str,
    producer_source_sha: str,
    receipt: Mapping[str, Any],
    frozen: Mapping[str, Any],
    stage_a_gate: Mapping[str, Any],
    stage_b_gate: Mapping[str, Any] | None,
    resources: Sequence[Mapping[str, Any]],
    validation_b_read: bool,
    status: str,
) -> dict[str, Any]:
    branch = _counterfactual_decision(
        stage_a_gate=stage_a_gate, stage_b_gate=stage_b_gate
    )
    decision = {
        "schema_version": 1,
        "experiment_id": "CRYPTO_FUNDING_FLOW_RESIDUAL_NESTED_CONFIRMATION_V1",
        "status": status,
        "evidence_status": "REUSED_DEVELOPMENT_VALIDATION_ADAPTIVE_DIAGNOSTIC_ONLY",
        "producer_source_sha": producer_source_sha,
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "stage_a_gate": dict(stage_a_gate),
        "stage_b_gate": dict(stage_b_gate) if stage_b_gate is not None else None,
        "counterfactual_preregistered_branch": branch,
        "research_decision": f"REUSED_VALIDATION_DIAGNOSTIC_ONLY::{branch}",
        "unread_migration_claim_authorized": False,
        "oos_authorization": False,
        "promotion_authorized": False,
        "automatic_expansion": False,
        "optimizer_feedback_written": False,
        "archive_written": False,
        "validation_b_read": bool(validation_b_read),
        "holdout_read_count": 0,
        "oos_read_count": 0,
        "source_deviation": dict(receipt["_contract"]["source_deviation"]),
    }
    _write_json(runtime_root / "final_decision.json", decision)
    report_path = root / "reports" / f"{REPORT_PREFIX}_{runtime_date}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_report_markdown(decision), encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "status": status,
        "evidence_status": decision["evidence_status"],
        "producer_source_sha": producer_source_sha,
        "runtime": runtime_root.relative_to(root).as_posix(),
        "report": report_path.relative_to(root).as_posix(),
        "run_receipt_sha256": _file_sha256(root / str(receipt["_receipt_path"])),
        "frozen_contract_sha256": frozen["frozen_contract_sha256"],
        "checkpoint_count": len(
            [
                path
                for path in (runtime_root / "checkpoints").glob("checkpoint_*")
                if path.is_dir() and ".tmp-" not in path.name
            ]
        ),
        "resources": [dict(value) for value in resources],
        "validation_b_read": bool(validation_b_read),
        "candidate_generation_performed": False,
        "optimizer_feedback_written": False,
        "policy_memory_written": False,
        "archive_written": False,
        "holdout_read_count": 0,
        "oos_read_count": 0,
        "second_run_performed": False,
        "files": _runtime_artifacts(root, runtime_root, report_path),
    }
    manifest["bundle_sha256"] = _canonical_sha256(manifest)
    _write_json(runtime_root / "run_manifest.json", manifest)
    _write_json(
        runtime_root / "producer_status.json",
        {
            "schema_version": 1,
            "status": status,
            "producer_pid": os.getpid(),
            "producer_source_sha": producer_source_sha,
            "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
            "checkpoint_count": manifest["checkpoint_count"],
            "validation_b_read": bool(validation_b_read),
            "holdout_read_count": 0,
            "oos_read_count": 0,
        },
    )
    return decision


def preflight_confirmation(
    repo_root: Path,
    *,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_confirmation_receipt(
        root, receipt_path=receipt_path, require_authorized=True
    )
    rows, pairs, proof = build_frozen_grid(root, receipt=receipt)
    target_metadata = _load_json(root / str(receipt["carrier"]["target_cache"]) / "metadata.json")
    if str(target_metadata["identity_sha256"]) != str(
        receipt["carrier"]["target_identity_sha256"]
    ):
        raise RuntimeError("FUNDING_FLOW_TARGET_IDENTITY_CHANGED")
    return {
        "schema_version": 1,
        "status": "PREFLIGHT_PASS_NO_MARKET_EVALUATION",
        "market_read_performed": False,
        "candidate_count": len(rows),
        "pair_count": len(pairs),
        "proof": proof,
        "target_identity_sha256": target_metadata["identity_sha256"],
        "evidence_status": receipt["_contract"]["evidence_status"],
        "holdout_read": False,
        "oos_read": False,
    }


def run_confirmation(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    producer_source_sha: str | None = None,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_confirmation_receipt(
        root, receipt_path=receipt_path, require_authorized=True
    )
    observed_sha = _git_head(root)
    source_sha = str(producer_source_sha or observed_sha).lower()
    if source_sha != observed_sha:
        raise RuntimeError("FUNDING_FLOW_PRODUCER_SOURCE_SHA_CHANGED")
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    if (runtime_root / "run_manifest.json").exists():
        raise RuntimeError("FUNDING_FLOW_CONFIRMATION_ALREADY_TERMINAL")
    runtime_root.mkdir(parents=True, exist_ok=True)
    rows, pairs, proof = build_frozen_grid(root, receipt=receipt)
    manifest, contracts, _, _ = _load_grid_inputs(root, receipt)
    target_metadata = _load_json(
        root / str(receipt["carrier"]["target_cache"]) / "metadata.json"
    )
    if str(target_metadata["identity_sha256"]) != str(
        receipt["carrier"]["target_identity_sha256"]
    ):
        raise RuntimeError("FUNDING_FLOW_TARGET_IDENTITY_CHANGED")
    frozen = {
        "schema_version": 1,
        "experiment_id": "CRYPTO_FUNDING_FLOW_RESIDUAL_NESTED_CONFIRMATION_V1",
        "producer_source_sha": source_sha,
        "evidence_status": "REUSED_DEVELOPMENT_VALIDATION_ADAPTIVE_DIAGNOSTIC_ONLY",
        "run_receipt_sha256": _file_sha256(root / receipt_path),
        "contract_sha256": _file_sha256(root / str(receipt["contract"]["path"])),
        "grid_proof": proof,
        "carrier_cache_identity_sha256": manifest["cache_identity_sha256"],
        "target_cache_identity_sha256": target_metadata["identity_sha256"],
        "validation_a": dict(receipt["_contract"]["validation_a"]),
        "validation_b": dict(receipt["_contract"]["validation_b"]),
        "development_train": dict(receipt["_contract"]["development_train"]),
        "stage_a_gate": dict(receipt["_contract"]["stage_a_gate"]),
        "stage_b_gate": dict(receipt["_contract"]["stage_b_gate"]),
        "source_deviation": dict(receipt["_contract"]["source_deviation"]),
        "validation_b_read": False,
        "candidate_generation": False,
        "optimizer_feedback": False,
        "archive_write": False,
        "holdout_read": False,
        "oos_read": False,
    }
    frozen["frozen_contract_sha256"] = _canonical_sha256(frozen)
    frozen_path = runtime_root / "frozen_contract.json"
    if frozen_path.exists():
        if _load_json(frozen_path) != frozen:
            raise RuntimeError("FUNDING_FLOW_FROZEN_CONTRACT_CHANGED")
    else:
        pd.DataFrame(rows).to_parquet(runtime_root / "candidate_grid.parquet", index=False)
        pd.DataFrame(pairs).to_parquet(runtime_root / "paired_grid.parquet", index=False)
        _write_json(frozen_path, frozen)
    compute = dict(receipt["_contract"]["compute"])
    cache_root = root / str(receipt["carrier"]["aligned_cache"])
    target_root = root / str(receipt["carrier"]["target_cache"])
    block_contract = dict(
        _load_json(root / "config" / "crypto_search_replication_aware_gate_v1.json")[
            "block_robust_contract"
        ]
    )
    resources: list[dict[str, Any]] = []

    def status(value: str, **extra: Any) -> None:
        _write_json(
            runtime_root / "producer_status.json",
            {
                "schema_version": 1,
                "status": value,
                "producer_pid": os.getpid(),
                "producer_source_sha": source_sha,
                "heartbeat_utc": pd.Timestamp.now(tz="UTC").isoformat(),
                "validation_b_read": False,
                "holdout_read_count": 0,
                "oos_read_count": 0,
                **extra,
            },
        )

    stage0_checkpoint = runtime_root / "checkpoints" / "checkpoint_stage_0"
    if stage0_checkpoint.exists():
        _verify_checkpoint(
            stage0_checkpoint,
            expected_stage="stage_0",
            producer_source_sha=source_sha,
            frozen_contract_sha256=frozen["frozen_contract_sha256"],
        )
        stage0_rows = pd.read_parquet(
            stage0_checkpoint / "candidate_ledger.parquet"
        ).to_dict("records")
        stage0_pairs = pd.read_parquet(
            stage0_checkpoint / "paired_ledger.parquet"
        ).to_dict("records")
        resources.append(_load_json(stage0_checkpoint / "summary.json")["resource"])
    else:
        status("STAGE_0_RUNNING", completed_candidate_count=0)
        stage0_rows, stage0_resource = _evaluate_stage(
            stage="stage_0",
            selected_rows=rows,
            cache_root=cache_root,
            target_root=target_root,
            contracts=contracts,
            economic=_build_economic_context(root, receipt),
            start=str(receipt["_contract"]["development_train"]["start"]),
            end_exclusive=str(
                receipt["_contract"]["development_train"]["end_exclusive"]
            ),
            role=str(receipt["_contract"]["development_train"]["role"]),
            block_contract=block_contract,
            workers_default=int(compute["workers_default"]),
            workers_fallback=int(compute["workers_memory_fallback"]),
            wall_time_seconds_maximum=float(compute["wall_time_seconds_maximum"]),
        )
        stage0_pairs = _paired_stage_rows(stage0_rows, pairs)
        _write_checkpoint(
            runtime_root,
            name="checkpoint_stage_0",
            stage="stage_0",
            rows=stage0_rows,
            pairs=stage0_pairs,
            resource=stage0_resource,
            producer_source_sha=source_sha,
            frozen_contract_sha256=frozen["frozen_contract_sha256"],
        )
        resources.append(stage0_resource)
    shutil.copy2(
        stage0_checkpoint / "candidate_ledger.parquet",
        runtime_root / "stage_0_candidate_ledger.parquet",
    )
    shutil.copy2(
        stage0_checkpoint / "paired_ledger.parquet",
        runtime_root / "stage_0_paired_ledger.parquet",
    )
    if not all(bool(row.get("strict_evaluated")) for row in stage0_rows):
        invalid_gate = {
            "schema_version": 1,
            "stage": "validation_a",
            "status": "NOT_RUN_STAGE_0_INCOMPLETE",
            "family_gate_pass": False,
            "main_vs_placebo_gate_pass": False,
        }
        return _write_terminal(
            root=root,
            runtime_root=runtime_root,
            runtime_date=runtime_date,
            producer_source_sha=source_sha,
            receipt=receipt,
            frozen=frozen,
            stage_a_gate=invalid_gate,
            stage_b_gate=None,
            resources=resources,
            validation_b_read=False,
            status="RUN_INVALID_STAGE_0_INCOMPLETE",
        )
    stage0_by_id = {str(row["candidate_id"]): dict(row) for row in stage0_rows}
    validation_rows = []
    for row in rows:
        augmented = dict(row)
        augmented["train_orientation"] = float(
            stage0_by_id[str(row["candidate_id"])]["train_orientation"]
        )
        validation_rows.append(augmented)

    stage_a_checkpoint = runtime_root / "checkpoints" / "checkpoint_validation_a"
    if stage_a_checkpoint.exists():
        _verify_checkpoint(
            stage_a_checkpoint,
            expected_stage="validation_a",
            producer_source_sha=source_sha,
            frozen_contract_sha256=frozen["frozen_contract_sha256"],
        )
        stage_a_rows = pd.read_parquet(
            stage_a_checkpoint / "candidate_ledger.parquet"
        ).to_dict("records")
        stage_a_pairs = pd.read_parquet(
            stage_a_checkpoint / "paired_ledger.parquet"
        ).to_dict("records")
        resources.append(_load_json(stage_a_checkpoint / "summary.json")["resource"])
    else:
        status("VALIDATION_A_RUNNING", completed_candidate_count=0)
        validation_a = dict(receipt["_contract"]["validation_a"])
        stage_a_rows, stage_a_resource = _evaluate_stage(
            stage="validation_a",
            selected_rows=validation_rows,
            cache_root=cache_root,
            target_root=target_root,
            contracts=contracts,
            economic=_build_economic_context(root, receipt, validation=validation_a),
            start=str(validation_a["start"]),
            end_exclusive=str(validation_a["end_exclusive"]),
            role=str(validation_a["role"]),
            block_contract=None,
            workers_default=int(compute["workers_default"]),
            workers_fallback=int(compute["workers_memory_fallback"]),
            wall_time_seconds_maximum=float(compute["wall_time_seconds_maximum"]),
        )
        stage_a_pairs = _paired_stage_rows(stage_a_rows, pairs)
        _write_checkpoint(
            runtime_root,
            name="checkpoint_validation_a",
            stage="validation_a",
            rows=stage_a_rows,
            pairs=stage_a_pairs,
            resource=stage_a_resource,
            producer_source_sha=source_sha,
            frozen_contract_sha256=frozen["frozen_contract_sha256"],
        )
        resources.append(stage_a_resource)
    shutil.copy2(
        stage_a_checkpoint / "candidate_ledger.parquet",
        runtime_root / "validation_a_candidate_ledger.parquet",
    )
    shutil.copy2(
        stage_a_checkpoint / "paired_ledger.parquet",
        runtime_root / "validation_a_paired_ledger.parquet",
    )
    a_gate = stage_a_family_gate(
        stage_a_rows, stage_a_pairs, contract=receipt["_contract"]
    )
    _write_json(runtime_root / "validation_a_gate.json", a_gate)
    if not bool(a_gate["family_gate_pass"]):
        return _write_terminal(
            root=root,
            runtime_root=runtime_root,
            runtime_date=runtime_date,
            producer_source_sha=source_sha,
            receipt=receipt,
            frozen=frozen,
            stage_a_gate=a_gate,
            stage_b_gate=None,
            resources=resources,
            validation_b_read=False,
            status="VALIDATION_A_TERMINAL_FAIL_CLOSED",
        )

    selected, selection = freeze_validation_b_selection(
        runtime_root=runtime_root,
        stage_a_rows=stage_a_rows,
        stage_0_rows=stage0_rows,
        pairs=pairs,
        stage_a_gate=a_gate,
        producer_source_sha=source_sha,
        frozen_contract_sha256=frozen["frozen_contract_sha256"],
    )
    diagnostics = {
        str(selection["anchor_candidate_id"]),
        str(selection["family_medoid_candidate_id"]),
    }
    stage_b_checkpoint = runtime_root / "checkpoints" / "checkpoint_validation_b"
    if stage_b_checkpoint.exists():
        _verify_checkpoint(
            stage_b_checkpoint,
            expected_stage="validation_b",
            producer_source_sha=source_sha,
            frozen_contract_sha256=frozen["frozen_contract_sha256"],
        )
        stage_b_rows = pd.read_parquet(
            stage_b_checkpoint / "candidate_ledger.parquet"
        ).to_dict("records")
        stage_b_pairs = pd.read_parquet(
            stage_b_checkpoint / "paired_ledger.parquet"
        ).to_dict("records")
        resources.append(_load_json(stage_b_checkpoint / "summary.json")["resource"])
    else:
        status(
            "VALIDATION_B_RUNNING",
            validation_b_read=True,
            frozen_candidate_count=len(selected),
        )
        validation_b = dict(receipt["_contract"]["validation_b"])
        stage_b_rows, stage_b_resource = _evaluate_stage(
            stage="validation_b",
            selected_rows=selected,
            cache_root=cache_root,
            target_root=target_root,
            contracts=contracts,
            economic=_build_economic_context(root, receipt, validation=validation_b),
            start=str(validation_b["start"]),
            end_exclusive=str(validation_b["end_exclusive"]),
            role=str(validation_b["role"]),
            block_contract=None,
            workers_default=int(compute["workers_default"]),
            workers_fallback=int(compute["workers_memory_fallback"]),
            wall_time_seconds_maximum=float(compute["wall_time_seconds_maximum"]),
            diagnostic_candidate_ids=diagnostics,
        )
        selected_pairs = [
            dict(pair)
            for pair in pairs
            if str(pair["main_candidate_id"])
            in set(dict(selection["paired_placebos"]).keys())
        ]
        stage_b_pairs = _paired_stage_rows(stage_b_rows, selected_pairs)
        _write_checkpoint(
            runtime_root,
            name="checkpoint_validation_b",
            stage="validation_b",
            rows=stage_b_rows,
            pairs=stage_b_pairs,
            resource=stage_b_resource,
            producer_source_sha=source_sha,
            frozen_contract_sha256=frozen["frozen_contract_sha256"],
        )
        resources.append(stage_b_resource)
    shutil.copy2(
        stage_b_checkpoint / "candidate_ledger.parquet",
        runtime_root / "validation_b_candidate_ledger.parquet",
    )
    shutil.copy2(
        stage_b_checkpoint / "paired_ledger.parquet",
        runtime_root / "validation_b_paired_ledger.parquet",
    )
    b_gate = stage_b_confirmation_gate(
        stage_b_rows, selection=selection, contract=receipt["_contract"]
    )
    _write_json(runtime_root / "validation_b_gate.json", b_gate)
    return _write_terminal(
        root=root,
        runtime_root=runtime_root,
        runtime_date=runtime_date,
        producer_source_sha=source_sha,
        receipt=receipt,
        frozen=frozen,
        stage_a_gate=a_gate,
        stage_b_gate=b_gate,
        resources=resources,
        validation_b_read=True,
        status="REUSED_DEVELOPMENT_VALIDATION_DIAGNOSTIC_COMPLETE",
    )


def check_confirmation(
    repo_root: Path,
    *,
    runtime_date: str = DEFAULT_RUNTIME_DATE,
    receipt_path: str = RECEIPT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    receipt = load_confirmation_receipt(
        root, receipt_path=receipt_path, require_authorized=False
    )
    runtime_root = root / "runtime" / f"{RUNTIME_PREFIX}_{runtime_date}"
    manifest = _load_json(runtime_root / "run_manifest.json")
    decision = _load_json(runtime_root / "final_decision.json")
    frozen = _load_json(runtime_root / "frozen_contract.json")
    source_sha = str(manifest["producer_source_sha"]).lower()
    try:
        subprocess.check_call(
            ["git", "cat-file", "-e", f"{source_sha}^{{commit}}"],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("FUNDING_FLOW_CHECKER_SOURCE_SHA_MISSING") from exc
    errors: list[str] = []
    if (
        decision.get("evidence_status")
        != "REUSED_DEVELOPMENT_VALIDATION_ADAPTIVE_DIAGNOSTIC_ONLY"
        or manifest.get("evidence_status")
        != "REUSED_DEVELOPMENT_VALIDATION_ADAPTIVE_DIAGNOSTIC_ONLY"
        or decision.get("oos_authorization") is not False
        or decision.get("promotion_authorized") is not False
        or int(decision.get("holdout_read_count", -1)) != 0
        or int(decision.get("oos_read_count", -1)) != 0
        or manifest.get("optimizer_feedback_written") is not False
        or manifest.get("archive_written") is not False
        or manifest.get("second_run_performed") is not False
    ):
        errors.append("boundary")
    frozen_payload = dict(frozen)
    frozen_hash = str(frozen_payload.pop("frozen_contract_sha256"))
    if (
        _canonical_sha256(frozen_payload) != frozen_hash
        or frozen_hash != str(manifest["frozen_contract_sha256"])
        or frozen_hash != str(decision["frozen_contract_sha256"])
        or frozen.get("validation_b_read") is not False
        or frozen.get("holdout_read") is not False
        or frozen.get("oos_read") is not False
    ):
        errors.append("frozen_contract")
    grid = pd.read_parquet(runtime_root / "candidate_grid.parquet")
    pair_grid = pd.read_parquet(runtime_root / "paired_grid.parquet")
    if (
        len(grid) != 162
        or grid["candidate_id"].nunique() != 162
        or int(grid["candidate_group"].eq("main").sum()) != 81
        or int(grid["candidate_group"].eq("placebo").sum()) != 81
        or len(pair_grid) != 81
        or pair_grid["pair_id"].nunique() != 81
        or int(grid["is_anchor"].sum()) != 1
        or str(grid.loc[grid["is_anchor"], "candidate_id"].iloc[0])
        != str(receipt["source_evidence"]["anchor_candidate_id"])
    ):
        errors.append("grid")
    stage0_path = runtime_root / "checkpoints" / "checkpoint_stage_0"
    stage_a_path = runtime_root / "checkpoints" / "checkpoint_validation_a"
    checkpoint_targets = [(stage0_path, "stage_0")]
    if decision.get("status") != "RUN_INVALID_STAGE_0_INCOMPLETE":
        checkpoint_targets.append((stage_a_path, "validation_a"))
    for path, stage in checkpoint_targets:
        try:
            _verify_checkpoint(
                path,
                expected_stage=stage,
                producer_source_sha=source_sha,
                frozen_contract_sha256=frozen_hash,
            )
        except Exception:
            errors.append(f"checkpoint:{stage}")
    stage0 = pd.read_parquet(stage0_path / "candidate_ledger.parquet")
    if decision.get("status") == "RUN_INVALID_STAGE_0_INCOMPLETE":
        if (
            len(stage0) != 162
            or stage0["strict_evaluated"].eq(True).all()
            or stage_a_path.exists()
            or decision.get("validation_b_read") is not False
        ):
            errors.append("stage0_invalid_boundary")
        recorded_a = dict(decision["stage_a_gate"])
        expected_branch = _counterfactual_decision(
            stage_a_gate=recorded_a, stage_b_gate=None
        )
    else:
        stage_a = pd.read_parquet(stage_a_path / "candidate_ledger.parquet")
        stage_a_pairs = pd.read_parquet(stage_a_path / "paired_ledger.parquet")
        if (
            len(stage0) != 162
            or not stage0["strict_evaluated"].eq(True).all()
            or not stage0["evaluation_partition"].eq("train").all()
            or not stage0["train_orientation_fitted"].eq(True).all()
            or stage0["block_robust_ordering_sha256"].isna().any()
            or len(stage_a) != 162
            or not stage_a["evaluation_partition"].dropna().eq("validation").all()
            or stage_a["train_orientation_fitted"].dropna().eq(True).any()
        ):
            errors.append("stage_identity")
        recomputed_a = stage_a_family_gate(
            stage_a.to_dict("records"),
            stage_a_pairs.to_dict("records"),
            contract=receipt["_contract"],
        )
        recorded_a = _load_json(runtime_root / "validation_a_gate.json")
        if recomputed_a != recorded_a or recomputed_a != decision.get("stage_a_gate"):
            errors.append("stage_a_gate")
        selection_path = runtime_root / "validation_b_selection_receipt.json"
        stage_b_path = runtime_root / "checkpoints" / "checkpoint_validation_b"
        if bool(recorded_a["family_gate_pass"]):
            if not selection_path.is_file() or not stage_b_path.is_dir():
                errors.append("conditional_stage_b_missing")
            else:
                selection = _load_json(selection_path)
                selection_payload = dict(selection)
                selection_hash = str(selection_payload.pop("selection_receipt_sha256"))
                if (
                    _canonical_sha256(selection_payload) != selection_hash
                    or selection.get("validation_b_read") is not False
                    or selection.get("optimizer_feedback_written") is not False
                    or selection.get("archive_written") is not False
                    or len(selection["candidate_ids"]) != len(
                        set(selection["candidate_ids"])
                    )
                    or int(selection["candidate_count"]) > 10
                ):
                    errors.append("selection_receipt")
                try:
                    _verify_checkpoint(
                        stage_b_path,
                        expected_stage="validation_b",
                        producer_source_sha=source_sha,
                        frozen_contract_sha256=frozen_hash,
                    )
                except Exception:
                    errors.append("checkpoint:validation_b")
                stage_b = pd.read_parquet(stage_b_path / "candidate_ledger.parquet")
                if (
                    set(stage_b["candidate_id"].astype(str))
                    != set(selection["candidate_ids"])
                    or len(stage_b) != int(selection["candidate_count"])
                    or not stage_b["evaluation_partition"].dropna().eq("validation").all()
                    or stage_b["train_orientation_fitted"].dropna().eq(True).any()
                ):
                    errors.append("validation_b_cohort")
                recomputed_b = stage_b_confirmation_gate(
                    stage_b.to_dict("records"),
                    selection=selection,
                    contract=receipt["_contract"],
                )
                if recomputed_b != _load_json(runtime_root / "validation_b_gate.json"):
                    errors.append("stage_b_gate")
                expected_branch = _counterfactual_decision(
                    stage_a_gate=recorded_a, stage_b_gate=recomputed_b
                )
                if decision.get("stage_b_gate") != recomputed_b:
                    errors.append("stage_b_decision")
        else:
            if selection_path.exists() or stage_b_path.exists() or bool(
                decision.get("validation_b_read")
            ):
                errors.append("validation_b_boundary")
            expected_branch = _counterfactual_decision(
                stage_a_gate=recorded_a, stage_b_gate=None
            )
    if (
        decision.get("counterfactual_preregistered_branch") != expected_branch
        or decision.get("research_decision")
        != f"REUSED_VALIDATION_DIAGNOSTIC_ONLY::{expected_branch}"
    ):
        errors.append("decision_branch")
    manifest_payload = dict(manifest)
    bundle_hash = str(manifest_payload.pop("bundle_sha256"))
    if _canonical_sha256(manifest_payload) != bundle_hash:
        errors.append("manifest_hash")
    for artifact in manifest.get("files") or []:
        path = root / str(artifact["path"])
        if (
            not path.is_file()
            or int(path.stat().st_size) != int(artifact["bytes"])
            or _file_sha256(path) != str(artifact["sha256"])
        ):
            errors.append(f"artifact:{artifact['path']}")
    if errors:
        raise RuntimeError("FUNDING_FLOW_CONFIRMATION_CHECK_FAILED:" + ",".join(errors))
    return {
        "schema_version": 1,
        "status": "CHECK_PASS",
        "producer_source_sha": source_sha,
        "bundle_sha256": bundle_hash,
        "research_decision": decision["research_decision"],
        "validation_b_read": bool(decision["validation_b_read"]),
        "holdout_read_count": 0,
        "oos_read_count": 0,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic funding-flow residual nested confirmation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "run", "check"):
        command = subparsers.add_parser(name)
        command.add_argument("--repo-root", default=".")
        command.add_argument("--receipt-path", default=RECEIPT_PATH)
        if name != "preflight":
            command.add_argument("--runtime-date", default=DEFAULT_RUNTIME_DATE)
        if name == "run":
            command.add_argument("--source-sha")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    if args.command == "preflight":
        result = preflight_confirmation(root, receipt_path=args.receipt_path)
    elif args.command == "run":
        result = run_confirmation(
            root,
            runtime_date=args.runtime_date,
            producer_source_sha=args.source_sha,
            receipt_path=args.receipt_path,
        )
    else:
        result = check_confirmation(
            root,
            runtime_date=args.runtime_date,
            receipt_path=args.receipt_path,
        )
    print(json.dumps(result, sort_keys=True, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
