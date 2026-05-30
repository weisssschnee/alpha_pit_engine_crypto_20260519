from __future__ import annotations

import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


REPO = Path(__file__).resolve().parents[1]

ENFORCEMENT = REPO / "runtime" / "a7aif0_field_contract_enforcement_ledger" / "a7aif0_semantic_field_enforcement_ledger.csv"
RESPONSE = REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_primitive_response_map.csv"
ROLE_LEDGER = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_feature_role_ledger.csv"
A7AIF4_PROMOTED = REPO / "runtime" / "a7aif4_response_backed_field_promotion" / "a7aif4_promoted_ordinary_alpha_fields.csv"
A7AIF4_MANIFEST = REPO / "runtime" / "a7aif4_response_backed_field_promotion" / "a7aif4_manifest.json"
A7FF0_MANIFEST = REPO / "runtime" / "a7ff0_field_ontology_v2" / "a7ff0_manifest.json"
A7FF4_MANIFEST = REPO / "runtime" / "a7ff4_feature_role_promotion" / "a7ff4_manifest.json"
A7FF6_MANIFEST = REPO / "runtime" / "a7ff6_portfolio_marginal_selector_dryrun" / "a7ff6_manifest.json"
A7FF21_MANIFEST = REPO / "runtime" / "a7ff21_external_confirmation_selector" / "a7ff21_manifest.json"
A7FF22_MANIFEST = REPO / "runtime" / "a7ff22_label_balanced_expansion_contract" / "a7ff22_manifest.json"

STAGES = {
    "A7FF-R0": {
        "runtime": REPO / "runtime" / "a7ffr0_derived_generation_failure_freeze",
        "report": REPO / "reports" / "CRYPTO_A7FFR0_DERIVED_GENERATION_FAILURE_FREEZE_20260530.md",
    },
    "A7FF-R1": {
        "runtime": REPO / "runtime" / "a7ffr1_field_ontology_v3",
        "report": REPO / "reports" / "CRYPTO_A7FFR1_FIELD_ONTOLOGY_V3_20260530.md",
    },
    "A7FF-R2": {
        "runtime": REPO / "runtime" / "a7ffr2_operator_probing_v2",
        "report": REPO / "reports" / "CRYPTO_A7FFR2_OPERATOR_PROBING_V2_20260530.md",
    },
    "A7FF-R3": {
        "runtime": REPO / "runtime" / "a7ffr3_feature_pair_policy_v2",
        "report": REPO / "reports" / "CRYPTO_A7FFR3_FEATURE_PAIR_POLICY_V2_20260530.md",
    },
    "A7FF-R4": {
        "runtime": REPO / "runtime" / "a7ffr4_coarse_to_fine_generation_redesign",
        "report": REPO / "reports" / "CRYPTO_A7FFR4_COARSE_TO_FINE_GENERATION_REDESIGN_20260530.md",
    },
    "A7FF-R5": {
        "runtime": REPO / "runtime" / "a7ffr5_response_backed_promotion_redesign",
        "report": REPO / "reports" / "CRYPTO_A7FFR5_RESPONSE_BACKED_PROMOTION_REDESIGN_20260530.md",
    },
}

