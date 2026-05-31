from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore8e_replay_preflight_packet_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE8E_REPLAY_PREFLIGHT_PACKET_AUDIT_20260601.md"
A7FFCORE8 = REPO / "runtime" / "a7ffcore8_numeric_clue_consolidation" / "a7ffcore8_manifest.json"
PREFLIGHT_QUEUE = REPO / "runtime" / "a7ffcore8_numeric_clue_consolidation" / "a7ffcore8_replay_preflight_queue.csv"
CORE5_QUEUE = REPO / "runtime" / "a7ffcore5_gate_native_generation_dryrun" / "a7ffcore5_gate_native_candidate_queue.csv"
CORE6E_MAT = REPO / "runtime" / "a7ffcore6e_materialization_preflight" / "a7ffcore6e_materialization_summary_rows.csv"
CORE7ER_CLUES = REPO / "runtime" / "a7ffcore7er_repaired_numeric_response" / "a7ffcore7er_numeric_clues.csv"


MIN_PACKET_CANDIDATES = 64
MIN_SEMANTIC_BUCKETS = 5
MIN_MOTIF_BUCKETS = 4
MAX_TOP_SEMANTIC_SHARE = 0.35
MAX_TOP_MOTIF_SHARE = 0.35
MAX_PER_SHARD = 32


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


