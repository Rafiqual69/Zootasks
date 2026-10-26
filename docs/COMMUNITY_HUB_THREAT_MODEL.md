# ZooTasks Community Hub — Privacy & Threat Model

**Status:** Design review baseline; not implementation evidence or a security certification.  
**Parent tracker:** https://github.com/Rafiqual69/Zootasks/issues/70  
**Feature tracker:** https://github.com/Rafiqual69/Zootasks/issues/72

## Scope

A community feature for finding, drafting, publishing, and discussing useful information and ideas. This document defines the minimum threat review required before implementation and public posting. Existing task, promotion, wallet, withdrawal, and claim systems are out of scope for mutation and must remain unchanged.

## Data classification

| Data | Default visibility | Handling rule |
|---|---|---|
| Published idea title/body/category/tags | Public only after publication and moderation policy permits it | Escape rendered text; validate server-side; support reporting and correction |
| Draft idea and unpublished edits | Author and explicitly authorized moderators only | Deny by default; enforce object-level authorization on every read/write endpoint |
| Account email, internal user identifiers, auth/session data | Private | Never include in public page context, search index, analytics, or error output unless strictly required |
| Reports, reporter identity, moderator notes | Restricted to authorized moderation staff | Separate permission checks; never expose internal notes to the reported author or public |
| Security/audit events | Restricted operational access | Minimize personal data; redact tokens, credentials, email and financial information |
| Public references/source URLs | Public if intentionally attached | Validate URL scheme; do not server-fetch arbitrary URLs without SSRF controls |

## Threats and mandatory controls

1. **Broken object-level authorization / IDOR**  
   Threat: users enumerate IDs to read or modify other people's drafts or moderation records.  
   Controls: query ownership or explicit moderator permission on every endpoint; tests for anonymous, owner, other user, and moderator cases; avoid trusting client-supplied author/status fields.

2. **Stored XSS and unsafe rich text**  
   Threat: submitted content executes script for readers or moderators.  
   Controls: default to plain text and Django auto-escaping; do not mark user input safe; if rich text is later required, use a maintained allowlist sanitizer and test payloads in title/body/tags/URLs.

3. **CSRF, spam, and automated abuse**  
   Threat: unwanted submissions, report flooding, scraping, or account abuse.  
   Controls: Django CSRF protection, authentication for write operations, rate limits and request-size limits, anti-spam throttles, abuse monitoring with privacy-safe logs, and a moderation queue.

4. **Private-draft and personal-data leakage**  
   Threat: drafts appear in public lists/search, API responses, cache, logs, exports, or error pages.  
   Controls: public querysets include published/approved records only; no private fields in serializers/templates; private response cache policy; tests for anonymous users and unrelated accounts; no content or credentials in logs.

5. **Moderation privilege escalation**  
   Threat: an ordinary user can hide, publish, delete, or inspect reports for another user.  
   Controls: dedicated Django permissions/groups; deny-by-default policy; audit moderator state changes; test all transitions; avoid granting staff access solely by a client-provided flag.

6. **Malicious references and server-side request forgery**  
   Threat: server-side preview/fetch of user-provided links accesses internal services.  
   Controls: initially store/display validated URLs without server-side fetching; if previews are introduced, require a separate SSRF design including DNS/IP validation, redirects, timeouts, and egress controls.

7. **Content abuse, copyright, and attribution disputes**  
   Threat: harassment, personal data posting, copied work, illegal content, or false attribution.  
   Controls: clear community rules, report/review/appeal workflow, takedown process, minimal public profile data, authorship timestamps, and an approved licensing/retention policy before launch.

8. **Search and ranking manipulation**  
   Threat: spam floods, vote manipulation, or sensitive content indexed unintentionally.  
   Controls: index only public/approved content, escape query input, rate-limit searches, do not add voting/ranking until abuse controls are tested, and provide moderation removal from search.

9. **Database and migration risk**  
   Threat: new feature migration collides with current broken migration graph or rewrites existing data.  
   Controls: first repair and verify the actual migration chain; inspect migration plan on a clean test database and a sanitized copy; reversible migrations where feasible; never auto-fix or delete production rows; do not touch wallet or claim tables.

10. **Secrets and CI output leakage**  
    Threat: tokens, environment values, database credentials, user content, or test fixtures appear in commits/logs/artifacts.  
    Controls: use synthetic fixtures only, ephemeral test secrets, mask values, avoid shell tracing around secrets, review artifacts/logs, and never upload production database dumps or raw user data to CI.

## Minimum test matrix before public launch

- Anonymous visitor can view public approved ideas but cannot create or read drafts.
- Author can create/read/edit their own draft; another account cannot read, edit, publish, or delete it.
- Public search never returns drafts, private metadata, reporter identity, or moderator notes.
- Untrusted HTML/script in every user-controlled field renders as text or is safely sanitized.
- CSRF failure blocks unsafe requests; rate limits constrain repeated submissions/reports.
- Only authorized moderators can change moderation status; each action records actor, time, and action without logging secrets.
- Invalid status transitions, oversized input, malformed tags, and unsafe URL schemes are rejected.
- Migration graph check, model drift check, focused tests, and full regression suite run on the exact merge candidate.
- Accessibility checks cover keyboard use, visible focus, labels/errors, contrast, narrow mobile screens, and reduced motion.

## Release gates

- Do not enable open public posting until moderation, reporting, privacy notice, attribution/licensing, retention, and deletion rules are approved.
- Do not connect idea publication to wallet balances or reward payouts. Any task derived from an idea must go through existing reviewed task approval and reward flows.
- Keep the feature behind a reviewed release boundary until CI and independent human security review pass.
- No production deployment, production migration, financial operation, or secret rotation is performed by this design document.
