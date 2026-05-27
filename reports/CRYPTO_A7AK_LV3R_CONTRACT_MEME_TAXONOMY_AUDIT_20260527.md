# CRYPTO A7AK-LV3R Contract / Meme Taxonomy Audit

Generated: 2026-05-27T00:31:52Z

## Decision

```text
PASS_A7AK_LV3R_CONTRACT_MEME_TAXONOMY_READY
```

This audit makes contract and meme classifications explicit for universe498. It does not run search, replay, or alpha proof.

## Summary

```json
{
  "all_usdt_margined_perpetual_contracts": true,
  "authorizes_alpha_proof": false,
  "authorizes_lv4_stratification_use": true,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7AK_LV3R_CONTRACT_MEME_TAXONOMY_READY",
  "executes_replay": false,
  "executes_search": false,
  "executes_taxonomy_audit": true,
  "generated_at": "2026-05-27T00:31:52Z",
  "input_classification": "G:\\AlphaFactory_CryptoData\\gold\\metadata\\binance_universe498_replay_1h_v1_symbol_classification_20260526.csv",
  "meme_multiplier_contract_symbols": 11,
  "meme_review_symbols": 6,
  "meme_symbols_high_confidence": 39,
  "meme_symbols_medium_confidence": 17,
  "multiplier_contract_symbols": 13,
  "non_meme_multiplier_contract_symbols": 2,
  "output_taxonomy": "G:\\AlphaFactory_CryptoData\\gold\\metadata\\binance_universe498_contract_meme_taxonomy_v1_20260527.csv",
  "plain_contract_symbols": 485,
  "symbols": 498,
  "warnings": [
    "Meme taxonomy is conservative and intended for stratification/control, not alpha labels",
    "Medium-confidence meme rows require review before proof use",
    "All symbols are futures contracts; taxonomy does not imply spot tradability"
  ]
}
```

## Contract Counts

| contract_format     | is_multiplier_contract   |   contract_unit_multiplier |   symbols |
|:--------------------|:-------------------------|---------------------------:|----------:|
| plain_contract      | False                    |                          1 |       485 |
| multiplier_contract | True                     |                       1000 |        10 |
| multiplier_contract | True                     |                    1000000 |         3 |

## Meme Counts

| is_meme_token   | meme_confidence   | meme_subtype        |   symbols |
|:----------------|:------------------|:--------------------|----------:|
| True            | high              | culture_meme        |        12 |
| True            | medium            | culture_meme        |        10 |
| True            | high              | dog                 |         9 |
| True            | high              | cat                 |         5 |
| True            | medium            | ai_meme             |         5 |
| True            | high              | animal_meme         |         4 |
| True            | high              | ai_meme             |         3 |
| True            | high              | political_meme      |         3 |
| True            | medium            | animal_meme         |         2 |
| True            | high              | btc_meme            |         1 |
| True            | high              | frog                |         1 |
| True            | high              | internet_meme       |         1 |
| False           | none              | not_meme_or_unknown |       436 |
| False           | review            | review              |         6 |

## Contract x Meme Cross Tab

| meme_contract_group          | liquidity_tier   | search_eligibility            |   symbols |
|:-----------------------------|:-----------------|:------------------------------|----------:|
| meme_multiplier_contract     | tail             | listing_aware                 |         4 |
| meme_multiplier_contract     | top100           | strict_full_history           |         2 |
| meme_multiplier_contract     | top50            | strict_full_history           |         2 |
| meme_multiplier_contract     | top20            | strict_full_history           |         1 |
| meme_multiplier_contract     | top200           | listing_aware                 |         1 |
| meme_multiplier_contract     | top200           | strict_full_history           |         1 |
| meme_plain_contract          | tail             | listing_aware                 |        18 |
| meme_plain_contract          | top200           | listing_aware                 |        11 |
| meme_plain_contract          | top100           | listing_aware                 |         7 |
| meme_plain_contract          | top50            | listing_aware                 |         3 |
| meme_plain_contract          | top20            | listing_aware                 |         2 |
| meme_plain_contract          | top20            | strict_full_history           |         2 |
| meme_plain_contract          | top100           | strict_full_history           |         1 |
| meme_plain_contract          | top20            | hold_quality_or_short_history |         1 |
| non_meme_multiplier_contract | tail             | strict_full_history           |         1 |
| non_meme_multiplier_contract | top200           | strict_full_history           |         1 |
| non_meme_plain_contract      | tail             | listing_aware                 |       187 |
| non_meme_plain_contract      | tail             | strict_full_history           |        78 |
| non_meme_plain_contract      | top200           | listing_aware                 |        44 |
| non_meme_plain_contract      | top200           | strict_full_history           |        41 |
| non_meme_plain_contract      | top100           | strict_full_history           |        22 |
| non_meme_plain_contract      | top100           | listing_aware                 |        18 |
| non_meme_plain_contract      | top50            | strict_full_history           |        18 |
| non_meme_plain_contract      | top20            | strict_full_history           |        11 |
| non_meme_plain_contract      | tail             | hold_quality_or_short_history |        10 |
| non_meme_plain_contract      | top50            | listing_aware                 |         7 |
| non_meme_plain_contract      | top20            | listing_aware                 |         3 |
| non_meme_plain_contract      | top200           | hold_quality_or_short_history |         1 |

