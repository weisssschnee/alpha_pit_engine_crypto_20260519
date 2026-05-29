from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ae2_label_adequacy_role_review"
REPORT = REPO / "reports" / "CRYPTO_A7AE2_LABEL_ADEQUACY_ROLE_REVIEW_20260529.md"

A7AE1_MANIFEST = REPO / "runtime" / "a7ae1_label_adequacy_response_map" / "a7ae1_manifest.json"
A7AE1_RESPONSE = REPO / "runtime" / "a7ae1_label_adequacy_response_map" / "a7ae1_label_adequacy_response_map.csv"
A7AE1_CANDIDATES = REPO / "runtime" / "a7ae1_label_adequacy_response_map" / "a7ae1_label_adequacy_candidates.csv"


RAW_RELATIVE_LABELS = {"L0_raw_forward_return", "L1_cross_sectional_relative_return"}
BETA_NEUTRAL_LABELS = {"L2_BTC_ETH_beta_residual_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"}
DOWNSIDE_LABELS = {"L6_downside_avoidance"}
RANK_LABELS = {"L7_ranked_future_return"}


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
    view = df.head(max_rows).copy().astype(str)
    for col in view.columns:
        view[col] = view[col].str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False, disable_numparse=True)


def join_unique(values: pd.Series) -> str:
    parts = sorted({str(x) for x in values.dropna() if str(x) and str(x) != "nan"})
    return "|".join(parts)


