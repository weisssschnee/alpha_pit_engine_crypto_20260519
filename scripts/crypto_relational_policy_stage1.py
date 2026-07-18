#!/usr/bin/env python3
"""Run the temporary fixed-budget relational layer attribution.

This is deliberately one thin runner, not a search or experiment platform.
It supports cache provisioning, one-batch local/PC2 parity, the six frozen
arm/seed fits, and evidence verification.  It never opens sealed roles or
executes Stage 2.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.broad_information_arena import array_sha256
from alphafactory_crypto.broad_search.panel18m import build_raw_panel_cache
from alphafactory_crypto.relational_policy import (
    RELATIONAL_ARM,
    SHIFTED_RELATIONAL_NULL_ARM,
    STAGE1_ARMS,
    TEMPORAL_ONLY_ARM,
    decide_stage1,
    identical_initialized_models,
    load_stage1_context,
    materialize_stage1_batch,
    stage1_block_metrics,
    stage1_data_identity,
    stage1_pair_metrics,
    torch_state_sha256,
)


DEFAULT_CONFIG = ROOT / "config" / "crypto_relational_policy_stage1_v1.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def _payload_sha256(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _git_sha(root: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip().lower()


def _git_is_ancestor(ancestor: str, descendant: str, root: Path = ROOT) -> bool:
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        ).returncode
        == 0
    )


def _runtime_identity() -> dict[str, Any]:
    packages: dict[str, str] = {}
    for name in ("numpy", "pandas", "pyarrow", "torch"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "NOT_INSTALLED"
    return {
        "python": platform.python_version(),
        "packages": packages,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "torch_threads": torch.get_num_threads(),
    }


def _model_kwargs(config: Mapping[str, Any], batch: Any) -> dict[str, int]:
    model = config["model"]
    return {
        "asset_features": int(batch.asset_values.shape[-1]),
        "market_features": int(batch.market_values.shape[-1]),
        "hidden_size": int(model["hidden_size"]),
        "attention_heads": int(model["attention_heads"]),
        "temporal_kernel": int(model["temporal_kernel"]),
    }


def _load_token_identity(config: Mapping[str, Any]) -> str:
    payload = _read_json(ROOT / str(config["inputs"]["resolved_core_pack"]))
    return str(payload["identity_sha256"])


def parity_payload(config_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    config = _read_json(config_path)
    torch.set_num_threads(int(config["training"]["torch_threads"]))
    context = load_stage1_context(ROOT, config)
    requested = pd.Timestamp(config["parity"]["decision_timestamp"]).value
    coordinate = int(np.searchsorted(context.timestamps, requested, side="left"))
    if coordinate >= len(context.timestamps) or int(context.timestamps[coordinate]) != int(
        requested
    ):
        raise ValueError("frozen parity timestamp is absent")
    batch = materialize_stage1_batch(context, config, [coordinate])
    inputs = batch.model_inputs()
    input_hashes = {
        name: array_sha256(value.detach().cpu().numpy())
        for name, value in inputs.items()
    }
    input_hashes.update(
        {
            "target_returns": array_sha256(batch.target_returns.numpy()),
            "target_valid": array_sha256(batch.target_valid.numpy()),
        }
    )
    outputs: dict[str, dict[str, Any]] = {}
    parameter_counts: dict[str, int] = {}
    initial_state_hashes: dict[str, str] = {}
    with torch.no_grad():
        for seed in config["training"]["seeds"]:
            models = identical_initialized_models(
                arms=tuple(config["training"]["arms"]),
                seed=int(seed),
                **_model_kwargs(config, batch),
            )
            for arm, model in models.items():
                model.eval()
                key = f"{arm}:{int(seed)}"
                score = model(arm=arm, **inputs).detach().cpu().numpy()
                outputs[key] = {
                    "shape": list(score.shape),
                    "sha256": array_sha256(score),
                    "values": score.astype(float).reshape(-1).tolist(),
                }
                parameter_counts[key] = sum(
                    parameter.numel() for parameter in model.parameters()
                )
                initial_state_hashes[key] = torch_state_sha256(model)
    data_identity = stage1_data_identity(context, config)
    elapsed = time.perf_counter() - started
    if elapsed > float(config["budget"]["maximum_parity_minutes"]) * 60.0:
        raise TimeoutError("parity exceeded its frozen time budget")
    return {
        "schema_version": 1,
        "kind": "RELATIONAL_POLICY_STAGE1_SINGLE_BATCH_PARITY_SIDE",
        "source_sha": _git_sha(),
        "config_sha256": _payload_sha256(config),
        "token_contract_identity_sha256": _load_token_identity(config),
        "data_identity": data_identity,
        "schedule_identity_sha256": context.schedule_identity_sha256,
        "scaler_identity_sha256": context.scaler.identity_sha256,
        "selected_asset_ids": list(context.selected_symbols),
        "decision_timestamp": config["parity"]["decision_timestamp"],
        "decision_coordinate": coordinate,
        "input_sha256": input_hashes,
        "parameter_counts": parameter_counts,
        "initial_state_sha256": initial_state_hashes,
        "outputs": outputs,
        "donor_current_membership_mismatch": batch.donor_current_membership_mismatch,
        "runtime": _runtime_identity(),
        "wall_seconds": elapsed,
    }


def compare_parity(
    local_path: Path, remote_path: Path, config_path: Path
) -> dict[str, Any]:
    config = _read_json(config_path)
    local = _read_json(local_path)
    remote = _read_json(remote_path)
    exact_fields = (
        "source_sha",
        "config_sha256",
        "token_contract_identity_sha256",
        "schedule_identity_sha256",
        "scaler_identity_sha256",
        "selected_asset_ids",
        "decision_timestamp",
        "decision_coordinate",
        "input_sha256",
        "parameter_counts",
        "initial_state_sha256",
    )
    mismatches = [name for name in exact_fields if local.get(name) != remote.get(name)]
    if (
        local["data_identity"]["logical_content_identity_sha256"]
        != remote["data_identity"]["logical_content_identity_sha256"]
    ):
        mismatches.append("logical_data_content_identity")
    if local["runtime"]["python"] != remote["runtime"]["python"]:
        mismatches.append("python_version")
    if local["runtime"]["packages"] != remote["runtime"]["packages"]:
        mismatches.append("package_versions")
    atol = float(config["parity"]["absolute_tolerance"])
    rtol = float(config["parity"]["relative_tolerance"])
    output_rows: list[dict[str, Any]] = []
    for key in sorted(local["outputs"]):
        if key not in remote["outputs"]:
            mismatches.append(f"missing_output:{key}")
            continue
        left = np.asarray(local["outputs"][key]["values"], dtype=float)
        right = np.asarray(remote["outputs"][key]["values"], dtype=float)
        if left.shape != right.shape:
            mismatches.append(f"output_shape:{key}")
            continue
        difference = np.abs(left - right)
        maximum_abs = float(np.max(difference)) if difference.size else 0.0
        denominator = np.maximum(np.abs(left), np.abs(right))
        maximum_rel = float(
            np.max(np.divide(difference, denominator, out=np.zeros_like(difference), where=denominator > 0.0))
        ) if difference.size else 0.0
        passed = bool(np.allclose(left, right, atol=atol, rtol=rtol))
        if not passed:
            mismatches.append(f"output_numeric:{key}")
        output_rows.append(
            {
                "model": key,
                "maximum_absolute_difference": maximum_abs,
                "maximum_relative_difference": maximum_rel,
                "passed": passed,
            }
        )
    status = "PASS" if not mismatches else "STOP_BEFORE_TRAINING"
    return {
        "schema_version": 1,
        "kind": "RELATIONAL_POLICY_STAGE1_LOCAL_PC2_PARITY",
        "status": status,
        "source_sha": local["source_sha"],
        "config_sha256": local["config_sha256"],
        "token_contract_identity_sha256": local[
            "token_contract_identity_sha256"
        ],
        "logical_data_content_identity_sha256": local["data_identity"][
            "logical_content_identity_sha256"
        ],
        "local_metadata_cache_identity_sha256": local["data_identity"].get(
            "metadata_identity_sha256"
        ),
        "remote_metadata_cache_identity_sha256": remote["data_identity"].get(
            "metadata_identity_sha256"
        ),
        "metadata_identity_portability_note": "metadata identity includes source SHA and build duration; logical used-prefix content identity is the cross-machine authority",
        "absolute_tolerance": atol,
        "relative_tolerance": rtol,
        "mismatches": mismatches,
        "output_comparison": output_rows,
        "local_runtime": local["runtime"],
        "remote_runtime": remote["runtime"],
        "local_wall_seconds": local["wall_seconds"],
        "remote_wall_seconds": remote["wall_seconds"],
        "local_side": local,
        "remote_side": remote,
    }


def _data_adequacy(context: Any, config: Mapping[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    selected = context.selected_asset_indices
    shift = int(config["data_contract"]["peer_shift_hours"])
    thresholds = config["data_adequacy"]
    for block in config["splits"]["attribution_blocks"]:
        block_id = str(block["block_id"])
        coordinates = context.schedules[block_id]
        nonnull: list[float] = []
        varying = 0
        for values in context.field_arrays:
            raw = np.asarray(values[selected[:, None], coordinates[None, :]], dtype=float)
            nonnull.append(float(np.isfinite(raw).mean()))
            varying += int(np.nanvar(raw) > 0.0)
        for index in range(len(context.market_fields)):
            raw = np.asarray(context.market_series[coordinates, index], dtype=float)
            nonnull.append(float(np.isfinite(raw).mean()))
            varying += int(np.nanvar(raw) > 0.0)
        current = np.asarray(
            context.eligibility[selected[:, None], coordinates[None, :]], dtype=bool
        )
        donor = np.asarray(
            context.eligibility[
                selected[:, None], (coordinates - shift)[None, :]
            ],
            dtype=bool,
        )
        target = np.asarray(
            context.target[selected[:, None], coordinates[None, :]], dtype=float
        )
        valid = current & np.isfinite(target)
        effective = valid.sum(axis=0)
        dispersions = [
            float(np.std(target[:, index][valid[:, index]]))
            for index in range(target.shape[1])
            if valid[:, index].sum() >= 3
        ]
        row = {
                "block_id": block_id,
                "decision_coordinates": int(len(coordinates)),
                "eligible_label_samples": int(valid.sum()),
                "median_effective_assets": float(np.median(effective)),
                "minimum_effective_assets": int(np.min(effective)),
                "minimum_field_nonnull_ratio": float(min(nonnull)),
                "loadable_fields": len(nonnull),
                "block_variable_fields": int(varying),
                "minimum_cross_sectional_target_std": float(min(dispersions)),
                "donor_current_membership_mismatch": float(np.mean(current != donor)),
            }
        row["checks"] = {
            "decision_coordinates": row["decision_coordinates"]
            >= int(thresholds["minimum_block_decision_coordinates"]),
            "eligible_labels": row["eligible_label_samples"]
            >= int(thresholds["minimum_block_eligible_labels"]),
            "effective_assets": row["median_effective_assets"]
            >= float(thresholds["minimum_median_effective_assets"]),
            "field_nonnull": row["minimum_field_nonnull_ratio"]
            >= float(thresholds["minimum_field_nonnull_ratio"]),
            "variable_fields": row["block_variable_fields"]
            >= int(thresholds["minimum_block_variable_fields"]),
            "target_dispersion": row["minimum_cross_sectional_target_std"]
            > float(thresholds["minimum_cross_sectional_target_std"]),
        }
        row["passed"] = all(row["checks"].values())
        rows.append(row)
    passed = len(rows) == 6 and all(row["passed"] for row in rows)
    return {
        "status": "DATA_ADEQUACY_PASS" if passed else "DATA_ADEQUACY_UNDERPOWERED",
        "scope": "39_REGISTERED_LOADABLE_FIELDS_WITH_BLOCK_VARIATION_REPORTED_SEPARATELY",
        "thresholds": thresholds,
        "blocks": rows,
    }


def _arm_nondegeneracy(
    rows: list[dict[str, Any]], config: Mapping[str, Any]
) -> dict[str, bool]:
    gate = config["nondegeneracy"]
    expected = len(config["training"]["seeds"]) * len(
        config["splits"]["attribution_blocks"]
    )
    result: dict[str, bool] = {}
    for arm in STAGE1_ARMS:
        local = [
            row
            for row in rows
            if row["row_type"] == "ARM_BLOCK" and row["arm"] == arm
        ]
        result[arm] = len(local) == expected and all(
            bool(row["finite_metrics"])
            and float(row["prediction_variance"])
            > float(gate["minimum_prediction_variance"])
            and float(row["mean_cross_sectional_prediction_variance"])
            > float(gate["minimum_mean_cross_sectional_prediction_variance"])
            and float(row["mean_temporal_prediction_variance"])
            > float(gate["minimum_mean_temporal_prediction_variance"])
            and int(row["prediction_unique_rounded_1e8"])
            >= int(gate["minimum_unique_predictions_rounded_1e8"])
            and float(row["median_effective_assets"])
            >= float(gate["minimum_median_effective_assets"])
            and float(row["target_coverage"])
            >= float(gate["minimum_target_coverage"])
            for row in local
        )
    return result


def _render_report(
    decision: Mapping[str, Any], evidence: pd.DataFrame
) -> str:
    pair = evidence[evidence["row_type"].eq("PAIR_DELTA")].copy()
    lines = [
        "# Crypto Relational Policy Stage 1 — Layer Attribution",
        "",
        f"- Decision: `{decision['status']}`",
        f"- Source SHA: `{decision['source_sha']}`",
        f"- PC2 parity: `{decision['parity_status']}`",
        f"- Seeds: `{decision['training']['seeds']}`",
        f"- Fixed optimizer steps per arm/seed: `{decision['training']['steps_per_model']}`",
        f"- Parameter count per arm: `{decision['models']['parameter_count']}`",
        f"- Actual machine wall: `{decision['budget']['actual_wall_seconds']:.2f}s`",
        "",
        "## What was attributed",
        "",
        "A, B, and N used the same 38 asset-local fields, one current market-state field, full-window causal temporal encoder, prediction head, initialization, batches, optimizer, and target. B alone received synchronized peer K/V; N received t-336h peer K/V with the current self query, current market context, and current membership mask.",
        "",
        "This is spent development representation attribution. It is not economic alpha, OOS, fresh evidence, deployment, challenge admission, or promotion evidence.",
        "",
        "## Primary block deltas",
        "",
        "Positive delta means lower MSE for B.",
        "",
        "| Block | Seed | Comparison | Control MSE - B MSE | Win |",
        "|---|---:|---|---:|---|",
    ]
    for row in pair.sort_values(["block_id", "seed", "pair"]).to_dict("records"):
        lines.append(
            f"| {row['block_id']} | {int(row['seed'])} | {row['pair']} | {float(row['primary_delta']):.12g} | {bool(row['win'])} |"
        )
    lines.extend(
        [
            "",
            "## Data and non-degeneracy",
            "",
            f"- Broad fields: 39 loadable; block-variable counts are persisted per block in `decision.json`.",
            f"- All three arms non-degenerate: `{decision['nondegeneracy']['all_arms_nondegenerate']}`",
            f"- B/A outputs materially differ: `{decision['nondegeneracy']['b_a_outputs_differ']}`",
            f"- Shifted donor/current membership mismatch is reported, not hidden or forced to equality.",
            "",
            "## Boundaries and expiry",
            "",
            "No recent, May-stress, forward, challenge, validation/test, candidate promotion, hyperparameter search, extra seed, or Stage 2 execution occurred. Calibration/selection/stability provenance labels did not feed training or model selection.",
            "",
            f"Temporary lifecycle action: `{decision['lifecycle']['closure_action']}`",
            "",
        ]
    )
    return "\n".join(lines)


def run_stage1(config_path: Path, parity_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    config = _read_json(config_path)
    parity = _read_json(parity_path)
    if parity.get("status") != "PASS":
        raise PermissionError("PC2 parity did not pass; STOP_BEFORE_TRAINING")
    if parity.get("source_sha") != _git_sha():
        raise ValueError("parity source SHA does not match the checked-out runner")
    if parity.get("config_sha256") != _payload_sha256(config):
        raise ValueError("parity config identity changed")
    torch.set_num_threads(int(config["training"]["torch_threads"]))
    context = load_stage1_context(ROOT, config)
    data_identity = stage1_data_identity(context, config)
    if (
        parity.get("logical_data_content_identity_sha256")
        != data_identity["logical_content_identity_sha256"]
    ):
        raise ValueError("parity data identity does not match the execution cache")
    adequacy = _data_adequacy(context, config)
    if adequacy["status"] != "DATA_ADEQUACY_PASS":
        raise RuntimeError("DATA_ADEQUACY_UNDERPOWERED: training is forbidden")
    coordinates = context.schedules["MODEL_FIT"]
    batch_size = int(config["training"]["coordinate_batch_size"])
    expected_steps = int(config["training"]["expected_optimizer_steps_per_arm_seed"])
    observed_steps = int(math.ceil(len(coordinates) / batch_size))
    if observed_steps != expected_steps:
        raise ValueError("optimizer step budget changed")
    probe = materialize_stage1_batch(context, config, coordinates[:1])
    models: dict[tuple[str, int], torch.nn.Module] = {}
    optimizers: dict[tuple[str, int], torch.optim.Optimizer] = {}
    model_stats: dict[tuple[str, int], dict[str, Any]] = {}
    initial_hashes: dict[str, str] = {}
    parameter_counts: dict[str, int] = {}
    for seed in config["training"]["seeds"]:
        local = identical_initialized_models(
            arms=tuple(config["training"]["arms"]),
            seed=int(seed),
            **_model_kwargs(config, probe),
        )
        for arm, model in local.items():
            key = (arm, int(seed))
            models[key] = model
            optimizers[key] = torch.optim.AdamW(
                model.parameters(),
                lr=float(config["training"]["learning_rate"]),
                weight_decay=float(config["training"]["weight_decay"]),
            )
            model_stats[key] = {
                "steps": 0,
                "loss_sum": 0.0,
                "first_loss": None,
                "last_loss": None,
                "last_gradient_l2_before_clip": None,
            }
            label = f"{arm}:{int(seed)}"
            initial_hashes[label] = torch_state_sha256(model)
            parameter_counts[label] = sum(
                parameter.numel() for parameter in model.parameters()
            )
    if len(set(parameter_counts.values())) != 1:
        raise ValueError("Stage-1 arm parameter counts are not identical")
    target_scale = float(config["model"]["target_scale"])
    maximum_seconds = float(config["budget"]["maximum_pc2_machine_hours"]) * 3600.0
    for start in range(0, len(coordinates), batch_size):
        batch = materialize_stage1_batch(
            context, config, coordinates[start : start + batch_size]
        )
        scaled_target = batch.target_returns * target_scale
        for key, model in models.items():
            arm, _ = key
            model.train()
            optimizer = optimizers[key]
            optimizer.zero_grad(set_to_none=True)
            prediction = model(arm=arm, **batch.model_inputs())
            loss = torch.square(prediction - scaled_target)[batch.target_valid].mean()
            if not torch.isfinite(loss):
                raise FloatingPointError(f"non-finite training loss: {key}")
            loss.backward()
            gradient = torch.nn.utils.clip_grad_norm_(
                model.parameters(), float(config["training"]["gradient_clip_l2"])
            )
            optimizer.step()
            value = float(loss.detach())
            stats = model_stats[key]
            stats["steps"] += 1
            stats["loss_sum"] += value
            stats["first_loss"] = value if stats["first_loss"] is None else stats["first_loss"]
            stats["last_loss"] = value
            stats["last_gradient_l2_before_clip"] = float(gradient)
        if time.perf_counter() - started > maximum_seconds:
            raise TimeoutError("Stage-1 exceeded its fixed PC2 machine-hour budget")
    for stats in model_stats.values():
        if int(stats["steps"]) != expected_steps:
            raise RuntimeError("a fixed arm/seed run left the training denominator")
        stats["mean_loss"] = float(stats.pop("loss_sum")) / int(stats["steps"])

    evidence_rows: list[dict[str, Any]] = []
    maximum_rank = int(config["evaluation"]["maximum_rank_samples"])
    for block in config["splits"]["attribution_blocks"]:
        block_id = str(block["block_id"])
        local_coordinates = context.schedules[block_id]
        predictions = {
            key: np.empty(
                (len(local_coordinates), len(context.selected_asset_indices)),
                dtype=np.float32,
            )
            for key in models
        }
        target = np.empty_like(next(iter(predictions.values())))
        valid = np.empty(target.shape, dtype=bool)
        cursor = 0
        for local_start in range(0, len(local_coordinates), batch_size):
            batch = materialize_stage1_batch(
                context,
                config,
                local_coordinates[local_start : local_start + batch_size],
            )
            width = int(batch.asset_values.shape[0])
            target[cursor : cursor + width] = batch.target_returns.numpy()
            valid[cursor : cursor + width] = batch.target_valid.numpy()
            with torch.no_grad():
                for key, model in models.items():
                    arm, _ = key
                    model.eval()
                    predictions[key][cursor : cursor + width] = (
                        model(arm=arm, **batch.model_inputs()).cpu().numpy()
                        / target_scale
                    )
            cursor += width
            if time.perf_counter() - started > maximum_seconds:
                raise TimeoutError("Stage-1 exceeded its fixed PC2 machine-hour budget")
        arm_metrics: dict[tuple[str, int], dict[str, Any]] = {}
        for key, prediction in predictions.items():
            arm, seed = key
            metrics = stage1_block_metrics(
                prediction, target, valid, maximum_rank_samples=maximum_rank
            )
            arm_metrics[key] = metrics
            evidence_rows.append(
                {
                    "row_type": "ARM_BLOCK",
                    "arm": arm,
                    "seed": int(seed),
                    "block_id": block_id,
                    "pair": None,
                    "primary_delta": None,
                    "win": None,
                    **metrics,
                }
            )
        for seed in config["training"]["seeds"]:
            seed = int(seed)
            for pair, control in (
                ("B_MINUS_A", TEMPORAL_ONLY_ARM),
                ("B_MINUS_N", SHIFTED_RELATIONAL_NULL_ARM),
            ):
                relation_key = (RELATIONAL_ARM, seed)
                control_key = (control, seed)
                delta = float(
                    arm_metrics[control_key]["mse"] - arm_metrics[relation_key]["mse"]
                )
                diagnostics = stage1_pair_metrics(
                    predictions[relation_key], predictions[control_key], valid
                )
                evidence_rows.append(
                    {
                        "row_type": "PAIR_DELTA",
                        "arm": RELATIONAL_ARM,
                        "control_arm": control,
                        "seed": seed,
                        "block_id": block_id,
                        "pair": pair,
                        "primary_delta": delta,
                        "win": bool(
                            delta
                            > float(config["decision"]["primary_mse_delta_floor"])
                        ),
                        "relational_mse": float(arm_metrics[relation_key]["mse"]),
                        "control_mse": float(arm_metrics[control_key]["mse"]),
                        **diagnostics,
                    }
                )

    per_arm_nondegeneracy = _arm_nondegeneracy(evidence_rows, config)
    all_arms_nondegenerate = all(per_arm_nondegeneracy.values())
    ba_rows = [
        row
        for row in evidence_rows
        if row["row_type"] == "PAIR_DELTA" and row["pair"] == "B_MINUS_A"
    ]
    b_a_outputs_differ = bool(
        ba_rows
        and min(float(row["mean_absolute_difference"]) for row in ba_rows)
        > float(config["nondegeneracy"]["minimum_b_a_mean_absolute_difference"])
    )
    gate = decide_stage1(
        evidence_rows,
        config,
        relational_nondegenerate=all_arms_nondegenerate,
        b_a_outputs_differ=b_a_outputs_differ,
    )
    evidence = pd.DataFrame(evidence_rows)
    output_root = ROOT / str(config["outputs"]["runtime_root"])
    report_path = ROOT / str(config["outputs"]["report"])
    output_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    frozen_config_path = output_root / "frozen_config.json"
    parity_output_path = output_root / "parity.json"
    evidence_path = output_root / "evidence.parquet"
    decision_path = output_root / "decision.json"
    shutil.copyfile(config_path, frozen_config_path)
    shutil.copyfile(parity_path, parity_output_path)
    evidence.to_parquet(evidence_path, index=False)
    actual_wall = time.perf_counter() - started
    final_hashes = {
        f"{arm}:{seed}": torch_state_sha256(model)
        for (arm, seed), model in models.items()
    }
    decision = {
        **gate,
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "source_sha": _git_sha(),
        "config_sha256": _payload_sha256(config),
        "token_contract_identity_sha256": _load_token_identity(config),
        "parity_status": parity["status"],
        "data_identity": data_identity,
        "schedule_identity_sha256": context.schedule_identity_sha256,
        "scaler_identity_sha256": context.scaler.identity_sha256,
        "selected_asset_count": len(context.selected_asset_indices),
        "selected_asset_identity_sha256": _payload_sha256(context.selected_symbols),
        "data_adequacy": adequacy,
        "models": {
            "parameter_count": next(iter(parameter_counts.values())),
            "parameter_counts": parameter_counts,
            "initial_state_sha256": initial_hashes,
            "final_state_sha256": final_hashes,
        },
        "training": {
            "seeds": list(config["training"]["seeds"]),
            "arms": list(config["training"]["arms"]),
            "training_coordinates": len(coordinates),
            "steps_per_model": expected_steps,
            "no_early_stopping": True,
            "no_checkpoint_selection": True,
            "per_model": {
                f"{arm}:{seed}": stats
                for (arm, seed), stats in model_stats.items()
            },
        },
        "nondegeneracy": {
            "all_arms_nondegenerate": all_arms_nondegenerate,
            "per_arm": per_arm_nondegeneracy,
            "b_a_outputs_differ": b_a_outputs_differ,
        },
        "budget": {
            "maximum_pc2_machine_hours": float(
                config["budget"]["maximum_pc2_machine_hours"]
            ),
            "actual_wall_seconds": actual_wall,
            "within_budget": actual_wall <= maximum_seconds,
        },
        "evidence_scope": {
            "architecture_capability": "RUNTIME_EXECUTED",
            "representation_attribution": "SPENT_DEVELOPMENT_ONLY",
            "economic_diagnostics": "NOT_RUN",
            "fresh_evidence": False,
            "oos_evidence": False,
            "promotion_authority": False,
        },
        "lifecycle": {
            "temporary_status": config["lifecycle"]["status"],
            "expires": config["lifecycle"]["expires"],
            "closure_action": (
                config["lifecycle"]["pass_action"]
                if gate["status"] == config["decision"]["pass_status"]
                else config["lifecycle"]["failure_action"]
            ),
        },
        "artifact_sha256": {
            "frozen_config.json": _file_sha256(frozen_config_path),
            "parity.json": _file_sha256(parity_output_path),
            "evidence.parquet": _file_sha256(evidence_path),
        },
        "runtime": _runtime_identity(),
    }
    _write_json(decision_path, decision)
    report_path.write_text(_render_report(decision, evidence), encoding="utf-8")
    return decision


def check_stage1(config_path: Path) -> dict[str, Any]:
    config = _read_json(config_path)
    output_root = ROOT / str(config["outputs"]["runtime_root"])
    report_path = ROOT / str(config["outputs"]["report"])
    required = {
        "frozen_config.json": output_root / "frozen_config.json",
        "parity.json": output_root / "parity.json",
        "evidence.parquet": output_root / "evidence.parquet",
        "decision.json": output_root / "decision.json",
        "report": report_path,
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        return {"result": "FAIL", "missing": missing}
    decision = _read_json(required["decision.json"])
    parity = _read_json(required["parity.json"])
    evidence = pd.read_parquet(required["evidence.parquet"])
    hashes_match = all(
        _file_sha256(required[name]) == expected
        for name, expected in decision["artifact_sha256"].items()
    )
    arm_rows = evidence[evidence["row_type"].eq("ARM_BLOCK")]
    pair_rows = evidence[evidence["row_type"].eq("PAIR_DELTA")]
    expected_arm = 3 * 2 * 6
    expected_pair = 2 * 2 * 6
    recomputed = decide_stage1(
        pair_rows.to_dict("records"),
        config,
        relational_nondegenerate=bool(
            decision["nondegeneracy"]["all_arms_nondegenerate"]
        ),
        b_a_outputs_differ=bool(decision["nondegeneracy"]["b_a_outputs_differ"]),
    )
    checks = {
        "parity_pass": parity.get("status") == "PASS",
        "runtime_source_is_ancestor": _git_is_ancestor(
            str(decision.get("source_sha")), _git_sha()
        ),
        "config_identity_matches": decision.get("config_sha256")
        == _payload_sha256(config),
        "artifact_hashes_match": hashes_match,
        "arm_rows_complete": len(arm_rows) == expected_arm,
        "pair_rows_complete": len(pair_rows) == expected_pair,
        "decision_recomputes": recomputed["status"] == decision["status"],
        "within_budget": bool(decision["budget"]["within_budget"]),
        "stage2_not_authorized": not bool(decision["stage2_execution_authorized"]),
    }
    return {
        "result": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "status": decision["status"],
        "artifact_sha256": {
            name: _file_sha256(path) for name, path in required.items()
        },
    }


def build_cache(
    config_path: Path,
    *,
    data_root: Path,
    cache_root: Path,
    eligibility_path: Path,
    source_sha: str,
) -> dict[str, Any]:
    if cache_root.exists() and any(cache_root.iterdir()):
        raise FileExistsError("refusing to replace a non-empty Stage-1 cache")
    config = _read_json(config_path)
    train_config = _read_json(ROOT / "config" / "crypto_train_surface_18m_v1.json")
    train_config["data_root"] = str(data_root)
    _, quality, _, metadata = build_raw_panel_cache(
        ROOT,
        train_config=train_config,
        cache_root=cache_root,
        eligibility_path=eligibility_path,
        source_sha=source_sha,
        warmup_hours=int(config["data_contract"]["history_hours"]),
    )
    local_config = json.loads(json.dumps(config))
    local_config["inputs"]["broad_cache"] = str(cache_root)
    context = load_stage1_context(ROOT, local_config)
    identity = stage1_data_identity(context, local_config)
    return {
        "result": "PASS",
        "cache_root": str(cache_root),
        "metadata": metadata,
        "logical_data_identity": identity,
        "quality_rows": len(quality),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("build-cache", "parity", "compare-parity", "run", "check")
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--local", type=Path)
    parser.add_argument("--remote", type=Path)
    parser.add_argument("--parity", type=Path)
    parser.add_argument("--data-root", type=Path)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--eligibility-path", type=Path)
    parser.add_argument("--source-sha")
    args = parser.parse_args()
    config_path = args.config.resolve()
    if args.command == "parity":
        result = parity_payload(config_path)
    elif args.command == "compare-parity":
        if args.local is None or args.remote is None:
            parser.error("compare-parity requires --local and --remote")
        result = compare_parity(args.local.resolve(), args.remote.resolve(), config_path)
    elif args.command == "run":
        if args.parity is None:
            parser.error("run requires --parity")
        result = run_stage1(config_path, args.parity.resolve())
    elif args.command == "check":
        result = check_stage1(config_path)
    else:
        if any(
            value is None
            for value in (args.data_root, args.cache_root, args.eligibility_path)
        ):
            parser.error(
                "build-cache requires --data-root --cache-root --eligibility-path"
            )
        result = build_cache(
            config_path,
            data_root=args.data_root.resolve(),
            cache_root=args.cache_root.resolve(),
            eligibility_path=args.eligibility_path.resolve(),
            source_sha=(args.source_sha or _git_sha()),
        )
    if args.output is not None:
        _write_json(args.output.resolve(), result)
        print(
            json.dumps(
                {
                    "output": str(args.output.resolve()),
                    "result": result.get("result"),
                    "status": result.get("status"),
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    if args.command == "parity":
        return 0
    if args.command == "compare-parity":
        return 0 if result.get("status") == "PASS" else 1
    if args.command == "run":
        # A negative attribution decision is still a successfully completed
        # fixed experiment; exceptions and parity failure already fail closed.
        return 0
    return 0 if result.get("result") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
