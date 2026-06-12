# CRYPTO A7DATA Recent Patch And CE Overlay Acceptance 20260613

## Decision

`PASS_A7DATA_RECENT_PATCH_CONTROLLED_EXPERIMENT_READY_WITH_SPLICE_AND_FIELD_GATES`

The Binance 498 recent patch and OKX x Binance CE overlay are accepted for controlled experiment use. They are not accepted for final proof until source checksum/trace audit is complete. Direct naive append into the 2024-2026 main panel is blocked because the patch overlaps the existing panel at the boundary hour.

## Inputs

- Binance patch: `G:\AlphaFactory_CryptoData\gold\features\binance_universe498_recent_patch_1h_v1_20260612`
- Binance report: `G:\AlphaFactory_CryptoData\reports\binance_universe498_recent_patch_1h_v1_20260612.json`
- CE overlay: `G:\AlphaFactory_CryptoData\gold\features\okx_ce_recent30d_binance_v2_plus_recent_patch_overlap_v1_20260612`
- CE report: `G:\AlphaFactory_CryptoData\reports\okx_ce_recent30d_binance_v2_plus_recent_patch_overlap_v1_20260612.json`
- Main 1h panel checked for continuity: `G:\AlphaFactory_CryptoData\gold\features\binance_universe498_replay_1h_v2_20260527`

## Binance Recent Patch Checks

- files: `498`
- rows: `203184`
- symbols: `498`
- columns: `65`
- time range: `2026-05-26 00:00:00` to `2026-06-11 23:00:00`
- rows per symbol: min `408`, median `408`, max `408`
- duplicate `(symbol, timestamp)`: `0`
- inf cells: `0`
- main panel range: `2024-01-01 00:00:00` to `2026-05-26 00:00:00`
- patch rows overlapping main panel: `498`, exactly one hour per symbol at `2026-05-26 00:00:00`

## Binance Coverage Notes

- trade/mark/index/funding coverage is suitable for controlled experiments.
- `open_interest_last` and `open_interest_value_last` coverage: about `0.999724`.
- 1h and 4h OI-change coverage is healthy after warmup; 24h change and 168h zscore have expected warmup missingness.
- Download manifest has `3` `missing_404` rows, all `premiumIndexKlines` for `SKRUSDT`, `SPACEUSDT`, and `ELSAUSDT` on `2026-06-04`.
- Those 404s create `24` missing `premium_close` rows for each affected symbol, while `mark_close`, `index_close`, `mark_index_basis_bps`, and `funding_rate_bps` remain present.

## CE Overlay Checks

- files: `191`
- rows: `135338`
- symbols: `191`
- columns: `59`
- time range: `2026-05-13 10:00:00` to `2026-06-11 23:00:00`
- rows per symbol: min `708`, median `709`, max `710`
- duplicate `(symbol, timestamp)`: `0`
- inf cells: `0`
- CE symbols subset of Binance patch symbols: `true`

## CE Coverage Notes

- Pre-patch overlap period, `2026-05-13 10:00:00` to `2026-05-25 23:00:00`:
  - rows: `57410`
  - Binance `funding_rate` coverage: `0.0`
  - CE funding spread coverage: `0.0`
  - CE mark/index/OI/taker spread coverage is near-complete.
- Patch period, `2026-05-26 00:00:00` to `2026-06-11 23:00:00`:
  - rows: `77928`
  - Binance `funding_rate` coverage: about `0.998447`
  - CE funding spread coverage: about `0.198388`, driven by OKX funding event sparsity.
  - CE mark/index/OI/taker spread coverage remains near-complete.

## Field Contract And Age

- Both delivered field contracts exist and parse.
- The main panel, recent patch, and CE overlay do not currently carry listing-age fields.
- This is not a schema regression, but merged search panels should add a unified observed-first-seen age/control layer before using age-sensitive candidates.

## Required Use Gates

1. Splice gate: when joining the patch to the main panel, drop or replace the overlapping `2026-05-26 00:00:00` patch/main boundary bar per symbol. Direct append is forbidden.
2. Premium gate: formulas using `premium_close` or `premium_bps` must see symbol/date coverage, because three symbols have a one-day premiumIndexKlines gap.
3. Funding gate: CE funding spread must be treated as sparse event coverage, especially before `2026-05-26`.
4. Proof gate: final proof requires Binance Vision official CHECKSUM audit and REST source trace audit.
5. Age gate: listing-age/control-like fields must be added by the merged panel builder, not assumed present in these delivered roots.

## Authorization

Allowed:

- controlled experiment
- recent-regime stress attribution
- CE overlay diagnostics
- patch-aware candidate validation

Not allowed:

- naive append into main panel
- alpha proof
- shadow, paper, or live use
- search runs that ignore splice/premium/funding/age gates
