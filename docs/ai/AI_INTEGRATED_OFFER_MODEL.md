# ZooTasks Integrated AI Offer Model

## Purpose
ZooTasks is designed as an integration layer that can discover, qualify, normalize, and present legitimate AI-related work from multiple providers through one worker-facing task model.

The target is broad coverage, not a claim that every provider or every offer can be accessed. Access depends on provider authorization, geography, eligibility, contracts, API/feed availability, terms, and task-specific restrictions.

## Provider classes
1. API/partner providers — authorized machine integration.
2. Public task providers — publicly available offers that permit participation.
3. Workforce platforms — contributor qualification and project matching.
4. Enterprise/managed providers — onboarding or contractual integration required.
5. Quarantined sources — discovered but not yet verified or authorized.

Unverified or restricted sources never enter the executable task pool.

## Canonical offer schema
Every imported offer should normalize into:
- provider identity and source
- provider authorization status
- acquisition route
- source URL/API identifier
- region and eligibility rules
- task category and skill requirements
- reward/currency and payment terms
- input/output data sensitivity
- retention/processing restrictions
- terms and expiry
- qualification requirements
- verification/QA method
- adapter and schema version
- synchronization status
- provenance and audit references
- risk/quarantine state

## Canonical task categories
- data annotation and labeling
- image/video/audio/text evaluation
- LLM response evaluation
- preference ranking / RLHF-style work
- prompt and instruction evaluation
- search/relevance evaluation
- translation and multilingual evaluation
- AI safety/red-team evaluation
- agent trajectory/task evaluation
- data collection and validation
- AI output verification
- human-in-the-loop review

## Worker experience
A worker should interact primarily with ZooTasks:
1. profile skills/languages/eligibility
2. see normalized offers
3. qualify where required
4. accept an eligible task
5. complete it in an approved environment
6. submit evidence/result
7. deterministic QA evaluates the submission
8. provider-specific settlement is reconciled before ZooTasks financial settlement

Provider credentials, private keys, and restricted provider data must never be exposed to workers or general-purpose agents.

## Adapter boundary
Each provider adapter must define:
- endpoint/source allowlist
- authentication boundary
- request/response schema
- rate and concurrency limits
- idempotency strategy
- timeout/retry/circuit-breaker behavior
- data classification
- provider terms/version
- audit events
- failure and quarantine behavior

No adapter may directly mutate ZooTasks wallet balances. Settlement remains inside the deterministic financial core.

## Acquisition boundary
Where a provider does not expose an approved automation interface, ZooTasks may research the provider and prepare an outreach proposal. Sending external communication requires a separate authorization boundary and human approval. No scraping around access controls, CAPTCHA bypass, credential harvesting, impersonation, or unsolicited bulk messaging is permitted.

## Evidence basis
The model reflects current market patterns: Appen describes AI-data platforms spanning annotation, LLM fine-tuning, red teaming and search relevance; TELUS Digital describes search, LLM evaluation, localization and human quality workflows; Toloka describes evaluation, red teaming, data collection and automated QA; OneForma describes annotation, data collection, judging, transcription and translation. These examples demonstrate why a normalized multi-category offer layer is more useful than a single-task connector.

## Security invariant
Discovery does not equal authorization.
Offer visibility does not equal acceptance eligibility.
Acceptance does not equal payment.
AI recommendation does not equal financial authorization.
All high-impact or irreversible actions remain subject to deterministic policy and authorized human approval.
