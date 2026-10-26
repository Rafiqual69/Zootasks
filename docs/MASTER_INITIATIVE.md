# ZooTasks Master Initiative — Product, Security & Reliability Roadmap

**Status:** Active plan; not a certification or a claim that the platform is production-ready.  
**Umbrella tracker:** https://github.com/Rafiqual69/Zootasks/issues/70  
**Default timezone for operations:** Asia/Dhaka  
**Current repository baseline:** `main` at `aa548d148d36df0c8ed2af3d58d8e1f0d8e38512` (verified 2026-10-26)

## Product objective

Evolve the existing ZooTasks Django application into a professional, accessible task marketplace and a welcoming community knowledge/idea hub. People should be able to discover useful information, share new ideas, learn from one another, and—where moderation and safety controls permit—turn approved ideas into tasks or projects. Improve the current product rather than rebuilding it from zero.

## Product principles

- **Open participation, safe by design:** make it easy to read and contribute, with clear account controls, anti-spam measures, reporting and moderation.
- **Ideas with useful structure:** allow a title, description, topic/category, tags, references/sources, expected benefit, and optional next steps; support drafts and revision history.
- **Findability:** plan for search, topic pages, sorting, and accessible filters; do not publish fake activity, fabricated statistics, or unverified recommendations.
- **Trust and attribution:** show contribution dates and authorship transparently, respect privacy, provide report/correction paths, and define content ownership/licensing before public launch.
- **Inclusive UX:** mobile-first, plain language, Bengali and English readiness, keyboard access, visible focus, semantic structure, and WCAG 2.2 AA-oriented testing.
- **No unsafe monetization claims:** task rewards, eligibility, moderation, and payout terms must be clear and accurate; never guarantee earnings.

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
| Community integrity | Idea quality, moderation, abuse reporting, privacy, attribution | Published rules, tested report/moderation flow, audit trail |
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

### P2A — Community knowledge and idea hub
- Inspect existing Django apps, routes, models, authentication and tests before deciding whether to extend an app or add a dedicated ideas app.
- Start with a reviewed, minimal data model: idea title, body, category/topic, tags, author, timestamps, status, and optional references; define editing, deletion, and retention rules.
- Build accessible browse/detail/create/edit flows with draft/publish states, server-side validation, CSRF protection, rate limits, spam controls, and object-level permissions.
- Add abuse reporting, moderation queues, clear community guidelines, and an audit trail for moderation actions before open public posting.
- Plan search and sorting with safe query handling; add comments/voting only after abuse, privacy, and manipulation risks are reviewed.
- Consider Bengali/English UI and content support, low-bandwidth/mobile performance, and simple explanations for first-time contributors.
- Decide licensing, copyright/attribution, privacy notice, prohibited content, retention and appeal process before enabling public contributions.
- Never expose private drafts, user email, internal moderation notes, security logs, or unpublished personal information in public pages/API responses.
- Keep community content separate from wallet/reward records. Any conversion of an idea into a paid task must use existing reviewed reward and approval paths—not direct client-side balance changes.

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
- PR #71's current Security Gate, PostgreSQL Financial Verification, and Security Review runs failed at the migration graph/full regression stage because `tasks.0005_alter_taskclaim_task` references the missing `tasks.0004_protect_claim_history` migration. This is a real blocker, not a UI-specific test failure; fix the migration chain before interpreting later test results.

## Release definition of done

1. Actual merge candidate has a consistent Django migration graph and no unexpected model/migration drift.
2. Security, financial, and regression tests pass on supported databases; CI logs are reviewed for secret/PII disclosure.
3. Migration preflight is clean; no unreviewed data rewrite, wallet adjustment, payout, or production migration.
4. Dependency risk has a documented resolution/mitigation and review.
5. Backup restore and rollback steps have been exercised.
6. Responsive/accessibility findings are recorded; no unverified compliance claims.
7. Independent human security and financial reviews are recorded.
8. Community posting/moderation, privacy, attribution, and abuse-reporting behavior are tested before open contribution is enabled.
9. Explicit release approval is given; no deployment occurs merely because a PR exists.
