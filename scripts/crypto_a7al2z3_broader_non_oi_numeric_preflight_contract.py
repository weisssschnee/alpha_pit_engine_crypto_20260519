from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7al2z3_broader_non_oi_numeric_preflight_contract"
REPORT = REPO / "reports" / "CRYPTO_A7AL2Z3_BROADER_NON_OI_NUMERIC_PREFLIGHT_CONTRACT_20260529.md"
Z2R_MANIFEST = REPO / "runtime" / "a7al2z2r_broader_non_oi_materialization_repair" / "a7al2z2r_manifest.json"
Z2R_SELECTED = REPO / "runtime" / "a7al2z2r_broader_non_oi_materialization_repair" / "a7al2z2r_repaired_selected_candidates.csv"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
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

    z2r = read_json(Z2R_MANIFEST)
    if not z2r.get("authorizes_a7al2z3_numeric_preflight_contract"):
        raise SystemExit("A7AL-2Z2R does not authorize Z3 numeric preflight contract")
    selected = pd.read_csv(Z2R_SELECTED)
    family_summary = (
        selected.groupby("objective_family", dropna=False)
        .agg(candidate_count=("candidate_id", "count"), skeleton_count=("skeleton_key", "nunique"))
        .reset_index()
    )
    controls = pd.DataFrame(
        [
            {"control": "one_bar_lag", "purpose": "entry latency survival"},
            {"control": "wrong_lag_future_24h", "purpose": "future-lag contamination check"},
            {"control": "wrong_lag_stale_168h", "purpose": "stale-lag contamination check"},
            {"control": "time_shuffle", "purpose": "time structure placebo"},
            {"control": "symbol_shuffle", "purpose": "cross-symbol identity placebo"},
            {"control": "same_family_random", "purpose": "same-shape random placebo"},
        ]
    )
    manifest = {
        "stage": "A7AL-2Z3",
        "generated_at": now_utc(),
        "decision": "PASS_A7AL2Z3_BROADER_NON_OI_NUMERIC_PREFLIGHT_CONTRACT_READY_FOR_Z4",
        "executes_contract_only": True,
        "executes_numeric_replay": False,
        "executes_training": False,
        "authorizes_a7al2z4_broader_non_oi_numeric_preflight": True,
        "authorizes_full_replay": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "candidate_count": int(len(selected)),
        "family_count": int(selected["objective_family"].nunique()),
        "symbol_cap": 96,
        "hours_per_split": 720,
        "label": "log_trade_close_t_plus_24h_minus_log_trade_close_t",
        "orientation": "train_2024_original_spread_sign_only",
        "cost_proxy_bps": [10],
        "may_policy": "post_selection_stress_only",
        "uses_may_in_selector_or_generation": False,
    }
    family_summary.to_csv(RUNTIME / "a7al2z3_family_input_summary.csv", index=False)
    controls.to_csv(RUNTIME / "a7al2z3_negative_control_contract.csv", index=False)
    write_json(RUNTIME / "a7al2z3_manifest.json", manifest)
    write_json(
        RUNTIME / "a7al2z3_authorization_matrix.json",
        {
            "A7AL-2Z3": {"status": manifest["decision"]},
            "a7al2z4_numeric_preflight": {"authorized": True},
            "full_replay": {"authorized": False},
            "formula_search": {"authorized": False},
            "large_search": {"authorized": False},
            "alpha_proof_shadow_paper_live": {"authorized": False},
        },
    )
    lines = [
        "# CRYPTO A7AL-2Z3 BROADER NON-OI NUMERIC PREFLIGHT CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "Z3 authorizes one bounded numeric preflight on the Z2R materialized queue. It does not authorize search, full replay, or proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Inputs",
        "",
        md_table(family_summary),
        "",
        "## Negative Controls",
        "",
        md_table(controls),
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
