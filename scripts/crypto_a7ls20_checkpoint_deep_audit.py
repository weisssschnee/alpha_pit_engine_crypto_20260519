from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO / "runtime" / "a7ls19_checkpoint_arbitration"
RUNTIME = REPO / "runtime" / "a7ls20_checkpoint_deep_audit"
REPORT = REPO / "reports" / "CRYPTO_A7LS20_CHECKPOINT_DEEP_AUDIT_20260607.md"

MANIFEST_IN = INPUT_DIR / "a7ls19_manifest.json"
QUEUE_IN = INPUT_DIR / "a7ls19_checkpoint_queue.csv"

TARGET_MARGINAL_QUEUE = 48
MIN_MARGINAL_QUEUE = 24
MAX_BASIS_PREMIUM_COUNT = 24
MAX_L5_COUNT = 32
MAX_SEMANTIC_PAIR_COUNT = 5
MAX_SKELETON_COUNT = 4
MAX_PAIRWISE_PROXY_CORR = 0.92

SOURCE_TOKENS = [
    "basis_premium_like",
    "price_like",
    "liquidity_like",
    "volatility_like",
    "positioning_like",
    "open_interest_like",
    "taker_flow_like",
    "funding_state_like",
    "listing_age_like",
    "regime_state",
]

SPLITS = ["train_2024", "validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]


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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```csv\n" + view.to_csv(index=False) + "```"


def to_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def add_deep_metrics(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "control_ratio_premay_max",
        "one_bar_lag_recent_oriented",
        "robust_median_tstat_floor",
        "robust_min_tstat_floor",
        "cost2_recent_oriented",
        "cost5_recent_oriented",
        "cost10_recent_oriented",
        "score_no_may",
        "finite_share",
        "nonzero_share",
        "label_horizon_h",
        "avg_n_obs_recent",
    ]
    for split in SPLITS:
        numeric_cols.extend(
            [
                f"{split}_n",
                f"{split}_mean_spread",
                f"{split}_tstat",
                f"{split}_nonoverlap_median_tstat",
                f"{split}_nonoverlap_min_tstat",
                f"{split}_positive_rate",
            ]
        )
    out = to_numeric(df, numeric_cols)
    out["contains_basis_premium"] = out["semantic_pair"].astype(str).str.contains("basis_premium_like", na=False)
    out["is_l5"] = out["label_family"].astype(str).eq("L5_vol_adjusted_return")
    for token in SOURCE_TOKENS:
        out[f"contains_{token}"] = out["semantic_pair"].astype(str).str.contains(token, na=False)

    split_means = [f"{split}_mean_spread" for split in SPLITS if f"{split}_mean_spread" in out.columns]
    split_tstats = [f"{split}_tstat" for split in SPLITS if f"{split}_tstat" in out.columns]
    split_nonoverlap = [f"{split}_nonoverlap_min_tstat" for split in SPLITS if f"{split}_nonoverlap_min_tstat" in out.columns]
    split_positive = [f"{split}_positive_rate" for split in SPLITS if f"{split}_positive_rate" in out.columns]

    out["split_mean_floor"] = out[split_means].min(axis=1, skipna=True)
    out["split_mean_median"] = out[split_means].median(axis=1, skipna=True)
    out["split_tstat_floor"] = out[split_tstats].min(axis=1, skipna=True)
    out["split_tstat_median"] = out[split_tstats].median(axis=1, skipna=True)
    out["split_nonoverlap_floor"] = out[split_nonoverlap].min(axis=1, skipna=True)
    out["split_positive_rate_floor"] = out[split_positive].min(axis=1, skipna=True)
    out["split_positive_rate_median"] = out[split_positive].median(axis=1, skipna=True)
    out["cost_floor"] = out[["cost2_recent_oriented", "cost5_recent_oriented", "cost10_recent_oriented"]].min(axis=1, skipna=True)
    out["control_margin"] = 1.0 - out["control_ratio_premay_max"]
    out["non_l5_bonus"] = (~out["is_l5"]).astype(float)
    out["non_basis_bonus"] = (~out["contains_basis_premium"]).astype(float)
    out["a7ls20_deep_score"] = (
        out["score_no_may"].fillna(0.0)
        + out["control_margin"].clip(lower=0).fillna(0.0) * 120.0
        + out["cost_floor"].clip(lower=0).fillna(0.0) * 500.0
        + out["one_bar_lag_recent_oriented"].clip(lower=0).fillna(0.0) * 300.0
        + out["robust_min_tstat_floor"].clip(lower=0).fillna(0.0) * 25.0
        + out["non_l5_bonus"] * 70.0
        + out["non_basis_bonus"] * 55.0
    )
    return out


def vector_columns(df: pd.DataFrame) -> list[str]:
    cols: list[str] = [
        "control_margin",
        "cost_floor",
        "one_bar_lag_recent_oriented",
        "robust_min_tstat_floor",
        "split_mean_floor",
        "split_mean_median",
        "split_tstat_floor",
        "split_tstat_median",
        "split_nonoverlap_floor",
        "split_positive_rate_floor",
        "finite_share",
        "nonzero_share",
    ]
    for split in SPLITS:
        cols.extend(
            [
                f"{split}_mean_spread",
                f"{split}_tstat",
                f"{split}_nonoverlap_min_tstat",
                f"{split}_positive_rate",
            ]
        )
    return [col for col in cols if col in df.columns]


def normalize_frame(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    z = df[cols].copy()
    for col in cols:
        values = pd.to_numeric(z[col], errors="coerce")
        med = values.median(skipna=True)
        values = values.fillna(med if pd.notna(med) else 0.0)
        std = values.std(ddof=0)
        if not std or not math.isfinite(std):
            z[col] = 0.0
        else:
            z[col] = (values - values.mean()) / std
    return z


def row_corr(a: pd.Series, b: pd.Series) -> float:
    av = a.astype(float)
    bv = b.astype(float)
    if av.std(ddof=0) == 0 or bv.std(ddof=0) == 0:
        return 0.0
    corr = float(av.corr(bv))
    return 0.0 if not math.isfinite(corr) else corr


def build_marginal_queue(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = vector_columns(df)
    z = normalize_frame(df, cols)
    ordered = df.sort_values(["a7ls20_deep_score", "score_no_may", "cost_floor"], ascending=[False, False, False]).copy()

    selected_indices: list[int] = []
    reject_rows: list[dict[str, Any]] = []
    semantic_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    basis_count = 0
    l5_count = 0

    for idx, row in ordered.iterrows():
        if len(selected_indices) >= TARGET_MARGINAL_QUEUE:
            break
        semantic = str(row.get("semantic_pair", ""))
        skeleton = str(row.get("skeleton_key", ""))
        is_basis = bool(row.get("contains_basis_premium", False))
        is_l5 = bool(row.get("is_l5", False))
        reasons: list[str] = []

        if is_basis and basis_count >= MAX_BASIS_PREMIUM_COUNT:
            reasons.append("basis_premium_marginal_cap")
        if is_l5 and l5_count >= MAX_L5_COUNT:
            reasons.append("l5_label_marginal_cap")
        if semantic_counts.get(semantic, 0) >= MAX_SEMANTIC_PAIR_COUNT:
            reasons.append("semantic_pair_marginal_cap")
        if skeleton_counts.get(skeleton, 0) >= MAX_SKELETON_COUNT:
            reasons.append("skeleton_marginal_cap")

        max_corr = 0.0
        if not reasons and selected_indices:
            current = z.loc[idx, cols]
            max_corr = max(abs(row_corr(current, z.loc[sel, cols])) for sel in selected_indices)
            if max_corr > MAX_PAIRWISE_PROXY_CORR:
                reasons.append("proxy_corr_cap")

        if reasons:
            reject_rows.append(
                {
                    "blueprint_id": row.get("blueprint_id"),
                    "semantic_pair": semantic,
                    "skeleton_key": skeleton,
                    "label_family": row.get("label_family"),
                    "a7ls20_deep_score": row.get("a7ls20_deep_score"),
                    "max_selected_proxy_corr": max_corr,
                    "decision": "MARGINAL_REJECT",
                    "reason": ";".join(reasons),
                }
            )
            continue

        selected_indices.append(idx)
        semantic_counts[semantic] = semantic_counts.get(semantic, 0) + 1
        skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1
        if is_basis:
            basis_count += 1
        if is_l5:
            l5_count += 1

    queue = ordered.loc[selected_indices].copy()
    queue.insert(0, "a7ls20_rank", range(1, len(queue) + 1))
    queue["a7ls20_decision"] = "A7LS20_MARGINAL_QUEUE"
    rejects = pd.DataFrame(reject_rows)
    return queue, rejects


def counts(df: pd.DataFrame, col: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[col, "count", "share"])
    out = df.groupby(col, dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    out["share"] = out["count"] / max(1, len(df))
    return out


def source_counts(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for token in SOURCE_TOKENS:
        col = f"contains_{token}"
        rows.append(
            {
                "source_token": token,
                "count": int(df[col].sum()) if col in df else 0,
                "share": float(df[col].sum() / max(1, len(df))) if col in df else 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values("count", ascending=False)


def concentration_summary(df: pd.DataFrame, prefix: str) -> dict[str, Any]:
    return {
        f"{prefix}_count": int(len(df)),
        f"{prefix}_basis_premium_count": int(df["contains_basis_premium"].sum()) if not df.empty else 0,
        f"{prefix}_basis_premium_share": float(df["contains_basis_premium"].sum() / max(1, len(df))) if not df.empty else 0.0,
        f"{prefix}_l5_count": int(df["is_l5"].sum()) if not df.empty else 0,
        f"{prefix}_l5_share": float(df["is_l5"].sum() / max(1, len(df))) if not df.empty else 0.0,
        f"{prefix}_semantic_pair_count": int(df["semantic_pair"].nunique()) if not df.empty else 0,
        f"{prefix}_skeleton_count": int(df["skeleton_key"].nunique()) if not df.empty else 0,
        f"{prefix}_max_semantic_pair_share": float(counts(df, "semantic_pair")["share"].max()) if not df.empty else 0.0,
        f"{prefix}_max_skeleton_share": float(counts(df, "skeleton_key")["share"].max()) if not df.empty else 0.0,
    }


def main() -> None:
    manifest_in = read_json(MANIFEST_IN)
    if manifest_in.get("decision") != "PASS_A7LS19_DIVERSIFIED_CHECKPOINT_QUEUE_READY_FOR_A7LS20":
        raise SystemExit(f"A7LS19 not ready: {manifest_in.get('decision')}")
    df = pd.read_csv(QUEUE_IN)
    df = add_deep_metrics(df)
    marginal, rejects = build_marginal_queue(df)

    RUNTIME.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUNTIME / "a7ls20_candidate_deep_metrics.csv", index=False)
    marginal.to_csv(RUNTIME / "a7ls20_marginal_candidate_queue.csv", index=False)
    rejects.to_csv(RUNTIME / "a7ls20_marginal_reject_audit.csv", index=False)

    checkpoint_label = counts(df, "label_family")
    marginal_label = counts(marginal, "label_family")
    checkpoint_semantic = counts(df, "semantic_pair")
    marginal_semantic = counts(marginal, "semantic_pair")
    checkpoint_skeleton = counts(df, "skeleton_key")
    marginal_skeleton = counts(marginal, "skeleton_key")
    checkpoint_source = source_counts(df)
    marginal_source = source_counts(marginal)
    reject_summary = counts(rejects, "reason") if not rejects.empty else pd.DataFrame(columns=["reason", "count", "share"])

    checkpoint_label.to_csv(RUNTIME / "a7ls20_checkpoint_label_distribution.csv", index=False)
    marginal_label.to_csv(RUNTIME / "a7ls20_marginal_label_distribution.csv", index=False)
    checkpoint_semantic.to_csv(RUNTIME / "a7ls20_checkpoint_semantic_pair_distribution.csv", index=False)
    marginal_semantic.to_csv(RUNTIME / "a7ls20_marginal_semantic_pair_distribution.csv", index=False)
    checkpoint_skeleton.to_csv(RUNTIME / "a7ls20_checkpoint_skeleton_distribution.csv", index=False)
    marginal_skeleton.to_csv(RUNTIME / "a7ls20_marginal_skeleton_distribution.csv", index=False)
    checkpoint_source.to_csv(RUNTIME / "a7ls20_checkpoint_source_distribution.csv", index=False)
    marginal_source.to_csv(RUNTIME / "a7ls20_marginal_source_distribution.csv", index=False)
    reject_summary.to_csv(RUNTIME / "a7ls20_marginal_reject_summary.csv", index=False)

    top_cols = [
        "a7ls20_rank",
        "blueprint_id",
        "semantic_pair",
        "motif",
        "label_family",
        "label_horizon_h",
        "control_ratio_premay_max",
        "cost10_recent_oriented",
        "one_bar_lag_recent_oriented",
        "robust_min_tstat_floor",
        "split_tstat_floor",
        "split_positive_rate_floor",
        "a7ls20_deep_score",
        "expression",
    ]
    top_cols = [col for col in top_cols if col in marginal.columns]
    marginal[top_cols].head(80).to_csv(RUNTIME / "a7ls20_top_marginal_candidates.csv", index=False)

    manifest = {
        "stage": "A7LS-20",
        "generated_at": now_utc(),
        "decision": "",
        "blockers": [],
        "warnings": [],
        "input_stage": "A7LS-19",
        "input_checkpoint_count": int(len(df)),
        "target_marginal_queue": TARGET_MARGINAL_QUEUE,
        "marginal_queue_count": int(len(marginal)),
        "uses_may": False,
        "executes_search": False,
        "executes_new_replay": False,
        "deep_audit_type": "checkpoint_metric_deep_audit_and_marginal_contribution_proxy",
        "authorizes_a7ls21_company_deep_replay_packet": False,
        "authorizes_formula_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        **concentration_summary(df, "checkpoint"),
        **concentration_summary(marginal, "marginal"),
    }

    blockers: list[str] = []
    warnings: list[str] = []
    if len(marginal) < MIN_MARGINAL_QUEUE:
        blockers.append("marginal_queue_too_small")
    if manifest["marginal_basis_premium_share"] > 0.55:
        blockers.append("marginal_basis_premium_dominant")
    elif manifest["marginal_basis_premium_share"] > 0.45:
        warnings.append("marginal_basis_premium_high")
    if manifest["marginal_l5_share"] > 0.75:
        warnings.append("marginal_l5_label_high")
    if manifest["marginal_max_semantic_pair_share"] > 0.18:
        blockers.append("marginal_semantic_pair_concentration")
    if manifest["marginal_max_skeleton_share"] > 0.14:
        blockers.append("marginal_skeleton_concentration")

    decision = (
        "PASS_A7LS20_MARGINAL_QUEUE_READY_FOR_A7LS21_DEEP_REPLAY_PACKET"
        if not blockers
        else "HOLD_A7LS20_MARGINAL_AUDIT_BLOCKED"
    )
    manifest["decision"] = decision
    manifest["blockers"] = blockers
    manifest["warnings"] = warnings
    manifest["authorizes_a7ls21_company_deep_replay_packet"] = decision.startswith("PASS_")
    write_json(RUNTIME / "a7ls20_manifest.json", manifest)
    write_json(RUNTIME / "a7ls20_decision_record.json", manifest)

    report_lines = [
        "# CRYPTO A7LS20 CHECKPOINT DEEP AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Interpretation",
        "",
        "A7LS20 does not run new search or new replay. It deep-audits the A7LS19 checkpoint metrics and builds a marginal-contribution proxy queue for the next replay packet.",
        "",
        "The marginal queue is deliberately stricter than A7LS19: it caps basis/premium, L5, semantic pair, skeleton, and metric-vector proxy similarity.",
        "",
        "## Checkpoint Source Distribution",
        "",
        md_table(checkpoint_source, 40),
        "",
        "## Marginal Source Distribution",
        "",
        md_table(marginal_source, 40),
        "",
        "## Marginal Label Distribution",
        "",
        md_table(marginal_label, 20),
        "",
        "## Marginal Semantic Pair Distribution",
        "",
        md_table(marginal_semantic, 50),
        "",
        "## Marginal Reject Summary",
        "",
        md_table(reject_summary, 50),
        "",
        "## Top Marginal Candidates",
        "",
        md_table(marginal[top_cols].head(50), 50),
        "",
        "## Authorization",
        "",
        "- A7LS21 company deep replay packet: authorized only if decision is PASS.",
        "- New formula search: not authorized.",
        "- Alpha proof / shadow / paper / live: not authorized.",
        "",
    ]
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
