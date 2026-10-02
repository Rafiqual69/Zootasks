from django.test import SimpleTestCase
from core.ai_provider_offer import AIProviderOfferError, validate_and_normalize_offer

def sample_offer():
    return {
      "schema_version":"1.0","offer_id":"OFFER-001",
      "provider":{"provider_id":"provider-a","name":"Provider A"},
      "authorization":{"status":"verified","route":"api_partner","contract_reference":"contract-1"},
      "source":{"kind":"api","identifier":"provider-a/offers/v1"},
      "eligibility":{"regions":["BD","US","BD"],"languages":["en","bn"],"requirements":["qualification"]},
      "task":{"category":"llm_evaluation","title":"Evaluate model responses","skills":["reasoning","en","reasoning"]},
      "reward":{"amount":1.25,"currency":"USD","payment_terms":"Provider approval"},
      "data_policy":{"sensitivity":"internal","retention":"30 days","processing_restrictions":[]},
      "qualification":{"required":True,"method":"provider test"},
      "verification":{"method":"provider QA"},"adapter":{"adapter_id":"provider-a-v1","version":"1.0"},
      "sync":{"status":"active","last_success_at":"2026-10-02T00:00:00Z"},
      "provenance":{"source_revision":"rev-1","evidence_refs":["E1","E1"]},"risk":{"state":"approved","reason":None}
    }

class AIProviderOfferTests(SimpleTestCase):
    def test_valid_offer_normalizes_deterministically(self):
        a=validate_and_normalize_offer(sample_offer()).payload
        b=validate_and_normalize_offer(sample_offer()).payload
        self.assertEqual(a,b); self.assertEqual(a["eligibility"]["regions"],["BD","US"]); self.assertEqual(a["reward"]["amount"],"1.25")
        self.assertTrue(validate_and_normalize_offer(sample_offer()).executable)

    def test_unverified_offer_is_never_executable(self):
        o=sample_offer(); o["authorization"]["status"]="pending"; n=validate_and_normalize_offer(o)
        self.assertFalse(n.executable); self.assertEqual(n.payload["risk"]["state"],"quarantined")

    def test_revoked_or_failed_sync_cannot_execute(self):
        o=sample_offer(); o["risk"]["state"]="revoked"; self.assertFalse(validate_and_normalize_offer(o).executable)
        o=sample_offer(); o["sync"]["status"]="failed"; self.assertFalse(validate_and_normalize_offer(o).executable)

    def test_unknown_root_fields_are_rejected(self):
        o=sample_offer(); o["unexpected"]="attack"
        with self.assertRaisesRegex(AIProviderOfferError,"offer_root_fields_invalid"): validate_and_normalize_offer(o)

    def test_unsupported_category_is_rejected(self):
        o=sample_offer(); o["task"]["category"]="wallet_payout"
        with self.assertRaisesRegex(AIProviderOfferError,"offer_task_category_unsupported"): validate_and_normalize_offer(o)

    def test_negative_reward_is_rejected(self):
        o=sample_offer(); o["reward"]["amount"]=-1
        with self.assertRaisesRegex(AIProviderOfferError,"offer_reward_amount_invalid"): validate_and_normalize_offer(o)

    def test_non_uppercase_currency_is_rejected(self):
        o=sample_offer(); o["reward"]["currency"]="usd"
        with self.assertRaisesRegex(AIProviderOfferError,"offer_reward_currency_invalid"): validate_and_normalize_offer(o)
