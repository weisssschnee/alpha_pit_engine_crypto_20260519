# CRYPTO A7SHADOW3 Reward Queue Adapter

Generated: 2026-07-03T15:41:27.397183+00:00

## Decision

`PASS_A7SHADOW3_REWARD_QUEUE_ADAPTED`

This adapter converts A7SHADOW-2 keep leaders into an A7REWARD-compatible queue. It assigns stable non-empty `blueprint_id` values from `candidate_id` to prevent reward grouping from collapsing multiple candidates into one blank id.

## Counts

- input_rows: `5`
- output_rows: `5`
- missing_expression_rows: `0`
- duplicate_blueprint_id_rows: `0`

## Outputs

- reward_input_queue: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow3_reward_queue_adapter_20260703\a7shadow3_reward_input_queue.csv`
- manifest: `G:\Project_V7_Rotation\alpha_pit_engine_crypto_20260519\runtime\a7shadow3_reward_queue_adapter_20260703\a7shadow3_queue_adapter_manifest.json`
