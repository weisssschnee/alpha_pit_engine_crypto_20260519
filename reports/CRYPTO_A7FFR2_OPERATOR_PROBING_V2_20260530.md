# CRYPTO A7FF-R2 OPERATOR PROBING V2

Generated: 2026-05-30T05:51:45Z

## Decision

`PASS_A7FFR2_OPERATOR_PROBING_V2_READY`

## Manifest

```json
{
  "authorizes_a7ffr3": true,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "decision": "PASS_A7FFR2_OPERATOR_PROBING_V2_READY",
  "executes_generation": false,
  "executes_search": false,
  "generated_at": "2026-05-30T05:51:45Z",
  "policy_rows": 42,
  "probe_required_rows": 39,
  "promote_operator_rows": 0,
  "stage": "A7FF-R2-OPERATOR-PROBING-V2"
}
```

## Operator Policy

| semantic_type_v3   | operator                |   tests |   candidate_rows |   non_l7_candidate_rows |   median_control_ratio | operator_policy_v2   |
|:-------------------|:------------------------|--------:|-----------------:|------------------------:|-----------------------:|:---------------------|
| basis_premium_like | Delta                   |      45 |                3 |                       2 |                9.47406 | diagnostic_only      |
| basis_premium_like | ZScore                  |       0 |                0 |                       0 |              nan       | probe_required       |
| basis_premium_like | CSRank                  |      45 |                0 |                       0 |                2.76686 | probe_required       |
| basis_premium_like | HorizonSpread           |       0 |                0 |                       0 |              nan       | probe_required       |
| basis_premium_like | SafeDiv                 |       0 |                0 |                       0 |              nan       | probe_required       |
| basis_premium_like | Clip                    |       0 |                0 |                       0 |              nan       | probe_required       |
| basis_premium_like | Shock                   |       0 |                0 |                       0 |              nan       | probe_required       |
| funding_like       | Delta                   |      27 |                0 |                       0 |                4.60207 | probe_required       |
| funding_like       | ZScore                  |       0 |                0 |                       0 |              nan       | probe_required       |
| funding_like       | Abs                     |       0 |                0 |                       0 |              nan       | probe_required       |
| funding_like       | Sign                    |       0 |                0 |                       0 |              nan       | probe_required       |
| funding_like       | Persistence             |       0 |                0 |                       0 |              nan       | probe_required       |
| funding_like       | CSRank                  |      27 |                0 |                       0 |                3.11786 | probe_required       |
| generic_numeric    | Delta                   |       0 |                0 |                       0 |              nan       | probe_required       |
| generic_numeric    | ZScore                  |       0 |                0 |                       0 |              nan       | probe_required       |
| generic_numeric    | CSRank                  |       0 |                0 |                       0 |              nan       | probe_required       |
| liquidity_like     | Delta                   |      27 |                0 |                       0 |               12.6964  | probe_required       |
| liquidity_like     | ZScore                  |       0 |                0 |                       0 |              nan       | probe_required       |
| liquidity_like     | Shock                   |       0 |                0 |                       0 |              nan       | probe_required       |
| liquidity_like     | Persistence             |       0 |                0 |                       0 |              nan       | probe_required       |
| liquidity_like     | CSRank                  |      27 |                0 |                       0 |                5.42153 | probe_required       |
| liquidity_like     | WithinLiquidityTierRank |       0 |                0 |                       0 |              nan       | probe_required       |
| positioning_like   | Delta                   |      72 |                0 |                       0 |               15.9212  | probe_required       |
| positioning_like   | ZScore                  |       0 |                0 |                       0 |              nan       | probe_required       |
| positioning_like   | Persistence             |       0 |                0 |                       0 |              nan       | probe_required       |
| positioning_like   | Shock                   |       0 |                0 |                       0 |              nan       | probe_required       |
| positioning_like   | CSRank                  |      72 |                0 |                       0 |                6.78564 | probe_required       |
| positioning_like   | HorizonSpread           |       0 |                0 |                       0 |              nan       | probe_required       |
| price_like         | Delta                   |      18 |                0 |                       0 |               14.186   | probe_required       |
| price_like         | ZScore                  |       0 |                0 |                       0 |              nan       | probe_required       |
| price_like         | TSRank                  |       0 |                0 |                       0 |              nan       | probe_required       |
| price_like         | CSRank                  |      18 |                2 |                       0 |               12.1836  | diagnostic_only      |
| price_like         | HorizonSpread           |       0 |                0 |                       0 |              nan       | probe_required       |
| state_or_taxonomy  | WithinGroupRank         |       0 |                0 |                       0 |              nan       | probe_required       |
| state_or_taxonomy  | RegimeMask              |       0 |                0 |                       0 |              nan       | probe_required       |
| state_or_taxonomy  | Neutralize              |       0 |                0 |                       0 |              nan       | probe_required       |
| state_or_taxonomy  | InteractionOnly         |       0 |                0 |                       0 |              nan       | probe_required       |
| volatility_like    | Delta                   |      18 |                0 |                       0 |               23.9557  | probe_required       |
| volatility_like    | ZScore                  |       0 |                0 |                       0 |              nan       | probe_required       |
| volatility_like    | Shock                   |       0 |                0 |                       0 |              nan       | probe_required       |
| volatility_like    | CSRank                  |      18 |                2 |                       0 |                6.67139 | diagnostic_only      |
| volatility_like    | HorizonSpread           |       0 |                0 |                       0 |              nan       | probe_required       |

