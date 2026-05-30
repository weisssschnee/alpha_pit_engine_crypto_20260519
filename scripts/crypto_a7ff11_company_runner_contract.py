from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff11_company_runner_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF11_COMPANY_RUNNER_CONTRACT_20260530.md"

A7FF10_PARALLEL = REPO / "runtime" / "a7ff10_company_parallel"
A7FF10_AGG = REPO / "runtime" / "a7ff10_company_parallel_aggregate"


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
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def scan_log(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    return {
        "log": path.name,
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
        "has_pass_decision": "PASS_A7FF10" in text,
        "has_traceback": "Traceback" in text,
        "has_tabulate_error": "No module named 'tabulate'" in text or "Import tabulate" in text,
        "has_missing_numpy": "No module named 'numpy'" in text,
        "has_missing_data_root": "AlphaFactory_CryptoData" in text and "missing" in text.lower(),
    }


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    agg_manifest = read_json(A7FF10_AGG / "a7ff10_manifest.json")
    launch_manifest_path = A7FF10_PARALLEL / "a7ff10_company_parallel_launch_manifest.csv"
    launch = pd.read_csv(launch_manifest_path) if launch_manifest_path.exists() else pd.DataFrame()
    logs = pd.DataFrame([scan_log(path) for path in sorted(A7FF10_PARALLEL.glob("a7ff10s*.log"))])

    issue_rows: list[dict[str, Any]] = []
    if not logs.empty and bool(logs["has_tabulate_error"].any()):
        issue_rows.append(
            {
                "issue": "remote_venv_missing_tabulate_for_report_render",
                "evidence": "A7FF-10S00 background log contains tabulate ImportError",
                "fix_applied": "md_table fallback added to numeric probe and aggregate scripts",
                "status": "fixed_for_future_runs",
            }
        )
    if not logs.empty and not bool(logs["has_pass_decision"].all()):
        issue_rows.append(
            {
                "issue": "background_launch_log_not_reliable_source_of_truth",
                "evidence": "At least one shard log does not contain final PASS even though final runtime manifest exists",
                "fix_applied": "Treat shard manifest and pulled report as source-of-truth; require per-shard manifest polling",
                "status": "requires_runner_hardening",
            }
        )
    issue_rows.append(
        {
            "issue": "company_machine_resource_preflight_required",
            "evidence": "Heavy shards share the machine with unrelated Python jobs",
            "fix_applied": "A7FF-12 launch must check free memory and heavy Python process count before starting",
            "status": "required_next_launch_gate",
        }
    )
    issues = pd.DataFrame(issue_rows)

    launch_contract = {
        "remote_host": "company-pc-via-hermes-stable",
        "remote_repo": "D:/HermesWorker/GDrive/Project_V7_Rotation/alpha_pit_engine_crypto_20260519_remote",
        "remote_python": "D:/HermesWorker/venvs/phase3z33/Scripts/python.exe",
        "data_root": "D:/HermesWorker/GDrive/AlphaFactory_CryptoData",
        "required_env": {
            "ALPHAFACTORY_CRYPTO_DATA_ROOT": "D:/HermesWorker/GDrive/AlphaFactory_CryptoData",
            "A7AL_BASE_PANEL_ROOT": "D:/HermesWorker/GDrive/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527",
        },
        "preflight_checks": [
            "python imports numpy/pandas/pyarrow",
            "base panel path exists",
            "meme taxonomy metadata exists",
            "free memory >= 8GB before starting 1 shard, >= 14GB before starting 2 shards",
            "no unrelated high-memory Python job unless running single-shard foreground",
            "per-shard manifest path is absent or explicitly quarantined before rerun",
        ],
        "recommended_execution_mode": "managed_foreground_or_manifest_polled_jobs",
        "background_start_process_status": "not_reliable_enough_for_unattended_scale_without_manifest_polling",
        "max_initial_parallel_shards": 2,
        "safe_fallback": "run shards sequentially via SSH foreground and pull manifests after each shard",
        "must_not_do": [
            "use D:/Python311/python.exe for numeric probes",
            "assume G:/AlphaFactory_CryptoData exists on company machine",
            "treat a process id in launch_manifest as completion evidence",
            "treat logs as source-of-truth when runtime manifests disagree",
        ],
    }

    decision = "PASS_A7FF11R_COMPANY_RUNNER_CONTRACT_READY_WITH_MANIFEST_POLLING_REQUIRED"
    manifest = {
        "stage": "A7FF-11R-COMPANY-RUNNER-CONTRACT",
        "generated_at": now_utc(),
        "decision": decision,
        "source_stage": agg_manifest.get("stage", "A7FF-10-COMPANY-PARALLEL-AGGREGATE"),
        "source_decision": agg_manifest.get("decision", ""),
        "launcher_rows": int(len(launch)),
        "log_rows": int(len(logs)),
        "issues_recorded": int(len(issues)),
        "authorizes_a7ff12_company_numeric_wave": True,
        "requires_manifest_polling": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    logs.to_csv(RUNTIME / "a7ff11r_log_issue_scan.csv", index=False)
    launch.to_csv(RUNTIME / "a7ff11r_launch_manifest_snapshot.csv", index=False)
    issues.to_csv(RUNTIME / "a7ff11r_runner_issue_summary.csv", index=False)
    write_json(RUNTIME / "a7ff11r_launch_contract.json", launch_contract)
    write_json(RUNTIME / "a7ff11r_manifest.json", manifest)

    lines = [
        "# CRYPTO A7FF-11R COMPANY RUNNER CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-11R records the company-machine launch contract for heavier A7FF numeric waves. It does not run search, replay, alpha proof, shadow, paper, or live execution.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Runner Issues",
        "",
        md_table(issues),
        "",
        "## Log Scan",
        "",
        md_table(logs),
        "",
        "## Launch Contract",
        "",
        "```json",
        json.dumps(launch_contract, indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "A7FF-12 may use the company machine for numeric-wave scale-up only after preflight checks pass.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
