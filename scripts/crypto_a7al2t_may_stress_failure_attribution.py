from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "runtime" / "a7al2t_may_stress_failure_attribution"
REPORT = REPO / "reports" / "CRYPTO_A7AL2T_MAY_STRESS_FAILURE_ATTRIBUTION_20260528.md"

A7AL2S_MANIFEST = REPO / "runtime" / "a7al2s_local_followup_contract" / "a7al2s_manifest.json"
A7AL2S_TIERS = REPO / "runtime" / "a7al2s_local_followup_contract" / "a7al2s_candidate_tiers.csv"
A7AL2R_INPUT = REPO / "runtime" / "a7al2r_local_forensic" / "a7al2r_input_candidates.csv"
A7AL2R_VARIANTS = REPO / "runtime" / "a7al2r_local_forensic" / "a7al2r_variant_metrics.csv"
A7AL2R_CONTROL = REPO / "runtime" / "a7al2r_local_forensic" / "a7al2r_control_dominance.csv"
A7AL2R_SYMBOL = REPO / "runtime" / "a7al2r_local_forensic" / "a7al2r_symbol_contribution.csv"
A7AL2R_MONTH = REPO / "runtime" / "a7al2r_local_forensic" / "a7al2r_month_contribution.csv"
A7AL2R_LATENT = REPO / "runtime" / "a7al2r_local_forensic" / "a7al2r_latent_state_contribution.csv"
A7AL2R_TOP_HOURS = REPO / "runtime" / "a7al2r_local_forensic" / "a7al2r_top_gain_loss_hours.csv"

EVAL_PREMAY_SPLITS = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]
MAY_SPLIT = "known_may2026_stress"
ENTRY_LABELS = ["label_t1_to_t25", "label_t2_to_t26"]
CONTROL_VARIANTS = [
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "same_family_random",
    "time_shuffle",
    "symbol_shuffle",
]


