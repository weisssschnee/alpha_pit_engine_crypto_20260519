from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16k_h2_strict_floor_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16K_H2_STRICT_FLOOR_REPAIR_CONTRACT_20260601.md"
CORE16J = REPO / "runtime" / "a7ffcore16j_nearmiss_resolution_audit" / "a7ffcore16j_manifest.json"
STRICT_QUEUE = REPO / "runtime" / "a7ffcore16j_nearmiss_resolution_audit" / "a7ffcore16j_strict_preseed_queue.csv"
EXCLUDED_NEAR = REPO / "runtime" / "a7ffcore16j_nearmiss_resolution_audit" / "a7ffcore16j_excluded_nearmiss_rows.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload) -> None:
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
    core16j = read_json(CORE16J)
    if core16j.get("decision") != "HOLD_A7FFCORE16J_STRICT_QUEUE_H2_FLOOR_INSUFFICIENT":
        raise SystemExit(f"CORE16J is not ready for CORE16K: {core16j.get('decision')}")
    strict = pd.read_csv(STRICT_QUEUE)
    near = pd.read_csv(EXCLUDED_NEAR)
    h2_strict = strict[strict["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].copy()
    h2_near = near[near["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].copy()
    repair_policy = pd.DataFrame(
        [
            {
                "policy_id": "h2_delta_repair",
                "scope": "H2_I4_near_miss_repair",
                "action": "run H2-only asymmetric transform variants around excluded near-miss rows",
                "target": "at least 3 additional strict H2 candidates with control_ratio < 1.0",
            },
            {
                "policy_id": "no_nearmiss_promotion",
                "scope": "H2 near-miss",
                "action": "near-miss rows remain excluded unless rerun as strict rows under repaired transforms",
                "target": "no forensic row enters CORE17 queue directly",
            },
            {
                "policy_id": "queue_fill",
                "scope": "balanced strict queue",
                "action": "replace excluded near-miss rows with strict H2 rows only",
                "target": "strict queue size 96 and H2 strict count >= 12",
            },
        ]
    )
    execution_contract = {
        "stage": "A7FF-CORE16KE",
        "name": "H2/I4 strict-floor repair execution",
        "authorized": True,
        "executes_replay": False,
        "executes_search": False,
        "target": {
            "additional_h2_strict_candidates": 3,
            "strict_h2_count": 12,
            "strict_queue_size": 96,
        },
        "allowed_scope": [
            "H2_I4_near_miss_repair only",
            "taker_flow x OI/liquidity typed probes",
            "control_ratio < 1.0 strict promotion only",
        ],
        "forbidden": [
            "near-miss direct promotion",
            "open grammar FormulaGen",
            "bounded replay",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }
    manifest = {
        "stage": "A7FF-CORE16K",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16J",
        "source_decision": core16j.get("decision"),
        "decision": "PASS_A7FFCORE16K_H2_STRICT_FLOOR_REPAIR_CONTRACT_READY_FOR_CORE16KE",
        "strict_h2_count": int(h2_strict.shape[0]),
        "excluded_h2_near_miss_count": int(h2_near.shape[0]),
        "additional_h2_needed": max(0, 12 - int(h2_strict.shape[0])),
        "authorizes_core16ke": True,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16KE H2/I4 strict-floor repair execution",
    }
    strict.to_csv(RUNTIME / "a7ffcore16k_source_strict_queue.csv", index=False)
    h2_strict.to_csv(RUNTIME / "a7ffcore16k_source_h2_strict_rows.csv", index=False)
    h2_near.to_csv(RUNTIME / "a7ffcore16k_source_h2_excluded_nearmiss_rows.csv", index=False)
    repair_policy.to_csv(RUNTIME / "a7ffcore16k_repair_policy.csv", index=False)
    write_json(RUNTIME / "a7ffcore16k_execution_contract.json", execution_contract)
    write_json(RUNTIME / "a7ffcore16k_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16K H2 STRICT-FLOOR REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        "`PASS_A7FFCORE16K_H2_STRICT_FLOOR_REPAIR_CONTRACT_READY_FOR_CORE16KE`",
        "",
        "CORE16K defines a narrow repair for the H2/I4 strict floor. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Repair Policy",
        "",
        md_table(repair_policy),
        "",
        "## Execution Contract",
        "",
        "```json",
        json.dumps(execution_contract, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
