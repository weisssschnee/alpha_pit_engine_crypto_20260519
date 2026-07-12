# Crypto AlphaFactory Planning State

Registry SHA256: `1B481B1F193C487CFF925E1F3302C6911773374430656E465D67AB006773FE81`.

## Formal Status

- `PHASE_A_GOVERNANCE_ACCEPTED`
- `SEARCH_COLLAPSE_SOURCE_PARTIALLY_IDENTIFIED`
- `ANALYSIS_AND_ENGINEERING_ALLOWED`
- Current phase: `MECHANISM_DATA_EXPANSION0_FIRST_RELEASE_QUALIFIED`
- Production observation qualification: `PRODUCTION_OBSERVATION_PARTIALLY_QUALIFIED`
- Phase B0P acceptance: `PHASE_B0P_PARTIALLY_ACCEPTED`
- Frozen signal behaviour: `FROZEN_SIGNAL_BEHAVIOUR_QUALIFIED`
- NEXTGEN-DARK: `NEXTGEN_DARK_SCOPED_READY`
- Formal search: `NEW_PERFORMANCE_SEARCH_FROZEN`
- CANARY: `B1S_CANARY_COMPLETED_WITH_NATURAL_QUOTA_UNDERFILL`
- Adaptive cross-epoch memory: `ADAPTIVE_CROSS_EPOCH_MEMORY_FROZEN`
- Candidate promotion: `NO_CANDIDATE_PROMOTION`
- Active stage: `MECHANISM_BENCHMARK_CANARY_FROZEN_DESIGN_PENDING`
- Phase B1: `PHASE_B1_PERFORMANCE_INTEGRATION_FROZEN`
- Forward data: `SEALED_NO_NEW_FORWARD_READ`
- Mechanism/data inventory: `DATA_MECHANISM_INVENTORY_COMPLETED`
- First release-qualification candidate: `BINANCE_UM_NATIVE_AGGTRADES_CORE12_HISTORY`
- First qualified release: `NATIVE_AGGTRADES_RELEASE_QUALIFIED_SCOPED`
- Release content SHA256: `9A715BD4EC8461E533BFBA43B33CC67A30596E026800DF90CD604BBB02BF9A3D`

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

- Status: `EPOCH1_EXECUTION_FAILED_PRE_STRICT`
- Accepted Epoch-0 subject: `46616450b1477d54eb45e47a42a8ed0541ce6cb7`
- Revision subject: `da030b362977af6106a39a2584fc7fdc203d4139`
- BBO offline replay: `32` -> `128`; history rewritten `False`
- Design frozen / performance started / execution: `True` / `True` / `FAILED_BEFORE_STRICT_EVALUATION`
- Attempts / persisted strict evaluations / rerun: `1` / `0` / `False`
- Failure: `EMPTY_FULL_IDENTITY_CAPACITY_NOT_HANDLED_AS_NATURAL_UNDERFILL`
- Recommendation: `REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH`
- Remote sync: `VERIFIED_SYNCED_WITH_EVIDENCE_TAG` for `403b3519773e18c38033b2eaeaf404c98320595a` after `4` attempts
- Forward read / promotion / cross-epoch memory: `False` / `False` / `False`

## CRYPTO NEXTGEN SEARCH EPOCH-1R

- Status: `FROZEN_DEVELOPMENT_EPOCH1R_COMPLETED_WITH_NATURAL_UNDERFILL`
- Repair scope: `EMPTY_REPRESENTATIVE_SET_ONLY`
- Failed evidence subject: `403b3519773e18c38033b2eaeaf404c98320595a`
- Upstream changes — generator / grammar / objective / adaptive / seeds / budgets: `False` / `False` / `False` / `False` / `False` / `False`
- Design frozen / strict started: `True` / `True`
- Frozen repo / manifest: `90a80795d4978497a2a5810ea02a5cdfdd1fac2e` / `4A04836FD6FC97ACF9F777075C2E8F049257FFC13E3740E318D2AF0D50FBFB15`
- Execution / strict / natural underfill: `COMPLETED` / `2052` / `True`
- Survivors / near misses / positive net LCB / adaptive successes: `0` / `84` / `2` / `0`
- Recommendation: `REVISE_SEARCH_ENGINE_AND_REPEAT_DEVELOPMENT_EPOCH`
- Remote sync: `VERIFIED_REMOTE_CONTAINS_EPOCH1R_CLOSURE` for closure `a9c119e4447755d76838373178c57ae8e05ab481` after `4` attempts

## CRYPTO EPOCH-2

- Status: `EPOCH2_STRICT_EVIDENCE_ACCEPTED`
- Hybrid comparison: `EPOCH2_HYBRID_COMPARISON_INVALID`
- Repair strategy: `BLOCKER_DIRECTED_REPAIR_STRATEGY_REJECTED`
- Calibration: `SURVIVOR_CONTRACT_CALIBRATED_REACHABLE`; planted/null pass `1.0` / `0.0`
- Frozen parents: `84` rows / `64` proposals / `57` exact identities
- Budget: `49152` proposals / `2304` strict / seeds `[5201, 5209]`
- Bias audit: `HOLD_RESEARCH_DEVELOPMENT_ONLY_OOS_NONE`
- Design frozen / performance started: `True` / `True`
- Forward read / promotion / cross-epoch memory: `False` / `False` / `False`

## CRYPTO EPOCH-2B Economic Bottleneck Audit

- Status: `ECONOMIC_BOTTLENECK_AUDIT_COMPLETED`
- Main recommendation: `PIVOT_TO_NEW_MECHANISM_OR_DATA`
- Existing logical strict rows read / new performance queries: `6157` / `0`
- Main median positive gross-LCB proxy fraction / rare-edge cost-kill share: `0.02944862155388471` / `0.9846153846153847`
- Parent classes — no edge / portfolio transform / unstable: `72` / `9` / `3`
- Adaptive operator cells without causal control / target crossing / collateral damage: `24` / `0.0` / `0.9036334913112164`
- Main NET_LCB near misses Epoch-1R -> Epoch-2 / distance change: `55` -> `174` / `0.13241328562959054`
- BBO secondary line: `BBO_DEVELOPMENT_COVERAGE_ACQUISITION_PLAN_ONLY`; positive exact / clusters / coverage `5` / `5` / `0.8222222222222222`

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

Freeze and execute only a simple native-trade-flow benchmark CANARY with sign-flip, wrong-lag, shuffled-timing, matched-random and incumbent controls; no complex generator or search may participate.
