# Crypto AlphaFactory current state

Last updated: 2026-08-13 Asia/Hong_Kong

## Current phase

`CRYPTO_TEMPORAL_TARGETED_P1_P4_BASIN_DEEPENING_R2_AUTHORIZED_NOT_STARTED`

Current user decision authorizes exactly one fresh PC2 r2 train-only targeted
basin-deepening run. Its execution implementation is frozen at
`e05efc63cff183e1d223ee2b02e56070bec1c7bb`; the authorization-only successor
may change only the one-time receipt, this state, the thin CURRENT experiment
projection, and the independent control checker. Every execution component is
bound byte-for-byte to e05. The new workspace/runtime is distinct from r1 and
may import only the hash-bound 50,000-row development ledger, its 302
matched-positive rows, and the reconstructed 23-basin / 228-parent frozen pool
with SHA256
`A08112ED1765A432D15D259A70F308C2DE5BA7B617D294BFB8349020EC61AA49`.

The frozen run contract is P1/P4 only, P2/P3 strict zero, and
Random/CEM/Evolution 20/20/60. Evolution uses preregistered sampling
probabilities 60% parameter mutation, 10% mechanism mutation and 30% crossover;
an unavailable or failed legal same-basin crossover may fall back to parameter
mutation. The independent control checker deterministically replays the frozen
policy to report requested and realized operation, fallback count/rate/reason,
and proposal/strict/matched-positive/basin contribution. Children cannot enter
the frozen parent pool. The run stops at the preregistered 20k saturation
decision or the unconditional 30k strict cap. Validation, OOS, holdout, forward,
promotion, sealed reads and automatic follow-up remain forbidden.

No market read or candidate evaluation has occurred under r2 authorization.
Launch is allowed only after the committed checkout is clean and tracking,
component SHA binding, exact baseline recovery and frozen-pool reconstruction
all independently pass before market access.

## Previous phase: r1 system-invalid closure

The sole current-user-authorized targeted P1/P4 PC2 run is consumed and closed
as `SYSTEM_INVALID`. Task `job_20260813_122829_4a039f` reached a last producer
heartbeat of 13,691 strict rows from 23,671 generation attempts before operator
termination. An independent audit of the exact, restore-verified and contiguous
10,000-row checkpoint found 77 P2 and 124 P3 rows even though both families were
paused. All 201 out-of-scope rows came from the Random arm's inherited
`EXTENSIBLE_MECHANISM_TYPED_RANDOM` diagnostic route. The task exited 1 at
15:36:54 HKT and no target-workspace process remains.

Validation, OOS and sealed reads are all zero. The 10k checkpoint ledger hash
matches its manifest, but the whole runtime is partial and has no normal final
decision, run manifest or PASS checker. The independent scope audit is `FAIL`;
the one-time receipt now has `run_authorized=false`, outcome `SYSTEM_INVALID`
and `automatic_next_run_started=false`. Contaminated checkpoint economics are
retained only as diagnostics and cannot support a targeted-deepening decision.

Source now prevents targeted mode from substituting the broad-search
out-of-scope Random diagnostic policy while preserving broad-mode behavior. An
independent ledger scope-audit script and system-invalid receipt-consumption
path close the failure without market reevaluation. Temporal regression tests
pass 89/89 and focused closure tests pass 5/5. No replacement run, validation,
OOS, holdout, forward read, promotion, Alpha qualification, pocket gate or new
algorithm is authorized. Authoritative report:
`reports/CRYPTO_TEMPORAL_TARGETED_P1_P4_BASIN_DEEPENING_V1_20260813r1.md`.

The only allowed next decision from this run is `SYSTEM_INVALID`.

## Preceding completed phase

`CRYPTO_TEMPORAL_LARGE_DEVELOPMENT_EXPANSION_COMPLETE_CONTINUE_DISCOVERY_ALPHA_HOLD`

The independently authorized fresh-state Temporal Program expansion is complete
and consumed. PC2 task `job_20260812_202835_6c7c25` evaluated exactly 50,000
train-only strict candidates from 90,692 attempts under the frozen
Random/CEM/Evolution 20/20/60 allocation, all four existing program families,
25 restore-verified checkpoints and the exact 50,000 mechanical stop. Ten
workers ran without memory fallback; validation, OOS and sealed reads are zero.
After correcting a checker-only arm-state expectation (Random is a fixed control,
not an adaptive state entry), the same immutable runtime passes PC2 independent
artifact-integrity and run-validity checks.

The historical report's 12,406 and 86 counts are baseline-new dual-positive and
matched-positive `behavior_family_id` counts, not independent economic
opportunities. A persisted-fingerprint-only recomputation of the 302
matched-positive rows yields 59/47/38/33 diagnostic economic clusters at
similarity 0.95/0.90/0.85/0.80, economic effective rank 3.6953, and PCA
dimensions 2/4/6 for 50%/80%/90% variance. The broad run therefore expanded
real economic breadth, but not to 86 independent Alpha. Evolution supplied 301
matched-positive rows (10.03/1k), versus CEM one (0.1/1k) and Random zero, while
its dual-positive and replication yields were 447.77/1k and 163.93/1k. Its
advantage came from parameter mutation and crossover; their historical
"new cluster" fields remain behavior-family diagnostics. Mechanism mutation
crossed program basins but produced zero matched positives.

This is credible development discovery, not Alpha qualification or migration
proof. The durable next decision is `CONTINUE_DEVELOPMENT_DISCOVERY`, but no
automatic next search, validation, OOS, promotion, grammar/evaluator change, or
new Arena is authorized by this closure. Authoritative report:
`reports/CRYPTO_TEMPORAL_LARGE_DEVELOPMENT_EXPANSION_V1_20260812r1.md`.
Retained local top-level runtime evidence:
`runtime/crypto_temporal_large_development_expansion_v1_20260812r1`; the full
7.85 GB checkpoint payload and process evidence remain retained on PC2 after
the PC2 checker verified every manifest-bound file.

The preceding completed phase was:

`CRYPTO_TEMPORAL_POLICY_VALIDATION_COMPLETE_FIXED_20_20_60_DEVELOPMENT_FLOW_ALPHA_HOLD`

The one pre-registered PC2 development validation is complete and consumed.
Its frozen cohort contains 360 candidates, exactly 120 each from Random, CEM,
and Evolution, with no candidate generation, optimizer feedback, Archive write,
backfill, OOS, holdout, or promotion. The completed full pass plus three equal
validation blocks produce exactly 1,440 pair evaluations. Independent PC2 and
local checkers pass and the final decision is
`QUALIFY_20_20_60_FIXED_DEVELOPMENT_FLOW`.

The effective train/validation split remains balanced and unchanged: 1,523
train hours (`51.09%`) and 1,458 validation hours (`48.91%`). Validation is
three equal 482-hour effective blocks, each with the frozen 6-hour tail purge;
the 720-hour feature warmup precedes evaluation and contributes no label or
metric rows.

Evolution retains the strongest end-to-end migrated replicated-cluster yield:
`50.2/1k`, versus CEM `20.1875/1k` and Random `15.4167/1k`. It also has 53/120
full-window dual-net-positive candidates and three validation matched-positive
candidates. Its candidate-level 2-of-3 replication rate is lower than Random
and CEM (`10.0%` versus `16.67%` and `14.17%`), but the frozen policy gate
multiplies train discovery density by migration and passes all family, lane,
program-basin, integrity, and split gates. This qualifies the existing fixed
development allocation only: Random/CEM/Evolution is now 2,000/2,000/6,000 per
10,000 strict. It is not an Alpha qualification, OOS result, or promotion, and
it starts no automatic search.

The first repair was required because the block runner reused the full-window
economic receipt for subblocks. The second was aggregation-only: pass ledgers
did not repeat frozen `program_family_id`/`program_id`/lane lineage. Both repairs
were fail-closed and reused the already completed hash-bound full pass; the final
aggregation repair performed zero market evaluations. Authoritative report:
`reports/CRYPTO_TEMPORAL_POLICY_VALIDATION_V1_20260812r2.md`. Machine decision:
`runtime/crypto_temporal_policy_validation_v1_20260812r2/final_decision.json`.

The preceding completed phase was:

`CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_COMPLETE_SEARCH_POLICY_EVIDENCE_PASS_ALPHA_HOLD`

The current-user-authorized schema-2 successor completed on PC2 as task
`job_20260811_233723_fbaac8` at exact producer
`d8106f271f86886621fd084c542671e23b695864`. It restored only the verified
30,000-row prefix, evaluated exactly 20,000 additional train-only strict rows,
and stopped mechanically at 50,000 cumulative strict. Its economic-independence
audit qualified Evolution as a productive development search policy under the
frozen contract while retaining `ALPHA_QUALIFICATION_HOLD`. Its authoritative
closure report is
`reports/CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_CLOSURE_20260812.md`.

The preceding repaired boundary was:

`CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_PRE_MARKET_DEPLOYMENT_INVALID_SOURCE_REPAIR_IMPLEMENTED_REPLACEMENT_NOT_AUTHORIZED`

The sole authorized PC2 task `job_20260811_212229_f6d45d` wrote the one-time
launch claim and then exited before reading a market array or evaluating a
candidate. The failed runtime contains exactly
`successor_launch_claim.json`; its SHA256 is
`09D63C46C65037823776F91DD2E467BD0CE882C007715E98DE105AA143A0550A` and
records zero market-array reads, zero candidate evaluations and zero sealed
reads. The task-level status is `FAILED` with exit code 1. The exception is a
`FileNotFoundError` for the manifest-bound but Git-excluded 115-field cache at
`.cache/crypto_search_engine_v1_4/oi_mark_x_aggtrades_115/metadata.json` in the
new PC2 checkout. No successor process remains active.

This is a pre-market deployment-portability invalid run, not development
economics and not a consumed candidate budget. The old runtime must not be
resumed or deleted to manufacture freshness. Source now verifies the tracked
carrier manifest, cache identity and the complete required directory bundle
before a successor launch claim can be written. The failure identity is
committed at
`config/crypto_temporal_program_30k_to_50k_successor_v1_pre_market_failure.json`.
The repair does not alter target, mapping, cost, reward, evaluator, prefix,
Random seeds, CEM/Evolution state, allocation, tranche gates, budget or sealed
boundaries. A market run remains absent. One source-only replacement requires
an explicit new schema-2 authorization bound to this failed claim, the repaired
implementation, a distinct PC2 runtime and the exact manifest-verified cache.

The preceding authorized boundary was:

`CRYPTO_TEMPORAL_30K_TO_50K_SUCCESSOR_AUTHORIZED_NOT_STARTED`

Current user decision `GO_WITH_LIMITED_SEARCH_POLICY_CHANGE` authorizes exactly
one schema-2 PC2 `30K_TO_50K_SUCCESSOR` development continuation. The committed
implementation remains `b5985037492a81198953629480c75db12e2a8afd`; the
materialized one-time authorization is bound to branch
`experiment/crypto-p4-pocket-validation-v1-20260811`, PC2 host
`desktop-a2h3a2g`, workspace
`C:\HermesWorker\workspace\crypto_temporal_successor_b5985037`, runtime
`crypto_temporal_program_30k_to_50k_successor_v1_20260811`, and authorization
SHA256 `F125061CD9DBFA0CAF2FFAC34B2479F370C600B6CF73A61352A309278DB5A38A`.

PC2 physical preflight found no active Python/search process, verified the
retained source file sizes and exact receipt-bound hashes, and returned
`SUCCESSOR_PREFLIGHT_PASS` from the authorized reconstruction path. Only
`completion_ordinal <= 30000` contributes state; the historical suffix from
30,001 contributes zero. Fresh Random remains fresh, while CEM and Evolution
restore only the verified reconstructed bundle. Allocation remains 20% Random,
20% CEM and 60% Evolution, with one decision every 5,000 additional strict and
an unconditional cumulative 50,000 mechanical hard stop. Market reads,
candidate evaluations, sealed reads and runtime-root creation remain zero at
this authorization boundary.

Validation, OOS, holdout, forward reads, promotion, rescue, reseed, tuning,
automatic expansion and a second successor remain forbidden. Authorization
does not promote the experimental node or fill any global economic authority;
the schema-2 target, optimizer-reward, execution-price and cost bindings are
receipt-scoped NON_FORMAL exceptions for this run only. At that boundary the
next action was to commit/push the authorization and launch once; the
pre-market failure and replacement requirement above supersede that action.

The preceding completed phase was:

`CRYPTO_P4_MECHANISM_POCKET_REPLACEMENT_PRE_CANDIDATE_ENGINE_RUN_INVALID_RESEARCH_HOLD`

The sole source-repaired replacement authorization is consumed and closed
without an economic evaluation. Exact producer
`d6a5f7907e74868787d3d70a4736868333c3c26f` and PC2 detached task
`job_20260811_101545_05f601` reused the hash-bound completed OI payload without
redownloading it. Binance aggTrades processing reached `200/200` symbols with
zero symbol failures and the frozen network concurrency of three. Package
assembly then failed because the required monthly object manifest
`symbol=BTCUSDT/2026-08.json` was absent. Carrier preparation and the frozen
80-candidate gate never started; strict evaluated count is zero.

PC2 and local independent checkers correctly return
`FAIL_MISSING_RUN_MANIFEST`. A separate pre-candidate contract audit also found
that 22 of the 80 frozen candidates require a complete 720-hour rolling window
while the receipt declares only 336 hours of pre-evaluation warmup. All 22 are
near-miss controls (16 Evolution and 6 Random), so evaluating this frozen
cohort would create asymmetric materialization support even if package
assembly were repaired.

This establishes a `PRE_CANDIDATE_ENGINE_RUN_INVALID` source-package and
admission-contract failure, not a failed P4, Evolution, matched-control, cost,
reward, stability or Alpha result. Candidate generation, optimizer feedback,
policy memory, Archive writes, automatic expansion and OOS reads remained
zero/false. The replacement receipt is consumed with `run_authorized=false`;
no second replacement, continuation, rescue, validation, OOS, promotion or new
Arena is authorized. The immutable downloaded inputs are retained as evidence.

The preceding completed phase was:

`CRYPTO_TEMPORAL_MAPPING_THROUGHPUT_QUALIFIED_RESEARCH_HOLD`

The one authorized post-mapping-repair checkpoint-only PC2 qualification is
consumed and closed. Exact producer
`49010c89e840320a873accdb27fa15fa6ea9c320` and detached task
`job_20260810_002520_d1ebdc` completed exactly 2,000 strict evaluations from
2,061 generation attempts as 1,000 matched static/temporal pairs. The run wrote
one restore-verified checkpoint, produced 1,993 behavior families, observed all
ten workers and ten submitted tasks per full batch, and recorded zero system
errors, zero sealed reads, zero validation/OOS/promotion reads, and no memory
fallback.

Realized end-to-end throughput was `3,983.8184 strict/hour`, above the frozen
`2,777.7778` floor by 43.4% and 1.97x the preceding q2 result. Active wall for
2,000 strict fell from 3,556.4084 to 1,807.2817 seconds. On a consistent
pairwise median, successful-pair wall fell from 18.2825 to 9.2357 seconds and
combined static/temporal mapping fell from 13.8233 to 3.8058 seconds. The new
rejected ledger also retains CPU, wall, RSS and private-byte evidence for 755
worker-side rejects. PC2 and local independent checkers pass artifact integrity
and run validity with zero errors and reconcile all attempts.

The producer correctly stopped at checkpoint 0 with
`CHECKPOINT_ONLY_QUALIFICATION_COMPLETE`; code and receipt prohibited release
to the 10,000-strict family gate. `adaptive_stage_started=false` remained
frozen, parameters and seed were unchanged, and no prior runtime, policy,
Archive, or candidates were imported. The preceding remote transport failure
`job_20260810_001417_9eb7b3` occurred before runtime creation, market read, or
candidate evaluation because its receipt bound an incorrect implementation
SHA; its consumed failure receipt is retained, and source-smoke now validates
the active authorization receipt before launch.

The durable result is an execution-capacity qualification, not an economic or
optimizer qualification. Zero matched-positive rows in this capped cohort are
explicitly non-interpretable for research. No continuation, second search,
validation, OOS, promotion, challenge, new Arena, reseed, tuning, or sealed read
is authorized. Research remains HOLD.

The preceding completed phase was:

`CRYPTO_TEMPORAL_STAGE0_QUALIFICATION_THROUGHPUT_GATE_FAILED_RESEARCH_HOLD`

The one authorized post-repair fresh-state Stage-0 qualification is consumed
and closed. Exact PC2 producer
`f846eb04c023fdf20a5130b40d7846a1ccdad3df` and detached task
`job_20260809_190549_48e93e` completed exactly 2,000 strict evaluations from
2,061 generation attempts as 1,000 matched static/temporal pairs. The run wrote
restore-verified `checkpoint_000` plus the terminal budget checkpoint, produced
1,993 behavior families, and recorded zero system errors, zero sealed reads,
zero validation/OOS/promotion reads, and zero matched-positive candidates.

The source repair is now runtime-observed: all ten worker initializers were
present, the producer submitted a maximum of ten paired tasks per batch, and
the final accounting records 180 batches and 1,755 submitted paired tasks with
no memory fallback. Full worker utilization therefore no longer has the prior
systematic half-pool defect. Realized end-to-end throughput was nevertheless
only `2,024.4987 strict/hour`, below the frozen `2,777.7778` floor. The producer
correctly returned
`ENGINE_BUDGET_EXHAUSTED_THROUGHPUT_FLOOR` at checkpoint 0; the 10,000-strict
family gate was never reached and `adaptive_stage_started=false` remained
frozen. This is about 15.7% faster than the prior 1,749.5621 strict/hour cohort,
but it does not qualify the repaired program for expansion.

The preceding q1 deployment-bound runtime is preserved as
`ENGINE_RUN_INVALID` with 11 raw attempts and zero strict evaluations because
the target cache was absent from the deployed checkout. It is not resumed or
interpreted. The replacement q2 receipt kept the seed, market, evaluator,
mapping, cost, and budget contracts unchanged and imported no runtime, policy,
Archive, or candidate state. Independent PC2 and local checkers pass artifact
integrity and run validity with zero errors, reconcile all 2,061 attempts, and
the one-time receipt is consumed with `run_authorized=false`.

The durable result is a throughput qualification failure, not a temporal
mechanism or optimizer verdict. Zero matched-positive rows from this partial
cohort cannot reject the four program families; CEM and Evolution did not run.
No restart, rescue, reseed, tuning, continuation, validation, OOS, promotion,
new Arena, or sealed read is authorized. The existing
`real_policy_upgrade_canary` CURRENT role is updated in place; no Graph node is
added.

A zero-market-budget post-repair performance attribution is now complete at
`reports/CRYPTO_TEMPORAL_PROGRAM_STAGE0_POST_REPAIR_PERFORMANCE_ATTRIBUTION_20260809.md`.
It confirms that coordinator fill is no longer the primary defect: 173 of 180
batches submitted all ten tasks and median batch overhead beyond the slowest
successful task was only `0.153 s`. The remaining measured hot path is portfolio
mapping. Successful-pair process CPU changed only +1.2% from r1 to q2, while
pair wall rose 71.9% and combined static/temporal mapping consumed `11.8206 s`
or 69.64% of successful-pair wall. P2/P4 also consumed 70.26% of raw attempts
and 85.96% of pair rejects to fill equal family quotas; 622 of 755 pair rejects
were behavior-equality failures reached after mapping work. It prescribed
a source-only, semantics-parity mapping hot-path repair, not another market run,
worker downgrade, behavior-gate weakening, reward change, or dependency install.

