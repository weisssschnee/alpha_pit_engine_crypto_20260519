# Crypto Branch Evidence Map

Date: 2026-07-14
Audit scope: repository/history/runtime evidence recovery plus the minimal CURRENT/STATE correction warranted by the recovered facts. No performance evaluation, sealed-block read, data integration, candidate promotion, or manual RAW Graph edit was performed.

## Authority model

The repository has three distinct evidence roles. They must not be collapsed into one “current Epoch.”

| Role | Repository reference | Peeled commit | Authority now |
|---|---|---:|---|
| Immutable audit input: navigation and static inventory baseline | `main@09ac397c61b0b462497e9a8c0ea84981cc6a93f9` captured after fetch | `09ac397c61b0b462497e9a8c0ea84981cc6a93f9` | Authoritative for the code-navigation/static-inventory tree audited here |
| Accepted Frontier economic evidence line | `crypto-frontier-provenance-closure-20260714^{}` | `4726795f61052470d56e2d1475e4f6da9d262943` | Authoritative for Frontier reproduction, qualification, provenance closure, and `CURRENT_DATA_UNDERPOWERED` |
| Historical search/evaluation stages | explicit commits and peeled tags listed below | stage-specific | Immutable evidence lineage; not current authorization |

`crypto-frontier-provenance-closure-20260714` is an annotated tag object (`a9d4f0e8bdd010cf72528e9bc15bf44b052aab4e`) whose peeled commit is `4726795...`. The immutable `main@09ac397...` audit input and the closure tag deliberately contain different capabilities: the former carries navigation/static-inventory assets, while the latter carries the accepted Frontier execution and qualification assets. The audit commit built on `09ac397...` adds evidence and deterministic audit scripts; it does not copy closure-only execution code into main.

The required `git fetch --all --tags --prune` completed before the audit baseline was fixed and was repeated before closure. The verified pre-commit identities were `HEAD == origin/main == 09ac397...`, and the annotated closure tag peeled to `4726795...`.

## Stage map

| Stage | Evidence ref (peeled) | Run identity | Actual evidence role | Current interpretation |
|---|---|---|---|---|
| A7V1/A7V2 | `40d37cb710d22b60a8453f8a448f1216a8138c35` | `NOT_RECOVERED` | Built a 94-row opt-in registry, 5,211 derived-spec metadata rows, and seven real-panel no-search smoke features | Historical contract/smoke only; it authorized A7V3, not search or alpha proof |
| A7V3 | `c50c123df31d0717ce5f7017d0d5e0f312f53c37` | `NOT_RECOVERED` | Read registry/spec metadata and Parquet schema, then emitted 360 expression records | Expression-generation dry run; signals were `NOT_MATERIALIZED`; no replay/search |
| A7EFF2 | `evalreset-baseline-20260711-ac9fd24^{}` = `ac9fd24...` | `NOT_RECOVERED` | Release bundle with ten verified runtime-loaded fields and historical reward assets | Useful runtime lineage; superseded as current economic/action authority |
| B1S | `39d12c89a15802311cf9e1a108e9015b4315a653` | `20260711_b1s_canary_001` | Controlled canary with equal-budget global-top-K control | Partial canary; formal search stayed frozen |
| Epoch-0 | `46616450b1477d54eb45e47a42a8ed0541ce6cb7` | `20260711_crypto_nextgen_search_epoch0_001` | Frozen development search with typed/adaptive lanes | Completed with natural underfill and zero survivors; challenge recommendation superseded by closure review |
| Epoch-1 | `epoch1-failed-pre-strict-403b351^{}` = `403b351...` | `20260712_crypto_nextgen_epoch1_001` | Failed execution preserved as evidence | Failed before strict evaluation; no performance conclusion exists |
| Epoch-1R | `epoch1r-completed-natural-underfill-a9c119e^{}` = `a9c119e...` | `20260712_crypto_nextgen_epoch1r_001` | Admission repair and matched adaptive controls | Completed with natural underfill and zero survivors; all four adaptive lanes failed survivor-gain controls |
| Epoch-2 | `epoch2-partially-completed-02ac98e^{}` = `02ac98e...` | `20260712_crypto_epoch2_001` | Blocker-directed repair versus matched random controls | Zero survivors and no adaptive success; the claimed hybrid 60/40 contract was not preserved |
| Epoch-2B | `epoch2b-economic-bottleneck-5d8be3d^{}` = `5d8be3d...` | `20260712_crypto_epoch2b_audit_001` | Report-only audit over cached strict evidence | Its pivot recommendation is historical; later Frontier qualification does not prove data is the unique bottleneck |
| Frontier Arena | `crypto-frontier-provenance-closure-20260714^{}` = `4726795...` | `CRYPTO_FRONTIER_RESEARCH_V2_20260713` | Multi-paradigm architecture, native reproductions, bridge, and corrected Arena evidence | Architecture accepted development-only; economic status is `CURRENT_DATA_UNDERPOWERED` |
| Qlib v0.9.7 | same closure tag | `MICROSOFT_QLIB_V097_ALPHA158_LIGHTGBM_TOPKDROPOUT` | Native reproduction plus one frozen degeneracy repair and matched comparison | Original 0/0 was `MODEL_FIT_DEGENERATE`; repaired comparison differs but is `DATA_ADEQUACY_UNDERPOWERED` |
| DeepDow v0.2.3 | same closure tag | `DEEPDOW_V023_UPSTREAM_NATIVE_FRAMEWORK_RUN` | Native KeynesNet reproduction and asset-rotated matched control | Comparison is not exactly degenerate; only five independent five-day development blocks; `DATA_ADEQUACY_UNDERPOWERED` |

