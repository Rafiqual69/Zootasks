from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0012_succession_state"),
    ]

    operations = [
        migrations.CreateModel(
            name="OwnerTrustedDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("device_identifier_hash", models.CharField(max_length=64)),
                ("label", models.CharField(blank=True, max_length=100)),
                ("status", models.CharField(choices=[("active", "Active"), ("revoked", "Revoked")], default="active", max_length=16)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("last_seen_at", models.DateTimeField(blank=True, null=True)),
                ("revoked_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("owner_entity", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="trusted_devices", to="accounts.accountentity")),
            ],
        ),
        migrations.AddConstraint(
            model_name="ownertrusteddevice",
            constraint=models.UniqueConstraint(
                fields=("owner_entity", "device_identifier_hash"),
                condition=models.Q(is_active=True) if False else models.Q(status="active"),
                name="accounts_unique_active_owner_device",
            ),
        ),
        migrations.AddIndex(
            model_name="ownertrusteddevice",
            index=models.Index(fields=("owner_entity", "status"), name="accounts_owner_device_status_idx"),
        ),
    ]
