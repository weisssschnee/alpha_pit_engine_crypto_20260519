# CRYPTO A7FF-CORE0 TYPED AST GOVERNANCE

Generated: 2026-05-31T16:55:36Z

## Decision

`PASS_A7FFCORE0_TYPED_AST_GOVERNANCE_READY_FOR_CORE1`

A7FF-CORE0 is a governance-only layer. It formalizes that derived feature generation and formula generation must use one typed expression / FeatureAlgebra AST. It does not execute generation, numeric evaluation, replay, or search.

## Current Breakpoint

```json
{
  "decision": "HOLD_A7FF55R5E_SHARDED_NUMERIC_WEAK_RESPONSE",
  "governance_interpretation": "R2/R3/R4 repaired coverage, but the system still lacks a unified typed subgraph boundary; field-family repair can create syntactic coverage without enough response-backed factor seeds.",
  "numeric_response_issue": {
    "non_l7_numeric_clue_rows": 4,
    "sampled_input_blueprints": 350,
    "selected_portfolio_queue_count": 2
  },
  "source": "A7FF-55R5E"
}
```

## Expression Node Schema

```json
{
  "global_invariants": [
    "label nodes cannot be referenced by Field/Transform/Interaction nodes",
    "diagnostic/risk/neutralizer nodes cannot become ordinary alpha without explicit response-backed promotion",
    "FormulaGen may only compose approved feature subgraphs",
    "FeatureFactory may only emit typed subgraphs, not standalone untyped columns",
    "selector reads factor_role and response_evidence, not only expression string"
  ],
  "node_types": {
    "FactorCandidate": {
      "promotion_boundary": "cannot become replay candidate without response/control/latency evidence",
      "required": [
        "expression_node_id",
        "orientation_source",
        "label_family",
        "horizon_hours",
        "neutralization",
        "control_policy",
        "response_evidence_id"
      ]
    },
    "Field": {
      "allowed_roles": [
        "raw_source",
        "signal_seed",
        "regime",
        "neutralizer",
        "risk_exposure",
        "diagnostic",
        "label_only",
        "forbidden"
      ],
      "required": [
        "field_name",
        "raw_source_family",
        "semantic_type",
        "field_role",
        "pit_policy",
        "latency_policy"
      ]
    },
    "Interaction": {
      "operators": [
        "Mul",
        "Sub",
        "Add",
        "SafeDiv",
        "GatedSign",
        "SpreadRank",
        "SmoothMul"
      ],
      "required": [
        "operator",
        "left_node_id",
        "right_node_id",
        "semantic_pair",
        "motif",
        "role_policy"
      ]
    },
    "Label": {
      "required": [
        "label_family",
        "horizon_hours",
        "entry_alignment",
        "usage"
      ],
      "usage": "target_only_never_feature"
    },
    "Neutralization": {
      "operators": [
        "CSRank",
        "WithinLatentRank",
        "WithinLiquidityTierRank",
        "Residualize"
      ],
      "required": [
        "input_node_id",
        "group_key",
        "neutralization_policy",
        "min_group_count"
      ]
    },
    "Transform": {
      "operators": [
        "Delta",
        "Mean",
        "ZScore",
        "TSRank",
        "Decay",
        "Rank",
        "CSRank",
        "Abs",
        "Sign",
        "Clip"
      ],
      "required": [
        "operator",
        "input_node_id",
        "lookback_hours",
        "fit_window",
        "pit_policy",
        "role_policy"
      ]
    }
  },
  "schema_version": "a7ff_core_ast_v0"
}
```

## Layer Boundary

| layer                      | owner                             | artifact                                  | may_generate                                               | must_not_generate                                   |
|:---------------------------|:----------------------------------|:------------------------------------------|:-----------------------------------------------------------|:----------------------------------------------------|
| L0_raw_field               | data_contracts / feature registry | Field node                                | raw field node only                                        | transforms, labels as feature, formula interactions |
| L1_typed_derived_feature   | Field-to-Factor Compiler          | Transform / Interaction subgraph          | typed subgraph with lineage/PIT/role                       | alpha candidate or replay authorization             |
| L2_response_tested_feature | response map / controls           | feature subgraph + response evidence      | promotion evidence                                         | portfolio claim                                     |
| L3_factor_candidate        | selector preflight                | FactorCandidate node                      | candidate with label/horizon/orientation/control policy    | paper/shadow/live authorization                     |
| L4_alpha_formula_candidate | FormulaGen / Searcher             | composition of approved factor candidates | bounded formula hypotheses                                 | raw unapproved feature transforms                   |
| L5_book_component          | replay / cluster / promotion      | book component                            | promotion candidate after replay/cluster/marginal evidence | bypass proof gates                                  |

