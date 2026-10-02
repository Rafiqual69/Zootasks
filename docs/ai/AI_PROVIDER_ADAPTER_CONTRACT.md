# ZooTasks AI Provider Adapter Contract

Adapters isolate provider-specific protocols from the stable ZooTasks offer contract. An adapter is not an authorization grant.

## Required properties
- deterministic input/output mapping
- explicit provider and adapter version
- endpoint/source allowlist
- bounded timeout, retries and concurrency
- idempotency for repeatable sync operations
- no wallet/withdrawal/promotion mutation
- no credential exposure to general AI context
- auditable provenance for normalized offers
- safe failure: errors produce stale/failed/quarantined state

## Lifecycle
disabled -> ready -> quarantined -> disabled

Only separately verified provider authorization may move an adapter to ready.

## Sync contract
A future adapter exposes a bounded, read-oriented sync operation:
sync_offers(context) -> candidate offers

It must verify registration, use only approved sources, enforce budgets, treat provider responses as untrusted, normalize candidates, attach provenance, and quarantine failures.

## Change detection
Material changes require revalidation: authorization, source identity, reward/payment terms, regions/languages, data sensitivity/retention/restrictions, qualification, verification method, adapter version.

## Explicit non-goals
Adapters do not approve workers, mutate balances, approve/pay withdrawals, pay promotions, grant agent permissions, bypass access controls/CAPTCHAs/provider restrictions, or send unsolicited bulk communication.

No network/provider adapter is enabled by this contract. Production AI remains disabled.
