# CI Failure Triage — Migration Graph Blocker

**Status:** Evidence captured from GitHub Actions for documentation/audit only.  
**Affected commit:** `dda2b62ccfdbfc25f17e99b24249923ee451a161` (financial write-path inventory PR head).  
**Candidate migration fix:** `be7de84d525b4c44012f6102c9d4968a9a42aaec` (PR #62 head).  
**No production action:** No deployment, migration execution against production, secret rotation, or financial-data mutation was performed.

## Confirmed CI failure

The following pull-request workflows failed on the inventory PR head:

- ZooTasks PostgreSQL Financial Verification — failed at **Migration drift check**.
- ZooTasks Security Gate — failed at **Migration drift check**.
- Security Review (Protected Branches) — failed at **Full regression**.

The common Django exception was:

`NodeNotFoundError: Migration tasks.0005_alter_taskclaim_task dependencies reference nonexistent parent node ('tasks', '0004_protect_claim_history')`

This indicates the tested branch's migration graph references `tasks.0004_protect_claim_history`, but that parent migration is absent from the branch's visible migration graph. The proposed migration fix is present on the separate PR #62 candidate branch, not on `main`; the inventory PR was created from `main`. This is a branch-integration / migration-lineage blocker, not evidence that the inventory documentation itself caused the missing migration.

## Safe next steps

1. Keep PR #62 and PR #64 Draft and unmerged until the migration lineage is reconciled.
2. Review the full migration directory and dependency graph on the exact base/head pair; do not add a duplicate migration or change dependencies by guesswork.
3. Re-run migration-drift checks and the full regression suite on a branch that includes the reviewed migration-lineage fix.
4. Rehearse both a fresh database migration and an upgrade from the oldest supported schema using disposable PostgreSQL data.
5. Confirm CI uses an intentionally generated test-only `SECRET_KEY`. The logs also emitted Django's weak-key warning; do not infer a production secret leak or rotate production credentials solely from that warning. Never copy secret values into PR comments or logs.

## Limitations

This triage is based on workflow job logs for the exact commit listed above. It does not establish production database state, prove that no secrets exist in Git history, or certify the application as secure. Secret-looking values in the logs were not reproduced here.
