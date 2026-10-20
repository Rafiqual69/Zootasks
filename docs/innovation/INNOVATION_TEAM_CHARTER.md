# ZooTasks Innovation & Reliability Team Charter

**Status:** Proposed operating charter; draft for review  
**Owner:** ZooTasks project owner  
**Effective date:** 2026-10-21  
**Scope:** Product discovery, secure engineering, financial integrity, quality, operations, and evidence-based release decisions.

## 1. Mission

Build ZooTasks into a reliable, privacy-preserving task marketplace by shipping small, measurable improvements without destabilizing existing functionality or risking user funds, records, credentials, or production availability.

This charter defines working roles for a virtual/AI-assisted team. It does **not** claim that human employees or GitHub organization teams have been created or invited.

## 2. Working roles

| Role | Primary responsibility | Required output |
|---|---|---|
| Product & Innovation Lead | Prioritize user problems, validate demand, define outcomes | Problem statement, success metric, staged experiment |
| Security & Privacy Lead | Threat modeling, least privilege, data minimization, dependency review | Threat/risk notes, security test evidence |
| Backend & Architecture Lead | Django design, backward compatibility, maintainable implementation | Small code change, migration plan where applicable |
| Financial Integrity Lead | Protect wallet ledger, rewards, promotion budgets, withdrawals, idempotency and concurrency | Invariant checklist and regression evidence |
| QA & Verification Lead | Reproduce defects and validate exact commit SHA | Automated test report, negative and regression tests |
| DevOps & Reliability Lead | Build/deploy configuration, backups, restore drills, monitoring and rollback | Rehearsal evidence, runbook, release/rollback plan |
| Product Research & Bangladesh Compliance Lead | Customer discovery, competitor evidence, Bangladesh legal/payment obligations | Source-linked research; unresolved legal questions clearly marked |
| AI Governance & Release Lead | Keep AI advisory, trace decisions, enforce release gates | Decision log and explicit go/no-go recommendation |

One person or AI assistant may help multiple roles, but role separation in reviews must be preserved. AI-generated changes are proposals until tests and appropriate human review support them.

## 3. Decision rights and safety boundaries

### AI may do autonomously
- Read repository files, workflow results, dependency manifests, and documentation.
- Prepare issue/PR drafts, documentation, test plans, threat models, and reversible branch-level changes.
- Run or request non-production automated checks where authorized.
- Report uncertainty, evidence, regressions, and next safe steps.

### Human approval is required before
- Merging a PR that changes security-sensitive, financial, authentication, migration, or deployment behavior.
- Running migrations against any production or production-derived database.
- Deploying, changing production environment variables/secrets, rotating credentials, or modifying access policies.
- Changing wallet/reward/payout rules, reconciling historical balances, deleting records, or initiating payments.
- Enabling a new payment provider, external AI action, or privileged automation.

Never print, commit, or place secrets/PII/raw financial records in issues, PRs, logs, or test fixtures. Use synthetic data and disposable environments.

## 4. Current evidence-led priority queue

1. **P0 — Restore trustworthy CI/release gates.** Resolve the missing tasks.0004_protect_claim_history migration dependency on main through a reviewed migration-lineage change. Do not fake migrations or silently rewrite migration history.
2. **P0 — Resolve the dependency-audit blocker.** Validate the draft proposal to remove unused Daphne/Twisted only after confirming no ASGI/WebSocket requirement exists in the actual deployment. Do not suppress the vulnerability finding or weaken the audit.
3. **P1 — Financial state-machine assurance.** Test approval/rejection replay, one-time ledger credit, promotion reservation release, last-slot concurrency, and historical-record preservation.
4. **P1 — Schema-drift and recovery rehearsal.** Use a fresh database and disposable legacy copy; verify backup isolation, restore integrity, rollback plan, and read-only schema audit.
5. **P1 — Deployment reproducibility.** Confirm the Docker build context matches the repository layout and exercise the deployment candidate in staging.
6. **P2 — Privacy and account security.** Review authentication/session controls, Owner privilege boundaries, secret handling, logging, and data retention.
7. **P2 — Product experiments.** Validate worker and advertiser needs before building new features; define measurable outcomes and avoid unsupported earnings/profit claims.

Priority labels are operational triage, not a claim that each issue has been independently audited in full.

## 5. Definition of done

A change is not complete until:
- Scope and risk are documented.
- Tests cover expected behavior, failure paths, replay/idempotency, and relevant authorization boundaries.
- Security, dependency, migration-drift, and financial CI gates pass on the exact proposed commit SHA.
- Any schema change has fresh-database and disposable legacy-copy rehearsal evidence plus a rollback/restore plan.
- No secrets, PII, or real financial records are exposed in test output.
- A reviewer independent of the implementation approves high-risk changes.
- Documentation and operational runbooks are updated.
- Production changes are separately authorized and performed through the approved release process.

If a gate fails or its evidence is unavailable, mark the release **BLOCKED** and report the precise blocker. Never bypass a failing check merely to make CI green.

## 6. Operating cadence

- **Every change:** small branch/PR, exact-SHA CI, explicit risk and rollback notes.
- **Daily work session:** review P0 blockers first; then one measurable P1/P2 item.
- **Weekly:** review incidents, dependency advisories, open security findings, backup/restore evidence, product metrics, and stale draft PRs.
- **Release review:** Security + Financial Integrity + QA/DevOps sign-off; project owner authorizes production action.
- **Decision log:** record decision, evidence links, alternatives, unresolved risks, reviewer, and date. Never record secrets or user-level financial data.

## 7. Initial acceptance checklist

- [ ] Main-branch migration graph is valid and migration drift check passes.
- [ ] Dependency audit passes without a CVE ignore/suppression.
- [ ] Security Gate passes on the exact release candidate SHA.
- [ ] Security Review passes on the exact release candidate SHA.
- [ ] PostgreSQL Financial Verification passes on the exact release candidate SHA.
- [ ] Financial idempotency/concurrency regression evidence is current.
- [ ] Fresh database and disposable legacy-copy migration rehearsals pass.
- [ ] Backup and restore have been demonstrated, not merely documented.
- [ ] Deployment build/startup is verified in staging.
- [ ] Independent review and project-owner release approval are recorded.

Until all applicable items are satisfied, ZooTasks must not be described as production-ready.
