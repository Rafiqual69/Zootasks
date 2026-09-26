from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0009_ownersocialidentity"),
    ]

    operations = [
        migrations.CreateModel(
            name="OwnerSocialOAuthState",
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
                ("provider", models.CharField(max_length=32)),
                ("state_hash", models.CharField(max_length=64, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "account_entity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="owner_social_oauth_states",
                        to="accounts.accountentity",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="ownersocialoauthstate",
            index=models.Index(
                fields=["account_entity", "provider", "created_at"],
                name="accounts_social_oauth_idx",
            ),
        ),
    ]
