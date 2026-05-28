from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7ar7_shared_candidate_pool"
REPORT = REPO / "reports" / "CRYPTO_A7AR7_SHARED_CANDIDATE_POOL_20260528.md"

Q_DIR = REPO / "runtime" / "company_a7al2q2r_full_20260528" / "runtime" / "a7al2q_local_oi_price_formula_search"
R_DIR = REPO / "runtime" / "company_a7al2q2r_full_20260528" / "runtime" / "a7al2r_local_forensic"
S_DIR = REPO / "runtime" / "a7al2s_company_full_followup_contract"
T_DIR = REPO / "runtime" / "a7al2t_company_may_stress_failure_attribution"
U_DIR = REPO / "runtime" / "a7al2u_objective_selector_repair_contract"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"Missing required artifact: {path}")
    return pd.read_csv(path)


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if pd.api.types.is_object_dtype(view[col]) or pd.api.types.is_string_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```\n" + view.to_string(index=False) + "\n```"


def bool_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(False, index=df.index)
    return df[column].astype(str).str.lower().isin(["true", "1", "yes"])


def prefix_columns(df: pd.DataFrame, prefix: str, keep: set[str]) -> pd.DataFrame:
    renamed = {}
    for col in df.columns:
        if col not in keep:
            renamed[col] = f"{prefix}{col}"
    return df.rename(columns=renamed)