## Role Enforcement Matrix

| role                                | feature_factory_allowed                     | formula_gen_allowed                                | selector_allowed                                   |
|:------------------------------------|:--------------------------------------------|:---------------------------------------------------|:---------------------------------------------------|
| ordinary_alpha_seed                 | emit typed subgraph after response evidence | compose with approved factor candidates            | eligible for alpha queue if controls pass          |
| exploratory_signal_seed             | emit typed subgraph for numeric response    | compose only in diagnostic/repair waves            | not alpha-eligible until response-backed promotion |
| regime_neutralizer_interaction_seed | emit as modifier/condition node             | right-hand modifier only unless promoted           | cannot stand alone as alpha signal                 |
| risk_defense_only                   | emit defense/neutralization node            | not allowed in ordinary alpha expression as signal | reject for alpha replay                            |
| diagnostic_only                     | emit only with diagnostic route             | diagnostic search only                             | cannot enter ordinary alpha replay queue           |
| label_only                          | target node only                            | forbidden as feature input                         | forbidden as candidate field                       |

## Generator Overlap Audit

| object_type   | object_id                              | in_a7ff_v20260530   | in_repaired_a7ff55r3   | governance_note                                                                |
|:--------------|:---------------------------------------|:--------------------|:-----------------------|:-------------------------------------------------------------------------------|
| semantic_pair | basis_premium_like                     | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | basis_premium_like\|basis_premium_like | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | basis_premium_like\|funding_like       | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | basis_premium_like\|generic_numeric    | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | basis_premium_like\|liquidity_like     | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | basis_premium_like\|positioning_like   | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | basis_premium_like\|price_like         | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | basis_premium_like\|state_or_taxonomy  | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | basis_premium_like\|volatility_like    | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | funding_like\|positioning_like         | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | liquidity_like                         | False               | True                   | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | liquidity_like\|volatility_like        | True                | True                   | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | open_interest_like                     | False               | True                   | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | open_interest_like\|positioning_like   | False               | True                   | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | open_interest_like\|price_like         | False               | True                   | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | price_like                             | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | price_like\|volatility_like            | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | taker_flow_like                        | False               | True                   | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | taker_flow_like\|basis_premium_like    | False               | True                   | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | taker_flow_like\|open_interest_like    | False               | True                   | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | volatility_like                        | True                | True                   | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| semantic_pair | volatility_like\|volatility_like       | True                | False                  | semantic pair must map to typed AST semantic_pair, not ad hoc string families  |
| field         | age_x_liquidity                        | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | basis_abs_168h                         | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | funding_rate                           | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | liquidity_rank_active_universe         | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | mark_index_basis_bps                   | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | mark_trade_basis_bps                   | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | open_interest_change_24h               | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | open_interest_last                     | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | open_interest_mean                     | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | open_interest_value_last               | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | open_interest_value_mean               | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | premium_abs_168h                       | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | premium_close                          | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | premium_close_bps                      | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | premium_count                          | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | premium_high                           | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | premium_low                            | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | premium_open                           | True                | False                  | field role must be carried as Field node metadata before transform/formula use |
| field         | taker_buy_quote_volume                 | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | taker_buy_sell_volume_ratio_last       | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | taker_buy_sell_volume_ratio_mean       | True                | True                   | field role must be carried as Field node metadata before transform/formula use |
| field         | taker_buy_volume                       | True                | True                   | field role must be carried as Field node metadata before transform/formula use |

## Migration Plan

| step       | task                              | success_criteria                                                                           | blocks                                                        |
|:-----------|:----------------------------------|:-------------------------------------------------------------------------------------------|:--------------------------------------------------------------|
| A7FF-CORE1 | AST schema adapter                | formula_index rows can round-trip expression string -> typed AST JSON -> expression string | no new formula generation until adapter exists for new stages |
| A7FF-CORE2 | FeatureFactory subgraph registry  | derived features are emitted as approved subgraphs with raw_inputs/lookback/PIT/role       | manual untyped derived columns                                |
| A7FF-CORE3 | FormulaGen approved-subgraph gate | FormulaGen can only compose approved AST subgraphs or explicitly diagnostic nodes          | bypass of field-role enforcement                              |
| A7FF-CORE4 | SearchMemory semantic dedup       | dedup includes raw_inputs/operator_path/semantic_type/response_role, not string only       | duplicate economic meaning under different names              |
| A7FF-CORE5 | selector role trace enforcement   | selector trace records AST node roles and rejects role violations fail-closed              | diagnostic/risk fields selected as ordinary alpha             |

## Boundary

```text
generation executed: false
numeric execution: false
replay executed: false
search executed: false
May used: false
alpha proof / shadow / paper / live: false
```
