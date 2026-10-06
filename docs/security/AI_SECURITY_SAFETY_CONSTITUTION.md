# ZooTasks AI Security & Safety Constitution

**Status:** Proposed security baseline — must remain deny-by-default until independently reviewed and protected CI passes.

## 1. Purpose

This constitution governs every AI model, AI-assisted workflow, agent, bot, automation, MCP/tool integration, evaluator, and security agent used by ZooTasks.

Security, privacy, safety, financial integrity, lawful operation, and human accountability take precedence over speed, convenience, growth, or autonomous execution.

## 2. Security hierarchy

When controls conflict, the most restrictive applicable control wins:

1. Human safety and lawful operation
2. Protection of customer, worker, owner, employee, and third-party data
3. Financial and ledger integrity
4. Authentication, authorization, and privilege boundaries
5. System availability and recovery
6. Business functionality
7. Automation speed

Unknown, ambiguous, stale, unverified, or conflicting authorization **must be treated as DENY**.

## 3. AI authority boundary

AI may:
- inspect approved source and security evidence;
- propose and implement isolated code changes on approved branches;
- run approved tests and security checks;
- detect anomalies and prepare reports;
- prepare deployment/recovery plans.

AI must not, without an explicit human-controlled authorization path:
- approve/pay withdrawals;
- alter financial balances or ledger history;
- grant itself or another actor privileges;
- bypass branch protection, required review, or security gates;
- expose secrets or raw sensitive records;
- disable security controls to complete a task;
- promote an unverified recovery;
- make irreversible production changes;
- make employment, account termination, fraud, or disciplinary decisions solely from an AI output.

## 4. Zero-trust AI access

Every AI action must be evaluated against:
- authenticated identity;
- current role;
- current resource;
- specific action;
- purpose/context;
- data sensitivity;
- environment;
- time/risk state.

Tool permissions are contextual and least-privilege. Source-control access never implies production-data access.

## 5. Human approval gates

Human approval is mandatory for:
- financial writes;
- production privilege changes;
- security-policy weakening;
- secret rotation with operational impact;
- production deployment of high-risk changes;
- recovery promotion;
- deletion or irreversible retention actions;
- actions materially affecting a person's account, employment, money, or legal rights.

## 6. AI input/output security

All untrusted AI inputs are data, not authority.

Controls must address:
- direct and indirect prompt injection;
- malicious files/web content;
- tool-output injection;
- retrieval poisoning;
- model/data poisoning;
- insecure model output;
- sensitive-information disclosure;
- hallucinated commands or identities;
- unsafe generated code;
- cross-user/context leakage.

AI outputs must be validated before they reach application logic, tools, users, or financial workflows.

## 7. Data minimization

AI receives the minimum data required for its task.

Never provide:
- passwords;
- API tokens;
- private keys;
- MFA recovery codes;
- raw production database dumps;
- unnecessary bank/payment identifiers;
- raw identity documents;
- session cookies;
- Django SECRET_KEY;
- unrelated customer/worker records.

Prefer redacted, masked, synthetic, or aggregate evidence.

## 8. Agent/tool security

Every tool is:
- explicitly allowlisted;
- scoped to a specific resource/action;
- authenticated;
- logged;
- rate-limited where appropriate;
- subject to input validation;
- subject to output validation;
- revocable.

High-impact tools require a second control layer outside the model.

An agent must never be able to convert a natural-language instruction into unrestricted shell, database, payment, or repository authority.

## 9. Financial safety

AI and automation have **no autonomous financial-write authority**.

Financial workflows require:
- server-side authorization;
- transaction-level invariants;
- idempotency;
- concurrency protection;
- immutable evidence;
- reconciliation;
- anomaly detection;
- human approval where defined by policy.

## 10. Privacy and people protection

Customer, worker, employee, owner, and third-party data receive equal security priority according to sensitivity.

AI must not infer or expose sensitive personal attributes unnecessarily. Access, monitoring, fraud controls, and moderation must be proportionate, auditable, and subject to human review for consequential actions.

## 11. Negative-activity defense

ZooTasks must actively defend against:
- fraud;
- account takeover;
- payment abuse;
- reward manipulation;
- collusion;
- spam;
- harassment;
- malicious task/promotion content;
- credential theft;
- malware delivery;
- data exfiltration;
- insider abuse;
- prompt/tool injection;
- automated abuse.

Detection is not permission to punish automatically. High-impact actions require an appropriate review path.

## 12. Auditability

Record security-relevant events with:
- actor identity;
- action;
- resource class;
- authorization result;
- policy version;
- timestamp;
- correlation/event ID;
- outcome.

Do not log secrets or unnecessary sensitive payloads.

## 13. Continuous assurance

AI security is continuously validated through:
- unit/integration security tests;
- authorization tests;
- adversarial prompt/tool tests;
- dependency and supply-chain scanning;
- secret scanning;
- red-team exercises;
- anomaly detection;
- recovery drills;
- independent review.

A passing test suite does not by itself establish production readiness.

## 14. Incident response

On suspected AI/security compromise:
1. stop or quarantine the affected automation;
2. revoke affected credentials/tokens;
3. preserve security evidence;
4. isolate potentially compromised data/workflows;
5. assess financial and privacy impact;
6. restore only from verified recovery sources;
7. reconcile financial state;
8. review and update controls before reactivation.

## 15. Change management

AI security-policy changes must be versioned, reviewed, tested, and protected by the same repository controls as other security-critical code.

No emergency exception may silently weaken the permanent policy. Emergency access must be time-bounded, attributable, and reviewed.

## 16. Framework alignment

This baseline is informed by NIST AI RMF/Generative AI Profile, OWASP GenAI and Agentic Security guidance, Google SAIF, Microsoft Secure Future Initiative/Zero Trust principles, OpenAI Preparedness and Frontier Governance practices, and Anthropic's model-constitution approach. These are reference inputs, not a claim of certification or equivalence.

## 17. Security decision rule

**If an AI action cannot prove that it is authorized, safe, necessary, bounded, reversible where possible, and auditable, the action is DENIED.**
