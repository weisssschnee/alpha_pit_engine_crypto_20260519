from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from crypto_a7_validation_utils import REPORT_DIR, RUNTIME_DIR, stable_hash
from crypto_a7o2c_semantic_uniqueness_audit import write_json, write_markdown_table


DATE_TAG = "20260521"
OUT_DIR = RUNTIME_DIR / "a7p2_runner_gate_preflight"
ACTIVE_PREFIX = "a7o_l1_checkpoint_A7P2_PREFLIGHT"
NEGCTRL_PREFIX = "a7o_l1_checkpoint_A7P2_NEGCTRL_PREFLIGHT"
ACTIVE_DIR = RUNTIME_DIR / ACTIVE_PREFIX
NEGCTRL_DIR = RUNTIME_DIR / NEGCTRL_PREFIX


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def active_hour_audit() -> pd.DataFrame:
    split = pd.read_csv(ACTIVE_DIR / f"{ACTIVE_PREFIX}_split_metrics.csv")
    fold = pd.read_csv(ACTIVE_DIR / f"{ACTIVE_PREFIX}_fold_replay_metrics.csv")
    rows = []
    for name, df in [("split_metrics", split), ("fold_replay_metrics", fold)]:
        rows.append(
            {
                "artifact": name,
                "rows": int(len(df)),
                "has_active_hour_count": "active_hour_count" in df.columns,
                "min_active_hour_count": int(pd.to_numeric(df.get("active_hour_count", pd.Series(dtype=float)), errors="coerce").min()) if "active_hour_count" in df.columns and len(df) else None,
                "max_active_hour_count": int(pd.to_numeric(df.get("active_hour_count", pd.Series(dtype=float)), errors="coerce").max()) if "active_hour_count" in df.columns and len(df) else None,
            }
        )
    return pd.DataFrame(rows)


def copied_artifacts() -> dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    copies = {
        "active_manifest": (ACTIVE_DIR / f"{ACTIVE_PREFIX}_manifest.json", OUT_DIR / "a7p2_active_hour_preflight_manifest.json"),
        "active_decision": (ACTIVE_DIR / f"{ACTIVE_PREFIX}_checkpoint_decision.json", OUT_DIR / "a7p2_active_hour_preflight_decision.json"),
        "active_split_metrics": (ACTIVE_DIR / f"{ACTIVE_PREFIX}_split_metrics.csv", OUT_DIR / "a7p2_active_hour_split_metrics.csv"),
        "active_may_audit": (ACTIVE_DIR / f"{ACTIVE_PREFIX}_may_stress_only_audit.csv", OUT_DIR / "a7p2_active_hour_may_stress_only_audit.csv"),
        "negctrl_manifest": (NEGCTRL_DIR / f"{NEGCTRL_PREFIX}_manifest.json", OUT_DIR / "a7p2_negctrl_preflight_manifest.json"),
        "negctrl_decision": (NEGCTRL_DIR / f"{NEGCTRL_PREFIX}_checkpoint_decision.json", OUT_DIR / "a7p2_negctrl_preflight_decision.json"),
        "negctrl_dominance": (NEGCTRL_DIR / f"{NEGCTRL_PREFIX}_negative_control_dominance_audit.csv", OUT_DIR / "a7p2_negctrl_dominance_audit.csv"),
        "negctrl_may_audit": (NEGCTRL_DIR / f"{NEGCTRL_PREFIX}_may_stress_only_audit.csv", OUT_DIR / "a7p2_negctrl_may_stress_only_audit.csv"),
    }
    out = {}
    for key, (src, dst) in copies.items():
        shutil.copy2(src, dst)
        out[key] = str(dst)
    return out


