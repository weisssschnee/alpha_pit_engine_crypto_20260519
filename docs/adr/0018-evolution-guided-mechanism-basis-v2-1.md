# ADR 0018: Evolution-Guided Mechanism Basis V2.1

- Status: Accepted
- Date: 2026-08-01
- Amends: ADR 0017 with one new fresh-state development campaign

## Context

Search Engine V2 completed 12,000 strict train candidates and demonstrated a
material train-only ordering gradient in mechanism Evolution, but its final
validation aggregation was blocked. The blocked campaign is consumed and will
not be rescued. Its declarative catalog and aggregate mechanism outcomes may be
used as reviewed design knowledge; candidate rewards, populations,
distributions, archives, RNG, and policy state may not cross the campaign
boundary.

The V2 catalog already contains Residual, NormalizedDifference, SafeDiv,
SafeMul, and RatioInteraction. Re-declaring those operators would not expand
the search system. The missing mechanism basis is frozen polarity-aware gates,
confirmation/disagreement, non-sign-flipping magnitude modulation, and regime
routing through the existing ConditionGate and StateModulation AST nodes.

## Decision

1. Authorize exactly one fresh-state, development-only 10,000-strict-candidate
   V2.1 campaign on the unchanged 115-field aligned OI/mark x aggTrades carrier,
   receipt-bound Binance USD-M target, joint primary-plus-matched Sortino
   reward, mappings, and conditional 5 bps cost assumption.
2. Reuse the existing Expression AST, TypedExpressionRegistry, CandidateSpec,
   compiler, A/B/AB/ABC controls, evaluator, behavior archive, and atomic
   checkpoint implementation. No second AST, compiler, evaluator, database,
   materializer, or scheduler is created.
3. Preserve the 184-mechanism V2 catalog as the old-grammar control. Compile a
   reviewed V2.1 catalog containing positive/negative gates,
   confirmation/disagreement, absolute/positive/negative magnitude modulation,
   and sign routing. Thresholds and modes are frozen before candidate one.
4. Allocate five exact 2,000-candidate checkpoints: 2,000 old-grammar random,
   4,000 expanded-basis random, and 4,000 fresh expanded-basis Evolution. CEM
   receives zero budget. All arms use the same four pre-registered V2.1 seeds,
   disjoint from V1-V6 and mechanism V2.
5. Import no V2 candidate, individual reward, population, distribution,
   archive, transition memory, RNG, or policy state. A committed aggregate-only
   knowledge file may document mechanism/template/operator/role/window/
   normalizer/horizon outcomes for catalog design and lifecycle. It is not a
   sampling-probability prior.
6. After 10,000 train candidates, run terminal validation only if the frozen
   equal-count train gate passes. The gate requires sufficient expanded-random
   positive search-reward density, Evolution improvement in mean, top-decile,
   and positive rate, at least 90% behavior-family yield, and at most 10%
   behavior duplicates. Failure stops without validation; it does not trigger
   tuning, reseeding, rescue, or more budget.
7. If the train gate passes, use the repaired heterogeneous-control validation
   aggregation. Validation generates no candidates, writes no optimizer/archive
   state, and reads no holdout.
8. The run is development-only. It cannot establish Alpha, OOS, challenge,
   recent, May-stress, forward, promotion, latent, relational, or liquidation
   authority and cannot start another Arena.

## Consequences

- Mechanism expansion is measured against an old-grammar control without
  repeating the V2 fixed-Skeleton baseline or allocating more budget to CEM.
- The campaign can stop after the train gate without spending validation when
  the new basis or Evolution is not learnable.
- Any retained cross-campaign knowledge remains declarative and aggregate; all
  adaptive state remains campaign-local and exactly checkpointed.
- A terminal result updates only the existing CURRENT Search Engine capability
  node during final closure.
