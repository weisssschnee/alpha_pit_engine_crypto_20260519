from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE54E = REPO / "runtime" / "a7ffcore54e_tag_aware_numeric_execution"
EXTERNAL54E = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore54e_tag_aware_numeric_execution_20260604")
RUNTIME = REPO / "runtime" / "a7ffcore55_numeric_clue_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE55_NUMERIC_CLUE_FORENSIC_20260604.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def load_shard_csv(suffix: str) -> pd.DataFrame:
    frames = []
    for shard_dir in sorted(EXTERNAL54E.glob("shard_[0-9][0-9]")):
        shard = "s" + shard_dir.name.rsplit("_", 1)[-1]
        path = shard_dir / f"a7ffcore54e_{shard}_{suffix}"
        frame = read_csv(path)
        if not frame.empty:
            frame["core54e_shard"] = shard
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def finite_float(value: Any, default: float = np.nan) -> float:
    try:
        out = float(value)
        return out if np.isfinite(out) else default
    except Exception:
        return default


def clue_score(row: pd.Series) -> float:
    control_margin = max(0.0, 1.0 - finite_float(row.get("control_ratio_premay_max"), 1.0))
    cost5 = max(0.0, finite_float(row.get("cost5_recent_oriented"), 0.0))
    robust = max(0.0, finite_float(row.get("robust_median_tstat_floor"), 0.0))
    premay = finite_float(row.get("premay_positive_split_count"), 0.0)
    return 10.0 * control_margin + 2.0 * robust + 100.0 * cost5 + premay


