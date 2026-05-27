# CRYPTO A7AL-0G Upper Regime State Builder

Generated: 2026-05-27T03:31:59Z

## Decision

```text
PASS_A7AL0G_UPPER_REGIME_STATE_BUILDER
```

Upper regime states are derived from observable top498 panel features. Thresholds are train-only and then frozen.

## Summary

```json
{
  "generated_at": "2026-05-27T03:31:59Z",
  "decision": "PASS_A7AL0G_UPPER_REGIME_STATE_BUILDER",
  "output_panel": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_upper_regime_state_v1_20260527.parquet",
  "rows": 20424,
  "columns": 35,
  "regime_states": 11,
  "executes_search": false,
  "executes_replay": false,
  "train_only_thresholds": true,
  "may_used": false,
  "authorizes_a7al0p_pretrain_gate": true,
  "authorizes_a7al1_baseline": false,
  "blockers": []
}
```

## Regime Contract

| regime_id | input_fields | economic_role | fit_rule | apply_rule | may_used | allowed_for_rank | allowed_for_regime | allowed_for_search_interaction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R0_market_trend | market_ret_24h_median | market trend / reversal pressure | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R1_market_volatility | market_vol_168h_median | aggregate volatility state | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R2_market_breadth | market_breadth_positive | cross-sectional breadth | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R3_liquidity_cycle | market_liquidity_log_median | market liquidity cycle | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R4_leverage_crowding | leverage_oi_change_median + funding_abs_median | aggregate leverage/funding crowding | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R5_basis_premium_dislocation | basis_abs_median + premium_abs_median | basis/premium dislocation | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R6_positioning_crowding | top_long_short_position_median | positioning crowding | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R7_meme_risk_on | meme_vs_nonmeme_ret_24h | meme risk-on state | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R8_listing_cycle_pressure | listing_age_lt30_share | listing lifecycle pressure | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R9_alt_vs_major_dispersion | alt_vs_major_ret_24h | alt vs major relative state | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |
| R10_stress_proxy | volatility high + breadth weak | market stress proxy | thresholds fit on train_2024 only | validation/test/recent apply frozen thresholds | False | False | True | True |

## Coverage By Split

| split | timestamps | active_symbols_median | R0_market_trend_state_states | R0_market_trend_state_missing | R1_market_volatility_state_states | R1_market_volatility_state_missing | R2_market_breadth_state_states | R2_market_breadth_state_missing | R3_liquidity_cycle_state_states | R3_liquidity_cycle_state_missing | R4_leverage_crowding_state_states | R4_leverage_crowding_state_missing | R5_basis_premium_dislocation_state_states | R5_basis_premium_dislocation_state_missing | R6_positioning_crowding_state_states | R6_positioning_crowding_state_missing | R7_meme_risk_on_state_states | R7_meme_risk_on_state_missing | R8_listing_cycle_pressure_state_states | R8_listing_cycle_pressure_state_missing | R9_alt_vs_major_dispersion_state_states | R9_alt_vs_major_dispersion_state_missing | R10_stress_proxy_state_states | R10_stress_proxy_state_missing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| recent_oos_2026JanApr | 2880 | 498.0 | 3 | 0 | 3 | 0 | 3 | 0 | 1 | 0 | 3 | 0 | 1 | 0 | 3 | 0 | 3 | 0 | 1 | 0 | 3 | 0 | 3 | 0 |
| test_2025H2 | 4416 | 440.0 | 3 | 0 | 3 | 0 | 3 | 0 | 1 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 |
| train_2024 | 8784 | 211.0 | 3 | 24 | 3 | 48 | 3 | 0 | 3 | 23 | 3 | 44 | 3 | 0 | 3 | 10 | 3 | 24 | 3 | 0 | 3 | 24 | 3 | 0 |
| validation_2025H1 | 4344 | 325.0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 | 3 | 0 |

## Transition Audit

| regime_state | transitions | transition_rate | distinct_states |
| --- | --- | --- | --- |
| R0_market_trend_state | 3352 | 0.16412064238151194 | 3 |
| R1_market_volatility_state | 306 | 0.014982373678025853 | 3 |
| R2_market_breadth_state | 3256 | 0.15942028985507245 | 3 |
| R3_liquidity_cycle_state | 53 | 0.0025949862906384648 | 3 |
| R4_leverage_crowding_state | 2893 | 0.14164708186447317 | 3 |
| R5_basis_premium_dislocation_state | 157 | 0.007687034860947905 | 3 |
| R6_positioning_crowding_state | 391 | 0.019144144144144143 | 3 |
| R7_meme_risk_on_state | 3679 | 0.18013121817469643 | 3 |
| R8_listing_cycle_pressure_state | 80 | 0.0039169604386995694 | 3 |
| R9_alt_vs_major_dispersion_state | 3778 | 0.18497845671758714 | 3 |
| R10_stress_proxy_state | 1076 | 0.0526831179005092 | 3 |

## Boundary

```text
AUTHORIZED NEXT:
  A7AL-0P pre-train readiness gate

NOT AUTHORIZED:
  A7AL-1 baseline replay
  formula search
  alpha proof / shadow / paper / live
```
