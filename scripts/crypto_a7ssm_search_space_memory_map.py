from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ssm_search_space_memory_map"
REPORT = REPO / "reports" / "CRYPTO_A7SSM_SEARCH_SPACE_MEMORY_MAP_20260605.md"

CORE60B = REPO / "runtime" / "a7ffcore60b_target_adequacy_repair_audit"
CORE60C = REPO / "runtime" / "a7ffcore60c_materialization_repair_audit"
CORE60D = REPO / "runtime" / "a7ffcore60d_selector_portfolio_proxy_attribution"
CORE61 = REPO / "runtime" / "a7ffcore61_integrated_repair_plan"


SEMANTIC_TYPES = {
    "basis_premium_like": {"role": "signal_candidate", "behavior": "dense_state_price_dislocation"},
    "price_like": {"role": "risk_exposure_or_interaction", "behavior": "dense_high_beta"},
    "volatility_like": {"role": "regime_or_interaction", "behavior": "dense_risk_state"},
    "funding_like": {"role": "materialization_repair_first", "behavior": "sparse_or_timestamp_sensitive"},
    "positioning_like": {"role": "materialization_repair_first", "behavior": "sparse_or_coverage_sensitive"},
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 50) -> str:
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


def semantic_parts(pair: str) -> list[str]:
    return [p for p in str(pair).split("|") if p]


