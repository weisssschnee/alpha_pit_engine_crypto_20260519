from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff28_deep_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF28_DEEP_REPLAY_CONTRACT_20260530.md"
A7FF27 = REPO / "runtime" / "a7ff27_replay_preflight"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


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
        return "```text\n" + view.to_string(index=False) + "\n```"


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    prior = read_json(A7FF27 / "a7ff27_summary_manifest.json")
    queue = read_csv(A7FF27 / "a7ff27_a7ff28_preflight_queue.csv")
    selected_summary = read_csv(A7FF27 / "a7ff27_candidate_replay_preflight_summary.csv")

    required_cols = {
        "blueprint_id",
        "expression",
        "semantic_pair",
        "motif",
        "label_family",
        "label_horizon_h",
        "control_ratio_premay_max",
        "score_no_may",
        "skeleton_key",
        "finite_share",
        "nonzero_share",
    }
    missing_cols = sorted(required_cols - set(queue.columns))
    selected_count = int(len(queue))
    semantic_pair_count = int(queue["semantic_pair"].nunique()) if "semantic_pair" in queue else 0
    skeleton_count = int(queue["skeleton_key"].nunique()) if "skeleton_key" in queue else 0
    control_max = float(pd.to_numeric(queue.get("control_ratio_premay_max", pd.Series(dtype=float)), errors="coerce").max()) if selected_count else None
    non_l7_count = int(queue["label_family"].ne("L7_ranked_future_return").sum()) if "label_family" in queue else 0
    warnings: list[str] = []
    if missing_cols:
        warnings.append("missing_required_queue_columns")
    if selected_count < 4:
        warnings.append("selected_count_lt_4")
    if semantic_pair_count < 3:
        warnings.append("semantic_pair_count_lt_3")
    if skeleton_count < selected_count:
        warnings.append("some_skeleton_reuse")
    if control_max is not None and control_max >= 1.0:
        warnings.append("control_ratio_hard_gate_violation")
    if non_l7_count != selected_count:
        warnings.append("rank_label_rows_present_in_deep_replay_queue")

    contract = pd.DataFrame(
        [
            {
                "gate": "source_of_truth",
                "rule": "input queue is runtime/a7ff27_replay_preflight/a7ff27_a7ff28_preflight_queue.csv",
                "hard": True,
            },
            {
                "gate": "no_generation",
                "rule": "A7FF-28 may not generate or mutate formulas",
                "hard": True,
            },
            {
                "gate": "no_search_authorization",
                "rule": "A7FF-28 is replay contract/preflight only",
                "hard": True,
            },
            {
                "gate": "full_symbol_replay",
                "rule": "deep replay must evaluate selected formulas on strict_full_history symbols and report listing-aware diagnostics separately",
                "hard": True,
            },
            {
                "gate": "label_family_balance",
                "rule": "non-L7 labels are required for promotion; L7 remains diagnostic",
                "hard": True,
            },
            {
                "gate": "control_dominance",
                "rule": "control_ratio >= 1.0 is rejected; 0.80-1.00 remains warning/diagnostic",
                "hard": True,
            },
            {
                "gate": "portfolio_proxy",
                "rule": "report equal-weight and liquidity-capped proxy, turnover, cost2/5/10, symbol/month/state concentration",
                "hard": True,
            },
            {
                "gate": "stress_policy",
                "rule": "May/stress may only be post-selection veto/failure attribution, never selector score",
                "hard": True,
            },
        ]
    )
    contract.to_csv(RUNTIME / "a7ff28_deep_replay_gate_contract.csv", index=False)

    execution_plan = pd.DataFrame(
        [
            {"step": "A7FF-28A", "action": "load A7FF-27 queue and freeze candidate order", "executes_search": False},
            {"step": "A7FF-28B", "action": "materialize all 8 expressions on full strict universe", "executes_search": False},
            {"step": "A7FF-28C", "action": "run split/horizon/label/control/cost replay metrics", "executes_search": False},
            {"step": "A7FF-28D", "action": "run portfolio proxy, concentration, and stress attribution", "executes_search": False},
            {"step": "A7FF-28E", "action": "decide research-clue vs diagnostic-only vs reject", "executes_search": False},
        ]
    )
    execution_plan.to_csv(RUNTIME / "a7ff28_execution_plan.csv", index=False)

    queue_out = queue.copy()
    if not queue_out.empty:
        queue_out.insert(0, "a7ff28_queue_rank", range(1, len(queue_out) + 1))
    queue_out.to_csv(RUNTIME / "a7ff28_deep_replay_queue.csv", index=False)

    family_summary = (
        queue.groupby(["semantic_pair", "motif", "label_family"], dropna=False)
        .agg(
            candidate_count=("blueprint_id", "count"),
            skeleton_count=("skeleton_key", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            median_score_no_may=("score_no_may", "median"),
        )
        .reset_index()
        if not queue.empty
        else pd.DataFrame()
    )
    family_summary.to_csv(RUNTIME / "a7ff28_queue_family_summary.csv", index=False)

    decision = (
        "PASS_A7FF28_DEEP_REPLAY_CONTRACT_READY_NO_SEARCH_AUTH"
        if not missing_cols and selected_count >= 4 and semantic_pair_count >= 3 and (control_max is None or control_max < 1.0)
        else "HOLD_A7FF28_DEEP_REPLAY_CONTRACT_QUEUE_NOT_READY"
    )
    manifest = {
        "stage": "A7FF-28",
        "generated_at": now_utc(),
        "decision": decision,
        "prior_stage": prior.get("stage", "A7FF-27"),
        "prior_decision": prior.get("decision", ""),
        "input_queue_count": selected_count,
        "semantic_pair_count": semantic_pair_count,
        "skeleton_count": skeleton_count,
        "non_l7_count": non_l7_count,
        "max_control_ratio": control_max,
        "missing_required_columns": missing_cols,
        "warnings": warnings,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_deep_replay_execution": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff28_manifest.json", manifest)
    write_json(RUNTIME / "a7ff28_authorization_matrix.json", manifest)

    lines = [
        "# CRYPTO A7FF-28 DEEP REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-28 freezes the A7FF-27 selected preflight queue and defines the next deep replay gates. It does not run replay, generate formulas, execute search, or prove alpha.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Queue",
        "",
        md_table(queue_out[["a7ff28_queue_rank", "blueprint_id", "expression", "semantic_pair", "motif", "label_family", "label_horizon_h", "control_ratio_premay_max", "score_no_may", "skeleton_key"]] if not queue_out.empty else queue_out, 20),
        "",
        "## Family Summary",
        "",
        md_table(family_summary, 40),
        "",
        "## Deep Replay Gate Contract",
        "",
        md_table(contract, 20),
        "",
        "## Execution Plan",
        "",
        md_table(execution_plan, 20),
        "",
        "## A7FF-27 Candidate Summary",
        "",
        md_table(selected_summary, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "A7FF-28 authorizes only bounded deep replay execution for the frozen 8-candidate queue.",
        "It does not authorize formula generation, large search, alpha proof, shadow, paper, or live execution.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
