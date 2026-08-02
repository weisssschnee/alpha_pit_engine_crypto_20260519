# Crypto Search Engine V2.2 Source Gap Report

The repository already contains the required 115-field carrier, 786 compiled
mechanisms, typed proposal policies, matched evaluator, crypto reward, behavior
archive, deterministic receipts, and exact checkpoint restore. No new search
grammar or data adapter is required.

The remaining source gap is orchestration-only:

1. a fresh V2.2 campaign/seed/receipt identity;
2. two-arm staged allocation with an 8k train gate and conditional 12k
   continuation;
3. the absolute positive floor applied to Evolution rather than its random
   comparator;
4. validation control-arm identity made receipt-bound instead of hard-coded to
   `canonical_typed_random`;
5. V2.2 terminal decisions and artifact checker for both early-stop and 20k
   completion.

Graph is not refreshed during implementation or execution. Any final durable
capability evidence updates the existing CURRENT search capability node only.
