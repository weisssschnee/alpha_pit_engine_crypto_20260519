from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, ROOT, clean_float, stable_hash


A7K0_DIR = RUNTIME_DIR / "a7k0_generator_space_redesign_contract"
A7J2_DIR = RUNTIME_DIR / "a7j2_same_budget_redesigned_smoke"
A7K1_DIR = RUNTIME_DIR / "a7k1_generator_space_preflight"
DATE_TAG = "20260520"
PANEL_PATH = ROOT / "gold" / "panels" / "crypto_core12_1h_v1.parquet"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def safe(value: Any, default: float = 0.0) -> float:
    out = clean_float(value)
    return default if out is None else out


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def pass_col(row: pd.Series, col: str, threshold: float, op: str) -> bool:
    value = safe(row.get(col), default=np.nan)
    if not np.isfinite(value):
        return False
    if op == ">=":
        return value >= threshold
    if op == ">":
        return value > threshold
    if op == "<":
        return value < threshold
    raise ValueError(op)


def audit_feature_coverage(contract: dict[str, Any]) -> pd.DataFrame:
    features: set[str] = set()
    for spec in contract["generator_space"].values():
        for field in spec.get("allowed_features", []):
            if field in {"seeded_random", "row_shuffle", "time_shuffle", "symbol_shuffle"}:
                continue
            features.add(field)
    features.update({"symbol", "timestamp", "spot_available"})

    panel_columns = set(pq.read_schema(PANEL_PATH).names)
    cols = [c for c in sorted(features) if c in panel_columns]
    panel = pd.read_parquet(PANEL_PATH, columns=cols, engine="pyarrow")
    symbols = sorted(panel["symbol"].dropna().unique().tolist())
    rows: list[dict[str, Any]] = []
    for field in sorted(features - {"symbol", "timestamp", "spot_available"}):
        if field not in panel.columns:
            rows.append(
                {
                    "feature": field,
                    "status": "missing_from_panel",
                    "coverage_all": 0.0,
                    "symbol_count_with_95pct": 0,
                    "core12_coverage_pass": False,
                    "core6_only": False,
                    "required_lane": "blocked_until_available",
                }
            )
            continue
        coverage_by_symbol = panel.groupby("symbol")[field].apply(lambda s: float(s.notna().mean()))
        symbol_count_95 = int((coverage_by_symbol >= 0.95).sum())
        coverage_all = float(panel[field].notna().mean())
        core12_pass = symbol_count_95 == len(symbols) and coverage_all >= 0.95
        core6_only = field == "spot_perp_basis" or (symbol_count_95 < len(symbols) and symbol_count_95 >= 6)
        rows.append(
            {
                "feature": field,
                "status": "available",
                "coverage_all": coverage_all,
                "symbol_count_with_95pct": symbol_count_95,
                "symbol_count_total": len(symbols),
                "core12_coverage_pass": core12_pass,
                "core6_only": core6_only,
                "required_lane": "core12" if core12_pass else ("explicit_core6_lane" if core6_only else "blocked_or_diagnostic_only"),
                "min_symbol_coverage": float(coverage_by_symbol.min()),
                "median_symbol_coverage": float(coverage_by_symbol.median()),
            }
        )
    return pd.DataFrame(rows)


