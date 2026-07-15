# ADR 0007: 18M pair-native compositional development search

- Status: Accepted for experimental development execution
- Date: 2026-07-16
- Base data authority: `a115913ae333696482059b497472864871cebc9f`

## Context

The previous broad-search closure proved that the active one-field grammar was
not an adequate test of compositional mechanisms.  Its experimental typed DAG
did not reach the real 18-month runtime, and its ablation helper removed raw
inputs instead of preserving pair support.  The newly qualified train adapter
now exposes 2023-07-01 through 2024-12-31 while keeping all 2025+, formal
challenge, validation, recent, stress, and forward roles sealed.

## Decision

Add one bounded experimental runner with the following authorities:

1. `alphafactory_crypto.train_surface` remains the only 18-month data ingress.
2. Search eligibility is computed at each hour from observations, input
   availability, and completed history; future survival and future coverage are
   forbidden.
3. Physical fields enter search only through a persisted admission and
   equivalence audit.  Physical presence alone is not authorization.
4. The typed DAG is limited to four raw inputs, depth four, three rolling
   windows, one cross-asset transform, and one state/regime operation.
5. A matched control retains the primary raw-input support through the
   control-only `SupportMatchedPayload` operator.
6. Policy feedback is the strict result of a separately costed incremental
   sleeve, `primary_weight - control_weight`.  Standalone scalar differences
   are diagnostic only.
7. July 2023 through June 2024 is the only adaptive block.  July through
   December 2024 is a development report-only block evaluated after proposal
   completion and is not the sealed formal challenge surface.
8. Independent policy/seed lanes may execute in parallel against a disposable
   raw-input memmap cache.  Derived expressions stay lazy and candidate-local.

## Consequences

- A qualified Stage A contains exactly 4,096 strict pairs; Stage B may add at
  most 4,096 under preregistered evidence triggers.
- The search can end in a layer-specific structural or resource bottleneck
  without being mislabeled as a market-wide no-alpha result.
- No result from this branch can move an accepted tag, promote a candidate,
  authorize formal performance search, or support an OOS/live-trading claim.
- RAW and CURRENT Graph projections are refreshed only after runtime evidence
  and decision artifacts exist.
