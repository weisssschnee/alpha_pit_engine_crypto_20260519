# Crypto A7I-1a Decision Record

decision: PASS_A7I1A_RUNNER_PREFLIGHT
stage: runner implementation preflight
executes_search: false
authorizes_a7i1b: true
authorizes_alpha_proof: false
authorizes_shadow_paper_live: false

confirmed:
- May stress result is mechanically excluded from rank_score and selected_for_replay.
- Residualization parameters are fit on train_2024 only.
- Execution lag 1bar stress outputs are generated.
- FundingCore/Core4/taker/placebo baseline classifications are explicit.

not_confirmed:
- A7I-1b candidate discovery
- alpha proof
- shadow readiness
- paper/live readiness
