from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wallet", "0004_alter_withdrawalrequest_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="wallettransaction",
            options={
                "ordering": ["-created_at"],
                "permissions": [
                    (
                        "view_live_wallet_dashboard",
                        "Can view the live wallet dashboard",
                    ),
                ],
            },
        ),
    ]
