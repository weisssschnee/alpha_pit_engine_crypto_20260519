from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE51PX = REPO / "runtime" / "a7ffcore51px_company_sharded_replay_runner_contract"
CORE52 = REPO / "runtime" / "a7ffcore52_company_replay_arbitration"
CORE53 = REPO / "runtime" / "a7ffcore53_replay_target_repair_contract"
A7FF_VERSION = REPO / "runtime" / "a7ff_version_20260530"
RUNTIME = REPO / "runtime" / "a7ffcore53i_factor_input_information_audit"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE53I_FACTOR_INPUT_INFORMATION_AUDIT_20260603.md"


FIELD_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b")
FUNCTION_TOKENS = {
    "Abs",
    "Add",
    "Clip",
    "CSRank",
    "Decay",
    "Delta",
    "Identity",
    "Mean",
    "Mul",
    "Neg",
    "Rank",
    "SafeDiv",
    "Sign",
    "SignedRankDelta",
    "SpreadShortLong",
    "Sub",
    "TSRank",
    "WinsorZ",
    "ZScore",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: dict) -> None:
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


def parse_fields(expression: str, known_fields: set[str]) -> list[str]:
    out = []
    for token in FIELD_RE.findall(str(expression)):
        if token in FUNCTION_TOKENS:
            continue
        if token in known_fields:
            out.append(token)
    return sorted(set(out))


def field_type(field: str) -> str:
    name = field.lower()
    if "basis" in name or "premium" in name:
        return "basis_premium_like"
    if "funding" in name:
        return "funding_like"
    if "open_interest" in name or "long_short" in name or "position" in name:
        return "positioning_like"
    if "taker" in name or "trade_count" in name or "volume" in name or "liquidity" in name or "coverage" in name or "gap" in name:
        return "liquidity_like"
    if "vol" in name:
        return "volatility_like"
    if "age" in name or "source_" in name or "split" in name:
        return "state_or_taxonomy"
    if "close" in name or "open" in name or "high" in name or "low" in name or "return" in name or "price" in name or "mark_" in name or "index_" in name:
        return "price_like"
    return "generic_numeric"


