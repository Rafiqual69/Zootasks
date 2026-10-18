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
