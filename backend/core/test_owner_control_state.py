from django.test import SimpleTestCase

from .owner_control_state import (
    OwnerControlState,
    OwnerControlStateDenied,
    parse_owner_control_state,
    requires_dual_control,
)


class OwnerControlStateTests(SimpleTestCase):
    def test_development_state_does_not_require_dual_control_for_nonproduction(self):
        self.assertFalse(
            requires_dual_control(
                state=OwnerControlState.DEVELOPMENT_SINGLE_DEVICE,
                protected_production=False,
            )
        )

    def test_production_dual_control_state_requires_two_devices(self):
        self.assertTrue(
            requires_dual_control(
                state=OwnerControlState.PRODUCTION_DUAL_CONTROL,
                protected_production=True,
            )
        )

    def test_readiness_state_denies_protected_production(self):
        with self.assertRaises(OwnerControlStateDenied):
            requires_dual_control(
                state=OwnerControlState.PRODUCTION_READINESS_PENDING,
                protected_production=True,
            )

    def test_security_freeze_denies_protected_production(self):
        with self.assertRaises(OwnerControlStateDenied):
            requires_dual_control(
                state=OwnerControlState.SECURITY_FREEZE,
                protected_production=True,
            )

    def test_unknown_state_denies(self):
        with self.assertRaises(OwnerControlStateDenied):
            parse_owner_control_state("UNKNOWN")

    def test_malformed_state_denies(self):
        with self.assertRaises(OwnerControlStateDenied):
            parse_owner_control_state(None)
