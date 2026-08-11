# Crypto Temporal 30K-to-50K Successor Authorization

## Decision

`GO_WITH_LIMITED_SEARCH_POLICY_CHANGE`

The current user authorized exactly one PC2 development continuation in
`30K_TO_50K_SUCCESSOR` mode. The authorization is schema-2, branch-,
implementation-, component-, host-, workspace- and runtime-bound. It does not
authorize validation, OOS, holdout, forward reads, promotion, rescue, reseed,
tuning, automatic expansion or a second successor.

## Bound identity

- implementation SHA: `b5985037492a81198953629480c75db12e2a8afd`
- branch: `experiment/crypto-p4-pocket-validation-v1-20260811`
- authorization SHA256: `F125061CD9DBFA0CAF2FFAC34B2479F370C600B6CF73A61352A309278DB5A38A`
- authorization decision: `USER_GO_WITH_LIMITED_SEARCH_POLICY_CHANGE_20260811`
- PC2 host: `desktop-a2h3a2g`
- PC2 workspace: `C:\HermesWorker\workspace\crypto_temporal_successor_b5985037`
- workspace identity SHA256: `237C577530372798A4E021721764830F0544F0FC0054C9DE3742A442CFBDA71D`
- runtime id: `crypto_temporal_program_30k_to_50k_successor_v1_20260811`
- reconstructed policy bundle SHA256: `DA229B716EC23C864C25E89443241345ECA645DB7EC7C7B1D57E0C1C7EA4485F`
- source artifact identity SHA256: `4A86407E9D399EDF4900AFB98A27B0FDC5FFE34D138D96882FCF30706A3338F6`

## Frozen execution contract

- valid historical prefix: `completion_ordinal <= 30000`
- invalid suffix start: `30001`
- invalid suffix state contribution: `0`
- fresh Random / reconstructed CEM / reconstructed Evolution allocation:
  `20% / 20% / 60%`
- decision cadence: every `5000` additional strict candidates
- maximum additional strict: `20000`
- cumulative mechanical hard stop: `50000`
- family concentration: allocation/diagnostic only, never a campaign-stop owner

## PC2 preflight evidence

The physical PC2 preflight observed no active Python process and no active
Crypto Search task. The machine exposed 20 logical processors, about 21.1 GiB
free physical memory and about 68.6 GiB free virtual memory. C: had about
283.3 GiB free; D: had only about 1.19 GiB free, so the dedicated successor
checkout was placed on C: and the retained 394 MiB source artifact was reused
in place rather than retransmitted.

All eight required retained source files were present. The four receipt-bound
source hashes matched exactly, including candidate ledger
`90DD15F53AC0891F8D157B50D8027EAABFBF9C195D1717C372041FB5A0067C47`,
behavior archive
`ADD236EDC5313BAF09A86303BE54174668AFF4C41F21C1AEF59D0155E6D128CC`,
rejected ledger
`C9875502D4781310DA85846E3E504FB8F54C4384C2B3DA35BF1891930595E76E`
and checkpoint-017 state
`AC341BB5D316E8F35E2A8ECA4F2058EA9AC411E1E2388B17B107806FA5AD8F1F`.

The authorized preflight returned `SUCCESSOR_PREFLIGHT_PASS`, reconstructed the
30,000-row state with zero suffix contribution, derived the four frozen fresh
Random lane seeds, and observed:

```text
market_arrays_read: 0
candidate_evaluations: 0
sealed_reads: 0
runtime_root_exists: false
```

The PC2 checkout disables newline rewriting locally so the committed
reconstruction report retains its exact frozen byte hash. A workspace-local,
hashable `psutil 7.0.0` vendor payload supplies the only dependency absent from
the retained PC2 Python without modifying the shared interpreter or search
semantics.

## Status

`RUN_AUTHORIZED_ONE_TIME_30K_TO_50K_DEVELOPMENT_SUCCESSOR / NOT_STARTED`

The authorization must be committed and the exact authorization-bearing
checkout reverified before the detached PC2 run starts. At terminal, the run
must stop before any action beyond cumulative 50,000 strict candidates and be
audited only as development evidence.
