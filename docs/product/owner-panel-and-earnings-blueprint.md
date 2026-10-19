# ZooTasks Owner Panel & Earnings-First Marketplace Blueprint

**Status:** research/design proposal; not production implementation  
**Research date:** 2026-10-18  
**Scope:** public homepage, worker dashboard, task detail/claim/submit flow, owner operations panel, unit economics and security gates.

## 1. Product goal

Build a trustworthy task marketplace where workers can make an informed choice before spending time, task owners get reliable completion quality, and ZooTasks earns sustainably without relying on hidden fees or misleading earnings claims.

Success is not “highest commission.” It is repeat funded demand, quality-adjusted task completion, low fraud/dispute costs, transparent worker net earnings, and positive contribution margin after payment, support, fraud, tax and operating costs.

## 2. Benchmark set: 20+ public websites

These are public-source patterns to learn from, not claims that ZooTasks has equivalent controls. Re-check each source before implementation because prices, availability and policies change.

| # | Website / official source | Observable pattern worth benchmarking | ZooTasks implication |
|---:|---|---|---|
| 1 | [Upwork fees](https://support.upwork.com/hc/en-us/articles/211062538-Learn-about-the-Freelancer-Service-Fee) | Fee shown per contract; examples and net-pay math | Show gross reward, every fee, expected net reward, and fee lock before claim |
| 2 | [Upwork trust & safety](https://support.upwork.com/hc/en-us/articles/30236803116435--Upwork-Trust-Safety) | Reporting, marketplace standards, fraud response | Visible report flow, fair rejection reason, appeal/dispute tracking |
| 3 | [Fiverr freelancer guide](https://help.fiverr.com/hc/en-us/articles/34069565843985-How-Fiverr-works-for-freelancers) | Order lifecycle, earnings and clearing period | Task status timeline and explain approval/withdrawal timing |
| 4 | [Freelancer.com fees](https://www.freelancer.com/feesandcharges) | Fees vary by job/payment type; optional upgrades | Never bury task/withdrawal/optional costs; show total before confirmation |
| 5 | [PeoplePerHour fee policy](https://support.peopleperhour.com/hc/en-us/articles/205218337-Freelancer-commission-fees) | Fee tiers depend on lifetime buyer relationship | Consider loyalty-based fee experiments only after margin/legal review |
| 6 | [Toptal talent FAQ](https://www.toptal.com/freelance-jobs/faq) | Talent sets rates; automated payments | Avoid hidden reward changes; reliable status and payout visibility |
| 7 | [Workana commission](https://help.workana.com/hc/en-us/articles/360041235874-How-is-the-commission-calculated-at-Workana) | Commission tiers reward longer client relationships | Model repeat-customer retention rather than maximizing first-task take rate |
| 8 | [Contra fee overview](https://help.contra.com/en/articles/9322934-fees-overview) | Itemized processing/platform fees and caps | Separate platform fee from payment-provider fees and show caps clearly |
| 9 | [Guru freelancer pricing](https://www.guru.com/pricing-freelancer/) | Membership, job fees and bid limits are explicit | If paid tiers ever exist, disclose limits and avoid pay-to-work traps |
| 10 | [Airtasker service fee](https://support.airtasker.com/hc/en-us/articles/200294499-What-is-the-service-fee) | Fee shown at offer and in payment history | Persist fee calculation on task/transaction receipts |
| 11 | [Taskrabbit pricing transparency](https://support.taskrabbit.com/hc/en-gb/articles/46260394090651-Pricing-Transparency-Policy) | Cost expectations and pricing rules | Explain time, prerequisites, proof requirements and all expected costs upfront |
| 12 | [Clickworker worker guide](https://www.clickworker.com/clickworker/clickworker/) | Task variety, qualification, recurring payments, privacy messaging | Skill-fit task recommendations and clear qualification requirements |
| 13 | [Prolific participant flow](https://www.prolific.com/participants-how-it-works) | Pay and estimated duration visible before participation | Display reward, estimated minutes, eligibility and approval state before start |
| 14 | [Toloka task rules](https://toloka.ai/docs/guide/unwanted/) | Task moderation and restrictions on deceptive tasks | Moderate campaigns before publishing; ban fake reviews/click fraud |
| 15 | [UserTesting payout FAQ](https://support.usertesting.com/hc/en-us/articles/11664442062867) | Payout method/requirements stated clearly | Country-specific payout availability and verification steps before users invest time |
| 16 | [Microworkers FAQ](https://www.microworkers.com/faq.php) | Transaction history, payout threshold, KYC and service fee | Show current balance, pending balance, payout threshold and fee before withdrawal |
| 17 | [Remotasks worker site](https://stable.remotasks.com/en) | Training unlocks higher-skill work; quality affects access | Skill ladder and transparent qualification criteria; do not promise a fixed income |
| 18 | [Amazon Mechanical Turk status](https://www.mturk.com/help) | Official notice says service closed on 2026-09-30 | Do not copy stale marketplace assumptions; verify active status before benchmarking |
| 19 | [Linear audit log](https://linear.app/docs/audit-log) | Owner-only audit access, filters and retention | Owner panel gets searchable, role-gated event history and documented retention |
| 20 | [Supabase access control](https://supabase.com/docs/guides/platform/access-control) | Owner/admin/developer/read-only roles | Separate financial approver, support, analyst and read-only permissions |
| 21 | [Supabase audit logs](https://supabase.com/docs/guides/security/platform-audit-logs) | Actor, time, action and target are recorded | Append-only audit events; avoid storing secrets or full sensitive payloads |
| 22 | [Vercel audit logs](https://vercel.com/docs/audit-log) | Owner access and bounded export links | Owner-only export with short-lived links and export audit events |
| 23 | [Cloudflare security dashboard](https://developers.cloudflare.com/security/) | Security posture overview, rules and traffic signals | Show security posture, abuse trends and action-required status, not raw private logs |
| 24 | [OWASP Passkey Security](https://cheatsheetseries.owasp.org/cheatsheets/Passkey_Security_Cheat_Sheet.html) | Server-verified WebAuthn ceremonies, secure recovery and lifecycle | Passkeys/step-up auth for owner actions; never treat device ID alone as authorization |
| 25 | [OWASP Agent Control Standard](https://genai.owasp.org/resource/agent-control-standard-acs/) | Runtime-enforced, inspectable and traceable agent authority | AI proposes; deterministic policy engine authorizes; human dual control for high risk |
| 26 | [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) | Govern/map/measure/manage AI risk | Track AI risks, tests, accountable owners and rollback criteria |

### Benchmark synthesis

- **Pricing:** itemize every deduction and show net-to-worker before task acceptance. Some platforms use variable/tiered fees, but that does not prove such a model is optimal for ZooTasks.
- **Trust:** pre-fund tasks or otherwise prove available budget before listing; fair rejection reasons, dispute path and clear approval windows reduce abuse.
- **Earning experience:** match by skill/eligibility, show time estimate and task requirements, keep task proof simple, and show pending vs approved vs withdrawable balances separately.
- **Owner controls:** role separation, append-only audit, strong authentication and least privilege are repeatable patterns.
- **Research caution:** Amazon Mechanical Turk’s official help page states it closed on 2026-09-30. Treat its current status as a warning against copying old competitor lists blindly.

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
| 10 | https://support.taskrabbit.com/hc/en-us/articles/46260504648731-What-s-the-Taskrabbit-Trust-Support-Fee | The invoice lists a Trust & Support fee separately; its treatment varies with local pricing rules. | Explain the purpose and payer for every fee; do not hide operating costs in the worker's reward. | Source fact; UI proposal is hypothesis. |
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
