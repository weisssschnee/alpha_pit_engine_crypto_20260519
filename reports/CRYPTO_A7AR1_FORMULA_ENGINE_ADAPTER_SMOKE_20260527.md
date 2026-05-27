# Crypto A7AR-1 Formula Engine Adapter Smoke

## Decision

PASS_A7AR1_FORMULA_ENGINE_ADAPTER_SMOKE

## Scope

- Importable crypto FormulaGenV2-style adapter package was created.
- The adapter inherits CN engine structure only: role/motif generation, typed metadata, and validation shape.
- It does not inherit CN search memory, candidate ledgers, clusters, retained flags, or reward payloads.
- This smoke does not run replay and does not authorize formula search beyond the adapter gate.

## Results

- generated_candidates: 1000
- validation_passed: 1000
- validation_failed: 0
- unique_expressions: 1000
- cn_memory_payload_violations: 0
- cn_reward_payload_violations: 0
- cn_stock_field_violations: 0
- memory_reset_checks_failed: 0

## Next Gate

A7AR-2 must adapt feature algebra and operator evaluation before any replay or formula search.