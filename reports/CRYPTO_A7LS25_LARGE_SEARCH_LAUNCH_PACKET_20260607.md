# CRYPTO A7LS-25 Large Search Launch Packet (20260607)

## Decision

`PASS_A7LS25_LARGE_SEARCH_PACKET_READY_FOR_COMPANY_MATERIALIZATION`

## Scope

- total queue rows: 78744
- materialization queue rows: 40000
- shards: 40 x 1000
- company concurrency: 2
- source: A7LS15 full blueprint index filtered by A7LS24 label-transfer axes
- no May usage
- no alpha proof / shadow / paper / live

## Axis Coverage

| axis                     |   candidate_rows_seen |   selected_rows |   target_rows |   semantic_pair_count |   motif_count |   skeleton_count |
|:-------------------------|----------------------:|----------------:|--------------:|----------------------:|--------------:|-----------------:|
| strong_positioning_basis |                 71423 |           22000 |         22000 |                     3 |            15 |              222 |
| oi_positioning           |                 38768 |           18000 |         18000 |                     9 |            17 |              215 |
| oi_taker_flow            |                 38284 |           18000 |         18000 |                     1 |            11 |              213 |
| raw_multi_axis_reserved  |                 80000 |           22000 |         22000 |                    55 |            10 |              133 |
