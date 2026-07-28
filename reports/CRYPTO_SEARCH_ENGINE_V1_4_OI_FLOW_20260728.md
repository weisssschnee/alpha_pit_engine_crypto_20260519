# Crypto Search Engine V1.4 OI/Flow

- Source: `018be6caca5c7ad294729c17294295283589ec7d`
- Aligned carrier: `71 OI/mark + 44 aggTrades`; raw window `2025-06-28T05:00:00+00:00` to `2026-07-01T00:00:00+00:00`.
- Frozen evaluation window: `2025-08-29T07:00:00+00:00` to `2026-07-01T00:00:00+00:00` (`7,337` contiguous hours). The pre-reward rule excluded one earlier zero-eligibility hour.
- Dynamic eligible intersection: `144` assets ever eligible, `58–143` active assets per evaluated hour; no missing-value fill.
- Fields and target: all `115` fields have finite support; the existing OI/mark priority-venue price target and PIT/lag contract were reused unchanged.
- Generation attempts: `1,958`; strict candidates: `1,264`. The frozen memory gate selected the authorized `8`-worker fallback.
- Stage A: `PASS`; Stage B: `HOLD_ADAPTIVE_GATE`; Stage C: `NOT_RUN_STAGE_B_GATE`.
- Stage A: `64/64` strict (`32` binary, `32` hierarchical; `8` per semantic tuple); checkpoint restore verified.
- Stage B: `1,200/1,200` compile-valid, exact-unique, matched-control-valid and full-cost evaluated (`600` binary, `150` per each of four hierarchical tuples).
- Stage-B pair reward: mean `-5.235040`; exact-count top decile `-2.189121`.
- Matched positives: `0`; hierarchical matched positives: `0`; AB interaction positives: `0`; ABC conditional positives: `0`.
- Behavior families: `1,200/1,200`; duplicate rate `0.000000`. This is diversity without positive matched evidence, not an Alpha result.
- CandidateSpec and expression-hash replay passed `1,264/1,264`. Mutation/crossover receipts are not applicable because the gate stopped before adaptive Stage C.
- A/B/AB/ABC share target, support, eligibility, horizon, mapping, and 5 bps cost.
- Adaptive qualification: none. CEM V2 and Evolution V2 consumed no Stage-C budget.
- Development-only result; no OOS, promotion, challenge, recent, forward, or sealed reads.
