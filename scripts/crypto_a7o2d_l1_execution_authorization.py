from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR
from crypto_a7o2c_semantic_uniqueness_audit import stable_file_hash, write_json, write_markdown_table


DATE_TAG = "20260520"
A7O2D_DIR = RUNTIME_DIR / "a7o2d_l1_execution_authorization"
A7O2C4_DIR = RUNTIME_DIR / "a7o2c4_cell_context_semantic_repair"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    A7O2D_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = utc_now()

    c4_manifest_path = A7O2C4_DIR / "a7o2c4_cell_context_semantic_repair_manifest.json"
    if not c4_manifest_path.exists():
        raise FileNotFoundError(f"missing A7O-2C4 manifest: {c4_manifest_path}")
    c4_manifest = load_json(c4_manifest_path)
    c4_ready = bool(c4_manifest.get("ready_for_a7o2d_authorization_record")) and not c4_manifest.get("blockers")

    authorization_rows = [
        {"scope": "A7O-L1 pilot shard", "authorized": c4_ready, "reason": "A7O-2C4 semantic/horizon/fold gates passed"},
        {"scope": "A7O-L1 full continuation after pilot pass", "authorized": c4_ready, "reason": "conditional on pilot shard checkpoint gates"},
        {"scope": "A7O-L1 unconditional full run", "authorized": False, "reason": "pilot shard and every-64-cell checkpoint required"},
        {"scope": "A7O-L2", "authorized": False, "reason": "requires L1 eligible pool and diversity pass"},
        {"scope": "A7O-L3", "authorized": False, "reason": "contract-only, not authorized"},
        {"scope": "alpha proof", "authorized": False, "reason": "A7O-L1 can only produce research candidate pool"},
        {"scope": "shadow/paper/live", "authorized": False, "reason": "requires future alpha proof and execution validation"},
    ]
    authorization = pd.DataFrame(authorization_rows)

    plan = pd.DataFrame(
        [
            {
                "stage": "A7O-L1 pilot shard",
                "cells": 64,
                "generated_per_cell": 2048,
                "total_generated": 64 * 2048,
                "strict_replay_per_cell": 24,
                "strict_replay_total": 64 * 24,
                "deep_audit_per_cell": 3,
                "deep_audit_total": 64 * 3,
                "checkpoint": "after pilot",
            },
            {
                "stage": "A7O-L1 full protected run",
                "cells": 1024,
                "generated_per_cell": 2048,
                "total_generated": 1024 * 2048,
                "strict_replay_per_cell": 24,
                "strict_replay_total": 1024 * 24,
                "deep_audit_per_cell": 3,
                "deep_audit_total": 1024 * 3,
                "checkpoint": "every 64 cells",
            },
        ]
    )

    stop_rules = pd.DataFrame(
        [
            {"gate": "may_leakage_violations", "threshold": "0", "action": "stop"},
            {"gate": "fold_metric_missing_rate", "threshold": "<= 0.01", "action": "stop_or_repair"},
            {"gate": "liquidity_volatility_deep_share", "threshold": "<= 0.15", "action": "stop_if_exceeded_after_checkpoint"},
            {"gate": "single_horizon_deep_share", "threshold": "<= 0.35", "action": "stop_if_exceeded_after_checkpoint"},
            {"gate": "single_return_corr_cluster_share", "threshold": "<= 0.35", "action": "stop_if_exceeded_after_checkpoint"},
            {"gate": "placebo_or_null_research_candidates", "threshold": "0", "action": "stop"},
            {"gate": "post_may_eligible_deep_survivors", "threshold": ">= 24 for full L1 pass", "action": "hold_if_not_met"},
        ]
    )

    paths = {
        "authorization_matrix": A7O2D_DIR / "a7o2d_authorization_matrix.csv",
        "execution_plan": A7O2D_DIR / "a7o2d_l1_execution_plan.csv",
        "checkpoint_stop_rules": A7O2D_DIR / "a7o2d_checkpoint_stop_rules.csv",
        "manifest": A7O2D_DIR / "a7o2d_manifest.json",
    }
    authorization.to_csv(paths["authorization_matrix"], index=False)
    plan.to_csv(paths["execution_plan"], index=False)
    stop_rules.to_csv(paths["checkpoint_stop_rules"], index=False)

    decision = "AUTHORIZED_A7O_L1_PROTECTED_PILOT_AND_CONDITIONAL_FULL_RUN" if c4_ready else "HOLD_A7O2D_C4_NOT_READY"
    manifest = {
        "generated_at": now,
        "decision": decision,
        "input_c4_manifest": str(c4_manifest_path),
        "input_c4_manifest_hash": stable_file_hash([c4_manifest_path]),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_l1_pilot_execution": bool(c4_ready),
        "authorizes_full_l1_continuation_after_pilot_pass": bool(c4_ready),
        "authorizes_unconditional_full_l1_execution": False,
        "authorizes_l2_execution": False,
        "authorizes_l3_execution": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "pilot_shard": {
            "cells": 64,
            "generated": 64 * 2048,
            "strict_replay": 64 * 24,
            "deep_audit": 64 * 3,
        },
        "full_l1_plan": {
            "cells": 1024,
            "generated": 1024 * 2048,
            "strict_replay": 1024 * 24,
            "deep_audit": 1024 * 3,
            "checkpoint_every_cells": 64,
        },
        "outputs": {k: str(v) for k, v in paths.items() if k != "manifest"},
    }
    manifest["stable_manifest_hash"] = stable_file_hash([v for k, v in paths.items() if k != "manifest"])
    write_json(paths["manifest"], manifest)

    report = [
        "# Crypto A7O-2D L1 Execution Authorization",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision}`",
        "- executes_search: `False`",
        "- executes_replay: `False`",
        f"- authorizes_l1_pilot_execution: `{bool(c4_ready)}`",
        f"- authorizes_full_l1_continuation_after_pilot_pass: `{bool(c4_ready)}`",
        "- authorizes_unconditional_full_l1_execution: `False`",
        "- authorizes_l2_execution: `False`",
        "- authorizes_l3_execution: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Authorization Matrix",
        "",
        write_markdown_table(authorization, 20),
        "## Execution Plan",
        "",
        write_markdown_table(plan, 10),
        "## Checkpoint Stop Rules",
        "",
        write_markdown_table(stop_rules, 20),
        "## Decision",
        "",
        "A7O-L1 may start only as a protected pilot shard. Full L1 continuation requires pilot checkpoint review and then every-64-cell checkpoint monitoring. A7O-L1 can only produce a research candidate pool.",
    ]
    report_path = REPORT_DIR / f"CRYPTO_A7O2D_L1_EXECUTION_AUTHORIZATION_{DATE_TAG}.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    print(
        json.dumps(
            {
                "decision": decision,
                "authorizes_l1_pilot_execution": bool(c4_ready),
                "authorizes_full_l1_continuation_after_pilot_pass": bool(c4_ready),
                "authorizes_unconditional_full_l1_execution": False,
                "manifest": str(paths["manifest"]),
                "report": str(report_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
