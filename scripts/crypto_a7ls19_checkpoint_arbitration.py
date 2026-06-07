from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO / "runtime" / "a7ls18_company_numeric_aggregate"
RUNTIME = REPO / "runtime" / "a7ls19_checkpoint_arbitration"
REPORT = REPO / "reports" / "CRYPTO_A7LS19_CHECKPOINT_ARBITRATION_20260607.md"

SELECTED_PATH = INPUT_DIR / "a7ls18_selected_portfolio_queue.csv"
MANIFEST_PATH = INPUT_DIR / "a7ls18_manifest.json"

TARGET_QUEUE_SIZE = 128
CONTROL_PRIMARY_MAX = 0.90
CONTROL_STRONG_MAX = 0.80
MAX_BASIS_PREMIUM_SHARE = 0.55
MAX_SEMANTIC_PAIR_COUNT = 14
MAX_SKELETON_COUNT = 8
MAX_LABEL_FAMILY_COUNT = 104

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


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def bool_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
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


def add_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    numeric_cols = [
        "control_ratio_premay_max",
        "cost10_recent_oriented",
        "cost5_recent_oriented",
        "cost2_recent_oriented",
        "one_bar_lag_recent_oriented",
        "robust_median_tstat_floor",
        "robust_min_tstat_floor",
        "score_no_may",
        "finite_share",
        "nonzero_share",
        "recent_oos_2026JanApr_mean_spread",
        "recent_oos_2026JanApr_tstat",
        "avg_n_obs_recent",
    ]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    if "label_horizon_h" in out.columns:
        out["label_horizon_h"] = pd.to_numeric(out["label_horizon_h"], errors="coerce").astype("Int64")
    out["lag_ok_bool"] = bool_series(out.get("lag_ok", pd.Series(False, index=out.index)))
    out["robust_ok_bool"] = bool_series(out.get("robust_ok", pd.Series(False, index=out.index)))
    out["premay_all_positive_bool"] = bool_series(out.get("premay_all_positive", pd.Series(False, index=out.index)))
    out["is_l7"] = out["label_family"].astype(str).eq("L7_ranked_future_return")
    out["is_placebo"] = out["semantic_pair"].astype(str).str.contains("placebo", case=False, na=False)
    out["is_low_prior"] = out["semantic_pair"].astype(str).str.contains("low_prior_axes", case=False, na=False)
    out["contains_basis_premium"] = out["semantic_pair"].astype(str).str.contains("basis_premium_like", na=False)
    for token in SOURCE_TOKENS:
        out[f"contains_{token}"] = out["semantic_pair"].astype(str).str.contains(token, na=False)
    out["strict_non_l7"] = (
        ~out["is_l7"]
        & ~out["is_placebo"]
        & ~out["is_low_prior"]
        & out["premay_all_positive_bool"]
        & out["lag_ok_bool"]
        & out["robust_ok_bool"]
        & (out["cost10_recent_oriented"] > 0)
        & (out["control_ratio_premay_max"] < CONTROL_PRIMARY_MAX)
    )
    out["strong_non_l7"] = out["strict_non_l7"] & (out["control_ratio_premay_max"] < CONTROL_STRONG_MAX)
    out["arbitration_score"] = (
        out["score_no_may"].fillna(0.0)
        + out["strong_non_l7"].astype(float) * 150.0
        + (~out["contains_basis_premium"]).astype(float) * 55.0
        + out["label_family"].astype(str).isin(
            ["L0_raw_forward_return", "L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return"]
        ).astype(float)
        * 45.0
        - out["control_ratio_premay_max"].fillna(1.0) * 60.0
    )
    return out