That source-only repair is now complete. On the frozen `121 x 1,523`, seed
`20260809` local input, all pre/post hashes remained exact for weights,
feasibility, transition reasons, diagnostics and behavior provenance.
Same-process alternating-order five-run medians improved time-series directional
mapping from 0.8899 to 0.2493 seconds (3.57x), and sparse event/carry from
0.7221 to 0.2752 seconds (2.62x); cross-sectional mapping was unchanged within
local noise.
Future rejected worker tasks now retain their already-computed CPU, wall and
memory fields in the existing rejected ledger. Focused tests pass 47/47 and the
full suite passes 518/518 with the existing NumPy warning. This is static and
local-benchmark verification, not PC2 throughput qualification or new economic
evidence. No market run, validation, OOS, optimizer, mapping-contract, reward,
cost, gate, budget, worker-count, or dependency change was made or authorized.

The preceding completed phase was:

`CRYPTO_SEARCH_TEMPORAL_ACTIVATION_V1_STOPPED_NOT_SUPPORTED_RESEARCH_HOLD`

The one authorized canonical temporal-primitive activation gate is consumed and
closed. Exact PC2 producer `07247878576daf56b66b3fb251a8d9faf02b3b6a`
completed tranche 0 with exactly 2,048 strict evaluations representing 1,024
matched static/temporal pairs, one atomic restore-verified checkpoint, 10
workers, zero sealed reads, and no validation, OOS, holdout, or optimizer
feedback. The frozen continuation gate returned
`STOP_TEMPORAL_NOT_SUPPORTED`; no later-tranche proposals were generated and
the 8,192 maximum was not released.

Canonical temporal transforms did not improve the frozen static comparator.
The native paired worst-axis-net delta median was
`-0.0000033632484912667765`, temporal win fraction was `0.46875`, dual-axis
net-positive rate fell from `0.076171875` to `0.0732421875`, 2-of-3 block
replication fell from `0.021484375` to `0.017578125`, and both representations
had one all-three-block-positive pair and zero matched-positive candidates.
The temporal cost-sign-kill rate was also slightly higher (`0.8407643312`
versus `0.8378378378`). Persistence was the strongest primitive median, but the
leave-best-template and leave-best-field-family breadth checks remained
negative. The durable decision is
`CANONICAL_TEMPORAL_PRIMITIVE_ACTIVATION_NOT_SUPPORTED`; temporal Evolution is
not authorized.

The original post-run checker exposed a deterministic self-hash defect: it
rehashed the receipt including its own `receipt_sha256`, so it could never
equal the pre-self-hash binding. Checker-only repair
`12cfc9bd07a6aae06df2bcec89f6eed5a39509ac` now verifies the receipt content
without the self-hash field and separately records producer and checker source
SHAs. The immutable market runtime was not rerun or modified. Independent PC2
and local checkers pass with zero errors, and the consumed receipt records the
actual negative outcome. No Alpha, validation, OOS, promotion, new grammar,
temporal optimizer, or further search authority is created. Research remains
HOLD.

The preceding completed phase was:

`CRYPTO_FUNDING_FLOW_RESIDUAL_NESTED_CONFIRMATION_V1_VALIDATION_A_FAILED_ROUTE_CLOSED_RESEARCH_HOLD`

The one explicitly authorized replacement diagnostic is consumed and closed.
Exact PC2 producer `3e8d1bbf07303ff983596ea295a3af82fd340b1b` and detached task
`job_20260806_204858_323d59` evaluated the unchanged 162-candidate grid as 81
exact main/swapped-timescale-placebo pairs. Stage 0 and reused development
Validation A each completed all 162 strict evaluations with zero candidate-local
failures. The producer and independent checker both exited zero.

The main construction beat the placebo on the two relative tests: median
main-minus-placebo worst-axis net was `0.00005048286306459388`, and main beat
placebo in `0.6296296296296297` of cells. Absolute family economics did not
transfer. Global main-cell median worst-axis net was
`-0.00034318043322402545`; only `0.07407407407407407` of main cells had both
matched axes net positive; only two of six anchor neighbors were positive; and
Bybit, Hyperliquid and OKX all had negative source-level median worst-axis net,
so positive funding-source count was zero. Validation A had eight candidates
with both axes net positive and zero strict matched-positive candidates.

The preregistered family gate therefore failed and the terminal decision is
`REUSED_VALIDATION_DIAGNOSTIC_ONLY::FUNDING_FLOW_RESIDUAL_ROUTE_CLOSED`.
Validation B was not read. Holdout and OOS read counts remain zero. This closes
the current long-funding/short-flow residual basin under the frozen target,
mapping, 5 bps cost, candidate grid and reused-validation diagnostic contract;
it is not an OOS or promotion result and does not reject all funding/flow
mechanisms.

The replacement receipt is
`RUN_AUTHORIZATION_CONSUMED_VALIDATION_A_TERMINAL_FAIL_CLOSED` with
`run_authorized=false`. Local independent checking passes against artifact
bundle `70855B9E57AA57342CF1A96684A234F26C05DB0338D5A87005869C49AD8CA1C8`.
The PC2 launch also records `core.autocrlf=false` and proves 18 critical source
and authority files by raw working-tree blob against commit blob, with proof
SHA256 `EA4E47AEF680B48F3C664190D08C04309BE14BFCD70C5B42B266E29B2419DD6A`.
Future launches fail before market read if checkout bytes, the economic receipt,
or its frozen runtime dependency are absent or transformed. No second task,
rescue rerun, reseed, tuning, optimizer feedback, Archive write, promotion, or
new Arena is authorized. Research state remains HOLD.

The preceding completed phase was:

`CRYPTO_SEARCH_REPLICATION_AWARE_GATE_V1_R3_COMPLETE_NOT_QUALIFIED_RESEARCH_HOLD`

The one authorized R3 development campaign is consumed and closed. Exact
producer `fd6220d56e0632b5084c2ed7574992c8bc2803fb`, receipt runtime
`20260806r3`, and PC2 task `job_20260806_145544_e65955` completed exactly 1,536
strict evaluations from 2,077 generation attempts with 512 per arm. All three
512-candidate checkpoints are atomically published and restore-verified. The
run kept 10 workers, used no memory fallback, completed in 1,478.333 active
seconds at 3,742.668 actual pairs/hour versus the 512/hour floor, and performed
zero sealed, validation, OOS, or holdout reads.

Independent PC2 and local checkers pass with engineering integrity `PASS`, no
errors, and artifact bundle SHA256
`708C48BB96624AD4902704C4FA17277D3336FAD57B9AC2919E1ECCB5FFAA47A1`.
The replication-aware Evolution arm produced 29 candidates positive in at
least two of three purged development blocks versus 27 for current Evolution,
and 74.651 versus 66.903 such candidates per process CPU-hour. It did not
qualify: after removing the best contributing template its replication rate
fell below current Evolution, and it produced zero all-three-block-positive
candidates versus two for current Evolution. The sole strict matched-positive
row remains development-only and grants no Alpha, validation, OOS, or promotion
claim. The frozen result is `NOT_QUALIFIED_FOR_VALIDATION`; no arm is qualified
and no continuation or next Arena started.

The detached wrapper returned exit 1 only after all market artifacts were
written because the non-authorized validation result omitted `resumed` while
the final return assembly indexed that key directly. Closure source now treats
an absent flag as false. This repair did not read market data or alter the
completed evidence. No restart, second task, reseed, tuning, rescue rerun,
validation, OOS, promotion, reward, mapping, compiler, AST, evaluator, or
mechanism-catalog change occurred. Research state remains HOLD.

The preceding completed phase was:

`CRYPTO_SEARCH_REPLICATION_AWARE_GATE_V1_R2_INVALID_ARGUMENT_FLATTENING_BEFORE_ENGINE_ENTRY_RESEARCH_HOLD`

The one authorized R2 task is consumed and closed without entering the search
engine. Exact producer `c8ddfed84ed06101cd69b3ae5d6b63451e5be698`, receipt
SHA256 `28FCCA347A380A63686F56F0984F3C99E2CEB0CED37606A33C6D0F992EDA9E77`,
and PC2 task `job_20260806_140152_2eabe8` passed the committed source/receipt,
resource, cache, and no-market warning smoke gates. The detached task then
ended in 2.036 seconds because Windows PowerShell `Start-Process -ArgumentList`
flattened two multiword descriptive CLI values; argparse exited 2 before
`run_engine` created its runtime.

Persisted counts are zero generation attempts, zero worker submissions, zero
returns, zero strict evaluations, zero market evaluations, zero checkpoints,
and zero sealed reads. PC2 and local independent checkers correctly return
`FAIL` with 15 and 13 missing engine artifacts respectively. The 20-file closure
bundle is `78862541488DEC0A3D7F12FAE1FC5376108CD8CD9A883F346851277B714728D3`.
No restart, second task, reseed, tuning, rescue rerun, validation, OOS, holdout,
automatic expansion, or promotion occurred.

The launcher now quotes native multiword arguments and its no-market smoke
checks both warning-only stderr and exact argument round-trip. This is a source
repair only. The R2 receipt is
`RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED` with
`run_authorized=false`; it grants no further market authority. The existing
Search capability node records this invalid run without a new node, authority,
lifecycle, or promotion transition. Research state remains HOLD.

Graphify maintenance refreshed the existing CURRENT projection and its HTML.
The audit remains `STALE` with one `RAW_GRAPH_SOURCE_CHANGED` error because RAW
was built at `ce713786dc80559dcbea8ee2ced581d9edb70c23`. The available build command
reports that Graphify is not installed, and this task forbids installing new
dependencies. Therefore global RAW/CURRENT freshness PASS is not claimed.

The preceding completed phase was:

`CRYPTO_SEARCH_REPLICATION_AWARE_GATE_V1_REPLACEMENT_INVALID_NATIVE_STDERR_BEFORE_WORKER_SUBMIT_RESEARCH_HOLD`

The one authorized 1,536-strict replacement run is consumed and closed without
market-evaluation evidence. Exact producer
`a0c60ec55c4e71da08f575dfcbf2ec76cecd7596`, replacement receipt SHA256
`8783957DE8CFBA99B5CE80F1AAF492E2348045A562E1BBBB2352ACF1B7D81167`, and
PC2 task `job_20260806_125929_7681d5` reached the first pre-submit batch only.
The persisted counters are eight generation attempts, zero worker submissions,
zero returns, zero strict evaluations, zero checkpoints, and zero sealed reads.

Windows PowerShell converted the NumPy `RuntimeWarning` written to native
stderr into a terminating `NativeCommandError`. The producer disappeared during
the first multiprocessing spawn, leaving one child with inherited log handles.
After five minutes of unchanged heartbeat, stdout, CPU, and counters, only that
exact orphan was terminated so the single detached task could persist its
terminal failure. No restart, second task, reseed, tuning, rescue rerun,
validation, OOS, holdout, automatic expansion, or promotion occurred.

PC2 and local independent checkers both return `FAIL` with the same 13 missing
terminal artifacts. The 16-file failure-evidence bundle is
`C8B3ADD62EEBC1C01A9A7E0D200571485BED83FF582B57AD798CE2E5568720EC`.
The replacement receipt is
`RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED` with
`run_authorized=false`. This is an operational invalid run, not evidence about
random, current Evolution, replication-aware Evolution, reward, Alpha, or
migration. Any further market run requires new explicit authorization and a new
receipt.

The existing Search capability node records this consumed replacement failure
without a new node, authority, lifecycle, or promotion transition. Research
state remains HOLD.

The preceding completed phase was:

`CRYPTO_SEARCH_REPLICATION_AWARE_GATE_V1_PROCESS_EVIDENCE_REPAIRED_SOURCE_AND_PC2_SMOKE_VERIFIED_RESEARCH_HOLD`

Replication-Aware Search Gate V1 remains a consumed invalid market run. Its
retained design and market contract are unchanged. Source commit
`175ce33f31ba56ab336d187e2b7ca0c9e2e29e98` repairs the missing process-evidence
chain without evaluating a candidate: proposal attempts and exact candidate
identities are now atomically persisted after batch construction and before
worker submission, while worker initializer/task receipts record started,
ready/completed, and failed stages. These receipts are campaign-local and
fail-closed; they do not feed reward, mapping, Archive, CEM, or Evolution.

The historical statement that the failed PC2 task made exactly zero generation
attempts is withdrawn. Its persisted producer status remained at zero, but no
pre-submit attempt receipt existed and one orphan multiprocessing spawn child
proved that the submission path began. The exact proposal count is therefore
unknown. Exactly zero strict evaluations and zero checkpoints remain supported.

The global remote launcher at
`G:/Chengbo/tools/company-remote/company-remote.ps1` (SHA256
`75036FFAC3A80A3E0A12637DD93F37B6A0582C9F6313E4F6BCBFC85F4BE726AA`)
now registers and starts each detached task once, holds an atomic start lock,
and persists launcher PID, child PID, separate streams, and the real child exit
code. PC2 smoke `job_20260806_111245_5b7afd` produced one invocation and the
intentional exit code 7. No-market engine smoke `job_20260806_114350_12ba4d`
initialized the exact 115-field store/registry and emitted five of five ready
worker receipts at the 10-worker configuration, with no market evaluation or
receipt consumption. Full tests pass: 454 passed with one existing warning.

The receipt is
`RUN_AUTHORIZATION_CONSUMED_ENGINE_VERIFICATION_FAILED` with
`run_authorized=false`. The ten-file invalid-run evidence bundle is
`D0E544EB1396CA5C43E77ED82B4277FAEF05164650846CB7735CB3D4F65EBCFD`.
No random/Evolution comparison, replication-ordering conclusion, Alpha claim,
validation, OOS, promotion, or next-Arena authority exists. A replacement run
requires new explicit authorization; this closure does not authorize one.

The existing Search capability overlay records the invalid run correction and
process-evidence repair without a new node, authority, lifecycle, or promotion
transition. Bounded CURRENT maintenance again failed to terminate; its partial
generated files were discarded and the prior committed CURRENT was restored.
The overlay is current, generated CURRENT remains stale, and no global freshness
PASS is claimed. Research state remains HOLD.

The preceding completed phase was:

`CRYPTO_SEARCH_FAMILY_CONSENSUS_DEV_V1_CHECKPOINT_PROJECTION_COMPLETE_RESEARCH_HOLD`

The source-only closure repaired the exact aggregation defect: the original
runner supplied the full 336-hour receipt target to economic weight paths whose
identity was correctly shortened to 330 hours by the two-hour execution delay
and four-hour horizon purge. Future online aggregation now selects target
columns by the persisted economic-path timestamps instead of positional receipt
length. Focused verification passed 27 tests and the final full suite passed
443 tests with the existing NumPy warning.

The already completed 35-candidate checkpoint was then consumed once without a
market read, candidate evaluation, generation, optimizer feedback, or archive
write. Because its persisted asset paths omit weights at or below `1e-12` and
asset gross contributions at or below `1e-18`, the result is explicitly a
bounded threshold-sparse projection, not a bit-exact reconstruction. The frozen
rank interval gives a 150-asset ceiling and a worst incremental net-mean error
bound of `3.003e-13`.

The 23-member primary family consensus has 66 common-support hours. Its
left/right matched incremental net means are `-0.00015651447691891477` and
`-0.000303735033547274`; both remain negative after the worst projection bound.
The result is therefore robustly
`FAMILY_CONSENSUS_DID_NOT_TRANSFER` for this development-fresh window. Net-LCB
values remain diagnostic point estimates only. The 12-member other group stays
descriptive and is not a fair primary comparator. The independent checker
passes with zero errors.

The receipt is `OFFLINE_CHECKPOINT_PROJECTION_COMPLETE` with
`run_authorized=false`. No second gate, rescue rerun, market replay, candidate
re-evaluation, generation, optimizer feedback, archive write, OOS read, or
promotion occurred. This closes the family-consensus question under the frozen
target, mapping, 5 bps cost, cohort, and interval; it does not qualify Alpha or
a common causal mechanism. The predecessor target-shape failure remains
recorded below as history.

The existing CURRENT search capability node now points to the committed
checker-backed projection evidence with `STATIC_VERIFIED / PASS`; no node,
authority, or lifecycle transition was added. Global CURRENT remains truthfully
`STALE` because the 21,761-node RAW graph predates the intervening source and
artifact commits. The installed maintenance route can refresh CURRENT but the
RAW builder dependency is absent, and this task did not install a new
dependency merely to erase that global warning.

The preceding completed phase was:

`CRYPTO_SEARCH_FAMILY_CONSENSUS_DEV_V1_ACQUISITION_FAILED_NO_GATE_CLOSED`

The separately authorized 4h two-axis family-consensus development gate is
consumed and closed without a consensus result. Producer
`d3dd61844cd05ca01aba857d57a5abd29c2a5840` froze exactly 23 primary
`FLOW_INTENSITY_CONVICTION × TIME_SERIES_DIRECTIONAL_STATEFUL × 4h × two-axis`
champions plus 12 descriptive 4h two-axis champions before reading the
2026-07-18 through 2026-08-01 development-fresh interval. The selection receipt
is `424037971D1473C78B68BFAA889B5900A86EE2DC349F946B4ECB7622C3AD1BF7`.

The single PC2 acquisition scheduled all 42 frozen venue-day coordinates. It
completed 38 and terminated with four OKX read timeouts on 2026-07-18,
2026-07-19, 2026-07-21, and 2026-07-22. The aligned carrier was not built, the
35-candidate gate and its independent checker never started, strict evaluated
count is zero, and no consensus transfer or economic conclusion is observed.
No retry, rescue, redownload, candidate generation, optimizer feedback, archive
write, OOS read, or promotion occurred. Partial payloads remain evidence only
and are not admitted as a research carrier.

The receipt is
`RUN_AUTHORIZATION_CONSUMED_ACQUISITION_FAILED_NO_GATE` with
`run_authorized=false`. A future retry would require new explicit authorization;
this closure does not authorize one. The previously completed V1.1 champion
development-validation result below remains the latest market-evaluated
research evidence.

The existing CURRENT Search capability node records this consumed failure while
retaining the prior completed validation as its latest checker-backed result.
No node or authority transition was added. CURRENT regenerated truthfully as
`STALE` because the RAW graph predates the closure worktree; no global freshness
claim is made.

The preceding completed phase was:

`CRYPTO_SEARCH_EVIDENCE_V1_1_CHAMPION_DEVELOPMENT_VALIDATION_COMPLETE_RESEARCH_HOLD`

The explicitly authorized wrapper-failure replacement is consumed and closed.
Producer `840c3038c9e461d1ba70dd7c520a9db9b1cb33fe` evaluated the exact same 49
frozen V1.1 positive behavior-family champions on the unchanged 2025-11-01 to
2026-01-01 Binance USD-M development-validation partition. The fixed candidate
identities, train orientation, target, portfolio mapping, 5 bps cost, reward,
and evaluator were unchanged. Ten PC2 workers completed 49/49 strict evaluations
in one restore-verified checkpoint at 1,570.779 pairs/hour with zero candidate
failures and no memory fallback. Candidate generation, optimizer feedback,
policy/archive writes, backfill, reseed, tuning, holdout/OOS reads, promotion,
and automatic expansion remained zero. Independent PC2 and local checkers pass.

