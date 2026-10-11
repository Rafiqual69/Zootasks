from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from .models import OwnerInputRequest
from .owner_console import _owner_console_authorized, owner_console


class OwnerConsoleAuthorizationTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model()(username="owner", is_staff=True, is_superuser=True)
        self.user.pk = 1
        self.user.is_verified = lambda: True
        self.request = self.factory.get("/owner/")
        self.request.user = self.user
        self.request.session = {
            "owner_reauthenticated_at": timezone.now().isoformat(),
        }

    @override_settings(OWNER_USERNAME="owner")
    def test_fresh_verified_configured_owner_is_allowed(self):
        self.assertTrue(_owner_console_authorized(self.request))

    @override_settings(OWNER_USERNAME="")
    def test_missing_owner_configuration_fails_closed(self):
        self.assertFalse(_owner_console_authorized(self.request))

    @override_settings(OWNER_USERNAME="different")
    def test_wrong_owner_fails_closed(self):
        self.assertFalse(_owner_console_authorized(self.request))

    @override_settings(OWNER_USERNAME="owner")
    def test_stale_reauthentication_fails_closed(self):
        self.request.session["owner_reauthenticated_at"] = (
            timezone.now() - timedelta(minutes=16)
        ).isoformat()
        self.assertFalse(_owner_console_authorized(self.request))

    @override_settings(OWNER_USERNAME="owner")
    def test_unverified_user_fails_closed(self):
        self.request.user.is_verified = lambda: False
        self.assertFalse(_owner_console_authorized(self.request))


class OwnerConsoleRequestTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="owner-console-test",
            password="not-used",
            is_staff=True,
            is_superuser=True,
        )

    def test_request_model_does_not_execute_or_mark_request_complete(self):
        item = OwnerInputRequest.objects.create(
            request_id=__import__("uuid").uuid4(),
            owner=self.owner,
            category=OwnerInputRequest.Category.INSTRUCTION,
            title="Review the plan",
            body="Prepare a draft only.",
        )
        self.assertEqual(item.status, OwnerInputRequest.Status.QUEUED)
        self.assertEqual(
            OwnerInputRequest.objects.filter(owner=self.owner).count(), 1
        )

    def test_credential_like_input_is_rejected_before_storage(self):
        from .owner_input_forms import OwnerInputRequestForm

        form = OwnerInputRequestForm(data={
            "category": OwnerInputRequest.Category.INSTRUCTION,
            "title": "Check integration",
            "body": "api_key=example-secret-value-1234567890",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("body", form.errors)

    def test_body_limit_is_enforced_by_model_field(self):
        from .owner_input_forms import OwnerInputRequestForm

        form = OwnerInputRequestForm(data={
            "category": OwnerInputRequest.Category.INSTRUCTION,
            "title": "Bounded input",
            "body": "x" * 5001,
        })
        self.assertFalse(form.is_valid())
