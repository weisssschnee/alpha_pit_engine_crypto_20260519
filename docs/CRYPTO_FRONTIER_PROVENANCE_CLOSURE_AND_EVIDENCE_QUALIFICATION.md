# Crypto Frontier provenance closure and evidence qualification

Pre-push status: `ARCHITECTURE_EXECUTION_COMPLETED` / `REPOSITORY_PROVENANCE_CLOSURE_PENDING`.

Economic conclusion: `CURRENT_DATA_UNDERPOWERED`.

## Qlib qualification

The historical full/control `0/0` comparison was not an informative negative.

- Full input contained 158 features; control contained 13. The 145 full-only features were retained by the processors, had positive variance and changed through time. The handler and matrix identities were distinct.
- Both original fits had flat train/validation L2, zero-split models, constant predictions and exactly identical positions. The paired zero was exact, not report rounding.
- Historical classification: `MODEL_FIT_DEGENERATE`, followed by `PORTFOLIO_MAPPING_COLLAPSE`.

One repair was frozen before observing repaired metrics: set only the CSI300-tuned `lambda_l1` and `lambda_l2` to zero. Features, label, splits, seed, two-fit budget, maximum boosting rounds, early stopping, TopK mapping, executor and costs remained unchanged. No parameter search was run.

The repair resolved the degeneracy:

- Full/control retained trees contain 25 and 17 split nodes.
- Prediction Pearson correlation is `0.0602`; rank correlation is `0.1779`.
- All 240 paired predictions differ; maximum absolute difference is `0.3715`.
- Mean daily portfolio L1 difference is `1.3824`; no date has identical weights.
- Corrected paired net increment mean is `0.002570`, but its 95% block-bootstrap lower bound is `-0.003135` over only 23 common dates.

Repair status: `EXTERNAL_PARADIGM_COMPARISON_DEGENERATE_FIXED`.

Economic status: `DATA_ADEQUACY_UNDERPOWERED`, not `INFORMATIVE_NEGATIVE` and not an observed development increment.

## DeepDow qualification

The four original-budget fits were rerun without semantic changes while persisting gradients, structured loss history, initial/final model identities, parameter deltas and per-seed weights.

- Tensor: `X=(156,4,20,10)`, `y=(156,4,5,10)`; train/valid/development windows are `84/24/24`.
- Cross-split target overlap pairs: zero. Adjacent samples still share 19/20 input days and 4/5 target days.
- Development contains only five non-overlapping five-day target blocks.
- Minimum final-versus-initial parameter L2 change is `0.3167`; minimum observed gradient L2 norm is `0.0129`.
- Ensemble challenger/control mean daily weight L1 difference is `0.0962`; their paths differ on every common date.
- The long-only allocator is compressed toward equal weight but not collapsed: challenger HHI is `0.100674` versus `0.100000` for one-over-N, and mean daily L1 distance from one-over-N is `0.0714`.
- Challenger/control gross means are `-0.00591560/-0.00591583`; mean costs are `2.338e-5/2.307e-5`; paired net mean is `-8.15e-8` with 95% LCB `-2.36e-4`.

Classification: `DATA_ADEQUACY_UNDERPOWERED`. The evidence rejects exact comparison, model-fit and portfolio-mapping degeneracy, but cannot support an informative negative.

## Frozen Data Adequacy Gate

Minimums are registered in `config/crypto_frontier_evidence_qualification_v1.json` before any new release is evaluated.

| Condition | Qlib daily | DeepDow direct five-day |
|---|---:|---:|
| Development dates | 60 | 60 |
| Training samples | 5,000 rows | 500 windows |
| Cross-sectional assets | 20 | 10 |
| Feature non-null rate | 95% | 100% |
| Positive-variance feature/channel fraction | 90% | 100% |
| History | 365 days | 600 days |
| Label support | 95% | 100% |
| Turnover observations | 60 | 60 |
| Independent evaluation blocks | 12 five-day blocks | 12 five-day blocks |

Current Qlib fails dates, samples, assets, one long-window feature's non-null minimum, history, turnover and independent blocks. DeepDow fails dates, samples, history, turnover and independent blocks. A failed gate must be reported as `DATA_ADEQUACY_UNDERPOWERED`; the external paradigm cannot be labelled failed.

## Corrected Arena status

The six-system Arena keeps the same 23 DEVELOPMENT dates, one-day delayed common bridge and 5 bps L1 turnover cost.

| Paired comparison | Mean net increment | 95% LCB | Qualification |
|---|---:|---:|---|
| Repaired Qlib full minus 13-feature control | 0.002570 | -0.003135 | `DATA_ADEQUACY_UNDERPOWERED` |
| DeepDow flow minus rotated-flow control | -0.0000000815 | -0.000236 | `DATA_ADEQUACY_UNDERPOWERED` |

No candidate or external component is promoted.

## New-data direct activation

Run:

```text
python scripts/crypto_frontier_evidence_qualification.py activation-plan --manifest <release-manifest>
```

The entry first runs the existing `ingress-preflight`, then applies the frozen adequacy profiles, selects at most the two highest information-match external paradigms and adds the internal baseline. It authorizes a fixed development-only Arena only when both external paradigms pass. Otherwise it returns `DATA_ADEQUACY_UNDERPOWERED` and `NO_LARGE_EXPERIMENT`.

## Bias and promotion boundary

The persisted bias audit decision is `HOLD_RESEARCH`. Date alignment and delayed labels pass for the stated development scope, and native/common costs are applied to post-mapping turnover. However, there is no opened OOS window, the fixed core10 selection cannot support broad-universe claims, only 23 turnover observations exist, and there are only four Qlib or five DeepDow independent evaluation blocks. This closure is reproducible evidence qualification, not KEEP or promotion evidence.

Challenge, forward, recent, May stress, candidate promotion, new performance search and cross-sprint adaptive memory remain disabled.

## Repository evidence contract

- The prior 122-artifact bundle remains immutable. Its committed index recomputes bundle SHA256 `99C0DACAF12F17DA6B7705DDBFCE9BAD996143082301F47BCA7E690071140EF2`.
- Qualification outputs use a separate content-hash manifest and preserve the failed pre-training entrypoint attempt, successful six-fit identity and no-fit classification finalization.
- Qlib provider binaries, handler pickles, source CSV cache, MLflow/TensorBoard output and runner logs are regenerable caches or volatile execution evidence and are not closure source artifacts.
- The closure does not modify the architecture-control registry or generated project graph.
