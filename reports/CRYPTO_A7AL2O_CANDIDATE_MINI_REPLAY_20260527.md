# CRYPTO A7AL-2O Candidate Mini Replay / Neutralization Audit

Generated: 2026-05-27T14:03:18Z

## Decision

```text
PASS_A7AL2O_MINI_REPLAY_CANDIDATES_READY_FOR_CONTRACT
```

This is a small audit on the four A7AL-2N diagnostic candidates. It tests field-native one-bar lag, group neutralization, exclusion variants, BTC/ETH beta residual alpha, negative-control margin, and turnover/cost proxies. It does not authorize alpha proof, formula-search execution, shadow, paper, or live.

## Manifest

```json
{
  "authorizes_a7al2p_contract": true,
  "authorizes_alpha_proof": false,
  "authorizes_formula_search_execution": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "candidate_count": 4,
  "cost_proxy_bps": [
    2.0,
    5.0,
    10.0
  ],
  "decision": "PASS_A7AL2O_MINI_REPLAY_CANDIDATES_READY_FOR_CONTRACT",
  "decision_cost_proxy_bps": 2.0,
  "decision_counts": {
    "A7AL2O_MINI_REPLAY_DIAGNOSTIC_PASS": 4
  },
  "diagnostic_pass_count": 4,
  "eval_errors": 0,
  "executes_alpha_proof": false,
  "executes_formula_generation": false,
  "executes_mini_replay": true,
  "generated_at": "2026-05-27T14:03:18Z",
  "input": "G:\\Project_V7_Rotation\\alpha_pit_engine_crypto_20260519\\runtime\\a7al2n_derived_deep_audit\\a7al2n_deep_candidate_summary.csv",
  "latency_policy": "field_native_one_bar_lag_no_blanket_plus2h",
  "latent_state_neutralization_note": "dominant_latent_state is a symbol-level proxy because time-varying latent-state panel is not materialized in this audit",
  "may_usage": "stress_reporting_only_not_used_for_selection_or_orientation",
  "neutralization_variants": [
    "neutral_liquidity_tier",
    "neutral_meme_contract_group",
    "neutral_multiplier_flag",
    "neutral_major_flag",
    "neutral_dominant_latent_state",
    "exclude_meme",
    "exclude_multiplier",
    "exclude_major"
  ]
}
```

## Decision Counts

| mini_replay_label                  |   count |
|:-----------------------------------|--------:|
| A7AL2O_MINI_REPLAY_DIAGNOSTIC_PASS |       4 |

## Candidate Decisions

| candidate_id            | cell                        | family                      | field_families   | mini_replay_label                  | reasons   | warnings                                                                      | pass_variants                                                                                                                                                                                           | net_2bps_pass_variants                                                                                                                                                                                  |   neutralized_pass_variant_count |   recent_original_turnover |   recent_beta_residual_alpha |   control_dominance_ratio_premay_max |
|:------------------------|:----------------------------|:----------------------------|:-----------------|:-----------------------------------|:----------|:------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------:|---------------------------:|-----------------------------:|-------------------------------------:|
| a7al2k_01759e5da72c472c | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis\|liquidity | A7AL2O_MINI_REPLAY_DIAGNOSTIC_PASS |           |                                                                               | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|neutral_dominant_latent_state\|exclude_meme\|exclude_multiplier\|exclude_major | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|neutral_dominant_latent_state\|exclude_meme\|exclude_multiplier\|exclude_major |                                8 |                 0.023054   |                   0.00210888 |                             0.946342 |
| a7al2k_0cf817ef95787b3d | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis\|liquidity | A7AL2O_MINI_REPLAY_DIAGNOSTIC_PASS |           |                                                                               | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|neutral_dominant_latent_state\|exclude_meme\|exclude_multiplier\|exclude_major | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|neutral_dominant_latent_state\|exclude_meme\|exclude_multiplier\|exclude_major |                                8 |                 0.0705655  |                   0.00406726 |                             1.04108  |
| a7al2k_134ec76b5d7444f9 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity\|price | A7AL2O_MINI_REPLAY_DIAGNOSTIC_PASS |           | a7al2n:train_oriented_spread_nonpositive                                      | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|neutral_dominant_latent_state\|exclude_meme\|exclude_multiplier\|exclude_major | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|neutral_dominant_latent_state\|exclude_meme\|exclude_multiplier\|exclude_major |                                8 |                 0.0445415  |                   0.00222801 |                             1.06869  |
| a7al2k_01298a6b5902f416 | J0_oi_derived_state         | derived_oi_price_state      | open_interest    | A7AL2O_MINI_REPLAY_DIAGNOSTIC_PASS |           | dominant_latent_state_proxy_fragile\|a7al2n:train_oriented_spread_nonpositive | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|exclude_meme\|exclude_multiplier\|exclude_major                                | original\|one_bar_lag\|neutral_liquidity_tier\|neutral_meme_contract_group\|neutral_multiplier_flag\|neutral_major_flag\|exclude_meme\|exclude_multiplier\|exclude_major                                |                                7 |                 0.00866136 |                   0.00157963 |                             0.932378 |

