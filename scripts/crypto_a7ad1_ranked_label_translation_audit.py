from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ad1_ranked_label_translation_audit"
REPORT = REPO / "reports" / "CRYPTO_A7AD1_RANKED_LABEL_TRANSLATION_AUDIT_20260529.md"

A7AD0_MANIFEST = REPO / "runtime" / "a7ad0_ranked_label_translation_contract" / "a7ad0_manifest.json"
A7AC3_DECISIONS = REPO / "runtime" / "a7ac3_label_diversification_diagnostic" / "a7ac3_label_neutralization_decisions.csv"

SOURCE_LABEL = "L7_ranked_future_return"
TARGET_LABELS = ["L0_raw_forward_return", "L1_cross_sectional_relative_return"]
HOLD_DECISION = "HOLD_A7AC3_LABEL_OR_NEUTRALIZATION_BLOCKED"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 120) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def pass_row(row: pd.Series) -> bool:
    return str(row.get("decision", "")) != HOLD_DECISION


def translate_status(targets: pd.DataFrame) -> dict[str, Any]:
    translated = targets[targets["decision"].ne(HOLD_DECISION)].copy()
    if not translated.empty:
        best = translated.sort_values(["control_ratio_premay_max", "oriented_recent_spread"], ascending=[True, False]).iloc[0]
        return {
            "translation_status": "translated_to_non_ranked",
            "translated_label": best["label_family"],
            "translated_control_ratio": float(best["control_ratio_premay_max"]),
            "translated_recent_spread": float(best["oriented_recent_spread"]),
            "translated_neutralization_mode": best["neutralization_mode"],
            "translated_blockers": best["blockers"],
            "translated_warnings": best["warnings"],
        }
    positive_like = targets[
        targets["oriented_validation_spread"].astype(float).gt(0)
        & targets["oriented_test_spread"].astype(float).gt(0)
        & targets["oriented_recent_spread"].astype(float).gt(0)
    ].copy()
    if not positive_like.empty:
        best = positive_like.sort_values(["control_ratio_premay_max", "oriented_recent_spread"], ascending=[True, False]).iloc[0]
        return {
            "translation_status": "positive_but_blocked",
            "translated_label": best["label_family"],
            "translated_control_ratio": float(best["control_ratio_premay_max"]),
            "translated_recent_spread": float(best["oriented_recent_spread"]),
            "translated_neutralization_mode": best["neutralization_mode"],
            "translated_blockers": best["blockers"],
            "translated_warnings": best["warnings"],
        }
    return {
        "translation_status": "no_raw_or_relative_translation",
        "translated_label": "",
        "translated_control_ratio": np.nan,
        "translated_recent_spread": np.nan,
        "translated_neutralization_mode": "",
        "translated_blockers": "",
        "translated_warnings": "",
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ad0 = read_json(A7AD0_MANIFEST)
    if not a7ad0.get("authorizes_a7ad1_ranked_label_translation_audit"):
        raise SystemExit("A7AD-0 does not authorize A7AD-1")
    decisions = pd.read_csv(A7AC3_DECISIONS)
    source = decisions[
        decisions["label_family"].eq(SOURCE_LABEL)
        & decisions["decision"].ne(HOLD_DECISION)
    ].copy()

    rows: list[dict[str, Any]] = []
    for _, src in source.iterrows():
        same = decisions[
            decisions["candidate_id"].eq(src["candidate_id"])
            & decisions["horizon_h"].astype(int).eq(int(src["horizon_h"]))
            & decisions["neutralization_mode"].eq(src["neutralization_mode"])
            & decisions["label_family"].isin(TARGET_LABELS)
        ].copy()
        tr = translate_status(same)
        rows.append(
            {
                "candidate_id": src["candidate_id"],
                "horizon_h": int(src["horizon_h"]),
                "neutralization_mode": src["neutralization_mode"],
                "l7_recent_spread": float(src["oriented_recent_spread"]),
                "l7_control_ratio": float(src["control_ratio_premay_max"]),
                "l7_min_nonoverlap_tstat": float(src["min_oriented_nonoverlap_min_tstat"]),
                "l7_decision": src["decision"],
                "l7_warnings": src["warnings"],
                **tr,
            }
        )
    translation = pd.DataFrame(rows)
    translated = translation[translation["translation_status"].eq("translated_to_non_ranked")].copy()
    positive_blocked = translation[translation["translation_status"].eq("positive_but_blocked")].copy()
    status_summary = (
        translation.groupby(["translation_status", "neutralization_mode"], as_index=False)
        .agg(
            rows=("candidate_id", "count"),
            candidates=("candidate_id", "nunique"),
            median_l7_control_ratio=("l7_control_ratio", "median"),
            median_translated_control_ratio=("translated_control_ratio", "median"),
        )
        .sort_values(["translation_status", "rows"], ascending=[True, False])
    )
    candidate_summary = (
        translation.groupby("candidate_id", as_index=False)
        .agg(
            l7_pass_rows=("candidate_id", "count"),
            translated_rows=("translation_status", lambda x: int((x == "translated_to_non_ranked").sum())),
            positive_blocked_rows=("translation_status", lambda x: int((x == "positive_but_blocked").sum())),
            neutralization_modes=("neutralization_mode", "nunique"),
            median_l7_control_ratio=("l7_control_ratio", "median"),
        )
        .sort_values(["translated_rows", "positive_blocked_rows", "l7_pass_rows"], ascending=[False, False, False])
    )
    translated_candidates = int(translated["candidate_id"].nunique()) if not translated.empty else 0
    translated_non_global_candidates = int(
        translated.loc[translated["neutralization_mode"].ne("global_rank"), "candidate_id"].nunique()
    ) if not translated.empty else 0
    translated_rows = int(len(translated))
    if translated_candidates >= 2 and translated_non_global_candidates >= 2:
        decision = "PASS_A7AD1_RANKED_LABEL_TRANSLATION_CONFIRMED"
        authorizes_next = True
    elif translated_candidates > 0:
        decision = "HOLD_A7AD1_RANKED_LABEL_TRANSLATION_TOO_NARROW"
        authorizes_next = False
    else:
        decision = "HOLD_A7AD1_RANKED_LABEL_ARTIFACT_RISK"
        authorizes_next = False

    experiment_record = {
        "date": "2026-05-29",
        "experiment_id": "20260529_a7ad1_ranked_label_translation_audit",
        "objective": "Audit whether L7 ranked-return passes translate into raw or cross-sectional relative PnL proxy.",
        "status": "completed",
        "mode": "light_diagnostic",
        "inputs": {
            "a7ad0_manifest": str(A7AD0_MANIFEST),
            "a7ac3_decisions": str(A7AC3_DECISIONS),
        },
        "parameters": {
            "source_label": SOURCE_LABEL,
            "target_labels": TARGET_LABELS,
            "minimum_translated_candidates": 2,
            "minimum_non_global_translated_candidates": 2,
            "May_usage": "not used",
        },
        "outputs": {"runtime": str(RUNTIME), "report": str(REPORT)},
        "decision": decision,
        "next_action": "A7AE non-ranked objective redesign contract" if not authorizes_next else "A7AD-2 translated candidate forensic contract",
    }
    manifest = {
        "stage": "A7AD-1",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_label_translation_audit": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ad0_decision": a7ad0.get("decision"),
        "l7_pass_rows": int(len(source)),
        "l7_pass_candidates": int(source["candidate_id"].nunique()),
        "translation_rows": int(len(translation)),
        "translated_rows": translated_rows,
        "translated_candidates": translated_candidates,
        "translated_non_global_candidates": translated_non_global_candidates,
        "positive_but_blocked_rows": int(len(positive_blocked)),
        "authorizes_a7ad2_translated_candidate_forensic_contract": authorizes_next,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    translation.to_csv(RUNTIME / "a7ad1_l7_to_nonrank_translation_rows.csv", index=False)
    translated.to_csv(RUNTIME / "a7ad1_translated_rows.csv", index=False)
    positive_blocked.to_csv(RUNTIME / "a7ad1_positive_but_blocked_rows.csv", index=False)
    status_summary.to_csv(RUNTIME / "a7ad1_translation_status_summary.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ad1_candidate_translation_summary.csv", index=False)
    write_json(RUNTIME / "a7ad1_experiment_record.json", experiment_record)
    write_json(RUNTIME / "a7ad1_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ad1_authorization_matrix.json",
        {
            "A7AD-1": {"status": decision},
            "A7AD-2_translated_candidate_forensic_contract": {"authorized": authorizes_next},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof": {"authorized": False},
            "shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AD-1 RANKED LABEL TRANSLATION AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AD-1 audits whether A7AC ranked-return passes translate into raw or cross-sectional relative PnL proxy. It does not execute replay, train, search, or authorize alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Translation Status Summary",
        "",
        md_table(status_summary),
        "",
        "## Candidate Translation Summary",
        "",
        md_table(candidate_summary),
        "",
        "## Translated Rows",
        "",
        md_table(translated),
        "",
        "## Positive But Blocked Rows",
        "",
        md_table(positive_blocked),
        "",
        "## Experiment Record",
        "",
        "```json",
        json.dumps(experiment_record, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
