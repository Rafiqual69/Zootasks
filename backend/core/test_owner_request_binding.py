import unittest

from .owner_request_binding import RequestBindingError, canonical_request_digest


class OwnerRequestBindingTests(unittest.TestCase):
    def _digest(self, **overrides):
        values = {
            "request_id": "req-001",
            "operation": "production_deploy",
            "target": "release-2026-10-06",
            "scope": "production",
            "environment": "production",
            "policy_version": "1.0.0",
            "material_parameters": {"commit_sha": "abc123", "migration": "none"},
        }
        values.update(overrides)
        return canonical_request_digest(**values)

    def test_same_request_has_same_digest(self):
        self.assertEqual(self._digest(), self._digest())

    def test_material_parameter_change_changes_digest(self):
        self.assertNotEqual(
            self._digest(),
            self._digest(material_parameters={"commit_sha": "changed", "migration": "none"}),
        )

    def test_target_change_changes_digest(self):
        self.assertNotEqual(
            self._digest(),
            self._digest(target="different-release"),
        )

    def test_action_change_changes_digest(self):
        self.assertNotEqual(
            self._digest(),
            self._digest(operation="production_rollback"),
        )

    def test_policy_version_is_bound(self):
        self.assertNotEqual(
            self._digest(),
            self._digest(policy_version="2.0.0"),
        )

    def test_float_is_rejected(self):
        with self.assertRaises(RequestBindingError):
            self._digest(material_parameters={"amount": 10.5})

    def test_sensitive_parameter_key_is_rejected(self):
        with self.assertRaises(RequestBindingError):
            self._digest(material_parameters={"api_token": "must-not-bind"})

    def test_nested_sensitive_parameter_names_are_rejected(self):
        for key in ("credential", "authorization", "access_key", "api_key"):
            with self.assertRaises(RequestBindingError):
                self._digest(material_parameters={"nested": {key: "must-not-bind"}})

    def test_empty_required_metadata_is_rejected(self):
        with self.assertRaises(RequestBindingError):
            self._digest(target="")

    def test_unsupported_parameter_type_is_rejected(self):
        with self.assertRaises(RequestBindingError):
            self._digest(material_parameters={"object": object()})


if __name__ == "__main__":
    unittest.main()
