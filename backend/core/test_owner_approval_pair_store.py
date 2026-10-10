from datetime import timedelta
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import OwnerApproval
from .owner_approval_pair_store import OwnerApprovalPairDenied, consume_owner_approval_pair


class OwnerApprovalPairStoreTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="owner-pair-test")
        self.now = timezone.now()
        self.digest = "a" * 64

    def approval(self, *, device_id, credential_id, **overrides):
        values = {
            "approval_id": uuid4(),
            "owner": self.user,
            "device_id": device_id,
            "credential_id": credential_id,
            "request_digest": self.digest,
            "expires_at": self.now + timedelta(minutes=2),
        }
        values.update(overrides)
        return OwnerApproval.objects.create(**values)

    def test_valid_pair_is_consumed_atomically(self):
        first = self.approval(device_id="device-1", credential_id="credential-1")
        second = self.approval(device_id="device-2", credential_id="credential-2")
        consume_owner_approval_pair(
            approval_ids=(first.approval_id, second.approval_id),
            owner_id=self.user.pk,
            request_digest=self.digest,
            now=self.now,
        )
        self.assertEqual(OwnerApproval.objects.filter(consumed_at__isnull=False).count(), 2)

    def test_one_approval_alone_is_denied(self):
        first = self.approval(device_id="device-1", credential_id="credential-1")
        with self.assertRaises(OwnerApprovalPairDenied):
            consume_owner_approval_pair(
                approval_ids=(first.approval_id, uuid4()),
                owner_id=self.user.pk,
                request_digest=self.digest,
                now=self.now,
            )

    def test_same_device_pair_is_denied(self):
        first = self.approval(device_id="device-1", credential_id="credential-1")
        second = self.approval(device_id="device-1", credential_id="credential-2")
        with self.assertRaises(OwnerApprovalPairDenied):
            consume_owner_approval_pair(
                approval_ids=(first.approval_id, second.approval_id),
                owner_id=self.user.pk,
                request_digest=self.digest,
                now=self.now,
            )

    def test_replay_is_denied_after_consumption(self):
        first = self.approval(device_id="device-1", credential_id="credential-1")
        second = self.approval(device_id="device-2", credential_id="credential-2")
        args = {
            "approval_ids": (first.approval_id, second.approval_id),
            "owner_id": self.user.pk,
            "request_digest": self.digest,
            "now": self.now,
        }
        consume_owner_approval_pair(**args)
        with self.assertRaises(OwnerApprovalPairDenied):
            consume_owner_approval_pair(**args)

    def test_freeze_is_denied(self):
        first = self.approval(device_id="device-1", credential_id="credential-1")
        second = self.approval(device_id="device-2", credential_id="credential-2")
        with self.assertRaises(OwnerApprovalPairDenied):
            consume_owner_approval_pair(
                approval_ids=(first.approval_id, second.approval_id),
                owner_id=self.user.pk,
                request_digest=self.digest,
                now=self.now,
                incident_freeze=True,
            )
