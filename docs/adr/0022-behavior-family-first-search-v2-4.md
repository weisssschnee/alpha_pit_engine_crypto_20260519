# ADR 0022: Behavior-family-first Search V2.4

- Status: Accepted
- Date: 2026-08-03
- Authority: current user instruction

## Context

V2.3 showed positive frozen-cohort policy direction, but its train-top cohort
weighted expressions rather than independent behavior families. The audit
reduced 256 Evolution train-top expressions to 161 behavior families and found
effective primary-path rank of only 7.306. The OOS artifact also retained only
net, matched-increment, and control paths, preventing an independent gross,
cost, turnover, position, asset-contribution, and venue audit.

The existing pair evaluator already computes mapped weights, gross, cost,
turnover, net, matched sleeves, and asset/time coordinates. The existing
Evolution population already replaces same-family members with the deterministic
train-reward champion. A new AST, compiler, evaluator, scheduler, database, or
search platform is therefore neither necessary nor allowed.

## Decision

V2.4 uses `arm x seed x horizon x behavior_family_id` as the selection key.
Each family receives one vote. Its sole representative is the candidate with
the highest train `search_reward`; completion ordinal and candidate id are the
deterministic tie-breaks. Validation or OOS outcomes never enter selection, and
duplicate expressions cannot backfill a family.

`pair18m.evaluate_pair` remains the sole economic evaluator. It gains an
opt-in audit projection for validation or holdout only. The projection retains
every sleeve's gross, cost, turnover, net and objective mask, plus sparse
asset/time weights and gross contributions with the execution venue. The V2.4
adapter converts those paths to daily sleeve and sparse position artifacts; it
also preserves an exact hourly sleeve path with the objective mask and 5/10 bps
cost projections. A single adapter must atomically write the family selection,
selection receipt, hourly/daily sleeves, sparse positions, and hash manifest.
It does not run a market evaluator or replace candidate economics.

A future fresh-data gate must start at or after the prior holdout end
(`2026-07-01T00:00:00Z`) or use an independently admitted new asset surface.
The family selection is frozen before any read. Candidate generation,
adaptation, policy/archive writes, tuning, and threshold changes are forbidden
during the gate. Absolute zero, typed random, and frozen 5/10 bps cost
sensitivity are mandatory.

## Consequences

- Expression duplication can no longer manufacture policy weight.
- Seed and horizon heterogeneity remain visible rather than being pooled during
  champion selection.
- Future evidence can distinguish gross signal, trading cost, turnover,
  concentration, venue, and asset contribution without a second evaluator.
- This accepted architecture decision does not authorize a market run or read,
  establish Alpha, promote Evolution, or make any search policy formal.
- The existing CURRENT search capability node remains the sole Graph node for
  this experimental capability.