## Top Meme / Meme-Like Contracts By Liquidity

| symbol          | underlying_asset   | contract_format     |   contract_unit_multiplier |   liquidity_rank | liquidity_tier   | search_eligibility            | is_meme_token   | meme_confidence   | meme_subtype   | meme_review_note                                     |
|:----------------|:-------------------|:--------------------|---------------------------:|-----------------:|:-----------------|:------------------------------|:----------------|:------------------|:---------------|:-----------------------------------------------------|
| DOGEUSDT        | DOGE               | plain_contract      |                          1 |                5 | top20            | strict_full_history           | True            | high              | dog            |                                                      |
| 1000PEPEUSDT    | PEPE               | multiplier_contract |                       1000 |                6 | top20            | strict_full_history           | True            | high              | frog           |                                                      |
| WIFUSDT         | WIF                | plain_contract      |                          1 |               10 | top20            | strict_full_history           | True            | high              | dog            |                                                      |
| FARTCOINUSDT    | FARTCOIN           | plain_contract      |                          1 |               12 | top20            | listing_aware                 | True            | high              | culture_meme   |                                                      |
| TRUMPUSDT       | TRUMP              | plain_contract      |                          1 |               17 | top20            | listing_aware                 | True            | high              | political_meme |                                                      |
| PUMPUSDT        | PUMP               | plain_contract      |                          1 |               18 | top20            | hold_quality_or_short_history | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| 1000SHIBUSDT    | SHIB               | multiplier_contract |                       1000 |               27 | top50            | strict_full_history           | True            | high              | dog            |                                                      |
| 1000BONKUSDT    | BONK               | multiplier_contract |                       1000 |               29 | top50            | strict_full_history           | True            | high              | dog            |                                                      |
| PENGUUSDT       | PENGU              | plain_contract      |                          1 |               33 | top50            | listing_aware                 | True            | high              | animal_meme    |                                                      |
| NEIROUSDT       | NEIRO              | plain_contract      |                          1 |               46 | top50            | listing_aware                 | True            | high              | dog            |                                                      |
| PNUTUSDT        | PNUT               | plain_contract      |                          1 |               47 | top50            | listing_aware                 | True            | high              | animal_meme    |                                                      |
| POPCATUSDT      | POPCAT             | plain_contract      |                          1 |               54 | top100           | listing_aware                 | True            | high              | cat            |                                                      |
| 1000FLOKIUSDT   | FLOKI              | multiplier_contract |                       1000 |               55 | top100           | strict_full_history           | True            | high              | dog            |                                                      |
| 1000SATSUSDT    | SATS               | multiplier_contract |                       1000 |               57 | top100           | strict_full_history           | True            | high              | btc_meme       |                                                      |
| BOMEUSDT        | BOME               | plain_contract      |                          1 |               61 | top100           | listing_aware                 | True            | high              | culture_meme   |                                                      |
| PEOPLEUSDT      | PEOPLE             | plain_contract      |                          1 |               65 | top100           | strict_full_history           | False           | review            | review         | DAO/social token, not automatically meme             |
| GIGGLEUSDT      | GIGGLE             | plain_contract      |                          1 |               69 | top100           | listing_aware                 | True            | high              | culture_meme   |                                                      |
| MOODENGUSDT     | MOODENG            | plain_contract      |                          1 |               72 | top100           | listing_aware                 | True            | high              | animal_meme    |                                                      |
| TURBOUSDT       | TURBO              | plain_contract      |                          1 |               74 | top100           | listing_aware                 | True            | high              | ai_meme        |                                                      |
| APEUSDT         | APE                | plain_contract      |                          1 |               77 | top100           | strict_full_history           | False           | review            | review         | nft/social token, not automatically meme             |
| SPXUSDT         | SPX                | plain_contract      |                          1 |               78 | top100           | listing_aware                 | True            | high              | culture_meme   |                                                      |
| NOTUSDT         | NOT                | plain_contract      |                          1 |               92 | top100           | listing_aware                 | False           | review            | review         | social/game token, review before meme treatment      |
| MEMEUSDT        | MEME               | plain_contract      |                          1 |               95 | top100           | strict_full_history           | True            | high              | culture_meme   |                                                      |
| PIPPINUSDT      | PIPPIN             | plain_contract      |                          1 |               98 | top100           | listing_aware                 | True            | high              | ai_meme        |                                                      |
| 1000RATSUSDT    | RATS               | multiplier_contract |                       1000 |              110 | top200           | strict_full_history           | True            | high              | animal_meme    |                                                      |
| GOATUSDT        | GOAT               | plain_contract      |                          1 |              114 | top200           | listing_aware                 | True            | high              | ai_meme        |                                                      |
| USELESSUSDT     | USELESS            | plain_contract      |                          1 |              124 | top200           | listing_aware                 | True            | high              | culture_meme   |                                                      |
| DOGSUSDT        | DOGS               | plain_contract      |                          1 |              136 | top200           | listing_aware                 | True            | high              | dog            | high-confidence meme but also app/community token    |
| ACTUSDT         | ACT                | plain_contract      |                          1 |              156 | top200           | listing_aware                 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| GRIFFAINUSDT    | GRIFFAIN           | plain_contract      |                          1 |              168 | top200           | listing_aware                 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| MEWUSDT         | MEW                | plain_contract      |                          1 |              171 | top200           | listing_aware                 | True            | high              | cat            |                                                      |
| BRETTUSDT       | BRETT              | plain_contract      |                          1 |              175 | top200           | listing_aware                 | True            | high              | culture_meme   |                                                      |
| MUBARAKUSDT     | MUBARAK            | plain_contract      |                          1 |              179 | top200           | listing_aware                 | True            | high              | political_meme |                                                      |
| CHILLGUYUSDT    | CHILLGUY           | plain_contract      |                          1 |              186 | top200           | listing_aware                 | True            | high              | culture_meme   |                                                      |
| JELLYJELLYUSDT  | JELLYJELLY         | plain_contract      |                          1 |              190 | top200           | listing_aware                 | True            | high              | culture_meme   |                                                      |
| ZEREBROUSDT     | ZEREBRO            | plain_contract      |                          1 |              192 | top200           | listing_aware                 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| 1MBABYDOGEUSDT  | BABYDOGE           | multiplier_contract |                    1000000 |              195 | top200           | listing_aware                 | True            | high              | dog            |                                                      |
| SWARMSUSDT      | SWARMS             | plain_contract      |                          1 |              205 | tail             | listing_aware                 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| ANIMEUSDT       | ANIME              | plain_contract      |                          1 |              208 | tail             | listing_aware                 | False           | review            | review         | culture token, review before meme treatment          |
| COOKIEUSDT      | COOKIE             | plain_contract      |                          1 |              211 | tail             | listing_aware                 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| 1000000MOGUSDT  | MOG                | multiplier_contract |                    1000000 |              215 | tail             | listing_aware                 | True            | high              | cat            |                                                      |
| MELANIAUSDT     | MELANIA            | plain_contract      |                          1 |              216 | tail             | listing_aware                 | True            | high              | political_meme |                                                      |
| BANANAS31USDT   | BANANAS31          | plain_contract      |                          1 |              217 | tail             | listing_aware                 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| 1000CATUSDT     | CAT                | multiplier_contract |                       1000 |              256 | tail             | listing_aware                 | True            | high              | cat            |                                                      |
| TSTUSDT         | TST                | plain_contract      |                          1 |              275 | tail             | listing_aware                 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| HMSTRUSDT       | HMSTR              | plain_contract      |                          1 |              278 | tail             | listing_aware                 | True            | medium            | animal_meme    | game/community token with meme-like behavior         |
| BROCCOLI714USDT | BROCCOLI714        | plain_contract      |                          1 |              298 | tail             | listing_aware                 | True            | high              | culture_meme   |                                                      |
| CATIUSDT        | CATI               | plain_contract      |                          1 |              313 | tail             | listing_aware                 | False           | review            | review         | game/app token, do not infer meme from CAT substring |
| 1000CHEEMSUSDT  | CHEEMS             | multiplier_contract |                       1000 |              345 | tail             | listing_aware                 | True            | high              | dog            |                                                      |
| BANUSDT         | BAN                | plain_contract      |                          1 |              386 | tail             | listing_aware                 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| DOODUSDT        | DOOD               | plain_contract      |                          1 |              425 | tail             | listing_aware                 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| BULLAUSDT       | BULLA              | plain_contract      |                          1 |              433 | tail             | listing_aware                 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| TOSHIUSDT       | TOSHI              | plain_contract      |                          1 |              434 | tail             | listing_aware                 | True            | high              | cat            |                                                      |
| KOMAUSDT        | KOMA               | plain_contract      |                          1 |              453 | tail             | listing_aware                 | True            | high              | culture_meme   |                                                      |
| CLANKERUSDT     | CLANKER            | plain_contract      |                          1 |              460 | tail             | listing_aware                 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| FLOCKUSDT       | FLOCK              | plain_contract      |                          1 |              462 | tail             | listing_aware                 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| SPORTFUNUSDT    | SPORTFUN           | plain_contract      |                          1 |              464 | tail             | listing_aware                 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| TURTLEUSDT      | TURTLE             | plain_contract      |                          1 |              471 | tail             | listing_aware                 | True            | medium            | animal_meme    | medium-confidence meme/social classification         |
| BROCCOLIF3BUSDT | BROCCOLIF3B        | plain_contract      |                          1 |              473 | tail             | listing_aware                 | True            | high              | culture_meme   |                                                      |
| IDOLUSDT        | IDOL               | plain_contract      |                          1 |              482 | tail             | listing_aware                 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| PUMPBTCUSDT     | PUMPBTC            | plain_contract      |                          1 |              486 | tail             | listing_aware                 | False           | review            | review         | wrapped/derivative naming, not direct meme token     |
| 1000000BOBUSDT  | BOB                | multiplier_contract |                    1000000 |              492 | tail             | listing_aware                 | True            | high              | internet_meme  |                                                      |

