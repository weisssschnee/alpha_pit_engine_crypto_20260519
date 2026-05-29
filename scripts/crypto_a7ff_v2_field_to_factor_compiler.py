from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


REPO = Path(__file__).resolve().parents[1]

ENFORCEMENT = REPO / "runtime" / "a7aif0_field_contract_enforcement_ledger" / "a7aif0_semantic_field_enforcement_ledger.csv"
RESPONSE = REPO / "runtime" / "a7aa1_primitive_response_map" / "a7aa1_primitive_response_map.csv"
ROLE_LEDGER = REPO / "runtime" / "a7aa2_feature_role_classification" / "a7aa2_feature_role_ledger.csv"
F4_PROMOTED = REPO / "runtime" / "a7aif4_response_backed_field_promotion" / "a7aif4_promoted_ordinary_alpha_fields.csv"
F4_MANIFEST = REPO / "runtime" / "a7aif4_response_backed_field_promotion" / "a7aif4_manifest.json"

STAGES = {
    "A7FF-0": {
        "runtime": REPO / "runtime" / "a7ff0_field_ontology_v2",
        "report": REPO / "reports" / "CRYPTO_A7FF0_FIELD_ONTOLOGY_V2_20260530.md",
    },
    "A7FF-1": {
        "runtime": REPO / "runtime" / "a7ff1_operator_probing",
        "report": REPO / "reports" / "CRYPTO_A7FF1_OPERATOR_PROBING_20260530.md",
    },
    "A7FF-2": {
        "runtime": REPO / "runtime" / "a7ff2_feature_pair_clustering",
        "report": REPO / "reports" / "CRYPTO_A7FF2_FEATURE_PAIR_CLUSTERING_20260530.md",
    },
    "A7FF-3": {
        "runtime": REPO / "runtime" / "a7ff3_coarse_to_fine_generation_contract",
        "report": REPO / "reports" / "CRYPTO_A7FF3_COARSE_TO_FINE_GENERATION_CONTRACT_20260530.md",
    },
    "A7FF-4": {
        "runtime": REPO / "runtime" / "a7ff4_feature_role_promotion",
        "report": REPO / "reports" / "CRYPTO_A7FF4_FEATURE_ROLE_PROMOTION_20260530.md",
    },
    "A7FF-5": {
        "runtime": REPO / "runtime" / "a7ff5_factor_candidate_compiler",
        "report": REPO / "reports" / "CRYPTO_A7FF5_FACTOR_CANDIDATE_COMPILER_20260530.md",
    },
    "A7FF-6": {
        "runtime": REPO / "runtime" / "a7ff6_portfolio_marginal_selector_dryrun",
        "report": REPO / "reports" / "CRYPTO_A7FF6_PORTFOLIO_MARGINAL_SELECTOR_DRYRUN_20260530.md",
    },
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(prefix: str, text: str) -> str:
    return f"{prefix}_{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    view = df.head(max_rows).copy()
    for col in view.columns:
        if view[col].dtype == object:
            view[col] = view[col].astype(str).str.replace("|", "\\|", regex=False)
    return view.to_markdown(index=False)


def semantic_type(row: pd.Series) -> str:
    text = "|".join(
        str(row.get(col, ""))
        for col in ["field_name", "field_family", "source_family", "motif_field_family", "semantic_role"]
    ).lower()
    if any(token in text for token in ["basis", "premium", "mark_index"]):
        return "basis_premium_like"
    if "funding" in text:
        return "rate_like"
    if any(token in text for token in ["open_interest", "long_short", "positioning", "taker_buy_sell"]):
        return "positioning_like"
    if any(token in text for token in ["volume", "liquidity", "notional", "trade_count"]):
        return "liquidity_like"
    if any(token in text for token in ["vol", "range"]):
        return "volatility_like"
    if any(token in text for token in ["return", "close", "price", "index", "mark"]):
        return "price_like"
    if any(token in text for token in ["meme", "multiplier", "major", "latent", "state", "age"]):
        return "categorical_state"
    return "generic_numeric"


def data_behavior(row: pd.Series) -> str:
    tags: list[str] = []
    source = str(row.get("source_family", "")).lower()
    name = str(row.get("field_name", "")).lower()
    role = str(row.get("semantic_role", "")).lower()
    if "funding" in source or "funding" in name:
        tags.append("event_or_interval_rate")
    if "metrics" in source or any(token in name for token in ["open_interest", "long_short", "ratio"]):
        tags.append("slow_moving")
    if any(token in name for token in ["meme", "multiplier", "major", "age", "latent"]):
        tags.append("listing_or_taxonomy_sensitive")
    if "risk_exposure" in role:
        tags.append("risk_exposure_sensitive")
    if not tags:
        tags.append("continuous_panel")
    return "|".join(tags)


def operator_from_transform(transform: str) -> str:
    mapping = {
        "level": "Identity",
        "cs_rank": "CSRank",
        "delta_24h": "Delta",
        "delta_4h": "Delta",
        "zscore": "ZScore",
        "rank": "CSRank",
        "tsrank": "TSRank",
        "persistence": "Persistence",
        "shock": "Shock",
        "spread_short_long": "HorizonSpread",
    }
    return mapping.get(str(transform), str(transform))


def response_score(row: pd.Series) -> float:
    control = pd.to_numeric(row.get("control_ratio_premay_max"), errors="coerce")
    control_margin = 0.0 if pd.isna(control) else max(0.0, 1.0 - float(control))
    nonoverlap = abs(pd.to_numeric(row.get("recent_oos_2026JanApr_nonoverlap_min_tstat"), errors="coerce"))
    nonoverlap_score = 0.0 if pd.isna(nonoverlap) else min(float(nonoverlap) / 5.0, 2.0)
    return (
        (1.0 if str(row.get("decision")) == "A7AA1_PRIMITIVE_RESPONSE_CANDIDATE" else 0.0)
        + (1.0 if str(row.get("label_family")) != "L7_ranked_future_return" else 0.0)
        + (1.0 if truthy(row.get("premay_all_positive")) else 0.0)
        + (0.5 if truthy(row.get("lag_ok")) else 0.0)
        + control_margin
        + nonoverlap_score
    )


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0 or np.allclose(a, a[0]) or np.allclose(b, b[0]):
        return 0.0
    value = np.corrcoef(a, b)[0, 1]
    if math.isnan(value):
        return 0.0
    return float(value)


def write_report(stage: str, decision: str, manifest: dict[str, Any], sections: list[tuple[str, str]]) -> None:
    report = STAGES[stage]["report"]
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# CRYPTO {stage} FIELD-TO-FACTOR COMPILER",
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
    for title, body in sections:
        lines.extend(["", f"## {title}", "", body])
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_ontology(enforcement: pd.DataFrame, roles: pd.DataFrame, response: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    field_response = (
        response.groupby("field_name")
        .agg(
            response_test_count=("field_name", "size"),
            primitive_candidate_count=("decision", lambda s: int((s == "A7AA1_PRIMITIVE_RESPONSE_CANDIDATE").sum())),
            non_l7_candidate_count=("label_family", lambda s: int(((response.loc[s.index, "decision"] == "A7AA1_PRIMITIVE_RESPONSE_CANDIDATE") & (s != "L7_ranked_future_return")).sum())),
            min_control_ratio=("control_ratio_premay_max", "min"),
            median_control_ratio=("control_ratio_premay_max", "median"),
        )
        .reset_index()
    )
    ontology = enforcement.merge(
        roles[["field_name", "feature_role", "reason"]].rename(columns={"feature_role": "a7aa2_feature_role"}),
        on="field_name",
        how="left",
    ).merge(field_response, on="field_name", how="left")
    ontology["semantic_type"] = ontology.apply(semantic_type, axis=1)
    ontology["data_behavior"] = ontology.apply(data_behavior, axis=1)
    ontology["compiler_role"] = "forbidden_or_unlicensed"
    ontology.loc[ontology["enforcement_status"].eq("OK_ORDINARY_ALPHA"), "compiler_role"] = "signal_seed_candidate"
    ontology.loc[ontology["semantic_role"].astype(str).str.contains("risk_exposure", na=False), "compiler_role"] = "risk_exposure_or_neutralizer"
    ontology.loc[ontology["semantic_role"].astype(str).str.contains("regime|diagnostic|unclassified", na=False), "compiler_role"] = "regime_or_diagnostic_input"
    ontology.loc[ontology["uses_future"].apply(truthy) | ontology["uses_label"].apply(truthy), "compiler_role"] = "forbidden_label_or_future"
    ontology["allowed_operator_groups"] = ontology["semantic_type"].map(
        {
            "basis_premium_like": "Identity|Delta|ZScore|CSRank|HorizonSpread|Clip",
            "rate_like": "Identity|Delta|ZScore|Abs|Sign|Persistence",
            "positioning_like": "Identity|Delta|ZScore|CSRank|Persistence|Shock",
            "liquidity_like": "Identity|Delta|ZScore|CSRank|Shock|Persistence",
            "volatility_like": "Identity|Delta|ZScore|CSRank|Shock",
            "price_like": "Delta|ZScore|CSRank|TSRank|HorizonSpread",
            "categorical_state": "GroupRank|Neutralize|RegimeMask",
            "generic_numeric": "Identity|Delta|ZScore|CSRank",
        }
    ).fillna("Identity|Delta|ZScore|CSRank")
    summary = {
        "stage": "A7FF-0",
        "generated_at": now_utc(),
        "decision": "PASS_A7FF0_FIELD_ONTOLOGY_V2_BUILT",
        "field_count": int(len(ontology)),
        "semantic_type_count": int(ontology["semantic_type"].nunique()),
        "signal_seed_candidate_count": int((ontology["compiler_role"] == "signal_seed_candidate").sum()),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    return ontology, summary


def operator_probe(response: pd.DataFrame, ontology: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    frame = response.copy()
    frame["operator"] = frame["transform"].map(operator_from_transform)
    frame["score"] = frame.apply(response_score, axis=1)
    frame = frame.merge(ontology[["field_name", "semantic_type", "compiler_role"]], on="field_name", how="left")
    probe = (
        frame.groupby(["semantic_type", "operator"], dropna=False)
        .agg(
            test_count=("field_name", "size"),
            candidate_count=("decision", lambda s: int((s == "A7AA1_PRIMITIVE_RESPONSE_CANDIDATE").sum())),
            non_l7_candidate_count=("label_family", lambda s: int(((frame.loc[s.index, "decision"] == "A7AA1_PRIMITIVE_RESPONSE_CANDIDATE") & (s != "L7_ranked_future_return")).sum())),
            median_control_ratio=("control_ratio_premay_max", "median"),
            min_control_ratio=("control_ratio_premay_max", "min"),
            mean_score=("score", "mean"),
            max_score=("score", "max"),
        )
        .reset_index()
    )
    probe["operator_policy"] = "block_or_low_priority"
    probe.loc[(probe["candidate_count"] > 0) & (probe["median_control_ratio"] < 1.0), "operator_policy"] = "diagnostic_probe_only"
    probe.loc[(probe["non_l7_candidate_count"] > 0) & (probe["min_control_ratio"] < 0.8), "operator_policy"] = "allow_for_coarse_to_fine"
    reliability = (
        probe.groupby("operator")
        .agg(
            semantic_type_count=("semantic_type", "nunique"),
            total_tests=("test_count", "sum"),
            total_candidates=("candidate_count", "sum"),
            total_non_l7_candidates=("non_l7_candidate_count", "sum"),
            best_score=("max_score", "max"),
            allow_count=("operator_policy", lambda s: int((s == "allow_for_coarse_to_fine").sum())),
        )
        .reset_index()
    )
    reliability["operator_reliability"] = "weak"
    reliability.loc[reliability["total_candidates"] > 0, "operator_reliability"] = "diagnostic"
    reliability.loc[reliability["allow_count"] > 0, "operator_reliability"] = "allowed_limited"
    blockers: list[str] = []
    if int((probe["operator_policy"] == "allow_for_coarse_to_fine").sum()) == 0:
        blockers.append("no_operator_non_l7_control_clean")
    decision = "PASS_A7FF1_OPERATOR_PROBING_READY_FOR_PAIR_CLUSTERING" if not blockers else "HOLD_A7FF1_NO_OPERATOR_READY"
    manifest = {
        "stage": "A7FF-1",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "operator_count": int(probe["operator"].nunique()),
        "allowed_operator_rows": int((probe["operator_policy"] == "allow_for_coarse_to_fine").sum()),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    return probe, reliability, manifest


def feature_pair_clustering(response: pd.DataFrame, ontology: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    frame = response.copy()
    frame["score"] = frame.apply(response_score, axis=1)
    keys = ["label_family", "label_horizon_h", "transform"]
    frame["vector_key"] = frame[keys].astype(str).agg("|".join, axis=1)
    pivot = frame.pivot_table(index="field_name", columns="vector_key", values="score", aggfunc="max", fill_value=0.0)
    vectors = pivot.reset_index().merge(ontology[["field_name", "semantic_type", "compiler_role"]], on="field_name", how="left")
    numeric_cols = [c for c in vectors.columns if c not in {"field_name", "semantic_type", "compiler_role"}]
    pairs: list[dict[str, Any]] = []
    for i, left in vectors.iterrows():
        for j in range(i + 1, len(vectors)):
            right = vectors.iloc[j]
            similarity = corr(left[numeric_cols].to_numpy(dtype=float), right[numeric_cols].to_numpy(dtype=float))
            semantic_pair = "|".join(sorted([str(left["semantic_type"]), str(right["semantic_type"])]))
            role_pair = "|".join(sorted([str(left["compiler_role"]), str(right["compiler_role"])]))
            policy = "block_pair"
            reason = "no_high_prior_or_response_similarity"
            if str(left["semantic_type"]) == str(right["semantic_type"]) and similarity >= 0.50:
                policy = "within_cluster_refinement"
                reason = "same_semantic_response_similar"
            high_prior = {
                "basis_premium_like|rate_like",
                "basis_premium_like|positioning_like",
                "basis_premium_like|volatility_like",
                "liquidity_like|volatility_like",
                "positioning_like|price_like",
                "price_like|volatility_like",
            }
            if semantic_pair in high_prior:
                policy = "cross_cluster_high_prior_interaction"
                reason = "semantic_high_prior_pair"
            if "forbidden_label_or_future" in role_pair:
                policy = "block_pair"
                reason = "forbidden_role_in_pair"
            pairs.append(
                {
                    "left_field": left["field_name"],
                    "right_field": right["field_name"],
                    "left_semantic_type": left["semantic_type"],
                    "right_semantic_type": right["semantic_type"],
                    "semantic_pair": semantic_pair,
                    "role_pair": role_pair,
                    "response_similarity": similarity,
                    "pair_policy": policy,
                    "policy_reason": reason,
                }
            )
    pair_df = pd.DataFrame(pairs)
    clusters = (
        vectors.groupby(["semantic_type", "compiler_role"], dropna=False)
        .size()
        .reset_index(name="field_count")
        .sort_values(["semantic_type", "compiler_role"])
    )
    allowed_pairs = pair_df[pair_df["pair_policy"].ne("block_pair")].copy()
    blockers = []
    if allowed_pairs.empty:
        blockers.append("no_feature_pairs_allowed")
    decision = "PASS_A7FF2_FEATURE_PAIR_POLICY_READY" if not blockers else "HOLD_A7FF2_NO_FEATURE_PAIRS_ALLOWED"
    manifest = {
        "stage": "A7FF-2",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "field_vector_count": int(len(vectors)),
        "pair_count": int(len(pair_df)),
        "allowed_pair_count": int(len(allowed_pairs)),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    return vectors, pair_df, clusters, manifest


def coarse_to_fine_contract(
    ontology: pd.DataFrame,
    probe: pd.DataFrame,
    pairs: pd.DataFrame,
    promoted: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    allowed_ops = probe[probe["operator_policy"].eq("allow_for_coarse_to_fine")][["semantic_type", "operator"]].drop_duplicates()
    promoted_fields = set(promoted["field_name"]) if not promoted.empty else set()
    blueprints: list[dict[str, Any]] = []
    for field in sorted(promoted_fields):
        o = ontology[ontology["field_name"].eq(field)].head(1)
        semantic = str(o["semantic_type"].iloc[0]) if not o.empty else "generic_numeric"
        ops = allowed_ops[allowed_ops["semantic_type"].eq(semantic)]["operator"].tolist() or ["Delta"]
        for op in sorted(set(ops)):
            blueprints.append(
                {
                    "blueprint_id": stable_id("a7ff3", f"F1|{field}|{op}"),
                    "layer": "F1_single_field_transform",
                    "primary_field": field,
                    "secondary_field": "",
                    "operator": op,
                    "semantic_type": semantic,
                    "pair_policy": "",
                    "status": "allowed_blueprint",
                }
            )
    allowed_pairs = pairs[pairs["pair_policy"].ne("block_pair")]
    for row in allowed_pairs.head(120).itertuples(index=False):
        if row.left_field not in promoted_fields and row.right_field not in promoted_fields:
            continue
        primary = row.left_field if row.left_field in promoted_fields else row.right_field
        secondary = row.right_field if primary == row.left_field else row.left_field
        blueprints.append(
            {
                "blueprint_id": stable_id("a7ff3", f"F2|{primary}|{secondary}|{row.pair_policy}"),
                "layer": "F2_typed_two_field_interaction",
                "primary_field": primary,
                "secondary_field": secondary,
                "operator": "Mul|Sub|SafeDiv",
                "semantic_type": row.semantic_pair,
                "pair_policy": row.pair_policy,
                "status": "allowed_blueprint",
            }
        )
    bp = pd.DataFrame(blueprints).drop_duplicates(subset=["blueprint_id"]) if blueprints else pd.DataFrame()
    layer_policy = {
        "F1_single_field_transform": {
            "allowed": True,
            "requires": ["field_ontology", "operator_probe_allowed", "non_l7_response_evidence"],
        },
        "F2_typed_two_field_interaction": {
            "allowed": True,
            "requires": ["one_promoted_signal_seed", "allowed_feature_pair_policy", "controls_attached"],
        },
        "F3_state_conditioned_or_neutralized": {
            "allowed": "contract_only",
            "requires": ["frozen_regime_state", "neutralization_policy", "no_label_or_future_state"],
        },
        "F4_portfolio_candidate": {
            "allowed": "not_yet",
            "requires": ["numeric_replay", "marginal_contribution", "cluster_registry"],
        },
    }
    blockers = []
    if bp.empty:
        blockers.append("no_blueprints_generated")
    decision = "PASS_A7FF3_COARSE_TO_FINE_BLUEPRINTS_READY" if not blockers else "HOLD_A7FF3_NO_BLUEPRINTS"
    manifest = {
        "stage": "A7FF-3",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "blueprint_count": int(len(bp)),
        "layer_count": int(bp["layer"].nunique()) if not bp.empty else 0,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    return bp, layer_policy, manifest


def role_promotion(
    ontology: pd.DataFrame,
    operator_probe_df: pd.DataFrame,
    promoted: pd.DataFrame,
    pair_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    promoted_fields = set(promoted["field_name"]) if not promoted.empty else set()
    allowed_pair_fields = set(pair_df.loc[pair_df["pair_policy"].ne("block_pair"), "left_field"]).union(
        set(pair_df.loc[pair_df["pair_policy"].ne("block_pair"), "right_field"])
    )
    rows = []
    for row in ontology.itertuples(index=False):
        field = row.field_name
        if field in promoted_fields:
            role = "promote_to_signal_candidate"
            reason = "non_l7_control_clean_response_backed"
        elif field in allowed_pair_fields and str(row.compiler_role) in {"risk_exposure_or_neutralizer", "regime_or_diagnostic_input"}:
            role = "promote_to_regime_or_interaction_input"
            reason = "allowed_pair_policy_but_no_standalone_alpha"
        elif str(row.compiler_role) == "forbidden_label_or_future":
            role = "forbidden"
            reason = "label_or_future"
        elif pd.to_numeric(getattr(row, "median_control_ratio", np.nan), errors="coerce") >= 1.0:
            role = "demote_to_control_like"
            reason = "median_control_ratio_ge_1"
        else:
            role = "weak_response_hold"
            reason = "insufficient_non_l7_control_clean_evidence"
        rows.append(
            {
                "field_name": field,
                "semantic_type": row.semantic_type,
                "compiler_role": row.compiler_role,
                "new_factor_role": role,
                "transition_reason": reason,
                "primitive_candidate_count": getattr(row, "primitive_candidate_count", 0),
                "non_l7_candidate_count": getattr(row, "non_l7_candidate_count", 0),
                "median_control_ratio": getattr(row, "median_control_ratio", np.nan),
            }
        )
    role_map = pd.DataFrame(rows)
    transition_policy = (
        role_map.groupby(["new_factor_role", "transition_reason"], dropna=False)
        .size()
        .reset_index(name="field_count")
        .sort_values(["new_factor_role", "transition_reason"])
    )
    blockers = []
    if int((role_map["new_factor_role"] == "promote_to_signal_candidate").sum()) == 0:
        blockers.append("no_signal_candidate_promotion")
    decision = "PASS_A7FF4_ROLE_PROMOTION_MAP_READY" if not blockers else "HOLD_A7FF4_NO_SIGNAL_PROMOTIONS"
    manifest = {
        "stage": "A7FF-4",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "signal_candidate_count": int((role_map["new_factor_role"] == "promote_to_signal_candidate").sum()),
        "regime_or_interaction_input_count": int((role_map["new_factor_role"] == "promote_to_regime_or_interaction_input").sum()),
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    return role_map, transition_policy, manifest


def factor_candidate_compile(blueprints: pd.DataFrame, role_map: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    if blueprints.empty:
        candidates = pd.DataFrame()
    else:
        allowed_signal = set(role_map.loc[role_map["new_factor_role"].eq("promote_to_signal_candidate"), "field_name"])
        allowed_interaction = set(role_map.loc[role_map["new_factor_role"].eq("promote_to_regime_or_interaction_input"), "field_name"])
        rows = []
        for bp in blueprints.itertuples(index=False):
            primary_ok = bp.primary_field in allowed_signal
            secondary_ok = not bp.secondary_field or bp.secondary_field in allowed_signal or bp.secondary_field in allowed_interaction
            status = "compiled_factor_blueprint" if primary_ok and secondary_ok else "blocked_role_policy"
            rows.append(
                {
                    "factor_blueprint_id": stable_id("a7ff5", f"{bp.blueprint_id}|{bp.layer}|{bp.primary_field}|{bp.secondary_field}|{bp.operator}"),
                    "source_blueprint_id": bp.blueprint_id,
                    "layer": bp.layer,
                    "primary_field": bp.primary_field,
                    "secondary_field": bp.secondary_field,
                    "operator": bp.operator,
                    "pair_policy": bp.pair_policy,
                    "factor_family": bp.semantic_type,
                    "status": status,
                }
            )
        candidates = pd.DataFrame(rows)
    compiled = candidates[candidates["status"].eq("compiled_factor_blueprint")].copy() if not candidates.empty else pd.DataFrame()
    blocked = candidates[candidates["status"].ne("compiled_factor_blueprint")].copy() if not candidates.empty else pd.DataFrame()
    blockers = []
    family_count = int(compiled["factor_family"].nunique()) if not compiled.empty else 0
    if compiled.empty:
        blockers.append("compiled_factor_blueprint_count_zero")
    if family_count < 3:
        blockers.append("compiled_factor_family_count_lt_3")
    decision = "PASS_A7FF5_FACTOR_BLUEPRINTS_READY_FOR_PORTFOLIO_DRYRUN" if not blockers else "HOLD_A7FF5_FACTOR_COMPILER_NOT_DIVERSE"
    manifest = {
        "stage": "A7FF-5",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "compiled_blueprint_count": int(len(compiled)),
        "compiled_factor_family_count": family_count,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
    }
    return compiled, blocked, manifest


def portfolio_marginal_dryrun(compiled: pd.DataFrame, role_map: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    if compiled.empty:
        queue = pd.DataFrame()
    else:
        role_scores = role_map.set_index("field_name")
        rows = []
        for row in compiled.itertuples(index=False):
            primary = role_scores.loc[row.primary_field] if row.primary_field in role_scores.index else None
            non_l7 = float(primary.get("non_l7_candidate_count", 0.0)) if primary is not None else 0.0
            control = float(primary.get("median_control_ratio", 1.0)) if primary is not None and not pd.isna(primary.get("median_control_ratio")) else 1.0
            novelty = 1.0 if row.secondary_field else 0.25
            marginal_proxy = non_l7 + max(0.0, 1.0 - control) + novelty
            rows.append(
                {
                    "factor_blueprint_id": row.factor_blueprint_id,
                    "layer": row.layer,
                    "primary_field": row.primary_field,
                    "secondary_field": row.secondary_field,
                    "factor_family": row.factor_family,
                    "marginal_proxy_no_may": marginal_proxy,
                    "cluster_novelty_proxy": novelty,
                    "requires_numeric_replay": True,
                    "selected_for_future_numeric_probe": False,
                }
            )
        queue = pd.DataFrame(rows).sort_values(["marginal_proxy_no_may", "factor_blueprint_id"], ascending=[False, True])
        selected_families: set[str] = set()
        selected_ids: set[str] = set()
        for idx, item in queue.iterrows():
            if item["factor_family"] in selected_families:
                continue
            selected_ids.add(item["factor_blueprint_id"])
            selected_families.add(item["factor_family"])
            if len(selected_ids) >= 4:
                break
        queue["selected_for_future_numeric_probe"] = queue["factor_blueprint_id"].isin(selected_ids)
    selected = queue[queue["selected_for_future_numeric_probe"]].copy() if not queue.empty else pd.DataFrame()
    blockers = []
    if len(selected) < 4:
        blockers.append("selected_factor_count_lt_4")
    if not selected.empty and selected["factor_family"].nunique() < min(len(selected), 4):
        blockers.append("selected_factor_family_diversity_low")
    blockers.append("portfolio_marginal_reward_requires_numeric_replay")
    decision = "HOLD_A7FF6_PORTFOLIO_MARGINAL_DRYRUN_NOT_PROMOTABLE"
    manifest = {
        "stage": "A7FF-6",
        "generated_at": now_utc(),
        "decision": decision,
        "blockers": blockers,
        "queue_count": int(len(queue)),
        "selected_count": int(len(selected)),
        "executes_search": False,
        "executes_replay": False,
        "uses_may": False,
        "authorizes_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    return queue, selected, manifest


def main() -> None:
    for spec in STAGES.values():
        spec["runtime"].mkdir(parents=True, exist_ok=True)
        spec["report"].parent.mkdir(parents=True, exist_ok=True)

    enforcement = pd.read_csv(ENFORCEMENT)
    response = pd.read_csv(RESPONSE)
    roles = pd.read_csv(ROLE_LEDGER)
    promoted = pd.read_csv(F4_PROMOTED) if F4_PROMOTED.exists() else pd.DataFrame()
    f4 = read_json(F4_MANIFEST)
    if not str(f4.get("decision", "")).startswith("PASS_"):
        raise SystemExit(f"A7AI-F4 is not pass-like: {f4.get('decision')}")

    ontology, m0 = build_ontology(enforcement, roles, response)
    r0 = STAGES["A7FF-0"]["runtime"]
    ontology.to_csv(r0 / "a7ff0_field_ontology_v2.csv", index=False)
    ontology.groupby(["semantic_type", "compiler_role"], dropna=False).size().reset_index(name="field_count").to_csv(
        r0 / "a7ff0_semantic_type_summary.csv", index=False
    )
    write_json(r0 / "a7ff0_manifest.json", m0)
    write_report(
        "A7FF-0",
        m0["decision"],
        m0,
        [
            ("Semantic Type Summary", md_table(pd.read_csv(r0 / "a7ff0_semantic_type_summary.csv"), 80)),
            ("Boundary", "No replay, no formula search, no alpha proof."),
        ],
    )

    probe, reliability, m1 = operator_probe(response, ontology)
    r1 = STAGES["A7FF-1"]["runtime"]
    probe.to_csv(r1 / "a7ff1_operator_probe_score.csv", index=False)
    reliability.to_csv(r1 / "a7ff1_operator_reliability_summary.csv", index=False)
    probe[["semantic_type", "operator", "operator_policy"]].drop_duplicates().to_csv(r1 / "a7ff1_operator_policy.csv", index=False)
    write_json(r1 / "a7ff1_manifest.json", m1)
    write_report(
        "A7FF-1",
        m1["decision"],
        m1,
        [
            ("Operator Reliability", md_table(reliability.sort_values("best_score", ascending=False), 80)),
            ("Allowed Operator Rows", md_table(probe[probe["operator_policy"].eq("allow_for_coarse_to_fine")], 80)),
        ],
    )

    vectors, pair_df, clusters, m2 = feature_pair_clustering(response, ontology)
    r2 = STAGES["A7FF-2"]["runtime"]
    vectors.to_csv(r2 / "a7ff2_field_response_vectors.csv", index=False)
    pair_df.to_csv(r2 / "a7ff2_feature_pair_similarity.csv", index=False)
    pair_df[pair_df["pair_policy"].ne("block_pair")].to_csv(r2 / "a7ff2_feature_pair_policy.csv", index=False)
    clusters.to_csv(r2 / "a7ff2_semantic_response_clusters.csv", index=False)
    write_json(r2 / "a7ff2_manifest.json", m2)
    write_report(
        "A7FF-2",
        m2["decision"],
        m2,
        [
            ("Semantic Response Clusters", md_table(clusters, 80)),
            ("Allowed Pair Policy", md_table(pair_df[pair_df["pair_policy"].ne("block_pair")], 80)),
        ],
    )

    blueprints, layer_policy, m3 = coarse_to_fine_contract(ontology, probe, pair_df, promoted)
    r3 = STAGES["A7FF-3"]["runtime"]
    blueprints.to_csv(r3 / "a7ff3_candidate_blueprints.csv", index=False)
    write_json(r3 / "a7ff3_generation_layer_policy.json", layer_policy)
    write_json(r3 / "a7ff3_manifest.json", m3)
    write_report(
        "A7FF-3",
        m3["decision"],
        m3,
        [
            ("Blueprints", md_table(blueprints, 80)),
            ("Layer Policy", "```json\n" + json.dumps(layer_policy, indent=2, sort_keys=True) + "\n```"),
        ],
    )

    role_map, transition_policy, m4 = role_promotion(ontology, probe, promoted, pair_df)
    r4 = STAGES["A7FF-4"]["runtime"]
    role_map.to_csv(r4 / "a7ff4_feature_role_map_v2.csv", index=False)
    transition_policy.to_csv(r4 / "a7ff4_role_transition_policy.csv", index=False)
    write_json(r4 / "a7ff4_manifest.json", m4)
    write_report(
        "A7FF-4",
        m4["decision"],
        m4,
        [
            ("Transition Policy", md_table(transition_policy, 80)),
            ("Promotions", md_table(role_map[role_map["new_factor_role"].str.contains("promote", na=False)], 80)),
        ],
    )

    compiled, blocked, m5 = factor_candidate_compile(blueprints, role_map)
    r5 = STAGES["A7FF-5"]["runtime"]
    compiled.to_csv(r5 / "a7ff5_factor_candidate_blueprints.csv", index=False)
    blocked.to_csv(r5 / "a7ff5_blocked_factor_blueprints.csv", index=False)
    write_json(r5 / "a7ff5_manifest.json", m5)
    write_report(
        "A7FF-5",
        m5["decision"],
        m5,
        [
            ("Compiled Factor Blueprints", md_table(compiled, 80)),
            ("Blocked Factor Blueprints", md_table(blocked, 80)),
        ],
    )

    queue, selected, m6 = portfolio_marginal_dryrun(compiled, role_map)
    r6 = STAGES["A7FF-6"]["runtime"]
    queue.to_csv(r6 / "a7ff6_portfolio_marginal_queue.csv", index=False)
    selected.to_csv(r6 / "a7ff6_selected_dryrun_queue.csv", index=False)
    write_json(r6 / "a7ff6_manifest.json", m6)
    write_report(
        "A7FF-6",
        m6["decision"],
        m6,
        [
            ("Portfolio Marginal Queue", md_table(queue, 80)),
            ("Selected Dryrun Queue", md_table(selected, 40)),
            ("Boundary", "No numeric replay was executed. Portfolio marginal reward remains a dry proxy and cannot authorize search."),
        ],
    )

    print(
        json.dumps(
            {
                "A7FF-0": m0["decision"],
                "A7FF-1": m1["decision"],
                "A7FF-2": m2["decision"],
                "A7FF-3": m3["decision"],
                "A7FF-4": m4["decision"],
                "A7FF-5": m5["decision"],
                "A7FF-6": m6["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
