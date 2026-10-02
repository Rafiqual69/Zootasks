# ZooTasks AI Certification Evidence Index

This index is the audit trail for AI governance evidence.

## Governance

- AI policy: docs/ai/AI_GOVERNANCE.md
- Risk register: docs/ai/AI_RISK_REGISTER.md
- System inventory: docs/ai/AI_SYSTEM_INVENTORY.md
- AI threat model: docs/ai/AI_THREAT_MODEL.md
- Capability lifecycle gate: docs/ai/AI_CAPABILITY_GATE.md
- Executive/agent architecture: docs/ai/AI_EXECUTIVE_AGENT_ARCHITECTURE.md
- Agent capability contract: docs/ai/AI_AGENT_CAPABILITY_CONTRACT.md
- Deterministic agent capability gate: backend/core/ai_agent_capability_gate.py
- Agent capability security tests: backend/core/ai_agent_capability_gate_tests.py
- Provider registry/offer pipeline: docs/ai/AI_PROVIDER_REGISTRY_AND_OFFER_PIPELINE.md
- Canonical provider offer schema: docs/ai/AI_PROVIDER_OFFER_SCHEMA.json
- Deterministic provider offer validator: backend/core/ai_provider_offer.py
- Provider offer security tests: backend/core/ai_provider_offer_tests.py

## Evidence classes

### E1 — Governance
Policies, roles, scope, objectives, approvals and review records.

### E2 — Risk
AI risk assessments, treatment plans, residual-risk decisions and review dates.

### Current evidence mapping

- E1 Governance: AI governance policy + capability lifecycle gate
- E2 Risk: AI risk register + AI threat model
- E3 Technical: threat-model trust boundaries + Executive/agent architecture + provider/offer pipeline + later implementation/data-flow evidence
- E4 Evaluation: AI-SYS-001 deterministic evaluation + agent capability security tests + provider offer normalization/security tests are implemented; production evaluation/approval remains pending
- E5 Operations: not yet complete; monitoring/rollback evidence required before production approval; agent resource budgets/circuit-breakers and provider sync/disable evidence required for agentic/provider capabilities
- E6 Privacy: not yet complete; provider/data-retention review required before production approval

### E3 — Technical
Architecture, data-flow diagrams, model/provider configuration, access control and isolation.

### E4 — Evaluation
Accuracy/quality, robustness, security, fairness where applicable, regression and adversarial test results.

### E5 — Operations
Monitoring, incident response, rollback, provider/model changes, availability and cost controls.

### E6 — Privacy
Data inventory, purpose, retention, data-subject controls, provider processing and transfer assessment.

## Evidence integrity

Evidence should be timestamped, attributable to an accountable actor/system, protected from unauthorized modification, and linked to the exact software/model/configuration version it describes.

## Certification statement

This repository contains preparation and implementation evidence only. It is not itself a certification certificate or conformity assessment.
