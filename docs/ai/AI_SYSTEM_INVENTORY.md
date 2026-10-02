# ZooTasks AI System Inventory

No production AI system is approved yet.

| System ID | Capability | Provider/model | Purpose | Data class | Risk class | Human oversight | Status |
|---|---|---|---|---|---|---|---|
| AI-SYS-001 | Task Classification & Quality Assistance | TBD | Suggest task category and identify missing/ambiguous instructions for human/admin review | Task content only; minimize/remove identity and financial data | Low/Moderate — pending formal assessment | Human/admin review; no autonomous financial or identity action | Design |
| AI-SYS-002 | Executive AI Advisor / Orchestrator | TBD | Coordinate specialized agents and prepare evidence-based Owner briefings; no sovereign authority | Minimum necessary operational/task context; privileged financial, authentication and secrets data excluded | High — architecture only | Owner approval for high-impact actions; deterministic authorization remains outside AI | Design |

## Approval state
AI-SYS-001 is a design candidate only. Provider, model, version, evaluation dataset, thresholds, and production approval remain TBD.

## Rule
No model, agent, autonomous workflow, AI API, embedding system, or automated decision service becomes a production component until it is entered here and passes the AI lifecycle gate.

The Executive Agent is an orchestration/advisory capability only. It does not grant permissions and cannot override deterministic authorization.

## Data boundary
The first candidate should receive only the minimum task fields needed for classification/quality assistance. Worker identity, wallet balances, withdrawal data, secrets, authentication material, and unnecessary personal data are out of scope.

## Agent governance

Every agent must have an explicit allowlist for tools, data, destinations and action classes. Default access is deny. External content, tool output and inter-agent messages are treated as untrusted input until validated. High-impact or irreversible actions require the applicable human/authorization gate.

The planned Executive Agent may coordinate research, provider/offer acquisition, task normalization, QA and security agents, but production external outreach and provider integrations require separate capability inventory entries and approval.

## Change control
A provider, model, model version, prompt version, system instruction, data source, or materially changed AI workflow requires inventory review and the applicable lifecycle gates again.
