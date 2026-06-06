# CRYPTO A7LS-16 LOCAL PREFLIGHT

Generated: 2026-06-06T05:09:13Z

## Decision

`PASS_A7LS16_LOCAL_SCHEMA_PREFLIGHT_READY_FOR_A7LS17_COMPANY_MATERIALIZATION`

## Mode

Local schema/queue preflight only. Numeric materialization smoke is intentionally not run on the local machine by default; A7LS17 handles company-machine materialization.

## Summary

- sample_rows: 256
- requested_field_count: 61
- missing_field_count: 0
- operator_count: 13
- unsupported_operator_count: 0

## Lane Summary

| a7ls_lane   |   rows |   semantic_pairs |   motifs |   skeletons |
|:------------|-------:|-----------------:|---------:|------------:|
| A7LS14_A    |     64 |               64 |        8 |          42 |
| A7LS14_B    |     64 |               55 |        4 |           5 |
| A7LS14_C    |     64 |                9 |       11 |          24 |
| A7LS14_D    |     64 |                7 |        6 |          16 |

## Field Status

| status                                                |   fields |
|:------------------------------------------------------|---------:|
| base                                                  |       26 |
| computed_dense_funding                                |        5 |
| computed_derived                                      |        3 |
| latent                                                |       22 |
| upper_regime_alias:R10_stress_proxy_state             |        1 |
| upper_regime_alias:R2_market_breadth_state            |        1 |
| upper_regime_alias:R3_liquidity_cycle_state           |        1 |
| upper_regime_alias:R4_leverage_crowding_state         |        1 |
| upper_regime_alias:R5_basis_premium_dislocation_state |        1 |

## Operator Status

| operator   | status    |
|:-----------|:----------|
| Abs        | supported |
| CSRank     | supported |
| Clip       | supported |
| Decay      | supported |
| Delta      | supported |
| Mean       | supported |
| Mul        | supported |
| Neg        | supported |
| SafeDiv    | supported |
| Sign       | supported |
| Sub        | supported |
| TSRank     | supported |
| ZScore     | supported |
