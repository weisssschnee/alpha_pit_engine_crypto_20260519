# Crypto 120-token Core Pack consumption qualification

This is a development-only plumbing qualification. It is not model-quality, alpha, portfolio, economic, or OOS evidence.

- Source SHA: `f01d0d22a40ae9949a027fe138c52998fb23c1ef`
- Status: `CORE_PACK_CONTEXT_BOUND_CONSUMPTION_VERIFIED`
- Core Pack identity: `B6765D5A60B9A348A47A88BB53D503A48E024C1BAF83BCB14B2F4BF06E248D00`
- Plumbing-connected tokens: 120/120
- Nontrivially utilized tokens: 120/120
- Runtime seconds: 17.941

## Context separation

The pack remains two independent model surfaces. No synthetic 120-channel joint panel was created.

### BROAD_PANEL_BASELINE

- Value channels: 39
- Probe samples: 8192
- Gradient reachable: 39/39
- First-layer parameters updated: 39/39
- Prediction-sensitive under zero ablation: 39/39
- Training loss decreased: True
- Data range: 2023-07-01T00:00:00+00:00 through 2024-06-30T23:00:00+00:00

### CORE3_MICROSTRUCTURE_PILOT

- Value channels: 81
- Probe samples: 8192
- Gradient reachable: 81/81
- First-layer parameters updated: 81/81
- Prediction-sensitive under zero ablation: 81/81
- Training loss decreased: False
- Data range: 2024-01-01T00:00:00+00:00 through 2024-06-30T23:00:00+00:00

## Derived execution contract

Core3 lazy tokens are resolved before execution: TSMean is a trailing same-symbol mean; Delta is a trailing same-symbol difference; ZScore is the historical `ZScore(TSMean(field, window))` cross-sectional execution; Decay is bound to the current `CryptoFeatureAlgebra` linear-decay implementation. Registry availability lag is aligned before the probe, and same-hour execution remains forbidden.

## Failures

None.

## Claim boundary

A passing token proves loadability, materialization, tensor exposure, gradient reachability, parameter update, and prediction sensitivity in this frozen probe. It does not prove unique information, stable learning value, portfolio increment, economic value, or OOS validity.
The context-level training-loss flag is reported separately and is not part of token consumption admission.
