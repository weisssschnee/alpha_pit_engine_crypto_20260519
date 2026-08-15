# P1 Semantic Supply Expansion V1 closure

Date: 2026-08-16 Asia/Hong_Kong  
Runtime: `crypto_temporal_p1_semantic_supply_expansion_v1_20260816r1`  
Implementation: `de77d3de399dacdf41de4c0f1bca96348d3d902f`  
Pure authorization: `e2c661b128a35b1dc799fd68908a2dacd02b6cc5`

## Outcome

Final decision: `P1_G2_CONTROL_OR_MAPPING_INCOMPATIBLE`.

The bounded P1 generation-2 semantic catalog and dispatcher integration were
implemented and passed proposal-only verification, but the productive run
failed closed before its first persisted strict row. This is not a negative
economic result for P1 and not a transport or PC2 deployment failure. It is a
direct incompatibility between the new conditional candidate identity and the
unchanged development block-robust evaluator.

Every frozen P1 G2 candidate is constructed with mechanism family
`CONDITIONAL_V2_P1`. The existing block-robust ordering contract rejects every
mechanism family beginning `CONDITIONAL_` with
`BLOCK_ROBUST_ORDERING_REQUIRES_BINARY_MECHANISM`. The error was reproduced by
the authorized worker path and confirmed by an independent static/runtime
checker. Continuing would require extending or bypassing the evaluator/control
contract, which this task explicitly forbids. No such change was made.

## Catalog

- Legacy P1 G1: 180, with exact prior identities retained.
- Raw G2 combinations: 192.
- Rejected: 21; 13 condition-output/type incompatibilities and 8 existing
  maximum-four-raw-field violations.
- Deduplicated: 0.
- Accepted frozen P1 G2 semantics: 171.
- Catalog SHA256:
  `60AEE0D3AF8EEABA43B89D39BE05AD1CC75DD076963D4FC6346CC5B95904E286`.
- Condition roles: FUNDING 84, FLOW_IMBALANCE 39, OI_LEVEL 36,
  CROSS_VENUE_OI_BUNDLE 12.
- Condition primitives: Persistence 86, Transition 48,
  MultiScaleRelation 24, EventWindow 13.
- Operator/modes: ConditionGate/null 50, ConditionGate/NEGATIVE 42,
  StateModulation/ABSOLUTE_MAGNITUDE 43, StateModulation/SIGN_ROUTING 36.
- Mapping classes: SPARSE_EVENT_CARRY 92 and CROSS_SECTIONAL_RELATIVE 79.
- Matched-control schema: HIERARCHICAL_A_B_AB_ABC for all 171.

The catalog was not mutated after authorization.

## Offline verification and the missed gate

All 171 G2 objects passed deterministic identity, expression compilation,
hierarchical matched-control construction, mapping derivation, PIT field
legality, checkpoint serialization, candidate rebuild, dispatcher feature
extraction and semantic dedup checks. Old P1 G1 identity replay also passed and
P2/P3 activation was zero. Offline market-array reads and candidate evaluations
were zero.

That verification did not exercise the separate development three-block
robust-ordering admission rule. The ordinary pair evaluator supports
hierarchical conditional controls, but the block-robust add-on remains binary
only. Therefore compiler/control construction success did not imply eligibility
for the frozen productive evaluator.

## Productive-run boundary

The initial launch and one diagnostic operational relaunch each completed one
eight-future worker batch before the batch-wide incompatibility was raised.
Thus 16 authorized train-only candidate evaluations occurred, but none was
committed to a checkpoint ledger. Raw proposal-attempt count was not persisted
and is reported as unavailable rather than reconstructed.

- Persisted strict: 0.
- Completed checkpoints: 0.
- P1 G2 / P1 G1 / P4 strict: 0 / 0 / 0.
- P2/P3 strict: 0 / 0.
- Persisted matched-positive: 0.
- Candidate ledger and run-complete artifacts: absent.
- 10k diagnostic and 20k hard cap: not reached.

Because no strict ledger exists, lane densities, economic clusters, new basins,
HQ-basin deepening, concrete realizations, depth increments, P1 G2 economic
attribution, P4 health and dispatcher score-decile outcomes are not available.
Zeros here mean not evaluated to a persisted strict boundary, not economic
failure.

## Independent checker and boundaries

The PC2 independent checker returned
`CANONICAL_P1_G2_CONTROL_INCOMPATIBILITY_CHECK_PASS`, payload SHA256
`E17131003BAF4175880707AB8CF4813F2CE892C62A7A7D9F0454862AEDB72252`.
It verified HEAD equals tracking at the authorization commit, a clean worktree,
all authorization-bound execution-component identities, the unchanged G2
catalog, the observed worker exception, zero persisted strict/checkpoints and
absence of ledger/run-complete artifacts.

Validation, OOS, holdout, forward, promotion and sealed reads are all zero.
P2/P3 strict are zero. The PC2 scheduled task is disabled, no Python runner
survives, and no validation, OOS, follow-up search or promotion was started.

Canonical compact evidence:
`reports/evidence/crypto_p1_semantic_supply_expansion_v1_20260816r1/control_incompatibility_closure.json`.

## Interpretation

The task's economic question was not answered because the current evaluator
cannot admit the conditioned candidate class. This does not justify another
optimizer, representation or dispatcher repair, and it does not justify
silently weakening matched controls or renaming conditional mechanisms to
bypass the evaluator guard.

Any future attempt must first receive an explicit research decision authorizing
a genuine conditional block-robust evaluator/control extension and a new frozen
authorization. No such successor is authorized by this closure.
