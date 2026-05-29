from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7af1_role_aware_selector_dryrun"
REPORT = REPO / "reports" / "CRYPTO_A7AF1_ROLE_AWARE_SELECTOR_DRYRUN_20260529.md"

A7AF0_MANIFEST = REPO / "runtime" / "a7af0_role_aware_selector_contract" / "a7af0_manifest.json"
A7AF0_TIERS = REPO / "runtime" / "a7af0_role_aware_selector_contract" / "a7af0_selector_tiers.csv"
A7AF0_ROLE_CAPS = REPO / "runtime" / "a7af0_role_aware_selector_contract" / "a7af0_role_caps.json"
A7AE1_CANDIDATES = REPO / "runtime" / "a7ae1_label_adequacy_response_map" / "a7ae1_label_adequacy_candidates.csv"
A7AE2_SEEDS = REPO / "runtime" / "a7ae2_label_adequacy_role_review" / "a7ae2_selector_seed_policy.csv"


TIER_ORDER = {
    "T0_raw_relative_alpha": 0,
    "T1_beta_neutral_alpha_diagnostic": 1,
    "T2_downside_risk_defense": 2,
}


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


def finite_float(value: Any, default: float = 0.0) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    return f if math.isfinite(f) else default


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def split_pipe(value: Any) -> set[str]:
    return {part.strip() for part in str(value).split("|") if part.strip()}


def assign_tier(row: pd.Series, role_by_field: dict[str, str]) -> str:
    role = role_by_field.get(str(row["field_name"]), "")
    label = str(row["label_family"])
    if role == "raw_relative_signal_candidate" and label in {
        "L0_raw_forward_return",
        "L1_cross_sectional_relative_return",
        "L2_BTC_ETH_beta_residual_return",
        "L3_liquidity_tier_relative_return",
        "L5_vol_adjusted_return",
    }:
        return "T0_raw_relative_alpha"
    if role == "beta_or_neutralized_signal_candidate" and label in {
        "L2_BTC_ETH_beta_residual_return",
        "L3_liquidity_tier_relative_return",
        "L5_vol_adjusted_return",
    }:
        return "T1_beta_neutral_alpha_diagnostic"
    if role == "downside_avoidance_signal_candidate" and label == "L6_downside_avoidance":
        return "T2_downside_risk_defense"
    return "blocked_role_label_mismatch"


