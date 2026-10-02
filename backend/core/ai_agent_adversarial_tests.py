from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase

from .ai_agent_audit import AIAuditError, build_provenance_receipt
from .ai_agent_session import AIAgentSessionError, issue_agent_session, validate_agent_session
from .ai_agent_registry import AIAgentRegistryError, validate_agent_autonomy, validate_agent_data_class, validate_agent_tool


class AIAgentAdversarialBoundaryTests(SimpleTestCase):
    def _session(self, *, agent_id="ZT-AGENT-001", scopes=frozenset({"task_quality:suggest"})):
        return issue_agent_session(
            session_id="adversarial-session",
            agent_id=agent_id,
            audience="zootasks-ai-gateway",
            scopes=scopes,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )

    def test_session_scope_escalation_is_denied(self):
        session = self._session()
        with self.assertRaisesMessage(AIAgentSessionError, "ai_session_scope_denied"):
            validate_agent_session(
                session=session,
                expected_agent_id="ZT-AGENT-001",
                expected_audience="zootasks-ai-gateway",
                required_scope="withdrawal:approve",
            )

    def test_cross_agent_session_reuse_is_denied(self):
        session = self._session()
        with self.assertRaisesMessage(AIAgentSessionError, "ai_session_agent_mismatch"):
            validate_agent_session(
                session=session,
                expected_agent_id="ZT-AGENT-999",
                expected_audience="zootasks-ai-gateway",
                required_scope="task_quality:suggest",
            )

    def test_data_class_escalation_is_denied(self):
        with self.assertRaisesRegex(AIAgentRegistryError, "ai_agent_data_class_not_allowed"):
            validate_agent_data_class(
                agent_id="ZT-AGENT-001",
                data_class="wallet_financial",
            )

    def test_autonomy_escalation_is_denied(self):
        with self.assertRaisesRegex(AIAgentRegistryError, "ai_agent_autonomy_not_allowed"):
            validate_agent_autonomy(
                agent_id="ZT-AGENT-001",
                autonomy="autonomous_execution",
            )

    def test_tool_permission_escalation_is_denied(self):
        with self.assertRaisesRegex(AIAgentRegistryError, "ai_agent_tool_not_allowed"):
            validate_agent_tool(
                agent_id="ZT-AGENT-001",
                tool_class="database_write",
            )

    def test_provenance_poisoning_is_denied(self):
        with self.assertRaisesMessage(AIAuditError, "ai_audit_unknown_field"):
            build_provenance_receipt({
                "agent_id": "ZT-AGENT-001",
                "capability_id": "AI-SYS-001",
                "correlation_id": "corr-adversarial",
                "decision": "authorized",
                "prompt": "attempted raw prompt injection",
                })

    def test_expired_session_is_denied(self):
        session = issue_agent_session(
            session_id="expired-session",
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
