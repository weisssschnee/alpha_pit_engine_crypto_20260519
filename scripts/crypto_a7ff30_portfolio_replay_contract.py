from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ff30_portfolio_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FF30_PORTFOLIO_REPLAY_CONTRACT_20260530.md"
A7FF29 = REPO / "runtime" / "a7ff29_candidate_forensic"


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

    prior = read_json(A7FF29 / "a7ff29_manifest.json")
    if not prior.get("authorizes_a7ff30_portfolio_replay_contract"):
        raise SystemExit("A7FF-29 does not authorize A7FF-30")
    queue = read_csv(A7FF29 / "a7ff29_a7ff30_portfolio_replay_contract_queue.csv")
    forensic = read_csv(A7FF29 / "a7ff29_candidate_forensic_summary.csv")

    replay_modes = pd.DataFrame(
        [
            {
                "mode": "equal_weight_top_bottom",
                "description": "rank signal cross-sectionally each hour; long top bucket, short bottom bucket; equal symbol weights",
                "required_outputs": "gross/net spread; turnover; cost2/5/10; symbol/month/state concentration",
            },
            {
                "mode": "liquidity_capped_top_bottom",
                "description": "same as equal-weight but cap symbol weights by liquidity tier and active universe size",
                "required_outputs": "gross/net spread; liquidity-cap hit rate; top weight concentration",
            },
            {
                "mode": "candidate_ensemble_equal",
                "description": "average normalized ranks across the 6 frozen candidates; no learned weights",
                "required_outputs": "ensemble gross/net spread; candidate marginal contribution; candidate correlation",
            },
            {
                "mode": "candidate_leave_one_out",
                "description": "remove one candidate at a time from ensemble to estimate marginal contribution",
                "required_outputs": "delta net spread; delta tstat; concentration change",
            },
        ]
    )
    replay_modes.to_csv(RUNTIME / "a7ff30_replay_modes.csv", index=False)

    gates = pd.DataFrame(
        [
            {"gate": "frozen_queue_only", "rule": "input must be runtime/a7ff29_candidate_forensic/a7ff29_a7ff30_portfolio_replay_contract_queue.csv", "hard": True},
            {"gate": "no_weight_learning", "rule": "no trained weights; equal candidate ensemble only", "hard": True},
            {"gate": "non_l7_only", "rule": "ranked-return diagnostic rows are excluded", "hard": True},
            {"gate": "control_clean", "rule": "reject any candidate with max_control_ratio >= 1.0; warn >= 0.8", "hard": True},
            {"gate": "cost_stress", "rule": "report 2/5/10 bps net proxies; no promotion if cost2 collapses", "hard": True},
            {"gate": "concentration", "rule": "report symbol, month, semantic pair, skeleton, liquidity tier, and latent-state concentration", "hard": True},
            {"gate": "basis_premium_warning", "rule": "basis/premium-root concentration is a warning; do not generalize to broad crypto alpha", "hard": True},
            {"gate": "no_may_selector", "rule": "May/stress remains post-selection attribution only", "hard": True},
        ]
    )
    gates.to_csv(RUNTIME / "a7ff30_portfolio_replay_gates.csv", index=False)

    queue_out = queue.copy()
    queue_out["portfolio_replay_allowed"] = True
    queue_out["weight_policy"] = "equal_candidate_weight_only"
    queue_out["search_allowed"] = False
    queue_out.to_csv(RUNTIME / "a7ff30_frozen_portfolio_replay_queue.csv", index=False)

    risk = pd.DataFrame(
        [
            {
                "risk": "basis_premium_root_concentration",
                "observed": bool(queue["semantic_pair"].astype(str).str.contains("basis_premium_like", regex=False).all()) if not queue.empty else False,
                "mitigation": "portfolio replay must report this as a family concentration warning",
            },
            {
                "risk": "safe_div_outlier",
                "observed": bool(queue["warning_flags"].astype(str).str.contains("safe_div_outlier_risk", regex=False).any()) if "warning_flags" in queue else False,
                "mitigation": "replay must report winsorized and raw variants side by side",
            },
            {
                "risk": "single_label_family",
                "observed": bool(queue["best_label_family"].nunique() <= 1) if "best_label_family" in queue else False,
                "mitigation": "report per-label and ensemble results; no promotion on one label only",
            },
        ]
    )
    risk.to_csv(RUNTIME / "a7ff30_risk_register.csv", index=False)

    execution_plan = pd.DataFrame(
        [
            {"step": "A7FF-30A", "action": "portfolio replay implementation smoke on frozen 6-candidate queue", "authorizes_search": False},
            {"step": "A7FF-30B", "action": "candidate ensemble and leave-one-out marginal replay", "authorizes_search": False},
            {"step": "A7FF-30C", "action": "portfolio concentration and stress attribution report", "authorizes_search": False},
        ]
    )
    execution_plan.to_csv(RUNTIME / "a7ff30_execution_plan.csv", index=False)

    warnings = prior.get("warnings", [])
    decision = (
        "PASS_A7FF30_PORTFOLIO_REPLAY_CONTRACT_READY_NO_SEARCH_AUTH"
        if len(queue) >= 4
        else "HOLD_A7FF30_PORTFOLIO_REPLAY_QUEUE_TOO_SMALL"
    )
    manifest = {
        "stage": "A7FF-30",
        "generated_at": now_utc(),
        "decision": decision,
        "prior_stage": prior.get("stage", "A7FF-29"),
        "prior_decision": prior.get("decision", ""),
        "candidate_count": int(len(queue)),
        "semantic_pair_count": int(queue["semantic_pair"].nunique()) if not queue.empty else 0,
        "warnings": warnings,
        "executes_generation": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_a7ff30a_portfolio_replay_smoke": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ff30_manifest.json", manifest)
    write_json(RUNTIME / "a7ff30_authorization_matrix.json", manifest)

    lines = [
        "# CRYPTO A7FF-30 PORTFOLIO REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7FF-30 defines portfolio replay rules for the frozen A7FF-29 six-candidate queue. It does not execute replay, generate formulas, run search, or prove alpha.",
        "",
        "## Experiment Record",
        "",
        "```text",
        "experiment_id: 20260530_a7ff30_portfolio_replay_contract",
        "objective: define a bounded portfolio replay for the six non-L7 candidates without search or learned weights",
        "input: runtime/a7ff29_candidate_forensic/a7ff29_a7ff30_portfolio_replay_contract_queue.csv",
        "parameters: equal candidate weights only; 2/5/10 bps cost stress; concentration and leave-one-out required",
        "```",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Frozen Queue",
        "",
        md_table(queue_out, 20),
        "",
        "## Replay Modes",
        "",
        md_table(replay_modes, 20),
        "",
        "## Gates",
        "",
        md_table(gates, 20),
        "",
        "## Risk Register",
        "",
        md_table(risk, 20),
        "",
        "## Prior Forensic",
        "",
        md_table(forensic, 20),
        "",
        "## Boundary",
        "",
        "```text",
        "A7FF-30 authorizes only A7FF-30A portfolio replay smoke on the frozen queue.",
        "No formula search, large search, alpha proof, shadow, paper, or live execution is authorized.",
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
