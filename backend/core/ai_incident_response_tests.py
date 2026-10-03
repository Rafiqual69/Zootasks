from django.test import SimpleTestCase

from core.ai_incident_response import (
    IncidentEvidence,
    IncidentResponseError,
    transition_incident,
)


class AIIncidentResponseTests(SimpleTestCase):
    def setUp(self):
        self.incident = IncidentEvidence(
            incident_id="INC-001",
            system_id="AI-SYS-001",
            release_id="release-1",
            severity="high",
            detection_reason="policy_violation",
            runtime_decision_digest="a" * 64,
        )

    def test_incident_requires_quarantine_before_rollback(self):
        quarantined = transition_incident(self.incident, "quarantined")
        candidate = transition_incident(quarantined, "rollback_candidate")
        approved = transition_incident(
            candidate,
            "rollback_approved",
            approval_ref="APP-001",
        )
        rolled_back = transition_incident(
            approved,
            "rolled_back",
            rollback_ref="RB-001",
        )
        self.assertEqual(rolled_back.state, "rolled_back")

    def test_recovery_requires_revalidation(self):
        quarantined = transition_incident(self.incident, "quarantined")
        candidate = transition_incident(quarantined, "rollback_candidate")
        approved = transition_incident(candidate, "rollback_approved", approval_ref="APP-001")
        rolled_back = transition_incident(approved, "rolled_back", rollback_ref="RB-001")
        pending = transition_incident(rolled_back, "revalidation_required")
        with self.assertRaisesRegex(IncidentResponseError, "revalidation_reference_required"):
            transition_incident(pending, "recovered")
        recovered = transition_incident(
            pending,
            "recovered",
            revalidation_ref="REV-001",
        )
        self.assertEqual(recovered.state, "recovered")

    def test_invalid_transition_fails_closed(self):
        with self.assertRaisesRegex(IncidentResponseError, "incident_transition_denied"):
            transition_incident(self.incident, "rolled_back")
