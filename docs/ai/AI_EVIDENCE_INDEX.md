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
- Deterministic AI action taxonomy: backend/core/ai_action_taxonomy.py + backend/core/ai_action_taxonomy_tests.py
- Adversarial regression memory: backend/core/ai_adversarial_regression.py + backend/core/ai_adversarial_regression_tests.py
- Agent capability security tests: backend/core/ai_agent_capability_gate_tests.py
- Provider registry/offer pipeline: docs/ai/AI_PROVIDER_REGISTRY_AND_OFFER_PIPELINE.md
- Canonical provider offer schema: docs/ai/AI_PROVIDER_OFFER_SCHEMA.json
- Deterministic provider offer validator: backend/core/ai_provider_offer.py
- Provider offer security tests: backend/core/ai_provider_offer_tests.py
- Deterministic provider change detection: backend/core/ai_provider_change_detection.py
- Provider change detection security tests: backend/core/ai_provider_change_detection_tests.py
- Provider ingress quarantine: docs/ai/AI_PROVIDER_INGRESS_QUARANTINE.md
- Deterministic provider ingress boundary: backend/core/ai_provider_ingress.py
- Provider ingress security tests: backend/core/ai_provider_ingress_tests.py
- Deterministic worker eligibility gate: backend/core/ai_worker_eligibility.py
- Worker eligibility security tests: backend/core/ai_worker_eligibility_tests.py
- Autonomous innovation model: docs/ai/AI_AUTONOMOUS_INNOVATION_MODEL.md
- Deterministic innovation gate/tests: backend/core/ai_innovation_loop.py + backend/core/ai_innovation_loop_tests.py
- Innovation Genome & Discovery Fabric: docs/ai/AI_INNOVATION_GENOME_AND_DISCOVERY_FABRIC.md
- Deterministic innovation genome/tests: backend/core/ai_innovation_genome.py + backend/core/ai_innovation_genome_tests.py
- Mechanism catalog + provenance fabric: backend/core/ai_mechanism_catalog.py + backend/core/ai_provenance_queue.py + docs/ai/AI_MECHANISM_CATALOG_AND_PROVENANCE_FABRIC.md
- Protocol-neutral Agent Card + scoped delegation: backend/core/ai_agent_card.py + backend/core/ai_delegation_token.py + docs/ai/AI_AGENT_CARD_AND_DELEGATION_BOUNDARY.md
- Source attestation + privacy/retention gate: backend/core/ai_source_attestation.py + backend/core/ai_privacy_gate.py + docs/ai/AI_SOURCE_ATTESTATION_AND_PRIVACY_GATE.md
- Trust graph + non-escalating delegation chain: backend/core/ai_delegation_chain.py + docs/ai/AI_TRUST_GRAPH_AND_DELEGATION_CHAIN.md
- Tamper-evident AI audit ledger: backend/core/ai_audit_ledger.py + docs/ai/AI_TAMPER_EVIDENT_AUDIT_LEDGER.md
- Policy decision evidence bundle: backend/core/ai_policy_evidence_bundle.py + docs/ai/AI_POLICY_DECISION_EVIDENCE_BUNDLE.md
- Release TEVV gate: backend/core/ai_release_tevv_gate.py + docs/ai/AI_RELEASE_TEVV_GATE.md
- Runtime Trust Sentinel: backend/core/ai_runtime_monitor.py + backend/core/ai_runtime_monitor_tests.py + docs/ai/AI_RUNTIME_MONITORING_AND_ROLLBACK_GATE.md
- Incident response + safe rollback state machine: backend/core/ai_incident_response.py + backend/core/ai_incident_response_tests.py + docs/ai/AI_INCIDENT_RESPONSE_AND_SAFE_ROLLBACK.md
- Incident evidence binding: backend/core/ai_incident_evidence_binding.py
- Incident evidence binding hardening: SHA-256-format validation for runtime decision digests + regression test
- Runtime decision context binding: incident evidence now verifies the decision digest against the exact system/release context before recovery evidence can be trusted

## Evidence classes

### E1 — Governance
Policies, roles, scope, objectives, approvals and review records.

### E2 — Risk
AI risk assessments, treatment plans, residual-risk decisions and review dates.

### Current evidence mapping

- E1 Governance: AI governance policy + capability lifecycle gate
- E2 Risk: AI risk register + AI threat model
- E3 Technical: threat-model trust boundaries + Executive/agent architecture + provider/offer pipeline + ingress quarantine + worker eligibility boundary + autonomous innovation boundary
- E4 Evaluation: deterministic capability/action-taxonomy tests, adversarial regression vectors, AI-SYS-001 evaluation, agent capability security tests, provider offer normalization/security tests, provider change-detection tests, provider ingress tests, worker eligibility tests, innovation gate tests, and innovation genome tests are implemented; model/provider production evaluation and approval remain pending
- E5 Operations: deterministic runtime-monitor, incident-response, rollback-state, capability-budget and provider quarantine controls are implemented and regression-tested; live operational evidence and an approved production monitoring/incident run remain required before production approval
- E6 Privacy: deterministic privacy/retention gate is implemented and regression-tested; provider-specific processing, transfer, retention and data-subject review remain required before production approval

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