def classify(row: pd.Series) -> tuple[str, str]:
    if int(row["raw_relative_candidate_count"]) > 0:
        return "raw_relative_signal_candidate", "has_raw_or_cross_sectional_relative_response"
    if int(row["beta_neutral_candidate_count"]) > 0:
        return "beta_or_neutralized_signal_candidate", "has_beta_liquidity_or_vol_adjusted_response"
    if int(row["downside_candidate_count"]) > 0:
        return "downside_avoidance_signal_candidate", "has_downside_avoidance_response_only"
    if int(row["rank_candidate_count"]) > 0:
        return "rank_label_diagnostic_only", "rank_label_response_without_non_rank_translation"
    if int(row["premay_stable_count"]) > 0 and int(row["control_like_count"]) >= int(row["premay_stable_count"]):
        return "control_like_or_risk_exposure", "premay_stable_but_control_like"
    if int(row["premay_stable_count"]) > 0:
        return "regime_state_or_interaction_input", "premay_stable_without_clean_candidate_gate"
    return "weak_or_unstable", "mostly_premay_unstable"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest1 = read_json(A7AE1_MANIFEST)
    if not manifest1.get("authorizes_feature_role_review"):
        raise SystemExit("A7AE-1 does not authorize A7AE-2")

    response = pd.read_csv(A7AE1_RESPONSE)
    candidates = pd.read_csv(A7AE1_CANDIDATES)
    response["is_candidate"] = response["decision"].eq("A7AE1_LABEL_ADEQUACY_RESPONSE_CANDIDATE")
    response["is_premay_stable"] = response["premay_all_positive"].astype(str).str.lower().isin(["true", "1"])
    response["is_control_like"] = response["decision"].eq("HOLD_A7AE1_CONTROL_LIKE")
    response["is_lag_fragile"] = response["decision"].eq("HOLD_A7AE1_LAG_FRAGILE")
    response["is_unstable"] = response["decision"].eq("HOLD_A7AE1_PRE_MAY_UNSTABLE")

    rows: list[dict[str, Any]] = []
    for field, sub in response.groupby("field_name", dropna=False):
        cand = sub[sub["is_candidate"]]
        raw_rel = cand[cand["label_family"].isin(RAW_RELATIVE_LABELS)]
        beta = cand[cand["label_family"].isin(BETA_NEUTRAL_LABELS)]
        downside = cand[cand["label_family"].isin(DOWNSIDE_LABELS)]
        rank = cand[cand["label_family"].isin(RANK_LABELS)]
        base = sub.iloc[0]
        row = {
            "field_name": field,
            "field_family": base.get("field_family", ""),
            "source_family": base.get("source_family", ""),
            "feature_class": base.get("feature_class", ""),
            "total_tests": int(len(sub)),
            "candidate_count": int(len(cand)),
            "raw_relative_candidate_count": int(len(raw_rel)),
            "beta_neutral_candidate_count": int(len(beta)),
            "downside_candidate_count": int(len(downside)),
            "rank_candidate_count": int(len(rank)),
            "premay_stable_count": int(sub["is_premay_stable"].sum()),
            "control_like_count": int(sub["is_control_like"].sum()),
            "lag_fragile_count": int(sub["is_lag_fragile"].sum()),
            "premay_unstable_count": int(sub["is_unstable"].sum()),
            "best_label_families": join_unique(cand["label_family"]),
            "best_horizons": join_unique(cand["label_horizon_h"].astype(str)),
            "best_transforms": join_unique(cand["transform"]),
        }
        role, reason = classify(pd.Series(row))
        row["feature_role"] = role
        row["reason"] = reason
        rows.append(row)

    role = pd.DataFrame(rows)
    role = role[
        [
            "field_name",
            "field_family",
            "source_family",
            "feature_class",
            "feature_role",
            "reason",
            "total_tests",
            "candidate_count",
            "raw_relative_candidate_count",
            "beta_neutral_candidate_count",
            "downside_candidate_count",
            "rank_candidate_count",
            "premay_stable_count",
            "control_like_count",
            "lag_fragile_count",
            "premay_unstable_count",
            "best_label_families",
            "best_horizons",
            "best_transforms",
        ]
    ].sort_values(
        [
            "raw_relative_candidate_count",
            "beta_neutral_candidate_count",
            "downside_candidate_count",
            "rank_candidate_count",
            "candidate_count",
        ],
        ascending=False,
    )
    seed_policy = role[
        role["feature_role"].isin(
            [
                "raw_relative_signal_candidate",
                "beta_or_neutralized_signal_candidate",
                "downside_avoidance_signal_candidate",
            ]
        )
    ].copy()
    family = (
        role.groupby(["field_family", "feature_role"], dropna=False)
        .agg(field_count=("field_name", "count"), candidate_count=("candidate_count", "sum"))
        .reset_index()
        .sort_values(["candidate_count", "field_count"], ascending=False)
    )

    decision = (
        "PASS_A7AE2_LABEL_ADEQUACY_ROLES_READY_FOR_SELECTOR_REWRITE_REVIEW"
        if len(seed_policy) > 0
        else "HOLD_A7AE2_NO_LABEL_ADEQUATE_SEED_FIELDS"
    )
    manifest = {
        "stage": "A7AE-2",
        "generated_at": now_utc(),
        "decision": decision,
        "source_a7ae1_decision": manifest1.get("decision"),
        "executes_role_review": True,
        "executes_search": False,
        "executes_training": False,
        "authorizes_selector_rewrite_review": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "field_count": int(len(role)),
        "seed_field_count": int(len(seed_policy)),
        "raw_relative_seed_field_count": int((seed_policy["feature_role"] == "raw_relative_signal_candidate").sum()),
        "beta_neutral_seed_field_count": int((seed_policy["feature_role"] == "beta_or_neutralized_signal_candidate").sum()),
        "downside_seed_field_count": int((seed_policy["feature_role"] == "downside_avoidance_signal_candidate").sum()),
        "uses_may": False,
    }
    role.to_csv(RUNTIME / "a7ae2_feature_role_update.csv", index=False)
    seed_policy.to_csv(RUNTIME / "a7ae2_selector_seed_policy.csv", index=False)
    family.to_csv(RUNTIME / "a7ae2_family_role_summary.csv", index=False)
    candidates.to_csv(RUNTIME / "a7ae2_source_candidates_snapshot.csv", index=False)
    write_json(RUNTIME / "a7ae2_manifest.json", manifest)
    write_json(
        RUNTIME / "a7ae2_authorization_matrix.json",
        {
            "A7AE-2": {"status": decision},
            "selector_rewrite_review": {"authorized": True},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AE-2 LABEL ADEQUACY ROLE REVIEW",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AE-2 converts the extended label response map into feature roles. It does not generate formulas, search, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Selector Seed Policy",
        "",
        md_table(seed_policy, 80),
        "",
        "## Family Role Summary",
        "",
        md_table(family, 120),
        "",
        "## Feature Role Update",
        "",
        md_table(role, 120),
        "",
        "## Boundary",
        "",
        "```text",
        "Formula search remains not authorized.",
        "A7AE-2 only updates feature roles after label adequacy diagnostics.",
        "May is not used.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
