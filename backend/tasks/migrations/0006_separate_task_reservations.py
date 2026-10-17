from django.db import migrations, models


def reconcile_task_capacity(apps, schema_editor):
    Task = apps.get_model("tasks", "Task")
    TaskClaim = apps.get_model("tasks", "TaskClaim")

    for task in Task.objects.all().iterator():
        active_reservations = TaskClaim.objects.filter(
            task_id=task.pk,
        ).exclude(status="rejected").count()
        approved = TaskClaim.objects.filter(
            task_id=task.pk,
            status="approved",
        ).count()

        Task.objects.filter(pk=task.pk).update(
            reserved_workers=active_reservations,
            completed_workers=approved,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0005_alter_taskclaim_task"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="reserved_workers",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(
            reconcile_task_capacity,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="task",
            constraint=models.CheckConstraint(
                condition=models.Q(("reserved_workers__lte", models.F("max_workers"))),
                name="task_reserved_lte_max_workers",
            ),
        ),
        migrations.AddConstraint(
            model_name="task",
            constraint=models.CheckConstraint(
                condition=models.Q(("completed_workers__lte", models.F("reserved_workers"))),
                name="task_completed_lte_reserved_workers",
            ),
        ),
    ]
