# Crypto A7R-0 Horizon Reframing Contract

- generated_at: `2026-05-21T00:44:09Z`
- decision: `PASS_A7R0_HORIZON_REFRAMING_CONTRACT`
- executes_search: `False`
- executes_replay: `False`
- authorizes: `A7R-1 small audit only`
- alpha proof / shadow / paper / live: `NOT_AUTHORIZED`

## Horizons

| horizon_id    | target_horizon_hours   | status                         | notes                                                       |
|:--------------|:-----------------------|:-------------------------------|:------------------------------------------------------------|
| H4            | 4                      | authorized_for_A7R1_diagnostic | No formula search; existing candidates only.                |
| H8            | 8                      | authorized_for_A7R1_diagnostic | No formula search; existing candidates only.                |
| H12           | 12                     | authorized_for_A7R1_diagnostic | No formula search; existing candidates only.                |
| H24           | 24                     | authorized_for_A7R1_diagnostic | No formula search; existing candidates only.                |
| H48           | 48                     | authorized_for_A7R1_diagnostic | No formula search; existing candidates only.                |
| H72           | 72                     | authorized_for_A7R1_diagnostic | No formula search; existing candidates only.                |
| H96           | 96                     | authorized_for_A7R1_diagnostic | No formula search; existing candidates only.                |
| mixed_H12_H48 | contract_only          | not_executed_in_A7R1           | Reserved for future contract; not used in this cheap audit. |
| mixed_H24_H96 | contract_only          | not_executed_in_A7R1           | Reserved for future contract; not used in this cheap audit. |

## Execution Lag Contract

|   execution_lag_bars | status                         | notes                                                                                   |
|---------------------:|:-------------------------------|:----------------------------------------------------------------------------------------|
|                    0 | authorized_for_A7R1_diagnostic | Lag is applied by shifting the signal forward by lag bars before position construction. |
|                    1 | authorized_for_A7R1_diagnostic | Lag is applied by shifting the signal forward by lag bars before position construction. |
|                    2 | authorized_for_A7R1_diagnostic | Lag is applied by shifting the signal forward by lag bars before position construction. |
|                    3 | authorized_for_A7R1_diagnostic | Lag is applied by shifting the signal forward by lag bars before position construction. |

## Cost Contract

|   cost_bps | status                         | notes                                            |
|-----------:|:-------------------------------|:-------------------------------------------------|
|         10 | authorized_for_A7R1_diagnostic | Fee drag applied through scaled array evaluator. |
|         20 | authorized_for_A7R1_diagnostic | Fee drag applied through scaled array evaluator. |
|         30 | authorized_for_A7R1_diagnostic | Fee drag applied through scaled array evaluator. |

## Boundary

A7R-1 may only reuse existing A7P-3 deep candidates or a <=64-cell audit. May remains stress-only and cannot enter ranking, threshold tuning, horizon selection, reward, generation, mutation, or surrogate targets.