The result is narrow directional survival, not qualification. Across all 49,
22 have positive validation search reward and 26 have positive net mean on both
matched axes, but zero have positive net LCB on both axes. The predeclared 4h
two-axis slice has 21/35 positive validation reward and 24/35 dual-axis positive
net mean, but 0/35 dual-axis positive net LCB. The signal is concentrated in
`MECHANISM_V2_FLOW_INTENSITY_CONVICTION` with
`TIME_SERIES_DIRECTIONAL_STATEFUL`: 18/23 validation-reward positive and 21/23
dual-axis net-mean positive. Three-axis candidates produce only 1/13 positive
validation rewards; 1h produces 0/6. All 49 candidates realize every declared
mechanism axis, so the weak result is not explained by an inactive declared
axis. Train-to-validation search-reward Spearman is -0.222 overall and -0.207
in the primary slice, so development reward ordering does not migrate.

Strict matched-positive count is zero because the frozen strict evaluator
requires non-negative net LCB on every matched axis and no candidate crosses
both validation axes. The producer summary accidentally read the source
`matched_positive` and `primary_net_mean` columns for two displayed counts;
their numeric results happen to agree with validation in this run. Closure code
now persists and reads explicit validation fields without market replay. The
validation projection did not emit a validation behavior-family identity, so
cross-window family-identity stability remains unobserved and is not inferred.

The replacement receipt is
`RUN_AUTHORIZATION_CONSUMED_VALIDATION_COMPLETE` with `run_authorized=false`.
This development validation provides no arm qualification, Alpha claim,
globally untouched OOS evidence, or promotion authority. No additional search,
validation replay, OOS, challenge, recent, May-stress, forward, promotion, or
new Arena is authorized.

Closure verification passes 436 tests with the existing NumPy
degrees-of-freedom warning. The existing CURRENT Search Engine capability node
is updated and independently resolves its committed validation receipt and
checker evidence as `STATIC_VERIFIED / PASS`; no node, authority role, or
promotion transition was added. The global RAW navigation graph still predates
the closure commit. Its single refresh attempt remained CPU-active but exceeded
the bounded ten-minute command budget and was terminated without replacing RAW;
CURRENT therefore truthfully retains `RAW_GRAPH_SOURCE_CHANGED / STALE` rather
than claiming global graph freshness.

The underlying V1.1 development evidence remains:

The one-time V1.1 fresh-state development run is consumed and closed. Producer
`67701ba73ac16c3da6cbdf6d98431d6d1df998e1` completed exactly 2,000 strict
candidates from 3,201 generation attempts on the existing 115-field aligned
OI/mark plus aggTrades carrier. `checkpoint_000` is atomically published and
restore-verified. The run used 10 workers, exceeded the frozen throughput floor,
read no validation, OOS, or holdout partition, and started no rescue run.

Independent PC2 and local checkers pass with artifact bundle SHA256
`DE21BD375C420DCA93C7FAE8FFB4E461E519041611E34314E32C43AAC791241C`.
All 2,000 strict ledger rows join exactly to their candidate-bound behavior and
mechanism provenance. The passive evidence contains 2,320 attributed proposals,
320 control-degenerate proposals, 1,942 behavior families, and 64 exposure
strata. All strict candidates realized every declared mechanism axis. Of the
320 proposal-level control degeneracies, the earliest stable equality is SIGNAL
for 259, RANK for 7, SELECTION for 52, and MAPPED_WEIGHT for 2. Mapping is
therefore not the dominant first failure layer.

The first supported system-wide bottleneck is
`GROSS_TO_NET_COST_THEN_DUAL_AXIS_NET_LCB_STABILITY`: primary gross/net is
positive for 1,725/695 strict candidates; both matched axes are gross/net
positive for 754/156, but neither axis has positive net LCB for any candidate.
Cost sign-kills 834 gross-positive candidates and turnover kills 264. There are
68 positive development `search_reward` candidates (63 Evolution, 5 random),
but zero strict matched-positive candidates. Those 68 are train-only family
champion inputs for a possible separately authorized validation, not Alpha,
qualification, OOS, or promotion evidence.

Evolution improves the conditional reward distribution but does not qualify as
the more productive search policy: it requires 1,772 attempts for 1,000 strict
evaluations and yields 943 families, versus random's 1,429 attempts and 999
families. Rare mechanism strata remain under-supported, so the run supports the
aggregate failure-layer conclusion, not a conclusion for every rare mechanism.

The detached wrapper recorded exit code 1 only because the CLI success mapper
recognized `result=PASS` but omitted the valid V1/V1.1 terminal status values.
The terminal artifact, checkpoint, and independent checks were already complete;
the closure fixes that source-only mapping without a market rerun. The receipt is
`RUN_AUTHORIZATION_CONSUMED_ENGINE_COMPLETE` with `run_authorized=false`.

No further development search, reward/mapping/search-policy change, validation,
OOS, promotion, challenge, recent, May-stress, forward, new Arena, or new Graph
node is authorized. The highest-information next experiment, only if separately
authorized, is a small no-feedback fresh validation of deduplicated champions
from the 68 positive development candidates under the unchanged target, mapping,
cost, and evaluator contracts.

The preceding source implementation record was:

`CRYPTO_SEARCH_ENGINE_V2_5_BEHAVIOR_PROVENANCE_CENSUS_CONSUMER_IMPLEMENTED_NO_REPLAY`

Source commits `e9f5d629`, `d66421cc`, `8be18c91`, `8f457091`,
`e6bdfce0`, and `743a7d0775a3c7880b31323386c1d5b2daf48092` implement the
source-only V2.5 Behavior Provenance Census Consumer. The consumer verifies a
candidate/spec/hash-bound provenance envelope, recomputes the mutually
exclusive earliest stable `first_equal_stage`, and produces fixed-schema
candidate provenance, stage-count, and monotonic policy-funnel tables. Its
frozen slices are arm, seed, skeleton, mechanism family, mapping family,
horizon, and direction authority; behavior uniqueness is explicitly scoped to
`ARM_SEED_HORIZON_BEHAVIOR_FAMILY`.

The consumer has no market-data path and writes no reward, CEM, Evolution,
archive, scheduler, or budget feedback. Partial or inconsistent provenance
fails closed. The existing V2.4 evaluation rows now carry only the diagnostic
dimensions required by future consumer runs; search generation, mapping,
matched controls, evaluation, rewards, and kill-lines are unchanged. Spec and
Standards reviews pass, the focused suite is 51 passed, and the full suite is
423 passed with the existing NumPy warning.

The verified source-only bundle at
`runtime/crypto_behavior_provenance_census_v1_20260804` is bound to source SHA
`743a7d0775a3c7880b31323386c1d5b2daf48092`, the immutable 512-row V2.4
repair ledger, and its source manifest. Its historical result is exactly
`NO_PROVENANCE_ROWS`, `legacy_final_equal_count=372`, and
`first_equal_stage=null`. The three Parquet outputs contain zero rows while
retaining their frozen schemas. No historical stage is inferred, no candidate
is replayed, no market data is read, and no reward or policy authority changes.

The preceding source implementation record was:

`CRYPTO_SEARCH_ENGINE_V2_4_CONTROL_DEGENERACY_PROVENANCE_IMPLEMENTED_NO_REPLAY`

Source commits `1ba4a36ef13fefaa7296bd7217af3c17b16d6c87`,
`6435cb909d1c55a8e7ec42a120c016168ac52c42`, and
`f5cee4bfc65634735393956d7b9a881a069b30e6` add an
opt-in, read-only control-degeneracy provenance projection to the existing
mapping and pair-evaluation authorities. It records the raw expression signal
separately from the frozen-train-oriented mapping input, then records only
mapping-defined rank, normalized-score, selection, raw-weight, capped-weight,
mapped-weight, and executable-weight identities. `first_equal_stage` is the
earliest observed stage from which every later mapping-defined identity remains
equal. Signal distribution, finite support, cross-sectional dispersion, rank
entropy, rank correlation, top/bottom overlap, and long/short set overlap are
diagnostic only; target, IC, gross, net, turnover, cost, and reward are excluded
from the identity.

The existing `CONTROL_BEHAVIOR_EQUALS_PRIMARY`, right-axis, and hierarchical
AB-left-control exact-weight kill-lines are unchanged. V2.4 workers validate
the provenance schema, stages, labels, failure reason, exact canonical hash,
and final equality before persisting a candidate/spec-bound envelope. Enabling
the projection leaves weights, feasibility, transition reasons, diagnostics,
reward, and evaluation authority unchanged. Verification is source-only and
synthetic: 417 tests pass with the existing NumPy warning. No candidate was
generated or replayed, no July data was reread, and no optimizer, archive,
policy memory, OOS, promotion, or new Arena was started.

The completed July repair ledger is now interpreted more precisely: all 512
candidate specs passed static typed reconstruction; 140 reached strict matched
cost evaluation, while 367 mapped primary/control pairs and five hierarchical
AB/left-control pairs became exactly weight-identical. The persisted historical
rows do not contain the new intermediate fingerprints, so they cannot be
retroactively assigned to SIGNAL, RANK, SELECTION, CAP, or MAPPING without a
separately authorized exact-cohort replay. Evolution's higher reward among 40
survivors remains conditional on a 15.6% evaluation-reachability rate versus
random's 39.1%; it is not an unconditional policy-productivity win.

The separately authorized V2.4 repair replay is consumed and closed. It reused
the exact frozen July 1-18 cohort: 512 candidate identities in the original
order, the same two seeds and 1h/4h horizons, the qualified 115-field carrier
(71 OI/mark plus 44 aggTrades), Binance USD-M target, and 5/10 bps cost paths.
It generated, replaced, or backfilled no candidate and imported no adaptive
state. A pre-market static sweep reconstructed all 512 candidate specs through
the existing typed compiler.

The unique 10-worker PC2 evaluation source
`ecf951c179abc5a29e19ab840f878d0cc97ccd1f` completed all 512 source
ordinals and eight exact 64-candidate checkpoints. Known control/support
degeneracies were persisted candidate-locally: 140 candidates completed strict
matched cost evaluation and 372 became behaviorally non-distinct from a required
control on the fresh window. The initial terminal
aggregation correctly stopped because one arm had zero strict candidates in
one seed-horizon cell; finalizer
`0a25183f79350b19bc8ae961e8df12fa815c12f8` treated that cell as an
equal comparison count of zero and assembled artifacts only from the existing
checkpoints, without market re-evaluation.

Independent PC2 and local checkers pass with artifact bundle SHA256
`85430B0965A88ADF64FE0F81B1168FF23D038C4454DD638D6C7E9241A008C18B`.
The repair replay contains 510 behavior families and zero strict matched-positive
candidates. Among the strict-evaluated survivors, Evolution beats typed random
on equal-count mean pair reward by
`2.747134383772` and on mean matched net at 5 bps by `0.000063753316`, but
neither arm qualifies because matched-positive count is zero. These are fresh
validation diagnostics only: economic Alpha remains HOLD, and no OOS,
promotion, challenge, new Arena, tuning, reseed, rescue, optimizer feedback,
policy/archive memory, or second search is authorized.

The one-time repair receipt now has
`RUN_AUTHORIZATION_CONSUMED_REPAIR_REPLAY_COMPLETE` and
`run_authorized=false`.

The preceding source implementation record was:

`CRYPTO_SEARCH_ENGINE_V2_4_SOURCE_GATE_IMPLEMENTED_RUN_NOT_AUTHORIZED`

ADR 0022 is accepted and source commit
`2f512c72` implements the next search-policy boundary without starting another
market experiment. V2.4 selection is behavior-family-first: every
`arm x seed x horizon x behavior_family_id` cell receives one vote, represented
only by its deterministic train-`search_reward` champion. Missing cells and
duplicate-family backfill fail closed. The existing Evolution population,
typed mutation receipts, AST, compiler, pair evaluator, mapping, and cost
authority are reused; no second search or evaluation stack was added.

The gate is now ordered rather than advisory. A pre-read atomic receipt freezes
the selected candidate/spec identities, equal cell counts, fresh interval,
contract hash, producer commit, and component Git blobs. V2.4 currently admits
only an interval starting at or after `2026-07-01T00:00:00Z`. The post-read
adapter rejects missing/extra candidates or mismatched spec, horizon, baseline
5 bps cost, economic receipt, partition, venue, assets, or timestamps. It then
atomically persists the selection receipt, exact hourly sleeve waterfall and
objective mask, daily sleeve waterfall, 5/10 bps sensitivity, sparse
asset-weight/gross-contribution paths, and a row-count/hash manifest.

`pair18m.evaluate_pair` remains the sole evaluator and exposes these paths only
through an opt-in validation/holdout audit projection. The V2.4 contract status
is `SOURCE_IMPLEMENTED_RUN_NOT_AUTHORIZED`; market search, sealed reads, OOS,
forward/recent/challenge, promotion, new grammar, and cross-sprint adaptive
memory remain false. The historical V2.3 OOS receipt loader also now verifies
its producer Git blobs rather than mutable current working-tree files. No new
performance evidence or Alpha claim was produced.

The existing CURRENT Search Engine capability node records the completed repair
replay without promotion or a new Graph node. Its overlay projection is current.
The global RAW Graph remains stale at source SHA
`75c7d3abf39223fe12034e42cfa9b880eb45624b`: the required RAW build command
failed closed because the Graphify CLI is not installed, and this task did not
install new dependencies. Global Graph freshness is therefore not claimed.

The preceding evidence state remains:

`CRYPTO_SEARCH_ENGINE_V2_3_OOS_POLICY_BIAS_AUDIT_COMPLETE_HOLD`

ADR 0021's one read-only frozen V2.3 OOS authorization is consumed. Producer
`3e593aaea93e9b521ba78d24186ad225e901eae7` replayed the exact four
pre-validation cohorts over the frozen `2026-01-01` through `2026-07-01`
holdout: 1,024 source identities, 1,023 completed evaluations, one persisted
candidate-local constructibility failure with no backfill, and 16 exact
64-candidate checkpoints with restore verification. The run performed exactly
one sealed partition read and generated no candidates or optimizer, archive,
policy, scheduler, or cross-sprint memory feedback.

The pooled equal-weight daily total-policy effect across both preregistered
seeds and the 1h/4h horizons is positive. Primary-net delta is
`0.000201472686` with seven-day block-bootstrap `P(delta>0)=0.9983` and
`q10=0.000121597033`; matched-increment delta is `0.000227422332` with
`P(delta>0)=1.0000` and `q10=0.000175464575`. Proposal-distribution and
train-ranker pooled effects are also positive. Seed/horizon cells remain
heterogeneity evidence rather than an all-cell veto.

Terminal classification is
`OOS_TOTAL_POLICY_POSITIVE_DIRECTION_Q10_SUPPORTED`. Independent PC2 and local
checkers pass with artifact bundle SHA256
`EEAFD289233B6E39737A43896DFBB76BEE78D06869F4A6FC846D2D3647B3A5BA`.
This is conditional OOS policy-attribution evidence under the frozen Binance
USD-M target and 5 bps cost; it is not a binary qualification gate, Alpha
claim, formal optimizer authority, or promotion. No second read, tuning,
reseed, rescue rerun, challenge, recent, May-stress, forward, promotion, new
search, or subsequent Arena occurred.

The subsequent existing-artifact-only policy bias audit changes no runtime
result or authority. It independently joins all 1,024 frozen identities to the
16,000-row train ledger and recomputes the absolute cohort economics. Evolution
stratified remains negative at `-0.0000964991` primary net per day; Evolution
train-top is positive at `0.0001778316`, versus random train-top
`-0.0000236411`. The OOS evidence therefore supports train ranking/selection,
not broad proposal-level Alpha.

Evolution train-top collapses from 256 exact expressions to 221 canonical
expressions and 161 behavior families, a `37.109%` behavior-duplicate rate. Its
primary daily-path correlation participation-ratio effective rank is only
`7.306`. The 97 `FLOW_INTENSITY_CONVICTION` candidates occur only in seed
`359914106`; the other seed selects 128/128 `FUNDING_FLOW_CROWDING` candidates.
Flow-intensity is the principal positive post-hoc mechanism contributor, while
funding-flow is mixed and positive in only two of six OOS months. Deterministic
equal-family and train-reward-champion sensitivities retain positive pooled
policy direction, so duplicate weighting does not create the sign, but the low
effective diversity and seed-mechanism confounding prevent a broad mechanism
claim.

The persisted OOS paths contain net, matched-increment, and control returns but
not gross, turnover, cost-path, asset-weight, venue-concentration, or capacity
paths. The single 181-day OOS window grades `WEAK` under the project bias-audit
rule. Result: `HOLD_RESEARCH`; economic Alpha remains unestablished, every
optimizer/search-arm authority remains NON_FORMAL or empty, and no additional
sealed read or market evaluation occurred. Canonical audit evidence is
`reports/CRYPTO_SEARCH_V2_3_OOS_POLICY_BIAS_AUDIT_20260803.md` with its
deterministic JSON companion.

The preceding durable state remains:

`CRYPTO_SEARCH_ENGINE_V2_3_POLICY_ATTRIBUTION_GATE_NEGATIVE_COMPLETE`

ADR 0020's one fresh-state, development-only V2.3 authorization is consumed.
Producer `06512e01876345d9921d56405d8254a82933a9b7` retained exactly
16,000 strict, exact-unique, matched-control-valid, full-cost train candidates
from 23,869 raw attempts across eight restore-verified 2,000-candidate
checkpoints. The run used 10 workers, the existing 115-field aligned carrier,
786-mechanism catalog, compiler, evaluator, receipt-bound Binance target,
mapping, joint primary-plus-matched Sortino reward, frozen 5 bps cost, archive,
and checkpoint path. No V2.2 candidate, reward, population, archive, RNG,
transition, or policy state entered the campaign.

The frozen validation evaluated exactly 1,024 candidates: 256 each from random
stratified, random train-top, Evolution stratified, and Evolution train-top,
balanced across both preregistered seeds and the 1h/4h horizons. The train-ranker
effect passed seven of eight primary/matched seed-horizon effects but failed the
second seed's 4h primary-net effect. Proposal-distribution passed only one of
four complete seed-horizon cells, and total policy passed both cells for the
first seed but neither cell for the second seed. Therefore proposal distribution,
train ranker, and total policy all remain unqualified; the full-policy gate is
negative and the conditional 4,000-candidate continuation was not allocated.

Terminal status is
`PASS_SEARCH_ENGINE_V2_3_POLICY_ATTRIBUTION_GATE_NEGATIVE`. Independent PC2 and
local checkers pass with artifact bundle SHA256
`A593CAB511326F30ABC426329E71F1451AD73250E5D4FEF4552CFD8F46AEDAF5`.
No holdout/OOS, promotion, rescue, seed change, tuning, new grammar, new data
surface, or subsequent Arena occurred; sealed reads are zero and future-Arena
qualified arms remain empty.

The preceding durable state remains:

`CRYPTO_SEARCH_ENGINE_V2_2_VALIDATION_GATE_NEGATIVE_COMPLETE`

ADR 0019's one fresh-state, development-only Search Engine V2.2 authorization
is consumed. Producer `e84b35c76a4cfc139f1c351286489b83fce61250`
retained exactly 8,000 strict, exact-unique, matched-control-valid, full-cost
train candidates from 12,240 raw attempts across four exact-restored
2,000-candidate checkpoints. The run used 10 workers without memory fallback,
reused the existing 115-field aligned carrier and 786-mechanism V2.1 catalog,
and produced 7,774 behavior families. No V2.1 candidate, reward, population,
archive, RNG, transition, or policy state entered the campaign.

