from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ah2f_downside_risk_defense_forensic_audit"
REPORT = REPO / "reports" / "CRYPTO_A7AH2F_DOWNSIDE_RISK_DEFENSE_FORENSIC_AUDIT_20260529.md"

A7AH2_MANIFEST = REPO / "runtime" / "a7ah2_downside_risk_defense_forensic_contract" / "a7ah2_manifest.json"
A7AG4_CLUES = REPO / "runtime" / "a7ag4_clue_forensic_contract" / "a7ag4_role_classified_clues.csv"
A7AG5_CONCENTRATION = REPO / "runtime" / "a7ag5_clue_forensic_audit" / "a7ag5_concentration_audit.csv"


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ah2 = read_json(A7AH2_MANIFEST)
    if not a7ah2.get("authorizes_a7ah2f_downside_forensic_audit"):
        raise SystemExit("A7AH-2 does not authorize A7AH-2F")

    clues = pd.read_csv(A7AG4_CLUES)
    concentration = pd.read_csv(A7AG5_CONCENTRATION)
    downside = clues[clues["clue_role"].eq("downside_risk_defense_clue")].copy()
    merged = downside.merge(
        concentration[["candidate_id", "top_symbol_abs_contrib_share", "top_month_abs_contrib_share", "top_raw_latent_state_id_abs_contrib_share", "concentration_blocker"]],
        on="candidate_id",
        how="left",
    )
    for col in [
        "control_ratio_premay_max",
        "cost5_recent_oriented",
        "cost10_recent_oriented",
        "cost20_recent_oriented",
        "robust_median_tstat_floor",
        "one_bar_lag_recent_oriented",
        "top_symbol_abs_contrib_share",
        "top_month_abs_contrib_share",
        "top_raw_latent_state_id_abs_contrib_share",
    ]:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")
    merged["survives_5bps_proxy"] = merged["cost5_recent_oriented"] > 0
    merged["survives_10bps_proxy"] = merged["cost10_recent_oriented"] > 0
    merged["survives_20bps_proxy"] = merged["cost20_recent_oriented"] > 0
    merged["control_margin_clean"] = merged["control_ratio_premay_max"] < 0.80
    merged["robust_positive"] = merged["robust_median_tstat_floor"] > 0
    merged["risk_defense_review_candidate"] = (
        merged["survives_10bps_proxy"]
        & merged["control_margin_clean"]
        & merged["robust_positive"]
        & ~merged["concentration_blocker"].fillna(False).astype(bool)
    )
    merged["strict_risk_defense_candidate"] = merged["risk_defense_review_candidate"] & merged["survives_20bps_proxy"]
    merged["risk_defense_tier"] = "hold"
    merged.loc[merged["risk_defense_review_candidate"], "risk_defense_tier"] = "review_candidate_10bps"
    merged.loc[merged["strict_risk_defense_candidate"], "risk_defense_tier"] = "strict_candidate_20bps"

    tier_summary = (
        merged.groupby("risk_defense_tier", dropna=False)
        .agg(
            candidates=("candidate_id", "count"),
            seed_field_count=("seed_field", "nunique"),
            interaction_field_count=("interaction_field", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost20=("cost20_recent_oriented", "median"),
            max_symbol_share=("top_symbol_abs_contrib_share", "max"),
            max_month_share=("top_month_abs_contrib_share", "max"),
        )
        .reset_index()
    )
    seed_pair_summary = (
        merged.groupby(["seed_field", "interaction_field"], dropna=False)
        .agg(
            candidates=("candidate_id", "count"),
            strict_20bps=("strict_risk_defense_candidate", "sum"),
            review_10bps=("risk_defense_review_candidate", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost20=("cost20_recent_oriented", "median"),
        )
        .reset_index()
        .sort_values(["strict_20bps", "review_10bps", "candidates"], ascending=False)
    )

    strict_count = int(merged["strict_risk_defense_candidate"].sum())
    review_count = int(merged["risk_defense_review_candidate"].sum())
    if strict_count >= 2:
        decision = "PASS_A7AH2F_DOWNSIDE_RISK_DEFENSE_STRICT_FORENSIC_CANDIDATES_FOUND"
    elif review_count >= 2:
        decision = "PASS_A7AH2F_DOWNSIDE_RISK_DEFENSE_REVIEW_CANDIDATES_FOUND"
    else:
        decision = "HOLD_A7AH2F_DOWNSIDE_RISK_DEFENSE_TOO_FRAGILE"

    manifest = {
        "stage": "A7AH-2F",
        "generated_at": now_utc(),
        "decision": decision,
        "input_a7ah2_decision": a7ah2.get("decision"),
        "executes_forensic_audit": True,
        "executes_formula_generation": False,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7ah2g_contract": decision.startswith("PASS_"),
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "input_downside_clues": int(len(merged)),
        "risk_defense_review_candidate_count": review_count,
        "strict_risk_defense_candidate_count": strict_count,
        "survives_20bps_proxy_count": int(merged["survives_20bps_proxy"].sum()),
        "control_margin_clean_count": int(merged["control_margin_clean"].sum()),
        "concentration_blocker_count": int(merged["concentration_blocker"].fillna(False).astype(bool).sum()),
    }

    merged.to_csv(RUNTIME / "a7ah2f_downside_candidate_audit.csv", index=False)
    tier_summary.to_csv(RUNTIME / "a7ah2f_tier_summary.csv", index=False)
    seed_pair_summary.to_csv(RUNTIME / "a7ah2f_seed_pair_summary.csv", index=False)
    write_json(RUNTIME / "a7ah2f_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ah2f_authorization_matrix.json",
        {
            "A7AH-2F": {"status": decision},
            "a7ah2g_contract": {"authorized": bool(manifest["authorizes_a7ah2g_contract"])},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AH-2F DOWNSIDE RISK-DEFENSE FORENSIC AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AH-2F audits A7AG downside clues under cost, control, robustness, and concentration gates. It does not promote ordinary alpha or authorize live overlay.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Tier Summary",
        "",
        md_table(tier_summary),
        "",
        "## Seed Pair Summary",
        "",
        md_table(seed_pair_summary, 80),
        "",
        "## Candidate Audit",
        "",
        md_table(merged, 80),
        "",
        "## Boundary",
        "",
        "```text",
        "A7AH-2F is forensic only.",
        "Strict risk-defense candidates are not ordinary alpha candidates.",
        "No formula search, large search, alpha proof, shadow, paper, live, or live risk overlay is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
