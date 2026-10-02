from django.test import SimpleTestCase

from .quality_ladder_policy import (
    LEVEL_NEW,
    LEVEL_QUALIFIED,
    LEVEL_SPECIALIST,
    LEVEL_TRUSTED,
    QualityEvidence,
    calculate_quality_level,
)


class QualityLadderPolicyTests(SimpleTestCase):
    def test_new_worker_stays_new(self):
        self.assertEqual(calculate_quality_level(QualityEvidence()), LEVEL_NEW)

    def test_qualification_unlocks_qualified(self):
        evidence = QualityEvidence(
            qualification_passed=True,
            completed_tasks=1,
            quality_rate_basis_points=8000,
        )
        self.assertEqual(calculate_quality_level(evidence), LEVEL_QUALIFIED)

    def test_trusted_requires_quality_and_independent_verification(self):
        evidence = QualityEvidence(
            qualification_passed=True,
            completed_tasks=10,
            quality_rate_basis_points=9000,
            verified_tasks=3,
        )
        self.assertEqual(calculate_quality_level(evidence), LEVEL_TRUSTED)

    def test_specialist_requires_stronger_threshold(self):
        evidence = QualityEvidence(
            qualification_passed=True,
            completed_tasks=50,
            quality_rate_basis_points=9500,
            verified_tasks=10,
        )
        self.assertEqual(calculate_quality_level(evidence), LEVEL_SPECIALIST)

    def test_fraud_flag_fails_closed_to_new(self):
        evidence = QualityEvidence(
            qualification_passed=True,
            completed_tasks=50,
            quality_rate_basis_points=9900,
            verified_tasks=20,
            fraud_flags=1,
        )
        self.assertEqual(calculate_quality_level(evidence), LEVEL_NEW)

    def test_cooldown_fails_closed_to_new(self):
        evidence = QualityEvidence(
            qualification_passed=True,
            completed_tasks=50,
            quality_rate_basis_points=9900,
            verified_tasks=20,
            cooldown_active=True,
        )
        self.assertEqual(calculate_quality_level(evidence), LEVEL_NEW)

    def test_negative_evidence_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_quality_level(QualityEvidence(completed_tasks=-1))
