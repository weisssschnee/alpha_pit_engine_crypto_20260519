# Architecture Boundary

Generated from registry SHA256: `3D506C56A75546A985A05AA143B7B73CAE8E797756C1B96D553977B021E517DE`.

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
| frozen_signal_behaviour_qualification | admission | B0A behaviour evidence cannot promote or select candidates |
| frozen_signal_behaviour_qualification | a7mem | B0A behaviour evidence cannot update memory |
| frozen_signal_behaviour_qualification | scheduler | B0A behaviour evidence cannot feed scheduler |
| frozen_signal_behaviour_qualification | strict_reward | B0A behaviour evidence cannot enter reward loop before B1D acceptance |
| spent_evaluation | admission | no candidate ranking |
| spent_evaluation | generation_lanes | no CEM/UCB/MCTS feedback |
| spent_evaluation | a7mem | no memory update |
| sealed_forward | scheduler | no forward OOS scheduling |
| benchmark_registry | a7mem | no benchmark positive memory |
| feature_state_fabric | strict_reward | State/event reward edge frozen until B1 |
| a7input0 | generation_lanes | unapproved fields cannot enter primary generator |
| bz | admission | undefined BZ cannot promote |
| nextgen_observation_fabric | strict_reward | NEXTGEN-DARK State/event outputs cannot enter reward |
| nextgen_observation_fabric | generation_lanes | new State/event outputs cannot enter legacy generator |
| isolated_hypothesis_lanes | a7mem | dark lanes cannot share or update A7MEM |
| challenger_harness | a7mem | benchmark/challenger results cannot enter positive memory |
| sealed_forward | canary_plan | CANARY cannot read sealed forward data |
| canary_plan | scheduler | CANARY is not authorized and cannot start scheduler |
