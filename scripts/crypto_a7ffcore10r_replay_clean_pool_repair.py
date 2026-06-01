from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore10r_replay_clean_pool_repair"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE10R_REPLAY_CLEAN_POOL_REPAIR_20260601.md"
A7FFCORE10 = REPO / "runtime" / "a7ffcore10_replay_clean_consolidation" / "a7ffcore10_manifest.json"
POOL = REPO / "runtime" / "a7ffcore10_replay_clean_consolidation" / "a7ffcore10_replay_clean_candidate_pool.csv"

MAX_PER_SEMANTIC = 8
MAX_PER_MOTIF = 8
MIN_BALANCED_CANDIDATES = 16
MIN_SEMANTIC = 6
MIN_MOTIF = 5


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
    core10 = read_json(A7FFCORE10)
    if core10.get("decision") != "HOLD_A7FFCORE10_REPLAY_CLEAN_POOL_WEAK":
        raise SystemExit(f"A7FF-CORE10 is not in repairable hold state: {core10.get('decision')}")
    pool = pd.read_csv(POOL)
    ordered = pool.sort_values(["max_tstat", "replay_min_control_ratio"], ascending=[False, True]).copy()
    selected: list[dict[str, Any]] = []
    semantic_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    for row in ordered.to_dict("records"):
        semantic = str(row["semantic_bucket"])
        motif = str(row["motif_bucket"])
        if semantic_counts.get(semantic, 0) >= MAX_PER_SEMANTIC:
            continue
        if motif_counts.get(motif, 0) >= MAX_PER_MOTIF:
            continue
        row["balanced_rank"] = len(selected) + 1
        selected.append(row)
        semantic_counts[semantic] = semantic_counts.get(semantic, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
    balanced = pd.DataFrame(selected)
    semantic_share = float(balanced["semantic_bucket"].value_counts(normalize=True).max()) if not balanced.empty else 0.0
    motif_share = float(balanced["motif_bucket"].value_counts(normalize=True).max()) if not balanced.empty else 0.0
    gates = {
        "min_balanced_candidates_16": len(balanced) >= MIN_BALANCED_CANDIDATES,
        "min_semantic_buckets_6": int(balanced["semantic_bucket"].nunique()) >= MIN_SEMANTIC,
        "min_motif_buckets_5": int(balanced["motif_bucket"].nunique()) >= MIN_MOTIF,
        "top_semantic_share_lte_035": semantic_share <= 0.35,
        "top_motif_share_lte_035": motif_share <= 0.35,
    }
    blockers = [k for k, v in gates.items() if not v]
    balanced.to_csv(RUNTIME / "a7ffcore10r_balanced_replay_clean_pool.csv", index=False)
    pd.DataFrame([{"gate": k, "pass": v} for k, v in gates.items()]).to_csv(RUNTIME / "a7ffcore10r_repair_gates.csv", index=False)
    balanced.groupby(["semantic_bucket", "motif_bucket"], dropna=False).agg(candidate_count=("candidate_id", "nunique")).reset_index().to_csv(
        RUNTIME / "a7ffcore10r_balanced_family_summary.csv", index=False
    )
    decision = "PASS_A7FFCORE10R_BALANCED_POOL_READY_FOR_SEARCH_READINESS_AUDIT" if not blockers else "HOLD_A7FFCORE10R_BALANCED_POOL_STILL_CONCENTRATED"
    manifest = {
        "stage": "A7FF-CORE10R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE10",
        "source_decision": core10.get("decision"),
        "decision": decision,
        "input_candidate_count": int(len(pool)),
        "balanced_candidate_count": int(len(balanced)),
        "semantic_bucket_count": int(balanced["semantic_bucket"].nunique()) if not balanced.empty else 0,
        "motif_bucket_count": int(balanced["motif_bucket"].nunique()) if not balanced.empty else 0,
        "top_semantic_bucket_share": semantic_share,
        "top_motif_bucket_share": motif_share,
        "dropped_candidate_count": int(len(pool) - len(balanced)),
        "blockers": blockers,
        "executes_search": False,
        "authorizes_core10e": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE10E search-readiness audit" if not blockers else "A7FF-CORE10R continuation",
    }
    write_json(RUNTIME / "a7ffcore10r_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE10R REPLAY-CLEAN POOL REPAIR",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE10R repairs CORE10 concentration by selecting a balanced replay-clean pool. It does not run search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Repair Gates",
        "",
        md_table(pd.DataFrame([{"gate": k, "pass": v} for k, v in gates.items()])),
        "",
        "## Balanced Pool",
        "",
        md_table(balanced, max_rows=60),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
