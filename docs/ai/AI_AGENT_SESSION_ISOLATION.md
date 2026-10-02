# ZooTasks AI Agent Session Isolation

AI agents must not inherit human, Owner, admin, worker, or provider credentials.

The session boundary creates only short-lived metadata bound to an agent identity, audience, explicit scope, and expiry. It deliberately does not accept or store passwords, API keys, bearer tokens, or provider secrets.

## Rules

- agent identity is separate from human identity;
- audience is explicit and prevents cross-service reuse;
- scopes are explicit and minimal;
- expiry is mandatory and timezone-aware;
- expired or mismatched sessions fail closed;
- credentials must be supplied by a future external secret/identity mechanism, never through prompts or ordinary application logs.

A future provider integration must use short-lived, audience-restricted credentials and must never reuse an Owner/admin credential. Financial and identity-control services remain inaccessible to the AI agent regardless of session scope.
