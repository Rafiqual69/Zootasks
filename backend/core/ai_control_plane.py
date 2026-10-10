"""Deterministic guardrails for AI proposals before any tool execution.

This layer never grants authority. It validates an AI proposal against a static
tool/action allowlist, bounds plan size and retries, and produces a secret-free
request digest. Critical actions must still pass the existing execution
authorization and human dual-control boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

from .ai_action_risk import AIRiskLevel, classify_ai_action
from .owner_request_binding import RequestBindingError, canonical_request_digest
from .security_policy import SecurityPolicyError, load_and_validate_policy


class AIGuardError(PermissionError):
    """Raised when an AI proposal cannot safely enter the execution boundary."""


class AITool(StrEnum):
    READ_PROJECT_DATA = "read_project_data"
    GENERATE_REPORT = "generate_report"
    CREATE_DRAFT = "create_draft"
    WRITE_NONFINANCIAL_RECORD = "write_nonfinancial_record"
    SEND_EXTERNAL_MESSAGE = "send_external_message"


AI_TOOL_ACTIONS = {
    AITool.READ_PROJECT_DATA: "read_scoped_project_data",
    AITool.GENERATE_REPORT: "generate_report",
    AITool.CREATE_DRAFT: "create_draft",
    AITool.WRITE_NONFINANCIAL_RECORD: "write_nonfinancial_record",
    AITool.SEND_EXTERNAL_MESSAGE: "send_external_message",
}

MAX_PLAN_STEPS = 12
MAX_RETRIES_PER_STEP = 3
MAX_TOOL_CALLS_PER_PLAN = 12
MAX_PARAMETER_DEPTH = 6
MAX_PARAMETER_NODES = 256
MAX_PARAMETER_STRING_LENGTH = 512


def _validate_parameter_shape(value: Any, *, depth: int = 0, nodes: list[int] | None = None) -> None:
    nodes = nodes if nodes is not None else [0]
    nodes[0] += 1
    if nodes[0] > MAX_PARAMETER_NODES or depth > MAX_PARAMETER_DEPTH:
        raise AIGuardError("AI parameter payload exceeds safety limits.")
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str) or not key or len(key) > MAX_PARAMETER_STRING_LENGTH:
                raise AIGuardError("AI parameter key denied.")
            _validate_parameter_shape(nested, depth=depth + 1, nodes=nodes)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            _validate_parameter_shape(nested, depth=depth + 1, nodes=nodes)
        return
    if value is None or isinstance(value, (str, bool, int)):
        if isinstance(value, str) and len(value) > MAX_PARAMETER_STRING_LENGTH:
            raise AIGuardError("AI parameter value denied.")
        return
    raise AIGuardError("AI parameter type denied.")


@dataclass(frozen=True)
class AIProposal:
    tool: str
    action: str
    target: str
    scope: str
    parameters: Mapping[str, Any]


@dataclass(frozen=True)
class AIPlanDecision:
    risk: AIRiskLevel
    human_governance_required: bool
    request_digest: str


def validate_ai_proposal(proposal: AIProposal) -> AIRiskLevel:
    """Validate tool/action/resource metadata without granting execution."""
    if not isinstance(proposal, AIProposal):
        raise AIGuardError("AI proposal denied.")

    try:
        tool = AITool(proposal.tool.strip().lower())
    except (AttributeError, ValueError):
        raise AIGuardError("AI tool denied.")

    expected_action = AI_TOOL_ACTIONS.get(tool)
    if expected_action != proposal.action.strip().lower():
        raise AIGuardError("AI tool/action mismatch.")

    if not isinstance(proposal.target, str) or not proposal.target.strip():
        raise AIGuardError("AI target denied.")
    if not isinstance(proposal.scope, str) or not proposal.scope.strip():
        raise AIGuardError("AI scope denied.")
    if not isinstance(proposal.parameters, Mapping):
        raise AIGuardError("AI parameters denied.")
    _validate_parameter_shape(proposal.parameters)

    risk = classify_ai_action(proposal.action)
    if risk is AIRiskLevel.CRITICAL:
        # Critical actions are never directly executable through this tool layer.
        raise AIGuardError("Critical AI action requires human governance.")

    return risk


def evaluate_ai_plan(
    *,
    proposals: list[AIProposal],
    request_id: str,
    environment: str,
    policy_version: str,
) -> AIPlanDecision:
    """Validate a bounded plan and return a secret-free exact-request digest."""
    if not isinstance(proposals, list) or not proposals:
        raise AIGuardError("AI plan denied.")
    if not isinstance(policy_version, str) or not policy_version.strip():
        raise AIGuardError("AI policy version denied.")
    try:
        current_policy_version = load_and_validate_policy()["policy_version"]
    except SecurityPolicyError as exc:
        raise AIGuardError("AI policy load denied.") from exc
    if policy_version != current_policy_version:
        raise AIGuardError("AI policy version is stale.")
    if len(proposals) > MAX_PLAN_STEPS:
        raise AIGuardError("AI plan exceeds step limit.")
    if len(proposals) > MAX_TOOL_CALLS_PER_PLAN:
        raise AIGuardError("AI plan exceeds tool-call limit.")

    risks = [validate_ai_proposal(proposal) for proposal in proposals]
    if any(risk is AIRiskLevel.CRITICAL for risk in risks):
        raise AIGuardError("Critical AI action requires a separate human-authorized execution path.")

    try:
        digest = canonical_request_digest(
            request_id=request_id,
            operation="ai_plan",
            target="ai_control_plane",
            scope="bounded",
            environment=environment,
            policy_version=policy_version,
            material_parameters={
                "steps": [
                    {
                        "tool": proposal.tool,
                        "action": proposal.action,
                        "target": proposal.target,
                        "scope": proposal.scope,
                        "parameters": dict(proposal.parameters),
                    }
                    for proposal in proposals
                ]
            },
        )
    except RequestBindingError as exc:
        raise AIGuardError("AI plan binding denied.") from exc

    highest_risk = max(risks, key=lambda value: list(AIRiskLevel).index(value))
    return AIPlanDecision(
        risk=highest_risk,
        human_governance_required=highest_risk is AIRiskLevel.HIGH,
        request_digest=digest,
    )


def validate_retry_count(retry_count: int) -> None:
    """Bound repeated tool execution to reduce runaway/cost-amplification risk."""
    if not isinstance(retry_count, int) or retry_count < 0 or retry_count >= MAX_RETRIES_PER_STEP:
        raise AIGuardError("AI retry budget exceeded.")