## Supersession rules used in the CSVs

`superseded=true` means that the row no longer supplies the current economic conclusion or action authorization. It does not erase the historical run fact. In particular:

- A7V1's pass still proves its registry/no-search smoke contract, but not that 94 fields were all runtime-loaded.
- A7V3's pass still proves expression/gate generation, but not numeric materialization, replay, search, or alpha.
- A7EFF2's ten loaded fields are a verified release fact, but “A7EFF2 is the current Crypto Epoch” is not a valid project-wide conclusion.
- Epoch-0's recorded `PREPARE_ROTATING_CHALLENGE_EPOCH` recommendation was overridden by its closure validation; challenge remains sealed.
- Epoch-2B remains a valid cached-evidence audit, but its `PIVOT_TO_NEW_MECHANISM_OR_DATA` route cannot be upgraded into “data is the unique bottleneck.”
- The unqualified Qlib 0/0 and any DeepDow informative-negative wording are superseded by the closure-tag qualifications.

## Current accepted result

The currently authoritative economic evidence is limited to:

```text
CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED
CURRENT_DATA_UNDERPOWERED
FINANCIAL_GATE_HOLD_RESEARCH
```

It supports two real native reproductions and a multi-paradigm development architecture. It does not support external component increment, OOS robustness, candidate promotion, a unique data bottleneck, exhausted mechanism space, or a claim that the market has no alpha.

The separate static qualification in this audit is `CRYPTO_SEARCH_INSTRUMENT_MISMATCH_CONFIRMED`, bounded to the recovered B1S/Epoch implementations, primitive semantics, and rank mapping. It qualifies the instrument; it does not replace the accepted economic result above.

## Machine-readable companions

- `runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_ACCEPTED_RESULT_TIMELINE.csv`
- `runtime/crypto_latest_evidence_independent_audit_20260714/CRYPTO_RUNTIME_STAGE_LINEAGE.csv`

Both files use `NOT_RECOVERED`, `UNKNOWN`, `NOT_MATERIALIZED`, or `NOT_APPLICABLE` rather than filling gaps by inference.

## 2026-07-18 residual / orthogonal / score-path closure

The repository already contains implemented residual/orthogonal variants and the current mapping/cost primitives. Renaming or wrapping these pieces is maintenance, not a new research result.

| Existing capability | Current asset | Qualified scope |
|---|---|---|
| Cross-fitted baseline residual | `alphafactory_crypto/field_information.py::cross_fitted_ridge_residual` | Residual-information diagnosis |
| Frozen-baseline residual learner | `alphafactory_crypto/latent_adaptive/experiment.py`, Arm D | TCN-specific implementation pattern; development negative under its fixed zero-net, full-L1, 5 bps evaluator |
| Full/control prediction, weight, direct-delta, causal-delta, sticky, and calibration diagnostics | `alphafactory_crypto/broad_information_arena.py` plus the purged Broad replay | Reusable matched diagnostics; no stable economic increment |
| Canonical portfolio mapping | `alphafactory_crypto/instrument_capability/mapping.py` | Current explicit mapping authority |
| Full-L1 turnover and cost | `alphafactory_crypto/instrument_canary/evaluator.py` | Current strict evaluator |
| Orthogonal score packet and book replay | CORE43E, CORE44E, CORE45E reports and scripts | Historical reference implementation only |

Current supersession order is:

```text
purged Broad replay
  > unpurged Broad Arena / mapping-repair / sticky artifacts

current cost authority:
  explicit mapping + full-L1 evaluator

historical non-comparable cost evidence:
  CORE45E abs(book_weight) * 5 bps

current sealed-role boundaries
  > historical CORE43-47 and archived A7H0 role usage
```

The executed variants established reusable implementation capability, not stable economic increment. The CORE43-47 chain remains `REFERENCE_ONLY` under its inherited historical split and replay contracts; CORE45E specifically uses the obsolete non-turnover cost rule. Archived A7H0 additionally reads roles that are now sealed. Within this residual/orthogonal/score-path closure, the identified small gaps are an executable label-ranked ceiling, a typed ordering-score-versus-calibrated-edge distinction, and a compact transfer table. These diagnostics must not become standalone projects; implement only the subset required by the relational policy's matched controls.
