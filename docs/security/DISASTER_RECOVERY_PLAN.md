# ZooTasks Disaster Recovery & Business Continuity Plan

**Status:** Security design baseline — implementation is incremental and must not be treated as production-ready until recovery gates are proven.

## Recovery principles
1. Backups must not contain production secrets in plaintext.
2. Production data must be encrypted in transit and at rest by the storage provider or backup mechanism.
3. At least one recovery copy must live outside the primary production failure domain.
4. A backup is unverified until integrity validation and a restore drill pass.
5. Recovery must prefer a known-good restore point; never blindly restore the newest artifact after suspected compromise.
6. Wallet, ledger, withdrawal, task rewards, and promotion rewards receive the highest recovery-integrity priority.
7. Recovery automation must fail closed when integrity, migration, policy, dependency, or financial checks fail.
8. Recovery actions must be auditable without logging secrets or sensitive financial/identity payloads.

## Target architecture
Production web/app -> managed PostgreSQL + Redis -> provider backups/PITR -> encrypted portable database dump -> isolated/off-site recovery storage -> integrity verification -> isolated restore environment -> Django/security/migration/regression/financial checks -> health check -> controlled traffic promotion.

## Backup layers
### Layer A — Provider-native recovery
Use managed PostgreSQL volume backups and PITR where supported by the production provider.

### Layer B — Portable logical backup
Create scheduled PostgreSQL logical dumps and transfer them to storage outside the primary failure domain. Encrypt the dump before it leaves the trusted runtime.

### Layer C — Application/media recovery
Recover source from Git. User-uploaded media and other persistent assets require a separate encrypted backup policy. Production .env files and raw credentials must never be archived.

## Recovery objectives
Initial planning targets, to be validated by business-impact analysis:
- RPO: 15 minutes for critical financial database state where provider/PITR permits.
- RTO: 60 minutes for critical service restoration.
- Backup verification: automated daily integrity validation.
- Restore drill: monthly before production launch; quarterly after stable production operation, plus after major recovery-architecture changes.
- Financial reconciliation: mandatory after every restore drill and actual recovery.

These are targets, not guarantees.

## Known-good recovery gate
A recovery candidate must pass all applicable checks:
- cryptographic/integrity verification
- successful archive/database restore
- expected schema and migration state
- Django check
- production check --deploy
- dependency/security audit
- authorization/policy contract tests
- full regression suite
- wallet/withdrawal/task/promotion financial regression suite
- financial ledger invariants and reconciliation
- application health check
- no unexpected privilege or configuration drift

Only a candidate passing every required gate may be promoted.

## Suspected compromise rule
If the incident may involve credentials, application code, or database integrity:
1. Freeze automated promotion of new recovery candidates.
2. Preserve incident evidence.
3. Revoke/rotate affected credentials.
4. Identify the last known-good point before compromise.
5. Restore into an isolated environment.
6. Run all recovery gates.
7. Promote only after security evidence is complete.

## Secret handling
Never place the following in backups, GitHub issues, policy files, logs, or recovery manifests:
- Django SECRET_KEY
- database passwords
- API keys/secrets
- Telegram bot tokens
- SMTP passwords
- TOTP/recovery secrets
- private keys
- session cookies
- raw bank/payment identifiers
- raw government identity documents

Secrets belong in the production secret manager/provider secret store.

## Implementation status
- [x] Existing local backup hardened with restrictive permissions and fail-closed behavior.
- [x] Production deployment contract defined.
- [ ] Scheduled provider-native PostgreSQL backups configured in production.
- [ ] PITR enabled and recovery window documented.
- [ ] Encrypted portable PostgreSQL dump implemented.
- [ ] Isolated/off-site backup storage configured.
- [x] Automated backup integrity verification (archive/gzip/path/sensitive-artifact checks).
- [ ] Automated restore sandbox.
- [ ] Financial reconciliation after restore.
- [ ] Controlled failover automation.
- [ ] First successful full restore drill.
- [ ] Recovery RPO/RTO measured and recorded.

No incomplete item should be represented as production-ready.

## Research basis
NIST SP 800-34 Rev. 1 covers backup/recovery strategy, alternate recovery capability, testing/exercises, and maintenance. Django's deployment checklist explicitly calls for database backups and protection of database credentials and production secrets.
