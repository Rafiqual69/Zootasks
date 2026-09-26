from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ("promotions", "0002_promotion_advertiser"),
    ]

    operations = [
        migrations.CreateModel(
            name="PromotionFunding",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("status", models.CharField(choices=[("pending", "Pending Verification"), ("verified", "Verified"), ("reserved", "Reserved"), ("released", "Released")], default="pending", max_length=20)),
                ("provider_reference", models.CharField(blank=True, max_length=150, null=True, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("reserved_at", models.DateTimeField(blank=True, null=True)),
                ("released_at", models.DateTimeField(blank=True, null=True)),
                ("promotion", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="funding", to="promotions.promotion")),
            ],
            options={
                "permissions": [
                    ("verify_promotion_funding", "Can verify promotion funding"),
                    ("reserve_promotion_funding", "Can reserve promotion funding"),
                    ("release_promotion_funding", "Can release promotion funding"),
                ],
            },
        ),
        migrations.CreateModel(
            name="PromotionFundingLedger",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("entry_type", models.CharField(choices=[("fund", "Funding Received"), ("reserve", "Worker Liability Reserved"), ("release", "Unused Funds Released"), ("refund", "Advertiser Refund")], max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("idempotency_key", models.CharField(max_length=120, unique=True)),
                ("provider_reference", models.CharField(blank=True, max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("funding", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ledger_entries", to="promotions.promotionfunding")),
            ],
            options={"ordering": ["created_at", "id"]},
        ),
    ]
