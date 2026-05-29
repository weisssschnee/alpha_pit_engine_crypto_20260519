from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ah1d_ordinary_alpha_dry_rerank"
REPORT = REPO / "reports" / "CRYPTO_A7AH1D_ORDINARY_ALPHA_DRY_RERANK_20260529.md"

A7AH1_MANIFEST = REPO / "runtime" / "a7ah1_ordinary_alpha_objective_rewrite_contract" / "a7ah1_manifest.json"
A7AG3_METRICS = REPO / "runtime" / "a7ag3_numeric_replay_pilot" / "a7ag3_candidate_replay_metrics.csv"

ORDINARY_LABELS = {"L0_raw_forward_return", "L1_cross_sectional_relative_return"}


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


def bool_series(frame: pd.DataFrame, column: str) -> pd.Series:
    return frame.get(column, pd.Series(False, index=frame.index)).fillna(False).astype(bool)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ah1 = read_json(A7AH1_MANIFEST)
    if not a7ah1.get("authorizes_a7ah1d_dry_rerank"):
        raise SystemExit("A7AH-1 does not authorize A7AH-1D")

    metrics = pd.read_csv(A7AG3_METRICS)
    ordinary = metrics[metrics["label_family"].isin(ORDINARY_LABELS)].copy()
    for col in [
        "premay_all_positive",
        "control_clean",
        "lag_ok",
        "robust_ok",
        "cost_proxy_ok",
        "activity_ok",
        "eval_success",
    ]:
        ordinary[col] = bool_series(ordinary, col)
    ordinary["ordinary_hard_gate_pass"] = (
        ordinary["eval_success"]
        & ordinary["activity_ok"]
        & ordinary["premay_all_positive"]
        & ordinary["control_clean"]
        & ordinary["lag_ok"]
        & ordinary["robust_ok"]
        & ordinary["cost_proxy_ok"]
    )
    numeric_cols = [
        "control_ratio_premay_max",
        "cost5_recent_oriented",
        "cost10_recent_oriented",
        "cost20_recent_oriented",
        "robust_median_tstat_floor",
        "one_bar_lag_recent_oriented",
    ]
    for col in numeric_cols:
        ordinary[col] = pd.to_numeric(ordinary.get(col, np.nan), errors="coerce")
    ordinary["selector_score"] = (
        ordinary["premay_all_positive"].astype(float)
        + ordinary["control_clean"].astype(float)
        + ordinary["lag_ok"].astype(float)
        + ordinary["robust_ok"].astype(float)
        + ordinary["cost_proxy_ok"].astype(float)
        + ordinary["robust_median_tstat_floor"].clip(lower=-5, upper=5).fillna(-5) / 5.0
        - ordinary["control_ratio_premay_max"].fillna(10).clip(lower=0, upper=10) / 10.0
    )
    ordinary["ordinary_reject_reason"] = "pass"
    ordinary.loc[~ordinary["premay_all_positive"], "ordinary_reject_reason"] = "pre_may_unstable"
    ordinary.loc[ordinary["premay_all_positive"] & ~ordinary["control_clean"], "ordinary_reject_reason"] = "control_dominated"
    ordinary.loc[
        ordinary["premay_all_positive"] & ordinary["control_clean"] & ~ordinary["lag_ok"],
        "ordinary_reject_reason",
    ] = "one_bar_lag_fragile"
    ordinary.loc[
        ordinary["premay_all_positive"] & ordinary["control_clean"] & ordinary["lag_ok"] & ~ordinary["robust_ok"],
        "ordinary_reject_reason",
    ] = "nonoverlap_weak"
    ordinary.loc[
        ordinary["premay_all_positive"]
        & ordinary["control_clean"]
        & ordinary["lag_ok"]
        & ordinary["robust_ok"]
        & ~ordinary["cost_proxy_ok"],
        "ordinary_reject_reason",
    ] = "cost5_proxy_fragile"

    rerank = ordinary.sort_values(["ordinary_hard_gate_pass", "selector_score"], ascending=False).copy()
    selected = rerank[rerank["ordinary_hard_gate_pass"]].copy()
    reject_summary = ordinary["ordinary_reject_reason"].value_counts().rename_axis("reject_reason").reset_index(name="count")
    label_summary = (
        ordinary.groupby("label_family", dropna=False)
        .agg(
            candidates=("candidate_id", "count"),
            hard_gate_pass=("ordinary_hard_gate_pass", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_selector_score=("selector_score", "median"),
        )
        .reset_index()
    )

    decision = (
        "PASS_A7AH1D_ORDINARY_ALPHA_DRY_RERANK_CANDIDATES_FOUND"
        if len(selected) >= 2
        else "HOLD_A7AH1D_NO_ORDINARY_ALPHA_DRY_RERANK_CANDIDATES"
    )
    manifest = {
        "stage": "A7AH-1D",
        "generated_at": now_utc(),
        "decision": decision,
        "input_a7ah1_decision": a7ah1.get("decision"),
        "executes_dry_rerank": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7ah1e_contract": decision.startswith("PASS_"),
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "ordinary_candidate_count": int(len(ordinary)),
        "ordinary_hard_gate_pass_count": int(len(selected)),
        "label_families": sorted(ordinary["label_family"].dropna().astype(str).unique().tolist()),
    }

    rerank.to_csv(RUNTIME / "a7ah1d_ordinary_alpha_rerank_queue.csv", index=False)
    selected.to_csv(RUNTIME / "a7ah1d_ordinary_alpha_selected.csv", index=False)
    reject_summary.to_csv(RUNTIME / "a7ah1d_reject_reason_summary.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ah1d_label_summary.csv", index=False)
    write_json(RUNTIME / "a7ah1d_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ah1d_authorization_matrix.json",
        {
            "A7AH-1D": {"status": decision},
            "a7ah1e_contract": {"authorized": bool(manifest["authorizes_a7ah1e_contract"])},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AH-1D ORDINARY ALPHA DRY RERANK",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AH-1D reranks existing A7AG candidates under the ordinary-alpha L0/L1 policy. It does not generate formulas, replay, search, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Summary",
        "",
        md_table(label_summary),
        "",
        "## Reject Reason Summary",
        "",
        md_table(reject_summary),
        "",
        "## Selected Ordinary Alpha Candidates",
        "",
        md_table(selected, 80),
        "",
        "## Top Rerank Queue",
        "",
        md_table(rerank.head(40), 40),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AH-1D is a dry rerank on existing metrics only.",
        "If no L0/L1 hard-gate candidates pass, ordinary alpha formula search remains blocked.",
        "No formula search, large search, alpha proof, shadow, paper, or live is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
