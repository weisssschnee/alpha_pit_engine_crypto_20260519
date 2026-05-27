from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(r"G:\AlphaFactory_CryptoData")

INPUT_CLASSIFICATION = DATA_ROOT / "gold" / "metadata" / "binance_universe498_replay_1h_v1_symbol_classification_20260526.csv"
OUT_DIR = ROOT / "runtime" / "a7ak_lv3r_contract_meme_taxonomy_audit"
REPORT_PATH = ROOT / "reports" / "CRYPTO_A7AK_LV3R_CONTRACT_MEME_TAXONOMY_AUDIT_20260527.md"

DATA_TAXONOMY = DATA_ROOT / "gold" / "metadata" / "binance_universe498_contract_meme_taxonomy_v1_20260527.csv"


HIGH_CONFIDENCE_MEME = {
    "BABYDOGE": "dog",
    "BOB": "internet_meme",
    "BONK": "dog",
    "BOME": "culture_meme",
    "BRETT": "culture_meme",
    "BROCCOLI714": "culture_meme",
    "BROCCOLIF3B": "culture_meme",
    "CAT": "cat",
    "CHEEMS": "dog",
    "CHILLGUY": "culture_meme",
    "DOGE": "dog",
    "DOGS": "dog",
    "FARTCOIN": "culture_meme",
    "FLOKI": "dog",
    "GIGGLE": "culture_meme",
    "GOAT": "ai_meme",
    "JELLYJELLY": "culture_meme",
    "KOMA": "culture_meme",
    "MELANIA": "political_meme",
    "MEME": "culture_meme",
    "MEW": "cat",
    "MOG": "cat",
    "MOODENG": "animal_meme",
    "MUBARAK": "political_meme",
    "NEIRO": "dog",
    "PENGU": "animal_meme",
    "PEPE": "frog",
    "PIPPIN": "ai_meme",
    "PNUT": "animal_meme",
    "POPCAT": "cat",
    "RATS": "animal_meme",
    "SATS": "btc_meme",
    "SHIB": "dog",
    "SPX": "culture_meme",
    "TOSHI": "cat",
    "TRUMP": "political_meme",
    "TURBO": "ai_meme",
    "USELESS": "culture_meme",
    "WIF": "dog",
}

MEDIUM_CONFIDENCE_MEME = {
    "ACT": "culture_meme",
    "BAN": "culture_meme",
    "BANANAS31": "culture_meme",
    "BULLA": "culture_meme",
    "CLANKER": "ai_meme",
    "COOKIE": "culture_meme",
    "DOOD": "culture_meme",
    "FLOCK": "ai_meme",
    "GRIFFAIN": "ai_meme",
    "HMSTR": "animal_meme",
    "IDOL": "culture_meme",
    "MEME": "culture_meme",
    "PUMP": "culture_meme",
    "SPORTFUN": "culture_meme",
    "SWARMS": "ai_meme",
    "TST": "culture_meme",
    "TURTLE": "animal_meme",
    "ZEREBRO": "ai_meme",
}

REVIEW_ASSETS = {
    "APE": "nft/social token, not automatically meme",
    "ANIME": "culture token, review before meme treatment",
    "CATI": "game/app token, do not infer meme from CAT substring",
    "PEOPLE": "DAO/social token, not automatically meme",
    "NOT": "social/game token, review before meme treatment",
    "DOGS": "high-confidence meme but also app/community token",
    "HMSTR": "game/community token with meme-like behavior",
    "PUMPBTC": "wrapped/derivative naming, not direct meme token",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows: int = 80) -> str:
    if df.empty:
        return "`<empty>`"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```\n" + df.head(max_rows).to_string(index=False) + "\n```"


def parse_contract(symbol: str, base_asset: str) -> dict[str, Any]:
    if not symbol.endswith("USDT"):
        quote_asset = "UNKNOWN"
    else:
        quote_asset = "USDT"
    raw_base = str(base_asset)
    multiplier = 1
    prefix = ""
    underlying = raw_base
    if raw_base.startswith("1000000") and len(raw_base) > 7:
        multiplier = 1_000_000
        prefix = "1000000"
        underlying = raw_base[7:]
    elif raw_base.startswith("1000") and len(raw_base) > 4:
        multiplier = 1_000
        prefix = "1000"
        underlying = raw_base[4:]
    elif raw_base.startswith("1M") and len(raw_base) > 2:
        multiplier = 1_000_000
        prefix = "1M"
        underlying = raw_base[2:]
    return {
        "quote_asset": quote_asset,
        "raw_contract_base_asset": raw_base,
        "underlying_asset": underlying,
        "contract_unit_multiplier": multiplier,
        "multiplier_prefix": prefix,
        "is_multiplier_contract": multiplier != 1,
        "instrument_family": "binance_usdm_futures",
        "instrument_type": "linear_usdt_margined_perpetual_contract",
        "is_derivative_contract": True,
        "is_spot": False,
        "margin_asset": "USDT",
        "settlement_asset": "USDT",
    }


