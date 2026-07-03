from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = REPO / "runtime" / "a7shadow3_execution_realism_summary_20260703" / "a7shadow3_execution_accepted.csv"
DEFAULT_SHADOW4 = REPO / "runtime" / "a7shadow4_live_capacity_correlation_r3_20260704"
DEFAULT_RUNTIME = REPO / "runtime" / "a7shadow7_dedup_review_packet_20260704"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7SHADOW7_DEDUP_REVIEW_PACKET_20260704.md"
FIELD_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
OPERATORS = {
    "Abs",
    "Add",
    "CSRank",
    "Decay",
    "Delta",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "Sub",
    "TSRank",
    "ZScore",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def candidate_key(row: pd.Series | dict[str, Any]) -> str:
    return f"{row['blueprint_id']}|h{int(row['horizon_h'])}"


def expression_fields(expression: str) -> set[str]:
    return {
        token
        for token in FIELD_RE.findall(str(expression))
        if token not in OPERATORS and token.lower() not in {"nan", "inf"}
    }


def field_family_counts(expression: str) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for field in expression_fields(expression):
        if "open_interest" in field:
            counts["open_interest"] += 1
        elif "funding" in field:
            counts["funding"] += 1
        elif "premium" in field or "basis" in field:
            counts["premium_basis"] += 1
        else:
            counts["other"] += 1
    return dict(counts)


class UnionFind:
    def __init__(self, nodes: list[str]) -> None:
        self.parent = {node: node for node in nodes}

    def find(self, node: str) -> str:
        parent = self.parent[node]
        if parent != node:
            self.parent[node] = self.find(parent)
        return self.parent[node]

    def union(self, left: str, right: str) -> None:
        root_l = self.find(left)
        root_r = self.find(right)
        if root_l != root_r:
            self.parent[root_r] = root_l


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def metric_summary(cost: pd.DataFrame) -> pd.DataFrame:
    if cost.empty:
        return pd.DataFrame()
    recent = cost[cost["split"].eq("recent_oos_2026JanApr")].copy()
    stress = cost[cost["split"].eq("known_may2026_stress")].copy()
    rows: list[dict[str, Any]] = []
    for (blueprint_id, horizon_h), group in recent.groupby(["blueprint_id", "horizon_h"], dropna=False):
        row: dict[str, Any] = {"blueprint_id": blueprint_id, "horizon_h": int(horizon_h)}
        for cost_bps in [20.0, 30.0]:
            sub = group[group["cost_bps"].astype(float).eq(cost_bps)]
            if not sub.empty:
                row[f"recent_sortino_{int(cost_bps)}bps"] = float(sub["sortino"].astype(float).iloc[0])
                row[f"recent_sharpe_{int(cost_bps)}bps"] = float(sub["sharpe"].astype(float).iloc[0])
                row[f"recent_max_drawdown_{int(cost_bps)}bps"] = float(sub["max_drawdown"].astype(float).iloc[0])
                row[f"recent_avg_turnover_{int(cost_bps)}bps"] = float(sub["avg_turnover"].astype(float).iloc[0])
        sgroup = stress[(stress["blueprint_id"].eq(blueprint_id)) & (stress["horizon_h"].astype(int).eq(int(horizon_h)))]
        for cost_bps in [20.0, 30.0]:
            sub = sgroup[sgroup["cost_bps"].astype(float).eq(cost_bps)]
            if not sub.empty:
                row[f"stress_sortino_{int(cost_bps)}bps"] = float(sub["sortino"].astype(float).iloc[0])
                row[f"stress_sharpe_{int(cost_bps)}bps"] = float(sub["sharpe"].astype(float).iloc[0])
        rows.append(row)
    return pd.DataFrame(rows)


def build(runtime: Path, report: Path, queue_path: Path, shadow4_runtime: Path, signal_threshold: float, return_threshold: float) -> dict[str, Any]:
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    queue = read_csv(queue_path)
    signal_corr = read_csv(shadow4_runtime / "a7shadow4_signal_correlation.csv")
    return_corr = read_csv(shadow4_runtime / "a7shadow4_net_return_correlation.csv")
    cost = read_csv(shadow4_runtime / "a7shadow4_cost_capacity_ladder.csv")
    shadow4_manifest = json.loads((shadow4_runtime / "a7shadow4_manifest.json").read_text(encoding="utf-8"))
    metrics = metric_summary(cost)

    if queue.empty:
        raise SystemExit(f"empty queue: {queue_path}")
    candidates = queue.drop_duplicates(["blueprint_id", "expression", "horizon_h"]).copy()
    candidates["candidate_key"] = candidates.apply(candidate_key, axis=1)
    candidates = candidates.merge(metrics, on=["blueprint_id", "horizon_h"], how="left")
    candidates["dedup_score"] = candidates["recent_sortino_30bps"].fillna(candidates["recent_sortino_20bps"]).fillna(-np.inf)
    candidates["field_family_counts"] = candidates["expression"].map(lambda expr: json.dumps(field_family_counts(expr), sort_keys=True))

    keys = candidates["candidate_key"].tolist()
    uf = UnionFind(keys)
    edges: list[dict[str, Any]] = []

    for expression, group in candidates.groupby("expression", dropna=False):
        group_keys = group["candidate_key"].tolist()
        if len(group_keys) > 1:
            for left in group_keys:
                for right in group_keys:
                    if left >= right:
                        continue
                    uf.union(left, right)
                    edges.append({"left": left, "right": right, "reason": "same_expression", "value": 1.0, "threshold": 1.0})

    for _, row in signal_corr.iterrows():
        value = float(row["signal_corr"]) if pd.notna(row["signal_corr"]) else np.nan
        if np.isfinite(value) and abs(value) > signal_threshold:
            left = str(row["left"])
            right = str(row["right"])
            if left in uf.parent and right in uf.parent:
                uf.union(left, right)
                edges.append({"left": left, "right": right, "reason": "signal_corr", "value": value, "threshold": signal_threshold})

    recent_ret = return_corr[return_corr["split"].eq("recent_oos_2026JanApr")].copy()
    for _, row in recent_ret.iterrows():
        value = float(row["net_return_corr"]) if pd.notna(row["net_return_corr"]) else np.nan
        if np.isfinite(value) and abs(value) > return_threshold:
            left = str(row["left"])
            right = str(row["right"])
            if left in uf.parent and right in uf.parent:
                uf.union(left, right)
                edges.append({"left": left, "right": right, "reason": "recent_net_return_corr", "value": value, "threshold": return_threshold})

    root_to_members: dict[str, list[str]] = defaultdict(list)
    for key in keys:
        root_to_members[uf.find(key)].append(key)
    root_to_cluster = {root: f"a7shadow7_cluster_{idx:03d}" for idx, root in enumerate(sorted(root_to_members))}
    candidates["overlap_cluster_id"] = candidates["candidate_key"].map(lambda key: root_to_cluster[uf.find(key)])

    selected_rows: list[pd.Series] = []
    rejected_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    for cluster_id, group in candidates.groupby("overlap_cluster_id"):
        ranked = group.sort_values(["dedup_score", "recent_sortino_20bps"], ascending=False, na_position="last")
        selected = ranked.iloc[0]
        selected_rows.append(selected)
        component_rows.append(
            {
                "overlap_cluster_id": cluster_id,
                "member_count": int(group.shape[0]),
                "selected_key": selected["candidate_key"],
                "selected_score": float(selected["dedup_score"]) if np.isfinite(selected["dedup_score"]) else np.nan,
                "members": "|".join(group["candidate_key"].tolist()),
            }
        )
        for _, rejected in ranked.iloc[1:].iterrows():
            rejected_rows.append(
                {
                    "candidate_key": rejected["candidate_key"],
                    "blueprint_id": rejected["blueprint_id"],
                    "horizon_h": int(rejected["horizon_h"]),
                    "expression": rejected["expression"],
                    "overlap_cluster_id": cluster_id,
                    "selected_key": selected["candidate_key"],
                    "reject_reason": "overlap_cluster_non_representative",
                    "dedup_score": rejected["dedup_score"],
                    "selected_score": selected["dedup_score"],
                }
            )

    selected_packet = pd.DataFrame(selected_rows).sort_values("dedup_score", ascending=False)
    rejected = pd.DataFrame(rejected_rows)
    components = pd.DataFrame(component_rows)
    edge_frame = pd.DataFrame(edges)

    selected_keys = selected_packet["candidate_key"].tolist()
    selected_signal = signal_corr[signal_corr["left"].isin(selected_keys) & signal_corr["right"].isin(selected_keys)].copy()
    selected_return = recent_ret[recent_ret["left"].isin(selected_keys) & recent_ret["right"].isin(selected_keys)].copy()
    max_selected_signal_corr = float(selected_signal["signal_corr"].abs().max()) if not selected_signal.empty else 0.0
    max_selected_recent_return_corr = float(selected_return["net_return_corr"].abs().max()) if not selected_return.empty else 0.0

    selected_packet.to_csv(runtime / "a7shadow7_selected_review_packet.csv", index=False)
    rejected.to_csv(runtime / "a7shadow7_overlap_rejections.csv", index=False)
    components.to_csv(runtime / "a7shadow7_overlap_components.csv", index=False)
    edge_frame.to_csv(runtime / "a7shadow7_overlap_edges.csv", index=False)

    family_counter: Counter[str] = Counter()
    for expression in selected_packet["expression"].astype(str):
        family_counter.update(field_family_counts(expression))

    warnings: list[str] = []
    blockers: list[str] = []
    if selected_packet.shape[0] < 2:
        blockers.append("selected_review_packet_lt_2")
    if max_selected_signal_corr > signal_threshold:
        blockers.append("selected_signal_corr_still_above_threshold")
    if max_selected_recent_return_corr > return_threshold:
        blockers.append("selected_recent_return_corr_still_above_threshold")
    if family_counter.get("open_interest", 0) >= 2:
        warnings.append("selected_packet_open_interest_concentrated")
    if selected_packet.shape[0] < 4:
        warnings.append("selected_packet_too_small_for_book")

    decision = "PASS_A7SHADOW7_DEDUP_REVIEW_PACKET_BUILT" if not blockers else "HOLD_A7SHADOW7_DEDUP_REVIEW_PACKET_BLOCKED"
    manifest = {
        "stage": "A7SHADOW-7",
        "generated_at": now_utc(),
        "decision": decision,
        "input_queue": str(queue_path),
        "input_shadow4_runtime": str(shadow4_runtime),
        "input_shadow4_decision": shadow4_manifest.get("decision"),
        "input_candidate_rows": int(candidates.shape[0]),
        "overlap_cluster_count": int(components.shape[0]),
        "selected_count": int(selected_packet.shape[0]),
        "rejected_overlap_variant_count": int(rejected.shape[0]),
        "max_selected_abs_signal_corr": max_selected_signal_corr,
        "max_selected_abs_recent_net_return_corr": max_selected_recent_return_corr,
        "selected_family_counts": dict(family_counter),
        "blockers": blockers,
        "warnings": warnings,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_book": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_live_adapter_probe": decision.startswith("PASS"),
        "next_required": [
            "Run A7LIVE-0 forward-locked adapter probe on the selected review packet.",
            "Do not treat this packet as a book; selected_count remains small and family concentration remains.",
            "Use the overlap rejection map as memory for the next family-diversified search.",
        ],
    }
    write_json(runtime / "a7shadow7_manifest.json", manifest)

    lines = [
        "# CRYPTO A7SHADOW7 Dedup Review Packet",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7SHADOW-7 converts the A7SHADOW-4 R3 engineering packet into a deduplicated review packet. It does not run search, replay, alpha proof, shadow, paper, or live trading.",
        "",
        "## Counts",
        "",
        f"- input_candidate_rows: `{manifest['input_candidate_rows']}`",
        f"- overlap_cluster_count: `{manifest['overlap_cluster_count']}`",
        f"- selected_count: `{manifest['selected_count']}`",
        f"- rejected_overlap_variant_count: `{manifest['rejected_overlap_variant_count']}`",
        f"- max_selected_abs_signal_corr: `{manifest['max_selected_abs_signal_corr']}`",
        f"- max_selected_abs_recent_net_return_corr: `{manifest['max_selected_abs_recent_net_return_corr']}`",
        f"- selected_family_counts: `{json.dumps(manifest['selected_family_counts'], sort_keys=True)}`",
        "",
        "## Selected Review Packet",
        "",
        md_table(selected_packet, 20),
        "",
        "## Overlap Components",
        "",
        md_table(components, 40),
        "",
        "## Overlap Rejections",
        "",
        md_table(rejected, 40),
        "",
        "## Interpretation",
        "",
        "The hard field-coverage blocker is repaired upstream, but this packet is intentionally small after overlap collapse. It is suitable for forward-locked adapter probing and search-memory feedback, not for book construction.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", default=str(DEFAULT_RUNTIME))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE))
    parser.add_argument("--shadow4-runtime", default=str(DEFAULT_SHADOW4))
    parser.add_argument("--signal-threshold", type=float, default=0.85)
    parser.add_argument("--return-threshold", type=float, default=0.85)
    args = parser.parse_args()
    build(
        Path(args.runtime),
        Path(args.report),
        Path(args.queue),
        Path(args.shadow4_runtime),
        args.signal_threshold,
        args.return_threshold,
    )


if __name__ == "__main__":
    main()
