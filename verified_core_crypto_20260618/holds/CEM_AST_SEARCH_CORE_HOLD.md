# CEM / AST / MCTS Search Core Hold

## Decision

`HOLD_CEM_AST_MCTS_SEARCH_CORE_NOT_VERIFIED`

## Reason

The current crypto repo contains typed AST representation, AST parser/render
logic, feature subgraph registry, search-space memory, and queue generation
scripts. Those are necessary support layers. They are not, by themselves, a
verified search optimizer.

Current large-search runs are best described as:

```text
queue construction
-> proxy reward sharding
-> strict reward sharding
-> aggregation
-> optional feedback-prior queue construction
```

That is useful, but it is not a verified CEM/AST/MCTS core.

## Requirement To Promote

To leave HOLD, a search core must provide:

- explicit optimizer state
- candidate origin tracking
- reward feedback update rule
- exploration/exploitation budget accounting
- checkpoint and resume semantics
- automatic proxy-to-strict validation handoff
- manifest-first aggregation
- no direct use of raw selected queues without strict reward acceptance

## Immediate Recommendation

Keep current queue/proxy/reward pipeline running only as a controlled exploration
workflow. Do not label it CEM, AST search, or MCTS until the optimizer loop is
implemented and audited.

