"""Canonical, secret-free request binding for Owner dual-control approvals.

The resulting digest is intended to bind approvals to the exact protected
operation. It contains only non-secret action metadata and material parameters.
Approval verification and atomic single-use consumption remain separate
responsibilities.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any


class RequestBindingError(ValueError):
    """Raised when a protected action cannot be safely canonicalized."""


MAX_BINDING_DEPTH = 8
MAX_BINDING_NODES = 512
MAX_BINDING_STRING_LENGTH = 512

_FORBIDDEN_KEY_PARTS = (
    "password",
    "secret",
    "token",
    "private_key",
    "session",
    "cookie",
    "credential_value",
    "credential",
    "authorization",
    "access_key",
    "api_key",
    "bank_account",
    "payment_identifier",
)


def _validate_value(value: Any, *, path: str = "value", depth: int = 0, nodes: list[int] | None = None) -> None:
    nodes = nodes if nodes is not None else [0]
    nodes[0] += 1
    if nodes[0] > MAX_BINDING_NODES or depth > MAX_BINDING_DEPTH:
        raise RequestBindingError("parameter payload exceeds safety limits")
    if value is None or isinstance(value, (str, bool, int)):
        if isinstance(value, str) and len(value) > MAX_BINDING_STRING_LENGTH:
            raise RequestBindingError("parameter string exceeds safety limits")
        return
    if isinstance(value, float):
        raise RequestBindingError(f"floating-point value forbidden at {path}")
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str) or not key:
                raise RequestBindingError("parameter keys must be non-empty strings")
            lowered = key.casefold()
            if any(part in lowered for part in _FORBIDDEN_KEY_PARTS):
                raise RequestBindingError("sensitive parameter key forbidden")
            if len(key) > MAX_BINDING_STRING_LENGTH:
                raise RequestBindingError("parameter key exceeds safety limits")
            _validate_value(nested, path=f"{path}.{key}", depth=depth + 1, nodes=nodes)
        return
    if isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _validate_value(nested, path=f"{path}[{index}]", depth=depth + 1, nodes=nodes)
        return
    raise RequestBindingError(f"unsupported parameter type at {path}")


def canonical_request_digest(
    *,
    request_id: str,
    operation: str,
    target: str,
    scope: str,
    environment: str,
    policy_version: str,
    material_parameters: Mapping[str, Any] | None = None,
) -> str:
    """Return a deterministic SHA-256 binding without secret values.

    The caller must provide stable, non-secret identifiers and material
    parameters. Changing any bound field changes the digest.
    """
    values = {
        "request_id": request_id,
        "operation": operation,
        "target": target,
        "scope": scope,
        "environment": environment,
        "policy_version": policy_version,
        "material_parameters": dict(material_parameters or {}),
    }
    if any(
        not isinstance(values[key], str) or not values[key].strip()
        for key in ("request_id", "operation", "target", "scope", "environment", "policy_version")
    ):
        raise RequestBindingError("request binding metadata must be non-empty strings")
    if any(
        len(values[key]) > MAX_BINDING_STRING_LENGTH
        for key in ("request_id", "operation", "target", "scope", "environment", "policy_version")
    ):
        raise RequestBindingError("request binding metadata exceeds safety limits")
    _validate_value(values["material_parameters"], path="material_parameters")

    canonical = json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
