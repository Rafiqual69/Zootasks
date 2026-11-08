import json
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from .whatsapp import WhatsAppDeliveryError, send_whatsapp_otp


@override_settings(
    WHATSAPP_OTP_ENABLED=True,
    META_WHATSAPP_GRAPH_API_VERSION="v26.0",
    META_WHATSAPP_PHONE_NUMBER_ID="123456789012345",
    META_WHATSAPP_ACCESS_TOKEN="test-token-not-real",
    META_WHATSAPP_OTP_TEMPLATE_NAME="zootasks_login_otp",
    META_WHATSAPP_OTP_LANGUAGE_CODE="en",
)
class WhatsAppCloudAPITests(SimpleTestCase):
    def test_sends_only_approved_template_payload_over_https(self):
        response = MagicMock()
        response.read.return_value = json.dumps(
            {"messages": [{"id": "wamid.test"}]}
        ).encode("utf-8")

        with patch("accounts.whatsapp.urlopen", return_value=response) as mocked:
            self.assertTrue(send_whatsapp_otp("+8801712345678", "123456"))

        request = mocked.call_args.args[0]
        self.assertTrue(request.full_url.startswith("https://graph.facebook.com/v26.0/"))
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token-not-real")
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["messaging_product"], "whatsapp")
        self.assertEqual(payload["to"], "8801712345678")
        self.assertEqual(payload["template"]["name"], "zootasks_login_otp")
        self.assertEqual(payload["template"]["components"][0]["parameters"][0]["text"], "123456")
        self.assertEqual(payload["template"]["components"][1]["sub_type"], "url")

    @override_settings(WHATSAPP_OTP_ENABLED=False)
    def test_missing_configuration_fails_closed(self):
        with self.assertRaises(WhatsAppDeliveryError) as caught:
            send_whatsapp_otp("+8801712345678", "123456")
        self.assertNotIn("test-token-not-real", str(caught.exception))

    def test_provider_transport_error_does_not_leak_credentials(self):
        from urllib.error import URLError

        with patch("accounts.whatsapp.urlopen", side_effect=URLError("private provider detail")):
            with self.assertRaises(WhatsAppDeliveryError) as caught:
                send_whatsapp_otp("+8801712345678", "123456")
        self.assertNotIn("test-token-not-real", str(caught.exception))
        self.assertNotIn("private provider detail", str(caught.exception))
