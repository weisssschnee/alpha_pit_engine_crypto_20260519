# Crypto A7AR-0 CN Engine Inheritance Audit

## Decision

PASS_A7AR0_CN_ENGINE_FLOW_UNDERSTOOD_ADAPTER_REQUIRED

## Boundary

- CN repo was read-only for this audit.
- Crypto may inherit engine structure and schema ideas.
- Crypto must not inherit CN search memory payloads, candidate ledgers, cluster ids, retained flags, or reward outcomes.
- This audit does not authorize A7AL-2 formula search, alpha proof, shadow, paper, or live.

## Finding

Crypto currently has many stage scripts and contracts, but the mature CN engine is only partially present as references.
The missing execution services are material: feature algebra, search memory, ledger policy, replay ranker, selector stack, and large-search orchestration.

## P0/P1 Components Required Before Formula Search

- formula_gen_v2_sampler: partial_reference_only - no importable crypto package; current scripts use simplified generator
- typed_ast_and_macros: partial_reference_only - reference copied but no crypto field/operator adapter package
- freeform_and_ablation_sampler: partial_reference_only - reference copied but not active in crypto search
- motif_packs: partial_reference_only - CN pack copied; crypto pack is small and not equivalent
- feature_algebra: missing - no crypto equivalent found as reusable package
- variation_and_fingerprint: missing - dedup exists ad hoc in scripts, not inherited engine service
- search_memory_schema: missing - memory policy not active; no CN payload should be inherited
- ledger_policy_and_bandit: missing - A7M surrogate exists but not CN ledger policy
- replay_ranker: missing - A7M surrogate is empirical diagnostic; CN replay ranker not ported
- real_market_validation: partial_crypto_specific - crypto has fast replay scripts; no reusable CN-style validation service

## Memory Policy

- schema: inherit_from_cn=yes, inherit_payload=no; Use LocalSearchMemory keying ideas and schema shape under crypto namespace.
- expression_keys: inherit_from_cn=no, inherit_payload=no; Initialize empty set; populate only from crypto candidates.
- skeleton_keys: inherit_from_cn=no, inherit_payload=no; Initialize empty set; avoid suppressing crypto formulas due to CN stock memory.
- production_rule_key: inherit_from_cn=yes, inherit_payload=no; Adapt context fields to engine/cell/horizon/neutralization namespace.
- reward_proxy: inherit_from_cn=structure_only, inherit_payload=no; Replace IC/OOS/replay components with A7AL pre-replay and neutralized metrics.
- candidate_records: inherit_from_cn=no, inherit_payload=no; Do not import CN candidate ledgers, retained flags, cluster ids, or replay metrics.

## Adapter Sequence

- A7AR-1 formula_engine_import_smoke: Create importable crypto FormulaGenV2/typed AST adapter package. Gate: Generate 1000 crypto field-safe expressions with zero CN field references.
- A7AR-2 feature_algebra_parity_smoke: Evaluate a fixed operator set on a tiny top498 slice with +1h/+2h timing. Gate: Operator parity, NaN/inf, activity, and timing checks pass.
- A7AR-3 fresh_memory_and_dedup_smoke: Initialize crypto memory empty and test expression/skeleton/family dedup. Gate: Memory starts empty; duplicate control works only on crypto-generated formulas.
- A7AR-4 pre_replay_ranker_adapter_smoke: Build CN-style pre-replay matrix from crypto-safe columns only. Gate: Forbidden post-replay and future/stress columns excluded mechanically.
- A7AR-5 a7al1_field_family_baseline_with_engine_services: Run field-family baseline smoke using inherited dedup/ranker/selector services. Gate: A7AL-1 gates define whether A7AL-2 formula search can start.

## Blockers

- A7AL-2 formula search remains blocked until A7AR-1 through A7AR-4 pass.
- Any non-empty CN memory import is a hard failure.
- Any CN stock field in generated crypto expressions is a hard failure.

## Summary Counts

- inventory_components: 15
- p0_or_p1_required_gaps: 10
- p0_missing_or_reference_only: 6