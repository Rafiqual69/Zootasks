from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0008_merge_financial_capacity_and_reservations"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="task",
            name="task_completed_lte_max_workers",
        ),
    ]
