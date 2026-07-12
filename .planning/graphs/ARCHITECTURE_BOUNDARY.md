# Architecture Boundary

Generated from registry SHA256: `27A2B09389855011B96FA065D375B6D339C8588C4EC840C98CFDE96A5A43FF0C`.

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
| b1s_main_canary | b1s_bbo_micro_canary | main metrics cannot rank or extrapolate BBO micro results |
| b1s_bbo_micro_canary | b1s_main_canary | BBO micro metrics cannot rank main candidates |
| spent_evaluation | b1s_canary_control | validation/test/recent/May stress cannot enter B1S feedback |
| sealed_forward | b1s_canary_control | sealed forward cannot enter B1S |
| b1s_canary_control | a7mem | B1S cannot update positive or negative A7MEM |
| b1s_canary_control | admission | B1S survivors cannot enter candidate promotion |
| b1s_canary_control | scheduler | B1S cannot persist policy, elite, learned value, or adaptive budget |
| spent_evaluation | epoch0_frozen_design | validation/test/recent/May stress cannot enter Epoch-0 |
| sealed_forward | epoch0_frozen_design | sealed forward cannot enter Epoch-0 |
| epoch0_frozen_design | a7mem | no cross-epoch elite, policy, value or statistics |
| epoch0_frozen_design | admission | Epoch-0 cannot promote candidates |
| epoch0_frozen_design | scheduler | no online budget, grammar, reward or admission changes |
| epoch0_execution | a7mem | no adaptive statistics, policy, elite or value persistence |
| epoch0_execution | admission | frozen candidate pack cannot promote |
| epoch0_execution | scheduler | no automatic rotating epoch or rerun |
| spent_evaluation | epoch0_execution | spent evaluation cannot enter execution or recommendation |
| sealed_forward | epoch0_execution | forward remains sealed after completion |
| spent_evaluation | epoch1_search_revision | spent evaluation cannot tune revision contracts |
| sealed_forward | epoch1_search_revision | sealed forward cannot enter revision or replay |
| spent_evaluation | epoch1_frozen_design | validation/test/recent/May stress cannot enter Epoch-1 |
| sealed_forward | epoch1_frozen_design | sealed forward cannot enter Epoch-1 |
| epoch1_frozen_design | a7mem | no cross-epoch elite, policy, value or statistics |
| epoch1_frozen_design | admission | Epoch-1 cannot promote candidates |
| epoch1_frozen_design | scheduler | no online budget, reward, seed, grammar or admission changes |
| epoch1_execution | a7mem | no adaptive policy or learned value persistence |
| epoch1_execution | admission | Epoch-1 candidates cannot promote |
| epoch1_execution | scheduler | no automatic rerun or next epoch |
| spent_evaluation | epoch1_execution | spent evaluation cannot enter execution or recommendation |
| sealed_forward | epoch1_execution | forward remains sealed during and after execution |
| spent_evaluation | epoch1r_admission_repair | repair and admission preflight cannot read spent evaluation |
| sealed_forward | epoch1r_admission_repair | repair and admission preflight cannot read forward data |
| spent_evaluation | epoch1r_execution | spent evaluation cannot enter Epoch-1R strict execution |
| sealed_forward | epoch1r_execution | forward remains sealed during and after Epoch-1R |
| epoch1r_execution | a7mem | Epoch-1R cannot persist adaptive state or memory |
| epoch1r_execution | admission | Epoch-1R cannot promote candidates |
| epoch1r_execution | scheduler | Epoch-1R cannot auto-rerun, reallocate or schedule another epoch |
| sealed_forward | epoch2_execution | forward remains sealed during Epoch-2 |
| spent_evaluation | epoch2_execution | spent evaluation cannot enter Epoch-2 |
| epoch2_execution | a7mem | Epoch-2 cannot persist adaptive state or memory |
| epoch2_execution | admission | Epoch-2 cannot promote candidates |
| epoch2_execution | scheduler | Epoch-2 cannot auto-rerun or extend budget |
