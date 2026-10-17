from django.db import migrations, models


def reconcile_promotion_capacity(apps, schema_editor):
    Promotion = apps.get_model("promotions", "Promotion")
    PromotionClaim = apps.get_model("promotions", "PromotionClaim")

    for promotion in Promotion.objects.all().iterator():
        active_reservations = PromotionClaim.objects.filter(
            promotion_id=promotion.pk,
        ).exclude(status="rejected").count()
        approved = PromotionClaim.objects.filter(
            promotion_id=promotion.pk,
            status="approved",
        ).count()

        Promotion.objects.filter(pk=promotion.pk).update(
            reserved_workers=active_reservations,
            completed_workers=approved,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("promotions", "0006_protect_claim_history"),
    ]

    operations = [
        migrations.AddField(
            model_name="promotion",
            name="reserved_workers",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(
            reconcile_promotion_capacity,
            migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name="promotion",
            constraint=models.CheckConstraint(
                condition=models.Q(("reserved_workers__lte", models.F("max_workers"))),
                name="promotion_reserved_lte_max_workers",
            ),
        ),
        migrations.AddConstraint(
            model_name="promotion",
            constraint=models.CheckConstraint(
                condition=models.Q(("completed_workers__lte", models.F("reserved_workers"))),
                name="promotion_completed_lte_reserved_workers",
            ),
        ),
    ]
