# CRYPTO Feature Runtime Inventory 20260714

## Decision

`PASS_CRYPTO_FEATURE_RUNTIME_INVENTORY_BUILT`

This package is a metadata and lineage inventory. It does not authorize search, replay, alpha proof, or forward use.

## Scope

| Asset | Rows | Status |
|---|---:|---|
| aggTrades base feature registry | 94 | recovered exactly from Git history `1ed5acd`; two non-feature schema/mask rows excluded |
| aggTrades derived feature specs | 5,211 | recovered exactly from Git history `1ed5acd` |
| Latest active field registry | 10 | A7EFF2 release |
| Latest input approval registry | 36 | A7INPUT0 |
| Unified runtime inventory | 5,388 | static union with field-level deduplication |
| Feature lineage ledger | 5,388 | base, derived-spec, and ontology lineage rows |
| Current Epoch runtime-loaded fields | 10 | A7EFF2 only |

## Runtime Meaning

The repository does not define a standalone `Epoch` object. For this inventory, current Epoch means the latest verifiable release runtime, `A7EFF2_GIT_RELEASE_20260711`. Only its ten active fields are marked `runtime_loaded=true`.

The 94 base features and 5,211 derived specs are real A7V1 registry assets, but their original runtime directory was later removed. They were recovered from Git commit `1ed5acd`. Historical A7V1 explicitly authorized an agg-aware dry run, not full search. They are therefore marked static/not loaded in the current Epoch.

## Identity

```text
source HEAD:       ac9fd24ede281bbcbf438f7c2f4f9b1e563b8b76
graph built SHA:   fb27d14c985f3e68429a02f84826e1cddd6293a6
graph file commit: ac9fd24ede281bbcbf438f7c2f4f9b1e563b8b76
graph SHA256:      6879005FB6DCC9E2CC19D8802BB3783FADD312FC934AB01A004CDDF349F9357F
updated UTC:       2026-07-14T12:08:07Z
```

## Files

`runtime/crypto_feature_runtime_inventory_20260714/asset_manifest.csv` records the SHA256 and source path for every content asset. `SHA256SUMS.csv` additionally hashes the manifest files; it intentionally omits its own self-hash.

## Known Boundary

The A7V1 base registry records field family, mask, scope, and lag but not the exact raw aggregation formula for every base feature. Those rows are marked `REGISTRY_RECOVERED_FORMULA_DETAIL_EXTERNAL` in the lineage ledger rather than being assigned invented lineage.
