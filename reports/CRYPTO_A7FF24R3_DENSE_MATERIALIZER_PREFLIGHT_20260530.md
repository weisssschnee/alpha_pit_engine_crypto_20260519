# CRYPTO A7FF-24R3 DENSE MATERIALIZER PREFLIGHT

Generated: 2026-05-30T11:01:42Z

## Decision

`PASS_A7FF24R3_DENSE_MATERIALIZER_PREFLIGHT_READY_FOR_REPAIRED_QUEUE_NUMERIC_WAVE_NO_SEARCH_AUTH`

A7FF-24R3 samples repaired dense funding tail rows from A7FF-24R2 and runs the existing numeric probe adapter. It validates materialization/activity/label-control plumbing only. It does not execute formula search, alpha proof, shadow, paper, or live.

## Manifest

```json
{
  "activity_ok_count": 78,
  "authorizes_alpha_proof": false,
  "authorizes_full_12_shard_numeric": false,
  "authorizes_repaired_queue_numeric_wave_contract": true,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "control_rows": 32760,
  "decision": "PASS_A7FF24R3_DENSE_MATERIALIZER_PREFLIGHT_READY_FOR_REPAIRED_QUEUE_NUMERIC_WAVE_NO_SEARCH_AUTH",
  "dense_funding_state_rows": 800,
  "dense_tail_activity_ok_count": 78,
  "dense_tail_rows": 800,
  "eval_failure_count": 0,
  "eval_success_count": 100,
  "executes_numeric_probe": true,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-05-30T11:01:42Z",
  "label_response_rows": 1560,
  "non_l7_numeric_clue_rows": 0,
  "numeric_probe_decision": "HOLD_A7FF24R3_NO_NON_L7_NUMERIC_CLUES",
  "process_exit_code": 0,
  "queue_rows": 2400,
  "rank_label_diagnostic_clue_rows": 0,
  "raw_funding_rate_global_rows": 13,
  "raw_funding_rate_tail_rows": 0,
  "sample_policy": {
    "rows_per_tail_shard": 25,
    "tail_shards": [
      "shard_08",
      "shard_09",
      "shard_10",
      "shard_11"
    ]
  },
  "sample_rows": 100,
  "source_a7ff24r2_decision": "PASS_A7FF24R2_REPAIRED_COMPANY_QUEUE_READY_FOR_DENSE_MATERIALIZER_PREFLIGHT_NO_SEARCH_AUTH",
  "stage": "A7FF-24R3",
  "started_at": "2026-05-30T10:54:18Z",
  "timed_out": false,
  "timeout_seconds": 1800,
  "uses_may": false,
  "warnings": [
    "preserved_healthy_queue_still_has_raw_funding_rate_rows"
  ]
}
```

## Dense Materializer Parity Summary

| check                        |   value | pass   |
|:-----------------------------|--------:|:-------|
| process_exit_code            |       0 | True   |
| timed_out                    |   False | True   |
| sample_rows                  |     100 | True   |
| eval_failure_count           |       0 | True   |
| activity_ok_count            |      78 | True   |
| dense_tail_activity_ok_count |      78 | True   |
| missing_field_blocker        |   False | True   |
| response_rows                |    1560 | True   |
| control_rows                 |   32760 | True   |
| tail_raw_funding_rate_rows   |       0 | True   |
| global_raw_funding_rate_rows |      13 | False  |

## Repaired Queue Shard Audit