## Observed Operator Response

| semantic_type_v3   | operator   |   tests |   candidate_rows |   non_l7_candidate_rows |   median_control_ratio |   min_control_ratio |
|:-------------------|:-----------|--------:|-----------------:|------------------------:|-----------------------:|--------------------:|
| basis_premium_like | CSRank     |      45 |                0 |                       0 |                2.76686 |            0.115016 |
| basis_premium_like | Delta      |      45 |                3 |                       2 |                9.47406 |            0.785786 |
| basis_premium_like | Identity   |      45 |                0 |                       0 |                2.76686 |            0.107775 |
| funding_like       | CSRank     |      27 |                0 |                       0 |                3.11786 |            0.607009 |
| funding_like       | Delta      |      27 |                0 |                       0 |                4.60207 |            0.878273 |
| funding_like       | Identity   |      27 |                0 |                       0 |                3.11786 |            0.607009 |
| liquidity_like     | CSRank     |      27 |                0 |                       0 |                5.42153 |            2.14076  |
| liquidity_like     | Delta      |      27 |                0 |                       0 |               12.6964  |            5.19194  |
| liquidity_like     | Identity   |      27 |                0 |                       0 |                5.5163  |            2.14076  |
| positioning_like   | CSRank     |      72 |                0 |                       0 |                6.78564 |            0.688118 |
| positioning_like   | Delta      |      72 |                0 |                       0 |               15.9212  |            2.22682  |
| positioning_like   | Identity   |      72 |                0 |                       0 |                6.78564 |            1.11232  |
| price_like         | CSRank     |      18 |                2 |                       0 |               12.1836  |            0.254317 |
| price_like         | Delta      |      18 |                0 |                       0 |               14.186   |            1.0876   |
| price_like         | Identity   |      18 |                2 |                       0 |               12.1836  |            0.254317 |
| state_or_taxonomy  | CSRank     |       9 |                0 |                       0 |                5.85194 |            0.997123 |
| state_or_taxonomy  | Delta      |       9 |                0 |                       0 |               18.6896  |            2.28492  |
| state_or_taxonomy  | Identity   |       9 |                0 |                       0 |                3.69828 |            0.997123 |
| volatility_like    | CSRank     |      18 |                2 |                       0 |                6.67139 |            0.879498 |
| volatility_like    | Delta      |      18 |                0 |                       0 |               23.9557  |            4.83029  |
| volatility_like    | Identity   |      18 |                2 |                       0 |                6.67139 |            0.879498 |
