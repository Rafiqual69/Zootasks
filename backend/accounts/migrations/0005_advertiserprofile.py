from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_accountentity"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdvertiserProfile",
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
                ("organization_name", models.CharField(blank=True, max_length=200)),
                ("contact_name", models.CharField(blank=True, max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="advertiser_profile",
                        to="auth.user",
                    ),
                ),
            ],
            options={
                "verbose_name": "Advertiser Profile",
                "verbose_name_plural": "Advertiser Profiles",
            },
        ),
    ]
