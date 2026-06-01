from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore10e_search_readiness_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE10E_SEARCH_READINESS_AUDIT_20260601.md"
A7FFCORE10R = REPO / "runtime" / "a7ffcore10r_replay_clean_pool_repair" / "a7ffcore10r_manifest.json"
BALANCED_POOL = REPO / "runtime" / "a7ffcore10r_replay_clean_pool_repair" / "a7ffcore10r_balanced_replay_clean_pool.csv"


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
    core10r = read_json(A7FFCORE10R)
    if core10r.get("decision") != "PASS_A7FFCORE10R_BALANCED_POOL_READY_FOR_SEARCH_READINESS_AUDIT":
        raise SystemExit(f"A7FF-CORE10R is not ready: {core10r.get('decision')}")
    pool = pd.read_csv(BALANCED_POOL)
    small_gates = {
        "seed_count_gte_16": len(pool) >= 16,
        "semantic_buckets_gte_6": int(pool["semantic_bucket"].nunique()) >= 6,
        "motif_buckets_gte_5": int(pool["motif_bucket"].nunique()) >= 5,
        "top_semantic_share_lte_035": float(pool["semantic_bucket"].value_counts(normalize=True).max()) <= 0.35,
        "top_motif_share_lte_035": float(pool["motif_bucket"].value_counts(normalize=True).max()) <= 0.35,
        "all_from_gate_native_core_path": pool["candidate_id"].astype(str).str.startswith("a7ffcore5_").all(),
    }
    large_gates = {
        "seed_count_gte_64": len(pool) >= 64,
        "semantic_buckets_gte_10": int(pool["semantic_bucket"].nunique()) >= 10,
        "motif_buckets_gte_8": int(pool["motif_bucket"].nunique()) >= 8,
    }
    small_ready = all(small_gates.values())
    large_ready = all(large_gates.values())
    gates = pd.DataFrame(
        [{"scope": "small_search_contract", "gate": k, "pass": v} for k, v in small_gates.items()]
        + [{"scope": "large_search_contract", "gate": k, "pass": v} for k, v in large_gates.items()]
    )
    family_summary = (
        pool.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), max_tstat=("max_tstat", "max"), median_control_ratio=("replay_min_control_ratio", "median"))
        .reset_index()
        .sort_values(["candidate_count", "max_tstat"], ascending=[False, False])
    )
    small_contract = {
        "next_stage": "A7FF-CORE11 small gate-native formula expansion contract",
        "seed_pool": str(BALANCED_POOL.relative_to(REPO)),
        "seed_candidate_count": int(len(pool)),
        "allowed_budget": {
            "generated_total": 4000,
            "materialization_preflight": 512,
            "numeric_response": 256,
            "bounded_replay": 64,
        },
        "required_constraints": [
            "use CORE typed AST and subgraph gate only",
            "derive from replay-clean seed semantic/motif families",
            "preserve sign_flip diagnostic-only control policy",
            "primary labels only: L1/L3/L5",
            "no May, no stale artifacts, no direct legacy generator bypass",
            "family/motif cap before replay",
        ],
        "not_authorized": ["large_search", "alpha_proof", "shadow", "paper", "live"],
    }
    write_json(RUNTIME / "a7ffcore10e_small_search_contract_preview.json", small_contract)
    pool.to_csv(RUNTIME / "a7ffcore10e_search_ready_seed_pool.csv", index=False)
    gates.to_csv(RUNTIME / "a7ffcore10e_readiness_gates.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore10e_family_summary.csv", index=False)

    decision = (
        "PASS_A7FFCORE10E_READY_FOR_CORE11_SMALL_SEARCH_CONTRACT"
        if small_ready and not large_ready
        else "PASS_A7FFCORE10E_READY_FOR_LARGE_SEARCH_CONTRACT"
        if small_ready and large_ready
        else "HOLD_A7FFCORE10E_SEARCH_READINESS_FAIL"
    )
    manifest = {
        "stage": "A7FF-CORE10E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE10R",
        "source_decision": core10r.get("decision"),
        "decision": decision,
        "seed_candidate_count": int(len(pool)),
        "semantic_bucket_count": int(pool["semantic_bucket"].nunique()),
        "motif_bucket_count": int(pool["motif_bucket"].nunique()),
        "small_search_contract_ready": small_ready,
        "large_search_contract_ready": large_ready,
        "executes_search": False,
        "authorizes_core11_contract": small_ready,
        "authorizes_large_search": large_ready,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE11 small gate-native formula expansion contract" if small_ready else "A7FF-CORE10R continuation",
    }
    write_json(RUNTIME / "a7ffcore10e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE10E SEARCH READINESS AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE10E audits whether the balanced replay-clean pool is ready for a search contract. It does not execute formula search, large search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Readiness Gates",
        "",
        md_table(gates),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Small Search Contract Preview",
        "",
        "```json",
        json.dumps(small_contract, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
