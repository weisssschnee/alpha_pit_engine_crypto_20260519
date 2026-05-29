from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ab1_selector_rewrite_dryrun"
REPORT = REPO / "reports" / "CRYPTO_A7AB1_SELECTOR_REWRITE_DRYRUN_20260529.md"

A7AB0_MANIFEST = REPO / "runtime" / "a7ab0_selector_rewrite_dryrun_contract" / "a7ab0_manifest.json"
A7AB0_SCORE_FEATURES = REPO / "runtime" / "a7ab0_selector_rewrite_dryrun_contract" / "a7ab0_selector_score_features.csv"
A7AA1_CANDIDATES = REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_primitive_response_candidates.csv"
A7AA2_SEEDS = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_selector_seed_fields.csv"
A7AA3_CONTRACT = REPO / "runtime" / "a7aa3_selector_rewrite_contract" / "a7aa3_selector_rewrite_contract.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and not pd.isna(value):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def finite_float(value: Any, default: float = 0.0) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    return f if math.isfinite(f) else default


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def file_meta(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False}
    stat = path.stat()
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_time_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
    }


def make_blueprint(row: pd.Series) -> str:
    field = str(row["field_name"])
    transform = str(row["transform"])
    label = str(row["label_family"])
    horizon = int(row["label_horizon_h"])
    orient = "short_high" if finite_float(row["orientation_from_train"]) < 0 else "long_high"
    return f"primitive_response::{field}::{transform}::{label}::{horizon}h::{orient}"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ab0 = read_json(A7AB0_MANIFEST)
    if not a7ab0.get("authorizes_a7ab1_selector_rewrite_dryrun"):
        raise SystemExit("A7AB-0 does not authorize A7AB-1")

    contract = read_json(A7AA3_CONTRACT)
    candidates = pd.read_csv(A7AA1_CANDIDATES)
    seeds = pd.read_csv(A7AA2_SEEDS)
    score_features = pd.read_csv(A7AB0_SCORE_FEATURES)

    seed_fields = set(seeds["field_name"].astype(str))
    allowed_labels = set(contract.get("allowed_label_focus", []))
    allowed_horizons = {int(x) for x in contract.get("allowed_horizon_focus", [])}

    rows: list[dict[str, Any]] = []
    gates: list[dict[str, Any]] = []
    for idx, row in candidates.iterrows():
        field = str(row["field_name"])
        label = str(row["label_family"])
        horizon = int(row["label_horizon_h"])
        control_ratio = finite_float(row.get("control_ratio_premay_max"), default=999.0)
        premay_positive = int(finite_float(row.get("premay_positive_split_count"), default=0.0))
        premay_all_positive = as_bool(row.get("premay_all_positive"))
        lag_ok = as_bool(row.get("lag_ok"))

        gate_map = {
            "seed_field": field in seed_fields,
            "premay_all_positive": premay_all_positive,
            "control_ratio_lt_1": control_ratio < 1.0,
            "lag_ok": lag_ok,
            "label_allowed": label in allowed_labels,
            "horizon_allowed": horizon in allowed_horizons,
            "no_may_used": True,
        }
        reject_reasons = [name for name, ok in gate_map.items() if not ok]
        eligible = len(reject_reasons) == 0

        orientation = finite_float(row.get("orientation_from_train"), default=1.0)
        recent_tstat = orientation * finite_float(row.get("recent_oos_2026JanApr_tstat"))
        validation_tstat = orientation * finite_float(row.get("validation_2025H1_tstat"))
        test_tstat = orientation * finite_float(row.get("test_2025H2_tstat"))
        recent_nonoverlap = orientation * finite_float(row.get("recent_oos_2026JanApr_nonoverlap_min_tstat"))
        validation_nonoverlap = orientation * finite_float(row.get("validation_2025H1_nonoverlap_min_tstat"))
        test_nonoverlap = orientation * finite_float(row.get("test_2025H2_nonoverlap_min_tstat"))
        robust_tstat_floor = min(validation_nonoverlap, test_nonoverlap, recent_nonoverlap)

        premay_score = clamp(premay_positive / 3.0)
        control_margin = clamp(1.0 - control_ratio)
        lag_survival_score = clamp(finite_float(row.get("one_bar_lag_recent_oriented")) / 0.03)
        robust_tstat_score = clamp(robust_tstat_floor / 5.0)
        family_diversity_prior = 1.0
        selector_score = (
            0.30 * premay_score
            + 0.25 * control_margin
            + 0.20 * lag_survival_score
            + 0.15 * robust_tstat_score
            + 0.10 * family_diversity_prior
        )

        candidate_id = f"a7ab1_seed_{idx:03d}"
        rows.append(
            {
                "candidate_id": candidate_id,
                "field_name": field,
                "field_family": row["field_family"],
                "source_family": row["source_family"],
                "feature_class": row["feature_class"],
                "transform": row["transform"],
                "label_family": label,
                "label_horizon_h": horizon,
                "orientation_from_train": orientation,
                "control_ratio_premay_max": control_ratio,
                "control_margin": control_margin,
                "premay_positive_split_count": premay_positive,
                "premay_score": premay_score,
                "one_bar_lag_recent_oriented": finite_float(row.get("one_bar_lag_recent_oriented")),
                "lag_survival_score": lag_survival_score,
                "validation_oriented_tstat": validation_tstat,
                "test_oriented_tstat": test_tstat,
                "recent_oriented_tstat": recent_tstat,
                "robust_tstat_floor": robust_tstat_floor,
                "robust_tstat_score": robust_tstat_score,
                "selector_score": selector_score if eligible else -1.0,
                "eligible": eligible,
                "reject_reasons": "|".join(reject_reasons),
                "blueprint": make_blueprint(row),
                "allowed_next_use": "A7AB2_contract_seed_only" if eligible else "not_allowed",
            }
        )
        gates.append({"candidate_id": candidate_id, **gate_map, "eligible": eligible, "reject_reasons": "|".join(reject_reasons)})

    scoreboard = pd.DataFrame(rows).sort_values(
        ["eligible", "selector_score", "control_margin", "robust_tstat_floor"],
        ascending=[False, False, False, False],
    )
    gate_audit = pd.DataFrame(gates)

    # Diversity-aware selection: this is still dry-run queue construction, not formula generation.
    max_selected = 10
    max_per_field = 3
    max_per_family = 4
    selected_rows: list[dict[str, Any]] = []
    field_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    for rec in scoreboard.to_dict("records"):
        if not rec["eligible"]:
            continue
        field = str(rec["field_name"])
        family = str(rec["field_family"])
        if field_counts.get(field, 0) >= max_per_field:
            continue
        if family_counts.get(family, 0) >= max_per_family:
            continue
        selected_rows.append(rec)
        field_counts[field] = field_counts.get(field, 0) + 1
        family_counts[family] = family_counts.get(family, 0) + 1
        if len(selected_rows) >= max_selected:
            break

    selected = pd.DataFrame(selected_rows)
    if selected.empty:
        selected = pd.DataFrame(columns=scoreboard.columns)
    selected = selected.reset_index(drop=True)
    selected.insert(0, "selector_rank", range(1, len(selected) + 1))

    selected_count = int(len(selected))
    selected_seed_fields = int(selected["field_name"].nunique()) if selected_count else 0
    selected_field_families = int(selected["field_family"].nunique()) if selected_count else 0
    selected_max_control_ratio = (
        float(selected["control_ratio_premay_max"].max()) if selected_count else None
    )
    top_field_share = (
        float(selected["field_name"].value_counts(normalize=True).iloc[0]) if selected_count else None
    )
    top_family_share = (
        float(selected["field_family"].value_counts(normalize=True).iloc[0]) if selected_count else None
    )

    pass_gate = (
        selected_count >= 8
        and selected_seed_fields >= 4
        and selected_field_families >= 3
        and (selected_max_control_ratio is not None and selected_max_control_ratio < 1.0)
    )
    decision = (
        "PASS_A7AB1_SELECTOR_REWRITE_DRYRUN_READY_FOR_A7AB2_CONTRACT"
        if pass_gate
        else "HOLD_A7AB1_SELECTOR_REWRITE_QUEUE_WEAK"
    )

    manifest = {
        "stage": "A7AB-1",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_selector_dryrun": True,
        "executes_formula_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "candidate_count": int(len(scoreboard)),
        "eligible_count": int(scoreboard["eligible"].sum()),
        "selected_count": selected_count,
        "selected_seed_field_count": selected_seed_fields,
        "selected_field_family_count": selected_field_families,
        "selected_max_control_ratio": selected_max_control_ratio,
        "top_field_share": top_field_share,
        "top_family_share": top_family_share,
        "authorizes_a7ab2_seed_constrained_micro_generation_contract": bool(pass_gate),
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "selection_caps": {
            "max_selected": max_selected,
            "max_per_field": max_per_field,
            "max_per_family": max_per_family,
        },
        "input_files": {
            "a7ab0_manifest": file_meta(A7AB0_MANIFEST),
            "a7aa1_candidates": file_meta(A7AA1_CANDIDATES),
            "a7aa2_seeds": file_meta(A7AA2_SEEDS),
            "a7aa3_contract": file_meta(A7AA3_CONTRACT),
        },
    }

    scoreboard.to_csv(RUNTIME / "a7ab1_seed_scoreboard.csv", index=False)
    selected.to_csv(RUNTIME / "a7ab1_selector_queue.csv", index=False)
    gate_audit.to_csv(RUNTIME / "a7ab1_selector_hard_gate_audit.csv", index=False)
    score_features.to_csv(RUNTIME / "a7ab1_score_feature_weights.csv", index=False)
    write_json(RUNTIME / "a7ab1_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ab1_authorization_matrix.json",
        {
            "A7AB-1": {"status": decision},
            "A7AB-2_seed_constrained_micro_generation_contract": {"authorized": bool(pass_gate)},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    experiment_record = {
        "experiment_id": "20260529_a7ab1_selector_rewrite_dryrun",
        "objective": "construct primitive-response-first selector queue before any formula generation",
        "status": "completed",
        "mode": "light",
        "commands": [
            "python -m py_compile scripts/crypto_a7ab1_selector_rewrite_dryrun.py",
            "python scripts/crypto_a7ab1_selector_rewrite_dryrun.py",
        ],
        "reproducible": True,
        "next_action": "write A7AB-2 contract only if A7AB-1 pass remains accepted",
    }
    write_json(RUNTIME / "a7ab1_experiment_record.json", experiment_record)

    lines = [
        "# CRYPTO A7AB-1 SELECTOR REWRITE DRYRUN",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-1 constructs a dry-run selector queue from A7AA primitive response candidates. It does not generate formulas, run replay, train a model, or authorize search execution.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Bias / Leakage Boundary",
        "",
        "- May is not used in selector score, thresholds, generation, mutation, or authorization.",
        "- Inputs are primitive response diagnostics, not a tradable replay.",
        "- Queue entries are blueprint seeds only; they are not alpha candidates.",
        "- Formula search execution remains unauthorized.",
        "",
        "## Selected Queue",
        "",
        md_table(
            selected[
                [
                    "selector_rank",
                    "candidate_id",
                    "field_name",
                    "field_family",
                    "transform",
                    "label_family",
                    "label_horizon_h",
                    "control_ratio_premay_max",
                    "robust_tstat_floor",
                    "selector_score",
                    "blueprint",
                ]
            ]
            if not selected.empty
            else selected
        ),
        "",
        "## Scoreboard",
        "",
        md_table(
            scoreboard[
                [
                    "candidate_id",
                    "field_name",
                    "field_family",
                    "transform",
                    "label_family",
                    "label_horizon_h",
                    "eligible",
                    "control_ratio_premay_max",
                    "robust_tstat_floor",
                    "selector_score",
                    "reject_reasons",
                ]
            ],
            max_rows=40,
        ),
        "",
        "## Hard Gate Audit",
        "",
        md_table(gate_audit, max_rows=40),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
