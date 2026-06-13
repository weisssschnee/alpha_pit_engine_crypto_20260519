from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DEFAULT_REJECTIONS = (
    REPO
    / "runtime"
    / "a7v3s3_strict_reward_early_stop_20260613"
    / "a7v3s3_early_stop_all_rejections.csv"
)
DEFAULT_RUNTIME = REPO / "runtime" / "a7v3s4_near_miss_prefilter_audit_20260613"
DEFAULT_REPORT = REPO / "reports" / "CRYPTO_A7V3S4_NEAR_MISS_PREFILTER_AUDIT_20260613.md"

FIELD_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
OPERATOR_NAMES = {
    "Abs",
    "Add",
    "Clip",
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


def md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```text\n" + view.to_string(index=False) + "\n```"


def to_bool(series: pd.Series) -> pd.Series:
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def numeric(frame: pd.DataFrame, column: str, default: float = np.nan) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def reason_contains(frame: pd.DataFrame, needle: str) -> pd.Series:
    reasons = frame.get("hard_reject_reasons", pd.Series("", index=frame.index)).fillna("").astype(str)
    return reasons.str.contains(needle, regex=False)


def extract_fields(expression: str) -> list[str]:
    fields: list[str] = []
    for token in FIELD_RE.findall(str(expression)):
        if token in OPERATOR_NAMES:
            continue
        if token.lower() in {"nan", "inf", "true", "false"}:
            continue
        fields.append(token)
    return sorted(set(fields))


def classify(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["recent_edge"] = (numeric(out, "recent_sortino") > 0) & (numeric(out, "recent_sharpe") > 0)
    out["oos_floor_clean"] = numeric(out, "min_oos_floor_sortino") > 0
    out["oos_sortino_clean"] = numeric(out, "min_oos_sortino") > 0
    stress_obs = numeric(out, "stress_n_obs", 0).fillna(0) > 0
    out["stress_floor_clean"] = (~stress_obs) | (numeric(out, "stress_floor_sortino") > 0)
    out["control_clean"] = (
        (numeric(out, "oos_control_dominated_count", 99).fillna(99) == 0)
        & (numeric(out, "oos_lag_stale_dominated_count", 99).fillna(99) == 0)
        & (numeric(out, "recent_shuffle_control_ratio", 99).fillna(99) < 1)
    )
    out["shuffle_clean"] = numeric(out, "recent_shuffle_control_ratio", 99).fillna(99) < 1
    out["train_oriented"] = ~reason_contains(out, "train_orientation_no_positive_edge")
    out["finite_clean"] = ~reason_contains(out, "non_finite_diagnostic_composite")
    out["oos_net_positive"] = ~reason_contains(out, "oos_net_mean_not_all_positive")
    out["control_dominated"] = reason_contains(out, "oos_control_dominated")
    out["lag_stale_dominated"] = reason_contains(out, "oos_lag_stale_dominated")
    out["shuffle_dominated"] = reason_contains(out, "oos_shuffle_dominated")

    score_cols = [
        "recent_edge",
        "oos_floor_clean",
        "oos_sortino_clean",
        "stress_floor_clean",
        "control_clean",
        "shuffle_clean",
        "train_oriented",
        "finite_clean",
        "oos_net_positive",
    ]
    out["prefilter_survival_score"] = out[score_cols].sum(axis=1).astype(int)

    classes = np.full(out.shape[0], "dead_or_no_recent_edge", dtype=object)
    classes[out["recent_edge"] & (~out["oos_floor_clean"])] = "recent_only_artifact"
    classes[out["recent_edge"] & out["oos_floor_clean"] & (~out["stress_floor_clean"])] = "stress_fragile_artifact"
    classes[
        out["recent_edge"]
        & out["oos_floor_clean"]
        & out["stress_floor_clean"]
        & (~out["control_clean"])
    ] = "control_polluted_near_miss"
    classes[
        out["recent_edge"]
        & out["oos_floor_clean"]
        & out["stress_floor_clean"]
        & out["control_clean"]
        & out["train_oriented"]
    ] = "mechanism_keep_probe"
    classes[~out["finite_clean"]] = "non_finite_invalid"
    out["prefilter_class"] = classes
    return out


def group_summary(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    rows = []
    for key, group in frame.groupby(keys, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        payload = {col: value for col, value in zip(keys, key)}
        n = len(group)
        payload.update(
            {
                "rows": n,
                "unique_blueprints": group["blueprint_id"].nunique() if "blueprint_id" in group else n,
                "mechanism_keep_probe": int((group["prefilter_class"] == "mechanism_keep_probe").sum()),
                "control_polluted_near_miss": int((group["prefilter_class"] == "control_polluted_near_miss").sum()),
                "recent_only_artifact": int((group["prefilter_class"] == "recent_only_artifact").sum()),
                "stress_fragile_artifact": int((group["prefilter_class"] == "stress_fragile_artifact").sum()),
                "control_dom_rate": float(group["control_dominated"].mean()),
                "lag_stale_dom_rate": float(group["lag_stale_dominated"].mean()),
                "shuffle_dom_rate": float(group["shuffle_dominated"].mean()),
                "oos_floor_clean_rate": float(group["oos_floor_clean"].mean()),
                "stress_floor_clean_rate": float(group["stress_floor_clean"].mean()),
                "median_recent_sortino": float(numeric(group, "recent_sortino").median()),
                "median_min_oos_floor_sortino": float(numeric(group, "min_oos_floor_sortino").median()),
                "median_stress_floor_sortino": float(numeric(group, "stress_floor_sortino").median()),
                "median_prefilter_survival_score": float(group["prefilter_survival_score"].median()),
            }
        )
        if payload["mechanism_keep_probe"] > 0:
            decision = "KEEP_REDUCED_CAP_MECHANISM_PROBE"
        elif payload["control_polluted_near_miss"] > 0:
            decision = "REDESIGN_NOT_REWARD_AS_IS"
        elif n >= 8 and payload["control_dom_rate"] >= 0.80 and payload["lag_stale_dom_rate"] >= 0.70:
            decision = "HARD_BLOCK_CONTROL_STALE_PATTERN"
        elif n >= 8 and payload["recent_only_artifact"] / max(n, 1) >= 0.60:
            decision = "DEPRIORITIZE_RECENT_ONLY_PATTERN"
        else:
            decision = "LOW_PRIORITY_OR_INSUFFICIENT_EVIDENCE"
        payload["prefilter_decision"] = decision
        rows.append(payload)
    return pd.DataFrame(rows).sort_values(
        ["mechanism_keep_probe", "control_polluted_near_miss", "median_prefilter_survival_score", "rows"],
        ascending=[False, False, False, False],
    )


def field_summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        for field in extract_fields(str(row.get("expression", ""))):
            rows.append(
                {
                    "field": field,
                    "prefilter_class": row["prefilter_class"],
                    "control_dominated": bool(row["control_dominated"]),
                    "lag_stale_dominated": bool(row["lag_stale_dominated"]),
                    "oos_floor_clean": bool(row["oos_floor_clean"]),
                    "stress_floor_clean": bool(row["stress_floor_clean"]),
                    "recent_sortino": row.get("recent_sortino"),
                    "min_oos_floor_sortino": row.get("min_oos_floor_sortino"),
                    "stress_floor_sortino": row.get("stress_floor_sortino"),
                }
            )
    if not rows:
        return pd.DataFrame()
    exploded = pd.DataFrame(rows)
    out = (
        exploded.groupby("field", dropna=False)
        .agg(
            rows=("field", "size"),
            mechanism_keep_probe=("prefilter_class", lambda s: int((s == "mechanism_keep_probe").sum())),
            control_polluted_near_miss=("prefilter_class", lambda s: int((s == "control_polluted_near_miss").sum())),
            control_dom_rate=("control_dominated", "mean"),
            lag_stale_dom_rate=("lag_stale_dominated", "mean"),
            oos_floor_clean_rate=("oos_floor_clean", "mean"),
            stress_floor_clean_rate=("stress_floor_clean", "mean"),
            median_recent_sortino=("recent_sortino", lambda s: pd.to_numeric(s, errors="coerce").median()),
            median_min_oos_floor_sortino=("min_oos_floor_sortino", lambda s: pd.to_numeric(s, errors="coerce").median()),
        )
        .reset_index()
    )
    return out.sort_values(["mechanism_keep_probe", "control_polluted_near_miss", "rows"], ascending=False)


def build_prefilter_rules(pair_motif: pd.DataFrame) -> dict[str, Any]:
    hard_block = pair_motif[pair_motif["prefilter_decision"].eq("HARD_BLOCK_CONTROL_STALE_PATTERN")]
    redesign = pair_motif[pair_motif["prefilter_decision"].eq("REDESIGN_NOT_REWARD_AS_IS")]
    keep = pair_motif[pair_motif["prefilter_decision"].eq("KEEP_REDUCED_CAP_MECHANISM_PROBE")]
    recent_only = pair_motif[pair_motif["prefilter_decision"].eq("DEPRIORITIZE_RECENT_ONLY_PATTERN")]
    return {
        "stage": "A7V3S4_SEARCH_SPACE_CONTROL_PREFILTER",
        "generated_at": now_utc(),
        "rule_scope": "pre_reward_candidate_queue_filter",
        "hard_block_pair_motif": hard_block[["semantic_pair", "motif", "rows", "control_dom_rate", "lag_stale_dom_rate"]].to_dict("records"),
        "redesign_pair_motif_not_reward_as_is": redesign[
            ["semantic_pair", "motif", "rows", "control_polluted_near_miss", "control_dom_rate", "lag_stale_dom_rate"]
        ].to_dict("records"),
        "keep_reduced_cap_mechanism_probe": keep[
            ["semantic_pair", "motif", "rows", "mechanism_keep_probe", "median_prefilter_survival_score"]
        ].to_dict("records"),
        "deprioritize_recent_only_pair_motif": recent_only[["semantic_pair", "motif", "rows", "recent_only_artifact"]].to_dict("records"),
        "queue_policy": {
            "do_not_continue_a7v3s3_same_queue": True,
            "require_prefilter_before_reward": True,
            "reject_if_oos_control_or_lag_stale_dominated_in_prior_audit": True,
            "allow_reduced_cap_for_mechanism_keep_probe": True,
            "allow_redesign_for_control_polluted_near_miss": True,
        },
    }


def main() -> None:
    runtime = DEFAULT_RUNTIME
    runtime.mkdir(parents=True, exist_ok=True)
    report = DEFAULT_REPORT
    rejected = pd.read_csv(DEFAULT_REJECTIONS, low_memory=False)
    classified = classify(rejected)

    pair_motif = group_summary(classified, ["semantic_pair", "motif"])
    pair_summary = group_summary(classified, ["semantic_pair"])
    motif_summary = group_summary(classified, ["motif"])
    fields = field_summary(classified)

    near_miss = classified[classified["prefilter_class"].isin(["mechanism_keep_probe", "control_polluted_near_miss"])].copy()
    near_miss = near_miss.sort_values(
        ["prefilter_class", "prefilter_survival_score", "recent_sortino", "min_oos_floor_sortino"],
        ascending=[True, False, False, False],
    )

    classified.to_csv(runtime / "a7v3s4_rejection_classification.csv", index=False)
    pair_motif.to_csv(runtime / "a7v3s4_pair_motif_prefilter_summary.csv", index=False)
    pair_summary.to_csv(runtime / "a7v3s4_semantic_pair_summary.csv", index=False)
    motif_summary.to_csv(runtime / "a7v3s4_motif_summary.csv", index=False)
    fields.to_csv(runtime / "a7v3s4_field_failure_summary.csv", index=False)
    near_miss.to_csv(runtime / "a7v3s4_near_miss_candidates.csv", index=False)
    rules = build_prefilter_rules(pair_motif)
    write_json(runtime / "a7v3s4_search_space_prefilter_rules.json", rules)

    class_summary = (
        classified.groupby("prefilter_class", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    reason_summary = pd.read_csv(REPO / "runtime" / "a7v3s3_strict_reward_early_stop_20260613" / "a7v3s3_early_stop_rejection_reason_summary.csv")
    manifest = {
        "stage": "A7V3S4_NEAR_MISS_PREFILTER_AUDIT",
        "generated_at": now_utc(),
        "input_rejections": str(DEFAULT_REJECTIONS),
        "runtime": str(runtime),
        "report": str(report),
        "input_rows": int(rejected.shape[0]),
        "mechanism_keep_probe_rows": int((classified["prefilter_class"] == "mechanism_keep_probe").sum()),
        "control_polluted_near_miss_rows": int((classified["prefilter_class"] == "control_polluted_near_miss").sum()),
        "hard_block_pair_motif_count": len(rules["hard_block_pair_motif"]),
        "redesign_pair_motif_count": len(rules["redesign_pair_motif_not_reward_as_is"]),
        "keep_reduced_cap_pair_motif_count": len(rules["keep_reduced_cap_mechanism_probe"]),
        "decision": "PASS_A7V3S4_PREFILTER_RULES_BUILT" if len(rules["hard_block_pair_motif"]) else "HOLD_A7V3S4_NO_HARD_BLOCK_RULES",
        "authorizes_continue_same_a7v3s3_queue": False,
        "authorizes_prefiltered_queue_build": True,
        "authorizes_alpha_proof": False,
    }
    write_json(runtime / "a7v3s4_manifest.json", manifest)

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        "\n".join(
            [
                "# CRYPTO A7V3S4 Near-Miss Prefilter Audit - 20260613",
                "",
                "## Decision",
                "",
                f"`{manifest['decision']}`",
                "",
                "A7V3S4 audits the A7V3S3 strict-reward early-stop rejections and converts the failure pattern into a pre-reward search-space filter. It does not authorize alpha proof, shadow, paper, or live execution.",
                "",
                "## Input",
                "",
                f"- Rejection rows: `{manifest['input_rows']}`",
                f"- Mechanism keep probes: `{manifest['mechanism_keep_probe_rows']}`",
                f"- Control-polluted near misses: `{manifest['control_polluted_near_miss_rows']}`",
                f"- Hard-block pair/motif rules: `{manifest['hard_block_pair_motif_count']}`",
                f"- Redesign-not-reward-as-is pair/motif rules: `{manifest['redesign_pair_motif_count']}`",
                "",
                "## Rejection Reasons",
                "",
                md_table(reason_summary, 20),
                "",
                "## Prefilter Classes",
                "",
                md_table(class_summary, 20),
                "",
                "## Pair/Motif Decisions",
                "",
                md_table(pair_motif[["semantic_pair", "motif", "rows", "mechanism_keep_probe", "control_polluted_near_miss", "control_dom_rate", "lag_stale_dom_rate", "median_min_oos_floor_sortino", "prefilter_decision"]], 40),
                "",
                "## Field Failure Summary",
                "",
                md_table(fields[["field", "rows", "mechanism_keep_probe", "control_polluted_near_miss", "control_dom_rate", "lag_stale_dom_rate", "oos_floor_clean_rate", "stress_floor_clean_rate"]], 40),
                "",
                "## Interpretation",
                "",
                "The A7V3S3 queue is not merely under-sampled. Its early rejected candidates are dominated by OOS floor failure, control dominance, and lag/stale dominance. A7V3S4 therefore moves these constraints upstream: candidate generation should not send known control/stale-dominated pair/motif patterns into expensive reward evaluation.",
                "",
                "Mechanism keep probes, if any, should be carried forward only under reduced caps. Control-polluted near misses should be redesigned, not rewarded as-is.",
                "",
                "## Outputs",
                "",
                f"- Runtime: `{runtime}`",
                "- `a7v3s4_rejection_classification.csv`",
                "- `a7v3s4_pair_motif_prefilter_summary.csv`",
                "- `a7v3s4_field_failure_summary.csv`",
                "- `a7v3s4_near_miss_candidates.csv`",
                "- `a7v3s4_search_space_prefilter_rules.json`",
                "- `a7v3s4_manifest.json`",
                "",
                "## Authorization",
                "",
                "Allowed next: build a prefiltered candidate queue using `a7v3s4_search_space_prefilter_rules.json`.",
                "",
                "Not allowed: continue the same A7V3S3 queue, alpha proof, shadow, paper, or live execution.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
