# Native aggTrades scoped release qualification

Status: `NATIVE_AGGTRADES_RELEASE_QUALIFIED_SCOPED`

- Scope: Binance UM core12, 2024-01..10; development 2024-01..06 and physically separate challenge 2024-07..10.
- Qualified symbol-months: `117/120` (`97.50%`).
- Development coverage: `97.22%`; challenge coverage: `97.92%`.
- Excluded before performance: BTCUSDT 2024-03, AVAXUSDT 2024-04, BNBUSDT 2024-08 because no matching official-checksum lineage was found. No interpolation was used.
- 2024-11/12 are quarantined outside the release contract because source checksum gaps would push the challenge panel below the 95% target.
- Reverse-order and shard-order materialization hashes match: `9A715BD4EC8461E533BFBA43B33CC67A30596E026800DF90CD604BBB02BF9A3D`.
- No return label, reward, forward block, candidate selection, promotion, or memory was read or updated.
