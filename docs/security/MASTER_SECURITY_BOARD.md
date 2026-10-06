# ZooTasks Master Security Board

**Status:** Normative planning and verification board — fail-closed  
**Baseline:** `main` at the security baseline reviewed on 2026-10-06  
**Rule:** This board does not declare production readiness. A control is complete only when its evidence exists and all required protected CI/review gates pass.

## 1. Governing standards

This board is aligned to:
- NIST Cybersecurity Framework 2.0: Govern, Identify, Protect, Detect, Respond, Recover.
- NIST Secure Software Development Framework (SSDF) 1.1; monitor the NIST 1.2 revision work and adopt it when finalized where applicable.
- OWASP Top 10:2025.
- OWASP Application Security Verification Standard (ASVS) as the application-control verification baseline.
- Django production security/deployment guidance.
- Railway PostgreSQL backup/PITR/restore guidance.
- NIST SP 800-34 Rev.1 for contingency planning and recovery testing.

These are control references, not claims of certification.

## 2. Non-negotiable security constitution

1. Unknown = deny.
2. Ambiguous authorization = deny.
3. Policy parse/validation failure = deny protected operations.
4. Source-control access never implies production-data access.
5. Financial state is integrity-critical and must not be casually deleted or rewritten.
6. AI/automation has no autonomous financial-write authority.
7. Secrets never enter Git, issues, logs, backups, test artifacts, URLs, or client-visible errors.
8. Production recovery is blocked until an isolated restore and all required security/financial gates pass.
9. No force-push or direct automation push to protected `main`.
10. No merge while a required review, security gate, financial gate, or recovery gate is missing or failed.

## 3. Master control board

| Domain | Control | Current evidence/status | Gate |
|---|---|---|---|
| Governance | Read/Write Constitution | Present on main | PASS baseline |
| Governance | Machine policy + schema | Policy 1.1.4 present on main | PASS baseline |
| Authorization | Worker authorization | PR #12 merged and verified | PASS baseline |
| Authorization | Financial Task/Promotion admin boundary | PR #25 merged and verified | PASS baseline |
| Authorization | Sensitive-field/object-level rules | Policy + regression coverage present | CONTINUOUS |
| Financial | Wallet/ledger integrity | Existing financial regression suite | CONTINUOUS |
| Financial | Withdrawal separation of duties | Policy rules + tests | CONTINUOUS |
| Financial | AI financial writes denied | Explicit policy rules | CONTINUOUS |
| Authentication | Owner boundary/MFA/re-auth | Existing controls; evidence must remain current | CONTINUOUS |
| Secrets | Environment/provider secret separation | Production contract + policy | CONTINUOUS |
| Supply chain | Immutable CI action pins | PR #26/main baseline | PASS baseline |
| Supply chain | Dependency audit | Protected CI | CONTINUOUS |
| Deployment | Production DATABASE_URL required | PR #27 draft baseline | PENDING MERGE/REVIEW |
| Deployment | No production SQLite fallback | Production contract | PENDING MERGE/REVIEW |
| Deployment | HTTPS/HSTS/secure cookies | Production contract | PENDING runtime verification |
| Recovery | Backup verifier | Main baseline | PASS baseline |
| Recovery | Synthetic PostgreSQL restore drill | PR #30 CI evidence | PASS CI |
| Recovery | Provider volume backups | Issue #31 | BLOCKED on provider access |
| Recovery | PITR | Issue #31 | BLOCKED on provider access |
| Recovery | Encrypted off-site logical dump | Issue #31 | BLOCKED on runtime/storage integration |
| Recovery | Production-like isolated restore | Issue #31 | BLOCKED on provider/runtime access |
| Recovery | Financial reconciliation after restore | Issue #31 | REQUIRED |
| Recovery | RPO/RTO measurement | Issue #31 | REQUIRED |
| Persistent assets | Media/non-DB recovery | Issue #32 | REQUIRED |
| Detection | Security/audit events | Policy requires safe audit metadata | CONTINUOUS |
| Incident response | Credential rotation/evidence preservation | DR plan | REQUIRED |
| Privacy | Data minimization / no raw identity docs in repo | Constitution + Issue #29 | CONTINUOUS |
| Change control | Protected PR + required CI | Current governance | CONTINUOUS |

## 4. Production-readiness hard gate

ZooTasks MUST remain **not production-ready** until all applicable items below have evidence:

### Code and application
- Django system check passes.
- Django deployment check passes with production configuration.
- Migration drift check passes.
- Full regression passes.
- Financial regression passes.
- Authorization/policy contract and engine tests pass.
- Sensitive-field/object-level authorization tests pass.
- Dependency/security audit passes.
- Diff hygiene passes.

