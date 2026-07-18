from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.broad_information_arena import (  # noqa: E402
    CONTROL_SURFACE,
    FULL_SURFACE,
    MLP_MODEL,
    RIDGE_MODEL,
    FixedMLP,
    arena_decision,
    data_adequacy,
    deterministic_coordinates,
    economic_metrics,
    fit_normalization,
    information_evidence,
    load_broad_arena_data,
    model_matrix,
    paired_increment,
    payload_sha256,
    predict_split,
    prediction_metrics,
)
from alphafactory_crypto.core_pack_consumption import sha256_file  # noqa: E402
from alphafactory_crypto.instrument_capability.mapping import (  # noqa: E402
    CROSS_SECTIONAL_ZERO_NET,
    DEFAULT_MAPPING_CONTRACTS,
    mapping_contract_sha256,
)


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")


def _write_jsonl(path: Path, values: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True, default=str) + "\n" for row in values), encoding="utf-8", newline="\n")


def _report(manifest: dict[str, Any], decision: dict[str, Any], adequacy: dict[str, Any], information: pd.DataFrame) -> str:
    added = information.loc[information["surface_role"] == "ADDED"]
    control = information.loc[information["surface_role"] == "CONTROL"]
    return "\n".join(
        [
            "# Broad Core Pack information and fixed 2x2 development Arena",
            "",
            "This is a frozen development-only comparison. It is not performance search, OOS evidence, or promotion authority.",
            "",
            f"- Source SHA: `{manifest['source_sha']}`",
            f"- Status: `{decision['status']}`",
            f"- Data adequacy: `{adequacy['status']}`",
            f"- Added fields with stable residual information: {int(added['stable_residual_information'].sum())}/{len(added)}",
            f"- Control fields with stable residual information: {int(control['stable_residual_information'].sum())}/{len(control)}",
            f"- Information gate: {decision['information_gate_pass']}",
            f"- Economic increment gate: {decision['economic_increment_gate_pass']}",
            "",
            "## Why entropy is not used alone",
            "",
            "Quantile-binned H(X) is an adequacy check and approaches its maximum for nearly every non-degenerate field. The decision therefore uses block-matched mutual-information excess, residual information over the current 10-field Ridge, redundancy evidence, and fixed-model matched increments.",
            "",
            "## Split increment summary",
            "",
            pd.DataFrame(decision["split_increment_summary"]).to_markdown(index=False),
            "",
            "## Boundaries",
            "",
            "No validation/test/recent/May-stress/forward/challenge role was read. No hyperparameter search or candidate promotion occurred.",
            "",
        ]
    )


