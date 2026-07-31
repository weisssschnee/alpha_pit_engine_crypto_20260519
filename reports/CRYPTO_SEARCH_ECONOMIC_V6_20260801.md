# Crypto Search Economic V6 Seed Robustness

- Status: `ENGINE_VALIDATION_BLOCKED` (`VALIDATION_CONTROL_ARM_FAILED_KILL_LINE`)
- Producer source: `07a699f11510b943991425c4a86eb7582aa59583`
- Strict train candidates retained: `2,000` from `2,263` raw attempts.
- Exact checkpoint: `checkpoint_validation`; restore verified: `True`.
- Failed typed-random conditions: `validation_control_not_dominant, validation_matched_increment_positive, validation_net_mean_positive, validation_nonoverlap_floor_sortino_positive`.

The frozen equal-count validation stage completed, but its typed-random control
arm failed the pre-authorized economic kill-line.  Without a surviving control
arm, later adaptive-arm comparisons are undefined, so the remaining campaign
budget was not allocated.  No parameter/seed change, rescue rerun,
holdout/OOS/challenge read, promotion, or next Arena occurred.
