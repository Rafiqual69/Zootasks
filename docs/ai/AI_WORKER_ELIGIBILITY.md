# Deterministic AI Worker Eligibility

Worker matching is a separate gate from provider authorization and financial
settlement.

## Rules

- Only a canonical offer can be evaluated.
- A non-executable offer is never eligible.
- Region and language restrictions are checked explicitly.
- Required task skills must be present in the worker profile.
- Required qualifications are matched by an exact normalized qualification
  identifier; free-text qualification instructions are not interpreted by AI.
- Eligibility is advisory to the task workflow and does not accept a task,
  change task state, or mutate wallet balances.
- A future ranking/matching agent may recommend candidates, but deterministic
  eligibility remains authoritative.

## Fail-closed behavior

Unknown or unmet eligibility conditions produce an ineligible result rather
than an assumption of eligibility. This prevents an AI agent from converting
ambiguous provider requirements into worker access.

## Security boundary

The engine receives only the minimum profile attributes needed for matching.
It has no provider credentials, no wallet authority, no withdrawal authority,
no promotion authority, and no external side effects.
