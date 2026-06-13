from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = REPO / "runtime" / "a7v3s5_prefiltered_queue_20260613" / "a7v3s5_prefiltered_reward_prequeue.csv"
DEFAULT_REJECTIONS = (
    REPO / "runtime" / "a7v3s6_prefiltered_reward_smoke_aggregate_20260614" / "a7v3s0_reward_rejections_enriched.csv"
)
DEFAULT_RUNTIME = REPO / "runtime" / "a7v3s7_candidate_construction_redesign_20260614"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7V3S7_CANDIDATE_CONSTRUCTION_REDESIGN_20260614.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(frame: pd.DataFrame, max_rows: int = 30) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def numeric(frame: pd.DataFrame, column: str, default: float = np.nan) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def contains_reason(frame: pd.DataFrame, reason: str) -> pd.Series:
    text = frame.get("hard_reject_reasons", pd.Series("", index=frame.index)).fillna("").astype(str)
    return text.str.contains(reason, regex=False)


def pair_motif_key(frame: pd.DataFrame) -> pd.Series:
    return frame.get("semantic_pair", pd.Series("", index=frame.index)).fillna("").astype(str) + "\t" + frame.get(
        "motif", pd.Series("", index=frame.index)
    ).fillna("").astype(str)


def same_family_pair(value: str) -> bool:
    parts = [p for p in str(value).split("|") if p]
    return len(parts) >= 2 and len(set(parts)) == 1


def failure_rules(rejections: pd.DataFrame) -> tuple[pd.DataFrame, set[str], set[str], set[str]]:
    frame = rejections.copy()
    frame["_oos_floor_fail"] = contains_reason(frame, "oos_nonoverlap_floor_not_positive")
    frame["_stress_floor_fail"] = contains_reason(frame, "stress_floor_not_positive")
    frame["_control_fail"] = contains_reason(frame, "oos_control_dominated")
    frame["_lag_stale_fail"] = contains_reason(frame, "oos_lag_stale_dominated")
    frame["_shuffle_fail"] = contains_reason(frame, "oos_shuffle_dominated")
    frame["_train_orientation_fail"] = contains_reason(frame, "train_orientation_no_positive_edge")
    frame["_pair_motif_key"] = pair_motif_key(frame)

    rows = []
    for key, group in frame.groupby(["semantic_pair", "motif"], dropna=False):
        pair, motif = key
        n = len(group)
        payload = {
            "semantic_pair": pair,
            "motif": motif,
            "rows": n,
            "unique_blueprints": group["blueprint_id"].nunique() if "blueprint_id" in group else n,
            "oos_floor_fail_rate": float(group["_oos_floor_fail"].mean()),
            "stress_floor_fail_rate": float(group["_stress_floor_fail"].mean()),
            "control_fail_rate": float(group["_control_fail"].mean()),
            "lag_stale_fail_rate": float(group["_lag_stale_fail"].mean()),
            "shuffle_fail_rate": float(group["_shuffle_fail"].mean()),
            "train_orientation_fail_rate": float(group["_train_orientation_fail"].mean()),
            "max_recent_sortino": float(numeric(group, "recent_sortino").max()),
            "median_min_oos_floor_sortino": float(numeric(group, "min_oos_floor_sortino").median()),
            "median_stress_floor_sortino": float(numeric(group, "stress_floor_sortino").median()),
        }
        if (
            n >= 16
            and payload["oos_floor_fail_rate"] >= 0.95
            and payload["stress_floor_fail_rate"] >= 0.70
            and (payload["control_fail_rate"] >= 0.70 or payload["lag_stale_fail_rate"] >= 0.70)
        ):
            decision = "HARD_BLOCK_A7V3S7"
        elif n >= 12 and payload["oos_floor_fail_rate"] >= 0.90:
            decision = "SOFT_DEPRIORITIZE_A7V3S7"
        else:
            decision = "OBSERVE"
        payload["construction_decision"] = decision
        rows.append(payload)
    summary = pd.DataFrame(rows).sort_values(
        ["construction_decision", "rows", "oos_floor_fail_rate", "control_fail_rate"],
        ascending=[True, False, False, False],
    )
    hard = set(
        summary[summary["construction_decision"].eq("HARD_BLOCK_A7V3S7")]
        .assign(key=lambda x: x["semantic_pair"].astype(str) + "\t" + x["motif"].astype(str))["key"]
        .tolist()
    )
    soft = set(
        summary[summary["construction_decision"].eq("SOFT_DEPRIORITIZE_A7V3S7")]
        .assign(key=lambda x: x["semantic_pair"].astype(str) + "\t" + x["motif"].astype(str))["key"]
        .tolist()
    )
    tested = set(frame.get("blueprint_id", pd.Series(dtype=str)).dropna().astype(str).unique())
    return summary, hard, soft, tested


