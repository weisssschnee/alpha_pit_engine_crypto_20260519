# Crypto Search V2.3 OOS Policy Attribution Bias Audit

## Decision

`HOLD_RESEARCH`

The frozen OOS replay supports a positive **search-policy direction**. It does
not establish broad mechanism Alpha, a formally qualified optimizer, a future
Arena arm, or promotion. This audit is read-only and post-hoc: it consumes only
the committed V2.3 train ledger and frozen-OOS ledger/path artifacts, performs
no market evaluation or candidate selection, and does not read the raw carrier
or holdout again.

Machine-recomputed evidence:
[`CRYPTO_SEARCH_V2_3_OOS_POLICY_BIAS_AUDIT_20260803.json`](CRYPTO_SEARCH_V2_3_OOS_POLICY_BIAS_AUDIT_20260803.json).

## Bias Audit

- Factor: frozen V2.3 total search policy, not an individual factor
- Run/experiment_id: `CRYPTO_SEARCH_V2_3_FROZEN_OOS_20260803`
- Data source and universe: 71 OI/mark plus 44 Binance aggTrades fields; 144
  physical/ever-eligible assets, dynamic active intersection 58-143; delivered
  observed archive, not a survivorship-complete exchange universe
- Frequency and horizon: hourly signals; frozen 1h and 4h horizons
- Train window: `2025-08-29T07:00:00Z` to `2025-11-01T00:00:00Z`
- Validation window: `2025-11-01T00:00:00Z` to `2026-01-01T00:00:00Z`
- OOS window: `2026-01-01T00:00:00Z` to `2026-07-01T00:00:00Z`
- OOS sample grade: `WEAK`; 181 paired daily observations, below the 250-day
  BASIC threshold
- Cost model: frozen full-L1 5 bps inside the retained evaluator; non-formal
  venue assumption
- Turnover: applied inside evaluation but OOS turnover and gross paths were not
  persisted, so independent cost stress cannot be reconstructed
- Benchmark: original random train-top for relative policy attribution; zero
  for the separate absolute-return reading
- Discovery status: frozen policy replay; all mechanism and behavior-family
  decompositions below are post-hoc attribution

## Absolute Economics

The formal `+2.0147 bp/day` primary total-policy result is a relative effect:

| Frozen cohort | Absolute primary net | Absolute matched increment | Positive cells |
|---|---:|---:|---:|
| random stratified | -2.0026 bp/day | -3.6877 bp/day | primary 0/4; matched 0/4 |
| Evolution stratified | -0.9650 bp/day | -2.1185 bp/day | primary 2/4; matched 0/4 |
| random train-top | -0.2364 bp/day | -1.1897 bp/day | primary 2/4; matched 0/4 |
| Evolution train-top | **+1.7783 bp/day** | **+1.0846 bp/day** | primary 4/4; matched 3/4 |

The proposal distribution is therefore only less negative than random. The
positive absolute result appears after the train ranker selects Evolution's top
cohort. This supports ranking/selection value, not broad proposal-level Alpha.

## Diversity And Dependence

Evolution train-top contains:

- 256 exact expressions;
- 221 canonical expressions;
- 161 behavior families;
- 37.109% behavior duplicates;
- primary-path correlation participation-ratio effective rank `7.306`;
- matched-path effective rank `11.008`;
- 6.04% of primary candidate pairs above correlation `0.90`;
- primary top-eigenvalue share `30.84%`.

The four seed/horizon cells contain 42, 39, 53, and 27 behavior families out of
64 candidates. The second seed's 4h cell has a 57.81% behavior-duplicate rate.
The 256 expressions must not be described as 256 independent Alpha bets.

Behavior duplication is not, however, the source of the positive pooled
direction. Two deterministic post-hoc sensitivities that use no OOS selection
remain positive:

