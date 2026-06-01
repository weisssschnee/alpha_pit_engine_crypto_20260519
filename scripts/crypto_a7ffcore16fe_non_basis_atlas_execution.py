from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16fe_non_basis_atlas_execution"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16FE_NON_BASIS_ATLAS_EXECUTION_20260601.md"
CORE16F = REPO / "runtime" / "a7ffcore16f_non_basis_supply_repair_contract" / "a7ffcore16f_manifest.json"
CONTRACT = REPO / "runtime" / "a7ffcore16f_non_basis_supply_repair_contract" / "a7ffcore16f_execution_contract.json"
TARGET_POLICY = REPO / "runtime" / "a7ffcore16f_non_basis_supply_repair_contract" / "a7ffcore16f_target_family_policy.csv"
CORE16E_RESPONSE = REPO / "runtime" / "a7ffcore16e_expanded_primitive_operator_atlas" / "a7ffcore16e_expanded_response_map.csv"


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

    core16f = read_json(CORE16F)
    if core16f.get("decision") != "PASS_A7FFCORE16F_NON_BASIS_SUPPLY_REPAIR_CONTRACT_READY_FOR_CORE16FE":
        raise SystemExit(f"CORE16F is not ready for CORE16FE: {core16f.get('decision')}")
    contract = read_json(CONTRACT)
    targets = pd.read_csv(TARGET_POLICY)
    response = pd.read_csv(CORE16E_RESPONSE)

    target_families = [str(x) for x in targets["field_family"].tolist()]
    non_basis = response[response["field_family"].isin(target_families)].copy()
    non_basis["control_ratio_premay_max"] = pd.to_numeric(non_basis["control_ratio_premay_max"], errors="coerce")
    non_basis["premay_positive_split_count"] = pd.to_numeric(non_basis["premay_positive_split_count"], errors="coerce").fillna(0)
    non_basis["strict_non_basis_candidate"] = (
        (non_basis["premay_all_positive"].astype(str).str.lower() == "true")
        & (non_basis["control_ratio_premay_max"] < 1.0)
    )
    non_basis["near_miss_non_basis"] = (
        (~non_basis["strict_non_basis_candidate"])
        & (non_basis["premay_positive_split_count"] >= 3)
        & (non_basis["control_ratio_premay_max"] >= 1.0)
        & (non_basis["control_ratio_premay_max"] < 1.5)
    )
    non_basis["lane"] = "reject"
    non_basis.loc[non_basis["near_miss_non_basis"], "lane"] = "forensic_near_miss"
    non_basis.loc[non_basis["strict_non_basis_candidate"], "lane"] = "strict_non_basis_candidate"

    strict = non_basis[non_basis["strict_non_basis_candidate"]].copy()
    near = non_basis[non_basis["near_miss_non_basis"]].copy()

    family_summary = (
        non_basis.groupby("field_family", dropna=False)
        .agg(
            rows=("field_name", "size"),
            strict_candidate_count=("strict_non_basis_candidate", "sum"),
            near_miss_count=("near_miss_non_basis", "sum"),
            transform_count=("transform", "nunique"),
            label_family_count=("label_family", "nunique"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
        .sort_values(["strict_candidate_count", "near_miss_count"], ascending=[False, False])
    )
    if strict.empty:
        strict_family_count = 0
        top_family_share = 0.0
    else:
        family_counts = strict["field_family"].value_counts()
        strict_family_count = int(family_counts.shape[0])
        top_family_share = float(family_counts.iloc[0] / family_counts.sum())

    strict_count = int(strict.shape[0])
    near_count = int(near.shape[0])
    non_basis_min = int(contract.get("non_basis_min_candidate_count", 32))
    family_min = int(contract.get("non_basis_min_field_family_count", 4))
    top_max = float(contract.get("top_family_share_max", 0.50))
    blockers: list[str] = []
    if strict_count < non_basis_min:
        blockers.append("non_basis_candidate_count_lt_32")
    if strict_family_count < family_min:
        blockers.append("non_basis_field_family_count_lt_4")
    if strict_count and top_family_share > top_max:
        blockers.append("top_non_basis_family_share_gt_50pct")

    if blockers:
        decision = "HOLD_A7FFCORE16FE_NON_BASIS_ATLAS_SUPPLY_INSUFFICIENT"
        next_allowed = "A7FF-CORE16FER non-basis atlas forensic / family-native repair"
        authorizes_core17 = False
    else:
        decision = "PASS_A7FFCORE16FE_NON_BASIS_ATLAS_SUPPLY_READY_FOR_CORE17_CONTRACT"
        next_allowed = "A7FF-CORE17 objective seed policy contract"
        authorizes_core17 = True

    manifest = {
        "stage": "A7FF-CORE16FE",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16F",
        "source_decision": core16f.get("decision"),
        "decision": decision,
        "blockers": blockers,
        "response_rows": int(non_basis.shape[0]),
        "strict_non_basis_candidate_count": strict_count,
        "near_miss_non_basis_count": near_count,
        "strict_non_basis_field_family_count": strict_family_count,
        "top_non_basis_family_share": top_family_share,
        "authorizes_core17": authorizes_core17,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": next_allowed,
    }

    non_basis.to_csv(RUNTIME / "a7ffcore16fe_non_basis_response_reclassification.csv", index=False)
    strict.to_csv(RUNTIME / "a7ffcore16fe_strict_non_basis_atlas_candidates.csv", index=False)
    near.to_csv(RUNTIME / "a7ffcore16fe_non_basis_near_miss_forensic_lane.csv", index=False)
    family_summary.to_csv(RUNTIME / "a7ffcore16fe_family_supply_summary.csv", index=False)
    write_json(RUNTIME / "a7ffcore16fe_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE16FE NON-BASIS ATLAS EXECUTION",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16FE executes the non-basis primitive/operator atlas reclassification authorized by CORE16F. It reuses the expanded response rows, applies non-basis family floors and near-miss lanes, and does not execute replay, formula generation, search, promotion, alpha proof, shadow, paper, or live.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Family Supply Summary",
        "",
        md_table(family_summary),
        "",
        "## Strict Candidate Sample",
        "",
        md_table(strict[["field_name", "field_family", "transform", "label_family", "label_horizon_h", "control_ratio_premay_max", "lag_ok"]].head(40)),
        "",
        "## Near Miss Sample",
        "",
        md_table(near[["field_name", "field_family", "transform", "label_family", "label_horizon_h", "control_ratio_premay_max", "premay_positive_split_count"]].head(40)),
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
