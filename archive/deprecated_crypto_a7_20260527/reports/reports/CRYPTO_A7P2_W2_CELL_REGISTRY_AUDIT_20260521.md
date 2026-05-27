# Crypto A7P-2 W2 Cell Registry Audit

- generated_at: `2026-05-20T18:27:57Z`
- decision: `PASS_A7P2CDE_W2_REGISTRY_READY_FOR_PROTECTED_PILOT_REVIEW`
- executes_new_search: `False`
- executes_replay: `False`
- authorizes_w2_pilot: `True`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`
- blockers: `[]`

## Coverage Audit

| metric                                      |     value |   threshold | operator   | pass   |
|:--------------------------------------------|----------:|------------:|:-----------|:-------|
| registry_cell_count                         | 64        |       64    | >=         | True   |
| primary_cell_count                          | 61        |       60    | >=         | True   |
| supplemental_cell_count                     |  3        |        4    | <=         | True   |
| quarantined_cells_in_registry               |  0        |        0    | =          | True   |
| policy_uses_may                             |  0        |        0    | =          | True   |
| registry_score_uses_may                     |  0        |        0    | =          | True   |
| registry_selection_uses_may                 |  0        |        0    | =          | True   |
| hypothesis_family_count                     | 13        |        8    | >=         | True   |
| feature_family_count                        | 14        |        8    | >=         | True   |
| single_hypothesis_family_share              |  0.15625  |        0.25 | <=         | True   |
| single_feature_family_share                 |  0.171875 |        0.25 | <=         | True   |
| single_feature_operator_horizon_motif_share |  0.015625 |        0.15 | <=         | True   |
| liquidity_volatility_cell_share             |  0.046875 |        0.15 | <=         | True   |
| control_contaminated_cells_quarantined      |  2        |        2    | >=         | True   |

## Quarantined Cells

|   checkpoint_id | cell_id   | recommended_action                   | primary_reason                                                     |
|----------------:|:----------|:-------------------------------------|:-------------------------------------------------------------------|
|               4 | C0208     | quarantine_control_contaminated_cell | negative_control_contamination;raw_weak;liquidity_volatility_heavy |
|               4 | C0223     | quarantine_control_contaminated_cell | negative_control_contamination;raw_weak                            |

## W2 Registry Preview

|   registry_rank |   checkpoint_id | cell_id   | registry_tier                        | hypothesis_family                           | feature_family_set    | operator_motif     | temporal_horizon_class   |   registry_score_non_may | may_used_for_registry_score   | may_used_for_registry_selection   |
|----------------:|----------------:|:----------|:-------------------------------------|:--------------------------------------------|:----------------------|:-------------------|:-------------------------|-------------------------:|:------------------------------|:----------------------------------|
|               1 |               2 | C0064     | primary_control_clean_non_may_robust | H05_volatility_structure_ex_liquidity_mul   | P11_volatility_basis  | NegRank            | H48                      |                0.620833  | False                         | False                             |
|               2 |               3 | C0132     | primary_control_clean_non_may_robust | H02_cross_symbol_dispersion_reversal        | P1_range_volatility   | ResidualizeVsCore4 | H72                      |                0.529167  | False                         | False                             |
|               3 |               1 | C0031     | primary_control_clean_non_may_robust | H08_trade_size_microstructure_lite          | P3_trade_size         | SubRank            | H48                      |                0.495833  | False                         | False                             |
|               4 |               3 | C0160     | primary_control_clean_non_may_robust | H10_range_breakout_failure                  | P1_range_volatility   | NegRank            | H24                      |                0.43125   | False                         | False                             |
|               5 |               4 | C0222     | primary_control_clean_non_may_robust | H02_cross_symbol_dispersion_reversal        | P1_range_volatility   | AddZScore          | H24                      |                0.4       | False                         | False                             |
|               6 |               4 | C0213     | primary_control_clean_non_may_robust | H12_horizon_ensemble_stability              | P11_volatility_basis  | NegRank            | H12                      |                0.377083  | False                         | False                             |
|               7 |               3 | C0169     | primary_control_clean_non_may_robust | H14_open_ast_cem_diversity                  | P3_trade_size         | WinsorZScore       | H48                      |                0.302083  | False                         | False                             |
|               8 |               1 | C0063     | primary_control_clean_non_may_robust | H12_horizon_ensemble_stability              | P10_price_liquidity   | TSRankMul          | H72                      |                0.26875   | False                         | False                             |
|               9 |               5 | C0280     | primary_control_clean_non_may_robust | H05_volatility_structure_ex_liquidity_mul   | P5_basis_premium      | Rank               | H72                      |                0.2625    | False                         | False                             |
|              10 |               1 | C0025     | primary_control_clean_non_may_robust | H02_cross_symbol_dispersion_reversal        | P0_price_return       | TSStdZScore        | mixed_6_24               |                0.260417  | False                         | False                             |
|              11 |               5 | C0318     | primary_control_clean_non_may_robust | H07_taker_flow_lag_stable                   | P11_volatility_basis  | RollingMinRank     | ensemble_6_12_24_48      |                0.258333  | False                         | False                             |
|              12 |               5 | C0270     | primary_control_clean_non_may_robust | H02_cross_symbol_dispersion_reversal        | P10_price_liquidity   | SmoothInteraction  | H12                      |                0.254167  | False                         | False                             |
|              13 |               3 | C0187     | primary_control_clean_non_may_robust | H07_taker_flow_lag_stable                   | P1_range_volatility   | AddZScore          | mixed_12_48              |                0.214583  | False                         | False                             |
|              14 |               3 | C0166     | primary_control_clean_non_may_robust | H02_cross_symbol_dispersion_reversal        | P1_range_volatility   | SafeDivZScore      | mixed_6_24               |                0.18125   | False                         | False                             |
|              15 |               1 | C0032     | primary_control_clean_non_may_robust | H02_cross_symbol_dispersion_reversal        | P0_price_return       | TSStdZScore        | spread_12_vs_48          |                0.145833  | False                         | False                             |
|              16 |               6 | C0360     | primary_control_clean_non_may_robust | H11_regime_conditional_non_may              | P3_trade_size         | ClipRank           | H24                      |                0.120833  | False                         | False                             |
|              17 |               4 | C0252     | primary_control_clean_non_may_robust | H05_volatility_structure_ex_liquidity_mul   | P6_funding_observable | AddZScore          | H24                      |                0.114583  | False                         | False                             |
|              18 |               6 | C0339     | primary_control_clean_non_may_robust | H10_range_breakout_failure                  | P11_volatility_basis  | RollingMinRank     | spread_6_vs_24           |                0.104167  | False                         | False                             |
|              19 |               2 | C0094     | primary_control_clean_non_may_robust | H05_volatility_structure_ex_liquidity_mul   | P10_price_liquidity   | HorizonSpread      | H48                      |                0.104167  | False                         | False                             |
|              20 |               4 | C0200     | primary_control_clean_non_may_robust | H05_volatility_structure_ex_liquidity_mul   | P1_range_volatility   | MulRankRank        | spread_6_vs_24           |                0.0979167 | False                         | False                             |
|              21 |               1 | C0017     | primary_control_clean_non_may_robust | H00_low_turnover_robust                     | P2_liquidity          | TSStdZScore        | H72                      |                0.0958333 | False                         | False                             |
|              22 |               5 | C0316     | primary_control_clean_non_may_robust | H07_taker_flow_lag_stable                   | P1_range_volatility   | RollingMaxRank     | H72                      |                0.0666667 | False                         | False                             |
|              23 |               4 | C0227     | primary_control_clean_non_may_robust | H11_regime_conditional_non_may              | P11_volatility_basis  | TSRankMul          | H72                      |                0.0604167 | False                         | False                             |
|              24 |               5 | C0289     | primary_control_clean_non_may_robust | H08_trade_size_microstructure_lite          | P0_price_return       | TSStdZScore        | H24                      |                0.0395833 | False                         | False                             |
|              25 |               4 | C0241     | primary_control_clean_non_may_robust | H06_liquidity_structure_ex_realized_vol_mul | P14_horizon_spread    | HorizonSpread      | mixed_6_24               |                0.0291667 | False                         | False                             |
|              26 |               4 | C0229     | primary_control_clean_non_may_robust | H06_liquidity_structure_ex_realized_vol_mul | P10_price_liquidity   | AddZScore          | ensemble_6_12_24_48      |                0.0270833 | False                         | False                             |
|              27 |               3 | C0134     | primary_control_clean_non_may_robust | H05_volatility_structure_ex_liquidity_mul   | P1_range_volatility   | DecayZScore        | mixed_12_48              |               -0.00625   | False                         | False                             |
|              28 |               3 | C0151     | primary_control_clean_non_may_robust | H11_regime_conditional_non_may              | P12_liquidity_flow    | TSStdZScore        | spread_6_vs_24           |               -0.0208333 | False                         | False                             |
|              29 |               6 | C0337     | primary_control_clean_non_may_robust | H07_taker_flow_lag_stable                   | P10_price_liquidity   | ResidualizeVsCore4 | H72                      |               -0.0270833 | False                         | False                             |
|              30 |               1 | C0050     | primary_control_clean_non_may_robust | H05_volatility_structure_ex_liquidity_mul   | P3_trade_size         | ZScore             | spread_6_vs_24           |               -0.0395833 | False                         | False                             |

## Boundary

This audit only builds and checks a control-clean W2 registry. It does not execute W2, full L1, L2/L3, alpha proof, shadow, paper, or live.