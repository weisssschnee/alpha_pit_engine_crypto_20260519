from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE56 = REPO / "runtime" / "a7ffcore56_bounded_replay_preflight"
RUNTIME = REPO / "runtime" / "a7ffcore57_replay_failure_decomposition"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE57_REPLAY_FAILURE_DECOMPOSITION_20260604.md"

PREMAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
CONTROL_KINDS = ["stale", "time_shuffle", "symbol_shuffle", "sign_flip"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def finite_float(value: Any, default: float = np.nan) -> float:
    try:
        out = float(value)
        return out if np.isfinite(out) else default
    except Exception:
        return default


def summary_by(df: pd.DataFrame, keys: list[str], extra_aggs: dict[str, tuple[str, str]] | None = None) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    aggs: dict[str, tuple[str, str]] = {
        "row_count": ("decision", "count"),
        "candidate_count": ("blueprint_id", "nunique"),
        "median_control_ratio": ("control_ratio_premay_max", "median"),
        "median_positive_split_count": ("premay_positive_split_count", "median"),
        "max_recent_spread": ("recent_oos_2026JanApr_spread", "max"),
        "median_cost5_recent": ("cost5_recent_oriented", "median"),
    }
    if extra_aggs:
        aggs.update(extra_aggs)
    return (
        df.groupby(keys, as_index=False, dropna=False)
        .agg(**aggs)
        .sort_values(["candidate_count", "row_count"], ascending=[False, False])
    )


def strongest_control(row: pd.Series) -> tuple[str, float, str]:
    best_kind = ""
    best_split = ""
    best_abs = -1.0
    for split in PREMAY_SPLITS:
        for kind in CONTROL_KINDS:
            value = abs(finite_float(row.get(f"{split}_{kind}_spread"), 0.0))
            if value > best_abs:
                best_abs = value
                best_kind = kind
                best_split = split
    return best_kind, best_abs, best_split


def sign_pattern(row: pd.Series) -> str:
    signs = []
    for split in PREMAY_SPLITS:
        value = finite_float(row.get(f"{split}_spread"), 0.0)
        signs.append("+" if value > 0 else "-" if value < 0 else "0")
    return "".join(signs)


def split_failure_reason(row: pd.Series) -> str:
    parts = []
    if int(finite_float(row.get("premay_positive_split_count"), 0)) < 3:
        parts.append("premay_sign_unstable")
    if finite_float(row.get("control_ratio_premay_max"), 99.0) >= 1.0:
        parts.append("control_dominated")
    if finite_float(row.get("stale_ratio_recent"), 99.0) >= 1.0:
        parts.append("stale_lag_fragile")
    if finite_float(row.get("cost5_recent_oriented"), -99.0) <= 0:
        parts.append("cost5_fragile")
    return "|".join(parts) if parts else "none"


def build_candidate_profile(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for blueprint_id, group in df.groupby("blueprint_id", sort=False):
        decisions = group["decision"].astype(str).value_counts()
        best = group.sort_values(
            ["cost5_recent_oriented", "recent_oos_2026JanApr_spread"],
            ascending=[False, False],
        ).iloc[0]
        rows.append(
            {
                "blueprint_id": blueprint_id,
                "expression": best.get("expression", ""),
                "a7input_queue": best.get("a7input_queue", ""),
                "semantic_pair": best.get("semantic_pair", ""),
                "motif": best.get("motif", ""),
                "skeleton_key": best.get("skeleton_key", ""),
                "production_key": best.get("production_key", ""),
                "row_count": int(len(group)),
                "label_family_count": int(group["label_family"].nunique()),
                "horizon_count": int(group["label_horizon_h"].nunique()),
                "dominant_decision": decisions.index[0] if len(decisions) else "",
                "dominant_decision_share": float(decisions.iloc[0] / len(group)) if len(decisions) else 0.0,
                "median_control_ratio": finite_float(group["control_ratio_premay_max"].median()),
                "min_control_ratio": finite_float(group["control_ratio_premay_max"].min()),
                "median_positive_split_count": finite_float(group["premay_positive_split_count"].median()),
                "max_positive_split_count": int(group["premay_positive_split_count"].max()),
                "max_recent_spread": finite_float(group["recent_oos_2026JanApr_spread"].max()),
                "max_cost5_recent": finite_float(group["cost5_recent_oriented"].max()),
                "best_label_family": best.get("label_family", ""),
                "best_label_horizon_h": int(best.get("label_horizon_h", 0)),
                "best_decision": best.get("decision", ""),
            }
        )
    return pd.DataFrame(rows).sort_values(["max_positive_split_count", "max_cost5_recent"], ascending=[False, False])


def label_observation_audit(df: pd.DataFrame) -> pd.DataFrame:
    obs_cols = [f"{split}_obs" for split in ["train_2024", *PREMAY_SPLITS]]
    rows = []
    for (label_family, horizon), group in df.groupby(["label_family", "label_horizon_h"], sort=False, dropna=False):
        row = {"label_family": label_family, "label_horizon_h": int(horizon), "row_count": int(len(group))}
        for col in obs_cols:
            values = pd.to_numeric(group[col], errors="coerce")
            row[f"{col}_median"] = finite_float(values.median(), 0.0)
            row[f"{col}_positive_rows"] = int((values > 0).sum())
        positive_all_premay = min(row[f"{split}_obs_positive_rows"] for split in PREMAY_SPLITS)
        row["premay_label_observation_status"] = "LABEL_OBS_OK" if positive_all_premay > 0 else "LABEL_OBS_EMPTY"
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["premay_label_observation_status", "label_family", "label_horizon_h"])


def repair_policy(df: pd.DataFrame, by_semantic: pd.DataFrame, by_motif: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    semantic_rows = []
    for _, row in by_semantic.iterrows():
        action = "keep_diagnostic"
        reason = []
        if finite_float(row.get("median_control_ratio"), 99.0) >= 1.0:
            action = "downweight_or_block_as_alpha"
            reason.append("median_control_ratio_ge_1")
        if finite_float(row.get("median_positive_split_count"), 0.0) < 2:
            action = "downweight_or_block_as_alpha"
            reason.append("premay_split_instability")
        if finite_float(row.get("median_cost5_recent"), -99.0) <= 0:
            reason.append("cost5_nonpositive")
        semantic_rows.append(
            {
                "policy_scope": "semantic_pair",
                "key": row.get("semantic_pair", ""),
                "action": action,
                "reason": "|".join(reason) if reason else "diagnostic_only_until_replay_clean",
                "candidate_count": int(row.get("candidate_count", 0)),
                "median_control_ratio": finite_float(row.get("median_control_ratio")),
                "median_positive_split_count": finite_float(row.get("median_positive_split_count")),
            }
        )
    motif_rows = []
    for _, row in by_motif.iterrows():
        action = "keep_diagnostic"
        reason = []
        if finite_float(row.get("median_control_ratio"), 99.0) >= 1.0:
            action = "downweight_or_block_as_alpha"
            reason.append("median_control_ratio_ge_1")
        if finite_float(row.get("median_positive_split_count"), 0.0) < 2:
            action = "downweight_or_block_as_alpha"
            reason.append("premay_split_instability")
        motif_rows.append(
            {
                "policy_scope": "motif",
                "key": row.get("motif", ""),
                "action": action,
                "reason": "|".join(reason) if reason else "diagnostic_only_until_replay_clean",
                "candidate_count": int(row.get("candidate_count", 0)),
                "median_control_ratio": finite_float(row.get("median_control_ratio")),
                "median_positive_split_count": finite_float(row.get("median_positive_split_count")),
            }
        )
    policy = pd.DataFrame([*semantic_rows, *motif_rows])
    next_policy = {
        "stage": "A7FF-CORE57",
        "next_recommended_stage": "A7FF-CORE58",
        "core58_objective": "failure-aware queue rebuild with control-clean and split-stable hard gates",
        "hard_exclusions": [
            "control_ratio_premay_max >= 1.0",
            "premay_positive_split_count < 3 for replay queue",
            "stale_ratio_recent >= 1.0",
            "cost5_recent_oriented <= 0",
            "label families with zero pre-May observations",
        ],
        "selector_changes": [
            "rank by preMay split consistency before recent spread",
            "penalize strongest control source directly",
            "require nonzero representation from at least four semantic pairs before replay",
            "do not promote CORE55 numeric clue rows without CORE56 replay clean evidence",
        ],
        "does_not_authorize_search": True,
    }
    return policy, next_policy


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    source = read_json(CORE56 / "a7ffcore56_manifest.json")
    if source.get("stage") != "A7FF-CORE56" or not source.get("executes_replay"):
        raise SystemExit("CORE57 requires CORE56 replay manifest")

    metrics_path = CORE56 / "a7ffcore56_replay_metrics.csv"
    if not metrics_path.exists():
        raise SystemExit(f"missing CORE56 metrics: {metrics_path}")
    df = pd.read_csv(metrics_path)
    if df.empty:
        raise SystemExit("CORE57 cannot decompose an empty CORE56 metrics table")

    strongest = df.apply(strongest_control, axis=1, result_type="expand")
    strongest.columns = ["strongest_control_kind", "strongest_control_abs_spread", "strongest_control_split"]
    df = pd.concat([df, strongest], axis=1)
    df["premay_sign_pattern"] = df.apply(sign_pattern, axis=1)
    df["failure_reason_detail"] = df.apply(split_failure_reason, axis=1)

    enriched = df.copy()
    enriched.to_csv(RUNTIME / "a7ffcore57_enriched_replay_metrics.csv", index=False)
    by_decision = summary_by(enriched, ["decision"])
    by_label = summary_by(enriched, ["label_family", "label_horizon_h", "decision"])
    by_semantic = summary_by(enriched, ["semantic_pair"])
    by_semantic_decision = summary_by(enriched, ["semantic_pair", "decision"])
    by_motif = summary_by(enriched, ["motif"])
    control_decomp = summary_by(enriched, ["strongest_control_kind", "strongest_control_split", "decision"])
    split_decomp = summary_by(enriched, ["premay_positive_split_count", "premay_sign_pattern", "decision"])
    label_obs = label_observation_audit(enriched)
    failure_detail = (
        enriched.assign(failure_reason_detail=enriched["failure_reason_detail"].astype(str).str.split("|"))
        .explode("failure_reason_detail")
        .groupby(["failure_reason_detail", "decision"], as_index=False, dropna=False)
        .size()
        .rename(columns={"size": "row_count"})
        .sort_values("row_count", ascending=False)
    )
    candidate_profile = build_candidate_profile(enriched)
    policy, next_policy = repair_policy(enriched, by_semantic, by_motif)

    outputs = {
        "a7ffcore57_decision_summary.csv": by_decision,
        "a7ffcore57_failure_by_label_horizon.csv": by_label,
        "a7ffcore57_failure_by_semantic_pair.csv": by_semantic,
        "a7ffcore57_failure_by_semantic_pair_decision.csv": by_semantic_decision,
        "a7ffcore57_failure_by_motif.csv": by_motif,
        "a7ffcore57_control_source_decomposition.csv": control_decomp,
        "a7ffcore57_split_stability_decomposition.csv": split_decomp,
        "a7ffcore57_label_observation_audit.csv": label_obs,
        "a7ffcore57_failure_reason_detail.csv": failure_detail,
        "a7ffcore57_candidate_failure_profile.csv": candidate_profile,
        "a7ffcore57_repair_policy.csv": policy,
    }
    for name, frame in outputs.items():
        frame.to_csv(RUNTIME / name, index=False)
    write_json(RUNTIME / "a7ffcore57_next_queue_policy.json", next_policy)

    clean_count = int(source.get("clean_candidate_count", 0))
    empty_label_families = sorted(label_obs.loc[label_obs["premay_label_observation_status"].eq("LABEL_OBS_EMPTY"), "label_family"].unique().tolist())
    decision = "PASS_A7FFCORE57_FAILURE_DECOMPOSITION_BUILT"
    blockers = ["core56_clean_candidate_count_zero"] if clean_count == 0 else []
    manifest = {
        "stage": "A7FF-CORE57",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE56",
        "source_decision": source.get("decision"),
        "decision": decision,
        "blockers_inherited_from_core56": blockers,
        "input_replay_rows": int(len(enriched)),
        "input_candidate_count": int(enriched["blueprint_id"].nunique()),
        "decision_count": int(enriched["decision"].nunique()),
        "semantic_pair_count": int(enriched["semantic_pair"].nunique()),
        "motif_count": int(enriched["motif"].nunique()),
        "control_dominated_rows": int(enriched["decision"].eq("HOLD_CORE56_CONTROL_DOMINATED").sum()),
        "premay_unstable_rows": int(enriched["decision"].eq("HOLD_CORE56_PREMAY_UNSTABLE").sum()),
        "cost5_fragile_rows": int(enriched["decision"].eq("HOLD_CORE56_COST5_FRAGILE").sum()),
        "stale_lag_fragile_rows": int(enriched["decision"].eq("HOLD_CORE56_STALE_LAG_FRAGILE").sum()),
        "empty_premay_label_families": empty_label_families,
        "empty_premay_label_family_count": int(len(empty_label_families)),
        "executes_replay": False,
        "executes_search": False,
        "uses_may": False,
        "authorizes_core58_failure_aware_queue_rebuild": True,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore57_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ffcore57_authorization_matrix.json",
        {
            "authorized": {"A7FF-CORE58 failure-aware queue rebuild": True},
            "not_authorized": {"large_search": True, "alpha_proof": True, "shadow_paper_live": True},
        },
    )

    report = [
        "# CRYPTO A7FF-CORE57 REPLAY FAILURE DECOMPOSITION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE57 decomposes CORE56 bounded replay failures. It does not generate formulas, run replay, or authorize alpha promotion.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Decision Summary",
        "",
        md_table(by_decision),
        "",
        "## Failure By Label / Horizon",
        "",
        md_table(by_label),
        "",
        "## Label Observation Audit",
        "",
        md_table(label_obs),
        "",
        "## Failure By Semantic Pair",
        "",
        md_table(by_semantic),
        "",
        "## Control Source Decomposition",
        "",
        md_table(control_decomp),
        "",
        "## Split Stability Decomposition",
        "",
        md_table(split_decomp),
        "",
        "## Repair Policy Preview",
        "",
        md_table(policy),
        "",
        "## Boundary",
        "",
        "```text",
        "search executed: false",
        "replay executed: false",
        "May used: false",
        "large search / alpha proof / shadow / paper / live: false",
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
