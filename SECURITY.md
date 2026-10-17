# Security Policy

## Scope

ZooTasks is a task-marketplace project. Security reports involving authentication, authorization, account data, wallet balances, task or promotion rewards, withdrawals, secrets, deployment configuration, or data exposure are especially important.

## Reporting a Vulnerability

- **Do not** publish exploitable details, credentials, personal data, or proof-of-concept payloads in public issues or pull requests.
- Prefer GitHub's **private vulnerability reporting** feature for this repository when it is enabled.
- If private reporting is unavailable, contact the repository maintainer privately through their GitHub profile and request a secure reporting channel. Do not include secrets or sensitive user data in the initial message.
- Include the affected component, impact, reproduction steps using synthetic/test data, and any suggested mitigation. Redact tokens, cookies, account identifiers, and production data.

## Response and Disclosure

The maintainer will assess reports as capacity permits. Please allow time for triage and remediation before public disclosure. No fixed response-time SLA is promised by this policy. Coordinated disclosure should avoid exposing users to unnecessary risk.

## Safe Testing

- Test only systems and accounts you own or are explicitly authorized to assess.
- Do not access, alter, or export other users' data.
- Do not perform denial-of-service, destructive testing, or real-money transaction tests against production.
- Use synthetic data and isolated test environments for financial and authorization checks.

## Project Security Principles

- Financial ledger, wallet, task reward, promotion reward, and withdrawal controls must fail closed on authorization or consistency errors.
- Secrets and sensitive request payloads must not be committed, logged, or disclosed.
- Security-sensitive changes must pass relevant automated checks and receive appropriate human review.
- Passing CI is evidence for the tested cases, not a guarantee that the system is secure or production-ready.

## Supported Versions

Security fixes are currently evaluated against the active security-development branch and the default branch. Production support status must be explicitly announced; this repository policy does not itself authorize production deployment.
