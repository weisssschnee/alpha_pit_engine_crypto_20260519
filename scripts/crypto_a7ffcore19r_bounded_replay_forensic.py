from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore19r_bounded_replay_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE19R_BOUNDED_REPLAY_FORENSIC_20260601.md"
CORE19E = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution" / "a7ffcore19e_manifest.json"
ROWS = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution" / "a7ffcore19e_replay_rows.csv"
CANDIDATES = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution" / "a7ffcore19e_candidate_summary.csv"
CLEAN = REPO / "runtime" / "a7ffcore19e_bounded_replay_execution" / "a7ffcore19e_replay_clean_candidates.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


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
    core19e = read_json(CORE19E)
    if core19e.get("decision") != "HOLD_A7FFCORE19E_BOUNDED_REPLAY_INSUFFICIENT":
        raise SystemExit(f"CORE19E is not in forensic state: {core19e.get('decision')}")
    rows = load_csv(ROWS)
    candidates = load_csv(CANDIDATES)
    clean = load_csv(CLEAN)

    fail_rows = []
    for cand in candidates.to_dict("records"):
        cid = str(cand["candidate_id"])
        cand_rows = rows[rows["candidate_id"].astype(str).eq(cid)].copy()
        premay_5 = cand_rows[cand_rows["split"].isin(["validation_2025H1", "test_2025H2", "recent_oos_2026JanApr"]) & cand_rows["cost_bps"].eq(5)]
        positive_splits = int(pd.to_numeric(premay_5["cost_adjusted_spread"], errors="coerce").gt(0).sum())
        control_clean_splits = int(pd.to_numeric(premay_5["control_ratio_premay_max"], errors="coerce").lt(1.0).sum())
        lag_positive_splits = int(pd.to_numeric(premay_5["one_bar_lag_spread"], errors="coerce").gt(0).sum())
        if str(cand.get("replay_clean", "")).lower() == "true":
            primary_failure = "clean"
        elif positive_splits < 3:
            primary_failure = "cost_adjusted_spread_not_positive_all_premay"
        elif control_clean_splits < 3:
            primary_failure = "control_ratio_not_clean_all_premay"
        elif lag_positive_splits < 3:
            primary_failure = "one_bar_lag_not_positive_all_premay"
        else:
            primary_failure = "unclassified_gate_gap"
        fail_rows.append(
            {
                "candidate_id": cid,
                "seed_lane": cand.get("seed_lane"),
                "second_pass_family": cand.get("second_pass_family"),
                "label_family": cand.get("label_family"),
                "label_horizon_h": cand.get("label_horizon_h"),
                "primary_failure": primary_failure,
                "positive_splits_at_5bps": positive_splits,
                "control_clean_splits": control_clean_splits,
                "lag_positive_splits": lag_positive_splits,
                "replay_clean": cand.get("replay_clean"),
            }
        )
    failure = pd.DataFrame(fail_rows)
    failure_summary = (
        failure.groupby(["seed_lane", "primary_failure"], dropna=False)
        .agg(rows=("candidate_id", "size"), label_family_count=("label_family", "nunique"))
        .reset_index()
        .sort_values(["seed_lane", "rows"], ascending=[True, False])
    )
    clean_summary = (
        clean.groupby(["seed_lane", "label_family"], dropna=False)
        .agg(rows=("candidate_id", "size"), median_control_ratio=("median_control_ratio", "median"), median_cost_adjusted_spread=("median_cost_adjusted_spread", "median"))
        .reset_index()
        .sort_values("rows", ascending=False)
        if not clean.empty
        else pd.DataFrame()
    )
    recommended = pd.DataFrame(
        [
            {
                "action_id": "R0_no_large_search",
                "action": "do not proceed to CORE20/search-readiness",
                "reason": "bounded replay clean supply is 2 candidates across 2 lanes, below the 12/3 gate",
            },
            {
                "action_id": "R1_contract_replay_repair",
                "action": "write CORE19S bounded replay repair contract",
                "reason": "the failure has moved from seed supply to replay translation; repair should target replay label/cost/lag translation, not formula generation",
            },
            {
                "action_id": "R2_preserve_clean_clues",
                "action": "freeze the 2 replay-clean candidates as diagnostic replay clues only",
                "reason": "they are not enough for search readiness or alpha proof",
            },
        ]
    )
    failure.to_csv(RUNTIME / "a7ffcore19r_candidate_failure_map.csv", index=False)
    failure_summary.to_csv(RUNTIME / "a7ffcore19r_failure_summary.csv", index=False)
    clean_summary.to_csv(RUNTIME / "a7ffcore19r_clean_clue_summary.csv", index=False)
    recommended.to_csv(RUNTIME / "a7ffcore19r_recommended_actions.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE19R",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE19E",
        "source_decision": core19e.get("decision"),
        "decision": "PASS_A7FFCORE19R_BOUNDED_REPLAY_FORENSIC_COMPLETE_READY_FOR_CORE19S",
        "dominant_failure": "bounded_replay_translation_supply_insufficient",
        "replay_clean_candidate_count": int(core19e.get("replay_clean_candidate_count", 0)),
        "replay_clean_seed_lane_count": int(core19e.get("replay_clean_seed_lane_count", 0)),
        "authorizes_core19s": True,
        "authorizes_core20": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE19S bounded replay repair contract",
    }
    write_json(RUNTIME / "a7ffcore19r_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE19R BOUNDED REPLAY FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE19R freezes the CORE19E bounded replay result. It does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Failure Summary",
        "",
        md_table(failure_summary),
        "",
        "## Clean Clue Summary",
        "",
        md_table(clean_summary),
        "",
        "## Recommended Actions",
        "",
        md_table(recommended),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