def audit_old_pool_preselection(scoreboard: pd.DataFrame) -> pd.DataFrame:
    df = scoreboard.copy()
    df["contains_spot_perp_basis"] = df["source_fields"].fillna("").str.contains("spot_perp_basis", regex=False) | df[
        "expression"
    ].fillna("").str.contains("spot_perp_basis", regex=False)

    checks: list[tuple[str, str, float, str]] = [
        ("validation_n", "raw_10bp__validation_2025H1__n", 250, ">="),
        ("recent_n", "raw_10bp__recent_oos_2025H2_2026Apr__n", 250, ">="),
        ("validation_gross_exposure", "raw_10bp__validation_2025H1__mean_gross_exposure", 0.10, ">="),
        ("recent_gross_exposure", "raw_10bp__recent_oos_2025H2_2026Apr__mean_gross_exposure", 0.10, ">="),
        ("raw_validation_positive", "raw_10bp__validation_2025H1__annualized_mean", 0.0, ">"),
        ("raw_recent_positive", "raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean", 0.0, ">"),
        ("cost20_validation_nonnegative", "raw_20bp__validation_2025H1__annualized_mean", 0.0, ">="),
        ("cost20_recent_nonnegative", "raw_20bp__recent_oos_2025H2_2026Apr__annualized_mean", 0.0, ">="),
        (
            "lag1_validation_nonnegative",
            "execution_lag_1bar_raw_10bp__validation_2025H1__annualized_mean",
            0.0,
            ">=",
        ),
        (
            "lag1_recent_nonnegative",
            "execution_lag_1bar_raw_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            0.0,
            ">=",
        ),
        (
            "residual_funding_validation_positive",
            "residual_vs_funding_10bp__validation_2025H1__annualized_mean",
            0.0,
            ">",
        ),
        (
            "residual_funding_recent_positive",
            "residual_vs_funding_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            0.0,
            ">",
        ),
        (
            "residual_core4_recent_positive",
            "residual_vs_core4_10bp__recent_oos_2025H2_2026Apr__annualized_mean",
            0.0,
            ">",
        ),
    ]
    for name, col, threshold, op in checks:
        df[f"pass_{name}"] = df.apply(lambda r: pass_col(r, col, threshold, op), axis=1)
    df["pass_beta"] = (df["funding_beta_recent"].fillna(99).abs() < 0.50) & (
        df["core4_beta_recent"].fillna(99).abs() < 0.50
    )
    df["pass_spot_artifact"] = ~df["contains_spot_perp_basis"]

    pass_cols = [c for c in df.columns if c.startswith("pass_")]
    df["a7k_preselection_pass"] = df[pass_cols].all(axis=1)

    def first_fail(row: pd.Series) -> str:
        for col in pass_cols:
            if not bool(row[col]):
                return col.replace("pass_", "")
        return "pass"

    df["first_a7k_preselection_fail"] = df.apply(first_fail, axis=1)
    return df


