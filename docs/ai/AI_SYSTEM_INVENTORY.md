# ZooTasks AI System Inventory

No production AI system is approved yet.

| System ID | Agent ID | Capability | Provider/model | Purpose | Data class | Risk class | Human oversight | Status |
|---|---|---|---|---|---|---|---|---|
| AI-SYS-001 | ZT-AGENT-001 | Task Classification & Quality Assistance | TBD | Suggest task category and identify missing/ambiguous instructions for human/admin review | task_content_minimal | Low/Moderate — pending formal assessment | Human/admin review; no autonomous financial or identity action | Design |

## Approval state

AI-SYS-001 is a design candidate only. ZT-AGENT-001 is a registered design-time identity with least-privilege policy. Provider, model, version, evaluation dataset, thresholds, and production approval remain TBD.

## Rule

No model, agent, autonomous workflow, AI API, embedding system, or automated decision service becomes a production component until it is entered here and passes the AI lifecycle gate.

## Agent boundary

ZT-AGENT-001 is bound to AI-SYS-001 only. Its approved data class is task_content_minimal, its tool allowlist is empty, and its maximum autonomy is suggestion_only. The agent registry is deny-by-default and does not grant application permissions.

## Data boundary

The first candidate should receive only the minimum task fields needed for classification/quality assistance. Worker identity, wallet balances, withdrawal data, secrets, authentication material, and unnecessary personal data are out of scope.

## Change control

A provider, model, model version, prompt version, system instruction, data source, agent policy, tool permission, or materially changed AI workflow requires inventory review and the applicable lifecycle gates again.
