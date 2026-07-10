# ADR 0001: Controlled Semantic, Signal Identity, and SafeDiv Gates

Status: Accepted

Date: 2026-07-10

## Context

The crypto search chain can generate expressions that are syntactically distinct but semantically degenerate or numerically equivalent. Examples include `Sign(CSRank(x))`, redundant `Abs` over non-negative subtrees, and different formulas that produce the same portfolio weights. `SafeDiv` also mixes economic structure with potentially unstable denominator leverage.

Expression hashes, AST skeletons, and whole-formula reward cannot distinguish these cases. This wastes source-lag and reward compute and can feed duplicate credit back into CEM/UCB search memory.

## Decision

1. Add a registry-backed value-domain inference layer before candidate admission.
2. Canonicalize identities that are deterministically proven by operator semantics and contracted field domains. Hard reject only when the canonical result is a constant or otherwise cannot carry a signal.
3. Compute an orientation-invariant fingerprint of portfolio weights after source-lag materialization.
4. Evaluate one representative for exact fingerprints, then restore aliases before aggregate reward and source-policy gates.
5. Treat quantized or highly correlated signals as review evidence only. They are never hard rejected by this layer.
6. Add `SafeDiv` denominator, tail, and perturbation diagnostics. These diagnostics initially flag review; they do not impose a blanket ban or alter the frozen numeric reward contract.
7. Preserve alias-specific expression, source-policy, and `SafeDiv` diagnostics when representative metrics are expanded.

## Boundaries

- This ADR does not authorize alpha proof, shadow, paper, live, or deployment.
- It does not change the train/OOS split contract, costs, reward coefficients, or source-lag thresholds.
- It does not import CN reward, memory, or search outcomes.
- A high correlation is not proof of equivalence.
- Missing or unknown field domains remain `UNKNOWN` and cannot trigger a deterministic hard reject.

## Consequences

- Search and reward spend less compute on provably duplicated information.
- Redundant wrappers do not destroy a potentially valid inner mechanism; the canonical expression retains it with explicit lineage.
- Search memory receives one numeric result per exact signal identity rather than duplicate formula credit.
- New field domains must be added to the versioned registry rules before they can support deterministic simplification.
- Exact fingerprinting is dataset/version specific and must be regenerated when panel lineage changes.
- `SafeDiv` remains available, but unstable denominator behavior becomes visible to promotion and marginal review.

## Verification

- Unit-style domain inference and identity tests.
- Generator regression on a bounded batch.
- Synthetic exact-alias expansion test.
- PC2 focused-pack regression against the frozen input checksum and prior legitimate accepted set.
- Runtime manifests must report semantic rejects, representative count, alias savings, similarity-review count, and `SafeDiv` review count.
