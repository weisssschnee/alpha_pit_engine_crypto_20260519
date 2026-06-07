from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260607"
STAGE = "A7LS-21"

RESULT_ROOT = Path(
    r"G:\AlphaFactory_CryptoData\research_runtime\a7ls21_company_deep_replay_20260607"
)
OUT_DIR = REPO / "runtime" / "a7ls21_company_deep_replay_aggregate"
REPORT = REPO / "reports" / f"CRYPTO_A7LS21_COMPANY_DEEP_REPLAY_AGGREGATE_{DATE}.md"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_csv_optional(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    shard_root = RESULT_ROOT / "shards"
    if not shard_root.exists():
        raise FileNotFoundError(f"missing shard root: {shard_root}")

    shard_rows: list[dict] = []
    decision_frames: list[pd.DataFrame] = []
    selected_frames: list[pd.DataFrame] = []
    portfolio_frames: list[pd.DataFrame] = []
    label_frames: list[pd.DataFrame] = []

    for shard_dir in sorted(p for p in shard_root.iterdir() if p.is_dir()):
        shard_id = shard_dir.name
        manifest_files = sorted(shard_dir.glob(f"a7ls21_{shard_id}_manifest.json"))
        if not manifest_files:
            shard_rows.append(
                {
                    "shard_id": shard_id,
                    "manifest_found": False,
                    "decision": "MISSING_MANIFEST",
                }
            )
            continue

        manifest = read_json(manifest_files[0])
        row = {
            "shard_id": shard_id,
            "manifest_found": True,
            "decision": manifest.get("decision"),
            "blockers": "|".join(manifest.get("blockers", [])),
            "input_blueprint_count": manifest.get("input_blueprint_count", 0),
            "materialized_activity_ok_count": manifest.get("materialized_activity_ok_count", 0),
            "label_response_rows": manifest.get("label_response_rows", 0),
            "non_l7_numeric_clue_rows": manifest.get("non_l7_numeric_clue_rows", 0),
            "rank_label_diagnostic_clue_rows": manifest.get("rank_label_diagnostic_clue_rows", 0),
            "portfolio_queue_count": manifest.get("portfolio_queue_count", 0),
            "selected_portfolio_queue_count": manifest.get("selected_portfolio_queue_count", 0),
            "uses_may": bool(manifest.get("uses_may", False)),
        }
        shard_rows.append(row)

        decision = read_csv_optional(shard_dir / f"a7ls21_{shard_id}_decision_counts.csv")
        if not decision.empty:
            decision.insert(0, "shard_id", shard_id)
            decision_frames.append(decision)

        selected = read_csv_optional(shard_dir / f"a7ls21_{shard_id}_selected_portfolio_queue.csv")
        if not selected.empty:
            selected.insert(0, "shard_id", shard_id)
            selected_frames.append(selected)

        portfolio = read_csv_optional(shard_dir / f"a7ls21_{shard_id}_portfolio_marginal_proxy.csv")
        if not portfolio.empty:
            portfolio.insert(0, "shard_id", shard_id)
            portfolio_frames.append(portfolio)

        label_response = read_csv_optional(shard_dir / f"a7ls21_{shard_id}_label_response_metrics.csv")
        if not label_response.empty:
            label_response.insert(0, "shard_id", shard_id)
            label_frames.append(label_response)

    shard_summary = pd.DataFrame(shard_rows).sort_values("shard_id")
    shard_summary.to_csv(OUT_DIR / "a7ls21_shard_summary.csv", index=False)

    decisions = pd.concat(decision_frames, ignore_index=True) if decision_frames else pd.DataFrame()
    if not decisions.empty:
        decisions.to_csv(OUT_DIR / "a7ls21_decision_counts_by_shard.csv", index=False)
        decision_total = (
            decisions.groupby(["decision", "label_family"], dropna=False)["count"]
            .sum()
            .reset_index()
            .sort_values(["decision", "label_family"])
        )
    else:
        decision_total = pd.DataFrame(columns=["decision", "label_family", "count"])
    decision_total.to_csv(OUT_DIR / "a7ls21_decision_counts_total.csv", index=False)

    selected_all = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    if not selected_all.empty:
        selected_all.to_csv(OUT_DIR / "a7ls21_selected_portfolio_queue_all.csv", index=False)

    portfolio_all = pd.concat(portfolio_frames, ignore_index=True) if portfolio_frames else pd.DataFrame()
    if not portfolio_all.empty:
        portfolio_all.to_csv(OUT_DIR / "a7ls21_portfolio_marginal_queue_all.csv", index=False)

    label_all = pd.concat(label_frames, ignore_index=True) if label_frames else pd.DataFrame()
    if not label_all.empty:
        label_all.to_csv(OUT_DIR / "a7ls21_label_response_metrics_all.csv", index=False)

    total_shards = int(len(shard_summary))
    completed_shards = int(shard_summary["manifest_found"].sum()) if not shard_summary.empty else 0
    pass_shards = int(shard_summary["decision"].fillna("").str.startswith("PASS_").sum())
    hold_shards = int(shard_summary["decision"].fillna("").str.startswith("HOLD_").sum())
    uses_may_any = bool(shard_summary.get("uses_may", pd.Series(dtype=bool)).fillna(False).any())
    selected_count = int(shard_summary["selected_portfolio_queue_count"].fillna(0).sum())
    non_l7_count = int(shard_summary["non_l7_numeric_clue_rows"].fillna(0).sum())
    rank_l7_count = int(shard_summary["rank_label_diagnostic_clue_rows"].fillna(0).sum())
    materialized_count = int(shard_summary["materialized_activity_ok_count"].fillna(0).sum())
    input_count = int(shard_summary["input_blueprint_count"].fillna(0).sum())

    selected_family_count = 0
    selected_semantic_pair_count = 0
    selected_skeleton_count = 0
    top_semantic_pair_share = None
    top_label_family_share = None
    top_motif_share = None
    if not selected_all.empty:
        selected_family_count = int(selected_all["label_family"].nunique(dropna=True))
        selected_semantic_pair_count = int(selected_all["semantic_pair"].nunique(dropna=True))
        selected_skeleton_count = int(selected_all["skeleton_key"].nunique(dropna=True))
        top_semantic_pair_share = float(selected_all["semantic_pair"].value_counts(normalize=True).iloc[0])
        top_label_family_share = float(selected_all["label_family"].value_counts(normalize=True).iloc[0])
        top_motif_share = float(selected_all["motif"].value_counts(normalize=True).iloc[0])

        selected_all.groupby(["semantic_pair", "motif", "label_family"], dropna=False).size().reset_index(
            name="selected_count"
        ).sort_values("selected_count", ascending=False).to_csv(
            OUT_DIR / "a7ls21_selected_family_summary.csv", index=False
        )

    # This aggregate remains a numeric clue gate, not a proof gate. PASS means the
    # company runner produced a non-empty, non-L7, multi-shard queue that can move
    # to attribution/promotion triage.
    blockers: list[str] = []
    if completed_shards < 4:
        blockers.append("missing_shard_manifest")
    if input_count < 48:
        blockers.append("input_queue_incomplete")
    if materialized_count < input_count:
        blockers.append("materialization_dropoff")
    if non_l7_count <= 0:
        blockers.append("no_non_l7_numeric_clues")
    if selected_count < 8:
        blockers.append("aggregate_selected_queue_lt_8")
    if selected_semantic_pair_count < 4:
        blockers.append("selected_semantic_pair_count_lt_4")
    if selected_skeleton_count < 8:
        blockers.append("selected_skeleton_count_lt_8")
    if uses_may_any:
        blockers.append("may_usage_detected")

    if blockers:
        decision = "HOLD_A7LS21_COMPANY_DEEP_REPLAY_AGGREGATE_INSUFFICIENT"
        next_authorized = ["A7LS21R aggregate failure attribution / queue repair"]
    else:
        decision = "PASS_A7LS21_COMPANY_DEEP_REPLAY_AGGREGATE_READY_FOR_A7LS22"
        next_authorized = ["A7LS22 clue attribution / promotion triage"]

    manifest = {
        "stage": "A7LS-21",
        "decision": decision,
        "blockers": blockers,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "result_root": str(RESULT_ROOT),
        "total_shards": total_shards,
        "completed_shards": completed_shards,
        "pass_shards": pass_shards,
        "hold_shards": hold_shards,
        "input_blueprint_count": input_count,
        "materialized_activity_ok_count": materialized_count,
        "non_l7_numeric_clue_rows": non_l7_count,
        "rank_label_diagnostic_clue_rows": rank_l7_count,
        "aggregate_selected_portfolio_queue_count": selected_count,
        "selected_label_family_count": selected_family_count,
        "selected_semantic_pair_count": selected_semantic_pair_count,
        "selected_skeleton_count": selected_skeleton_count,
        "top_semantic_pair_share": top_semantic_pair_share,
        "top_label_family_share": top_label_family_share,
        "top_motif_share": top_motif_share,
        "uses_may": uses_may_any,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_authorized": next_authorized,
    }
    write_json(OUT_DIR / "a7ls21_manifest.json", manifest)

    auth = {
        "authorized": next_authorized,
        "not_authorized": [
            "formula search",
            "large search",
            "alpha proof",
            "shadow",
            "paper",
            "live",
        ],
    }
    write_json(OUT_DIR / "a7ls21_authorization_matrix.json", auth)

    report_lines = [
        f"# CRYPTO A7LS-21 Company Deep Replay Aggregate ({DATE})",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        f"- shards completed: {completed_shards} / {total_shards}",
        f"- pass shards: {pass_shards}",
        f"- hold shards: {hold_shards}",
        f"- input blueprints: {input_count}",
        f"- materialized activity-ok: {materialized_count}",
        f"- non-L7 numeric clue rows: {non_l7_count}",
        f"- L7 ranked-label diagnostic clue rows: {rank_l7_count}",
        f"- aggregate selected portfolio queue: {selected_count}",
        f"- selected semantic pairs: {selected_semantic_pair_count}",
        f"- selected skeletons: {selected_skeleton_count}",
        f"- top semantic pair share: {top_semantic_pair_share if top_semantic_pair_share is not None else 'n/a'}",
        "",
        "## Boundaries",
        "",
        "- May was not used.",
        "- This stage executed numeric deep replay only.",
        "- It does not authorize formula search, alpha proof, shadow, paper, or live.",
        "",
        "## Shards",
        "",
        shard_summary.to_markdown(index=False),
        "",
    ]

    if blockers:
        report_lines.extend(["## Blockers", "", *[f"- {b}" for b in blockers], ""])
    else:
        report_lines.extend(
            [
                "## Next",
                "",
                "- A7LS-22 clue attribution / promotion triage is authorized as a diagnostic stage.",
                "- Search execution remains blocked.",
                "",
            ]
        )

    REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
