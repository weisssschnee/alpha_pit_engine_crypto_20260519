# CRYPTO A7AL-2L Fast Derived Replay Preflight

Generated: 2026-05-28T02:32:25Z

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
    "A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE": 3,
    "HOLD_A7AL2L_CONTROL_DOMINATED": 22,
    "HOLD_A7AL2L_ONE_BAR_LAG_FRAGILE": 2,
    "HOLD_A7AL2L_UNSTABLE_PRE_MAY": 37
  },
  "derived_replay_preflight_clue_count": 3,
  "engine": "matrix_fast_preflight",
  "executes_alpha_proof": false,
  "executes_formula_generation": false,
  "executes_replay_preflight": true,
  "generated_at": "2026-05-28T02:32:25Z",
  "input_base": "G:\\AlphaFactory_CryptoData\\gold\\features\\binance_universe498_replay_1h_v2_20260527",
  "matrix_rows": 3805525,
  "max_symbols_env": 0,
  "replay_cap": 64,
  "runtime_seconds": 2800.023,
  "selected_from_a7al2k": 64,
  "strict_symbols": 181,
  "timestamps": 21025,
  "warnings": [
    "control_dominated_candidates_rejected"
  ]
}
```

## Decision Counts

| decision                             |   count |
|:-------------------------------------|--------:|
| HOLD_A7AL2L_UNSTABLE_PRE_MAY         |      37 |
| HOLD_A7AL2L_CONTROL_DOMINATED        |      22 |
| A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE |       3 |
| HOLD_A7AL2L_ONE_BAR_LAG_FRAGILE      |       2 |

## Candidate Decisions

| candidate_id            | cell                        | family                      | field_families          | decision                             |   original_validation_spread |   original_test_spread |   original_recent_spread |   original_may_stress_spread |   one_bar_lag_recent_spread |   control_dominance_ratio_premay_max |
|:------------------------|:----------------------------|:----------------------------|:------------------------|:-------------------------------------|-----------------------------:|-----------------------:|-------------------------:|-----------------------------:|----------------------------:|-------------------------------------:|
| a7al2k_000b2f43c9a9bc8d | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.00262226  |           -0.00308782  |             -0.000835063 |                 -0.00249127  |                -0.000842423 |                             1.29939  |
| a7al2k_0041e6ed001f2431 | J1_vol_range_structure      | derived_vol_range_state     | price|volatility        | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                  0.000455199 |           -5.39833e-05 |              9.06824e-05 |                  0.00099409  |                 8.38524e-05 |                            15.3465   |
| a7al2k_00870205696c9eab | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.000328989 |           -0.000191352 |             -0.000762448 |                  0.000438196 |                -0.000850749 |                            50.8125   |
| a7al2k_01878e31bc021813 | J3_basis_funding_derived    | derived_basis_funding_state | funding|price           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000542891 |           -0.00222151  |              0.000199276 |                 -0.00712128  |                 0.000213866 |                             8.91511  |
| a7al2k_0504fd431f5d1bef | J4_upper_regime_interaction | derived_upper_regime_proxy  | funding|liquidity       | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.000386908 |           -0.00189416  |             -0.00236837  |                nan           |                -0.00216624  |                             8.36913  |
| a7al2k_005ea931395b1d44 | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.0014061   |           -0.0020365   |             -0.000262125 |                 -0.00251284  |                -0.000248072 |                             2.31686  |
| a7al2k_02e0fd675c16f060 | J1_vol_range_structure      | derived_vol_range_state     | price|volatility        | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.00062561  |            4.25489e-05 |             -5.09556e-05 |                  0.000162605 |                -7.75744e-06 |                            20.2139   |
| a7al2k_0112fb8a50839382 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000764994 |            0.000145492 |             -8.33141e-05 |                 -0.000542928 |                -6.12499e-05 |                           144.875    |
| a7al2k_0221940909117744 | J3_basis_funding_derived    | derived_basis_funding_state | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                  0.000833727 |           -0.00103217  |             -0.00102428  |                  0.00259507  |                -0.000909099 |                             3.33057  |
| a7al2k_0b54d61e939cac19 | J4_upper_regime_interaction | derived_upper_regime_proxy  | funding|liquidity       | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                nan           |          nan           |            nan           |                nan           |               nan           |                           nan        |
| a7al2k_0229cfd8f3eab064 | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.00183517  |           -0.00189559  |             -0.000362557 |                 -0.0023809   |                -0.000351925 |                             2.82458  |
| a7al2k_0468947143e6f5ea | J1_vol_range_structure      | derived_vol_range_state     | price|volatility        | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000218312 |           -0.000341468 |              0.000197927 |                 -3.41619e-05 |                 0.000251359 |                             4.84124  |
| a7al2k_03ae1d0730934813 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.00115746  |            0.000270472 |              5.78262e-05 |                  0.000207551 |                -1.80268e-05 |                           147.665    |
| a7al2k_0376e6fb4b01c15e | J3_basis_funding_derived    | derived_basis_funding_state | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                  2.15367e-05 |           -0.00124538  |             -0.000868796 |                  0.00413131  |                -0.000498205 |                            68.599    |
| a7al2k_010b928604355c8b | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000373059 |            0.000593428 |              0.00113409  |                 -0.00235821  |                 0.00155396  |                             8.81745  |
| a7al2k_00ee9f9173e811d7 | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000991128 |           -0.000147675 |              0.000455203 |                 -0.000974427 |                 0.000455292 |                            81.0304   |
| a7al2k_06ab627029577475 | J1_vol_range_structure      | derived_vol_range_state     | price|volatility        | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                  6.51562e-05 |           -0.000357257 |             -4.84218e-05 |                 -0.000662629 |                -0.000232834 |                            67.7091   |
| a7al2k_05d6c180aad8e803 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -2.93962e-05 |            0.000360383 |              0.000529646 |                 -0.000522943 |                 0.000492112 |                            41.44     |
| a7al2k_020e72ea4dda0dbf | J3_basis_funding_derived    | derived_basis_funding_state | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                nan           |          nan           |            nan           |                nan           |               nan           |                           nan        |
| a7al2k_0204ebfe1394580c | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                nan           |          nan           |            nan           |                nan           |               nan           |                           nan        |
| a7al2k_0293e0ba2eb2cd5d | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.000455182 |           -0.000402242 |             -0.00142519  |                  0.00103404  |                -0.00136943  |                            63.8397   |
| a7al2k_0af411481a5ff916 | J1_vol_range_structure      | derived_vol_range_state     | price|volatility        | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.00119392  |            0.000841899 |             -0.000644056 |                  0.000456135 |                -0.000701021 |                             0.914953 |
| a7al2k_060620a27cb890a8 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.00109864  |            7.82099e-05 |              0.000301048 |                 -0.000772347 |                 0.000210086 |                            66.9924   |
| a7al2k_0582e4bf9eee07c3 | J3_basis_funding_derived    | derived_basis_funding_state | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                nan           |          nan           |            nan           |                nan           |               nan           |                           nan        |
| a7al2k_08d85f94f610ca1c | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000365027 |            0.000306931 |              0.00206028  |                  0.00321298  |                 0.00220218  |                            41.2185   |
| a7al2k_036407741848d4cb | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.000685891 |           -5.62975e-05 |             -0.000734752 |                  0.00100193  |                -0.00071252  |                           154.712    |
| a7al2k_0da40100e049ebb0 | J1_vol_range_structure      | derived_vol_range_state     | price|volatility        | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000241136 |           -5.73263e-05 |              0.00015562  |                  0.000134352 |                 0.000262597 |                             8.70992  |
| a7al2k_0203ae25fddb9c4c | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.00215031  |           -0.00191191  |             -0.00237418  |                 -0.000159117 |                -0.00227696  |                            14.1955   |
| a7al2k_071c8b8bfa242a30 | J3_basis_funding_derived    | derived_basis_funding_state | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                nan           |          nan           |            nan           |                nan           |               nan           |                           nan        |
| a7al2k_0096829c83c908a8 | J4_upper_regime_interaction | derived_upper_regime_proxy  | liquidity|open_interest | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE |                 -0.000508861 |           -0.0014315   |             -0.00224684  |                  0.000152454 |                -0.00219818  |                             1.05137  |
| a7al2k_03ce8aaac75e26e9 | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_ONE_BAR_LAG_FRAGILE      |                 -0.00114881  |           -0.000715654 |             -8.11412e-05 |                  0.00108215  |                -1.59441e-05 |                           146.337    |
| a7al2k_0e03c17e1bf7169e | J1_vol_range_structure      | derived_vol_range_state     | price|volatility        | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                  1.81707e-05 |           -0.000418967 |              0.000313778 |                 -0.000610109 |                 0.000232838 |                            12.6865   |
| a7al2k_03b9932969f62f8e | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.00146728  |           -6.37405e-05 |             -0.00046763  |                 -0.00383829  |                -0.000506555 |                           482.904    |
| a7al2k_096415a86f56d3f8 | J3_basis_funding_derived    | derived_basis_funding_state | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                nan           |          nan           |            nan           |                nan           |               nan           |                           nan        |
| a7al2k_01bdc8d049fffe52 | J4_upper_regime_interaction | derived_upper_regime_proxy  | liquidity|open_interest | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE |                 -0.00112037  |           -0.00224767  |             -0.0027401   |                  0.0011895   |                -0.00266342  |                             1.22977  |
| a7al2k_063b28f2f9d781f7 | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.00102338  |           -0.000108441 |             -0.0025247   |                 -6.89953e-05 |                -0.00240869  |                           136.665    |
| a7al2k_1150d95fb30558dd | J1_vol_range_structure      | derived_vol_range_state     | price|volatility        | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000743536 |            0.000274068 |              7.64611e-05 |                  0.000628043 |                 0.000141077 |                            25.8615   |
| a7al2k_06188102ca912109 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000628692 |            0.000348829 |              1.22809e-05 |                  0.000513651 |                 8.29685e-06 |                           106.732    |
| a7al2k_09b5234b389c5fe1 | J3_basis_funding_derived    | derived_basis_funding_state | basis|funding           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                nan           |          nan           |            nan           |                nan           |               nan           |                           nan        |
| a7al2k_03504657e3ba5b29 | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis|open_interest     | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.0012196   |            0.00234088  |              0.00054944  |                  0.00733901  |                 0.000486204 |                             9.18787  |
| a7al2k_06b8318f595f8506 | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -3.81522e-05 |           -0.000944196 |              0.00014342  |                  0.000316772 |                 0.000157154 |                           118.395    |
| a7al2k_03d8e5796670fb0c | J1_vol_range_structure      | derived_vol_range_state     | volatility              | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                  0           |            0           |              0           |                  0           |                 0           |                           nan        |
| a7al2k_089c06984d76c253 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.00186529  |           -6.95578e-05 |              0.000581403 |                 -0.00388773  |                 0.000509252 |                           209.011    |
| a7al2k_026b22c78bdd76b5 | J3_basis_funding_derived    | derived_basis_funding_state | basis                   | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                  0.000506783 |           -1.3096e-05  |              0.0011095   |                 -0.00067402  |                 0.0015958   |                           761.137    |
| a7al2k_0159c55db14e25cc | J4_upper_regime_interaction | derived_upper_regime_proxy  | funding|open_interest   | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -1.86598e-05 |           -0.0025278   |             -0.00176451  |                 -0.00483714  |                -0.00172182  |                           157.075    |
| a7al2k_086e152c31cc3b70 | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                  0.000346371 |           -0.000762432 |             -0.00199651  |                 -0.000746398 |                -0.00198159  |                            42.0518   |
| a7al2k_03fbcde11749cea6 | J1_vol_range_structure      | derived_vol_range_state     | volatility              | HOLD_A7AL2L_CONTROL_DOMINATED        |                  0.000323625 |            0.00150714  |              0.00101429  |                  0.000243409 |                 0.000881139 |                            18.6558   |
| a7al2k_0a4084dd0b626854 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.00291433  |           -0.000908442 |             -0.00066702  |                 -0.000441967 |                -0.000589621 |                            47.773    |
| a7al2k_04511ab39ae22ff6 | J3_basis_funding_derived    | derived_basis_funding_state | basis                   | HOLD_A7AL2L_CONTROL_DOMINATED        |                  0.000617497 |            0.000997632 |              0.00116747  |                  0.00187106  |                 0.00140641  |                             9.63053  |
| a7al2k_04ed2a291c49f7d2 | J4_upper_regime_interaction | derived_upper_regime_proxy  | funding|open_interest   | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.000168413 |           -0.00257116  |             -0.00169943  |                 -0.00649972  |                -0.00162595  |                            13.8461   |
| a7al2k_08c7d090dcdf82bc | J0_oi_derived_state         | derived_oi_price_state      | open_interest|price     | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                  0.000276086 |           -0.000426795 |             -0.000265105 |                 -0.000723667 |                -0.000272214 |                            19.562    |
| a7al2k_079876e32e058a42 | J1_vol_range_structure      | derived_vol_range_state     | volatility              | HOLD_A7AL2L_CONTROL_DOMINATED        |                  0.00172612  |            0.000767879 |              0.00130327  |                  0.000521859 |                 0.00123448  |                            21.4368   |
| a7al2k_0de0ec5226a37b15 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.00234488  |           -0.000729401 |             -0.00111873  |                 -0.00130558  |                -0.00104491  |                            43.3439   |
| a7al2k_0b608b3e905615d7 | J3_basis_funding_derived    | derived_basis_funding_state | basis                   | HOLD_A7AL2L_CONTROL_DOMINATED        |                  0.000779354 |            0.000399145 |              0.00105055  |                  5.12981e-05 |                 0.00141657  |                            19.6975   |
| a7al2k_01759e5da72c472c | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis|liquidity         | A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE |                 -0.00123838  |           -0.00303946  |             -0.00195588  |                 -0.00338678  |                -0.00191405  |                             0.946342 |
| a7al2k_0d183c93611d3ea2 | J0_oi_derived_state         | derived_oi_price_state      | open_interest           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000873644 |            0.000354196 |             -0.00196364  |                 -0.00343069  |                -0.00202437  |                            41.398    |
| a7al2k_0aa42c09ec49389c | J1_vol_range_structure      | derived_vol_range_state     | volatility              | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.000923785 |           -0.000258316 |             -0.00271528  |                  0.00108311  |                -0.00269329  |                            95.9414   |
| a7al2k_0097d25af2875cc8 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -0.0013701   |           -0.00110509  |             -0.00247894  |                 -0.00131015  |                -0.00237046  |                            21.462    |
| a7al2k_18c59f7cae132548 | J3_basis_funding_derived    | derived_basis_funding_state | basis                   | HOLD_A7AL2L_ONE_BAR_LAG_FRAGILE      |                 -0.000332201 |           -0.000287042 |             -0.00105907  |                 -0.000186945 |                -0.000225259 |                             3.45244  |
| a7al2k_0406084a43f0d6e3 | J4_upper_regime_interaction | derived_upper_regime_proxy  | basis|liquidity         | HOLD_A7AL2L_CONTROL_DOMINATED        |                 -9.18757e-05 |           -0.00233065  |             -0.00574632  |                 -0.00459666  |                -0.00557703  |                            89.5315   |
| a7al2k_10d26ef9ef6068ab | J0_oi_derived_state         | derived_oi_price_state      | open_interest           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000979502 |            0.000576045 |             -0.000360522 |                  0.00216438  |                -0.000228597 |                           140.4      |
| a7al2k_0c53e43cfdaf2667 | J1_vol_range_structure      | derived_vol_range_state     | volatility              | HOLD_A7AL2L_CONTROL_DOMINATED        |                  0.0011097   |            0.00093459  |              0.00226639  |                 -0.000812664 |                 0.00224366  |                            16.1462   |
| a7al2k_0505415561457923 | J2_liquidity_lifecycle      | derived_liquidity_lifecycle | liquidity               | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                 -0.000583847 |            0.000325357 |              0.000760358 |                 -0.000911231 |                 0.000695134 |                            12.3296   |
| a7al2k_0308f7c0d2fce66c | J3_basis_funding_derived    | derived_basis_funding_state | funding|price           | HOLD_A7AL2L_UNSTABLE_PRE_MAY         |                nan           |          nan           |            nan           |                nan           |               nan           |                           nan        |

## Boundary

```text
Allowed interpretation:
  A7AL2L_DERIVED_REPLAY_PREFLIGHT_CLUE means a derived structure deserves controlled follow-up.

Not authorized:
  alpha proof
  shadow / paper / live
  large formula search
```
