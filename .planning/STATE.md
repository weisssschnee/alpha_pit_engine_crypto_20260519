# Crypto AlphaFactory Planning State

Registry SHA256: `F2663F7BDDC3BAEC4E18E9850F1327154E7F1132E7A8F9432539B2B3D1622F63`.

## Formal Status

- `PHASE_A_GOVERNANCE_ACCEPTED`
- `SEARCH_COLLAPSE_SOURCE_PARTIALLY_IDENTIFIED`
- `HOLD_RESEARCH`
- Current phase: `PHASE_B0_CONTRACTS_AND_OBSERVATION_FOUNDATION`
- Phase B1: `FROZEN`
- Forward data: `SEALED_NO_NEW_FORWARD_READ`

## Remote Baseline

- Branch: `audit/evalreset-collapse-forensics-20260711`
- Local Phase A SHA: `e1fa83493b1ee1893992fb37604d21099c5aad65`
- Remote Phase A SHA: `e1fa83493b1ee1893992fb37604d21099c5aad65`
- Baseline tag commit: `ac9fd24ede281bbcbf438f7c2f4f9b1e563b8b76`
- Sync status: `VERIFIED_SYNCED_2026_07_11`

The earlier unsynchronized state is superseded by the verified remote refs above. Current B0 commits may be locally ahead until their own post-test push.

## Phase B0 Items

- `B0.1` Funding event detector and audit: `IMPLEMENTED`
- `B0.2` Future wrong-lag negative control: `IMPLEMENTED`
- `B0.3` A7INPUT0-v2 field roles: `IMPLEMENTED`
- `B0.4` BZ authority contract: `IMPLEMENTED`
- `B0.5` Layered identity registry: `IMPLEMENTED`
- `B0.6` Benchmark registry: `PLANNED`
- `B0.7` Temporal/event primitive contract: `PLANNED`
- `B0.8` Feature/State Fabric schema and cache contract: `PLANNED`

## Allowed

- contracts
- registries
- synthetic and historical audit fixtures
- deterministic cache schema
- control-plane graph maintenance

## Prohibited

- search execution
- new generator fields
- State/event to reward
- CEM/UCB/MCTS update
- A7MEM positive memory update
- new forward performance read
- spent OOS candidate selection

## Next Acceptance Gate

All B0.1-B0.8 contracts, registries, tests, graph nodes, STATE, decision log, run manifest, and artifact index are synchronized; then stop before B1.