def aggregate_candidates(clues: pd.DataFrame, queue: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    selected_ids = set(selected["blueprint_id"].astype(str)) if not selected.empty and "blueprint_id" in selected.columns else set()
    rows = []
    for blueprint_id, group in clues.groupby("blueprint_id", sort=False):
        group = group.copy()
        group["clue_score"] = group.apply(clue_score, axis=1)
        best = group.sort_values(
            ["clue_score", "cost5_recent_oriented", "robust_median_tstat_floor"],
            ascending=[False, False, False],
        ).iloc[0]
        queue_row = queue[queue["blueprint_id"].astype(str).eq(str(blueprint_id))]
        q = queue_row.iloc[0].to_dict() if not queue_row.empty else {}
        label_families = sorted(group["label_family"].dropna().astype(str).unique().tolist())
        horizons = sorted(group["label_horizon_h"].dropna().astype(int).unique().tolist())
        decisions = sorted(group["decision"].dropna().astype(str).unique().tolist())
        rows.append(
            {
                "blueprint_id": blueprint_id,
                "expression": best.get("expression", q.get("expression", "")),
                "a7input_queue": q.get("a7input_queue", ""),
                "semantic_pair": best.get("semantic_pair", q.get("semantic_pair", "")),
                "motif": best.get("motif", q.get("motif", "")),
                "skeleton_key": q.get("skeleton_key", best.get("skeleton_key", "")),
                "production_key": q.get("production_key", ""),
                "input_fields": q.get("input_fields", ""),
                "input_tags": q.get("input_tags", ""),
                "input_clusters": q.get("input_clusters", ""),
                "input_semantic_types": q.get("input_semantic_types", ""),
                "clue_row_count": int(len(group)),
                "label_family_count": int(len(label_families)),
                "label_families": "|".join(label_families),
                "horizons": "|".join(map(str, horizons)),
                "decisions": "|".join(decisions),
                "selected_overlap": str(blueprint_id) in selected_ids,
                "best_label_family": best.get("label_family", ""),
                "best_label_horizon_h": int(best.get("label_horizon_h", 0)),
                "best_decision": best.get("decision", ""),
                "best_control_ratio": finite_float(best.get("control_ratio_premay_max")),
                "best_cost5_recent_oriented": finite_float(best.get("cost5_recent_oriented")),
                "best_robust_median_tstat_floor": finite_float(best.get("robust_median_tstat_floor")),
                "best_lag_ok": str(best.get("lag_ok", "")).lower() in {"true", "1"},
                "best_robust_ok": str(best.get("robust_ok", "")).lower() in {"true", "1"},
                "score": float(best.get("clue_score", 0.0)),
            }
        )
    return pd.DataFrame(rows).sort_values(["selected_overlap", "score"], ascending=[False, False])


def build_replay_packet(candidates: pd.DataFrame, max_rows: int = 128) -> tuple[pd.DataFrame, pd.DataFrame]:
    selected = []
    rejects = []
    semantic_counts: Counter[str] = Counter()
    skeleton_counts: Counter[str] = Counter()
    production_seen: set[str] = set()
    semantic_cap = max(1, int(max_rows * 0.25))
    skeleton_cap = max(1, int(max_rows * 0.20))
    for _, row in candidates.iterrows():
        reasons = []
        semantic = str(row.get("semantic_pair", ""))
        skeleton = str(row.get("skeleton_key", ""))
        production = str(row.get("production_key", ""))
        if finite_float(row.get("best_control_ratio"), 99.0) >= 1.0:
            reasons.append("control_ratio_ge_1")
        if str(row.get("best_label_family", "")) == "L7_ranked_future_return":
            reasons.append("l7_only_best_label")
        if not bool(row.get("best_lag_ok")):
            reasons.append("lag_not_ok")
        if not bool(row.get("best_robust_ok")):
            reasons.append("robust_not_ok")
        if semantic_counts[semantic] >= semantic_cap:
            reasons.append("semantic_pair_cap")
        if skeleton and skeleton_counts[skeleton] >= skeleton_cap:
            reasons.append("skeleton_cap")
        if production and production in production_seen:
            reasons.append("production_duplicate")
        if len(selected) >= max_rows:
            reasons.append("packet_full")
        if reasons:
            rejected = row.to_dict()
            rejected["reject_reason"] = "|".join(reasons)
            rejects.append(rejected)
            continue
        selected.append(row.to_dict())
        semantic_counts[semantic] += 1
        if skeleton:
            skeleton_counts[skeleton] += 1
        if production:
            production_seen.add(production)
    return pd.DataFrame(selected), pd.DataFrame(rejects)


def summary_by(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[*cols, "row_count"])
    return df.groupby(cols, dropna=False).size().reset_index(name="row_count").sort_values("row_count", ascending=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE54E / "a7ffcore54e_manifest.json")
    if not source.get("authorizes_core55_numeric_forensic"):
        raise SystemExit(f"CORE54E does not authorize CORE55: {source.get('decision')}")

    queue = read_csv(EXTERNAL54E / "a7ffcore54e_main_numeric_queue.csv")
    responses = load_shard_csv("label_response_metrics.csv")
    selected = load_shard_csv("selected_portfolio_queue.csv")
    if responses.empty:
        raise SystemExit("CORE55 cannot find CORE54E label response metrics")
    clue_mask = responses["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False) & responses["label_family"].ne("L7_ranked_future_return")
    clues = responses[clue_mask].copy()
    candidates = aggregate_candidates(clues, queue, selected)
    replay_packet, rejected = build_replay_packet(candidates, max_rows=128)

    clue_pool = candidates.copy()
    clue_pool.to_csv(RUNTIME / "a7ffcore55_candidate_clue_pool.csv", index=False)
    replay_packet.to_csv(RUNTIME / "a7ffcore55_replay_ready_packet.csv", index=False)
    rejected.to_csv(RUNTIME / "a7ffcore55_rejected_candidates.csv", index=False)

    label_summary = summary_by(clues, ["label_family", "label_horizon_h"])
    semantic_summary = summary_by(clue_pool, ["semantic_pair", "best_label_family"])
    packet_semantic_summary = summary_by(replay_packet, ["semantic_pair", "best_label_family"])
    selected_overlap = summary_by(clue_pool, ["selected_overlap", "semantic_pair"])
    reject_summary = (
        rejected.assign(reject_reason=rejected["reject_reason"].astype(str).str.split("|")).explode("reject_reason")
        .groupby("reject_reason", dropna=False).size().reset_index(name="row_count").sort_values("row_count", ascending=False)
        if not rejected.empty
        else pd.DataFrame(columns=["reject_reason", "row_count"])
    )

    label_summary.to_csv(RUNTIME / "a7ffcore55_label_family_summary.csv", index=False)
    semantic_summary.to_csv(RUNTIME / "a7ffcore55_semantic_pair_summary.csv", index=False)
    packet_semantic_summary.to_csv(RUNTIME / "a7ffcore55_packet_semantic_summary.csv", index=False)
    selected_overlap.to_csv(RUNTIME / "a7ffcore55_selected_overlap_audit.csv", index=False)
    reject_summary.to_csv(RUNTIME / "a7ffcore55_reject_reason_summary.csv", index=False)

    packet_count = int(len(replay_packet))
    packet_label_count = int(replay_packet["best_label_family"].nunique()) if not replay_packet.empty else 0
    packet_semantic_count = int(replay_packet["semantic_pair"].nunique()) if not replay_packet.empty else 0
    top_semantic_share = (
        float(replay_packet["semantic_pair"].value_counts(normalize=True).iloc[0]) if not replay_packet.empty else 0.0
    )
    selected_overlap_count = int(replay_packet["selected_overlap"].sum()) if not replay_packet.empty else 0
    blockers = []
    if packet_count < 32:
        blockers.append("replay_packet_lt_32")
    if packet_label_count < 3:
        blockers.append("non_l7_label_family_count_lt_3")
    if packet_semantic_count < 5:
        blockers.append("semantic_pair_count_lt_5")
    if top_semantic_share > 0.30:
        blockers.append("top_semantic_pair_share_gt_30pct")
    if selected_overlap_count < 8:
        blockers.append("selected_overlap_lt_8")
    decision = "PASS_A7FFCORE55_REPLAY_READY_PACKET_BUILT" if not blockers else "HOLD_A7FFCORE55_REPLAY_PACKET_INSUFFICIENT"
    manifest = {
        "stage": "A7FF-CORE55",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7FF-CORE54E",
        "source_decision": source.get("decision"),
        "response_rows": int(len(responses)),
        "non_l7_clue_rows": int(len(clues)),
        "unique_candidate_count": int(len(candidates)),
        "replay_ready_packet_count": packet_count,
        "replay_packet_label_family_count": packet_label_count,
        "replay_packet_semantic_pair_count": packet_semantic_count,
        "replay_packet_top_semantic_pair_share": top_semantic_share,
        "replay_packet_selected_overlap_count": selected_overlap_count,
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core56_bounded_replay_preflight": decision.startswith("PASS_"),
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore55_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ffcore55_authorization_matrix.json",
        {
            "authorized": {
                "A7FF-CORE56 bounded replay preflight": decision.startswith("PASS_"),
            },
            "not_authorized": {
                "large_search": True,
                "alpha_proof": True,
                "shadow_paper_live": True,
            },
        },
    )

    report = [
        "# CRYPTO A7FF-CORE55 NUMERIC CLUE FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE55 consolidates CORE54E numeric clues into a replay-ready packet. It filters L7-only, control-dominated, lag/robust fragile, duplicate production, and over-concentrated semantic/skeleton structures. It does not execute replay or search.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label Summary",
        "",
        md_table(label_summary, 40),
        "",
        "## Replay Packet Semantic Summary",
        "",
        md_table(packet_semantic_summary, 80),
        "",
        "## Selected Overlap Audit",
        "",
        md_table(selected_overlap, 80),
        "",
        "## Reject Reason Summary",
        "",
        md_table(reject_summary, 40),
        "",
        "## Replay Ready Packet Preview",
        "",
        md_table(replay_packet[["blueprint_id", "semantic_pair", "motif", "best_label_family", "best_label_horizon_h", "best_control_ratio", "score", "selected_overlap"]], 40)
        if not replay_packet.empty
        else "`<empty>`",
        "",
        "## Boundary",
        "",
        "```text",
        "replay executed: false",
        "search executed: false",
        "May used: false",
        "large search / alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
