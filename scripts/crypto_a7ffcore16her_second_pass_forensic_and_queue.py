from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
RUNTIME = REPO / "runtime" / "a7ffcore16her_second_pass_forensic"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE16HER_SECOND_PASS_FORENSIC_20260601.md"
CORE16HE = REPO / "runtime" / "a7ffcore16he_second_pass_interaction_breadth" / "a7ffcore16he_manifest.json"
FAMILY_SUMMARY = REPO / "runtime" / "a7ffcore16he_second_pass_interaction_breadth" / "a7ffcore16he_family_summary.csv"
CANDIDATES = REPO / "runtime" / "a7ffcore16he_second_pass_interaction_breadth" / "a7ffcore16he_second_pass_candidates.csv"
RESPONSE = REPO / "runtime" / "a7ffcore16he_second_pass_interaction_breadth" / "a7ffcore16he_response_map.csv"


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


def build_balanced_queue(candidates: pd.DataFrame, response: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame()
    candidates = candidates.copy()
    candidates["control_ratio_premay_max"] = pd.to_numeric(candidates["control_ratio_premay_max"], errors="coerce")
    candidates["lag_bonus"] = candidates["lag_ok"].astype(str).str.lower().eq("true").astype(int)
    candidates["non_l5_bonus"] = candidates["label_family"].astype(str).ne("L5_vol_adjusted_return").astype(int)
    candidates["selection_score"] = (
        candidates["lag_bonus"] * 10.0
        + candidates["non_l5_bonus"] * 5.0
        - candidates["control_ratio_premay_max"].fillna(9.0)
    )
    target = 96
    caps = {
        "H0_I3_deconcentration": 35,
        "H1_I5_deconcentration": 35,
        "H2_I4_near_miss_repair": 12,
        "H3_cross_family_bridge": 24,
    }
    selected_parts: list[pd.DataFrame] = []
    h2_strict = candidates[candidates["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].copy()
    h2_strict = h2_strict.sort_values(["selection_score", "control_ratio_premay_max"], ascending=[False, True]).head(caps["H2_I4_near_miss_repair"])
    selected_parts.append(h2_strict)
    h2_count = int(h2_strict.shape[0])
    if h2_count < 12 and not response.empty:
        near = response[
            response["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")
            & response["near_miss"].astype(str).str.lower().eq("true")
        ].copy()
        if not near.empty:
            near["control_ratio_premay_max"] = pd.to_numeric(near["control_ratio_premay_max"], errors="coerce")
            near["queue_role"] = "forensic_near_miss_not_alpha_seed"
            add = near.sort_values("control_ratio_premay_max").head(12 - h2_count)
            selected_parts.append(add)
    for family, cap in caps.items():
        if family == "H2_I4_near_miss_repair":
            continue
        fam = candidates[candidates["second_pass_family"].astype(str).eq(family)].copy()
        if fam.empty:
            continue
        selected_parts.append(fam.sort_values(["selection_score", "control_ratio_premay_max"], ascending=[False, True]).head(cap))
    selected = pd.concat(selected_parts, ignore_index=True) if selected_parts else pd.DataFrame()
    if "queue_role" not in selected.columns:
        selected["queue_role"] = "strict_candidate"
    selected["queue_role"] = selected["queue_role"].fillna("strict_candidate")
    selected["family_priority"] = selected["second_pass_family"].map(
        {
            "H2_I4_near_miss_repair": 0,
            "H3_cross_family_bridge": 1,
            "H0_I3_deconcentration": 2,
            "H1_I5_deconcentration": 2,
        }
    ).fillna(9)
    selected = selected.sort_values(["family_priority", "queue_role", "selection_score"], ascending=[True, False, False]).head(target).copy()
    selected = selected.drop(columns=["family_priority"])
    selected.insert(0, "queue_rank", range(1, len(selected) + 1))
    return selected


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    core16he = read_json(CORE16HE)
    if core16he.get("decision") != "HOLD_A7FFCORE16HE_SECOND_PASS_BREADTH_INSUFFICIENT":
        raise SystemExit(f"CORE16HE is not in forensic state: {core16he.get('decision')}")
    family = load_csv(FAMILY_SUMMARY)
    candidates = load_csv(CANDIDATES)
    response = load_csv(RESPONSE)
    queue = build_balanced_queue(candidates, response)

    if queue.empty:
        queue_summary = pd.DataFrame()
        strict_count = 0
        family_count = 0
        top_share = 0.0
        h2_count = 0
        non_l5_share = 0.0
        near_count = 0
    else:
        queue_summary = (
            queue.groupby(["second_pass_family", "queue_role"], dropna=False)
            .agg(
                rows=("queue_rank", "size"),
                lag_ok_count=("lag_ok", lambda s: int(s.astype(str).str.lower().eq("true").sum())),
                median_control_ratio=("control_ratio_premay_max", "median"),
                label_family_count=("label_family", "nunique"),
                operator_count=("operator", "nunique"),
            )
            .reset_index()
            .sort_values("rows", ascending=False)
        )
        strict = queue[queue["queue_role"].astype(str).eq("strict_candidate")]
        strict_count = int(strict.shape[0])
        family_count = int(queue["second_pass_family"].nunique())
        top_share = float(queue["second_pass_family"].value_counts(normalize=True).max())
        h2_count = int(queue[queue["second_pass_family"].astype(str).eq("H2_I4_near_miss_repair")].shape[0])
        non_l5_share = float(queue["label_family"].astype(str).ne("L5_vol_adjusted_return").mean())
        near_count = int(queue["queue_role"].astype(str).eq("forensic_near_miss_not_alpha_seed").sum())

    queue_pass = (
        len(queue) >= 96
        and family_count >= 4
        and top_share <= 0.45
        and h2_count >= 12
        and non_l5_share >= 0.40
    )

    repair_actions = pd.DataFrame(
        [
            {
                "action_id": "R0_balanced_preseed_queue",
                "action": "use capped H0/H1, preserve H3, and top up H2 with explicitly flagged near-miss rows",
                "reason": "strict candidates are abundant but concentrated; H2 strict count is 9 vs floor 12",
            },
            {
                "action_id": "R1_no_core17_yet",
                "action": "do not authorize objective seed policy until near-miss rows are either upgraded or excluded by a dedicated audit",
                "reason": "balanced queue may need forensic rows to satisfy H2 breadth",
            },
            {
                "action_id": "R2_execute_core16i",
                "action": "run balanced pre-seed queue audit with role-aware near-miss isolation",
                "reason": "supply is now nonzero enough to test queue governance, not search",
            },
        ]
    )

    next_contract = {
        "stage": "A7FF-CORE16I",
        "name": "balanced interaction pre-seed queue audit",
        "authorized": True,
        "executes_replay": False,
        "executes_search": False,
        "inputs": [
            "CORE16HE second-pass candidates",
            "CORE16HE near-miss rows",
            "CORE16H cap policy",
        ],
        "queue_targets": {
            "queue_size": 96,
            "family_count": 4,
            "top_family_share_max": 0.45,
            "h2_floor": 12,
            "non_l5_share_min": 0.40,
            "near_miss_rows_must_be_role_flagged": True,
        },
        "forbidden": [
            "objective seed promotion from near-miss rows",
            "open grammar FormulaGen",
            "bounded replay",
            "large search",
            "alpha proof",
            "shadow/paper/live",
        ],
    }

    decision = "PASS_A7FFCORE16HER_SECOND_PASS_FORENSIC_READY_FOR_CORE16I"
    manifest = {
        "stage": "A7FF-CORE16HER",
        "generated_at": now_utc(),
        "source_stage": "A7FF-CORE16HE",
        "source_decision": core16he.get("decision"),
        "decision": decision,
        "dominant_failure": "breadth_gate_near_pass_with_h2_floor_shortfall",
        "source_candidate_count": int(core16he.get("second_pass_candidate_count", 0)),
        "source_family_count": int(core16he.get("second_pass_family_count", 0)),
        "balanced_queue_size": int(len(queue)),
        "balanced_queue_strict_count": strict_count,
        "balanced_queue_near_miss_count": near_count,
        "balanced_queue_family_count": family_count,
        "balanced_queue_top_family_share": top_share,
        "balanced_queue_h2_count": h2_count,
        "balanced_queue_non_l5_share": non_l5_share,
        "balanced_queue_meets_targets": queue_pass,
        "authorizes_core16i": True,
        "authorizes_core17": False,
        "authorizes_replay": False,
        "authorizes_formula_generation": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "executes_replay": False,
        "executes_search": False,
        "next_allowed": "A7FF-CORE16I balanced interaction pre-seed queue audit",
    }

    family.to_csv(RUNTIME / "a7ffcore16her_source_family_summary.csv", index=False)
    queue.to_csv(RUNTIME / "a7ffcore16her_balanced_preseed_queue_preview.csv", index=False)
    queue_summary.to_csv(RUNTIME / "a7ffcore16her_balanced_queue_summary.csv", index=False)
    repair_actions.to_csv(RUNTIME / "a7ffcore16her_repair_actions.csv", index=False)
    write_json(RUNTIME / "a7ffcore16her_next_contract.json", next_contract)
    write_json(RUNTIME / "a7ffcore16her_manifest.json", manifest)

    report = [
        "# CRYPTO A7FF-CORE16HER SECOND-PASS FORENSIC",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE16HER freezes CORE16HE. The second-pass probe produced enough raw candidate supply and four families, but failed concentration and H2 floor gates. A balanced pre-seed queue is possible only if H2 near-miss rows remain explicitly forensic and cannot be promoted as alpha seeds.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Source Family Summary",
        "",
        md_table(family),
        "",
        "## Balanced Queue Summary",
        "",
        md_table(queue_summary),
        "",
        "## Repair Actions",
        "",
        md_table(repair_actions),
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
