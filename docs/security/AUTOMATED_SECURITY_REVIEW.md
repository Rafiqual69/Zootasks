# ZooTasks Automated Security Review Gate

## Purpose
This document defines the Board's recurring security verification boundary for ZooTasks.

## Mandatory sequence
1. Verify repository state and branch isolation.
2. Validate the Read/Write policy and JSON Schema.
3. Verify Policy Decision Point (PDP) and Policy Enforcement Points (PEP).
4. Verify object ownership and collection-query authorization.
5. Verify financial invariants and state transitions.
6. Verify atomicity, locking, and idempotency for financial mutations.
7. Verify authentication, privileged re-authentication, session invalidation, CSRF, and rate-limit controls.
8. Verify data minimization and security-log redaction.
9. Run regression, deployment checks, dependency audit, and diff checks.
10. Do not merge or deploy until all required gates are green.

## Financial invariants
- A worker cannot directly mutate wallet balance or ledger records.
- Withdrawal reservation and balance mutation must be atomic.
- A withdrawal may be paid only from the approved state.
- Payment must be idempotent and must not create a second ledger transaction.
- Approval and payment must remain separated by permission and PDP policy.
- Task and promotion rewards must have an explicit, tested relationship to their claim/payment state.
- Concurrent requests must not bypass capacity, ownership, status, or idempotency constraints.

## Read safety
Protected collection reads must apply authorization filters. GET/read paths must not perform hidden financial or account-state mutations. Sensitive financial identity data must be returned only where explicitly required.

## Evidence
Every policy change requires tests. Every financial policy change requires financial regression evidence. Failed or unavailable policy evaluation is deny-by-default.

## Research baseline
The control model is aligned with OWASP Top 10:2025 A01 (server-side authorization, deny-by-default, record ownership, business limits, failure logging, rate limiting) and NIST SP 800-218 secure-development verification practices.

## Stop conditions
Automation must stop and report when:
- a security gate fails;
- policy/schema/implementation drift is detected;
- a financial invariant cannot be proven;
- a protected mutation lacks an explicit PEP;
- a test result is stale or cannot be reproduced;
- a proposed change would require bypassing an existing security control.

No production financial data is used as CI test data.
