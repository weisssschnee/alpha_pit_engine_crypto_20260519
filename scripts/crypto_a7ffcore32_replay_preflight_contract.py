from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore32_replay_preflight_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE32_REPLAY_PREFLIGHT_CONTRACT_20260602.md"
CORE31 = REPO / "runtime" / "a7ffcore31_independent_family_clue_consolidation" / "a7ffcore31_manifest.json"
CORE31_QUEUE = REPO / "runtime" / "a7ffcore31_independent_family_clue_consolidation" / "a7ffcore31_replay_preflight_queue.csv"


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
    source = read_json(CORE31)
    if source.get("decision") != "PASS_A7FFCORE31_CLUE_CONSOLIDATION_READY_FOR_CORE32_REPLAY_PREFLIGHT_CONTRACT":
        raise SystemExit(f"CORE31 not ready for CORE32: {source.get('decision')}")
    queue = pd.read_csv(CORE31_QUEUE)
    queue = queue.sort_values(["family_id", "quality_score"], ascending=[True, False]).copy()
    queue["preflight_candidate_id"] = [f"a7ffcore32_{i:03d}" for i in range(len(queue))]
    queue["executes_replay_in_core32"] = False
    family_balance = (
        queue.groupby("family_id", as_index=False)
        .agg(
            preflight_count=("preflight_candidate_id", "count"),
            cluster_count=("cluster_key", "nunique"),
            median_control_ratio=("min_control_ratio", "median"),
            median_ic=("max_oriented_ic", "median"),
        )
        .sort_values("family_id")
    )
    preflight_checks = pd.DataFrame(
        [
            {
                "check": "candidate_rebuild",
                "requirement": "re-materialize expression from source datasets, not reuse CORE30E vectors",
                "blocking": True,
            },
            {
                "check": "split_coverage",
                "requirement": "train/validation/test/recent coverage by symbol and timestamp",
                "blocking": True,
            },
            {
                "check": "label_set",
                "requirement": "L0/L1/L3/L5/L7 at 4h/8h/24h with L7 diagnostic-only",
                "blocking": True,
            },
            {
                "check": "controls",
                "requirement": "row shuffle, time shuffle, wrong-lag future, stale, sign flip, same-family placebo",
                "blocking": True,
            },
            {
                "check": "non_overlap_stats",
                "requirement": "offset non-overlap tstats and simple block bootstrap summary",
                "blocking": True,
            },
            {
                "check": "family_and_cluster_caps",
                "requirement": "no single family > 40%; no repeated cluster representatives",
                "blocking": True,
            },
            {
                "check": "turnover_cost_proxy",
                "requirement": "2/5/10 bps proxy and one-bar executable alignment",
                "blocking": True,
            },
            {
                "check": "source_boundary",
                "requirement": "cross-exchange forward-only and liquidation/orderbook excluded",
                "blocking": True,
            },
        ]
    )
    pass_gates = pd.DataFrame(
        [
            {"gate": "queue_count", "threshold": "24", "observed": int(queue.shape[0]), "pass": bool(queue.shape[0] == 24)},
            {
                "gate": "family_count",
                "threshold": "3",
                "observed": int(queue["family_id"].nunique()),
                "pass": bool(queue["family_id"].nunique() == 3),
            },
            {
                "gate": "per_family_count",
                "threshold": "8 each",
                "observed": ",".join(f"{r.family_id}:{r.preflight_count}" for r in family_balance.itertuples()),
                "pass": bool((family_balance["preflight_count"] == 8).all()),
            },
            {
                "gate": "cluster_unique",
                "threshold": "24 unique clusters",
                "observed": int(queue["cluster_key"].nunique()),
                "pass": bool(queue["cluster_key"].nunique() == queue.shape[0]),
            },
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE32E replay preflight execution": True},
        "not_authorized": {
            "tradable_replay": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    decision = (
        "PASS_A7FFCORE32_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE32E"
        if bool(pass_gates["pass"].all())
        else "HOLD_A7FFCORE32_REPLAY_PREFLIGHT_QUEUE_INVALID"
    )
    manifest = {
        "stage": "A7FF-CORE32",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE31",
        "source_decision": source.get("decision"),
        "decision": decision,
        "preflight_queue_count": int(queue.shape[0]),
        "family_count": int(queue["family_id"].nunique()),
        "cluster_count": int(queue["cluster_key"].nunique()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core32e_preflight": decision.startswith("PASS_"),
        "authorizes_tradable_replay": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE32E replay preflight execution"
        if decision.startswith("PASS_")
        else "CORE32 replay-preflight contract repair",
    }
    queue.to_csv(RUNTIME / "a7ffcore32_replay_preflight_queue.csv", index=False)
    family_balance.to_csv(RUNTIME / "a7ffcore32_family_balance.csv", index=False)
    preflight_checks.to_csv(RUNTIME / "a7ffcore32_preflight_checks.csv", index=False)
    pass_gates.to_csv(RUNTIME / "a7ffcore32_gate_audit.csv", index=False)
    write_json(RUNTIME / "a7ffcore32_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore32_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE32 REPLAY PREFLIGHT CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE32 is a replay-preflight contract. It does not execute tradable replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Gate Audit",
        "",
        md_table(pass_gates),
        "",
        "## Family Balance",
        "",
        md_table(family_balance),
        "",
        "## Preflight Checks",
        "",
        md_table(preflight_checks),
        "",
        "## Replay Preflight Queue",
        "",
        md_table(queue[["preflight_candidate_id", "numeric_probe_id", "family_id", "motif", "operator", "primary_field", "partner_field", "quality_score"]]),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