def classify_meme(underlying: str) -> dict[str, Any]:
    if underlying in HIGH_CONFIDENCE_MEME:
        subtype = HIGH_CONFIDENCE_MEME[underlying]
        return {
            "is_meme_token": True,
            "meme_confidence": "high",
            "meme_subtype": subtype,
            "meme_taxonomy_source": "conservative_manual_seed_v1",
            "meme_review_note": REVIEW_ASSETS.get(underlying, ""),
        }
    if underlying in MEDIUM_CONFIDENCE_MEME:
        subtype = MEDIUM_CONFIDENCE_MEME[underlying]
        return {
            "is_meme_token": True,
            "meme_confidence": "medium",
            "meme_subtype": subtype,
            "meme_taxonomy_source": "manual_seed_v1_needs_review",
            "meme_review_note": REVIEW_ASSETS.get(underlying, "medium-confidence meme/social classification"),
        }
    if underlying in REVIEW_ASSETS:
        return {
            "is_meme_token": False,
            "meme_confidence": "review",
            "meme_subtype": "review",
            "meme_taxonomy_source": "manual_review_flag_v1",
            "meme_review_note": REVIEW_ASSETS[underlying],
        }
    heuristic_hit = bool(re.search(r"(DOGE|DOG|CAT|PEPE|FLOKI|SHIB|BONK|WIF|TRUMP|MELANIA|PNUT|POPCAT)", underlying))
    if heuristic_hit:
        return {
            "is_meme_token": True,
            "meme_confidence": "medium",
            "meme_subtype": "heuristic_name_match",
            "meme_taxonomy_source": "heuristic_name_match_v1",
            "meme_review_note": "heuristic token-name match; review before promotion",
        }
    return {
        "is_meme_token": False,
        "meme_confidence": "none",
        "meme_subtype": "not_meme_or_unknown",
        "meme_taxonomy_source": "not_in_meme_seed_v1",
        "meme_review_note": "",
    }


def taxonomy_row(row: pd.Series) -> dict[str, Any]:
    contract = parse_contract(str(row["symbol"]), str(row["base_asset"]))
    meme = classify_meme(contract["underlying_asset"])
    out = row.to_dict()
    out.update(contract)
    out.update(meme)
    out["meme_contract_group"] = (
        "meme_multiplier_contract"
        if out["is_meme_token"] and out["is_multiplier_contract"]
        else "meme_plain_contract"
        if out["is_meme_token"]
        else "non_meme_multiplier_contract"
        if out["is_multiplier_contract"]
        else "non_meme_plain_contract"
    )
    out["search_stratification_group"] = (
        out["meme_contract_group"] + "|" + str(out["liquidity_tier"]) + "|" + str(out["search_eligibility"])
    )
    out["taxonomy_version"] = "contract_meme_taxonomy_v1_20260527"
    return out


