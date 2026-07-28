# Search Engine V1.4 source gap report

- Existing OI/mark carrier: 71 finite fields, 144 physical assets, 2025-06-28 05:00 through 2026-07-18, existing 1h/4h priority-venue mark target.
- Existing aggTrades authority: full 44-field TAR contract through 2026-06; the prior materialized carrier stops at 2024-07 and cannot be reused as the V1.4 aligned panel.
- Reusable bridge: `build_aggtrades_search_surface_cache` already joins a source `RawPanelStore`, requires complete PIT-safe minute hours, preserves missingness, intersects eligibility, copies the source target, and recomputes post-join context.
- Required carrier change: reuse that bridge with the OI/mark store as source/target authority over the real overlap ending 2026-07-01. No new materializer or target formula is required.
- Existing grammar: 40 binary Skeleton variants remain registered; only compiler-compatible variants may execute on the 115-field surface.
- Required grammar change: four typed semantic tuples compile as `StateModulation(RatioInteraction(A,B),C)` through the existing AST and compiler.
- Required evaluator change: the existing pair evaluator must preserve one shared support/target/mapping/cost contract and record `AB-A`, `AB-B`, and `ABC-AB` separately.
- Existing V1.3 policy/archive state is spent and cannot seed V1.4.
- Broad, Core3, liquidation, OOS, challenge, recent, forward, promotion, latent priority, relational training, and sealed reads remain excluded.
