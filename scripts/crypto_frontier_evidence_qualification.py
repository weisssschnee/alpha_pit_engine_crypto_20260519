from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_IMPORT_ROOT = Path(__file__).resolve().parents[1]
if str(_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_IMPORT_ROOT))

from alphafactory_crypto.frontier_v2.qualification import (
    base_bundle_attestation,
    build_artifact_index,
    evaluate_data_adequacy,
    plan_new_release_activation,
    run_corrected_arena,
    run_deepdow_qualification,
    run_qlib_qualification,
    write_json,
)
from alphafactory_crypto.frontier_v2.release import canonical_sha256, sha256_file


REPO = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO / "config" / "crypto_frontier_evidence_qualification_v1.json"


def _load() -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
    qualification = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    base_config_path = REPO / qualification["base_config"]
    base_config = json.loads(base_config_path.read_text(encoding="utf-8"))
    base_root = REPO / qualification["base_run_root"]
    output_root = REPO / qualification["output_root"]
    return qualification, base_config, base_root, output_root


def _repo_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def _ensure_boundaries(qualification: dict[str, Any], daily: pd.DataFrame) -> None:
    if qualification["allowed_role"] != "DEVELOPMENT":
        raise PermissionError("evidence qualification is development-only")
    if set(daily.data_role.unique()) != {"DEVELOPMENT"}:
        raise PermissionError("non-development data reached evidence qualification")
    lowered = " ".join(str(path).lower() for path in (CONFIG_PATH,))
    if any(token in lowered for token in qualification["prohibited_roles"]):
        raise PermissionError("prohibited role path reached")


def _gate_actuals(
    daily: pd.DataFrame,
    qlib_result: dict[str, Any],
    deepdow_result: dict[str, Any],
) -> dict[str, dict[str, float]]:
    qlib_feature_stats = qlib_result["feature_stats"]
    qlib_full_only = qlib_feature_stats[qlib_feature_stats.full_only]
    qlib_diag = qlib_result["qualification"]["repaired_model_diagnostics"]["FULL_ALPHA158"]
    label_rows = qlib_result["qualification"]["original_input"]["label_stats"]
    label_support = next(
        float(row["support"])
        for row in label_rows
        if row["variant"] == "FULL_ALPHA158" and row["stage"] == "learn" and row["split"] == "train"
    )
    common_dates = qlib_result["full_weights"].index.intersection(
        deepdow_result["challenger_weights"].index
    )
    deep_tensor = deepdow_result["tensor_stats"]
    deep_independent = deep_tensor["intervals"]["splits"]["development_holdout"][
        "max_nonoverlapping_target_windows"
    ]
    return {
        "QLIB_CROSS_SECTIONAL_DAILY": {
            "development_dates": float(len(common_dates)),
            "training_samples": float(qlib_diag["train_rows"]),
            "cross_sectional_assets": float(daily.symbol.nunique()),
            "feature_non_null_rate": float(qlib_full_only.learn_non_null_rate.min()),
            "positive_variance_feature_fraction": float((qlib_full_only.learn_variance > 0).mean()),
            "history_days": float(daily.date.nunique()),
            "label_support": label_support,
            "turnover_observations": float(len(common_dates)),
            "independent_evaluation_blocks": float(math.floor(len(common_dates) / 5)),
        },
        "DEEPDOW_DIRECT_5D": {
            "development_dates": float(len(common_dates)),
            "training_samples": float(
                deep_tensor["intervals"]["splits"]["train"]["windows"]
            ),
            "cross_sectional_assets": float(daily.symbol.nunique()),
            "feature_non_null_rate": float(deep_tensor["input_non_null_rate"]),
            "positive_variance_feature_fraction": float(
                np.mean(np.asarray(deep_tensor["input_channel_variance"]) > 0)
            ),
            "history_days": float(daily.date.nunique()),
            "label_support": float(deep_tensor["target_non_null_rate"]),
            "turnover_observations": float(len(common_dates)),
            "independent_evaluation_blocks": float(deep_independent),
        },
        "INTERNAL_LONG_ONLY_DAILY": {
            "development_dates": float(len(common_dates)),
            "training_samples": 0.0,
            "cross_sectional_assets": float(daily.symbol.nunique()),
            "feature_non_null_rate": 1.0,
            "positive_variance_feature_fraction": 1.0,
            "history_days": float(daily.date.nunique()),
            "label_support": float(daily.label_1d_delayed.notna().mean()),
            "turnover_observations": float(len(common_dates)),
            "independent_evaluation_blocks": float(math.floor(len(common_dates) / 20)),
        },
    }


