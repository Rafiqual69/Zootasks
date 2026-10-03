# ZooTasks AI Security Roadmap

## Research basis — October 2026

This roadmap uses NIST AI RMF / NIST AI 600-1, OWASP Top 10 for LLM and GenAI Applications 2025, ISO/IEC 42001-oriented lifecycle governance already adopted by ZooTasks, and SLSA/GitHub artifact-provenance practices.

NIST's GenAI profile emphasizes governance, pre-deployment testing, content provenance, and incident disclosure. OWASP 2025 highlights prompt injection, sensitive-information disclosure, supply-chain risk, improper output handling, excessive agency, and related risks. SLSA treats provenance as verifiable information linking an artifact to its source and build process, with stronger levels adding signed provenance. GitHub artifact attestations use signed provenance and are intended to make build provenance verifiable.

## Security-first direction

ZooTasks will not move directly from a deterministic evaluation runner to production AI.

The controlled sequence is:

1. **Boundary** — AI remains an untrusted computation boundary.
2. **Deterministic validation** — application code validates all AI input and output.
3. **Adversarial evaluation** — prompt injection, sensitive-data, malformed-output, provider-failure and financial-boundary cases must pass.
4. **Evidence integrity** — evaluation evidence is content-addressed with SHA-256 and linked to dataset, source revision and Git commit.
5. **Provenance** — CI records the exact source/build context.
6. **Independent attestation** — release-grade evidence may receive signed artifact provenance; routine test runs should not be signed merely for volume.
7. **Production approval gate** — an explicit, human-controlled approval record is required before any provider adapter can be enabled.
8. **Runtime kill switch** — AI must have a default-off production control and fail closed.
9. **Human oversight** — AI suggestions cannot authorize financial, identity, permission or other irreversible actions.
10. **Monitoring and rollback** — quality, abuse, latency, cost, provider errors and security incidents are monitored; disabling AI must leave the core marketplace operational.

## Non-negotiable ZooTasks financial boundary

AI must never become an authority over:

- wallet balances or ledger mutation;
- task reward mutation or claim approval;
- withdrawal reservation, approval or payment;
- promotion funding, liability or payout;
- permissions/RBAC;
- Owner authentication, MFA or identity binding.

These remain deterministic, server-authorized application operations.

## Current stage

**AI-SYS-001 — Task Classification & Quality Assistance: DESIGN ONLY.**

No production provider/model is approved.

## Next implementation gates

### Gate 1 — Evaluation quality
Strengthen the deterministic test suite so each adversarial case proves a concrete control rather than merely recording a PASS.

### Gate 2 — Production kill switch
Add a default-off runtime approval control and require an auditable approval reference before a provider adapter can be reached.

### Gate 3 — Release evidence
Create a release-only provenance/attestation workflow. Do not add signing to every routine evaluation run; GitHub documents artifact attestations as a provenance mechanism for artifacts intended to be consumed/released, while routine testing need not be attested.

### Gate 4 — Provider contract
Before selecting a provider, document endpoint allowlisting, data processing/retention, region/transfer requirements, credential isolation, model/version pinning, timeout/rate/budget limits and failure behavior.

### Gate 5 — Pre-production red-team
Run adversarial testing against the actual provider adapter in an isolated environment with synthetic data only. Production secrets and financial records remain excluded.

### Gate 6 — Approval and rollback
Require explicit release evidence, accountable approval, monitoring thresholds and a tested disable path. Any material provider/model/prompt/data change re-enters the applicable gates.

## Security principle

Passing an evaluation is evidence of tested behavior; it is not proof that the AI system is safe in every context. Production authorization remains a separate governance and security decision.