### Financial integrity
- Wallet invariants pass.
- WalletTransaction immutability and ownership invariants pass.
- Withdrawal state/idempotency/separation-of-duties checks pass.
- Task reward invariants pass.
- Promotion reward invariants pass.
- Ledger reconciliation passes after recovery tests.
- No destructive admin operation can erase financial history.

### Supply chain and CI
- Protected workflows use immutable action references.
- Workflow permissions remain least-privilege.
- Checkout credentials are not persisted.
- Secret scanning and dependency auditing pass.
- No unreviewed workflow/security-policy change reaches main.

### Production infrastructure
- Production uses PostgreSQL; SQLite fallback is impossible in production mode.
- Production secrets are provider-managed.
- HTTPS, secure cookies, CSRF trusted origins, proxy trust and HSTS are verified against the actual deployment topology.
- Production health/observability and alerting are operational.
- Database and persistent asset access follow least privilege.

### Recovery
- Scheduled provider backups enabled.
- PITR enabled and healthy.
- Portable encrypted logical dump exists outside the primary failure domain.
- At least one isolated provider/runtime restore has succeeded.
- Recovered environment passes application/security/financial gates.
- Media/persistent non-DB assets have an isolated restore test.
- Actual RPO/RTO is measured.
- Recovery owner and controlled cutover procedure are documented.

## 5. Fail-closed recovery sequence

1. Freeze promotion if compromise or integrity uncertainty exists.
2. Preserve evidence.
3. Rotate/revoke affected credentials.
4. Select a known-good recovery point.
5. Restore only into an isolated environment.
6. Verify archive/database/media integrity.
7. Verify schema and migrations.
8. Run Django and deployment checks.
9. Run dependency/security checks.
10. Run authorization/policy tests.
11. Run full regression and financial regression.
12. Reconcile financial state against ledger invariants.
13. Verify application health and privilege/configuration drift.
14. Record RPO/RTO and evidence.
15. Only then permit controlled promotion.

## 6. Security-data boundary

Never store in GitHub, issues, logs, backups, CI artifacts, policy files, URLs or client-visible errors:
- SECRET_KEY
- DATABASE_URL/passwords
- API keys/secrets
- Telegram bot tokens
- SMTP passwords
- MFA/TOTP secrets or recovery codes
- private keys
- session cookies
- raw bank/payment identifiers
- raw government identity documents

Only minimum necessary verification metadata may be retained in controlled records.

## 7. AI and automation boundary

Automation may:
- inspect code and evidence,
- run approved tests,
- prepare feature/security branches,
- produce reports,
- propose changes.

Automation MUST NOT:
- invent authorization,
- bypass required review,
- push directly to protected main,
- force-push protected refs,
- expose secrets,
- directly mutate production financial state,
- approve/pay withdrawals on its own,
- promote an unverified recovery candidate.

## 8. Evidence standard

Every security change must leave:
- exact commit/PR reference,
- test/gate results,
- scope statement,
- security impact,
- rollback/recovery path,
- reviewer evidence where required.

A passing test is evidence for that test only; it is not a blanket security guarantee.

## 9. Current blockers

The following are intentionally not marked complete:
- production provider backup/PITR activation,
- encrypted off-site logical dump integration,
- provider/runtime isolated restore,
- post-restore financial reconciliation evidence,
- measured production RPO/RTO,
- persistent media/non-database recovery evidence,
- final production deployment verification.

No source-control change may silently convert these blockers into PASS.

## 10. Change-control rule

Before merging any future security or financial change:
1. Re-read this board and the Read/Write Constitution.
2. Start from current protected main.
3. Keep scope minimal.
4. Run the relevant focused tests.
5. Run all protected CI gates.
6. Review changed files and diff hygiene.
7. Verify no secrets or production data are present.
8. Require the configured protected-branch review.
9. Merge only after all required evidence is green.
10. Never auto-merge.

## 11. Research maintenance

Review this board whenever:
- OWASP Top 10 / ASVS changes,
- NIST SSDF/CSF guidance materially changes,
- Django major security/deployment guidance changes,
- Railway production recovery architecture changes,
- a security incident occurs,
- Owner/privilege/recovery architecture changes,
- a new financial feature is introduced.

**Board conclusion:** The project has a strong security baseline, but security is not a one-time “complete” state. Production readiness is an evidence-based gate, and unknown or unverified areas remain blocked by design.