NON_L7 = {
    "L0_raw_forward_return",
    "L1_cross_sectional_relative_return",
    "L2_BTC_ETH_beta_residual_return",
    "L3_liquidity_tier_relative_return",
    "L4_latent_state_relative_return",
    "L5_vol_adjusted_return",
    "L6_downside_avoidance_or_crash_beta",
}


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
    safe = df.head(max_rows).copy()
    for col in safe.select_dtypes(include=["object"]).columns:
        safe[col] = safe[col].astype(str).str.replace("|", r"\|", regex=False)
    try:
        return safe.to_markdown(index=False)
    except ImportError:
        return "```text\n" + safe.to_string(index=False) + "\n```"


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def semantic_type(row: pd.Series) -> str:
    text = "|".join(
        str(row.get(col, ""))
        for col in ["field_name", "field_family", "source_family", "motif_field_family", "semantic_role"]
    ).lower()
    if any(token in text for token in ["basis", "premium", "mark_index", "mark_trade"]):
        return "basis_premium_like"
    if "funding" in text:
        return "funding_like"
    if any(token in text for token in ["open_interest", "long_short", "positioning", "taker_buy_sell"]):
        return "positioning_like"
    if any(token in text for token in ["volume", "liquidity", "notional", "trade_count"]):
        return "liquidity_like"
    if any(token in text for token in ["vol", "range"]):
        return "volatility_like"
    if any(token in text for token in ["return", "close", "price", "index", "mark"]):
        return "price_like"
    if any(token in text for token in ["meme", "multiplier", "major", "latent", "state", "age", "tier"]):
        return "state_or_taxonomy"
    return "generic_numeric"


def data_behavior(row: pd.Series) -> str:
    name = str(row.get("field_name", "")).lower()
    source = str(row.get("source_family", "")).lower()
    tags: list[str] = []
    if "funding" in source or "funding" in name:
        tags.append("interval_rate")
    if "metrics" in source or any(token in name for token in ["open_interest", "long_short", "ratio"]):
        tags.append("slow_moving")
    if any(token in name for token in ["meme", "multiplier", "age", "latent", "tier"]):
        tags.append("state_categorical")
    if any(token in name for token in ["volume", "notional", "liquidity"]):
        tags.append("activity_sensitive")
    if not tags:
        tags.append("continuous_panel")
    return "|".join(tags)


def response_features(response: pd.DataFrame) -> pd.DataFrame:
    df = response.copy()
    df["is_candidate"] = df["decision"].astype(str).eq("A7AA1_PRIMITIVE_RESPONSE_CANDIDATE")
    df["is_non_l7_candidate"] = df["is_candidate"] & df["label_family"].isin(NON_L7)
    df["control_clean"] = pd.to_numeric(df["control_ratio_premay_max"], errors="coerce").lt(1.0)
    df["control_strong"] = pd.to_numeric(df["control_ratio_premay_max"], errors="coerce").lt(0.8)
    df["lag_ok_bool"] = df["lag_ok"].map(boolish)
    return (
        df.groupby("field_name", dropna=False)
        .agg(
            response_tests=("field_name", "count"),
            primitive_candidate_count=("is_candidate", "sum"),
            non_l7_candidate_count=("is_non_l7_candidate", "sum"),
            control_clean_rows=("control_clean", "sum"),
            control_strong_rows=("control_strong", "sum"),
            lag_ok_rows=("lag_ok_bool", "sum"),
            best_control_ratio=("control_ratio_premay_max", "min"),
            best_label_families=("label_family", lambda s: ";".join(sorted(set(map(str, s.dropna()))))),
            best_transforms=("transform", lambda s: ";".join(sorted(set(map(str, s.dropna()))))),
        )
        .reset_index()
    )


def load_inputs() -> dict[str, Any]:
    return {
        "enforcement": pd.read_csv(ENFORCEMENT),
        "response": pd.read_csv(RESPONSE),
        "roles": pd.read_csv(ROLE_LEDGER),
        "promoted": pd.read_csv(A7AIF4_PROMOTED) if A7AIF4_PROMOTED.exists() else pd.DataFrame(),
        "a7aif4": read_json(A7AIF4_MANIFEST),
        "a7ff0": read_json(A7FF0_MANIFEST),
        "a7ff4": read_json(A7FF4_MANIFEST),
        "a7ff6": read_json(A7FF6_MANIFEST),
        "a7ff21": read_json(A7FF21_MANIFEST),
        "a7ff22": read_json(A7FF22_MANIFEST),
    }