def build_report(summary: dict[str, Any], taxonomy: pd.DataFrame, contract_counts: pd.DataFrame, meme_counts: pd.DataFrame, cross: pd.DataFrame, top_meme: pd.DataFrame, review: pd.DataFrame) -> None:
    report = f"""# CRYPTO A7AK-LV3R Contract / Meme Taxonomy Audit

Generated: {summary["generated_at"]}

## Decision

```text
{summary["decision"]}
```

This audit makes contract and meme classifications explicit for universe498. It does not run search, replay, or alpha proof.

## Summary

```json
{json.dumps(summary, indent=2, sort_keys=True)}
```

## Contract Counts

{md_table(contract_counts)}

## Meme Counts

{md_table(meme_counts)}

## Contract x Meme Cross Tab

{md_table(cross)}

## Top Meme / Meme-Like Contracts By Liquidity

{md_table(top_meme, max_rows=80)}

## Review Flags

{md_table(review, max_rows=80)}

## Boundary

```text
CONTRACT RULE:
  All rows are Binance USD-M futures linear USDT-margined perpetual contracts, not spot.
  plain_contract means no symbol multiplier prefix.
  multiplier_contract means the Binance contract symbol embeds a unit multiplier such as 1000/1000000/1M.

MEME RULE:
  meme classification is explicit and conservative.
  medium/review classifications must not be used for proof promotion without review.
  meme flags are stratification controls, not alpha labels.

AUTHORIZED NEXT:
  Use taxonomy as a stratification/control field in A7AK-LV4 design.

NOT AUTHORIZED:
  alpha proof
  shadow / paper / live
```
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(INPUT_CLASSIFICATION)
    taxonomy = pd.DataFrame([taxonomy_row(row) for _, row in raw.iterrows()])
    taxonomy = taxonomy.sort_values("liquidity_rank").reset_index(drop=True)

    contract_counts = (
        taxonomy.groupby(["contract_format", "is_multiplier_contract", "contract_unit_multiplier"], dropna=False)
        .size()
        .reset_index(name="symbols")
        .sort_values("symbols", ascending=False)
    )
    meme_counts = (
        taxonomy.groupby(["is_meme_token", "meme_confidence", "meme_subtype"], dropna=False)
        .size()
        .reset_index(name="symbols")
        .sort_values(["is_meme_token", "symbols"], ascending=[False, False])
    )
    cross = (
        taxonomy.groupby(["meme_contract_group", "liquidity_tier", "search_eligibility"], dropna=False)
        .size()
        .reset_index(name="symbols")
        .sort_values(["meme_contract_group", "symbols"], ascending=[True, False])
    )
    top_meme = taxonomy[taxonomy["is_meme_token"] | taxonomy["meme_confidence"].isin(["medium", "review"])][
        [
            "symbol",
            "underlying_asset",
            "contract_format",
            "contract_unit_multiplier",
            "liquidity_rank",
            "liquidity_tier",
            "search_eligibility",
            "is_meme_token",
            "meme_confidence",
            "meme_subtype",
            "meme_review_note",
        ]
    ].sort_values("liquidity_rank")
    review = taxonomy[taxonomy["meme_confidence"].isin(["medium", "review"])][
        ["symbol", "underlying_asset", "liquidity_rank", "is_meme_token", "meme_confidence", "meme_subtype", "meme_review_note"]
    ].sort_values("liquidity_rank")

    blockers: list[str] = []
    if not bool(taxonomy["is_derivative_contract"].all()):
        blockers.append("non_derivative_contract_rows_found")
    if not bool((taxonomy["quote_asset"] == "USDT").all()):
        blockers.append("non_usdt_quote_rows_found")
    if int(taxonomy["underlying_asset"].isna().sum()):
        blockers.append("missing_underlying_asset")
    mismatch = taxonomy[
        ((taxonomy["contract_format"] == "multiplier_contract") & (~taxonomy["is_multiplier_contract"]))
        | ((taxonomy["contract_format"] == "plain_contract") & (taxonomy["is_multiplier_contract"]))
    ]
    if len(mismatch):
        blockers.append("contract_format_multiplier_parse_mismatch")

    summary = {
        "generated_at": utc_now(),
        "decision": "PASS_A7AK_LV3R_CONTRACT_MEME_TAXONOMY_READY",
        "input_classification": str(INPUT_CLASSIFICATION),
        "output_taxonomy": str(DATA_TAXONOMY),
        "symbols": int(len(taxonomy)),
        "all_usdt_margined_perpetual_contracts": bool(taxonomy["is_derivative_contract"].all()),
        "multiplier_contract_symbols": int(taxonomy["is_multiplier_contract"].sum()),
        "plain_contract_symbols": int((~taxonomy["is_multiplier_contract"]).sum()),
        "meme_symbols_high_confidence": int(((taxonomy["is_meme_token"]) & (taxonomy["meme_confidence"] == "high")).sum()),
        "meme_symbols_medium_confidence": int(((taxonomy["is_meme_token"]) & (taxonomy["meme_confidence"] == "medium")).sum()),
        "meme_review_symbols": int((taxonomy["meme_confidence"] == "review").sum()),
        "meme_multiplier_contract_symbols": int((taxonomy["meme_contract_group"] == "meme_multiplier_contract").sum()),
        "non_meme_multiplier_contract_symbols": int((taxonomy["meme_contract_group"] == "non_meme_multiplier_contract").sum()),
        "executes_taxonomy_audit": True,
        "executes_search": False,
        "executes_replay": False,
        "authorizes_lv4_stratification_use": True,
        "authorizes_alpha_proof": False,
        "authorizes_shadow_paper_live": False,
        "blockers": blockers,
        "warnings": [
            "Meme taxonomy is conservative and intended for stratification/control, not alpha labels",
            "Medium-confidence meme rows require review before proof use",
            "All symbols are futures contracts; taxonomy does not imply spot tradability",
        ],
    }
    if blockers:
        summary["decision"] = "HOLD_A7AK_LV3R_CONTRACT_MEME_TAXONOMY_BLOCKED"
        summary["authorizes_lv4_stratification_use"] = False

    write_json(OUT_DIR / "a7ak_lv3r_manifest.json", summary)
    taxonomy.to_csv(OUT_DIR / "a7ak_lv3r_contract_meme_taxonomy.csv", index=False)
    contract_counts.to_csv(OUT_DIR / "a7ak_lv3r_contract_counts.csv", index=False)
    meme_counts.to_csv(OUT_DIR / "a7ak_lv3r_meme_counts.csv", index=False)
    cross.to_csv(OUT_DIR / "a7ak_lv3r_contract_meme_stratification_counts.csv", index=False)
    top_meme.to_csv(OUT_DIR / "a7ak_lv3r_top_meme_contracts.csv", index=False)
    review.to_csv(OUT_DIR / "a7ak_lv3r_meme_review_flags.csv", index=False)

    DATA_TAXONOMY.parent.mkdir(parents=True, exist_ok=True)
    taxonomy.to_csv(DATA_TAXONOMY, index=False)
    build_report(summary, taxonomy, contract_counts, meme_counts, cross, top_meme, review)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
