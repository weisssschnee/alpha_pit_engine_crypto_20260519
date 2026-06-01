from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore31_independent_family_clue_consolidation"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE31_INDEPENDENT_FAMILY_CLUE_CONSOLIDATION_20260602.md"
CORE30E = REPO / "runtime" / "a7ffcore30e_bounded_numeric_probe" / "a7ffcore30e_manifest.json"
CORE30_RESULTS = REPO / "runtime" / "a7ffcore30e_bounded_numeric_probe" / "a7ffcore30e_numeric_results.csv"
CORE30_SELECTED = REPO / "runtime" / "a7ffcore30e_bounded_numeric_probe" / "a7ffcore30e_selected_numeric_clues.csv"
CORE30_QUEUE = REPO / "runtime" / "a7ffcore30_independent_family_numeric_probe_contract" / "a7ffcore30_numeric_probe_queue.csv"


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
    source = read_json(CORE30E)
    if source.get("decision") != "PASS_A7FFCORE30E_NUMERIC_PROBE_CLUES_READY_FOR_CORE31_CONTRACT":
        raise SystemExit(f"CORE30E not ready for CORE31: {source.get('decision')}")

    results = pd.read_csv(CORE30_RESULTS)
    selected = pd.read_csv(CORE30_SELECTED)
    queue = pd.read_csv(CORE30_QUEUE)
    enriched = selected.merge(
        queue[
            [
                "numeric_probe_id",
                "candidate_id",
                "family_id",
                "dataset",
                "motif",
                "operator",
                "primary_field",
                "partner_field",
                "window_h",
                "expression",
            ]
        ],
        on=["numeric_probe_id", "family_id"],
        how="left",
    )
    enriched["cluster_key"] = (
        enriched["family_id"].astype(str)
        + "|"
        + enriched["motif"].astype(str)
        + "|"
        + enriched["operator"].astype(str)
        + "|"
        + enriched["primary_field"].astype(str)
        + "|"
        + enriched["partner_field"].astype(str)
    )
    enriched["quality_score"] = (
        enriched["clean_label_count"].astype(float) * 10.0
        + enriched["max_oriented_ic"].astype(float) * 100.0
        + (1.0 - enriched["min_control_ratio"].clip(upper=1.5).astype(float)) * 5.0
    )
    label_evidence = (
        results[results["numeric_probe_id"].isin(enriched["numeric_probe_id"])]
        .groupby(["numeric_probe_id", "label_family", "horizon_h"], as_index=False)
        .agg(
            max_abs_ic=("oriented_ic", "max"),
            median_control_ratio=("control_ratio", "median"),
            clean_rows=("control_clean", "sum"),
            eval_rows=("n", "max"),
        )
        .sort_values(["numeric_probe_id", "label_family", "horizon_h"])
    )
    cluster_registry = (
        enriched.groupby(["cluster_key", "family_id", "motif", "operator", "primary_field", "partner_field"], as_index=False)
        .agg(
            clue_count=("numeric_probe_id", "count"),
            best_quality_score=("quality_score", "max"),
            best_ic=("max_oriented_ic", "max"),
            median_control_ratio=("min_control_ratio", "median"),
            best_clean_label_count=("clean_label_count", "max"),
        )
        .sort_values(["best_quality_score", "best_ic"], ascending=[False, False])
    )
    # One representative per cluster first, then balance by family.
    representatives = (
        enriched.sort_values(["cluster_key", "quality_score", "max_oriented_ic"], ascending=[True, False, False])
        .groupby("cluster_key", as_index=False)
        .head(1)
        .sort_values(["family_id", "quality_score"], ascending=[True, False])
    )
    replay_queue_parts = []
    for _, group in representatives.groupby("family_id", sort=True):
        replay_queue_parts.append(group.head(8))
    replay_queue = pd.concat(replay_queue_parts, ignore_index=True).sort_values(
        ["quality_score", "max_oriented_ic"], ascending=[False, False]
    )
    replay_queue["replay_preflight_role"] = "candidate_for_replay_preflight_contract"
    replay_queue["executes_replay"] = False

    family_summary = (
        enriched.groupby("family_id", as_index=False)
        .agg(
            clue_count=("numeric_probe_id", "count"),
            cluster_count=("cluster_key", "nunique"),
            median_control_ratio=("min_control_ratio", "median"),
            median_ic=("max_oriented_ic", "median"),
            max_ic=("max_oriented_ic", "max"),
        )
        .sort_values("family_id")
    )
    replay_family_summary = (
        replay_queue.groupby("family_id", as_index=False)
        .agg(
            replay_preflight_candidate_count=("numeric_probe_id", "count"),
            cluster_count=("cluster_key", "nunique"),
            median_control_ratio=("min_control_ratio", "median"),
            median_ic=("max_oriented_ic", "median"),
        )
        .sort_values("family_id")
    )
    concentration = pd.DataFrame(
        [
            {
                "metric": "top_family_share_selected_clues",
                "value": float(enriched["family_id"].value_counts(normalize=True).max()) if not enriched.empty else 0.0,
            },
            {
                "metric": "top_cluster_share_selected_clues",
                "value": float(enriched["cluster_key"].value_counts(normalize=True).max()) if not enriched.empty else 0.0,
            },
            {
                "metric": "top_family_share_replay_queue",
                "value": float(replay_queue["family_id"].value_counts(normalize=True).max()) if not replay_queue.empty else 0.0,
            },
            {
                "metric": "top_cluster_share_replay_queue",
                "value": float(replay_queue["cluster_key"].value_counts(normalize=True).max()) if not replay_queue.empty else 0.0,
            },
        ]
    )
    gate_rows = [
        {
            "gate": "selected_clue_count",
            "threshold": ">= 24",
            "observed": int(enriched.shape[0]),
            "pass": bool(enriched.shape[0] >= 24),
        },
        {
            "gate": "selected_family_count",
            "threshold": ">= 3",
            "observed": int(enriched["family_id"].nunique()),
            "pass": bool(enriched["family_id"].nunique() >= 3),
        },
        {
            "gate": "cluster_count",
            "threshold": ">= 12",
            "observed": int(enriched["cluster_key"].nunique()),
            "pass": bool(enriched["cluster_key"].nunique() >= 12),
        },
        {
            "gate": "replay_queue_count",
            "threshold": ">= 18",
            "observed": int(replay_queue.shape[0]),
            "pass": bool(replay_queue.shape[0] >= 18),
        },
        {
            "gate": "replay_queue_family_count",
            "threshold": ">= 3",
            "observed": int(replay_queue["family_id"].nunique()),
            "pass": bool(replay_queue["family_id"].nunique() >= 3),
        },
        {
            "gate": "top_family_share_replay_queue",
            "threshold": "<= 0.50",
            "observed": float(concentration.loc[concentration["metric"].eq("top_family_share_replay_queue"), "value"].iloc[0]),
            "pass": bool(concentration.loc[concentration["metric"].eq("top_family_share_replay_queue"), "value"].iloc[0] <= 0.50),
        },
    ]
    gates = pd.DataFrame(gate_rows)
    decision = (
        "PASS_A7FFCORE31_CLUE_CONSOLIDATION_READY_FOR_CORE32_REPLAY_PREFLIGHT_CONTRACT"
        if bool(gates["pass"].all())
        else "HOLD_A7FFCORE31_CLUE_CONSOLIDATION_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-CORE31",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE30E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "selected_clue_count": int(enriched.shape[0]),
        "cluster_count": int(enriched["cluster_key"].nunique()),
        "family_count": int(enriched["family_id"].nunique()),
        "replay_preflight_queue_count": int(replay_queue.shape[0]),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core32_contract": decision.startswith("PASS_"),
        "authorizes_replay_execution": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE32 replay preflight contract"
        if decision.startswith("PASS_")
        else "CORE31 clue consolidation repair",
    }
    enriched.to_csv(RUNTIME / "a7ffcore31_enriched_numeric_clues.csv", index=False)
    label_evidence.to_csv(RUNTIME / "a7ffcore31_label_evidence.csv", index=False)
    cluster_registry.to_csv(RUNTIME / "a7ffcore31_cluster_registry.csv", index=False)
    replay_queue.to_csv(RUNTIME / "a7ffcore31_replay_preflight_queue.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore31_family_summary.csv", index=False)
    replay_family_summary.to_csv(RUNTIME / "a7ffcore31_replay_family_summary.csv", index=False)
    concentration.to_csv(RUNTIME / "a7ffcore31_concentration_audit.csv", index=False)
    gates.to_csv(RUNTIME / "a7ffcore31_gate_audit.csv", index=False)
    write_json(RUNTIME / "a7ffcore31_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE31 INDEPENDENT FAMILY CLUE CONSOLIDATION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE31 consolidates bounded numeric clues into a replay-preflight candidate queue. It does not execute replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Summary",
        "",
        f"- selected_clue_count: `{manifest['selected_clue_count']}`",
        f"- cluster_count: `{manifest['cluster_count']}`",
        f"- family_count: `{manifest['family_count']}`",
        f"- replay_preflight_queue_count: `{manifest['replay_preflight_queue_count']}`",
        "",
        "## Gate Audit",
        "",
        md_table(gates),
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Replay Queue Family Summary",
        "",
        md_table(replay_family_summary),
        "",
        "## Concentration Audit",
        "",
        md_table(concentration),
        "",
        "## Replay Preflight Queue Preview",
        "",
        md_table(replay_queue.head(40)),
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
