# ZooTasks Owner Panel & Earnings-First Marketplace Blueprint

**Status:** research/design proposal; not production implementation  
**Research date:** 2026-11-28  
**Scope:** public homepage, worker dashboard, task detail/claim/submit flow, owner operations panel, unit economics and security gates.

## 1. Product goal

Build a trustworthy task marketplace where workers can make an informed choice before spending time, task owners get reliable completion quality, and ZooTasks earns sustainably without relying on hidden fees or misleading earnings claims.

Success is not “highest commission.” It is repeat funded demand, quality-adjusted task completion, low fraud/dispute costs, transparent worker net earnings, and positive contribution margin after payment, support, fraud, tax and operating costs.

## 2. Benchmark set: 23 active platforms and standards

The active evidence set contains the 15 requested marketplace platforms, five engineering platforms (Linear, Supabase, Vercel, Cloudflare and GitHub), and three AI governance/security references (NIST AI RMF, OWASP Agent Control Standard and OWASP AISVS). The dated source register below records the checked date, source freshness, observed evidence and a separate ZooTasks hypothesis.

Amazon Mechanical Turk is excluded from this active set. It appears only in the discontinued-platform lesson after the register. No fee, payout threshold or policy from another country is assumed to apply in Bangladesh.

### Benchmark synthesis

- **Pricing:** disclose the payer, fee base, every known deduction and expected worker net before commitment. A competitor's fee model is evidence of its own policy, not evidence that the same model fits ZooTasks.
- **Trust:** verify funding and capacity from authoritative records before presenting a task as funded or available.
- **Earnings:** separate pending, approved, withdrawable and paid amounts; compare estimated duration with measured completion time.
- **Owner controls:** use role-scoped audit access, strong authentication, least privilege and exact-head release gates.
- **Evidence discipline:** source observations are facts about the cited page on the checked date; ZooTasks design implications remain hypotheses until measured.

## 3. Proposed website information architecture

### Public homepage
1. Clear value proposition: “Find verified tasks. See the reward before you start.”
2. Search/filter by category, expected duration, skill, eligibility and reward.
3. Real task cards only when backed by live, policy-approved data; otherwise label as illustrative examples.
4. Trust strip: how approval works, dispute process, payout methods supported in the user's country, and privacy controls.
5. Transparent fee example showing gross reward → platform/provider fees → estimated net reward.
6. FAQ and plain-language rules; no guaranteed-income, “risk-free profit” or fake scarcity claims.

### Worker dashboard (mobile-first)
- **Available tasks:** match score, required skills, estimated minutes, gross reward, estimated net reward, slots remaining only when current and authoritative.
- **My work:** claimed → submitted → under review → approved/rejected with reason → paid.
- **Earnings:** pending, approved, withdrawable and lifetime totals shown separately; every number links to a transaction statement.
- **Task fit:** personal history used minimally and transparently; explain why a task is recommended.
- **Safety & privacy:** active sessions, passkeys, data download/deletion request route, report task/user, dispute status.
- **Low bandwidth:** lightweight pages, no auto-playing media, resilient draft submission and explicit retry state.

### Owner panel
- **Overview:** funded task value, gross platform fee revenue, refunds/reversals, payment-processing cost, support/fraud cost, operating cost, contribution margin and cash timing—each with date range and definition.
- **Task operations:** draft/moderation queue, budget reserve, approval SLA, completion quality, rejection reasons, dispute rate, expired/cancelled capacity.
- **Worker fairness:** median net reward/hour by task category, approval time, rejection/appeal reversal rates, repeat-worker retention and payout delay. Suppress small cohorts to avoid exposing individuals.
- **Risk & abuse:** velocity anomalies, duplicate submissions, suspicious task owners, budget exhaustion and payout risk; show aggregate indicators and authorized case IDs, not raw private logs.
- **Finance controls:** immutable ledger view, reconciliation differences, fee-policy version, refund/reversal queue and payout states. Never edit balances directly.
- **Governance:** owner device/session security, role grants, pending dual-control actions, audit log, policy versions, backups/restore status and incident checklist.
- **AI board:** research sources, hypotheses vs evidence, confidence, impact/effort, privacy/security risk, owner decision, experiment owner and rollback trigger. AI must not self-approve its own recommendations.

## 4. Unit economics and the 15% pool proposal

Keep the previously discussed 15% platform-fee pool as a **hypothesis to validate**, not a guaranteed net-profit model:
- 10% allocation to Owner account;
- 5% allocation to development/AI/operating costs.

Before implementation, define the denominator precisely (for example, eligible completed and non-refunded task value), rounding, taxes, refunds, chargebacks, provider fees and when revenue is recognized. Determine whether the split is legally and operationally appropriate in Bangladesh. Never deduct an undisclosed fee from a worker's promised reward.

Suggested calculation per settled task:

- Gross task value funded by buyer
- minus worker reward owed
- minus refunds/chargebacks and payment processing
- minus platform fee allocation and applicable taxes
- minus attributable support, fraud, hosting and AI costs
- equals contribution margin (not necessarily accounting net profit)

Track at least: funded-task conversion, task fill rate, valid completion rate, median worker net reward/hour, median approval time, dispute/reversal rate, repeat buyer rate, repeat worker rate, fraud loss rate, payout failure rate, and contribution margin after variable costs.

No guarantee that users will earn more than competitors. The defensible target is to improve measured **net reward per active hour** while preserving task quality and a sustainable contribution margin. Compare only equivalent task categories, eligibility and time windows.

## 5. Security and privacy boundaries

1. AI is a researcher/advisor, not a financial authority. A deterministic server-side policy engine must validate every operation.
2. Owner actions require server-side authorization, least privilege, CSRF/session protection, recent strong authentication for sensitive changes and audit events.
3. High-risk actions (payout-policy changes, reward-budget overrides, privileged access changes, migration/deploy actions) require explicit human confirmation and independent second approval where appropriate.
4. Bind approvals to actor, operation, target, normalized parameters, policy version, expiry and single-use nonce; reject replay and parameter substitution.
5. Use an append-only ledger; never mutate wallet balances directly. Enforce idempotency and serialize competing reward approvals against the same budget.
6. Audit logs should record who/when/what/target/outcome and safe metadata. Never log passwords, tokens, session IDs, full identity documents, raw payment details or full private task submissions.
7. Do not expose small-cohort earnings or user-level risk signals in owner analytics; use aggregation and access controls.
8. Treat external task instructions, uploaded files and webpages as untrusted input to AI. Tool allowlists, output validation, cost/rate limits and a kill switch are required.
9. Test access denial, CSRF, replay, concurrent last-slot/budget claims, idempotency, account recovery and role escalation.
10. Keep all changes on feature branches and draft PRs. No production migration, deploy, merge, workflow rerun or financial logic change without explicit authorization and passing current-head gates.

## 6. Phased implementation

### Phase 0 — Verify and measure (no financial behavior changes)
- Confirm the actual default-branch SHA, app routes, existing Owner/admin authorization and templates.
- Resolve migration graph collisions in the security board before Owner panel expansion; do not fake migration state.
- Establish event definitions and baseline metrics using sanitized aggregates only.
- Run 20+ site research refresh and tag every claim as source-backed fact or hypothesis.

