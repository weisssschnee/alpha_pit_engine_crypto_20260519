# Crypto Internal Search Instrument Capability Report

**Final status:** `CRYPTO_INTERNAL_SEARCH_INSTRUMENT_CAPABILITY_QUALIFIED`  
**Source commit:** `46280c5ad2acf6783d0ede0eb27fd93e3713d6f0`  
**Accepted closure:** `crypto-frontier-provenance-closure-20260714` → `4726795f61052470d56e2d1475e4f6da9d262943`  
**Scope:** deterministic synthetic capability only; no market alpha or economic increment claim.

## 结论

内部搜索仪器已经通过固定有限 grammar 内的表达、发现、保留、显式持仓映射、full-L1 换手/固定 5 bps 成本和 decoy 排序能力门槛。该结论不改变 `CURRENT_DATA_UNDERPOWERED`、`FINANCIAL_GATE_HOLD_RESEARCH` 或任何 sealed/frozen 边界。

## 十个必答问题

### 1. Canonical primitive authority

`Delta`, `Slope`, `Acceleration`, `Persistence`, `Duration`, `StateAge`, `TimeSince`, `LastHit`, `FirstHit`, `Transition`, `PathShape`, `EventWindow`, `MultiScaleRelation`。每个 active ID 只绑定 `alphafactory_crypto.instrument_capability.primitives.evaluate_primitive` 中的一种数学语义。

### 2. Deprecated 旧实现

Closure tag 中 `temporal_program`、`nextgen_epoch` 与 `b1s_canary` 的同名差异实现仅保留为 source-qualified legacy adapter/parity source；它们不能以旧同名重新取得 active authority。35 条显式 alias 记录见 implementation authority CSV。

### 3. 已确认的历史语义漂移

- `EXACT_PARITY`: Acceleration, Delta
- `CONDITIONAL_PARITY`: MultiScaleRelation
- `EXPECTED_SEMANTIC_CHANGE`: Duration, EventWindow, Persistence, Slope, Transition
- `LEGACY_BEHAVIOR_DEPRECATED`: FirstHit, LastHit, PathShape, StateAge, TimeSince

### 4. 三种 mapping 保留/删除的信息

- `CROSS_SECTIONAL_ZERO_NET` 保留同一时点资产间相对次序；显式删除 common mode 与绝对置信度。singleton/inadequate cross-section 为 infeasible no-trade。
- `TIME_SERIES_DIRECTIONAL_STATEFUL` 保留符号、绝对置信度、common mode、entry/exit hysteresis 与持有状态；不 demean。
- `SPARSE_EVENT_OR_CARRY` 保留 singleton event、少量 active assets、settlement cadence、fixed hold 与 explicit exit/no-trade；不强制横截面归零。

### 5. Turnover attribution

`raw signal movement` 与权重变化使用不同单位，不能直接作历史因果分解。证据分别报告 raw movement、entry establishment、rebalance、exit、mapped full-L1 turnover，以及同一 raw signal 的 direct clipped-signal counterfactual。固定 5 bps 只覆盖线性 cost；spread/slippage/impact/fill/capacity 未建模。

### 6. Aligned feedback 是否优于旧 gross proxy

在固定 synthetic comparable set 上，aligned decoy rejection 为 100.0%，旧 proxy 为 53.6%；aligned top-3 strict-feasible rate 为 33.3%，旧 proxy 为 23.8%。这是 instrument alignment 增量，不是经济收益增量。

### 7. 仍能欺骗 feedback 的 decoy

旧 zero-cost gross proxy：`high_gross_high_concentration`, `high_gross_high_cost`, `negative_benchmark_increment`。新 aligned feedback：无。

### 8. 七类 planted mechanism

| Family | discover | explicit mapping | survivor | canonical cross-seed | behavior cross-seed |
|---|---:|---:|---:|---:|---:|
| CROSS_SECTIONAL_RELATIVE_ALPHA | PASS | PASS | PASS | PASS | PASS |
| MARKET_DIRECTIONAL_ALPHA | PASS | PASS | PASS | PASS | PASS |
| PERSISTENT_LOW_TURNOVER_ALPHA | PASS | PASS | PASS | PASS | PASS |
| SPARSE_EVENT_ALPHA | PASS | PASS | PASS | PASS | PASS |
| STATEFUL_HOLD_ALPHA | PASS | PASS | PASS | PASS | PASS |
| FUNDING_CARRY_ALPHA | PASS | PASS | PASS | PASS | PASS |
| REGIME_CONDITIONED_ALPHA | PASS | PASS | PASS | PASS | PASS |

