# ZooTasks AI Risk Register — Initial Baseline

| ID | Risk | Initial control | Evidence |
|---|---|---|---|
| AI-001 | Prompt injection causes unauthorized behavior | Treat model instructions and retrieved/external content as untrusted; enforce application authorization outside the model | Security tests + code review |
| AI-002 | Sensitive information disclosure | Data minimization, secret redaction, provider allowlist and logging policy | Data-flow review |
| AI-003 | Unsafe/inaccurate model output | Structured output validation and deterministic business rules | Evaluation + regression tests |
| AI-004 | AI directly changes financial state | AI cannot bypass wallet/task/promotion services or authorization boundaries | Finance integration tests |
| AI-005 | Model/provider supply-chain change | Version/provider inventory and controlled release | Change records |
| AI-006 | Model denial of service / uncontrolled cost | Rate, token, concurrency and budget limits | Monitoring |
| AI-007 | Data/model poisoning | Controlled datasets, provenance and review | Dataset evidence |
| AI-008 | Privacy/regulatory non-compliance | Purpose limitation, minimization, retention and access controls | Privacy review |
| AI-009 | Excessive automation of high-impact decisions | Risk-based human review and deterministic policy gates | Approval records |
| AI-010 | AI incident not detected | Security/quality/cost monitoring and incident response | Alert/incident logs |

## Risk scoring

Before each production AI release, score each applicable risk for likelihood and impact using the project's approved risk methodology. Record residual risk after controls and identify an accountable owner.

A risk is not considered closed merely because a mitigation exists; effectiveness must be tested and evidenced.