def reason_for(row: pd.Series) -> str:
    reasons: list[str] = []
    if row.get("is_l7", False):
        reasons.append("rank_label_diagnostic_only")
    if row.get("is_placebo", False):
        reasons.append("placebo_semantic_pair")
    if row.get("is_low_prior", False):
        reasons.append("low_prior_axis")
    if not row.get("premay_all_positive_bool", False):
        reasons.append("premay_not_all_positive")
    if not row.get("lag_ok_bool", False):
        reasons.append("lag_fail")
    if not row.get("robust_ok_bool", False):
        reasons.append("robust_fail")
    if pd.isna(row.get("control_ratio_premay_max")) or row.get("control_ratio_premay_max") >= CONTROL_PRIMARY_MAX:
        reasons.append("control_ratio_too_high")
    if pd.isna(row.get("cost10_recent_oriented")) or row.get("cost10_recent_oriented") <= 0:
        reasons.append("cost10_not_positive")
    return ";".join(reasons) if reasons else "strict_non_l7_eligible"


def build_checkpoint_queue(eligible: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ordered = eligible.sort_values(
        ["strong_non_l7", "arbitration_score", "score_no_may", "cost10_recent_oriented"],
        ascending=[False, False, False, False],
    ).copy()

    selected: list[int] = []
    audit_rows: list[dict[str, Any]] = []
    semantic_counts: dict[str, int] = {}
    skeleton_counts: dict[str, int] = {}
    label_counts: dict[str, int] = {}
    basis_count = 0

    basis_cap = int(TARGET_QUEUE_SIZE * MAX_BASIS_PREMIUM_SHARE)

    for idx, row in ordered.iterrows():
        if len(selected) >= TARGET_QUEUE_SIZE:
            break
        semantic = str(row.get("semantic_pair", ""))
        skeleton = str(row.get("skeleton_key", ""))
        label = str(row.get("label_family", ""))
        is_basis = bool(row.get("contains_basis_premium", False))

        reject: list[str] = []
        if semantic_counts.get(semantic, 0) >= MAX_SEMANTIC_PAIR_COUNT:
            reject.append("semantic_pair_cap")
        if skeleton_counts.get(skeleton, 0) >= MAX_SKELETON_COUNT:
            reject.append("skeleton_cap")
        if label_counts.get(label, 0) >= MAX_LABEL_FAMILY_COUNT:
            reject.append("label_family_cap")
        if is_basis and basis_count >= basis_cap:
            reject.append("basis_premium_cap")

        if reject:
            audit_rows.append(
                {
                    "blueprint_id": row.get("blueprint_id"),
                    "expression": row.get("expression"),
                    "semantic_pair": semantic,
                    "skeleton_key": skeleton,
                    "label_family": label,
                    "arbitration_score": row.get("arbitration_score"),
                    "decision": "CAP_REJECT",
                    "reason": ";".join(reject),
                }
            )
            continue

        selected.append(idx)
        semantic_counts[semantic] = semantic_counts.get(semantic, 0) + 1
        skeleton_counts[skeleton] = skeleton_counts.get(skeleton, 0) + 1
        label_counts[label] = label_counts.get(label, 0) + 1
        if is_basis:
            basis_count += 1

    queue = ordered.loc[selected].copy()
    queue.insert(0, "a7ls19_rank", range(1, len(queue) + 1))
    queue["a7ls19_decision"] = "A7LS19_CHECKPOINT_QUEUE"
    cap_audit = pd.DataFrame(audit_rows)
    return queue, cap_audit


def group_counts(df: pd.DataFrame, col: str, total_name: str = "count") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[col, total_name, "share"])
    out = df.groupby(col, dropna=False).size().reset_index(name=total_name).sort_values(total_name, ascending=False)
    out["share"] = out[total_name] / max(1, len(df))
    return out


