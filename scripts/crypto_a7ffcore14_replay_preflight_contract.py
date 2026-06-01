from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore14_replay_preflight_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE14_REPLAY_PREFLIGHT_CONTRACT_20260601.md"
A7FFCORE13E = REPO / "runtime" / "a7ffcore13e_numeric_response" / "a7ffcore13e_manifest.json"
CLUES = REPO / "runtime" / "a7ffcore13e_numeric_response" / "a7ffcore13e_numeric_clues.csv"
QUEUE = REPO / "runtime" / "a7ffcore13_numeric_response_contract" / "a7ffcore13_numeric_response_queue.csv"

MAX_PACKET = 128
MAX_PER_SEMANTIC = 28
MAX_PER_MOTIF = 32


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


def balanced_packet(candidates: pd.DataFrame) -> pd.DataFrame:
    ordered = candidates.sort_values(["clue_rows", "label_count", "horizon_count", "min_control_ratio", "best_abs_corr"], ascending=[False, False, False, True, False])
    selected: list[dict[str, Any]] = []
    sem: dict[str, int] = {}
    mot: dict[str, int] = {}
    for row in ordered.to_dict("records"):
        s = str(row["semantic_bucket"])
        m = str(row["motif_bucket"])
        if sem.get(s, 0) >= MAX_PER_SEMANTIC:
            continue
        if mot.get(m, 0) >= MAX_PER_MOTIF:
            continue
        row["core14_rank"] = len(selected) + 1
        selected.append(row)
        sem[s] = sem.get(s, 0) + 1
        mot[m] = mot.get(m, 0) + 1
        if len(selected) >= MAX_PACKET:
            break
    return pd.DataFrame(selected)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core13e = read_json(A7FFCORE13E)
    if core13e.get("decision") != "PASS_A7FFCORE13E_NUMERIC_RESPONSE_READY_FOR_CORE14":
        raise SystemExit(f"A7FF-CORE13E is not ready: {core13e.get('decision')}")
    clues = pd.read_csv(CLUES)
    queue = pd.read_csv(QUEUE)
    clue_agg = (
        clues.groupby(["candidate_id", "semantic_bucket", "motif_bucket", "generation_mode"], dropna=False)
        .agg(
            clue_rows=("candidate_id", "size"),
            label_count=("label_id", "nunique"),
            horizon_count=("horizon", "nunique"),
            best_abs_corr=("corr", lambda s: float(pd.to_numeric(s, errors="coerce").abs().max())),
            best_original_score=("original_score", "max"),
            min_control_ratio=("control_ratio", "min"),
        )
        .reset_index()
    )
    packet = balanced_packet(clue_agg).merge(
        queue[["candidate_id", "proposed_subgraph_id", "expression", "raw_inputs"]],
        on="candidate_id",
        how="left",
        validate="one_to_one",
    )
    label_summary = (
        clues[clues["candidate_id"].isin(packet["candidate_id"])]
        .groupby(["label_id", "horizon"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), clue_rows=("candidate_id", "size"), median_control_ratio=("control_ratio", "median"))
        .reset_index()
        .sort_values(["candidate_count", "clue_rows"], ascending=[False, False])
    )
    family_summary = (
        packet.groupby(["semantic_bucket", "motif_bucket", "generation_mode"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), median_control_ratio=("min_control_ratio", "median"))
        .reset_index()
        .sort_values("candidate_count", ascending=False)
    )
    top_sem = float(packet["semantic_bucket"].value_counts(normalize=True).max()) if not packet.empty else 0.0
    top_mot = float(packet["motif_bucket"].value_counts(normalize=True).max()) if not packet.empty else 0.0
    gates = {
        "packet_count_gte_64": len(packet) >= 64,
        "semantic_buckets_gte_5": int(packet["semantic_bucket"].nunique()) >= 5,
        "motif_buckets_gte_5": int(packet["motif_bucket"].nunique()) >= 5,
        "top_semantic_share_lte_035": top_sem <= 0.35,
        "top_motif_share_lte_035": top_mot <= 0.35,
    }
    blockers = [k for k, v in gates.items() if not v]
    packet.to_csv(RUNTIME / "a7ffcore14_replay_packet.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ffcore14_label_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore14_family_summary.csv", index=False)
    pd.DataFrame([{"gate": k, "pass": v} for k, v in gates.items()]).to_csv(RUNTIME / "a7ffcore14_gates.csv", index=False)
    protocol = {
        "packet": str((RUNTIME / "a7ffcore14_replay_packet.csv").relative_to(REPO)),
        "cost_bps": [0, 2, 5, 10],
        "labels": ["L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"],
        "horizons": [1, 4, 8, 24],
        "controls": ["wrong_lag_future", "wrong_lag_stale", "time_shuffle", "symbol_shuffle", "same_family_placebo"],
        "sign_flip": "diagnostic_only",
    }
    write_json(RUNTIME / "a7ffcore14_replay_protocol.json", protocol)
    decision = "PASS_A7FFCORE14_REPLAY_PREFLIGHT_CONTRACT_READY_FOR_CORE14E" if not blockers else "HOLD_A7FFCORE14_PACKET_CONCENTRATION_OR_SIZE_FAIL"
    manifest = {
        "stage": "A7FF-CORE14",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE13E",
        "source_decision": core13e.get("decision"),
        "decision": decision,
        "numeric_clue_candidate_count": int(clue_agg.shape[0]),
        "packet_candidate_count": int(packet.shape[0]),
        "semantic_bucket_count": int(packet["semantic_bucket"].nunique()) if not packet.empty else 0,
        "motif_bucket_count": int(packet["motif_bucket"].nunique()) if not packet.empty else 0,
        "top_semantic_share": top_sem,
        "top_motif_share": top_mot,
        "blockers": blockers,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core14e": not blockers,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE14E bounded replay execution" if not blockers else "A7FF-CORE14R packet repair",
    }
    write_json(RUNTIME / "a7ffcore14_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE14 REPLAY-PREFLIGHT CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE14 builds a bounded replay packet from CORE13E numeric clues. It does not execute replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Gates",
        "",
        md_table(pd.DataFrame([{"gate": k, "pass": v} for k, v in gates.items()])),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Label Summary",
        "",
        md_table(label_summary),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
