# ZooTasks Innovation & Revenue Research Board — Batch 01

Status: research/design only
Date: 2026-10-02
Security posture: no production AI activation; no financial-control delegation.

## Objective

Research marketplace, crowdsourcing, AI-training, reputation, quality-control, and agent-security patterns before introducing new ZooTasks earning or revenue features.

## Verified external signals

1. Upwork — AI-assisted talent discovery and screening are being integrated into the marketplace. AI summaries are positioned as assistance over profiles, skills, work history, and feedback. This supports a ZooTasks concept of AI-assisted task discovery without giving AI financial authority.
2. Fiverr — service marketplace supports hundreds of categories, including AI services, graphics/design, automation, and data. Its workflow separates service delivery/review from payment release.
3. Amazon Mechanical Turk — uses self-contained HITs, worker qualifications, approval before earnings become available, and API/batch task creation. Its pricing also separates worker reward from marketplace fee.
4. Prolific — has an AI-tasker participant group with qualification assessment and access to specialized AI evaluation/training studies.
5. NIST — current agent-security work emphasizes agent identity, authentication, authorization, least privilege, auditing/non-repudiation, and prompt-injection mitigation.

## Research targets for the broader 20–50 source board

Upwork, Fiverr, Amazon Mechanical Turk, Prolific, Toloka, Clickworker, Appen, TELUS Digital, OneForma, Remotasks, Microworkers, RapidWorkers, Freelancer, PeoplePerHour, Guru, Contra, Toptal, Outlier, DataAnnotation, Scale AI, Surge AI, Labelbox, NIST, NIST NCCoE, OWASP, ISO/IEC AI standards resources.

These targets are a research queue, not claims that every item has been verified in this batch.

## Candidate ZooTasks innovation hypotheses

### R01 — Proof-Carrying Task

A completed task can carry a privacy-minimized evidence chain:
task version → permitted agent identity → allowed data class → deterministic checks → human/worker verification → evidence receipt.

Potential value:
- stronger client confidence
- better dispute investigation
- premium task classes
- reusable quality evidence

Security boundary:
- evidence must never contain prompts, secrets, payment credentials, raw private data, or unrestricted model output.

### R02 — Quality Ladder

Workers can unlock higher-value task classes through deterministic qualification tests and measured quality history.

Potential value:
- better task matching
- higher-value earning paths
- reduced client quality risk

Security boundary:
- qualification changes must be deterministic and auditable; AI may recommend, not silently grant financial privileges.

### R03 — Verification Bounty

For selected tasks, a second worker can perform independent verification and earn a bounded verification reward.

Potential value:
- creates a new earning category
- increases task reliability
- distributes quality control across the marketplace

Security boundary:
- reward calculation and payout remain deterministic.
- anti-collusion, duplicate-submission, and Sybil controls are required.

### R04 — AI Evaluation Tasks

Create a task family for human evaluation of AI outputs: factuality, instruction following, safety, localization, and preference comparison.

Potential value:
- new global earning category
- client-side AI evaluation demand
- direct alignment with emerging AI-task markets

Security boundary:
- no sensitive client data by default.
- strict content/data classification and isolation.
- AI output is untrusted input, not authorization.

### R05 — Research-to-Task Pipeline

A client submits a research objective; the system decomposes it into bounded human tasks. AI may suggest decomposition, while deterministic policy validates task scope, reward limits, and data class.

Potential value:
- higher-value research workflows
- scalable task creation

Security boundary:
- no autonomous publishing or financial commitment by AI.

## Revenue experiments to evaluate

1. Marketplace service fee.
2. Client-funded verification tier.
3. Premium quality/verification package.
4. Enterprise task orchestration subscription.
5. API access for approved clients.
6. Verified evidence/export package.
7. Specialized AI-evaluation task programs.
8. Team/agency workflow features.
9. Priority task distribution.
10. Private task pools with controlled access.

No experiment is approved for implementation yet. Each requires unit economics, Bangladesh/international compliance review, fraud analysis, and financial-integrity tests.

## Security gates for every future earning feature

- AI cannot mutate wallet/ledger balances.
- AI cannot approve/pay withdrawals.
- AI cannot execute promotion payouts.
- AI cannot change permissions or Owner identity/authentication.
- Data minimization and explicit data-class allowlists.
- Least-privilege agent identity.
- Bounded tool/action budget.
- No external side effects by default.
- Immutable/cryptographically verifiable evidence where appropriate.
- Human escalation for uncertain/high-impact decisions.
- Kill switch and rate limits.
- CI adversarial evaluation before production exposure.

## Next research cycle

Expand the verified source set toward 20–50 relevant sources, capture concrete feature patterns, pricing/revenue mechanisms, trust/safety controls, and worker incentives, then convert only evidence-supported ideas into ZooTasks design specifications.
