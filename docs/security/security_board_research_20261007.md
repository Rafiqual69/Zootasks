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
- Promotion cumulative monetary budget: an application-level check exists in `PromotionClaimAdmin.approve_claims` (promotion row lock + earning-ledger sum + reject if the new payout would exceed budget). It is not a database-enforced cumulative invariant. A PostgreSQL-only concurrency regression test now exercises two competing $60 approvals against a $100 budget and asserts that only one claim is approved and only one $60 earning-ledger credit exists. This test passed on the exact candidate commit listed in the evidence snapshot below. Existing-payment reconciliation and legacy over-budget/orphaned ledger rows still require an explicit policy decision and safe reconciliation; do not silently rewrite historic financial records. Production activation remains gated.
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


## Evidence snapshot — 2026-10-14

Candidate branch: `security/full-integrated-security-board-20261007`  
Exact tested commit: `6f452f15a6df38ad628341bf3bb652061c0980a6`

The following GitHub Actions runs completed successfully for that exact commit:
- Security Gate: https://github.com/Rafiqual69/Zootasks/actions/runs/38349328400
- Security Review: https://github.com/Rafiqual69/Zootasks/actions/runs/38349328449
- PostgreSQL Financial Verification: https://github.com/Rafiqual69/Zootasks/actions/runs/38349328409

The PostgreSQL financial workflow ran 292 tests and executed the PostgreSQL-only competing promotion-approval test. The SQLite suite also ran 292 tests; the PostgreSQL row-lock-specific test is skipped on SQLite by design. These results support only the tested commit and scenarios; they are not a complete security audit, production validation, or certification.

## Owner authentication and device-binding status

- The Owner console is a queue-only request intake surface; submission does not execute a protected operation.
- Owner console authorization checks the configured immutable `OWNER_USER_ID`, staff/superuser flags, verified OTP, and a recent re-authentication timestamp.
- A backend WebAuthn assertion-verification service exists and validates the assertion against a stored, non-revoked credential, expected challenge, RP ID, exact origin supplied by its caller, required user verification, and sign counter. Unit tests currently cover denial for unknown/revoked credentials and invalid challenge input.
- A backend registration service exists, but the threat model explicitly records that there is no enabled public enrollment endpoint/UI and no completed bootstrap/recovery ceremony.
- **Not verified/implemented end-to-end:** a protected route invoking the assertion service; challenge issuance/consumption for authentication; fixed deployment-controlled RP/origin wired into the route; cryptographic device-bound session creation and per-request revocation checks; first-device bootstrap; recovery; independent Device 1/Device 2 proof; and notifications.
- Therefore, do not describe the Owner session as cryptographically device-bound, do not activate enrollment routes/UI, and do not permit protected production mutations until the documented acceptance gates and adversarial tests pass.

## Current release decision

PR #41 remains Draft/open and unmerged. Production migration, deployment, live financial-data reconciliation, and secret changes remain blocked. The next safe work item is to add or verify tests for the Owner authentication challenge lifecycle and session binding without enabling a public route, while separately defining the approved treatment of already-paid/legacy promotion claims that exceed a promotion budget.