The equal-count train gate passed. Evolution produced 406/4,000 positive search
rewards (10.15%) versus random's 16/4,000 (0.40%), improved mean search reward
from `-0.831556` to `-0.363293` and top-decile reward from `-0.161436` to
`0.117570`, retained 3,779 families (94.475% yield), and kept duplicate rate at
5.525%. The frozen 128-per-arm validation then completed with 64 candidates at
each 1h and 4h horizon. Evolution's worst-horizon validation metrics were
positive: net mean `0.0000588561`, non-overlap floor Sortino `1.6127145`, and
matched increment `0.0000663935`. The receipt-bound expanded-random control
failed net mean, Sortino, and matched increment, so the mandatory control
survival rule exited both arms. Stage C allocated none of the remaining 12,000
candidate ceiling; qualified arms are empty.

Terminal status is `PASS_SEARCH_ENGINE_V2_2_VALIDATION_GATE_NEGATIVE`.
Independent PC2 and local checkers pass with artifact bundle SHA256
`BF5567FC2401AA14343753065F8209A2016EB225EC5C6FE58498CBE2C28967E4`.
No holdout/OOS, promotion, rescue, seed change, tuning, new grammar, new data
surface, or subsequent Arena occurred; sealed reads are zero.

The preceding durable state remains:

`CRYPTO_SEARCH_ENGINE_V2_1_TRAIN_GATE_NEGATIVE_COMPLETE`

ADR 0018's one fresh-state, development-only Search Engine V2.1 authorization
is consumed. Producer `94b016fa7847d5c5b06db1e6144bda7062064151` retained
exactly 10,000 strict, exact-unique, matched-control-valid, full-cost train
candidates from 14,237 raw attempts across five exact-restored 2,000-candidate
checkpoints. The run used the frozen eight-worker memory fallback, reused the
existing 115-field aligned carrier, AST, compiler, controls, evaluator, archive,
and checkpoint path, compiled 184 legacy plus 786 expanded mechanisms, and
produced 9,754 behavior families. No V2 candidate, reward, population,
distribution, archive, RNG, or policy state entered the campaign.

The equal-count train gate was negative. Expanded random produced 23/4,000
positive search rewards (0.575%), below the frozen 40-count and 1% absolute
floors. Evolution produced 327/4,000 positives (8.175%), improved matched-count
mean and top-decile search reward, retained 3,757 families, and stayed below the
10% duplicate ceiling, but the random-control absolute floor correctly blocked
validation. Terminal status is
`PASS_SEARCH_ENGINE_V2_1_TRAIN_GATE_NEGATIVE`; validation, OOS, promotion, and
the next Arena did not run, sealed reads are zero, and qualified arms are empty.
Closure source `2c4cb156fbe886c13482ba7d2e0e460732f2be0e` repaired only
the return/checker path and independently rechecked the immutable producer
artifacts on PC2 with `errors=[]`; it generated no market candidate.

The one fresh-state, development-only Search Engine V2 authorization is
consumed. Producer `ef688d89ca0e89654015bf5f76a6b9c26494d837` retained exactly
12,000 strict, exact-unique, matched-control-valid, full-cost train candidates
from 20,386 raw attempts across six exact 2,000-candidate checkpoints. The run
used 8 workers after the frozen memory preflight, compiled 12 declarative
economic templates into 184 legal mechanism specs, and produced 11,738 behavior
families. No prior candidate, reward, distribution, population, archive,
transition, or policy state entered the campaign.

The final validation did not complete. Binary and hierarchical mechanisms
legally expose different matched-control schemas, while the producer arm
aggregator incorrectly required identical control names and raised
`validation control path inconsistent for arm:
extensible_mechanism_random_v2:interaction_left`. The exact train checkpoint is
`checkpoint_005`; no validation checkpoint or complete equal-count validation
metrics exist. The independent blocked-outcome checker passes, but all arm
qualification remains empty. This is an engine aggregation defect, not a
market, carrier, or Alpha negative.

Closure `8a526e8683874e3bdbcfd54e49adfbd0c1f290ff` repaired future
heterogeneous-control aggregation without re-evaluating the campaign. Follow-up
source `c7d4806e` added reward-authority-aligned positive-search-reward
productivity metrics because the producer dashboard still reported only legacy
`matched_positive/pair_reward` counts. The old diagnostic did not enter policy
updates or the validation kill-line. No seed, parameter, budget, validation
rerun, holdout/OOS/challenge/forward read, promotion, or next Arena occurred.

The preceding durable state remains:

`CRYPTO_SEARCH_ECONOMIC_V6_SEED_ROBUSTNESS_VALIDATION_COMPLETE_CONTROL_FAILED_CLOSED`

The single authorized V6 fresh-state seed-robustness campaign is complete and
its receipt is consumed. Producer
`07a699f11510b943991425c4a86eb7582aa59583` used four pre-registered,
SHA256-derived uint32 seeds (`2816876876`, `329219361`, `3805005781`, and
`4227787900`) disjoint from V1-V5. It retained exactly `2,000` strict candidates
from `2,263` generation attempts, with all five initial arms at `400` candidates
and all four V6 seeds at `500` candidates. `checkpoint_000` and
`checkpoint_validation` restore exactly; the archive contains `1,947` behavior
families (`2.65%` duplicate rate).

The frozen equal-count validation stage completed `128` matched evaluations per
current arm, split `64/64` across 1h and 4h. One canonical-random candidate and
one typed-Evolution candidate produced known control-behavior degenerations and
were recorded and deterministically backfilled by frozen train rank. Policy and
archive hashes were unchanged, no candidate was generated during validation,
and no holdout was read. The canonical typed-random control failed all four
kill-line conditions: validation net mean, non-overlap floor Sortino, matched
increment, and control-not-dominant. Its worst-horizon aggregate was
`-0.0001665951` net mean, `-29.1668` Sortino, and `-0.0002597542` matched
increment. The runner exited all current arms and allocated none of the
remaining 18k budget.

V6 therefore qualifies no arm for a future new-data Arena. The result is
development-only and does not rewrite V5, establish an Alpha claim, or authorize
holdout/OOS, challenge, forward, promotion, rescue, tuning, a third seed
campaign, or import of any V1-V6 state. The independent artifact checker passes
with bundle SHA256
`41F0ED04B1568C35323CE328A2251DC06EACBE1BED4D61CD3A8BE7F346427B89`.

The preceding durable state remains:

`CRYPTO_SEARCH_ECONOMIC_V5_VALIDATION_COMPLETE_CONTROL_FAILED_CLOSED`

The repository-wide authority audit confirms that Search Engine V1 has a
substantial reusable engineering chain: admitted carriers, PIT/lag contracts,
the existing typed AST/compiler, A/B/AB/ABC matched controls, deterministic
replay, incremental behavior identity, campaign-local adaptive mechanics, and
exact checkpoint restoration. It does not need to be replaced.

The audit also supersedes ADR 0014's stronger authority claim.
`PHASE3CM_STYLE_TRAIN_PORTFOLIO_SORTINO_V1` remains deterministic diagnostic
code, but it is not a qualified economic optimizer authority: CandidateSpec
does not bind direction/orientation, portfolio role, execution
venue/instrument/price, or venue-specific cost; its single selected horizon is
duplicated in the nominal worst-horizon term; IID day resampling ignores
dependence; and primary-portfolio ordering is not jointly constrained by the
matched mechanism increment. No candidate was generated or reevaluated.

The prior Binance target exact replay remains immutable historical evidence:
`1,200` strict-valid entries, `661` final gross-positive, `86` HAC-LCB-positive,
`69` jointly persistent, `32` net-positive, and `0` matched-positive rows.
Those values remain execution/matched diagnostics. They cannot be reinterpreted
as portfolio search-reward results because the old ledger does not persist the
complete daily primary-portfolio path needed to reconstruct `search_reward`.
Research remains `HOLD`; adaptive search has not started. A distinct fresh
validation kill-line and read-only holdout must be bound before any future
adaptive market campaign.

`CRYPTO_SEARCH_ECONOMIC_RECEIPT_V1` now closes the source-level binding gap
without creating another evaluator. It resolves Skeleton hypotheses through
the existing mechanism-to-mapping authority, consumes A7Reward's train-frozen
orientation in the retained pair evaluator, retains the formal explicit
mapping, wraps the existing carrier with the existing Binance USD-M
`BinanceTargetStore`, and uses the joint standalone-plus-matched Sortino
reward. The pair evaluator consumes the receipt-bound cost instead of its
legacy module default; the full-L1 5 bps value remains a NON_FORMAL Binance
venue assumption, not a venue-qualified authority. A new pure validation
kill-line consumes only frozen validation metrics; its runtime adapter stops
the failed arm and atomically writes a checkpoint without reading
test/recent/stress/holdout or writing optimizer state. All referenced source
hashes are frozen. Canonical and direct runner entry points revalidate the
receipt. The one authorized conditional-development campaign under the frozen
5 bps assumption has now been consumed; no formal claim, sealed read, OOS,
challenge, or promotion was authorized.

Crypto Search Economic V1 stopped at the frozen raw-attempt hard limit with
`95,776` attempts and `1,190` strict, exact-unique, matched-control-valid,
fully cost-evaluated candidates. It wrote and restore-verified
`checkpoint_budget_exhausted`; no 2,000-candidate checkpoint, validation stage,
adaptive update, holdout read, OOS, promotion, or rescue rerun occurred. The
three functioning arms contributed 397 typed-random, 399 Hierarchical CEM V2,
and 394 Typed Evolution V2 candidates. The two fresh-state V1 controls each
failed before compilation because their legacy proposal path re-required a
complete Broad role surface after a compatible carrier-specific Skeleton
subset had already been frozen; together they consumed 94,469 raw attempts.
The partial ledger contains 1,160 behavior families, 35 positive train joint
search rewards, zero positive strict `pair_reward`, and zero matched-positive
discoveries. This is an incomplete, allocation-imbalanced campaign and
qualifies no arm. The proposal compatibility defect and the budget-exhausted
report/manifest closure path are fixed at `da7842dabacf7c98e62475014666877eeda86664`;
the run authorization is now false and cannot launch a second campaign.

The postmortem proposal repair now reuses the proven CN generator discipline
without importing CN fields, evaluator, calendar, or A-share constraints.
Every campaign first exercises one source-only proposal from every frozen
arm/seed lane on the exact admitted carrier, verifies field scope, matched
control construction, and deterministic replay, and records zero reward reads
and zero market evaluations. The real 115-field carrier passes all 20 lanes.
Legacy V1 proposal paths now perform bounded internal compile-domain resampling;
the rolling engine retries only the explicitly typed bounded-underfill failure.
Unexpected role, configuration, receipt, or replay errors fail closed instead
of being counted indefinitely as ordinary proposal rejection.

`CRYPTO_SEARCH_ECONOMIC_RECEIPT_V2` has been consumed. Producer
`bcb77cecf2d75e650e73998b37af9ceed1b71072` passed the 20/20 zero-market
proposal preflight, selected the fail-closed eight-worker fallback, and reached
the exact restore-verified `checkpoint_000` with `2,000` strict candidates from
`2,280` attempts and `1,964` behavior families. Before any
`checkpoint_001` allocation, the frozen validation stage rejected one selected
candidate with `CONTROL_BEHAVIOR_EQUALS_PRIMARY`. The producer correctly
detected the invalid matched control but its orchestration did not persist the
candidate identity or convert the deterministic validation-constructibility
failure into a terminal state. Source closure
`a371330a8ec5f77a70d34ecdbf0193e89cb5ea94` now performs that fail-closed
conversion for future runs and closes this historical process from the
verified checkpoint without candidate generation or evaluation. The current
run was not resumed, rescued, reseeded, or tuned; it read no sealed partition,
qualifies no arm, and supplies no Alpha or carrier-information conclusion.

`CRYPTO_SEARCH_ECONOMIC_RECEIPT_V3` has been consumed. Producer
`ead338b4d34a95b707ae1a140b1aa318a71e4f6a` independently reproduced the
fresh-state train trajectory and reached restore-verified `checkpoint_000`
with `2,000` strict candidates from `2,280` attempts and `1,964` behavior
families. The frozen validation gate then identified candidate
`1DC068A07C8B4C29BFE9C35A27A5948D9FA0503B0DECF2A601D36B35F512B038`
from `canonical_typed_random`, 1h, selection rank 9, whose matched control was
behavior-identical to primary. The repaired orchestration wrote
`checkpoint_validation_blocked` with exact RNG, policy, population, archive,
ledger, receipts, arm state, and failure identity, then terminated normally.
No validation optimizer/archive write, checkpoint continuation, rescue,
reseed, tuning, sealed read, arm qualification, Alpha claim, or next Arena
occurred.

The V3 validation result exposed two evaluator implementation defects rather
than a negative market result. `ConditionGate` and safe-division operators
could turn unavailable inputs into valid zeroes, so primary and controls did
not necessarily share transformed finite support. Validation also
materialized rolling features from the validation boundary without the
candidate's prior feature-only warm-up. Source commit
`cc9614e6485dafc8d37f951cee4c1437f076e2f8` repairs both defects, adds
fail-closed transformed-support gates, persists warm-up provenance, and passes
`338` tests. `CRYPTO_SEARCH_ECONOMIC_RECEIPT_V4` authorized exactly one new
fresh-state campaign on the unchanged 115-field OI/mark x aggTrades carrier
and existing Binance target/reward/cost authority. It imported no candidate,
reward, RNG, distribution, population, policy, archive, checkpoint, or
transition memory from V1-V3.

V4 producer `94c79d0a8e559b7223fa1eaddb2d07ca76c1e628` completed the exact
five-arm `checkpoint_000`: `2,000` strict candidates from `2,298` attempts,
`1,962` behavior families, eight-worker memory fallback, and exact checkpoint
restore. Train-only diagnostics contained two matched positives and 91
positive joint search rewards, but these are not validation, Alpha, OOS, or
promotion evidence. Before checkpoint_001, validation candidate
`88D6330B8CC329460CBFA97E810FCE4109A5159A796FA4D4E9F2C8D00F0AD88D`
from canonical typed random, 1h, selection rank 13, produced
`CONTROL_BEHAVIOR_EQUALS_PRIMARY`. Its 719-hour feature warm-up and transformed
support checks passed; train primary/control behaviors were distinct. The
historical defect was orchestration scope: one candidate whose
validation-period cross-sectional mapping degenerates to its control terminated
the whole equal-count validation stage instead of recording an arm-local
validation failure. V4 stopped normally at `checkpoint_validation_blocked`,
consumed no remaining 18k budget, read no sealed partition, wrote no validation
optimizer or archive state, and started no rescue, reseed, OOS, promotion, or
next Arena. Its receipt is consumed and no arm is qualified.

The retained validation orchestrator now records every known candidate-local
constructibility degeneration in the validation ledger, then deterministically
backfills from the next frozen train-ranked candidate within the same arm and
horizon. It does not use validation reward for selection and cannot write
policy, archive, candidate-generation, or holdout state. An arm exits only when
its frozen pool cannot supply the receipt-bound equal matched count; if the
typed-random control cannot supply that count, other arms cannot qualify. The
checkpoint persists attempted, evaluated, and failure counts plus exact failure
identities and restores without reevaluation. The normalized runtime-binding
component hash is
`3C62C389787E8035A0FC6918B2623FC953FADB71ECB401D93113D45B4585282A`;
all consumed receipt heirs remain `run_authorized=false`. Verification is
source/synthetic only: `345 passed, 1 warning`; no candidate or market pair was
evaluated and no historical V4 artifact was replayed or rewritten. The control-arm terminal path
now also closes a completed equal-count validation cleanly at
`checkpoint_validation` when canonical typed random fails its economic
kill-line, instead of reaching an undefined next-checkpoint allocation.

`CRYPTO_SEARCH_ECONOMIC_RECEIPT_V5` is now consumed. Producer
`a6946df8b9b24db8572e48a5f8b79ef621feb0f9` ran one independent fresh-state
campaign on the unchanged 115-field carrier, Binance target, joint reward,
5 bps cost, and frozen seeds. The memory gate selected 8 workers. It completed
restore-verified `checkpoint_000` with 2,000 strict candidates from 2,298
attempts and 1,962 behavior families. The repaired validation path recorded
the prior 1h random candidate's `CONTROL_BEHAVIOR_EQUALS_PRIMARY` as one
candidate-local failure, then deterministically backfilled it; random attempted
129 candidates and all three current arms completed exactly 128 matched
validation evaluations, 64 at 1h and 64 at 4h.

The typed-random validation ensemble then failed all four frozen economic
conditions: net mean `-0.0001782358`, non-overlap floor Sortino `-31.9044694`,
matched increment `-0.0002523015`, and control-not-dominant false. CEM V2 and
Evolution V2 were constructible at equal count, but their economic kill-lines
were not adjudicated after the required random baseline failed. The runner
wrote restore-verified `checkpoint_validation`, marked all three arms `EXITED`,
and stopped without allocating the remaining 18k budget. The terminal status
is `ENGINE_VALIDATION_BLOCKED`; no arm or archive qualifies for a future Arena.
There was no tuning, reseed, rescue, prior-state import, holdout/OOS/challenge/
forward read, promotion, latent training, operator expansion, or second run.

The existing-ledger-only V1.4 failure decomposition completed with zero new
candidate evaluations and zero market budget. It found that `666/1,200` Stage-B
final increments were gross-positive, only `26` were net-positive, and `640` of
the `666` gross-positive increments were cost sign-killed after the generic
5 bps full-L1 cost. The target audit also established that the prior target mapping
was venue-dependent (Bybit/Hyperliquid/OKX priority mix: 88.50%, 7.41%, and
4.09%; `126/144` assets changed priority venue), with decision
`HOLD_ADAPTIVE_TARGET_EXECUTION_AND_TURNOVER_REPAIR_FIRST`.

Search Engine V1.4 built one aligned `71 OI/mark + 44 aggTrades` carrier and
froze the longest pre-reward continuous eligible block: 7,337 hours from
2025-08-29 07:00 UTC through 2026-07-01 00:00 UTC, with 144 assets ever
eligible and 58-143 active per hour. Stage A completed 64 constructibility
candidates and verified five atomic checkpoint restores across the campaign.
Stage B completed exactly 1,200 fresh typed-random candidates: 600 binary
baselines plus 150 candidates for each of four hierarchical OI/flow/state
tuples. All were compile-valid, exact-unique, matched-control-valid,
full-cost-evaluated, and behavior-family unique. Pair reward mean was
`-5.235040`, exact-count top decile was `-2.189121`, and no binary,
interaction, conditional, or final matched-positive discovery occurred. The
frozen semantic gate therefore held Stage C before CEM or Evolution consumed
budget. Engineering integrity is `PASS`; research remains `HOLD_RESEARCH`;
future new-data Arena qualification remains empty.

Search Engine V1.3 reused the existing 2024H1 physical carrier to evaluate
4,000 fresh-state Broad39 x aggTrades44 candidates. Every candidate contained
both semantic sources and completed dual-axis matched controls, turnover, and
cost evaluation. The run used 7,165 attempts, retained 3,848 behavior
families, restored four checkpoints exactly, and recorded zero sealed reads
and zero positive matched discoveries. CEM improved density and mean reward
but lost top-decile reward; Evolution improved reward ordering but lost
behavior-family discovery and reached a 9.125% duplicate rate. No arm qualifies
for a future new-data Arena. Engineering integrity is `PASS`; research remains
`HOLD_RESEARCH_FIXED_RETROSPECTIVE_CROSS_CARRIER`. OI/mark was not joined
because it has no common verified target window with another active carrier;
Core3 remained outside the 121-asset Arena because its qualified context has
only three assets. The right-axis ledger trace gap is closed for V1.3 without
rerunning the prior 768 candidates.