def _classification(
    qlib_result: dict[str, Any],
    deepdow_result: dict[str, Any],
    gate_summary: dict[str, Any],
) -> dict[str, Any]:
    qlib_original = qlib_result["qualification"]["original_classification"]
    qlib_repaired_pre = qlib_result["qualification"]["repaired_status_before_data_adequacy"]
    if qlib_repaired_pre != "EFFECTIVE_DIFFERENCE_PRESENT":
        qlib_final = qlib_repaired_pre
    elif gate_summary["QLIB_CROSS_SECTIONAL_DAILY"]["status"] != "PASS":
        qlib_final = "DATA_ADEQUACY_UNDERPOWERED"
    else:
        qlib_final = "INFORMATIVE_NEGATIVE"

    deep_pre = deepdow_result["qualification"]["status_before_data_adequacy"]
    if deep_pre != "EFFECTIVE_DIFFERENCE_PRESENT":
        deep_final = deep_pre
    elif gate_summary["DEEPDOW_DIRECT_5D"]["status"] != "PASS":
        deep_final = "DATA_ADEQUACY_UNDERPOWERED"
    else:
        deep_final = "INFORMATIVE_NEGATIVE"
    return {
        "qlib_original": qlib_original,
        "qlib_repair_status": "EXTERNAL_PARADIGM_COMPARISON_DEGENERATE_FIXED"
        if qlib_original in {"MODEL_FIT_DEGENERATE", "COMPETITOR_COMPARISON_DEGENERATE", "PORTFOLIO_MAPPING_COLLAPSE"}
        and qlib_repaired_pre == "EFFECTIVE_DIFFERENCE_PRESENT"
        else "REPAIR_NOT_QUALIFIED",
        "qlib_current_economic_status": qlib_final,
        "deepdow_current_economic_status": deep_final,
        "main_conclusion": "CURRENT_DATA_UNDERPOWERED"
        if "DATA_ADEQUACY_UNDERPOWERED" in {qlib_final, deep_final}
        else "EXTERNAL_PARADIGM_INFORMATIVE_NEGATIVE",
    }


