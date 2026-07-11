from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq


REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from alphafactory_crypto.identity_registry import activation_identity, exact_signal_identity
from alphafactory_crypto.signal_behaviour import (
    behaviour_pair_metrics,
    canonical_weight_hash,
    cluster_behaviours,
    deterministic_weight_sketch,
    lag_persistence,
    pair_passes_contract,
    signal_to_rank_weights,
    top_bottom_masks,
    validate_observation_columns,
)
from scripts.crypto_a7ab4_materialization_preflight import A7AB4Evaluator
from scripts.crypto_a7al2x5_evaluator_preflight_smoke import shift_matrix


CONFIG = REPO / "config" / "crypto_b0a_signal_behaviour_v1.json"
HYPOTHESES = REPO / "config" / "crypto_b0p_economic_hypothesis_registry_v1.json"
RUNTIME = REPO / "runtime" / "a7b0a_signal_behaviour_20260711"
REPORT = REPO / "reports" / "CRYPTO_B0A_FROZEN_SIGNAL_BEHAVIOUR_QUALIFICATION_20260711.md"

ALIAS_SAFE_COLUMNS = [
    "blueprint_id",
    "production_key",
    "source_blueprint_id",
    "horizon_h",
    "semantic_pair",
    "motif",
    "skeleton_key",
    "expression",
    "original_expression",
    "semantic_canonical_expression",
    "semantic_rewrite_applied",
    "signal_weight_exact_fingerprint",
    "signal_weight_quantized_fingerprint",
    "representative_blueprint_id",
    "representative_expression",
    "is_signal_identity_representative",
]
ACCEPTED_SAFE_COLUMNS = [
    "blueprint_id",
    "representative_blueprint_id",
    "is_signal_identity_representative",
    "semantic_pair",
    "motif",
    "expression",
    "horizon_h",
    "signal_weight_exact_fingerprint",
]
MATERIALIZER_CODE_PATHS = [
    "alphafactory_crypto/identity_registry.py",
    "alphafactory_crypto/signal_behaviour.py",
    "alphafactory_crypto/engines/signal_identity.py",
    "scripts/crypto_a7ab4_materialization_preflight.py",
    "scripts/crypto_a7al2x5_evaluator_preflight_smoke.py",
    "scripts/crypto_b0a_frozen_signal_behaviour.py",
]
PROHIBITED_FLAGS = [
    "search_started",
    "candidate_modified",
    "generator_field_added",
    "state_event_reward_connected",
    "cem_ucb_mcts_updated",
    "a7mem_updated",
    "candidate_selection_performed",
    "forward_performance_read",
    "return_label_read",
    "reward_read",
    "spent_oos_reoptimized",
    "b1_lane_integration",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def canonical_json(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def relative(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO / path


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, lineterminator="\n", float_format="%.12g")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def bootstrap_frozen_alias_input(config: dict[str, Any]) -> dict[str, Any]:
    source = resolve_path(config["frozen_alias_provenance_source"])
    target = resolve_path(config["frozen_alias_source"])
    provenance_path = resolve_path(config["frozen_alias_provenance"])
    alias = pd.read_csv(source, usecols=ALIAS_SAFE_COLUMNS, dtype=str, keep_default_na=False)
    alias = alias.sort_values("blueprint_id").reset_index(drop=True)
    if len(alias) != 33 or alias["signal_weight_exact_fingerprint"].nunique() != 18:
        raise RuntimeError("alias bootstrap source must contain 33 rows and 18 exact identities")
    write_csv(target, alias)
    provenance = {
        "source_path": str(source).replace("\\", "/"),
        "source_sha256": sha256_file(source),
        "safe_snapshot_path": relative(target),
        "safe_snapshot_sha256": sha256_file(target),
        "allowed_columns": ALIAS_SAFE_COLUMNS,
        "performance_columns_copied": False,
    }
    write_json(provenance_path, provenance)
    return provenance


def freeze_candidate_inputs(config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    alias_source = resolve_path(config["frozen_alias_source"])
    provenance_path = resolve_path(config["frozen_alias_provenance"])
    accepted_path = resolve_path(config["accepted_pack"])
    release_path = resolve_path(config["accepted_release_manifest"])
    alias = pd.read_csv(alias_source, usecols=ALIAS_SAFE_COLUMNS, dtype=str, keep_default_na=False)
    accepted = pd.read_csv(accepted_path, usecols=ACCEPTED_SAFE_COLUMNS, dtype=str, keep_default_na=False)
    if len(alias) != 33 or alias["signal_weight_exact_fingerprint"].nunique() != 18:
        raise RuntimeError("frozen survivor mapping must contain 33 rows and 18 exact identities")
    if len(accepted) != 16 or accepted["signal_weight_exact_fingerprint"].nunique() != 6:
        raise RuntimeError("accepted pack must contain 16 rows and 6 exact identities")
    accepted_fingerprints = set(accepted["signal_weight_exact_fingerprint"])
    alias["accepted_behaviour_scope"] = alias["signal_weight_exact_fingerprint"].isin(accepted_fingerprints)
    if int(alias["accepted_behaviour_scope"].sum()) != 16:
        raise RuntimeError("accepted behaviour scope must bind 16 of the 33 frozen survivor rows")
    release = json.loads(release_path.read_text(encoding="utf-8"))
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    if sha256_file(alias_source) != provenance["safe_snapshot_sha256"]:
        raise RuntimeError("frozen alias snapshot differs from bootstrap provenance")
    expected_pack_hash = release["outputs"][accepted_path.name]["sha256"].upper()
    actual_pack_hash = sha256_file(accepted_path)
    if actual_pack_hash != expected_pack_hash:
        raise RuntimeError("accepted pack hash differs from its frozen release manifest")
    hashes = {
        "accepted_candidate_pack_sha256": actual_pack_hash,
        "accepted_release_manifest_sha256": sha256_file(release_path),
        "source_alias_map_sha256": provenance["source_sha256"],
        "frozen_alias_snapshot_sha256": provenance["safe_snapshot_sha256"],
        "safe_alias_mapping_sha256": sha256_bytes(
            alias.sort_values("blueprint_id").to_csv(index=False, lineterminator="\n").encode("utf-8")
        ),
    }
    return alias.sort_values("blueprint_id").reset_index(drop=True), accepted.sort_values("blueprint_id").reset_index(drop=True), hashes


def load_symbol_universe(config: dict[str, Any]) -> tuple[str, ...]:
    path = resolve_path(config["symbol_universe_source"])
    coverage = pd.read_csv(path, usecols=["symbol", "search_eligibility"], dtype=str)
    eligibility = config["symbol_universe_contract"]["eligibility"]
    eligible = tuple(sorted(coverage.loc[coverage["search_eligibility"].eq(eligibility), "symbol"].drop_duplicates()))
    cap = int(config["symbol_universe_contract"]["cap_after_sort"])
    symbols = eligible[:cap]
    expected = int(config["symbol_universe_contract"]["expected_symbols"])
    if len(symbols) != expected:
        raise RuntimeError(f"symbol universe count mismatch: {len(symbols)} != {expected}")
    return symbols


def field_lag_audit(config: dict[str, Any]) -> pd.DataFrame:
    required = set(config["allowed_panel_columns"]) - {"timestamp"}
    required.update(config["derived_observation_fields"])
    active_path = resolve_path(config["active_field_registry"])
    active = pd.read_csv(
        active_path,
        usecols=["field_name", "pit_lag_required", "feature_available_time_primary"],
        dtype=str,
    )
    audit = active[active["field_name"].isin(required)].drop_duplicates("field_name").sort_values("field_name").copy()
    if set(audit["field_name"]) != required:
        raise RuntimeError(f"field registry is missing B0A fields: {sorted(required - set(audit['field_name']))}")
    audit["lag_contract_pass"] = audit["pit_lag_required"].eq("+1h primary") & audit[
        "feature_available_time_primary"
    ].eq("timestamp + 1h")
    if not bool(audit["lag_contract_pass"].all()):
        raise RuntimeError("B0A field lag contract is not uniformly +1h")
    return audit


def hash_panel_release(panel_root: Path, symbols: tuple[str, ...]) -> tuple[pd.DataFrame, str]:
    rows: list[dict[str, Any]] = []
    for symbol in symbols:
        path = panel_root / f"symbol={symbol}" / "part.parquet"
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(
            {
                "symbol": symbol,
                "path": str(path).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    frame = pd.DataFrame(rows).sort_values("symbol").reset_index(drop=True)
    digest = sha256_bytes(frame.to_csv(index=False, lineterminator="\n").encode("utf-8"))
    return frame, digest


def load_observations(
    config: dict[str, Any], symbols: tuple[str, ...]
) -> tuple[pd.DatetimeIndex, dict[str, np.ndarray], dict[str, Any]]:
    columns = list(validate_observation_columns(config["allowed_panel_columns"]))
    panel_root = resolve_path(config["panel_root"])
    start = pd.Timestamp(config["development_pre_forward_interval"]["start_utc"])
    end = pd.Timestamp(config["development_pre_forward_interval"]["end_utc_inclusive"])
    timestamps = pd.date_range(start, end, freq="1h", tz="UTC")
    field_names = [column for column in columns if column != "timestamp"]
    matrices = {field: np.full((len(symbols), len(timestamps)), np.nan, dtype=np.float64) for field in field_names}
    duplicate_rows = 0
    off_grid_rows = 0
    source_rows = 0
    for symbol_index, symbol in enumerate(symbols):
        path = panel_root / f"symbol={symbol}" / "part.parquet"
        table = pq.read_table(
            path,
            columns=columns,
            partitioning=None,
            filters=[
                ("timestamp", ">=", start.tz_convert(None).to_pydatetime()),
                ("timestamp", "<=", end.tz_convert(None).to_pydatetime()),
            ],
        )
        frame = table.to_pandas()
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
        duplicate_rows += int(frame["timestamp"].duplicated().sum())
        if frame["timestamp"].duplicated().any():
            raise RuntimeError(f"duplicate observation coordinate for {symbol}")
        source_rows += len(frame)
        off_grid_rows += int((~frame["timestamp"].isin(timestamps)).sum())
        frame = frame.set_index("timestamp").reindex(timestamps)
        for field in field_names:
            matrices[field][symbol_index] = pd.to_numeric(frame[field], errors="coerce").to_numpy(dtype=np.float64)
    lag = int(config["coordinate_selection_contract"]["source_lag_hours"])
    lagged = {field: shift_matrix(values, lag) for field, values in matrices.items()}
    lagged["account_position_divergence"] = (
        lagged["top_long_short_position_ratio_last"] - lagged["top_long_short_account_ratio_last"]
    )
    lagged["top_global_account_divergence"] = (
        lagged["top_long_short_account_ratio_last"] - lagged["global_long_short_account_ratio_last"]
    )
    view_digest = hashlib.sha256()
    view_digest.update("|".join(symbols).encode("utf-8"))
    view_digest.update(np.ascontiguousarray(timestamps.asi8, dtype="<i8").tobytes())
    for field, values in sorted(lagged.items()):
        view_digest.update(field.encode("utf-8"))
        canonical = np.ascontiguousarray(np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0), dtype="<f8")
        view_digest.update(canonical.tobytes(order="C"))
        view_digest.update(np.packbits(~np.isfinite(values), axis=None).tobytes())
    audit = {
        "expected_coordinates": len(symbols) * len(timestamps),
        "source_rows": source_rows,
        "missing_source_coordinates": len(symbols) * len(timestamps) - source_rows,
        "source_coordinate_coverage": source_rows / (len(symbols) * len(timestamps)),
        "duplicate_rows": duplicate_rows,
        "off_grid_rows": off_grid_rows,
        "symbols": len(symbols),
        "timestamps": len(timestamps),
        "first_timestamp_utc": timestamps[0].isoformat(),
        "last_timestamp_utc": timestamps[-1].isoformat(),
        "source_lag_hours": lag,
        "pit_source_lag_status": "PASS_TIMESTAMP_PLUS_1H_OBSERVABLE_TIME",
        "observation_view_sha256": view_digest.hexdigest().upper(),
    }
    return timestamps, lagged, audit


def materializer_code_hash() -> tuple[list[dict[str, str]], str]:
    rows = [{"path": path, "sha256": sha256_file(REPO / path)} for path in MATERIALIZER_CODE_PATHS]
    return rows, sha256_bytes(canonical_json(rows))


def _month_labels(timestamps: pd.DatetimeIndex) -> np.ndarray:
    return timestamps.strftime("%Y-%m").to_numpy(dtype=str)


def _profile_rows(
    pack_id: str,
    activation: np.ndarray,
    symbols: tuple[str, ...],
    timestamps: pd.DatetimeIndex,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    rows: list[dict[str, Any]] = []
    month_labels = _month_labels(timestamps)
    symbol_month_values: list[float] = []
    for symbol_index, symbol in enumerate(symbols):
        value = float(activation[symbol_index].mean())
        rows.append({"pack_exact_fingerprint": pack_id, "profile_type": "symbol", "profile_key": symbol, "activation_share": value})
        for month in sorted(set(month_labels)):
            mask = month_labels == month
            month_value = float(activation[symbol_index, mask].mean())
            symbol_month_values.append(month_value)
            rows.append(
                {
                    "pack_exact_fingerprint": pack_id,
                    "profile_type": "symbol_month",
                    "profile_key": f"{symbol}|{month}",
                    "activation_share": month_value,
                }
            )
    for month in sorted(set(month_labels)):
        mask = month_labels == month
        rows.append(
            {
                "pack_exact_fingerprint": pack_id,
                "profile_type": "month",
                "profile_key": month,
                "activation_share": float(activation[:, mask].mean()),
            }
        )
    hours = timestamps.hour.to_numpy()
    sessions = {
        "ASIA_00_07_UTC": (hours >= 0) & (hours < 8),
        "EUROPE_08_15_UTC": (hours >= 8) & (hours < 16),
        "AMERICAS_16_23_UTC": (hours >= 16) & (hours < 24),
    }
    for name, mask in sessions.items():
        rows.append(
            {
                "pack_exact_fingerprint": pack_id,
                "profile_type": "session",
                "profile_key": name,
                "activation_share": float(activation[:, mask].mean()),
            }
        )
    return rows, np.asarray(symbol_month_values, dtype=np.float64)


def _behaviour_id(pack_id: str, weight_hash: str, activation_id: str, persistence: np.ndarray, stability: np.ndarray) -> str:
    payload = (
        pack_id.encode("ascii")
        + weight_hash.encode("ascii")
        + activation_id.encode("ascii")
        + np.ascontiguousarray(np.nan_to_num(persistence), dtype="<f8").tobytes()
        + np.ascontiguousarray(stability, dtype="<f8").tobytes()
    )
    return "behaviour:" + hashlib.sha256(payload).hexdigest()[:24]


def materialize_once(
    expressions: dict[str, str],
    numeric: dict[str, np.ndarray],
    symbols: tuple[str, ...],
    timestamps: pd.DatetimeIndex,
    config: dict[str, Any],
    *,
    reverse_order: bool = False,
) -> dict[str, dict[str, Any]]:
    evaluator = A7AB4Evaluator(numeric, {})
    selection = config["selection_contract"]
    lags = config["persistence_lags_hours"]
    ordered_ids = sorted(expressions, reverse=reverse_order)
    result: dict[str, dict[str, Any]] = {}
    for pack_id in ordered_ids:
        signal = evaluator.eval(expressions[pack_id])
        ranks, weights = signal_to_rank_weights(
            signal,
            gross=float(selection["gross"]),
            max_abs_weight=float(selection["max_abs_weight"]),
        )
        missing = ~np.isfinite(signal)
        activation = (np.abs(weights) > float(selection["activation_epsilon"])) & ~missing
        positive = (weights > float(selection["activation_epsilon"])) & ~missing
        negative = (weights < -float(selection["activation_epsilon"])) & ~missing
        top, bottom = top_bottom_masks(
            ranks,
            top_fraction=float(selection["top_fraction"]),
            bottom_fraction=float(selection["bottom_fraction"]),
        )
        top &= ~missing
        bottom &= ~missing
        activation_id = activation_identity(activation, universe_ids=symbols, timestamps_ns=timestamps.asi8)
        persistence = lag_persistence(weights, lags)
        profile_rows, stability = _profile_rows(pack_id, activation, symbols, timestamps)
        weight_hash = canonical_weight_hash(weights)
        behaviour_id = _behaviour_id(pack_id, weight_hash, activation_id, persistence, stability)
        result[pack_id] = {
            "expression": expressions[pack_id],
            "signal": signal,
            "ranks": ranks,
            "weights": weights,
            "missing": missing,
            "activation": activation,
            "positive": positive,
            "negative": negative,
            "top": top,
            "bottom": bottom,
            "activation_identity": activation_id,
            "b0a_exact_weight_sha256": weight_hash,
            "behaviour_identity": behaviour_id,
            "persistence": persistence,
            "stability": stability,
            "profile_rows": profile_rows,
            "weight_sketch": deterministic_weight_sketch(weights, size=int(config["weight_sketch_size"])),
        }
    return {pack_id: result[pack_id] for pack_id in sorted(result)}


def pairwise_rows(materialized: dict[str, dict[str, Any]], thresholds: dict[str, float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left, right in combinations(sorted(materialized), 2):
        a, b = materialized[left], materialized[right]
        metrics = behaviour_pair_metrics(
            a["weights"],
            b["weights"],
            a["activation"],
            b["activation"],
            a["top"],
            b["top"],
            a["bottom"],
            b["bottom"],
            persistence_left=a["persistence"],
            persistence_right=b["persistence"],
            stability_left=a["stability"],
            stability_right=b["stability"],
        )
        row: dict[str, Any] = {"left": left, "right": right, **metrics}
        row["same_behaviour_cluster_edge"] = pair_passes_contract(row, thresholds)
        rows.append(row)
    return rows


def deterministic_artifact_bytes(
    materialized: dict[str, dict[str, Any]], symbols: tuple[str, ...], timestamps: pd.DatetimeIndex
) -> bytes:
    signal_ids = sorted(materialized)
    header = {
        "schema": "crypto.b0a.signal-behaviour-sketch.v1",
        "axis_order": "signal,symbol,timestamp",
        "signal_ids": signal_ids,
        "symbols": list(symbols),
        "timestamps_sha256": sha256_bytes(np.ascontiguousarray(timestamps.asi8, dtype="<i8").tobytes()),
        "arrays_per_signal": ["weight_sketch_f4", "activation_packbits", "missing_packbits", "positive_packbits", "negative_packbits", "top_packbits", "bottom_packbits"],
        "weight_hashes": {signal_id: materialized[signal_id]["b0a_exact_weight_sha256"] for signal_id in signal_ids},
    }
    header_bytes = canonical_json(header)
    payload = bytearray(b"B0ASB1\n" + struct.pack("<Q", len(header_bytes)) + header_bytes)
    for signal_id in signal_ids:
        item = materialized[signal_id]
        payload.extend(np.ascontiguousarray(item["weight_sketch"], dtype="<f4").tobytes())
        for name in ["activation", "missing", "positive", "negative", "top", "bottom"]:
            payload.extend(np.packbits(item[name], axis=None, bitorder="little").tobytes())
    return bytes(payload)


def time_slice_stability(
    materialized: dict[str, dict[str, Any]],
    timestamps: pd.DatetimeIndex,
    thresholds: dict[str, float],
    global_clusters: dict[str, str],
) -> pd.DataFrame:
    quarters = timestamps.tz_localize(None).to_period("Q").astype(str).to_numpy()
    rows: list[dict[str, Any]] = []
    ids = sorted(materialized)
    for quarter in sorted(set(quarters)):
        mask = quarters == quarter
        sliced: dict[str, dict[str, Any]] = {}
        for signal_id, item in materialized.items():
            weights = item["weights"][:, mask]
            activation = item["activation"][:, mask]
            top = item["top"][:, mask]
            bottom = item["bottom"][:, mask]
            persistence = lag_persistence(weights, [1, 24, 168])
            stability = activation.mean(axis=1)
            sliced[signal_id] = {
                "weights": weights,
                "activation": activation,
                "top": top,
                "bottom": bottom,
                "persistence": persistence,
                "stability": stability,
            }
        pair_rows = pairwise_rows(sliced, thresholds)
        clusters = cluster_behaviours(ids, pair_rows, thresholds)
        agreements = [
            (clusters[a] == clusters[b]) == (global_clusters[a] == global_clusters[b])
            for a, b in combinations(ids, 2)
        ]
        rows.append(
            {
                "time_slice": quarter,
                "timestamp_count": int(mask.sum()),
                "pair_cluster_assignment_agreement": float(np.mean(agreements)),
                "median_pair_rank_correlation": float(np.median([row["rank_correlation"] for row in pair_rows])),
                "behaviour_cluster_count": len(set(clusters.values())),
            }
        )
    return pd.DataFrame(rows)


def build(runtime: Path = RUNTIME, report: Path = REPORT) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    config = load_config()
    alias, accepted, input_hashes = freeze_candidate_inputs(config)
    symbols = load_symbol_universe(config)
    lag_audit = field_lag_audit(config)
    panel_hash_rows, data_release_hash = hash_panel_release(resolve_path(config["panel_root"]), symbols)
    timestamps, numeric, coordinate_audit = load_observations(config, symbols)

    accepted_ids = sorted(accepted["signal_weight_exact_fingerprint"].unique())
    expressions: dict[str, str] = {}
    for pack_id in accepted_ids:
        candidates = sorted(set(accepted.loc[accepted["signal_weight_exact_fingerprint"].eq(pack_id), "expression"]))
        expressions[pack_id] = candidates[0]
    first = materialize_once(expressions, numeric, symbols, timestamps, config)
    second = materialize_once(expressions, numeric, symbols, timestamps, config, reverse_order=True)
    first_bytes = deterministic_artifact_bytes(first, symbols, timestamps)
    second_bytes = deterministic_artifact_bytes(second, symbols, timestamps)
    first_hash = sha256_bytes(first_bytes)
    second_hash = sha256_bytes(second_bytes)
    reproducible = first_hash == second_hash

    reconstructed_by_pack: dict[str, set[str]] = {pack_id: set() for pack_id in accepted_ids}
    evaluator = A7AB4Evaluator(numeric, {})
    selection = config["selection_contract"]
    for row in accepted.to_dict("records"):
        _, weights = signal_to_rank_weights(
            evaluator.eval(row["expression"]),
            gross=float(selection["gross"]),
            max_abs_weight=float(selection["max_abs_weight"]),
        )
        reconstructed_by_pack[row["signal_weight_exact_fingerprint"]].add(canonical_weight_hash(weights))
    alias_reconstruction_pass = all(len(hashes) == 1 for hashes in reconstructed_by_pack.values())
    b0a_hash_by_pack = {pack_id: next(iter(hashes)) for pack_id, hashes in reconstructed_by_pack.items()}
    if b0a_hash_by_pack != {pack_id: first[pack_id]["b0a_exact_weight_sha256"] for pack_id in accepted_ids}:
        raise RuntimeError("accepted alias reconstruction does not match representative materialization")

    thresholds = config["behaviour_cluster_thresholds"]
    pair_rows = pairwise_rows(first, thresholds)
    clusters = cluster_behaviours(accepted_ids, pair_rows, thresholds)
    time_stability = time_slice_stability(first, timestamps, thresholds, clusters)
    hypotheses_config = json.loads(HYPOTHESES.read_text(encoding="utf-8"))
    hypothesis_by_pack = {
        row["signal_weight_exact_fingerprint"]: row["hypothesis_id"] for row in hypotheses_config["assignments"]
    }
    if set(accepted_ids).difference(hypothesis_by_pack):
        raise RuntimeError("accepted signal is missing its frozen economic hypothesis")

    cluster_rows: list[dict[str, Any]] = []
    coverage_rows: list[dict[str, Any]] = []
    persistence_rows: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []
    for pack_id, item in first.items():
        signal = item["signal"]
        finite = np.isfinite(signal)
        coverage_rows.append(
            {
                "pack_exact_fingerprint": pack_id,
                "registered_exact_signal_identity": exact_signal_identity(pack_id),
                "b0a_exact_weight_sha256": item["b0a_exact_weight_sha256"],
                "activation_identity": item["activation_identity"],
                "behaviour_identity": item["behaviour_identity"],
                "behaviour_cluster": clusters[pack_id],
                "economic_hypothesis": hypothesis_by_pack[pack_id],
                "finite_share": float(finite.mean()),
                "missing_share": float(item["missing"].mean()),
                "activation_share": float(item["activation"].mean()),
                "positive_weight_share": float((item["weights"] > 0).mean()),
                "negative_weight_share": float((item["weights"] < 0).mean()),
                "top_selection_share": float(item["top"].mean()),
                "bottom_selection_share": float(item["bottom"].mean()),
            }
        )
        cluster_rows.append(
            {
                "pack_exact_fingerprint": pack_id,
                "registered_exact_signal_identity": exact_signal_identity(pack_id),
                "activation_identity": item["activation_identity"],
                "behaviour_identity": item["behaviour_identity"],
                "behaviour_cluster": clusters[pack_id],
                "economic_hypothesis": hypothesis_by_pack[pack_id],
                "feedback_permission": "NONE_NO_SELECTION_MEMORY_SCHEDULER_GENERATOR_OR_REWARD",
            }
        )
        for lag, value in zip(config["persistence_lags_hours"], item["persistence"]):
            persistence_rows.append(
                {"pack_exact_fingerprint": pack_id, "lag_hours": lag, "holding_weight_correlation": value}
            )
        profile_rows.extend(item["profile_rows"])

    alias["registered_exact_signal_identity"] = alias["signal_weight_exact_fingerprint"].map(
        {pack_id: exact_signal_identity(pack_id) for pack_id in accepted_ids}
    ).fillna("")
    alias["b0a_exact_weight_sha256"] = alias["signal_weight_exact_fingerprint"].map(b0a_hash_by_pack).fillna("")
    alias["activation_identity"] = alias["signal_weight_exact_fingerprint"].map(
        {pack_id: first[pack_id]["activation_identity"] for pack_id in accepted_ids}
    ).fillna("")
    alias["behaviour_cluster"] = alias["signal_weight_exact_fingerprint"].map(clusters).fillna("")
    alias["scope_note"] = np.where(
        alias["accepted_behaviour_scope"],
        "MATERIALIZED_ACCEPTED_SCOPE",
        "FROZEN_SURVIVOR_MAPPING_ONLY_NOT_ACCEPTED_BEHAVIOUR_SCOPE",
    )

    cluster_counts = Counter(clusters.values())
    sizes = np.asarray(list(cluster_counts.values()), dtype=np.float64)
    n_eff = float((sizes.sum() ** 2) / np.sum(sizes**2))
    top_cluster_share = float(sizes.max() / sizes.sum())
    code_rows, code_hash = materializer_code_hash()
    input_hashes.update(
        {
            "source_panel_container_sha256": data_release_hash,
            "data_release_sha256": coordinate_audit["observation_view_sha256"],
            "observation_view_sha256": coordinate_audit["observation_view_sha256"],
            "field_registry_sha256": sha256_file(resolve_path(config["field_registry"])),
            "active_field_registry_sha256": sha256_file(resolve_path(config["active_field_registry"])),
            "symbol_universe_source_sha256": sha256_file(resolve_path(config["symbol_universe_source"])),
            "materializer_code_sha256": code_hash,
        }
    )

    (runtime / "signal_behaviour_sketch.bin").write_bytes(first_bytes)
    write_csv(runtime / "frozen_alias_expression_map.csv", alias)
    write_csv(runtime / "panel_release_file_hashes.csv", panel_hash_rows)
    write_csv(runtime / "field_source_lag_audit.csv", lag_audit)
    write_csv(runtime / "signal_coverage_profile.csv", pd.DataFrame(coverage_rows).sort_values("pack_exact_fingerprint"))
    write_csv(runtime / "temporal_persistence_profile.csv", pd.DataFrame(persistence_rows).sort_values(["pack_exact_fingerprint", "lag_hours"]))
    write_csv(runtime / "symbol_month_session_activation_profile.csv", pd.DataFrame(profile_rows).sort_values(["pack_exact_fingerprint", "profile_type", "profile_key"]))
    write_csv(runtime / "behaviour_pair_metrics.csv", pd.DataFrame(pair_rows).sort_values(["left", "right"]))
    write_csv(runtime / "activation_behaviour_identity_registry.csv", pd.DataFrame(cluster_rows).sort_values("pack_exact_fingerprint"))
    write_csv(runtime / "time_slice_stability.csv", time_stability)
    write_json(runtime / "materializer_code_hashes.json", {"files": code_rows, "combined_sha256": code_hash})

    qualified = bool(
        reproducible
        and alias_reconstruction_pass
        and coordinate_audit["duplicate_rows"] == 0
        and coordinate_audit["off_grid_rows"] == 0
        and len(symbols) == 96
        and len(accepted_ids) == 6
        and len(set(item["activation_identity"] for item in first.values())) >= 1
        and len(set(hypothesis_by_pack[pack_id] for pack_id in accepted_ids)) == 5
    )
    decision = "FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED" if qualified else (
        "FROZEN_SIGNAL_BEHAVIOUR_NOT_REPRODUCIBLE" if not reproducible else "FROZEN_SIGNAL_BEHAVIOUR_PARTIALLY_QUALIFIED"
    )
    manifest: dict[str, Any] = {
        "manifest_id": "CRYPTO-B0A-FROZEN-SIGNAL-BEHAVIOUR-20260711",
        "decision": decision,
        "b0p_accepted_subject_sha": "5219e7899cad1be83f9bcf2ec520ed1ff5037f9e",
        "b0p_partial_acceptance_commit": "b52eabae665f0e5a9ce0ae63fa2355ea0f28c769",
        "input_hashes": input_hashes,
        "coordinate_audit": coordinate_audit,
        "symbol_universe": list(symbols),
        "full_survivor_rows": int(len(alias)),
        "full_survivor_exact_identities": int(alias["signal_weight_exact_fingerprint"].nunique()),
        "accepted_alias_rows_materialized": int(alias["accepted_behaviour_scope"].sum()),
        "canonical_exact_signals_materialized": len(accepted_ids),
        "activation_identities": len(set(item["activation_identity"] for item in first.values())),
        "behaviour_identities": len(set(item["behaviour_identity"] for item in first.values())),
        "behaviour_clusters": len(cluster_counts),
        "economic_hypotheses": len(set(hypothesis_by_pack[pack_id] for pack_id in accepted_ids)),
        "n_eff": n_eff,
        "top_cluster_share": top_cluster_share,
        "cross_time_slice_stability_median": float(time_stability["pair_cluster_assignment_agreement"].median()),
        "cross_time_slice_stability_min": float(time_stability["pair_cluster_assignment_agreement"].min()),
        "artifact_path": relative(runtime / "signal_behaviour_sketch.bin"),
        "artifact_sha256": first_hash,
        "repeat_artifact_sha256": second_hash,
        "reproducible": reproducible,
        "alias_reconstruction_pass": alias_reconstruction_pass,
        "identity_dimension_note": "33 frozen source-lag survivors contain 18 exact identities; the accepted behaviour scope is 16 restored aliases mapped to 6 exact signals",
        "exact_identity_contract": "registered pack exact fingerprint maps to a coordinate-specific B0A exact weight SHA; aliases sharing a pack fingerprint must reconstruct to one B0A SHA",
        "pnl_regime_status": "SPENT_HISTORICAL_DIAGNOSTIC_ONLY",
        "pnl_regime_selection_permission": "NO_SELECTION",
        "pnl_regime_memory_permission": "NO_MEMORY",
        "pnl_regime_scheduler_permission": "NO_SCHEDULER_FEEDBACK",
        **{flag: False for flag in PROHIBITED_FLAGS},
        "hold_research": True,
        "phase_b1_frozen": True,
        "sealed_no_new_forward_read": True,
    }
    write_json(runtime / "b0a_run_manifest.json", manifest)

    report.write_text(
        "\n".join(
            [
                "# Crypto B0A Frozen Signal Behaviour Qualification",
                "",
                f"Decision: `{decision}`",
                "",
                "## Frozen Inputs",
                "",
                f"- accepted candidate pack SHA256: `{input_hashes['accepted_candidate_pack_sha256']}`",
                f"- 33-row alias mapping SHA256: `{input_hashes['safe_alias_mapping_sha256']}`",
                f"- observation data release SHA256: `{input_hashes['data_release_sha256']}`",
                f"- physical panel container SHA256: `{input_hashes['source_panel_container_sha256']}`",
                f"- field registry SHA256: `{input_hashes['field_registry_sha256']}`",
                f"- materializer code SHA256: `{input_hashes['materializer_code_sha256']}`",
                f"- interval: `{coordinate_audit['first_timestamp_utc']}` through `{coordinate_audit['last_timestamp_utc']}`",
                f"- coordinates: `{len(symbols)} symbols x {len(timestamps)} hourly timestamps`",
                f"- source coordinate coverage: `{coordinate_audit['source_coordinate_coverage']:.9f}`; missing coordinates are reindexed and preserved in the missingness mask",
                "",
                "## Identity Compression",
                "",
                f"- frozen source-lag survivor mapping: `33 rows -> 18 exact identities`",
                f"- accepted behaviour scope: `16 restored aliases -> 6 canonical/exact signals -> {manifest['activation_identities']} activation identities -> {manifest['behaviour_clusters']} behaviour clusters -> 5 economic hypotheses`",
                f"- N_eff: `{n_eff:.6f}`",
                f"- top-cluster share: `{top_cluster_share:.6f}`",
                f"- cross-time slice stability median/min: `{manifest['cross_time_slice_stability_median']:.6f}` / `{manifest['cross_time_slice_stability_min']:.6f}`",
                "",
                "The 33 survivor rows must not be misstated as six exact signals: only the 16 accepted restored rows map to the six accepted exact identities. The remaining 17 survivor rows are frozen provenance but are outside accepted behaviour qualification.",
                "",
                "## Reproducibility",
                "",
                f"- first artifact SHA256: `{first_hash}`",
                f"- repeated reversed-order artifact SHA256: `{second_hash}`",
                f"- reproducible: `{reproducible}`",
                f"- alias reconstruction: `{alias_reconstruction_pass}`",
                "",
                "## Boundaries",
                "",
                "No return label, reward, new forward/OOS performance, search, candidate modification, candidate selection, scheduler feedback, or memory update was used. PnL/regime remains `SPENT_HISTORICAL_DIAGNOSTIC_ONLY / NO_SELECTION / NO_MEMORY / NO_SCHEDULER_FEEDBACK`.",
                "Phase B1 remains frozen.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["bootstrap", "build", "check"])
    args = parser.parse_args()
    if args.mode == "bootstrap":
        print(json.dumps(bootstrap_frozen_alias_input(load_config()), indent=2, sort_keys=True))
        return
    if args.mode == "build":
        print(json.dumps(build(), indent=2, sort_keys=True))
        return
    manifest = json.loads((RUNTIME / "b0a_run_manifest.json").read_text(encoding="utf-8"))
    artifact_hash = sha256_file(RUNTIME / "signal_behaviour_sketch.bin")
    if manifest["artifact_sha256"] != artifact_hash or not manifest["reproducible"]:
        raise SystemExit("B0A artifact drift or non-reproducibility")
    if any(manifest.get(flag) for flag in PROHIBITED_FLAGS):
        raise SystemExit("B0A manifest records prohibited activity")
    current_code_hash = materializer_code_hash()[1]
    if manifest["input_hashes"]["materializer_code_sha256"] != current_code_hash:
        raise SystemExit("B0A materializer code hash drift")
    config = load_config()
    if manifest["input_hashes"]["accepted_candidate_pack_sha256"] != sha256_file(resolve_path(config["accepted_pack"])):
        raise SystemExit("B0A accepted candidate pack hash drift")
    if manifest["input_hashes"]["field_registry_sha256"] != sha256_file(resolve_path(config["field_registry"])):
        raise SystemExit("B0A field registry hash drift")
    provenance = json.loads(resolve_path(config["frozen_alias_provenance"]).read_text(encoding="utf-8"))
    if manifest["input_hashes"]["frozen_alias_snapshot_sha256"] != sha256_file(resolve_path(config["frozen_alias_source"])):
        raise SystemExit("B0A frozen alias snapshot hash drift")
    if provenance["safe_snapshot_sha256"] != manifest["input_hashes"]["frozen_alias_snapshot_sha256"]:
        raise SystemExit("B0A alias provenance mismatch")
    if manifest["decision"] not in {
        "FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED",
        "FROZEN_SIGNAL_BEHAVIOUR_PARTIALLY_QUALIFIED",
        "FROZEN_SIGNAL_BEHAVIOUR_NOT_REPRODUCIBLE",
    }:
        raise SystemExit("invalid B0A terminal decision")
    print("PASS_B0A_SIGNAL_BEHAVIOUR_ARTIFACT_VALID")


if __name__ == "__main__":
    main()
