# ADR 0020: Evolution Policy Attribution V2.3

Status: Accepted for one development-only run on 2026-08-02.

## Decision

Run one fresh-state Search Engine V2.3 campaign on the existing 115-field
OI/mark x aggTrades carrier and the unchanged 786-mechanism V2.1 catalog. The
campaign trains expanded random and Mechanism Evolution at equal count for
16,000 strict candidates over two preregistered fresh seeds.

At checkpoint 007, evaluate four frozen, disjoint cohorts for each seed and
each 1h/4h horizon: random stratified, random train-top, Evolution stratified,
and Evolution train-top. Each cell contains 64 successful matched evaluations,
for 1,024 candidate-cohort evaluations. Random is a comparator only; it is not
required to cross the absolute profitability kill-line.

The validation separately attributes:

- proposal distribution: Evolution stratified minus random stratified;
- train ranker: Evolution train-top minus Evolution stratified;
- total policy: Evolution train-top minus random train-top.

Daily equal-weight primary, matched-increment, and control paths are persisted.
Each relative effect must have positive observed mean and positive fixed
seven-day paired-block-bootstrap 25th percentile for both primary net and
matched increment in every seed/horizon cell. Evolution train-top must also
pass the existing absolute validation kill-line in every cell. Only the full
joint pass releases two Evolution-only 2,000-candidate checkpoints.

## Boundaries

This decision creates no field, carrier, mechanism, AST, compiler, evaluator,
target, cost model, or persistent adaptive prior. It imports no V2.2 candidate,
reward, population, archive, RNG, transition, or policy state. It authorizes no
holdout/OOS, challenge, recent, stress, forward, promotion, rescue, tuning, or
additional seed campaign.

## Consequence

V2.3 can distinguish whether Evolution changes the proposal distribution,
whether train reward ranks that distribution out of sample, and whether the
combined policy replicates across two fresh seeds. A negative component closes
that component without reinterpreting random profitability as an engine gate.