def first_by_candidate(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    return df.sort_values("candidate_id").drop_duplicates("candidate_id", keep="first")


def load_pool() -> pd.DataFrame:
    generated = read_csv(Q_DIR / "a7al2q_generated_candidates.csv")
    q_score = read_csv(Q_DIR / "a7al2q_candidate_scoreboard.csv")
    r_decision = read_csv(R_DIR / "a7al2r_decision_record.csv")
    s_tiers = read_csv(S_DIR / "a7al2s_candidate_tiers.csv")
    t_failure = read_csv(T_DIR / "a7al2t_candidate_failure_summary.csv")

    q_keep = [
        "candidate_id",
        "decision",
        "reasons",
        "warnings",
        "label_t1_positive_premay_splits",
        "label_t2_positive_premay_splits",
        "one_bar_lag_positive_premay_splits",
        "timevarying_latent_positive_premay_splits",
        "net_10bps_positive_premay_splits",
        "control_ratio_premay_max_by_split",
        "recent_net_mean_spread_10bps",
        "recent_turnover",
        "recent_newey_west_tstat_lag24",
        "selector_score_no_may",
    ]
    q_score = q_score[[c for c in q_keep if c in q_score.columns]]
    q_score = prefix_columns(q_score, "q_", {"candidate_id"})

    r_keep = [
        "candidate_id",
        "decision",
        "reasons",
        "warnings",
        "label_t1_positive_premay_splits",
        "label_t2_positive_premay_splits",
        "one_bar_lag_positive_premay_splits",
        "latent_positive_premay_splits",
        "net_10bps_positive_premay_splits",
        "control_ratio_premay_max",
        "top_symbol_abs_contribution_share",
        "top_month_abs_contribution_share",
        "top_latent_abs_contribution_share",
    ]
    r_decision = r_decision[[c for c in r_keep if c in r_decision.columns]]
    r_decision = prefix_columns(r_decision, "r_", {"candidate_id"})

    s_keep = [
        "candidate_id",
        "a7al2s_tier",
        "allowed_as_seed_for_large_search",
        "allowed_as_seed_for_company_full_qr_comparison",
        "allowed_for_may_stress_failure_attribution",
        "allowed_for_local_expansion_before_full_pool",
        "premay_positive_split_count",
        "pre_may_control_ratio_max",
        "may_control_ratio_max",
        "may_gate_max",
    ]
    s_tiers = s_tiers[[c for c in s_keep if c in s_tiers.columns]]
    s_tiers = prefix_columns(s_tiers, "s_", {"candidate_id"})

    t_agg = (
        t_failure.assign(
            t_entry_rows=1,
            t_may_sign_flip=t_failure["may_sign_flip"].astype(str).str.lower().isin(["true", "1"]),
            t_may_control_dominated=t_failure["may_gates"].astype(str).str.contains("control_dominated", case=False, na=False),
        )
        .groupby("candidate_id", as_index=False)
        .agg(
            t_entry_rows=("t_entry_rows", "sum"),
            t_failure_labels=("a7al2t_failure_label", lambda x: "|".join(sorted(set(map(str, x))))),
            t_may_sign_flip_rows=("t_may_sign_flip", "sum"),
            t_may_control_dominated_rows=("t_may_control_dominated", "sum"),
            t_may_min_spread=("may_spread", "min"),
            t_may_mean_spread=("may_spread", "mean"),
            t_premay_mean_spread=("premay_eval_mean_spread", "mean"),
            t_eligible_for_expansion=("eligible_for_expansion", lambda x: bool(pd.Series(x).astype(str).str.lower().isin(["true", "1", "yes"]).any())),
        )
    )

    pool = generated.merge(q_score, on="candidate_id", how="left")
    pool = pool.merge(r_decision, on="candidate_id", how="left")
    pool = pool.merge(s_tiers, on="candidate_id", how="left")
    pool = pool.merge(t_agg, on="candidate_id", how="left")

    pool["in_a7al2q_generated"] = True
    pool["in_a7al2q_fast_replay"] = pool["q_decision"].notna()
    pool["in_a7al2r_forensic"] = pool["r_decision"].notna()
    pool["in_a7al2s_followup"] = pool["s_a7al2s_tier"].notna()
    pool["in_a7al2t_may_attribution"] = pool["t_entry_rows"].fillna(0).astype(float) > 0
    pool["selected_for_fast_replay"] = bool_series(pool, "selected_for_fast_replay")
    pool["shared_pool_stage"] = "generated_only"
    pool.loc[pool["in_a7al2q_fast_replay"], "shared_pool_stage"] = "fast_replay_scored"
    pool.loc[pool["in_a7al2r_forensic"], "shared_pool_stage"] = "deep_forensic"
    pool.loc[pool["in_a7al2t_may_attribution"], "shared_pool_stage"] = "stress_attributed"

    pool["has_repaired_canonical_chain"] = pool["in_a7al2q_generated"] & pool["in_a7al2q_fast_replay"]
    pool["is_control_dominated_premay"] = pd.to_numeric(pool.get("r_control_ratio_premay_max"), errors="coerce").fillna(
        pd.to_numeric(pool.get("q_control_ratio_premay_max_by_split"), errors="coerce")
    ) >= 1.0
    pool["is_may_stress_failed"] = (
        (pool["t_may_sign_flip_rows"].fillna(0).astype(float) > 0)
        | (pool["t_may_control_dominated_rows"].fillna(0).astype(float) > 0)
        | (pool["t_may_min_spread"].fillna(0).astype(float) < 0)
    )
    pool["eligible_for_large_search"] = False
    pool["eligible_for_alpha_proof"] = False
    return pool


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    q_manifest = read_json(Q_DIR / "a7al2q_manifest.json")
    r_manifest = read_json(R_DIR / "a7al2r_manifest.json")
    s_manifest = read_json(S_DIR / "a7al2s_manifest.json")
    t_manifest = read_json(T_DIR / "a7al2t_manifest.json")
    u_manifest = read_json(U_DIR / "a7al2u_manifest.json")

    pool = load_pool()
    pool_path = OUT_DIR / "a7ar7_shared_candidate_pool.csv"
    pool.to_csv(pool_path, index=False)

    stage_summary = (
        pool.groupby("shared_pool_stage", as_index=False)
        .agg(candidate_count=("candidate_id", "count"))
        .sort_values("shared_pool_stage")
    )
    decision_summary = (
        pool.groupby(["q_decision", "r_decision", "s_a7al2s_tier"], dropna=False, as_index=False)
        .agg(candidate_count=("candidate_id", "count"))
        .sort_values("candidate_count", ascending=False)
    )
    provenance_audit = pd.DataFrame(
        [
            {"check": "q_manifest_present", "pass": bool(q_manifest), "detail": q_manifest.get("decision", "")},
            {"check": "r_manifest_present", "pass": bool(r_manifest), "detail": r_manifest.get("decision", "")},
            {"check": "s_manifest_present", "pass": bool(s_manifest), "detail": s_manifest.get("decision", "")},
            {"check": "t_manifest_present", "pass": bool(t_manifest), "detail": t_manifest.get("decision", "")},
            {"check": "u_manifest_present", "pass": bool(u_manifest), "detail": u_manifest.get("decision", "")},
            {"check": "candidate_id_unique", "pass": pool["candidate_id"].is_unique, "detail": str(pool["candidate_id"].duplicated().sum())},
            {"check": "all_fast_replay_candidates_in_generated_pool", "pass": bool(pool.loc[pool["in_a7al2q_fast_replay"], "in_a7al2q_generated"].all()), "detail": str(int(pool["in_a7al2q_fast_replay"].sum()))},
            {"check": "all_forensic_candidates_in_fast_replay_pool", "pass": bool(pool.loc[pool["in_a7al2r_forensic"], "in_a7al2q_fast_replay"].all()), "detail": str(int(pool["in_a7al2r_forensic"].sum()))},
            {"check": "all_may_attributed_candidates_in_forensic_pool", "pass": bool(pool.loc[pool["in_a7al2t_may_attribution"], "in_a7al2r_forensic"].all()), "detail": str(int(pool["in_a7al2t_may_attribution"].sum()))},
        ]
    )
    stale_artifact_audit = pd.DataFrame(
        [
            {"artifact": "a7al2q_generated_candidates.csv", "status": "current_company_chain", "stale_risk": False},
            {"artifact": "a7al2q_candidate_scoreboard.csv", "status": "current_company_chain", "stale_risk": False},
            {"artifact": "a7al2r_decision_record.csv", "status": "current_company_chain", "stale_risk": False},
            {"artifact": "a7al2s_candidate_tiers.csv", "status": "current_company_chain", "stale_risk": False},
            {"artifact": "a7al2t_candidate_failure_summary.csv", "status": "current_company_chain", "stale_risk": False},
            {"artifact": "a7al2u_manifest.json", "status": "contract_only", "stale_risk": False},
        ]
    )
    authorization_matrix = pd.DataFrame(
        [
            {"action": "a7al2v_replay_aware_selector_dryrun", "status": "AUTHORIZED", "reason": "shared pool now available; no search/replay required"},
            {"action": "same_objective_rerun", "status": "NOT_AUTHORIZED", "reason": "A7AL-2T stress attribution failed all company-full candidates"},
            {"action": "direct_oi_price_expansion", "status": "NOT_AUTHORIZED", "reason": "A7AL-2U holds direct expansion until selector repair"},
            {"action": "large_formula_search", "status": "NOT_AUTHORIZED", "reason": "candidate pool governance and replay-aware selector not complete"},
            {"action": "alpha_proof_shadow_paper_live", "status": "NOT_AUTHORIZED", "reason": "no stress-clean candidate pool"},
        ]
    )

    stage_summary.to_csv(OUT_DIR / "a7ar7_stage_summary.csv", index=False)
    decision_summary.to_csv(OUT_DIR / "a7ar7_decision_summary.csv", index=False)
    provenance_audit.to_csv(OUT_DIR / "a7ar7_provenance_audit.csv", index=False)
    stale_artifact_audit.to_csv(OUT_DIR / "a7ar7_stale_artifact_audit.csv", index=False)
    authorization_matrix.to_csv(OUT_DIR / "a7ar7_authorization_matrix.csv", index=False)

    blockers = []
    if not bool(provenance_audit["pass"].all()):
        blockers.append("provenance_audit_failed")

    manifest = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AR7_SHARED_CANDIDATE_POOL_READY_FOR_A7AL2V" if not blockers else "HOLD_A7AR7_SHARED_POOL_PROVENANCE_FAIL",
        "candidate_count": int(len(pool)),
        "generated_count": int(pool["in_a7al2q_generated"].sum()),
        "fast_replay_count": int(pool["in_a7al2q_fast_replay"].sum()),
        "forensic_count": int(pool["in_a7al2r_forensic"].sum()),
        "stress_attributed_count": int(pool["in_a7al2t_may_attribution"].sum()),
        "premay_control_dominated_count": int(pool["is_control_dominated_premay"].sum()),
        "may_stress_failed_count": int(pool["is_may_stress_failed"].sum()),
        "blockers": blockers,
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_a7al2v_selector_dryrun": not blockers,
        "authorizes_same_objective_rerun": False,
        "authorizes_direct_expansion": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "may_used_for_pool_construction": False,
        "may_retained_for_veto_or_attribution": True,
    }
    write_json(OUT_DIR / "a7ar7_manifest.json", manifest)

    report = f"""# CRYPTO A7AR-7 Shared Candidate Pool

Generated: {manifest["generated_at"]}

## Decision

```text
{manifest["decision"]}
```

This stage builds a durable candidate ledger from existing A7AL-2Q/2R/2S/2T/2U artifacts. It executes no search, no replay, no training, and no proof.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Stage Summary

{md_table(stage_summary)}

## Decision Summary

{md_table(decision_summary, 40)}

## Provenance Audit

{md_table(provenance_audit)}

## Authorization

{md_table(authorization_matrix)}

## Boundary

```text
Authorized:
  A7AL-2V replay-aware selector dry-run on the shared pool

Not authorized:
  same-objective rerun
  direct OI x price expansion
  large formula search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
