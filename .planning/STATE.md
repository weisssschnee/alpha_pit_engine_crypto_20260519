# Crypto AlphaFactory Planning State

Registry SHA256: `532ECCD3A9AB618A8EEACF4BA30A8010CEE8AFF32AF7185D8FD5F63AE67F3CD8`.

## Formal Status

- `PHASE_A_GOVERNANCE_ACCEPTED`
- `SEARCH_COLLAPSE_SOURCE_PARTIALLY_IDENTIFIED`
- `RESEARCH_MODE_CONTROLLED_FROZEN_EPOCH_PREPARATION`
- Current phase: `SEARCH_ENGINE_REVISION_COMPLETED`
- Production observation qualification: `PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED`
- Phase B0P acceptance: `PHASE_B0P_PARTIALLY_ACCEPTED`
- Frozen signal behaviour: `FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED`
- NEXTGEN-DARK: `NEXTGEN_DARK_SCOPED_READY`
- Formal search: `FORMAL_SEARCH_FROZEN`
- CANARY: `B1S_CANARY_COMPLETED_WITH_NATURAL_QUOTA_UNDERFILL`
- Adaptive cross-epoch memory: `ADAPTIVE_CROSS_EPOCH_MEMORY_FROZEN`
- Candidate promotion: `NO_CANDIDATE_PROMOTION`
- Active stage: `EPOCH1_REVISION_COMPLETE_CONTINUING_TO_DESIGN_FREEZE`
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

## B1S-CANARY Closure

- `B1S.1` Frozen repo/data/capability/budget/contracts: `IMPLEMENTED_SHA_39DBD40`
- `B1S.2` Main capability CANARY: `COMPLETED_WITH_NATURAL_QUOTA_UNDERFILL`
- `B1S.3` BBO micro-CANARY: `COMPLETED_SCOPED_BBO_ONLY`
- `B1S.4` Equal-budget global-top-K controls: `COMPLETED_320_OF_320`
- `B1S.5` Adaptive challenger runtime namespace: `COMPLETED_64_QUERIES_NOT_PERSISTED`
- `B1S.6` Candidate promotion and memory boundary: `ENFORCED`
- `B1S.7` Graph/STATE closure: `IMPLEMENTED`

- Decision: `B1S_CANARY_COMPLETED_WITH_NATURAL_QUOTA_UNDERFILL`
- Frozen repo SHA: `39dbd40e6ce7bde3fbaba0067da6a5bfbae797f8`
- Frozen manifest SHA256: `897A36543AC4CB4E9F658DFA7CF0B71F869ACB3755F318F451AE039E63FDE1D2`
- Proposals / legal rate: `5120` / `0.8076171875`
- Stratified admissions: `564` of planned `640`
- Stratified strict evaluations: `315` of planned `320`
- Global-top-K strict evaluations: `320`
- Adaptive feedback queries: `64`
- Execution acceptance: `B1S_CANARY_EXECUTION_ACCEPTED` / `FIXED_BUDGET_CONTRACT_PRESERVED`
- Quota fill: `0.984375`; natural underfill `5` in `funding_event`; rerun required `False`
- Underfill explanation: This was not an interruption or failure. Funding-event yielded only 27 legal exact identities under the frozen proposal budget and one-exact-identity-one-vote contract; no identity was duplicated, admission relaxed, seed changed, proposal added, or budget extended.

## CRYPTO NEXTGEN SEARCH EPOCH-0 Design Freeze

- Status: `FROZEN_DEVELOPMENT_EPOCH_COMPLETED`
- Implementation subject: `3b608e08f3e95af45a00ea1b24694c600a268f9c`
- Frozen manifest SHA256: `CD839D4F095E330DE17EB50E69FC55F8AFDEEA16CADB0C62FF3CE3DE9E6E7E62`
- Proposals / lanes / seeds: `32768` / `9` / `[2701, 2709]`
- Strict budgets: `1024` stratified + `1024` equal-budget global-top-K
- Performance started: `True`
- Execution / strict fill: `COMPLETED` / `1801` of `2048` (`0.87939453125`)
- Development survivors / Pareto / frozen pack: `0` / `429` / `191`
- Natural full-identity underfill / rerun required: `True` / `False`
- Validated recommendation: `REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH` — zero development survivors, infeasible BBO family cap, and UCT reward-basin concentration; funding grammar capacity expanded beyond the B1S 27-identity limit
- Forward read / promotion / cross-epoch memory: `False` / `False` / `False`

## CRYPTO NEXTGEN SEARCH EPOCH-1

- Status: `SEARCH_ENGINE_REVISION_COMPLETED`
- Accepted Epoch-0 subject: `46616450b1477d54eb45e47a42a8ed0541ce6cb7`
- Revision subject: `ced7c45`
- BBO offline replay: `32` -> `128`; history rewritten `False`
- Design frozen / performance started / execution: `False` / `False` / `NOT_STARTED`
- Forward read / promotion / cross-epoch memory: `False` / `False` / `False`

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

Run the no-performance throughput smoke, freeze and hash the exact Epoch-1 design, synchronize the freeze control plane, then execute once without online changes. FORMAL_SEARCH_FROZEN, ADAPTIVE_CROSS_EPOCH_MEMORY_FROZEN, FORWARD_SEALED, and NO_CANDIDATE_PROMOTION remain in force.
