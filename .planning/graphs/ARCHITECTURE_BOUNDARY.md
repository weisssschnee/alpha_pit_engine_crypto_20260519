# Architecture Boundary

Generated from registry SHA256: `C3497D0F93DCBA57A51B8BB64C54BA300033737A1A5073CEEE79744CE70E5E83`.

## Authority

1. Current user instruction and governance decisions.
2. `config/crypto_architecture_control_registry_v1.json` for architecture nodes and edges.
3. `config/crypto_phase_state_v1.json` and the EVALRESET decision log for phase state.
4. Curated architecture documents generated from those sources.
5. `graph.json` as raw navigation plus deterministic control overlay.

External graphify is currently unavailable. This does not permit manual architecture claims: `scripts/crypto_architecture_control_plane.py --check` must pass.

## Acceptance Rule

Any code, registry, route, artifact, curated document, STATE, decision log, run manifest, artifact index, or control graph mismatch blocks Phase acceptance.

## Forbidden Edges

| Source | Target | Prohibition |
|---|---|---|
| spent_evaluation | admission | no candidate ranking |
| spent_evaluation | generation_lanes | no CEM/UCB/MCTS feedback |
| spent_evaluation | a7mem | no memory update |
| sealed_forward | scheduler | no forward OOS scheduling |
| benchmark_registry | a7mem | no benchmark positive memory |
| feature_state_fabric | strict_reward | State/event reward edge frozen until B1 |
| a7input0 | generation_lanes | unapproved fields cannot enter primary generator |
| bz | admission | undefined BZ cannot promote |