| Evolution-top weighting | Primary total-policy delta | Primary Q10 | Matched delta | Matched Q10 |
|---|---:|---:|---:|---:|
| original candidate equal-weight | +2.0147 bp/day | +1.1726 bp/day | +2.2742 bp/day | +1.7768 bp/day |
| equal behavior-family weight | +2.6502 bp/day | +1.6420 bp/day | +2.3627 bp/day | +1.6887 bp/day |
| train-reward champion per family | +2.6425 bp/day | +1.6404 bp/day | +2.3426 bp/day | +1.6599 bp/day |

These are robustness diagnostics only. They cannot retrofit a new policy or
qualification gate after the sealed read.

## Mechanism Attribution

Evolution train-top collapses to two templates, not twelve broadly successful
mechanisms:

### Flow Intensity Conviction

- 97 candidates, all from seed `359914106` only;
- 1h: primary `+6.96 bp/day`, matched `+4.14 bp/day`;
- 4h: primary `+2.96 bp/day`, matched `+1.61 bp/day`;
- primary positive in 6/6 months; matched positive in 5/6 months;
- primary-path effective rank `5.02` across 97 candidates.

This is the main positive economic contributor, but it has no second-seed
replication because the second seed selected none of this template.

### Funding Flow Crowding

- 159 candidates across all four cells;
- first seed primary: `-0.47` and `-0.49 bp/day` at 1h/4h;
- second seed primary: `+0.14` and `+0.81 bp/day` at 1h/4h;
- matched increments: `+0.53`, `-0.04`, `-0.51`, and `+0.32 bp/day`;
- primary and matched each positive in only 2/6 months;
- primary-path effective rank `4.30` across 159 candidates.

This family does not independently support a broad or stable Alpha claim. The
second seed's positive relative total-policy cells mainly reflect a weaker
random baseline while Evolution top is near zero to modestly positive.

## Bias Findings

- Look-ahead: no new defect found. The frozen carrier declares a one-hour
  observable lag, the economic receipt purges six hours at each partition tail,
  train orientation and limiting matched sleeve were frozen, and this audit
  reads no raw market data.
- Survivorship: unresolved for promotion. Dynamic eligibility and no-fill gates
  passed, but the delivered observed archive is not a historical
  survivorship-complete exchange universe.
- Date alignment: train, validation, and OOS roles are disjoint and the OOS
  replay used unchanged Binance target, mapping, horizon, orientation, and cost.
- Label horizon: 1h and 4h are explicit; seven-day block bootstrap preserves
  short dependence at the daily effect level.
- Costs: net results include the frozen 5 bps assumption, but the OOS artifact
  omits gross, turnover, and cost paths. A 10/15 bps sensitivity cannot be
  reconstructed without another market evaluation.
- Turnover and concentration: OOS asset weights, venue exposures, turnover
  paths, and asset contribution paths were not persisted. Concentration and
  execution-capacity claims remain unavailable.
- Multi-window stability: only one 181-day OOS window exists. Monthly
  attribution is descriptive and not an independent set of holdouts.
- Replay vs discovery: policy candidates and direction were frozen before OOS;
  mechanism/family analysis was performed after seeing OOS and is explicitly
  post-hoc.

## Blocking Issues

1. OOS evidence is a single 181-day window and grades `WEAK`.
2. Candidate count greatly overstates independent behavior count and effective
   path dimension.
3. The strongest template is confined to one seed.
4. Persisted OOS artifacts cannot support cost, turnover, asset, venue, or
   capacity sensitivity.
5. Universe construction remains dynamically eligible but not
   survivorship-complete.

## Authority Consequence

- Preserve `OOS_TOTAL_POLICY_DIRECTION_SUPPORTED` as conditional policy evidence.
- Preserve optimizer reward, target, execution price, validation role, and cost
  as `NON_FORMAL`.
- Record economic Alpha as `NOT_ESTABLISHED / HOLD_RESEARCH`.
- Keep every arm, archive, future Arena, promotion, second OOS read, tuning,
  reseed, rescue, and new search unauthorized.

Any future economic qualification requires a separately authorized fresh-data
contract that preregisters behavior-family de-overlap, compares absolute net
return with zero as well as random, persists gross/turnover/cost/asset-weight
paths, and supplies multi-window evidence. This audit itself authorizes no such
run.
