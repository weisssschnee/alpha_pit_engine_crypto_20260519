# Crypto AlphaFactory Planning State

Registry SHA256: `0CACD837521139E8396D65895EB4B6A64D894BCB9B500A33F9E14FB5951059C4`.

## Formal Status

- `PHASE_A_GOVERNANCE_ACCEPTED`
- `SEARCH_COLLAPSE_SOURCE_PARTIALLY_IDENTIFIED`
- `HOLD_RESEARCH`
- Current phase: `PHASE_B0_CONTRACTS_COMPLETE_AWAITING_ACCEPTANCE`
- Phase B1: `FROZEN`
- Forward data: `SEALED_NO_NEW_FORWARD_READ`

## Remote Baseline

- Branch: `audit/evalreset-collapse-forensics-20260711`
- Local Phase A SHA: `e1fa83493b1ee1893992fb37604d21099c5aad65`
- Remote Phase A SHA: `e1fa83493b1ee1893992fb37604d21099c5aad65`
- Baseline tag commit: `ac9fd24ede281bbcbf438f7c2f4f9b1e563b8b76`
- Sync status: `VERIFIED_SYNCED_2026_07_11`

The earlier Phase A unsynchronized state is superseded by the verified remote refs above.

## Phase B0 Remote Status

- B0 completion SHA: `a0a36145ccd9666f5a137bee4b8414767aaa7ffd`
- Last verified remote SHA: `130c76d1abacc36761755b54d6fcf8efe58cd99f`
- Sync status: `VERIFIED_REMOTE_CONTAINS_B0_COMPLETION_2026_07_11`
- Blocker: None for branch transport; Phase B0 acceptance is still required and Phase B1 remains frozen.

## Phase B0 Items

- `B0.1` Funding event detector and audit: `IMPLEMENTED`
- `B0.2` Future wrong-lag negative control: `IMPLEMENTED`
- `B0.3` A7INPUT0-v2 field roles: `IMPLEMENTED`
- `B0.4` BZ authority contract: `IMPLEMENTED`
- `B0.5` Layered identity registry: `IMPLEMENTED`
- `B0.6` Benchmark registry: `IMPLEMENTED`
- `B0.7` Temporal/event primitive contract: `IMPLEMENTED`
- `B0.8` Feature/State Fabric schema and cache contract: `IMPLEMENTED`

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

Independent acceptance of the synchronized B0.1-B0.8 contracts, registries, tests, graph nodes, STATE, decision log, run manifest, and artifact index; B1 remains frozen.
