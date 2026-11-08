import hashlib
import hmac
import json
from urllib.request import Request, urlopen

from django.conf import settings


class WhatsAppDeliveryError(Exception):
    """Raised when Meta does not accept the OTP message."""


def keyed_digest(value):
    return hmac.new(
        settings.WHATSAPP_PHONE_HASH_KEY.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def otp_digest(challenge_id, code):
    value = f"whatsapp-otp:{challenge_id}:{code}".encode("utf-8")
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        value,
        hashlib.sha256,
    ).hexdigest()


def send_whatsapp_otp(phone_number, code):
    """Send a Meta-approved WhatsApp authentication template without logging PII."""
    if not getattr(settings, "WHATSAPP_OTP_ENABLED", False):
        raise WhatsAppDeliveryError("WhatsApp OTP is not configured.")

    version = settings.META_WHATSAPP_GRAPH_API_VERSION
    phone_number_id = settings.META_WHATSAPP_PHONE_NUMBER_ID
    url = (
        f"https://graph.facebook.com/{version}/"
        f"{phone_number_id}/messages"
    )
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number.lstrip("+"),
        "type": "template",
        "template": {
            "name": settings.META_WHATSAPP_OTP_TEMPLATE_NAME,
            "language": {"code": settings.META_WHATSAPP_OTP_LANGUAGE_CODE},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": code}],
                },
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [{"type": "text", "text": code}],
                },
            ],
        },
    }
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.META_WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=8) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError):
        # Never include the provider response, token, phone, or OTP in logs/errors.
        raise WhatsAppDeliveryError("WhatsApp delivery failed.") from None

    if not isinstance(result, dict) or not result.get("messages"):
        raise WhatsAppDeliveryError("WhatsApp delivery was not accepted.")
    return True