## Review Flags

| symbol        | underlying_asset   |   liquidity_rank | is_meme_token   | meme_confidence   | meme_subtype   | meme_review_note                                     |
|:--------------|:-------------------|-----------------:|:----------------|:------------------|:---------------|:-----------------------------------------------------|
| PUMPUSDT      | PUMP               |               18 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| PEOPLEUSDT    | PEOPLE             |               65 | False           | review            | review         | DAO/social token, not automatically meme             |
| APEUSDT       | APE                |               77 | False           | review            | review         | nft/social token, not automatically meme             |
| NOTUSDT       | NOT                |               92 | False           | review            | review         | social/game token, review before meme treatment      |
| ACTUSDT       | ACT                |              156 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| GRIFFAINUSDT  | GRIFFAIN           |              168 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| ZEREBROUSDT   | ZEREBRO            |              192 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| SWARMSUSDT    | SWARMS             |              205 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| ANIMEUSDT     | ANIME              |              208 | False           | review            | review         | culture token, review before meme treatment          |
| COOKIEUSDT    | COOKIE             |              211 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| BANANAS31USDT | BANANAS31          |              217 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| TSTUSDT       | TST                |              275 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| HMSTRUSDT     | HMSTR              |              278 | True            | medium            | animal_meme    | game/community token with meme-like behavior         |
| CATIUSDT      | CATI               |              313 | False           | review            | review         | game/app token, do not infer meme from CAT substring |
| BANUSDT       | BAN                |              386 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| DOODUSDT      | DOOD               |              425 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| BULLAUSDT     | BULLA              |              433 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| CLANKERUSDT   | CLANKER            |              460 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| FLOCKUSDT     | FLOCK              |              462 | True            | medium            | ai_meme        | medium-confidence meme/social classification         |
| SPORTFUNUSDT  | SPORTFUN           |              464 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| TURTLEUSDT    | TURTLE             |              471 | True            | medium            | animal_meme    | medium-confidence meme/social classification         |
| IDOLUSDT      | IDOL               |              482 | True            | medium            | culture_meme   | medium-confidence meme/social classification         |
| PUMPBTCUSDT   | PUMPBTC            |              486 | False           | review            | review         | wrapped/derivative naming, not direct meme token     |

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
