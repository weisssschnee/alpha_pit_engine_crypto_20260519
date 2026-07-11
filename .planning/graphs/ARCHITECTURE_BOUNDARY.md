# Architecture Boundary

Generated from registry SHA256: `3F5602C1357AEBB056CA445673B81011BBE6C9383A9194543DF2CBC7CCF4613E`.

## Authority

1. Current user instruction and governance decisions.
2. `config/crypto_architecture_control_registry_v1.json` is the machine-readable architecture authority.
3. `graph.json` is the deterministic graph view generated from the registry.
4. `.planning/graphs/CURRENT_ARCHITECTURE.md` is the human-readable generated view.
5. `.planning/STATE.md`, the EVALRESET decision log, and the run manifest record phase state and history.

External graphify is currently unavailable. This does not permit manual architecture claims: `scripts/crypto_architecture_control_plane.py --check` must pass.

## Acceptance Rule

Any code, registry, route, artifact, curated document, STATE, decision log, run manifest, artifact index, or control graph mismatch blocks Phase acceptance.

## Forbidden Edges

| Source | Target | Prohibition |
|---|---|---|
| identity_registry | admission | B0P identities are diagnostic-only and cannot promote |
| production_observation_qualification | admission | partial B0P qualification cannot promote or authorize search |
| spent_evaluation | admission | no candidate ranking |
| spent_evaluation | generation_lanes | no CEM/UCB/MCTS feedback |
| spent_evaluation | a7mem | no memory update |
| sealed_forward | scheduler | no forward OOS scheduling |
| benchmark_registry | a7mem | no benchmark positive memory |
| feature_state_fabric | strict_reward | State/event reward edge frozen until B1 |
| a7input0 | generation_lanes | unapproved fields cannot enter primary generator |
| bz | admission | undefined BZ cannot promote |
