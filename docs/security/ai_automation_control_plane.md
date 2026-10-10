# AI Automation Control Plane

ZooTasks targets approximately 98% AI-driven automation with approximately 2%
human governance. This does **not** grant the AI unrestricted authority.

## Control model

1. AI proposes an action.
2. The action is normalized and classified by a deterministic risk layer.
3. The independent authorization/policy layer validates actor, resource, scope,
   exact parameters, policy version, and current owner-control state.
4. Critical financial, security, compliance, credential, destructive, and
   production actions require human governance/dual control.
5. Execution occurs atomically where state mutation is financial or otherwise
   security-critical.
6. Audit records contain bounded decision metadata and must not contain secrets,
   credentials, or unnecessary sensitive data.

## Fail-closed rule

Unknown AI actions are classified as HIGH risk. They are never silently treated
as low-risk because a model claims they are safe.

The initial deterministic classifier lives in
`backend/core/ai_action_risk.py`. It is intentionally not a substitute for
the existing authorization engine; it is an additional risk boundary.

## Security research basis

This design follows the current OWASP AI Agent Security guidance around
least-privilege tool access, independent authorization outside the model,
exact-action approval binding, replay resistance, human approval for
high-impact actions, output validation, circuit breakers, and adversarial CI
testing. OWASP also identifies prompt injection, tool abuse, memory poisoning,
excessive autonomy, high-impact action abuse, cascading failures, and Denial of
Wallet as material agent risks.

NIST AI RMF and its Generative AI Profile likewise emphasize governance,
testing/evaluation, documentation, and appropriately configured human oversight.

Production activation remains gated by CI, migration review, configuration
verification, and the existing owner dual-control state.

## Tool execution boundary

`backend/core/ai_control_plane.py` adds a deterministic pre-execution
boundary for AI proposals:

- Tool names are a closed enum; unknown tools fail closed.
- Each tool is bound to exactly one normalized action.
- Targets and scopes must be explicit.
- Plans are bounded to a small maximum step/tool-call count.
- Retries are bounded to reduce runaway execution and Denial-of-Wallet risk.
- Request parameters are passed through the existing secret-rejecting canonical
  binding before a plan digest is produced.
- Critical actions cannot enter the AI tool execution path.
- Higher-impact actions must use a separate governed execution path; the AI
  layer itself never upgrades its authority.

This is intentionally a **proposal/control boundary**, not an authorization
grant. The existing execution authorization and Owner dual-control mechanisms
remain authoritative for protected mutations.