def forbidden_token_count(series: pd.Series) -> int:
    # Past return and taker_buy_* fields are valid feature inputs. This check is
    # limited to explicit label/future/May/target leakage markers.
    token_re = r"(?i)(?:forward_|future_|label_|_label|may_|_may|return_horizon|target_|_target)"
    return int(series.fillna("").astype(str).str.contains(token_re, regex=True).sum())


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core8 = read_json(A7FFCORE8)
    if core8.get("decision") != "PASS_A7FFCORE8_NUMERIC_CLUE_CONSOLIDATION_READY_FOR_CORE8E":
        raise SystemExit(f"A7FF-CORE8 is not ready: {core8.get('decision')}")

    queue = pd.read_csv(PREFLIGHT_QUEUE)
    core5 = pd.read_csv(CORE5_QUEUE)
    mat = pd.read_csv(CORE6E_MAT)
    clues = pd.read_csv(CORE7ER_CLUES)
    packet = (
        queue.merge(
            core5[
                [
                    "candidate_id",
                    "root_subgraph_id",
                    "expression",
                    "raw_inputs",
                    "candidate_roles",
                    "semantic_pairs",
                    "motifs",
                    "formula_gen_gate",
                    "gate_mode",
                    "gate_allowed",
                    "uses_may",
                    "ordinary_alpha_allowed",
                    "authorizes_replay",
                    "authorizes_search",
                ]
            ],
            on="candidate_id",
            how="left",
            validate="one_to_one",
        )
        .merge(
            mat[
                [
                    "candidate_id",
                    "status",
                    "missing_field_count",
                    "label_or_may_token",
                    "non_null_ratio",
                    "active_ratio",
                    "std",
                ]
            ].rename(columns={"status": "materialization_status"}),
            on="candidate_id",
            how="left",
            validate="one_to_one",
        )
    )
    clue_agg = (
        clues.groupby("candidate_id", dropna=False)
        .agg(
            clue_rows_from_detail=("candidate_id", "size"),
            clue_label_count=("label_id", "nunique"),
            clue_horizon_count=("horizon", "nunique"),
            min_detail_control_ratio=("control_ratio", "min"),
            max_abs_detail_corr=("corr", lambda s: float(pd.to_numeric(s, errors="coerce").abs().max())),
            best_detail_score=("original_score", "max"),
        )
        .reset_index()
    )
    packet = packet.merge(clue_agg, on="candidate_id", how="left", validate="one_to_one")
    packet["packet_ready"] = (
        packet["expression"].notna()
        & packet["materialization_status"].eq("ok")
        & packet["gate_allowed"].astype(str).str.lower().eq("true")
        & packet["uses_may"].astype(str).str.lower().ne("true")
        & packet["authorizes_replay"].astype(str).str.lower().ne("true")
        & packet["authorizes_search"].astype(str).str.lower().ne("true")
        & packet["label_or_may_token"].astype(str).str.lower().ne("true")
        & packet["missing_field_count"].fillna(999).astype(float).eq(0)
        & packet["clue_rows_from_detail"].fillna(0).astype(float).gt(0)
    )

    label_coverage = (
        clues[clues["candidate_id"].isin(packet["candidate_id"])]
        .groupby(["label_id", "horizon"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), clue_rows=("candidate_id", "size"), median_control_ratio=("control_ratio", "median"))
        .reset_index()
        .sort_values(["candidate_count", "clue_rows"], ascending=[False, False])
    )
    semantic_summary = (
        packet.groupby("semantic_bucket", dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), ready_count=("packet_ready", "sum"), median_min_control_ratio=("min_control_ratio", "median"))
        .reset_index()
        .sort_values(["candidate_count"], ascending=False)
    )
    motif_summary = (
        packet.groupby("motif_bucket", dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), ready_count=("packet_ready", "sum"), median_min_control_ratio=("min_control_ratio", "median"))
        .reset_index()
        .sort_values(["candidate_count"], ascending=False)
    )
    role_summary = (
        packet.groupby(["candidate_roles", "formula_gen_gate", "gate_mode"], dropna=False)
        .agg(candidate_count=("candidate_id", "nunique"), ready_count=("packet_ready", "sum"))
        .reset_index()
        .sort_values("candidate_count", ascending=False)
    )
    shard_rows = []
    for i, start in enumerate(range(0, len(packet), MAX_PER_SHARD)):
        end = min(start + MAX_PER_SHARD, len(packet))
        shard_rows.append({"shard_id": f"S{i:02d}", "start_index": start, "end_index_exclusive": end, "candidate_count": end - start})
    shard_plan = pd.DataFrame(shard_rows)

    top_semantic_share = float(packet["semantic_bucket"].value_counts(normalize=True).max()) if not packet.empty else 0.0
    top_motif_share = float(packet["motif_bucket"].value_counts(normalize=True).max()) if not packet.empty else 0.0
    risk_flags = []
    if len(packet) < MIN_PACKET_CANDIDATES:
        risk_flags.append("packet_too_small")
    if int(packet["semantic_bucket"].nunique()) < MIN_SEMANTIC_BUCKETS:
        risk_flags.append("semantic_breadth_low")
    if int(packet["motif_bucket"].nunique()) < MIN_MOTIF_BUCKETS:
        risk_flags.append("motif_breadth_low")
    if top_semantic_share > MAX_TOP_SEMANTIC_SHARE:
        risk_flags.append("semantic_concentration")
    if top_motif_share > MAX_TOP_MOTIF_SHARE:
        risk_flags.append("motif_concentration")
    if not bool(packet["packet_ready"].all()):
        risk_flags.append("packet_readiness_fail")
    if forbidden_token_count(packet["expression"]) > 0 or forbidden_token_count(packet["raw_inputs"]) > 0:
        risk_flags.append("forbidden_expression_or_field_token")

    packet.to_csv(RUNTIME / "a7ffcore8e_replay_preflight_packet.csv", index=False)
    label_coverage.to_csv(RUNTIME / "a7ffcore8e_label_horizon_coverage.csv", index=False)
    semantic_summary.to_csv(RUNTIME / "a7ffcore8e_semantic_bucket_audit.csv", index=False)
    motif_summary.to_csv(RUNTIME / "a7ffcore8e_motif_bucket_audit.csv", index=False)
    role_summary.to_csv(RUNTIME / "a7ffcore8e_role_gate_audit.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ffcore8e_replay_preflight_shard_plan.csv", index=False)
    pd.DataFrame([{"risk_flag": flag} for flag in risk_flags]).to_csv(RUNTIME / "a7ffcore8e_risk_flags.csv", index=False)

    decision = "PASS_A7FFCORE8E_REPLAY_PREFLIGHT_PACKET_READY_FOR_CORE9_CONTRACT" if not risk_flags else "HOLD_A7FFCORE8E_REPLAY_PREFLIGHT_PACKET_RISK"
    manifest = {
        "stage": "A7FF-CORE8E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE8",
        "source_decision": core8.get("decision"),
        "decision": decision,
        "packet_candidate_count": int(len(packet)),
        "packet_ready_count": int(packet["packet_ready"].sum()),
        "semantic_bucket_count": int(packet["semantic_bucket"].nunique()),
        "motif_bucket_count": int(packet["motif_bucket"].nunique()),
        "label_family_count": int(label_coverage["label_id"].nunique()) if not label_coverage.empty else 0,
        "horizon_count": int(label_coverage["horizon"].nunique()) if not label_coverage.empty else 0,
        "top_semantic_bucket_share": top_semantic_share,
        "top_motif_bucket_share": top_motif_share,
        "risk_flags": risk_flags,
        "shard_count": int(len(shard_plan)),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core9_contract": decision.startswith("PASS_"),
        "authorizes_replay_execution": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE9 bounded replay contract" if decision.startswith("PASS_") else "A7FF-CORE8R packet repair",
    }
    write_json(RUNTIME / "a7ffcore8e_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE8E REPLAY-PREFLIGHT PACKET AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-CORE8E audits the CORE8 packet as input for a future replay contract. It does not run portfolio replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Label-Horizon Coverage",
        "",
        md_table(label_coverage),
        "",
        "## Semantic Bucket Audit",
        "",
        md_table(semantic_summary),
        "",
        "## Motif Bucket Audit",
        "",
        md_table(motif_summary),
        "",
        "## Role/Gate Audit",
        "",
        md_table(role_summary),
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan),
        "",
        "## Boundary",
        "",
        "```text",
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
