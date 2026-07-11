# Crypto AlphaFactory Planning State

Registry SHA256: `3D506C56A75546A985A05AA143B7B73CAE8E797756C1B96D553977B021E517DE`.

## Formal Status

- `PHASE_A_GOVERNANCE_ACCEPTED`
- `SEARCH_COLLAPSE_SOURCE_PARTIALLY_IDENTIFIED`
- `HOLD_RESEARCH`
- Current phase: `NEXTGEN_DARK_INFRASTRUCTURE_PARTIALLY_READY`
- Production observation qualification: `PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED`
- Phase B0P acceptance: `PHASE_B0P_PARTIALLY_ACCEPTED`
- Frozen signal behaviour: `FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED`
- NEXTGEN-DARK: `NEXTGEN_DARK_INFRASTRUCTURE_PARTIALLY_READY`
- Formal search: `FORMAL_SEARCH_FROZEN`
- CANARY: `CANARY_PLAN_PREPARED_NOT_AUTHORIZED_NOT_STARTED`
- Active stage: `NEXTGEN_DARK_CLOSED_WAITING_CANARY_AUTHORIZATION`
- Phase B1: `PHASE_B1_PERFORMANCE_INTEGRATION_FROZEN`
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

## NEXTGEN-DARK Closure

- `ND.1` Development-only Feature/State materialization: `PARTIAL_LIQUIDATION_NO_SOURCE_TOP_OF_BOOK_LIQUIDITY_SCOPED_QUALIFIED`
- `ND.2` Typed Temporal/Event Program: `IMPLEMENTED`
- `ND.3` Isolated hypothesis lanes: `IMPLEMENTED_NOT_EXECUTED`
- `ND.4` Anti-collapse admission: `IMPLEMENTED_QUOTA_TESTS_ONLY`
- `ND.5` Benchmark and competitor harness: `IMPLEMENTED_NOT_EXECUTED`
- `ND.6` Non-performance coverage metrics: `IMPLEMENTED`
- `ND.7` Fixed-budget CANARY plan: `PREPARED_NOT_AUTHORIZED_NOT_STARTED`
- `ND.8` Closure control-plane synchronization: `IMPLEMENTED`

## NEXTGEN-DARK Allowed

- development/pre-forward observable materialization
- typed temporal/event contract execution without performance
- deterministic lane and admission quota tests
- benchmark/challenger interface construction without comparison
- non-performance coverage accounting
- prepare but do not launch one fixed-budget CANARY plan

## NEXTGEN-DARK Prohibited

- formal search execution
- candidate performance evaluation or selection
- new forward read
- State/event connection to reward
- CEM/UCB/MCTS/A7MEM update
- online policy or budget reweighting
- automatic CANARY launch or Phase B1 performance integration

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

NEXTGEN-DARK remains PARTIALLY_READY because PC1 contains no liquidation/force-order source. PC1 top-of-book liquidity is scoped-qualified for Binance UM bookTicker only over its observed 2024-01/02 subset and is not multi-level depth. The fixed-budget development-only CANARY plan is not authorized and not started. HOLD_RESEARCH, FORMAL_SEARCH_FROZEN, PHASE_B1_PERFORMANCE_INTEGRATION_FROZEN, and SEALED_NO_NEW_FORWARD_READ remain in force.
