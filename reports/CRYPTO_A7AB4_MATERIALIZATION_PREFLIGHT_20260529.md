# CRYPTO A7AB-4 MATERIALIZATION PREFLIGHT

Generated: 2026-05-29T06:08:06Z

## Decision

`PASS_A7AB4_MATERIALIZATION_PREFLIGHT_READY_FOR_A7AB5_NUMERIC_REPLAY_CONTRACT`

A7AB-4 evaluates static A7AB-3 expressions for materialization, finite coverage, and activity only. It does not compute returns, run replay, execute search, train, or authorize alpha proof.

## Manifest

```json
{
  "activity_failure_count": 0,
  "activity_ok_count": 512,
  "activity_ok_rate": 1.0,
  "authorizes_a7ab5_numeric_replay_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_large_search": false,
  "authorizes_numeric_replay_execution": false,
  "authorizes_shadow_paper_live": false,
  "decision": "PASS_A7AB4_MATERIALIZATION_PREFLIGHT_READY_FOR_A7AB5_NUMERIC_REPLAY_CONTRACT",
  "eval_failure_count": 0,
  "evaluated_candidates": 512,
  "executes_materialization_preflight": true,
  "executes_replay": false,
  "executes_search": false,
  "executes_training": false,
  "family_count": 4,
  "full_timestamps_before_materialization_subset": 21025,
  "generated_at": "2026-05-29T06:08:06Z",
  "missing_field_count": 0,
  "missing_fields": [],
  "numeric_field_count": 5,
  "seed_field_count": 5,
  "selected_candidates": 512,
  "skeleton_count": 74,
  "stage": "A7AB-4",
  "symbols_loaded": 96,
  "timestamp_cap": 4096,
  "timestamps": 4096,
  "uses_may": false
}
```

## Family Materialization Summary

| family_id                    |   evaluated_count |   eval_success_count |   activity_ok_count |   median_finite_share |   median_nonzero_share |   skeleton_count |   seed_field_count |
|:-----------------------------|------------------:|---------------------:|--------------------:|----------------------:|-----------------------:|-----------------:|-------------------:|
| G0_price_return_reversal     |               128 |                  128 |                 128 |              0.988281 |                      1 |               48 |                  1 |
| G1_volatility_state_reversal |               179 |                  179 |                 179 |              0.847412 |                      1 |               48 |                  2 |
| G2_basis_premium_dislocation |               179 |                  179 |                 179 |              0.993896 |                      1 |               48 |                  2 |
| G3_seed_pair_interaction     |                26 |                   26 |                  26 |              0.847656 |                      1 |               26 |                  4 |

## Motif Materialization Summary

| motif                   |   evaluated_count |   activity_ok_count |   median_finite_share |   median_nonzero_share |
|:------------------------|------------------:|--------------------:|----------------------:|-----------------------:|
| clip_atom               |                35 |                  35 |              0.988281 |               0.975703 |
| clip_horizon_spread     |                66 |                  66 |              0.985962 |               1        |
| decay_atom              |                26 |                  26 |              0.985107 |               0.999932 |
| horizon_spread          |                74 |                  74 |              0.988281 |               1        |
| pair_clip_mul           |                 5 |                   5 |              0.881836 |               1        |
| pair_mul                |                 4 |                   4 |              0.847534 |               0.99317  |
| pair_rank_mul           |                 4 |                   4 |              0.917847 |               1        |
| pair_sub                |                 4 |                   4 |              0.850586 |               0.999726 |
| pair_winsor_sub         |                 5 |                   5 |              0.847412 |               1        |
| pair_zscore_sub         |                 4 |                   4 |              0.917969 |               1        |
| rank_atom               |                24 |                  24 |              0.994141 |               1        |
| rank_horizon_spread     |                37 |                  37 |              0.987793 |               1        |
| self_interaction        |                37 |                  37 |              0.987305 |               0.999    |
| single_atom             |                33 |                  33 |              0.993896 |               1        |
| winsor_atom             |                29 |                  29 |              0.993896 |               1        |
| winsor_self_interaction |                45 |                  45 |              0.988037 |               1        |
| zscore_atom             |                36 |                  36 |              0.987915 |               0.999879 |
| zscore_self_interaction |                44 |                  44 |              0.988281 |               1        |

