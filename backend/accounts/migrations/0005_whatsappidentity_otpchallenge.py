# Generated for secure WhatsApp OTP sign-in.
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_accountentity"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WhatsAppIdentity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phone_hash", models.CharField(max_length=64, unique=True)),
                ("phone_last4", models.CharField(blank=True, max_length=4)),
                ("verified_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="whatsapp_identity", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="WhatsAppOTPChallenge",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("phone_number", models.CharField(blank=True, default="", max_length=16)),
                ("phone_hash", models.CharField(db_index=True, max_length=64)),
                ("code_hash", models.CharField(max_length=64)),
                ("requester_hash", models.CharField(db_index=True, max_length=64)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("consumed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["phone_hash", "created_at"], name="accounts_wa_phone_created"),
                    models.Index(fields=["requester_hash", "created_at"], name="accounts_wa_ip_created"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="whatsappotpchallenge",
            constraint=models.UniqueConstraint(
                condition=models.Q(("consumed_at__isnull", True)),
                fields=("phone_hash",),
                name="accounts_one_active_whatsapp_otp",
            ),
        ),
    ]
