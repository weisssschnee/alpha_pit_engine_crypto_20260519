from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "runtime" / "a7ls3h_company_numeric_handoff"
RUNTIME = REPO / "runtime" / "a7ls3hr_company_handoff_resize"
REPORT = REPO / "reports" / "CRYPTO_A7LS3HR_COMPANY_HANDOFF_RESIZE_20260605.md"


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
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```csv\n" + view.to_csv(index=False) + "```"


def resize(queue: pd.DataFrame, rows_per_shard: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = queue.copy().reset_index(drop=True)
    out["company_numeric_shard"] = [f"a7ls3hr_s{i // rows_per_shard:03d}" for i in range(len(out))]
    out["checkpoint_key"] = out["company_numeric_shard"] + "::" + out["blueprint_id"].astype(str)
    shard_plan = out.groupby(["company_numeric_shard"], dropna=False).agg(
        rows=("blueprint_id", "size"),
        arm_count=("a7ls_arm", "nunique"),
        semantic_pair_count=("semantic_pair", "nunique"),
        motif_count=("motif", "nunique"),
        skeleton_count=("skeleton_key", "nunique"),
    ).reset_index()
    return out, shard_plan


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    src_manifest = read_json(SRC / "a7ls3h_manifest.json")
    if not src_manifest.get("authorizes_company_numeric_async"):
        raise SystemExit(f"A7LS-3H not ready: {src_manifest.get('decision')}")
    queue = pd.read_csv(SRC / "a7ls3h_company_numeric_queue.csv")

    primary_rows = int(64)
    fallback_rows = int(32)
    primary_queue, primary_plan = resize(queue, primary_rows)
    fallback_queue, fallback_plan = resize(queue, fallback_rows)
    primary_queue.to_csv(RUNTIME / "a7ls3hr_company_numeric_queue_64.csv", index=False)
    primary_plan.to_csv(RUNTIME / "a7ls3hr_company_shard_plan_64.csv", index=False)
    fallback_queue.to_csv(RUNTIME / "a7ls3hr_company_numeric_queue_32_fallback.csv", index=False)
    fallback_plan.to_csv(RUNTIME / "a7ls3hr_company_shard_plan_32_fallback.csv", index=False)

    arm_summary = primary_queue.groupby(["a7ls_arm"], dropna=False).agg(
        rows=("blueprint_id", "size"),
        semantic_pair_count=("semantic_pair", "nunique"),
        motif_count=("motif", "nunique"),
        skeleton_count=("skeleton_key", "nunique"),
    ).reset_index()
    arm_summary.to_csv(RUNTIME / "a7ls3hr_arm_summary.csv", index=False)

    command_template = {
        "stage": "A7LS-3HR",
        "primary_plan": {
            "rows_per_shard": primary_rows,
            "shard_count": int(primary_plan["company_numeric_shard"].nunique()),
            "recommended_parallelism": 8,
            "max_parallelism_if_memory_headroom_confirmed": 12,
            "queue_file": str(RUNTIME / "a7ls3hr_company_numeric_queue_64.csv").replace("\\", "/"),
            "shard_plan_file": str(RUNTIME / "a7ls3hr_company_shard_plan_64.csv").replace("\\", "/"),
        },
        "fallback_plan": {
            "rows_per_shard": fallback_rows,
            "shard_count": int(fallback_plan["company_numeric_shard"].nunique()),
            "recommended_parallelism": 4,
            "queue_file": str(RUNTIME / "a7ls3hr_company_numeric_queue_32_fallback.csv").replace("\\", "/"),
            "shard_plan_file": str(RUNTIME / "a7ls3hr_company_shard_plan_32_fallback.csv").replace("\\", "/"),
        },
        "per_shard_env_primary": {
            "A7FF8_STAGE": "A7LS-3HR-${SHARD}",
            "A7FF8_FILE_PREFIX": "a7ls3hr_${SHARD}",
            "A7FF8_RUNTIME": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3hr_company_numeric/${SHARD}",
            "A7FF8_REPORT": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3hr_company_numeric/${SHARD}/A7LS3HR_NUMERIC_DETAIL.md",
            "A7FF8_QUEUE_PATH": "G:/AlphaFactory_CryptoData/research_runtime/a7ls3hr_company_numeric/${SHARD}/queue.csv",
            "A7FF8_AUTH_MANIFEST": "G:/Project_V7_Rotation/alpha_pit_engine_crypto_20260519/runtime/a7ls2_sharded_materialization_wave/a7ls2_manifest.json",
            "A7FF8_AUTH_DECISION": "PASS_A7LS2_FIRST_CHECKPOINT_MATERIALIZATION_READY",
            "A7FF8_MATERIALIZE_CAP": str(primary_rows),
            "A7FF8_FAST_NUMERIC_CAP": str(primary_rows),
            "A7FF8_PORTFOLIO_CAP": "96",
            "A7FF8_QUEUE_LIMIT": str(primary_rows),
            "A7FF8_WRITE_CONTROL_DETAIL": "1",
        },
        "resume_rule": "skip shard when manifest exists and process returncode == 0",
        "checkpoint_policy": "first run 2-4 primary shards, inspect runtime/memory, then scale to parallelism 8-12",
    }
    write_json(RUNTIME / "a7ls3hr_company_command_template.json", command_template)

    blockers: list[str] = []
    if int(primary_plan["company_numeric_shard"].nunique()) != 16:
        blockers.append("primary_shard_count_not_16")
    if int(fallback_plan["company_numeric_shard"].nunique()) != 32:
        blockers.append("fallback_shard_count_not_32")
    if queue["a7ls_arm"].nunique() < 4:
        blockers.append("not_all_arms_present")
    decision = "PASS_A7LS3HR_COMPANY_HANDOFF_RESIZED_64_READY" if not blockers else "HOLD_A7LS3HR_RESIZE_WEAK"
    manifest = {
        "stage": "A7LS-3HR",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "source_stage": "A7LS-3H",
        "source_decision": src_manifest.get("decision"),
        "queue_rows": int(len(queue)),
        "primary_rows_per_shard": primary_rows,
        "primary_shard_count": int(primary_plan["company_numeric_shard"].nunique()),
        "fallback_rows_per_shard": fallback_rows,
        "fallback_shard_count": int(fallback_plan["company_numeric_shard"].nunique()),
        "recommended_parallelism": 8,
        "max_parallelism_if_memory_headroom_confirmed": 12,
        "executes_numeric_probe": False,
        "executes_search": False,
        "authorizes_company_numeric_async_64": decision.startswith("PASS_"),
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ls3hr_manifest.json", manifest)

    REPORT.write_text("\n".join([
        "# CRYPTO A7LS-3HR COMPANY HANDOFF RESIZE",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7LS-3HR resizes the company numeric handoff from 32 rows/shard to 64 rows/shard while preserving a 32-row fallback plan. It does not execute numeric probe locally.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Arm Summary",
        "",
        md_table(arm_summary, 20),
        "",
        "## Primary 64-Row Shard Plan",
        "",
        md_table(primary_plan, 40),
        "",
        "## Fallback 32-Row Shard Plan",
        "",
        md_table(fallback_plan, 40),
        "",
        "## Command Template",
        "",
        "```json",
        json.dumps(command_template, indent=2, sort_keys=True),
        "```",
    ]), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
