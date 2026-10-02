# AI Mechanism Catalog & Provenance Fabric

## Purpose

ZooTasks separates two questions: whether a mechanism is genuinely new, and where a candidate observation came from.

The Mechanism Catalog answers novelty using deterministic innovation-genome fingerprints. The Provenance Fabric records exactly what was observed using source identity, timestamps, payload digests, sequence numbers, and optional chain links.

## Discovery flow

approved-source observation -> provenance record -> quarantine -> canonical normalization -> genome fingerprint -> mechanism catalog comparison -> material-change gate -> security and TEVV -> human design approval

A provenance record is evidence, not authorization.

## Mechanism Catalog

Each known mechanism contains a stable ID, name, five-dimensional genome, evidence references, and lifecycle status. Exact genome matches are known. Changed genomes become candidates for further novelty analysis. Semantic novelty still requires evidence and review.

## Provenance Fabric

Each observation is bound to source kind, source identifier, observation timestamp, canonical payload digest, sequence number, optional previous-record digest, and a record digest. Trust is explicitly untrusted by default.

The first implementation is network-free and storage-neutral. A future persistence service must preserve the digest contract and must never turn provenance into permission.

## Security properties

- fail-closed input validation
- deterministic SHA-256 digests
- untrusted-by-default source state
- quarantine before activation
- no provider authorization or adapter enablement
- no worker task acceptance
- no wallet, withdrawal, or promotion mutation
- no permission or Owner-authentication change
- no production AI activation
- no external communication side effect

## Standards alignment

NIST's 2026 AI Agent Standards Initiative emphasizes interoperability together with agent security and identity, while the NCCoE work highlights identification, authorization, auditing, and non-repudiation as implementation concerns. citeturn0search1turn0search2

A2A 1.0 is a production-ready open interoperability standard. Its security guidance includes authentication, least-privilege authorization, input validation, resource limits, and privacy controls. ZooTasks can keep protocol adapters behind the existing authorization and provenance boundaries instead of coupling the marketplace core to one protocol. citeturn0search5turn0search7

## Controlled next evolution

1. Signed or attested source manifests.
2. Protocol-neutral Agent and Provider Cards with scoped capabilities.
3. Deterministic delegation-token boundary for multi-agent calls.
4. Privacy and retention evidence gates before production provider activation.
5. Production AI remains disabled until the complete approval chain is evidenced.
