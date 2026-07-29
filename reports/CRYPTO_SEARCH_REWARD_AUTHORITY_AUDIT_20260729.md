# Crypto Search Reward Authority Audit

- Production source: `1066153eaa72fd6036a81a31583f4666105adffc`
- Scope: Search Engine V1 reward, ordering, archive, matched attribution, and cost semantics
- Market candidate evaluations: `0`
- New search budget: `0`
- Tests: `295 passed`, one pre-existing NumPy warning
- Decision: `HOLD_RESEARCH`

## Audit result

The central allegation is confirmed: Search Engine V1 used `pair_reward`, the
minimum normalized distance to strict matched-sleeve feasibility thresholds,
as the sole ordering authority for CEM elites, Evolution parents and
replacement, Behavior Archive champions, and arm quality gates.

`pair_reward` is not a portfolio reward. It has no portfolio Sortino objective
and cannot establish that V1.1-V1.3 policies became better at finding Alpha.
Those campaigns remain engineering and matched-feasibility evidence only.

The cost allegation requires correction. Current Search Engine cost is:

```text
full_L1_turnover * one_side_cost
```

Phase3CM long-short cost is:

```text
2 * one_way_turnover * one_side_cost
```

With `one_way_turnover = full_L1_turnover / 2`, these are identical. The
A7Reward-1 implementation uses a different one-way accounting contract; it
does not prove that Search Engine cost should be halved. Fixed-cost turnover
and cost thresholds are redundant at their zero boundary, but they now remain
matched diagnostics and do not order search.

## Implemented authority repair

The existing `pair18m` evaluator now also produces:

```text
search_reward =
    0.55 * train day Sortino
  + 0.25 * selected-horizon worst-horizon day Sortino
  + 0.20 * deterministic bootstrap Sortino p25
  - Phase3CM one-way turnover penalty
```

`CandidateSpec` contains one selected horizon, so the worst-horizon term equals
that selected-horizon Sortino. Cross-horizon instability is explicitly absent;
the implementation does not fabricate a second horizon evaluation.

The following now order only by `search_reward`:

- CEM elite admission and updates
- Evolution tournament, family replacement, and bounded population
- Behavior Archive family champion replacement
- equal-count mean and top-decile quality metrics
- adaptive arm diagnostic/exit gates

`pair_reward`, matched-positive status, strict margins, turnover, cost,
concentration, and support remain persisted attribution/execution diagnostics.
Legacy archive or checkpoint state without `search_reward` fails closed.
Behavior identity excludes both reward fields.

## Evidence boundary

The V1.1-V1.4 ledgers do not persist enough complete daily primary-portfolio
return data to reconstruct the new reward without market reevaluation.
Therefore:

- no historical reward is rewritten;
- no old CEM/Evolution conclusion is relabeled as economic evidence;
- V1.4 `0 matched-positive` remains a strict attribution result, not proof of
  zero portfolio signal;
- the `661` gross-positive and `32` net-positive replay observations remain
  diagnostics, not candidates or promotion evidence.

Search Engine V1 still lacks a formal validation kill-line. Its historical
report-only block is not validation and remains outside optimizer feedback.
Before any fresh adaptive campaign, a new contract must freeze:

1. train-only search reward;
2. a distinct validation split used only for budget/kill decisions;
3. read-only holdout;
4. tradable venue-specific execution and cost;
5. fresh policy/archive/checkpoint state.

No OOS, challenge, recent, May-stress, forward, promotion, latent training, or
new Arena is authorized by this audit.

