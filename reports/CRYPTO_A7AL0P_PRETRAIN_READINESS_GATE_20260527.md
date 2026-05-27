# CRYPTO A7AL-0P Pretrain Readiness Gate

Generated: 2026-05-27T03:51:50Z

## Decision

```text
PASS_A7AL0P_PRETRAIN_READY_FOR_A7AL1_FIELD_FAMILY_BASELINE
```

## Checks

| check | status | blocker | detail |
| --- | --- | --- | --- |
| feature_lineage_100pct_resolved | PASS |  | rows=81 |
| label_fields_isolated | PASS |  | label_rows=1 |
| pit_lag_and_field_native_latency_contract | PASS |  | pit_rows=80 fixed_2h_delay_ok=True |
| derived_feature_contract_passed | PASS |  | PASS_A7AL0F_DERIVED_FEATURE_ENGINEERING_CONTRACT |
| upper_regime_train_only_passed | PASS |  | PASS_A7AL0G_UPPER_REGIME_STATE_BUILDER |
| fixed_delay_stress_abolished | PASS |  | PASS_A7AL0L_FIXED_DELAY_STRESS_ABOLISHED |
| neutralization_policy_exists | PASS |  | modes=6 |
| negative_control_plan_exists | PASS |  | controls=8 |
| no_may_dependency | PASS |  | May unavailable and not used |
| a7al1_only_authorization | PASS |  | pretrain gate can authorize field-family baseline only, not formula search |

## Authorization

```text
AUTHORIZED:
  A7AL-1 field-family neutralized baseline replay

NOT AUTHORIZED:
  A7AL-2 formula search
  alpha proof
  shadow / paper / live
```
