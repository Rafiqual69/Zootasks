# ZooTasks Coordinated Security Remediation Plan

**Plan status:** Active; remediation and validation are in progress.  
**Scope:** PR #66, branch `security/ci-ephemeral-secret-20261022`.  
**Production:** No production deployment or production migration is authorized by this plan.

## Evidence snapshot (2026-10-24)

- Latest validated commit: `a039eab4466600a5f1f0465b2ab86ad7324dc07b`.
- Security Review #931 succeeded: Twisted installed-artifact semantics, Django system/deployment checks, migration drift, Read/Write policy contract, policy engine, full regression, dependency audit, backup isolation smoke, and diff hygiene all passed.
- ZooTasks Security Gate #1179 succeeded, including full regression, dependency audit, backup isolation smoke, and diff hygiene.
- PostgreSQL Financial Verification #310 succeeded on the same commit.
- The prior head failed the dependency audit on `Twisted 26.4.0 / CVE-2026-106454`; the temporary RC pin and focused tests passed on the current head.
- Upstream fix commit `2f8a3c29246f4eb324690e06a9767a11dc4aec9f` was inspected. It escapes all non-IMAP-wildcard characters in `wildcardToRegexp`. The official upstream tag `twisted-26.10.0rc1` was inspected and contains that implementation.
- As a temporary testable mitigation, `backend/requirements.txt` now pins `Twisted==26.10.0rc1`. This is a pre-release, not a final-release recommendation. Replace it with the first verified final upstream release before merge when available, and rerun all gates.
- Two CI workflows include a focused installed-artifact check for regex metacharacters and IMAP `*` / `%` semantics; both relevant workflows passed on the latest validated commit.
- Retrieved Security Gate logs show `SECRET_KEY: ***`; a bounded pattern check found no unmasked `SECRET_KEY`-shaped value in that log. This does not prove all historical logs or every artifact are free of sensitive data.
- The two new unsupported-HTTP-method regression tests for task and promotion proof submission passed as part of the full regression run.

## Coordinated workstreams and acceptance criteria

### A. Dependency vulnerability — release blocker
**Finding:** The PyPI artifact previously installed as Twisted 26.4.0 was reported by `pip-audit` for CVE-2026-106454. The vulnerability concerns catastrophic regex backtracking in IMAP mailbox patterns. Debian fixed its downstream package in 26.4.0-5, but a distro patch level does not prove the PyPI wheel contains the patch.

**Current mitigation:** The official upstream 26.10.0rc1 source contains the upstream fix commit. This exact RC pin is temporary and must not be mistaken for a final stable dependency.

**Actions**
1. Verify the installed Twisted version and test that regex syntax is treated literally while IMAP `*` and `%` wildcards retain expected semantics.
2. Run `pip-audit` against the actual resolved environment and review all findings.
3. Check Daphne/ASGI startup, Django checks, and full regression with the RC.
4. Replace the RC with the first final upstream release that contains the fix as soon as available; rerun all gates.
5. If the advisory database still flags a verified patched artifact, document evidence and use only a transparent, narrow, time-limited exception after independent human security review. Never silently suppress the finding.

**Acceptance:** Final dependency is stable/reproducible, patch behavior is verified in the installed artifact, dependency audit has an evidence-backed disposition, compatibility and regression tests pass, and independent review approves.

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
- Upstream Twisted fix commit: https://github.com/twisted/twisted/commit/2f8a3c29246f4eb324690e06a9767a11dc4aec9
- Upstream RC release: https://github.com/twisted/twisted/releases/tag/twisted-26.10.0rc1
- OWASP ASVS: https://asvs.owasp.org/
- Django deployment checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

## Current disposition

The Twisted dependency mitigation is now under CI verification, but is not yet accepted as a final release fix because the pinned upstream version is a release candidate and the new workflows have not been verified. Do not merge, deploy, run production migrations, or claim that every issue is solved until all evidence and independent review are complete. This plan coordinates the work; it does not itself prove controls have passed or constitute a guarantee of complete security.
