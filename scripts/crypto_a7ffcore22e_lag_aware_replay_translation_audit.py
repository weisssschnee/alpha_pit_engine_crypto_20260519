from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore22e_lag_aware_replay_translation_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE22E_LAG_AWARE_REPLAY_TRANSLATION_AUDIT_20260601.md"
CORE22 = REPO / "runtime" / "a7ffcore22_lag_aware_replay_translation_contract" / "a7ffcore22_manifest.json"
ROWS = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution" / "a7ffcore19e_replay_rows.csv"

PREMAY = ["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]


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


def count_clean(data: pd.DataFrame, spread_col: str, cost: int) -> tuple[int, int, float]:
    x = data[data["split"].isin(PREMAY) & data["cost_bps"].eq(cost)].copy()
    ok = x[
        pd.to_numeric(x[spread_col], errors="coerce").gt(0)
        & pd.to_numeric(x["control_ratio_premay_max"], errors="coerce").lt(1.0)
    ]
    split_counts = ok.groupby("candidate_id")["split"].nunique()
    clean_ids = set(split_counts[split_counts >= len(PREMAY)].index.astype(str))
    clean_lanes = x[x["candidate_id"].astype(str).isin(clean_ids)]["seed_lane"].nunique() if clean_ids else 0
    non_l5_share = x[x["candidate_id"].astype(str).isin(clean_ids)]["label_family"].astype(str).ne("L5_vol_adjusted_return").mean() if clean_ids else 0.0
    return len(clean_ids), int(clean_lanes), float(non_l5_share)


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    core22 = read_json(CORE22)
    if core22.get("decision") != "PASS_A7FFCORE22_LAG_AWARE_REPLAY_TRANSLATION_CONTRACT_READY_FOR_CORE22E":
        raise SystemExit(f"CORE22 is not ready: {core22.get('decision')}")
    rows = pd.read_csv(ROWS)
    matrix_rows = []
    for cost in sorted(rows["cost_bps"].unique()):
        same_count, same_lanes, same_non_l5 = count_clean(rows, "cost_adjusted_spread", int(cost))
        lag_source = rows.copy()
        lag_source["lag_cost_adjusted_spread"] = pd.to_numeric(lag_source["one_bar_lag_spread"], errors="coerce") - (2.0 * int(cost) / 10000.0)
        lag_count, lag_lanes, lag_non_l5 = count_clean(lag_source, "lag_cost_adjusted_spread", int(cost))
        stale_proxy = rows.copy()
        stale_proxy["stale_proxy_spread"] = pd.to_numeric(stale_proxy["spread"], errors="coerce")
        stale_count, stale_lanes, stale_non_l5 = count_clean(stale_proxy, "stale_proxy_spread", int(cost))
        matrix_rows.extend(
            [
                {"lag_bucket": "same_bar_diagnostic", "cost_bps": int(cost), "clean_candidate_count": same_count, "clean_lane_count": same_lanes, "non_l5_share": same_non_l5},
                {"lag_bucket": "one_bar_primary_costed", "cost_bps": int(cost), "clean_candidate_count": lag_count, "clean_lane_count": lag_lanes, "non_l5_share": lag_non_l5},
                {"lag_bucket": "stale_proxy_uncosted", "cost_bps": int(cost), "clean_candidate_count": stale_count, "clean_lane_count": stale_lanes, "non_l5_share": stale_non_l5},
            ]
        )
    matrix = pd.DataFrame(matrix_rows)
    best_one_bar = matrix[matrix["lag_bucket"].eq("one_bar_primary_costed")].sort_values(["clean_candidate_count", "clean_lane_count"], ascending=[False, False]).head(1)
    best_same = matrix[matrix["lag_bucket"].eq("same_bar_diagnostic")].sort_values(["clean_candidate_count", "clean_lane_count"], ascending=[False, False]).head(1)
    best_one_bar_count = int(best_one_bar["clean_candidate_count"].iloc[0]) if not best_one_bar.empty else 0
    best_one_bar_lanes = int(best_one_bar["clean_lane_count"].iloc[0]) if not best_one_bar.empty else 0
    same_bar_count = int(best_same["clean_candidate_count"].iloc[0]) if not best_same.empty else 0
    diagnosis = pd.DataFrame(
        [
            {"finding": "one_bar_primary_supply", "value": best_one_bar_count, "interpretation": "best executable lag clean candidate count"},
            {"finding": "one_bar_primary_lanes", "value": best_one_bar_lanes, "interpretation": "best executable lag clean lane breadth"},
            {"finding": "same_bar_diagnostic_supply", "value": same_bar_count, "interpretation": "same-bar diagnostic count; not promotion evidence"},
            {"finding": "same_bar_minus_one_bar_gap", "value": same_bar_count - best_one_bar_count, "interpretation": "timing fragility proxy"},
        ]
    )
    blockers: list[str] = []
    if best_one_bar_count < 6:
        blockers.append("one_bar_clean_count_lt_6")
    if best_one_bar_lanes < 3:
        blockers.append("one_bar_clean_lane_count_lt_3")
    if same_bar_count > best_one_bar_count * 2 and same_bar_count >= 6:
        blockers.append("same_bar_dominates_one_bar")
    decision = "PASS_A7FFCORE22E_LAG_TRANSLATION_READY_FOR_CORE23" if not blockers else "HOLD_A7FFCORE22E_LAG_TRANSLATION_INSUFFICIENT"
    matrix.to_csv(RUNTIME / "a7ffcore22e_lag_translation_matrix.csv", index=False)
    diagnosis.to_csv(RUNTIME / "a7ffcore22e_diagnosis.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE22E",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE22",
        "source_decision": core22.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "best_one_bar_clean_candidate_count": best_one_bar_count,
        "best_one_bar_clean_lane_count": best_one_bar_lanes,
        "best_same_bar_diagnostic_count": same_bar_count,
        "authorizes_core23_contract": decision.startswith("PASS_"),
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE23 lane repair / search-readiness contract" if decision.startswith("PASS_") else "A7FF-CORE22R lag translation forensic",
    }
    write_json(RUNTIME / "a7ffcore22e_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE22E LAG-AWARE REPLAY TRANSLATION AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE22E audits lag-aware translation from existing replay rows. It does not execute formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Diagnosis",
        "",
        md_table(diagnosis),
        "",
        "## Lag Translation Matrix",
        "",
        md_table(matrix),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
