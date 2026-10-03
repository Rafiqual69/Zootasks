# ZooTasks AI Integration Boundary

## Status
Design-only. No production AI provider is configured or invoked.

## Purpose
Define the technical boundary for AI-SYS-001 before any provider SDK or runtime integration is introduced.

## Required architecture

Application -> AI Gateway -> explicitly allowlisted provider/model

The AI Gateway must:
- accept only approved capability IDs;
- construct prompts from an allowlisted/minimized field set;
- never receive secrets, authentication material, wallet balances, withdrawal records, payment credentials, or unnecessary identity data;
- enforce request size, timeout, rate, concurrency, and budget limits;
- attach capability ID, provider, model/version, prompt version, and correlation ID to the request context;
- validate structured output before returning it to application code;
- return a controlled failure when provider/model/configuration is not approved.

## Provider/model isolation

Provider and model identifiers are configuration, not user input.

A production configuration must explicitly identify:
- provider;
- model;
- model version or immutable release identifier where supported;
- endpoint;
- credential reference;
- timeout;
- request-size limit;
- output-size limit;
- rate/concurrency limit;
- budget;
- prompt/system-instruction version.

Unknown provider/model combinations are denied by default.

## Authorization boundary

The AI Gateway has no Django permission to mutate:
- wallet balances;
- reserved balances;
- WalletTransaction records;
- withdrawal status/payment state;
- promotion funding or payout state;
- task rewards/capacity/completion state;
- Owner authentication or RBAC.

Any AI suggestion that reaches an application workflow must pass normal Django authorization and deterministic service-layer validation.

## Output contract

The first capability should return only a bounded suggestion object:

- category suggestion;
- missing-information flags;
- quality-check suggestions;
- confidence/uncertainty indicator;
- non-binding rationale suitable for review.

Free-form output must not be interpreted as an instruction to execute an application action.

## Logging and privacy

Audit records should retain metadata needed for traceability without unnecessarily storing raw sensitive prompts or responses.

Minimum metadata:
- capability ID;
- request correlation ID;
- provider/model/version;
- prompt version;
- timestamp;
- result class;
- validation outcome;
- failure category.

Raw content retention requires a separate privacy/retention decision.

## Rollback

AI use must be disableable by configuration without removing or weakening the deterministic application workflow. Provider failure must not block normal non-AI task operation where AI assistance is optional.