def run(config_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_root = ROOT / config["outputs"]["runtime_root"]
    report_path = ROOT / config["outputs"]["report"]
    output_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    data = load_broad_arena_data(ROOT, config)
    adequacy = data_adequacy(data, config)
    _write_json(output_root / "data_adequacy.json", adequacy)
    if adequacy["status"] != "DATA_ADEQUACY_PASS":
        raise RuntimeError("Broad information Arena failed its pre-registered Data Adequacy Gate")

    train = data.slices["train"]
    train_mask = data.eligibility[:, train] & np.isfinite(data.target[:, train])
    train_assets, train_times = deterministic_coordinates(train_mask, int(config["models"]["train_samples"]))
    train_absolute = train_times + train.start
    median, scale = fit_normalization(data, train_assets, train_absolute)
    full_indices = np.arange(len(data.fields))
    control_indices = np.asarray([data.fields.index(field) for field in data.control_fields])
    train_target = data.target[train_assets, train_absolute].astype(np.float32)
    target_mean = float(np.mean(train_target))
    target_scale = float(max(np.std(train_target), 1e-8))
    train_scaled = (train_target - target_mean) / target_scale
    raw_full = data.values[train_assets[:, None], full_indices[None, :], train_absolute[:, None]]

    models: list[tuple[str, str, int, Any, dict[str, Any], np.ndarray]] = []
    for surface, indices in ((CONTROL_SURFACE, control_indices), (FULL_SURFACE, full_indices)):
        x = model_matrix(raw_full[:, indices], median[indices], scale[indices])
        ridge = Ridge(alpha=float(config["models"]["ridge_alpha"]))
        fit_started = time.perf_counter()
        ridge.fit(x, train_scaled)
        models.append((RIDGE_MODEL, surface, 0, ridge, {"fit_seconds": time.perf_counter() - fit_started, "training_score": float(ridge.score(x, train_scaled))}, indices))
        for seed in config["models"]["mlp_seeds"]:
            model = FixedMLP(x.shape[1], config["models"]["mlp_hidden"], int(seed))
            diagnostic = model.fit(
                x,
                train_scaled,
                seed=int(seed),
                epochs=int(config["models"]["mlp_epochs"]),
                batch_size=int(config["models"]["mlp_batch_size"]),
                learning_rate=float(config["models"]["mlp_learning_rate"]),
                weight_decay=float(config["models"]["mlp_weight_decay"]),
                torch_threads=int(config["models"]["torch_threads"]),
            )
            models.append((MLP_MODEL, surface, int(seed), model, diagnostic, indices))

    baseline_ridge = next(model for family, surface, _, model, _, _ in models if family == RIDGE_MODEL and surface == CONTROL_SURFACE)
    prior_census = pd.read_parquet(ROOT / config["inputs"]["prior_information_census"])
    information = information_evidence(
        data,
        baseline_ridge=baseline_ridge,
        median=median,
        scale=scale,
        target_mean=target_mean,
        target_scale=target_scale,
        config=config,
        prior_census=prior_census,
    )
    information_path = output_root / "information_evidence.csv"
    information.to_csv(information_path, index=False, lineterminator="\n")

    model_rows: list[dict[str, Any]] = []
    weights: dict[tuple[str, int, str, str], np.ndarray] = {}
    for family, surface, seed, model, diagnostic, indices in models:
        for split in ("selection", "stability"):
            block = data.slices[split]
            prediction = predict_split(
                model,
                model_family=family,
                data=data,
                block=block,
                field_indices=indices,
                median=median,
                scale=scale,
                target_mean=target_mean,
                target_scale=target_scale,
            )
            predictive = prediction_metrics(prediction, data.target[:, block], int(config["models"]["rank_metric_samples"]))
            economic, local_weights = economic_metrics(prediction, data, block)
            weights[(family, seed, split, surface)] = local_weights
            model_rows.append({
                "model_family": family,
                "surface": surface,
                "seed": seed,
                "split": split,
                "field_count": int(len(indices)),
                "fit": diagnostic,
                "predictive": predictive,
                "economic": economic,
            })
    increment_rows: list[dict[str, Any]] = []
    for family, seed in ((RIDGE_MODEL, 0), *[(MLP_MODEL, int(seed)) for seed in config["models"]["mlp_seeds"]]):
        for split in ("selection", "stability"):
            increment_rows.append({
                "model_family": family,
                "seed": seed,
                "split": split,
                "full_surface": FULL_SURFACE,
                "control_surface": CONTROL_SURFACE,
                "metrics": paired_increment(
                    weights[(family, seed, split, FULL_SURFACE)],
                    weights[(family, seed, split, CONTROL_SURFACE)],
                    data,
                    data.slices[split],
                ),
            })
    decision = arena_decision(information, increment_rows, config)
    _write_jsonl(output_root / "model_evidence.jsonl", model_rows)
    _write_jsonl(output_root / "paired_increment_evidence.jsonl", increment_rows)
    _write_json(output_root / "decision.json", decision)

    input_paths = {
        name: ROOT / value for name, value in config["inputs"].items() if name != "broad_cache"
    }
    cache_metadata = ROOT / config["inputs"]["broad_cache"] / "metadata.json"
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": config["experiment_id"],
        "objective": config["objective"],
        "status": decision["status"],
        "source_sha": _git_sha(),
        "created_at": _now(),
        "command": "python scripts/crypto_broad_core_pack_information_arena_v1.py",
        "parameters": {key: config[key] for key in ("splits", "information", "models", "data_adequacy", "frozen_budget", "economic_contract")},
        "input_identities": {
            **{f"{name}_sha256": sha256_file(path) for name, path in input_paths.items()},
            "broad_cache_metadata_sha256": sha256_file(cache_metadata),
            "broad_cache_identity_sha256": json.loads(cache_metadata.read_text())["identity_sha256"],
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "sklearn": sklearn.__version__,
        },
        "data_adequacy": adequacy,
        "decision": decision,
        "economic_mapping_sha256": mapping_contract_sha256(DEFAULT_MAPPING_CONTRACTS[CROSS_SECTIONAL_ZERO_NET]),
        "cost_time": {
            "estimated_wall_minutes": config["frozen_budget"]["estimated_wall_minutes"],
            "estimated_peak_memory_gb": config["frozen_budget"]["estimated_peak_memory_gb"],
            "actual_wall_seconds": float(time.perf_counter() - started),
        },
        "boundaries": config["boundaries"],
        "reproducibility": {
            "reproducible": True,
            "continuation": "Rerun the exact command at source_sha with the same content-hash-bound inputs; do not tune models or open sealed roles.",
            "failure": None,
        },
        "files": {},
    }
    manifest["identity_sha256"] = payload_sha256({key: value for key, value in manifest.items() if key != "files"})
    report_path.write_text(_report(manifest, decision, adequacy, information), encoding="utf-8", newline="\n")
    for path in (
        output_root / "data_adequacy.json",
        information_path,
        output_root / "model_evidence.jsonl",
        output_root / "paired_increment_evidence.jsonl",
        output_root / "decision.json",
        report_path,
    ):
        manifest["files"][path.relative_to(ROOT).as_posix()] = sha256_file(path)
    _write_json(output_root / "run_manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "config/crypto_broad_core_pack_information_arena_v1.json")
    args = parser.parse_args()
    print(json.dumps(run(args.config), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
