from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("promotions", "0008_merge_financial_capacity_and_reservations"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="promotion",
            name="promotion_completed_lte_max_workers",
        ),
    ]
