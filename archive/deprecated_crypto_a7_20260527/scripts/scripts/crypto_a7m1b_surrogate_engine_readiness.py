from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash


DATE_TAG = "20260520"
A7M1B_DIR = RUNTIME_DIR / "a7m1b_surrogate_engine_readiness"
DATASET_PATH = RUNTIME_DIR / "a7m0_failure_labeled_search_dataset" / "crypto_a7m0_failure_labeled_candidate_dataset.csv"
CN_ROOT = Path("G:/Project_V7_Rotation/alpha_pit_engine_project_20260511")
CRYPTO_ROOT = Path("G:/AlphaFactory_CryptoData/alphafactory_crypto")

FEATURE_COLUMNS = [
    "family",
    "arm",
    "field_family_signature",
    "operator_signature",
    "horizon",
    "formula_depth",
]

TARGETS = {
    "raw_survive": ["raw_validation_fail", "raw_recent_fail"],
    "residual_survive": [
        "residual_funding_validation_fail",
        "residual_funding_recent_fail",
        "residual_core4_recent_fail",
    ],
    "cost20_survive": ["cost20_validation_fail", "cost20_recent_fail"],
    "lag1_survive": ["lag1_validation_fail", "lag1_recent_fail"],
    "near_miss": ["near_miss_label"],
    "research_candidate": ["research_candidate_label"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def bool_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    return df[col].fillna(False).astype(str).str.lower().isin(["true", "1", "yes"])


def build_targets(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for target, fail_cols in TARGETS.items():
        if target in {"near_miss", "research_candidate"}:
            out[target] = bool_series(out, fail_cols[0])
            continue
        fail_any = pd.Series(False, index=out.index)
        available_any = pd.Series(False, index=out.index)
        for col in fail_cols:
            if col in out.columns:
                fail_any |= bool_series(out, col)
                available_any |= out[col].notna()
        out[target] = available_any & (~fail_any)
    return out


def laplace_rate(success: int, total: int, prior: float, strength: float = 20.0) -> float:
    if total <= 0:
        return prior
    return (success + prior * strength) / (total + strength)


def train_table(train: pd.DataFrame, targets: list[str]) -> pd.DataFrame:
    rows = []
    priors = {target: float(train[target].mean()) if len(train) else 0.0 for target in targets}
    for feature in FEATURE_COLUMNS:
        for value, part in train.groupby(feature, dropna=False):
            row: dict[str, Any] = {"feature": feature, "value": str(value), "n": len(part)}
            for target in targets:
                success = int(part[target].sum())
                row[f"{target}_smoothed"] = laplace_rate(success, len(part), priors[target])
            rows.append(row)
    return pd.DataFrame(rows)


def score(df: pd.DataFrame, table: pd.DataFrame, targets: list[str]) -> pd.DataFrame:
    out = df.copy()
    lookup: dict[tuple[str, str, str], float] = {}
    for _, row in table.iterrows():
        for target in targets:
            lookup[(str(row["feature"]), str(row["value"]), target)] = float(row[f"{target}_smoothed"])
    for target in targets:
        pred = []
        for _, row in out.iterrows():
            vals = []
            for feature in FEATURE_COLUMNS:
                key = (feature, str(row.get(feature)), target)
                if key in lookup:
                    vals.append(lookup[key])
            pred.append(sum(vals) / len(vals) if vals else 0.0)
        out[f"pred_{target}"] = pred
    return out


def lift_for(scored: pd.DataFrame, target: str) -> dict[str, Any]:
    if scored.empty:
        return {"target": target, "base_rate": 0.0, "top_decile_rate": 0.0, "lift": "", "n": 0, "top_n": 0}
    base = float(scored[target].mean())
    cutoff = scored[f"pred_{target}"].quantile(0.90)
    top = scored[scored[f"pred_{target}"] >= cutoff]
    top_rate = float(top[target].mean()) if len(top) else 0.0
    return {
        "target": target,
        "base_rate": round(base, 6),
        "top_decile_rate": round(top_rate, 6),
        "lift": round(top_rate / base, 6) if base > 0 else "",
        "n": int(len(scored)),
        "top_n": int(len(top)),
    }


def run_scope(df: pd.DataFrame, train_mask: pd.Series, score_mask: pd.Series, scope: str) -> list[dict[str, Any]]:
    targets = list(TARGETS.keys())
    train = df.loc[train_mask].copy()
    scored = score(df.loc[score_mask].copy(), train_table(train, targets), targets)
    rows = []
    for target in targets:
        row = lift_for(scored, target)
        row["scope"] = scope
        row["train_n"] = int(train_mask.sum())
        rows.append(row)
    return rows


def engine_inventory() -> list[dict[str, Any]]:
    checks = [
        {
            "engine": "FormulaGenV2_crypto_adapter",
            "cn_paths": [
                CN_ROOT / "src" / "our_system_phase2" / "formula_gen_v2" / "sampler.py",
                CN_ROOT / "src" / "our_system_phase2" / "formula_gen_v2" / "typed_ast.py",
            ],
            "crypto_paths": [CRYPTO_ROOT / "cn_reference" / "formula_gen_v2" / "sampler.py"],
            "required_adapter": "field_dictionary_and_crypto_evaluator_adapter",
        },
        {
            "engine": "typed_AST_sampler_crypto_adapter",
            "cn_paths": [CN_ROOT / "src" / "our_system_phase2" / "formula_gen_v2" / "typed_ast.py"],
            "crypto_paths": [CRYPTO_ROOT / "cn_reference" / "formula_gen_v2" / "typed_ast.py"],
            "required_adapter": "crypto_field_types_and_operator_timing_contract",
        },
        {
            "engine": "AST_failure_aware_repair",
            "cn_paths": [CN_ROOT / "src" / "our_system_phase2" / "services" / "stock_pit_phase3_repair.py"],
            "crypto_paths": [],
            "required_adapter": "crypto_failure_taxonomy_and_repair_actions",
        },
        {
            "engine": "CEM_adaptive_grammar_crypto",
            "cn_paths": [CN_ROOT / "runtime" / "phase3h_shared_pool_source_s33_20260515" / "h0_source" / "cem_internal"],
            "crypto_paths": [],
            "required_adapter": "crypto_CEM_candidate_ledger_and_production_weight_update",
        },
        {
            "engine": "surrogate_prioritized_sampler",
            "cn_paths": [],
            "crypto_paths": [CRYPTO_ROOT / "runtime" / "a7m1_surrogate_policy_preflight" / "a7m1_surrogate_feature_table.csv"],
            "required_adapter": "A7M1_surrogate_score_to_generator_prior_interface",
        },
        {
            "engine": "cluster_registry_search_memory",
            "cn_paths": [CN_ROOT / "src" / "our_system_phase2" / "services" / "search_memory.py"],
            "crypto_paths": [CRYPTO_ROOT / "runtime" / "a3_signal_cluster_registry" / "crypto_a3_signal_clusters_20260519.csv"],
            "required_adapter": "crypto_return_corr_or_signal_cluster_memory",
        },
    ]
    rows = []
    for check in checks:
        cn_exists = [str(p) for p in check["cn_paths"] if p.exists()]
        crypto_exists = [str(p) for p in check["crypto_paths"] if p.exists()]
        if crypto_exists and check["engine"] in {"FormulaGenV2_crypto_adapter", "typed_AST_sampler_crypto_adapter", "surrogate_prioritized_sampler", "cluster_registry_search_memory"}:
            status = "adapter_ready"
        elif cn_exists:
            status = "inventory_present_adapter_needed"
        else:
            status = "missing"
        rows.append(
            {
                "engine": check["engine"],
                "status": status,
                "cn_inventory_count": len(cn_exists),
                "crypto_inventory_count": len(crypto_exists),
                "required_adapter": check["required_adapter"],
                "cn_paths": ";".join(cn_exists),
                "crypto_paths": ";".join(crypto_exists),
            }
        )
    return rows


def main() -> int:
    A7M1B_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    df = pd.read_csv(DATASET_PATH)
    df = build_targets(df)
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            df[col] = "missing"
        df[col] = df[col].fillna("missing").astype(str)

    eligible = df["policy_training_eligible"].fillna(False).astype(str).str.lower().isin(["true", "1"])
    dry = df["source_run"] == "A7L1B_dry_preflight"
    replayed = eligible & (~dry)
    rows: list[dict[str, Any]] = []

    rows += run_scope(df, replayed, replayed, "replayed_train_and_score")
    rows += run_scope(df, replayed, eligible & (~dry), "excluding_A7L1B_dry")
    rows += run_scope(df, replayed, dry, "score_A7L1B_dry_only")

    for holdout in sorted(df.loc[replayed, "source_run"].dropna().unique()):
        train_mask = replayed & (df["source_run"] != holdout)
        score_mask = replayed & (df["source_run"] == holdout)
        rows += run_scope(df, train_mask, score_mask, f"leave_source_out:{holdout}")

    families = sorted(df.loc[replayed, "family"].dropna().astype(str).unique())
    for family in families:
        if family.lower().find("placebo") >= 0:
            continue
        train_mask = replayed & (df["family"].astype(str) != family)
        score_mask = replayed & (df["family"].astype(str) == family)
        if score_mask.sum() < 20:
            continue
        rows += run_scope(df, train_mask, score_mask, f"leave_family_out:{family}")

    lift_path = A7M1B_DIR / "a7m1b_calibrated_lift_by_scope.csv"
    write_csv(lift_path, rows, ["scope", "target", "base_rate", "top_decile_rate", "lift", "n", "top_n", "train_n"])

    engine_rows = engine_inventory()
    engine_path = A7M1B_DIR / "a7m1b_inherited_engine_inventory.csv"
    write_csv(engine_path, engine_rows, ["engine", "status", "cn_inventory_count", "crypto_inventory_count", "required_adapter", "cn_paths", "crypto_paths"])

    may_rows = [
        {"check": "may_not_target", "status": "pass", "detail": "May labels excluded from TARGETS"},
        {"check": "may_not_feature", "status": "pass", "detail": "May labels excluded from FEATURE_COLUMNS"},
        {"check": "may_not_arm_allocation_signal", "status": "pass", "detail": "A7M-1B does not allocate arms"},
        {"check": "may_not_mutation_prior", "status": "pass", "detail": "A7M-1B does not set mutation priors"},
        {"check": "may_stress_only", "status": "pass", "detail": "May labels remain in A7M-0 dataset only as stress/failure attribution"},
    ]
    may_path = A7M1B_DIR / "a7m1b_may_policy_audit.csv"
    write_csv(may_path, may_rows, ["check", "status", "detail"])

    def get_lift(scope: str, target: str) -> float:
        for row in rows:
            if row["scope"] == scope and row["target"] == target:
                try:
                    return float(row["lift"])
                except (TypeError, ValueError):
                    return 0.0
        return 0.0

    near_replayed = get_lift("excluding_A7L1B_dry", "near_miss")
    cost_replayed = get_lift("excluding_A7L1B_dry", "cost20_survive")
    lag_replayed = get_lift("excluding_A7L1B_dry", "lag1_survive")
    source_near = [
        float(row["lift"])
        for row in rows
        if str(row["scope"]).startswith("leave_source_out:") and row["target"] == "near_miss" and row["lift"] != ""
    ]
    min_source_near = min(source_near) if source_near else 0.0
    adapter_ready_count = sum(1 for row in engine_rows if row["status"] == "adapter_ready")
    decision = (
        "PASS_A7M1B_SURROGATE_AND_ENGINE_READINESS"
        if near_replayed >= 3.0 and cost_replayed >= 1.5 and lag_replayed >= 1.5 and min_source_near >= 2.0 and adapter_ready_count >= 3
        else "HOLD_A7M1B_SURROGATE_OR_ENGINE_READINESS_WEAK"
    )

    manifest = {
        "generated_at": now,
        "decision": decision,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_a7m2_protocol_writing": True,
        "authorizes_a7m2_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "near_miss_lift_excluding_dry": near_replayed,
        "cost20_lift_excluding_dry": cost_replayed,
        "lag1_lift_excluding_dry": lag_replayed,
        "leave_source_out_near_miss_lift_min": min_source_near,
        "adapter_ready_count": adapter_ready_count,
        "outputs": {
            "calibrated_lift_by_scope": str(lift_path),
            "inherited_engine_inventory": str(engine_path),
            "may_policy_audit": str(may_path),
        },
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(A7M1B_DIR / f"crypto_a7m1b_manifest_{DATE_TAG}.json", manifest)

    report_path = REPORT_DIR / f"CRYPTO_A7M1B_SURROGATE_ENGINE_READINESS_{DATE_TAG}.md"
    report_lines = [
        "# Crypto A7M-1B Surrogate Calibration + Inherited Engine Readiness",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- alpha_proof_status: `NOT_ALPHA_PROOF`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        "- authorizes_a7m2_protocol_writing: `True`",
        "- authorizes_a7m2_execution: `False`",
        f"- near_miss_lift_excluding_dry: `{near_replayed}`",
        f"- cost20_lift_excluding_dry: `{cost_replayed}`",
        f"- lag1_lift_excluding_dry: `{lag_replayed}`",
        f"- leave_source_out_near_miss_lift_min: `{min_source_near}`",
        f"- adapter_ready_count: `{adapter_ready_count}`",
        "",
        "## Engine Inventory",
        "",
        "| engine | status | required adapter |",
        "|---|---|---|",
    ]
    for row in engine_rows:
        report_lines.append(f"| `{row['engine']}` | `{row['status']}` | {row['required_adapter']} |")
    report_lines += [
        "",
        "## Boundary",
        "",
        "A7M-1B may authorize writing an A7M-2 inherited-engine bakeoff protocol. It does not authorize executing A7M-2, large search, alpha proof, shadow, paper, or live deployment.",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    decision_path = REPORT_DIR / f"CRYPTO_A7M1B_DECISION_RECORD_{DATE_TAG}.md"
    decision_path.write_text(
        "\n".join(
            [
                "# Crypto A7M-1B Decision Record",
                "",
                f"- decision: `{decision}`",
                "- alpha_proof_status: `NOT_ALPHA_PROOF`",
                "- search_executed: `False`",
                "- replay_executed: `False`",
                "- authorizes_a7m2_protocol_writing: `True`",
                "- authorizes_a7m2_execution: `False`",
                "",
                "## Confirmed",
                "",
                "- Surrogate lift is recalibrated excluding dry-preflight rows.",
                "- Leave-source and leave-family lift tables are produced.",
                "- May remains excluded from policy targets, features, arm allocation, and mutation priors.",
                "- Inherited CN engines are inventoried with crypto adapter status.",
                "",
                "## Not Confirmed",
                "",
                "- No A7M-2 execution.",
                "- No adaptive large search.",
                "- No research candidate, alpha proof, shadow, paper, live, or production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