def route_for_pair(pair: str, activity_ok_rate: float, non_l7_rows: int, selected_l7_share: float) -> tuple[str, str, bool]:
    parts = semantic_parts(pair)
    has_funding_or_positioning = any(p in {"funding_like", "positioning_like"} for p in parts)
    has_basis = "basis_premium_like" in parts
    has_price_or_vol = any(p in {"price_like", "volatility_like"} for p in parts)
    if activity_ok_rate == 0 or has_funding_or_positioning and activity_ok_rate < 0.2:
        return "materialization_repair", "blocked_until_materialized", False
    if non_l7_rows > 0 and has_basis and has_price_or_vol:
        return "target_near_miss_repair", "repair_only", False
    if selected_l7_share > 0.65:
        return "selector_l7_bias_diagnostic", "diagnostic_only", False
    return "diagnostic_memory", "diagnostic_only", False


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    core60b = read_json(CORE60B / "core60b_decision_record.json")
    core60c = read_json(CORE60C / "core60c_decision_record.json")
    core60d = read_json(CORE60D / "core60d_decision_record.json")
    core61 = read_json(CORE61 / "core61_decision_record.json")

    material = read_csv(CORE60C / "core60c_materialization_by_semantic_pair.csv")
    selected_pressure = read_csv(CORE60D / "core60d_l7_pressure_by_semantic_pair.csv")
    route_summary = read_csv(CORE61 / "core61_route_summary.csv")
    target_summary = read_csv(CORE60B / "core60b_target_summary.csv")

    field_rows = []
    for semantic, spec in SEMANTIC_TYPES.items():
        related_pairs = material[material["semantic_pair"].astype(str).str.contains(semantic, regex=False)] if not material.empty else pd.DataFrame()
        min_activity = float(pd.to_numeric(related_pairs.get("activity_ok_rate"), errors="coerce").min()) if not related_pairs.empty else None
        max_activity = float(pd.to_numeric(related_pairs.get("activity_ok_rate"), errors="coerce").max()) if not related_pairs.empty else None
        if min_activity == 0 and max_activity and max_activity >= 0.6:
            search_permission = "mixed_pair_level_required"
        elif min_activity == 0:
            search_permission = "blocked_until_materialized"
        else:
            search_permission = "repair_or_diagnostic_only"
        field_rows.append(
            {
                "semantic_type": semantic,
                "default_role": spec["role"],
                "data_behavior": spec["behavior"],
                "min_observed_activity_ok_rate": min_activity,
                "max_observed_activity_ok_rate": max_activity,
                "search_permission": search_permission,
            }
        )
    field_map = pd.DataFrame(field_rows)
    field_map.to_csv(RUNTIME / "a7ssm_field_family_route_map.csv", index=False)

    pair_rows = []
    selected_l7 = selected_pressure.set_index("semantic_pair") if not selected_pressure.empty and "semantic_pair" in selected_pressure.columns else pd.DataFrame()
    non_l7_by_pair = (
        route_summary.groupby("core61_route", dropna=False).sum(numeric_only=True).reset_index()
        if not route_summary.empty
        else pd.DataFrame()
    )
    # Use route preview for exact non-L7 rows by pair.
    preview = read_csv(CORE61 / "core61_repair_candidate_queue_preview.csv")
    exact_non_l7 = preview[preview.get("core61_reason", pd.Series(dtype=str)).eq("exact_non_l7_clue")] if not preview.empty else pd.DataFrame()
    exact_by_pair = exact_non_l7.groupby("semantic_pair").size().to_dict() if not exact_non_l7.empty else {}

    for row in material.to_dict("records"):
        pair = str(row["semantic_pair"])
        activity = float(row.get("activity_ok_rate", 0) or 0)
        non_l7_rows = int(exact_by_pair.get(pair, 0))
        l7_share = float(selected_l7.loc[pair, "l7_share"]) if not selected_l7.empty and pair in selected_l7.index else 0.0
        route, permission, search_ready = route_for_pair(pair, activity, non_l7_rows, l7_share)
        pair_rows.append(
            {
                "semantic_pair": pair,
                "semantic_parts": ";".join(semantic_parts(pair)),
                "activity_ok_rate": activity,
                "non_l7_exact_rows": non_l7_rows,
                "selected_l7_share": l7_share,
                "route": route,
                "search_permission": permission,
                "search_ready": search_ready,
                "next_allowed": {
                    "materialization_repair": "CORE62C",
                    "target_near_miss_repair": "CORE62B",
                    "selector_l7_bias_diagnostic": "CORE62B",
                    "diagnostic_memory": "CORE62B",
                }[route],
            }
        )
    pair_map = pd.DataFrame(pair_rows).sort_values(["search_permission", "semantic_pair"])
    pair_map.to_csv(RUNTIME / "a7ssm_interaction_permission_matrix.csv", index=False)

    label = target_summary.copy()
    if not label.empty:
        label["label_permission"] = label.apply(
            lambda r: "diagnostic_only"
            if r["label_family"] == "L7_ranked_future_return"
            else ("repair_target" if int(r.get("non_l7_rows", 0)) > 0 else "near_miss_or_blocked"),
            axis=1,
        )
        label["selector_role"] = label["label_family"].map(
            lambda x: "hard_capped_diagnostic" if x == "L7_ranked_future_return" else "non_l7_primary"
        )
    label.to_csv(RUNTIME / "a7ssm_label_permission_matrix.csv", index=False)

    selector_eligibility = preview.copy()
    if not selector_eligibility.empty:
        pair_perm = pair_map.set_index("semantic_pair")["search_permission"].to_dict()
        selector_eligibility["search_permission"] = selector_eligibility["semantic_pair"].map(pair_perm)
        selector_eligibility["selector_eligible"] = (
            selector_eligibility["search_permission"].ne("blocked_until_materialized")
            & selector_eligibility["label_family"].ne("L7_ranked_future_return")
            & (pd.to_numeric(selector_eligibility["control_ratio"], errors="coerce") < 1.0)
            & (pd.to_numeric(selector_eligibility["cost10"], errors="coerce") > 0)
        )
    selector_eligibility.to_csv(RUNTIME / "a7ssm_selector_eligibility_map.csv", index=False)

    search_ready_pairs = int(pair_map["search_ready"].sum()) if not pair_map.empty else 0
    repair_pairs = int(pair_map["search_permission"].isin(["repair_only", "blocked_until_materialized"]).sum()) if not pair_map.empty else 0
    selector_eligible_rows = int(selector_eligibility.get("selector_eligible", pd.Series(dtype=bool)).sum()) if not selector_eligibility.empty else 0

    auth = {
        "stage": "A7SSM",
        "generated_at": now_utc(),
        "decision": "PASS_A7SSM_SEARCH_SPACE_MEMORY_MAP_BUILT",
        "source_core60b_decision": core60b.get("decision"),
        "source_core60c_decision": core60c.get("decision"),
        "source_core60d_decision": core60d.get("decision"),
        "source_core61_decision": core61.get("decision"),
        "search_ready_pairs": search_ready_pairs,
        "repair_or_blocked_pairs": repair_pairs,
        "selector_eligible_rows": selector_eligible_rows,
        "authorizes_core62b": bool(core61.get("authorizes_core62b_target_near_miss_dryrun")),
        "authorizes_core62c": bool(core61.get("authorizes_core62c_materialization_repair_dryrun")),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ssm_search_authorization_matrix.json", auth)
    write_json(RUNTIME / "a7ssm_manifest.json", auth)

    REPORT.write_text("\n".join([
        "# CRYPTO A7SSM SEARCH SPACE MEMORY MAP",
        "",
        f"Generated: {auth['generated_at']}",
        "",
        "## Decision",
        "",
        "`PASS_A7SSM_SEARCH_SPACE_MEMORY_MAP_BUILT`",
        "",
        "A7SSM is a memory-like mapping layer from semantic fields to routes, permissions, selector eligibility, and next dryrun stages. It does not search, replay, or promote candidates.",
        "",
        "## Authorization Matrix",
        "",
        "```json",
        json.dumps(auth, indent=2, sort_keys=True),
        "```",
        "",
        "## Field Family Route Map",
        "",
        md_table(field_map),
        "",
        "## Interaction Permission Matrix",
        "",
        md_table(pair_map),
        "",
        "## Label Permission Matrix",
        "",
        md_table(label, 30),
        "",
        "## Selector Eligibility Map",
        "",
        md_table(selector_eligibility, 40),
        "",
    ]), encoding="utf-8")
    print(json.dumps(auth, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
