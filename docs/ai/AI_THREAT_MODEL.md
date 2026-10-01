# ZooTasks AI Threat Model

## Status
Design-stage artifact. ZooTasks has no approved production AI system yet.

## Scope
This threat model applies to the planned first AI capability and later model, agent, retrieval, or provider integrations.

The initial capability is intentionally limited to task-classification and quality-assistance. It may propose classifications, detect missing/ambiguous task information, and produce review suggestions. It must not directly approve workers, approve claims, change task rewards, mutate wallet balances, reserve/approve/pay withdrawals, release promotion funds, change permissions, or authenticate an Owner.

## System boundary
User/Admin input -> Django application + deterministic authorization -> AI gateway (untrusted computation) -> model/provider -> structured validation + policy gate -> human review when required -> persisted non-financial suggestion.

The AI gateway is outside the application's trust boundary. A model response is treated as untrusted input.

## Trust boundaries
1. User/content -> application: user-provided and external content is untrusted.
2. Application -> AI gateway: only explicitly allowed, minimized data may cross this boundary.
3. AI gateway -> model/provider: provider access is constrained by an explicit allowlist and configuration.
4. AI response -> application: output is untrusted and must pass schema, size, content, and policy validation.
5. AI-assisted result -> privileged business operation: no AI result can bypass Django authorization or deterministic financial services.

## Protected assets
- Wallet balances and reserved balances.
- WalletTransaction and withdrawal records.
- Promotion funding, declared liability, and payout records.
- Task claims, approvals, rewards, and completion counters.
- Owner authentication, MFA, OAuth state, and privileged permissions.
- Secrets, provider credentials, bot tokens, API keys, and signing material.
- Personal data and account identity information.
- AI prompts, outputs, evaluations, model/provider configuration, and audit evidence.
- Availability and AI-provider cost budgets.

## Threats and mandatory controls

| ID | Threat | Required control | Verification evidence |
|---|---|---|---|
| TM-01 | Prompt injection attempts to obtain privileged behavior | Treat external/user content as adversarial; AI has no application authority | Adversarial prompt tests + authorization tests |
| TM-02 | Sensitive data disclosure to provider | Data minimization, field allowlist, redaction, provider allowlist, retention rules | Data-flow review + provider configuration |
| TM-03 | Malicious or malformed model output | Strict structured-output schema, size limits, deterministic validation | Unit/integration tests |
| TM-04 | AI-induced financial mutation | AI cannot call wallet/withdrawal/promotion financial mutation paths | Architecture test + service-boundary tests |
| TM-05 | Excessive agency | AI capability allowlist and explicit prohibited actions | Capability-gate record |
| TM-06 | Model/provider supply-chain change | Pin and record provider/model/version/config; change review | Model inventory + release evidence |
| TM-07 | Model/data poisoning | Provenance and review for evaluation/training data | Dataset manifest + review record |
| TM-08 | Uncontrolled cost or denial of service | Request, token, concurrency, timeout and budget limits | Runtime metrics + limit tests |
| TM-09 | AI failure or unsafe degradation | Fail closed for privileged actions; deterministic fallback for non-AI workflow | Failure tests + rollback procedure |
| TM-10 | Inadequate auditability | Record capability ID, model/provider version, prompt version, result class, timestamp and correlation ID without unnecessary sensitive content | Audit-log test + evidence record |
| TM-11 | Privacy/retention violation | Purpose limitation, minimization, retention and access controls | Data inventory + retention review |
| TM-12 | Human review bypass | Risk-based human approval gate for high-impact actions | Approval workflow test |

## Non-negotiable financial boundary
The deterministic server-side chain remains: Task approval -> Wallet ledger -> Withdrawal reservation -> Withdrawal approval -> Paid -> Reconciliation.

AI may assist with information or recommendations around these processes, but it cannot become the authority that changes financial state.

## Failure behavior
- Provider unavailable: controlled application error or deterministic fallback; never invent a result.
- Schema validation failure: discard the AI result and record a safe failure event.
- Authorization ambiguity: deny the action.
- Prompt injection detected: treat content as untrusted and prevent privilege escalation.
- Budget/rate limit reached: stop AI calls without weakening application security.
- Provider/model/configuration mismatch: block production use until inventory and approval are updated.

## Required pre-production evidence
1. Inventory entry completed.
2. Intended and prohibited use documented.
3. Data-flow and data classification approved.
4. Risk assessment completed with residual risk.
5. Provider/model/version recorded.
6. Structured output contract implemented.
7. Evaluation set and adversarial tests completed.
8. Human oversight defined.
9. Monitoring and incident response defined.
10. Rollback/disable mechanism tested.
11. Release approval recorded.
12. Evidence is linked to the exact software/configuration/model version.

## Alignment
This artifact operationalizes the ZooTasks AI governance policy against NIST AI RMF concepts of Govern, Map, Measure, and Manage. NIST describes AI risk management as continuous across the AI lifecycle and emphasizes governance, context/risk mapping, measurement, and risk treatment. The framework is voluntary and currently being revised, so this document is an implementation artifact rather than a certification claim.
