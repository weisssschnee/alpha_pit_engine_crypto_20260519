from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore7r_control_policy_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE7R_CONTROL_POLICY_FORENSIC_20260601.md"
A7FFCORE7E = REPO / "runtime" / "a7ffcore7e_numeric_response" / "a7ffcore7e_manifest.json"
RESPONSE = REPO / "runtime" / "a7ffcore7e_numeric_response" / "a7ffcore7e_response_rows.csv"

PRIMARY_LABELS = {
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
}
NON_SIGN_CONTROLS = [
    "time_shuffle",
    "symbol_shuffle",
    "same_family_placebo",
    "wrong_lag_future",
    "wrong_lag_stale",
]
SIGN_FLIP = "sign_flip"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
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


def control_score(df: pd.DataFrame, control: str) -> pd.Series:
    return df[[f"{control}_corr", f"{control}_spread"]].abs().max(axis=1)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core7e = read_json(A7FFCORE7E)
    if core7e.get("decision") != "HOLD_A7FFCORE7E_NUMERIC_RESPONSE_WEAK":
        raise SystemExit(f"A7FF-CORE7E is not in expected HOLD state: {core7e.get('decision')}")

    df = pd.read_csv(RESPONSE)
    df = df[df["label_id"].ne("EVAL_ERROR")].copy()
    original = pd.to_numeric(df["original_score"], errors="coerce").replace(0.0, np.nan)
    for control in NON_SIGN_CONTROLS + [SIGN_FLIP]:
        df[f"{control}_score"] = control_score(df, control)
        df[f"{control}_ratio"] = df[f"{control}_score"] / original
    df["non_sign_max_control_score"] = df[[f"{c}_score" for c in NON_SIGN_CONTROLS]].max(axis=1)
    df["non_sign_control_ratio"] = df["non_sign_max_control_score"] / original
    df["sign_flip_tautology"] = np.isclose(df["sign_flip_ratio"], 1.0, rtol=1e-9, atol=1e-9)
    df["repaired_numeric_clue"] = (
        df["label_id"].isin(PRIMARY_LABELS)
        & pd.to_numeric(df["corr"], errors="coerce").abs().ge(0.001)
        & df["non_sign_control_ratio"].lt(0.8)
    )
    df["original_policy_blocked_by_sign_flip"] = (
        df["repaired_numeric_clue"]
        & pd.to_numeric(df["control_ratio"], errors="coerce").ge(0.8)
        & df["sign_flip_tautology"]
    )

    clue_df = df[df["repaired_numeric_clue"]].copy()
    label_summary = (
        df.groupby(["label_id", "horizon"], dropna=False)
        .agg(
            rows=("candidate_id", "size"),
            repaired_numeric_clues=("repaired_numeric_clue", "sum"),
            original_numeric_clues=("numeric_clue", "sum"),
            median_original_control_ratio=("control_ratio", "median"),
            median_non_sign_control_ratio=("non_sign_control_ratio", "median"),
            median_sign_flip_ratio=("sign_flip_ratio", "median"),
        )
        .reset_index()
        .sort_values(["repaired_numeric_clues", "median_non_sign_control_ratio"], ascending=[False, True])
    )
    family_summary = (
        df.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            rows=("candidate_id", "size"),
            candidate_count=("candidate_id", "nunique"),
            repaired_numeric_clues=("repaired_numeric_clue", "sum"),
            original_numeric_clues=("numeric_clue", "sum"),
            median_non_sign_control_ratio=("non_sign_control_ratio", "median"),
            median_sign_flip_ratio=("sign_flip_ratio", "median"),
        )
        .reset_index()
        .sort_values(["repaired_numeric_clues", "median_non_sign_control_ratio"], ascending=[False, True])
    )
    candidate_summary = (
        clue_df.groupby(["candidate_id", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            clue_rows=("candidate_id", "size"),
            best_abs_corr=("corr", lambda s: float(np.nanmax(np.abs(pd.to_numeric(s, errors="coerce"))))),
            best_original_score=("original_score", "max"),
            min_non_sign_control_ratio=("non_sign_control_ratio", "min"),
        )
        .reset_index()
        .sort_values(["clue_rows", "min_non_sign_control_ratio"], ascending=[False, True])
    )
    control_summary = pd.DataFrame(
        [
            {
                "control": control,
                "median_ratio": float(df[f"{control}_ratio"].median()),
                "p90_ratio": float(df[f"{control}_ratio"].quantile(0.90)),
                "ratio_ge_1_share": float(df[f"{control}_ratio"].ge(1.0).mean()),
            }
            for control in NON_SIGN_CONTROLS + [SIGN_FLIP]
        ]
    )

    df.to_csv(RUNTIME / "a7ffcore7r_repaired_response_rows.csv", index=False)
    clue_df.to_csv(RUNTIME / "a7ffcore7r_repaired_numeric_clues.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ffcore7r_label_summary_repaired.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore7r_family_summary_repaired.csv", index=False)
    candidate_summary.to_csv(RUNTIME / "a7ffcore7r_candidate_summary.csv", index=False)
    control_summary.to_csv(RUNTIME / "a7ffcore7r_control_summary.csv", index=False)

    repaired_clues = int(df["repaired_numeric_clue"].sum())
    repaired_candidates = int(clue_df["candidate_id"].nunique())
    sign_tautology_share = float(df["sign_flip_tautology"].mean())
    decision = (
        "PASS_A7FFCORE7R_CONTROL_POLICY_REPAIR_REQUIRED_READY_FOR_CORE7ER"
        if repaired_clues > 0 and sign_tautology_share >= 0.999
        else "HOLD_A7FFCORE7R_NO_REPAIRED_NUMERIC_CLUES"
    )
    manifest = {
        "stage": "A7FF-CORE7R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE7E",
        "source_decision": core7e.get("decision"),
        "decision": decision,
        "response_rows": int(len(df)),
        "source_numeric_clue_rows": int(pd.to_numeric(df["numeric_clue"], errors="coerce").fillna(False).astype(bool).sum()),
        "repaired_numeric_clue_rows": repaired_clues,
        "repaired_candidate_count": repaired_candidates,
        "primary_non_l7_repaired_clue_rows": int(clue_df["label_id"].isin(PRIMARY_LABELS).sum()),
        "sign_flip_tautology_share": sign_tautology_share,
        "non_sign_controls": NON_SIGN_CONTROLS,
        "sign_flip_policy": "diagnostic_only_not_allowed_in_abs_max_control_score",
        "executes_search": False,
        "executes_replay": False,
        "authorizes_core7er": decision.startswith("PASS_"),
        "authorizes_core8": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE7ER repaired numeric-response rerun with sign_flip diagnostic-only policy"
        if decision.startswith("PASS_")
        else "A7FF-CORE7R label/control forensic continuation",
    }
    write_json(RUNTIME / "a7ffcore7r_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE7R CONTROL POLICY FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE7R does not run search, replay, promotion, alpha proof, shadow, paper, or live. It audits whether CORE7E's control policy mechanically blocked all numeric clues.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Control Summary",
        "",
        md_table(control_summary),
        "",
        "## Repaired Label Summary",
        "",
        md_table(label_summary),
        "",
        "## Repaired Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Top Repaired Candidate Summary",
        "",
        md_table(candidate_summary, max_rows=40),
        "",
        "## Boundary",
        "",
        "```text",
        "sign_flip is retained only as an orientation diagnostic.",
        "sign_flip is not eligible for absolute max-control dominance because abs(score(sign_flip)) is mechanically equal to abs(score(original)).",
        "This stage only authorizes a repaired numeric-response rerun; it does not authorize replay/search/promotion.",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
