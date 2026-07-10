# CRYPTO A7EFF2 Semantic Identity and SafeDiv Integration

Generated: 2026-07-10

## Decision

`PASS_A7EFF2_SEMANTIC_IDENTITY_SAFEDIV_INTEGRATED`

The active crypto source-lag/reward flow now canonicalizes deterministic DSL identities, evaluates exact portfolio-signal identities once, restores formula aliases before final gates, and routes unstable `SafeDiv` candidates to numeric review. The frozen reward contract and all previously accepted focused-pack rows were preserved.

This is an engineering/search-quality pass. It is not alpha proof and does not authorize shadow, paper, live, or deployment.

## Frozen Regression Input

```text
queue rows: 53
queue SHA256: 4B95E3CFD18496058A050AAF254496605DE9A287755B575C2832BEF87AF08AB3
canonical sources: 8
PC2 task: job_20260710_235000_1faab2
PC2 run root:
  D:\HermesWorker\runtime\crypto_line\a7eff2_semantic_identity_safediv_20260710_v2
local compact evidence:
  G:\Chengbo\runtime\a7eff2_semantic_identity_safediv_20260710_v2_results
compact evidence SHA256:
  FBEC60802F5381FD5505BC455269ADA80CC9ED8E5A47067E8A1FD73D3C387801
final PC2 code sync SHA256:
  86506431943F11E6D66E25F0BF071202281DED1238A2025D0D9FF137E9C3C681
```

After the regression, the final semantic compiler, identity, reward, and Source6 scripts were synchronized to the PC2 repo and passed remote `py_compile`. PC2 then regenerated the final Source6 summary in place with `eval_errors=0`, decision `PASS_A7SOURCE6_INCREMENTAL_EVIDENCE_FOUND`, and exactly one Source6-eligible identity representative. The pulled final feedback SHA256 is `75BA01A5F6270F131B47E28C3DBE4AB7DD9842F841E8CE2F29DCC4C4C0B2F5CA`.

## Git Release Evidence

The compact, reviewable Git evidence is grouped under `runtime/a7eff2_git_release_20260711/`:

```text
a7eff2_active_field_registry.csv
a7eff2_train_validation_oos_split_log.csv
a7eff2_accepted_train_validation_oos_log.csv
a7eff2_release_manifest.json
```

The actual cache contains `96` assets, `10` numeric fields, and `11,545` selected hourly timestamps. The evaluated windows are full-year 2024 train, the final 720 hours of each validation/test/recent OOS contract, and 601 May 2026 stress hours. The available 2023H2 backfill was not part of this replay panel or cache and is explicitly recorded as `pre2024_backfill_used=false`.

The release manifest also points to the full 81-row field ontology, field-enforcement ledger, derived-field backfill contract, A7INPUT0 approval registry, value-domain rules, split implementation, raw graph, and curated architecture. It contains hashes and paths, but no raw market data or full numeric cache.

Registry reconciliation found that `6 / 10` active cache fields do not have a row in the older 36-field A7INPUT0 approval package. The final incremental formula uses two of them: `open_interest_value_last` (covered by ontology) and `account_position_divergence` (covered by the derived-field backfill contract). This is an approval-coverage gap, not a missing materialization contract and not evidence that the formula is invalid. Release status for positive A7MEM/CEM/UCB credit is therefore `HOLD_A7INPUT0_COVERAGE_GAP` until those two inputs receive explicit approve/cap/condition/block decisions.

## Semantic Canonicalization

```text
input rows: 53
valid rows: 50
canonical rewrites: 8
constant-only rejects: 3
eval errors: 0
```

The gate no longer destroys a valid inner mechanism merely because its wrapper is redundant. It rewrites nonconstant identities and rejects only constant collapse.

Examples:

```text
Mul(Delta(OI,240), Sign(TSRank(positive_ratio,48)))
-> Delta(OI,240)

SafeDiv(Delta(OI,240), Abs(Abs(ZScore(divergence))))
-> SafeDiv(Delta(OI,240), Abs(ZScore(divergence)))

Sign(Decay(positive_ratio,4))
-> 1  [rejected as constant-only]
```

The A7LS15 generator now resamples constant-conditioner collapses and canonicalizes nonconstant redundant wrappers before indexing/materialization.

## Signal Identity Efficiency

```text
source-lag survivors: 33
exact signal representatives sent to reward: 18
exact alias evaluations avoided: 15
reward compute reduction after source-lag: 45.5%
high-similarity review pairs: 41
hard rejects from high similarity: 0
```

Exact identity is computed from orientation-canonicalized portfolio weights. Quantized or highly correlated sketches are review evidence only and never hard-reject a candidate.

The aggregate restores all aliases for source-policy and validation decisions. It emits representative-only reward feedback for A7SOURCE6 triage, and A7SOURCE6 emits one incremental representative pending the release-level A7INPUT0 coverage hold:

```text
accepted alias rows: 16
reward identity-representative feedback rows: 6
final incremental identity feedback rows: 1
```

## Reward Regression

```text
old reward rows: 132
new reward rows after alias restoration: 132
old accepted rows: 16
new accepted rows: 16
accepted set match: exact
eval errors: 0
```

For all 132 common blueprint/horizon rows, train, validation, test, recent, stress, floor, and RankIC metrics match exactly. `overall_reward` differs only at floating-point noise (`<= 3.57e-12`). No reward coefficient, split, cost, source-lag threshold, or gate was changed.

## SafeDiv Review

The previously accepted nested-`Abs` formula was retained in canonical form:

```text
SafeDiv(
  Delta(open_interest_value_mean,240),
  Abs(ZScore(Mean(top_global_account_divergence,240)))
)
```

Observed diagnostics:

```text
source-lag gate: PASS
denominator q01 / median: 0.020154
near-zero denominator share: 0.000535
local rank stability after denominator floor: 1.0
signal abs p99 / median: 462.110403
top 1% absolute signal mass share: 0.743924
```

It remains accepted by the frozen standalone reward, but A7SOURCE6 now assigns `HOLD_PORTFOLIO_MARGINAL_REVIEW`. This preserves a potentially real mechanism without allowing extreme numerical leverage to masquerade as clean incremental information.

## Information Decisions

```text
incremental interaction: 1
OOS-equivalent / non-unique: 5
canonical repass failure: 1
portfolio-marginal SafeDiv review: 1
```

The surviving incremental formula remains:

```text
Mean(
  Mul(
    Delta(open_interest_value_last,120),
    Abs(ZScore(Mean(account_position_divergence,3)))
  ),
  4
)
```

Its focused-pack metrics are:

```text
train Sortino: 2.119919
validation Sortino: 2.533467
test Sortino: 9.022089
recent Sortino: 10.870869
minimum OOS floor Sortino: 0.623839
stress floor Sortino: 1.643427
```

## Active Contract

```text
field value-domain registry
-> semantic canonicalization / constant-only rejection
-> source-lag survivor gate
-> exact portfolio-signal identity representatives
-> shared numeric cache and strict reward
-> alias restoration and source-policy gates
-> exact-representative search-memory feedback
-> subtree / SafeDiv / portfolio-marginal triage
```

After the two final-formula inputs receive explicit A7INPUT0 decisions, the next broad search memory update must consume `a7source6_incremental_identity_feedback.csv`, not the alias-expanded accepted file and not the pre-triage reward representative file alone. Until then, the row remains positive evidence with held memory credit. High-similarity clusters should receive cluster-aware credit or marginal review, while remaining eligible for independent-information proof.
