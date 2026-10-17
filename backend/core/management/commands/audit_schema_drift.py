from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.recorder import MigrationRecorder


class Command(BaseCommand):
    help = (
        "Read-only audit of database schema columns and applied migrations "
        "that are absent from the checked-out source."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            action="append",
            dest="app_labels",
            help="Limit model/table comparison to this app label; may be repeated.",
        )

    def handle(self, *args, **options):
        app_labels = set(options.get("app_labels") or [])
        loader = MigrationLoader(connection, ignore_no_migrations=True)
        recorder = MigrationRecorder(connection)
        applied = recorder.applied_migrations()
        disk = set(loader.disk_migrations)
        missing_source = sorted(
            (app, name) for app, name in applied
            if (app, name) not in disk
        )

        if missing_source:
            self.stdout.write(self.style.WARNING(
                "Applied database migrations not present in this checkout:"
            ))
            for app, name in missing_source:
                self.stdout.write(f"  - {app}.{name}")
        else:
            self.stdout.write(self.style.SUCCESS(
                "No applied migrations are missing from this checkout."
            ))

        table_names = set(connection.introspection.table_names())
        model_tables = {
            model._meta.db_table
            for model in apps.get_models()
            if not app_labels or model._meta.app_label in app_labels
        }
        owner_tables = sorted(
            table for table in table_names
            if table.startswith("accounts_") and table not in model_tables
        )
        if owner_tables:
            self.stdout.write(self.style.WARNING(
                "accounts_* tables not represented by selected current models:"
            ))
            for table in owner_tables:
                self.stdout.write(f"  - {table}")

        differences = 0
        models = sorted(
            (
                model for model in apps.get_models()
                if not app_labels or model._meta.app_label in app_labels
            ),
            key=lambda model: (model._meta.app_label, model._meta.label),
        )
        for model in models:
            table = model._meta.db_table
            if table not in table_names:
                self.stdout.write(self.style.ERROR(
                    f"MISSING TABLE {table} ({model._meta.label})"
                ))
                differences += 1
                continue

            expected = {
                field.column for field in model._meta.local_concrete_fields
            }
            with connection.cursor() as cursor:
                actual = {
                    column.name
                    for column in connection.introspection.get_table_description(
                        cursor, table
                    )
                }

            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            if missing or extra:
                differences += 1
                self.stdout.write(self.style.WARNING(
                    f"SCHEMA DRIFT {table} ({model._meta.label})"
                ))
                for column in missing:
                    self.stdout.write(f"  missing column: {column}")
                for column in extra:
                    self.stdout.write(f"  extra column: {column}")

        if differences == 0 and not missing_source and not owner_tables:
            self.stdout.write(self.style.SUCCESS(
                "No column/table/migration-source drift detected in the selected scope."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                "Audit only: no database rows, schema, or migration records were changed."
            ))
            self.stdout.write(
                "Review every difference before generating or applying migrations."
            )
