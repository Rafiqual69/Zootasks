# ZooTasks Persistent Asset Recovery Register

**Status:** Development security baseline — production activation pending  
**Scope:** Non-database persistent assets and recovery evidence  
**Financial logic:** Unchanged  
**Owner authorization logic:** Unchanged

## 1. Purpose

This register defines what ZooTasks must recover outside PostgreSQL and prevents production readiness from being declared until those assets have a tested recovery path.

This document is a recovery contract, not proof that production backups already exist.

## 2. Current repository inventory

The current Django application has:

- `backend/media/`: excluded by `.gitignore`; treat as potentially persistent user/application media. The current main branch does not contain a configured Django `MEDIA_ROOT`/`MEDIA_URL` storage backend or a `FileField`/`ImageField` in the reviewed domain models, so no production media backup is assumed to exist.
- `backend/staticfiles/`: generated deployment artifact; rebuildable from source and therefore not a primary backup target.
- `backend/static/`: source-controlled static assets; recoverable from Git.
- Celery/Redis runtime state: operational state, not a substitute for durable application records. Recovery must tolerate queue loss and re-create required scheduled work safely.
- Environment variables, provider credentials, tokens, MFA secrets, recovery codes and private keys: **never backup as application data**. They must be re-provisioned from the provider secret store.

## 3. Data classification

| Asset | Confidentiality | Integrity | Availability | Recovery class |
|---|---|---|---|---|
| User-uploaded media, when introduced | Confidential | High | High | Encrypted off-site backup + isolated restore |
| Generated non-rebuildable files | Confidential | High | High | Encrypted off-site backup + isolated restore |
| Source-controlled static assets | Internal | High | Medium | Git recovery |
| Generated staticfiles | Internal | Medium | Medium | Rebuild with `collectstatic` |
| Redis/Celery runtime state | Internal | Medium | Medium | Re-create/replay safely; never source of financial truth |
| Secrets/credentials | Security-critical | Critical | Critical | Secret-store recovery/rotation; never archive in asset backup |

## 4. Mandatory recovery boundary

A production recovery candidate is **not known-good** until:

1. the asset source and backup are identified;
2. the backup is integrity-verified;
3. the restore occurs in an isolated environment;
4. restored objects are checked for unexpected paths, permissions and ownership;
5. application references are checked for missing assets;
6. secret material is confirmed absent from the asset archive;
7. application/security/policy tests pass;
8. financial reconciliation passes for database state;
9. measured RPO/RTO evidence is recorded.

Failure of any required gate blocks promotion.

## 5. Backup safety rules

Asset archives must never contain:

- `.env` files or environment snapshots;
- `SECRET_KEY`, database URLs/passwords, API credentials or provider tokens;
- Telegram bot tokens;
- SMTP credentials;
- MFA/TOTP secrets or recovery codes;
- private keys or session cookies;
- raw bank/payment identifiers;
- raw government identity documents;
- PostgreSQL data dumps unless explicitly handled by the database recovery workflow.

Archives must be created with restrictive permissions and must be checked before leaving the source environment.

## 6. Development-stage rule

The Trial Railway environment does not provide the production backup/PITR controls required for final recovery readiness. Therefore this register intentionally stops at the application/repository recovery contract and local/CI verification.

No production subscription is required for this development work.

When production activation begins, the provider storage/backup layer must be selected and tested before production promotion.

## 7. Required production evidence

Before production readiness is declared, record:

- backup location and failure-domain separation;
- encryption-at-rest and encryption-in-transit controls;
- key custody/rotation method without storing keys in Git;
- successful integrity verification;
- isolated restore result;
- application-reference integrity result;
- retention/deletion policy;
- measured RPO and RTO;
- recovery owner and controlled cutover approval.

## 8. Fail-closed rule

**No verified asset backup + no isolated restore evidence = no production recovery PASS.**

This register does not grant storage access and does not authorize production writes.
