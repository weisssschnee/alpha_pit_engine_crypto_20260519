# Crypto Unified Field Management V1

## Decision

`PASS_COMPILED_VIEW_NOT_AUTHORITY`

The existing field-information capability was extended into a deterministic
management/navigation view. No market search, reward read, sealed read,
candidate promotion, new ontology, new approval authority, new compiler,
new AST, new materializer, database, or Graph layer was created.

## Authority map

| Concern | Existing authority reused |
|---|---|
| Inventory and runtime status | `CRYPTO_FEATURE_RUNTIME_INVENTORY.csv` |
| PIT lineage | `feature_lineage_ledger.csv` |
| Semantic ontology | `a7ffr1_field_ontology_v3.csv` |
| Input approval | `latest_input_approval_registry.csv` |
| Lazy derived recipes | `aggtrades_derived_feature_specs_5211.csv` |
| Broad/Core3 tokens | existing field registry and resolved token contract |
| Carrier contracts | Search Surface Integration V1 `carrier_contracts.json` |
| Typed search roles | existing `field_role_surface` resolver |
| Candidate/compiler identity | existing `CandidateSpec`, `FieldContract`, and `TypedExpressionRegistry` |

## Compiled result

- canonical management records: `5,509`
- base/registered records: `298`
- existing lazy derived views: `5,211`
- carrier bindings: `235`
  - Broad: `39`
  - Core3: `81`
  - aggTrades: `44`
  - OI/mark: `71`
- typed role bindings: `852`
- provenance-only fields: `4`
- authority conflict rows: `1` nonfatal scoped PIT-authority difference
- fatal authority conflicts: `0`
- carrier contexts merged: `false`

Closure repair regenerated every runtime artifact from production commit
`f21ed7d1375904f62cb0cc03abb350ea56f911cd`. The manifest records that exact
`source_sha` and the committed production-code bundle SHA256
`BD72E2C8934B00BDCE32ADB720F322DC88F95705DFF7A9E0E64179957AD32E3B`.

The main catalog now joins type, unit, PIT authority, approval, lineage, grain,
venue, statistic, deprecation, materialization, and ontology semantic type.
Unresolved facts remain explicit rather than inferred.

`field_reachability_matrix.parquet` contains 5,638 carrier-scoped or unbound
rows and one deterministic first breakpoint per row:

- current Broad, Core3, and full aggTrades: research admission not granted;
- OI/mark ranks51-200: 71 engineering-reachable and 25 zero-finite-support
  source holds;
- Top50 OI/mark: compact materializer not verified;
- liquidation: source/data-adequacy quarantine;
- catalog identities outside current carriers: no current carrier binding.

The four provenance-only fields are the first/last aggregate-trade receipt IDs
and transaction timestamps. They remain available for provenance but receive
no search role.

## Duplicate and conflict audit

Ontology and approval identities are complete subsets of the 5,388-row
inventory. Carrier integration introduces 121 canonical physical identities
not present in that inventory. The only cross-carrier same-name contract is
`agg_trade_count`; its type, unit, and lag agree, so it shares a canonical
management identity while retaining two independent carrier bindings. Its two
carrier-scoped PIT authority labels differ and are reported as one nonfatal
scoped difference, not falsely asserted as `EXACT_EQUIVALENT`. No fatal
type/unit/lag, lineage, approval, or ontology-semantic conflict was found.

## Boundary

This result improves discovery, navigation, and fail-closed consistency only.
It is not field research admission, Alpha evidence, OOS evidence, search-arm
qualification, or permission to start another Arena.
