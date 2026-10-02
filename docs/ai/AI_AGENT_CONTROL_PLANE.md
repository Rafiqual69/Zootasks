# ZooTasks AI Agent Control Plane

## Purpose

The agent control plane establishes a provider/model-independent identity and
least-privilege boundary before ZooTasks introduces autonomous AI agents.

This layer does not call providers, execute tools, mutate business state, or
grant application permissions.

## Current registered agent

| Agent ID | Capability | Data class | Tools | Autonomy | Status |
|---|---|---|---|---|---|
| ZT-AGENT-001 | AI-SYS-001 | task_content_minimal | none | suggestion_only | Design |

## Hard boundaries

- Agent identity is separate from provider/model identity.
- Capabilities are explicit allowlists.
- Data classes are explicit allowlists.
- Tools are deny-by-default.
- Autonomy cannot be escalated by model output.
- Financial, identity, permission, and irreversible actions remain outside the agent boundary.
- Unknown agents, capabilities, data classes, tools, and autonomy levels fail closed.
- Registry validation is not business authorization; deterministic application controls remain authoritative.

## Data-minimization contract

ZT-AGENT-001 may receive only the minimum task content required by AI-SYS-001.
Worker identity, wallet balances, withdrawal information, authentication
material, secrets, and unrelated personal data are not part of its approved
data class.

This follows the security direction emphasized by NIST for agent identity and
authorization and by OWASP's agentic-security guidance: agents should be
treated as systems with explicit identity, tool, memory, and trust boundaries.

## Next expansion

Before any production agent is enabled, add and evaluate:

1. data-classification/redaction gateway;
2. tool permission gateway with per-tool approval levels;
3. agent session and credential isolation;
4. agent action audit/provenance;
5. adversarial tests for indirect prompt injection and data exfiltration;
6. production disable/rollback controls.

No production provider or autonomous execution is enabled by this registry.