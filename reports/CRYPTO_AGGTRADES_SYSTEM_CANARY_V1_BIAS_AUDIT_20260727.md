# Crypto aggTrades Search-System Canary V1 — Bias Audit

- Factor: three-arm, 2,000-candidate search-system canary; no candidate promotion review
- Run/experiment_id: `20260727_aggtrades_system_canary_001`
- Data source and universe: delivered Binance aggTrades fixed retrospective cohort joined to the existing development target cache; 121 assets
- Frequency and horizon: complete 60-minute bars; typed 1h/4h target horizons
- IS window: `2024-01-01T00:00:00Z` to `2024-07-01T00:00:00Z` exclusive
- OOS window: none
- OOS sample grade: `NONE`
- Cost model: 5 bps full-L1 matched primary/control cost
- Turnover: evaluator weight-path turnover and independently recomputed incremental delta-weight turnover
- Benchmark: same-seed canonical typed random at the same first-N matched completion ordinal
- Discovery status: development diagnostic on a fixed retrospective cohort

## Findings

- Look-ahead: the consumer admits only complete hours whose `feature_available_time` is no later than the hour end; the frozen evaluator uses horizon-aware HAC with `horizon_hours - 1` dependency lags.
- Survivorship: the delivered symbol set is a fixed retrospective cohort, not a historical PIT universe. This blocks economic or promotion claims.
- Date alignment: minute inputs are aggregated without missing-value fill; panel context is recomputed after the joined panel. The run checker reports zero sealed reads.
- Label horizon: both typed horizons remain inside the existing evaluator contract; overlapping 4h uncertainty uses Newey-West/Bartlett HAC.
- Costs: full matched cost evaluation completed for all 2,000 counted candidates.
- Turnover: cost-killed and turnover-killed rates are preserved by arm and checkpoint; neither enters elite ordering.
- Multi-window stability: not tested and not authorized.
- Replay vs discovery: fresh policy, distribution, population, candidate, reward, and archive state were used, but the fixed cohort is still only a system diagnostic.

## Blocking Issues

- No OOS, challenge, recent, May-stress, forward, or independent market window.
- Fixed retrospective cohort has survivorship limitations.
- All three arms produced zero positive matched discoveries in this canary.

## Decision

`HOLD_RESEARCH`

## Required Next Action

- Preserve this run as system evidence only. Do not promote a candidate or arm, and do not start a larger or new-data Arena without separate authorization.