def blueprint(row: pd.Series) -> str:
    orient = "short_high" if finite_float(row.get("orientation_from_train"), default=1.0) < 0 else "long_high"
    return (
        f"role_response::{row['field_name']}::{row['transform']}::"
        f"{row['label_family']}::{int(row['label_horizon_h'])}h::{orient}"
    )


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7af0 = read_json(A7AF0_MANIFEST)
    if not a7af0.get("authorizes_a7af1_role_aware_selector_dryrun"):
        raise SystemExit("A7AF-0 does not authorize A7AF-1")

    tiers = pd.read_csv(A7AF0_TIERS)
    role_caps = read_json(A7AF0_ROLE_CAPS)
    seeds = pd.read_csv(A7AE2_SEEDS)
    candidates = pd.read_csv(A7AE1_CANDIDATES)
    role_by_field = dict(zip(seeds["field_name"].astype(str), seeds["feature_role"].astype(str)))
    seed_fields = set(role_by_field)
    tier_allowed = {row["selector_tier"]: split_pipe(row["allowed_labels"]) for _, row in tiers.iterrows()}
    tier_caps = {row["selector_tier"]: int(row["queue_cap"]) for _, row in tiers.iterrows()}

    rows: list[dict[str, Any]] = []
    for idx, row in candidates.iterrows():
        field = str(row["field_name"])
        label = str(row["label_family"])
        tier = assign_tier(row, role_by_field)
        control_ratio = finite_float(row.get("control_ratio_premay_max"), default=999.0)
        premay_count = int(finite_float(row.get("premay_positive_split_count"), default=0.0))
        lag_ok = str(row.get("lag_ok")).lower() in {"true", "1"}
        premay_all = str(row.get("premay_all_positive")).lower() in {"true", "1"}
        tier_label_ok = tier in tier_allowed and label in tier_allowed[tier]
        gates = {
            "seed_field": field in seed_fields,
            "tier_label_ok": tier_label_ok,
            "control_ratio_lt_1": control_ratio < 1.0,
            "premay_all_positive": premay_all,
            "lag_ok": lag_ok,
            "no_may_used": True,
        }
        reject_reasons = [gate for gate, ok in gates.items() if not ok]
        eligible = not reject_reasons
        orientation = finite_float(row.get("orientation_from_train"), default=1.0)
        validation_tstat = orientation * finite_float(row.get("validation_2025H1_tstat"))
        test_tstat = orientation * finite_float(row.get("test_2025H2_tstat"))
        recent_tstat = orientation * finite_float(row.get("recent_oos_2026JanApr_tstat"))
        validation_no = orientation * finite_float(row.get("validation_2025H1_nonoverlap_min_tstat"))
        test_no = orientation * finite_float(row.get("test_2025H2_nonoverlap_min_tstat"))
        recent_no = orientation * finite_float(row.get("recent_oos_2026JanApr_nonoverlap_min_tstat"))
        robust_floor = min(validation_no, test_no, recent_no)
        control_margin = clamp(1.0 - control_ratio)
        premay_score = clamp(premay_count / 3.0)
        lag_score = clamp(abs(finite_float(row.get("one_bar_lag_recent_oriented"))) / max(abs(finite_float(row.get("recent_oos_2026JanApr_mean_spread"))), 1e-9))
        robust_score = clamp(robust_floor / 5.0)
        role_priority = 1.0 - 0.15 * TIER_ORDER.get(tier, 3)
        selector_score = (
            0.25 * role_priority
            + 0.25 * premay_score
            + 0.25 * control_margin
            + 0.15 * lag_score
            + 0.10 * robust_score
        )
        rows.append(
            {
                "candidate_id": f"a7af1_queue_{idx:03d}",
                "selector_tier": tier,
                "field_name": field,
                "field_family": row.get("field_family", ""),
                "feature_role": role_by_field.get(field, ""),
                "source_family": row.get("source_family", ""),
                "feature_class": row.get("feature_class", ""),
                "transform": row.get("transform", ""),
                "label_family": label,
                "label_horizon_h": int(row.get("label_horizon_h", 0)),
                "orientation_from_train": orientation,
                "control_ratio_premay_max": control_ratio,
                "control_margin": control_margin,
                "premay_positive_split_count": premay_count,
                "premay_score": premay_score,
                "one_bar_lag_recent_oriented": finite_float(row.get("one_bar_lag_recent_oriented")),
                "lag_score": lag_score,
                "validation_oriented_tstat": validation_tstat,
                "test_oriented_tstat": test_tstat,
                "recent_oriented_tstat": recent_tstat,
                "robust_tstat_floor": robust_floor,
                "robust_score": robust_score,
                "role_priority": role_priority,
                "selector_score": selector_score if eligible else -1.0,
                "eligible": eligible,
                "reject_reasons": "|".join(reject_reasons),
                "blueprint": blueprint(row),
                "allowed_next_use": (
                    tiers.set_index("selector_tier").loc[tier, "allowed_next_use"]
                    if eligible and tier in set(tiers["selector_tier"])
                    else "not_allowed"
                ),
            }
        )

    scoreboard = pd.DataFrame(rows).sort_values(
        ["eligible", "selector_tier", "selector_score", "control_margin", "robust_tstat_floor"],
        ascending=[False, True, False, False, False],
    )
    selected_rows: list[dict[str, Any]] = []
    per_field: dict[str, int] = {}
    per_family_tier: dict[tuple[str, str], int] = {}
    max_per_field = int(role_caps.get("max_per_field", 3))
    max_per_family_tier = int(role_caps.get("max_per_field_family_per_tier", 4))
    max_total = int(role_caps.get("max_selected_total", 18))
    for tier in sorted(tier_caps, key=lambda x: TIER_ORDER.get(x, 99)):
        tier_pool = scoreboard[scoreboard["eligible"].eq(True) & scoreboard["selector_tier"].eq(tier)]
        tier_count = 0
        for rec in tier_pool.to_dict("records"):
            field = str(rec["field_name"])
            family = str(rec["field_family"])
            key = (tier, family)
            if per_field.get(field, 0) >= max_per_field:
                continue
            if per_family_tier.get(key, 0) >= max_per_family_tier:
                continue
            selected_rows.append(rec)
            per_field[field] = per_field.get(field, 0) + 1
            per_family_tier[key] = per_family_tier.get(key, 0) + 1
            tier_count += 1
            if tier_count >= tier_caps[tier] or len(selected_rows) >= max_total:
                break
        if len(selected_rows) >= max_total:
            break
    selected = pd.DataFrame(selected_rows)
    if selected.empty:
        selected = pd.DataFrame(columns=scoreboard.columns)
    selected = selected.reset_index(drop=True)
    selected.insert(0, "selector_rank", range(1, len(selected) + 1))

    tier_summary = (
        scoreboard.groupby(["selector_tier"], dropna=False)
        .agg(
            candidates=("candidate_id", "count"),
            eligible=("eligible", "sum"),
            selected=("candidate_id", lambda s: int(s.isin(selected["candidate_id"]).sum()) if not selected.empty else 0),
            unique_fields=("field_name", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
    )
    selected_tier_summary = (
        selected.groupby(["selector_tier"], dropna=False)
        .agg(
            selected=("candidate_id", "count"),
            unique_fields=("field_name", "nunique"),
            unique_families=("field_family", "nunique"),
            max_control_ratio=("control_ratio_premay_max", "max"),
            min_robust_tstat_floor=("robust_tstat_floor", "min"),
        )
        .reset_index()
        if not selected.empty
        else pd.DataFrame()
    )

    raw_selected = int((selected["selector_tier"] == "T0_raw_relative_alpha").sum()) if not selected.empty else 0
    beta_selected = int((selected["selector_tier"] == "T1_beta_neutral_alpha_diagnostic").sum()) if not selected.empty else 0
    downside_selected = int((selected["selector_tier"] == "T2_downside_risk_defense").sum()) if not selected.empty else 0
    decision = (
        "PASS_A7AF1_ROLE_AWARE_SELECTOR_DRYRUN_READY_FOR_A7AG0_CONTRACT"
        if raw_selected >= 2 and beta_selected >= 3 and downside_selected >= 4
        else "HOLD_A7AF1_ROLE_AWARE_SELECTOR_QUEUE_PARTIAL"
    )
    manifest = {
        "stage": "A7AF-1",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_selector_dryrun": True,
        "executes_formula_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "authorizes_a7ag0_role_aware_generation_contract": decision.startswith("PASS_"),
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "candidate_count": int(len(scoreboard)),
        "eligible_count": int(scoreboard["eligible"].sum()),
        "selected_count": int(len(selected)),
        "raw_relative_selected_count": raw_selected,
        "beta_neutral_selected_count": beta_selected,
        "downside_selected_count": downside_selected,
        "selected_field_count": int(selected["field_name"].nunique()) if not selected.empty else 0,
        "selected_family_count": int(selected["field_family"].nunique()) if not selected.empty else 0,
        "uses_may": False,
    }

    scoreboard.to_csv(RUNTIME / "a7af1_selector_scoreboard.csv", index=False)
    selected.to_csv(RUNTIME / "a7af1_selected_queue.csv", index=False)
    tier_summary.to_csv(RUNTIME / "a7af1_tier_summary.csv", index=False)
    selected_tier_summary.to_csv(RUNTIME / "a7af1_selected_tier_summary.csv", index=False)
    write_json(RUNTIME / "a7af1_manifest.json", manifest)
    write_json(
        RUNTIME / "a7af1_authorization_matrix.json",
        {
            "A7AF-1": {"status": decision},
            "a7ag0_role_aware_generation_contract": {"authorized": manifest["authorizes_a7ag0_role_aware_generation_contract"]},
            "formula_search_execution": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )

    lines = [
        "# CRYPTO A7AF-1 ROLE-AWARE SELECTOR DRYRUN",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AF-1 builds a role-aware selector queue from A7AE label adequacy candidates. It does not generate formulas, replay, search, train, or authorize proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Tier Summary",
        "",
        md_table(tier_summary, 80),
        "",
        "## Selected Tier Summary",
        "",
        md_table(selected_tier_summary, 80),
        "",
        "## Selected Queue",
        "",
        md_table(selected, 80),
        "",
        "## Scoreboard Head",
        "",
        md_table(scoreboard.head(120), 120),
        "",
        "## Boundary",
        "",
        "```text",
        "Formula search remains not authorized.",
        "A7AF-1 is a dryrun queue only.",
        "Downside/risk-defense queue is separate from ordinary alpha.",
        "May is not used.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
