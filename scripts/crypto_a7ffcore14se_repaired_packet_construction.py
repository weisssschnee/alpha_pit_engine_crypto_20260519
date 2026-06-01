from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore14se_repaired_packet_construction"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE14SE_REPAIRED_PACKET_CONSTRUCTION_20260601.md"
CORE14S = REPO / "runtime" / "a7ffcore14s_replay_packet_repair_contract" / "a7ffcore14s_manifest.json"
CORE13_QUEUE = REPO / "runtime" / "a7ffcore13_numeric_response_contract" / "a7ffcore13_numeric_response_queue.csv"
CORE13E_CLUES = REPO / "runtime" / "a7ffcore13e_numeric_response" / "a7ffcore13e_numeric_clues.csv"
OLD_PACKET = REPO / "runtime" / "a7ffcore14_replay_preflight_contract" / "a7ffcore14_replay_packet.csv"

MAX_PACKET = 128
MIN_PACKET = 96
MAX_PER_PAIR = 25
MIN_OUTSIDE_OLD_PACKET = 32
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


def select_balanced(scored: pd.DataFrame, old_ids: set[str]) -> pd.DataFrame:
    selected: list[dict[str, Any]] = []
    pair_counts: dict[tuple[str, str], int] = {}
    outside_old = 0

    # Seed one per semantic bucket, then one per motif, before score fill. This prevents score-only collapse.
    queues = [
        scored.sort_values(["semantic_bucket", "repair_score"], ascending=[True, False]).groupby("semantic_bucket", as_index=False).head(1),
        scored.sort_values(["motif_bucket", "repair_score"], ascending=[True, False]).groupby("motif_bucket", as_index=False).head(1),
        scored.sort_values(["outside_old_packet", "repair_score"], ascending=[False, False]),
    ]
    seen: set[str] = set()
    for queue in queues:
        for row in queue.to_dict("records"):
            cid = str(row["candidate_id"])
            if cid in seen or len(selected) >= MAX_PACKET:
                continue
            pair = (str(row["semantic_bucket"]), str(row["motif_bucket"]))
            if pair_counts.get(pair, 0) >= MAX_PER_PAIR:
                continue
            if len(selected) >= MAX_PACKET - 8 and outside_old < MIN_OUTSIDE_OLD_PACKET and not bool(row["outside_old_packet"]):
                continue
            selected.append(row)
            seen.add(cid)
            pair_counts[pair] = pair_counts.get(pair, 0) + 1
            outside_old += int(cid not in old_ids)
    out = pd.DataFrame(selected)
    return out.sort_values("repair_score", ascending=False).head(MAX_PACKET).reset_index(drop=True)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core14s = read_json(CORE14S)
    if core14s.get("decision") != "PASS_A7FFCORE14S_REPLAY_PACKET_REPAIR_CONTRACT_READY_FOR_CORE14SE":
        raise SystemExit(f"A7FF-CORE14S is not ready: {core14s.get('decision')}")

    queue = pd.read_csv(CORE13_QUEUE)
    clues = pd.read_csv(CORE13E_CLUES)
    old = pd.read_csv(OLD_PACKET)
    old_ids = set(old["candidate_id"].astype(str))

    clue_summary = (
        clues[clues["numeric_clue"].astype(bool)]
        .assign(abs_corr=lambda x: pd.to_numeric(x["corr"], errors="coerce").abs())
        .groupby(["candidate_id", "semantic_bucket", "motif_bucket", "generation_mode"], dropna=False)
        .agg(
            clue_rows=("candidate_id", "size"),
            label_count=("label_id", "nunique"),
            horizon_count=("horizon", "nunique"),
            best_abs_corr=("abs_corr", "max"),
            best_original_score=("original_score", "max"),
            min_control_ratio=("control_ratio", "min"),
            median_control_ratio=("control_ratio", "median"),
            median_spread=("spread", "median"),
        )
        .reset_index()
    )
    scored = clue_summary.merge(
        queue[["candidate_id", "proposed_subgraph_id", "expression", "raw_inputs"]].drop_duplicates("candidate_id"),
        on="candidate_id",
        how="inner",
        validate="one_to_one",
    )
    scored["outside_old_packet"] = ~scored["candidate_id"].astype(str).isin(old_ids)
    scored["repair_score"] = (
        scored["label_count"].clip(upper=3) * 2.0
        + scored["horizon_count"].clip(upper=4) * 1.5
        + scored["clue_rows"].clip(upper=8) * 0.5
        + pd.to_numeric(scored["best_original_score"], errors="coerce").fillna(0) * 20.0
        - pd.to_numeric(scored["min_control_ratio"], errors="coerce").fillna(10) * 2.0
        + scored["outside_old_packet"].astype(int) * 2.5
    )
    scored = scored.sort_values("repair_score", ascending=False)
    repaired = select_balanced(scored, old_ids)
    repaired.insert(0, "core14se_rank", range(1, len(repaired) + 1))

    family_summary = (
        repaired.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            candidate_count=("candidate_id", "nunique"),
            outside_old_packet_count=("outside_old_packet", "sum"),
            median_repair_score=("repair_score", "median"),
            median_min_control_ratio=("min_control_ratio", "median"),
            median_best_original_score=("best_original_score", "median"),
        )
        .reset_index()
        .sort_values(["candidate_count", "median_repair_score"], ascending=[False, False])
    )
    gates = {
        "packet_count": int(repaired.shape[0]),
        "semantic_bucket_count": int(repaired["semantic_bucket"].nunique()),
        "motif_bucket_count": int(repaired["motif_bucket"].nunique()),
        "outside_old_packet_count": int(repaired["outside_old_packet"].sum()),
        "top_pair_share": float(family_summary["candidate_count"].max() / max(repaired.shape[0], 1)) if not family_summary.empty else 1.0,
    }
    blockers: list[str] = []
    if gates["packet_count"] < MIN_PACKET:
        blockers.append("packet_count_lt_96")
    if gates["semantic_bucket_count"] < MIN_SEMANTIC:
        blockers.append("semantic_bucket_count_lt_6")
    if gates["motif_bucket_count"] < MIN_MOTIF:
        blockers.append("motif_bucket_count_lt_5")
    if gates["outside_old_packet_count"] < MIN_OUTSIDE_OLD_PACKET:
        blockers.append("outside_old_packet_count_lt_32")
    if gates["top_pair_share"] > 0.20:
        blockers.append("top_pair_share_gt_20pct")

    decision = (
        "PASS_A7FFCORE14SE_REPAIRED_PACKET_READY_FOR_BOUNDED_REPLAY"
        if not blockers
        else "HOLD_A7FFCORE14SE_REPAIRED_PACKET_CONSTRUCTION_FAIL"
    )
    repaired.to_csv(RUNTIME / "a7ffcore14se_repaired_replay_packet.csv", index=False)
    scored.to_csv(RUNTIME / "a7ffcore14se_scored_source_pool.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore14se_family_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore14se_gates.json", gates)
    manifest = {
        "stage": "A7FF-CORE14SE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE14S",
        "source_decision": core14s.get("decision"),
        "decision": decision,
        "blockers": blockers,
        **gates,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core14see": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE14SEE repaired packet bounded replay execution" if decision.startswith("PASS_") else "A7FF-CORE14SER packet construction repair",
    }
    write_json(RUNTIME / "a7ffcore14se_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE14SE REPAIRED PACKET CONSTRUCTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE14SE constructs a repaired bounded-replay packet from CORE13E numeric clues under CORE14S rules. It does not execute replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Repaired Packet Preview",
        "",
        md_table(repaired.head(80)),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
