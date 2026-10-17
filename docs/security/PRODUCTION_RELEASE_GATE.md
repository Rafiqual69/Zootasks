# Controlled Production Release Gate

**Status: blocked by default.** This repository configuration does not authorize a production release, database migration, or merge.

## Release requirements

1. Keep the candidate PR in Draft until an independent reviewer has examined the full diff and the current-head CI results.
2. Verify a recent provider backup/PITR recovery point and confirm rollback steps. Do not use production data in public artifacts or CI.
3. Before applying any new migration, run `DATABASE_URL='<private connection string>' bash scripts/preflight_financial_migrations.sh` from a secure operator environment. The script prints only aggregate invariant names and counts, exits nonzero if any count is nonzero, and fails closed if the expected schema is missing. Do not paste connection strings or raw production data into chat, GitHub, or logs.
4. Review every preflight finding and reconcile the affected records through an audited, approved process. Do not silently clamp balances, rewards, claim counts, or withdrawal amounts to make constraints pass.
5. Run migrations as a separate, explicitly approved operator action only after the preflight is clear and a recovery point is verified. The Railway pre-deploy command intentionally uses `migrate --check`, not `migrate`; it refuses deployment when migrations remain unapplied.
6. Confirm financial reconciliation and the task/promotion/withdrawal regression tests against a safe, representative non-production database.
7. Only after those checks, set `ZOOTASKS_APPROVED_RELEASE_SHA` in the Railway service to the exact reviewed Git commit SHA. The pre-deploy script compares it to Railway's `RAILWAY_GIT_COMMIT_SHA`, so a later commit is blocked until separately approved.
8. Review the resulting deployment manually and remove the approval variable after the intended release if no further deploy of that exact SHA is needed.

## Fail-closed checks

The pre-deploy script refuses to continue unless:
- the approved SHA exactly matches the commit being deployed;
- `PRODUCTION_MODE=true`;
- `SECRET_KEY`, `DATABASE_URL`, and `ALLOWED_HOSTS` are present;
- all migrations have already been applied; and
- Django's `check --deploy` succeeds.

Static assets are collected during image build, not in Railway's separate pre-deploy container, because that container's filesystem changes do not persist to the running application.

The preflight checks aggregate counts for legacy task/promotion capacity, reward/budget values, wallet invariants, withdrawal amounts, and ledger-operation identity constraints. It does not print user identifiers, bank details, or transaction payloads.

This gate is a technical safeguard, not a substitute for review, backups, a tested restore, financial reconciliation, or repository branch protection. No production settings were changed by this repository edit.
