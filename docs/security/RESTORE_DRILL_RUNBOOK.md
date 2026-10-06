# Isolated PostgreSQL Restore Drill

This helper is deliberately local-only. It restores a portable PostgreSQL dump into a new scratch database and fails closed for non-local database hosts.

Safety contract:
- never points at a production host
- never overwrites an existing restore target
- target database name must begin with restore_drill_
- uses pg_restore with --no-owner and --exit-on-error
- does not print credentials or restored financial data
- provider/PITR recovery remains a separate isolated sibling-service operation

Usage:
PGADMIN_URL='<local-admin-url>' bash scripts/restore_drill_postgres.sh <dump-file> <restore-drill-database-name>

Production promotion remains blocked until the restored candidate passes schema/migration checks, Django checks, policy/security tests, full regression, financial reconciliation, health checks, and privilege/configuration drift checks.
