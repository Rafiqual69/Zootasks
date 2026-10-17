# Owner security migration reconciliation

## Why a controlled integration is required

The active branch `fix/restore-task-claim-migration-20261009` and
`feat/owner-session-binding-foundation` are divergent histories, not a safe
fast-forward. GitHub's comparison reports 512 commits on the Owner-security
side and 360 commits on the active side since their merge base. A wholesale
merge would also bring unrelated AI, admin, promotion, task and wallet changes.

The Owner-security branch contains useful building blocks: canonical
`AccountEntity` policy checks, Owner trusted-device enrollment, server-side
session bindings, WebAuthn/passkeys, email/social identity workflows, and
nominee/succession features. Those features depend on model fields and
migration history not represented by the active branch's current `accounts`
models.

The active branch also carries financial-integrity changes that must not be
discarded: `PROTECT` on task/promotion claim relationships, withdrawal-to-
transaction reconciliation, and wallet/task/promotion capacity constraints.
Do not cherry-pick or merge the Owner-security branch wholesale.

## Current risks

- The checked-out `AccountEntity` model does not represent legacy database
  columns such as `identity_email`, `email_verified_at`, and
  `webauthn_user_handle`.
- The legacy schema contains Owner-related tables not represented by the
  active branch's current models.
- Both branches use overlapping migration names for different operations.
  A database migration record with a matching name does not guarantee the
  current file describes the operation that originally created the schema.
- The main SQLite database previously passed SQLite integrity and foreign-key
  checks, but those checks do not prove that Django's migration graph matches
  the checked-out source.
- Invalid Ed25519 signatures must be handled as `cryptography.exceptions.InvalidSignature`.
  Treating only `ValueError` and `TypeError` as invalid-signature cases can
  turn routine authentication failures into server errors.

## Safe integration sequence

1. Preserve the current financial-integrity branch and make a separate
   integration branch from it.
2. Run the read-only `python manage.py audit_schema_drift --app accounts`
   command against a disposable copy of the target database. Use
   `--app tasks --app promotions --app wallet` as a separate scoped check.
3. Compare the output with `showmigrations`, `migrate --plan`, actual SQLite
   tables/columns, and the recorded migration table. Do not infer that a
   schema difference is safe to repair automatically.
4. Define a new migration lineage for Owner-security models with unique,
   non-conflicting migration names. Where the database already has a legacy
   column/table, use an explicitly reviewed state/database reconciliation
   strategy rather than blindly adding it again.
5. Port the minimum required model and service dependencies, preserving
   current financial constraints and `PROTECT` relationships. Review every
   `CASCADE`, especially on users, claims, and wallet-related records.
6. Test on a fresh database and a copy of the legacy database. Include
   migration forward checks, reverse/rollback rehearsal where feasible,
   invalid/expired/replayed WebAuthn challenge tests, revoked-device session
   tests, unauthorized-owner tests, and wallet/task/promotion regression tests.
7. Only merge after the latest CI run passes and the migration plan is empty
   on both rehearsal databases. Never run a repair migration against the main
   database before its exact before/after schema and data effects are reviewed.

## Scope of the audit command

`audit_schema_drift` is read-only. It compares current Django model columns
with the connected database, identifies `accounts_*` tables not represented
by selected current models, and lists applied migration records missing from
the current checkout. It does not repair schemas, delete tables, modify
migration records, or update user/financial data.

The command is a diagnostic aid, not a substitute for reviewing migration
operations, constraints, indexes, data migrations, and business invariants.