def run() -> dict[str, Any]:
    qualification, base_config, base_root, output_root = _load()
    output_root.mkdir(parents=True, exist_ok=True)
    daily = pd.read_parquet(base_root / "development_daily_panel.parquet")
    daily["date"] = pd.to_datetime(daily.date, utc=True)
    _ensure_boundaries(qualification, daily)

    base_attestation = base_bundle_attestation(REPO, base_root)
    write_json(output_root / "base_122_artifact_bundle_attestation.json", base_attestation)
    qlib_result = run_qlib_qualification(
        daily, base_config, qualification, base_root, output_root
    )
    deepdow_result = run_deepdow_qualification(daily, base_config, output_root)
    actuals = _gate_actuals(daily, qlib_result, deepdow_result)
    gate_rows, gate_summary = evaluate_data_adequacy(
        qualification["data_adequacy_gate"], actuals
    )
    gate_rows.to_csv(output_root / "data_adequacy_gate.csv", index=False, lineterminator="\n")
    write_json(output_root / "data_adequacy_gate.json", gate_summary)
    arena = run_corrected_arena(daily, qlib_result, deepdow_result, base_config, output_root)
    classifications = _classification(qlib_result, deepdow_result, gate_summary)

    deep_path = arena["paths"]
    deep_cost_rows = []
    for system_id in (
        "DEEPDOW_V023_KEYNESNET_FLOW",
        "DEEPDOW_V023_ASSET_ROTATED_FLOW_CONTROL",
    ):
        frame = deep_path[deep_path.system_id.eq(system_id)]
        deep_cost_rows.append(
            {
                "system_id": system_id,
                "observations": int(len(frame)),
                "gross_mean": float(frame.gross_return.mean()),
                "cost_mean": float(frame.cost.mean()),
                "net_mean": float(frame.net_return.mean()),
                "gross_minus_net": float((frame.gross_return - frame.net_return).mean()),
            }
        )
    write_json(output_root / "deepdow" / "bridge_cost_evidence.json", deep_cost_rows)

    paired_records = arena["paired"].to_dict(orient="records")
    corrected_status = {
        "status": classifications["main_conclusion"],
        "qlib": {
            "historical_0_0": qlib_result["qualification"]["original_classification"],
            "repair": classifications["qlib_repair_status"],
            "current_economic_status": classifications["qlib_current_economic_status"],
        },
        "deepdow": {
            "current_economic_status": classifications["deepdow_current_economic_status"],
            "exact_comparison_degenerate": False,
        },
        "paired_comparisons": paired_records,
        "data_adequacy": {
            paradigm: value["status"] for paradigm, value in gate_summary.items()
        },
        "candidate_promotion": False,
        "forward_read": False,
        "challenge_read": False,
        "recent_read": False,
        "may_stress_read": False,
        "cross_sprint_adaptive_memory": False,
    }
    write_json(output_root / "corrected_arena_evidence_status.json", corrected_status)

    activation_contract = {
        "entry_command": "python scripts/crypto_frontier_evidence_qualification.py activation-plan --manifest <release-manifest>",
        "sequence": [
            "existing ingress-preflight",
            "paradigm compatibility and Data Adequacy Gate",
            "select the two highest information-match external paradigms",
            "add current internal baseline",
            "freeze fixed development-only budget",
            "run Arena only when both selected paradigms pass adequacy",
        ],
        "required_manifest_extension": "adequacy_profiles keyed by registered paradigm id",
        "boundaries": qualification["new_release_activation"],
    }
    write_json(output_root / "new_data_direct_activation_contract.json", activation_contract)

    closure_manifest = {
        "closure_id": "CRYPTO_FRONTIER_PROVENANCE_CLOSURE_20260714",
        "status": "REPOSITORY_PROVENANCE_CLOSURE_PENDING",
        "architecture_status": "ARCHITECTURE_EXECUTION_COMPLETED",
        "evidence_subject_repo_sha": _repo_sha(),
        "qualification_config": CONFIG_PATH.relative_to(REPO).as_posix(),
        "qualification_config_sha256": sha256_file(CONFIG_PATH),
        "base_bundle": base_attestation,
        "main_conclusion": classifications["main_conclusion"],
        "qlib_qualification": classifications["qlib_current_economic_status"],
        "deepdow_qualification": classifications["deepdow_current_economic_status"],
        "qlib_degenerate_comparison_fixed": classifications["qlib_repair_status"],
        "data_adequacy_gate_sha256": sha256_file(output_root / "data_adequacy_gate.json"),
        "corrected_arena_status_sha256": sha256_file(
            output_root / "corrected_arena_evidence_status.json"
        ),
        "intended_tag": "crypto-frontier-provenance-closure-20260714",
        "promotion": False,
        "forward_read": False,
        "new_performance_search": False,
        "cross_sprint_adaptive_memory": False,
    }
    write_json(output_root / "closure_manifest.json", closure_manifest)
    seal = build_artifact_index(REPO, output_root)
    write_json(output_root / "seal_result.json", seal)
    summary = {
        "qualification_id": qualification["qualification_id"],
        "status": classifications["main_conclusion"],
        "repository_status": "REPOSITORY_PROVENANCE_CLOSURE_PENDING",
        "qlib": classifications,
        "deepdow": classifications["deepdow_current_economic_status"],
        "base_artifacts_verified": base_attestation["content_verification"]["verified_count"],
        "base_bundle_sha256": base_attestation["bundle_sha256"],
        "arena_systems": arena["systems"],
        "fixed_model_fits": 6,
        "parameter_search_performed": False,
        "candidate_promotion": False,
        "forward_read": False,
        "challenge_read": False,
        "recent_read": False,
        "may_stress_read": False,
    }
    write_json(output_root / "qualification_summary.json", summary)
    seal = build_artifact_index(REPO, output_root)
    write_json(output_root / "seal_result.json", seal)
    return {**summary, **seal}


