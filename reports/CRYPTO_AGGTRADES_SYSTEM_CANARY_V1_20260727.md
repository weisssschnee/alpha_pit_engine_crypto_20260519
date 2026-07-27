# Crypto aggTrades Search-System Canary V1

- Status: `PASS_SYSTEM_CANARY_COMPLETED`
- Research decision: `HOLD_RESEARCH_FIXED_RETROSPECTIVE_COHORT`
- Producer source: `5a17a91732a7aca7ec53cf9e10963faf2998a649`
- Strict completed: `2,000` from `3,452` raw attempts.
- Checkpoints: `2/2`, exact restore verified: `True`.
- Every candidate used at least one aggTrades field: `True`.
- Behavior families: `1,946`; duplicate rate `2.70%`.

## System comparison versus typed random

| Arm | valid exact-unique / CPU-hour delta | new families / 1k delta | mean pair reward delta | top-decile reward delta |
|---|---:|---:|---:|---:|
| Hierarchical Typed CEM V2 | 169.553689 | 0.000000 | 0.04025858 | 0.15055474 |
| Typed Evolution V2 | 50.755944 | -65.000000 | 0.36718781 | 0.94932567 |

This fixed-retrospective-cohort canary evaluates search-system behavior only.
It creates no Alpha, OOS, challenge, recent, May-stress, forward, promotion,
data-admission, latent-priority, or relational-training authority.
