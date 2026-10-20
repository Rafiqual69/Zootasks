# ZooTasks Read/Write Model Audit Plan

**Status:** Draft design / review artifact
**Scope:** Existing Django application; read-only planning, no runtime behavior change.
**Safety boundary:** This document does not authorize production migrations, financial-data edits, secret rotation, deployment, or merging any candidate.

## 1. Goal

Separate and document read paths from state-changing write paths so the existing application can be audited and improved incrementally without rebuilding it. Keep authorization, privacy, wallet correctness, task/promotion rewards, and withdrawal invariants explicit.

## 2. Read Model

A read operation retrieves and presents data only. It must not mutate balances, reservations, reward states, task capacity, or financial ledger rows.

### Required controls
- Authenticate the requester and enforce object-level/owner-scoped authorization before returning private data.
- Return only fields needed by the page/API; do not expose secrets, tokens, password hashes, raw environment configuration, or internal exception details.
- Mask payment identifiers in history views; keep raw bank/payment data out of logs and unnecessary template/API contexts.
- Apply pagination and bounded query sizes to histories and listings.
- Keep dashboard totals read-only. Document which source of truth each total represents (ledger, profile balance, reserved balance, or derived aggregate).
- Test that unauthorized cross-account reads return no private records.
- Test that read requests do not change database state.

### Initial read-path inventory (observed in reviewed branch)
- wallet.get_wallet_summary(user) aggregates earning/withdrawal ledger amounts and reads WorkerProfile.balance / reserved_balance.
- wallet.wallet scopes transactions and withdrawal requests to request.user and invokes the policy engine.
- wallet.withdrawal_history constructs masked account-holder and bank-account representations for the template.
- Task/promotion marketplace and claim history paths still require a complete route/query inventory before declaring the read model complete.

## 3. Write Model

A write operation changes durable state. Financial writes must be explicit, authorized, transactional, replay-safe, and auditable.

| Write path | Required invariant | Verification to add/confirm |
|---|---|---|
| Withdrawal request | Amount is finite, positive, valid precision, above configured minimum, and no greater than available balance | Parallel requests cannot reserve more than available balance; failed creation rolls back reservation |
| Withdrawal approve/reject/pay | Allowed status transitions only; reservation is settled/released exactly once | Concurrent admin actions and replay tests; ledger linkage and final balance reconciliation |
| Task reward approval | Claim is eligible; balance, total earned, completed-task count, ledger row and claim status commit together | Atomic rollback test; concurrent approval produces exactly one earning row |
| Promotion reward approval | Claim eligible; profile balance and total earned change once; ledger row matches claim and reward | Replay, amount mismatch, rollback and concurrent approval tests |
| Task/promotion claim | Capacity is never exceeded; duplicate claims are prevented; capacity counters have a documented meaning | PostgreSQL last-slot concurrency and rejected/replayed claim tests |
| Admin financial/state change | Permission and policy checks occur server-side; generic forms cannot bypass protected workflow | Permission matrix tests and audit-event tests |

## 4. Financial invariants to define before changing code

1. WorkerProfile.balance is never spent beyond the amount available under the agreed accounting policy.
2. reserved_balance equals the sum of withdrawal reservations that are still pending under the agreed status policy.
3. Every successful task/promotion reward has one matching earning ledger entry, and repeated approval cannot credit twice.
4. Claim status, profile totals, and ledger writes are consistent after commit; on failure, the whole operation rolls back.
5. Every withdrawal has a single, traceable lifecycle and at most one corresponding withdrawal ledger entry.
6. Historical ledger rows are never silently rewritten to make totals match. Differences require an approved reconciliation procedure and auditable adjustment.
7. Decimal amounts use the currency's documented precision; database constraints must reflect transaction-type semantics, not assumptions about all transaction signs.

These are target invariants to verify, not claims that the current production database already satisfies them.

## 5. Known review points

- The reviewed withdrawal request path uses transaction.atomic, validates finite precision, and performs a conditional database update to reserve balance. Confirm its behavior under concurrent PostgreSQL requests and rollback after request creation failure.
- Reviewed task and promotion admin reward paths lock claim/profile rows and check for existing linked earning transactions. Verify every other reward writer (views, signals, bots, management commands, admin actions) uses equivalent protection.
- WalletTransaction.amount and WithdrawalRequest.amount are decimal fields. Do not add a blanket non-negative constraint until transaction signs and adjustment semantics are documented and historical data is checked.
- completed_workers increments at claim/approval boundaries in different flows; establish whether it means claimed/reserved capacity or completed work before altering counters.
- PR #62 restores task-claim migration lineage and changes task-claim foreign keys to PROTECT, while removing Daphne from the WSGI-oriented runtime. Keep that PR Draft until migration rehearsal and ASGI/WebSocket/runtime requirements are verified.

## 6. Test matrix

### Read tests
- Anonymous requester cannot read private wallet or withdrawal data.
- Worker A cannot retrieve Worker B's transactions, withdrawals, claims, or payment identifiers.
- Sensitive values do not appear in rendered history or captured logs.
- Read-only views do not mutate profile, ledger, claim, or withdrawal state.
- Large histories remain bounded and paginated.

### Write tests
- Invalid amounts: empty, nonnumeric, zero, negative, NaN, infinity, excessive decimal places, and over-balance.
- Two simultaneous withdrawals cannot reserve more than available balance.
- Duplicate task/promotion approval does not double-credit.
- Existing linked ledger amount mismatch fails closed and requires reconciliation.
- Injected exception rolls back profile, ledger, and claim/status updates together.
- Concurrent last-slot claims do not exceed capacity.
- Invalid status transitions and insufficient permissions are rejected.
- PostgreSQL-specific locking tests run against disposable test data, not production records.

## 7. Safe implementation sequence

1. Inventory all reads and writes across views, admin actions, signals, bots, tasks, promotions, wallet, and management commands.
2. Record each write's transaction boundary, row locks, authorization policy, idempotency key/unique constraint, ledger linkage, and tests.
3. Add missing regression tests first on a separate branch.
4. Make the smallest service-boundary or code change needed; preserve current public behavior.
5. Run Django checks, migration-drift checks, complete regression tests, and focused PostgreSQL concurrency tests on disposable data.
6. Rehearse migrations from a representative legacy schema and verify backup restoration before any release.
7. Require independent review; keep changes Draft/unmerged until evidence is complete.

## 8. Release gates

- Exact-head CI passes for the exact commit proposed for release.
- Full secret scanning covers current files and Git history; findings are redacted in reports.
- No unreviewed financial invariant changes.
- PostgreSQL concurrency tests and migration rehearsal pass.
- Backup restoration is demonstrated, not merely backup-script syntax checked.
- Production runtime, database, ASGI/WebSocket needs, and deployment overrides are confirmed.
- Independent review approves the change.

## 9. Current evidence caveat

This is a design/audit plan based on source inspection, not a completed full-repository audit. Green CI on an older or different commit does not establish readiness of a newer head or prove legacy production migration/restore safety. No production changes are authorized by this document.