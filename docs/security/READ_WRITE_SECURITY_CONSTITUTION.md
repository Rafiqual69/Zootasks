# ZooTasks Read/Write Security Constitution

**Policy ID:** ZT-SEC-CONSTITUTION  
**Policy Version:** 1.0.0  
**Policy Status:** Normative design baseline  
**Scope:** Application data, privileged operations, financial state, authentication/authorization state, AI capabilities, security evidence, and future resources.

## 1. Purpose

This Constitution defines the non-negotiable security principles for deciding who or what may read, create, update, delete, approve, pay, or otherwise cause an effect on ZooTasks resources.

It is the human-readable authority for the machine-readable policy at:

`docs/security/read_write_policy.json`

The JSON policy is a policy declaration, not a substitute for server-side enforcement. A request is never authorized merely because a client, template, URL, role name, or JSON value says it is allowed.

## 2. Core Security Invariants

1. **Deny by default.** An action not explicitly permitted by an applicable policy rule is denied.
2. **Server-side enforcement.** Authorization decisions must be enforced in trusted server-side code at the protected operation/resource boundary.
3. **Least privilege.** Actors receive only the minimum access required for their defined business function.
4. **Object ownership matters.** Role membership alone never grants access to another user's object.
5. **Field sensitivity matters.** A user may be allowed to update a resource while still being forbidden from changing security-sensitive or financial fields.
6. **Financial state is critical.** Wallet balances, ledger entries, withdrawal state, rewards, promotion payouts, and related integrity controls require explicit financial authorization.
7. **Separation of duties.** Approval and payment authority are distinct capabilities unless an explicitly reviewed policy says otherwise.
8. **AI is non-authoritative by default.** AI has no write authority unless a capability is explicitly approved, bounded, audited, and separately enforced. AI must never directly mutate protected financial state.
9. **No client-controlled authorization.** Hidden form fields, query parameters, HTTP methods, UI visibility, or client-side role flags cannot establish authority.
10. **Fail closed.** Missing policy, malformed policy, unknown actor/resource/action, policy conflict, or enforcement failure must not silently grant access.
11. **No secret material in policy.** Policy files must contain identifiers and rules only; never passwords, tokens, API keys, session secrets, private keys, raw OTP/WebAuthn challenges, or personal identity secrets.
12. **Minimal disclosure.** Authorization failures and logs must not disclose protected resource contents, secrets, credentials, or unnecessary personal data.
13. **Atomic critical writes.** Financial and other integrity-critical mutations must execute inside the appropriate transactional/concurrency controls.
14. **Idempotency for money movement.** Financial business events must be protected against duplicate execution.
15. **Immutable evidence.** Financial ledger records and security evidence must not be silently rewritten to hide prior state.
16. **Explicit deletion.** Destructive actions require an explicit policy rule; absence of a rule means deletion is denied.
17. **Authentication is not authorization.** A valid login does not by itself authorize privileged operations.
18. **Privileged operations require stronger assurance.** Sensitive Owner/Finance operations may require recent re-authentication, MFA, session binding, or other explicit conditions.
19. **Policy changes are security changes.** Changes to this Constitution, the JSON policy, schema, or enforcement semantics require review and CI evidence.
20. **Backward-compatible evolution.** Policy identifiers are stable. New fields must be additive where possible; removal or semantic change requires a versioned migration and regression evidence.

## 3. Decision Model

Every protected operation follows this conceptual model:

**Actor → Resource → Action → Object/Scope → Conditions → Decision → Enforcement → Audit Evidence**

The minimum decision inputs are:

- actor type and authenticated identity
- active role/entity state
- resource type
- action
- target object and ownership/tenant scope where applicable
- resource state
- security/financial sensitivity
- required authentication assurance
- policy version
- relevant business invariants

A policy decision is binary:

- `allow`
- `deny`

There is no implicit "maybe" or "allow if the UI permits it" state.

## 4. Canonical Vocabulary

### Actors

Current canonical actors include:

- `anonymous`
- `worker`
- `owner`
- `finance`
- `finance_payer`
- `ai`
- `system`

A future actor type must be added deliberately and must not inherit permissions accidentally.

### Actions

Actions are intentionally more precise than HTTP verbs:

- `read`
- `create`
- `update`
- `delete`
- `claim`
- `submit`
- `approve`
- `reject`
- `pay`
- `manage_access`
- `manage_authentication`
- `export`

A new action is a security-policy change.

### Scopes

- `public`
- `own`
- `assigned`
- `role_scope`
- `global`
- `none`

Object-level ownership or assignment must be checked independently of role membership.

## 5. Data Classification

Every policy resource must declare a sensitivity class:

- `public`: intentionally public information.
- `internal`: application information not intended for public disclosure.
- `confidential`: user/business/security information requiring controlled access.
- `financial_critical`: wallet, ledger, withdrawal, reward, payout, or equivalent integrity-critical state.
- `security_critical`: authentication, authorization, credentials, security evidence, policy, or privileged-control state.

Policy metadata must never contain the underlying sensitive values.

## 6. Financial Boundary

The following are explicitly protected:

