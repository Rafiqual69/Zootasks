# ZooTasks AI Tool Permission Gateway

The tool gateway is a separate authorization boundary from the agent registry and AI safety firewall.

## Current policy

ZT-AGENT-001 / AI-SYS-001 has zero permitted tool classes, zero tool-call budget, and no external side effects.

Unknown agents, capabilities, and tools fail closed.

## Security rule

Agent/model output can never grant itself a tool. A future tool must be explicitly registered with an agent/capability policy and receive deterministic scope and call budget before execution.

Business authorization remains outside this gateway. Wallet, withdrawal, promotion payout, permission, owner authentication, identity binding and irreversible actions remain controlled by deterministic application services.