def write_report(stage: str, title: str, decision: str, manifest: dict[str, Any], sections: list[tuple[str, str]]) -> None:
    report = STAGES[stage]["report"]
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title}",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
    ]
    for header, body in sections:
        lines.extend(["", f"## {header}", "", body])
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def stage_r0(inputs: dict[str, Any]) -> dict[str, Any]:
    runtime = STAGES["A7FF-R0"]["runtime"]
    runtime.mkdir(parents=True, exist_ok=True)
    evidence = pd.DataFrame(
        [
            {
                "record": "A7AI-F4",
                "decision": inputs["a7aif4"].get("decision", ""),
                "key_metric": "promoted_field_count",
                "value": inputs["a7aif4"].get("promoted_field_count", None),
                "interpretation": "ordinary alpha seed breadth insufficient",
            },
            {
                "record": "A7FF-0",
                "decision": inputs["a7ff0"].get("decision", ""),
                "key_metric": "signal_seed_candidate_count",
                "value": inputs["a7ff0"].get("signal_seed_candidate_count", None),
                "interpretation": "ontology v2 produced one primary seed",
            },
            {
                "record": "A7FF-4",
                "decision": inputs["a7ff4"].get("decision", ""),
                "key_metric": "signal_candidate_count",
                "value": inputs["a7ff4"].get("signal_candidate_count", None),
                "interpretation": "role promotion still single-family",
            },
            {
                "record": "A7FF-6",
                "decision": inputs["a7ff6"].get("decision", ""),
                "key_metric": "selected_count",
                "value": inputs["a7ff6"].get("selected_count", None),
                "interpretation": "portfolio marginal dryrun not promotable",
            },
            {
                "record": "A7FF-21",
                "decision": inputs["a7ff21"].get("decision", ""),
                "key_metric": "selected_unique_blueprints",
                "value": inputs["a7ff21"].get("selected_unique_blueprints", None),
                "interpretation": "external selector works but blueprint diversity warning remains",
            },
            {
                "record": "A7FF-22",
                "decision": inputs["a7ff22"].get("decision", ""),
                "key_metric": "generated_blueprints_target",
                "value": inputs["a7ff22"].get("generation_budget", {}).get("generated_blueprints_target", None),
                "interpretation": "expansion contract exists but should be paused before execution",
            },
        ]
    )
    decision = "HOLD_A7FF_CURRENT_DERIVED_GENERATION_INSUFFICIENT_FOR_SEARCH"
    manifest = {
        "stage": "A7FF-R0-DERIVED-GENERATION-FAILURE-FREEZE",
        "generated_at": now_utc(),
        "decision": decision,
        "a7ff23_execution_paused": True,
        "authorizes_a7ffr1": True,
        "authorizes_a7ffr2": True,
        "authorizes_a7ffr3": True,
        "authorizes_a7ffr4": True,
        "authorizes_a7ffr5": True,
        "executes_generation": False,
        "executes_search": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    evidence.to_csv(runtime / "a7ffr0_failure_evidence_matrix.csv", index=False)
    write_json(runtime / "a7ffr0_manifest.json", manifest)
    write_report(
        "A7FF-R0",
        "CRYPTO A7FF-R0 DERIVED GENERATION FAILURE FREEZE",
        decision,
        manifest,
        [
            ("Evidence Matrix", md_table(evidence)),
            (
                "Interpretation",
                "A7FF-23 is paused because the current derived feature supply is still too narrow. The failure is not materialization or numeric evaluation; it is response-backed factor breadth.",
            ),
        ],
    )
    return manifest


def stage_r1(inputs: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    runtime = STAGES["A7FF-R1"]["runtime"]
    runtime.mkdir(parents=True, exist_ok=True)
    enforcement = inputs["enforcement"].copy()
    roles = inputs["roles"][["field_name", "feature_role", "reason"]].rename(columns={"feature_role": "a7aa2_feature_role", "reason": "a7aa2_reason"})
    resp = response_features(inputs["response"])
    promoted_fields = set(inputs["promoted"].get("field_name", pd.Series(dtype=str)).astype(str))
    ontology = enforcement.merge(roles, on="field_name", how="left").merge(resp, on="field_name", how="left")
    ontology["semantic_type_v3"] = ontology.apply(semantic_type, axis=1)
    ontology["data_behavior_v3"] = ontology.apply(data_behavior, axis=1)
    ontology["response_tests"] = ontology["response_tests"].fillna(0).astype(int)
    ontology["non_l7_candidate_count"] = ontology["non_l7_candidate_count"].fillna(0).astype(int)
    ontology["primitive_candidate_count"] = ontology["primitive_candidate_count"].fillna(0).astype(int)
    ontology["compiler_role_v3"] = "blocked_or_unlicensed"
    ontology.loc[ontology["field_name"].astype(str).isin(promoted_fields), "compiler_role_v3"] = "ordinary_alpha_seed"
    ontology.loc[
        (ontology["compiler_role_v3"] != "ordinary_alpha_seed")
        & ontology["a7aa2_feature_role"].astype(str).eq("predictive_signal_candidate")
        & ontology["timing_ok"].map(boolish),
        "compiler_role_v3",
    ] = "exploratory_signal_seed"
    ontology.loc[
        (ontology["compiler_role_v3"] != "ordinary_alpha_seed")
        & (ontology["non_l7_candidate_count"] > 0)
        & ontology["timing_ok"].map(boolish),
        "compiler_role_v3",
    ] = "exploratory_signal_seed"
    ontology.loc[
        (ontology["compiler_role_v3"] == "blocked_or_unlicensed")
        & (ontology["primitive_candidate_count"] > 0)
        & ontology["timing_ok"].map(boolish),
        "compiler_role_v3",
    ] = "rank_diagnostic_seed"
    ontology.loc[
        (ontology["compiler_role_v3"] == "blocked_or_unlicensed")
        & (
            ontology["risk_defense_allowed"].map(boolish)
            | ontology["allowed_for_regime"].map(boolish)
            | ontology["allowed_for_neutralization"].map(boolish)
        )
        & ontology["timing_ok"].map(boolish),
        "compiler_role_v3",
    ] = "regime_neutralizer_interaction_seed"
    ontology.loc[
        ontology["uses_future"].map(boolish) | ontology["uses_label"].map(boolish) | ~ontology["timing_ok"].map(boolish),
        "compiler_role_v3",
    ] = "forbidden_label_future_or_timing"
    ontology["allowed_roles_v3"] = ontology["compiler_role_v3"].map(
        {
            "ordinary_alpha_seed": "signal|interaction|selector",
            "exploratory_signal_seed": "diagnostic_signal|interaction|selector_after_confirmation",
            "rank_diagnostic_seed": "rank_diagnostic|feature_probe_only",
            "regime_neutralizer_interaction_seed": "regime|neutralizer|interaction_modifier",
            "blocked_or_unlicensed": "none",
            "forbidden_label_future_or_timing": "none",
        }
    )
    summary = (
        ontology.groupby(["semantic_type_v3", "compiler_role_v3"], dropna=False)
        .size()
        .reset_index(name="field_count")
        .sort_values(["semantic_type_v3", "compiler_role_v3"])
    )
    decision = "PASS_A7FFR1_FIELD_ONTOLOGY_V3_BUILT"
    manifest = {
        "stage": "A7FF-R1-FIELD-ONTOLOGY-V3",
        "generated_at": now_utc(),
        "decision": decision,
        "field_count": int(len(ontology)),
        "semantic_type_count": int(ontology["semantic_type_v3"].nunique()),
        "ordinary_alpha_seed_count": int((ontology["compiler_role_v3"] == "ordinary_alpha_seed").sum()),
        "exploratory_signal_seed_count": int((ontology["compiler_role_v3"] == "exploratory_signal_seed").sum()),
        "regime_neutralizer_interaction_seed_count": int((ontology["compiler_role_v3"] == "regime_neutralizer_interaction_seed").sum()),
        "executes_generation": False,
        "executes_search": False,
        "authorizes_a7ffr2": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    ontology.to_csv(runtime / "a7ffr1_field_ontology_v3.csv", index=False)
    summary.to_csv(runtime / "a7ffr1_semantic_role_summary.csv", index=False)
    write_json(runtime / "a7ffr1_manifest.json", manifest)
    write_report(
        "A7FF-R1",
        "CRYPTO A7FF-R1 FIELD ONTOLOGY V3",
        decision,
        manifest,
        [("Semantic / Role Summary", md_table(summary, 120)), ("Ontology Preview", md_table(ontology[["field_name", "semantic_type_v3", "compiler_role_v3", "allowed_roles_v3", "non_l7_candidate_count", "primitive_candidate_count"]], 120))],
    )
    return ontology, manifest


def operator_family_policy(semantic: str) -> list[str]:
    return {
        "basis_premium_like": ["Delta", "ZScore", "CSRank", "HorizonSpread", "SafeDiv", "Clip", "Shock"],
        "funding_like": ["Delta", "ZScore", "Abs", "Sign", "Persistence", "CSRank"],
        "positioning_like": ["Delta", "ZScore", "Persistence", "Shock", "CSRank", "HorizonSpread"],
        "liquidity_like": ["Delta", "ZScore", "Shock", "Persistence", "CSRank", "WithinLiquidityTierRank"],
        "volatility_like": ["Delta", "ZScore", "Shock", "CSRank", "HorizonSpread"],
        "price_like": ["Delta", "ZScore", "TSRank", "CSRank", "HorizonSpread"],
        "state_or_taxonomy": ["WithinGroupRank", "RegimeMask", "Neutralize", "InteractionOnly"],
        "generic_numeric": ["Delta", "ZScore", "CSRank"],
    }.get(semantic, ["Delta", "ZScore", "CSRank"])


def transform_to_operator(transform: str) -> str:
    t = str(transform).lower()
    if "delta" in t:
        return "Delta"
    if "zscore" in t:
        return "ZScore"
    if "cs_rank" in t or t == "rank":
        return "CSRank"
    if "tsrank" in t:
        return "TSRank"
    if "shock" in t:
        return "Shock"
    if "persistence" in t:
        return "Persistence"
    if "spread" in t:
        return "HorizonSpread"
    return "Identity"


def stage_r2(inputs: dict[str, Any], ontology: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    runtime = STAGES["A7FF-R2"]["runtime"]
    runtime.mkdir(parents=True, exist_ok=True)
    response = inputs["response"].copy()
    response["operator"] = response["transform"].map(transform_to_operator)
    response["is_candidate"] = response["decision"].astype(str).eq("A7AA1_PRIMITIVE_RESPONSE_CANDIDATE")
    response["is_non_l7_candidate"] = response["is_candidate"] & response["label_family"].isin(NON_L7)
    response = response.merge(ontology[["field_name", "semantic_type_v3", "compiler_role_v3"]], on="field_name", how="left")
    observed = (
        response.groupby(["semantic_type_v3", "operator"], dropna=False)
        .agg(
            tests=("field_name", "count"),
            candidate_rows=("is_candidate", "sum"),
            non_l7_candidate_rows=("is_non_l7_candidate", "sum"),
            median_control_ratio=("control_ratio_premay_max", "median"),
            min_control_ratio=("control_ratio_premay_max", "min"),
        )
        .reset_index()
    )
    rows: list[dict[str, Any]] = []
    for semantic in sorted(ontology["semantic_type_v3"].dropna().unique()):
        for operator in operator_family_policy(semantic):
            obs = observed[(observed["semantic_type_v3"] == semantic) & (observed["operator"] == operator)]
            payload = {
                "semantic_type_v3": semantic,
                "operator": operator,
                "tests": int(obs["tests"].iloc[0]) if not obs.empty else 0,
                "candidate_rows": int(obs["candidate_rows"].iloc[0]) if not obs.empty else 0,
                "non_l7_candidate_rows": int(obs["non_l7_candidate_rows"].iloc[0]) if not obs.empty else 0,
                "median_control_ratio": float(obs["median_control_ratio"].iloc[0]) if not obs.empty and pd.notna(obs["median_control_ratio"].iloc[0]) else None,
                "operator_policy_v2": "probe_required",
            }
            if payload["non_l7_candidate_rows"] > 0 and (payload["median_control_ratio"] is None or payload["median_control_ratio"] < 1.0):
                payload["operator_policy_v2"] = "promote_for_generation"
            elif payload["candidate_rows"] > 0:
                payload["operator_policy_v2"] = "diagnostic_only"
            rows.append(payload)
    policy = pd.DataFrame(rows)
    decision = "PASS_A7FFR2_OPERATOR_PROBING_V2_READY"
    manifest = {
        "stage": "A7FF-R2-OPERATOR-PROBING-V2",
        "generated_at": now_utc(),
        "decision": decision,
        "policy_rows": int(len(policy)),
        "promote_operator_rows": int((policy["operator_policy_v2"] == "promote_for_generation").sum()),
        "probe_required_rows": int((policy["operator_policy_v2"] == "probe_required").sum()),
        "executes_generation": False,
        "executes_search": False,
        "authorizes_a7ffr3": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    observed.to_csv(runtime / "a7ffr2_observed_operator_response.csv", index=False)
    policy.to_csv(runtime / "a7ffr2_operator_probe_policy.csv", index=False)
    write_json(runtime / "a7ffr2_manifest.json", manifest)
    write_report(
        "A7FF-R2",
        "CRYPTO A7FF-R2 OPERATOR PROBING V2",
        decision,
        manifest,
        [("Operator Policy", md_table(policy, 120)), ("Observed Operator Response", md_table(observed, 120))],
    )
    return policy, manifest


def pair_priority(left: pd.Series, right: pd.Series) -> str:
    pair = "|".join(sorted([str(left["semantic_type_v3"]), str(right["semantic_type_v3"])]))
    if "forbidden" in str(left["compiler_role_v3"]) or "forbidden" in str(right["compiler_role_v3"]):
        return "forbidden"
    if left["compiler_role_v3"] in {"ordinary_alpha_seed", "exploratory_signal_seed"} and right["compiler_role_v3"] in {"regime_neutralizer_interaction_seed", "exploratory_signal_seed", "ordinary_alpha_seed"}:
        return "allow_high_priority"
    if pair in {
        "basis_premium_like|positioning_like",
        "basis_premium_like|volatility_like",
        "basis_premium_like|price_like",
        "basis_premium_like|funding_like",
        "funding_like|positioning_like",
        "liquidity_like|volatility_like",
    }:
        return "probe_high_priority"
    return "diagnostic_or_low_priority"


def stage_r3(ontology: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    runtime = STAGES["A7FF-R3"]["runtime"]
    runtime.mkdir(parents=True, exist_ok=True)
    seed_roles = {"ordinary_alpha_seed", "exploratory_signal_seed", "regime_neutralizer_interaction_seed", "rank_diagnostic_seed"}
    seeds = ontology[ontology["compiler_role_v3"].isin(seed_roles)].copy()
    rows: list[dict[str, Any]] = []
    for _, left in seeds.iterrows():
        for _, right in seeds.iterrows():
            if str(left["field_name"]) >= str(right["field_name"]):
                continue
            priority = pair_priority(left, right)
            rows.append(
                {
                    "left_field": left["field_name"],
                    "right_field": right["field_name"],
                    "left_semantic_type": left["semantic_type_v3"],
                    "right_semantic_type": right["semantic_type_v3"],
                    "semantic_pair": "|".join(sorted([str(left["semantic_type_v3"]), str(right["semantic_type_v3"])])),
                    "left_role": left["compiler_role_v3"],
                    "right_role": right["compiler_role_v3"],
                    "pair_policy_v2": priority,
                }
            )
    pairs = pd.DataFrame(rows)
    summary = pairs.groupby(["semantic_pair", "pair_policy_v2"], dropna=False).size().reset_index(name="pair_count").sort_values("pair_count", ascending=False) if not pairs.empty else pd.DataFrame()
    decision = "PASS_A7FFR3_FEATURE_PAIR_POLICY_READY" if not pairs.empty else "HOLD_A7FFR3_NO_FEATURE_PAIRS"
    manifest = {
        "stage": "A7FF-R3-FEATURE-PAIR-POLICY-V2",
        "generated_at": now_utc(),
        "decision": decision,
        "seed_field_count": int(len(seeds)),
        "pair_count": int(len(pairs)),
        "allow_high_priority_pairs": int((pairs["pair_policy_v2"] == "allow_high_priority").sum()) if not pairs.empty else 0,
        "probe_high_priority_pairs": int((pairs["pair_policy_v2"] == "probe_high_priority").sum()) if not pairs.empty else 0,
        "executes_generation": False,
        "executes_search": False,
        "authorizes_a7ffr4": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    pairs.to_csv(runtime / "a7ffr3_feature_pair_policy_v2.csv", index=False)
    summary.to_csv(runtime / "a7ffr3_pair_policy_summary.csv", index=False)
    write_json(runtime / "a7ffr3_manifest.json", manifest)
    write_report(
        "A7FF-R3",
        "CRYPTO A7FF-R3 FEATURE PAIR POLICY V2",
        decision,
        manifest,
        [("Pair Policy Summary", md_table(summary, 120)), ("Pair Policy Preview", md_table(pairs, 120))],
    )
    return pairs, manifest


def stage_r4(pairs: pd.DataFrame, operator_policy: pd.DataFrame) -> dict[str, Any]:
    runtime = STAGES["A7FF-R4"]["runtime"]
    runtime.mkdir(parents=True, exist_ok=True)
    allowed_pairs = pairs[pairs["pair_policy_v2"].isin(["allow_high_priority", "probe_high_priority"])].copy()
    generation_levels = pd.DataFrame(
        [
            {"level": "L1_single_field_transform", "budget": 2400, "source": "ontology_v3 + operator_policy_v2", "gate": "operator_policy_v2 != block"},
            {"level": "L2_typed_two_field_interaction", "budget": 4800, "source": "feature_pair_policy_v2", "gate": "allow_high_priority or probe_high_priority"},
            {"level": "L3_state_conditioned_feature", "budget": 1600, "source": "regime_neutralizer_interaction_seed", "gate": "state field may condition but not become standalone alpha"},
            {"level": "L4_factor_candidate", "budget": 800, "source": "response-backed generated features", "gate": "non-L7, control-clean, cost/lag robust"},
        ]
    )
    operator_budget = operator_policy.groupby("operator_policy_v2").size().reset_index(name="rows").sort_values("rows", ascending=False)
    decision = "PASS_A7FFR4_COARSE_TO_FINE_GENERATION_REDESIGN_READY"
    manifest = {
        "stage": "A7FF-R4-COARSE-TO-FINE-GENERATION-REDESIGN",
        "generated_at": now_utc(),
        "decision": decision,
        "allowed_or_probe_pair_count": int(len(allowed_pairs)),
        "generation_budget_total": int(generation_levels["budget"].sum()),
        "executes_generation": False,
        "executes_search": False,
        "authorizes_a7ffr5": True,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    allowed_pairs.to_csv(runtime / "a7ffr4_allowed_generation_pairs.csv", index=False)
    generation_levels.to_csv(runtime / "a7ffr4_generation_levels.csv", index=False)
    operator_budget.to_csv(runtime / "a7ffr4_operator_budget_summary.csv", index=False)
    write_json(runtime / "a7ffr4_manifest.json", manifest)
    write_report(
        "A7FF-R4",
        "CRYPTO A7FF-R4 COARSE TO FINE GENERATION REDESIGN",
        decision,
        manifest,
        [("Generation Levels", md_table(generation_levels)), ("Allowed Pair Preview", md_table(allowed_pairs, 120)), ("Operator Budget Summary", md_table(operator_budget))],
    )
    return manifest


def stage_r5(ontology: pd.DataFrame, pairs: pd.DataFrame) -> dict[str, Any]:
    runtime = STAGES["A7FF-R5"]["runtime"]
    runtime.mkdir(parents=True, exist_ok=True)
    promotion_gates = pd.DataFrame(
        [
            {"gate": "non_l7_label_evidence", "threshold": ">=1 non-L7 candidate row", "hard": True},
            {"gate": "control_clean", "threshold": "control_ratio < 0.80 for promotion; <1.0 for diagnostic", "hard": True},
            {"gate": "lag_and_timing", "threshold": "lag_ok and timing_ok", "hard": True},
            {"gate": "cost_survival", "threshold": "cost5-or-better for diagnostic; cost10 preferred", "hard": False},
            {"gate": "role_integrity", "threshold": "risk/regime fields cannot become standalone alpha", "hard": True},
            {"gate": "field_family_breadth", "threshold": ">=3 semantic families before search authorization", "hard": True},
            {"gate": "selector_policy", "threshold": "external label-balanced selector only", "hard": True},
        ]
    )
    seed_preview = ontology[ontology["compiler_role_v3"].isin(["ordinary_alpha_seed", "exploratory_signal_seed", "regime_neutralizer_interaction_seed"])][
        ["field_name", "semantic_type_v3", "compiler_role_v3", "non_l7_candidate_count", "primitive_candidate_count", "best_control_ratio", "allowed_roles_v3"]
    ].copy()
    semantic_families = int(seed_preview[seed_preview["compiler_role_v3"].isin(["ordinary_alpha_seed", "exploratory_signal_seed"])]["semantic_type_v3"].nunique())
    decision = (
        "PASS_A7FFR5_PROMOTION_REDESIGN_READY_BUT_SEARCH_STILL_HOLD"
        if semantic_families >= 2
        else "HOLD_A7FFR5_INSUFFICIENT_SIGNAL_FAMILY_BREADTH"
    )
    manifest = {
        "stage": "A7FF-R5-RESPONSE-BACKED-PROMOTION-REDESIGN",
        "generated_at": now_utc(),
        "decision": decision,
        "seed_preview_rows": int(len(seed_preview)),
        "signal_semantic_family_count": semantic_families,
        "pair_policy_rows": int(len(pairs)),
        "executes_generation": False,
        "executes_search": False,
        "authorizes_a7ff23r_contract": decision.startswith("PASS"),
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    promotion_gates.to_csv(runtime / "a7ffr5_promotion_gates.csv", index=False)
    seed_preview.to_csv(runtime / "a7ffr5_seed_preview.csv", index=False)
    write_json(runtime / "a7ffr5_manifest.json", manifest)
    write_report(
        "A7FF-R5",
        "CRYPTO A7FF-R5 RESPONSE BACKED PROMOTION REDESIGN",
        decision,
        manifest,
        [("Promotion Gates", md_table(promotion_gates)), ("Seed Preview", md_table(seed_preview, 120))],
    )
    return manifest


def main() -> None:
    inputs = load_inputs()
    r0 = stage_r0(inputs)
    ontology, r1 = stage_r1(inputs)
    operator_policy, r2 = stage_r2(inputs, ontology)
    pairs, r3 = stage_r3(ontology)
    r4 = stage_r4(pairs, operator_policy)
    r5 = stage_r5(ontology, pairs)
    print(
        json.dumps(
            {
                "A7FF-R0": r0["decision"],
                "A7FF-R1": r1["decision"],
                "A7FF-R2": r2["decision"],
                "A7FF-R3": r3["decision"],
                "A7FF-R4": r4["decision"],
                "A7FF-R5": r5["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
