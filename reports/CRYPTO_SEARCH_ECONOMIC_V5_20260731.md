# Crypto Search Economic V5

- Status: `ENGINE_VALIDATION_BLOCKED` (`VALIDATION_CONTROL_ARM_FAILED_KILL_LINE`)
- Producer source: `a6946df8b9b24db8572e48a5f8b79ef621feb0f9`
- Strict train candidates retained: `2,000` from `2,298` raw attempts.
- Exact checkpoint: `checkpoint_validation`; restore verified: `True`.
- Failed typed-random conditions: `validation_control_not_dominant, validation_matched_increment_positive, validation_net_mean_positive, validation_nonoverlap_floor_sortino_positive`.

The frozen equal-count validation stage completed, but its typed-random control
arm failed the pre-authorized economic kill-line.  Without a surviving control
arm, later adaptive-arm comparisons are undefined, so the remaining campaign
budget was not allocated.  No parameter/seed change, rescue rerun,
holdout/OOS/challenge read, promotion, or next Arena occurred.
