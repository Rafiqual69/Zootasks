# ZooTasks Coordinated Security Remediation Plan

**Plan status:** Active; remediation and validation are in progress.  
**Scope:** PR #66, branch `security/ci-ephemeral-secret-20261022`.  
**Production:** No production deployment or production migration is authorized by this plan.

## Evidence snapshot (2026-10-22)

- Latest inspected commit before this plan: `122ffd3fdedcc7f50863d7866af162dc9cacd04e`.
- Security Review run `39662945981` failed at Dependency audit. Full regression passed. Backup smoke and diff hygiene were skipped after the dependency-audit failure.
- PostgreSQL Financial Verification run `39662945837`: Django system check, migration drift check, PostgreSQL migration apply, and full PostgreSQL regression had passed at the latest inspection; workflow was still finishing.
- Security Gate run `39662946139`: Django checks, deployment security check, migration drift, and policy contract steps had passed at the latest inspection; workflow was still finishing.
- CI log confirmed `SECRET_KEY` appears masked as `***` in the inspected run. This is positive evidence for that run only, not a guarantee about every workflow or future log.
- Dependency audit found one unresolved item: `Twisted 26.4.0 / CVE-2026-106454`. Do not suppress this finding or declare the version fixed solely because it is newer than 25.5.0.

## Coordinated workstreams and acceptance criteria

### A. Dependency vulnerability — release blocker
**Finding:** CI's `pip-audit` reports CVE-2026-106454 against Twisted 26.4.0 and does not provide a fix version. NVD describes the issue as IMAP wildcard-to-regex catastrophic backtracking and currently says no fixed release is available. Debian separately marks its package 26.4.0-4 vulnerable and 26.4.0-5 fixed, indicating that a distribution patch level matters. Do not assume the plain PyPI wheel contains that distribution patch.

**Actions**
1. Verify the exact upstream security commit and patch diff against the installed PyPI artifact.
2. Determine whether the upstream fix has been released in a new upstream version or only backported by downstream distributions.
3. Prefer an official upstream release containing the fix. If no release exists, evaluate a reviewed, immutable upstream commit pin or a maintained downstream patched package, with provenance, reproducible install, licensing and deployment compatibility reviewed.
4. Re-run `pip-audit` on the actual resolved environment, not only the requirements text. If the advisory database still flags a verified patched commit, document evidence and choose a transparent, narrow, time-limited advisory exception only after independent security review; do not silently ignore the advisory.
5. Check Daphne/Twisted compatibility, ASGI startup, and full regression. Keep the dependency audit gate failing until the evidence-backed disposition is accepted.

**Acceptance:** Resolved dependency and advisory evidence recorded; install reproducible; audit passes or an independently reviewed, explicit and expiring exception is documented; regression passes.

### B. CI secrets and data-leak prevention
- Generate a fresh random Django key per workflow run.
- Apply GitHub Actions masking before writing the key to `GITHUB_ENV`.
- Never print environment dumps, credentials, tokens, private user data, wallet identifiers, or raw exception payloads.
- Inspect all three latest workflow logs and backup artifacts using synthetic sentinel secrets. Verify that sentinels are absent and the secret is masked.
- If any historical fixed CI key was reused outside CI, rotate it in the real secret store; do not assume that happened without evidence.

**Acceptance:** All current logs/artifacts checked; no unmasked secret or personal data observed; test evidence recorded.

### C. Database migration and claim-history integrity
- Keep `TaskClaim.task` and `TaskClaim.worker` model relations aligned with `PROTECT` and the committed migration.
- Require migration drift check, migration apply on disposable PostgreSQL, and SQLite regression where applicable.
- Add or verify tests proving task/user deletion cannot erase claim history and that expected protected-delete errors are handled.
- Never run these test migrations against production.

**Acceptance:** Migration graph clean, model state matches migration state, PostgreSQL apply and regression pass, claim-history protection tests pass.

### D. Wallet, reward, and withdrawal integrity
- Preserve the existing ledger; do not rewrite balances or delete financial history as a “cleanup.”
- Verify earning/withdrawal/adjustment sign and identity constraints.
- Test concurrent withdrawal requests, concurrent approval/payment, duplicate submissions, retries/idempotency, transaction rollback, insufficient/reserved balance, rejected/cancelled transitions, and ledger reconciliation.
- Payment action must remain separately permissioned from approval; retries must not double-pay.
- Use synthetic fixtures only; do not trigger real payment providers during CI.

**Acceptance:** Deterministic automated tests pass, concurrent tests demonstrate no duplicate debit/payment, reconciliation matches ledger, and an independent reviewer signs off.

### E. Backups, recovery, and privacy
- Run backup syntax and isolation smoke tests even if an earlier gate fails; report each gate independently where possible.
- Ensure backups exclude `.env`, tokens, logs, virtual environments, caches, and unrelated private files unless explicitly required and encrypted.
- Verify restrictive file permissions, restore a synthetic backup into an isolated disposable database, and confirm expected rows/schema.
- Review bot, Django, admin-export, error, and CI logs for sensitive data.

**Acceptance:** Backup and isolated restore tests pass, exclusions and permissions are asserted, and no real user data is used.

### F. Django deployment and platform security
- Review DEBUG, allowed hosts, HTTPS/proxy trust, secure session/CSRF cookies, HSTS, CORS, static/media handling, admin access, and secret source.
- CI values such as `SECURE_HSTS_SECONDS=0` are test inputs, not proof that production is configured securely.
- Verify settings against the actual deployment platform before proposing changes; don't invent production configuration.
- Do not remove Daphne/ASGI components without dependency and runtime review.

**Acceptance:** Environment-specific evidence and a rollback plan exist; no secret is committed; an independent reviewer approves.

### G. Automation and release gate
1. Fetch status for the latest branch SHA and all required workflows.
2. Inspect failed steps and logs, redacting any secret values.
3. Fix one root cause at a time in a small reviewable commit.
4. Re-run all required gates against the final head: Django/system checks, policy engine, full regression, dependency audit, migration drift, PostgreSQL migration and financial regression, backup isolation/restore smoke, diff hygiene, and secret/PII log review.
5. Require independent human review before merge. CI success is necessary, not sufficient.
6. Keep PR draft/unmerged until acceptance criteria are met.
7. Production migration/deployment requires separate explicit authorization, verified production backup/restore evidence, a rollback plan, and a change window.

## Research references

- NVD CVE-2026-106454: https://nvd.nist.gov/vuln/detail/CVE-2026-106454
- Debian tracker for CVE-2026-106454: https://security-tracker.debian.org/tracker/CVE-2026-106454
- Upstream Twisted fix commit cited by NVD: https://github.com/twisted/twisted/commit/2f8a3c29246f4eb324690e06a9767a11dc4aec9
- OWASP ASVS: https://asvs.owasp.org/
- Django deployment checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

## Current disposition

The dependency audit failure is an active release blocker. Do not merge, deploy, run production migrations, or claim that every issue is solved until the above evidence is recorded. This plan coordinates the work; it does not itself prove controls have passed or constitute a guarantee of complete security.
