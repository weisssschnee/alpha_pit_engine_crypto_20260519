from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


REPO = Path(__file__).resolve().parents[1]
CORE52F = REPO / "runtime" / "a7ffcore52f_diagnostic_clue_forensic"
RUNTIME = REPO / "runtime" / "a7ffcore53_replay_target_repair_contract"
REPORT = REPO / "reports" / "CRYPTO_A7FFCORE53_REPLAY_TARGET_REPAIR_CONTRACT_20260602.md"


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


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    source = read_json(CORE52F / "a7ffcore52f_manifest.json")
    if not source.get("authorizes_core53_replay_target_repair_contract"):
        raise SystemExit(f"CORE53 contract not authorized by CORE52F: {source.get('decision')}")

    label_targets = pd.DataFrame(
        [
            {
                "target_id": "T0_raw_return",
                "role": "baseline",
                "status": "allowed_baseline",
                "description": "raw forward return by horizon",
                "independent_for_top_bottom_spread": True,
                "promotion_role": "baseline_only",
            },
            {
                "target_id": "T1_xs_relative_return",
                "role": "redundant_for_decile_spread",
                "status": "blocked_as_independent_evidence",
                "description": "cross-sectional demeaned return; top-bottom spread equals raw spread after common component removal",
                "independent_for_top_bottom_spread": False,
                "promotion_role": "diagnostic_only",
            },
            {
                "target_id": "T2_btc_eth_beta_residual_return",
                "role": "market_beta_residual",
                "status": "required_new_target",
                "description": "future return residual after BTC/ETH or major-beta exposure removal",
                "independent_for_top_bottom_spread": True,
                "promotion_role": "primary_candidate_evidence",
            },
            {
                "target_id": "T3_liquidity_tier_relative_return",
                "role": "liquidity_neutral_relative",
                "status": "required_new_target",
                "description": "future return relative to active liquidity tier peers",
                "independent_for_top_bottom_spread": True,
                "promotion_role": "primary_candidate_evidence",
            },
            {
                "target_id": "T4_latent_state_relative_return",
                "role": "latent_state_neutral_relative",
                "status": "required_new_target",
                "description": "future return relative to frozen listing-age/liquidity/volatility latent state peers",
                "independent_for_top_bottom_spread": True,
                "promotion_role": "primary_candidate_evidence",
            },
            {
                "target_id": "T5_vol_adjusted_return",
                "role": "risk_scaled_return",
                "status": "required_new_target",
                "description": "future return divided by ex-ante realized volatility scale",
                "independent_for_top_bottom_spread": True,
                "promotion_role": "supporting_candidate_evidence",
            },
            {
                "target_id": "T6_ranked_future_return",
                "role": "rank_label",
                "status": "diagnostic_only",
                "description": "future cross-sectional rank; cannot alone promote candidate to alpha pool",
                "independent_for_top_bottom_spread": True,
                "promotion_role": "diagnostic_only",
            },
            {
                "target_id": "T7_portfolio_net_spread_proxy",
                "role": "book_proxy",
                "status": "required_new_target",
                "description": "top-bottom book spread proxy with turnover/cost accounting fields",
                "independent_for_top_bottom_spread": True,
                "promotion_role": "promotion_gate",
            },
        ]
    )
    horizon_policy = pd.DataFrame(
        [
            {"horizon": "1h", "status": "allowed", "notes": "primary fast horizon; require turnover/cost proxy"},
            {"horizon": "4h", "status": "allowed", "notes": "medium fast horizon"},
            {"horizon": "8h", "status": "allowed", "notes": "medium horizon"},
            {"horizon": "24h", "status": "allowed", "notes": "slow horizon"},
        ]
    )
    gate_policy = {
        "strict_replay_clue": {
            "min_clean_independent_target_count": 3,
            "min_clean_horizon_count": 2,
            "median_control_ratio_max": 0.9,
            "min_control_ratio_max": 0.8,
            "requires_portfolio_net_spread_proxy_positive": True,
        },
        "diagnostic_clue": {
            "min_clean_independent_target_count": 1,
            "min_clean_horizon_count": 1,
            "median_control_ratio_max": 1.0,
            "requires_forensic_not_search": True,
        },
        "forbidden_counting_rules": [
            "T0_raw_return and T1_xs_relative_return cannot be counted as two independent labels for top-bottom spread",
            "ranked_future_return cannot be the only positive target for alpha promotion",
            "control_ratio just below one is not sufficient without positive control margin",
        ],
    }
    metric_schema = pd.DataFrame(
        [
            {"column": "target_id", "required": True, "description": "repaired replay target id"},
            {"column": "horizon", "required": True, "description": "label horizon"},
            {"column": "original_spread_mean", "required": True, "description": "top-bottom target spread"},
            {"column": "original_tstat", "required": True, "description": "hourly or non-overlap robust tstat"},
            {"column": "control_ratio", "required": True, "description": "max absolute control spread divided by original absolute spread"},
            {"column": "control_margin", "required": True, "description": "1 - control_ratio"},
            {"column": "independent_target_flag", "required": True, "description": "whether target counts as independent evidence"},
            {"column": "portfolio_net_spread_proxy", "required": False, "description": "book-level net spread proxy where applicable"},
        ]
    )
    authorization = {
        "authorized": {
            "A7FF-CORE53E replay target builder preflight": True,
        },
        "not_authorized": {
            "formula_search": True,
            "large_search": True,
            "candidate_promotion": True,
            "alpha_proof": True,
            "shadow_paper_live": True,
        },
    }
    manifest = {
        "stage": "A7FF-CORE53",
        "generated_at": now_utc(),
        "source_stage": source.get("stage"),
        "source_decision": source.get("decision"),
        "decision": "PASS_A7FFCORE53_REPLAY_TARGET_REPAIR_CONTRACT_READY_FOR_CORE53E",
        "target_count": int(label_targets.shape[0]),
        "required_new_target_count": int(label_targets["status"].eq("required_new_target").sum()),
        "executes_replay": False,
        "executes_search": False,
        "authorizes_core53e_preflight": True,
        "authorizes_formula_search": False,
        "authorizes_large_search": False,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
    }
    label_targets.to_csv(RUNTIME / "a7ffcore53_repaired_label_target_contract.csv", index=False)
    horizon_policy.to_csv(RUNTIME / "a7ffcore53_horizon_policy.csv", index=False)
    metric_schema.to_csv(RUNTIME / "a7ffcore53_replay_metric_schema.csv", index=False)
    write_json(RUNTIME / "a7ffcore53_gate_policy.json", gate_policy)
    write_json(RUNTIME / "a7ffcore53_authorization_matrix.json", authorization)
    write_json(RUNTIME / "a7ffcore53_manifest.json", manifest)
    lines = [
        "# CRYPTO A7FF-CORE53 REPLAY TARGET REPAIR CONTRACT",
        "",
        f"Generated: {manifest['generated_at']}",
        "",
        "## Decision",
        "",
        f"`{manifest['decision']}`",
        "",
        "CORE53 repairs the replay target contract after CORE52F found L0/L1 top-bottom spread redundancy and thin control margins. It does not execute replay/search/proof.",
        "",
        "## Manifest",
        "",
        "```json",
        json.dumps(manifest, indent=2, sort_keys=True),
        "```",
        "",
        "## Repaired Label Targets",
        "",
        md_table(label_targets),
        "",
        "## Gate Policy",
        "",
        "```json",
        json.dumps(gate_policy, indent=2, sort_keys=True),
        "```",
        "",
        "## Metric Schema",
        "",
        md_table(metric_schema),
        "",
        "## Authorization",
        "",
        "```json",
        json.dumps(authorization, indent=2, sort_keys=True),
        "```",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
