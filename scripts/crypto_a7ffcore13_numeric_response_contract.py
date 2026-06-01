from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore13_numeric_response_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE13_NUMERIC_RESPONSE_CONTRACT_20260601.md"
A7FFCORE12E = REPO / "runtime" / "a7ffcore12e_materialization_preflight" / "a7ffcore12e_manifest.json"
MAT_ROWS = REPO / "runtime" / "a7ffcore12e_materialization_preflight" / "a7ffcore12e_materialization_rows.csv"

LABELS = ["L1_cross_sectional_relative_return", "L3_liquidity_tier_relative_return", "L5_vol_adjusted_return"]
HORIZONS = [1, 4, 8, 24]
CONTROLS = ["wrong_lag_future", "wrong_lag_stale", "time_shuffle", "symbol_shuffle", "same_family_placebo"]
SHARD_SIZE = 104


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
    core12e = read_json(A7FFCORE12E)
    if core12e.get("decision") != "PASS_A7FFCORE12E_MATERIALIZATION_PREFLIGHT_READY_FOR_CORE13":
        raise SystemExit(f"A7FF-CORE12E is not ready: {core12e.get('decision')}")
    rows = pd.read_csv(MAT_ROWS)
    queue = rows[rows["status"].eq("ok")].copy().reset_index(drop=True)
    shard_rows = []
    for i, start in enumerate(range(0, len(queue), SHARD_SIZE)):
        end = min(start + SHARD_SIZE, len(queue))
        shard_rows.append({"shard_id": f"S{i:02d}", "start_index": start, "end_index_exclusive": end, "candidate_count": end - start})
    shard_plan = pd.DataFrame(shard_rows)
    label_contract = pd.DataFrame([{"label_id": label, "horizon": h, "primary_non_l7": True} for label in LABELS for h in HORIZONS])
    control_contract = pd.DataFrame(
        [{"control": c, "dominance_role": "hard_control"} for c in CONTROLS]
        + [{"control": "sign_flip", "dominance_role": "diagnostic_only_excluded_from_abs_max"}]
    )
    pass_gates = {
        "eval_error_count": 0,
        "numeric_clue_candidates_min": 64,
        "semantic_bucket_count_min": 6,
        "motif_bucket_count_min": 5,
        "control_ratio_lt_0_8_for_clue": True,
        "sign_flip_diagnostic_only": True,
    }
    queue.to_csv(RUNTIME / "a7ffcore13_numeric_response_queue.csv", index=False)
    shard_plan.to_csv(RUNTIME / "a7ffcore13_shard_plan.csv", index=False)
    label_contract.to_csv(RUNTIME / "a7ffcore13_label_contract.csv", index=False)
    control_contract.to_csv(RUNTIME / "a7ffcore13_control_contract.csv", index=False)
    write_json(RUNTIME / "a7ffcore13_pass_gates.json", pass_gates)
    authorization = {
        "A7FF-CORE13E numeric response execution": True,
        "replay": False,
        "search": False,
        "large_search": False,
        "alpha_proof": False,
        "shadow_paper_live": False,
    }
    write_json(RUNTIME / "a7ffcore13_authorization_matrix.json", authorization)
    manifest = {
        "stage": "A7FF-CORE13",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE12E",
        "source_decision": core12e.get("decision"),
        "decision": "PASS_A7FFCORE13_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE13E",
        "queue_count": int(len(queue)),
        "semantic_bucket_count": int(queue["semantic_bucket"].nunique()),
        "motif_bucket_count": int(queue["motif_bucket"].nunique()),
        "label_count": len(LABELS),
        "horizon_count": len(HORIZONS),
        "control_count": len(CONTROLS),
        "shard_count": int(len(shard_plan)),
        "executes_numeric": False,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core13e": True,
        "authorizes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "next_allowed": "A7FF-CORE13E numeric response execution",
    }
    write_json(RUNTIME / "a7ffcore13_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE13 NUMERIC RESPONSE CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        "`PASS_A7FFCORE13_NUMERIC_RESPONSE_CONTRACT_READY_FOR_CORE13E`",
        "",
        "A7FF-CORE13 defines numeric response execution over CORE12E materialized temp subgraphs. It does not execute numeric response, replay, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Shard Plan",
        "",
        md_table(shard_plan),
        "",
        "## Label Contract",
        "",
        md_table(label_contract),
        "",
        "## Control Contract",
        "",
        md_table(control_contract),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
