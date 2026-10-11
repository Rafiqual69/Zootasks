# ZooTasks Owner Dual-Control Security Constitution

**Policy ID:** ZT-OWNER-DUAL-CONTROL
**Version:** 1.0.0
**Status:** Proposed production-readiness control
**Activation:** Development remains compatible with the currently authorized Owner device; mandatory dual approval activates only at the production security-freeze gate.

## 1. Purpose
Prevent a single compromised Owner credential, device, session, application instance, CI token, AI agent, or web-server foothold from independently making critical production changes.

## 2. Core rule
For every operation classified as dual-control, one Owner device approval is insufficient. Execution requires two independent Owner-device-bound approvals for the exact action, target, scope, and material parameters.

Two sessions on the same device, two browser tabs, or two approvals derived from one credential do not satisfy this rule.

## 3. Protected operations
At minimum:
- production deployment or rollback;
- security policy/Constitution changes;
- Owner/admin/privilege changes;
- authentication/MFA/security-control weakening;
- production environment/security configuration changes;
- database schema/migration promotion;
- production database restore/recovery promotion;
- financial ledger/balance mutation;
- withdrawal approval/payment and other money movement;
- secret/key rotation with operational impact;
- network/public-exposure changes;
- irreversible deletion/retention actions;
- break-glass security operations.

## 4. Independent authorization
Each Owner device must have an independent device identity and phishing-resistant authentication/approval credential. Approval must be:
- bound to the exact action and target;
- short-lived;
- nonce/replay protected;
- invalidated if material parameters change;
- auditable without storing secrets;
- revocable independently;
- evaluated again at execution time.

An application login is not itself an approval key.

## 5. Fail-closed behavior
Deny when:
- either approval is missing, expired, revoked, duplicated, or ambiguous;
- device identity cannot be independently established;
- action/target/parameters differ from the approved request;
- policy validation fails;
- risk context changes materially;
- required CI/review/security gates are missing or failed;
- audit evidence cannot be safely recorded where mandatory;
- one device/session is suspected compromised.

## 6. Current-device compatibility
Before production activation, the existing running Owner device remains usable for normal development operations that do not require dual control. It must not be silently removed or disrupted by introducing this policy.

Production activation is a separate explicit gate. Once activated, dual-control operations cannot be completed by the current device alone.

## 7. Attack containment
A website compromise, stolen session, compromised CI runner, compromised AI/tool, or single Owner-device compromise must not provide dual-control authority. The application/runtime must never receive the private approval keys for both devices.

During an active security incident, critical writes may be frozen and pending approvals invalidated.

## 8. Human and automation boundaries
AI, bots, CI/CD and background automation may prepare or validate a request but cannot manufacture, borrow, replay, or substitute Owner approvals. Automation must not bypass dual control.

## 9. Audit and privacy
Record safe metadata: request/event ID, policy version, device identity reference, action class, target reference, timestamps, decision, and outcome. Never record passwords, private keys, OTP secrets, session cookies, approval signatures, raw bank/payment data, or unnecessary personal data.

## 10. Testing contract
Before production activation, tests must demonstrate:
1. Device-1 alone => DENY.
2. Device-2 alone => DENY.
3. Same credential presented twice => DENY.
4. Replayed approval => DENY.
5. Expired/revoked approval => DENY.
6. Changed target/action/amount/parameters => DENY.
7. Compromised application session => DENY for dual-control actions.
8. Compromised CI/AI/tool => DENY for dual-control actions.
9. Valid independent Device-1 + Device-2 approvals => eligible to continue, subject to all other security gates.
10. Incident/freeze state => DENY.

## 11. Activation gate
This policy does not by itself activate production dual control. Activation requires:
- independently reviewed implementation;
- machine-readable policy;
- protected CI and regression evidence;
- phishing-resistant device enrollment;
- recovery/revocation procedure;
- incident/freeze procedure;
- owner acceptance of both device identities;
- production readiness gate PASS.

Unknown or unverified activation state is treated as DENY for protected production operations.

## 12. Security rule
**One compromised trust anchor must never be enough to authorize a protected production change.**


## 10. Single primary Owner input device

