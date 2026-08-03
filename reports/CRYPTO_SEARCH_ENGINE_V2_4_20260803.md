# Crypto Search Engine V2.4 closure

## Decision

`ENGINE_VALIDATION_BLOCKED`

The one authorized V2.4 fresh-family gate was consumed exactly once on PC2 at
producer SHA `83a38d56fc2b362aed65ba246ea3fbd7993dfc4a`. It failed closed on
the first frozen candidate because the matched control reproduced the primary
behavior:

`ValueError:CONTROL_BEHAVIOR_EQUALS_PRIMARY`

No candidate was replaced, backfilled, regenerated, tuned, or rerun.

## What passed

- July aggTrades acquisition completed for the frozen Top200 cohort: 200/200
  attempted, zero failures, with two upstream `notfound` symbols.
- Both TAR sidecar hashes and contents passed independent verification.
- The aligned carrier passed independent qualification: 115 fields (71
  OI/mark plus 44 aggTrades), Binance USD-M target, dynamic eligibility,
  PIT/lag identities, and no missing-value fill.
- The behavior-family receipt was frozen before the fresh-data read with 512
  unique candidates, 64 in each of eight arm-seed-horizon cells.

## Gate outcome

| Item | Result |
| --- | --- |
| Frozen candidates | 512 |
| Strict evaluated | 0 |
| Checkpoints | 0 |
| Workers | 10 |
| Memory fallback | No |
| Failed candidate | `949A5E2EDAE1E2117B9C9E49C9ABCA229F7E080A429285D3A57D0FFFBAF40D37` |
| Failure | `CONTROL_BEHAVIOR_EQUALS_PRIMARY` |
| Qualified arms | None |

Independent PC2 and local terminal checkers both returned
`PASS_V24_TERMINAL_BLOCKED_INDEPENDENT_CHECK`.

## Interpretation and boundary

This is a validation-constructibility block before any portfolio economics
were evaluated. It is not a negative result for the carrier, supplied fields,
behavior families, or crypto Alpha space. The one-time authorization is
consumed. No OOS, promotion, challenge, recent/May-stress/forward read, new
grammar, new evaluator, new search, reseed, tuning, or rescue rerun is
authorized by this closure.
