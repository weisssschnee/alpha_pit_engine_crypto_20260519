from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16l_strict_preseed_queue_lock"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16L_STRICT_PRESEED_QUEUE_LOCK_20260601.md"
CORE16ME = REPO / "runtime" / "a7ffcore16me_broader_h2_repair_execution" / "a7ffcore16me_manifest.json"
QUEUE = REPO / "runtime" / "a7ffcore16me_broader_h2_repair_execution" / "a7ffcore16me_repaired_strict_preseed_queue.csv"


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    me = read_json(CORE16ME)
    if me.get("decision") != "PASS_A7FFCORE16ME_H2_FLOOR_REPAIRED_READY_FOR_CORE16L":
        raise SystemExit(f"CORE16ME is not ready for CORE16L: {me.get('decision')}")
    queue = pd.read_csv(QUEUE)
    queue = queue.copy()
    if "queue_rank" in queue.columns:
        queue = queue.drop(columns=["queue_rank"])
    queue.insert(0, "queue_rank", range(1, len(queue) + 1))
    queue["locked_stage"] = "A7FF-CORE16L"
    queue["locked_for"] = "CORE17_CONTRACT_ONLY"

    summary = (
        queue.groupby(["second_pass_family", "queue_role"], dropna=False)
        .agg(
            rows=("blueprint_id", "size"),
            label_family_count=("label_family", "nunique"),
            horizon_count=("label_horizon_h", "nunique"),
            operator_count=("operator", "nunique"),
            lag_ok_count=("lag_ok", lambda s: int(s.astype(str).str.lower().eq("true").sum())),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    duplicate_keys = int(queue.duplicated(subset=["blueprint_id", "label_family", "label_horizon_h"]).sum())
    near_miss_count = int(queue["queue_role"].astype(str).str.contains("near", case=False, na=False).sum()) if "queue_role" in queue.columns else 0
    strict_count = int(queue["queue_role"].astype(str).eq("strict_candidate").sum()) if "queue_role" in queue.columns else int(len(queue))
    family_count = int(queue["second_pass_family"].nunique())
    top_share = float(queue["second_pass_family"].value_counts(normalize=True).max()) if not queue.empty else 0.0
    h2_count = int(queue[queue["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].shape[0])
    h3_count = int(queue[queue["second_pass_family"].astype(str).eq("H3_cross_family_bridge")].shape[0])
    non_l5_share = float(queue["label_family"].astype(str).ne("L5_vol_adjusted_return").mean()) if not queue.empty else 0.0
    operator_count = int(queue["operator"].nunique()) if "operator" in queue.columns else 0
    blockers: list[str] = []
    if len(queue) < 96:
        blockers.append("queue_size_lt_96")
    if strict_count != len(queue):
        blockers.append("non_strict_rows_present")
    if near_miss_count:
        blockers.append("near_miss_rows_present")
    if duplicate_keys:
        blockers.append("duplicate_candidate_label_horizon_keys")
    if family_count < 4:
        blockers.append("family_count_lt_4")
    if top_share > 0.45:
        blockers.append("top_family_share_gt_45pct")
    if h2_count < 12:
        blockers.append("h2_floor_lt_12")
    if h3_count < 12:
        blockers.append("h3_floor_lt_12")
    if non_l5_share < 0.40:
        blockers.append("non_l5_share_lt_40pct")
    if operator_count < 2:
        blockers.append("operator_count_lt_2")

    passed = not blockers
    decision = "PASS_A7FFCORE16L_STRICT_PRESEED_QUEUE_LOCKED_READY_FOR_CORE17_CONTRACT" if passed else "HOLD_A7FFCORE16L_STRICT_PRESEED_QUEUE_LOCK_FAIL"
    queue.to_csv(RUNTIME / "a7ffcore16l_locked_strict_preseed_queue.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore16l_queue_family_summary.csv", index=False)
    gate = pd.DataFrame(
        [
            {"gate": "queue_size", "value": len(queue), "threshold": ">=96", "pass": len(queue) >= 96},
            {"gate": "strict_count", "value": strict_count, "threshold": "==queue_size", "pass": strict_count == len(queue)},
            {"gate": "near_miss_count", "value": near_miss_count, "threshold": "0", "pass": near_miss_count == 0},
            {"gate": "family_count", "value": family_count, "threshold": ">=4", "pass": family_count >= 4},
            {"gate": "top_family_share", "value": top_share, "threshold": "<=0.45", "pass": top_share <= 0.45},
            {"gate": "h2_count", "value": h2_count, "threshold": ">=12", "pass": h2_count >= 12},
            {"gate": "h3_count", "value": h3_count, "threshold": ">=12", "pass": h3_count >= 12},
            {"gate": "non_l5_share", "value": non_l5_share, "threshold": ">=0.40", "pass": non_l5_share >= 0.40},
            {"gate": "operator_count", "value": operator_count, "threshold": ">=2", "pass": operator_count >= 2},
            {"gate": "duplicate_keys", "value": duplicate_keys, "threshold": "0", "pass": duplicate_keys == 0},
        ]
    )
    gate.to_csv(RUNTIME / "a7ffcore16l_gate_audit.csv", index=False)

    manifest = {
        "stage": "A7FF-CORE16L",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16ME",
        "source_decision": me.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "locked_queue_size": int(len(queue)),
        "strict_count": strict_count,
        "near_miss_count": near_miss_count,
        "family_count": family_count,
        "top_family_share": top_share,
        "h2_count": h2_count,
        "h3_count": h3_count,
        "non_l5_share": non_l5_share,
        "operator_count": operator_count,
        "duplicate_keys": duplicate_keys,
        "authorizes_core17_contract": passed,
        "authorizes_core17_execution": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE17 objective seed policy contract" if passed else "A7FF-CORE16LR strict queue lock forensic",
    }
    write_json(RUNTIME / "a7ffcore16l_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16L STRICT PRESEED QUEUE LOCK",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16L locks the strict pre-seed queue for contract drafting only. It does not execute replay, search, formula generation, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Gate Audit",
        "",
        md_table(gate),
        "",
        "## Family Summary",
        "",
        md_table(summary),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
