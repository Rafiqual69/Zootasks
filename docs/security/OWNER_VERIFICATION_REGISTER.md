# ZooTasks Owner Verification Register

**Status:** Controlled checklist — verification metadata only.

## Privacy boundary
Never store raw NID/passport scans, full identity numbers, bank-account numbers, passwords, API secrets, Telegram tokens, MFA secrets, recovery codes, session cookies, or production database contents in GitHub or this document.

## Verification record
| Evidence | Required when | Status | Verified date | Expiry/review date | Non-sensitive reference |
|---|---|---|---|---|---|
| Owner identity | Always | PENDING | | | |
| Legal-name match | Always | PENDING | | | |
| Verified Owner contact | Always | PENDING | | | |
| Ownership/control authority | Before production | PENDING | | | |
| Business registration | If applicable | PENDING | | | |
| Trade license | If applicable | PENDING | | | |
| TIN/tax registration | If applicable | PENDING | | | |
| BIN/VAT registration | If applicable | PENDING | | | |
| Business bank/payment ownership | Before financial production | PENDING | | | |
| Domain control | Before production | PENDING | | | |
| Hosting/provider control | Before production | PENDING | | | |
| GitHub/repository control | Before production | PENDING | | | |
| Owner AccountEntity active | Before privileged production access | PENDING | | | |
| Owner MFA | Before privileged production access | PENDING | | | |
| Privileged re-authentication | Before privileged production access | PENDING | | | |
| Recovery contact/process | Before production | PENDING | | | |
| Secret custody/rotation procedure | Before production | PENDING | | | |
| Incident-response contact | Before production | PENDING | | | |
| Backup/recovery authority | Before production | PENDING | | | |

## Server-side verification gates
Documents alone never establish runtime authority. Before privileged production access, the application must independently enforce:
- active Owner AccountEntity
- canonical Owner boundary
- staff/superuser boundary
- MFA/re-authentication where required
- session/security assurance
- server-side authorization
- audit evidence
- deny-by-default behavior

## Review schedule
Re-verify before production launch; quarterly for privileged identity/authority evidence; before document expiry; immediately after Owner/account/authority changes; after a security incident; and after material payment/provider changes.

## Financial separation
Identity/authority verification does not grant financial approval or payment authority. Finance approval and payer capabilities remain separately enforced by the Read/Write Security Constitution and machine policy.

## Evidence rule
A verification record is complete only when the evidence was independently checked, minimum necessary metadata was retained, the result is auditable, no sensitive document/secret entered source control, and the corresponding server-side control passed regression tests.
