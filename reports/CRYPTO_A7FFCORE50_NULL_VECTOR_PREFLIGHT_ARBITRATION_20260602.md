# CRYPTO A7FF-CORE50 NULL-VECTOR PREFLIGHT ARBITRATION

Generated: 2026-06-02T01:20:08Z

## Decision

`PASS_A7FFCORE50_NULL_VECTOR_ARBITRATION_READY_FOR_CORE51_FILTERED_REPLAY_CONTRACT`

CORE50 arbitrates CORE49E vector materialization results. It writes replay-contract filters only; it does not execute replay, search, proof, promotion, shadow, paper, or live.

## Summary

| metric                           |         value |
|:---------------------------------|--------------:|
| seed_count                       | 1800          |
| materialization_pass_count       | 1728          |
| eligible_after_null_filter_count | 1462          |
| semantic_family_count            |   39          |
| eligible_semantic_family_count   |   39          |
| operator_count                   |    7          |
| eligible_operator_count          |    7          |
| median_abs_stale_corr            |    0.614064   |
| median_abs_time_shuffle_corr     |    0.127275   |
| median_abs_symbol_shuffle_corr   |    0.00568673 |

## Replay Filter Policy

| gate                    | rule                                                           | hard_gate   |
|:------------------------|:---------------------------------------------------------------|:------------|
| materialization_status  | must equal pass                                                | True        |
| active_ratio            | >= 0.001                                                       | True        |
| symbol_shuffle_corr_abs | <= 0.35 or missing                                             | True        |
| time_shuffle_corr_abs   | <= 0.95 or missing                                             | True        |
| stale_corr_abs          | record as risk tier; do not hard reject before replay contract | False       |
| family_cap              | replay contract must cap semantic_pair share <= 0.25           | True        |
| operator_cap            | replay contract must cap operator share <= 0.25                | True        |

## Stale Risk Tiers

| stale_risk_tier   |   seed_count |   semantic_family_count |   operator_count |
|:------------------|-------------:|------------------------:|-----------------:|
| medium            |          506 |                      33 |                7 |
| high              |          478 |                      38 |                7 |
| low               |          478 |                      28 |                6 |

## Filtered Family / Operator Summary

