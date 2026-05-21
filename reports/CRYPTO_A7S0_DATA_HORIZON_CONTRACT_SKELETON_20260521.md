# Crypto A7S-0 Data / Horizon Contract Skeleton

- generated_at: `2026-05-21T00:44:09Z`
- decision: `PASS_A7S0_DATA_HORIZON_CONTRACT_SKELETON`
- executes_search: `False`
- executes_replay: `False`
- data download / alpha search / alpha proof: `NOT_AUTHORIZED`

## Candidate Data Sources

| source                               |   priority | status            | pit_risk    | expected_value                       |
|:-------------------------------------|-----------:|:------------------|:------------|:-------------------------------------|
| open_interest                        |          1 | contract_required | medium      | market_state_and_leverage            |
| liquidation_events_or_volume         |          2 | contract_required | high        | forced_flow_state                    |
| orderbook_depth_spread_imbalance     |          3 | contract_required | high        | tradability_and_short_horizon_stress |
| cross_exchange_basis_premium         |          4 | contract_required | medium_high | venue_relative_value_state           |
| cross_exchange_funding               |          5 | contract_required | medium_high | funding_dispersion_state             |
| long_short_account_or_position_ratio |          6 | contract_required | medium      | crowding_state                       |

## PIT Timestamp Contract Fields

| field               | required   | description                                                  |
|:--------------------|:-----------|:-------------------------------------------------------------|
| observable_time     | True       | Timestamp when the value is available for signal generation. |
| event_time          | True       | Exchange or vendor event timestamp.                          |
| publication_delay   | True       | Delay between event and observability.                       |
| symbol_coverage     | True       | Per-symbol availability and missingness.                     |
| aggregation_lag     | True       | Lag added before joining to 1h/4h/24h panels.                |
| survivorship_policy | True       | Handling of listing, delisting, and inactive markets.        |

## Boundary

This skeleton does not authorize data acquisition or alpha search. Each candidate source must pass field semantics, timestamp observability, publication delay, coverage, and cost review before use.