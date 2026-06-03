from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE53IA = REPO / "runtime" / "a7ffcore53ia_incremental_input_approval"
CORE53IAE = REPO / "runtime" / "a7ffcore53iae_input_approval_filter_experiment"
RUNTIME = REPO / "runtime" / "a7input0_input_approval_package"
REPORT = REPO / "reports" / "CRYPTO_A7INPUT0_INPUT_APPROVAL_PACKAGE_20260603.md"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
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


def route_for(row: pd.Series) -> tuple[str, str, str]:
    role = str(row["system_input_role"])
    approval = str(row["input_approval"])
    reason = str(row["approval_reason"])
    if role == "signal_primary":
        return "ordinary_alpha_signal", "A7INPUT_APPROVED_SIGNAL_PRIMARY", "direct alpha input allowed"
    if role == "signal_redundant_cap":
        return "capped_alpha_signal", "A7INPUT_APPROVED_REDUNDANT_CAP", "allowed with cluster representative/cap"
    if role == "condition_or_neutralizer":
        return "condition_neutralizer_only", "A7INPUT_CONDITION_NEUTRALIZER_ONLY", "not standalone alpha; allowed as state/gate/neutralizer"
    if role == "blocked":
        if "coverage" in reason and row["unique_count"] > 1000 and row["active_xs_share"] >= 0.5:
            return "rescue_event_or_sparse_signal", "A7INPUT_RESCUE_SPARSE_EVENT", "blocked for ordinary alpha but allowed in rescue lane"
        if "cross_sectional" in reason:
            return "rescue_timeseries_or_market_state", "A7INPUT_RESCUE_TS_STATE", "blocked for cross-section alpha but allowed as market/time-series state"
        return "hard_blocked", "A7INPUT_HARD_BLOCKED", "blocked from alpha input"
    return "unknown_review", "A7INPUT_REVIEW_REQUIRED", "manual review required"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE53IA / "a7ffcore53ia_manifest.json")
    experiment = read_json(CORE53IAE / "a7ffcore53iae_manifest.json")
    if source.get("decision") != "PASS_A7FFCORE53IA_INCREMENTAL_INPUT_APPROVAL_BUILT":
        raise SystemExit(f"CORE53IA not ready: {source.get('decision')}")
    if experiment.get("decision") != "PASS_A7FFCORE53IAE_INPUT_APPROVAL_FILTER_EXPERIMENT_BUILT":
        raise SystemExit(f"CORE53IAE not ready: {experiment.get('decision')}")
    registry = pd.read_csv(CORE53IAE / "a7ffcore53iae_system_input_registry.csv")
    route_rows = []
    for _, row in registry.iterrows():
        route, tag, route_reason = route_for(row)
        route_rows.append(
            {
                "field": row["field"],
                "semantic_type": row["semantic_type"],
                "info_cluster_id": row["info_cluster_id"],
                "cluster_size": row["cluster_size"],
                "system_input_role": row["system_input_role"],
                "input_route": route,
                "input_tag": tag,
                "route_reason": route_reason,
                "source_input_approval": row["input_approval"],
                "source_approval_reason": row["approval_reason"],
                "coverage": row["coverage"],
                "unique_count": row["unique_count"],
                "median_xs_std": row["median_xs_std"],
                "active_xs_share": row["active_xs_share"],
            }
        )
    package = pd.DataFrame(route_rows)
    tag_dictionary = pd.DataFrame(
        [
            {
                "input_tag": "A7INPUT_APPROVED_SIGNAL_PRIMARY",
                "meaning": "field has enough standalone incremental information for ordinary alpha input",
                "allowed_in": "generator,evaluator,selector,replay",
                "requires_cap": False,
                "rescue_lane": False,
            },
            {
                "input_tag": "A7INPUT_APPROVED_REDUNDANT_CAP",
                "meaning": "field is informative but belongs to high-correlation cluster; cap by info_cluster_id",
                "allowed_in": "generator,evaluator,selector,replay",
                "requires_cap": True,
                "rescue_lane": False,
            },
            {
                "input_tag": "A7INPUT_CONDITION_NEUTRALIZER_ONLY",
                "meaning": "field is state/taxonomy/neutralizer; not standalone alpha input",
                "allowed_in": "regime,neutralizer,condition,interaction_gate",
                "requires_cap": True,
                "rescue_lane": False,
            },
            {
                "input_tag": "A7INPUT_RESCUE_SPARSE_EVENT",
                "meaning": "low coverage but high uniqueness/activity; can be tested only in sparse/event rescue lane",
                "allowed_in": "rescue_event,diagnostic_interaction",
                "requires_cap": True,
                "rescue_lane": True,
            },
            {
                "input_tag": "A7INPUT_RESCUE_TS_STATE",
                "meaning": "low cross-sectional variation; can be tested only as time-series or market-state variable",
                "allowed_in": "rescue_state,market_regime",
                "requires_cap": True,
                "rescue_lane": True,
            },
            {
                "input_tag": "A7INPUT_HARD_BLOCKED",
                "meaning": "field should not enter alpha generation unless re-audited",
                "allowed_in": "none",
                "requires_cap": True,
                "rescue_lane": False,
            },
            {
                "input_tag": "A7INPUT_REVIEW_REQUIRED",
                "meaning": "field lacks stable routing decision",
                "allowed_in": "manual_review",
                "requires_cap": True,
                "rescue_lane": False,
            },
        ]
    )
    routing_policy = {
        "ordinary_alpha": {
            "allowed_tags": ["A7INPUT_APPROVED_SIGNAL_PRIMARY", "A7INPUT_APPROVED_REDUNDANT_CAP"],
            "blocked_tags": [
                "A7INPUT_CONDITION_NEUTRALIZER_ONLY",
                "A7INPUT_RESCUE_SPARSE_EVENT",
                "A7INPUT_RESCUE_TS_STATE",
                "A7INPUT_HARD_BLOCKED",
                "A7INPUT_REVIEW_REQUIRED",
            ],
            "max_same_info_cluster_share": 0.20,
            "max_redundant_cap_share": 0.35,
        },
        "interaction_alpha": {
            "allowed_tags": [
                "A7INPUT_APPROVED_SIGNAL_PRIMARY",
                "A7INPUT_APPROVED_REDUNDANT_CAP",
                "A7INPUT_CONDITION_NEUTRALIZER_ONLY",
            ],
            "requires_at_least_one_signal_tag": True,
            "condition_only_formula_forbidden": True,
        },
        "rescue_lane": {
            "allowed_tags": ["A7INPUT_RESCUE_SPARSE_EVENT", "A7INPUT_RESCUE_TS_STATE"],
            "must_be_separately_reported": True,
            "cannot_authorize_alpha_search": True,
            "requires_event_or_state_specific_label": True,
        },
        "hard_block": {
            "blocked_tags": ["A7INPUT_HARD_BLOCKED", "A7INPUT_REVIEW_REQUIRED"],
            "fail_closed": True,
        },
    }
    package_summary = (
        package.groupby(["semantic_type", "input_tag", "input_route"], as_index=False)
        .agg(field_count=("field", "count"))
        .sort_values(["semantic_type", "field_count"], ascending=[True, False])
    )
    cluster_policy = (
        package.groupby("info_cluster_id", as_index=False)
        .agg(
            field_count=("field", "count"),
            tags=("input_tag", lambda s: "|".join(sorted(set(s)))),
            semantic_types=("semantic_type", lambda s: "|".join(sorted(set(s)))),
            fields=("field", lambda s: "|".join(sorted(s))),
        )
        .sort_values(["field_count", "info_cluster_id"], ascending=[False, True])
    )
    manifest = {
        "stage": "A7INPUT-0",
        "generated_at": now_utc(),
        "source_stages": ["A7FF-CORE53IA", "A7FF-CORE53IAE"],
        "source_decisions": [source.get("decision"), experiment.get("decision")],
        "decision": "PASS_A7INPUT0_INPUT_APPROVAL_PACKAGE_READY",
        "field_count": int(package.shape[0]),
        "tag_count": int(tag_dictionary.shape[0]),
        "ordinary_alpha_allowed_field_count": int(package["input_tag"].isin(["A7INPUT_APPROVED_SIGNAL_PRIMARY", "A7INPUT_APPROVED_REDUNDANT_CAP"]).sum()),
        "condition_only_field_count": int(package["input_tag"].eq("A7INPUT_CONDITION_NEUTRALIZER_ONLY").sum()),
        "rescue_lane_field_count": int(package["input_tag"].astype(str).str.startswith("A7INPUT_RESCUE").sum()),
        "hard_blocked_field_count": int(package["input_tag"].eq("A7INPUT_HARD_BLOCKED").sum()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_a7input1_integration_smoke": True,
    }
    authorization = {
        "authorized": {
            "A7INPUT-1 generator/evaluator integration smoke": True,
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    package.to_csv(RUNTIME / "a7input0_input_approval_registry.csv", index=False)
    tag_dictionary.to_csv(RUNTIME / "a7input0_input_tag_dictionary.csv", index=False)
    package_summary.to_csv(RUNTIME / "a7input0_package_summary.csv", index=False)
    cluster_policy.to_csv(RUNTIME / "a7input0_info_cluster_policy.csv", index=False)
    write_json(RUNTIME / "a7input0_routing_policy.json", routing_policy)
    write_json(RUNTIME / "a7input0_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7input0_manifest.json", manifest)
    report = [
        "# CRYPTO A7INPUT-0 INPUT APPROVAL PACKAGE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "A7INPUT-0 packages the input approval layer as an independent registry and tag/routing contract. It is not a replay, search, proof, or promotion stage.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Tag Dictionary",
        "",
        md_table(tag_dictionary),
        "",
        "## Package Summary",
        "",
        md_table(package_summary, 80),
        "",
        "## Cluster Policy",
        "",
        md_table(cluster_policy, 80),
        "",
        "## Routing Policy",
        "",
        "```json",
        json.dumps(routing_policy, indent=2, sort_keys=True),
        "```",
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
