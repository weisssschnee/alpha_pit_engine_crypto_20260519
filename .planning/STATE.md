# Crypto AlphaFactory Planning State

Registry SHA256: `3F5602C1357AEBB056CA445673B81011BBE6C9383A9194543DF2CBC7CCF4613E`.

## Formal Status

- `PHASE_A_GOVERNANCE_ACCEPTED`
- `SEARCH_COLLAPSE_SOURCE_PARTIALLY_IDENTIFIED`
- `HOLD_RESEARCH`
- Current phase: `PHASE_B0_CONTRACTS_ACCEPTED`
- Production observation qualification: `PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED`
- Active stage: `PHASE_B0P_COMPLETE_STOPPED`
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

## Phase B0P Allowed

- approved funding truth-set qualification without price returns or Alpha reward
- activation identity and activation clustering from signal behavior only
- PnL/regime identity from spent historical data for diagnostic-only use
- economic hypothesis identity from field, structure, and mechanism semantics only
- control-plane and identity artifact synchronization

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

B0P is stopped at PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED. Any B1 or activation-artifact work requires explicit authorization; large search and alpha-ready claims remain prohibited.