## Selected Variant Split Metrics

| candidate_id            | variant                       | split                 |   mean_spread_24h |   net_mean_spread_2bps |   avg_one_way_turnover |   positive_spread_rate |
|:------------------------|:------------------------------|:----------------------|------------------:|-----------------------:|-----------------------:|-----------------------:|
| a7al2k_01759e5da72c472c | original                      | validation_2025H1     |       0.00123838  |            0.00123119  |             0.0359405  |               0.534722 |
| a7al2k_01759e5da72c472c | original                      | test_2025H2           |       0.00303946  |            0.00303319  |             0.0313535  |               0.569217 |
| a7al2k_01759e5da72c472c | original                      | recent_oos_2026JanApr |       0.00195588  |            0.00195127  |             0.023054   |               0.54902  |
| a7al2k_01759e5da72c472c | original                      | known_may2026_stress  |       0.00338678  |            0.00337998  |             0.0339912  |               0.546875 |
| a7al2k_01759e5da72c472c | one_bar_lag                   | validation_2025H1     |       0.00122295  |            0.00121577  |             0.0359284  |               0.53287  |
| a7al2k_01759e5da72c472c | one_bar_lag                   | test_2025H2           |       0.0030201   |            0.00301382  |             0.0313655  |               0.567623 |
| a7al2k_01759e5da72c472c | one_bar_lag                   | recent_oos_2026JanApr |       0.00191405  |            0.00190944  |             0.023054   |               0.54902  |
| a7al2k_01759e5da72c472c | one_bar_lag                   | known_may2026_stress  |       0.003354    |            0.00334718  |             0.0340826  |               0.539931 |
| a7al2k_01759e5da72c472c | neutral_liquidity_tier        | validation_2025H1     |       0.001119    |            0.00111429  |             0.0235502  |               0.508333 |
| a7al2k_01759e5da72c472c | neutral_liquidity_tier        | test_2025H2           |       0.00197471  |            0.00197138  |             0.0166371  |               0.551457 |
| a7al2k_01759e5da72c472c | neutral_liquidity_tier        | recent_oos_2026JanApr |       0.00180179  |            0.00179827  |             0.0175991  |               0.542017 |
| a7al2k_01759e5da72c472c | neutral_liquidity_tier        | known_may2026_stress  |       0.00101037  |            0.00100558  |             0.0239401  |               0.494792 |
| a7al2k_01759e5da72c472c | neutral_dominant_latent_state | validation_2025H1     |       0.000665589 |            0.000659901 |             0.0284433  |               0.509028 |
| a7al2k_01759e5da72c472c | neutral_dominant_latent_state | test_2025H2           |       0.00507567  |            0.00507031  |             0.0268101  |               0.607696 |
| a7al2k_01759e5da72c472c | neutral_dominant_latent_state | recent_oos_2026JanApr |       0.000536604 |            0.000533181 |             0.0171131  |               0.526961 |
| a7al2k_01759e5da72c472c | neutral_dominant_latent_state | known_may2026_stress  |      -0.000578873 |           -0.000584255 |             0.0269097  |               0.515625 |
| a7al2k_0cf817ef95787b3d | original                      | validation_2025H1     |       0.0020818   |            0.00206002  |             0.10893    |               0.561574 |
| a7al2k_0cf817ef95787b3d | original                      | test_2025H2           |       0.00449646  |            0.00447997  |             0.0824772  |               0.632286 |
| a7al2k_0cf817ef95787b3d | original                      | recent_oos_2026JanApr |       0.00379066  |            0.00377655  |             0.0705655  |               0.595238 |
| a7al2k_0cf817ef95787b3d | original                      | known_may2026_stress  |       0.00648685  |            0.00646953  |             0.0866228  |               0.715278 |
| a7al2k_0cf817ef95787b3d | one_bar_lag                   | validation_2025H1     |       0.00210293  |            0.00208115  |             0.108918   |               0.564352 |
| a7al2k_0cf817ef95787b3d | one_bar_lag                   | test_2025H2           |       0.00445164  |            0.00443515  |             0.0824772  |               0.632058 |
| a7al2k_0cf817ef95787b3d | one_bar_lag                   | recent_oos_2026JanApr |       0.00367299  |            0.00365888  |             0.0705471  |               0.596989 |
| a7al2k_0cf817ef95787b3d | one_bar_lag                   | known_may2026_stress  |       0.00633682  |            0.0063195   |             0.0866228  |               0.710069 |
| a7al2k_0cf817ef95787b3d | neutral_liquidity_tier        | validation_2025H1     |       0.000762371 |            0.00074676  |             0.078058   |               0.521065 |
| a7al2k_0cf817ef95787b3d | neutral_liquidity_tier        | test_2025H2           |       0.00245593  |            0.00244586  |             0.0503174  |               0.599044 |
| a7al2k_0cf817ef95787b3d | neutral_liquidity_tier        | recent_oos_2026JanApr |       0.00248032  |            0.0024704   |             0.0496318  |               0.576681 |
| a7al2k_0cf817ef95787b3d | neutral_liquidity_tier        | known_may2026_stress  |       0.00541435  |            0.005402    |             0.061769   |               0.668403 |
| a7al2k_0cf817ef95787b3d | neutral_dominant_latent_state | validation_2025H1     |       0.00258678  |            0.00256898  |             0.0890046  |               0.580324 |
| a7al2k_0cf817ef95787b3d | neutral_dominant_latent_state | test_2025H2           |       0.00551782  |            0.00550381  |             0.0700421  |               0.632286 |
| a7al2k_0cf817ef95787b3d | neutral_dominant_latent_state | recent_oos_2026JanApr |       0.00272429  |            0.00271371  |             0.0529149  |               0.60049  |
| a7al2k_0cf817ef95787b3d | neutral_dominant_latent_state | known_may2026_stress  |       0.00835345  |            0.00833961  |             0.0692274  |               0.71875  |
| a7al2k_134ec76b5d7444f9 | original                      | validation_2025H1     |       0.00214053  |            0.00213062  |             0.0495648  |               0.538194 |
| a7al2k_134ec76b5d7444f9 | original                      | test_2025H2           |       0.00418491  |            0.00417643  |             0.0424216  |               0.615437 |
| a7al2k_134ec76b5d7444f9 | original                      | recent_oos_2026JanApr |       0.00218342  |            0.00217451  |             0.0445415  |               0.570378 |
| a7al2k_134ec76b5d7444f9 | original                      | known_may2026_stress  |       0.00385336  |            0.00384245  |             0.0545504  |               0.734375 |
| a7al2k_134ec76b5d7444f9 | one_bar_lag                   | validation_2025H1     |       0.00214771  |            0.0021378   |             0.0495892  |               0.538194 |
| a7al2k_134ec76b5d7444f9 | one_bar_lag                   | test_2025H2           |       0.00418378  |            0.00417529  |             0.0424336  |               0.616576 |
| a7al2k_134ec76b5d7444f9 | one_bar_lag                   | recent_oos_2026JanApr |       0.00209957  |            0.00209065  |             0.0445784  |               0.564776 |
| a7al2k_134ec76b5d7444f9 | one_bar_lag                   | known_may2026_stress  |       0.00382696  |            0.0038161   |             0.0542763  |               0.725694 |
| a7al2k_134ec76b5d7444f9 | neutral_liquidity_tier        | validation_2025H1     |       0.00236148  |            0.00233765  |             0.11916    |               0.56088  |
| a7al2k_134ec76b5d7444f9 | neutral_liquidity_tier        | test_2025H2           |       0.00366611  |            0.00364515  |             0.104808   |               0.623406 |
| a7al2k_134ec76b5d7444f9 | neutral_liquidity_tier        | recent_oos_2026JanApr |       0.00128297  |            0.00126284  |             0.100656   |               0.55007  |
| a7al2k_134ec76b5d7444f9 | neutral_liquidity_tier        | known_may2026_stress  |       0.00451002  |            0.0044878   |             0.111111   |               0.706597 |
| a7al2k_134ec76b5d7444f9 | neutral_dominant_latent_state | validation_2025H1     |       0.00193869  |            0.00190642  |             0.161343   |               0.577778 |
| a7al2k_134ec76b5d7444f9 | neutral_dominant_latent_state | test_2025H2           |       0.00492861  |            0.00490357  |             0.125228   |               0.623634 |
| a7al2k_134ec76b5d7444f9 | neutral_dominant_latent_state | recent_oos_2026JanApr |       0.0013616   |            0.00133709  |             0.122549   |               0.540966 |
| a7al2k_134ec76b5d7444f9 | neutral_dominant_latent_state | known_may2026_stress  |       0.00482731  |            0.00480227  |             0.125217   |               0.621528 |
| a7al2k_01298a6b5902f416 | original                      | validation_2025H1     |       0.000830232 |            0.000828695 |             0.00768762 |               0.530787 |
| a7al2k_01298a6b5902f416 | original                      | test_2025H2           |       0.00174322  |            0.00174147  |             0.00871201 |               0.5699   |
| a7al2k_01298a6b5902f416 | original                      | recent_oos_2026JanApr |       0.00159322  |            0.00159149  |             0.00866136 |               0.532563 |
| a7al2k_01298a6b5902f416 | original                      | known_may2026_stress  |       0.00171216  |            0.0017103   |             0.00932018 |               0.605903 |
| a7al2k_01298a6b5902f416 | one_bar_lag                   | validation_2025H1     |       0.000826828 |            0.00082529  |             0.00768762 |               0.531481 |
| a7al2k_01298a6b5902f416 | one_bar_lag                   | test_2025H2           |       0.00175369  |            0.00175194  |             0.00871201 |               0.570355 |
| a7al2k_01298a6b5902f416 | one_bar_lag                   | recent_oos_2026JanApr |       0.00157885  |            0.00157712  |             0.00866136 |               0.532213 |
| a7al2k_01298a6b5902f416 | one_bar_lag                   | known_may2026_stress  |       0.00174609  |            0.00174423  |             0.00932018 |               0.611111 |
| a7al2k_01298a6b5902f416 | neutral_liquidity_tier        | validation_2025H1     |       0.000383541 |            0.000381465 |             0.0103801  |               0.498611 |
| a7al2k_01298a6b5902f416 | neutral_liquidity_tier        | test_2025H2           |       0.00188958  |            0.0018872   |             0.0118996  |               0.602687 |
| a7al2k_01298a6b5902f416 | neutral_liquidity_tier        | recent_oos_2026JanApr |       0.000869593 |            0.000867187 |             0.0120338  |               0.556373 |
| a7al2k_01298a6b5902f416 | neutral_liquidity_tier        | known_may2026_stress  |      -0.000413904 |           -0.000416335 |             0.0121528  |               0.432292 |
| a7al2k_01298a6b5902f416 | neutral_dominant_latent_state | validation_2025H1     |       0.000480576 |            0.00047844  |             0.0106771  |               0.509722 |
| a7al2k_01298a6b5902f416 | neutral_dominant_latent_state | test_2025H2           |       0.000751615 |            0.00074968  |             0.00967668 |               0.529599 |
| a7al2k_01298a6b5902f416 | neutral_dominant_latent_state | recent_oos_2026JanApr |      -0.00246879  |           -0.00247074  |             0.00976015 |               0.480042 |
| a7al2k_01298a6b5902f416 | neutral_dominant_latent_state | known_may2026_stress  |       0.00199054  |            0.00198867  |             0.0093316  |               0.590278 |

## Boundary

```text
Allowed next step if mini replay passes:
  A7AL-2P small formula-search contract / candidate pool definition.

Not authorized:
  formula search execution
  alpha proof
  shadow / paper / live
```
