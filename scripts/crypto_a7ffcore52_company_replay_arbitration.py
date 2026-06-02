from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
IMPORT_RUNTIME = REPO / "runtime" / "a7ffcore51pxe_company_sharded_replay_import"
EXTERNAL_OUT = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602")
RUNTIME = REPO / "runtime" / "a7ffcore52_company_replay_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE52_COMPANY_REPLAY_ARBITRATION_20260602.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def label_family(label_key: str) -> str:
    return str(label_key).split("_")[0]


def label_horizon(label_key: str) -> str:
    return str(label_key).rsplit("_", 1)[-1]


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(IMPORT_RUNTIME / "a7ffcore51pxe_import_manifest.json")
    if source.get("decision") != "PASS_A7FFCORE51PXE_COMPANY_RESULTS_IMPORTED_READY_FOR_CORE52_ARBITRATION":
        raise SystemExit(f"CORE51PXE import is not ready for CORE52: {source.get('decision')}")
    metrics_path = EXTERNAL_OUT / "a7ffcore51pxe_aggregate_metrics.csv"
    if not metrics_path.exists():
        raise SystemExit(f"missing aggregate metrics: {metrics_path}")
    metrics = pd.read_csv(metrics_path)
    clean = metrics["decision"].eq("control_clean_positive")
    metrics["is_control_clean_positive"] = clean
    metrics["label_family"] = metrics["label_key"].map(label_family)
    metrics["label_horizon"] = metrics["label_key"].map(label_horizon)

    seed_summary = (
        metrics.groupby("seed_id", as_index=False)
        .agg(
            semantic_pair=("semantic_pair", "first"),
            operator=("operator", "first"),
            stale_risk_tier=("stale_risk_tier", "first"),
            metric_rows=("label_key", "count"),
            clean_label_count=("is_control_clean_positive", "sum"),
            min_control_ratio=("control_ratio", "min"),
            median_control_ratio=("control_ratio", "median"),
            max_original_spread=("original_spread_mean", "max"),
            median_original_spread=("original_spread_mean", "median"),
            max_original_tstat=("original_tstat", "max"),
            clean_label_families=("label_family", lambda s: int(metrics.loc[s.index, "label_family"][metrics.loc[s.index, "is_control_clean_positive"]].nunique())),
            clean_horizons=("label_horizon", lambda s: int(metrics.loc[s.index, "label_horizon"][metrics.loc[s.index, "is_control_clean_positive"]].nunique())),
        )
        .sort_values(["clean_label_count", "median_control_ratio", "max_original_spread"], ascending=[False, True, False])
    )
    seed_summary["arbitration_status"] = "rejected"
    strict_mask = (
        (seed_summary["clean_label_count"] >= 4)
        & (seed_summary["median_control_ratio"] < 0.9)
        & (seed_summary["max_original_spread"] > 0)
        & (seed_summary["clean_horizons"] >= 2)
    )
    diagnostic_mask = (
        (seed_summary["clean_label_count"] >= 2)
        & (seed_summary["min_control_ratio"] < 1.0)
        & (seed_summary["max_original_spread"] > 0)
    )
    seed_summary.loc[diagnostic_mask, "arbitration_status"] = "diagnostic_clue"
    seed_summary.loc[strict_mask, "arbitration_status"] = "strict_replay_clue"

    family_summary = (
        seed_summary.groupby(["semantic_pair", "operator"], as_index=False)
        .agg(
            seed_count=("seed_id", "count"),
            diagnostic_seed_count=("arbitration_status", lambda s: int((s == "diagnostic_clue").sum())),
            strict_seed_count=("arbitration_status", lambda s: int((s == "strict_replay_clue").sum())),
            median_clean_label_count=("clean_label_count", "median"),
            median_control_ratio=("median_control_ratio", "median"),
            max_original_spread=("max_original_spread", "max"),
        )
        .sort_values(["strict_seed_count", "diagnostic_seed_count", "median_control_ratio"], ascending=[False, False, True])
    )
    label_summary = (
        metrics.groupby("label_key", as_index=False)
        .agg(
            row_count=("seed_id", "count"),
            seed_count=("seed_id", "nunique"),
            control_clean_positive_count=("is_control_clean_positive", "sum"),
            median_control_ratio=("control_ratio", "median"),
            median_original_spread=("original_spread_mean", "median"),
        )
        .sort_values("label_key")
    )

    strict_count = int(seed_summary["arbitration_status"].eq("strict_replay_clue").sum())
    diagnostic_count = int(seed_summary["arbitration_status"].isin(["strict_replay_clue", "diagnostic_clue"]).sum())
    strict_family_count = int(seed_summary.loc[seed_summary["arbitration_status"].eq("strict_replay_clue"), "semantic_pair"].nunique())
    decision = (
        "PASS_A7FFCORE52_REPLAY_CLUE_POOL_READY_FOR_CORE53_DEEP_AUDIT_CONTRACT"
        if strict_count >= 4 and strict_family_count >= 3
        else "HOLD_A7FFCORE52_DIAGNOSTIC_CLUES_INSUFFICIENT_FOR_SEARCH"
        if diagnostic_count > 0
        else "HOLD_A7FFCORE52_NO_REPLAY_CLUES"
    )

    seed_summary.to_csv(RUNTIME / "a7ffcore52_seed_arbitration.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore52_family_operator_arbitration.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ffcore52_label_arbitration.csv", index=False)
    top_clues = seed_summary.loc[seed_summary["arbitration_status"].isin(["strict_replay_clue", "diagnostic_clue"])].head(80)
    top_clues.to_csv(RUNTIME / "a7ffcore52_top_diagnostic_clues.csv", index=False)
    authorization = {
        "authorized": {
            "A7FF-CORE52F diagnostic clue forensic": diagnostic_count > 0,
            "A7FF-CORE53 deep audit contract": decision.startswith("PASS_"),
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    manifest = {
        "stage": "A7FF-CORE52",
        "generated_at": now_utc(),
        "source_stage": source.get("stage"),
        "source_decision": source.get("decision"),
        "decision": decision,
        "metric_rows": int(metrics.shape[0]),
        "seed_count": int(seed_summary.shape[0]),
        "diagnostic_clue_count": diagnostic_count,
        "strict_replay_clue_count": strict_count,
        "strict_replay_clue_semantic_pair_count": strict_family_count,
        "label_count": int(metrics["label_key"].nunique()),
        "semantic_pair_count": int(metrics["semantic_pair"].nunique()),
        "operator_count": int(metrics["operator"].nunique()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_core52f_forensic": diagnostic_count > 0,
        "authorizes_core53_deep_audit_contract": decision.startswith("PASS_"),
    }
    write_json(RUNTIME / "a7ffcore52_manifest.json", manifest)
    write_json(RUNTIME / "a7ffcore52_authorization_matrix.json", authorization)

    lines = [
        "# CRYPTO A7FF-CORE52 COMPANY REPLAY ARBITRATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE52 arbitrates the imported CORE51PXE company-sharded replay. It does not execute replay, generation, search, proof, or promotion.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Arbitration",
        "",
        md_table(label_summary),
        "",
        "## Top Diagnostic Clues",
        "",
        md_table(top_clues[["seed_id", "arbitration_status", "semantic_pair", "operator", "clean_label_count", "clean_horizons", "min_control_ratio", "median_control_ratio", "max_original_spread"]], 40),
        "",
        "## Family Arbitration",
        "",
        md_table(family_summary, 80),
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