def seal() -> dict[str, Any]:
    _, _, _, output_root = _load()
    result = build_artifact_index(REPO, output_root)
    write_json(output_root / "seal_result.json", result)
    return result


def finalize_existing() -> dict[str, Any]:
    qualification, _, base_root, output_root = _load()
    qlib_path = output_root / "qlib" / "qualification.json"
    deepdow_path = output_root / "deepdow" / "qualification.json"
    qlib = json.loads(qlib_path.read_text(encoding="utf-8"))
    deepdow = json.loads(deepdow_path.read_text(encoding="utf-8"))
    importance = pd.read_csv(output_root / "qlib" / "repaired_feature_importance.csv")
    for variant, diagnostics in qlib["repaired_model_diagnostics"].items():
        variant_importance = importance[importance.variant.eq(variant)]
        diagnostics["total_split_nodes"] = int(variant_importance.split_importance.sum())
    repaired_degenerate = any(
        not diagnostics["loss_changed"]
        or diagnostics["nonzero_split_importance_features"] == 0
        or diagnostics["total_split_nodes"] == 0
        for diagnostics in qlib["repaired_model_diagnostics"].values()
    ) or any(
        qlib["repaired_predictions"][f"{name}_value_variance"] <= 1e-15
        for name in ("full", "control")
    )
    qlib["repaired_status_before_data_adequacy"] = (
        "MODEL_FIT_DEGENERATE"
        if repaired_degenerate
        else "PORTFOLIO_MAPPING_COLLAPSE"
        if qlib["repaired_weights"]["exact_equality"]
        else "EFFECTIVE_DIFFERENCE_PRESENT"
    )
    write_json(qlib_path, qlib)
    gate_summary = json.loads((output_root / "data_adequacy_gate.json").read_text(encoding="utf-8"))
    classifications = _classification(
        {"qualification": qlib}, {"qualification": deepdow}, gate_summary
    )
    corrected_path = output_root / "corrected_arena_evidence_status.json"
    corrected = json.loads(corrected_path.read_text(encoding="utf-8"))
    corrected["status"] = classifications["main_conclusion"]
    corrected["qlib"] = {
        "historical_0_0": qlib["original_classification"],
        "repair": classifications["qlib_repair_status"],
        "current_economic_status": classifications["qlib_current_economic_status"],
    }
    corrected["deepdow"]["current_economic_status"] = classifications[
        "deepdow_current_economic_status"
    ]
    write_json(corrected_path, corrected)
    base_index = pd.read_csv(base_root / "artifact_index.csv")
    cache_tokens = (
        "/qlib_provider/",
        "/qlib_source_csv/",
        "qlib_handler_",
        "qlib_provider_cache_manifest.json",
        "development_daily_panel.parquet",
    )
    storage_rows = []
    for row in base_index.to_dict(orient="records"):
        artifact = str(row["artifact"])
        regenerable = any(token in artifact for token in cache_tokens)
        storage_rows.append(
            {
                **row,
                "storage_class": "REGENERABLE_CACHE_HASH_ONLY"
                if regenerable
                else "COMMITTED_EVIDENCE",
                "git_policy": "IGNORE_CONTENT_KEEP_HASH" if regenerable else "COMMIT",
            }
        )
    storage_path = output_root / "base_122_artifact_storage_manifest.csv"
    pd.DataFrame(storage_rows).to_csv(storage_path, index=False, lineterminator="\n")
    closure_path = output_root / "closure_manifest.json"
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    closure["main_conclusion"] = classifications["main_conclusion"]
    closure["qlib_qualification"] = classifications["qlib_current_economic_status"]
    closure["deepdow_qualification"] = classifications["deepdow_current_economic_status"]
    closure["qlib_degenerate_comparison_fixed"] = classifications["qlib_repair_status"]
    closure["corrected_arena_status_sha256"] = sha256_file(corrected_path)
    closure["base_artifact_storage_manifest"] = storage_path.relative_to(REPO).as_posix()
    closure["base_artifact_storage_manifest_sha256"] = sha256_file(storage_path)
    write_json(closure_path, closure)
    summary_path = output_root / "qualification_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["status"] = classifications["main_conclusion"]
    summary["qlib"] = classifications
    summary["deepdow"] = classifications["deepdow_current_economic_status"]
    write_json(summary_path, summary)
    sealed = build_artifact_index(REPO, output_root)
    write_json(output_root / "seal_result.json", sealed)
    return {"status": "FINALIZED_WITHOUT_NEW_FITS", "classifications": classifications, **sealed}


