# ZooTasks Financial Invariant Matrix

This is a security review artifact, not a substitute for server-side enforcement.

| Domain | Invariant | Required enforcement | Evidence required |
|---|---|---|---|
| Task claim | A worker has at most one claim per task | Unique constraint + locked claim path | duplicate/concurrency test |
| Task capacity | completed_workers never exceeds max_workers | lock task before capacity check and increment | concurrent claim test |
| Task earning | One approved claim creates at most one earning transaction | lock claim + idempotency check | replay test |
| Promotion claim | A worker has at most one claim per promotion | Unique constraint + locked claim path | duplicate/concurrency test |
| Promotion capacity | completed_workers never exceeds max_workers | lock promotion before capacity check and increment | concurrent claim test |
| Promotion budget | Total approved promotion rewards cannot exceed the authoritative budget definition | explicit invariant in the approval/payment transaction | boundary + overspend test |
| Wallet | balance/reserved_balance remain non-negative | atomic transaction + row lock | boundary/concurrency tests |
| Withdrawal | reserved balance covers pending/approved withdrawal | atomic reservation + locked profile | state-transition tests |
| Withdrawal payment | Only approved withdrawals can be paid | state transition + PDP | negative-state tests |
| Withdrawal replay | A paid withdrawal cannot create a second ledger transaction | idempotency key/transaction identity | replay test |
| Separation of duties | Approver cannot perform payer operation | permission + PDP | privilege matrix test |
| Ledger | Financial transaction records are immutable after creation | deny update/delete + code-path restriction | mutation denial tests |

## Board decision rules

- If the authoritative meaning of Promotion.budget is unclear, do not introduce a budget decrement or payout formula by assumption. Resolve the domain definition first.
- A security test that exposes an unimplemented invariant must remain a documented risk until the implementation and regression evidence exist; it must not be hidden by weakening the test.
- Concurrency tests should use TransactionTestCase or an equivalent real transaction boundary. Django documents that TestCase wraps tests in transactions and can mask select_for_update behavior; SQLite also does not provide SELECT FOR UPDATE semantics.
- Production financial verification must use PostgreSQL-compatible locking semantics before release.
- Every financial state transition must be both authorization-safe and state-safe. Authorization alone is not evidence of financial integrity.

## Threat mapping

- OWASP A01: Broken Access Control
- OWASP 2025 Business Logic Abuse: action-limit overrun, concurrent workflow-order bypass, object-state manipulation, missing transition validation, and quota violation
- OWASP A08: Software/Data Integrity
- OWASP A09: Security Logging and Alerting
- OWASP A10: Mishandling of Exceptional Conditions
- NIST SSDF: secure design, verification, vulnerability mitigation, and repeatable evidence

## Release gate

No financial feature is considered production-ready until:
1. the invariant has an unambiguous domain definition;
2. the enforcement point is server-side;
3. the mutation is atomic;
4. concurrency/replay behavior is tested;
5. the regression suite passes;
6. CI dependency and deployment checks pass;
7. evidence is linked to the security review record.