| semantic_pair                         | operator        |   eligible_count |   median_active_ratio |   median_abs_stale_corr |   median_abs_time_shuffle_corr |   median_abs_symbol_shuffle_corr |
|:--------------------------------------|:----------------|-----------------:|----------------------:|------------------------:|-------------------------------:|---------------------------------:|
| basis_premium_like|liquidity_like     | Delta           |                8 |              0.889278 |             0.720894    |                    0.000320878 |                      1.67969e-06 |
| basis_premium_like|volatility_like    | Delta           |                8 |              0.849384 |             0.914417    |                    0.00280468  |                      2.04316e-06 |
| basis_premium_like|basis_premium_like | Delta           |                8 |              0.888707 |             0.780888    |                    0.00100232  |                      2.16731e-06 |
| basis_premium_like|price_like         | Delta           |                8 |              0.88919  |             0.190915    |                    0.0076432   |                      9.186e-06   |
| basis_premium_like|positioning_like   | Identity        |                8 |              0.996323 |             0.802121    |                    0.0683389   |                      2.76533e-05 |
| basis_premium_like|positioning_like   | Delta           |                8 |              0.888341 |             0.082828    |                    0.00893433  |                      9.00661e-05 |
| basis_premium_like|basis_premium_like | Identity        |                8 |              0.987993 |             0.179762    |                    0.0499948   |                      0.00014484  |
| funding_like                          | Delta           |                8 |              0.410506 |             0.980441    |                    0.365546    |                      0.000930681 |
| basis_premium_like|liquidity_like     | Identity        |                8 |              0.996735 |             0.421153    |                    0.214376    |                      0.00130579  |
| basis_premium_like|volatility_like    | Identity        |                8 |              0.951307 |             0.833581    |                    0.227887    |                      0.00131437  |
| basis_premium_like                    | Delta           |                8 |              0.889735 |             0.781461    |                    0.0732497   |                      0.00153888  |
| basis_premium_like|price_like         | Identity        |                8 |              0.995297 |             0.0326786   |                    0.00976204  |                      0.00153988  |
| funding_like|funding_like             | Identity        |                8 |              0.11834  |             0.446878    |                    0.263719    |                      0.00413884  |
| basis_premium_like|positioning_like   | CSRank          |                8 |              0.997311 |             0.635453    |                    0.0159238   |                      0.0241486   |
| funding_like|funding_like             | CSRank          |                8 |              0.118484 |             0.762809    |                    0.22629     |                      0.0356951   |
| basis_premium_like|basis_premium_like | CSRank          |                8 |              0.791608 |             0.0895523   |                    0.0277736   |                      0.0807929   |
| basis_premium_like|liquidity_like     | CSRank          |                8 |              0.997726 |             0.310421    |                    0.104509    |                      0.201097    |
| basis_premium_like|volatility_like    | CSRank          |                8 |              0.952195 |             0.652877    |                    0.2004      |                      0.245997    |
| basis_premium_like|price_like         | CSRank          |                8 |              0.992884 |             0.0195589   |                    0.0100891   |                      0.294862    |
| positioning_like|positioning_like     | Delta           |                7 |              0.998082 |             9.17188e-07 |                    5.65883e-07 |                      8.21588e-07 |
| positioning_like|price_like           | Delta           |                7 |              0.998015 |             1.93872e-06 |                    1.23968e-05 |                      1.01541e-06 |
| positioning_like|volatility_like      | Delta           |                7 |              0.998229 |             1.36528e-05 |                    4.70725e-06 |                      1.06535e-06 |
| liquidity_like|positioning_like       | Delta           |                7 |              0.998229 |             2.6342e-05  |                    1.24811e-05 |                      4.52944e-06 |
| state_or_taxonomy|volatility_like     | Delta           |                7 |              0.151476 |             0.929747    |                    0.00304631  |                      1.24032e-05 |
| basis_premium_like|positioning_like   | AbsDelta        |                7 |              0.996761 |             0.723133    |                    0.04014     |                      7.00188e-05 |
| basis_premium_like|basis_premium_like | AbsDelta        |                7 |              0.991388 |             0.245287    |                    0.0327002   |                      9.72923e-05 |
| liquidity_like|positioning_like       | Identity        |                7 |              0.998179 |             0.0165062   |                    0.00480253  |                      0.000100484 |
| basis_premium_like|state_or_taxonomy  | AbsDelta        |                7 |              0.992679 |             0.0110699   |                    0.00480454  |                      0.00011084  |
| liquidity_like|volatility_like        | Delta           |                7 |              0.952369 |             0.649963    |                    0.00511673  |                      0.000129226 |
| positioning_like|volatility_like      | Identity        |                7 |              0.99161  |             0.0286628   |                    0.000680862 |                      0.000157522 |
| positioning_like|state_or_taxonomy    | Delta           |                7 |              0.998168 |             0.0115825   |                    0.00900238  |                      0.000159036 |
| funding_like|liquidity_like           | Delta           |                7 |              0.371287 |             0.615272    |                    0.0094543   |                      0.000201944 |
| funding_like|price_like               | Delta           |                7 |              0.371291 |             0.0775944   |                    0.00339216  |                      0.000246543 |
| basis_premium_like|volatility_like    | AbsDelta        |                7 |              0.951044 |             0.788663    |                    0.184658    |                      0.000257158 |
| basis_premium_like|liquidity_like     | AbsDelta        |                7 |              0.996989 |             0.469956    |                    0.142546    |                      0.000278295 |
| positioning_like|price_like           | Identity        |                7 |              0.992058 |             0.000893023 |                    0.000824072 |                      0.000287571 |
| basis_premium_like|price_like         | AbsDelta        |                7 |              0.994732 |             0.0284122   |                    0.00944207  |                      0.000414841 |
| positioning_like|positioning_like     | Identity        |                7 |              0.997904 |             0.0166363   |                    0.00825464  |                      0.00055566  |
| volatility_like|volatility_like       | Delta           |                7 |              0.95237  |             0.881278    |                    0.00433239  |                      0.000733877 |
| funding_like|state_or_taxonomy        | Delta           |                7 |              0.37128  |             0.0771939   |                    0.0192624   |                      0.000749982 |
| price_like|volatility_like            | Delta           |                7 |              0.952371 |             0.0739013   |                    0.00132044  |                      0.000905222 |
| liquidity_like|price_like             | Delta           |                7 |              0.992334 |             0.0447996   |                    0.00364416  |                      0.00118141  |
| funding_like|positioning_like         | Delta           |                7 |              0.371169 |             0.891535    |                    0.0236794   |                      0.00123705  |
| funding_like                          | WinsorZ         |                7 |              0.195846 |             0.708347    |                    0.28583     |                      0.00126402  |
| liquidity_like|volatility_like        | Identity        |                7 |              0.99875  |             0.411371    |                    0.204671    |                      0.00126457  |
| funding_like|volatility_like          | Delta           |                7 |              0.371289 |             0.892416    |                    0.0910862   |                      0.00130536  |
| liquidity_like|price_like             | Identity        |                7 |              0.998463 |             0.452197    |                    0.21128     |                      0.00137744  |
| basis_premium_like                    | AbsDelta        |                7 |              0.997509 |             0.901612    |                    0.551032    |                      0.00142078  |
| basis_premium_like|positioning_like   | WinsorZ         |                7 |              0.996876 |             0.527695    |                    0.0196256   |                      0.00146781  |
| funding_like|positioning_like         | Identity        |                7 |              0.196303 |             0.376435    |                    0.0140357   |                      0.00148785  |
| price_like|price_like                 | Identity        |                7 |              0.992342 |             0.0331549   |                    0.0101218   |                      0.00154655  |
| state_or_taxonomy|state_or_taxonomy   | Delta           |                7 |              0.124909 |             0.0224031   |                    0.000855277 |                      0.00157541  |
| generic_numeric|volatility_like       | Identity        |                7 |              0.992068 |             0.657082    |                    0.0245491   |                      0.00159106  |
| basis_premium_like|state_or_taxonomy  | WinsorZ         |                7 |              0.992711 |             0.0059921   |                    0.00359421  |                      0.00159996  |
| price_like|volatility_like            | Identity        |                7 |              0.991893 |             0.695835    |                    0.0212545   |                      0.00164849  |
| funding_like|state_or_taxonomy        | Identity        |                7 |              0.196361 |             0.0319762   |                    0.0158769   |                      0.00168532  |
| liquidity_like|state_or_taxonomy      | Delta           |                7 |              0.998672 |             0.0281838   |                    0.0281271   |                      0.00187393  |
| funding_like|positioning_like         | WinsorZ         |                7 |              0.194266 |             0.448034    |                    0.015866    |                      0.00204528  |
| liquidity_like|state_or_taxonomy      | Identity        |                7 |              0.950087 |             0.395022    |                    0.135475    |                      0.00250604  |
| funding_like|positioning_like         | AbsDelta        |                7 |              0.105407 |             0.586505    |                    0.00834258  |                      0.00270961  |
| basis_premium_like|basis_premium_like | WinsorZ         |                7 |              0.991418 |             0.126432    |                    0.00931915  |                      0.00282713  |
| funding_like|liquidity_like           | Identity        |                7 |              0.19634  |             0.267596    |                    0.0663314   |                      0.00287628  |
| funding_like                          | SignedRankDelta |                7 |              0.195961 |             0.668829    |                    0.243143    |                      0.003569    |
| funding_like|funding_like             | AbsDelta        |                7 |              0.072829 |             0.661825    |                    0.15297     |                      0.00373844  |
| positioning_like|state_or_taxonomy    | Identity        |                7 |              0.949763 |             0.697284    |                    0.0202063   |                      0.0038085   |
| funding_like|liquidity_like           | WinsorZ         |                7 |              0.194343 |             0.340588    |                    0.0363648   |                      0.00384846  |
| funding_like|price_like               | Identity        |                7 |              0.196069 |             0.0080278   |                    0.00245919  |                      0.0039852   |
| funding_like|volatility_like          | Identity        |                7 |              0.195623 |             0.404469    |                    0.137416    |                      0.00484894  |
| price_like|state_or_taxonomy          | Identity        |                7 |              0.948462 |             0.0239505   |                    0.00817519  |                      0.00485259  |
| state_or_taxonomy|volatility_like     | Identity        |                7 |              0.952862 |             0.0383526   |                    0.0139101   |                      0.00505605  |
| price_like|state_or_taxonomy          | Delta           |                7 |              0.998458 |             0.0510154   |                    0.0408644   |                      0.00592634  |
| funding_like|funding_like             | WinsorZ         |                7 |              0.112906 |             0.516498    |                    0.0302924   |                      0.00627196  |
| basis_premium_like|liquidity_like     | WinsorZ         |                7 |              0.997105 |             0.322043    |                    0.00960556  |                      0.00654643  |
| funding_like|liquidity_like           | AbsDelta        |                7 |              0.105468 |             0.541388    |                    0.0351031   |                      0.00782416  |
| basis_premium_like|volatility_like    | WinsorZ         |                7 |              0.951151 |             0.560967    |                    0.0102082   |                      0.00789917  |
| funding_like|price_like               | AbsDelta        |                7 |              0.112802 |             0.0370408   |                    0.00509472  |                      0.010015    |
| basis_premium_like|price_like         | WinsorZ         |                7 |              0.995267 |             0.0240391   |                    0.026411    |                      0.0103335   |
| funding_like                          | AbsDelta        |                7 |              0.112973 |             0.843668    |                    0.320674    |                      0.0139642   |
| volatility_like|volatility_like       | Identity        |                7 |              0.952378 |             0.824936    |                    0.259607    |                      0.0141761   |
| basis_premium_like                    | SignedRankDelta |                7 |              0.997922 |             0.734424    |                    0.0277503   |                      0.0162098   |

