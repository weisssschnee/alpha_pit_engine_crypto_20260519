from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ab9_survivor_freeze_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AB9_SURVIVOR_FREEZE_CONTRACT_20260529.md"

A7AB8_MANIFEST = REPO / "runtime" / "a7ab8_clue_forensic_execution" / "a7ab8_manifest.json"
A7AB8_SURVIVORS = REPO / "runtime" / "a7ab8_clue_forensic_execution" / "a7ab8_forensic_survivors.csv"
A7AB8_CLUSTER_SUMMARY = REPO / "runtime" / "a7ab8_clue_forensic_execution" / "a7ab8_return_corr_cluster_summary.csv"


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


def representative_pool(survivors: pd.DataFrame) -> pd.DataFrame:
    ranked = survivors.copy()
    ranked["representative_score"] = (
        ranked["oriented_recent_spread"].astype(float)
        + ranked["oriented_test_spread"].astype(float)
        + ranked["oriented_validation_spread"].astype(float)
        - ranked["control_ratio_premay_max"].astype(float) * 0.01
        - ranked["turnover_proxy"].astype(float) * 0.001
    )
    ranked = ranked.sort_values(
        ["return_corr_cluster", "representative_score", "control_ratio_premay_max"],
        ascending=[True, False, True],
    )
    rows: list[dict[str, Any]] = []
    for _, group in ranked.groupby("return_corr_cluster", sort=True):
        rows.append(group.iloc[0].to_dict())
    reps = pd.DataFrame(rows).sort_values("representative_score", ascending=False).reset_index(drop=True)
    reps.insert(0, "representative_rank", range(1, len(reps) + 1))
    return reps


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ab8 = read_json(A7AB8_MANIFEST)
    if not a7ab8.get("authorizes_a7ab9_survivor_freeze_contract"):
        raise SystemExit("A7AB-8 does not authorize A7AB-9")
    survivors = pd.read_csv(A7AB8_SURVIVORS)
    clusters = pd.read_csv(A7AB8_CLUSTER_SUMMARY)
    reps = representative_pool(survivors)

    survivor_rows = int(len(survivors))
    top_cluster_share = float(
        survivors["return_corr_cluster"].value_counts(normalize=True).iloc[0]
    ) if survivor_rows else 0.0
    top_label_share = float(
        survivors["label_family"].value_counts(normalize=True).iloc[0]
    ) if survivor_rows else 0.0
    label_audit = (
        survivors.groupby(["label_family", "horizon_h"], as_index=False)
        .agg(
            survivor_rows=("candidate_id", "count"),
            survivor_candidates=("candidate_id", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_recent_spread=("oriented_recent_spread", "median"),
        )
        .sort_values("survivor_rows", ascending=False)
    )
    cluster_audit = (
        survivors.groupby("return_corr_cluster", as_index=False)
        .agg(
            survivor_rows=("candidate_id", "count"),
            survivor_candidates=("candidate_id", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_recent_spread=("oriented_recent_spread", "median"),
        )
        .sort_values("survivor_rows", ascending=False)
    )
    warnings = []
    if top_cluster_share > 0.35:
        warnings.append("top_return_corr_cluster_share_gt_35pct")
    if top_label_share >= 0.80:
        warnings.append("single_label_family_dominates")
    decision = "PASS_A7AB9_SURVIVOR_FREEZE_REPRESENTATIVE_POOL_WITH_WARNINGS" if warnings else "PASS_A7AB9_SURVIVOR_FREEZE_REPRESENTATIVE_POOL"
    manifest = {
        "stage": "A7AB-9",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ab8_decision": a7ab8.get("decision"),
        "survivor_rows": survivor_rows,
        "survivor_candidates": int(survivors["candidate_id"].nunique()),
        "survivor_clusters": int(survivors["return_corr_cluster"].nunique()),
        "representative_rows": int(len(reps)),
        "top_cluster_share": top_cluster_share,
        "top_label_share": top_label_share,
        "warnings": warnings,
        "authorizes_a7ac0_representative_forensic_contract": True,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    survivors.to_csv(RUNTIME / "a7ab9_survivor_pool.csv", index=False)
    reps.to_csv(RUNTIME / "a7ab9_representative_survivor_pool.csv", index=False)
    clusters.to_csv(RUNTIME / "a7ab9_input_cluster_summary.csv", index=False)
    cluster_audit.to_csv(RUNTIME / "a7ab9_survivor_cluster_audit.csv", index=False)
    label_audit.to_csv(RUNTIME / "a7ab9_survivor_label_audit.csv", index=False)
    write_json(RUNTIME / "a7ab9_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ab9_authorization_matrix.json",
        {
            "A7AB-9": {"status": decision},
            "A7AC-0_representative_forensic_contract": {"authorized": True},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AB-9 SURVIVOR FREEZE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-9 freezes A7AB-8 forensic survivors into a representative pool. It does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Survivor Label Audit",
        "",
        md_table(label_audit),
        "",
        "## Survivor Cluster Audit",
        "",
        md_table(cluster_audit),
        "",
        "## Representative Survivor Pool",
        "",
        md_table(reps, 80),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
