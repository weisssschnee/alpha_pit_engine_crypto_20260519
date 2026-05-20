from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, clean_float, stable_hash
from crypto_a7o2c_semantic_uniqueness_audit import write_json, write_markdown_table


DATE_TAG = "20260521"
OUT_DIR = RUNTIME_DIR / "a7p2_w2_cell_registry_audit"
SOURCE_DIR = RUNTIME_DIR / "a7p_cell_failure_map_redesign"
TARGET_W2_CELLS = 64


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_bool(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def contains_liqvol(value: Any) -> bool:
    parts = {p.strip() for p in str(value).split(";") if p.strip()}
    return "liquidity" in parts and "volatility" in parts


def load_recommendations() -> pd.DataFrame:
    rec = pd.read_csv(SOURCE_DIR / "a7p_cell_policy_recommendations.csv")
    rec["w2_registry_candidate"] = rec["w2_registry_candidate"].apply(to_bool)
    rec["policy_uses_may"] = rec["policy_uses_may"].apply(to_bool)
    for col in [
        "pre_may_pass_normal_rate",
        "cost20_recent_fail_rate",
        "lag1_recent_fail_rate",
        "residual_funding_recent_fail_rate",
        "raw_recent_fail_rate",
        "raw_validation_fail_rate",
        "liquidity_volatility_share",
    ]:
        rec[col] = pd.to_numeric(rec[col], errors="coerce")
    return rec


def non_may_score(df: pd.DataFrame) -> pd.Series:
    return (
        df["pre_may_pass_normal_rate"].fillna(0.0)
        - 0.35 * df["cost20_recent_fail_rate"].fillna(1.0)
        - 0.35 * df["lag1_recent_fail_rate"].fillna(1.0)
        - 0.25 * df["residual_funding_recent_fail_rate"].fillna(1.0)
        - 0.10 * df["raw_recent_fail_rate"].fillna(1.0)
        - 0.10 * df["raw_validation_fail_rate"].fillna(1.0)
        - 0.15 * df["liquidity_volatility_share"].fillna(0.0)
    )


def build_registry(rec: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    quarantine = rec[rec["recommended_action"].eq("quarantine_control_contaminated_cell")].copy()
    eligible = rec[
        (~rec["recommended_action"].eq("quarantine_control_contaminated_cell"))
        & (~rec["policy_uses_may"])
        & (rec["negative_control_research_like_count"].fillna(0).astype(float) == 0)
    ].copy()
    eligible["registry_score_non_may"] = non_may_score(eligible)

    primary = eligible[eligible["w2_registry_candidate"]].copy()
    primary["registry_tier"] = "primary_control_clean_non_may_robust"
    primary = primary.sort_values(
        ["registry_score_non_may", "pre_may_pass_normal_rate", "cost20_recent_fail_rate", "lag1_recent_fail_rate", "cell_id"],
        ascending=[False, False, True, True, True],
    )
    primary = primary.head(TARGET_W2_CELLS).copy()

    shortfall = max(0, TARGET_W2_CELLS - len(primary))
    supplemental = eligible[
        (~eligible["cell_id"].isin(primary["cell_id"]))
        & eligible["recommended_action"].isin(
            [
                "retain_for_targeted_mutation_diagnostic",
                "redesign_for_cost_lag_robustness",
                "redesign_for_residual_independence",
                "retain_only_under_liquidity_volatility_quarantine_cap",
            ]
        )
    ].copy()
    supplemental["registry_tier"] = "supplemental_non_may_diagnostic"
    supplemental = supplemental.sort_values(
        ["registry_score_non_may", "pre_may_pass_normal_rate", "cost20_recent_fail_rate", "lag1_recent_fail_rate", "cell_id"],
        ascending=[False, False, True, True, True],
    ).head(shortfall)

    registry = pd.concat([primary, supplemental], ignore_index=True)
    registry["registry_rank"] = range(1, len(registry) + 1)
    registry["liquidity_volatility_cell"] = registry["source_field_families"].apply(contains_liqvol)
    registry["may_used_for_registry_score"] = False
    registry["may_used_for_registry_selection"] = False
    registry["quarantine_status"] = "allowed_control_clean"
    return registry, quarantine


def coverage_audit(registry: pd.DataFrame, quarantine: pd.DataFrame) -> pd.DataFrame:
    if registry.empty:
        metrics = {
            "registry_cell_count": (0, TARGET_W2_CELLS, ">="),
            "quarantined_cells_in_registry": (0, 0, "="),
        }
    else:
        motif = registry["feature_family_set"].astype(str) + "|" + registry["operator_motif"].astype(str) + "|" + registry["temporal_horizon_class"].astype(str)
        metrics = {
            "registry_cell_count": (len(registry), TARGET_W2_CELLS, ">="),
            "primary_cell_count": (int(registry["registry_tier"].eq("primary_control_clean_non_may_robust").sum()), 60, ">="),
            "supplemental_cell_count": (int(registry["registry_tier"].eq("supplemental_non_may_diagnostic").sum()), 4, "<="),
            "quarantined_cells_in_registry": (int(registry["cell_id"].isin(quarantine["cell_id"]).sum()), 0, "="),
            "policy_uses_may": (int(registry["policy_uses_may"].sum()), 0, "="),
            "registry_score_uses_may": (int(registry["may_used_for_registry_score"].sum()), 0, "="),
            "registry_selection_uses_may": (int(registry["may_used_for_registry_selection"].sum()), 0, "="),
            "hypothesis_family_count": (int(registry["hypothesis_family"].nunique()), 8, ">="),
            "feature_family_count": (int(registry["feature_family_set"].nunique()), 8, ">="),
            "single_hypothesis_family_share": (float(registry["hypothesis_family"].value_counts(normalize=True).iloc[0]), 0.25, "<="),
            "single_feature_family_share": (float(registry["feature_family_set"].value_counts(normalize=True).iloc[0]), 0.25, "<="),
            "single_feature_operator_horizon_motif_share": (float(motif.value_counts(normalize=True).iloc[0]), 0.15, "<="),
            "liquidity_volatility_cell_share": (float(registry["liquidity_volatility_cell"].mean()), 0.15, "<="),
            "control_contaminated_cells_quarantined": (len(quarantine), 2, ">="),
        }
    rows = []
    for metric, (value, threshold, op) in metrics.items():
        passed = value <= threshold if op == "<=" else value >= threshold if op == ">=" else value == threshold
        rows.append({"metric": metric, "value": clean_float(value), "threshold": threshold, "operator": op, "pass": bool(passed)})
    return pd.DataFrame(rows)


def write_report(decision: dict[str, Any], audit: pd.DataFrame, registry: pd.DataFrame, quarantine: pd.DataFrame) -> Path:
    path = REPORT_DIR / f"CRYPTO_A7P2_W2_CELL_REGISTRY_AUDIT_{DATE_TAG}.md"
    report = [
        "# Crypto A7P-2 W2 Cell Registry Audit",
        "",
        f"- generated_at: `{decision['generated_at']}`",
        f"- decision: `{decision['decision']}`",
        "- executes_new_search: `False`",
        "- executes_replay: `False`",
        f"- authorizes_w2_pilot: `{decision['authorizes_w2_pilot']}`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        f"- blockers: `{decision['blockers']}`",
        "",
        "## Coverage Audit",
        "",
        write_markdown_table(audit, 30),
        "## Quarantined Cells",
        "",
        write_markdown_table(quarantine[["checkpoint_id", "cell_id", "recommended_action", "primary_reason"]], 20),
        "## W2 Registry Preview",
        "",
        write_markdown_table(
            registry[
                [
                    "registry_rank",
                    "checkpoint_id",
                    "cell_id",
                    "registry_tier",
                    "hypothesis_family",
                    "feature_family_set",
                    "operator_motif",
                    "temporal_horizon_class",
                    "registry_score_non_may",
                    "may_used_for_registry_score",
                    "may_used_for_registry_selection",
                ]
            ],
            30,
        ),
        "## Boundary",
        "",
        "This audit only builds and checks a control-clean W2 registry. It does not execute W2, full L1, L2/L3, alpha proof, shadow, paper, or live.",
    ]
    path.write_text("\n".join(report), encoding="utf-8")
    return path


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    rec = load_recommendations()
    registry, quarantine = build_registry(rec)
    audit = coverage_audit(registry, quarantine)
    blockers = audit.loc[~audit["pass"], "metric"].astype(str).tolist()
    decision = {
        "generated_at": now,
        "decision": "PASS_A7P2CDE_W2_REGISTRY_READY_FOR_PROTECTED_PILOT_REVIEW" if not blockers else "HOLD_A7P2CDE_W2_REGISTRY",
        "executes_new_search": False,
        "executes_replay": False,
        "authorizes_w2_pilot": bool(not blockers),
        "authorizes_full_l1_without_checkpoint": False,
        "authorizes_l2_or_l3": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "blockers": blockers,
        "metrics": {
            "registry_cell_count": int(len(registry)),
            "primary_cell_count": int(registry["registry_tier"].eq("primary_control_clean_non_may_robust").sum()) if len(registry) else 0,
            "supplemental_cell_count": int(registry["registry_tier"].eq("supplemental_non_may_diagnostic").sum()) if len(registry) else 0,
            "quarantine_cell_count": int(len(quarantine)),
            "policy_uses_may": False,
        },
    }
    paths = {
        "decision": OUT_DIR / "a7p2_w2_cell_registry_decision.json",
        "manifest": OUT_DIR / "a7p2_w2_cell_registry_manifest.json",
        "quarantine": OUT_DIR / "a7p2c_control_contaminated_cell_quarantine.csv",
        "registry": OUT_DIR / "a7p2d_control_clean_w2_cell_registry.csv",
        "coverage_audit": OUT_DIR / "a7p2e_w2_registry_coverage_audit.csv",
    }
    quarantine.to_csv(paths["quarantine"], index=False)
    registry.to_csv(paths["registry"], index=False)
    audit.to_csv(paths["coverage_audit"], index=False)
    report = write_report(decision, audit, registry, quarantine)
    decision["outputs"] = {k: str(v) for k, v in paths.items()}
    decision["outputs"]["report"] = str(report)
    decision["stable_decision_hash"] = stable_hash({k: v for k, v in decision.items() if k != "stable_decision_hash"})
    write_json(paths["decision"], decision)
    manifest = {
        **decision,
        "source": str(SOURCE_DIR / "a7p_cell_policy_recommendations.csv"),
        "may_policy": {
            "allowed": ["post_selection_stress_label", "post_selection_veto", "failure_attribution"],
            "forbidden": ["registry_score", "registry_selection", "ranking", "threshold", "generation", "allocation", "mutation", "surrogate_target"],
        },
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(paths["manifest"], manifest)
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
