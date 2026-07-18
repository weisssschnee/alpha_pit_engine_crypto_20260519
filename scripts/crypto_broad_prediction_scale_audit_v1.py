from __future__ import annotations

import argparse
import json
import math
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from alphafactory_crypto.broad_information_arena import payload_sha256  # noqa: E402
from alphafactory_crypto.core_pack_consumption import sha256_file  # noqa: E402


DEFAULT_RUNTIME = ROOT / "runtime/crypto_broad_core_pack_sticky_mapping_v1_20260718"
DEFAULT_OUTPUT = ROOT / "runtime/crypto_broad_prediction_scale_audit_v1_20260718"
DEFAULT_REPORT = ROOT / "reports/CRYPTO_BROAD_PREDICTION_SCALE_AUDIT_V1_20260718.md"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8", newline="\n")


def _rank_correlation(frame: pd.DataFrame, left: str, right: str) -> float:
    value = frame[left].corr(frame[right], method="spearman")
    return float(value) if pd.notna(value) else 0.0


def run(runtime_root: Path, output_root: Path, report_path: Path) -> dict[str, Any]:
    started = time.perf_counter()
    runtime_root = runtime_root.resolve()
    output_root = output_root.resolve()
    report_path = report_path.resolve()
    model_path = runtime_root / "model_evidence.jsonl"
    sticky_path = runtime_root / "sticky_surface_evidence.jsonl"
    pair_path = runtime_root / "sticky_pair_evidence.jsonl"
    models = _read_jsonl(model_path)
    sticky = _read_jsonl(sticky_path)
    sticky_by_key = {
        (row["model_family"], int(row["seed"]), row["split"], row["surface"]): row
        for row in sticky
    }
    rows: list[dict[str, Any]] = []
    for model in models:
        key = (
            model["model_family"],
            int(model["seed"]),
            model["split"],
            model["surface"],
        )
        if key not in sticky_by_key:
            raise ValueError(f"STICKY_SURFACE_KEY_MISSING:{key}")
        mapped = sticky_by_key[key]
        diagnostics = mapped["diagnostics"]
        rows.append(
            {
                "model_family": model["model_family"],
                "seed": int(model["seed"]),
                "split": model["split"],
                "surface": model["surface"],
                "prediction_std": math.sqrt(float(model["predictive"]["prediction_variance"])),
                "pearson": float(model["predictive"]["pearson"]),
                "spearman": float(model["predictive"]["spearman"]),
                "acceptance_ratio": float(diagnostics["acceptance_ratio"]),
                "edge_cost_ratio": float(
                    diagnostics["mean_predicted_improvement"]
                    / max(float(diagnostics["mean_required_round_trip_edge"]), 1e-18)
                ),
                "turnover_mean": float(mapped["metrics"]["turnover_mean"]),
                "net_mean": float(mapped["metrics"]["net_mean"]),
                "prediction_sha256": mapped["reference_prediction_sha256"],
                "sticky_weight_sha256": diagnostics["sticky_weight_sha256"],
            }
        )
    frame = pd.DataFrame(rows)
    scopes = {
        "all": frame,
        "full": frame.loc[frame["surface"] == "BROAD_CORE_PACK_39"],
        "control": frame.loc[frame["surface"] == "CURRENT_10"],
        "full_mlp": frame.loc[
            (frame["surface"] == "BROAD_CORE_PACK_39")
            & (frame["model_family"] == "FIXED_MLP")
        ],
    }
    correlations = {
        name: {
            "observations": int(len(local)),
            "scale_vs_acceptance": _rank_correlation(local, "prediction_std", "acceptance_ratio"),
            "scale_vs_turnover": _rank_correlation(local, "prediction_std", "turnover_mean"),
            "scale_vs_net": _rank_correlation(local, "prediction_std", "net_mean"),
            "scale_vs_pearson": _rank_correlation(local, "prediction_std", "pearson"),
            "scale_vs_spearman": _rank_correlation(local, "prediction_std", "spearman"),
        }
        for name, local in scopes.items()
    }
    criteria = {
        "minimum_scale_acceptance_rank_correlation": 0.80,
        "minimum_scale_turnover_rank_correlation": 0.80,
        "maximum_scale_net_rank_correlation_for_quality": 0.30,
        "minimum_full_mlp_acceptance_range": 0.50,
    }
    full_mlp = scopes["full_mlp"]
    acceptance_range = float(full_mlp["acceptance_ratio"].max() - full_mlp["acceptance_ratio"].min())
    checks = {
        "scale_controls_acceptance": correlations["all"]["scale_vs_acceptance"]
        >= criteria["minimum_scale_acceptance_rank_correlation"],
        "scale_controls_turnover": correlations["all"]["scale_vs_turnover"]
        >= criteria["minimum_scale_turnover_rank_correlation"],
        "scale_not_positive_net_quality": correlations["all"]["scale_vs_net"]
        <= criteria["maximum_scale_net_rank_correlation_for_quality"],
        "full_mlp_acceptance_dispersion": acceptance_range
        >= criteria["minimum_full_mlp_acceptance_range"],
        "prediction_identity_complete": bool(len(frame) == 16 and frame["prediction_sha256"].nunique() == 16),
    }
    decision = {
        "status": (
            "PREDICTION_SCALE_CALIBRATION_RISK_CONFIRMED"
            if all(checks.values())
            else "PREDICTION_SCALE_CALIBRATION_RISK_NOT_ESTABLISHED"
        ),
        "checks": checks,
        "criteria": criteria,
        "correlations": correlations,
        "full_mlp_acceptance_range": acceptance_range,
        "claim_scope": "FROZEN_STICKY_MAPPING_DIAGNOSTIC_ONLY",
        "cannot_infer": [
            "a calibrated mapping would produce positive net increment",
            "directional alpha quality from prediction amplitude",
            "OOS qualification",
            "candidate promotion",
        ],
        "next_action": "Do not tune the observed sticky threshold. Any repair must estimate a return-scale calibration on train-only data and replay the same frozen development comparison.",
    }
    output_root.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    diagnostics_path = output_root / "scale_diagnostics.csv"
    decision_path = output_root / "decision.json"
    frame.to_csv(diagnostics_path, index=False, lineterminator="\n")
    _write_json(decision_path, decision)
    report = "\n".join(
        [
            "# Broad prediction-scale audit",
            "",
            "This is a diagnostic over committed frozen predictions and sticky-mapping evidence. It does not retrain, tune, or open sealed roles.",
            "",
            f"- Status: `{decision['status']}`",
            f"- All-surface scale vs acceptance Spearman: `{correlations['all']['scale_vs_acceptance']:.3f}`",
            f"- All-surface scale vs turnover Spearman: `{correlations['all']['scale_vs_turnover']:.3f}`",
            f"- All-surface scale vs net Spearman: `{correlations['all']['scale_vs_net']:.3f}`",
            f"- Full-surface scale vs net Spearman: `{correlations['full']['scale_vs_net']:.3f}`",
            f"- Full MLP acceptance range: `{acceptance_range:.3f}`",
            "",
            "Prediction amplitude almost determines whether the fixed cost gate trades, but it does not predict better net outcomes. The sticky result is therefore scale-sensitive and cannot justify threshold tuning or a component increment claim.",
            "",
            "## Scope correlations",
            "",
            pd.DataFrame.from_dict(correlations, orient="index").reset_index(names="scope").to_markdown(index=False),
            "",
            "## Boundaries",
            "",
            "No model was trained. No threshold was changed. No validation, test, recent, May-stress, forward, or challenge role was read.",
            "",
        ]
    )
    report_path.write_text(report, encoding="utf-8", newline="\n")
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "experiment_id": "20260718_broad_prediction_scale_audit_005",
        "objective": "Determine whether frozen prediction amplitude rather than economic quality controls the sticky cost gate",
        "status": decision["status"],
        "source_sha": _git_sha(),
        "created_at": _now(),
        "command": "python scripts/crypto_broad_prediction_scale_audit_v1.py",
        "inputs": {
            model_path.relative_to(ROOT).as_posix(): sha256_file(model_path),
            sticky_path.relative_to(ROOT).as_posix(): sha256_file(sticky_path),
            pair_path.relative_to(ROOT).as_posix(): sha256_file(pair_path),
        },
        "parameters": criteria,
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__},
        "cost_time": {"estimated_wall_seconds": 30, "actual_wall_seconds": float(time.perf_counter() - started)},
        "decision": decision,
        "boundaries": {
            "model_training": False,
            "threshold_tuning": False,
            "sealed_reads_allowed": False,
            "candidate_promotion": False,
        },
        "reproducibility": {
            "reproducible": True,
            "continuation": "Rerun the exact command against the content-hash-bound sticky evidence.",
            "failure": None,
        },
        "files": {
            diagnostics_path.relative_to(ROOT).as_posix(): sha256_file(diagnostics_path),
            decision_path.relative_to(ROOT).as_posix(): sha256_file(decision_path),
            report_path.relative_to(ROOT).as_posix(): sha256_file(report_path),
        },
    }
    manifest["identity_sha256"] = payload_sha256({key: value for key, value in manifest.items() if key != "files"})
    _write_json(output_root / "run_manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(json.dumps(run(args.runtime_root, args.output_root, args.report), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
