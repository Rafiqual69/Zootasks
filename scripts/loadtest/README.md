# Controlled read-only load smoke test

This harness is a **small, opt-in smoke test**, not proof of 10-million-session capacity. It sends only unauthenticated HTTP GET requests to one configured path; it does not submit forms, authenticate, mutate wallet/task/promotion data, or follow more than three redirects.

## Safety requirements

- Run only against an environment you own or are explicitly authorized to test.
- Prefer an isolated staging deployment with synthetic data.
- Do not point this test at production without a separately approved test window, provider approval, monitoring, and an agreed stop procedure.
- Start with the default ramp (maximum 30 virtual users). Do not increase it until the operator reviews service/database limits and monitoring.
- The script requires an explicit opt-in flag and requires HTTPS except for an explicitly allowed localhost target.
- The default path is `/`; verify the selected path is a safe read-only endpoint before running. Do not set a path that triggers actions.

## Prerequisites

Install k6 using its official installation instructions: https://grafana.com/docs/k6/latest/set-up/install-k6/

## Example: local development only

From the repository root, after starting the app locally:

```bash
LOAD_TEST_AUTHORIZED=YES \
ALLOW_LOCAL_HTTP=YES \
BASE_URL=http://127.0.0.1:8000 \
READ_PATH=/ \
k6 run scripts/loadtest/public_read_smoke.js
```

## Example: authorized HTTPS staging

```bash
LOAD_TEST_AUTHORIZED=YES \
BASE_URL=https://staging.example.invalid \
READ_PATH=/ \
k6 run scripts/loadtest/public_read_smoke.js
```

Replace the example host with the exact staging host you are authorized to test. Do not include tokens, cookies, credentials, personal data, or financial records in environment variables or test output.

## Interpreting results

The script uses preliminary smoke thresholds of less than 1% failed requests and p95 latency under 1.5 seconds. These are starter thresholds, not approved production SLOs. A threshold failure is a signal to stop and investigate—not a reason to increase load.

Record the exact commit SHA, environment/topology, region, test window, k6 version, request path, achieved request rate, p50/p95/p99 latency, error rate, CPU/memory, database connection usage, queue lag, and cost. Redact hostnames or telemetry where disclosure would reveal private infrastructure.

## Not covered

This test does not exercise authenticated sessions, write paths, financial concurrency, WebAuthn, failover, geographic distribution, long-lived connections, or 10-million-user workloads. Those require separately designed and authorized test plans, synthetic data, capacity limits, and independent review.
