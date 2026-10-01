# ZooTasks AI Governance Baseline

## Purpose

ZooTasks will treat AI as a controlled socio-technical capability, not as an unrestricted automation layer. AI features must have an identified owner, defined purpose, documented risks, measurable controls, human oversight where appropriate, and auditable evidence.

This baseline aligns the project with:
- ISO/IEC 42001:2023 — Artificial Intelligence Management System (AIMS).
- NIST AI RMF 1.0 — Govern, Map, Measure, Manage.
- ISO/IEC 23894:2023 — AI risk-management guidance.
- ISO/IEC 27001:2022 — information-security management.
- ISO/IEC 27701:2025 — privacy-information management.
- OWASP Top 10 for LLM Applications 2025 for AI application security.

Alignment is not certification. Formal certification requires an independent certification/audit process.

## AI lifecycle gate

Every AI capability must pass:

1. Identify — purpose, users, data, model/provider, owner.
2. Risk assess — security, privacy, safety, reliability, bias/fairness where relevant, legal/regulatory impact, financial impact.
3. Define controls — access, data minimization, output validation, human approval, rate/cost limits, logging, rollback.
4. Test — adversarial, functional, regression, abuse and failure-mode tests.
5. Approve — documented owner and release decision.
6. Monitor — quality, incidents, drift, cost, abuse and control effectiveness.
7. Review — periodic reassessment after material model/provider/prompt/data changes.

## Mandatory AI control principles

- No AI component may directly mutate wallet balances or financial ledger records without deterministic server-side authorization and transaction controls.
- AI output is untrusted input until validated by application code.
- Secrets, authentication credentials, payment information and unnecessary personal data must not be sent to AI providers.
- External content must be treated as potentially adversarial; prompt injection must not grant new application privileges.
- High-impact or irreversible actions require deterministic policy checks and, where defined by the risk assessment, human approval.
- Every production AI capability must have a rollback/disable mechanism.
- AI model/provider changes must be versioned and auditable.
- Security and privacy incidents must be recorded and investigated.

## Evidence required for each AI capability

- AI system/capability inventory entry.
- Intended-use and prohibited-use statement.
- Data-flow and data-classification record.
- AI risk assessment and treatment plan.
- Model/provider/version record.
- Evaluation dataset and evaluation results.
- Security test results, including prompt-injection testing where applicable.
- Human-oversight design.
- Monitoring metrics and alert thresholds.
- Incident/exception record.
- Release approval and change history.

## Certification position

ZooTasks must not claim "ISO/IEC 42001 certified", "ISO/IEC 27001 certified", or equivalent until a competent independent certification body has completed the applicable conformity assessment and issued certification.