def utc_now() -> str:
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
        if pd.api.types.is_object_dtype(view[col]) or pd.api.types.is_string_dtype(view[col]):
            view[col] = view[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except Exception:
        return "```\n" + view.to_string(index=False) + "\n```"


def require(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required artifact: {path}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in [
        A7AL2S_MANIFEST,
        A7AL2S_TIERS,
        A7AL2R_INPUT,
        A7AL2R_VARIANTS,
        A7AL2R_CONTROL,
        A7AL2R_SYMBOL,
        A7AL2R_MONTH,
        A7AL2R_LATENT,
        A7AL2R_TOP_HOURS,
    ]:
        require(path)

    s_manifest = read_json(A7AL2S_MANIFEST)
    if not s_manifest.get("authorizes_a7al2t_may_stress_failure_attribution"):
        raise SystemExit("A7AL-2S does not authorize A7AL-2T")

    tiers = pd.read_csv(A7AL2S_TIERS)
    inputs = pd.read_csv(A7AL2R_INPUT)
    variants = pd.read_csv(A7AL2R_VARIANTS)
    control = pd.read_csv(A7AL2R_CONTROL)
    symbol = pd.read_csv(A7AL2R_SYMBOL)
    month = pd.read_csv(A7AL2R_MONTH)
    latent = pd.read_csv(A7AL2R_LATENT)
    top_hours = pd.read_csv(A7AL2R_TOP_HOURS)

    original = variants[variants["variant"].eq("original") & variants["entry_label"].isin(ENTRY_LABELS)].copy()
    pre = original[original["split"].isin(EVAL_PREMAY_SPLITS)].copy()
    may = original[original["split"].eq(MAY_SPLIT)].copy()

    split_contrast = pre.merge(
        may[["candidate_id", "entry_label", "mean_oriented_spread", "net_mean_spread_10bps", "hourly_tstat_naive"]].rename(
            columns={
                "mean_oriented_spread": "may_mean_oriented_spread",
                "net_mean_spread_10bps": "may_net_mean_spread_10bps",
                "hourly_tstat_naive": "may_hourly_tstat_naive",
            }
        ),
        on=["candidate_id", "entry_label"],
        how="left",
    )
    split_contrast["stress_delta_vs_split"] = split_contrast["may_mean_oriented_spread"] - split_contrast["mean_oriented_spread"]
    split_contrast["stress_ratio_vs_split"] = split_contrast["may_mean_oriented_spread"] / split_contrast["mean_oriented_spread"].replace(0, pd.NA)
    split_contrast["sign_flip_to_may"] = (split_contrast["mean_oriented_spread"] > 0) & (split_contrast["may_mean_oriented_spread"] < 0)

    controls = variants[
        variants["variant"].isin(CONTROL_VARIANTS)
        & variants["entry_label"].isin(ENTRY_LABELS)
        & variants["split"].eq(MAY_SPLIT)
    ].copy()
    if not controls.empty:
        controls["abs_control_spread"] = controls["mean_oriented_spread"].abs()
        control_mode_failure = controls.sort_values("abs_control_spread", ascending=False).groupby(["candidate_id", "entry_label"], as_index=False).head(3)
    else:
        control_mode_failure = pd.DataFrame()

    may_control = control[control["split"].eq(MAY_SPLIT)].copy()
    premay_control = control[control["split"].isin(EVAL_PREMAY_SPLITS)].copy()
    premay_control_summary = (
        premay_control.groupby(["candidate_id", "entry_label"], as_index=False)
        .agg(
            premay_max_control_ratio=("control_ratio", "max"),
            premay_hold_count=("gate", lambda s: int((s == "HOLD_CONTROL_DOMINATED").sum())),
            premay_warning_count=("gate", lambda s: int((s == "WARN_CONTROL_CLOSE").sum())),
        )
    )
    may_control_summary = (
        may_control.groupby(["candidate_id", "entry_label"], as_index=False)
        .agg(
            may_max_control_ratio=("control_ratio", "max"),
            may_hold_count=("gate", lambda s: int((s == "HOLD_CONTROL_DOMINATED").sum())),
            may_gates=("gate", lambda s: ";".join(sorted(set(map(str, s))))),
        )
    )

    original_summary = (
        original[original["split"].isin(EVAL_PREMAY_SPLITS + [MAY_SPLIT])]
        .pivot_table(index=["candidate_id", "entry_label"], columns="split", values="mean_oriented_spread", aggfunc="first")
        .reset_index()
    )
    original_summary["premay_eval_min_spread"] = original_summary[EVAL_PREMAY_SPLITS].min(axis=1)
    original_summary["premay_eval_mean_spread"] = original_summary[EVAL_PREMAY_SPLITS].mean(axis=1)
    original_summary["may_spread"] = original_summary[MAY_SPLIT]
    original_summary["may_vs_premay_mean_delta"] = original_summary["may_spread"] - original_summary["premay_eval_mean_spread"]
    original_summary["may_sign_flip"] = (original_summary["premay_eval_min_spread"] > 0) & (original_summary["may_spread"] < 0)

    candidate_failure = original_summary.merge(premay_control_summary, on=["candidate_id", "entry_label"], how="left")
    candidate_failure = candidate_failure.merge(may_control_summary, on=["candidate_id", "entry_label"], how="left")
    candidate_failure = candidate_failure.merge(
        tiers[["candidate_id", "a7al2s_tier", "warnings", "control_ratio_premay_max"]],
        on="candidate_id",
        how="left",
    )
    candidate_failure = candidate_failure.merge(
        inputs[["candidate_id", "expression", "fields", "field_families", "pattern_id", "oi_window", "price_window", "source", "parent_seed_id"]],
        on="candidate_id",
        how="left",
    )
    for text_col in ["warnings", "a7al2s_tier", "may_gates", "expression", "fields", "field_families", "parent_seed_id"]:
        if text_col in candidate_failure.columns:
            candidate_failure[text_col] = candidate_failure[text_col].fillna("")

    def failure_label(row: pd.Series) -> str:
        labels: list[str] = []
        if bool(row.get("may_sign_flip", False)):
            labels.append("MAY_SIGN_FLIP")
        if float(row.get("may_max_control_ratio", 0.0) or 0.0) >= 1.0:
            labels.append("MAY_CONTROL_DOMINATED")
        if str(row.get("warnings", "") or "").strip():
            labels.append("PREMAY_CONTROL_CLOSE")
        if not labels:
            labels.append("MAY_STRESS_WEAKNESS")
        return "|".join(labels)

    candidate_failure["a7al2t_failure_label"] = candidate_failure.apply(failure_label, axis=1)
    candidate_failure["may_used_for_selection"] = False
    candidate_failure["eligible_for_expansion"] = False

    may_symbol = symbol[symbol["split"].eq(MAY_SPLIT)].copy()
    may_month = month[month["split"].eq(MAY_SPLIT)].copy()
    may_latent = latent[latent["split"].eq(MAY_SPLIT)].copy()
    may_top_loss_hours = top_hours[(top_hours["split"].eq(MAY_SPLIT)) & (top_hours["side"].eq("loss"))].copy()

    action_matrix = pd.DataFrame(
        [
            {
                "action": "company_full_a7al2q2r",
                "status": "PREFERRED_NEXT_IF_COMPANY_PATH_AVAILABLE",
                "reason": "local run only deep-audited 16; full 128 replay should test whether May failure is local-pilot artifact",
            },
            {
                "action": "local_mutation_expansion",
                "status": "NOT_AUTHORIZED",
                "reason": "all candidates sign-flip and become control-dominated in May stress",
            },
            {
                "action": "a7al2u_objective_repair_contract",
                "status": "AUTHORIZED_FOR_CONTRACT_ONLY",
                "reason": "future selector may penalize pre-May structures that resemble stress-control behavior without using May labels",
            },
            {
                "action": "alpha_proof_shadow_paper_live",
                "status": "NOT_AUTHORIZED",
                "reason": "known stress failure and local diagnostic-only evidence",
            },
        ]
    )

    sign_flip_count = int(candidate_failure["may_sign_flip"].sum())
    may_control_dominated_count = int((candidate_failure["may_max_control_ratio"] >= 1.0).sum())
    decision = "HOLD_A7AL2T_MAY_STRESS_FAILURE_CONFIRMED_NO_EXPANSION"
    manifest = {
        "generated_at": utc_now(),
        "decision": decision,
        "input_a7al2s_decision": s_manifest.get("decision"),
        "candidate_entry_rows": int(len(candidate_failure)),
        "unique_candidates": int(candidate_failure["candidate_id"].nunique()),
        "sign_flip_rows": sign_flip_count,
        "may_control_dominated_rows": may_control_dominated_count,
        "authorizes_company_full_a7al2q2r": True,
        "authorizes_a7al2u_objective_repair_contract": True,
        "authorizes_local_expansion": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may_for_selection": False,
        "uses_may_for_ranking": False,
        "uses_may_for_mutation": False,
        "blockers": [
            "all_local_candidates_may_sign_flip",
            "all_local_candidates_may_control_dominated",
        ],
        "required_next": "Prefer company full A7AL-2Q/2R. If unavailable, draft A7AL-2U objective-repair contract; do not run local expansion.",
    }

    candidate_failure.to_csv(OUT_DIR / "a7al2t_candidate_failure_summary.csv", index=False)
    split_contrast.to_csv(OUT_DIR / "a7al2t_split_contrast.csv", index=False)
    control_mode_failure.to_csv(OUT_DIR / "a7al2t_control_mode_failure.csv", index=False)
    may_symbol.to_csv(OUT_DIR / "a7al2t_may_symbol_concentration.csv", index=False)
    may_month.to_csv(OUT_DIR / "a7al2t_may_month_concentration.csv", index=False)
    may_latent.to_csv(OUT_DIR / "a7al2t_may_latent_concentration.csv", index=False)
    may_top_loss_hours.to_csv(OUT_DIR / "a7al2t_may_top_loss_hours.csv", index=False)
    action_matrix.to_csv(OUT_DIR / "a7al2t_action_matrix.csv", index=False)
    write_json(OUT_DIR / "a7al2t_manifest.json", manifest)

    report = f"""# CRYPTO A7AL-2T May-Stress Failure Attribution

Generated: {manifest["generated_at"]}

## Decision

```text
{decision}
```

This stage performs attribution only. It uses May as a post-selection stress/failure label, not as a selector, ranker, mutation prior, or training target.

## Manifest

```json
{json.dumps(manifest, indent=2, sort_keys=True)}
```

## Candidate Failure Summary

{md_table(candidate_failure, 40)}

## Split Contrast

{md_table(split_contrast[["candidate_id", "entry_label", "split", "mean_oriented_spread", "may_mean_oriented_spread", "stress_delta_vs_split", "stress_ratio_vs_split", "sign_flip_to_may"]], 60)}

## May Control Mode Failure

{md_table(control_mode_failure[["candidate_id", "entry_label", "variant", "mean_oriented_spread", "abs_control_spread", "hourly_tstat_naive"]], 40) if not control_mode_failure.empty else "`<empty>`"}

## May Symbol Concentration

{md_table(may_symbol.head(40), 40)}

## May Latent Concentration

{md_table(may_latent.head(40), 40)}

## Action Matrix

{md_table(action_matrix, 20)}

## Boundary

```text
Authorized:
  company full A7AL-2Q/2R if company path is available
  A7AL-2U objective-repair contract drafting only

Not authorized:
  local mutation expansion
  large search
  alpha proof
  shadow / paper / live
```
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
