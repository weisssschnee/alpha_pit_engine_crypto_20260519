from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff14_label_balanced_selector_repair"
REPORT = REPO / "reports" / "CRYPTO_A7FF14_LABEL_BALANCED_SELECTOR_REPAIR_20260530.md"

A7FF12_AGG = REPO / "runtime" / "a7ff12_company_wave_aggregate"
A7FF13_MANIFEST = REPO / "runtime" / "a7ff13_wave_triage" / "a7ff13_manifest.json"

LABEL_ORDER = [
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L3_liquidity_tier_relative_return",
    "L5_vol_adjusted_return",
]
TARGET_TOTAL = 64
LABEL_QUOTA = 16
SEMANTIC_CAP = 20
MOTIF_CAP = 20
SKELETON_CAP = 4


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
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def bool_series(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s.fillna(False)
    return s.astype(str).str.lower().isin(["true", "1", "yes"])


def load_shard_frames(suffix: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in sorted(glob.glob(str(REPO / "runtime" / "a7ff12_company_numeric_probe_shard_*" / f"a7ff12s*_{suffix}.csv"))):
        p = Path(path)
        shard = p.parent.name.rsplit("_", 1)[-1]
        df = pd.read_csv(p)
        df.insert(0, "shard", shard)
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def select_balanced(candidates: pd.DataFrame) -> pd.DataFrame:
    selected_rows: list[dict[str, Any]] = []
    used_blueprints: set[str] = set()
    semantic_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    label_counts: dict[str, int] = {}

    for label in LABEL_ORDER:
        sub = candidates[candidates["label_family"].eq(label)].sort_values(
            ["selector_score", "strict_priority", "cost10_recent_oriented", "robust_min_tstat_floor"],
            ascending=[False, False, False, False],
        )
        for _, row in sub.iterrows():
            if label_counts.get(label, 0) >= LABEL_QUOTA:
                break
            bp = str(row["blueprint_id"])
            sem = str(row["semantic_pair"])
            motif = str(row["motif"])
            skel = str(row.get("skeleton_key", ""))
            if bp in used_blueprints:
                continue
            if semantic_counts.get(sem, 0) >= SEMANTIC_CAP:
                continue
            if motif_counts.get(motif, 0) >= MOTIF_CAP:
                continue
            if skeleton_counts.get(skel, 0) >= SKELETON_CAP:
                continue
            payload = row.to_dict()
            payload["selector_rank"] = len(selected_rows) + 1
            payload["selector_tier"] = "strict_priority" if bool(row["strict_priority"]) else "balanced_numeric_diagnostic"
            selected_rows.append(payload)
            used_blueprints.add(bp)
            semantic_counts[sem] = semantic_counts.get(sem, 0) + 1
            motif_counts[motif] = motif_counts.get(motif, 0) + 1
            skeleton_counts[skel] = skeleton_counts.get(skel, 0) + 1
            label_counts[label] = label_counts.get(label, 0) + 1
            if len(selected_rows) >= TARGET_TOTAL:
                break
    return pd.DataFrame(selected_rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ff13 = read_json(A7FF13_MANIFEST)
    responses = load_shard_frames("label_response_metrics")
    mats = load_shard_frames("materialization_metrics")
    if responses.empty:
        raise SystemExit("missing A7FF-12 label response metrics")
    if mats.empty:
        raise SystemExit("missing A7FF-12 materialization metrics")

    for col in ["lag_ok", "robust_ok", "premay_all_positive"]:
        responses[col] = bool_series(responses[col])
    clue = responses[
        responses["decision"].astype(str).str.contains("NUMERIC_CLUE", na=False)
        & responses["label_family"].isin(LABEL_ORDER)
        & responses["premay_all_positive"]
        & responses["lag_ok"]
        & responses["robust_ok"]
        & (responses["control_ratio_premay_max"] < 1.0)
        & (responses["cost2_recent_oriented"] > 0)
    ].copy()

    mat_cols = ["shard", "blueprint_id", "skeleton_key", "finite_share", "nonzero_share"]
    clue = clue.merge(mats[mat_cols], on=["shard", "blueprint_id"], how="left")
    clue["strict_priority"] = (
        (clue["control_ratio_premay_max"] < 0.8)
        & (clue["cost10_recent_oriented"] > 0)
        & (clue["robust_min_tstat_floor"] > 0)
    )
    clue["selector_score"] = (
        3.0 * (1.0 - clue["control_ratio_premay_max"].clip(upper=1.0))
        + 2.0 * clue["strict_priority"].astype(float)
        + clue["cost2_recent_oriented"].clip(lower=0.0) * 1000.0
        + clue["robust_min_tstat_floor"].clip(lower=0.0)
        + clue["premay_positive_split_count"].astype(float)
        + clue["cost10_recent_oriented"].clip(lower=0.0) * 250.0
    )

    selected = select_balanced(clue)

    candidate_label_summary = (
        clue.groupby(["label_family", "label_horizon_h"], dropna=False)
        .agg(
            candidate_rows=("blueprint_id", "count"),
            unique_blueprints=("blueprint_id", "nunique"),
            strict_priority_rows=("strict_priority", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost10=("cost10_recent_oriented", "median"),
        )
        .reset_index()
        .sort_values(["label_family", "label_horizon_h"])
    )
    selected_label_summary = (
        selected.groupby(["label_family", "label_horizon_h"], dropna=False)
        .agg(
            selected_count=("blueprint_id", "count"),
            strict_priority_count=("strict_priority", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_cost10=("cost10_recent_oriented", "median"),
        )
        .reset_index()
        .sort_values(["label_family", "label_horizon_h"])
        if not selected.empty
        else pd.DataFrame()
    )
    selected_semantic_summary = (
        selected.groupby("semantic_pair", dropna=False)
        .agg(
            selected_count=("blueprint_id", "count"),
            strict_priority_count=("strict_priority", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values("selected_count", ascending=False)
        if not selected.empty
        else pd.DataFrame()
    )
    selected_motif_summary = (
        selected.groupby("motif", dropna=False)
        .size()
        .reset_index(name="selected_count")
        .sort_values("selected_count", ascending=False)
        if not selected.empty
        else pd.DataFrame()
    )

    label_families = int(selected["label_family"].nunique()) if not selected.empty else 0
    top_label_share = float(selected["label_family"].value_counts(normalize=True).max()) if not selected.empty else 0.0
    top_semantic_share = float(selected["semantic_pair"].value_counts(normalize=True).max()) if not selected.empty else 0.0
    strict_count = int(selected["strict_priority"].sum()) if not selected.empty else 0
    decision = (
        "PASS_A7FF14_LABEL_BALANCED_SELECTOR_REPAIR_READY_FOR_A7FF15"
        if len(selected) >= TARGET_TOTAL
        and label_families == len(LABEL_ORDER)
        and top_label_share <= 0.30
        and top_semantic_share <= 0.35
        else "HOLD_A7FF14_LABEL_BALANCED_SELECTOR_REPAIR_INSUFFICIENT"
    )
    manifest = {
        "stage": "A7FF-14-LABEL-BALANCED-SELECTOR-REPAIR",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ff13_decision": a7ff13.get("decision", ""),
        "candidate_rows": int(len(clue)),
        "candidate_unique_blueprints": int(clue["blueprint_id"].nunique()) if not clue.empty else 0,
        "selected_count": int(len(selected)),
        "selected_unique_blueprints": int(selected["blueprint_id"].nunique()) if not selected.empty else 0,
        "selected_label_families": label_families,
        "selected_top_label_share": top_label_share,
        "selected_top_semantic_share": top_semantic_share,
        "selected_strict_priority_count": strict_count,
        "target_total": TARGET_TOTAL,
        "label_quota": LABEL_QUOTA,
        "semantic_cap": SEMANTIC_CAP,
        "motif_cap": MOTIF_CAP,
        "skeleton_cap": SKELETON_CAP,
        "uses_may": False,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_a7ff15_balanced_numeric_followup_contract": decision.startswith("PASS_"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    clue.to_csv(RUNTIME / "a7ff14_balanced_candidate_pool.csv", index=False)
    selected.to_csv(RUNTIME / "a7ff14_label_balanced_selected_queue.csv", index=False)
    candidate_label_summary.to_csv(RUNTIME / "a7ff14_candidate_label_summary.csv", index=False)
    selected_label_summary.to_csv(RUNTIME / "a7ff14_selected_label_summary.csv", index=False)
    selected_semantic_summary.to_csv(RUNTIME / "a7ff14_selected_semantic_summary.csv", index=False)
    selected_motif_summary.to_csv(RUNTIME / "a7ff14_selected_motif_summary.csv", index=False)
    write_json(RUNTIME / "a7ff14_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ff14_experiment_record.json",
        {
            "date": manifest["generated_at"],
            "experiment_id": "20260530_a7ff14_label_balanced_selector_repair",
            "objective": "Repair A7FF selector target so raw L0/L1/L3/L5 clue surface is preserved in dry rerank.",
            "status": "completed",
            "mode": "research_governance",
            "inputs": [
                "runtime/a7ff12_company_numeric_probe_shard_*/a7ff12s*_label_response_metrics.csv",
                "runtime/a7ff12_company_numeric_probe_shard_*/a7ff12s*_materialization_metrics.csv",
                "runtime/a7ff13_wave_triage/a7ff13_manifest.json",
            ],
            "parameters": {
                "target_total": TARGET_TOTAL,
                "label_quota": LABEL_QUOTA,
                "semantic_cap": SEMANTIC_CAP,
                "motif_cap": MOTIF_CAP,
                "skeleton_cap": SKELETON_CAP,
                "hard_filters": [
                    "non-L7 only",
                    "premay_all_positive",
                    "lag_ok",
                    "robust_ok",
                    "control_ratio_premay_max < 1.0",
                    "cost2_recent_oriented > 0",
                ],
            },
            "decision": decision,
            "next_action": "A7FF-15 may run balanced numeric follow-up / dry validation only; no formula search is authorized.",
        },
    )

    lines = [
        "# CRYPTO A7FF-14 LABEL-BALANCED SELECTOR REPAIR",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-14 repairs the A7FF selector target by dry-reranking the A7FF-12 numeric clue surface with explicit label-family quotas. It does not generate formulas, execute replay, run search, use May, or authorize alpha proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Candidate Label Surface",
        "",
        md_table(candidate_label_summary, 80),
        "",
        "## Selected Label Surface",
        "",
        md_table(selected_label_summary, 80),
        "",
        "## Selected Semantic Surface",
        "",
        md_table(selected_semantic_summary, 80),
        "",
        "## Selected Motif Surface",
        "",
        md_table(selected_motif_summary, 80),
        "",
        "## Selected Queue",
        "",
        md_table(
            selected[
                [
                    "selector_rank",
                    "selector_tier",
                    "blueprint_id",
                    "label_family",
                    "label_horizon_h",
                    "semantic_pair",
                    "motif",
                    "control_ratio_premay_max",
                    "cost10_recent_oriented",
                    "selector_score",
                ]
            ],
            80,
        ),
        "",
        "## Boundary",
        "",
        "```text",
        "No May is used.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "A7FF-14 only authorizes a follow-up balanced numeric diagnostic contract.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