## Operator Coverage

| operator   |   selected_candidate_count |
|:-----------|---------------------------:|
| Clip       |                        159 |
| Decay      |                        326 |
| Delta      |                        250 |
| Mean       |                        306 |
| Mul        |                        179 |
| Rank       |                        333 |
| Sub        |                        403 |
| TSRank     |                        178 |
| Winsor     |                        121 |
| ZScore     |                        260 |

## Blockers

No blockers.

## Candidate Summary Sample

| candidate_id           | family_id                | primary_seed_field   | motif                   | eval_success   |   finite_share |   nonzero_share | activity_ok   |
|:-----------------------|:-------------------------|:---------------------|:------------------------|:---------------|---------------:|----------------:|:--------------|
| a7ab3_3b8e498a22c42cbc | G0_price_return_reversal | trade_return_1h      | rank_atom               | True           |       0.999512 |        1        | True          |
| a7ab3_617d5fd64be60100 | G0_price_return_reversal | trade_return_1h      | zscore_atom             | True           |       0.988281 |        0.999411 | True          |
| a7ab3_385c707663bf3d94 | G0_price_return_reversal | trade_return_1h      | horizon_spread          | True           |       0.988281 |        1        | True          |
| a7ab3_e9d3ac5ca8c61f32 | G0_price_return_reversal | trade_return_1h      | self_interaction        | True           |       0.987061 |        0.996993 | True          |
| a7ab3_1b877fb7b527e1ae | G0_price_return_reversal | trade_return_1h      | clip_atom               | True           |       0.998047 |        0.998425 | True          |
| a7ab3_1bbac777d8c7cece | G0_price_return_reversal | trade_return_1h      | winsor_atom             | True           |       0.999512 |        1        | True          |
| a7ab3_b32904f3e48a1c9f | G0_price_return_reversal | trade_return_1h      | decay_atom              | True           |       0.994141 |        1        | True          |
| a7ab3_1f806f028de41c42 | G0_price_return_reversal | trade_return_1h      | rank_horizon_spread     | True           |       0.992676 |        1        | True          |
| a7ab3_2408450b6a3804c1 | G0_price_return_reversal | trade_return_1h      | zscore_self_interaction | True           |       0.991211 |        1        | True          |
| a7ab3_038bfab0a7a0ecb3 | G0_price_return_reversal | trade_return_1h      | clip_horizon_spread     | True           |       0.986328 |        1        | True          |
| a7ab3_1615f89091205d2b | G0_price_return_reversal | trade_return_1h      | winsor_self_interaction | True           |       0.992676 |        1        | True          |
| a7ab3_90e5cc8b69d8e4f8 | G0_price_return_reversal | trade_return_1h      | single_atom             | True           |       0.993896 |        0.991403 | True          |
| a7ab3_568082728e6a9609 | G0_price_return_reversal | trade_return_1h      | rank_atom               | True           |       0.998047 |        1        | True          |
| a7ab3_09c000b24485330c | G0_price_return_reversal | trade_return_1h      | zscore_atom             | True           |       0.993408 |        1        | True          |
| a7ab3_8a63f47f08ef2ff2 | G0_price_return_reversal | trade_return_1h      | horizon_spread          | True           |       0.988281 |        1        | True          |
| a7ab3_54087a42f7c10ba9 | G0_price_return_reversal | trade_return_1h      | self_interaction        | True           |       0.987305 |        0.999817 | True          |
| a7ab3_e3e5d9d8a8429553 | G0_price_return_reversal | trade_return_1h      | clip_atom               | True           |       0.993896 |        0.964398 | True          |
| a7ab3_29a63a6062424850 | G0_price_return_reversal | trade_return_1h      | winsor_atom             | True           |       0.988281 |        1        | True          |
| a7ab3_972af57f374b5dfa | G0_price_return_reversal | trade_return_1h      | decay_atom              | True           |       0.990723 |        1        | True          |
| a7ab3_98b89c29ed9d981a | G0_price_return_reversal | trade_return_1h      | rank_horizon_spread     | True           |       0.982666 |        1        | True          |
| a7ab3_86e5ec09c46a292b | G0_price_return_reversal | trade_return_1h      | zscore_self_interaction | True           |       0.988281 |        1        | True          |
| a7ab3_c96b6ce75090d30c | G0_price_return_reversal | trade_return_1h      | clip_horizon_spread     | True           |       0.992188 |        1        | True          |
| a7ab3_19c5ae8eb5cebf96 | G0_price_return_reversal | trade_return_1h      | winsor_self_interaction | True           |       0.991211 |        0.999856 | True          |
| a7ab3_eaae2209184ca101 | G0_price_return_reversal | trade_return_1h      | single_atom             | True           |       0.988281 |        1        | True          |
| a7ab3_39d7d82ced61179e | G0_price_return_reversal | trade_return_1h      | rank_atom               | True           |       0.998291 |        1        | True          |
| a7ab3_7fa990b397bb88bd | G0_price_return_reversal | trade_return_1h      | zscore_atom             | True           |       0.993408 |        1        | True          |
| a7ab3_dfba4b96be94d2d4 | G0_price_return_reversal | trade_return_1h      | horizon_spread          | True           |       0.988281 |        1        | True          |
| a7ab3_b979e5779612d9dd | G0_price_return_reversal | trade_return_1h      | self_interaction        | True           |       0.988281 |        1        | True          |
| a7ab3_6a5ba7fe2527a46c | G0_price_return_reversal | trade_return_1h      | clip_atom               | True           |       0.976562 |        1        | True          |
| a7ab3_03c8dd1e0f1406bb | G0_price_return_reversal | trade_return_1h      | winsor_atom             | True           |       0.993652 |        1        | True          |
| a7ab3_1d0854ac5ec2163d | G0_price_return_reversal | trade_return_1h      | decay_atom              | True           |       0.983643 |        0.99993  | True          |
| a7ab3_8a1c4ec5e39f7a5a | G0_price_return_reversal | trade_return_1h      | rank_horizon_spread     | True           |       0.987793 |        1        | True          |
| a7ab3_5244861cb5bca9f2 | G0_price_return_reversal | trade_return_1h      | zscore_self_interaction | True           |       0.988281 |        1        | True          |
| a7ab3_a0aabd2a13785c73 | G0_price_return_reversal | trade_return_1h      | clip_horizon_spread     | True           |       0.988281 |        1        | True          |
| a7ab3_8680c0acdd0b3423 | G0_price_return_reversal | trade_return_1h      | winsor_self_interaction | True           |       0.993408 |        0.988203 | True          |
| a7ab3_ac1d320447cdc0e1 | G0_price_return_reversal | trade_return_1h      | single_atom             | True           |       0.993164 |        1        | True          |
| a7ab3_679945dd31d9c8a9 | G0_price_return_reversal | trade_return_1h      | rank_atom               | True           |       0.988281 |        1        | True          |
| a7ab3_fe15894bfdfc1a5c | G0_price_return_reversal | trade_return_1h      | zscore_atom             | True           |       0.981934 |        0.999189 | True          |
| a7ab3_43a43b7a0cdeb066 | G0_price_return_reversal | trade_return_1h      | horizon_spread          | True           |       0.977051 |        1        | True          |
| a7ab3_5261a71eb76ffc5c | G0_price_return_reversal | trade_return_1h      | self_interaction        | True           |       0.988281 |        1        | True          |