def score_queue(frame: pd.DataFrame, soft_keys: set[str]) -> pd.DataFrame:
    out = frame.copy()
    for col in ["finite_share", "nonzero_share", "std_value"]:
        out[col] = numeric(out, col, 0).fillna(0)
    out["_pair_motif_key"] = pair_motif_key(out)
    out["_score"] = 0.0
    out["_score"] += out["finite_share"].clip(0, 1) * 2.0
    out["_score"] += out["nonzero_share"].clip(0, 1) * 1.0
    out["_score"] += np.log1p(out["std_value"].clip(lower=0)) / 20.0

    semantic = out.get("semantic_pair", pd.Series("", index=out.index)).fillna("").astype(str)
    motif = out.get("motif", pd.Series("", index=out.index)).fillna("").astype(str)
    primary = out.get("primary_field", pd.Series("", index=out.index)).fillna("").astype(str)
    secondary = out.get("secondary_field", pd.Series("", index=out.index)).fillna("").astype(str)

    out["_score"] += semantic.str.contains("regime", regex=False).astype(float) * 2.5
    out["_score"] += semantic.str.contains("funding_basis", regex=False).astype(float) * 1.5
    out["_score"] += semantic.str.contains("basis", regex=False).astype(float) * 0.8
    out["_score"] += semantic.str.contains("open_interest", regex=False).astype(float) * 0.5
    out["_score"] += motif.str.contains("state_conditioned", regex=False).astype(float) * 3.0
    out["_score"] += motif.isin(["funding_basis_delta_sign", "funding_basis_spread_24h", "oi_flow_delta_rank"]).astype(float) * 2.0
    out["_score"] -= motif.isin(["smooth_mul", "spread_rank", "signed_rank_gate"]).astype(float) * 1.0
    out["_score"] -= semantic.str.contains("liquidity", regex=False).astype(float) * 0.8
    out["_score"] -= out["_pair_motif_key"].isin(soft_keys).astype(float) * 2.0
    out["_score"] -= (primary == secondary).astype(float) * 5.0
    out["_score"] -= semantic.apply(same_family_pair).astype(float) * 4.0
    return out


def bounded_select(
    frame: pd.DataFrame,
    target: int,
    pair_cap: int,
    motif_cap: int,
    skeleton_cap: int,
    lane_cap: int,
) -> pd.DataFrame:
    selected = []
    pair_counts: dict[str, int] = {}
    motif_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    lane_counts: dict[str, int] = {}
    ranked = frame.sort_values(["_score", "finite_share", "nonzero_share", "blueprint_id"], ascending=[False, False, False, True])
    for _, row in ranked.iterrows():
        pair = str(row.get("semantic_pair", ""))
        motif = str(row.get("motif", ""))
        skeleton = str(row.get("skeleton_key", ""))
        lane = str(row.get("a7ls_lane", ""))
        if pair_counts.get(pair, 0) >= pair_cap:
            continue
        if motif_counts.get(motif, 0) >= motif_cap:
            continue
        if skeleton_counts.get(skeleton, 0) >= skeleton_cap:
            continue
        if lane_counts.get(lane, 0) >= lane_cap:
            continue
        selected.append(row)
        pair_counts[pair] = pair_counts.get(pair, 0) + 1
        motif_counts[motif] = motif_counts.get(motif, 0) + 1
        skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1
        lane_counts[lane] = lane_counts.get(lane, 0) + 1
        if len(selected) >= target:
            break
    return pd.DataFrame(selected)


def summary(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=keys + ["count"])
    return frame.groupby(keys, dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)


