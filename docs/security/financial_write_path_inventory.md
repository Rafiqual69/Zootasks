# ZooTasks Financial Write-Path Inventory (Partial)

**Status:** Source-based review notes; not a completed audit.  
**Reviewed ref:** `security/migration-dependency-candidate-20261021`  
**Purpose:** Record confirmed write boundaries and verification work without copying secrets, customer data, payment identifiers, or production records.  
**Safety:** No runtime code or financial data changed. Do not treat this document as release approval.

## Scope and confidence

This is a partial inventory from source files reviewed on the stated branch. GitHub code-search returned no useful indexed matches for the targeted write expressions, so absence from this list does **not** prove a writer does not exist. The remaining repository-wide search must include views, admin actions, Telegram handlers, signals, management commands, scheduled tasks, and any deployment-only code.

## Observed write paths

| Path | Transaction / protection observed | Main follow-up |
|---|---|---|
| `backend/wallet/views.py::request_withdrawal` | `transaction.atomic`; finite Decimal and precision checks; conditional profile update reserves funds before creating a request | Add PostgreSQL concurrency test for two simultaneous requests, plus injected request-create failure to prove reservation rollback. |
| `backend/wallet/admin.py::approve_withdrawals` | Per-request atomic block; locks withdrawal row; pending-state guard; policy check; locks profile | Verify all status transitions against one explicit state machine; test concurrent admin actions and stale reservation cases. |
| `backend/wallet/admin.py::reject_withdrawals` | Atomic block; locks withdrawal and profile; releases reserved amount and marks rejected together | Test rollback and exact-once release under replay/concurrency. |
| `backend/wallet/admin.py::mark_withdrawals_paid` | Atomic block; locks withdrawal/profile; only approved requests proceed; operation-bound OneToOne ledger identity; amount mismatch fails closed | Test exact-once ledger creation, legacy-row reconciliation, concurrent payment actions, and balance/reservation invariants. Keep any reconciliation manual and auditable. |
| `backend/tasks/admin.py::approve_submissions` | Atomic block; locks claim and profile; checks existing claim-linked earning row; updates profile, ledger and claim in the same transaction | Test concurrent approval, exception rollback, and current-reward vs historical-ledger mismatch. |
| `backend/promotions/admin.py::PromotionClaimAdmin.approve_claims` | Atomic block; locks claim/profile; checks existing claim-linked earning row; updates profile, ledger and claim together | Test concurrent approval, rollback, amount mismatch, and bounded/redacted operational logging. |
| `backend/tasks/views.py` / `backend/promotions/views.py` claim and proof paths | Reviewed promotion claim flow is atomic and locks promotion; worker identity is unique per promotion. Telegram task claim flow also uses atomic + task row lock | Confirm all web/bot claim paths enforce identical capacity semantics; run PostgreSQL last-slot concurrency tests. |
| `backend/run_bot.py::withdrawal_message` | Final creation runs atomically, locks the profile and conditionally reserves funds before creating the withdrawal request | Web and bot flows duplicate business logic. Add parity tests and plan a shared service only after behavior is documented; do not change accounting semantics in this documentation-only step. |
| `backend/run_bot.py::get_telegram_account` | Creates/updates Telegram identity and worker profile | Test account-linking uniqueness, retry behavior, and that unverified identity cannot access another user's account. |

## Privacy and data-minimization observations

- `backend/wallet/views.py::withdrawal_history` passes masked account-holder/account-number representations to its template rather than raw values. Add a regression test that raw values are absent from rendered output.
- The Telegram `contact` handler includes direct contact details in a public bot reply. Treat these as public disclosures, not secrets; verify the owner intentionally wants every bot user to see them. This inventory deliberately does not repeat those values.
- Avoid logging raw bank/MFS account details, bot tokens, environment values, proof text, or full request/object representations. For exception events, prefer event name, exception class, and a non-sensitive correlation identifier.
- A source scan has **not** been completed for the full current tree or Git history. No claim is made that the repository is free of leaked credentials or personal information.

## High-priority verification backlog

1. **Writer completeness:** Enumerate every call site that creates `WalletTransaction`, changes `WorkerProfile.balance` / `reserved_balance` / `total_earned`, changes withdrawal status, or changes task/promotion capacity counters.
2. **Withdrawal state machine:** Specify permitted transitions (pending → approved/rejected; approved → paid) and define when reservations are held/released/consumed. Test each transition for duplicate and concurrent execution.
3. **Accounting reconciliation:** Define the approved relationship between profile aggregates, reserved balance, withdrawal rows, and ledger rows. Never silently rewrite historical ledger data to force totals to match.
4. **Capacity semantics:** Establish whether `completed_workers` means claims reserved, work completed, or rewards approved. Preserve current behavior until that definition is confirmed.
5. **Read isolation:** Test cross-account access for wallet, withdrawals, task claims, promotion claims, and proof data; verify read-only routes do not mutate state.
6. **Security scanning:** Run a full secret scan on the current tree and Git history using a trusted scanner. Report only redacted finding metadata; do not paste secret values into issues, logs, or PR comments.
7. **Verification evidence:** Run Django checks, migration-drift checks, full tests, and PostgreSQL concurrency tests against disposable data on the exact proposed commit. Rehearse migrations and demonstrate backup restoration before release.

## Release status

No tests were executed by this document-only change. No production migration, deployment, merge, secret rotation, or production-data operation was performed. Keep related security changes Draft until exact-head CI, migration rehearsal, dependency/runtime review, secret-history scan, restore proof, and independent review are complete.
