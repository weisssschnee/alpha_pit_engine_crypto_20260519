# CRYPTO A7POOL-0 ALPHA-ELIGIBLE POOL REBUILD

Generated: 2026-05-29T14:40:16Z

## Decision

`HOLD_A7POOL0_POOL_NOT_READY_FOR_SELECTOR`

A7POOL-0 rebuilds a role-clean pool only from A7AI-F4 promoted ordinary-alpha field evidence. It does not run replay or search.

## Manifest

```json
{
  "alpha_eligible_count": 8,
  "authorizes_a7sel1": false,
  "authorizes_alpha_proof": false,
  "authorizes_search": false,
  "authorizes_shadow_paper_live": false,
  "blockers": [
    "single_family_concentration_gt_35pct"
  ],
  "decision": "HOLD_A7POOL0_POOL_NOT_READY_FOR_SELECTOR",
  "duplicate_expression_count_before_dedup": 8,
  "executes_generation": true,
  "executes_replay": false,
  "executes_search": false,
  "field_family_count": 1,
  "generated_at": "2026-05-29T14:40:16Z",
  "generated_count": 8,
  "skeleton_count": 7,
  "stage": "A7POOL-0",
  "top_family_share": 1.0,
  "top_skeleton_share": 0.25,
  "uses_may": false
}
```

## Family Distribution

| field_family   |   count |   share |
|:---------------|--------:|--------:|
| basis_premium  |       8 |       1 |

## Generated Pool

| candidate_id             | expression                                             | field_family   | variant              | candidate_role       | skeleton_key              |
|:-------------------------|:-------------------------------------------------------|:---------------|:---------------------|:---------------------|:--------------------------|
| a7pool0_a3242ce835dd1b8c | Neg(Delta(mark_index_basis_bps,24))                    | basis_premium  | base_oriented        | ordinary_alpha_valid | skeleton_18251bd7256b8dc6 |
| a7pool0_7600397360cad719 | Clip(ZScore(Neg(Delta(mark_index_basis_bps,24))),-3,3) | basis_premium  | clip_zscore_oriented | ordinary_alpha_valid | skeleton_53dc28f93093638a |
| a7pool0_3e1829dfd7143d6f | CSRank(Neg(Delta(mark_index_basis_bps,24)))            | basis_premium  | cs_rank_oriented     | ordinary_alpha_valid | skeleton_b79cfcecad767a02 |
| a7pool0_d6cc2ef5deeaaebc | Decay(Neg(Delta(mark_index_basis_bps,24)),8)           | basis_premium  | decay8_oriented      | ordinary_alpha_valid | skeleton_2936e80c01c9afaa |
| a7pool0_a6aeb5a6688421fc | Mean(Neg(Delta(mark_index_basis_bps,24)),24)           | basis_premium  | mean24_oriented      | ordinary_alpha_valid | skeleton_66aea7f2fb86e1df |
| a7pool0_d10f3ed87f0448a0 | Mean(Neg(Delta(mark_index_basis_bps,24)),4)            | basis_premium  | mean4_oriented       | ordinary_alpha_valid | skeleton_66aea7f2fb86e1df |
| a7pool0_7170d59ad2e122c8 | TSRank(Neg(Delta(mark_index_basis_bps,24)),24)         | basis_premium  | tsrank24_oriented    | ordinary_alpha_valid | skeleton_e832e47f732ad2d3 |
| a7pool0_5665b6de1cfed2ab | ZScore(Neg(Delta(mark_index_basis_bps,24)))            | basis_premium  | zscore_oriented      | ordinary_alpha_valid | skeleton_c9be780d74a0fdd7 |

## Boundary

```text
A7POOL-0 may produce role-clean diagnostic pool artifacts, but it does not authorize formula search or alpha proof.
If family/skeleton concentration fails, A7SEL-1 is not authorized except as a blocked/not-run record.
```
