# Crypto Temporal Program 30K-to-50K Successor Closure

Date: 2026-08-12 Asia/Hong_Kong
Scope: one bounded train-only `30K_TO_50K_SUCCESSOR` continuation
Research status: development evidence only; no validation, OOS, holdout, promotion, or Alpha claim

## Terminal execution result

- PC2 task: `job_20260811_233723_fbaac8`
- Producer SHA: `d8106f271f86886621fd084c542671e23b695864`
- Authorization decision: `AUTHORIZE_SECOND_REPLACEMENT_30K_TO_50K_SUCCESSOR`
- Original run authorization SHA256: `16101D62E85392A7D9037148EBAFE84F41186680C1CC5C117D6487F0A3498F9D`
- Producer status: `SUCCESSOR_DEVELOPMENT_BUDGET_COMPLETE`
- Valid source prefix: 30,000 strict
- Additional evaluations: 20,000 strict
- Mechanical terminal boundary: 50,000 cumulative strict
- Generation attempts: 32,959
- Checkpoints and decisions: four, at +5k / +10k / +15k / +20k
- Workers: ten; memory fallback was not used
- System errors: zero
- Sealed reads: zero
- Invalid historical suffix contribution: zero in candidate rows, archive rows, completed pair IDs, attempted exact IDs, and policy-local counts
- Post-stop proposal/submit/observe/archive/ledger continuation: none
- PC2 independent checker: `PASS`
- Relocated-artifact local independent checker: `PASS`

The run is mechanically valid. The 50,000 boundary is final for this authorization even though the last diagnostic decision says `CONTINUE`; `automatic_next_run_started=false` and the one-time authorization is consumed.

## Economic independence definitions

The read-only closure audit uses only the 20,000-row valid successor suffix. A *new* cluster is a `behavior_family_id` absent from the verified `completion_ordinal <= 30000` prefix.

- New behavior cluster: new unique `behavior_family_id`.
- New economic-opportunity cluster: new unique behavior family with both left and right incremental net mean above zero.
- New matched-positive cluster: new unique behavior family whose frozen matched-positive predicate is true.
- Program basin: canonical `program_id`.
- CPU denominator: summed proposal-compile plus paired-evaluation process CPU seconds.

The machine-readable audit is `reports/CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_ECONOMIC_INDEPENDENCE_20260812.json`, SHA256 `648D59CC9DCC1EDAA40A29734E08AD0B7A7E49962BBEAA6B005D76751EA0BFE4`.

## Full successor suffix

| Arm | Proposals | New behavior clusters / 1k | New economic clusters / 1k | New matched-positive clusters / 1k | New economic clusters / CPU-hour |
|---|---:|---:|---:|---:|---:|
| Random | 4,000 | 980.00 | 92.50 | 0.25 | 163.58 |
| CEM | 4,000 | 971.25 | 142.50 | 0.00 | 243.95 |
| Evolution | 12,000 | 892.08 | 502.00 | 14.00 | 880.07 |

Evolution generated 6,024 new dual-net-positive economic clusters and 168 new matched-positive clusters. Random generated 370 and one; CEM generated 570 and zero. Evolution sacrificed some raw behavior breadth but converted proposals and CPU into economically interesting independent behavior much more efficiently.

## Equal-count comparison

The four successor tranches contribute equal Random/adaptive samples of `899, 900, 899, 900`, for 3,598 proposals per compared arm.

| Comparison | Random | Adaptive |
|---|---:|---:|
| New economic clusters / 1k, Random vs CEM | 97.55 | 142.30 |
| New economic clusters / CPU-hour, Random vs CEM | 175.85 | 243.67 |
| New matched-positive clusters / 1k, Random vs CEM | 0.28 | 0.00 |
| New economic clusters / 1k, Random vs Evolution | 97.55 | 534.19 |
| New economic clusters / CPU-hour, Random vs Evolution | 175.85 | 933.05 |
| New matched-positive clusters / 1k, Random vs Evolution | 0.28 | 14.45 |

This supports a development-only policy conclusion: Evolution is materially more productive than fresh Random under the frozen target, mapping, cost, reward, data, and grammar. CEM improves the broad dual-net-positive frontier but did not produce a new matched-positive cluster in this suffix.

## Concentration stress

Evolution's equal-count advantage does not disappear after removing the dominant basins:

- Remove the largest program basin: 1,443 new economic clusters remain.
- Remove the three largest program basins: 673 remain, or 187.05 per 1,000 original proposals.
- Remove the dominant P4 program family and retain P1: 380 remain, or 105.61 per 1,000 original proposals.

The full Evolution suffix shows the same qualitative result: after removing its top three program basins, 2,119 new economic clusters remain, or 176.58 per 1,000 proposals. Family concentration is therefore material but does not explain away the productivity advantage.

## Research decision

`SEARCH_POLICY_DEVELOPMENT_EVIDENCE_PASS / ALPHA_QUALIFICATION_HOLD`

The successor answered its development question. Evolution can discover many more economically independent, matched-positive behavior clusters than Random or CEM under this frozen train contract, and the advantage survives coarse basin-removal stress. This is a search-productivity result, not proof that the clusters migrate across time.

No additional same-window search is justified automatically. The remaining bottleneck is migration and cluster-level selection: the next decision, if separately authorized, is whether to freeze a small behavior-cluster-stratified cohort before any fresh development validation. OOS, promotion, parameter tuning, new grammar, and a new Arena remain unauthorized.

## Project-control post-batch review

- Decision Delta: `YES` — the project can now decide whether to test migration of a frozen independent-cluster cohort rather than spend more train-search budget.
- Bottleneck Delta: `YES` — the primary bottleneck moved from authority/orchestration validity to temporal migration and representative selection.
- Frontier Delta: `YES` — Evolution dominates Random on new economic and matched-positive cluster productivity, including leave-largest/top-three-basin stress.
- Capability Delta: `YES` — the bounded reconstructed-state successor completed with exact prefix/suffix isolation and hard-stop enforcement.
- Information Delta: `HIGH`.
- Budget Burn: 20,000 additional strict, 32,959 generation attempts, ten workers, approximately 4.23 active wall hours.
- Verdict: `PAUSE` at the mandatory 50,000 boundary; no automatic continuation.

## Integrity anchors

- Final decision SHA256: `4C103B4AE1DD7FB73F492868FAE1BA519EA7448418049B644932EB4E83594AD8`
- Candidate ledger SHA256: `34BD491481B6CFEEB7029E07B09B8207B92220D296105A6B499CBDCBBDA88483`
- Behavior archive SHA256: `8516D87BE9175FBD0EE0419FC6E7C2ABE866281F33CAF3099F9594E47FD8833D`
- PC2 checker SHA256: `F50EC1EBFFCF108900E5C2DA0E83DFE12199F86BA486DC4849C317015F4BE559`
- Local relocated checker SHA256: `5928145F56AF9EDB9CA9E933C504D7E9C4CB25684DF34659D72CB1ED3FF3457B`
- Transferred runtime archive SHA256: `820404EE6ED7F4F16D27600D6F8CDE2B6827838BD697B0F70C1C7D5ADFA0FF4C`
- Consumed authorization file SHA256: `F448E17F290001C852E34BF70A305F9CF0C4C2CA2C4ACA11C12A04D6F1701891`
