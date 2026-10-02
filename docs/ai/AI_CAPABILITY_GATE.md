# ZooTasks AI Capability Lifecycle Gate

## Purpose
No AI feature enters production merely because a model can perform the task. Every capability must pass a documented lifecycle gate.

## Gate A — Define
Record system ID, business purpose, intended users, explicit prohibited uses, data classes, provider/model/version, application components touched, and whether output can affect a high-impact or irreversible action.

Reject the AI approach when a deterministic non-AI control is safer and sufficient.

## Gate B — Risk and architecture
Complete the threat model, data-flow diagram, trust boundaries, privacy/data-minimization review, authorization-boundary review, cost/availability limits, failure/rollback design, and human-oversight requirement.

For agentic capabilities, also define explicit tool/data/destination/action allowlists, reversibility classes, circuit breakers, inter-agent trust boundaries and resource budgets. Treat prompts, retrieved content, tool output and agent messages as untrusted input until validated.

Hard rule: AI output never grants application permissions.

The Executive AI Advisor/Orchestrator is advisory and coordinating only. It cannot override deterministic authorization or become the source of privileged authority.

## Gate C — Evaluation
Minimum suite:
- Golden functional cases.
- Invalid/malformed input cases.
- Prompt-injection/adversarial cases.
- Sensitive-data handling cases.
- Out-of-scope requests.
- Provider/API failure cases.
- Output-schema violations.
- Regression cases against the previous approved model/provider version.

The evaluation record must identify exact model/provider/version and test-data version.

## Gate D — Security and privacy
Verify provider endpoint allowlisting, credential isolation, minimum necessary data, redaction/exclusion of sensitive values, request/response limits, rate/concurrency/budget limits, safe logging, and no direct AI path to privileged financial or identity operations.

## Gate E — Human oversight
- Informational: AI may produce a suggestion for a normal application workflow.
- Moderate impact: deterministic validation and, where required by the risk assessment, human review.
- High impact / irreversible: no autonomous execution; deterministic policy gate plus authorized human approval.

For agentic systems, the approval interface must expose the actual proposed action and material parameters. An agent-generated summary is not sufficient evidence for a high-impact approval.

ZooTasks high-impact examples include wallet mutation, withdrawal state changes, permission changes, Owner authentication decisions, and irreversible financial or identity actions.

## Gate F — Release
Production release requires evidence for inventory, risk assessment, evaluation, security tests, privacy review, model/provider/version, configuration and prompt version, human oversight, monitoring, rollback/disable procedure, approval, and change history.

No evidence means no production approval.

## Gate G — Monitor and change
Monitor failures, abuse, quality drift, cost, latency, and provider errors. Re-evaluate after model/provider/configuration/prompt changes. Re-run relevant security/regression tests. Record incidents/exceptions. Maintain a tested disable/rollback path.

A materially changed model or provider is a controlled change, not an invisible dependency update.

## Agentic acquisition boundary

ZooTasks may pursue legitimate task acquisition through two controlled routes: authenticated provider/API/feed integrations and authorized business outreach when a provider does not expose an automation feed. Discovery alone does not establish authorization.

Agents must not spam, impersonate, bypass CAPTCHA or access controls, harvest credentials, or scrape restricted/private systems. Unverified sources remain quarantined until authorization, terms, security and data-handling requirements are established.

Each provider/offer integration must retain provenance including source, authorization status, region/eligibility, reward/currency, data requirements, restrictions, expiry, verification method, adapter/version and audit references.

## First candidate capability
AI-SYS-001 — Task Classification & Quality Assistance

Intended scope:
- suggest task category;
- identify missing or ambiguous task instructions;
- suggest non-binding quality checks for human/admin review.

Out of scope:
- worker claim approval/rejection;
- reward/budget/capacity changes;
- wallet or withdrawal operations;
- promotion payout decisions;
- account permission changes;
- Owner authentication or identity binding;
- autonomous external actions.

Status: Design — not approved for production.
