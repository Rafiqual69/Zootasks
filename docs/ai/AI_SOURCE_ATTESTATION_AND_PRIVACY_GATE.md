# AI Source Attestation & Privacy Gate

## Research basis

NIST identifies agent identification, authorization, auditing and non-repudiation as important controls for agentic systems. A2A's current specification supports signed Agent Cards and requires authorization to remain scoped to the authenticated caller. It also recommends keeping credentials out of cards and obtaining them out-of-band. citeturn0search1turn0search0

## Source attestation

ZooTasks now treats source attestation as evidence, not authority. A Source Manifest binds source identity, provider identity, version, source type, region scope, evidence references and an optional attestation reference.

States:
- `unverified` -> quarantine
- `attested` -> candidate for subsequent authorization gates
- `revoked` -> quarantine

A manifest digest binds the exact manifest contents. This implementation does not perform network key retrieval or cryptographic signature verification; that belongs to a separately authorized trust service.

## Privacy and retention gate

Provider capabilities must declare:
- data sensitivity
- purpose
- retention
- processing restrictions
- approved regions
- explicit review approval

Any missing review, unsupported region or invalid policy remains quarantined. Privacy approval never grants provider authorization or financial authority.

## Controlled activation chain

`source manifest -> attestation evidence -> provenance -> privacy/retention review -> provider authorization -> adapter readiness -> offer validation -> worker eligibility -> execution gate`

No step implicitly authorizes the next step.

## Security invariants

- credentials are never placed in Agent Cards or source manifests
- unverified sources remain quarantined
- revoked sources remain quarantined
- privacy approval cannot mutate wallets or withdrawals
- privacy approval cannot activate production AI
- external communication remains separately authorized
- production AI remains disabled pending the complete approval chain