Carrier Activation & Fresh-State Matched Gate V1 reused the existing 235-field
carrier surface and Search Engine implementation. It completed 768 fresh-state,
dual-axis, matched, cost-evaluated candidates: 256 full-44 aggTrades, 256
Core3-81, and 256 available OI/mark-71. All six checkpoints restored exactly;
sealed reads and promotion remained zero. No carrier produced a positive
matched discovery and no CEM/Evolution arm dominated typed random across the
frozen density, family-discovery, mean-reward, and top-decile dimensions.
Status is engineering `PASS`, research `HOLD_RESEARCH`, future larger-Arena
qualification `NONE`. OI/mark PIT-universe limitations and liquidation HOLD
remain unchanged. The right-axis waterfall is not separately persisted in the
ledger and must be added before any larger Arena without rerunning this gate.

Search Surface Integration V1 completed at producer source
`caa4500485995119a908790508030e305add6841`. Four independent
`RawPanelStore` carriers expose 235 runtime-active fields with actual runner
load, candidate-local minimum-three-asset support, compiler/matched-control
materialization, and deterministic replay: Broad39 `39/39`, independent Core3
`81/81`, Top200 aggTrades `44/44`, and ranks51-200 OI/mark `71/96`. The
remaining 25 engineering fields are explicit source-unavailable HOLDs because
they have zero finite support in the full delivered OI/mark root; no source
value was filled or synthesized. Liquidation remains schema-observed inventory only and Top50
OI/mark remains raw-only. The independent checker passed after recomputing
source/config/carrier identities, the full OI root bundle, and both aggTrades
TAR SHA256 values. Market pair evaluations, reward reads, sealed reads, Alpha
claims, future-Arena qualification, and promotion are all zero/false.

Unified Field Management V1 completed as a deterministic compiled management
view over the existing inventory, lineage, ontology, approval, derived-recipe,
token, and carrier authorities. It records 5,509 canonical management
identities, 5,211 existing lazy derived views, 235 independent carrier
bindings, 852 typed-role bindings, four provenance-only exclusions, and zero
fatal authority conflicts. It creates no field authority, ontology, approval
registry, materializer, compiler, AST, database, or Graph layer; candidate and
carrier identities are unchanged, and no market search or reward read ran.

Closure repair binds all regenerated runtime artifacts to production commit
`f21ed7d1375904f62cb0cc03abb350ea56f911cd`, adds a 5,638-row first-breakpoint
reachability matrix, and expands the catalog authority joins. One nonfatal
carrier-scoped PIT-authority difference for `agg_trade_count` is explicit;
fatal type/unit/lag, lineage, approval, and ontology-semantic conflicts remain
zero. The prior statement of zero total conflict rows is superseded by this
fatal-versus-scoped distinction.

The preceding one-run fresh-state Search Engine V1.2 exception completed at producer
source `395a972a99c869f1c6acc24c6a167939b9f0857e`. It counted exactly 2,000
compile-valid, exact-unique, matched-control-valid, fully cost-evaluated
candidates from 3,598 raw attempts over two atomic 1,000-candidate
checkpoints; both checkpoints passed independent state, receipt, transition
memory, rotating-lane, and exact restore replay. Memory preflight failed closed
from 10 to 8 workers and never used 12. Against equal-count typed random,
Evolution V2.2 improved strict/raw by `+0.15753484`, balanced strict throughput
by `+16.264802` candidates per CPU-hour, mean reward by `+0.79537693`, and
top-decile reward by `+1.29472341`. It nevertheless produced 75 fewer behavior
families per 1k, lost `97.067482` new families per CPU-hour, and reached a 7.9%
duplicate rate against random's 0%. Campaign-local collision memory blocked 67
transitions and skipped three pre-evaluation repeats, but did not satisfy the
frozen discovery or duplicate gates. Engineering integrity is `PASS`; the
V2.2 increment is `REJECT_INCREMENT_NOT_DEMONSTRATED`; research remains
`HOLD_RESEARCH_SPENT_FIXED_RETROSPECTIVE_COHORT`; future qualified arms remain
`[]`. No larger run, OOS, challenge, recent, May-stress, forward, promotion,
latent, relational, sealed read, or rescue rerun was started.

## Current decisions

```text
REPOSITORY_PROVENANCE_CLOSURE_COMPLETED
CRYPTO_FRONTIER_PROVENANCE_CLOSURE_ACCEPTED
CURRENT_DATA_UNDERPOWERED
FINANCIAL_GATE_HOLD_RESEARCH
CRYPTO_INTERNAL_SEARCH_INSTRUMENT_CAPABILITY_QUALIFIED
CRYPTO_COMPOSITIONAL_GRAMMAR_BOTTLENECK_CONFIRMED
CURRENT_FIELD_FOUR_POLICY_CONTINUATION_COMPLETED
POLICY_PRODUCTIVITY_INCREMENT_OBSERVED
CEM_DISTRIBUTION_SEARCH_UPGRADE_ENGINEERING_EVIDENCE_ONLY
EVOLUTIONARY_TYPED_MUTATION_UPGRADE_ENGINEERING_EVIDENCE_ONLY
POLICY_UPGRADE_CANARY_ENGINEERING_EVIDENCE_ONLY
REAL_POLICY_UPGRADE_FUTURE_ARENA_QUALIFICATION_SUSPENDED
SEARCH_ENGINE_V1_20K_ARENA_ENGINEERING_EVIDENCE_ONLY
SEARCH_ENGINE_V1_POST_AUDIT_RESEARCH_HOLD
SEARCH_ENGINE_V1_FUTURE_ARENA_COMPONENT_QUALIFICATION_SUSPENDED
PANEL_CONTEXT_POST_JOIN_RECOMPUTE_REQUIRED
OVERLAPPING_HORIZON_HAC_LCB_REQUIRED
SEARCH_ENGINE_V1_PROCESS_CPU_ACCOUNTING_FROZEN
SEARCH_ENGINE_V1_PREPUBLICATION_CHECKPOINT_RESTORE_REQUIRED
TYPED_EVOLUTION_V2_REPAIRS_VERIFIED_DISCOVERY_INCREMENT_NOT_DEMONSTRATED
SEARCH_ENGINE_V1_EXACT_CHECKPOINT_RESTORE_VERIFIED
AGGTRADES_SEARCH_SYSTEM_CANARY_V1_ENGINEERING_PASS
AGGTRADES_SEARCH_SYSTEM_CANARY_V1_RESEARCH_HOLD
AGGTRADES_SEARCH_SYSTEM_CANARY_FUTURE_ARMS_NONE
CEM_V2_UNIT_COMPUTE_DENSITY_INCREMENT_OBSERVED
EVOLUTION_V2_REPAIR_EFFICIENCY_INCREMENT_OBSERVED
EVOLUTION_V2_BEHAVIOR_DISCOVERY_INCREMENT_NOT_ESTABLISHED
BEHAVIOR_ARCHIVE_DUPLICATE_REPLACEMENT_OPERATIONALLY_VERIFIED
CAMPAIGN_LOCAL_PER_RUN_MEMORY_ONLY
LATENT_SEARCH_PRIORITY_MODEL_REMAINS_DEFERRED_AFTER_V1_2
THRESHOLDED_WORKING_SET_TRIM_QUALIFIED
NEXT_NEW_DATA_ARENA_WORKER_LIMIT_10
IMPLEMENTATION_SPECIFIC_INFORMATIVE_NEGATIVE
GRAPH_RAW_CURRENT_SEPARATION_ACTIVE
CURRENT_CONTRACT_CAPSULE_ACTIVE
CURRENT_SEMANTIC_AUTHORITY_CLASSES_EXPLICIT
MULTI_PARADIGM_ARENA_ACTIVE_NON_FORMAL_REFERENCE_REPAIRED
CRYPTO_FIELD_INFORMATION_V0_COMPLETED
BROAD_PURGED_CALIBRATED_STICKY_INCREMENT_NOT_ESTABLISHED
EXECUTED_RESIDUAL_ORTHOGONAL_VARIANTS_ARCHIVED
DYNAMIC_UNIVERSE_RELATIONAL_COST_AWARE_POLICY_STAGE0_LOCAL_COMPLETED
RELATIONAL_POLICY_STAGE1_LAYER_ATTRIBUTION_COMPLETED
RELATIONAL_REPRESENTATION_INCREMENT_NOT_ESTABLISHED
RELATIONAL_STAGE2_NOT_AUTHORIZED
RELATIONAL_STAGE1_TEMPORARY_SCAFFOLD_EVICTED
LIQUIDATION_SUPPLIER_INGRESS_QUALIFIED_QUARANTINED
BINANCE_FORCE_ORDER_FORWARD_CAPTURE_ACTIVE
NEW_PERFORMANCE_SEARCH_FROZEN
SEARCH_ENGINE_V1_1_ENGINEERING_PASS
SEARCH_ENGINE_V1_1_RESEARCH_HOLD
SEARCH_ENGINE_V1_1_FUTURE_ARMS_NONE
CEM_V2_1_INCREMENT_NOT_DEMONSTRATED
EVOLUTION_V2_1_INCREMENT_NOT_DEMONSTRATED
BEHAVIOR_NICHE_CAUSAL_DUPLICATE_REDUCTION_NOT_ESTABLISHED
SEARCH_ENGINE_V1_2_ENGINEERING_PASS
SEARCH_ENGINE_V1_2_RESEARCH_HOLD
SEARCH_ENGINE_V1_2_FUTURE_ARMS_NONE
EVOLUTION_V2_2_INCREMENT_NOT_DEMONSTRATED
BALANCED_ROTATING_MICROBATCH_EXECUTION_VERIFIED
CAMPAIGN_LOCAL_TRANSITION_COLLISION_MEMORY_VERIFIED
SEARCH_SURFACE_INTEGRATION_V1_ENGINEERING_PASS
SEARCH_SURFACE_RUNTIME_ACTIVE_FIELDS_235
SEARCH_SURFACE_DECLARED_SOURCE_UNAVAILABLE_HOLDS_25
BROAD39_CORE3_81_CONTEXT_SEPARATION_PRESERVED
LIQUIDATION_AND_TOP50_OI_MARK_REMAIN_QUARANTINED
SEARCH_SURFACE_FUTURE_ARENA_NOT_AUTHORIZED
SEARCH_ENGINE_V1_3_CROSS_CARRIER_ENGINEERING_PASS
SEARCH_ENGINE_V1_3_CROSS_CARRIER_RESEARCH_HOLD
SEARCH_ENGINE_V1_3_FUTURE_ARMS_NONE
SEARCH_ENGINE_V1_3_RIGHT_AXIS_LEDGER_TRACE_VERIFIED
OI_MARK_CROSS_CARRIER_NO_COMMON_VERIFIED_TARGET_WINDOW_SUPERSEDED_BY_V1_4_ALIGNED_CARRIER
SEARCH_ENGINE_V1_4_OI_FLOW_ALIGNED_CARRIER_ENGINEERING_PASS
SEARCH_ENGINE_V1_4_HIERARCHICAL_THREE_AXIS_EXECUTION_VERIFIED
SEARCH_ENGINE_V1_4_SEMANTIC_GATE_HOLD
SEARCH_ENGINE_V1_4_STAGE_C_NOT_RUN
SEARCH_ENGINE_V1_4_FUTURE_ARMS_NONE
SEARCH_ENGINE_V1_4_FAILURE_DECOMPOSITION_PASS
SEARCH_ENGINE_V1_4_BINANCE_TARGET_EXACT_REPLAY_PASS
SEARCH_ENGINE_V1_4_FULL_WATERFALL_PERSISTED
SEARCH_ENGINE_V1_4_TARGET_EXECUTION_CONTRACT_REPAIRED_FOR_DIAGNOSTIC
SEARCH_ENGINE_V1_4_GROSS_PERSISTENCE_DIAGNOSTIC_PASS
SEARCH_ENGINE_V1_4_TURNOVER_REPAIR_NEXT
SEARCH_ENGINE_V1_4_ADAPTIVE_SEARCH_NOT_STARTED
SEARCH_ENGINE_V1_4_COST_SIGN_KILL_DOMINANT
SEARCH_ENGINE_V1_4B_NOT_AUTHORIZED
SEARCH_ENGINE_V1_5_OPERATOR_EXPANSION_NOT_AUTHORIZED
SEARCH_ENGINE_PAIR_REWARD_SOLE_ORDERING_AUTHORITY_REVOKED
SEARCH_ENGINE_PHASE3CM_STYLE_REWARD_DIAGNOSTIC_CODE_RETAINED
SEARCH_ENGINE_ECONOMIC_OPTIMIZER_AUTHORITY_SUSPENDED
SEARCH_ENGINE_PAIR_REWARD_MATCHED_DIAGNOSTIC_ONLY
SEARCH_ENGINE_LEGACY_STATE_WITHOUT_SEARCH_REWARD_FAIL_CLOSED
SEARCH_ENGINE_HISTORICAL_POLICY_REWARD_CLAIMS_SUSPENDED
SEARCH_ENGINE_VALIDATION_KILL_LINE_CONTRACT_BOUND
SEARCH_ENGINE_FROZEN_VALIDATION_ORCHESTRATION_SOURCE_COMPLETE
SEARCH_ENGINE_ECONOMIC_V5_AUTHORIZATION_CONSUMED
SEARCH_ENGINE_ECONOMIC_V5_CHECKPOINT_000_RESTORE_VERIFIED
SEARCH_ENGINE_ECONOMIC_V5_VALIDATION_EQUAL_COUNT_COMPLETE
SEARCH_ENGINE_ECONOMIC_V5_RANDOM_CONTROL_KILL_LINE_FAILED
SEARCH_ENGINE_ECONOMIC_V5_ENGINE_VALIDATION_BLOCKED
SEARCH_ENGINE_ECONOMIC_V5_REMAINING_18K_NOT_ALLOCATED
SEARCH_ENGINE_ECONOMIC_V5_NO_ARM_QUALIFICATION
SEARCH_ENGINE_ECONOMIC_V5_NO_RESCUE_RERUN
SEARCH_ENGINE_ECONOMIC_V5_NO_PRIOR_STATE_IMPORT
SEARCH_ENGINE_VALIDATION_CONTROL_ARM_TERMINAL_PATH_VERIFIED
SEARCH_ENGINE_ECONOMIC_RECEIPT_V1_SOURCE_QUALIFIED
SEARCH_ENGINE_ECONOMIC_RECEIPT_RUN_AUTHORIZATION_CONSUMED
SEARCH_ENGINE_ECONOMIC_V1_ENGINE_BUDGET_EXHAUSTED
SEARCH_ENGINE_ECONOMIC_V1_EMERGENCY_CHECKPOINT_RESTORE_VERIFIED
SEARCH_ENGINE_ECONOMIC_V1_INCOMPLETE_IMBALANCED_NO_ARM_QUALIFICATION
SEARCH_ENGINE_ECONOMIC_V2_AUTHORIZATION_CONSUMED
SEARCH_ENGINE_ECONOMIC_V2_CHECKPOINT_000_RESTORE_VERIFIED
SEARCH_ENGINE_ECONOMIC_V2_ENGINE_VALIDATION_BLOCKED
SEARCH_ENGINE_ECONOMIC_V2_NO_ARM_QUALIFICATION
SEARCH_ENGINE_ECONOMIC_V2_NO_RESCUE_RERUN
SEARCH_ENGINE_ECONOMIC_V3_AUTHORIZATION_CONSUMED
SEARCH_ENGINE_ECONOMIC_V3_CHECKPOINT_000_RESTORE_VERIFIED
SEARCH_ENGINE_ECONOMIC_V3_VALIDATION_BLOCKED_CHECKPOINT_VERIFIED
SEARCH_ENGINE_ECONOMIC_V3_NO_ARM_QUALIFICATION
SEARCH_ENGINE_ECONOMIC_V3_NO_RESCUE_RERUN
SEARCH_ENGINE_ECONOMIC_V4_AUTHORIZATION_CONSUMED
SEARCH_ENGINE_ECONOMIC_V4_CHECKPOINT_000_RESTORE_VERIFIED
SEARCH_ENGINE_ECONOMIC_V4_VALIDATION_BLOCKED_CHECKPOINT_VERIFIED
SEARCH_ENGINE_VALIDATION_CANDIDATE_LOCAL_FAILURE_PERSISTED
SEARCH_ENGINE_VALIDATION_FROZEN_RANK_BACKFILL_VERIFIED
SEARCH_ENGINE_VALIDATION_ARM_LOCAL_EQUAL_COUNT_FAIL_CLOSED
SEARCH_ENGINE_VALIDATION_CHECKPOINT_RESTORE_WITH_FAILURES_VERIFIED
SEARCH_ENGINE_ECONOMIC_V4_NO_ARM_QUALIFICATION
SEARCH_ENGINE_ECONOMIC_V4_NO_RESCUE_RERUN
SEARCH_ENGINE_V1_CONTROLS_PARTIAL_CARRIER_ROLE_RESOLUTION_REPAIRED
CAPABILITY_STRICT_FEEDBACK_GLOBAL_SCOPE_REVOKED
CAPABILITY_STRICT_FEEDBACK_AUTHORITY_RETAINED
UNIFIED_FIELD_MANAGEMENT_V1_COMPILED_VIEW_ACTIVE
UNIFIED_FIELD_MANAGEMENT_V1_NOT_FIELD_AUTHORITY
UNIFIED_FIELD_MANAGEMENT_V1_AUTHORITY_CONFLICTS_ZERO
CRYPTO_TEMPORAL_POLICY_VALIDATION_COMPLETE
CRYPTO_TEMPORAL_POLICY_VALIDATION_SPLIT_51_09_48_91_PASS
CRYPTO_TEMPORAL_FIXED_DEVELOPMENT_FLOW_20_20_60_QUALIFIED
CRYPTO_TEMPORAL_ALPHA_QUALIFICATION_HOLD
FORWARD_SEALED
NO_CANDIDATE_PROMOTION
NO_CROSS_SPRINT_ADAPTIVE_MEMORY
```

## Accepted identities