The Owner may use one enrolled, trusted primary device as the normal command and input surface for the ZooTasks control plane. From that device, the Owner may submit instructions, drafts, research requests, configuration proposals, monitoring queries, and approval requests. The server must authenticate the Owner and authorize each operation independently; device identity alone is not authorization.

The primary-device feature must:
- enroll only after a fresh phishing-resistant WebAuthn/passkey ceremony and explicit Owner confirmation;
- store only public credential metadata and a non-secret device reference, never authenticator private keys or recovery secrets;
- bind each session to the authenticated Owner, device/credential, expiry, CSRF protections, and risk signals;
- allow a single primary device to prepare and submit requests without granting background agents or the device blanket write privileges;
- support explicit revocation, device-loss recovery, session invalidation, audit events, rate limits, and notification of primary-device changes;
- never accept a primary-device ID supplied by an untrusted request as proof of identity.

The single-device input surface does not waive independent authorization for protected production operations listed in this Constitution. Financial movement, privilege/security changes, production deployment/migrations, destructive operations, and incident break-glass remain blocked until their required approval and release gates pass. If the primary device is suspected compromised, freeze privileged mutations and revoke its sessions/credential.

This is a control-plane requirement, not a claim that an Owner device has already been enrolled. Enrollment and the user-facing control surface must be implemented and tested before the feature can be marked active.


## 11. Staged Owner input rollout: Device 1 first, Device 2 later

**Requested operating sequence:** the Owner uses one trusted primary device now to enter and submit all ordinary instructions; a second independently enrolled Owner device will be added later. This is a staged onboarding mode, not a dual-control bypass.

### Phase A — single-device input mode

The primary device may be used to enter and submit all ordinary control-plane inputs, including research prompts, task drafts, content drafts, configuration proposals, workflow requests, monitoring queries, and requests for privileged actions. The server must still authenticate the Owner and authorize every request by action and scope. Inputs are untrusted data until validated; AI agents may prepare proposals but cannot self-authorize them.

Allowed in Phase A:
- create, edit, and submit ordinary drafts/proposals;
- start read-only research, diagnostics, and monitoring;
- queue a privileged request with a visible pending/blocked status;
- configure non-production settings that do not weaken security or grant privilege;
- view sanitized audit events and request status.

Not allowed with Device 1 alone:
- production deployment, rollback, schema migration, or production restore;
- payment, withdrawal, balance/ledger, budget, or other money movement/mutation;
- Owner/admin/role/permission changes;
- changing authentication, MFA, security policy, secrets, network exposure, or audit controls;
- destructive deletion, incident break-glass, or disabling required safeguards.

These requests may be prepared and queued, but execution must remain denied until the second independent device is enrolled and the dual-control ceremony is implemented, tested, and activated through the explicit production-readiness gate. A queued request must not auto-execute when Device 2 is later enrolled; the Owner must review and approve the exact current request after enrollment.

### Phase B — second-device enrollment

Enrollment of Device 2 requires fresh phishing-resistant WebAuthn/passkey verification, explicit Owner confirmation, independent device and credential identity, revocation/recovery readiness, and an auditable enrollment event. Never accept a device identity or approval fact supplied only by the client. Device 2 enrollment does not itself activate production privileges.

### Required acceptance tests

1. Device 1 can submit an ordinary draft and read-only request after authentication.
2. Device 1 cannot directly execute any protected operation listed above.
3. A privileged request from Device 1 remains pending and has no side effects.
4. Device 2 enrollment cannot automatically release or execute previously queued requests.
5. Device 1 and Device 2 approvals must bind to the same current action, target, scope, and material parameters.
6. Revoked, expired, replayed, same-device, same-credential, changed-request, and incident-freeze cases deny.
7. Device loss/compromise supports revocation and session invalidation without weakening the dual-control requirement.
8. Audit records contain minimal non-secret metadata only; no passwords, private keys, passkey secrets, session cookies, recovery codes, or raw payment data.
9. All Phase A/Phase B behavior is verified in regression tests before the user-facing feature is marked active.

**Implementation status:** policy/requirements only. This document change does not claim the user-facing primary-device input surface or second-device enrollment flow is already implemented. Production remains blocked until the runtime endpoints, UI, tests, and independent review pass.
