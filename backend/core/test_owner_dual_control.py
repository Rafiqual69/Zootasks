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
        self.digest = "request-digest-v1"
        expires = self.now + timedelta(minutes=2)
        self.a = VerifiedOwnerApproval(
            "approval-a", "device-a", "credential-a", self.digest,
            expires, False, False, True, True,
        )
        self.b = VerifiedOwnerApproval(
            "approval-b", "device-b", "credential-b", self.digest,
            expires, False, False, True, True,
        )

    def test_device_one_alone_denies(self):
        self.assertFalse(authorize_dual_control(
            request_digest=self.digest, approvals=(self.a,), now=self.now,
        ))

    def test_device_two_alone_denies(self):
        self.assertFalse(authorize_dual_control(
            request_digest=self.digest, approvals=(self.b,), now=self.now,
        ))

    def test_two_independent_valid_approvals_allow(self):
        self.assertTrue(authorize_dual_control(
            request_digest=self.digest, approvals=(self.a, self.b), now=self.now,
        ))

    def test_same_device_twice_denies(self):
        duplicate = VerifiedOwnerApproval(
            "approval-b", "device-a", "credential-b", self.digest,
            self.b.expires_at, False, False, True, True,
        )
        self.assertFalse(authorize_dual_control(
            request_digest=self.digest, approvals=(self.a, duplicate), now=self.now,
        ))

    def test_same_credential_twice_denies(self):
        duplicate = VerifiedOwnerApproval(
            "approval-b", "device-b", "credential-a", self.digest,
            self.b.expires_at, False, False, True, True,
        )
        self.assertFalse(authorize_dual_control(
            request_digest=self.digest, approvals=(self.a, duplicate), now=self.now,
        ))

    def test_request_parameter_binding_denies(self):
        self.assertFalse(authorize_dual_control(
            request_digest="tampered-request", approvals=(self.a, self.b), now=self.now,
        ))

    def test_expired_approval_denies(self):
        expired = VerifiedOwnerApproval(
            "approval-b", "device-b", "credential-b", self.digest,
            self.now, False, False, True, True,
        )
        self.assertFalse(authorize_dual_control(
            request_digest=self.digest, approvals=(self.a, expired), now=self.now,
        ))

    def test_revoked_approval_denies(self):
        revoked = VerifiedOwnerApproval(
            "approval-b", "device-b", "credential-b", self.digest,
            self.b.expires_at, True, False, True, True,
        )
        self.assertFalse(authorize_dual_control(
            request_digest=self.digest, approvals=(self.a, revoked), now=self.now,
        ))

    def test_replayed_approval_denies(self):
        replayed = VerifiedOwnerApproval(
            "approval-b", "device-b", "credential-b", self.digest,
            self.b.expires_at, False, True, True, True,
        )
        self.assertFalse(authorize_dual_control(
            request_digest=self.digest, approvals=(self.a, replayed), now=self.now,
        ))

    def test_non_phishing_resistant_approval_denies(self):
        weak = VerifiedOwnerApproval(
            "approval-b", "device-b", "credential-b", self.digest,
            self.b.expires_at, False, False, False, True,
        )
        self.assertFalse(authorize_dual_control(
            request_digest=self.digest, approvals=(self.a, weak), now=self.now,
        ))

    def test_incident_freeze_denies(self):
        self.assertFalse(authorize_dual_control(
            request_digest=self.digest, approvals=(self.a, self.b),
            now=self.now, incident_freeze=True,
        ))

    def test_require_dual_control_raises_without_second_approval(self):
        with self.assertRaises(DualControlDenied):
            require_dual_control(
                request_digest=self.digest, approvals=(self.a,), now=self.now,
            )


if __name__ == "__main__":
    unittest.main()
