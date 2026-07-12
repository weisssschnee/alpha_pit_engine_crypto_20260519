# CRYPTO MECHANISM/DATA EXPANSION-0 closure

Status: `MECHANISM_DATA_EXPANSION0_PARTIALLY_COMPLETED`  
Recommendation: `STOP_CRYPTO_ALPHA_DISCOVERY_PENDING_EXTERNAL_DATA`

## What completed

- Inventoried `608073` local/PC1 file observations without row-data or performance access.
- Qualified native aggTrades release `BINANCE_UM_NATIVE_AGGTRADES_CORE12_2024M01_M10_V1` at `97.50%` symbol-month coverage with physical development/challenge separation and deterministic content hash `9A715BD4EC8461E533BFBA43B33CC67A30596E026800DF90CD604BBB02BF9A3D`.
- Executed exactly `164` frozen simple benchmark/control evaluations. `5` base rows had positive gross LCB, `0` had positive net LCB, and `0` benchmark-horizons passed future-search admission.
- Measured native-flow behaviour N_eff `3.3722`; this diversity did not produce a cost-surviving mechanism.
- Verified official Binance UM monthly bookTicker source only for `48/144` full-year coordinates (`33.33%`). May-Dec return HTTP 404, so downloading the available `87.45` GiB cannot satisfy the 95% full-year gate.

## Mechanism decisions

| mechanism                    | decision              | evidence                                                                                                             |
|:-----------------------------|:----------------------|:---------------------------------------------------------------------------------------------------------------------|
| cross_venue_price_discovery  | UNAVAILABLE_NO_SOURCE | only recent/May short probes; no verified longitudinal source                                                        |
| native_aggtrades_trade_flow  | REJECT_NO_EDGE        | qualified 97.5% scoped release; 164 fixed evaluations; zero admitted benchmark-horizons; every base net LCB negative |
| native_bbo_full_year         | HOLD_FOR_MORE_DATA    | official monthly source only 48/144 symbol-months (33.33%); May-Dec HTTP 404                                         |
| multi_level_order_book_depth | UNAVAILABLE_NO_SOURCE | no verified historical snapshots/deltas; BBO not relabelled as depth                                                 |
| forced_flow_liquidation      | UNAVAILABLE_NO_SOURCE | no verified historical force-order/liquidation source; proxy substitution prohibited                                 |
| options_expectation_state    | UNAVAILABLE_NO_SOURCE | no options historical source found on local or PC1                                                                   |

Formal search remains frozen. No candidate was promoted, no spent/forward block was read, and no cross-epoch memory was updated. A future crypto-alpha stage requires an independently verified external historical source (cross-venue, full-year BBO, forced-flow or options); expanding the rejected existing formula space is not authorized.