### Phase 1 — Low-risk experience
- Homepage sample-vs-live labelling (already proposed in Draft PR #55).
- Task detail fee/net-reward breakdown only where the backend already has authoritative data.
- Mobile accessibility, keyboard focus, readable status states and lightweight loading/error states.
- Add copy for approval, dispute and payout timelines without inventing guarantees.

### Phase 2 — Owner read-only insights
- Read-only dashboard from existing, authorized aggregate data.
- Definitions for gross fees, refunds, provider costs, operating costs and contribution margin.
- Audit events and security posture indicators with role-based visibility.
- No manual balance editing or new payout actions.

### Phase 3 — Guarded workflows
- Moderation, budget reserve and reward-capacity invariants only after tests and written financial policy.
- Dual-control approvals, idempotency, concurrency tests and dispute/reversal flows.
- Owner passkey/step-up authentication and tested recovery.
- Shadow-mode AI recommendations before any controlled action; no autonomous financial execution.

### Phase 4 — Measured growth experiments
- A/B test task card clarity, duration estimates and category filters.
- Improve match quality and repeat buyer/worker retention.
- Evaluate transparent loyalty fees or paid employer tools only after cost, legal and user-impact review.
- Stop experiments that lower worker net reward/hour, raise disputes/fraud or create misleading earnings expectations.

## 7. Acceptance gates

A feature is not “done” until:
- The relevant current-head CI and tests pass, with no stale-run substitution.
- Permission-denial and privacy tests prove unauthorized roles cannot access data/actions.
- Financial tests cover rounding, refunds, replays, idempotency, concurrent last-slot and cumulative budget boundaries where relevant.
- Accessibility and responsive checks pass for mobile.
- Public text does not imply live availability or guaranteed income without evidence.
- An independent review is complete for high-risk changes.
- The Draft PR states exact SHA, tests actually run, remaining gaps and rollback plan.

## 8. Bangladesh and international compliance review

Before monetization or payout changes, obtain a qualified review of Bangladesh requirements applicable to the actual operating model, including tax/VAT, payment service/provider arrangements, consumer-facing fee disclosures, privacy/data protection, advertising and worker/contractor terms. Also map relevant international privacy/security/accessibility standards to actual user geographies and contracts. This blueprint is not legal advice and does not establish compliance by itself.

## 9. Research limitations

This is a source-backed first-pass product blueprint, not a full UX teardown, penetration test, legal opinion, financial forecast or proof of market superiority. Competitor terms may change and some services may be region-restricted. Validate proposed metrics against sanitized production aggregates only after access controls and data minimization are reviewed.


## 10. Security-board refresh — 2026-10-18

This snapshot was gathered through read-only repository metadata, source-file inspection, workflow-run summaries, and official public sources. No workflow was dispatched or rerun. No secrets, environment values, raw CI logs, private artifacts, production database, customer records, or financial records were accessed.

### Exact-head release evidence

| Ref | Exact head SHA | Evidence observed | Decision |
|---|---|---|---|
| Default branch `main` | `aa548d148d36df0c8ed2af3d58d8e1f0d8e38512` | Combined-status query returned no status records; the PR-run query returned no PR-triggered runs for this SHA. | Exact-head release approval is not established by these results. Absence from these endpoints does not prove no other workflow exists. |
| PR #41, integrated security candidate | `841b65cbb6ef51b563537d49f809e58830e70104` | Security Review #843 failed; Security Gate #1120 failed; PostgreSQL Financial Verification #271 passed, all with this exact head SHA. [Review #843](https://github.com/Rafiqual69/Zootasks/actions/runs/39055731615), [Gate #1120](https://github.com/Rafiqual69/Zootasks/actions/runs/39055731591), [PostgreSQL #271](https://github.com/Rafiqual69/Zootasks/actions/runs/39055731605). | Blocked. Do not merge or deploy. |
| PR #52, schema-drift audit | `b14aece21769fc7c3782e9326b3a0fc5213730b4` | Security Review #854, PostgreSQL Financial Verification #275, and Security Gate #1139 passed on this head. [Review #854](https://github.com/Rafiqual69/Zootasks/actions/runs/39065416663), [PostgreSQL #275](https://github.com/Rafiqual69/Zootasks/actions/runs/39065416559), [Gate #1139](https://github.com/Rafiqual69/Zootasks/actions/runs/39065416499). | Useful branch-local evidence only. PR #52 targets `fix/restore-task-claim-migration-20261009`, not `main`. |
| PR #53, promotion transition regression | `4d5b5e58495263064c71dea40911bc4b8403732c` | Security Review #862 passed on this exact SHA but was a push-triggered run; Promotion PostgreSQL Regression #7 passed on this exact SHA and was PR-triggered. [Review #862](https://github.com/Rafiqual69/Zootasks/actions/runs/39146130309), [Regression #7](https://github.com/Rafiqual69/Zootasks/actions/runs/39146133710). | The dedicated tests passed, but the exact-head Security Gate and full PostgreSQL Financial Verification were not returned for this SHA. PR #53 targets the integrated security branch, not `main`. Keep Draft. |
| PR #55, sample-task wording | `a33432cb40ced36ad152a7a31e917c80953b70ce` | Security Gate #1140, Security Review #863, and PostgreSQL Financial Verification #276 failed on this exact head. | Keep Draft; do not claim the UX change is approved or shipped. |
| PR #56, this blueprint | `c16ab1f184d1345e105512939afe97af33357be2` | Security Review #864, Security Gate #1141, and PostgreSQL Financial Verification #277 failed on this exact head. [Review #864](https://github.com/Rafiqual69/Zootasks/actions/runs/39147903776), [Gate #1141](https://github.com/Rafiqual69/Zootasks/actions/runs/39147903791), [PostgreSQL #277](https://github.com/Rafiqual69/Zootasks/actions/runs/39147903759). | Keep Draft. These results are not approval for a later commit; check the new head after any documentation update. |

Workflow conclusions above come from run metadata and final conclusions only; raw logs and artifacts were not opened. A successful run on a different SHA or base branch is not a substitute for the release candidate's required checks. Independent human review remains required.

### Repository facts affecting product design

- On the inspected `main` SHA, `Promotion` has `completed_workers` but no `reserved_workers` field. The public promotion page derives remaining slots and progress from `completed_workers`. Issue #43 separately records that the claim path increments that counter at claim time. Until the reservation/completion workflow is reconciled and integrated, do not present that progress figure as a verified count of approved completions.
- The integrated security branch used by PR #53 contains `reserved_workers` and database checks for nonnegative reward/budget and worker-count relationships. That is branch-local evidence, not proof the default branch has those protections.
- PR #52's `audit_schema_drift` command compares migration records with source migration files and checks model tables/columns. It does not compare every index, check constraint, foreign-key behavior, or legacy-row meaning. Treat it as a narrow read-only diagnostic, not a complete migration sign-off.
- Issue #48's acceptance criteria require a real enrollment/confirmation ceremony, one-primary-device invariant, revocation/recovery, session and CSRF protection, replay tests, and exact-head CI. An issue description or a WebAuthn service module alone is not proof that an Owner device is enrolled or active.
- Issue #46 remains a release gate: AI may propose actions, but authorization must happen in the execution layer. High-impact financial, credential, migration, and deployment actions remain subject to human dual control and fail-closed policy enforcement.

### Refreshed source register

**Checked on 2026-10-18.** “Source evidence” below means the official page states the listed feature or policy. The ZooTasks change is a **hypothesis** until implemented, tested, and measured. Fees, availability, terms, and regional restrictions change; do not copy competitor prices or assume availability in Bangladesh.

| # | Official source | Source evidence observed | ZooTasks implication — hypothesis |
|---:|---|---|---|
| 1 | [Upwork service fee](https://support.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee) | Fee can vary by contract; the exact fee is shown before commitment and net-pay examples are provided. | Show fee, rounding, refund treatment, and estimated net reward before a worker starts; persist the fee-policy version. |
| 2 | [Fiverr order flow and fees](https://help.fiverr.com/hc/en-us/articles/360010558038-How-Fiverr-Works) | Buyer service fee is shown at checkout, including an additional fee for smaller orders. | Show the full buyer total and worker reward separately before confirmation. Do not copy Fiverr's rates. |
| 3 | [Freelancer.com fees](https://www.freelancer.com/feesandcharges) | Fees vary by transaction type and optional services; milestone payment handling is documented. | Make mandatory and optional fees distinguishable and show funding/hold/refund status. |
| 4 | [PeoplePerHour commission](https://support.peopleperhour.com/hc/en-us/articles/205218337-Freelancer-commission-fees) | Commission tiers depend on lifetime billing with a buyer; payment statements show effective fees. | Test repeat-buyer retention before considering any loyalty tier; disclose how the tier is calculated. |
| 5 | [Toptal talent FAQ](https://www.toptal.com/freelance-jobs/faq) | Its FAQ describes talent-set rates and automated payment handling. | Avoid silent reward changes and give workers a clear approval-to-payment timeline. |
| 6 | [Workana commission](https://help.workana.com/hc/en-us/articles/360041235874-How-is-the-commission-calculated-at-Workana) | Official help describes a tiered commission tied to client relationship spend; the page was updated in September 2026. | Consider loyalty pricing only after unit-economics, legal, and user-impact review. |
| 7 | [Contra crypto payout fee](https://help.contra.com/en/articles/13119448-crypto-payout-fee) | A payout-specific fee is shown in the withdrawal summary before confirmation; the page distinguishes it from project earnings. | Separate earned reward from optional payout-method fees and show the exact deduction before withdrawal. |
| 8 | [Guru freelancer pricing](https://www.guru.com/pricing-freelancer/) | Membership tiers change bid limits and job fees. | If paid tiers are considered, state limits and costs plainly; do not require workers to pay to unlock basic access to funded work. |
| 9 | [Airtasker service fee](https://support.airtasker.com/hc/en-us/articles/200294499-What-is-the-service-fee) | Fee breakdown appears when offering and is available in payment history; local fee/tax rules can differ. | Store a transaction-level fee receipt and localize supported payout/fee rules by jurisdiction. |
| 10 | [Taskrabbit pricing transparency](https://support.taskrabbit.com/hc/en-us/articles/46260394090651-Pricing-Transparency-Policy) | Policy requires recurring costs to be reflected in the rate and explains pricing expectations. | Put prerequisites, time estimate, proof requirements, and unavoidable user costs in task details. |
| 11 | [Clickworker worker guide](https://www.clickworker.com/CLICKWORKER/) | The official page describes microtasks, qualification, weekly payments, and multiple task types. | Use transparent skill/eligibility filters and show actual payment availability by country and provider. |
| 12 | [Prolific participant flow](https://www.prolific.com/participants-how-it-works) | Participants can see pay, duration, and study details before taking part; eligibility and identity verification are part of the flow. | Display reward, estimated minutes, eligibility, and expected approval process before task claim. |
| 13 | [Toloka user agreement](https://toloka.ai/tolokers/user-agreement-january-2025) | The published agreement describes payment after task acceptance and allows rejection/resubmission under its terms; the cited version is dated January 2025. | Verify the latest terms before borrowing a pattern; define ZooTasks' review window, rejection reason, and appeal policy in its own terms. |
| 14 | [UserTesting payment FAQ](https://support.usertesting.com/hc/en-us/articles/4405116832019-FAQ-Payments) | The official FAQ says payment amounts appear on the dashboard and payments usually arrive about 14 days after a test. | Show the amount and status per task, expected payout timing, payment history, and failure resolution. Confirm regional payout availability. |
| 15 | [Microworkers FAQ](https://www.microworkers.com/faq.php) | The FAQ describes balance/withdrawal history, minimum withdrawal, KYC, and campaign fees. | Separate pending, approved, and withdrawable balances; explain KYC and thresholds before workers invest time. |
| 16 | [Remotasks worker site](https://stable.remotasks.com/en) | The official site advertises training, task unlocking, and weekly payments through listed providers. | A skill ladder may help, but verify current service/country availability and actual realized net earnings before using this as a benchmark. |
| 17 | [Amazon Mechanical Turk closure FAQ](https://www.mturk.com/help) | The official FAQ states MTurk permanently closed on 2026-09-30. | Remove stale competitor assumptions from future research and re-verify platform status each run. |
| 18 | [Linear audit log](https://linear.app/docs/audit-log) | Workspace audit events are owner-restricted and retained for a stated period. | Use role-gated, searchable audit events with a documented retention policy and data minimization. |
| 19 | [Supabase access control](https://supabase.com/docs/guides/platform/access-control) | Owner, administrator, developer, read-only, and no-access roles have different scopes. | Separate Owner, finance approver, support, analyst, and read-only permissions; grant only necessary scope. |
| 20 | [Supabase platform audit logs](https://supabase.com/docs/guides/security/platform-audit-logs) | Logs identify timestamp, actor, action, target, and metadata; availability and retention vary by plan. | Record actor/action/target/outcome and safe metadata; do not place secrets or full private payloads in audit entries. |
| 21 | [Vercel audit logs](https://vercel.com/docs/audit-log) | Owner-role access, exports, short-lived export links, and SIEM streaming are documented. | Require authorized export, short-lived links, export-event auditing, and minimal export scope. |
| 22 | [Cloudflare Audit Logs v2](https://developers.cloudflare.com/fundamentals/account/account-security/audit-logs/) | The docs describe standardized action logs, filtering, retention, and view-action coverage updated in October 2026. | Track sensitive reads as well as writes where supported; apply filters and retention limits to avoid over-collection. |
| 23 | [GitHub organization audit log](https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization) | Organization audit entries record who, what, and when; owner access and time-window limits are documented. | Audit policy, role grants, release decisions, and export activity without exposing raw secrets or customer data. |
| 24 | [Stripe Connect pricing](https://stripe.com/en-de/connect/pricing) | Connect pricing distinguishes platform/account and payout costs; the cited page is regional. | Include actual processor/payout costs in contribution margin and verify a payment provider's Bangladesh eligibility before selecting it. |
| 25 | [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | NIST provides a voluntary lifecycle framework for identifying, measuring, and managing AI risks; the framework is under revision. | Maintain a risk register, accountable owner, test evidence, residual risk, and rollback condition for each AI capability. |
| 26 | [OWASP Agent Control Standard](https://genai.owasp.org/resource/agent-control-standard-acs/) | OWASP describes ACS as guidance for runtime-enforced, inspectable control of agent authority. | Enforce tool and resource permissions in a deterministic executor outside model context; bind approvals to exact actions. |
| 27 | [OWASP AISVS 1.0](https://owasp.github.io/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/) | AISVS 1.0 provides testable AI security requirements across lifecycle, orchestration, and monitoring. | Map applicable requirements to acceptance tests and CI; record the standard version used. |
| 28 | [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | The 2026 list describes risks specific to agents that plan and act across workflows. | Add adversarial tests for tool abuse, prompt injection, memory poisoning, privilege escalation, cascading actions, and denial-of-wallet. |
| 29 | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | WCAG 2.2 is a W3C Recommendation covering accessibility needs including vision, movement, cognition, and input interaction. | Target WCAG 2.2 AA for the public site and dashboards; combine automated checks with keyboard and mobile testing. |
| 30 | [Bangladesh Bank MFS Regulations 2022](https://www.bb.org.bd/aboutus/regulationguideline/psd/mfs_regulations_2022.pdf) | The official regulation defines a Bangladesh MFS framework and refers to AML/CFT and payment-system rules. | Obtain qualified advice on the exact payout flow/provider; do not assume an MFS product authorizes cross-border transfers. |
| 31 | [National Board of Revenue VAT Acts](https://nbr.gov.bd/regulations/acts/vat-acts/eng/contents/eng) | NBR publishes the relevant VAT acts and rules. | Model tax separately from platform fee and obtain a Bangladesh tax review before adopting the 15% allocation. |
| 32 | [Bangladesh law portal — Cyber Security Ordinance page](https://bdlaws.minlaw.gov.bd/act-print-1538.html) | The official page says the 2025 ordinance was repealed by the Cyber Security Act 2026. | Do not rely on a repealed ordinance as current law; legal counsel must verify the current consolidated law and commencement provisions before release. |

### Ranked product/security work

| Rank | Work item | Measurable acceptance criteria |
|---:|---|---|
| P0 | Release gate integrity | 100% of required checks are successful on the exact release-candidate SHA, with independent human review recorded. Any missing, stale, or failed gate blocks release. |
| P0 | Budget and capacity invariant | Tests cover under-budget, exact-budget, over-budget, replay, legacy-ledger reconciliation, rejection release, and concurrent last-slot claims. Zero over-budget approvals and zero capacity oversubscription in the tested paths. |
| P0 | Migration reconciliation | Migration graph is reviewed before merge; a fresh database and a disposable legacy-schema copy both migrate and pass regression tests. Audit index/constraint/foreign-key/data semantics separately from column drift. |
| P1 | Owner primary-device security | Enrollment requires explicit Owner confirmation; a database/transaction invariant permits one active primary credential; revoke, recovery, session invalidation, CSRF, replay, concurrent enrollment, and protected-action bypass tests pass. |
| P1 | AI authority and privacy | Every tool call is authorized by the execution layer; exact-action approvals are single-use and parameter-bound; unauthorized writes are denied; adversarial tests cover prompt injection, memory poisoning, tool chaining, and cost exhaustion. Audit tests assert that secrets/PII/payloads are not logged. |
| P1 | Task reward and capacity clarity | Every published task with a reward shows the authoritative reward and prerequisites; only verified data is shown as live. Do not label claimed/reserved slots as completed work. |
| P2 | Worker net earnings and time-to-earn | Measure median and 25th-percentile net reward per active hour by task category, plus approval delay and payout failure. Compare equivalent tasks and periods; suppress small cohorts. |
| P2 | Owner read-only finance dashboard | Every metric has a definition and reconciliation source. Show gross fees, refunds/reversals, provider costs, taxes, support/fraud costs, operating costs, and contribution margin separately. No direct balance editing. |
| P2 | Low-bandwidth accessible task flow | WCAG 2.2 AA review, keyboard-only test, responsive/mobile check, and slow-network retry/error tests pass; track task detail-to-start conversion and failed submissions. |

### Phased implementation plan

1. **Release integrity first:** resolve current exact-head failures through reviewed changes, then confirm all required checks on the final candidate SHA and obtain independent review. Do not merge or deploy while a gate is failed or missing.
2. **Financial and migration controls:** finalize the written budget meaning and reservation/completion state machine. Add exact-boundary and concurrency tests; review the migration graph and legacy data on disposable databases only.
3. **Owner authentication and governance:** implement the real passkey enrollment/confirmation lifecycle, single-primary-device enforcement, session controls, revocation/recovery, role separation, and safe audit events.
4. **AI control plane:** enforce allowlisted tools and scoped identities at runtime; bind approvals to action/target/normalized parameters/policy version/expiry; test replay, prompt injection, cross-tool escalation, data exfiltration, and cost limits.
5. **Read-only product analytics:** add worker earnings/time-to-earn and Owner unit-economics metrics only from authorized aggregates with documented definitions and privacy thresholds.
6. **Measured UX experiments:** test task card clarity, filters, fee/net reward display, and low-bandwidth flow. Roll back any experiment that worsens dispute/fraud rates or lowers worker net reward per active hour.

### Bangladesh legal and data-protection caveat

The official sources reviewed confirm that Bangladesh has a current Cyber Security Act 2026 reference and Bangladesh Bank MFS rules, and NBR publishes VAT legislation. The current consolidated personal-data-protection text and commencement/transitional details were not independently verified from a stable official text in this run. Do not treat this research note as a legal opinion. Before production, have qualified Bangladesh counsel verify the current personal-data protection law, cyber-security law, payment-provider authorization, AML/CFT, tax/VAT, consumer disclosures, cross-border processing/transfers, data-subject rights, breach response, and worker terms against the actual business model.

This is a research and design update only. It does not claim that ZooTasks is compliant, secure, profitable, or ready for release.


## Research board refresh — 2026-10-19

### Repository state and release evidence

The default branch was rechecked at `aa548d148d36df0c8ed2af3d58d8e1f0d8e38512` (commit message: “Security: align task claim migration state”). The checks below were retrieved from GitHub for the listed exact PR head SHA. No workflow was manually dispatched or rerun. Raw logs and artifacts were not opened.

| PR | Exact head SHA | Current evidence | Board decision |
|---|---|---|---|
| #41 integrated security | `841b65cbb6ef51b563537d49f809e58830e70104` | Security Review #843 failed at Dependency audit; Security Gate #1120 failed at Dependency vulnerability audit; PostgreSQL Financial Verification #271 passed. | Blocked. |
| #52 schema-drift audit | `b14aece21769fc7c3782e9326b3a0fc5213730b4` | Security Review #854, Security Gate #1139, and PostgreSQL Financial Verification #275 passed. Base is `fix/restore-task-claim-migration-20261009`, not `main`. | Branch-local evidence only; Draft. |
| #53 promotion replay regression | `4d5b5e58495263064c71dea40911bc4b8403732c` | Security Review run #862 and dedicated Promotion PostgreSQL Regression #7 report success for this head. The current PR-triggered run query did not return the full Security Gate or full PostgreSQL Financial Verification on this head. | Draft; do not treat missing full gates as passed. |
| #55 homepage sample labels | `a33432cb40ced36ad152a7a31e917c80953b70ce` | Security Gate #1140 and PostgreSQL Financial Verification #276 failed at migration-drift check; Security Review #863 failed at full regression. | Draft; UX-only scope does not waive release gates. |
| #56 research blueprint | `78aeb3fd2abd4a3ba0a039f36332c9017811c78a` | Security Gate #1143 and PostgreSQL Financial Verification #279 failed at migration-drift check; Security Review #866 failed at full regression. | Draft; documentation only, no release approval. |
| #57 read-only Owner dashboard | `3a5c3f0cc0425fb06666ab075fef69da1f6ee96e` | Security Gate #1142 and PostgreSQL Financial Verification #278 failed at migration-drift check; Security Review #865 failed at full regression. | Draft; render/accessibility checks also remain unrun. |
| #58 claim-history migration lineage | `9e59254ab974adf3cac51767af622803f0bf7962` | PostgreSQL Financial Verification #280 passed. Security Gate #1144 and Security Review #867 failed at dependency-vulnerability audit. | Draft; migration success does not clear security gates. |

No independent review submissions were returned for PRs #52, #53, #55, #56, #57, or #58. A successful run on a different branch, base, or SHA is not release approval. The repository default branch had no PR-triggered workflow runs returned by the connector for its SHA; this is not proof that no other workflow types exist.

### Additional repository evidence

At the checked `main` SHA, `backend/promotions/models.py` defines `reward`, `budget`, `max_workers`, and `completed_workers`, but no `reserved_workers`. `backend/promotions/views.py` calculates remaining capacity from `max_workers - completed_workers` and renders `completed_workers/max_workers`. This supports issue #43's concern that the public counter can conflate claims with completed work. The current `backend/tasks/migrations/0005_alter_taskclaim_task.py` depends on `tasks.0004_protect_claim_history`, while that parent migration is absent from the checked default-branch tree. These are source-level findings only; no database was inspected or migrated.

### Official-source refresh, checked 2026-10-19

For every row, the linked page is the source evidence. The ZooTasks implication remains a hypothesis until implemented, tested, and measured. Prices, eligibility, payout routes, regional availability, and terms can change.

| # | Official source URL | Observable source evidence checked | ZooTasks implication | Evidence type |
|---:|---|---|---|---|
| 1 | https://support.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee | The contract fee is disclosed before commitment; the help page provides net-pay examples and fee/refund treatment. | Show gross reward, fee, rounding, refund rules, and estimated net reward before claim. | Source fact; UI proposal is hypothesis. |
| 2 | https://help.fiverr.com/hc/en-us/articles/34069565843985-How-Fiverr-works-for-freelancers | The official guide describes 80% of cleared client payment to freelancers, a standard 14-day clearing period, and a Resolution Center. | Display pending/approved/available states, expected payout timing, and an appeal route. | Source fact; UI proposal is hypothesis. |
| 3 | https://www.freelancer.com/support/payments/project-fees | The fee schedule varies by project/payment type and explains when fees are charged. | Distinguish platform fees from payment processing and optional services. | Source fact; UI proposal is hypothesis. |
| 4 | https://support.peopleperhour.com/hc/en-us/articles/205218337-Freelancer-commission-fees | Commission tiers depend on lifetime billing with a buyer; monthly payment statements show effective fees. | Test loyalty pricing only after checking worker impact and unit economics. | Source fact; pricing change is hypothesis. |
| 5 | https://www.toptal.com/freelance-jobs/faq | Talent set their rates; the official FAQ describes automated payment handling and says Toptal does not take a cut of talent earnings. | Keep worker reward terms stable after acceptance and show approval-to-payout status. | Source fact; UI proposal is hypothesis. |
| 6 | https://help.workana.com/hc/en-us/articles/360041235874-How-is-the-commission-calculated-at-Workana | The page, updated 2026-09-17, describes tiered freelancer commission and a client service fee. | If evaluating repeat-client discounts, model both sides' effective fees and disclose the formula. | Source fact; pricing change is hypothesis. |
| 7 | https://contra.com//pricing | The pricing page separates plan fees, client payment fees, faster payout fees, and third-party processing fees. | Keep platform commission and provider/payout costs as separate line items; verify Bangladesh availability. | Source fact; fee design is hypothesis. |
| 8 | https://www.guru.com/pricing-freelancer/ | Membership tiers list different job fees and bid allowances. | Do not require paid membership to access ordinary funded tasks without evidence of worker benefit. | Source fact; policy proposal is hypothesis. |
| 9 | https://support.airtasker.com/hc/en-us/articles/360031769372-What-is-the-Connection-Fee | The US-specific connection fee is separate from the Tasker service fee, is disclosed at assignment, and has cancellation/refund conditions. | Display customer charges and worker-side fees separately and apply only the correct jurisdiction's schedule. | Source fact; UI proposal is hypothesis. |
| 10 | https://support.taskrabbit.com/hc/en-gb/articles/46260504648731-What-s-the-Taskrabbit-trust-support-fee | The invoice lists a Trust & Support fee separately; its treatment varies with local pricing rules. | Explain the purpose and payer for every fee; do not hide operating costs in the worker's reward. | Source fact; UI proposal is hypothesis. |
| 11 | https://support-workplace.clickworker.com/support/solutions/articles/80000672350-what-payment-options-do-i-have- | Payment methods, minimum thresholds, KYC requirements, and estimated processing windows vary by method and country. | Show only payout routes confirmed for the member's country and explain thresholds before work begins. | Source fact; localization proposal is hypothesis. |
| 12 | https://participant-help.prolific.com/en/articles/445059-when-will-i-be-paid-for-a-study | A submission must be reviewed; if not approved within 22 days, it is automatically approved under the described policy. | Define a clear review SLA, escalation path, and fair timeout policy for unreviewed submissions. | Source fact; policy proposal is hypothesis. |
| 13 | https://toloka.ai/tolokers/user-agreement-january-2025 | The previously recorded official agreement describes acceptance/rejection and payment conditions; its current replacement was not independently verified on this run. | Re-check current terms before borrowing any rejection or payment pattern. | Historical source fact; current status unverified; proposal is hypothesis. |
| 14 | https://support.usertesting.com/hc/en-us/articles/4405125498003-Where-s-my-payment | The contributor help page says payments usually arrive 14 days after a test and status/amount can be checked in test history. | Show task-level payment status and expected payout date, with an explicit exception path for delays. | Source fact; UI proposal is hypothesis. |
| 15 | https://www.microworkers.com/faq.php | The FAQ documents withdrawal history, minimum withdrawal, KYC, and a twice-weekly payment schedule. | Separate earned, approved, and withdrawable balances and disclose identity verification requirements early. | Source fact; UI proposal is hypothesis. |
| 16 | https://www.remotasks.com/en | The official worker site advertises training, unlocking more difficult tasks, and weekly payments through listed providers; country availability is stated on the site. | A skills ladder may be tested, but measure actual net earnings and confirm eligibility in Bangladesh. | Source fact; product proposal is hypothesis. |
| 17 | https://www.mturk.com/help | The official closure FAQ says MTurk permanently closed on 2026-09-30; post-closure worker/requester actions remain open until 2026-10-30, and transaction history is stated to remain available until 2027-01-28. | Do not treat MTurk as an operating competitor or copy its operating assumptions; recheck status each run. | Current official status fact; implication is hypothesis. |
| 18 | https://linear.app/docs/audit-log | Workspace audit events are owner-restricted, searchable/filterable, and retained for 90 days on the described plan. | Use role-gated audit search, documented retention, and a safe export trail. | Source fact; design proposal is hypothesis. |
| 19 | https://supabase.com/docs/guides/platform/access-control | Owner, administrator, developer, read-only, and no-access roles have distinct scopes. | Split Owner, finance approver, support, analyst, and read-only access by least privilege. | Source fact; RBAC proposal is hypothesis. |
| 20 | https://supabase.com/docs/guides/security/platform-audit-logs | Organization actions record timestamp, actor, action, target, and metadata; plan restrictions apply. | Record safe actor/action/target/outcome fields without credentials or full private payloads. | Source fact; implementation is hypothesis. |
| 21 | https://vercel.com/docs/audit-log | Owner-role audit access, CSV export, and SIEM streaming are documented; export links are time-limited. | Require explicit export authorization, short-lived links, and audit events for export requests/downloads. | Source fact; implementation is hypothesis. |
| 22 | https://developers.cloudflare.com/fundamentals/account/account-security/audit-logs/ | Audit Logs v2 provides consistent actor/action/resource filters and records supported reads and writes; 18-month retention is documented. | Audit sensitive reads as well as writes when justified, and set minimal retention based on risk and law. | Source fact; policy proposal is hypothesis. |
| 23 | https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization | Organization audit entries show who, what, and when; access is owner-restricted and a 180-day event window is documented. | Preserve an append-only security/audit history and test access restrictions and retention. | Source fact; implementation is hypothesis. |
| 24 | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets | Rulesets can require pull requests and status checks and block force pushes; bypass roles can be configured. | Require current-head gates and independent review for release; minimize and audit bypass access. | Source fact; repository policy proposal is hypothesis. |
| 25 | https://stripe.com/pricing | The public pricing page itemizes processing, dispute-prevention, authentication, conversion, and instant-payout costs; rates vary by product/account. | Model actual provider and payout costs before setting fees; do not assume Stripe is available for ZooTasks' Bangladesh entity. | Source fact; provider choice is unverified; pricing proposal is hypothesis. |
| 26 | https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook | NIST's voluntary playbook organizes actions around Govern, Map, Measure, and Manage. | Maintain an AI risk register, named control owners, measurable tests, residual risk, and incident/rollback criteria. | Source fact; governance implementation is hypothesis. |
| 27 | https://genai.owasp.org/2026/09/01/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/ | OWASP announced its 2026 LLM guidance and Agent Control Standard, aimed at practical runtime control of agentic AI. | Authorize tools in the execution layer, not in model instructions alone; bind approvals to exact action parameters. | Source fact; implementation is hypothesis. |
| 28 | https://owasp.github.io/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/ | AISVS 1.0 was released in June 2026 with 191 testable requirements across 12 chapters, including identity, orchestration, adversarial robustness, and monitoring. | Map applicable requirements to versioned acceptance tests and CI; use alongside general application-security controls. | Source fact; test mapping is hypothesis. |
| 29 | https://www.w3.org/TR/WCAG22/ | WCAG 2.2 is a W3C Recommendation with testable accessibility criteria for web content across devices. | Target WCAG 2.2 AA and test keyboard, focus, mobile, screen-reader, and low-bandwidth paths. | Standard fact; target is a proposal pending assessment. |
| 30 | https://www.bb.org.bd/aboutus/regulationguideline/psd/mfs_regulations_2022.pdf | Bangladesh Bank's MFS Regulations 2022 set a regulatory framework and refer to payment-system and AML/CFT rules. | Obtain legal/provider review of the actual payout model; do not assume that an MFS interface alone authorizes every flow. | Official regulation fact; applicability requires legal analysis. |
| 31 | https://nbr.gov.bd/uploads/acts/18.pdf | NBR hosts the VAT and Supplementary Duty Act 2012 English translation; the text notes that commencement depends on provisions and government notification. | Recheck current amendments, commencement, and service-specific tax treatment with Bangladesh counsel/accounting advice. | Official publication fact; applicability remains unverified. |

### Updated ranked backlog

1. **P0 — Release integrity:** 100% of required checks must pass on the final exact candidate SHA and independent human review must be recorded. Missing or stale checks block release.
2. **P0 — Budget/capacity correctness:** zero over-budget approvals, duplicate credits, or capacity oversubscription in exact-boundary, replay, rejection, legacy-reconciliation, and concurrent-last-slot tests.
3. **P0 — Migration lineage:** fresh-database and disposable legacy-copy rehearsal, with indexes, constraints, foreign keys, and data semantics reviewed; no production rehearsal.
4. **P1 — Owner security:** real passkey enrollment/confirmation, one active primary credential, revoke/recovery, session invalidation, CSRF/replay and concurrency tests.
5. **P1 — AI control plane:** every tool call receives an independent policy decision; high-risk actions require exact-action dual control; adversarial tests show zero unauthorized writes and no sensitive audit leakage.
6. **P1 — Fee/net reward disclosure:** before claim, show reward, applicable fee/deduction, estimated net amount, prerequisites, estimated time, and approval/payout policy.
7. **P2 — Owner unit economics:** reconcile gross fees, refunds/reversals, provider costs, taxes, support/fraud, infrastructure, and AI costs separately; label contribution margin only when the formula and source are documented.
8. **P2 — Accessibility and low bandwidth:** WCAG 2.2 AA assessment, keyboard/mobile checks, slow-network/error recovery, and tracked task-start/submission success.

The proposed 15% fee pool (10% Owner account / 5% development, AI, and operating costs) remains an unvalidated pricing hypothesis. It is not net profit and must be modeled against actual costs, refunds, payout routes, taxes, and legal obligations.

### Safety and delivery record

This update changes research documentation only on the existing feature branch. No application code, configuration, financial logic, access controls, production database, or migration state was changed. No raw logs/artifacts, secrets, credentials, PII, or customer/financial records were accessed or added. No workflow was manually dispatched or rerun. Keep this PR Draft until its new exact-head CI, source review, and independent human review are complete.


---

## Research board refresh — 2026-11-25

**Scope and handling.** This refresh uses public GitHub metadata, safe source-file reads, Railway service inventory, and official public web pages. It does not read .env files, secrets, credentials, PII, customer or financial records, raw CI logs, or private workflow artifacts. No production database or migration was accessed. Workflow evidence below is queried by the exact commit SHA; a run on another SHA or base is not a substitute.

### 1. Current repository and release state

- Default branch: **main**
- Exact current main head: **aa548d148d36df0c8ed2af3d58d8e1f0d8e38512**
- Main commit date: **2026-10-06T14:58:00Z**
- Commit message: **Security: align task claim migration state**
- GitHub branch metadata reports **protected: false**; the repository rulesets endpoint returned an empty list.
- Exact-head workflow evidence for main: ZooTasks Security Gate run [37483388868](https://github.com/Rafiqual69/Zootasks/actions/runs/37483388868) failed; Security Review run [40273321095](https://github.com/Rafiqual69/Zootasks/actions/runs/40273321095) failed. No PostgreSQL Financial Verification run was returned for the main SHA. The PostgreSQL workflow is configured for pull requests to main and manual dispatch, so the absence of a main push run is not a passing result.
- The main tree contains backend/tasks/migrations/0005_alter_taskclaim_task.py, whose dependency is tasks.0004_protect_claim_history; the 0004_protect_claim_history.py file is absent from main. This is a source-level migration-graph defect, not a claim about any live database.
- Two competing repair approaches are open: PR #74 restores a 0004 migration and protects both task and worker references; PR #75 changes 0005 to depend directly on 0003. These are different migration lineages. Do not combine, fake, rename, or mark migrations applied without a reviewed fresh-database and disposable-legacy-database reconciliation.
- The release gate is currently not enforceable at repository level because main is unprotected and no rulesets were returned. Required reviews, exact-head security checks, PostgreSQL financial verification, migration review, and a deployment gate must be configured by an authorized repository administrator before release.

#### Open issue queue

These are issues, not pull requests; they have no head SHA or workflow runs.

| Issue | Current open requirement | Product/security consequence |
|---:|---|---|
| [#43](https://github.com/Rafiqual69/Zootasks/issues/43) | Define promotion budget semantics and prevent approvals from exceeding the funded reward ceiling under concurrency | Separate reserved capacity from approved completions; lock the promotion or equivalent reservation record; make approval idempotent |
| [#45](https://github.com/Rafiqual69/Zootasks/issues/45) | Reconcile reservation and completion transitions | Increment completed only once on approval; release reserved capacity once on rejection/cancellation/expiry; test replay and last-slot concurrency |
| [#46](https://github.com/Rafiqual69/Zootasks/issues/46) | AI-agent authority boundary and human governance | The model proposes; an independent runtime policy engine authorizes; high-impact actions require exact-action human approval and dual control |
| [#48](https://github.com/Rafiqual69/Zootasks/issues/48) | Single primary Owner input device | A device identifier is not authorization; require server-verified passkey ceremonies, revocation, recovery, short sessions and separate critical-action approvals |
| [#54](https://github.com/Rafiqual69/Zootasks/issues/54) | Evidence-led website UX and trust improvements | Keep UX hypotheses measurable and inspect existing homepage, Owner and security PRs before creating overlapping work |

#### Exact-head PR matrix

Run IDs below are GitHub Actions workflow-run IDs. “Pass” means the listed workflow completed successfully on that exact head SHA; it does not establish independent review, safe migration integration, production readiness, or approval to merge.

| PR | Exact head SHA | Base branch (recorded base SHA where relevant) | State | Exact-head workflow evidence |
|---:|---|---|---|---|
| [#41](https://github.com/Rafiqual69/Zootasks/pull/41) | 841b65cbb6ef51b563537d49f809e58830e70104 | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; Draft; merged=false | Security Gate 39055731591 failed; Security Review 39055731615 failed; PostgreSQL Financial Verification 39055731605 passed. This is the failing base used by #53. |
| [#52](https://github.com/Rafiqual69/Zootasks/pull/52) | b14aece21769fc7c3782e9326b3a0fc5213730b4 | fix/restore-task-claim-migration-20261009 (dd5c3b9d25af27306069651682348bb98388b238) | Open; Draft; merged=false | Security Gate 39065416499 passed; Security Review 39065416663 passed; PostgreSQL Financial Verification 39065416559 passed. All are branch-local; this PR does not target main. |
| [#53](https://github.com/Rafiqual69/Zootasks/pull/53) | 4d5b5e58495263064c71dea40911bc4b8403732c | security/full-integrated-security-board-20261007 (841b65cbb6ef51b563537d49f809e58830e70104) | Open; Draft; merged=false | Security Review push run 39146130309 passed; Promotion PostgreSQL Regression PR run 39146133710 passed. No exact-head Security Gate or full PostgreSQL Financial Verification was returned. Stacked on #41, whose Security Gate and Security Review failed. |
| [#55](https://github.com/Rafiqual69/Zootasks/pull/55) | a33432cb40ced36ad152a7a31e917c80953b70ce | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; Draft; merged=false | Security Gate 39147130401 failed; Security Review 39147130469 failed; PostgreSQL Financial Verification 39147130476 failed. |
| [#56](https://github.com/Rafiqual69/Zootasks/pull/56) | 6834a406187bfda5a0aac7a7ee5e00c742ee4971 immediately before this documentation commit | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; Draft; merged=false | Security Gate 45541849329 failed; Security Review 45541849333 failed; PostgreSQL Financial Verification 45541849328 failed on this exact head. The next documentation commit advances the PR head and must be checked separately. |
| [#57](https://github.com/Rafiqual69/Zootasks/pull/57) | 3a5c3f0cc0425fb06666ab075fef69da1f6ee96e | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; Draft; merged=false | Security Gate 39148226265 failed; Security Review 39148226226 failed; PostgreSQL Financial Verification 39148226231 failed. The template is read-only, but current release checks and render/accessibility evidence are not sufficient. |
| [#66](https://github.com/Rafiqual69/Zootasks/pull/66) | e7e4b3eacd39aa0b6146354ac2545c491fa25934 | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; Draft; merged=false | Security Gate 40011292003 passed; Security Review 40011291937 passed; PostgreSQL Financial Verification 40011291839 passed. The PR description still identifies Twisted 26.10.0rc1 as a pre-release blocker; verify the installed stable artifact and dependency audit before treating this branch as releasable. |
| [#69](https://github.com/Rafiqual69/Zootasks/pull/69) | df6311bd81388eafc29da45de1cbabf68b8ebc83 | security/ci-ephemeral-secret-20261022 (e7e4b3eacd39aa0b6146354ac2545c491fa25934) | Open; Draft; merged=false | Security Gate 40171986340 failed; Security Review 40171986327 failed; PostgreSQL Financial Verification 40171986317 failed. Explicitly stacked on #66; do not merge independently of its base and migration review. |
| [#71](https://github.com/Rafiqual69/Zootasks/pull/71) | 4a09b2aa032e7c33eaa336be2dc5cc9fdeb93994 | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; Draft; merged=false | Security Gate 40271645126 failed; Security Review 40271645136 failed; PostgreSQL Financial Verification 40271645139 failed. Homepage work overlaps #55 and #73. |
| [#73](https://github.com/Rafiqual69/Zootasks/pull/73) | d57616188ffac3abf2e82b1d4acccb4faffb9a62 | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; Draft; merged=false | Security Gate 40271860129 failed; Security Review 40271860145 failed; PostgreSQL Financial Verification 40271860188 failed. Homepage work overlaps #55 and #71. |
| [#74](https://github.com/Rafiqual69/Zootasks/pull/74) | 655d4476bb24161cd0724232271734140323c91d | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; Draft; merged=false | PostgreSQL Financial Verification 40273069238 passed; Security Gate 40273069246 failed; Security Review 40273069281 failed. This branch restores the missing 0004 migration. |
| [#75](https://github.com/Rafiqual69/Zootasks/pull/75) | c935b5cd06167890aa8849c4cc378ca06ad64747 | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; Draft; merged=false | Security Gate 41617278377 passed; Security Review 41617278184 passed; PostgreSQL Financial Verification 41617278403 passed. Later exact-head Security Review push run 42505462940 passed. Its migration file changes 0005 to depend on 0003 rather than restoring 0004; reconcile this against #74 before selecting one migration lineage. |
| [#77](https://github.com/Rafiqual69/Zootasks/pull/77) | 96d10046e0eaeb8a6b7895695b51f7841badcce9 | security/multi-provider-review-base-20261108 (recorded base 550a8aede970812e3dc2ae8f1e9076f70f95a0ef) | Open; Draft; merged=false | Security Gate push run 42505990731 passed; Security Review PR run 42505995213 passed; PostgreSQL Financial Verification PR run 42505995188 passed. This is stacked, not main-based. Its recorded base is one commit behind the current base branch tip 9952c85fdbe9b397fbd3b805cb4b53bff5f43081; update/retest against the current base before review. |
| [#47](https://github.com/Rafiqual69/Zootasks/pull/47) | fdc4e0ee88199c910193da8c7cfccc1bbad174f6 | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open; not Draft; merged=false | Security Gate 37926180609 failed; Security Review 37926180563 failed; PostgreSQL Financial Verification 37926180491 failed. Railway deployment configuration is therefore not release evidence. |

**Stack and release interpretation**

- #52 has green branch-local checks but targets an unmerged migration branch, not main.
- #53 is stacked on #41; its dedicated promotion regression does not replace the missing full Security Gate and PostgreSQL Financial Verification.
- #69 is stacked on #66 and its exact-head checks fail.
- #77 is stacked on a security review base containing a long chain of security commits; it is not a clean main-based candidate, and its base advanced after the PR's recorded base SHA.
- #74 and #75 propose different fixes for the missing task migration. Choose one reviewed lineage after comparing migration operations and fresh/legacy rehearsal results; do not infer safety from a green PostgreSQL job alone.
- #56, #57, #71 and #73 are existing overlapping research/Owner/homepage work. Keep using these PRs rather than creating duplicate product PRs.
- A passing PR workflow is not merge authorization. Main currently has no branch protection/rulesets, no exact-head PostgreSQL verification, and no recorded independent review gate in this refresh.

### 2. Railway inventory

The Railway project inventory returned the ZooTasks project with two configured services: PostgreSQL and Redis. The environment status reported both services as **Offline**, and no active application deployment was returned. No web/application service appeared in the service list. The environment descriptor had no latest deployment. This is an inventory/status observation, not proof that an external deployment cannot exist. No Railway variables, secrets, customer data, or logs were read.

**Implication (hypothesis):** before describing ZooTasks as cloud-hosted or 24/7, verify a dedicated web service, worker/bot service if required, health checks, database/Redis connectivity, backups and restore tests, deployment health, and a monitored rollback path. Do not deploy as part of this research run.

### 3. Official-source benchmark refresh

All links below were checked on **2026-11-25**. Where an official page exposes an update date, that date is noted. Source statements are evidence about the named provider only; the ZooTasks recommendation is a hypothesis until implemented and measured. Region, account plan, payout eligibility and current terms must be rechecked before copying any fee or payment rule.

| Checked | Official source | Observable feature — evidence | ZooTasks implication — hypothesis |
|---|---|---|---|
| 2026-11-25 | [Upwork freelancer fee](https://support.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee) and [payment protection](https://support.upwork.com/hc/en-us/articles/211062568-How-Upwork-protects-your-payments) | Contract-level fee disclosure and distinct hourly/fixed-price protection rules. | Lock the fee formula at claim/contract acceptance; show gross, deductions, net, eligibility, evidence requirements and protection limits before work starts. |
| 2026-11-25 | [Fiverr — how it works for freelancers](https://help.fiverr.com/hc/en-us/articles/34069565843985-How-Fiverr-works-for-freelancers) | The official guide describes the freelancer's 80% share, a clearing period, order states and a Resolution Center. | Separate pending, cleared and withdrawable earnings; display the review/payout timeline and an appeal path. |
| 2026-11-25 | [Freelancer.com fees and charges](https://www.freelancer.com/feesandcharges) and [milestone payments](https://www.freelancer.com/support/payments/how-do-i-get-paid) | Fee rules vary by project/payment type; milestone funding and release are separate steps. | Itemize client charges and worker deductions; reserve funds per milestone and show who can release them. |
| 2026-11-25 | [PeoplePerHour commission policy](https://support.peopleperhour.com/hc/en-us/articles/205218337-Freelancer-commission-fees) | The official page describes lifetime-buyer commission tiers; the page is old and should not be treated as a current rate card. | Loyalty pricing is only an experiment hypothesis; verify current policy, buyer/worker impact and contribution margin before testing. |
| 2026-11-25 | [Toptal talent FAQ](https://www.toptal.com/freelance-jobs/faq) | Screening and talent matching are explicit parts of the marketplace; the FAQ describes rate-setting and payment handling. | Use transparent skill/quality qualification and a reviewable eligibility process; never imply a screening badge guarantees future work. |
| 2026-11-25 | [Workana commission calculation](https://help.workana.com/hc/en-us/articles/360041235874-How-is-the-commission-calculated-at-Workana) | The page updated 2026-09-17 describes tiered freelancer commission and a client-side fee. | If testing repeat-client discounts, show the formula and both sides' effective cost; do not assume tiers improve ZooTasks' economics. |
| 2026-11-25 | [Contra fees overview](https://help.contra.com/en/articles/9322934-fees-overview) and [pricing](https://contra.com/pricing) | Platform positioning separates commission from plan, payment-processing and payout-related charges. | Distinguish platform fee, provider fee, payout fee and optional plan costs on the receipt; verify country/payment-rail availability. |
| 2026-11-25 | [Guru SafePay](https://www.guru.com/help/employer/release-funds-from-safepay/) and [Guru WorkRoom](https://www.guru.com/help/freelancer/managing-your-job/) | SafePay funding and WorkRoom records provide a structured place for agreements, work and payment release. | Make task scope, funded amount, evidence, review and release state visible; keep dispute evidence attached to a versioned task record. |
| 2026-11-25 | [Airtasker service fee](https://support.airtasker.com/hc/en-us/articles/200294499-What-is-the-service-fee) and [connection fee](https://support.airtasker.com/hc/en-us/articles/360031769372-What-is-the-Connection-Fee) | Worker and customer-side fees are distinct and jurisdiction-specific. | Show payer, purpose and amount for every fee; never transplant one country's fee schedule into Bangladesh. |
| 2026-11-25 | [Taskrabbit invoice fees](https://support.taskrabbit.com/hc/en-us/articles/46260407116955-I-d-Like-To-Understand-The-Fees-On-My-Task-s-Invoice) and [Trust & Support Fee](https://support.taskrabbit.com/hc/en-gb/articles/46260504648731-What-s-the-Taskrabbit-trust-support-fee) | Customer invoices separate a service fee from a Trust & Support fee; the display can vary with local pricing law. | Keep payment and dispute records on-platform; explain each fee and the conditions for any platform protection. |
| 2026-11-25 | [Clickworker payment options](https://support-workplace.clickworker.com/support/solutions/articles/80000672350-what-payment-options-do-i-have-) | Payment method, threshold, verification and availability depend on country and payment route. | Show only payout methods actually enabled for the member's country, plus threshold, fee and expected processing window before work begins. |
| 2026-11-25 | [Prolific minimum hourly reward](https://participant-help.prolific.com/en/articles/445043-underpaying-studies) and [payment timing](https://participant-help.prolific.com/en/articles/445059-when-will-i-be-paid-for-a-study) | Minimum/recommended hourly reward and a defined review/auto-approval policy are published for participants. | Show estimated minutes, effective reward per hour, eligibility and review deadline before claim; create a timeout/escalation policy for unreviewed work. |
| 2026-11-25 | [Toloka task rules](https://toloka.ai/docs/guide/unwanted/) and [user agreement](https://toloka.ai/tolokers/user-agreement-january-2025) | Task moderation and acceptance/rejection conditions are documented; the linked agreement is dated January 2025. | Moderate prohibited/deceptive tasks before publication. Re-verify current agreement and country/payout rules before adopting any timing or rejection policy. |
| 2026-11-25 | [UserTesting — where is my payment?](https://support.usertesting.com/hc/en-us/articles/4405125498003-Where-s-my-payment) | Contributor help describes payment timing and task-level payment status. | Show task-level payment state, expected date and a clear delay-report route; do not promise a universal payout time across countries. |
| 2026-11-25 | [Microworkers FAQ](https://www.microworkers.com/faq.php) | The FAQ documents withdrawal conditions, verification and payment history; methods and thresholds can vary. | Explain KYC and withdrawal thresholds before work; separate earned, approved and withdrawable amounts. |
| 2026-11-25 | [Linear Insights](https://linear.app/docs/insights) and [audit log](https://linear.app/docs/audit-log) | Work tracking includes cycle/lead-time style metrics and a role-gated audit history. | Track task review age, approval time, dispute time and moderation backlog; give audit search only to authorized roles. |
| 2026-11-25 | [Supabase Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) and [platform audit logs](https://supabase.com/docs/guides/security/platform-audit-logs) | RLS requires both suitable grants and policies; the service role bypasses RLS. Audit events identify actor/action/target. RLS guidance was updated 2026-11-24. | Test grants and policies together for every exposed table; keep privileged service credentials server-side; audit sensitive reads/writes with safe metadata. |
| 2026-11-25 | [Vercel preview deployments](https://vercel.com/docs/deployments/sharing-deployments) and [deployment protection](https://vercel.com/docs/deployment-protection) | Preview and production environments can be separated and access to previews can be protected. | Use isolated preview environments and require authorization before exposing private test data or promoting a build. |
| 2026-11-25 | [Cloudflare managed WAF rules](https://developers.cloudflare.com/waf/managed-rules/) and [rate limiting](https://developers.cloudflare.com/waf/rate-limiting-rules/) | Managed rules and configurable rate limits provide layered request filtering; rule availability depends on plan. | Apply targeted limits to login, task claim, proof submission and withdrawal endpoints; tune false positives and do not assume paid-plan features. |
| 2026-11-25 | [Cloudflare Bot Management](https://developers.cloudflare.com/bots/get-started/bot-management/) | Enterprise Bot Management exposes a per-request score, but a score does not block traffic by itself; a separate WAF rule must act on it. | Treat bot scores as signals, not authorization. Combine velocity, account, task and payment signals with reviewable policy decisions. |
| 2026-11-25 | [GitHub ruleset requirements](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) | Rulesets can require PRs, reviews, status checks and other merge conditions, with explicit bypass controls. | Protect main with required exact-head security and PostgreSQL checks, independent review, stale-approval dismissal and minimal audited bypass. |
| 2026-11-25 | [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) and [Playbook](https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook) | The voluntary framework organizes risk work as Govern, Map, Measure and Manage; NIST says AI RMF 1.0 is being revised. | Maintain an AI risk register, named owners, impact assessments, test evidence, residual risk and rollback/incident actions; version the mapping as NIST updates it. |
| 2026-11-25 | [OWASP Agent Control Standard](https://genai.owasp.org/resource/agent-control-standard-acs/) | ACS describes inspectable, traceable agents and middleware hooks for declarative runtime policy enforcement. | Enforce tool permissions outside model prompts; log the policy decision and bind human approvals to the exact action and parameters. |
| 2026-11-25 | [OWASP AISVS 1.0](https://owasp.github.io/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/) | AISVS 1.0 (June 2026) defines 191 testable requirements across 12 chapters and three verification levels, including identity, orchestration, MCP and monitoring. | Map applicable requirements to versioned acceptance tests; target at least Level 2 for production AI that handles personal or consequential data, alongside ordinary application-security controls. |
| 2026-11-25 | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | WCAG 2.2 is a testable W3C accessibility standard covering keyboard, focus, interaction and content accessibility. | Set WCAG 2.2 AA as the design target; test keyboard, screen-reader, mobile, contrast, focus and error recovery on real flows. |
| 2026-11-25 | [Amazon Mechanical Turk closure FAQ](https://www.mturk.com/help) — discontinued-platform lesson only | The official FAQ states MTurk permanently closed on 2026-09-30; worker payment preferences can be verified through 2026-11-30 and transaction history is stated to remain available until 2027-01-28. | Do not list MTurk as an active competitor or rely on stale marketplace assumptions. Design clear wind-down, worker payment and transaction-history retention procedures. |
| 2026-11-25 | [Bangladesh Personal Data Protection Act, 2026](https://bdlaws.minlaw.gov.bd/act-1692.html) | The official BDLaws text confirms Act No. 63 of 2026, dated 2026-04-10. Section 1 applies to specified Bangladesh-linked data subjects and processing, including some processing outside Bangladesh connected with services to people in Bangladesh. It deems the Act effective from 2025-11-06 except sections 23 and 31–35, which take effect on a date set by Government Gazette notification after 18 months from issuance. | Map the Act's lawful processing bases, data-subject rights, controller/processor duties, security, retention, records, breach response and cross-border provisions to the actual product. Verify the Gazette commencement notice for deferred sections 23 and 31–35 before relying on them. |
| 2026-11-25 | [Bangladesh Cyber Security Act, 2026](https://bdlaws.minlaw.gov.bd/act-1710.html) and [2026 amendment Gazette](https://www.dpp.gov.bd/bgpress/index.php/document/get_extraordinary/62172) | The official Laws of Bangladesh page identifies Act No. 81 of 2026; the Government Press lists a 2026 amendment Act No. 99. | Review cyber incident response, access controls, evidence preservation and any applicable critical-infrastructure obligations against the current consolidated text. |
| 2026-11-25 | [Bangladesh Labour Act, 2006 — current text](https://bdlaws.minlaw.gov.bd/act-print-952.html) and [section 175](https://bdlaws.minlaw.gov.bd/act-print-952/section-print-28053.html) | The official text records 2026 amendments; section 175 includes self-employed, daily/temporary and digital labour-platform workers for the purposes of that chapter. | Do not assume that calling members “independent contractors” settles their legal status. Obtain Bangladesh labour counsel's classification and worker-rights review for the actual task model. |
| 2026-11-25 | [Consumer Rights Protection Act, 2009](https://bdlaws.minlaw.gov.bd/act-print-1014.html) | The official law text establishes consumer-protection and complaint mechanisms. | Publish accurate prices, fee payer, cancellation/refund rules, task-owner obligations and a reachable complaint/dispute path; counsel should assess the platform's role in each transaction. |
| 2026-11-25 | [Bangladesh Bank PSP/PSO licensing procedure](https://www.bb.org.bd/aboutus/regulationguideline/psd/pso_psp_03022019.pdf), [Payment Systems Department](https://www.bb.org.bd/en/index.php/financialsystems/paysystems), and [Payment Systems Report 2025](https://www.bb.org.bd/pub/annual/psdreport/paymentreport_dec2025.pdf) | Bangladesh Bank's 2025 Payment Systems Report and 2024–25 Annual Report confirm the Payment and Settlement System Act, 2024 (Act No. 9 of 2024), published 2024-07-04 and activated 2024-12-31. Bangladesh Bank licenses PSPs and PSOs; its guidance also covers merchant acquiring/escrow services and prepaid instruments. One general Bangladesh Bank webpage still contains older text saying the bill is in process, so use the later reports, Gazette and current circulars rather than that stale paragraph. | Use a properly authorized bank/PSP/PSO for payment and settlement. Have counsel determine whether the proposed task reserve, wallet, stored value, advance-payment instrument, merchant acquiring, trust/escrow-like funds or cross-border payout triggers approval or licensing. Do not issue a stored-value product or hold trust funds on an assumption that a marketplace label exempts it. |
| 2026-11-25 | [NBR Income Tax Acts](https://nbr.gov.bd/regulations/acts/income-tax-acts) and [authentic English Income Tax Act, 2023](https://nbr.gov.bd/uploads/acts/Income_tax_act_2023.pdf) | NBR's official list includes the Authentic English Text of the Income Tax Act, 2023 dated 2025-11-20 and 2025 amendment instruments. | Have a Bangladesh tax adviser check the latest Finance Act/SROs, withholding, VAT, platform-fee treatment, worker tax reporting and cross-border remittance before pricing or payout changes. |

### 4. Product design decisions to carry forward

#### Public website

- Homepage must distinguish live, funded tasks from examples, previews and unavailable tasks. Never show fabricated counts, fake scarcity or guaranteed-income claims.
- Each task card should show category, skill/eligibility, estimated active minutes, gross reward, every known deduction, estimated worker net, approval window, payout route and proof requirements before a member claims it.
- Show a **funding verified** label only when a server-side reserve or authorized provider confirmation proves the remaining worker reward is funded. Do not call an internal database number “escrow” unless the legal/payment structure supports that term.
- Task detail should explain scope, accepted proof, prohibited behavior, rejection reasons, appeal route, cancellation/expiry rules and the time estimate's basis.
- Public trust pages should explain platform fees, provider fees, privacy, complaints, refunds, task-owner duties and country-specific payout availability.

#### Member experience

- Keep available, claimed, submitted, under review, approved, rejected, disputed, paid and withdrawable states separate.
- Show gross reward, known fee, estimated net reward and estimated time-to-earn before claim. After completion, replace estimates with actual recorded values.
- Show task-level submission, review, approval and payout timestamps. Report median and percentile time-to-earn using a clearly defined cohort and time window.
- Keep pending, approved, withdrawable and lifetime earnings separate; every total must reconcile to an authorized statement or ledger view.
- Offer passkeys, session review, account recovery, data access/deletion request routes, and task/user reporting.
- Low-bandwidth defaults: server-rendered core content, progressive enhancement, compressed images, no autoplay, small payloads, explicit retry states, idempotent submissions, keyboard access and readable validation errors.

#### Owner panel — read-only first

1. **Overview:** funded task value, reserved worker rewards, approved worker rewards, gross platform fees, refunds/reversals, provider costs, tax/VAT liabilities, support/fraud costs, hosting/AI costs and contribution margin. Each metric needs a definition, source, date range and reconciliation status.
2. **Funding and capacity:** funded coverage, reserved slots, completed slots, remaining capacity, budget utilization, expired/cancelled reservations and exact-boundary exceptions.
3. **Task quality:** completion/approval rate, evidence failure categories, rework, review age, median approval time, dispute rate, appeal reversal rate and repeat buyer rate.
4. **Worker fairness:** median net reward per active hour by task type, time to first task, time to first approved earning, time to first payout, rejection rate and payout delay. Suppress small cohorts and never expose a worker's private risk score to general support.
5. **Finance:** read-only ledger, reconciliation exceptions, refund/chargeback queue, payout status and versioned fee policy. No manual balance editing and no direct wallet writes from the dashboard.
6. **Access and governance:** role grants, passkey/session status, pending dual-control actions, access reviews, audit search, retention policy, backup/restore status and incident freeze controls.
7. **AI policy:** approved models/tools, scoped identities, policy version, decision outcome, human approvals, blocked actions, cost/velocity limits and rollback status. Do not display prompts, credentials or full private submissions.

#### Unit economics and the 15% proposal

The proposed 15% platform-fee pool remains an **unvalidated allocation hypothesis**: 10% proposed for the Owner account and 5% proposed for development, AI and operating costs. It is not net profit, does not prove positive contribution margin, and is not a profitability guarantee.

Before testing it, define the fee denominator, who pays the fee, whether the fee is taken from buyer funding or a separately disclosed platform charge, rounding, refunds, chargebacks, taxes, provider costs, payout costs and revenue-recognition timing. Never reduce a worker's accepted reward after claim.

For each settled task, report separately:

- buyer funding received and still available;
- worker reward reserved, approved, paid and reversed;
- platform fee earned under the disclosed policy;
- provider and payout costs;
- refunds and chargebacks;
- taxes/VAT/withholding payable;
- attributable support, fraud, infrastructure and AI costs;
- contribution margin after defined variable costs.

Only call a number “contribution margin” when its formula and included costs are documented. Accounting net profit requires the full accounts and applicable accounting treatment.

### 5. Financial, capacity and governance invariants

- Before a task becomes claimable, verify available authorized funding covers all outstanding worker reward obligations and any required reserve.
- Define capacity as completed/approved slots plus active reserved slots; enforce completed plus active reservations not exceeding max workers.
- Define the reward ceiling as approved reward already committed plus the maximum reward exposure of active reservations not exceeding the funded budget.
- Lock the relevant task/promotion row or reservation record during competing claims and approvals. Use database constraints where they can express the invariant.
- On claim, reserve capacity and reward budget atomically. On approval, convert a reservation to a completed slot and create exactly one earning ledger entry. On rejection, cancellation or expiry, release the reservation exactly once. Make every transition idempotent and replay-safe.
- Never use a client-supplied balance, slot count, device ID, status or approval flag as authority. Recompute and authorize on the server.
- Wallet and payout history must be append-only. Corrections use compensating ledger entries with reason and approval; do not edit historic balances or delete transaction rows.
- Keep withdrawal request, approval and payment permissions separate. A person requesting a high-risk action must not be the sole approver of that action.
- RBAC should distinguish Owner, Finance Approver, Finance Viewer, Support, Moderator, Security Reviewer, Analyst and Developer Read-only. Default deny; scope access to the smallest required object and action.
- Owner access should use server-verified passkeys/WebAuthn, step-up authentication for sensitive operations, explicit revocation and tested recovery. A trusted device is an input channel, not blanket authorization.
- High-risk changes require dual control: payout policy, fee policy, reward/budget overrides, privileged role grants, key changes, destructive actions, production migrations and deployment promotion.
- Approval records must bind actor, action, target, normalized parameters, policy version, expiry and one-time nonce. Reject replay, parameter substitution and self-approval.
- Audit events should be append-only and record actor, action, target, timestamp, outcome, policy version and safe metadata. Never put passwords, tokens, cookies, recovery codes, identity documents, bank details, raw private submissions or unnecessary PII in audit events.
- AI tools must be allowlisted and scoped. AI cannot directly mutate wallets, payouts, reward budgets, privileged credentials, production migrations or deployment state. External webpages, uploaded task content and user instructions are untrusted input; the runtime policy engine must enforce decisions outside the model context.
- Use privacy thresholds for aggregate earnings/risk reporting; never expose small-cohort data that could identify a member.

### 6. Ranked product ideas and measurable acceptance

| Rank | Product idea | Acceptance / guardrail | Measurement |
|---:|---|---|---|
| P0 | Release integrity and migration lineage | Main protected; required review and exact-head Security Gate, Security Review and PostgreSQL Financial Verification; one reviewed migration lineage; fresh and disposable-legacy rehearsal; no stale-run substitution | 100% required checks pass on the final candidate SHA; zero unresolved migration graph/constraint differences; independent review recorded |
| P0 | Funded-task and capacity proof | No claim unless funding and capacity reservation succeed atomically; rejection/expiry releases once; approval credits once | Zero over-budget approvals, duplicate credits or capacity oversubscription in exact-boundary, replay and concurrent-last-slot tests |
| P1 | Reward/time/net task cards | Before claim, display reward, known deductions, net estimate, active-minute estimate, eligibility and approval/payout rules; accepted reward cannot change after claim | Track task detail-to-start, valid completion, median net reward per active hour and worker confusion/support reports; stop if net reward/hour or task quality falls |
| P1 | Member earning and payout timeline | Distinct pending/approved/withdrawable/paid states with task-level timestamps and reasoned exceptions | Median and P95 submission-to-review, approval-to-payout, time-to-first-approved-earning and payout failure rate |
| P1 | Owner read-only unit-economics panel | Read-only source data, metric definitions, reconciliation status, no balance editing or payout actions | Ledger-to-dashboard reconciliation difference; stale-data age; zero unauthorized financial writes |
| P1 | Task quality and fair dispute flow | Clear proof requirements, reason-coded rejection, appeal, reviewer SLA and audit trail | Valid completion rate, rejection rate, appeal reversal, dispute rate, resolution time and repeat buyer rate |
| P2 | Owner passkeys, RBAC and dual control | Server-side permission tests, step-up, revocation/recovery, independent approval and replay protection | Zero unauthorized access/action in negative tests; 100% dual-control coverage for designated high-risk actions |
| P2 | Privacy and low-bandwidth accessibility | Data minimization, small-cohort suppression, safe audit, WCAG 2.2 AA review and slow-network retry tests | Zero sensitive fields in unauthorized views/audit; keyboard/screen-reader/mobile checks; successful retry without duplicate submission |
| P3 | AI-assisted moderation and task matching | Shadow mode first; tool allowlist; deterministic policy engine; human review for consequential decisions; kill switch | Precision/recall on reviewed samples, false-positive appeal rate, cost per reviewed task and zero unauthorized tool writes |

### 7. Phased implementation plan

1. **Phase 0 — Release and data integrity.** Resolve the main migration graph with one reviewed approach; compare migration operations, constraints and data semantics on a fresh database and disposable legacy copy. Protect main and configure exact-head release checks. Do not migrate or deploy production.
2. **Phase 1 — Read-only measurement.** Define event names, metric formulas, cohort rules, data retention and access roles. Build sanitized aggregate queries and reconcile them to the existing ledger. No financial behavior changes.
3. **Phase 2 — Public/member experience.** Update one existing homepage/task-flow PR after duplicate review. Add live-versus-example labels, fee/net/time disclosure, task proof and status clarity, payout country checks, mobile/keyboard/low-bandwidth behavior.
4. **Phase 3 — Owner read-only panel.** Reuse the existing #57 dashboard direction only after its render/accessibility and authorization gates pass. Add metric definitions, reconciliation status and task quality/worker fairness views. No write actions.
5. **Phase 4 — Funding and capacity state machine.** Only after the written budget definition and legal/payment structure are approved, implement atomic reservation, approval, release and idempotent ledger transitions on a dedicated branch. Add PostgreSQL concurrency and exact-boundary tests. No production migration without explicit authorization.
6. **Phase 5 — Owner governance.** Implement role separation, passkey enrollment/recovery/revocation, step-up auth, append-only audit and dual-control workflow. Test negative permissions, replay, parameter substitution and account recovery.
7. **Phase 6 — AI control plane and measured experiments.** Keep AI read-only/shadow-mode first. Add runtime tool policy, scoped identities, human review, cost/rate limits and kill switch. Run small UX experiments only with baseline and rollback criteria.

### 8. Bangladesh and international legal review

The current official source set includes the Personal Data Protection Act, 2026, Cyber Security Act, 2026 and its 2026 amendment, Bangladesh Labour Act, 2006 as amended in 2026, Consumer Rights Protection Act, 2009, Bangladesh Bank payment-system rules and the 2025 Payment Systems Report, and NBR's Income Tax Act, 2023. The Labour Act's current section 175 expressly includes digital-platform workers for the purposes of that chapter; the platform should not assume that an “independent contractor” label resolves classification or worker rights.

Before launch or monetization, obtain qualified Bangladesh advice on the actual operating model: worker classification and terms, payment/settlement licensing, merchant acquiring and escrow/trust-fund rules, prepaid-instrument restrictions, use of licensed PSP/bank partners, AML/CFT/KYC, consumer fee and refund disclosure, VAT and withholding, foreign exchange and cross-border payouts, privacy lawful basis and transfers, breach response, data retention, and any critical-infrastructure designation. Verify current consolidated Gazette text, commencement notices and Bangladesh Bank circulars rather than relying on old webpage paragraphs or unofficial summaries.

For international users or clients, map the actual jurisdictions and contracts to applicable privacy, consumer, tax, payment, accessibility and security obligations. NIST AI RMF is voluntary risk-management guidance; OWASP ACS and AISVS are security resources, not legal certification. WCAG 2.2 AA is a product target, not a claim of compliance until tested.

### 9. Run record and limits

This is a dated research/design refresh and a documentation-only update to the existing Draft PR #56. It does not implement application code, change permissions, alter wallet/payout/reward-budget logic, edit migrations, access production data, run production migrations, deploy, merge, or manually dispatch/rerun workflows. The new document commit will have a new SHA; all previous PR #56 workflow results are stale for that new head. Automatic CI triggered by the branch update must be checked against the resulting exact SHA. Keep the PR Draft and do not infer release readiness from documentation-only changes or prior runs.



## Research board run — 2026-11-26

**Checked date:** 2026-11-26 (Asia/Dhaka).  
**Mode:** read-only repository, issue, PR, workflow-metadata, Railway inventory/health, and official public-source research. No .env, credentials, customer/financial records, private logs, workflow logs, or artifacts were read. Retrieved content was treated as untrusted data.

### Current repository and release state

- Default branch main is still at aa548d148d36df0c8ed2af3d58d8e1f0d8e38512 (commit dated 2026-10-06).
- GitHub reports main as unprotected (protected: false). Required branch protection/ruleset enforcement is not established.
- The exact-main-SHA Actions API returned 11 runs: 10 Security Review failures and one Security Gate failure. No PostgreSQL Financial Verification run was returned for this exact SHA. Examples: [Security Gate #37483388868](https://github.com/Rafiqual69/Zootasks/actions/runs/37483388868), [Security Review #40273321095](https://github.com/Rafiqual69/Zootasks/actions/runs/40273321095). The run list is metadata only; no raw logs were opened.
- Current main's task migration graph is incomplete: tasks.0005_alter_taskclaim_task depends on tasks.0004_protect_claim_history, but that 0004 source migration is absent from main. The current 0005 migration changes the TaskClaim.task FK to PROTECT; the current model still has CASCADE for both task and worker.
- Main's Promotion model has reward, budget, max_workers and completed_workers, but no reserved_workers. The current start_promotion view increments completed_workers when a claim is created, before approval. The public progress display derives remaining capacity from completed_workers. Main therefore does not establish a verified approved-completion count, reservation state, or cumulative reward-budget invariant.
- Issues [#43](https://github.com/Rafiqual69/Zootasks/issues/43), [#45](https://github.com/Rafiqual69/Zootasks/issues/45), [#46](https://github.com/Rafiqual69/Zootasks/issues/46), [#48](https://github.com/Rafiqual69/Zootasks/issues/48), and [#54](https://github.com/Rafiqual69/Zootasks/issues/54) remain open. Issue comments describe branch-local progress; that does not mean the work is on main.

### Exact-head PR and workflow register

All listed PRs were open and Draft at inspection time; none was merged. Workflow outcomes below are only accepted when the run's head SHA exactly matches the PR head. A green run on another commit or base is not substituted.

| PR | Exact head SHA | Base branch | Exact-head workflow evidence | Board status |
|---:|---|---|---|---|
| #52 | b14aece21769fc7c3782e9326b3a0fc5213730b4 | fix/restore-task-claim-migration-20261009 | Security Gate #39065416499 pass; Security Review #39065416663 pass; PostgreSQL Financial Verification #39065416559 pass | Stacked on a migration-fix branch, not main. Useful branch-local evidence only. |
| #53 | 4d5b5e58495263064c71dea40911bc4b8403732c | security/full-integrated-security-board-20261007 | Security Review push #39146130309 pass; Promotion PostgreSQL Regression #39146133710 pass | Security Gate and full PostgreSQL Financial Verification are missing on this exact head. Stacked on #41; independent review remains outstanding. |
| #55 | a33432cb40ced36ad152a7a31e917c80953b70ce | main | Security Gate #39147130401 fail; Security Review #39147130469 fail; PostgreSQL Financial Verification #39147130476 fail | Homepage sample-label change is still Draft. |
| #56 | 449fd5cb004a75d84be24e5efa3c56e44ffd5677 | main | Security Gate #45541962875 fail; Security Review #45541962872 fail; PostgreSQL Financial Verification #45541962866 fail | This research PR is documentation-only, but the three exact-head gates failed. A documentation-only scope does not turn failed release checks into passes. |
| #57 | 3a5c3f0cc0425fb06666ab075fef69da1f6ee96e | main | Security Review #39148226226 fail; Security Gate #39148226265 fail; PostgreSQL Financial Verification #39148226231 fail | Existing Owner dashboard template proposal; do not create a duplicate dashboard PR. Browser/accessibility review is also outstanding. |
| #62 | be7de84d525b4c44012f6102c9d4968a9a42aaec | main | Security Gate #39477083819 pass; Security Review #39477083798 pass; PostgreSQL Financial Verification #39477083843 pass | One green migration-lineage candidate; still Draft and requires independent migration/data-semantics review. |
| #66 | e7e4b3eacd39aa0b6146354ac2545c491fa25934 | main | Security Gate #40011292003 pass; Security Review #40011291937 pass; PostgreSQL Financial Verification #40011291839 pass | Another green candidate containing the missing 0004 migration and broader changes; still Draft. |
| #69 | df6311bd81388eafc29da45de1cbabf68b8ebc83 | security/ci-ephemeral-secret-20261022 | Security Gate #40171986340 fail; Security Review #40171986327 fail; PostgreSQL Financial Verification #40171986317 fail | Stacked on #66 and currently failing all three exact-head gates. |
| #74 | 655d4476bb24161cd0724232271734140323c91d | main | PostgreSQL Financial Verification #40273069238 pass; Security Gate #40273069246 fail; Security Review #40273069281 fail | Restores 0004 but is not release-ready. |
| #75 | c935b5cd06167890aa8849c4cc378ca06ad64747 | main | Security Gate #41617278377 pass; Security Review #41617278184 pass; PostgreSQL Financial Verification #41617278403 pass | All three exact-head PR workflows passed. Still Draft; migration semantics conflict with the 0004-restoration candidates. |
| #77 | 96d10046e0eaeb8a6b7895695b51f7841badcce9 | security/multi-provider-review-base-20261108 | Security Gate push #42505990731 pass; Security Review push #42505990723 and PR #42505995213 pass; PostgreSQL Financial Verification PR #42505995188 pass | All three workflow types have exact-head passes. However, the base branch has advanced from the PR's recorded base SHA 550a8aede970812e3dc2ae8f1e9076f70f95a0ef to 9952c85fdbe9b397fbd3b805cb4b53bff5f43081. Reconcile and retest against the current base before review/merge. |

Related duplicate/conflicting migration PRs also remain open: #50 and #58 restore a 0004 migration; #62 and #66 contain 0004-based candidates; #74 restores 0004; #75 instead changes 0005's dependency to 0003. PR #52 is stacked on a separate migration branch. Do not merge these branches together by title or green status alone.

**Migration decision:** #74's 0004 migration changes both TaskClaim.task and TaskClaim.worker to PROTECT. #75 changes 0005 to depend directly on 0003 and changes only TaskClaim.task to PROTECT; it does not provide the same worker-FK protection. #62/#66 also contain 0004-based migration candidates. Compare migration operations, current model state, FK behavior, legacy rows, constraints, indexes, and fresh/disposable-legacy database results before selecting one lineage. No candidate is approved by this board for merge or production migration.

### Railway production inventory and health

The ZooTasks production environment contains only Postgres and Redis. Both services report offline, have no active/latest deployment, and have no pending environment changes. Each has a persistent volume. No web application or worker/bot service is listed. No runtime logs or variables were inspected. This is not evidence of a running 24/7 application.

### Official-source benchmark refresh

**Checked on 2026-11-26.** Each row separates an observable statement on an official public page (**evidence**) from a proposed ZooTasks response (**hypothesis**). Fees, payment methods, product availability, regional coverage and terms can change. Do not assume any listed payout route is available in Bangladesh without checking the provider and applicable law.

| Checked | Official source URL | Observable feature — evidence | ZooTasks implication — hypothesis |
|---|---|---|---|
| 2026-11-26 | [Upwork service fee](https://support.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee) and [payment protection](https://support.upwork.com/hc/en-us/articles/211062568-How-Upwork-protects-your-payments) | Contract fees vary; the fee is disclosed before commitment. Fixed-price milestones are funded before work and have approval/dispute handling, including an automatic release rule. | Show the exact fee and net reward before claim; show a funded state only from an authoritative payment/reserve record; publish review and dispute timing. |
| 2026-11-26 | [Fiverr payment terms](https://www.fiverr.com/legal-portal/legal-terms/payment-terms-of-service) and [earnings page](https://help.fiverr.com/hc/en-us/articles/9234443621137-Your-earnings-page) | Standard seller earnings are credited at 80% of the purchase amount; the earnings area separates available and future payments and provides transaction history. | Separate gross buyer spend, worker reward, fees, pending funds and withdrawable funds. Never imply a pending balance is paid. |
| 2026-11-26 | [Freelancer.com FAQ](https://www.freelancer.com/faq/view.php) | Milestone payments remain pending until release; disputes are available when parties cannot agree. | Use funded milestone/task proof, approval states, and a documented dispute route. |
| 2026-11-26 | [PeoplePerHour escrow](https://support.peopleperhour.com/hc/en-us/articles/17826151118097-What-is-Escrow-and-how-is-it-used) | Buyer funds are deposited before work; release follows approval, specified automatic-invoice conditions, or dispute resolution. The page distinguishes release from the later clearing period. | Keep funded, approved, released and withdrawable as separate states; disclose the applicable review and clearing rules. |
| 2026-11-26 | [Toptal screening](https://www.toptal.com/top-3-percent) | Toptal describes language/communication, skills, live screening and test-project stages; its stated process takes 3–8 weeks. | Use evidence-based skill levels and quality checks for specialist tasks. Do not copy its acceptance-rate claim or imply ZooTasks has equivalent screening. |
| 2026-11-26 | [Workana costs](https://help.workana.com/hc/en-us/articles/360040846094-How-much-does-it-cost-to-use-Workana) | The official help page distinguishes freelancer commission, a customer service cost and payment-processing cost that varies by method/country. | Show who pays each fee and calculate country/method-specific costs before confirmation. Recheck the current fee schedule before using rates in pricing. |
| 2026-11-26 | [Contra commission-free payments](https://contra.com/commission-free) and [global payments](https://contra.com/features/global-payments) | Contra advertises no freelancer commission while describing client-side processing and contract fees and several payout methods. | State the fee payer, separate processor charges from platform fees, and avoid describing the whole transaction as cost-free. |
| 2026-11-26 | [Guru SafePay](https://www.guru.com/safepay/) | Employer-funded SafePay can cover tasks, milestones, hours and bonuses; the balance is not necessarily tied to one specific task and arbitration is limited to available funds. | Show verified available funding and dispute coverage accurately. Do not call a shared balance task-specific escrow. |
| 2026-11-26 | [Airtasker service fee](https://support.airtasker.com/hc/en-us/articles/200294499-What-is-the-service-fee) and [payment guidelines](https://support.airtasker.com/hc/en-gb/articles/225553508-What-are-the-Payment-Guidelines) | The service fee is shown in the offer flow and payment history; the payment guidance describes task funding and trust-account handling. | Show the fee and net amount before acceptance and retain a transaction-level fee receipt. |
| 2026-11-26 | [Taskrabbit payment process](https://support.taskrabbit.com/hc/en-gb/articles/46260427597595-How-do-I-pay-my-Tasker) | Payment is handled through the platform after the Tasker submits an invoice; protection applies only to qualifying on-platform bookings/payments. | Keep invoices and payment status visible; explain that off-platform work is outside platform protection. |
| 2026-11-26 | [Clickworker payment methods](https://support-workplace.clickworker.com/support/solutions/articles/80000672350-what-payment-methods-are-available-) | The official page, modified 2026-03-12, lists country-dependent payment methods, weekly bill runs, minimum thresholds and account ownership/KYC requirements. | Check the member's country and supported payout method before they invest time; show thresholds, fees and expected processing separately. |
| 2026-11-26 | [Prolific reward calculator](https://www.prolific.com/calculator) | Prolific states minimum hourly rewards of $8/£6 and says its platform fee is added on top so participants receive the stated hourly rate. | Display estimated active minutes and net reward per active hour; identify whether a fee is paid by the buyer or worker. |
| 2026-11-26 | [Toloka Self-Service Agreement](https://toloka.ai/legal/self-service-agreement) | The agreement, published and effective 2026-04-22, requires project scope, quality criteria, deliverables, timelines and a rate. This is a buyer-side task specification source, not proof of worker payout terms. | Require structured task scope, measurable acceptance criteria, deadline, review rules and budget before publication. Do not infer worker payment guarantees from this agreement. |
| 2026-11-26 | [UserTesting test and payment history](https://support.usertesting.com/hc/en-us/articles/4409767959059-How-do-I-track-my-test-and-payment-history) | Test history records upload time, payment amount, scheduled payment date, rating and feedback; the support page says payments usually arrive about 14 days after a test. | Give each task a timestamped status and payment history, with expected dates clearly labelled as estimates until confirmed. |
| 2026-11-26 | [Microworkers guidelines and FAQ](https://www.microworkers.com/faq-guidelines.php) | The official page describes KYC before withdrawal, method-specific thresholds, payment schedules and sanctions for fake/copy-pasted proof. | State KYC and withdrawal rules before claim; use clear proof standards, reason-coded rejection and appeal rather than opaque quality penalties. |
| 2026-11-26 | [Linear Insights](https://linear.app/docs/insights) | Insights turns issue data into filterable analytics for project resources, cycle trends, bug-fix time and estimation. | Build an Owner dashboard with named metric definitions, date/cohort filters, trend context and data freshness. |
| 2026-11-26 | [Supabase platform audit logs](https://supabase.com/docs/guides/security/platform-audit-logs) and [Auth audit logs](https://supabase.com/docs/guides/auth/audit-logs) | Platform events identify timestamp, actor, action and target; authentication events are separately recorded. Availability and retention vary by plan/storage choice. | Keep append-only audit events with actor, action, target, outcome and safe metadata; set explicit retention and minimize personal data. |
| 2026-11-26 | [Vercel Deployment Protection](https://vercel.com/docs/deployment-protection) | Deployment URLs can be protected with Vercel authentication, passwords or trusted IPs; scope and plan availability differ. | Separate preview from production access; restrict Owner/admin previews and require review before public promotion. |
| 2026-11-26 | [Cloudflare Access policies](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/), [rate limiting](https://developers.cloudflare.com/waf/rate-limiting-rules/) and [Audit Logs v2](https://developers.cloudflare.com/logs/changelog/audit-logs/) | Access policies combine Include, Exclude and Require rules; rate limits can constrain abuse; Audit Logs v2 records actor/action/result/resource with documented retention and coverage limits. | Enforce authorization and abuse controls at runtime; audit sensitive actions and document what is and is not captured. Do not assume every read or failed request is logged. |
| 2026-11-26 | [GitHub rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) | Rulesets can require pull requests, status checks, successful deployments and other branch controls, and can restrict force pushes. | Protect main with required exact-head checks, limited bypass, and a documented release process. |
| 2026-11-26 | [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) and [Playbook](https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook) | NIST's voluntary framework organizes lifecycle risk work as Govern, Map, Measure and Manage. | Maintain an AI risk register with an accountable owner, use context, tests, residual risk, monitoring and rollback condition. |
| 2026-11-26 | [OWASP Agent Control Standard](https://genai.owasp.org/resource/agent-control-standard-acs/) | OWASP ACS, dated 2026-09-01, describes inspectable, traceable agents and runtime-enforced policies through middleware hooks. | Put authorization in a deterministic execution layer outside model context; scope tools/resources and bind approvals to exact operations. |
| 2026-11-26 | [OWASP AISVS](https://owasp.github.io/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/) | The current official page describes AISVS 1.0, released June 2026, with 191 testable requirements across 12 chapters and verification levels 1–3. | Map applicable requirement IDs to tests and review evidence; do not claim certification or compliance merely by referencing the standard. |
| 2026-11-26 | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | WCAG 2.2 is a W3C Recommendation with testable success criteria for accessible content and interaction. | Target WCAG 2.2 AA; combine automated checks with keyboard, screen-reader, mobile and low-bandwidth testing. |
| 2026-11-26 | [Amazon Mechanical Turk official closure FAQ](https://www.mturk.com/help) — discontinued-platform lesson only | Amazon states MTurk permanently closed on 2026-09-30. The page now concerns post-closure worker/requester administration. | Do not count MTurk as an active benchmark. Treat closure as a reminder to plan worker payout completion, records retention, support and orderly wind-down. |

### Bangladesh legal and payment review

This is a product-risk register, not legal advice. Obtain Bangladesh counsel and payment-provider/regulatory advice before holding funds, collecting platform fees, issuing wallet value or changing payout flows.

- [Personal Data Protection Act, 2026](https://bdlaws.minlaw.gov.bd/act-1692.html): the official text identifies Act No. 63 of 2026. It deems most provisions effective from 2025-11-06, while sections 23 and 31–35 require a later Government Gazette commencement date after the stated 18-month period. The definition of personal data includes identifiers, financial and location data. Confirm current Gazette commencement and map lawful basis, rights, controller/processor duties, security, retention and cross-border processing.
- [Cyber Security Act, 2026](https://bdlaws.minlaw.gov.bd/act-print-1710.html): use the current official text for incident handling, authorized security testing and any applicable critical-information-infrastructure obligations. Applicability depends on the actual facts and any designation; do not assume ZooTasks is designated.
- [Bangladesh Labour Act, 2006, Chapter XIII](https://bdlaws.minlaw.gov.bd/act-952/act-chapter-print-1043.html): section 175, as replaced by the Bangladesh Labour (Amendment) Act, 2026, includes self-employed and digital-platform-engaged people for that chapter's trade-union/industrial-relations purposes. Do not overread this as automatically determining worker status for every Labour Act chapter; obtain a fact-specific classification review.
- [Payment and Settlement Systems Act, 2024](https://bdlaws.minlaw.gov.bd/act-1496.html?lang=bn), especially [section 15](https://bdlaws.minlaw.gov.bd/act-1496/section-54115.html): section 15(1) restricts issuing/trading prepaid payment instruments without Bangladesh Bank approval; section 15(2) restricts operating specified platforms involving public investment, lending, storing money or financial transactions without Bangladesh Bank approval. Whether ZooTasks' task funding, wallet, reserve, payout or marketplace model falls within these provisions requires formal legal advice and, where appropriate, Bangladesh Bank clarification. Do not assume that calling an internal balance a wallet, reserve or escrow changes its legal treatment.
- [Bangladesh Bank Payment Systems Report 2025](https://www.bb.org.bd/pub/annual/psdreport/paymentreport_dec2025.pdf) and [Annual Report 2024–2025](https://www.bb.org.bd/pub/annual/anreport/ar2024-2025.pdf) describe licensed PSP/PSO roles and payment/merchant-acquiring/escrow guidance. Use an appropriately authorized bank or provider after confirming the exact product and flow.
- [NBR Income Tax Acts](https://nbr.gov.bd/regulations/acts/income-tax-acts) and official VAT materials should be reviewed for platform-fee, withholding, VAT, worker reporting and cross-border treatment. Consumer-facing fees, cancellation/refund terms and complaints also require review under the [Consumer Rights Protection Act, 2009](https://bdlaws.minlaw.gov.bd/act-print-1014.html).

### Updated product ranking and implementation order

| Rank | Work item | Measurable acceptance |
|---:|---|---|
| P0 | Choose and reconcile one task-claim migration lineage | No missing dependency; fresh database and disposable legacy copy migrate; task and worker FK semantics, constraints, indexes and historical rows independently reviewed; exact-head SG, SR and PostgreSQL gates pass. |
| P0 | Promotion reward-budget and capacity invariants | No claim unless funding and capacity reserve atomically; completed + active reservations never exceed max_workers; approved exposure never exceeds funded budget; zero duplicate credits, over-budget approvals or last-slot oversubscription in replay/concurrency tests. |
| P0 | Main release integrity | Main protected; required SG, SR and PostgreSQL checks required on exact candidate SHA; independent review recorded; missing or stale checks block release. |
| P1 | Worker net reward and time-to-earn | Before claim show gross reward, all known deductions, estimated net, active-minute estimate, eligibility, proof and review rules; measure median and P25 net reward per active hour and P50/P95 claim-to-approved-earning/payout. |
| P1 | Read-only Owner finance and task-quality panel | Every metric has source, formula, time window and freshness; dashboard reconciles to ledger with no unexplained variance; zero write endpoints and zero unauthorized financial reads/writes in negative tests. |
| P1 | Fair review and dispute flow | Reason-coded rejection, appeal and review timestamps; measure P50/P95 review time, dispute rate, appeal reversal rate and payout failure rate. |
| P2 | Owner governance | Server-verified passkeys, step-up authentication, explicit recovery/revocation, least-privilege RBAC and independent dual control for high-risk actions; all negative authorization and replay tests deny. |
| P2 | Privacy and accessibility | Data minimization, small-cohort suppression, safe audit fields, WCAG 2.2 AA review, keyboard/screen-reader/mobile and slow-network tests; retry must not duplicate submissions. |
| P3 | AI-assisted moderation/matching | Shadow mode first; deterministic runtime policy and allowlisted tools; zero unauthorized writes; measure precision/recall, false-positive appeals, cost per reviewed task and human override rate. |

**Implementation sequence:** (0) resolve release/migration and payment-law gates; (1) define metrics and build sanitized read-only queries; (2) improve public/member task reward, fee, time and status disclosures using authoritative existing data; (3) complete the existing #57 read-only Owner dashboard proposal after its checks and authorization review; (4) implement funding/capacity state transitions only after written policy and legal approval; (5) add passkeys/RBAC/dual control; (6) run AI in shadow mode before any limited, human-approved action.

The previously discussed 15% platform-fee pool remains an unvalidated allocation proposal: 10% proposed for the Owner account and 5% for development/AI/operating costs. It is not net profit and is not a profitability guarantee. Validate the denominator, fee payer, provider/payout costs, refunds, chargebacks, taxes, support, fraud, hosting and AI costs first. Never reduce a worker's accepted reward after claim.

### Run boundary

This update changes only this research document on the existing Draft PR #56 feature branch. It does not change application code, permissions, secrets, wallet/payout/reward-budget logic or migrations. No workflow was manually dispatched or rerun; any new CI is automatic and must be checked against the new exact PR head. No merge, production migration, deployment or live-data access was performed.



## Research board run — 2026-11-27

**Review date:** 2026-11-27. Public source pages were checked on this date. The page publication/update date is recorded where the page displayed one. “Evidence” below means the public page states the feature; “hypothesis” means the proposed ZooTasks application and must be tested against real users, legal advice and actual unit costs.

### Current repository and release evidence

Main remains at **aa548d148d36df0c8ed2af3d58d8e1f0d8e38512**. GitHub reports the default branch as unprotected, with required status checks disabled. The exact-main-head workflow inventory returned 11 PR-triggered runs: ten Security Review failures and one Security Gate failure; no PostgreSQL Financial Verification run was returned for this SHA. Old green PR checks do not establish main readiness.

The requested issues #43, #45, #46, #48 and #54 are all open:

- #43 — promotion reward must be bounded by funded budget; claim-time capacity and approved payout accounting are currently separate.
- #45 — promotion reservation/completion reconciliation; approval, rejection, replay and last-slot concurrency remain explicit gates.
- #46 — AI-agent authority boundary; the policy executor must authorize independently of model output.
- #48 — primary Owner device; device identity must not replace per-action server authorization or dual control.
- #54 — evidence-led UX work; inspect existing homepage and dashboard PRs before proposing another change.

| PR | Exact head SHA | Base branch (recorded base SHA) | State | Exact-head workflow evidence |
|---|---|---|---|---|
| #52 | b14aece21769fc7c3782e9326b3a0fc5213730b4 | fix/restore-task-claim-migration-20261009 (dd5c3b9d25af27306069651682348bb98388b238) | Open, Draft, unmerged | Security Gate passed; Security Review passed; PostgreSQL Financial Verification passed |
| #53 | 4d5b5e58495263064c71dea40911bc4b8403732c | security/full-integrated-security-board-20261007 (841b65cbb6ef51b563537d49f809e58830e70104) | Open, Draft, unmerged | Security Review passed; Promotion PostgreSQL Regression passed; full Security Gate and full PostgreSQL Financial Verification not present on this head |
| #55 | a33432cb40ced36ad152a7a31e917c80953b70ce | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open, Draft, unmerged | Security Gate failed; Security Review failed; PostgreSQL Financial Verification failed |
| #56 | c41e44faf3ce700ce10ccdb0a5921d223d15abe5 | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open, Draft, unmerged | Security Gate failed; Security Review failed; PostgreSQL Financial Verification failed |
| #75 | c935b5cd06167890aa8849c4cc378ca06ad64747 | main (aa548d148d36df0c8ed2af3d58d8e1f0d8e38512) | Open, Draft, unmerged | Security Gate passed; Security Review passed; PostgreSQL Financial Verification passed |
| #77 | 96d10046e0eaeb8a6b7895695b51f7841badcce9 | security/multi-provider-review-base-20261108 (550a8aede970812e3dc2ae8f1e9076f70f95a0ef) | Open, Draft, unmerged | Security Gate passed; Security Review passed; PostgreSQL Financial Verification passed |

**Stacked-base and related-PR notes**

- #53 is stacked directly on #41's head SHA 841b65cbb6ef51b563537d49f809e58830e70104. #41 itself is based on main and has Security Gate and Security Review failures; its PostgreSQL check passed. #53's one promotion-specific passing run is not a substitute for the three release gates.
- #52 is based on a separate migration branch. A branch comparison reports that base branch as diverged from main (216 commits ahead and one behind); the comparison response did not expose the current branch-tip SHA. The base SHA recorded in #52 metadata is not main.
- #77 is stacked on a separate authentication review branch. Its base branch compares as 28 commits ahead of main and zero behind; the PR's recorded base SHA is 550a8aede970812e3dc2ae8f1e9076f70f95a0ef. Recheck the actual base tip and rerun all required gates on the updated merge candidate before considering it.
- Related open PRs already cover the same work: #57 changes only the Owner dashboard template; #55, #71 and #73 overlap the homepage template/CSS; #62 and #66 are green migration/security candidates; #74 restores the missing task-claim migration but its Security Gate and Security Review failed. Do not create duplicate homepage, Owner-dashboard or migration PRs.
- #75 is the only requested PR with all three named release workflows returned as passing on its exact head. It remains Draft and requires independent migration, dependency and financial-code review. Green checks alone do not approve it.

### Current main code facts that affect product design

The public main-branch files were inspected; no .env files, credentials, customer records, financial records, private logs or CI log artifacts were read.

- Task has reward, max_workers and completed_workers. TaskClaim has claimed/submitted/approved/rejected states and a unique task/worker constraint. Its task and worker foreign keys still use cascade deletion on main.
- The task claim view locks the Task row but increments completed_workers when the claim is created, before proof submission or approval. This makes the displayed completion count a claim count, not an approved-work count.
- Promotion has reward, budget, max_workers and completed_workers but no reserved_workers field. The claim path also increments completed_workers at claim time. The issue #43/#45 invariants remain unresolved on main.
- WalletTransaction links to task claims, promotion claims and withdrawal requests. WithdrawalRequest includes bank account, bank name and account-holder fields. These must never appear in a general analytics response or broad Owner export.
- The main homepage labels static sample cards “Live task activity” and shows sample rewards without an illustrative label. Existing PR #55 changes this to “Example task cards” and adds an explanatory note; it is the existing fix, so no duplicate was created.
- Existing PR #57 is a template-only redesign. It labels totals as recorded wallet activity and says the page is read-only, but its changed-file list contains no query/view implementation. It does not yet establish metric definitions, source freshness, authorization or ledger reconciliation.

### Railway production inventory and health

The ZooTasks production environment currently contains PostgreSQL and Redis resources with persistent volumes. The inventory marks the service resources live, but the environment health endpoint reports both services offline, with no active deployments and no replicas running. No web application or worker/bot service was returned. There is no staged deployment work. Resource existence is not proof of a running service or 24/7 operation.

### Official-source benchmark register — checked 2026-11-28

The source URL and checked date are recorded for every row. A source's own publication/update date is stated where the page exposes one. “Evidence” describes only what the cited official page says; the ZooTasks implication is a hypothesis to test. Country, plan and account-specific rules must be checked before implementation.

| # | Platform / official source | Source date or freshness | Observable feature — evidence | ZooTasks implication — hypothesis |
|---:|---|---|---|---|
| 1 | [Upwork — freelancer service fee](https://support.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee) | Checked 2026-11-28; page has no revision date in the retrieved view | The fee can range from 0% to 15% per contract, is shown before acceptance and is fixed once the contract begins; a net-pay calculator is provided | Freeze the disclosed fee for each accepted task and show net reward before claim |
| 2 | [Fiverr — earnings page](https://help.fiverr.com/hc/en-us/articles/9234443621137-Your-earnings-page) | Checked 2026-11-28; page has no revision date in the retrieved view | The earnings page shows available balance, future payments, withdrawals, transaction history and financial documents; it says order earnings are 80% before taxes | Separate gross, deductions, pending, available and withdrawable amounts in the member ledger |
| 3 | [Freelancer.com — fees and charges](https://www.freelancer.com/feesandcharges) | Checked 2026-11-28; live fee page | Fees vary by project/payment type; contest posters fund the total prize at posting; milestone payments remain until release, refund or dispute resolution | Do not label a task funded until the required amount is verified; show the fee payer and milestone/funding state |
| 4 | [PeoplePerHour — freelancer commission fees](https://support.peopleperhour.com/hc/en-us/articles/205218337-Freelancer-commission-fees) | Official page dated 2021-12-08; checked 2026-11-28 | The page describes buyer-relationship commission tiers and a monthly net effective fee statement; its numeric rates are old and are not treated as current | Consider relationship-based pricing only after rechecking current terms and modeling ZooTasks' costs |
| 5 | [Toptal — screening process](https://www.toptal.com/top-3-percent) | Checked 2026-11-28; page has no revision date in the retrieved view | Describes language/communication, skill, live-screening and test-project stages; the page reports a 3–8 week process and fewer than 3% accepted | Offer optional, task-relevant skill verification; do not impose a long screening path on every microtask |
| 6 | [Workana — commission calculation](https://help.workana.com/hc/en-us/articles/360041235874-How-is-the-commission-calculated-at-Workana) | Official page updated 2026-09-17; checked 2026-11-28 | Describes a client service cost and a freelancer commission tiered by cumulative payments with the same client | Show buyer and worker fees separately; test repeat-client pricing only after margin and legal review |
| 7 | [Contra — fees overview](https://help.contra.com/en/articles/9322934-fees-overview) | Official help page published about three months before this check; checked 2026-11-28 | Separates payment-processor card fees from Contra fees and lists ACH processing with a cap for eligible clients | Keep processor, FX, payout and platform fees as separate line items in quotes and receipts |
| 8 | [Guru — SafePay](https://www.guru.com/safepay/) | Checked 2026-11-28; page has no revision date in the retrieved view | Employer funds SafePay before work; funds can be released after review or enter arbitration, and the shared balance is not tied to one specific task | Keep task/campaign allocation in ZooTasks' own ledger; do not describe a pooled balance as task-specific escrow |
| 9 | [Airtasker — service fee](https://support.airtasker.com/hc/en-us/articles/200294499-What-is-the-service-fee) | Official page dated 2025-01-15; checked 2026-11-28 | Describes a tier-based tasker service fee and says the fee breakdown appears before an offer and in payment history | Display the exact fee before a worker commits and preserve the same calculation in the receipt |
| 10 | [Taskrabbit — Trust & Support Fee](https://support.taskrabbit.com/hc/en-us/articles/46260504648731-What-s-the-Taskrabbit-Trust-Support-Fee) | Checked 2026-11-28; page has no revision date in the retrieved view | The fee is shown as a separate invoice item and does not change what the Tasker is paid; expenses and tips are treated separately | Identify who pays each fee and keep buyer-side service charges separate from worker reward |
| 11 | [Clickworker — payment methods](https://support-workplace.clickworker.com/support/solutions/articles/80000672350-what-payment-methods-are-available-) and [payment process](https://support-workplace.clickworker.com/support/solutions/articles/80000672346-what-payment-options-do-i-have-) | Pages updated 2026-03-12 and 2026-03-13; checked 2026-11-28 | Weekly bill runs, method-specific thresholds and tax/payment-profile prerequisites; some work is credited after client acceptance | Show country-specific payout availability, payable threshold and pending-versus-payable state before work starts |
| 12 | [Prolific — underpaying studies](https://participant-help.prolific.com/en/articles/445043-underpaying-studies) | Official page dated 2026-07-28; checked 2026-11-28 | States a minimum hourly reward and recommends a higher rate; effective hourly pay is assessed using median actual completion time, not only the researcher's estimate | Compare estimated duration with measured median duration and flag consistently underpaid task types |
| 13 | [Toloka — user agreement](https://toloka.ai/tolokers/user-agreement-january-2025) | Terms dated 2025-01-08; checked 2026-11-28 | Describes acceptance-based payment crediting, a stated up-to-30-day crediting window and a limited resubmission route for rejected work | Publish review windows, reasons and appeal deadlines; verify the current agreement before relying on exact timing |
| 14 | [UserTesting — payment timing](https://support.usertesting.com/hc/en-us/articles/4405125498003-Where-s-my-payment) and [test/payment history](https://support.usertesting.com/hc/en-us/articles/4409767959059-How-do-I-track-my-test-and-payment-history) | Payment article dated 2025-04-23; checked 2026-11-28 | Says test payments usually arrive 14 days after completion and test history shows amount, scheduled date, status and upload time | Give each task a payment timeline and measure claim-to-approval and approval-to-payout delays |
| 15 | [Microworkers — worker FAQ](https://www.microworkers.com/faq.php) | Checked 2026-11-28; page has no revision date in the retrieved view | Describes a withdrawal threshold, KYC before withdrawal and country-dependent payment methods | Show the actual method, KYC state, threshold and fee for the member's country; do not assume Bangladesh availability |
| 16 | [Linear — audit log](https://linear.app/docs/audit-log) | Checked 2026-11-28; page describes current Enterprise-plan availability | Records workspace events for 90 days; only workspace owners can access the log; filters and API queries are supported | Build a role-gated audit view with explicit retention, actor/action filters and export auditing |
| 17 | [Supabase — Platform Audit Logs](https://supabase.com/docs/guides/security/platform-audit-logs) and [Auth Audit Logs](https://supabase.com/docs/guides/auth/audit-logs) | Auth page updated 2026-10-31; checked 2026-11-28 | Platform events include timestamp, actor, action and target; Auth logs capture sign-in, sign-up, password and token events; retention depends on plan | Keep append-only, privacy-minimized business/security events and separate authentication events |
| 18 | [Vercel — Deployment Protection](https://vercel.com/docs/deployment-protection) | Page updated 2026-01-07; checked 2026-11-28 | Controls access to preview and production deployment URLs through plan-dependent protection scopes and methods | Protect preview environments and Owner interfaces; treat staging access and production release approval separately |
| 19 | [Cloudflare — Access policy management](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/policy-management/) and [policy rules](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/) | Policy-management page updated 2026-11-02; policy overview updated 2026-11-17; checked 2026-11-28 | Policies define actions, rules, selectors, values and session duration; independent MFA and policy testing are available | Use identity-aware access, step-up checks and deny-by-default policy tests for privileged surfaces |
| 20 | [GitHub — ruleset rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) | Checked 2026-11-28; live documentation | Supports required status checks and strict/loose up-to-date behavior; expected check source can be constrained | Protect main with required Security Gate, Security Review and PostgreSQL checks on the current head |
| 21 | [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) | AI RMF 1.0 released 2023-01-26; page checked 2026-11-28 | Voluntary lifecycle framework organized around Govern, Map, Measure and Manage; NIST says AI RMF 1.0 is being revised and notes a 2026 profile concept note | Maintain an AI risk register, named owners, impact measures, monitoring and versioned controls; recheck the framework during design reviews |
| 22 | [OWASP Agent Control Standard](https://owaspacs.org/docs/acs/) and [instrumentation overview](https://owaspacs.org/docs/spec/instrument/) | Specification namespace v0.1.0; reference release 0.1.5; checked 2026-11-28 | A separate Guardian receives signed runtime step/tool requests and returns allow, deny, modify, ask or defer; the standard defines trace/inspect profiles. Official pages also document differing failure-posture text and implementation coverage | Put deterministic authorization outside the model; configure deny/refuse on Guardian failure, bind approvals to exact parameters and test every tool path |
| 23 | [OWASP AISVS project page](https://owasp.org/projects/artificial-intelligence-security-verification-standard-aisvs-docs) | Checked 2026-11-28; project page says 1.0 is latest stable and 1.01 is in development | Provides testable AI security requirements and three verification levels; the project page recommends Level 2 for most production systems | Pin the exact stable version and map production AI controls to testable requirements; do not claim 1.01 is stable |

**Discontinued-platform lesson — not an active benchmark:** [Amazon Mechanical Turk's official closure FAQ](https://www.mturk.com/help) states that the service permanently closed on 2026-09-30. The FAQ was updated 2026-11-12; workers have until 2026-11-30 to verify payment preferences, requester prepaid balances are due for refund by 2026-11-30, and transaction history remains available until 2027-01-28. Do not compare MTurk as an operating competitor. The lesson for ZooTasks is to plan a controlled wind-down, pending-work decisions, worker payout completion, buyer refunds, record retention and post-closure support.


### Updated product and security priorities

| Rank | Work | Measurable acceptance |
|---:|---|---|
| P0 | One reviewed task-claim migration lineage | Fresh database and disposable legacy copy both migrate; task/worker FK protection and historical claims verified; no missing dependency; exact-head SG, SR and PostgreSQL checks pass |
| P0 | Funded reward and capacity invariant | Active reserved reward plus approved reward exposure never exceeds verified available campaign funding; reserved slots plus completed slots never exceed max_workers; concurrency/replay tests produce zero over-budget approvals, duplicate credits and last-slot oversubscription |
| P0 | Main release gates | Main protected; SG, SR and PostgreSQL Financial Verification required; strict up-to-date checks; stale, missing, skipped-without-policy or failed gates block merge |
| P1 | Worker reward/time disclosure | Before claim, show gross reward, each known fee, estimated net, estimated active minutes, proof, eligibility and review window; compare actual median and P95 time-to-earn by task type |
| P1 | Read-only Owner finance panel | Metric source, formula, window and freshness visible; reconciles to ledger; role-scoped aggregate only; zero wallet/payout write endpoints and zero unauthorized reads |
| P1 | Task quality and dispute measurement | Track submission completeness, approval/rejection reasons, review P50/P95, dispute rate, appeal reversal, fraud loss and payout failure; suppress small cohorts |
| P2 | Owner governance | Passkey user verification, step-up for sensitive reads/exports, RBAC, explicit recovery/revocation, independent dual control and replay-negative tests |
| P2 | Privacy and accessibility | WCAG 2.2 AA audit, keyboard/screen-reader/mobile review, low-bandwidth test, data minimization and retention schedule; no sensitive data in analytics exports |
| P3 | AI policy enforcement | Shadow mode first; Guardian/policy decision before tool execution; allowlisted tools; zero direct AI writes to wallets, payouts, reward budgets, privileged access or production migrations |

**Unit-economics rule:** report platform-fee revenue, payment-processing cost, payout cost, refunds, chargebacks, fraud loss, tax, support, hosting and AI cost separately. Contribution margin is revenue less attributable costs; accounting net profit is a separate measure. The 15% pool remains only a proposal to validate. The 10% Owner and 5% development/AI/operating split is not net profit and does not prove profitability. Define the fee payer, fee base, refund behavior, taxes and all variable costs before any public fee promise.

**Owner-panel rule:** begin read-only. Use least-privilege roles for finance, support, analyst, security and Owner. Show aggregates with freshness and reconciliation status; never expose bank details, account-holder data, raw proof, secrets or unredacted audit payloads. Keep an append-only audit event for every privileged read/export and every proposed/approved action. High-risk actions require passkey step-up and independent dual approval.

**Financial-state rule:** a claim reserves one slot and the associated reward exposure atomically. Submission keeps the reservation. Approval converts the reservation into a completed/approved payout exactly once. Rejection, expiry or cancellation releases the reservation exactly once. Enforce the state transition under a row lock or equivalent serializable mechanism, with database constraints, idempotency keys and replay/concurrency tests. Do not change live wallet, payout or reward-budget behavior until the business meaning of budget and all legacy reconciliation cases are approved and tested.

### Bangladesh law and standards — current-source correction

This section is a product-risk register, not legal advice.

- [Payment and Settlement Systems Act, 2024, section 4](https://bdlaws.minlaw.gov.bd/act-1496/section-54104.html) restricts operating payment systems or providing payment services without the applicable Bangladesh Bank approval/licence. [Section 15](https://bdlaws.minlaw.gov.bd/act-1496/section-54115.html) separately addresses prepaid payment instruments and online/offline platforms involving public investment, lending, storing money or financial transactions. [Section 14](https://bdlaws.minlaw.gov.bd/act-1496/section-54114.html) requires advance fee disclosure by relevant payment-system participants/providers. The Act's general provisions became effective 2024-12-31, subject to the stated earlier commencement of sections 18(4) and 31. Whether ZooTasks' exact task funding, balance, reserve and payout design falls within these provisions requires Bangladesh counsel and, where appropriate, Bangladesh Bank clarification.
- [Personal Data Protection Act, 2026](https://bdlaws.minlaw.gov.bd/act-print-1692.html), Act No. 63 of 2026, deems most provisions effective from 2025-11-06. Sections 23 and 31–35 require a later Gazette commencement date after the stated 18-month period. The Act includes lawful-basis, security, retention, accountability and cross-border data provisions. Map worker identity, financial, location, proof and device data to purpose, access, retention and transfer controls.
- [Bangladesh Labour (Amendment) Act, 2026, section 32](https://bdlaws.minlaw.gov.bd/act-print-1672/section-print-58581.html) replaces Labour Act section 175. Its inclusion of self-employed and digital-platform-engaged people is expressly for Chapter XIII, concerning trade unions and industrial relations. Do not treat section 175 alone as deciding classification for every Labour Act chapter or every ZooTasks relationship.
- [Cyber Security Act, 2026](https://bdlaws.minlaw.gov.bd/act-1710.html) is the current official cyber-law source found for this review. Security testing must be authorized, scoped and documented; do not assume ZooTasks is designated critical information infrastructure.
- [NBR Income Tax Acts](https://nbr.gov.bd/regulations/acts/income-tax-acts/eng) and [Finance Act 2026](https://nbr.gov.bd/regulations/acts/finance-acts/eng) should be reviewed with a Bangladesh tax adviser for platform fees, withholding, VAT, worker reporting and cross-border payments. The authentic English text of the Income Tax Act and VAT Act is available from NBR; where Bangla and English texts conflict, confirm the controlling text and current amendments with counsel.

### Run boundary — 2026-11-27

This research refresh changes only this Markdown document on the existing PR #56 research branch. It does not change application code, secrets, permissions, financial records, wallet/payout/reward-budget logic or migrations. The new commit, if accepted by GitHub, will trigger only normal automatic PR workflows; none are manually dispatched or rerun. PR #56 remains Draft and unmerged. No production migration, deployment or live financial-data access is authorized or performed.


### Dependency-advisory review — 2026-11-27

The PR diffs reveal a release-gate issue that needs explicit review:

- PR #53's security-review workflow allows only Twisted 26.4.0 and suppresses CVE-2026-106454 on the premise that the affected range ends at 25.5.0. The upstream [Twisted GitHub advisory](https://github.com/twisted/twisted/security/advisories/GHSA-8pqf-f4m5-798g), published 2026-08-15 and checked 2026-11-27, lists affected versions as <=26.4.0 and lists no patched version. Therefore the PR #53 26.4.0 exception is not supported by that advisory and must remain fail-closed. Its single promotion regression pass does not resolve this.
- The [Twisted 26.10.0 release notes](https://github.com/twisted/twisted/releases) list the IMAP fix under #12787 (“no longer allows clients to specify arbitrary regexes”). The upstream fix was merged in [Twisted PR #12788](https://github.com/twisted/twisted/pull/12788) on 2026-08-15. [PyPI's Twisted 26.10.0 release record](https://pypi.org/project/Twisted/26.10.0/) shows the release uploaded 2026-10-30 with provenance. PR #75 pins Twisted 26.10.0, so it is materially different from PR #53's 26.4.0 pin. Still verify the exact artifact and runtime dependency tree and retain the upstream release-note/advisory evidence with the dependency review; do not rely on a blanket CVE suppression.
- [OSV's CVE record](https://osv.dev/vulnerability/CVE-2026-106454) currently records the affected range through 25.5.0 and a fixed upstream commit, while the upstream GitHub advisory lists <=26.4.0 and no patched version. Treat the advisory metadata as inconsistent until the vendor record is reconciled. The 26.10.0 upstream release notes provide evidence that the relevant code fix shipped; they do not authorize suppressing other Twisted advisories.
- [PyPI's Pillow 13.0.0 record](https://pypi.org/project/pillow/13.0.0/) shows a release uploaded 2026-10-16 with provenance. This verifies that the PR #75 pin is a published release, not that the package is automatically suitable; retain dependency and compatibility testing.

**Disposition:** PR #53's Twisted 26.4.0 exception is a security-review blocker. PR #75's Twisted 26.10.0 pin has upstream release-note evidence for the IMAP fix, but still requires independent dependency review and all exact-head release gates. No dependency or application code was changed by this research note.


### Repository, release-gate and Railway refresh — 2026-11-28

This section records public repository metadata and source code only. No secrets, environment files, customer/worker records, financial records or private logs were read.

#### Main branch

- Default branch: `main`.
- Exact main head: `aa548d148d36df0c8ed2af3d58d8e1f0d8e38512`.
- Branch protection: disabled; GitHub reports `protected=false` and no required status-check contexts.
- Exact-main Actions metadata for this SHA: 11 runs, all failed — 10 Security Review runs and one Security Gate run. No PostgreSQL Financial Verification run was returned.
- The latest main commit is not a release gate. A green PR on another SHA does not prove this main SHA is safe.

#### Requested open issues

Issues [#43](https://github.com/Rafiqual69/Zootasks/issues/43), [#45](https://github.com/Rafiqual69/Zootasks/issues/45), [#46](https://github.com/Rafiqual69/Zootasks/issues/46), [#48](https://github.com/Rafiqual69/Zootasks/issues/48) and [#54](https://github.com/Rafiqual69/Zootasks/issues/54) were all Open when checked 2026-11-28. Their scopes remain promotion funding/capacity, workflow reconciliation, AI authority, primary Owner device security and evidence-led website UX.

#### Exact-head PR audit

All PRs below were Open, Draft and unmerged when checked 2026-11-28. Workflow results are only for the exact head SHA shown. Repeated runs of the same workflow are counted once when describing unique gates.

| PR | Exact head SHA | Base branch (base SHA where relevant) | Exact-head workflow runs |
|---:|---|---|---|
| [#41](https://github.com/Rafiqual69/Zootasks/pull/41) | `841b65cbb6ef51b563537d49f809e58830e70104` | `main` | Security Gate failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39055731591)); Security Review failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39377004933)); PostgreSQL Financial Verification passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39055731605)) |
| [#52](https://github.com/Rafiqual69/Zootasks/pull/52) | `b14aece21769fc7c3782e9326b3a0fc5213730b4` | `fix/restore-task-claim-migration-20261009` @ `dd5c3b9d25af27306069651682348bb98388b238` | Security Gate passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39065416499)); Security Review passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39065416663)); PostgreSQL Financial Verification passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39065416559)) |
| [#53](https://github.com/Rafiqual69/Zootasks/pull/53) | `4d5b5e58495263064c71dea40911bc4b8403732c` | `security/full-integrated-security-board-20261007` @ PR #41 head `841b65cbb6ef51b563537d49f809e58830e70104` | Security Review passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39146130309)); Promotion PostgreSQL Regression passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39146133710)); full Security Gate and full PostgreSQL Financial Verification are missing |
| [#55](https://github.com/Rafiqual69/Zootasks/pull/55) | `a33432cb40ced36ad152a7a31e917c80953b70ce` | `main` @ `aa548d148d36df0c8ed2af3d58d8e1f0d8e38512` | Security Gate failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39147130401)); Security Review failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39147130469)); PostgreSQL Financial Verification failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39147130476)) |
| [#56](https://github.com/Rafiqual69/Zootasks/pull/56) | `e101a2e08782036ccbe0579efb1b2c754af68cd5` | `main` @ `aa548d148d36df0c8ed2af3d58d8e1f0d8e38512` | Security Review failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/45928608909)); Security Gate failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/45928608961)); PostgreSQL Financial Verification failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/45928608972)) |
| [#57](https://github.com/Rafiqual69/Zootasks/pull/57) | `3a5c3f0cc0425fb06666ab075fef69da1f6ee96e` | `main` | Security Review failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39148226226)); Security Gate failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39148226265)); PostgreSQL Financial Verification failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39148226231)) |
| [#62](https://github.com/Rafiqual69/Zootasks/pull/62) | `be7de84d525b4c44012f6102c9d4968a9a42aaec` | `main` | Security Gate passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39477083819)); Security Review passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39477083798)); PostgreSQL Financial Verification passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/39477083843)) |
| [#66](https://github.com/Rafiqual69/Zootasks/pull/66) | `e7e4b3eacd39aa0b6146354ac2545c491fa25934` | `main` | Security Gate passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/40171915855)); Security Review passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/40171915862)); PostgreSQL Financial Verification passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/40011291839)) |
| [#71](https://github.com/Rafiqual69/Zootasks/pull/71) | `4a09b2aa032e7c33eaa336be2dc5cc9fdeb93994` | `main` | Security Gate failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/40271645126)); Security Review failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/40271645136)); PostgreSQL Financial Verification failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/40271645139)) |
| [#74](https://github.com/Rafiqual69/Zootasks/pull/74) | `655d4476bb24161cd0724232271734140323c91d` | `main` | PostgreSQL Financial Verification passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/40273069238)); Security Gate failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/40273069246)); Security Review failed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/40273069281)) |
| [#75](https://github.com/Rafiqual69/Zootasks/pull/75) | `c935b5cd06167890aa8849c4cc378ca06ad64747` | `main` | Security Gate passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/41617278377)); Security Review passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/41617278184)); PostgreSQL Financial Verification passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/41617278403)) |
| [#77](https://github.com/Rafiqual69/Zootasks/pull/77) | `96d10046e0eaeb8a6b7895695b51f7841badcce9` | `security/multi-provider-review-base-20261108` @ `550a8aede970812e3dc2ae8f1e9076f70f95a0ef` | Security Review passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/42505995213)); PostgreSQL Financial Verification passed ([run](https://github.com/Rafiqual69/Zootasks/actions/runs/42505995188)); Security Gate is missing |

#### Stacked bases and duplicate scope

- PR #52 is based on `fix/restore-task-claim-migration-20261009`; that base is 216 commits ahead and one behind main. It is not an independent main-based candidate.
- PR #53 is based on PR #41's exact head; its base branch is 305 commits ahead and one behind main. It is stacked and lacks two full release gates.
- PR #77 is based on a branch 27 commits ahead of main. It has no Security Gate run on its current head.
- PRs #62, #66, #74 and #75 all touch migration/dependency/security surfaces. Their changes must be reconciled before selecting a single migration candidate.
- PRs #55 and #71 both change the public homepage. PR #57 already contains the read-only Owner finance dashboard template. Do not create duplicate work without reviewing these existing diffs.

#### Main-branch code evidence

Read-only source inspection of the current main SHA found:

- `backend/tasks/models.py`: Task has `max_workers` and `completed_workers`; TaskClaim task and worker foreign keys use CASCADE. No task reservation counter is present.
- `backend/tasks/views.py`: claim uses `select_for_update()`, then increments `completed_workers` at claim time. This is not an approved-completion count.
- `backend/promotions/models.py`: Promotion has `budget`, `max_workers` and `completed_workers`, but no `reserved_workers` field.
- `backend/promotions/views.py`: starting a promotion creates a claim and increments `completed_workers` at claim time. This does not prove that the work was approved or that its reward is funded.
- `backend/wallet/views.py`: the member wallet summary separates balance and reserved balance; withdrawal requests reserve balance. This is source-code inspection only, not a review of live balances or customer records.

Do not interpret task/promotion `completed_workers` as approved work. The current main code does not establish the proposed reserved-plus-approved budget/capacity invariant.

#### Railway production inventory and health

The Railway project has one production environment. Redis and PostgreSQL service resources exist and each has a persistent volume. The inventory marks both service resources live, but the health endpoint reports both Offline, with no active deployment, no running replica and no latest deployment. No web application or worker/bot service was returned. There is no staged change. Resource existence is not proof of a running service or 24/7 operation.

#### Current release disposition

- No merge or deployment is approved.
- Keep security gates fail-closed. A missing Security Gate on #53 or #77 is not a pass.
- Resolve the migration graph before any migration PR is selected.
- Specify and test the promotion budget/capacity state machine before changing live financial behavior.
- Protect main and require current-head Security Gate, Security Review and PostgreSQL Financial Verification; no stale or missing result can satisfy a release gate.

### Run boundary — 2026-11-28

This refresh updates only this Markdown document on the existing non-default PR #56 branch. It does not change application code, credentials, permissions, financial records, wallet/payout/reward-budget behavior or migrations. GitHub's normal PR workflows may run automatically after the documentation commit; none are manually dispatched or rerun. PR #56 remains Draft and unmerged. No production migration, deployment or live financial-data access was performed.
