# Current Architecture

Generated from `config/crypto_architecture_control_registry_v1.json`. Registry SHA256: `8CF30496E2493072A3B36416C5365BD3C6A771602C2D89C4EB671197852E40D1`.

Status: `PHASE_B0_CONTRACTS_ACCEPTED` / `PHASE_B0_PRODUCTION_OBSERVATION_QUALIFICATION_PENDING` / `HOLD_RESEARCH` / `PHASE_B1_FROZEN` / `SEALED_NO_NEW_FORWARD_READ`.

Authority: `config/crypto_architecture_control_registry_v1.json` is the machine-readable architecture authority; `graph.json` is its deterministic graph view; this file is the human-readable generated view. Raw graphify is unavailable, so `graph.json` retains the prior navigation graph plus a deterministic `control_*` overlay.

## Architecture

```mermaid
flowchart TD
  control_data_release["Data release\nIMPLEMENTED"]
  control_time_block_roles["Time block roles\nIMPLEMENTED"]
  control_field_ontology["Field ontology\nIMPLEMENTED"]
  control_a7input0["A7INPUT0-v2 field roles\nIMPLEMENTED"]
  control_feature_builder["Feature builders\nPARTIAL"]
  control_label_builder["Label builders\nIMPLEMENTED"]
  control_regime_builder["Regime builders\nPARTIAL"]
  control_funding_event_detector["Funding event detector\nIMPLEMENTED"]
  control_basis_oi_event_detection["Basis/OI event detection\nPARTIAL"]
  control_semantic_compiler["Semantic compiler\nIMPLEMENTED"]
  control_exact_signal_identity["Exact signal identity\nIMPLEMENTED"]
  control_identity_registry["Layered identity registry\nIMPLEMENTED"]
  control_generation_lanes["Generation lanes\nFROZEN"]
  control_proxy["Proxy evaluator\nFROZEN"]
  control_strict_reward["Strict reward\nFROZEN"]
  control_admission["Admission gates\nPARTIAL"]
  control_a7mem["A7MEM\nFROZEN"]
  control_scheduler["Scheduler / successive halving\nFROZEN"]
  control_benchmark_registry["Benchmark registry\nIMPLEMENTED"]
  control_evaluation_access_ledger["Evaluation access ledger\nIMPLEMENTED"]
  control_spent_evaluation["Spent historical evaluation\nFROZEN"]
  control_sealed_forward["Sealed forward data\nFROZEN"]
  control_future_wrong_lag["Future wrong-lag control\nIMPLEMENTED"]
  control_bz["BZ / Benchmark Zero\nIMPLEMENTED"]
  control_temporal_event_contract["Temporal/event primitive contract\nIMPLEMENTED"]
  control_feature_state_fabric["Feature/State Fabric\nIMPLEMENTED"]
  control_data_release --> control_time_block_roles
  control_time_block_roles --> control_field_ontology
  control_field_ontology --> control_a7input0
  control_a7input0 --> control_feature_builder
  control_feature_builder --> control_semantic_compiler
  control_semantic_compiler --> control_exact_signal_identity
  control_exact_signal_identity --> control_identity_registry
  control_identity_registry --> control_admission
  control_evaluation_access_ledger --> control_proxy
  control_evaluation_access_ledger --> control_strict_reward
  control_funding_event_detector --> control_temporal_event_contract
  control_temporal_event_contract --> control_feature_state_fabric
  control_bz --> control_benchmark_registry
  control_spent_evaluation --> control_proxy
  control_spent_evaluation --> control_strict_reward
  control_spent_evaluation -. forbidden .-> control_admission
  control_spent_evaluation -. forbidden .-> control_generation_lanes
  control_spent_evaluation -. forbidden .-> control_a7mem
  control_sealed_forward -. forbidden .-> control_scheduler
  control_benchmark_registry -. forbidden .-> control_a7mem
  control_feature_state_fabric -. forbidden .-> control_strict_reward
  control_a7input0 -. forbidden .-> control_generation_lanes
  control_bz -. forbidden .-> control_admission
```

