# Owner Account Management Security Benchmark — ZooTasks

**Status:** Research/design baseline; not a certification or independent penetration-test report.  
**Prepared:** 2026-10-11  
**Scope:** Owner identity, privileged access, device enrollment, sessions, automation/service identities, auditability, recovery, and fail-closed execution.

## Executive decision

ZooTasks should use a **single, strongly verified Owner identity with separately enrolled authenticators**, least-privilege permissions, short-lived privileged authorization, and independent approval for high-impact operations. “One Owner account” must not mean “one shared credential,” “permanent session,” or “one device can bypass dual control.”

No platform can guarantee absolute security. Controls must be layered and fail closed, with evidence from tests and release gates. This benchmark uses publicly available official documentation, not hands-on testing of vendor products.

## Benchmark: 12 comparable automation / identity platforms

| Platform | Publicly documented account/authorization pattern | Transferable lesson for ZooTasks | Source |
|---|---|---|---|
| GitHub Organizations | Organization Owner has broad administrative power; GitHub recommends limiting the role while maintaining at least two people for continuity. | Treat Owner as a high-risk role; keep a documented recovery/continuity plan rather than making the only credential irreplaceable. ZooTasks can use one human Owner while requiring two independent authenticators/approvals for critical actions. | [GitHub: organization roles](https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/roles-in-an-organization) |
| GitLab | Granular roles separate Owner, Maintainer, Developer and Security Manager; audit events cover user and permission changes. | Separate Owner administration from security review; record role, authenticator and access changes in an audit trail. | [GitLab roles](https://docs.gitlab.com/user/permissions/); [Audit events](https://docs.gitlab.com/user/compliance/audit_events/) |
| Microsoft Entra ID | Recommends phishing-resistant MFA for privileged administrator roles; warns to register suitable methods before enforcing policies to avoid lockout. | Require passkey/WebAuthn or security key for privileged operations, but prove enrollment and recovery work before enforcing a new hard gate. | [Microsoft: phishing-resistant admin MFA](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-admin-phish-resistant-mfa) |
| Temporal Cloud | RBAC assigns account-level roles and namespace-level permissions; supports SAML/SCIM; recommends least privilege and distinct service accounts for automation. | Separate human Owner identity from worker/agent identities; scope machine credentials narrowly and revoke independently. | [Temporal: account access](https://docs.temporal.io/cloud/manage-access); [Security controls](https://github.com/temporalio/documentation/blob/main/docs/best-practices/security-controls.mdx) |
| Zapier | Owner, Super Admin, Admin and Member roles have different powers; SAML SSO and provisioning options are documented for eligible plans. | Distinguish ownership transfer/deletion from routine administration; avoid giving all operators Owner powers. | [Zapier roles](https://help.zapier.com/hc/en-us/articles/39698983334797-User-roles-and-permissions-in-Team-and-Enterprise-accounts); [SAML SSO](https://help.zapier.com/hc/en-us/articles/8496279747085-Set-up-single-sign-on-with-SAML) |
| Make | Organization and team roles are separate; Owner has broad organization-level rights, including ownership transfer and deletion. | Enforce scope boundaries at organization, project/task and execution levels; make destructive ownership operations separately authorized. | [Make: organizations and roles](https://help.make.com/organizations) |
| Apache Airflow | Authentication and authorization are handled by a pluggable Auth Manager; changing the auth manager affects user and permission mappings. | Keep the authorization backend explicit and tested; treat identity-provider/backend changes as migrations requiring preflight and rollback plans. | [Airflow: Auth Manager](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/auth-manager/index.html) |
| Jenkins | Authentication (Security Realm) and authorization (strategy) are separate; documentation warns against permissive “anyone can do anything” setups. | Never infer authorization from successful login; every Owner endpoint and operation must check action-specific permissions server-side. | [Jenkins: access control](https://www.jenkins.io/doc/book/security/access-control/); [Securing Jenkins](https://www.jenkins.io/doc/book/security/securing-jenkins/) |
| Rundeck | ACL policies restrict actions on jobs, nodes, commands and APIs; authorization decisions are evaluated and logged. | Apply deny-by-default, resource/action-specific authorization to task execution and APIs, not just the UI. | [Rundeck: access control policy](https://docs.rundeck.com/docs/administration/security/authorization.html) |
| Argo CD | RBAC controls resource access; the built-in admin account is unrestricted, so RBAC/SSO configuration is central to safe use. | Avoid unrestricted fallback accounts; ensure no local/default administrator bypass remains after the secure identity path is configured. | [Argo CD: RBAC](https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/) |
| Prefect | Account and workspace roles differ; service accounts have separate keys and scopes, and keys can be rotated/revoked. | Use non-human service identities for AI agents and workers; add expiration/rotation, minimum scope and separate revocation. | [Prefect: roles](https://prefect-docs-preview.netlify.app/cloud/users/roles/); [Service accounts](https://docs-3.prefect.io/v3/how-to-guides/cloud/manage-users/service-accounts) |
| n8n | User management documents Owner/Admin/Member roles and identity integration options such as LDAP/SAML in applicable configurations. | Keep Owner-specific management separate from regular members; account for deployment/plan-specific features instead of assuming every deployment has the same controls. | [n8n: user management](https://docs.n8n.io/user-management/) |

### Benchmark limitations

Vendor features vary by deployment type, version and subscription tier. The table records publicly documented patterns relevant to the design, not a claim that every feature is enabled by default or available in every plan. No hands-on vendor configuration audit was performed.

## Standards and guidance mapped to the design

1. **NIST SP 800-63B-4 (July 2025)** — current Digital Identity Guidelines for authentication and authenticator management. Prefer phishing-resistant, verifier-bound cryptographic authentication for privileged access; enforce throttling, lifecycle management, revocation and safe recovery. OTP can be useful MFA but is not equivalent to phishing-resistant WebAuthn/passkeys.  
   Source: [NIST SP 800-63B-4](https://csrc.nist.gov/pubs/sp/800/63/B/4/final); [phishing resistance and WebAuthn](https://pages.nist.gov/800-63-4/sp800-63b.html)
2. **OWASP ASVS** — use applicable verification requirements for authentication, sessions, access control, validation, cryptography, logging, data protection, communications, APIs and configuration. Set a documented target level based on risk and verify it rather than claiming compliance by design alone.  
   Source: [OWASP ASVS guide](https://devguide.owasp.org/en/03-requirements/05-asvs/); [ASVS session management](https://github.com/OWASP/ASVS/blob/master/5.0/en/0x16-V7-Session-Management.md)
3. **CIS Controls v8.1, Controls 5, 6 and 8** — maintain an account inventory; centrally manage accounts where practical; separate administrator accounts; review privileges; require MFA for administrative access; revoke access promptly; collect and review audit logs.  
   Source: [CIS Account Management](https://www.cisecurity.org/controls/account-management); [CIS Access Control Management](https://www.cisecurity.org/controls/access-control-management); [CIS Controls Navigator](https://www.cisecurity.org/controls/CIS-controls-navigator)

These are engineering baselines, not a statement that ZooTasks is certified or legally compliant. A legal applicability review should separately consider Bangladesh requirements and the jurisdictions in which the platform operates.

## ZooTasks target controls

### A. Owner identity and account lifecycle
- Bind the Owner role to a verified, immutable internal user ID, not only a mutable username or email. OWNER_USERNAME may be a deployment bootstrap guard, but must not be the sole permanent identity binding.
- Never auto-promote an account to staff/superuser just because a configuration variable matches.
- Keep account creation, role changes, credential changes and ownership transfer behind a separate, audited administrative ceremony.
- Keep a break-glass recovery procedure sealed, logged, tested and independently reviewed; do not place recovery secrets in source control.
- Do not make the account “permanent” by disabling revocation. Permanence means continuity of identity and records; credentials and sessions must remain revocable.

### B. Authenticator and device lifecycle
- Implement complete WebAuthn registration and assertion ceremonies using a maintained library: fresh, single-use, expiring server challenges; strict RP ID/origin/type checks; signature and user-verification checks; credential uniqueness; transactional counter handling where applicable; replay rejection.
- Require a previously verified Owner session and fresh reauthentication to enroll, rename, revoke or replace authenticators. Notify the Owner through a separate channel of enrollment/revocation events.
- Device 1 is not “bound” merely because it submitted a request or passed OTP. Display device-binding status accurately.
- Enroll a second independent authenticator/device only after explicit Owner confirmation. Enrollment alone must never approve old queued requests.
- Loss or compromise must allow immediate credential revocation and session invalidation without deleting audit evidence.

### C. Sessions and browser security
- Use HTTPS only in production; secure, HttpOnly, appropriately SameSite cookies; session rotation after authentication/privilege changes; CSRF protection; content-security policy and output escaping.
- Set and test both inactivity and absolute session lifetimes. Reauthentication must be required for authenticator changes, recovery, account privilege changes, and high-impact actions.
- Provide “revoke all sessions” and per-session/device review; invalidate sessions after password/MFA/device/role changes.
- Never treat a session cookie, user-agent string, IP address or browser fingerprint as proof of device identity.

### D. Authorization and high-impact execution
- Default deny; enforce authorization in the server/service layer for every request, not only in the template/UI.
- Keep AI agents and workers on distinct service identities with minimum scopes, short-lived or rotatable credentials, expiry and separate revocation.
- A single Device 1 session may submit normal instructions and queue protected requests, but must not alone execute production deploys/rollbacks, migrations/restores, money movement, ledger changes, access-control changes, secret exposure or destructive/break-glass operations.
- Critical approvals must be bound to the exact canonical request digest, actor, operation, target environment and expiry; require two distinct enrolled authenticators/devices for designated actions. Reject reused, expired, revoked or request-mismatched approvals.
- No automatic execution of old queued requests after Device 2 is enrolled.

### E. Audit and data-leak prevention
- Record actor ID, event type, request/approval IDs, target, decision, timestamp, correlation ID and safe outcome metadata.
- Do not log passwords, OTPs, recovery codes, cookies, authorization headers, private keys, API tokens, raw WebAuthn assertions or unnecessary full request bodies.
- Redact secrets before error reporting; avoid logging rejected secret-like input itself.
- Protect audit records against ordinary Owner/worker tampering; restrict access, define retention, alert on role/authenticator changes, repeated failures, unusual recovery and break-glass use.
- Define data minimization, retention, deletion and export policies; keep sensitive request data private to its Owner and explicitly authorized reviewers.

## Required implementation and release gates

| Gate | Evidence required before enabling |
|---|---|
| Owner identity | Immutable owner ID binding; no auto-promotion; missing/mismatched config fails closed |
| WebAuthn enrollment | Valid/invalid origin, challenge expiry/replay, tampering, wrong RP ID, UV-required, duplicate credential and revoked credential tests |
| Recovery/revocation | Lost-device flow, recovery abuse tests, revoke-all sessions, notifications, recovery audit evidence |
| Session controls | Cookie flags, CSRF, session fixation, idle/absolute timeout, reauthentication and session invalidation tests |
| Authorization | Direct-URL/API bypass, IDOR, privilege escalation and default-deny tests for every protected action |
| Dual control | Two distinct devices/credentials, request-digest binding, expiry, replay, revocation, race/concurrency and freeze tests |
| Privacy | Canary-secret tests prove secrets are absent from logs, errors, audit events and UI; data access isolation tests |
| Persistence | Migration drift check; backup/restore rehearsal on isolated test data; SQLite and PostgreSQL regression suites |
| Supply chain | Dependency audit, pinned/controlled dependencies, secret scan, code review and CI on the exact PR head |
| Production gate | Independent review, all required checks green, documented rollback, and explicit SHA-specific Owner approval |

## Current repository status and safe next steps

The current Owner console work is an early implementation slice: it queues bounded requests and requires the configured immutable `OWNER_USER_ID` (database primary key), staff/superuser status, verified OTP and fresh reauthentication. The runtime authorization check and regression tests now fail closed when that ID is absent, malformed or mismatched, and a username change does not change the bound identity. Deployment configuration remains intentionally unset in source control and must be resolved from the protected database; this code change does not identify the live Owner account. It does **not** yet implement WebAuthn registration/device binding or complete account recovery. The current branch and PR must remain Draft until the new controls and tests are complete and all exact-head checks pass.

Recommended order:
1. Add this benchmark as the security-board baseline and map each target control to a test.
2. Replace mutable-username-only binding with immutable Owner ID and a safe deployment bootstrap check.
3. Implement WebAuthn registration/revocation and device inventory, with migration and adversarial tests.
4. Add server-side action authorization and test all critical-operation bypasses.
5. Finish privacy-safe audit logging, recovery controls, and exact-head CI.
6. Only after independent review and explicit SHA approval, consider deployment. No live migration or account role change is part of this research update.
