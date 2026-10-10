from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wallet", "0007_withdrawal_amount_nonnegative"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="wallettransaction",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(("transaction_type", "adjustment"))
                    | models.Q(("amount__gte", 0))
                ),
                name="wallet_tx_amount_nonnegative_unless_adjustment",
            ),
        ),
    ]
