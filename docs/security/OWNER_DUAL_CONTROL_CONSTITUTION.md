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
