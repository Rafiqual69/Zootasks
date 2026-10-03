# ZooTasks Principal Readiness — Restore Point 4829340

## Baseline

The principal implementation continues from restore point `4829340` on branch `feat/ai-runtime-approval-gate`. No rebuild or reset is required.

## Security and Owner boundary

- Canonical active Owner remains the trust anchor.
- Owner login remains password + confirmed TOTP + Owner policy constrained.
- Owner email verification uses hashed, expiring, single-use tokens.
- Verification requests are Owner-only, CSRF-protected POST actions, with cooldown enforcement.
- The verification center exposes status and controlled actions without exposing raw verification tokens.
- Social OAuth state is random, hashed at rest, provider-bound, expiring and single-use.
- OAuth provider endpoints are HTTPS/allowlist constrained and redirects are blocked by the exchange client.
- Financial authority remains outside the verification center.

## Financial integrity boundary

AI and Owner verification code must not mutate wallet balances, withdrawal state, promotion payouts, task rewards or financial ledger records. Those operations remain deterministic application workflows.

## AI principal boundary

Production AI remains disabled by default.

Implemented deterministic controls include:

- capability allowlists and deny-by-default authorization;
- hard-zero external side-effect budgets for registered design-stage agents;
- capability input/output/tool budgets;
- action taxonomy with explicit impact classes;
- adversarial regression memory;
- provider offer normalization and quarantine;
- privacy/retention gate;
- policy evidence bundle and tamper-evident audit ledger;
- release TEVV gate;
- runtime trust monitoring;
- incident response and safe rollback state machine;
- scoped delegation and non-escalating trust boundaries.

The first planned production capability remains `AI-SYS-001 — Task Classification & Quality Assistance`.

It may suggest classifications and quality issues for human/admin review. It may not approve claims, alter rewards, mutate wallets, approve/pay withdrawals, release promotion funds, change permissions, authenticate the Owner, bind identity, or activate production AI.

## Evidence position

E1 governance and E2 risk artifacts are present.

E3 technical controls are implemented in deterministic code and architecture artifacts.

E4 regression/adversarial/security evidence is implemented, but provider/model production evaluation is still pending.

E5 deterministic monitoring/rollback controls are implemented and tested; live production operational evidence is still required.

E6 deterministic privacy controls are implemented and tested; provider-specific privacy, transfer, retention and data-subject review is still required.

## Release rule

No production AI provider/model is activated by this branch merely because tests pass. Production activation requires an explicit approved release evidence bundle, completed evaluation, privacy review, operational monitoring/rollback evidence and authorized release decision.

## Restore discipline

Future work must preserve this boundary and continue incrementally from the latest verified commit. Wallet, withdrawal, promotion and Owner authorization paths require dedicated regression coverage before modification.
