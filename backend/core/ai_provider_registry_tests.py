from django.test import SimpleTestCase
from core.ai_provider_registry import AIProviderRegistryError,ProviderRegistration,can_sync_provider,validate_provider_registration

def provider(status="verified",adapter_state="ready"):
    return ProviderRegistration("provider-a","Provider A","api_partner",status,"provider-a-v1","1.0",frozenset({"BD"}),frozenset({"llm_evaluation"}),adapter_state)

class AIProviderRegistryTests(SimpleTestCase):
    def test_verified_ready_provider_can_sync(self): self.assertTrue(can_sync_provider(provider()))
    def test_pending_provider_cannot_sync(self): self.assertFalse(can_sync_provider(provider("pending","disabled")))
    def test_unverified_provider_cannot_be_ready(self):
        with self.assertRaisesRegex(AIProviderRegistryError,"unverified_provider_cannot_be_ready"): validate_provider_registration(provider("pending","ready"))
    def test_revoked_provider_cannot_sync(self): self.assertFalse(can_sync_provider(provider("revoked","disabled")))
    def test_unsupported_route_is_rejected(self):
        e=provider(); e=ProviderRegistration(e.provider_id,e.name,"unknown",e.status,e.adapter_id,e.adapter_version,e.allowed_regions,e.capabilities,e.adapter_state)
        with self.assertRaisesRegex(AIProviderRegistryError,"provider_route_unsupported"): validate_provider_registration(e)
    def test_invalid_region_type_is_rejected(self):
        e=provider(); e=ProviderRegistration(e.provider_id,e.name,e.route,e.status,e.adapter_id,e.adapter_version,{"BD"},e.capabilities,e.adapter_state)
        with self.assertRaisesRegex(AIProviderRegistryError,"provider_regions_invalid"): validate_provider_registration(e)
