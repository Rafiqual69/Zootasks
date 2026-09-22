from decimal import Decimal, InvalidOperation
from django.test import SimpleTestCase

class BotWithdrawalAmountValidationTests(SimpleTestCase):
    def validate(self, text, available=Decimal("200.00")):
        try:
            amount = Decimal(text)
        except (InvalidOperation, TypeError):
            return "invalid"
        if not amount.is_finite():
            return "invalid"
        if amount.as_tuple().exponent < -2:
            return "decimal_places"
        if amount < Decimal("50.00"):
            return "minimum"
        if amount > available:
            return "insufficient"
        return "valid"

    def test_valid_amount(self):
        self.assertEqual(self.validate("50"), "valid")
        self.assertEqual(self.validate("50.00"), "valid")
        self.assertEqual(self.validate("199.99"), "valid")

    def test_minimum_amount(self):
        self.assertEqual(self.validate("49.99"), "minimum")

    def test_excess_decimal_places(self):
        self.assertEqual(self.validate("50.001"), "decimal_places")

    def test_nan_rejected(self):
        self.assertEqual(self.validate("NaN"), "invalid")

    def test_infinity_rejected(self):
        self.assertEqual(self.validate("Infinity"), "invalid")
        self.assertEqual(self.validate("-Infinity"), "invalid")

    def test_insufficient_balance(self):
        self.assertEqual(self.validate("200.01", Decimal("200.00")), "insufficient")

    def test_invalid_text(self):
        self.assertEqual(self.validate("abc"), "invalid")
        self.assertEqual(self.validate(""), "invalid")


from unittest.mock import AsyncMock, Mock
from django.contrib.auth.models import User
from accounts.models import WorkerProfile
from wallet.models import WithdrawalRequest
from run_bot import withdrawal_message
from django.test import TransactionTestCase


class BotWithdrawalIntegrationTests(TransactionTestCase):
    def make_update(self, text, username="bot_test_user"):
        update = Mock()
        update.effective_user.username = username
        update.effective_user.id = 987654321
        update.effective_user.first_name = "Bot"
        update.effective_user.last_name = "Test"
        update.message.text = text
        update.message.reply_text = AsyncMock()
        return update

    def test_valid_amount_uses_real_withdrawal_message(self):
        user = User.objects.create(username="bot_test_user")
        profile = WorkerProfile.objects.create(user=user, balance=Decimal("200.00"))
        context = Mock()
        context.user_data = {"withdraw_step": "amount"}

        result = __import__("asyncio").run(
            withdrawal_message(self.make_update("50"), context)
        )

        self.assertTrue(result)
        self.assertEqual(context.user_data["withdraw_amount"], "50")
        self.assertEqual(context.user_data["withdraw_step"], "bank")
        self.assertEqual(WithdrawalRequest.objects.count(), 0)
        profile.refresh_from_db()
        self.assertEqual(profile.reserved_balance, Decimal("0.00"))

    def test_nan_is_rejected_by_real_withdrawal_message(self):
        User.objects.create(username="bot_test_user")
        WorkerProfile.objects.create(user_id=User.objects.get(username="bot_test_user").id, balance=Decimal("200.00"))
        context = Mock()
        context.user_data = {"withdraw_step": "amount"}
        update = self.make_update("NaN")

        result = __import__("asyncio").run(withdrawal_message(update, context))

        self.assertTrue(result)
        self.assertEqual(context.user_data["withdraw_step"], "amount")
        update.message.reply_text.assert_awaited_once()
        self.assertEqual(WithdrawalRequest.objects.count(), 0)
