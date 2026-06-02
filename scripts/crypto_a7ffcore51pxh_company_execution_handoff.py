from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore51pxh_company_execution_handoff"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE51PXH_COMPANY_EXECUTION_HANDOFF_20260602.md"
CORE51PXV = REPO / "runtime" / "a7ffcore51pxv_company_execution_preflight_validator" / "a7ffcore51pxv_manifest.json"
COMMANDS = REPO / "runtime" / "a7ffcore51px_company_sharded_replay_runner_contract" / "a7ffcore51px_company_execution_commands.ps1"
OUT = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602")


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
    source = read_json(CORE51PXV)
    if source.get("decision") != "PASS_A7FFCORE51PXV_COMPANY_EXECUTION_PREFLIGHT_READY":
        raise SystemExit(f"CORE51PXV not ready for handoff: {source.get('decision')}")

    execution_steps = pd.DataFrame(
        [
            {
                "step": 1,
                "name": "run_orchestrator",
                "command": f"powershell -ExecutionPolicy Bypass -File {COMMANDS.as_posix()}",
                "purpose": "build compact frame and run 16 replay shards with jobs=8",
            },
            {
                "step": 2,
                "name": "check_status",
                "command": f"py {REPO.as_posix()}/scripts/crypto_a7ffcore51pxe_company_status.py --out {OUT.as_posix()}",
                "purpose": "inspect shard completion and missing manifests",
            },
            {
                "step": 3,
                "name": "aggregate_if_needed",
                "command": f"py {REPO.as_posix()}/scripts/crypto_a7ffcore51pxe_company_result_aggregator.py --out {OUT.as_posix()} --expected-shards 16",
                "purpose": "rebuild aggregate summary if orchestrator completed but summary is stale/missing",
            },
            {
                "step": 4,
                "name": "import_to_repo_after_completion",
                "command": f"py {REPO.as_posix()}/scripts/crypto_a7ffcore51pxe_import_company_results.py --out {OUT.as_posix()}",
                "purpose": "copy aggregate summaries into repo runtime for CORE52 arbitration",
            },
        ]
    )
    acceptance = pd.DataFrame(
        [
            {"gate": "completed_shards", "pass_condition": "16/16 shard manifests PASS"},
            {"gate": "eval_failures", "pass_condition": "aggregate eval_failure_count == 0"},
            {"gate": "metric_rows", "pass_condition": "aggregate metric_rows > 0"},
            {"gate": "import_manifest", "pass_condition": "repo runtime import decision PASS"},
            {"gate": "authorization_boundary", "pass_condition": "no formula search / proof / promotion / live"},
        ]
    )
    failure_policy = pd.DataFrame(
        [
            {"failure": "single_shard_timeout", "action": "rerun only that shard with --force after checking compact frame exists"},
            {"failure": "compact_frame_build_fail", "action": "check base/latent panel availability and field contract"},
            {"failure": "multiple_shard_failures", "action": "freeze CORE51PXE as runner/data issue and open forensic; do not search"},
            {"failure": "control_clean_zero", "action": "still aggregate/import; CORE52 decides signal route"},
        ]
    )
    decision = "PASS_A7FFCORE51PXH_COMPANY_EXECUTION_HANDOFF_READY"
    manifest = {
        "stage": "A7FF-CORE51PXH",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE51PXV",
        "source_decision": source.get("decision"),
        "decision": decision,
        "output_dir": OUT.as_posix(),
        "command_file": COMMANDS.as_posix(),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core51pxe_execution": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE51PXE company-machine sharded replay execution",
    }
    execution_steps.to_csv(RUNTIME / "a7ffcore51pxh_execution_steps.csv", index=False)
    acceptance.to_csv(RUNTIME / "a7ffcore51pxh_acceptance_gates.csv", index=False)
    failure_policy.to_csv(RUNTIME / "a7ffcore51pxh_failure_policy.csv", index=False)
    write_json(RUNTIME / "a7ffcore51pxh_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE51PXH COMPANY EXECUTION HANDOFF",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "This is the execution handoff for company-machine sharded replay. It does not run replay itself.",
        "",
        "## Execution Steps",
        "",
        md_table(execution_steps, 20),
        "",
        "## Acceptance Gates",
        "",
        md_table(acceptance),
        "",
        "## Failure Policy",
        "",
        md_table(failure_policy),
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
