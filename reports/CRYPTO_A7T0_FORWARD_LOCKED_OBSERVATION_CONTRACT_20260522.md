# Crypto A7T-0 Forward-Locked Observation Contract

- generated_at: `2026-05-22T07:10:45Z`
- decision: `PASS_A7T0_FORWARD_LOCKED_OBSERVATION_CONTRACT_READY`
- executes_search: `False`
- executes_replay: `False`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Scope

A7T-0 defines append-only observation rules for forward-only and research-only objects. It does not authorize trading or alpha proof.

## Forward Field Registry

| field_group                | local_path                                                                                 | current_status                           | append_only_key                            | historical_proof_allowed   | allowed_use                                                                                       | blocked_use                                            | path_exists   |
|:---------------------------|:-------------------------------------------------------------------------------------------|:-----------------------------------------|:-------------------------------------------|:---------------------------|:--------------------------------------------------------------------------------------------------|:-------------------------------------------------------|:--------------|
| orderbook_forward_snapshot | G:\AlphaFactory_CryptoData\silver\binance_api\orderbook_forward_snapshot                   | FORWARD_ONLY_AVAILABLE                   | collector_time;symbol                      | False                      | forward context; spread/depth telemetry; future locked observation after sufficient history       | 2024-2026 historical alpha proof or May retro-fit      | True          |
| positioning_forward        | G:\AlphaFactory_CryptoData\metadata\positioning_forward_state.csv                          | FORWARD_ONLY_AVAILABLE                   | event_time;observable_time;symbol;endpoint | False                      | append-only telemetry for OI/long-short/taker-ratio after collection time                         | backfilled historical proof before PIT/source contract | True          |
| aggtrades_enhanced_panel   | G:\AlphaFactory_CryptoData\gold\panels\crypto_core12_1h_with_aggtrades_features_v1.parquet | HISTORICAL_CORE3_READY_SOURCE_TRACE_PASS | symbol;timestamp                           | True                       | controlled diagnostics with availability mask; future observation if panel refresh is append-only | standalone activity/liquidity family promotion         | True          |

## Observation Object Registry

| object_id                                        | status                    | forward_observation_allowed   | proof_use                        | notes                                                                             |
|:-------------------------------------------------|:--------------------------|:------------------------------|:---------------------------------|:----------------------------------------------------------------------------------|
| FundingCore                                      | BENCHMARK_ONLY            | True                          | excluded_until_new_locked_window | funding line remains HOLD; observation is telemetry, not promotion                |
| Core4                                            | RESEARCH_OBJECT_ONLY      | True                          | excluded_until_new_locked_window | A7 baseline failures and drawdown issues remain unresolved                        |
| A7X3_near_miss_horizon_spread_flow_minus_btc_eth | STRESS_CLUE_NOT_CANDIDATE | True                          | monitor_only                     | two A7X-3 near-misses were control-clean pre-May but May-negative; not promotable |
| negative_controls                                | MANDATORY_CONTROL         | True                          | framework_health_only            | wrong-lag/row-shuffle/time-shuffle/sign-flip must remain non-promotable           |

## Append-Only Rules

| rule_id                       | rule                                                                                                                            | violation_action                             |
|:------------------------------|:--------------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------|
| freeze_before_window          | candidate list, formulas, scoring, gates, costs, lag rules, and negative controls must be frozen before a forward window starts | window evidence invalid for proof            |
| no_may_or_seen_forward_tuning | known May stress and observed forward outcomes cannot tune ranking, thresholds, weights, generation, or allocation              | downgrade to post-hoc diagnostic             |
| append_only_storage           | forward snapshots and positioning records must append with collector_time/observable_time; no overwrite without restatement log | hold affected window until restatement audit |
| negative_controls_required    | negative controls must be reported beside every monitored object                                                                | hold framework health claim                  |
| no_trade_authorization        | A7T telemetry cannot authorize shadow, paper, live, or production book                                                          | promotion blocked                            |

## Output Contract

| artifact                 | required_fields                                                                      | proof_status                                |
|:-------------------------|:-------------------------------------------------------------------------------------|:--------------------------------------------|
| hourly_forward_snapshot  | timestamp;symbol;object_id;signal;position_proxy;source_version;collector_time       | telemetry_only                              |
| hourly_forward_pnl_proxy | timestamp;object_id;gross_pnl;fee_proxy;funding_proxy;net_pnl;cost_bps;lag_bars      | telemetry_only_until_locked_window_complete |
| negative_control_log     | timestamp;control_id;control_mode;net_pnl_proxy;status                               | framework_health                            |
| forward_window_manifest  | window_start;window_end;frozen_commit;input_data_hash;gate_version;restatement_count | required_for_any_future_claim               |

## Authorization

```json
{
  "authorizes_a7t1_forward_observation_runner_design": true,
  "authorizes_alpha_proof": false,
  "authorizes_historical_proof_from_forward_only_fields": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7T0_FORWARD_LOCKED_OBSERVATION_CONTRACT_READY",
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-22T07:10:45Z",
  "may_policy": "known_stress_not_training_or_tuning_input",
  "required_next": [
    "A7T-1 forward observation runner design after frozen commit/window selection",
    "A7S-1 field availability/source-trace audit for newly delivered historical fields",
    "No promotion from A7T telemetry alone"
  ]
}
```

## Required Next

- Implement A7T-1 only after selecting a frozen commit/window.
- Keep all forward-only fields out of historical proof.
- Report negative controls beside every forward object.