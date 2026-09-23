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
from accounts.models import TelegramIdentity, WorkerProfile
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
        TelegramIdentity.objects.create(
            user=user,
            telegram_user_id=987654321,
            username="bot_test_user",
        )
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

from django.contrib.auth.models import Group, Permission
from accounts.models import TelegramIdentity
from run_bot import telegram_user_has_perm


class TelegramIdentityRBACSecurityTests(TransactionTestCase):
    def make_telegram_user(self, telegram_id=987654321012345, username="test_admin"):
        update_user = Mock()
        update_user.id = telegram_id
        update_user.username = username
        update_user.first_name = "Telegram"
        update_user.last_name = "Test"
        return update_user

    def test_telegram_identity_uses_numeric_id_and_updates_profile_data(self):
        telegram_user = self.make_telegram_user()

        user = User.objects.create(
            username="telegram_test_user",
        )

        identity = TelegramIdentity.objects.create(
            user=user,
            telegram_user_id=telegram_user.id,
            username="old_username",
            first_name="Old",
            last_name="Name",
        )

        telegram_user.username = "new_username"
        telegram_user.first_name = "New"
        telegram_user.last_name = "Person"

        resolved = __import__("asyncio").run(
            __import__("run_bot").get_telegram_account(telegram_user)
        )

        identity.refresh_from_db()

        self.assertEqual(resolved.id, user.id)
        self.assertEqual(identity.telegram_user_id, telegram_user.id)
        self.assertEqual(identity.username, "new_username")
        self.assertEqual(identity.first_name, "New")
        self.assertEqual(identity.last_name, "Person")

    def test_telegram_rbac_uses_django_permission(self):
        telegram_user = self.make_telegram_user(
            telegram_id=987654321012346,
            username="rbac_admin",
        )

        user = User.objects.create(username="rbac_admin_user")

        TelegramIdentity.objects.create(
            user=user,
            telegram_user_id=telegram_user.id,
            username=telegram_user.username,
        )

        group = Group.objects.create(name="Telegram Reviewer")

        permission = Permission.objects.get(
            content_type__app_label="tasks",
            codename="approve_task_submission",
        )
        group.permissions.add(permission)
        user.groups.add(group)

        allowed = __import__("asyncio").run(
            telegram_user_has_perm(
                telegram_user,
                "tasks.approve_task_submission",
            )
        )

        self.assertTrue(allowed)

    def test_telegram_rbac_denies_missing_permission(self):
        telegram_user = self.make_telegram_user(
            telegram_id=987654321012347,
            username="normal_user",
        )

        user = User.objects.create(username="normal_telegram_user")

        TelegramIdentity.objects.create(
            user=user,
            telegram_user_id=telegram_user.id,
            username=telegram_user.username,
        )

        allowed = __import__("asyncio").run(
            telegram_user_has_perm(
                telegram_user,
                "tasks.approve_task_submission",
            )
        )

        self.assertFalse(allowed)

    def test_old_telegram_username_cannot_authorize_another_identity(self):
        telegram_user = self.make_telegram_user(
            telegram_id=987654321012348,
            username="current_name",
        )

        user = User.objects.create(username="identity_owner")

        TelegramIdentity.objects.create(
            user=user,
            telegram_user_id=telegram_user.id,
            username="old_name",
        )

        group = Group.objects.create(name="Telegram Approver")

        permission = Permission.objects.get(
            content_type__app_label="tasks",
            codename="approve_task_submission",
        )
        group.permissions.add(permission)
        user.groups.add(group)

        # Authorization follows the immutable numeric Telegram ID,
        # not the cached username.
        telegram_user.username = "someone_else"

        allowed = __import__("asyncio").run(
            telegram_user_has_perm(
                telegram_user,
                "tasks.approve_task_submission",
            )
        )

        self.assertTrue(allowed)
