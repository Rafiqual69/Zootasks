from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase

from .ai_agent_session import AIAgentSessionError, issue_agent_session, validate_agent_session


class AIAgentSessionTests(SimpleTestCase):
    def _session(self):
        return issue_agent_session(
            session_id="sess-1",
            agent_id="ZT-AGENT-001",
            audience="zootasks-ai-gateway",
            scopes=frozenset({"task_quality:suggest"}),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )

    def test_session_is_bound_to_agent_and_audience(self):
        session = self._session()
        validate_agent_session(
            session=session,
            expected_agent_id="ZT-AGENT-001",
            expected_audience="zootasks-ai-gateway",
            required_scope="task_quality:suggest",
        )

    def test_wrong_agent_is_denied(self):
        with self.assertRaisesMessage(AIAgentSessionError, "ai_session_agent_mismatch"):
            validate_agent_session(
                session=self._session(),
                expected_agent_id="ZT-AGENT-999",
                expected_audience="zootasks-ai-gateway",
                required_scope="task_quality:suggest",
            )

    def test_wrong_audience_is_denied(self):
        with self.assertRaisesMessage(AIAgentSessionError, "ai_session_audience_mismatch"):
            validate_agent_session(
                session=self._session(),
                expected_agent_id="ZT-AGENT-001",
                expected_audience="other-service",
                required_scope="task_quality:suggest",
            )

    def test_expired_session_is_denied(self):
        session = issue_agent_session(
            session_id="sess-expired",
            agent_id="ZT-AGENT-001",
            audience="zootasks-ai-gateway",
            scopes=frozenset({"task_quality:suggest"}),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=1),
        )
        expired = session.__class__(
            session_id=session.session_id,
            agent_id=session.agent_id,
            audience=session.audience,
            scopes=session.scopes,
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        with self.assertRaisesMessage(AIAgentSessionError, "ai_session_expired"):
            validate_agent_session(
                session=expired,
                expected_agent_id="ZT-AGENT-001",
                expected_audience="zootasks-ai-gateway",
                required_scope="task_quality:suggest",
            )
