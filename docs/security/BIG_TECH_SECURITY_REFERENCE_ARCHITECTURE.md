# ZooTasks Big-Tech-Inspired Security Reference Architecture

Status: Normative design reference (1.0.0)
Important: This document uses publicly documented security properties of Google, Meta/Facebook/Instagram, and Telegram. It does not claim knowledge of proprietary internal systems or equivalence.

## 1. Security objective
ZooTasks should reproduce security properties, not proprietary implementations:
Identity assurance -> risk detection -> session binding -> least privilege -> object/field authorization -> business invariant -> atomic effect -> audit evidence -> detection/response

## 2. Research-derived patterns
### Google
Publicly documented controls include passkeys/FIDO-based phishing-resistant authentication, stronger protection for high-risk accounts, and additional verification for sensitive account changes.
ZooTasks: WebAuthn/passkeys preferred; TOTP bounded as fallback/step-up; recent re-authentication for sensitive changes; trusted authenticator before changing recovery/authentication factors; stronger Owner assurance; session binding/rotation/expiry/revocation; recovery cannot silently reduce assurance.

### Meta / Facebook / Instagram
Publicly documented controls include 2FA, login alerts/security checkups, adaptive recovery, security-key support, data minimization, de-identified authentication research, and cryptographic monitoring.
ZooTasks: security-event monitoring; risk-aware step-up; active-session visibility/revocation; recovery separated from normal authentication; minimum necessary collection/response/logging/export; cryptographic/dependency monitoring; explicit classification and response allowlists.

### Telegram
Publicly documented controls include 2-Step Verification, passkeys, active-session/security controls, a separated test environment for security research, open-source clients/reproducible builds, and a vulnerability bounty program.
ZooTasks: Account Security Center with session/device inventory and revocation; passkey/recovery controls; dedicated non-production security testing; no production data in security testing; responsible disclosure and authorized security triage.

## 3. Authentication assurance tiers
A0: anonymous/public data only.
A1: normal authenticated worker/user session.
A2: strong authentication plus recent re-authentication for account/security changes.
A3: privileged financial/security operations; phishing-resistant authentication preferred/required, recent re-authentication, explicit role/object authorization, separation of duties and audit evidence.
Authentication success never equals authorization.

## 4. Session security
Every authenticated session requires unpredictable server-side identifiers, HTTPS in production, appropriate Secure/HttpOnly/SameSite cookies, rotation after authentication/privilege changes, idle and absolute limits, explicit revocation, server-side security-state binding, recent-authentication state for privileged actions, and no raw session IDs in logs.

## 5. Recovery security
Recovery is a separate authentication pathway. Changing MFA/passkeys/recovery factors requires recent authentication. Recovery is audited, suspicious recovery may be delayed/reviewed, recovery never directly grants financial authority, and recovered accounts may require step-up before sensitive actions.

## 6. Privileged boundaries
Owner: explicit security/configuration authority with recent re-authentication and strong authenticator.
Finance: approve/reject only where explicitly granted.
Finance Payer: payment execution only; cannot approve the same withdrawal.
Worker: own resources only; no financial administration.
AI: decision support only; no direct financial/security mutation or privilege escalation.

## 7. Risk-adaptive security
Signals may include new device/session, repeated authentication failures, recent credential/recovery changes, unusual high-impact operations and repeated authorization failures.
Responses may include step-up authentication, session revalidation, action delay, session revocation, security notification and human review.
Risk scoring is never authority to move money.

## 8. Data minimization
Classification: public -> internal -> confidential -> financial_critical -> security_critical.
Every endpoint/admin view requires response allowlists, object filtering, field minimization, no sensitive values in URLs, no credentials/tokens/payment identifiers in logs, no raw proof in generic search, explicit export authorization, enumeration-resistant failures, and masked financial identifiers by default.

## 9. Financial integrity
Every financial workflow: PDP -> PEP -> state validation -> object lock -> balance invariant -> idempotency -> atomic mutation -> immutable evidence.
Required: DB-enforced operation identity where feasible; replay/duplicate protection; PostgreSQL concurrency tests; valid state transitions; approval/payment separation; balance/reserved-balance invariants; reconciliation evidence.
UI success is never ledger truth.

## 10. AI boundary
AI proposal -> validation -> PDP -> approved service action -> business invariant -> audit.
AI cannot mutate wallet balances, create financial ledger effects, approve/pay withdrawals, process promotion payouts, change privileged roles, bypass authentication/authorization, or disable security controls.

## 11. Detection and evidence
Security events should contain timestamp, actor category/pseudonymous ID, event type, resource/action, decision/result, correlation ID and safe reason/category.
Never log passwords, tokens, session cookies, OTP secrets, WebAuthn challenges, private keys, API secrets or raw payment identifiers.

## 12. Continuous assurance
Every security-sensitive change requires threat modeling; positive/negative authorization tests; ownership tests; state-transition tests; field/data-leakage tests; replay/idempotency tests; concurrency tests where applicable; logging-boundary tests; security and financial regression; Django checks; CI evidence; review before merge.

## 13. Target architecture
Client -> TLS/edge controls -> authentication -> session security -> PDP -> PEP -> object/field authorization -> business invariant service -> transaction/idempotency/concurrency controls -> database -> immutable security/financial evidence -> monitoring/response.
AI connects only through a bounded capability gateway.

## 14. Implementation roadmap
Phase 1 Identity: Owner WebAuthn/passkey, TOTP fallback, recent re-auth, session inventory/revocation, recovery threat model.
Phase 2 Authorization/Data: PDP/PEP coverage, admin read boundaries, object ownership, field allowlists, enumeration resistance, exports.
Phase 3 Finance: withdrawal operation identity, DB idempotency, PostgreSQL concurrency, state machine, reconciliation.
Phase 4 Abuse/Detection: authentication rate limits, adaptive step-up, suspicious-session controls, security notifications.
Phase 5 Supply Chain/Deployment: dependency monitoring, secret scanning, reproducible/security-reviewed builds, HTTPS production hardening, backup/recovery security tests.
Phase 6 Assurance: OWASP ASVS mapping, NIST identity/session mapping, authorized penetration testing, responsible disclosure, periodic architecture review.

## 15. Non-negotiable rules
Unknown = deny.
Authentication != authorization.
Strong authentication != financial authority.
AI output != authority.
Role != object ownership.
Approval != payment.
UI success != ledger truth.
Logs != secret storage.
Production data != test data.
Policy declaration != enforcement.
Historical PASS != current PASS.

## 16. Research basis
Public sources reviewed: Google Account Security/Google Security Blog; Meta Engineering/Facebook security documentation; Telegram FAQ/Bug Bounty; OWASP ASVS 5.0; NIST SP 800-63B-4.
Implementation sequence: Research -> threat model -> controlled change -> targeted tests -> security/financial regression -> CI evidence -> review -> deployment verification.