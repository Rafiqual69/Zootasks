from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0013_ownertrusteddevice"),
    ]

    operations = [
        migrations.AddField(
            model_name="ownertrusteddevice",
            name="public_key",
            field=models.BinaryField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="ownertrusteddevice",
            name="enrollment_challenge_hash",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="ownertrusteddevice",
            name="enrollment_challenge_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ownertrusteddevice",
            name="auth_challenge_hash",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name="ownertrusteddevice",
            name="auth_challenge_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="ownertrusteddevice",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("active", "Active"),
                    ("revoked", "Revoked"),
                ],
                default="pending",
                max_length=16,
            ),
        ),
    ]
