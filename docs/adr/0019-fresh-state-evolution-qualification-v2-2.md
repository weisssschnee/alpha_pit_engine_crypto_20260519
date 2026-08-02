# ADR 0019: Fresh-State Evolution Qualification V2.2

- Status: Accepted for one development-only run
- Date: 2026-08-02
- Authority: current user instruction

## Decision

Run one fresh-state Search Engine V2.2 campaign on PC2 using the existing
115-field aligned carrier, 786-mechanism V2.1 catalog, typed compiler, matched
evaluator, reward authority, behavior archive, and checkpoint format.

The campaign has only two arms: expanded mechanism random and a fresh
Mechanism Evolution policy. Checkpoints 0-3 allocate 1,000 strict evaluations
to each arm. Evolution must satisfy its own frozen positive floor and beat the
equal-count random control on mean reward, top-decile reward, and positive
rate while retaining behavior-family yield. The random arm is a comparator;
its train positive count is not the policy admission floor.

If the train gate passes, the existing no-feedback validation evaluates 128
candidates per arm, balanced 64/64 across 1h and 4h. Both the random control
and Evolution must pass the same absolute validation kill-line. Only then may
the same campaign-local Evolution state continue through checkpoints 4-9 at
20% random and 80% Evolution, up to 20,000 strict evaluations.

## Frozen boundaries

- Four deterministic seeds are preregistered and disjoint from prior crypto
  search campaigns.
- No prior candidate, reward, population, archive, RNG, policy, or collision
  state is imported.
- No field, carrier, materializer, mechanism, operator, AST, compiler,
  evaluator, reward, cost, scheduler, or dependency is added.
- Aggregate V2 mechanism knowledge is declarative only and is not a sampling
  prior.
- Raw attempts are capped at 100,000 and active wall time at 18 hours.
- PC2 uses 10 workers, fails closed to 8 on memory pressure, and never uses 12.
- No OOS, holdout, challenge, recent, May-stress, forward, promotion, Alpha
  claim, rescue rerun, seed change, or automatic next Arena is authorized.

## Consequences

V2.2 can distinguish a one-seed Evolution lift from a fresh, continuously
expanding mechanism search policy. A negative train or validation gate stops
the campaign with completed results. A positive gate only qualifies the
policy for continued development search; it does not promote an Alpha.
