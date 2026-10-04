from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase, override_settings

from .models import AccountEntity, OwnerTrustedDevice
from .owner_devices import bind_owner_device
from .owner_session_binding import bind_owner_session
from .owner_session_guard import owner_session_binding_required


@override_settings(OWNER_USERNAME="owner-session-guard-test")
class OwnerSessionBindingGuardTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(
            username="owner-session-guard-test",
            password="Strong-Test-Password-123!",
            is_staff=True,
            is_superuser=True,
        )
        self.entity = AccountEntity.objects.create(
            user=self.owner,
            entity_type=AccountEntity.EntityType.OWNER,
            identity_email="owner@example.com",
        )
        private_key = Ed25519PrivateKey.generate()
        self.device = bind_owner_device(
            self.owner,
            "guard-device-1",
            private_key.public_key().public_bytes_raw(),
            "Guard Device",
        )
        self.client.force_login(self.owner)

    def test_unbound_owner_request_fails_closed(self):
        request = self._request()

        response = self._protected_view(request)

        self.assertEqual(response.status_code, 403)

    def test_bound_owner_request_is_allowed(self):
        request = self._request()
        bind_owner_session(request, self.owner, self.device.pk)

        response = self._protected_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"protected")

    def test_revoked_device_fails_closed(self):
        request = self._request()
        bind_owner_session(request, self.owner, self.device.pk)

        self.device.status = OwnerTrustedDevice.Status.REVOKED
        from django.utils import timezone
        self.device.revoked_at = timezone.now()
        self.device.save(update_fields=("status", "revoked_at", "updated_at"))

        response = self._protected_view(request)

        self.assertEqual(response.status_code, 403)

    @owner_session_binding_required
    def _protected_view(self, request):
        return HttpResponse("protected")

    def _request(self):
        request = self.client.request()
        request.user = self.owner
        request.session = self.client.session
        return request