- wallet balance and reserved balance
- WalletTransaction records
- withdrawal state and payment execution
- task rewards and reward-bearing fields
- promotion rewards, budgets, payout state, and completed-worker counters
- financial audit/reconciliation evidence

The policy must distinguish:

**read → create → update → approve → pay**

A role with one financial capability must not inherit another capability.

In particular:

- AI: no financial write authority.
- Worker: no financial administration authority.
- Finance: may approve/reject only where explicitly granted; cannot pay.
- Finance payer: may pay only where explicitly granted; cannot approve/reject.
- Owner: privileged authority is explicit and must remain server-side controlled.

No policy change may alter financial semantics merely to make authorization easier.

## 7. Object-Level Authorization

For resources containing user-owned or assigned records, authorization must evaluate the target object.

Examples:

- Worker A may access Worker A's claims, but not Worker B's claims.
- A withdrawal belonging to Worker A is not readable or mutable by Worker B.
- A task claim must be checked against the authenticated worker, not only by an object ID.
- A future API endpoint must not accept an object identifier as proof of ownership.

## 8. Field-Level Write Protection

Resource-level write permission does not imply unrestricted field mutation.

Examples of fields requiring stronger controls include:

- reward
- budget
- max_workers
- completed_workers
- wallet balance
- reserved balance
- withdrawal status
- payout identifiers
- role/entity type
- staff/superuser flags
- authentication state
- policy version/state

Sensitive fields must be protected both in the interface and server-side validation/update path.

## 9. AI Boundary

AI is treated as an untrusted decision-support actor unless a capability is explicitly approved.

AI must not directly:

- mutate wallet balances
- create financial ledger effects
- approve or pay withdrawals
- process promotion payouts
- change privileged roles
- create or activate an Owner entity
- bypass authentication or authorization
- disable security controls

AI output is data, not authority. Any future AI-assisted action must pass through the same server-side policy enforcement and business invariants as a human action.

## 10. Policy Conflict Resolution

The following precedence is mandatory:

1. Explicit deny for the exact protected action.
2. Security-critical invariant.
3. Financial-critical invariant.
4. Object ownership/scope restriction.
5. Explicit allow rule.
6. Default deny.

A broader allow rule must never override a narrower security-critical or financial-critical deny.

## 11. Policy Evolution and Compatibility

The machine-readable policy uses:

- `policy_id` — stable identity.
- `policy_version` — semantic policy version.
- `schema_version` — machine format version.

Rules use stable `rule_id` values.

### Compatibility rules

- Patch: documentation/metadata-only compatible changes.
- Minor: additive rules/fields that preserve existing denials and existing rule meanings.
- Major: removal, renaming, changed meaning, changed default behavior, or changed security semantics.

A policy parser must reject unsupported major schema versions rather than guessing.

Unknown fields may be tolerated only where the validator explicitly supports forward-compatible metadata. Unknown actions, actors, resources, scopes, or decisions must fail closed.

## 12. Data-Leakage Rules

The Constitution and JSON policy must never contain:

- passwords
- SECRET_KEY
- API keys/secrets
- OAuth client secrets
- Telegram bot tokens
- SMTP credentials
- session cookies
- raw OTP/TOTP secrets
- WebAuthn challenge values
- private keys
- bank account numbers
- unnecessary personal identifiers
- production database contents

Audit events should record stable identifiers and decision metadata, not protected payloads.

## 13. Enforcement Architecture

The intended architecture is:

**Policy declaration → policy validation → Policy Decision Point → Policy Enforcement Point → business invariant/service → atomic mutation → audit evidence**

The JSON file is not itself a security boundary. Every critical operation must have a trusted enforcement point.

Policy code must not be generated from untrusted request data.

## 14. Testing Contract

For every new or changed rule, tests must cover at minimum:

- permitted actor/action
- denied actor/action
- missing role/entity
- inactive role/entity
- wrong object owner
- wrong object state
- sensitive-field mutation
- malformed/unknown policy input
- conflict between allow and deny
- unauthenticated request
- privileged request without required assurance
- duplicate critical operation where applicable

Financial changes additionally require the existing financial regression suite and idempotency/concurrency coverage.

## 15. CI and Change Governance

A policy change is incomplete until:

1. JSON parses and validates against its schema.
2. No secret scan finding is introduced.
3. Policy invariant tests pass.
4. Relevant application authorization tests pass.
5. Financial regression tests pass for financial-related changes.
6. Full regression passes.
7. Django system/deployment checks pass.
8. Dependency/security checks pass.
9. `git diff --check` passes.
10. The change is reviewed and merged through the protected development path.

This aligns the policy with secure-development practices such as NIST SSDF and with OWASP guidance on access control and software supply-chain integrity. citeturn0search7turn0search0

## 16. Security Constitution Rule

If an implementation conflicts with this Constitution, the implementation must be treated as a security defect until the Constitution and its supporting evidence are deliberately changed.

The safest future behavior is therefore:

**Unknown = Deny.  
Ambiguous = Deny.  
Broken policy = Deny.  
Missing authorization check = Deny.  
Financial ambiguity = Stop and investigate.**

## 17. Change History

- 1.0.0 — Initial normative Read/Write Security Constitution.
