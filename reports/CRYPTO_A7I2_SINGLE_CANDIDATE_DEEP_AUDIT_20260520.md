# Crypto A7I-2 Single Candidate Deep Audit

- generated_at: `2026-05-19T16:53:14Z`
- decision: `HOLD_A7I2_COST_LAG_MAY_FRAGILE`
- evidence_level: `single_candidate_deep_audit_not_alpha_proof`
- candidate_id: `i2_microstructure_lite_113`
- expression: `Mul(Rank(realized_vol_6),ZScore(quote_volume_mean_12))`
- horizon: `12`

## Boundary

- No new candidate generation.
- No reward/gate/threshold tuning.
- May 2026 remains a known adversarial stress set.
- Base replay uses bar-boundary execution where feature availability equals next-open execution time; promotion depends on the required 1bar lag stress.
- This does not authorize alpha proof, shadow, paper, live, or production.

## Key Metrics

- raw validation ann 10bps: `0.3570`
- raw recent ann 10bps: `0.2656`
- raw May stress ann 10bps: `-0.4979`
- residual vs FundingCore recent ann 10bps: `0.5615`
- residual vs FundingCore May ann 10bps: `0.6781`
- raw recent ann 20bps: `-0.2332`
- raw recent ann lag1 10bps: `0.2640`
- raw May ann lag1 10bps: `-1.0388`
- recent symbol LOO raw positive rate: `0.833`
- May symbol LOO raw positive rate: `0.083`

## Blockers

- `raw_may_materially_negative`
- `cost20_recent_negative`
- `lag1_may_severely_negative`
- `may_symbol_loo_weak`

## Interpretation

The candidate remains a microstructure-lite clue, not an alpha proof object. It keeps positive validation/recent raw 10bps performance and positive residual-vs-FundingCore behavior, but the 20bps recent result is negative and one-bar execution lag is severely negative on May stress. The May stress weakness is not used for ranking, but it is enough to block promotion.

## Output Files

- candidate_metrics: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_candidate_metrics.csv`
- cost_ladder: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_cost_ladder.csv`
- lag_ladder: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_lag_ladder.csv`
- symbol_loo: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_symbol_loo.csv`
- symbol_contribution: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_symbol_contribution.csv`
- month_contribution: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_month_contribution.csv`
- month_loo: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_month_loo.csv`
- top_loss_hours: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_top_loss_hours.csv`
- field_timing_audit: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_field_timing_audit.csv`
- candidate_meta: `G:\AlphaFactory_CryptoData\alphafactory_crypto\runtime\a7i2_single_candidate_deep_audit\a7i2_candidate_meta.csv`
