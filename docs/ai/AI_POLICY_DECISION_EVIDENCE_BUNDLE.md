# AI Policy Decision Evidence Bundle

NIST's agent identity work calls out proving an agent's authority for a specific action, delegation, human-in-the-loop authorization, auditing and non-repudiation. NIST AI RMF also emphasizes traceable measurement, documentation and continuous risk management. citeturn0search38turn0search9

## Purpose

ZooTasks now has a deterministic evidence bundle that binds the decision lineage for an AI action without granting authority itself.

A bundle binds:
- policy version
- authorization digest
- delegation-chain digest
- source/provenance digest
- privacy decision digest
- audit-entry digest
- decision state
- approval reference when the decision is `allow`

The complete bundle is hashed with canonical JSON.

## Decision states

`allow`, `deny`, `quarantine`, and `review` are evidence states. An `allow` bundle must contain an approval reference.

## Security properties

- changing any bound evidence changes the bundle digest;
- an approval reference is required for an allow decision;
- a digest mismatch fails closed;
- the bundle does not mint credentials or authorize network access;
- the bundle cannot mutate wallets, approve withdrawals, pay promotions, change permissions, bind identities, or activate production AI.

## Audit reconstruction

The intended evidence lineage is:

`source -> privacy -> agent identity -> delegation -> authorization -> policy decision -> execution audit`

This gives reviewers a deterministic way to reconstruct which evidence was bound to a decision at the time it was recorded.

This implementation is an evidence primitive, not a claim of legal certification or cryptographic non-repudiation by itself. External immutable storage, signing keys, timestamping and retention controls remain separate infrastructure decisions.