- Provenance closure: branch `origin/audit/evalreset-collapse-forensics-20260711`, commit `4726795f61052470d56e2d1475e4f6da9d262943`, tag `crypto-frontier-provenance-closure-20260714`.
- Current research branch: `replay/crypto-search-engine-v1-4-binance-target-20260729`.
- Explicit/latent implementation qualification: `7389a36ebb4ee62f57aeb818cf4db7157bd1ea9f`.
- Field Information V0 source: `057e31df71f55f9e3a6e8ea3b48d53293d7d2e13`; run identity SHA256: `623036F48CBC8089CC61E81876F3A1E14199FC781456BF9F39183F8A129E53D6`.
- Latest qualified Graph closure before this maintenance phase: `920e0ad35c07e2e2cee3ed2be8ad0753937f86f4`.
- Accepted closure bundle SHA256: `99C0DACAF12F17DA6B7705DDBFCE9BAD996143082301F47BCA7E690071140EF2`.
- 18-month compositional bundle SHA256: `EABBD9B4844A0589A1C409A274688D2D2C41B9793A0B584BE54909C0AC27D492`.
- Current-field four-policy continuation: producer source `2350405595446b1c8615537666857ce5342159e3`; base closure `a115913ae333696482059b497472864871cebc9f`; runtime bundle SHA256 `13A521BE23B193EA3BFD9B4B319E69280BD9932A1B8A394EB4E3A73AD2D577EB`; compiler bundle SHA256 `E9A438114E8619E39B5535251F0B0A91E3905B61259E3A0ABB7745E94A5A6842`; raw-cache bundle SHA256 `D120C0444B2A5828CBE0C7B538DEF81A1D2E50689C941F4B1A96D2AE60D93FED`; raw-cache identity SHA256 `CBD66860C54314A8376A5EA126E4FE5A9760FB766D250AD1F966DC1007EE99F0`.
- Real policy-upgrade canary: producer source `33d44a57af99a1fb506216b336351674a10d0488`; original fail-closed bundle SHA256 `267CAB35DC4E1709DD77475BA59FCE4FC130A2AC7E6644D6B6A41803A52001F6`; immutable pair artifact SHA256 `F4D34B76DAEEF6E19E5CEB39E4E09F542F75490AF2B957F148AB5B34028E4222`; qualifier source `3d9a9ea2951216d66c72a2b70c539d109975375b`; supersession bundle SHA256 `EB705D416523D1C42EAE75B86FF4DF230B72106D77FB90CF381106FEC2D745BA`.
- Search Engine V1 historical engineering evidence: base `bbb0e696bc5f560f733dd4e9bfe263f11e4bb840`; producer source `baab218fdd9441fbf5851ba7ed8c587b0c4cae15`; artifact bundle SHA256 `2E0EAED26747E1B97F5F4C06482BE61337965DC0CAAA2A5B1C48C06625657288`; frozen contract SHA256 `24EFF2FDC11A4FFD47FCD61F638ABEC0B82FF13A7804AF378B244402B382F264`; legacy cache identity SHA256 `CBD66860C54314A8376A5EA126E4FE5A9760FB766D250AD1F966DC1007EE99F0`; remediation source `369dbb8fadf7a1308fd1820da37e5cd95ffc8450`; engineering integrity `PASS`; component qualification `HOLD_POST_AUDIT_REMEDIATION_REQUIRED`; future qualified arms `[]`; sealed reads `0`.
- Fresh-state aggTrades Search-System Canary V1: producer source `5a17a91732a7aca7ec53cf9e10963faf2998a649`; artifact bundle SHA256 `880BC5D5AD5F47242FD534AD4AD0A9C40C4BFBE91A76523E773CA487F9A4EC74`; frozen contract SHA256 `FD61656C7D53A682B8E8CA4E9C704B8D655F9EE3CFC2B3124B796243E1E06FAD`; data-cache identity SHA256 `127C1C4EBA099A5AB1F2CE8AE0E78564AEABBAE83D12C7FEC0FE784191C3CD04`; 2,000 strict candidates; 3,452 attempts; 2/2 exact-restored checkpoints; 1,946 behavior families; engineering integrity `PASS`; research `HOLD_RESEARCH_FIXED_RETROSPECTIVE_COHORT`; future qualified arms `[]`; sealed reads `0`.
- Search Engine V1.1 Behavior-Niched Arena: producer source `17ac5de989dec464b0c4903256f3f7662eeb9778`; artifact bundle SHA256 `E27E0F116CBE1D1FB3F23D76178688AA44E4D1DE6738D02284F3D6F6FCA729A8`; frozen contract SHA256 `A94F0AE452FF626823E4408A786DBC7B7979EDBAEB5843950A10853548A393CC`; data-cache identity SHA256 `127C1C4EBA099A5AB1F2CE8AE0E78564AEABBAE83D12C7FEC0FE784191C3CD04`; 3,000 strict candidates; 5,444 attempts; 2/2 exact-restored checkpoints; 2,916 behavior families; 42 champion replacements; engineering integrity `PASS`; research `HOLD_RESEARCH_SPENT_FIXED_RETROSPECTIVE_COHORT`; CEM V2.1 and Evolution V2.1 increments rejected; future qualified arms `[]`; sealed reads `0`.
- Search Engine V1.2 Balanced Collision Arena: producer source `395a972a99c869f1c6acc24c6a167939b9f0857e`; artifact bundle SHA256 `F142EB44FE91C349A54F0D7C78C704A491658B7FBC0B30402E0B08E5B8459296`; frozen contract SHA256 `620B40B5AEE6634BB719E3AA0FA95B778939CB66264869DC7E851A8949EB1C83`; data-cache identity SHA256 `127C1C4EBA099A5AB1F2CE8AE0E78564AEABBAE83D12C7FEC0FE784191C3CD04`; 2,000 strict candidates; 3,598 attempts; 2/2 exact-restored checkpoints; 1,916 behavior families; 250 balanced rotating micro-batches; engineering integrity `PASS`; research `HOLD_RESEARCH_SPENT_FIXED_RETROSPECTIVE_COHORT`; Evolution V2.2 increment rejected; future qualified arms `[]`; sealed reads `0`.
- Search Engine V1.4 OI/flow conditional gate: producer source `018be6caca5c7ad294729c17294295283589ec7d`; artifact bundle SHA256 `3AE3E801A58C1C3F9AEABFB80F7E748AF933C026BA2A99EB1E6EDB429F24BF7E`; aligned-cache identity SHA256 `E8BFD15AF1EA58807A75868D52AD3535126DFB77CEDEB404EEE8E690AA58F2BA`; `71 OI/mark + 44 aggTrades`; 1,264 strict candidates from 1,958 attempts; 5/5 exact-restored checkpoints; 1,264 behavior families; Stage B `HOLD_ADAPTIVE_GATE`; Stage C not run; future qualified arms `[]`; sealed reads `0`.
- Crypto Search Economic V1 partial terminal run: producer source `17d5b5f19acd1366cf5b8f332249d78e918556f1`; closure source `da7842dabacf7c98e62475014666877eeda86664`; artifact bundle SHA256 `D639AB3BDD671BB71725BD7013BE61B2CD698C7BEDD08C9481F44DE309B8A870`; aligned-cache identity SHA256 `E8BFD15AF1EA58807A75868D52AD3535126DFB77CEDEB404EEE8E690AA58F2BA`; 1,190 strict candidates from 95,776 attempts; emergency restore `PASS`; status `ENGINE_BUDGET_EXHAUSTED`; research `HOLD_INCOMPLETE_IMBALANCED_CAMPAIGN`; future qualified arms `[]`; sealed reads `0`.
- Crypto Search Economic V4 terminal run: producer and closure source `94c79d0a8e559b7223fa1eaddb2d07ca76c1e628`; artifact bundle SHA256 `136A03D53B36CBC76F9BD2B491E1CADDD9C03DE5B95B43B35FE5517AFD56BF84`; 2,000 strict candidates from 2,298 attempts; 1,962 behavior families; checkpoint_000 and checkpoint_validation_blocked restore `PASS`; status `ENGINE_VALIDATION_BLOCKED`; reason `CONTROL_BEHAVIOR_EQUALS_PRIMARY`; research `HOLD_ENGINE_VALIDATION_BLOCKED`; future qualified arms `[]`; sealed reads `0`.
- Crypto Search Economic V5 terminal run: producer source `a6946df8b9b24db8572e48a5f8b79ef621feb0f9`; artifact bundle SHA256 `F8590101FE6EF9ABE2B3C9D796880B894C215BDD4195789842EDBC72C4A38B92`; frozen contract SHA256 `00638EC5A872A43A1420AA522DC9AC90D20F5F615569E6B306EDAEED4A1DFCE7`; 2,000 strict candidates from 2,298 attempts; 1,962 behavior families; checkpoint_000 and checkpoint_validation restore `PASS`; 384 equal-count validation evaluations plus one persisted/backfilled candidate-local failure; status `ENGINE_VALIDATION_BLOCKED`; reason `VALIDATION_CONTROL_ARM_FAILED_KILL_LINE`; research `HOLD_ENGINE_VALIDATION_BLOCKED`; future qualified arms `[]`; sealed reads `0`.
- Search Engine V1.4 existing-ledger failure decomposition: producer source `16fc1feabc79f711d4b7b728eac2c2b9d00f91e5`; input bundle SHA256 `0DE62CB1D38F10A0477F6E8D98B9A0EB2A863A7B8CD5531F03A909592203EFEB`; artifact bundle SHA256 `D50D37ECB025E09B5BDEDADDC3ED8F6D60CE5F6CAB7A770203F5FAFD13A38E96`; five diagnostic tables; zero candidate evaluations, market budget, sealed reads, OOS, or promotion; adaptive V1.4b and operator expansion not authorized.
- Search Engine V1.4 Binance target exact replay: producer source `fe82d94e5530d13e933c0f3db5d2b4869ad34521`; artifact commit `9dbb4ce52f5db218683e10c5463e2e6554c7b060`; aligned cache identity `E8BFD15AF1EA58807A75868D52AD3535126DFB77CEDEB404EEE8E690AA58F2BA`; target identity `27F780D458CBA50D6C82393F7DFDA396AC3994724645D112C4F8EF0ACDA865F0`; frozen contract `ADA30AE30B55B449F7FBE2C6B8E28E41757F4A8CEA87B5513D5277DA7FE2BF85`; run manifest SHA256 `6458EE3F8272A54F468411610F45CF5D3A3FC361DE6DCA5EDC98F7AC61599E46`; final decision SHA256 `C369FF6B1D7C9FB7F4CC39556B58A66F3A4EA82766354798C927162F639FAA56`; 4 checkpoints; exact replay ledger and full/ monthly waterfalls persisted; gross persistence diagnostic passed; research qualification `HOLD_SPENT_DEVELOPMENT_EXACT_REPLAY`; next action turnover repair then bounded adaptive.
- Search Surface Integration V1: producer source `caa4500485995119a908790508030e305add6841`; source-binding SHA256 `D1AF43DAB909256A8B9EF171E70548B58DC3CC524852194071263A636AA87C7D`; run-manifest SHA256 `5959D31E6218E0A12EDE2730D68F97D012B7AC9164AC06EA8BD31850A9BE7BF2`; carrier-manifest SHA256 `F4E1A3F81B7C7F80097FE42B52DEBE5E086C884D7123FB854A360F3868E691D8`; frozen-contract identity SHA256 `28368DC76F3C3D150A8B1EAD8C9D13011CB6B754AAFFF67BF1D7DFBD42A6B176`; aggTrades full-44 carrier identity SHA256 `0F8BDE06E35D62E7B64BD3A43866C19796D84E65CF8F096465E9CA63B75630B6`; 260 declared engineering fields, 235 runtime-active, 25 explicit source-unavailable HOLD; checker `PASS`; research and future Arena `HOLD`; market pair evaluations/reward/sealed reads `0`.
- Unified Field Management V1: producer source `43739edd18c264bfa9b4ce11a3953c95b6ca58db`; config SHA256 `C6D0A1A9C1E24EB7FC0C2A80A400D4C8AA4A677A4E4979645920F7D7AEF4FBE8`; committed run-manifest SHA256 `A2DDFC630F9FF48F5804AAB816A92AFB62E95A75550669D6DD8BC14705791478`; 5,509 canonical management records, 5,211 existing lazy derived views, 235 independent carrier bindings, four provenance-only exclusions, zero authority conflicts; compiled view only, not field authority; market search/reward/sealed reads `0`.
- Unified Field Management V1 closure repair: production source `f21ed7d1375904f62cb0cc03abb350ea56f911cd`; artifact commit `45c9936302418d2dd9e4b7ec7dd4e8e0790e009b`; production bundle SHA256 `BD72E2C8934B00BDCE32ADB720F322DC88F95705DFF7A9E0E64179957AD32E3B`; committed run-manifest SHA256 `F44A54C9F09AACB0FEB5E8E293041BBDE8E101F95CD1C7B3651E095E0A121FEC`; 5,638 reachability rows; one nonfatal scoped PIT-authority difference; fatal authority conflicts `0`; no market search or reward read.
- Bounded acceleration canary: execution producer `d77cdc4b0ff2ccf4662a690864be78b37e743605`; deterministic report-order repair `e806c15380e029ac00e662afec72a82620162d8f`; evidence bundle SHA256 `10E8002034399AD8B319F7EB4EE74FAB7B81E41C1943A38A37D44757301C38AB`; 512 fixed spent-development executions; no pair rerun during report repair.
- Localized qualification bundle SHA256: `0C6193E81FEAB8271B8BAE05AD04604D74494EAB2710794C59A7F42919DD68EB`.
- Liquidation ingress implementation: `d64a783dac4c148d1924f76acb7b8a80cbcc7f1a`; byte-stable evidence commit: `58ff34e48cb88acc0005e741c8aaa52d3528177e`; release identity SHA256: `C9717263EC6F97839466A4BC13D8DBA803E3D0D5854AE6E3A005F4C6F0F34D7A`.
- Core Pack consumption implementation source: `f01d0d22a40ae9949a027fe138c52998fb23c1ef`; evidence commit: `e3631d31ae5022b6765b0a333fb9c32015312c01`.
- Core Pack identity SHA256: `B6765D5A60B9A348A47A88BB53D503A48E024C1BAF83BCB14B2F4BF06E248D00`; resolved execution-contract identity SHA256: `35E54F79576A6D7A1D94AE697E8066CB9FB49CF9A97979259F39490E3281914E`; run identity SHA256: `7DE0F5FB394970C804AC483D42A63231687C461528AF0947D85855D91000A149`.
- Broad information Arena implementation source: `4aa96ba65a950adca07c4bdb9b0db734f729bdd0`; evidence commit: `edc3cda`; run identity SHA256: `E9DE6B6A98E6986D99E08571322CD66B0E2B5B145D3B392E251587FFDEE619E1`.
- Broad sticky mapping implementation source: `7fee8559c1819a779f4a5fc22e2ee21e4d84e807`; evidence commit: `66bb993`; run identity SHA256: `90FB47E5B54B410AF56B2B985E98AAD8077359E9364E6A233792A5BE66384439`.
- Broad prediction-scale audit source: `172340ac129b9f0ed79bfcbecd5126adfe662c76`; evidence commit: `39751d7`; run identity SHA256: `98493E159D5AA36A5C1BCC7E52F33D47B3C3B8E6D52FEE6BC332B288F66C7C35`.
- Purged Broad calibration replay source: `35546635450cba974457e90c0b0a3d0257689cd4`; evidence commit: `3bd334c7e11dcb3583a0b3ebba3c577242172fef`; run identity SHA256: `154731A3608CB3FFA4765E98F8C167C7776386F6115C51DCF5265D17FCF1035B`.
- Relational direct-weight vertical slice: initial implementation `2097fd70`; state/cost repair `dac123fb`; real dynamic-membership repair `78616e7156e6c48509a99c0afcaa75be33b7ae0c`; fail-closed smoke source `9c5f2f64691013033a0edf583fe57de86cd966c0`; field-view identity SHA256 `D48789F4BECC74536A077B2D6C092CBC23E789A7D4BBAF9BC61C825CF2592DC1`.
- Relational Stage-1 attribution: frozen source `7421d4c0ef78f9212f692c46fa9e023438257ed2`; evidence commit `0626dd4`; scaffold-expiry commit `c8af3c3396b380f190ca323e630ae59f6b54b706`; config SHA256 `EE9C8D55ACD7492A26984D58C888BBBDF96A3F185930FC16CE294B69F2467074`; parity SHA256 `A9F34935C9BE8B103449CDFCA2F61022F49B01919F1CB50E0630862B41C91B0F`; logical data identity `93CD5FA4587BC0813B8AC3BD20051F5A664664A82BF8766A7D06C69C38728E0F`; decision SHA256 `CB7963C83C280F4E53700ABFB6F7BBDB782BC8182AF13FED89DEBB1149B8C54F`.
- Bitfinex liquidation ingress source: `7a5dfee6a7d1097ca37b06d85f3c3882a8ece388`; evidence commit: `2c8086093412a70eaf3694359e7651bfe96f3ce6`; run identity SHA256: `DB8E56C85ABD2008ECF6F97E046ED00A2CCC571B2C517BCACA9F786CEAF5320A`.
- Binance forceOrder forward-capture snapshot source: `3bd334c7e11dcb3583a0b3ebba3c577242172fef`; evidence commit: `949b277845a8ad4945dc14b6b75339b9eb7acbaa`; capture identity SHA256: `22411352F986AB29B4AC2D3E0F5241486D86FA940D7A5C63B5D98FD3E13CB934`.

## Evidence-qualified position

