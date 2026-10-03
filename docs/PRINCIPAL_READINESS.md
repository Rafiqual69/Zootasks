# ZooTasks Principal Readiness — Restore Point 4829340

## Baseline
The principal implementation continues incrementally from restore point `4829340` on `feat/ai-runtime-approval-gate`.

## Security and Owner boundary
- Canonical active Owner remains the trust anchor.
- Owner login remains password + confirmed TOTP + Owner policy constrained.
- Owner email verification uses hashed, expiring, single-use tokens.
- Verification requests are Owner-only and CSRF-protected.
- The verification center exposes status and controlled actions without exposing raw verification tokens.
- Social OAuth state is random, hashed at rest, provider-bound, expiring and single-use.
- OAuth endpoints are HTTPS/allowlist constrained and redirect-following is blocked.
- Financial authority remains outside the verification center.
- Verification-center email requests route through one Owner-only, POST-only, CSRF-protected action.

## Financial integrity boundary
AI and Owner verification code must not mutate wallet balances, withdrawal state, promotion payouts, task rewards or financial ledger records.
- Withdrawal requests reserve balance atomically and cannot report success when reservation fails.
- Promotion claims do not increment completion counters; payout increments completion exactly once and pauses at capacity.
- Promotion claim admission accounts for completed and active liability so declared budget cannot be over-committed.
- Regression coverage exists for withdrawal reservation, promotion lifecycle, payout idempotency and budget exposure.

## AI principal boundary
Production AI remains disabled by default. Deterministic controls include capability allowlists, hard-zero side-effect budgets, capability budgets, action taxonomy, adversarial regression vectors, provider quarantine, privacy gating, policy evidence, tamper-evident audit, release TEVV, runtime monitoring, incident response/rollback, and scoped delegation.

The first planned capability remains `AI-SYS-001 — Task Classification & Quality Assistance`. It is limited to non-binding classification and quality suggestions for human/admin review and cannot approve claims, alter rewards, mutate wallets, approve/pay withdrawals, release promotion funds, change permissions, authenticate the Owner, bind identity, or activate production AI.

## Evidence position
- E1 governance and E2 risk artifacts: present.
- E3 technical controls: implemented in deterministic code and architecture artifacts.
- E4 regression/adversarial/security evidence: implemented; provider/model production evaluation remains pending.
- E5 monitoring/rollback controls: implemented and tested; live operational evidence remains required.
- E6 privacy controls: implemented and tested; provider-specific processing/transfer/retention review remains required.

## Release rule
Passing tests alone never activates production AI. Production activation requires an approved release evidence bundle, completed evaluation, privacy review, operational monitoring/rollback evidence, and an authorized release decision.

## Restore discipline
Continue from the latest verified commit. Wallet, withdrawal, promotion, and Owner authorization changes require dedicated regression coverage before modification.