def main() -> None:
    runtime = DEFAULT_RUNTIME
    runtime.mkdir(parents=True, exist_ok=True)
    queue = pd.read_csv(DEFAULT_QUEUE, low_memory=False)
    rejections = pd.read_csv(DEFAULT_REJECTIONS, low_memory=False)
    rules, hard_keys, soft_keys, tested_blueprints = failure_rules(rejections)
    scored = score_queue(queue, soft_keys)

    scored["_tested_in_a7v3s6"] = scored["blueprint_id"].astype(str).isin(tested_blueprints)
    scored["_hard_block_pair_motif"] = scored["_pair_motif_key"].isin(hard_keys)
    scored["_same_family_pair"] = scored["semantic_pair"].astype(str).apply(same_family_pair)
    scored["_same_primary_secondary"] = scored["primary_field"].astype(str).eq(scored["secondary_field"].astype(str))

    hard_mask = (
        scored["_tested_in_a7v3s6"]
        | scored["_hard_block_pair_motif"]
        | scored["_same_family_pair"]
        | scored["_same_primary_secondary"]
    )
    eligible = scored[~hard_mask].copy()
    selected = bounded_select(eligible, target=1024, pair_cap=48, motif_cap=256, skeleton_cap=4, lane_cap=512)

    drop_cols = [col for col in selected.columns if col.startswith("_")]
    selected.drop(columns=drop_cols, errors="ignore").to_csv(runtime / "a7v3s7_redesigned_reward_prequeue.csv", index=False)
    scored[hard_mask].drop(columns=[col for col in scored.columns if col.startswith("_score")], errors="ignore").to_csv(
        runtime / "a7v3s7_construction_rejected_queue.csv", index=False
    )
    rules.to_csv(runtime / "a7v3s7_pair_motif_failure_rules.csv", index=False)
    summary(selected, ["semantic_pair"]).to_csv(runtime / "a7v3s7_selected_pair_summary.csv", index=False)
    summary(selected, ["motif"]).to_csv(runtime / "a7v3s7_selected_motif_summary.csv", index=False)
    summary(selected, ["semantic_pair", "motif"]).to_csv(runtime / "a7v3s7_selected_pair_motif_summary.csv", index=False)
    pd.DataFrame(
        [
            {"reason": "tested_in_a7v3s6", "count": int(scored["_tested_in_a7v3s6"].sum())},
            {"reason": "hard_block_pair_motif", "count": int(scored["_hard_block_pair_motif"].sum())},
            {"reason": "same_family_pair", "count": int(scored["_same_family_pair"].sum())},
            {"reason": "same_primary_secondary", "count": int(scored["_same_primary_secondary"].sum())},
            {"reason": "eligible_after_construction_filter", "count": int(eligible.shape[0])},
            {"reason": "selected", "count": int(selected.shape[0])},
        ]
    ).to_csv(runtime / "a7v3s7_construction_filter_summary.csv", index=False)

    manifest = {
        "stage": "A7V3S7_CANDIDATE_CONSTRUCTION_REDESIGN",
        "generated_at": now_utc(),
        "decision": "PASS_A7V3S7_REDESIGNED_QUEUE_READY" if selected.shape[0] >= 512 else "HOLD_A7V3S7_QUEUE_TOO_SMALL",
        "input_queue": str(DEFAULT_QUEUE),
        "input_rejections": str(DEFAULT_REJECTIONS),
        "runtime": str(runtime),
        "input_rows": int(queue.shape[0]),
        "tested_blueprint_count": int(len(tested_blueprints)),
        "hard_block_pair_motif_count": int(len(hard_keys)),
        "soft_deprioritize_pair_motif_count": int(len(soft_keys)),
        "eligible_rows": int(eligible.shape[0]),
        "selected_rows": int(selected.shape[0]),
        "selected_semantic_pair_count": int(selected["semantic_pair"].nunique()) if not selected.empty else 0,
        "selected_motif_count": int(selected["motif"].nunique()) if not selected.empty else 0,
        "selected_skeleton_count": int(selected["skeleton_key"].nunique()) if "skeleton_key" in selected else 0,
        "output_queue": str(runtime / "a7v3s7_redesigned_reward_prequeue.csv"),
        "authorizes_smoke_reward": selected.shape[0] >= 512,
        "authorizes_full_reward_wave": False,
        "authorizes_alpha_proof": False,
    }
    write_json(runtime / "a7v3s7_manifest.json", manifest)

    report = DEFAULT_REPORT
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "\n".join(
            [
                "# CRYPTO A7V3S7 Candidate Construction Redesign - 20260614",
                "",
                f"Decision: `{manifest['decision']}`",
                "",
                "A7V3S7 redesigns the pre-reward candidate construction layer using A7V3S6 smoke failures. It does not execute reward and does not authorize alpha proof.",
                "",
                "## Counts",
                "",
                f"- input_rows: `{manifest['input_rows']}`",
                f"- tested_blueprint_count: `{manifest['tested_blueprint_count']}`",
                f"- hard_block_pair_motif_count: `{manifest['hard_block_pair_motif_count']}`",
                f"- soft_deprioritize_pair_motif_count: `{manifest['soft_deprioritize_pair_motif_count']}`",
                f"- eligible_rows: `{manifest['eligible_rows']}`",
                f"- selected_rows: `{manifest['selected_rows']}`",
                f"- selected_semantic_pair_count: `{manifest['selected_semantic_pair_count']}`",
                f"- selected_motif_count: `{manifest['selected_motif_count']}`",
                "",
                "## Construction Filter Summary",
                "",
                md_table(pd.read_csv(runtime / "a7v3s7_construction_filter_summary.csv"), 20),
                "",
                "## Selected Pairs",
                "",
                md_table(pd.read_csv(runtime / "a7v3s7_selected_pair_summary.csv"), 30),
                "",
                "## Selected Motifs",
                "",
                md_table(pd.read_csv(runtime / "a7v3s7_selected_motif_summary.csv"), 20),
                "",
                "## Hard Failure Rules",
                "",
                md_table(rules[rules["construction_decision"].eq("HARD_BLOCK_A7V3S7")], 30),
                "",
                "## Interpretation",
                "",
                "A7V3S7 is stricter than A7V3S5: it removes A7V3S6-tested blueprints, pair/motif patterns with severe OOS/stress/control failure, same-family pairs, and same primary/secondary field constructions. The selected queue is smaller but more diverse and more mechanism-oriented.",
                "",
                "Allowed next: bounded strict reward smoke on `a7v3s7_redesigned_reward_prequeue.csv`.",
                "",
                "Not allowed: full reward wave, alpha proof, shadow, paper, or live.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
