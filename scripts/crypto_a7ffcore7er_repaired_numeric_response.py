from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore7er_repaired_numeric_response"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE7ER_REPAIRED_NUMERIC_RESPONSE_20260601.md"
A7FFCORE7R = REPO / "runtime" / "a7ffcore7r_control_policy_forensic" / "a7ffcore7r_manifest.json"
REPAIRED_ROWS = REPO / "runtime" / "a7ffcore7r_control_policy_forensic" / "a7ffcore7r_repaired_response_rows.csv"


PRIMARY_LABELS = {
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
}


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core7r = read_json(A7FFCORE7R)
    if core7r.get("decision") != "PASS_A7FFCORE7R_CONTROL_POLICY_REPAIR_REQUIRED_READY_FOR_CORE7ER":
        raise SystemExit(f"A7FF-CORE7R is not ready: {core7r.get('decision')}")

    df = pd.read_csv(REPAIRED_ROWS)
    df["max_control_score"] = df["non_sign_max_control_score"]
    df["control_ratio"] = df["non_sign_control_ratio"]
    df["numeric_clue"] = df["repaired_numeric_clue"]
    df["sign_flip_diagnostic_ratio"] = df["sign_flip_ratio"]
    df["sign_flip_in_max_control_policy"] = "diagnostic_only_excluded_from_abs_max_control"
    clue_df = df[df["numeric_clue"].astype(bool)].copy()

    label_summary = (
        df.groupby(["label_id", "horizon"], dropna=False)
        .agg(
            rows=("candidate_id", "size"),
            numeric_clues=("numeric_clue", "sum"),
            candidate_count=("candidate_id", "nunique"),
            median_abs_corr=("corr", lambda s: float(pd.to_numeric(s, errors="coerce").abs().median())),
            median_control_ratio=("control_ratio", "median"),
            median_sign_flip_diagnostic_ratio=("sign_flip_diagnostic_ratio", "median"),
        )
        .reset_index()
        .sort_values(["numeric_clues", "median_control_ratio"], ascending=[False, True])
    )
    family_summary = (
        df.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            rows=("candidate_id", "size"),
            candidate_count=("candidate_id", "nunique"),
            numeric_clues=("numeric_clue", "sum"),
            median_control_ratio=("control_ratio", "median"),
            median_sign_flip_diagnostic_ratio=("sign_flip_diagnostic_ratio", "median"),
        )
        .reset_index()
        .sort_values(["numeric_clues", "median_control_ratio"], ascending=[False, True])
    )
    selected_queue = (
        clue_df.groupby(["candidate_id", "semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            clue_rows=("candidate_id", "size"),
            label_count=("label_id", "nunique"),
            horizon_count=("horizon", "nunique"),
            best_abs_corr=("corr", lambda s: float(pd.to_numeric(s, errors="coerce").abs().max())),
            best_original_score=("original_score", "max"),
            min_control_ratio=("control_ratio", "min"),
        )
        .reset_index()
        .sort_values(["clue_rows", "label_count", "min_control_ratio"], ascending=[False, False, True])
    )

    df.to_csv(RUNTIME / "a7ffcore7er_response_rows.csv", index=False)
    clue_df.to_csv(RUNTIME / "a7ffcore7er_numeric_clues.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ffcore7er_label_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore7er_family_summary.csv", index=False)
    selected_queue.to_csv(RUNTIME / "a7ffcore7er_candidate_queue.csv", index=False)

    clue_rows = int(clue_df.shape[0])
    candidate_count = int(clue_df["candidate_id"].nunique())
    primary_clue_rows = int(clue_df["label_id"].isin(PRIMARY_LABELS).sum())
    decision = (
        "PASS_A7FFCORE7ER_REPAIRED_NUMERIC_RESPONSE_READY_FOR_CORE8"
        if primary_clue_rows > 0 and candidate_count > 0
        else "HOLD_A7FFCORE7ER_NO_REPAIRED_PRIMARY_CLUES"
    )
    manifest = {
        "stage": "A7FF-CORE7ER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE7R",
        "source_decision": core7r.get("decision"),
        "decision": decision,
        "response_rows": int(df.shape[0]),
        "numeric_clue_rows": clue_rows,
        "primary_non_l7_clue_rows": primary_clue_rows,
        "numeric_clue_candidate_count": candidate_count,
        "label_family_count_with_clues": int(clue_df["label_id"].nunique()) if clue_rows else 0,
        "semantic_bucket_count_with_clues": int(clue_df["semantic_bucket"].nunique()) if clue_rows else 0,
        "sign_flip_policy": "diagnostic_only_excluded_from_abs_max_control",
        "executes_numeric_reclassification": True,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core8_contract": decision.startswith("PASS_"),
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE8 numeric clue consolidation / replay-preflight contract"
        if decision.startswith("PASS_")
        else "A7FF-CORE7R continuation",
    }
    write_json(RUNTIME / "a7ffcore7er_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE7ER REPAIRED NUMERIC RESPONSE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE7ER is a reclassification of CORE7E response rows under the CORE7R repaired control policy. It does not run portfolio replay, search, promotion, alpha proof, shadow, paper, or live.",
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
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Candidate Queue Preview",
        "",
        md_table(selected_queue, max_rows=60),
        "",
        "## Boundary",
        "",
        "```text",
        "numeric response reclassified: true",
        "portfolio replay: false",
        "search: false",
        "promotion: false",
        "sign_flip: diagnostic-only, excluded from absolute max-control dominance",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
