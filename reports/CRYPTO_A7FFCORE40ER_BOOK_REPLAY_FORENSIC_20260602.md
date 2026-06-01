# CRYPTO A7FF-CORE40ER BOOK REPLAY FORENSIC

Generated: 2026-06-01T20:25:14Z

## Decision

`PASS_A7FFCORE40ER_BOOK_REPLAY_FORENSIC_READY_FOR_CORE41_CONTRACT`

CORE40ER freezes the CORE40E book replay failure. It does not run replay, generation, search, alpha proof, shadow, paper, or live.

## Main Finding

`book_objective_control_dominated`

The symbol-level book packet makes the objective computable, and several objective medians are positive. The blocker is that stale/sign-flip controls remain as strong or stronger than the original book response.

## Objective Forensic

| objective_id                  |   replay_rows |   positive_rows |   control_clean_rows |   median_net_book_return |   median_control_ratio | diagnosis         |
|:------------------------------|--------------:|----------------:|---------------------:|-------------------------:|-----------------------:|:------------------|
| B1_cross_sectional_rank_book  |           168 |              88 |                   46 |               0.0040954  |                1.56025 | control_dominated |
| B2_market_beta_residual_book  |           168 |              86 |                   47 |               0.00315561 |                1.58252 | control_dominated |
| B3_vol_adjusted_rank_book     |           168 |              87 |                   47 |               0.14006    |                1.33276 | control_dominated |
| B4_liquidity_cost_capped_book |           168 |              95 |                   50 |               0.0012116  |                1.39518 | control_dominated |

## Failure Counts

| family_id                         | failure_reason             |   candidate_count |
|:----------------------------------|:---------------------------|------------------:|
| F1a_aggtrades_flow_microstructure | train_control_dominated    |                 5 |
| F1a_aggtrades_flow_microstructure | train_book_net_nonpositive |                 2 |
| F1b_taker_flow_market_panel       | train_book_net_nonpositive |                 4 |
| F1b_taker_flow_market_panel       | train_control_dominated    |                 2 |
| F2a_basis_funding_independent     | train_book_net_nonpositive |                 4 |
| F2a_basis_funding_independent     | train_control_dominated    |                 4 |

## Split Objective Forensic

| objective_id                  | split             |   replay_rows |   positive_rows |   control_clean_rows |   median_net_book_return |   median_control_ratio |
|:------------------------------|:------------------|--------------:|----------------:|---------------------:|-------------------------:|-----------------------:|
| B1_cross_sectional_rank_book  | recent_2026JanApr |            42 |              23 |                    7 |              0.00903037  |                1.89562 |
| B1_cross_sectional_rank_book  | test_2025H2       |            42 |              26 |                   15 |              0.0127965   |                1.5295  |
| B1_cross_sectional_rank_book  | train_2024        |            42 |              20 |                   10 |             -0.005829    |                1.3523  |
| B1_cross_sectional_rank_book  | validation_2025H1 |            42 |              19 |                   14 |             -0.00645963  |                1.545   |
| B2_market_beta_residual_book  | recent_2026JanApr |            42 |              22 |                    7 |              0.00501016  |                1.78392 |
| B2_market_beta_residual_book  | test_2025H2       |            42 |              26 |                   15 |              0.0127965   |                1.53262 |
| B2_market_beta_residual_book  | train_2024        |            42 |              20 |                   10 |             -0.005829    |                1.3523  |
| B2_market_beta_residual_book  | validation_2025H1 |            42 |              18 |                   15 |             -0.00464543  |                1.545   |
| B3_vol_adjusted_rank_book     | recent_2026JanApr |            42 |              19 |                    9 |             -0.88984     |                1.47578 |
| B3_vol_adjusted_rank_book     | test_2025H2       |            42 |              26 |                   10 |              1.85318     |                1.48724 |
| B3_vol_adjusted_rank_book     | train_2024        |            42 |              18 |                   11 |             -0.879322    |                1.26776 |
| B3_vol_adjusted_rank_book     | validation_2025H1 |            42 |              24 |                   17 |              0.615936    |                1.08372 |
| B4_liquidity_cost_capped_book | recent_2026JanApr |            42 |              21 |                    9 |              0.000258623 |                1.59567 |
| B4_liquidity_cost_capped_book | test_2025H2       |            42 |              28 |                   14 |              0.00254281  |                1.3138  |
| B4_liquidity_cost_capped_book | train_2024        |            42 |              22 |                   13 |              0.000269735 |                1.28842 |
| B4_liquidity_cost_capped_book | validation_2025H1 |            42 |              24 |                   14 |              0.00249148  |                1.48568 |

## Authorization Matrix

| task                                               | status                   | reason                                                                              |
|:---------------------------------------------------|:-------------------------|:------------------------------------------------------------------------------------|
| A7FF-CORE41 book-objective control repair contract | AUTHORIZED_CONTRACT_ONLY | book objectives show positive medians but are dominated by stale/sign-flip controls |
| book objective survivor promotion                  | NOT_AUTHORIZED           | survivor_count=0                                                                    |
| formula_search                                     | NOT_AUTHORIZED           | book response is control-dominated                                                  |
| large_search                                       | NOT_AUTHORIZED           | book response is control-dominated                                                  |
| alpha_proof / shadow / paper / live                | NOT_AUTHORIZED           | no proof object                                                                     |

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core41_contract": true,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "book_survivor_count": 0,
  "candidate_count": 21,
  "decision": "PASS_A7FFCORE40ER_BOOK_REPLAY_FORENSIC_READY_FOR_CORE41_CONTRACT",
  "dominant_failure": "book_objective_control_dominated",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-01T20:25:14Z",
  "next_allowed": "A7FF-CORE41 book-objective control repair contract",
  "source_decision": "HOLD_A7FFCORE40E_BOOK_OBJECTIVE_REPLAY_INSUFFICIENT",
  "source_stage": "A7FF-CORE40E",
  "stage": "A7FF-CORE40ER"
}
```
