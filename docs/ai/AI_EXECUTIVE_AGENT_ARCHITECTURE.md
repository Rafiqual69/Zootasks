# ZooTasks AI Executive and Agent Orchestration Architecture

## Purpose

ZooTasks will use a governed multi-agent architecture in which an Executive AI Advisor/Orchestrator coordinates specialized agents and provides the Owner with evidence-based briefings. The Executive Agent is an advisory and orchestration layer; it is not a replacement for Owner authority or deterministic application authorization.

This design also supports the product requirement to acquire legitimate AI-task opportunities from both automation-enabled providers and organizations that do not expose automated task feeds.

## Operating model

```
Owner
  |
  v
Executive AI Advisor / Orchestrator
  |
  +--> Research Agent
  +--> AI Provider / Offer Agent
  +--> Business Acquisition Agent
  +--> Task Normalization Agent
  +--> Worker Matching Agent
  +--> QA / Verification Agent
  +--> Security / Compliance Agent
  +--> Automation Agent
  |
  v
Deterministic ZooTasks Core
  |
  +--> authorization
  +--> task state
  +--> wallet / withdrawal controls
  +--> audit trail
```

## Executive Agent responsibilities

The Executive Agent may:

- aggregate findings from specialized agents;
- identify opportunities, risks, conflicts and missing evidence;
- prepare Owner briefings and recommended next actions;
- coordinate research and non-privileged workflows;
- require a human approval gate when the policy says approval is necessary;
- maintain decision context, provenance and audit references;
- stop or escalate a workflow when a security, compliance, authorization or evidence requirement is not satisfied.

The Executive Agent must not obtain sovereign authority over the application.

## Agent authority model

Every agent receives an explicit capability profile:

- allowed tools;
- allowed data classes;
- allowed external destinations;
- allowed action classes;
- maximum resource/budget limits;
- reversibility class;
- approval requirement;
- audit/provenance requirements.

Default is deny. An agent may use only capabilities explicitly granted to it.

Agent messages, retrieved content, external task descriptions, provider responses and tool output are untrusted input and must be validated before they influence an action.

## High-impact boundary

AI/agents have no direct authority to:

- mutate wallet balances;
- approve, reject, reserve, pay or otherwise finalize withdrawals;
- execute promotion payouts;
- change Owner authentication or privileged permissions;
- grant application privileges;
- bypass deterministic business rules;
- activate production AI without the required approval evidence;
- perform irreversible external actions without the required human/authorization gate.

The financial and privileged boundaries remain enforced by deterministic application controls, not by an agent instruction or model output.

## AI-task acquisition

### Route A — automation-enabled provider

```
Provider/API/feed
 -> authenticated intake
 -> source validation
 -> security/compliance checks
 -> offer normalization
 -> eligibility
 -> task execution
 -> QA
 -> deterministic settlement workflow
```

### Route B — provider without an automation feed

```
Research / discovery
 -> provider qualification
 -> controlled business offer
 -> authorized communication
 -> human/authorized onboarding
 -> approved agreement/feed
 -> provider adapter or controlled intake
 -> normal task pipeline
```

The acquisition agent must not spam, impersonate ZooTasks or a person, bypass access controls, defeat CAPTCHA/anti-bot controls, harvest credentials, or scrape restricted/private task systems. External outreach must respect applicable law, provider terms and communication controls.

The system must distinguish:

1. public/open opportunities;
2. authorized partner/API opportunities;
3. private/vendor opportunities obtained through an authorized relationship;
4. unverified or restricted sources, which remain quarantined.

No unverified source becomes a production task source merely because an agent discovers it.

## Provider and offer provenance

Each provider/offer integration should record, where applicable:

- provider identity and source;
- acquisition route;
- authorization/contract status;
- source URL or API identifier;
- region/worker eligibility;
- task category;
- reward and currency;
- data sensitivity;
- retention/processing requirements;
- terms and restrictions;
- expiration;
- verification method;
- adapter/version;
- last successful synchronization;
- security review status;
- audit references.

Provenance must remain linked to the normalized offer and subsequent task execution.

## Security controls

Required controls before external agent actions include:

- allowlisted tools and destinations;
- isolated credentials/secrets;
- least-privilege service identities;
- schema validation for all agent/tool inputs and outputs;
- prompt-injection and untrusted-content defenses;
- rate/concurrency/session budgets;
- circuit breakers and kill/disable paths;
- idempotency for external operations;
- immutable or protected audit evidence;
- deterministic authorization outside the model;
- explicit approval for high-impact or irreversible actions.

Human approval screens must present the actual proposed action and material parameters, not an agent-generated summary alone, because approval interfaces themselves can be manipulated.

## Governance lifecycle

A new agent or materially changed capability must:

1. enter the AI system inventory;
2. receive a capability/threat assessment;
3. define its tool/data/action allowlist;
4. receive deterministic security and adversarial tests;
5. establish provenance and evidence requirements;
6. pass the applicable lifecycle gates;
7. remain disabled in production until approval is recorded.

Provider/model/prompt/tool changes are controlled changes and trigger re-evaluation where material.

## Initial implementation status

This document defines the architecture only. No production Executive Agent or external acquisition agent is approved or enabled by this document.

The first implementation should be read-only/advisory and network-disabled during evaluation. External communication and provider adapters remain separate capabilities that require their own inventory entries, security tests and approval gates.

## Research basis

The design follows current risk-management and agent-security guidance emphasizing governance, human oversight, data provenance, least privilege, validation of untrusted agent inputs, resource limits and explicit approval for high-impact actions. See NIST AI RMF/GAI Profile and OWASP agentic-AI guidance.

