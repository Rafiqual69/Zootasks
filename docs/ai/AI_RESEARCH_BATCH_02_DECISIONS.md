# ZooTasks AI Research Batch 02 — Decisions

Date: 2026-10-02
Status: research/design; implementation gates remain closed for production AI.

## Research scope

This batch reviewed current public material from AI-agent security, AI governance, human-evaluation, crowdsourcing, and freelance/task marketplaces. The verified set now extends the initial five-source baseline; sources were selected for concrete workflow, quality, security, or monetization signals rather than generic AI news.

## Verified signals and ZooTasks implications

### 1. Deterministic security must sit outside the model
NIST's 2026 agent identity/authorization work emphasizes identification, authentication, authorization, and controls for agents that access data, tools, and applications.
OWASP's current GenAI guidance recommends enforcing privilege separation and authorization bounds independently from the LLM.
Decision: keep Agent Registry, Session Isolation, Data Boundary, Capability Budget, Tool Permission Gateway, Safety Firewall, and Evidence as deterministic controls. Do not replace them with prompts.

### 2. Human evaluation is a real marketplace category
Prolific currently offers specialized AI Taskers, human evaluation, domain experts, preference data, and API-driven task workflows. Qualification and quality controls are part of the operating model.
Decision: R04 AI Evaluation Tasks remains a viable design candidate. Initial version must use synthetic/public-data or client-approved non-sensitive data. Qualification and reward eligibility remain deterministic.

### 3. Layered QA is a recurring pattern
Appen describes calibration, independent review, statistical sampling, and reviewer assignment. TELUS Digital describes programmatic QA plus human validation and contributor qualification. Toloka describes multi-stage quality controls, exams, overlap/consensus, and human review. Scale describes generation, RLHF, red teaming, and evaluation loops. Clickworker describes human generation, annotation, validation, and evaluation.
Decision: use a Quality Ladder + Verification Bounty combination rather than a single AI score. AI quality suggestions remain advisory.

### 4. Qualification before higher-value work is commercially validated
Prolific uses assessment for AI Taskers. Toloka uses training and exams before production tasks. OneForma describes credential paths for higher-paying specialized work.
Decision: R02 Quality Ladder becomes the first candidate earning-feature specification. Higher-value eligibility must come from deterministic qualification records and measurable quality history.

### 5. Research/data collection is a marketplace service
Clickworker publicly describes web research, competitive analysis, surveys, store checks, data validation, and AI training-data workflows.
Decision: R05 Research-to-Task Pipeline is an architectural candidate. Client objectives may be decomposed into bounded tasks; client budgets and rewards remain deterministic application logic.

### 6. Revenue should be attached to verifiable value
MTurk separates worker rewards from marketplace fees and uses approval before earnings become available. PeoplePerHour exposes AI service categories and price bands. Contra combines opportunity discovery with project/payment management. Toptal uses a curated expert network.
Decision: revenue experiments should attach to a concrete service boundary: marketplace fee, verification/QA fee, enterprise orchestration/API fee, privacy-minimized evidence/export fee, or specialized AI-evaluation program fee. Unit economics and fraud-loss assumptions must be tested first.

## ZooTasks Quality Ladder v0.1

Worker state: NEW -> QUALIFIED -> TRUSTED -> SPECIALIST.
Transitions require qualification assessment, a minimum completed-task sample, deterministic quality metrics, independent verification where required, fraud/abuse checks, and cooldown/review rules for anomalies.
AI may suggest task category or non-binding quality review signals. AI may not grant/revoke wallet funds, approve withdrawals, alter promotion liabilities, change permissions, or change Owner identity/authentication.

## Verification Bounty v0.1

1. Worker A submits.
2. Deterministic rules select a bounded verification task.
3. Worker B independently reviews against a fixed rubric.
4. Disagreement routes to deterministic escalation or an authorized human reviewer.
5. Reward calculation is deterministic.
6. Evidence receipt stores minimal metadata.

Before implementation: prevent self-verification, add duplicate/collusion controls, bound verifier frequency, cap rewards, retain audit trail, define dispute/reversal policy, and minimize evidence data.

## Proof-Carrying Task v0.1

Evidence chain: task_version -> worker_submission_id -> deterministic_checks -> verifier_decision -> evidence_receipt.
Evidence must exclude passwords, API keys/tokens, payment credentials, raw private identity data, raw wallet balances, unrestricted model output, and unnecessary task content.

## Security decision

AI-SYS-001 remains the baseline control plane. No provider/network adapter is enabled. No new tool permission is granted.

## Next implementation order

1. Finish current Security Gate.
2. Preserve green AI Evaluation evidence as CI-generated artifact.
3. Specify deterministic Quality Ladder data model and tests.
4. Specify Verification Bounty policy and anti-collusion tests.
5. Add synthetic evaluation cases for quality-routing and escalation boundaries.
6. Only after those gates are green, prototype a non-financial AI task-routing assistant.

Production AI remains disabled until the complete release gate is explicitly satisfied.