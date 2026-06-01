from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16i_balanced_preseed_queue_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16I_BALANCED_PRESEED_QUEUE_AUDIT_20260601.md"
CORE16HER = REPO / "runtime" / "a7ffcore16her_second_pass_forensic" / "a7ffcore16her_manifest.json"
QUEUE_PREVIEW = REPO / "runtime" / "a7ffcore16her_second_pass_forensic" / "a7ffcore16her_balanced_preseed_queue_preview.csv"


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
    core16her = read_json(CORE16HER)
    if core16her.get("decision") != "PASS_A7FFCORE16HER_SECOND_PASS_FORENSIC_READY_FOR_CORE16I":
        raise SystemExit(f"CORE16HER is not ready for CORE16I: {core16her.get('decision')}")
    queue = pd.read_csv(QUEUE_PREVIEW)
    queue["queue_role"] = queue["queue_role"].fillna("strict_candidate")
    queue["control_ratio_premay_max"] = pd.to_numeric(queue["control_ratio_premay_max"], errors="coerce")
    summary = (
        queue.groupby(["second_pass_family", "queue_role"], dropna=False)
        .agg(
            rows=("queue_rank", "size"),
            label_family_count=("label_family", "nunique"),
            operator_count=("operator", "nunique"),
            lag_ok_count=("lag_ok", lambda s: int(s.astype(str).str.lower().eq("true").sum())),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    queue_size = int(queue.shape[0])
    family_count = int(queue["second_pass_family"].nunique())
    top_share = float(queue["second_pass_family"].value_counts(normalize=True).max())
    h2_count = int(queue[queue["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].shape[0])
    near_count = int(queue["queue_role"].astype(str).eq("forensic_near_miss_not_alpha_seed").sum())
    strict_count = queue_size - near_count
    non_l5_share = float(queue["label_family"].astype(str).ne("L5_vol_adjusted_return").mean())
    operator_count = int(queue["operator"].nunique())
    structure_ok = (
        queue_size >= 96
        and family_count >= 4
        and top_share <= 0.45
        and h2_count >= 12
        and non_l5_share >= 0.40
        and operator_count >= 2
    )
    blockers: list[str] = []
    if not structure_ok:
        blockers.append("balanced_queue_structure_fail")
    if near_count > 0:
        blockers.append("near_miss_rows_present_not_promotable")
    decision = (
        "PASS_A7FFCORE16I_BALANCED_PRESEED_QUEUE_READY_FOR_NEARMISS_RESOLUTION"
        if structure_ok
        else "HOLD_A7FFCORE16I_BALANCED_PRESEED_QUEUE_INVALID"
    )
    next_allowed = (
        "A7FF-CORE16J near-miss upgrade/exclusion audit"
        if structure_ok
        else "A7FF-CORE16HR queue repair"
    )
    manifest = {
        "stage": "A7FF-CORE16I",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16HER",
        "source_decision": core16her.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "queue_size": queue_size,
        "strict_count": strict_count,
        "near_miss_count": near_count,
        "family_count": family_count,
        "top_family_share": top_share,
        "h2_count": h2_count,
        "non_l5_share": non_l5_share,
        "operator_count": operator_count,
        "authorizes_core16j": structure_ok,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": next_allowed,
    }
    queue.to_csv(RUNTIME / "a7ffcore16i_balanced_preseed_queue.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore16i_queue_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore16i_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16I BALANCED PRE-SEED QUEUE AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16I audits the balanced pre-seed queue created from CORE16HE. It does not promote near-miss rows, execute replay, formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Queue Summary",
        "",
        md_table(summary),
        "",
        "## Queue Sample",
        "",
        md_table(queue.head(80)),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
