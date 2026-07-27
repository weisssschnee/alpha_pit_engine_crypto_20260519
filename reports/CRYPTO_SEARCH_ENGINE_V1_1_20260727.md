# Crypto Search Engine V1.1 Behavior-Niched Arena

- Status: `PASS_SEARCH_ENGINE_V1_1_COMPLETED`
- Research decision: `HOLD_RESEARCH_SPENT_FIXED_RETROSPECTIVE_COHORT`
- Producer source: `17ac5de989dec464b0c4903256f3f7662eeb9778`
- Strict completed: `3,000` from `5,444` raw attempts.
- Checkpoints: `2/2`, exact restore verified: `True`.
- Behavior families: `2,916`; duplicate rate `2.80%`.
- Positive matched discoveries by arm: `{"behavior_niched_cem_v2_1": 0, "behavior_niched_evolution_v2_1": 0, "canonical_typed_random": 0}`.

## Equal-count system comparison versus typed random

| Arm | valid unique / CPU-hour delta | new families / 1k | delta | mean reward delta | top-decile delta | duplicate rate |
|---|---:|---:|---:|---:|---:|---:|
| Behavior-Niched CEM V2.1 | -145.497924 | 1000.000 | 0.000 | 0.12060297 | -0.08651707 | 0.00% |
| Behavior-Niched Evolution V2.1 | -233.935522 | 926.000 | -74.000 | 0.76606812 | 1.14011489 | 7.80% |

## System decision

- CEM V2.1: `REJECT_INCREMENT_NOT_DEMONSTRATED`
- Evolution V2.1: `REJECT_INCREMENT_NOT_DEMONSTRATED`
- Future new-data Arena arms: `[]`

This fixed, spent-development Arena evaluates search capability only. It
creates no Alpha, OOS, challenge, recent, May-stress, forward, promotion,
data-admission, latent-priority, relational-training, or future-Arena
qualification authority.