- Qlib: the historical full/control comparison was `MODEL_FIT_DEGENERATE`. A frozen repair produced different predictions and weights, but 23 development dates fail adequacy requirements. Status: `EXTERNAL_PARADIGM_COMPARISON_DEGENERATE_FIXED` plus `DATA_ADEQUACY_UNDERPOWERED`.
- DeepDow: parameters and portfolio weights differ from control, so exact comparison, fit, and mapping collapse are not established. Its 156 overlapping windows do not provide enough independent blocks. Status: `DATA_ADEQUACY_UNDERPOWERED`.
- Internal search instrument: qualified only for the frozen finite grammar, deterministic synthetic reachability, mapping, cost, feedback, and survivor retention. It is not market alpha, open-generator recall, or OOS evidence.
- Observed-archive train surface: 2,549,139 rows, 13,200 unique hours, and 276 observed assets across the joined 2023H2/2024 train archive. It is not survivorship-complete; native aggTrades history remains much narrower.
- 18-month compositional run: 41 fields across 12 families, 500,000 proposal audit, 8,192 adaptive matched pairs, and zero sealed reads. Localized mechanisms did not supply independent evidence sufficient to issue a challenger.
- Current-field/current-compiler continuation: Broad 38+1 supplied 39 fields across 11 families; 500,000 legal proposals produced 251,892 exact-unique and 41,625 behavior-unique candidates. All 16 policy/seed lanes completed 512 adaptive pairs and deterministic replay. CEM-lite beat same-seed typed random on both mean and fixed top-decile reward in 4/4 seeds; Evolutionary-lite did so in 3/4. These gates independently recomputed exactly from the strict parquet. The policies are eligible for narrow real implementations, but average rewards remained negative, Evolutionary-lite was coverage-concentrated, and challenge instability prevented an economic challenger.
- Real policy-upgrade canary: all 20 lanes and 2,560 pairs completed with deterministic replay, unchanged raw cache, 6,844-second wall time, and 646,377,472-byte maximum worker RSS. Its execution evidence remains intact, but it shared the legacy raw-cache identity and iid overlapping-horizon pair evaluator now placed on post-audit HOLD. Its former future-Arena component qualification is suspended; the old mean/top-decile margins are historical diagnostics only.
- Search Engine V1 post-audit position: the historical campaign still proves exact counting, compiler/receipt/replay integrity, atomic checkpoint restoration, and bounded campaign-local state. It does not currently qualify any arm or archive for a future Arena. Partition-local `active_universe_size`, `age_percentile_active_universe`, and `history_length_hours` polluted candidate inputs and every behavior-family PIT regime; 121/151 matched-positive candidates and 51/63 matched-positive families used at least one affected field. The overlapping 4h primary reward also used iid hourly uncertainty, and the ledger did not preserve the full matched monthly waterfall. Status: historical engineering integrity `PASS`; research and future-Arena component qualification `HOLD`; old productivity and family comparisons are historical diagnostics only.
- Fresh-state aggTrades Search-System Canary V1: 2,000/2,000 counted candidates and 2/2 exact-restored checkpoints passed with zero sealed reads. CEM V2 established a unit-compute valid-candidate-density increment and preserved typed-random behavior-family yield. Evolution V2 established repair/operator execution and higher reward ordering quality at matched count, but did not establish a behavior-discovery increment because family yield fell from `1,000` to `935` per 1k evaluations and duplicate rate rose from `0%` to `6.5%`. The Behavior Archive operationally detected duplicate behavior, retained reward champions, and performed 39 duplicate replacements; without an archive-off counterfactual this does not estimate a causal reduction rate. All arms had zero positive matched discoveries. Status: engineering `PASS`; research `HOLD_RESEARCH`; future-Arena arms `[]`.
- Search Engine V1.1 Behavior-Niched Arena: 3,000/3,000 counted candidates and 2/2 exact-restored checkpoints passed with zero sealed reads. CEM V2.1 preserved 1,000 families per 1k and eliminated within-arm behavior duplicates, but its valid exact-unique density was 7.91% below typed random and its top-decile reward was lower, so the frozen increment gate failed. Evolution V2.1 verified 399 effective-gene mutations, 244 skeleton mutations, and 229 crossovers and improved matched-count mean/top-decile reward, but its valid density was 12.72% below random, family yield was 926 per 1k, and duplicate rate rose to 7.8%, above both random and the prior 6.5% diagnostic. The archive correctly kept reward champions and exposed 84 global duplicate memberships, but causal proposal-duplication reduction was not established. This spent fixed-retrospective cohort has OOS grade `NONE` and cannot support an Alpha-space conclusion. Status: engineering `PASS`; research `HOLD_RESEARCH`; both V2.1 increments rejected; future-Arena arms `[]`.
- Search Engine V1.2 Balanced Collision Arena: 2,000/2,000 counted candidates, 250 balanced rotating micro-batches, and 2/2 exact-restored checkpoints passed with zero sealed reads. Evolution V2.2 improved strict/raw efficiency, balanced strict throughput, mean reward, and top-decile reward versus equal-count typed random, but family yield fell to 925 per 1k, new families per CPU-hour were lower, and its duplicate rate reached 7.9% versus random's 0%. Campaign-local transition collision memory was checkpointed and replayed exactly, blocked 67 transitions, and skipped three known repeats before evaluation, but did not reduce duplicates to the frozen 3% gate. All arms again had zero positive matched discoveries. Status: engineering `PASS`; research `HOLD_RESEARCH`; Evolution V2.2 increment rejected; future-Arena arms `[]`.
- New-data admission and PIT-universe V1: both aggTrades TARs passed independent SHA and full 203,334,643-row schema/time-semantic validation; OI/mark schema-fixed v3 independently passed all 1,155 partitions and markers. The official daily source build verified 13,544 ZIP/checksum pairs with zero failures and excluded 40,226 zero-volume inactive rows before lifecycle/rank construction. The 893-day Top200 ledger is provisional fail-closed: unresolved `BDXNUSDT` is material to 76 Top200 dates, five inferred multi-lifecycle identities require review, and actual mean symbol-date support is only 88.88% for the current-498 hourly panel, 61.46% for delivered aggTrades, and 14.73% for schema-fixed ranks51-200 OI/mark. The schema-2 intersection cache correctly rebuilds context over 21,432 hours but has 0% full-Top200 hourly support. Status: delivery content `PASS`; PIT universe and search cache `HOLD`; no search was run.
- Acceleration qualification: eight frozen candidates completed four ABBA memory trials plus two reversed-order scheduler rounds at 8/10/12 workers, for 512 executions. Every execution matched the frozen source's complete non-timing evaluation payload, reward, replay hashes, and delta-weight hash. Threshold-plus-lane-boundary trimming reduced native trim attempts from 8 to 2 per eight-pair parity lane and improved median wall time from 48.98s to 47.49s (1.031x). Two-trial median throughput was 0.4651, 0.5072, and 0.5131 pairs/s at 8, 10, and 12 workers. Ten workers is the smallest eligible setting within 95% of best; twelve was rejected because conservative aggregate peak RSS was 14.63 GB, above the 12 GiB gate. A concurrent CryptoHFT process was recorded, so this is bounded launch guidance for the next development Arena, not a permanent 128-pair or global throughput guarantee. The formal wrapper initially exited 1 only because package rendering order differed before/after sorted JSON serialization; source `e806c15` repaired report/manifest determinism and the checker passed without rerunning pairs.
- Explicit/latent comparison: 41/41 means cache loadability plus minimum adaptive-surface nonmissing/variance. Arm D is implementation-verified. Arm E is an overlapping field-family grouped structured proxy with shared objectives and zero-out ablation; its configured semantic matched controls were not executed. The result is an implementation-specific development negative after 5 bps cost, not OOS evidence or rejection of latent-state research.
- Field Information V0: the compiled view contains 177 base/registered tokens and 5,211 derived specifications. Census loading succeeded for 41/41 broad fields and 94/94 Core3 aggTrades fields. `census_loaded` is not `current_runtime_member`: only ten broad fields are current-runtime members, while the 94 Core3 fields remain a separate three-asset mechanism context.
- Volume and flow are materially represented: the broad context contains seven quote-volume/activity fields; the Core3 registry contains 19 activity/liquidity, 16 flow, 6 large-trade, and 26 rolling fields. Trade count, quote volume, size-bucket notional, buy/sell quantity, and price-range fields lead the information census.
- Core Pack consumption: 120 unique tokens = 75 base plus 45 lazy derived, split into independent Broad (39) and Core3 (81) consumers. The repaired full-context probe verified 120/120 loadability, materialization, tensor exposure, gradient reachability, first-layer update, and prediction sensitivity. A preserved late-window attempt reached 118/120 because `active_universe_size` and `age_percentile_active_universe` were constant in that narrower Broad probe; the full authorized Broad period restored their variation. No 120-channel joint panel was created.
- Model-fit boundary: Broad probe loss decreased from 1.054226 to 1.011711. Core3 probe loss increased from 1.015130 to 1.107231, so Core3 model fit is not qualified even though all 81 channels were genuinely consumed. Neither result is a matched alpha comparison, portfolio result, economic increment, or OOS proof.
- Broad supersession and conditional information: the earlier Arena and sticky artifacts omitted a 6h role-tail purge and are no longer current inference evidence. The repaired run fits normalization and eight fixed models only on 2023-07 through 2023-12, fits eight independent nonnegative calibration coefficients only on 2024-01 through 2024-02, and purges the final 6h from model-fit, calibration, selection, and stability. All boundary and fit-independence checks pass. Stable residual information remains in 12/29 added fields, so the information gate still passes; marginal entropy remains an adequacy diagnostic, not an alpha selector.
- Purged Broad economic boundary: the uncalibrated full-minus-control paired net medians are `-1.02e-04` in selection and `-1.22e-04` in stability. Direct delta and the fixed 4h causal repair remain net-negative in every arm. The sticky mechanism reduces turnover, but the repaired matched Broad differences are `-5.97e-05` and `-9.02e-06`; it is cost-management behavior, not a Broad component increment.
- Relational Stage 0: the committed selector resolves the 120-token contract into separate Broad `38+1` and Core3 `31+5+45` views without pooling contexts. One real pre-2024 smoke used 16 assets, 168h history, eight 4h-sleeve decisions, one real eligibility transition, four nonzero recurrent previous-weight coordinates, zero ineligible weight, and exact training/evaluator turnover and 5 bps cost parity. This remains architecture/runtime qualification only; the completed Stage-1 parity and attribution did not turn it into an economic, OOS, or promotion authority.
- Relational Stage 1: local/PC2 parity passed for source, packages, logical data, 128 assets, field order, schedule, scaler, inputs, initialization, and all six arm/seed forwards; the largest absolute forward difference was `2.38e-07`. Each arm/seed completed 245 fixed optimizer steps in 508.92 seconds. B-minus-A won only 1/6 seed-aggregated blocks; seed means were `+1.04e-06` and `-3.95e-06`. B-minus-N won 4/6 blocks and both seed means were positive. All arms were non-degenerate and B/A exact-equality ratio was zero. Status: `RELATIONAL_REPRESENTATION_INCREMENT_NOT_ESTABLISHED`; this is spent-development, implementation-specific evidence with no economic, fresh, OOS, or promotion authority.
- Held-out calibration qualification: seven of eight slopes are positive and preserve raw candidate weights; one Broad MLP slope is negative before the nonnegative constraint and is marked `CALIBRATION_FIT_DEGENERATE`. Intercepts do not change zero-net sticky weights. Degenerate arms stay in the denominator. Calibrated matched-net and delta-sleeve medians are positive only in selection, with 1/4 positive arms; stability medians are zero with 0/4 positive arms. Bias audit: `PASS`. Economic result: `BROAD_PURGED_CALIBRATED_STICKY_INCREMENT_NOT_ESTABLISHED`.
- Liquidation supplier release: 762 Parquet partitions across 381 dates passed schema, count, primary-key, PIT-delay, and content-identity preflight. Of 500 symbols and 11,138,396 events, 464 linear USDT/USDC symbols with 11,101,810 events are eligible for source comparison. Nineteen inverse/delivery and seventeen unknown-semantics symbols remain notional-quarantined because the supplier's quantity-times-price value is not a qualified common notional for those contracts. This is ingress evidence only, not a research field admission or economic result.
- Bitfinex liquidation ingress: all 18 declared monthly bundles and 127 files reconcile internally, with 89,273 raw rows and 81,231 silver rows. This does not prove continuous source coverage: only 135/544 requested dates contain events, 17/18 months have at least seven trailing event-free days, 15/18 raw counts are page-boundary-like, and no request/page/cursor ledger exists. The USTF0 proxy has 55,195 rows but only 7.14 effective months and 4.39 effective symbols, with no price-label bridge or turnover observations. Status: `FILE_INTEGRITY_QUALIFIED_SOURCE_COVERAGE_UNVERIFIED` plus `DATA_ADEQUACY_UNDERPOWERED`; it cannot validate Binance/CryptoHFT or enter research.
- Binance raw provenance capture: the official `!forceOrder@arr` forward collector is active at `G:/AlphaFactory_CryptoData/raw/binance_force_order_ws_v1`. The latest committed prefix snapshot contains 887 valid records across 134 symbols and four hourly files with zero parse, hash, source, or forceOrder-contract failures. Capture began on 2026-07-18 after the supplier package ended on 2026-07-13, so current-package overlap is zero and stitching remains blocked.

## Closed lines and reusable capability

The implemented residual/orthogonal variants and current signal-to-portfolio primitives are inventoried in `reports/CRYPTO_BRANCH_EVIDENCE_MAP.md`. The purged Broad replay owns current inference for its stack; historical CORE43-47/A7H0 remains reference-only under its recorded contracts. CURRENT marks the Broad 6M, observed-archive 18M, localized-mechanism, CEM diversity, and explicit/latent branches `DEPRECATED` without deleting their evidence. The current synchronized-relational forecast implementation is also closed for rescue tuning after its matched Stage-1 negative; the Stage-0 direct-weight slice remains only as reusable architecture. Generic residual packets, transfer probes, or label oracles must not become standalone projects.

## Active execution plan

0. Preserve the consumed V2.3 train/validation outcome at producer
   `06512e01876345d9921d56405d8254a82933a9b7`: 16,000 strict train
   candidates, eight exact-restored train checkpoints plus
   `checkpoint_validation`, exact 1,024-candidate four-cohort attribution,
   all three policy components unqualified, no continuation, and no qualified
   arms. Also preserve the separate frozen OOS replay at producer
   `3e593aaea93e9b521ba78d24186ad225e901eae7`: 1,023/1,024 completed,
   one persisted no-backfill failure, 16 exact-restored checkpoints, one sealed
   read, and pooled total-policy positive direction with Q10 support. Do not
   reopen either campaign, reread the holdout, or reuse adaptive state.
1. Preserve the consumed V2.2 outcome at producer
   `e84b35c76a4cfc139f1c351286489b83fce61250`: 8,000 strict candidates,
   four exact-restored train checkpoints plus `checkpoint_validation`, train
   gate pass, validation-control failure, Stage C not run, and no qualified
   arms. Do not reopen the campaign or reuse its adaptive state.
2. Preserve the consumed V2.1 outcome at producer
   `94b016fa7847d5c5b06db1e6144bda7062064151`: 10,000 strict candidates,
   five exact-restored checkpoints, `TRAIN_GATE_NEGATIVE`, no validation, and
   no qualified arms. Closure `2c4cb156fbe886c13482ba7d2e0e460732f2be0e`
   is source/checker-only and must not be represented as a market replay.
3. Preserve the consumed V2 mechanism campaign at producer `ef688d89ca0e89654015bf5f76a6b9c26494d837`: six exact checkpoints, 12,000 strict train candidates, and terminal `ENGINE_VALIDATION_BLOCKED`. Do not rerun its validation or reuse its adaptive state.
4. Preserve the four Search Surface Integration V1 carriers as engineering inputs only. They make 235 fields runner-reachable but do not grant research admission. Keep the 25 OI/mark source-unavailable holds explicit and do not merge Broad39 with Core3 81.
5. Keep formal future-Arena qualification empty. V2.3's development all-cell
   gate rejected proposal distribution, train ranker, and total policy, so its
   conditional 4k continuation did not run. The separately authorized frozen
   OOS replay now supports a positive pooled total-policy direction under the
   existing target/cost contract, but ADR 0021 intentionally defines no binary
   qualification or promotion gate. V2.2's conditional 12k expansion also did
   not run. V1.1-V1.3 policy comparisons measured pair-feasibility optimization,
   not portfolio search-reward improvement; V1.4 never ran adaptive Stage C.
6. Preserve `PHASE3CM_STYLE_TRAIN_PORTFOLIO_SORTINO_V1` only as reproducible diagnostic code; do not treat it or the capability strict-feasibility tuple as a qualified economic optimizer. `CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2` is source-qualified for future fresh-state use but remains inactive until the rest of the economic receipt closes. Keep `pair_reward`, matched-positive status, strict margins, turnover, cost, support, and concentration as attribution/execution diagnostics only.
7. Keep V1-V5 as consumed outcomes. V3 and V4 are each bound to their own `checkpoint_000` plus `checkpoint_validation_blocked`; V5 is bound to `checkpoint_000` plus completed `checkpoint_validation`. Do not reuse any receipt or run state.
8. Use the existing memory preflight at 10 workers and fail closed to 8 when its gate requires; the V2.3 campaign passed and used 10. Do not use 12 workers.
9. Preserve the completed V2, V2.1, V2.2, V2.3, and V2.3 frozen-OOS Git/Graph
   closures, their consumed receipts, immutable producer artifacts, checker
   results, and empty formally qualified arm sets. Do not reopen those campaigns,
   reread the holdout, or reuse adaptive state.
10. Keep the relational Stage-1 line closed, Stage 0 experimental only, Broad `38+1` and Core3 `31+5+45` separate, and CryptoHFT/Bitfinex/Binance boundaries unchanged.
11. Treat `runtime/crypto_new_data_admission_v1_20260727` and the Search Surface Integration V1 bundle as distinct authorities: the former owns research admission gaps; the latter owns engineering carrier reachability. Resolve `BDXNUSDT`, lifecycle splits, Top200 surface gaps, and the Top50 OI/mark consumer before research admission.
12. Use Unified Field Management V1 only as the deterministic navigation and conflict-checking view over those authorities. Add future registries by declaring their authority path and recompiling; do not hand-maintain duplicate field facts or infer research admission from catalog presence.
13. Preserve the consumed corrected Temporal Mechanism Program V1 outcome at
    producer `1a847cece5014d6d4891538a2a44c3885a00059a`: 2,000 strict
    evaluations from 2,061 attempts, 1,993 behavior families, one completed
    restore-verified checkpoint plus the terminal throughput checkpoint, zero
    system errors, zero sealed reads, and independent PC2 plus local checker
    PASS. The frozen first-checkpoint throughput gate stopped the campaign at
    `1,749.5621 strict/hour` below the required `2,777.7778`; zero
    matched-positive candidates were observed and CEM/Evolution never started.
    Do not restart, resume, import its state, or interpret this throughput-stop
    cohort as a complete temporal-program or optimizer comparison.
14. Preserve the source-only Stage-0 throughput repair recorded in
    `reports/CRYPTO_TEMPORAL_PROGRAM_STAGE0_THROUGHPUT_AUDIT_20260808.md`.
    Independent recomputation found five observed worker PIDs and a maximum of
    five submitted pair tasks despite the declared ten-worker contract. Stage 0
    now submits one paired task per configured worker, records configured versus
    observed worker capacity, and fails closed on systematic pool underfill. The
    source-only audit remains immutable; item 15 records its separate runtime
    qualification without rewriting the prior campaign.
15. Preserve the consumed post-repair Stage-0 qualification at producer
    `f846eb04c023fdf20a5130b40d7846a1ccdad3df`: 2,000 strict evaluations
    from 2,061 attempts, 1,993 behavior families, 1,000 paired diagnostics,
    ten observed workers, a maximum of ten submitted paired tasks per batch,
    zero system errors, zero sealed reads, and independent PC2 plus local
    checker PASS. The half-pool defect is closed, but realized throughput was
    only `2,024.4987 strict/hour`, below the frozen `2,777.7778` floor, so the
    producer stopped at checkpoint 0 before the family gate or adaptive arms.
    The q1 deployment-bound zero-strict invalid runtime is preserved separately
    and imported no state. Do not restart, resume, import state, or interpret
    this throughput-stop cohort as a temporal-program or optimizer comparison.
16. Preserve the source-only mapping hot-path closure recorded in
    `reports/CRYPTO_TEMPORAL_PROGRAM_STAGE0_POST_REPAIR_PERFORMANCE_ATTRIBUTION_20260809.md`.
    Frozen randomized parity keeps weights, feasibility, transition reasons,
    diagnostics and behavior provenance byte-identical; local medians improve
    stateful mapping by 3.57x and sparse mapping by 2.62x. Future rejected tasks
    retain worker CPU/wall/memory fields in the existing ledger. This does not
    establish PC2 end-to-end throughput, consume another market budget, or
    alter the research HOLD.
17. Preserve the consumed 10,000-strict Stage-0 family gate at producer
    `a051f557844d59d829be80c33b7517157828a482`. P1 and P4 crossed one
    family-local continuation route each, but temporal random underperformed
    paired static globally and both arms produced zero matched-positive rows.
    The result supports narrow temporal-family attribution only; it does not
    authorize adaptive search, validation, OOS, promotion, tuning, rescue, or
    another campaign, and none of its candidate, policy or Archive state may be
    imported.
18. Use the qualified fixed Temporal Program development allocation of 2,000
    Random, 2,000 CEM and 6,000 Evolution per 10,000 strict. This transition is
    supported by the frozen 360-candidate development validation with a
    1,523h/1,458h effective train/validation split, three equal 482h validation
    blocks and PC2 plus local checker PASS. It qualifies allocation only. Do not
    infer Alpha, read OOS/holdout, promote a candidate, or start an automatic
    search from this state.

No V2, V2.1, V2.2, V2.3, V2.3 frozen-OOS, successor, or policy-validation
receipt remains authorized. The fixed development flow is reusable for a
future separately authorized development run; no search or sealed replay starts
automatically from this plan.