### 9. 实际独立搜索行为

Capability harness 中实际运行且 behavior hash 区分的策略为 `canonical_typed_random`, `cem_like`, `uct_ucb_like`, `evolutionary`。`typed_random`/`typed_ast` 不被伪装成两个算法；历史 B1S 标签 `cem, uct_mcts, evolutionary` 继续标记为 `ALGORITHM_LABEL_DEGENERATE`。策略定义：`canonical_typed_random`=random_without_replacement_then_reshuffled_cycles; `cem_like`=full_coverage_then_elite_categorical_update; `uct_ucb_like`=one_visit_per_arm_then_ucb; `evolutionary`=full_coverage_then_aligned_parent_structural_gene_mutation。结构 proposal identity 与 evolutionary mutation 均排除 role_id 和 evidence label；mutation receipt 绑定 parent、child 与精确 changed genes；资格门槛要求至少两个不同的固定 seed。这里的 discovery 是固定小型 proposal grammar 的可达、评价与保留；每个策略先覆盖 grammar，再执行各自 adaptive update，不等于宽泛真实市场 generator search。

### 10. 是否可启动小型 development-only canary

技术上的固定有限 grammar capability-only 先决条件已满足；执行授权仍为 **NO**。`NEW_PERFORMANCE_SEARCH_FROZEN` 与 financial HOLD 未改变，因此本结果不自动启动真实 development search、接入新数据、打开 challenge/forward/recent/May stress、promotion 或跨 sprint memory。

## Qualification gate

| Criterion | Result | Evidence |
|---|---:|---|
| UNIQUE_CANONICAL_SEMANTICS | PASS | `CRYPTO_PRIMITIVE_SYNTHETIC_PARITY.json` |
| PRIMITIVE_SYNTHETIC_TESTS_PASS | PASS | `CRYPTO_PRIMITIVE_SYNTHETIC_PARITY.json` |
| THREE_EXPLICIT_MAPPINGS_PASS | PASS | `CRYPTO_MAPPING_SYNTHETIC_BEHAVIOR.json` |
| FINAL_POSITION_CAP_HOLDS | PASS | `CRYPTO_MAPPING_SYNTHETIC_BEHAVIOR.json` |
| ALIGNED_FEEDBACK_REJECTS_MAJOR_DECOYS | PASS | `CRYPTO_PROXY_STRICT_ALIGNMENT_SYNTHETIC.json` |
| SEVEN_PLANTED_FAMILIES_DISCOVERED_MAPPED_RETAINED | PASS | `CRYPTO_INSTRUMENT_CAPABILITY_MATRIX.csv` |
| NULL_WRONG_LAG_MAPPING_MISMATCH_HIGH_COST_HANDLED | PASS | `CRYPTO_PLANTED_MECHANISM_RESULTS.csv` |
| TWO_FIXED_SEEDS_REPRODUCE_CANONICAL_MECHANISM | PASS | `CRYPTO_INSTRUMENT_CAPABILITY_QUALIFICATION.json` |
| NO_SEALED_DATA_READ | PASS | `CRYPTO_INSTRUMENT_CAPABILITY_QUALIFICATION.json` |
| NO_REAL_PERFORMANCE_SEARCH | PASS | `CRYPTO_INSTRUMENT_CAPABILITY_QUALIFICATION.json` |

## 仍存 mismatch / 不能推出的结论

- 未做真实市场或 OOS 经济资格化，不能推出存在 alpha、可交易性或 external component increment。
- 5 bps 固定成本不含 spread、slippage、impact、fill 与 capacity。
- 普通标准误 LCB 未做时间依赖修正，只用于 deterministic planted gate。
- 历史 B1S/Epoch runner 保持冻结；本任务没有迁移或恢复真实 performance search。
- 发现资格只覆盖固定 finite proposal grammar，不证明完整历史 generator 或开放式表达空间的召回率。
- Legacy parity 的语义变化是显式兼容分类，不通过调参强求旧行为。

## Boundary record

- closed input surface: `PASS` (`STATIC_VERIFIED_CLOSED_INPUT_SURFACE`)
- synthetic run shape: `PASS`
- formal GraphSkill runtime trace supplied: `false`; this is static closed-input assurance.
- `new_performance_search_run`: `false`
- `sealed_data_read`: `false`
- `forward_opened`: `false`
- `challenge_opened`: `false`
- `recent_opened`: `false`
- `may_stress_opened`: `false`
- `new_data_integrated`: `false`
- `candidate_promoted`: `false`
- `cross_sprint_adaptive_memory_written`: `false`
- `historical_frontier_closure_rewritten`: `false`