## Node Registry

| Node | Status | Implementation | Entrypoint | Input -> Output | Data role | Feedback | Artifact/test | Last verified SHA | Blocker |
|---|---|---|---|---|---|---|---|---|---|
| Data release | IMPLEMENTED | runtime/a7eff2_git_release_20260711/a7eff2_release_manifest.json | a7eff2_release_manifest.json | immutable released artifacts -> hash-addressed release evidence | historical release evidence | AUDIT_ONLY | runtime/a7evalreset0_evaluation_governance_20260711/a7evalreset0_release_integrity_audit.csv | 1D5B5C5D498F65DE0DAC360A4604036F654119666DCEF32E256501B65C2A9D60 | source arrays absent locally |
| Time block roles | IMPLEMENTED | config/crypto_evaluation_access_policy_v1.json | epoch_access | epoch id -> discovery/spent/sealed role | evaluation governance | TRAIN_OR_INNER_VALIDATION_ONLY | tests/test_evaluation_access.py | 57B23A06C28A64F230C39B82D39E4631B7D195898B686E27B869233EDB728FBC | none |
| Field ontology | IMPLEMENTED | runtime/a7ffr1_field_ontology_v3/a7ffr1_field_ontology_v3.csv | a7ffr1_field_ontology_v3.csv | source and derived fields -> semantic/value-domain roles | field semantics | NO_DIRECT_FEEDBACK | runtime/a7eff2_git_release_20260711/a7eff2_active_field_registry.csv | 6087848CEA8B417D33446C759D8CBC7B78925617E048A3DC8D25D0C1CEE1205E | ontology is broader than approved inputs |
| A7INPUT0-v2 field roles | IMPLEMENTED | runtime/a7input0_input_approval_package/a7input0_input_approval_registry.csv; alphafactory_crypto/input_roles.py; config/crypto_a7input0_v2_role_policy.json; scripts/crypto_b0_a7input0_v2_registry.py | classify_input_role / a7input0_v2_field_role_registry.csv | field ontology -> approved input roles | input authorization | NO_OOS_DERIVATION | runtime/a7input0_v2_field_roles_20260711/a7input0_v2_field_role_registry.csv; runtime/a7input0_v2_field_roles_20260711/a7input0_v2_manifest.json; tests/test_input_roles.py; reports/CRYPTO_B0_A7INPUT0_V2_FIELD_ROLES_20260711.md | 1ABE655340B55FDCF259D6F76411A0028F78A6FA58921CBFACE764090F649F9C | roles are registered but all generator enablement remains false in B0 |
| Feature builders | PARTIAL | scripts/crypto_a7ak_lv1_latent_state_feature_build.py | feature build scripts | approved observable fields -> historical features | feature construction | NO_NEW_GENERATOR_FIELDS_THROUGH_B0P | runtime/a7al0r_code_feature_regime_readiness_audit/a7al0r_feature_lineage_ledger.csv | 60B7FC55A963B16D6D877D9E0B88C450694CA5F414C84EFE2CDCB220D8C0B493 | Feature/State Fabric contract implemented; production materialization and generator integration remain frozen until B1 |
| Label builders | IMPLEMENTED | scripts/crypto_a7aa1_primitive_response_map.py | horizon_label | PIT prices and horizons -> research labels | label only | SPENT_EPOCH_REPORT_ONLY | scripts/crypto_a7al2x5_evaluator_preflight_smoke.py | 278CDCF482AF999B93946C24123877CD919E6AEB7F804F9C051394297A8FB922 | no untouched final OOS |
| Regime builders | PARTIAL | scripts/crypto_a7al0g_upper_regime_state_builder.py | regime builder scripts | historical features -> regime/state observations | state and audit | FROZEN_FROM_REWARD_UNTIL_B1 | runtime/a7al0g_upper_regime_state_builder/a7al0g_regime_state_contract.csv | 92AE2B97BB46B86A2C2525BF66F6E0A7B92BD276E42138964930774D05EA6288 | reusable State object not established |
| Funding event detector | IMPLEMENTED | alphafactory_crypto/funding_events.py; alphafactory_crypto/funding_qualification.py; config/crypto_funding_event_contract_v1.json; config/crypto_b0p_funding_qualification_v1.json; scripts/crypto_b0_funding_event_audit.py; scripts/crypto_b0p_funding_qualification.py | canonicalize_funding_events / qualify_production_funding | native funding settlement records -> canonical payment events and audit | event observation | AUDIT_ONLY_THROUGH_B0P | tests/test_funding_events.py; tests/test_funding_qualification.py; runtime/a7b0_funding_event_contract_20260711/funding_event_audit_summary.json; runtime/a7b0p_funding_qualification_20260711/funding_qualification_summary.json; runtime/a7b0p_funding_qualification_20260711/approved_funding_truth_set.csv; runtime/a7b0p_funding_qualification_20260711/funding_symbol_month_coverage.csv; reports/CRYPTO_B0_FUNDING_EVENT_CONTRACT_20260711.md; reports/CRYPTO_B0P_FUNDING_PRODUCTION_QUALIFICATION_20260711.md | 8864ABDDB019147EFA0767A5F7A7A7F76205B9EC2D38120AED4FF9B30E36C6C3 | BINANCE_UM core12 production observation qualified through 2026-04-30; no cross-venue qualification is claimed |
| Basis/OI event detection | PARTIAL | scripts/crypto_a7regime2_mechanism_regime_audit.py | mechanism regime audit | basis and OI observations -> historical mechanism states | event/state audit | FROZEN_FROM_REWARD_UNTIL_B1 | runtime/a7regime2_mechanism_regime_audit_20260612/a7regime2_hourly_mechanism_state_panel.csv | CB1EDDE3AA987D74C4478A141D2A775076EC8F01E71B66588A0FF76307A4AAA5 | temporal/event primitive contract implemented; production detector qualification and lane integration remain pending |
| Semantic compiler | IMPLEMENTED | alphafactory_crypto/engines/semantic_domains.py | semantic canonicalization | typed AST and field domains -> canonical expression | semantic identity | NO_METRIC_FEEDBACK | docs/adr/0001-controlled-semantic-identity-and-safediv-gates.md | 8673D940C00111D362E55FE1A70B5F52F77D2BA9FA37882221C8CBE0166F2AC3 | none |
| Exact signal identity | IMPLEMENTED | alphafactory_crypto/engines/signal_identity.py | signal fingerprint | materialized signal weights -> representative and aliases | exact numeric identity | REPORT_ONLY_DURING_HOLD | runtime/a7eff2_git_release_20260711/a7eff2_accepted_train_validation_oos_log.csv | FCA93D783E1F0950C899906D810509DA637FD81A8059A9DF3C6DBB2D74B02DF8 | activation and PnL/regime artifacts remain unresolved |
| Layered identity registry | IMPLEMENTED | alphafactory_crypto/identity_registry.py; config/crypto_identity_layers_v1.json; scripts/crypto_b0_identity_registry.py | syntax_identity through register_economic_hypothesis | syntax through economic hypothesis -> six-layer identities and mappings | identity governance | NO_PROMOTION_THROUGH_B0P | tests/test_identity_registry.py; runtime/a7b0_identity_registry_20260711/layered_identity_registry.csv; runtime/a7b0_identity_registry_20260711/identity_registry_manifest.json; reports/CRYPTO_B0_LAYERED_IDENTITY_REGISTRY_20260711.md | CDE4384AD367F1EA6CC6A5C09A682A8CDC5EE6C0F8463E8D0A750CDA8179007F | activation, PnL/regime, and economic hypothesis IDs remain unresolved without artifacts/provenance |
| Generation lanes | FROZEN | scripts/crypto_a7ls1_multi_arm_blueprint_generation.py | generation scripts | approved fields and primitives -> candidate queues | candidate generation | NO_RUN_THROUGH_B0P | verified_core_crypto_20260618/holds/CEM_AST_SEARCH_CORE_HOLD.md | 08493D1801C8D733E3EE1F8B7F755259D4B6CE0D599985DC51B70E046CC051BC | search revoked; role classification does not authorize generation |
| Proxy evaluator | FROZEN | scripts/crypto_a7v3s9_prereward_oos_control_proxy.py | proxy main | candidate queue and spent historical metrics -> report-only diagnostics | historical evaluation | NO_CANDIDATE_FEEDBACK | tests/test_evaluation_access.py | 227162B70E5897768F07D9E7A7E5C7A7E1FB0EAA81AA0BC4552D210694581128 | spent OOS contamination |
| Strict reward | FROZEN | scripts/crypto_a7reward1_portfolio_reward_model.py | aggregate_rewards | signals and historical splits -> report-only reward audit | historical evaluation | NO_CANDIDATE_FEEDBACK | tests/test_evaluation_access.py; tests/test_future_wrong_lag.py | 1A1293EF5304B9772109A854F65D7E505653B22E901F024A51B1325ED2DA95CC | spent OOS; production negative control not executed during HOLD_RESEARCH |
| Admission gates | PARTIAL | scripts/crypto_a7source5_a7search7_source_lag_reward_flow.py | semantic/source-lag/identity gates | candidate rows -> survivors and aliases | candidate admission | REPORT_ONLY_THROUGH_B0P | runtime/a7evalreset0_evaluation_governance_20260711/a7evalreset0_collapse_stage_audit.csv | 9E4B859D56B665BADB4A6F579CAF31BEAA107A3E45CE70685911F740858A69F1 | independent-information collapse not localized |
| A7MEM | FROZEN | scripts/crypto_a7mem0_search_memory_registry.py | memory registry main | candidate feedback -> search priors | search memory | NO_POSITIVE_OR_NEGATIVE_UPDATE_THROUGH_B0P | tests/test_evaluation_access.py | 7EC9C27A3FDD1AE8D5CCB6D674B2DBD092704CECB22593C3E228AFAAD3988717 | all current candidate feedback is spent/OOS-derived |
| Scheduler / successive halving | FROZEN | scripts/crypto_a7source10_proxy_reward_flow_company_py_20260708.py | scheduler main | proxy/reward queues -> budgets and shards | compute allocation | NO_ADAPTIVE_OOS_FEEDBACK | tests/test_evaluation_access.py | AEA93934C17B10B0AC4EA5F833DFC807281F322DD481A3A8C39DCE1637FE53E6 | spent evaluation budget contamination |
| Benchmark registry | IMPLEMENTED | alphafactory_crypto/benchmarks.py; config/crypto_benchmark_registry_v1.json; scripts/crypto_b0_benchmark_registry.py | BenchmarkRegistry.register | benchmark definitions -> versioned benchmark observations | comparison only | NO_POSITIVE_MEMORY | tests/test_benchmarks.py; runtime/a7b0_benchmark_registry_20260711/benchmark_registry.csv; runtime/a7b0_benchmark_registry_20260711/benchmark_registry_manifest.json; reports/CRYPTO_B0_BENCHMARK_REGISTRY_20260711.md | C163766672593974442708124438F43BCB784B46A9383B2D2975810981CF8CB0 | benchmark execution remains frozen; observations are report-only |
| Evaluation access ledger | IMPLEMENTED | alphafactory_crypto/evaluation_access.py | assert_candidate_feedback_columns_allowed | epoch and metric access -> allow/block decision | evaluation governance | FAIL_CLOSED | runtime/a7evalreset0_evaluation_governance_20260711/a7evalreset0_evaluation_access_ledger.csv; tests/test_evaluation_access.py | 25D58EBAFB84B933E27AAEE25DB3BBD5C709440608E686BF3B7D76CA234BF76C | none |
| Spent historical evaluation | FROZEN | runtime/a7evalreset0_evaluation_governance_20260711/a7evalreset0_oos_burn_ledger.csv | OOS burn ledger | validation/test/recent/May -> spent classification | historical report only | DENY_CANDIDATE_FEEDBACK | tests/test_evaluation_access.py | CE9A5FE5B41F5858F65B8A1058C44E9C1D3572398A3080CBD32BC48D044F975A | irreversible exposure |
| Sealed forward data | FROZEN | config/crypto_evaluation_access_policy_v1.json | unknown epoch default | unseen epoch -> SEALED_FORWARD | sealed evaluation | NO_READ_THROUGH_B0P | tests/test_evaluation_access.py | 57B23A06C28A64F230C39B82D39E4631B7D195898B686E27B869233EDB728FBC | requires explicit future authorization |
| Future wrong-lag control | IMPLEMENTED | alphafactory_crypto/negative_controls.py; config/crypto_future_wrong_lag_control_v1.json; scripts/crypto_b0_future_wrong_lag_audit.py; scripts/crypto_a7reward1_portfolio_reward_model.py | future_wrong_lag / audit_future_wrong_lag | signal and future shifts -> negative-control metrics | leakage control | AUDIT_ONLY_THROUGH_B0P | tests/test_future_wrong_lag.py; runtime/a7b0_future_wrong_lag_control_20260711/future_wrong_lag_audit_summary.json; reports/CRYPTO_B0_FUTURE_WRONG_LAG_CONTROL_20260711.md | 8C10045585A87B577A001D07341FA1B8E06F9C14B5AA681471B760B1D54D4347 | production execution frozen during HOLD_RESEARCH |
| BZ / Benchmark Zero | IMPLEMENTED | alphafactory_crypto/bz.py; config/crypto_bz_benchmark_zero_v1.json; scripts/crypto_b0_bz_authority.py | create_benchmark_zero | benchmark-only fields -> zero-alpha diagnostic benchmark object | benchmark sanity only | NONE | tests/test_bz.py; runtime/a7b0_bz_authority_20260711/bz_authority_manifest.json; reports/CRYPTO_B0_BZ_BENCHMARK_ZERO_20260711.md | 1AFC8220B1F63A01959E16049E43D7D0324AA4CE00F246BC669679CEA59B093D | legacy undefined BZ mentions require explicit migration |
| Temporal/event primitive contract | IMPLEMENTED | alphafactory_crypto/temporal_contracts.py; config/crypto_temporal_event_primitives_v1.json; scripts/crypto_b0_temporal_event_contract.py | TemporalObservation / canonicalize_primitive / temporal_equivalent | observable event streams -> PIT temporal primitives | temporal semantics | NO_REWARD_THROUGH_B0P | tests/test_temporal_contracts.py; runtime/a7b0_temporal_event_contract_20260711/temporal_event_primitive_registry.csv; runtime/a7b0_temporal_event_contract_20260711/temporal_event_contract_manifest.json; reports/CRYPTO_B0_TEMPORAL_EVENT_PRIMITIVE_CONTRACT_20260711.md | 8755ED21F49B04334B7F3E272518197884082F91853A30324D4284A1B595E5DF | primitive execution and State/event reward coupling remain frozen until B1 |
| Feature/State Fabric | IMPLEMENTED | alphafactory_crypto/fabric.py; config/crypto_feature_state_fabric_v1.json; scripts/crypto_b0_feature_state_fabric.py | FabricArtifactSpec / deterministic_cache_key / write_deterministic_array_cache / validate_cache | approved observations and contracts -> deterministic feature/state cache | feature/state materialization | NO_REWARD_THROUGH_B0P | tests/test_fabric.py; runtime/a7b0_feature_state_fabric_20260711/feature_state_fabric_manifest.json; reports/CRYPTO_B0_FEATURE_STATE_FABRIC_20260711.md | B010B2324E71057D4879FC9AA4C875BC6896A9C341610DFE4741D5B9DE14C997 | real materialization, generator integration, and reward integration remain frozen until B1 |

## Time Block Roles

- 2024 train: discovery training, not OOS proof.
- 2025-06 validation, 2025-12 test, 2026-04 recent, and 2026-05 stress: `SPENT_HISTORICAL_EVALUATION`, report-only.
- Unknown/new epochs: `SEALED_FORWARD`, no read in B0.

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