## Qualified policy components

The implementation preserves compiler authority, hierarchical A/B/AB/ABC matched controls, deterministic replay, campaign-local memory, exact checkpoint restoration, and a reproducible train-only portfolio diagnostic. The formal portfolio-mapping module and capability receipt/lazy-engine patterns are reusable. Capability strict-feasibility feedback remains formal only inside that capability scope. The frozen OOS replay provides positive pooled total-policy attribution and Q10 support, and the read-only bias audit supports ranking/selection value after deterministic behavior-family de-overlap. It does not establish broad mechanism Alpha: 256 Evolution train-top expressions collapse to 161 behavior families and about 7.3 effective primary path dimensions, while the strongest mechanism occurs in only one seed. No economic optimizer, search arm, or archive is formally qualified for a future Arena because the replay had no binary qualification or promotion authority. V1.4 exercised a newly aligned OI/flow carrier and stopped before adaptive Stage C. V1.1-V1.4 state and trajectories cannot seed another campaign.

## Blockers

- The fresh post-mapping Stage-0 family gate closed the prior throughput blocker:
  all ten workers and ten paired tasks per batch were observed, end-to-end
  throughput reached `3,959.8469 strict/hour`, and the uninterrupted run completed
  all 10,000 strict rows. The resulting economic evidence is mixed rather than a
  broad temporal-program qualification: P1 and P4 crossed one frozen family-local
  route each, while temporal random underperformed paired static globally and
  produced zero matched-positive candidates. No adaptive, validation, OOS,
  promotion, rescue, or successor market budget is authorized by this closure.

- The observed-archive surface is not survivorship-complete, and its selection/stability blocks are spent; they can support engineering attribution but not fresh confirmation.
- The completed continuation and V1.1-V1.3 policy comparisons optimized strict matched-feasibility distance, not portfolio Sortino. Their throughput and engineering evidence remain valid, but reward-improvement claims do not establish better Alpha-search ability.
- Search Engine V1 arm-productivity and behavior-family comparisons are research-invalid because panel-context identity and 4h reward uncertainty were defective; the historical run remains engineering-valid, and all trajectories, policies, and archive state are spent and cannot seed another campaign.
- Search Engine V1.1 and V1.2 retain valid proposal, duplicate, family-yield, checkpoint, and receipt evidence. Their mean/top-decile `pair_reward` comparisons are matched-feasibility diagnostics and cannot qualify or reject CEM/Evolution as Alpha-search policies.
- Search Engine V1.4 proved that OI/mark and aggTrades can share a real, PIT/lag-safe, dynamically eligible carrier and that hierarchical A/B/AB/ABC controls execute without a new AST or evaluator. Its zero matched-positive result is a strict attribution outcome, not a portfolio reward negative and not evidence that the supplied fields or crypto market contain no Alpha.
- Search Engine V2.1 completed its 10,000-candidate train campaign, but expanded random missed both frozen absolute positive-reward floors. Evolution's stronger reward ordering and 8.175% positive rate therefore remain a train-only diagnostic; validation did not run and no arm is qualified. This does not authorize reseeding, rescue, OOS, promotion, or another Arena.
- Search Engine V2.2 passed its equal-count train gate and Evolution was positive on all three frozen worst-horizon validation economics. Qualification still failed closed because the receipt required the expanded-random control to survive the same validation kill-line, and that control had negative net mean, Sortino, and matched increment. This is a validation-control qualification negative, not evidence that the Evolution candidates themselves were validation-negative; neither arm is qualified and Stage C did not run.
- Search Engine V2.3 removed the V2.2 random-profitability requirement and
  separated proposal-distribution, train-ranker, and total-policy attribution.
  Its 1,024-candidate validation found a strong train-ranker effect in seven of
  eight seed-horizon metric cells, but the second seed's 4h primary-net effect
  failed; proposal distribution and total policy also failed replication across
  both seeds. The conditional 4k continuation did not run, all qualification
  remained empty. ADR 0021 subsequently authorized one exact frozen-cohort OOS
  replay. That replay found positive pooled total-policy primary-net and matched
  increments with positive Q10, while preserving cell heterogeneity and one
  no-backfill candidate-local failure. It consumed the only OOS read and did not
  retrofit a binary qualification gate, formal authority, promotion, tuning,
  reseeding, rescue, or another Arena.
- The V2.3 frozen-OOS read-only bias audit grades the single 181-day window
  `WEAK`. Evolution train-top is absolutely positive, and behavior-family
  de-overlap retains the pooled policy sign, but its 256 expressions contain
  only 161 behavior families and about 7.3 effective primary path dimensions.
  `FLOW_INTENSITY_CONVICTION` appears only in the first seed; the persisted OOS
  paths omit gross, turnover, cost-path, asset-weight, venue, and capacity
  contributions. Policy-ranking direction remains supported; broad mechanism
  Alpha, cost robustness, concentration robustness, and promotion remain HOLD.
- V1.4 failure decomposition: final-increment gross directionality exists frequently, but 96.10% of gross-positive rows are sign-killed after cost and only 0.25% of Stage-B rows are within one strict-distance unit of zero. This points first to target/execution and turnover economics, not a larger random or adaptive budget. Because standalone sleeves and monthly waterfalls were not persisted, the audit cannot distinguish A/B efficacy from AB/ABC incremental failure strongly enough to authorize a residual, gate, or regime-routing grammar.
- Historical aggTrades coverage remains narrower than the observed-archive surface; the qualified Core3 slice has 3 assets, 4,368 hours, and 13,068 eligible observations.
- V1.4 target semantics are not a qualified execution contract. Binance order flow is evaluated against an availability-dependent non-Binance mark; 126/144 assets use more than one priority venue, and 0.205% of 1h plus 0.512% of 4h valid label endpoints cross venues. The generic 5 bps model is not tied to fees, slippage, mark-to-trade basis, or an executable instrument on those venues.
- The delivered current cohorts are not historical PIT-complete. Every one of 893 provisional Top200 dates has feature-surface gaps; Top50 OI/mark remains raw-only without an authorized materialized consumer. `BDXNUSDT` lacks historical type authority and would alter 76 Top200 dates if admitted as crypto.
- Qlib and DeepDow remain data-underpowered; neither supplies a clean economic negative for its full external paradigm.
- Bitfinex source-interval coverage is unverified and its effective months/symbols plus missing price-label and turnover bridges fail event-study Data Adequacy.
- The active Binance forceOrder capture starts after the current supplier release ends, so supplier/WS overlap compatibility is not yet qualified and stitching is blocked.
- Search Engine V1's distinct validation kill-line is now market-exercised only to the point of a deterministic constructibility block. It remains NON_FORMAL, made no optimizer or archive writes on validation, and did not complete the equal-count arm gate.
- Search Engine V2 completed all 12,000 train candidates but its final arm aggregator rejected legal heterogeneous control schemas before equal-count validation artifacts were persisted. Future source now aggregates controls equal-weight within candidate and then equal-weight across candidates; the consumed run remains blocked and cannot be rescued.
- V1-V6, V2 mechanism, V2.1 mechanism-basis, V2.2 Evolution-qualification,
  V2.3 policy-attribution, and V2.3 frozen-OOS receipts are consumed with
  `run_authorized=false`; their component hashes resolve against each run's
  frozen producer source. None authorizes a current market-development run.
- V4 confirms the NaN/support and rolling-warm-up repairs but exposes a distinct orchestration defect: validation-period mapped-control equality for one selected candidate terminates all active arms before equal-count metrics exist. This is an engine-validation failure, not a market or Alpha negative.
- V3 proves the repaired failure path: the exact validation candidate identity and all campaign state are persisted in `checkpoint_validation_blocked`, and the process terminates as `ENGINE_VALIDATION_BLOCKED` instead of crashing. This is a validation-constructibility result, not a portfolio-reward, Alpha-space, or carrier-information negative. All retained results remain development-only and conditional on 5 bps.

## Source-of-truth order

1. Current user instruction and sealed-data boundaries.
2. Committed source, data contracts, manifests, and real run assets at exact SHA.
3. Accepted closure tag and independent closure attestations.
4. `.planning/PROJECT.md` for mission and this file for current state.
5. `config/architecture_overlay.json` and generated CURRENT for approved architecture authority/contracts.
6. RAW Graphify for navigation only.
7. Historical reports and older status text.

No status code overrides observed runtime or source facts.

## Graph and maintenance

- RAW and CURRENT remain the only two graph layers.
- Lifecycle color, evidence line style, and validation assurance are independent.
- CURRENT never infers authority or lifecycle promotion from RAW presence or test success.
- Semantic role bindings declare `FORMAL` or `NON_FORMAL`; canonical artifact paths and ACTIVE lifecycle do not grant formal authority.
- Use `scripts/maintain_crypto_navigation_graph.ps1 build` after source changes that stale RAW.
- Use `scripts/maintain_crypto_navigation_graph.ps1 maintain` after overlay/profile changes.
- Use `scripts/maintain_crypto_navigation_graph.ps1 check` before closure; it verifies both RAW and CURRENT input hashes.
- Use `scripts/maintain_crypto_navigation_graph.ps1 query -Question "..."` for RAW navigation.
- Lifecycle history not recalled with confidence remains in Git; it is not reconstructed into CURRENT.

## Real experiment authority preflight

The canonical Search Engine `run*` CLI now resolves target, optimizer reward,
execution price, portfolio mapping, cost, validation role, and promotion gate
from CURRENT before execution. It also requires a concrete evidence increment
and the decision that evidence can change. Vacancy, conflict, stale or inactive
authority, or missing intent fails closed. NON_FORMAL roles remain visible
development boundaries and are runnable only when the bound node explicitly
declares `active_authority: true`; they grant no formal claim or promotion
authority.

ADR 0015 records the preflight and ADR 0016 records the active-authority rule,
economic authority suspension, reuse map, and successor receipt. The former
target, optimizer-reward and execution-price bindings to
`real_policy_upgrade_canary` were erroneous and are now vacant; the canary is
implementation/evidence and cannot own them. Cost remains inactive NON_FORMAL,
while validation access and promotion remain fail-closed under the formal sealed
boundary. Portfolio mapping remains formal; that does not promote the venue cost
assumption. Vacancy and inactivity intentionally block canonical Search Engine
execution until an explicit external-control/ADR transition names valid owners.
The committed implementation-only 30k-to-50k successor authorization remains
`IMPLEMENTED_NOT_AUTHORIZED` and fills no role. ADR 0023 registers one narrower
schema-2 exception only if a current user decision atomically activates and
commits that exact receipt: it may receipt-bind the frozen target,
optimizer-reward, execution-price and cost identities as NON_FORMAL for one
host/workspace/runtime, while the formal portfolio-mapping, validation-role and
promotion-gate authorities must still resolve in CURRENT. The canonical runner
then rechecks the complete economic identity before any market-array load. That
one frozen OOS exception remains consumed; any further OOS access, promotion,
cost tuning, seed changes, or rescue reruns remain forbidden.

## Crypto reward uncertainty V2 source repair

The retained crypto evaluator now implements
`CRYPTO_TRAIN_JOINT_PRIMARY_MATCHED_SORTINO_V2`. It removes the duplicated
single-horizon term, replaces IID day sampling with deterministic ordered-day
stationary bootstrap, and gives primary plus every required matched
delta-weight sleeve one shared bootstrap path. Binary reward is the minimum of
primary, primary-minus-left-control and primary-minus-right-control portfolio
quality; hierarchical reward is the minimum of primary, `AB-A`, `AB-B` and
`ABC-AB`. Legacy V1 reward identities fail closed when presented to fresh
adaptive ordering.

This repair is crypto-only and applies continuous UTC semantics. It imports no
CN evaluator or reward and applies no A-share T+1, ST, price-limit, stamp-duty
or suspension-calendar rule. Verification is synthetic and source-only. No
candidate was generated, replayed or evaluated against market data, and no
authority binding or research qualification was promoted.

## Completed phase: Stage-0 temporal-program family gate

The one-time receipt is consumed with `run_authorized=false`. Producer
`a051f557844d59d829be80c33b7517157828a482` and PC2 task
`job_20260810_035743_38e6b6` completed exactly 10,000 strict evaluations from
10,194 generation attempts as 5,000 paired static/temporal programs. Five atomic
checkpoints contain 2,000 strict rows each and independently restore. The run
produced 9,839 behavior families, observed all ten workers and a maximum of ten
submitted paired tasks per batch, used no memory fallback, recorded zero system
errors and zero sealed reads, and reached `3,959.8469 strict/hour`. Independent
PC2 and local artifact/run-validity checks pass. Adaptive Stage C did not start,
and the ledger contains only `paired_static` and `temporal_program_random` arms.

The four frozen program families each received exactly 1,250 pairs. Globally,
temporal random was weaker than its paired static comparator: dual-axis net-positive
counts were 551 versus 659, replicated 2-of-3 counts were 203 versus 318, mean
search reward was `-0.4897395` versus `-0.3859738`, and top-decile reward was
`0.0348805` versus `0.0566757`. Both representations produced zero strict
matched-positive candidates.

The frozen family-local gate nevertheless returned
`LOCAL_TEMPORAL_PROGRAM_LINE_IDENTIFIED` for two narrow reasons. P1 position-state
change to response improved dual-axis net-positive rate from 1.92% to 4.96%
with broad semantic support, but its paired median delta was negative, win rate
was 48.72%, replication rate fell, and matched-positive count remained zero. P4
multiscale state-transition routing crossed only the strictly-positive paired
median route at `3.997238486450849e-07`; its win rate was 50.08%, dual-axis
net-positive and replicated rates were slightly below static, and matched-positive
count remained zero. P2 recent crowding and P3 flow-shock persistence failed all
primary continuation routes.

This is development-only evidence that P1 and P4 contain local temporal variants
worth attribution; it is not evidence that the temporal program space beats the
static catalog, not an Alpha qualification, and not validation or OOS evidence.
The fixed target, mapping, 5 bps cost, reward, seeds, compiler, AST and evaluator
were unchanged. No prior state was imported and no further search, adaptive arm,
validation, OOS, promotion, tuning, rescue, new Arena or new Graph node is
authorized by this closure.

## Completed phase: adaptive broad gate invalid stop and source repair

The one-time fresh-state adaptive-broad receipt is consumed. Producer
`6450be52f7ff85385ac7de86e1d62819a48c1e66` and PC2 task
`job_20260810_101654_098175` reached frozen gates at 10k, 20k and 30k strict
rows using only P1/P4, fresh seeds, Random/CEM/Evolution, the unchanged 115-field
carrier, Binance USD-M target, 4h horizon, existing mapping, 5 bps cost and
dual-axis evaluator. No prior campaign state or sealed evidence was read.

CEM moved to diagnostic at 10k and exited at 20k. Evolution improved equal-count
economic density at every gate, reaching 605 dual-axis net-positive and 393
2-of-3 replicated rows per 1k at 30k versus Random's 126 and 43. That improvement
collapsed into one program family: the positive-family concentration rose to
86.12%, so Evolution failed breadth and exited. The frozen 30k decision was
`STOP_ALL_ADAPTIVE_ARMS_EXITED`; neither arm qualifies for validation, OOS,
promotion or a future Arena.

The producer then violated that stop because the subsequent throughput check
overwrote the existing terminal reason with `None`. It continued Random-only
until operator intervention at 36,277 observed strict rows; checkpoint 017
preserves 36,000. All 6,000 checkpointed post-gate rows are contamination
evidence only and are excluded from economic interpretation. The process was
stopped without restart or rescue. Independent checking correctly fails on the
missing normal terminal manifest/final decision, so the run is recorded as
`ENGINE_RUN_INVALID`, not retrofitted into a valid campaign.

Source now preserves an already-issued gate terminal reason when applying
checkpoint throughput qualification. The focused regression suite passes 32/32.
This source repair changes no market, optimizer or evaluator semantics and grants
no new research authority. No rerun is authorized by this closure.

## Completed phase: 30k valid-prefix policy reconstruction and successor preflight

The historical adaptive-broad runtime remains a whole-run
`ENGINE_RUN_INVALID`: its valid economic prefix ends at strict row 30,000 and
its invalid orchestration suffix begins at 30,001. Source now treats a persisted
`STOP_*` decision as a mechanical mutation barrier across generation, executor
submission, ledger append, Behavior Archive mutation and policy observation.
Program-family concentration remains a reported allocation diagnostic but is
no longer an arm-survival or campaign-stop predicate.

Artifact-only reconstruction from the persisted `<=30k` candidate, lineage,
reward and operation facts returned
`PREFIX_POLICY_STATE_RECONSTRUCTION_PASS`. All four CEM and all four Evolution
lane learning states match the checkpoint-017 snapshots; the checkpoint policy
hash and input hashes verify, post-prefix adaptive mutation rows are zero, and
the procedure performed zero market-array reads, zero candidate reevaluations
and zero sealed reads. Random has no proved exact 30k RNG state and is therefore
identified only as `FRESH_RANDOM_CONTROL_AFTER_30K`.

A minimal 30k-to-50k successor receipt and independent preflight now exist with
20% fresh Random, 60% reconstructed Evolution and 20% reconstructed CEM, 5k
checkpoint decisions, train-only access and unchanged target, execution,
mapping, cost, evaluator, grammar and Temporal Program semantics. Its status is
`IMPLEMENTED_NOT_AUTHORIZED`; `run_authorized=false` and
`market_run_started=false`. No continuation, validation, OOS, holdout, forward
read or promotion occurred in this phase. The next required decision is whether
external control authorizes exactly this one development continuation or keeps
the family on hold.

## Completed phase: canonical 30k-to-50k successor implementation readiness

The canonical `temporal_program_search_v1.py` runner now contains one explicit
`30K_TO_50K_SUCCESSOR` execution mode. It reuses the existing Temporal Program
market loader, compiler, AST, evaluator, reward, mapping, cost, archive and
worker path. It physically consumes the reconstructed 30k adaptive-policy
bundle, restores only `completion_ordinal <= 30000` ledger/archive/dedupe/
lineage and policy-local state, restores all four Evolution plus four CEM lanes,
and creates four deterministic fresh Random control lanes. The invalid source
suffix beginning at 30,001 contributes zero state.

The mode fail-closes before market access unless the sole successor
authorization is externally and atomically moved from
`IMPLEMENTED_NOT_AUTHORIZED` to the one-time authorized state and committed
with the accepted implementation SHA, exact component hashes, fixed branch and
fixed host/workspace/runtime identity. It must also pass the existing seven-role
CURRENT preflight; only the receipt-scoped target, optimizer-reward,
execution-price and cost identities may remain NON_FORMAL, while mapping,
validation and promotion stay under their existing formal authorities. A launch
claim is created before economic or market authority access, so the same
workspace/runtime identity cannot be launched twice or resumed. Decisions occur
only on complete 5,000-additional-strict tranches;
20% fresh Random is retained, adaptive budget is deterministically reassigned
after an arm exit, and 20,000 additional / 50,000 cumulative strict is a
mechanical stop.

The independent implementation checker reports `PASS`: prefix reconstruction
`PASS`, successor implementation `READY`, authorization `NOT_AUTHORIZED`, and
market continuation `NOT_RUN`. It performed zero market-array reads, zero
candidate evaluations and zero sealed reads. Validation, OOS, holdout, forward,
promotion and automatic expansion remain forbidden. This phase is source and
synthetic verification only; it creates no market or Alpha evidence.
