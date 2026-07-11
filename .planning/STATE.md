# Crypto AlphaFactory Planning State

Registry SHA256: `6B48E715ED8980832CB3FE0D37EAAD1DDF337D144FCA1CC30358836F807401FB`.

## Formal Status

- `PHASE_A_GOVERNANCE_ACCEPTED`
- `SEARCH_COLLAPSE_SOURCE_PARTIALLY_IDENTIFIED`
- `HOLD_RESEARCH`
- Current phase: `PHASE_B0_CONTRACTS_ACCEPTED`
- Production observation qualification: `PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED`
- Phase B0P acceptance: `PHASE_B0P_PARTIALLY_ACCEPTED`
- Frozen signal behaviour: `FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED`
- Active stage: `PHASE_B0A_COMPLETE_STOPPED`
- Phase B1: `PHASE_B1_FROZEN`
- Forward data: `SEALED_NO_NEW_FORWARD_READ`

## Remote Baseline

- Branch: `audit/evalreset-collapse-forensics-20260711`
- Local Phase A SHA: `e1fa83493b1ee1893992fb37604d21099c5aad65`
- Remote Phase A SHA: `e1fa83493b1ee1893992fb37604d21099c5aad65`
- Baseline tag commit: `ac9fd24ede281bbcbf438f7c2f4f9b1e563b8b76`
- Sync status: `VERIFIED_SYNCED_2026_07_11`

The earlier Phase A unsynchronized state is superseded by the verified remote refs above.

## Phase B0 Acceptance Attestation

- Accepted subject SHA: `9574d32053d1679d64179fe2d6607d1a05e13db9`
- Accepted subject remote ref: `refs/heads/audit/evalreset-collapse-forensics-20260711`
- Attestation artifact: `runtime/a7b0_control_plane_20260711/phase_b0_acceptance_attestation.json`
- Attestation commit policy: `INDEPENDENT_FOLLOWUP_COMMIT_NO_SELF_SHA`
- Status: `ATTESTED_PHASE_B0_CONTRACTS_ACCEPTED`

## Phase B0 Items

- `B0.1` Funding event detector and audit: `IMPLEMENTED`
- `B0.2` Future wrong-lag negative control: `IMPLEMENTED`
- `B0.3` A7INPUT0-v2 field roles: `IMPLEMENTED`
- `B0.4` BZ authority contract: `IMPLEMENTED`
- `B0.5` Layered identity registry: `IMPLEMENTED`
- `B0.6` Benchmark registry: `IMPLEMENTED`
- `B0.7` Temporal/event primitive contract: `IMPLEMENTED`
- `B0.8` Feature/State Fabric schema and cache contract: `IMPLEMENTED`

## Phase B0P Items

- `B0P.1` Funding production observation qualification: `QUALIFIED_BINANCE_UM_CORE12`
- `B0P.2` Layered identity completion: `PARTIALLY_QUALIFIED_ACTIVATION_ARTIFACT_MISSING`
- `B0P.3` Control-plane synchronization: `IMPLEMENTED`

## Phase B0P Partial Acceptance

- Accepted subject SHA: `5219e7899cad1be83f9bcf2ec520ed1ff5037f9e`
- Accepted subject remote ref: `refs/heads/audit/evalreset-collapse-forensics-20260711`
- Attestation artifact: `runtime/a7b0p_control_plane_20260711/phase_b0p_partial_acceptance_attestation.json`
- Funding: `PRODUCTION_FUNDING_OBSERVATION_QUALIFIED_WITHIN_BINANCE_UM_CORE12`
- Identity: `LAYERED_IDENTITY_PARTIALLY_QUALIFIED`
- Activation: `ACTIVATION_IDENTITY_NOT_QUALIFIED`

## Phase B0A Items

- `B0A.1` Frozen input binding: `IMPLEMENTED`
- `B0A.2` Signal behaviour sketch and masks: `IMPLEMENTED`
- `B0A.3` Deterministic repeat materialization: `QUALIFIED`
- `B0A.4` Activation and behaviour identities: `QUALIFIED`
- `B0A.5` PnL/regime no-feedback boundary: `ENFORCED`
- `B0A.6` Control-plane synchronization: `IMPLEMENTED`

## Phase B0A Result

- Decision: `FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED`
- Artifact: `runtime/a7b0a_signal_behaviour_20260711/signal_behaviour_sketch.bin`
- Artifact index: `runtime/a7b0a_signal_behaviour_20260711/b0a_artifact_index.csv`
- Artifact SHA256: `CD40C5C521DDBC6A2704D5A45A798CF3DAB5A5A7B6D2CD476D28F6BFB30C7D6B`
- Compression: `33 survivor rows -> 18 exact identities; accepted scope 16 aliases -> 6 exact -> 5 activation -> 4 behaviour -> 5 semantic hypotheses`
- N_eff: `3.0`
- Top-cluster share: `0.5`
- Cross-time stability median/min: `1.0` / `1.0`

## Phase B0A Allowed

- freeze existing accepted/candidate inputs and their hashes
- materialize signal behaviour from development and pre-forward observations only
- build activation and behaviour identities without returns, reward, or candidate changes
- verify deterministic materialization and coordinate-order invariance
- synchronize control-plane and B0A evidence artifacts

## Prohibited

- search execution
- new generator fields
- State/event to reward
- CEM/UCB/MCTS update
- A7MEM positive or negative memory update
- new forward performance read
- spent OOS candidate selection
- B1 lane integration

## Next Acceptance Gate

B0A is complete and stopped at FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED. Wait for an independent acceptance before any B1D work; HOLD_RESEARCH, PHASE_B1_FROZEN, and SEALED_NO_NEW_FORWARD_READ remain in force.
