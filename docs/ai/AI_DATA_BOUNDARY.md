# ZooTasks AI Data Boundary

## Purpose

The data boundary is the deterministic gate between ZooTasks application data and an AI provider. It uses an explicit allowlisted projection plus deterministic redaction. It does not use an AI model to decide what is safe to send.

## Current contract

- Agent: `ZT-AGENT-001`
- Capability: `AI-SYS-001`
- Data class: `task_content_minimal`
- Approved fields: `title`, `description`, `category`
- Unknown data classes: deny
- Credentials and common contact identifiers in the projection: redact
- No raw sensitive values are written to the evidence record
- Tool access remains disabled

## Security rule

The provider payload must be constructed from this projection, not from a model-generated scrubber or an arbitrary model input object. Redaction is defense-in-depth; it does not authorize additional fields.

Worker identity, wallet/withdrawal data, authentication material, owner-security data, and unrelated personal data remain outside the approved data class.

## Evaluation requirements

Before production provider approval, add adversarial coverage for secret reflection, indirect prompt injection, cross-task data access, data-class escalation, and attempts to induce the agent to reveal redacted content.
