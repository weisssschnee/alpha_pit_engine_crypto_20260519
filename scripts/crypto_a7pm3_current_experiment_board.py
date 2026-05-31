from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7pm3_experiment_board"
REPORT = REPO / "reports" / "CRYPTO_A7PM3_CURRENT_EXPERIMENT_BOARD_20260529.md"
A7PM0 = REPO / "runtime" / "a7pm0_source_of_truth_registry" / "a7pm0_manifest.json"
A7PM2 = REPO / "runtime" / "a7pm2_candidate_lifecycle" / "a7pm2_manifest.json"
A7FF52E = REPO / "runtime" / "a7ff52e_materialization_preflight" / "a7ff52e_manifest.json"
A7FF53 = REPO / "runtime" / "a7ff53_numeric_response_contract" / "a7ff53_manifest.json"
A7FF53E_S00 = REPO / "runtime" / "a7ff53e_numeric_response_execution_s00" / "a7ff53e_s00_manifest.json"
A7FF53E = REPO / "runtime" / "a7ff53e_numeric_response_summary" / "a7ff53e_manifest.json"
A7FF54 = REPO / "runtime" / "a7ff54_numeric_clue_consolidation" / "a7ff54_manifest.json"
A7FF55 = REPO / "runtime" / "a7ff55_selector_repair_contract" / "a7ff55_manifest.json"
A7FF55D = REPO / "runtime" / "a7ff55d_selector_repair_partial_dryrun" / "a7ff55d_manifest.json"
A7FF55F = REPO / "runtime" / "a7ff55f_full_primary_input_rebuild" / "a7ff55f_manifest.json"
A7FF55R = REPO / "runtime" / "a7ff55r_selector_field_family_repair_contract" / "a7ff55r_manifest.json"
A7FF55R1 = REPO / "runtime" / "a7ff55r1_supplemental_queue_feasibility" / "a7ff55r1_manifest.json"
A7FF55R2 = REPO / "runtime" / "a7ff55r2_atlas_field_family_generation_repair" / "a7ff55r2_manifest.json"
A7FF55R3 = REPO / "runtime" / "a7ff55r3_repaired_atlas_dry_generation" / "a7ff55r3_manifest.json"
A7FF55R4 = REPO / "runtime" / "a7ff55r4_repaired_atlas_coverage_audit" / "a7ff55r4_manifest.json"


BASE_BLOCKED = {
    "A7FF-24R4E execution": "pending explicit heavy-execution authorization; A7FF-24R4 contract is ready but numeric wave execution is not started",
    "A7FF-51 execution": "not authorized by A7FF-R11; only contract drafting is allowed",
    "A7FF-50": "not authorized by A7FF-49; no non-reference non-L5 candidates exist in current maps",
    "A7FF-48": "not authorized by A7FF-47; frozen clues fail non-L5 label translation",
    "A7FF-45 continuation": "bounded replay passed but is superseded by A7FF-47 L5-only translation hold",
    "A7FF-43 deep forensic": "not authorized by A7FF-42; selected control-strict non-L7 evidence remains single-family",
    "A7FF-41 control-strict expansion": "not authorized by A7FF-40; selected control-strict non-L7 evidence remains single-family",
    "A7FF search execution": "numeric wave has clues but still no replay/search authorization",
    "A7AL-2Y generation": "not authorized",
    "A7AL-3 large search": "not authorized",
    "direct OI-price rerun": "superseded weak prior / not authorized",
    "A7AL-2Q": "not authorized by A7AL-2X0",
    "alpha proof": "not authorized",
    "shadow/paper/live": "not authorized",
}


