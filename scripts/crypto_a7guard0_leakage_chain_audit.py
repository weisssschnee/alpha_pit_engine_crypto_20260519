from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
DATE = "20260612"
STAGE = "A7GUARD-0"
RUNTIME = REPO / "runtime" / "a7guard0_leakage_chain_audit_20260612"
REPORT = REPO / "reports" / "CRYPTO_A7GUARD0_LEAKAGE_CHAIN_AUDIT_20260612.md"

SCRIPT_ALLOWLIST = {
    "crypto_a7guard0_leakage_chain_audit.py",
}

INTENTIONAL_CONTEXT = re.compile(
    r"(control|wrong_lag|future_label|horizon_label|label_|_label|label_matrix|forward_return|fwd_ret|label_end|stress|leakage_scan|bias_audit)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ScanPattern:
    name: str
    regex: re.Pattern[str]
    category: str
    severity: str
    rationale: str


PATTERNS = [
    ScanPattern(
        "negative_shift_or_lag",
        re.compile(r"(\.shift\s*\(\s*-\d+|shift_matrix\s*\([^,\n]+,\s*-\d+|np\.roll\s*\([^,\n]+,\s*-\d+)"),
        "lookahead_or_control",
        "high",
        "Negative shifts are valid only for label/control construction; production features must never use them.",
    ),
    ScanPattern(
        "negative_pct_change_or_diff",
        re.compile(r"(\.pct_change\s*\(\s*-\d+|\.diff\s*\(\s*-\d+)"),
        "lookahead",
        "high",
        "Negative diff/pct_change can directly leak future returns into a feature.",
    ),
    ScanPattern(
        "centered_rolling",
        re.compile(r"\.rolling\s*\([^)]*center\s*=\s*True"),
        "lookahead",
        "high",
        "Centered rolling windows use future observations unless explicitly delayed.",
    ),
    ScanPattern(
        "backward_fill",
        re.compile(r"(\.bfill\s*\(|method\s*=\s*['\"]bfill['\"]|fillna\s*\([^)]*method\s*=\s*['\"]bfill['\"])"),
        "timestamp_alignment",
        "medium",
        "Backward fill can import future observations into earlier timestamps.",
    ),
    ScanPattern(
        "merge_asof_forward_or_nearest",
        re.compile(r"merge_asof\s*\([^)]*direction\s*=\s*['\"](?:forward|nearest)['\"]", re.DOTALL),
        "timestamp_alignment",
        "high",
        "Forward or nearest as-of joins are unsafe for PIT features without a strict lag proof.",
    ),
    ScanPattern(
        "full_sample_fit_transform",
        re.compile(r"(fit_transform\s*\(|StandardScaler\s*\(|PCA\s*\(|KMeans\s*\()"),
        "train_oos_contamination",
        "medium",
        "Model/statistic fitting must be split-aware; full-sample fit contaminates OOS.",
    ),
    ScanPattern(
        "global_rank_or_quantile",
        re.compile(r"(\.rank\s*\(|\.quantile\s*\()"),
        "normalization_scope",
        "low",
        "Ranks/quantiles must be timestamp-local, train-only, or explicitly rolling.",
    ),
]


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def md_table(frame: pd.DataFrame, max_rows: int = 40) -> str:
    if frame.empty:
        return "`<empty>`"
    view = frame.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    try:
        return view.to_markdown(index=False)
    except ImportError:
        return "```text\n" + view.to_string(index=False) + "\n```"


def classify_occurrence(path: Path, context_block: str, pattern: ScanPattern) -> tuple[str, str]:
    rel = path.relative_to(REPO).as_posix()
    context = f"{rel} {context_block}"
    if path.name in SCRIPT_ALLOWLIST:
        return "allowlisted_guard_self", "ignore"
    if INTENTIONAL_CONTEXT.search(context):
        return "intentional_label_or_control_context", "review"
    if "tests/" in rel or rel.startswith("test_"):
        return "test_context", "review"
    if pattern.severity == "high":
        return "potential_blocker", "hold_review"
    if pattern.severity == "medium":
        return "needs_pit_proof", "review"
    return "scope_check", "review"


def static_leakage_scan() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in sorted((REPO / "scripts").glob("*.py")):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            rows.append(
                {
                    "path": path.relative_to(REPO).as_posix(),
                    "line_no": 0,
                    "pattern": "read_error",
                    "category": "scan_error",
                    "severity": "medium",
                    "decision": "review",
                    "classification": "read_error",
                    "excerpt": repr(exc),
                    "rationale": "File could not be scanned.",
                }
            )
            continue
        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            for pattern in PATTERNS:
                if pattern.regex.search(line):
                    context_block = "\n".join(lines[max(0, line_no - 4) : min(len(lines), line_no + 3)])
                    classification, decision = classify_occurrence(path, context_block, pattern)
                    rows.append(
                        {
                            "path": path.relative_to(REPO).as_posix(),
                            "line_no": line_no,
                            "pattern": pattern.name,
                            "category": pattern.category,
                            "severity": pattern.severity,
                            "decision": decision,
                            "classification": classification,
                            "excerpt": stripped[:260],
                            "rationale": pattern.rationale,
                        }
                    )
    return pd.DataFrame(rows)


def file_contains(path: Path, needles: list[str]) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return all(needle in text for needle in needles)


def chain_gate_inventory() -> pd.DataFrame:
    reward_script = REPO / "scripts" / "crypto_a7reward1_portfolio_reward_model.py"
    reward_runtime = REPO / "runtime" / "a7reward1_portfolio_reward_model_20260610"
    checks = [
        {
            "gate": "reward_writes_accepted_queue",
            "artifact": reward_script.relative_to(REPO).as_posix(),
            "status": "PASS"
            if file_contains(reward_script, ["a7reward1_accepted_for_next_search.csv", "a7reward1_validation_gate_rejections.csv"])
            else "FAIL",
            "required_action": "Reward must auto-write accepted/rejected queues; raw selected queues cannot feed search directly.",
        },
        {
            "gate": "reward_uses_nonoverlap_floor",
            "artifact": reward_script.relative_to(REPO).as_posix(),
            "status": "PASS" if file_contains(reward_script, ["min_oos_floor_sortino", "oos_nonoverlap_floor_not_positive"]) else "FAIL",
            "required_action": "Reward must reject candidates with negative OOS non-overlap floors.",
        },
        {
            "gate": "reward_has_control_gate",
            "artifact": reward_script.relative_to(REPO).as_posix(),
            "status": "PASS" if file_contains(reward_script, ["recent_shuffle_control_ratio < 1", "CONTROL_VARIANTS"]) else "FAIL",
            "required_action": "Reward must compare original signal against controls before next-search acceptance.",
        },
        {
            "gate": "reward_orientation_not_tail720_only",
            "artifact": reward_script.relative_to(REPO).as_posix(),
            "status": "PASS" if file_contains(reward_script, ["--train-hours-per-split", "orientation_extension_hours"]) else "FAIL",
            "required_action": "Orientation must support full train and explicitly logged contiguous extension; tail-only orientation is not enough.",
        },
        {
            "gate": "accepted_queue_exists",
            "artifact": (reward_runtime / "a7reward1_accepted_for_next_search.csv").relative_to(REPO).as_posix(),
            "status": "PASS" if (reward_runtime / "a7reward1_accepted_for_next_search.csv").exists() else "MISSING",
            "required_action": "Search seeds must come from accepted_for_next_search after rerun under current reward code.",
        },
        {
            "gate": "rejection_queue_exists",
            "artifact": (reward_runtime / "a7reward1_validation_gate_rejections.csv").relative_to(REPO).as_posix(),
            "status": "PASS" if (reward_runtime / "a7reward1_validation_gate_rejections.csv").exists() else "MISSING",
            "required_action": "Rejected candidates and reasons must be retained for audit.",
        },
    ]
    return pd.DataFrame(checks)


def runtime_result_inventory() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in sorted((REPO / "runtime").glob("**/*.csv")):
        name = path.name.lower()
        if not any(token in name for token in ["selected", "accepted", "reward", "gate", "queue", "manifest"]):
            continue
        rel = path.relative_to(REPO).as_posix()
        rows.append(
            {
                "artifact": rel,
                "size_bytes": path.stat().st_size,
                "class": "accepted_search_input"
                if "accepted_for_next_search" in name
                else ("raw_selected_or_queue" if "selected" in name or "queue" in name else "diagnostic_or_gate"),
                "search_feed_policy": "allowed_after_current_reward_rerun"
                if "accepted_for_next_search" in name
                else "not_allowed_directly_without_guard",
            }
        )
    return pd.DataFrame(rows)


def required_fixes(static_scan: pd.DataFrame, gates: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    blockers = static_scan[static_scan["decision"].eq("hold_review")] if not static_scan.empty else pd.DataFrame()
    if not blockers.empty:
        rows.append(
            {
                "priority": "P0",
                "issue": "Potential production lookahead patterns need owner review.",
                "evidence": f"{len(blockers)} high-severity static occurrences outside obvious label/control context.",
                "required_action": "Classify each as feature, label, control, or test path; production feature occurrences must be blocked or lagged.",
            }
        )
    failed_gates = gates[~gates["status"].isin(["PASS"])] if not gates.empty else pd.DataFrame()
    for _, row in failed_gates.iterrows():
        rows.append(
            {
                "priority": "P0" if row["status"] == "FAIL" else "P1",
                "issue": f"Gate not clean: {row['gate']}",
                "evidence": f"{row['artifact']} status={row['status']}",
                "required_action": row["required_action"],
            }
        )
    rows.append(
        {
            "priority": "P0",
            "issue": "Next large search must consume guarded accepted queues only.",
            "evidence": "Raw selected queues are discovery artifacts, not promotion artifacts.",
            "required_action": "Wire pre-search launcher to require A7GUARD-0 PASS plus current reward accepted_for_next_search from the active code version.",
        }
    )
    rows.append(
        {
            "priority": "P1",
            "issue": "Regime sufficiency remains a data dependency.",
            "evidence": "A7REGIME-1 found thin extreme volatility, funding extreme, and liquidity expansion OOS coverage.",
            "required_action": "Add about six months forward data if available, and prefer earlier-history backfill for high-volatility regimes.",
        }
    )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", default=str(RUNTIME))
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--fail-on-hold", action="store_true", help="Exit non-zero unless the guard decision is PASS.")
    parser.add_argument(
        "--require-accepted-queue",
        default="",
        help="Optional explicit accepted_for_next_search CSV path required by a pre-search launcher.",
    )
    args = parser.parse_args()

    runtime = Path(args.runtime)
    report = Path(args.report)
    runtime.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    static_scan = static_leakage_scan()
    gates = chain_gate_inventory()
    if args.require_accepted_queue:
        queue_path = Path(args.require_accepted_queue)
        if not queue_path.is_absolute():
            queue_path = REPO / queue_path
        gates = pd.concat(
            [
                gates,
                pd.DataFrame(
                    [
                        {
                            "gate": "explicit_presearch_accepted_queue_exists",
                            "artifact": str(queue_path.relative_to(REPO) if queue_path.is_relative_to(REPO) else queue_path),
                            "status": "PASS" if queue_path.exists() and queue_path.stat().st_size > 0 else "FAIL",
                            "required_action": "Pre-search launcher must point to a non-empty accepted_for_next_search queue, not a raw selected queue.",
                        },
                        {
                            "gate": "explicit_presearch_queue_is_accepted_type",
                            "artifact": str(queue_path.relative_to(REPO) if queue_path.is_relative_to(REPO) else queue_path),
                            "status": "PASS" if "accepted_for_next_search" in queue_path.name else "FAIL",
                            "required_action": "Queue filename must make the promotion status explicit.",
                        },
                    ]
                ),
            ],
            ignore_index=True,
        )
    artifacts = runtime_result_inventory()
    fixes = required_fixes(static_scan, gates)

    write_csv(runtime / "a7guard0_static_leakage_scan.csv", static_scan)
    write_csv(runtime / "a7guard0_chain_gate_inventory.csv", gates)
    write_csv(runtime / "a7guard0_runtime_result_inventory.csv", artifacts)
    write_csv(runtime / "a7guard0_required_fixes.csv", fixes)

    hold_review = int(static_scan["decision"].eq("hold_review").sum()) if not static_scan.empty else 0
    gate_fail = int(gates["status"].eq("FAIL").sum()) if not gates.empty else 0
    gate_missing = int(gates["status"].eq("MISSING").sum()) if not gates.empty else 0
    decision = "HOLD_A7GUARD0_REVIEW_REQUIRED" if hold_review or gate_fail or gate_missing else "PASS_A7GUARD0_PRESEARCH_GUARD_READY"

    manifest = {
        "stage": STAGE,
        "generated_at": now_utc(),
        "decision": decision,
        "static_scan_rows": int(static_scan.shape[0]),
        "static_hold_review_rows": hold_review,
        "gate_rows": int(gates.shape[0]),
        "gate_fail_rows": gate_fail,
        "gate_missing_rows": gate_missing,
        "runtime_artifact_rows": int(artifacts.shape[0]),
        "outputs": {
            "static_leakage_scan": str((runtime / "a7guard0_static_leakage_scan.csv").relative_to(REPO)),
            "chain_gate_inventory": str((runtime / "a7guard0_chain_gate_inventory.csv").relative_to(REPO)),
            "runtime_result_inventory": str((runtime / "a7guard0_runtime_result_inventory.csv").relative_to(REPO)),
            "required_fixes": str((runtime / "a7guard0_required_fixes.csv").relative_to(REPO)),
            "report": str(report.relative_to(REPO)),
        },
        "guard_policy": {
            "raw_selected_queues": "not_allowed_directly_without_guard",
            "accepted_for_next_search": "allowed_only_after_current_reward_rerun_and_guard_review",
            "negative_shift": "allowed only in label/control code paths",
            "backward_fill": "requires explicit PIT proof",
            "fit_transform": "requires split-aware fit proof",
        },
    }
    write_json(runtime / "a7guard0_manifest.json", manifest)

    top_static = static_scan.sort_values(["decision", "severity", "path", "line_no"]) if not static_scan.empty else static_scan
    report.write_text(
        "\n".join(
            [
                "# CRYPTO A7GUARD0 Leakage And Chain Audit 20260612",
                "",
                "## Decision",
                "",
                f"`{decision}`",
                "",
                "This audit does not authorize alpha proof, shadow, paper, or live execution.",
                "",
                "## Data Sufficiency Read",
                "",
                "A further half year of data is likely enough to improve most regime coverage gaps, especially funding extreme and drawdown-like states. It is not a guaranteed fix for rare high-volatility or liquidity-expansion regimes if those states do not occur in the added period. Earlier-history backfill remains the cleaner way to fill high-volatility samples.",
                "",
                "## Gate Inventory",
                "",
                md_table(gates, 30),
                "",
                "## Static Leakage Scan Summary",
                "",
                f"- scanned_occurrences: `{static_scan.shape[0]}`",
                f"- hold_review_occurrences: `{hold_review}`",
                "",
                md_table(top_static.head(40), 40),
                "",
                "## Required Fixes / Operating Rules",
                "",
                md_table(fixes, 30),
                "",
                "## Pre-Search Rule",
                "",
                "The next large search must not consume raw `selected_*` or diagnostic queues directly. It must consume a current-code `accepted_for_next_search` queue after reward rerun, with A7GUARD-0 attached as the pre-search audit packet.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(decision)
    print(report)
    if args.fail_on_hold and decision != "PASS_A7GUARD0_PRESEARCH_GUARD_READY":
        sys.exit(2)


if __name__ == "__main__":
    main()
