from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
A7LS11 = REPO / "runtime" / "a7ls11_promotion_and_missing_field_repair"
RUNTIME = REPO / "runtime" / "a7ls12_deep_audit_packet"
REPORT = REPO / "reports" / "CRYPTO_A7LS12_DEEP_AUDIT_PACKET_20260606.md"

FIELD_ALIAS = {
    "quote_volume": "trade_quote_volume",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def replace_field_token(expr: str, old: str, new: str) -> str:
    return re.sub(rf"\b{re.escape(old)}\b", new, str(expr))


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "<none>"
    return df.head(max_rows).to_markdown(index=False)


def build() -> dict:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    manifest11 = json.loads((A7LS11 / "a7ls11_manifest.json").read_text(encoding="utf-8"))
    queue = pd.read_csv(A7LS11 / "a7ls11_immediate_deep_audit_queue.csv")
    if queue.empty:
        raise RuntimeError("A7LS11 immediate deep audit queue is empty")

    queue = queue.copy()
    queue["a7ls12_rank"] = range(1, len(queue) + 1)
    queue["a7ls12_alias_applied"] = False
    queue["a7ls12_original_expression"] = queue["expression"].astype(str)
    for old, new in FIELD_ALIAS.items():
        mask = queue["expression"].astype(str).str.contains(rf"\b{re.escape(old)}\b", regex=True, na=False)
        if mask.any():
            queue.loc[mask, "expression"] = queue.loc[mask, "expression"].map(lambda x: replace_field_token(x, old, new))
            queue.loc[mask, "a7ls12_alias_applied"] = True

    shard_count = 4
    rows_per_shard = int(math.ceil(len(queue) / shard_count))
    queue["a7ls12_deep_shard"] = [
        f"a7ls12_s{min(i // rows_per_shard, shard_count - 1):03d}" for i in range(len(queue))
    ]
    queue["a7input_queue"] = queue["a7ls12_deep_shard"]
    queue["a7ls12_execution_mode"] = "full_timestamp_deep_audit"
    queue["a7ls12_hours_per_split"] = 0
    queue["a7ls12_source_stage"] = "A7LS-11"

    shard_plan = (
        queue.groupby("a7ls12_deep_shard", dropna=False)
        .agg(
            queue_rows=("blueprint_id", "count"),
            unique_source_axis=("source_info_axis", "nunique"),
            unique_label_family=("label_family", "nunique"),
            unique_semantic_pair=("semantic_pair", "nunique"),
            unique_skeleton=("skeleton_key", "nunique"),
        )
        .reset_index()
    )
    shard_plan["rows_per_shard_target"] = rows_per_shard
    shard_plan["hours_per_split"] = 0

    family_summary = (
        queue.groupby(["source_info_axis", "next_wave_family", "label_family"], dropna=False)
        .size()
        .reset_index(name="deep_audit_rows")
        .sort_values("deep_audit_rows", ascending=False)
    )
    label_summary = queue.groupby("label_family").size().reset_index(name="deep_audit_rows")
    axis_summary = queue.groupby("source_info_axis").size().reset_index(name="deep_audit_rows")
    alias_audit = pd.DataFrame(
        [
            {
                "old_field": old,
                "replacement_field": new,
                "queue_rows_rewritten": int(
                    queue["a7ls12_original_expression"].astype(str).str.contains(rf"\b{re.escape(old)}\b", regex=True, na=False).sum()
                ),
                "status": "ACTIVE_ALIAS_REWRITE" if old == "quote_volume" else "REGISTERED",
            }
            for old, new in FIELD_ALIAS.items()
        ]
    )

    auth = {
        "stage": "A7LS-12",
        "input_stage": "A7LS-11",
        "authorizes_company_deep_audit_execution": True,
        "authorizes_new_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "uses_may": False,
        "selector_uses_may": False,
        "execution_hours_per_split": 0,
        "execution_note": "HOURS_PER_SPLIT=0 means all available timestamps per split in crypto_a7ff8_expanded_numeric_probe.py.",
    }

    outputs = {
        "a7ls12_deep_audit_queue.csv": queue,
        "a7ls12_deep_audit_shard_plan.csv": shard_plan,
        "a7ls12_family_summary.csv": family_summary,
        "a7ls12_label_summary.csv": label_summary,
        "a7ls12_source_axis_summary.csv": axis_summary,
        "a7ls12_field_alias_audit.csv": alias_audit,
    }
    for name, df in outputs.items():
        df.to_csv(RUNTIME / name, index=False)
    (RUNTIME / "a7ls12_authorization_matrix.json").write_text(json.dumps(auth, indent=2, sort_keys=True), encoding="utf-8")

    manifest = {
        "stage": "A7LS-12",
        "decision": "PASS_A7LS12_DEEP_AUDIT_PACKET_READY_FOR_COMPANY_EXECUTION_NO_SEARCH_AUTH",
        "generated_at": now_iso(),
        "input_decision": manifest11.get("decision"),
        "input_immediate_deep_audit_rows": int(manifest11.get("immediate_deep_audit_rows", len(queue))),
        "deep_audit_queue_rows": int(len(queue)),
        "deep_audit_shard_count": int(shard_count),
        "rows_per_shard_target": int(rows_per_shard),
        "hours_per_split": 0,
        "alias_rewrite_rows": int(queue["a7ls12_alias_applied"].sum()),
        "source_info_axis_count": int(queue["source_info_axis"].nunique()),
        "label_family_count": int(queue["label_family"].nunique()),
        "next_wave_family_count": int(queue["next_wave_family"].nunique()),
        "uses_may": False,
        "executes_numeric_probe": False,
        "executes_search": False,
        "authorizes_company_deep_audit_execution": True,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": [],
    }
    (RUNTIME / "a7ls12_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    report = [
        "# CRYPTO A7LS-12 DEEP AUDIT PACKET",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## Summary",
        "",
        f"- deep_audit_queue_rows: {manifest['deep_audit_queue_rows']}",
        f"- deep_audit_shard_count: {manifest['deep_audit_shard_count']}",
        f"- rows_per_shard_target: {manifest['rows_per_shard_target']}",
        f"- hours_per_split: {manifest['hours_per_split']} (full available timestamps per split)",
        f"- alias_rewrite_rows: {manifest['alias_rewrite_rows']}",
        f"- source_info_axis_count: {manifest['source_info_axis_count']}",
        f"- label_family_count: {manifest['label_family_count']}",
        f"- next_wave_family_count: {manifest['next_wave_family_count']}",
        "",
        "A7LS-12 packages A7LS-11 promoted non-L7 clues for company-machine deep audit. It does not generate new formulas and does not authorize search or alpha proof.",
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan),
        "",
        "## Source Axis Summary",
        "",
        md_table(axis_summary),
        "",
        "## Label Summary",
        "",
        md_table(label_summary),
        "",
        "## Field Alias Audit",
        "",
        md_table(alias_audit),
        "",
        "## Authorization",
        "",
        "- company deep audit execution: authorized",
        "- new generation / formula search / large search: not authorized",
        "- alpha proof / shadow / paper / live: not authorized",
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, sort_keys=True))
