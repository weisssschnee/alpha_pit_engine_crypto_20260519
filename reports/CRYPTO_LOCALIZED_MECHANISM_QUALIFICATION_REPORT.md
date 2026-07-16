# Crypto Localized Mechanism Qualification

## Decision

`INSUFFICIENT_INDEPENDENT_EVIDENCE`

The unique robust-positive candidate is not an exact identity or portfolio
duplicate of its matched control, and its fixed 18-month contribution is not
dominated by one month or one asset.  The evidence is nevertheless not
independent enough to freeze a challenger.

## Candidate and native pair

- candidate: `E35D9F1CC2D69E7E5F8985606315DBE5351FF13241D67A3135821CCF5AAAF751`
- formula: `StateModulation(RollingZScore(Raw(open_interest_last), window=336), CrossSectionalRobustZScore(Raw(history_length_hours)))`
- control: `SupportMatchedPayload(RollingZScore(Raw(open_interest_last), window=336), CrossSectionalRobustZScore(Raw(history_length_hours)))`
- adaptive incremental net / LCB: `3.53434641217e-05` / `1.30756067117e-05`
- report-only incremental net / LCB: `1.54594901929e-05` / `-9.70655516473e-06`
- mapping: `CROSS_SECTIONAL_ZERO_NET` at 5 bps full L1 cost

## Identity and mapping qualification

- exact formula equals control: `False`
- portfolio equals control on any block: `False`
- adaptive primary/control portfolio-size ratio: `0.525171`
- report-only primary/control portfolio-size ratio: `0.979749`
- artifact replay: `PASS`

The native pair changes occupancy on the adaptive block because the
cross-sectional listing-age state creates tied/zero scores.  The fixed A-G
audit therefore also uses a matched-occupancy bridge that preserves A's exact
weight multiset at every timestamp; it is diagnostic and does not change the
source mapping or candidate.

## Economic concentration

- combined fixed-portfolio net mean: `2.86030304939e-05`
- Top-1 month positive contribution share: `0.238746`
- Top-3 month positive contribution share: `0.523251`
- Top-1 asset positive contribution share: `0.067670`
- minimum leave-one-month net mean: `2.18201653699e-05`
- leave-top-3-assets net mean: `1.21204093758e-05`
- accidental concentration: `False`

## Report-only independence

`CANDIDATE_PACK_COUNTERFACTUALLY_INDEPENDENT_BUT_REPORT_ONLY_VISIBILITY_CONTRACT_FAILED`

The Stage B gate read Stage A report-only cluster/yield statistics even though
the feedback contract declared those metrics invisible to policy.  In this
frozen run the read was non-causal: adaptive cross-seed policy improvement
already made the OR gate true, so removing report-only terms leaves the same
Stage B authorization.  No report-only reward was written to lane state.

The larger limitation is statistical: the reported 18-month robust statistic
combines 12 adaptive selection months with only six report-only months.  The
candidate's independent report-only LCB is negative.

## Fixed A-G ablation

- A full candidate robust positive: `True`
- C regime-only robust positive: `True`
- E time-shuffled regime robust positive: `False`
- F lagged regime portfolio equals A on the frozen coordinates: `False`
- G matched-occupancy placebo robust positive: `False`

The results are compatible with a listing-age/maturity localization, but they
do not isolate a unique contemporaneous regime mechanism.  The 4-hour lag
remains highly portfolio-correlated with A and is still robust-positive.  The
time-shuffled state loses standalone robustness but retains a positive
incremental-vs-base mean on both development blocks.

## Cross-seed qualification

- reproduced source clusters: `2`
- independent mechanism replications: `0`

Both clusters are report-only-positive variants of the same broad
STATE_REGIME_MODULATION family.  They do not provide a distinct mechanism that
is matched-positive on both blocks and therefore cannot independently validate
the unique candidate.

## Claim boundary

- `NEW_SEARCH_REMAINS_FROZEN`
- `STRICT_OOS_REMAINS_NOT_AUTHORIZED`
- `PROMOTION_REMAINS_FORBIDDEN`
- forward, recent, validation, holdout, May stress, and formal challenge were not read
- no `ALPHA_FOUND`, `OOS_PASS`, or `PROMOTION_READY` conclusion is authorized
