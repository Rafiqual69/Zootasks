# ZooTasks Provider Registry & Autonomous Offer Pipeline

## Objective
ZooTasks must add future AI providers and offer types without rewriting the financial core or granting agents implicit authority. The stable interface is the canonical offer contract in docs/ai/AI_PROVIDER_OFFER_SCHEMA.json. Provider-specific integrations belong behind adapters.

## Lifecycle
1. Discover candidate provider/offer from an approved source.
2. Register stable provider and adapter identity.
3. Normalize into the canonical schema.
4. Validate fields, categories and values.
5. Authorize provider, region, terms and data policy.
6. Quarantine pending/revoked/unsafe offers.
7. Activate only verified + approved + active offers.
8. Monitor provider/schema/terms changes.
9. Revalidate after material changes.
10. Disable failed adapters or revoked authorization safely.

## Boundaries
- Discovery is not authorization.
- Normalization is not approval.
- Offer visibility is not worker eligibility.
- Acceptance is not payment.
- No adapter may mutate ZooTasks wallet state.
- Credentials and secrets never enter general model context.
- External communication remains separately authorized.
- Financial settlement remains deterministic.

## Future compatibility
A new provider normally requires a registry entry, versioned adapter, canonical-schema mapping, provider verification, security/data-policy review, deterministic adapter tests, and provenance evidence. A new task category requires schema/category review rather than a core lifecycle rewrite.

## Automated change handling
Adapters publish version and source revision. A sync worker compares the last accepted revision with the newly observed revision. If authorization, reward terms, region eligibility, data sensitivity, processing restrictions, qualification, verification or source identity changes materially, the offer must return to review/quarantine rather than remain silently executable.

## Evidence basis
NIST describes AI risk management as a lifecycle activity, and its 2026 monitoring work highlights post-deployment monitoring for unexpected real-world behavior. OWASP agentic guidance emphasizes least privilege, per-request authorization, input validation, human confirmation for high-impact actions, and resource budgets.

## Status
- Canonical schema: implemented.
- Deterministic normalizer/validator: implemented.
- Network/provider adapters: not enabled.
- Production AI: remains disabled.
- Financial settlement: unchanged.