def main() -> None:
    manifest_in = read_json(MANIFEST_PATH)
    if manifest_in.get("decision") != "PASS_A7LS18_COMPANY_NUMERIC_CLUES_READY_FOR_A7LS19":
        raise SystemExit(f"A7LS18 not ready for A7LS19: {manifest_in.get('decision')}")
    df = pd.read_csv(SELECTED_PATH)
    df = add_numeric_columns(df)
    df["a7ls19_reject_reason"] = df.apply(reason_for, axis=1)

    strict = df[df["strict_non_l7"]].copy()
    strong = df[df["strong_non_l7"]].copy()
    rejected = df[~df["strict_non_l7"]].copy()
    checkpoint, cap_audit = build_checkpoint_queue(strict)

    RUNTIME.mkdir(parents=True, exist_ok=True)
    strict.to_csv(RUNTIME / "a7ls19_strict_non_l7_eligible.csv", index=False)
    strong.to_csv(RUNTIME / "a7ls19_strong_non_l7_eligible.csv", index=False)
    rejected.to_csv(RUNTIME / "a7ls19_rejected_or_diagnostic.csv", index=False)
    checkpoint.to_csv(RUNTIME / "a7ls19_checkpoint_queue.csv", index=False)
    cap_audit.to_csv(RUNTIME / "a7ls19_cap_reject_audit.csv", index=False)

    rejection_summary = (
        df.groupby("a7ls19_reject_reason", dropna=False).size().reset_index(name="count").sort_values("count", ascending=False)
    )
    rejection_summary.to_csv(RUNTIME / "a7ls19_rejection_summary.csv", index=False)

    label_dist = group_counts(checkpoint, "label_family")
    label_dist.to_csv(RUNTIME / "a7ls19_checkpoint_label_distribution.csv", index=False)
    semantic_dist = group_counts(checkpoint, "semantic_pair")
    semantic_dist.to_csv(RUNTIME / "a7ls19_checkpoint_semantic_pair_distribution.csv", index=False)
    skeleton_dist = group_counts(checkpoint, "skeleton_key")
    skeleton_dist.to_csv(RUNTIME / "a7ls19_checkpoint_skeleton_distribution.csv", index=False)

    source_rows: list[dict[str, Any]] = []
    for token in SOURCE_TOKENS:
        col = f"contains_{token}"
        source_rows.append(
            {
                "source_token": token,
                "selected_count": int(checkpoint[col].sum()) if col in checkpoint else 0,
                "selected_share": float(checkpoint[col].sum() / max(1, len(checkpoint))) if col in checkpoint else 0.0,
                "strict_eligible_count": int(strict[col].sum()) if col in strict else 0,
                "strict_eligible_share": float(strict[col].sum() / max(1, len(strict))) if col in strict else 0.0,
            }
        )
    source_caps = pd.DataFrame(source_rows).sort_values("selected_count", ascending=False)
    source_caps.to_csv(RUNTIME / "a7ls19_source_family_caps.csv", index=False)

    top = checkpoint.head(40).copy()
    top.to_csv(RUNTIME / "a7ls19_top_checkpoint_candidates.csv", index=False)

    basis_share = float(checkpoint["contains_basis_premium"].sum() / max(1, len(checkpoint))) if not checkpoint.empty else 0.0
    basis_count = int(checkpoint["contains_basis_premium"].sum()) if not checkpoint.empty else 0
    basis_count_cap = int(TARGET_QUEUE_SIZE * MAX_BASIS_PREMIUM_SHARE)
    l5_share = float((checkpoint["label_family"].astype(str) == "L5_vol_adjusted_return").sum() / max(1, len(checkpoint))) if not checkpoint.empty else 0.0
    max_skeleton_share = float(skeleton_dist["share"].max()) if not skeleton_dist.empty else 0.0
    max_semantic_share = float(semantic_dist["share"].max()) if not semantic_dist.empty else 0.0
    non_l5_count = int((checkpoint["label_family"].astype(str) != "L5_vol_adjusted_return").sum()) if not checkpoint.empty else 0

    blockers: list[str] = []
    warnings: list[str] = []
    if len(checkpoint) < 64:
        blockers.append("checkpoint_queue_too_small")
    if basis_count > basis_count_cap:
        blockers.append("basis_premium_absolute_cap_violation")
    if basis_share > 0.50:
        warnings.append("basis_premium_still_dominant")
    if l5_share > 0.85:
        warnings.append("label_l5_dominant")
    if max_skeleton_share > 0.10:
        blockers.append("skeleton_concentration")
    if max_semantic_share > 0.15:
        blockers.append("semantic_pair_concentration")
    if non_l5_count < 12:
        warnings.append("non_l5_label_breadth_weak")

    decision = (
        "PASS_A7LS19_DIVERSIFIED_CHECKPOINT_QUEUE_READY_FOR_A7LS20"
        if not blockers
        else "HOLD_A7LS19_CHECKPOINT_ARBITRATION_BLOCKED"
    )

    out_manifest = {
        "stage": "A7LS-19",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "warnings": warnings,
        "input_stage": "A7LS-18",
        "input_selected_count": int(len(df)),
        "strict_non_l7_eligible_count": int(len(strict)),
        "strong_non_l7_eligible_count": int(len(strong)),
        "checkpoint_queue_count": int(len(checkpoint)),
        "checkpoint_basis_premium_count": basis_count,
        "checkpoint_basis_premium_count_cap": basis_count_cap,
        "checkpoint_basis_premium_share": basis_share,
        "checkpoint_l5_share": l5_share,
        "checkpoint_non_l5_count": non_l5_count,
        "checkpoint_max_skeleton_share": max_skeleton_share,
        "checkpoint_max_semantic_pair_share": max_semantic_share,
        "target_queue_size": TARGET_QUEUE_SIZE,
        "control_primary_max": CONTROL_PRIMARY_MAX,
        "control_strong_max": CONTROL_STRONG_MAX,
        "excludes_l7_from_checkpoint": True,
        "excludes_placebo_from_checkpoint": True,
        "excludes_low_prior_axes_from_checkpoint": True,
        "uses_may": False,
        "executes_search": False,
        "authorizes_a7ls20_checkpoint_deep_replay": decision.startswith("PASS_"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls19_manifest.json", out_manifest)
    write_json(RUNTIME / "a7ls19_decision_record.json", out_manifest)

    report_lines = [
        "# CRYPTO A7LS19 CHECKPOINT ARBITRATION",
        "",
        f"Generated: {out_manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(out_manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Interpretation",
        "",
        "A7LS19 does not run search or replay. It arbitrates the completed A7LS18 selected queue into a stricter, non-L7, role-clean checkpoint queue.",
        "",
        "Key hard filters:",
        "",
        "- excludes L7 ranked-return diagnostic-only rows from checkpoint promotion",
        "- excludes placebo and low-prior semantic axes",
        "- requires pre-May all-positive, lag survival, robust survival, positive cost10",
        f"- requires control_ratio_premay_max < {CONTROL_PRIMARY_MAX}",
        "- applies semantic pair, skeleton, label-family, and basis/premium concentration caps",
        "",
        "## Source Family Caps",
        "",
        md_table(source_caps, 40),
        "",
        "## Label Distribution",
        "",
        md_table(label_dist, 20),
        "",
        "## Semantic Pair Distribution",
        "",
        md_table(semantic_dist, 40),
        "",
        "## Rejection Summary",
        "",
        md_table(rejection_summary, 80),
        "",
        "## Top Checkpoint Candidates",
        "",
        md_table(
            top[
                [
                    "a7ls19_rank",
                    "blueprint_id",
                    "semantic_pair",
                    "motif",
                    "label_family",
                    "label_horizon_h",
                    "control_ratio_premay_max",
                    "cost10_recent_oriented",
                    "one_bar_lag_recent_oriented",
                    "score_no_may",
                    "expression",
                ]
            ],
            40,
        ),
        "",
        "## Authorization",
        "",
        "- A7LS20 checkpoint deep replay / marginal contribution audit: authorized only if decision is PASS.",
        "- New formula search: not authorized.",
        "- Alpha proof / shadow / paper / live: not authorized.",
        "",
    ]
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    print(json.dumps(out_manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
