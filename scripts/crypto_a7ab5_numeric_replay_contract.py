from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ab5_numeric_replay_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AB5_NUMERIC_REPLAY_CONTRACT_20260529.md"

A7AB4_MANIFEST = REPO / "runtime" / "a7ab4_materialization_preflight" / "a7ab4_manifest.json"
A7AB4_SUMMARY = REPO / "runtime" / "a7ab4_materialization_preflight" / "a7ab4_candidate_materialization_summary.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def build_balanced_queue(summary: pd.DataFrame, target: int = 128) -> pd.DataFrame:
    ok = summary[summary["activity_ok"].astype(str).str.lower().isin(["true", "1"])].copy()
    ok = ok.sort_values(
        ["family_id", "nonzero_share", "finite_share", "candidate_id"],
        ascending=[True, False, False, True],
    )
    family_target = max(1, target // max(1, ok["family_id"].nunique()))
    selected_rows: list[dict[str, Any]] = []
    for _, fam_df in ok.groupby("family_id", sort=True):
        selected_rows.extend(fam_df.head(family_target).to_dict("records"))
    if len(selected_rows) < target:
        used = {row["candidate_id"] for row in selected_rows}
        rest = ok[~ok["candidate_id"].isin(used)].sort_values(
            ["nonzero_share", "finite_share", "candidate_id"],
            ascending=[False, False, True],
        )
        selected_rows.extend(rest.head(target - len(selected_rows)).to_dict("records"))
    queue = pd.DataFrame(selected_rows).head(target).reset_index(drop=True)
    queue.insert(0, "replay_contract_rank", range(1, len(queue) + 1))
    return queue


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    a7ab4 = read_json(A7AB4_MANIFEST)
    if not a7ab4.get("authorizes_a7ab5_numeric_replay_contract"):
        raise SystemExit("A7AB-4 does not authorize A7AB-5")
    summary = pd.read_csv(A7AB4_SUMMARY)
    queue = build_balanced_queue(summary, target=128)

    label_contract = pd.DataFrame(
        [
            {"label_family": "L7_ranked_future_return", "horizons_h": "1|4", "primary": True},
            {"label_family": "L1_cross_sectional_relative_return", "horizons_h": "1|4", "primary": False},
            {"label_family": "L0_raw_forward_return", "horizons_h": "1", "primary": False},
        ]
    )
    control_contract = pd.DataFrame(
        [
            {"control": "one_bar_lag", "required": True, "failure_if": "candidate collapses under field-native one-bar lag"},
            {"control": "wrong_lag_future_1h", "required": True, "failure_if": "control ratio >= 1.0"},
            {"control": "wrong_lag_stale_24h", "required": True, "failure_if": "control ratio >= 1.0"},
            {"control": "time_shuffle", "required": True, "failure_if": "control ratio >= 1.0"},
            {"control": "symbol_shuffle", "required": True, "failure_if": "control ratio >= 1.0"},
            {"control": "same_family_random", "required": True, "failure_if": "control ratio >= 1.0"},
        ]
    )
    pass_gates = pd.DataFrame(
        [
            {"gate": "pre_may_split_stability", "rule": "validation/test/recent oriented spread positive"},
            {"gate": "control_dominance", "rule": "matched control ratio < 1.0 in every pre-May split"},
            {"gate": "nonoverlap_stats", "rule": "24h non-overlap min/median stats reported; naive hourly tstat not sufficient"},
            {"gate": "latency", "rule": "field-native one-bar lag must survive; no artificial +2h policy"},
            {"gate": "cost_proxy", "rule": "2bps/5bps/10bps proxy reported"},
            {"gate": "diversity", "rule": "no single family > 35%, no single skeleton > 15%, no single seed field > 25%"},
            {"gate": "no_may", "rule": "May not used in score, selector, threshold, replay ranking, or mutation"},
        ]
    )
    authorization = {
        "A7AB-5": {"status": "PASS_A7AB5_NUMERIC_REPLAY_CONTRACT_READY_FOR_A7AB6_SMALL_REPLAY_PREFLIGHT"},
        "A7AB-6_small_numeric_replay_preflight": {"authorized": True},
        "numeric_replay_execution_scope": {
            "authorized": True,
            "max_candidates": 128,
            "labels": ["L7_ranked_future_return", "L1_cross_sectional_relative_return", "L0_raw_forward_return"],
            "horizons_h": [1, 4],
            "purpose": "bounded preflight only",
        },
        "formula_search_execution": {"authorized": False},
        "large_search": {"authorized": False},
        "alpha_proof": {"authorized": False},
        "shadow_paper_live": {"authorized": False},
    }
    decision = authorization["A7AB-5"]["status"]
    manifest = {
        "stage": "A7AB-5",
        "generated_at": now_utc(),
        "decision": decision,
        "executes_contract_only": True,
        "executes_replay": False,
        "executes_search": False,
        "executes_training": False,
        "uses_may": False,
        "input_a7ab4_decision": a7ab4.get("decision"),
        "queue_count": int(len(queue)),
        "queue_family_count": int(queue["family_id"].nunique()),
        "queue_seed_field_count": int(queue["primary_seed_field"].nunique()),
        "queue_skeleton_count": int(queue["skeleton_key"].nunique()),
        "authorizes_a7ab6_small_numeric_replay_preflight": True,
        "authorizes_formula_search_execution": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }

    queue.to_csv(RUNTIME / "a7ab5_replay_contract_queue.csv", index=False)
    label_contract.to_csv(RUNTIME / "a7ab5_label_contract.csv", index=False)
    control_contract.to_csv(RUNTIME / "a7ab5_control_contract.csv", index=False)
    pass_gates.to_csv(RUNTIME / "a7ab5_pass_gates.csv", index=False)
    write_json(RUNTIME / "a7ab5_manifest.json", manifest)
    write_json(RUNTIME / "a7ab5_authorization_matrix.json", authorization)

    lines = [
        "# CRYPTO A7AB-5 NUMERIC REPLAY CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "A7AB-5 is a contract only. It authorizes a bounded A7AB-6 small numeric replay preflight and does not authorize formula search, large search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Replay Contract Queue Summary",
        "",
        md_table(
            queue.groupby("family_id", as_index=False).agg(
                queued_count=("candidate_id", "count"),
                seed_field_count=("primary_seed_field", "nunique"),
                skeleton_count=("skeleton_key", "nunique"),
            )
        ),
        "",
        "## Label Contract",
        "",
        md_table(label_contract),
        "",
        "## Control Contract",
        "",
        md_table(control_contract),
        "",
        "## Pass Gates",
        "",
        md_table(pass_gates),
        "",
        "## Queue Sample",
        "",
        md_table(
            queue[
                [
                    "replay_contract_rank",
                    "candidate_id",
                    "family_id",
                    "primary_seed_field",
                    "motif",
                    "finite_share",
                    "nonzero_share",
                    "expression",
                ]
            ],
            max_rows=40,
        ),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
