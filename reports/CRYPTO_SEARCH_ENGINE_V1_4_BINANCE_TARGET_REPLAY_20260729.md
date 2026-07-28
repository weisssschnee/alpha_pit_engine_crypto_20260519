# Crypto Search Engine V1.4 Binance Target Exact Replay

- Producer source: `fe82d94e5530d13e933c0f3db5d2b4869ad34521`.
- Replay: exact existing V1.4 Stage-B `1,200` CandidateSpec objects in original completion order; new candidates `0`.
- Target: Binance USD-M aggTrades hourly `open_price`, `log(open[t+2+h] / open[t+2])`, horizons `1h/4h`.
- Target identity: `27F780D458CBA50D6C82393F7DFDA396AC3994724645D112C4F8EF0ACDA865F0`.
- Evaluator/mapping/cost: existing pair evaluator, existing mappings, unchanged `5 bps` full-L1 cost.
- Old/new gross-positive final increments: `666/661`.
- New net-positive / gross-HAC-LCB-positive / matched-positive: `32/86/0`.
- Old/new mean pair reward: `-5.235040` / `-5.342312`.
- Joint gross-persistent candidates: `69`; horizons `[1, 4]`; semantic groups `5`.
- Gross persistence gate: `PASS_GROSS_PERSISTS_DIAGNOSTIC`.
- Decision: `TURNOVER_REPAIR_THEN_BOUNDED_ADAPTIVE_SEARCH_IS_INFORMATION_BEARING`.

## Evidence boundary

- Complete A/B/AB/ABC and incremental sleeve metrics plus monthly waterfalls are persisted.
- This is spent-development exact replay, not OOS, promotion, challenge, recent, May-stress, forward, or fresh Alpha evidence.
- No CEM, Evolution, operator expansion, turnover optimization, or rescue rerun was started.

## Bias audit

- Decision: `HOLD`.
- Target venue now matches the Binance USD-M order-flow source; missing target prices remain missing.
- Candidate selection, order, mapping, horizon, eligibility and cost are frozen; only target_return is overridden.
- Gross HAC LCB is diagnostic and does not replace strict pair_reward or grant research qualification.
