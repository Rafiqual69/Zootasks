# ZooTasks Security Board Research Record — 2026-10-07

## Research basis

The current security board work is aligned with:

- OWASP Business Logic Security: contextual authorization, state/workflow integrity, server-side business rules, concurrency and idempotency.
- OWASP Secure Code Review: workflow integrity, race-condition prevention, transaction atomicity, resource limits, authorization at workflow steps, secure defaults, and abuse-case review.
- OWASP Transaction Authorization: protected transaction data must remain bound to the authorized operation and workflow steps must not be skipped or reordered.
- OWASP ASVS 5.0: business logic, authorization, secure architecture/coding, data protection, and security logging/error handling are explicit control areas.
- NIST CSF 2.0: Govern, Identify, Protect, Detect, Respond, Recover are concurrent functions rather than a one-time checklist.

## Current board decisions

1. Financial mutations remain deny-by-default and production dual-control protected.
2. Task and promotion worker capacity are modeled separately from completed/approved accounting.
3. Row-local financial invariants are enforced at the database layer where practical.
4. State-transition rules remain transactionally enforced in application operations.
5. Legacy data is reconciled before new constraints are activated.
6. Concurrency verification must include PostgreSQL because production row-lock semantics matter.
7. Existing financial idempotency controls must not be weakened by workflow refactoring.
8. Production deployment/migration remains blocked until CI, migration review, PostgreSQL verification, regression, and security review are green.

## Current implementation tranche

- Withdrawal amount nonnegative database invariant: implemented.
- Task reservation/completed separation: implemented with reconciliation migration and targeted tests.
- Promotion reservation/completed separation: implemented with reconciliation migration and targeted tests.
- Promotion cumulative monetary budget invariant: not yet implemented; intentionally gated for dedicated data-reconciliation and concurrency review.
- Withdrawal state-transition database history: not forced into an unsuitable row-local CHECK constraint; authoritative transitions remain transactional.

## Source references

OWASP Business Logic Security:
https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html

OWASP Secure Code Review:
https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html

OWASP Transaction Authorization:
https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html

OWASP ASVS 5.0:
https://cornucopia.owasp.org/taxonomy/asvs-5.0

NIST CSF 2.0:
https://www.nist.gov/cyberframework

This record is engineering/security guidance, not legal advice or a claim of regulatory certification.
