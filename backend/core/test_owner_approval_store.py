from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import OwnerApproval
from .owner_approval_store import OwnerApprovalDenied, consume_owner_approval


class OwnerApprovalStoreTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="owner-approval-test",
            password="test-only-password",
        )
        self.now = timezone.now()
        self.approval = OwnerApproval.objects.create(
            approval_id=uuid4(),
            owner=self.user,
            device_id="device-a",
            credential_id="credential-a",
            request_digest="a" * 64,
            expires_at=self.now + timedelta(minutes=2),
        )

    def test_valid_approval_is_consumed_once(self):
        consumed = consume_owner_approval(
            approval_id=self.approval.approval_id,
            owner_id=self.user.pk,
            request_digest=self.approval.request_digest,
            now=self.now,
        )
        self.assertIsNotNone(consumed.consumed_at)

        with self.assertRaises(OwnerApprovalDenied):
            consume_owner_approval(
                approval_id=self.approval.approval_id,
                owner_id=self.user.pk,
                request_digest=self.approval.request_digest,
                now=self.now,
            )

    def test_wrong_owner_denies(self):
        other = get_user_model().objects.create_user(
            username="other-owner-test",
            password="test-only-password",
        )
        with self.assertRaises(OwnerApprovalDenied):
            consume_owner_approval(
                approval_id=self.approval.approval_id,
                owner_id=other.pk,
                request_digest=self.approval.request_digest,
                now=self.now,
            )

    def test_wrong_request_denies(self):
        with self.assertRaises(OwnerApprovalDenied):
            consume_owner_approval(
                approval_id=self.approval.approval_id,
                owner_id=self.user.pk,
                request_digest="b" * 64,
                now=self.now,
            )

    def test_expired_approval_denies(self):
        with self.assertRaises(OwnerApprovalDenied):
            consume_owner_approval(
                approval_id=self.approval.approval_id,
                owner_id=self.user.pk,
                request_digest=self.approval.request_digest,
                now=self.now + timedelta(minutes=3),
            )

    def test_revoked_approval_denies(self):
        self.approval.revoked_at = self.now
        self.approval.save(update_fields=("revoked_at",))
        with self.assertRaises(OwnerApprovalDenied):
            consume_owner_approval(
                approval_id=self.approval.approval_id,
                owner_id=self.user.pk,
                request_digest=self.approval.request_digest,
                now=self.now,
            )

    def test_missing_approval_denies(self):
        with self.assertRaises(OwnerApprovalDenied):
            consume_owner_approval(
                approval_id=uuid4(),
                owner_id=self.user.pk,
                request_digest=self.approval.request_digest,
                now=self.now,
            )
