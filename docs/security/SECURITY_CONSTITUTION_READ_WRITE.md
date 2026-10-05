# ZooTasks Security Constitution — Read/Write Boundary

Status: Active design baseline for incremental enforcement.

## Non-negotiable invariants

1. Deny by default: authentication and authorization decisions are server-side.
2. A Django `is_staff` or `is_superuser` flag is not sufficient evidence of the Owner role.
3. Financial writes must preserve existing transaction semantics, atomicity, locking, and idempotency.
4. AI has no direct write authority over wallets, withdrawals, promotions, AccountEntity roles, or privilege state.
5. Sensitive data is never placed in logs, exceptions, CI output, URLs, analytics payloads, or client-visible error messages.
6. Object access must validate both the actor's role and ownership/scope; numeric IDs are never authorization.
7. Security failures fail closed and must not disclose whether a protected resource exists when that disclosure is unnecessary.
8. Every high-value security or financial action must have an auditable server-side event.
9. No migration or change may alter balances, ledger history, withdrawal state, or promotion payout semantics without explicit security review.
10. Production secrets are never committed to the repository.

## Read/write decision model

Actor -> Role -> Resource -> Action -> Object scope -> State conditions -> Decision -> Audit

A policy is complete only when the read and write path are both protected.

| Resource | Worker | Finance | Finance Payer | Owner | AI |
|---|---|---|---|---|---|
| WorkerProfile | own read/update-safe fields | scoped read | scoped read | read | deny write |
| WalletTransaction | own read | scoped read | scoped read | privileged read | deny write |
| WithdrawalRequest | own create/read | approve/reject | pay | privileged oversight | deny |
| Task | read/claim/submit own claim | review claims | no payout authority | create/change policy | classify/read only |
| Promotion | read/claim/submit own claim | review claims | no payout authority | create/change policy | classify/read only |
| AccountEntity | own role is not self-editable | deny | deny | privileged lifecycle | deny |
| Security evidence | deny | scoped | scoped | privileged | append only through audited gateway |

## Data-leakage rules

- Never log passwords, TOTP/WebAuthn secrets, session identifiers, API credentials, SMTP credentials, bank account numbers, raw proof secrets, or raw authentication tokens.
- Admin list views should expose the minimum fields required for the operator's function.
- Search fields must not create an unintended disclosure channel for sensitive identifiers.
- User-facing errors must be actionable but non-sensitive.
- CI must use synthetic credentials only.
- Security test fixtures must use fake identities and fake financial values.

## Enforcement roadmap

This document is a policy contract, not a claim that every control is already implemented. Each invariant must become executable tests and, where appropriate, server-side policy enforcement before being marked enforced.
