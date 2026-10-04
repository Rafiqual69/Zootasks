import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0011_ownernominee"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="ownernominee",
            name="accounts_unique_nominee_succession_order",
        ),
        migrations.AddConstraint(
            model_name="ownernominee",
            constraint=models.UniqueConstraint(
                fields=("owner_entity", "succession_order"),
                condition=models.Q(is_active=True),
                name="accounts_unique_active_nominee_succession_order",
            ),
        ),
        migrations.CreateModel(
            name="OwnerSuccessionState",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("owner_active", "Owner Active"), ("activation_pending", "Activation Pending"), ("super_nominee_active", "Super Nominee Active"), ("fallback_active", "Fallback Nominee Active"), ("suspended", "Suspended")], default="owner_active", max_length=32)),
                ("activation_reference", models.CharField(blank=True, max_length=128)),
                ("activated_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("activated_nominee", models.ForeignKey(blank=True, null=True, on_delete=models.deletion.PROTECT, related_name="succession_activations", to="accounts.ownernominee")),
                ("owner_entity", models.OneToOneField(on_delete=models.deletion.PROTECT, related_name="succession_state", to="accounts.accountentity")),
            ],
        ),
    ]
