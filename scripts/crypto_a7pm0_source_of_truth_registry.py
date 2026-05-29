from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7pm0_source_of_truth_registry"
REPORT = REPO / "reports" / "CRYPTO_A7PM0_SOURCE_OF_TRUTH_REGISTRY_20260529.md"


BLOCKED_TASKS = {
    "A7AL-2Q": "superseded/not_authorized by A7AL-2X0",
    "A7AL-2Y": "formula generation/search execution not authorized",
    "A7AL-3": "large search not authorized",
    "direct_OI_price_rerun": "same objective rerun not authorized",
    "formula_search": "not authorized",
    "large_search": "not authorized",
    "alpha_proof": "not authorized",
    "shadow_paper_live": "not authorized",
}

NEXT_ALLOWED_TASKS = {
    "A7PM-1": "asset taxonomy and modularization plan",
    "A7PM-2": "candidate lifecycle state machine",
    "A7PM-3": "current experiment board",
    "A7AI-F2": "end-to-end field enforcement regression audit",
    "A7AI-F3": "materialization/evaluator parity sprint",
    "A7AA": "primitive response / label adequacy continuation",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True, encoding="utf-8", errors="replace")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO)).replace("\\", "/")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


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


def normalize_stage_id(text: str) -> str:
    token = text.strip()
    token = re.sub(r"^CRYPTO_", "", token, flags=re.IGNORECASE)
    token = re.sub(r"_20\d{6}.*$", "", token)
    token = token.replace("_", "-")
    token = re.sub(r"-+", "-", token)
    return token.upper()


def stage_from_runtime_dir(path: Path) -> str:
    name = path.name
    m = re.match(r"^(a7[a-z0-9]+)", name, flags=re.IGNORECASE)
    if not m:
        return normalize_stage_id(name)
    token = m.group(1).upper()
    token = token.replace("A7AIF", "A7AI-F")
    token = token.replace("A7PM", "A7PM-")
    token = token.replace("A7AL2", "A7AL-2")
    token = token.replace("A7AR", "A7AR-")
    token = token.replace("A7AA", "A7AA-")
    token = token.replace("A7AH", "A7AH-")
    token = token.replace("A7AG", "A7AG-")
    token = token.replace("A7AC", "A7AC-")
    token = token.replace("A7AB", "A7AB-")
    token = token.replace("A7AD", "A7AD-")
    token = token.replace("A7AE", "A7AE-")
    return token


