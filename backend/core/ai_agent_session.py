"""Fail-closed AI agent session and credential isolation boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import FrozenSet


class AIAgentSessionError(ValueError):
    """Expected failure at the AI agent session boundary."""


@dataclass(frozen=True)
class AIAgentSession:
    session_id: str
    agent_id: str
    audience: str
    scopes: FrozenSet[str]
    expires_at: datetime


def issue_agent_session(
    *,
    session_id: str,
    agent_id: str,
    audience: str,
    scopes: FrozenSet[str],
    expires_at: datetime,
) -> AIAgentSession:
    """Create metadata for a short-lived, non-human agent session.

    This function never accepts or stores a human/admin password, API key,
    bearer token, or provider secret.
    """
    if not session_id or not agent_id or not audience:
        raise AIAgentSessionError("ai_session_identity_required")
    if not scopes:
        raise AIAgentSessionError("ai_session_scope_required")
    if any(not str(scope).strip() for scope in scopes):
        raise AIAgentSessionError("ai_session_scope_invalid")
    if expires_at.tzinfo is None:
        raise AIAgentSessionError("ai_session_expiry_must_be_timezone_aware")
    if expires_at <= datetime.now(timezone.utc):
        raise AIAgentSessionError("ai_session_expired")
    return AIAgentSession(
        session_id=session_id,
        agent_id=agent_id,
        audience=audience,
        scopes=frozenset(scopes),
        expires_at=expires_at,
    )


def validate_agent_session(
    *,
    session: AIAgentSession,
    expected_agent_id: str,
    expected_audience: str,
    required_scope: str,
) -> None:
    now = datetime.now(timezone.utc)
    if session.agent_id != expected_agent_id:
        raise AIAgentSessionError("ai_session_agent_mismatch")
    if session.audience != expected_audience:
        raise AIAgentSessionError("ai_session_audience_mismatch")
    if required_scope not in session.scopes:
        raise AIAgentSessionError("ai_session_scope_denied")
    if session.expires_at <= now:
        raise AIAgentSessionError("ai_session_expired")