| company_shard   |   row_count |   raw_funding_rate_rows |   dense_funding_rows |   semantic_pairs |   motifs |
|:----------------|------------:|------------------------:|---------------------:|-----------------:|---------:|
| shard_00        |         200 |                       0 |                    0 |                2 |        5 |
| shard_01        |         200 |                       0 |                    0 |                1 |        3 |
| shard_02        |         200 |                       0 |                    0 |                2 |        4 |
| shard_03        |         200 |                       0 |                    0 |                1 |        3 |
| shard_04        |         200 |                       0 |                    0 |                2 |        4 |
| shard_05        |         200 |                       0 |                    0 |                1 |        4 |
| shard_06        |         200 |                       0 |                    0 |                2 |        6 |
| shard_07        |         200 |                      13 |                    0 |                6 |        7 |
| shard_08        |         200 |                       0 |                  200 |                1 |        2 |
| shard_09        |         200 |                       0 |                  200 |                1 |        2 |
| shard_10        |         200 |                       0 |                  200 |                1 |        2 |
| shard_11        |         200 |                       0 |                  200 |                2 |        4 |

## Dense Tail Materialization Sample

| blueprint_id              | expression                                                                              | semantic_pair                   | motif               | skeleton_key          | eval_success   |   finite_share |   nonzero_share | activity_ok   |    min_value |   max_value |     std_value |   error |
|:--------------------------|:----------------------------------------------------------------------------------------|:--------------------------------|:--------------------|:----------------------|:---------------|---------------:|----------------:|:--------------|-------------:|------------:|--------------:|--------:|
| a7ff24r2_aac74fb684f80584 | Mul(Delta(funding_rate_state_last_ffill_8h,2),Sign(ZScore(Mean(index_close,8))))        | basis_premium_like|funding_like | gated_sign          | skel_523be22f876215ad | True           |       0.825996 |        0.197505 | True          |  -0.018943   |   0.0200424 |   0.000255889 |     nan |
| a7ff24r2_52d678d2d595dfd5 | Mul(Mean(funding_rate_state_last_ffill_8h,4),Sign(ZScore(Mean(mark_close,2))))          | basis_premium_like|funding_like | gated_sign          | skel_cb65bca4d75ac48a | True           |       0.827145 |        0.99428  | True          |  -0.00131852 |   0.0168193 |   0.000444423 |     nan |
| a7ff24r2_466d8b672783d699 | Mul(Mean(funding_rate_state_last_ffill_8h,4),Sign(ZScore(Mean(index_close,1))))         | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0        |        0        | False         | nan          | nan         | nan           |     nan |
| a7ff24r2_6d7b1888b3ccf15b | Mul(Delta(funding_rate_state_last_ffill_8h,1),Sign(ZScore(Mean(index_close,2))))        | basis_premium_like|funding_like | gated_sign          | skel_523be22f876215ad | True           |       0.82772  |        0.100425 | True          |  -0.0178449  |   0.0200424 |   0.000189739 |     nan |
| a7ff24r2_5ce573f6c88214c9 | Mul(Mean(funding_rate_state_last_ffill_8h,2),Sign(ZScore(Mean(index_close,4))))         | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0.827145 |        0.993915 | True          |  -0.00131852 |   0.0183122 |   0.000457358 |     nan |
| a7ff24r2_30d0d789684705ce | Mul(Mean(funding_rate_state_last_ffill_8h,1),Sign(ZScore(Mean(mark_close,4))))          | basis_premium_like|funding_like | gated_sign          | skel_cb65bca4d75ac48a | True           |       0        |        0        | False         | nan          | nan         | nan           |     nan |
| a7ff24r2_63583f31e4efb718 | Mul(Delta(funding_rate_state_last_ffill_8h,1),Sign(ZScore(Mean(mark_close,8))))         | basis_premium_like|funding_like | gated_sign          | skel_0e5392b1f587e401 | True           |       0.825996 |        0.100562 | True          |  -0.0178449  |   0.0200424 |   0.000189934 |     nan |
| a7ff24r2_9bf237009ccb5524 | Mul(Mean(funding_rate_state_last_ffill_8h,2),Sign(ZScore(Mean(mark_close,1))))          | basis_premium_like|funding_like | gated_sign          | skel_cb65bca4d75ac48a | True           |       0        |        0        | False         | nan          | nan         | nan           |     nan |
| a7ff24r2_7d57b5bbad998f9f | Mul(Mean(funding_rate_state_last_ffill_8h,1),Sign(ZScore(Mean(index_close,1))))         | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0        |        0        | False         | nan          | nan         | nan           |     nan |
| a7ff24r2_f5fab881b87b475e | Mul(Mean(funding_rate_state_last_ffill_8h,2),Sign(ZScore(Mean(index_close,2))))         | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0.82772  |        0.993919 | True          |  -0.00131852 |   0.0183122 |   0.000457281 |     nan |
| a7ff24r2_ba67eb6fa5bd0b12 | Mul(Delta(funding_rate_state_last_ffill_8h,4),Sign(ZScore(Mean(mark_close,1))))         | basis_premium_like|funding_like | gated_sign          | skel_0e5392b1f587e401 | True           |       0        |        0        | False         | nan          | nan         | nan           |     nan |
| a7ff24r2_b363cdd654565b03 | Mul(Delta(funding_rate_state_last_ffill_8h,2),Sign(ZScore(Mean(mark_close,2))))         | basis_premium_like|funding_like | gated_sign          | skel_0e5392b1f587e401 | True           |       0.827432 |        0.197307 | True          |  -0.018943   |   0.0200424 |   0.000255671 |     nan |
| a7ff24r2_5a34a8e925c740a0 | Mul(Mean(funding_rate_state_last_ffill_8h,4),Sign(ZScore(Mean(index_close,8))))         | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0.825996 |        0.994272 | True          |  -0.00131852 |   0.0168193 |   0.000444563 |     nan |
| a7ff24r2_b30c0f0c08915785 | Mul(Mean(funding_rate_state_last_ffill_8h,12),Sign(ZScore(Mean(index_close,8))))        | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0.824847 |        0.995552 | True          |  -0.00110226 |   0.0143979 |   0.000407518 |     nan |
| a7ff24r2_c42e024e34c23e6d | Mul(Delta(funding_rate_state_last_ffill_8h,8),Sign(ZScore(Mean(mark_close,12))))        | basis_premium_like|funding_like | gated_sign          | skel_0e5392b1f587e401 | True           |       0.824847 |        0.653317 | True          |  -0.0186295  |   0.02005   |   0.000437667 |     nan |
| a7ff24r2_59e0d7f5b9f241bc | Mul(Mean(funding_rate_state_last_ffill_8h,1),Sign(ZScore(Mean(mark_close,1))))          | basis_premium_like|funding_like | gated_sign          | skel_cb65bca4d75ac48a | True           |       0        |        0        | False         | nan          | nan         | nan           |     nan |
| a7ff24r2_81b318a0ef41f7e0 | Mul(Delta(funding_rate_state_last_ffill_8h,1),Sign(ZScore(Mean(index_close,4))))        | basis_premium_like|funding_like | gated_sign          | skel_523be22f876215ad | True           |       0.827145 |        0.100495 | True          |  -0.0178449  |   0.0200424 |   0.000189805 |     nan |
| a7ff24r2_d8acd911760aed00 | Mul(Delta(funding_rate_state_last_ffill_8h,8),Sign(ZScore(Mean(index_close,12))))       | basis_premium_like|funding_like | gated_sign          | skel_523be22f876215ad | True           |       0.824847 |        0.653317 | True          |  -0.0186295  |   0.02005   |   0.000437667 |     nan |
| a7ff24r2_35e3efc8f14ac3ef | Mul(Mean(funding_rate_state_last_ffill_8h,2),Sign(ZScore(Mean(mark_close,4))))          | basis_premium_like|funding_like | gated_sign          | skel_cb65bca4d75ac48a | True           |       0.827145 |        0.993915 | True          |  -0.00131852 |   0.0183122 |   0.000457358 |     nan |
| a7ff24r2_af4e9a6fdf3559ca | Mul(Mean(funding_rate_state_last_ffill_8h,8),Sign(ZScore(Mean(index_close,4))))         | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0.825996 |        0.994997 | True          |  -0.00126255 |   0.0167992 |   0.000423998 |     nan |
| a7ff24r2_7a8aed5e699be2ec | Mul(Mean(funding_rate_state_last_ffill_8h,1),Sign(ZScore(Mean(index_close,12))))        | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0        |        0        | False         | nan          | nan         | nan           |     nan |
| a7ff24r2_adc43ff463fcf3cd | Mul(Mean(funding_rate_state_last_ffill_8h,12),Sign(ZScore(Mean(index_close,2))))        | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0.824847 |        0.995552 | True          |  -0.00110226 |   0.0143979 |   0.000407518 |     nan |
| a7ff24r2_8f8d7a8f8c4d0638 | Mul(Delta(funding_rate_state_last_ffill_8h,4),Sign(ZScore(Mean(index_close,2))))        | basis_premium_like|funding_like | gated_sign          | skel_523be22f876215ad | True           |       0.826858 |        0.391306 | True          |  -0.0189955  |   0.0200424 |   0.000343159 |     nan |
| a7ff24r2_6749907272ca9d02 | Mul(Mean(funding_rate_state_last_ffill_8h,2),Sign(ZScore(Mean(mark_close,8))))          | basis_premium_like|funding_like | gated_sign          | skel_cb65bca4d75ac48a | True           |       0.825996 |        0.993906 | True          |  -0.00131852 |   0.0183122 |   0.00045751  |     nan |
| a7ff24r2_ad66bc107103e39d | Mul(Mean(funding_rate_state_last_ffill_8h,2),Sign(ZScore(Mean(index_close,1))))         | basis_premium_like|funding_like | gated_sign          | skel_afcf7abb9d226ed6 | True           |       0        |        0        | False         | nan          | nan         | nan           |     nan |
| a7ff24r2_df50800c84fab699 | Mul(Neg(ZScore(Mean(funding_rate_state_last_ffill_8h,2))),Sign(Delta(index_close,12)))  | basis_premium_like|funding_like | mean_reversion_gate | skel_27dd3b339a7ac705 | True           |       0.82456  |        0.999837 | True          |  -9.68103    |   9.68445   |   0.994639    |     nan |
| a7ff24r2_fee0953712edb34a | Mul(Neg(ZScore(Mean(funding_rate_state_last_ffill_8h,4))),Sign(Mean(index_close,8)))    | basis_premium_like|funding_like | mean_reversion_gate | skel_61e38895d3ebdb34 | True           |       0.825996 |        1        | True          |  -7.41092    |   9.68445   |   0.994773    |     nan |
| a7ff24r2_50d41a811a1ac207 | Mul(Neg(ZScore(Delta(funding_rate_state_last_ffill_8h,2))),Sign(Delta(index_close,4)))  | basis_premium_like|funding_like | mean_reversion_gate | skel_321727627a648531 | True           |       0.549842 |        0.999603 | True          |  -9.6959     |   9.6959    |   0.994701    |     nan |
| a7ff24r2_551a3215dd03a78d | Mul(Neg(ZScore(Delta(funding_rate_state_last_ffill_8h,1))),Sign(Delta(index_close,12))) | basis_premium_like|funding_like | mean_reversion_gate | skel_321727627a648531 | True           |       0.408503 |        0.999832 | True          |  -9.6959     |   9.6959    |   0.994702    |     nan |
| a7ff24r2_d38cd97a2e3e142a | Mul(Neg(ZScore(Mean(funding_rate_state_last_ffill_8h,1))),Sign(Mean(index_close,12)))   | basis_premium_like|funding_like | mean_reversion_gate | skel_61e38895d3ebdb34 | True           |       0        |        0        | False         | nan          | nan         | nan           |     nan |
| a7ff24r2_0c6f03b82f20d4a0 | Mul(Neg(ZScore(Delta(funding_rate_state_last_ffill_8h,2))),Sign(Mean(index_close,2)))   | basis_premium_like|funding_like | mean_reversion_gate | skel_c4cc431ec74593ce | True           |       0.549842 |        1        | True          |  -9.6959     |   9.6959    |   0.994778    |     nan |
| a7ff24r2_85ae81c4843f36cb | Mul(Neg(ZScore(Delta(funding_rate_state_last_ffill_8h,1))),Sign(Delta(index_close,4)))  | basis_premium_like|funding_like | mean_reversion_gate | skel_321727627a648531 | True           |       0.409078 |        0.999576 | True          |  -9.6959     |   9.6959    |   0.994031    |     nan |
| a7ff24r2_fbf6c74a10d6855f | Mul(Neg(ZScore(Mean(funding_rate_state_last_ffill_8h,4))),Sign(Delta(index_close,1)))   | basis_premium_like|funding_like | mean_reversion_gate | skel_27dd3b339a7ac705 | True           |       0.827145 |        0.999244 | True          |  -9.68137    |   9.68445   |   0.994646    |     nan |
| a7ff24r2_0103d38556b8ee94 | Mul(Neg(ZScore(Mean(funding_rate_state_last_ffill_8h,2))),Sign(Mean(index_close,12)))   | basis_premium_like|funding_like | mean_reversion_gate | skel_61e38895d3ebdb34 | True           |       0.824847 |        1        | True          |  -7.41092    |   9.68445   |   0.994773    |     nan |
| a7ff24r2_deb7bf788a456338 | Mul(Neg(ZScore(Delta(funding_rate_state_last_ffill_8h,2))),Sign(Delta(index_close,8)))  | basis_premium_like|funding_like | mean_reversion_gate | skel_321727627a648531 | True           |       0.549267 |        0.9997   | True          |  -9.6959     |   9.6959    |   0.994297    |     nan |
| a7ff24r2_1a57982d0da19e58 | Mul(Neg(ZScore(Mean(funding_rate_state_last_ffill_8h,2))),Sign(Mean(index_close,2)))    | basis_premium_like|funding_like | mean_reversion_gate | skel_61e38895d3ebdb34 | True           |       0.82772  |        1        | True          |  -7.41092    |   9.68445   |   0.994773    |     nan |
| a7ff24r2_a7fd45e531c1de6c | Mul(Neg(ZScore(Delta(funding_rate_state_last_ffill_8h,4))),Sign(Delta(index_close,2)))  | basis_premium_like|funding_like | mean_reversion_gate | skel_321727627a648531 | True           |       0.826199 |        0.999486 | True          |  -9.69351    |   9.6959    |   0.994641    |     nan |
| a7ff24r2_561e8d6743d106fc | Mul(Neg(ZScore(Delta(funding_rate_state_last_ffill_8h,4))),Sign(Mean(index_close,2)))   | basis_premium_like|funding_like | mean_reversion_gate | skel_c4cc431ec74593ce | True           |       0.826199 |        1        | True          |  -9.6959     |   9.6952    |   0.994778    |     nan |
| a7ff24r2_05c828f583507e57 | Mul(Neg(ZScore(Delta(funding_rate_state_last_ffill_8h,1))),Sign(Mean(index_close,2)))   | basis_premium_like|funding_like | mean_reversion_gate | skel_c4cc431ec74593ce | True           |       0.409078 |        1        | True          |  -9.6959     |   9.6959    |   0.994778    |     nan |
| a7ff24r2_0a5b988ea25dc18b | Mul(Neg(ZScore(Mean(funding_rate_state_last_ffill_8h,4))),Sign(Mean(index_close,2)))    | basis_premium_like|funding_like | mean_reversion_gate | skel_61e38895d3ebdb34 | True           |       0.827145 |        1        | True          |  -7.41092    |   9.68445   |   0.994773    |     nan |

## Boundary

```text
numeric probe executed: true, bounded dense-tail sample only
replay executed: false
search executed: false
May used: false
full 12-shard numeric execution authorized: false
next if PASS: repaired-queue numeric wave contract / A7FF-32 family diversification contract
```
