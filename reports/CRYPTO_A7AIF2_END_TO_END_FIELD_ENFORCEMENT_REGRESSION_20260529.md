# CRYPTO A7AI-F2 END TO END FIELD ENFORCEMENT REGRESSION

Generated: 2026-05-29T14:09:19Z

## Decision

`PASS_A7AIF2_END_TO_END_ENFORCEMENT_CONNECTED`

## Generator Mode Smoke

| mode           |   registry_field_count |   eligible_motif_family_count |   generated_count | error                                                               |   blocked_field_leak_count | sample_expression                                                                    | decision                           |
|:---------------|-----------------------:|------------------------------:|------------------:|:--------------------------------------------------------------------|---------------------------:|:-------------------------------------------------------------------------------------|:-----------------------------------|
| ordinary_alpha |                      1 |                             0 |                 0 | no motif families have fields allowed for field_mode=ordinary_alpha |                          0 |                                                                                      | PASS_FAIL_CLOSED_NO_ELIGIBLE_MOTIF |
| diagnostic     |                     21 |                             5 |                 8 |                                                                     |                          0 | Add(ZScore(Delta(taker_buy_sell_volume_ratio_last,48)),Rank(Mean(trade_volume,168))) | PASS                               |
| risk_defense   |                      5 |                             0 |                 0 | no motif families have fields allowed for field_mode=risk_defense   |                          0 |                                                                                      | PASS_FAIL_CLOSED_NO_ELIGIBLE_MOTIF |

## Evaluator Fail-Closed Audit

| check                  | expression              | should_pass   | actual_pass   | error                                                       | decision   |
|:-----------------------|:------------------------|:--------------|:--------------|:------------------------------------------------------------|:-----------|
| allowed_contract_field | mark_index_basis_bps    | True          | True          |                                                             | PASS       |
| label_future_field     | forward_trade_return_1h | False         | False         | field contract blocks field: forward_trade_return_1h:FORBID | PASS       |
| missing_contract_field | made_up_field           | False         | False         | field contract missing: made_up_field                       | PASS       |

## Historical Candidate Role Summary

| candidate_role       | decision        |   count |
|:---------------------|:----------------|--------:|
| risk_defense_only    | DIAGNOSTIC_ONLY |    1982 |
| weak_or_unclassified | DIAGNOSTIC_ONLY |    2018 |

## Boundary

```text
No formula search, replay execution, alpha proof, shadow, paper, or live execution is authorized.
Diagnostic-only and risk-defense-only fields are not ordinary alpha replay seeds.
```
