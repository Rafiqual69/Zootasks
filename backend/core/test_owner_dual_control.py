from datetime import datetime, timedelta, timezone
import unittest

from .owner_dual_control import (
    DualControlDenied,
    VerifiedOwnerApproval,
    authorize_dual_control,
    require_dual_control,
)


class OwnerDualControlTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 6, 18, 0, tzinfo=timezone.utc)
        self.owner_id = "owner-001"
        self.digest = "request-digest-v1"
        expires = self.now + timedelta(minutes=2)
        self.a = VerifiedOwnerApproval(
            "approval-a", self.owner_id, "device-a", "credential-a", self.digest,
            expires, False, False, True, True,
        )
        self.b = VerifiedOwnerApproval(
            "approval-b", self.owner_id, "device-b", "credential-b", self.digest,
            expires, False, False, True, True,
        )

    def _authorize(self, **overrides):
        values = {
            "owner_id": self.owner_id,
            "request_digest": self.digest,
            "approvals": (self.a, self.b),
            "now": self.now,
        }
        values.update(overrides)
        return authorize_dual_control(**values)

    def test_device_one_alone_denies(self):
        self.assertFalse(self._authorize(approvals=(self.a,)))

    def test_device_two_alone_denies(self):
        self.assertFalse(self._authorize(approvals=(self.b,)))

    def test_two_independent_valid_approvals_allow(self):
        self.assertTrue(self._authorize())

    def test_wrong_owner_denies(self):
        self.assertFalse(self._authorize(owner_id="different-owner"))

    def test_same_device_twice_denies(self):
        duplicate = VerifiedOwnerApproval(
            "approval-b", self.owner_id, "device-a", "credential-b", self.digest,
            self.b.expires_at, False, False, True, True,
        )
        self.assertFalse(self._authorize(approvals=(self.a, duplicate)))

    def test_same_credential_twice_denies(self):
        duplicate = VerifiedOwnerApproval(
            "approval-b", self.owner_id, "device-b", "credential-a", self.digest,
            self.b.expires_at, False, False, True, True,
        )
        self.assertFalse(self._authorize(approvals=(self.a, duplicate)))

    def test_request_parameter_binding_denies(self):
        self.assertFalse(self._authorize(request_digest="tampered-request"))

    def test_expired_approval_denies(self):
        expired = VerifiedOwnerApproval(
            "approval-b", self.owner_id, "device-b", "credential-b", self.digest,
            self.now, False, False, True, True,
        )
        self.assertFalse(self._authorize(approvals=(self.a, expired)))

    def test_revoked_approval_denies(self):
        revoked = VerifiedOwnerApproval(
            "approval-b", self.owner_id, "device-b", "credential-b", self.digest,
            self.b.expires_at, True, False, True, True,
        )
        self.assertFalse(self._authorize(approvals=(self.a, revoked)))

    def test_replayed_approval_denies(self):
        replayed = VerifiedOwnerApproval(
            "approval-b", self.owner_id, "device-b", "credential-b", self.digest,
            self.b.expires_at, False, True, True, True,
        )
        self.assertFalse(self._authorize(approvals=(self.a, replayed)))

    def test_non_phishing_resistant_approval_denies(self):
        weak = VerifiedOwnerApproval(
            "approval-b", self.owner_id, "device-b", "credential-b", self.digest,
            self.b.expires_at, False, False, False, True,
        )
        self.assertFalse(self._authorize(approvals=(self.a, weak)))

    def test_incident_freeze_denies(self):
        self.assertFalse(self._authorize(incident_freeze=True))

    def test_naive_clock_denies(self):
        self.assertFalse(self._authorize(now=datetime(2026, 10, 6, 18, 0)))

    def test_require_dual_control_raises_without_second_approval(self):
        with self.assertRaises(DualControlDenied):
            require_dual_control(
                owner_id=self.owner_id,
                request_digest=self.digest,
                approvals=(self.a,),
                now=self.now,
            )


if __name__ == "__main__":
    unittest.main()
