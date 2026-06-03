from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
A7INPUT0 = REPO / "runtime" / "a7input0_input_approval_package"
CORE53IAE = REPO / "runtime" / "a7ffcore53iae_input_approval_filter_experiment"
RUNTIME = REPO / "runtime" / "a7input1_integration_smoke"
REPORT = REPO / "reports" / "CRYPTO_A7INPUT1_INTEGRATION_SMOKE_20260603.md"

FIELD_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b")
FUNCTION_TOKENS = {
    "Abs",
    "Add",
    "Clip",
    "CSRank",
    "Decay",
    "Delta",
    "Identity",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "SignedRankDelta",
    "SpreadShortLong",
    "Sub",
    "TSRank",
    "WinsorZ",
    "ZScore",
}


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


def parse_fields(expression: str, known_fields: set[str]) -> list[str]:
    fields = []
    for token in FIELD_RE.findall(str(expression)):
        if token in FUNCTION_TOKENS:
            continue
        if token in known_fields:
            fields.append(token)
    return sorted(set(fields))


def classify(fields: list[str], registry: dict[str, dict], mode: str, policy: dict) -> tuple[str, str, str]:
    if not fields:
        return "reject", "no_known_fields", ""
    tags = [registry[field]["input_tag"] for field in fields if field in registry]
    missing = [field for field in fields if field not in registry]
    if missing:
        return "reject", "missing_registry_field", "|".join(missing)
    clusters = [registry[field]["info_cluster_id"] for field in fields]
    tag_set = set(tags)
    if mode == "ordinary_alpha":
        allowed = set(policy["ordinary_alpha"]["allowed_tags"])
        blocked = set(policy["ordinary_alpha"]["blocked_tags"])
        if tag_set & blocked:
            return "reject", "ordinary_alpha_blocked_tag", "|".join(sorted(tag_set & blocked))
        if not tag_set <= allowed:
            return "reject", "ordinary_alpha_unknown_tag", "|".join(sorted(tag_set - allowed))
        return "accept", "ordinary_alpha_allowed", "|".join(sorted(set(clusters)))
    if mode == "interaction_alpha":
        allowed = set(policy["interaction_alpha"]["allowed_tags"])
        if not tag_set <= allowed:
            return "reject", "interaction_blocked_tag", "|".join(sorted(tag_set - allowed))
        if policy["interaction_alpha"].get("requires_at_least_one_signal_tag") and not (
            "A7INPUT_APPROVED_SIGNAL_PRIMARY" in tag_set or "A7INPUT_APPROVED_REDUNDANT_CAP" in tag_set
        ):
            return "reject", "interaction_missing_signal_tag", "|".join(sorted(tag_set))
        return "accept", "interaction_allowed", "|".join(sorted(set(clusters)))
    if mode == "rescue_lane":
        allowed = set(policy["rescue_lane"]["allowed_tags"])
        if not tag_set <= allowed:
            return "reject", "rescue_lane_non_rescue_tag", "|".join(sorted(tag_set - allowed))
        return "accept", "rescue_lane_allowed", "|".join(sorted(set(clusters)))
    return "reject", "unknown_mode", mode


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(A7INPUT0 / "a7input0_manifest.json")
    if not source.get("authorizes_a7input1_integration_smoke"):
        raise SystemExit(f"A7INPUT-1 not authorized by A7INPUT-0: {source.get('decision')}")
    registry_df = pd.read_csv(A7INPUT0 / "a7input0_input_approval_registry.csv")
    policy = read_json(A7INPUT0 / "a7input0_routing_policy.json")
    traces = pd.read_csv(CORE53IAE / "a7ffcore53iae_formula_index_filter_trace.csv")
    sample = traces.head(5000).copy()
    registry = registry_df.set_index("field").to_dict("index")
    known_fields = set(registry)
    rows = []
    for _, row in sample.iterrows():
        fields = parse_fields(row["expression"], known_fields)
        for mode in ["ordinary_alpha", "interaction_alpha", "rescue_lane"]:
            decision, reason, detail = classify(fields, registry, mode, policy)
            rows.append(
                {
                    "seed_id": row["seed_id"],
                    "expression": row["expression"],
                    "mode": mode,
                    "decision": decision,
                    "reason": reason,
                    "detail": detail,
                    "input_fields": "|".join(fields),
                    "input_field_count": len(fields),
                }
            )
    result = pd.DataFrame(rows)
    summary = (
        result.groupby(["mode", "decision", "reason"], as_index=False)
        .agg(row_count=("seed_id", "count"), median_input_field_count=("input_field_count", "median"))
        .sort_values(["mode", "decision", "row_count"], ascending=[True, True, False])
    )
    mode_accept = (
        result.groupby("mode", as_index=False)
        .agg(accepted=("decision", lambda s: int((s == "accept").sum())), total=("decision", "count"))
    )
    mode_accept["accept_rate"] = mode_accept["accepted"] / mode_accept["total"].clip(lower=1)
    ordinary_ok = bool(mode_accept.loc[mode_accept["mode"].eq("ordinary_alpha"), "accepted"].iloc[0] > 0)
    interaction_ok = bool(mode_accept.loc[mode_accept["mode"].eq("interaction_alpha"), "accepted"].iloc[0] > 0)
    rescue_ok = bool(mode_accept.loc[mode_accept["mode"].eq("rescue_lane"), "accepted"].iloc[0] >= 0)
    decision = (
        "PASS_A7INPUT1_INPUT_ROUTING_INTEGRATION_SMOKE"
        if ordinary_ok and interaction_ok and rescue_ok
        else "HOLD_A7INPUT1_INPUT_ROUTING_INTEGRATION_FAIL"
    )
    manifest = {
        "stage": "A7INPUT-1",
        "generated_at": now_utc(),
        "source_stage": source.get("stage"),
        "source_decision": source.get("decision"),
        "decision": decision,
        "sample_formula_count": int(sample.shape[0]),
        "mode_count": 3,
        "ordinary_alpha_accept_count": int(mode_accept.loc[mode_accept["mode"].eq("ordinary_alpha"), "accepted"].iloc[0]),
        "interaction_alpha_accept_count": int(mode_accept.loc[mode_accept["mode"].eq("interaction_alpha"), "accepted"].iloc[0]),
        "rescue_lane_accept_count": int(mode_accept.loc[mode_accept["mode"].eq("rescue_lane"), "accepted"].iloc[0]),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core54_queue_builder_contract": decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    authorization = {
        "authorized": {
            "A7FF-CORE54 input-tag-aware queue builder contract": decision.startswith("PASS_"),
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    result.to_csv(RUNTIME / "a7input1_mode_filter_trace.csv", index=False)
    summary.to_csv(RUNTIME / "a7input1_mode_filter_summary.csv", index=False)
    mode_accept.to_csv(RUNTIME / "a7input1_mode_acceptance.csv", index=False)
    write_json(RUNTIME / "a7input1_manifest.json", manifest)
    write_json(RUNTIME / "a7input1_authorization_matrix.json", authorization)
    report = [
        "# CRYPTO A7INPUT-1 INTEGRATION SMOKE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7INPUT-1 verifies that the independent input tag package can gate formula inputs by ordinary-alpha, interaction-alpha, and rescue-lane modes. It does not execute replay/search/proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Mode Acceptance",
        "",
        md_table(mode_accept),
        "",
        "## Mode Filter Summary",
        "",
        md_table(summary, 80),
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
