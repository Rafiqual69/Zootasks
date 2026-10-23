# ZooTasks Security Board

**Status:** Active governance proposal and automated release gate; not a claim of complete security.  
**Repository:** Rafiqual69/Zootasks  
**Scope:** Django application, identity and access control, wallet/task/promotion/withdrawal records, database migrations, dependencies, CI/CD, backups, secrets, and incident response.

## 1. Board structure (role-based)

These are accountable review roles, not claims that named human specialists have been hired or appointed. Until real reviewers are assigned, automated checks can assist but cannot replace independent human approval.

1. **Security Chair / Release Gatekeeper** — maintains risk register, ensures findings have owners and evidence, blocks release on unresolved critical/high issues, and records exceptions.
2. **Application Security Reviewer** — reviews authentication, authorization, CSRF, session/cookie policy, input validation, file handling, admin permissions, and data exposure.
3. **Financial Integrity Reviewer** — independently reviews wallet ledger invariants, reward idempotency, withdrawal state transitions, race conditions, reconciliation, and immutable/auditable history.
4. **Database & Recovery Reviewer** — checks migration graph/state parity, constraints, backup exclusion of secrets, backup permissions, and restore drills.
5. **Supply-chain & CI Reviewer** — checks dependency advisories, version pins, workflow permissions, action pinning, secret handling/masking, and artifact/log exposure.
6. **Privacy & Incident Response Reviewer** — checks data minimization, logging redaction, retention, incident containment, credential rotation, and notification obligations.
7. **Independent Release Approver** — verifies evidence from the above areas and must not approve their own change alone.

## 2. Decision rules

- Default-deny: unresolved critical/high security findings, failing tests, migration drift, financial invariant failures, exposed secrets, or unreviewed destructive migrations block merge/release.
- Require green Security Review, Security Gate, PostgreSQL Financial Verification, dependency audit, backup isolation smoke test, and relevant targeted tests.
- Require a human reviewer independent of the author for security-sensitive changes. CI success is evidence, not a substitute for code review.
- Do not run production migrations, change production settings, or deploy from this PR. Production changes require an explicit change plan, verified backup and restore evidence, rollback plan, and human authorization.
- Never use real user data, production credentials, or production payment integrations in CI.
- Do not suppress or ignore a dependency finding merely to turn CI green. Record package, advisory, affected range, installed version, patched version, reachability/exposure analysis, and test evidence.

## 3. Risk register (initial)

| ID | Risk | Current control / evidence | Required closure evidence | Status |
|---|---|---|---|---|
| SB-01 | CI secret value may appear in logs/environment summaries | Per-run random key and explicit workflow masking added to three workflows; latest Security Gate log shows `SECRET_KEY: ***` and bounded scan found no unmasked key-shaped value | Inspect all current workflow logs/artifacts and relevant historical logs before release | Partial verification; scope-limited |
| SB-02 | Pillow dependency audit findings | Pillow 13.0.0 selected; latest dependency audit passed | Confirm relevant upload/image regression coverage and independent review | CI verified; review pending |
| SB-03 | Twisted advisory CVE-2026-106454 | Upstream fix commit and 26.10.0rc1 implementation inspected; installed-artifact wildcard test and pip-audit passed on latest validated commit | Replace pre-release pin with verified final upstream release and rerun all gates; review runtime compatibility independently | Mitigation tested; final-release blocker open |
| SB-04 | Task claim history could be cascade-deleted | TaskClaim task/worker relations changed to PROTECT; migration drift and PostgreSQL regression passed on latest validated commit | Independent review and deletion/history regression evidence | CI verified; review pending |
| SB-05 | Wallet/withdrawal concurrency and ledger correctness | Existing constraints and locked admin transitions inspected; this is not a full audit | Independent tests for concurrent approval/payment, duplicate requests, idempotency, rollback, reconciliation, and ledger balance invariants | Open |
| SB-06 | Backup may include sensitive files or fail to restore | Backup smoke test passed for exclusions and file mode on latest validated commit | Isolated synthetic restore drill and recovery evidence; never test restore over production | Smoke verified; restore drill open |
| SB-07 | Production security settings/secrets may differ from CI | Deployment checks exist | Documented environment review, secret rotation where warranted, HTTPS/proxy/cookie/HSTS verification, least privilege | Open |
| SB-08 | Private data leakage through logs/errors/exports | Secret masking added to CI key generation | Review app logs, admin exports, exception paths, bot logs and backup output using synthetic secrets | Open |

## 4. Research and verification basis

- **OWASP ASVS 5.0.0** is the baseline for application-security verification; requirements should be tracked by versioned identifiers as controls are implemented.
- **NVD CVE-2026-106454** reports Twisted affected through 25.5.0, CVSS 3.1 medium (4.3), involving inefficient regular-expression complexity in a network-facing component. Reachability must be assessed, but the finding must not be dismissed without evidence.
- **Official Pillow release notes** identify 13.0.0 as released on 2026-10-16 and advise using the latest release because fixes are not expected to be backported to older versions.
- Dependency versions and advisory status must be re-checked at CI time; web research is a snapshot, not a guarantee.

References:
- OWASP ASVS: https://asvs.owasp.org/
- NVD CVE-2026-106454: https://nvd.nist.gov/vuln/detail/CVE-2026-106454
- Twisted on PyPI: https://pypi.org/project/Twisted/
- Pillow release notes: https://pillow.readthedocs.io/en/stable/releasenotes/

## 5. Automated operating loop

1. Fetch latest repository and PR checks.
2. Review new advisories and installed dependency versions.
3. Reproduce failures in isolated CI; avoid production access.
4. Make the smallest reviewable branch change with focused tests.
5. Run static checks, security policy tests, full regression, migration drift, PostgreSQL migrations and financial tests, dependency audit, and backup smoke test.
6. Inspect logs and artifacts for secrets/PII.
7. Require independent human review; keep PR draft or blocked while any required evidence is missing.
8. Record decision, remaining risk, and rollback plan.

## 6. Explicit limitations

No process can guarantee “complete security.” This board reduces risk through defense in depth, independent review, verifiable tests, and conservative release gates. No real board membership or human approval is implied until named people are assigned in the repository. This document does not authorize production changes.