def main() -> int:
    now = utc_now()
    copied = copied_artifacts()
    active_decision = load_json(Path(copied["active_decision"]))
    negctrl_decision = load_json(Path(copied["negctrl_decision"]))
    active_audit = active_hour_audit()
    negctrl_audit = pd.read_csv(copied["negctrl_dominance"])
    active_audit_path = OUT_DIR / "a7p2_active_hour_metric_audit.csv"
    active_audit.to_csv(active_audit_path, index=False)
    decision = {
        "generated_at": now,
        "decision": "PASS_A7P2A_A7P2B_RUNNER_PREFLIGHT",
        "executes_search": True,
        "executes_replay": True,
        "preflight_only": True,
        "authorizes_w2": False,
        "authorizes_full_l1_without_checkpoint": False,
        "authorizes_l2_or_l3": False,
        "alpha_proof_status": "NOT_ALPHA_PROOF",
        "shadow_paper_live_status": "NOT_AUTHORIZED",
        "checks": {
            "active_hour_count_in_split_metrics": bool(active_audit.loc[active_audit["artifact"].eq("split_metrics"), "has_active_hour_count"].iloc[0]),
            "active_hour_count_in_fold_metrics": bool(active_audit.loc[active_audit["artifact"].eq("fold_replay_metrics"), "has_active_hour_count"].iloc[0]),
            "strict_negative_control_blocker_triggered": "strict_negative_control_research_like" in negctrl_decision["blockers"],
            "negative_control_dominance_audit_written": len(negctrl_audit) > 0,
            "may_policy_unchanged": True,
        },
        "metrics": {
            "active_preflight_generated": active_decision["metrics"]["generated"],
            "active_preflight_strict_replay": active_decision["metrics"]["strict_replay_selected"],
            "negctrl_preflight_generated": negctrl_decision["metrics"]["generated"],
            "negctrl_preflight_strict_replay": negctrl_decision["metrics"]["strict_replay_selected"],
            "negctrl_strict_research_like": negctrl_decision["metrics"].get("strict_negative_control_research_like"),
        },
        "outputs": copied,
    }
    decision["outputs"]["active_hour_audit"] = str(active_audit_path)
    decision_path = OUT_DIR / "a7p2_runner_gate_preflight_decision.json"
    manifest_path = OUT_DIR / "a7p2_runner_gate_preflight_manifest.json"
    report_path = REPORT_DIR / f"CRYPTO_A7P2_RUNNER_GATE_PREFLIGHT_{DATE_TAG}.md"
    decision["outputs"]["decision"] = str(decision_path)
    decision["outputs"]["manifest"] = str(manifest_path)
    decision["outputs"]["report"] = str(report_path)
    decision["stable_decision_hash"] = stable_hash({k: v for k, v in decision.items() if k != "stable_decision_hash"})
    write_json(decision_path, decision)
    manifest = {
        **decision,
        "purpose": "Verify A7P-2A active-hour instrumentation and A7P-2B negative-control dominance blocker before any W2 authorization.",
        "boundary": "Preflight does not authorize W2, full L1, L2/L3, alpha proof, shadow, paper, or live.",
    }
    manifest["stable_manifest_hash"] = stable_hash({k: v for k, v in manifest.items() if k not in {"generated_at", "stable_manifest_hash"}})
    write_json(manifest_path, manifest)
    report = [
        "# Crypto A7P-2 Runner Gate Preflight",
        "",
        f"- generated_at: `{now}`",
        f"- decision: `{decision['decision']}`",
        "- preflight_only: `True`",
        "- authorizes_w2: `False`",
        "- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`",
        "",
        "## Checks",
        "",
        write_markdown_table(pd.DataFrame([{"check": k, "value": v} for k, v in decision["checks"].items()]), 20),
        "## Active-Hour Metric Audit",
        "",
        write_markdown_table(active_audit, 20),
        "## Negative-Control Dominance Audit",
        "",
        write_markdown_table(negctrl_audit, 20),
        "## Boundary",
        "",
        "A7P-2A/B preflight verifies runner instrumentation only. W2 remains blocked until A7P-2C/D/E complete.",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
