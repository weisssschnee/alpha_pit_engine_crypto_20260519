# CRYPTO A7AL-2L Fast Derived Replay Preflight

Generated: 2026-05-28T07:12:23Z

## Decision

```text
PASS_A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD
```

This is a matrix-level replay preflight on A7AL-2K derived-tolerant generated candidates. It does not authorize alpha proof, large search, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_eval_errors": 0,
  "controls": [
    "one_bar_lag",
    "wrong_lag_future_24h",
    "wrong_lag_stale_168h",
    "time_shuffle",
    "symbol_shuffle",
    "same_family_random"
  ],
  "decision": "PASS_A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUES_FOUND_EXECUTION_HOLD",
  "decision_counts": {
    "A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE": 2
  },
  "derived_replay_preflight_clue_count": 2,
  "engine": "matrix_fast_preflight",
  "executes_alpha_proof": false,
  "executes_formula_generation": false,
  "executes_replay_preflight": true,
  "generated_at": "2026-05-28T07:12:23Z",
  "input_base": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v2_20260527",
  "matrix_rows": 3805525,
  "max_symbols_env": 0,
  "replay_cap": 2,
  "runtime_seconds": 111.114,
  "selected_from_a7al2k": 2,
  "strict_symbols": 181,
  "target_ids": [
    "a7al2k_046e806368e99c76",
    "a7al2k_0a247ec03472983b"
  ],
  "target_replay_mode": true,
  "timestamps": 21025,
  "warnings": []
}
```

## Decision Counts

| decision                             |   count |
|:-------------------------------------|--------:|
| A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE |       2 |

## Candidate Decisions

| candidate_id            | cell                | family                 | field_families      | decision                             |   original_validation_spread |   original_test_spread |   original_recent_spread |   original_may_stress_spread |   one_bar_lag_recent_spread |   control_dominance_ratio_premay_max |
|:------------------------|:--------------------|:-----------------------|:--------------------|:-------------------------------------|-----------------------------:|-----------------------:|-------------------------:|-----------------------------:|----------------------------:|-------------------------------------:|
| a7al2k_046e806368e99c76 | J0_oi_derived_state | derived_oi_price_state | open_interest|price | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE |                   0.00128866 |             0.00191171 |               0.00186543 |                  -0.00164923 |                  0.0018384  |                              0.79335 |
| a7al2k_0a247ec03472983b | J0_oi_derived_state | derived_oi_price_state | open_interest|price | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE |                   0.00122938 |             0.00159185 |               0.00188517 |                  -0.00166771 |                  0.00186493 |                              0.88085 |

## Boundary

```text
Allowed interpretation:
  A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE means a derived structure deserves controlled follow-up.

Not authorized:
  alpha proof
  shadow / paper / live
  large formula search
```
