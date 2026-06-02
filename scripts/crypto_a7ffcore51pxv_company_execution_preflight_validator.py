from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore51pxv_company_execution_preflight_validator"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE51PXV_COMPANY_EXECUTION_PREFLIGHT_VALIDATOR_20260602.md"
CORE51PX = REPO / "runtime" / "a7ffcore51px_company_sharded_replay_runner_contract" / "a7ffcore51px_manifest.json"
CONTRACT = REPO / "runtime" / "a7ffcore51px_company_sharded_replay_runner_contract"
BASE_PANEL = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_replay_1h_v2_20260527")
LATENT_PANEL = Path("G:/AlphaFactory_CryptoData/gold/features/binance_universe498_latent_state_features_v1_20260527.parquet")
DEFAULT_OUT = Path("G:/AlphaFactory_CryptoData/research_runtime/a7ffcore51px_company_sharded_replay_20260602")


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


def compile_status(path: Path) -> tuple[str, str]:
    try:
        py_compile.compile(str(path), doraise=True)
        return "PASS", ""
    except Exception as exc:  # pragma: no cover - diagnostic output
        return "HOLD", str(exc)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE51PX)
    if source.get("decision") != "PASS_A7FFCORE51PX_COMPANY_SHARDED_REPLAY_CONTRACT_READY_FOR_COMPANY_EXECUTION":
        raise SystemExit(f"CORE51PX not ready for CORE51PXV: {source.get('decision')}")

    shard_files = sorted((CONTRACT / "candidate_shards").glob("*.csv"))
    selected = pd.read_csv(CONTRACT / "a7ffcore51px_selected_candidate_queue.csv")
    shard_plan = pd.read_csv(CONTRACT / "a7ffcore51px_candidate_shard_plan.csv")
    field_contract = pd.read_csv(CONTRACT / "a7ffcore51px_compact_frame_contract.csv")
    commands = CONTRACT / "a7ffcore51px_company_execution_commands.ps1"
    scripts = [
        REPO / "scripts" / "crypto_a7ffcore51px_company_compact_frame_builder.py",
        REPO / "scripts" / "crypto_a7ffcore51px_company_shard_worker.py",
        REPO / "scripts" / "crypto_a7ffcore51pxe_company_sharded_replay_orchestrator.py",
        REPO / "scripts" / "crypto_a7ffcore51pxe_company_result_aggregator.py",
        REPO / "scripts" / "crypto_a7ffcore51pxe_company_status.py",
        REPO / "scripts" / "crypto_a7ffcore51pxe_import_company_results.py",
    ]

    checks = []
    checks.append({"check": "base_panel_exists", "status": "PASS" if BASE_PANEL.exists() else "HOLD", "detail": str(BASE_PANEL)})
    checks.append({"check": "latent_panel_exists", "status": "PASS" if LATENT_PANEL.exists() else "HOLD", "detail": str(LATENT_PANEL)})
    checks.append({"check": "selected_candidate_count", "status": "PASS" if selected.shape[0] == 384 else "HOLD", "detail": str(selected.shape[0])})
    checks.append({"check": "shard_file_count", "status": "PASS" if len(shard_files) == 16 else "HOLD", "detail": str(len(shard_files))})
    checks.append({"check": "shard_plan_count", "status": "PASS" if shard_plan.shape[0] == 16 else "HOLD", "detail": str(shard_plan.shape[0])})
    checks.append({"check": "missing_field_count", "status": "PASS" if int(field_contract["status"].eq("missing").sum()) == 0 else "HOLD", "detail": str(int(field_contract["status"].eq("missing").sum()))})
    checks.append({"check": "command_template_exists", "status": "PASS" if commands.exists() else "HOLD", "detail": str(commands)})
    DEFAULT_OUT.mkdir(parents=True, exist_ok=True)
    probe = DEFAULT_OUT / ".write_probe"
    try:
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        out_status, out_detail = "PASS", str(DEFAULT_OUT)
    except Exception as exc:
        out_status, out_detail = "HOLD", str(exc)
    checks.append({"check": "external_output_dir_writable", "status": out_status, "detail": out_detail})

    script_rows = []
    for script in scripts:
        status, error = compile_status(script)
        script_rows.append({"script": str(script.relative_to(REPO)).replace("\\", "/"), "exists": script.exists(), "compile_status": status, "error": error})
    script_df = pd.DataFrame(script_rows)
    for _, row in script_df.iterrows():
        checks.append({"check": f"compile_{Path(row['script']).name}", "status": row["compile_status"], "detail": row["error"]})

    checks_df = pd.DataFrame(checks)
    blockers = checks_df.loc[~checks_df["status"].eq("PASS"), "check"].astype(str).tolist()
    decision = "PASS_A7FFCORE51PXV_COMPANY_EXECUTION_PREFLIGHT_READY" if not blockers else "HOLD_A7FFCORE51PXV_COMPANY_EXECUTION_PREFLIGHT_BLOCKERS"
    manifest = {
        "stage": "A7FF-CORE51PXV",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE51PX",
        "source_decision": source.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "selected_candidate_count": int(selected.shape[0]),
        "shard_count": int(len(shard_files)),
        "required_field_count": int(field_contract.shape[0]),
        "missing_field_count": int(field_contract["status"].eq("missing").sum()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core51pxe_execution": decision.startswith("PASS_"),
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE51PXE company-machine sharded replay execution" if decision.startswith("PASS_") else "A7FF-CORE51PXV repair",
    }
    authorization = {
        "authorized": {"A7FF-CORE51PXE company-machine sharded replay execution": decision.startswith("PASS_")},
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    checks_df.to_csv(RUNTIME / "a7ffcore51pxv_preflight_checks.csv", index=False)
    script_df.to_csv(RUNTIME / "a7ffcore51pxv_script_compile_audit.csv", index=False)
    write_json(RUNTIME / "a7ffcore51pxv_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore51pxv_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE51PXV COMPANY EXECUTION PREFLIGHT VALIDATOR",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE51PXV validates the company-machine replay execution package. It does not execute replay/search/proof.",
        "",
        "## Checks",
        "",
        md_table(checks_df, 100),
        "",
        "## Script Compile Audit",
        "",
        md_table(script_df, 100),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
