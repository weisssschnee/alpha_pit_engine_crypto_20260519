from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE52 = REPO / "runtime" / "a7ffcore52_company_replay_arbitration"
EXTERNAL_OUT = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602")
RUNTIME = REPO / "runtime" / "a7ffcore52f_diagnostic_clue_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE52F_DIAGNOSTIC_CLUE_FORENSIC_20260602.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 50) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core52 = read_json(CORE52 / "a7ffcore52_manifest.json")
    if not core52.get("authorizes_core52f_forensic"):
        raise SystemExit(f"CORE52F not authorized by CORE52: {core52.get('decision')}")
    metrics = pd.read_csv(EXTERNAL_OUT / "a7ffcore51pxe_aggregate_metrics.csv")
    seed = pd.read_csv(CORE52 / "a7ffcore52_seed_arbitration.csv")
    clue = seed.loc[seed["arbitration_status"].isin(["strict_replay_clue", "diagnostic_clue"])].copy()
    clue["control_margin"] = 1.0 - clue["median_control_ratio"]
    clue["thin_control_margin"] = clue["median_control_ratio"] >= 0.95
    clue["single_horizon_evidence"] = clue["clean_horizons"] <= 1
    clue["strict_ready"] = clue["arbitration_status"].eq("strict_replay_clue")

    redundancy_rows = []
    value_cols = [
        "original_spread_mean",
        "original_tstat",
        "control_ratio",
        "stale_spread_mean",
        "time_shuffle_spread_mean",
        "symbol_shuffle_spread_mean",
        "sign_flip_spread_mean",
    ]
    for horizon in ["1h", "4h", "8h", "24h"]:
        raw = metrics.loc[metrics["label_key"].eq(f"L0_raw_{horizon}")].set_index("seed_id")
        xs = metrics.loc[metrics["label_key"].eq(f"L1_xs_{horizon}")].set_index("seed_id")
        common = raw.index.intersection(xs.index)
        row = {"horizon": horizon, "common_seed_count": int(len(common))}
        for col in value_cols:
            diff = (raw.loc[common, col] - xs.loc[common, col]).abs()
            row[f"max_abs_diff_{col}"] = float(diff.max()) if len(diff) else np.nan
            row[f"median_abs_diff_{col}"] = float(diff.median()) if len(diff) else np.nan
        spread_diff_cols = [
            "max_abs_diff_original_spread_mean",
            "max_abs_diff_stale_spread_mean",
            "max_abs_diff_time_shuffle_spread_mean",
            "max_abs_diff_symbol_shuffle_spread_mean",
            "max_abs_diff_sign_flip_spread_mean",
        ]
        row["is_redundant_for_decile_spread"] = bool(
            max(float(row[col]) for col in spread_diff_cols) < 1e-9
            and float(row["median_abs_diff_control_ratio"]) < 1e-6
        )
        redundancy_rows.append(row)
    redundancy = pd.DataFrame(redundancy_rows)

    family_forensic = (
        clue.groupby(["semantic_pair", "operator"], as_index=False)
        .agg(
            clue_count=("seed_id", "count"),
            strict_count=("strict_ready", "sum"),
            thin_control_margin_count=("thin_control_margin", "sum"),
            median_control_margin=("control_margin", "median"),
            median_clean_horizons=("clean_horizons", "median"),
            max_original_spread=("max_original_spread", "max"),
            max_original_tstat=("max_original_tstat", "max"),
        )
        .sort_values(["strict_count", "clue_count", "median_control_margin"], ascending=[False, False, False])
    )
    failure_rows = []
    for _, row in clue.iterrows():
        reasons = []
        if row["thin_control_margin"]:
            reasons.append("thin_control_margin")
        if row["single_horizon_evidence"]:
            reasons.append("single_horizon_evidence")
        if row["median_control_ratio"] >= 1.0:
            reasons.append("median_control_dominated")
        if row["arbitration_status"] != "strict_replay_clue":
            reasons.append("not_strict_replay_clue")
        failure_rows.append(
            {
                "seed_id": row["seed_id"],
                "semantic_pair": row["semantic_pair"],
                "operator": row["operator"],
                "arbitration_status": row["arbitration_status"],
                "clean_label_count": row["clean_label_count"],
                "clean_horizons": row["clean_horizons"],
                "median_control_ratio": row["median_control_ratio"],
                "control_margin": row["control_margin"],
                "failure_reasons": ";".join(reasons) if reasons else "strict_but_insufficient_family_breadth",
            }
        )
    failure = pd.DataFrame(failure_rows)

    redundant_horizons = int(redundancy["is_redundant_for_decile_spread"].sum())
    thin_margin_count = int(clue["thin_control_margin"].sum())
    single_horizon_count = int(clue["single_horizon_evidence"].sum())
    strict_count = int(clue["strict_ready"].sum())
    decision = "HOLD_A7FFCORE52F_LABEL_REDUNDANCY_AND_THIN_CONTROL_MARGIN"
    manifest = {
        "stage": "A7FF-CORE52F",
        "generated_at": now_utc(),
        "source_stage": core52.get("stage"),
        "source_decision": core52.get("decision"),
        "decision": decision,
        "diagnostic_clue_count": int(clue.shape[0]),
        "strict_replay_clue_count": strict_count,
        "redundant_l0_l1_horizon_count": redundant_horizons,
        "thin_control_margin_clue_count": thin_margin_count,
        "single_horizon_clue_count": single_horizon_count,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core53_replay_target_repair_contract": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    authorization = {
        "authorized": {
            "A7FF-CORE53 replay target repair contract": True,
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "deep_audit": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    redundancy.to_csv(RUNTIME / "a7ffcore52f_label_redundancy_audit.csv", index=False)
    clue.to_csv(RUNTIME / "a7ffcore52f_control_margin_audit.csv", index=False)
    family_forensic.to_csv(RUNTIME / "a7ffcore52f_family_forensic.csv", index=False)
    failure.to_csv(RUNTIME / "a7ffcore52f_failure_attribution.csv", index=False)
    write_json(RUNTIME / "a7ffcore52f_manifest.json", manifest)
    write_json(RUNTIME / "a7ffcore52f_authorization_matrix.json", authorization)
    repair_contract = {
        "required_repairs": [
            "do_not_count_L0_raw_and_L1_xs_as_independent_for_top_bottom_spread",
            "add_non_redundant_label_targets_before_next_replay_wave",
            "require_control_margin_not_just_control_ratio_below_one",
            "separate_diagnostic_clues_from_strict_replay_clues",
            "do_not_expand_formula_search_from_current_35_diagnostic_clues",
        ],
        "suggested_label_targets": [
            "BTC_ETH_beta_residual_return",
            "liquidity_tier_relative_return",
            "latent_state_relative_return",
            "vol_adjusted_return",
            "ranked_future_return_diagnostic_only",
            "portfolio_top_bottom_net_spread_proxy",
        ],
    }
    write_json(RUNTIME / "a7ffcore52f_replay_target_repair_requirements.json", repair_contract)
    lines = [
        "# CRYPTO A7FF-CORE52F DIAGNOSTIC CLUE FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE52F explains why CORE52 diagnostic clues are insufficient for search. It does not execute replay, generation, proof, or promotion.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Redundancy",
        "",
        md_table(redundancy),
        "",
        "## Control Margin Forensic",
        "",
        md_table(clue[["seed_id", "arbitration_status", "semantic_pair", "operator", "clean_label_count", "clean_horizons", "median_control_ratio", "control_margin", "thin_control_margin"]], 50),
        "",
        "## Family Forensic",
        "",
        md_table(family_forensic, 80),
        "",
        "## Replay Target Repair Requirements",
        "",
        "```json",
        json.dumps(repair_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
