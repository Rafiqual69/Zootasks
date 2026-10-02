# AI Trust Graph & Delegation Chain

NIST's 2026 agent-identity work raises least-privilege authorization, proof of authority, delegation, human-in-the-loop binding, auditing and non-repudiation as key design questions. A2A likewise requires server-side authorization based on authenticated identity and scoped skills/actions/data policies. citeturn0search0turn0search36turn0search1

## ZooTasks model

`Owner/Root -> Executive Agent -> Specialist Agent -> Tool/Operation`

Every child link must bind to the previous delegation digest, use the previous subject as issuer, use subsets of parent actions/tools/destinations, and use no larger call budget. Any mismatch or privilege expansion fails closed.

## Trust graph boundary

Source attestation, provider authorization, Agent Cards, privacy approval and delegation are separate layers. Passing one layer never silently grants the next.

## Security invariant

A downstream agent may narrow authority but cannot amplify it. This limits the impact of a compromised or prompt-injected intermediary.

The module is network-free and does not mint credentials. Credential issuance, authentication and transport security remain separate infrastructure responsibilities.
