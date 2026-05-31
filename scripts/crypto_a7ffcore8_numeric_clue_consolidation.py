from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore8_numeric_clue_consolidation"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE8_NUMERIC_CLUE_CONSOLIDATION_20260601.md"
A7FFCORE7ER = REPO / "runtime" / "a7ffcore7er_repaired_numeric_response" / "a7ffcore7er_manifest.json"
CLUES = REPO / "runtime" / "a7ffcore7er_repaired_numeric_response" / "a7ffcore7er_numeric_clues.csv"
CANDIDATES = REPO / "runtime" / "a7ffcore7er_repaired_numeric_response" / "a7ffcore7er_candidate_queue.csv"

MAX_PREFLIGHT_CANDIDATES = 128
MAX_PER_SEMANTIC_BUCKET = 24
MAX_PER_MOTIF_BUCKET = 28


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


def build_balanced_queue(candidates: pd.DataFrame) -> pd.DataFrame:
    ordered = candidates.sort_values(
        ["clue_rows", "label_count", "horizon_count", "min_control_ratio", "best_abs_corr"],
        ascending=[False, False, False, True, False],
    ).copy()
    selected: list[dict[str, Any]] = []
    semantic_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    for row in ordered.to_dict("records"):
        semantic = str(row["semantic_bucket"])
        motif = str(row["motif_bucket"])
        if semantic_counts.get(semantic, 0) >= MAX_PER_SEMANTIC_BUCKET:
            continue
        if motif_counts.get(motif, 0) >= MAX_PER_MOTIF_BUCKET:
            continue
        row["preflight_rank"] = len(selected) + 1
        selected.append(row)
        semantic_counts[semantic] = semantic_counts.get(semantic, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        if len(selected) >= MAX_PREFLIGHT_CANDIDATES:
            break
    return pd.DataFrame(selected)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core7er = read_json(A7FFCORE7ER)
    if core7er.get("decision") != "PASS_A7FFCORE7ER_REPAIRED_NUMERIC_RESPONSE_READY_FOR_CORE8":
        raise SystemExit(f"A7FF-CORE7ER is not ready: {core7er.get('decision')}")

    clues = pd.read_csv(CLUES)
    candidates = pd.read_csv(CANDIDATES)
    label_summary = (
        clues.groupby(["label_id", "horizon"], dropna=False)
        .agg(
            clue_rows=("candidate_id", "size"),
            candidate_count=("candidate_id", "nunique"),
            semantic_bucket_count=("semantic_bucket", "nunique"),
            motif_bucket_count=("motif_bucket", "nunique"),
            median_control_ratio=("control_ratio", "median"),
            max_best_score=("original_score", "max"),
        )
        .reset_index()
        .sort_values(["clue_rows", "candidate_count"], ascending=[False, False])
    )
    family_summary = (
        clues.groupby(["semantic_bucket", "motif_bucket"], dropna=False)
        .agg(
            clue_rows=("candidate_id", "size"),
            candidate_count=("candidate_id", "nunique"),
            label_count=("label_id", "nunique"),
            horizon_count=("horizon", "nunique"),
            median_control_ratio=("control_ratio", "median"),
        )
        .reset_index()
        .sort_values(["clue_rows", "candidate_count"], ascending=[False, False])
    )
    replay_queue = build_balanced_queue(candidates)
    queue_semantic = replay_queue["semantic_bucket"].value_counts(normalize=True) if not replay_queue.empty else pd.Series(dtype=float)
    queue_motif = replay_queue["motif_bucket"].value_counts(normalize=True) if not replay_queue.empty else pd.Series(dtype=float)
    risk_flags = []
    if len(replay_queue) < min(MAX_PREFLIGHT_CANDIDATES, 64):
        risk_flags.append("small_replay_preflight_queue")
    if not queue_semantic.empty and float(queue_semantic.max()) > 0.35:
        risk_flags.append("semantic_bucket_concentration")
    if not queue_motif.empty and float(queue_motif.max()) > 0.35:
        risk_flags.append("motif_bucket_concentration")
    if int(replay_queue["semantic_bucket"].nunique()) < 5:
        risk_flags.append("semantic_breadth_low")
    if int(replay_queue["motif_bucket"].nunique()) < 4:
        risk_flags.append("motif_breadth_low")
    replay_queue.to_csv(RUNTIME / "a7ffcore8_replay_preflight_queue.csv", index=False)
    clues.to_csv(RUNTIME / "a7ffcore8_numeric_clues.csv", index=False)
    candidates.to_csv(RUNTIME / "a7ffcore8_candidate_consolidation.csv", index=False)
    label_summary.to_csv(RUNTIME / "a7ffcore8_label_horizon_summary.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore8_family_motif_summary.csv", index=False)
    pd.DataFrame([{"risk_flag": flag} for flag in risk_flags]).to_csv(RUNTIME / "a7ffcore8_risk_flags.csv", index=False)
    authorization = {
        "A7FF-CORE8E replay-preflight packet audit": True,
        "portfolio_replay_execution": False,
        "formula_search": False,
        "large_search": False,
        "alpha_proof": False,
        "shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore8_authorization_matrix.json", authorization)

    decision = (
        "PASS_A7FFCORE8_NUMERIC_CLUE_CONSOLIDATION_READY_FOR_CORE8E"
        if len(replay_queue) >= 64 and int(replay_queue["semantic_bucket"].nunique()) >= 5
        else "HOLD_A7FFCORE8_REPLAY_PREFLIGHT_QUEUE_WEAK"
    )
    manifest = {
        "stage": "A7FF-CORE8",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE7ER",
        "source_decision": core7er.get("decision"),
        "decision": decision,
        "numeric_clue_rows": int(clues.shape[0]),
        "numeric_clue_candidate_count": int(candidates.shape[0]),
        "preflight_queue_count": int(replay_queue.shape[0]),
        "preflight_queue_semantic_bucket_count": int(replay_queue["semantic_bucket"].nunique()) if not replay_queue.empty else 0,
        "preflight_queue_motif_bucket_count": int(replay_queue["motif_bucket"].nunique()) if not replay_queue.empty else 0,
        "top_semantic_bucket_share": float(queue_semantic.max()) if not queue_semantic.empty else 0.0,
        "top_motif_bucket_share": float(queue_motif.max()) if not queue_motif.empty else 0.0,
        "risk_flags": risk_flags,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core8e": decision.startswith("PASS_"),
        "authorizes_replay_execution": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE8E replay-preflight packet audit" if decision.startswith("PASS_") else "A7FF-CORE8R queue diversification repair",
    }
    write_json(RUNTIME / "a7ffcore8_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE8 NUMERIC CLUE CONSOLIDATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE8 consolidates CORE7ER repaired numeric clues into a bounded replay-preflight candidate packet. It does not run replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label-Horizon Summary",
        "",
        md_table(label_summary),
        "",
        "## Family-Motif Summary",
        "",
        md_table(family_summary),
        "",
        "## Replay-Preflight Queue Preview",
        "",
        md_table(replay_queue, max_rows=60),
        "",
        "## Boundary",
        "",
        "```text",
        "replay-preflight queue built: true",
        "portfolio replay execution: false",
        "formula search: false",
        "promotion: false",
        "alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
