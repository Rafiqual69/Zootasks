from django.test import SimpleTestCase

from .verification_bounty_policy import (
    MAX_VERIFICATION_REWARD_UNITS,
    VerificationInput,
    validate_verification_assignment,
    verification_outcome_allowed,
)


class VerificationBountyPolicyTests(SimpleTestCase):
    def valid(self, **overrides):
        data = dict(
            submission_worker_id=1,
            verifier_worker_id=2,
            submission_id="submission-1",
            verifier_id="verification-1",
            reward_units=50,
        )
        data.update(overrides)
        return VerificationInput(**data)

    def test_valid_independent_verification_is_allowed(self):
        validate_verification_assignment(self.valid())

    def test_self_verification_is_denied(self):
        with self.assertRaisesMessage(ValueError, "self_verification_denied"):
            validate_verification_assignment(self.valid(verifier_worker_id=1))

    def test_duplicate_verification_is_denied(self):
        with self.assertRaisesMessage(ValueError, "duplicate_verification_denied"):
            validate_verification_assignment(self.valid(duplicate_verification=True))

    def test_collusion_flag_requires_review(self):
        with self.assertRaisesMessage(ValueError, "collusion_review_required"):
            validate_verification_assignment(self.valid(collusion_flag=True))

    def test_reward_is_bounded(self):
        with self.assertRaisesMessage(ValueError, "verification_reward_out_of_bounds"):
            validate_verification_assignment(
                self.valid(reward_units=MAX_VERIFICATION_REWARD_UNITS + 1)
            )

    def test_inactive_verifier_is_denied(self):
        with self.assertRaisesMessage(ValueError, "verifier_not_active"):
            validate_verification_assignment(self.valid(verifier_active=False))

    def test_disagreement_is_disputed(self):
        self.assertEqual(
            verification_outcome_allowed(agreement=False, escalation_required=False),
            "disputed",
        )

    def test_escalation_takes_precedence(self):
        self.assertEqual(
            verification_outcome_allowed(agreement=True, escalation_required=True),
            "escalate",
        )
