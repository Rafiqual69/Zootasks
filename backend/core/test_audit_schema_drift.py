from io import StringIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import SimpleTestCase


class AuditSchemaDriftCommandTests(SimpleTestCase):
    @patch("core.management.commands.audit_schema_drift.MigrationRecorder")
    @patch("core.management.commands.audit_schema_drift.MigrationLoader")
    @patch("core.management.commands.audit_schema_drift.connection")
    @patch("core.management.commands.audit_schema_drift.apps")
    def test_reports_legacy_migration_and_extra_column_without_writes(
        self, apps_mock, connection_mock, loader_mock, recorder_mock
    ):
        field_names = ("id", "user_id", "entity_type")
        model = SimpleNamespace(
            _meta=SimpleNamespace(
                db_table="accounts_accountentity",
                app_label="accounts",
                label="AccountEntity",
                local_concrete_fields=[
                    SimpleNamespace(column=name) for name in field_names
                ],
            )
        )
        apps_mock.get_models.return_value = [model]
        connection_mock.introspection.table_names.return_value = [
            "accounts_accountentity",
        ]
        cursor = MagicMock()
        connection_mock.cursor.return_value.__enter__.return_value = cursor
        connection_mock.introspection.get_table_description.return_value = [
            SimpleNamespace(name=name)
            for name in (*field_names, "identity_email")
        ]
        loader_mock.return_value.disk_migrations = {
            ("accounts", "0001_initial"),
        }
        recorder_mock.return_value.applied_migrations.return_value = {
            ("accounts", "0001_initial"),
            ("accounts", "0019_owner_session_binding_expiry"),
        }

        output = StringIO()
        call_command("audit_schema_drift", "--app", "accounts", stdout=output)
        rendered = output.getvalue()

        self.assertIn(
            "accounts.0019_owner_session_binding_expiry",
            rendered,
        )
        self.assertIn("extra column: identity_email", rendered)
        self.assertIn("Audit only: no database rows, schema, or migration records were changed.", rendered)
        cursor.execute.assert_not_called()
        connection_mock.execute.assert_not_called()
