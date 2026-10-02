# ZooTasks AI Innovation Genome & Discovery Fabric

## Purpose

The Innovation Genome & Discovery Fabric (IGDF) extends the Autonomous Innovation Loop with a deterministic representation of what is new. It prevents an innovation system from repeatedly proposing the same mechanism under different wording while still allowing genuinely different combinations of capability, workflow, integration, safety controls, and worker value to be discovered.

This is a proposal/discovery system, not an execution authority. Production AI remains disabled until the existing approval gates are satisfied.

## Research basis

NIST's 2026 AI Agent Standards Initiative emphasizes trusted agent interoperability, agent security and identity, and standards for autonomous agents. NIST's current agentic-AI work also emphasizes evaluation, testing, governance, interoperability and risk management. NIST's TEVV-Athlon draft describes an extensible evaluation approach applicable to agentic systems. See NIST AI Agent Standards Initiative and NIST TEVV-Athlon Framework.

OWASP guidance for agentic systems emphasizes least privilege, validated inputs/context, authenticated agent identity and message integrity, hard resource budgets/circuit breakers, and explicit human approval for high-impact actions. The design therefore keeps novelty generation separate from execution authority.

Current AI-work providers demonstrate a broad task surface including annotation, data collection, judging, transcription, translation, multimodal training data, model evaluation and agentic-workflow training. This supports a provider-neutral canonical model rather than hard-coding one provider's task taxonomy.

## The model

### 1. Innovation Genome

Every proposal is represented across five dimensions:

1. Capability — what ZooTasks can newly do.
2. Workflow — how work moves through discovery, qualification, execution and verification.
3. Integration — how external providers/data sources connect through approved boundaries.
4. Safety — what new controls make the capability safer or more auditable.
5. Worker value — what legitimate new work opportunity, qualification path, or matching improvement is created.

The genome is canonicalized and hashed. An exact fingerprint match means the mechanism is already known.

### 2. Distance-based novelty

The first deterministic implementation counts changed dimensions against known mechanisms. This is intentionally conservative: a textual rewording is not treated as innovation. Future versions may add weighted semantic fingerprints, but any such extension must remain deterministic, versioned, and evidence-backed.

### 3. Discovery Fabric

The long-term loop is:

approved-source observation
-> candidate extraction
-> source/provenance capture
-> canonical provider/offer normalization
-> quarantine
-> genome fingerprint
-> duplicate/material-change detection
-> security and reversibility gate
-> innovation proposal
-> human design approval
-> implementation
-> deterministic TEVV
-> controlled rollout
-> monitor
-> learning

Discovery does not activate a provider or offer.

### 4. Future-provider compatibility

A new AI company, workforce platform, API, feed, or legitimate public offer should be representable by the same provider/offer contract. Provider-specific behavior belongs behind an adapter. Unknown or changed sources enter quarantine rather than silently becoming executable.

This makes the core extensible: future offers can be added through new source registrations/adapters and schema mappings without rewriting wallet, authorization, or settlement logic.

### 5. Acquisition extension

For providers without an approved automation interface, the fabric may produce a research record and a draft outreach proposal. External communication remains a separate state machine requiring explicit authorization and human approval. It must not bypass CAPTCHA, access controls, credentials, rate limits, private data restrictions, or provider terms.

### 6. Non-negotiable financial boundary

The innovation fabric cannot:
- mutate balances;
- approve or pay withdrawals;
- execute promotion payouts;
- change permissions/Owner authentication;
- activate production AI;
- grant provider authorization;
- directly create an executable worker task;
- send external side effects without the separate approval gate.

## Next implementation stages

1. Mechanism catalog persistence and versioned fingerprints.
2. Approved-source discovery queue with provenance and quarantine.
3. Deterministic acquisition state machine with approval bound to exact proposal digest and expiry.
4. Provider sync-health/circuit-breaker gate.
5. Automated material-change revalidation.
6. TEVV evidence expansion and rollback drills.
7. Only after all gates: controlled production activation review.

## Evidence principle

The system should continuously generate candidates, not continuously grant authority. This distinction lets ZooTasks pursue continuous innovation while preserving deterministic control over money, identity, permissions, provider authorization and external effects.
