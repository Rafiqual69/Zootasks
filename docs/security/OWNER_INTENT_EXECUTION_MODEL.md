# ZooTasks Owner Intent Execution Model

Version: 1.0.0
Status: Security design baseline

## Purpose
The Owner should be able to direct legitimate ZooTasks project work efficiently without turning Owner authentication into unrestricted data or financial authority.

## Execution chain
Owner intent -> capability decomposition -> server-side policy decision -> required approval -> bounded service -> business invariants -> atomic effect -> audit evidence -> result

## Owner-directed capabilities
- product development workflows
- security audit/remediation workflows
- research/reporting workflows
- tests and CI workflows
- deployment preparation
- approved operational workflows

Each capability must be explicitly defined. An instruction is not itself permission to mutate protected data.

## Required controls
Before a sensitive capability executes, the server must independently verify:
1. authenticated Owner identity;
2. recent privileged re-authentication where required;
3. server-side target/object resolution;
4. PDP/PEP authorization;
5. object ownership and scope;
6. financial/security business invariants;
7. idempotency and concurrency requirements where applicable;
8. safe audit evidence.

## High-impact operations
Authentication, authorization, security-policy, deployment, financial, and sensitive-data operations must use narrowly scoped capability requests.

A capability request contains only:
- capability ID
- actor category
- resource/action
- object scope
- intended outcome
- expiry
- required assurance level
- required approval

Secrets, passwords, tokens, raw payment identifiers, and client assertions are never authority inputs.

## Separation of duties
Owner direction does not remove Finance/Finance Payer separation. Approval and payment remain distinct. Financial operations continue to require their existing state, balance, reservation, idempotency and atomicity checks.

## AI boundary
AI may help decompose or propose work, but AI is never the authority source for Owner capabilities. AI cannot grant itself access, change roles, bypass policy, mutate wallet/ledger state, approve/pay withdrawals, or process promotion payouts.

## Automation
Automation executes only capabilities that have already passed policy and authorization. Automation does not become an additional privileged identity merely because it is running on behalf of the Owner.

## Security response
Suspicious or high-risk Owner activity may require re-authentication, session revocation, temporary restriction, or human review. Risk signals never authorize financial movement by themselves.

## Audit
Every high-impact capability records safe evidence: timestamp, actor category/pseudonymous ID, capability ID, resource/action, object scope where safe, authorization decision, result, and correlation ID.
Secrets and sensitive payloads are excluded from logs.

## Governance
New Owner capabilities require threat modeling, explicit policy rules, tests, security regression, and CI evidence before production use.

Core rule:
Owner intent controls WHAT ZooTasks should attempt. Security policy controls WHETHER and HOW that action may execute.