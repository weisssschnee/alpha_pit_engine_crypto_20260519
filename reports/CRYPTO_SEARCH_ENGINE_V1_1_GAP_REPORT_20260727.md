# Search Engine V1.1 Source Gap Report

## Already implemented and retained

- Evolution V2 already keeps one reward champion per behavior family in its bounded population.
- Mutation already changes one to three effective generation genes and verifies receipts and expression hashes.
- Crossover already uses one typed-role-compatible homologous point.
- Compiler, matched control, evaluator, Behavior Archive, deterministic replay, and atomic checkpoint restore remain shared authorities.

## Search-capability gaps

1. CEM checkpoint elites can contain multiple expressions from the same behavior family.
2. CEM elite updates have no mechanism/skeleton-variant frontier, so high-reward local concentration can suppress reachable variants.
3. Evolution uses frozen operation probabilities even when an operation repeatedly fails to produce a new policy-local behavior family.
4. Compatible crossover does not prefer a different skeleton variant when one is available.
5. No equal-count V1.1 profile/checker exists for a fresh-state, system-only comparison.

## Minimal V1.1 delta

- Admit one pair-reward champion per behavior family to CEM elites and seed the elite set with the best observed mechanisms and skeleton variants before global reward fill.
- Keep Evolution parent tournaments reward-first, retain one population champion per family, bound skeleton occupancy, prefer compatible cross-skeleton crossover, and update mutation/crossover allocation from checkpoint-local family productivity under a frozen probability floor.
- Add one 3,000-candidate profile: typed random, behavior-niched CEM V2.1, and behavior-niched Evolution V2.1 at 1,000 equal-count evaluations each.
- Reuse the exact V1 aggTrades cache and every existing compiler/evaluator/checkpoint authority.

This is system-search evidence only. It does not unfreeze Alpha research, OOS,
challenge, recent, May-stress, forward, promotion, latent priority, relational
training, or future-Arena qualification.
