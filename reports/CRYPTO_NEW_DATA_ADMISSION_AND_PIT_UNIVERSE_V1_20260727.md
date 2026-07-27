# Crypto new-data admission and PIT universe V1

- Decision: `HOLD_PIT_UNIVERSE_AND_SEARCH_CACHE`
- PIT ledger status: `PROVISIONAL_FAIL_CLOSED`
- Search started: `NO`
- Contract SHA256:
  `EB70D29CC4D19264C0DC00CBCD0DE2241E00B923E4402BD948E8A2BE60467D68`
- Runtime: `runtime/crypto_new_data_admission_v1_20260727`
- Derived root:
  `G:/AlphaFactory_CryptoData/derived/crypto_new_data_admission_v1_20260727`

## Independent delivery acceptance

Both aggTrades TARs independently matched their sidecars. The full logical scan
read every Parquet timestamp row, not just archive headers.

| Package | Parquets | Rows checked | SHA256 | Result |
|---|---:|---:|---|---|
| Top100 compact 1m | 2,542 | 110,104,239 | `59c9dc82...01e1` | PASS |
| ranks101-200 compact 1m | 2,167 | 93,230,404 | `87eae5c0...8f5a` | PASS |

Across 203,334,643 rows there were zero schema variants beyond the one expected
schema, zero row/manifest mismatches, zero duplicate or unsorted files, zero
month-bound violations, and zero failures of
`feature_available_time = timestamp + 1m` or
`execution_time_min = timestamp + 2m`.

OI/mark schema-fixed v3 independently passed 1,155 feature Parquets, 1,155
object-manifest Parquets, and 1,155 done markers. Its 2,587,012 feature rows and
5,173,729 manifest rows had zero schema, marker-hash, marker-row, or zero-column
failures. Archive SHA256 `a7eeacf2...04bbb` matched. These are content PASS
results, not PIT-universe admission.

## Frozen PIT construction

The official-source build requested 20,863 symbol-month objects from 2023-12
through 2026-06. It verified 13,544 ZIP/checksum pairs, recorded 7,319 expected
not-found symbol-months, downloaded 23,237,115 bytes, and had zero source
failures.

Membership uses:

- trailing 30 completed UTC days of quote volume;
- at least seven observed positive-volume days;
- one completed-day information lag;
- previous-day active evidence;
- deterministic `instrument_id` tie-break;
- no reward, search, or outcome feedback.

The source exposed 405,230 daily rows. Exactly 40,226 zero-volume rows were
treated as inactive before lifecycle and rank construction, leaving 365,004
active daily rows. This prevents delisted zero-filled intervals from masquerading
as tradable history.

The provisional ledger contains 893 dates, 200 rows per date, 178,600 rows,
634 raw symbols, and 639 lifecycle identities. `LITUSDT` is explicitly split
between Litentry and Lighter Protocol. Five additional long-gap symbols are
conservatively split but still require semantic review:
`AIAUSDT`, `CTKUSDT`, `CVXUSDT`, `MAVIAUSDT`, and `SLPUSDT`.

## Why the PIT ledger remains provisional

`BDXNUSDT` is present in the official archive from 2025-06 through 2026-03 but
is absent from the frozen current exchange-info type map. Its ten source ZIPs
all passed checksum. If classified as crypto, it crosses the provisional
Top200 cutoff on 76 days from 2025-06-15 through 2026-02-13; its maximum
trailing-volume/cutoff ratio is 4.2646.

The system therefore does not guess its type, does not silently include it, and
does not call the provisional 178,600-row ledger research-qualified.

## Actual delivered coverage

Coverage below uses actual delivered symbol-date support. It does not project a
current symbol list backward through history.

| Surface | Mean | Minimum | Maximum | Days with gaps |
|---|---:|---:|---:|---:|
| Current 498 hourly panel | 88.88% | 77.00% | 99.50% | 893 / 893 |
| Delivered aggTrades 1m | 61.46% | 48.00% | 70.00% | 893 / 893 |
| OI/mark schema-fixed ranks51-200 | 14.73% | 0.00% | 44.00% | 893 / 893 |

Top50 OI/mark remains raw-only and has no materialized, authorized consumer, so
it is not counted as usable schema-2 feature coverage. The exact missing
coordinates and compact backfill requirements are persisted in:

- `surface_missing_members.parquet`: 240,989 symbol-date-surface rows;
- `surface_backfill_requirements.parquet`: 1,198 symbol-surface requirements;
- `surface_cohort_overlap.parquet`: separate retrospective cohort-overlap
  diagnostic.

## Schema-2 result

The hourly cache calls the existing
`broad_search.panel18m.rebuild_panel_context_fields` after the PIT/current-498
join. It covers 21,432 hours and 3,809,712 observed coordinates. Rebuilt active
support ranges from 154 to 199 assets. No hour has all 200 historical PIT
members, so complete-support rate is 0% and search reuse is false.

Cache identity:
`2A03AF048B4907276182A6349060AD3703AC390F3BB50E08AC68F732AD90F91A`.
All six NPY arrays have recorded SHA256 values in `cache_identity.json`.

## Conclusion

The old lack of search results is not evidence that the old market data had no
Alpha. The post-audit defects were real: partition-local panel context,
overlapping-horizon uncertainty, incomplete matched waterfalls, retrospective
fixed cohorts, and incomplete historical feature support. The new delivery adds
substantial valid data, but it does not repair those defects merely by existing
on disk.

The next admissible data action is exact and bounded: resolve historical
`BDXNUSDT` type authority, review the five inferred lifecycle splits,
materialize a safe Top50 OI/mark consumer, and fill the persisted 1,198
symbol-surface requirements. Then rebuild the full Broad39 post-join schema-2
cache. A fresh-state search still requires separate authorization.

No Arena, OOS, challenge, recent/May-stress/forward evaluation, promotion,
latent training, relational training, or candidate evaluation was run.
