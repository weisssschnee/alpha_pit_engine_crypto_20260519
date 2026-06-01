from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore33_bounded_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE33_BOUNDED_REPLAY_CONTRACT_20260602.md"
CORE32E = REPO / "runtime" / "a7ffcore32e_replay_preflight_execution" / "a7ffcore32e_manifest.json"
SELECTED = REPO / "runtime" / "a7ffcore32e_replay_preflight_execution" / "a7ffcore32e_selected_preflight_candidates.csv"
QUEUE = REPO / "runtime" / "a7ffcore32_replay_preflight_contract" / "a7ffcore32_replay_preflight_queue.csv"


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
    source = read_json(CORE32E)
    if source.get("decision") != "PASS_A7FFCORE32E_REPLAY_PREFLIGHT_READY_FOR_CORE33_CONTRACT":
        raise SystemExit(f"CORE32E not ready for CORE33: {source.get('decision')}")
    selected = pd.read_csv(SELECTED)
    queue = pd.read_csv(QUEUE)
    replay_queue = selected.merge(
        queue[
            [
                "preflight_candidate_id",
                "numeric_probe_id",
                "family_id",
                "dataset",
                "motif",
                "operator",
                "primary_field",
                "partner_field",
                "window_h",
                "expression",
                "cluster_key",
            ]
        ],
        on=["preflight_candidate_id", "numeric_probe_id", "family_id"],
        how="left",
    )
    replay_queue["replay_candidate_id"] = [f"a7ffcore33_{i:03d}" for i in range(len(replay_queue))]
    family_summary = (
        replay_queue.groupby("family_id", as_index=False)
        .agg(
            replay_candidate_count=("replay_candidate_id", "count"),
            cluster_count=("cluster_key", "nunique"),
            median_control_ratio=("min_control_ratio", "median"),
            median_abs_ic=("max_abs_ic", "median"),
        )
        .sort_values("family_id")
    )
    replay_protocol = pd.DataFrame(
        [
            {"item": "portfolio_proxy", "value": "hourly cross-sectional top/bottom decile spread; equal-weight and liquidity-capped variants"},
            {"item": "labels", "value": "L0/L1/L3/L5 primary; L7 diagnostic only"},
            {"item": "horizons", "value": "4h, 8h, 24h"},
            {"item": "costs", "value": "2bps, 5bps, 10bps proxy"},
            {"item": "controls", "value": "row shuffle, time shuffle, wrong-lag future, stale, sign flip, same-family placebo"},
            {"item": "robust_stats", "value": "non-overlap offset tstat; simple block bootstrap; split consistency"},
            {"item": "concentration", "value": "family, cluster, symbol, month, and dataset contribution caps"},
            {"item": "boundary", "value": "bounded replay only; no search, alpha proof, shadow, paper, live"},
        ]
    )
    gates = pd.DataFrame(
        [
            {"gate": "replay_candidate_count", "threshold": ">= 12", "observed": int(replay_queue.shape[0]), "pass": bool(replay_queue.shape[0] >= 12)},
            {"gate": "family_count", "threshold": ">= 3", "observed": int(replay_queue["family_id"].nunique()), "pass": bool(replay_queue["family_id"].nunique() >= 3)},
            {"gate": "cluster_unique", "threshold": "all selected candidates unique clusters", "observed": int(replay_queue["cluster_key"].nunique()), "pass": bool(replay_queue["cluster_key"].nunique() == replay_queue.shape[0])},
            {"gate": "top_family_share", "threshold": "<= 0.50", "observed": float(replay_queue["family_id"].value_counts(normalize=True).max()), "pass": bool(replay_queue["family_id"].value_counts(normalize=True).max() <= 0.50)},
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE33E bounded replay execution": True},
        "not_authorized": {
            "large_search": True,
            "formula_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    decision = (
        "PASS_A7FFCORE33_BOUNDED_REPLAY_CONTRACT_READY_FOR_CORE33E"
        if bool(gates["pass"].all())
        else "HOLD_A7FFCORE33_REPLAY_CONTRACT_INVALID"
    )
    manifest = {
        "stage": "A7FF-CORE33",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE32E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "replay_candidate_count": int(replay_queue.shape[0]),
        "family_count": int(replay_queue["family_id"].nunique()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core33e_bounded_replay": decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE33E bounded replay execution" if decision.startswith("PASS_") else "CORE33 contract repair",
    }
    replay_queue.to_csv(RUNTIME / "a7ffcore33_replay_candidate_queue.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore33_family_summary.csv", index=False)
    replay_protocol.to_csv(RUNTIME / "a7ffcore33_replay_protocol.csv", index=False)
    gates.to_csv(RUNTIME / "a7ffcore33_gate_audit.csv", index=False)
    write_json(RUNTIME / "a7ffcore33_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore33_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE33 BOUNDED REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE33 defines bounded replay execution over CORE32E preflight survivors. It does not execute search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Gate Audit",
        "",
        md_table(gates),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Replay Protocol",
        "",
        md_table(replay_protocol),
        "",
        "## Replay Candidate Queue",
        "",
        md_table(replay_queue[["replay_candidate_id", "family_id", "motif", "operator", "primary_field", "partner_field", "max_abs_ic", "min_control_ratio"]]),
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