def check() -> dict[str, Any]:
    qualification, _, base_root, output_root = _load()
    index = pd.read_csv(output_root / "artifact_index.csv")
    missing = []
    drift = []
    for row in index.itertuples():
        path = REPO / row.artifact
        if not path.is_file():
            missing.append(row.artifact)
        elif sha256_file(path) != str(row.sha256).upper() or path.stat().st_size != int(row.size_bytes):
            drift.append(row.artifact)
    base = base_bundle_attestation(REPO, base_root)
    corrected = json.loads((output_root / "corrected_arena_evidence_status.json").read_text(encoding="utf-8"))
    summary = json.loads((output_root / "qualification_summary.json").read_text(encoding="utf-8"))
    qlib = json.loads((output_root / "qlib" / "qualification.json").read_text(encoding="utf-8"))
    deepdow = json.loads((output_root / "deepdow" / "qualification.json").read_text(encoding="utf-8"))
    if missing or drift:
        raise RuntimeError(f"qualification artifact drift: missing={missing} drift={drift}")
    if base["artifact_count"] != 122 or base["bundle_sha256"] != "99C0DACAF12F17DA6B7705DDBFCE9BAD996143082301F47BCA7E690071140EF2":
        raise RuntimeError("base 122-artifact bundle identity drift")
    if corrected["status"] != "CURRENT_DATA_UNDERPOWERED":
        raise RuntimeError("corrected economic conclusion drift")
    if qlib["original_classification"] != "MODEL_FIT_DEGENERATE":
        raise RuntimeError("Qlib historical 0/0 qualification drift")
    if qlib["repaired_status_before_data_adequacy"] != "EFFECTIVE_DIFFERENCE_PRESENT":
        raise RuntimeError("Qlib one-shot repair did not resolve degeneracy")
    if deepdow["status_before_data_adequacy"] != "EFFECTIVE_DIFFERENCE_PRESENT":
        raise RuntimeError("DeepDow comparison became degenerate")
    if summary["fixed_model_fits"] != 6 or summary["parameter_search_performed"]:
        raise RuntimeError("frozen fit budget drift")
    prohibited_true = [
        key
        for key in (
            "candidate_promotion",
            "forward_read",
            "challenge_read",
            "recent_read",
            "may_stress_read",
        )
        if summary.get(key)
    ]
    if prohibited_true:
        raise PermissionError(f"frozen boundary violated: {prohibited_true}")
    return {
        "status": "CRYPTO_FRONTIER_EVIDENCE_QUALIFICATION_CHECK_PASSED",
        "qualification_artifacts_verified": int(len(index)),
        "base_artifacts_verified": base["content_verification"]["verified_count"],
        "base_bundle_sha256": base["bundle_sha256"],
        "main_conclusion": corrected["status"],
        "frozen_boundaries_intact": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run")
    subparsers.add_parser("seal")
    subparsers.add_parser("check")
    subparsers.add_parser("finalize")
    activation = subparsers.add_parser("activation-plan")
    activation.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "run":
        result = run()
    elif args.command == "seal":
        result = seal()
    elif args.command == "check":
        result = check()
    elif args.command == "finalize":
        result = finalize_existing()
    else:
        qualification, base_config, _, _ = _load()
        result = plan_new_release_activation(args.manifest, base_config, qualification)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
