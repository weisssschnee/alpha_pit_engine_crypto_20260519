from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore30_independent_family_numeric_probe_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE30_INDEPENDENT_FAMILY_NUMERIC_PROBE_CONTRACT_20260602.md"
CORE29E = REPO / "runtime" / "a7ffcore29e_independent_family_preflight" / "a7ffcore29e_manifest.json"
CORE29E_QUEUE = REPO / "runtime" / "a7ffcore29e_independent_family_preflight" / "a7ffcore29e_blueprint_preflight_queue.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
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


def build_numeric_queue(preflight: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for family_id, group in preflight[preflight["materialization_preflight_pass"]].groupby("family_id", sort=True):
        # Round-robin by motif/operator so the 80-row probe is not only first-N.
        g = group.sort_values(["motif", "operator", "window_h", "candidate_id"]).copy()
        picked = (
            g.groupby(["motif", "operator"], group_keys=False)
            .head(4)
            .sort_values(["candidate_id"])
            .head(80)
            .copy()
        )
        if picked.shape[0] < 80:
            remainder = g.loc[~g["candidate_id"].isin(picked["candidate_id"])].head(80 - picked.shape[0])
            picked = pd.concat([picked, remainder], ignore_index=True)
        rows.append(picked)
    queue = pd.concat(rows, ignore_index=True)
    queue = queue.sort_values(["family_id", "motif", "operator", "candidate_id"]).reset_index(drop=True)
    queue["numeric_probe_id"] = [f"a7ffcore30_{i:04d}" for i in range(len(queue))]
    queue["executes_numeric_in_core30"] = False
    queue["authorized_for_core30e_numeric_probe"] = True
    return queue


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE29E)
    if source.get("decision") != "PASS_A7FFCORE29E_INDEPENDENT_FAMILY_PREFLIGHT_READY_FOR_CORE30_CONTRACT":
        raise SystemExit(f"CORE29E not ready for CORE30: {source.get('decision')}")
    preflight = pd.read_csv(CORE29E_QUEUE)
    queue = build_numeric_queue(preflight)
    family_summary = (
        queue.groupby("family_id", as_index=False)
        .agg(
            numeric_queue_count=("numeric_probe_id", "count"),
            motif_count=("motif", "nunique"),
            operator_count=("operator", "nunique"),
            window_count=("window_h", "nunique"),
        )
        .sort_values("family_id")
    )
    label_plan = pd.DataFrame(
        [
            {"label": "L0_raw_forward_return", "horizons_h": "4,8,24", "role": "primary_non_ranked"},
            {"label": "L1_cross_sectional_relative_return", "horizons_h": "4,8,24", "role": "primary_non_ranked"},
            {"label": "L3_liquidity_tier_relative_return", "horizons_h": "8,24", "role": "state_relative"},
            {"label": "L5_vol_adjusted_return", "horizons_h": "8,24", "role": "risk_adjusted"},
            {"label": "L7_ranked_future_return", "horizons_h": "8,24", "role": "diagnostic_only_not_sufficient"},
        ]
    )
    control_plan = pd.DataFrame(
        [
            {"control": "row_shuffle", "required": True},
            {"control": "time_shuffle", "required": True},
            {"control": "wrong_lag_future", "required": True},
            {"control": "wrong_lag_stale", "required": True},
            {"control": "sign_flip", "required": True},
            {"control": "same_family_placebo", "required": True},
        ]
    )
    gate_plan = pd.DataFrame(
        [
            {"gate": "family_balance", "threshold": "80 numeric rows per family"},
            {"gate": "preflight_pass", "threshold": "all 240 selected rows passed CORE29E field preflight"},
            {"gate": "non_l7_evidence", "threshold": "at least one non-L7 primary label family must be positive before any replay contract"},
            {"gate": "control_ratio", "threshold": "median control_ratio < 1.0; preferred < 0.8"},
            {"gate": "split_consistency", "threshold": "train/validation/test not all sign-inconsistent"},
            {"gate": "single_family_cap", "threshold": "no family can alone authorize replay/search"},
            {"gate": "large_search", "threshold": "false"},
        ]
    )
    authorization = {
        "authorized": {"A7FF-CORE30E bounded numeric probe execution": True},
        "not_authorized": {
            "replay_contract": True,
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    family_ok = bool((family_summary["numeric_queue_count"] == 80).all())
    selected_ok = int(queue.shape[0]) == 240 and bool(queue["materialization_preflight_pass"].all())
    decision = (
        "PASS_A7FFCORE30_NUMERIC_PROBE_CONTRACT_READY_FOR_CORE30E"
        if family_ok and selected_ok
        else "HOLD_A7FFCORE30_NUMERIC_QUEUE_CONTRACT_INVALID"
    )
    manifest = {
        "stage": "A7FF-CORE30",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE29E",
        "source_decision": source.get("decision"),
        "decision": decision,
        "numeric_queue_count": int(queue.shape[0]),
        "family_count": int(queue["family_id"].nunique()),
        "per_family_queue_target": 80,
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core30e_numeric_probe": decision.startswith("PASS_"),
        "authorizes_replay_contract": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE30E bounded numeric probe execution" if decision.startswith("PASS_") else "CORE30 queue repair",
    }
    queue.to_csv(RUNTIME / "a7ffcore30_numeric_probe_queue.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore30_family_summary.csv", index=False)
    label_plan.to_csv(RUNTIME / "a7ffcore30_label_plan.csv", index=False)
    control_plan.to_csv(RUNTIME / "a7ffcore30_control_plan.csv", index=False)
    gate_plan.to_csv(RUNTIME / "a7ffcore30_gate_plan.csv", index=False)
    write_json(RUNTIME / "a7ffcore30_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore30_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-CORE30 INDEPENDENT FAMILY NUMERIC PROBE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE30 is a numeric-probe contract. It prepares a balanced 240-row numeric queue but does not execute numeric evaluation, replay, search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Family Summary",
        "",
        md_table(family_summary),
        "",
        "## Label Plan",
        "",
        md_table(label_plan),
        "",
        "## Control Plan",
        "",
        md_table(control_plan),
        "",
        "## Gate Plan",
        "",
        md_table(gate_plan),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
