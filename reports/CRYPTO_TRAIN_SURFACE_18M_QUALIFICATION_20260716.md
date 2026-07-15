# Crypto Train Surface 18M Qualification

## Decision

`PASS_CRYPTO_TRAIN_SURFACE_18M_DEVELOPMENT_READY_WITH_SCOPE_LIMITS`

The train surface is now 2023-07-01 through 2024-12-31 only.  No 2025+
row is returned, no formal search was run, and no economic claim is made.

## Corrected train facts

- rows: 2,549,139
- unique hourly timestamps: 13,200
- assets observed: 276
- assets with any 2024 rows: 276
- assets present in every 2024 month: 183
- assets with all 8,784 hours in 2024: 176
- assets spanning both 2023H2 and 2024: 176
- monthly active asset range: 140 to 276
- continuous months: 18
- current Git runtime fields materializable: 10/10
- source content bundle SHA256: `8CEB549ED8AF73611163D827AD15DD5F409DCD422A6831ABCA28E86B8627D439`

## Git field reconciliation

- inventory identities checked: 5,388
- physical normalized fields common to both periods: 72
- common physical fields registered in the inventory: 51
- current runtime fields admitted: 10
- physical fields are not automatically search-authorized; the current 10-field runtime contract remains the activation boundary.

## Runtime field quality

| field_id                             |   non_null_ratio |     variance |   assets_with_time_variation | gate_pass   |
|:-------------------------------------|-----------------:|-------------:|-----------------------------:|:------------|
| account_position_divergence          |         0.998886 |  0.944534    |                          276 | True        |
| global_long_short_account_ratio_last |         0.998886 |  1.02149     |                          276 | True        |
| mark_trade_basis_bps                 |         0.999134 | 23.786       |                          276 | True        |
| open_interest_value_last             |         0.998886 |  1.65589e+17 |                          276 | True        |
| open_interest_value_mean             |         0.998886 |  1.65388e+17 |                          276 | True        |
| top_global_account_divergence        |         0.998886 |  0.163915    |                          276 | True        |
| top_long_short_account_ratio_last    |         0.998886 |  1.08446     |                          276 | True        |
| top_long_short_position_ratio_last   |         0.998886 |  0.500807    |                          276 | True        |
| trade_close                          |         1        |  1.77351e+07 |                          276 | True        |
| trade_quote_volume                   |         1        |  6.13622e+15 |                          276 | True        |

## Supersession scope

- superseded: TIME_HISTORY_TOO_SHORT_FOR_OBSERVED_ARCHIVE_KLINE_DERIVATIVES_TRAIN_SURFACE, A7EFF2_96_ASSETS_AS_PHYSICAL_PANEL_LIMIT
- remains unresolved: SURVIVORSHIP_OR_ELIGIBILITY_UNRESOLVED, ORDER_FIELD_COVERAGE_FRAGMENTED, EXPLICIT_CORE_AGGTRADES_TIME_HISTORY_TOO_SHORT, COMPOSITIONAL_GRAMMAR_BOTTLENECK_NO_NEW_ECONOMIC_TEST
- the 96-asset A7EFF2 numeric cache is classified as a cache scope, not the physical 2024 panel limit.

## Boundaries

- observed-archive/current-seed universe only; omitted delisted contracts remain possible.
- native aggTrades order-field history is still only the smaller historical release.
- validation, test, recent, May stress, challenge, and forward remain sealed.
- no candidate promotion and no cross-sprint adaptive memory.