def bool_authorized(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        upper = value.upper()
        return "AUTHORIZED" in upper and "NOT_AUTHORIZED" not in upper and "FALSE" not in upper
    if isinstance(value, dict):
        if "authorized" in value:
            return bool_authorized(value.get("authorized"))
        if "status" in value:
            return bool_authorized(value.get("status"))
    return False


def collect_authorization(payload: dict[str, Any], auth_payloads: list[dict[str, Any]]) -> dict[str, bool]:
    keys = {
        "contract": False,
        "execution": False,
        "search": False,
        "alpha_proof": False,
        "shadow_paper_live": False,
    }
    for key, value in payload.items():
        lower = str(key).lower()
        if "authorize" not in lower and "authorizes" not in lower:
            continue
        authorized = bool_authorized(value)
        if "contract" in lower or "next" in lower or "a7" in lower:
            keys["contract"] = keys["contract"] or authorized
        if "execution" in lower or "replay" in lower:
            keys["execution"] = keys["execution"] or authorized
        if (
            "large_search" in lower
            or lower.endswith("formula_search")
            or "formula_search_execution" in lower
            or lower.endswith("search_execution")
        ):
            keys["search"] = keys["search"] or authorized
        if "alpha_proof" in lower or "alpha proof" in lower:
            keys["alpha_proof"] = keys["alpha_proof"] or authorized
        if "shadow" in lower or "paper" in lower or "live" in lower:
            keys["shadow_paper_live"] = keys["shadow_paper_live"] or authorized
    for auth in auth_payloads:
        for key, value in auth.items():
            lower = str(key).lower()
            authorized = bool_authorized(value)
            if "contract" in lower or lower.startswith("a7"):
                keys["contract"] = keys["contract"] or authorized
            if "execution" in lower or "replay" in lower:
                keys["execution"] = keys["execution"] or authorized
            if (
                "large_search" in lower
                or lower.endswith("formula_search")
                or "formula_search_execution" in lower
                or lower.endswith("search_execution")
            ):
                keys["search"] = keys["search"] or authorized
            if "alpha_proof" in lower or "alpha proof" in lower:
                keys["alpha_proof"] = keys["alpha_proof"] or authorized
            if "shadow" in lower or "paper" in lower or "live" in lower:
                keys["shadow_paper_live"] = keys["shadow_paper_live"] or authorized
    return keys


def build_commit_map() -> dict[str, dict[str, str]]:
    output = run_git(["log", "--name-only", "--pretty=format:@@@%H\t%h\t%s"])
    commit: dict[str, str] = {}
    mapping: dict[str, dict[str, str]] = {}
    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("@@@"):
            parts = line[3:].split("\t", 2)
            commit = {"commit": parts[0], "short_commit": parts[1], "subject": parts[2] if len(parts) > 2 else ""}
            continue
        if commit and line not in mapping:
            mapping[line.replace("\\", "/")] = dict(commit)
    return mapping


def find_reports() -> list[Path]:
    return sorted((REPO / "reports").glob("CRYPTO_A7*.md"))


def report_stage_id(path: Path) -> str:
    return normalize_stage_id(path.stem)


def infer_evidence_level(decision: str, stage_id: str) -> str:
    upper = (decision or "").upper()
    if "ALPHA" in upper and "NOT" not in upper:
        return "alpha_claim_check_required"
    if "SMOKE" in upper:
        return "smoke"
    if "CONTRACT" in upper:
        return "contract"
    if "FORENSIC" in upper or "DIAGNOSTIC" in upper:
        return "diagnostic"
    if "HOLD" in upper:
        return "hold"
    if stage_id.startswith("A7AL-2Z"):
        return "diagnostic"
    return "governance_or_audit"


def apply_special_status(row: dict[str, Any]) -> dict[str, Any]:
    stage = str(row["stage_id"]).upper()
    decision = str(row.get("decision", "")).upper()
    row["supersedes"] = ""
    row["superseded_by"] = ""
    notes: list[str] = []

    if stage in {"A7AL-2P2", "A7AL2P2"} or "A7AL2P2" in stage:
        row["current_status"] = "superseded_diagnostic"
        row["superseded_by"] = "A7AL-2X0"
        notes.append("A7AL-2P2 superseded by A7AL-2X0 arbitration")
    elif stage in {"A7AL-2Q", "A7AL2Q"} or "A7AL2Q" in stage:
        row["current_status"] = "not_authorized"
        row["superseded_by"] = "A7AL-2X0"
        notes.append("A7AL-2Q local execution not authorized")
    elif stage.startswith("A7AL-2Z"):
        row["current_status"] = "engineering_pass_signal_hold"
        notes.append("Z-series frozen as engineering diagnostics with signal hold")
    elif stage in {"A7AI-F0", "A7AI-F1"}:
        row["current_status"] = "current_valid_governance"
        notes.append("A7AI field enforcement is synced to origin/main")
    elif "HOLD" in decision:
        row["current_status"] = "hold"
    elif row.get("authorizes_search") or row.get("authorizes_alpha_proof") or row.get("authorizes_shadow_paper_live"):
        row["current_status"] = "authorization_conflict_review"
        notes.append("search/proof/live authorization requires manual review")
    else:
        row["current_status"] = row.get("current_status") or "valid_or_historical_record"
    row["notes"] = "; ".join(notes)
    return row


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    commit_map = build_commit_map()
    runtime_dirs = sorted([path for path in (REPO / "runtime").iterdir() if path.is_dir()])
    reports = find_reports()
    reports_by_stage: dict[str, list[str]] = {}
    for report in reports:
        reports_by_stage.setdefault(report_stage_id(report), []).append(rel(report))

    stage_rows: list[dict[str, Any]] = []
    artifact_rows: list[dict[str, Any]] = []
    auth_rows: list[dict[str, Any]] = []

    for report in reports:
        r = rel(report)
        info = commit_map.get(r, {})
        artifact_rows.append(
            {
                "artifact_type": "report",
                "stage_id": report_stage_id(report),
                "path": r,
                "commit": info.get("short_commit", ""),
                "commit_subject": info.get("subject", ""),
                "bytes": report.stat().st_size,
            }
        )

    for runtime_dir in runtime_dirs:
        stage_id = stage_from_runtime_dir(runtime_dir)
        files = sorted([path for path in runtime_dir.rglob("*") if path.is_file()])
        manifest_files = [p for p in files if "manifest" in p.name.lower() and p.suffix.lower() == ".json"]
        decision_files = [p for p in files if "decision" in p.name.lower() and p.suffix.lower() == ".json"]
        auth_files = [p for p in files if "authorization" in p.name.lower() and p.suffix.lower() == ".json"]
        payload: dict[str, Any] = {}
        manifest_path = ""
        if manifest_files:
            manifest_path = rel(manifest_files[0])
            payload = read_json(manifest_files[0])
            if payload.get("stage"):
                stage_id = str(payload["stage"]).upper()
        decisions = [read_json(path) for path in decision_files]
        auth_payloads = [read_json(path) for path in auth_files]
        decision = str(payload.get("decision") or "")
        if not decision:
            for candidate in decisions + auth_payloads:
                decision = str(candidate.get("decision") or candidate.get("status") or "")
                if decision:
                    break
        if not decision:
            decision = "NO_DECISION_FIELD"
        auth = collect_authorization(payload, auth_payloads)
        runtime_rel = rel(runtime_dir)
        primary_report = ""
        stage_norm = stage_id.replace("-", "")
        for report_stage, paths in reports_by_stage.items():
            if stage_norm in report_stage.replace("-", "") or report_stage.replace("-", "") in stage_norm:
                primary_report = paths[0]
                break
        commit_info = commit_map.get(primary_report) or commit_map.get(manifest_path) or commit_map.get(runtime_rel, {})
        row = {
            "stage_id": stage_id,
            "commit": commit_info.get("short_commit", ""),
            "report_path": primary_report,
            "runtime_path": runtime_rel,
            "manifest_path": manifest_path,
            "decision": decision,
            "evidence_level": infer_evidence_level(decision, stage_id),
            "authorizes_contract": auth["contract"],
            "authorizes_execution": auth["execution"],
            "authorizes_search": auth["search"],
            "authorizes_alpha_proof": auth["alpha_proof"],
            "authorizes_shadow_paper_live": auth["shadow_paper_live"],
            "supersedes": "",
            "superseded_by": "",
            "current_status": "",
            "notes": "",
            "artifact_count": len(files),
        }
        row = apply_special_status(row)
        stage_rows.append(row)

        for file_path in files:
            r = rel(file_path)
            info = commit_map.get(r, {})
            artifact_rows.append(
                {
                    "artifact_type": "runtime",
                    "stage_id": stage_id,
                    "path": r,
                    "commit": info.get("short_commit", ""),
                    "commit_subject": info.get("subject", ""),
                    "bytes": file_path.stat().st_size,
                }
            )
        for auth_path, auth_payload in zip(auth_files, auth_payloads):
            for key, value in auth_payload.items():
                auth_rows.append(
                    {
                        "stage_id": stage_id,
                        "authorization_path": rel(auth_path),
                        "authorization_key": key,
                        "authorization_value": json.dumps(value, sort_keys=True),
                        "authorized_bool": bool_authorized(value),
                    }
                )

    stage_df = pd.DataFrame(stage_rows).sort_values(["stage_id", "runtime_path"])
    artifact_df = pd.DataFrame(artifact_rows).sort_values(["stage_id", "artifact_type", "path"])
    auth_df = pd.DataFrame(auth_rows).sort_values(["stage_id", "authorization_path", "authorization_key"])
    supersession_df = stage_df.loc[
        stage_df["superseded_by"].astype(str).ne("") | stage_df["supersedes"].astype(str).ne(""),
        ["stage_id", "supersedes", "superseded_by", "current_status", "notes"],
    ].copy()
    conflict_df = stage_df[
        stage_df["current_status"].eq("authorization_conflict_review")
        | stage_df["authorizes_search"]
        | stage_df["authorizes_alpha_proof"]
        | stage_df["authorizes_shadow_paper_live"]
    ].copy()
    current_valid = stage_df[
        stage_df["current_status"].isin(["current_valid_governance", "valid_or_historical_record", "engineering_pass_signal_hold"])
    ].copy()

    decision = "PASS_A7PM0_SOURCE_OF_TRUTH_REGISTRY_BUILT"
    blockers: list[str] = []
    if not conflict_df.empty:
        blockers.append("authorization_conflict_review_rows_present")
        decision = "HOLD_A7PM0_AUTHORIZATION_CONFLICT"
    if stage_df.empty:
        blockers.append("missing_stage_records")
        decision = "HOLD_A7PM0_MISSING_CURRENT_SOURCE_OF_TRUTH"

    head = run_git(["rev-parse", "HEAD"]).strip()
    origin = run_git(["rev-parse", "origin/main"]).strip()
    status = run_git(["status", "--short", "--branch"]).strip()
    manifest = {
        "stage": "A7PM-0",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "head": head,
        "origin_main": origin,
        "head_equals_origin_main": head == origin,
        "stage_count": int(len(stage_df)),
        "artifact_count": int(len(artifact_df)),
        "authorization_record_count": int(len(auth_df)),
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_a7pm1": decision.startswith("PASS_"),
        "authorizes_a7pm2": decision.startswith("PASS_"),
        "authorizes_a7pm3": decision.startswith("PASS_"),
    }

    stage_df.to_csv(RUNTIME / "a7pm0_stage_registry.csv", index=False)
    artifact_df.to_csv(RUNTIME / "a7pm0_artifact_registry.csv", index=False)
    auth_df.to_csv(RUNTIME / "a7pm0_authorization_matrix.csv", index=False)
    supersession_df.to_csv(RUNTIME / "a7pm0_supersession_map.csv", index=False)
    write_json(RUNTIME / "a7pm0_current_valid_records.json", current_valid.to_dict("records"))
    write_json(RUNTIME / "a7pm0_blocked_tasks.json", BLOCKED_TASKS)
    write_json(RUNTIME / "a7pm0_next_allowed_tasks.json", NEXT_ALLOWED_TASKS)
    write_json(RUNTIME / "a7pm0_manifest.json", manifest)

    status_summary = (
        stage_df.groupby(["current_status", "evidence_level"], dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values(["current_status", "count"], ascending=[True, False])
    )
    lines = [
        "# CRYPTO A7PM-0 SOURCE OF TRUTH REGISTRY",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7PM-0 builds a machine-readable registry from reports, runtime manifests, authorization records, and git history. It does not run search, replay, training, or proof.",
        "",
        "## Git State",
        "",
        "```text",
        status,
        f"HEAD={head}",
        f"origin/main={origin}",
        f"HEAD == origin/main: {head == origin}",
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Current Status Summary",
        "",
        md_table(status_summary, 120),
        "",
        "## Supersession Map",
        "",
        md_table(supersession_df, 80),
        "",
        "## Blocked Tasks",
        "",
        "```json",
        json.dumps(BLOCKED_TASKS, indent=2, sort_keys=True),
        "```",
        "",
        "## Next Allowed Tasks",
        "",
        "```json",
        json.dumps(NEXT_ALLOWED_TASKS, indent=2, sort_keys=True),
        "```",
        "",
        "## Boundary",
        "",
        "```text",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "A7AL-2P2 is superseded diagnostic; A7AL-2Q is not authorized.",
        "A7AL-2Z0-Z9 are engineering diagnostics with signal hold.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
