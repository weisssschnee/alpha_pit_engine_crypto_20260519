# CRYPTO A7FF-CORE59 NUMERIC REPAIR EXECUTION

Generated: 2026-06-04T14:33:33Z

## Decision

`HOLD_A7FFCORE59_NUMERIC_REPAIR_EXECUTION`

CORE59 executes the numeric probe over the CORE58 failure-aware numeric queue. It is numeric execution, not replay/search/proof.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core60_numeric_forensic": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "non_l7_candidate_count_lt_24",
    "non_l7_semantic_count_lt_4"
  ],
  "decision": "HOLD_A7FFCORE59_NUMERIC_REPAIR_EXECUTION",
  "eval_failure_count": 0,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "external_runtime_dir": "D:/HermesWorker/GDrive/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604",
  "failed_shard_count": 0,
  "generated_at": "2026-06-04T14:33:33Z",
  "input_queue_rows": 1200,
  "label_response_rows": 12940,
  "materialized_activity_ok_count": 647,
  "non_l7_candidate_count": 6,
  "non_l7_numeric_clue_rows": 6,
  "non_l7_semantic_pair_count": 2,
  "rank_label_diagnostic_clue_rows": 341,
  "selected_portfolio_queue_count": 44,
  "shard_count": 6,
  "source_decision": "PASS_A7FFCORE58_FAILURE_AWARE_QUEUE_REBUILT_READY_FOR_CORE59",
  "source_stage": "A7FF-CORE58",
  "stage": "A7FF-CORE59",
  "timed_out_shard_count": 0,
  "uses_may": false
}
```

## Shard Summary

```csv
shard,returncode,timed_out,reused_existing,runtime_dir,queue_rows,decision,blockers,materialized_activity_ok_count,label_response_rows,non_l7_numeric_clue_rows,rank_label_diagnostic_clue_rows,selected_portfolio_queue_count
s00,0,False,True,D:/HermesWorker/GDrive/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604/shard_00,200,HOLD_A7FFCORE59S00_NO_ACTIVITY_OK_BLUEPRINTS,no_activity_ok_blueprints,0,0,0,0,0
s01,0,False,True,D:/HermesWorker/GDrive/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604/shard_01,200,HOLD_A7FFCORE59S01_NO_NON_L7_NUMERIC_CLUES,no_non_l7_numeric_clues,23,460,0,11,4
s02,0,False,True,D:/HermesWorker/GDrive/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604/shard_02,200,HOLD_A7FFCORE59S02_NO_NON_L7_NUMERIC_CLUES,no_non_l7_numeric_clues,154,3080,0,63,7
s03,0,False,True,D:/HermesWorker/GDrive/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604/shard_03,200,HOLD_A7FFCORE59S03_NO_NON_L7_NUMERIC_CLUES,no_non_l7_numeric_clues,144,2880,0,93,11
s04,0,False,True,D:/HermesWorker/GDrive/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604/shard_04,200,PASS_A7FFCORE59S04_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH,,164,3280,1,84,13
s05,0,False,True,D:/HermesWorker/GDrive/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604/shard_05,200,PASS_A7FFCORE59S05_NUMERIC_PROBE_CLUES_FOUND_NO_SEARCH_AUTH,,162,3240,5,90,9
```

## Materialization By Semantic

```csv
semantic_pair,rows,eval_success,activity_ok,median_finite_share,median_nonzero_share
basis_premium_like|price_like,282,282,230,0.9956908934214306,0.9879385963551817
basis_premium_like|volatility_like,213,213,167,0.8253375466819879,0.9888954060943111
basis_premium_like|basis_premium_like,200,200,132,0.9962654409652398,0.9441900749701323
price_like|volatility_like,51,51,43,0.8253375466819879,0.9879481378350156
basis_premium_like,38,38,36,0.9933927032461936,1.0
volatility_like|volatility_like,26,26,22,0.8256248204538925,0.9781246369234344
volatility_like,14,14,14,0.8273484630853203,1.0
price_like,3,3,3,0.9994254524561909,1.0
funding_like|positioning_like,13,13,0,0.0032647467202911,0.9007155635062611
basis_premium_like|funding_like,360,360,0,0.0006703054677774,0.9581056466302368
```

## Decision By Semantic

```csv
semantic_pair,decision,label_family,row_count
basis_premium_like|price_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L0_raw_forward_return,243
basis_premium_like|price_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,243
basis_premium_like|price_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,242
basis_premium_like|price_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,241
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,181
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L0_raw_forward_return,181
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,172
basis_premium_like|price_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,171
basis_premium_like|price_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L0_raw_forward_return,170
basis_premium_like|price_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,170
basis_premium_like|price_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,169
basis_premium_like|price_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,168
basis_premium_like|price_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L0_raw_forward_return,163
basis_premium_like|price_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,163
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,163
basis_premium_like|price_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,159
basis_premium_like|volatility_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,153
basis_premium_like|volatility_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L0_raw_forward_return,153
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,152
basis_premium_like|price_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L7_ranked_future_return,149
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,149
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L0_raw_forward_return,149
basis_premium_like|volatility_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,148
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,144
basis_premium_like|volatility_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,142
basis_premium_like|price_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,141
basis_premium_like|price_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,140
basis_premium_like|price_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,140
basis_premium_like|price_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L0_raw_forward_return,140
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_CONTROL_DOMINATED,L7_ranked_future_return,118
basis_premium_like|price_like,HOLD_A7FFCORE59S04_CONTROL_DOMINATED,L7_ranked_future_return,106
basis_premium_like|volatility_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,104
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L0_raw_forward_return,101
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,101
basis_premium_like|volatility_like,HOLD_A7FFCORE59S04_CONTROL_DOMINATED,L7_ranked_future_return,100
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,100
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,100
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,99
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,99
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L0_raw_forward_return,99
basis_premium_like|volatility_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,97
basis_premium_like|volatility_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,95
basis_premium_like|volatility_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L0_raw_forward_return,95
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L7_ranked_future_return,95
basis_premium_like|price_like,HOLD_A7FFCORE59S02_CONTROL_DOMINATED,L7_ranked_future_return,93
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,93
basis_premium_like|volatility_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L7_ranked_future_return,91
basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L0_raw_forward_return,88
basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,88
basis_premium_like|price_like,HOLD_A7FFCORE59S05_CONTROL_DOMINATED,L7_ranked_future_return,87
basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,87
basis_premium_like|volatility_like,HOLD_A7FFCORE59S02_CONTROL_DOMINATED,L7_ranked_future_return,86
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L7_ranked_future_return,86
volatility_like|volatility_like,HOLD_A7FFCORE59S01_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,84
basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,83
basis_premium_like|price_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L7_ranked_future_return,82
basis_premium_like|price_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L7_ranked_future_return,80
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S02_PRE_MAY_UNSTABLE,L7_ranked_future_return,77
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_CONTROL_DOMINATED,L3_liquidity_tier_relative_return,76
basis_premium_like|volatility_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,75
basis_premium_like|volatility_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L0_raw_forward_return,74
basis_premium_like|volatility_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L1_cross_sectional_relative_return,74
basis_premium_like|price_like,HOLD_A7FFCORE59S05_PRE_MAY_UNSTABLE,L7_ranked_future_return,73
basis_premium_like|volatility_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L3_liquidity_tier_relative_return,72
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S02_CONTROL_DOMINATED,L7_ranked_future_return,72
basis_premium_like|price_like,HOLD_A7FFCORE59S04_CONTROL_DOMINATED,L3_liquidity_tier_relative_return,71
basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L7_ranked_future_return,70
basis_premium_like|price_like,HOLD_A7FFCORE59S04_CONTROL_DOMINATED,L1_cross_sectional_relative_return,69
basis_premium_like|price_like,HOLD_A7FFCORE59S04_CONTROL_DOMINATED,L0_raw_forward_return,68
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_CONTROL_DOMINATED,L5_vol_adjusted_return,66
basis_premium_like|price_like,HOLD_A7FFCORE59S04_CONTROL_DOMINATED,L5_vol_adjusted_return,64
basis_premium_like|volatility_like,HOLD_A7FFCORE59S04_CONTROL_DOMINATED,L5_vol_adjusted_return,63
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_CONTROL_DOMINATED,L1_cross_sectional_relative_return,59
basis_premium_like|volatility_like,HOLD_A7FFCORE59S03_CONTROL_DOMINATED,L7_ranked_future_return,58
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S03_PRE_MAY_UNSTABLE,L7_ranked_future_return,57
basis_premium_like|volatility_like,HOLD_A7FFCORE59S05_CONTROL_DOMINATED,L0_raw_forward_return,57
basis_premium_like|volatility_like,HOLD_A7FFCORE59S04_CONTROL_DOMINATED,L3_liquidity_tier_relative_return,57
basis_premium_like|basis_premium_like,HOLD_A7FFCORE59S04_PRE_MAY_UNSTABLE,L5_vol_adjusted_return,55
basis_premium_like|price_like,HOLD_A7FFCORE59S05_CONTROL_DOMINATED,L0_raw_forward_return,54
basis_premium_like|price_like,HOLD_A7FFCORE59S03_CONTROL_DOMINATED,L7_ranked_future_return,54
```

## Non-L7 Clue Summary

```csv
semantic_pair,decision,label_family,row_count
basis_premium_like|price_like,A7FFCORE59S05_NUMERIC_CLUE,L5_vol_adjusted_return,2
basis_premium_like|price_like,A7FFCORE59S04_NUMERIC_CLUE,L0_raw_forward_return,1
basis_premium_like|price_like,A7FFCORE59S05_NUMERIC_CLUE,L1_cross_sectional_relative_return,1
basis_premium_like|price_like,A7FFCORE59S05_NUMERIC_CLUE,L3_liquidity_tier_relative_return,1
basis_premium_like|volatility_like,A7FFCORE59S05_NUMERIC_CLUE,L0_raw_forward_return,1
```

## Selected Summary

```csv
semantic_pair,label_family,row_count
basis_premium_like|price_like,L7_ranked_future_return,12
basis_premium_like|volatility_like,L7_ranked_future_return,10
basis_premium_like|basis_premium_like,L7_ranked_future_return,8
volatility_like|volatility_like,L7_ranked_future_return,4
price_like|volatility_like,L7_ranked_future_return,3
price_like,L7_ranked_future_return,3
volatility_like,L7_ranked_future_return,2
basis_premium_like,L7_ranked_future_return,1
basis_premium_like|price_like,L5_vol_adjusted_return,1
```

## External Detail Artifacts

```text
D:/HermesWorker/GDrive/AlphaFactory_CryptoData/research_runtime/a7ffcore59_numeric_repair_execution_20260604
```

## Boundary

```text
numeric probe executed: true
replay executed: false
search executed: false
May used: false
large search / alpha proof / shadow / paper / live: false
```
