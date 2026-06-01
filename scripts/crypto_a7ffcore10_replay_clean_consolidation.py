from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore10_replay_clean_consolidation"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE10_REPLAY_CLEAN_CONSOLIDATION_20260601.md"
A7FFCORE9E = REPO / "runtime" / "a7ffcore9e_bounded_replay" / "a7ffcore9e_manifest.json"
CLEAN = REPO / "runtime" / "a7ffcore9e_bounded_replay" / "a7ffcore9e_replay_clean_candidates.csv"
CANDIDATE_SUMMARY = REPO / "runtime" / "a7ffcore9e_bounded_replay" / "a7ffcore9e_candidate_summary.csv"
FAMILY_SUMMARY = REPO / "runtime" / "a7ffcore9e_bounded_replay" / "a7ffcore9e_family_summary.csv"
PACKET = REPO / "runtime" / "a7ffcore9_bounded_replay_contract" / "a7ffcore9_replay_contract_packet.csv"


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
    core9e = read_json(A7FFCORE9E)
    if core9e.get("decision") != "PASS_A7FFCORE9E_BOUNDED_REPLAY_CLEAN_CANDIDATES_READY_FOR_CORE10":
        raise SystemExit(f"A7FF-CORE9E is not ready: {core9e.get('decision')}")

    clean = pd.read_csv(CLEAN)
    candidate_summary = pd.read_csv(CANDIDATE_SUMMARY)
    family_summary = pd.read_csv(FAMILY_SUMMARY)
    packet = pd.read_csv(PACKET)
    clean_ids = set(clean["candidate_id"].astype(str))
    replay_cols = candidate_summary[
        [
            "candidate_id",
            "semantic_bucket",
            "motif_bucket",
            "replay_rows",
            "positive_validation_recent_cost5",
            "median_spread",
            "median_cost_adjusted_spread",
            "max_tstat",
            "min_control_ratio",
        ]
    ].rename(columns={"min_control_ratio": "replay_min_control_ratio"})
    pool = (
        packet[packet["candidate_id"].astype(str).isin(clean_ids)]
        .merge(replay_cols, on=["candidate_id", "semantic_bucket", "motif_bucket"], how="left", validate="one_to_one")
        .sort_values(["max_tstat", "replay_min_control_ratio"], ascending=[False, True])
        .reset_index(drop=True)
    )
    pool["core10_rank"] = range(1, len(pool) + 1)
    clean_family = family_summary[family_summary["clean_candidate_count"].gt(0)].copy()
    clean_family = clean_family.sort_values(["clean_candidate_count", "median_cost_adjusted_spread"], ascending=[False, False])
    semantic_count = int(pool["semantic_bucket"].nunique())
    motif_count = int(pool["motif_bucket"].nunique())
    top_semantic_share = float(pool["semantic_bucket"].value_counts(normalize=True).max()) if not pool.empty else 0.0
    top_motif_share = float(pool["motif_bucket"].value_counts(normalize=True).max()) if not pool.empty else 0.0
    readiness = {
        "min_clean_candidates_16": len(pool) >= 16,
        "min_semantic_buckets_6": semantic_count >= 6,
        "min_motif_buckets_5": motif_count >= 5,
        "top_semantic_share_lte_035": top_semantic_share <= 0.35,
        "top_motif_share_lte_035": top_motif_share <= 0.35,
        "core9e_eval_errors_zero": int(core9e.get("eval_error_count", 1)) == 0,
        "bounded_replay_only": core9e.get("executes_replay") is True and core9e.get("executes_search") is False,
    }
    blockers = [name for name, ok in readiness.items() if not ok]
    search_readiness_contract = {
        "source_pool": str((RUNTIME / "a7ffcore10_replay_clean_candidate_pool.csv").relative_to(REPO)),
        "candidate_count": int(len(pool)),
        "allowed_next_stage": "A7FF-CORE10E search-readiness audit",
        "not_authorized": ["formula_search", "large_search", "alpha_proof", "shadow", "paper", "live"],
        "required_before_any_search_contract": [
            "verify expression/materialization parity for clean pool",
            "verify split-level replay rows and cost buckets for clean pool",
            "verify control dominance by candidate and by family",
            "verify no single family/motif concentration",
            "define search budget, grammar, negative controls, and rollback gates",
        ],
    }
    pool.to_csv(RUNTIME / "a7ffcore10_replay_clean_candidate_pool.csv", index=False)
    clean_family.to_csv(RUNTIME / "a7ffcore10_clean_family_summary.csv", index=False)
    pd.DataFrame([{"gate": k, "pass": v} for k, v in readiness.items()]).to_csv(RUNTIME / "a7ffcore10_search_readiness_gates.csv", index=False)
    write_json(RUNTIME / "a7ffcore10_search_readiness_contract.json", search_readiness_contract)
    authorization = {
        "A7FF-CORE10E search-readiness audit": len(blockers) == 0,
        "formula_search": False,
        "large_search": False,
        "alpha_proof": False,
        "shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore10_authorization_matrix.json", authorization)
    decision = (
        "PASS_A7FFCORE10_REPLAY_CLEAN_POOL_READY_FOR_SEARCH_READINESS_AUDIT"
        if not blockers
        else "HOLD_A7FFCORE10_REPLAY_CLEAN_POOL_WEAK"
    )
    manifest = {
        "stage": "A7FF-CORE10",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE9E",
        "source_decision": core9e.get("decision"),
        "decision": decision,
        "clean_candidate_count": int(len(pool)),
        "semantic_bucket_count": semantic_count,
        "motif_bucket_count": motif_count,
        "top_semantic_bucket_share": top_semantic_share,
        "top_motif_bucket_share": top_motif_share,
        "blockers": blockers,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core10e": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE10E search-readiness audit" if not blockers else "A7FF-CORE10R replay-clean pool repair",
    }
    write_json(RUNTIME / "a7ffcore10_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE10 REPLAY-CLEAN CONSOLIDATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE10 consolidates CORE9E replay-clean candidates into a search-readiness input pool. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Search-Readiness Gates",
        "",
        md_table(pd.DataFrame([{"gate": k, "pass": v} for k, v in readiness.items()])),
        "",
        "## Clean Family Summary",
        "",
        md_table(clean_family),
        "",
        "## Clean Candidate Pool",
        "",
        md_table(pool, max_rows=60),
        "",
        "## Boundary",
        "",
        "```text",
        "search-readiness input pool built: true",
        "formula search / large search: false",
        "promotion: false",
        "alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