def summarize_gate_counts(pre: pd.DataFrame) -> pd.DataFrame:
    rows = []
    pass_cols = [c for c in pre.columns if c.startswith("pass_")]
    for col in pass_cols:
        rows.append(
            {
                "gate": col.replace("pass_", ""),
                "pass_count": int(pre[col].sum()),
                "fail_count": int((~pre[col]).sum()),
                "pass_rate": float(pre[col].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(["pass_rate", "gate"], ascending=[True, True])


def audit_family_diversity(pre: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for subset_name, subset in [
        ("old_pool_all", pre),
        ("old_pool_a7j_selected", pre[pre.get("a7j_selected_for_replay", False) == True],  # noqa: E712
        ),
        ("a7k_preselection_pass", pre[pre["a7k_preselection_pass"]]),
    ]:
        total = len(subset)
        counts = Counter(subset["family"].fillna("unknown").tolist())
        if total == 0:
            rows.append(
                {
                    "subset": subset_name,
                    "family": "none",
                    "count": 0,
                    "share": 0.0,
                    "cap": 0.25,
                    "cap_pass": True,
                }
            )
            continue
        for family, count in counts.items():
            share = count / total
            rows.append(
                {
                    "subset": subset_name,
                    "family": family,
                    "count": count,
                    "share": share,
                    "cap": 0.25,
                    "cap_pass": share <= 0.25 or total < 4,
                }
            )
    return pd.DataFrame(rows)


def audit_may_exclusion(contract: dict[str, Any], pre: pd.DataFrame) -> pd.DataFrame:
    preselection_cols = [c for c in pre.columns if c.startswith("pass_")]
    rank_like_cols = [
        "a7j_rank_score",
        "component_raw_validation",
        "component_raw_recent",
        "component_residual_funding_validation",
        "component_residual_funding_recent",
        "component_residual_core4_recent",
        "component_cost20_validation",
        "component_cost20_recent",
        "component_lag1_validation",
        "component_lag1_recent",
    ]
    rows = [
        {
            "check": "contract_forbids_may_in_generator_tuning",
            "pass": "generator_parameter_tuning" in contract["may_policy"]["forbidden_uses"],
        },
        {
            "check": "preselection_gate_columns_exclude_may",
            "pass": not any("may" in c.lower() or "fresh_forward" in c.lower() for c in preselection_cols),
        },
        {
            "check": "score_columns_exclude_may",
            "pass": not any("may" in c.lower() or "fresh_forward" in c.lower() for c in rank_like_cols),
        },
        {
            "check": "may_columns_present_only_as_stress_metrics",
            "pass": any("fresh_forward" in c for c in pre.columns)
            and not any("fresh_forward" in c for c in preselection_cols),
        },
    ]
    return pd.DataFrame(rows)


def main() -> int:
    A7K1_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    contract_path = A7K0_DIR / f"crypto_a7k0_generator_space_contract_{DATE_TAG}.json"
    contract = load_json(contract_path)
    scoreboard_path = A7J2_DIR / "a7j2_candidate_scoreboard.csv"
    scoreboard = pd.read_csv(scoreboard_path)

    feature_coverage = audit_feature_coverage(contract)
    preselection = audit_old_pool_preselection(scoreboard)
    gate_counts = summarize_gate_counts(preselection)
    family_diversity = audit_family_diversity(preselection)
    may_audit = audit_may_exclusion(contract, preselection)
    beta_screen = preselection[
        [
            "candidate_id",
            "arm",
            "family",
            "expression",
            "funding_beta_recent",
            "core4_beta_recent",
            "pass_beta",
            "a7k_preselection_pass",
            "first_a7k_preselection_fail",
        ]
    ].copy()
    cost_lag = preselection[
        [
            "candidate_id",
            "arm",
            "family",
            "expression",
            "pass_cost20_validation_nonnegative",
            "pass_cost20_recent_nonnegative",
            "pass_lag1_validation_nonnegative",
            "pass_lag1_recent_nonnegative",
            "a7k_preselection_pass",
            "first_a7k_preselection_fail",
        ]
    ].copy()
    activity = preselection[
        [
            "candidate_id",
            "arm",
            "family",
            "expression",
            "contains_spot_perp_basis",
            "pass_validation_n",
            "pass_recent_n",
            "pass_validation_gross_exposure",
            "pass_recent_gross_exposure",
            "pass_spot_artifact",
            "a7k_preselection_pass",
            "first_a7k_preselection_fail",
        ]
    ].copy()

    feature_path = A7K1_DIR / "a7k1_feature_coverage_audit.csv"
    activity_path = A7K1_DIR / "a7k1_activity_exposure_audit.csv"
    family_path = A7K1_DIR / "a7k1_family_diversity_audit.csv"
    cost_lag_path = A7K1_DIR / "a7k1_cost_lag_preselection_audit.csv"
    beta_path = A7K1_DIR / "a7k1_funding_core4_beta_screen.csv"
    may_path = A7K1_DIR / "a7k1_may_exclusion_audit.csv"
    gate_path = A7K1_DIR / "a7k1_gate_pass_counts.csv"
    old_pool_path = A7K1_DIR / "a7k1_old_pool_preselection_screen.csv"

    feature_coverage.to_csv(feature_path, index=False)
    activity.to_csv(activity_path, index=False)
    family_diversity.to_csv(family_path, index=False)
    cost_lag.to_csv(cost_lag_path, index=False)
    beta_screen.to_csv(beta_path, index=False)
    may_audit.to_csv(may_path, index=False)
    gate_counts.to_csv(gate_path, index=False)
    preselection.to_csv(old_pool_path, index=False)

    feature_blockers = []
    for _, row in feature_coverage.iterrows():
        if row["required_lane"] == "blocked_or_diagnostic_only":
            feature_blockers.append(f"{row['feature']}: insufficient core12 coverage")
        if row["required_lane"] == "blocked_until_available":
            feature_blockers.append(f"{row['feature']}: missing")

    may_exclusion_pass = bool(may_audit["pass"].all())
    old_pool_pass_count = int(preselection["a7k_preselection_pass"].sum())
    old_pool_generated = int(len(preselection))
    old_pool_selected = int(preselection["a7j_selected_for_replay"].sum()) if "a7j_selected_for_replay" in preselection else 0
    old_pool_family_cap_pass = bool(family_diversity[family_diversity["subset"] == "a7k_preselection_pass"]["cap_pass"].all())

    blockers = []
    if not may_exclusion_pass:
        blockers.append("may_exclusion_failed")
    if feature_blockers:
        blockers.append("feature_coverage_blockers_present")
    # Passing old A7J candidates is not a success: old pool was already alpha-HOLD.
    if old_pool_pass_count > 0:
        blockers.append("old_a7j_pool_still_has_candidates_passing_a7k_preselection")
    if not old_pool_family_cap_pass:
        blockers.append("old_pool_family_cap_fail")

    if may_exclusion_pass and not blockers:
        decision = "PASS_A7K1_OLD_POOL_FAILURE_MODE_SCREEN"
    elif may_exclusion_pass and blockers == ["feature_coverage_blockers_present"]:
        decision = "HOLD_A7K1_FEATURE_COVERAGE_REQUIRES_NEW_SPACE_REPAIR"
    else:
        decision = "HOLD_A7K1_PREFLIGHT_BLOCKED"

    authorizes_a7k2 = False
    if decision == "PASS_A7K1_OLD_POOL_FAILURE_MODE_SCREEN":
        # A7K-1 validates the gates and rejects the old failed pool. It still does not implement
        # or test a new generator; A7K-2 needs a separate new-space generator implementation review.
        authorizes_a7k2 = False

    generator_manifest = {
        "generated_at": now,
        "contract_id": contract["contract_id"],
        "contract_hash": contract["stable_contract_hash"],
        "generator_space": contract["generator_space"],
        "preselection_gates": contract["global_preselection_gates"],
        "may_policy": contract["may_policy"],
        "feature_coverage_summary_hash": stable_hash(feature_coverage.fillna("").to_dict(orient="list")),
    }
    generator_manifest_path = A7K1_DIR / "a7k1_generator_space_manifest.json"
    write_json(generator_manifest_path, generator_manifest)

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7k2": authorizes_a7k2,
        "authorizes_alpha_proof": False,
        "may_exclusion_pass": may_exclusion_pass,
        "old_pool_generated_count": old_pool_generated,
        "old_pool_a7j_selected_count": old_pool_selected,
        "old_pool_a7k_preselection_pass_count": old_pool_pass_count,
        "feature_blockers": feature_blockers,
        "blockers": blockers,
        "outputs": {
            "generator_space_manifest": str(generator_manifest_path),
            "feature_coverage_audit": str(feature_path),
            "activity_exposure_audit": str(activity_path),
            "family_diversity_audit": str(family_path),
            "cost_lag_preselection_audit": str(cost_lag_path),
            "funding_core4_beta_screen": str(beta_path),
            "may_exclusion_audit": str(may_path),
            "gate_pass_counts": str(gate_path),
            "old_pool_preselection_screen": str(old_pool_path),
        },
    }
    manifest_path = A7K1_DIR / f"crypto_a7k1_manifest_{DATE_TAG}.json"
    write_json(manifest_path, manifest)

    top_gate_fail = gate_counts.head(8)
    report_path = REPORT_DIR / f"CRYPTO_A7K1_GENERATOR_SPACE_PREFLIGHT_{DATE_TAG}.md"
    lines = [
        "# Crypto A7K-1 Generator-Space Preflight",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- evidence_level: `generator_preflight_not_alpha_proof`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        f"- authorizes_a7k2: `{authorizes_a7k2}`",
        "- authorizes_alpha_proof: `False`",
        f"- may_exclusion_pass: `{may_exclusion_pass}`",
        f"- old_pool_a7k_preselection_pass_count: `{old_pool_pass_count}/{old_pool_generated}`",
        f"- blockers: `{blockers}`",
        "",
        "## Interpretation",
        "",
        "- A7K-1 validates the redesigned preselection gates against the frozen failed A7J/A7I pool.",
        "- A pass here means the old failure modes are mechanically screened; it does not mean a new generator can produce alpha candidates.",
        "- A7K-2 remains blocked until a new-space generator implementation is reviewed with the same contract.",
        "",
        "## Feature Coverage",
        "",
        "| feature | required lane | coverage_all | symbols >=95% | core12 pass |",
        "|---|---|---:|---:|---:|",
    ]
    for _, row in feature_coverage.sort_values("feature").iterrows():
        lines.append(
            f"| `{row['feature']}` | `{row['required_lane']}` | {float(row['coverage_all']):.4f} | "
            f"{int(row.get('symbol_count_with_95pct', 0))}/{int(row.get('symbol_count_total', 12) or 12)} | "
            f"`{bool(row['core12_coverage_pass'])}` |"
        )
    lines += [
        "",
        "## Tightest Old-Pool Gates",
        "",
        "| gate | pass_count | fail_count | pass_rate |",
        "|---|---:|---:|---:|",
    ]
    for _, row in top_gate_fail.iterrows():
        lines.append(
            f"| `{row['gate']}` | {int(row['pass_count'])} | {int(row['fail_count'])} | {float(row['pass_rate']):.4f} |"
        )
    lines += [
        "",
        "## May Exclusion",
        "",
        "| check | pass |",
        "|---|---:|",
    ]
    for _, row in may_audit.iterrows():
        lines.append(f"| `{row['check']}` | `{bool(row['pass'])}` |")
    lines += [
        "",
        "## Boundary",
        "",
        "- May remains stress-only.",
        "- This preflight does not authorize alpha proof, shadow, paper, live, or production.",
        "- Do not expand the old A7J generator budget. Next valid engineering work is new-space generator implementation review or forward wait.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7K1_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7K-1 Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                f"- old_pool_a7k_preselection_pass_count: `{old_pool_pass_count}/{old_pool_generated}`",
                f"- authorizes_a7k2: `{authorizes_a7k2}`",
                f"- blockers: `{blockers}`",
                "",
                "A7K-1 confirms whether the redesigned generator-space gates catch A7J failure modes. It does not test a new generator and does not promote any crypto alpha.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print("A7K1_REPORT=" + str(report_path))
    print("A7K1_DECISION_RECORD=" + str(decision_path))
    print("A7K1_MANIFEST=" + str(manifest_path))
    print("DECISION=" + decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