def board_state() -> tuple[dict[str, str], dict[str, str], pd.DataFrame]:
    a7ff52e = read_json(A7FF52E)
    a7ff53 = read_json(A7FF53)
    a7ff53e_s00 = read_json(A7FF53E_S00)
    a7ff53e = read_json(A7FF53E)
    a7ff54 = read_json(A7FF54)
    a7ff55 = read_json(A7FF55)
    a7ff55d = read_json(A7FF55D)
    a7ff55f = read_json(A7FF55F)
    a7ff55r = read_json(A7FF55R)
    a7ff55r1 = read_json(A7FF55R1)
    a7ff55r2 = read_json(A7FF55R2)
    a7ff55r3 = read_json(A7FF55R3)
    a7ff55r4 = read_json(A7FF55R4)
    allowed = {
        "A7FF-24R4E repaired numeric wave execution option": "requires explicit user authorization; no search and no promotion",
        "A7PM-0/3 maintenance": "governance registry maintenance",
    }
    blocked = dict(BASE_BLOCKED)
    if a7ff55r4.get("decision") == "PASS_A7FF55R4_REPAIRED_ATLAS_COVERAGE_READY_FOR_NUMERIC_CONTRACT":
        allowed["A7FF-55R5 repaired atlas numeric contract"] = (
            "contract drafting only; define bounded primary-label numeric run over repaired 2400-row queue; no numeric/replay/search execution"
        )
        blocked["A7FF-55R4 direct numeric execution"] = "blocked: coverage audit authorizes numeric contract only, not execution"
        blocked["A7FF-56 replay-preflight contract"] = "blocked until repaired atlas numeric response selector queue passes"
        current_stage = "A7FF-55R4"
        status = "repaired_atlas_coverage_ready_for_numeric_contract"
        next_task = "A7FF-55R5 repaired atlas numeric contract"
    elif a7ff55r3.get("decision") == "PASS_A7FF55R3_REPAIRED_ATLAS_DRY_GENERATION_READY_FOR_COVERAGE_AUDIT":
        allowed["A7FF-55R4 repaired atlas coverage audit"] = (
            "coverage audit only; verify repaired 2400-row queue family/motif/base-field balance before numeric execution"
        )
        blocked["A7FF-55R3 direct numeric execution"] = "blocked: dry generation only authorizes coverage audit, not numeric execution"
        blocked["A7FF-56 replay-preflight contract"] = "blocked until repaired atlas numeric response selector queue passes"
        current_stage = "A7FF-55R3"
        status = "repaired_atlas_dry_generation_ready_for_coverage_audit"
        next_task = "A7FF-55R4 repaired atlas coverage audit"
    elif a7ff55r2.get("decision") == "PASS_A7FF55R2_ATLAS_FIELD_FAMILY_GENERATION_REPAIR_READY_NO_GENERATION_EXEC":
        allowed["A7FF-55R3 repaired atlas dry generation"] = (
            "dry generation only; use repaired open_interest/taker-flow/liquidity seed and pair previews; no numeric/replay/search/promotion"
        )
        blocked["A7FF-55R1 supplemental numeric execution"] = "blocked until repaired atlas dry generation and coverage audit pass"
        blocked["A7FF-56 replay-preflight contract"] = "blocked until repaired atlas numeric response selector queue passes"
        current_stage = "A7FF-55R2"
        status = "atlas_field_family_generation_repair_ready_no_generation_exec"
        next_task = "A7FF-55R3 repaired atlas dry generation"
    elif a7ff55r1.get("decision") == "HOLD_A7FF55R1_SUPPLEMENTAL_QUEUE_ATLAS_COVERAGE_FAIL":
        allowed["A7FF-55R2 atlas field-family generation repair"] = (
            "contract/implementation repair only; add missing open_interest/taker-flow families and materializable liquidity queue before numeric execution"
        )
        blocked["A7FF-55R1 supplemental numeric execution"] = "blocked: current atlas lacks open_interest/taker-flow formulas and liquidity materialization coverage"
        blocked["A7FF-56 replay-preflight contract"] = "blocked: A7FF-55R1 atlas coverage fail"
        current_stage = "A7FF-55R1"
        status = "supplemental_queue_atlas_coverage_fail"
        next_task = "A7FF-55R2 atlas field-family generation repair"
    elif a7ff55r.get("decision") == "PASS_A7FF55R_SELECTOR_FIELD_FAMILY_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH":
        allowed["A7FF-55R1 family-diverse supplemental primary-label input generation"] = (
            "requires explicit heavy execution; over-sample open_interest/positioning/liquidity/volatility/taker-flow primary-label inputs; no replay/search/promotion"
        )
        blocked["A7FF-56 replay-preflight contract"] = "blocked: A7FF-55F selected queue still family/motif/label concentrated"
        blocked["A7FF-55F selected queue replay"] = "blocked: selector dryrun did not pass concentration caps"
        current_stage = "A7FF-55R"
        status = "selector_field_family_repair_contract_ready_no_execution"
        next_task = "A7FF-55R1 family-diverse supplemental primary-label input generation if explicitly authorized"
    elif a7ff55f.get("decision") == "HOLD_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_REPAIR_REQUIRED":
        allowed["A7FF-55R selector / field-family repair contract"] = (
            "contract drafting only; repair family/motif/top-label concentration before any replay preflight"
        )
        blocked["A7FF-56 replay-preflight contract"] = "blocked: A7FF-55F selected queue still family/motif/label concentrated"
        current_stage = "A7FF-55F"
        status = "full_primary_selector_input_hold_repair_required"
        next_task = "A7FF-55R selector / field-family repair contract"
    elif a7ff55f.get("decision") == "PASS_A7FF55F_FULL_PRIMARY_SELECTOR_INPUT_READY_NO_REPLAY_AUTH":
        allowed["A7FF-56 replay-preflight contract"] = (
            "contract drafting only; A7FF-55F selected queue passed primary-label and diversity caps; no replay/search/promotion"
        )
        blocked["A7FF-55F direct replay"] = "blocked: A7FF-55F authorizes contract only, not replay execution"
        current_stage = "A7FF-55F"
        status = "full_primary_selector_input_ready_no_replay"
        next_task = "A7FF-56 replay-preflight contract"
    elif a7ff55d.get("decision") == "HOLD_A7FF55D_PARTIAL_SELECTOR_DRYRUN_REQUIRES_FULL_INPUT_REBUILD":
        allowed["A7FF-55F full primary-label input rebuild"] = (
            "requires heavy execution; rebuild S02-S06 primary-label compact inputs with shard outputs; no replay/search/promotion"
        )
        blocked["A7FF-55D replay preflight"] = "blocked: partial dryrun still family/motif concentrated and is not full-scope"
        current_stage = "A7FF-55D"
        status = "partial_selector_dryrun_hold_full_input_rebuild_required"
        next_task = "A7FF-55F full primary-label input rebuild"
    elif a7ff55.get("decision") == "PASS_A7FF55_SELECTOR_REPAIR_CONTRACT_READY_NO_EXECUTION_AUTH":
        allowed["A7FF-55D selector input rebuild / dryrun option"] = (
            "requires explicit execution; rebuild primary-label response compact and dryrun selector repair; no replay/search/promotion"
        )
        blocked["A7FF-54 selected queue replay"] = "blocked by A7FF-55: no L0/L1/L3 selected rows and L5/L7 absorption"
        current_stage = "A7FF-55"
        status = "selector_repair_contract_ready_no_execution"
        next_task = "A7FF-55D selector input rebuild / dryrun if explicitly authorized"
    elif a7ff54.get("decision") == "HOLD_A7FF54_SELECTED_QUEUE_LABEL_REPAIR_REQUIRED_NO_REPLAY_AUTH":
        allowed["A7FF-55 selector repair contract"] = (
            "contract drafting only; require L0/L1/L3 representation and motif caps before any replay preflight"
        )
        blocked["A7FF-54 replay preflight"] = "blocked: selected queue has no L0/L1/L3 rows and non-L7 rows are L5-only"
        current_stage = "A7FF-54"
        status = "hold_selector_label_repair_required"
        next_task = "A7FF-55 selector repair contract"
    elif a7ff53e.get("decision") == "PASS_A7FF53E_NUMERIC_RESPONSE_SHARD_SUMMARY_READY_NO_SEARCH_AUTH":
        allowed["A7FF-54 numeric clue consolidation contract"] = (
            "contract drafting only; consolidate 186 non-L7 clues and 148 selected queue rows; no replay/search/promotion"
        )
        blocked["A7FF-53E rerun"] = "numeric response summary complete; rerun only if queue or runner changes"
        current_stage = "A7FF-53E"
        status = "numeric_response_summary_pass_no_search"
        next_task = "A7FF-54 clue consolidation contract"
    elif a7ff53e_s00.get("decision") == "PASS_A7FF53ES00_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH":
        allowed["A7FF-53E remaining shard execution option"] = (
            "requires explicit heavy-task authorization; continue bounded numeric response shards or optimize runner; no replay/search/promotion"
        )
        blocked["A7FF-53E full one-shot execution"] = "current runner timed out on 1200-row one-shot; use shard execution or optimize before full run"
        current_stage = "A7FF-53E-S00"
        status = "first_numeric_shard_pass_no_search"
        next_task = "A7FF-53E remaining shards or runner optimization"
    elif a7ff53.get("decision") == "PASS_A7FF53_NUMERIC_RESPONSE_CONTRACT_READY_NO_EXECUTION_AUTH":
        allowed["A7FF-53E numeric response execution option"] = (
            "requires explicit authorization; bounded numeric response only; no replay/search/promotion"
        )
        blocked["A7FF-53 execution"] = "contract ready but numeric response execution is not started"
        blocked["A7FF-52E rerun"] = "already executed; rerun only if A7FF-51E pool or evaluator changes"
        current_stage = "A7FF-53"
        status = "numeric_response_contract_ready_no_execution"
        next_task = "A7FF-53E if explicitly authorized"
    elif a7ff52e.get("decision") == "PASS_A7FF52E_MATERIALIZATION_PREFLIGHT_READY_FOR_NUMERIC_CONTRACT":
        allowed["A7FF-53 numeric response contract"] = (
            "contract drafting only; use A7FF-52E materialization metrics; no numeric execution/search"
        )
        blocked["A7FF-52E rerun"] = "already executed; rerun only if A7FF-51E pool or evaluator changes"
        current_stage = "A7FF-52E"
        status = "materialization_preflight_pass_no_numeric"
        next_task = "A7FF-53 numeric response contract"
    else:
        allowed["A7FF-52E materialization preflight execution option"] = (
            "requires explicit authorization; 1200 family-balanced rows; no numeric replay/search"
        )
        blocked["A7FF-52E execution"] = (
            "pending explicit materialization-preflight authorization; A7FF-52 contract is ready but materialization is not started"
        )
        current_stage = "A7FF-52"
        status = "contract_ready_no_materialization"
        next_task = "A7FF-52E if explicitly authorized"
    active = pd.DataFrame(
        [
            {"workstream": "governance", "current_stage": "A7PM-0/1/2/3", "status": "pass", "next": "keep registry as source-of-truth"},
            {"workstream": "a7ff_family_diversification", "current_stage": current_stage, "status": status, "next": next_task},
            {"workstream": "a7ff_funding_tail", "current_stage": "A7FF-24R4", "status": "contract_ready_no_execution", "next": "A7FF-24R4E if explicitly authorized"},
            {"workstream": "search_execution", "current_stage": "blocked", "status": "not_authorized", "next": "none"},
        ]
    )
    return allowed, blocked, active


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    pm0 = read_json(A7PM0)
    pm2 = read_json(A7PM2)
    if not pm0.get("authorizes_a7pm3") and not pm2.get("authorizes_a7pm3"):
        raise SystemExit("A7PM source stages do not authorize A7PM-3")

    allowed, blocked, active = board_state()
    manifest = {
        "stage": "A7PM-3",
        "generated_at": now_utc(),
        "decision": "PASS_A7PM3_CURRENT_EXPERIMENT_BOARD_BUILT",
        "executes_search": False,
        "executes_replay": False,
        "executes_training": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "allowed_next_task_count": len(allowed),
        "blocked_task_count": len(blocked),
    }
    write_json(RUNTIME / "a7pm3_allowed_next_tasks.json", allowed)
    write_json(RUNTIME / "a7pm3_blocked_tasks.json", blocked)
    active.to_csv(RUNTIME / "a7pm3_active_workstreams.csv", index=False)
    write_json(
        RUNTIME / "a7pm3_latest_source_of_truth.json",
        {"a7pm0": pm0, "a7pm2": pm2, "head_equals_origin_main": pm0.get("head_equals_origin_main")},
    )
    write_json(RUNTIME / "a7pm3_manifest.json", manifest)
    allowed_df = pd.DataFrame([{"task": k, "reason": v} for k, v in allowed.items()])
    blocked_df = pd.DataFrame([{"task": k, "reason": v} for k, v in blocked.items()])
    lines = [
        "# CRYPTO A7PM-3 CURRENT EXPERIMENT BOARD",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "## Active Workstreams",
        "",
        md_table(active),
        "",
        "## Allowed Next Tasks",
        "",
        md_table(allowed_df),
        "",
        "## Blocked Tasks",
        "",
        md_table(blocked_df),
        "",
        "## Boundary",
        "",
        "```text",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "A7FF-52E materialization is complete if present in the source-of-truth registry. Next A7FF step is contract-only unless explicitly authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
