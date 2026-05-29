from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al2z4f_broader_non_oi_preflight_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z4F_BROADER_NON_OI_PREFLIGHT_FORENSIC_20260529.md"
Z4_MANIFEST = REPO / "runtime" / "a7al2z4_broader_non_oi_numeric_replay_preflight" / "a7al2z4_manifest.json"
Z4_DECISIONS = REPO / "runtime" / "a7al2z4_broader_non_oi_numeric_replay_preflight" / "a7al2z4_candidate_decisions.csv"
Z4_METRICS = REPO / "runtime" / "a7al2z4_broader_non_oi_numeric_replay_preflight" / "a7al2z4_candidate_variant_metrics.csv"

PRE_MAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
CONTROL_VARIANTS = ["wrong_lag_future_24h", "wrong_lag_stale_168h", "time_shuffle", "symbol_shuffle", "same_family_random"]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def split_metric(metrics: pd.DataFrame, cid: str, variant: str, split: str) -> float:
    sub = metrics[
        metrics["candidate_id"].eq(cid)
        & metrics["variant"].eq(variant)
        & metrics["split"].eq(split)
    ]
    return float(sub["mean_spread_24h"].iloc[0]) if len(sub) else np.nan


def control_forensic(decisions: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for row in decisions.to_dict("records"):
        cid = str(row["candidate_id"])
        orientation = float(row["orientation_from_train"])
        for split in PRE_MAY_SPLITS:
            original = abs(orientation * split_metric(metrics, cid, "original", split))
            for variant in CONTROL_VARIANTS:
                control = abs(orientation * split_metric(metrics, cid, variant, split))
                ratio = control / original if np.isfinite(original) and original > 1e-12 and np.isfinite(control) else np.nan
                rows.append(
                    {
                        "candidate_id": cid,
                        "objective_family": row["objective_family"],
                        "split": split,
                        "control_variant": variant,
                        "oriented_original_abs": original,
                        "oriented_control_abs": control,
                        "control_ratio": ratio,
                        "control_dominates": bool(np.isfinite(ratio) and ratio >= 1.0),
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    z4 = read_json(Z4_MANIFEST)
    if not z4 or z4.get("eval_error_count", 1) != 0:
        raise SystemExit("A7AL-2Z4 must complete with zero eval errors before forensic")
    decisions = pd.read_csv(Z4_DECISIONS)
    metrics = pd.read_csv(Z4_METRICS)
    controls = control_forensic(decisions, metrics)

    split_rows = []
    for row in decisions.to_dict("records"):
        vals = {
            "validation_2025H1": row["oriented_validation_spread"],
            "test_2025H2": row["oriented_test_spread"],
            "recent_oos_2026JanApr": row["oriented_recent_spread"],
        }
        split_rows.append(
            {
                "candidate_id": row["candidate_id"],
                "objective_family": row["objective_family"],
                **{f"{k}_positive": bool(np.isfinite(v) and v > 0) for k, v in vals.items()},
                "premay_positive_split_count": int(sum(np.isfinite(v) and v > 0 for v in vals.values())),
                "premay_spread_sum": float(sum(v for v in vals.values() if np.isfinite(v))),
                "decision": row["decision"],
            }
        )
    split_profile = pd.DataFrame(split_rows)
    family = (
        decisions.groupby("objective_family", dropna=False)
        .agg(
            candidate_count=("candidate_id", "count"),
            pre_may_positive_count=("pre_may_positive", "sum"),
            lag_ok_count=("lag_ok", "sum"),
            may_stress_clean_count=("may_stress_clean", "sum"),
            median_control_ratio=("control_dominance_ratio_premay_max", "median"),
        )
        .reset_index()
    )
    decision_family = (
        decisions.groupby(["objective_family", "decision"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["objective_family", "count"], ascending=[True, False])
    )
    control_summary = (
        controls.groupby(["objective_family", "control_variant"], dropna=False)
        .agg(
            median_control_ratio=("control_ratio", "median"),
            max_control_ratio=("control_ratio", "max"),
            dominated_count=("control_dominates", "sum"),
        )
        .reset_index()
        .sort_values(["objective_family", "dominated_count"], ascending=[True, False])
    )
    near_miss = decisions[
        decisions["pre_may_positive"].astype(str).str.lower().isin(["true", "1"])
    ].copy()
    near_miss = near_miss.sort_values(
        ["control_dominance_ratio_premay_max", "oriented_recent_spread"],
        ascending=[True, False],
    )

    pre_may_positive_count = int(decisions["pre_may_positive"].astype(str).str.lower().isin(["true", "1"]).sum())
    control_dominated_count = int(decisions["decision"].eq("HOLD_A7AL2Z4_CONTROL_DOMINATED").sum())
    lag_fragile_count = int(decisions["decision"].eq("HOLD_A7AL2Z4_ONE_BAR_LAG_FRAGILE").sum())
    pre_may_unstable_count = int(decisions["decision"].eq("HOLD_A7AL2Z4_PRE_MAY_UNSTABLE").sum())
    decision = (
        "HOLD_A7AL2Z4F_PRE_MAY_SIGNAL_CONTROL_OR_LAG_FRAGILE"
        if pre_may_positive_count > 0
        else "HOLD_A7AL2Z4F_BROADER_NON_OI_PRE_MAY_STRUCTURE_ABSENT"
    )
    manifest = {
        "stage": "A7AL-2Z4F",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_forensic_only": True,
        "executes_replay": False,
        "executes_generation": False,
        "executes_training": False,
        "authorizes_same_pool_expansion": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "candidate_count": int(len(decisions)),
        "pre_may_positive_count": pre_may_positive_count,
        "pre_may_unstable_count": pre_may_unstable_count,
        "control_dominated_count": control_dominated_count,
        "lag_fragile_count": lag_fragile_count,
        "stress_clean_count": int(z4.get("stress_clean_clue_count", 0)),
        "may_veto_count": int(z4.get("pre_may_clue_may_veto_count", 0)),
        "uses_may_in_selector": False,
    }

    family.to_csv(RUNTIME / "a7al2z4f_family_failure_profile.csv", index=False)
    decision_family.to_csv(RUNTIME / "a7al2z4f_family_decision_breakdown.csv", index=False)
    split_profile.to_csv(RUNTIME / "a7al2z4f_split_stability_profile.csv", index=False)
    controls.to_csv(RUNTIME / "a7al2z4f_control_ratio_detail.csv", index=False)
    control_summary.to_csv(RUNTIME / "a7al2z4f_control_ratio_summary.csv", index=False)
    near_miss.to_csv(RUNTIME / "a7al2z4f_premay_near_miss_candidates.csv", index=False)
    write_json(RUNTIME / "a7al2z4f_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z4f_authorization_matrix.json",
        {
            "A7AL-2Z4F": {"status": decision},
            "same_pool_expansion": {"authorized": False},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AL-2Z4F BROADER NON-OI PREFLIGHT FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "Z4F explains the Z4 numeric preflight hold. It does not run new replay, generation, training, or proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Failure Profile",
        "",
        md_table(family),
        "",
        "## Family Decision Breakdown",
        "",
        md_table(decision_family),
        "",
        "## Control Summary",
        "",
        md_table(control_summary, 80),
        "",
        "## Premay Near Misses",
        "",
        md_table(near_miss, 40),
        "",
        "## Boundary",
        "",
        "```text",
        "Same-pool expansion is not authorized.",
        "The useful evidence is failure attribution: most candidates are pre-May unstable; the few pre-May positives are rejected by control or lag gates.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
