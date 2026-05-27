# Crypto A7AR-3 Fresh Memory And Dedup Smoke

## Decision

PASS_A7AR3_FRESH_MEMORY_DEDUP_SMOKE

## Scope

- Initializes a fresh crypto search memory namespace.
- Ingests A7AR-1 generated formulas only.
- Tests expression-key, skeleton-key, and production-key bookkeeping.
- Does not inherit CN memory payloads and does not run replay/search.

## Results

- initial_inherited_paths: 0
- initial_expression_keys: 0
- initial_skeleton_keys: 0
- input_candidates: 1000
- accepted_records: 1000
- duplicate_events: 0
- skeleton_repeat_events_soft: 991
- expression_key_count: 1000
- skeleton_key_count: 9
- production_key_count: 356

## Authorization

- A7AR-4 pre-replay ranker adapter smoke is authorized if this decision is PASS.
- A7AL-2 formula search remains not authorized.