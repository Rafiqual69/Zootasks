# AI Release TEVV Gate

NIST AI RMF says AI systems should be tested before deployment and regularly during operation, with documented test sets, metrics and TEVV details. It also emphasizes monitoring deployed systems and documenting safe-failure conditions. citeturn0search1turn0search6turn0search8

## Release evidence

A ZooTasks AI release candidate binds release identity, AI system identity, code revision, source revision digest, evaluation digest, policy evidence bundle digest, test digest, rollback reference, monitoring reference, and human approval reference when approved.

The complete release evidence is deterministically hashed.

## Gate states

`candidate -> quarantined` until approval evidence exists.

`approved -> approved_for_controlled_rollout` only when all required evidence is present and a human approval reference is bound.

This gate does not activate production AI. It only establishes that the release has reached controlled-rollout stage; a separate production activation gate remains required.

## Safety properties

- missing evaluation, test, rollback or monitoring evidence fails closed;
- changing bound release evidence changes the digest;
- approval is bound to the exact release evidence;
- production activation is not implied;
- financial authority is never granted by the release gate.
