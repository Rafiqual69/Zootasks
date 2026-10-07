# Financial Workflow State & Invariant Specification

Status: security-board design gate
Branch: security/full-integrated-security-board-20261007
Baseline: 68daeca00fa3f031a20f54493c58341ae6832bb0

This document is a design gate for the next financial/workflow changes. It intentionally does not change runtime behavior.

## 1. Task capacity

Current behavior uses `Task.completed_workers` as a claim-time reservation counter. That prevents over-claiming under the existing parent-row lock, but it is not semantically a completed/approved count and rejected claims do not release the slot.

Required target semantics:

- `claimed`: capacity reserved, no earning ledger entry.
- `submitted`: capacity remains reserved, no earning ledger entry.
- `approved`: capacity remains consumed and exactly one matching earning ledger entry may exist.
- `rejected`: capacity reservation is released exactly once; no earning ledger entry.
- A worker may have at most one claim per task under the existing unique constraint.
- Concurrent claims must serialize on the task capacity authority; the invariant must hold after every committed transaction.
- A task must never expose or accept more active reservations than `max_workers`.

Implementation gate: introduce an explicit reservation representation (preferred) or formally redefine the existing counter before changing claim/reject behavior. Do not silently reinterpret `completed_workers`.

## 2. Promotion capacity and budget

Promotion has worker capacity and monetary budget. These are separate integrity dimensions.

Required target semantics:

- Worker capacity reservation follows the same claimed -> submitted -> approved/rejected lifecycle.
- `reward` is the amount credited for one approved promotion claim.
- `budget` is the maximum cumulative payout liability for the promotion unless a later business decision explicitly changes this definition.
- Approved promotion payouts must never exceed `budget`.
- Concurrent approvals must serialize on the promotion budget authority (promotion row or an equivalent reservation/ledger authority).
- For an approval of amount R, the committed state must satisfy:
  `approved_payout_total + R <= budget`.
- Rejected claims create no payout liability.
- Exactly one earning ledger entry may be associated with an approved promotion claim.
- Idempotent replay of an already approved claim must not create another ledger entry or increase cumulative payout.
- Existing dual-control execution authorization remains mandatory for protected production financial mutations.

Data migration gate: before enforcing `reward <= budget` or any cumulative-budget database invariant, audit existing promotion data and explicitly choose the invariant. Do not add a constraint that can invalidate legitimate legacy rows without a reconciliation plan.

## 3. Withdrawal state machine

Allowed forward transitions:

- `pending -> approved`
- `pending -> rejected`
- `approved -> paid`

Terminal states:

- `rejected` is immutable.
- `paid` is immutable.

Financial invariants:

- `amount >= 0` at database level.
- Approval does not debit the wallet; the existing reservation remains held.
- Rejection releases exactly the reserved amount once.
- Payment debits balance and reserved balance exactly once.
- A paid withdrawal has exactly one withdrawal ledger identity.
- A replay of payment is a no-op.
- A mismatched pre-existing ledger row blocks payment and requires reconciliation; it must never be silently treated as a valid debit.
- Approval and payment remain separated by permission and execution authorization.

A database status-transition constraint cannot generally express cross-row transition history by itself. Therefore the authoritative transition check remains in the transactionally locked application operation, with tests for every invalid transition and replay. Database constraints should cover row-local monetary invariants and operation identity.

## 4. Concurrency test matrix

Before changing production behavior, tests must cover at minimum:

1. Two workers racing for the last task slot: exactly one claim succeeds.
2. A rejected task claim releases its reservation exactly once.
3. Two promotion approvals racing for the final budget: only the amount within budget is approved/credited.
4. Replaying an approved promotion does not double-credit.
5. Negative withdrawal amount cannot be persisted.
6. pending -> approved and pending -> rejected are allowed only through authorized operations.
7. rejected -> paid, paid -> approved, and paid -> rejected are denied/no-op.
8. Two payment attempts cannot create two withdrawal ledger entries or two wallet debits.
9. Existing wallet idempotency and dual-control tests remain green.
10. PostgreSQL verification must be run because row locking and constraint behavior are production-relevant.

## 5. Migration/data-reconciliation gate

No local or production migration should be run merely because a migration exists.

Before migration:

- inspect current database state;
- identify legacy rows affected by each new invariant;
- produce a deterministic reconciliation rule;
- test migration on SQLite and PostgreSQL;
- verify `makemigrations --check --dry-run` is clean;
- run full regression and financial verification;
- preserve the backup branch `backup/security-board-20261007-68daeca`.

## 6. Security decision

Until these invariants and tests are implemented and verified, production activation remains blocked. Green CI on the existing baseline is evidence of regression safety for the current code, not approval of an unreconciled financial redesign.
