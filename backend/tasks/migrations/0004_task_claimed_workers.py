from django.db import migrations, models


def backfill_task_worker_counters(apps, schema_editor):
    Task = apps.get_model("tasks", "Task")
    TaskClaim = apps.get_model("tasks", "TaskClaim")
    db_alias = schema_editor.connection.alias

    for task in Task.objects.using(db_alias).all().iterator():
        claims = TaskClaim.objects.using(db_alias).filter(task_id=task.pk)
        claimed_workers = claims.exclude(status="rejected").count()
        completed_workers = claims.filter(status="approved").count()

        Task.objects.using(db_alias).filter(pk=task.pk).update(
            claimed_workers=claimed_workers,
            completed_workers=completed_workers,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0003_alter_task_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="claimed_workers",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(
            backfill_task_worker_counters,
            migrations.RunPython.noop,
        ),
    ]
