from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16j_nearmiss_resolution_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16J_NEARMISS_RESOLUTION_AUDIT_20260601.md"
CORE16I = REPO / "runtime" / "a7ffcore16i_balanced_preseed_queue_audit" / "a7ffcore16i_manifest.json"
QUEUE = REPO / "runtime" / "a7ffcore16i_balanced_preseed_queue_audit" / "a7ffcore16i_balanced_preseed_queue.csv"


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
    core16i = read_json(CORE16I)
    if core16i.get("decision") != "PASS_A7FFCORE16I_BALANCED_PRESEED_QUEUE_READY_FOR_NEARMISS_RESOLUTION":
        raise SystemExit(f"CORE16I is not ready for CORE16J: {core16i.get('decision')}")
    queue = pd.read_csv(QUEUE)
    strict = queue[queue["queue_role"].astype(str).eq("strict_candidate")].copy()
    near = queue[queue["queue_role"].astype(str).eq("forensic_near_miss_not_alpha_seed")].copy()
    strict_size = int(strict.shape[0])
    strict_family_count = int(strict["second_pass_family"].nunique()) if not strict.empty else 0
    strict_top_share = float(strict["second_pass_family"].value_counts(normalize=True).max()) if not strict.empty else 0.0
    strict_h2 = int(strict[strict["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].shape[0])
    strict_non_l5 = float(strict["label_family"].astype(str).ne("L5_vol_adjusted_return").mean()) if not strict.empty else 0.0
    strict_operator_count = int(strict["operator"].nunique()) if not strict.empty else 0
    strict_ok = (
        strict_size >= 96
        and strict_family_count >= 4
        and strict_top_share <= 0.45
        and strict_h2 >= 12
        and strict_non_l5 >= 0.40
        and strict_operator_count >= 2
    )
    if strict_ok:
        decision = "PASS_A7FFCORE16J_STRICT_QUEUE_READY_FOR_CORE17_CONTRACT"
        next_allowed = "A7FF-CORE17 objective seed policy contract"
        authorizes_core17 = True
        blockers = []
    else:
        decision = "HOLD_A7FFCORE16J_STRICT_QUEUE_H2_FLOOR_INSUFFICIENT"
        next_allowed = "A7FF-CORE16K H2/I4 strict-floor repair"
        authorizes_core17 = False
        blockers = []
        if strict_size < 96:
            blockers.append("strict_queue_size_lt_96")
        if strict_h2 < 12:
            blockers.append("strict_h2_floor_lt_12")
        if strict_family_count < 4:
            blockers.append("strict_family_count_lt_4")
        if strict_top_share > 0.45:
            blockers.append("strict_top_family_share_gt_45pct")
        if strict_non_l5 < 0.40:
            blockers.append("strict_non_l5_share_lt_40pct")
        if strict_operator_count < 2:
            blockers.append("strict_operator_count_lt_2")

    summary = pd.DataFrame(
        [
            {"metric": "queue_size", "value": int(queue.shape[0])},
            {"metric": "strict_size", "value": strict_size},
            {"metric": "near_miss_size", "value": int(near.shape[0])},
            {"metric": "strict_family_count", "value": strict_family_count},
            {"metric": "strict_h2_count", "value": strict_h2},
            {"metric": "strict_top_family_share", "value": strict_top_share},
            {"metric": "strict_non_l5_share", "value": strict_non_l5},
            {"metric": "strict_operator_count", "value": strict_operator_count},
        ]
    )
    near_resolution = pd.DataFrame(
        [
            {
                "resolution": "exclude_from_alpha_seed",
                "rows": int(near.shape[0]),
                "reason": "near-miss rows have control_ratio >= 1.0 and cannot be promoted without a dedicated strict repair",
            }
        ]
    )
    next_contract = {
        "stage": "A7FF-CORE16K",
        "name": "H2/I4 strict-floor repair",
        "authorized": not authorizes_core17,
        "executes_replay": False,
        "executes_search": False,
        "target": {
            "strict_h2_candidate_count": 12,
            "strict_queue_size": 96,
            "near_miss_promotions_allowed": False,
        },
        "forbidden": [
            "promoting near-miss as alpha seed",
            "open grammar FormulaGen",
            "bounded replay",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }
    manifest = {
        "stage": "A7FF-CORE16J",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16I",
        "source_decision": core16i.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "strict_queue_size": strict_size,
        "strict_h2_count": strict_h2,
        "near_miss_excluded_count": int(near.shape[0]),
        "authorizes_core17": authorizes_core17,
        "authorizes_core16k": not authorizes_core17,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": next_allowed,
    }
    strict.to_csv(RUNTIME / "a7ffcore16j_strict_preseed_queue.csv", index=False)
    near.to_csv(RUNTIME / "a7ffcore16j_excluded_nearmiss_rows.csv", index=False)
    summary.to_csv(RUNTIME / "a7ffcore16j_strict_queue_summary.csv", index=False)
    near_resolution.to_csv(RUNTIME / "a7ffcore16j_nearmiss_resolution.csv", index=False)
    write_json(RUNTIME / "a7ffcore16j_next_contract.json", next_contract)
    write_json(RUNTIME / "a7ffcore16j_manifest.json", manifest)
    report = [
        "# CRYPTO A7FF-CORE16J NEAR-MISS RESOLUTION AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16J resolves the near-miss rows from CORE16I. Near-miss rows remain excluded from alpha seed eligibility. This stage does not execute replay, formula generation, search, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Strict Queue Summary",
        "",
        md_table(summary),
        "",
        "## Near-Miss Resolution",
        "",
        md_table(near_resolution),
        "",
        "## Next Contract",
        "",
        "```json",
        json.dumps(next_contract, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