## Authorization

```json
{
  "authorized": {
    "A7FF-CORE50R null-vector filter repair": false,
    "A7FF-CORE51 filtered replay contract": true
  },
  "not_authorized": {
    "alpha_proof": true,
    "direct_replay_execution": true,
    "formula_search": true,
    "large_search": true,
    "promotion": true,
    "shadow_paper_live": true
  }
}
```

## Manifest

```json
{
  "authorizes_alpha_proof": false,
  "authorizes_core51_filtered_replay_contract": true,
  "authorizes_direct_replay_execution": false,
  "authorizes_formula_search": false,
  "authorizes_large_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [],
  "decision": "PASS_A7FFCORE50_NULL_VECTOR_ARBITRATION_READY_FOR_CORE51_FILTERED_REPLAY_CONTRACT",
  "eligible_after_null_filter_count": 1462,
  "eligible_operator_count": 7,
  "eligible_semantic_family_count": 39,
  "executes_generation": false,
  "executes_replay": false,
  "executes_search": false,
  "generated_at": "2026-06-02T01:20:08Z",
  "materialization_pass_count": 1728,
  "next_allowed": "A7FF-CORE51 filtered replay contract",
  "seed_count": 1800,
  "source_decision": "PASS_A7FFCORE49E_NULL_VECTOR_PREFLIGHT_READY_FOR_CORE50_CONTRACT",
  "source_stage": "A7FF-CORE49E",
  "stage": "A7FF-CORE50"
}
```
