# ZooTasks Bootstrap Operations & Safe Automation Plan

Status: research/design baseline
Target bootstrap budget: USD 100-200
Principle: security and deterministic financial controls take priority over AI autonomy.

## 1. Bootstrap objective

Run the first cloud production-like environment continuously without making the platform dependent on the developer's phone or Termux session.

The initial budget is an operating envelope, not a promise of fixed spend. Actual usage, taxes, domains, email, AI inference and provider pricing must be measured before activation.

## 2. Recommended architecture

Internet
→ DNS/CDN/WAF
→ single application VM
→ Django + Gunicorn/Daphne
→ PostgreSQL
→ Redis/Celery
→ isolated worker processes
→ monitoring/logging
→ encrypted backups

Financial ledger, withdrawal approval/payment, promotion payout, permissions and Owner authentication remain deterministic application controls.

AI is a constrained automation layer behind:
Data Boundary → Agent Identity → Capability Budget → Tool Permission → AI Gateway → Safety Firewall → Evidence.

No agent receives a human/admin credential.

## 3. Cost-control strategy

Start with one modest cloud VM and avoid unnecessary managed services.

A current DigitalOcean Basic 1 GiB Droplet is listed at $6/month; 2 GiB is $12/month. AWS Lightsail lists Linux/Unix bundles starting at $5/month and a 1 GiB bundle at $7/month. AWS also currently advertises up to $200 in Free Tier credits for eligible new customers. These are reference prices only; eligibility, tax, region and actual usage must be verified before purchase.

Use managed Redis only if operational risk justifies the additional cost. Upstash currently has a free tier and pay-as-you-go pricing, while fixed plans start at $10/month.

## 4. Initial USD 100-200 envelope

Illustrative allocation:

- Compute + storage: $40-70
- Backups/snapshots/object storage: $10-25
- Domain/DNS/email/transactional messaging: $10-30
- Monitoring/security services: $0-20
- AI inference experimentation: $20-50
- Emergency reserve: $20-40

Do not spend the full envelope automatically. Every paid component requires a measurable need, a usage limit and a disable path.

## 5. Safe automation rules

1. Automation defaults to read-only.
2. Every agent has a stable non-human identity.
3. Every capability has an explicit data class.
4. Every tool requires explicit allowlisting.
5. Tool calls have deterministic budgets.
6. External side effects are denied by default.
7. Financial mutations never originate from AI.
8. Secrets never enter prompts, evidence receipts or ordinary logs.
9. Production AI remains disabled until evaluation and approval gates pass.
10. Every automated workflow has an emergency kill switch.
11. Scheduled jobs must be idempotent and bounded.
12. Cost-sensitive providers require quotas/alerts before activation.

## 6. Board-level research program

The project should maintain a rolling research board covering:

- secure agent identity and authorization
- zero-trust tool execution
- agent provenance and non-repudiation
- prompt-injection and indirect-injection resistance
- marketplace trust and reputation mechanisms
- human escalation and uncertainty handling
- AI evaluation and evidence standards
- cloud cost optimization
- Bangladesh compliance and international standards
- novel ZooTasks intellectual-property opportunities

Research output should become one of four things: architecture change, experiment, article/evidence artifact, or rejected idea with a documented reason.

## 7. First unique product hypothesis

Proof-Carrying Task:

A completed task can carry a compact evidence chain showing the task context, permitted agent identity, allowed data class, capability policy, verification decision and evidence receipt—without exposing private task data.

This should remain a research/prototype concept until adversarial testing demonstrates that the evidence chain itself does not become a privacy or security leak.

## 8. Deployment gates

Bootstrap cloud deployment is blocked until:

- Security Gate is green.
- AI evaluation is green.
- backup/restore test is demonstrated.
- secrets are externalized.
- monitoring and alerting exist.
- rate limits and abuse controls exist.
- financial integrity tests are green.
- production AI approval remains explicit and separately auditable.

## 9. Operational philosophy

Spend money on reliability and security first, inference second.

Prefer simple infrastructure with strong isolation over a large collection of managed services. Scale only after measured workload justifies it.

NIST's 2026 agent-identity work emphasizes distinct agent identity, authentication, least-privilege authorization, auditing/non-repudiation and prompt-injection mitigation. ZooTasks adopts those principles while adding deterministic financial separation and data minimization.
