# ZooTasks AI Agent Provenance Receipts

## Purpose

ZooTasks records a compact provenance receipt for an AI decision without storing the prompt, model output, secrets, or task payload.

## Receipt

The receipt binds agent identity, capability, correlation ID, data class, policy version, decision, optional tool decision, and evidence reference to a deterministic SHA-256 digest.

## Security boundary

This is an evidence layer, not an authorization mechanism. Authorization is still enforced by the agent registry, data boundary, tool permission gateway, AI capability budget, and safety firewall.

Raw prompts and outputs must not be copied into the receipt. Unknown fields fail closed so future code cannot silently turn the provenance record into a sensitive-data sink.

## Research direction

The design follows the emerging agent-identity direction emphasizing identity, authority, delegation context, auditability and non-repudiation, while keeping ZooTasks data-minimization as a hard constraint.
