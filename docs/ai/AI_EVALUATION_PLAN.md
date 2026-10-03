# ZooTasks AI Evaluation Plan — AI-SYS-001

## Status
Design-stage evaluation plan. No production approval.

## Objective
Measure whether Task Classification & Quality Assistance is useful, robust, safe, and resistant to adversarial input before production consideration.

## Evaluation groups

### Functional
- Clear task descriptions.
- Ambiguous descriptions.
- Missing required instructions.
- Different task categories.
- Boundary cases between categories.

### Security
- Direct prompt injection.
- Indirect prompt injection embedded in task content.
- Attempts to request secrets or credentials.
- Attempts to trigger wallet/withdrawal/promotion actions.
- Attempts to override system constraints.
- Malformed and oversized inputs.
- Malicious output/schema manipulation.

### Privacy
- Task content containing accidental personal information.
- Secrets embedded in task text.
- Requests that attempt to expose worker identity or financial data.

Expected behavior: minimize/exclude unnecessary sensitive data and never disclose protected application data.

### Reliability
- Provider timeout.
- Provider unavailable.
- Invalid response.
- Unexpected model/version.
- Rate or budget limit reached.
- Repeated identical requests.

Expected behavior: controlled failure or deterministic fallback; no privileged action.

## Golden dataset

The production approval record must reference a versioned, reviewed evaluation dataset. Each case should have:
- case ID;
- input classification;
- expected safe behavior;
- expected output schema;
- security/privacy expectation;
- reviewer;
- dataset version.

Do not place real secrets, payment credentials, authentication material, or unnecessary personal data in the dataset.

## Release thresholds

Thresholds must be defined and approved before production evaluation. At minimum, a release candidate must demonstrate:
- zero successful privilege-escalation cases;
- zero direct financial-state mutation paths;
- zero secret/authentication-data disclosure cases;
- 100% schema validation for accepted outputs;
- controlled handling of provider failure cases;
- regression results no worse than the approved baseline for defined quality measures.

Quality thresholds are capability-specific and must not be invented after seeing results.

## Evidence

Store evaluation results with:
- system ID;
- provider/model/version;
- prompt version;
- dataset version;
- test runner version;
- timestamp;
- pass/fail counts;
- failed case IDs;
- reviewer/approval;
- remediation and re-test history.
