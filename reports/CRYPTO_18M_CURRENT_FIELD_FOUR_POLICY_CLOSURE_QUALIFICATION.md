# Crypto 18M Current-Field Four-Policy Closure Qualification

## Result

The immutable producer decision remains:

`CRYPTO_18M_COMPOSITIONAL_SEARCH_LOCALIZED_MECHANISMS_ONLY`

Independent closure qualification adds two future policy-engine decisions:

- `cem_diversity_v2`: `ELIGIBLE_FOR_DISTRIBUTION_SEARCH_UPGRADE`
- `evolutionary`: `ELIGIBLE_FOR_TYPED_MUTATION_UPGRADE`

These are matched search-productivity results. They do not establish alpha,
positive absolute reward, economic increment, OOS validity, or promotion
authority.

## Identity and budget

- experiment: `CRYPTO_18M_COMPOSITIONAL_CURRENT_FIELD_CONTINUATION_V1`
- producer source: `2350405595446b1c8615537666857ce5342159e3`
- base closure: `a115913ae333696482059b497472864871cebc9f`
- runtime bundle: `13A521BE23B193EA3BFD9B4B319E69280BD9932A1B8A394EB4E3A73AD2D577EB`
- compiler bundle: `E9A438114E8619E39B5535251F0B0A91E3905B61259E3A0ABB7745E94A5A6842`
- raw-cache bundle: `D120C0444B2A5828CBE0C7B538DEF81A1D2E50689C941F4B1A96D2AE60D93FED`
- raw-cache identity: `CBD66860C54314A8376A5EA126E4FE5A9760FB766D250AD1F966DC1007EE99F0`
- Core Pack contract: `35E54F79576A6D7A1D94AE697E8066CB9FB49CF9A97979259F39490E3281914E`
- view: Broad `38+1`; 39 fields, 11 families; Core3 excluded
- environment: PC2, Python 3.11.9, NumPy 2.1.3, pandas 2.2.3,
  PyArrow 19.0.1, SciPy 1.17.1, psutil 7.0.0, eight workers
- elapsed: 5h 48m 42s

Frozen work completed exactly:

- 500,000 legal structural proposals; 251,892 exact-unique
- 50,000 numeric audits; 41,399 numeric-unique and 41,625 behavior-unique
- 64/64 preflight pairs
- 16 policy/seed lanes, 512 adaptive pairs per lane
- 4,096 Stage-A plus 4,096 pre-frozen Stage-B pairs
- 8,192 adaptive and 8,192 later report-only pairs
- adaptive calls: 16,384 standalone and 8,192 incremental-sleeve
- report-only calls: 16,384 standalone and 8,192 incremental-sleeve
- 39/39 fields exposed somewhere in adaptive proposals
- zero report-only feedback writes and zero sealed reads
- post-run raw-cache bundle unchanged

## Independent policy recomputation

The closure recomputed each lane directly from
`CRYPTO_STRICT_PAIR_RESULTS.parquet`. Every group had 512 rows and proposal
steps 0..511; all statuses were PASS, all failure reasons were null, and the
maximum difference from persisted lane summaries and margins was `0.0`.

| Policy | Seed | Mean margin vs matched random | Top-52 margin | Joint pass |
|---|---:|---:|---:|---|
| CEM-lite | 20260716 | 0.111952329 | 0.971844316 | yes |
| CEM-lite | 20260717 | 0.224092549 | 0.466189821 | yes |
| CEM-lite | 20260718 | 0.013649910 | 0.198466988 | yes |
| CEM-lite | 20260719 | 0.182486696 | 0.354203292 | yes |
| Evolutionary-lite | 20260716 | 0.466989998 | 1.942268775 | yes |
| Evolutionary-lite | 20260717 | 0.508665708 | 1.872742226 | yes |
| Evolutionary-lite | 20260718 | 0.470825422 | 1.730685793 | yes |
| Evolutionary-lite | 20260719 | -0.089752942 | -1.001669391 | no |

The frozen gate requires both margins to be positive in at least two seeds.
CEM-lite passed 4/4 and Evolutionary-lite passed 3/4. Evolutionary
parent-child uplift is explicitly
`UNMATCHED_DIAGNOSTIC_NOT_DECISION_AUTHORITY` and was not used.

Mean pair rewards remained negative. Evolutionary-lite also concentrated on
eight skeletons and two to three mechanism families; its 20260719 lane exposed
only 19 fields. A real typed-mutation implementation therefore needs matched
coverage controls and may not narrow the research surface around the current
elite family.

## Economic attribution

- adaptive matched-positive clusters: 3
- report-only matched-positive clusters: 15
- robust-positive candidates: 4
- cross-seed reproduced clusters: 4
- primary bottleneck: `CHALLENGE_INSTABILITY`

The report-only block ran after all adaptive work and never fed policy state.
It is spent development evidence, not formal validation, recent, May stress,
forward, challenge authority, or OOS proof.

## Reproducer qualification

- PC2 task `job_20260719_034126_54b922` exited 0.
- Producer-side built-in check returned PASS with no errors and exact bundle.
- The same check passed locally with the producer's config bytes.
- Config line content is identical across machines: PC2 CRLF SHA256 is
  `BE7A3B66DA95F5EF1E97F6FD840730B06AA5888B98CBC669040D7D14AD2FBAE5`;
  committed LF SHA256 is
  `A0DD2AD657EEDDF69DAD7B9E054E63A736EB35EC9758F885BA2F274CCA3DD70E`;
  newline normalization maps the first exactly to the second.
- The 21 producer artifacts, including its two original generated reports, are
  immutable members of `CRYPTO_ARTIFACT_MANIFEST.json`. This qualification
  report is deliberately outside that bundle.

Reproducer:

```text
python scripts/crypto_18m_compositional_broad_search.py check --config config/crypto_18m_current_field_four_policy_continuation_v1.json
```

## Next decision

Implement only two expiring upgrades inside the existing policy interface: a
real frozen CEM distribution update and receipt-bearing typed mutation. Keep
same-seed typed random and UCT controls, then run one compile/replay check and
one small fixed development canary. Do not rerun this continuation or open a
new large budget, sealed role, candidate promotion, or cross-sprint memory.