def skeleton(expression: str) -> str:
    return re.sub(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", lambda m: "F" if m.group(0) not in FUNCTION_TOKENS else m.group(0), str(expression))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE53 / "a7ffcore53_manifest.json")
    if source.get("decision") != "PASS_A7FFCORE53_REPLAY_TARGET_REPAIR_CONTRACT_READY_FOR_CORE53E":
        raise SystemExit(f"CORE53 is not ready for CORE53I: {source.get('decision')}")

    queue = pd.read_csv(CORE51PX / "a7ffcore51px_selected_candidate_queue.csv")
    seed_arbitration = pd.read_csv(CORE52 / "a7ffcore52_seed_arbitration.csv")
    version_fields = pd.read_csv(A7FF_VERSION / "a7ff_v20260530_base_field_usage.csv")
    compact_contract = pd.read_csv(CORE51PX / "a7ffcore51px_compact_frame_contract.csv")
    known_fields = set(version_fields["base_field"].dropna().astype(str))
    known_fields |= set(compact_contract["field_name"].dropna().astype(str))
    for col in ["semantic_pair", "operator"]:
        if col not in queue.columns and col in seed_arbitration.columns:
            queue = queue.merge(seed_arbitration[["seed_id", col]], on="seed_id", how="left")
    enriched = queue.merge(
        seed_arbitration[
            [
                "seed_id",
                "arbitration_status",
                "clean_label_count",
                "clean_horizons",
                "min_control_ratio",
                "median_control_ratio",
                "max_original_spread",
            ]
        ],
        on="seed_id",
        how="left",
    )
    enriched["input_fields"] = enriched["expression"].map(lambda x: parse_fields(x, known_fields))
    enriched["input_field_count"] = enriched["input_fields"].map(len)
    enriched["input_field_key"] = enriched["input_fields"].map(lambda xs: "|".join(xs))
    enriched["input_type_set"] = enriched["input_fields"].map(lambda xs: sorted({field_type(x) for x in xs}))
    enriched["input_type_key"] = enriched["input_type_set"].map(lambda xs: "|".join(xs))
    enriched["expression_skeleton"] = enriched["expression"].map(skeleton)
    enriched["factor_input_status"] = "accepted_input"

    top_field_counter: Counter[str] = Counter()
    for fields in enriched["input_fields"]:
        top_field_counter.update(fields)
    field_usage = pd.DataFrame(
        [{"field": field, "candidate_count": count, "field_type": field_type(field)} for field, count in top_field_counter.items()]
    ).sort_values(["candidate_count", "field"], ascending=[False, True])
    field_usage["candidate_share"] = field_usage["candidate_count"] / max(1, len(enriched))

    type_usage = (
        enriched.explode("input_type_set")
        .groupby("input_type_set", as_index=False)
        .agg(candidate_count=("seed_id", "nunique"))
        .rename(columns={"input_type_set": "field_type"})
        .sort_values("candidate_count", ascending=False)
    )
    type_usage["candidate_share"] = type_usage["candidate_count"] / max(1, len(enriched))

    field_set_summary = (
        enriched.groupby("input_field_key", as_index=False)
        .agg(
            candidate_count=("seed_id", "count"),
            diagnostic_clue_count=("arbitration_status", lambda s: int(s.isin(["diagnostic_clue", "strict_replay_clue"]).sum())),
            strict_clue_count=("arbitration_status", lambda s: int((s == "strict_replay_clue").sum())),
            median_control_ratio=("median_control_ratio", "median"),
            median_clean_label_count=("clean_label_count", "median"),
            example_expression=("expression", "first"),
        )
        .sort_values(["candidate_count", "diagnostic_clue_count"], ascending=False)
    )
    type_set_summary = (
        enriched.groupby("input_type_key", as_index=False)
        .agg(
            candidate_count=("seed_id", "count"),
            diagnostic_clue_count=("arbitration_status", lambda s: int(s.isin(["diagnostic_clue", "strict_replay_clue"]).sum())),
            strict_clue_count=("arbitration_status", lambda s: int((s == "strict_replay_clue").sum())),
            median_control_ratio=("median_control_ratio", "median"),
            semantic_pair_count=("semantic_pair", "nunique"),
            operator_count=("operator", "nunique"),
        )
        .sort_values(["candidate_count", "diagnostic_clue_count"], ascending=False)
    )
    skeleton_summary = (
        enriched.groupby("expression_skeleton", as_index=False)
        .agg(
            candidate_count=("seed_id", "count"),
            input_field_set_count=("input_field_key", "nunique"),
            diagnostic_clue_count=("arbitration_status", lambda s: int(s.isin(["diagnostic_clue", "strict_replay_clue"]).sum())),
            example_expression=("expression", "first"),
        )
        .sort_values(["candidate_count", "diagnostic_clue_count"], ascending=False)
    )

    clue = enriched.loc[enriched["arbitration_status"].isin(["diagnostic_clue", "strict_replay_clue"])].copy()
    clue_pairs = []
    clue_rows = clue[["seed_id", "input_fields", "input_type_key", "expression_skeleton", "semantic_pair", "operator"]].to_dict("records")
    for i, left in enumerate(clue_rows):
        left_fields = set(left["input_fields"])
        for right in clue_rows[i + 1 :]:
            sim = jaccard(left_fields, set(right["input_fields"]))
            same_type = left["input_type_key"] == right["input_type_key"]
            same_skeleton = left["expression_skeleton"] == right["expression_skeleton"]
            if sim >= 0.5 or same_type or same_skeleton:
                clue_pairs.append(
                    {
                        "seed_id_left": left["seed_id"],
                        "seed_id_right": right["seed_id"],
                        "field_jaccard": sim,
                        "same_input_type_key": same_type,
                        "same_skeleton": same_skeleton,
                        "left_semantic_pair": left["semantic_pair"],
                        "right_semantic_pair": right["semantic_pair"],
                        "left_operator": left["operator"],
                        "right_operator": right["operator"],
                    }
                )
    clue_pair_df = pd.DataFrame(clue_pairs).sort_values(
        ["field_jaccard", "same_input_type_key", "same_skeleton"], ascending=[False, False, False]
    ) if clue_pairs else pd.DataFrame()

    top_field_share = float(field_usage["candidate_share"].max()) if not field_usage.empty else 0.0
    top_type_share = float(type_usage["candidate_share"].max()) if not type_usage.empty else 0.0
    top_field_set_share = float(field_set_summary["candidate_count"].max() / max(1, len(enriched))) if not field_set_summary.empty else 0.0
    diagnostic_type_count = int(clue["input_type_key"].nunique())
    diagnostic_field_set_count = int(clue["input_field_key"].nunique())
    strict_type_count = int(clue.loc[clue["arbitration_status"].eq("strict_replay_clue"), "input_type_key"].nunique())
    blockers = []
    if top_type_share > 0.55:
        blockers.append("top_input_type_dominates")
    if top_field_share > 0.45:
        blockers.append("top_base_field_dominates")
    if diagnostic_type_count < 6:
        blockers.append("diagnostic_input_type_breadth_low")
    if strict_type_count < 3:
        blockers.append("strict_input_type_breadth_low")
    decision = "HOLD_A7FFCORE53I_FACTOR_INPUT_REDUNDANCY_RISK" if blockers else "PASS_A7FFCORE53I_FACTOR_INPUT_BREADTH_ACCEPTABLE"

    enriched_out = enriched.copy()
    enriched_out["input_fields"] = enriched_out["input_fields"].map(lambda xs: "|".join(xs))
    enriched_out["input_type_set"] = enriched_out["input_type_set"].map(lambda xs: "|".join(xs))
    enriched_out.to_csv(RUNTIME / "a7ffcore53i_candidate_input_lineage.csv", index=False)
    field_usage.to_csv(RUNTIME / "a7ffcore53i_base_field_usage.csv", index=False)
    type_usage.to_csv(RUNTIME / "a7ffcore53i_field_type_usage.csv", index=False)
    field_set_summary.to_csv(RUNTIME / "a7ffcore53i_field_set_redundancy.csv", index=False)
    type_set_summary.to_csv(RUNTIME / "a7ffcore53i_input_type_redundancy.csv", index=False)
    skeleton_summary.to_csv(RUNTIME / "a7ffcore53i_skeleton_redundancy.csv", index=False)
    clue_pair_df.to_csv(RUNTIME / "a7ffcore53i_clue_pair_overlap.csv", index=False)
    manifest = {
        "stage": "A7FF-CORE53I",
        "generated_at": now_utc(),
        "source_stage": source.get("stage"),
        "source_decision": source.get("decision"),
        "decision": decision,
        "candidate_count": int(enriched.shape[0]),
        "diagnostic_clue_count": int(clue.shape[0]),
        "strict_clue_count": int(clue["arbitration_status"].eq("strict_replay_clue").sum()) if not clue.empty else 0,
        "base_field_count": int(field_usage.shape[0]),
        "input_type_count": int(type_usage.shape[0]),
        "diagnostic_input_type_count": diagnostic_type_count,
        "diagnostic_field_set_count": diagnostic_field_set_count,
        "strict_input_type_count": strict_type_count,
        "top_base_field_share": top_field_share,
        "top_input_type_share": top_type_share,
        "top_input_field_set_share": top_field_set_share,
        "blockers": blockers,
        "executes_replay": False,
        "executes_search": False,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "authorizes_core53e_preflight": decision.startswith("PASS_"),
        "authorizes_factor_input_repair": bool(blockers),
    }
    authorization = {
        "authorized": {
            "A7FF-CORE53IR factor input repair contract": bool(blockers),
            "A7FF-CORE53E repaired target preflight": decision.startswith("PASS_"),
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "alpha_proof": True,
            "promotion": True,
            "shadow_paper_live": True,
        },
    }
    write_json(RUNTIME / "a7ffcore53i_manifest.json", manifest)
    write_json(RUNTIME / "a7ffcore53i_authorization_matrix.json", authorization)

    report = [
        "# CRYPTO A7FF-CORE53I FACTOR INPUT INFORMATION AUDIT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "CORE53I audits factor input information overlap before repaired-target replay. It does not execute replay, generation, search, proof, or promotion.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Base Field Usage",
        "",
        md_table(field_usage, 40),
        "",
        "## Field Type Usage",
        "",
        md_table(type_usage, 40),
        "",
        "## Input Type Redundancy",
        "",
        md_table(type_set_summary, 60),
        "",
        "## Field Set Redundancy",
        "",
        md_table(field_set_summary, 60),
        "",
        "## Skeleton Redundancy",
        "",
        md_table(skeleton_summary, 40),
        "",
        "## Clue Pair Overlap",
        "",
        md_table(clue_pair_df, 80),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
