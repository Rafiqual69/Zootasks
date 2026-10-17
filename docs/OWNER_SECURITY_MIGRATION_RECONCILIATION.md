# Owner security migration reconciliation

## Current verified rehearsal findings (2026-10-18)

The disposable `backend/db-migration-rehearsal.sqlite3` database was checked
using the read-only schema audit, Django migration inspection, SQLite integrity
checks, and the project's test suite. Results observed in this rehearsal:

- `PRAGMA integrity_check` returned `ok` and foreign-key violation count was
  zero.
- The current source migration plan was empty; `showmigrations` showed the
  current financial-integrity migrations applied.
- The migration recorder also contained legacy Owner-security, advertiser,
  promotion-funding, task-counter, and wallet-permission migration names absent
  from the current checkout. An empty current migration plan does not resolve
  those orphaned legacy records or prove equivalent schema operations.
- `accounts_accountentity` had legacy `identity_email`,
  `email_verified_at`, and `webauthn_user_handle` columns not represented by
  the current model. Owner-specific tables were present but not represented by
  current models.
- Five `accounts_owneremailverificationchallenge` rows were all marked used,
  linked to an existing AccountEntity, and had no missing expiry. Attempt
  counts were four records at zero and one at one. No tokens or emails were
  displayed. Do not delete these records based only on this aggregate result.
- Current branch checks reported no Django system-check or model/migration
  state differences, and 129 tests passed against the configured rehearsal
  environment. This does not test the legacy Owner-security integration.

These results are specific to the rehearsal file and do not establish that the
main database or a deployed environment has the same state. The main database
has not been migrated or repaired as part of this work.

## Why a controlled integration is required

The active branch `fix/restore-task-claim-migration-20261009` and
`feat/owner-session-binding-foundation` are divergent histories, not a safe
fast-forward. A wholesale merge would also bring unrelated AI, admin,
promotion, task and wallet changes.

The Owner-security branch contains useful building blocks: canonical
`AccountEntity` policy checks, Owner trusted-device enrollment, server-side
session bindings, WebAuthn/passkeys, email/social identity workflows, and
nominee/succession features. Those features depend on model fields and
migration history not represented by the active branch's current `accounts`
models.

The active branch also carries financial-integrity changes that must not be
discarded: `PROTECT` on task/promotion claim relationships,
withdrawal-to-transaction reconciliation, and wallet/task/promotion capacity
constraints. Do not cherry-pick or merge the Owner-security branch wholesale.

## Dependency audit finding

The first GitHub security-gate run passed Django checks, migration drift checks,
and all 271 tests, then failed `pip-audit` because the installed dependency
tree included Twisted 26.4.0 flagged as CVE-2026-106454. The reported issue is
an IMAP pattern regular-expression denial of service; the project's deployment
uses Gunicorn's WSGI entry point, and the repository had no Daphne/Channels
usage found during source inspection. Daphne was therefore removed from
`backend/requirements.txt` rather than suppressing the advisory or pinning an
unreleased upstream patch. Re-run all workflows and verify the dependency
tree before treating this remediation as complete.

## Confirmed migration-name collisions

The branches reuse migration names for different operations:

- `accounts.0005`: current branch protects the WorkerProfile user relation;
  Owner-security branch creates AdvertiserProfile.
- `promotions.0006`: current branch protects promotion claim history;
  Owner-security branch merges promotion funding and options histories.
- `tasks.0004`: current branch protects task claim history; Owner-security
  branch adds and backfills `Task.claimed_workers`.
- `wallet.0005`: current branch adds a withdrawal-to-ledger identity and
  performs a guarded backfill; Owner-security branch adds dashboard permission
  metadata.

These are not interchangeable. Do not copy, rename, fake, or mark migrations
applied merely to make the plan appear empty. Migration files and their
dependencies must be reconciled with the actual schema and data.

## Current risks

- The checked-out `AccountEntity` model does not represent legacy database
  columns such as `identity_email`, `email_verified_at`, and
  `webauthn_user_handle`.
- The legacy schema contains Owner-related tables not represented by the
  active branch's current models.
- The current audit compares tables and columns; it does not fully compare
  constraints, indexes, triggers, defaults, or data semantics.
- SQLite integrity and foreign-key checks do not prove that Django's migration
  graph matches the checked-out source.
- Invalid Ed25519 signatures must be handled as
  `cryptography.exceptions.InvalidSignature`; otherwise routine invalid
  signatures may become server errors.

## Safe integration sequence

1. Preserve the current financial-integrity branch and make a separate
   integration branch from it.
2. Run the read-only `python manage.py audit_schema_drift` command against a
   disposable copy of each target database. Specify `--app` repeatedly to
   scope model-column checks.
3. Compare results with `showmigrations`, `migrate --plan`, SQLite tables
   and columns, migration recorder rows, constraints, indexes, and data.
4. Define a reviewed, unique migration lineage for Owner-security models.
   Where a legacy column/table already exists, use an explicitly reviewed
   state/database reconciliation strategy rather than blindly adding it.
5. Port the minimum required model and service dependencies while preserving
   current financial constraints and `PROTECT` relationships. Review every
   `CASCADE`, especially on users, claims, and wallet-related records.
6. Test both a fresh database and a disposable legacy copy. Include forward
   migration checks, rollback rehearsal where feasible, invalid/expired/
   replayed WebAuthn challenges, revoked-device sessions, unauthorized-owner
   access, and wallet/task/promotion regression tests.
7. Require successful CI on the exact final commit and a reviewed migration
   plan on both rehearsal databases. Do not run a repair migration against the
   main database until exact before/after schema and data effects are approved.

## Scope and limits of the audit command

`audit_schema_drift` is read-only. It compares current model columns with the
connected database, identifies `accounts_*` tables not represented by current
models, and lists applied migration records missing from the current checkout.
It does not repair schemas, delete tables, modify migration records, or update
user/financial data. It does not fully verify constraints, indexes, triggers,
or semantic correctness.

The command is a diagnostic aid, not a substitute for reviewing migration
operations and business invariants.
