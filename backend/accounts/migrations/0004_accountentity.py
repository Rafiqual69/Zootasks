import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_telegramidentity"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountEntity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "entity_type",
                    models.CharField(
                        choices=[
                            ("owner", "Owner"),
                            ("super_admin", "Super Admin"),
                            ("admin", "Admin"),
                            ("worker", "Worker"),
                            ("advertiser", "Advertiser"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "identity_email",
                    models.EmailField(
                        blank=True,
                        max_length=254,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "email_verified_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="account_entity",
                        to="auth.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "Account Entity",
                "verbose_name_plural": "Account Entities",
            },
        ),
    ]
