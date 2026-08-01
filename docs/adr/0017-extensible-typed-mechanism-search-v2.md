# ADR 0017: Extensible Typed Mechanism Search V2

- Status: Accepted
- Date: 2026-08-01
- Amends: ADR 0016 for one new fresh-state development campaign

## Context

V1-V6 established a reusable crypto search chain but did not establish a
sustainable mechanism-expansion path. The existing fixed Skeleton registry
conflates mechanism coverage with a closed template list. Repeating the same
fixed-template campaigns or changing seeds cannot answer whether a wider typed
economic-mechanism grammar improves proposal productivity, behavior discovery,
or train-only reward ordering.

The repository already owns the required execution authorities: the aligned
71-field OI/mark plus 44-field aggTrades carrier, existing Expression AST,
TypedExpressionRegistry, CandidateSpec, compiler validation, A/B/AB/ABC matched
controls, Binance USD-M delayed-open target, frozen 5 bps cost assumption,
joint primary-plus-matched Sortino reward, incremental behavior archive, and
atomic checkpoint/replay path. A second AST, compiler, evaluator, database, or
AutoML layer is neither necessary nor authorized.

## Decision

1. Authorize exactly one fresh-state, development-only Search Engine V2
   campaign under `config/crypto_search_mechanism_v2_receipt.json`. The actual
   producer source is `ef688d89ca0e89654015bf5f76a6b9c26494d837`;
   the earlier `fbc396a...` production bundle remains its code-equivalent
   pre-governance implementation ancestor.
2. Compile the declarative mechanism catalog into the existing typed genome.
   The frozen catalog contains 12 economic templates and 184 legal binary or
   conditional mechanism specifications using only existing operators,
   mappings, compiler, matched controls, and evaluator.
3. Run one continuous 12,000-strict-candidate Arena:
   - checkpoint 0: 2,000 legacy fixed-Skeleton typed-random controls;
   - checkpoints 1-2: 4,000 expanded-mechanism typed-random candidates;
   - checkpoints 3-5: 3,000 mechanism CEM and 3,000 mechanism Evolution
     candidates.
4. Do not use a random-arm economic-positivity gate before adaptive search.
   CEM and Evolution are evaluated because the decision concerns search
   learnability and mechanism-space productivity. Final development validation
   occurs only after checkpoint 5 and qualifies each arm independently; the
   random control cannot veto an adaptive arm.
5. Keep adaptive state arm-local. CEM uses current-checkpoint elites and the
   frozen hierarchy. Evolution uses bounded population, typed 1-3 parameter
   group mutation, compatible mechanism mutation with deterministic remapping,
   and one-point compatible gene-bundle crossover. Every child retains receipt,
   expression-hash, compiler, matched-control, and deterministic replay proof.
6. Persist exact checkpoint state only within this campaign. Across campaigns,
   persist only declarative mechanism specifications, lineage, constructibility
   counts, aggregate outcomes, behavior yield, and lifecycle. Candidate rewards,
   populations, CEM distributions, RNG state, and policy state never become
   cross-campaign adaptive memory.
7. Reuse the existing CURRENT Search Engine node. Its target, reward, execution,
   cost, and validation bindings remain NON_FORMAL. This decision does not
   promote any component or authorize OOS, holdout reads, challenge, recent,
   May stress, forward evaluation, latent training, relational training,
   liquidation admission, or a rescue rerun.
8. Historical V1-V6 receipts remain unchanged. Consumed-run source validation
   resolves their frozen component hashes against each recorded producer Git
   blob; the current V2 authorization resolves against the current producer
   source.

## Consequences

- The mechanism grammar can expand through reviewed declarative specifications
  without forking the representation or evaluation stack.
- Search policy comparisons use equal completed counts and campaign-local state;
  market positivity is not a prerequisite for measuring learnability.
- Checkpoint 5 and the final per-arm validation are the only completion gates.
- Any terminal outcome remains development evidence conditional on the frozen
  target, window, mapping, and 5 bps cost. It cannot support an Alpha, OOS, or
  promotion claim.
- No additional campaign is implied. A budget-exhausted or validation-blocked
  outcome is retained without tuning, seed change, rescue, or state import.

## Observed outcome

The single authorization is consumed as `ENGINE_VALIDATION_BLOCKED`. Producer
`ef688d89ca0e89654015bf5f76a6b9c26494d837` retained exactly 12,000 strict,
exact-unique, matched-control-valid, full-cost train candidates from 20,386 raw
attempts. All six 2,000-candidate checkpoints restore exactly. The archive
contains 11,738 behavior families, and the compiled grammar contains 184 legal
mechanism specifications.

After checkpoint 5, the frozen validation stage evaluated candidates but failed
before equal-count arm aggregation. Binary and hierarchical mechanisms legally
emit different control schemas; the producer aggregator incorrectly required
every candidate in an arm to expose identical control names and raised
`validation control path inconsistent for arm:
extensible_mechanism_random_v2:interaction_left`. No validation checkpoint was
written, no arm is qualified, and no validation result or market-information
conclusion is inferred.

Closure source `8a526e8683874e3bdbcfd54e49adfbd0c1f290ff` repaired future
heterogeneous-control aggregation without re-evaluating this campaign. Source
`c7d4806e` also added reward-authority-aligned positive-search-reward
productivity metrics while preserving legacy pair/matched-positive diagnostics.
Neither repair changes the retained producer artifacts or rescues this run.
