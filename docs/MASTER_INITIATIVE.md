# ZooTasks Master Initiative — Product, Security & Reliability Roadmap

**Status:** Active plan; not a certification or a claim that the platform is production-ready.  
**Umbrella tracker:** https://github.com/Rafiqual69/Zootasks/issues/70  
**Default timezone for operations:** Asia/Dhaka  
**Current repository baseline:** `main` at `aa548d148d36df0c8ed2af3d58d8e1f0d8e38512` (verified 2026-10-26)

## Product objective

Evolve the existing ZooTasks Django application into a professional, accessible task marketplace while preserving existing functionality and all financial/claim history. Improve the current product rather than rebuilding it from zero.

## Governance model

These are review roles, not claims that human reviewers have been appointed. Automated checks cannot replace independent human review.

| Role | Review responsibility | Release evidence |
|---|---|---|
| Security gatekeeper | Risk register, severity, exceptions, release gates | No unresolved critical/high release blockers |
| Application security | Authentication, authorization, CSRF, session/cookie, input/output handling | Focused tests and review notes |
| Financial integrity | Wallet ledger, reward idempotency, withdrawal lifecycle, concurrency | DB-backed tests, reconciliation, safe migration preflight |
| Data protection | PII minimization, secrets, logs, artifacts, retention | No sensitive values in source/logs/artifacts or client responses |
| Database & recovery | Migration graph, schema drift, backup and restore | Consistent graph and a documented restore drill |
| Product & accessibility | Mobile usability, navigation, truthful copy, forms | Responsive checks and WCAG 2.2 AA-oriented audit |
| Operations | Deployment configuration, health, alerting, incident response | Rollback and monitoring evidence |

## Priority order

### P0 — Stop unsafe releases
- Keep PR #66 and #69 Draft/unmerged until their exact merge candidates pass required CI and independent review is recorded.
- Fix the missing `tasks.0004_protect_claim_history` migration graph problem on the actual workflow merge ref; do not treat stale or unrelated runs as evidence.
- Track Twisted CVE-2026-106454 in issue #67 and verify the stable upstream status before choosing an upgrade/mitigation.
- Review branch protection: GitHub API reported `main` protection disabled on 2026-10-26. Confirm settings and access impacts before changing policy.
- Never print or commit secret values; mask them in CI and inspect log/artifact output for disclosure.

### P1 — Application and financial integrity
- Test object-level authorization for tasks, promotions, wallet and withdrawal records.
- Preserve append-only financial history; never silently repair migration preflight data.
- Test duplicate submission/idempotency, race conditions, permission boundaries, valid status transitions, and database constraints.
- Separate withdrawal review/approval/payment permissions and audit transitions.
- Minimize wallet and admin template context to fields actually rendered.

### P2 — Professional public website
- Mobile-first layout with clear task, promotion, onboarding, sign-in and dashboard navigation.
- Use accurate product language. Do not label static examples as live activity or promise a specific earning outcome.
- Add privacy, terms, contact/support, eligibility and reward/withdrawal policy pages only with accurate, approved content.
- Keyboard navigation, visible focus, semantic headings/landmarks, form labels/errors, contrast and reduced-motion support.
- Test on narrow screens and common browsers before release.

### P3 — Reliability and operations
- Verify environment-specific production settings, HTTPS, secure cookies, HSTS, host validation and trusted proxy configuration against the actual host.
- Define database ownership, backup frequency, encrypted storage, access controls, retention and restore drill.
- Add health checks and privacy-safe operational monitoring; avoid logging tokens, credentials, bank details or unnecessary PII.
- Document incident response, rollback and deployment ownership before 24/7 claims.

## External baseline references

- OWASP ASVS 5.0.0: https://asvs.owasp.org/
- NIST SP 800-218 SSDF: https://csrc.nist.gov/pubs/sp/800/218/final
- Django deployment checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- WCAG 2.2 Recommendation: https://www.w3.org/TR/WCAG22/

Use stable published standards for release criteria. A checklist or code change is not proof of compliance; record test evidence and reviewer sign-off.

## Current known blockers (2026-10-26)

- PR #66: open/Draft; ephemeral CI secret and TaskClaim history migration changes require current successful gates and human review.
- PR #69: open/Draft, stacked on PR #66; last recorded CI attempt failed before validating withdrawal constraints because the workflow merge ref could not resolve `tasks.0004_protect_claim_history`.
- Issue #67: open; Twisted CVE-2026-106454 remains a release blocker until a stable patched release or verified mitigation is established.
- Main branch protection: API reports disabled; review policy and enable intentionally after validating contributor access and required-check names.

## Release definition of done

1. Actual merge candidate has a consistent Django migration graph and no unexpected model/migration drift.
2. Security, financial, and regression tests pass on supported databases; CI logs are reviewed for secret/PII disclosure.
3. Migration preflight is clean; no unreviewed data rewrite, wallet adjustment, payout, or production migration.
4. Dependency risk has a documented resolution/mitigation and review.
5. Backup restore and rollback steps have been exercised.
6. Responsive/accessibility findings are recorded; no unverified compliance claims.
7. Independent human security and financial reviews are recorded.
8. Explicit release approval is given; no deployment occurs merely because a PR exists.
